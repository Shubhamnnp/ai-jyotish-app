"""
Ghatna Query & Multi-Layer Event Timing Engine (Phase 5, Task P5-T3).
Reference: docs/upgrade/MASTER_10_PHASE_ROADMAP.md (Phase 5).

Upgraded from legacy heuristic threshold (0.55 cutoff) to the classical 5-level
fruition architecture with grounded Evidence Packs and Dasha/Transit timing.
"""

from datetime import date, datetime
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field

from ..core.models import BirthData, KundaliChart
from ..core.calculator import default_chart_calculator
from ..evidence.factors import default_factor_extractor
from ..evidence.domains.analyzer import default_domain_analyzer
from ..evidence.pack import default_evidence_pack_builder, EvidencePack
from .taxonomy import default_event_taxonomy
from .multi_layer_engine import default_multi_layer_engine, MultiLayerPredictionResult, EventFruitionState


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
    event_id: Optional[str] = None
    fruition_state: Optional[str] = None
    level_breakdown: Optional[Dict[str, Any]] = None


# Domain-to-default-event mapping
DOMAIN_TO_EVENT_MAP = {
    "career": "career_recognition",
    "job": "job_start",
    "promotion": "promotion",
    "marriage": "marriage",
    "relationship": "marriage",
    "wealth": "property_purchase",
    "property": "property_purchase",
    "progeny": "childbirth",
    "children": "childbirth",
    "travel": "foreign_travel",
    "health": "disease_onset",
    "legal": "litigation"
}


class GhatnaQueryEngine:
    """Evaluates life event windows grounded on Evidence Packs and Multi-Layer Engine."""

    @classmethod
    def evaluate_event_window(
        cls,
        birth_data: BirthData,
        target_date: date,
        domain: str = "career",
        event_id: Optional[str] = None
    ) -> GhatnaQueryResult:
        """
        Evaluates whether target_date serves as an auspicious/active fruition window
        using the classical 5-layer pipeline (Natal, Varga, Dasha, Double Transit, Yogas).
        """
        chart = default_chart_calculator.calculate_full_chart(birth_data)
        domain_clean = domain.strip().lower()

        # Resolve event_id
        if not event_id:
            event_id = DOMAIN_TO_EVENT_MAP.get(domain_clean, "career_recognition")

        # 1. Evaluate via MultiLayerPredictionEngine (5 Classical Layers)
        multi_layer_res: MultiLayerPredictionResult = default_multi_layer_engine.evaluate_event(
            chart=chart,
            event_id=event_id,
            target_date=target_date
        )

        # 2. Build Grounded Evidence Pack
        evidence_pack = default_evidence_pack_builder.build_evidence_pack(
            chart=chart,
            domain=domain_clean if domain_clean in ("career", "marriage", "wealth", "health") else "career",
            school="parashari"
        )

        # 3. Annotate findings with active timing and layer evidence
        for finding in evidence_pack.findings:
            finding.timing.dasha_support.append(
                f"Active during {multi_layer_res.active_md_lord} MD / {multi_layer_res.active_ad_lord} AD"
            )
            if multi_layer_res.double_transit_active:
                finding.timing.transit_support.append(
                    f"Triggered by Classical Double Transit at {target_date}"
                )

        operating_dasha_str = f"{multi_layer_res.active_md_lord} MD"
        operating_ad_str = f"{multi_layer_res.active_ad_lord} AD"

        # Collect timing reasons across layers 3 and 4
        all_reasons = (
            multi_layer_res.level_breakdown["level_3_dasha"].reasons_en +
            multi_layer_res.level_breakdown["level_4_transit"].reasons_en
        )

        level_dict = {
            k: {
                "score": v.score,
                "weight": v.weight,
                "contribution": v.contribution,
                "reasons": v.reasons_en
            }
            for k, v in multi_layer_res.level_breakdown.items()
        }

        return GhatnaQueryResult(
            domain=domain_clean,
            target_date=target_date,
            is_window_active=multi_layer_res.is_window_active,
            timing_confidence=multi_layer_res.timing_confidence,
            operating_dasha=operating_dasha_str,
            operating_bhukti=operating_ad_str,
            double_transit_active=multi_layer_res.double_transit_active,
            grounded_evidence_pack=evidence_pack,
            timing_reasons=all_reasons,
            event_summary_en=multi_layer_res.summary_en,
            event_summary_hi=multi_layer_res.summary_hi,
            disclaimers=evidence_pack.disclaimers,
            event_id=event_id,
            fruition_state=multi_layer_res.fruition_state.value,
            level_breakdown=level_dict
        )


default_ghatna_engine = GhatnaQueryEngine()
