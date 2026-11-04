"""
Unit tests for API v1 Evidence Endpoints (Phase 6, Task P6-T4).
Reference: docs/IMPLEMENTATION_PRD.md (P6-T4).
"""

import pytest
from fastapi.testclient import TestClient
from src.jyotish.api.main import app
from src.jyotish.evidence.pack import EvidencePack


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def sample_birth_payload():
    return {
        "birth_data": {
            "name": "Arjuna Test",
            "birth_date": "1990-05-15",
            "birth_time": "14:30:00",
            "latitude": 28.6139,
            "longitude": 77.2090,
            "timezone": "Asia/Kolkata"
        },
        "domain": "career",
        "school": "parashari",
        "ayanamsa": "Lahiri"
    }


def test_get_supported_domains_endpoint(client):
    res = client.get("/api/v1/evidence/domains")
    assert res.status_code == 200
    data = res.json()
    assert data["total_domains"] >= 9
    domain_keys = [d["domain"] for d in data["domains"]]
    assert "career" in domain_keys
    assert "marriage" in domain_keys
    assert "wealth" in domain_keys
    assert "health" in domain_keys

    # Check structure of career domain
    career = next(d for d in data["domains"] if d["domain"] == "career")
    assert 10 in career["primary_bhavas"]
    assert "Sun" in career["karakas"]


def test_get_evidence_schema_endpoint(client):
    res = client.get("/api/v1/evidence/schema")
    assert res.status_code == 200
    schema = res.json()
    assert "title" in schema
    assert schema["title"] == "EvidencePack"
    assert "properties" in schema
    assert "findings" in schema["properties"]
    assert "domain" in schema["properties"]


def test_generate_evidence_pack_endpoint_success(client, sample_birth_payload):
    res = client.post("/api/v1/evidence/pack", json=sample_birth_payload)
    assert res.status_code == 200
    data = res.json()

    # Validate against EvidencePack Pydantic model
    pack = EvidencePack.model_validate(data)
    assert pack.domain == "career"
    assert pack.school == "parashari"
    assert len(pack.findings) > 0

    # Ensure findings have provenance and no hallucinated free text
    for f in pack.findings:
        assert f.finding_id.startswith("F")
        assert f.claim_en != ""
        assert f.claim_hi != ""
        assert 0.0 <= f.strength <= 1.0
        if f.source_ref:
            assert f.source_ref.grantha != ""


def test_generate_evidence_pack_invalid_domain(client, sample_birth_payload):
    payload = dict(sample_birth_payload)
    payload["domain"] = "alien_abduction"

    res = client.post("/api/v1/evidence/pack", json=payload)
    assert res.status_code == 400
    assert "Unsupported domain" in res.json()["detail"]


def test_extract_chart_factors_endpoint(client, sample_birth_payload):
    res = client.post("/api/v1/evidence/factors?ayanamsa=Lahiri", json=sample_birth_payload["birth_data"])
    assert res.status_code == 200
    factors = res.json()
    assert "planets" in factors
    assert "houses" in factors
    assert "Sun" in factors["planets"]
    assert "Jupiter" in factors["planets"]
    assert "1" in factors["houses"]

