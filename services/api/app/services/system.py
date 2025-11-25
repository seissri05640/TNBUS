from __future__ import annotations

from datetime import datetime, timezone

from ..core.config import get_settings


class SystemService:
    """Provide system-level diagnostics and metadata."""

    def __init__(self) -> None:
        self._boot_time = datetime.now(timezone.utc)

    def health_status(self) -> dict[str, int | str]:
        settings = get_settings()
        uptime = datetime.now(timezone.utc) - self._boot_time
        return {
            "status": "ok",
            "environment": settings.environment,
            "uptime_seconds": int(uptime.total_seconds()),
        }

    def version_info(self) -> dict[str, str]:
        settings = get_settings()
        return {
            "name": settings.app_name,
            "version": settings.version,
        }
