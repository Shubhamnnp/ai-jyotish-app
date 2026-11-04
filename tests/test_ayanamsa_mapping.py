"""
Test suite for Ayanamsa Mapping and Validation (Phase 1 Task P1-T3).
Verifies:
1. Exact mapping of supported ayanamsa names to Swiss sidereal modes.
2. Every supported mode matches direct swe.get_ayanamsa_ut calculations.
3. Unknown ayanamsa name raises ValueError (zero silent fallback to Lahiri).
4. API endpoint /api/v1/astronomy/ayanamsas exposes all supported modes.
"""

import pytest
import swisseph as swe
from fastapi.testclient import TestClient
from src.jyotish.core.ephemeris import (
    SUPPORTED_AYANAMSAS,
    AYANAMSA_ALIASES,
    resolve_ayanamsa_mode,
    SwissEphemerisProvider,
    PyEphemProvider,
)
from src.jyotish.api.main import app


def test_every_supported_ayanamsa_matches_swiss_ephemeris():
    """Verify calculate_ayanamsa produces identical results to direct swe.get_ayanamsa_ut for every mode."""
    provider = SwissEphemerisProvider()
    jd = swe.julday(2000, 1, 1, 12.0)

    for name, (mode_code, description) in SUPPORTED_AYANAMSAS.items():
        # Direct calculation from Swiss
        swe.set_sid_mode(mode_code)
        expected_val = float(swe.get_ayanamsa_ut(jd))

        # Calculation via Jyotish provider
        calc_val = provider.calculate_ayanamsa(jd, name)

        assert abs(calc_val - expected_val) < 1e-9, (
            f"Ayanamsa mismatch for {name} (code {mode_code}): expected {expected_val}, got {calc_val}"
        )


def test_ayanamsa_aliases_resolution():
    """Verify common user/client aliases resolve to expected canonical modes."""
    aliases_to_test = {
        "kp": "Krishnamurti",
        "krishnamurti": "Krishnamurti",
        "bv_raman": "Raman",
        "chitra_paksha": "Lahiri",
        "pushya_paksha": "True_Pushya",
        "true_chitra": "True_Citra",
        "fagan": "Fagan_Bradley",
        "sri_yukteshwar": "Yukteshwar",
        "bhasin": "JN_Bhasin",
    }

    for alias, expected_canonical in aliases_to_test.items():
        canonical, code = resolve_ayanamsa_mode(alias)
        assert canonical == expected_canonical
        assert code == SUPPORTED_AYANAMSAS[expected_canonical][0]


def test_unknown_ayanamsa_raises_value_error():
    """Verify unknown ayanamsa name raises ValueError rather than silently defaulting."""
    provider = SwissEphemerisProvider()
    jd = 2451545.0

    with pytest.raises(ValueError) as exc_info:
        resolve_ayanamsa_mode("NonExistentAyanamsa")
    assert "Unknown ayanamsa 'NonExistentAyanamsa'" in str(exc_info.value)
    assert "Supported ayanamsas are:" in str(exc_info.value)

    with pytest.raises(ValueError):
        provider.calculate_ayanamsa(jd, "FantasyAyanamsa")

    pyephem = PyEphemProvider()
    with pytest.raises(ValueError):
        pyephem.calculate_ayanamsa(jd, "FantasyAyanamsa")


def test_default_ayanamsa_is_lahiri():
    """Verify None or empty string defaults to Lahiri."""
    canonical_none, code_none = resolve_ayanamsa_mode(None)
    assert canonical_none == "Lahiri"
    assert code_none == 1

    canonical_empty, code_empty = resolve_ayanamsa_mode("")
    assert canonical_empty == "Lahiri"
    assert code_empty == 1


def test_api_ayanamsas_list_endpoint():
    """Verify GET /api/v1/astronomy/ayanamsas returns the complete list of supported modes."""
    client = TestClient(app)
    response = client.get("/api/v1/astronomy/ayanamsas")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == len(SUPPORTED_AYANAMSAS)

    names = {item["name"] for item in data}
    assert "Lahiri" in names
    assert "Raman" in names
    assert "Krishnamurti" in names
    assert "True_Citra" in names
    assert "True_Pushya" in names

    # Verify Lahiri J2000 value
    lahiri_entry = next(item for item in data if item["name"] == "Lahiri")
    assert abs(lahiri_entry["reference_j2000_degrees"] - 23.857092) < 0.0001

