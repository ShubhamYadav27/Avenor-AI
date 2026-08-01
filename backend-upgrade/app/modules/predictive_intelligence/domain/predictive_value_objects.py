"""
Predictive Value Objects (Phase 6.1)
Domain enums and value objects for Enterprise Predictive Revenue Intelligence Engine.
Zero external framework dependencies.
"""
from enum import Enum


class BuyingWindowStage(str, Enum):
    EARLY_SIGNAL = "early_signal"
    ACTIVE_WINDOW = "active_window"
    PEAK_SURGE = "peak_surge"
    CLOSING_WINDOW = "closing_window"


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class PredictionCategory(str, Enum):
    BUYING_WINDOW = "buying_window"
    WIN_PROBABILITY = "win_probability"
    CHURN_RISK = "churn_risk"
    EXPANSION_OPPORTUNITY = "expansion_opportunity"
