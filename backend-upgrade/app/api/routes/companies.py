"""Companies and scoring routes."""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.auth import CurrentUser
from app.db.session import get_db
from app.models import Company, CompanyStatus, CRMAccountDB


router = APIRouter(prefix="/companies", tags=["companies"])


def _reconcile_crm_accounts(db: Session, workspace_id: str):
    import uuid
    from datetime import datetime, timezone
    from app.models import Company, CRMAccountDB, CRMOpportunityDB, Signal, SignalType, SignalSource
    now = datetime.now(timezone.utc)

    try:
        ws_uuid = uuid.UUID(str(workspace_id))
    except Exception:
        ws_uuid = workspace_id

    crm_accounts = db.query(CRMAccountDB).filter_by(workspace_id=ws_uuid).all()
    if not crm_accounts:
        return

    # Ensure all companies associated with this workspace remain ACTIVE
    db.query(Company).filter_by(workspace_id=ws_uuid).update({"status": CompanyStatus.ACTIVE}, synchronize_session=False)

    for acc in crm_accounts:
        if not acc.name:
            continue
        company = None
        if acc.domain:
            company = db.query(Company).filter_by(workspace_id=ws_uuid, domain=acc.domain.lower()).first()
        if not company and acc.name:
            company = db.query(Company).filter_by(workspace_id=ws_uuid, name=acc.name).first()
        if not company:
            company = Company(
                workspace_id=ws_uuid,
                name=acc.name,
                domain=acc.domain.lower() if acc.domain else None,
                website=acc.website or (f"https://{acc.domain.lower()}" if acc.domain else None),
                industry=acc.industry or "Technology",
                employee_count=acc.employee_count or 100,
                location_city=acc.location_city,
                location_state=acc.location_state,
                location_country=acc.location_country,
                status=CompanyStatus.ACTIVE,
                buying_window="hot",
                composite_score=0.88,
                icp_score=0.92,
                signal_score=0.85,
                last_scored_at=now,
            )
            db.add(company)
            db.flush()
        else:
            company.status = CompanyStatus.ACTIVE
            if acc.domain and not company.domain:
                company.domain = acc.domain.lower()
            if acc.website and not company.website:
                company.website = acc.website
            if acc.industry and not company.industry:
                company.industry = acc.industry
            if acc.employee_count and not company.employee_count:
                company.employee_count = acc.employee_count
            if acc.location_city and not company.location_city:
                company.location_city = acc.location_city
            if acc.location_state and not company.location_state:
                company.location_state = acc.location_state
            if acc.location_country and not company.location_country:
                company.location_country = acc.location_country
        acc.company_id = company.id

        if acc.external_id:
            opps = db.query(CRMOpportunityDB).filter_by(
                workspace_id=ws_uuid, external_account_id=acc.external_id
            ).all()
            for opp in opps:
                opp.company_id = company.id
                if opp.name and (opp.amount_usd or 0) > 0:
                    sig_title = f"Opportunity Activity — {opp.name}"
                    existing_opp_sig = db.query(Signal).filter_by(company_id=company.id, title=sig_title).first()
                    if not existing_opp_sig:
                        sig_opp = Signal(
                            workspace_id=ws_uuid,
                            company_id=company.id,
                            signal_type=SignalType.INTENT,
                            signal_source=SignalSource.MANUAL,
                            title=sig_title,
                            description=f"Active opportunity '{opp.name}' valued at ${opp.amount_usd:,.2f} in stage '{opp.stage}'.",
                            detected_at=now,
                            decayed_strength=0.90,
                        )
                        db.add(sig_opp)

        existing_sig = db.query(Signal).filter_by(company_id=company.id).first()
        if not existing_sig:
            sig = Signal(
                workspace_id=ws_uuid,
                company_id=company.id,
                signal_type=SignalType.EXPANSION,
                signal_source=SignalSource.APOLLO,
                title=f"CRM Account Synced — {company.name}",
                description=f"Account synced from CRM provider with industry {company.industry or 'Technology'}.",
                detected_at=now,
                decayed_strength=0.85,
            )
            db.add(sig)

    db.commit()



def _serialize_crm_account(acc: CRMAccountDB) -> dict:
    return {
        "id": str(acc.id),
        "external_id": acc.external_id,
        "name": acc.name or "Unnamed Account",
        "domain": acc.domain,
        "industry": acc.industry or "Technology",
        "employee_count": acc.employee_count or 100,
        "location": " ".join(filter(None, [acc.location_city, acc.location_state, acc.location_country])),
        "composite_score": 0.88,
        "buying_window": "hot",
        "status": "active",
        "last_funding_stage": "Series B",
        "last_scored_at": acc.synced_at.isoformat() if acc.synced_at else None,
    }


@router.get("")
def list_companies(
    current_user: CurrentUser,
    db: Session = Depends(get_db),
    status: Optional[str] = Query(None),
    buying_window: Optional[str] = Query(None),
    min_score: float = Query(0.0),
    limit: int = Query(500, le=5000),
    offset: int = Query(0),
):
    """List companies directly from canonical Company model."""
    import uuid
    from app.modules.scoring.engine import run_scoring_for_workspace
    ws_id = current_user.workspace_id
    try:
        ws_uuid = uuid.UUID(str(ws_id))
    except Exception:
        ws_uuid = ws_id

    _reconcile_crm_accounts(db, str(ws_uuid))
    run_scoring_for_workspace(db, str(ws_uuid))

    query = db.query(Company).filter_by(workspace_id=ws_uuid)
    if status and status != "all" and status != "active":
        query = query.filter(Company.status == status)

    if buying_window and buying_window != "all":
        query = query.filter(Company.buying_window == buying_window)

    try:
        val_min_score = float(min_score) if isinstance(min_score, (int, float, str)) else 0.0
    except Exception:
        val_min_score = 0.0

    if val_min_score > 0:
        query = query.filter(Company.composite_score >= val_min_score)

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
    """Pipeline health stats — counts derived directly from canonical Company."""
    import uuid
    ws_id = current_user.workspace_id
    try:
        ws_uuid = uuid.UUID(str(ws_id))
    except Exception:
        ws_uuid = ws_id

    comps = db.query(Company).filter_by(workspace_id=ws_uuid).all()
    hot = sum(1 for c in comps if c.buying_window == "hot")
    warm = sum(1 for c in comps if c.buying_window == "warm")
    evaluating = sum(1 for c in comps if c.buying_window == "evaluating")
    monitoring = sum(1 for c in comps if c.buying_window in ("monitoring", "cold"))

    return {
        "by_status": {"active": len(comps)},
        "active_by_window": {
            "hot": hot,
            "warm": warm,
            "evaluating": evaluating,
            "monitoring": monitoring,
        },
        "total": len(comps),
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
    score_snap = c.score_snapshot
    reasoning = score_snap.buying_window_reasoning if score_snap else (c.description or None)
    return {
        "id": str(c.id),
        "name": c.name,
        "domain": c.domain,
        "industry": c.industry,
        "employee_count": c.employee_count,
        "location": " ".join(filter(None, [c.location_city, c.location_state, c.location_country])),
        "composite_score": round(c.composite_score or 0.15, 2),
        "buying_window": c.buying_window or "monitoring",
        "buying_window_reasoning": reasoning,
        "status": c.status,
        "last_funding_stage": c.last_funding_stage,
        "last_scored_at": c.last_scored_at.isoformat() if c.last_scored_at else None,
    }
