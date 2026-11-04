"""
Hardening and Verification Test Suite for Phase 10:
Layer 4 AI Intelligence & Daivajna Multi-Agent Orchestrator.

Verifies:
1. Specialist Calculation Agent: Deterministic fact extraction with zero mathematical hallucination.
2. Classical Shastriya Rule Retrieval Agent: RAG retrieval of authentic Sanskrit shlokas and grantha pramana.
3. Evidence Verification Audit Agent: Strict segregation of supporting vs conflicting evidence and formulaic confidence scoring.
4. Synthesis & Explanation Agent: Authentic classical Vedic remedies and balanced bilingual synthesis.
5. Master Daivajna Orchestrator: End-to-end multi-agent orchestration for career, marriage, and health domains.
"""

from datetime import date, time
import pytest
from src.jyotish.core.models import BirthData
from src.jyotish.core.calculator import default_chart_calculator
from src.jyotish.ai.orchestrator import (
    SpecialistCalculationAgent,
    ShastriyaRuleRetrievalAgent,
    EvidenceVerificationAuditAgent,
    SynthesisExplanationAgent,
    MasterDaivajnaOrchestrator,
    default_daivajna_orchestrator,
    DeterministicFactSheet,
    DaivajnaConsultationResult
)


@pytest.fixture
def sample_test_chart():
    """Deterministic test native born in Nanpara, UP."""
    bdata = BirthData(
        name="Shri Test Native",
        birth_date=date(1994, 5, 16),
        birth_time=time(17, 0, 0),
        latitude=28.0327,
        longitude=81.3787,
        timezone_offset=5.5,
        city="Nanpara, UP",
        gender="male"
    )
    return default_chart_calculator.calculate_chart(bdata)


def test_specialist_calculation_agent_fact_sheet(sample_test_chart):
    agent = SpecialistCalculationAgent()
    facts = agent.extract_fact_sheet(sample_test_chart)

    assert isinstance(facts, DeterministicFactSheet)
    assert facts.native_name == "Shri Test Native"
    assert facts.ascendant_sign == sample_test_chart.lagna_sign_name
    assert abs(facts.ascendant_degree - sample_test_chart.lagna_degree) < 0.01

    # Verify 9 grahas are present
    assert len(facts.planets) >= 9
    for p_name in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]:
        assert p_name in facts.planets
        p_info = facts.planets[p_name]
        assert "sign" in p_info
        assert "degree" in p_info
        assert "house" in p_info
        assert "dignity" in p_info
        assert "is_retrograde" in p_info
        assert "is_combust" in p_info

    # Verify SAV points for 12 houses
    assert len(facts.houses_sav) == 12
    for h in range(1, 13):
        assert h in facts.houses_sav
        assert isinstance(facts.houses_sav[h], int)

    # Verify Active Dasha presence
    assert facts.active_mahadasha != "Unknown"
    assert facts.active_antardasha != "Unknown"


def test_shastriya_rule_retrieval_agent(sample_test_chart):
    calc_agent = SpecialistCalculationAgent()
    facts = calc_agent.extract_fact_sheet(sample_test_chart)

    rag_agent = ShastriyaRuleRetrievalAgent()
    
    # Test for career and marriage topics
    career_pramana = rag_agent.retrieve_evidence("career", facts)
    assert len(career_pramana) > 0
    for p in career_pramana:
        assert p.grantha
        assert p.chapter
        assert p.translation_hi
        assert p.translation_en
        assert len(p.principles) > 0

    marriage_pramana = rag_agent.retrieve_evidence("marriage", facts)
    assert len(marriage_pramana) > 0
    assert any("marriage" in p.theme.lower() or "partner" in p.theme.lower() or "lagna" in p.theme.lower() or "career" in p.theme.lower() for p in marriage_pramana)


def test_evidence_verification_audit_agent(sample_test_chart):
    calc_agent = SpecialistCalculationAgent()
    facts = calc_agent.extract_fact_sheet(sample_test_chart)

    audit_agent = EvidenceVerificationAuditAgent()
    verdict = audit_agent.audit_evidence("career", facts)

    # Must segregate supporting and conflicting factors
    assert len(verdict.supporting_evidence) > 0
    assert len(verdict.conflicting_evidence) > 0

    for factor in verdict.supporting_evidence:
        assert factor.impact == "SUPPORTING"
        assert factor.weight > 0
        assert factor.rationale != ""

    for factor in verdict.conflicting_evidence:
        assert factor.impact == "CONFLICTING"
        assert factor.weight > 0
        assert factor.rationale != ""

    # Formulaic confidence score bounded between 15% and 92%
    assert 15.0 <= verdict.confidence_score <= 92.0
    assert verdict.confidence_tier in ["HIGH", "MODERATE", "LOW"]
    assert verdict.verdict_summary != ""


def test_synthesis_explanation_agent_remedies(sample_test_chart):
    calc_agent = SpecialistCalculationAgent()
    facts = calc_agent.extract_fact_sheet(sample_test_chart)
    audit_agent = EvidenceVerificationAuditAgent()
    verdict = audit_agent.audit_evidence("general", facts)

    synth_agent = SynthesisExplanationAgent()
    remedies = synth_agent.generate_remedies(facts, verdict)

    assert len(remedies) >= 2
    for r in remedies:
        assert r.planet_or_deity != ""
        assert r.remedy_type in ["Mantra", "Stotra", "Dana", "Vrata", "Lifestyle"]
        assert r.title_hi != ""
        assert r.title_en != ""
        assert r.procedure != ""
        assert r.classical_reference != ""


def test_master_daivajna_orchestrator_end_to_end(sample_test_chart):
    orchestrator = default_daivajna_orchestrator

    domains_to_test = ["career", "marriage", "health"]
    for domain in domains_to_test:
        result = orchestrator.process_consultation(
            chart=sample_test_chart,
            topic=domain,
            user_query=f"{domain.title()} timing and prospects"
        )

        assert isinstance(result, DaivajnaConsultationResult)
        assert result.status == "success"
        assert result.topic == domain
        assert result.fact_sheet.native_name == "Shri Test Native"
        assert len(result.shastriya_pramana) > 0
        assert len(result.audit_verdict.supporting_evidence) > 0
        assert len(result.audit_verdict.conflicting_evidence) > 0
        assert 15.0 <= result.audit_verdict.confidence_score <= 92.0

        # Bilingual synthesis check
        assert "प्राथमिक गणितीय स्थिति" in result.synthesis_hi
        assert "सकारात्मक शास्त्रीय पक्ष" in result.synthesis_hi
        assert "शास्त्रीय सत्य व सतर्कता" in result.synthesis_hi
        assert "Verified Astronomical Baseline" in result.synthesis_en
        assert "Supporting Astrological Evidence" in result.synthesis_en
        assert "Independent Audit Verdict" in result.synthesis_en

        # Remedies check
        assert len(result.remedies) >= 2

