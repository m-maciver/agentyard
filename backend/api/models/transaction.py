"""
AgentYard — Transaction model (financial ledger)
"""
from datetime import datetime, timezone
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


class TransactionType(str, Enum):
    ESCROW_IN = "escrow_in"
    STAKE_HOLD = "stake_hold"
    FEE_COLLECT = "fee_collect"
    PROVIDER_RELEASE = "provider_release"
    STAKE_RETURN = "stake_return"
    STAKE_SLASH = "stake_slash"
    CLIENT_REFUND = "client_refund"
    STAKE_TOPUP = "stake_topup"


class Transaction(SQLModel, table=True):
    __tablename__ = "transactions"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    job_id: Optional[UUID] = Field(default=None, foreign_key="jobs.id")
    type: TransactionType
    amount_sats: int
    payment_hash: Optional[str] = Field(default=None)
    from_wallet: Optional[str] = Field(default=None)
    to_wallet: Optional[str] = Field(default=None)
    note: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
