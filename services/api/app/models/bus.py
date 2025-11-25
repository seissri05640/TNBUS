from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum as SqlEnum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from .route import Route
    from .telemetry import TelemetryRecord


class BusStatus(str, Enum):
    IN_SERVICE = "in_service"
    MAINTENANCE = "maintenance"
    OUT_OF_SERVICE = "out_of_service"


class Bus(TimestampMixin, Base):
    __tablename__ = "buses"

    id: Mapped[int] = mapped_column(primary_key=True)
    fleet_number: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)
    route_id: Mapped[int] = mapped_column(
        ForeignKey("routes.id", ondelete="CASCADE"), nullable=False, index=True
    )
    capacity: Mapped[int] = mapped_column(Integer, nullable=False, server_default="40", default=40)
    status: Mapped[BusStatus] = mapped_column(
        SqlEnum(BusStatus, name="bus_status"),
        nullable=False,
        default=BusStatus.IN_SERVICE,
        server_default=BusStatus.IN_SERVICE.value,
    )
    last_service_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    route: Mapped["Route"] = relationship("Route", back_populates="buses")
    telemetry_records: Mapped[list["TelemetryRecord"]] = relationship(
        "TelemetryRecord", back_populates="bus", cascade="all, delete-orphan"
    )
