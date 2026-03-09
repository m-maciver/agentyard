"""
AgentYard — Platform stats helper
Simple JSON file for lightweight platform-level accounting.
WHY: avoids a whole new DB table for what is essentially a few running counters.
"""
import json
import os
from pathlib import Path

STATS_PATH = Path(__file__).parent.parent.parent / "data" / "platform_stats.json"

_DEFAULTS = {
    "protection_pool_sats": 0,
    "total_fees_collected": 0,
    "total_disputes_resolved": 0,
    "total_buyer_protection_paid": 0,
}


def load_stats() -> dict:
    if STATS_PATH.exists():
        with open(STATS_PATH) as f:
            return {**_DEFAULTS, **json.load(f)}
    return dict(_DEFAULTS)


def save_stats(stats: dict) -> None:
    STATS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(STATS_PATH, "w") as f:
        json.dump(stats, f, indent=2)


def contribute_to_pool(platform_fee_sats: int) -> int:
    """
    Add 2% of platform fee to the buyer protection pool.
    Returns the contribution amount.
    """
    from config import settings
    contribution = int(platform_fee_sats * settings.buyer_protection_rate)
    stats = load_stats()
    stats["protection_pool_sats"] += contribution
    stats["total_fees_collected"] += platform_fee_sats
    save_stats(stats)
    return contribution


def pay_from_pool(amount_sats: int) -> int:
    """
    Pay buyer protection from the pool. Caps at BUYER_PROTECTION_MAX_SATS and pool balance.
    Returns actual amount paid.
    """
    from config import settings
    stats = load_stats()
    capped = min(amount_sats, settings.buyer_protection_max_sats, stats["protection_pool_sats"])
    stats["protection_pool_sats"] -= capped
    stats["total_buyer_protection_paid"] += capped
    stats["total_disputes_resolved"] += 1
    save_stats(stats)
    return capped
