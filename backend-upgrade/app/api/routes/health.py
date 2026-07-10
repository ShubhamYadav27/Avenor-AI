"""Health check and admin routes."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.auth import CurrentUser
from app.db.session import get_db, check_db_connection
from app.models import Job, JobStatus, Workspace, SignalWeights

router = APIRouter(tags=["health"])


@router.get("/health")
def health_check(db: Session = Depends(get_db)):
    """Public health check — used by load balancers and monitoring."""
    db_ok = check_db_connection()
    return {
        "status": "healthy" if db_ok else "degraded",
        "database": "connected" if db_ok else "disconnected",
        "service": "avenor-backend",
        "version": "0.1.0",
    }


@router.get("/admin/status")
def system_status(current_user: CurrentUser, db: Session = Depends(get_db)):
    """Internal system status — job health, workspace stats."""
    current_user.require_admin()

    # Last 10 jobs for this workspace
    recent_jobs = (
        db.query(Job)
        .filter_by(workspace_id=current_user.workspace_id)
        .order_by(Job.created_at.desc())
        .limit(10)
        .all()
    )

    failed_jobs = [j for j in recent_jobs if j.status == JobStatus.FAILED]

    sw = db.query(SignalWeights).filter_by(workspace_id=current_user.workspace_id).first()

    return {
        "workspace": {
            "id": str(current_user.workspace_id),
            "name": current_user.workspace.name,
            "tier": current_user.workspace.subscription_tier,
            "is_active": current_user.workspace.is_active,
        },
        "model": {
            "accuracy": sw.model_accuracy if sw else None,
            "training_sample_size": sw.training_sample_size if sw else 0,
            "last_trained_at": sw.last_trained_at.isoformat() if sw and sw.last_trained_at else None,
            "current_weights": sw.weights if sw else {},
        },
        "recent_jobs": [
            {
                "id": str(j.id),
                "type": j.job_type,
                "status": j.status,
                "duration_seconds": j.duration_seconds,
                "records_processed": j.records_processed,
                "error": j.error_message,
                "created_at": j.created_at.isoformat(),
            }
            for j in recent_jobs
        ],
        "failed_jobs_count": len(failed_jobs),
        "alerts": [
            f"Job {j.job_type} failed: {j.error_message}"
            for j in failed_jobs
        ],
    }


@router.post("/admin/pipeline/trigger")
def trigger_full_pipeline(current_user: CurrentUser, db: Session = Depends(get_db)):
    """Manually trigger the full pipeline for the workspace."""
    current_user.require_admin()
    from app.workers.tasks import run_full_pipeline_for_workspace
    run_full_pipeline_for_workspace.delay(str(current_user.workspace_id))
    return {"status": "pipeline_triggered", "workspace_id": str(current_user.workspace_id)}
