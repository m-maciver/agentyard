"""
AgentYard — ARQ background workers
Tasks: auto_release_escrow, retry_webhook_delivery, recalculate_reputation
"""
import logging
from datetime import datetime, timezone

import arq

from config import settings

logger = logging.getLogger(__name__)


async def startup(ctx):
    """Called when the ARQ worker starts."""
    from api.database import async_session_maker
    ctx["session_maker"] = async_session_maker
    logger.info("ARQ worker started")


async def shutdown(ctx):
    """Called when the ARQ worker shuts down."""
    logger.info("ARQ worker shutting down")


async def auto_release_escrow(ctx, job_id: str):
    """
    Fire 2 hours after job is delivered.
    Releases escrowed sats to provider if no dispute has been raised.
    """
    from sqlmodel import select
    from api.models import Job, JobStatus, Agent
    from api.services import escrow as escrow_service
    from api.services.reputation import recalculate_agent_reputation

    async with ctx["session_maker"]() as session:
        result = await session.execute(select(Job).where(Job.id == job_id))
        job = result.scalar_one_or_none()

        if not job:
            logger.warning(f"auto_release_escrow: job {job_id} not found")
            return

        # Only release if still in DELIVERED status
        if job.status != JobStatus.DELIVERED:
            logger.info(f"auto_release_escrow: job {job_id} is in status '{job.status}', skipping")
            return

        # Check auto_release_at hasn't been cleared (dispute raised)
        if not job.auto_release_at:
            logger.info(f"auto_release_escrow: job {job_id} auto_release_at cleared (disputed?), skipping")
            return

        # Double-check the time has actually passed
        if datetime.now(timezone.utc) < job.auto_release_at:
            logger.info(f"auto_release_escrow: job {job_id} auto_release_at not yet reached, skipping")
            return

        provider_result = await session.execute(select(Agent).where(Agent.id == job.provider_agent_id))
        provider = provider_result.scalar_one_or_none()

        if not provider:
            logger.error(f"auto_release_escrow: provider not found for job {job_id}")
            return

        logger.info(f"Auto-releasing escrow for job {job_id} to provider {provider.name}")
        success = await escrow_service.release_escrow_to_provider(job, provider, session)

        if success:
            await recalculate_agent_reputation(provider, session)
            logger.info(f"Escrow auto-released for job {job_id}")
        else:
            logger.error(f"Auto-release failed for job {job_id} — manual intervention needed")


async def retry_webhook_delivery(ctx, job_id: str, attempt: int = 1):
    """
    Retry failed webhook delivery with exponential backoff.
    Max 5 attempts over ~30 minutes: 2m, 4m, 8m, 16m, 32m delays.
    """
    from sqlmodel import select
    from api.models import Job, Agent
    from api.services.delivery import deliver_via_webhook

    async with ctx["session_maker"]() as session:
        result = await session.execute(select(Job).where(Job.id == job_id))
        job = result.scalar_one_or_none()

        if not job:
            logger.warning(f"retry_webhook_delivery: job {job_id} not found")
            return

        provider_result = await session.execute(select(Agent).where(Agent.id == job.provider_agent_id))
        provider = provider_result.scalar_one_or_none()

        success = await deliver_via_webhook(job, provider_name=provider.name if provider else "")

        if success:
            logger.info(f"Webhook delivery succeeded for job {job_id} on attempt {attempt}")
        elif attempt < 5:
            delay_seconds = (2 ** attempt) * 60  # 2m, 4m, 8m, 16m, 32m
            logger.warning(
                f"Webhook delivery failed for job {job_id}, attempt {attempt}. "
                f"Retrying in {delay_seconds}s"
            )
            await ctx["redis"].enqueue_job(
                "retry_webhook_delivery",
                job_id,
                attempt + 1,
                _defer_by=delay_seconds,
            )
        else:
            logger.error(f"Webhook delivery failed for job {job_id} after {attempt} attempts — giving up")


async def recalculate_reputation(ctx, agent_id: str):
    """
    Recalculate an agent's reputation score.
    Called after every job completion or dispute resolution.
    """
    from sqlmodel import select
    from api.models import Agent
    from api.services.reputation import recalculate_agent_reputation

    async with ctx["session_maker"]() as session:
        result = await session.execute(select(Agent).where(Agent.id == agent_id))
        agent = result.scalar_one_or_none()

        if not agent:
            logger.warning(f"recalculate_reputation: agent {agent_id} not found")
            return

        new_score = await recalculate_agent_reputation(agent, session)
        logger.info(f"Reputation recalculated for agent {agent_id}: {new_score}")


# ARQ worker settings
def _get_redis_settings():
    """Return ARQ RedisSettings or None if Redis is disabled."""
    if not settings.redis_url or settings.redis_url.lower() in ("disabled", "none", ""):
        logger.warning("[STUB] Redis/ARQ disabled — background workers will not start")
        return None
    return arq.connections.RedisSettings.from_dsn(settings.redis_url)


class WorkerSettings:
    functions = [auto_release_escrow, retry_webhook_delivery, recalculate_reputation]
    on_startup = startup
    on_shutdown = shutdown
    redis_settings = _get_redis_settings()
    max_jobs = 10
    job_timeout = 300  # 5 minutes per job max
