from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from datetime import datetime, timedelta

from app.modules.billing.domain.models import Subscription, SubscriptionTier
from app.modules.billing.application.services import EntitlementEngine, UsageTracker, InvoiceEngine

router = APIRouter(prefix="/v1/billing", tags=["Enterprise Billing Platform"])

# Pre-seed for demonstration
_subscriptions_db = {
    "org_1": Subscription(
        id="sub_1", 
        org_id="org_1", 
        tier=SubscriptionTier.FREE,
        current_period_start=datetime.utcnow(),
        current_period_end=datetime.utcnow() + timedelta(days=30)
    ),
    "org_2": Subscription(
        id="sub_2", 
        org_id="org_2", 
        tier=SubscriptionTier.PROFESSIONAL,
        current_period_start=datetime.utcnow(),
        current_period_end=datetime.utcnow() + timedelta(days=30)
    )
}

@router.post("/entitlements/evaluate")
async def evaluate_entitlement(payload: Dict[str, Any]) -> dict:
    """Evaluate if an Organization has the rights to perform an action based on their Subscription."""
    org_id = payload.get("org_id")
    feature = payload.get("feature")
    requested_amount = payload.get("requested_amount", 1)
    
    sub = _subscriptions_db.get(org_id)
    if not sub:
        raise HTTPException(status_code=404, detail="Subscription not found")
        
    is_allowed = EntitlementEngine.can_provision_resource(sub, feature, requested_amount)
    
    if not is_allowed:
        raise HTTPException(status_code=402, detail=f"Upgrade required: Entitlement '{feature}' limit reached or not included in plan.")
        
    return {"granted": True}

@router.post("/usage")
async def report_usage(payload: Dict[str, Any]) -> dict:
    """Internal API for platform services to report metered consumption."""
    org_id = payload.get("org_id")
    metric = payload.get("metric_name")
    value = payload.get("value")
    
    record = UsageTracker.record_usage(org_id, metric, float(value))
    return {"status": "recorded", "id": record.id}

@router.get("/invoices/preview")
async def preview_invoice(org_id: str) -> dict:
    """Generate a preview of the upcoming invoice including base tier and usage overages."""
    sub = _subscriptions_db.get(org_id)
    if not sub:
        raise HTTPException(status_code=404, detail="Subscription not found")
        
    invoice = InvoiceEngine.generate_invoice(sub)
    
    return {
        "id": invoice.id,
        "status": invoice.status.value,
        "amount_due": invoice.amount_due,
        "line_items": [
            {"description": li.description, "quantity": li.quantity, "total": li.total}
            for li in invoice.line_items
        ]
    }
