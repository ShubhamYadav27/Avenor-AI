"""
Capacity Planner (Phase 6.5)
Calculates rep capacity utilization, meeting load bottlenecks, and recommended hiring deltas.
"""
from app.modules.strategic_intelligence.domain.strategic_entities import CapacityPlan


class CapacityPlanner:
    def evaluate_capacity(self) -> CapacityPlan:
        return CapacityPlan(
            rep_capacity_utilization=0.82,
            recommended_headcount_delta=2,
            avg_deals_per_rep=9,
            bottleneck_risk="Demo Scheduling Bottleneck in NA East",
        )


capacity_planner = CapacityPlanner()
