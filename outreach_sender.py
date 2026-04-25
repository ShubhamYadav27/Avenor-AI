"""
Outreach sender.
Uses Instantly.ai API if configured, falls back to mock sender for development.
Mock sender logs everything to a local file for inspection.
"""
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
import httpx
from sqlalchemy.orm import Session

from app.config import settings
from app.models import OutreachMessage, OutreachStatus, Company, Contact

logger = logging.getLogger(__name__)

INSTANTLY_BASE = "https://api.instantly.ai/api/v1"
MOCK_LOG_PATH = Path("mock_sent_emails.jsonl")


# ─────────────────────────────────────────────
# Instantly Sender
# ─────────────────────────────────────────────

class InstantlySender:
    def __init__(self):
        self.api_key = settings.INSTANTLY_API_KEY
        self.campaign_id = settings.INSTANTLY_CAMPAIGN_ID
        self.headers = {"Content-Type": "application/json"}

    def add_lead_to_campaign(
        self,
        email: str,
        first_name: str,
        last_name: str,
        company_name: str,
        custom_variables: dict = None,
    ) -> dict:
        """Add a lead to an Instantly campaign (they handle sequencing)."""
        payload = {
            "api_key": self.api_key,
            "campaign_id": self.campaign_id,
            "skip_if_in_workspace": True,   # dedupe across campaigns
            "leads": [
                {
                    "email": email,
                    "first_name": first_name,
                    "last_name": last_name,
                    "company_name": company_name,
                    **(custom_variables or {}),
                }
            ],
        }

        resp = httpx.post(
            f"{INSTANTLY_BASE}/lead/add",
            json=payload,
            timeout=15,
        )
        resp.raise_for_status()
        return resp.json()

    def send_email_directly(
        self,
        to_email: str,
        subject: str,
        body: str,
        from_name: str,
    ) -> dict:
        """
        Send a one-off email directly (not via campaign sequence).
        Useful for manual follow-ups or immediate sends.
        """
        payload = {
            "api_key": self.api_key,
            "campaign_id": self.campaign_id,
            "email_list": [to_email],
            "subject": subject,
            "body": body,
            "from_name": from_name,
        }

        resp = httpx.post(
            f"{INSTANTLY_BASE}/email/send",
            json=payload,
            timeout=15,
        )
        resp.raise_for_status()
        return resp.json()


# ─────────────────────────────────────────────
# Mock Sender (for development)
# ─────────────────────────────────────────────

class MockSender:
    """
    Simulates sending without hitting any real API.
    Writes to mock_sent_emails.jsonl for inspection.
    """

    def send(
        self,
        to_email: str,
        subject: str,
        body: str,
        from_name: str,
        company_name: str,
        message_id: str,
    ) -> dict:
        record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "message_id": message_id,
            "to": to_email,
            "company": company_name,
            "from_name": from_name,
            "subject": subject,
            "body": body,
            "status": "mock_sent",
        }

        # Append to JSONL log
        with open(MOCK_LOG_PATH, "a") as f:
            f.write(json.dumps(record) + "\n")

        logger.info(f"[MOCK] Email sent to {to_email} ({company_name}): '{subject}'")
        return {"status": "mock_sent", "message_id": message_id}


# ─────────────────────────────────────────────
# Unified Send Function
# ─────────────────────────────────────────────

def send_outreach_message(
    db: Session,
    message: OutreachMessage,
    from_name: str = "Alex",
) -> dict:
    """
    Sends a message that has passed the quality gate.
    Routes to Instantly if configured, otherwise mock.
    Updates the OutreachMessage record on success.
    """
    if message.status == OutreachStatus.SENT:
        logger.warning(f"Message {message.id} already sent — skipping")
        return {"status": "already_sent"}

    if not message.passed_quality_gate:
        logger.error(f"Message {message.id} has not passed quality gate — refusing to send")
        return {"status": "blocked", "reason": "quality_gate_failed"}

    contact: Contact = db.query(Contact).get(message.contact_id)
    company: Company = db.query(Company).get(message.company_id)

    if not contact or not contact.email:
        logger.error(f"No email for contact {message.contact_id}")
        return {"status": "error", "reason": "no_email"}

    result = {}

    # Route to appropriate sender
    if settings.INSTANTLY_API_KEY and settings.INSTANTLY_CAMPAIGN_ID:
        logger.info(f"Sending via Instantly to {contact.email}")
        try:
            sender = InstantlySender()
            result = sender.add_lead_to_campaign(
                email=contact.email,
                first_name=contact.first_name or "",
                last_name=contact.last_name or "",
                company_name=company.name,
                custom_variables={
                    "custom_subject": message.subject,
                    "custom_opener": message.body,
                },
            )
            result["channel"] = "instantly"
        except Exception as e:
            logger.error(f"Instantly send failed: {e}")
            return {"status": "error", "reason": str(e)}
    else:
        logger.info(f"[DEV] Using mock sender for {contact.email}")
        mock = MockSender()
        result = mock.send(
            to_email=contact.email,
            subject=message.subject,
            body=message.body,
            from_name=from_name,
            company_name=company.name,
            message_id=str(message.id),
        )
        result["channel"] = "mock"

    # Update message record
    message.status = OutreachStatus.SENT
    message.sent_at = datetime.now(timezone.utc)
    message.instantly_id = result.get("id") or result.get("message_id")
    db.commit()

    logger.info(f"Sent message {message.id} to {contact.email} via {result.get('channel')}")
    return result


def send_batch(
    db: Session,
    messages: list[OutreachMessage],
    from_name: str = "Alex",
    dry_run: bool = False,
) -> list[dict]:
    """Send multiple messages. dry_run=True previews without sending."""
    results = []
    for msg in messages:
        if dry_run:
            contact = db.query(Contact).get(msg.contact_id)
            results.append({
                "message_id": str(msg.id),
                "to": contact.email if contact else "unknown",
                "subject": msg.subject,
                "word_count": msg.word_count,
                "quality_passed": msg.passed_quality_gate,
                "status": "dry_run",
            })
        else:
            result = send_outreach_message(db, msg, from_name=from_name)
            results.append({**result, "message_id": str(msg.id)})
    return results
