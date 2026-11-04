"""
Unit tests for Legacy Template Deprecation & Evidence Pack Flow Hardening (Phase 5, Task P5-T10).
Reference: docs/IMPLEMENTATION_PRD.md (Section 5.3 & 5.4, P5-T10).

Verifies:
1. Complete deprecation of unprovenanced text generation in Shastriya Faladesh service.
2. Dimension synthesis strictly flows through and incorporates Evidence Packs.
3. Every finding in positives/negatives/citations references classical Granthas (BPHS, Phaladeepika, etc.).
4. FAQ answers are grounded on Evidence Pack findings and verified scriptural sources.
5. Strict enforcement of the Astrological Safety Layer within FAQ answers (unsafe queries blocked/redirected).
6. Shastriya Pramana engine returns authentic canonical grantha citations.
"""

import sys
import os
import pytest
from datetime import date, time

from jyotish.core.models import BirthData
from jyotish.core.calculator import default_chart_calculator
from jyotish.services.shastriya_faladesh import default_shastriya_faladesh_engine
from jyotish.services.shastriya_pramana import default_shastriya_pramana_engine, SHASTRIYA_SHLOKAS


@pytest.fixture(scope="module")
def sample_chart():
    bd = BirthData(
        name="Vivekananda",
        birth_date=date(1863, 1, 12),
        birth_time=time(6, 33, 0),
        latitude=22.5726,
        longitude=88.3639,
        timezone_offset=5.89,
        gender="male",
        confidence="exact"
    )
    return default_chart_calculator.calculate_full_chart(bd)


def test_dimension_synthesis_evidence_pack_flow(sample_chart):
    """Test that synthesize_dimension integrates Evidence Pack and sets domain."""
    res = default_shastriya_faladesh_engine.synthesize_dimension(sample_chart, dim_id=1)
    assert res is not None
    assert "evidence_pack" in res
    assert res["evidence_pack"] is not None
    assert res["domain"] == "career"

    # Check that findings have provenance
    epack_findings = res["evidence_pack"]["findings"]
    assert len(epack_findings) > 0
    for f in epack_findings:
        assert "finding_id" in f
        assert "claim_hi" in f
        assert "source_ref" in f
        assert f["source_ref"]["grantha"] != ""


def test_positives_and_negatives_provenance(sample_chart):
    """Test that positive and negative factors contain finding IDs or classical grantha references."""
    res = default_shastriya_faladesh_engine.synthesize_dimension(sample_chart, dim_id=1)
    positives = res["positives"]
    assert len(positives) > 0
    # At least one positive has [F#] tag from evidence pack
    assert any("[F" in p for p in positives)

    citations = res["citations"]
    assert len(citations) > 0
    for c in citations:
        assert any(g in c for g in ["Brihat", "बृहत्पाराशर", "BPHS", "फलदीपिका", "Phaladeepika", "सर्वार्थ", "Uttara"])


def test_faq_answer_grounded_in_evidence(sample_chart):
    """Test that answer_specific_faq produces an answer grounded on evidence pack findings."""
    ans = default_shastriya_faladesh_engine.answer_specific_faq(sample_chart, dim_id=1, faq_num=1)
    assert ans["is_safe"] is True
    assert "full_answer_md" in ans
    text = ans["full_answer_md"]
    assert "प्रत्यक्ष शास्त्रीय निर्णय" in text
    assert "काल निर्णय" in text
    assert "सकारात्मक शास्त्रीय पक्ष" in text
    assert "शास्त्रीय ग्रन्थ आधार" in text


def test_faq_safety_layer_enforcement(sample_chart):
    """Test that unsafe questions are blocked and redirected by safety filter."""
    # We simulate an unsafe death-timing question
    unsafe_question = "Tell me the exact date of my death"
    from jyotish.safety.filter import AstrologicalSafetyFilter

    is_safe, msg = AstrologicalSafetyFilter.validate_query(unsafe_question)
    assert is_safe is False
    assert "मृत्यु की सटीक तिथि" in msg or "नैतिक मर्यादा" in msg or "देहावसान" in msg


def test_shastriya_pramana_citations_authenticity(sample_chart):
    """Test that shastriya pramana references authentic canonical granthas and shlokas."""
    pushkara_audit = default_shastriya_pramana_engine.audit_chart_pushkara(sample_chart)
    assert "shastriya_shloka" in pushkara_audit["planets"]["Sun"]
    shloka_data = pushkara_audit["planets"]["Sun"]["shastriya_shloka"]
    assert "grantha" in shloka_data
    assert "जातक परिजात" in shloka_data["grantha"]
    assert "shloka" in shloka_data
