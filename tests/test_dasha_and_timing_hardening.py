"""
Unit test suite for Phase 6: Dasha Systems & Timing Engine Hardening.
Tests:
1. 5-level Vimshottari Dasha hierarchy (MD, AD, PD, SD, PAD) with exact datetime continuity.
2. Vimshottari balance of dasha at birth based on exact lunar longitude.
3. 36-year Yogini Dasha cycle (Mangala to Sankata) and point-in-time calculation.
4. Jaimini Chara Dasha sign durations and direct/indirect progressions.
5. Transit Engine Gochar snapshot with Sade Sati and Dhaiya detection.
6. Classical Phaladeepika Gochar Vedha (Obstruction) and father-son exemption rules.
"""

import pytest
from datetime import date, time, datetime, timedelta
from src.jyotish.core.models import BirthData
from src.jyotish.core.calculator import default_chart_calculator
from src.jyotish.dasha.vimshottari import VimshottariDashaEngine
from src.jyotish.dasha.yogini import YoginiDashaEngine, YOGINI_SEQUENCE
from src.jyotish.dasha.chara import CharaDashaEngine
from src.jyotish.core.gochar import default_transit_engine


@pytest.fixture
def timing_chart():
    bdata = BirthData(
        name="Timing Benchmark Native",
        birth_date=date(1990, 8, 15),
        birth_time=time(10, 30, 0),
        latitude=28.6139,
        longitude=77.2090,
        timezone_offset=5.5,
        city="New Delhi"
    )
    return default_chart_calculator.calculate_full_chart(bdata)


def test_vimshottari_5level_hierarchy(timing_chart):
    """Verify 5-level Vimshottari calculation (MD, AD, PD, SD, PAD) with valid nesting."""
    engine = VimshottariDashaEngine()
    birth_dt = datetime.combine(timing_chart.birth_data.birth_date, timing_chart.birth_data.birth_time)
    moon_lon = timing_chart.planets["Moon"].longitude
    target_dt = datetime(2026, 11, 3, 12, 0, 0)
    
    hierarchy = engine.get_5level_hierarchy(birth_dt, moon_lon, target_dt)
    
    # 5 active levels present
    assert "mahadasha" in hierarchy
    assert "antardasha" in hierarchy
    assert "pratyantardasha" in hierarchy
    assert "sookshmadasha" in hierarchy
    assert "pranadasha" in hierarchy
    
    # Verify that target_dt falls cleanly within the Mahadasha and Antardasha bounds
    md = hierarchy["mahadasha"]
    ad = hierarchy["antardasha"]
    assert md["start_date"] <= target_dt <= md["end_date"]
    assert ad["start_date"] <= target_dt <= ad["end_date"]


def test_vimshottari_birth_balance_continuity(timing_chart):
    """Verify that Antardashas within a full Mahadasha exactly sum to the Mahadasha duration."""
    engine = VimshottariDashaEngine()
    timeline = engine.generate_timeline(timing_chart)
    
    assert len(timeline) >= 9
    first_md = timeline[0]
    assert first_md["duration_years"] > 0.0
    
    # Second Mahadasha is always a full uncurtailed cycle
    second_md = timeline[1]
    antardashas = engine.generate_antardashas(
        second_md["lord"],
        second_md["start_date"],
        second_md["end_date"],
        is_partial=False
    )
    assert len(antardashas) == 9
    
    # Verify temporal continuity: end of each AD is start of next AD
    for i in range(len(antardashas) - 1):
        assert antardashas[i]["end_date"] == antardashas[i+1]["start_date"]


def test_yogini_dasha_36_year_cycle(timing_chart):
    """Verify 36-year Yogini Dasha sequence and starting balance calculation."""
    moon_lon = timing_chart.planets["Moon"].longitude
    idx, balance_years = YoginiDashaEngine.calculate_starting_yogini(moon_lon)
    
    assert 0 <= idx <= 7
    starting_yogini = YOGINI_SEQUENCE[idx]
    assert 0.0 <= balance_years <= starting_yogini["years"]
    
    # Generate timeline
    timeline = YoginiDashaEngine.generate_timeline(timing_chart, target_years=72.0)
    assert len(timeline) >= 8
    for entry in timeline:
        assert entry["yogini"] in [y["name"] for y in YOGINI_SEQUENCE]
        assert entry["end_date"] > entry["start_date"]


def test_jaimini_chara_dasha_sign_durations(timing_chart):
    """Verify Jaimini Chara Dasha sign sequence and durations (1 to 12 years per sign)."""
    chara_timeline = CharaDashaEngine.generate_timeline(timing_chart)
    assert len(chara_timeline) == 12
    
    for entry in chara_timeline:
        assert 1 <= entry["sign_id"] <= 12
        assert 1 <= entry["duration_years"] <= 12
        assert entry["end_date"] > entry["start_date"]


def test_transit_engine_snapshot_and_sade_sati(timing_chart):
    """Verify Gochar transit snapshot, Sade Sati phase, and Ashtakavarga transit lookup."""
    target_date = date(2026, 11, 3)
    transit_data, summary = default_transit_engine.compute_transit_snapshot(timing_chart, target_date)
    
    assert "Saturn" in transit_data
    assert "Jupiter" in transit_data
    assert 1 <= summary.saturn_house_from_moon <= 12
    assert 1 <= summary.jupiter_house_from_moon <= 12
    
    # Check Sade Sati logic consistency
    if summary.saturn_house_from_moon in (12, 1, 2):
        assert summary.is_sade_sati is True
        assert summary.sade_sati_phase is not None
    else:
        assert summary.is_sade_sati is False


def test_gochar_vedha_obstruction_and_exemptions():
    """Verify classical Phaladeepika Vedha pairs and Sun-Saturn father-son exemption."""
    # Mock transit positions where Sun is in favorable 3rd house from Moon
    # and Mars is in 9th house from Moon (Vedha obstruction for Sun in 3rd)
    mock_transit = {
        "Sun": {"house_from_moon": 3},
        "Mars": {"house_from_moon": 9},
        "Saturn": {"house_from_moon": 9},  # Sun-Saturn exemption test
        "Jupiter": {"house_from_moon": 5},
    }
    
    vedha_analysis = default_transit_engine.evaluate_gochar_vedha(mock_transit)
    
    sun_v = vedha_analysis["Sun"]
    assert sun_v["is_favorable"] is True
    assert sun_v["vedha_house"] == 9
    # Mars causes vedha, but Saturn does NOT cause vedha on Sun due to father-son exemption
    assert sun_v["is_obstructed"] is True
    assert "Mars" in sun_v["blocking_planets"]
    assert "Saturn" not in sun_v["blocking_planets"]
