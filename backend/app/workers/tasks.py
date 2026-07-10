"""
Celery task definitions.
Each task:
  1. Creates a Job record for audit
  2. Executes the module function
  3. Updates the Job record with results
  4. Logs structured output
"""
import traceback
from datetime import datetime, timezone

from celery import Task

from app.workers.celery_app import celery_app
from app.core.logging import get_logger
from app.db.session import db_session
from app.models import Job, JobStatus, Workspace

logger = get_logger(__name__)


# ── Job audit helper ──────────────────────────────────────────

class JobContext:
    """Context manager that creates and updates a Job audit record."""

    def __init__(self, db, job_type: str, workspace_id: str | None = None):
        self.db = db
        self.job = Job(
            workspace_id=workspace_id,
            job_type=job_type,
            status=JobStatus.RUNNING,
            started_at=datetime.now(timezone.utc),
        )
        db.add(self.job)
        db.flush()

    def complete(self, stats: dict):
        self.job.status = JobStatus.COMPLETED
        self.job.completed_at = datetime.now(timezone.utc)
        self.job.duration_seconds = (
            self.job.completed_at - self.job.started_at
        ).total_seconds()
        self.job.records_processed = stats.get("companies_created", 0) + stats.get("scored", 0) + stats.get("generated", 0)
        self.job.records_created = stats.get("companies_created", 0) + stats.get("signals_created", 0)
        self.job.job_metadata = stats
        self.db.commit()

    def fail(self, error: str, tb: str):
        self.job.status = JobStatus.FAILED
        self.job.completed_at = datetime.now(timezone.utc)
        self.job.error_message = error[:500]
        self.job.error_traceback = tb[:2000]
        self.db.commit()


# ── Per-workspace tasks ───────────────────────────────────────

@celery_app.task(name="app.workers.tasks.collect_signals_for_workspace", bind=True, max_retries=2)
def collect_signals_for_workspace(self: Task, workspace_id: str):
    """Run signal collection for one workspace (Apollo + News)."""
    from app.modules.signals.apollo_collector import run_apollo_collection
    from app.modules.signals.news_collector import run_news_collection

    logger.info("signal_collection_start", workspace_id=workspace_id)

    with db_session() as db:
        ctx = JobContext(db, "signal_collection", workspace_id)
        try:
            apollo_stats = run_apollo_collection(db, workspace_id)
            news_stats = run_news_collection(db, workspace_id)

            combined = {
                "apollo": apollo_stats,
                "news": news_stats,
                "companies_created": apollo_stats.get("companies_created", 0),
                "signals_created": (
                    apollo_stats.get("signals_created", 0) + news_stats.get("signals_created", 0)
                ),
            }
            ctx.complete(combined)
            logger.info("signal_collection_done", workspace_id=workspace_id, **combined)
            return combined

        except Exception as e:
            tb = traceback.format_exc()
            ctx.fail(str(e), tb)
            logger.error("signal_collection_failed", workspace_id=workspace_id, error=str(e))
            raise self.retry(exc=e, countdown=120)


@celery_app.task(name="app.workers.tasks.score_workspace", bind=True, max_retries=2)
def score_workspace(self: Task, workspace_id: str):
    """Run scoring engine for one workspace."""
    from app.modules.scoring.engine import run_scoring_for_workspace

    logger.info("scoring_start", workspace_id=workspace_id)

    with db_session() as db:
        ctx = JobContext(db, "scoring", workspace_id)
        try:
            stats = run_scoring_for_workspace(db, workspace_id)
            ctx.complete(stats)
            logger.info("scoring_done", workspace_id=workspace_id, **stats)
            return stats
        except Exception as e:
            tb = traceback.format_exc()
            ctx.fail(str(e), tb)
            logger.error("scoring_failed", workspace_id=workspace_id, error=str(e))
            raise self.retry(exc=e, countdown=60)


@celery_app.task(name="app.workers.tasks.generate_feed_for_workspace", bind=True, max_retries=2)
def generate_feed_for_workspace(self: Task, workspace_id: str, force_refresh: bool = False):
    """Generate intelligence feed items for one workspace."""
    from app.modules.intelligence.engine import run_feed_generation_for_workspace

    logger.info("feed_generation_start", workspace_id=workspace_id)

    with db_session() as db:
        ctx = JobContext(db, "feed_generation", workspace_id)
        try:
            stats = run_feed_generation_for_workspace(db, workspace_id, force_refresh)
            ctx.complete(stats)
            logger.info("feed_generation_done", workspace_id=workspace_id, **stats)
            return stats
        except Exception as e:
            tb = traceback.format_exc()
            ctx.fail(str(e), tb)
            logger.error("feed_generation_failed", workspace_id=workspace_id, error=str(e))
            raise self.retry(exc=e, countdown=60)


# ── All-workspace fan-out tasks ────────────────────────────────

@celery_app.task(name="app.workers.tasks.collect_signals_all_workspaces")
def collect_signals_all_workspaces():
    """Fan out signal collection to all active workspaces."""
    with db_session() as db:
        workspace_ids = [
            str(ws.id)
            for ws in db.query(Workspace).filter_by(is_active=True).all()
        ]

    logger.info("fanning_out_signal_collection", workspace_count=len(workspace_ids))
    for wid in workspace_ids:
        collect_signals_for_workspace.delay(wid)

    return {"dispatched": len(workspace_ids)}


@celery_app.task(name="app.workers.tasks.score_all_workspaces")
def score_all_workspaces():
    """Fan out scoring to all active workspaces."""
    with db_session() as db:
        workspace_ids = [
            str(ws.id)
            for ws in db.query(Workspace).filter_by(is_active=True).all()
        ]

    logger.info("fanning_out_scoring", workspace_count=len(workspace_ids))
    for wid in workspace_ids:
        score_workspace.delay(wid)

    return {"dispatched": len(workspace_ids)}


@celery_app.task(name="app.workers.tasks.generate_feeds_all_workspaces")
def generate_feeds_all_workspaces():
    """Fan out feed generation to all active workspaces."""
    with db_session() as db:
        workspace_ids = [
            str(ws.id)
            for ws in db.query(Workspace).filter_by(is_active=True).all()
        ]

    logger.info("fanning_out_feed_generation", workspace_count=len(workspace_ids))
    for wid in workspace_ids:
        generate_feed_for_workspace.delay(wid)

    return {"dispatched": len(workspace_ids)}


@celery_app.task(name="app.workers.tasks.recalibrate_all_models")
def recalibrate_all_models():
    """Run weekly model recalibration for all workspaces."""
    from app.modules.scoring.trainer import run_model_recalibration_all_workspaces

    logger.info("model_recalibration_start")
    with db_session() as db:
        results = run_model_recalibration_all_workspaces(db)

    logger.info("model_recalibration_complete", workspace_count=len(results))
    return {"results": results}


@celery_app.task(name="app.workers.tasks.run_full_pipeline_for_workspace")
def run_full_pipeline_for_workspace(workspace_id: str):
    """
    Run the complete pipeline for one workspace synchronously.
    Useful for on-demand refresh or initial setup.
    """
    logger.info("full_pipeline_start", workspace_id=workspace_id)

    collect_signals_for_workspace(workspace_id)
    score_workspace(workspace_id)
    generate_feed_for_workspace(workspace_id, force_refresh=True)

    logger.info("full_pipeline_complete", workspace_id=workspace_id)
    return {"status": "complete", "workspace_id": workspace_id}
