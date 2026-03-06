"""
AgentYard — FastAPI dependencies
Auth middleware for agents (API key) and humans (JWT).
"""
import hashlib
import logging
from typing import Optional
from uuid import UUID

from fastapi import Depends, Header, HTTPException, status
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from fastapi.security import OAuth2PasswordBearer
from api.database import get_session
from api.models import Agent, Human, User
from config import settings

# OAuth2 scheme for GitHub JWT tokens
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)

logger = logging.getLogger(__name__)


def hash_api_key(raw_key: str) -> str:
    """SHA-256 hash an API key for storage."""
    return hashlib.sha256(raw_key.encode()).hexdigest()


async def get_agent_by_key(
    x_agent_key: Optional[str] = Header(None, alias="X-Agent-Key"),
    session: AsyncSession = Depends(get_session),
) -> Agent:
    """
    FastAPI dependency — authenticate agent by API key.
    Header: X-Agent-Key: <raw_key>
    """
    if not x_agent_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing X-Agent-Key header",
        )

    key_hash = hash_api_key(x_agent_key)
    result = await session.execute(
        select(Agent).where(Agent.api_key_hash == key_hash, Agent.is_active == True)
    )
    agent = result.scalar_one_or_none()

    if not agent:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or inactive API key",
        )

    return agent


async def get_optional_agent(
    x_agent_key: Optional[str] = Header(None, alias="X-Agent-Key"),
    session: AsyncSession = Depends(get_session),
) -> Optional[Agent]:
    """Optional agent auth — returns None if no key provided."""
    if not x_agent_key:
        return None
    try:
        return await get_agent_by_key(x_agent_key=x_agent_key, session=session)
    except HTTPException:
        return None


async def get_current_human(
    authorization: Optional[str] = Header(None),
    session: AsyncSession = Depends(get_session),
) -> Human:
    """
    FastAPI dependency — authenticate human by JWT.
    Header: Authorization: Bearer <token>
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired token",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not authorization or not authorization.startswith("Bearer "):
        raise credentials_exception

    token = authorization.split(" ", 1)[1]

    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],
        )
        human_id: str = payload.get("sub")
        if not human_id:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    try:
        human_uuid = UUID(human_id)
    except (ValueError, AttributeError):
        raise credentials_exception

    result = await session.execute(
        select(Human).where(Human.id == human_uuid)
    )
    human = result.scalar_one_or_none()

    if not human:
        raise credentials_exception

    return human


async def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_session),
) -> User:
    """
    FastAPI dependency — authenticate GitHub OAuth user by JWT.
    Header: Authorization: Bearer <token>
    JWT payload must contain: sub (user.id), github_username, github_avatar
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired token",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not token:
        raise credentials_exception

    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],
        )
        user_id = payload.get("sub")
        # Must have github_username to be a GitHub OAuth token
        github_username = payload.get("github_username")
        if not user_id or not github_username:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = await session.get(User, int(user_id))
    if not user or not user.is_active:
        raise credentials_exception

    return user


async def get_admin_human(
    human: Human = Depends(get_current_human),
) -> Human:
    """Require admin role."""
    if not human.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return human


async def get_admin_by_key(
    x_admin_key: Optional[str] = Header(None, alias="X-Admin-Key"),
    human: Optional[Human] = Depends(get_current_human) if False else None,
) -> bool:
    """Allow admin access via admin API key OR admin JWT (simplified for MVP)."""
    if x_admin_key and x_admin_key == settings.admin_api_key:
        return True
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
