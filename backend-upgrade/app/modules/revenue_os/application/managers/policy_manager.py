"""
Revenue Policy Manager (Phase 6.6)
Manages enterprise-wide governance policies and auto-approval thresholds.
"""
from app.modules.revenue_os.domain.revenue_os_entities import RevenuePolicy
from app.modules.revenue_os.domain.revenue_os_value_objects import PolicyLevel


class RevenuePolicyManager:
    def get_active_policy(self) -> RevenuePolicy:
        return RevenuePolicy(
            policy_level=PolicyLevel.BALANCED,
            auto_approval_threshold_usd=100000.0,
            required_roles=["manager", "admin"],
        )


policy_manager = RevenuePolicyManager()
