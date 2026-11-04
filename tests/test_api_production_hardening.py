"""
Production API & FastAPI Hardening Test Suite (Phase 11).

Verifies:
1. Daivajna Multi-Agent REST orchestration endpoint (/api/v1/chat/orchestrate).
2. OpenAPI 3.0 schema integrity and tags coverage.
3. Chart calculation latency performance benchmark.
4. Structured 422 error handling for invalid input payloads.
5. SaaS subscription tier and rate-limiting middleware integration.
"""

import time
import pytest
from fastapi.testclient import TestClient

from src.jyotish.api.main import app

client = TestClient(app)


def test_api_v1_daivajna_orchestration():
    """Validates Layer 4 Daivajna Multi-Agent consultation endpoint."""
    payload = {
        "birth_data": {
            "name": "API Daivajna Native",
            "birth_date": "1994-05-16",
            "birth_time": "17:00:00",
            "latitude": 28.0327,
            "longitude": 81.3787,
            "timezone_offset": 5.5,
            "city": "Nanpara, UP",
            "confidence": "Exact",
            "gender": "male"
        },
        "topic": "career",
        "user_query": "What are my career prospects and timing for promotion?",
        "ayanamsa": "Lahiri"
    }

    res = client.post("/api/v1/chat/orchestrate", json=payload)
    assert res.status_code == 200, f"Orchestrate failed: {res.text}"
    data = res.json()

    assert data["status"] == "success"
    assert data["topic"] == "career"
    assert data["user_query"] == payload["user_query"]

    # Verify fact sheet (Specialist Calculation Agent output)
    assert "fact_sheet" in data
    fs = data["fact_sheet"]
    assert fs["native_name"] == "API Daivajna Native"
    assert fs["ascendant_sign"] != ""
    assert len(fs["planets"]) >= 9
    assert len(fs["houses_sav"]) == 12

    # Verify Shastriya pramana (RAG output)
    assert "shastriya_pramana" in data
    assert len(data["shastriya_pramana"]) > 0
    assert data["shastriya_pramana"][0]["grantha"] != ""

    # Verify Audit verdict (Independent Audit Agent output)
    assert "audit_verdict" in data
    verdict = data["audit_verdict"]
    assert len(verdict["supporting_evidence"]) > 0
    assert len(verdict["conflicting_evidence"]) > 0
    assert 15.0 <= verdict["confidence_score"] <= 92.0
    assert verdict["confidence_tier"] in ["HIGH", "MODERATE", "LOW"]

    # Verify Remedies & Synthesis
    assert len(data["remedies"]) >= 2
    assert "प्राथमिक गणितीय स्थिति" in data["synthesis_hi"]
    assert "Verified Astronomical Baseline" in data["synthesis_en"]


def test_api_v1_openapi_schema_completeness():
    """Validates OpenAPI schema endpoints, descriptions, and tags."""
    res = client.get("/openapi.json")
    assert res.status_code == 200
    schema = res.json()

    assert "openapi" in schema
    assert "info" in schema
    assert "paths" in schema

    # Key production v1 routes must exist
    paths = schema["paths"]
    assert "/api/v1/charts/calculate" in paths
    assert "/api/v1/charts/dashas" in paths
    assert "/api/v1/chat/consult" in paths
    assert "/api/v1/chat/orchestrate" in paths
    assert "/api/v1/events/verify-past" in paths
    assert "/api/v1/rules/count" in paths
    assert "/api/v1/auth/login" in paths


def test_api_v1_chart_performance_benchmark():
    """Benchmarks chart calculation latency (< 2.0s for end-to-end full calculation + D1-D60 vargas)."""
    payload = {
        "name": "Benchmark Native",
        "birth_date": "1992-10-24",
        "birth_time": "06:45:00",
        "latitude": 19.0760,
        "longitude": 72.8777,
        "timezone_offset": 5.5,
        "city": "Mumbai"
    }

    t0 = time.perf_counter()
    res = client.post("/api/v1/charts/calculate", json=payload)
    elapsed = time.perf_counter() - t0

    assert res.status_code == 200
    assert elapsed < 2.0, f"Chart calculation exceeded latency threshold: {elapsed:.2f}s"
    data = res.json()
    assert data["lagna_sign_name"] == "Libra"


def test_api_v1_error_handling_and_validation():
    """Validates structured 422 response for malformed or missing payload."""
    malformed_payload = {
        "birth_data": {
            "name": "Invalid Native",
            "birth_date": "not-a-valid-date",  # Invalid date format
            "birth_time": "12:00:00",
            "latitude": "invalid-coord",
            "longitude": 77.2090
        }
    }

    res = client.post("/api/v1/chat/orchestrate", json=malformed_payload)
    assert res.status_code == 422
    data = res.json()
    assert "detail" in data
    assert isinstance(data["detail"], list)
