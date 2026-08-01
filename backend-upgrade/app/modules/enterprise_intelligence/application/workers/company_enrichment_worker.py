import logging
from uuid import UUID
from typing import List

from app.modules.enterprise_intelligence.application.engines.company_intelligence_engine import CompanyIntelligenceEngine

logger = logging.getLogger(__name__)

class CompanyEnrichmentWorker:
    """
    Background worker for processing bulk company enrichment (Phase 7, Engine 1).
    Runs asynchronously, often triggered via Celery or similar task queues.
    """
    def __init__(self, engine: CompanyIntelligenceEngine):
        self.engine = engine

    async def bulk_enrich_companies(self, tenant_id: UUID, domains: List[str]) -> None:
        """
        Processes a batch of domains for enrichment.
        """
        logger.info(f"Starting bulk enrichment for {len(domains)} companies (tenant: {tenant_id})")
        
        success_count = 0
        failure_count = 0
        
        for domain in domains:
            try:
                # Force refresh is usually false unless specifically requested.
                await self.engine.get_or_enrich_company(tenant_id, domain, force_refresh=False)
                success_count += 1
            except Exception as e:
                logger.error(f"Failed to bulk enrich {domain}: {str(e)}")
                failure_count += 1
                
        logger.info(f"Bulk enrichment complete. Success: {success_count}, Failed: {failure_count}")

# In a real environment, this would be wrapped in a Celery @task or FastAPI BackgroundTasks dependency.
