from functools import lru_cache
from typing import Optional
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # App
    APP_ENV: str = "development"
    APP_SECRET_KEY: str = "dev-secret-change-in-production"
    LOG_LEVEL: str = "INFO"
    ALLOWED_ORIGINS: str = "http://localhost:3000"

    # Database
    DATABASE_URL: str = "postgresql://avenor_user:avenor_pass@localhost:5432/avenor_db"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # AI
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o"
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"

    # Signal sources
    APOLLO_API_KEY: str = ""
    CRUNCHBASE_API_KEY: str = ""
    BUILTITH_API_KEY: str = ""
    BRIGHTDATA_USERNAME: str = ""
    BRIGHTDATA_PASSWORD: str = ""
    SERPAPI_KEY: str = ""

    # HubSpot
    HUBSPOT_APP_CLIENT_ID: str = ""
    HUBSPOT_APP_CLIENT_SECRET: str = ""
    HUBSPOT_WEBHOOK_SECRET: str = ""

    # Integrations
    INSTANTLY_API_KEY: str = ""
    SLACK_WEBHOOK_URL: str = ""

    # Observability
    SENTRY_DSN: str = ""
    LOGFIRE_TOKEN: str = ""

    # Worker schedules
    SIGNAL_COLLECTION_CRON: str = "0 */6 * * *"
    SCORE_COMPUTATION_CRON: str = "30 */6 * * *"
    FEED_GENERATION_CRON: str = "0 2 * * *"
    MODEL_RECALIBRATION_CRON: str = "0 2 * * 6"

    # LLM limits
    LLM_CACHE_TTL_HOURS: int = 24
    LLM_MAX_REQUESTS_PER_WORKSPACE_PER_HOUR: int = 10

    # Phase 4.2 — HubSpot CRM sync
    # Fernet key — generate: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
    ENCRYPTION_KEY: str = ""
    HUBSPOT_HISTORICAL_DAYS: int = 180
    HUBSPOT_SYNC_INTERVAL_MINUTES: int = 30
    HUBSPOT_HISTORICAL_BATCH_SIZE: int = 100

    @field_validator("DATABASE_URL")
    @classmethod
    def validate_db_url(cls, v: str) -> str:
        if not v.startswith("postgresql://"):
            raise ValueError("DATABASE_URL must start with postgresql://")
        return v

    @property
    def is_production(self) -> bool:
        return self.APP_ENV == "production"

    @property
    def is_development(self) -> bool:
        return self.APP_ENV == "development"

    @property
    def allowed_origins_list(self) -> list[str]:
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",")]

    @property
    def has_openai(self) -> bool:
        return bool(self.OPENAI_API_KEY and not self.OPENAI_API_KEY.startswith("sk-..."))

    @property
    def has_apollo(self) -> bool:
        return bool(self.APOLLO_API_KEY)

    @property
    def has_hubspot(self) -> bool:
        return bool(self.HUBSPOT_APP_CLIENT_ID and self.HUBSPOT_APP_CLIENT_SECRET)

    @property
    def has_encryption_key(self) -> bool:
        return bool(self.ENCRYPTION_KEY)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


# Convenience alias
settings = get_settings()
