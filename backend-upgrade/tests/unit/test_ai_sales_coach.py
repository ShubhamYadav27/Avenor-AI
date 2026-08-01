"""Unit tests for Phase 5.4 AI Sales Coach contracts."""
import pytest
from pydantic import ValidationError as PydanticValidationError

from app.core.exceptions import ValidationError
from app.modules.ai.prompts import ACTIVE_SALES_COACH_PROMPT_VERSION, get_sales_coach_prompt
from app.modules.ai.schemas import SalesCoachPayload


def valid_sales_coach_payload() -> dict:
    evidence = {
        "buying_signals": ["Operations hiring detected."],
        "research_findings": ["Research highlights process scaling pressure."],
        "crm_information": ["No active deal is linked."],
        "briefing_insights": ["Briefing recommends VP Operations discovery."],
    }
    return {
        "executive_coaching_summary": "Acme is a viable coaching candidate, but the rep should validate urgency early.",
        "deal_health_assessment": "healthy",
        "win_probability": 0.62,
        "win_probability_explanation": "Strong hiring signal improves odds, while thin CRM context limits certainty.",
        "positive_buying_signals": [
            {
                "title": "Operations hiring",
                "evidence": "Three operations roles detected.",
                "impact": "Suggests active workflow scale pressure.",
                "strength": "strong",
            }
        ],
        "risk_factors": [
            {
                "title": "No active CRM deal",
                "description": "The opportunity may still be early.",
                "severity": "medium",
                "mitigation": "Confirm owner, timing and budget in discovery.",
                "evidence": evidence,
            }
        ],
        "deal_blockers": [
            {
                "title": "Budget unknown",
                "description": "No budget source is visible.",
                "severity": "high",
                "mitigation": "Ask about approved initiatives.",
                "evidence": evidence,
            }
        ],
        "decision_maker_analysis": "VP Operations is the likely decision owner; finance involvement is unknown.",
        "stakeholder_influence_map": [
            {
                "name": "Priya Shah",
                "title": "VP Operations",
                "influence": "decision_maker",
                "priority": "high",
                "likely_motivation": "Improve operational throughput.",
                "recommended_approach": "Lead with timing and prioritization pain.",
            }
        ],
        "likely_customer_objections": [
            {
                "objection": "We already use CRM scoring.",
                "severity": "medium",
                "customer_statement": "We already have scoring in our CRM.",
                "why_customer_may_say_this": "They may see Avenor as duplicate scoring.",
                "recommended_response": "Position Avenor as timing intelligence using external buying signals.",
                "follow_up_question": "Which signals currently change rep prioritization?",
                "goal_of_response": "Separate timing intelligence from static CRM scores.",
                "evidence": evidence,
            }
        ],
        "competitive_battle_cards": [
            {
                "competitor_or_alternative": "CRM scoring",
                "likely_positioning": "Native and already adopted.",
                "avenor_advantage": "Avenor detects external buying windows before CRM activity.",
                "risk": "Buyer may prefer existing tools.",
                "recommended_talk_track": "Anchor on external signal timing and revenue attribution.",
            }
        ],
        "competitor_comparison": "CRM scoring is known; no named third-party competitor appears in context.",
        "pricing_negotiation_strategy": "Anchor price to monitored account volume and revenue at risk.",
        "discovery_coaching": {
            "stage": "discovery",
            "objective": "Validate the prioritization workflow.",
            "coaching": "Ask how reps decide who to contact this week.",
            "questions": ["How are high-priority accounts surfaced today?"],
        },
        "demo_coaching": {
            "stage": "demo",
            "objective": "Show buying-window evidence.",
            "coaching": "Demo signal timelines and account rationale.",
            "questions": ["Which signal would your reps trust most?"],
        },
        "negotiation_coaching": {
            "stage": "negotiation",
            "objective": "Protect value.",
            "coaching": "Trade concessions for volume or timeline commitment.",
            "questions": ["What outcome would justify this investment?"],
        },
        "closing_coaching": {
            "stage": "closing",
            "objective": "Secure mutual action plan.",
            "coaching": "Confirm owner, procurement path and success metrics.",
            "questions": ["Who signs off after the pilot?"],
        },
        "expansion_opportunity": "Start with operations and expand to revenue operations.",
        "recommended_next_best_action": "Book discovery with the VP Operations persona.",
        "immediate_action_plan": [
            {
                "action": "Ask for current prioritization workflow.",
                "rationale": "Validates the pain behind the hiring signal.",
                "priority": "high",
                "owner": "Sales rep",
                "timeframe": "Next call",
            }
        ],
        "follow_up_strategy": [
            {
                "action": "Send recap with signal evidence.",
                "rationale": "Keeps the conversation grounded.",
                "priority": "medium",
                "owner": "Sales rep",
                "timeframe": "Within 24 hours",
            }
        ],
        "long_term_action_plan": [
            {
                "action": "Build business case around conversion lift.",
                "rationale": "Supports later budget approval.",
                "priority": "medium",
                "owner": "Sales rep",
                "timeframe": "After discovery",
            }
        ],
        "escalation_recommendation": None,
        "confidence_score": 0.7,
        "confidence_explanation": "Confidence is moderate because account signals are strong but CRM activity is sparse.",
        "explainability": evidence,
    }


class TestSalesCoachPrompt:
    def test_active_sales_coach_prompt_resolves(self):
        template = get_sales_coach_prompt()
        assert template.version == ACTIVE_SALES_COACH_PROMPT_VERSION

    def test_unknown_sales_coach_prompt_raises(self):
        with pytest.raises(ValidationError):
            get_sales_coach_prompt("sales_coach.v999")

    def test_render_interpolates_all_sales_coach_placeholders(self):
        template = get_sales_coach_prompt()
        system, user = template.render(
            deal_stage="discovery",
            company_profile="{}",
            scoring="{}",
            signals="[]",
            intelligence="{}",
            contacts="[]",
            crm="{}",
            icp="{}",
            research="{}",
            emails="[]",
            briefing="{}",
            previous_coaching="[]",
        )

        assert system
        assert "{company_profile}" not in user
        assert "{previous_coaching}" not in user
        assert "win_probability" in user


class TestSalesCoachPayloadSchema:
    def test_valid_sales_coach_payload_parses(self):
        payload = SalesCoachPayload.model_validate(valid_sales_coach_payload())
        assert payload.win_probability == 0.62
        assert payload.likely_customer_objections[0].severity == "medium"

    def test_missing_summary_is_rejected(self):
        data = valid_sales_coach_payload()
        del data["executive_coaching_summary"]

        with pytest.raises(PydanticValidationError):
            SalesCoachPayload.model_validate(data)

    def test_probability_bounds_are_enforced(self):
        data = valid_sales_coach_payload()
        data["win_probability"] = 1.4

        with pytest.raises(PydanticValidationError):
            SalesCoachPayload.model_validate(data)

    def test_extra_keys_are_ignored(self):
        data = valid_sales_coach_payload()
        data["unsupported"] = "ignore me"

        payload = SalesCoachPayload.model_validate(data)
        assert not hasattr(payload, "unsupported")
