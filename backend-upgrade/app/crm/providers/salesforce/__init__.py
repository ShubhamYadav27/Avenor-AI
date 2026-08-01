"""app/crm/providers/salesforce/__init__.py"""
from app.crm.providers.salesforce.provider import SalesforceProvider
from app.crm.registry import CRMProviderRegistry

CRMProviderRegistry.register(
    name="salesforce",
    provider_cls=SalesforceProvider,
    display_name="Salesforce",
    description="Connect Salesforce CRM to sync Opportunities, Accounts, Contacts, and Leads.",
    logo_url="/logos/salesforce.svg",
    docs_url="https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/",
    feature_flag="ENABLE_SALESFORCE",
)

__all__ = ["SalesforceProvider"]
