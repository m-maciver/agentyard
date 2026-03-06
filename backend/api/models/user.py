"""
AgentYard — GitHub OAuth User model
Represents users authenticated via GitHub OAuth.
Separate from the legacy Human model (email/password).
"""
from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    github_id: int = Field(unique=True, index=True)
    github_username: str
    github_avatar: str
    github_email: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = Field(default=True)
    wallet_balance_sats: int = Field(default=0)
    agent_name: Optional[str] = None
    reputation_score: float = Field(default=0.0)
    total_jobs_completed: int = Field(default=0)
