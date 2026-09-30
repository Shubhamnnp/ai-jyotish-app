"""
Test suite for Retrospective Past Event Verification Engine (Milestone 4).
Verifies:
1. Verification of retrospective query: "क्या मेरी शादी हो चुकी है?"
2. Verification across 6 Classical Pillars (D1, Prashna, Varga D9/D10, Dasha, Transit, Shastriya Rules).
3. Status assignment adhering to Master Directive Rule 5 (Supported, Strongly Supported, etc.).
4. Career event verification and Prashna horary integration.
5. Storage and retrieval in relational database (EventVerificationModel).
"""

import sys
import os
import pytest
from datetime import datetime, date

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from jyotish.core.models import BirthData
from jyotish.core.calculator import default_chart_calculator
from jyotish.events.past_verification import (
    PastEventVerificationEngine,
    PastEventVerificationInput,
    default_past_event_engine,
    AstrologicalEvidenceStatus
)
from jyotish.db.session import SessionLocal
from jyotish.db.models import EventVerificationModel, Chart


@pytest.fixture(scope="module")
def benchmark_chart():
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
    return default_chart_calculator.calculate_full_chart(bd)


def test_retrospective_marriage_query(benchmark_chart):
    """Test retrospective marriage verification query on historical Kundali."""
    inp = PastEventVerificationInput(
        birth_data=benchmark_chart.birth_data,
        event_theme="marriage",
        query_text="क्या मेरी शादी हो चुकी है?",
        target_date=date(1890, 1, 1),
        search_window_start=date(1883, 1, 1),
        search_window_end=date(1895, 1, 1)
    )

    res = default_past_event_engine.verify_past_event(inp, precomputed_chart=benchmark_chart)

    assert res.event_theme == "marriage"
    assert res.status in AstrologicalEvidenceStatus
    assert 0.0 <= res.confidence_score <= 1.0

    assert "promising_score" in res.pillar_1_d1_evidence
    assert res.pillar_3_varga_evidence["varga_code"] == "D9"
    assert res.pillar_3_varga_evidence["varga_verified"] is True
    assert "mahadasha" in res.pillar_4_dasha_evidence
    assert "transit_score" in res.pillar_5_transit_evidence
    assert res.pillar_6_rules_evidence["rules_evaluated_count"] > 0

    assert len(res.ai_explanation_hi) > 20
    assert len(res.ai_explanation_en) > 20
    assert "disclaimer_hi" in res.model_dump()


def test_retrospective_career_query_with_prashna(benchmark_chart):
    """Test career verification query integrating Prashna Horary overlay."""
    inp = PastEventVerificationInput(
        birth_data=benchmark_chart.birth_data,
        event_theme="career",
        query_text="Did I achieve international recognition in 1893?",
        target_date=date(1893, 9, 11),
        query_timestamp=datetime(2026, 9, 30, 10, 0, 0),
        query_lat=28.6139,
        query_lon=77.2090
    )

    res = default_past_event_engine.verify_past_event(inp, precomputed_chart=benchmark_chart)

    assert res.event_theme == "career"
    assert res.pillar_2_prashna_evidence is not None
    assert "prashna_lagna_lord" in res.pillar_2_prashna_evidence
    assert res.pillar_3_varga_evidence["varga_code"] == "D10"

    assert res.confidence_score >= 0.50
    assert res.status in (
        AstrologicalEvidenceStatus.STRONGLY_SUPPORTED,
        AstrologicalEvidenceStatus.SUPPORTED,
        AstrologicalEvidenceStatus.MODERATELY_SUPPORTED
    )


def test_database_persistence_of_event_verification(benchmark_chart):
    """Verify that an event verification result can be cleanly stored and retrieved from the enterprise database."""
    inp = PastEventVerificationInput(
        birth_data=benchmark_chart.birth_data,
        event_theme="career",
        query_text="क्या 1893 में मेरा वैश्विक उत्थान हुआ?",
        target_date=date(1893, 9, 11)
    )

    res = default_past_event_engine.verify_past_event(inp, precomputed_chart=benchmark_chart)

    db = SessionLocal()
    try:
        db_chart = db.query(Chart).first()
        assert db_chart is not None

        db_event = EventVerificationModel(
            chart_id=db_chart.id,
            event_theme=res.event_theme,
            query_text=res.query_text,
            candidate_window_start=date(1890, 1, 1),
            candidate_window_end=date(1895, 1, 1),
            status=res.status.value,
            astrological_evidence_score=res.confidence_score,
            d1_evidence=res.pillar_1_d1_evidence,
            prashna_evidence=res.pillar_2_prashna_evidence,
            d9_evidence=res.pillar_3_varga_evidence,
            dasha_evidence=res.pillar_4_dasha_evidence,
            transit_evidence=res.pillar_5_transit_evidence,
            rule_evidence_ids=["KP_CUSP_10", "BPHS_RAJA_YOGA"],
            ai_explanation_hi=res.ai_explanation_hi,
            ai_explanation_en=res.ai_explanation_en
        )
        db.add(db_event)
        db.commit()
        db.refresh(db_event)

        retrieved = db.query(EventVerificationModel).filter_by(id=db_event.id).first()
        assert retrieved is not None
        assert retrieved.event_theme == "career"
        assert retrieved.status == res.status.value
        assert retrieved.astrological_evidence_score == res.confidence_score

        db.delete(retrieved)
        db.commit()
    finally:
        db.close()
