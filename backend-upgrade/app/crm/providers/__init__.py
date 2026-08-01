"""app/crm/providers/__init__.py
Imports all providers to trigger their self-registration with CRMProviderRegistry.
This file must be imported before the factory is used.
"""
# Each provider's __init__.py calls CRMProviderRegistry.register() on import.
# Import order does not matter — providers are independent.

from app.crm.providers.hubspot import HubSpotProvider        # noqa: F401
from app.crm.providers.salesforce import SalesforceProvider  # noqa: F401
from app.crm.providers.dynamics import DynamicsProvider      # noqa: F401
from app.crm.providers.zoho import ZohoProvider              # noqa: F401

__all__ = ["HubSpotProvider", "SalesforceProvider", "DynamicsProvider", "ZohoProvider"]
