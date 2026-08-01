"""Unit tests for Phase 5.2 AI Email Generator contracts."""
import pytest
from pydantic import ValidationError as PydanticValidationError

from app.core.exceptions import ValidationError
from app.modules.ai.prompts import ACTIVE_EMAIL_PROMPT_VERSION, get_email_prompt
from app.modules.ai.schemas import EmailPayload


def valid_email_payload() -> dict[str, str]:
    return {
        "subject": "Worth a quick look at pipeline timing?",
        "body": "Hi Priya,\n\nSaw the team is scaling GTM after the recent funding signal.",
        "cta": "Open to a quick call next week?",
        "reasoning": "Uses the strongest buying signal and keeps the ask low-friction.",
        "variation": "A",
    }


class TestEmailPrompt:
    def test_active_email_prompt_resolves(self):
        template = get_email_prompt()
        assert template.version == ACTIVE_EMAIL_PROMPT_VERSION

    def test_unknown_email_prompt_raises(self):
        with pytest.raises(ValidationError):
            get_email_prompt("email.v999")

    def test_render_interpolates_all_email_placeholders(self):
        template = get_email_prompt()
        system, user = template.render(
            email_type="cold_email",
            tone="professional",
            length="medium",
            cta_type="book_meeting",
            variation="A",
            variation_style="Direct and specific.",
            company_profile="{}",
            contact="{}",
            research="{}",
            buying_signals="[]",
            outreach_strategy="{}",
            icp="{}",
        )

        assert system
        assert "{email_type}" not in user
        assert "{company_profile}" not in user
        assert "Return a JSON object" in user


class TestEmailPayloadSchema:
    def test_valid_email_payload_parses(self):
        payload = EmailPayload.model_validate(valid_email_payload())
        assert payload.subject.startswith("Worth")
        assert payload.variation == "A"

    def test_missing_body_is_rejected(self):
        data = valid_email_payload()
        del data["body"]

        with pytest.raises(PydanticValidationError):
            EmailPayload.model_validate(data)

    def test_bad_variation_is_rejected(self):
        data = valid_email_payload()
        data["variation"] = "D"

        with pytest.raises(PydanticValidationError):
            EmailPayload.model_validate(data)

    def test_extra_keys_are_ignored(self):
        data = valid_email_payload()
        data["unsupported"] = "ignore me"

        payload = EmailPayload.model_validate(data)
        assert not hasattr(payload, "unsupported")
