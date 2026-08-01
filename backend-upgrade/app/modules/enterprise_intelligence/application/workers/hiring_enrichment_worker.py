import logging
from uuid import UUID
from typing import List, Tuple

from app.modules.enterprise_intelligence.application.engines.hiring_intelligence_engine import HiringIntelligenceEngine

logger = logging.getLogger(__name__)

class HiringEnrichmentWorker:
    """
    Background worker for processing bulk hiring enrichment (Phase 7, Engine 6).
    """
    def __init__(self, engine: HiringIntelligenceEngine):
        self.engine = engine

    async def bulk_enrich_hiring(self, tenant_id: UUID, companies: List[Tuple[UUID, str]]) -> None:
        """
        Processes a batch of companies (id, domain tuples) for hiring enrichment.
        """
        logger.info(f"Starting bulk hiring enrichment for {len(companies)} companies (tenant: {tenant_id})")
        
        success_count = 0
        failure_count = 0
        
        for company_id, domain in companies:
            try:
                await self.engine.get_or_enrich_hiring(tenant_id, company_id, domain, force_refresh=False)
                success_count += 1
            except Exception as e:
                logger.error(f"Failed to bulk enrich hiring for {domain}: {str(e)}")
                failure_count += 1
                
        logger.info(f"Bulk hiring enrichment complete. Success: {success_count}, Failed: {failure_count}")
