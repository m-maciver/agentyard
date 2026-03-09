"""
AgentYard — Escrow service
Handles the payment flow: create invoice → verify → release → refund
"""
import logging
from datetime import datetime, timezone, timedelta
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from api.models import Job, JobStatus, Transaction, TransactionType, Stake, StakeStatus, Agent
from api.services import lnbits as lnbits_service
from api.services.reputation import calculate_stake_sats, calculate_platform_fee
from config import settings

logger = logging.getLogger(__name__)


async def create_job_invoice(job: Job, provider: Agent, session: AsyncSession) -> dict:
    """
    Create a LNBits invoice for a job.
    Returns {payment_hash, escrow_invoice, total_sats}
    """
    platform_fee = calculate_platform_fee(job.price_sats, provider.reputation_score)
    stake_sats = calculate_stake_sats(job.price_sats, provider.reputation_score)
    total_sats = job.price_sats + platform_fee

    # Create invoice on the escrow wallet
    memo = f"AgentYard job {str(job.id)[:8]} — {job.title or job.description[:50]}"
    result = await lnbits_service.create_invoice(
        invoice_key=settings.lnbits_escrow_wallet_inkey,
        amount_sats=total_sats,
        memo=memo,
    )

    # Update job with invoice details
    job.platform_fee_sats = platform_fee
    job.stake_sats = stake_sats
    job.payment_hash = result["payment_hash"]
    job.escrow_invoice = result["payment_request"]
    job.status = JobStatus.AWAITING_PAYMENT

    session.add(job)
    await session.commit()
    await session.refresh(job)

    return {
        "payment_hash": result["payment_hash"],
        "escrow_invoice": result["payment_request"],
        "total_sats": total_sats,
        "price_sats": job.price_sats,
        "platform_fee_sats": platform_fee,
        "stake_sats": stake_sats,
    }


async def confirm_payment(job: Job, provider: Agent, session: AsyncSession) -> bool:
    """
    Called when LNBits confirms payment. 
    Checks provider has enough stake, updates job status.
    """
    # Check provider stake balance
    if provider.stake_balance_sats < job.stake_sats:
        logger.warning(
            f"Provider {provider.id} insufficient stake: "
            f"has {provider.stake_balance_sats}, needs {job.stake_sats}"
        )
        # Job stays ESCROWED — provider must top up
        return False

    # Deduct stake from provider balance
    provider.stake_balance_sats -= job.stake_sats
    provider.updated_at = datetime.now(timezone.utc)

    # Record ESCROW_IN transaction
    escrow_tx = Transaction(
        job_id=job.id,
        type=TransactionType.ESCROW_IN,
        amount_sats=job.price_sats + job.platform_fee_sats,
        payment_hash=job.payment_hash,
        note=f"Client payment escrowed for job {str(job.id)[:8]}",
    )
    # Record STAKE_HOLD transaction
    stake_tx = Transaction(
        job_id=job.id,
        type=TransactionType.STAKE_HOLD,
        amount_sats=job.stake_sats,
        note=f"Provider stake held for job {str(job.id)[:8]}",
    )
    # Create stake record
    stake = Stake(
        agent_id=provider.id,
        job_id=job.id,
        amount_sats=job.stake_sats,
        status=StakeStatus.HELD,
    )

    # Move job to IN_PROGRESS
    job.status = JobStatus.IN_PROGRESS
    job.started_at = datetime.now(timezone.utc)

    session.add(provider)
    session.add(escrow_tx)
    session.add(stake_tx)
    session.add(stake)
    session.add(job)
    await session.commit()

    logger.info(f"Payment confirmed for job {job.id}, status → IN_PROGRESS")
    return True


async def release_escrow_to_provider(job: Job, provider: Agent, session: AsyncSession) -> bool:
    """
    Release escrowed sats to the provider.
    Called on: auto-release after 2h, or client early-confirm.
    """
    # Check if in stub mode
    import os
    lightning_stub = os.environ.get("LIGHTNING_STUB", "").lower() in ("true", "1") or \
        settings.lnbits_url in ("stub", "")
    
    if lightning_stub:
        # Skip LNBits calls in stub mode
        logger.info(f"Stub mode: skipping LNBits payment for job {job.id}")
        # Mark job as complete directly
        job.status = JobStatus.COMPLETE
        job.completed_at = datetime.now(timezone.utc)
        provider.jobs_completed += 1
        provider.job_count += 1
        provider.stake_balance_sats += job.stake_sats
        provider.updated_at = datetime.now(timezone.utc)
        session.add(job)
        session.add(provider)
        await session.commit()
        return True
    
    if not provider.lnbits_invoice_key or not provider.lnbits_wallet_id:
        logger.error(f"Provider {provider.id} has no LNBits wallet configured")
        return False

    try:
        # Generate invoice on provider's wallet
        provider_invoice = await lnbits_service.create_invoice(
            invoice_key=provider.lnbits_invoice_key,
            amount_sats=job.price_sats,
            memo=f"AgentYard payment for job {str(job.id)[:8]}",
        )

        # Pay from escrow wallet to provider
        await lnbits_service.pay_invoice(
            admin_key=settings.lnbits_escrow_wallet_adminkey,
            bolt11=provider_invoice["payment_request"],
        )

        # Return stake to provider
        provider.stake_balance_sats += job.stake_sats
        provider.jobs_completed += 1
        provider.job_count += 1
        provider.updated_at = datetime.now(timezone.utc)

        # Record transactions
        release_tx = Transaction(
            job_id=job.id,
            type=TransactionType.PROVIDER_RELEASE,
            amount_sats=job.price_sats,
            payment_hash=provider_invoice["payment_hash"],
            to_wallet=provider.lnbits_wallet_id,
            note="Escrow released to provider",
        )
        stake_return_tx = Transaction(
            job_id=job.id,
            type=TransactionType.STAKE_RETURN,
            amount_sats=job.stake_sats,
            note="Stake returned to provider after successful delivery",
        )
        fee_tx = Transaction(
            job_id=job.id,
            type=TransactionType.FEE_COLLECT,
            amount_sats=job.platform_fee_sats,
            note="Platform fee collected",
        )

        # Update stake record
        result = await session.execute(
            select(Stake).where(Stake.job_id == job.id, Stake.agent_id == provider.id)
        )
        stake = result.scalar_one_or_none()
        if stake:
            stake.status = StakeStatus.RETURNED
            stake.resolved_at = datetime.now(timezone.utc)
            session.add(stake)

        job.status = JobStatus.COMPLETE
        job.completed_at = datetime.now(timezone.utc)

        session.add(provider)
        session.add(release_tx)
        session.add(stake_return_tx)
        session.add(fee_tx)
        session.add(job)
        await session.commit()

        logger.info(f"Escrow released for job {job.id}, provider {provider.id} paid {job.price_sats} sats")
        return True

    except Exception as e:
        logger.error(f"Failed to release escrow for job {job.id}: {e}")
        return False


async def refund_client(job: Job, client: Agent, provider: Agent, session: AsyncSession) -> bool:
    """
    Refund client and slash provider stake (client wins dispute).
    """
    if not client.lnbits_invoice_key or not client.lnbits_wallet_id:
        logger.error(f"Client {client.id} has no LNBits wallet configured for refund")
        return False

    try:
        # Generate refund invoice on client's wallet
        client_invoice = await lnbits_service.create_invoice(
            invoice_key=client.lnbits_invoice_key,
            amount_sats=job.price_sats + job.platform_fee_sats,
            memo=f"AgentYard refund for job {str(job.id)[:8]}",
        )

        # Pay refund from escrow wallet
        await lnbits_service.pay_invoice(
            admin_key=settings.lnbits_escrow_wallet_adminkey,
            bolt11=client_invoice["payment_request"],
        )

        # Slash provider stake (goes to platform)
        provider.jobs_disputed += 1
        provider.job_count += 1
        provider.updated_at = datetime.now(timezone.utc)

        # Record transactions
        refund_tx = Transaction(
            job_id=job.id,
            type=TransactionType.CLIENT_REFUND,
            amount_sats=job.price_sats + job.platform_fee_sats,
            payment_hash=client_invoice["payment_hash"],
            to_wallet=client.lnbits_wallet_id,
            note="Client refund (won dispute)",
        )
        slash_tx = Transaction(
            job_id=job.id,
            type=TransactionType.STAKE_SLASH,
            amount_sats=job.stake_sats,
            note="Provider stake slashed (lost dispute)",
        )

        # Update stake record
        result = await session.execute(
            select(Stake).where(Stake.job_id == job.id, Stake.agent_id == provider.id)
        )
        stake = result.scalar_one_or_none()
        if stake:
            stake.status = StakeStatus.SLASHED
            stake.resolved_at = datetime.now(timezone.utc)
            session.add(stake)

        job.status = JobStatus.COMPLETE
        job.completed_at = datetime.now(timezone.utc)

        session.add(provider)
        session.add(refund_tx)
        session.add(slash_tx)
        session.add(job)
        await session.commit()

        logger.info(f"Client refund for job {job.id}, provider stake slashed")
        return True

    except Exception as e:
        logger.error(f"Failed to refund client for job {job.id}: {e}")
        return False
