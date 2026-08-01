"""AI Sales Briefing routes (Phase 5.3)."""
from typing import Any
from fastapi import APIRouter, BackgroundTasks, Depends, Response, status
from sqlalchemy.orm import Session

from app.api.auth import CurrentUser
from app.core.exceptions import LLMError, ValidationError
from app.core.logging import get_logger
from app.db.session import db_session, get_db
from app.modules.ai import briefing_service
from app.modules.ai.provider import LLMProvider, get_provider
from app.modules.ai.schemas import (
    BriefingGenerateRequest,
    BriefingListResponse,
    BriefingRegenerateRequest,
    BriefingResponse,
)

logger = get_logger(__name__)

router = APIRouter(tags=["ai-briefings"])


def _bg_generate_briefing(
    briefing_id: str,
    workspace_id: Any,
    provider: LLMProvider | None = None,
) -> None:
    with db_session() as db:
        briefing_service.generate_briefing_row(db, briefing_id, workspace_id, provider=provider)


@router.get("/companies/{company_id}/briefings", response_model=BriefingListResponse)
def list_company_briefings(
    company_id: str,
    current_user: CurrentUser,
    db: Session = Depends(get_db),
) -> BriefingListResponse:
    """List non-archived AI sales briefings for a company."""
    return briefing_service.list_company_briefings(db, company_id, current_user.workspace_id)


@router.post("/companies/{company_id}/briefings", response_model=BriefingResponse)
def generate_company_briefing(
    company_id: str,
    payload: BriefingGenerateRequest,
    current_user: CurrentUser,
    response: Response,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    provider: LLMProvider = Depends(get_provider),
) -> BriefingResponse:
    """
    Generate an AI sales briefing from existing Avenor intelligence.

    Returns a cached completed briefing when the research hash, prompt and model
    are unchanged. Otherwise returns 202 while background generation runs.
    """
    try:
        result, should_dispatch = briefing_service.request_briefing_generation(
            db,
            company_id,
            current_user.workspace_id,
            payload,
            provider=provider,
        )
    except LLMError as exc:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return BriefingResponse(
            id="00000000-0000-0000-0000-000000000000",
            workspace_id=str(current_user.workspace_id),
            company_id=company_id,
            research_id="00000000-0000-0000-0000-000000000000",
            status="failed",
            error_message=exc.message,
        )
    except ValidationError as exc:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return BriefingResponse(
            id="00000000-0000-0000-0000-000000000000",
            workspace_id=str(current_user.workspace_id),
            company_id=company_id,
            research_id="00000000-0000-0000-0000-000000000000",
            status="failed",
            error_message=exc.message,
        )

    if should_dispatch:
        dispatched = False
        try:
            from app.workers.tasks import generate_company_ai_briefing

            generate_company_ai_briefing.delay(str(current_user.workspace_id), result.id)
            dispatched = True
        except Exception as exc:
            logger.warning("celery_dispatch_failed_using_background_task", error=str(exc))

        if not dispatched:
            background_tasks.add_task(
                _bg_generate_briefing,
                result.id,
                current_user.workspace_id,
                provider=provider,
            )

        response.status_code = status.HTTP_202_ACCEPTED
    elif result.status in ("pending", "running"):
        response.status_code = status.HTTP_202_ACCEPTED

    return result


@router.get("/briefings/{briefing_id}", response_model=BriefingResponse)
def get_briefing(
    briefing_id: str,
    current_user: CurrentUser,
    db: Session = Depends(get_db),
) -> BriefingResponse:
    """Retrieve one AI sales briefing, scoped to the caller's workspace."""
    return briefing_service.get_briefing(db, briefing_id, current_user.workspace_id)


@router.post("/briefings/{briefing_id}/regenerate", response_model=BriefingResponse)
def regenerate_briefing(
    briefing_id: str,
    payload: BriefingRegenerateRequest,
    current_user: CurrentUser,
    response: Response,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    provider: LLMProvider = Depends(get_provider),
) -> BriefingResponse:
    """Generate a new briefing version from the latest completed research."""
    _ = payload.force_refresh
    try:
        result, should_dispatch = briefing_service.request_regeneration(
            db,
            briefing_id,
            current_user.workspace_id,
            provider=provider,
        )
    except LLMError as exc:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return BriefingResponse(
            id=briefing_id,
            workspace_id=str(current_user.workspace_id),
            company_id="00000000-0000-0000-0000-000000000000",
            research_id="00000000-0000-0000-0000-000000000000",
            status="failed",
            error_message=exc.message,
        )

    if should_dispatch:
        dispatched = False
        try:
            from app.workers.tasks import generate_company_ai_briefing

            generate_company_ai_briefing.delay(str(current_user.workspace_id), result.id)
            dispatched = True
        except Exception as exc:
            logger.warning("celery_dispatch_failed_using_background_task", error=str(exc))

        if not dispatched:
            background_tasks.add_task(
                _bg_generate_briefing,
                result.id,
                current_user.workspace_id,
                provider=provider,
            )

        response.status_code = status.HTTP_202_ACCEPTED
    return result


@router.post("/briefings/{briefing_id}/archive", response_model=BriefingResponse)
def archive_briefing(
    briefing_id: str,
    current_user: CurrentUser,
    db: Session = Depends(get_db),
) -> BriefingResponse:
    """Archive a briefing without deleting its audit trail."""
    return briefing_service.archive_briefing(db, briefing_id, current_user.workspace_id)
