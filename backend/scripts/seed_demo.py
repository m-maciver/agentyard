#!/usr/bin/env python3
"""
AgentYard — Demo Seed Script
============================
Creates two demo agents (AgentForge + AgentScout), approves both via the admin
API key, and creates a sample job from buyer (AgentScout) to seller (AgentForge).

Usage:
    python scripts/seed_demo.py [--api-url URL]

Defaults to the live Railway backend if --api-url is not supplied.

⚠️  NOTE on registration:
    Agent registration via /agents/register requires a GitHub OAuth JWT.
    This script cannot perform that step automatically (no browser flow here).
    Instead it checks /admin/agents/pending for any already-registered pending
    agents and approves them, OR it registers via the legacy /agents endpoint
    (which requires a Human JWT).

    To fully seed from scratch:
      1. Log in via the frontend (GitHub OAuth) and register AgentForge + AgentScout
         using the AgentYard skill wizard, OR call POST /agents with a Human JWT.
      2. Re-run this script — it will auto-approve and create the sample job.

    Alternatively, if the backend exposes an admin-only registration path in the
    future, update this script to use it.

    TODO: Add admin-only registration endpoint to bypass OAuth for seeding.
"""

import argparse
import json
import sys
import httpx

# ── Config ─────────────────────────────────────────────────────────────────────

DEFAULT_API_URL = "https://agentyard-production.up.railway.app"
ADMIN_API_KEY = "081494c833f1d11765fa2113cfd1ac8835ed89fb8dfd76a8"

AGENTS_TO_SEED = [
    {
        "agent_name": "AgentForge",
        "role": "SELLER",
        "capabilities": "code generation, backend development, API design",
        "price_sats": 5000,
        "public_key": "demo-ed25519-pubkey-agentforge-0000000000000000000000000000000001",
        "openclaw_user_id": "demo-forge-user-001",
    },
    {
        "agent_name": "AgentScout",
        "role": "BUYER_ONLY",
        "capabilities": "research, web search, data extraction",
        "price_sats": 0,
        "public_key": "demo-ed25519-pubkey-agentscout-0000000000000000000000000000000002",
        "openclaw_user_id": "demo-scout-user-002",
    },
]


# ── Helpers ────────────────────────────────────────────────────────────────────

def admin_headers() -> dict:
    return {
        "Content-Type": "application/json",
        "X-API-Key": ADMIN_API_KEY,
    }


def ok(label: str, data: dict) -> None:
    print(f"  ✅ {label}")
    print(f"     {json.dumps(data, indent=6)}")


def warn(label: str, detail: str) -> None:
    print(f"  ⚠️  {label}: {detail}")


def fail(label: str, detail: str) -> None:
    print(f"  ❌ {label}: {detail}")


# ── Steps ──────────────────────────────────────────────────────────────────────

def fetch_pending_agents(client: httpx.Client, api_url: str) -> list[dict]:
    """Fetch the admin pending-agents list."""
    r = client.get(f"{api_url}/admin/agents/pending", headers=admin_headers())
    if r.status_code == 200:
        return r.json().get("agents", [])
    warn("fetch_pending_agents", f"HTTP {r.status_code} — {r.text[:200]}")
    return []


def approve_agent(client: httpx.Client, api_url: str, agent_id: int, agent_name: str) -> bool:
    """Approve an agent listing using the admin API key."""
    r = client.post(
        f"{api_url}/admin/agents/{agent_id}/approve",
        headers=admin_headers(),
    )
    if r.status_code == 200:
        ok(f"Approved '{agent_name}' (id={agent_id})", r.json())
        return True
    fail(f"approve '{agent_name}'", f"HTTP {r.status_code} — {r.text[:200]}")
    return False


def create_sample_job(
    client: httpx.Client,
    api_url: str,
    buyer_api_key: str,
    seller_agent_id: int,
) -> dict | None:
    """Create a sample job from AgentScout → AgentForge."""
    payload = {
        "provider_agent_id": seller_agent_id,
        "task_description": "Generate a FastAPI route that returns the current Bitcoin price in sats via CoinGecko API. Include docstring and error handling.",
        "task_input": {"language": "python", "framework": "fastapi"},
        "delivery_channel": "webhook",
        "delivery_target": f"{api_url}/webhooks/delivery",
    }
    r = client.post(
        f"{api_url}/jobs",
        json=payload,
        headers={
            "Content-Type": "application/json",
            "X-Agent-Key": buyer_api_key,
        },
    )
    if r.status_code in (200, 201):
        return r.json()
    warn("create_sample_job", f"HTTP {r.status_code} — {r.text[:300]}")
    return None


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="AgentYard demo seed script")
    parser.add_argument("--api-url", default=DEFAULT_API_URL, help="Base URL of the AgentYard backend")
    args = parser.parse_args()
    api_url = args.api_url.rstrip("/")

    print(f"\n🌱 AgentYard Demo Seed")
    print(f"   API: {api_url}")
    print(f"   Admin key: {ADMIN_API_KEY[:12]}…\n")

    summary = {
        "api_url": api_url,
        "agents_approved": [],
        "sample_job": None,
        "todos": [],
    }

    with httpx.Client(timeout=20) as client:

        # ── Step 1: Check pending agents ─────────────────────────────────────
        print("Step 1 — Fetching pending agents from marketplace review queue…")
        pending = fetch_pending_agents(client, api_url)

        target_names = {a["agent_name"] for a in AGENTS_TO_SEED}
        pending_targets = [p for p in pending if p["agent_name"] in target_names]

        if not pending_targets:
            print("  ℹ️  No pending agents found for AgentForge / AgentScout.")
            print("     They may not be registered yet, or are already approved.")
            print()
            summary["todos"].append(
                "Register AgentForge and AgentScout via GitHub OAuth login + AgentYard skill wizard,"
                " then re-run this script to auto-approve them."
            )

        # ── Step 2: Approve pending targets ──────────────────────────────────
        print("Step 2 — Approving pending demo agents…")
        forge_id = None
        scout_id = None
        forge_approved = False
        scout_approved = False

        for agent in pending_targets:
            aid = agent["id"]
            name = agent["agent_name"]
            approved = approve_agent(client, api_url, aid, name)
            if approved:
                summary["agents_approved"].append({"id": aid, "name": name, "role": agent.get("role")})
                if name == "AgentForge":
                    forge_id = aid
                    forge_approved = True
                elif name == "AgentScout":
                    scout_id = aid
                    scout_approved = True

        if not pending_targets:
            print("  (skipped — no pending agents to approve)\n")
        else:
            print()

        # ── Step 3: Check marketplace for existing approved agents ────────────
        print("Step 3 — Checking marketplace for approved AgentForge / AgentScout…")
        r = client.get(f"{api_url}/agents/marketplace", headers={"Content-Type": "application/json"})
        if r.status_code == 200:
            marketplace_agents = r.json().get("agents", [])
            for a in marketplace_agents:
                if a.get("agent_name") == "AgentForge" and not forge_id:
                    forge_id = a["id"]
                    print(f"  ✅ AgentForge already approved on marketplace (id={forge_id})")
                elif a.get("agent_name") == "AgentScout" and not scout_id:
                    scout_id = a["id"]
                    print(f"  ✅ AgentScout already approved on marketplace (id={scout_id})")
        else:
            warn("marketplace fetch", f"HTTP {r.status_code}")
        print()

        # ── Step 4: Create sample job (needs buyer agent key) ─────────────────
        print("Step 4 — Creating sample job (AgentScout → AgentForge)…")

        if not forge_id:
            warn(
                "create_job",
                "AgentForge not found on marketplace — skipping job creation. "
                "Register and approve both agents first.",
            )
            summary["todos"].append(
                "Re-run seed_demo.py after both agents are registered and approved "
                "to create the sample job."
            )
        else:
            # We need AgentScout's API key to POST /jobs.
            # For demo purposes, if the scout agent isn't registered, instruct the user.
            scout_api_key = None

            # Try to find scout API key from env or a local config file
            import os
            scout_api_key = os.environ.get("AGENTSCOUT_API_KEY")

            if not scout_api_key:
                warn(
                    "create_job",
                    "AGENTSCOUT_API_KEY env var not set. "
                    "Export the API key returned when AgentScout was registered, then re-run.",
                )
                summary["todos"].append(
                    "Set AGENTSCOUT_API_KEY=<key from registration> and re-run seed_demo.py "
                    "to create the sample job."
                )
            else:
                job = create_sample_job(client, api_url, scout_api_key, forge_id)
                if job:
                    ok("Sample job created", job)
                    summary["sample_job"] = job
                else:
                    summary["todos"].append(
                        "Sample job creation failed — check that AgentScout's API key is correct "
                        "and AgentForge is a registered Agent (not just AgentProfile) with a valid provider_agent_id UUID."
                    )

    # ── Summary ────────────────────────────────────────────────────────────────
    print("\n" + "─" * 60)
    print("📋 SEED SUMMARY")
    print("─" * 60)
    print(f"  API URL     : {api_url}")
    print(f"  Admin key   : {ADMIN_API_KEY}")

    if summary["agents_approved"]:
        print(f"\n  Agents approved ({len(summary['agents_approved'])}):")
        for a in summary["agents_approved"]:
            print(f"    • {a['name']} (id={a['id']}, role={a.get('role', '?')})")
    else:
        print("\n  Agents approved : none (pending registration or already approved)")

    if summary["sample_job"]:
        job = summary["sample_job"]
        print(f"\n  Sample job:")
        print(f"    job_id  = {job.get('job_id', '?')}")
        print(f"    invoice = {job.get('invoice', 'n/a')[:60]}…")
        print(f"    status  = {job.get('status', '?')}")
    else:
        print("\n  Sample job      : not created")

    if summary["todos"]:
        print(f"\n  📌 TODOs ({len(summary['todos'])}):")
        for i, todo in enumerate(summary["todos"], 1):
            print(f"    {i}. {todo}")

    print("\n  ℹ️  Registration note:")
    print("     Agent registration (/agents/register) requires GitHub OAuth JWT.")
    print("     To register demo agents:")
    print("       1. Log in at the AgentYard frontend with GitHub")
    print("       2. Run: openclaw skill install agentyard")
    print("       3. Re-run this script to approve + seed the job")
    print()


if __name__ == "__main__":
    main()
