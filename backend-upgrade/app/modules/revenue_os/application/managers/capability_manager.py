"""
Capability Manager (Phase 6.6)
Evaluates revenue operational readiness, sales process maturity, and capability health.
"""
from typing import List

from app.modules.revenue_os.domain.revenue_os_entities import CapabilityHealth, RevenueCapability
from app.modules.revenue_os.domain.revenue_os_value_objects import CapabilityStatus


class CapabilityManager:
    def get_capabilities(self) -> List[RevenueCapability]:
        return [
            RevenueCapability(name="Predictive Intelligence & Decisioning", status=CapabilityStatus.OPTIMAL, health_index=94.0, readiness_score=96.0),
            RevenueCapability(name="Autonomous RevOps Execution", status=CapabilityStatus.OPERATIONAL, health_index=88.0, readiness_score=90.0),
            RevenueCapability(name="Knowledge Graph Traversal", status=CapabilityStatus.OPTIMAL, health_index=92.0, readiness_score=95.0),
            RevenueCapability(name="Sales Capacity & Scheduling", status=CapabilityStatus.BOTTLENECKED, health_index=72.0, readiness_score=78.0),
        ]

    def get_capability_health(self) -> List[CapabilityHealth]:
        return [
            CapabilityHealth(capability_name="Sales Capacity & Scheduling", status=CapabilityStatus.BOTTLENECKED, health_score=72.0, bottleneck_notes="Demo scheduling bottleneck in NA East; AI Workflows deployed.")
        ]


capability_manager = CapabilityManager()
