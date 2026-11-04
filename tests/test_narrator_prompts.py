"""
Prompt Snapshot & Grounding Prompt Tests (Phase 5, Task P5-T5).
Reference: docs/IMPLEMENTATION_PRD.md (Section 5.4, P5-T5).

Verifies:
1. Prompt builder receives only EvidencePack.
2. Embeds mandatory citation rules ([F#] per sentence).
3. Probabilistic language mandate.
4. Bilingual prompt support (English and Hindi).
"""

import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from jyotish.evidence.pack import EvidencePack, EvidenceFinding, FindingTiming
from jyotish.narrate.prompt import build_narrator_prompt


@pytest.fixture
def mock_evidence_pack():
    return EvidencePack(
        chart_meta={"engine": "swisseph", "ayanamsa": "lahiri", "house_system": "whole_sign"},
        domain="career",
        school="parashari",
        findings=[
            EvidenceFinding(
                finding_id="F1",
                rule_ids=["BPHS-10-LORD10-H11"],
                title_en="10th Lord in 11th House",
                title_hi="दशमेश एकादश भाव में",
                claim_en="10th lord Venus in 11th house confers professional financial gains.",
                claim_hi="दशम भाव के स्वामी शुक्र एकादश भाव में स्थित होकर व्यवसाय से प्रचुर लाभ कराते हैं।",
                polarity="+",
                strength=0.85,
                strength_reason=["Exalted dignity", "High SAV bindus"],
                timing=FindingTiming(dasha_support=["Venus MD 2024-2044"]),
                caveats=[]
            )
        ],
        disclaimers=["Traditional guidance, not guarantee."]
    )


def test_prompt_snapshot_english(mock_evidence_pack):
    """Verify English prompt contains grounding mandates and Evidence Pack JSON."""
    bundle = build_narrator_prompt(mock_evidence_pack, language="en", user_query="What about my career?")

    sys_instr = bundle["system_instruction"]
    user_p = bundle["user_prompt"]

    assert "CITATION TAGGING" in sys_instr
    assert "[F#]" in sys_instr
    assert "ZERO HALLUCINATIONS" in sys_instr
    assert "PROBABILISTIC LANGUAGE" in sys_instr

    assert "BPHS-10-LORD10-H11" in user_p
    assert "Venus in 11th house" in user_p
    assert "What about my career?" in user_p


def test_prompt_snapshot_hindi(mock_evidence_pack):
    """Verify Hindi prompt contains Devanagari instructions."""
    bundle = build_narrator_prompt(mock_evidence_pack, language="hi")

    sys_instr = bundle["system_instruction"]
    user_p = bundle["user_prompt"]

    assert "अनिवार्य सूत्र अंकन (Citation)" in sys_instr
    assert "[F#]" in sys_instr
    assert "शून्य कपोल-कल्पना" in sys_instr
    assert "Hindi (Devanagari)" in user_p
