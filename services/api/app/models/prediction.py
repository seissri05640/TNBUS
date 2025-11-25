from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Float, ForeignKey, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from .route import Route
    from .traffic_snapshot import TrafficSnapshot


class Prediction(TimestampMixin, Base):
    __tablename__ = "predictions"
    __table_args__ = (Index("ix_predictions_route_target", "route_id", "target_arrival"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    route_id: Mapped[int] = mapped_column(ForeignKey("routes.id", ondelete="CASCADE"), nullable=False)
    traffic_snapshot_id: Mapped[int | None] = mapped_column(
        ForeignKey("traffic_snapshots.id", ondelete="SET NULL"), nullable=True
    )
    target_arrival: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    estimated_headway_minutes: Mapped[int | None] = mapped_column(Integer)
    travel_time_minutes: Mapped[int | None] = mapped_column(Integer)
    confidence: Mapped[float | None] = mapped_column(Float)
    notes: Mapped[str | None] = mapped_column(String(512))

    route: Mapped["Route"] = relationship("Route", back_populates="predictions")
    traffic_snapshot: Mapped["TrafficSnapshot" | None] = relationship(
        "TrafficSnapshot", back_populates="predictions"
    )
