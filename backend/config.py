"""
AgentYard — Configuration
All settings loaded from environment variables.
"""
from pydantic import ConfigDict
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
    lnbits_webhook_secret: str = "dev_webhook_secret"

    # Auth
    jwt_secret: str = "dev_jwt_secret_change_in_production"
    jwt_expiry_hours: int = 24
    jwt_algorithm: str = "HS256"

    # Platform
    platform_fee_rate: float = 0.12
    agentyard_webhook_secret: str = "dev_agentyard_webhook_secret"

    # Admin
    admin_email: str = "admin@agentyard.dev"
    admin_discord_webhook: Optional[str] = None
    admin_api_key: str = "dev_admin_key"

    # App
    app_env: str = "development"
    debug: bool = True

    @property
    def is_sqlite(self) -> bool:
        return "sqlite" in self.database_url


settings = Settings()
