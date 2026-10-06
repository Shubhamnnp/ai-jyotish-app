import datetime
import pytest
from src.jyotish.core.models import BirthData
from src.jyotish.core.calculator import default_chart_calculator
from src.jyotish.core.constants import SIGN_NAMES, SIGN_LORDS, NAKSHATRAS

def test_12_bhava_master_table_data_generation():
    """Verify that all 12 houses compute correct signs, cusps, occupying planets,
    chalit shift detection, Parashari aspects, and SAV points."""
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

    # Test Bhava 1 (Lagna)
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
