"""
AgentYard — Job model
"""
from datetime import datetime, timezone
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


class JobStatus(str, Enum):
    DRAFT = "draft"
    AWAITING_PAYMENT = "awaiting_payment"
    ESCROWED = "escrowed"
    IN_PROGRESS = "in_progress"
    DELIVERED = "delivered"
    DISPUTED = "disputed"
    COMPLETE = "complete"
    CANCELLED = "cancelled"
    FAILED = "failed"


class Job(SQLModel, table=True):
    __tablename__ = "jobs"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    client_agent_id: UUID = Field(foreign_key="agents.id")
    provider_agent_id: UUID = Field(foreign_key="agents.id")

    # Job details
    title: str = Field(default="")
    description: str = Field(default="")
    task_input: Optional[str] = Field(default=None)  # JSON string

    # Financials
    price_sats: int = Field(ge=1)
    platform_fee_sats: int = Field(default=0)
    stake_sats: int = Field(default=0)

    # Status
    status: JobStatus = Field(default=JobStatus.DRAFT)

    # Payment
    payment_hash: Optional[str] = Field(default=None)
    escrow_invoice: Optional[str] = Field(default=None)  # bolt11 invoice

    # Delivery
    delivery_channel: str = Field(default="webhook")  # webhook | discord | email
    delivery_target: Optional[str] = Field(default=None)
    output_payload: Optional[str] = Field(default=None)  # JSON string
    output_url: Optional[str] = Field(default=None)

    # Timestamps
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    started_at: Optional[datetime] = Field(default=None)
    delivered_at: Optional[datetime] = Field(default=None)
    auto_release_at: Optional[datetime] = Field(default=None)
    completed_at: Optional[datetime] = Field(default=None)
    disputed_at: Optional[datetime] = Field(default=None)

    # Set when buyer explicitly accepts — enables instant release vs waiting for the window
    accepted_at: Optional[datetime] = Field(default=None)
    accepted_by: Optional[str] = Field(default=None)  # user/agent id of buyer who accepted

    # Dispute
    dispute_reason: Optional[str] = Field(default=None)
    dispute_resolved_by: Optional[str] = Field(default=None)
    dispute_resolution: Optional[str] = Field(default=None)  # "client" | "provider"


class JobCreate(SQLModel):
    provider_agent_id: UUID
    title: str = ""
    description: str
    task_input: Optional[dict] = Field(default={})
    delivery_channel: str = "webhook"
    delivery_target: Optional[str] = None


class JobPublic(SQLModel):
    id: UUID
    client_agent_id: UUID
    provider_agent_id: UUID
    title: str
    description: str
    price_sats: int
    platform_fee_sats: int
    stake_sats: int
    status: JobStatus
    payment_hash: Optional[str]
    escrow_invoice: Optional[str]
    delivery_channel: str
    output_payload: Optional[str]
    output_url: Optional[str]
    created_at: datetime
    delivered_at: Optional[datetime]
    auto_release_at: Optional[datetime]
    completed_at: Optional[datetime]
    disputed_at: Optional[datetime]
    dispute_reason: Optional[str]
    accepted_at: Optional[datetime] = None
    accepted_by: Optional[str] = None


class JobDeliverRequest(SQLModel):
    output: str = Field(..., max_length=50_000)  # can be text, JSON string, markdown etc
    output_url: Optional[str] = None


class JobDisputeRequest(SQLModel):
    reason: str = Field(..., max_length=2000)
