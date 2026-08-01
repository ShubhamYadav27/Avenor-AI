"""
AI Account Research routes (Phase 5.1).

POST /api/v1/companies/{company_id}/research   — start generation
GET  /api/v1/companies/{company_id}/research   — latest report

Workspace isolation is enforced in the service layer, which raises NotFoundError
for companies outside the caller's workspace. The global handler in main.py
translates that to a 404 — never a 403 — so no cross-tenant existence leaks.
"""
from typing import Any
from fastapi import APIRouter, BackgroundTasks, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.api.auth import CurrentUser
from app.core.exceptions import LLMError
from app.core.logging import get_logger
from app.db.session import db_session, get_db
from app.modules.ai import research_service
from app.modules.ai.provider import LLMProvider, get_provider
from app.modules.ai.schemas import ResearchResponse

logger = get_logger(__name__)

router = APIRouter(prefix="/companies", tags=["ai-research"])


def _bg_generate_research(
    company_id: str,
    workspace_id: Any,
    provider: LLMProvider | None = None,
) -> None:
    with db_session() as db:
        research_service.generate_research(db, company_id, workspace_id, provider=provider)


@router.get("/{company_id}/research", response_model=ResearchResponse)
def get_company_research(
    company_id: str,
    current_user: CurrentUser,
    db: Session = Depends(get_db),
    provider: LLMProvider = Depends(get_provider),
) -> ResearchResponse:
    """
    Return the latest AI research for a company.

    Cached research is returned immediately. `status = "none"` means no report
    has been generated yet; `is_stale = true` means the company's intelligence
    has changed since the report was produced.
    """
    return research_service.get_latest_research(
        db, company_id, current_user.workspace_id, provider=provider
    )


@router.post("/{company_id}/research", response_model=ResearchResponse)
def start_company_research(
    company_id: str,
    current_user: CurrentUser,
    response: Response,
    background_tasks: BackgroundTasks,
    force_refresh: bool = Query(
        False,
        description="Regenerate even if cached research is still valid.",
    ),
    db: Session = Depends(get_db),
    provider: LLMProvider = Depends(get_provider),
) -> ResearchResponse:
    """
    Start AI research generation.

    Returns 200 with the report when a valid cache entry exists (no LLM call),
    otherwise 202 while generation runs in the background. Poll the GET endpoint
    until status becomes `completed` or `failed`.
    """
    try:
        result, should_dispatch = research_service.request_research(
            db,
            company_id,
            current_user.workspace_id,
            force_refresh=force_refresh,
            provider=provider,
        )
    except LLMError as exc:
        # Provider misconfigured or unreachable — a 503, not a 500. The global
        # AvenorError handler would flatten this to 500, so answer here.
        logger.warning(
            "research_request_provider_error",
            company_id=company_id,
            workspace_id=str(current_user.workspace_id),
            code=exc.code,
            error=exc.message,
        )
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return ResearchResponse(
            company_id=company_id,
            status="failed",
            error_message=exc.message,
        )

    if should_dispatch:
        dispatched = False
        try:
            from app.workers.tasks import generate_company_research

            generate_company_research.delay(
                str(current_user.workspace_id),
                str(company_id),
            )
            dispatched = True
        except Exception as exc:
            logger.warning("celery_dispatch_failed_using_background_task", error=str(exc))

        if not dispatched:
            background_tasks.add_task(
                _bg_generate_research,
                company_id,
                current_user.workspace_id,
                provider=provider,
            )

        response.status_code = status.HTTP_202_ACCEPTED
    elif result.status in ("pending", "running"):
        response.status_code = status.HTTP_202_ACCEPTED

    return result
