"""
Test suite for Upagraha & Aprakash Graha Engine Hardening (Phase 3 Task 6).
Verifies:
1. Classical Aprakasha Grahas mathematical invariant: (Upaketu + 30°) % 360 == Sun.
2. Diurnal daytime 8-part division for Gulika (start) and Mandi (middle).
3. Nocturnal nighttime 8-part division.
4. Pre-sunrise birth correctly assigned to preceding Vedic day night.
5. Invariant bounds across all upagraha longitudes and valid zodiac sign names.
"""

import pytest
from datetime import date, time
from src.jyotish.core.models import BirthData
from src.jyotish.core.calculator import default_chart_calculator
from src.jyotish.core.upagraha import default_upagraha_calculator
from src.jyotish.core.constants import SIGN_NAMES


def test_aprakasha_grahas_classical_sun_invariant():
    """Verify that (Upaketu + 30°) % 360 == Sun longitude across diverse dates."""
    dates_to_test = [
        date(1985, 11, 23),
        date(1999, 8, 11),
        date(2024, 1, 1),
    ]
    for b_date in dates_to_test:
        bdata = BirthData(
            name="Aprakasha Native",
            birth_date=b_date,
            birth_time=time(12, 0, 0),
            latitude=28.6139,
            longitude=77.2090,
            timezone_offset=5.5
        )
        chart = default_chart_calculator.calculate_chart(bdata)
        up = default_upagraha_calculator.calculate(chart)

        sun_lon = chart.planets["Sun"].longitude
        derived_sun = (up.upaketu_longitude + 30.0) % 360.0
        diff = abs(derived_sun - sun_lon)
        if diff > 180.0:
            diff = abs(diff - 360.0)
        assert diff < 0.01, f"Classical Aprakasha invariant violated: diff={diff}° on {b_date}"

        # Verify sign names match longitudes
        assert up.dhuma_sign_name == SIGN_NAMES[int(up.dhuma_longitude // 30.0)]
        assert up.vyatipata_sign_name == SIGN_NAMES[int(up.vyatipata_longitude // 30.0)]
        assert up.parivesha_sign_name == SIGN_NAMES[int(up.parivesha_longitude // 30.0)]
        assert up.indrachapa_sign_name == SIGN_NAMES[int(up.indrachapa_longitude // 30.0)]
        assert up.upaketu_sign_name == SIGN_NAMES[int(up.upaketu_longitude // 30.0)]


def test_saturday_day_birth_gulika_segment_1():
    """Nov 23, 1985 was Saturday. Daytime birth (8:15 AM) must have Gulika segment 1."""
    bdata = BirthData(
        name="Saturday Day Native",
        birth_date=date(1985, 11, 23),
        birth_time=time(8, 15, 0),
        latitude=28.6139,
        longitude=77.2090,
        timezone_offset=5.5
    )
    chart = default_chart_calculator.calculate_full_chart(bdata)
    up = chart.upagrahas
    assert up is not None
    assert up.is_night_birth is False
    assert up.gulika_segment == 1
    assert 0.0 <= up.gulika_longitude < 360.0
    assert 0.0 <= up.mandi_longitude < 360.0
    assert up.gulika_sign_name in SIGN_NAMES
    assert up.mandi_sign_name in SIGN_NAMES
    assert up.dinamana_hours is not None
    assert 9.0 <= up.dinamana_hours <= 15.0


def test_saturday_night_birth_gulika_segment_4():
    """Nov 23, 1985 (Saturday). Nighttime birth (23:30) must have Gulika segment 4."""
    bdata = BirthData(
        name="Saturday Night Native",
        birth_date=date(1985, 11, 23),
        birth_time=time(23, 30, 0),
        latitude=28.6139,
        longitude=77.2090,
        timezone_offset=5.5
    )
    chart = default_chart_calculator.calculate_full_chart(bdata)
    up = chart.upagrahas
    assert up is not None
    assert up.is_night_birth is True
    assert up.gulika_segment == 4
    assert up.ratrimana_hours is not None
    assert 9.0 <= up.ratrimana_hours <= 15.0


def test_pre_sunrise_birth_belongs_to_previous_night():
    """
    Nov 23, 1985 03:00 AM (pre-sunrise on Saturday).
    Belongs to Friday night. On Friday night, Saturn's segment is 5.
    """
    bdata = BirthData(
        name="Pre-Sunrise Native",
        birth_date=date(1985, 11, 23),
        birth_time=time(3, 0, 0),
        latitude=28.6139,
        longitude=77.2090,
        timezone_offset=5.5
    )
    chart = default_chart_calculator.calculate_full_chart(bdata)
    up = chart.upagrahas
    assert up is not None
    assert up.is_night_birth is True
    assert up.gulika_segment == 5  # Friday night segment 5
