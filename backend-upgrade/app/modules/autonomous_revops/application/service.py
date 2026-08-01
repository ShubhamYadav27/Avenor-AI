"""
Autonomous RevOps Service (Phase 6.3)
Delegates to AutonomousRevOpsEngine.
"""
import uuid

from app.modules.autonomous_revops.application.engine import autonomous_revops_engine
from app.modules.autonomous_revops.domain.revops_entities import RevOpsPackage


class AutonomousRevOpsService:
    async def execute_operations(self, workspace_id: uuid.UUID, company_id: str) -> RevOpsPackage:
        return await autonomous_revops_engine.plan_and_execute_mission(
            workspace_id=workspace_id,
            mission_type="pipeline_optimization",
            target_company_ids=[company_id],
        )


autonomous_revops_service = AutonomousRevOpsService()
