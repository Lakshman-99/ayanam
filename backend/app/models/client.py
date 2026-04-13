from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TenantMixin

if TYPE_CHECKING:
    from app.models.chart import Chart


class Client(Base, TenantMixin):
    """
    A client (subject) whose charts are managed by the tenant astrologer.
    Multiple charts can belong to a single client (natal, horary, etc.)
    """

    __tablename__ = "clients"

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str | None] = mapped_column(String(320), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relationships
    charts: Mapped[list[Chart]] = relationship("Chart", back_populates="client")

    def __repr__(self) -> str:
        return f"<Client name={self.name!r} tenant={self.tenant_id}>"
