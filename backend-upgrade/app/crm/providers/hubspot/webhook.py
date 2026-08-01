"""app/crm/providers/hubspot/webhook.py
HubSpot webhook signature verification and event parsing.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import time

from app.core.config import settings
from app.core.logging import get_logger
from app.crm.base.models import CRMEvent, CRMEventType, CRMObjectType

logger = get_logger(__name__)

CLOSED_WON_STAGES = {"closedwon", "closed_won"}
CLOSED_LOST_STAGES = {"closedlost", "closed_lost"}


class HubSpotWebhookHandler:
    """Handles HubSpot webhook signature verification and event parsing."""

    def verify_signature(self, payload: bytes, headers: dict[str, str]) -> bool:
        """
        Verify HubSpot v3 webhook signature.
        HubSpot signs with HMAC-SHA256 of (client_secret + request_body + timestamp).
        """
        secret = settings.HUBSPOT_WEBHOOK_SECRET
        if not secret:
            logger.warning("hubspot_webhook_secret_not_configured")
            return True  # Permissive if not configured

        sig_header = headers.get("X-HubSpot-Signature-v3") or headers.get("x-hubspot-signature-v3")
        timestamp = headers.get("X-HubSpot-Request-Timestamp") or headers.get("x-hubspot-request-timestamp")

        if not sig_header or not timestamp:
            # Fall back to v1 signature
            return self._verify_v1(payload, headers, secret)

        # Reject if timestamp is older than 5 minutes
        try:
            ts = int(timestamp)
            if abs(time.time() * 1000 - ts) > 300_000:
                logger.warning("hubspot_webhook_stale_timestamp")
                return False
        except (ValueError, TypeError):
            return False

        body_str = payload.decode("utf-8", errors="replace")
        msg = f"POST\n{body_str}\n{timestamp}".encode()
        expected = hmac.new(secret.encode(), msg, hashlib.sha256).hexdigest()
        return self.constant_time_compare(sig_header, expected)

    def _verify_v1(self, payload: bytes, headers: dict[str, str], secret: str) -> bool:
        sig = headers.get("X-HubSpot-Signature") or headers.get("x-hubspot-signature")
        if not sig:
            return False
        raw = secret.encode() + payload
        expected = hashlib.sha256(raw).hexdigest()
        return self.constant_time_compare(sig, expected)

    @staticmethod
    def constant_time_compare(a: str, b: str) -> bool:
        import secrets
        return secrets.compare_digest(a.encode(), b.encode())

    def parse_events(self, payload: bytes, workspace_id: str) -> list[CRMEvent]:
        """Parse HubSpot webhook payload into generic CRMEvents."""
        try:
            events_raw = json.loads(payload)
        except json.JSONDecodeError:
            logger.error("hubspot_webhook_invalid_json")
            return []

        if not isinstance(events_raw, list):
            events_raw = [events_raw]

        crm_events: list[CRMEvent] = []
        for ev in events_raw:
            event_type_str = ev.get("subscriptionType", "")
            object_id = str(ev.get("objectId", ""))
            property_name = ev.get("propertyName", "")
            property_value = ev.get("propertyValue", "")

            # Map to CRMObjectType
            if "deal" in event_type_str:
                obj_type = CRMObjectType.OPPORTUNITY
            elif "contact" in event_type_str:
                obj_type = CRMObjectType.CONTACT
            elif "company" in event_type_str:
                obj_type = CRMObjectType.ACCOUNT
            else:
                continue

            # Map to CRMEventType
            if "creation" in event_type_str:
                evt = CRMEventType.CREATED
            elif "deletion" in event_type_str:
                evt = CRMEventType.DELETED
            elif property_name == "dealstage":
                if property_value.lower() in CLOSED_WON_STAGES:
                    evt = CRMEventType.WON
                elif property_value.lower() in CLOSED_LOST_STAGES:
                    evt = CRMEventType.LOST
                else:
                    evt = CRMEventType.STAGE_CHANGED
            else:
                evt = CRMEventType.UPDATED

            crm_events.append(CRMEvent(
                provider="hubspot",
                event_type=evt,
                object_type=obj_type,
                external_id=object_id,
                workspace_id=workspace_id,
                payload=ev,
                raw_payload=ev,
            ))

        return crm_events
