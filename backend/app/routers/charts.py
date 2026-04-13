from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Query

from app.dependencies import AppSettings, CurrentUser, DbSession
from app.schemas.chart import (
    ChartCreateRequest,
    ChartListItem,
    ChartOut,
    HoraryChartRequest,
)
from app.schemas.common import PaginatedResponse, PaginationParams
from app.services.chart_service import ChartService

router = APIRouter(prefix="/charts", tags=["Charts"])


@router.post("/natal", response_model=ChartOut, status_code=201)
async def create_natal_chart(
    body: ChartCreateRequest,
    user: CurrentUser,
    db: DbSession,
    settings: AppSettings,
) -> ChartOut:
    """Generate a KP natal chart. Stores full chart data as JSONB."""
    service = ChartService(db, settings)
    chart = await service.create_natal_chart(body, user)
    return chart


@router.post("/horary", response_model=ChartOut, status_code=201)
async def create_horary_chart(
    body: HoraryChartRequest,
    user: CurrentUser,
    db: DbSession,
    settings: AppSettings,
) -> ChartOut:
    """Generate a KP horary chart from a number (1–249)."""
    service = ChartService(db, settings)
    chart = await service.create_horary_chart(body, user)
    return chart


@router.get("", response_model=PaginatedResponse[ChartListItem])
async def list_charts(
    user: CurrentUser,
    db: DbSession,
    settings: AppSettings,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    client_id: UUID | None = Query(None),
) -> PaginatedResponse[ChartListItem]:
    """List all charts for the current tenant (paginated)."""
    service = ChartService(db, settings)
    charts, total = await service.list_charts(
        tenant_id=user.tenant_id,
        page=page,
        page_size=page_size,
        client_id=client_id,
    )
    params = PaginationParams(page=page, page_size=page_size)
    return PaginatedResponse.create(items=charts, total=total, params=params)


@router.get("/{chart_id}", response_model=ChartOut)
async def get_chart(
    chart_id: UUID,
    user: CurrentUser,
    db: DbSession,
    settings: AppSettings,
) -> ChartOut:
    """Retrieve a specific chart by ID."""
    service = ChartService(db, settings)
    return await service.get_chart(chart_id, user.tenant_id)


@router.delete("/{chart_id}", status_code=204)
async def delete_chart(
    chart_id: UUID,
    user: CurrentUser,
    db: DbSession,
    settings: AppSettings,
) -> None:
    """Soft-delete a chart."""
    service = ChartService(db, settings)
    await service.delete_chart(chart_id, user)
