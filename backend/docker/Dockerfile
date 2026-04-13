# =============================================================================
# KP Astrology API — Production Dockerfile
# Python 3.12 for production stability (3.13 also works with pysweph)
# =============================================================================

FROM python:3.12-slim AS base

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# System dependencies:
#   build-essential: compile pysweph (Swiss Ephemeris) C extension
#   libpq-dev: PostgreSQL client libraries for psycopg2
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# =============================================================================
# Dependencies layer (cached unless pyproject.toml changes)
# =============================================================================
FROM base AS deps

COPY pyproject.toml .
RUN pip install --no-cache-dir -e .

# =============================================================================
# Application layer
# =============================================================================
FROM deps AS app

# Ephemeris data files (download from astro.com/swisseph)
# Must exist for accurate calculations — falls back to Moshier if absent
COPY data/ephemeris/ /app/data/ephemeris/

# Application source
COPY app/ /app/app/
COPY alembic/ /app/alembic/
COPY alembic.ini /app/alembic.ini

# Non-root user for security
RUN groupadd --gid 1001 appgroup && \
    useradd --uid 1001 --gid appgroup --no-create-home appuser && \
    chown -R appuser:appgroup /app

USER appuser

EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health || exit 1

# Production: 4 Uvicorn workers managed by Gunicorn
CMD ["gunicorn", "app.main:app", \
     "--worker-class", "uvicorn.workers.UvicornWorker", \
     "--workers", "4", \
     "--bind", "0.0.0.0:8000", \
     "--timeout", "120", \
     "--access-logfile", "-", \
     "--error-logfile", "-"]
