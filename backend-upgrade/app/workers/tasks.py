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


# ═══════════════════════════════════════════════════════════════
# Production CRM Sync Tasks
# ═══════════════════════════════════════════════════════════════

@celery_app.task(
    name="app.workers.tasks.crm_post_sync_pipeline",
    bind=True,
    max_retries=2,
)
def crm_post_sync_pipeline(self: Task, workspace_id: str):
    """Run the post-sync pipeline for a workspace after a CRM sync completes.

    Executed as a separate Celery task so it does NOT block the HTTP thread or
    the sync task itself. Runs:
      1. Account reconciliation  (crm_accounts → companies table)
      2. Signal generation       (initial signals for new companies)
      3. Scoring engine          (icp_score, signal_score, composite_score)
      4. Intelligence feed       (feed item generation)
    """
    logger.info("crm_post_sync_pipeline_start", workspace_id=workspace_id)

    with db_session() as db:
        ctx = JobContext(db, "crm_post_sync_pipeline", workspace_id)
        try:
            from app.crm.routes import _run_post_sync_pipeline
            _run_post_sync_pipeline(db, workspace_id)
            ctx.complete({"status": "completed"})
            logger.info("crm_post_sync_pipeline_done", workspace_id=workspace_id)
            return {"status": "completed", "workspace_id": workspace_id}
        except Exception as e:
            tb = traceback.format_exc()
            ctx.fail(str(e), tb)
            logger.error("crm_post_sync_pipeline_failed", workspace_id=workspace_id, error=str(e))
            raise self.retry(exc=e, countdown=120)


@celery_app.task(
    name="app.workers.tasks.crm_historical_sync",
    bind=True,
    max_retries=2,
)
def crm_historical_sync(self: Task, workspace_id: str, provider_name: str | None = None):
    """Run a full historical sync through the provider-agnostic CRM engine.

    Used on first OAuth connect to import everything from the CRM org.
    After the SOQL sync completes, dispatches crm_post_sync_pipeline as a
    separate Celery task so the account reconciliation + scoring + feed
    generation does not run inside this task's timeout window.
    """
    logger.info("crm_historical_sync_start", workspace_id=workspace_id, provider=provider_name)

    with db_session() as db:
        ctx = JobContext(db, "crm_historical_sync", workspace_id)
        try:
            from app.crm import CRMFactory
            from app.crm.engine import CRMSyncEngine
            from app.models import CRMConnectionDB

            if provider_name:
                connection = db.query(CRMConnectionDB).filter_by(
                    workspace_id=workspace_id,
                    provider=provider_name,
                    is_active=True,
                ).first()
                provider = CRMFactory.get_provider(provider_name, connection, db) if connection else None
            else:
                provider = CRMFactory.get_for_workspace(workspace_id, db)

            if not provider:
                stats = {"skipped": True, "reason": "no_active_crm_connection"}
                ctx.complete(stats)
                return stats

            result = CRMSyncEngine(db, provider).run_historical_sync()
            stats = result.model_dump(mode="json")
            ctx.complete(stats)
            logger.info(
                "crm_historical_sync_done",
                workspace_id=workspace_id,
                provider=result.provider,
                fetched=result.total_fetched,
                created=result.total_created,
                updated=result.total_updated,
            )
        except Exception as e:
            tb = traceback.format_exc()
            ctx.fail(str(e), tb)
            logger.error("crm_historical_sync_failed", workspace_id=workspace_id, error=str(e))
            raise self.retry(exc=e, countdown=300)

    # Dispatch post-sync pipeline as a separate task AFTER the DB session closes.
    # This ensures the SOQL data is committed before reconciliation reads it.
    crm_post_sync_pipeline.delay(workspace_id)
    return stats


@celery_app.task(
    name="app.workers.tasks.crm_incremental_sync",
    bind=True,
    max_retries=3,
)
def crm_incremental_sync(self: Task, workspace_id: str, provider_name: str | None = None):
    """Run an incremental sync through the provider-agnostic CRM engine.

    Uses per-object LastModifiedDate cursors — each object type (Account,
    Contact, Opportunity…) advances its own cursor independently.
    Dispatches crm_post_sync_pipeline after sync completes.
    """
    logger.info("crm_incremental_sync_start", workspace_id=workspace_id, provider=provider_name)

    with db_session() as db:
        ctx = JobContext(db, "crm_incremental_sync", workspace_id)
        try:
            from app.crm import CRMFactory
            from app.crm.engine import CRMSyncEngine
            from app.models import CRMConnectionDB

            if provider_name:
                connection = db.query(CRMConnectionDB).filter_by(
                    workspace_id=workspace_id,
                    provider=provider_name,
                    is_active=True,
                ).first()
                provider = CRMFactory.get_provider(provider_name, connection, db) if connection else None
            else:
                provider = CRMFactory.get_for_workspace(workspace_id, db)

            if not provider:
                stats = {"skipped": True, "reason": "no_active_crm_connection"}
                ctx.complete(stats)
                return stats

            result = CRMSyncEngine(db, provider).run_incremental_sync()
            stats = result.model_dump(mode="json")
            ctx.complete(stats)
            logger.info(
                "crm_incremental_sync_done",
                workspace_id=workspace_id,
                provider=result.provider,
                fetched=result.total_fetched,
                created=result.total_created,
                updated=result.total_updated,
            )
        except Exception as e:
            tb = traceback.format_exc()
            ctx.fail(str(e), tb)
            logger.error("crm_incremental_sync_failed", workspace_id=workspace_id, error=str(e))
            raise self.retry(exc=e, countdown=60)

    # Dispatch post-sync pipeline after the DB session closes
    crm_post_sync_pipeline.delay(workspace_id)
    return stats


@celery_app.task(name="app.workers.tasks.crm_sync_all_workspaces")
def crm_sync_all_workspaces():
    """Fan out incremental sync for every active generic CRM connection.

    Each workspace gets its own crm_incremental_sync task which in turn
    dispatches crm_post_sync_pipeline after it finishes.
    """
    with db_session() as db:
        from app.models import CRMConnectionDB

        connections = db.query(CRMConnectionDB).filter_by(is_active=True).all()
        targets = [(str(c.workspace_id), c.provider) for c in connections]

    logger.info("fanning_out_crm_sync", connection_count=len(targets))
    for workspace_id, provider in targets:
        crm_incremental_sync.delay(workspace_id, provider)

    return {"dispatched": len(targets)}


@celery_app.task(
    name="app.workers.tasks.hubspot_historical_import",
    bind=True, max_retries=2
)
def hubspot_historical_import(self: Task, workspace_id: str):
    """
    Import historical HubSpot deals on first connect.
    Bootstraps the feedback model before new outcome data accumulates.
    """
    logger.info("hubspot_historical_import_start", workspace_id=workspace_id)

    with db_session() as db:
        from app.models import HubSpotConnection
        conn = db.query(HubSpotConnection).filter_by(
            workspace_id=workspace_id, is_active=True
        ).first()
        if not conn:
            logger.warning("historical_import_no_connection", workspace_id=workspace_id)
            return {"skipped": True, "reason": "no_active_connection"}

        ctx = JobContext(db, "hubspot_historical_import", workspace_id)
        try:
            from app.integrations.hubspot.client import HubSpotClient
            from app.integrations.hubspot.sync import run_historical_import
            client = HubSpotClient(conn, db)
            stats = run_historical_import(db, client, workspace_id)
            ctx.complete(stats)

            # After import, run attribution and feedback loop
            if stats.get("outcomes_created", 0) > 0:
                from app.modules.outcomes.attribution import run_attribution_for_workspace
                run_attribution_for_workspace(db, workspace_id)
                from app.modules.outcomes.feedback_loop import run_full_feedback_loop
                run_full_feedback_loop(db, workspace_id)

            logger.info("hubspot_historical_import_done", workspace_id=workspace_id, **stats)
            return stats

        except Exception as e:
            tb = traceback.format_exc()
            ctx.fail(str(e), tb)
            logger.error("hubspot_historical_import_failed", workspace_id=workspace_id, error=str(e))
            raise self.retry(exc=e, countdown=300)  # 5 minute backoff


@celery_app.task(
    name="app.workers.tasks.hubspot_incremental_sync",
    bind=True, max_retries=3
)
def hubspot_incremental_sync(self: Task, workspace_id: str):
    """
    Incremental HubSpot sync — runs every HUBSPOT_SYNC_INTERVAL_MINUTES.
    Syncs owners, contacts, deals modified since last run.
    """
    logger.info("hubspot_incremental_sync_start", workspace_id=workspace_id)

    with db_session() as db:
        ctx = JobContext(db, "hubspot_incremental_sync", workspace_id)
        try:
            from app.integrations.hubspot.sync import run_incremental_sync
            stats = run_incremental_sync(db, workspace_id)

            if stats.get("skipped"):
                ctx.complete({"skipped": True})
                return stats

            ctx.complete(stats)

            # If new outcomes were logged, run attribution
            deals_stats = stats.get("deals", {})
            if deals_stats.get("outcomes_logged", 0) > 0:
                from app.modules.outcomes.attribution import run_attribution_for_workspace
                run_attribution_for_workspace(db, workspace_id)

            logger.info("hubspot_incremental_sync_done", workspace_id=workspace_id)
            return stats

        except Exception as e:
            tb = traceback.format_exc()
            ctx.fail(str(e), tb)
            logger.error("hubspot_incremental_sync_failed", workspace_id=workspace_id, error=str(e))
            raise self.retry(exc=e, countdown=60)


@celery_app.task(name="app.workers.tasks.hubspot_sync_all_workspaces")
def hubspot_sync_all_workspaces():
    """Fan out incremental sync to all connected workspaces."""
    with db_session() as db:
        from app.models import HubSpotConnection
        connections = db.query(HubSpotConnection).filter_by(is_active=True).all()
        workspace_ids = [str(c.workspace_id) for c in connections]

    logger.info("fanning_out_hubspot_sync", workspace_count=len(workspace_ids))
    for wid in workspace_ids:
        hubspot_incremental_sync.delay(wid)

    return {"dispatched": len(workspace_ids)}


@celery_app.task(name="app.workers.tasks.run_attribution_for_workspace_task")
def run_attribution_for_workspace_task(workspace_id: str):
    """Attribute un-attributed outcomes for a workspace."""
    with db_session() as db:
        ctx = JobContext(db, "outcome_attribution", workspace_id)
        try:
            from app.modules.outcomes.attribution import run_attribution_for_workspace
            stats = run_attribution_for_workspace(db, workspace_id)
            ctx.complete(stats)
            return stats
        except Exception as e:
            tb = traceback.format_exc()
            ctx.fail(str(e), tb)
            raise


@celery_app.task(name="app.workers.tasks.run_feedback_loop_all_workspaces")
def run_feedback_loop_all_workspaces():
    """Compute signal effectiveness for all workspaces. Runs weekly after model recalibration."""
    with db_session() as db:
        from app.modules.outcomes.feedback_loop import run_feedback_loop_all_workspaces as _run
        results = _run(db)
    logger.info("feedback_loop_complete", workspace_count=len(results))
    return {"results": results}


# ── Phase 5.1 — AI Account Research ───────────────────────────

@celery_app.task(
    name="app.workers.tasks.generate_company_research",
    bind=True,
    max_retries=0,  # retries are owned by the provider; failures persist on the row
)
def generate_company_research(self: Task, workspace_id: str, company_id: str):
    """
    Generate AI account research for a single company.

    The service records expected AI failures on the research row itself and
    returns stats rather than raising, so the Job audit record always closes
    cleanly and the frontend poll always reaches a terminal state.
    """
    from app.modules.ai.research_service import generate_research

    with db_session() as db:
        job = JobContext(db, "generate_company_research", workspace_id)
        try:
            stats = generate_research(db, company_id, workspace_id)
            stats["company_id"] = company_id
            job.complete(stats)
            logger.info(
                "research_task_finished",
                workspace_id=workspace_id,
                company_id=company_id,
                **{k: v for k, v in stats.items() if k != "company_id"},
            )
            return stats
        except Exception as e:
            job.fail(str(e), traceback.format_exc())
            logger.error(
                "research_task_error",
                workspace_id=workspace_id,
                company_id=company_id,
                error=str(e),
            )
            raise


@celery_app.task(
    name="app.workers.tasks.generate_company_ai_emails",
    bind=True,
    max_retries=0,
)
def generate_company_ai_emails(self: Task, workspace_id: str, email_ids: list[str]):
    """
    Generate AI email drafts for one company/request.

    Expected provider failures are recorded on each email row by the service,
    letting the polling UI reach a terminal state without retry storms.
    """
    logger.info(
        "celery_task_received_generate_company_ai_emails",
        task_id=str(self.request.id),
        workspace_id=workspace_id,
        email_ids=email_ids,
    )
    from app.modules.ai.email_service import generate_email_rows

    with db_session() as db:
        job = JobContext(db, "generate_company_ai_emails", workspace_id)
        try:
            logger.info(
                "celery_task_started_generate_company_ai_emails",
                task_id=str(self.request.id),
                workspace_id=workspace_id,
                email_ids=email_ids,
            )
            stats = generate_email_rows(db, email_ids, workspace_id)
            stats["email_ids"] = email_ids
            job.complete(stats)
            logger.info(
                "email_generation_task_finished",
                workspace_id=workspace_id,
                generated=stats.get("generated", 0),
                failed=stats.get("failed", 0),
            )
            return stats
        except Exception as e:
            tb = traceback.format_exc()
            job.fail(str(e), tb)
            logger.error(
                "email_generation_task_error",
                workspace_id=workspace_id,
                error=str(e),
                traceback=tb,
            )
            raise


@celery_app.task(
    name="app.workers.tasks.generate_company_ai_briefing",
    bind=True,
    max_retries=0,
)
def generate_company_ai_briefing(self: Task, workspace_id: str, briefing_id: str):
    """
    Generate one AI sales briefing.

    Expected provider failures are recorded on the briefing row by the service,
    letting the polling UI reach a terminal state without retries.
    """
    from app.modules.ai.briefing_service import generate_briefing_row

    with db_session() as db:
        job = JobContext(db, "generate_company_ai_briefing", workspace_id)
        try:
            stats = generate_briefing_row(db, briefing_id, workspace_id)
            stats["briefing_id"] = briefing_id
            job.complete(stats)
            logger.info(
                "briefing_generation_task_finished",
                workspace_id=workspace_id,
                briefing_id=briefing_id,
                generated=stats.get("generated", 0),
                failed=stats.get("failed", 0),
            )
            return stats
        except Exception as e:
            job.fail(str(e), traceback.format_exc())
            logger.error(
                "briefing_generation_task_error",
                workspace_id=workspace_id,
                briefing_id=briefing_id,
                error=str(e),
            )
            raise


@celery_app.task(
    name="app.workers.tasks.generate_company_ai_sales_coaching",
    bind=True,
    max_retries=0,
)
def generate_company_ai_sales_coaching(self: Task, workspace_id: str, coaching_id: str):
    """
    Generate one AI sales coaching artifact.

    Expected provider failures are recorded on the coaching row by the service,
    letting the polling UI reach a terminal state without retries.
    """
    from app.modules.ai.sales_coach_service import generate_sales_coaching_row

    with db_session() as db:
        job = JobContext(db, "generate_company_ai_sales_coaching", workspace_id)
        try:
            stats = generate_sales_coaching_row(db, coaching_id, workspace_id)
            stats["coaching_id"] = coaching_id
            job.complete(stats)
            logger.info(
                "sales_coaching_generation_task_finished",
                workspace_id=workspace_id,
                coaching_id=coaching_id,
                generated=stats.get("generated", 0),
                failed=stats.get("failed", 0),
            )
            return stats
        except Exception as e:
            job.fail(str(e), traceback.format_exc())
            logger.error(
                "sales_coaching_generation_task_error",
                workspace_id=workspace_id,
                coaching_id=coaching_id,
                error=str(e),
            )
            raise
