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
    assert provider.engine_type.startswith("Swiss")


def test_moshier_mode_labeling_without_de431_files():
    """Verify Moshier analytical mode is strictly labelled 'Swiss (Moshier)' and not DE431."""
    provider = SwissEphemerisProvider()
    if provider.ephe_files_count == 0:
        assert provider.ephemeris_mode == "Swiss (Moshier)"
        assert provider.engine_type == "Swiss (Moshier)"
        assert "DE431" not in provider.ephemeris_mode


def test_no_silent_fallback_raises_ephemeris_unavailable(monkeypatch):
    """Verify that when Swiss is unavailable and ALLOW_DEGRADED_ENGINE is false, EphemerisUnavailable is raised."""
    monkeypatch.setenv("ALLOW_DEGRADED_ENGINE", "false")
    provider = SwissEphemerisProvider()
    provider._has_swisseph = False

    from datetime import datetime, timezone
    dt = datetime(2024, 1, 1, 12, 0, tzinfo=timezone.utc)

    with pytest.raises(EphemerisUnavailable) as exc_info:
        provider.get_planet_positions(dt)
    assert "ALLOW_DEGRADED_ENGINE=true" in str(exc_info.value)

    with pytest.raises(EphemerisUnavailable):
        provider.calculate_ayanamsa(2451545.0)

    with pytest.raises(EphemerisUnavailable):
        provider.calculate_ascendant(dt, 28.61, 77.20, 24.0)


def test_allowed_degraded_engine_sets_degraded_flag(monkeypatch):
    """Verify that when ALLOW_DEGRADED_ENGINE is true, PyEphem fallback sets engine_degraded=True."""
    monkeypatch.setenv("ALLOW_DEGRADED_ENGINE", "true")
    provider = SwissEphemerisProvider()
    provider._has_swisseph = False

    from datetime import datetime, timezone
    dt = datetime(2024, 1, 1, 12, 0, tzinfo=timezone.utc)

    positions, ayanamsa = provider.get_planet_positions(dt)
    assert "Sun" in positions
    assert provider.is_degraded is True
    assert provider.ephemeris_mode == "PyEphem (Degraded)"


def test_chart_calculator_attaches_engine_degraded_flag():
    """Verify ChartCalculator attaches engine_degraded boolean to KundaliChart and CalculationMetadata."""
    from src.jyotish.core.calculator import ChartCalculator
    from src.jyotish.core.ephemeris import PyEphemProvider
    from src.jyotish.core.models import BirthData
    from datetime import date, time

    bdata = BirthData(
        name="Degradation Test",
        birth_date=date(1990, 5, 20),
        birth_time=time(10, 15, 0),
        latitude=28.6139,
        longitude=77.2090,
        timezone_offset=5.5,
        city="New Delhi"
    )

    # Calculate with Swiss (non-degraded)
    swiss_calc = ChartCalculator()
    chart_swiss = swiss_calc.calculate_chart(bdata)
    assert chart_swiss.engine_degraded is False
    assert chart_swiss.metadata.engine_degraded is False

    # Calculate with PyEphem (degraded fallback)
    degraded_calc = ChartCalculator(ephem_provider=PyEphemProvider())
    chart_degraded = degraded_calc.calculate_chart(bdata)
    assert chart_degraded.engine_degraded is True
    assert chart_degraded.metadata.engine_degraded is True
    assert chart_degraded.metadata.ephemeris_mode == "PyEphem (Degraded)"


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
    assert "Swiss" in data["ephemeris"]
    assert data["engine_health"] == "passed"

