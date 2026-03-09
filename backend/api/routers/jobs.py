"""
AgentYard — Jobs router
Full job lifecycle: create → escrow → deliver → complete/dispute
"""
import json
import logging
from datetime import datetime, timezone, timedelta
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, col, or_

from api.database import get_session
from api.deps import get_agent_by_key
from api.models import (
    Agent, Job, JobCreate, JobPublic, JobStatus,
    JobDeliverRequest, JobDisputeRequest,
    AdminReview,
)
from api.services import escrow as escrow_service
from api.services.delivery import deliver_via_webhook, notify_provider, notify_admin_dispute
from api.services.reputation import calculate_platform_fee, calculate_stake_sats, recalculate_agent_reputation
from api.utils.platform_stats import contribute_to_pool
from config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.post("", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_job(
    body: JobCreate,
    client_agent: Agent = Depends(get_agent_by_key),
    session: AsyncSession = Depends(get_session),
):
    """
    Create a job and get a Lightning payment invoice.
    Client agent auth required (X-Agent-Key).
    """
    # Get provider agent
    result = await session.execute(
        select(Agent).where(Agent.id == body.provider_agent_id, Agent.is_active == True)
    )
    provider = result.scalar_one_or_none()
    if not provider:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "agent_not_found",
                "message": f"Provider agent '{body.provider_agent_id}' not found or is inactive. Check the agent ID and try again.",
                "docs": "https://agentyard.xyz/docs#jobs",
            },
        )

    # Can't hire yourself
    if client_agent.id == provider.id:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "self_hire",
                "message": "An agent cannot hire itself. Use a different agent as the client.",
                "docs": "https://agentyard.xyz/docs#jobs",
            },
        )

    price_sats = provider.price_per_task_sats
    platform_fee = calculate_platform_fee(price_sats, provider.reputation_score)
    stake_sats = calculate_stake_sats(price_sats, provider.reputation_score)

    # Check job size cap
    if price_sats > provider.max_job_sats:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "job_too_large",
                "message": f"Job price {price_sats} sats exceeds provider's max job size of {provider.max_job_sats} sats. Contact the provider to increase their limit.",
                "docs": "https://agentyard.xyz/docs#jobs",
            },
        )

    # Create job record
    job = Job(
        client_agent_id=client_agent.id,
        provider_agent_id=provider.id,
        title=body.title,
        description=body.description,
        task_input=json.dumps(body.task_input) if body.task_input else None,
        price_sats=price_sats,
        platform_fee_sats=platform_fee,
        stake_sats=stake_sats,
        delivery_channel=body.delivery_channel,
        delivery_target=body.delivery_target,
        status=JobStatus.DRAFT,
    )
    session.add(job)
    await session.commit()
    await session.refresh(job)

    # Create LNBits invoice
    try:
        invoice_data = await escrow_service.create_job_invoice(job, provider, session)
    except Exception as e:
        logger.error(f"Failed to create invoice for job {job.id}: {e}")
        # Still return the job, client can retry or use mock invoice for dev
        return {
            "job_id": str(job.id),
            "invoice": "lnbc_dev_invoice_lnbits_not_configured",
            "amount_sats": price_sats + platform_fee,
            "breakdown": {
                "task_price_sats": price_sats,
                "platform_fee_sats": platform_fee,
                "stake_required_sats": stake_sats,
            },
            "status": job.status,
            "warning": "Lightning payments not yet configured. This is a placeholder invoice. Real payments coming soon.",
        }

    return {
        "job_id": str(job.id),
        "invoice": invoice_data["escrow_invoice"],
        "amount_sats": invoice_data["total_sats"],
        "breakdown": {
            "task_price_sats": invoice_data["price_sats"],
            "platform_fee_sats": invoice_data["platform_fee_sats"],
            "stake_required_sats": invoice_data["stake_sats"],
        },
        "pay_by": (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat(),
        "status": job.status,
    }


@router.get("", response_model=dict)
async def list_jobs(
    role: Optional[str] = Query(None, description="Filter: 'client' or 'provider'"),
    job_status: Optional[JobStatus] = Query(None, alias="status"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    agent: Agent = Depends(get_agent_by_key),
    session: AsyncSession = Depends(get_session),
):
    """List jobs for the authenticated agent."""
    if role == "client":
        query = select(Job).where(Job.client_agent_id == agent.id)
    elif role == "provider":
        query = select(Job).where(Job.provider_agent_id == agent.id)
    else:
        query = select(Job).where(
            or_(Job.client_agent_id == agent.id, Job.provider_agent_id == agent.id)
        )

    if job_status:
        query = query.where(Job.status == job_status)

    query = query.offset(offset).limit(limit).order_by(col(Job.created_at).desc())
    result = await session.execute(query)
    jobs = result.scalars().all()

    return {
        "jobs": [JobPublic.model_validate(j) for j in jobs],
        "limit": limit,
        "offset": offset,
    }


@router.get("/{job_id}", response_model=JobPublic)
async def get_job(
    job_id: UUID,
    agent: Agent = Depends(get_agent_by_key),
    session: AsyncSession = Depends(get_session),
):
    """Get job status and output."""
    result = await session.execute(select(Job).where(Job.id == job_id))
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "job_not_found",
                "message": f"Job '{job_id}' not found. Check the job ID and try again.",
                "docs": "https://agentyard.xyz/docs#jobs",
            },
        )

    # Only client or provider can view
    if job.client_agent_id != agent.id and job.provider_agent_id != agent.id:
        raise HTTPException(
            status_code=403,
            detail={
                "error": "forbidden",
                "message": "Access denied. Only the client or provider of this job can view it.",
                "docs": "https://agentyard.xyz/docs#jobs",
            },
        )

    return job


@router.post("/{job_id}/deliver", response_model=JobPublic)
async def deliver_job(
    job_id: UUID,
    body: JobDeliverRequest,
    agent: Agent = Depends(get_agent_by_key),
    session: AsyncSession = Depends(get_session),
):
    """
    Provider submits job output.
    Sets auto_release_at = now + 2h (dispute window).
    """
    result = await session.execute(select(Job).where(Job.id == job_id))
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "job_not_found",
                "message": f"Job '{job_id}' not found. Check the job ID and try again.",
                "docs": "https://agentyard.xyz/docs#jobs",
            },
        )

    if job.provider_agent_id != agent.id:
        raise HTTPException(
            status_code=403,
            detail={
                "error": "job_not_deliverable",
                "message": "Only the assigned provider can deliver this job.",
                "docs": "https://agentyard.xyz/docs#jobs",
            },
        )

    if job.status not in (JobStatus.IN_PROGRESS, JobStatus.ESCROWED):
        raise HTTPException(
            status_code=400,
            detail={
                "error": "job_not_deliverable",
                "message": f"This job cannot be delivered. Current status: {job.status}. Job must be IN_PROGRESS or ESCROWED.",
                "docs": "https://agentyard.xyz/docs#jobs",
            },
        )

    now = datetime.now(timezone.utc)
    job.output_payload = body.output
    job.output_url = body.output_url
    job.status = JobStatus.DELIVERED
    job.delivered_at = now
    # Dispute window — buyer has this long to raise a dispute before funds auto-release
    job.auto_release_at = now + timedelta(minutes=settings.dispute_window_minutes)

    session.add(job)
    await session.commit()
    await session.refresh(job)

    # Check if this is one of provider's first 5 jobs — queue for admin review
    if agent.jobs_completed < 5:
        review = AdminReview(
            job_id=job.id,
            agent_id=agent.id,
            review_type="first_5_jobs",
            status="pending",
        )
        session.add(review)
        await session.commit()

    # Deliver output to client (best-effort — ARQ worker handles retries)
    try:
        await deliver_via_webhook(job, provider_name=agent.name)
    except Exception as e:
        logger.warning(f"Immediate delivery failed for job {job.id}: {e} — will retry via ARQ")

    return job


@router.post("/{job_id}/complete", response_model=JobPublic)
async def complete_job(
    job_id: UUID,
    agent: Agent = Depends(get_agent_by_key),
    session: AsyncSession = Depends(get_session),
):
    """Client confirms delivery, triggers early escrow release."""
    result = await session.execute(select(Job).where(Job.id == job_id))
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "job_not_found",
                "message": f"Job '{job_id}' not found. Check the job ID and try again.",
                "docs": "https://agentyard.xyz/docs#jobs",
            },
        )

    if job.client_agent_id != agent.id:
        raise HTTPException(
            status_code=403,
            detail={
                "error": "job_not_acceptable",
                "message": "Only the job poster (client) can confirm delivery.",
                "docs": "https://agentyard.xyz/docs#jobs",
            },
        )

    if job.status != JobStatus.DELIVERED:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "job_not_deliverable",
                "message": f"This job cannot be completed. Current status: {job.status}. Job must be DELIVERED first.",
                "docs": "https://agentyard.xyz/docs#jobs",
            },
        )

    # Get provider
    provider_result = await session.execute(select(Agent).where(Agent.id == job.provider_agent_id))
    provider = provider_result.scalar_one_or_none()
    if not provider:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "provider_not_found",
                "message": "Provider agent not found. Contact support: github.com/m-maciver/agentyard/issues",
                "docs": "https://agentyard.xyz/docs#support",
            },
        )

    # Release escrow
    success = await escrow_service.release_escrow_to_provider(job, provider, session)
    if not success:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "escrow_release_failed",
                "message": "Failed to release escrow. Please try again. If this persists, contact support: github.com/m-maciver/agentyard/issues",
                "docs": "https://agentyard.xyz/docs#support",
            },
        )

    # Recalculate provider reputation (includes JSS recalculation + threshold enforcement)
    await recalculate_agent_reputation(provider, session)

    # Feed 2% of platform fee into buyer protection pool
    try:
        contribute_to_pool(job.platform_fee_sats)
    except Exception as e:
        logger.warning(f"Failed to update protection pool for job {job.id}: {e}")

    await session.refresh(job)
    return job


@router.put("/{job_id}/accept", response_model=dict)
async def accept_job_delivery(
    job_id: UUID,
    agent: Agent = Depends(get_agent_by_key),
    session: AsyncSession = Depends(get_session),
):
    """
    Buyer explicitly accepts delivery — releases sats immediately.
    Skips the dispute window entirely. Use when you're happy and want to pay now.
    """
    result = await session.execute(select(Job).where(Job.id == job_id))
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "job_not_found",
                "message": f"Job '{job_id}' not found. Check the job ID and try again.",
                "docs": "https://agentyard.xyz/docs#jobs",
            },
        )

    if job.client_agent_id != agent.id:
        raise HTTPException(
            status_code=403,
            detail={
                "error": "job_not_acceptable",
                "message": "Only the job poster (buyer) can accept delivery.",
                "docs": "https://agentyard.xyz/docs#jobs",
            },
        )

    if job.status != JobStatus.DELIVERED:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "job_not_deliverable",
                "message": f"This job cannot be accepted. Current status: {job.status}. Job must be DELIVERED first.",
                "docs": "https://agentyard.xyz/docs#jobs",
            },
        )

    # Get provider
    provider_result = await session.execute(select(Agent).where(Agent.id == job.provider_agent_id))
    provider = provider_result.scalar_one_or_none()
    if not provider:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "provider_not_found",
                "message": "Provider agent not found. Contact support: github.com/m-maciver/agentyard/issues",
                "docs": "https://agentyard.xyz/docs#support",
            },
        )

    # Stamp acceptance before releasing (idempotency guard)
    now = datetime.now(timezone.utc)
    job.accepted_at = now
    job.accepted_by = str(agent.id)
    session.add(job)
    await session.commit()

    # Same release path as auto-release and complete endpoint
    success = await escrow_service.release_escrow_to_provider(job, provider, session)
    if not success:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "escrow_release_failed",
                "message": "Failed to release escrow. Please try again. If this persists, contact support: github.com/m-maciver/agentyard/issues",
                "docs": "https://agentyard.xyz/docs#support",
            },
        )

    await recalculate_agent_reputation(provider, session)

    try:
        contribute_to_pool(job.platform_fee_sats)
    except Exception as e:
        logger.warning(f"Failed to update protection pool for job {job.id}: {e}")

    await session.refresh(job)
    return {"status": "completed", "message": "Payment released to provider", "job_id": str(job.id)}


@router.post("/{job_id}/dispute", response_model=JobPublic)
async def dispute_job(
    job_id: UUID,
    body: JobDisputeRequest,
    agent: Agent = Depends(get_agent_by_key),
    session: AsyncSession = Depends(get_session),
):
    """Client raises a dispute. Stops auto-release timer."""
    result = await session.execute(select(Job).where(Job.id == job_id))
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "job_not_found",
                "message": f"Job '{job_id}' not found. Check the job ID and try again.",
                "docs": "https://agentyard.xyz/docs#jobs",
            },
        )

    if job.client_agent_id != agent.id:
        raise HTTPException(
            status_code=403,
            detail={
                "error": "forbidden",
                "message": "Only the client (buyer) can dispute this job.",
                "docs": "https://agentyard.xyz/docs#disputes",
            },
        )

    if job.status != JobStatus.DELIVERED:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "job_not_disputable",
                "message": f"Cannot dispute job in status '{job.status}'. Job must be DELIVERED and within the {settings.dispute_window_minutes}-minute dispute window.",
                "docs": "https://agentyard.xyz/docs#disputes",
            },
        )

    # Check still in dispute window
    # Handle SQLite returning naive datetimes by making them UTC-aware
    auto_release = job.auto_release_at
    if auto_release and auto_release.tzinfo is None:
        auto_release = auto_release.replace(tzinfo=timezone.utc)
    if auto_release and datetime.now(timezone.utc) >= auto_release:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "dispute_window_closed",
                "message": f"The {settings.dispute_window_minutes}-minute dispute window has closed and escrow has been auto-released to the provider. Contact support for assistance: github.com/m-maciver/agentyard/issues",
                "docs": "https://agentyard.xyz/docs#disputes",
            },
        )

    job.status = JobStatus.DISPUTED
    job.dispute_reason = body.reason
    job.disputed_at = datetime.now(timezone.utc)
    job.auto_release_at = None  # Stop the auto-release timer

    session.add(job)
    await session.commit()
    await session.refresh(job)

    # Notify admin
    try:
        await notify_admin_dispute(job)
    except Exception as e:
        logger.warning(f"Failed to notify admin of dispute {job.id}: {e}")

    return job
