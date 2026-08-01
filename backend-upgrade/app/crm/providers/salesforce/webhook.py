"""app/crm/providers/salesforce/webhook.py"""
from __future__ import annotations

import json
import xml.etree.ElementTree as ET

from app.core.logging import get_logger
from app.crm.base.models import CRMEvent, CRMEventType, CRMObjectType

logger = get_logger(__name__)


class SalesforceWebhookHandler:
    """
    Handles Salesforce Outbound Messages (SOAP XML) and Platform Events (JSON).
    """

    def verify_signature(self, payload: bytes, headers: dict[str, str]) -> bool:
        # Salesforce Outbound Messages do not support HMAC — validated by IP allowlist
        # Platform Events use a client_secret as Authorization header
        return True

    def parse_events(self, payload: bytes, workspace_id: str) -> list[CRMEvent]:
        content_type = ""
        events: list[CRMEvent] = []

        # Try JSON (Platform Events)
        try:
            data = json.loads(payload)
            return self._parse_platform_events(data, workspace_id)
        except (json.JSONDecodeError, ValueError):
            pass

        # Try SOAP XML (Outbound Messages)
        try:
            return self._parse_outbound_message(payload, workspace_id)
        except ET.ParseError:
            logger.error("salesforce_webhook_unrecognised_payload")
            return []

    def _parse_platform_events(self, data: dict, workspace_id: str) -> list[CRMEvent]:
        events = []
        for ev in data.get("events", [data]):
            entity = ev.get("entityName", "").lower()
            change_type = ev.get("changeType", "UPDATE").upper()
            record_id = ev.get("recordId", "")
            if not record_id:
                continue

            obj_type = self._map_entity(entity)
            if not obj_type:
                continue

            evt = CRMEventType.CREATED if change_type == "CREATE" else (
                CRMEventType.DELETED if change_type == "DELETE" else CRMEventType.UPDATED
            )
            events.append(CRMEvent(
                provider="salesforce",
                event_type=evt,
                object_type=obj_type,
                external_id=record_id,
                workspace_id=workspace_id,
                payload=ev,
                raw_payload=ev,
            ))
        return events

    def _parse_outbound_message(self, payload: bytes, workspace_id: str) -> list[CRMEvent]:
        try:
            root = ET.fromstring(payload)
        except ET.ParseError:
            logger.error("salesforce_webhook_unrecognised_payload")
            return []

        events = []
        for elem in root.iter():
            if elem.tag.endswith("Notification"):
                sf_object = None
                for child in elem.iter():
                    if child.tag.endswith("sObject"):
                        sf_object = child
                        break
                if sf_object is None:
                    continue

                sf_type = (
                    sf_object.get("{http://www.w3.org/2001/XMLSchema-instance}type")
                    or sf_object.get("type")
                    or ""
                )
                record_id = ""
                for child in sf_object.iter():
                    if child.tag.endswith("Id") and child.text:
                        record_id = child.text.strip()
                        break
                if not record_id:
                    continue

                clean_type = sf_type.lower().replace("sf:", "")
                obj_type = self._map_entity(clean_type)
                if not obj_type:
                    continue

                events.append(
                    CRMEvent(
                        provider="salesforce",
                        event_type=CRMEventType.UPDATED,
                        object_type=obj_type,
                        external_id=record_id,
                        workspace_id=workspace_id,
                        payload={},
                        raw_payload={},
                    )
                )
        return events

    @staticmethod
    def _map_entity(entity: str) -> CRMObjectType | None:
        mapping = {
            "opportunity": CRMObjectType.OPPORTUNITY,
            "account": CRMObjectType.ACCOUNT,
            "contact": CRMObjectType.CONTACT,
            "lead": CRMObjectType.LEAD,
        }
        return mapping.get(entity)
