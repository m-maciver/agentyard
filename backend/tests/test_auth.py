"""
Tests for authentication endpoints.
"""
import pytest


@pytest.mark.asyncio
async def test_register_human(client):
    """Human can register with email + password."""
    resp = await client.post(
        "/auth/register",
        json={"email": "newuser@example.com", "password": "securepassword"},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["email"] == "newuser@example.com"
    assert "password" not in data  # no password in response
    assert "id" in data


@pytest.mark.asyncio
async def test_register_duplicate_email(client):
    """Duplicate email returns 400."""
    await client.post(
        "/auth/register",
        json={"email": "duplicate@example.com", "password": "password"},
    )
    resp = await client.post(
        "/auth/register",
        json={"email": "duplicate@example.com", "password": "password2"},
    )
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_login(client):
    """Login returns JWT token."""
    email = "logintest@example.com"
    await client.post("/auth/register", json={"email": email, "password": "mypassword"})
    resp = await client.post("/auth/login", json={"email": email, "password": "mypassword"})
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_wrong_password(client):
    """Wrong password returns 401."""
    email = "wrongpass@example.com"
    await client.post("/auth/register", json={"email": email, "password": "correct"})
    resp = await client.post("/auth/login", json={"email": email, "password": "wrong"})
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_me_endpoint(client, human_token):
    """JWT auth returns current human."""
    resp = await client.get("/auth/me", headers={"Authorization": f"Bearer {human_token}"})
    assert resp.status_code == 200
    assert "email" in resp.json()


@pytest.mark.asyncio
async def test_me_requires_auth(client):
    """Cannot access /auth/me without token."""
    resp = await client.get("/auth/me")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_health_endpoint(client):
    """Health check returns 200."""
    resp = await client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"
