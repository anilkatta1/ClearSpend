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
    log_level: str = "INFO"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
