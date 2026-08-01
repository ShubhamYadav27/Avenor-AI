import logging
from typing import Optional
from uuid import UUID
from datetime import datetime, timezone

from app.modules.enterprise_intelligence.domain.hiring_intelligence import HiringIntelligence
from app.modules.enterprise_intelligence.domain.repositories import HiringIntelligenceRepository, HiringIntelligenceProvider

logger = logging.getLogger(__name__)

class HiringIntelligenceEngine:
    """
    Core Application Service for the Hiring Intelligence Engine (Phase 7, Engine 6).
    Orchestrates data enrichment from Layer 2 (Public), Layer 3 (Licensed Providers),
    and applies Layer 4 (Proprietary AI) intelligence for hiring and growth analysis.
    """
    def __init__(
        self,
        repository: HiringIntelligenceRepository,
        provider: HiringIntelligenceProvider
    ):
        self.repository = repository
        self.provider = provider
        
    async def get_or_enrich_hiring(
        self, 
        tenant_id: UUID, 
        company_id: UUID, 
        company_domain: str, 
        force_refresh: bool = False
    ) -> HiringIntelligence:
        """
        Retrieves hiring intelligence for a given company.
        """
        existing = await self.repository.get_by_company_id(tenant_id, company_id)
        
        if existing and not force_refresh:
            if existing.last_enriched_at:
                days_old = (datetime.now(timezone.utc) - existing.last_enriched_at).days
                if days_old < 7: # Hiring data changes frequently
                    return existing
                    
        return await self._run_enrichment_pipeline(tenant_id, company_id, company_domain, existing)
        
    async def _run_enrichment_pipeline(
        self, 
        tenant_id: UUID, 
        company_id: UUID, 
        company_domain: str, 
        existing: Optional[HiringIntelligence] = None
    ) -> HiringIntelligence:
        logger.info(f"Starting Hiring Intelligence enrichment for {company_domain} (tenant: {tenant_id})")
        
        intelligence = existing or HiringIntelligence(tenant_id=tenant_id, company_id=company_id, company_domain=company_domain)
        intelligence.enrichment_status = "enriching"
        
        try:
            # 1. Fetch external hiring data (Layer 2 & 3 via Provider Abstraction)
            external_data = await self.provider.fetch_hiring_data(company_domain)
            
            intelligence.open_roles = external_data.open_roles
            intelligence.total_open_roles = len(external_data.open_roles)
            
            # Aggregate counts by department
            dept_counts = {}
            for role in intelligence.open_roles:
                dept_counts[role.department] = dept_counts.get(role.department, 0) + 1
            intelligence.department_counts = dept_counts
            
            # 2. Invoke Layer 4 (Proprietary AI Models)
            intelligence = await self._apply_proprietary_ai(intelligence)
            
            intelligence.enrichment_status = "enriched"
            intelligence.last_enriched_at = datetime.now(timezone.utc)
            
            return await self.repository.save(intelligence)
            
        except Exception as e:
            logger.error(f"Failed to enrich hiring for {company_domain}: {str(e)}")
            intelligence.enrichment_status = "failed"
            await self.repository.save(intelligence)
            raise

    async def _apply_proprietary_ai(self, intelligence: HiringIntelligence) -> HiringIntelligence:
        """
        Layer 4: Avenor's Proprietary AI models applied to hiring data.
        Generates hiring velocity, growth momentum, and buying window insights.
        """
        total_roles = intelligence.total_open_roles
        dept_counts = intelligence.department_counts
        
        if total_roles == 0:
            intelligence.hiring_velocity = "frozen"
            intelligence.buying_window_impact = "low"
            intelligence.organizational_expansion_score = 0.0
            intelligence.hiring_momentum_score = 0.0
            intelligence.ai_summary = "No active hiring detected. Company may be on a hiring freeze or has low growth momentum."
            return intelligence
            
        intelligence.organizational_expansion_score = min(1.0, total_roles / 50.0)
        intelligence.hiring_momentum_score = min(1.0, total_roles / 25.0)
        
        if intelligence.hiring_momentum_score > 0.7:
            intelligence.hiring_velocity = "accelerating"
            intelligence.buying_window_impact = "high"
        elif intelligence.hiring_momentum_score > 0.3:
            intelligence.hiring_velocity = "stable"
            intelligence.buying_window_impact = "medium"
        else:
            intelligence.hiring_velocity = "slowing"
            intelligence.buying_window_impact = "low"
            
        # Detect Revenue/Tech expansion signals
        if dept_counts.get("Sales", 0) > 0 or dept_counts.get("Marketing", 0) > 0:
            intelligence.revenue_expansion_indicators.append("Aggressive GTM expansion detected.")
            
        if dept_counts.get("Engineering", 0) > 0 or dept_counts.get("AI/ML", 0) > 0:
            intelligence.technology_adoption_indicators.append("Strong technical scale-up. High probability of new software purchases.")
            
        intelligence.ai_summary = f"Detected {total_roles} open roles across {len(dept_counts)} departments. Hiring velocity is {intelligence.hiring_velocity}."
        
        if intelligence.buying_window_impact == "high":
            intelligence.growth_opportunity_detection = "High hiring volume indicates strong budget availability and potential organizational restructuring. Excellent time to engage."
            
        return intelligence
