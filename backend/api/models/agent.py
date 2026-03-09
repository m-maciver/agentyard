"""
AgentYard — Agent model
"""
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


class Agent(SQLModel, table=True):
    __tablename__ = "agents"

    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    owner_id: Optional[UUID] = Field(default=None, foreign_key="humans.id")

    name: str = Field(max_length=100)
    specialty: str = Field(max_length=500)
    soul_excerpt: str = Field(default="", max_length=500)
    webhook_url: str = Field(default="", max_length=2048)
    delivery_url: str = Field(default="", max_length=2048)
    price_per_task_sats: int = Field(default=1000)
    lnbits_wallet_id: str = Field(default="")
    lnbits_invoice_key: str = Field(default="")

    # API key (stored as hash — raw key returned once at registration)
    api_key_hash: str = Field(default="")

    # Reputation & trust
    reputation_score: float = Field(default=0.0)
    stake_balance_sats: int = Field(default=0)
    stake_percent: float = Field(default=30.0)

    # Stats
    job_count: int = Field(default=0)
    jobs_completed: int = Field(default=0)
    jobs_disputed: int = Field(default=0)
    jobs_won: int = Field(default=0)
    jobs_disputed_lost: int = Field(default=0)  # disputes where agent was at fault

    # Job Success Score — primary trust signal shown to buyers
    jss: float = Field(default=100.0)

    # Marketplace status — updated automatically when JSS drops below thresholds
    approval_status: str = Field(default="active")  # active | rate_limited | suspended

    # Job size caps
    max_job_sats: int = Field(default=50000)

    # Status
    is_active: bool = Field(default=True)
    is_verified: bool = Field(default=False)

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AgentCreate(SQLModel):
    name: str
    specialty: str
    soul_excerpt: str = ""
    webhook_url: str = ""
    delivery_url: str = ""
    price_per_task_sats: int = 1000
    lnbits_wallet_id: str = ""
    lnbits_invoice_key: str = ""


class AgentUpdate(SQLModel):
    name: Optional[str] = None
    specialty: Optional[str] = None
    soul_excerpt: Optional[str] = None
    webhook_url: Optional[str] = None
    delivery_url: Optional[str] = None
    price_per_task_sats: Optional[int] = None
    lnbits_wallet_id: Optional[str] = None
    lnbits_invoice_key: Optional[str] = None
    is_active: Optional[bool] = None


class AgentPublic(SQLModel):
    id: UUID
    name: str
    specialty: str
    soul_excerpt: str
    webhook_url: str
    delivery_url: str
    price_per_task_sats: int
    reputation_score: float
    stake_balance_sats: int
    stake_percent: float
    job_count: int
    jobs_completed: int
    jobs_disputed: int
    max_job_sats: int
    is_active: bool
    is_verified: bool
    created_at: datetime
    jss: float = 100.0
    approval_status: str = "active"
