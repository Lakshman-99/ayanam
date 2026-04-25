from __future__ import annotations

import enum
import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TenantMixin

if TYPE_CHECKING:
    from app.models.tenant import Tenant


class PlanTier(str, enum.Enum):
    FREE = "free"
    STARTER = "starter"
    PRO = "pro"
    ENTERPRISE = "enterprise"


class Plan(Base):
    """
    SaaS subscription plans. Seeded once — not tenant-scoped.
    features JSONB holds feature flags, e.g.:
    {"horary": true, "matching": true, "bulk_import": false, "api_access": false}
    """

    __tablename__ = "plans"

    tier: Mapped[PlanTier] = mapped_column(
        Enum(
            PlanTier,
            native_enum=False,
            values_callable=lambda x: [e.value for e in x],
        ),
        unique=True,
        nullable=False,
    )
    display_name: Mapped[str] = mapped_column(String(100), nullable=False)

    # Prices in smallest currency unit (paise for INR, cents for USD)
    price_monthly_paise: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    price_yearly_paise: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # -1 = unlimited
    max_charts_per_month: Mapped[int] = mapped_column(Integer, default=50, nullable=False)
    max_clients: Mapped[int] = mapped_column(Integer, default=100, nullable=False)
    max_users: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    features: Mapped[dict] = mapped_column(JSONB, server_default="{}", nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)

    # Relationships
    subscriptions: Mapped[list[Subscription]] = relationship("Subscription", back_populates="plan")

    def __repr__(self) -> str:
        return f"<Plan tier={self.tier}>"


class Subscription(Base, TenantMixin):
    """Active subscription for a tenant."""

    __tablename__ = "subscriptions"

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    plan_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("plans.id"),
        nullable=False,
    )

    # status: active | trialing | past_due | cancelled | unpaid
    status: Mapped[str] = mapped_column(String(20), default="active", nullable=False)

    current_period_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    current_period_end: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    # Usage counter — reset monthly by Celery Beat task
    charts_used_this_period: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Payment provider subscription IDs (Phase 3)
    razorpay_subscription_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    stripe_subscription_id: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Relationships
    tenant: Mapped[Tenant] = relationship("Tenant", back_populates="subscriptions")
    plan: Mapped[Plan] = relationship("Plan", back_populates="subscriptions")

    def __repr__(self) -> str:
        return f"<Subscription tenant={self.tenant_id} plan={self.plan_id} status={self.status}>"
