"""app/crm/providers/hubspot/__init__.py"""
from app.crm.providers.hubspot.provider import HubSpotProvider
from app.crm.registry import CRMProviderRegistry

CRMProviderRegistry.register(
    name="hubspot",
    provider_cls=HubSpotProvider,
    display_name="HubSpot",
    description="Connect HubSpot CRM to sync deals, companies, contacts, and owners.",
    logo_url="/logos/hubspot.svg",
    docs_url="https://developers.hubspot.com/docs/api/overview",
    feature_flag="ENABLE_HUBSPOT",
)

__all__ = ["HubSpotProvider"]
