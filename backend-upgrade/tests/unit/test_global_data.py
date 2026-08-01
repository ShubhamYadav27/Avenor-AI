import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.modules.global_data_platform.api.router import router, _graph_nodes

app = FastAPI()
app.include_router(router)
client = TestClient(app)

@pytest.fixture(autouse=True)
def clear_state():
    _graph_nodes.clear()
    yield

def test_entity_creation_and_merge():
    # 1. Provide data from low-trust source (web scraper)
    client.post("/v1/intelligence/entities", json={
        "entity_id": "comp_apple",
        "type": "company",
        "provider_name": "public_web_scraper",
        "facts": {"revenue": "300B", "ceo": "Tim Cook"}
    })
    
    # 2. Provide conflicting data from high-trust source (Salesforce CRM)
    client.post("/v1/intelligence/entities", json={
        "entity_id": "comp_apple",
        "type": "company",
        "provider_name": "salesforce_crm",
        "facts": {"revenue": "394.3B"} # Overrides scraper's 300B
    })
    
    # 3. Verify Canonical State
    res = client.get("/v1/intelligence/entities/comp_apple")
    assert res.status_code == 200
    data = res.json()["data"]
    
    # CEO should still be Tim Cook (only provided by scraper)
    assert data["ceo"] == "Tim Cook"
    
    # Revenue should be 394.3B (Salesforce CRM > Web Scraper)
    assert data["revenue"] == "394.3B"

def test_provenance_history_is_maintained():
    # Insert conflict
    client.post("/v1/intelligence/entities", json={
        "entity_id": "comp_msft",
        "type": "company",
        "provider_name": "public_web_scraper",
        "facts": {"employees": "180,000"}
    })
    client.post("/v1/intelligence/entities", json={
        "entity_id": "comp_msft",
        "type": "company",
        "provider_name": "clearbit_api",
        "facts": {"employees": "221,000"}
    })
    
    # Fetch Provenance
    res = client.get("/v1/intelligence/entities/comp_msft/provenance")
    assert res.status_code == 200
    history = res.json()["provenance"]
    
    # Check Employee Field
    emp_history = history["employees"]["history"]
    assert len(emp_history) == 2
    
    # Clearbit has higher confidence (0.85) than Web Scraper (0.40)
    assert history["employees"]["canonical_source"] == "clearbit_api"
    assert history["employees"]["canonical_value"] == "221,000"

def test_relationship_edge_creation():
    res = client.post("/v1/intelligence/relationships", json={
        "source_id": "comp_apple",
        "target_id": "tech_swift",
        "relationship_type": "uses_tech",
        "provider_name": "clearbit_api"
    })
    assert res.status_code == 200
    assert "edge_id" in res.json()
