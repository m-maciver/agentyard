"""
Tests for reputation and stake calculations.
"""
import pytest
from api.services.reputation import (
    calculate_reputation,
    calculate_stake_pct,
    calculate_stake_sats,
    calculate_platform_fee,
    get_max_job_sats,
)


def test_reputation_no_jobs():
    """0 jobs → 0.0 score."""
    assert calculate_reputation(0, 0) == 0.0


def test_reputation_perfect():
    """Many jobs, no disputes → high score."""
    score = calculate_reputation(jobs_completed=50, jobs_disputed=0, avg_delivery_time_mins=30)
    assert score > 90


def test_reputation_with_disputes():
    """Disputes lower score."""
    clean = calculate_reputation(10, 0)
    disputed = calculate_reputation(10, 3)
    assert disputed < clean


def test_reputation_caps_at_100():
    """Score never exceeds 100."""
    score = calculate_reputation(1000, 0, avg_delivery_time_mins=1)
    assert score <= 100.0


def test_stake_pct_new_agent():
    """New agent with 0 rep gets 30% stake."""
    pct = calculate_stake_pct(0.0, 1000)
    assert pct == 0.30


def test_stake_pct_high_rep():
    """High rep agent gets low stake (min 5%)."""
    pct = calculate_stake_pct(100.0, 1000)
    assert pct == 0.05


def test_stake_pct_large_job():
    """Large job (>10k sats) adds 10% stake."""
    base_pct = calculate_stake_pct(100.0, 1000)  # 5% for high rep
    large_job_pct = calculate_stake_pct(100.0, 50_000)  # Should be 15%
    assert large_job_pct > base_pct
    assert large_job_pct <= 0.50  # Capped at 50%


def test_stake_pct_never_exceeds_50():
    """Stake never exceeds 50%."""
    pct = calculate_stake_pct(0.0, 100_000)
    assert pct <= 0.50


def test_stake_sats_calculation():
    """Stake sats = ceil(price * pct)."""
    sats = calculate_stake_sats(10_000, 0.0)  # 30% of 10k = 3000
    assert sats == 3000


def test_platform_fee_standard():
    """Standard fee is 12%."""
    fee = calculate_platform_fee(10_000, reputation_score=50)
    assert fee == 1200


def test_platform_fee_high_rep():
    """High rep agents get 10% fee."""
    fee = calculate_platform_fee(10_000, reputation_score=90)
    assert fee == 1000


def test_max_job_sats_unverified():
    """Unverified agents capped at 50k."""
    cap = get_max_job_sats(0.0, 0, is_verified=False)
    assert cap == 50_000


def test_max_job_sats_high_rep():
    """High rep verified agents get large cap."""
    cap = get_max_job_sats(90.0, 100, is_verified=True)
    assert cap >= 1_000_000
