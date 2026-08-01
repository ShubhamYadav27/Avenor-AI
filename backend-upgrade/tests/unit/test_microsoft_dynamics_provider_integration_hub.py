import pytest
import asyncio
from typing import Dict, Any

from app.modules.integration_hub.providers.microsoft_dynamics.provider import DynamicsProvider
from app.modules.integration_hub.providers.microsoft_dynamics.normalizer import DynamicsNormalizer

@pytest.fixture
def dynamics_provider():
    return DynamicsProvider()

def test_dynamics_normalizer_company():
    raw_ms_account = {
        "accountid": "b3b246a4-44df-e811-a957-000d3a1b32d0",
        "name": "Adventure Works",
        "websiteurl": "adventure-works.com",
        "industrycode": 10,
        "numberofemployees": 500,
        "revenue": 25000000.0,
        "createdon": "2023-01-01T10:00:00Z",
        "modifiedon": "2023-01-05T10:00:00Z"
    }
    
    normalized = DynamicsNormalizer.normalize_company(raw_ms_account)
    
    assert normalized["source"] == "microsoft_dynamics"
    assert normalized["source_id"] == "b3b246a4-44df-e811-a957-000d3a1b32d0"
    assert normalized["domain"] == "adventure-works.com"
    assert normalized["name"] == "Adventure Works"
    assert normalized["industry"] == 10
    assert normalized["employee_count"] == 500
    assert normalized["annual_revenue"] == 25000000.0

def test_dynamics_normalizer_lead():
    raw_ms_lead = {
        "leadid": "c1d2e3f4-55aa-b811-c957-000d3a1b32d1",
        "firstname": "John",
        "lastname": "Smith",
        "emailaddress1": "john@example.com",
        "companyname": "Smith Tech",
        "statecode": 0,
        "createdon": "2023-01-01T10:00:00Z",
        "modifiedon": "2023-01-05T10:00:00Z"
    }
    
    normalized = DynamicsNormalizer.normalize_lead(raw_ms_lead)
    
    assert normalized["source"] == "microsoft_dynamics"
    assert normalized["source_id"] == "c1d2e3f4-55aa-b811-c957-000d3a1b32d1"
    assert normalized["first_name"] == "John"
    assert normalized["last_name"] == "Smith"
    assert normalized["email"] == "john@example.com"
    assert normalized["company_name"] == "Smith Tech"
    assert normalized["status"] == 0

@pytest.mark.asyncio
async def test_dynamics_webhook_verification(dynamics_provider):
    # Test valid signature (mock)
    headers = {"x-ms-dynamics-mock": "valid"}
    is_valid = await dynamics_provider.verify_webhook_signature(headers, b"{}")
    assert is_valid is True
    
    # Test invalid signature
    headers = {"x-ms-dynamics-mock": "invalid"}
    is_valid = await dynamics_provider.verify_webhook_signature(headers, b"bad body")
    assert is_valid is False
