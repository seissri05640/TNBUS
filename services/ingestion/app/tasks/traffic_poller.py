import asyncio
import logging

from celeryconfig import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(name="app.tasks.traffic_poller.poll_traffic_api")
def poll_traffic_api():
    """
    Celery task to periodically poll the external traffic API
    and persist the data to the database.
    """
    logger.info("Starting traffic API polling task")

    try:
        asyncio.run(_poll_traffic_api_async())
        logger.info("Traffic API polling task completed successfully")
        return {"status": "success"}
    except Exception as e:
        logger.error(f"Error in traffic API polling task: {e}")
        return {"status": "error", "message": str(e)}


async def _poll_traffic_api_async():
    """Async implementation of the traffic API polling logic."""
    from ..adapters.traffic_adapter import TrafficAPIAdapter
    from ..db.session import get_sessionmaker
    from ..services.persistence import persist_traffic_data

    adapter = TrafficAPIAdapter()
    traffic_data = await adapter.fetch_traffic_data()

    if traffic_data:
        session_factory = get_sessionmaker()
        async with session_factory() as session:
            await persist_traffic_data(traffic_data, session)
        logger.info("Successfully polled and persisted traffic data")
    else:
        logger.warning("No traffic data received from API")
