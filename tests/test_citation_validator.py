"""
Adversarial & Unit Tests for Citation Grounding Validator (Phase 5, Task P5-T6).
Reference: docs/IMPLEMENTATION_PRD.md (Section 5.4, P5-T6).

Verifies:
1. Valid tagged text passes validation, strips tags for display, and extracts provenance.
2. Missing citation tag rejection.
3. Unknown finding ID rejection.
4. Adversarial check: Hallucinated planetary entities rejected.
5. Deterministic fallback rendering works cleanly without raising exceptions.
6. GroundedNarrator executes gracefully even with offline/unconfigured API.
"""

import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from jyotish.evidence.pack import EvidencePack, EvidenceFinding, FindingTiming
from jyotish.narrate.validator import (
    CitationGroundingValidator,
    default_citation_validator,
    ValidationResult
)
from jyotish.narrate.engine import GroundedNarrator


@pytest.fixture
def sample_pack():
    return EvidencePack(
        chart_meta={"engine": "swisseph", "ayanamsa": "lahiri", "house_system": "whole_sign"},
        domain="career",
        school="parashari",
        findings=[
            EvidenceFinding(
                finding_id="F1",
                rule_ids=["BPHS-10-LORD10-H11"],
                title_en="10th Lord Venus in 11th House",
                title_hi="दशमेश शुक्र एकादश भाव में",
                claim_en="10th lord Venus in 11th house signifies substantial career gains.",
                claim_hi="दशमेश शुक्र का एकादश में वास व्यवसाय से प्रचुर लाभ दिलाता है।",
                polarity="+",
                strength=0.88,
                strength_reason=["Exalted Venus", "Ashtakavarga 32 bindus"],
                timing=FindingTiming(dasha_support=["Venus MD: 2026-2046"]),
                caveats=[]
            ),
            EvidenceFinding(
                finding_id="F2",
                rule_ids=["BPHS-JUPITER-10"],
                title_en="Jupiter in 10th House",
                title_hi="दशम में गुरु",
                claim_en="Jupiter occupying the 10th house confers societal prestige and mentoring aptitude.",
                claim_hi="दशम भाव में स्थित गुरु समाज में प्रतिष्ठा और मार्गदर्शक क्षमता प्रदान करते हैं।",
                polarity="+",
                strength=0.82,
                strength_reason=["Digbala Jupiter"],
                timing=FindingTiming(),
                caveats=[]
            )
        ],
        disclaimers=["Traditional guidance, not guarantee."]
    )


def test_valid_generation_passes_and_strips_tags(sample_pack):
    """Verify properly tagged text passes validation and strips [F#] tags for display."""
    valid_text = (
        "Your 10th lord Venus sits in the 11th house, signifying steady professional rewards [F1]. "
        "Furthermore, Jupiter in the 10th house indicates natural leadership and moral authority [F2]."
    )

    result: ValidationResult = default_citation_validator.validate_and_clean(valid_text, sample_pack)

    assert result.is_valid is True
    assert "[F1]" not in result.clean_display_text
    assert "[F2]" not in result.clean_display_text
    assert len(result.provenance) == 2
    assert result.provenance[0].cited_finding_ids == ["F1"]
    assert "BPHS-10-LORD10-H11" in result.provenance[0].rule_ids
    assert result.provenance[1].cited_finding_ids == ["F2"]


def test_adversarial_missing_citation_rejected(sample_pack):
    """Adversarial test: A sentence with no [F#] tag must fail validation."""
    untagged_text = (
        "Your 10th lord Venus brings professional gains [F1]. "
        "You will definitely become a CEO and travel to Mars tomorrow."  # Missing tag!
    )

    result = default_citation_validator.validate_and_clean(untagged_text, sample_pack)

    assert result.is_valid is False
    assert any("has no [F#] citation tag" in err for err in result.errors)


def test_adversarial_unknown_finding_id_rejected(sample_pack):
    """Adversarial test: Text citing a hallucinated ID (e.g. [F99]) must fail validation."""
    fake_id_text = (
        "Your 10th lord Venus is placed favorably [F1]. "
        "A mystical alignment guarantees unexpected wealth [F99]."  # Unknown ID!
    )

    result = default_citation_validator.validate_and_clean(fake_id_text, sample_pack)

    assert result.is_valid is False
    assert any("non-existent finding" in err for err in result.errors)


def test_adversarial_hallucinated_planet_rejected(sample_pack):
    """Adversarial test: Introducing a foreign planet not in the pack fails validation."""
    # Pack only has Venus and Jupiter. Mentioning Saturn should fail!
    hallucinated_planet_text = (
        "Your 10th lord Venus brings steady prosperity [F1]. "
        "Saturn casts a severe malefic gaze obstructing your job [F2]."  # Saturn is NOT in the pack!
    )

    result = default_citation_validator.validate_and_clean(hallucinated_planet_text, sample_pack)

    assert result.is_valid is False
    assert any("Saturn" in err and "ungrounded planet" in err for err in result.errors)


def test_deterministic_fallback_rendering(sample_pack):
    """Verify fallback template rendering outputs 100% grounded claim text."""
    fallback_res = default_citation_validator.fallback_template_render(sample_pack, language="en")

    assert fallback_res.is_valid is True
    assert fallback_res.fallback_used is True
    assert "Venus" in fallback_res.clean_display_text
    assert "Jupiter" in fallback_res.clean_display_text
    assert len(fallback_res.provenance) == len(sample_pack.findings)


def test_grounded_narrator_fallback_execution(sample_pack):
    """Verify GroundedNarrator executes cleanly and falls back when API is unconfigured."""
    narrator = GroundedNarrator(model_name="unconfigured-model")
    response = narrator.narrate(sample_pack, language="en")

    assert response.validation_passed is True
    assert response.fallback_used is True
    assert len(response.display_text) > 50
    assert len(response.provenance) > 0
