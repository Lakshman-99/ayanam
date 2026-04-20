"""Add birth data columns to clients table

Revision ID: 0002
Revises: 0001
Create Date: 2026-04-12 00:00:00.000000

Replaces the minimal clients schema (name/email/phone) with full KP birth
data fields required for chart generation.
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Drop old columns that no longer apply
    op.drop_column("clients", "name")
    op.drop_column("clients", "email")
    op.drop_column("clients", "phone")

    # Add birth identity columns
    op.add_column("clients", sa.Column("full_name", sa.String(255), nullable=False, server_default=""))
    op.add_column("clients", sa.Column("gender", sa.String(10), nullable=False, server_default="male"))

    # Add birth data columns
    op.add_column("clients", sa.Column("date_of_birth", sa.Date(), nullable=False, server_default="2000-01-01"))
    op.add_column("clients", sa.Column("time_of_birth", sa.Time(), nullable=False, server_default="00:00:00"))
    op.add_column("clients", sa.Column("place_of_birth", sa.String(255), nullable=False, server_default=""))
    op.add_column("clients", sa.Column("latitude", sa.Float(), nullable=False, server_default="0.0"))
    op.add_column("clients", sa.Column("longitude", sa.Float(), nullable=False, server_default="0.0"))
    op.add_column("clients", sa.Column("timezone", sa.String(64), nullable=False, server_default="Asia/Kolkata"))

    # Cached computed columns (filled after natal chart generation)
    op.add_column("clients", sa.Column("lagna_sign", sa.String(30), nullable=True))
    op.add_column("clients", sa.Column("lagna_degree", sa.Float(), nullable=True))
    op.add_column("clients", sa.Column("current_dasha", sa.String(100), nullable=True))
    op.add_column("clients", sa.Column("natal_chart_id", postgresql.UUID(as_uuid=True), nullable=True))

    # Remove server defaults once the NOT NULL columns are added
    op.alter_column("clients", "full_name", server_default=None)
    op.alter_column("clients", "date_of_birth", server_default=None)
    op.alter_column("clients", "time_of_birth", server_default=None)
    op.alter_column("clients", "place_of_birth", server_default=None)
    op.alter_column("clients", "latitude", server_default=None)
    op.alter_column("clients", "longitude", server_default=None)


def downgrade() -> None:
    op.drop_column("clients", "natal_chart_id")
    op.drop_column("clients", "current_dasha")
    op.drop_column("clients", "lagna_degree")
    op.drop_column("clients", "lagna_sign")
    op.drop_column("clients", "timezone")
    op.drop_column("clients", "longitude")
    op.drop_column("clients", "latitude")
    op.drop_column("clients", "place_of_birth")
    op.drop_column("clients", "time_of_birth")
    op.drop_column("clients", "date_of_birth")
    op.drop_column("clients", "gender")
    op.drop_column("clients", "full_name")

    op.add_column("clients", sa.Column("name", sa.String(255), nullable=False, server_default=""))
    op.add_column("clients", sa.Column("email", sa.String(320), nullable=True))
    op.add_column("clients", sa.Column("phone", sa.String(30), nullable=True))
    op.alter_column("clients", "name", server_default=None)
