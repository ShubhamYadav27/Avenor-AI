"""
Versioned prompt templates.

Prompts are never hardcoded inside services. Every template carries a version
string persisted to `company_ai_research.prompt_version`, so a stored report
always remains traceable to the exact instructions that produced it.

Adding a new version:
    1. Define RESEARCH_PROMPT_V2 below
    2. Register it in _RESEARCH_PROMPTS
    3. Point ACTIVE_RESEARCH_PROMPT_VERSION at it

Old rows keep their original version and stay interpretable. The input hash
includes the prompt version, so bumping it invalidates caches automatically.
"""
from dataclasses import dataclass

from app.core.exceptions import ValidationError


@dataclass(frozen=True)
class PromptTemplate:
    """A versioned system/user prompt pair."""

    version: str
    system: str
    user_template: str

    def render(self, **kwargs: object) -> tuple[str, str]:
        """Return (system_prompt, user_prompt) with the context interpolated."""
        return self.system, self.user_template.format(**kwargs)


# ── research.v1 ───────────────────────────────────────────────

_RESEARCH_SYSTEM_V1 = """You are a senior B2B revenue intelligence analyst working inside Avenor, \
a predictive revenue intelligence platform. You brief sales representatives before they engage \
an account.

Your job is to turn the structured intelligence Avenor has collected about a company into a \
sharp, decision-ready sales research report.

Rules you must follow:
1. Ground every claim in the intelligence provided. Never invent funding rounds, headcount, \
executives, customers, products or news that are not in the context.
2. If the evidence is thin, say so plainly and lower your confidence. A short honest report beats \
a padded speculative one.
3. Be specific and concrete. Never write filler like "significant growth", "exciting developments" \
or "leveraging synergies".
4. Reference actual signals, scores and contacts by name when you use them as evidence.
5. Write for a salesperson who has 60 seconds before a call.
6. Only name a contact in `matched_contact_name` if that exact person appears in the Known contacts \
section. Otherwise leave it null and describe the persona by job title.
7. Respond with a single JSON object and nothing else. No markdown, no code fences, no commentary."""

_RESEARCH_USER_V1 = """Produce an account research report for the company below.

Return a JSON object with EXACTLY this structure:

{{
  "summary": "3-5 sentence executive summary: what the company does, and whether they are plausibly in a buying window and why.",
  "buying_signals": [
    {{"title": "short label", "evidence": "the specific Avenor signal or data point this rests on", "why_it_matters": "why this suggests a buying window", "strength": "strong|moderate|weak"}}
  ],
  "pain_points": [
    {{"title": "short label", "description": "the business challenge they likely face", "evidence": "what in the context implies it, or null", "priority": "high|medium|low"}}
  ],
  "recommended_personas": [
    {{"title": "job title to target", "rationale": "why this role owns the problem", "matched_contact_name": "exact name from Known contacts, or null", "priority": "high|medium|low"}}
  ],
  "outreach_strategy": {{
    "recommended_channel": "e.g. email, LinkedIn, warm intro",
    "timing": "when to reach out and why",
    "angle": "the core positioning for this account",
    "opening_hook": "a specific opening line referencing real evidence"
  }},
  "talking_points": [
    {{"point": "the point to make", "supporting_detail": "the evidence behind it"}}
  ],
  "risks": [
    {{"title": "short label", "description": "what could derail this deal", "mitigation": "how to handle it, or null", "severity": "high|medium|low"}}
  ],
  "next_actions": [
    {{"action": "the concrete next step", "rationale": "why this step now", "priority": "high|medium|low", "suggested_timeframe": "e.g. this week, or null"}}
  ]
}}

Provide 2-5 items in each list. Every list may be shorter if the evidence does not support more.
`outreach_strategy` and `summary` are required.

=== COMPANY PROFILE ===
{company_profile}

=== AVENOR PREDICTIVE SCORING ===
{scoring}

=== BUYING SIGNALS DETECTED ({signal_count}) ===
{signals}

=== EXISTING AVENOR INTELLIGENCE ===
{intelligence}

=== KNOWN CONTACTS ({contact_count}) ===
{contacts}

=== IDEAL CUSTOMER PROFILE (what we sell) ===
{icp}

=== CRM CONTEXT ===
{crm}

=== COMPARABLE WON ACCOUNTS ===
{similar_companies}

Return the JSON object now."""

RESEARCH_PROMPT_V1 = PromptTemplate(
    version="research.v1",
    system=_RESEARCH_SYSTEM_V1,
    user_template=_RESEARCH_USER_V1,
)


# -- email.v1 -----------------------------------------------------------------

_EMAIL_SYSTEM_V1 = """You are an experienced B2B SDR writing outbound sales email inside Avenor, \
a predictive revenue intelligence platform.

Your job is to turn Avenor AI research into a concise, personalized sales email that a human rep \
could send after a careful account review.

Rules you must follow:
1. Use only the company, contact and research context provided. Never invent facts, customers, \
funding, technologies, news or job changes.
2. Write like a senior SDR: specific, relevant, useful and direct. Avoid hype, empty praise and \
generic personalization.
3. Match the requested email type, tone, length, CTA type and variation style.
4. If a contact is provided, address that person naturally and connect the message to their role. \
If no contact is provided, write to the appropriate persona without fabricating a name.
5. Keep the body as an email draft only. Do not include markdown, bullet-heavy formatting, \
signatures, placeholders or commentary.
6. Respond with a single JSON object and nothing else. No markdown, no code fences."""

_EMAIL_USER_V1 = """Generate one outbound sales email using the context below.

Return a JSON object with EXACTLY this structure:

{{
  "subject": "email subject line",
  "body": "complete email body, without signature placeholders",
  "cta": "the final ask or call to action",
  "reasoning": "brief explanation of the personalization and strategy used",
  "variation": "{variation}"
}}

EMAIL CONTROLS:
- Email type: {email_type}
- Tone: {tone}
- Length: {length}
- CTA type: {cta_type}
- Variation: {variation}
- Variation style guidance: {variation_style}

=== COMPANY PROFILE ===
{company_profile}

=== SELECTED RECIPIENT ===
{contact}

=== AI RESEARCH REPORT ===
{research}

=== BUYING SIGNALS ===
{buying_signals}

=== OUTREACH STRATEGY FROM RESEARCH ===
{outreach_strategy}

=== WORKSPACE ICP / WHAT WE SELL ===
{icp}

Return the JSON object now."""

EMAIL_PROMPT_V1 = PromptTemplate(
    version="email.v1",
    system=_EMAIL_SYSTEM_V1,
    user_template=_EMAIL_USER_V1,
)


# ── Registry ──────────────────────────────────────────────────

_RESEARCH_PROMPTS: dict[str, PromptTemplate] = {
    RESEARCH_PROMPT_V1.version: RESEARCH_PROMPT_V1,
}

ACTIVE_RESEARCH_PROMPT_VERSION = RESEARCH_PROMPT_V1.version

_EMAIL_PROMPTS: dict[str, PromptTemplate] = {
    EMAIL_PROMPT_V1.version: EMAIL_PROMPT_V1,
}

ACTIVE_EMAIL_PROMPT_VERSION = EMAIL_PROMPT_V1.version


def get_research_prompt(version: str | None = None) -> PromptTemplate:
    """Resolve a research prompt template by version (defaults to the active one)."""
    resolved = version or ACTIVE_RESEARCH_PROMPT_VERSION
    template = _RESEARCH_PROMPTS.get(resolved)
    if template is None:
        raise ValidationError(
            f"Unknown prompt version '{resolved}'. "
            f"Registered: {', '.join(sorted(_RESEARCH_PROMPTS))}",
            field="prompt_version",
        )
    return template


def get_email_prompt(version: str | None = None) -> PromptTemplate:
    """Resolve an email prompt template by version (defaults to the active one)."""
    resolved = version or ACTIVE_EMAIL_PROMPT_VERSION
    template = _EMAIL_PROMPTS.get(resolved)
    if template is None:
        raise ValidationError(
            f"Unknown email prompt version '{resolved}'. "
            f"Registered: {', '.join(sorted(_EMAIL_PROMPTS))}",
            field="prompt_version",
        )
    return template


# -- briefing.v1 --------------------------------------------------------------

_BRIEFING_SYSTEM_V1 = """You are a senior B2B revenue copilot inside Avenor.

Your job is to turn existing Avenor account intelligence into a complete pre-meeting sales briefing.

Rules you must follow:
1. Reuse only the supplied intelligence. Never invent news, funding, contacts, emails, deals or technologies.
2. Do not regenerate research. Summarize and organize the existing AI research, CRM data, signals and email drafts.
3. If evidence is thin, say so plainly and lower confidence.
4. Write for a sales representative preparing for a meeting or sales call.
5. Keep recommendations specific, practical and grounded in the context.
6. Respond with a single JSON object and nothing else. No markdown, no code fences."""

_BRIEFING_USER_V1 = """Generate a complete AI sales briefing for the company below.

Return a JSON object with EXACTLY this structure:

{{
  "executive_summary": "3-5 sentence meeting-ready summary.",
  "company_overview": "Concise overview of the company and account context.",
  "current_buying_signals": [{{"title": "short label", "evidence": "specific evidence", "strength": "strong|moderate|weak"}}],
  "why_buy_now": ["specific reason this account may be in market now"],
  "recent_company_changes": ["funding, hiring, leadership, technology or other changes present in context"],
  "existing_relationship_summary": "What Avenor knows about current relationship depth, or that it is unknown.",
  "crm_activity_summary": "Summary of CRM deals/outcomes/activity from context.",
  "key_stakeholders": [{{"name": "contact name or null", "title": "role/title", "priority": "high|medium|low", "rationale": "why they matter"}}],
  "recommended_contact_priority": [{{"contact_or_persona": "name or persona", "priority": "high|medium|low", "reason": "why"}}],
  "existing_ai_research_summary": "Summary of the existing AI research report.",
  "previous_generated_emails": [{{"subject": "subject", "variation": "A|B|C", "summary": "what the draft says", "cta": "cta or null"}}],
  "pain_points": [{{"title": "short label", "description": "pain point", "evidence": "specific evidence or null", "priority": "high|medium|low"}}],
  "business_opportunities": [{{"title": "opportunity", "rationale": "why it matters", "priority": "high|medium|low"}}],
  "suggested_value_proposition": "Recommended value proposition for this meeting.",
  "competitive_landscape": "Known competitor/alternative context, or note what is unknown.",
  "discovery_questions": ["question"],
  "technical_questions": ["question"],
  "business_questions": ["question"],
  "executive_questions": ["question"],
  "possible_customer_objections": ["objection"],
  "suggested_responses": [{{"objection": "objection", "response": "recommended response"}}],
  "recommended_meeting_agenda": ["agenda item"],
  "meeting_goals": ["goal"],
  "recommended_demo_focus": ["demo area to focus on"],
  "recommended_pricing_strategy": "Pricing guidance grounded in account context.",
  "recommended_follow_up_timeline": ["time-bound follow-up step"],
  "next_best_action": "The single best next action.",
  "risk_factors": [{{"title": "risk", "description": "why it matters", "severity": "high|medium|low", "mitigation": "mitigation or null"}}],
  "confidence_score": 0.0,
  "confidence_explanation": "Explain why confidence is high or low, which signals contributed most, and what missing information reduced confidence."
}}

Use 0.0-1.0 for confidence_score.

=== COMPANY PROFILE ===
{company_profile}

=== PREDICTIVE SCORING ===
{scoring}

=== BUYING SIGNALS ===
{signals}

=== COMPANY INTELLIGENCE ===
{intelligence}

=== CRM CONTACTS ===
{contacts}

=== CRM DEALS AND OUTCOMES ===
{crm}

=== WORKSPACE ICP / WHAT WE SELL ===
{icp}

=== EXISTING AI RESEARCH ===
{research}

=== PREVIOUS GENERATED EMAILS ===
{emails}

=== PREVIOUS AI BRIEFINGS ===
{previous_briefings}

Return the JSON object now."""

BRIEFING_PROMPT_V1 = PromptTemplate(
    version="briefing.v1",
    system=_BRIEFING_SYSTEM_V1,
    user_template=_BRIEFING_USER_V1,
)

_BRIEFING_PROMPTS: dict[str, PromptTemplate] = {
    BRIEFING_PROMPT_V1.version: BRIEFING_PROMPT_V1,
}

ACTIVE_BRIEFING_PROMPT_VERSION = BRIEFING_PROMPT_V1.version


def get_briefing_prompt(version: str | None = None) -> PromptTemplate:
    """Resolve a briefing prompt template by version (defaults to the active one)."""
    resolved = version or ACTIVE_BRIEFING_PROMPT_VERSION
    template = _BRIEFING_PROMPTS.get(resolved)
    if template is None:
        raise ValidationError(
            f"Unknown briefing prompt version '{resolved}'. "
            f"Registered: {', '.join(sorted(_BRIEFING_PROMPTS))}",
            field="prompt_version",
        )
    return template


# -- sales_coach.v1 -----------------------------------------------------------

_SALES_COACH_SYSTEM_V1 = """You are a senior B2B sales coach and revenue copilot inside Avenor.

Your job is to coach a sales representative before a difficult customer conversation.

Rules you must follow:
1. Reuse only the supplied Avenor intelligence. Never invent news, funding, contacts, deals, technologies or competitors.
2. Do not regenerate research, emails or briefings. Use them as source material and explain how they influenced the coaching.
3. Adapt guidance to industry, company size, funding stage, technology stack, buying signals, CRM activity, relationship depth and deal stage.
4. Make every recommendation practical enough for a rep to use in a live call.
5. For every objection, include a realistic customer statement, why they may say it, response, follow-up question and goal.
6. If evidence is thin, say so plainly, reduce win probability and lower confidence.
7. Respond with a single JSON object and nothing else. No markdown, no code fences."""

_SALES_COACH_USER_V1 = """Generate AI Revenue Copilot sales coaching for the company below.

Return a JSON object with EXACTLY this structure:

{{
  "executive_coaching_summary": "3-5 sentence practical coaching summary.",
  "deal_health_assessment": "strong|healthy|at_risk|blocked|unknown",
  "win_probability": 0.0,
  "win_probability_explanation": "Why this win probability was assigned.",
  "positive_buying_signals": [{{"title": "signal", "evidence": "specific evidence", "impact": "why it helps the deal", "strength": "strong|moderate|weak"}}],
  "risk_factors": [{{"title": "risk", "description": "why it matters", "severity": "high|medium|low", "mitigation": "how to mitigate", "evidence": {{"buying_signals": [], "research_findings": [], "crm_information": [], "briefing_insights": []}}}}],
  "deal_blockers": [{{"title": "blocker", "description": "what could block the deal", "severity": "high|medium|low", "mitigation": "how to unblock", "evidence": {{"buying_signals": [], "research_findings": [], "crm_information": [], "briefing_insights": []}}}}],
  "decision_maker_analysis": "Who likely decides, who influences, and what is unknown.",
  "stakeholder_influence_map": [{{"name": "contact name or null", "title": "role/title", "influence": "decision_maker|influencer|champion|blocker|unknown", "priority": "high|medium|low", "likely_motivation": "motivation", "recommended_approach": "how to engage"}}],
  "likely_customer_objections": [{{"objection": "short label", "severity": "critical|high|medium|low", "customer_statement": "realistic customer wording", "why_customer_may_say_this": "reason", "recommended_response": "rep response", "follow_up_question": "question", "goal_of_response": "goal", "evidence": {{"buying_signals": [], "research_findings": [], "crm_information": [], "briefing_insights": []}}}}],
  "competitive_battle_cards": [{{"competitor_or_alternative": "name or category", "likely_positioning": "how they compete", "avenor_advantage": "advantage", "risk": "risk", "recommended_talk_track": "talk track"}}],
  "competitor_comparison": "Comparison against known competitors or alternatives, or what is unknown.",
  "pricing_negotiation_strategy": "Pricing and concession strategy.",
  "discovery_coaching": {{"stage": "discovery", "objective": "objective", "coaching": "guidance", "questions": ["question"]}},
  "demo_coaching": {{"stage": "demo", "objective": "objective", "coaching": "guidance", "questions": ["question"]}},
  "negotiation_coaching": {{"stage": "negotiation", "objective": "objective", "coaching": "guidance", "questions": ["question"]}},
  "closing_coaching": {{"stage": "closing", "objective": "objective", "coaching": "guidance", "questions": ["question"]}},
  "expansion_opportunity": "Expansion or land-and-expand opportunity.",
  "recommended_next_best_action": "single next best action",
  "immediate_action_plan": [{{"action": "action", "rationale": "why", "priority": "high|medium|low", "owner": "owner or null", "timeframe": "timeframe or null"}}],
  "follow_up_strategy": [{{"action": "action", "rationale": "why", "priority": "high|medium|low", "owner": "owner or null", "timeframe": "timeframe or null"}}],
  "long_term_action_plan": [{{"action": "action", "rationale": "why", "priority": "high|medium|low", "owner": "owner or null", "timeframe": "timeframe or null"}}],
  "escalation_recommendation": "recommend escalation if required, otherwise null",
  "confidence_score": 0.0,
  "confidence_explanation": "Why confidence is high or low.",
  "explainability": {{"buying_signals": [], "research_findings": [], "crm_information": [], "briefing_insights": []}}
}}

Use 0.0-1.0 for win_probability and confidence_score.
Provide 2-5 useful items in lists when evidence supports them. Lists may be shorter when context is thin.
Every recommendation must explain which source evidence contributed through the evidence/explainability fields.

REQUESTED DEAL STAGE:
{deal_stage}

=== COMPANY PROFILE ===
{company_profile}

=== PREDICTIVE SCORING ===
{scoring}

=== BUYING SIGNALS ===
{signals}

=== COMPANY INTELLIGENCE ===
{intelligence}

=== CRM CONTACTS ===
{contacts}

=== CRM DEALS AND OUTCOMES ===
{crm}

=== WORKSPACE ICP / WHAT WE SELL ===
{icp}

=== EXISTING AI RESEARCH ===
{research}

=== PREVIOUS GENERATED EMAILS ===
{emails}

=== AI SALES BRIEFING ===
{briefing}

=== PREVIOUS SALES COACHING ===
{previous_coaching}

Return the JSON object now."""

SALES_COACH_PROMPT_V1 = PromptTemplate(
    version="sales_coach.v1",
    system=_SALES_COACH_SYSTEM_V1,
    user_template=_SALES_COACH_USER_V1,
)

_SALES_COACH_PROMPTS: dict[str, PromptTemplate] = {
    SALES_COACH_PROMPT_V1.version: SALES_COACH_PROMPT_V1,
}

ACTIVE_SALES_COACH_PROMPT_VERSION = SALES_COACH_PROMPT_V1.version


def get_sales_coach_prompt(version: str | None = None) -> PromptTemplate:
    """Resolve a sales coach prompt template by version (defaults to the active one)."""
    resolved = version or ACTIVE_SALES_COACH_PROMPT_VERSION
    template = _SALES_COACH_PROMPTS.get(resolved)
    if template is None:
        raise ValidationError(
            f"Unknown sales coach prompt version '{resolved}'. "
            f"Registered: {', '.join(sorted(_SALES_COACH_PROMPTS))}",
            field="prompt_version",
        )
    return template
