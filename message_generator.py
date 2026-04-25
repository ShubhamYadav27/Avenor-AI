"""
AI personalization engine.
1. Builds structured context from company + contact + signals.
2. Generates message via GPT-4o.
3. Runs quality gate before allowing send.
"""
import logging
import re
from datetime import datetime
from typing import Optional
from openai import OpenAI
from sqlalchemy.orm import Session

from app.config import settings
from app.models import (
    Company, Contact, Signal, SignalType,
    OutreachMessage, OutreachStatus
)

logger = logging.getLogger(__name__)

client = OpenAI(api_key=settings.OPENAI_API_KEY)

# Quality gate config
MAX_WORD_COUNT = 80
MIN_WORD_COUNT = 20
BANNED_PHRASES = [
    "i hope this email finds you",
    "hope you're doing well",
    "just following up",
    "touching base",
    "circle back",
    "synergy",
    "revolutionary",
    "game-changing",
    "i wanted to reach out",
    "as per my last",
]


# ─────────────────────────────────────────────
# Context Builder
# ─────────────────────────────────────────────

def build_context(
    company: Company,
    contact: Contact,
    signals: list[Signal],
    sender_name: str = "Alex",
    sender_company: str = "Nexus",
    product_description: str = "an AI-powered data pipeline tool that helps engineering teams scale their data infrastructure",
) -> dict:
    """
    Builds the structured context object passed to the LLM.
    Keeps logic here — not inside the prompt — for testability.
    """
    # Summarize signals
    signal_summaries = []
    for sig in sorted(signals, key=lambda s: s.decayed_score, reverse=True)[:3]:
        if sig.signal_type == SignalType.FUNDING:
            stage = sig.metadata_.get("stage", "recent round")
            signal_summaries.append(f"raised a {stage}")
        elif sig.signal_type == SignalType.HIRING:
            role = sig.raw_value or "engineering roles"
            signal_summaries.append(f"actively hiring for {role}")
        elif sig.signal_type == SignalType.TECH_CHANGE:
            techs = sig.metadata_.get("technologies", [])
            if techs:
                signal_summaries.append(f"using {', '.join(techs[:2])}")
        elif sig.signal_type == SignalType.EXPANSION:
            signal_summaries.append(f"expanding to new markets")
        elif sig.signal_type == SignalType.INTENT:
            signal_summaries.append("showing active intent signals")

    # Infer pain point from signals
    pain_point = _infer_pain_point(company, signals)

    # Determine tone profile from contact title
    tone = _select_tone_profile(contact.title or "", contact.seniority or "")

    context = {
        "sender_name": sender_name,
        "sender_company": sender_company,
        "product_description": product_description,
        "prospect_first_name": contact.first_name or contact.full_name or "there",
        "prospect_title": contact.title or "leader",
        "company_name": company.name,
        "company_industry": company.industry or "tech",
        "company_size": company.employee_count,
        "company_location": company.location,
        "signals": signal_summaries,
        "pain_point": pain_point,
        "tone_profile": tone,
        "technologies": [t.get("name", "") for t in (company.technologies or [])[:5]],
    }

    return context


# ─────────────────────────────────────────────
# Message Generator
# ─────────────────────────────────────────────

SYSTEM_PROMPT = """You are an expert B2B sales copywriter. You write cold emails that sound 
like they came from a real person, not a marketing department.

RULES (non-negotiable):
- Under 80 words total for the email body
- Start with something specific about their company (a signal), NOT "I hope you're well"
- Never open with "I" as the first word
- No pitch in the first sentence — lead with their situation
- One clear, low-pressure call to action at the end (a question or 15-min offer)
- Sound human, direct, and genuinely curious about their situation
- Do NOT use buzzwords: synergy, game-changing, revolutionary, leverage, utilize
- Do NOT start with flattery ("Congrats on your funding!")

OUTPUT FORMAT:
Subject: [subject line]
---
[email body]"""


def generate_message(
    context: dict,
    angle: str = "pain_led",
) -> tuple[str, str]:
    """
    Generate subject + body for a cold email.
    angle: "pain_led" | "outcome_led" | "curiosity_led"
    Returns (subject, body).
    """
    user_prompt = _build_user_prompt(context, angle)

    logger.info(f"Generating message for {context['company_name']} — angle: {angle}")

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.7,
        max_tokens=300,
    )

    raw_output = response.choices[0].message.content.strip()

    # Parse subject and body
    subject, body = _parse_output(raw_output)
    return subject, body


def _build_user_prompt(context: dict, angle: str) -> str:
    signals_str = "; ".join(context["signals"]) if context["signals"] else "growing their team"

    angle_instructions = {
        "pain_led": "Lead with the problem they're likely facing given these signals.",
        "outcome_led": "Lead with the outcome other companies like them achieved with us.",
        "curiosity_led": "Ask a specific, provocative question about their situation that makes them think.",
    }

    prompt = f"""Write a cold email with these details:

Sender: {context['sender_name']} at {context['sender_company']}
Product: {context['product_description']}

Prospect: {context['prospect_first_name']}, {context['prospect_title']} at {context['company_name']}
Company context: {context['company_industry']} company, ~{context['company_size']} employees
Location: {context['company_location']}
Recent signals: {signals_str}
Technologies used: {', '.join(context['technologies']) or 'unknown'}
Pain point to address: {context['pain_point']}
Tone: {context['tone_profile']}

Angle instruction: {angle_instructions.get(angle, angle_instructions['pain_led'])}

Remember: Under 80 words. Start with something SPECIFIC about their company, not a greeting."""

    return prompt


def _parse_output(raw: str) -> tuple[str, str]:
    """Split GPT output into subject and body."""
    if "---" in raw:
        parts = raw.split("---", 1)
        subject_line = parts[0].replace("Subject:", "").strip()
        body = parts[1].strip()
    elif raw.startswith("Subject:"):
        lines = raw.split("\n", 1)
        subject_line = lines[0].replace("Subject:", "").strip()
        body = lines[1].strip() if len(lines) > 1 else raw
    else:
        subject_line = "Quick question"
        body = raw

    return subject_line, body


# ─────────────────────────────────────────────
# Quality Gate
# ─────────────────────────────────────────────

def run_quality_gate(subject: str, body: str) -> tuple[bool, list[str]]:
    """
    Returns (passed: bool, issues: list[str]).
    All issues must be empty for passed=True.
    """
    issues = []
    body_lower = body.lower()
    words = body.split()

    if len(words) > MAX_WORD_COUNT:
        issues.append(f"Too long: {len(words)} words (max {MAX_WORD_COUNT})")

    if len(words) < MIN_WORD_COUNT:
        issues.append(f"Too short: {len(words)} words (min {MIN_WORD_COUNT})")

    for phrase in BANNED_PHRASES:
        if phrase in body_lower:
            issues.append(f"Banned phrase detected: '{phrase}'")

    if body.strip().startswith("I "):
        issues.append("Email starts with 'I' — rewrite to lead with prospect")

    if not subject or len(subject) < 3:
        issues.append("Missing or empty subject line")

    if len(subject) > 60:
        issues.append(f"Subject too long: {len(subject)} chars (max 60)")

    return len(issues) == 0, issues


# ─────────────────────────────────────────────
# Full Generation + Storage
# ─────────────────────────────────────────────

def generate_and_store_message(
    db: Session,
    company: Company,
    contact: Contact,
    sender_name: str = "Alex",
    sender_company: str = "Nexus",
    product_description: str = "an AI-powered data pipeline tool",
    angle: str = "pain_led",
    sequence_step: int = 1,
) -> OutreachMessage:
    """
    Full pipeline: build context → generate → quality gate → store.
    Returns the OutreachMessage record.
    """
    signals = db.query(Signal).filter_by(company_id=company.id).all()

    context = build_context(
        company=company,
        contact=contact,
        signals=signals,
        sender_name=sender_name,
        sender_company=sender_company,
        product_description=product_description,
    )

    subject, body = generate_message(context, angle=angle)
    passed, issues = run_quality_gate(subject, body)

    message = OutreachMessage(
        company_id=company.id,
        contact_id=contact.id,
        sequence_step=sequence_step,
        subject=subject,
        body=body,
        angle=angle,
        tone_profile=context["tone_profile"],
        status=OutreachStatus.DRAFT,
        context_used=context,
        word_count=len(body.split()),
        passed_quality_gate=passed,
        quality_gate_notes="; ".join(issues) if issues else None,
    )

    db.add(message)
    db.commit()
    db.refresh(message)

    if not passed:
        logger.warning(
            f"Message for {company.name} failed quality gate: {issues}"
        )
    else:
        logger.info(f"Message generated and approved for {company.name}")

    return message


# ─────────────────────────────────────────────
# Internal helpers
# ─────────────────────────────────────────────

def _infer_pain_point(company: Company, signals: list[Signal]) -> str:
    """
    Heuristic: infer the most likely pain point from signal combination.
    In a real system this would be a retrieval step from a pain point library.
    """
    signal_types = {s.signal_type for s in signals}

    if SignalType.FUNDING in signal_types and SignalType.HIRING in signal_types:
        return (
            f"Post-funding scale: {company.name} is growing headcount rapidly — "
            "their current data stack will hit limits before the next round"
        )
    elif SignalType.HIRING in signal_types:
        return (
            "Hiring surge creates data chaos: more teams means more data requests, "
            "pipelines that were fine at smaller scale start breaking"
        )
    elif SignalType.FUNDING in signal_types:
        return (
            "Post-funding pressure: investors expect faster decisions, "
            "which means the data team needs to move faster too"
        )
    elif SignalType.TECH_CHANGE in signal_types:
        return (
            "Active tech evaluation: company is reassessing their stack — "
            "prime moment for a conversation"
        )
    else:
        return (
            f"Growing {company.industry or 'tech'} company likely managing data "
            "infrastructure manually as team scales"
        )


def _select_tone_profile(title: str, seniority: str) -> str:
    """Pick a communication tone based on the contact's role."""
    title_lower = title.lower()

    if any(t in title_lower for t in ["ceo", "cto", "coo", "founder", "co-founder"]):
        return "executive_direct"  # very short, ROI-focused, no jargon
    elif any(t in title_lower for t in ["engineering", "engineer", "technical", "infrastructure"]):
        return "technical_peer"   # technical credibility, specific tool mentions
    elif any(t in title_lower for t in ["data", "analytics", "bi", "insights"]):
        return "data_practitioner" # data-specific pain points
    elif any(t in title_lower for t in ["marketing", "growth", "revenue"]):
        return "business_outcome"  # metrics, pipeline, conversion
    else:
        return "professional_warm"  # safe default
