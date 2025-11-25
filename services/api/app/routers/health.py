from fastapi import APIRouter, status

from ..schemas.health import HealthResponse
from ..services.system import SystemService

router = APIRouter(tags=["system"])
_system_service = SystemService()


@router.get("/health", response_model=HealthResponse, status_code=status.HTTP_200_OK)
def read_health() -> HealthResponse:
    """Return service health diagnostics."""

    return HealthResponse(**_system_service.health_status())
