"""
Pytest configuration and shared fixtures for the KP Astrology backend test suite.

Test DB strategy:
- Unit tests (engine/): no DB needed — pure Python functions
- API tests: SQLite in-memory via aiosqlite (fast, no PostgreSQL required)
- Integration tests: real PostgreSQL (requires TEST_DATABASE_URL env var)
"""
from __future__ import annotations

import asyncio
from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.models import Base

# =============================================================================
# Test settings — override JWT keys with generated in-memory RSA keys
# =============================================================================

def _generate_test_rsa_keys() -> tuple[str, str]:
    """Generate a throwaway RSA key pair for testing."""
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric import rsa

    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode()
    public_pem = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    ).decode()
    return private_pem, public_pem


TEST_PRIVATE_KEY, TEST_PUBLIC_KEY = _generate_test_rsa_keys()


@pytest.fixture(scope="session")
def test_settings():
    """Return Settings with overridden values for testing."""
    from unittest.mock import patch
    from app.config import Settings

    settings = Settings(
        app_env="development",
        debug=True,
        database_url="sqlite+aiosqlite:///:memory:",
        database_url_sync="sqlite:///:memory:",
        redis_url="redis://localhost:6379/15",  # separate test DB
        celery_broker_url="memory://",
        celery_result_backend="cache+memory://",
        jwt_private_key_path="/dev/null",
        jwt_public_key_path="/dev/null",
        ephe_path="/tmp/ephe_test",
    )
    settings.jwt_private_key = TEST_PRIVATE_KEY
    settings.jwt_public_key = TEST_PUBLIC_KEY
    return settings


# =============================================================================
# Database fixtures
# =============================================================================

@pytest_asyncio.fixture(scope="session")
async def db_engine(test_settings):
    """Session-scoped async SQLite engine with all tables created."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
        connect_args={"check_same_thread": False},
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(db_engine) -> AsyncGenerator[AsyncSession, None]:
    """Per-test DB session that always rolls back."""
    factory = async_sessionmaker(db_engine, expire_on_commit=False)
    async with factory() as session:
        yield session
        await session.rollback()


# =============================================================================
# HTTP client fixture
# =============================================================================

@pytest_asyncio.fixture
async def client(test_settings) -> AsyncGenerator[AsyncClient, None]:
    """AsyncClient pointing at the test app with mocked settings."""
    from unittest.mock import patch
    from app.main import create_app

    with patch("app.config.get_settings", return_value=test_settings), \
         patch("app.dependencies.get_settings", return_value=test_settings):
        app = create_app()
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://testserver",
        ) as c:
            yield c


# =============================================================================
# Auth helpers
# =============================================================================

@pytest.fixture
def make_access_token(test_settings):
    """Factory: create an access token for a fake user."""
    import uuid
    from app.core.security import create_access_token

    def _make(user_id=None, tenant_id=None, role="astrologer"):
        return create_access_token(
            user_id=user_id or uuid.uuid4(),
            tenant_id=tenant_id or uuid.uuid4(),
            role=role,
            private_key=test_settings.jwt_private_key,
            algorithm=test_settings.jwt_algorithm,
            expire_minutes=test_settings.jwt_access_token_expire_minutes,
        )
    return _make
