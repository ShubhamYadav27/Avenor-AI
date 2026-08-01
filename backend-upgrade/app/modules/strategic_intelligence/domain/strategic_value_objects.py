"""
Strategic Intelligence Value Objects (Phase 6.5 & 6.6)
Domain enums and value objects for Strategic Revenue Intelligence & Executive Advisory Engine.
Zero external framework dependencies.
"""
from enum import Enum


class StrategicPlanningType(str, Enum):
    QUARTERLY_PLANNING = "quarterly_planning"
    ANNUAL_PLANNING = "annual_planning"
    TERRITORY_PLANNING = "territory_planning"
    CAPACITY_PLANNING = "capacity_planning"
    COMPETITIVE_STRATEGY = "competitive_strategy"
    EXPANSION_STRATEGY = "expansion_strategy"


class SystemOperatingState(str, Enum):
    MONITORING = "monitoring"
    PREDICTING = "predicting"
    COORDINATING = "coordinating"
    EXECUTING = "executing"
    LEARNING = "learning"


class ScenarioType(str, Enum):
    HEADCOUNT_CONSTRAINED_GROWTH = "headcount_constrained_growth"
    WIN_RATE_EXPANSION = "win_rate_expansion"
    PRICING_OPTIMIZATION = "pricing_optimization"
    MACRO_HEADWIND = "macro_headwind"
    COMPETITOR_ENTRY = "competitor_entry"


class RiskCategory(str, Enum):
    PIPELINE_SHORTFALL = "pipeline_shortfall"
    HIGH_CHURN_RISK = "high_churn_risk"
    CAPACITY_BOTTLENECK = "capacity_bottleneck"
    TERRITORY_IMBALANCE = "territory_imbalance"
    COMPETITIVE_THREAT = "competitive_threat"


class ExecutiveRole(str, Enum):
    CRO = "cro"
    VP_SALES = "vp_sales"
    REVOPS_LEADER = "revops_leader"
    CEO = "ceo"
    BOARD_MEMBER = "board_member"
