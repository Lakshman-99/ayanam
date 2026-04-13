from __future__ import annotations

import json
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import Settings
from app.core.exceptions import ChartCalculationError, NotFoundError, QuotaExceededError
from app.engine.calculator import ChartResult, calculate_natal_chart, calculate_horary_chart
from app.models.chart import Chart
from app.models.subscription import Subscription
from app.models.user import User
from app.schemas.chart import ChartCreateRequest, HoraryChartRequest


class ChartService:
    def __init__(self, db: AsyncSession, settings: Settings) -> None:
        self.db = db
        self.settings = settings

    # -------------------------------------------------------------------------
    # Create
    # -------------------------------------------------------------------------

    async def create_natal_chart(
        self, data: ChartCreateRequest, user: User
    ) -> Chart:
        """
        Full pipeline: quota check → calculate → persist → audit.
        """
        await self._check_quota(user.tenant_id)

        # Run the KP engine
        result = await calculate_natal_chart(
            birth_date=data.birth_date,
            birth_time_str=data.birth_time.strftime("%H:%M:%S"),
            birth_tz=data.birth_tz,
            latitude=data.birth_lat,
            longitude=data.birth_lon,
        )

        chart = Chart(
            tenant_id=user.tenant_id,
            created_by_id=user.id,
            client_id=data.client_id,
            chart_type="natal",
            birth_name=data.birth_name,
            birth_date=data.birth_date,
            birth_time=data.birth_time,
            birth_tz=data.birth_tz,
            birth_lat=data.birth_lat,
            birth_lon=data.birth_lon,
            birth_location_name=data.birth_location_name,
            ayanamsa=data.ayanamsa,
            house_system=data.house_system,
            chart_data=self._result_to_dict(result),
            engine_version=result.engine_version,
            calculated_at=datetime.now(tz=timezone.utc),
        )

        self.db.add(chart)
        await self.db.flush()  # get chart.id before commit

        await self._increment_usage(user.tenant_id)
        await self._write_audit(user, "chart.created", "chart", chart.id)

        return chart

    async def create_horary_chart(
        self, data: HoraryChartRequest, user: User
    ) -> Chart:
        await self._check_quota(user.tenant_id)

        result = await calculate_horary_chart(
            horary_number=data.horary_number,
            latitude=data.birth_lat,
            longitude=data.birth_lon,
        )

        from datetime import date, time as dtime
        today = datetime.now(tz=timezone.utc)

        chart = Chart(
            tenant_id=user.tenant_id,
            created_by_id=user.id,
            chart_type="horary",
            birth_name=f"Horary #{data.horary_number}",
            horary_number=data.horary_number,
            birth_date=today.date(),
            birth_time=today.time(),
            birth_tz="UTC",
            birth_lat=data.birth_lat,
            birth_lon=data.birth_lon,
            birth_location_name=data.birth_location_name,
            ayanamsa="KP",
            house_system="Placidus",
            chart_data=self._result_to_dict(result),
            engine_version=result.engine_version,
            calculated_at=today,
        )

        self.db.add(chart)
        await self.db.flush()
        await self._increment_usage(user.tenant_id)
        await self._write_audit(user, "chart.created", "chart", chart.id)

        return chart

    # -------------------------------------------------------------------------
    # Read
    # -------------------------------------------------------------------------

    async def get_chart(self, chart_id: UUID, tenant_id: UUID) -> Chart:
        """Fetch a chart, enforcing tenant isolation."""
        stmt = select(Chart).where(
            Chart.id == chart_id,
            Chart.tenant_id == tenant_id,
            Chart.is_deleted.is_(False),
        )
        result = await self.db.execute(stmt)
        chart = result.scalar_one_or_none()
        if not chart:
            raise NotFoundError("Chart", chart_id)
        return chart

    async def list_charts(
        self,
        tenant_id: UUID,
        page: int = 1,
        page_size: int = 20,
        client_id: UUID | None = None,
    ) -> tuple[list[Chart], int]:
        """Return (items, total_count) for the tenant, optionally filtered by client."""
        base_filter = [
            Chart.tenant_id == tenant_id,
            Chart.is_deleted.is_(False),
        ]
        if client_id:
            base_filter.append(Chart.client_id == client_id)

        count_stmt = select(func.count()).select_from(Chart).where(*base_filter)
        total = (await self.db.execute(count_stmt)).scalar_one()

        stmt = (
            select(Chart)
            .where(*base_filter)
            .order_by(Chart.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        items = list((await self.db.execute(stmt)).scalars().all())

        return items, total

    # -------------------------------------------------------------------------
    # Delete (soft)
    # -------------------------------------------------------------------------

    async def delete_chart(self, chart_id: UUID, user: User) -> None:
        chart = await self.get_chart(chart_id, user.tenant_id)
        chart.is_deleted = True
        await self._write_audit(user, "chart.deleted", "chart", chart_id)

    # -------------------------------------------------------------------------
    # Private helpers
    # -------------------------------------------------------------------------

    async def _check_quota(self, tenant_id: UUID) -> None:
        """Raise QuotaExceededError if the tenant has hit their monthly chart limit."""
        stmt = (
            select(Subscription)
            .where(
                Subscription.tenant_id == tenant_id,
                Subscription.status == "active",
            )
            .order_by(Subscription.created_at.desc())
            .limit(1)
        )
        result = await self.db.execute(stmt)
        sub = result.scalar_one_or_none()

        if sub is None:
            # No subscription = free tier
            return

        # -1 = unlimited
        if sub.plan and sub.plan.max_charts_per_month != -1:
            if sub.charts_used_this_period >= sub.plan.max_charts_per_month:
                raise QuotaExceededError("charts")

    async def _increment_usage(self, tenant_id: UUID) -> None:
        """Increment the chart usage counter on the active subscription."""
        from sqlalchemy import update
        await self.db.execute(
            update(Subscription)
            .where(
                Subscription.tenant_id == tenant_id,
                Subscription.status == "active",
            )
            .values(charts_used_this_period=Subscription.charts_used_this_period + 1)
        )

    async def _write_audit(
        self,
        user: User,
        action: str,
        resource_type: str,
        resource_id: UUID,
    ) -> None:
        from app.models.audit_log import AuditLog
        log_entry = AuditLog(
            tenant_id=user.tenant_id,
            user_id=user.id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
        )
        self.db.add(log_entry)

    @staticmethod
    def _result_to_dict(result: ChartResult) -> dict:
        """Convert ChartResult dataclass to plain dict for JSONB storage."""
        import dataclasses
        return dataclasses.asdict(result)
