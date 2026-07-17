# """
# Intelligence engine.
# Generates Account Intelligence Feed items for each high-scored company.
# Combines:
#   1. Signal summarization (GPT-4o)
#   2. Buying window reasoning (from scorer)
#   3. Recommended outreach angle (GPT-4o)
#   4. Similar converted companies (pgvector similarity search)

# Results are cached in intelligence_feed_items table (24-hour TTL).
# LLM calls are skipped if a fresh cache entry exists.
# """
# import json
# from datetime import datetime, timedelta, timezone
# from uuid import UUID

# from openai import OpenAI
# from sqlalchemy import select, text
# from sqlalchemy.orm import Session

# from app.core.config import settings
# from app.core.exceptions import LLMError
# from app.core.logging import get_logger
# from app.models import (
#     Company, Contact, ICPConfig, IntelligenceFeedItem,
#     Outcome, OutcomeType, Signal, CompanyStatus,
# )

# logger = get_logger(__name__)

# CACHE_TTL_HOURS = 24
# FEED_ITEM_LIMIT = 50  # max items per workspace per feed

# POSITIVE_OUTCOME_TYPES = {
#     OutcomeType.BECAME_OPPORTUNITY.value,
#     OutcomeType.MEETING_BOOKED.value,
#     OutcomeType.REPLIED_POSITIVE.value,
#     OutcomeType.CLOSED_WON.value,
# }


# # ── LLM Client ────────────────────────────────────────────────

# def _get_openai_client() -> OpenAI:
#     #if not settings.has_openai:
#     if not settings.has_gemini:
    
#         raise LLMError("OpenAI API key not configured")
#     #return OpenAI(api_key=settings.OPENAI_API_KEY)
#     return OpenAI(
#     api_key=settings.GEMINI_API_KEY,
#     base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
# )


# # ── Signal summarizer ─────────────────────────────────────────

# SIGNAL_SUMMARY_PROMPT = """You are a B2B sales intelligence analyst. Summarize the following company signals 
# into 2 clear, specific sentences that explain what is happening at this company and why it matters for a sales conversation.

# Be specific. Use the actual signal data. Do not use vague phrases like "significant changes" or "interesting developments".
# Do not use bullet points. Write in plain prose.

# Company: {company_name}
# Industry: {industry}
# Employee count: {employee_count}

# Signals detected:
# {signals_text}

# Respond with ONLY the 2-sentence summary. Nothing else."""


# def generate_signal_summary(
#     company: Company,
#     signals: list[Signal],
#     client: OpenAI,
# ) -> str:
#     """Generate a 2-sentence plain-English signal summary."""
#     signals_text = "\n".join([
#         f"- {s.signal_type.upper()}: {s.title}"
#         + (f" ({s.description[:100]})" if s.description else "")
#         for s in sorted(signals, key=lambda x: x.decayed_strength, reverse=True)[:5]
#     ])

#     prompt = SIGNAL_SUMMARY_PROMPT.format(
#         company_name=company.name,
#         industry=company.industry or "unknown",
#         employee_count=company.employee_count or "unknown",
#         signals_text=signals_text,
#     )

#     try:
#         response = client.chat.completions.create(
#             #model=settings.OPENAI_MODEL,
#             model=settings.GEMINI_MODEL,
#             messages=[{"role": "user", "content": prompt}],
#             temperature=0.3,
#             max_tokens=150,
#         )
#         return response.choices[0].message.content.strip()
#     except Exception as e:
#         logger.warning("signal_summary_llm_failed", error=str(e), company=company.name)
#         # Graceful fallback — non-LLM summary
#         top = signals[:3]
#         return (
#             f"{company.name} is showing {len(signals)} buying signals including "
#             f"{', '.join(s.title for s in top)}. "
#             f"These suggest the company may be entering an active evaluation phase."
#         )


# # ── Angle recommender ─────────────────────────────────────────

# ANGLE_PROMPT = """You are an expert B2B sales strategist. Given these company signals and product context,
# recommend a specific outreach angle in 2–3 sentences.

# The angle must:
# - Reference a SPECIFIC signal (not generic)
# - Connect it to a specific pain the product solves
# - Suggest the opening framing for a cold email or call
# - Sound like advice from a smart colleague, not a marketing script

# Company: {company_name}
# Industry: {industry}
# Signal summary: {signal_summary}
# Product: {product_name}
# Product description: {product_description}
# Key pain points product solves: {pain_points}
# Target personas: {personas}

# Respond with ONLY the recommended angle. No headers, no bullets."""


# def generate_recommended_angle(
#     company: Company,
#     signal_summary: str,
#     icp: ICPConfig,
#     client: OpenAI,
# ) -> str:
#     """Generate a recommended outreach angle based on signals and product context."""
#     prompt = ANGLE_PROMPT.format(
#         company_name=company.name,
#         industry=company.industry or "unknown",
#         signal_summary=signal_summary,
#         product_name=icp.product_name or "our product",
#         product_description=icp.product_description or "a B2B software solution",
#         pain_points=", ".join(icp.key_pain_points[:3]) if icp.key_pain_points else "scaling challenges",
#         personas=", ".join(icp.customer_personas[:3]) if icp.customer_personas else "VP of Engineering, Head of Data",
#     )

#     try:
#         response = client.chat.completions.create(
#             #model=settings.OPENAI_MODEL,
#             model=settings.GEMINI_MODEL,
#             messages=[{"role": "user", "content": prompt}],
#             temperature=0.5,
#             max_tokens=150,
#         )
#         return response.choices[0].message.content.strip()
#     except Exception as e:
#         logger.warning("angle_llm_failed", error=str(e), company=company.name)
#         return (
#             f"Lead with {company.name}'s recent signals. "
#             f"Connect to the pain of scaling {company.industry or 'B2B'} operations "
#             f"and how {icp.product_name or 'the product'} helps companies at their stage."
#         )


# # ── Similarity search ─────────────────────────────────────────

# def find_similar_converted_companies(
#     db: Session,
#     company: Company,
#     workspace_id: str,
#     limit: int = 3,
# ) -> list[dict]:
#     """
#     Find similar companies from outcomes that converted (positive outcomes).
#     Uses pgvector cosine similarity on company embeddings.
#     Falls back to industry+size matching if embeddings aren't available.
#     """
#     # Get company IDs with positive outcomes in this workspace
#     positive_outcomes = (
#         db.query(Outcome)
#         .filter(
#             Outcome.workspace_id == workspace_id,
#             Outcome.outcome_type.in_(list(POSITIVE_OUTCOME_TYPES)),
#         )
#         .all()
#     )

#     if not positive_outcomes:
#         return []

#     converted_company_ids = [str(o.company_id) for o in positive_outcomes]

#     if company.embedding and len(company.embedding) > 0:
#         # Vector similarity search
#         try:
#             results = db.execute(
#                 text("""
#                     SELECT c.id, c.name, c.industry, c.employee_count,
#                            1 - (c.embedding <=> :query_embedding) AS similarity
#                     FROM companies c
#                     WHERE c.id = ANY(:company_ids)
#                       AND c.embedding IS NOT NULL
#                     ORDER BY c.embedding <=> :query_embedding
#                     LIMIT :limit
#                 """),
#                 {
#                     "query_embedding": company.embedding,
#                     "company_ids": converted_company_ids,
#                     "limit": limit,
#                 },
#             ).fetchall()

#             return [
#                 {
#                     "name": r.name,
#                     "industry": r.industry,
#                     "employee_count": r.employee_count,
#                     "similarity": round(float(r.similarity), 3),
#                 }
#                 for r in results
#             ]
#         except Exception as e:
#             logger.warning("vector_search_failed", error=str(e))

#     # Fallback: match by industry and employee size range
#     similar = (
#         db.query(Company)
#         .filter(
#             Company.id.in_(converted_company_ids),
#             Company.industry == company.industry,
#         )
#         .limit(limit)
#         .all()
#     )

#     return [
#         {"name": c.name, "industry": c.industry, "employee_count": c.employee_count}
#         for c in similar
#     ]


# # ── Embedding generation ───────────────────────────────────────

# def generate_company_embedding(company: Company, client: OpenAI) -> list[float] | None:
#     """Generate embedding for a company profile for similarity search."""
#     text_to_embed = " ".join(filter(None, [
#         company.name,
#         company.industry,
#         company.description,
#         " ".join(company.technologies[:10] if company.technologies else []),
#         company.employee_range,
#         company.location_country,
#     ]))

#     if not text_to_embed.strip():
#         return None

#     try:
#         response = client.embeddings.create(
#             model=settings.OPENAI_EMBEDDING_MODEL,
#             input=text_to_embed[:2000],  # token limit safety
#         )
#         return response.data[0].embedding
#     except Exception as e:
#         logger.warning("embedding_failed", company=company.name, error=str(e))
#         return None


# # ── Best contact selector ─────────────────────────────────────

# def select_best_contact_title(contacts: list[Contact], personas: list[str]) -> str | None:
#     """Select the most relevant contact title based on ICP personas."""
#     if not contacts:
#         return None

#     personas_lower = [p.lower() for p in personas]

#     # Score contacts by persona match
#     scored = []
#     for c in contacts:
#         title_lower = (c.title or "").lower()
#         score = sum(1 for p in personas_lower if p in title_lower)
#         # Bonus for primary flag
#         if c.is_primary:
#             score += 0.5
#         scored.append((score, c))

#     scored.sort(key=lambda x: x[0], reverse=True)
#     return scored[0][1].title if scored else None


# # ── Main generator ────────────────────────────────────────────

# def generate_feed_item(
#     db: Session,
#     company: Company,
#     icp: ICPConfig,
#     workspace_id: str,
#     force_refresh: bool = False,
# ) -> IntelligenceFeedItem | None:
#     """
#     Generate (or return cached) intelligence feed item for one company.
#     Returns None if company doesn't qualify for the feed.
#     """
#     # Only generate for active companies
#     if company.status not in (CompanyStatus.ACTIVE,):
#         return None

#     if company.composite_score < icp.watch_score_threshold:
#         return None

#     # Check cache
#     if not force_refresh:
#         existing = (
#             db.query(IntelligenceFeedItem)
#             .filter_by(company_id=company.id)
#             .filter(IntelligenceFeedItem.expires_at > datetime.now(timezone.utc))
#             .filter_by(is_dismissed=False)
#             .first()
#         )
#         if existing:
#             return existing

#     # Load signals
#     signals = (
#         db.query(Signal)
#         .filter_by(company_id=company.id)
#         .order_by(Signal.detected_at.desc())
#         .limit(10)
#         .all()
#     )

#     if not signals:
#         return None

#     # Generate LLM content (with graceful fallback)
#     client = _get_openai_client() if settings.has_openai else None

#     if client:
#         # Generate embedding if missing
#         if company.embedding is None:
#             embedding = generate_company_embedding(company, client)
#             if embedding:
#                 company.embedding = embedding

#         signal_summary = generate_signal_summary(company, signals, client)
#         recommended_angle = generate_recommended_angle(company, signal_summary, icp, client)
#     else:
#         # Fallback: rule-based summaries when no OpenAI key
#         top_signals = sorted(signals, key=lambda s: s.decayed_strength, reverse=True)[:3]
#         signal_summary = (
#             f"{company.name} is showing {len(signals)} buying signals. "
#             f"Top signals: {', '.join(s.title for s in top_signals)}."
#         )
#         recommended_angle = (
#             f"Reach out referencing {top_signals[0].title if top_signals else 'recent activity'}. "
#             f"Connect to how {icp.product_name or 'the product'} helps at their stage."
#         )

#     # Find similar converted companies
#     similar = find_similar_converted_companies(db, company, workspace_id)

#     # Top signals for the feed (serialized)
#     top_signals_data = [
#         {
#             "type": s.signal_type,
#             "title": s.title,
#             "detected_at": s.detected_at.isoformat(),
#             "strength": round(s.decayed_strength, 3),
#         }
#         for s in sorted(signals, key=lambda x: x.decayed_strength, reverse=True)[:3]
#     ]

#     # Contact recommendation
#     contacts = db.query(Contact).filter_by(company_id=company.id).all()
#     recommended_title = select_best_contact_title(contacts, icp.customer_personas or [])

#     now = datetime.now(timezone.utc)

#     # Upsert feed item
#     feed_item = (
#         db.query(IntelligenceFeedItem)
#         .filter_by(company_id=company.id)
#         .first()
#     )

#     if feed_item is None:
#         feed_item = IntelligenceFeedItem(
#             workspace_id=workspace_id,
#             company_id=company.id,
#         )
#         db.add(feed_item)

#     feed_item.composite_score = company.composite_score
#     feed_item.buying_window = company.buying_window
#     feed_item.buying_window_confidence = company.buying_window_confidence
#     feed_item.signal_summary = signal_summary
#     feed_item.buying_window_reasoning = (
#         company.score_snapshot.buying_window_reasoning
#         if company.score_snapshot else "Signals indicate buying activity."
#     )
#     feed_item.recommended_angle = recommended_angle
#     feed_item.recommended_contact_title = recommended_title
#     feed_item.top_signals = top_signals_data
#     feed_item.similar_converted_companies = similar
#     feed_item.generated_at = now
#     feed_item.expires_at = now + timedelta(hours=CACHE_TTL_HOURS)
#     feed_item.is_dismissed = False

#     db.flush()
#     return feed_item


# def run_feed_generation_for_workspace(
#     db: Session,
#     workspace_id: str,
#     force_refresh: bool = False,
# ) -> dict:
#     """
#     Generate intelligence feed items for all qualified companies in a workspace.
#     Called by nightly batch job.
#     """
#     from app.models import Workspace
#     workspace = db.get(Workspace, workspace_id)
#     if not workspace or not workspace.icp_config:
#         return {"skipped": True}

#     icp = workspace.icp_config

#     companies = (
#         db.query(Company)
#         .filter_by(workspace_id=workspace_id, status=CompanyStatus.ACTIVE)
#         .order_by(Company.composite_score.desc())
#         .limit(FEED_ITEM_LIMIT)
#         .all()
#     )

#     stats = {"generated": 0, "cached": 0, "skipped": 0, "errors": 0}

#     for company in companies:
#         try:
#             item = generate_feed_item(db, company, icp, workspace_id, force_refresh)
#             if item:
#                 stats["generated"] += 1
#             else:
#                 stats["skipped"] += 1
#         except Exception as e:
#             logger.error(
#                 "feed_item_generation_error",
#                 company=company.name,
#                 workspace_id=workspace_id,
#                 error=str(e),
#             )
#             stats["errors"] += 1

#     db.commit()
#     logger.info("feed_generation_complete", workspace_id=workspace_id, **stats)
#     return stats


"""
Intelligence engine.
Generates Account Intelligence Feed items for each high-scored company.
Combines:
  1. Signal summarization (Gemini)
  2. Buying window reasoning (from scorer)
  3. Recommended outreach angle (Gemini)
  4. Similar converted companies (pgvector similarity search)

Results are cached in intelligence_feed_items table (24-hour TTL).
LLM calls are skipped if a fresh cache entry exists.

Uses Google's Gemini API through its OpenAI-compatible endpoint,
so the `openai` client library is still used as the HTTP client.
"""
import json
from datetime import datetime, timedelta, timezone
from uuid import UUID

from openai import OpenAI
from sqlalchemy import select, text
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import LLMError
from app.core.logging import get_logger
from app.models import (
    Company, Contact, ICPConfig, IntelligenceFeedItem,
    Outcome, OutcomeType, Signal, CompanyStatus,
)

logger = get_logger(__name__)

CACHE_TTL_HOURS = 24
FEED_ITEM_LIMIT = 50  # max items per workspace per feed

# The companies.embedding column is Vector(1536).
# gemini-embedding-001 outputs 3072 dims by default but supports
# truncation — we request 1536 so no DB migration is required.
EMBEDDING_DIMENSIONS = 1536

GEMINI_OPENAI_COMPAT_BASE_URL = (
    "https://generativelanguage.googleapis.com/v1beta/openai/"
)

POSITIVE_OUTCOME_TYPES = {
    OutcomeType.BECAME_OPPORTUNITY.value,
    OutcomeType.MEETING_BOOKED.value,
    OutcomeType.REPLIED_POSITIVE.value,
    OutcomeType.CLOSED_WON.value,
}


# ── LLM Client ────────────────────────────────────────────────

def _get_gemini_client() -> OpenAI:
    """Return an OpenAI-SDK client pointed at Gemini's OpenAI-compatible endpoint."""
    if not settings.has_gemini:
        raise LLMError("Gemini API key not configured")
    return OpenAI(
        api_key=settings.GEMINI_API_KEY,
        base_url=GEMINI_OPENAI_COMPAT_BASE_URL,
    )


# ── Signal summarizer ─────────────────────────────────────────

SIGNAL_SUMMARY_PROMPT = """You are a B2B sales intelligence analyst. Summarize the following company signals 
into 2 clear, specific sentences that explain what is happening at this company and why it matters for a sales conversation.

Be specific. Use the actual signal data. Do not use vague phrases like "significant changes" or "interesting developments".
Do not use bullet points. Write in plain prose.

Company: {company_name}
Industry: {industry}
Employee count: {employee_count}

Signals detected:
{signals_text}

Respond with ONLY the 2-sentence summary. Nothing else."""


def generate_signal_summary(
    company: Company,
    signals: list[Signal],
    client: OpenAI,
) -> str:
    """Generate a 2-sentence plain-English signal summary."""
    signals_text = "\n".join([
        f"- {s.signal_type.upper()}: {s.title}"
        + (f" ({s.description[:100]})" if s.description else "")
        for s in sorted(signals, key=lambda x: x.decayed_strength, reverse=True)[:5]
    ])

    prompt = SIGNAL_SUMMARY_PROMPT.format(
        company_name=company.name,
        industry=company.industry or "unknown",
        employee_count=company.employee_count or "unknown",
        signals_text=signals_text,
    )

    try:
        response = client.chat.completions.create(
            model=settings.GEMINI_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=150,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.warning("signal_summary_llm_failed", error=str(e), company=company.name)
        # Graceful fallback — non-LLM summary
        top = signals[:3]
        return (
            f"{company.name} is showing {len(signals)} buying signals including "
            f"{', '.join(s.title for s in top)}. "
            f"These suggest the company may be entering an active evaluation phase."
        )


# ── Angle recommender ─────────────────────────────────────────

ANGLE_PROMPT = """You are an expert B2B sales strategist. Given these company signals and product context,
recommend a specific outreach angle in 2–3 sentences.

The angle must:
- Reference a SPECIFIC signal (not generic)
- Connect it to a specific pain the product solves
- Suggest the opening framing for a cold email or call
- Sound like advice from a smart colleague, not a marketing script

Company: {company_name}
Industry: {industry}
Signal summary: {signal_summary}
Product: {product_name}
Product description: {product_description}
Key pain points product solves: {pain_points}
Target personas: {personas}

Respond with ONLY the recommended angle. No headers, no bullets."""


def generate_recommended_angle(
    company: Company,
    signal_summary: str,
    icp: ICPConfig,
    client: OpenAI,
) -> str:
    """Generate a recommended outreach angle based on signals and product context."""
    prompt = ANGLE_PROMPT.format(
        company_name=company.name,
        industry=company.industry or "unknown",
        signal_summary=signal_summary,
        product_name=icp.product_name or "our product",
        product_description=icp.product_description or "a B2B software solution",
        pain_points=", ".join(icp.key_pain_points[:3]) if icp.key_pain_points else "scaling challenges",
        personas=", ".join(icp.customer_personas[:3]) if icp.customer_personas else "VP of Engineering, Head of Data",
    )

    try:
        response = client.chat.completions.create(
            model=settings.GEMINI_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            max_tokens=150,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.warning("angle_llm_failed", error=str(e), company=company.name)
        return (
            f"Lead with {company.name}'s recent signals. "
            f"Connect to the pain of scaling {company.industry or 'B2B'} operations "
            f"and how {icp.product_name or 'the product'} helps companies at their stage."
        )


# ── Similarity search ─────────────────────────────────────────

def find_similar_converted_companies(
    db: Session,
    company: Company,
    workspace_id: str,
    limit: int = 3,
) -> list[dict]:
    """
    Find similar companies from outcomes that converted (positive outcomes).
    Uses pgvector cosine similarity on company embeddings.
    Falls back to industry+size matching if embeddings aren't available.
    """
    # Get company IDs with positive outcomes in this workspace
    positive_outcomes = (
        db.query(Outcome)
        .filter(
            Outcome.workspace_id == workspace_id,
            Outcome.outcome_type.in_(list(POSITIVE_OUTCOME_TYPES)),
        )
        .all()
    )

    if not positive_outcomes:
        return []

    converted_company_ids = [str(o.company_id) for o in positive_outcomes]

    if company.embedding is not None and len(company.embedding) > 0:
        # Vector similarity search
        try:
            results = db.execute(
                text("""
                    SELECT c.id, c.name, c.industry, c.employee_count,
                           1 - (c.embedding <=> :query_embedding) AS similarity
                    FROM companies c
                    WHERE c.id = ANY(:company_ids)
                      AND c.embedding IS NOT NULL
                    ORDER BY c.embedding <=> :query_embedding
                    LIMIT :limit
                """),
                {
                    "query_embedding": company.embedding,
                    "company_ids": converted_company_ids,
                    "limit": limit,
                },
            ).fetchall()

            return [
                {
                    "name": r.name,
                    "industry": r.industry,
                    "employee_count": r.employee_count,
                    "similarity": round(float(r.similarity), 3),
                }
                for r in results
            ]
        except Exception as e:
            logger.warning("vector_search_failed", error=str(e))

    # Fallback: match by industry and employee size range
    similar = (
        db.query(Company)
        .filter(
            Company.id.in_(converted_company_ids),
            Company.industry == company.industry,
        )
        .limit(limit)
        .all()
    )

    return [
        {"name": c.name, "industry": c.industry, "employee_count": c.employee_count}
        for c in similar
    ]


# ── Embedding generation ───────────────────────────────────────

def generate_company_embedding(company: Company, client: OpenAI) -> list[float] | None:
    """Generate embedding for a company profile for similarity search."""
    text_to_embed = " ".join(filter(None, [
        company.name,
        company.industry,
        company.description,
        " ".join(company.technologies[:10] if company.technologies else []),
        company.employee_range,
        company.location_country,
    ]))

    if not text_to_embed.strip():
        return None

    try:
        response = client.embeddings.create(
            model=settings.GEMINI_EMBEDDING_MODEL,
            input=text_to_embed[:2000],  # token limit safety
            dimensions=EMBEDDING_DIMENSIONS,  # truncate 3072 -> 1536 to match Vector(1536)
        )
        return response.data[0].embedding
    except Exception as e:
        logger.warning("embedding_failed", company=company.name, error=str(e))
        return None


# ── Best contact selector ─────────────────────────────────────

def select_best_contact_title(contacts: list[Contact], personas: list[str]) -> str | None:
    """Select the most relevant contact title based on ICP personas."""
    if not contacts:
        return None

    personas_lower = [p.lower() for p in personas]

    # Score contacts by persona match
    scored = []
    for c in contacts:
        title_lower = (c.title or "").lower()
        score = sum(1 for p in personas_lower if p in title_lower)
        # Bonus for primary flag
        if c.is_primary:
            score += 0.5
        scored.append((score, c))

    scored.sort(key=lambda x: x[0], reverse=True)
    return scored[0][1].title if scored else None


# ── Main generator ────────────────────────────────────────────

def generate_feed_item(
    db: Session,
    company: Company,
    icp: ICPConfig,
    workspace_id: str,
    force_refresh: bool = False,
) -> IntelligenceFeedItem | None:
    """
    Generate (or return cached) intelligence feed item for one company.
    Returns None if company doesn't qualify for the feed.
    """
    # Only generate for active companies
    if company.status not in (CompanyStatus.ACTIVE,):
        return None

    if company.composite_score < icp.watch_score_threshold:
        return None

    # Check cache
    if not force_refresh:
        existing = (
            db.query(IntelligenceFeedItem)
            .filter_by(company_id=company.id)
            .filter(IntelligenceFeedItem.expires_at > datetime.now(timezone.utc))
            .filter_by(is_dismissed=False)
            .first()
        )
        if existing:
            return existing

    # Load signals
    signals = (
        db.query(Signal)
        .filter_by(company_id=company.id)
        .order_by(Signal.detected_at.desc())
        .limit(10)
        .all()
    )

    if not signals:
        return None

    # Generate LLM content (with graceful fallback)
    client = _get_gemini_client() if settings.has_gemini else None

    if client:
        # Generate embedding if missing
        if company.embedding is None:
            embedding = generate_company_embedding(company, client)
            if embedding:
                company.embedding = embedding

        signal_summary = generate_signal_summary(company, signals, client)
        recommended_angle = generate_recommended_angle(company, signal_summary, icp, client)
    else:
        # Fallback: rule-based summaries when no Gemini key
        top_signals = sorted(signals, key=lambda s: s.decayed_strength, reverse=True)[:3]
        signal_summary = (
            f"{company.name} is showing {len(signals)} buying signals. "
            f"Top signals: {', '.join(s.title for s in top_signals)}."
        )
        recommended_angle = (
            f"Reach out referencing {top_signals[0].title if top_signals else 'recent activity'}. "
            f"Connect to how {icp.product_name or 'the product'} helps at their stage."
        )

    # Find similar converted companies
    similar = find_similar_converted_companies(db, company, workspace_id)

    # Top signals for the feed (serialized)
    top_signals_data = [
        {
            "type": s.signal_type,
            "title": s.title,
            "detected_at": s.detected_at.isoformat(),
            "strength": round(s.decayed_strength, 3),
        }
        for s in sorted(signals, key=lambda x: x.decayed_strength, reverse=True)[:3]
    ]

    # Contact recommendation
    contacts = db.query(Contact).filter_by(company_id=company.id).all()
    recommended_title = select_best_contact_title(contacts, icp.customer_personas or [])

    now = datetime.now(timezone.utc)

    # Upsert feed item
    feed_item = (
        db.query(IntelligenceFeedItem)
        .filter_by(company_id=company.id)
        .first()
    )

    if feed_item is None:
        feed_item = IntelligenceFeedItem(
            workspace_id=workspace_id,
            company_id=company.id,
        )
        db.add(feed_item)

    feed_item.composite_score = company.composite_score
    feed_item.buying_window = company.buying_window
    feed_item.buying_window_confidence = company.buying_window_confidence
    feed_item.signal_summary = signal_summary
    feed_item.buying_window_reasoning = (
        company.score_snapshot.buying_window_reasoning
        if company.score_snapshot else "Signals indicate buying activity."
    )
    feed_item.recommended_angle = recommended_angle
    feed_item.recommended_contact_title = recommended_title
    feed_item.top_signals = top_signals_data
    feed_item.similar_converted_companies = similar
    feed_item.generated_at = now
    feed_item.expires_at = now + timedelta(hours=CACHE_TTL_HOURS)
    feed_item.is_dismissed = False

    db.flush()
    return feed_item


def run_feed_generation_for_workspace(
    db: Session,
    workspace_id: str,
    force_refresh: bool = False,
) -> dict:
    """
    Generate intelligence feed items for all qualified companies in a workspace.
    Called by nightly batch job.
    """
    from app.models import Workspace
    workspace = db.get(Workspace, workspace_id)
    if not workspace or not workspace.icp_config:
        return {"skipped": True}

    icp = workspace.icp_config

    companies = (
        db.query(Company)
        .filter_by(workspace_id=workspace_id, status=CompanyStatus.ACTIVE)
        .order_by(Company.composite_score.desc())
        .limit(FEED_ITEM_LIMIT)
        .all()
    )

    stats = {"generated": 0, "cached": 0, "skipped": 0, "errors": 0}

    for company in companies:
        try:
            item = generate_feed_item(db, company, icp, workspace_id, force_refresh)
            if item:
                stats["generated"] += 1
            else:
                stats["skipped"] += 1
        except Exception as e:
            logger.error(
                "feed_item_generation_error",
                company=company.name,
                workspace_id=workspace_id,
                error=str(e),
            )
            stats["errors"] += 1

    db.commit()
    logger.info("feed_generation_complete", workspace_id=workspace_id, **stats)
    return stats

