import logging
from uuid import UUID
from typing import List, Tuple

from app.modules.enterprise_intelligence.application.engines.technology_intelligence_engine import TechnologyIntelligenceEngine

logger = logging.getLogger(__name__)

class TechnologyEnrichmentWorker:
    """
    Background worker for processing bulk technology landscape enrichment (Phase 7, Engine 3).
    """
    def __init__(self, engine: TechnologyIntelligenceEngine):
        self.engine = engine

    async def bulk_enrich_technology(self, tenant_id: UUID, companies: List[Tuple[UUID, str]]) -> None:
        """
        Processes a batch of companies (id, domain tuples) for tech enrichment.
        """
        logger.info(f"Starting bulk technology enrichment for {len(companies)} companies (tenant: {tenant_id})")
        
        success_count = 0
        failure_count = 0
        
        for company_id, domain in companies:
            try:
                await self.engine.get_or_enrich_technology(tenant_id, company_id, domain, force_refresh=False)
                success_count += 1
            except Exception as e:
                logger.error(f"Failed to bulk enrich technology for {domain}: {str(e)}")
                failure_count += 1
                
        logger.info(f"Bulk technology enrichment complete. Success: {success_count}, Failed: {failure_count}")
