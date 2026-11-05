"""
Phase 5 Comprehensive Multi-Layer Event Prediction & Timing Engine Test Suite.
Validates tasks P5-T1 through P5-T4:
- P5-T1: Canonical Jyotish Event Taxonomy & Significator Mapping
- P5-T2: 5-Level Event Fruition Engine (Natal, Varga, Dasha, Double Transit, Yogas)
- P5-T3: Decoupled Planetary Capability vs Activation & Threshold Replacement in Ghatna
- P5-T4: Past Event Verification Lab & Historical Benchmark Calibration
"""

import pytest
from datetime import date, time

from src.jyotish.core.models import BirthData
from src.jyotish.core.calculator import default_chart_calculator
from src.jyotish.events.taxonomy import (
    default_event_taxonomy,
    EventDefinition,
    CANONICAL_EVENTS
)
from src.jyotish.events.multi_layer_engine import (
    default_multi_layer_engine,
    MultiLayerPredictionResult,
    EventFruitionState,
    LAYER_WEIGHTS
)
from src.jyotish.events.ghatna import (
    default_ghatna_engine,
    GhatnaQueryResult
)
from src.jyotish.events.past_verification import (
    default_past_event_engine,
    PastEventVerificationEngine,
    PastEventVerificationResult,
    AstrologicalEvidenceStatus
)


@pytest.fixture(scope="module")
def benchmark_chart():
    """Canonical Swami Vivekananda birth chart."""
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
# P5-T1: Canonical Event Taxonomy & Significator Mapping
# -----------------------------------------------------------------------------
def test_p5_t1_canonical_event_taxonomy():
    """Verify all major life events exist with classical bhavas, karakas, and vargas."""
    events = default_event_taxonomy.list_all_events()
    assert len(events) >= 8

    # 1. Career Recognition
    career_ev = default_event_taxonomy.get_event("career_recognition")
    assert career_ev is not None
    assert career_ev.domain == "career"
    assert 10 in career_ev.primary_houses
    assert "Sun" in career_ev.primary_karakas
    assert career_ev.varga == "D10"

    # 2. Marriage
    marriage_ev = default_event_taxonomy.get_event("marriage")
    assert marriage_ev is not None
    assert marriage_ev.domain == "marriage"
    assert 7 in marriage_ev.primary_houses
    assert "Venus" in marriage_ev.primary_karakas
    assert marriage_ev.varga == "D9"

    # 3. Childbirth / Progeny
    progeny_ev = default_event_taxonomy.get_event("childbirth")
    assert progeny_ev is not None
    assert progeny_ev.domain == "progeny"
    assert 5 in progeny_ev.primary_houses
    assert "Jupiter" in progeny_ev.primary_karakas
    assert progeny_ev.varga == "D7"

    # 4. Property Purchase
    prop_ev = default_event_taxonomy.get_event("property_purchase")
    assert prop_ev is not None
    assert 4 in prop_ev.primary_houses
    assert "Mars" in prop_ev.primary_karakas
    assert prop_ev.varga == "D4"

    # 5. Domain query
    career_list = default_event_taxonomy.get_events_for_domain("career")
    assert len(career_list) >= 3


# -----------------------------------------------------------------------------
# P5-T2: 5-Level Event Fruition Architecture
# -----------------------------------------------------------------------------
def test_p5_t2_multi_layer_prediction_engine(benchmark_chart):
    """Verify 5-level pipeline evaluates with calibrated weights summing to 1.0."""
    # Check weights sum strictly to 1.000
    total_w = sum(LAYER_WEIGHTS.values())
    assert pytest.approx(total_w, abs=0.001) == 1.0

    # Historical event: Chicago Parliament of Religions (11-Sep-1893)
    target_date = date(1893, 9, 11)
    result = default_multi_layer_engine.evaluate_event(
        chart=benchmark_chart,
        event_id="career_recognition",
        target_date=target_date
    )

    assert isinstance(result, MultiLayerPredictionResult)
    assert result.event_id == "career_recognition"
    assert result.target_date == target_date
    assert 0.0 <= result.timing_confidence <= 1.0
    assert isinstance(result.fruition_state, EventFruitionState)

    # All 5 layers must be present
    assert len(result.level_breakdown) == 5
    for key in ["level_1_natal", "level_2_varga", "level_3_dasha", "level_4_transit", "level_5_yoga"]:
        assert key in result.level_breakdown
        lvl = result.level_breakdown[key]
        assert 0.0 <= lvl.score <= 1.0
        assert lvl.weight > 0.0
        assert lvl.contribution >= 0.0

    # Vivekananda was in Jupiter MD / Jupiter AD in Sept 1893 (Lagna Lord activation)
    assert result.active_md_lord == "Jupiter"
    assert result.active_ad_lord == "Jupiter"
    assert result.fruition_state == EventFruitionState.HIGH_FRUITION_WINDOW
    assert result.double_transit_active is True
    assert result.timing_confidence >= 0.70
    assert len(result.summary_en) > 0
    assert len(result.summary_hi) > 0


# -----------------------------------------------------------------------------
# P5-T3: Ghatna Query Engine Unified with 5-Level Pipeline
# -----------------------------------------------------------------------------
def test_p5_t3_ghatna_engine_multi_layer_integration(benchmark_chart):
    """Verify GhatnaQueryEngine uses the 5-layer pipeline and evidence packs."""
    target_date = date(1893, 9, 11)
    ghatna_res = default_ghatna_engine.evaluate_event_window(
        birth_data=benchmark_chart.birth_data,
        target_date=target_date,
        domain="career"
    )

    assert isinstance(ghatna_res, GhatnaQueryResult)
    assert ghatna_res.domain == "career"
    assert ghatna_res.target_date == target_date
    assert isinstance(ghatna_res.is_window_active, bool)
    assert 0.0 <= ghatna_res.timing_confidence <= 1.0
    assert ghatna_res.event_id == "career_recognition"
    assert ghatna_res.fruition_state in [s.value for s in EventFruitionState]
    assert ghatna_res.level_breakdown is not None
    assert len(ghatna_res.level_breakdown) == 5

    # Grounded evidence pack must contain findings
    assert ghatna_res.grounded_evidence_pack is not None
    assert len(ghatna_res.grounded_evidence_pack.findings) > 0


# -----------------------------------------------------------------------------
# P5-T4: Past Event Verification Lab & Historical Calibration
# -----------------------------------------------------------------------------
def test_p5_t4_past_event_verification_lab(benchmark_chart):
    """Verify retrospective event verification on verified historical benchmark."""
    target_date = date(1893, 9, 11)
    res = default_past_event_engine.verify_benchmark_event(
        birth_data=benchmark_chart.birth_data,
        event_id="career_recognition",
        target_date=target_date,
        query_text="Did Vivekananda achieve world renown at the Chicago Parliament in 1893?"
    )

    assert isinstance(res, PastEventVerificationResult)
    assert res.target_date == target_date
    # Must be supported or strongly supported on this canonical event
    assert res.status in (
        AstrologicalEvidenceStatus.STRONGLY_SUPPORTED,
        AstrologicalEvidenceStatus.SUPPORTED
    )
    assert res.confidence_score >= 0.60

    # Verify all 6 retrospective pillars
    assert res.pillar_1_d1_evidence["primary_house"] == 10
    assert res.pillar_3_varga_evidence["varga_code"] == "D10"
    assert "mahadasha" in res.pillar_4_dasha_evidence
    assert "transit_date" in res.pillar_5_transit_evidence
    assert res.pillar_6_rules_evidence["rules_evaluated_count"] > 0
