from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "development"
    database_url: str = "postgresql+psycopg://clears_spend:clears_spend@localhost:5432/clears_spend"
    procrastinate_database_url: str = (
        "postgresql://clears_spend:clears_spend@localhost:5432/clears_spend"
    )
    ai_provider: str = "fake"
    openai_api_key: str | None = None
    openai_model: str = "gpt-5.6-terra"
    demo_auth_enabled: bool = True
    receipt_storage_endpoint: str = "http://localhost:9000"
    receipt_storage_access_key: str = "clears_spend"
    receipt_storage_secret_key: str = "clears_spend_dev_secret"
    receipt_quarantine_bucket: str = "clears-spend-quarantine"
    receipt_clean_bucket: str = "clears-spend-clean"
    receipt_storage_secure: bool = False
    receipt_encryption_key: str = (
        "MDEyMzQ1Njc4OWFiY2RlZjAxMjM0NTY3ODlhYmNkZWY="
    )
    clamav_host: str = "localhost"
    clamav_port: int = 3310
    malware_scan_required: bool = True
    log_level: str = "INFO"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
