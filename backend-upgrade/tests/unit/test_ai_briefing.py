"""Unit tests for Phase 5.3 AI Sales Briefing contracts."""
import pytest
from pydantic import ValidationError as PydanticValidationError

from app.core.exceptions import ValidationError
from app.modules.ai.prompts import ACTIVE_BRIEFING_PROMPT_VERSION, get_briefing_prompt
from app.modules.ai.schemas import BriefingPayload


def valid_briefing_payload() -> dict:
    return {
        "executive_summary": "Acme is a strong meeting candidate based on recent hiring.",
        "company_overview": "Acme sells logistics software to mid-market warehouses.",
        "current_buying_signals": [
            {"title": "Hiring", "evidence": "Three operations roles detected.", "strength": "strong"}
        ],
        "why_buy_now": ["Operations hiring suggests process scale pressure."],
        "recent_company_changes": ["New operations hiring activity."],
        "existing_relationship_summary": "No prior relationship is known.",
        "crm_activity_summary": "No open CRM deal is linked.",
        "key_stakeholders": [
            {"name": "Priya Shah", "title": "VP Operations", "priority": "high", "rationale": "Owns operating efficiency."}
        ],
        "recommended_contact_priority": [
            {"contact_or_persona": "VP Operations", "priority": "high", "reason": "Closest owner of the pain."}
        ],
        "existing_ai_research_summary": "Research highlights operations scaling pain.",
        "previous_generated_emails": [
            {"subject": "Operations timing", "variation": "A", "summary": "Connects hiring to workflow scale.", "cta": "Quick call?"}
        ],
        "pain_points": [
            {"title": "Manual triage", "description": "Qualification is manual.", "evidence": "Research report.", "priority": "high"}
        ],
        "business_opportunities": [
            {"title": "Pipeline efficiency", "rationale": "Improve prioritization.", "priority": "high"}
        ],
        "suggested_value_proposition": "Help Acme prioritize in-market accounts sooner.",
        "competitive_landscape": "No competitor context is known.",
        "discovery_questions": ["How are accounts prioritized today?"],
        "technical_questions": ["Which CRM objects drive routing?"],
        "business_questions": ["What pipeline coverage target matters this quarter?"],
        "executive_questions": ["What revenue risk is most visible right now?"],
        "possible_customer_objections": ["We already use CRM scoring."],
        "suggested_responses": [
            {"objection": "We already use CRM scoring.", "response": "Position Avenor as signal-driven timing intelligence."}
        ],
        "recommended_meeting_agenda": ["Confirm current prioritization workflow."],
        "meeting_goals": ["Identify the buying owner."],
        "recommended_demo_focus": ["Buying window timeline."],
        "recommended_pricing_strategy": "Anchor on monitored account volume.",
        "recommended_follow_up_timeline": ["Send recap within 24 hours."],
        "next_best_action": "Book discovery with VP Operations.",
        "risk_factors": [
            {"title": "Thin CRM context", "description": "No active deal.", "severity": "medium", "mitigation": "Validate urgency early."}
        ],
        "confidence_score": 0.74,
        "confidence_explanation": "Confidence is moderate because hiring signal is strong, but CRM activity is missing.",
    }


class TestBriefingPrompt:
    def test_active_briefing_prompt_resolves(self):
        template = get_briefing_prompt()
        assert template.version == ACTIVE_BRIEFING_PROMPT_VERSION

    def test_unknown_briefing_prompt_raises(self):
        with pytest.raises(ValidationError):
            get_briefing_prompt("briefing.v999")

    def test_render_interpolates_all_briefing_placeholders(self):
        template = get_briefing_prompt()
        system, user = template.render(
            company_profile="{}",
            scoring="{}",
            signals="[]",
            intelligence="{}",
            contacts="[]",
            crm="{}",
            icp="{}",
            research="{}",
            emails="[]",
            previous_briefings="[]",
        )

        assert system
        assert "{company_profile}" not in user
        assert "{previous_briefings}" not in user
        assert "confidence_score" in user


class TestBriefingPayloadSchema:
    def test_valid_briefing_payload_parses(self):
        payload = BriefingPayload.model_validate(valid_briefing_payload())
        assert payload.confidence_score == 0.74
        assert payload.key_stakeholders[0].priority == "high"

    def test_missing_summary_is_rejected(self):
        data = valid_briefing_payload()
        del data["executive_summary"]

        with pytest.raises(PydanticValidationError):
            BriefingPayload.model_validate(data)

    def test_confidence_score_bounds_are_enforced(self):
        data = valid_briefing_payload()
        data["confidence_score"] = 1.5

        with pytest.raises(PydanticValidationError):
            BriefingPayload.model_validate(data)

    def test_extra_keys_are_ignored(self):
        data = valid_briefing_payload()
        data["unsupported"] = "ignore me"

        payload = BriefingPayload.model_validate(data)
        assert not hasattr(payload, "unsupported")
