"""
Tests for agent registration and listing.
"""
import pytest


@pytest.mark.asyncio
async def test_register_agent(client, human_token):
    """Agent registration returns API key."""
    resp = await client.post(
        "/agents",
        json={
            "name": "TestBot",
            "specialty": "Testing automated systems",
            "price_per_task_sats": 500,
        },
        headers={"Authorization": f"Bearer {human_token}"},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert "api_key" in data
    assert data["api_key"].startswith("ay_live_")
    assert data["agent"]["name"] == "TestBot"
    assert data["warning"]  # key shown once warning


@pytest.mark.asyncio
async def test_register_agent_requires_auth(client):
    """Cannot register agent without JWT."""
    resp = await client.post("/agents", json={"name": "Anon", "specialty": "Nothing"})
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_list_agents(client, test_agent):
    """List agents returns paginated results."""
    resp = await client.get("/agents")
    assert resp.status_code == 200
    data = resp.json()
    assert "agents" in data
    assert "total" in data
    assert len(data["agents"]) >= 1


@pytest.mark.asyncio
async def test_list_agents_filter_specialty(client, test_agent):
    """Filter agents by specialty substring."""
    resp = await client.get("/agents?specialty=Testing")
    assert resp.status_code == 200
    data = resp.json()
    assert any("Testing" in a["specialty"] for a in data["agents"])


@pytest.mark.asyncio
async def test_get_agent_profile(client, test_agent):
    """Get agent by ID."""
    agent_data, _ = test_agent
    resp = await client.get(f"/agents/{agent_data['id']}")
    assert resp.status_code == 200
    assert resp.json()["name"] == "TestAgent"


@pytest.mark.asyncio
async def test_get_agent_not_found(client):
    """404 for nonexistent agent."""
    resp = await client.get("/agents/00000000-0000-0000-0000-000000000000")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_update_agent(client, test_agent):
    """Agent can update own profile."""
    agent_data, api_key = test_agent
    resp = await client.put(
        f"/agents/{agent_data['id']}",
        json={"specialty": "Updated specialty for testing"},
        headers={"X-Agent-Key": api_key},
    )
    assert resp.status_code == 200
    assert resp.json()["specialty"] == "Updated specialty for testing"


@pytest.mark.asyncio
async def test_update_agent_wrong_key(client, test_agent, test_provider):
    """Agent cannot update another agent's profile."""
    agent_data, _ = test_agent
    _, provider_key = test_provider
    resp = await client.put(
        f"/agents/{agent_data['id']}",
        json={"specialty": "Hack attempt"},
        headers={"X-Agent-Key": provider_key},
    )
    assert resp.status_code == 403
