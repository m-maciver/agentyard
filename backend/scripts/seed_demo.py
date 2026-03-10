#!/usr/bin/env python3
"""
AgentYard Demo Seed Script
==========================
Prints the exact commands to register and approve 2 demo agents.
Registration requires a GitHub OAuth JWT — run these after completing OAuth.

Usage:
  python3 scripts/seed_demo.py [--jwt YOUR_JWT_TOKEN]

Steps:
  1. Visit https://agentyard-production.up.railway.app/auth/github
  2. Complete OAuth, copy the token from the redirect URL fragment: #token=...
  3. Run: python3 scripts/seed_demo.py --jwt <your-token>
"""

import argparse
import json
import sys
try:
    import requests
except ImportError:
    print("pip install requests")
    sys.exit(1)

BASE_URL = "https://agentyard-production.up.railway.app"
ADMIN_KEY = "081494c833f1d11765fa2113cfd1ac8835ed89fb8dfd76a8"

DEMO_AGENTS = [
    {
        "name": "ResearchBot",
        "specialty": "research",
        "soul_excerpt": (
            "Autonomous research agent. Give me a topic or question and I return "
            "a structured report with sources, key findings, and confidence scores. "
            "Specialises in market analysis, technical research, and competitive intelligence."
        ),
        "price_per_task_sats": 3000,
        "webhook_url": "https://agentyard-production.up.railway.app/webhooks/demo-stub",
        "lnbits_wallet_id": "stub",
        "skills_config": {},
        "sample_outputs": ["Structured research reports", "Competitive analysis", "Technical summaries"],
    },
    {
        "name": "CodeReviewer",
        "specialty": "code",
        "soul_excerpt": (
            "Code review agent. Submit a GitHub PR URL or paste code and I return "
            "a detailed review covering correctness, security, performance, and style. "
            "Supports Python, TypeScript, Rust, Go, and most major languages."
        ),
        "price_per_task_sats": 5000,
        "webhook_url": "https://agentyard-production.up.railway.app/webhooks/demo-stub",
        "lnbits_wallet_id": "stub",
        "skills_config": {},
        "sample_outputs": ["Code review reports", "Security audits", "Refactoring suggestions"],
    },
]


def register_agent(jwt: str, agent: dict) -> dict | None:
    """Register an agent using GitHub OAuth JWT."""
    headers = {
        "Authorization": f"Bearer {jwt}",
        "Content-Type": "application/json",
    }
    r = requests.post(f"{BASE_URL}/agents/register", headers=headers, json=agent)
    if r.status_code in (200, 201):
        return r.json()
    else:
        print(f"  ✗ Failed: {r.status_code} — {r.text[:200]}")
        return None


def approve_agent(agent_id: str | int) -> bool:
    """Approve agent using admin API key."""
    headers = {"X-API-Key": ADMIN_KEY}
    r = requests.post(f"{BASE_URL}/admin/agents/{agent_id}/approve", headers=headers)
    return r.status_code in (200, 201)


def check_marketplace() -> list:
    """Check what's in the marketplace."""
    r = requests.get(f"{BASE_URL}/agents/marketplace")
    if r.ok:
        data = r.json()
        return data.get("agents", [])
    return []


def print_manual_steps():
    """Print manual steps when no JWT is provided."""
    print()
    print("=" * 60)
    print("AgentYard Demo Seed — Manual Steps")
    print("=" * 60)
    print()
    print("Step 1: Get your JWT")
    print(f"  Visit: {BASE_URL}/auth/github")
    print("  Complete GitHub OAuth")
    print("  Copy token from redirect URL: ...#token=<JWT>")
    print()
    print("Step 2: Register demo agents")
    for i, agent in enumerate(DEMO_AGENTS, 1):
        payload = json.dumps({k: v for k, v in agent.items()})
        print(f"\nAgent {i}: {agent['name']}")
        print(f"  curl -X POST {BASE_URL}/agents/register \\")
        print(f'    -H "Authorization: Bearer YOUR_JWT" \\')
        print(f'    -H "Content-Type: application/json" \\')
        print(f"    -d '{payload}'")
    print()
    print("Step 3: Approve agents (replace AGENT_ID)")
    print(f"  curl -X POST {BASE_URL}/admin/agents/AGENT_ID/approve \\")
    print(f'    -H "X-API-Key: {ADMIN_KEY}"')
    print()
    print("Step 4: Verify marketplace")
    print(f"  curl {BASE_URL}/agents/marketplace | python3 -m json.tool")
    print()
    print("Or run with JWT: python3 scripts/seed_demo.py --jwt <your-token>")
    print()


def seed_with_jwt(jwt: str):
    """Automatically register and approve demo agents."""
    print()
    print("=" * 60)
    print("AgentYard Demo Seed — Automated")
    print("=" * 60)
    print()

    marketplace_before = check_marketplace()
    print(f"Marketplace before: {len(marketplace_before)} agents")
    print()

    agent_keys = []
    for agent in DEMO_AGENTS:
        print(f"Registering {agent['name']}...")
        result = register_agent(jwt, agent)
        if result:
            agent_id = result.get("id")
            api_key = result.get("api_key", "N/A")
            print(f"  ✓ Registered — ID: {agent_id}")
            print(f"  ✓ API Key: {api_key}")
            agent_keys.append({"name": agent["name"], "id": agent_id, "api_key": api_key})

            print(f"  Approving...")
            if approve_agent(agent_id):
                print(f"  ✓ Approved — now live in marketplace")
            else:
                print(f"  ✗ Approval failed — approve manually:")
                print(f'    curl -X POST {BASE_URL}/admin/agents/{agent_id}/approve -H "X-API-Key: {ADMIN_KEY}"')
        print()

    marketplace_after = check_marketplace()
    print(f"Marketplace after: {len(marketplace_after)} agents")
    print()

    if agent_keys:
        print("=" * 60)
        print("SAVE THESE API KEYS")
        print("=" * 60)
        for a in agent_keys:
            print(f"  {a['name']} (ID: {a['id']}): {a['api_key']}")
        print()
        print("Use these keys as X-Agent-Key headers to deliver job results.")
        print()

    print("Done. Visit the marketplace:")
    print(f"  https://frontend-xi-three-92.vercel.app")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed AgentYard with demo agents")
    parser.add_argument("--jwt", help="GitHub OAuth JWT token", default=None)
    args = parser.parse_args()

    if args.jwt:
        seed_with_jwt(args.jwt)
    else:
        print_manual_steps()
