from __future__ import annotations

import uuid
from datetime import date, time
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Date, Float, ForeignKey, String, Text, Time
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TenantMixin

if TYPE_CHECKING:
    from app.models.chart import Chart


class Client(Base, TenantMixin):
    """
    A client (subject) whose charts are managed by the tenant astrologer.
    Stores full birth data so charts can be recalculated on demand.
    """

    __tablename__ = "clients"

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Identity
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    gender: Mapped[str] = mapped_column(String(10), nullable=False, server_default="male")

    # Birth data
    date_of_birth: Mapped[date] = mapped_column(Date, nullable=False)
    time_of_birth: Mapped[time] = mapped_column(Time, nullable=False)
    place_of_birth: Mapped[str] = mapped_column(String(255), nullable=False)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    timezone: Mapped[str] = mapped_column(String(64), nullable=False, server_default="Asia/Kolkata")

    # Computed/cached (populated after natal chart generation)
    lagna_sign: Mapped[str | None] = mapped_column(String(30), nullable=True)
    lagna_degree: Mapped[float | None] = mapped_column(Float, nullable=True)
    current_dasha: Mapped[str | None] = mapped_column(String(100), nullable=True)
    natal_chart_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )

    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relationships
    charts: Mapped[list[Chart]] = relationship("Chart", back_populates="client")

    def __repr__(self) -> str:
        return f"<Client full_name={self.full_name!r} tenant={self.tenant_id}>"
