"""
AgentYard — Wallets router
Lightning wallet creation and management for skill-registered agents.
"""
import logging
import os
from typing import Optional

import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, SQLModel

from api.database import get_session
from api.models import AgentProfile
from config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/wallets", tags=["wallets"])

BACKEND_HOST = os.environ.get("RAILWAY_PUBLIC_DOMAIN", "agentyard-production.up.railway.app")


class WalletCreateRequest(SQLModel):
    agent_name: str
    public_key: str  # must match registered agent


def _is_stub_mode() -> bool:
    """Check if Lightning is in stub mode (no real LNbits)."""
    return (
        os.environ.get("LIGHTNING_STUB", "").lower() in ("true", "1")
        or settings.lnbits_url in ("stub", "", "https://demo.lnbits.com")
    )


@router.post("/create", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_wallet(
    body: WalletCreateRequest,
    session: AsyncSession = Depends(get_session),
):
    """
    Create a Lightning sub-wallet for a registered agent.
    Called by the AgentYard skill wizard after agent registration.
    
    Returns wallet_id and lightning_address.
    """
    # Verify agent exists and pubkey matches
    result = await session.execute(
        select(AgentProfile).where(AgentProfile.agent_name == body.agent_name)
    )
    profile = result.scalar_one_or_none()

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent '{body.agent_name}' not found. Register first via POST /agents/register",
        )

    if profile.public_key != body.public_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Public key mismatch — cannot create wallet for this agent",
        )

    # Return existing wallet if already created
    if profile.wallet_id:
        lightning_address = f"{body.agent_name}@{BACKEND_HOST}"
        return {
            "wallet_id": profile.wallet_id,
            "lightning_address": lightning_address,
            "balance_sats": profile.wallet_balance_sats,
        }

    # Stub mode — return fake wallet
    if _is_stub_mode():
        wallet_id = f"stub_{body.agent_name}"
        lightning_address = f"{body.agent_name}@{BACKEND_HOST}"

        profile.wallet_id = wallet_id
        profile.wallet_balance_sats = 0
        session.add(profile)
        await session.commit()
        await session.refresh(profile)

        logger.info("Stub wallet created for %s: %s", body.agent_name, lightning_address)

        return {
            "wallet_id": wallet_id,
            "lightning_address": lightning_address,
            "balance_sats": 0,
        }

    # Live LNbits sub-wallet creation
    lnbits_admin_key = os.environ.get("LNBITS_ADMIN_KEY", settings.lnbits_escrow_wallet_adminkey)
    if not lnbits_admin_key:
        logger.warning("No LNbits admin key configured — falling back to stub")
        wallet_id = f"stub_{body.agent_name}"
        lightning_address = f"{body.agent_name}@{BACKEND_HOST}"

        profile.wallet_id = wallet_id
        session.add(profile)
        await session.commit()

        return {
            "wallet_id": wallet_id,
            "lightning_address": lightning_address,
            "balance_sats": 0,
        }

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(
                f"{settings.lnbits_url}/api/v1/account",
                headers={
                    "X-Api-Key": lnbits_admin_key,
                    "Content-Type": "application/json",
                },
                json={"name": f"agentyard_{body.agent_name}"},
            )
            resp.raise_for_status()
            data = resp.json()

        wallet_id = data.get("id") or data.get("wallet", {}).get("id", f"lnbits_{body.agent_name}")
        lightning_address = f"{body.agent_name}@{BACKEND_HOST}"

        profile.wallet_id = wallet_id
        profile.wallet_balance_sats = 0
        session.add(profile)
        await session.commit()
        await session.refresh(profile)

        logger.info("LNbits wallet created for %s: wallet_id=%s", body.agent_name, wallet_id)

        return {
            "wallet_id": wallet_id,
            "lightning_address": lightning_address,
            "balance_sats": 0,
        }

    except httpx.HTTPStatusError as e:
        logger.error("LNbits wallet creation failed for %s: %s", body.agent_name, e)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"LNbits wallet creation failed: {e.response.status_code}",
        )
    except Exception as e:
        logger.error("Wallet creation error for %s: %s", body.agent_name, e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Wallet creation failed — check LNbits connectivity",
        )
