"""AI Sales Coach routes (Phase 5.4)."""
from typing import Any
from fastapi import APIRouter, BackgroundTasks, Depends, Response, status
from sqlalchemy.orm import Session

from app.api.auth import CurrentUser
from app.core.exceptions import LLMError, ValidationError
from app.core.logging import get_logger
from app.db.session import db_session, get_db
from app.modules.ai import sales_coach_service
from app.modules.ai.provider import LLMProvider, get_provider
from app.modules.ai.schemas import (
    SalesCoachGenerateRequest,
    SalesCoachListResponse,
    SalesCoachRegenerateRequest,
    SalesCoachResponse,
)

logger = get_logger(__name__)

router = APIRouter(tags=["ai-sales-coaching"])


def _bg_generate_sales_coaching(
    coaching_id: str,
    workspace_id: Any,
    provider: LLMProvider | None = None,
) -> None:
    with db_session() as db:
        sales_coach_service.generate_sales_coaching_row(db, coaching_id, workspace_id, provider=provider)


@router.get("/companies/{company_id}/sales-coaching", response_model=SalesCoachListResponse)
def list_company_sales_coaching(
    company_id: str,
    current_user: CurrentUser,
    db: Session = Depends(get_db),
) -> SalesCoachListResponse:
    """List non-archived AI sales coaching for a company."""
    return sales_coach_service.list_company_sales_coaching(
        db, company_id, current_user.workspace_id
    )


@router.post("/companies/{company_id}/sales-coaching", response_model=SalesCoachResponse)
def generate_company_sales_coaching(
    company_id: str,
    payload: SalesCoachGenerateRequest,
    current_user: CurrentUser,
    response: Response,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    provider: LLMProvider = Depends(get_provider),
) -> SalesCoachResponse:
    """
    Generate AI sales coaching from existing Avenor intelligence.

    Returns cached completed coaching when research, briefing, prompt and model
    are unchanged. Otherwise returns 202 while background generation runs.
    """
    try:
        result, should_dispatch = sales_coach_service.request_sales_coaching_generation(
            db,
            company_id,
            current_user.workspace_id,
            payload,
            provider=provider,
        )
    except LLMError as exc:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return SalesCoachResponse(
            id="00000000-0000-0000-0000-000000000000",
            workspace_id=str(current_user.workspace_id),
            company_id=company_id,
            research_id="00000000-0000-0000-0000-000000000000",
            status="failed",
            error_message=exc.message,
        )
    except ValidationError as exc:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return SalesCoachResponse(
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
            from app.workers.tasks import generate_company_ai_sales_coaching

            generate_company_ai_sales_coaching.delay(str(current_user.workspace_id), result.id)
            dispatched = True
        except Exception as exc:
            logger.warning("celery_dispatch_failed_using_background_task", error=str(exc))

        if not dispatched:
            background_tasks.add_task(
                _bg_generate_sales_coaching,
                result.id,
                current_user.workspace_id,
                provider=provider,
            )

        response.status_code = status.HTTP_202_ACCEPTED
    elif result.status in ("pending", "running"):
        response.status_code = status.HTTP_202_ACCEPTED

    return result


@router.get("/sales-coaching/{coaching_id}", response_model=SalesCoachResponse)
def get_sales_coaching(
    coaching_id: str,
    current_user: CurrentUser,
    db: Session = Depends(get_db),
) -> SalesCoachResponse:
    """Retrieve one AI sales coaching row, scoped to the caller's workspace."""
    return sales_coach_service.get_sales_coaching(
        db, coaching_id, current_user.workspace_id
    )


@router.post("/sales-coaching/{coaching_id}/regenerate", response_model=SalesCoachResponse)
def regenerate_sales_coaching(
    coaching_id: str,
    payload: SalesCoachRegenerateRequest,
    current_user: CurrentUser,
    response: Response,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    provider: LLMProvider = Depends(get_provider),
) -> SalesCoachResponse:
    """Generate a new sales coaching version from the latest completed intelligence."""
    _ = payload.force_refresh
    try:
        result, should_dispatch = sales_coach_service.request_regeneration(
            db,
            coaching_id,
            current_user.workspace_id,
            provider=provider,
        )
    except LLMError as exc:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return SalesCoachResponse(
            id=coaching_id,
            workspace_id=str(current_user.workspace_id),
            company_id="00000000-0000-0000-0000-000000000000",
            research_id="00000000-0000-0000-0000-000000000000",
            status="failed",
            error_message=exc.message,
        )

    if should_dispatch:
        dispatched = False
        try:
            from app.workers.tasks import generate_company_ai_sales_coaching

            generate_company_ai_sales_coaching.delay(str(current_user.workspace_id), result.id)
            dispatched = True
        except Exception as exc:
            logger.warning("celery_dispatch_failed_using_background_task", error=str(exc))

        if not dispatched:
            background_tasks.add_task(
                _bg_generate_sales_coaching,
                result.id,
                current_user.workspace_id,
                provider=provider,
            )

        response.status_code = status.HTTP_202_ACCEPTED
    return result


@router.post("/sales-coaching/{coaching_id}/archive", response_model=SalesCoachResponse)
def archive_sales_coaching(
    coaching_id: str,
    current_user: CurrentUser,
    db: Session = Depends(get_db),
) -> SalesCoachResponse:
    """Archive sales coaching without deleting its audit trail."""
    return sales_coach_service.archive_sales_coaching(
        db, coaching_id, current_user.workspace_id
    )
