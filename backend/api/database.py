"""
AgentYard — Database engine and session management
Supports SQLite (local dev) and PostgreSQL (production) via DATABASE_URL env var.
"""
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlmodel import SQLModel

from config import settings

# Create async engine
# SQLite: sqlite+aiosqlite:///./agentyard.db
# PostgreSQL: postgresql+asyncpg://user:pass@localhost/agentyard
engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    connect_args={"check_same_thread": False} if settings.is_sqlite else {},
)

async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def init_db():
    """Create all tables. Used for local dev (SQLite). Production uses Alembic migrations."""
    async with engine.begin() as conn:
        # Import all models to register them with SQLModel metadata
        from api.models import (  # noqa: F401
            Agent, Human, Job, Transaction, Stake, AdminReview
        )
        await conn.run_sync(SQLModel.metadata.create_all)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency — yields a database session."""
    async with async_session_maker() as session:
        yield session
