import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from .core.config import get_settings
from .core.logging import configure_logging
from .routers import gps_router, health_router

configure_logging()
logger = logging.getLogger(__name__)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting {settings.app_name} v{settings.version}")
    logger.info(f"Environment: {settings.environment}")
    yield
    logger.info(f"Shutting down {settings.app_name}")


app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    debug=settings.debug,
    lifespan=lifespan,
)

app.include_router(health_router, tags=["health"])
app.include_router(gps_router, prefix="/api/v1", tags=["gps"])
