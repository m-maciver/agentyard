"""
AgentYard — Delivery engine
Sends job output to client agents via webhook.
"""
import hashlib
import hmac
import json
import logging
from datetime import datetime

import httpx

from config import settings

logger = logging.getLogger(__name__)


def sign_payload(payload: dict) -> str:
    """HMAC-SHA256 sign a payload. Client agents use this to verify the callback is from us."""
    body = json.dumps(payload, sort_keys=True, default=str)
    signature = hmac.new(
        settings.agentyard_webhook_secret.encode(),
        body.encode(),
        hashlib.sha256,
    ).hexdigest()
    return f"sha256={signature}"


async def deliver_via_webhook(job, provider_name: str = "") -> bool:
    """
    Deliver job output to client's webhook URL.
    Returns True if successful.
    """
    if not job.delivery_target:
        logger.warning(f"Job {job.id} has no delivery_target — skipping delivery")
        return False

    payload = {
        "job_id": str(job.id),
        "status": "delivered",
        "output": job.output_payload,
        "output_url": job.output_url,
        "provider_id": str(job.provider_agent_id),
        "provider_name": provider_name,
        "delivered_at": job.delivered_at.isoformat() if job.delivered_at else None,
        "auto_release_at": job.auto_release_at.isoformat() if job.auto_release_at else None,
        "dispute_window_seconds": 7200,
    }

    signature = sign_payload(payload)
    headers = {
        "Content-Type": "application/json",
        "X-AgentYard-Signature": signature,
        "X-AgentYard-Job-ID": str(job.id),
    }

    async with httpx.AsyncClient(timeout=30) as client:
        try:
            response = await client.post(
                job.delivery_target,
                json=payload,
                headers=headers,
            )
            response.raise_for_status()
            logger.info(f"Job {job.id} delivered to {job.delivery_target} — status {response.status_code}")
            return True
        except httpx.HTTPStatusError as e:
            logger.error(f"Delivery failed for job {job.id}: HTTP {e.response.status_code} from {job.delivery_target}")
            return False
        except httpx.RequestError as e:
            logger.error(f"Delivery error for job {job.id}: {e}")
            return False


async def notify_provider(job, provider) -> bool:
    """
    Notify provider agent about a new job via their webhook URL.
    """
    if not provider.webhook_url:
        logger.warning(f"Provider {provider.id} has no webhook_url — can't notify")
        return False

    payload = {
        "event": "job_assigned",
        "job_id": str(job.id),
        "title": job.title,
        "description": job.description,
        "price_sats": job.price_sats,
        "stake_sats": job.stake_sats,
        "client_agent_id": str(job.client_agent_id),
        "created_at": job.created_at.isoformat(),
    }

    signature = sign_payload(payload)
    headers = {
        "Content-Type": "application/json",
        "X-AgentYard-Signature": signature,
        "X-AgentYard-Event": "job_assigned",
    }

    async with httpx.AsyncClient(timeout=15) as client:
        try:
            response = await client.post(
                provider.webhook_url,
                json=payload,
                headers=headers,
            )
            response.raise_for_status()
            logger.info(f"Provider {provider.id} notified of job {job.id}")
            return True
        except Exception as e:
            logger.warning(f"Failed to notify provider {provider.id} of job {job.id}: {e}")
            return False  # Not fatal — provider can poll


async def notify_admin_dispute(job) -> None:
    """
    Notify admin of a new dispute via Discord webhook.
    """
    if not settings.admin_discord_webhook:
        return

    embed = {
        "title": f"⚠️ Dispute raised — Job {str(job.id)[:8]}",
        "description": job.dispute_reason or "No reason provided",
        "color": 0xFF4444,
        "fields": [
            {"name": "Job ID", "value": str(job.id), "inline": False},
            {"name": "Price", "value": f"{job.price_sats} sats", "inline": True},
            {"name": "Stake at risk", "value": f"{job.stake_sats} sats", "inline": True},
        ],
    }

    async with httpx.AsyncClient(timeout=10) as client:
        try:
            await client.post(
                settings.admin_discord_webhook,
                json={"embeds": [embed]},
            )
        except Exception as e:
            logger.warning(f"Failed to send admin dispute notification: {e}")
