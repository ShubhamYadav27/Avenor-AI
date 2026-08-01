"""
Analytics Value Objects (Phase 5.6)
Domain enums and value objects for Enterprise Real-Time Revenue Intelligence & Analytics Engine.
Zero external framework dependencies.
"""
from enum import Enum


class ForecastCategory(str, Enum):
    PIPELINE = "pipeline"
    BEST_CASE = "best_case"
    COMMIT = "commit"
    CLOSED_WON = "closed_won"


class HeatmapTier(str, Enum):
    HIGH_SURGE = "high_surge"
    MODERATE_SURGE = "moderate_surge"
    LOW_SURGE = "low_surge"
    NEUTRAL = "neutral"
