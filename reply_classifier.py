"""
Reply classifier.
Classifies incoming email replies using GPT-4o with few-shot examples.
Fires Slack notification for positive/soft-interest replies.
"""
import json
import logging
from datetime import datetime, timezone
from typing import Optional
import httpx
from openai import OpenAI
from sqlalchemy.orm import Session

from app.config import settings
from app.models import Reply, ReplyType, OutreachMessage, Contact, Company

logger = logging.getLogger(__name__)
client = OpenAI(api_key=settings.OPENAI_API_KEY)


# ─────────────────────────────────────────────
# Classification
# ─────────────────────────────────────────────

CLASSIFIER_PROMPT = """Classify the following email reply from a sales prospect into one of these categories:

CATEGORIES:
- positive: Prospect is clearly interested, wants to learn more, agrees to a call
- soft_interest: Prospect shows some interest but isn't committing yet (e.g. "send more info")
- objection: Prospect has a specific concern (timing, price, wrong person, etc.)
- hard_no: Clear rejection, unsubscribe request, or "not interested"
- out_of_office: Auto-reply or manual OOO message

FEW-SHOT EXAMPLES:
Reply: "Yes, this is actually relevant timing. Let's schedule a call."
Classification: positive

Reply: "Can you send over some more information? Happy to take a look."
Classification: soft_interest

Reply: "We already have something in place for this, but thanks."
Classification: objection

Reply: "Please remove me from your list."
Classification: hard_no

Reply: "I'm out of the office until Jan 15. For urgent matters contact..."
Classification: out_of_office

Reply: "Not the right time for us, we just signed a 2 year contract."
Classification: objection

Reply: "Interesting — who else in our space have you worked with?"
Classification: soft_interest

NOW CLASSIFY THIS REPLY:
---
{reply_text}
---

Respond in JSON only, no other text:
{{"classification": "<one of the categories above>", "confidence": <0.0-1.0>, "reasoning": "<one sentence>"}}"""


def classify_reply(reply_text: str) -> tuple[ReplyType, float, str]:
    """
    Returns (reply_type, confidence, reasoning).
    Uses GPT-4o with structured JSON output.
    """
    prompt = CLASSIFIER_PROMPT.format(reply_text=reply_text[:2000])  # cap at 2k chars

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,  # low temp for classification
            max_tokens=150,
            response_format={"type": "json_object"},
        )

        raw = response.choices[0].message.content.strip()
        parsed = json.loads(raw)

        category = parsed.get("classification", "unknown")
        confidence = float(parsed.get("confidence", 0.5))
        reasoning = parsed.get("reasoning", "")

        # Map to enum
        reply_type_map = {
            "positive": ReplyType.POSITIVE,
            "soft_interest": ReplyType.SOFT_INTEREST,
            "objection": ReplyType.OBJECTION,
            "hard_no": ReplyType.HARD_NO,
            "out_of_office": ReplyType.OUT_OF_OFFICE,
        }

        reply_type = reply_type_map.get(category, ReplyType.UNKNOWN)
        logger.info(f"Reply classified as {reply_type.value} (confidence: {confidence:.2f})")
        return reply_type, confidence, reasoning

    except Exception as e:
        logger.error(f"Classification failed: {e}")
        return ReplyType.UNKNOWN, 0.0, f"Classification error: {str(e)}"


# ─────────────────────────────────────────────
# Slack Notification
# ─────────────────────────────────────────────

def notify_slack(
    company_name: str,
    contact_name: str,
    contact_title: str,
    reply_type: ReplyType,
    reply_text: str,
    reasoning: str,
    composite_score: float,
) -> bool:
    """Send a Slack webhook notification for hot replies."""
    if not settings.SLACK_WEBHOOK_URL:
        logger.debug("No Slack webhook configured — skipping notification")
        return False

    emoji = {
        ReplyType.POSITIVE: "🟢",
        ReplyType.SOFT_INTEREST: "🟡",
    }.get(reply_type, "⚪")

    preview = reply_text[:200] + ("..." if len(reply_text) > 200 else "")

    payload = {
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"{emoji} {reply_type.value.upper().replace('_', ' ')} — {company_name}",
                },
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*Contact:*\n{contact_name}"},
                    {"type": "mrkdwn", "text": f"*Title:*\n{contact_title}"},
                    {"type": "mrkdwn", "text": f"*Company:*\n{company_name}"},
                    {"type": "mrkdwn", "text": f"*Lead Score:*\n{composite_score:.2f}"},
                ],
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Reply preview:*\n>{preview}",
                },
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*AI reasoning:* {reasoning}",
                },
            },
        ]
    }

    try:
        resp = httpx.post(settings.SLACK_WEBHOOK_URL, json=payload, timeout=10)
        resp.raise_for_status()
        return True
    except Exception as e:
        logger.error(f"Slack notification failed: {e}")
        return False


# ─────────────────────────────────────────────
# Full Reply Handler
# ─────────────────────────────────────────────

def handle_reply(
    db: Session,
    outreach_message_id: str,
    reply_text: str,
    received_at: Optional[datetime] = None,
) -> Reply:
    """
    Full reply processing pipeline:
    1. Classify the reply
    2. Store in DB
    3. Send Slack notification if hot
    4. Mark if human action needed
    """
    message: OutreachMessage = db.query(OutreachMessage).get(outreach_message_id)
    if not message:
        raise ValueError(f"OutreachMessage not found: {outreach_message_id}")

    contact: Contact = db.query(Contact).get(message.contact_id)
    company: Company = db.query(Company).get(message.company_id)

    # Classify
    reply_type, confidence, reasoning = classify_reply(reply_text)

    # Determine if human needs to act
    requires_human = reply_type in (ReplyType.POSITIVE, ReplyType.SOFT_INTEREST)

    # Store reply
    reply = Reply(
        outreach_message_id=message.id,
        contact_id=message.contact_id,
        raw_body=reply_text,
        reply_type=reply_type,
        classification_confidence=confidence,
        classification_reasoning=reasoning,
        requires_human_action=requires_human,
        received_at=received_at or datetime.now(timezone.utc),
    )
    db.add(reply)

    # Update message status
    message.status = __import__('app.models', fromlist=['OutreachStatus']).OutreachStatus.REPLIED

    db.commit()
    db.refresh(reply)

    # Notify Slack for hot replies
    if reply_type in (ReplyType.POSITIVE, ReplyType.SOFT_INTEREST):
        notified = notify_slack(
            company_name=company.name,
            contact_name=contact.full_name or contact.first_name or "Unknown",
            contact_title=contact.title or "Unknown",
            reply_type=reply_type,
            reply_text=reply_text,
            reasoning=reasoning,
            composite_score=company.composite_score,
        )
        reply.slack_notified = notified
        db.commit()

    logger.info(
        f"Reply handled: {reply_type.value} from {company.name} "
        f"(confidence: {confidence:.2f}, human_action: {requires_human})"
    )

    return reply
