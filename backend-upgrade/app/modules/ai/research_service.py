"""
AI Account Research service.

Orchestration only — this module knows nothing about Gemini, HTTP, or FastAPI.
It depends on the `LLMProvider` interface, the versioned prompt registry, and
the Pydantic contracts.

Cache strategy:
  * Every generation stores `input_hash`, a digest of the exact intelligence
    used (see context.py).
  * A request whose freshly-computed hash matches a completed row returns that
    row with no LLM call.
  * If the company's intelligence has moved, the hash moves, and the report is
    regenerated automatically.
  * `force_refresh=True` regenerates regardless.
"""
import time
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

from pydantic import ValidationError as PydanticValidationError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import LLMError, NotFoundError, RateLimitError
from app.core.logging import get_logger
from app.models import Company, CompanyAIResearch, ResearchStatus
from app.modules.ai.context import build_research_context, render_prompt_variables
from app.modules.ai.prompts import get_research_prompt
from app.modules.ai.provider import (
    InvalidAIResponseError,
    LLMProvider,
    ProviderUnavailableError,
    get_provider,
)
from app.modules.ai.schemas import (
    ResearchMeta,
    ResearchPayload,
    ResearchResponse,
)

logger = get_logger(__name__)

TERMINAL_STATUSES = {ResearchStatus.COMPLETED.value, ResearchStatus.FAILED.value}


# ── Workspace-scoped lookups ──────────────────────────────────

def get_company_for_workspace(db: Session, company_id: str, workspace_id: Any) -> Company:
    """
    Fetch a company, enforcing workspace isolation.

    Raises NotFoundError for both "does not exist" and "belongs to another
    workspace" — matching the existing Avenor convention, which never reveals
    the existence of another workspace's records.
    """
    # Validate before touching the DB: passing a malformed UUID to db.get()
    # raises a DBAPIError that aborts the surrounding transaction, causing every
    # later query on this session to fail. A bad path param must be a plain 404.
    try:
        company_uuid = uuid.UUID(str(company_id))
    except (ValueError, AttributeError, TypeError):
        raise NotFoundError("Company", str(company_id))

    company = db.get(Company, company_uuid)
    if not company or str(company.workspace_id) != str(workspace_id):
        raise NotFoundError("Company", str(company_id))
    return company


def get_research_row(db: Session, company_id: Any, workspace_id: Any) -> CompanyAIResearch | None:
    return (
        db.query(CompanyAIResearch)
        .filter_by(company_id=company_id, workspace_id=workspace_id)
        .first()
    )


# ── Stale-run reaping ─────────────────────────────────────────

def _reap_if_stale(db: Session, row: CompanyAIResearch) -> CompanyAIResearch:
    """
    A worker that died mid-generation would leave a row stuck in `running`,
    and the frontend would poll it forever. Any run older than the configured
    threshold is marked failed so the UI can offer a retry.
    """
    if row.status not in (ResearchStatus.PENDING.value, ResearchStatus.RUNNING.value):
        return row

    cutoff = datetime.now(timezone.utc) - timedelta(
        minutes=settings.AI_RESEARCH_STALE_RUNNING_MINUTES
    )
    updated_at = row.updated_at
    if updated_at is None:
        return row
    if updated_at.tzinfo is None:
        updated_at = updated_at.replace(tzinfo=timezone.utc)

    if updated_at < cutoff:
        logger.warning(
            "research_run_stale_reaped",
            company_id=str(row.company_id),
            workspace_id=str(row.workspace_id),
            stuck_since=updated_at.isoformat(),
        )
        row.status = ResearchStatus.FAILED.value
        row.error_message = (
            "Generation timed out and did not complete. Please try again."
        )
        db.commit()
        db.refresh(row)
    return row


# ── Serialization ─────────────────────────────────────────────

def _empty_response(company_id: str) -> ResearchResponse:
    return ResearchResponse(company_id=company_id, status="none")


def to_response(
    row: CompanyAIResearch | None,
    company_id: str,
    *,
    cached: bool = False,
    is_stale: bool = False,
) -> ResearchResponse:
    """Map a stored row onto the public API contract."""
    if row is None:
        return _empty_response(company_id)

    payload: dict[str, Any] = {}
    if row.status == ResearchStatus.COMPLETED.value:
        payload = {
            "summary": row.summary,
            "buying_signals": row.buying_signals or [],
            "pain_points": row.pain_points or [],
            "recommended_personas": row.recommended_personas or [],
            "outreach_strategy": row.outreach_strategy or None,
            "talking_points": row.talking_points or [],
            "risks": row.risks or [],
            "next_actions": row.next_actions or [],
        }

    return ResearchResponse(
        company_id=company_id,
        status=row.status,
        cached=cached,
        is_stale=is_stale,
        error_message=row.error_message,
        meta=ResearchMeta(
            model_provider=row.model_provider,
            model_version=row.model_version,
            prompt_version=row.prompt_version,
            generation_duration_ms=row.generation_duration_ms,
            input_hash=row.input_hash,
        ),
        generated_at=row.created_at,
        updated_at=row.updated_at,
        **payload,
    )


# ── Read path ─────────────────────────────────────────────────

def get_latest_research(
    db: Session,
    company_id: str,
    workspace_id: Any,
    *,
    provider: LLMProvider | None = None,
) -> ResearchResponse:
    """GET handler logic — returns the latest report and whether it is stale."""
    company = get_company_for_workspace(db, company_id, workspace_id)

    row = get_research_row(db, company.id, workspace_id)
    if row is None:
        return _empty_response(str(company.id))

    row = _reap_if_stale(db, row)

    is_stale = False
    if row.status == ResearchStatus.COMPLETED.value and row.input_hash:
        # Cheap enough to tell the UI its report no longer reflects reality.
        try:
            active_provider = provider or get_provider()
            current_hash = _compute_current_hash(db, company, active_provider)
            is_stale = current_hash != row.input_hash
        except LLMError:
            # Provider unavailable is not a reason to fail a read.
            is_stale = False

    return to_response(row, str(company.id), cached=True, is_stale=is_stale)


def _compute_current_hash(db: Session, company: Company, provider: LLMProvider) -> str:
    context = build_research_context(db, company)
    template = get_research_prompt()
    return context.compute_input_hash(template.version, provider.model_version)


# ── Write path ────────────────────────────────────────────────

def request_research(
    db: Session,
    company_id: str,
    workspace_id: Any,
    *,
    force_refresh: bool = False,
    provider: LLMProvider | None = None,
) -> tuple[ResearchResponse, bool]:
    """
    POST handler logic.

    Returns (response, should_dispatch). `should_dispatch` tells the route
    whether to enqueue the Celery task — the service never imports the worker,
    keeping the dependency direction one-way.
    """
    company = get_company_for_workspace(db, company_id, workspace_id)
    active_provider = provider or get_provider()

    if not active_provider.is_available():
        raise ProviderUnavailableError(
            f"AI provider '{active_provider.name}' is not configured"
        )

    row = get_research_row(db, company.id, workspace_id)
    if row is not None:
        row = _reap_if_stale(db, row)

    # Already generating — never dispatch a duplicate run.
    if row is not None and row.status in (
        ResearchStatus.PENDING.value,
        ResearchStatus.RUNNING.value,
    ):
        logger.info(
            "research_already_in_progress",
            company_id=str(company.id),
            workspace_id=str(workspace_id),
            status=row.status,
        )
        return to_response(row, str(company.id)), False

    current_hash = _compute_current_hash(db, company, active_provider)

    # Cache hit — intelligence unchanged since the last completed report.
    if (
        not force_refresh
        and row is not None
        and row.status == ResearchStatus.COMPLETED.value
        and row.input_hash == current_hash
    ):
        logger.info(
            "research_cache_hit",
            company_id=str(company.id),
            workspace_id=str(workspace_id),
            input_hash=current_hash[:12],
        )
        return to_response(row, str(company.id), cached=True), False

    if row is None:
        row = CompanyAIResearch(
            workspace_id=company.workspace_id,
            company_id=company.id,
        )
        db.add(row)

    row.status = ResearchStatus.PENDING.value
    row.error_message = None
    db.commit()
    db.refresh(row)

    logger.info(
        "research_generation_queued",
        company_id=str(company.id),
        workspace_id=str(workspace_id),
        force_refresh=force_refresh,
        reason="forced" if force_refresh else "hash_changed_or_absent",
    )
    return to_response(row, str(company.id)), True


# ── Generation (worker path) ──────────────────────────────────

def generate_research(
    db: Session,
    company_id: str,
    workspace_id: Any,
    *,
    provider: LLMProvider | None = None,
) -> dict[str, Any]:
    """
    Perform the actual generation. Called from the Celery task.

    Never raises for expected AI failures — records them on the row and returns
    stats so the Job audit record stays accurate.
    """
    started = time.perf_counter()
    company = get_company_for_workspace(db, company_id, workspace_id)
    active_provider = provider or get_provider()

    row = get_research_row(db, company.id, workspace_id)
    if row is None:
        row = CompanyAIResearch(workspace_id=company.workspace_id, company_id=company.id)
        db.add(row)

    row.status = ResearchStatus.RUNNING.value
    db.commit()

    def _fail(message: str, code: str) -> dict[str, Any]:
        row.status = ResearchStatus.FAILED.value
        row.error_message = message[:1000]
        row.generation_duration_ms = int((time.perf_counter() - started) * 1000)
        db.commit()
        logger.warning(
            "research_generation_failed",
            company_id=str(company.id),
            workspace_id=str(workspace_id),
            code=code,
            error=message,
        )
        return {"generated": 0, "failed": 1, "status": "failed", "code": code}

    try:
        context = build_research_context(db, company)
    except Exception as exc:
        return _fail(f"Failed to assemble research context: {exc}", "context_error")

    if not context.has_minimum_data:
        return _fail(
            "Not enough company data available to generate research.",
            "insufficient_data",
        )

    template = get_research_prompt()
    input_hash = context.compute_input_hash(template.version, active_provider.model_version)

    try:
        system_prompt, user_prompt = template.render(**render_prompt_variables(context))
    except (KeyError, IndexError) as exc:
        return _fail(f"Prompt template rendering failed: {exc}", "prompt_error")

    try:
        raw_payload = active_provider.generate_json(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
        )
    except RateLimitError as exc:
        return _fail(exc.message, exc.code)
    except ProviderUnavailableError as exc:
        return _fail(exc.message, exc.code)
    except InvalidAIResponseError as exc:
        return _fail(f"AI returned an unusable response: {exc.message}", exc.code)
    except LLMError as exc:
        return _fail(exc.message, exc.code)
    except Exception as exc:  # defensive: the API must never crash
        return _fail(f"Unexpected AI generation error: {exc}", "unexpected_error")

    try:
        payload = ResearchPayload.model_validate(raw_payload)
    except PydanticValidationError as exc:
        return _fail(
            f"AI response failed schema validation: {exc.error_count()} error(s)",
            "schema_validation_failed",
        )

    duration_ms = int((time.perf_counter() - started) * 1000)

    row.summary = payload.summary
    row.buying_signals = [item.model_dump() for item in payload.buying_signals]
    row.pain_points = [item.model_dump() for item in payload.pain_points]
    row.recommended_personas = [item.model_dump() for item in payload.recommended_personas]
    row.outreach_strategy = payload.outreach_strategy.model_dump()
    row.talking_points = [item.model_dump() for item in payload.talking_points]
    row.risks = [item.model_dump() for item in payload.risks]
    row.next_actions = [item.model_dump() for item in payload.next_actions]

    row.status = ResearchStatus.COMPLETED.value
    row.error_message = None
    row.model_provider = active_provider.name
    row.model_version = active_provider.model_version
    row.prompt_version = template.version
    row.generation_duration_ms = duration_ms
    row.input_hash = input_hash
    db.commit()

    logger.info(
        "research_generation_complete",
        company_id=str(company.id),
        workspace_id=str(workspace_id),
        provider=active_provider.name,
        model=active_provider.model_version,
        prompt_version=template.version,
        duration_ms=duration_ms,
        input_hash=input_hash[:12],
        signal_count=len(payload.buying_signals),
    )
    return {
        "generated": 1,
        "failed": 0,
        "status": "completed",
        "duration_ms": duration_ms,
    }
