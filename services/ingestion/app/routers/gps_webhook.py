import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..adapters.gps_adapter import GPSAdapter
from ..core.config import get_settings
from ..db.session import get_db_session
from ..schemas.gps import GPSEvent

router = APIRouter()
logger = logging.getLogger(__name__)

settings = get_settings()
gps_adapter = GPSAdapter(
    batch_size=settings.gps_batch_size, batch_timeout=settings.gps_batch_timeout
)


@router.post("/gps/events", status_code=status.HTTP_202_ACCEPTED)
async def receive_gps_event(
    event: GPSEvent, session: AsyncSession = Depends(get_db_session)
) -> dict[str, Any]:
    """
    Webhook endpoint to receive GPS telemetry events.
    Events are validated, batched, and persisted to the database.
    """
    try:
        logger.info(f"Received GPS event for fleet {event.fleet_number}")
        result = await gps_adapter.add_event(event, session)
        return {
            "message": "GPS event received",
            "batch_status": result["status"],
            "batch_count": result["count"],
        }
    except Exception as e:
        logger.error(f"Error processing GPS event: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process GPS event",
        )


@router.post("/gps/events/batch", status_code=status.HTTP_202_ACCEPTED)
async def receive_gps_events_batch(
    events: list[GPSEvent], session: AsyncSession = Depends(get_db_session)
) -> dict[str, Any]:
    """
    Webhook endpoint to receive multiple GPS telemetry events in a single request.
    """
    if not events:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Event list cannot be empty"
        )

    try:
        logger.info(f"Received batch of {len(events)} GPS events")
        results = []
        for event in events:
            result = await gps_adapter.add_event(event, session)
            results.append(result)

        return {
            "message": f"Batch of {len(events)} GPS events received",
            "processed": len(results),
        }
    except Exception as e:
        logger.error(f"Error processing GPS event batch: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process GPS event batch",
        )
