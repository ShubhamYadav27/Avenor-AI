import logging
from typing import Optional, List
from uuid import UUID
from datetime import datetime, timezone

from app.modules.enterprise_intelligence.domain.company_intelligence import CompanyIntelligence
from app.modules.enterprise_intelligence.domain.repositories import CompanyIntelligenceRepository, CompanyIntelligenceProvider
# Reusing the existing KnowledgeGraph / Signals logic conceptually, as instructed by the architecture rules.

logger = logging.getLogger(__name__)

class CompanyIntelligenceEngine:
    """
    Core Application Service for the Company Intelligence Engine (Phase 7, Engine 1).
    Orchestrates data enrichment from Layer 1 (CRM), Layer 2 (Public), Layer 3 (Licensed Providers),
    and finally applies Layer 4 (Proprietary AI) intelligence.
    """
    def __init__(
        self,
        repository: CompanyIntelligenceRepository,
        provider: CompanyIntelligenceProvider
    ):
        self.repository = repository
        self.provider = provider
        
    async def get_or_enrich_company(self, tenant_id: UUID, domain: str, force_refresh: bool = False) -> CompanyIntelligence:
        """
        Retrieves company intelligence. If missing or stale, triggers the enrichment pipeline.
        """
        existing = await self.repository.get_by_domain(tenant_id, domain)
        
        if existing and not force_refresh:
            # Check staleness (e.g., older than 30 days)
            if existing.last_enriched_at:
                days_old = (datetime.now(timezone.utc) - existing.last_enriched_at).days
                if days_old < 30:
                    return existing
                    
        return await self._run_enrichment_pipeline(tenant_id, domain, existing)
        
    async def _run_enrichment_pipeline(
        self, 
        tenant_id: UUID, 
        domain: str, 
        existing: Optional[CompanyIntelligence] = None
    ) -> CompanyIntelligence:
        """
        The multi-layer intelligence enrichment pipeline.
        """
        logger.info(f"Starting Company Intelligence enrichment for {domain} (tenant: {tenant_id})")
        
        intelligence = existing or CompanyIntelligence(tenant_id=tenant_id, company_domain=domain)
        intelligence.enrichment_status = "enriching"
        
        try:
            # 1. Fetch external intelligence (Layer 2 & 3 via Provider Abstraction)
            external_data = await self.provider.fetch_company_data(domain)
            
            # Merge logic (simplified for the application service)
            intelligence.overview = external_data.overview
            intelligence.financials = external_data.financials
            intelligence.social = external_data.social
            intelligence.provider_sources = external_data.provider_sources
            
            # 2. Invoke Layer 4 (Proprietary AI Models)
            intelligence = await self._apply_proprietary_ai(intelligence)
            
            intelligence.enrichment_status = "enriched"
            intelligence.last_enriched_at = datetime.now(timezone.utc)
            
            # 3. Save and return
            return await self.repository.save(intelligence)
            
        except Exception as e:
            logger.error(f"Failed to enrich company {domain}: {str(e)}")
            intelligence.enrichment_status = "failed"
            await self.repository.save(intelligence)
            raise

    async def _apply_proprietary_ai(self, intelligence: CompanyIntelligence) -> CompanyIntelligence:
        """
        Layer 4: Avenor's Proprietary AI models applied to the collected company data.
        """
        # In a real implementation, this would call the `predictive_intelligence` module
        # or the AI provider to generate summaries and scores based on financial trajectory, hiring, etc.
        overview = intelligence.overview.description or ""
        financials = intelligence.financials.estimated_revenue or 0
        
        # Mock logic representing the ML output
        intelligence.ai_summary = f"AI Analysis: {intelligence.company_domain} is a growing entity in its sector."
        intelligence.buying_intent_score = 0.85 if financials > 1_000_000 else 0.45
        
        return intelligence
