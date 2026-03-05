"""
AgentYard — Stake model
"""
from datetime import datetime, timezone
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


class StakeStatus(str, Enum):
    HELD = "held"
    RETURNED = "returned"
    SLASHED = "slashed"


class Stake(SQLModel, table=True):
    __tablename__ = "stakes"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    agent_id: UUID = Field(foreign_key="agents.id")
    job_id: UUID = Field(foreign_key="jobs.id")
    amount_sats: int
    status: StakeStatus = Field(default=StakeStatus.HELD)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    resolved_at: Optional[datetime] = Field(default=None)
