"""
Governance Engine API Routes (Phase 5.5.8)
Exposes endpoints for querying workspace audit logs and compliance reports.
"""
from typing import Any, Dict
from fastapi import APIRouter, Depends

from app.api.auth import AuthenticatedUser, get_current_user
from app.modules.copilot.governance_engine.application.engine import governance_engine

governance_router_api = APIRouter(prefix="", tags=["copilot-governance"])


@governance_router_api.get("/governance/audit-logs", response_model=Dict[str, Any])
async def get_audit_logs(
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    report = governance_engine.generate_report(current_user.workspace_id)

    return {
        "workspace_id": str(report.workspace_id),
        "total_audit_events": report.total_audit_events,
        "compliance_status": report.compliance_status.value,
        "active_policy_rules": report.active_policy_rules,
        "recent_logs": [
            {
                "log_id": log.log_id,
                "action": log.action.value,
                "target": log.target,
                "timestamp": log.timestamp.isoformat(),
                "details": log.details,
            }
            for log in report.recent_logs
        ],
    }
