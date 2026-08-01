import logging
from uuid import UUID
from typing import List

from app.modules.enterprise_intelligence.application.engines.contact_intelligence_engine import ContactIntelligenceEngine

logger = logging.getLogger(__name__)

class ContactEnrichmentWorker:
    """
    Background worker for processing bulk contact enrichment (Phase 7, Engine 2).
    """
    def __init__(self, engine: ContactIntelligenceEngine):
        self.engine = engine

    async def bulk_enrich_contacts(self, tenant_id: UUID, emails: List[str]) -> None:
        """
        Processes a batch of emails for enrichment.
        """
        logger.info(f"Starting bulk contact enrichment for {len(emails)} contacts (tenant: {tenant_id})")
        
        success_count = 0
        failure_count = 0
        
        for email in emails:
            try:
                await self.engine.get_or_enrich_contact(tenant_id, email, force_refresh=False)
                success_count += 1
            except Exception as e:
                logger.error(f"Failed to bulk enrich contact {email}: {str(e)}")
                failure_count += 1
                
        logger.info(f"Bulk contact enrichment complete. Success: {success_count}, Failed: {failure_count}")
