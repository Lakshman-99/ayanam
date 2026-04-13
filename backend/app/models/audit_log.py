from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class AuditLog(Base):
    """
    Immutable audit log for all write operations.
    No updated_at — audit rows are never modified.

    action examples: "user.login", "user.logout", "chart.created",
                     "chart.deleted", "client.created", "settings.updated"
    """

    __tablename__ = "audit_logs"

    # Override Base.updated_at — audit rows are immutable
    # (Base still adds created_at which is what we want)
    updated_at: Mapped[datetime] = mapped_column(  # type: ignore[assignment]
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    tenant_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Dot-namespaced action identifier
    action: Mapped[str] = mapped_column(String(100), nullable=False, index=True)

    # What entity was affected
    resource_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    resource_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)

    # Arbitrary metadata (diff, old/new values, etc.)
    # Column named 'log_metadata' to avoid clash with SQLAlchemy's reserved 'metadata' attribute
    log_metadata: Mapped[dict] = mapped_column(
        "metadata",  # actual DB column name stays 'metadata'
        JSONB,
        server_default="{}",
        nullable=False,
    )

    # Request context
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)
    request_id: Mapped[str | None] = mapped_column(String(36), nullable=True, index=True)

    def __repr__(self) -> str:
        return f"<AuditLog action={self.action!r} tenant={self.tenant_id}>"
