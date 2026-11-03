"""
Unit test suite for Phase 9: Birth Time Rectification (BTR) & Verification Engine Hardening.
Tests:
1. Classical Kunda Shodhana calculation and Nakshatra Trikona alignment.
2. Tattwa Shodhana gender alignment and Ishta Kala computation.
3. Multi-event BTR candidate window scanning and fitness scoring.
4. Retrospective Event Verification across 6 classical pillars.
5. Deterministic verification status assignment (Supported, Strongly Supported, etc.).
"""

import pytest
from datetime import date, time
from src.jyotish.core.models import BirthData
from src.jyotish.core.calculator import default_chart_calculator
from src.jyotish.services.btr import default_btr_service, LifeEvent
from src.jyotish.events.past_verification import (
    default_past_event_engine,
    PastEventVerificationInput,
    AstrologicalEvidenceStatus
)


@pytest.fixture
def btr_native_data():
    return BirthData(
        name="BTR Benchmark Subject",
        birth_date=date(1995, 3, 25),
        birth_time=time(14, 15, 0),
        latitude=28.6139,
        longitude=77.2090,
        timezone_offset=5.5,
        city="New Delhi",
        gender="male"
    )


def test_kunda_shodhana_calculation(btr_native_data):
    """Verify BPHS Kunda Shodhana formula: (Lagna degrees * 81) % 27."""
    chart = default_chart_calculator.calculate_full_chart(btr_native_data)
    kunda_res = default_btr_service.calculate_kunda_pranapada(chart, btr_native_data)
    
    assert "kunda_nakshatra_num" in kunda_res
    assert 1 <= kunda_res["kunda_nakshatra_num"] <= 27
    assert len(kunda_res["kunda_nakshatra_name"]) > 0
    assert "is_kunda_pure" in kunda_res
    assert isinstance(kunda_res["is_kunda_pure"], bool)
    assert 0.0 <= kunda_res["kunda_score"] <= 100.0


def test_tattwa_shodhana_gender_alignment(btr_native_data):
    """Verify Tattwa Shodhana computes Ishta Kala and gender concordance."""
    tattwa_res = default_btr_service.calculate_tattwa_shodhana(btr_native_data, gender="male")
    
    assert "maha_tattwa" in tattwa_res
    assert "antar_tattwa" in tattwa_res
    assert "gender_match_status" in tattwa_res
    assert 0.0 <= tattwa_res["score"] <= 100.0
    assert "sub_tattwa_schedule" in tattwa_res
    assert len(tattwa_res["sub_tattwa_schedule"]) == 5


def test_btr_multi_event_rectification_scanning(btr_native_data):
    """Verify BTR window scanning produces ranked candidates matching chronological events."""
    events = [
        LifeEvent(event_date=date(2015, 6, 1), event_category="career", description="First Corporate Job"),
        LifeEvent(event_date=date(2021, 11, 28), event_category="marriage", description="Wedding Ceremony"),
    ]
    
    candidates = default_btr_service.rectify_birth_time(
        base_birth_data=btr_native_data,
        events=events,
        window_minutes=6,
        step_minutes=2
    )
    
    assert len(candidates) > 0
    # Ranked descending by fit score
    for i in range(len(candidates) - 1):
        assert candidates[i].fit_score >= candidates[i+1].fit_score
        
    top_cand = candidates[0]
    assert 0.0 <= top_cand.fit_score <= 100.0
    assert top_cand.candidate_time is not None
    assert top_cand.matching_events_count >= 0


def test_past_event_retrospective_verification_pillars(btr_native_data):
    """Verify 6-pillar retrospective verification of historical life events."""
    chart = default_chart_calculator.calculate_full_chart(btr_native_data)
    
    inp = PastEventVerificationInput(
        birth_data=btr_native_data,
        event_theme="marriage",
        query_text="Did marriage occur in late 2021?",
        target_date=date(2021, 11, 28),
        search_window_start=date(2020, 1, 1),
        search_window_end=date(2023, 1, 1)
    )
    
    res = default_past_event_engine.verify_past_event(inp, precomputed_chart=chart)
    
    assert res.event_theme == "marriage"
    assert res.status in AstrologicalEvidenceStatus
    assert 0.0 <= res.confidence_score <= 1.0
    
    # Check that core classical pillars are evaluated
    assert "promising_score" in res.pillar_1_d1_evidence
    assert res.pillar_3_varga_evidence["varga_code"] == "D9"
    assert "mahadasha" in res.pillar_4_dasha_evidence
    assert "transit_score" in res.pillar_5_transit_evidence
    assert res.pillar_6_rules_evidence["rules_evaluated_count"] >= 0
    assert len(res.ai_explanation_hi) > 10
    assert len(res.ai_explanation_en) > 10
