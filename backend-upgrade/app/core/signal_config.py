"""
Signal weight defaults and decay configuration.
Uses plain string literals for signal types to avoid circular imports.
The string values match SignalType enum values defined in app.models.
"""

# ── Base weights (prior, before learning) ─────────────────────
DEFAULT_SIGNAL_WEIGHTS: dict[str, float] = {
    "funding": 0.35,
    "hiring": 0.28,
    "leadership_change": 0.22,
    "tech_change": 0.20,
    "intent": 0.18,
    "expansion": 0.12,
    "product_launch": 0.10,
    "news": 0.06,
}

# ── Decay half-life in days ────────────────────────────────────
SIGNAL_HALF_LIFE_DAYS: dict[str, int] = {
    "funding": 90,
    "hiring": 30,
    "leadership_change": 60,
    "tech_change": 60,
    "intent": 14,
    "expansion": 45,
    "product_launch": 30,
    "news": 21,
}

# ── ICP match multipliers ──────────────────────────────────────
ICP_MULTIPLIER_FULL: float = 1.5
ICP_MULTIPLIER_PARTIAL: float = 1.0
ICP_MULTIPLIER_WEAK: float = 0.3

# ── Buying window thresholds ───────────────────────────────────
BUYING_WINDOW_HOT_THRESHOLD: float = 0.65
BUYING_WINDOW_WARM_THRESHOLD: float = 0.45
BUYING_WINDOW_WATCH_THRESHOLD: float = 0.25

# ── Signal combination bonuses ─────────────────────────────────
# frozenset of string signal type values → bonus added to composite score
COMBINATION_BONUSES: dict[frozenset, float] = {
    frozenset(["funding", "hiring"]): 0.15,
    frozenset(["leadership_change", "hiring"]): 0.12,
    frozenset(["funding", "tech_change"]): 0.10,
    frozenset(["intent", "hiring"]): 0.10,
    frozenset(["funding", "leadership_change"]): 0.08,
}
