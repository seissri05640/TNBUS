"""Initial database schema for routes, buses, telemetry, traffic snapshots, and predictions."""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "20241125_0001"
down_revision = None
branch_labels = None
depends_on = None

BUS_STATUS = sa.Enum("in_service", "maintenance", "out_of_service", name="bus_status")


def upgrade() -> None:
    BUS_STATUS.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "routes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(length=16), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("origin", sa.String(length=255), nullable=False),
        sa.Column("destination", sa.String(length=255), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
    )

    op.create_table(
        "buses",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("fleet_number", sa.String(length=32), nullable=False),
        sa.Column("route_id", sa.Integer(), nullable=False),
        sa.Column("capacity", sa.Integer(), server_default="40", nullable=False),
        sa.Column("status", BUS_STATUS, server_default="in_service", nullable=False),
        sa.Column("last_service_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["route_id"], ["routes.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("fleet_number"),
    )
    op.create_index("ix_buses_route_id", "buses", ["route_id"], unique=False)

    op.create_table(
        "traffic_snapshots",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("source", sa.String(length=64), nullable=False),
        sa.Column("captured_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("congestion_index", sa.Integer(), nullable=False),
        sa.Column("incident_count", sa.Integer(), nullable=False),
        sa.Column("average_speed_kph", sa.Float(), nullable=True),
        sa.Column("payload", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_traffic_snapshots_captured_at", "traffic_snapshots", ["captured_at"], unique=False)

    op.create_table(
        "telemetry_records",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("bus_id", sa.Integer(), nullable=False),
        sa.Column("recorded_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("latitude", sa.Float(), nullable=False),
        sa.Column("longitude", sa.Float(), nullable=False),
        sa.Column("speed_kph", sa.Float(), nullable=True),
        sa.Column("heading", sa.Integer(), nullable=True),
        sa.Column("passenger_load", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["bus_id"], ["buses.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("bus_id", "recorded_at", name="uq_telemetry_bus_recorded_at"),
    )
    op.create_index(
        "ix_telemetry_bus_recorded_at",
        "telemetry_records",
        ["bus_id", "recorded_at"],
        unique=False,
    )

    op.create_table(
        "predictions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("route_id", sa.Integer(), nullable=False),
        sa.Column("traffic_snapshot_id", sa.Integer(), nullable=True),
        sa.Column("target_arrival", sa.DateTime(timezone=True), nullable=False),
        sa.Column("estimated_headway_minutes", sa.Integer(), nullable=True),
        sa.Column("travel_time_minutes", sa.Integer(), nullable=True),
        sa.Column("confidence", sa.Float(), nullable=True),
        sa.Column("notes", sa.String(length=512), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["route_id"], ["routes.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["traffic_snapshot_id"], ["traffic_snapshots.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_predictions_route_target",
        "predictions",
        ["route_id", "target_arrival"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_predictions_route_target", table_name="predictions")
    op.drop_table("predictions")

    op.drop_index("ix_telemetry_bus_recorded_at", table_name="telemetry_records")
    op.drop_table("telemetry_records")

    op.drop_index("ix_traffic_snapshots_captured_at", table_name="traffic_snapshots")
    op.drop_table("traffic_snapshots")

    op.drop_index("ix_buses_route_id", table_name="buses")
    op.drop_table("buses")

    op.drop_table("routes")

    BUS_STATUS.drop(op.get_bind(), checkfirst=True)
