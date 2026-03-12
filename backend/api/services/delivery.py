"""
AgentYard — Delivery engine
Sends job output to client agents via webhook or email (Resend).
"""
import hashlib
import hmac
import json
import logging
from datetime import datetime

import httpx

from config import settings
from api.services.output_scanner import scan_output

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


async def deliver_via_email(job, provider_name: str = "", delivery_email: str = "") -> bool:
    """
    Deliver job output to client's email via Resend API.
    Scans output for integrity before sending.
    Returns True if successful.
    """
    email = delivery_email or getattr(job, "delivery_target", "")
    if not email or "@" not in email:
        logger.warning(f"Job {job.id} has no valid delivery email — skipping email delivery")
        return False

    if not settings.resend_api_key:
        logger.warning("Resend API key not configured — skipping email delivery")
        return False

    # Scan output for integrity issues
    output_content = job.output_payload or ""
    scan = scan_output(output_content, content_type="text")

    if not scan.passed:
        logger.warning(f"Job {job.id} output failed integrity scan: {scan.reason}")
        # Still deliver but include warning
        scan_warning = f"<p style='color:#e53e3e;font-weight:bold;'>Integrity warning: {scan.reason}</p>"
    else:
        scan_warning = ""

    scan_note = ""
    if scan.warnings:
        scan_note = "<p style='color:#d69e2e;'>Scan notes: " + ", ".join(scan.warnings) + "</p>"

    html_body = f"""
    <div style="font-family:Inter,system-ui,sans-serif;max-width:600px;margin:0 auto;padding:32px;">
        <h2 style="color:#1a1a2e;margin-bottom:4px;">Task Delivered</h2>
        <p style="color:#666;margin-top:0;">From {provider_name or 'an agent'} on AgentYard</p>
        <hr style="border:none;border-top:1px solid #e2e8f0;margin:24px 0;" />
        {scan_warning}
        {scan_note}
        <div style="background:#f7fafc;border:1px solid #e2e8f0;border-radius:8px;padding:20px;margin:16px 0;">
            <h3 style="margin-top:0;color:#1a1a2e;">Output</h3>
            <pre style="white-space:pre-wrap;word-break:break-word;font-size:14px;color:#2d3748;">{output_content[:10000]}</pre>
        </div>
        <p style="color:#999;font-size:12px;margin-top:24px;">
            This output was scanned for integrity (blank files, corruption, malware).
            Quality disputes can be raised through the AgentYard platform.
        </p>
    </div>
    """

    async with httpx.AsyncClient(timeout=15) as client:
        try:
            response = await client.post(
                "https://api.resend.com/emails",
                headers={
                    "Authorization": f"Bearer {settings.resend_api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "from": settings.resend_from,
                    "to": [email],
                    "subject": f"Task delivered — {provider_name or 'AgentYard'}",
                    "html": html_body,
                },
            )
            response.raise_for_status()
            logger.info(f"Job {job.id} delivered via email to {email}")
            return True
        except httpx.HTTPStatusError as e:
            logger.error(f"Email delivery failed for job {job.id}: HTTP {e.response.status_code}")
            return False
        except httpx.RequestError as e:
            logger.error(f"Email delivery error for job {job.id}: {e}")
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
