import uuid
import pytest

from app.modules.revenue_os.application.coordinators.executive_coordination_engine import executive_coordination_engine
from app.modules.revenue_os.application.coordinators.intelligence_coordinator import intelligence_coordinator
from app.modules.revenue_os.application.engine import revenue_os_engine
from app.modules.revenue_os.application.kernel.revenue_os_kernel import revenue_os_kernel
from app.modules.revenue_os.application.managers.capability_manager import capability_manager
from app.modules.revenue_os.application.managers.policy_manager import policy_manager
from app.modules.revenue_os.domain.revenue_os_entities import OperatingPackage
from app.modules.revenue_os.domain.revenue_os_value_objects import CapabilityStatus, OperatingMode, PolicyLevel


@pytest.fixture
def anyio_backend():
    return "asyncio"


def test_revenue_os_kernel():
    ws_id = uuid.uuid4()
    state = revenue_os_kernel.get_kernel_state(ws_id)
    assert state.global_health_index == 87.0
    assert state.active_agents_count == 18


def test_intelligence_coordinator():
    health = intelligence_coordinator.get_subsystem_health()
    assert len(health) == 10
    assert "operational" in health["context_engine"]


def test_executive_coordination_engine():
    ws_id = uuid.uuid4()
    cmd = executive_coordination_engine.generate_command_center_snapshot(ws_id)
    insights = executive_coordination_engine.get_executive_insights()

    assert cmd.title == "CEO & CRO Executive Command Center"
    assert "Overall Revenue Org Health is 87%" in cmd.ceo_dashboard_summary
    assert len(insights) == 3


def test_capability_manager():
    caps = capability_manager.get_capabilities()
    bottlenecks = capability_manager.get_capability_health()

    assert len(caps) == 4
    assert caps[0].status == CapabilityStatus.OPTIMAL
    assert len(bottlenecks) == 1


def test_policy_manager():
    policy = policy_manager.get_active_policy()
    assert policy.policy_level == PolicyLevel.BALANCED
    assert policy.auto_approval_threshold_usd == 100000.0


@pytest.mark.anyio
async def test_revenue_os_engine_e2e():
    ws_id = uuid.uuid4()
    pkg = await revenue_os_engine.get_operating_system_status(ws_id)

    assert isinstance(pkg, OperatingPackage)
    assert pkg.org_state.operating_mode == OperatingMode.HYBRID_GOVERNED
    assert len(pkg.capabilities) == 4
    assert len(pkg.insights) == 3
    assert pkg.health_metrics.rep_productivity_index == 88.5

    updated_pkg = await revenue_os_engine.update_operating_mode(ws_id, "fully_autonomous")
    assert updated_pkg.org_state.operating_mode == OperatingMode.FULLY_AUTONOMOUS
