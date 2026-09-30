"""
Rule Conflict Graph & Master Directive Rule 5 Astrological Evidence Synthesis.
Detects classical cancellations (Neechabhanga, Kemadruma Bhanga, Manglik Bhanga),
resolves opposing shastriya yogas/doshas, and assigns calibrated evidence confidence states:
- Strongly Supported
- Supported
- Moderately Supported
- Weakly Supported
- Conflicting
- Inconclusive
- Not Supported
"""

from enum import Enum
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field
from ..core.constants import KENDRA_HOUSES, TRIKONA_HOUSES, SIGN_LORDS
from ..core.models import KundaliChart, RuleEvidence


class AstrologicalEvidenceStatus(str, Enum):
    STRONGLY_SUPPORTED = "Strongly Supported"
    SUPPORTED = "Supported"
    MODERATELY_SUPPORTED = "Moderately Supported"
    WEAKLY_SUPPORTED = "Weakly Supported"
    CONFLICTING = "Conflicting"
    INCONCLUSIVE = "Inconclusive"
    NOT_SUPPORTED = "Not Supported"


class SynthesizedThemeEvidence(BaseModel):
    theme: str
    status: AstrologicalEvidenceStatus
    confidence_score: float = 0.0
    positive_weight: float = 0.0
    negative_weight: float = 0.0
    synthesis_summary_hi: str
    synthesis_summary_en: str
    active_cancellations: List[str] = Field(default_factory=list)
    supporting_rules_count: int = 0
    opposing_rules_count: int = 0


class RuleConflictGraph:
    """Evaluates cross-rule cancellations, bhangas, and evidence synthesis."""

    def check_neechabhanga(self, chart: KundaliChart) -> List[str]:
        """
        Detects classical cancellation of debilitation (Neechabhanga):
        1. Debilitation sign lord is in Kendra from Lagna or Moon.
        2. Planet that exalts in that sign is in Kendra from Lagna or Moon.
        """
        cancellations = []
        for p_name, pos in chart.planets.items():
            if pos.dignity == "debilitated":
                sign_name = pos.sign_name
                sign_lord = SIGN_LORDS.get(sign_name)
                lord_p = chart.planets.get(sign_lord)
                if lord_p and (lord_p.house_from_lagna in KENDRA_HOUSES or lord_p.house_from_moon in KENDRA_HOUSES):
                    cancellations.append(f"{p_name} Neechabhanga: Lord {sign_lord} in Kendra")
        return cancellations

    def check_kemadruma_bhanga(self, chart: KundaliChart) -> bool:
        """
        Kemadruma Bhanga (Cancellation):
        - Moon in Kendra (1, 4, 7, 10) from Lagna.
        - Benefics (Jupiter, Venus, Mercury) in Kendra from Moon or Lagna.
        """
        moon = chart.planets.get("Moon")
        if not moon:
            return False

        if moon.house_from_lagna in KENDRA_HOUSES:
            return True

        for b_name in ["Jupiter", "Venus", "Mercury"]:
            bp = chart.planets.get(b_name)
            if bp and (bp.house_from_lagna in KENDRA_HOUSES or bp.house_from_moon in KENDRA_HOUSES):
                return True

        return False

    def check_manglik_bhanga(self, chart: KundaliChart) -> bool:
        """
        Manglik Dosha Cancellation:
        - Mars in own sign (Aries, Scorpio) or exalted (Capricorn).
        - Jupiter aspects or conjuncts Mars.
        """
        mars = chart.planets.get("Mars")
        if not mars:
            return False

        if mars.dignity in ("exalted", "own"):
            return True

        jup = chart.planets.get("Jupiter")
        if jup:
            diff = abs(jup.house_from_lagna - mars.house_from_lagna)
            if diff in (0, 4, 6, 8):
                return True

        return False

    def synthesize_conflicts(
        self,
        evidences: List[RuleEvidence],
        chart: KundaliChart,
        target_theme: str = "career"
    ) -> Dict[str, SynthesizedThemeEvidence]:
        """
        Synthesizes fired rules for a target theme, evaluates cancellations,
        and assigns calibrated status per Master Directive Rule 5.
        """
        target_theme = target_theme.strip().lower()

        pos_weight = 0.0
        neg_weight = 0.0
        pos_rules = []
        neg_rules = []
        cancellations = []

        if self.check_kemadruma_bhanga(chart):
            cancellations.append("केमद्रुम भंग (Kemadruma Bhanga Active - Moon/Benefics in Kendra)")
        nb = self.check_neechabhanga(chart)
        cancellations.extend(nb)
        if self.check_manglik_bhanga(chart):
            cancellations.append("मांगलिक दोष भंग (Manglik Dosha Bhanga Active)")

        for ev in evidences:
            if not ev.fired:
                continue

            themes_lower = [t.lower() for t in ev.themes]
            if target_theme != "all" and target_theme not in themes_lower and ev.category not in ("dasha-gochar", "bhav-based"):
                continue

            if "kemadruma" in ev.rule_id.lower() and self.check_kemadruma_bhanga(chart):
                continue
            if "mangal" in ev.rule_id.lower() and self.check_manglik_bhanga(chart):
                continue

            if ev.polarity == "+":
                pos_weight += ev.signal_score
                pos_rules.append(ev)
            elif ev.polarity == "-":
                neg_weight += ev.signal_score
                neg_rules.append(ev)

        total_weight = pos_weight + neg_weight
        confidence = (pos_weight / (total_weight + 0.001)) if total_weight > 0 else 0.50

        if pos_weight >= 1.2 and neg_weight < 0.4:
            status = AstrologicalEvidenceStatus.STRONGLY_SUPPORTED
            status_hi = "प्रबल शास्त्र-सम्मत समर्थन (Strongly Supported)"
            status_en = "Strongly Supported by Classical Consensus"
        elif pos_weight >= 0.6 and neg_weight <= 0.6:
            status = AstrologicalEvidenceStatus.SUPPORTED
            status_hi = "शास्त्र-सम्मत समर्थन (Supported)"
            status_en = "Supported by Classical Rules"
        elif pos_weight > neg_weight:
            status = AstrologicalEvidenceStatus.MODERATELY_SUPPORTED
            status_hi = "मध्यम शास्त्र-सम्मत समर्थन (Moderately Supported)"
            status_en = "Moderately Supported"
        elif abs(pos_weight - neg_weight) < 0.3 and total_weight > 1.0:
            status = AstrologicalEvidenceStatus.CONFLICTING
            status_hi = "परस्पर-विरोधी शास्त्रीय योग (Conflicting Signals)"
            status_en = "Conflicting Astrological Signals"
        elif pos_weight > 0:
            status = AstrologicalEvidenceStatus.WEAKLY_SUPPORTED
            status_hi = "आंशिक समर्थन (Weakly Supported)"
            status_en = "Weakly Supported"
        else:
            status = AstrologicalEvidenceStatus.NOT_SUPPORTED
            status_hi = "समर्थन अनुपलब्ध (Not Supported)"
            status_en = "Not Supported by Current Alignments"

        summary_hi = (
            f"{target_theme.capitalize()} विषय पर {len(pos_rules)} शुभ योग एवं {len(neg_rules)} सतर्कता सूचक प्राप्त हुए। "
            f"शुद्ध शास्त्रीय प्रमाण बल: {pos_weight:.2f} (+), विरोध बल: {neg_weight:.2f} (-)। निष्कर्ष: {status_hi}।"
        )
        if cancellations:
            summary_hi += f" सक्रिय शास्त्रीय परिहार: {', '.join(cancellations)}।"

        summary_en = (
            f"For {target_theme}, {len(pos_rules)} auspicious yogas and {len(neg_rules)} cautionary indications fired. "
            f"Positive evidence weight: {pos_weight:.2f}, opposing: {neg_weight:.2f}. Status: {status_en}."
        )

        result = SynthesizedThemeEvidence(
            theme=target_theme,
            status=status,
            confidence_score=round(confidence, 3),
            positive_weight=round(pos_weight, 2),
            negative_weight=round(neg_weight, 2),
            synthesis_summary_hi=summary_hi,
            synthesis_summary_en=summary_en,
            active_cancellations=cancellations,
            supporting_rules_count=len(pos_rules),
            opposing_rules_count=len(neg_rules)
        )

        return {target_theme: result}


default_conflict_graph = RuleConflictGraph()
