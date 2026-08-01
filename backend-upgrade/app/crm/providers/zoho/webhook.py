"""app/crm/providers/zoho/webhook.py"""
from __future__ import annotations

import json
import secrets

from app.core.logging import get_logger
from app.crm.base.models import CRMEvent, CRMEventType, CRMObjectType

logger = get_logger(__name__)

_MODULE_MAP = {
    "Deals": CRMObjectType.OPPORTUNITY,
    "Accounts": CRMObjectType.ACCOUNT,
    "Contacts": CRMObjectType.CONTACT,
    "Leads": CRMObjectType.LEAD,
}


class ZohoWebhookHandler:
    """
    Handles Zoho CRM webhook notifications.
    Zoho sends notifications to a URL you register via the Notifications API.
    """

    def verify_signature(self, payload: bytes, headers: dict[str, str]) -> bool:
        token = headers.get("x-zoho-webhook-token") or headers.get("X-Zoho-Webhook-Token")
        if not token:
            return True  # Permissive if not configured
        # Token-based validation — compare against a configured secret
        from app.core.config import settings
        expected = settings.ZOHO_CLIENT_SECRET or ""
        return secrets.compare_digest(token, expected[:len(token)])

    def parse_events(self, payload: bytes, workspace_id: str) -> list[CRMEvent]:
        try:
            data = json.loads(payload)
        except json.JSONDecodeError:
            logger.error("zoho_webhook_invalid_json")
            return []

        events: list[CRMEvent] = []
        # Zoho notification format: {"module": "Deals", "operation": "insert", "ids": [...]}
        if isinstance(data, dict):
            data = [data]

        for ev in data:
            module = ev.get("module", "")
            operation = ev.get("operation", "update").lower()
            raw_ids = ev.get("ids") or ev.get("id") or ev.get("entity_id") or []
            if isinstance(raw_ids, (str, int)):
                ids = [str(raw_ids)]
            elif isinstance(raw_ids, list):
                ids = [str(i) for i in raw_ids if i]
            else:
                ids = []

            obj_type = _MODULE_MAP.get(module)
            if not obj_type:
                continue

            if operation in ("insert", "create"):
                evt = CRMEventType.CREATED
            elif operation == "delete":
                evt = CRMEventType.DELETED
            else:
                evt = CRMEventType.UPDATED

            for record_id in ids:
                events.append(CRMEvent(
                    provider="zoho",
                    event_type=evt,
                    object_type=obj_type,
                    external_id=str(record_id),
                    workspace_id=workspace_id,
                    payload=ev,
                    raw_payload=ev,
                ))
        return events
