import logging
from uuid import UUID
from typing import List, Tuple

from app.modules.enterprise_intelligence.application.engines.competitive_intelligence_engine import CompetitiveIntelligenceEngine

logger = logging.getLogger(__name__)

class CompetitiveEnrichmentWorker:
    """
    Background worker for processing bulk competitive enrichment (Phase 7, Engine 8).
    """
    def __init__(self, engine: CompetitiveIntelligenceEngine):
        self.engine = engine

    async def bulk_enrich_competitive(self, tenant_id: UUID, companies: List[Tuple[UUID, str]]) -> None:
        """
        Processes a batch of companies (id, domain tuples) for competitive enrichment.
        """
        logger.info(f"Starting bulk competitive enrichment for {len(companies)} companies (tenant: {tenant_id})")
        
        success_count = 0
        failure_count = 0
        
        for company_id, domain in companies:
            try:
                await self.engine.get_or_enrich_competitive(tenant_id, company_id, domain, force_refresh=False)
                success_count += 1
            except Exception as e:
                logger.error(f"Failed to bulk enrich competitive data for {domain}: {str(e)}")
                failure_count += 1
                
        logger.info(f"Bulk competitive enrichment complete. Success: {success_count}, Failed: {failure_count}")
