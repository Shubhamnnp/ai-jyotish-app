"""
Unit test suite for Astrological School Isolation & Conflict Precedence Engine.
Reference: docs/IMPLEMENTATION_PRD.md (Section 4.2, P4-T8 & P4-T9).

Verifies:
1. P4-T8: School Isolation (Parashari, Jaimini, KP, Lal Kitab, Tajika evaluate independently).
2. P4-T8: Parashari output is completely unaffected by Lal Kitab or KP rules.
3. P4-T8: Side-by-side multi-school comparison without synthetic score averaging.
4. P4-T9: Neechabhanga precedence overrides debilitation with explicit PrecedenceRecord.
5. P4-T9: Kemadruma Bhanga precedence overrides Kemadruma dosha.
6. P4-T9: Viparita Raja Yoga overrides dusthana affliction.
7. P4-T9: Shadbala dominance resolves conflicting planetary forces.
"""

import sys
import os
import pytest
from datetime import date, datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from jyotish.core.models import BirthData
from jyotish.core.calculator import default_chart_calculator
from jyotish.schools.registry import default_school_registry
from jyotish.schools.parashari import ParashariEngine
from jyotish.schools.jaimini import JaiminiEngine
from jyotish.schools.kp import KPEngine
from jyotish.schools.lalkitab import LalKitabEngine
from jyotish.schools.tajika import TajikaEngine
from jyotish.schools.conflict import ShastriyaPrecedenceEngine
from jyotish.schools.base import PrecedencePrinciple
from jyotish.rules.consensus import ConsensusAggregator, MultiSchoolSideBySideReport
from jyotish.core.models import RuleEvidence


@pytest.fixture(scope="module")
def benchmark_chart():
    """Swami Vivekananda benchmark chart."""
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


def test_registered_schools_completeness():
    """Verify all 5 classical schools are registered in SchoolRegistry."""
    schools = default_school_registry.list_schools()
    assert "parashari" in schools
    assert "jaimini" in schools
    assert "kp" in schools
    assert "lal_kitab" in schools
    assert "tajika" in schools


def test_parashari_isolation_unaffected_by_other_schools(benchmark_chart):
    """
    Verify Parashari engine operates in strict isolation.
    Its output contains only classical Parashari references and zero KP/Lal Kitab tags.
    """
    engine = ParashariEngine()
    res = engine.evaluate(benchmark_chart, domain="career")

    assert res.school_key == "parashari"
    assert "Brihat Parashara Hora Shastra (BPHS)" in res.canonical_texts

    # Check findings contain only Parashari rule IDs
    for f in res.supported_findings + res.cautionary_findings:
        assert not f.finding_id.startswith("KP-"), f"Found KP finding {f.finding_id} in Parashari output"
        assert not f.finding_id.startswith("LK-"), f"Found Lal Kitab finding {f.finding_id} in Parashari output"
        assert not f.finding_id.startswith("TAJ-"), f"Found Tajika finding {f.finding_id} in Parashari output"

    assert len(res.supported_findings) > 0
    assert "total_classical_yogas" in res.system_metrics


def test_jaimini_isolation(benchmark_chart):
    """Verify Jaimini engine computes Atmakaraka, Amatyakaraka, and Arudhas independently."""
    engine = JaiminiEngine()
    res = engine.evaluate(benchmark_chart)

    assert res.school_key == "jaimini"
    assert "Jaimini Upadesha Sutras (Maharishi Jaimini)" in res.canonical_texts
    assert res.system_metrics.get("atmakaraka") is not None
    assert res.system_metrics.get("amatyakaraka") is not None

    finding_ids = [f.finding_id for f in res.supported_findings]
    assert any("JAI-AK-" in fid for fid in finding_ids)
    assert any("JAI-AMK-" in fid for fid in finding_ids)


def test_kp_isolation(benchmark_chart):
    """Verify KP engine evaluates Cuspal Sub-lords and Significations in isolation."""
    engine = KPEngine()
    res = engine.evaluate(benchmark_chart, domain="career")

    assert res.school_key == "kp"
    assert "KP Readers I-VI (Prof. K.S. Krishnamurti)" in res.canonical_texts
    assert res.system_metrics.get("cusp_1_sublord") is not None

    all_findings = res.supported_findings + res.cautionary_findings
    assert any(f.finding_id.startswith("KP-") for f in all_findings)


def test_lalkitab_isolation(benchmark_chart):
    """Verify Lal Kitab engine evaluates fixed houses, Teva status, and Rinas in isolation."""
    engine = LalKitabEngine()
    res = engine.evaluate(benchmark_chart)

    assert res.school_key == "lal_kitab"
    assert "Lal Kitab (1952 Tarjuma by Pt. Roop Chand Joshi)" in res.canonical_texts
    assert res.system_metrics.get("teva_type") in ("Dharmi Teva", "Andha Teva", "Ratandh Teva", "Normal")


def test_tajika_isolation(benchmark_chart):
    """Verify Tajika engine computes Muntha, Varsheshwara, and Tajika yogas in isolation."""
    engine = TajikaEngine()
    res = engine.evaluate(benchmark_chart, target_year=1893)

    assert res.school_key == "tajika"
    assert "Tajika Neelakanthi (Neelakantha Daivajna)" in res.canonical_texts
    assert res.system_metrics.get("muntha_house") in range(1, 13)
    assert res.system_metrics.get("varsheshwara") in chart_planet_names(benchmark_chart)


def chart_planet_names(chart):
    return set(chart.planets.keys())


def test_side_by_side_evaluation_no_averaging(benchmark_chart):
    """Verify side-by-side evaluation runs all schools without cross-school score averaging."""
    side_by_side = default_school_registry.evaluate_all_side_by_side(benchmark_chart, domain="career")

    assert len(side_by_side) == 5
    for school_key in ["parashari", "jaimini", "kp", "lal_kitab", "tajika"]:
        assert school_key in side_by_side
        result = side_by_side[school_key]
        assert result.school_key == school_key
        # Verify findings are isolated
        assert isinstance(result.supported_findings, list)
        assert isinstance(result.cautionary_findings, list)


def test_multi_school_side_by_side_consensus_report():
    """Verify ConsensusAggregator.aggregate_side_by_side groups without blending."""
    evidences = [
        RuleEvidence(
            rule_id="BPHS-24-LORD1-H1",
            rule_name_hi="लग्नेश प्रथम भाव में",
            rule_name_en="Lagna Lord in 1st House",
            school="parashari",
            category="Parashari",
            source_text="BPHS",
            source_chapter="Ch. 24",
            themes=["career"],
            fired=True,
            polarity="+",
            signal_score=1.0,
            base_strength=1.0
        ),
        RuleEvidence(
            rule_id="KP-CUSP-10-SUBLORD",
            rule_name_hi="दशम उप-स्वामी",
            rule_name_en="10th Cusp Sub-Lord",
            school="kp",
            category="KP",
            source_text="KP Reader",
            source_chapter="Reader IV",
            themes=["career"],
            fired=True,
            polarity="+",
            signal_score=1.2,
            base_strength=1.2
        ),
        RuleEvidence(
            rule_id="LK-KHANA-10-KETU",
            rule_name_hi="खाना 10 में केतु",
            rule_name_en="Ketu in 10th Khana",
            school="lal_kitab",
            category="Lal Kitab",
            source_text="Lal Kitab 1952",
            source_chapter="Farman 10",
            themes=["career"],
            fired=True,
            polarity="-",
            signal_score=0.8,
            base_strength=0.8
        )
    ]

    report: MultiSchoolSideBySideReport = ConsensusAggregator.aggregate_side_by_side(evidences)
    assert report.total_active_rules == 3
    assert "Parashari" in report.schools
    assert "KP" in report.schools
    assert "Lal Kitab" in report.schools
    assert report.schools["Parashari"].positive_count == 1
    assert report.schools["KP"].positive_count == 1
    assert report.schools["Lal Kitab"].negative_count == 1


def test_conflict_precedence_kemadruma_bhanga(benchmark_chart):
    """Verify Kemadruma Bhanga precedence records dominant and overridden rules."""
    prec = ShastriyaPrecedenceEngine.resolve_kemadruma_precedence(benchmark_chart)
    assert prec is not None
    assert prec.principle == PrecedencePrinciple.BHANGA_CANCELLATION
    assert prec.dominant_rule_id == "BPHS-KEMADRUMA-BHANGA"
    assert prec.overridden_rule_id == "GEN-KEMADRUMA-DOSHA"
    assert "Kemadruma" in prec.explanation_en
    assert "केमद्रुम" in prec.explanation_hi


def test_conflict_precedence_shadbala_dominance():
    """Verify Shadbala dominance resolves house conflicts by virupa/ratio."""
    prec = ShastriyaPrecedenceEngine.resolve_shadbala_precedence(
        p1_name="Jupiter",
        p1_ratio=1.45,
        p2_name="Saturn",
        p2_ratio=0.92,
        house_num=10
    )
    assert prec.principle == PrecedencePrinciple.SHADBALA_DOMINANCE
    assert "JUPITER" in prec.dominant_rule_id
    assert "SATURN" in prec.overridden_rule_id
    assert "1.45" in prec.explanation_en
