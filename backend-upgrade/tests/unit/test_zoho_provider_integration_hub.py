import pytest
import asyncio
from typing import Dict, Any

from app.modules.integration_hub.providers.zoho.provider import ZohoProvider
from app.modules.integration_hub.providers.zoho.normalizer import ZohoNormalizer

@pytest.fixture
def zoho_provider():
    return ZohoProvider()

def test_zoho_normalizer_company():
    raw_zoho_account = {
        "id": "1111222233334444",
        "Account_Name": "Zoho Corp",
        "Website": "zoho.com",
        "Industry": "Technology",
        "Employees": 5000,
        "Annual_Revenue": 50000000.0,
        "Created_Time": "2023-01-01T10:00:00+05:30",
        "Modified_Time": "2023-01-05T10:00:00+05:30"
    }
    
    normalized = ZohoNormalizer.normalize_company(raw_zoho_account)
    
    assert normalized["source"] == "zoho"
    assert normalized["source_id"] == "1111222233334444"
    assert normalized["domain"] == "zoho.com"
    assert normalized["name"] == "Zoho Corp"
    assert normalized["industry"] == "Technology"
    assert normalized["employee_count"] == 5000
    assert normalized["annual_revenue"] == 50000000.0

def test_zoho_normalizer_contact():
    raw_zoho_contact = {
        "id": "5555666677778888",
        "First_Name": "Alice",
        "Last_Name": "Smith",
        "Email": "alice@zoho.com",
        "Title": "Director",
        "Account_Name": {"name": "Zoho Corp", "id": "1111222233334444"},
        "Created_Time": "2023-01-01T10:00:00+05:30",
        "Modified_Time": "2023-01-05T10:00:00+05:30"
    }
    
    normalized = ZohoNormalizer.normalize_contact(raw_zoho_contact)
    
    assert normalized["source"] == "zoho"
    assert normalized["source_id"] == "5555666677778888"
    assert normalized["first_name"] == "Alice"
    assert normalized["last_name"] == "Smith"
    assert normalized["email"] == "alice@zoho.com"
    assert normalized["job_title"] == "Director"
    assert normalized["associated_company_id"] == "1111222233334444"

@pytest.mark.asyncio
async def test_zoho_webhook_verification(zoho_provider):
    # Test valid signature (mock)
    headers = {"x-zoho-mock": "valid"}
    is_valid = await zoho_provider.verify_webhook_signature(headers, b"{}")
    assert is_valid is True
    
    # Test invalid signature
    headers = {"x-zoho-mock": "invalid"}
    is_valid = await zoho_provider.verify_webhook_signature(headers, b"bad body")
    assert is_valid is False
