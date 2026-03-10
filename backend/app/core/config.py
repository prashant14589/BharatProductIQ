"""Application configuration."""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings from environment."""

    # App
    app_name: str = "BharatProductIQ"
    debug: bool = False

    # Database
    database_url: str = "postgresql://postgres:postgres@localhost:5432/bharatproductiq"

    # Redis
    redis_url: str = "redis://localhost:6379/0"
    celery_broker_url: str = "redis://localhost:6379/1"

    # AI
    openai_api_key: str | None = None
    anthropic_api_key: str | None = None
    ai_provider: str = "openai"  # openai | anthropic

    # Pipeline
    min_margin_pct: float = 40.0
    min_score: int = 70
    price_min_inr: int = 799
    price_max_inr: int = 2499
    top_products_count: int = 5

    # CORS
    cors_origins: list[str] = ["http://localhost:3000"]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


@lru_cache
def get_settings() -> Settings:
    return Settings()
