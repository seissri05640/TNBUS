from fastapi import FastAPI

from .core.config import get_settings
from .core.logging import configure_logging
from .db.session import get_engine
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
    register_event_handlers(app)
    return app


def register_event_handlers(app: FastAPI) -> None:
    """Attach lifecycle hooks for shared resources such as the database engine."""

    @app.on_event("startup")
    async def _startup() -> None:
        # Ensure the async engine is instantiated on application boot.
        get_engine()

    @app.on_event("shutdown")
    async def _shutdown() -> None:
        engine = get_engine()
        await engine.dispose()


app = create_app()
