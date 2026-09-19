"""
Gochar (Planetary Transit) Engine for JyotishOS.
Calculates transits for any given target date/window and analyzes interactions with the natal chart:
- Houses from Natal Lagna & Natal Moon
- Sade Sati (Phase 1, Peak, Phase 3) & Dhaiya (4th/8th)
- Jupiter-Saturn Double Transit on Dasama (10th)
- Guru-Chandal transit conjunction
- Ashtakavarga bindu support at transit positions
"""

from datetime import datetime, date, time
from typing import Dict, Any, Optional, Tuple
from .constants import SIGN_NAMES, SPECIAL_ASPECTS
from .models import KundaliChart, TransitSummary
from .ephemeris import PyEphemProvider, default_ephemeris_provider
from .ashtakavarga import AshtakavargaCalculator


class TransitEngine:
    """Computes and analyzes Gochar relative to a natal KundaliChart."""

    def __init__(self, ephem_provider: Optional[PyEphemProvider] = None):
        self.provider = ephem_provider or default_ephemeris_provider

    def compute_transit_snapshot(
        self,
        chart: KundaliChart,
        target_date: date,
        ayanamsa_name: str = "Lahiri"
    ) -> Tuple[Dict[str, Dict[str, Any]], TransitSummary]:
        """
        Calculates transit positions for the target date and evaluates
        key astrological transit indicators against the natal chart.
        """
        # Noon UTC on target date for standard transit evaluation
        target_dt = datetime.combine(target_date, time(12, 0, 0))
        raw_transits, _ = self.provider.get_planet_positions(target_dt, ayanamsa_name)

        natal_moon_sign = chart.planets["Moon"].sign_id
        natal_lagna_sign = chart.lagna_sign_id

        transit_data: Dict[str, Dict[str, Any]] = {}
        transit_bindus: Dict[str, int] = {}

        for p_name, p_info in raw_transits.items():
            lon = p_info["longitude"]
            sign_id = int((lon % 360.0) // 30.0) + 1
            sign_deg = lon % 30.0

            house_moon = ((sign_id - natal_moon_sign) % 12) + 1
            house_lagna = ((sign_id - natal_lagna_sign) % 12) + 1

            # Ashtakavarga bindu lookup if available
            bindu = 0
            if chart.ashtakavarga and p_name in chart.ashtakavarga.bav:
                bindu = AshtakavargaCalculator.get_transit_bindus(
                    chart.ashtakavarga, p_name, sign_id
                )
                transit_bindus[p_name] = bindu

            transit_data[p_name] = {
                "longitude": lon,
                "sign_id": sign_id,
                "sign_name": SIGN_NAMES[sign_id - 1],
                "sign_degree": sign_deg,
                "speed": p_info.get("speed", 0.0),
                "is_retrograde": p_info.get("is_retrograde", False),
                "house_from_moon": house_moon,
                "house_from_lagna": house_lagna,
                "ashtakavarga_bindu": bindu,
            }

        # --- 1. Shani Sade Sati Check ---
        saturn_h_moon = transit_data["Saturn"]["house_from_moon"]
        is_sade_sati = saturn_h_moon in (12, 1, 2)
        sade_sati_phase = None
        if saturn_h_moon == 12:
            sade_sati_phase = "Phase 1 (Rising / Arambhik - 12th from Moon)"
        elif saturn_h_moon == 1:
            sade_sati_phase = "Phase 2 (Peak / Madhyam - Over Natal Moon)"
        elif saturn_h_moon == 2:
            sade_sati_phase = "Phase 3 (Setting / Antarik - 2nd from Moon)"

        # --- 2. Shani Dhaiya Check ---
        is_dhaiya = saturn_h_moon in (4, 8)
        dhaiya_type = None
        if saturn_h_moon == 4:
            dhaiya_type = "Kantaka / Ardhashtama Shani (4th from Moon)"
        elif saturn_h_moon == 8:
            dhaiya_type = "Ashtama Shani (8th from Moon - Health & Obstacles)"

        # --- 3. Double Transit on 10th House (Career Trigger) ---
        # Saturn aspects 3, 7, 10 or occupies 10th
        sat_h_lagna = transit_data["Saturn"]["house_from_lagna"]
        sat_aspects_10th = (
            sat_h_lagna == 10 or
            ((sat_h_lagna - 1 + 2) % 12 + 1) == 10 or  # 3rd aspect
            ((sat_h_lagna - 1 + 6) % 12 + 1) == 10 or  # 7th aspect
            ((sat_h_lagna - 1 + 9) % 12 + 1) == 10     # 10th aspect
        )
        # Jupiter aspects 5, 7, 9 or occupies 10th
        jup_h_lagna = transit_data["Jupiter"]["house_from_lagna"]
        jup_aspects_10th = (
            jup_h_lagna == 10 or
            ((jup_h_lagna - 1 + 4) % 12 + 1) == 10 or  # 5th aspect
            ((jup_h_lagna - 1 + 6) % 12 + 1) == 10 or  # 7th aspect
            ((jup_h_lagna - 1 + 8) % 12 + 1) == 10     # 9th aspect
        )
        double_transit_10th = sat_aspects_10th and jup_aspects_10th

        # --- 4. Guru-Chandal Transit Conjunction ---
        jup_lon = transit_data["Jupiter"]["longitude"]
        rahu_lon = transit_data["Rahu"]["longitude"]
        jup_rahu_diff = abs(jup_lon - rahu_lon)
        if jup_rahu_diff > 180.0:
            jup_rahu_diff = 360.0 - jup_rahu_diff
        is_guru_chandal = (jup_rahu_diff <= 8.0)

        summary = TransitSummary(
            saturn_house_from_moon=saturn_h_moon,
            saturn_house_from_lagna=sat_h_lagna,
            jupiter_house_from_moon=transit_data["Jupiter"]["house_from_moon"],
            jupiter_house_from_lagna=jup_h_lagna,
            is_sade_sati=is_sade_sati,
            sade_sati_phase=sade_sati_phase,
            is_dhaiya=is_dhaiya,
            dhaiya_type=dhaiya_type,
            is_jupiter_saturn_double_transit_on_10th=double_transit_10th,
            is_guru_chandal_transit=is_guru_chandal,
            saturn_retrograde=transit_data["Saturn"]["is_retrograde"],
            jupiter_retrograde=transit_data["Jupiter"]["is_retrograde"],
            ashtakavarga_transit_bindus=transit_bindus,
        )

        return transit_data, summary


# Singleton transit engine
default_transit_engine = TransitEngine()
