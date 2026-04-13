from __future__ import annotations

from datetime import date, datetime, time
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ChartCreateRequest(BaseModel):
    """Request body for creating a natal chart."""

    birth_name: str = Field(min_length=1, max_length=255)
    birth_date: date
    birth_time: time
    birth_tz: str = Field(description="IANA timezone string, e.g. 'Asia/Kolkata'")
    birth_lat: float = Field(ge=-90.0, le=90.0, description="Latitude in decimal degrees")
    birth_lon: float = Field(ge=-180.0, le=180.0, description="Longitude in decimal degrees")
    birth_location_name: str | None = Field(None, max_length=255)

    # Optional: link to existing client record
    client_id: UUID | None = None

    # Chart settings (defaults to KP standard)
    ayanamsa: str = Field("KP", description="Ayanamsa: KP | Lahiri | Raman")
    house_system: str = Field("Placidus", description="House system: Placidus | Koch | Equal")

    @field_validator("birth_tz")
    @classmethod
    def validate_timezone(cls, v: str) -> str:
        try:
            from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
            ZoneInfo(v)
        except (KeyError, Exception):
            raise ValueError(f"Unknown or invalid timezone: '{v}'")
        return v

    @field_validator("birth_date")
    @classmethod
    def validate_birth_date(cls, v: date) -> date:
        from datetime import date as dt_date
        if v.year < 1800 or v.year > 2100:
            raise ValueError("Birth date must be between 1800 and 2100")
        return v


class HoraryChartRequest(BaseModel):
    """Request body for a KP horary chart."""

    horary_number: int = Field(ge=1, le=249, description="KP horary number (1-249)")
    birth_lat: float = Field(ge=-90.0, le=90.0)
    birth_lon: float = Field(ge=-180.0, le=180.0)
    birth_location_name: str | None = None
    query_note: str | None = Field(None, max_length=500, description="The question being asked")


class ChartOut(BaseModel):
    """Chart response — includes full computed data."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    chart_type: str
    birth_name: str
    birth_date: date
    birth_time: time
    birth_tz: str
    birth_lat: float
    birth_lon: float
    birth_location_name: str | None
    ayanamsa: str
    house_system: str

    # Full computed chart data (the JSONB blob)
    chart_data: dict | None

    engine_version: str | None
    calculated_at: datetime | None
    created_at: datetime
    client_id: UUID | None


class ChartListItem(BaseModel):
    """Lightweight chart summary for list views."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    chart_type: str
    birth_name: str
    birth_date: date
    birth_location_name: str | None
    calculated_at: datetime | None
    created_at: datetime
    client_id: UUID | None
