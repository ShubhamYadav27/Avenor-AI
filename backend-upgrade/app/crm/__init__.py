"""
app/crm/__init__.py

CRM-Agnostic Integration Layer for Avenor-AI.

This package provides a provider-independent abstraction over any CRM system.
Business logic must NEVER import from app.crm.providers.* directly.
Instead, always use CRMFactory.get_for_workspace() or CRMFactory.get_provider().

Architecture:
  app/crm/
    base/           <- Interfaces, canonical models, base OAuth handler
    providers/      <- Provider-specific adapters (HubSpot, Salesforce, etc.)
    engine/         <- Generic sync engine, mapper, conflict resolution
    registry.py     <- Provider registry + CRMProvider enum
    factory.py      <- CRMFactory
    router.py       <- Generic /crm/* API endpoints

Usage:
  from app.crm.factory import CRMFactory
  provider = CRMFactory.get_for_workspace(workspace_id, db)
  result = provider.incremental_sync()
"""

from app.crm.registry import CRMProvider, CRMProviderRegistry  # noqa: F401
from app.crm.factory import CRMFactory  # noqa: F401

__all__ = ["CRMProvider", "CRMProviderRegistry", "CRMFactory"]
