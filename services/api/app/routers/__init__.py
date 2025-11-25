from fastapi import FastAPI

from .health import router as health_router
from .version import router as version_router


def register_routers(app: FastAPI) -> None:
    """Attach all API routers to the FastAPI application."""

    app.include_router(health_router)
    app.include_router(version_router)
