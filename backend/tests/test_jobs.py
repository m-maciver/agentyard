"""
Tests for job lifecycle: create → pay → deliver → complete.
Uses mock LNBits (LNBits not required for tests).
"""
import pytest
from unittest.mock import AsyncMock, patch


@pytest.mark.asyncio
async def test_create_job(client, test_agent, test_provider):
    """Create a job returns invoice details."""
    client_data, client_key = test_agent
    provider_data, _ = test_provider

    # Patch LNBits to avoid needing a real server
    with patch("api.services.lnbits.create_invoice", new_callable=AsyncMock) as mock_invoice:
        mock_invoice.return_value = {
            "payment_hash": "testhash123",
            "payment_request": "lnbctestinvoice",
        }

        resp = await client.post(
            "/jobs",
            json={
                "provider_agent_id": provider_data["id"],
                "description": "Write a test blog post",
                "delivery_channel": "webhook",
                "delivery_target": "https://example.com/callback",
            },
            headers={"X-Agent-Key": client_key},
        )

    assert resp.status_code == 201
    data = resp.json()
    assert "job_id" in data
    assert "amount_sats" in data
    assert data["breakdown"]["task_price_sats"] == provider_data["price_per_task_sats"]


@pytest.mark.asyncio
async def test_create_job_requires_auth(client, test_provider):
    """Cannot create job without agent key."""
    provider_data, _ = test_provider
    resp = await client.post(
        "/jobs",
        json={"provider_agent_id": provider_data["id"], "description": "test"},
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_cannot_hire_yourself(client, test_agent):
    """Agent cannot hire itself."""
    agent_data, api_key = test_agent
    resp = await client.post(
        "/jobs",
        json={
            "provider_agent_id": agent_data["id"],
            "description": "Self-hire attempt",
        },
        headers={"X-Agent-Key": api_key},
    )
    assert resp.status_code == 400
    assert "yourself" in resp.json()["detail"].lower()


@pytest.mark.asyncio
async def test_deliver_job(client, test_agent, test_provider, session):
    """Provider can deliver a job in IN_PROGRESS status."""
    from api.models import Job, JobStatus
    from uuid import uuid4, UUID

    client_data, client_key = test_agent
    provider_data, provider_key = test_provider

    # Create job directly in DB in IN_PROGRESS state
    job = Job(
        client_agent_id=UUID(client_data["id"]),
        provider_agent_id=UUID(provider_data["id"]),
        description="Test job for delivery",
        price_sats=2000,
        platform_fee_sats=240,
        stake_sats=600,
        status=JobStatus.IN_PROGRESS,
        delivery_channel="webhook",
        delivery_target="https://example.com/cb",
    )
    session.add(job)
    await session.commit()
    await session.refresh(job)

    with patch("api.routers.jobs.deliver_via_webhook", new_callable=AsyncMock) as mock_deliver:
        mock_deliver.return_value = True
        resp = await client.post(
            f"/jobs/{job.id}/deliver",
            json={"output": "Here is the delivered content."},
            headers={"X-Agent-Key": provider_key},
        )

    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "delivered"
    assert data["auto_release_at"] is not None


@pytest.mark.asyncio
async def test_dispute_job(client, test_agent, test_provider, session):
    """Client can dispute a delivered job."""
    from api.models import Job, JobStatus
    from datetime import datetime, timezone, timedelta
    from uuid import UUID

    client_data, client_key = test_agent
    provider_data, _ = test_provider

    # Create job in DELIVERED state
    job = Job(
        client_agent_id=UUID(client_data["id"]),
        provider_agent_id=UUID(provider_data["id"]),
        description="Test job for dispute",
        price_sats=2000,
        platform_fee_sats=240,
        stake_sats=600,
        status=JobStatus.DELIVERED,
        delivered_at=datetime.now(timezone.utc),
        auto_release_at=datetime.now(timezone.utc) + timedelta(hours=2),
    )
    session.add(job)
    await session.commit()
    await session.refresh(job)

    resp = await client.post(
        f"/jobs/{job.id}/dispute",
        json={"reason": "Output was off-topic and did not meet the brief."},
        headers={"X-Agent-Key": client_key},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "disputed"
    assert data["dispute_reason"]


@pytest.mark.asyncio
async def test_list_jobs(client, test_agent):
    """Agent can list their jobs."""
    _, api_key = test_agent
    resp = await client.get("/jobs", headers={"X-Agent-Key": api_key})
    assert resp.status_code == 200
    assert "jobs" in resp.json()


@pytest.mark.asyncio
async def test_provider_cannot_dispute(client, test_agent, test_provider, session):
    """Provider cannot raise a dispute on their own job."""
    from api.models import Job, JobStatus
    from datetime import datetime, timezone, timedelta
    from uuid import UUID

    client_data, _ = test_agent
    provider_data, provider_key = test_provider

    job = Job(
        client_agent_id=UUID(client_data["id"]),
        provider_agent_id=UUID(provider_data["id"]),
        description="Another test job",
        price_sats=2000,
        platform_fee_sats=240,
        stake_sats=600,
        status=JobStatus.DELIVERED,
        delivered_at=datetime.now(timezone.utc),
        auto_release_at=datetime.now(timezone.utc) + timedelta(hours=2),
    )
    session.add(job)
    await session.commit()
    await session.refresh(job)

    resp = await client.post(
        f"/jobs/{job.id}/dispute",
        json={"reason": "I want a refund"},
        headers={"X-Agent-Key": provider_key},
    )
    assert resp.status_code == 403
