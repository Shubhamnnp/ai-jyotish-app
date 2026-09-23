"""
Ashtakavarga Kakshya Transit Scanner for JyotishOS (Jagannatha Hora Standard).
Calculates 8-Kakshya transit division (3°45' each) across Saturn, Jupiter, Mars,
Sun, Venus, Mercury, Moon, and Lagna for all transiting planets.
Evaluates native's BAV bindu (1=Subha vs 0=Asubha), generating a live Kakshya meter
and a forward-looking transition timeline.
"""

from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, date, time, timedelta, timezone
try:
    from ..core.ephemeris import PyEphemProvider
    from ..core.constants import SIGN_NAMES, ASHTAKAVARGA_RULES
    from ..core.ashtakavarga import AshtakavargaCalculator
    from ..core.models import KundaliChart
except (ImportError, ValueError):
    from src.jyotish.core.ephemeris import PyEphemProvider
    from src.jyotish.core.constants import SIGN_NAMES, ASHTAKAVARGA_RULES
    from src.jyotish.core.ashtakavarga import AshtakavargaCalculator
    from src.jyotish.core.models import KundaliChart


KAKSHYA_LORDS = ["Saturn", "Jupiter", "Mars", "Sun", "Venus", "Mercury", "Moon", "Lagna"]
KAKSHYA_NAMES_HI = ["शनि", "गुरु", "मंगल", "सूर्य", "शुक्र", "बुध", "चन्द्र", "लग्न"]
KAKSHYA_ICONS = ["🪐", "♃", "♂️", "☀️", "♀️", "☿", "🌙", "🏛️"]

PLANET_NAMES_HI = {
    "Sun": "सूर्य", "Moon": "चन्द्र", "Mars": "मंगल", "Mercury": "बुध",
    "Jupiter": "गुरु", "Venus": "शुक्र", "Saturn": "शनि", "Rahu": "राहु", "Ketu": "केतु"
}


class KakshyaTransitService:
    """Calculates classical 8-Kakshya transit divisions and BAV bindu auspiciousness."""

    def __init__(self):
        self.provider = PyEphemProvider()

    def get_kakshya_details(
        self,
        planet_name: str,
        transit_lon: float,
        chart: KundaliChart
    ) -> Dict[str, Any]:
        """
        Calculates the Kakshya of a planet given its transit longitude and the native's chart.
        """
        norm_lon = transit_lon % 360.0
        sign_idx = int(norm_lon // 30.0)  # 0..11
        sign_name = SIGN_NAMES[sign_idx]
        deg_in_sign = norm_lon % 30.0

        # Kakshya index 0..7 (each 3.75 degrees = 3 deg 45 min)
        kakshya_idx = min(7, int(deg_in_sign / 3.75))
        kakshya_lord = KAKSHYA_LORDS[kakshya_idx]
        kakshya_lord_hi = KAKSHYA_NAMES_HI[kakshya_idx]
        kakshya_icon = KAKSHYA_ICONS[kakshya_idx]

        start_deg = kakshya_idx * 3.75
        end_deg = (kakshya_idx + 1) * 3.75
        deg_progress = (deg_in_sign - start_deg) / 3.75 * 100.0

        # Native's natal contributor positions (1..12)
        contributors = {
            "Sun": chart.planets["Sun"].sign_id,
            "Moon": chart.planets["Moon"].sign_id,
            "Mars": chart.planets["Mars"].sign_id,
            "Mercury": chart.planets["Mercury"].sign_id,
            "Jupiter": chart.planets["Jupiter"].sign_id,
            "Venus": chart.planets["Venus"].sign_id,
            "Saturn": chart.planets["Saturn"].sign_id,
            "Lagna": chart.lagna_sign_id,
        }

        # Check if contributor gave a bindu for this planet in this sign
        target_sign_1based = sign_idx + 1
        ref_sign = contributors.get(kakshya_lord, 1)
        house_from_contrib = ((target_sign_1based - ref_sign) % 12) + 1

        # Check in ASHTAKAVARGA_RULES
        rule_planet = planet_name if planet_name in ASHTAKAVARGA_RULES else "Saturn"
        allowed_houses = ASHTAKAVARGA_RULES.get(rule_planet, {}).get(kakshya_lord, [])
        has_bindu = house_from_contrib in allowed_houses
        bindu_val = 1 if has_bindu else 0

        # Full 8 Kakshyas status for this planet in this sign
        full_kakshyas = []
        for k_i in range(8):
            k_lord = KAKSHYA_LORDS[k_i]
            k_ref = contributors.get(k_lord, 1)
            h = ((target_sign_1based - k_ref) % 12) + 1
            b = 1 if h in ASHTAKAVARGA_RULES.get(rule_planet, {}).get(k_lord, []) else 0
            full_kakshyas.append({
                "kakshya_num": k_i + 1,
                "lord": k_lord,
                "lord_hi": KAKSHYA_NAMES_HI[k_i],
                "icon": KAKSHYA_ICONS[k_i],
                "range_deg": f"{k_i*3.75:.2f}° - {(k_i+1)*3.75:.2f}°",
                "bindu": b,
                "is_current": (k_i == kakshya_idx)
            })

        # Calculate BAV score for this sign
        bav_sign_score = sum(k["bindu"] for k in full_kakshyas)

        # Interpret status
        if bindu_val == 1:
            verdict_badge = "🟢 शुभ फलदायी (Subha)"
            verdict_desc = f"कक्षी स्वामी {kakshya_lord_hi} ने जातक के अष्टकवर्ग में बिन्दु प्रदान किया है। इस कक्षी ({start_deg:.1f}°-{end_deg:.1f}°) में गोचर अत्यंत शुभ व कार्यसिद्धि कारक रहेगा।"
        else:
            verdict_badge = "🔴 अशुभ / रिक्ता (Asubha)"
            verdict_desc = f"कक्षी स्वामी {kakshya_lord_hi} द्वारा बिन्दु शून्य (0) है। इस कक्षी में गोचर के दौरान ग्रह फल देने में असमर्थ व विलंबकारी रहेगा।"

        return {
            "planet": planet_name,
            "planet_hi": PLANET_NAMES_HI.get(planet_name, planet_name),
            "transit_lon": norm_lon,
            "sign_name": sign_name,
            "sign_idx": sign_idx,
            "deg_in_sign": deg_in_sign,
            "kakshya_num": kakshya_idx + 1,
            "kakshya_lord": kakshya_lord,
            "kakshya_lord_hi": kakshya_lord_hi,
            "kakshya_icon": kakshya_icon,
            "start_deg": start_deg,
            "end_deg": end_deg,
            "deg_progress": deg_progress,
            "has_bindu": has_bindu,
            "bindu_val": bindu_val,
            "verdict_badge": verdict_badge,
            "verdict_desc": verdict_desc,
            "bav_sign_score": bav_sign_score,
            "full_kakshyas": full_kakshyas
        }

    def scan_all_transits(
        self,
        chart: KundaliChart,
        target_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        Scans Kakshya positions for all 7 classical planets on target_date.
        """
        if target_date is None:
            target_date = date.today()

        dt_noon = datetime.combine(target_date, time(12, 0)).replace(tzinfo=timezone.utc)
        pos, _ = self.provider.get_planet_positions(dt_noon)

        planets_to_scan = ["Saturn", "Jupiter", "Mars", "Sun", "Venus", "Mercury", "Moon"]
        results = {}
        for p in planets_to_scan:
            if p in pos:
                lon = pos[p]["longitude"]
                results[p] = self.get_kakshya_details(p, lon, chart)

        # Count total subha vs asubha active kakshyas
        subha_count = sum(1 for r in results.values() if r["bindu_val"] == 1)
        total_count = len(results)

        return {
            "target_date": target_date,
            "planets": results,
            "subha_count": subha_count,
            "asubha_count": total_count - subha_count,
            "total_count": total_count,
            "overall_kakshya_pct": round((subha_count / total_count) * 100.0, 1)
        }

    def generate_30day_kakshya_timeline(
        self,
        chart: KundaliChart,
        start_date: Optional[date] = None,
        days: int = 30
    ) -> List[Dict[str, Any]]:
        """
        Generates day-by-day Kakshya transit timeline for major planets (Saturn, Jupiter, Mars)
        highlighting transition dates when a planet moves from Subha to Asubha or vice-versa.
        """
        if start_date is None:
            start_date = date.today()

        timeline = []
        prev_sat_k = None
        prev_jup_k = None

        for d_offset in range(days):
            cur_d = start_date + timedelta(days=d_offset)
            dt_noon = datetime.combine(cur_d, time(12, 0)).replace(tzinfo=timezone.utc)
            pos, _ = self.provider.get_planet_positions(dt_noon)

            sat_k = self.get_kakshya_details("Saturn", pos["Saturn"]["longitude"], chart) if "Saturn" in pos else None
            jup_k = self.get_kakshya_details("Jupiter", pos["Jupiter"]["longitude"], chart) if "Jupiter" in pos else None
            mars_k = self.get_kakshya_details("Mars", pos["Mars"]["longitude"], chart) if "Mars" in pos else None

            # Detect transition events
            events = []
            if sat_k and prev_sat_k and sat_k["kakshya_num"] != prev_sat_k["kakshya_num"]:
                status = "शुभ (Bindu 1)" if sat_k["bindu_val"] == 1 else "अशुभ (Bindu 0)"
                events.append(f"🪐 शनि कक्षी परिवर्तन: {sat_k['kakshya_lord_hi']} कक्षी में प्रवेश ({status})")

            if jup_k and prev_jup_k and jup_k["kakshya_num"] != prev_jup_k["kakshya_num"]:
                status = "शुभ (Bindu 1)" if jup_k["bindu_val"] == 1 else "अशुभ (Bindu 0)"
                events.append(f"♃ गुरु कक्षी परिवर्तन: {jup_k['kakshya_lord_hi']} कक्षी में प्रवेश ({status})")

            timeline.append({
                "date": cur_d,
                "date_str": cur_d.strftime("%d-%b-%Y"),
                "saturn": sat_k,
                "jupiter": jup_k,
                "mars": mars_k,
                "events": events
            })

            prev_sat_k = sat_k
            prev_jup_k = jup_k

        return timeline


# Singleton instance
default_kakshya_service = KakshyaTransitService()

