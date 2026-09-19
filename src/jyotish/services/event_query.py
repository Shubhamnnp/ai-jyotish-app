"""
Ghatna Query (Event Window Analysis) Service for JyotishOS.
Orchestrates:
1. Natal Baseline Chart & Divisional Charts
2. Ashtakavarga Calculations
3. Active Vimshottari Dasha Hierarchy at Target Date
4. Planetary Transits & Gochar Triggers
5. 32-Rule Evaluation Engine
6. Multi-System Consensus Aggregation
7. Structured Evidence Packaging
"""

from datetime import date
from typing import Optional

from ..core.models import (
    BirthData, GhatnaQueryInput, GhatnaQueryResult, KundaliChart, TransitSummary
)
from ..core.calculator import default_chart_calculator
from ..core.varga import VargaCalculator
from ..core.ashtakavarga import AshtakavargaCalculator
from ..core.gochar import default_transit_engine
from ..dasha.vimshottari import default_dasha_engine
from ..rules.engine import default_rules_engine
from ..rules.consensus import ConsensusAggregator


DISCLAIMER_TEXT_HI = (
    "वैधानिक एवं नैतिक सूचना: ज्योतिष एक पारम्परिक विद्या और सांस्कृतिक मार्गदर्शक है। "
    "यह गणना गणितीय ग्रहीय स्थिति एवं शास्त्रीय ग्रन्थों के नियमों पर आधारित है। "
    "इसे किसी भी प्रकार की चिकित्सीय (medical), विधिक (legal), या वित्तीय निवेश की निश्चित भविष्यवाणी न समझें। "
    "अंतिम निर्णय अपने विवेक और योग्य विशेषज्ञों के परामर्श से ही लें।"
)

DISCLAIMER_TEXT_EN = (
    "Disclaimer: Vedic Astrology is a traditional interpretive system for reflection and planning. "
    "Calculations are strictly derived from astronomical ephemeris and classical Sanskrit treatises. "
    "This does not constitute medical, legal, or financial advice."
)


class EventQueryService:
    """Core Ghatna Query execution service."""

    def __init__(self):
        self.calculator = default_chart_calculator
        self.dasha_engine = default_dasha_engine
        self.transit_engine = default_transit_engine
        self.rules_engine = default_rules_engine

    def execute_query(
        self,
        query_input: GhatnaQueryInput,
        precomputed_chart: Optional[KundaliChart] = None
    ) -> GhatnaQueryResult:
        """Executes complete Event Window Analysis for a given profile and date."""
        # 1. Compute or use precomputed natal chart
        if precomputed_chart:
            chart = precomputed_chart
        else:
            chart = self.calculator.calculate_chart(query_input.birth_data)
            chart.vargas = VargaCalculator.calculate_all_vargas(chart)
            chart.ashtakavarga = AshtakavargaCalculator.calculate(chart)

        # 2. Compute active Vimshottari Dasha at target date
        birth_dt = chart.birth_data.birth_date
        from datetime import datetime
        full_birth_dt = datetime.combine(chart.birth_data.birth_date, chart.birth_data.birth_time)
        moon_lon = chart.planets["Moon"].longitude
        active_dasha = self.dasha_engine.get_active_dasha_at(
            full_birth_dt, moon_lon, query_input.target_date
        )

        # 3. Compute Transits (Gochar) at target date
        transits, transit_summary = self.transit_engine.compute_transit_snapshot(
            chart, query_input.target_date, chart.ayanamsa_name
        )

        # 4. Evaluate Rules Library (32 rules)
        evidences = self.rules_engine.evaluate_all(
            chart, active_dasha, transits, transit_summary, filter_theme=query_input.theme
        )

        # 5. Consensus Aggregation
        composite_score, confidence_band, consensus_ratio, top_pos, top_neg = (
            ConsensusAggregator.aggregate(evidences)
        )

        # 6. Generate Deterministic Structured Narrative
        narrative_hi, narrative_en = self._generate_narrative(
            query_input, active_dasha, transit_summary, composite_score, top_pos, top_neg
        )

        return GhatnaQueryResult(
            target_date=query_input.target_date,
            target_end_date=query_input.target_end_date,
            theme=query_input.theme,
            composite_score=composite_score,
            confidence_band=confidence_band,
            consensus_ratio=consensus_ratio,
            active_dasha=active_dasha,
            transit_summary=transit_summary,
            top_positive_signals=top_pos,
            top_negative_signals=top_neg,
            all_evaluated_rules=evidences,
            narrative_hi=narrative_hi,
            narrative_en=narrative_en,
            disclaimer=DISCLAIMER_TEXT_HI,
        )

    def _generate_narrative(
        self,
        query_input: GhatnaQueryInput,
        dasha,
        transit: TransitSummary,
        score: float,
        top_pos,
        top_neg
    ) -> tuple[str, str]:
        """Generates clear, transparent Hindi and English summaries based strictly on evidence."""
        d_summary = dasha.formatted_summary
        theme_title = query_input.theme.capitalize()

        # Hindi Narrative Construction
        hi_lines = [
            f"### घटना विश्लेषण सार (विषय: {theme_title} | दिनांक: {query_input.target_date.strftime('%d-%b-%Y')})",
            f"- **सक्रिय विंशोत्तरी दशा:** {d_summary}",
            f"- **समग्र सम्भावना सूचकांक (Composite Score):** {score:.2f} ({'अनुकूल अवसर' if score >= 0.60 else ('मिश्रित / सामान्य' if score >= 0.45 else 'सावधानी / धैर्य की आवश्यकता')})",
            "",
            "#### मुख्य सकारात्मक शास्त्रीय संकेत:",
        ]
        if top_pos:
            for s in top_pos:
                hi_lines.append(f"- **{s.rule_name_hi}** ({s.source_text}): {s.explanation_hi}")
        else:
            hi_lines.append("- इस विषय में कोई असाधारण सकारात्मक शास्त्रीय योग सक्रिय नहीं दिखा।")

        hi_lines.append("\n#### मुख्य अवरोधक / सावधानी संकेत:")
        if top_neg:
            for s in top_neg:
                hi_lines.append(f"- **{s.rule_name_hi}** ({s.source_text}): {s.explanation_hi}")
        else:
            hi_lines.append("- कोई बड़ा नकारात्मक दोष या अवरोध इस अवधि में सक्रिय नहीं है।")

        if transit.is_sade_sati:
            hi_lines.append(f"\n> **गोचर चेतावनी:** {transit.sade_sati_phase} सक्रिय है। कार्यक्षेत्र और पारिवारिक मामलों में अनुशासित रहने की सलाह है।")

        # English Narrative Construction
        en_lines = [
            f"### Event Analysis Summary (Theme: {theme_title} | Date: {query_input.target_date.strftime('%d-%b-%Y')})",
            f"- **Operating Vimshottari Dasha:** {d_summary}",
            f"- **Composite Probability Score:** {score:.2f}",
            "",
            "#### Key Supporting Classical Signals:",
        ]
        if top_pos:
            for s in top_pos:
                en_lines.append(f"- **{s.rule_name_en}** [{s.source_text}]: {s.explanation_hi}")
        else:
            en_lines.append("- No strong affirmative classical indicators active for this theme.")

        en_lines.append("\n#### Key Mitigating / Restrictive Factors:")
        if top_neg:
            for s in top_neg:
                en_lines.append(f"- **{s.rule_name_en}** [{s.source_text}]: {s.explanation_hi}")
        else:
            en_lines.append("- No major obstructive afflictions active for this window.")

        return "\n".join(hi_lines), "\n".join(en_lines)


# Singleton event query service
default_event_query_service = EventQueryService()
