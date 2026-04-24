from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import UUID

import structlog
from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import Settings
from app.core.exceptions import (
    AuthenticationError,
    ConflictError,
    RefreshTokenRevokedError,
    TenantSlugTakenError,
)
from app.core.security import (
    create_access_token,
    create_refresh_token,
    hash_jti,
    hash_password,
    verify_password,
)
from app.dependencies import AppSettings, CurrentUser, DbSession, get_db, get_settings
from app.models.subscription import Plan, PlanTier, Subscription
from app.models.tenant import Tenant
from app.models.user import RefreshToken, User, UserRole
from app.schemas.auth import (
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
    UpdateProfileRequest,
    UserOut,
)

log = structlog.get_logger()
router = APIRouter(prefix="/auth", tags=["Authentication"])
REFRESH_COOKIE_NAME = "refresh_token"


def _make_token_response(
    user: User,
    settings: Settings,
    request: Request | None = None,
) -> tuple[TokenResponse, str, str]:
    """
    Create access + refresh tokens.
    Returns (TokenResponse, signed_refresh_token, jti).
    """
    access_token = create_access_token(
        user_id=user.id,
        tenant_id=user.tenant_id,
        role=user.role.value,
        private_key=settings.jwt_private_key,
        algorithm=settings.jwt_algorithm,
        expire_minutes=settings.jwt_access_token_expire_minutes,
    )
    refresh_token_str, jti = create_refresh_token(
        user_id=user.id,
        tenant_id=user.tenant_id,
        role=user.role.value,
        private_key=settings.jwt_private_key,
        algorithm=settings.jwt_algorithm,
        expire_days=settings.jwt_refresh_token_expire_days,
    )

    response = TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token_str,
        token_type="bearer",
        expires_in=settings.jwt_access_token_expire_minutes * 60,
    )
    return response, refresh_token_str, jti


async def _store_refresh_token(
    db: AsyncSession,
    user: User,
    jti: str,
    settings: Settings,
    request: Request | None = None,
) -> None:
    """Persist a new refresh token record to the DB."""
    expires_at = datetime.now(tz=timezone.utc) + timedelta(
        days=settings.jwt_refresh_token_expire_days
    )
    rt = RefreshToken(
        user_id=user.id,
        jti_hash=hash_jti(jti),
        expires_at=expires_at,
        user_agent=request.headers.get("user-agent") if request else None,
        ip_address=request.client.host if request and request.client else None,
    )
    db.add(rt)


def _set_refresh_cookie(response: Response, refresh_token: str, settings: Settings) -> None:
    response.set_cookie(
        key=REFRESH_COOKIE_NAME,
        value=refresh_token,
        httponly=True,
        secure=settings.is_production,
        samesite="strict",
        max_age=settings.jwt_refresh_token_expire_days * 24 * 60 * 60,
        path="/",
    )


def _get_refresh_token(request: Request, body: RefreshRequest | None) -> str:
    if body and body.refresh_token:
        return body.refresh_token

    cookie_token = request.cookies.get(REFRESH_COOKIE_NAME)
    if cookie_token:
        return cookie_token

    raise AuthenticationError("Refresh token missing")


# =============================================================================
# Endpoints
# =============================================================================

@router.post("/register", response_model=TokenResponse, status_code=201)
async def register(
    body: RegisterRequest,
    request: Request,
    response: Response,
    db: DbSession,
    settings: AppSettings,
) -> TokenResponse:
    """
    Register a new tenant + owner user.
    Creates: Tenant → User (role=tenant_admin) → free Subscription → tokens.
    """
    # Check slug uniqueness
    existing = await db.scalar(select(Tenant).where(Tenant.slug == body.tenant_slug))
    if existing:
        raise TenantSlugTakenError(body.tenant_slug)

    # Check email uniqueness within tenant (can't exist yet since tenant is new,
    # but guard against race conditions)
    tenant = Tenant(
        slug=body.tenant_slug,
        display_name=body.tenant_display_name,
        settings={},
    )
    db.add(tenant)
    await db.flush()  # populate tenant.id

    user = User(
        tenant_id=tenant.id,
        email=body.email.lower(),
        password_hash=hash_password(body.password),
        full_name=body.full_name,
        role=UserRole.TENANT_ADMIN,
    )
    db.add(user)
    await db.flush()  # populate user.id

    # Provision free subscription
    free_plan = await db.scalar(select(Plan).where(Plan.tier == PlanTier.FREE))
    if free_plan:
        now = datetime.now(tz=timezone.utc)
        sub = Subscription(
            tenant_id=tenant.id,
            plan_id=free_plan.id,
            status="active",
            current_period_start=now,
            current_period_end=now + timedelta(days=30),
        )
        db.add(sub)

    token_response, refresh_token_str, jti = _make_token_response(
        user, settings, request
    )
    await _store_refresh_token(db, user, jti, settings, request)
    _set_refresh_cookie(response, refresh_token_str, settings)

    log.info("tenant_registered", tenant_slug=body.tenant_slug, user_email=body.email)
    return token_response


@router.post("/login", response_model=TokenResponse)
async def login(
    body: LoginRequest,
    request: Request,
    response: Response,
    db: DbSession,
    settings: AppSettings,
) -> TokenResponse:
    """Authenticate with email + password. Returns token pair."""
    # Find user by email (case-insensitive) — must check across tenants
    # In real usage, tenant slug from header or subdomain narrows this
    stmt = select(User).where(
        User.email == body.email.lower(),
        User.is_active.is_(True),
    )
    # If tenant slug is in header, scope to it
    tenant_slug = getattr(request.state, "tenant_slug", None)
    if tenant_slug:
        stmt = stmt.join(Tenant, User.tenant_id == Tenant.id).where(
            Tenant.slug == tenant_slug
        )

    result = await db.execute(stmt.limit(1))
    user = result.scalar_one_or_none()

    if not user or not verify_password(body.password, user.password_hash):
        raise AuthenticationError("Invalid email or password")

    # Update last login
    user.last_login_at = datetime.now(tz=timezone.utc)

    token_response, refresh_token_str, jti = _make_token_response(
        user, settings, request
    )
    await _store_refresh_token(db, user, jti, settings, request)
    _set_refresh_cookie(response, refresh_token_str, settings)

    log.info("user_login", user_id=str(user.id), tenant_id=str(user.tenant_id))
    return token_response


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    body: RefreshRequest | None,
    request: Request,
    response: Response,
    db: DbSession,
    settings: AppSettings,
) -> TokenResponse:
    """
    Rotate refresh token — validates old, issues new pair, revokes old.
    Reuse of a revoked refresh token should trigger all sessions to be invalidated.
    """
    from app.core.security import decode_token

    refresh_token = _get_refresh_token(request, body)

    payload = decode_token(
        token=refresh_token,
        public_key=settings.jwt_public_key,
        algorithm=settings.jwt_algorithm,
    )

    if payload.get("type") != "refresh":
        raise AuthenticationError("Invalid token type")

    jti = payload.get("jti")
    if not jti:
        raise AuthenticationError("Token missing JTI")

    jti_hash = hash_jti(jti)

    # Find and validate the stored token
    rt = await db.scalar(select(RefreshToken).where(RefreshToken.jti_hash == jti_hash))
    if not rt:
        raise AuthenticationError("Refresh token not found")

    if rt.is_revoked:
        # Potential token reuse attack — revoke ALL tokens for this user
        log.warning("refresh_token_reuse", user_id=str(rt.user_id))
        from sqlalchemy import update
        await db.execute(
            update(RefreshToken)
            .where(RefreshToken.user_id == rt.user_id, RefreshToken.revoked_at.is_(None))
            .values(revoked_at=datetime.now(tz=timezone.utc))
        )
        raise RefreshTokenRevokedError()

    # Revoke the current token
    rt.revoked_at = datetime.now(tz=timezone.utc)

    # Get the user
    user = await db.get(User, rt.user_id)
    if not user or not user.is_active:
        raise AuthenticationError("User not found or inactive")

    # Issue new pair
    token_response, new_refresh_token, new_jti = _make_token_response(
        user, settings, request
    )
    await _store_refresh_token(db, user, new_jti, settings, request)
    _set_refresh_cookie(response, new_refresh_token, settings)

    return token_response


@router.post("/logout", status_code=204)
async def logout(
    body: RefreshRequest | None,
    request: Request,
    response: Response,
    db: DbSession,
    settings: AppSettings,
) -> None:
    """Revoke a specific refresh token (logout from one device)."""
    from app.core.security import decode_token

    try:
        refresh_token = _get_refresh_token(request, body)
        payload = decode_token(
            token=refresh_token,
            public_key=settings.jwt_public_key,
            algorithm=settings.jwt_algorithm,
        )
        jti = payload.get("jti", "")
        jti_hash = hash_jti(jti)
        rt = await db.scalar(select(RefreshToken).where(RefreshToken.jti_hash == jti_hash))
        if rt and not rt.is_revoked:
            rt.revoked_at = datetime.now(tz=timezone.utc)
    except Exception:
        pass  # Logout should always succeed silently

    response.delete_cookie(REFRESH_COOKIE_NAME, path="/")


@router.get("/me", response_model=UserOut)
async def me(user: CurrentUser) -> User:
    """Return the current authenticated user's profile."""
    return user


@router.put("/me", response_model=UserOut)
async def update_profile(
    body: UpdateProfileRequest,
    user: CurrentUser,
    db: DbSession,
) -> User:
    """Update the current user's profile."""
    if body.full_name is not None:
        user.full_name = body.full_name
    if body.phone is not None:
        user.phone = body.phone
    if body.language is not None:
        user.language = body.language
    return user
