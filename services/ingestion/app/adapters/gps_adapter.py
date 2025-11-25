import logging
from collections import defaultdict
from datetime import datetime
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from ..schemas.gps import GPSEvent

logger = logging.getLogger(__name__)


class GPSAdapter:
    """Adapter for processing and validating GPS events before persistence."""

    def __init__(self, batch_size: int = 50, batch_timeout: int = 30):
        self.batch_size = batch_size
        self.batch_timeout = batch_timeout
        self._batches: dict[str, list[GPSEvent]] = defaultdict(list)
        self._last_flush: dict[str, datetime] = {}

    async def add_event(self, event: GPSEvent, session: AsyncSession) -> dict[str, Any]:
        """
        Add a GPS event to the batch for the corresponding fleet.
        Returns a status dict indicating if the batch was flushed.
        """
        fleet_key = event.fleet_number
        self._batches[fleet_key].append(event)

        if fleet_key not in self._last_flush:
            self._last_flush[fleet_key] = datetime.utcnow()

        should_flush = (
            len(self._batches[fleet_key]) >= self.batch_size
            or (datetime.utcnow() - self._last_flush[fleet_key]).total_seconds()
            >= self.batch_timeout
        )

        if should_flush:
            flushed_count = await self.flush_batch(fleet_key, session)
            return {"status": "flushed", "count": flushed_count, "fleet_number": fleet_key}

        return {
            "status": "batched",
            "count": len(self._batches[fleet_key]),
            "fleet_number": fleet_key,
        }

    async def flush_batch(self, fleet_key: str, session: AsyncSession) -> int:
        """Flush the batch for a specific fleet to the database."""
        if fleet_key not in self._batches or not self._batches[fleet_key]:
            return 0

        events = self._batches[fleet_key]
        logger.info(f"Flushing {len(events)} GPS events for fleet {fleet_key}")

        try:
            from ..services.persistence import persist_gps_events

            await persist_gps_events(events, session)
            count = len(events)

            self._batches[fleet_key].clear()
            self._last_flush[fleet_key] = datetime.utcnow()

            return count
        except Exception as e:
            logger.error(f"Error flushing GPS batch for {fleet_key}: {e}")
            raise

    async def flush_all(self, session: AsyncSession) -> int:
        """Flush all pending batches to the database."""
        total_flushed = 0
        for fleet_key in list(self._batches.keys()):
            flushed = await self.flush_batch(fleet_key, session)
            total_flushed += flushed
        return total_flushed
