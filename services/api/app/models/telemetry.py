from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Float, ForeignKey, Index, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..db.base import Base

if TYPE_CHECKING:
    from .bus import Bus


class TelemetryRecord(Base):
    __tablename__ = "telemetry_records"
    __table_args__ = (
        UniqueConstraint("bus_id", "recorded_at", name="uq_telemetry_bus_recorded_at"),
        Index("ix_telemetry_bus_recorded_at", "bus_id", "recorded_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    bus_id: Mapped[int] = mapped_column(ForeignKey("buses.id", ondelete="CASCADE"), nullable=False)
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    speed_kph: Mapped[float | None] = mapped_column(Float)
    heading: Mapped[int | None] = mapped_column(Integer)
    passenger_load: Mapped[int | None] = mapped_column(Integer)

    bus: Mapped["Bus"] = relationship("Bus", back_populates="telemetry_records")
