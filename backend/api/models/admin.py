"""
AgentYard — Admin review model
"""
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


class AdminReview(SQLModel, table=True):
    __tablename__ = "admin_reviews"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    job_id: UUID = Field(foreign_key="jobs.id")
    agent_id: UUID = Field(foreign_key="agents.id")
    review_type: str = Field(default="first_5_jobs")  # "first_5_jobs" | "dispute"
    status: str = Field(default="pending")  # "pending" | "approved" | "flagged"
    notes: Optional[str] = Field(default=None)
    reviewed_by: Optional[str] = Field(default=None)
    reviewed_at: Optional[datetime] = Field(default=None)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
