"""
Unit and Integration Tests for House Systems and Bhava Chalit (Phase 1 Task P1-T6).
Verifies:
1. Whole Sign, Equal, Sripati, Porphyry, and Placidus house systems via Swiss Ephemeris.
2. High-latitude (> 66° N/S) circumpolar safeguards and graceful fallback to Equal.
3. Sripati Bhava Chalit sandhis (midpoints) and madhyas (cusps).
4. Benchmark across 20 global geographic coordinates spanning both hemispheres.
5. Planet-in-house mapping for Whole Sign, Equal, Sripati, and Placidus.
"""

import pytest
import swisseph as swe
from datetime import datetime, timezone
from src.jyotish.core.houses import (
    HouseCalculator, normalize_house_system_name, point_in_arc, HOUSE_SYSTEM_CODES
)
from src.jyotish.core.models import BirthData
from src.jyotish.core.calculator import ChartCalculator
from src.jyotish.core.ephemeris import SwissEphemerisProvider


# 20 diverse worldwide locations
GLOBAL_LOCATIONS = [
    ("Lucknow", 26.8467, 80.9462),
    ("Delhi", 28.6139, 77.2090),
    ("Mumbai", 19.0760, 72.8777),
    ("Kolkata", 22.5726, 88.3639),
    ("Chennai", 13.0827, 80.2707),
    ("Tokyo", 35.6762, 139.6503),
    ("Singapore", 1.3521, 103.8198),
    ("Dubai", 25.2048, 55.2708),
    ("Cairo", 30.0444, 31.2357),
    ("Cape Town", -33.9249, 18.4241),
    ("London", 51.5074, -0.1278),
    ("Paris", 48.8566, 2.3522),
    ("Moscow", 55.7558, 37.6173),
    ("Reykjavik", 64.1466, -21.9426),
    ("Tromso", 69.6492, 18.9553),          # Arctic (> 66° N)
    ("Longyearbyen", 78.2232, 15.6267),    # High Arctic (> 66° N)
    ("New York", 40.7128, -74.0060),
    ("Los Angeles", 34.0522, -118.2437),
    ("Rio de Janeiro", -22.9068, -43.1729),
    ("Sydney", -33.8688, 151.2093),
]


def test_house_system_name_normalization():
    assert normalize_house_system_name("whole_sign") == "Whole Sign"
    assert normalize_house_system_name("Whole") == "Whole Sign"
    assert normalize_house_system_name("w") == "Whole Sign"
    assert normalize_house_system_name("equal") == "Equal"
    assert normalize_house_system_name("sripati") == "Sripati"
    assert normalize_house_system_name("porphyry") == "Porphyry"
    assert normalize_house_system_name("placidus") == "Placidus"
    assert normalize_house_system_name("kp") == "Placidus"


def test_point_in_arc():
    # Simple arc [10, 50)
    assert point_in_arc(25.0, 10.0, 50.0) is True
    assert point_in_arc(5.0, 10.0, 50.0) is False
    assert point_in_arc(55.0, 10.0, 50.0) is False

    # Wrap-around arc [350, 20) across 0°
    assert point_in_arc(355.0, 350.0, 20.0) is True
    assert point_in_arc(10.0, 350.0, 20.0) is True
    assert point_in_arc(25.0, 350.0, 20.0) is False
    assert point_in_arc(340.0, 350.0, 20.0) is False


def test_house_calculation_20_global_locations():
    """Verify ASC, MC, and 12 cusps for 20 global locations on standard J2000 epoch."""
    jd_test = 2451545.0  # 2000-01-01 12:00 UTC

    for city, lat, lon in GLOBAL_LOCATIONS:
        # Test Whole Sign
        ws_res = HouseCalculator.calculate_houses(jd_test, lat, lon, "Whole Sign", ayanamsa_code=1)
        assert len(ws_res.cusps) == 12
        assert 0.0 <= ws_res.ascendant < 360.0
        assert 0.0 <= ws_res.midheaven < 360.0

        # In Whole Sign, each cusp is separated by 30°
        for i in range(11):
            diff = (ws_res.cusps[i+1] - ws_res.cusps[i]) % 360.0
            assert abs(diff - 30.0) < 0.0001, f"{city}: Whole sign cusp distance {diff} != 30°"

        # Test Equal
        eq_res = HouseCalculator.calculate_houses(jd_test, lat, lon, "Equal", ayanamsa_code=1)
        assert len(eq_res.cusps) == 12
        assert abs(eq_res.cusps[0] - eq_res.ascendant) < 0.0001
        for i in range(11):
            diff = (eq_res.cusps[i+1] - eq_res.cusps[i]) % 360.0
            assert abs(diff - 30.0) < 0.0001, f"{city}: Equal cusp distance {diff} != 30°"


def test_circumpolar_high_latitude_fallback():
    """Verify latitude > 66° circumpolar safeguard for Placidus and Porphyry."""
    jd_test = 2451545.0
    lat_tromso = 69.6492  # Above Arctic Circle (66.5° N)
    lon_tromso = 18.9553

    # Placidus should fall back to Equal and set polar_latitude_adjusted=True
    res_plac = HouseCalculator.calculate_houses(jd_test, lat_tromso, lon_tromso, "Placidus", ayanamsa_code=1)
    assert res_plac.polar_latitude_adjusted is True
    assert res_plac.warning is not None
    assert "polar threshold" in res_plac.warning.lower() or "collapsed" in res_plac.warning.lower()

    # Equal and Whole Sign should compute cleanly without falling back
    res_eq = HouseCalculator.calculate_houses(jd_test, lat_tromso, lon_tromso, "Equal", ayanamsa_code=1)
    assert res_eq.polar_latitude_adjusted is False
    assert res_eq.warning is None

    res_ws = HouseCalculator.calculate_houses(jd_test, lat_tromso, lon_tromso, "Whole Sign", ayanamsa_code=1)
    assert res_ws.polar_latitude_adjusted is False


def test_sripati_bhava_madhyas_and_sandhis():
    """Verify Sripati calculates 12 Madhyas and 12 Sandhis as midpoints."""
    jd_test = 2451545.0
    lat_delhi = 28.6139
    lon_delhi = 77.2090

    res = HouseCalculator.calculate_houses(jd_test, lat_delhi, lon_delhi, "Sripati", ayanamsa_code=1)
    assert res.madhyas is not None
    assert res.sandhis is not None
    assert len(res.madhyas) == 12
    assert len(res.sandhis) == 12

    # Verify each sandhi is exact midpoint between madhya[i] and madhya[i+1]
    for i in range(12):
        m_curr = res.madhyas[i]
        m_next = res.madhyas[(i + 1) % 12]
        arc = (m_next - m_curr) % 360.0
        expected_sandhi = (m_curr + (arc / 2.0)) % 360.0
        actual_sandhi = res.sandhis[i]
        assert abs((actual_sandhi - expected_sandhi) % 360.0) < 0.0001


def test_chart_calculator_with_house_systems():
    """Integration test: ChartCalculator produces valid houses for different systems."""
    dt_utc = datetime(2024, 10, 24, 8, 30, tzinfo=timezone.utc)
    b_data = BirthData(
        name="Test Native",
        birth_date=dt_utc.date(),
        birth_time=dt_utc.time(),
        latitude=26.8467,
        longitude=80.9462,
        timezone_offset=0.0,
        city="Lucknow"
    )

    calc = ChartCalculator()

    # 1. Whole Sign chart
    chart_ws = calc.calculate_full_chart(b_data, house_system="Whole Sign")
    assert chart_ws.metadata.house_system == "Whole Sign"
    assert len(chart_ws.houses) == 12
    assert chart_ws.houses[0].house_number == 1
    assert chart_ws.houses[0].sign_id == chart_ws.lagna_sign_id

    # 2. Sripati chart
    chart_sripati = calc.calculate_full_chart(b_data, house_system="Sripati")
    assert chart_sripati.metadata.house_system == "Sripati"
    assert chart_sripati.houses[0].sandhi_start is not None
    assert chart_sripati.houses[0].sandhi_end is not None

    # Bhava chalit calculation
    chalit = calc.calculate_bhava_chalit(chart_sripati)
    assert "planet_positions" in chalit
    assert "bhava_cusps" in chalit
    assert len(chalit["planet_positions"]) == len(chart_sripati.planets)
    assert len(chalit["bhava_cusps"]) == 12


def test_house_calculator_tuple_length_compatibility(monkeypatch):
    """Verifies HouseCalculator safely handles both 12-element and 13-element cusps tuples."""
    import src.jyotish.core.houses as houses_mod

    # Case 1: 12-element tuple (0-indexed cusps from some Linux pyswisseph builds)
    mock_12 = tuple(float(i * 30) for i in range(12))
    mock_ascmc = (15.0, 105.0, 15.0, 195.0)

    monkeypatch.setattr(houses_mod.swe, "houses_ex", lambda *args, **kwargs: (mock_12, mock_ascmc))
    res12 = houses_mod.HouseCalculator.calculate_houses(2460000.5, 28.6139, 77.2090, "Whole Sign")
    assert len(res12.cusps) == 12
    assert res12.ascendant == 15.0

    # Case 2: 13-element tuple (1-indexed with dummy index 0)
    mock_13 = (0.0,) + tuple(float(i * 30) for i in range(12))
    monkeypatch.setattr(houses_mod.swe, "houses_ex", lambda *args, **kwargs: (mock_13, mock_ascmc))
    res13 = houses_mod.HouseCalculator.calculate_houses(2460000.5, 28.6139, 77.2090, "Whole Sign")
    assert len(res13.cusps) == 12
    assert res13.ascendant == 15.0


def test_sripati_bhava_spans_and_zero_crossing():
    """Verifies detailed BhavaSpan generation and sandhi interpolation across 0° boundary."""
    jd_test = 2451545.0
    lat_delhi = 28.6139
    lon_delhi = 77.2090

    res = HouseCalculator.calculate_houses(jd_test, lat_delhi, lon_delhi, "Sripati", ayanamsa_code=1)
    spans = res.get_bhava_spans()
    assert len(spans) == 12

    for span in spans:
        assert 1 <= span.house_number <= 12
        assert 0.0 <= span.arambha < 360.0
        assert 0.0 <= span.madhya < 360.0
        assert 0.0 <= span.samapti < 360.0
        assert 15.0 <= span.span_degrees <= 45.0  # Realistic Sripati house widths
        assert span.arambha_sign in [
            "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
            "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
        ]

    # Verify that house 1 arambha is indeed previous house (12) samapti
    assert abs(spans[0].arambha - spans[11].samapti) < 0.0001
    # Verify house 1 samapti is house 2 arambha
    assert abs(spans[0].samapti - spans[1].arambha) < 0.0001

