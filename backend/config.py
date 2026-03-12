"""
AgentYard — Configuration
All settings loaded from environment variables.
"""
from pydantic import ConfigDict, Field
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    model_config = ConfigDict(env_file=".env", extra="ignore")

    # Database
    database_url: str = "sqlite+aiosqlite:///./agentyard.db"

    # Redis
    redis_url: str = "redis://localhost:6379"

    # LNBits
    lnbits_url: str = "https://demo.lnbits.com"
    lnbits_escrow_wallet_adminkey: str = ""
    lnbits_escrow_wallet_inkey: str = ""
    lnbits_fee_wallet_adminkey: str = ""
    lnbits_stake_wallet_adminkey: str = ""
    lnbits_webhook_secret: str = Field(default="stub_webhook_secret")

    # Lightning stub — set LIGHTNING_STUB=true or LNBITS_URL=stub to bypass real LNBits
    lightning_stub: bool = False

    # Auth
    jwt_secret: str = Field(..., min_length=32)
    jwt_expiry_hours: int = 24
    jwt_algorithm: str = "HS256"

    # Platform
    platform_fee_rate: float = 0.12
    agentyard_webhook_secret: str = Field(default="stub_agentyard_secret")

    # GitHub OAuth
    # Replace with real secret from github.com/settings/developers
    github_client_id: str = Field(default="")
    github_client_secret: str = Field(...)
    github_callback_url: str = Field(default="http://localhost:8000/auth/github/callback")
    frontend_url: str = Field(default="http://localhost:5173")

    # Escrow timing — 10 min window buyers have to dispute before auto-release
    dispute_window_minutes: int = 10

    # JSS thresholds — agents below these get rate-limited or suspended
    jss_rate_limit_threshold: float = 80.0   # below → rate_limited (still listed, flagged)
    jss_delist_threshold: float = 70.0        # below → suspended (removed from marketplace)

    # Buyer protection pool — 2% of each platform fee goes to the pool
    buyer_protection_rate: float = 0.02
    buyer_protection_max_sats: int = 50000    # max payout per dispute claim

    # Resend (email delivery)
    resend_api_key: str = ""
    resend_from: str = "AgentYard <noreply@agentyard.dev>"

    # Admin
    admin_email: str = "admin@agentyard.dev"
    admin_discord_webhook: Optional[str] = None
    admin_api_key: str = Field(...)

    # App
    app_env: str = "development"
    debug: bool = False

    @property
    def is_sqlite(self) -> bool:
        return "sqlite" in self.database_url


settings = Settings()
