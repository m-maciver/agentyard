"""
AgentYard — Agents router
CRUD for agent registry + skill-based AgentProfile registration.
"""
import hashlib
import logging
import os
import secrets
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query, status, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func
from sqlmodel import select, col

from api.database import get_session
from api.deps import get_agent_by_key, get_current_human, get_current_user, hash_api_key
from api.models import (
    Agent, AgentCreate, AgentPublic, AgentUpdate, Human, Job,
    AgentProfile, AgentRegisterRequest, AgentProfilePublic, User,
)
from config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/agents", tags=["agents"])
limiter = Limiter(key_func=get_remote_address)

# ─── AgentProfile endpoints (skill-based, Ed25519 keypair) ────────────────────


@router.post("/register", response_model=dict, status_code=status.HTTP_201_CREATED)
@limiter.limit("3/minute")
async def register_agent_profile(
    request: Request,
    body: AgentRegisterRequest,
    session: AsyncSession = Depends(get_session),
):
    """
    Register an OpenClaw agent with Ed25519 public key.
    Called by the AgentYard skill wizard after keypair generation.
    Public endpoint — authenticated by the public key itself.
    """
    # Check for existing agent with same name
    result = await session.execute(
        select(AgentProfile).where(AgentProfile.agent_name == body.agent_name)
    )
    existing = result.scalar_one_or_none()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error": "agent_already_registered",
                "message": f"Agent '{body.agent_name}' is already registered. To re-register, delete the existing config and run: openclaw skill install agentyard",
                "docs": "https://agentyard.xyz/docs#registration",
            },
        )

    # Validate role
    valid_roles = {"BUYER_ONLY", "SELLER", "BOTH"}
    if body.role not in valid_roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "invalid_role",
                "message": f"Invalid role '{body.role}'. Must be one of: {', '.join(valid_roles)}",
                "docs": "https://agentyard.xyz/docs#roles",
            },
        )

    # Accept specialty as alias for capabilities (CLI sends specialty)
    capabilities = body.capabilities or body.specialty or ""

    profile = AgentProfile(
        agent_name=body.agent_name,
        public_key=body.public_key,
        role=body.role,
        capabilities=capabilities,
        price_sats=body.price_sats,
        github_user_id=body.openclaw_user_id,
        approval_status="approved",  # CLI-registered agents are auto-approved
    )
    session.add(profile)
    await session.commit()
    await session.refresh(profile)

    logger.info("Agent registered: %s role=%s", profile.agent_name, profile.role)

    return {
        "agent_id": profile.id,
        "public_key": profile.public_key,
        "registered": True,
    }


@router.get("/marketplace", response_model=dict)
async def list_marketplace_agents(
    category: Optional[str] = Query(None, description="Filter by capabilities keyword"),
    specialty: Optional[str] = Query(None, description="Alias for category — filter by specialty"),
    sort: Optional[str] = Query("rating", description="Sort by: rating | price | jobs"),
    search: Optional[str] = Query(None, description="Search in agent name or capabilities"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_session),
):
    """List seller agents available on the marketplace."""
    from sqlmodel import or_

    # Accept specialty as alias for category
    filter_keyword = category or specialty

    query = select(AgentProfile).where(
        AgentProfile.is_active == True,
        AgentProfile.role.in_(["SELLER", "BOTH"]),  # type: ignore
    )

    if filter_keyword:
        query = query.where(col(AgentProfile.capabilities).contains(filter_keyword))
    if search:
        query = query.where(
            or_(
                col(AgentProfile.agent_name).contains(search),
                col(AgentProfile.capabilities).contains(search),
            )
        )

    # Sorting
    if sort == "price":
        query = query.order_by(col(AgentProfile.price_sats).asc())
    elif sort == "jobs":
        query = query.order_by(col(AgentProfile.total_jobs).desc())
    else:
        query = query.order_by(col(AgentProfile.reputation_score).desc())

    result = await session.execute(query.offset(offset).limit(limit))
    profiles = result.scalars().all()

    return {
        "agents": [AgentProfilePublic.model_validate(p) for p in profiles],
        "total": len(profiles),
        "limit": limit,
        "offset": offset,
    }





def generate_api_key() -> str:
    """Generate a new agent API key: ay_live_{32 random hex chars}"""
    return f"ay_live_{secrets.token_hex(32)}"


# UUID route registered FIRST to take priority
@router.get("/{agent_id}", response_model=AgentPublic)
async def get_agent(agent_id: UUID, session: AsyncSession = Depends(get_session)):
    """Get agent profile by ID (legacy JWT-registered agents)."""
    result = await session.execute(select(Agent).where(Agent.id == agent_id))
    agent = result.scalar_one_or_none()
    if not agent:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "agent_not_found",
                "message": f"Agent with ID '{agent_id}' not found. Check the ID or run: openclaw skill install agentyard",
                "docs": "https://agentyard.xyz/docs#agents",
            },
        )
    return agent


# Name route registered AFTER UUID route (lower priority)
@router.get("/{agent_name}", response_model=AgentProfilePublic)
async def get_agent_by_name(
    agent_name: str,
    session: AsyncSession = Depends(get_session),
):
    """Get agent profile by name (skill-registered agents + JWT agents)."""
    # Skip UUID-like strings (handled by the UUID endpoint above)
    import re
    UUID_PATTERN = re.compile(
        r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
        re.IGNORECASE,
    )
    if UUID_PATTERN.match(agent_name):
        raise HTTPException(
            status_code=404,
            detail={
                "error": "use_uuid_endpoint",
                "message": "This looks like a UUID. Use /agents/{uuid} for legacy agent lookups.",
                "docs": "https://agentyard.xyz/docs#agents",
            },
        )

    # Search both AgentProfile and Agent tables
    # First try AgentProfile (skill-registered)
    result = await session.execute(
        select(AgentProfile).where(AgentProfile.agent_name == agent_name)
    )
    profile = result.scalar_one_or_none()
    if profile:
        return profile
    
    # Fall back to Agent table (JWT-registered agents)
    agent_result = await session.execute(
        select(Agent).where(Agent.name == agent_name)
    )
    agent = agent_result.scalar_one_or_none()
    if agent:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "use_uuid_endpoint",
                "message": f"Agent '{agent_name}' is a legacy agent. Use /agents/{agent.id} to fetch its profile.",
                "docs": "https://agentyard.xyz/docs#agents",
            },
        )
    
    raise HTTPException(
        status_code=404,
        detail={
            "error": "agent_not_found",
            "message": f"Agent '{agent_name}' is not registered. Run: openclaw skill install agentyard",
            "docs": "https://agentyard.xyz/docs#registration",
        },
    )


@router.get("/{agent_name}/balance", response_model=dict)
async def get_agent_balance(
    agent_name: str,
    current_agent: Agent = Depends(get_agent_by_key),
    session: AsyncSession = Depends(get_session),
):
    """Get agent's Lightning wallet balance. Requires agent auth."""
    result = await session.execute(
        select(AgentProfile).where(AgentProfile.agent_name == agent_name)
    )
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "agent_not_found",
                "message": f"Agent '{agent_name}' is not registered. Run: openclaw skill install agentyard",
                "docs": "https://agentyard.xyz/docs#registration",
            },
        )

    # Stub mode or no wallet yet
    lightning_stub = os.environ.get("LIGHTNING_STUB", "").lower() in ("true", "1") or \
        settings.lnbits_url in ("stub", "")

    if lightning_stub or not profile.wallet_id:
        return {"balance_sats": profile.wallet_balance_sats}

    # Live LNbits query
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(
                f"{settings.lnbits_url}/api/v1/wallet",
                headers={"X-Api-Key": settings.lnbits_escrow_wallet_inkey},
            )
            if resp.status_code == 200:
                data = resp.json()
                balance_sats = data.get("balance", 0) // 1000  # msat → sat
                return {"balance_sats": balance_sats}
    except Exception as e:
        logger.warning("LNbits balance check failed for %s: %s", agent_name, e)

    return {"balance_sats": profile.wallet_balance_sats}


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


@router.put("/{agent_id}", response_model=AgentPublic)
async def update_agent(
    agent_id: UUID,
    body: AgentUpdate,
    current_agent: Agent = Depends(get_agent_by_key),
    session: AsyncSession = Depends(get_session),
):
    """Update own agent profile. Agent API key auth required."""
    if current_agent.id != agent_id:
        raise HTTPException(
            status_code=403,
            detail={
                "error": "forbidden",
                "message": "You can only update your own agent profile.",
                "docs": "https://agentyard.xyz/docs#agents",
            },
        )

    result = await session.execute(select(Agent).where(Agent.id == agent_id))
    agent = result.scalar_one_or_none()
    if not agent:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "agent_not_found",
                "message": f"Agent with ID '{agent_id}' not found.",
                "docs": "https://agentyard.xyz/docs#agents",
            },
        )

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
    current_agent: Agent = Depends(get_agent_by_key),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_session),
):
    """Get job history for an agent (as client or provider). Requires agent auth."""
    from sqlmodel import or_
    
    # Verify agent can only view their own jobs or is an admin (TODO: add admin check)
    if current_agent.id != agent_id:
        raise HTTPException(
            status_code=403,
            detail={
                "error": "forbidden",
                "message": "You can only view your own job history. Check the agent ID in your request.",
                "docs": "https://agentyard.xyz/docs#jobs",
            },
        )
    
    result = await session.execute(
        select(Agent).where(Agent.id == agent_id)
    )
    agent = result.scalar_one_or_none()
    if not agent:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "agent_not_found",
                "message": f"Agent with ID '{agent_id}' not found.",
                "docs": "https://agentyard.xyz/docs#agents",
            },
        )

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
