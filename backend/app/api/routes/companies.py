"""Companies and scoring routes."""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session

from app.api.auth import CurrentUser
from app.db.session import get_db
from app.models import Company, CompanyScore, CompanyStatus

router = APIRouter(prefix="/companies", tags=["companies"])


@router.get("")
def list_companies(
    current_user: CurrentUser,
    db: Session = Depends(get_db),
    status: Optional[str] = Query(None),
    buying_window: Optional[str] = Query(None),
    min_score: float = Query(0.0),
    limit: int = Query(50, le=200),
    offset: int = Query(0),
):
    """List companies in the workspace, ordered by composite score."""
    query = db.query(Company).filter_by(workspace_id=current_user.workspace_id)

    if status:
        query = query.filter(Company.status == status)
    if buying_window:
        query = query.filter(Company.buying_window == buying_window)
    if min_score > 0:
        query = query.filter(Company.composite_score >= min_score)

    total = query.count()
    companies = (
        query
        .order_by(Company.composite_score.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    return {
        "total": total,
        "companies": [_serialize_company(c) for c in companies],
    }


@router.get("/stats")
def company_stats(current_user: CurrentUser, db: Session = Depends(get_db)):
    """Pipeline health stats — counts per status and buying window."""
    from sqlalchemy import func

    status_counts = (
        db.query(Company.status, func.count(Company.id))
        .filter_by(workspace_id=current_user.workspace_id)
        .group_by(Company.status)
        .all()
    )
    window_counts = (
        db.query(Company.buying_window, func.count(Company.id))
        .filter(
            Company.workspace_id == current_user.workspace_id,
            Company.status == CompanyStatus.ACTIVE,
        )
        .group_by(Company.buying_window)
        .all()
    )
    return {
        "by_status": {s: c for s, c in status_counts},
        "active_by_window": {w: c for w, c in window_counts},
        "total": sum(c for _, c in status_counts),
    }


@router.get("/{company_id}/score")
def get_company_score(
    company_id: str,
    current_user: CurrentUser,
    db: Session = Depends(get_db),
):
    """Get the latest score breakdown for a company."""
    company = db.get(Company, company_id)
    if not company or str(company.workspace_id) != str(current_user.workspace_id):
        raise HTTPException(status_code=404, detail="Company not found")

    score = company.score_snapshot
    return {
        "company_id": company_id,
        "company_name": company.name,
        "composite_score": company.composite_score,
        "icp_score": company.icp_score,
        "signal_score": company.signal_score,
        "buying_window": company.buying_window,
        "buying_window_confidence": company.buying_window_confidence,
        "last_scored_at": company.last_scored_at.isoformat() if company.last_scored_at else None,
        "score_breakdown": {
            "icp_breakdown": score.icp_breakdown if score else {},
            "signal_breakdown": score.signal_breakdown if score else [],
            "buying_window_reasoning": score.buying_window_reasoning if score else None,
        },
    }


@router.post("/score")
def trigger_scoring(
    current_user: CurrentUser,
    db: Session = Depends(get_db),
):
    """Trigger on-demand scoring for the workspace."""
    current_user.require_admin()
    from app.workers.tasks import score_workspace
    score_workspace.delay(str(current_user.workspace_id))
    return {"status": "scoring_queued", "workspace_id": str(current_user.workspace_id)}


def _serialize_company(c: Company) -> dict:
    return {
        "id": str(c.id),
        "name": c.name,
        "domain": c.domain,
        "industry": c.industry,
        "employee_count": c.employee_count,
        "location": " ".join(filter(None, [c.location_city, c.location_state, c.location_country])),
        "composite_score": round(c.composite_score, 3),
        "buying_window": c.buying_window,
        "status": c.status,
        "last_funding_stage": c.last_funding_stage,
        "last_scored_at": c.last_scored_at.isoformat() if c.last_scored_at else None,
    }
