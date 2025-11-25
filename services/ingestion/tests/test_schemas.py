from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from app.schemas.gps import GPSEvent
from app.schemas.traffic import TrafficData


def test_gps_event_valid():
    """Test valid GPS event creation."""
    event = GPSEvent(
        fleet_number="BUS-001",
        latitude=37.7749,
        longitude=-122.4194,
        recorded_at=datetime.now(timezone.utc),
        speed_kph=45.5,
        heading=180,
        passenger_load=25,
    )
    assert event.fleet_number == "BUS-001"
    assert event.latitude == 37.7749
    assert event.longitude == -122.4194


def test_gps_event_invalid_latitude():
    """Test GPS event with invalid latitude."""
    with pytest.raises(ValidationError):
        GPSEvent(
            fleet_number="BUS-001",
            latitude=100.0,  # Invalid: > 90
            longitude=-122.4194,
            recorded_at=datetime.now(timezone.utc),
        )


def test_gps_event_invalid_longitude():
    """Test GPS event with invalid longitude."""
    with pytest.raises(ValidationError):
        GPSEvent(
            fleet_number="BUS-001",
            latitude=37.7749,
            longitude=-200.0,  # Invalid: < -180
            recorded_at=datetime.now(timezone.utc),
        )


def test_traffic_data_valid():
    """Test valid traffic data creation."""
    data = TrafficData(
        source="test_api",
        captured_at=datetime.now(timezone.utc),
        congestion_index=65,
        incident_count=3,
        average_speed_kph=42.5,
        payload={"region": "downtown"},
    )
    assert data.source == "test_api"
    assert data.congestion_index == 65
    assert data.incident_count == 3


def test_traffic_data_invalid_congestion():
    """Test traffic data with invalid congestion index."""
    with pytest.raises(ValidationError):
        TrafficData(
            source="test_api",
            captured_at=datetime.now(timezone.utc),
            congestion_index=150,  # Invalid: > 100
            incident_count=3,
        )
