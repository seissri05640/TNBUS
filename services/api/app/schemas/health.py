from typing import Literal

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: Literal["ok", "degraded", "unhealthy"] = Field(
        description="Overall service health indicator"
    )
    environment: str = Field(description="Deployment environment name")
    uptime_seconds: int = Field(description="Number of seconds since process start")
