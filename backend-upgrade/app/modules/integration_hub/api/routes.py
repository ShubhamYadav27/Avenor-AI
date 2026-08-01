from fastapi import APIRouter, Depends, HTTPException, Request, BackgroundTasks
from typing import List, Dict, Any
from uuid import UUID
import logging

from app.modules.integration_hub.application.provider_registry import provider_registry
from app.modules.integration_hub.application.oauth_manager import OAuthManager
from app.modules.integration_hub.application.webhook_engine import WebhookEngine
from app.modules.integration_hub.workers.integration_worker import trigger_incremental_sync

router = APIRouter(prefix="/integrations", tags=["Integration Hub"])
oauth_manager = OAuthManager()
webhook_engine = WebhookEngine()
logger = logging.getLogger(__name__)

@router.get("/providers", response_model=Dict[str, dict])
async def list_available_providers():
    """Lists all natively supported providers in the Integration Hub."""
    return provider_registry.list_providers()

@router.get("/auth/{provider_name}/url")
async def get_authorization_url(provider_name: str, redirect_uri: str):
    """Generates the OAuth consent URL for a specific provider."""
    url = oauth_manager.get_authorization_url(provider_name, redirect_uri)
    if not url:
        raise HTTPException(status_code=400, detail=f"Provider {provider_name} does not support OAuth.")
    return {"authorization_url": url}

@router.post("/auth/{provider_name}/callback")
async def oauth_callback(provider_name: str, code: str, state: str, redirect_uri: str, tenant_id: UUID):
    """Exchanges the authorization code for an access token via PKCE."""
    try:
        credentials_id = await oauth_manager.exchange_callback(
            provider_name=provider_name, 
            code=code, 
            state=state, 
            redirect_uri=redirect_uri, 
            tenant_id=tenant_id
        )
        return {"status": "success", "credentials_id": credentials_id}
    except Exception as e:
        logger.error(f"OAuth callback failed: {str(e)}")
        raise HTTPException(status_code=400, detail="Authentication failed")

@router.post("/webhooks/{provider_name}")
async def handle_provider_webhook(provider_name: str, request: Request, background_tasks: BackgroundTasks):
    """Unified ingress for all provider webhooks."""
    body = await request.body()
    headers = dict(request.headers)
    
    # Process webhook verification and routing in background to return 200 OK fast
    background_tasks.add_task(webhook_engine.process_incoming_webhook, provider_name, headers, body)
    
    return {"status": "accepted"}

@router.post("/connections/{connection_id}/sync")
async def trigger_manual_sync(connection_id: UUID, entity_type: str):
    """Triggers an out-of-band incremental sync for a specific connection."""
    # Enqueue to Celery worker immediately
    # trigger_incremental_sync.delay(connection_id, entity_type)
    trigger_incremental_sync(None, connection_id, entity_type)
    return {"status": "sync_queued"}
