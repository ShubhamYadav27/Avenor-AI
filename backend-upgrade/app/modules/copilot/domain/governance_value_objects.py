"""
Governance Value Objects (Phase 5.5.8)
Domain enums and value objects for Enterprise Integration & Governance Platform.
Zero external framework dependencies.
"""
from enum import Enum


class UserRole(str, Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    SALES_REP = "sales_rep"
    ANALYST = "analyst"


class AuditAction(str, Enum):
    TOOL_EXECUTION = "tool_execution"
    MEMORY_ACCESS = "memory_access"
    WORKFLOW_TRIGGER = "workflow_trigger"
    SWARM_RUN = "swarm_run"
    FEEDBACK_SUBMIT = "feedback_submit"


class ComplianceStatus(str, Enum):
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    AUDIT_FLAGGED = "audit_flagged"
