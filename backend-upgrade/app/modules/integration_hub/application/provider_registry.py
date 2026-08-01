from typing import Dict, Optional, Type
from app.modules.integration_hub.domain.ports import IntegrationProvider
import logging

logger = logging.getLogger(__name__)

class ProviderRegistry:
    """
    Factory pattern implementing the central registry for all Integration Providers.
    The Integration Orchestrator relies on this to discover and instantiate providers natively.
    """
    
    def __init__(self):
        self._providers: Dict[str, Type[IntegrationProvider]] = {}
        
    def register(self, name: str, provider_class: Type[IntegrationProvider]):
        """Registers a provider class under a specific name."""
        if name in self._providers:
            logger.warning(f"Provider {name} is already registered. Overwriting.")
        self._providers[name] = provider_class
        logger.info(f"Successfully registered provider: {name}")
        
    def get_provider(self, name: str) -> Optional[IntegrationProvider]:
        """Instantiates and returns the requested provider."""
        provider_class = self._providers.get(name)
        if not provider_class:
            logger.error(f"Provider {name} not found in registry.")
            return None
        # Providers are stateless, so instantiating them on-demand is safe
        return provider_class()
        
    def list_providers(self) -> Dict[str, dict]:
        """Returns the metadata for all registered providers."""
        metadata = {}
        for name, provider_class in self._providers.items():
            provider_instance = provider_class()
            metadata[name] = provider_instance.get_metadata().model_dump()
        return metadata

# Global singleton registry instance
provider_registry = ProviderRegistry()
