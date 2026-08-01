import logging
from typing import Optional
from uuid import UUID
from datetime import datetime, timezone

from app.modules.enterprise_intelligence.domain.competitive_intelligence import CompetitiveIntelligence
from app.modules.enterprise_intelligence.domain.repositories import CompetitiveIntelligenceRepository, CompetitiveIntelligenceProvider

logger = logging.getLogger(__name__)

class CompetitiveIntelligenceEngine:
    """
    Core Application Service for the Competitive Intelligence Engine (Phase 7, Engine 8).
    Orchestrates data enrichment from Layer 2 (Public), Layer 3 (Licensed Providers),
    and applies Layer 4 (Proprietary AI) intelligence for competitive analysis.
    """
    def __init__(
        self,
        repository: CompetitiveIntelligenceRepository,
        provider: CompetitiveIntelligenceProvider
    ):
        self.repository = repository
        self.provider = provider
        
    async def get_or_enrich_competitive(
        self, 
        tenant_id: UUID, 
        company_id: UUID, 
        company_domain: str, 
        force_refresh: bool = False
    ) -> CompetitiveIntelligence:
        """
        Retrieves competitive intelligence for a given company.
        """
        existing = await self.repository.get_by_company_id(tenant_id, company_id)
        
        if existing and not force_refresh:
            if existing.last_enriched_at:
                days_old = (datetime.now(timezone.utc) - existing.last_enriched_at).days
                if days_old < 14: # Competitive landscape changes at a medium pace
                    return existing
                    
        return await self._run_enrichment_pipeline(tenant_id, company_id, company_domain, existing)
        
    async def _run_enrichment_pipeline(
        self, 
        tenant_id: UUID, 
        company_id: UUID, 
        company_domain: str, 
        existing: Optional[CompetitiveIntelligence] = None
    ) -> CompetitiveIntelligence:
        logger.info(f"Starting Competitive Intelligence enrichment for {company_domain} (tenant: {tenant_id})")
        
        intelligence = existing or CompetitiveIntelligence(tenant_id=tenant_id, company_id=company_id, company_domain=company_domain)
        intelligence.enrichment_status = "enriching"
        
        try:
            # 1. Fetch external competitive data (Layer 2 & 3 via Provider Abstraction)
            external_data = await self.provider.fetch_competitive_data(company_domain)
            
            intelligence.competitors = external_data.competitors
            
            # 2. Invoke Layer 4 (Proprietary AI Models)
            intelligence = await self._apply_proprietary_ai(intelligence)
            
            intelligence.enrichment_status = "enriched"
            intelligence.last_enriched_at = datetime.now(timezone.utc)
            
            return await self.repository.save(intelligence)
            
        except Exception as e:
            logger.error(f"Failed to enrich competitive data for {company_domain}: {str(e)}")
            intelligence.enrichment_status = "failed"
            await self.repository.save(intelligence)
            raise

    async def _apply_proprietary_ai(self, intelligence: CompetitiveIntelligence) -> CompetitiveIntelligence:
        """
        Layer 4: Avenor's Proprietary AI models applied to competitive data.
        Generates risk scores, displacement opportunities, and positioning recommendations.
        """
        competitors = intelligence.competitors
        
        if not competitors:
            intelligence.competitive_risk_score = 0.1
            intelligence.ai_summary = "No major competitors detected in this segment. High first-mover advantage opportunity."
            intelligence.recommended_positioning = "Focus on market creation and educating the buyer on the core problem."
            return intelligence
            
        direct_competitors = [c for c in competitors if c.is_direct]
        leaders = [c for c in competitors if c.market_position == "leader"]
        
        # Calculate risk score based on density of direct leaders
        base_risk = len(direct_competitors) * 0.1
        leader_penalty = len(leaders) * 0.2
        intelligence.competitive_risk_score = min(1.0, base_risk + leader_penalty)
        
        # Determine displacement and feature gaps
        opportunities = []
        gaps = []
        
        for comp in competitors:
            if comp.market_position == "leader":
                opportunities.append(f"Displace {comp.name} by highlighting lower TCO and faster time-to-value.")
                gaps.append(f"{comp.name} lacks advanced AI orchestration capabilities.")
            elif comp.market_position == "niche":
                opportunities.append(f"Block {comp.name} by emphasizing enterprise scale and security.")
                
        intelligence.displacement_opportunities = opportunities[:3]
        intelligence.feature_gaps = list(set(gaps))
        
        if intelligence.competitive_risk_score > 0.7:
            intelligence.strategic_opportunity_detection = "Highly competitive red ocean market. Require strong technical differentiation and executive multi-threading."
            intelligence.recommended_positioning = "Position Avenor as the next-generation AI-native alternative to legacy platforms. Lead with the Knowledge Graph."
        elif intelligence.competitive_risk_score > 0.4:
            intelligence.strategic_opportunity_detection = "Moderate competition. Opportunities exist in specific feature gaps."
            intelligence.recommended_positioning = "Highlight workflow automation and context intelligence."
        else:
            intelligence.strategic_opportunity_detection = "Fragmented market with weak incumbents. Strong opportunity for rapid market capture."
            intelligence.recommended_positioning = "Focus on ease of use and rapid deployment to outmaneuver slow incumbents."
            
        intelligence.ai_summary = f"Detected {len(competitors)} competitors ({len(direct_competitors)} direct). Competitive risk score is {intelligence.competitive_risk_score*100:.0f}%. Key vulnerability across incumbents is legacy architecture."
        
        return intelligence
