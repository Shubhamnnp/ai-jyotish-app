"""
Unit and Integration Tests for Time and Location Service (Phase 1 Task P1-T7).
Verifies:
1. IANA timezone parsing via Python standard library zoneinfo.
2. Historical Indian time rules (1942-45 War Time, 1962/1965/1971 DST, pre-1906 LMT).
3. Ambiguous DST transition detection (requires fold=0 or fold=1).
4. Non-existent DST spring-forward gap detection.
5. Pydantic BirthData birth_time_confidence and fold support.
"""

import pytest
from datetime import date, time, datetime, timezone
from src.jyotish.timeloc import (
    TimeService,
    AmbiguousTimeError,
    NonExistentTimeError,
    InvalidTimezoneError,
)
from src.jyotish.core.models import BirthData
from src.jyotish.core.calculator import ChartCalculator


def test_standard_ist_time_resolution():
    """Verify modern Indian Standard Time (+5:30)."""
    res = TimeService.resolve_to_utc(
        local_date=date(2024, 6, 15),
        local_time=time(14, 30),
        timezone_name="Asia/Kolkata"
    )
    assert res.timezone_name == "Asia/Kolkata"
    assert res.offset_hours == 5.5
    assert res.utc_datetime == datetime(2024, 6, 15, 9, 0, tzinfo=timezone.utc)
    assert res.is_dst is False


def test_invalid_timezone_raises_error():
    """Verify invalid or unknown timezone raises InvalidTimezoneError."""
    with pytest.raises(InvalidTimezoneError):
        TimeService.resolve_to_utc(
            local_date=date(2024, 6, 15),
            local_time=time(12, 0),
            timezone_name="NonExistent/City"
        )


def test_historical_indian_war_time_1942_1945():
    """Verify World War II Indian War Time (+6:30) from 1942 to 1945."""
    # Test during War Time
    res = TimeService.resolve_to_utc(
        local_date=date(1943, 7, 1),
        local_time=time(12, 0),
        timezone_name="Asia/Kolkata"
    )
    assert res.offset_hours == 6.5
    assert "War Time" in (res.historical_rule or "")
    # 12:00 local - 6:30 offset = 05:30 UTC
    assert res.utc_datetime == datetime(1943, 7, 1, 5, 30, tzinfo=timezone.utc)


def test_historical_indian_war_emergencies():
    """Verify 1962, 1965, and 1971 war emergency DST (+6:30)."""
    # 1962 Sino-Indian War
    res_62 = TimeService.resolve_to_utc(
        local_date=date(1962, 11, 1),
        local_time=time(10, 0),
        timezone_name="Asia/Kolkata"
    )
    assert res_62.offset_hours == 6.5
    assert "1962" in (res_62.historical_rule or "")

    # 1965 Indo-Pak War
    res_65 = TimeService.resolve_to_utc(
        local_date=date(1965, 9, 15),
        local_time=time(10, 0),
        timezone_name="Asia/Kolkata"
    )
    assert res_65.offset_hours == 6.5
    assert "1965" in (res_65.historical_rule or "")

    # 1971 Indo-Pak War
    res_71 = TimeService.resolve_to_utc(
        local_date=date(1971, 12, 10),
        local_time=time(10, 0),
        timezone_name="Asia/Kolkata"
    )
    assert res_71.offset_hours == 6.5
    assert "1971" in (res_71.historical_rule or "")


def test_pre_1906_local_mean_time():
    """Verify pre-1906 dates use longitude-derived Local Mean Time (LMT)."""
    # Test Kolkata longitude 88.3639° -> LMT offset = 88.3639 / 15 = 5.890926 hours (approx 5h 53m 27s)
    res_lmt = TimeService.resolve_to_utc(
        local_date=date(1890, 5, 10),
        local_time=time(12, 0),
        timezone_name="Asia/Kolkata",
        longitude=88.3639,
        use_lmt_pre_1906=True
    )
    assert res_lmt.historical_lmt_applied is True
    assert abs(res_lmt.offset_hours - (88.3639 / 15.0)) < 0.0001
    assert "LMT" in (res_lmt.historical_rule or "")


def test_dst_ambiguous_time_detection():
    """Verify ambiguous time during DST fall-back raises AmbiguousTimeError unless fold is specified."""
    # In America/New_York, 2023-11-05 01:30:00 occurs twice:
    # First at EDT (UTC-4 -> 05:30 UTC, fold=0)
    # Second at EST (UTC-5 -> 06:30 UTC, fold=1)

    # 1. Without fold specified -> MUST raise AmbiguousTimeError
    with pytest.raises(AmbiguousTimeError):
        TimeService.resolve_to_utc(
            local_date=date(2023, 11, 5),
            local_time=time(1, 30),
            timezone_name="America/New_York",
            fold=None
        )

    # 2. With fold=0 (EDT / daylight time)
    res_fold0 = TimeService.resolve_to_utc(
        local_date=date(2023, 11, 5),
        local_time=time(1, 30),
        timezone_name="America/New_York",
        fold=0
    )
    assert res_fold0.fold_applied == 0
    assert res_fold0.utc_datetime == datetime(2023, 11, 5, 5, 30, tzinfo=timezone.utc)

    # 3. With fold=1 (EST / standard time)
    res_fold1 = TimeService.resolve_to_utc(
        local_date=date(2023, 11, 5),
        local_time=time(1, 30),
        timezone_name="America/New_York",
        fold=1
    )
    assert res_fold1.fold_applied == 1
    assert res_fold1.utc_datetime == datetime(2023, 11, 5, 6, 30, tzinfo=timezone.utc)


def test_dst_non_existent_time_detection():
    """Verify spring-forward gap raises NonExistentTimeError."""
    # In America/New_York, 2023-03-12 02:30:00 does not exist (clocks jump from 01:59:59 to 03:00:00)
    with pytest.raises(NonExistentTimeError):
        TimeService.resolve_to_utc(
            local_date=date(2023, 3, 12),
            local_time=time(2, 30),
            timezone_name="America/New_York"
        )


def test_birth_data_confidence_and_calculator_integration():
    """Verify BirthData confidence fields and ChartCalculator integration."""
    b_data = BirthData(
        name="Exact Native",
        birth_date=date(2020, 1, 1),
        birth_time=time(12, 0),
        latitude=28.6139,
        longitude=77.2090,
        timezone="Asia/Kolkata",
        birth_time_confidence="exact"
    )
    calc = ChartCalculator()
    chart = calc.calculate_full_chart(b_data)
    assert chart.birth_data.birth_time_confidence == "exact"
    assert chart.birth_data.timezone == "Asia/Kolkata"
    assert chart.metadata.jd_ut is not None
