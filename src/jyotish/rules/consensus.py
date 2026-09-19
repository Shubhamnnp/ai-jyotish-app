"""
Multi-System Consensus Aggregator for JyotishOS.
Aggregates signals from Dasha, Gochar, Ashtakavarga, and Natal Yogas into:
- Composite probability score (0.0 to 1.0)
- Confidence band (Uchha, Madhyam, Sanketik)
- Agreement ratio across rules
- Ranked top positive and mitigating signals
"""

from typing import List, Tuple
from ..core.models import RuleEvidence


class ConsensusAggregator:
    """Aggregates rule evidences into a transparent multi-system consensus."""

    @staticmethod
    def aggregate(evidences: List[RuleEvidence]) -> Tuple[float, str, str, List[RuleEvidence], List[RuleEvidence]]:
        """
        Returns:
        (composite_score, confidence_band, consensus_ratio, top_positives, top_negatives)
        """
        active_evidences = [e for e in evidences if e.fired]

        positives = [e for e in active_evidences if e.polarity == "+"]
        negatives = [e for e in active_evidences if e.polarity == "-"]

        total_active = len(active_evidences)
        pos_count = len(positives)
        neg_count = len(negatives)

        if total_active == 0:
            return 0.50, "Sanketik (Tentative)", "0/0 Rules active", [], []

        # Weighted calculation
        pos_score_sum = sum(e.signal_score for e in positives)
        neg_score_sum = sum(e.signal_score for e in negatives)

        # Baseline composite score computation
        # Positive signals push score toward 1.0; negative drag it down
        raw_score = 0.50 + (pos_score_sum * 0.15) - (neg_score_sum * 0.15)
        composite_score = round(min(0.95, max(0.15, raw_score)), 2)

        # Confidence Band
        if composite_score >= 0.70:
            confidence_band = "Uchha (High Agreement)"
        elif composite_score >= 0.45:
            confidence_band = "Madhyam (Moderate Support)"
        else:
            confidence_band = "Sanketik (Caution / Delays Indicated)"

        consensus_ratio = f"{pos_count}/{total_active} Fired Rules Support Positive Outcome"

        # Sort top signals
        sorted_pos = sorted(positives, key=lambda x: x.signal_score, reverse=True)[:3]
        sorted_neg = sorted(negatives, key=lambda x: x.signal_score, reverse=True)[:3]

        return composite_score, confidence_band, consensus_ratio, sorted_pos, sorted_neg

