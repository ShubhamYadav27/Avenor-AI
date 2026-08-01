import uuid
import pytest

from app.modules.autonomous_org.application.service import autonomous_org_service
from app.modules.autonomous_org.application.services.org_governance_engine import org_governance_engine
from app.modules.autonomous_org.application.services.org_health_monitor import org_health_monitor
from app.modules.autonomous_org.application.services.org_orchestrator import org_orchestrator
from app.modules.autonomous_org.domain.org_entities import AutonomousOrgPlatformPackage
from app.modules.autonomous_org.domain.org_value_objects import OrgHealthTier, OrgOperatingMode


@pytest.fixture
def anyio_backend():
    return "asyncio"


def test_org_orchestrator():
    ws_id = uuid.uuid4()
    state = org_orchestrator.get_org_state(ws_id)
    assert state.operating_mode == OrgOperatingMode.HYBRID_GOVERNED
    assert state.active_agents_count == 18


def test_org_health_monitor():
    health = org_health_monitor.evaluate_health()
    assert health.health_tier == OrgHealthTier.HEALTHY
    assert health.rep_productivity_index == 88.5


def test_org_governance_engine():
    policy = org_governance_engine.get_active_policy()
    assert policy.auto_approval_threshold_usd == 100000.0
    assert "manager" in policy.required_roles_for_overrides


@pytest.mark.anyio
async def test_autonomous_org_service_e2e():
    ws_id = uuid.uuid4()
    pkg = await autonomous_org_service.get_platform_status(ws_id)

    assert isinstance(pkg, AutonomousOrgPlatformPackage)
    assert pkg.org_state.operating_mode == OrgOperatingMode.HYBRID_GOVERNED
    assert pkg.health_metrics.health_tier == OrgHealthTier.HEALTHY

    updated_pkg = await autonomous_org_service.update_operating_mode(ws_id, "fully_autonomous")
    assert updated_pkg.org_state.operating_mode == OrgOperatingMode.FULLY_AUTONOMOUS
