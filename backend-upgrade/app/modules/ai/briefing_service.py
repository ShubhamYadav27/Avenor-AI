"""AI Sales Briefing service (Phase 5.3)."""
import hashlib
import json
import time
import uuid
from datetime import datetime, timezone
from typing import Any

from pydantic import ValidationError as PydanticValidationError
from sqlalchemy.orm import Session

from app.core.exceptions import LLMError, NotFoundError, RateLimitError, ValidationError
from app.core.logging import get_logger
from app.models import (
    AIBriefingStatus,
    AIEmailStatus,
    Company,
    CompanyAIBriefing,
    CompanyAIEmail,
    CompanyAIResearch,
    ResearchStatus,
)
from app.modules.ai.context import build_research_context
from app.modules.ai.prompts import get_briefing_prompt
from app.modules.ai.provider import (
    InvalidAIResponseError,
    LLMProvider,
    ProviderUnavailableError,
    get_provider,
)
from app.modules.ai.research_service import get_company_for_workspace
from app.modules.ai.schemas import (
    BriefingGenerateRequest,
    BriefingListResponse,
    BriefingMeta,
    BriefingPayload,
    BriefingResponse,
)

logger = get_logger(__name__)

MAX_EMAILS = 6
MAX_PREVIOUS_BRIEFINGS = 3


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
            "Generate AI research before generating a sales briefing.",
            field="research",
        )
    return row


def _get_source_email(
    db: Session, company: Company, workspace_id: Any, source_email_id: str | None
) -> CompanyAIEmail | None:
    if source_email_id is None:
        return None
    email_uuid = _validate_uuid(source_email_id, "Email")
    email = db.get(CompanyAIEmail, email_uuid)
    if (
        not email
        or str(email.workspace_id) != str(workspace_id)
        or str(email.company_id) != str(company.id)
    ):
        raise NotFoundError("Email", source_email_id)
    return email


def _research_block(research: CompanyAIResearch) -> dict[str, Any]:
    return {
        "summary": research.summary,
        "buying_signals": research.buying_signals or [],
        "pain_points": research.pain_points or [],
        "recommended_personas": research.recommended_personas or [],
        "outreach_strategy": research.outreach_strategy or {},
        "talking_points": research.talking_points or [],
        "risks": research.risks or [],
        "next_actions": research.next_actions or [],
        "input_hash": research.input_hash,
        "generated_at": research.updated_at,
    }


def _email_block(row: CompanyAIEmail) -> dict[str, Any]:
    return {
        "id": str(row.id),
        "contact_id": str(row.contact_id) if row.contact_id else None,
        "email_type": row.email_type,
        "subject": row.subject,
        "body": row.body,
        "cta": row.cta,
        "tone": row.tone,
        "length": row.length,
        "variation": row.variation,
        "reasoning": row.reasoning,
        "version": row.version,
        "updated_at": row.updated_at,
    }


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


def _previous_briefings(db: Session, company: Company, workspace_id: Any) -> list[dict[str, Any]]:
    rows = (
        db.query(CompanyAIBriefing)
        .filter(
            CompanyAIBriefing.workspace_id == workspace_id,
            CompanyAIBriefing.company_id == company.id,
            CompanyAIBriefing.status == AIBriefingStatus.COMPLETED.value,
        )
        .order_by(CompanyAIBriefing.created_at.desc())
        .limit(MAX_PREVIOUS_BRIEFINGS)
        .all()
    )
    return [
        {
            "id": str(row.id),
            "summary": row.summary,
            "confidence_score": row.confidence_score,
            "created_at": row.created_at,
        }
        for row in rows
    ]


def _compute_input_hash(
    research: CompanyAIResearch,
    provider: LLMProvider,
    prompt_version: str,
    source_email_id: str | None,
) -> str:
    canonical = json.dumps(
        {
            "research_input_hash": research.input_hash,
            "research_id": str(research.id),
            "source_email_id": source_email_id,
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
    emails: list[CompanyAIEmail],
    source_email: CompanyAIEmail | None,
) -> dict[str, Any]:
    context = build_research_context(db, company)
    email_rows = emails
    if source_email and all(str(row.id) != str(source_email.id) for row in email_rows):
        email_rows = [source_email, *email_rows[: MAX_EMAILS - 1]]

    return {
        "company_profile": _render_json(context.company_profile, "No company profile available."),
        "scoring": _render_json(context.scoring, "Not scored yet."),
        "signals": _render_json(context.signals, "No buying signals detected yet."),
        "intelligence": _render_json(context.intelligence, "No intelligence feed item generated yet."),
        "contacts": _render_json(context.contacts, "No contacts known."),
        "crm": _render_json(context.crm, "No CRM deals or outcomes linked."),
        "icp": _render_json(context.icp, "ICP not configured for this workspace."),
        "research": _render_json(_research_block(research), "No completed AI research available."),
        "emails": _render_json([_email_block(row) for row in email_rows], "No AI emails generated yet."),
        "previous_briefings": _render_json(
            _previous_briefings(db, company, company.workspace_id),
            "No previous AI briefings generated yet.",
        ),
    }


def _to_response(row: CompanyAIBriefing, *, cached: bool = False) -> BriefingResponse:
    payload = None
    if row.status == AIBriefingStatus.COMPLETED.value and row.briefing_json:
        payload = BriefingPayload.model_validate(row.briefing_json)
    return BriefingResponse(
        id=str(row.id),
        workspace_id=str(row.workspace_id),
        company_id=str(row.company_id),
        research_id=str(row.research_id),
        source_email_id=str(row.source_email_id) if row.source_email_id else None,
        summary=row.summary,
        briefing_json=payload,
        confidence_score=row.confidence_score,
        status=row.status,
        cached=cached,
        error_message=row.error_message,
        meta=BriefingMeta(
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


def _list_rows(db: Session, company_id: Any, workspace_id: Any) -> list[CompanyAIBriefing]:
    return (
        db.query(CompanyAIBriefing)
        .filter(
            CompanyAIBriefing.company_id == company_id,
            CompanyAIBriefing.workspace_id == workspace_id,
            CompanyAIBriefing.status != AIBriefingStatus.ARCHIVED.value,
        )
        .order_by(CompanyAIBriefing.created_at.desc())
        .all()
    )


def list_company_briefings(
    db: Session, company_id: str, workspace_id: Any
) -> BriefingListResponse:
    company = get_company_for_workspace(db, company_id, workspace_id)
    rows = _list_rows(db, company.id, workspace_id)
    if not rows:
        return BriefingListResponse(company_id=str(company.id), status="none")
    statuses = {row.status for row in rows}
    if AIBriefingStatus.RUNNING.value in statuses:
        status = "running"
    elif AIBriefingStatus.PENDING.value in statuses:
        status = "pending"
    elif statuses == {AIBriefingStatus.FAILED.value}:
        status = "failed"
    elif AIBriefingStatus.COMPLETED.value in statuses:
        status = "completed"
    else:
        status = "none"
    first_error = next((row.error_message for row in rows if row.error_message), None)
    return BriefingListResponse(
        company_id=str(company.id),
        status=status,
        briefings=[_to_response(row) for row in rows],
        error_message=first_error,
    )


def request_briefing_generation(
    db: Session,
    company_id: str,
    workspace_id: Any,
    request: BriefingGenerateRequest,
    *,
    provider: LLMProvider | None = None,
) -> tuple[BriefingResponse, bool]:
    company = get_company_for_workspace(db, company_id, workspace_id)
    research = _latest_completed_research(db, company, workspace_id)
    source_email = _get_source_email(db, company, workspace_id, request.source_email_id)
    active_provider = provider or get_provider()
    if not active_provider.is_available():
        raise ProviderUnavailableError(f"AI provider '{active_provider.name}' is not configured")

    template = get_briefing_prompt()
    input_hash = _compute_input_hash(
        research,
        active_provider,
        template.version,
        str(source_email.id) if source_email else None,
    )

    if not request.force_refresh:
        cached = (
            db.query(CompanyAIBriefing)
            .filter(
                CompanyAIBriefing.workspace_id == workspace_id,
                CompanyAIBriefing.company_id == company.id,
                CompanyAIBriefing.research_id == research.id,
                CompanyAIBriefing.input_hash == input_hash,
                CompanyAIBriefing.model_version == active_provider.model_version,
                CompanyAIBriefing.prompt_version == template.version,
                CompanyAIBriefing.status == AIBriefingStatus.COMPLETED.value,
            )
            .order_by(CompanyAIBriefing.created_at.desc())
            .first()
        )
        if cached is not None:
            return _to_response(cached, cached=True), False

        in_flight = (
            db.query(CompanyAIBriefing)
            .filter(
                CompanyAIBriefing.workspace_id == workspace_id,
                CompanyAIBriefing.company_id == company.id,
                CompanyAIBriefing.status.in_(
                    [AIBriefingStatus.PENDING.value, AIBriefingStatus.RUNNING.value]
                ),
            )
            .order_by(CompanyAIBriefing.created_at.desc())
            .first()
        )
        if in_flight is not None:
            return _to_response(in_flight), False

    row = CompanyAIBriefing(
        workspace_id=company.workspace_id,
        company_id=company.id,
        research_id=research.id,
        source_email_id=source_email.id if source_email else None,
        status=AIBriefingStatus.PENDING.value,
        input_hash=input_hash,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return _to_response(row), True


def get_briefing(db: Session, briefing_id: str, workspace_id: Any) -> BriefingResponse:
    row = db.get(CompanyAIBriefing, _validate_uuid(briefing_id, "Briefing"))
    if not row or str(row.workspace_id) != str(workspace_id):
        raise NotFoundError("Briefing", briefing_id)
    return _to_response(row)


def request_regeneration(
    db: Session,
    briefing_id: str,
    workspace_id: Any,
    *,
    provider: LLMProvider | None = None,
) -> tuple[BriefingResponse, bool]:
    source = db.get(CompanyAIBriefing, _validate_uuid(briefing_id, "Briefing"))
    if not source or str(source.workspace_id) != str(workspace_id):
        raise NotFoundError("Briefing", briefing_id)
    return request_briefing_generation(
        db,
        str(source.company_id),
        workspace_id,
        BriefingGenerateRequest(
            force_refresh=True,
            source_email_id=str(source.source_email_id) if source.source_email_id else None,
        ),
        provider=provider,
    )


def archive_briefing(db: Session, briefing_id: str, workspace_id: Any) -> BriefingResponse:
    row = db.get(CompanyAIBriefing, _validate_uuid(briefing_id, "Briefing"))
    if not row or str(row.workspace_id) != str(workspace_id):
        raise NotFoundError("Briefing", briefing_id)
    row.status = AIBriefingStatus.ARCHIVED.value
    row.archived_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(row)
    return _to_response(row)


def generate_briefing_row(
    db: Session,
    briefing_id: str,
    workspace_id: Any,
    *,
    provider: LLMProvider | None = None,
) -> dict[str, Any]:
    started = time.perf_counter()
    row = db.get(CompanyAIBriefing, _validate_uuid(briefing_id, "Briefing"))
    if not row or str(row.workspace_id) != str(workspace_id):
        return {"generated": 0, "failed": 1, "status": "failed", "code": "not_found"}

    active_provider = provider or get_provider()
    row.status = AIBriefingStatus.RUNNING.value
    row.error_message = None
    db.commit()

    def _fail(message: str, code: str) -> dict[str, Any]:
        row.status = AIBriefingStatus.FAILED.value
        row.error_message = message[:1000]
        row.generation_duration_ms = int((time.perf_counter() - started) * 1000)
        db.commit()
        logger.warning(
            "briefing_generation_failed",
            briefing_id=str(row.id),
            workspace_id=str(workspace_id),
            code=code,
            error=message,
        )
        return {"generated": 0, "failed": 1, "status": "failed", "code": code}

    try:
        company = get_company_for_workspace(db, str(row.company_id), workspace_id)
        research = _latest_completed_research(db, company, workspace_id)
        source_email = _get_source_email(
            db,
            company,
            workspace_id,
            str(row.source_email_id) if row.source_email_id else None,
        )
        template = get_briefing_prompt()
        emails = _completed_emails(db, company, workspace_id)
        system_prompt, user_prompt = template.render(
            **_prompt_variables(db, company, research, emails, source_email)
        )
        raw_payload = active_provider.generate_json(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.25,
            max_tokens=4096,
        )
        payload = BriefingPayload.model_validate(raw_payload)
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
        return _fail(f"Unexpected AI briefing generation error: {exc}", "unexpected_error")

    duration_ms = int((time.perf_counter() - started) * 1000)
    row.summary = payload.executive_summary
    row.briefing_json = payload.model_dump()
    row.confidence_score = payload.confidence_score
    row.status = AIBriefingStatus.COMPLETED.value
    row.error_message = None
    row.model_provider = active_provider.name
    row.model_version = active_provider.model_version
    row.prompt_version = template.version
    row.generation_duration_ms = duration_ms
    row.input_hash = _compute_input_hash(
        research,
        active_provider,
        template.version,
        str(row.source_email_id) if row.source_email_id else None,
    )
    db.commit()

    logger.info(
        "briefing_generation_complete",
        briefing_id=str(row.id),
        company_id=str(company.id),
        workspace_id=str(workspace_id),
        duration_ms=duration_ms,
        confidence_score=payload.confidence_score,
    )
    return {"generated": 1, "failed": 0, "status": "completed", "duration_ms": duration_ms}
