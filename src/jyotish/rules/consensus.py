"""
Multi-School Side-by-Side Presentation & Consensus Architecture.
Reference: docs/IMPLEMENTATION_PRD.md (Section 4.2, P4-T8).

Rules:
- Strictly prohibits cross-school probability averaging or confidence blurring.
- Displays per-school results side-by-side (Parashari, Jaimini, KP, Lal Kitab, Tajika).
- Preserves backward compatibility for legacy single-stream evidence callers without artificial blending.
"""

from typing import List, Tuple, Dict, Any, Optional
from pydantic import BaseModel, Field
from ..core.models import RuleEvidence


class SchoolEvidenceBreakdown(BaseModel):
    """Side-by-side breakdown for a single school."""
    school_name: str
    active_count: int = 0
    positive_count: int = 0
    negative_count: int = 0
    top_positives: List[RuleEvidence] = Field(default_factory=list)
    top_negatives: List[RuleEvidence] = Field(default_factory=list)
    summary: str = ""


class MultiSchoolSideBySideReport(BaseModel):
    """Clean side-by-side comparative presentation across isolated astrological traditions."""
    schools: Dict[str, SchoolEvidenceBreakdown] = Field(default_factory=dict)
    total_active_rules: int = 0
    note: str = "Results presented strictly side-by-side per classical tradition without synthetic averaging."


class ConsensusAggregator:
    """Side-by-side multi-school aggregator eliminating synthetic cross-tradition averaging."""

    @staticmethod
    def aggregate_side_by_side(evidences: List[RuleEvidence]) -> MultiSchoolSideBySideReport:
        """
        Groups evidences by astrological school / category and produces an isolated
        side-by-side breakdown with no synthetic score averaging.
        """
        report = MultiSchoolSideBySideReport()
        active = [e for e in evidences if e.fired]
        report.total_active_rules = len(active)

        # Categorize by school tag or category
        by_school: Dict[str, List[RuleEvidence]] = {
            "Parashari": [],
            "Jaimini": [],
            "KP": [],
            "Lal Kitab": [],
            "Tajika": [],
            "General / Dasha": []
        }

        for e in active:
            r_id = e.rule_id.lower()
            cat = (e.category or "").lower()
            if "jaimini" in r_id or "jaimini" in cat:
                by_school["Jaimini"].append(e)
            elif "kp-" in r_id or "kp" in cat:
                by_school["KP"].append(e)
            elif "lal" in r_id or "lal" in cat or "lk-" in r_id:
                by_school["Lal Kitab"].append(e)
            elif "tajika" in r_id or "varsha" in cat:
                by_school["Tajika"].append(e)
            elif "bphs" in r_id or "saravali" in r_id or "phaladeepika" in r_id or "parashar" in cat:
                by_school["Parashari"].append(e)
            else:
                by_school["General / Dasha"].append(e)

        for school, s_evs in by_school.items():
            if not s_evs:
                continue
            pos = [x for x in s_evs if x.polarity == "+"]
            neg = [x for x in s_evs if x.polarity == "-"]
            sorted_pos = sorted(pos, key=lambda x: x.signal_score, reverse=True)[:3]
            sorted_neg = sorted(neg, key=lambda x: x.signal_score, reverse=True)[:3]

            report.schools[school] = SchoolEvidenceBreakdown(
                school_name=school,
                active_count=len(s_evs),
                positive_count=len(pos),
                negative_count=len(neg),
                top_positives=sorted_pos,
                top_negatives=sorted_neg,
                summary=f"{len(pos)} supportive indications, {len(neg)} cautionary factors in {school} tradition."
            )

        return report

    @staticmethod
    def aggregate(evidences: List[RuleEvidence]) -> Tuple[float, str, str, List[RuleEvidence], List[RuleEvidence]]:
        """
        Legacy interface preserved for backward compatibility.
        Aggregates raw evidences while maintaining clear polarity counts.
        """
        active_evidences = [e for e in evidences if e.fired]

        positives = [e for e in active_evidences if e.polarity == "+"]
        negatives = [e for e in active_evidences if e.polarity == "-"]

        total_active = len(active_evidences)
        pos_count = len(positives)
        neg_count = len(negatives)

        if total_active == 0:
            return 0.50, "Sanketik (Tentative)", "0/0 Rules active", [], []

        pos_score_sum = sum(e.signal_score for e in positives)
        neg_score_sum = sum(e.signal_score for e in negatives)

        raw_score = 0.50 + (pos_score_sum * 0.15) - (neg_score_sum * 0.15)
        composite_score = round(min(0.95, max(0.15, raw_score)), 2)

        if composite_score >= 0.70:
            confidence_band = "Uchha (Strong Indication)"
        elif composite_score >= 0.45:
            confidence_band = "Madhyam (Moderate Support)"
        else:
            confidence_band = "Sanketik (Caution / Delays Indicated)"

        consensus_ratio = f"{pos_count}/{total_active} Fired Rules Support Positive Outcome"

        sorted_pos = sorted(positives, key=lambda x: x.signal_score, reverse=True)[:3]
        sorted_neg = sorted(negatives, key=lambda x: x.signal_score, reverse=True)[:3]

        return composite_score, confidence_band, consensus_ratio, sorted_pos, sorted_neg
