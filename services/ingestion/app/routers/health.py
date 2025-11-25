from fastapi import APIRouter

from ..core.config import get_settings

router = APIRouter()


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "ingestion"}


@router.get("/version")
async def version():
    """Return the service version."""
    settings = get_settings()
    return {"version": settings.version, "service": "ingestion"}
