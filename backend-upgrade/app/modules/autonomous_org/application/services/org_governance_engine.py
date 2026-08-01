"""
Org Governance Engine (Phase 6.6)
Manages workspace operating modes, auto-approval thresholds, and human override gates.
"""
from app.modules.autonomous_org.domain.org_entities import OrgGovernancePolicy


class OrgGovernanceEngine:
    def get_active_policy(self) -> OrgGovernancePolicy:
        return OrgGovernancePolicy(
            auto_approval_threshold_usd=100000.0,
            required_roles_for_overrides=["manager", "admin"],
        )


org_governance_engine = OrgGovernanceEngine()
