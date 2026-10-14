"""
Tests for Trio AI Astrological Engine:
Synthesizing JyotishOS Deep Math Engine + Google Gemini AI + OpenAI (GPT-4o).
"""

from datetime import date, time
import pytest
from src.jyotish.core.models import BirthData
from src.jyotish.core.calculator import default_chart_calculator
from src.jyotish.ai.narrative import AINarrativeService, default_narrative_service


@pytest.fixture
def sample_chart():
    b = BirthData(
        name="परीक्षार्थी जातक",
        birth_date=date(1995, 5, 15),
        birth_time=time(14, 30),
        latitude=28.6139,
        longitude=77.2090,
        timezone_offset=5.5
    )
    return default_chart_calculator.calculate_chart(b)


def test_trio_chart_context_contains_deep_math(sample_chart):
    """Verifies that build_full_chart_context embeds all deep mathematical metrics."""
    srv = AINarrativeService()
    ctx = srv.build_full_chart_context(sample_chart)
    
    # 1. Fundamental chart profile
    assert "परीक्षार्थी जातक" in ctx
    assert "Lagna (Ascendant)" in ctx
    assert "Moon Sign" in ctx
    assert "Sun Sign" in ctx
    
    # 2. Planetary avashthas & degrees
    assert "अवस्था:" in ctx
    assert "बाल्यावस्था" in ctx or "युवावस्था" in ctx or "कुमारावस्था" in ctx or "वृद्धावस्था" in ctx or "मृतावस्था" in ctx
    
    # 3. 12 Bhavas, Bhavabala & SAV points
    assert "12 BHAVAS" in ctx
    assert "SAV=" in ctx
    assert "Bhavabala=" in ctx
    
    # 4. Sudarshan Chakra & Kota Chakra
    assert "SUDARSHAN CHAKRA" in ctx
    assert "KOTA CHAKRA" in ctx
    
    # 5. D1 to D60 & Gemology
    assert "D1 TO D60 DIVISIONAL CHARTS" in ctx
    assert "GEMOLOGY AUDIT" in ctx or "GEMSTONE" in ctx


def test_trio_greeting_response(sample_chart):
    """Verifies that greetings receive dignified, chart-grounded responses without dumping horoscopes."""
    srv = AINarrativeService()
    res = srv.chat_consultation("नमस्ते", chart=sample_chart, provider_mode="trio")
    
    assert "नमस्ते" in res or "स्वागत" in res or "कल्याण" in res
    assert "परीक्षार्थी जातक" in res or "लग्न" in res


def test_trio_gratitude_response(sample_chart):
    """Verifies that gratitude expressions receive a dignified Vedic blessing."""
    srv = AINarrativeService()
    res = srv.chat_consultation("बहुत-बहुत धन्यवाद", chart=sample_chart, provider_mode="trio")
    
    assert "कल्याणमस्तु" in res or "शुभम्" in res or "आभार" in res or "धन्यवाद" in res


def test_trio_astrological_consultation_offline_fallback(sample_chart):
    """Verifies that when offline, the deterministic engine delivers a complete, honest consultation."""
    srv = AINarrativeService()
    res = srv.chat_consultation("मेरी शादी कब होगी?", chart=sample_chart, provider_mode="offline")
    
    assert "विवाह" in res
    assert "शास्त्रीय" in res
    assert "उपाय" in res or "सात्विक" in res

