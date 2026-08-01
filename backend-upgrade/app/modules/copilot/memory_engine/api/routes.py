"""
Memory Engine API Routes (Phase 5.5.4)
Exposes endpoints for querying, listing, and persisting workspace memories.
"""
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, Query, status

from app.api.auth import AuthenticatedUser, get_current_user
from app.modules.copilot.domain.memory_entities import MemoryItem
from app.modules.copilot.domain.memory_value_objects import MemoryCategory, MemoryImportance, MemoryTier
from app.modules.copilot.memory_engine.application.engine import memory_engine
from app.modules.copilot.memory_engine.infrastructure.adapters.in_memory_adapter import in_memory_adapter

memory_router_api = APIRouter(prefix="/memories", tags=["copilot-memories"])


@memory_router_api.get("", response_model=List[Dict[str, Any]])
async def query_memories(
    category: Optional[str] = Query(None, description="Memory category filter"),
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    categories = [category] if category else None
    items = await in_memory_adapter.query_memories(
        workspace_id=current_user.workspace_id,
        categories=categories,
        limit=50,
    )
    return [
        {
            "id": m.id,
            "category": m.category.value,
            "tier": m.tier.value,
            "content": m.content,
            "confidence_score": m.confidence_score,
            "importance": m.importance.name,
            "provenance_id": m.provenance_id,
            "citation_id": m.citation_id,
            "created_at": m.created_at.isoformat(),
        }
        for m in items
    ]


@memory_router_api.post("", status_code=status.HTTP_201_CREATED)
async def store_memory(
    content: str,
    category: str = "workspace",
    importance: str = "NORMAL",
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    try:
        mem_cat = MemoryCategory(category.lower())
    except ValueError:
        mem_cat = MemoryCategory.WORKSPACE

    try:
        imp = MemoryImportance[importance.upper()]
    except KeyError:
        imp = MemoryImportance.NORMAL

    item = MemoryItem(
        workspace_id=current_user.workspace_id,
        category=mem_cat,
        tier=MemoryTier.LONG_TERM,
        content=content,
        confidence_score=1.0,
        importance=imp,
        source_type="user_explicit",
    )
    res = await memory_engine.consolidate_and_persist(current_user.workspace_id, [item])
    return {"status": "persisted", "memory_id": item.id, "citation_id": item.citation_id}
