from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from pydantic import BaseModel
import secrets

from app.modules.event_platform.domain.models import WebhookEndpoint, WebhookStatus
from app.modules.event_platform.application.services import WebhookManager

router = APIRouter(prefix="/v1/webhooks", tags=["Event Platform - Webhooks"])

_manager = WebhookManager()

# Pre-seed for demonstration
_manager.register_endpoint(WebhookEndpoint(
    id="wh_123",
    workspace_id="ws_001",
    url="https://api.mycompany.com/avenor-webhook",
    subscribed_events=["company.created", "opportunity.*"],
    secret="whsec_" + secrets.token_urlsafe(24)
))

class CreateWebhookRequest(BaseModel):
    url: str
    subscribed_events: List[str]

@router.get("/")
async def list_webhooks(workspace_id: str) -> List[dict]:
    """List all registered webhooks for a workspace."""
    endpoints = _manager.get_endpoints_for_workspace(workspace_id)
    return [
        {
            "id": ep.id,
            "url": ep.url,
            "subscribed_events": ep.subscribed_events,
            "status": ep.status,
            "created_at": ep.created_at
        }
        for ep in endpoints
    ]

@router.post("/")
async def create_webhook(req: CreateWebhookRequest, workspace_id: str) -> dict:
    """Create a new Webhook Endpoint."""
    if not req.url.startswith("https://"):
        raise HTTPException(status_code=400, detail="Webhook URL must use HTTPS")
        
    ep = WebhookEndpoint(
        id=f"wh_{secrets.token_hex(4)}",
        workspace_id=workspace_id,
        url=req.url,
        subscribed_events=req.subscribed_events,
        secret="whsec_" + secrets.token_urlsafe(24)
    )
    _manager.register_endpoint(ep)
    
    return {
        "id": ep.id,
        "url": ep.url,
        "secret": ep.secret # Only returned once!
    }
