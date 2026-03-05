"""
AgentYard — LNBits REST API client
All Lightning operations go through here.
"""
import logging
from typing import Optional

import httpx

from config import settings

logger = logging.getLogger(__name__)

LNBITS_URL = settings.lnbits_url.rstrip("/")


class LNBitsError(Exception):
    """Raised when LNBits returns an error."""
    pass


async def create_invoice(
    invoice_key: str,
    amount_sats: int,
    memo: str,
    webhook: Optional[str] = None,
) -> dict:
    """
    Create a Lightning invoice (inbound payment request).
    Returns dict with 'payment_hash' and 'payment_request' (bolt11).
    """
    payload: dict = {
        "out": False,
        "amount": amount_sats,
        "memo": memo,
    }
    if webhook:
        payload["webhook"] = webhook

    async with httpx.AsyncClient(timeout=30) as client:
        try:
            response = await client.post(
                f"{LNBITS_URL}/api/v1/payments",
                headers={"X-Api-Key": invoice_key},
                json=payload,
            )
            response.raise_for_status()
            data = response.json()
            return {
                "payment_hash": data["payment_hash"],
                "payment_request": data["payment_request"],
            }
        except httpx.HTTPStatusError as e:
            logger.error(f"LNBits create_invoice failed: {e.response.text}")
            raise LNBitsError(f"Failed to create invoice: {e.response.text}") from e
        except httpx.RequestError as e:
            logger.error(f"LNBits connection error: {e}")
            raise LNBitsError(f"LNBits connection error: {e}") from e


async def check_invoice(invoice_key: str, payment_hash: str) -> bool:
    """
    Check if an invoice has been paid.
    Returns True if paid, False if pending.
    """
    async with httpx.AsyncClient(timeout=30) as client:
        try:
            response = await client.get(
                f"{LNBITS_URL}/api/v1/payments/{payment_hash}",
                headers={"X-Api-Key": invoice_key},
            )
            response.raise_for_status()
            data = response.json()
            return data.get("paid", False)
        except httpx.HTTPStatusError as e:
            logger.error(f"LNBits check_invoice failed: {e.response.text}")
            raise LNBitsError(f"Failed to check invoice: {e.response.text}") from e
        except httpx.RequestError as e:
            logger.error(f"LNBits connection error: {e}")
            raise LNBitsError(f"LNBits connection error: {e}") from e


async def pay_invoice(admin_key: str, bolt11: str) -> dict:
    """
    Pay a Lightning invoice (outbound payment).
    Returns payment details including payment_hash.
    """
    async with httpx.AsyncClient(timeout=60) as client:
        try:
            response = await client.post(
                f"{LNBITS_URL}/api/v1/payments",
                headers={"X-Api-Key": admin_key},
                json={"out": True, "bolt11": bolt11},
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"LNBits pay_invoice failed: {e.response.text}")
            raise LNBitsError(f"Failed to pay invoice: {e.response.text}") from e
        except httpx.RequestError as e:
            logger.error(f"LNBits connection error: {e}")
            raise LNBitsError(f"LNBits connection error: {e}") from e


async def get_wallet_balance(invoice_key: str) -> int:
    """
    Get wallet balance in sats.
    """
    async with httpx.AsyncClient(timeout=30) as client:
        try:
            response = await client.get(
                f"{LNBITS_URL}/api/v1/wallet",
                headers={"X-Api-Key": invoice_key},
            )
            response.raise_for_status()
            data = response.json()
            # LNBits returns balance in millisatoshis
            return data.get("balance", 0) // 1000
        except httpx.HTTPStatusError as e:
            logger.error(f"LNBits get_wallet_balance failed: {e.response.text}")
            raise LNBitsError(f"Failed to get wallet balance: {e.response.text}") from e
        except httpx.RequestError as e:
            logger.error(f"LNBits connection error: {e}")
            raise LNBitsError(f"LNBits connection error: {e}") from e


async def create_provider_invoice(agent_wallet_id: str, agent_invoice_key: str, amount_sats: int, memo: str) -> dict:
    """
    Create an invoice on the provider's own LNBits wallet.
    Used when releasing payment to provider — we generate an invoice on their side,
    then pay it from our escrow wallet.
    """
    return await create_invoice(
        invoice_key=agent_invoice_key,
        amount_sats=amount_sats,
        memo=memo,
    )
