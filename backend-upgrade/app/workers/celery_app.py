"""
Celery application and all batch worker tasks.
Beat schedule drives the 6-hour pipeline.
Each task is workspace-isolated and idempotent.
"""
from celery import Celery
from celery.schedules import crontab

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

# ── Celery app ─────────────────────────────────────────────────

celery_app = Celery(
    "avenor",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["app.workers.tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,           # only ack after task completes (safer)
    worker_prefetch_multiplier=1,  # one task at a time per worker
    task_routes={
        "app.workers.tasks.collect_signals_for_workspace": {"queue": "signals"},
        "app.workers.tasks.score_workspace": {"queue": "scoring"},
        "app.workers.tasks.generate_feed_for_workspace": {"queue": "intelligence"},
        "app.workers.tasks.crm_historical_sync": {"queue": "integrations"},
        "app.workers.tasks.crm_incremental_sync": {"queue": "integrations"},
        "app.workers.tasks.crm_sync_all_workspaces": {"queue": "integrations"},
        "app.workers.tasks.crm_post_sync_pipeline": {"queue": "integrations"},
        "app.workers.tasks.recalibrate_all_models": {"queue": "training"},
        "app.workers.tasks.run_full_pipeline_for_workspace": {"queue": "pipeline"},
        # Phase 5 — AI tasks run on the "ai" queue so slow LLM calls don't block pipeline
        "app.workers.tasks.generate_company_research": {"queue": "ai"},
        "app.workers.tasks.generate_company_ai_emails": {"queue": "ai"},
        "app.workers.tasks.generate_company_ai_briefing": {"queue": "ai"},
        "app.workers.tasks.generate_company_ai_sales_coaching": {"queue": "ai"},
    },
    beat_schedule={
        # Signal collection — every 6 hours
        "collect-signals-all-workspaces": {
            "task": "app.workers.tasks.collect_signals_all_workspaces",
            "schedule": crontab(minute=0, hour="*/6"),
        },
        # Scoring — 30 min after signal collection
        "score-all-workspaces": {
            "task": "app.workers.tasks.score_all_workspaces",
            "schedule": crontab(minute=30, hour="*/6"),
        },
        # Feed generation — nightly at 2am UTC
        "generate-feeds-all-workspaces": {
            "task": "app.workers.tasks.generate_feeds_all_workspaces",
            "schedule": crontab(minute=0, hour=2),
        },
        # Model recalibration — weekly Saturday 2am UTC
        "recalibrate-models": {
            "task": "app.workers.tasks.recalibrate_all_models",
            "schedule": crontab(minute=0, hour=2, day_of_week=6),
        },
        # Phase 4.2 — HubSpot incremental sync every 30 minutes
        "hubspot-sync-all": {
            "task": "app.workers.tasks.hubspot_sync_all_workspaces",
            "schedule": crontab(minute="*/30"),
        },
        "crm-sync-all": {
            "task": "app.workers.tasks.crm_sync_all_workspaces",
            "schedule": crontab(minute="*/30"),
        },
        # Phase 4.2 — Signal feedback loop weekly (after model recalibration)
        "feedback-loop-all": {
            "task": "app.workers.tasks.run_feedback_loop_all_workspaces",
            "schedule": crontab(minute=30, hour=2, day_of_week=6),
        },
    },
)
