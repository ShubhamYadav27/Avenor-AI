"""
RBAC Manager (Phase 5.5.8)
Enforces Role-Based Access Control permissions across tools, memories, workflows, and swarm executions.
"""
from typing import Dict

from app.modules.copilot.domain.governance_entities import AccessPermission
from app.modules.copilot.domain.governance_value_objects import AuditAction, UserRole


class RBACManager:
    def __init__(self):
        self._role_permissions: Dict[UserRole, AccessPermission] = {
            UserRole.ADMIN: AccessPermission(
                role=UserRole.ADMIN,
                allowed_actions=list(AuditAction),
                can_execute_workflows=True,
                can_access_memories=True,
            ),
            UserRole.MANAGER: AccessPermission(
                role=UserRole.MANAGER,
                allowed_actions=[AuditAction.TOOL_EXECUTION, AuditAction.MEMORY_ACCESS, AuditAction.WORKFLOW_TRIGGER, AuditAction.SWARM_RUN, AuditAction.FEEDBACK_SUBMIT],
                can_execute_workflows=True,
                can_access_memories=True,
            ),
            UserRole.SALES_REP: AccessPermission(
                role=UserRole.SALES_REP,
                allowed_actions=[AuditAction.TOOL_EXECUTION, AuditAction.MEMORY_ACCESS, AuditAction.FEEDBACK_SUBMIT],
                can_execute_workflows=False,
                can_access_memories=True,
            ),
            UserRole.ANALYST: AccessPermission(
                role=UserRole.ANALYST,
                allowed_actions=[AuditAction.TOOL_EXECUTION, AuditAction.MEMORY_ACCESS],
                can_execute_workflows=False,
                can_access_memories=True,
            ),
        }

    def check_permission(self, role: UserRole, action: AuditAction) -> bool:
        perm = self._role_permissions.get(role)
        if not perm:
            return False
        return action in perm.allowed_actions


rbac_manager = RBACManager()
