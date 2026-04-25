from __future__ import annotations

from collections.abc import AsyncGenerator
from typing import Annotated
from uuid import UUID

import redis.asyncio as aioredis
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import Settings, get_settings
from app.core.exceptions import AuthenticationError, AuthorizationError
from app.core.security import decode_token
from app.models.user import User, UserRole

# =============================================================================
# Database
# =============================================================================

def _make_engine(settings: Settings):
    return create_async_engine(
        settings.database_url,
        pool_size=settings.db_pool_size,
        max_overflow=settings.db_max_overflow,
        echo=settings.debug,
        pool_pre_ping=True,
        connect_args={"statement_cache_size": 0},
    )


# Module-level engine and session factory (created once at first use)
_engine = None
_session_factory = None


def get_engine(settings: Settings = None):
    global _engine
    if _engine is None:
        if settings is None:
            settings = get_settings()
        _engine = _make_engine(settings)
    return _engine


def get_session_factory(settings: Settings = None) -> async_sessionmaker:
    global _session_factory
    if _session_factory is None:
        engine = get_engine(settings)
        _session_factory = async_sessionmaker(
            engine, expire_on_commit=False, class_=AsyncSession
        )
    return _session_factory


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency: yields a DB session, commits on success, rolls back on error."""
    factory = get_session_factory()
    async with factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


# =============================================================================
# Redis
# =============================================================================

_redis_pool = None


def get_redis_pool(settings: Settings = None) -> aioredis.ConnectionPool:
    global _redis_pool
    if _redis_pool is None:
        if settings is None:
            settings = get_settings()
        _redis_pool = aioredis.ConnectionPool.from_url(
            settings.redis_url, decode_responses=True
        )
    return _redis_pool


async def get_redis() -> aioredis.Redis:
    """FastAPI dependency: returns a Redis client from the connection pool."""
    pool = get_redis_pool()
    return aioredis.Redis(connection_pool=pool)


# =============================================================================
# Auth
# =============================================================================

_bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> User:
    """Validate JWT and return the authenticated User."""
    if not credentials:
        raise AuthenticationError("Missing authentication token")

    payload = decode_token(
        token=credentials.credentials,
        public_key=settings.jwt_public_key,
        algorithm=settings.jwt_algorithm,
    )

    if payload.get("type") != "access":
        raise AuthenticationError("Invalid token type — use access token")

    user_id = payload.get("sub")
    if not user_id:
        raise AuthenticationError("Invalid token payload")

    from sqlalchemy import select
    stmt = select(User).where(User.id == UUID(user_id), User.is_active.is_(True))
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        raise AuthenticationError("User not found or deactivated")

    return user


def require_roles(*roles: UserRole):
    """
    Dependency factory: require at least one of the specified roles.

    Usage:
        @router.post("/admin")
        async def endpoint(user: User = require_roles(UserRole.SUPER_ADMIN)):
            ...
    """
    async def checker(user: User = Depends(get_current_user)) -> User:
        if user.role not in roles:
            raise AuthorizationError(
                f"Requires one of: {', '.join(r.value for r in roles)}"
            )
        return user
    return Depends(checker)


# Type aliases for clean router signatures
CurrentUser = Annotated[User, Depends(get_current_user)]
DbSession = Annotated[AsyncSession, Depends(get_db)]
AppSettings = Annotated[Settings, Depends(get_settings)]
RedisClient = Annotated[aioredis.Redis, Depends(get_redis)]
