import logging
from typing import Optional
from uuid import UUID
from datetime import datetime, timezone

from app.modules.enterprise_intelligence.domain.contact_intelligence import ContactIntelligence
from app.modules.enterprise_intelligence.domain.repositories import ContactIntelligenceRepository, ContactIntelligenceProvider

logger = logging.getLogger(__name__)

class ContactIntelligenceEngine:
    """
    Core Application Service for the Contact Intelligence Engine (Phase 7, Engine 2).
    Orchestrates data enrichment from Layer 1 (CRM), Layer 2 (Public), Layer 3 (Licensed Providers),
    and finally applies Layer 4 (Proprietary AI) intelligence.
    """
    def __init__(
        self,
        repository: ContactIntelligenceRepository,
        provider: ContactIntelligenceProvider
    ):
        self.repository = repository
        self.provider = provider
        
    async def get_or_enrich_contact(self, tenant_id: UUID, email: str, force_refresh: bool = False) -> ContactIntelligence:
        """
        Retrieves contact intelligence. If missing or stale, triggers the enrichment pipeline.
        """
        existing = await self.repository.get_by_email(tenant_id, email)
        
        if existing and not force_refresh:
            if existing.last_enriched_at:
                days_old = (datetime.now(timezone.utc) - existing.last_enriched_at).days
                if days_old < 14: # Contacts decay faster than companies
                    return existing
                    
        return await self._run_enrichment_pipeline(tenant_id, email, existing)
        
    async def _run_enrichment_pipeline(
        self, 
        tenant_id: UUID, 
        email: str, 
        existing: Optional[ContactIntelligence] = None
    ) -> ContactIntelligence:
        logger.info(f"Starting Contact Intelligence enrichment for {email} (tenant: {tenant_id})")
        
        intelligence = existing or ContactIntelligence(tenant_id=tenant_id)
        intelligence.communication.email = email
        intelligence.enrichment_status = "enriching"
        
        try:
            # 1. Fetch external intelligence (Layer 2 & 3 via Provider Abstraction)
            external_data = await self.provider.fetch_contact_data(email)
            
            intelligence.profile = external_data.profile
            intelligence.communication = external_data.communication
            intelligence.relationships = external_data.relationships
            intelligence.provider_sources = external_data.provider_sources
            
            # 2. Invoke Layer 4 (Proprietary AI Models)
            intelligence = await self._apply_proprietary_ai(intelligence)
            
            intelligence.enrichment_status = "enriched"
            intelligence.last_enriched_at = datetime.now(timezone.utc)
            
            return await self.repository.save(intelligence)
            
        except Exception as e:
            logger.error(f"Failed to enrich contact {email}: {str(e)}")
            intelligence.enrichment_status = "failed"
            await self.repository.save(intelligence)
            raise

    async def _apply_proprietary_ai(self, intelligence: ContactIntelligence) -> ContactIntelligence:
        """
        Layer 4: Avenor's Proprietary AI models applied to contact data.
        Determines influence score and summarizes communication insights.
        """
        seniority = intelligence.profile.seniority or ""
        
        # Mock logic representing AI output
        base_influence = 0.5
        if seniority.lower() in ["c-level", "vp"]:
            base_influence = 0.95
        elif seniority.lower() in ["director", "head"]:
            base_influence = 0.75
            
        intelligence.influence_score = base_influence
        intelligence.ai_summary = f"Contact holds a {seniority} role. Projected to have strong purchasing influence."
        
        return intelligence
