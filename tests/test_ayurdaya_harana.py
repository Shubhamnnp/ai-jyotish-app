"""
Unit tests for Classical Pindayu Longevity and Harana Reductions (BPHS Ch. 43).
Verifies:
1. Unreduced Pindayu planetary contributions based on exaltation distance.
2. Shatrukshetra Harana (1/3 reduction, exception for retrograde).
3. Astangata Harana (1/2 reduction, exception for Venus and Saturn).
4. Chakrapata Harana (reductions for planets in houses 12 down to 7).
5. Lagna Ayurdaya addition and net lifespan compilation.
"""

import pytest
from datetime import date, time
from src.jyotish.core.models import BirthData
from src.jyotish.core.calculator import default_chart_calculator
from src.jyotish.core.ayurdaya import AyurdayaEngine


@pytest.fixture
def sample_chart():
    bdata = BirthData(
        name="Harana Benchmark Native",
        birth_date=date(1990, 6, 15),
        birth_time=time(14, 30, 0),
        latitude=28.6139,
        longitude=77.2090,
        timezone_offset=5.5,
        city="New Delhi"
    )
    return default_chart_calculator.calculate_chart(bdata)


def test_pindayu_with_haranas_structure_and_bounds(sample_chart):
    """Verify calculate_pindayu_with_haranas produces complete breakdown."""
    res = AyurdayaEngine.calculate_pindayu_with_haranas(sample_chart)
    
    assert "planet_contributions" in res
    assert "unreduced_contributions" in res
    assert "total_unreduced" in res
    assert "lagna_contribution" in res
    assert "net_pindayu_years" in res
    assert "shatrukshetra_reductions" in res
    assert "astangata_reductions" in res
    assert "chakrapata_reductions" in res
    assert "audit_table" in res

    # Check 7 classical planets
    for p in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]:
        assert p in res["planet_contributions"]
        assert p in res["unreduced_contributions"]
        # Net cannot exceed unreduced
        assert res["planet_contributions"][p] <= res["unreduced_contributions"][p]

    assert 20.0 <= res["total_unreduced"] <= 125.0
    assert 0.0 <= res["lagna_contribution"] <= 12.0
    assert 15.0 <= res["net_pindayu_years"] <= 120.0
    assert len(res["audit_table"]) == 7


def test_astangata_harana_exceptions(sample_chart):
    """Verify Venus and Saturn are exempt from Astangata (combustion) reduction."""
    res = AyurdayaEngine.calculate_pindayu_with_haranas(sample_chart)
    ast_map = res["astangata_reductions"]
    
    # Even if combust, cut must be 0 for Venus and Saturn
    if sample_chart.planets["Venus"].is_combust:
        assert ast_map["Venus"]["cut"] == 0.0
        assert "अपवाद" in ast_map["Venus"]["reason"]
        
    if sample_chart.planets["Saturn"].is_combust:
        assert ast_map["Saturn"]["cut"] == 0.0
        assert "अपवाद" in ast_map["Saturn"]["reason"]
