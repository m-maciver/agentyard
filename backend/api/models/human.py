"""
AgentYard — Human model (agent owners / dashboard users)
"""
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


class HumanBase(SQLModel):
    email: str = Field(unique=True, max_length=255)


class Human(HumanBase, table=True):
    __tablename__ = "humans"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    password_hash: str
    api_key: str = Field(default="")  # optional human API key for programmatic access
    is_admin: bool = Field(default=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class HumanCreate(SQLModel):
    email: str
    password: str


class HumanPublic(SQLModel):
    id: UUID
    email: str
    is_admin: bool
    created_at: datetime
