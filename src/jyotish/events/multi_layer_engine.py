"""
Multi-Layer Event Prediction & Timing Engine (Phase 5, Task P5-T2).
Reference: docs/upgrade/MASTER_10_PHASE_ROADMAP.md (Phase 5).

Implements the classical 5-Level Event Fruition Architecture:
- Level 1: Natal Promise in D1 (Bhavas, Lords, Dignities, SAV bindus)
- Level 2: Divisional Chart Confirmation (D9, D10, D7, D4, etc.)
- Level 3: Dasha Hierarchy Resonance (MD, AD, PD lord connectivity to event)
- Level 4: Transit Trigger & Classical Double Transit (Jupiter & Saturn Gochar + SAV)
- Level 5: Classical Yogas & Bhanga Cancellations
Synthesizes with calibrated weights summing strictly to 1.000.
"""

from datetime import date, datetime
from typing import Dict, List, Optional, Any, Union
from enum import Enum
from pydantic import BaseModel, Field

from ..core.models import KundaliChart, PlanetPosition, HouseCusp
from ..core.varga import VargaCalculator
from ..core.gochar import default_transit_engine
from ..dasha.vimshottari import default_dasha_engine
from ..core.yoga import ClassicalYogaDoshaEngine
from ..rules.conflict_graph import default_conflict_graph
from .taxonomy import EventDefinition, default_event_taxonomy


class EventFruitionState(str, Enum):
    HIGH_FRUITION_WINDOW = "HIGH_FRUITION_WINDOW"
    FAVORABLE_WINDOW = "FAVORABLE_WINDOW"
    MODERATE_WINDOW = "MODERATE_WINDOW"
    OBSTRUCTED_WINDOW = "OBSTRUCTED_WINDOW"


class LayerEvaluation(BaseModel):
    layer_num: int
    name: str
    score: float = Field(ge=0.0, le=1.0)
    weight: float
    contribution: float
    reasons_en: List[str] = Field(default_factory=list)
    reasons_hi: List[str] = Field(default_factory=list)


class MultiLayerPredictionResult(BaseModel):
    event_id: str
    event_name_en: str
    event_name_hi: str
    target_date: date
    timing_confidence: float = Field(ge=0.0, le=1.0)
    fruition_state: EventFruitionState
    is_window_active: bool
    double_transit_active: bool
    active_md_lord: str
    active_ad_lord: str
    active_pd_lord: str
    level_breakdown: Dict[str, LayerEvaluation]
    summary_en: str
    summary_hi: str
    cancellations: List[str] = Field(default_factory=list)


# Calibrated layer weights summing strictly to 1.000
LAYER_WEIGHTS = {
    "level_1_natal": 0.20,
    "level_2_varga": 0.15,
    "level_3_dasha": 0.35,
    "level_4_transit": 0.20,
    "level_5_yoga": 0.10
}


def _get_house_by_num(chart: KundaliChart, house_num: int) -> Optional[HouseCusp]:
    """Safely retrieves a house cusp regardless of list or dict storage."""
    if isinstance(chart.houses, list):
        if 1 <= house_num <= len(chart.houses):
            return chart.houses[house_num - 1]
        return None
    elif isinstance(chart.houses, dict):
        return chart.houses.get(house_num)
    return None


class MultiLayerPredictionEngine:
    """Evaluates life event probability across 5 classical Vedic layers."""

    @classmethod
    def evaluate_event(
        cls,
        chart: KundaliChart,
        event_id: str,
        target_date: date
    ) -> MultiLayerPredictionResult:
        ev_def = default_event_taxonomy.get_event(event_id)
        if not ev_def:
            raise ValueError(f"Unknown event_id: '{event_id}'. Valid events: {list(default_event_taxonomy.CANONICAL_EVENTS.keys())}")

        # -------------------------------------------------------------
        # LEVEL 1: Natal Promise in D1 (Weight 0.20)
        # -------------------------------------------------------------
        l1_score, l1_reasons_en, l1_reasons_hi = cls._eval_level_1_natal(chart, ev_def)

        # -------------------------------------------------------------
        # LEVEL 2: Divisional Chart Confirmation (Weight 0.15)
        # -------------------------------------------------------------
        l2_score, l2_reasons_en, l2_reasons_hi = cls._eval_level_2_varga(chart, ev_def)

        # -------------------------------------------------------------
        # LEVEL 3: Dasha Hierarchy (Weight 0.35)
        # -------------------------------------------------------------
        l3_score, md_lord, ad_lord, pd_lord, l3_reasons_en, l3_reasons_hi = cls._eval_level_3_dasha(
            chart, ev_def, target_date
        )

        # -------------------------------------------------------------
        # LEVEL 4: Transit & Double Transit Trigger (Weight 0.20)
        # -------------------------------------------------------------
        l4_score, dt_active, l4_reasons_en, l4_reasons_hi = cls._eval_level_4_transit(
            chart, ev_def, target_date
        )

        # -------------------------------------------------------------
        # LEVEL 5: Classical Yogas & Bhanga Cancellations (Weight 0.10)
        # -------------------------------------------------------------
        l5_score, cancellations, l5_reasons_en, l5_reasons_hi = cls._eval_level_5_yoga(chart, ev_def)

        # -------------------------------------------------------------
        # Synthesis & Calibrated Confidence Score
        # -------------------------------------------------------------
        breakdown = {
            "level_1_natal": LayerEvaluation(
                layer_num=1,
                name="Natal Promise (D1)",
                score=round(l1_score, 3),
                weight=LAYER_WEIGHTS["level_1_natal"],
                contribution=round(l1_score * LAYER_WEIGHTS["level_1_natal"], 3),
                reasons_en=l1_reasons_en,
                reasons_hi=l1_reasons_hi
            ),
            "level_2_varga": LayerEvaluation(
                layer_num=2,
                name=f"Varga Confirmation ({ev_def.varga})",
                score=round(l2_score, 3),
                weight=LAYER_WEIGHTS["level_2_varga"],
                contribution=round(l2_score * LAYER_WEIGHTS["level_2_varga"], 3),
                reasons_en=l2_reasons_en,
                reasons_hi=l2_reasons_hi
            ),
            "level_3_dasha": LayerEvaluation(
                layer_num=3,
                name="Dasha Hierarchy Alignment",
                score=round(l3_score, 3),
                weight=LAYER_WEIGHTS["level_3_dasha"],
                contribution=round(l3_score * LAYER_WEIGHTS["level_3_dasha"], 3),
                reasons_en=l3_reasons_en,
                reasons_hi=l3_reasons_hi
            ),
            "level_4_transit": LayerEvaluation(
                layer_num=4,
                name="Transit & Double Transit Trigger",
                score=round(l4_score, 3),
                weight=LAYER_WEIGHTS["level_4_transit"],
                contribution=round(l4_score * LAYER_WEIGHTS["level_4_transit"], 3),
                reasons_en=l4_reasons_en,
                reasons_hi=l4_reasons_hi
            ),
            "level_5_yoga": LayerEvaluation(
                layer_num=5,
                name="Classical Yogas & Cancellations",
                score=round(l5_score, 3),
                weight=LAYER_WEIGHTS["level_5_yoga"],
                contribution=round(l5_score * LAYER_WEIGHTS["level_5_yoga"], 3),
                reasons_en=l5_reasons_en,
                reasons_hi=l5_reasons_hi
            ),
        }

        total_confidence = sum(layer.contribution for layer in breakdown.values())
        total_confidence = max(0.0, min(1.0, total_confidence))

        # Determine Fruition State
        if total_confidence >= 0.70 and (dt_active or l3_score >= 0.65):
            state = EventFruitionState.HIGH_FRUITION_WINDOW
            is_active = True
        elif total_confidence >= 0.55:
            state = EventFruitionState.FAVORABLE_WINDOW
            is_active = True
        elif total_confidence >= 0.42:
            state = EventFruitionState.MODERATE_WINDOW
            is_active = False
        else:
            state = EventFruitionState.OBSTRUCTED_WINDOW
            is_active = False

        state_en_map = {
            EventFruitionState.HIGH_FRUITION_WINDOW: "High Fruition Alignment",
            EventFruitionState.FAVORABLE_WINDOW: "Favorable Alignment",
            EventFruitionState.MODERATE_WINDOW: "Moderate / Deliberate Progression",
            EventFruitionState.OBSTRUCTED_WINDOW: "Obstructed / Low Potential"
        }
        state_hi_map = {
            EventFruitionState.HIGH_FRUITION_WINDOW: "अत्यंत अनुकूल एवं प्रबल फलदायी कालखंड",
            EventFruitionState.FAVORABLE_WINDOW: "अनुकूल कालखंड",
            EventFruitionState.MODERATE_WINDOW: "मध्यम गतिशीलता",
            EventFruitionState.OBSTRUCTED_WINDOW: "प्रतिकूल अथवा अवरुद्ध कालखंड"
        }

        summary_en = (
            f"Event analysis for '{ev_def.name_en}' at {target_date}: {state_en_map[state]} "
            f"(Confidence: {total_confidence:.2f}). Operating Dasha: {md_lord} MD / {ad_lord} AD / {pd_lord} PD. "
            f"Double Transit active: {dt_active}."
        )
        summary_hi = (
            f"'{ev_def.name_hi}' हेतु {target_date} पर बहु-स्तरीय विश्लेषण: {state_hi_map[state]} "
            f"(अनुकूलता सूचकांक: {total_confidence:.2f})। सक्रिय दशा: {md_lord} महादशा / {ad_lord} अंतर्दशा / {pd_lord} प्रत्यंतर। "
            f"डबल ट्रांजिट सक्रिय: {'हाँ' if dt_active else 'नहीं'}।"
        )

        return MultiLayerPredictionResult(
            event_id=ev_def.event_id,
            event_name_en=ev_def.name_en,
            event_name_hi=ev_def.name_hi,
            target_date=target_date,
            timing_confidence=round(total_confidence, 3),
            fruition_state=state,
            is_window_active=is_active,
            double_transit_active=dt_active,
            active_md_lord=md_lord,
            active_ad_lord=ad_lord,
            active_pd_lord=pd_lord,
            level_breakdown=breakdown,
            summary_en=summary_en,
            summary_hi=summary_hi,
            cancellations=cancellations
        )

    # -----------------------------------------------------------------
    # Internal Evaluation Helpers
    # -----------------------------------------------------------------

    @classmethod
    def _eval_level_1_natal(cls, chart: KundaliChart, ev: EventDefinition) -> tuple:
        score = 0.50
        reasons_en = []
        reasons_hi = []

        # Check primary house lords and occupants
        for h_num in ev.primary_houses:
            h = _get_house_by_num(chart, h_num)
            if not h:
                continue
            h_lord = chart.planets.get(h.lord)
            if h_lord:
                if h_lord.dignity in ("exalted", "own", "moolatrikona"):
                    score += 0.15
                    reasons_en.append(f"Primary House {h_num} lord {h.lord} is {h_lord.dignity}")
                    reasons_hi.append(f"प्राथमिक भाव {h_num} का स्वामी {h.lord} {h_lord.dignity} अवस्था में है")
                elif h_lord.dignity == "debilitated":
                    score -= 0.15
                    reasons_en.append(f"Primary House {h_num} lord {h.lord} is debilitated")
                    reasons_hi.append(f"प्राथमिक भाव {h_num} का स्वामी {h.lord} नीच राशि में है")

        # Check primary karakas
        for k_name in ev.primary_karakas:
            kp = chart.planets.get(k_name)
            if kp:
                if kp.dignity in ("exalted", "own", "friend"):
                    score += 0.10
                    reasons_en.append(f"Karaka {k_name} possesses auspicious dignity ({kp.dignity})")
                    reasons_hi.append(f"कारक ग्रह {k_name} शुभ गरिमा ({kp.dignity}) में स्थित है")
                elif kp.dignity == "debilitated":
                    score -= 0.10

        score = max(0.20, min(1.0, score))
        return score, reasons_en, reasons_hi

    @classmethod
    def _eval_level_2_varga(cls, chart: KundaliChart, ev: EventDefinition) -> tuple:
        score = 0.55
        reasons_en = []
        reasons_hi = []

        varga_code = ev.varga if ev.varga != "D1" else "D9"
        vargas = VargaCalculator.calculate_all_vargas(chart)
        varga_chart = vargas.get(varga_code)

        if varga_chart:
            # Check varga placement of primary karakas
            for k_name in ev.primary_karakas:
                vp = varga_chart.planets.get(k_name)
                d1_p = chart.planets.get(k_name)
                if vp and d1_p:
                    if vp.sign_id == d1_p.sign_id:
                        score += 0.20
                        reasons_en.append(f"Karaka {k_name} is Vargottama in {varga_code}")
                        reasons_hi.append(f"कारक ग्रह {k_name} {varga_code} में वर्गोत्तम है")
                    elif vp.house_number in (1, 4, 7, 10, 5, 9):
                        score += 0.10
                        reasons_en.append(f"Karaka {k_name} in auspicious Kendra/Trikona ({vp.house_number}) in {varga_code}")
                        reasons_hi.append(f"कारक ग्रह {k_name} {varga_code} के केंद्र/त्रिकोण भाव {vp.house_number} में स्थित है")

        score = max(0.20, min(1.0, score))
        return score, reasons_en, reasons_hi

    @classmethod
    def _eval_level_3_dasha(cls, chart: KundaliChart, ev: EventDefinition, target_date: date) -> tuple:
        score = 0.40
        reasons_en = []
        reasons_hi = []

        full_dt = datetime.combine(chart.birth_data.birth_date, chart.birth_data.birth_time)
        moon_lon = chart.planets["Moon"].longitude
        active_dasha = default_dasha_engine.get_active_dasha_at(full_dt, moon_lon, target_date)

        md_lord = active_dasha.mahadasha.lord if hasattr(active_dasha, "mahadasha") else "Unknown"
        ad_lord = active_dasha.antardasha.lord if hasattr(active_dasha, "antardasha") else "Unknown"
        pd_lord = active_dasha.pratyantardasha.lord if hasattr(active_dasha, "pratyantardasha") else "Unknown"

        # Check significator status of MD and AD lords
        primary_houses_objs = [_get_house_by_num(chart, h) for h in ev.primary_houses]
        secondary_houses_objs = [_get_house_by_num(chart, h) for h in ev.secondary_houses]

        primary_lords = {h.lord for h in primary_houses_objs if h}
        secondary_lords = {h.lord for h in secondary_houses_objs if h}
        all_event_karakas = set(ev.primary_karakas + ev.secondary_karakas)

        # Mahadasha lord resonance
        if md_lord in primary_lords:
            score += 0.25
            reasons_en.append(f"MD lord {md_lord} rules primary house of {ev.name_en}")
            reasons_hi.append(f"महादशा स्वामी {md_lord} घटना के प्राथमिक भाव का स्वामी है")
        elif md_lord in all_event_karakas or md_lord in secondary_lords:
            score += 0.15
            reasons_en.append(f"MD lord {md_lord} is a canonical significator/karaka")
            reasons_hi.append(f"महादशा स्वामी {md_lord} घटना का कारक अथवा सहायक भावेश है")

        # Antardasha lord resonance
        if ad_lord in primary_lords:
            score += 0.25
            reasons_en.append(f"AD lord {ad_lord} rules primary house")
            reasons_hi.append(f"अंतर्दशा स्वामी {ad_lord} प्राथमिक भाव का अधिपति है")
        elif ad_lord in all_event_karakas or ad_lord in secondary_lords:
            score += 0.15
            reasons_en.append(f"AD lord {ad_lord} is a canonical significator/karaka")
            reasons_hi.append(f"अंतर्दशा स्वामी {ad_lord} घटना का कारक अथवा सहायक भावेश है")

        score = max(0.20, min(1.0, score))
        return score, md_lord, ad_lord, pd_lord, reasons_en, reasons_hi

    @classmethod
    def _eval_level_4_transit(cls, chart: KundaliChart, ev: EventDefinition, target_date: date) -> tuple:
        score = 0.40
        reasons_en = []
        reasons_hi = []
        dt_active = False

        transits, summary = default_transit_engine.compute_transit_snapshot(chart, target_date)
        jup_info = transits.get("Jupiter")
        sat_info = transits.get("Saturn")

        if jup_info and sat_info:
            jup_house = jup_info.get("house_from_lagna", 1)
            sat_house = sat_info.get("house_from_lagna", 1)

            # Classical aspects from house_from_lagna
            # Jupiter aspects 1st (conjunction), 5th, 7th, 9th from its position
            jup_aspects = {jup_house, (jup_house + 4 - 1) % 12 + 1, (jup_house + 6 - 1) % 12 + 1, (jup_house + 8 - 1) % 12 + 1}
            # Saturn aspects 1st (conjunction), 3rd, 7th, 10th from its position
            sat_aspects = {sat_house, (sat_house + 2 - 1) % 12 + 1, (sat_house + 6 - 1) % 12 + 1, (sat_house + 9 - 1) % 12 + 1}

            for p_h in ev.primary_houses:
                jup_influences = (p_h in jup_aspects)
                sat_influences = (p_h in sat_aspects)

                if jup_influences and sat_influences:
                    dt_active = True
                    score += 0.35
                    reasons_en.append(f"Classical Double Transit active on primary house {p_h} (Jupiter in house {jup_house}, Saturn in house {sat_house})")
                    reasons_hi.append(f"प्राथमिक भाव {p_h} पर शास्त्रीय डबल ट्रांजिट (गुरु व शनि दोनों का प्रभाव) सक्रिय है")
                    break
                elif jup_influences:
                    score += 0.15
                    reasons_en.append(f"Benefic Jupiter transits/aspects house {p_h}")
                    reasons_hi.append(f"शुभ गुरु गोचर भाव {p_h} पर दृष्टि/स्थिति द्वारा प्रभाव डाल रहा है")
                elif sat_influences:
                    score += 0.10
                    reasons_en.append(f"Saturn activates house {p_h} via transit")
                    reasons_hi.append(f"शनि गोचर भाव {p_h} को सक्रिय कर रहा है")

            if summary.is_jupiter_saturn_double_transit_on_10th and 10 in ev.primary_houses:
                dt_active = True
                score = max(score, 0.75)

        score = max(0.20, min(1.0, score))
        return score, dt_active, reasons_en, reasons_hi

    @classmethod
    def _eval_level_5_yoga(cls, chart: KundaliChart, ev: EventDefinition) -> tuple:
        score = 0.50
        cancellations = []
        reasons_en = []
        reasons_hi = []

        # Check yoga cancellations
        if default_conflict_graph.check_kemadruma_bhanga(chart):
            cancellations.append("Kemadruma Bhanga Active")
            score += 0.10
            reasons_en.append("Kemadruma Bhanga nullifies lunar isolation")
            reasons_hi.append("केमद्रुम भंग योग सक्रिय है")

        nb_list = default_conflict_graph.check_neechabhanga(chart)
        if nb_list:
            cancellations.extend(nb_list)
            score += 0.15
            reasons_en.append(f"Neechabhanga Rajayoga active ({len(nb_list)} cancellations)")
            reasons_hi.append(f"नीचभंग राजयोग सक्रिय है ({len(nb_list)} परिहार)")

        # Evaluate classical yogas
        y_result = ClassicalYogaDoshaEngine.evaluate_all(chart)
        active_raja_dhana = [y for y in y_result.yogas if y.is_active and ("Raja" in y.name_en or "Dhana" in y.name_en or "Mahapurusha" in y.name_en)]
        if active_raja_dhana and ev.is_favorable:
            score += 0.15
            reasons_en.append(f"Active auspicious classical yogas: {', '.join(y.name_en for y in active_raja_dhana[:2])}")
            reasons_hi.append(f"सक्रिय शुभ योग: {', '.join(y.name_hi for y in active_raja_dhana[:2])}")

        score = max(0.20, min(1.0, score))
        return score, cancellations, reasons_en, reasons_hi


default_multi_layer_engine = MultiLayerPredictionEngine()
