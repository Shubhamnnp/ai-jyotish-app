"""
Test suite for Swiss Ephemeris Engine (Phase 1 Task P1-T1).
Verifies:
1. Hard requirement of Swiss Ephemeris engine (swisseph/pysweph/pyswisseph).
2. Ephemeris startup self-test (Sun longitude at J2000.0).
3. /health/engine API endpoint reporting engine mode and files found.
4. High-precision astronomical calculation without silent fallback errors.
"""

import pytest
from fastapi.testclient import TestClient
from src.jyotish.core.ephemeris import (
    SwissEphemerisProvider,
    get_ephemeris_provider,
    get_engine_health,
    default_ephemeris_provider,
    EphemerisUnavailable,
)
from src.jyotish.api.main import app


def test_swisseph_provider_instantiation_and_self_test():
    """Verify SwissEphemerisProvider initializes and passes J2000 self-test."""
    provider = SwissEphemerisProvider()
    assert provider._has_swisseph is True
    assert provider._swe is not None

    test_res = provider.run_self_test()
    assert test_res["status"] == "passed", f"Self-test failed: {test_res}"
    assert "Sun sidereal longitude at J2000.0" in test_res["test"]
    assert abs(test_res["calculated_longitude"] - 256.515697) < 0.001
    assert test_res["daily_speed"] > 0.95


def test_default_ephemeris_provider_is_swiss():
    """Verify that auto-selection defaults to SwissEphemerisProvider."""
    provider = get_ephemeris_provider("auto")
    assert isinstance(provider, SwissEphemerisProvider)
    assert default_ephemeris_provider.engine_type.startswith("Swiss Ephemeris")


def test_get_engine_health_structure():
    """Verify get_engine_health returns complete diagnostic payload."""
    health = get_engine_health()
    assert health["engine"] == "swisseph"
    assert "version" in health
    assert "ephe_path" in health
    assert "ephe_files_count" in health
    assert "ephemeris_mode" in health
    assert health["self_test"] == "passed"
    assert "self_test_details" in health


def test_api_health_engine_endpoint():
    """Verify GET /health/engine endpoint via FastAPI test client."""
    client = TestClient(app)
    response = client.get("/health/engine")
    assert response.status_code == 200
    data = response.json()
    assert data["engine"] == "swisseph"
    assert data["self_test"] == "passed"
    assert "ephemeris_mode" in data
    assert "version" in data


def test_api_root_reports_swiss_ephemeris():
    """Verify GET / reports the active Swiss Ephemeris engine mode."""
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "Swiss Ephemeris" in data["ephemeris"]
    assert data["engine_health"] == "passed"

