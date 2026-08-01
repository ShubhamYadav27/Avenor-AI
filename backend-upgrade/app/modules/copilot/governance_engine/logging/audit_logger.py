"""
Audit Trail Logger (Phase 5.5.8)
Maintains an immutable in-memory audit log record for workspace compliance and explainability.
"""
from typing import Dict, List, Optional
import uuid

from app.modules.copilot.domain.governance_entities import AuditLogEntry
from app.modules.copilot.domain.governance_value_objects import AuditAction


class AuditTrailLogger:
    def __init__(self):
        self._log_store: List[AuditLogEntry] = []

    def log_action(
        self,
        workspace_id: uuid.UUID,
        action: AuditAction,
        target: str,
        user_id: Optional[uuid.UUID] = None,
        details: Optional[Dict[str, str]] = None,
    ) -> AuditLogEntry:
        entry = AuditLogEntry(
            workspace_id=workspace_id,
            user_id=user_id,
            action=action,
            target=target,
            details=details or {},
        )
        self._log_store.append(entry)
        return entry

    def get_workspace_logs(self, workspace_id: uuid.UUID, limit: int = 50) -> List[AuditLogEntry]:
        logs = [e for e in self._log_store if e.workspace_id == workspace_id]
        return logs[-limit:]


audit_trail_logger = AuditTrailLogger()
