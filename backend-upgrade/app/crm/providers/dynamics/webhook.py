"""app/crm/providers/dynamics/webhook.py"""
from __future__ import annotations

import hashlib
import hmac
import json
import secrets

from app.core.logging import get_logger
from app.crm.base.models import CRMEvent, CRMEventType, CRMObjectType

logger = get_logger(__name__)

_ENTITY_MAP = {
    "opportunity": CRMObjectType.OPPORTUNITY,
    "account": CRMObjectType.ACCOUNT,
    "contact": CRMObjectType.CONTACT,
    "lead": CRMObjectType.LEAD,
}
_MESSAGE_MAP = {
    "Create": CRMEventType.CREATED,
    "Update": CRMEventType.UPDATED,
    "Delete": CRMEventType.DELETED,
}


class DynamicsWebhookHandler:
    """
    Handles Dynamics 365 HTTP webhooks (Plugin/Custom API webhooks).
    Dynamics sends JSON payloads with MessageName and EntityName fields.
    """

    def verify_signature(self, payload: bytes, headers: dict[str, str]) -> bool:
        # Dynamics webhooks can be configured with a shared secret
        # X-Dynamics-Signature header (custom plugin implementation)
        sig = headers.get("X-Dynamics-Signature") or headers.get("x-dynamics-signature")
        secret = headers.get("X-Dynamics-Secret") or headers.get("x-dynamics-secret", "")
        if not sig or not secret:
            return True  # Permissive if not configured
        expected = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
        return secrets.compare_digest(sig, expected)

    def parse_events(self, payload: bytes, workspace_id: str) -> list[CRMEvent]:
        try:
            data = json.loads(payload)
        except json.JSONDecodeError:
            logger.error("dynamics_webhook_invalid_json")
            return []

        if not isinstance(data, list):
            data = [data]

        events: list[CRMEvent] = []
        for ev in data:
            entity = ev.get("EntityName", ev.get("PrimaryEntityName", "")).lower()
            message = ev.get("MessageName", "Update")
            record_id = ev.get("PrimaryEntityId", ev.get("InputParameters", {}).get("Target", {}).get("Id", ""))

            if not record_id:
                continue

            obj_type = _ENTITY_MAP.get(entity)
            if not obj_type:
                continue

            evt = _MESSAGE_MAP.get(message, CRMEventType.UPDATED)
            events.append(CRMEvent(
                provider="dynamics",
                event_type=evt,
                object_type=obj_type,
                external_id=record_id,
                workspace_id=workspace_id,
                payload=ev,
                raw_payload=ev,
            ))
        return events
