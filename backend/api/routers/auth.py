"""
AgentYard — Auth router
POST /auth/register, POST /auth/login, GET /auth/me
"""
import os
import hashlib
import secrets
from datetime import datetime, timezone, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from jose import jwt
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from api.database import get_session
from api.deps import get_current_human, hash_api_key
from api.models import Human, HumanCreate, HumanPublic
from config import settings

router = APIRouter(prefix="/auth", tags=["auth"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(human_id: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(hours=settings.jwt_expiry_hours)
    payload = {
        "sub": human_id,
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


@router.post("/register", response_model=HumanPublic, status_code=status.HTTP_201_CREATED)
async def register(body: HumanCreate, session: AsyncSession = Depends(get_session)):
    """Register a new human account."""
    # Check email not taken
    result = await session.execute(select(Human).where(Human.email == body.email))
    existing = result.scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    human = Human(
        email=body.email,
        password_hash=hash_password(body.password),
    )
    session.add(human)
    await session.commit()
    await session.refresh(human)
    return human


@router.post("/login")
async def login(body: HumanCreate, session: AsyncSession = Depends(get_session)):
    """Login and get JWT access token."""
    result = await session.execute(select(Human).where(Human.email == body.email))
    human = result.scalar_one_or_none()

    if not human or not verify_password(body.password, human.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    token = create_access_token(str(human.id))
    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_in": settings.jwt_expiry_hours * 3600,
    }


@router.get("/me", response_model=HumanPublic)
async def me(human: Human = Depends(get_current_human)):
    """Get current human profile."""
    return human
