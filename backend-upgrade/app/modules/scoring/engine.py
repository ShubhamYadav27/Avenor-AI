"""
Scoring engine.
Computes composite scores from signals and ICP config.
Pure functions — no database writes except at the top-level run function.
Designed to be swappable: replace score_company() with an ML model later.
"""
import math
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.core.signal_config import (
    DEFAULT_SIGNAL_WEIGHTS,
    SIGNAL_HALF_LIFE_DAYS,
    ICP_MULTIPLIER_FULL,
    ICP_MULTIPLIER_PARTIAL,
    ICP_MULTIPLIER_WEAK,
    BUYING_WINDOW_HOT_THRESHOLD,
    BUYING_WINDOW_WARM_THRESHOLD,
    BUYING_WINDOW_WATCH_THRESHOLD,
    COMBINATION_BONUSES,
)
from app.models import (
    Company, Signal, CompanyScore, SignalWeights,
    ICPConfig, BuyingWindowLabel, CompanyStatus,
)

logger = get_logger(__name__)


# ── ICP Matching ───────────────────────────────────────────────

def compute_icp_match(company: Company, icp: ICPConfig) -> tuple[float, dict]:
    """
    Returns (multiplier, breakdown).
    Checks industry, size, and location against ICP definition.
    """
    checks: dict[str, bool | str] = {}

    # Industry
    company_industry = (company.industry or "").lower()
    icp_industries_lower = [i.lower() for i in (icp.industries or [])]
    checks["industry_match"] = (
        any(ind in company_industry for ind in icp_industries_lower)
        if icp_industries_lower else True  # no filter = all pass
    )

    # Employee count
    count = company.employee_count or 0
    checks["size_match"] = icp.min_employees <= count <= icp.max_employees

    # Location
    company_location = " ".join(filter(None, [
        company.location_city,
        company.location_state,
        company.location_country,
    ])).lower()
    icp_locations_lower = [l.lower() for l in (icp.locations or [])]
    checks["location_match"] = (
        any(loc in company_location for loc in icp_locations_lower)
        if icp_locations_lower else True
    )

    # Technology overlap (bonus, not a gate)
    company_techs = {t.lower() for t in (company.technologies or [])}
    icp_techs_lower = {t.lower() for t in (icp.technologies or [])}
    overlap = company_techs & icp_techs_lower
    checks["tech_overlap"] = list(overlap)
    checks["tech_match"] = len(overlap) > 0

    # Determine multiplier from core 3 criteria
    core_matches = sum([
        checks["industry_match"],
        checks["size_match"],
        checks["location_match"],
    ])

    if core_matches == 3:
        multiplier = ICP_MULTIPLIER_FULL
    elif core_matches == 2:
        multiplier = ICP_MULTIPLIER_PARTIAL
    else:
        multiplier = ICP_MULTIPLIER_WEAK

    # Tech overlap bonus (up to +0.2 on multiplier)
    if checks["tech_match"] and multiplier > ICP_MULTIPLIER_WEAK:
        tech_bonus = min(len(overlap) * 0.05, 0.2)
        multiplier = min(multiplier + tech_bonus, 1.8)

    # Funding stage filter (if specified)
    if icp.funding_stages and company.last_funding_stage:
        stage_match = any(
            s.lower() in company.last_funding_stage.lower()
            for s in icp.funding_stages
        )
        checks["funding_stage_match"] = stage_match
        if not stage_match and icp.funding_stages:
            multiplier *= 0.7  # penalty for wrong stage

    return round(multiplier, 3), checks


# ── Signal Decay ───────────────────────────────────────────────

def apply_decay(signal: Signal, weights: dict[str, float]) -> float:
    """
    Compute decayed signal strength.
    Formula: base_weight × 2^(-days_elapsed / half_life)
    """
    base_weight = weights.get(signal.signal_type, DEFAULT_SIGNAL_WEIGHTS.get(signal.signal_type, 0.05))
    half_life = SIGNAL_HALF_LIFE_DAYS.get(signal.signal_type, 30)

    now = datetime.now(timezone.utc)
    detected = signal.detected_at
    if detected.tzinfo is None:
        detected = detected.replace(tzinfo=timezone.utc)

    days_elapsed = max((now - detected).total_seconds() / 86400, 0)
    decayed = base_weight * math.pow(2.0, -(days_elapsed / half_life))
    return round(decayed, 5)


# ── Combination Bonus ──────────────────────────────────────────

def compute_combination_bonus(signal_types: set[str]) -> float:
    """
    Check if active signal types match known high-value combinations.
    Returns additive bonus to raw signal score.
    """
    bonus = 0.0
    for combo, combo_bonus in COMBINATION_BONUSES.items():
        if combo.issubset(signal_types):
            bonus += combo_bonus
    return round(min(bonus, 0.25), 4)  # cap total bonus at 0.25


# ── Buying Window ──────────────────────────────────────────────

def compute_buying_window(
    composite_score: float,
    signals: list[Signal],
    signal_breakdown: list[dict],
) -> tuple[str, float, str]:
    """
    Returns (window_label, confidence, reasoning).
    Currently heuristic-based; swap for ML model output later.
    """
    # Recency factor: how fresh are the top signals?
    now = datetime.now(timezone.utc)
    recent_signals = [
        s for s in signals
        if (now - (s.detected_at.replace(tzinfo=timezone.utc) if s.detected_at.tzinfo is None else s.detected_at)).days <= 14
    ]
    recency_factor = min(len(recent_signals) / max(len(signals), 1), 1.0)

    # Signal diversity: multiple types = stronger signal
    unique_types = {s.signal_type for s in signals}
    diversity_factor = min(len(unique_types) / 4, 1.0)

    # Composite confidence
    confidence = round((composite_score * 0.6) + (recency_factor * 0.25) + (diversity_factor * 0.15), 3)

    # Label assignment
    if composite_score >= BUYING_WINDOW_HOT_THRESHOLD:
        window = BuyingWindowLabel.HOT
        reasoning = _generate_window_reasoning(window, signals, composite_score)
    elif composite_score >= BUYING_WINDOW_WARM_THRESHOLD:
        window = BuyingWindowLabel.WARM
        reasoning = _generate_window_reasoning(window, signals, composite_score)
    elif composite_score >= BUYING_WINDOW_WATCH_THRESHOLD:
        window = BuyingWindowLabel.WATCH
        reasoning = _generate_window_reasoning(window, signals, composite_score)
    else:
        window = BuyingWindowLabel.COLD
        reasoning = "Insufficient signals to predict an active buying window."

    return window.value, confidence, reasoning


def _generate_window_reasoning(
    window: BuyingWindowLabel,
    signals: list[Signal],
    score: float,
) -> str:
    """Generate plain-English explanation of the buying window prediction."""
    top_signals = sorted(signals, key=lambda s: s.decayed_strength, reverse=True)[:3]
    signal_descriptions = [s.title for s in top_signals]

    window_text = {
        BuyingWindowLabel.HOT: "likely in an active buying cycle right now (0–30 days)",
        BuyingWindowLabel.WARM: "showing strong buying indicators for the next 30–60 days",
        BuyingWindowLabel.WATCH: "worth monitoring — buying signals developing over 60–90 days",
    }.get(window, "no clear buying window detected")

    signals_text = "; ".join(signal_descriptions) if signal_descriptions else "multiple signals"
    return f"This company is {window_text}. Key signals: {signals_text}. Composite score: {score:.2f}."


# ── Core Scorer ────────────────────────────────────────────────

def score_company(
    company: Company,
    signals: list[Signal],
    opportunities: list,
    contacts: list,
    icp: ICPConfig,
    weights: dict[str, float],
) -> dict:
    """
    Computes composite AI score for a company using real CRM Opportunities,
    Contacts, Market Signals, and ICP configuration.
    Returns structured score result dict.
    """
    # 1. Opportunities component (0.0 to 0.45)
    opp_score = 0.0
    opp_reasons = []
    high_stage_opps = [
        o for o in opportunities
        if (getattr(o, "stage", "") or "").lower() in ["value proposition", "negotiation/review", "proposal/price quote", "closed won"]
    ]
    won_opps = [o for o in opportunities if getattr(o, "is_closed_won", False)]
    total_opp_val = sum((getattr(o, "amount_usd", 0) or 0) for o in opportunities)

    if high_stage_opps:
        opp_score += 0.35
        top_opp = high_stage_opps[0]
        val_str = f"${top_opp.amount_usd:,.2f}" if getattr(top_opp, "amount_usd", None) else "unspecified amount"
        opp_reasons.append(f"Active Opportunity '{top_opp.name}' ({val_str}) in stage '{top_opp.stage}'")
    elif opportunities:
        opp_score += 0.20
        opp_reasons.append(f"{len(opportunities)} active opportunity(ies) in pipeline")

    if won_opps:
        opp_score += 0.15
        opp_reasons.append(f"{len(won_opps)} Closed-Won deal(s)")

    if total_opp_val >= 50000:
        opp_score += 0.10
    elif total_opp_val >= 10000:
        opp_score += 0.05

    # 2. Contacts component (0.0 to 0.15)
    contact_score = 0.0
    contact_reasons = []
    if len(contacts) >= 2:
        contact_score = 0.15
        contact_name = getattr(contacts[0], "full_name", None) or getattr(contacts[0], "name", "Contact")
        contact_reasons.append(f"{len(contacts)} decision maker personas linked ({contact_name})")
    elif len(contacts) == 1:
        contact_score = 0.08
        contact_name = getattr(contacts[0], "full_name", None) or getattr(contacts[0], "name", "Contact")
        contact_reasons.append(f"Key contact linked ({contact_name})")

    # 3. ICP match (0.0 to 0.20)
    icp_multiplier, icp_breakdown = compute_icp_match(company, icp)
    icp_score = round(icp_multiplier / ICP_MULTIPLIER_FULL, 4)

    # 4. Signals component (0.0 to 0.35)
    signal_breakdown = []
    total_signal_score = 0.0
    signal_types_active: set[str] = set()

    for sig in signals:
        decayed = apply_decay(sig, weights)
        total_signal_score += decayed
        signal_types_active.add(sig.signal_type)
        signal_breakdown.append({
            "signal_id": str(sig.id),
            "type": sig.signal_type,
            "title": sig.title,
            "base_strength": sig.base_strength,
            "decayed_strength": round(decayed, 4),
            "age_days": max(
                (datetime.now(timezone.utc) - sig.detected_at.replace(
                    tzinfo=timezone.utc if sig.detected_at.tzinfo is None else sig.detected_at.tzinfo
                )).days, 0
            ),
        })

    combo_bonus = compute_combination_bonus(signal_types_active)
    total_signal_score += combo_bonus
    signal_reasons = []
    if signals:
        signal_reasons.append(f"{len(signals)} market buying signal(s) detected")

    # 5. Composite score calculation
    raw_composite = opp_score + contact_score + min(0.35, total_signal_score) + (icp_score * 0.10)
    composite = round(min(0.98, max(0.12, raw_composite)), 2)

    # 6. Buying Window Classification
    if composite >= 0.70:
        buying_window = BuyingWindowLabel.HOT.value
    elif composite >= 0.45:
        buying_window = BuyingWindowLabel.WARM.value
    elif composite >= 0.30:
        buying_window = "evaluating"
    else:
        buying_window = "monitoring"

    # 7. Transparent Reasoning Explanation
    all_reasons = opp_reasons + contact_reasons + signal_reasons
    if all_reasons:
        buying_window_reasoning = f"{buying_window.upper()} WINDOW ({int(composite * 100)}% Match Score): " + " | ".join(all_reasons) + "."
    else:
        buying_window_reasoning = f"MONITORING ONLY ({int(composite * 100)}% Baseline Score): Account synchronized from CRM with no active opportunity pipeline or market intent signals."

    return {
        "company_id": str(company.id),
        "icp_score": icp_score,
        "signal_score": round(total_signal_score, 4),
        "composite_score": composite,
        "icp_multiplier": icp_multiplier,
        "icp_breakdown": icp_breakdown,
        "signal_breakdown": signal_breakdown,
        "buying_window": buying_window,
        "buying_window_confidence": 0.90 if all_reasons else 0.50,
        "buying_window_reasoning": buying_window_reasoning,
        "combination_bonus": combo_bonus,
    }


# ── DB-level run function ─────────────────────────────────────

def run_scoring_for_workspace(db: Session, workspace_id: str) -> dict:
    """
    Score all companies in a workspace.
    Reads signals, loads workspace weights, updates company and score tables.
    """
    from app.models import Workspace
    from app.crm.routes import ensure_workspace_icp_config

    workspace = db.get(Workspace, workspace_id)
    if not workspace:
        return {"skipped": True, "reason": "no_workspace"}

    if not workspace.icp_config:
        ensure_workspace_icp_config(db, workspace_id)
        db.refresh(workspace)

    icp = workspace.icp_config

    # Load workspace-specific weights (fall back to defaults)
    sw = workspace.signal_weights
    weights = sw.weights if sw and sw.weights else DEFAULT_SIGNAL_WEIGHTS

    companies = (
        db.query(Company)
        .filter_by(workspace_id=workspace_id)
        .all()
    )

    stats = {
        "scored": 0,
        "active": 0,
        "watch": 0,
        "disqualified": 0,
    }

    now = datetime.now(timezone.utc)

    from app.models import Opportunity, Contact

    for company in companies:
        signals = (
            db.query(Signal)
            .filter_by(company_id=company.id)
            .all()
        )
        opportunities = (
            db.query(Opportunity)
            .filter_by(company_id=company.id)
            .all()
        )
        if not opportunities and company.external_id:
            opportunities = (
                db.query(Opportunity)
                .filter_by(workspace_id=workspace_id, external_account_id=company.external_id)
                .all()
            )
        contacts = (
            db.query(Contact)
            .filter_by(company_id=company.id)
            .all()
        )

        result = score_company(company, signals, opportunities, contacts, icp, weights)

        # Update decayed strengths in Signal rows
        signal_map = {str(s.id): s for s in signals}
        for sb in result["signal_breakdown"]:
            sig = signal_map.get(sb["signal_id"])
            if sig:
                sig.decayed_strength = sb["decayed_strength"]

        # Update company
        company.icp_score = result["icp_score"]
        company.signal_score = result["signal_score"]
        company.composite_score = result["composite_score"]
        company.buying_window = result["buying_window"]
        company.buying_window_confidence = result["buying_window_confidence"]
        company.last_scored_at = now

        # Update status — synced CRM accounts stay Active in pipeline
        company.status = CompanyStatus.ACTIVE
        stats["active"] += 1


        # Upsert CompanyScore snapshot
        score_row = company.score_snapshot
        if score_row is None:
            score_row = CompanyScore(company_id=company.id)
            db.add(score_row)

        score_row.icp_score = result["icp_score"]
        score_row.signal_score = result["signal_score"]
        score_row.composite_score = result["composite_score"]
        score_row.icp_breakdown = result["icp_breakdown"]
        score_row.signal_breakdown = result["signal_breakdown"]
        score_row.buying_window = result["buying_window"]
        score_row.buying_window_confidence = result["buying_window_confidence"]
        score_row.buying_window_reasoning = result["buying_window_reasoning"]
        score_row.scored_at = now

        stats["scored"] += 1

    db.commit()
    logger.info("scoring_complete", workspace_id=workspace_id, **stats)
    return stats


def initialize_workspace_weights(db: Session, workspace_id: str) -> SignalWeights:
    """Create default signal weights for a new workspace."""
    from app.models import Workspace
    workspace = db.get(Workspace, workspace_id)

    existing = workspace.signal_weights if workspace else None
    if existing:
        return existing

    sw = SignalWeights(
        workspace_id=workspace_id,
        weights={k: v for k, v in DEFAULT_SIGNAL_WEIGHTS.items()},
        training_sample_size=0,
    )
    db.add(sw)
    db.commit()
    db.refresh(sw)
    return sw
