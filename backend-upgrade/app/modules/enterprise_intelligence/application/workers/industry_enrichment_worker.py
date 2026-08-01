import logging
from uuid import UUID
from typing import List

from app.modules.enterprise_intelligence.application.engines.industry_intelligence_engine import IndustryIntelligenceEngine

logger = logging.getLogger(__name__)

class IndustryEnrichmentWorker:
    """
    Background worker for processing bulk industry enrichment (Phase 7, Engine 10).
    """
    def __init__(self, engine: IndustryIntelligenceEngine):
        self.engine = engine

    async def bulk_enrich_industry(self, tenant_id: UUID, industries: List[str]) -> None:
        """
        Processes a batch of industries for intelligence enrichment.
        """
        logger.info(f"Starting bulk industry enrichment for {len(industries)} industries (tenant: {tenant_id})")
        
        success_count = 0
        failure_count = 0
        
        for industry in industries:
            try:
                await self.engine.get_or_enrich_industry(tenant_id, industry, force_refresh=False)
                success_count += 1
            except Exception as e:
                logger.error(f"Failed to bulk enrich industry data for {industry}: {str(e)}")
                failure_count += 1
                
        logger.info(f"Bulk industry enrichment complete. Success: {success_count}, Failed: {failure_count}")
