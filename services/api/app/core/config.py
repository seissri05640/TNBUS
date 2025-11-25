from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application runtime configuration loaded from the environment."""

    app_name: str = Field(default="Traffic Services API", description="Human-readable app name")
    environment: Literal["local", "test", "staging", "production"] = Field(
        default="local", description="Deployment environment name"
    )
    debug: bool = Field(default=False, description="Enables FastAPI debug mode")
    version: str = Field(default="0.1.0", description="Semantic API version string")
    log_level: str = Field(default="INFO", description="Root logger level")
    database_url: str = Field(
        default="postgresql+asyncpg://traffic:traffic@localhost:5432/traffic",
        description="SQLAlchemy connection string for the primary database",
    )

    model_config = SettingsConfigDict(
        env_prefix="API_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    """Return cached settings so expensive env parsing only occurs once."""

    return Settings()
