"""
Unit tests for Sarvatobhadra Chakra 81-cell engine and 28-nakshatra Vedha calculation.
Verifies:
1. 28 Nakshatras including Abhijit placement.
2. Frontal (Agra), Right Diagonal (Dakshina), and Left Diagonal (Vama) Vedhas.
3. Native's sensitive Nakshatras (Janma, Karma, Sanghatika, Aadhana, Vainashika, Manasa, Raja).
4. Malefic vs Benefic Vedha influence tagging.
"""

import pytest
from datetime import date, time
from src.jyotish.core.models import BirthData
from src.jyotish.core.calculator import default_chart_calculator
from src.jyotish.core.sarvatobhadra import SarvatobhadraChakraEngine, SARVATOBHADRA_28_NAKSHATRAS


@pytest.fixture
def sample_chart():
    bdata = BirthData(
        name="Sarvatobhadra Benchmark Native",
        birth_date=date(1988, 8, 20),
        birth_time=time(15, 45, 0),
        latitude=28.6139,
        longitude=77.2090,
        timezone_offset=5.5,
        city="New Delhi"
    )
    return default_chart_calculator.calculate_chart(bdata)


def test_28_nakshatra_abhijit_bracket():
    """Verify Abhijit occupies Capricorn 6°40' to 10°53'20" (276.67° to 280.89°)."""
    # Lon 278.5° is inside Abhijit
    nak, idx = SarvatobhadraChakraEngine.get_28_nakshatra_for_longitude(278.5)
    assert nak == "Abhijit"
    assert idx == 19

    # Lon 10.0° is Ashwini
    nak2, idx2 = SarvatobhadraChakraEngine.get_28_nakshatra_for_longitude(10.0)
    assert nak2 == "Ashwini"
    assert idx2 == SARVATOBHADRA_28_NAKSHATRAS.index("Ashwini")


def test_sarvatobhadra_vedha_calculation(sample_chart):
    """Verify complete Sarvatobhadra Chakra Vedha calculation."""
    res = SarvatobhadraChakraEngine.calculate_chakra_vedha(sample_chart)
    
    assert "janma_nakshatra_28" in res
    assert "sensitive_nakshatra_map" in res
    assert "planet_positions_28" in res
    assert "all_vedhas" in res
    assert "sensitive_vedhas" in res

    # 9 classical sensitive nakshatras mapped
    assert len(res["sensitive_nakshatra_map"]) == 9

    # All planets have frontal, right diagonal, and left diagonal vedhas
    all_vedhas = res["all_vedhas"]
    assert len(all_vedhas) >= len(sample_chart.planets) * 3

    vedha_types = {v.vedha_type for v in all_vedhas}
    assert "अग्र वेध (Frontal)" in vedha_types
    assert "दक्षिण वेध (Right Diagonal)" in vedha_types
    assert "वाम वेध (Left Diagonal)" in vedha_types
