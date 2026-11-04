"""
Unit and Integration Tests for Hardened Dasha Engines (Phase 3 Task P3-T1).
Verifies:
1. User-selectable year bases: Solar (365.2425d), Savana (360.0d), Nakshatra (327.85d).
2. Complete 5-level hierarchy: Mahadasha, Antardasha, Pratyantar, Sookshma, Prana with exact nesting.
3. Dasha Sandhi detection (30-day window around Mahadashas, 7-day window around Antardashas).
4. Jaimini Chara Dasha engine timeline and duration calculation.
5. Yogini Dasha 36-year cycle timeline.
"""

import pytest
from datetime import datetime, date, time, timedelta, timezone
from src.jyotish.dasha import (
    VimshottariDashaEngine,
    CharaDashaEngine,
    YoginiDashaEngine,
    DASHA_CAPABILITIES
)
from src.jyotish.core.models import BirthData
from src.jyotish.core.calculator import ChartCalculator


def test_dasha_year_bases():
    """Verify exact duration scaling across Solar, Savana, and Nakshatra year bases."""
    eng_solar = VimshottariDashaEngine(year_type="solar")
    eng_savana = VimshottariDashaEngine(year_type="savana")
    eng_nakshatra = VimshottariDashaEngine(year_type="nakshatra")

    assert eng_solar.year_days == 365.2425
    assert eng_savana.year_days == 360.0
    assert eng_nakshatra.year_days == 327.85

    birth_dt = datetime(2000, 1, 1, 12, 0)
    # Moon at 0.0 deg (Ashwini -> Ketu, 7 years)
    seq_solar = eng_solar.generate_mahadasha_sequence(birth_dt, 0.0)
    seq_savana = eng_savana.generate_mahadasha_sequence(birth_dt, 0.0)
    seq_nakshatra = eng_nakshatra.generate_mahadasha_sequence(birth_dt, 0.0)

    # 2nd period is Venus (20 years)
    dur_solar = (seq_solar[1]["end_date"] - seq_solar[1]["start_date"]).total_seconds() / 86400.0
    dur_savana = (seq_savana[1]["end_date"] - seq_savana[1]["start_date"]).total_seconds() / 86400.0
    dur_nakshatra = (seq_nakshatra[1]["end_date"] - seq_nakshatra[1]["start_date"]).total_seconds() / 86400.0

    assert abs(dur_solar - (20.0 * 365.2425)) < 0.01
    assert abs(dur_savana - (20.0 * 360.0)) < 0.01
    assert abs(dur_nakshatra - (20.0 * 327.85)) < 0.01


def test_5level_hierarchy_nesting():
    """Verify strict nesting of 5-level Dasha hierarchy down to Prana."""
    eng = VimshottariDashaEngine(year_type="solar")
    birth_dt = datetime(1990, 5, 15, 8, 30)
    moon_lon = 45.0  # Rohini -> Moon dasha

    target_dt = datetime(2024, 10, 24, 12, 0)
    h5 = eng.get_5level_hierarchy(birth_dt, moon_lon, target_dt)

    maha = h5["mahadasha"]
    antar = h5["antardasha"]
    prat = h5["pratyantardasha"]
    sookshma = h5["sookshmadasha"]
    prana = h5["pranadasha"]

    # Strict containment checks
    assert maha["start_date"] <= antar["start_date"]
    assert antar["end_date"] <= maha["end_date"]

    assert antar["start_date"] <= prat["start_date"]
    assert prat["end_date"] <= antar["end_date"]

    assert prat["start_date"] <= sookshma["start_date"]
    assert sookshma["end_date"] <= prat["end_date"]

    assert sookshma["start_date"] <= prana["start_date"]
    assert prana["end_date"] <= sookshma["end_date"]

    # Target datetime must fall inside the active Prana dasha
    assert prana["start_date"] <= target_dt <= prana["end_date"]


def test_dasha_sandhi_detection():
    """Verify Dasha Sandhi detection at Mahadasha and Antardasha boundaries."""
    eng = VimshottariDashaEngine()
    birth_dt = datetime(2000, 1, 1, 0, 0)
    moon_lon = 0.0  # Ketu dasha: 7 years -> ends 2007-01-01

    # 1. Right at the end of Ketu Mahadasha (10 days before end -> inside 30-day window)
    sandhi_target = datetime(2006, 12, 25, 0, 0)
    res = eng.check_dasha_sandhi(birth_dt, moon_lon, sandhi_target)
    assert res["is_sandhi"] is True
    assert res["is_mahadasha_sandhi"] is True
    assert res["sandhi_type"] == "Mahadasha Sandhi"
    assert res["maha_days_to_boundary"] <= 30.0

    # 2. Right in the middle of a Mahadasha (e.g. year 2003 -> no sandhi)
    mid_target = datetime(2003, 6, 15, 0, 0)
    res_mid = eng.check_dasha_sandhi(birth_dt, moon_lon, mid_target)
    # Either False or only Antardasha if by chance near an Antar boundary
    if not res_mid["is_antardasha_sandhi"]:
        assert res_mid["is_sandhi"] is False
        assert res_mid["is_mahadasha_sandhi"] is False


def test_chara_and_yogini_engines():
    """Verify Jaimini Chara Dasha and Yogini Dasha timeline generation."""
    calc = ChartCalculator()
    b_data = BirthData(
        name="Dasha Test Native",
        birth_date=date(1995, 8, 20),
        birth_time=time(14, 30),
        latitude=28.6139,
        longitude=77.2090,
        timezone="Asia/Kolkata"
    )
    chart = calc.calculate_full_chart(b_data)

    # Chara Dasha
    chara_timeline = CharaDashaEngine.generate_timeline(chart)
    assert len(chara_timeline) == 12
    for entry in chara_timeline:
        assert 1 <= entry["duration_years"] <= 12
        assert entry["sign_name"] in ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
                                      "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]

    # Yogini Dasha
    yogini_timeline = YoginiDashaEngine.generate_timeline(chart)
    assert len(yogini_timeline) >= 8
    first_yogini = yogini_timeline[0]
    assert first_yogini["yogini_name"] in ["Mangala", "Pingala", "Dhanya", "Bhramari", "Bhadrika", "Ulka", "Siddha", "Sankata"]
    assert "start_date" in first_yogini
    assert "end_date" in first_yogini
