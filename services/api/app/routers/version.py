from fastapi import APIRouter, status

from ..schemas.version import VersionResponse
from ..services.system import SystemService

router = APIRouter(tags=["system"])
_system_service = SystemService()


@router.get("/version", response_model=VersionResponse, status_code=status.HTTP_200_OK)
def read_version() -> VersionResponse:
    """Return API version metadata."""

    return VersionResponse(**_system_service.version_info())
