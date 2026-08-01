import logging
from typing import Optional
from uuid import UUID
from datetime import datetime, timezone

from app.modules.enterprise_intelligence.domain.technology_intelligence import TechnologyIntelligence, TechnologyItem
from app.modules.enterprise_intelligence.domain.repositories import TechnologyIntelligenceRepository, TechnologyIntelligenceProvider
from app.modules.enterprise_intelligence.domain.company_intelligence import CompanyIntelligence

logger = logging.getLogger(__name__)

class TechnologyIntelligenceEngine:
    """
    Core Application Service for the Technology Intelligence Engine (Phase 7, Engine 3).
    Orchestrates data enrichment from Layer 2 (Public), Layer 3 (Licensed Providers),
    and applies Layer 4 (Proprietary AI) intelligence for tech landscape analysis.
    """
    def __init__(
        self,
        repository: TechnologyIntelligenceRepository,
        provider: TechnologyIntelligenceProvider
    ):
        self.repository = repository
        self.provider = provider
        
    async def get_or_enrich_technology(
        self, 
        tenant_id: UUID, 
        company_id: UUID, 
        company_domain: str, 
        force_refresh: bool = False
    ) -> TechnologyIntelligence:
        """
        Retrieves technology intelligence for a given company.
        """
        existing = await self.repository.get_by_company_id(tenant_id, company_id)
        
        if existing and not force_refresh:
            if existing.last_enriched_at:
                days_old = (datetime.now(timezone.utc) - existing.last_enriched_at).days
                if days_old < 30: # Tech stack changes slowly
                    return existing
                    
        return await self._run_enrichment_pipeline(tenant_id, company_id, company_domain, existing)
        
    async def _run_enrichment_pipeline(
        self, 
        tenant_id: UUID, 
        company_id: UUID, 
        company_domain: str, 
        existing: Optional[TechnologyIntelligence] = None
    ) -> TechnologyIntelligence:
        logger.info(f"Starting Technology Intelligence enrichment for {company_domain} (tenant: {tenant_id})")
        
        intelligence = existing or TechnologyIntelligence(tenant_id=tenant_id, company_id=company_id, company_domain=company_domain)
        intelligence.enrichment_status = "enriching"
        
        try:
            # 1. Fetch external technology data (Layer 2 & 3 via Provider Abstraction)
            external_data = await self.provider.fetch_technology_data(company_domain)
            
            intelligence.stack = external_data.stack
            intelligence.provider_sources = external_data.provider_sources
            
            # 2. Invoke Layer 4 (Proprietary AI Models)
            intelligence = await self._apply_proprietary_ai(intelligence)
            
            intelligence.enrichment_status = "enriched"
            intelligence.last_enriched_at = datetime.now(timezone.utc)
            
            return await self.repository.save(intelligence)
            
        except Exception as e:
            logger.error(f"Failed to enrich technology for {company_domain}: {str(e)}")
            intelligence.enrichment_status = "failed"
            await self.repository.save(intelligence)
            raise

    async def _apply_proprietary_ai(self, intelligence: TechnologyIntelligence) -> TechnologyIntelligence:
        """
        Layer 4: Avenor's Proprietary AI models applied to the technology landscape.
        Generates maturity score, fit score, opportunity detection, and risk analysis.
        """
        stack = intelligence.stack
        
        has_crm = len(stack.crm) > 0
        has_cloud = len(stack.cloud_providers) > 0
        
        # Mock ML derivations
        base_maturity = 0.5
        if has_cloud: base_maturity += 0.2
        if has_crm: base_maturity += 0.2
            
        intelligence.maturity_score = min(1.0, base_maturity)
        intelligence.fit_score = 0.85 if has_crm else 0.40 # High fit if they use a CRM we can integrate with
        
        intelligence.ai_summary = "Modern tech stack with strong cloud infrastructure and CRM adoption."
        intelligence.opportunity_detection = "Likely expanding data analytics capabilities. Opportunity to pitch Revenue OS."
        intelligence.risk_analysis = "Low vendor lock-in risk."
        intelligence.competitive_comparison = "Above average maturity for the industry."
        
        return intelligence
