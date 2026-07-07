from __future__ import annotations

from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    app_name: str = "Garment Deal Finder"
    environment: str = "development"
    debug: bool = False
    secret_key: str = "change-me-in-production"
    admin_token: str = "change-me-admin-token"

    database_url: str = Field(default="sqlite+aiosqlite:///./garment_deals.sqlite3")
    redis_url: str = "redis://localhost:6379/0"
    use_celery: bool = False
    auto_create_tables: bool = True

    user_agent: str = (
        "GarmentDealFinderBot/1.0 (+https://example.local/garment-deal-finder; "
        "contact: admin@example.local)"
    )
    request_timeout_seconds: float = 12.0
    retailer_request_delay_seconds: float = 0.2
    max_retailer_failures: int = 2
    page_cache_ttl_seconds: int = 600
    search_rate_limit_per_minute: int = 20

    demo_user_email: str = "demo@garment.local"
    nicegui_storage_secret: str = "dev-nicegui-storage-secret"
    allowed_product_url_hosts: list[str] = Field(
        default_factory=lambda: ["www.google.com", "images.unsplash.com"]
    )

    @field_validator("database_url")
    @classmethod
    def normalize_database_url(cls, value: str) -> str:
        if value.startswith("postgresql://"):
            return value.replace("postgresql://", "postgresql+asyncpg://", 1)
        return value

    @field_validator("debug", mode="before")
    @classmethod
    def parse_debug_flag(cls, value: object) -> object:
        if isinstance(value, str) and value.lower() in {"release", "prod", "production"}:
            return False
        return value


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
