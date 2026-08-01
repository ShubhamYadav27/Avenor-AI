"""app/crm/providers/dynamics/__init__.py"""
from app.crm.providers.dynamics.provider import DynamicsProvider
from app.crm.registry import CRMProviderRegistry

CRMProviderRegistry.register(
    name="dynamics",
    provider_cls=DynamicsProvider,
    display_name="Microsoft Dynamics 365",
    description="Connect Microsoft Dynamics 365 to sync Opportunities, Accounts, Contacts, and Leads.",
    logo_url="/logos/dynamics.svg",
    docs_url="https://docs.microsoft.com/en-us/dynamics365/developer/",
    feature_flag="ENABLE_DYNAMICS",
)

__all__ = ["DynamicsProvider"]
