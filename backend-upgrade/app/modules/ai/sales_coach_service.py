"""AI Sales Coach service (Phase 5.4)."""
import hashlib
import json
import time
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

from pydantic import ValidationError as PydanticValidationError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import LLMError, NotFoundError, RateLimitError, ValidationError
from app.core.logging import get_logger
from app.models import (
    AIBriefingStatus,
    AIEmailStatus,
    AISalesCoachingStatus,
    Company,
    CompanyAIBriefing,
    CompanyAIEmail,
    CompanyAIResearch,
    CompanyAISalesCoaching,
    ResearchStatus,
)
from app.modules.ai.briefing_service import _email_block, _research_block
from app.modules.ai.context import build_research_context
from app.modules.ai.prompts import get_sales_coach_prompt
from app.modules.ai.provider import (
    InvalidAIResponseError,
    LLMProvider,
    ProviderUnavailableError,
    get_provider,
)
from app.modules.ai.research_service import get_company_for_workspace
from app.modules.ai.schemas import (
    SalesCoachGenerateRequest,
    SalesCoachListResponse,
    SalesCoachMeta,
    SalesCoachPayload,
    SalesCoachResponse,
)

logger = get_logger(__name__)

MAX_EMAILS = 6
MAX_PREVIOUS_COACHING = 3


def _reap_stale_sales_coaching(db: Session, rows: list[CompanyAISalesCoaching]) -> bool:
    cutoff = datetime.now(timezone.utc) - timedelta(
        minutes=settings.AI_RESEARCH_STALE_RUNNING_MINUTES
    )
    reaped = False
    for row in rows:
        if row.status in (AISalesCoachingStatus.PENDING.value, AISalesCoachingStatus.RUNNING.value):
            updated_at = row.updated_at
            if updated_at is not None:
                if updated_at.tzinfo is None:
                    updated_at = updated_at.replace(tzinfo=timezone.utc)
                if updated_at < cutoff:
                    logger.warning(
                        "sales_coaching_run_stale_reaped",
                        coaching_id=str(row.id),
                        workspace_id=str(row.workspace_id),
                        stuck_since=updated_at.isoformat(),
                    )
                    row.status = AISalesCoachingStatus.FAILED.value
                    row.error_message = "Generation timed out and did not complete. Please try again."
                    reaped = True
    if reaped:
        db.commit()
    return reaped


def _validate_uuid(value: str, resource: str) -> uuid.UUID:
    try:
        return uuid.UUID(str(value))
    except (ValueError, AttributeError, TypeError):
        raise NotFoundError(resource, str(value))


def _render_json(data: Any, empty: str) -> str:
    if not data:
        return empty
    return json.dumps(data, indent=2, sort_keys=True, default=str, ensure_ascii=False)


def _latest_completed_research(
    db: Session, company: Company, workspace_id: Any
) -> CompanyAIResearch:
    row = (
        db.query(CompanyAIResearch)
        .filter_by(
            company_id=company.id,
            workspace_id=workspace_id,
            status=ResearchStatus.COMPLETED.value,
        )
        .first()
    )
    if row is None or not row.input_hash:
        raise ValidationError(
            "Generate AI research before generating sales coaching.",
            field="research",
        )
    return row


def _completed_briefing(
    db: Session,
    company: Company,
    workspace_id: Any,
    briefing_id: str | None,
) -> CompanyAIBriefing:
    query = db.query(CompanyAIBriefing).filter(
        CompanyAIBriefing.company_id == company.id,
        CompanyAIBriefing.workspace_id == workspace_id,
        CompanyAIBriefing.status == AIBriefingStatus.COMPLETED.value,
    )
    if briefing_id:
        query = query.filter(CompanyAIBriefing.id == _validate_uuid(briefing_id, "Briefing"))
    row = query.order_by(CompanyAIBriefing.created_at.desc()).first()
    if row is None:
        raise ValidationError(
            "Generate an AI sales briefing before generating sales coaching.",
            field="briefing",
        )
    return row


def _completed_emails(db: Session, company: Company, workspace_id: Any) -> list[CompanyAIEmail]:
    return (
        db.query(CompanyAIEmail)
        .filter(
            CompanyAIEmail.workspace_id == workspace_id,
            CompanyAIEmail.company_id == company.id,
            CompanyAIEmail.status == AIEmailStatus.COMPLETED.value,
        )
        .order_by(CompanyAIEmail.updated_at.desc(), CompanyAIEmail.created_at.desc())
        .limit(MAX_EMAILS)
        .all()
    )


def _briefing_block(briefing: CompanyAIBriefing) -> dict[str, Any]:
    return {
        "id": str(briefing.id),
        "summary": briefing.summary,
        "briefing_json": briefing.briefing_json or {},
        "confidence_score": briefing.confidence_score,
        "input_hash": briefing.input_hash,
        "generated_at": briefing.updated_at,
    }


def _previous_coaching(db: Session, company: Company, workspace_id: Any) -> list[dict[str, Any]]:
    rows = (
        db.query(CompanyAISalesCoaching)
        .filter(
            CompanyAISalesCoaching.workspace_id == workspace_id,
            CompanyAISalesCoaching.company_id == company.id,
            CompanyAISalesCoaching.status == AISalesCoachingStatus.COMPLETED.value,
        )
        .order_by(CompanyAISalesCoaching.created_at.desc())
        .limit(MAX_PREVIOUS_COACHING)
        .all()
    )
    return [
        {
            "id": str(row.id),
            "summary": row.summary,
            "win_probability": row.win_probability,
            "confidence_score": row.confidence_score,
            "created_at": row.created_at,
        }
        for row in rows
    ]


def _compute_input_hash(
    research: CompanyAIResearch,
    briefing: CompanyAIBriefing,
    provider: LLMProvider,
    prompt_version: str,
    deal_stage: str | None,
) -> str:
    canonical = json.dumps(
        {
            "research_input_hash": research.input_hash,
            "research_id": str(research.id),
            "briefing_id": str(briefing.id),
            "briefing_input_hash": briefing.input_hash,
            "deal_stage": deal_stage,
            "prompt_version": prompt_version,
            "model": provider.model_version,
        },
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _prompt_variables(
    db: Session,
    company: Company,
    research: CompanyAIResearch,
    briefing: CompanyAIBriefing,
    emails: list[CompanyAIEmail],
    deal_stage: str | None,
) -> dict[str, Any]:
    context = build_research_context(db, company)
    return {
        "deal_stage": deal_stage or "infer from CRM deal stage and briefing context",
        "company_profile": _render_json(context.company_profile, "No company profile available."),
        "scoring": _render_json(context.scoring, "Not scored yet."),
        "signals": _render_json(context.signals, "No buying signals detected yet."),
        "intelligence": _render_json(context.intelligence, "No intelligence feed item generated yet."),
        "contacts": _render_json(context.contacts, "No contacts known."),
        "crm": _render_json(context.crm, "No CRM deals or outcomes linked."),
        "icp": _render_json(context.icp, "ICP not configured for this workspace."),
        "research": _render_json(_research_block(research), "No completed AI research available."),
        "emails": _render_json([_email_block(row) for row in emails], "No AI emails generated yet."),
        "briefing": _render_json(_briefing_block(briefing), "No AI sales briefing generated yet."),
        "previous_coaching": _render_json(
            _previous_coaching(db, company, company.workspace_id),
            "No previous sales coaching generated yet.",
        ),
    }


def _to_response(row: CompanyAISalesCoaching, *, cached: bool = False) -> SalesCoachResponse:
    payload = None
    if row.status == AISalesCoachingStatus.COMPLETED.value and row.coaching_json:
        payload = SalesCoachPayload.model_validate(row.coaching_json)
    return SalesCoachResponse(
        id=str(row.id),
        workspace_id=str(row.workspace_id),
        company_id=str(row.company_id),
        research_id=str(row.research_id),
        briefing_id=str(row.briefing_id) if row.briefing_id else None,
        summary=row.summary,
        coaching_json=payload,
        win_probability=row.win_probability,
        confidence_score=row.confidence_score,
        status=row.status,
        cached=cached,
        error_message=row.error_message,
        meta=SalesCoachMeta(
            model_provider=row.model_provider,
            model_version=row.model_version,
            prompt_version=row.prompt_version,
            generation_duration_ms=row.generation_duration_ms,
            input_hash=row.input_hash,
        ),
        created_at=row.created_at,
        updated_at=row.updated_at,
        archived_at=row.archived_at,
    )


def _list_rows(db: Session, company_id: Any, workspace_id: Any) -> list[CompanyAISalesCoaching]:
    return (
        db.query(CompanyAISalesCoaching)
        .filter(
            CompanyAISalesCoaching.company_id == company_id,
            CompanyAISalesCoaching.workspace_id == workspace_id,
            CompanyAISalesCoaching.status != AISalesCoachingStatus.ARCHIVED.value,
        )
        .order_by(CompanyAISalesCoaching.created_at.desc())
        .all()
    )


def list_company_sales_coaching(
    db: Session, company_id: str, workspace_id: Any
) -> SalesCoachListResponse:
    company = get_company_for_workspace(db, company_id, workspace_id)
    rows = _list_rows(db, company.id, workspace_id)
    if not rows:
        return SalesCoachListResponse(company_id=str(company.id), status="none")
    if _reap_stale_sales_coaching(db, rows):
        rows = _list_rows(db, company.id, workspace_id)

    statuses = {row.status for row in rows}
    if AISalesCoachingStatus.RUNNING.value in statuses:
        status = "running"
    elif AISalesCoachingStatus.PENDING.value in statuses:
        status = "pending"
    elif AISalesCoachingStatus.COMPLETED.value in statuses:
        status = "completed"
    elif statuses == {AISalesCoachingStatus.FAILED.value}:
        status = "failed"
    else:
        status = "none"
    first_error = next((row.error_message for row in rows if row.error_message), None)
    return SalesCoachListResponse(
        company_id=str(company.id),
        status=status,
        coaching=[_to_response(row) for row in rows],
        error_message=first_error,
    )


def request_sales_coaching_generation(
    db: Session,
    company_id: str,
    workspace_id: Any,
    request: SalesCoachGenerateRequest,
    *,
    provider: LLMProvider | None = None,
) -> tuple[SalesCoachResponse, bool]:
    company = get_company_for_workspace(db, company_id, workspace_id)
    research = _latest_completed_research(db, company, workspace_id)
    briefing = _completed_briefing(db, company, workspace_id, request.briefing_id)
    active_provider = provider or get_provider()
    if not active_provider.is_available():
        raise ProviderUnavailableError(f"AI provider '{active_provider.name}' is not configured")

    template = get_sales_coach_prompt()
    input_hash = _compute_input_hash(
        research,
        briefing,
        active_provider,
        template.version,
        None,
    )

    if not request.force_refresh:
        cached = (
            db.query(CompanyAISalesCoaching)
            .filter(
                CompanyAISalesCoaching.workspace_id == workspace_id,
                CompanyAISalesCoaching.company_id == company.id,
                CompanyAISalesCoaching.research_id == research.id,
                CompanyAISalesCoaching.briefing_id == briefing.id,
                CompanyAISalesCoaching.input_hash == input_hash,
                CompanyAISalesCoaching.model_version == active_provider.model_version,
                CompanyAISalesCoaching.prompt_version == template.version,
                CompanyAISalesCoaching.status == AISalesCoachingStatus.COMPLETED.value,
            )
            .order_by(CompanyAISalesCoaching.created_at.desc())
            .first()
        )
        if cached is not None:
            return _to_response(cached, cached=True), False

        in_flight = (
            db.query(CompanyAISalesCoaching)
            .filter(
                CompanyAISalesCoaching.workspace_id == workspace_id,
                CompanyAISalesCoaching.company_id == company.id,
                CompanyAISalesCoaching.status.in_(
                    [AISalesCoachingStatus.PENDING.value, AISalesCoachingStatus.RUNNING.value]
                ),
            )
            .order_by(CompanyAISalesCoaching.created_at.desc())
            .first()
        )
        if in_flight is not None:
            return _to_response(in_flight), False

    row = CompanyAISalesCoaching(
        workspace_id=company.workspace_id,
        company_id=company.id,
        research_id=research.id,
        briefing_id=briefing.id,
        status=AISalesCoachingStatus.PENDING.value,
        input_hash=input_hash,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return _to_response(row), True


def get_sales_coaching(db: Session, coaching_id: str, workspace_id: Any) -> SalesCoachResponse:
    row = db.get(CompanyAISalesCoaching, _validate_uuid(coaching_id, "Sales coaching"))
    if not row or str(row.workspace_id) != str(workspace_id):
        raise NotFoundError("Sales coaching", coaching_id)
    return _to_response(row)


def request_regeneration(
    db: Session,
    coaching_id: str,
    workspace_id: Any,
    *,
    provider: LLMProvider | None = None,
) -> tuple[SalesCoachResponse, bool]:
    source = db.get(CompanyAISalesCoaching, _validate_uuid(coaching_id, "Sales coaching"))
    if not source or str(source.workspace_id) != str(workspace_id):
        raise NotFoundError("Sales coaching", coaching_id)
    return request_sales_coaching_generation(
        db,
        str(source.company_id),
        workspace_id,
        SalesCoachGenerateRequest(
            force_refresh=True,
            briefing_id=str(source.briefing_id) if source.briefing_id else None,
        ),
        provider=provider,
    )


def archive_sales_coaching(db: Session, coaching_id: str, workspace_id: Any) -> SalesCoachResponse:
    row = db.get(CompanyAISalesCoaching, _validate_uuid(coaching_id, "Sales coaching"))
    if not row or str(row.workspace_id) != str(workspace_id):
        raise NotFoundError("Sales coaching", coaching_id)
    row.status = AISalesCoachingStatus.ARCHIVED.value
    row.archived_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(row)
    return _to_response(row)


def generate_sales_coaching_row(
    db: Session,
    coaching_id: str,
    workspace_id: Any,
    *,
    provider: LLMProvider | None = None,
) -> dict[str, Any]:
    started = time.perf_counter()
    row = db.get(CompanyAISalesCoaching, _validate_uuid(coaching_id, "Sales coaching"))
    if not row or str(row.workspace_id) != str(workspace_id):
        return {"generated": 0, "failed": 1, "status": "failed", "code": "not_found"}

    active_provider = provider or get_provider()
    row.status = AISalesCoachingStatus.RUNNING.value
    row.error_message = None
    db.commit()

    def _fail(message: str, code: str) -> dict[str, Any]:
        row.status = AISalesCoachingStatus.FAILED.value
        row.error_message = message[:1000]
        row.generation_duration_ms = int((time.perf_counter() - started) * 1000)
        db.commit()
        logger.warning(
            "sales_coaching_generation_failed",
            coaching_id=str(row.id),
            workspace_id=str(workspace_id),
            code=code,
            error=message,
        )
        return {"generated": 0, "failed": 1, "status": "failed", "code": code}

    try:
        company = get_company_for_workspace(db, str(row.company_id), workspace_id)
        research = _latest_completed_research(db, company, workspace_id)
        briefing = _completed_briefing(
            db,
            company,
            workspace_id,
            str(row.briefing_id) if row.briefing_id else None,
        )
        template = get_sales_coach_prompt()
        emails = _completed_emails(db, company, workspace_id)
        system_prompt, user_prompt = template.render(
            **_prompt_variables(db, company, research, briefing, emails, None)
        )
        raw_payload = active_provider.generate_json(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.25,
            max_tokens=6144,
        )
        payload = SalesCoachPayload.model_validate(raw_payload)
    except RateLimitError as exc:
        return _fail(exc.message, exc.code)
    except ProviderUnavailableError as exc:
        return _fail(exc.message, exc.code)
    except InvalidAIResponseError as exc:
        return _fail(f"AI returned an unusable response: {exc.message}", exc.code)
    except PydanticValidationError as exc:
        return _fail(f"AI response failed schema validation: {exc.error_count()} error(s)", "schema_validation_failed")
    except LLMError as exc:
        return _fail(exc.message, exc.code)
    except Exception as exc:
        return _fail(f"Unexpected AI sales coaching generation error: {exc}", "unexpected_error")

    duration_ms = int((time.perf_counter() - started) * 1000)
    row.summary = payload.executive_coaching_summary
    row.coaching_json = payload.model_dump()
    row.win_probability = payload.win_probability
    row.confidence_score = payload.confidence_score
    row.status = AISalesCoachingStatus.COMPLETED.value
    row.error_message = None
    row.model_provider = active_provider.name
    row.model_version = active_provider.model_version
    row.prompt_version = template.version
    row.generation_duration_ms = duration_ms
    row.input_hash = _compute_input_hash(research, briefing, active_provider, template.version, None)
    db.commit()

    logger.info(
        "sales_coaching_generation_complete",
        coaching_id=str(row.id),
        company_id=str(company.id),
        workspace_id=str(workspace_id),
        duration_ms=duration_ms,
        win_probability=payload.win_probability,
        confidence_score=payload.confidence_score,
    )
    return {"generated": 1, "failed": 0, "status": "completed", "duration_ms": duration_ms}
