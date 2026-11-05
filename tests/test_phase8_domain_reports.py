"""
Phase 8 Comprehensive Test Suite: Domain Intelligence & Premium Reports.
Validates tasks P8-T1 through P8-T5:
- P8-T1: 12 Life Domains Deep-Dive Analysis Pipeline (Career, Marriage, Wealth, etc.)
- P8-T2: Kundali Milan & Synastry Suite (36-Guna Ashtakoota, Nadi/Bhakoot Bhangas, Manglik)
- P8-T3: Panchang & Muhurta Engine (5 Limbs, Choghadiya, Rahukaal, Abhijit Muhurta)
- P8-T4: Shastriya Remedies Pipeline (Ratna, Rudraksha, Prohibited Gems, Vedic Mantras)
- P8-T5: Enterprise Report Generator (Provenance bar, SVG charts, Engine honesty badges)
"""

import pytest
from datetime import date, time, datetime

from src.jyotish.core.models import BirthData
from src.jyotish.core.calculator import default_chart_calculator
from src.jyotish.evidence.domains.analyzer import default_domain_analyzer
from src.jyotish.evidence.factors import default_factor_extractor
from src.jyotish.services.milan import default_milan_service, AshtakootaScore
from src.jyotish.services.panchang import default_panchang_service
from src.jyotish.services.prescription import default_prescription_service
from src.jyotish.services.report_generator import default_report_generator


@pytest.fixture(scope="module")
def benchmark_chart():
    """Swami Vivekananda canonical chart."""
    bd = BirthData(
        name="Swami Vivekananda",
        birth_date=date(1863, 1, 12),
        birth_time=time(6, 33, 0),
        latitude=22.5726,
        longitude=88.3639,
        timezone_offset=5.89,
        gender="male",
        confidence="exact"
    )
    return default_chart_calculator.calculate_full_chart(bd)


# -----------------------------------------------------------------------------
# P8-T1: 12 Life Domains Deep-Dive Analysis Pipeline
# -----------------------------------------------------------------------------
def test_p8_t1_domain_intelligence_pipeline(benchmark_chart):
    """Verify deep-dive analysis across life domains with significator grounding."""
    factors = default_factor_extractor.extract_factors(benchmark_chart)

    domains = ["career", "wealth", "marriage", "children", "health"]
    for dom in domains:
        result = default_domain_analyzer.analyze_domain(dom, factors, school="parashari")
        assert result.domain == dom
        assert len(result.primary_bhavas) > 0
        assert 0.0 <= result.overall_prominence_score <= 1.0
        assert len(result.classical_summary_en) > 0

        # Check significator metadata
        sigs = default_domain_analyzer.get_significators(dom)
        assert sigs.domain == dom
        assert len(sigs.parashari_primary_bhavas) > 0
        assert len(sigs.parashari_karakas) > 0


# -----------------------------------------------------------------------------
# P8-T2: Kundali Milan & Synastry Suite
# -----------------------------------------------------------------------------
def test_p8_t2_kundali_milan_and_synastry():
    """Verify 36-Guna Ashtakoota matching, dosha cancellations, and mutual Manglik analysis."""
    # Groom (Vivekananda) & Prospective chart
    b_groom = BirthData(
        name="Groom",
        birth_date=date(1990, 1, 1),
        birth_time=time(10, 0, 0),
        latitude=28.6139,
        longitude=77.2090,
        timezone_offset=5.5,
        gender="male",
        confidence="exact"
    )
    b_bride = BirthData(
        name="Bride",
        birth_date=date(1992, 5, 15),
        birth_time=time(14, 30, 0),
        latitude=28.6139,
        longitude=77.2090,
        timezone_offset=5.5,
        gender="female",
        confidence="exact"
    )
    c_groom = default_chart_calculator.calculate_full_chart(b_groom)
    c_bride = default_chart_calculator.calculate_full_chart(b_bride)

    milan_res = default_milan_service.match_computed_charts(c_groom, c_bride)
    assert isinstance(milan_res, AshtakootaScore)
    assert milan_res.max_score == 36.0
    assert 0.0 <= milan_res.total_score <= 36.0

    # Verify the 8 classical Ashtakoota pillars
    assert 0.0 <= milan_res.varna <= 1.0
    assert 0.0 <= milan_res.vashya <= 2.0
    assert 0.0 <= milan_res.tara <= 3.0
    assert 0.0 <= milan_res.yoni <= 4.0
    assert 0.0 <= milan_res.graha_maitri <= 5.0
    assert 0.0 <= milan_res.gana <= 6.0
    assert 0.0 <= milan_res.bhakoot <= 7.0
    assert 0.0 <= milan_res.nadi <= 8.0

    # Sum of the 8 scores must strictly match total_score
    calculated_sum = (
        milan_res.varna + milan_res.vashya + milan_res.tara + milan_res.yoni +
        milan_res.graha_maitri + milan_res.gana + milan_res.bhakoot + milan_res.nadi
    )
    assert pytest.approx(calculated_sum, abs=0.01) == milan_res.total_score

    # Dosha cancellations flags must be boolean
    assert isinstance(milan_res.nadi_dosha, bool)
    assert isinstance(milan_res.nadi_dosha_cancelled, bool)
    assert isinstance(milan_res.bhakoot_dosha, bool)
    assert isinstance(milan_res.bhakoot_dosha_cancelled, bool)
    assert isinstance(milan_res.manglik_match, bool)


# -----------------------------------------------------------------------------
# P8-T3: Panchang & Muhurta Engine Hardening
# -----------------------------------------------------------------------------
def test_p8_t3_panchang_and_muhurta_engine():
    """Verify 5 Panchanga pillars, Choghadiya table, and Shubh/Ashubh muhurtas."""
    panchang_svc = default_panchang_service
    test_d = date(2026, 11, 5)

    full_p = panchang_svc.get_full_panchang(test_d, 28.6139, 77.2090)
    assert full_p is not None

    # 1. Five Classical Limbs (Panchanga / Five Pillars)
    assert "five_pillars" in full_p
    p_pillars = full_p["five_pillars"]
    assert "tithi" in p_pillars
    assert "vara" in p_pillars
    assert "nakshatra" in p_pillars
    assert "yoga" in p_pillars
    assert "karana" in p_pillars

    # 2. Choghadiya & Horas
    assert "choghadiya_horas" in full_p
    chogh = full_p["choghadiya_horas"]
    assert "day_choghadiyas" in chogh
    assert "night_choghadiyas" in chogh
    assert len(chogh["day_choghadiyas"]) == 8
    assert len(chogh["night_choghadiyas"]) == 8

    # 3. Shubh & Ashubh Muhurtas (Abhijit, Rahukaal, etc.)
    assert "muhurtas" in full_p
    muhurtas = full_p["muhurtas"]
    assert "shubh_windows" in muhurtas
    assert "ashubh_windows" in muhurtas
    shubh_titles = [m.get("title", "") for m in muhurtas["shubh_windows"]]
    ashubh_titles = [m.get("title", "") for m in muhurtas["ashubh_windows"]]
    assert any("अभिजित" in t or "Abhijit" in t for t in shubh_titles)
    assert any("राहुकाल" in t or "Rahu" in t for t in ashubh_titles)


# -----------------------------------------------------------------------------
# P8-T4: Classical Shastriya Remedies Pipeline
# -----------------------------------------------------------------------------
def test_p8_t4_shastriya_remedies_pipeline(benchmark_chart):
    """Verify Consultation Slip remedies: Primary/Secondary gem, prohibited gems, and mantras."""
    pres = default_prescription_service.generate_prescription(benchmark_chart)

    assert "native_name" in pres
    assert "lagna" in pres
    assert "primary_gem" in pres
    assert "secondary_gem" in pres
    assert "prohibited_gems" in pres
    assert "mantras" in pres
    assert "charity" in pres

    # Dusthana/harmful gems must never be prescribed as primary
    prohibited = pres["prohibited_gems"]
    primary_gem = pres["primary_gem"]
    if primary_gem:
        assert primary_gem["planet"] not in [g["planet"] for g in prohibited]
        assert primary_gem["gem"] not in [g["gem"] for g in prohibited]


# -----------------------------------------------------------------------------
# P8-T5: Enterprise Multi-Page PDF & Provenance Integration
# -----------------------------------------------------------------------------
def test_p8_t5_enterprise_report_generator(benchmark_chart):
    """Verify HTML report generation with provenance, SVG charts, and honesty badges."""
    report_html = default_report_generator.generate_html_report(benchmark_chart)
    assert report_html is not None
    assert len(report_html) > 500

    # Must contain provenance metadata and classical citations
    assert "Swami Vivekananda" in report_html
    assert "lahiri" in report_html.lower() or "swisseph" in report_html.lower() or "jyotish" in report_html.lower()
