"""
Celery application factory and task definitions.

Note: Celery tasks are synchronous — use asyncio.run() for async operations.
The Beat schedule handles maintenance tasks automatically.
"""
from __future__ import annotations

from celery import Celery
from celery.schedules import crontab

from app.config import get_settings

settings = get_settings()

celery_app = Celery(
    "kp_astro",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)

celery_app.conf.update(
    # Serialization
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],

    # Time
    timezone="UTC",
    enable_utc=True,

    # Worker behavior
    worker_hijack_root_logger=False,  # let structlog handle logging
    worker_prefetch_multiplier=1,     # fair scheduling for long tasks
    task_acks_late=True,              # ack after task completes (safer)

    # Beat schedule — maintenance tasks
    beat_schedule={
        "cleanup-expired-refresh-tokens": {
            "task": "app.tasks.maintenance.cleanup_expired_refresh_tokens",
            "schedule": crontab(hour=3, minute=0),  # daily at 03:00 UTC
        },
        "reset-monthly-chart-counts": {
            "task": "app.tasks.maintenance.reset_monthly_chart_counts",
            "schedule": crontab(day_of_month=1, hour=0, minute=0),  # 1st of month
        },
    },
)


# =============================================================================
# Task definitions
# =============================================================================

@celery_app.task(bind=True, max_retries=3, default_retry_delay=60, name="app.tasks.celery_app.generate_pdf")
def generate_pdf(self, chart_id: str, tenant_id: str) -> dict:
    """
    Phase 3: Generate PDF report for a chart.
    Currently a placeholder — will render SVG chart + populate template.
    """
    import asyncio
    try:
        return asyncio.run(_generate_pdf_impl(chart_id, tenant_id))
    except Exception as exc:
        raise self.retry(exc=exc)


async def _generate_pdf_impl(chart_id: str, tenant_id: str) -> dict:
    """Async implementation for PDF generation."""
    # Phase 3: implement with WeasyPrint or ReportLab
    return {"status": "pending", "chart_id": chart_id}
