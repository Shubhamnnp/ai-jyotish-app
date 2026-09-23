"""
Astrological Search and Research Query Engine for JyotishOS.
Enables searching, pattern discovery, and cross-tabulating horoscopes based on classical yogas,
planetary dignities, house/sign placements, and dasha states.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
from ..core.calculator import default_chart_calculator
from ..core.models import BirthData, KundaliChart
from ..core.constants import SIGN_NAMES, SIGN_LORDS
from .folder_manager import default_folder_manager, BENCHMARK_DEMO_CHARTS

AVAILABLE_RESEARCH_YOGAS = [
    {"key": "gajakesari", "name_hi": "गजकेसरी योग (Gajakesari)", "desc": "चन्द्रमा से केन्द्र में गुरु (१, ४, ७, १० भाव)"},
    {"key": "budhaditya", "name_hi": "बुधादित्य योग (Budhaditya)", "desc": "सूर्य व बुध की एक ही राशि में युति"},
    {"key": "ruchaka", "name_hi": "रुचक महापुरुष योग (Ruchaka)", "desc": "मंगल केन्द्र में स्व/उच्च राशि में (मेष, वृश्चिक, मकर)"},
    {"key": "bhadra", "name_hi": "भद्र महापुरुष योग (Bhadra)", "desc": "बुध केन्द्र में स्व/उच्च राशि में (मिथुन, कन्या)"},
    {"key": "hamsa", "name_hi": "हंस महापुरुष योग (Hamsa)", "desc": "गुरु केन्द्र में स्व/उच्च राशि में (धनु, मीन, कर्क)"},
    {"key": "malavya", "name_hi": "मालव्य महापुरुष योग (Malavya)", "desc": "शुक्र केन्द्र में स्व/उच्च राशि में (वृषभ, तुला, मीन)"},
    {"key": "sasa", "name_hi": "शश महापुरुष योग (Sasa)", "desc": "शनि केन्द्र में स्व/उच्च राशि में (मकर, कुंभ, तुला)"},
    {"key": "vipareeta_raja", "name_hi": "विपरीत राजयोग (Vipareeta Raja)", "desc": "त्रिकेश (६, ८, १२ स्वामी) त्रिक भावों में"},
    {"key": "neechabhanga", "name_hi": "नीचभंग राजयोग (Neechabhanga)", "desc": "नीच ग्रह के राशि स्वामी का केन्द्र में होना"},
    {"key": "manglik", "name_hi": "मांगलिक योग (Manglik)", "desc": "मंगल १, २, ४, ७, ८ या १२वें भाव में"},
    {"key": "kemadruma", "name_hi": "केमद्रुम दोष (Kemadruma)", "desc": "चन्द्रमा से २रे व १२वें भाव में किसी ग्रह का न होना"},
    {"key": "kalasarpa", "name_hi": "कालसर्प दोष (Kalasarpa)", "desc": "सभी ग्रह राहु-केतु अक्ष के एक ओर स्थित"},
]


class AstrologicalResearchEngine:
    """Queries saved and benchmark charts for complex astrological patterns."""

    def __init__(self):
        self._chart_cache: Dict[str, KundaliChart] = {}

    def get_all_searchable_charts(self) -> List[Dict[str, Any]]:
        """Collects all charts from saved database and benchmark pool."""
        all_charts = []
        seen_ids = set()

        # 1. Benchmark Demo Charts
        for c in BENCHMARK_DEMO_CHARTS:
            c_id = f"demo_{c['id']}"
            if c_id not in seen_ids:
                seen_ids.add(c_id)
                all_charts.append({
                    "id": c_id,
                    "name": c["name"],
                    "folder": "🌟 10 प्रामाणिक डेमो कुण्डलियाँ",
                    "birth_data": c["birth_data"]
                })

        # 2. Saved Folders
        folders = default_folder_manager.list_folders()
        for f in folders:
            f_name = f.get("name", "सामान्य")
            for c in f.get("charts", []):
                raw_id = c.get("id", c.get("name", "chart"))
                c_id = f"user_{raw_id}"
                if c_id not in seen_ids:
                    seen_ids.add(c_id)
                    all_charts.append({
                        "id": c_id,
                        "name": c.get("name", "अनाम"),
                        "folder": f_name,
                        "birth_data": c.get("birth_data", {})
                    })

        return all_charts

    def get_or_calculate_chart(self, chart_entry: Dict[str, Any]) -> Optional[KundaliChart]:
        """Calculates or retrieves cached KundaliChart for a chart entry."""
        cid = chart_entry["id"]
        if cid in self._chart_cache:
            return self._chart_cache[cid]

        bd_raw = chart_entry.get("birth_data", {})
        if not bd_raw:
            return None

        try:
            b_date_raw = bd_raw.get("birth_date")
            b_time_raw = bd_raw.get("birth_time")

            if isinstance(b_date_raw, str):
                b_date = datetime.strptime(b_date_raw, "%Y-%m-%d").date()
            else:
                b_date = b_date_raw

            if isinstance(b_time_raw, str):
                b_time = datetime.strptime(b_time_raw, "%H:%M:%S").time() if ":" in b_time_raw else datetime.strptime(b_time_raw, "%H:%M").time()
            else:
                b_time = b_time_raw

            b_data = BirthData(
                name=bd_raw.get("name", chart_entry["name"]),
                birth_date=b_date,
                birth_time=b_time,
                latitude=float(bd_raw.get("latitude", 28.6139)),
                longitude=float(bd_raw.get("longitude", 77.2090)),
                timezone_offset=float(bd_raw.get("timezone_offset", 5.5)),
                city=bd_raw.get("city", "New Delhi")
            )
            calculated = default_chart_calculator.calculate_chart(b_data)
            self._chart_cache[cid] = calculated
            return calculated
        except Exception:
            return None

    def detect_yogas_in_chart(self, chart: KundaliChart) -> List[str]:
        """Checks for the presence of major classical yogas in a chart."""
        yogas_found = []
        planets = chart.planets

        # 1. Gajakesari (Jupiter in 1, 4, 7, 10 from Moon)
        moon_h = planets["Moon"].house_from_lagna
        jup_h = planets["Jupiter"].house_from_lagna
        jup_from_moon = ((jup_h - moon_h) % 12) + 1
        if jup_from_moon in [1, 4, 7, 10]:
            yogas_found.append("gajakesari")

        # 2. Budhaditya (Sun + Mercury in same sign)
        if planets["Sun"].sign_id == planets["Mercury"].sign_id:
            yogas_found.append("budhaditya")

        # 3. Panchamahapurusha
        # Ruchaka (Mars in 1,4,7,10 in Aries 1, Scorpio 8, Capricorn 10)
        if planets["Mars"].house_from_lagna in [1, 4, 7, 10] and planets["Mars"].sign_id in [1, 8, 10]:
            yogas_found.append("ruchaka")

        # Bhadra (Mercury in 1,4,7,10 in Gemini 3, Virgo 6)
        if planets["Mercury"].house_from_lagna in [1, 4, 7, 10] and planets["Mercury"].sign_id in [3, 6]:
            yogas_found.append("bhadra")

        # Hamsa (Jupiter in 1,4,7,10 in Cancer 4, Sag 9, Pisces 12)
        if planets["Jupiter"].house_from_lagna in [1, 4, 7, 10] and planets["Jupiter"].sign_id in [4, 9, 12]:
            yogas_found.append("hamsa")

        # Malavya (Venus in 1,4,7,10 in Taurus 2, Libra 7, Pisces 12)
        if planets["Venus"].house_from_lagna in [1, 4, 7, 10] and planets["Venus"].sign_id in [2, 7, 12]:
            yogas_found.append("malavya")

        # Sasa (Saturn in 1,4,7,10 in Libra 7, Cap 10, Aqu 11)
        if planets["Saturn"].house_from_lagna in [1, 4, 7, 10] and planets["Saturn"].sign_id in [7, 10, 11]:
            yogas_found.append("sasa")

        # 4. Vipareeta Raja Yoga (Lords of 6, 8, 12 in 6, 8, 12)
        def get_lord(h: int) -> str:
            s_id = ((chart.lagna_sign_id - 1 + (h - 1)) % 12) + 1
            return SIGN_LORDS[SIGN_NAMES[s_id - 1]]

        l6, l8, l12 = get_lord(6), get_lord(8), get_lord(12)
        vry = False
        for lord in [l6, l8, l12]:
            if lord in planets and planets[lord].house_from_lagna in [6, 8, 12]:
                vry = True
                break
        if vry:
            yogas_found.append("vipareeta_raja")

        # 5. Neechabhanga
        for p_name, pos in planets.items():
            if pos.dignity == "debilitated":
                dep_lord = SIGN_LORDS[pos.sign_name]
                if dep_lord in planets and planets[dep_lord].house_from_lagna in [1, 4, 7, 10]:
                    yogas_found.append("neechabhanga")
                    break

        # 6. Manglik (Mars in 1, 2, 4, 7, 8, 12)
        if planets["Mars"].house_from_lagna in [1, 2, 4, 7, 8, 12]:
            yogas_found.append("manglik")

        # 7. Kemadruma (No planets in 2nd or 12th from Moon)
        h2_moon = (moon_h % 12) + 1
        h12_moon = ((moon_h - 2) % 12) + 1
        has_occ = False
        for p_name, pos in planets.items():
            if p_name not in ["Moon", "Sun", "Rahu", "Ketu"]:
                if pos.house_from_lagna in [h2_moon, h12_moon]:
                    has_occ = True
                    break
        if not has_occ:
            yogas_found.append("kemadruma")

        # 8. Kalasarpa
        rahu_lon = planets["Rahu"].longitude
        ketu_lon = planets["Ketu"].longitude
        all_one_side = True
        for p_name, pos in planets.items():
            if p_name not in ["Rahu", "Ketu"]:
                diff = (pos.longitude - rahu_lon) % 360.0
                if diff > 180.0:
                    all_one_side = False
                    break
        if all_one_side:
            yogas_found.append("kalasarpa")

        return yogas_found

    def search(
        self,
        yoga_keys: Optional[List[str]] = None,
        lagna_signs: Optional[List[int]] = None,
        planet_in_house: Optional[Dict[str, int]] = None,
        planet_in_sign: Optional[Dict[str, int]] = None,
        planet_dignity: Optional[Dict[str, str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Executes search across all stored charts matching the given criteria.
        """
        all_charts = self.get_all_searchable_charts()
        results = []

        total_filters = 0
        if yoga_keys: total_filters += len(yoga_keys)
        if lagna_signs: total_filters += 1
        if planet_in_house: total_filters += 1
        if planet_in_sign: total_filters += 1
        if planet_dignity: total_filters += 1

        for entry in all_charts:
            chart = self.get_or_calculate_chart(entry)
            if not chart:
                continue

            matches = []
            mismatches = 0

            # 1. Yoga Filter
            detected_yogas = self.detect_yogas_in_chart(chart)
            if yoga_keys:
                for y_key in yoga_keys:
                    if y_key in detected_yogas:
                        # find yoga label
                        y_info = next((y for y in AVAILABLE_RESEARCH_YOGAS if y["key"] == y_key), None)
                        lbl = y_info["name_hi"].split(" ")[0] if y_info else y_key
                        matches.append(f"योग: {lbl}")
                    else:
                        mismatches += 1

            # 2. Lagna Sign
            if lagna_signs:
                if chart.lagna_sign_id in lagna_signs:
                    matches.append(f"लग्न: {chart.lagna_sign_name}")
                else:
                    mismatches += 1

            # 3. Planet in House
            if planet_in_house:
                p_name = planet_in_house.get("planet")
                h_target = planet_in_house.get("house")
                if p_name and h_target and p_name in chart.planets:
                    if chart.planets[p_name].house_from_lagna == h_target:
                        matches.append(f"{p_name} भाव {h_target} में")
                    else:
                        mismatches += 1

            # 4. Planet in Sign
            if planet_in_sign:
                p_name = planet_in_sign.get("planet")
                s_target = planet_in_sign.get("sign")
                if p_name and s_target and p_name in chart.planets:
                    if chart.planets[p_name].sign_id == s_target:
                        s_name = SIGN_NAMES[s_target - 1]
                        matches.append(f"{p_name} {s_name} राशि में")
                    else:
                        mismatches += 1

            # 5. Planet Dignity
            if planet_dignity:
                p_name = planet_dignity.get("planet")
                target_dig = planet_dignity.get("dignity")
                if p_name and target_dig and p_name in chart.planets:
                    if target_dig == "retrograde" and chart.planets[p_name].is_retrograde:
                        matches.append(f"{p_name} वक्री")
                    elif chart.planets[p_name].dignity == target_dig:
                        matches.append(f"{p_name} {target_dig}")
                    else:
                        mismatches += 1

            # Only include if at least 1 match and no hard mismatches if filters are set
            if total_filters > 0 and mismatches == 0 and len(matches) > 0:
                results.append({
                    "id": entry["id"],
                    "name": entry["name"],
                    "folder": entry["folder"],
                    "lagna": chart.lagna_sign_name,
                    "moon_sign": chart.planets["Moon"].sign_name,
                    "nakshatra": chart.panchang.nakshatra_name,
                    "all_yogas": detected_yogas,
                    "matched_criteria": matches,
                    "birth_data": entry["birth_data"]
                })
            elif total_filters == 0:
                # Return all charts with detected yogas
                results.append({
                    "id": entry["id"],
                    "name": entry["name"],
                    "folder": entry["folder"],
                    "lagna": chart.lagna_sign_name,
                    "moon_sign": chart.planets["Moon"].sign_name,
                    "nakshatra": chart.panchang.nakshatra_name,
                    "all_yogas": detected_yogas,
                    "matched_criteria": [f"{len(detected_yogas)} योग सक्रिय"],
                    "birth_data": entry["birth_data"]
                })

        return results


default_research_engine = AstrologicalResearchEngine()
