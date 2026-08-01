"""Generic CRM integration API routes."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, Query

from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.api.auth import CurrentUser
from app.core.config import settings
from app.core.exceptions import ExternalServiceError
from app.core.logging import get_logger
from app.crm import CRMFactory
from app.crm.base.models import SyncStatus
from app.crm.engine import CRMSyncEngine
from app.crm.registry import CRMProviderRegistry
from app.db.session import get_db
from app.models import CRMConnectionDB

logger = get_logger(__name__)


# Import providers once so their registry hooks run before any endpoint uses the factory.
import app.crm.providers  # noqa: F401

router = APIRouter(prefix="/crm", tags=["crm"])
integrations_crm_router = APIRouter(prefix="/integrations", tags=["crm"])


def _ensure_provider(provider: str) -> None:
    if not CRMProviderRegistry.is_registered(provider):
        raise HTTPException(status_code=404, detail=f"CRM provider not registered: {provider}")


def _provider_enabled(provider: str) -> bool:
    flag_map = {
        "hubspot": settings.ENABLE_HUBSPOT,
        "salesforce": settings.ENABLE_SALESFORCE,
        "dynamics": settings.ENABLE_DYNAMICS,
        "zoho": settings.ENABLE_ZOHO,
    }
    return flag_map.get(provider, False)


@router.get("/providers")
def list_providers():
    providers = []
    for item in CRMFactory.list_providers():
        provider = item["name"]
        providers.append({
            **item,
            "enabled": _provider_enabled(provider),
            "configured": provider in settings.enabled_crm_providers,
        })
    return {"providers": providers}


@router.get("/connections")
def list_connections(current_user: CurrentUser, db: Session = Depends(get_db)):
    connections = (
        db.query(CRMConnectionDB)
        .filter_by(workspace_id=current_user.workspace_id)
        .order_by(CRMConnectionDB.created_at.desc())
        .all()
    )
    return {
        "connections": [
            {
                "id": str(conn.id),
                "provider": conn.provider,
                "external_account_id": conn.external_account_id,
                "external_account_name": conn.external_account_name,
                "is_active": conn.is_active,
                "last_sync_at": conn.last_sync_at.isoformat() if conn.last_sync_at else None,
                "sync_error": conn.sync_error,
                "created_at": conn.created_at.isoformat() if conn.created_at else None,
            }
            for conn in connections
        ]
    }


@router.get("/status")
def get_active_status(current_user: CurrentUser, db: Session = Depends(get_db)):
    provider = CRMFactory.get_for_workspace(str(current_user.workspace_id), db)
    if not provider:
        return {"connected": False, "provider": None}
    return {"connected": True, "status": provider.get_status().model_dump(mode="json")}


@router.post("/{provider}/oauth/start")
def start_oauth(provider: str, current_user: CurrentUser):
    _ensure_provider(provider)
    if not _provider_enabled(provider):
        raise HTTPException(status_code=403, detail=f"CRM provider disabled: {provider}")
    try:
        result = CRMFactory.get_oauth_url(provider, str(current_user.workspace_id))
    except ExternalServiceError as exc:
        raise HTTPException(status_code=400, detail=exc.message) from exc
    return result.model_dump(mode="json")


@router.get("/{provider}/callback", summary="Generic CRM OAuth Callback")
def oauth_callback(
    provider: str,
    code: str,
    state: str,
    db: Session = Depends(get_db),
):
    """
    Generic CRM OAuth 2.0 Callback Endpoint.
    Receives authorization code & state parameter, validates workspace,
    retrieves PKCE code_verifier (for providers requiring PKCE like Salesforce),
    exchanges authorization code for tokens, encrypts tokens with Fernet,
    updates CRM connection state in DB, and ALWAYS redirects browser back
    to the frontend CRM dashboard (http://localhost:3000/dashboard/crm?status=connected&provider=...).
    """
    _ensure_provider(provider)
    provider_cls = CRMProviderRegistry.get(provider)
    try:
        crm_provider = provider_cls(connection=None, db=None)
        result = crm_provider.handle_oauth_callback(code, state, state, db)
    except ExternalServiceError as exc:
        raise HTTPException(status_code=400, detail=exc.message) from exc

    # ALWAYS redirect browser to frontend CRM dashboard (302 Found)
    target_url = f"{settings.frontend_base}/dashboard/crm?status=connected&provider={result.provider}"
    return RedirectResponse(url=target_url, status_code=302)


@integrations_crm_router.get("/{provider}/callback", include_in_schema=False)
def legacy_integrations_callback(
    provider: str,
    code: str,
    state: str,
    db: Session = Depends(get_db),
):
    """
    Fallback callback handler for /api/v1/integrations/{provider}/callback path.
    Executes the exact same token exchange, DB persistence, and 302 RedirectResponse.
    """
    return oauth_callback(provider=provider, code=code, state=state, db=db)


def purge_crm_data_for_provider(db: Session, workspace_id: str, provider: str) -> None:
    """
    Purge all synced CRM records for a given provider and workspace upon disconnect.
    If no active CRM connection remains for the workspace, clean up all reconciled
    companies, signals, scores, and feed items so zero stale CRM data remains.
    """
    import uuid
    from app.models import (
        CRMAccountDB, CRMOpportunityDB, CRMContactDB, CRMLeadDB, CRMUserDB,
        CRMSyncStateV2, CRMAuditLog, CRMConnectionDB, Company, CompanyScore,
        Signal, IntelligenceFeedItem
    )

    try:
        ws_uuid = uuid.UUID(str(workspace_id))
    except Exception:
        ws_uuid = workspace_id

    # 1. Delete canonical CRM DB records for this provider & workspace
    db.query(CRMAccountDB).filter_by(workspace_id=ws_uuid, provider=provider).delete(synchronize_session=False)
    db.query(CRMOpportunityDB).filter_by(workspace_id=ws_uuid, provider=provider).delete(synchronize_session=False)
    db.query(CRMContactDB).filter_by(workspace_id=ws_uuid, provider=provider).delete(synchronize_session=False)
    db.query(CRMLeadDB).filter_by(workspace_id=ws_uuid, provider=provider).delete(synchronize_session=False)
    db.query(CRMUserDB).filter_by(workspace_id=ws_uuid, provider=provider).delete(synchronize_session=False)
    db.query(CRMSyncStateV2).filter_by(workspace_id=ws_uuid, provider=provider).delete(synchronize_session=False)
    db.query(CRMAuditLog).filter_by(workspace_id=ws_uuid, provider=provider).delete(synchronize_session=False)

    # 2. Check if any active CRM connection remains for this workspace
    active_count = db.query(CRMConnectionDB).filter_by(workspace_id=ws_uuid, is_active=True).count()
    if active_count == 0:
        company_ids = [c.id for c in db.query(Company.id).filter_by(workspace_id=ws_uuid).all()]
        if company_ids:
            db.query(CompanyScore).filter(CompanyScore.company_id.in_(company_ids)).delete(synchronize_session=False)
        db.query(Signal).filter_by(workspace_id=ws_uuid).delete(synchronize_session=False)
        db.query(IntelligenceFeedItem).filter_by(workspace_id=ws_uuid).delete(synchronize_session=False)
        db.query(Company).filter_by(workspace_id=ws_uuid).delete(synchronize_session=False)

    db.commit()


@router.post("/{provider}/disconnect")
def disconnect(provider: str, current_user: CurrentUser, db: Session = Depends(get_db)):
    _ensure_provider(provider)
    connection = (
        db.query(CRMConnectionDB)
        .filter_by(workspace_id=current_user.workspace_id, provider=provider, is_active=True)
        .first()
    )
    crm_provider = CRMFactory.get_provider(provider, connection, db) if connection else CRMProviderRegistry.get(provider)(None, db)
    ok = crm_provider.disconnect(str(current_user.workspace_id), db)

    # Purge all synced CRM records for this provider & workspace
    purge_crm_data_for_provider(db, str(current_user.workspace_id), provider)

    return {"status": "disconnected" if ok else "failed", "provider": provider}



def ensure_workspace_icp_config(db: Session, workspace_id: str):
    """Ensure a workspace has an ICPConfig initialized so scoring & feed generation never skip."""
    import uuid
    from app.models import ICPConfig
    try:
        ws_uuid = uuid.UUID(str(workspace_id))
    except Exception:
        ws_uuid = workspace_id
    icp = db.query(ICPConfig).filter_by(workspace_id=ws_uuid).first()
    if not icp:
        icp = ICPConfig(
            workspace_id=ws_uuid,
            industries=[],
            min_employees=1,
            max_employees=500000,
            locations=[],
            active_score_threshold=0.0,
            watch_score_threshold=0.0,
        )
        db.add(icp)
        db.commit()
        db.refresh(icp)
    return icp


def _run_post_sync_pipeline(db: Session, workspace_id: str):
    """
    Automated post-sync pipeline:
    1. Signal Generation for synced accounts & opportunities
    2. Company Scoring Engine execution
    3. Intelligence Feed Generation
    """
    from datetime import datetime, timezone
    from app.models import Company, Opportunity, Signal, SignalType, SignalSource
    from app.modules.scoring.engine import run_scoring_for_workspace
    from app.modules.intelligence.engine import run_feed_generation_for_workspace
    import uuid

    now = datetime.now(timezone.utc)
    ensure_workspace_icp_config(db, workspace_id)

    try:
        ws_uuid = uuid.UUID(str(workspace_id))
    except Exception:
        ws_uuid = workspace_id

    # The sync_engine now dual-writes directly to Company and Opportunity.
    # We only need to generate Signals.

    companies = db.query(Company).filter(Company.workspace_id == ws_uuid, Company.provider != None).all()
    for company in companies:
        opps = db.query(Opportunity).filter_by(workspace_id=ws_uuid, company_id=company.id).all()
        for opp in opps:
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


    try:
        run_scoring_for_workspace(db, workspace_id)
    except Exception:
        logger.exception("post_sync_scoring_failed", workspace_id=workspace_id, exc_info=True)

    try:
        run_feed_generation_for_workspace(db, workspace_id, force_refresh=True)
    except Exception:
        logger.exception("post_sync_feed_generation_failed", workspace_id=workspace_id, exc_info=True)



@router.post("/sync")
def sync_active_provider(current_user: CurrentUser, db: Session = Depends(get_db)):
    """Force Sync: fetches all records from the connected CRM provider.

    The SOQL sync runs synchronously so the API can return accurate counts.
    The post-sync pipeline (account reconciliation, scoring, feed) is dispatched
    as a background Celery task after the DB session closes to avoid blocking.
    """
    provider = CRMFactory.get_for_workspace(str(current_user.workspace_id), db)
    if not provider:
        raise HTTPException(status_code=404, detail="No active CRM provider for workspace")
    result = CRMSyncEngine(db, provider).run_incremental_sync(force_all=True)
    db.commit()

    # Dispatch post-sync pipeline asynchronously
    try:
        from app.workers.tasks import crm_post_sync_pipeline
        crm_post_sync_pipeline.delay(str(current_user.workspace_id))
    except Exception as exc:
        # If Celery unavailable, run inline as fallback
        logger.warning("crm_post_sync_celery_unavailable_fallback", error=str(exc))
        _run_post_sync_pipeline(db, str(current_user.workspace_id))

    return {
        "success": result.status in (SyncStatus.COMPLETED, "completed"),
        "fetched": result.total_fetched,
        "inserted": result.total_created,
        "updated": result.total_updated,
        "failed": result.total_failed,
        "provider": provider.provider_name,
        "stats": [s.model_dump() for s in result.stats],
        "error": result.error,
    }


@router.post("/{provider}/sync")
def sync_provider(provider: str, current_user: CurrentUser, db: Session = Depends(get_db)):
    """Force Sync for a specific named provider."""
    _ensure_provider(provider)
    connection = (
        db.query(CRMConnectionDB)
        .filter_by(workspace_id=current_user.workspace_id, provider=provider, is_active=True)
        .first()
    )
    if not connection:
        raise HTTPException(status_code=404, detail=f"No active {provider} connection")
    crm_provider = CRMFactory.get_provider(provider, connection, db)
    result = CRMSyncEngine(db, crm_provider).run_incremental_sync(force_all=True)
    db.commit()

    # Dispatch post-sync pipeline asynchronously
    try:
        from app.workers.tasks import crm_post_sync_pipeline
        crm_post_sync_pipeline.delay(str(current_user.workspace_id))
    except Exception as exc:
        logger.warning("crm_post_sync_celery_unavailable_fallback", error=str(exc))
        _run_post_sync_pipeline(db, str(current_user.workspace_id))

    return {
        "success": result.status in (SyncStatus.COMPLETED, "completed"),
        "fetched": result.total_fetched,
        "inserted": result.total_created,
        "updated": result.total_updated,
        "failed": result.total_failed,
        "provider": provider,
        "stats": [s.model_dump() for s in result.stats],
        "error": result.error,
    }


@router.get("/sync/status")
def get_sync_status(current_user: CurrentUser, db: Session = Depends(get_db)):
    """Return per-object sync state for the connected CRM provider.

    The frontend polls this endpoint to show sync progress, last sync time,
    and total records synced per object type.
    """
    from app.models import CRMSyncStateV2

    ws_id = current_user.workspace_id
    connection = (
        db.query(CRMConnectionDB)
        .filter_by(workspace_id=ws_id, is_active=True)
        .first()
    )
    if not connection:
        return {"connected": False, "is_syncing": False, "objects": {}}

    states = (
        db.query(CRMSyncStateV2)
        .filter_by(workspace_id=ws_id, provider=connection.provider)
        .all()
    )

    objects = {}
    for state in states:
        objects[state.object_type] = {
            "last_synced_at": state.last_synced_at.isoformat() if state.last_synced_at else None,
            "last_run_at": state.last_run_at.isoformat() if state.last_run_at else None,
            "last_run_status": state.last_run_status,
            "last_run_created": state.last_run_created,
            "last_run_updated": state.last_run_updated,
            "last_run_error": state.last_run_error,
            "total_synced": state.total_synced,
            "historical_completed": state.historical_import_completed,
        }

    return {
        "connected": True,
        "provider": connection.provider,
        "last_sync_at": connection.last_sync_at.isoformat() if connection.last_sync_at else None,
        "sync_error": connection.sync_error,
        "is_syncing": False,  # Celery task status not directly queryable here; frontend uses polling
        "objects": objects,
    }


@router.get("/analytics")
def get_crm_analytics(current_user: CurrentUser, db: Session = Depends(get_db)):
    """
    Calculates live CRM Analytics directly from canonical tables.
    """
    from app.models import Company, Contact, Lead, Opportunity, CRMUser as CanonicalCRMUser

    ws_id = current_user.workspace_id

    total_accounts = db.query(Company).filter_by(workspace_id=ws_id).count()
    total_contacts = db.query(Contact).filter_by(workspace_id=ws_id).count()
    total_leads = db.query(Lead).filter_by(workspace_id=ws_id).count()
    total_opportunities = db.query(Opportunity).filter_by(workspace_id=ws_id).count()

    opps = db.query(Opportunity).filter_by(workspace_id=ws_id).all()

    pipeline_value = sum((o.amount_usd or 0.0) for o in opps if not o.is_closed_won and not o.is_closed_lost)
    won_revenue = sum((o.amount_usd or 0.0) for o in opps if o.is_closed_won)
    lost_revenue = sum((o.amount_usd or 0.0) for o in opps if o.is_closed_lost)
    
    amounts = [o.amount_usd for o in opps if o.amount_usd and o.amount_usd > 0]
    avg_deal_size = (sum(amounts) / len(amounts)) if amounts else 0.0

    open_count = sum(1 for o in opps if not o.is_closed_won and not o.is_closed_lost)
    won_count = sum(1 for o in opps if o.is_closed_won)
    lost_count = sum(1 for o in opps if o.is_closed_lost)

    # Stage distribution
    stage_map: dict[str, dict] = {}
    for o in opps:
        stage = o.stage or "Unspecified Stage"
        if stage not in stage_map:
            stage_map[stage] = {"stage": stage, "count": 0, "value": 0.0}
        stage_map[stage]["count"] += 1
        stage_map[stage]["value"] += (o.amount_usd or 0.0)

    stage_distribution = sorted(list(stage_map.values()), key=lambda x: x["value"], reverse=True)

    # Owner performance
    users = {u.external_id: (u.name or u.email or u.external_id) for u in db.query(CanonicalCRMUser).filter_by(workspace_id=ws_id).all()}
    owner_map: dict[str, dict] = {}
    for o in opps:
        owner_id = o.external_owner_id or "Unassigned"
        owner_name = users.get(owner_id, owner_id if owner_id != "Unassigned" else "Unassigned Rep")
        if owner_name not in owner_map:
            owner_map[owner_name] = {"owner": owner_name, "count": 0, "total_value": 0.0, "won_value": 0.0}
        owner_map[owner_name]["count"] += 1
        owner_map[owner_name]["total_value"] += (o.amount_usd or 0.0)
        if o.is_closed_won:
            owner_map[owner_name]["won_value"] += (o.amount_usd or 0.0)

    owner_performance = sorted(list(owner_map.values()), key=lambda x: x["total_value"], reverse=True)[:10]

    return {
        "summary": {
            "total_accounts": total_accounts,
            "total_contacts": total_contacts,
            "total_leads": total_leads,
            "total_opportunities": total_opportunities,
            "pipeline_value": pipeline_value,
            "won_revenue": won_revenue,
            "lost_revenue": lost_revenue,
            "avg_deal_size": avg_deal_size,
            "open_count": open_count,
            "won_count": won_count,
            "lost_count": lost_count,
        },
        "stage_distribution": stage_distribution,
        "owner_performance": owner_performance,
    }


@router.post("/{provider}/webhook/{workspace_id}")
async def provider_webhook(
    provider: str,
    workspace_id: str,
    request: Request,
    db: Session = Depends(get_db),
):
    _ensure_provider(provider)
    payload = await request.body()
    headers = dict(request.headers)
    connection = (
        db.query(CRMConnectionDB)
        .filter_by(workspace_id=workspace_id, provider=provider, is_active=True)
        .first()
    )
    if not connection:
        raise HTTPException(status_code=404, detail="No active CRM connection for webhook")
    crm_provider = CRMFactory.get_provider(provider, connection, db)
    if not crm_provider.verify_webhook_signature(payload, headers):
        raise HTTPException(status_code=401, detail="Invalid webhook signature")
    events = crm_provider.handle_webhook(payload, headers)
    return CRMSyncEngine(db, crm_provider).process_events(events)


@router.get("/opportunities")
def list_crm_opportunities(
    current_user: CurrentUser,
    db: Session = Depends(get_db),
    q: str | None = Query(None),
    stage: str | None = Query(None),
    company_id: str | None = Query(None),
    limit: int = Query(500, le=5000),
    offset: int = Query(0),
):
    """List all synced CRM opportunities (deals) for the workspace with search, filtering, and company metadata."""
    from app.models import Opportunity, Company
    ws_id = current_user.workspace_id
    query = db.query(Opportunity, Company.name.label("company_name"), Company.domain.label("company_domain")).outerjoin(
        Company, Opportunity.company_id == Company.id
    ).filter(Opportunity.workspace_id == ws_id)

    if q and q.strip():
        search = f"%{q.strip()}%"
        query = query.filter(
            (Opportunity.name.ilike(search)) |
            (Company.name.ilike(search)) |
            (Opportunity.stage.ilike(search))
        )

    if stage and stage.strip() and stage != "all":
        query = query.filter(Opportunity.stage == stage)

    if company_id and company_id.strip():
        import uuid
        try:
            query = query.filter(Opportunity.company_id == uuid.UUID(company_id))
        except ValueError:
            pass

    total = query.count()
    opps = (
        query
        .order_by(Opportunity.amount_usd.desc().nullslast(), Opportunity.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    return {
        "total": total,
        "opportunities": [
            {
                "id": str(o.Opportunity.id),
                "external_id": o.Opportunity.external_id,
                "name": o.Opportunity.name,
                "stage": o.Opportunity.stage,
                "amount_usd": o.Opportunity.amount_usd,
                "probability": o.Opportunity.probability,
                "close_date": o.Opportunity.close_date.isoformat() if o.Opportunity.close_date else None,
                "created_date": o.Opportunity.created_date.isoformat() if o.Opportunity.created_date else (o.Opportunity.created_at.isoformat() if o.Opportunity.created_at else None),
                "is_closed_won": o.Opportunity.is_closed_won,
                "is_closed_lost": o.Opportunity.is_closed_lost,
                "company_id": str(o.Opportunity.company_id) if o.Opportunity.company_id else None,
                "company_name": o.company_name or "Unassigned",
                "company_domain": o.company_domain or "",
                "provider": o.Opportunity.provider or "salesforce",
                "raw_data": o.Opportunity.raw_data or {},
            }
            for o in opps
        ],
    }


@router.get("/contacts")
def list_crm_contacts(
    current_user: CurrentUser,
    db: Session = Depends(get_db),
    q: str | None = Query(None),
    company_id: str | None = Query(None),
    limit: int = Query(500, le=5000),
    offset: int = Query(0),
):
    """List all synced CRM contacts for the workspace with search and company resolution."""
    from app.models import Contact, Company
    ws_id = current_user.workspace_id
    query = db.query(Contact, Company.name.label("company_name"), Company.domain.label("company_domain")).outerjoin(
        Company, Contact.company_id == Company.id
    ).filter(Contact.workspace_id == ws_id)

    if q and q.strip():
        search = f"%{q.strip()}%"
        query = query.filter(
            (Contact.first_name.ilike(search)) |
            (Contact.last_name.ilike(search)) |
            (Contact.full_name.ilike(search)) |
            (Contact.email.ilike(search)) |
            (Contact.title.ilike(search)) |
            (Company.name.ilike(search))
        )

    if company_id and company_id.strip():
        import uuid
        try:
            query = query.filter(Contact.company_id == uuid.UUID(company_id))
        except ValueError:
            pass

    total = query.count()
    rows = (
        query
        .order_by(Contact.last_name.asc().nullslast(), Contact.first_name.asc().nullslast())
        .offset(offset)
        .limit(limit)
        .all()
    )

    return {
        "total": total,
        "contacts": [
            {
                "id": str(c.Contact.id),
                "external_id": c.Contact.external_id,
                "first_name": c.Contact.first_name,
                "last_name": c.Contact.last_name,
                "full_name": c.Contact.full_name or f"{c.Contact.first_name or ''} {c.Contact.last_name or ''}".strip(),
                "email": c.Contact.email,
                "phone": c.Contact.phone,
                "title": c.Contact.title,
                "department": c.Contact.department,
                "seniority": c.Contact.seniority,
                "company_id": str(c.Contact.company_id) if c.Contact.company_id else None,
                "company_name": c.company_name or "Unassigned",
                "company_domain": c.company_domain or "",
                "synced_at": c.Contact.synced_at.isoformat() if c.Contact.synced_at else None,
                "raw_data": c.Contact.raw_data or {},
            }
            for c in rows
        ],
    }


@router.get("/leads")
def list_crm_leads(
    current_user: CurrentUser,
    db: Session = Depends(get_db),
    q: str | None = Query(None),
    limit: int = Query(500, le=5000),
    offset: int = Query(0),
):
    """List all synced CRM leads for the workspace."""
    from app.models import Lead
    ws_id = current_user.workspace_id
    query = db.query(Lead).filter_by(workspace_id=ws_id)

    if q and q.strip():
        search = f"%{q.strip()}%"
        query = query.filter(
            (Lead.first_name.ilike(search)) |
            (Lead.last_name.ilike(search)) |
            (Lead.full_name.ilike(search)) |
            (Lead.company_name.ilike(search)) |
            (Lead.email.ilike(search)) |
            (Lead.title.ilike(search))
        )

    total = query.count()
    rows = (
        query
        .order_by(Lead.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    return {
        "total": total,
        "leads": [
            {
                "id": str(l.id),
                "external_id": l.external_id,
                "first_name": l.first_name,
                "last_name": l.last_name,
                "full_name": l.full_name or f"{l.first_name or ''} {l.last_name or ''}".strip(),
                "company_name": l.company_name,
                "title": l.title,
                "email": l.email,
                "phone": l.phone,
                "status": (l.raw_data or {}).get("Status", "Open"),
                "source": (l.raw_data or {}).get("LeadSource", "Salesforce"),
                "provider": l.provider or "salesforce",
                "synced_at": l.created_at.isoformat() if l.created_at else None,
                "raw_data": l.raw_data or {},
            }
            for l in rows
        ],
    }


@router.get("/users")
def list_crm_users(
    current_user: CurrentUser,
    db: Session = Depends(get_db),
    q: str | None = Query(None),
    limit: int = Query(500, le=5000),
    offset: int = Query(0),
):
    """List all synced CRM users / owners for the workspace."""
    from app.models import CRMUser, CRMUserDB
    ws_id = current_user.workspace_id

    # Try canonical_crm_users first, fallback to crm_users
    query = db.query(CRMUser).filter_by(workspace_id=ws_id)
    if query.count() == 0:
        query_db = db.query(CRMUserDB).filter_by(workspace_id=ws_id)
        if q and q.strip():
            search = f"%{q.strip()}%"
            query_db = query_db.filter((CRMUserDB.name.ilike(search)) | (CRMUserDB.email.ilike(search)))
        total = query_db.count()
        rows = query_db.offset(offset).limit(limit).all()
        return {
            "total": total,
            "users": [
                {
                    "id": str(u.id),
                    "external_id": u.external_id,
                    "name": u.name,
                    "email": u.email,
                    "provider": u.provider or "salesforce",
                    "is_active": u.is_active,
                    "synced_at": u.synced_at.isoformat() if u.synced_at else None,
                }
                for u in rows
            ],
        }

    if q and q.strip():
        search = f"%{q.strip()}%"
        query = query.filter((CRMUser.name.ilike(search)) | (CRMUser.email.ilike(search)))

    total = query.count()
    rows = query.offset(offset).limit(limit).all()
    return {
        "total": total,
        "users": [
            {
                "id": str(u.id),
                "external_id": u.external_id,
                "name": u.name,
                "email": u.email,
                "provider": u.provider or "salesforce",
                "is_active": u.is_active,
                "synced_at": u.synced_at.isoformat() if u.synced_at else None,
            }
            for u in rows
        ],
    }


