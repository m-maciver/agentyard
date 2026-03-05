"""
AgentYard — Agents router
CRUD for agent registry.
"""
import hashlib
import secrets
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func
from sqlmodel import select, col

from api.database import get_session
from api.deps import get_agent_by_key, get_current_human, hash_api_key
from api.models import Agent, AgentCreate, AgentPublic, AgentUpdate, Human, Job

router = APIRouter(prefix="/agents", tags=["agents"])


def generate_api_key() -> str:
    """Generate a new agent API key: ay_live_{32 random hex chars}"""
    return f"ay_live_{secrets.token_hex(32)}"


@router.post("", response_model=dict, status_code=status.HTTP_201_CREATED)
async def register_agent(
    body: AgentCreate,
    human: Human = Depends(get_current_human),
    session: AsyncSession = Depends(get_session),
):
    """
    Register a new agent. Returns the raw API key ONCE — store it securely.
    Requires human JWT auth.
    """
    raw_key = generate_api_key()
    key_hash = hash_api_key(raw_key)

    agent = Agent(
        name=body.name,
        specialty=body.specialty,
        soul_excerpt=body.soul_excerpt,
        webhook_url=body.webhook_url,
        delivery_url=body.delivery_url,
        price_per_task_sats=body.price_per_task_sats,
        lnbits_wallet_id=body.lnbits_wallet_id,
        lnbits_invoice_key=body.lnbits_invoice_key,
        owner_id=human.id,
        api_key_hash=key_hash,
    )
    session.add(agent)
    await session.commit()
    await session.refresh(agent)

    return {
        "agent": AgentPublic.model_validate(agent),
        "api_key": raw_key,
        "warning": "Store this API key securely. It will NOT be shown again.",
    }


@router.get("", response_model=dict)
async def list_agents(
    specialty: Optional[str] = Query(None, description="Substring match on specialty"),
    min_reputation: Optional[float] = Query(None, ge=0, le=100),
    max_price_sats: Optional[int] = Query(None, ge=1),
    available: Optional[bool] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_session),
):
    """List and search agents."""
    query = select(Agent).where(Agent.is_active == True)

    if specialty:
        query = query.where(col(Agent.specialty).contains(specialty))
    if min_reputation is not None:
        query = query.where(Agent.reputation_score >= min_reputation)
    if max_price_sats is not None:
        query = query.where(Agent.price_per_task_sats <= max_price_sats)

    # Count total with proper COUNT() query
    count_query = select(func.count()).select_from(query.subquery())
    count_result = await session.execute(count_query)
    total = count_result.scalar_one()

    # Apply pagination
    query = query.offset(offset).limit(limit).order_by(col(Agent.reputation_score).desc())
    result = await session.execute(query)
    agents = result.scalars().all()

    return {
        "agents": [AgentPublic.model_validate(a) for a in agents],
        "total": total,
        "limit": limit,
        "offset": offset,
    }


@router.get("/{agent_id}", response_model=AgentPublic)
async def get_agent(agent_id: UUID, session: AsyncSession = Depends(get_session)):
    """Get agent profile by ID."""
    result = await session.execute(select(Agent).where(Agent.id == agent_id))
    agent = result.scalar_one_or_none()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent


@router.put("/{agent_id}", response_model=AgentPublic)
async def update_agent(
    agent_id: UUID,
    body: AgentUpdate,
    current_agent: Agent = Depends(get_agent_by_key),
    session: AsyncSession = Depends(get_session),
):
    """Update own agent profile. Agent API key auth required."""
    if current_agent.id != agent_id:
        raise HTTPException(status_code=403, detail="Can only update your own agent")

    result = await session.execute(select(Agent).where(Agent.id == agent_id))
    agent = result.scalar_one_or_none()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    update_data = body.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(agent, key, value)
    agent.updated_at = datetime.now(timezone.utc)

    session.add(agent)
    await session.commit()
    await session.refresh(agent)
    return agent


@router.get("/{agent_id}/jobs", response_model=dict)
async def get_agent_jobs(
    agent_id: UUID,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_session),
):
    """Get job history for an agent (as client or provider)."""
    from sqlmodel import or_
    result = await session.execute(
        select(Agent).where(Agent.id == agent_id)
    )
    agent = result.scalar_one_or_none()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    jobs_result = await session.execute(
        select(Job)
        .where(
            or_(Job.client_agent_id == agent_id, Job.provider_agent_id == agent_id)
        )
        .offset(offset)
        .limit(limit)
        .order_by(col(Job.created_at).desc())
    )
    jobs = jobs_result.scalars().all()

    return {
        "jobs": [
            {
                "id": str(j.id),
                "status": j.status,
                "price_sats": j.price_sats,
                "role": "client" if j.client_agent_id == agent_id else "provider",
                "created_at": j.created_at.isoformat(),
                "completed_at": j.completed_at.isoformat() if j.completed_at else None,
            }
            for j in jobs
        ],
        "total": len(jobs),
    }
