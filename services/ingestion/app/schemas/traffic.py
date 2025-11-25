from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class TrafficData(BaseModel):
    """Schema for validating traffic data from external APIs."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "source": "traffic_api_v1",
                "captured_at": "2024-01-15T10:30:00Z",
                "congestion_index": 65,
                "incident_count": 3,
                "average_speed_kph": 42.5,
                "payload": {"region": "downtown", "weather": "clear"},
            }
        }
    )

    source: str = Field(..., max_length=64, description="Source identifier for the traffic data")
    captured_at: datetime = Field(..., description="Timestamp when the traffic data was captured")
    congestion_index: int = Field(
        ..., ge=0, le=100, description="Traffic congestion index (0-100)"
    )
    incident_count: int = Field(..., ge=0, description="Number of reported traffic incidents")
    average_speed_kph: float | None = Field(
        None, ge=0, le=200, description="Average traffic speed in km/h"
    )
    payload: dict[str, Any] | None = Field(
        None, description="Additional data from the traffic API"
    )
