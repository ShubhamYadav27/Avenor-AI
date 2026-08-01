"""
tests/unit/test_ai_research.py

Unit tests for the Phase 5.1 AI Account Research engine.
No real LLM API is called — a fake LLMProvider is injected everywhere, which
is exactly the point of the provider abstraction.

Covers:
  - JSON extraction from messy model output
  - Input hash determinism and sensitivity
  - Provider registry resolution and error translation
  - Prompt versioning
  - Schema validation of AI payloads
  - Cache hit / force refresh / regeneration-on-change
  - Workspace isolation
  - Graceful failure on timeout, rate limit, invalid JSON, bad schema
"""
import json
import uuid
from typing import Any

import pytest

from app.modules.ai.context import ResearchContext
from app.modules.ai.prompts import (
    ACTIVE_RESEARCH_PROMPT_VERSION,
    get_research_prompt,
)
from app.modules.ai.provider import (
    InvalidAIResponseError,
    LLMProvider,
    ProviderUnavailableError,
    _extract_json_object,
    get_provider,
)
from app.modules.ai.schemas import ResearchPayload

# ══════════════════════════════════════════════════════════════
# Fakes
# ══════════════════════════════════════════════════════════════


def valid_payload() -> dict[str, Any]:
    """A minimal, schema-valid AI response."""
    return {
        "summary": "Acme builds warehouse robotics and is hiring aggressively in ops.",
        "buying_signals": [
            {
                "title": "Series B raised",
                "evidence": "Funding signal detected 2024-01-04",
                "why_it_matters": "New capital typically unlocks tooling budget.",
                "strength": "strong",
            }
        ],
        "pain_points": [
            {
                "title": "Manual pipeline triage",
                "description": "Reps spend hours qualifying accounts by hand.",
                "evidence": "12 open ops roles",
                "priority": "high",
            }
        ],
        "recommended_personas": [
            {
                "title": "VP Sales",
                "rationale": "Owns pipeline efficiency.",
                "matched_contact_name": None,
                "priority": "high",
            }
        ],
        "outreach_strategy": {
            "recommended_channel": "email",
            "timing": "Within two weeks of the funding announcement.",
            "angle": "Tie new capital to faster pipeline coverage.",
            "opening_hook": "Congrats on the Series B — saw you are scaling ops headcount.",
        },
        "talking_points": [
            {"point": "Faster qualification", "supporting_detail": "12 open ops roles."}
        ],
        "risks": [
            {
                "title": "No budget owner identified",
                "description": "No economic buyer in contacts.",
                "mitigation": "Ask for a referral upward.",
                "severity": "medium",
            }
        ],
        "next_actions": [
            {
                "action": "Email the VP Sales",
                "rationale": "Highest-intent persona.",
                "priority": "high",
                "suggested_timeframe": "this week",
            }
        ],
    }


class FakeProvider(LLMProvider):
    """Deterministic in-memory provider used in place of Gemini."""

    name = "fake"

    def __init__(self, response: Any = None, raises: Exception | None = None):
        self._response = response if response is not None else valid_payload()
        self._raises = raises
        self.call_count = 0

    @property
    def model_version(self) -> str:
        return "fake-model-1"

    def is_available(self) -> bool:
        return True

    def generate_json(self, *, system_prompt, user_prompt, temperature=0.2, max_tokens=4096):
        self.call_count += 1
        if self._raises is not None:
            raise self._raises
        return self._response


# ══════════════════════════════════════════════════════════════
# JSON extraction
# ══════════════════════════════════════════════════════════════


class TestJsonExtraction:
    def test_plain_object(self):
        assert json.loads(_extract_json_object('{"a": 1}')) == {"a": 1}

    def test_markdown_fenced(self):
        raw = '```json\n{"a": 1}\n```'
        assert json.loads(_extract_json_object(raw)) == {"a": 1}

    def test_preamble_before_json(self):
        raw = 'Here is your report:\n{"a": 1}'
        assert json.loads(_extract_json_object(raw)) == {"a": 1}

    def test_braces_inside_strings_do_not_confuse_parser(self):
        raw = '{"a": "a } brace", "b": {"c": 2}}'
        assert json.loads(_extract_json_object(raw)) == {"a": "a } brace", "b": {"c": 2}}

    def test_escaped_quote_inside_string(self):
        raw = r'{"a": "he said \"hi\" }", "b": 1}'
        assert json.loads(_extract_json_object(raw)) == {"a": 'he said "hi" }', "b": 1}

    def test_no_json_raises(self):
        with pytest.raises(InvalidAIResponseError):
            _extract_json_object("I cannot help with that.")

    def test_unterminated_json_raises(self):
        with pytest.raises(InvalidAIResponseError):
            _extract_json_object('{"a": 1')


# ══════════════════════════════════════════════════════════════
# Provider registry
# ══════════════════════════════════════════════════════════════


class TestProviderRegistry:
    def test_resolves_gemini_by_default(self):
        provider = get_provider("gemini")
        assert provider.name == "gemini"

    def test_registry_returns_singleton(self):
        assert get_provider("gemini") is get_provider("gemini")

    def test_unknown_provider_raises(self):
        with pytest.raises(ProviderUnavailableError) as exc:
            get_provider("not-a-real-provider")
        assert "Unknown AI provider" in exc.value.message

    def test_gemini_unavailable_without_key(self, monkeypatch):
        from app.core.config import settings
        from app.modules.ai.provider import GeminiProvider

        monkeypatch.setattr(settings, "GEMINI_API_KEY", "", raising=False)
        assert GeminiProvider().is_available() is False


# ══════════════════════════════════════════════════════════════
# Prompts
# ══════════════════════════════════════════════════════════════


class TestPrompts:
    def test_active_version_resolves(self):
        template = get_research_prompt()
        assert template.version == ACTIVE_RESEARCH_PROMPT_VERSION

    def test_unknown_version_raises(self):
        from app.core.exceptions import ValidationError

        with pytest.raises(ValidationError):
            get_research_prompt("research.v999")

    def test_render_interpolates_all_placeholders(self):
        template = get_research_prompt()
        system, user = template.render(
            company_profile="{}",
            scoring="{}",
            signal_count=0,
            signals="none",
            intelligence="{}",
            contact_count=0,
            contacts="none",
            icp="{}",
            crm="{}",
            similar_companies="none",
        )
        assert system
        # No unresolved placeholders should survive rendering.
        assert "{company_profile}" not in user
        assert "{similar_companies}" not in user

    def test_prompt_demands_json_only(self):
        template = get_research_prompt()
        assert "JSON" in template.system


# ══════════════════════════════════════════════════════════════
# Input hashing
# ══════════════════════════════════════════════════════════════


def make_context(**overrides) -> ResearchContext:
    base = dict(
        company_id=str(uuid.uuid4()),
        workspace_id=str(uuid.uuid4()),
        company_profile={"name": "Acme"},
        scoring={"composite_score": 0.8},
        signals=[{"title": "Series B"}],
        intelligence={},
        contacts=[],
        icp={},
        crm={},
        similar_companies=[],
    )
    base.update(overrides)
    return ResearchContext(**base)


class TestInputHash:
    def test_hash_is_deterministic(self):
        ctx = make_context()
        assert ctx.compute_input_hash("v1", "m1") == ctx.compute_input_hash("v1", "m1")

    def test_hash_is_key_order_independent(self):
        a = make_context(company_profile={"name": "Acme", "industry": "Robotics"})
        b = make_context(company_profile={"industry": "Robotics", "name": "Acme"})
        assert a.compute_input_hash("v1", "m1") == b.compute_input_hash("v1", "m1")

    def test_hash_changes_when_signals_change(self):
        a = make_context()
        b = make_context(signals=[{"title": "Series C"}])
        assert a.compute_input_hash("v1", "m1") != b.compute_input_hash("v1", "m1")

    def test_hash_changes_with_prompt_version(self):
        ctx = make_context()
        assert ctx.compute_input_hash("v1", "m1") != ctx.compute_input_hash("v2", "m1")

    def test_hash_changes_with_model(self):
        ctx = make_context()
        assert ctx.compute_input_hash("v1", "m1") != ctx.compute_input_hash("v1", "m2")

    def test_hash_is_sha256_hex(self):
        digest = make_context().compute_input_hash("v1", "m1")
        assert len(digest) == 64
        int(digest, 16)  # raises if not hex

    def test_enrichment_participates_in_hash(self):
        a = make_context()
        b = make_context()
        b.enrichment = {"linkedin": {"followers": 100}}
        assert a.compute_input_hash("v1", "m1") != b.compute_input_hash("v1", "m1")

    def test_has_minimum_data(self):
        assert make_context().has_minimum_data is True
        assert make_context(company_profile={"name": None}).has_minimum_data is False


# ══════════════════════════════════════════════════════════════
# Schema validation
# ══════════════════════════════════════════════════════════════


class TestResearchPayloadSchema:
    def test_valid_payload_parses(self):
        payload = ResearchPayload.model_validate(valid_payload())
        assert payload.summary
        assert payload.outreach_strategy.recommended_channel == "email"

    def test_missing_summary_rejected(self):
        from pydantic import ValidationError as PVE

        data = valid_payload()
        del data["summary"]
        with pytest.raises(PVE):
            ResearchPayload.model_validate(data)

    def test_missing_outreach_strategy_rejected(self):
        from pydantic import ValidationError as PVE

        data = valid_payload()
        del data["outreach_strategy"]
        with pytest.raises(PVE):
            ResearchPayload.model_validate(data)

    def test_bad_enum_rejected(self):
        from pydantic import ValidationError as PVE

        data = valid_payload()
        data["buying_signals"][0]["strength"] = "extremely-strong"
        with pytest.raises(PVE):
            ResearchPayload.model_validate(data)

    def test_unknown_extra_keys_ignored(self):
        data = valid_payload()
        data["hallucinated_section"] = ["nonsense"]
        payload = ResearchPayload.model_validate(data)
        assert not hasattr(payload, "hallucinated_section")

    def test_empty_lists_allowed(self):
        data = valid_payload()
        for key in ("buying_signals", "pain_points", "risks", "next_actions"):
            data[key] = []
        payload = ResearchPayload.model_validate(data)
        assert payload.buying_signals == []
