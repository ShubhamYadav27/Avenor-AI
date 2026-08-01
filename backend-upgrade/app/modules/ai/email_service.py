"""AI Email Generator service (Phase 5.2)."""
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
    AIEmailStatus,
    Company,
    CompanyAIEmail,
    CompanyAIResearch,
    Contact,
    ICPConfig,
    ResearchStatus,
)
from app.modules.ai.context import build_research_context
from app.modules.ai.prompts import get_email_prompt
from app.modules.ai.provider import (
    InvalidAIResponseError,
    LLMProvider,
    ProviderUnavailableError,
    get_provider,
)
from app.modules.ai.research_service import get_company_for_workspace
from app.modules.ai.schemas import (
    EmailGenerateRequest,
    EmailListResponse,
    EmailPayload,
    EmailResponse,
    EmailMeta,
)

logger = get_logger(__name__)

VARIATIONS = ("A", "B", "C")
VARIATION_STYLES = {
    "A": "Crisp and direct, with a clear business trigger in the opener.",
    "B": "Warm and consultative, with a helpful observation before the ask.",
    "C": "Executive and value-led, focused on business impact and timing.",
}


def _reap_stale_emails(db: Session, rows: list[CompanyAIEmail]) -> bool:
    cutoff = datetime.now(timezone.utc) - timedelta(
        minutes=settings.AI_RESEARCH_STALE_RUNNING_MINUTES
    )
    reaped = False
    for row in rows:
        if row.status in (AIEmailStatus.PENDING.value, AIEmailStatus.RUNNING.value):
            updated_at = row.updated_at
            if updated_at is not None:
                if updated_at.tzinfo is None:
                    updated_at = updated_at.replace(tzinfo=timezone.utc)
                if updated_at < cutoff:
                    logger.warning(
                        "email_run_stale_reaped",
                        email_id=str(row.id),
                        workspace_id=str(row.workspace_id),
                        stuck_since=updated_at.isoformat(),
                    )
                    row.status = AIEmailStatus.FAILED.value
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


def _latest_completed_research(
    db: Session, company: Company, workspace_id: Any
) -> CompanyAIResearch:
    ws_uuid = _validate_uuid(workspace_id, "Workspace")
    row = (
        db.query(CompanyAIResearch)
        .filter(
            CompanyAIResearch.company_id == company.id,
            CompanyAIResearch.workspace_id == ws_uuid,
            CompanyAIResearch.status == ResearchStatus.COMPLETED.value,
        )
        .first()
    )
    if row is None or not row.input_hash:
        raise ValidationError(
            "Generate AI research before generating sales emails.",
            field="research",
        )
    return row


def _get_contact_for_company(
    db: Session, company: Company, contact_id: str | None
) -> Contact | None:
    if contact_id is None:
        return None
    contact_uuid = _validate_uuid(contact_id, "Contact")
    contact = db.get(Contact, contact_uuid)
    if not contact or str(contact.company_id) != str(company.id):
        raise NotFoundError("Contact", contact_id)
    return contact


def _render_json(data: Any, empty: str) -> str:
    if not data:
        return empty
    return json.dumps(data, indent=2, sort_keys=True, default=str, ensure_ascii=False)


def _research_block(research: CompanyAIResearch) -> dict[str, Any]:
    return {
        "summary": research.summary,
        "pain_points": research.pain_points or [],
        "recommended_personas": research.recommended_personas or [],
        "talking_points": research.talking_points or [],
        "risks": research.risks or [],
        "next_actions": research.next_actions or [],
    }


def _contact_block(contact: Contact | None) -> dict[str, Any]:
    if contact is None:
        return {}
    return {
        "name": contact.full_name,
        "title": contact.title,
        "department": contact.department,
        "seniority": contact.seniority,
        "has_email": bool(contact.email),
        "is_primary": contact.is_primary,
    }


def _icp_block(db: Session, company: Company) -> dict[str, Any]:
    icp = db.query(ICPConfig).filter_by(workspace_id=company.workspace_id).first()
    if icp is None:
        return {}
    return {
        "product_name": icp.product_name,
        "product_description": icp.product_description,
        "key_pain_points": icp.key_pain_points or [],
        "customer_personas": icp.customer_personas or [],
    }


def _prompt_variables(
    db: Session,
    company: Company,
    research: CompanyAIResearch,
    contact: Contact | None,
    request: EmailGenerateRequest,
    variation: str,
) -> dict[str, Any]:
    context = build_research_context(db, company)
    return {
        "email_type": request.email_type,
        "tone": request.tone,
        "length": request.length,
        "cta_type": request.cta_type,
        "variation": variation,
        "variation_style": VARIATION_STYLES[variation],
        "company_profile": _render_json(context.company_profile, "No company profile available."),
        "contact": _render_json(_contact_block(contact), "No specific recipient selected."),
        "research": _render_json(_research_block(research), "No research report available."),
        "buying_signals": _render_json(research.buying_signals or [], "No buying signals available."),
        "outreach_strategy": _render_json(
            research.outreach_strategy or {}, "No outreach strategy available."
        ),
        "icp": _render_json(_icp_block(db, company), "ICP not configured for this workspace."),
    }


def _to_response(row: CompanyAIEmail) -> EmailResponse:
    return EmailResponse(
        id=str(row.id),
        workspace_id=str(row.workspace_id),
        company_id=str(row.company_id),
        research_id=str(row.research_id),
        contact_id=str(row.contact_id) if row.contact_id else None,
        email_type=row.email_type,
        subject=row.subject,
        body=row.body,
        cta=row.cta,
        cta_type=row.cta_type,
        tone=row.tone,
        length=row.length,
        variation=row.variation,
        reasoning=row.reasoning,
        status=row.status,
        copy_count=row.copy_count,
        regeneration_count=row.regeneration_count,
        version=row.version,
        error_message=row.error_message,
        meta=EmailMeta(
            model_provider=row.model_provider,
            model_version=row.model_version,
            prompt_version=row.prompt_version,
            generation_duration_ms=row.generation_duration_ms,
            research_input_hash=row.research_input_hash,
        ),
        created_at=row.created_at,
        updated_at=row.updated_at,
        archived_at=row.archived_at,
    )


def _list_rows(db: Session, company_id: Any, workspace_id: Any) -> list[CompanyAIEmail]:
    return (
        db.query(CompanyAIEmail)
        .filter(
            CompanyAIEmail.company_id == company_id,
            CompanyAIEmail.workspace_id == workspace_id,
            CompanyAIEmail.status != AIEmailStatus.ARCHIVED.value,
        )
        .order_by(CompanyAIEmail.created_at.desc(), CompanyAIEmail.variation.asc())
        .all()
    )


def _matching_completed_rows(
    db: Session,
    company: Company,
    research: CompanyAIResearch,
    request: EmailGenerateRequest,
    provider: LLMProvider,
) -> list[CompanyAIEmail]:
    template = get_email_prompt()
    rows = (
        db.query(CompanyAIEmail)
        .filter(
            CompanyAIEmail.workspace_id == company.workspace_id,
            CompanyAIEmail.company_id == company.id,
            CompanyAIEmail.research_id == research.id,
            CompanyAIEmail.research_input_hash == research.input_hash,
            CompanyAIEmail.contact_id == (
                uuid.UUID(request.contact_id) if request.contact_id else None
            ),
            CompanyAIEmail.email_type == request.email_type,
            CompanyAIEmail.tone == request.tone,
            CompanyAIEmail.length == request.length,
            CompanyAIEmail.cta_type == request.cta_type,
            CompanyAIEmail.model_version == provider.model_version,
            CompanyAIEmail.prompt_version == template.version,
            CompanyAIEmail.status == AIEmailStatus.COMPLETED.value,
        )
        .order_by(CompanyAIEmail.variation.asc(), CompanyAIEmail.version.desc())
        .all()
    )
    latest_by_variation: dict[str, CompanyAIEmail] = {}
    for row in rows:
        latest_by_variation.setdefault(row.variation, row)
    return [latest_by_variation[v] for v in VARIATIONS if v in latest_by_variation]


def list_company_emails(
    db: Session, company_id: str, workspace_id: Any
) -> EmailListResponse:
    company = get_company_for_workspace(db, company_id, workspace_id)
    rows = _list_rows(db, company.id, workspace_id)
    if not rows:
        return EmailListResponse(company_id=str(company.id), status="none")
    
    if _reap_stale_emails(db, rows):
        rows = _list_rows(db, company.id, workspace_id)

    statuses = {row.status for row in rows}
    if AIEmailStatus.RUNNING.value in statuses:
        status = "running"
    elif AIEmailStatus.PENDING.value in statuses:
        status = "pending"
    elif AIEmailStatus.COMPLETED.value in statuses:
        status = "completed"
    elif statuses == {AIEmailStatus.FAILED.value}:
        status = "failed"
    else:
        status = "none"
    first_error = next((row.error_message for row in rows if row.error_message), None)
    return EmailListResponse(
        company_id=str(company.id),
        status=status,
        emails=[_to_response(row) for row in rows],
        error_message=first_error,
    )


def request_email_generation(
    db: Session,
    company_id: str,
    workspace_id: Any,
    request: EmailGenerateRequest,
    *,
    provider: LLMProvider | None = None,
) -> tuple[EmailListResponse, bool]:
    company = get_company_for_workspace(db, company_id, workspace_id)
    active_provider = provider or get_provider()
    if not active_provider.is_available():
        raise ProviderUnavailableError(f"AI provider '{active_provider.name}' is not configured")

    research = _latest_completed_research(db, company, workspace_id)
    _get_contact_for_company(db, company, request.contact_id)

    if not request.force_refresh:
        cached = _matching_completed_rows(db, company, research, request, active_provider)
        if len(cached) == len(VARIATIONS):
            return EmailListResponse(
                company_id=str(company.id),
                status="completed",
                cached=True,
                emails=[_to_response(row) for row in cached],
            ), False

    contact_uuid = uuid.UUID(request.contact_id) if request.contact_id else None
    rows: list[CompanyAIEmail] = []
    for variation in VARIATIONS:
        row = CompanyAIEmail(
            workspace_id=company.workspace_id,
            company_id=company.id,
            research_id=research.id,
            contact_id=contact_uuid,
            email_type=request.email_type,
            cta_type=request.cta_type,
            tone=request.tone,
            length=request.length,
            variation=variation,
            status=AIEmailStatus.PENDING.value,
            research_input_hash=research.input_hash,
        )
        db.add(row)
        rows.append(row)
    db.commit()
    for row in rows:
        db.refresh(row)

    return EmailListResponse(
        company_id=str(company.id),
        status="pending",
        emails=[_to_response(row) for row in rows],
    ), True


def get_email(db: Session, email_id: str, workspace_id: Any) -> EmailResponse:
    email_uuid = _validate_uuid(email_id, "Email")
    row = db.get(CompanyAIEmail, email_uuid)
    if not row or str(row.workspace_id) != str(workspace_id):
        raise NotFoundError("Email", email_id)
    return _to_response(row)


def copy_email(db: Session, email_id: str, workspace_id: Any) -> EmailResponse:
    email_uuid = _validate_uuid(email_id, "Email")
    row = db.get(CompanyAIEmail, email_uuid)
    if not row or str(row.workspace_id) != str(workspace_id):
        raise NotFoundError("Email", email_id)
    row.copy_count += 1
    db.commit()
    db.refresh(row)
    return _to_response(row)


def archive_email(db: Session, email_id: str, workspace_id: Any) -> EmailResponse:
    email_uuid = _validate_uuid(email_id, "Email")
    row = db.get(CompanyAIEmail, email_uuid)
    if not row or str(row.workspace_id) != str(workspace_id):
        raise NotFoundError("Email", email_id)
    row.status = AIEmailStatus.ARCHIVED.value
    row.archived_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(row)
    return _to_response(row)


def request_regeneration(
    db: Session,
    email_id: str,
    workspace_id: Any,
    *,
    provider: LLMProvider | None = None,
) -> tuple[EmailResponse, bool]:
    email_uuid = _validate_uuid(email_id, "Email")
    source = db.get(CompanyAIEmail, email_uuid)
    if not source or str(source.workspace_id) != str(workspace_id):
        raise NotFoundError("Email", email_id)
    active_provider = provider or get_provider()
    if not active_provider.is_available():
        raise ProviderUnavailableError(f"AI provider '{active_provider.name}' is not configured")

    company = get_company_for_workspace(db, str(source.company_id), workspace_id)
    research = _latest_completed_research(db, company, workspace_id)
    row = CompanyAIEmail(
        workspace_id=source.workspace_id,
        company_id=source.company_id,
        research_id=research.id,
        contact_id=source.contact_id,
        email_type=source.email_type,
        cta_type=source.cta_type,
        tone=source.tone,
        length=source.length,
        variation=source.variation,
        status=AIEmailStatus.PENDING.value,
        regeneration_count=source.regeneration_count + 1,
        version=source.version + 1,
        research_input_hash=research.input_hash,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return _to_response(row), True


def generate_email_rows(
    db: Session,
    email_ids: list[str],
    workspace_id: Any,
    *,
    provider: LLMProvider | None = None,
) -> dict[str, Any]:
    active_provider = provider or get_provider()
    generated = 0
    failed = 0

    try:
        for email_id in email_ids:
            started = time.perf_counter()
            row = db.get(CompanyAIEmail, _validate_uuid(email_id, "Email"))
            if not row or str(row.workspace_id) != str(workspace_id):
                failed += 1
                continue

            row.status = AIEmailStatus.RUNNING.value
            row.error_message = None
            db.commit()

            def _fail(message: str, code: str) -> None:
                nonlocal failed
                row.status = AIEmailStatus.FAILED.value
                row.error_message = message[:1000]
                row.generation_duration_ms = int((time.perf_counter() - started) * 1000)
                db.commit()
                failed += 1
                logger.warning(
                    "email_generation_failed",
                    email_id=str(row.id),
                    workspace_id=str(workspace_id),
                    code=code,
                    error=message,
                )

            try:
                company = get_company_for_workspace(db, str(row.company_id), workspace_id)
                research = _latest_completed_research(db, company, workspace_id)
                contact = _get_contact_for_company(db, company, str(row.contact_id) if row.contact_id else None)
                request = EmailGenerateRequest(
                    email_type=row.email_type,
                    tone=row.tone,
                    length=row.length,
                    cta_type=row.cta_type,
                    contact_id=str(row.contact_id) if row.contact_id else None,
                    force_refresh=True,
                )
                template = get_email_prompt()
                system_prompt, user_prompt = template.render(
                    **_prompt_variables(db, company, research, contact, request, row.variation)
                )
                raw_payload = active_provider.generate_json(
                    system_prompt=system_prompt,
                    user_prompt=user_prompt,
                    temperature=0.35,
                    max_tokens=2048,
                )
                payload = EmailPayload.model_validate(raw_payload)
                if payload.variation != row.variation:
                    payload.variation = row.variation
            except RateLimitError as exc:
                _fail(exc.message, exc.code)
                continue
            except ProviderUnavailableError as exc:
                _fail(exc.message, exc.code)
                continue
            except InvalidAIResponseError as exc:
                _fail(f"AI returned an unusable response: {exc.message}", exc.code)
                continue
            except PydanticValidationError as exc:
                _fail(f"AI response failed schema validation: {exc.error_count()} error(s)", "schema_validation_failed")
                continue
            except LLMError as exc:
                _fail(exc.message, exc.code)
                continue
            except Exception as exc:
                _fail(f"Unexpected AI email generation error: {exc}", "unexpected_error")
                continue

            duration_ms = int((time.perf_counter() - started) * 1000)
            row.subject = payload.subject
            row.body = payload.body
            row.cta = payload.cta
            row.reasoning = payload.reasoning
            row.variation = payload.variation
            row.status = AIEmailStatus.COMPLETED.value
            row.error_message = None
            row.model_provider = active_provider.name
            row.model_version = active_provider.model_version
            row.prompt_version = template.version
            row.generation_duration_ms = duration_ms
            row.research_input_hash = research.input_hash
            db.commit()
            generated += 1
    except Exception as exc:
        logger.error("email_generation_batch_uncaught_error", error=str(exc), workspace_id=str(workspace_id))
        for email_id in email_ids:
            try:
                row = db.get(CompanyAIEmail, _validate_uuid(email_id, "Email"))
                if row and row.status in (AIEmailStatus.PENDING.value, AIEmailStatus.RUNNING.value):
                    row.status = AIEmailStatus.FAILED.value
                    row.error_message = f"Generation failed unexpectedly: {exc}"
                    db.commit()
                    failed += 1
            except Exception:
                pass

    return {"generated": generated, "failed": failed, "status": "completed" if failed == 0 else "partial"}
