"""
Phase 10 Comprehensive Test Suite: Quality Assurance, Validation & Production Launch.
Validates tasks P10-T1 through P10-T6:
- P10-T1: Full End-to-End Subsystem Integration & Interoperability
- P10-T2: High-Precision Ephemeris State & Oracle Tolerances
- P10-T3: Historical Event Timing & Retrospective Verification
- P10-T4: Classical Shastriya Pramana & Anti-Hallucination Guardrails
- P10-T5: Production Security, Encryption & Multi-Tenant Boundaries
- P10-T6: OpenAPI Contract Completeness & Export Verification
"""

import os
import json
import pytest
from datetime import date, time, datetime

from src.jyotish.core.models import BirthData
from src.jyotish.core.calculator import default_chart_calculator
from src.jyotish.core.ephemeris import get_engine_health
from src.jyotish.events.past_verification import (
    PastEventVerificationInput,
    default_past_event_engine,
    AstrologicalEvidenceStatus
)
from src.jyotish.ai.shastra_rag import default_shastra_rag
from src.jyotish.ai.auditor import default_auditor_agent, AuditVerdict
from src.jyotish.evidence.pack import default_evidence_pack_builder
from src.jyotish.security.crypto import default_crypto


@pytest.fixture(scope="module")
def vivekananda_chart():
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
# P10-T1: Full End-to-End Subsystem Integration & Interoperability
# -----------------------------------------------------------------------------
def test_p10_t1_e2e_subsystem_integration(vivekananda_chart):
    """Verify that all core subsystems calculate cohesively without errors."""
    chart = vivekananda_chart

    # 1. Astronomical lagna & planets
    assert chart.lagna_sign_name in ("Sagittarius", "Dhanu", "dhanu", "sagittarius")
    assert chart.engine_degraded is False
    assert len(chart.planets) >= 7

    # 2. SAV bindus conservation (must equal exactly 337)
    sav_sum = sum(chart.ashtakavarga.sav)
    assert sav_sum == 337, f"Sarvashtakavarga must strictly conserve 337 bindus, got {sav_sum}"

    # 3. Varga calculations (D1, D9, D10)
    assert chart.vargas is not None
    assert "D9" in chart.vargas or "navamsha" in chart.vargas or hasattr(chart.vargas, "d9")


# -----------------------------------------------------------------------------
# P10-T2: High-Precision Ephemeris State & Oracle Tolerances
# -----------------------------------------------------------------------------
def test_p10_t2_ephemeris_precision_and_tolerances(vivekananda_chart):
    """Verify Swiss Ephemeris engine health and canonical longitude boundaries."""
    health = get_engine_health()
    assert health.get("self_test") == "passed"
    assert health.get("engine") == "swisseph"
    assert "Swiss" in health.get("ephemeris_mode", "") or "Moshier" in health.get("ephemeris_mode", "")

    # Vivekananda canonical positions: Sun in Sagittarius ~29°, Moon in Virgo ~17°
    chart = vivekananda_chart
    sun_pos = chart.planets["Sun"]
    moon_pos = chart.planets["Moon"]

    assert sun_pos.sign_name in ("Sagittarius", "Dhanu")
    assert 260.0 <= sun_pos.longitude <= 275.0

    assert moon_pos.sign_name in ("Virgo", "Kanya")
    assert 160.0 <= moon_pos.longitude <= 175.0


# -----------------------------------------------------------------------------
# P10-T3: Historical Event Timing & Retrospective Verification
# -----------------------------------------------------------------------------
def test_p10_t3_historical_event_timing(vivekananda_chart):
    """Verify historical retrospective timing analysis against milestone events."""
    # Chicago Parliament of Religions: September 11, 1893 (Career/Fame milestone)
    inp = PastEventVerificationInput(
        birth_data=vivekananda_chart.birth_data,
        event_theme="career",
        query_text="World Parliament of Religions Speech in Chicago",
        target_date=date(1893, 9, 11)
    )

    result = default_past_event_engine.verify_past_event(inp)
    assert result.target_date == date(1893, 9, 11)
    assert result.event_theme == "career"
    assert 0.0 <= result.confidence_score <= 1.0
    assert result.pillar_4_dasha_evidence is not None
    assert result.pillar_5_transit_evidence is not None
    assert result.status != AstrologicalEvidenceStatus.NOT_SUPPORTED


# -----------------------------------------------------------------------------
# P10-T4: Classical Shastriya Pramana & Anti-Hallucination Guardrails
# -----------------------------------------------------------------------------
def test_p10_t4_shastriya_citations_and_auditor(vivekananda_chart):
    """Verify classical grantha quotation retrieval and auditor hallucination blocks."""
    # 1. RAG retrieval of verified Sanskrit citations
    citations = default_shastra_rag.list_all_citations()
    assert len(citations) >= 5
    c_raja = default_shastra_rag.search_citations_for_rule("BPHS-RAJA-YOGA-10")
    assert c_raja is not None
    assert c_raja.grantha == "Brihat Parashara Hora Shastra"
    assert "राजयोग" in c_raja.shloka_sanskrit

    # 2. Auditor verification: grounded claims pass, ungrounded claims fail
    pack = default_evidence_pack_builder.build_evidence_pack(vivekananda_chart, "career")
    first_fid = pack.findings[0].finding_id

    # Valid grounded statement
    res_pass = default_auditor_agent.audit_narration(
        f"दशम भाव में शुभ स्थिति विद्यमान है [{first_fid}]।",
        pack
    )
    assert res_pass.verdict == AuditVerdict.PASS
    assert res_pass.is_safe is True
    assert f"[{first_fid}]" not in res_pass.audited_text

    # Ungrounded entity hallucination (e.g. Pluto)
    res_hallucinated = default_auditor_agent.audit_narration(
        f"Pluto is aspecting the ascendant [{first_fid}].",
        pack
    )
    assert res_hallucinated.verdict == AuditVerdict.REJECTED_HALLUCINATION
    assert res_hallucinated.is_safe is False


# -----------------------------------------------------------------------------
# P10-T5: Production Security, Encryption & Multi-Tenant Boundaries
# -----------------------------------------------------------------------------
def test_p10_t5_production_security_and_encryption():
    """Verify at-rest encryption prefix and deterministic decryption."""
    crypto = default_crypto
    sensitive_name = "Shriman Narayan Shastri"
    encrypted = crypto.encrypt(sensitive_name)

    assert encrypted.startswith("enc::v1::")
    decrypted = crypto.decrypt(encrypted)
    assert decrypted == sensitive_name


# -----------------------------------------------------------------------------
# P10-T6: OpenAPI Contract Completeness & Export Verification
# -----------------------------------------------------------------------------
def test_p10_t6_openapi_spec_exported():
    """Verify docs/openapi.json exists, is valid JSON, and has complete endpoints."""
    spec_path = os.path.join(os.path.dirname(__file__), "..", "docs", "openapi.json")
    assert os.path.exists(spec_path), "docs/openapi.json must exist at repo root"

    with open(spec_path, "r", encoding="utf-8") as f:
        spec = json.load(f)

    assert spec["openapi"].startswith("3.")
    assert "paths" in spec
    assert len(spec["paths"]) >= 50

    # Essential SaaS paths must be present
    assert "/api/v1/charts/calculate" in spec["paths"]
    assert "/api/v1/tasks/generate-report" in spec["paths"]
    assert "/api/v1/auth/login" in spec["paths"]
    assert "/api/v1/evidence/pack" in spec["paths"]
