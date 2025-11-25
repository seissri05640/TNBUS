import logging
from typing import Sequence

from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from ..schemas.gps import GPSEvent
from ..schemas.traffic import TrafficData

logger = logging.getLogger(__name__)


async def persist_gps_events(events: Sequence[GPSEvent], session: AsyncSession) -> int:
    """
    Persist a batch of GPS events to the telemetry_records table.
    Returns the number of records inserted.
    """
    if not events:
        return 0

    try:
        from sqlalchemy import text

        bus_fleet_numbers = {event.fleet_number for event in events}

        result = await session.execute(
            text("SELECT id, fleet_number FROM buses WHERE fleet_number = ANY(:fleet_numbers)"),
            {"fleet_numbers": list(bus_fleet_numbers)},
        )
        bus_map = {row[1]: row[0] for row in result.fetchall()}

        records = []
        skipped = 0
        for event in events:
            bus_id = bus_map.get(event.fleet_number)
            if not bus_id:
                logger.warning(f"Bus with fleet_number {event.fleet_number} not found, skipping")
                skipped += 1
                continue

            records.append(
                {
                    "bus_id": bus_id,
                    "recorded_at": event.recorded_at,
                    "latitude": event.latitude,
                    "longitude": event.longitude,
                    "speed_kph": event.speed_kph,
                    "heading": event.heading,
                    "passenger_load": event.passenger_load,
                }
            )

        if records:
            stmt = pg_insert(text("telemetry_records")).values(records)
            stmt = stmt.on_conflict_do_nothing(
                constraint="uq_telemetry_bus_recorded_at"
            )
            await session.execute(stmt)
            await session.commit()

            inserted = len(records)
            logger.info(
                f"Persisted {inserted} GPS events, skipped {skipped} (missing buses)"
            )
            return inserted

        logger.warning(f"No GPS events persisted, all {skipped} events skipped")
        return 0

    except Exception as e:
        await session.rollback()
        logger.error(f"Error persisting GPS events: {e}")
        raise


async def persist_traffic_data(traffic_data: TrafficData, session: AsyncSession) -> int:
    """
    Persist traffic snapshot data to the traffic_snapshots table.
    Returns the ID of the inserted record.
    """
    try:
        from sqlalchemy import text

        result = await session.execute(
            text(
                """
                INSERT INTO traffic_snapshots 
                (source, captured_at, congestion_index, incident_count, 
                 average_speed_kph, payload, created_at, updated_at)
                VALUES (:source, :captured_at, :congestion_index, :incident_count, 
                        :average_speed_kph, :payload, NOW(), NOW())
                RETURNING id
                """
            ),
            {
                "source": traffic_data.source,
                "captured_at": traffic_data.captured_at,
                "congestion_index": traffic_data.congestion_index,
                "incident_count": traffic_data.incident_count,
                "average_speed_kph": traffic_data.average_speed_kph,
                "payload": traffic_data.payload,
            },
        )
        await session.commit()

        traffic_id = result.scalar_one()
        logger.info(f"Persisted traffic snapshot with ID {traffic_id}")
        return traffic_id

    except Exception as e:
        await session.rollback()
        logger.error(f"Error persisting traffic data: {e}")
        raise
