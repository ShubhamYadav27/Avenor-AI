"""
Unit tests for the scoring engine.
Tests pure functions only — no database required.
"""
import math
from datetime import datetime, timezone, timedelta
import pytest
from types import SimpleNamespace

from app.core.signal_config import DEFAULT_SIGNAL_WEIGHTS
from app.models import (
    Company, Signal, ICPConfig, SignalType, SignalSource,
    BuyingWindowLabel, CompanyStatus,
)
from app.modules.scoring.engine import (
    compute_icp_match,
    apply_decay,
    compute_combination_bonus,
    compute_buying_window,
    score_company,
)


# ── Fixtures ──────────────────────────────────────────────────

def make_company(**kwargs) -> SimpleNamespace:
    """Use SimpleNamespace so attribute access returns real values, not MagicMocks."""
    defaults = dict(
        id="00000000-0000-0000-0000-000000000001",
        workspace_id="00000000-0000-0000-0000-000000000099",
        name="Veridian Labs",
        domain="veridian.io",
        industry="SaaS",
        employee_count=150,
        location_city="San Francisco",
        location_state="CA",
        location_country="United States",
        technologies=["Snowflake", "Airflow"],
        last_funding_stage="Series A",
        composite_score=0.0,
        icp_score=0.0,
        signal_score=0.0,
        status=CompanyStatus.MONITORING,
        buying_window=BuyingWindowLabel.COLD,
        buying_window_confidence=0.0,
        funding_total_usd=12_000_000,
    )
    defaults.update(kwargs)
    return SimpleNamespace(**defaults)


def make_icp(**kwargs) -> SimpleNamespace:
    defaults = dict(
        industries=["SaaS", "FinTech"],
        min_employees=50,
        max_employees=500,
        locations=["United States", "United Kingdom"],
        technologies=["Snowflake", "Databricks"],
        funding_stages=[],
        customer_personas=["VP of Engineering", "Head of Data"],
        key_pain_points=["data pipeline scaling"],
        product_name="DataFlow",
        product_description="A data pipeline platform for growing teams.",
        active_score_threshold=0.60,
        watch_score_threshold=0.30,
    )
    defaults.update(kwargs)
    return SimpleNamespace(**defaults)


def make_signal(
    signal_type=SignalType.HIRING,
    age_days=3,
    base_strength=0.28,
) -> SimpleNamespace:
    return SimpleNamespace(
        id="00000000-0000-0000-0000-000000000002",
        signal_type=signal_type.value if hasattr(signal_type, 'value') else signal_type,
        base_strength=base_strength,
        decayed_strength=base_strength,
        detected_at=datetime.now(timezone.utc) - timedelta(days=age_days),
        title=f"Test {signal_type} signal",
        description="Test description",
    )


# ── ICP match tests ───────────────────────────────────────────

class TestICPMatch:
    def test_full_match_returns_full_multiplier(self):
        company = make_company()
        icp = make_icp()
        multiplier, breakdown = compute_icp_match(company, icp)
        assert multiplier >= 1.5
        assert breakdown["industry_match"] is True
        assert breakdown["size_match"] is True
        assert breakdown["location_match"] is True

    def test_partial_match_two_of_three(self):
        # Wrong industry, right size and location
        company = make_company(industry="Healthcare", location_country="United States")
        icp = make_icp()
        multiplier, breakdown = compute_icp_match(company, icp)
        assert breakdown["industry_match"] is False
        assert 0.9 <= multiplier <= 1.1  # partial range

    def test_no_match_returns_weak_multiplier(self):
        company = make_company(
            industry="Government",
            employee_count=5000,
            location_country="China",
        )
        icp = make_icp()
        multiplier, breakdown = compute_icp_match(company, icp)
        assert multiplier <= 0.35

    def test_tech_overlap_adds_bonus(self):
        company = make_company(technologies=["Snowflake", "Databricks", "Airflow"])
        icp = make_icp(technologies=["Snowflake", "Databricks"])
        multiplier_with_tech, _ = compute_icp_match(company, icp)

        company_no_tech = make_company(technologies=[])
        multiplier_no_tech, _ = compute_icp_match(company_no_tech, icp)

        assert multiplier_with_tech > multiplier_no_tech

    def test_no_industry_filter_passes_all(self):
        company = make_company(industry="Anything at all")
        icp = make_icp(industries=[])
        _, breakdown = compute_icp_match(company, icp)
        assert breakdown["industry_match"] is True

    def test_employee_count_boundaries(self):
        icp = make_icp(min_employees=50, max_employees=500)
        assert compute_icp_match(make_company(employee_count=49), icp)[1]["size_match"] is False
        assert compute_icp_match(make_company(employee_count=50), icp)[1]["size_match"] is True
        assert compute_icp_match(make_company(employee_count=500), icp)[1]["size_match"] is True
        assert compute_icp_match(make_company(employee_count=501), icp)[1]["size_match"] is False


# ── Decay tests ────────────────────────────────────────────────

class TestSignalDecay:
    def test_fresh_signal_retains_most_strength(self):
        sig = make_signal(SignalType.FUNDING, age_days=0)
        decayed = apply_decay(sig, DEFAULT_SIGNAL_WEIGHTS)
        assert decayed >= 0.30  # should be close to 0.35

    def test_old_signal_decays_significantly(self):
        sig = make_signal(SignalType.HIRING, age_days=90)
        decayed = apply_decay(sig, DEFAULT_SIGNAL_WEIGHTS)
        # Half-life is 30 days → 3 half-lives → 12.5% remaining
        assert decayed < 0.28 * 0.15

    def test_funding_decays_slower_than_hiring(self):
        funding = make_signal(SignalType.FUNDING, age_days=30)
        hiring = make_signal(SignalType.HIRING, age_days=30)
        fd = apply_decay(funding, DEFAULT_SIGNAL_WEIGHTS)
        hd = apply_decay(hiring, DEFAULT_SIGNAL_WEIGHTS)
        # Funding has 90-day half-life vs 30-day for hiring
        # At 30 days: funding retains 70%, hiring retains 50%
        assert fd > hd

    def test_custom_weights_override_defaults(self):
        sig = make_signal(SignalType.HIRING, age_days=0)
        custom_weights = {SignalType.HIRING: 0.50}
        decayed = apply_decay(sig, custom_weights)
        assert decayed >= 0.45  # close to 0.50 at age 0

    def test_decay_is_never_negative(self):
        sig = make_signal(SignalType.NEWS, age_days=365)
        decayed = apply_decay(sig, DEFAULT_SIGNAL_WEIGHTS)
        assert decayed >= 0.0


# ── Combination bonus tests ────────────────────────────────────

class TestCombinationBonus:
    def test_funding_plus_hiring_gets_bonus(self):
        bonus = compute_combination_bonus({SignalType.FUNDING, SignalType.HIRING})
        assert bonus > 0

    def test_single_signal_no_bonus(self):
        bonus = compute_combination_bonus({SignalType.FUNDING})
        assert bonus == 0.0

    def test_bonus_is_capped(self):
        # All signal types at once
        all_types = set(SignalType)
        bonus = compute_combination_bonus(all_types)
        assert bonus <= 0.25


# ── Full scoring test ──────────────────────────────────────────

class TestScoreCompany:
    def test_no_signals_returns_zero_score(self):
        company = make_company()
        icp = make_icp()
        result = score_company(company, [], icp, DEFAULT_SIGNAL_WEIGHTS)
        assert result["composite_score"] == 0.0
        assert result["buying_window"] == BuyingWindowLabel.COLD.value

    def test_strong_signals_full_icp_produces_high_score(self):
        company = make_company()
        icp = make_icp()
        signals = [
            make_signal(SignalType.FUNDING, age_days=7),
            make_signal(SignalType.HIRING, age_days=3),
            make_signal(SignalType.TECH_CHANGE, age_days=5),
        ]
        result = score_company(company, signals, icp, DEFAULT_SIGNAL_WEIGHTS)
        assert result["composite_score"] >= 0.60
        assert result["buying_window"] in (BuyingWindowLabel.HOT.value, BuyingWindowLabel.WARM.value)

    def test_score_is_capped_at_one(self):
        company = make_company()
        icp = make_icp()
        # Many strong fresh signals
        signals = [make_signal(t, age_days=1) for t in SignalType]
        result = score_company(company, signals, icp, DEFAULT_SIGNAL_WEIGHTS)
        assert result["composite_score"] <= 1.0

    def test_weak_icp_match_reduces_score(self):
        strong_icp = make_icp()
        weak_icp = make_icp(
            industries=["Government"],
            locations=["China"],
            min_employees=5000,
            max_employees=50000,
        )
        signals = [make_signal(SignalType.FUNDING, age_days=2)]
        company = make_company()

        strong_result = score_company(company, signals, strong_icp, DEFAULT_SIGNAL_WEIGHTS)
        weak_result = score_company(company, signals, weak_icp, DEFAULT_SIGNAL_WEIGHTS)
        assert strong_result["composite_score"] > weak_result["composite_score"]

    def test_result_contains_required_fields(self):
        company = make_company()
        icp = make_icp()
        signals = [make_signal(SignalType.HIRING, age_days=5)]
        result = score_company(company, signals, icp, DEFAULT_SIGNAL_WEIGHTS)

        required = [
            "company_id", "icp_score", "signal_score", "composite_score",
            "icp_multiplier", "icp_breakdown", "signal_breakdown",
            "buying_window", "buying_window_confidence", "buying_window_reasoning",
        ]
        for field in required:
            assert field in result, f"Missing field: {field}"

    def test_stale_funding_signal_less_valuable_than_fresh(self):
        company = make_company()
        icp = make_icp()

        fresh = [make_signal(SignalType.FUNDING, age_days=3)]
        stale = [make_signal(SignalType.FUNDING, age_days=120)]

        fresh_result = score_company(company, fresh, icp, DEFAULT_SIGNAL_WEIGHTS)
        stale_result = score_company(company, stale, icp, DEFAULT_SIGNAL_WEIGHTS)

        assert fresh_result["composite_score"] > stale_result["composite_score"]
