"""
AgentYard — Reputation calculation service
"""
import math
import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from api.models import Agent

logger = logging.getLogger(__name__)


def calculate_reputation(jobs_completed: int, jobs_disputed: int, avg_delivery_time_mins: float = 60.0) -> float:
    """
    Calculate reputation score 0.0-100.0.
    
    Args:
        jobs_completed: Number of completed jobs (including won disputes)
        jobs_disputed: Number of disputes lost
        avg_delivery_time_mins: Average delivery time in minutes
    """
    if jobs_completed == 0:
        return 0.0

    dispute_rate = jobs_disputed / max(jobs_completed, 1)
    base_score = (1 - dispute_rate) * 100
    speed_bonus = max(0, 10 - (avg_delivery_time_mins / 60))
    volume_bonus = min(10, jobs_completed / 10)
    return round(min(100, base_score + speed_bonus + volume_bonus), 1)


def calculate_stake_pct(reputation_score: float, job_price_sats: int) -> float:
    """
    Calculate required stake percentage for a job.
    
    - New agents (rep=0): 30% stake
    - High-rep agents: minimum 5%
    - Large jobs (>10k sats): +10% regardless of rep
    """
    if reputation_score == 0:
        base_pct = 0.30
    else:
        base_pct = max(0.05, 0.30 - (reputation_score / 100) * 0.25)

    # Large job bump
    if job_price_sats > 10_000:
        base_pct = min(0.50, base_pct + 0.10)

    return base_pct


def calculate_stake_sats(price_sats: int, reputation_score: float) -> int:
    """Calculate stake amount in sats."""
    pct = calculate_stake_pct(reputation_score, price_sats)
    return math.ceil(price_sats * pct)


def calculate_platform_fee(price_sats: int, reputation_score: float = 0.0) -> int:
    """
    Calculate platform fee.
    12% default, 10% for high-rep agents (score > 80).
    """
    fee_rate = 0.10 if reputation_score > 80 else 0.12
    return math.ceil(price_sats * fee_rate)


def get_max_job_sats(reputation_score: float, jobs_completed: int, is_verified: bool) -> int:
    """
    Job size cap based on reputation tier.
    """
    if not is_verified or jobs_completed < 5:
        return 50_000

    if reputation_score < 30:
        return 100_000
    elif reputation_score < 60:
        return 300_000
    elif reputation_score < 80:
        return 1_000_000
    else:
        return 10_000_000  # effectively uncapped


async def recalculate_agent_reputation(agent, session) -> float:
    """
    Recalculate and update an agent's reputation score in the database.
    Called after every job completion or dispute resolution.
    """
    from datetime import timezone
    from datetime import datetime

    new_score = calculate_reputation(
        jobs_completed=agent.jobs_completed,
        jobs_disputed=agent.jobs_disputed,
    )
    old_score = agent.reputation_score
    agent.reputation_score = new_score
    agent.stake_percent = calculate_stake_pct(new_score, 1000) * 100
    agent.max_job_sats = get_max_job_sats(new_score, agent.jobs_completed, agent.is_verified)
    agent.updated_at = datetime.now(timezone.utc)

    session.add(agent)
    await session.commit()
    await session.refresh(agent)

    logger.info(f"Agent {agent.id} reputation updated: {old_score} → {new_score}")
    return new_score
