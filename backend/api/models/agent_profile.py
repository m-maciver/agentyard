"""
AgentYard — AgentProfile model
Skill-registered agents with Ed25519 keypairs.
Separate from the Human-owned Agent model — these are OpenClaw-registered agents.
"""
from datetime import datetime, timezone
from typing import Optional

from sqlmodel import Field, SQLModel


class AgentProfile(SQLModel, table=True):
    __tablename__ = "agent_profiles"

    id: Optional[int] = Field(default=None, primary_key=True)
    agent_name: str = Field(unique=True, index=True, max_length=100)
    public_key: str = Field(unique=True, max_length=128)  # base64 Ed25519 pubkey
    role: str = Field(default="BUYER_ONLY")  # BUYER_ONLY | SELLER | BOTH
    capabilities: Optional[str] = Field(default=None, max_length=500)
    price_sats: Optional[int] = Field(default=None)
    wallet_id: Optional[str] = Field(default=None, max_length=256)
    wallet_balance_sats: int = Field(default=0)
    reputation_score: float = Field(default=0.0)
    total_jobs: int = Field(default=0)
    is_active: bool = Field(default=True)
    registered_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    github_user_id: Optional[str] = Field(default=None, max_length=100)

    # Listing approval
    approval_status: str = Field(default="pending")  # pending, approved, rejected
    seller_tier: str = Field(default="none")  # none, basic, premium


class AgentRegisterRequest(SQLModel):
    agent_name: str
    public_key: str          # hex Ed25519 pubkey
    role: str = "SELLER"     # BUYER_ONLY | SELLER | BOTH
    capabilities: Optional[str] = None
    specialty: Optional[str] = None  # Alias for capabilities (from CLI)
    description: Optional[str] = None  # Human-readable description
    price_sats: Optional[int] = None
    openclaw_user_id: Optional[str] = None  # GitHub user ID if linked
    lightning_address: Optional[str] = None  # From CLI wallet generation


class AgentProfilePublic(SQLModel):
    id: int
    agent_name: str
    public_key: str
    role: str
    capabilities: Optional[str]
    price_sats: Optional[int]
    wallet_id: Optional[str]
    wallet_balance_sats: int
    reputation_score: float
    total_jobs: int
    is_active: bool
    registered_at: datetime
    approval_status: str
    seller_tier: str
