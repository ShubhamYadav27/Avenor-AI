import logging
from uuid import UUID

from app.modules.enterprise_intelligence.application.engines.identity_resolution_engine import IdentityResolutionEngine

logger = logging.getLogger(__name__)

class IdentityResolutionWorker:
    """
    Background worker for continuous duplicate detection and identity refresh (Phase 7, Engine 12).
    """
    def __init__(self, engine: IdentityResolutionEngine):
        self.engine = engine

    async def scan_for_duplicates(self, tenant_id: UUID, entity_type: str) -> None:
        """
        Periodically scans the canonical entity tables to find and generate AI merge candidates.
        """
        logger.info(f"Starting duplicate scan for {entity_type}s (tenant: {tenant_id})")
        
        try:
            # Triggering find_merge_candidates executes the Layer 4 AI logic to calculate confidence scores
            # and append merge candidates to the entities.
            candidates = await self.engine.find_merge_candidates(tenant_id, entity_type)
            
            logger.info(f"Duplicate scan complete. Found {len(candidates)} entities with highly confident merge suggestions.")
        except Exception as e:
            logger.error(f"Failed to run duplicate scan for {entity_type}s: {str(e)}")
