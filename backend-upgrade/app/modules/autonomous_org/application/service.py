"""
Autonomous Org Service (Phase 6.6)
Coordinates AutonomousOrgOrchestrator -> OrgHealthMonitor -> OrgGovernanceEngine -> AutonomousOrgPlatformPackage.
Zero DB ORM coupling.
"""
import time
import uuid

from app.modules.autonomous_org.application.services.org_governance_engine import org_governance_engine
from app.modules.autonomous_org.application.services.org_health_monitor import org_health_monitor
from app.modules.autonomous_org.application.services.org_orchestrator import org_orchestrator
from app.modules.autonomous_org.domain.org_entities import AutonomousOrgPlatformPackage
from app.modules.autonomous_org.domain.org_value_objects import OrgOperatingMode


class AutonomousOrgService:
    async def get_platform_status(self, workspace_id: uuid.UUID) -> AutonomousOrgPlatformPackage:
        t0 = time.perf_counter()

        state = org_orchestrator.get_org_state(workspace_id)
        health = org_health_monitor.evaluate_health()
        policy = org_governance_engine.get_active_policy()

        total_lat = (time.perf_counter() - t0) * 1000.0

        return AutonomousOrgPlatformPackage(
            workspace_id=workspace_id,
            org_state=state,
            health_metrics=health,
            active_policy=policy,
            ai_partner_status="Avenor Autonomous Revenue Organization Operating System Active & Self-Governing",
            execution_time_ms=round(total_lat, 2),
        )

    async def update_operating_mode(self, workspace_id: uuid.UUID, mode: str) -> AutonomousOrgPlatformPackage:
        pkg = await self.get_platform_status(workspace_id)
        try:
            pkg.org_state.operating_mode = OrgOperatingMode(mode)
        except ValueError:
            pass
        return pkg


autonomous_org_service = AutonomousOrgService()
