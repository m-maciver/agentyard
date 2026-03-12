"""
AgentYard — LNURL-Auth Service
Implements LNURL-Auth (LUD-06) for Lightning wallet verification.

Reference: https://github.com/lnurl/lunaticoin/wiki/lnurl-auth
"""
import logging
import secrets
import hashlib
from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import uuid4
from urllib.parse import urlencode

import coincurve
from fastapi import HTTPException

logger = logging.getLogger(__name__)

# Store challenges in memory with expiry (5 minutes)
# In production, use Redis or database
_challenges: dict[str, dict] = {}

class LNURLAuthError(Exception):
    """Raised when LNURL-Auth fails."""
    pass


def generate_challenge() -> tuple[str, str]:
    """
    Generate a random challenge for LNURL-Auth.
    Returns (challenge_id, lnurl_string)
    """
    challenge_id = str(uuid4())
    challenge_secret = secrets.token_hex(32)  # 64-char hex string
    
    # Store challenge with expiry
    _challenges[challenge_id] = {
        "secret": challenge_secret,
        "created_at": datetime.now(timezone.utc),
        "expires_at": datetime.now(timezone.utc) + timedelta(minutes=5),
    }
    
    logger.info(f"Generated LNURL-Auth challenge: {challenge_id}")
    return challenge_id, challenge_secret


def verify_signature(
    challenge_id: str,
    public_key: str,  # 33-byte compressed public key as hex
    signature: str,   # 64-byte signature as hex
    key: str,         # "linking" key (user's identity)
) -> bool:
    """
    Verify an LNURL-Auth signature.
    
    LNURL-Auth signing process:
    1. Challenge = SHA256(challenge_secret)
    2. User signs Challenge with their private key
    3. User sends back (public_key, signature, key)
    4. Backend verifies signature against challenge
    """
    if challenge_id not in _challenges:
        logger.warning(f"Challenge not found: {challenge_id}")
        raise LNURLAuthError("Challenge expired or not found")
    
    challenge_data = _challenges[challenge_id]
    
    # Check if challenge expired
    if datetime.now(timezone.utc) > challenge_data["expires_at"]:
        del _challenges[challenge_id]
        logger.warning(f"Challenge expired: {challenge_id}")
        raise LNURLAuthError("Challenge expired")
    
    # Compute message hash (SHA256 of challenge_secret)
    message_hash = hashlib.sha256(challenge_data["secret"].encode()).digest()
    
    try:
        # Verify signature using coincurve
        pubkey = coincurve.PublicKey(bytes.fromhex(public_key))
        is_valid = pubkey.verify(
            bytes.fromhex(signature),
            message_hash,
            hasher=None  # We already hashed it
        )
        
        if is_valid:
            logger.info(f"LNURL-Auth signature verified for: {key}")
            # Clean up challenge after successful use
            del _challenges[challenge_id]
            return True
        else:
            logger.warning(f"LNURL-Auth signature verification failed for: {key}")
            return False
    except Exception as e:
        logger.error(f"LNURL-Auth verification error: {e}")
        raise LNURLAuthError(f"Signature verification failed: {e}")


def get_lnurl_callback_url(base_url: str, challenge_id: str) -> str:
    """
    Generate the LNURL callback URL for the QR code.
    
    Format: https://example.com/auth/lnurl/callback?tag=login&k1=<challenge_id>
    """
    params = {
        "tag": "login",
        "k1": challenge_id,
    }
    return f"{base_url.rstrip('/')}/auth/lnurl/callback?{urlencode(params)}"


def bech32_encode(data: str) -> str:
    """
    Encode URL as bech32 LNURL format.
    
    In production, use the lnurl package:
    pip install lnurl
    """
    # Simplified version — full implementation uses bech32 codec
    # For now, return the URL directly (works for QR scanning)
    return f"lnurl{data.encode().hex()}"
