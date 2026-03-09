"""
AgentYard — Auth router
GitHub OAuth: GET /auth/github, GET /auth/github/callback, GET /auth/me, POST /auth/logout
Sellers authenticate via GitHub OAuth only. Email/password registration removed.
"""
import hashlib
import secrets
import time
from datetime import datetime, timezone, timedelta

import httpx
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import RedirectResponse
from jose import jwt
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from api.database import get_session
from api.deps import get_current_user
from api.models import User
from config import settings

limiter = Limiter(key_func=get_remote_address)

router = APIRouter(prefix="/auth", tags=["auth"])

# OAuth state storage (in-memory for MVP, can be Redis later)
_oauth_states: dict[str, float] = {}


# ─── Helpers ──────────────────────────────────────────────────────────────────

def create_github_jwt(user: User) -> str:
    """Issue a 7-day JWT for a GitHub OAuth user."""
    now = datetime.now(timezone.utc)
    expire = now + timedelta(days=7)
    payload = {
        "sub": str(user.id),
        "github_username": user.github_username,
        "github_avatar": user.github_avatar,
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


# ─── GitHub OAuth Routes ───────────────────────────────────────────────────────

@router.get("/github", tags=["auth"])
@limiter.limit("10/minute")
async def github_login(request: Request):
    """Redirect to GitHub OAuth authorization page."""
    # Generate and store OAuth state for CSRF prevention
    state = secrets.token_urlsafe(32)
    _oauth_states[state] = time.time()
    
    github_auth_url = (
        f"https://github.com/login/oauth/authorize"
        f"?client_id={settings.github_client_id}"
        f"&scope=read:user,user:email"
        f"&redirect_uri={settings.github_callback_url}"
        f"&state={state}"
    )
    return RedirectResponse(github_auth_url)


@router.get("/github/callback", tags=["auth"])
@limiter.limit("10/minute")
async def github_callback(request: Request, code: str, state: str = None, session: AsyncSession = Depends(get_session)):
    """
    Handle GitHub OAuth callback.
    1. Validate state parameter (CSRF prevention)
    2. Exchange code for access token
    3. Fetch user profile from GitHub
    4. Create or update User in DB
    5. Issue JWT and redirect to frontend with token
    """
    # Validate state parameter
    if not state or state not in _oauth_states:
        raise HTTPException(status_code=400, detail="Invalid OAuth state")
    
    # Clean up expired states (>10 min old)
    now = time.time()
    _oauth_states_copy = _oauth_states.copy()
    for k, v in _oauth_states_copy.items():
        if now - v > 600:
            del _oauth_states[k]
    
    # Consume the state
    del _oauth_states[state]
    
    # Exchange code for GitHub access token
    async with httpx.AsyncClient() as client:
        token_resp = await client.post(
            "https://github.com/login/oauth/access_token",
            headers={"Accept": "application/json"},
            json={
                "client_id": settings.github_client_id,
                "client_secret": settings.github_client_secret,
                "code": code,
            },
        )

    token_data = token_resp.json()
    access_token = token_data.get("access_token")

    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="GitHub OAuth failed — no access token returned",
        )

    # Fetch GitHub user profile
    async with httpx.AsyncClient() as client:
        user_resp = await client.get(
            "https://api.github.com/user",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Accept": "application/vnd.github+json",
            },
        )

    if user_resp.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to fetch GitHub user profile",
        )

    gh_data = user_resp.json()
    github_id = gh_data["id"]
    github_username = gh_data["login"]
    github_avatar = gh_data.get("avatar_url", "")
    github_email = gh_data.get("email")

    # Create or update User in DB
    result = await session.execute(select(User).where(User.github_id == github_id))
    user = result.scalar_one_or_none()

    now = datetime.now(timezone.utc)
    if user:
        # Update existing user
        user.github_username = github_username
        user.github_avatar = github_avatar
        user.github_email = github_email
        user.last_login = now
        session.add(user)
    else:
        # Create new user
        user = User(
            github_id=github_id,
            github_username=github_username,
            github_avatar=github_avatar,
            github_email=github_email,
            created_at=now,
            last_login=now,
        )
        session.add(user)

    await session.commit()
    await session.refresh(user)

    # Issue JWT
    jwt_token = create_github_jwt(user)

    # Redirect to frontend with token (use fragment instead of query param to prevent logging)
    redirect_url = f"{settings.frontend_url}/#token={jwt_token}"
    return RedirectResponse(redirect_url)


@router.get("/me", tags=["auth"])
async def get_me(current_user: User = Depends(get_current_user)):
    """Return current GitHub OAuth user profile."""
    return {
        "id": current_user.id,
        "githubUsername": current_user.github_username,
        "githubAvatar": current_user.github_avatar,
        "agentName": current_user.agent_name,
        "walletBalance": current_user.wallet_balance_sats,
        "reputationScore": current_user.reputation_score,
        "totalJobsCompleted": current_user.total_jobs_completed,
    }


@router.post("/logout", tags=["auth"])
async def logout():
    """
    Logout endpoint. JWT is stateless — actual logout is client-side (delete the token).
    This endpoint exists for completeness / future server-side revocation.
    """
    return {"message": "Logged out. Delete the token on the client."}


# Email/password registration removed. Sellers authenticate via GitHub OAuth only.
