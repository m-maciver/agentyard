"""
AgentYard — Admin router
Review queue, dispute resolution. Admin API key or admin JWT required.
"""
import hmac
import logging
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Header, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, col

from api.database import get_session
from api.models import AdminReview, Agent, Job, JobStatus
from api.services import escrow as escrow_service
from api.services.reputation import recalculate_agent_reputation
from config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin", tags=["admin"])


async def require_admin(x_admin_key: Optional[str] = Header(None, alias="X-Admin-Key")):
    """Simple admin key check using timing-safe comparison."""
    if not x_admin_key or not hmac.compare_digest(x_admin_key, settings.admin_api_key):
        raise HTTPException(status_code=403, detail="Admin access required")
    return True


# ─── Review Queue ─────────────────────────────────────────────────────────────

@router.get("/reviews")
async def list_reviews(
    review_status: str = Query("pending"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    _: bool = Depends(require_admin),
    session: AsyncSession = Depends(get_session),
):
    """List pending admin reviews (first-5-job queue)."""
    result = await session.execute(
        select(AdminReview)
        .where(AdminReview.status == review_status)
        .offset(offset)
        .limit(limit)
        .order_by(col(AdminReview.created_at).asc())
    )
    reviews = result.scalars().all()

    return {
        "reviews": [
            {
                "id": str(r.id),
                "job_id": str(r.job_id),
                "agent_id": str(r.agent_id),
                "review_type": r.review_type,
                "status": r.status,
                "notes": r.notes,
                "created_at": r.created_at.isoformat(),
            }
            for r in reviews
        ],
        "total": len(reviews),
    }


@router.post("/reviews/{review_id}/approve")
async def approve_review(
    review_id: UUID,
    notes: Optional[str] = None,
    _: bool = Depends(require_admin),
    session: AsyncSession = Depends(get_session),
):
    """Approve a first-5-job review."""
    result = await session.execute(select(AdminReview).where(AdminReview.id == review_id))
    review = result.scalar_one_or_none()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    review.status = "approved"
    review.notes = notes
    review.reviewed_by = "admin"
    review.reviewed_at = datetime.now(timezone.utc)
    session.add(review)

    # Check if agent now has 5 approved reviews → mark as verified
    approved_result = await session.execute(
        select(AdminReview).where(
            AdminReview.agent_id == review.agent_id,
            AdminReview.status == "approved",
        )
    )
    approved_count = len(approved_result.all())

    if approved_count >= 5:
        agent_result = await session.execute(select(Agent).where(Agent.id == review.agent_id))
        agent = agent_result.scalar_one_or_none()
        if agent and not agent.is_verified:
            agent.is_verified = True
            agent.updated_at = datetime.now(timezone.utc)
            session.add(agent)
            logger.info(f"Agent {agent.id} ({agent.name}) is now verified!")

    await session.commit()
    return {"status": "approved", "review_id": str(review_id)}


@router.post("/reviews/{review_id}/reject")
async def reject_review(
    review_id: UUID,
    reason: str,
    _: bool = Depends(require_admin),
    session: AsyncSession = Depends(get_session),
):
    """Flag/reject a first-5-job review. Agent may be suspended."""
    result = await session.execute(select(AdminReview).where(AdminReview.id == review_id))
    review = result.scalar_one_or_none()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    review.status = "flagged"
    review.notes = reason
    review.reviewed_by = "admin"
    review.reviewed_at = datetime.now(timezone.utc)
    session.add(review)

    # Suspend the agent
    agent_result = await session.execute(select(Agent).where(Agent.id == review.agent_id))
    agent = agent_result.scalar_one_or_none()
    if agent:
        agent.is_active = False
        agent.updated_at = datetime.now(timezone.utc)
        session.add(agent)
        logger.warning(f"Agent {agent.id} ({agent.name}) suspended after flagged review")

    await session.commit()
    return {"status": "flagged", "review_id": str(review_id), "agent_suspended": True}


# ─── Disputes ─────────────────────────────────────────────────────────────────

@router.get("/disputes")
async def list_disputes(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    _: bool = Depends(require_admin),
    session: AsyncSession = Depends(get_session),
):
    """List open disputes."""
    result = await session.execute(
        select(Job)
        .where(Job.status == JobStatus.DISPUTED)
        .offset(offset)
        .limit(limit)
        .order_by(col(Job.disputed_at).asc())
    )
    jobs = result.scalars().all()

    return {
        "disputes": [
            {
                "job_id": str(j.id),
                "client_agent_id": str(j.client_agent_id),
                "provider_agent_id": str(j.provider_agent_id),
                "price_sats": j.price_sats,
                "stake_sats": j.stake_sats,
                "dispute_reason": j.dispute_reason,
                "disputed_at": j.disputed_at.isoformat() if j.disputed_at else None,
                "output": j.output_payload,
            }
            for j in jobs
        ],
        "total": len(jobs),
    }


@router.post("/disputes/{job_id}/resolve")
async def resolve_dispute(
    job_id: UUID,
    resolution: str,  # "client" or "provider"
    notes: Optional[str] = None,
    _: bool = Depends(require_admin),
    session: AsyncSession = Depends(get_session),
):
    """
    Resolve a dispute.
    resolution="client" → refund client, slash provider stake
    resolution="provider" → pay provider, return stake
    """
    if resolution not in ("client", "provider"):
        raise HTTPException(status_code=400, detail="resolution must be 'client' or 'provider'")

    result = await session.execute(select(Job).where(Job.id == job_id))
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if job.status != JobStatus.DISPUTED:
        raise HTTPException(status_code=400, detail="Job is not in disputed status")

    # Get agents
    client_result = await session.execute(select(Agent).where(Agent.id == job.client_agent_id))
    client = client_result.scalar_one_or_none()

    provider_result = await session.execute(select(Agent).where(Agent.id == job.provider_agent_id))
    provider = provider_result.scalar_one_or_none()

    job.dispute_resolved_by = "admin"
    job.dispute_resolution = resolution

    if resolution == "client":
        # Client wins: refund + slash stake
        success = await escrow_service.refund_client(job, client, provider, session)
        if not success:
            raise HTTPException(status_code=500, detail="Refund failed — check LNBits config")
    else:
        # Provider wins: release payment + return stake
        provider.jobs_won = (provider.jobs_won or 0) + 1
        provider.jobs_completed += 1
        session.add(provider)
        success = await escrow_service.release_escrow_to_provider(job, provider, session)
        if not success:
            raise HTTPException(status_code=500, detail="Escrow release failed — check LNBits config")

    # Recalculate provider reputation
    await recalculate_agent_reputation(provider, session)

    logger.info(f"Dispute for job {job.id} resolved in favour of {resolution}")
    return {
        "status": "resolved",
        "job_id": str(job_id),
        "resolution": resolution,
        "notes": notes,
    }
