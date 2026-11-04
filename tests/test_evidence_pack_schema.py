"""
Unit tests for Evidence Pack Generation & JSON Schema Validation (Phase 5, Task P5-T3).
Reference: docs/IMPLEMENTATION_PRD.md (Section 5.3 & 5.4, P5-T3).

Verifies:
1. Complete Evidence Pack generation for Vivekananda benchmark chart.
2. Strict adherence to JSON schema structure.
3. Every finding possesses immutable finding_id ('F1', 'F2', etc.), verified rule_ids,
   calibrated strength (0.0 to 1.0), and non-empty bilingual claims.
4. Classical disclaimers are present.
"""

import sys
import os
import pytest
from datetime import date, datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from jyotish.core.models import BirthData
from jyotish.core.calculator import default_chart_calculator
from jyotish.evidence.pack import (
    EvidencePack,
    EvidenceFinding,
    EvidencePackBuilder,
    default_evidence_pack_builder
)


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


def test_evidence_pack_generation(benchmark_chart):
    """Verify building Evidence Pack for Career domain."""
    pack: EvidencePack = default_evidence_pack_builder.build_evidence_pack(
        chart=benchmark_chart,
        domain="career",
        school="parashari"
    )

    assert pack.domain == "career"
    assert pack.school == "parashari"
    assert pack.chart_meta["engine"] == "swisseph"
    assert pack.chart_meta["ayanamsa"] == "lahiri"
    assert len(pack.findings) > 0
    assert len(pack.disclaimers) > 0

    # Verify Findings
    for idx, f in enumerate(pack.findings, start=1):
        assert f.finding_id == f"F{idx}"
        assert len(f.rule_ids) > 0
        assert f.polarity in ("+", "-")
        assert 0.0 <= f.strength <= 1.0
        assert len(f.claim_en) > 10
        assert len(f.claim_hi) > 10
        assert isinstance(f.strength_reason, list)
        assert isinstance(f.caveats, list)


def test_evidence_pack_json_schema():
    """Verify EvidencePack exports valid JSON Schema."""
    schema = EvidencePack.export_json_schema()

    assert "properties" in schema
    assert "findings" in schema["properties"]
    assert "chart_meta" in schema["properties"]
    assert "domain" in schema["properties"]
    assert "school" in schema["properties"]


def test_evidence_pack_serialization(benchmark_chart):
    """Verify EvidencePack serialization to JSON dict and reloading."""
    pack = default_evidence_pack_builder.build_evidence_pack(
        chart=benchmark_chart,
        domain="wealth",
        school="parashari"
    )

    data = pack.model_dump()
    assert isinstance(data, dict)
    assert data["domain"] == "wealth"
    assert len(data["findings"]) > 0

    reloaded = EvidencePack.model_validate(data)
    assert reloaded.domain == pack.domain
    assert len(reloaded.findings) == len(pack.findings)
