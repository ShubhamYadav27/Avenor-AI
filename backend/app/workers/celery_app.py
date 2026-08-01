"""
Celery application and all batch worker tasks.
Beat schedule drives the 6-hour pipeline.
Each task is workspace-isolated and idempotent.
"""
import traceback
from datetime import datetime, timezone

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
        "app.workers.tasks.recalibrate_all_models": {"queue": "training"},
        "app.workers.tasks.run_full_pipeline_for_workspace": {"queue": "pipeline"},
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
    },
)
