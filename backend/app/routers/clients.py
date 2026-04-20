from __future__ import annotations

from uuid import UUID

import structlog
from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import func, or_, select

from app.dependencies import CurrentUser, DbSession
from app.models.chart import Chart
from app.models.client import Client
from app.schemas.chart import ChartOut
from app.schemas.client import (
    ClientCreate,
    ClientListItem,
    ClientListResponse,
    ClientOut,
    ClientUpdate,
)

log = structlog.get_logger()
router = APIRouter(prefix="/clients", tags=["Clients"])


@router.get("", response_model=ClientListResponse)
async def list_clients(
    user: CurrentUser,
    db: DbSession,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: str | None = Query(None, max_length=200),
    sort_by: str = Query("created_at"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$"),
) -> ClientListResponse:
    """List clients for the current tenant with optional search and sorting."""
    allowed_sort = {
        "full_name", "date_of_birth", "place_of_birth",
        "lagna_sign", "current_dasha", "created_at",
    }
    if sort_by not in allowed_sort:
        sort_by = "created_at"

    stmt = (
        select(Client)
        .where(Client.tenant_id == user.tenant_id, Client.is_deleted.is_(False))
    )

    if search:
        term = f"%{search}%"
        stmt = stmt.where(
            or_(
                Client.full_name.ilike(term),
                Client.place_of_birth.ilike(term),
            )
        )

    # Total count
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total: int = (await db.execute(count_stmt)).scalar_one()

    # Sort
    col = getattr(Client, sort_by)
    stmt = stmt.order_by(col.asc() if sort_order == "asc" else col.desc())

    # Paginate
    stmt = stmt.offset((page - 1) * page_size).limit(page_size)
    rows = (await db.execute(stmt)).scalars().all()

    return ClientListResponse(
        items=[ClientListItem.model_validate(c) for c in rows],
        total=total,
        page=page,
        page_size=page_size,
        has_more=(page * page_size) < total,
    )


@router.post("", response_model=ClientOut, status_code=status.HTTP_201_CREATED)
async def create_client(
    body: ClientCreate,
    user: CurrentUser,
    db: DbSession,
) -> ClientOut:
    """Create a new client record."""
    client = Client(
        tenant_id=user.tenant_id,
        full_name=body.full_name,
        gender=body.gender,
        date_of_birth=body.date_of_birth,
        time_of_birth=body.time_of_birth,
        place_of_birth=body.place_of_birth,
        latitude=body.latitude,
        longitude=body.longitude,
        timezone=body.timezone,
        notes=body.notes,
    )
    db.add(client)
    await db.flush()
    await db.refresh(client)
    log.info("client_created", client_id=str(client.id), tenant_id=str(user.tenant_id))
    return ClientOut.model_validate(client)


@router.get("/{client_id}", response_model=ClientOut)
async def get_client(
    client_id: UUID,
    user: CurrentUser,
    db: DbSession,
) -> ClientOut:
    """Get a single client by ID."""
    client = await _get_or_404(db, client_id, user.tenant_id)
    return ClientOut.model_validate(client)


@router.patch("/{client_id}", response_model=ClientOut)
async def update_client(
    client_id: UUID,
    body: ClientUpdate,
    user: CurrentUser,
    db: DbSession,
) -> ClientOut:
    """Update client fields."""
    client = await _get_or_404(db, client_id, user.tenant_id)
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(client, field, value)
    await db.flush()
    await db.refresh(client)
    return ClientOut.model_validate(client)


@router.delete("/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_client(
    client_id: UUID,
    user: CurrentUser,
    db: DbSession,
) -> None:
    """Soft-delete a client."""
    client = await _get_or_404(db, client_id, user.tenant_id)
    client.is_deleted = True
    await db.flush()
    log.info("client_deleted", client_id=str(client_id), tenant_id=str(user.tenant_id))


@router.get("/{client_id}/chart", response_model=ChartOut)
async def get_client_chart(
    client_id: UUID,
    user: CurrentUser,
    db: DbSession,
) -> ChartOut:
    """Return the most recent natal chart for a client."""
    await _get_or_404(db, client_id, user.tenant_id)  # ensure client exists + tenant check

    stmt = (
        select(Chart)
        .where(
            Chart.client_id == client_id,
            Chart.tenant_id == user.tenant_id,
            Chart.chart_type == "natal",
            Chart.is_deleted.is_(False),
        )
        .order_by(Chart.calculated_at.desc())
        .limit(1)
    )
    chart = (await db.execute(stmt)).scalar_one_or_none()
    if not chart:
        raise HTTPException(status_code=404, detail="No natal chart found for this client")
    return ChartOut.model_validate(chart)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

async def _get_or_404(db: DbSession, client_id: UUID, tenant_id: UUID) -> Client:
    stmt = select(Client).where(
        Client.id == client_id,
        Client.tenant_id == tenant_id,
        Client.is_deleted.is_(False),
    )
    client = (await db.execute(stmt)).scalar_one_or_none()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return client
