"""AI Email Generator routes (Phase 5.2)."""
from typing import Any
from fastapi import APIRouter, BackgroundTasks, Depends, Response, status
from sqlalchemy.orm import Session

from app.api.auth import CurrentUser
from app.core.exceptions import LLMError, ValidationError
from app.core.logging import get_logger
from app.db.session import db_session, get_db
from app.modules.ai import email_service
from app.modules.ai.provider import LLMProvider, get_provider
from app.modules.ai.schemas import (
    EmailGenerateRequest,
    EmailListResponse,
    EmailRegenerateRequest,
    EmailResponse,
)

logger = get_logger(__name__)

router = APIRouter(tags=["ai-emails"])


def _bg_generate_email_rows(
    email_ids: list[str],
    workspace_id: Any,
    provider: LLMProvider | None = None,
) -> None:
    with db_session() as db:
        email_service.generate_email_rows(db, email_ids, workspace_id, provider=provider)


@router.get("/companies/{company_id}/emails", response_model=EmailListResponse)
def list_company_emails(
    company_id: str,
    current_user: CurrentUser,
    db: Session = Depends(get_db),
) -> EmailListResponse:
    """List non-archived AI emails for a company in the caller's workspace."""
    return email_service.list_company_emails(db, company_id, current_user.workspace_id)


@router.post("/companies/{company_id}/emails", response_model=EmailListResponse)
def generate_company_emails(
    company_id: str,
    payload: EmailGenerateRequest,
    current_user: CurrentUser,
    response: Response,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    provider: LLMProvider = Depends(get_provider),
) -> EmailListResponse:
    """
    Generate three AI email variations from the latest completed AI research.

    Returns cached completed variations when research and controls are unchanged.
    Otherwise returns 202 and background generation fills the pending rows.
    """
    try:
        result, should_dispatch = email_service.request_email_generation(
            db,
            company_id,
            current_user.workspace_id,
            payload,
            provider=provider,
        )
    except LLMError as exc:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return EmailListResponse(
            company_id=company_id,
            status="failed",
            error_message=exc.message,
        )
    except ValidationError as exc:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return EmailListResponse(
            company_id=company_id,
            status="failed",
            error_message=exc.message,
        )

    if should_dispatch:
        email_ids = [str(email.id) for email in result.emails]
        dispatched = False
        logger.info(
            "celery_dispatch_before",
            route="POST /companies/{company_id}/emails",
            workspace_id=str(current_user.workspace_id),
            company_id=company_id,
            email_ids=email_ids,
        )
        try:
            from app.workers.tasks import generate_company_ai_emails

            async_res = generate_company_ai_emails.delay(
                str(current_user.workspace_id),
                email_ids,
            )
            dispatched = True
            logger.info(
                "celery_dispatch_after",
                task_id=str(async_res.id),
                route="POST /companies/{company_id}/emails",
                workspace_id=str(current_user.workspace_id),
                company_id=company_id,
                email_ids=email_ids,
            )
        except Exception as exc:
            logger.warning("celery_dispatch_failed_using_background_task", error=str(exc))

        if not dispatched:
            background_tasks.add_task(
                _bg_generate_email_rows,
                email_ids,
                current_user.workspace_id,
                provider=provider,
            )

        response.status_code = status.HTTP_202_ACCEPTED

    return result


@router.get("/emails/{email_id}", response_model=EmailResponse)
def get_email(
    email_id: str,
    current_user: CurrentUser,
    db: Session = Depends(get_db),
) -> EmailResponse:
    """Retrieve one generated email, scoped to the caller's workspace."""
    return email_service.get_email(db, email_id, current_user.workspace_id)


@router.post("/emails/{email_id}/copy", response_model=EmailResponse)
def copy_email(
    email_id: str,
    current_user: CurrentUser,
    db: Session = Depends(get_db),
) -> EmailResponse:
    """Increment the copy counter for a generated email."""
    return email_service.copy_email(db, email_id, current_user.workspace_id)


@router.post("/emails/{email_id}/regenerate", response_model=EmailResponse)
def regenerate_email(
    email_id: str,
    payload: EmailRegenerateRequest,
    current_user: CurrentUser,
    response: Response,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    provider: LLMProvider = Depends(get_provider),
) -> EmailResponse:
    """Generate a new version of a single email variation."""
    _ = payload.force_refresh
    try:
        result, should_dispatch = email_service.request_regeneration(
            db,
            email_id,
            current_user.workspace_id,
            provider=provider,
        )
    except LLMError as exc:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return EmailResponse(
            id=email_id,
            workspace_id=str(current_user.workspace_id),
            company_id="00000000-0000-0000-0000-000000000000",
            research_id="00000000-0000-0000-0000-000000000000",
            email_type="cold_email",
            cta_type="book_meeting",
            tone="professional",
            length="medium",
            variation="A",
            status="failed",
            error_message=exc.message,
        )

    if should_dispatch:
        dispatched = False
        logger.info(
            "celery_dispatch_before",
            route="POST /emails/{email_id}/regenerate",
            workspace_id=str(current_user.workspace_id),
            email_id=email_id,
        )
        try:
            from app.workers.tasks import generate_company_ai_emails

            async_res = generate_company_ai_emails.delay(str(current_user.workspace_id), [str(result.id)])
            dispatched = True
            logger.info(
                "celery_dispatch_after",
                task_id=str(async_res.id),
                route="POST /emails/{email_id}/regenerate",
                workspace_id=str(current_user.workspace_id),
                email_id=email_id,
            )
        except Exception as exc:
            logger.warning("celery_dispatch_failed_using_background_task", error=str(exc))

        if not dispatched:
            background_tasks.add_task(
                _bg_generate_email_rows,
                [str(result.id)],
                current_user.workspace_id,
                provider=provider,
            )

        response.status_code = status.HTTP_202_ACCEPTED
    return result


@router.post("/emails/{email_id}/archive", response_model=EmailResponse)
def archive_email(
    email_id: str,
    current_user: CurrentUser,
    db: Session = Depends(get_db),
) -> EmailResponse:
    """Archive an email draft without deleting it."""
    return email_service.archive_email(db, email_id, current_user.workspace_id)
