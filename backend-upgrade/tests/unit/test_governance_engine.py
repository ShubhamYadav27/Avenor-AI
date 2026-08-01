import uuid

from app.modules.copilot.domain.governance_entities import GovernanceReport
from app.modules.copilot.domain.governance_value_objects import AuditAction, ComplianceStatus, UserRole
from app.modules.copilot.governance_engine.application.engine import governance_engine
from app.modules.copilot.governance_engine.logging.audit_logger import audit_trail_logger
from app.modules.copilot.governance_engine.security.rbac_manager import rbac_manager


def test_rbac_manager_permissions():
    assert rbac_manager.check_permission(UserRole.ADMIN, AuditAction.WORKFLOW_TRIGGER) is True
    assert rbac_manager.check_permission(UserRole.MANAGER, AuditAction.WORKFLOW_TRIGGER) is True
    assert rbac_manager.check_permission(UserRole.SALES_REP, AuditAction.WORKFLOW_TRIGGER) is False
    assert rbac_manager.check_permission(UserRole.SALES_REP, AuditAction.TOOL_EXECUTION) is True


def test_audit_trail_logger():
    ws_id = uuid.uuid4()
    entry = audit_trail_logger.log_action(
        workspace_id=ws_id,
        action=AuditAction.TOOL_EXECUTION,
        target="CrmTool",
        details={"query": "Get deals"},
    )

    assert entry.log_id.startswith("audit-")
    assert entry.target == "CrmTool"

    logs = audit_trail_logger.get_workspace_logs(ws_id)
    assert len(logs) >= 1
    assert logs[-1] == entry


def test_governance_engine_validation_and_report():
    ws_id = uuid.uuid4()

    # Allowed Action
    allowed, entry = governance_engine.validate_and_log_action(
        workspace_id=ws_id,
        role=UserRole.MANAGER,
        action=AuditAction.WORKFLOW_TRIGGER,
        target="meeting_prep",
    )
    assert allowed is True
    assert entry is not None

    # Denied Action
    denied, entry_denied = governance_engine.validate_and_log_action(
        workspace_id=ws_id,
        role=UserRole.ANALYST,
        action=AuditAction.WORKFLOW_TRIGGER,
        target="meeting_prep",
    )
    assert denied is False
    assert entry_denied is None

    report = governance_engine.generate_report(ws_id)
    assert isinstance(report, GovernanceReport)
    assert report.total_audit_events >= 2
    assert report.compliance_status == ComplianceStatus.COMPLIANT
