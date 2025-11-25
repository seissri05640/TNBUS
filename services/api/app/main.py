from fastapi import FastAPI

from .core.config import get_settings
from .core.logging import configure_logging
from .routers import register_routers


def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging(settings.log_level)

    app = FastAPI(
        title=settings.app_name,
        version=settings.version,
        debug=settings.debug,
        docs_url="/docs" if settings.environment != "production" else None,
        redoc_url="/redoc" if settings.environment != "production" else None,
    )

    register_routers(app)
    return app


app = create_app()
