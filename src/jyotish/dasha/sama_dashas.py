"""
Dwig-Saptati Sama Dasha (72-year) & Shattrimsa Sama Dasha (36-year) Engines for JyotishOS.
Both are nakshatra-based conditional dashas from Brihat Parashara Hora Shastra.

- Dwisaptati Sama: 72-year cycle, 8 planets (Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn, Rahu)
  Conditional: Applicable when Lagna lord and 7th lord are in a Kendra from each other.
- Shattrimsa Sama: 36-year cycle, 6 planets (Sun, Moon, Mars, Mercury, Jupiter, Venus)
  Conditional: Male born at night, or Female born during day.

Reference: BPHS Ch. 46 & 47.
"""

from datetime import datetime, date, timedelta
from typing import List, Dict, Tuple, Any
from ..core.models import KundaliChart
from ..core.constants import SIGN_NAMES

# ============================
# DWISAPTATI SAMA DASHA (72 yr)
# ============================
DWISAPTATI_LORDS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu"]
DWISAPTATI_YEARS: Dict[str, float] = {
    "Sun": 9.0, "Moon": 9.0, "Mars": 9.0, "Mercury": 9.0,
    "Jupiter": 9.0, "Venus": 9.0, "Saturn": 9.0, "Rahu": 9.0,
}
TOTAL_DWISAPTATI_YEARS = 72.0

# Nakshatra lord mapping for Dwisaptati (cycle repeats every 8 nakshatras = 3 cycles for 27)
DWISAPTATI_NAK_LORD = [
    "Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu",
    "Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu",
    "Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu",
    "Sun", "Moon", "Mars"
]


class DwisaptatiDashaEngine:
    """72-year Dwisaptati Sama Dasha — 8 equal periods of 9 years each."""

    def __init__(self, year_type: str = "solar"):
        self.year_days = 360.0 if year_type.lower() == "savana" else 365.2425

    def calculate_birth_balance(self, moon_lon: float) -> Tuple[str, float]:
        span = 360.0 / 27.0
        nak_idx = int((moon_lon % 360.0) // span) % 27
        rem_deg = (moon_lon % 360.0) % span
        frac_remaining = 1.0 - (rem_deg / span)
        start_lord = DWISAPTATI_NAK_LORD[nak_idx]
        return start_lord, DWISAPTATI_YEARS[start_lord] * frac_remaining

    def generate_timeline(self, chart: KundaliChart) -> List[Dict[str, Any]]:
        birth_dt = datetime.combine(chart.birth_data.birth_date, chart.birth_data.birth_time)
        moon_lon = chart.planets["Moon"].longitude
        start_lord, rem_years = self.calculate_birth_balance(moon_lon)
        start_idx = DWISAPTATI_LORDS.index(start_lord)

        mahadashas = []
        current_dt = birth_dt

        mahadashas.append({
            "lord": start_lord, "start_date": current_dt,
            "end_date": current_dt + timedelta(days=rem_years * self.year_days),
            "duration_years": round(rem_years, 4), "is_partial": True,
            "total_lord_years": DWISAPTATI_YEARS[start_lord],
        })
        current_dt = mahadashas[0]["end_date"]

        for i in range(1, 16):
            lord = DWISAPTATI_LORDS[(start_idx + i) % 8]
            years = DWISAPTATI_YEARS[lord]
            end_dt = current_dt + timedelta(days=years * self.year_days)
            mahadashas.append({
                "lord": lord, "start_date": current_dt, "end_date": end_dt,
                "duration_years": years, "is_partial": False,
                "total_lord_years": years,
            })
            current_dt = end_dt

        return mahadashas

    def generate_antardashas(self, maha_lord: str, maha_start_dt: datetime,
                              maha_end_dt: datetime, is_partial: bool = False) -> List[Dict[str, Any]]:
        maha_idx = DWISAPTATI_LORDS.index(maha_lord)
        maha_total_years = DWISAPTATI_YEARS[maha_lord]
        nominal_start = maha_start_dt
        if is_partial:
            actual_years = (maha_end_dt - maha_start_dt).total_seconds() / 86400.0 / self.year_days
            elapsed_years = maha_total_years - actual_years
            nominal_start = maha_start_dt - timedelta(days=elapsed_years * self.year_days)

        antardashas = []
        curr_dt = nominal_start
        for i in range(8):
            antar_lord = DWISAPTATI_LORDS[(maha_idx + i) % 8]
            antar_years = (maha_total_years * DWISAPTATI_YEARS[antar_lord]) / TOTAL_DWISAPTATI_YEARS
            dur_days = antar_years * self.year_days
            next_dt = curr_dt + timedelta(days=dur_days)
            if next_dt > maha_start_dt and curr_dt < maha_end_dt:
                antardashas.append({
                    "lord": antar_lord,
                    "start_date": max(curr_dt, maha_start_dt),
                    "end_date": min(next_dt, maha_end_dt),
                    "duration_years": round(antar_years, 4),
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
            active_maha["lord"], active_maha["start_date"],
            active_maha["end_date"], active_maha.get("is_partial", False)
        )
        active_antar = antardashas[0] if antardashas else {"lord": active_maha["lord"], "start_date": active_maha["start_date"], "end_date": active_maha["end_date"]}
        for a in antardashas:
            if a["start_date"] <= target_dt <= a["end_date"]:
                active_antar = a
                break
        return {
            "mahadasha": active_maha, "antardasha": active_antar,
            "all_antardashas": antardashas,
            "summary": f"{active_maha['lord']} / {active_antar['lord']}",
        }


# ============================
# SHATTRIMSA SAMA DASHA (36 yr)
# ============================
SHATTRIMSA_LORDS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus"]
SHATTRIMSA_YEARS: Dict[str, float] = {
    "Sun": 6.0, "Moon": 6.0, "Mars": 6.0,
    "Mercury": 6.0, "Jupiter": 6.0, "Venus": 6.0,
}
TOTAL_SHATTRIMSA_YEARS = 36.0

SHATTRIMSA_NAK_LORD = [
    "Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus",
    "Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus",
    "Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus",
    "Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus",
    "Sun", "Moon", "Mars"
]


class ShattrimpaDashaEngine:
    """36-year Shattrimsa Sama Dasha — 6 equal periods of 6 years each."""

    def __init__(self, year_type: str = "solar"):
        self.year_days = 360.0 if year_type.lower() == "savana" else 365.2425

    def calculate_birth_balance(self, moon_lon: float) -> Tuple[str, float]:
        span = 360.0 / 27.0
        nak_idx = int((moon_lon % 360.0) // span) % 27
        rem_deg = (moon_lon % 360.0) % span
        frac_remaining = 1.0 - (rem_deg / span)
        start_lord = SHATTRIMSA_NAK_LORD[nak_idx]
        return start_lord, SHATTRIMSA_YEARS[start_lord] * frac_remaining

    def generate_timeline(self, chart: KundaliChart) -> List[Dict[str, Any]]:
        birth_dt = datetime.combine(chart.birth_data.birth_date, chart.birth_data.birth_time)
        moon_lon = chart.planets["Moon"].longitude
        start_lord, rem_years = self.calculate_birth_balance(moon_lon)
        start_idx = SHATTRIMSA_LORDS.index(start_lord)

        mahadashas = []
        current_dt = birth_dt
        mahadashas.append({
            "lord": start_lord, "start_date": current_dt,
            "end_date": current_dt + timedelta(days=rem_years * self.year_days),
            "duration_years": round(rem_years, 4), "is_partial": True,
            "total_lord_years": SHATTRIMSA_YEARS[start_lord],
        })
        current_dt = mahadashas[0]["end_date"]

        for i in range(1, 12):
            lord = SHATTRIMSA_LORDS[(start_idx + i) % 6]
            years = SHATTRIMSA_YEARS[lord]
            end_dt = current_dt + timedelta(days=years * self.year_days)
            mahadashas.append({
                "lord": lord, "start_date": current_dt, "end_date": end_dt,
                "duration_years": years, "is_partial": False, "total_lord_years": years,
            })
            current_dt = end_dt

        return mahadashas

    def generate_antardashas(self, maha_lord: str, maha_start_dt: datetime,
                              maha_end_dt: datetime, is_partial: bool = False) -> List[Dict[str, Any]]:
        maha_idx = SHATTRIMSA_LORDS.index(maha_lord)
        maha_total_years = SHATTRIMSA_YEARS[maha_lord]
        nominal_start = maha_start_dt
        if is_partial:
            actual_years = (maha_end_dt - maha_start_dt).total_seconds() / 86400.0 / self.year_days
            elapsed_years = maha_total_years - actual_years
            nominal_start = maha_start_dt - timedelta(days=elapsed_years * self.year_days)

        antardashas = []
        curr_dt = nominal_start
        for i in range(6):
            antar_lord = SHATTRIMSA_LORDS[(maha_idx + i) % 6]
            antar_years = (maha_total_years * SHATTRIMSA_YEARS[antar_lord]) / TOTAL_SHATTRIMSA_YEARS
            dur_days = antar_years * self.year_days
            next_dt = curr_dt + timedelta(days=dur_days)
            if next_dt > maha_start_dt and curr_dt < maha_end_dt:
                antardashas.append({
                    "lord": antar_lord,
                    "start_date": max(curr_dt, maha_start_dt),
                    "end_date": min(next_dt, maha_end_dt),
                    "duration_years": round(antar_years, 4),
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
            active_maha["lord"], active_maha["start_date"],
            active_maha["end_date"], active_maha.get("is_partial", False)
        )
        active_antar = antardashas[0] if antardashas else {"lord": active_maha["lord"], "start_date": active_maha["start_date"], "end_date": active_maha["end_date"]}
        for a in antardashas:
            if a["start_date"] <= target_dt <= a["end_date"]:
                active_antar = a
                break
        return {
            "mahadasha": active_maha, "antardasha": active_antar,
            "all_antardashas": antardashas,
            "summary": f"{active_maha['lord']} / {active_antar['lord']}",
        }


# Singletons
default_dwisaptati_engine = DwisaptatiDashaEngine(year_type="solar")
default_shattrimsa_engine = ShattrimpaDashaEngine(year_type="solar")

