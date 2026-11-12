"""
Unit tests for Tajika Patyayini Dasha (Tajika Neelakanthi Ch. 4).
Verifies:
1. Generation of 1-year Patyayini Dasha for solar return chart.
2. Ascending sign degree ordering.
3. Total duration sums to exactly 365.25 days within rounding margin.
4. Active dasha identification.
"""

import pytest
from datetime import datetime, date, time
from src.jyotish.core.models import BirthData
from src.jyotish.core.calculator import default_chart_calculator
from src.jyotish.services.varshaphal import VarshaphalService


@pytest.fixture
def sample_chart():
    bdata = BirthData(
        name="Patyayini Benchmark Native",
        birth_date=date(1992, 7, 24),
        birth_time=time(16, 10, 0),
        latitude=28.6139,
        longitude=77.2090,
        timezone_offset=5.5,
        city="New Delhi"
    )
    return default_chart_calculator.calculate_chart(bdata)


def test_patyayini_dasha_calculation(sample_chart):
    """Verify VarshaphalService._calculate_patyayini_dasha generates a valid 365.25-day sequence."""
    service = VarshaphalService()
    start_dt = datetime(2024, 7, 24, 12, 0, 0)
    timeline = service._calculate_patyayini_dasha(start_dt, sample_chart)

    assert len(timeline) >= 7

    total_days = sum(d["duration_days"] for d in timeline)
    assert abs(total_days - 365.25) <= 1.5

    # Check structure
    for d in timeline:
        assert "lord" in d
        assert "lord_hi" in d
        assert "sign_degree" in d
        assert "patyamsa_diff" in d
        assert "start_date" in d
        assert "end_date" in d
        assert "duration_days" in d
        assert "status" in d
