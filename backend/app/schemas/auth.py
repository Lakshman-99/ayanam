from __future__ import annotations

import re
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.models.user import UserRole

# Tenant slug: lowercase alphanumeric + hyphens, 3-63 chars
_SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9-]{1,61}[a-z0-9]$")


class RegisterRequest(BaseModel):
    """Register a new tenant + owner user in one step."""

    email: EmailStr
    password: str = Field(min_length=8, max_length=100)
    full_name: str = Field(min_length=1, max_length=255)

    # Tenant details
    tenant_slug: str = Field(
        min_length=3,
        max_length=63,
        description="URL-safe slug for subdomain (e.g. 'astrojohn')",
    )
    tenant_display_name: str = Field(min_length=1, max_length=255)

    @field_validator("tenant_slug")
    @classmethod
    def validate_slug(cls, v: str) -> str:
        v = v.lower().strip()
        if not _SLUG_RE.match(v):
            raise ValueError(
                "Slug must be 3-63 characters, lowercase alphanumeric and hyphens, "
                "cannot start or end with a hyphen"
            )
        # Reserved slugs
        reserved = {"www", "app", "api", "admin", "mail", "static", "assets", "cdn"}
        if v in reserved:
            raise ValueError(f"'{v}' is a reserved slug")
        return v

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        if not any(c.isalpha() for c in v):
            raise ValueError("Password must contain at least one letter")
        return v


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds until access token expiry


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: str
    full_name: str
    role: UserRole
    language: str
    tenant_id: UUID
    is_active: bool
    created_at: datetime


class UpdateProfileRequest(BaseModel):
    full_name: str | None = Field(None, min_length=1, max_length=255)
    phone: str | None = Field(None, max_length=30)
    language: str | None = Field(None, min_length=2, max_length=10)
