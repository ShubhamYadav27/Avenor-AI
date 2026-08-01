from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any

from app.modules.cross_customer_intelligence.domain.models import SignalType
from app.modules.cross_customer_intelligence.application.services import (
    ConsentManager, PrivacyGuard, PatternDiscoveryEngine, InsightEngine, ConsentRequiredError
)

router = APIRouter(prefix="/v1/collective", tags=["Cross-Customer Intelligence"])

@router.post("/consent/{org_id}")
async def update_consent(org_id: str, payload: Dict[str, Any]) -> dict:
    """Explicitly grant or revoke consent for Collective Intelligence."""
    is_opted_in = payload.get("is_opted_in", False)
    user_id = payload.get("audit_user_id", "system")
    
    status = ConsentManager.set_consent(org_id, is_opted_in, user_id)
    return {
        "organization_id": status.organization_id,
        "is_opted_in": status.is_opted_in,
        "updated_at": status.updated_at.isoformat()
    }

@router.post("/signals/ingest")
async def ingest_raw_signal(payload: Dict[str, Any]) -> dict:
    """
    Attempt to ingest a raw signal. 
    If consent is granted, it is anonymized and stored.
    If consent is missing, it throws a 403 Forbidden.
    """
    org_id = payload.get("org_id")
    cohort = payload.get("cohort_name")
    signal_type = SignalType(payload.get("signal_type"))
    raw_value = payload.get("raw_value")
    
    try:
        # PrivacyGuard completely strips org_id and buckets the raw_value
        anon_signal = PrivacyGuard.anonymize_signal(org_id, cohort, signal_type, raw_value)
        return {
            "status": "anonymized_and_ingested",
            "anonymous_id": anon_signal.id,
            "cohort": anon_signal.anonymized_cohort_id,
            "bucket": anon_signal.bucketed_value.value
        }
    except ConsentRequiredError as e:
        raise HTTPException(status_code=403, detail=str(e))

@router.get("/insights")
async def get_collective_insights() -> dict:
    """Fetch all discovered global patterns and their AI Insights."""
    # In reality, fetches from the materialized pattern cache
    patterns = PatternDiscoveryEngine.discover_patterns([])
    
    insights = []
    for p in patterns:
        insight = InsightEngine.generate_insight(p)
        insights.append({
            "insight_id": insight.id,
            "message": insight.message,
            "confidence": f"{insight.confidence_score * 100}%",
            "evidence_base": f"{p.occurrence_count} organizations"
        })
        
    return {"insights": insights}
