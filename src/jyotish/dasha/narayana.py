"""
Narayana Dasha Engine for JyotishOS.
Implements the classical Jaimini Narayana Dasha (Rashi/Sign-based timing system).
Reference: Jaimini Upadesha Sutras, PVNR Narasimha Rao's method.

Rules:
- Signs with odd lords (Aries, Gemini, Leo, Libra, Sagittarius, Aquarius) proceed forward (1→2→3...)
- Signs with even lords (Taurus, Cancer, Virgo, Scorpio, Capricorn, Pisces) proceed backward (12→11→10...)
- Duration of each sign's dasha = count of planets in that sign + aspects + special rules
- Standard duration: each sign gets between 1 and 12 years
"""

from datetime import datetime, date, timedelta
from typing import List, Dict, Tuple, Optional, Any
from ..core.models import KundaliChart
from ..core.constants import SIGN_NAMES

# Odd-lord signs (chara/moveable-natured for Narayana sequencing): Aries, Gemini, Leo, Libra, Sagittarius, Aquarius
# sign_id 1=Aries, 2=Taurus, ... 12=Pisces
ODD_SIGNS = {1, 3, 5, 7, 9, 11}   # Aries, Gemini, Leo, Libra, Sagittarius, Aquarius
EVEN_SIGNS = {2, 4, 6, 8, 10, 12}  # Taurus, Cancer, Virgo, Scorpio, Capricorn, Pisces


class NarayanaDashaEngine:
    """
    Calculates Jaimini Narayana Dasha (Rashi Dasha) with Maha and Antar levels.
    Works on D1 chart by default; can be applied to any divisional chart.
    """

    def __init__(self, year_type: str = "solar"):
        self.year_days = 360.0 if year_type.lower() == "savana" else 365.2425

    def _get_sign_duration(self, sign_id: int, chart: KundaliChart) -> int:
        """
        Calculates dasha duration for a sign based on PVNR method.
        Base = number of planets occupying that sign.
        Then add: if sign lord is in own sign or exalted → +1; if in enemy sign → -1 (min 1).
        Duration is always 1-12 years.
        """
        from ..core.constants import SIGN_LORDS, EXALTATION, DEBILITATION

        # Count planets in this sign
        planet_count = 0
        for p_name, p_pos in chart.planets.items():
            if p_name in ["Rahu", "Ketu"]:
                continue  # Nodes not counted in standard Narayana
            if p_pos.sign_id == sign_id:
                planet_count += 1

        # Get sign lord and its position
        sign_name = SIGN_NAMES[sign_id - 1]
        lord_name = SIGN_LORDS.get(sign_name, "")
        base_years = 1

        if lord_name and lord_name in chart.planets:
            lord_pos = chart.planets[lord_name]
            lord_sign = lord_pos.sign_name
            exalt_sign = EXALTATION.get(lord_name, "")
            debil_sign = DEBILITATION.get(lord_name, "")

            if lord_sign == sign_name or lord_sign == exalt_sign:
                # Own or exalted: planets_in_sign + 1 (minimum 1)
                base_years = max(1, planet_count + 1)
            elif lord_sign == debil_sign:
                # Debilitated: planets_in_sign - 1 (minimum 1)
                base_years = max(1, planet_count - 1)
            else:
                base_years = max(1, planet_count)
        else:
            base_years = max(1, planet_count)

        # Cap at 12
        return min(12, base_years) if base_years > 0 else 1

    def _get_dasha_sequence(self, chart: KundaliChart) -> List[int]:
        """
        Returns the ordered list of sign_ids for Narayana Dasha sequence.
        Starts from Lagna sign.
        - If Lagna is in ODD sign → proceed forward: lagna, lagna+1, ..., lagna+11
        - If Lagna is in EVEN sign → proceed backward: lagna, lagna-1, ..., lagna-11
        """
        lagna_sign = chart.lagna_sign_id  # 1-12

        sequence = []
        if lagna_sign in ODD_SIGNS:
            for i in range(12):
                s = ((lagna_sign - 1 + i) % 12) + 1
                sequence.append(s)
        else:
            for i in range(12):
                s = ((lagna_sign - 1 - i) % 12) + 1
                sequence.append(s)

        return sequence

    def generate_timeline(self, chart: KundaliChart) -> List[Dict[str, Any]]:
        """Generates 12 Narayana Mahadashas (one per sign) starting from birth."""
        birth_dt = datetime.combine(chart.birth_data.birth_date, chart.birth_data.birth_time)
        sequence = self._get_dasha_sequence(chart)

        mahadashas = []
        current_dt = birth_dt

        for sign_id in sequence:
            sign_name = SIGN_NAMES[sign_id - 1]
            years = self._get_sign_duration(sign_id, chart)
            dur_days = years * self.year_days
            end_dt = current_dt + timedelta(days=dur_days)

            mahadashas.append({
                "sign_id": sign_id,
                "sign_name": sign_name,
                "lord": _get_sign_lord(sign_name),
                "start_date": current_dt,
                "end_date": end_dt,
                "duration_years": years,
                "is_partial": False,
            })
            current_dt = end_dt

        return mahadashas

    def generate_antardashas(self, maha_sign_id: int, maha_start_dt: datetime,
                              maha_end_dt: datetime, chart: KundaliChart) -> List[Dict[str, Any]]:
        """
        Generates 12 Antardashas within a Narayana Mahadasha.
        Antardasha sequence: if maha_sign is odd → forward from maha_sign; if even → backward.
        Duration proportional to antardasha sign's own Narayana period.
        """
        maha_dur_days = (maha_end_dt - maha_start_dt).total_seconds() / 86400.0
        total_sub_years = sum(self._get_sign_duration(s, chart) for s in range(1, 13))

        if maha_sign_id in ODD_SIGNS:
            sub_sequence = [((maha_sign_id - 1 + i) % 12) + 1 for i in range(12)]
        else:
            sub_sequence = [((maha_sign_id - 1 - i) % 12) + 1 for i in range(12)]

        antardashas = []
        curr_dt = maha_start_dt

        for sub_sign_id in sub_sequence:
            sub_sign_name = SIGN_NAMES[sub_sign_id - 1]
            sub_years = self._get_sign_duration(sub_sign_id, chart)
            sub_frac = sub_years / total_sub_years if total_sub_years > 0 else 1.0 / 12
            sub_dur_days = maha_dur_days * sub_frac
            next_dt = curr_dt + timedelta(days=sub_dur_days)

            antardashas.append({
                "sign_id": sub_sign_id,
                "sign_name": sub_sign_name,
                "lord": _get_sign_lord(sub_sign_name),
                "start_date": curr_dt,
                "end_date": next_dt,
                "duration_days": round(sub_dur_days, 2),
            })
            curr_dt = next_dt

        return antardashas

    def get_active_dasha_at(self, chart: KundaliChart, target_date: date) -> Dict[str, Any]:
        """Returns the active Narayana Maha + Antar at a given target date."""
        target_dt = datetime.combine(target_date, datetime.min.time())
        mahadashas = self.generate_timeline(chart)

        active_maha = mahadashas[0]
        for m in mahadashas:
            if m["start_date"] <= target_dt <= m["end_date"]:
                active_maha = m
                break

        antardashas = self.generate_antardashas(
            active_maha["sign_id"], active_maha["start_date"],
            active_maha["end_date"], chart
        )
        active_antar = antardashas[0] if antardashas else active_maha
        for a in antardashas:
            if a["start_date"] <= target_dt <= a["end_date"]:
                active_antar = a
                break

        return {
            "mahadasha": active_maha,
            "antardasha": active_antar,
            "all_antardashas": antardashas,
            "summary": f"{active_maha['sign_name']} / {active_antar['sign_name']}",
        }


def _get_sign_lord(sign_name: str) -> str:
    from ..core.constants import SIGN_LORDS
    return SIGN_LORDS.get(sign_name, "")


# Singleton
default_narayana_engine = NarayanaDashaEngine(year_type="solar")

