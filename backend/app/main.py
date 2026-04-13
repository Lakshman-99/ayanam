from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from sqlalchemy import text

from app.config import Settings, get_settings
from app.core.exceptions import register_exception_handlers
from app.core.middleware import RequestIDMiddleware, TenantMiddleware
from app.routers import auth, charts


def _configure_logging(settings: Settings) -> None:
    import logging
    import structlog

    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)
    logging.basicConfig(level=log_level)

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.JSONRenderer() if settings.is_production
            else structlog.dev.ConsoleRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(log_level),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown events."""
    settings = get_settings()
    log = structlog.get_logger()

    # -------------------------------------------------------------------------
    # Startup
    # -------------------------------------------------------------------------
    _configure_logging(settings)

    # Validate ephemeris data files exist
    ephe_path = settings.ephe_path
    if not ephe_path.exists():
        log.warning("ephemeris_path_missing", path=str(ephe_path))
    else:
        se1_files = list(ephe_path.glob("*.se1"))
        if not se1_files:
            log.warning("no_ephemeris_files_found", path=str(ephe_path))
        else:
            log.info("ephemeris_files_found", count=len(se1_files))

    # Initialize Swiss Ephemeris
    try:
        from app.engine.ephemeris import initialize_ephemeris
        initialize_ephemeris(ephe_path)
        log.info("ephemeris_initialized", path=str(ephe_path))
    except ImportError:
        log.warning("pyswisseph_not_installed")
    except Exception as exc:
        log.error("ephemeris_init_failed", error=str(exc))

    # Test database connectivity
    try:
        from app.dependencies import get_engine
        engine = get_engine(settings)
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        log.info("database_connected")
    except Exception as exc:
        log.error("database_connection_failed", error=str(exc))

    log.info(
        "application_started",
        env=settings.app_env,
        debug=settings.debug,
    )

    yield

    # -------------------------------------------------------------------------
    # Shutdown
    # -------------------------------------------------------------------------
    try:
        from app.dependencies import _engine
        if _engine is not None:
            await _engine.dispose()
    except Exception:
        pass

    log.info("application_stopped")


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title="KP Astrology API",
        version="0.1.0",
        description=(
            "Enterprise KP (Krishnamurti Paddhati) Astrology SaaS Platform API. "
            "Accurate natal charts, horary, matching, and real-time panchang."
        ),
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
        openapi_url="/openapi.json" if settings.debug else None,
        lifespan=lifespan,
    )

    # -------------------------------------------------------------------------
    # CORS
    # -------------------------------------------------------------------------
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # -------------------------------------------------------------------------
    # Custom middleware (outermost executes first)
    # -------------------------------------------------------------------------
    app.add_middleware(TenantMiddleware)
    app.add_middleware(RequestIDMiddleware)

    # -------------------------------------------------------------------------
    # Rate limiting
    # -------------------------------------------------------------------------
    limiter = Limiter(
        key_func=get_remote_address,
        default_limits=[settings.rate_limit_default],
    )
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    # -------------------------------------------------------------------------
    # Exception handlers
    # -------------------------------------------------------------------------
    register_exception_handlers(app)

    # -------------------------------------------------------------------------
    # Routers
    # -------------------------------------------------------------------------
    app.include_router(auth.router, prefix="/api/v1")
    app.include_router(charts.router, prefix="/api/v1")

    # -------------------------------------------------------------------------
    # Health endpoints
    # -------------------------------------------------------------------------
    @app.get("/api/v1/health", tags=["Health"], include_in_schema=False)
    async def health():
        from datetime import datetime, timezone
        return {"status": "ok", "timestamp": datetime.now(tz=timezone.utc).isoformat()}

    @app.get("/api/v1/ready", tags=["Health"], include_in_schema=False)
    async def ready():
        """Readiness probe — checks DB, Redis, and ephemeris."""
        checks = {}

        # DB
        try:
            from app.dependencies import get_engine
            engine = get_engine(settings)
            async with engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
            checks["database"] = "ok"
        except Exception as exc:
            checks["database"] = f"error: {exc}"

        # Ephemeris
        ephe_path = settings.ephe_path
        checks["ephemeris"] = "ok" if any(ephe_path.glob("*.se1")) else "missing"

        all_ok = all(v == "ok" for v in checks.values())
        from fastapi.responses import JSONResponse
        return JSONResponse(
            content={"status": "ready" if all_ok else "degraded", "checks": checks},
            status_code=200 if all_ok else 503,
        )

    return app


# Application instance (used by uvicorn / gunicorn)
app = create_app()
