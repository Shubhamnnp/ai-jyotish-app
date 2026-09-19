"""
Jaimini Chara Dasha Engine for JyotishOS.
Implements sign-based rashi dasha sequence and duration calculation
according to Jaimini Upadesha Sutras.
"""

from datetime import datetime, date, timedelta
from typing import List, Dict, Any
from ..core.constants import SIGN_NAMES, SIGN_LORDS
from ..core.models import KundaliChart


class CharaDashaEngine:
    """Calculates Jaimini Chara Dasha periods and lookups."""

    DIRECT_SIGNS = [1, 2, 3, 7, 8, 9]  # Aries, Taurus, Gemini, Libra, Scorpio, Sagittarius

    @classmethod
    def calculate_sign_duration(cls, sign_id: int, chart: KundaliChart) -> int:
        """
        Calculates the duration in years (1 to 12) for a sign's Chara Dasha.
        Direct count: from sign to its lord - 1 (or 12 if in own sign).
        Indirect count: backward count - 1.
        """
        sign_name = SIGN_NAMES[sign_id - 1]
        lord_name = SIGN_LORDS[sign_name]
        lord_sign_id = chart.planets[lord_name].sign_id

        if lord_sign_id == sign_id:
            return 12

        is_direct = sign_id in cls.DIRECT_SIGNS

        if is_direct:
            distance = ((lord_sign_id - sign_id) % 12) + 1
        else:
            distance = ((sign_id - lord_sign_id) % 12) + 1

        duration = distance - 1
        return 12 if duration <= 0 else duration

    @classmethod
    def generate_timeline(cls, chart: KundaliChart) -> List[Dict[str, Any]]:
        """Generates consecutive Chara Dasha sequence for 12 signs."""
        lagna_sign_id = chart.lagna_sign_id
        is_direct = lagna_sign_id in cls.DIRECT_SIGNS

        # Order of 12 signs
        if is_direct:
            sign_sequence = [((lagna_sign_id - 1 + i) % 12) + 1 for i in range(12)]
        else:
            sign_sequence = [((lagna_sign_id - 1 - i) % 12) + 1 for i in range(12)]

        timeline: List[Dict[str, Any]] = []
        curr_time = datetime.combine(chart.birth_data.birth_date, chart.birth_data.birth_time)

        for s_id in sign_sequence:
            dur_years = cls.calculate_sign_duration(s_id, chart)
            end_time = curr_time + timedelta(days=dur_years * 365.25)
            s_name = SIGN_NAMES[s_id - 1]

            timeline.append({
                "sign_id": s_id,
                "sign_name": s_name,
                "start_date": curr_time,
                "end_date": end_time,
                "duration_years": dur_years,
            })
            curr_time = end_time

        return timeline

    @classmethod
    def get_active_chara_dasha_at(cls, chart: KundaliChart, target_date: date) -> Dict[str, Any]:
        """Returns the active Chara Dasha rashi at target_date."""
        timeline = cls.generate_timeline(chart)
        target_dt = datetime.combine(target_date, datetime.min.time())

        for period in timeline:
            if period["start_date"] <= target_dt < period["end_date"]:
                return period

        return timeline[-1] if timeline else {
            "sign_name": chart.lagna_sign_name,
            "duration_years": 7,
            "start_date": chart.birth_data.birth_date,
            "end_date": chart.birth_data.birth_date
        }


# Singleton Chara Dasha engine
default_chara_engine = CharaDashaEngine()

