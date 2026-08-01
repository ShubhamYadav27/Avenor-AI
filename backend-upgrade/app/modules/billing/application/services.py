import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime

from app.modules.billing.domain.models import (
    SubscriptionTier, Subscription, Entitlement, UsageRecord, Invoice, InvoiceLineItem, InvoiceStatus
)

# Mocked configurations mapping Tiers to Entitlements
_PLAN_ENTITLEMENTS = {
    SubscriptionTier.FREE: {
        "max_agents": Entitlement("max_agents", max_limit=1),
        "api_access": Entitlement("api_access", has_access=False)
    },
    SubscriptionTier.PROFESSIONAL: {
        "max_agents": Entitlement("max_agents", max_limit=5),
        "api_access": Entitlement("api_access", has_access=True)
    }
}

class UsageTracker:
    """Aggregates telemetry emitted by the platform."""
    
    _ledger: List[UsageRecord] = []
    
    @classmethod
    def record_usage(cls, org_id: str, metric_name: str, value: float) -> UsageRecord:
        record = UsageRecord(
            id=f"usg_{uuid.uuid4().hex[:8]}",
            org_id=org_id,
            metric_name=metric_name,
            value=value
        )
        cls._ledger.append(record)
        return record
        
    @classmethod
    def get_current_usage(cls, org_id: str, metric_name: str) -> float:
        """Calculate total usage for current billing cycle (mocked as all-time here)."""
        return sum(r.value for r in cls._ledger if r.org_id == org_id and r.metric_name == metric_name)

class EntitlementEngine:
    """Evaluates if an Organization is authorized to use a feature."""
    
    @staticmethod
    def can_access_feature(sub: Subscription, feature_name: str) -> bool:
        """Evaluates pure boolean feature locks."""
        entitlements = _PLAN_ENTITLEMENTS.get(sub.tier, {})
        entitlement = entitlements.get(feature_name)
        if not entitlement:
            return False
        return entitlement.has_access

    @staticmethod
    def can_provision_resource(sub: Subscription, feature_name: str, requested_amount: int = 1) -> bool:
        """Evaluates numerical quota locks against current usage."""
        entitlements = _PLAN_ENTITLEMENTS.get(sub.tier, {})
        entitlement = entitlements.get(feature_name)
        
        if not entitlement or not entitlement.has_access:
            return False
            
        if entitlement.max_limit is None: # Unlimited
            return True
            
        current_usage = UsageTracker.get_current_usage(sub.org_id, feature_name)
        if current_usage + requested_amount > entitlement.max_limit:
            return False
            
        return True

class InvoiceEngine:
    """Calculates billing cycles."""
    
    @staticmethod
    def generate_invoice(sub: Subscription) -> Invoice:
        # Base Plan logic
        base_price = 0.0
        if sub.tier == SubscriptionTier.PROFESSIONAL:
            base_price = 299.0
            
        line_items = [
            InvoiceLineItem(description=f"{sub.tier.value.title()} Base Plan", quantity=1, unit_amount=base_price, total=base_price)
        ]
        
        # Metered Usage logic (e.g. LLM tokens overage)
        llm_usage = UsageTracker.get_current_usage(sub.org_id, "llm_tokens")
        if llm_usage > 0:
            token_price = 0.02 # $0.02 per 1k tokens
            token_cost = (llm_usage / 1000) * token_price
            line_items.append(
                InvoiceLineItem(description="LLM Token Usage (per 1k)", quantity=llm_usage/1000, unit_amount=token_price, total=token_cost)
            )
            
        total_due = sum(li.total for li in line_items)
        
        return Invoice(
            id=f"inv_{uuid.uuid4().hex[:8]}",
            org_id=sub.org_id,
            status=InvoiceStatus.DRAFT,
            line_items=line_items,
            amount_due=total_due
        )
