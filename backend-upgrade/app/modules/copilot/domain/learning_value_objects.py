"""
Learning Value Objects (Phase 5.5.6)
Domain enums and value objects for Enterprise Learning & Feedback Engine.
Zero external framework dependencies.
"""
from enum import Enum


class FeedbackType(str, Enum):
    THUMBS_UP = "thumbs_up"
    THUMBS_DOWN = "thumbs_down"
    RATING = "rating"
    TEXT_CORRECTION = "text_correction"
    DEAL_WON = "deal_won"
    DEAL_LOST = "deal_lost"
    SIGNAL_CONVERTED = "signal_converted"


class RewardType(str, Enum):
    EXPLICIT_USER = "explicit_user"
    IMPLICIT_BEHAVIORAL = "implicit_behavioral"
    CRM_OUTCOME = "crm_outcome"


class OptimizationTarget(str, Enum):
    SIGNAL_WEIGHT = "signal_weight"
    TOOL_SELECTION = "tool_selection"
    MEMORY_REINFORCEMENT = "memory_reinforcement"
    PROMPT_STRATEGY = "prompt_strategy"


class DriftStatus(str, Enum):
    STABLE = "stable"
    SLIGHT_DRIFT = "slight_drift"
    SIGNIFICANT_DRIFT = "significant_drift"
