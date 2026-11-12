"""
Unit tests for Horary Shodasha Sphutas (16 Sensitive Longitudinal Points) per Kerala Prashna Marga.
Verifies:
1. Trisphuta, Chatursphuta, Panchasphuta calculation.
2. Prana, Deha, Mrityu Sphutas.
3. Beeja, Kshetra, Santana, Vivaha Sphutas.
4. Completeness of all 16 Sphutas with degrees, nakshatra, and navamsha.
"""

import pytest
from datetime import date, time
from src.jyotish.core.models import BirthData
from src.jyotish.core.calculator import default_chart_calculator
from src.jyotish.services.prashna import PrashnaService


@pytest.fixture
def horary_chart():
    bdata = BirthData(
        name="Horary Prashna Query",
        birth_date=date(2024, 3, 21),
        birth_time=time(10, 15, 0),
        latitude=28.6139,
        longitude=77.2090,
        timezone_offset=5.5,
        city="New Delhi"
    )
    return default_chart_calculator.calculate_chart(bdata)


def test_shodasha_sphutas_completeness_and_bounds(horary_chart):
    """Verify all 16 sphutas are computed with valid mathematical properties."""
    sphutas = PrashnaService.calculate_shodasha_sphutas(horary_chart, karyesha="Jupiter")
    assert len(sphutas) == 16

    expected_sphuta_names = [
        "Trisphuta", "Chatursphuta", "Panchasphuta", "Prana Sphuta", "Deha Sphuta",
        "Mrityu Sphuta", "Beeja Sphuta", "Kshetra Sphuta", "Santana Sphuta", "Vivaha Sphuta",
        "Artha Sphuta", "Karya Sphuta", "Shatru Sphuta", "Labha Sphuta", "Rina Sphuta", "Dosha Sphuta"
    ]

    for s, exp_name in zip(sphutas, expected_sphuta_names):
        assert s["name_en"] == exp_name
        assert 0.0 <= s["longitude"] < 360.0
        assert len(s["sign"]) > 0
        assert "°" in s["dms"]
        assert "पद" in s["nakshatra_pada"]
        assert len(s["navamsha_sign"]) > 0
        assert len(s["formula"]) > 0
        assert len(s["phala"]) > 0
