import pytest
import asyncio
from typing import Dict, Any

from app.modules.integration_hub.providers.pipedrive.provider import PipedriveProvider
from app.modules.integration_hub.providers.pipedrive.normalizer import PipedriveNormalizer

@pytest.fixture
def pipedrive_provider():
    return PipedriveProvider()

def test_pipedrive_normalizer_company():
    raw_pd_org = {
        "id": 50,
        "name": "Wayne Enterprises",
        "people_count": 1000,
        "add_time": "2023-01-01 10:00:00",
        "update_time": "2023-01-05 10:00:00"
    }
    
    normalized = PipedriveNormalizer.normalize_company(raw_pd_org)
    
    assert normalized["source"] == "pipedrive"
    assert normalized["source_id"] == "50"
    assert normalized["name"] == "Wayne Enterprises"
    assert normalized["employee_count"] == 1000

def test_pipedrive_normalizer_contact():
    raw_pd_person = {
        "id": 100,
        "name": "Bruce Wayne",
        "email": [{"value": "bruce@wayne.com", "primary": True}],
        "phone": [{"value": "555-0101", "primary": True}],
        "org_id": {"name": "Wayne Enterprises", "value": 50},
        "add_time": "2023-01-01 10:00:00",
        "update_time": "2023-01-05 10:00:00"
    }
    
    normalized = PipedriveNormalizer.normalize_contact(raw_pd_person)
    
    assert normalized["source"] == "pipedrive"
    assert normalized["source_id"] == "100"
    assert normalized["first_name"] == "Bruce"
    assert normalized["last_name"] == "Wayne"
    assert normalized["email"] == "bruce@wayne.com"
    assert normalized["phone"] == "555-0101"
    assert normalized["associated_company_id"] == "50"

@pytest.mark.asyncio
async def test_pipedrive_webhook_verification(pipedrive_provider):
    # Test valid signature (mock)
    headers = {"x-pipedrive-mock": "valid"}
    is_valid = await pipedrive_provider.verify_webhook_signature(headers, b"{}")
    assert is_valid is True
    
    # Test invalid signature
    headers = {"x-pipedrive-mock": "invalid"}
    is_valid = await pipedrive_provider.verify_webhook_signature(headers, b"bad body")
    assert is_valid is False
