"""
Sthira Dasha & Drigdasha Engines for JyotishOS.
Both are Jaimini Rashi-based sign dashas from BPHS & Jaimini Sutras.

Sthira Dasha (Fixed Sign Dasha):
- Chara signs = 7 years; Sthira signs = 8 years; Dwiswabhava signs = 9 years
- Starts from Lagna sign, proceeds in zodiacal order

Drig Dasha (Sight-based Dasha):
- Based on signs that aspect the Lagna by Jaimini Rashi Drishti
- Duration same as Sthira rules
Reference: Jaimini Sutras, Santanam's commentary.
"""

from datetime import datetime, date, timedelta
from typing import List, Dict, Any
from ..core.models import KundaliChart
from ..core.constants import SIGN_NAMES

# Sign types: 1=Chara(moveable), 2=Sthira(fixed), 3=Dwiswabhava(dual)
SIGN_TYPE: Dict[int, str] = {
    1: "Chara", 2: "Sthira", 3: "Dwiswabhava",   # Aries, Taurus, Gemini
    4: "Chara", 5: "Sthira", 6: "Dwiswabhava",   # Cancer, Leo, Virgo
    7: "Chara", 8: "Sthira", 9: "Dwiswabhava",   # Libra, Scorpio, Sagittarius
    10: "Chara", 11: "Sthira", 12: "Dwiswabhava", # Capricorn, Aquarius, Pisces
}

STHIRA_DURATION: Dict[str, int] = {
    "Chara": 7, "Sthira": 8, "Dwiswabhava": 9
}

# Jaimini Rashi Drishti: Chara → Sthira (skip adjacent); Sthira → Chara (skip adjacent); Dwiswabhava → all Dwiswabhava
def get_rashi_drishti(sign_id: int) -> List[int]:
    """Returns list of signs that receive Jaimini Rashi Drishti from this sign."""
    s_type = SIGN_TYPE[sign_id]
    aspects = []
    if s_type == "Chara":
        # Aspects all fixed signs EXCEPT the adjacent one
        fixed_signs = [2, 5, 8, 11]
        adj_fixed = ((sign_id - 1 + 1) % 12) + 1  # Next sign
        if adj_fixed not in fixed_signs:
            adj_fixed = ((sign_id - 1 - 1) % 12) + 1  # Previous sign
        for s in fixed_signs:
            if s != adj_fixed:
                aspects.append(s)
    elif s_type == "Sthira":
        # Aspects all moveable signs EXCEPT the adjacent one
        chara_signs = [1, 4, 7, 10]
        adj_chara = ((sign_id - 1 + 1) % 12) + 1
        if adj_chara not in chara_signs:
            adj_chara = ((sign_id - 1 - 1) % 12) + 1
        for s in chara_signs:
            if s != adj_chara:
                aspects.append(s)
    else:  # Dwiswabhava
        # Aspects all dual signs except itself
        dual_signs = [3, 6, 9, 12]
        for s in dual_signs:
            if s != sign_id:
                aspects.append(s)
    return aspects


class SthiraDashaEngine:
    """
    Jaimini Sthira Dasha (Fixed/Constant Dasha).
    Chara signs = 7 yrs, Sthira = 8 yrs, Dwiswabhava = 9 yrs.
    Sequence: from Lagna sign in zodiacal order (forward always).
    """

    def __init__(self, year_type: str = "solar"):
        self.year_days = 360.0 if year_type.lower() == "savana" else 365.2425

    def generate_timeline(self, chart: KundaliChart) -> List[Dict[str, Any]]:
        birth_dt = datetime.combine(chart.birth_data.birth_date, chart.birth_data.birth_time)
        lagna_sign = chart.lagna_sign_id

        mahadashas = []
        current_dt = birth_dt

        for i in range(12):
            sign_id = ((lagna_sign - 1 + i) % 12) + 1
            sign_name = SIGN_NAMES[sign_id - 1]
            s_type = SIGN_TYPE[sign_id]
            years = STHIRA_DURATION[s_type]
            dur_days = years * self.year_days
            end_dt = current_dt + timedelta(days=dur_days)

            mahadashas.append({
                "sign_id": sign_id, "sign_name": sign_name,
                "type": s_type, "start_date": current_dt, "end_date": end_dt,
                "duration_years": years, "is_partial": False,
            })
            current_dt = end_dt

        return mahadashas

    def generate_antardashas(self, maha_sign_id: int, maha_start_dt: datetime,
                              maha_end_dt: datetime) -> List[Dict[str, Any]]:
        """Antardasha: same sequence as maha but sub-divided proportionally."""
        maha_dur_days = (maha_end_dt - maha_start_dt).total_seconds() / 86400.0
        total_years = sum(STHIRA_DURATION[SIGN_TYPE[s]] for s in range(1, 13))

        sub_sequence = [((maha_sign_id - 1 + i) % 12) + 1 for i in range(12)]
        antardashas = []
        curr_dt = maha_start_dt

        for sub_sign_id in sub_sequence:
            sub_years = STHIRA_DURATION[SIGN_TYPE[sub_sign_id]]
            sub_frac = sub_years / total_years
            sub_dur = maha_dur_days * sub_frac
            next_dt = curr_dt + timedelta(days=sub_dur)
            antardashas.append({
                "sign_id": sub_sign_id,
                "sign_name": SIGN_NAMES[sub_sign_id - 1],
                "start_date": curr_dt, "end_date": next_dt,
                "duration_days": round(sub_dur, 2),
            })
            curr_dt = next_dt

        return antardashas

    def get_active_dasha_at(self, chart: KundaliChart, target_date: date) -> Dict[str, Any]:
        target_dt = datetime.combine(target_date, datetime.min.time())
        mahadashas = self.generate_timeline(chart)
        active_maha = mahadashas[0]
        for m in mahadashas:
            if m["start_date"] <= target_dt <= m["end_date"]:
                active_maha = m
                break
        antardashas = self.generate_antardashas(
            active_maha["sign_id"], active_maha["start_date"], active_maha["end_date"]
        )
        active_antar = antardashas[0] if antardashas else active_maha
        for a in antardashas:
            if a["start_date"] <= target_dt <= a["end_date"]:
                active_antar = a
                break
        return {
            "mahadasha": active_maha, "antardasha": active_antar,
            "all_antardashas": antardashas,
            "summary": f"{active_maha['sign_name']} / {active_antar['sign_name']}",
        }


class DrigDashaEngine:
    """
    Jaimini Drig Dasha (Sight/Aspect-based Dasha).
    Sequence: signs that have Rashi Drishti on the Lagna in a specific order.
    Duration: same as Sthira rules (Chara=7, Sthira=8, Dwiswabhava=9).
    """

    def __init__(self, year_type: str = "solar"):
        self.year_days = 360.0 if year_type.lower() == "savana" else 365.2425

    def _get_drig_sequence(self, chart: KundaliChart) -> List[int]:
        """Signs that aspect Lagna by Jaimini Rashi Drishti, starting from Lagna."""
        lagna_sign = chart.lagna_sign_id
        # Start with Lagna, then add signs that aspect Lagna, in order from Lagna forward
        aspecting = get_rashi_drishti(lagna_sign)
        all_signs = list(range(1, 13))
        # Sort aspecting signs by zodiacal distance from Lagna
        aspecting_sorted = sorted(aspecting, key=lambda s: (s - lagna_sign) % 12)

        # Sequence: Lagna first, then aspecting signs, then remaining
        sequence = [lagna_sign]
        for s in aspecting_sorted:
            if s not in sequence:
                sequence.append(s)
        for s in range(1, 13):
            if s not in sequence:
                sequence.append(s)

        return sequence[:12]

    def generate_timeline(self, chart: KundaliChart) -> List[Dict[str, Any]]:
        birth_dt = datetime.combine(chart.birth_data.birth_date, chart.birth_data.birth_time)
        sequence = self._get_drig_sequence(chart)

        mahadashas = []
        current_dt = birth_dt
        for sign_id in sequence:
            sign_name = SIGN_NAMES[sign_id - 1]
            s_type = SIGN_TYPE[sign_id]
            years = STHIRA_DURATION[s_type]
            dur_days = years * self.year_days
            end_dt = current_dt + timedelta(days=dur_days)
            mahadashas.append({
                "sign_id": sign_id, "sign_name": sign_name,
                "type": s_type, "start_date": current_dt, "end_date": end_dt,
                "duration_years": years,
                "aspects_from": get_rashi_drishti(sign_id),
            })
            current_dt = end_dt

        return mahadashas

    def get_active_dasha_at(self, chart: KundaliChart, target_date: date) -> Dict[str, Any]:
        target_dt = datetime.combine(target_date, datetime.min.time())
        mahadashas = self.generate_timeline(chart)
        active_maha = mahadashas[0]
        for m in mahadashas:
            if m["start_date"] <= target_dt <= m["end_date"]:
                active_maha = m
                break
        return {"mahadasha": active_maha, "summary": active_maha["sign_name"]}


# Singletons
default_sthira_engine = SthiraDashaEngine(year_type="solar")
default_drigdasha_engine = DrigDashaEngine(year_type="solar")

