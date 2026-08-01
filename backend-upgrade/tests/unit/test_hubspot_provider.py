import pytest
import asyncio
from uuid import UUID, uuid4
from typing import Dict, Any

from app.modules.integration_hub.providers.hubspot.provider import HubSpotProvider
from app.modules.integration_hub.providers.hubspot.normalizer import HubSpotNormalizer
from app.modules.integration_hub.domain.models import IntegrationConnection, ProviderAuthType

@pytest.fixture
def hubspot_provider():
    return HubSpotProvider()

def test_hubspot_normalizer_company():
    raw_hubspot_company = {
        "id": "1001",
        "properties": {
            "domain": "acme.com",
            "name": "Acme Corp",
            "industry": "Software",
            "numemployees": "150",
            "annualrevenue": "5000000.0",
            "createdate": "2023-01-01T10:00:00Z",
            "hs_lastmodifieddate": "2023-01-05T10:00:00Z"
        }
    }
    
    normalized = HubSpotNormalizer.normalize_company(raw_hubspot_company)
    
    assert normalized["source"] == "hubspot"
    assert normalized["source_id"] == "1001"
    assert normalized["domain"] == "acme.com"
    assert normalized["name"] == "Acme Corp"
    assert normalized["industry"] == "Software"
    assert normalized["employee_count"] == 150
    assert normalized["annual_revenue"] == 5000000.0

def test_hubspot_normalizer_contact():
    raw_hubspot_contact = {
        "id": "2001",
        "properties": {
            "email": "jane@acme.com",
            "firstname": "Jane",
            "lastname": "Doe",
            "jobtitle": "CEO",
            "phone": "555-1234",
            "associatedcompanyid": "1001"
        }
    }
    
    normalized = HubSpotNormalizer.normalize_contact(raw_hubspot_contact)
    
    assert normalized["source"] == "hubspot"
    assert normalized["source_id"] == "2001"
    assert normalized["email"] == "jane@acme.com"
    assert normalized["first_name"] == "Jane"
    assert normalized["last_name"] == "Doe"
    assert normalized["job_title"] == "CEO"

@pytest.mark.asyncio
async def test_hubspot_webhook_verification(hubspot_provider):
    # Test valid signature (our mock check)
    headers = {"x-hubspot-signature-v3": "valid_mock_signature"}
    is_valid = await hubspot_provider.verify_webhook_signature(headers, b"body")
    assert is_valid is True
    
    # Test invalid signature
    headers = {"x-hubspot-signature-v3": "invalid"}
    is_valid = await hubspot_provider.verify_webhook_signature(headers, b"body")
    assert is_valid is False

def test_hubspot_webhook_parser(hubspot_provider):
    payload = [
        {"objectId": 123, "subscriptionType": "company.creation"},
        {"objectId": 456, "subscriptionType": "contact.propertyChange"}
    ]
    
    events = hubspot_provider.parse_webhook_events(payload)
    
    assert len(events) == 2
    assert events[0]["event_type"] == "company_created"
    assert events[0]["source_id"] == 123
    assert events[1]["event_type"] == "contact_updated"
    assert events[1]["source_id"] == 456
