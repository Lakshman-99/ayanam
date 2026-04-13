from __future__ import annotations

import time
import uuid

import structlog
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

log = structlog.get_logger()


class RequestIDMiddleware(BaseHTTPMiddleware):
    """
    Attaches a unique request ID to every request.
    Reads X-Request-ID header from upstream (gateway/CDN) if present,
    otherwise generates a new UUID4. Injects into structlog context
    and echoes back in the response header.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = request.headers.get("x-request-id") or str(uuid.uuid4())
        request.state.request_id = request_id

        # Bind to structlog context for this request
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(
            request_id=request_id,
            method=request.method,
            path=request.url.path,
        )

        start_time = time.perf_counter()
        response = await call_next(request)
        duration_ms = round((time.perf_counter() - start_time) * 1000, 2)

        response.headers["X-Request-ID"] = request_id
        response.headers["X-Response-Time"] = f"{duration_ms}ms"

        log.info(
            "request_handled",
            status_code=response.status_code,
            duration_ms=duration_ms,
        )
        return response


class TenantMiddleware(BaseHTTPMiddleware):
    """
    Resolves the current tenant from the X-Tenant-Slug request header.

    JWT-based tenant resolution happens in the auth dependency (get_current_user)
    since the JWT contains the tenant_id. This middleware handles pre-auth
    endpoints (like registration) where the tenant context comes from the header.

    Does NOT block requests with no tenant — health check, docs, and auth
    endpoints may legitimately have no tenant context.
    """

    # Paths that bypass tenant resolution entirely
    _BYPASS_PATHS = {"/api/v1/health", "/api/v1/ready", "/docs", "/redoc", "/openapi.json"}

    async def dispatch(self, request: Request, call_next) -> Response:
        request.state.tenant = None
        request.state.tenant_slug = None

        if request.url.path not in self._BYPASS_PATHS:
            slug = request.headers.get("x-tenant-slug")
            if slug:
                request.state.tenant_slug = slug.lower().strip()
                structlog.contextvars.bind_contextvars(tenant_slug=slug)

        return await call_next(request)
