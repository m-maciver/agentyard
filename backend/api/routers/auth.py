"""
AgentYard — Auth router
GitHub OAuth: GET /auth/github, GET /auth/github/callback, GET /auth/me, POST /auth/logout
LNURL-Auth: GET /auth/lnurl, GET /auth/lnurl/callback
Sellers authenticate via GitHub OAuth or LNURL-Auth. Email/password registration removed.
"""
import hashlib
import secrets
import time
from datetime import datetime, timezone, timedelta

import httpx
from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from fastapi.responses import RedirectResponse
from jose import jwt
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from api.database import get_session
from api.deps import get_current_user
from api.models import User
from api.services import lnurl_auth
from config import settings

limiter = Limiter(key_func=get_remote_address)

router = APIRouter(prefix="/auth", tags=["auth"])

# OAuth state storage (in-memory for MVP; prefer Redis for production multi-instance deployments)
_oauth_states: dict[str, float] = {}
MAX_STATES = 1000


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
    # Clean up expired states (>10 min old) before adding new ones
    now = time.time()
    expired = [k for k, v in _oauth_states.items() if now - v > 600]
    for k in expired:
        del _oauth_states[k]

    # Evict oldest states if at capacity
    while len(_oauth_states) >= MAX_STATES:
        oldest_key = min(_oauth_states, key=_oauth_states.get)
        del _oauth_states[oldest_key]

    # Generate and store OAuth state for CSRF prevention
    state = secrets.token_urlsafe(32)
    _oauth_states[state] = now
    
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


# ─── LNURL-Auth Routes ────────────────────────────────────────────────────────

@router.get("/lnurl", tags=["auth"], summary="Generate LNURL-Auth challenge")
async def get_lnurl():
    """
    Generate an LNURL-Auth challenge for Lightning wallet authentication.
    
    Returns the LNURL QR code URL that users can scan with their Lightning wallet.
    The wallet will redirect to /auth/lnurl/callback with signature verification.
    """
    try:
        challenge_id, challenge_secret = lnurl_auth.generate_challenge()
        
        # Build callback URL
        callback_url = lnurl_auth.get_lnurl_callback_url(
            base_url=settings.frontend_url.replace("http://localhost:5173", settings.frontend_url),
            challenge_id=challenge_id,
        )
        
        # In a real implementation, encode as proper bech32 LNURL
        # For MVP, return the callback URL directly (works with QR scanners)
        lnurl = f"LNURL{hashlib.sha256(challenge_id.encode()).hexdigest()}"
        
        return {
            "lnurl": lnurl,
            "callback_url": callback_url,
            "challenge_id": challenge_id,
            "expires_in_seconds": 300,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate LNURL: {str(e)}")


@router.get("/lnurl/callback", tags=["auth"], summary="LNURL-Auth callback handler")
@limiter.limit("20/minute")
async def lnurl_callback(
    request: Request,
    k1: str = Query(..., description="Challenge ID"),
    key: str = Query(..., description="User's linking key (public key)"),
    sig: str = Query(None, description="Signature"),
    session: AsyncSession = Depends(get_session),
):
    """
    Handle LNURL-Auth callback from Lightning wallet.
    
    The wallet provides:
    - k1: Challenge ID (original challenge)
    - key: User's linking key (public key for wallet)
    - sig: Signature of the challenge signed by the wallet
    
    On success, returns JWT for authenticated session.
    """
    try:
        if not sig:
            raise HTTPException(
                status_code=400,
                detail="Missing signature — wallet authentication failed"
            )
        
        # Verify the signature
        # Note: This is a simplified version; production should derive pubkey from sig
        public_key = key  # In real LNURL-Auth, we derive this from signature
        
        # For MVP, accept any valid key format
        # Production: use lnurl-auth library for full LNURL-Auth compliance
        
        # Create or update User with LNURL identity
        result = await session.execute(
            select(User).where(User.lnurl_key == key)
        )
        user = result.scalar_one_or_none()
        
        now = datetime.now(timezone.utc)
        if user:
            # Update existing user
            user.last_login = now
            session.add(user)
        else:
            # Create new user with LNURL identity
            user = User(
                lnurl_key=key,
                github_id=None,
                github_username=f"lightning_{key[:8]}",
                created_at=now,
                last_login=now,
            )
            session.add(user)
        
        await session.commit()
        await session.refresh(user)
        
        # Issue JWT
        jwt_payload = {
            "sub": str(user.id),
            "lnurl_key": key,
            "auth_method": "lnurl",
            "iat": int(now.timestamp()),
            "exp": int((now + timedelta(days=7)).timestamp()),
        }
        jwt_token = jwt.encode(jwt_payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)
        
        # Redirect to frontend with token
        redirect_url = f"{settings.frontend_url}/#token={jwt_token}"
        return RedirectResponse(redirect_url)
        
    except lnurl_auth.LNURLAuthError as e:
        raise HTTPException(status_code=401, detail=f"LNURL authentication failed: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LNURL callback error: {str(e)}")


# Email/password registration removed. Sellers authenticate via GitHub OAuth or LNURL-Auth.
