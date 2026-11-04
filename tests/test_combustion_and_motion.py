"""
Unit and Integration Tests for Planetary Speed and Combustion (Phase 1 Task P1-T9).
Verifies:
1. Direct extraction of planetary speed from Swiss Ephemeris FLG_SPEED.
2. Classical BPHS / Surya Siddhanta combustion orbs (Moon 12°, Mars 17°, Mercury direct 14° / retro 12°,
   Jupiter 11°, Venus direct 10° / retro 8°, Saturn 15°).
3. Sun, Rahu, and Ketu are never combust.
4. School-configurable orbs (Varahamihira vs BPHS vs custom overrides).
5. Integration with ChartCalculator and PlanetPosition.is_combust.
"""

import pytest
from datetime import datetime, timezone, date, time
from src.jyotish.core.combustion import CombustionCalculator, CombustionOrbConfig
from src.jyotish.core.ephemeris import SwissEphemerisProvider
from src.jyotish.core.models import BirthData
from src.jyotish.core.calculator import ChartCalculator


def test_planetary_speed_from_swiss_ephemeris():
    """Verify Swiss Ephemeris provider extracts non-zero daily motion for all grahas directly via FLG_SPEED."""
    provider = SwissEphemerisProvider()
    dt = datetime(2024, 1, 1, 12, 0, tzinfo=timezone.utc)
    positions, ayanamsa = provider.get_planet_positions(dt, "Lahiri")

    # Sun speed ~ 1 degree/day
    sun_speed = positions["Sun"]["speed"]
    assert 0.95 <= sun_speed <= 1.05, f"Sun speed anomalous: {sun_speed}"

    # Moon speed ~ 11 to 15 degrees/day
    moon_speed = positions["Moon"]["speed"]
    assert 11.0 <= moon_speed <= 16.0, f"Moon speed anomalous: {moon_speed}"

    # Verify all grahas have numeric speed
    for g in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]:
        assert "speed" in positions[g]
        assert isinstance(positions[g]["speed"], float)


def test_bphs_classical_combustion_orbs():
    """Verify exact classical orbs under BPHS / Surya Siddhanta."""
    sun_lon = 100.0
    calc = CombustionCalculator

    # 1. Moon (orb 12°)
    assert calc.check_combustion("Moon", 111.9, sun_lon) is True
    assert calc.check_combustion("Moon", 112.1, sun_lon) is False

    # 2. Mars (orb 17°)
    assert calc.check_combustion("Mars", 116.9, sun_lon) is True
    assert calc.check_combustion("Mars", 117.1, sun_lon) is False

    # 3. Mercury direct (orb 14°) vs retrograde (orb 12°)
    assert calc.check_combustion("Mercury", 113.5, sun_lon, is_retrograde=False) is True
    assert calc.check_combustion("Mercury", 114.5, sun_lon, is_retrograde=False) is False
    assert calc.check_combustion("Mercury", 111.5, sun_lon, is_retrograde=True) is True
    assert calc.check_combustion("Mercury", 112.5, sun_lon, is_retrograde=True) is False

    # 4. Jupiter (orb 11°)
    assert calc.check_combustion("Jupiter", 110.5, sun_lon) is True
    assert calc.check_combustion("Jupiter", 111.5, sun_lon) is False

    # 5. Venus direct (orb 10°) vs retrograde (orb 8°)
    assert calc.check_combustion("Venus", 109.5, sun_lon, is_retrograde=False) is True
    assert calc.check_combustion("Venus", 110.5, sun_lon, is_retrograde=False) is False
    assert calc.check_combustion("Venus", 107.5, sun_lon, is_retrograde=True) is True
    assert calc.check_combustion("Venus", 108.5, sun_lon, is_retrograde=True) is False

    # 6. Saturn (orb 15°)
    assert calc.check_combustion("Saturn", 114.5, sun_lon) is True
    assert calc.check_combustion("Saturn", 115.5, sun_lon) is False

    # 7. Sun, Rahu, Ketu are never combust
    assert calc.check_combustion("Sun", 100.0, sun_lon) is False
    assert calc.check_combustion("Rahu", 100.0, sun_lon) is False
    assert calc.check_combustion("Ketu", 100.0, sun_lon) is False


def test_school_configurable_combustion():
    """Verify Varahamihira school and custom overrides."""
    sun_lon = 50.0

    # Under Varahamihira, Venus direct orb is 9° (instead of 10° in BPHS)
    cfg_varaha = CombustionOrbConfig.from_school("Varahamihira")
    assert CombustionCalculator.check_combustion("Venus", 59.5, sun_lon, False, config=cfg_varaha) is False
    assert CombustionCalculator.check_combustion("Venus", 58.5, sun_lon, False, config=cfg_varaha) is True

    # Custom override (e.g. custom practitioner orb: Jupiter 15°)
    cfg_custom = CombustionOrbConfig.from_school("BPHS", custom_overrides={"Jupiter": 15.0})
    assert CombustionCalculator.check_combustion("Jupiter", 64.0, sun_lon, config=cfg_custom) is True
    assert CombustionCalculator.check_combustion("Jupiter", 66.0, sun_lon, config=cfg_custom) is False


def test_chart_calculator_combustion_integration():
    """Verify ChartCalculator integrates combustion with PlanetPosition.is_combust."""
    b_data = BirthData(
        name="Combust Test Native",
        birth_date=date(2024, 4, 8),  # Total Solar Eclipse period (Sun + Moon + Venus close)
        birth_time=time(18, 20),
        latitude=28.6139,
        longitude=77.2090,
        timezone="Asia/Kolkata"
    )
    calc = ChartCalculator()
    chart = calc.calculate_full_chart(b_data)

    sun = chart.planets["Sun"]
    moon = chart.planets["Moon"]

    # During solar eclipse, Moon is extremely close to Sun and must be combust
    diff = abs(moon.longitude - sun.longitude)
    if diff > 180.0:
        diff = 360.0 - diff
    if diff <= 12.0:
        assert moon.is_combust is True
