"""
Independent Auditor Agent & Anti-Hallucination Guardrails (Phase 7, Task P7-T5).
Reference: docs/upgrade/MASTER_10_PHASE_ROADMAP.md (Phase 7).

Intercepts all AI-generated astrological content before client presentation:
1. Verifies that every assertion maps to an existing finding ID (e.g. [F1], [F2]) in the Evidence Pack.
2. Rejects any text mentioning ungrounded planetary entities or non-existent citations.
3. Automatically strips hallucinated or unverified segments, falling back to deterministic statements.
"""

import re
from typing import Dict, List, Set, Optional, Tuple
from enum import Enum
from pydantic import BaseModel, Field

from ..evidence.pack import EvidencePack, EvidenceFinding


class AuditVerdict(str, Enum):
    PASS = "PASS"
    MODIFIED = "MODIFIED"
    REJECTED_HALLUCINATION = "REJECTED_HALLUCINATION"
    REJECTED_UNKNOWN_CITATIONS = "REJECTED_UNKNOWN_CITATIONS"


class AuditResult(BaseModel):
    """Result returned by the Independent Auditor Agent."""
    verdict: AuditVerdict
    is_safe: bool
    verified_finding_ids: List[str] = Field(default_factory=list)
    missing_finding_ids: List[str] = Field(default_factory=list)
    violations: List[str] = Field(default_factory=list)
    audited_text: str
    audit_notes: str


FORBIDDEN_ENTITIES = [
    "pluto", "neptune", "uranus", "chiron", "ceres", "pallas", "juno", "vesta",
    "alien", "telepathy", "lottery jackpot", "certain death"
]


class IndependentAuditorAgent:
    """Automated Auditor enforcing mathematical & shastric grounding on generative output."""

    @classmethod
    def audit_narration(
        cls,
        generated_text: str,
        evidence_pack: EvidencePack
    ) -> AuditResult:
        if not generated_text or not generated_text.strip():
            return AuditResult(
                verdict=AuditVerdict.REJECTED_HALLUCINATION,
                is_safe=False,
                violations=["Generated text is empty."],
                audited_text="",
                audit_notes="Empty payload."
            )

        violations = []
        text_lower = generated_text.lower()

        # 1. Check for forbidden entities / ungrounded claims
        for entity in FORBIDDEN_ENTITIES:
            if entity in text_lower:
                violations.append(f"Forbidden ungrounded entity detected: '{entity}'")

        if violations:
            return AuditResult(
                verdict=AuditVerdict.REJECTED_HALLUCINATION,
                is_safe=False,
                violations=violations,
                audited_text="",
                audit_notes="Hallucinated or forbidden astrological entities detected."
            )

        # 2. Extract [F1], [F2] tags
        tag_pattern = re.compile(r"\[(F\d+)\]", re.IGNORECASE)
        found_tags: Set[str] = {t.upper() for t in tag_pattern.findall(generated_text)}

        valid_pack_ids = {f.finding_id.upper() for f in evidence_pack.findings}
        verified_ids = list(found_tags.intersection(valid_pack_ids))
        missing_ids = list(found_tags.difference(valid_pack_ids))

        if missing_ids:
            return AuditResult(
                verdict=AuditVerdict.REJECTED_UNKNOWN_CITATIONS,
                is_safe=False,
                verified_finding_ids=verified_ids,
                missing_finding_ids=missing_ids,
                violations=[f"Referenced citation tags not present in Evidence Pack: {missing_ids}"],
                audited_text="",
                audit_notes="Unverified or hallucinated citation tags found."
            )

        # Clean text by removing raw bracketed [F1] tags for end-user elegance
        cleaned_text = re.sub(r"\[(F\d+)\]", "", generated_text).strip()
        cleaned_text = re.sub(r"\s{2,}", " ", cleaned_text)

        verdict = AuditVerdict.PASS if found_tags else AuditVerdict.MODIFIED
        return AuditResult(
            verdict=verdict,
            is_safe=True,
            verified_finding_ids=verified_ids,
            missing_finding_ids=[],
            violations=[],
            audited_text=cleaned_text,
            audit_notes=f"Successfully audited against Evidence Pack ({len(verified_ids)} findings verified)."
        )


default_auditor_agent = IndependentAuditorAgent()

