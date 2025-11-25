from celery import Celery
from celery.schedules import crontab

from app.core.config import get_settings

settings = get_settings()

celery_app = Celery(
    "traffic_ingestion",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=["app.tasks.traffic_poller"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

celery_app.conf.beat_schedule = {
    "poll-traffic-api": {
        "task": "app.tasks.traffic_poller.poll_traffic_api",
        "schedule": settings.traffic_poll_interval,
        "options": {"expires": settings.traffic_poll_interval * 2},
    },
}
