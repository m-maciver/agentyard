"""
AgentYard — Webhooks router
Inbound webhook from LNBits when payment is confirmed.
"""
import hashlib
import hmac
import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Header, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from api.database import get_session
from api.models import Agent, Job, JobStatus
from api.services import escrow as escrow_service
from api.services.delivery import notify_provider
from config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


def verify_lnbits_signature(payload: bytes, signature: Optional[str]) -> bool | None:
    """
    Verify LNBits webhook HMAC signature.
    Returns True if valid, False if invalid, None if no secret is configured.
    """
    if not settings.lnbits_webhook_secret:
        # No webhook secret configured — caller must reject with 503
        return None

    if not signature:
        # Secret is configured but request has no signature — reject
        return False

    expected = hmac.new(
        settings.lnbits_webhook_secret.encode(),
        payload,
        hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(expected, signature)


@router.post("/lnbits")
async def lnbits_payment_webhook(
    request: Request,
    x_webhook_signature: Optional[str] = Header(None, alias="X-Webhook-Signature"),
    session: AsyncSession = Depends(get_session),
):
    """
    LNBits payment confirmation webhook.
    Called when a Lightning payment is confirmed.
    Moves job from AWAITING_PAYMENT → ESCROWED → IN_PROGRESS.
    """
    body = await request.body()

    sig_result = verify_lnbits_signature(body, x_webhook_signature)
    if sig_result is None:
        raise HTTPException(status_code=503, detail="Webhook secret not configured")
    if not sig_result:
        raise HTTPException(status_code=401, detail="Invalid webhook signature")

    try:
        data = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    payment_hash = data.get("payment_hash")
    if not payment_hash:
        logger.warning("LNBits webhook received without payment_hash")
        return {"status": "ignored", "reason": "no payment_hash"}

    # Find the job with this payment hash
    result = await session.execute(
        select(Job).where(
            Job.payment_hash == payment_hash,
            Job.status == JobStatus.AWAITING_PAYMENT,
        )
    )
    job = result.scalar_one_or_none()

    if not job:
        logger.info(f"No pending job found for payment_hash {payment_hash}")
        return {"status": "not_found"}

    # Get provider
    provider_result = await session.execute(
        select(Agent).where(Agent.id == job.provider_agent_id)
    )
    provider = provider_result.scalar_one_or_none()
    if not provider:
        logger.error(f"Provider not found for job {job.id}")
        return {"status": "error", "reason": "provider not found"}

    # Move job through payment flow
    # First: mark as ESCROWED
    job.status = JobStatus.ESCROWED
    session.add(job)
    await session.commit()

    # Then: check stake and move to IN_PROGRESS
    success = await escrow_service.confirm_payment(job, provider, session)

    if success:
        # Notify provider about the new job
        try:
            await notify_provider(job, provider)
        except Exception as e:
            logger.warning(f"Failed to notify provider {provider.id}: {e}")

        logger.info(f"Job {job.id} activated — provider {provider.name} notified")
        return {"status": "ok", "job_id": str(job.id), "job_status": "in_progress"}
    else:
        # Provider needs to top up stake — job stays ESCROWED
        logger.warning(f"Provider {provider.id} needs to top up stake for job {job.id}")
        return {"status": "ok", "job_id": str(job.id), "job_status": "escrowed_awaiting_stake"}
