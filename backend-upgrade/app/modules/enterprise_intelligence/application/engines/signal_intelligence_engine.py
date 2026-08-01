import logging
from typing import Optional, List
from uuid import UUID
from datetime import datetime, timezone

from app.modules.enterprise_intelligence.domain.signal_intelligence import SignalIntelligence, NormalizedSignal
from app.modules.enterprise_intelligence.domain.repositories import SignalIntelligenceRepository, SignalProvider

logger = logging.getLogger(__name__)

class SignalIntelligenceEngine:
    """
    Core Application Service for the Global Signal Intelligence Engine (Phase 7, Engine 11).
    Orchestrates data enrichment from Layer 2 (Public), Layer 3 (Licensed Providers),
    and applies Layer 4 (Proprietary AI) intelligence for signal fusion and correlation.
    """
    def __init__(
        self,
        repository: SignalIntelligenceRepository,
        provider: SignalProvider
    ):
        self.repository = repository
        self.provider = provider
        
    async def process_signals(
        self, 
        tenant_id: UUID, 
        company_id: UUID, 
        company_domain: str,
        incoming_signals: Optional[List[NormalizedSignal]] = None
    ) -> SignalIntelligence:
        """
        Retrieves, merges, and correlates signals for a specific company.
        """
        existing = await self.repository.get_by_company_id(tenant_id, company_id)
        return await self._run_processing_pipeline(tenant_id, company_id, company_domain, existing, incoming_signals)
        
    async def _run_processing_pipeline(
        self, 
        tenant_id: UUID, 
        company_id: UUID, 
        company_domain: str,
        existing: Optional[SignalIntelligence] = None,
        incoming_signals: Optional[List[NormalizedSignal]] = None
    ) -> SignalIntelligence:
        logger.info(f"Starting Global Signal processing for {company_domain} (tenant: {tenant_id})")
        
        intelligence = existing or SignalIntelligence(
            tenant_id=tenant_id, 
            company_id=company_id,
            company_domain=company_domain
        )
        intelligence.processing_status = "processing"
        
        try:
            signals_to_process = incoming_signals or []
            
            # Fetch external signals if no incoming stream was provided
            if not signals_to_process:
                external_signals = await self.provider.fetch_signals(company_domain)
                signals_to_process.extend(external_signals)
            
            # Deduplicate and append new signals
            existing_ids = {s.id for s in intelligence.active_signals}
            for s in signals_to_process:
                if s.id not in existing_ids:
                    intelligence.active_signals.append(s)
            
            # Move expired signals to historical
            now = datetime.now(timezone.utc)
            still_active = []
            for s in intelligence.active_signals:
                if s.expires_at and s.expires_at < now:
                    s.is_active = False
                    intelligence.historical_signals.append(s)
                else:
                    still_active.append(s)
            intelligence.active_signals = still_active
            
            # Invoke Layer 4 (Proprietary AI Models) for Correlation and Scoring
            intelligence = await self._apply_proprietary_ai(intelligence)
            
            intelligence.processing_status = "processed"
            intelligence.last_processed_at = datetime.now(timezone.utc)
            
            return await self.repository.save(intelligence)
            
        except Exception as e:
            logger.error(f"Failed to process signals for {company_domain}: {str(e)}")
            intelligence.processing_status = "failed"
            await self.repository.save(intelligence)
            raise

    async def _apply_proprietary_ai(self, intelligence: SignalIntelligence) -> SignalIntelligence:
        """
        Layer 4: Avenor's Proprietary AI models applied to normalized signals.
        Generates correlated events, buying window scores, and strategic prioritization.
        """
        active = intelligence.active_signals
        
        if not active:
            intelligence.composite_buying_window_score = 0.1
            intelligence.risk_indicator_score = 0.1
            intelligence.growth_indicator_score = 0.1
            intelligence.ai_generated_summary = "No active signals detected."
            intelligence.strategic_prioritization_tier = 3
            return intelligence
            
        # Segment signals
        buying_signals = [s for s in active if s.signal_type == "buying"]
        risk_signals = [s for s in active if s.signal_type == "risk"]
        growth_signals = [s for s in active if s.signal_type in ("growth", "funding", "hiring")]
        
        # Calculate impact-weighted scores
        def calc_score(sigs):
            return min(1.0, sum(s.impact_score * s.confidence_score for s in sigs) / max(1, len(sigs)) + (len(sigs) * 0.1))
            
        intelligence.composite_buying_window_score = calc_score(buying_signals)
        intelligence.risk_indicator_score = calc_score(risk_signals)
        intelligence.growth_indicator_score = calc_score(growth_signals)
        
        # Mock Correlation Logic
        if len(buying_signals) > 0 and len(growth_signals) > 0:
            intelligence.correlated_events = [
                {
                    "event_name": "High-intent Expansion Window",
                    "signals": [s.id for s in buying_signals + growth_signals],
                    "insight": "Company is showing direct buying intent alongside growth markers (e.g. hiring, funding)."
                }
            ]
            
        # Strategic Prioritization Tier
        if intelligence.composite_buying_window_score > 0.7:
            intelligence.strategic_prioritization_tier = 1
            intelligence.ai_generated_summary = f"High priority account. {len(active)} active signals detected pointing to immediate buying window."
            intelligence.ai_explanations = [
                "Multiple high-impact buying signals detected.",
                "Growth indicators corroborate budget availability."
            ]
        elif intelligence.growth_indicator_score > 0.5:
            intelligence.strategic_prioritization_tier = 2
            intelligence.ai_generated_summary = f"Monitoring account. Strong growth signals detected but direct buying intent is moderate."
            intelligence.ai_explanations = ["Account is expanding but has not yet initiated active vendor evaluation."]
        else:
            intelligence.strategic_prioritization_tier = 3
            intelligence.ai_generated_summary = f"Low priority. Monitor for future signal spikes."
            intelligence.ai_explanations = ["Insufficient signal volume to trigger active outreach."]
            
        return intelligence
