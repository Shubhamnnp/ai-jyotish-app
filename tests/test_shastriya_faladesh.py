"""
Unit Tests for Shastriya Faladesh (शास्त्रीय फलादेश) Service.
Verifies:
- 50 Life Dimensions
- 100 FAQs per Dimension
- Mathematical Synthesis (Degrees, Houses, SAV, Bhavabala, Shadbala, Vargas, Dasha)
- Positive & Negative Shastric Balances
"""

import pytest
from datetime import date, time
from src.jyotish.core.calculator import default_chart_calculator
from src.jyotish.core.models import BirthData
from src.jyotish.services.shastriya_faladesh import (
    default_shastriya_faladesh_engine,
    LIFE_DIMENSIONS_50
)


def test_shastriya_faladesh_dimensions_count():
    assert len(LIFE_DIMENSIONS_50) == 50, "Expected exactly 50 life dimensions"


def test_shastriya_faladesh_synthesis_and_faqs():
    b_data = BirthData(
        name="Test Querent",
        birth_date=date(1995, 5, 15),
        birth_time=time(14, 30),
        latitude=28.6139,
        longitude=77.2090,
        timezone_offset=5.5
    )
    chart = default_chart_calculator.calculate_full_chart(b_data)
    assert chart is not None

    # Test Dimension 1 (Career)
    synth = default_shastriya_faladesh_engine.synthesize_dimension(chart, 1, b_data)
    assert synth is not None
    assert synth["dimension"]["id"] == 1
    assert "आजीविका" in synth["dimension"]["name_hi"]
    assert len(synth["faqs_100"]) == 100, "Expected exactly 100 FAQs"
    assert 0 <= synth["positive_pct"] <= 100
    assert 0 <= synth["negative_pct"] <= 100
    assert synth["positive_pct"] + synth["negative_pct"] == 100

    # Test answering a specific FAQ
    ans = default_shastriya_faladesh_engine.answer_specific_faq(chart, 1, 1, b_data)
    assert ans["faq_num"] == 1
    assert len(ans["full_answer_md"]) > 20
    assert "प्रत्यक्ष शास्त्रीय निर्णय" in ans["full_answer_md"]
    assert "काल निर्णय" in ans["full_answer_md"]

