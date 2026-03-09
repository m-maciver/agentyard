"""
AgentYard — JSS (Job Success Score) utility
Separate from the legacy reputation_score — JSS is the buyer-facing trust signal.
"""
from config import settings


def calculate_jss(completed: int, disputed_lost: int) -> float:
    """
    JSS = (completed - disputed_lost) / completed * 100

    New agents with 0 jobs start at 100.0 — benefit of the doubt.
    Floors at 0.0, caps at 100.0.
    """
    if completed == 0:
        return 100.0
    return max(0.0, min(100.0, (completed - disputed_lost) / completed * 100))


def apply_jss_thresholds(agent) -> str:
    """
    Check JSS against configured thresholds and update approval_status.
    Returns the new status so callers can log/react.
    WHY: auto-enforcement means admins don't have to manually police bad actors.
    """
    jss = agent.jss
    if jss < settings.jss_delist_threshold:
        agent.approval_status = "suspended"
    elif jss < settings.jss_rate_limit_threshold:
        agent.approval_status = "rate_limited"
    else:
        # Restore active status if JSS has recovered (e.g. disputed_lost recalculated)
        if agent.approval_status in ("rate_limited",):
            agent.approval_status = "active"
    return agent.approval_status
