from typing import Dict, Any
import logging
import asyncio

from app.modules.integration_hub.domain.models import IntegrationConnection, SyncCursor
from app.modules.integration_hub.domain.ports import SyncProvider
from app.modules.integration_hub.application.provider_registry import provider_registry

logger = logging.getLogger(__name__)

class SyncEngine:
    """
    Application Service responsible for executing full and incremental data syncs
    from an external provider into the Enterprise Intelligence Cloud.
    """
    
    async def run_sync_job(self, connection: IntegrationConnection, entity_type: str, cursor: SyncCursor = None) -> SyncCursor:
        """
        Executes a sync job for a specific entity type (e.g., companies, contacts).
        Handles pagination internally by continuously fetching records until the async generator is exhausted.
        """
        provider = provider_registry.get_provider(connection.provider_name)
        if not provider or not isinstance(provider, SyncProvider):
            logger.error(f"Provider {connection.provider_name} does not support Sync operations.")
            raise ValueError("Unsupported sync provider")

        logger.info(f"Starting sync job for {connection.provider_name} - {entity_type} (Connection: {connection.id})")
        
        records_processed = 0
        new_cursor = cursor
        
        try:
            # Consume the async generator provided by the SDK
            async for record in provider.fetch_records(connection=connection, entity_type=entity_type, cursor=cursor):
                await self._process_record(entity_type, record)
                records_processed += 1
                
                # In a real implementation, the generator might yield a tuple of (record, next_cursor)
                # For simplicity here, we assume the engine tracks processing count
                
        except Exception as e:
            logger.error(f"Sync failed for {connection.provider_name}: {str(e)}")
            # Raise exception so RetryEngine or Celery can intercept it and schedule a retry
            raise
            
        logger.info(f"Completed sync job. Processed {records_processed} records.")
        # Return the updated cursor boundary for the next incremental sync
        return new_cursor

    async def _process_record(self, entity_type: str, record: Dict[str, Any]):
        """
        Passes the raw record to the Normalization Layer to map into a Canonical Entity.
        """
        # Here we would call the Normalizer and send it to the Event Bus
        # e.g., NormalizationLayer.normalize(entity_type, record)
        # e.g., EventBus.publish("integration.record_synced", canonical_entity)
        pass
