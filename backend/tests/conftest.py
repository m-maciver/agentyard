"""
AgentYard tests — shared fixtures
"""
import asyncio
import hashlib
import secrets
import sys
import os

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlmodel import SQLModel

# Ensure backend is on path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Force SQLite test DB
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///./test_agentyard.db")
os.environ.setdefault("JWT_SECRET", "test_jwt_secret")
os.environ.setdefault("ADMIN_API_KEY", "test_admin_key")
os.environ.setdefault("LNBITS_URL", "https://demo.lnbits.com")

from main import app
from api.database import get_session
from api.models import Agent, Human


TEST_DB_URL = "sqlite+aiosqlite:///./test_agentyard.db"

test_engine = create_async_engine(TEST_DB_URL, echo=False)
test_session_maker = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)


async def override_get_session():
    async with test_session_maker() as session:
        yield session


app.dependency_overrides[get_session] = override_get_session


@pytest_asyncio.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_db():
    """Create test database tables."""
    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
    # Clean up test db file
    if os.path.exists("./test_agentyard.db"):
        os.remove("./test_agentyard.db")


@pytest_asyncio.fixture
async def session():
    async with test_session_maker() as s:
        yield s


@pytest_asyncio.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c


@pytest_asyncio.fixture
async def human_token(client):
    """Register and login a human, return token."""
    resp = await client.post("/auth/register", json={"email": "test@example.com", "password": "testpass123"})
    if resp.status_code == 400:
        # Already registered
        pass
    resp = await client.post("/auth/login", json={"email": "test@example.com", "password": "testpass123"})
    assert resp.status_code == 200
    return resp.json()["access_token"]


@pytest_asyncio.fixture
async def test_agent(client, human_token, session):
    """Create a test agent, return (agent_data, api_key)."""
    resp = await client.post(
        "/agents",
        json={
            "name": "TestAgent",
            "specialty": "Testing",
            "soul_excerpt": "I test things",
            "price_per_task_sats": 1000,
            "webhook_url": "https://example.com/webhook",
            "lnbits_wallet_id": "test_wallet",
            "lnbits_invoice_key": "test_invoice_key",
        },
        headers={"Authorization": f"Bearer {human_token}"},
    )
    assert resp.status_code == 201
    data = resp.json()
    return data["agent"], data["api_key"]


@pytest_asyncio.fixture
async def test_provider(client, human_token):
    """Create a second agent as provider."""
    resp = await client.post(
        "/agents",
        json={
            "name": "ProviderAgent",
            "specialty": "Writing",
            "soul_excerpt": "I write things",
            "price_per_task_sats": 2000,
            "webhook_url": "https://example.com/provider-webhook",
            "lnbits_wallet_id": "provider_wallet",
            "lnbits_invoice_key": "provider_invoice_key",
        },
        headers={"Authorization": f"Bearer {human_token}"},
    )
    assert resp.status_code == 201
    data = resp.json()
    return data["agent"], data["api_key"]
