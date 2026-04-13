from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.subscription import Subscription


class Tenant(Base):
    __tablename__ = "tenants"

    # URL-safe slug — used as subdomain (e.g. "astrojohn" → astrojohn.domain.com)
    slug: Mapped[str] = mapped_column(String(63), unique=True, index=True, nullable=False)

    # Human-readable name for branding
    display_name: Mapped[str] = mapped_column(String(255), nullable=False)

    # Optional custom domain (Phase 2 — white-label)
    custom_domain: Mapped[str | None] = mapped_column(String(253), unique=True, nullable=True)

    # Branding
    logo_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    tagline: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Per-tenant settings: language, default_ayanamsa, default_house_system, theme, etc.
    settings: Mapped[dict] = mapped_column(JSONB, server_default="{}", nullable=False)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    users: Mapped[list[User]] = relationship("User", back_populates="tenant")
    subscriptions: Mapped[list[Subscription]] = relationship("Subscription", back_populates="tenant")

    def __repr__(self) -> str:
        return f"<Tenant slug={self.slug!r}>"
