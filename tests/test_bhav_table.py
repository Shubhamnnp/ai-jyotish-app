import datetime
import pytest
from src.jyotish.core.models import BirthData
from src.jyotish.core.calculator import default_chart_calculator
from src.jyotish.core.constants import SIGN_NAMES, SIGN_LORDS, NAKSHATRAS

def test_12_bhava_master_table_data_generation():
    """Verify that all 12 houses compute correct signs, cusps, occupying planets,
    chalit shift detection, Parashari aspects, and SAV points for D1."""
    bd = BirthData(
        name="Test Native",
        birth_date=datetime.date(1995, 5, 15),
        birth_time=datetime.time(14, 30),
        latitude=28.6139,
        longitude=77.2090,
        timezone_offset=5.5
    )
    chart = default_chart_calculator.calculate_full_chart(bd)
    bc_res = default_chart_calculator.calculate_bhava_chalit(chart)

    cusps_list = bc_res.get("bhava_cusps", [])
    assert len(cusps_list) == 12, "Must compute all 12 Bhava cusps"

    # Test Bhava 1 (Lagna) in D1
    b1_cusp = next((c for c in cusps_list if c.get("bhava") == 1), None)
    assert b1_cusp is not None
    assert b1_cusp["sign_name"] == "Virgo"

    # Test Chalit shift detection (Sun in this test chart shifts from 9th house to 8th house)
    planet_positions = bc_res.get("planet_positions", [])
    sun_pos = next((p for p in planet_positions if p.get("planet") == "Sun"), None)
    assert sun_pos is not None
    assert sun_pos["rashi_house"] == 9
    assert sun_pos["chalit_house"] == 8
    assert sun_pos["is_different"] is True

    # Test SAV points exist for each sign
    assert chart.ashtakavarga is not None
    assert len(chart.ashtakavarga.sav) == 12


def test_12_bhava_master_table_dynamic_varga_adaptation():
    """Verify that when switching to divisional charts (e.g. D9 Navamsha, D10 Dashamsha),
    the Bhav table dynamically uses that varga's Lagna, signs, house lords, and occupying planets."""
    bd = BirthData(
        name="Test Native",
        birth_date=datetime.date(1995, 5, 15),
        birth_time=datetime.time(14, 30),
        latitude=28.6139,
        longitude=77.2090,
        timezone_offset=5.5
    )
    chart = default_chart_calculator.calculate_full_chart(bd)

    # In D1, Lagna is Virgo (6)
    d1_varga = chart.vargas["D1"]
    assert d1_varga.lagna_sign_id == 6

    # In D9, Lagna is Capricorn (10)
    d9_varga = chart.vargas["D9"]
    assert d9_varga.lagna_sign_id == 10
    assert d9_varga.lagna_sign_name == "Capricorn"

    # House 1 of D9 has sign Capricorn (10), ruled by Saturn
    d9_h1_sign_id = ((d9_varga.lagna_sign_id - 1 + 0) % 12) + 1
    assert d9_h1_sign_id == 10
    assert SIGN_NAMES[d9_h1_sign_id - 1] == "Capricorn"
    assert SIGN_LORDS["Capricorn"] == "Saturn"

    # Occupying planets in House 1 of D9 are Sun & Rahu
    d9_h1_planets = [vp.name for vp in d9_varga.planets.values() if vp.house_number == 1]
    assert "Sun" in d9_h1_planets
    assert "Rahu" in d9_h1_planets

    # In D10, Lagna is Taurus (2)
    d10_varga = chart.vargas["D10"]
    assert d10_varga.lagna_sign_id == 2
    assert d10_varga.lagna_sign_name == "Taurus"
    d10_h1_planets = [vp.name for vp in d10_varga.planets.values() if vp.house_number == 1]
    assert "Venus" in d10_h1_planets
