"""
Dasha and Transit Timing Integrator for JyotishOS (Phase 5, Task P5-T4).
Reference: docs/IMPLEMENTATION_PRD.md (Section 5.4, P5-T4).

Connects:
1. Active Vimshottari Dasha hierarchy (MD, AD, PD) at any given query date.
2. Classical Double Transit (Guru & Shani Gochar) triggering bhava fruition.
3. Maps whether dasha lords and transiting planets act as domain significators
   (Bhava Lord, Bhava Occupant, Karaka, or Aspecting Planet).
4. Annotates Evidence Findings with verified timing windows.
"""

from datetime import date, datetime
from typing import Dict, List, Optional, Tuple, Set, Any
from pydantic import BaseModel, Field

from ..core.models import KundaliChart
from ..dasha.vimshottari import default_dasha_engine
from ..core.gochar import default_transit_engine
from .factors import ChartFactors, PlanetFactors, HouseFactors


class TimingEvaluation(BaseModel):
    """Detailed timing evaluation for a domain at a specific date."""
    target_date: date
    active_md_lord: str
    active_ad_lord: str
    active_pd_lord: str
    md_window: str
    ad_window: str
    is_dasha_significator: bool
    dasha_significance_reasons: List[str] = Field(default_factory=list)
    is_double_transit_active: bool
    transit_reasons: List[str] = Field(default_factory=list)
    timing_confidence: float = Field(default=0.5, ge=0.0, le=1.0)


class TimingIntegrator:
    """Evaluates planetary timing alignment against domain significators."""

    @classmethod
    def evaluate_timing_for_domain(
        cls,
        chart: KundaliChart,
        factors: ChartFactors,
        target_date: date,
        primary_bhavas: List[int],
        primary_karakas: List[str]
    ) -> TimingEvaluation:
        """
        Determines whether active dasha lords and transits at target_date
        signify and activate the requested domain.
        """
        full_dt = datetime.combine(chart.birth_data.birth_date, chart.birth_data.birth_time)
        moon_lon = chart.planets["Moon"].longitude

        # 1. Active Dasha Hierarchy
        active_dasha = default_dasha_engine.get_active_dasha_at(full_dt, moon_lon, target_date)
        if hasattr(active_dasha, "mahadasha"):
            md_lord = active_dasha.mahadasha.lord
            ad_lord = active_dasha.antardasha.lord
            pd_lord = active_dasha.pratyantardasha.lord
            md_start = active_dasha.mahadasha.start_date.strftime("%Y-%m-%d") if hasattr(active_dasha.mahadasha.start_date, "strftime") else str(active_dasha.mahadasha.start_date)
            md_end = active_dasha.mahadasha.end_date.strftime("%Y-%m-%d") if hasattr(active_dasha.mahadasha.end_date, "strftime") else str(active_dasha.mahadasha.end_date)
            ad_start = active_dasha.antardasha.start_date.strftime("%Y-%m-%d") if hasattr(active_dasha.antardasha.start_date, "strftime") else str(active_dasha.antardasha.start_date)
            ad_end = active_dasha.antardasha.end_date.strftime("%Y-%m-%d") if hasattr(active_dasha.antardasha.end_date, "strftime") else str(active_dasha.antardasha.end_date)
        else:
            md_lord = active_dasha.get("maha_dasha", "")
            ad_lord = active_dasha.get("antar_dasha", "")
            pd_lord = active_dasha.get("pratyantar_dasha", "")
            md_start = str(active_dasha.get("md_start", ""))
            md_end = str(active_dasha.get("md_end", ""))
            ad_start = str(active_dasha.get("ad_start", ""))
            ad_end = str(active_dasha.get("ad_end", ""))

        md_window_str = f"{md_lord} MD: {md_start} -> {md_end}"
        ad_window_str = f"{ad_lord} AD: {ad_start} -> {ad_end}"

        # 2. Collect Domain Significator Planets
        significator_planets: Set[str] = set(primary_karakas)

        # Add bhava lords and occupants of primary bhavas
        for bh_num in primary_bhavas:
            hf = factors.houses.get(bh_num)
            if hf:
                if hf.lord:
                    significator_planets.add(hf.lord)
                for occ in hf.occupants:
                    significator_planets.add(occ)
                for asp in hf.aspecting_planets:
                    significator_planets.add(asp)

        # 3. Check Dasha Lords Alignment
        dasha_reasons: List[str] = []
        md_is_sig = md_lord in significator_planets
        ad_is_sig = ad_lord in significator_planets
        pd_is_sig = pd_lord in significator_planets

        if md_is_sig:
            dasha_reasons.append(f"Maha Dasha lord {md_lord} is a primary domain significator")
        if ad_is_sig:
            dasha_reasons.append(f"Antar Dasha lord {ad_lord} activates domain significations")
        if pd_is_sig:
            dasha_reasons.append(f"Pratyantar lord {pd_lord} triggers active window fruition")

        is_dasha_active = (md_is_sig or ad_is_sig)

        # 4. Double Transit Evaluation (Jupiter & Saturn)
        transit_data, summary = default_transit_engine.compute_transit_snapshot(chart, target_date)
        transit_reasons: List[str] = []

        # Find Jupiter and Saturn transit houses relative to Lagna
        jup_info = transit_data.get("Jupiter", {})
        sat_info = transit_data.get("Saturn", {})
        jup_transit_h = jup_info.get("house_from_lagna", 1)
        sat_transit_h = sat_info.get("house_from_lagna", 1)

        # Check if Jupiter or Saturn transit or aspect primary bhavas
        jup_aspect_houses = {
            jup_transit_h,
            ((jup_transit_h + 5 - 2) % 12) + 1,
            ((jup_transit_h + 7 - 2) % 12) + 1,
            ((jup_transit_h + 9 - 2) % 12) + 1
        }
        sat_aspect_houses = {
            sat_transit_h,
            ((sat_transit_h + 3 - 2) % 12) + 1,
            ((sat_transit_h + 7 - 2) % 12) + 1,
            ((sat_transit_h + 10 - 2) % 12) + 1
        }

        jup_touches = any(h in jup_aspect_houses for h in primary_bhavas)
        sat_touches = any(h in sat_aspect_houses for h in primary_bhavas)
        double_transit = jup_touches and sat_touches

        if jup_touches:
            transit_reasons.append(f"Transiting Jupiter influences primary bhava {primary_bhavas[0]} (House {jup_transit_h})")
        if sat_touches:
            transit_reasons.append(f"Transiting Saturn influences primary bhava {primary_bhavas[0]} (House {sat_transit_h})")
        if double_transit:
            transit_reasons.append("Classical Double Transit (Guru & Shani) fully established over domain axis")

        # 5. Composite Timing Confidence
        t_conf = 0.30
        if is_dasha_active:
            t_conf += 0.35
        if double_transit:
            t_conf += 0.25
        elif jup_touches or sat_touches:
            t_conf += 0.15

        return TimingEvaluation(
            target_date=target_date,
            active_md_lord=md_lord,
            active_ad_lord=ad_lord,
            active_pd_lord=pd_lord,
            md_window=md_window_str,
            ad_window=ad_window_str,
            is_dasha_significator=is_dasha_active,
            dasha_significance_reasons=dasha_reasons,
            is_double_transit_active=double_transit,
            transit_reasons=transit_reasons,
            timing_confidence=round(min(1.0, max(0.1, t_conf)), 3)
        )


default_timing_integrator = TimingIntegrator()
