import uuid
from typing import List, Dict, Callable
from datetime import datetime

from app.modules.event_platform.domain.models import Event, WebhookEndpoint, DeliveryLog, DeliveryStatus
from app.modules.event_platform.application.crypto import generate_signature

class WebhookManager:
    """CRUD operations for Webhook Endpoints."""
    def __init__(self):
        self._endpoints: List[WebhookEndpoint] = []

    def register_endpoint(self, endpoint: WebhookEndpoint):
        self._endpoints.append(endpoint)
        
    def get_endpoints_for_workspace(self, workspace_id: str) -> List[WebhookEndpoint]:
        return [ep for ep in self._endpoints if ep.workspace_id == workspace_id]

class EventDispatcher:
    """Fans out domain events to matching Webhook Endpoints."""
    def __init__(self, manager: WebhookManager):
        self.manager = manager
        self._dlq: List[DeliveryLog] = [] # Dead Letter Queue

    def dispatch(self, event: Event, workspace_id: str) -> List[DeliveryLog]:
        endpoints = self.manager.get_endpoints_for_workspace(workspace_id)
        logs = []
        for ep in endpoints:
            if ep.matches_event(event.type):
                log = DeliveryLog(
                    id=f"del_{uuid.uuid4().hex[:8]}",
                    endpoint_id=ep.id,
                    event_id=event.id,
                    status=DeliveryStatus.QUEUED
                )
                logs.append(log)
        return logs

class DeliveryEngine:
    """
    Worker engine that processes DeliveryLogs.
    In production, this pulls off Kafka and makes Async HTTP POSTs.
    """
    def __init__(self, http_client_mock: Callable):
        self.http_client_mock = http_client_mock # Mock function (url, headers, body) -> (status_code, text)

    def process_delivery(self, log: DeliveryLog, event: Event, endpoint: WebhookEndpoint):
        if log.status == DeliveryStatus.DEAD or log.attempts >= log.max_attempts:
            return

        log.status = DeliveryStatus.PROCESSING
        log.attempts += 1
        
        timestamp = str(int(datetime.utcnow().timestamp()))
        signature = generate_signature(event.payload, timestamp, endpoint.secret)
        
        headers = {
            "Content-Type": "application/json",
            "X-Avenor-Signature": f"t={timestamp},v1={signature}",
            "X-Avenor-Event-Id": event.id,
            "X-Avenor-Event-Type": event.type
        }
        
        status_code, error_msg = self.http_client_mock(endpoint.url, headers, event.payload)
        
        if 200 <= status_code < 300:
            log.status = DeliveryStatus.DELIVERED
            log.delivered_at = datetime.utcnow()
        else:
            log.last_error_code = status_code
            log.last_error_message = error_msg
            
            if log.attempts >= log.max_attempts:
                log.status = DeliveryStatus.DEAD
            else:
                log.status = DeliveryStatus.FAILED
                # Exponential backoff scheduling logic would go here
