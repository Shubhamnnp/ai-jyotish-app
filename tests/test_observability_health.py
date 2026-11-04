"""
Unit tests for Observability, Request Tracing, PII Scrubbing, and Health Monitoring (Phase 6, Task P6-T5).
Reference: docs/IMPLEMENTATION_PRD.md (Section 6.5, P6-T5).
"""

import pytest
from fastapi.testclient import TestClient
from src.jyotish.api.main import app
from src.jyotish.api.middleware import scrub_pii


@pytest.fixture
def client():
    return TestClient(app)


def test_request_id_generation_and_propagation(client):
    # Case 1: Client does not supply X-Request-ID
    res1 = client.get("/health")
    assert res1.status_code == 200
    req_id1 = res1.headers.get("X-Request-ID")
    assert req_id1 is not None
    assert req_id1.startswith("req_")

    # Case 2: Client supplies custom X-Request-ID
    custom_id = "trace-client-12345-abc"
    res2 = client.get("/health", headers={"X-Request-ID": custom_id})
    assert res2.status_code == 200
    assert res2.headers.get("X-Request-ID") == custom_id


def test_process_time_header_present(client):
    res = client.get("/health")
    assert res.status_code == 200
    proc_time = res.headers.get("X-Process-Time")
    assert proc_time is not None
    assert proc_time.endswith("ms")


def test_pii_scrubber_redacts_sensitive_keys():
    test_payload = {
        "name": "Devadatta",
        "birth_name": "Deva",
        "birth_date": "1995-10-24",
        "birth_time": "08:15:00",
        "ayanamsa": "Lahiri",
        "latitude": 28.6139,
        "longitude": 77.2090,
        "nested": {
            "email": "user@example.com",
            "password": "secretpassword",
            "school": "parashari"
        },
        "list_of_records": [
            {"phone": "+919876543210", "plan": "pro"}
        ]
    }

    scrubbed = scrub_pii(test_payload)
    assert scrubbed["name"] == "[REDACTED_PII]"
    assert scrubbed["birth_name"] == "[REDACTED_PII]"
    assert scrubbed["birth_date"] == "[REDACTED_PII]"
    assert scrubbed["birth_time"] == "[REDACTED_PII]"
    assert scrubbed["ayanamsa"] == "Lahiri"
    assert scrubbed["latitude"] == 28.6139

    # Nested check
    assert scrubbed["nested"]["email"] == "[REDACTED_PII]"
    assert scrubbed["nested"]["password"] == "[REDACTED_PII]"
    assert scrubbed["nested"]["school"] == "parashari"

    # List check
    assert scrubbed["list_of_records"][0]["phone"] == "[REDACTED_PII]"
    assert scrubbed["list_of_records"][0]["plan"] == "pro"


def test_system_health_endpoint(client):
    for path in ("/health", "/api/v1/health"):
        res = client.get(path)
        assert res.status_code == 200
        data = res.json()
        assert data["status"] in ("healthy", "degraded")
        assert "uptime_seconds" in data
        assert data["uptime_seconds"] >= 0
        assert "timestamp" in data
        assert "engine_degraded" in data
        assert isinstance(data["engine_degraded"], bool)

        # Ephemeris health
        assert "ephemeris" in data
        assert "ephemeris_mode" in data["ephemeris"]

        # Rules health
        assert "rules" in data
        assert "scholar_verified" in data["rules"]
        assert "draft" in data["rules"]

        # System health
        assert "system" in data
        assert "memory_rss_mb" in data["system"]


def test_engine_health_endpoint(client):
    for path in ("/health/engine", "/api/v1/health/engine"):
        res = client.get(path)
        assert res.status_code == 200
        data = res.json()
        assert "ephemeris_mode" in data
        assert "self_test" in data
        assert data["self_test"] == "passed"

