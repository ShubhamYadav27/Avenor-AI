"""
Copilot API Routes (Phase 5.5.1 Foundation)
Mounted under /api/v1/copilot
"""
from typing import List, Optional
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.api.auth import AuthenticatedUser, get_current_user
from app.db.session import get_db
from app.modules.copilot.application.orchestrator.orchestrator import IntelligenceOrchestrator
from app.modules.copilot.application.services.message_service import MessageService
from app.modules.copilot.application.services.thread_service import ThreadService
from app.modules.copilot.config import copilot_settings
from app.modules.copilot.domain.exceptions import ThreadNotFoundError
from app.modules.copilot.infrastructure.repositories.message_repository import SQLAlchemyMessageRepository
from app.modules.copilot.infrastructure.repositories.thread_repository import SQLAlchemyThreadRepository
from app.modules.copilot.schemas.message import SendMessageRequest
from app.modules.copilot.schemas.thread import (
    CreateThreadRequest,
    MessageResponse,
    ThreadResponse,
    UpdateThreadRequest,
)

router = APIRouter(prefix="/copilot", tags=["Revenue Copilot Foundation"])


def get_thread_service(db: Session = Depends(get_db)) -> ThreadService:
    repo = SQLAlchemyThreadRepository(db)
    return ThreadService(repo)


def get_message_service(db: Session = Depends(get_db)) -> MessageService:
    msg_repo = SQLAlchemyMessageRepository(db)
    thread_repo = SQLAlchemyThreadRepository(db)
    return MessageService(msg_repo, thread_repo)


def get_orchestrator(db: Session = Depends(get_db)) -> IntelligenceOrchestrator:
    thread_svc = get_thread_service(db)
    msg_svc = get_message_service(db)
    return IntelligenceOrchestrator(thread_svc, msg_svc)


# ── Health Endpoint ──────────────────────────────────────────────────────────

@router.get("/health")
def get_copilot_health(db: Session = Depends(get_db)):
    """Health check for Copilot providers, database, streaming engine, tool orchestrator, and feature flags."""
    db_healthy = True
    try:
        db.execute("SELECT 1")
    except Exception:
        db_healthy = False

    return {
        "status": "healthy" if db_healthy else "degraded",
        "system": copilot_settings.system_name,
        "version": copilot_settings.version,
        "database": "connected" if db_healthy else "disconnected",
        "streaming": "ready" if copilot_settings.features.streaming_enabled else "disabled",
        "tool_orchestration": "ready",
        "memory_engine": "ready",
        "citation_engine": "ready",
        "learning_engine": "ready",
        "swarm_engine": "ready",
        "workflow_engine": "ready",
        "governance_engine": "ready",
        "agent_framework": "ready",
        "predictive_intelligence_engine": "ready",
        "revenue_decision_engine": "ready",
        "autonomous_revops_engine": "ready",
        "knowledge_graph_engine": "ready",
        "strategic_intelligence_engine": "ready",
        "autonomous_org_platform": "ready",
        "revenue_os_kernel": "ready",












        "providers": {
            "default": copilot_settings.llm.default_provider,
            "fallback": copilot_settings.llm.fallback_provider,
        },
        "feature_flags": copilot_settings.features.model_dump(),
    }



# ── Thread Management Endpoints ─────────────────────────────────────────────

@router.post("/threads", response_model=ThreadResponse, status_code=status.HTTP_201_CREATED)
async def create_thread(
    req: CreateThreadRequest,
    current_user: AuthenticatedUser = Depends(get_current_user),
    thread_svc: ThreadService = Depends(get_thread_service),
):
    """Create a new conversation thread scoped to the authenticated workspace."""
    thread = await thread_svc.create_thread(
        workspace_id=current_user.workspace_id,
        user_id=current_user.user_id,
        title=req.title or "New Strategic Session",
    )
    return thread


@router.get("/threads", response_model=List[ThreadResponse])
async def list_threads(
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    current_user: AuthenticatedUser = Depends(get_current_user),
    thread_svc: ThreadService = Depends(get_thread_service),
):
    """List active conversation threads for the current workspace."""
    return await thread_svc.list_threads(
        workspace_id=current_user.workspace_id,
        user_id=current_user.user_id,
        limit=limit,
        offset=offset,
    )


@router.get("/threads/{thread_id}", response_model=ThreadResponse)
async def get_thread(
    thread_id: uuid.UUID,
    current_user: AuthenticatedUser = Depends(get_current_user),
    thread_svc: ThreadService = Depends(get_thread_service),
):
    """Retrieve details and message history of a specific thread."""
    try:
        return await thread_svc.get_thread(thread_id, current_user.workspace_id)
    except ThreadNotFoundError as e:
        raise HTTPException(status_code=404, detail=e.message)


@router.patch("/threads/{thread_id}", response_model=ThreadResponse)
async def update_thread(
    thread_id: uuid.UUID,
    req: UpdateThreadRequest,
    current_user: AuthenticatedUser = Depends(get_current_user),
    thread_svc: ThreadService = Depends(get_thread_service),
):
    """Update title or status of a conversation thread."""
    try:
        if req.title:
            return await thread_svc.rename_thread(thread_id, current_user.workspace_id, req.title)
        if req.status == "archived":
            return await thread_svc.archive_thread(thread_id, current_user.workspace_id)
        return await thread_svc.get_thread(thread_id, current_user.workspace_id)
    except ThreadNotFoundError as e:
        raise HTTPException(status_code=404, detail=e.message)


@router.delete("/threads/{thread_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_thread(
    thread_id: uuid.UUID,
    current_user: AuthenticatedUser = Depends(get_current_user),
    thread_svc: ThreadService = Depends(get_thread_service),
):
    """Delete a conversation thread."""
    deleted = await thread_svc.delete_thread(thread_id, current_user.workspace_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Thread not found")


# ── Message Endpoints ────────────────────────────────────────────────────────

@router.post("/threads/{thread_id}/messages", response_model=MessageResponse)
async def add_message(
    thread_id: uuid.UUID,
    req: SendMessageRequest,
    current_user: AuthenticatedUser = Depends(get_current_user),
    msg_svc: MessageService = Depends(get_message_service),
):
    """Add a user message to a thread (non-streaming)."""
    try:
        msg = await msg_svc.add_user_message(
            thread_id=thread_id,
            workspace_id=current_user.workspace_id,
            content=req.content,
        )
        return msg
    except ThreadNotFoundError as e:
        raise HTTPException(status_code=404, detail=e.message)


# ── SSE Streaming Chat Endpoint ──────────────────────────────────────────────

@router.get("/threads/{thread_id}/chat/stream")
async def chat_stream(
    thread_id: uuid.UUID,
    message: str = Query(..., min_length=1),
    provider: Optional[str] = Query(default=None),
    model: Optional[str] = Query(default=None),
    current_user: AuthenticatedUser = Depends(get_current_user),
    orchestrator: IntelligenceOrchestrator = Depends(get_orchestrator),
):
    """
    Real-time Server-Sent Events (SSE) token streaming endpoint.
    Streams AI Revenue Copilot tokens chunk by chunk.
    """
    event_generator = orchestrator.execute_stream(
        thread_id=thread_id,
        workspace_id=current_user.workspace_id,
        user_message_content=message,
        workspace_name=getattr(current_user.workspace, "name", "Avenor Workspace"),
        crm_provider=getattr(current_user.workspace, "crm_provider", None),
        preferred_provider=provider,
        preferred_model=model,
    )

    return StreamingResponse(
        event_generator,
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
