"""
Signal scoring engine.
Computes composite score = Σ(signal_decayed) × ICP_multiplier.
Pure rule-based for MVP. Swap in ML model later by replacing score_company().
"""
import math
import logging
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.config import settings
from app.models import Company, Signal, SignalType, LeadStatus

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────
# Signal base weights (tune these over time)
# ─────────────────────────────────────────────

SIGNAL_WEIGHTS = {
    SignalType.FUNDING: 0.35,
    SignalType.HIRING: 0.25,
    SignalType.TECH_CHANGE: 0.20,
    SignalType.INTENT: 0.15,
    SignalType.EXPANSION: 0.05,
}

# Decay half-life in days (signal loses 50% value after this many days)
SIGNAL_HALF_LIFE_DAYS = {
    SignalType.FUNDING: 90,     # funding stays relevant longer
    SignalType.HIRING: 30,      # job posts go stale faster
    SignalType.TECH_CHANGE: 60,
    SignalType.INTENT: 14,      # intent surges decay fast
    SignalType.EXPANSION: 45,
}

# ICP match multipliers
ICP_MULTIPLIER_FULL = 1.5     # all criteria match
ICP_MULTIPLIER_PARTIAL = 1.0  # some criteria match
ICP_MULTIPLIER_NONE = 0.3     # no criteria match (still track, don't prioritize)

# Scoring thresholds
SCORE_ACTIVE = 0.60       # above this → active outreach queue
SCORE_NURTURE = 0.30      # above this → nurture watch list
# below SCORE_NURTURE → archive


# ─────────────────────────────────────────────
# ICP Matching
# ─────────────────────────────────────────────

def compute_icp_score(company: Company) -> tuple[float, dict]:
    """
    Returns (multiplier, breakdown_dict).
    Checks industry, employee count, and location against ICP config.
    """
    checks = {}

    # Industry check
    icp_industries = [i.lower() for i in settings.icp_industries_list]
    company_industry = (company.industry or "").lower()
    checks["industry_match"] = any(ind in company_industry for ind in icp_industries)

    # Employee count check
    employee_count = company.employee_count or 0
    checks["size_match"] = (
        settings.ICP_MIN_EMPLOYEES <= employee_count <= settings.ICP_MAX_EMPLOYEES
    )

    # Location check
    icp_locations = [l.lower() for l in settings.icp_locations_list]
    company_location = (company.location or "").lower()
    checks["location_match"] = any(loc in company_location for loc in icp_locations)

    # Funding presence (bonus)
    checks["has_funding"] = company.funding_total is not None and company.funding_total > 0

    # Score
    core_matches = sum([checks["industry_match"], checks["size_match"], checks["location_match"]])

    if core_matches == 3:
        multiplier = ICP_MULTIPLIER_FULL
    elif core_matches >= 2:
        multiplier = ICP_MULTIPLIER_PARTIAL
    else:
        multiplier = ICP_MULTIPLIER_NONE

    # Funding bonus
    if checks["has_funding"] and multiplier > ICP_MULTIPLIER_NONE:
        multiplier = min(multiplier * 1.1, 1.8)  # cap at 1.8

    return multiplier, checks


# ─────────────────────────────────────────────
# Signal Decay
# ─────────────────────────────────────────────

def apply_recency_decay(signal: Signal) -> float:
    """
    Exponential decay: score = base_weight × 2^(-days / half_life)
    Returns decayed score (0.0 – base_weight).
    """
    base_weight = SIGNAL_WEIGHTS.get(signal.signal_type, 0.10)
    half_life = SIGNAL_HALF_LIFE_DAYS.get(signal.signal_type, 30)

    now = datetime.now(timezone.utc)
    detected = signal.detected_at
    if detected.tzinfo is None:
        detected = detected.replace(tzinfo=timezone.utc)

    days_elapsed = (now - detected).days
    decayed = base_weight * math.pow(2, -(days_elapsed / half_life))
    return round(decayed, 4)


# ─────────────────────────────────────────────
# Core Scorer
# ─────────────────────────────────────────────

def score_company(db: Session, company: Company) -> dict:
    """
    Score a single company.
    Returns scoring breakdown and updates company record.
    """
    signals = db.query(Signal).filter_by(company_id=company.id).all()

    # Step 1: Compute decayed signal scores
    signal_scores = []
    signal_breakdown = []
    for sig in signals:
        decayed = apply_recency_decay(sig)
        sig.decayed_score = decayed
        signal_scores.append(decayed)
        signal_breakdown.append({
            "type": sig.signal_type.value,
            "raw_value": sig.raw_value,
            "base_weight": SIGNAL_WEIGHTS.get(sig.signal_type, 0.10),
            "decayed_score": decayed,
            "age_days": (datetime.now(timezone.utc) - sig.detected_at.replace(tzinfo=timezone.utc)).days,
        })

    raw_signal_score = sum(signal_scores)

    # Step 2: ICP multiplier
    icp_multiplier, icp_checks = compute_icp_score(company)

    # Step 3: Composite score (cap at 1.0)
    composite = min(raw_signal_score * icp_multiplier, 1.0)

    # Step 4: Update company record
    company.signal_score = round(raw_signal_score, 4)
    company.icp_score = round(icp_multiplier / ICP_MULTIPLIER_FULL, 4)
    company.composite_score = round(composite, 4)

    if composite >= SCORE_ACTIVE:
        company.status = LeadStatus.QUEUED
    elif composite >= SCORE_NURTURE:
        company.status = LeadStatus.SCORED  # nurture
    else:
        company.status = LeadStatus.DISQUALIFIED

    db.commit()

    result = {
        "company_id": str(company.id),
        "company_name": company.name,
        "raw_signal_score": round(raw_signal_score, 4),
        "icp_multiplier": round(icp_multiplier, 2),
        "icp_checks": icp_checks,
        "composite_score": round(composite, 4),
        "status": company.status.value,
        "signals": signal_breakdown,
        "priority": _priority_label(composite),
    }

    logger.info(
        f"Scored {company.name}: composite={composite:.3f} → {company.status.value}"
    )
    return result


def score_all_unscored(db: Session) -> list[dict]:
    """Score every company that's been enriched but not yet queued."""
    companies = db.query(Company).filter(
        Company.status.in_([LeadStatus.NEW, LeadStatus.ENRICHED, LeadStatus.SCORED])
    ).all()

    results = []
    for company in companies:
        try:
            result = score_company(db, company)
            results.append(result)
        except Exception as e:
            logger.error(f"Scoring failed for {company.name}: {e}")

    # Sort by composite score descending
    results.sort(key=lambda x: x["composite_score"], reverse=True)
    return results


def get_top_leads(db: Session, limit: int = 20) -> list[Company]:
    """Return top-scored companies ready for outreach."""
    return (
        db.query(Company)
        .filter(Company.status == LeadStatus.QUEUED)
        .order_by(Company.composite_score.desc())
        .limit(limit)
        .all()
    )


# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────

def _priority_label(score: float) -> str:
    if score >= 0.80:
        return "🔴 HIGH"
    elif score >= 0.60:
        return "🟡 MEDIUM"
    elif score >= 0.30:
        return "⚪ NURTURE"
    else:
        return "⛔ DISQUALIFIED"
