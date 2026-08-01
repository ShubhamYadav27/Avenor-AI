import logging
from typing import Optional
from uuid import UUID
from datetime import datetime, timezone

from app.modules.enterprise_intelligence.domain.industry_intelligence import IndustryIntelligence
from app.modules.enterprise_intelligence.domain.repositories import IndustryIntelligenceRepository, IndustryIntelligenceProvider

logger = logging.getLogger(__name__)

class IndustryIntelligenceEngine:
    """
    Core Application Service for the Industry Intelligence Engine (Phase 7, Engine 10).
    Orchestrates data enrichment from Layer 2 (Public), Layer 3 (Licensed Providers),
    and applies Layer 4 (Proprietary AI) intelligence for deep industry analysis.
    """
    def __init__(
        self,
        repository: IndustryIntelligenceRepository,
        provider: IndustryIntelligenceProvider
    ):
        self.repository = repository
        self.provider = provider
        
    async def get_or_enrich_industry(
        self, 
        tenant_id: UUID, 
        industry_name: str,
        force_refresh: bool = False
    ) -> IndustryIntelligence:
        """
        Retrieves deep intelligence for a specific industry.
        """
        existing = await self.repository.get_by_industry(tenant_id, industry_name)
        
        if existing and not force_refresh:
            if existing.last_enriched_at:
                days_old = (datetime.now(timezone.utc) - existing.last_enriched_at).days
                if days_old < 30: # Industry benchmarks move slower (monthly refresh)
                    return existing
                    
        return await self._run_enrichment_pipeline(tenant_id, industry_name, existing)
        
    async def _run_enrichment_pipeline(
        self, 
        tenant_id: UUID, 
        industry_name: str, 
        existing: Optional[IndustryIntelligence] = None
    ) -> IndustryIntelligence:
        logger.info(f"Starting Industry Intelligence enrichment for {industry_name} (tenant: {tenant_id})")
        
        intelligence = existing or IndustryIntelligence(
            tenant_id=tenant_id, 
            industry_name=industry_name
        )
        intelligence.enrichment_status = "enriching"
        
        try:
            # 1. Fetch external industry data (Layer 2 & 3 via Provider Abstraction)
            external_data = await self.provider.fetch_industry_data(industry_name)
            
            intelligence.lifecycle_stage = external_data.lifecycle_stage
            intelligence.market_size_estimate = external_data.market_size_estimate
            intelligence.growth_rate = external_data.growth_rate
            intelligence.average_sales_cycle_days = external_data.average_sales_cycle_days
            intelligence.average_deal_size = external_data.average_deal_size
            intelligence.kpis = external_data.kpis
            intelligence.regulatory_environment = external_data.regulatory_environment
            intelligence.key_challenges = external_data.key_challenges
            intelligence.key_opportunities = external_data.key_opportunities
            
            # 2. Invoke Layer 4 (Proprietary AI Models)
            intelligence = await self._apply_proprietary_ai(intelligence)
            
            intelligence.enrichment_status = "enriched"
            intelligence.last_enriched_at = datetime.now(timezone.utc)
            
            return await self.repository.save(intelligence)
            
        except Exception as e:
            logger.error(f"Failed to enrich industry data for {industry_name}: {str(e)}")
            intelligence.enrichment_status = "failed"
            await self.repository.save(intelligence)
            raise

    async def _apply_proprietary_ai(self, intelligence: IndustryIntelligence) -> IndustryIntelligence:
        """
        Layer 4: Avenor's Proprietary AI models applied to industry data.
        Generates maturity, transformation, and readiness scores.
        """
        # Calculate Maturity Score based on lifecycle
        stage_map = {"emerging": 0.2, "growth": 0.6, "mature": 0.9, "declining": 1.0}
        intelligence.industry_maturity_score = stage_map.get(intelligence.lifecycle_stage.lower(), 0.5)
        
        # Calculate Digital Transformation Score based on tech industry vs legacy
        high_tech_industries = ["saas", "cybersecurity", "fintech", "telecommunications"]
        lagging_industries = ["manufacturing", "logistics", "government", "real estate"]
        
        if intelligence.industry_name.lower() in high_tech_industries:
            intelligence.digital_transformation_score = 0.9
            intelligence.opportunity_score = 0.8
            intelligence.buying_patterns = ["Consensus-based", "High technical evaluation", "Self-serve trials"]
            intelligence.best_practices = ["Lead with technical differentiation", "Multi-thread with Engineering & RevOps"]
        elif intelligence.industry_name.lower() in lagging_industries:
            intelligence.digital_transformation_score = 0.4
            intelligence.opportunity_score = 0.9  # High opportunity for digitization
            intelligence.buying_patterns = ["Relationship-driven", "Long procurement cycles", "RFP heavy"]
            intelligence.best_practices = ["Focus on ROI and cost-reduction", "Engage C-level executives directly"]
        else:
            intelligence.digital_transformation_score = 0.6
            intelligence.opportunity_score = 0.6
            intelligence.buying_patterns = ["Standard enterprise sales cycle"]
            intelligence.best_practices = ["Standard multi-threading"]
            
        # Risk score based on regulation
        reg_map = {"high": 0.8, "medium": 0.4, "low": 0.1}
        intelligence.risk_score = reg_map.get(intelligence.regulatory_environment.lower(), 0.5)
        
        # Readiness score balances opportunity, transformation maturity, and risk
        readiness = (intelligence.opportunity_score * 0.5) + (intelligence.digital_transformation_score * 0.3) - (intelligence.risk_score * 0.2)
        intelligence.readiness_score = max(0.1, min(1.0, readiness))
        
        if intelligence.readiness_score > 0.7:
            intelligence.strategic_recommendations = f"High readiness in {intelligence.industry_name}. Allocate Tier 1 GTM resources. Pitch digital transformation."
        else:
            intelligence.strategic_recommendations = f"Moderate/Low readiness in {intelligence.industry_name}. Proceed with targeted account-based marketing."
            
        intelligence.ai_summary = f"Industry: {intelligence.industry_name} is in a {intelligence.lifecycle_stage} stage. Readiness score is {intelligence.readiness_score*100:.0f}%. Key challenge: {intelligence.key_challenges[0] if intelligence.key_challenges else 'Unknown'}."
        
        return intelligence
