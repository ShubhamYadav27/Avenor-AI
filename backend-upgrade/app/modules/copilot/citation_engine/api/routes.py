"""
Citation Engine API Routes (Phase 5.5.5)
Exposes endpoints for querying workspace citation registry and validating AI claim grounding.
"""
from typing import Any, Dict
from fastapi import APIRouter, Depends

from app.api.auth import AuthenticatedUser, get_current_user
from app.modules.copilot.citation_engine.application.engine import citation_engine
from app.modules.copilot.domain.context import ContextIntent

citation_router_api = APIRouter(prefix="", tags=["copilot-citations"])


@citation_router_api.get("/citations", response_model=Dict[str, Any])
async def get_citations(
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    pkg = await citation_engine.generate_citation_package(
        workspace_id=current_user.workspace_id,
        query="Active Workspace Citation Registry Request",
        intent=ContextIntent.GENERAL_STRATEGY,
    )

    return {
        "workspace_id": str(pkg.workspace_id),
        "total_citations": pkg.registry.total_citations,
        "overall_grounding_score": pkg.overall_confidence_score,
        "grounding_status": pkg.grounding_status.value,
        "citations": [
            {
                "citation_id": m.citation_id,
                "title": m.title,
                "category": m.category,
                "confidence_score": m.confidence_score,
                "verified": m.verified,
                "snippet": m.snippet,
            }
            for m in pkg.registry.citations_map.values()
        ],
    }


@citation_router_api.post("/grounding/validate", response_model=Dict[str, Any])
async def validate_claim(
    claim: str,
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    res = citation_engine.validate_claim(claim)
    return {
        "is_grounded": res.is_grounded,
        "grounding_score": res.grounding_score,
        "verified_claims_count": res.verified_claims_count,
        "status": res.status.value,
        "unsupported_warnings": res.unsupported_warnings,
    }
