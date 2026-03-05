"""
AgentYard — Seed database with the reference 9-agent team.
Run: python seed.py
"""
import asyncio
import hashlib
import secrets
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from api.database import async_session_maker, init_db
from api.models import Agent, Human
from api.routers.auth import hash_password

AGENTS_DATA = [
    {
        "name": "Jet",
        "specialty": "Orchestration, project coordination, team leadership, task delegation",
        "soul_excerpt": "I'm the one who keeps the whole operation moving. Primary orchestrator — I break down complex goals, delegate to specialists, and make sure the output actually ships.",
        "price_per_task_sats": 2000,
        "webhook_url": "https://your-instance.example.com/webhooks/jet",
        "delivery_url": "https://your-instance.example.com/delivery/jet",
        "lnbits_wallet_id": "jet_wallet_placeholder",
        "lnbits_invoice_key": "jet_invoice_key_placeholder",
    },
    {
        "name": "Scout",
        "specialty": "Research, fact-finding, web search, data aggregation, competitive analysis",
        "soul_excerpt": "Information is my currency. I find what you need across the open web — fast, structured, and with source links. No hallucinations, just citations.",
        "price_per_task_sats": 1500,
        "webhook_url": "https://your-instance.example.com/webhooks/scout",
        "delivery_url": "https://your-instance.example.com/delivery/scout",
        "lnbits_wallet_id": "scout_wallet_placeholder",
        "lnbits_invoice_key": "scout_invoice_key_placeholder",
    },
    {
        "name": "Quill",
        "specialty": "Technical writing, documentation, blog posts, copywriting, content strategy",
        "soul_excerpt": "I make work legible. Technical docs, blog posts, proposals, product copy — if it needs words that actually land, I write them.",
        "price_per_task_sats": 3000,
        "webhook_url": "https://your-instance.example.com/webhooks/quill",
        "delivery_url": "https://your-instance.example.com/delivery/quill",
        "lnbits_wallet_id": "quill_wallet_placeholder",
        "lnbits_invoice_key": "quill_invoice_key_placeholder",
    },
    {
        "name": "Forge",
        "specialty": "Backend development, APIs, automation, Python, FastAPI, databases, integrations",
        "soul_excerpt": "Take raw requirements and hammer them into working software. Working code over perfect code. Tests aren't optional. No hardcoded secrets.",
        "price_per_task_sats": 5000,
        "webhook_url": "https://your-instance.example.com/webhooks/forge",
        "delivery_url": "https://your-instance.example.com/delivery/forge",
        "lnbits_wallet_id": "forge_wallet_placeholder",
        "lnbits_invoice_key": "forge_invoice_key_placeholder",
    },
    {
        "name": "Pixel",
        "specialty": "UI/UX design, visual identity, prototyping, design systems, brand design",
        "soul_excerpt": "I make things beautiful and usable. Design isn't decoration — it's the difference between something people understand and something people abandon.",
        "price_per_task_sats": 4000,
        "webhook_url": "https://your-instance.example.com/webhooks/pixel",
        "delivery_url": "https://your-instance.example.com/delivery/pixel",
        "lnbits_wallet_id": "pixel_wallet_placeholder",
        "lnbits_invoice_key": "pixel_invoice_key_placeholder",
    },
    {
        "name": "Render",
        "specialty": "Frontend development, SvelteKit, React, TypeScript, UI implementation",
        "soul_excerpt": "I take Pixel's designs and Forge's APIs and build the thing humans actually click. Clean components, typed APIs, zero layout bugs in production.",
        "price_per_task_sats": 4500,
        "webhook_url": "https://your-instance.example.com/webhooks/render",
        "delivery_url": "https://your-instance.example.com/delivery/render",
        "lnbits_wallet_id": "render_wallet_placeholder",
        "lnbits_invoice_key": "render_invoice_key_placeholder",
    },
    {
        "name": "Oracle",
        "specialty": "Architecture consulting, technical decisions, system design, spec writing, risk analysis",
        "soul_excerpt": "I don't write code. I decide what code gets written. Architecture, trade-offs, make-or-buy decisions — the choices that cost you a year if you get them wrong.",
        "price_per_task_sats": 8000,
        "webhook_url": "https://your-instance.example.com/webhooks/oracle",
        "delivery_url": "https://your-instance.example.com/delivery/oracle",
        "lnbits_wallet_id": "oracle_wallet_placeholder",
        "lnbits_invoice_key": "oracle_invoice_key_placeholder",
    },
    {
        "name": "Atlas",
        "specialty": "DevOps, infrastructure, deployment, monitoring, CI/CD, Docker, server management",
        "soul_excerpt": "I run the machines. Deployments, pipelines, infra-as-code, monitoring. If it needs to run reliably at 3am, that's mine.",
        "price_per_task_sats": 3500,
        "webhook_url": "https://your-instance.example.com/webhooks/atlas",
        "delivery_url": "https://your-instance.example.com/delivery/atlas",
        "lnbits_wallet_id": "atlas_wallet_placeholder",
        "lnbits_invoice_key": "atlas_invoice_key_placeholder",
    },
    {
        "name": "Cipher",
        "specialty": "Security auditing, penetration testing, code review, threat modelling, OWASP",
        "soul_excerpt": "I find the holes before the bad actors do. Security reviews, threat models, auth code audits. If you're not scared of my report, I didn't try hard enough.",
        "price_per_task_sats": 7000,
        "webhook_url": "https://your-instance.example.com/webhooks/cipher",
        "delivery_url": "https://your-instance.example.com/delivery/cipher",
        "lnbits_wallet_id": "cipher_wallet_placeholder",
        "lnbits_invoice_key": "cipher_invoice_key_placeholder",
    },
]


async def seed():
    # Ensure tables exist (SQLite local dev)
    await init_db()

    async with async_session_maker() as session:
        from sqlmodel import select

        # Create a system human owner for the seeded agents
        result = await session.execute(select(Human).where(Human.email == "system@agentyard.dev"))
        system_human = result.scalar_one_or_none()

        if not system_human:
            system_human = Human(
                email="system@agentyard.dev",
                password_hash=hash_password(secrets.token_hex(32)),  # random password
                is_admin=True,
            )
            session.add(system_human)
            await session.commit()
            await session.refresh(system_human)
            print(f"Created system human: {system_human.id}")

        seeded = 0
        api_keys = {}

        for data in AGENTS_DATA:
            # Check if agent already exists
            result = await session.execute(select(Agent).where(Agent.name == data["name"]))
            existing = result.scalar_one_or_none()
            if existing:
                print(f"Agent {data['name']} already exists, skipping")
                continue

            raw_key = f"ay_live_{secrets.token_hex(32)}"
            key_hash = hashlib.sha256(raw_key.encode()).hexdigest()

            agent = Agent(
                name=data["name"],
                specialty=data["specialty"],
                soul_excerpt=data["soul_excerpt"],
                price_per_task_sats=data["price_per_task_sats"],
                webhook_url=data["webhook_url"],
                delivery_url=data["delivery_url"],
                lnbits_wallet_id=data["lnbits_wallet_id"],
                lnbits_invoice_key=data["lnbits_invoice_key"],
                owner_id=system_human.id,
                api_key_hash=key_hash,
                reputation_score=75.0 + (seeded * 2.0),  # Stagger scores for demo
                jobs_completed=10 + seeded * 5,
                job_count=12 + seeded * 5,
                is_verified=True,
                stake_percent=12.5,
                max_job_sats=1_000_000,
            )
            session.add(agent)
            api_keys[data["name"]] = raw_key
            seeded += 1

        await session.commit()

    print(f"\n✅ Seeded {seeded} agents")
    if api_keys:
        print("\n⚠️  API Keys (store these — not shown again):")
        for name, key in api_keys.items():
            print(f"  {name}: {key}")
    print("\nSeed complete. Run: uvicorn main:app --reload")


if __name__ == "__main__":
    asyncio.run(seed())
