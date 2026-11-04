"""
Citation & Grounding Validator for JyotishOS (Phase 5, Task P5-T6).
Reference: docs/IMPLEMENTATION_PRD.md (Section 5.4, P5-T6).

Enforces post-generation grounding verification:
1. Every non-empty sentence must contain a valid [F#] citation tag.
2. All cited IDs (e.g. F1, F2) must exist in the provided EvidencePack.
3. Detects hallucinated planetary entities not present in the cited evidence.
4. Strips tags to produce clean display text for users, while maintaining structured provenance.
5. Provides deterministic template fallback rendering if LLM validation fails after max retries.
"""

import re
from typing import Dict, List, Set, Tuple, Optional, Any
from pydantic import BaseModel, Field
from ..evidence.pack import EvidencePack, EvidenceFinding


PLANET_TOKENS = {
    "sun": "Sun", "surya": "Sun", "सूर्य": "Sun",
    "moon": "Moon", "chandra": "Moon", "चन्द्र": "Moon", "चन्द्रमा": "Moon",
    "mars": "Mars", "mangal": "Mars", "मंगल": "Mars", "kuja": "Mars",
    "mercury": "Mercury", "budha": "Mercury", "बुध": "Mercury",
    "jupiter": "Jupiter", "guru": "Jupiter", "गुरु": "Jupiter", "brihaspati": "Jupiter", "बृहस्पति": "Jupiter",
    "venus": "Venus", "shukra": "Venus", "शुक्र": "Venus",
    "saturn": "Saturn", "shani": "Saturn", "शनि": "Saturn",
    "rahu": "Rahu", "राहु": "Rahu",
    "ketu": "Ketu", "केतु": "Ketu"
}

TAG_REGEX = re.compile(r'\[F(\d+)\]', re.IGNORECASE)


class ProvenanceSentence(BaseModel):
    """A single sentence with its associated finding IDs and underlying rules."""
    sentence_index: int
    text_clean: str
    cited_finding_ids: List[str]
    rule_ids: List[str]


class ValidationResult(BaseModel):
    """Result of validating generated text against an EvidencePack."""
    is_valid: bool
    clean_display_text: str
    provenance: List[ProvenanceSentence] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)
    fallback_used: bool = False


class CitationGroundingValidator:
    """Validates citations, verifies entity containment, and strips tags."""

    @classmethod
    def get_pack_allowed_planets(cls, pack: EvidencePack) -> Set[str]:
        """Collects all planets mentioned in the EvidencePack findings and metadata."""
        allowed: Set[str] = set()
        for f in pack.findings:
            text_blob = (f.title_en + " " + f.title_hi + " " + f.claim_en + " " + f.claim_hi + " " + " ".join(f.strength_reason)).lower()
            for token, p_name in PLANET_TOKENS.items():
                if token in text_blob:
                    allowed.add(p_name)
        return allowed

    @classmethod
    def validate_and_clean(
        cls,
        generated_text: str,
        pack: EvidencePack
    ) -> ValidationResult:
        """
        Validates that generated_text conforms to citation tagging and grounding rules.
        """
        valid_finding_map: Dict[str, EvidenceFinding] = {
            f.finding_id.upper(): f for f in pack.findings
        }
        allowed_planets = cls.get_pack_allowed_planets(pack)

        # Split into sentences by '.', '!', '?', or Hindi Purna Viram '।'
        raw_sentences = re.split(r'(?<=[.!?।])\s+', generated_text.strip())
        sentences = [s.strip() for s in raw_sentences if len(s.strip()) > 3]

        if not sentences:
            return ValidationResult(
                is_valid=False,
                clean_display_text="",
                errors=["Generated response is empty or contains no coherent sentences."]
            )

        provenance_list: List[ProvenanceSentence] = []
        clean_sentences: List[str] = []
        errors: List[str] = []

        for idx, sentence in enumerate(sentences):
            # 1. Check for [F#] tags
            tag_matches = TAG_REGEX.findall(sentence)
            if not tag_matches:
                errors.append(f"Sentence {idx + 1} has no [F#] citation tag: \"{sentence[:60]}...\"")
                continue

            # 2. Check if all tags exist in the EvidencePack
            cited_fids = [f"F{num}".upper() for num in tag_matches]
            sentence_rules: List[str] = []
            sentence_allowed_planets: Set[str] = set()

            unknown_tags = [fid for fid in cited_fids if fid not in valid_finding_map]
            if unknown_tags:
                errors.append(f"Sentence {idx + 1} references non-existent finding(s) {unknown_tags}.")
                continue

            for fid in cited_fids:
                ef = valid_finding_map[fid]
                sentence_rules.extend(ef.rule_ids)
                # Find planets referenced in this specific finding
                f_blob = (ef.title_en + " " + ef.title_hi + " " + ef.claim_en + " " + ef.claim_hi + " " + " ".join(ef.strength_reason)).lower()
                for token, p_name in PLANET_TOKENS.items():
                    if token in f_blob:
                        sentence_allowed_planets.add(p_name)

            # 3. Entity check: Did sentence introduce a planet foreign to the pack?
            words = re.findall(r'[\w\u0900-\u097F]+', sentence.lower())
            for w in words:
                if w in PLANET_TOKENS:
                    detected_p = PLANET_TOKENS[w]
                    if detected_p not in allowed_planets:
                        errors.append(
                            f"Sentence {idx + 1} introduces ungrounded planet '{detected_p}' "
                            f"not present in the Evidence Pack."
                        )

            # 4. Clean sentence by stripping tags
            clean_s = TAG_REGEX.sub('', sentence).strip()
            # Clean up potential double spaces left by tag removal
            clean_s = re.sub(r'\s+', ' ', clean_s)
            clean_sentences.append(clean_s)

            provenance_list.append(ProvenanceSentence(
                sentence_index=idx + 1,
                text_clean=clean_s,
                cited_finding_ids=cited_fids,
                rule_ids=list(set(sentence_rules))
            ))

        if errors:
            return ValidationResult(
                is_valid=False,
                clean_display_text="",
                errors=errors
            )

        clean_text = " ".join(clean_sentences)
        return ValidationResult(
            is_valid=True,
            clean_display_text=clean_text,
            provenance=provenance_list,
            errors=[]
        )

    @classmethod
    def fallback_template_render(
        cls,
        pack: EvidencePack,
        language: str = "en"
    ) -> ValidationResult:
        """
        Deterministic, 100% grounded template rendering.
        Used when LLM generation fails validation after max retries.
        """
        is_hi = language.strip().lower() in ("hi", "hindi")
        paragraphs: List[str] = []
        provenance_list: List[ProvenanceSentence] = []

        header = f"शास्त्रीय फलित सारांश ({pack.domain.capitalize()}):" if is_hi else f"Classical Interpretation Summary ({pack.domain.capitalize()}):"
        paragraphs.append(header)

        for idx, f in enumerate(pack.findings, start=1):
            claim = f.claim_hi if is_hi else f.claim_en
            reasons = f" [कारण: {', '.join(f.strength_reason)}]" if is_hi and f.strength_reason else (f" [Basis: {', '.join(f.strength_reason)}]" if f.strength_reason else "")
            caveat_str = f" (सतर्कता: {', '.join(f.caveats)})" if is_hi and f.caveats else (f" (Caution: {', '.join(f.caveats)})" if f.caveats else "")

            clean_sentence = f"{claim}{reasons}{caveat_str}"
            paragraphs.append(clean_sentence)

            provenance_list.append(ProvenanceSentence(
                sentence_index=idx,
                text_clean=clean_sentence,
                cited_finding_ids=[f.finding_id],
                rule_ids=f.rule_ids
            ))

        display_text = "\n\n".join(paragraphs)
        return ValidationResult(
            is_valid=True,
            clean_display_text=display_text,
            provenance=provenance_list,
            errors=["Fell back to deterministic template rendering due to validation threshold."],
            fallback_used=True
        )


default_citation_validator = CitationGroundingValidator()
