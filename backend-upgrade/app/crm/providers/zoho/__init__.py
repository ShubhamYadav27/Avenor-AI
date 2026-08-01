"""app/crm/providers/zoho/__init__.py"""
from app.crm.providers.zoho.provider import ZohoProvider
from app.crm.registry import CRMProviderRegistry

CRMProviderRegistry.register(
    name="zoho",
    provider_cls=ZohoProvider,
    display_name="Zoho CRM",
    description="Connect Zoho CRM to sync Deals, Accounts, Contacts, and Leads.",
    logo_url="/logos/zoho.svg",
    docs_url="https://www.zoho.com/crm/developer/docs/api/v7/",
    feature_flag="ENABLE_ZOHO",
)

__all__ = ["ZohoProvider"]
