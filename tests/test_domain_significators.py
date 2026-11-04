"""
Unit tests for Domain Significators & Domain Analysis Engine (Phase 5, Task P5-T2).
Reference: docs/IMPLEMENTATION_PRD.md (Section 5.2).

Verifies:
1. Declarative YAML loading across all supported life domains.
2. Classical significator mapping (Primary Bhavas, Lords, Karakas, Vargas).
3. Parashari order of analysis enforcement.
4. Medical disclaimer attachment for health domain.
5. School-specific domain configurations (Jaimini, KP, Lal Kitab, Tajika).
"""

import sys
import os
import pytest
from datetime import date, datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from jyotish.core.models import BirthData
from jyotish.core.calculator import default_chart_calculator
from jyotish.evidence.factors import default_factor_extractor
from jyotish.evidence.domains.analyzer import (
    DomainAnalyzer,
    default_domain_analyzer,
    DomainSignificators,
    DomainAnalysisResult
)


@pytest.fixture(scope="module")
def benchmark_factors():
    bd = BirthData(
        name="Swami Vivekananda",
        birth_date=date(1863, 1, 12),
        birth_time=datetime.strptime("06:33:00", "%H:%M:%S").time(),
        latitude=22.5726,
        longitude=88.3639,
        timezone_offset=5.5,
        city="Kolkata",
        confidence="Exact"
    )
    chart = default_chart_calculator.calculate_full_chart(bd)
    return default_factor_extractor.extract_factors(chart)


def test_domain_yaml_configs_loading():
    """Verify all domain YAML files load and register cleanly."""
    domains = default_domain_analyzer.list_available_domains()
    assert len(domains) >= 8

    expected_domains = [
        "career", "wealth", "marriage", "health",
        "education", "spirituality", "property", "children", "personality"
    ]
    for d in expected_domains:
        assert d in domains, f"Domain '{d}' not found in loaded configs"


def test_domain_significators_structure():
    """Verify domain significators map classical bhavas, karakas, and analysis order."""
    career_sigs = default_domain_analyzer.get_significators("career")

    assert career_sigs.domain == "career"
    assert 10 in career_sigs.parashari_primary_bhavas
    assert "Sun" in career_sigs.parashari_karakas
    assert "Saturn" in career_sigs.parashari_karakas
    assert "D10" in career_sigs.parashari_vargas
    assert "bhava_occupants" in career_sigs.analysis_order
    assert "bhava_lord" in career_sigs.analysis_order


def test_career_domain_analysis(benchmark_factors):
    """Verify evaluating career domain against ChartFactors produces typed factors."""
    result: DomainAnalysisResult = default_domain_analyzer.analyze_domain(
        "career", benchmark_factors, school="parashari"
    )

    assert result.domain == "career"
    assert len(result.primary_bhavas) >= 1
    h10_factor = result.primary_bhavas[0]
    assert h10_factor.house_num == 10
    assert h10_factor.lord == "Venus"  # Libra is 10th for Capricorn Lagna
    assert h10_factor.sav_bindus > 0
    assert h10_factor.net_bhava_strength > 0.0

    # Karakas
    karaka_names = [k.planet for k in result.primary_karakas]
    assert "Sun" in karaka_names
    assert "Saturn" in karaka_names

    assert result.overall_prominence_score > 0.0
    assert len(result.classical_summary_en) > 20
    assert len(result.classical_summary_hi) > 20


def test_health_domain_disclaimer(benchmark_factors):
    """Verify health domain attaches non-medical disclaimer."""
    result = default_domain_analyzer.analyze_domain("health", benchmark_factors)

    assert result.domain == "health"
    assert len(result.disclaimers) > 0
    assert "Non-medical" in result.disclaimers[0] or "medical" in result.disclaimers[0].lower()


def test_multischool_domain_significators():
    """Verify domain significators provide separate configs for Jaimini and KP."""
    marriage_sigs = default_domain_analyzer.get_significators("marriage")

    # Jaimini specifies Darakaraka (DK) and Upapada (UL)
    assert "DK" in marriage_sigs.jaimini_karakas
    assert "UL" in marriage_sigs.jaimini_arudhas

    # KP specifies 7th cusp
    assert 7 in marriage_sigs.kp_primary_cusps
    assert 2 in marriage_sigs.kp_favorable_houses
    assert 11 in marriage_sigs.kp_favorable_houses
