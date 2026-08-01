import logging
from typing import Optional
from uuid import UUID
from datetime import datetime, timezone

from app.modules.enterprise_intelligence.domain.funding_intelligence import FundingIntelligence
from app.modules.enterprise_intelligence.domain.repositories import FundingIntelligenceRepository, FundingIntelligenceProvider

logger = logging.getLogger(__name__)

class FundingIntelligenceEngine:
    """
    Core Application Service for the Funding Intelligence Engine (Phase 7, Engine 5).
    Orchestrates data enrichment from Layer 2 (Public), Layer 3 (Licensed Providers),
    and applies Layer 4 (Proprietary AI) intelligence for funding and growth analysis.
    """
    def __init__(
        self,
        repository: FundingIntelligenceRepository,
        provider: FundingIntelligenceProvider
    ):
        self.repository = repository
        self.provider = provider
        
    async def get_or_enrich_funding(
        self, 
        tenant_id: UUID, 
        company_id: UUID, 
        company_domain: str, 
        force_refresh: bool = False
    ) -> FundingIntelligence:
        """
        Retrieves funding intelligence for a given company.
        """
        existing = await self.repository.get_by_company_id(tenant_id, company_id)
        
        if existing and not force_refresh:
            if existing.last_enriched_at:
                days_old = (datetime.now(timezone.utc) - existing.last_enriched_at).days
                if days_old < 30: # Funding rounds occur infrequently
                    return existing
                    
        return await self._run_enrichment_pipeline(tenant_id, company_id, company_domain, existing)
        
    async def _run_enrichment_pipeline(
        self, 
        tenant_id: UUID, 
        company_id: UUID, 
        company_domain: str, 
        existing: Optional[FundingIntelligence] = None
    ) -> FundingIntelligence:
        logger.info(f"Starting Funding Intelligence enrichment for {company_domain} (tenant: {tenant_id})")
        
        intelligence = existing or FundingIntelligence(tenant_id=tenant_id, company_id=company_id, company_domain=company_domain)
        intelligence.enrichment_status = "enriching"
        
        try:
            # 1. Fetch external funding data (Layer 2 & 3 via Provider Abstraction)
            external_data = await self.provider.fetch_funding_data(company_domain)
            
            intelligence.total_funding = external_data.total_funding
            intelligence.funding_rounds = external_data.funding_rounds
            intelligence.last_funding_date = external_data.last_funding_date
            
            # 2. Invoke Layer 4 (Proprietary AI Models)
            intelligence = await self._apply_proprietary_ai(intelligence)
            
            intelligence.enrichment_status = "enriched"
            intelligence.last_enriched_at = datetime.now(timezone.utc)
            
            return await self.repository.save(intelligence)
            
        except Exception as e:
            logger.error(f"Failed to enrich funding for {company_domain}: {str(e)}")
            intelligence.enrichment_status = "failed"
            await self.repository.save(intelligence)
            raise

    async def _apply_proprietary_ai(self, intelligence: FundingIntelligence) -> FundingIntelligence:
        """
        Layer 4: Avenor's Proprietary AI models applied to funding history.
        Generates expansion probabilities and buying window insights.
        """
        rounds = intelligence.funding_rounds
        total = intelligence.total_funding
        
        if not rounds:
            intelligence.capital_growth_trend = "stable"
            intelligence.revenue_expansion_probability = 0.2
            intelligence.hiring_probability = 0.2
            intelligence.buying_window_impact = "low"
            intelligence.ai_summary = "No major recent funding events detected. Organic growth expected."
            return intelligence
            
        # Mock ML derivations
        latest_round = sorted(rounds, key=lambda x: x.date_announced, reverse=True)[0]
        days_since_funding = (datetime.now(timezone.utc) - latest_round.date_announced).days
        
        intelligence.capital_growth_trend = "accelerating" if total > 10_000_000 else "stable"
        
        if days_since_funding < 180: # Strong buying window in first 6 months post-funding
            intelligence.buying_window_impact = "high"
            intelligence.revenue_expansion_probability = 0.85
            intelligence.hiring_probability = 0.90
            intelligence.technology_investment_probability = 0.85
            intelligence.sales_readiness_score = 0.95
            intelligence.growth_opportunity_detection = f"Recent {latest_round.round_type} indicates strong imminent budget expansion."
            intelligence.ai_summary = f"Company recently secured {latest_round.round_type} funding. High probability of technology and headcount expansion in the next 6 months."
        else:
            intelligence.buying_window_impact = "medium"
            intelligence.revenue_expansion_probability = 0.60
            intelligence.hiring_probability = 0.60
            intelligence.technology_investment_probability = 0.50
            intelligence.sales_readiness_score = 0.65
            intelligence.growth_opportunity_detection = "Budget may be stabilizing post-funding scale-up."
            intelligence.ai_summary = f"Last funding was {days_since_funding} days ago. Expected to be in a steady execution phase."
            
        return intelligence
