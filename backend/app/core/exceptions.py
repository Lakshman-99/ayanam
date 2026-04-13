from __future__ import annotations

from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


# =============================================================================
# Base exception
# =============================================================================

class AppError(Exception):
    """Base for all application-level errors. Maps directly to HTTP responses."""

    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    error_code: str = "internal_error"

    def __init__(self, message: str = "An unexpected error occurred", detail: Any = None) -> None:
        super().__init__(message)
        self.message = message
        self.detail = detail


# =============================================================================
# Auth errors
# =============================================================================

class AuthenticationError(AppError):
    status_code = status.HTTP_401_UNAUTHORIZED
    error_code = "authentication_error"


class TokenExpiredError(AuthenticationError):
    error_code = "token_expired"

    def __init__(self) -> None:
        super().__init__("Access token has expired")


class InvalidTokenError(AuthenticationError):
    error_code = "invalid_token"

    def __init__(self, detail: str = "Token is invalid or malformed") -> None:
        super().__init__(detail)


class RefreshTokenRevokedError(AuthenticationError):
    error_code = "token_revoked"

    def __init__(self) -> None:
        super().__init__("Refresh token has been revoked")


class AuthorizationError(AppError):
    status_code = status.HTTP_403_FORBIDDEN
    error_code = "forbidden"

    def __init__(self, message: str = "You do not have permission to perform this action") -> None:
        super().__init__(message)


# =============================================================================
# Resource errors
# =============================================================================

class NotFoundError(AppError):
    status_code = status.HTTP_404_NOT_FOUND
    error_code = "not_found"

    def __init__(self, resource: str = "Resource", resource_id: Any = None) -> None:
        msg = f"{resource} not found"
        if resource_id:
            msg = f"{resource} '{resource_id}' not found"
        super().__init__(msg)


class ConflictError(AppError):
    status_code = status.HTTP_409_CONFLICT
    error_code = "conflict"


class DomainValidationError(AppError):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    error_code = "validation_error"


# =============================================================================
# Tenant errors
# =============================================================================

class TenantNotFoundError(NotFoundError):
    error_code = "tenant_not_found"

    def __init__(self, slug: str = "") -> None:
        AppError.__init__(self, f"Tenant '{slug}' not found or inactive")


class TenantSlugTakenError(ConflictError):
    error_code = "tenant_slug_taken"

    def __init__(self, slug: str) -> None:
        super().__init__(f"Tenant slug '{slug}' is already taken")


# =============================================================================
# Subscription errors
# =============================================================================

class QuotaExceededError(AppError):
    status_code = status.HTTP_402_PAYMENT_REQUIRED
    error_code = "quota_exceeded"

    def __init__(self, resource: str = "charts") -> None:
        super().__init__(f"Monthly {resource} quota exceeded. Please upgrade your plan.")


# =============================================================================
# Calculation errors
# =============================================================================

class ChartCalculationError(AppError):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    error_code = "chart_calculation_failed"

    def __init__(self, reason: str = "") -> None:
        msg = "Chart calculation failed"
        if reason:
            msg = f"Chart calculation failed: {reason}"
        super().__init__(msg)


class EphemerisNotFoundError(AppError):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    error_code = "ephemeris_not_found"

    def __init__(self) -> None:
        super().__init__(
            "Swiss Ephemeris data files not found. "
            "Please ensure .se1 files are present in EPHE_PATH."
        )


# =============================================================================
# Exception handlers — registered in main.py
# =============================================================================

def _error_response(error_code: str, message: str, detail: Any, status_code: int) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "code": error_code,
                "message": message,
                "detail": detail,
            }
        },
    )


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
        return _error_response(
            error_code=exc.error_code,
            message=exc.message,
            detail=exc.detail,
            status_code=exc.status_code,
        )

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        errors = []
        for err in exc.errors():
            errors.append({
                "field": ".".join(str(loc) for loc in err["loc"]),
                "message": err["msg"],
                "type": err["type"],
            })
        return _error_response(
            error_code="request_validation_error",
            message="Request validation failed",
            detail=errors,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )

    @app.exception_handler(Exception)
    async def unhandled_error_handler(request: Request, exc: Exception) -> JSONResponse:
        # In production, don't leak stack traces
        import structlog
        log = structlog.get_logger()
        log.exception("Unhandled exception", path=request.url.path)
        return _error_response(
            error_code="internal_error",
            message="An unexpected error occurred",
            detail=None,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
