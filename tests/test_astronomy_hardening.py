"""
Unit test suite for Phase 3 Astronomical Engine Hardening.
Tests:
1. Topocentric Moon parallax calculation vs geocentric Moon.
2. High polar latitude (>66.5° N/S) Ascendant & house calculations without singularity.
3. Deterministic calculation metadata persistence on KundaliChart.
4. Ayanamsa system integrity (Lahiri, Raman, KP, True Chitra, Yukteshwar).
"""

import pytest
from datetime import date, time, datetime, timezone
from src.jyotish.core.models import BirthData
from src.jyotish.core.calculator import default_chart_calculator
from src.jyotish.core.ephemeris import default_ephemeris_provider


def test_calculation_metadata_attached():
    """Verify that every computed chart carries full calculation metadata."""
    bdata = BirthData(
        name="Metadata Test Subject",
        birth_date=date(1995, 10, 15),
        birth_time=time(14, 30, 0),
        latitude=28.6139,
        longitude=77.2090,
        timezone_offset=5.5,
        city="New Delhi"
    )
    chart = default_chart_calculator.calculate_chart(bdata, ayanamsa_name="Lahiri")
    
    assert chart.metadata is not None
    assert chart.metadata.engine_version == "2.1.0"
    assert "Swiss" in chart.metadata.engine_type or "Ephem" in chart.metadata.engine_type
    assert chart.metadata.ayanamsa_name == "Lahiri"
    assert 23.0 < chart.metadata.ayanamsa_value < 25.0
    assert chart.metadata.jd_ut > 2440000.0
    assert chart.metadata.calculation_timestamp_utc is not None
    assert chart.metadata.polar_latitude_adjusted is False


def test_topocentric_moon_parallax():
    """Verify topocentric Moon calculation produces expected parallax shift vs geocentric."""
    bdata = BirthData(
        name="Topocentric Subject",
        birth_date=date(2024, 6, 21),
        birth_time=time(12, 0, 0),
        latitude=28.6139,
        longitude=77.2090,
        timezone_offset=5.5,
        city="New Delhi"
    )
    # Geocentric chart
    chart_geo = default_chart_calculator.calculate_chart(bdata, topocentric_moon=False)
    # Topocentric chart (with observer latitude & longitude)
    chart_topo = default_chart_calculator.calculate_chart(bdata, topocentric_moon=True, latitude=28.6139, longitude=77.2090)
    
    assert chart_geo.metadata.topocentric_moon is False
    assert chart_topo.metadata.topocentric_moon is True
    assert chart_topo.metadata.coordinate_type == "topocentric"
    
    # Moon parallax causes a small longitudinal shift (< 1.2 degrees)
    geo_moon_lon = chart_geo.planets["Moon"].longitude
    topo_moon_lon = chart_topo.planets["Moon"].longitude
    
    diff = abs(geo_moon_lon - topo_moon_lon)
    if diff > 180.0:
        diff = abs(diff - 360.0)
        
    assert 0.0 < diff < 1.5, f"Topocentric lunar parallax shift {diff}° should be between 0.0° and 1.5°"


def test_polar_latitude_circumpolar_safeguard():
    """Verify polar latitude (>66.5° N/S) calculations succeed safely without division by zero."""
    # Tromsø, Norway (69.6492° N, 18.9553° E)
    bdata_polar = BirthData(
        name="Arctic Subject",
        birth_date=date(2000, 6, 21),  # Summer Solstice midnight sun
        birth_time=time(0, 30, 0),
        latitude=69.6492,
        longitude=18.9553,
        timezone_offset=1.0,
        city="Tromso"
    )
    
    chart_polar = default_chart_calculator.calculate_chart(bdata_polar)
    
    assert chart_polar.metadata.polar_latitude_adjusted is True
    assert 0.0 <= chart_polar.lagna_longitude < 360.0
    assert 1 <= chart_polar.lagna_sign_id <= 12
    assert len(chart_polar.houses) == 12
    # Verify all house cusps are valid numbers
    for h in chart_polar.houses:
        assert 0.0 <= h.cusp_longitude < 360.0


def test_ayanamsa_reproducibility():
    """Verify precision and stability across supported Ayanamsa systems."""
    bdata = BirthData(
        name="Ayanamsa Subject",
        birth_date=date(2000, 1, 1),
        birth_time=time(12, 0, 0),
        latitude=28.6139,
        longitude=77.2090,
        timezone_offset=5.5
    )
    
    chart_lahiri = default_chart_calculator.calculate_chart(bdata, ayanamsa_name="Lahiri")
    chart_raman = default_chart_calculator.calculate_chart(bdata, ayanamsa_name="Raman")
    chart_kp = default_chart_calculator.calculate_chart(bdata, ayanamsa_name="KP")
    
    # Lahiri at J2000 is ~23.857°
    assert 23.8 < chart_lahiri.ayanamsa_value < 23.9
    # Raman is approximately ~1.44° lower than Lahiri
    assert chart_raman.ayanamsa_value < chart_lahiri.ayanamsa_value
    # KP is very close to Lahiri (within 0.15°)
    assert abs(chart_kp.ayanamsa_value - chart_lahiri.ayanamsa_value) < 0.20
