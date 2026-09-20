"""
Vimshottari Dasha Engine for JyotishOS.
Implements the classical 120-year Vimshottari cycle down to Sookshma and Prana levels.
Supports Savana (360-day) and Solar (365.25-day) year bases.
Provides point-in-time active dasha hierarchy lookup for any event date.
"""

from datetime import datetime, date, timedelta
from typing import List, Dict, Tuple, Optional, Any
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

    def generate_sookshmadashas(
        self,
        maha_lord: str,
        antar_lord: str,
        prat_lord: str,
        prat_start_dt: datetime,
        prat_end_dt: datetime
    ) -> List[Dict[str, Any]]:
        """
        Generates 9 Sookshmadashas within a Pratyantardasha (Level 4).
        Sequence starts with the Pratyantar lord.
        Duration = (Prat_duration * Sookshma_years) / 120.
        """
        prat_idx = DASHA_LORDS.index(prat_lord)
        prat_duration_sec = (prat_end_dt - prat_start_dt).total_seconds()

        sookshmas = []
        curr_dt = prat_start_dt
        for i in range(9):
            s_idx = (prat_idx + i) % 9
            s_lord = DASHA_LORDS[s_idx]
            s_frac = DASHA_YEARS[s_lord] / TOTAL_VIMSHOTTARI_YEARS
            s_dur_sec = prat_duration_sec * s_frac
            next_dt = curr_dt + timedelta(seconds=s_dur_sec)
            sookshmas.append({
                "lord": s_lord,
                "start_date": curr_dt,
                "end_date": next_dt,
                "duration_days": round(s_dur_sec / 86400.0, 2),
            })
            curr_dt = next_dt

        return sookshmas

    def generate_pranadashas(
        self,
        maha_lord: str,
        antar_lord: str,
        prat_lord: str,
        sookshma_lord: str,
        sookshma_start_dt: datetime,
        sookshma_end_dt: datetime
    ) -> List[Dict[str, Any]]:
        """
        Generates 9 Pranadashas within a Sookshmadasha (Level 5).
        Sequence starts with the Sookshma lord.
        Duration = (Sookshma_duration * Prana_years) / 120.
        """
        s_idx = DASHA_LORDS.index(sookshma_lord)
        sookshma_duration_sec = (sookshma_end_dt - sookshma_start_dt).total_seconds()

        pranas = []
        curr_dt = sookshma_start_dt
        for i in range(9):
            p_idx = (s_idx + i) % 9
            p_lord = DASHA_LORDS[p_idx]
            p_frac = DASHA_YEARS[p_lord] / TOTAL_VIMSHOTTARI_YEARS
            p_dur_sec = sookshma_duration_sec * p_frac
            next_dt = curr_dt + timedelta(seconds=p_dur_sec)
            pranas.append({
                "lord": p_lord,
                "start_date": curr_dt,
                "end_date": next_dt,
                "duration_hours": round(p_dur_sec / 3600.0, 2),
            })
            curr_dt = next_dt

        return pranas

    def generate_dehadashas(
        self,
        maha_lord: str,
        antar_lord: str,
        prat_lord: str,
        sookshma_lord: str,
        prana_lord: str,
        prana_start_dt: datetime,
        prana_end_dt: datetime
    ) -> List[Dict[str, Any]]:
        """
        Generates 9 Dehadashas within a Pranadasha (Level 6).
        Sequence starts with the Prana lord.
        Duration = (Prana_duration * Deha_years) / 120.
        """
        p_idx = DASHA_LORDS.index(prana_lord)
        prana_duration_sec = (prana_end_dt - prana_start_dt).total_seconds()

        dehas = []
        curr_dt = prana_start_dt
        for i in range(9):
            d_idx = (p_idx + i) % 9
            d_lord = DASHA_LORDS[d_idx]
            d_frac = DASHA_YEARS[d_lord] / TOTAL_VIMSHOTTARI_YEARS
            d_dur_sec = prana_duration_sec * d_frac
            next_dt = curr_dt + timedelta(seconds=d_dur_sec)
            dehas.append({
                "lord": d_lord,
                "start_date": curr_dt,
                "end_date": next_dt,
                "duration_minutes": round(d_dur_sec / 60.0, 1),
            })
            curr_dt = next_dt

        return dehas

    def get_5level_hierarchy(
        self,
        birth_dt: datetime,
        moon_lon: float,
        target_dt: datetime
    ) -> Dict[str, Any]:
        """
        Calculates all 5 nested active levels (Maha, Antar, Prat, Sookshma, Prana)
        active at the exact target datetime.
        """
        mahadashas = self.generate_mahadasha_sequence(birth_dt, moon_lon, num_cycles=2)

        # 1. Active Mahadasha
        active_maha = None
        for m in mahadashas:
            if m["start_date"] <= target_dt <= m["end_date"]:
                active_maha = m
                break
        if not active_maha:
            active_maha = mahadashas[-1] if target_dt > mahadashas[-1]["end_date"] else mahadashas[0]

        # 2. Active Antardasha
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

        # 3. Active Pratyantardasha
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

        # 4. Active Sookshmadasha
        sookshmas = self.generate_sookshmadashas(
            active_maha["lord"],
            active_antar["lord"],
            active_prat["lord"],
            active_prat["start_date"],
            active_prat["end_date"]
        )
        active_sookshma = None
        for s in sookshmas:
            if s["start_date"] <= target_dt <= s["end_date"]:
                active_sookshma = s
                break
        if not active_sookshma:
            active_sookshma = sookshmas[0] if sookshmas else {"lord": active_prat["lord"], "start_date": active_prat["start_date"], "end_date": active_prat["end_date"]}

        # 5. Active Pranadasha
        pranas = self.generate_pranadashas(
            active_maha["lord"],
            active_antar["lord"],
            active_prat["lord"],
            active_sookshma["lord"],
            active_sookshma["start_date"],
            active_sookshma["end_date"]
        )
        active_prana = None
        for pr in pranas:
            if pr["start_date"] <= target_dt <= pr["end_date"]:
                active_prana = pr
                break
        if not active_prana:
            active_prana = pranas[0] if pranas else {"lord": active_sookshma["lord"], "start_date": active_sookshma["start_date"], "end_date": active_sookshma["end_date"]}

        return {
            "mahadasha": active_maha,
            "antardasha": active_antar,
            "pratyantardasha": active_prat,
            "sookshmadasha": active_sookshma,
            "pranadasha": active_prana,
            "all_antardashas": antardashas,
            "all_pratyantardashas": pratyantars,
            "all_sookshmadashas": sookshmas,
            "all_pranadashas": pranas,
            "summary_short": f"{active_maha['lord']} / {active_antar['lord']} / {active_prat['lord']} / {active_sookshma['lord']} / {active_prana['lord']}"
        }

    def get_active_dasha_at(
        self,
        birth_dt: datetime,
        moon_lon: float,
        target_date: date
    ) -> ActiveDashaHierarchy:
        """
        Returns the active 3-level (Maha/Antar/Pratyantar) hierarchy active on the target date.
        """
        target_dt = datetime.combine(target_date, datetime.min.time())
        h5 = self.get_5level_hierarchy(birth_dt, moon_lon, target_dt)

        active_maha = h5["mahadasha"]
        active_antar = h5["antardasha"]
        active_prat = h5["pratyantardasha"]
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

