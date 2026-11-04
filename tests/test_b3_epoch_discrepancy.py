"""
Test suite for PRD Finding B3 / Task P1-T4:
Verifies and quantifies the epoch drift between PyEphem and Swiss Ephemeris.
Codifies the requirement that PyEphem standalone path is declared unsupported
for high-precision Jyotish due to epoch drift exceeding the 0.02° tolerance threshold.
"""

import pytest
import datetime
from src.jyotish.core.ephemeris import PyEphemProvider, SwissEphemerisProvider
from scripts.investigate_b3_epoch import run_investigation


def test_b3_epoch_investigation_run():
    """Verify that the B3 investigation runs across 21 dates spanning 1950-2050."""
    result = run_investigation()
    assert len(result["records"]) == 21
    assert result["max_sun_error_deg"] > 0.5, "Expected significant epoch drift (>0.5 deg) away from J2000"
    assert result["max_moon_error_deg"] > 0.5
    assert result["max_jupiter_error_deg"] > 0.5
    # PyEphem must be declared unsupported for professional tolerance
    assert result["pyephem_supported"] is False


def test_j2000_minimal_epoch_drift():
    """Verify that around J2000.0 epoch, PyEphem and Swiss are relatively close (< 0.02 deg)."""
    py_prov = PyEphemProvider()
    sw_prov = SwissEphemerisProvider()
    dt_j2000 = datetime.datetime(2000, 1, 1, 12, 0, tzinfo=datetime.timezone.utc)

    p_py, _ = py_prov.get_planet_positions(dt_j2000, ayanamsa_name="Lahiri")
    p_sw, _ = sw_prov.get_planet_positions(dt_j2000, ayanamsa_name="Lahiri")

    diff_sun = abs(p_py["Sun"]["longitude"] - p_sw["Sun"]["longitude"])
    diff_moon = abs(p_py["Moon"]["longitude"] - p_sw["Moon"]["longitude"])

    assert diff_sun < 0.02, f"Sun error at J2000 is {diff_sun}°"
    assert diff_moon < 0.02, f"Moon error at J2000 is {diff_moon}°"


def test_1950_excessive_epoch_drift_proves_b3():
    """Verify that at 1950, PyEphem drifts by > 0.65 degrees (~2400 arcsec), proving B3."""
    py_prov = PyEphemProvider()
    sw_prov = SwissEphemerisProvider()
    dt_1950 = datetime.datetime(1950, 1, 15, 12, 0, tzinfo=datetime.timezone.utc)

    p_py, _ = py_prov.get_planet_positions(dt_1950, ayanamsa_name="Lahiri")
    p_sw, _ = sw_prov.get_planet_positions(dt_1950, ayanamsa_name="Lahiri")

    diff_sun = abs(p_py["Sun"]["longitude"] - p_sw["Sun"]["longitude"])
    assert diff_sun > 0.65, f"Sun error at 1950 was expected to be > 0.65°, got {diff_sun}°"
