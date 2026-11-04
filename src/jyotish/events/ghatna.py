"""
Ghatna Query & Event Window Analysis Engine (Phase 5, Task P5-T4).
Reference: docs/IMPLEMENTATION_PRD.md (Section 5.4, P5-T4).

Refactored to consume grounded Evidence Packs and Dasha/Transit Timing evaluations.
Solves event-window questions across career, marriage, travel, and material fruition
using verified planetary factors instead of ungrounded templates.
"""

from datetime import date, datetime
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field

from ..core.models import BirthData, KundaliChart
from ..core.calculator import default_chart_calculator
from ..evidence.factors import default_factor_extractor
from ..evidence.domains.analyzer import default_domain_analyzer
from ..evidence.timing import default_timing_integrator, TimingEvaluation
from ..evidence.pack import default_evidence_pack_builder, EvidencePack


class GhatnaQueryResult(BaseModel):
    """Structured result of an Event-Window / Ghatna Query."""
    domain: str
    target_date: date
    is_window_active: bool
    timing_confidence: float = Field(ge=0.0, le=1.0)
    operating_dasha: str
    operating_bhukti: str
    double_transit_active: bool
    grounded_evidence_pack: EvidencePack
    timing_reasons: List[str] = Field(default_factory=list)
    event_summary_en: str
    event_summary_hi: str
    disclaimers: List[str] = Field(default_factory=list)


class GhatnaQueryEngine:
    """Evaluates life event windows grounded on Evidence Packs."""

    @classmethod
    def evaluate_event_window(
        cls,
        birth_data: BirthData,
        target_date: date,
        domain: str = "career"
    ) -> GhatnaQueryResult:
        """
        Evaluates whether target_date serves as a high-probability fruition window
        for domain based on chart potential, dasha hierarchy, and double transit.
        """
        chart = default_chart_calculator.calculate_full_chart(birth_data)
        factors = default_factor_extractor.extract_factors(chart)
        domain_clean = domain.strip().lower()

        # 1. Domain Significators & Timing
        sigs = default_domain_analyzer.get_significators(domain_clean)
        timing_eval: TimingEvaluation = default_timing_integrator.evaluate_timing_for_domain(
            chart=chart,
            factors=factors,
            target_date=target_date,
            primary_bhavas=sigs.parashari_primary_bhavas,
            primary_karakas=sigs.parashari_karakas
        )

        # 2. Grounded Evidence Pack
        evidence_pack = default_evidence_pack_builder.build_evidence_pack(
            chart=chart,
            domain=domain_clean,
            school="parashari"
        )

        # Annotate findings with active timing
        for finding in evidence_pack.findings:
            if timing_eval.is_dasha_significator:
                finding.timing.dasha_support.append(
                    f"Active during {timing_eval.active_md_lord} MD / {timing_eval.active_ad_lord} AD"
                )
            if timing_eval.is_double_transit_active:
                finding.timing.transit_support.append(
                    f"Triggered by Double Transit at {target_date}"
                )

        # 3. Formulate Summary
        is_active = (timing_eval.timing_confidence >= 0.55)
        operating_dasha_str = f"{timing_eval.active_md_lord} ({timing_eval.md_window})"
        operating_ad_str = f"{timing_eval.active_ad_lord} ({timing_eval.ad_window})"

        status_en = "Favorable Alignment" if is_active else "Moderate / Deliberate Progression"
        status_hi = "अनुकूल कालखंड" if is_active else "सामान्य / मध्यम गतिशीलता"

        all_reasons = timing_eval.dasha_significance_reasons + timing_eval.transit_reasons

        summary_en = (
            f"Event analysis for {sigs.display_name_en} at {target_date}: {status_en}. "
            f"Operating Dasha: {operating_dasha_str}, Antar: {operating_ad_str}. "
            f"Timing confidence: {timing_eval.timing_confidence:.2f}."
        )
        summary_hi = (
            f"{sigs.display_name_hi} हेतु {target_date} पर विश्लेषण: {status_hi}। "
            f"सक्रिय दशा: {timing_eval.active_md_lord} महादशा / {timing_eval.active_ad_lord} अंतर्दशा। "
            f"समय अनुकूलता सूचकांक: {timing_eval.timing_confidence:.2f}।"
        )

        return GhatnaQueryResult(
            domain=domain_clean,
            target_date=target_date,
            is_window_active=is_active,
            timing_confidence=timing_eval.timing_confidence,
            operating_dasha=operating_dasha_str,
            operating_bhukti=operating_ad_str,
            double_transit_active=timing_eval.is_double_transit_active,
            grounded_evidence_pack=evidence_pack,
            timing_reasons=all_reasons,
            event_summary_en=summary_en,
            event_summary_hi=summary_hi,
            disclaimers=evidence_pack.disclaimers
        )


default_ghatna_engine = GhatnaQueryEngine()
