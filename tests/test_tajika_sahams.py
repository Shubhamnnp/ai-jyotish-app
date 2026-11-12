"""
Unit tests for Tajika Sahams and Saham-to-Planets Aspect Matrix (Tajika Neelakanthi).
Verifies:
1. Canonical Saham generation.
2. Tajika Aspect Matrix calculation (Mitra, Shatru, Neutral, Conjunction).
3. Overall aspect verdict calculation.
"""

import pytest
from datetime import date, time
from src.jyotish.core.models import BirthData
from src.jyotish.core.calculator import default_chart_calculator
from src.jyotish.services.varshaphal import VarshaphalService


@pytest.fixture
def sample_chart():
    bdata = BirthData(
        name="Tajika Benchmark Native",
        birth_date=date(1995, 4, 12),
        birth_time=time(11, 20, 0),
        latitude=28.6139,
        longitude=77.2090,
        timezone_offset=5.5,
        city="New Delhi"
    )
    return default_chart_calculator.calculate_chart(bdata)


def test_saham_aspect_matrix_calculation(sample_chart):
    """Verify VarshaphalService.calculate_saham_aspect_matrix produces valid aspects."""
    service = VarshaphalService()
    sahams = service._calculate_extended_sahams(sample_chart, is_day=True)
    assert len(sahams) >= 20

    matrix = VarshaphalService.calculate_saham_aspect_matrix(sahams, sample_chart)
    assert len(matrix) == len(sahams)

    planets = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
    for row in matrix:
        assert "सहम बिंदु" in row
        assert "सहम राशि" in row
        assert "ताजिक दृष्टि फलादेश" in row
        for p in planets:
            assert p in row
            aspect_tag = row[p]
            assert any(tag in aspect_tag for tag in ["मित्र", "शत्रु", "सम", "युति", "—"])
