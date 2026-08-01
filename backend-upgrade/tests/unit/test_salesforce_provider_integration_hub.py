import pytest
import asyncio
from typing import Dict, Any

from app.modules.integration_hub.providers.salesforce.provider import SalesforceProvider
from app.modules.integration_hub.providers.salesforce.normalizer import SalesforceNormalizer

@pytest.fixture
def salesforce_provider():
    return SalesforceProvider()

def test_salesforce_normalizer_company():
    raw_sfdc_account = {
        "Id": "0015g00000XyZ1AAAK",
        "Name": "Global Corp",
        "Website": "globalcorp.com",
        "Industry": "Technology",
        "NumberOfEmployees": 1500,
        "AnnualRevenue": 100000000.0,
        "CreatedDate": "2023-01-01T10:00:00Z",
        "LastModifiedDate": "2023-01-05T10:00:00Z"
    }
    
    normalized = SalesforceNormalizer.normalize_company(raw_sfdc_account)
    
    assert normalized["source"] == "salesforce"
    assert normalized["source_id"] == "0015g00000XyZ1AAAK"
    assert normalized["domain"] == "globalcorp.com"
    assert normalized["name"] == "Global Corp"
    assert normalized["industry"] == "Technology"
    assert normalized["employee_count"] == 1500
    assert normalized["annual_revenue"] == 100000000.0

def test_salesforce_normalizer_opportunity():
    raw_sfdc_opp = {
        "Id": "0065g00000AaBbCCAK",
        "Name": "Enterprise Deal Q3",
        "Amount": 250000.0,
        "StageName": "Negotiation",
        "ForecastCategoryName": "Pipeline",
        "CloseDate": "2023-09-30",
        "OwnerId": "0055g00000XXxxyyZZ",
        "AccountId": "0015g00000XyZ1AAAK"
    }
    
    normalized = SalesforceNormalizer.normalize_opportunity(raw_sfdc_opp)
    
    assert normalized["source"] == "salesforce"
    assert normalized["source_id"] == "0065g00000AaBbCCAK"
    assert normalized["name"] == "Enterprise Deal Q3"
    assert normalized["amount"] == 250000.0
    assert normalized["stage"] == "Negotiation"
    assert normalized["pipeline"] == "Pipeline"
    assert normalized["close_date"] == "2023-09-30"
    assert normalized["associated_company_id"] == "0015g00000XyZ1AAAK"

@pytest.mark.asyncio
async def test_salesforce_webhook_verification(salesforce_provider):
    # Test valid signature (our mock check looks for OrganizationId or x-sfdc-mock header)
    headers = {"x-sfdc-mock": "valid"}
    is_valid = await salesforce_provider.verify_webhook_signature(headers, b"<OrganizationId>12345</OrganizationId>")
    assert is_valid is True
    
    # Test invalid signature
    headers = {"x-sfdc-mock": "invalid"}
    is_valid = await salesforce_provider.verify_webhook_signature(headers, b"bad body")
    assert is_valid is False

def test_salesforce_webhook_parser(salesforce_provider):
    payload = {}
    events = salesforce_provider.parse_webhook_events(payload)
    # The mock currently returns an empty list
    assert events == []
