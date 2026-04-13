from __future__ import annotations

import uuid
from datetime import date, datetime, time
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Date, DateTime, Float, ForeignKey, String, Time
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TenantMixin

if TYPE_CHECKING:
    from app.models.client import Client
    from app.models.user import User


class Chart(Base, TenantMixin):
    """
    A KP astrological chart. The full computation result is stored as JSONB
    so we never recalculate — computed once, served forever.

    chart_type values: "natal", "horary", "prashna", "transit", "rectification"
    """

    __tablename__ = "charts"

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    client_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("clients.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    created_by_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # -------------------------------------------------------------------------
    # Chart type and metadata
    # -------------------------------------------------------------------------
    chart_type: Mapped[str] = mapped_column(String(20), default="natal", nullable=False)

    # Subject name (may differ from client.name for family members etc.)
    birth_name: Mapped[str] = mapped_column(String(255), nullable=False)

    # For horary charts: the querent's number (1-249)
    horary_number: Mapped[int | None] = mapped_column(nullable=True)

    # -------------------------------------------------------------------------
    # Birth data (immutable after creation)
    # -------------------------------------------------------------------------
    birth_date: Mapped[date] = mapped_column(Date, nullable=False)
    birth_time: Mapped[time] = mapped_column(Time, nullable=False)
    birth_tz: Mapped[str] = mapped_column(String(64), nullable=False)  # IANA tz e.g. "Asia/Kolkata"

    birth_lat: Mapped[float] = mapped_column(Float, nullable=False)
    birth_lon: Mapped[float] = mapped_column(Float, nullable=False)
    birth_location_name: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # -------------------------------------------------------------------------
    # Calculation settings
    # -------------------------------------------------------------------------
    ayanamsa: Mapped[str] = mapped_column(String(30), default="KP", nullable=False)
    house_system: Mapped[str] = mapped_column(String(20), default="Placidus", nullable=False)

    # -------------------------------------------------------------------------
    # Computed output (JSONB — denormalized for O(1) retrieval)
    # Structured per the chart_data spec in the architecture document.
    # -------------------------------------------------------------------------
    chart_data: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # Engine version that produced this chart — used for cache invalidation
    # and to know which charts need recalculation after engine upgrades
    engine_version: Mapped[str | None] = mapped_column(String(20), nullable=True)
    calculated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Soft delete
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # PDF report (Phase 3)
    pdf_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)

    # -------------------------------------------------------------------------
    # Relationships
    # -------------------------------------------------------------------------
    client: Mapped[Client | None] = relationship("Client", back_populates="charts")
    created_by: Mapped[User | None] = relationship("User")

    def __repr__(self) -> str:
        return f"<Chart name={self.birth_name!r} type={self.chart_type} tenant={self.tenant_id}>"
