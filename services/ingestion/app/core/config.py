from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Ingestion service runtime configuration loaded from the environment."""

    app_name: str = Field(
        default="Traffic Ingestion Service", description="Human-readable app name"
    )
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
    
    redis_url: str = Field(
        default="redis://localhost:6379/0",
        description="Redis connection URL for Celery broker",
    )
    
    celery_broker_url: str = Field(
        default="redis://localhost:6379/0",
        description="Celery broker URL",
    )
    
    celery_result_backend: str = Field(
        default="redis://localhost:6379/0",
        description="Celery result backend URL",
    )
    
    traffic_api_url: str = Field(
        default="http://localhost:8001/traffic",
        description="External traffic API endpoint URL",
    )
    
    traffic_api_key: str = Field(
        default="",
        description="API key for external traffic service",
    )
    
    traffic_poll_interval: int = Field(
        default=300,
        description="Interval in seconds to poll traffic API",
    )
    
    gps_batch_size: int = Field(
        default=50,
        description="Number of GPS events to batch before persisting",
    )
    
    gps_batch_timeout: int = Field(
        default=30,
        description="Maximum seconds to wait before flushing GPS batch",
    )

    model_config = SettingsConfigDict(
        env_prefix="INGESTION_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    """Return cached settings so expensive env parsing only occurs once."""

    return Settings()
