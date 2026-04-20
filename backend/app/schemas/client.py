from __future__ import annotations

from datetime import date, datetime, time
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ClientCreate(BaseModel):
    full_name: str = Field(min_length=1, max_length=255)
    gender: str = Field("male", pattern="^(male|female|other)$")
    date_of_birth: date
    time_of_birth: time
    place_of_birth: str = Field(min_length=1, max_length=255)
    latitude: float = Field(ge=-90.0, le=90.0)
    longitude: float = Field(ge=-180.0, le=180.0)
    timezone: str = Field(min_length=1, max_length=64)
    notes: str | None = Field(None, max_length=5000)


class ClientUpdate(BaseModel):
    full_name: str | None = Field(None, min_length=1, max_length=255)
    gender: str | None = Field(None, pattern="^(male|female|other)$")
    date_of_birth: date | None = None
    time_of_birth: time | None = None
    place_of_birth: str | None = Field(None, max_length=255)
    latitude: float | None = Field(None, ge=-90.0, le=90.0)
    longitude: float | None = Field(None, ge=-180.0, le=180.0)
    timezone: str | None = Field(None, max_length=64)
    notes: str | None = Field(None, max_length=5000)


class ClientOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    full_name: str
    gender: str
    date_of_birth: date
    time_of_birth: time
    place_of_birth: str
    latitude: float
    longitude: float
    timezone: str
    lagna_sign: str | None = None
    lagna_degree: float | None = None
    current_dasha: str | None = None
    natal_chart_id: UUID | None = None
    notes: str | None = None
    created_at: datetime
    updated_at: datetime


class ClientListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    full_name: str
    gender: str
    date_of_birth: date
    place_of_birth: str
    lagna_sign: str | None = None
    current_dasha: str | None = None
    natal_chart_id: UUID | None = None
    created_at: datetime


class ClientListResponse(BaseModel):
    items: list[ClientListItem]
    total: int
    page: int
    page_size: int
    has_more: bool
