"""
Intent Detector
Classifies user queries into business intents for context provider resolution.
"""
from app.modules.copilot.domain.context import ContextIntent


class IntentDetector:
    def detect_intent(self, query: str) -> ContextIntent:
        q = query.lower()

        if any(w in q for w in ["objection", "pushback", "competitor", "risk", "hesitant", "concern"]):
            return ContextIntent.OBJECTION_HANDLING

        if any(w in q for w in ["signal", "hiring", "funding", "tech change", "expansion", "buying window"]):
            return ContextIntent.BUYING_SIGNALS

        if any(w in q for w in ["deal", "pipeline", "opportunity", "crm", "stage", "close date"]):
            return ContextIntent.CRM_PIPELINE

        if any(w in q for w in ["company", "companies", "account", "accounts", "target", "research", "briefing", "overview", "who to contact"]):
            return ContextIntent.COMPANY_DEEP_DIVE


        if any(w in q for w in ["email", "outreach", "sequence", "pitch", "what to say", "contact"]):
            return ContextIntent.OUTREACH_STRATEGY


        return ContextIntent.GENERAL_STRATEGY


intent_detector = IntentDetector()
