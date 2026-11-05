"""
Phase 7 Comprehensive Test Suite: Multi-Agent AI & Daivajna Brain.
Validates tasks P7-T1 through P7-T5:
- P7-T1: Canonical 14 Specialist AI Agent Personas & Protocols
- P7-T2: Multi-Agent Structured Evidence Pack Communication Protocol
- P7-T3: Shastra Citation & Sanskrit Shloka RAG Retrieval
- P7-T4: Multi-Lingual Style Synthesis Engine (Hindi, English, Hinglish)
- P7-T5: Independent Auditor Agent & Anti-Hallucination Guardrails
"""

import pytest
from datetime import date, time

from src.jyotish.core.models import BirthData
from src.jyotish.core.calculator import default_chart_calculator
from src.jyotish.evidence.pack import default_evidence_pack_builder, EvidenceFinding
from src.jyotish.ai.agents.registry import (
    default_agent_registry,
    AgentDomain,
    SpecialistAgentDefinition,
    CANONICAL_14_AGENTS
)
from src.jyotish.ai.protocol import (
    AgentMessage,
    default_protocol_validator
)
from src.jyotish.ai.shastra_rag import (
    default_shastra_rag,
    ShastraCitation
)
from src.jyotish.ai.style import (
    default_style_formatter,
    LanguageStyle
)
from src.jyotish.ai.auditor import (
    default_auditor_agent,
    AuditVerdict,
    AuditResult
)


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
# P7-T1: 14 Specialist AI Agent Personas & Protocols
# -----------------------------------------------------------------------------
def test_p7_t1_canonical_14_agents():
    """Verify all 14 canonical specialist agents exist with authorized domains."""
    agents = default_agent_registry.list_all_agents()
    assert len(agents) == 14

    required_agent_ids = [
        "master_jyotish_agent",
        "parashari_agent",
        "jaimini_agent",
        "kp_agent",
        "prashna_agent",
        "dasha_agent",
        "transit_agent",
        "varga_agent",
        "yoga_agent",
        "dosha_agent",
        "btr_agent",
        "event_prediction_agent",
        "shastra_research_agent",
        "independent_auditor_agent"
    ]

    for aid in required_agent_ids:
        agent = default_agent_registry.get_agent(aid)
        assert agent is not None
        assert agent.agent_id == aid
        assert len(agent.name_en) > 0
        assert len(agent.name_hi) > 0
        assert len(agent.authorized_sources) > 0


# -----------------------------------------------------------------------------
# P7-T2: Multi-Agent Structured Evidence Pack Communication Protocol
# -----------------------------------------------------------------------------
def test_p7_t2_agent_protocol_validation(benchmark_chart):
    """Verify intra-agent messages adhere strictly to Evidence Pack serialization."""
    pack = default_evidence_pack_builder.build_evidence_pack(benchmark_chart, "career")
    assert len(pack.findings) > 0

    # Valid message creation
    msg = default_protocol_validator.create_response(
        sender_id="parashari_agent",
        recipient_id="master_jyotish_agent",
        domain="career",
        findings=pack.findings[:2],
        confidence=0.85,
        metadata={"chart_id": "Vivekananda"}
    )
    assert isinstance(msg, AgentMessage)
    assert msg.sender_agent_id == "parashari_agent"
    assert msg.recipient_agent_id == "master_jyotish_agent"
    assert len(msg.evidence_findings) == 2
    assert default_protocol_validator.validate_message(msg) is True

    # Adversarial validation: invalid confidence score
    with pytest.raises(ValueError):
        invalid_msg = AgentMessage(
            sender_agent_id="test",
            recipient_agent_id="master",
            domain="career",
            confidence_score=1.5  # Out of bounds
        )
        default_protocol_validator.validate_message(invalid_msg)


# -----------------------------------------------------------------------------
# P7-T3: Shastra Citation & Sanskrit Retrieval (RAG)
# -----------------------------------------------------------------------------
def test_p7_t3_shastra_rag_retrieval():
    """Verify authentic Sanskrit shlokas and classical grantha coordinates retrieval."""
    citations = default_shastra_rag.list_all_citations()
    assert len(citations) >= 5

    # 1. Rajayoga retrieval
    c_raja = default_shastra_rag.search_citations_for_rule("BPHS-RAJA-YOGA-10")
    assert c_raja is not None
    assert c_raja.grantha == "Brihat Parashara Hora Shastra"
    assert "राजयोग" in c_raja.shloka_sanskrit

    # 2. Gajakesari retrieval
    c_gaja = default_shastra_rag.search_citations_for_rule("GAJAKESARI")
    assert c_gaja is not None
    assert "गजाकेशरी" in c_gaja.shloka_sanskrit

    # 3. Neechabhanga retrieval
    c_neecha = default_shastra_rag.search_citations_for_rule("NEECHABHANGA")
    assert c_neecha is not None
    assert c_neecha.grantha == "Phaladeepika"
    assert "नीचस्थितो" in c_neecha.shloka_sanskrit


# -----------------------------------------------------------------------------
# P7-T4: Multi-Lingual Style Synthesis Engine
# -----------------------------------------------------------------------------
def test_p7_t4_multilingual_style_formatting():
    """Verify dignified, respectful phrasing across Hindi, English, and Hinglish."""
    # 1. Pure Hindi
    hi_verdict = default_style_formatter.format_verdict("करियर", 0.85, LanguageStyle.PURE_HINDI)
    assert "शास्त्र-सम्मत प्रबल अनुकूलता" in hi_verdict
    assert "85%" in hi_verdict

    # 2. Scholarly English
    en_verdict = default_style_formatter.format_verdict("career", 0.85, LanguageStyle.SCHOLARLY_ENGLISH)
    assert "strongly supported favorable alignment" in en_verdict

    # 3. Hinglish
    hing_verdict = default_style_formatter.format_verdict("career", 0.85, LanguageStyle.HINGLISH)
    assert "strong favorable yog" in hing_verdict

    # 4. Footnote attachment
    cited_text = default_style_formatter.attach_citations("फलादेश विवरण।", ["BPHS Ch. 35", "Phaladeepika Ch. 6"])
    assert "[BPHS Ch. 35]" in cited_text
    assert "[Phaladeepika Ch. 6]" in cited_text


# -----------------------------------------------------------------------------
# P7-T5: Independent Auditor Agent & Anti-Hallucination Guardrails
# -----------------------------------------------------------------------------
def test_p7_t5_independent_auditor_guardrails(benchmark_chart):
    """Verify Independent Auditor blocks hallucinations and unverified claims."""
    pack = default_evidence_pack_builder.build_evidence_pack(benchmark_chart, "career")
    first_fid = pack.findings[0].finding_id

    # 1. Valid grounded text -> PASS
    valid_text = f"दशम भाव में शुभ स्थिति विद्यमान है [{first_fid}]।"
    res_pass = default_auditor_agent.audit_narration(valid_text, pack)
    assert res_pass.verdict == AuditVerdict.PASS
    assert res_pass.is_safe is True
    assert first_fid in res_pass.verified_finding_ids
    assert f"[{first_fid}]" not in res_pass.audited_text  # Cleaned of raw tags

    # 2. Unknown finding tag -> REJECTED_UNKNOWN_CITATIONS
    hallucinated_tag_text = "अप्रत्याशित धन लाभ होगा [F9999]."
    res_bad_tag = default_auditor_agent.audit_narration(hallucinated_tag_text, pack)
    assert res_bad_tag.verdict == AuditVerdict.REJECTED_UNKNOWN_CITATIONS
    assert res_bad_tag.is_safe is False
    assert "F9999" in res_bad_tag.missing_finding_ids

    # 3. Forbidden entity -> REJECTED_HALLUCINATION
    forbidden_text = f"Pluto transit will cause major shifts [{first_fid}]."
    res_forbidden = default_auditor_agent.audit_narration(forbidden_text, pack)
    assert res_forbidden.verdict == AuditVerdict.REJECTED_HALLUCINATION
    assert res_forbidden.is_safe is False
    assert any("pluto" in v.lower() for v in res_forbidden.violations)

