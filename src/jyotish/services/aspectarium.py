"""
Dynamic Vedic and Western Aspectarium Engine for JyotishOS (Shri Jyoti Star Grade).
Calculates:
1. 9x9 Angular Distance Matrix (exact degrees and arcminutes).
2. Vedic Drishti Matrix (100% Special aspects of Mars 4/8, Jupiter 5/9, Saturn 3/10, all 7th).
3. Western Major Aspectarium (Conjunction 0°, Sextile 60°, Square 90°, Trine 120°, Opposition 180°, Quincunx 150°).
4. Applying (A - intensifying) vs Separating (S - fading) orbs based on planetary speeds.
5. High-contrast, responsive visual aspect grid.
"""

from typing import Dict, List, Any, Optional, Tuple
try:
    from ..core.models import KundaliChart
    from ..core.constants import GRAHAS as PLANET_NAMES
except (ImportError, ValueError):
    from src.jyotish.core.models import KundaliChart
    from src.jyotish.core.constants import GRAHAS as PLANET_NAMES


PLANET_SPEED_RANK = {
    "Moon": 1, "Mercury": 2, "Venus": 3, "Sun": 4,
    "Mars": 5, "Jupiter": 6, "Saturn": 7, "Rahu": 8, "Ketu": 9
}

PLANET_SYMBOLS = {
    "Sun": "☀️", "Moon": "🌙", "Mars": "♂️", "Mercury": "☿",
    "Jupiter": "♃", "Venus": "♀️", "Saturn": "🪐", "Rahu": "☊", "Ketu": "☋"
}

PLANET_NAMES_HI = {
    "Sun": "सूर्य", "Moon": "चन्द्र", "Mars": "मंगल", "Mercury": "बुध",
    "Jupiter": "गुरु", "Venus": "शुक्र", "Saturn": "शनि", "Rahu": "राहु", "Ketu": "केतु"
}

WESTERN_ASPECT_RULES = [
    {"name": "Conjunction (युति)", "angle": 0.0, "orb": 8.0, "symbol": "☌", "nature": "Neutral / Dynamic", "color": "#F59E0B"},
    {"name": "Sextile (लाभ)", "angle": 60.0, "orb": 5.0, "symbol": "⚹", "nature": "Harmonic (शुभ)", "color": "#3B82F6"},
    {"name": "Square (केंद्र/कष्ट)", "angle": 90.0, "orb": 6.0, "symbol": "□", "nature": "Tension / Challenge (चुनौती)", "color": "#EF4444"},
    {"name": "Trine (त्रिकोण/वरदान)", "angle": 120.0, "orb": 7.0, "symbol": "△", "nature": "Grace / Harmony (परम शुभ)", "color": "#10B981"},
    {"name": "Quincunx (षडाष्टक)", "angle": 150.0, "orb": 3.0, "symbol": "⚼", "nature": "Adjustment / Health (सामंजस्य)", "color": "#8B5CF6"},
    {"name": "Opposition (प्रतियुति)", "angle": 180.0, "orb": 8.0, "symbol": "☍", "nature": "Polarity / Awareness (विरोध)", "color": "#DC2626"},
]


class AspectariumService:
    """Calculates comprehensive Vedic and Western angular aspects between all planets."""

    @classmethod
    def calculate_aspectarium(cls, chart: KundaliChart) -> Dict[str, Any]:
        """
        Generates full 9x9 aspectarium matrix, Vedic drishti connections, and active major aspects.
        """
        planets = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]
        active_planets = [p for p in planets if p in chart.planets]

        matrix_data: Dict[str, Dict[str, Any]] = {p: {} for p in active_planets}
        detected_aspects: List[Dict[str, Any]] = []
        vedic_drishtis: List[Dict[str, Any]] = []

        for i, p1 in enumerate(active_planets):
            lon1 = chart.planets[p1].longitude
            for j, p2 in enumerate(active_planets):
                if p1 == p2:
                    matrix_data[p1][p2] = {"angle": 0.0, "aspect": "Self", "symbol": "—", "orb": 0.0}
                    continue

                lon2 = chart.planets[p2].longitude

                # Shortest angular distance
                diff = abs(lon1 - lon2) % 360.0
                ang_dist = min(diff, 360.0 - diff)

                # Check Western Major Aspect
                matched_asp = None
                for asp in WESTERN_ASPECT_RULES:
                    orb_val = abs(ang_dist - asp["angle"])
                    if orb_val <= asp["orb"]:
                        # Determine Applying (A) vs Separating (S)
                        # The faster planet moving toward exact aspect = Applying
                        is_faster_p1 = PLANET_SPEED_RANK.get(p1, 5) < PLANET_SPEED_RANK.get(p2, 5)
                        # Relative position determines motion toward/away
                        is_applying = (lon1 < lon2 and is_faster_p1) or (lon2 < lon1 and not is_faster_p1)
                        app_sep_code = "A" if is_applying else "S"

                        matched_asp = {
                            "name": asp["name"],
                            "symbol": asp["symbol"],
                            "exact_angle": asp["angle"],
                            "angular_dist": round(ang_dist, 2),
                            "orb": round(orb_val, 2),
                            "orb_str": f"{int(orb_val)}°{int((orb_val%1)*60):02d}' {app_sep_code}",
                            "nature": asp["nature"],
                            "color": asp["color"],
                            "is_applying": is_applying
                        }
                        break

                matrix_data[p1][p2] = {
                    "angle": round(ang_dist, 2),
                    "aspect_info": matched_asp
                }

                # Avoid duplicate pair reporting in list
                if i < j and matched_asp:
                    motion_hi = "⚡ संमुख (Applying)" if matched_asp["is_applying"] else "मन्द/विमुख (Separating)"
                    detected_aspects.append({
                        "p1": p1,
                        "p2": p2,
                        "planet1": p1,
                        "planet2": p2,
                        "p1_hi": PLANET_NAMES_HI.get(p1, p1),
                        "p2_hi": PLANET_NAMES_HI.get(p2, p2),
                        "p1_icon": PLANET_SYMBOLS.get(p1, ""),
                        "p2_icon": PLANET_SYMBOLS.get(p2, ""),
                        "aspect_name": matched_asp["name"],
                        "actual_angle": matched_asp["angular_dist"],
                        "orb_abs": matched_asp["orb"],
                        "motion_hi": motion_hi,
                        **matched_asp
                    })

                # Check Vedic Special Drishti from p1 to p2
                # House distance from p1 sign to p2 sign
                s1 = chart.planets[p1].sign_id
                s2 = chart.planets[p2].sign_id
                h_dist = ((s2 - s1) % 12) + 1

                vedic_str = None
                if h_dist == 7:
                    vedic_str = "पूर्ण समसप्तक दृष्टि (100% 7th Aspect)"
                elif p1 == "Mars" and h_dist in [4, 8]:
                    vedic_str = f"मंगल विशेष {h_dist}वीं दृष्टि (100% Mars Aspect)"
                elif p1 == "Jupiter" and h_dist in [5, 9]:
                    vedic_str = f"गुरु विशेष {h_dist}वीं दृष्टि (100% Jupiter Divine Aspect)"
                elif p1 == "Saturn" and h_dist in [3, 10]:
                    vedic_str = f"शनि विशेष {h_dist}वीं दृष्टि (100% Saturn Aspect)"
                elif p1 in ["Rahu", "Ketu"] and h_dist in [5, 9]:
                    vedic_str = f"{PLANET_NAMES_HI.get(p1, p1)} विशेष {h_dist}वीं त्रिकोण दृष्टि"

                if vedic_str:
                    vedic_drishtis.append({
                        "aspecting": p1,
                        "aspected": p2,
                        "drishti_kar": f"{PLANET_NAMES_HI.get(p1, p1)} ({p1})",
                        "drishti_prapak": f"{PLANET_NAMES_HI.get(p2, p2)} ({p2})",
                        "drishti_type": vedic_str,
                        "house_dist": h_dist,
                        "impact": f"पूर्ण दृष्टि ({h_dist}वें भाव पर)",
                        "aspecting_hi": PLANET_NAMES_HI.get(p1, p1),
                        "aspected_hi": PLANET_NAMES_HI.get(p2, p2),
                        "aspecting_icon": PLANET_SYMBOLS.get(p1, ""),
                        "aspected_icon": PLANET_SYMBOLS.get(p2, ""),
                        "house_distance": h_dist,
                        "description": vedic_str,
                        "exact_degrees": round(ang_dist, 2)
                    })

        return {
            "planets": active_planets,
            "matrix_data": matrix_data,
            "aspects": detected_aspects,
            "detected_aspects": detected_aspects,
            "vedic_drishtis": vedic_drishtis,
            "total_aspects_count": len(detected_aspects),
            "total_drishti_count": len(vedic_drishtis)
        }

    @classmethod
    def render_aspectarium_html(cls, chart: KundaliChart) -> str:
        """
        Renders an interactive, responsive Aspectarium Grid in HTML.
        """
        data = cls.calculate_aspectarium(chart)
        planets = data["planets"]
        matrix = data["matrix_data"]

        headers_html = "".join([f'<th style="padding:8px 6px; text-align:center; font-size:12px; color:#F8FAFC; background:#0F172A; border:1px solid #334155;">{PLANET_SYMBOLS.get(p, "")}<br>{PLANET_NAMES_HI.get(p, p)[:2]}</th>' for p in planets])

        rows_html = ""
        for i, p1 in enumerate(planets):
            row_cells = f'<td style="padding:6px 10px; font-weight:700; font-size:13px; color:#0F172A; background:#F1F5F9; border:1px solid #CBD5E1; white-space:nowrap;">{PLANET_SYMBOLS.get(p1, "")} {PLANET_NAMES_HI.get(p1, p1)}</td>'
            for j, p2 in enumerate(planets):
                if i == j:
                    cell = '<td style="background:#E2E8F0; text-align:center; color:#94A3B8; font-size:11px; border:1px solid #CBD5E1;">—</td>'
                elif i > j:
                    # Show angular distance in lower diagonal
                    ang = matrix[p1][p2]["angle"]
                    cell = f'<td style="background:#FFFFFF; text-align:center; color:#475569; font-size:11px; border:1px solid #E2E8F0;" title="{p1}-{p2}: {ang}°">{ang:.1f}°</td>'
                else:
                    # Show aspect symbol & orb in upper diagonal
                    asp_info = matrix[p1][p2].get("aspect_info")
                    if asp_info:
                        cell = f'<td style="background:#FFFFFF; text-align:center; font-weight:800; font-size:14px; color:{asp_info["color"]}; border:1.5px solid {asp_info["color"]}; cursor:pointer;" title="{asp_info["name"]} (Orb: {asp_info["orb_str"]})">{asp_info["symbol"]}</td>'
                    else:
                        cell = '<td style="background:#FAFAFA; text-align:center; color:#CBD5E1; font-size:11px; border:1px solid #E2E8F0;">·</td>'
                row_cells += cell

            rows_html += f"<tr>{row_cells}</tr>"

        html = f"""
<div style="font-family: 'Segoe UI', Tahoma, sans-serif; overflow-x: auto; margin-bottom: 20px;">
    <table style="width: 100%; border-collapse: collapse; text-align: center; border: 1.5px solid #CBD5E1; border-radius: 8px; overflow: hidden; background: #FFFFFF;">
        <thead>
            <tr>
                <th style="padding: 10px; background: #0F172A; color: #FFFFFF; font-size: 13px; text-align: left;">ग्रह (Graha)</th>
                {headers_html}
            </tr>
        </thead>
        <tbody>
            {rows_html}
        </tbody>
    </table>
    <div style="display: flex; gap: 14px; flex-wrap: wrap; margin-top: 10px; font-size: 12px; color: #475569;">
        <span><b style="color: #10B981;">△</b> त्रिकोण (120° Trine)</span>
        <span><b style="color: #3B82F6;">⚹</b> लाभ (60° Sextile)</span>
        <span><b style="color: #F59E0B;">☌</b> युति (0° Conjunction)</span>
        <span><b style="color: #EF4444;">□</b> केंद्र/कष्ट (90° Square)</span>
        <span><b style="color: #DC2626;">☍</b> प्रतियुति (180° Opposition)</span>
        <span><b style="color: #8B5CF6;">⚼</b> षडाष्टक (150° Quincunx)</span>
    </div>
</div>
        """
        return html


# Singleton instance
default_aspectarium_service = AspectariumService()
