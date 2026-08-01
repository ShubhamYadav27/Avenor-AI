import logging
from typing import Optional
from uuid import UUID
from datetime import datetime, timezone

from app.modules.enterprise_intelligence.domain.buying_committee import BuyingCommitteeIntelligence, CommitteeMember
from app.modules.enterprise_intelligence.domain.repositories import BuyingCommitteeRepository, BuyingCommitteeProvider

logger = logging.getLogger(__name__)

class BuyingCommitteeEngine:
    """
    Core Application Service for the Buying Committee Intelligence Engine (Phase 7, Engine 4).
    Orchestrates data enrichment from Layer 2 (Public), Layer 3 (Licensed Providers),
    and applies Layer 4 (Proprietary AI) intelligence for committee analysis.
    """
    def __init__(
        self,
        repository: BuyingCommitteeRepository,
        provider: BuyingCommitteeProvider
    ):
        self.repository = repository
        self.provider = provider
        
    async def get_or_enrich_committee(
        self, 
        tenant_id: UUID, 
        company_id: UUID, 
        force_refresh: bool = False
    ) -> BuyingCommitteeIntelligence:
        """
        Retrieves buying committee intelligence for a given company.
        """
        existing = await self.repository.get_by_company_id(tenant_id, company_id)
        
        if existing and not force_refresh:
            if existing.last_enriched_at:
                days_old = (datetime.now(timezone.utc) - existing.last_enriched_at).days
                if days_old < 7: # Committees change fast during deals
                    return existing
                    
        return await self._run_enrichment_pipeline(tenant_id, company_id, existing)
        
    async def _run_enrichment_pipeline(
        self, 
        tenant_id: UUID, 
        company_id: UUID, 
        existing: Optional[BuyingCommitteeIntelligence] = None
    ) -> BuyingCommitteeIntelligence:
        logger.info(f"Starting Buying Committee enrichment for company {company_id} (tenant: {tenant_id})")
        
        intelligence = existing or BuyingCommitteeIntelligence(tenant_id=tenant_id, company_id=company_id)
        intelligence.enrichment_status = "enriching"
        
        try:
            # 1. Fetch external committee data (Layer 2 & 3 via Provider Abstraction)
            external_data = await self.provider.fetch_committee_data(company_id)
            
            intelligence.members = external_data.members
            
            # 2. Invoke Layer 4 (Proprietary AI Models)
            intelligence = await self._apply_proprietary_ai(intelligence)
            
            intelligence.enrichment_status = "enriched"
            intelligence.last_enriched_at = datetime.now(timezone.utc)
            
            return await self.repository.save(intelligence)
            
        except Exception as e:
            logger.error(f"Failed to enrich committee for {company_id}: {str(e)}")
            intelligence.enrichment_status = "failed"
            await self.repository.save(intelligence)
            raise

    async def _apply_proprietary_ai(self, intelligence: BuyingCommitteeIntelligence) -> BuyingCommitteeIntelligence:
        """
        Layer 4: Avenor's Proprietary AI models applied to the buying committee.
        Generates completeness score, risk analysis, and missing stakeholders.
        """
        members = intelligence.members
        
        has_economic_buyer = any(m.roles.is_economic_buyer for m in members)
        has_champion = any(m.roles.is_champion for m in members)
        has_legal = any(m.roles.is_legal for m in members)
        
        # Mock ML derivations
        completeness = 0.3
        missing = []
        if has_economic_buyer:
            completeness += 0.3
        else:
            missing.append("Economic Buyer")
            
        if has_champion:
            completeness += 0.3
        else:
            missing.append("Champion")
            
        if has_legal:
            completeness += 0.1
        else:
            missing.append("Legal/Procurement")
            
        intelligence.committee_completeness_score = min(1.0, completeness)
        intelligence.missing_stakeholders = missing
        intelligence.multi_threading_score = min(1.0, len(members) / 5.0)
        
        if not has_economic_buyer:
            intelligence.buying_risk_analysis = "High Risk: No Economic Buyer identified."
        elif not has_champion:
            intelligence.buying_risk_analysis = "Medium Risk: Lack of a strong Champion."
        else:
            intelligence.buying_risk_analysis = "Low Risk: Key decision makers are engaged."
            
        intelligence.ai_summary = f"Identified {len(members)} committee members. Completeness score is {completeness*100}%."
        
        return intelligence
