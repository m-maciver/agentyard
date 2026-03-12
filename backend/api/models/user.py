"""
AgentYard — User model
Represents users authenticated via GitHub OAuth or LNURL-Auth.
Separate from the legacy Human model (email/password).
"""
from datetime import datetime, timezone
from typing import Optional

from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    # GitHub OAuth fields (optional if using LNURL-Auth)
    github_id: Optional[int] = Field(default=None, unique=True, index=True)
    github_username: Optional[str] = None
    github_avatar: Optional[str] = None
    github_email: Optional[str] = None
    # LNURL-Auth fields (optional if using GitHub OAuth)
    lnurl_key: Optional[str] = Field(default=None, unique=True, index=True)
    # User fields
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_login: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    is_active: bool = Field(default=True)
    wallet_balance_sats: int = Field(default=0)
    agent_name: Optional[str] = None
    reputation_score: float = Field(default=0.0)
    total_jobs_completed: int = Field(default=0)
