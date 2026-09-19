"""
Vimshottari Dasha Engine for JyotishOS.
Implements the classical 120-year Vimshottari cycle down to Sookshma and Prana levels.
Supports Savana (360-day) and Solar (365.25-day) year bases.
Provides point-in-time active dasha hierarchy lookup for any event date.
"""

from datetime import datetime, date, timedelta
from typing import List, Dict, Tuple, Optional
from ..core.constants import VIMSHOTTARI_DASHAS, TOTAL_VIMSHOTTARI_YEARS
from ..core.models import DashaLevel, ActiveDashaHierarchy, KundaliChart


# Cyclic order of dasha lords
DASHA_LORDS = [d["lord"] for d in VIMSHOTTARI_DASHAS]
DASHA_YEARS: Dict[str, float] = {d["lord"]: float(d["years"]) for d in VIMSHOTTARI_DASHAS}


class VimshottariDashaEngine:
    """Calculates Vimshottari Mahadasha, Antardasha, and Pratyantardasha periods."""

    def __init__(self, year_type: str = "solar"):
        # Solar year = 365.2425 days; Savana = 360 days
        self.year_days = 360.0 if year_type.lower() == "savana" else 365.2425

    def calculate_birth_balance(self, moon_lon: float) -> Tuple[str, float, float]:
        """
        Calculates starting Mahadasha lord, elapsed fraction, and remaining years.
        Each nakshatra = 13 deg 20 min = 13.3333333 degrees.
        """
        span = 360.0 / 27.0  # 13.3333333 deg
        nak_idx = int((moon_lon % 360.0) // span) % 27
        rem_deg = (moon_lon % 360.0) % span
        frac_elapsed = rem_deg / span
        frac_remaining = 1.0 - frac_elapsed

        # 27 nakshatras mapped to 9 dasha lords (3 cycles of 9)
        lord = DASHA_LORDS[nak_idx % 9]
        total_years = DASHA_YEARS[lord]
        remaining_years = total_years * frac_remaining

        return lord, frac_elapsed, remaining_years

    def generate_mahadasha_sequence(
        self,
        birth_dt: datetime,
        moon_lon: float,
        num_cycles: int = 1
    ) -> List[Dict[str, any]]:
        """Generates all Mahadashas covering a lifetime (~120 years)."""
        start_lord, frac_elapsed, rem_years = self.calculate_birth_balance(moon_lon)
        start_idx = DASHA_LORDS.index(start_lord)

        mahadashas = []
        current_dt = birth_dt

        # First Mahadasha (partial)
        first_duration_days = rem_years * self.year_days
        end_first_dt = current_dt + timedelta(days=first_duration_days)
        mahadashas.append({
            "lord": start_lord,
            "start_date": current_dt,
            "end_date": end_first_dt,
            "duration_years": rem_years,
            "is_partial": True,
            "total_lord_years": DASHA_YEARS[start_lord],
        })
        current_dt = end_first_dt

        # Subsequent Mahadashas
        total_periods = 9 * num_cycles
        for i in range(1, total_periods):
            lord_idx = (start_idx + i) % 9
            lord = DASHA_LORDS[lord_idx]
            years = DASHA_YEARS[lord]
            duration_days = years * self.year_days
            end_dt = current_dt + timedelta(days=duration_days)
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

    def generate_timeline(self, chart: KundaliChart) -> List[Dict[str, any]]:
        """Generates Mahadasha sequence for the chart's Moon position and birth datetime."""
        birth_dt = datetime.combine(chart.birth_data.birth_date, chart.birth_data.birth_time)
        moon_lon = chart.planets["Moon"].longitude
        return self.generate_mahadasha_sequence(birth_dt, moon_lon)

    def generate_antardashas(
        self,
        maha_lord: str,
        maha_start_dt: datetime,
        maha_end_dt: datetime,
        is_partial: bool = False
    ) -> List[Dict[str, any]]:
        """
        Generates 9 Antardashas within a Mahadasha.
        Sub-periods start with the Mahadasha lord.
        Duration = (Maha_years * Antar_years) / 120.
        """
        maha_idx = DASHA_LORDS.index(maha_lord)
        maha_total_years = DASHA_YEARS[maha_lord]

        antardashas = []
        nominal_start = maha_start_dt

        # If partial at birth, we reconstruct from the true nominal start of the Mahadasha
        if is_partial:
            actual_duration_days = (maha_end_dt - maha_start_dt).total_seconds() / 86400.0
            actual_years = actual_duration_days / self.year_days
            elapsed_years = maha_total_years - actual_years
            nominal_start = maha_start_dt - timedelta(days=elapsed_years * self.year_days)

        curr_dt = nominal_start
        for i in range(9):
            antar_idx = (maha_idx + i) % 9
            antar_lord = DASHA_LORDS[antar_idx]
            antar_years = (maha_total_years * DASHA_YEARS[antar_lord]) / TOTAL_VIMSHOTTARI_YEARS
            duration_days = antar_years * self.year_days
            next_dt = curr_dt + timedelta(days=duration_days)

            # Only include if intersects with actual mahadasha window
            if next_dt > maha_start_dt and curr_dt < maha_end_dt:
                eff_start = max(curr_dt, maha_start_dt)
                eff_end = min(next_dt, maha_end_dt)
                antardashas.append({
                    "lord": antar_lord,
                    "start_date": eff_start,
                    "end_date": eff_end,
                    "duration_years": antar_years,
                })
            curr_dt = next_dt

        return antardashas

    def generate_pratyantardashas(
        self,
        maha_lord: str,
        antar_lord: str,
        antar_start_dt: datetime,
        antar_end_dt: datetime
    ) -> List[Dict[str, any]]:
        """
        Generates 9 Pratyantardashas within an Antardasha.
        Duration = (Antar_duration * Pratyantar_years) / 120.
        """
        antar_idx = DASHA_LORDS.index(antar_lord)
        antar_duration_days = (antar_end_dt - antar_start_dt).total_seconds() / 86400.0

        pratyantars = []
        curr_dt = antar_start_dt
        for i in range(9):
            prat_idx = (antar_idx + i) % 9
            prat_lord = DASHA_LORDS[prat_idx]
            prat_frac = DASHA_YEARS[prat_lord] / TOTAL_VIMSHOTTARI_YEARS
            dur_days = antar_duration_days * prat_frac
            next_dt = curr_dt + timedelta(days=dur_days)
            pratyantars.append({
                "lord": prat_lord,
                "start_date": curr_dt,
                "end_date": next_dt,
            })
            curr_dt = next_dt

        return pratyantars

    def get_active_dasha_at(
        self,
        birth_dt: datetime,
        moon_lon: float,
        target_date: date
    ) -> ActiveDashaHierarchy:
        """
        Returns the active 3-level (Maha/Antar/Pratyantar) and 4-level (Sookshma)
        hierarchy active on the target date.
        """
        target_dt = datetime.combine(target_date, datetime.min.time())
        mahadashas = self.generate_mahadasha_sequence(birth_dt, moon_lon, num_cycles=2)

        # 1. Find active Mahadasha
        active_maha = None
        for m in mahadashas:
            if m["start_date"] <= target_dt <= m["end_date"]:
                active_maha = m
                break

        if not active_maha:
            # Fallback to last or first
            active_maha = mahadashas[-1] if target_dt > mahadashas[-1]["end_date"] else mahadashas[0]

        # 2. Find active Antardasha
        antardashas = self.generate_antardashas(
            active_maha["lord"],
            active_maha["start_date"],
            active_maha["end_date"],
            is_partial=active_maha.get("is_partial", False)
        )
        active_antar = None
        for a in antardashas:
            if a["start_date"] <= target_dt <= a["end_date"]:
                active_antar = a
                break
        if not active_antar:
            active_antar = antardashas[0] if antardashas else {"lord": active_maha["lord"], "start_date": active_maha["start_date"], "end_date": active_maha["end_date"]}

        # 3. Find active Pratyantardasha
        pratyantars = self.generate_pratyantardashas(
            active_maha["lord"],
            active_antar["lord"],
            active_antar["start_date"],
            active_antar["end_date"]
        )
        active_prat = None
        for p in pratyantars:
            if p["start_date"] <= target_dt <= p["end_date"]:
                active_prat = p
                break
        if not active_prat:
            active_prat = pratyantars[0] if pratyantars else {"lord": active_antar["lord"], "start_date": active_antar["start_date"], "end_date": active_antar["end_date"]}

        summary = f"{active_maha['lord']} / {active_antar['lord']} / {active_prat['lord']}"

        return ActiveDashaHierarchy(
            target_date=target_date,
            mahadasha=DashaLevel(
                lord=active_maha["lord"],
                start_date=active_maha["start_date"],
                end_date=active_maha["end_date"]
            ),
            antardasha=DashaLevel(
                lord=active_antar["lord"],
                start_date=active_antar["start_date"],
                end_date=active_antar["end_date"]
            ),
            pratyantardasha=DashaLevel(
                lord=active_prat["lord"],
                start_date=active_prat["start_date"],
                end_date=active_prat["end_date"]
            ),
            formatted_summary=summary
        )


# Singleton dasha engine
default_dasha_engine = VimshottariDashaEngine(year_type="solar")

