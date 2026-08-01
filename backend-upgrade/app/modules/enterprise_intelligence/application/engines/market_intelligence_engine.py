import logging
from typing import Optional
from uuid import UUID
from datetime import datetime, timezone

from app.modules.enterprise_intelligence.domain.market_intelligence import MarketIntelligence
from app.modules.enterprise_intelligence.domain.repositories import MarketIntelligenceRepository, MarketIntelligenceProvider

logger = logging.getLogger(__name__)

class MarketIntelligenceEngine:
    """
    Core Application Service for the Market Intelligence Engine (Phase 7, Engine 9).
    Orchestrates data enrichment from Layer 2 (Public), Layer 3 (Licensed Providers),
    and applies Layer 4 (Proprietary AI) intelligence for market analysis.
    """
    def __init__(
        self,
        repository: MarketIntelligenceRepository,
        provider: MarketIntelligenceProvider
    ):
        self.repository = repository
        self.provider = provider
        
    async def get_or_enrich_market(
        self, 
        tenant_id: UUID, 
        company_id: UUID, 
        company_domain: str,
        industry: str,
        force_refresh: bool = False
    ) -> MarketIntelligence:
        """
        Retrieves market intelligence for a given company.
        """
        existing = await self.repository.get_by_company_id(tenant_id, company_id)
        
        if existing and not force_refresh:
            if existing.last_enriched_at:
                days_old = (datetime.now(timezone.utc) - existing.last_enriched_at).days
                if days_old < 30: # Market trends move slower (monthly refresh)
                    return existing
                    
        return await self._run_enrichment_pipeline(tenant_id, company_id, company_domain, industry, existing)
        
    async def _run_enrichment_pipeline(
        self, 
        tenant_id: UUID, 
        company_id: UUID, 
        company_domain: str, 
        industry: str,
        existing: Optional[MarketIntelligence] = None
    ) -> MarketIntelligence:
        logger.info(f"Starting Market Intelligence enrichment for {company_domain} (Industry: {industry}, tenant: {tenant_id})")
        
        intelligence = existing or MarketIntelligence(
            tenant_id=tenant_id, 
            company_id=company_id, 
            company_domain=company_domain,
            industry=industry
        )
        intelligence.enrichment_status = "enriching"
        
        try:
            # 1. Fetch external market data (Layer 2 & 3 via Provider Abstraction)
            external_data = await self.provider.fetch_market_data(industry)
            
            intelligence.market_trends = external_data.market_trends
            intelligence.macro_economic_indicators = external_data.macro_economic_indicators
            intelligence.regulatory_changes = external_data.regulatory_changes
            
            # 2. Invoke Layer 4 (Proprietary AI Models)
            intelligence = await self._apply_proprietary_ai(intelligence)
            
            intelligence.enrichment_status = "enriched"
            intelligence.last_enriched_at = datetime.now(timezone.utc)
            
            return await self.repository.save(intelligence)
            
        except Exception as e:
            logger.error(f"Failed to enrich market data for {company_domain}: {str(e)}")
            intelligence.enrichment_status = "failed"
            await self.repository.save(intelligence)
            raise

    async def _apply_proprietary_ai(self, intelligence: MarketIntelligence) -> MarketIntelligence:
        """
        Layer 4: Avenor's Proprietary AI models applied to market data.
        Generates risk scores, opportunity scores, and strategic macro positioning.
        """
        trends = intelligence.market_trends
        
        if not trends:
            intelligence.market_risk_score = 0.5
            intelligence.opportunity_score = 0.5
            intelligence.market_sentiment = "neutral"
            intelligence.ai_summary = "Insufficient market data for robust analysis."
            return intelligence
            
        positive_trends = [t for t in trends if t.impact == "positive"]
        negative_trends = [t for t in trends if t.impact == "negative"]
        
        # Calculate scores
        pos_ratio = len(positive_trends) / len(trends)
        neg_ratio = len(negative_trends) / len(trends)
        
        intelligence.opportunity_score = min(1.0, pos_ratio + 0.1)
        intelligence.market_risk_score = min(1.0, neg_ratio + (0.2 if len(intelligence.regulatory_changes) > 0 else 0))
        
        if intelligence.opportunity_score > 0.6 and intelligence.market_risk_score < 0.4:
            intelligence.market_sentiment = "bullish"
            intelligence.strategic_market_recommendations = f"Aggressively target the {intelligence.industry} vertical. Strong macro tailwinds."
        elif intelligence.market_risk_score > 0.6:
            intelligence.market_sentiment = "bearish"
            intelligence.strategic_market_recommendations = f"Exercise caution in {intelligence.industry}. Lead with cost-reduction and efficiency ROI."
        else:
            intelligence.market_sentiment = "neutral"
            intelligence.strategic_market_recommendations = "Focus on niche pain points that bypass general macro stagnation."
            
        # Detect expansions
        if intelligence.market_sentiment == "bullish":
            intelligence.expansion_opportunities = ["Upsell existing accounts", "Expand total addressable market targeting"]
            
        # Mock seasonal pattern logic
        if intelligence.industry.lower() in ["retail", "ecommerce"]:
            intelligence.seasonal_buying_patterns = ["Q3 planning for Q4 holiday scale-up"]
        elif intelligence.industry.lower() in ["software", "saas"]:
            intelligence.seasonal_buying_patterns = ["Q4 budget flush", "Q1 strategic kickoffs"]
            
        intelligence.ai_summary = f"Analyzed {len(trends)} macro trends in the {intelligence.industry} sector. Sentiment is {intelligence.market_sentiment} with a risk score of {intelligence.market_risk_score*100:.0f}%."
        
        return intelligence
