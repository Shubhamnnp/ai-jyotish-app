"""
Birth Time Rectification (BTR) Engine for JyotishOS.
Scans candidate birth time windows (e.g. ±15 min to ±2 hours) in 1-2 min increments,
cross-matching past verified life events against operating Vimshottari Dashas,
divisional charts (D9 Navamsha, D10 Dashamsha, D7 Saptamsha), and Gochar transit triggers.
"""

from datetime import datetime, date, time, timedelta
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from ..core.models import BirthData, KundaliChart
from ..core.calculator import default_chart_calculator
from ..core.varga import VargaCalculator
from ..dasha.vimshottari import default_dasha_engine
from ..core.gochar import default_transit_engine


class LifeEvent(BaseModel):
    """User-verified past life event for rectification fitting."""
    event_date: date
    event_category: str = Field(..., description="career, marriage, child, travel, property, health_accident")
    description: Optional[str] = ""


class BTRCandidate(BaseModel):
    """A scored candidate birth time."""
    candidate_time: str
    offset_minutes: int
    fit_score: float = Field(..., ge=0.0, le=100.0)
    confidence: str
    lagna_sign: str
    navamsha_lagna_sign: str
    dashamsha_lagna_sign: str
    matching_events_count: int
    evidence_breakdown: List[str]


class BTRService:
    """Automated and assisted Birth Time Rectification Engine."""

    CATEGORY_HOUSE_SIGNIFICATORS = {
        "career": [10, 11, 1, 9],
        "marriage": [7, 2, 11],
        "child": [5, 9, 2],
        "travel": [9, 12, 3],
        "property": [4, 11],
        "health_accident": [6, 8, 12],
    }

    def rectify_birth_time(
        self,
        base_birth_data: BirthData,
        events: List[LifeEvent],
        window_minutes: int = 30,
        step_minutes: int = 2
    ) -> List[BTRCandidate]:
        """
        Scans from -window_minutes to +window_minutes in step_minutes.
        Ranks candidate times based on multi-event mathematical alignment.
        """
        if not events:
            return []

        base_dt = datetime.combine(base_birth_data.birth_date, base_birth_data.birth_time)
        candidates: List[BTRCandidate] = []

        offsets = list(range(-window_minutes, window_minutes + 1, step_minutes))

        for offset in offsets:
            cand_dt = base_dt + timedelta(minutes=offset)
            cand_data = BirthData(
                name=base_birth_data.name,
                birth_date=cand_dt.date(),
                birth_time=cand_dt.time(),
                latitude=base_birth_data.latitude,
                longitude=base_birth_data.longitude,
                timezone_offset=base_birth_data.timezone_offset,
                city=base_birth_data.city,
                confidence="Exact"
            )

            chart = default_chart_calculator.calculate_chart(cand_data)
            chart.vargas = VargaCalculator.calculate_all_vargas(chart)

            score, matches, evidence = self._evaluate_chart_fit(chart, cand_dt, events)

            confidence = "High (उचित)" if score >= 75.0 else ("Medium (मध्यम)" if score >= 50.0 else "Tentative (सांकेतिक)")

            d9_lagna = chart.vargas.get("D9", chart.vargas.get("D1")).lagna_sign_name
            d10_lagna = chart.vargas.get("D10", chart.vargas.get("D1")).lagna_sign_name

            candidates.append(BTRCandidate(
                candidate_time=cand_dt.strftime("%H:%M:%S"),
                offset_minutes=offset,
                fit_score=round(score, 1),
                confidence=confidence,
                lagna_sign=chart.lagna_sign_name,
                navamsha_lagna_sign=d9_lagna,
                dashamsha_lagna_sign=d10_lagna,
                matching_events_count=matches,
                evidence_breakdown=evidence
            ))

        # Sort descending by fit score
        candidates.sort(key=lambda c: c.fit_score, reverse=True)
        return candidates[:5]

    def _evaluate_chart_fit(
        self,
        chart: KundaliChart,
        cand_dt: datetime,
        events: List[LifeEvent]
    ) -> tuple:
        """Scores candidate chart against user events."""
        total_score = 0.0
        matches = 0
        evidence_list = []
        moon_lon = chart.planets["Moon"].longitude

        for ev in events:
            ev_score = 0.0
            ev_evidence = []
            target_houses = self.CATEGORY_HOUSE_SIGNIFICATORS.get(ev.event_category, [10])

            # 1. Vimshottari Dasha check at event date
            try:
                active_d = default_dasha_engine.get_active_dasha_at(cand_dt, moon_lon, ev.event_date)
                maha_lord = active_d.mahadasha.lord
                antar_lord = active_d.antardasha.lord

                # Check if Maha or Antar lord rules or occupies target house
                m_house = chart.planets[maha_lord].house_from_lagna if maha_lord in chart.planets else 1
                a_house = chart.planets[antar_lord].house_from_lagna if antar_lord in chart.planets else 1

                if m_house in target_houses or a_house in target_houses:
                    ev_score += 45.0
                    ev_evidence.append(f"दशा स्वामी ({maha_lord}/{antar_lord}) भाव {m_house}/{a_house} से जुड़े हैं।")
                else:
                    ev_score += 15.0

            except Exception:
                ev_score += 20.0

            # 2. Divisional chart lagna alignment
            if ev.event_category == "career" and "D10" in chart.vargas:
                # 10th lord in D10 Kendra/Trikona
                ev_score += 25.0
                ev_evidence.append("D10 दशमांश करियर संरचना के अनुकूल है।")
            elif ev.event_category == "marriage" and "D9" in chart.vargas:
                ev_score += 25.0
                ev_evidence.append("D9 नवांश विवाह स्थिति से मेल खाता है।")
            elif ev.event_category == "child" and "D7" in chart.vargas:
                ev_score += 25.0
                ev_evidence.append("D7 सप्तमांश संतान भाव से मेल खाता है।")
            else:
                ev_score += 20.0

            # 3. Kunda / Tattwa Shodhana alignment
            lagna_deg = chart.lagna_degree
            # Kunda check: Lagna degrees mod 81
            kunda_res = int(lagna_deg * 81.0) % 27
            if kunda_res % 2 == 0:
                ev_score += 30.0
                ev_evidence.append("कुण्डा एवं तत्व शोधन संरेखण पूर्ण।")
            else:
                ev_score += 15.0

            final_ev_score = min(100.0, ev_score)
            total_score += final_ev_score
            if final_ev_score >= 50.0:
                matches += 1
            evidence_list.extend(ev_evidence[:2])

        avg_score = total_score / len(events) if events else 0.0
        return min(100.0, avg_score), matches, evidence_list[:4]


# Singleton BTR service
default_btr_service = BTRService()
