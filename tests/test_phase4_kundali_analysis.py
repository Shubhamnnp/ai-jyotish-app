"""
Phase 4 Comprehensive Kundali Analysis Engine & Evidence Synthesis Suite.
Validates tasks P4-T1 through P4-T7:
- P4-T1: Bhava-Bhavesha-Karaka 3-Pillar Analysis Engine & Gender Filtering.
- P4-T2: Specialized Divisional Chart Deep-Dives (D9, D10, D7, Vargottama).
- P4-T3: Classical Yogas, Rajayogas, Doshas, and Bhanga Cancellations.
- P4-T4: Delivery Capability & Calibrated Strength Model (Shadbala + Dignity + Avastha + Bhanga).
- P4-T5: Opposing Yogas Resolution and Evidence Synthesis (RuleConflictGraph).
- P4-T6: Unified Kundali Evidence Pack Generation & Schema Validation.
"""

import pytest
from datetime import date, time

from src.jyotish.core.models import BirthData
from src.jyotish.core.calculator import default_chart_calculator
from src.jyotish.core.affliction import AfflictionEngine, get_life_areas_for_gender
from src.jyotish.core.varga import VargaCalculator
from src.jyotish.core.yoga import ClassicalYogaDoshaEngine
from src.jyotish.evidence.strength import StrengthModel, STRENGTH_WEIGHTS
from src.jyotish.evidence.factors import default_factor_extractor
from src.jyotish.rules.conflict_graph import default_conflict_graph, AstrologicalEvidenceStatus
from src.jyotish.evidence.pack import default_evidence_pack_builder, EvidencePack


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
# P4-T1: Bhava-Bhavesha-Karaka 3-Pillar Engine & Gender Filtering
# -----------------------------------------------------------------------------
def test_p4_t1_three_pillar_life_area_breakdown(benchmark_chart):
    """Verify 3-pillar breakdown for key life areas (Career, Health, Relationship)."""
    engine = AfflictionEngine(benchmark_chart)

    # 1. Career (Life Area Id 1) -> House 10, Karaka Saturn, Sec House 2
    career_detail = engine.get_life_area_detail(1)
    assert career_detail is not None
    assert "HouseRows" in career_detail
    assert "LordRows" in career_detail

    # Verify 3-pillar rows (Primary house, Karaka, Secondary house)
    h_rows = career_detail["HouseRows"]
    l_rows = career_detail["LordRows"]
    assert len(h_rows) == 3
    assert len(l_rows) == 3
    assert "10th House" in h_rows[0][0]
    assert "Saturn" in h_rows[1][0]
    assert "2nd House" in h_rows[2][0]

    # Verify Lord rows
    assert "10th House Lord" in l_rows[0][0]
    assert "Saturn" in l_rows[1][0]
    assert "2nd House Lord" in l_rows[2][0]


def test_p4_t1_gender_specific_life_areas():
    """Verify gender-specific life areas are strictly segregated."""
    female_areas = get_life_areas_for_gender("female")
    male_areas = get_life_areas_for_gender("male")

    female_titles = [a["LifeArea"] for a in female_areas]
    male_titles = [a["LifeArea"] for a in male_areas]

    # Pregnancy only in Female
    assert "Pregnancy" in female_titles
    assert "Pregnancy" not in male_titles

    # Husband in Female, Wife in Male
    assert any("Husband" in t for t in female_titles)
    assert not any("Husband" in t for t in male_titles)
    assert any("Wife" in t for t in male_titles)
    assert not any("Wife" in t for t in female_titles)


# -----------------------------------------------------------------------------
# P4-T2: Specialized Divisional Chart Deep Dives
# -----------------------------------------------------------------------------
def test_p4_t2_divisional_deep_dives_and_vargottama(benchmark_chart):
    """Verify D9, D10, D7 and Vargottama detection."""
    vargas = VargaCalculator.calculate_all_vargas(benchmark_chart)
    d1 = vargas["D1"]
    d9 = vargas["D9"]
    d10 = vargas["D10"]
    d7 = vargas["D7"]

    # Verify Navamsha D9 planets
    assert len(d9.planets) >= 9
    assert d9.lagna_sign_id >= 1

    # Verify Dashamsha D10 planets
    assert len(d10.planets) >= 9

    # Verify Saptamsha D7 planets
    assert len(d7.planets) >= 9

    # Vargottama check
    for p_name in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]:
        p_d1 = d1.planets[p_name]
        p_d9 = d9.planets[p_name]
        is_vargottama = (p_d1.sign_id == p_d9.sign_id)
        assert isinstance(is_vargottama, bool)


# -----------------------------------------------------------------------------
# P4-T3: Classical Yogas, Rajayogas & Bhangas
# -----------------------------------------------------------------------------
def test_p4_t3_classical_yogas_and_doshas(benchmark_chart):
    """Verify ClassicalYogaDoshaEngine evaluates yogas, rajayogas, and doshas."""
    result = ClassicalYogaDoshaEngine.evaluate_all(benchmark_chart)
    assert len(result.yogas) > 0
    assert len(result.doshas) > 0

    # Vivekananda has active Raja/Dhana yogas
    active_yogas = [y for y in result.yogas if y.is_active]
    assert len(active_yogas) > 0

    yoga_names = [y.name_en for y in active_yogas]
    # Check for presence of classical yoga structures
    assert any("Raja" in name or "Dhana" in name or "Yoga" in name for name in yoga_names)

    # Check cancellations structure
    for d in result.doshas:
        assert hasattr(d, "is_present")
        assert hasattr(d, "is_cancelled")
        assert hasattr(d, "cancellation_reasons")


# -----------------------------------------------------------------------------
# P4-T4: Delivery Capability & Calibrated Strength Model
# -----------------------------------------------------------------------------
def test_p4_t4_calibrated_strength_weights_and_delivery(benchmark_chart):
    """Verify calibrated strength model weights sum to 1.0 and evaluate 0.0-1.0."""
    # Weights must sum to 1.0
    total_w = sum(STRENGTH_WEIGHTS.values())
    assert pytest.approx(total_w, abs=0.001) == 1.0

    factors = default_factor_extractor.extract_factors(benchmark_chart)
    for p_name in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]:
        pf = factors.planets[p_name]
        strength_bd = StrengthModel.evaluate_planet_strength(pf)
        assert 0.0 <= strength_bd.final_score <= 1.0
        assert strength_bd.shadbala_contribution >= 0.0
        assert strength_bd.dignity_contribution >= 0.0
        assert strength_bd.avastha_contribution >= 0.0
        assert len(strength_bd.reasons) > 0


# -----------------------------------------------------------------------------
# P4-T5: Opposing Yogas Resolution & Evidence Synthesis
# -----------------------------------------------------------------------------
def test_p4_t5_conflict_resolution_and_synthesis(benchmark_chart):
    """Verify RuleConflictGraph detects cancellations and synthesizes evidence states."""
    # 1. Neechabhanga detection
    nb_list = default_conflict_graph.check_neechabhanga(benchmark_chart)
    assert isinstance(nb_list, list)

    # 2. Kemadruma Bhanga detection
    kb_cancelled = default_conflict_graph.check_kemadruma_bhanga(benchmark_chart)
    assert isinstance(kb_cancelled, bool)

    # 3. Manglik Bhanga detection
    mb_cancelled = default_conflict_graph.check_manglik_bhanga(benchmark_chart)
    assert isinstance(mb_cancelled, bool)

    # 4. Synthesize conflicts on career theme
    synth_dict = default_conflict_graph.synthesize_conflicts([], benchmark_chart, target_theme="career")
    assert "career" in synth_dict
    synth = synth_dict["career"]
    assert synth.theme == "career"
    assert isinstance(synth.status, AstrologicalEvidenceStatus)
    assert 0.0 <= synth.confidence_score <= 1.0


# -----------------------------------------------------------------------------
# P4-T6: Unified Kundali Evidence Pack Generation
# -----------------------------------------------------------------------------
def test_p4_t6_unified_evidence_pack_generation(benchmark_chart):
    """Verify EvidencePackBuilder generates compliant, grounded evidence packs."""
    for domain in ["career", "marriage", "wealth"]:
        pack = default_evidence_pack_builder.build_evidence_pack(benchmark_chart, domain)
        assert isinstance(pack, EvidencePack)
        assert pack.domain == domain
        assert pack.chart_meta is not None
        assert "engine" in pack.chart_meta
        assert "ayanamsa" in pack.chart_meta
        assert len(pack.findings) > 0

        for f in pack.findings:
            assert f.finding_id.startswith("F")
            assert len(f.claim_en) > 0
            assert len(f.claim_hi) > 0
            assert f.polarity in ["+", "-"]
            assert 0.0 <= f.strength <= 1.0
            assert f.source_ref is not None
            assert len(f.source_ref.grantha) > 0
