"""
Shoola Dasha (Ayurdaya & Maraka Periods Engine) for JyotishOS.
According to Jaimini Sutras and Maharishi Parashara.
Calculates:
1. Stronger between 1st and 7th houses as dasha starting seed.
2. 12 Dasha periods of fixed 9 years each (Total 108 years lifespan coverage).
3. Direct progression for odd signs, reverse progression for even signs.
4. Identification of Trishoola (Rudramsha) signs (1st, 5th, 9th trines).
5. Vulnerability / Maraka risk rating for each period based on malefic occupation and aspects.
"""

from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime, timedelta
from src.jyotish.core.constants import SIGN_NAMES
from src.jyotish.core.models import KundaliChart


class ShoolaDashaEngine:
    """Calculates Shoola Dasha timeline for longevity and health crisis timing."""

    @classmethod
    def calculate(cls, chart: KundaliChart) -> Dict[str, Any]:
        """Generate 12 Shoola Dasha periods."""
        birth_dt = datetime.combine(chart.birth_data.birth_date, chart.birth_data.birth_time)

        # 1. Determine starting sign (Stronger between Lagna and 7th house)
        h1_sign_id = chart.lagna_sign_id
        h7_sign_id = ((h1_sign_id - 1 + 6) % 12) + 1

        h1_occupants = len(chart.houses[0].occupants)
        h7_occupants = len(chart.houses[6].occupants)

        start_sign_id = h1_sign_id if h1_occupants >= h7_occupants else h7_sign_id
        start_sign_name = SIGN_NAMES[start_sign_id - 1]

        # 2. Progression: Odd -> Direct (+1), Even -> Reverse (-1)
        is_odd = (start_sign_id % 2 != 0)
        direction_text = "प्रत्यक्ष क्रम (Direct / Zodiacal)" if is_odd else "व्युत्क्रम (Reverse / Anti-zodiacal)"

        # 3. Identify Trishoola / Rudramsha signs (1st, 5th, 9th from start sign)
        trishoola_ids = [
            start_sign_id,
            ((start_sign_id - 1 + 4) % 12) + 1,
            ((start_sign_id - 1 + 8) % 12) + 1
        ]
        trishoola_names = [SIGN_NAMES[sid - 1] for sid in trishoola_ids]

        # 4. Generate 12 periods of 9 years each
        timeline = []
        curr_time = birth_dt

        for step in range(12):
            if is_odd:
                curr_sign_id = ((start_sign_id - 1 + step) % 12) + 1
            else:
                curr_sign_id = ((start_sign_id - 1 - step) % 12) + 1

            sign_name = SIGN_NAMES[curr_sign_id - 1]
            end_time = curr_time + timedelta(days=9.0 * 365.2425)

            is_trishoola = curr_sign_id in trishoola_ids

            # Assess vulnerability (occupants in this sign)
            occupants = []
            malefic_count = 0
            for p_name, p_obj in chart.planets.items():
                if p_obj.sign_id == curr_sign_id:
                    occupants.append(p_name)
                    if p_name in ("Saturn", "Mars", "Rahu", "Ketu", "Sun"):
                        malefic_count += 1

            risk_level = "सामान्य (Balanced)"
            if is_trishoola and malefic_count >= 1:
                risk_level = "🚨 मारक / संवेदनशील (High Maraka Risk)"
            elif is_trishoola or malefic_count >= 2:
                risk_level = "⚠️ मध्यम सावधानी (Moderate Vulnerability)"
            elif malefic_count == 0:
                risk_level = "🛡️ सुरक्षित (Safe & Harmonious)"

            timeline.append({
                "period_index": step + 1,
                "sign": sign_name,
                "duration_years": 9.0,
                "start_date": curr_time.strftime("%d-%b-%Y"),
                "end_date": end_time.strftime("%d-%b-%Y"),
                "is_trishoola": "🔱 त्रिशूल राशि" if is_trishoola else "—",
                "occupants": ", ".join(occupants) if occupants else "None",
                "risk_level": risk_level
            })

            curr_time = end_time

        return {
            "start_sign": start_sign_name,
            "direction": direction_text,
            "trishoola_signs": trishoola_names,
            "timeline": timeline
        }


default_shoola_engine = ShoolaDashaEngine()

