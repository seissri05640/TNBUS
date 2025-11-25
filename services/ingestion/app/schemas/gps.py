from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class GPSEvent(BaseModel):
    """Schema for validating incoming GPS telemetry events."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "fleet_number": "BUS-001",
                "latitude": 37.7749,
                "longitude": -122.4194,
                "recorded_at": "2024-01-15T10:30:00Z",
                "speed_kph": 45.5,
                "heading": 180,
                "passenger_load": 25,
            }
        }
    )

    fleet_number: str = Field(..., description="Unique identifier for the bus")
    latitude: float = Field(..., ge=-90, le=90, description="GPS latitude coordinate")
    longitude: float = Field(..., ge=-180, le=180, description="GPS longitude coordinate")
    recorded_at: datetime = Field(..., description="Timestamp when the GPS reading was recorded")
    speed_kph: float | None = Field(None, ge=0, le=200, description="Vehicle speed in km/h")
    heading: int | None = Field(
        None, ge=0, le=359, description="Vehicle heading in degrees (0-359)"
    )
    passenger_load: int | None = Field(None, ge=0, description="Current number of passengers")

    @field_validator("fleet_number")
    @classmethod
    def validate_fleet_number(cls, v: str) -> str:
        if not v or len(v) > 32:
            raise ValueError("fleet_number must be non-empty and at most 32 characters")
        return v
