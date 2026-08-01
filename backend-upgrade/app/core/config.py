"""
app/core/config.py
Application settings and configuration management via Pydantic BaseSettings.
"""
from functools import lru_cache
from typing import Optional
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict



class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", ".env.local"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # App
    APP_ENV: str = "development"
    APP_SECRET_KEY: str = "dev-secret-change-in-production"
    LOG_LEVEL: str = "INFO"
    ALLOWED_ORIGINS: str = "http://localhost:3000"
    FRONTEND_URL: str = "http://localhost:3000"

    # Database (Supabase PostgreSQL / Managed Postgres compatible)
    DATABASE_URL: str = "postgresql://avenor_user:avenor_pass@localhost:5432/avenor_db"
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    DB_POOL_RECYCLE: int = 1800
    DB_POOL_PRE_PING: bool = True
    DB_SSL_MODE: Optional[str] = None

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # AI (Google Gemini via OpenAI-compatible endpoint)
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.0-flash"
    GEMINI_EMBEDDING_MODEL: str = "gemini-embedding-001"

    # Phase 5.1 — AI Account Research
    # Active LLM provider for the research engine. Registered providers live in
    # app/modules/ai/provider.py — adding one here requires no service changes.
    AI_PROVIDER: str = "gemini"
    AI_REQUEST_TIMEOUT_SECONDS: float = 90.0
    AI_MAX_RETRIES: int = 2
    AI_RESEARCH_STALE_RUNNING_MINUTES: int = 10

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
    HUBSPOT_REDIRECT_URI: str = "https://backend-45395119059.asia-south1.run.app/api/v1/integrations/hubspot/callback"

    # Salesforce
    SALESFORCE_CLIENT_ID: str = ""
    SALESFORCE_CLIENT_SECRET: str = ""
    SALESFORCE_REDIRECT_URI: str = "http://localhost:8000/api/v1/crm/salesforce/callback"
    SALESFORCE_SANDBOX: bool = False                         # True = test.salesforce.com

    # Microsoft Dynamics 365
    DYNAMICS_CLIENT_ID: str = ""
    DYNAMICS_CLIENT_SECRET: str = ""
    DYNAMICS_TENANT_ID: str = "common"                      # Azure AD tenant ID or "common"
    DYNAMICS_REDIRECT_URI: str = "http://localhost:8000/api/v1/crm/dynamics/callback"

    # Zoho CRM
    ZOHO_CLIENT_ID: str = ""
    ZOHO_CLIENT_SECRET: str = ""
    ZOHO_REDIRECT_URI: str = "http://localhost:8000/api/v1/crm/zoho/callback"
    ZOHO_DATA_CENTER: str = "com"                           # com, eu, in, au, jp, ca

    # ── Generic CRM settings ──────────────────────────────────────────────────
    CRM_SYNC_INTERVAL_MINUTES: int = 30
    CRM_HISTORICAL_DAYS: int = 180
    CRM_HISTORICAL_BATCH_SIZE: int = 100
    CRM_FUZZY_MATCH_THRESHOLD: int = 85
    CRM_DEFAULT_PROVIDER: str = ""                          # Global default; workspace-level overrides

    # ── Feature flags — enable/disable providers without code changes ─────────
    ENABLE_HUBSPOT: bool = True
    ENABLE_SALESFORCE: bool = True
    ENABLE_DYNAMICS: bool = True
    ENABLE_ZOHO: bool = True
    ENABLE_PIPEDRIVE: bool = False                          # Future
    ENABLE_FRESHSALES: bool = False                         # Future


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
    HUBSPOT_FUZZY_MATCH_THRESHOLD: int = 85

    @field_validator("DATABASE_URL")
    @classmethod
    def validate_db_url(cls, v: str) -> str:
        if v.startswith("postgres://"):
            v = "postgresql://" + v[len("postgres://"):]
        if not v.startswith("postgresql://") and not v.startswith("postgresql+psycopg2://"):
            raise ValueError("DATABASE_URL must start with postgresql:// or postgres://")
        return v

    @property
    def is_production(self) -> bool:
        return self.APP_ENV == "production"

    @property
    def is_development(self) -> bool:
        return self.APP_ENV == "development"

    @property
    def effective_salesforce_redirect_uri(self) -> str:
        """Return environment-aware Salesforce redirect URI (localhost for dev, cloud run for prod)."""
        if self.is_development:
            if "localhost" not in self.SALESFORCE_REDIRECT_URI and "127.0.0.1" not in self.SALESFORCE_REDIRECT_URI:
                return "http://localhost:8000/api/v1/integrations/salesforce/callback"
        return self.SALESFORCE_REDIRECT_URI

    @property
    def effective_hubspot_redirect_uri(self) -> str:
        """Return environment-aware HubSpot redirect URI (localhost for dev, cloud run for prod)."""
        if self.is_development:
            if "localhost" not in self.HUBSPOT_REDIRECT_URI and "127.0.0.1" not in self.HUBSPOT_REDIRECT_URI:
                return "http://localhost:8000/api/v1/integrations/hubspot/callback"
        return self.HUBSPOT_REDIRECT_URI

    @property
    def frontend_base(self) -> str:
        """Return clean base URL for frontend redirects (environment-aware)."""
        if self.FRONTEND_URL and self.FRONTEND_URL.strip():
            return self.FRONTEND_URL.strip().rstrip("/")
        if self.is_production:
            return "https://avenorai.in"
        origins = self.allowed_origins_list
        for o in origins:
            o_clean = o.rstrip("/")
            if o_clean != "*" and ("localhost" in o_clean or "avenor" in o_clean):
                return o_clean
        return "http://localhost:3000"

    @property
    def allowed_origins_list(self) -> list[str]:
        if self.ALLOWED_ORIGINS.strip() == "*":
            return ["*"]
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",") if o.strip()]

    @property
    def has_gemini(self) -> bool:
        return bool(self.GEMINI_API_KEY)

    @property
    def has_ai(self) -> bool:
        """True when the configured AI_PROVIDER has the credentials it needs."""
        if self.AI_PROVIDER == "gemini":
            return self.has_gemini
        return False

    @property
    def has_apollo(self) -> bool:
        return bool(self.APOLLO_API_KEY)

    @property
    def has_hubspot(self) -> bool:
        return bool(self.HUBSPOT_APP_CLIENT_ID and self.HUBSPOT_APP_CLIENT_SECRET)

    @property
    def has_salesforce(self) -> bool:
        return bool(self.SALESFORCE_CLIENT_ID and self.SALESFORCE_CLIENT_SECRET)

    @property
    def has_dynamics(self) -> bool:
        return bool(self.DYNAMICS_CLIENT_ID and self.DYNAMICS_CLIENT_SECRET)

    @property
    def has_zoho(self) -> bool:
        return bool(self.ZOHO_CLIENT_ID and self.ZOHO_CLIENT_SECRET)

    @property
    def has_encryption_key(self) -> bool:
        return bool(self.ENCRYPTION_KEY)

    @property
    def enabled_crm_providers(self) -> list[str]:
        """Return list of CRM provider slugs that are both configured and feature-flagged on."""
        providers = []
        if self.ENABLE_HUBSPOT and self.has_hubspot:
            providers.append("hubspot")
        if self.ENABLE_SALESFORCE and self.has_salesforce:
            providers.append("salesforce")
        if self.ENABLE_DYNAMICS and self.has_dynamics:
            providers.append("dynamics")
        if self.ENABLE_ZOHO and self.has_zoho:
            providers.append("zoho")
        return providers



@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


# Convenience alias
settings = get_settings()
