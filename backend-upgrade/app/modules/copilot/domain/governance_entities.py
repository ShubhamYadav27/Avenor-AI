"""
Governance Entities (Phase 5.5.8)
Pure domain entities representing immutable audit logs, RBAC permissions, and compliance reports.
"""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Optional
import uuid

from app.modules.copilot.domain.governance_value_objects import AuditAction, ComplianceStatus, UserRole


@dataclass
class AuditLogEntry:
    log_id: str = field(default_factory=lambda: f"audit-{uuid.uuid4().hex[:12]}")
    workspace_id: uuid.UUID = field(default_factory=uuid.uuid4)
    user_id: Optional[uuid.UUID] = None
    action: AuditAction = AuditAction.TOOL_EXECUTION
    target: str = ""
    details: Dict[str, str] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class AccessPermission:
    role: UserRole
    allowed_actions: List[AuditAction] = field(default_factory=list)
    can_execute_workflows: bool = True
    can_access_memories: bool = True


@dataclass
class GovernanceReport:
    workspace_id: uuid.UUID
    total_audit_events: int = 0
    compliance_status: ComplianceStatus = ComplianceStatus.COMPLIANT
    active_policy_rules: List[str] = field(default_factory=list)
    recent_logs: List[AuditLogEntry] = field(default_factory=list)
