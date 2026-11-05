"""
Phase 6 Comprehensive Test Suite: Prashna, BTR & Multi-System Intelligence.
Validates tasks P6-T1 through P6-T5:
- P6-T1: Autonomous Prashna (Horary) Engine & Daivajna Authenticity (Prashna Marga).
- P6-T2: Systemic Isolation: Natal Kundali vs Prashna Kundali & Divergence Reporting.
- P6-T3: Advanced BTR Engine (Boundary Scan, Kunda/Tattwa Shodhana, Multi-Event Fit).
- P6-T4: KP Horary 1-249 Sub-Lord Table & 4-Fold Significations & Ruling Planets.
- P6-T5: Tajika Varshaphal Engine (Muntha Progression, Varshesha, Sahams, Yogas).
"""

import pytest
from datetime import date, time, datetime

from src.jyotish.core.models import BirthData
from src.jyotish.core.calculator import default_chart_calculator
from src.jyotish.services.prashna import default_prashna_service, PrashnaService
from src.jyotish.services.btr import BTRService, default_btr_service, LifeEvent
from src.jyotish.core.kp import default_kp_engine, KPEngine
from src.jyotish.services.varshaphal import VarshaphalService


@pytest.fixture(scope="module")
def benchmark_chart():
    """Swami Vivekananda benchmark chart."""
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
# P6-T1: Autonomous Prashna Engine & Daivajna Authenticity
# -----------------------------------------------------------------------------
def test_p6_t1_prashna_engine_and_daivajna_authenticity():
    """Verify Prashna Kundali calculation, Tajika aspect/yoga, and Daivajna Authenticity."""
    prashna_res = default_prashna_service.generate_prashna_chart(
        query_text="Will my new professional venture succeed?",
        category_name="Career",
        latitude=28.6139,
        longitude=77.2090,
        timezone_offset=5.5,
        query_dt=datetime(2026, 11, 5, 14, 30, 0)
    )

    assert prashna_res is not None
    assert prashna_res["category"] == "Career"
    assert prashna_res["karya_house_num"] == 10
    assert len(prashna_res["karyesh_name"]) > 0
    assert len(prashna_res["lagnesh_name"]) > 0
    assert "tajika_yoga" in prashna_res
    assert isinstance(prashna_res["is_ithasala"], bool)
    assert 0.0 <= prashna_res["verdict_score"] <= 1.0

    # Daivajna Authenticity Check (Prashna Marga)
    assert "daivajna_authenticity" in prashna_res
    auth = prashna_res["daivajna_authenticity"]
    assert "is_authentic" in auth
    assert "authenticity_score" in auth
    assert 0.0 <= auth["authenticity_score"] <= 1.0
    assert "is_lagna_sandhi" in auth
    assert isinstance(auth["caveats"], list)


# -----------------------------------------------------------------------------
# P6-T2: Systemic Isolation: Natal vs Prashna Kundali
# -----------------------------------------------------------------------------
def test_p6_t2_natal_vs_prashna_systemic_isolation(benchmark_chart):
    """Verify Natal and Prashna evaluations remain strictly decoupled with divergence reporting."""
    prashna_res = default_prashna_service.generate_prashna_chart(
        query_text="Will career advancement happen soon?",
        category_name="Career",
        latitude=22.5726,
        longitude=88.3639,
        timezone_offset=5.89,
        query_dt=datetime(1893, 9, 11, 10, 0, 0)
    )

    comparison = default_prashna_service.compare_natal_and_prashna(
        natal_chart=benchmark_chart,
        prashna_result=prashna_res,
        domain="career"
    )

    assert comparison["domain"] == "career"
    assert comparison["target_house"] == 10
    assert comparison["natal_verdict"] in ["Favorable", "Obstructed"]
    assert comparison["prashna_verdict"] in ["Favorable", "Obstructed"]
    assert "consensus_status" in comparison
    assert isinstance(comparison["is_aligned"], bool)
    assert len(comparison["summary_en"]) > 0
    assert len(comparison["summary_hi"]) > 0


# -----------------------------------------------------------------------------
# P6-T3: Advanced BTR (Birth Time Rectification) Engine
# -----------------------------------------------------------------------------
def test_p6_t3_btr_shodhana_and_boundary_scan(benchmark_chart):
    """Verify BTR Shodhana techniques (Kunda, Tattwa, Pranapada) and boundary scan."""
    btr_svc = default_btr_service

    # 1. Kunda & Pranapada Shodhana
    kunda_res = btr_svc.calculate_kunda_pranapada(benchmark_chart, benchmark_chart.birth_data)
    assert "kunda_nakshatra_num" in kunda_res
    assert "kunda_status" in kunda_res
    assert "pranapada_longitude" in kunda_res
    assert 0.0 <= kunda_res["kunda_score"] <= 100.0

    # 2. Tattwa Shodhana
    tattwa_res = btr_svc.calculate_tattwa_shodhana(benchmark_chart.birth_data, gender="male")
    assert "maha_tattwa" in tattwa_res
    assert "antar_tattwa" in tattwa_res
    assert "score" in tattwa_res

    # 3. Divisional Boundary Precision Scan (D1, D9, D10, D60)
    div_res = btr_svc.calculate_divisional_boundaries(benchmark_chart, benchmark_chart.birth_data)
    assert "d1_progress_pct" in div_res
    assert "d9_progress_pct" in div_res
    assert "d60_progress_pct" in div_res

    # 4. Multi-Event Candidate Scanning
    events = [
        LifeEvent(
            event_date=date(1893, 9, 11),
            event_category="career",
            description="Chicago Parliament of Religions"
        )
    ]
    candidates = btr_svc.rectify_birth_time(
        base_birth_data=benchmark_chart.birth_data,
        events=events,
        window_minutes=4,
        step_minutes=2,
        gender="male"
    )
    assert len(candidates) > 0
    for cand in candidates:
        assert 0.0 <= cand.fit_score <= 100.0
        assert len(cand.candidate_time) > 0
        assert cand.matching_events_count >= 0


# -----------------------------------------------------------------------------
# P6-T4: KP Horary (1-249 Sub-Lord System) & 4-Fold Significators
# -----------------------------------------------------------------------------
def test_p6_t4_kp_249_table_and_horary_engine(benchmark_chart):
    """Verify complete 1-249 Sub-Lord Table, 4-fold significations, and KP query prediction."""
    # 1. Table boundaries
    first_sub = default_kp_engine.get_horary_number_detail(1)
    last_sub = default_kp_engine.get_horary_number_detail(249)
    assert first_sub["number"] == 1
    assert first_sub["sign_name"] == "Aries"
    assert first_sub["star_lord"] == "Ketu"
    assert first_sub["sub_lord"] == "Ketu"

    assert last_sub["number"] == 249
    assert last_sub["sign_name"] == "Pisces"
    assert last_sub["star_lord"] == "Mercury"
    assert last_sub["sub_lord"] == "Jupiter"

    # 2. Complete 249 table size
    table = default_kp_engine.get_all_249_table()
    assert len(table) in (249, 250)

    # 3. 4-Fold Significations & Chart KP
    kp_data = default_kp_engine.calculate_chart_kp(benchmark_chart)
    assert "cusps_kp" in kp_data
    assert len(kp_data["cusps_kp"]) == 12
    assert "planet_significations" in kp_data
    assert "ruling_planets" in kp_data

    # 4. KP Query Prediction
    kp_query = default_kp_engine.predict_kp_query(
        chart=benchmark_chart,
        query_key="JOB_CAREER",
        horary_num=108,
        query_text="Will Vivekananda's global mission succeed?"
    )
    assert kp_query["query_key"] == "JOB_CAREER"
    assert 0 <= kp_query["confidence_score"] <= 100
    assert len(kp_query["verdict_badge"]) > 0
    assert "primary_csl" in kp_query
    assert "ruling_planets_active" in kp_query


# -----------------------------------------------------------------------------
# P6-T5: Tajika Varshaphal & Annual Progression Engine
# -----------------------------------------------------------------------------
def test_p6_t5_tajika_varshaphal_and_sahams(benchmark_chart):
    """Verify Tajika Solar Return calculation, Muntha progression, Varshesha, and Sahams."""
    varsha_svc = VarshaphalService()
    target_year = 1893  # Age 30
    varsha_res = varsha_svc.calculate_varshaphal(benchmark_chart, target_year)

    assert varsha_res is not None
    assert varsha_res["target_year"] == 1893
    assert "varsha_chart" in varsha_res

    # 1. Muntha Progression
    assert "muntha_sign" in varsha_res
    assert "muntha_house" in varsha_res
    assert 1 <= varsha_res["muntha_house"] <= 12

    # 2. Varshesha Selection (Lord of the Year)
    assert len(varsha_res["varshesha"]) > 0
    assert "varshesha_candidates_scored" in varsha_res
    assert len(varsha_res["varshesha_candidates_scored"]) == 5

    # 3. Canonical Sahams
    assert "sahams" in varsha_res
    sahams = varsha_res["sahams"]
    assert len(sahams) >= 20  # Punya, Vidya, Karma, etc.
    saham_names = [s["saham_en"] for s in sahams]
    assert any("Punya" in name for name in saham_names)
    assert any("Karma" in name for name in saham_names)

    # 4. Panchavargiya Bala
    assert "panchavargiya_bala" in varsha_res
    assert len(varsha_res["panchavargiya_bala"]) > 0
    for b_data in varsha_res["panchavargiya_bala"]:
        assert 0.0 <= b_data["vishopaka"] <= 20.0
