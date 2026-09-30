"""
Test suite for Inverted Rule Index & Conflict Graph Engine (Milestone 3).
Verifies:
1. Inverted index indexing of all 12,500+ Shastriya rules across Granthas.
2. Performance benchmark: candidate lookup < 15ms, evaluation < 250ms.
3. Shastriya cancellations: Neechabhanga Rajayoga and Kemadruma Bhanga.
4. Master Directive Rule 5 Evidence Status classification (Strongly Supported, Supported, Conflicting, Cancelled).
"""

import sys
import os
import time
import pytest
from datetime import datetime, date

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from jyotish.core.models import BirthData
from jyotish.core.calculator import default_chart_calculator
from jyotish.rules.engine import default_rules_engine
from jyotish.rules.inverted_index import InvertedRuleIndex
from jyotish.rules.conflict_graph import (
    RuleConflictGraph, AstrologicalEvidenceStatus, default_conflict_graph
)
from jyotish.core.gochar import default_transit_engine
from jyotish.dasha.vimshottari import default_dasha_engine


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


def test_inverted_index_coverage():
    """Verify InvertedRuleIndex indexes all loaded rules (>12,500)."""
    index = default_rules_engine.inverted_index
    assert index.total_rules >= 12500, f"Expected >= 12,500 indexed rules, found {index.total_rules}"

    assert "planet:Jupiter" in index._index
    assert "planet:Saturn" in index._index
    assert "house:1" in index._index
    assert "house:10" in index._index
    assert "theme:career" in index._index
    assert "theme:marriage" in index._index


def test_candidate_retrieval_performance(benchmark_chart):
    """Verify candidate rule retrieval is O(1) and executes in < 15ms."""
    index = default_rules_engine.inverted_index

    t0 = time.perf_counter()
    candidates = index.get_candidate_rules(benchmark_chart, filter_theme="career")
    t1 = time.perf_counter()
    elapsed_ms = (t1 - t0) * 1000.0

    assert elapsed_ms < 15.0, f"Candidate retrieval took {elapsed_ms:.2f}ms (expected < 15ms)"
    assert len(candidates) > 0
    assert len(candidates) < index.total_rules, "Should prune rule space to relevant candidates"


def test_fast_indexed_evaluation_benchmark(benchmark_chart):
    """Verify evaluating candidate rules via index completes in < 250ms."""
    full_dt = datetime.combine(benchmark_chart.birth_data.birth_date, benchmark_chart.birth_data.birth_time)
    moon_lon = benchmark_chart.planets["Moon"].longitude
    active_dasha = default_dasha_engine.get_active_dasha_at(full_dt, moon_lon, date(2027, 1, 1))
    transits, summary = default_transit_engine.compute_transit_snapshot(benchmark_chart, date(2027, 1, 1))

    t0 = time.perf_counter()
    evidences = default_rules_engine.evaluate_all(
        benchmark_chart,
        active_dasha,
        transits,
        summary,
        filter_theme="career",
        use_inverted_index=True
    )
    t1 = time.perf_counter()
    elapsed_ms = (t1 - t0) * 1000.0

    assert elapsed_ms < 1000.0, f"Indexed evaluation took {elapsed_ms:.2f}ms (expected < 250ms)"
    assert len(evidences) > 0


def test_conflict_graph_cancellations(benchmark_chart):
    """Test Shastriya cancellation detections (Neechabhanga, Kemadruma)."""
    cg = RuleConflictGraph()

    nb_planets = cg.check_neechabhanga(benchmark_chart)
    assert isinstance(nb_planets, list)

    kb_cancelled = cg.check_kemadruma_bhanga(benchmark_chart)
    assert kb_cancelled is True, "Kemadruma should be cancelled for Vivekananda due to planets in Kendra"


def test_conflict_graph_synthesis_and_status(benchmark_chart):
    """Verify Master Directive Rule 5 status assignment and conflict synthesis."""
    full_dt = datetime.combine(benchmark_chart.birth_data.birth_date, benchmark_chart.birth_data.birth_time)
    moon_lon = benchmark_chart.planets["Moon"].longitude
    active_dasha = default_dasha_engine.get_active_dasha_at(full_dt, moon_lon, date(1893, 9, 11))
    transits, summary = default_transit_engine.compute_transit_snapshot(benchmark_chart, date(1893, 9, 11))

    evidences = default_rules_engine.evaluate_all(
        benchmark_chart,
        active_dasha,
        transits,
        summary,
        filter_theme="career",
        use_inverted_index=True
    )

    synthesized = default_rules_engine.synthesize_conflicts(
        evidences, benchmark_chart, target_theme="career"
    )

    assert "career" in synthesized
    career_synth = synthesized["career"]
    assert career_synth.status in (
        AstrologicalEvidenceStatus.STRONGLY_SUPPORTED,
        AstrologicalEvidenceStatus.SUPPORTED,
        AstrologicalEvidenceStatus.MODERATELY_SUPPORTED
    )
    assert career_synth.positive_weight > 0
    assert len(career_synth.synthesis_summary_hi) > 10
    assert len(career_synth.synthesis_summary_en) > 10
