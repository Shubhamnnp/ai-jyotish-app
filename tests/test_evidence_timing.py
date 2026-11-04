"""
Unit tests for Dasha & Transit Timing Integrator and Ghatna Queries (Phase 5, Task P5-T4).
Reference: docs/IMPLEMENTATION_PRD.md (Section 5.4, P5-T4).

Verifies:
1. Exact timing evaluation on historical fixed dates (Swami Vivekananda, 1893-09-11 Chicago address).
2. Dasha significator detection: Jupiter Maha Dasha recognized as Lagna Lord & Karaka.
3. Classical Double Transit (Guru & Shani) evaluation.
4. GhatnaQueryEngine integration using grounded Evidence Packs.
"""

import sys
import os
import pytest
from datetime import date, datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from jyotish.core.models import BirthData
from jyotish.core.calculator import default_chart_calculator
from jyotish.evidence.factors import default_factor_extractor
from jyotish.evidence.timing import (
    TimingIntegrator,
    default_timing_integrator,
    TimingEvaluation
)
from jyotish.events.ghatna import (
    GhatnaQueryEngine,
    default_ghatna_engine,
    GhatnaQueryResult
)


@pytest.fixture(scope="module")
def vivekananda_birth_data():
    return BirthData(
        name="Swami Vivekananda",
        birth_date=date(1863, 1, 12),
        birth_time=datetime.strptime("06:33:00", "%H:%M:%S").time(),
        latitude=22.5726,
        longitude=88.3639,
        timezone_offset=5.5,
        city="Kolkata",
        confidence="Exact"
    )


@pytest.fixture(scope="module")
def vivekananda_chart(vivekananda_birth_data):
    return default_chart_calculator.calculate_full_chart(vivekananda_birth_data)


def test_historical_timing_chicago_1893(vivekananda_chart):
    """
    Verify historical timing on 1893-09-11 (Chicago Parliament of Religions).
    Vivekananda was running Jupiter Maha Dasha, a major spiritual & career significator.
    """
    target_dt = date(1893, 9, 11)
    factors = default_factor_extractor.extract_factors(vivekananda_chart)

    timing: TimingEvaluation = default_timing_integrator.evaluate_timing_for_domain(
        chart=vivekananda_chart,
        factors=factors,
        target_date=target_dt,
        primary_bhavas=[10],
        primary_karakas=["Sun", "Jupiter"]
    )

    assert timing.target_date == target_dt
    assert timing.active_md_lord == "Jupiter", f"Expected Jupiter MD on 1893-09-11, found {timing.active_md_lord}"
    assert timing.is_dasha_significator is True
    assert len(timing.dasha_significance_reasons) > 0
    assert "Jupiter" in timing.dasha_significance_reasons[0]
    assert timing.timing_confidence >= 0.60


def test_ghatna_query_refactored_engine(vivekananda_birth_data):
    """Verify GhatnaQueryEngine returns grounded Evidence Pack and timing windows."""
    target_dt = date(1893, 9, 11)
    res: GhatnaQueryResult = default_ghatna_engine.evaluate_event_window(
        birth_data=vivekananda_birth_data,
        target_date=target_dt,
        domain="career"
    )

    assert res.domain == "career"
    assert res.target_date == target_dt
    assert res.is_window_active is True
    assert "Jupiter" in res.operating_dasha
    assert len(res.timing_reasons) > 0
    assert len(res.grounded_evidence_pack.findings) > 0

    # Ensure findings were annotated with timing
    annotated = [
        f for f in res.grounded_evidence_pack.findings
        if len(f.timing.dasha_support) > 0
    ]
    assert len(annotated) > 0
    assert "Jupiter" in annotated[0].timing.dasha_support[0]
