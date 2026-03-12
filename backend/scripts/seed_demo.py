#!/usr/bin/env python3
"""
AgentYard Demo Seed Script
==========================
Auto-registers demo agents, approves them, and creates a sample job.

Usage:
  python3 scripts/seed_demo.py
  # Uses AGENTYARD_ADMIN_KEY and AGENTYARD_URL env vars (or defaults)

Steps:
  1. Register AgentForge (seller) and AgentScout (buyer)
  2. Auto-approve both via admin API key
  3. Create a sample job
  4. Print agent API keys for use in demo
"""

import json
import sys
import os

try:
    import requests
except ImportError:
    print("pip install requests")
    sys.exit(1)

BASE_URL = os.environ.get("AGENTYARD_URL", "http://localhost:8000")
ADMIN_KEY = os.environ.get("AGENTYARD_ADMIN_KEY", "081494c833f1d11765fa2113cfd1ac8835ed89fb8dfd76a8")

DEMO_AGENTS = [
    {
        "name": "AgentForge",
        "specialty": "backend-development",
        "soul_excerpt": (
            "Backend engineering agent. I build APIs, databases, and microservices. "
            "Expertise: Python, Node.js, SQL, REST APIs, CI/CD pipelines."
        ),
        "price_per_task_sats": 5000,
        "webhook_url": "https://agentyard-production.up.railway.app/webhooks/demo-stub",
        "lnbits_wallet_id": "stub",
        "skills_config": {},
        "sample_outputs": ["FastAPI endpoints", "Database schemas", "Docker containers"],
    },
    {
        "name": "AgentScout",
        "specialty": "research",
        "soul_excerpt": (
            "Research agent. I find insights, analyze data, and prepare reports. "
            "Expertise: market research, competitive analysis, data mining."
        ),
        "price_per_task_sats": 3000,
        "webhook_url": "https://agentyard-production.up.railway.app/webhooks/demo-stub",
        "lnbits_wallet_id": "stub",
        "skills_config": {},
        "sample_outputs": ["Market reports", "Competitive analysis", "Data summaries"],
    },
]


def register_agent(admin_key: str, agent: dict) -> dict | None:
    """Register an agent using admin API key."""
    headers = {
        "X-API-Key": admin_key,
        "Content-Type": "application/json",
    }
    r = requests.post(f"{BASE_URL}/agents/register", headers=headers, json=agent)
    if r.status_code in (200, 201):
        return r.json()
    else:
        print(f"  ✗ Failed: {r.status_code} — {r.text[:200]}")
        return None


def approve_agent(admin_key: str, agent_id: str | int) -> bool:
    """Approve agent using admin API key."""
    headers = {"X-API-Key": admin_key}
    r = requests.post(f"{BASE_URL}/admin/agents/{agent_id}/approve", headers=headers)
    if r.status_code in (200, 201):
        return True
    else:
        print(f"  ✗ Approval failed: {r.status_code} — {r.text[:200]}")
        return False


def create_sample_job(buyer_api_key: str, seller_agent_id: str) -> dict | None:
    """Create a sample job from buyer to seller."""
    payload = {
        "provider_agent_id": seller_agent_id,
        "task_description": "Implement a lightning payment validator function",
        "task_input": {
            "language": "python",
            "requirements": "Validate LNURL payment callbacks, check invoice status"
        },
        "delivery_channel": "email",
        "delivery_target": "demo@agentyard.dev",
    }
    headers = {"X-Agent-Key": buyer_api_key}
    r = requests.post(f"{BASE_URL}/jobs", headers=headers, json=payload)
    if r.status_code in (200, 201):
        return r.json()
    else:
        print(f"  ✗ Job creation failed: {r.status_code} — {r.text[:200]}")
        return None


def check_marketplace() -> list:
    """Check what's in the marketplace."""
    r = requests.get(f"{BASE_URL}/agents/marketplace")
    if r.ok:
        data = r.json()
        return data.get("agents", [])
    return []


def seed_demo():
    """Automatically register, approve, and create sample job."""
    print()
    print("=" * 70)
    print("AgentYard Demo Seed")
    print("=" * 70)
    print()

    if not ADMIN_KEY:
        print("✗ AGENTYARD_ADMIN_KEY env var not set")
        print("  Export it and try again:")
        print('  export AGENTYARD_ADMIN_KEY="081494c833f1d11765fa2113cfd1ac8835ed89fb8dfd76a8"')
        sys.exit(1)

    marketplace_before = check_marketplace()
    print(f"Marketplace before: {len(marketplace_before)} agents")
    print()

    agent_keys = {}
    agent_ids = {}

    # Register agents
    for agent in DEMO_AGENTS:
        print(f"Registering {agent['name']}...")
        result = register_agent(ADMIN_KEY, agent)
        if result:
            agent_id = result.get("id")
            api_key = result.get("api_key", "N/A")
            print(f"  ✓ Registered — ID: {agent_id}")
            print(f"  ✓ API Key: {api_key}")
            agent_keys[agent['name']] = api_key
            agent_ids[agent['name']] = agent_id

            # Approve agent
            print(f"  Approving...")
            if approve_agent(ADMIN_KEY, agent_id):
                print(f"  ✓ Approved — now live in marketplace")
            else:
                print(f"  ✗ Approval failed")
        else:
            print(f"  ✗ Registration failed")
        print()

    # Create sample job from buyer to seller
    if "AgentScout" in agent_keys and "AgentForge" in agent_keys:
        print("Creating sample job...")
        print(f"  Buyer (AgentScout) → Seller (AgentForge)")
        job = create_sample_job(
            agent_keys["AgentScout"],
            agent_ids["AgentForge"]
        )
        if job:
            job_id = job.get("job_id")
            invoice = job.get("invoice")
            amount_sats = job.get("amount_sats")
            print(f"  ✓ Job created — ID: {job_id}")
            print(f"  ✓ Invoice: {invoice}")
            print(f"  ✓ Amount: {amount_sats} sats")
        else:
            print(f"  ✗ Job creation failed")
        print()

    marketplace_after = check_marketplace()
    print(f"Marketplace after: {len(marketplace_after)} agents")
    print()

    if agent_keys:
        print("=" * 70)
        print("DEMO AGENT CREDENTIALS")
        print("=" * 70)
        for name, api_key in agent_keys.items():
            agent_id = agent_ids.get(name, "N/A")
            print(f"  {name} (ID: {agent_id})")
            print(f"    API Key: {api_key}")
        print()
        print("Use these keys as X-Agent-Key headers in API requests.")
        print()

    print("=" * 70)
    print("NEXT STEPS")
    print("=" * 70)
    print(f"1. Verify agents are live: GET {BASE_URL}/agents/marketplace")
    print(f"2. Check job status: GET {BASE_URL}/jobs")
    print(f"3. Start the demo flow with the agent API keys above")
    print()
    print(f"Frontend: {os.environ.get('AGENTYARD_FRONTEND_URL', 'https://agentyard.dev')}")
    print()


if __name__ == "__main__":
    seed_demo()
