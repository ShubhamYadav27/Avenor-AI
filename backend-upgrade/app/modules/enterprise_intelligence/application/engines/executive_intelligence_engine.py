import logging
from typing import Optional
from uuid import UUID
from datetime import datetime, timezone

from app.modules.enterprise_intelligence.domain.executive_intelligence import ExecutiveIntelligence
from app.modules.enterprise_intelligence.domain.repositories import ExecutiveIntelligenceRepository, ExecutiveIntelligenceProvider

logger = logging.getLogger(__name__)

class ExecutiveIntelligenceEngine:
    """
    Core Application Service for the Executive Intelligence Engine (Phase 7, Engine 7).
    Orchestrates data enrichment from Layer 2 (Public), Layer 3 (Licensed Providers),
    and applies Layer 4 (Proprietary AI) intelligence for executive analysis.
    """
    def __init__(
        self,
        repository: ExecutiveIntelligenceRepository,
        provider: ExecutiveIntelligenceProvider
    ):
        self.repository = repository
        self.provider = provider
        
    async def get_or_enrich_executives(
        self, 
        tenant_id: UUID, 
        company_id: UUID, 
        company_domain: str, 
        force_refresh: bool = False
    ) -> ExecutiveIntelligence:
        """
        Retrieves executive intelligence for a given company.
        """
        existing = await self.repository.get_by_company_id(tenant_id, company_id)
        
        if existing and not force_refresh:
            if existing.last_enriched_at:
                days_old = (datetime.now(timezone.utc) - existing.last_enriched_at).days
                if days_old < 14: # Executive data is relatively stable but changes matter
                    return existing
                    
        return await self._run_enrichment_pipeline(tenant_id, company_id, company_domain, existing)
        
    async def _run_enrichment_pipeline(
        self, 
        tenant_id: UUID, 
        company_id: UUID, 
        company_domain: str, 
        existing: Optional[ExecutiveIntelligence] = None
    ) -> ExecutiveIntelligence:
        logger.info(f"Starting Executive Intelligence enrichment for {company_domain} (tenant: {tenant_id})")
        
        intelligence = existing or ExecutiveIntelligence(tenant_id=tenant_id, company_id=company_id, company_domain=company_domain)
        intelligence.enrichment_status = "enriching"
        
        try:
            # 1. Fetch external executive data (Layer 2 & 3 via Provider Abstraction)
            external_data = await self.provider.fetch_executive_data(company_id)
            
            intelligence.executives = external_data.executives
            intelligence.recent_leadership_changes = external_data.recent_leadership_changes
            
            # 2. Invoke Layer 4 (Proprietary AI Models)
            intelligence = await self._apply_proprietary_ai(intelligence)
            
            intelligence.enrichment_status = "enriched"
            intelligence.last_enriched_at = datetime.now(timezone.utc)
            
            return await self.repository.save(intelligence)
            
        except Exception as e:
            logger.error(f"Failed to enrich executives for {company_domain}: {str(e)}")
            intelligence.enrichment_status = "failed"
            await self.repository.save(intelligence)
            raise

    async def _apply_proprietary_ai(self, intelligence: ExecutiveIntelligence) -> ExecutiveIntelligence:
        """
        Layer 4: Avenor's Proprietary AI models applied to executive data.
        Generates buying influence score, aggregates strategic priorities, and detects risks.
        """
        executives = intelligence.executives
        
        if not executives:
            intelligence.executive_buying_influence_score = 0.0
            intelligence.executive_risk_analysis = "High Risk: No executive leadership identified."
            intelligence.ai_summary = "Missing executive profile data."
            return intelligence
            
        # Aggregate strategic priorities
        all_priorities = []
        high_influence_count = 0
        
        for exec_prof in executives:
            all_priorities.extend(exec_prof.strategic_priorities)
            if exec_prof.decision_authority == "high" or exec_prof.influence_score > 0.7:
                high_influence_count += 1
                
        # Deduplicate priorities for the summary
        intelligence.overall_strategic_priorities = list(set(all_priorities))[:5]
        
        # Calculate buying influence score based on presence of high-authority execs
        score = min(1.0, high_influence_count / max(1, len(executives)) + (0.2 if high_influence_count > 0 else 0))
        intelligence.executive_buying_influence_score = score
        
        if len(intelligence.recent_leadership_changes) > 0:
            intelligence.executive_risk_analysis = "Moderate Risk: Recent leadership changes detected. Watch for strategic pivots."
            intelligence.strategic_opportunity_detection = "New executives often bring new budgets. Opportunity to displace legacy vendors."
            intelligence.recommended_engagement_strategy = "Multi-thread with both new and tenured executives to map shifting priorities."
        else:
            intelligence.executive_risk_analysis = "Low Risk: Stable leadership team."
            intelligence.strategic_opportunity_detection = "Focus on alignment with established long-term strategic priorities."
            intelligence.recommended_engagement_strategy = "Engage high-influence decision makers with ROI-focused business cases."
            
        priority_str = ", ".join(intelligence.overall_strategic_priorities) if intelligence.overall_strategic_priorities else "unknown"
        intelligence.ai_summary = f"Identified {len(executives)} key executives. Primary strategic priorities appear to be: {priority_str}. Buying influence score is {score*100:.0f}%."
        
        return intelligence
