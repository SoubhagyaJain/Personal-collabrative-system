from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Personal Collaborative API"
    app_env: str = "development"
    app_log_level: str = "INFO"
    app_host: str = "0.0.0.0"
    app_port: int = 8000

    database_url: str = Field(default="postgresql+asyncpg://postgres:postgres@postgres:5432/app_db")
    redis_url: str = Field(default="redis://redis:6379/0")
    model_version: str = "dev"
    home_cache_ttl_seconds: int = 60
    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:3000"])
    git_sha: str = "unknown"

    model_config = SettingsConfigDict(env_prefix="APP_", case_sensitive=False)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()