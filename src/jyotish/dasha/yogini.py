"""
Yogini Dasha Calculation Engine for JyotishOS.
Implements the classical 36-year Chandra-based Yogini Dasha cycle:
Mangala (1), Pingala (2), Dhanya (3), Bhramari (4), Bhadrika (5), Ulka (6), Siddha (7), Sankata (8).
"""

from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Tuple, Optional


YOGINI_SEQUENCE = [
    {"name": "Mangala", "lord": "Moon", "years": 1},
    {"name": "Pingala", "lord": "Sun", "years": 2},
    {"name": "Dhanya", "lord": "Jupiter", "years": 3},
    {"name": "Bhramari", "lord": "Mars", "years": 4},
    {"name": "Bhadrika", "lord": "Mercury", "years": 5},
    {"name": "Ulka", "lord": "Saturn", "years": 6},
    {"name": "Siddha", "lord": "Venus", "years": 7},
    {"name": "Sankata", "lord": "Rahu", "years": 8},
]

TOTAL_YOGINI_CYCLE_YEARS = 36.0


class YoginiDashaEngine:
    """Calculates 36-year classical Yogini Dasha sequence and point-in-time lookups."""

    @classmethod
    def calculate_starting_yogini(cls, moon_longitude: float) -> Tuple[int, float]:
        """
        Calculates starting Yogini index (0-7) and balance of starting period at birth.
        Nakshatra index N = 1 to 27. Starting Yogini = ((N + 3) % 8) (1-based index).
        """
        nak_span = 360.0 / 27.0
        nak_idx = int(moon_longitude // nak_span)  # 0 to 26
        nak_num = nak_idx + 1  # 1 to 27
        rem_deg = moon_longitude % nak_span
        frac_passed = rem_deg / nak_span
        frac_remaining = 1.0 - frac_passed

        # Classical Yogini formula: (Nakshatra + 3) / 8 remainder
        yogini_idx = (nak_num + 3 - 1) % 8  # 0 to 7

        full_duration_years = YOGINI_SEQUENCE[yogini_idx]["years"]
        balance_years = full_duration_years * frac_remaining
        return yogini_idx, balance_years

    @classmethod
    def generate_timeline(
        cls,
        birth_datetime_or_chart: Any,
        moon_longitude: Optional[float] = None,
        target_years: float = 100.0
    ) -> List[Dict[str, Any]]:
        """Generates consecutive Yogini periods from birth up to target_years."""
        if hasattr(birth_datetime_or_chart, "birth_data"):
            b_dt = datetime.combine(birth_datetime_or_chart.birth_data.birth_date, birth_datetime_or_chart.birth_data.birth_time)
            m_lon = birth_datetime_or_chart.planets["Moon"].longitude
        else:
            b_dt = birth_datetime_or_chart
            m_lon = moon_longitude if moon_longitude is not None else 0.0

        start_idx, balance_years = cls.calculate_starting_yogini(m_lon)
        timeline: List[Dict[str, Any]] = []

        curr_time = b_dt
        # First partial period
        first_duration = balance_years
        first_end = curr_time + timedelta(days=first_duration * 365.25)
        timeline.append({
            "yogini": YOGINI_SEQUENCE[start_idx]["name"],
            "yogini_name": YOGINI_SEQUENCE[start_idx]["name"],
            "lord": YOGINI_SEQUENCE[start_idx]["lord"],
            "start_date": curr_time,
            "end_date": first_end,
            "duration_years": round(first_duration, 2),
            "is_partial": True
        })
        curr_time = first_end

        # Loop subsequent periods
        idx = (start_idx + 1) % 8
        total_elapsed = first_duration

        while total_elapsed < target_years:
            dur = YOGINI_SEQUENCE[idx]["years"]
            end_time = curr_time + timedelta(days=dur * 365.25)
            timeline.append({
                "yogini": YOGINI_SEQUENCE[idx]["name"],
                "yogini_name": YOGINI_SEQUENCE[idx]["name"],
                "lord": YOGINI_SEQUENCE[idx]["lord"],
                "start_date": curr_time,
                "end_date": end_time,
                "duration_years": dur,
                "is_partial": False
            })
            curr_time = end_time
            total_elapsed += dur
            idx = (idx + 1) % 8

        return timeline

    @classmethod
    def generate_antardashas(
        cls,
        major_yogini: str,
        start_dt: datetime,
        end_dt: datetime
    ) -> List[Dict[str, Any]]:
        """
        Generates 8 Antardashas within a Yogini Dasha.
        Sub-periods start from the major Yogini.
        Duration = (Major_duration * Sub_years) / 36.
        """
        names = [y["name"] for y in YOGINI_SEQUENCE]
        start_idx = names.index(major_yogini) if major_yogini in names else 0
        total_duration_sec = (end_dt - start_dt).total_seconds()

        antardashas = []
        curr_dt = start_dt
        for i in range(8):
            idx = (start_idx + i) % 8
            sub_y = YOGINI_SEQUENCE[idx]
            sub_frac = sub_y["years"] / TOTAL_YOGINI_CYCLE_YEARS
            sub_sec = total_duration_sec * sub_frac
            next_dt = curr_dt + timedelta(seconds=sub_sec)
            antardashas.append({
                "yogini": sub_y["name"],
                "yogini_name": sub_y["name"],
                "lord": sub_y["lord"],
                "start_date": curr_dt,
                "end_date": next_dt,
                "duration_days": round(sub_sec / 86400.0, 2),
                "duration_months": round(sub_sec / (86400.0 * 30.4375), 1),
            })
            curr_dt = next_dt

        return antardashas

    @classmethod
    def generate_pratyantardashas(
        cls,
        major_yogini: str,
        antar_yogini: str,
        start_dt: datetime,
        end_dt: datetime
    ) -> List[Dict[str, Any]]:
        """
        Generates 8 Pratyantardashas within a Yogini Antardasha.
        Duration = (Antar_duration * Sub_years) / 36.
        """
        names = [y["name"] for y in YOGINI_SEQUENCE]
        start_idx = names.index(antar_yogini) if antar_yogini in names else 0
        total_duration_sec = (end_dt - start_dt).total_seconds()

        pratyantars = []
        curr_dt = start_dt
        for i in range(8):
            idx = (start_idx + i) % 8
            sub_y = YOGINI_SEQUENCE[idx]
            sub_frac = sub_y["years"] / TOTAL_YOGINI_CYCLE_YEARS
            sub_sec = total_duration_sec * sub_frac
            next_dt = curr_dt + timedelta(seconds=sub_sec)
            pratyantars.append({
                "yogini": sub_y["name"],
                "yogini_name": sub_y["name"],
                "lord": sub_y["lord"],
                "start_date": curr_dt,
                "end_date": next_dt,
                "duration_days": round(sub_sec / 86400.0, 2),
            })
            curr_dt = next_dt

        return pratyantars

    @classmethod
    def get_active_yogini_at(
        cls,
        birth_datetime: datetime,
        moon_longitude: float,
        target_date: date
    ) -> Dict[str, Any]:
        """Returns the active Yogini period at target_date."""
        timeline = cls.generate_timeline(birth_datetime, moon_longitude)
        target_dt = datetime.combine(target_date, datetime.min.time())

        for p in timeline:
            if p["start_date"] <= target_dt < p["end_date"]:
                return p

        return timeline[-1] if timeline else {
            "yogini": "Siddha", "lord": "Venus",
            "start_date": birth_datetime, "end_date": birth_datetime,
            "duration_years": 7
        }


# Singleton Yogini engine
default_yogini_engine = YoginiDashaEngine()

