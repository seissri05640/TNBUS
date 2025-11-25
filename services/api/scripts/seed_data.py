from __future__ import annotations

import asyncio
from datetime import datetime, timedelta, timezone

from sqlalchemy import delete

from app.db.session import get_sessionmaker
from app.models import Bus, BusStatus, Prediction, Route, TelemetryRecord, TrafficSnapshot


async def seed() -> None:
    """Populate the database with deterministic sample data for local development."""

    session_factory = get_sessionmaker()
    async with session_factory() as session:
        # Clean up existing records in dependency order to satisfy FK constraints.
        for model in (Prediction, TelemetryRecord, Bus, TrafficSnapshot, Route):
            await session.execute(delete(model))
        await session.commit()

        now = datetime.now(timezone.utc)

        downtown_loop = Route(
            code="R1",
            name="Downtown Loop",
            origin="Union Station",
            destination="Hillcrest",
        )
        airport_express = Route(
            code="AX",
            name="Airport Express",
            origin="Central Terminal",
            destination="North Airport",
        )
        session.add_all([downtown_loop, airport_express])

        bus_1001 = Bus(fleet_number="BUS-1001", route=downtown_loop, capacity=60)
        bus_1002 = Bus(fleet_number="BUS-1002", route=downtown_loop)
        bus_2001 = Bus(
            fleet_number="BUS-2001",
            route=airport_express,
            status=BusStatus.MAINTENANCE,
        )
        session.add_all([bus_1001, bus_1002, bus_2001])
        await session.flush()

        telemetry_records = [
            TelemetryRecord(
                bus=bus_1001,
                recorded_at=now - timedelta(minutes=10),
                latitude=40.7128,
                longitude=-74.006,
                speed_kph=32.5,
                heading=180,
                passenger_load=24,
            ),
            TelemetryRecord(
                bus=bus_1001,
                recorded_at=now - timedelta(minutes=5),
                latitude=40.706,
                longitude=-74.009,
                speed_kph=28.1,
                heading=175,
                passenger_load=27,
            ),
            TelemetryRecord(
                bus=bus_1002,
                recorded_at=now - timedelta(minutes=6),
                latitude=40.721,
                longitude=-74.002,
                speed_kph=35.0,
                heading=5,
                passenger_load=18,
            ),
        ]
        session.add_all(telemetry_records)

        traffic_snapshot = TrafficSnapshot(
            source="DOT Feed",
            captured_at=now - timedelta(minutes=15),
            congestion_index=68,
            incident_count=2,
            average_speed_kph=33.2,
            payload={"note": "Two-lane closure near Hillcrest"},
        )
        session.add(traffic_snapshot)

        prediction = Prediction(
            route=downtown_loop,
            traffic_snapshot=traffic_snapshot,
            target_arrival=now + timedelta(minutes=25),
            estimated_headway_minutes=12,
            travel_time_minutes=47,
            confidence=0.78,
            notes="Expect lingering delays due to construction",
        )
        session.add(prediction)

        await session.commit()


if __name__ == "__main__":
    asyncio.run(seed())
