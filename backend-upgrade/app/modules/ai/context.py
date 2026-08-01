"""
Research context assembly.

Gathers everything Avenor already knows about a company — profile, signals,
scores, contacts, intelligence feed, ICP, CRM deals, comparable wins — into a
typed context, and derives a deterministic `input_hash` from it.

This module is the enrichment seam. Future providers (LinkedIn, Crunchbase,
Company Websites, News APIs, Job Boards, Product Hunt, GitHub, G2) implement
`ContextEnricher` and are registered below. Their output lands in
`ResearchContext.enrichment` and is folded into both the prompt and the hash —
without touching prompts.py, schemas.py, research_service.py, the API
contracts, or the frontend.

Phase 5.1 ships zero enrichers: all data comes from inside Avenor.
"""
import hashlib
import json
from dataclasses import dataclass, field
from typing import Any, Protocol

from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.models import (
    Company,
    CompanyScore,
    Contact,
    HubSpotDeal,
    ICPConfig,
    IntelligenceFeedItem,
    Outcome,
    OutcomeType,
    Signal,
)

logger = get_logger(__name__)

MAX_SIGNALS = 25
MAX_CONTACTS = 25
MAX_DEALS = 10
MAX_SIMILAR = 5

POSITIVE_OUTCOME_TYPES = {
    OutcomeType.BECAME_OPPORTUNITY.value,
    OutcomeType.MEETING_BOOKED.value,
    OutcomeType.REPLIED_POSITIVE.value,
    OutcomeType.CLOSED_WON.value,
}


@dataclass
class ResearchContext:
    """Everything the model is allowed to reason about, plus its digest."""

    company_id: str
    workspace_id: str
    company_profile: dict[str, Any]
    scoring: dict[str, Any]
    signals: list[dict[str, Any]]
    intelligence: dict[str, Any]
    contacts: list[dict[str, Any]]
    icp: dict[str, Any]
    crm: dict[str, Any]
    similar_companies: list[dict[str, Any]]
    enrichment: dict[str, Any] = field(default_factory=dict)

    def to_hashable(self, prompt_version: str, model_identifier: str) -> dict[str, Any]:
        """
        The canonical representation the input hash is computed over.

        Deliberately excludes volatile fields (last_seen_at, scored_at
        timestamps, sync clocks) so that re-reading unchanged intelligence
        produces an identical hash. Includes prompt version and model so that
        changing either invalidates the cache.
        """
        return {
            "company_profile": self.company_profile,
            "scoring": self.scoring,
            "signals": self.signals,
            "intelligence": self.intelligence,
            "contacts": self.contacts,
            "icp": self.icp,
            "crm": self.crm,
            "similar_companies": self.similar_companies,
            "enrichment": self.enrichment,
            "prompt_version": prompt_version,
            "model": model_identifier,
        }

    def compute_input_hash(self, prompt_version: str, model_identifier: str) -> str:
        """SHA-256 over a canonical JSON serialization (sorted keys, no whitespace drift)."""
        canonical = json.dumps(
            self.to_hashable(prompt_version, model_identifier),
            sort_keys=True,
            separators=(",", ":"),
            default=str,
            ensure_ascii=True,
        )
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    @property
    def has_minimum_data(self) -> bool:
        """A company name alone is enough to brief on; anything less is not."""
        return bool(self.company_profile.get("name"))


# ── Enrichment seam ───────────────────────────────────────────

class ContextEnricher(Protocol):
    """
    Future external enrichment providers implement this.

    `key` namespaces the provider's output inside ResearchContext.enrichment.
    Returned data must be JSON-serializable and deterministic for a given
    company state, otherwise it will defeat the input hash cache.
    """

    key: str

    def enrich(self, db: Session, company: Company) -> dict[str, Any]:
        """Return this provider's contribution to the research context."""


_ENRICHERS: list[ContextEnricher] = []


def register_enricher(enricher: ContextEnricher) -> None:
    """Register an external enrichment provider (LinkedIn, Crunchbase, G2, ...)."""
    _ENRICHERS.append(enricher)


def _run_enrichers(db: Session, company: Company) -> dict[str, Any]:
    """
    Run every registered enricher. A failing enricher degrades the report; it
    never fails the generation.
    """
    enrichment: dict[str, Any] = {}
    for enricher in _ENRICHERS:
        try:
            enrichment[enricher.key] = enricher.enrich(db, company)
        except Exception as exc:
            logger.warning(
                "research_enricher_failed",
                enricher=enricher.key,
                company_id=str(company.id),
                error=str(exc),
            )
    return enrichment


# ── Builders ──────────────────────────────────────────────────

def _build_company_profile(company: Company) -> dict[str, Any]:
    return {
        "name": company.name,
        "domain": company.domain,
        "website": company.website,
        "linkedin_url": company.linkedin_url,
        "industry": company.industry,
        "sub_industry": company.sub_industry,
        "employee_count": company.employee_count,
        "employee_range": company.employee_range,
        "location": " ".join(
            part
            for part in (company.location_city, company.location_state, company.location_country)
            if part
        )
        or None,
        "founded_year": company.founded_year,
        "description": company.description,
        "technologies": sorted(company.technologies or []),
        "funding_total_usd": company.funding_total_usd,
        "last_funding_stage": company.last_funding_stage,
        "last_funding_amount_usd": company.last_funding_amount_usd,
        "last_funding_date": company.last_funding_date.date().isoformat()
        if company.last_funding_date
        else None,
        "status": company.status,
    }


def _build_scoring(company: Company, score: CompanyScore | None) -> dict[str, Any]:
    return {
        # Rounded: score jitter below 1% should not invalidate a cached report.
        "composite_score": round(company.composite_score or 0.0, 3),
        "icp_score": round(company.icp_score or 0.0, 3),
        "signal_score": round(company.signal_score or 0.0, 3),
        "buying_window": company.buying_window,
        "buying_window_confidence": round(company.buying_window_confidence or 0.0, 3),
        "icp_breakdown": score.icp_breakdown if score else {},
        "signal_breakdown": score.signal_breakdown if score else [],
        "buying_window_reasoning": score.buying_window_reasoning if score else None,
    }


def _build_signals(signals: list[Signal]) -> list[dict[str, Any]]:
    return [
        {
            "type": signal.signal_type,
            "source": signal.signal_source,
            "title": signal.title,
            "description": signal.description,
            "strength": round(signal.decayed_strength or 0.0, 3),
            "detected_at": signal.detected_at.date().isoformat() if signal.detected_at else None,
        }
        for signal in signals
    ]


def _build_intelligence(item: IntelligenceFeedItem | None) -> dict[str, Any]:
    if item is None:
        return {}
    return {
        "signal_summary": item.signal_summary,
        "buying_window_reasoning": item.buying_window_reasoning,
        "recommended_angle": item.recommended_angle,
        "recommended_contact_title": item.recommended_contact_title,
        "top_signals": item.top_signals or [],
    }


def _build_contacts(contacts: list[Contact]) -> list[dict[str, Any]]:
    return [
        {
            "name": contact.full_name,
            "title": contact.title,
            "seniority": contact.seniority,
            "department": contact.department,
            "has_email": bool(contact.email),
            "is_primary": contact.is_primary,
        }
        for contact in contacts
    ]


def _build_icp(icp: ICPConfig | None) -> dict[str, Any]:
    if icp is None:
        return {}
    return {
        "product_name": icp.product_name,
        "product_description": icp.product_description,
        "key_pain_points": icp.key_pain_points or [],
        "customer_personas": icp.customer_personas or [],
        "target_industries": icp.industries or [],
        "target_employee_range": [icp.min_employees, icp.max_employees],
        "target_technologies": icp.technologies or [],
        "competitor_names": icp.competitor_names or [],
        "keywords": icp.keywords or [],
    }


def _build_crm(deals: list[HubSpotDeal], outcomes: list[Outcome]) -> dict[str, Any]:
    return {
        "deals": [
            {
                "name": deal.deal_name,
                "stage": deal.deal_stage,
                "amount_usd": deal.amount_usd,
                "is_closed_won": deal.is_closed_won,
                "is_closed_lost": deal.is_closed_lost,
                "close_date": deal.close_date.date().isoformat() if deal.close_date else None,
            }
            for deal in deals
        ],
        "logged_outcomes": [
            {
                "type": outcome.outcome_type,
                "source": outcome.outcome_source,
                "deal_value_usd": outcome.deal_value_usd,
                "notes": outcome.notes,
                "occurred_at": outcome.occurred_at.date().isoformat()
                if outcome.occurred_at
                else None,
            }
            for outcome in outcomes
        ],
    }


def _fetch_similar_won_companies(
    db: Session, company: Company, workspace_id: str
) -> list[dict[str, Any]]:
    """
    Comparable accounts that converted, reusing the Phase 4.1 embedding column
    when it is populated and falling back to industry match when it is not.
    """
    rows = (
        db.query(Company.name, Company.industry, Company.employee_count)
        .join(Outcome, Outcome.company_id == Company.id)
        .filter(
            Company.workspace_id == workspace_id,
            Company.id != company.id,
            Outcome.outcome_type.in_(sorted(POSITIVE_OUTCOME_TYPES)),
        )
        .order_by(Company.name)
        .limit(MAX_SIMILAR)
        .all()
    )
    return [
        {"name": name, "industry": industry, "employee_count": employee_count}
        for name, industry, employee_count in rows
    ]


def build_research_context(db: Session, company: Company) -> ResearchContext:
    """
    Assemble the full research context for a company from Avenor's own data.

    All queries are scoped to the company's workspace. No external API is
    called in Phase 5.1.
    """
    workspace_id = str(company.workspace_id)

    signals = (
        db.query(Signal)
        .filter_by(company_id=company.id, workspace_id=company.workspace_id)
        .order_by(Signal.decayed_strength.desc(), Signal.detected_at.desc())
        .limit(MAX_SIGNALS)
        .all()
    )

    contacts = (
        db.query(Contact)
        .filter_by(company_id=company.id)
        .order_by(Contact.is_primary.desc(), Contact.full_name)
        .limit(MAX_CONTACTS)
        .all()
    )

    feed_item = (
        db.query(IntelligenceFeedItem)
        .filter_by(company_id=company.id, workspace_id=company.workspace_id)
        .order_by(IntelligenceFeedItem.generated_at.desc())
        .first()
    )

    icp = db.query(ICPConfig).filter_by(workspace_id=company.workspace_id).first()

    deals = (
        db.query(HubSpotDeal)
        .filter_by(company_id=company.id, workspace_id=company.workspace_id)
        .order_by(HubSpotDeal.created_date.desc().nullslast())
        .limit(MAX_DEALS)
        .all()
    )

    outcomes = (
        db.query(Outcome)
        .filter_by(company_id=company.id, workspace_id=company.workspace_id)
        .order_by(Outcome.occurred_at.desc())
        .limit(MAX_DEALS)
        .all()
    )

    context = ResearchContext(
        company_id=str(company.id),
        workspace_id=workspace_id,
        company_profile=_build_company_profile(company),
        scoring=_build_scoring(company, company.score_snapshot),
        signals=_build_signals(signals),
        intelligence=_build_intelligence(feed_item),
        contacts=_build_contacts(contacts),
        icp=_build_icp(icp),
        crm=_build_crm(deals, outcomes),
        similar_companies=_fetch_similar_won_companies(db, company, workspace_id),
    )
    context.enrichment = _run_enrichers(db, company)

    logger.info(
        "research_context_built",
        company_id=context.company_id,
        workspace_id=workspace_id,
        signal_count=len(context.signals),
        contact_count=len(context.contacts),
        has_icp=bool(context.icp),
        enrichers=len(_ENRICHERS),
    )
    return context


# ── Prompt rendering ──────────────────────────────────
MAX_SIGNALS = 15
MAX_CONTACTS = 15
MAX_DEALS = 10
MAX_SIMILAR = 5


def _render_block(data: Any, empty: str) -> str:
    """Render a context block as compact JSON for the prompt to optimize token size."""
    if not data:
        return empty
    return json.dumps(data, sort_keys=True, default=str, ensure_ascii=False, separators=(",", ":"))


def render_prompt_variables(context: ResearchContext) -> dict[str, Any]:
    """Map a ResearchContext onto the research prompt's placeholders."""
    company_profile = dict(context.company_profile)
    if context.enrichment:
        company_profile["external_enrichment"] = context.enrichment

    return {
        "company_profile": _render_block(company_profile, "No company profile available."),
        "scoring": _render_block(context.scoring, "Not scored yet."),
        "signal_count": len(context.signals),
        "signals": _render_block(context.signals, "No buying signals detected yet."),
        "intelligence": _render_block(
            context.intelligence, "No intelligence feed item generated yet."
        ),
        "contact_count": len(context.contacts),
        "contacts": _render_block(context.contacts, "No contacts known."),
        "icp": _render_block(context.icp, "ICP not configured for this workspace."),
        "crm": _render_block(context.crm, "No CRM deals or outcomes linked."),
        "similar_companies": _render_block(
            context.similar_companies, "No comparable won accounts yet."
        ),
    }
