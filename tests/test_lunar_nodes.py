"""
Test suite for Lunar Nodes (Phase 1 Task P1-T5).
Verifies:
1. Swiss MEAN_NODE and TRUE_NODE calculation precision.
2. Dynamic node speed from Swiss Ephemeris FLG_SPEED (no hardcoded constants).
3. Exact Ketu = (Rahu + 180°) % 360° opposition invariant.
4. Dynamic direct vs retrograde detection for True Lunar Nodes.
"""

import pytest
import datetime
import swisseph as swe
from src.jyotish.core.ephemeris import SwissEphemerisProvider


def test_mean_node_calculation():
    """Verify Mean Node longitude and speed match direct Swiss swe.MEAN_NODE."""
    provider = SwissEphemerisProvider()
    dt = datetime.datetime(2024, 1, 1, 12, 0, tzinfo=datetime.timezone.utc)
    jd = provider.datetime_to_jd(dt)

    # Direct Swiss calculation
    swe.set_sid_mode(1)
    flg = swe.FLG_SWIEPH | swe.FLG_SPEED | swe.FLG_SIDEREAL
    direct_res = swe.calc_ut(jd, swe.MEAN_NODE, flg)[0]

    positions, ayanamsa = provider.get_planet_positions(dt, ayanamsa_name="Lahiri", node_type="mean")

    rahu = positions["Rahu"]
    ketu = positions["Ketu"]

    assert abs(rahu["longitude"] - direct_res[0] % 360.0) < 1e-6
    assert abs(rahu["speed"] - direct_res[3]) < 1e-6
    assert rahu["speed"] < 0.0  # Mean node always moves retrograde
    assert rahu["is_retrograde"] is True

    # Ketu 180 deg opposition invariant
    expected_ketu = (rahu["longitude"] + 180.0) % 360.0
    assert abs(ketu["longitude"] - expected_ketu) < 1e-6
    assert ketu["speed"] == rahu["speed"]
    assert ketu["is_retrograde"] is True


def test_true_node_calculation_and_direct_motion():
    """Verify True Node calculation, varying speed, and direct motion support."""
    provider = SwissEphemerisProvider()

    # Test date where True Node is moving direct (day 4 of Jan 2024 has speed > 0)
    dt_direct = datetime.datetime(2024, 1, 4, 12, 0, tzinfo=datetime.timezone.utc)
    jd_direct = provider.datetime_to_jd(dt_direct)

    swe.set_sid_mode(1)
    flg = swe.FLG_SWIEPH | swe.FLG_SPEED | swe.FLG_SIDEREAL
    direct_res = swe.calc_ut(jd_direct, swe.TRUE_NODE, flg)[0]

    positions, _ = provider.get_planet_positions(dt_direct, ayanamsa_name="Lahiri", node_type="true")
    rahu = positions["Rahu"]
    ketu = positions["Ketu"]

    assert abs(rahu["longitude"] - direct_res[0] % 360.0) < 1e-6
    assert abs(rahu["speed"] - direct_res[3]) < 1e-6

    # Verify that on direct station, speed > 0 and is_retrograde is False
    assert direct_res[3] > 0.0
    assert rahu["speed"] > 0.0
    assert rahu["is_retrograde"] is False
    assert ketu["is_retrograde"] is False

    # Check Ketu opposition
    assert abs(ketu["longitude"] - (rahu["longitude"] + 180.0) % 360.0) < 1e-6


def test_true_vs_mean_node_discrepancy():
    """Verify True Node oscillates around Mean Node within astronomical bounds (< 2 degrees)."""
    provider = SwissEphemerisProvider()
    dt = datetime.datetime(2024, 6, 15, 12, 0, tzinfo=datetime.timezone.utc)

    pos_mean, _ = provider.get_planet_positions(dt, ayanamsa_name="Lahiri", node_type="mean")
    pos_true, _ = provider.get_planet_positions(dt, ayanamsa_name="Lahiri", node_type="true")

    rahu_mean = pos_mean["Rahu"]["longitude"]
    rahu_true = pos_true["Rahu"]["longitude"]

    diff = abs(rahu_mean - rahu_true) % 360.0
    if diff > 180.0:
        diff = 360.0 - diff

    # True node deviates from mean node by up to ~1.75 degrees
    assert 0.001 < diff < 2.0, f"True-Mean nodal deviation {diff}° should be between 0.001° and 2.0°"

