"""
Ashtottari Dasha Engine for JyotishOS.
Implements the classical 108-year Ashtottari cycle (8 planets: Sun, Moon, Mars, Mercury, Saturn, Jupiter, Rahu, Venus).
Nakshatra-based like Vimshottari. Applies when Rahu is NOT in a Kendra or Trikona from the Moon (conditional dasha).
Reference: BPHS Ch. 46.
"""

from datetime import datetime, date, timedelta
from typing import List, Dict, Tuple, Optional, Any
from ..core.models import KundaliChart

# Ashtottari lords in cyclic order
ASHTOTTARI_LORDS = ["Sun", "Moon", "Mars", "Mercury", "Saturn", "Jupiter", "Rahu", "Venus"]

# Ashtottari periods in years (total = 108)
ASHTOTTARI_YEARS: Dict[str, float] = {
    "Sun": 6.0,
    "Moon": 15.0,
    "Mars": 8.0,
    "Mercury": 17.0,
    "Saturn": 10.0,
    "Jupiter": 19.0,
    "Rahu": 12.0,
    "Venus": 21.0,
}
TOTAL_ASHTOTTARI_YEARS = 108.0

# Nakshatra-to-lord mapping for Ashtottari (Ashwini → Krittika → ..., cycle of 8 lords over 27 nakshatras)
# Each lord gets 3 nakshatras (27/9 = 3, but Ashtottari has 8 lords, so pattern is different)
# Classical mapping: Ashwini=Sun, Bharani=Moon, Krittika=Mars, Rohini=Mercury, Mrigashira=Saturn,
# Ardra=Jupiter, Punarvasu=Rahu, Pushya=Venus, Ashlesha=Sun, Magha=Moon, PurvaPhalguni=Mars,
# UttaraPhalguni=Mercury, Hasta=Saturn, Chitra=Jupiter, Swati=Rahu, Vishakha=Venus,
# Anuradha=Sun, Jyeshtha=Moon, Mula=Mars, PurvaAshadha=Mercury, UttaraAshadha=Saturn,
# Shravana=Jupiter, Dhanishtha=Rahu, Shatabhisha=Venus, PurvaBhadrapada=Sun,
# UttaraBhadrapada=Moon, Revati=Mars
ASHTOTTARI_NAK_LORD = [
    "Sun", "Moon", "Mars", "Mercury", "Saturn", "Jupiter", "Rahu", "Venus",   # 1-8
    "Sun", "Moon", "Mars", "Mercury", "Saturn", "Jupiter", "Rahu", "Venus",   # 9-16
    "Sun", "Moon", "Mars", "Mercury", "Saturn", "Jupiter", "Rahu", "Venus",   # 17-24
    "Sun", "Moon", "Mars"                                                       # 25-27
]


class AshtottariDashaEngine:
    """Calculates Ashtottari Dasha (108-year cycle) with Maha, Antar, and Pratyantardasha levels."""

    def __init__(self, year_type: str = "solar"):
        self.year_days = 360.0 if year_type.lower() == "savana" else 365.2425

    def calculate_birth_balance(self, moon_lon: float) -> Tuple[str, float]:
        """
        Returns the starting lord and remaining years at birth based on Moon's nakshatra.
        Each nakshatra = 13.333... degrees.
        """
        span = 360.0 / 27.0  # 13.3333 deg per nakshatra
        nak_idx = int((moon_lon % 360.0) // span) % 27
        rem_deg = (moon_lon % 360.0) % span
        frac_elapsed = rem_deg / span
        frac_remaining = 1.0 - frac_elapsed

        start_lord = ASHTOTTARI_NAK_LORD[nak_idx]
        total_years = ASHTOTTARI_YEARS[start_lord]
        remaining_years = total_years * frac_remaining
        return start_lord, remaining_years

    def generate_timeline(self, chart: KundaliChart) -> List[Dict[str, Any]]:
        """Generates Ashtottari Mahadasha timeline for the chart."""
        birth_dt = datetime.combine(chart.birth_data.birth_date, chart.birth_data.birth_time)
        moon_lon = chart.planets["Moon"].longitude
        start_lord, rem_years = self.calculate_birth_balance(moon_lon)
        start_idx = ASHTOTTARI_LORDS.index(start_lord)

        mahadashas = []
        current_dt = birth_dt

        # First (partial) Mahadasha
        first_dur_days = rem_years * self.year_days
        end_first_dt = current_dt + timedelta(days=first_dur_days)
        mahadashas.append({
            "lord": start_lord,
            "start_date": current_dt,
            "end_date": end_first_dt,
            "duration_years": round(rem_years, 4),
            "is_partial": True,
            "total_lord_years": ASHTOTTARI_YEARS[start_lord],
        })
        current_dt = end_first_dt

        # Subsequent full Mahadashas (cover ~108 years)
        for i in range(1, 16):
            lord_idx = (start_idx + i) % 8
            lord = ASHTOTTARI_LORDS[lord_idx]
            years = ASHTOTTARI_YEARS[lord]
            dur_days = years * self.year_days
            end_dt = current_dt + timedelta(days=dur_days)
            mahadashas.append({
                "lord": lord,
                "start_date": current_dt,
                "end_date": end_dt,
                "duration_years": years,
                "is_partial": False,
                "total_lord_years": years,
            })
            current_dt = end_dt

        return mahadashas

    def generate_antardashas(self, maha_lord: str, maha_start_dt: datetime,
                              maha_end_dt: datetime, is_partial: bool = False) -> List[Dict[str, Any]]:
        """Generates 8 Antardashas within a Mahadasha. Duration = (Maha_years × Antar_years) / 108."""
        maha_idx = ASHTOTTARI_LORDS.index(maha_lord)
        maha_total_years = ASHTOTTARI_YEARS[maha_lord]

        nominal_start = maha_start_dt
        if is_partial:
            actual_dur_days = (maha_end_dt - maha_start_dt).total_seconds() / 86400.0
            actual_years = actual_dur_days / self.year_days
            elapsed_years = maha_total_years - actual_years
            nominal_start = maha_start_dt - timedelta(days=elapsed_years * self.year_days)

        antardashas = []
        curr_dt = nominal_start
        for i in range(8):
            antar_idx = (maha_idx + i) % 8
            antar_lord = ASHTOTTARI_LORDS[antar_idx]
            antar_years = (maha_total_years * ASHTOTTARI_YEARS[antar_lord]) / TOTAL_ASHTOTTARI_YEARS
            dur_days = antar_years * self.year_days
            next_dt = curr_dt + timedelta(days=dur_days)

            if next_dt > maha_start_dt and curr_dt < maha_end_dt:
                eff_start = max(curr_dt, maha_start_dt)
                eff_end = min(next_dt, maha_end_dt)
                antardashas.append({
                    "lord": antar_lord,
                    "start_date": eff_start,
                    "end_date": eff_end,
                    "duration_years": round(antar_years, 4),
                })
            curr_dt = next_dt

        return antardashas

    def generate_pratyantardashas(self, maha_lord: str, antar_lord: str,
                                   antar_start_dt: datetime, antar_end_dt: datetime) -> List[Dict[str, Any]]:
        """Generates 8 Pratyantardashas within an Antardasha."""
        antar_idx = ASHTOTTARI_LORDS.index(antar_lord)
        antar_dur_days = (antar_end_dt - antar_start_dt).total_seconds() / 86400.0

        pratyantars = []
        curr_dt = antar_start_dt
        for i in range(8):
            prat_idx = (antar_idx + i) % 8
            prat_lord = ASHTOTTARI_LORDS[prat_idx]
            prat_frac = ASHTOTTARI_YEARS[prat_lord] / TOTAL_ASHTOTTARI_YEARS
            dur_days = antar_dur_days * prat_frac
            next_dt = curr_dt + timedelta(days=dur_days)
            pratyantars.append({
                "lord": prat_lord,
                "start_date": curr_dt,
                "end_date": next_dt,
                "duration_days": round(dur_days, 2),
            })
            curr_dt = next_dt

        return pratyantars

    def get_active_dasha_at(self, chart: KundaliChart, target_date: date) -> Dict[str, Any]:
        """Returns the active Maha/Antar/Pratyantar hierarchy at a given date."""
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

        pratyantars = self.generate_pratyantardashas(
            active_maha["lord"], active_antar["lord"],
            active_antar["start_date"], active_antar["end_date"]
        )
        active_prat = pratyantars[0] if pratyantars else {"lord": active_antar["lord"], "start_date": active_antar["start_date"], "end_date": active_antar["end_date"]}
        for p in pratyantars:
            if p["start_date"] <= target_dt <= p["end_date"]:
                active_prat = p
                break

        return {
            "mahadasha": active_maha,
            "antardasha": active_antar,
            "pratyantardasha": active_prat,
            "all_antardashas": antardashas,
            "all_pratyantardashas": pratyantars,
            "summary": f"{active_maha['lord']} / {active_antar['lord']} / {active_prat['lord']}",
        }


# Singleton
default_ashtottari_engine = AshtottariDashaEngine(year_type="solar")

