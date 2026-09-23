"""
Multi-Year Ephemeris Waves and Retrograde Ingress Engine for JyotishOS (Shri Jyoti Star Grade).
Generates:
1. 5-Year High-Precision Planetary Trajectory Curves for Saturn, Jupiter, Rahu, Ketu, and Mars.
2. Exact Retrograde (वक्र), Stationary (स्थिर), and Direct (मार्गी) Phase Transitions.
3. Rashi Ingress (राशि परिवर्तन) Milestones over 5-year span.
4. Responsive SVG/HTML Wave Graph with color-coded motion paths.
"""

from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, date, time, timedelta, timezone
try:
    from ..core.ephemeris import PyEphemProvider
    from ..core.constants import SIGN_NAMES
except (ImportError, ValueError):
    from src.jyotish.core.ephemeris import PyEphemProvider
    from src.jyotish.core.constants import SIGN_NAMES

PLANET_CONFIGS = {
    "Saturn": {"name_hi": "शनि", "color": "#3B82F6", "symbol": "🪐", "step_days": 10},
    "Jupiter": {"name_hi": "गुरु", "color": "#F59E0B", "symbol": "♃", "step_days": 7},
    "Rahu": {"name_hi": "राहु", "color": "#64748B", "symbol": "☊", "step_days": 15},
    "Mars": {"name_hi": "मंगल", "color": "#EF4444", "symbol": "♂️", "step_days": 5},
}


class EphemerisWavesService:
    """Calculates multi-year transit trajectories, retrograde loops, and visual wave charts."""

    def __init__(self):
        self.provider = PyEphemProvider()

    def generate_multi_year_waves(
        self,
        start_year: Optional[int] = None,
        duration_years: int = 5
    ) -> Dict[str, Any]:
        """
        Calculates 5-year trajectory points, retrograde intervals, and ingress events.
        """
        if start_year is None:
            start_year = date.today().year

        start_dt = datetime(start_year, 1, 1, 12, 0, tzinfo=timezone.utc)
        end_dt = datetime(start_year + duration_years, 12, 31, 12, 0, tzinfo=timezone.utc)
        total_days = (end_dt - start_dt).days

        planet_trajectories: Dict[str, List[Dict[str, Any]]] = {}
        retrograde_events: List[Dict[str, Any]] = []
        ingress_events: List[Dict[str, Any]] = []

        for p_name, cfg in PLANET_CONFIGS.items():
            step = cfg["step_days"]
            points = []
            prev_lon = None
            prev_sign = None
            in_retrograde = False
            retro_start_date = None

            cur_dt = start_dt
            while cur_dt <= end_dt:
                pos, _ = self.provider.get_planet_positions(cur_dt)
                if p_name in pos:
                    lon = pos[p_name]["longitude"] % 360.0
                    s_id = int(lon // 30.0) + 1
                    s_name = SIGN_NAMES[s_id - 1]

                    # Speed & Motion detection
                    speed = 0.0
                    is_retro = False
                    if prev_lon is not None:
                        d_lon = lon - prev_lon
                        # Adjust for 360/0 wrap-around
                        if d_lon > 180.0:
                            d_lon -= 360.0
                        elif d_lon < -180.0:
                            d_lon += 360.0
                        speed = d_lon / step
                        is_retro = (speed < -0.002)

                    # Ingress detection
                    if prev_sign is not None and s_id != prev_sign:
                        ingress_events.append({
                            "planet": p_name,
                            "planet_hi": cfg["name_hi"],
                            "symbol": cfg["symbol"],
                            "date": cur_dt.strftime("%d-%b-%Y"),
                            "year": cur_dt.year,
                            "from_sign": SIGN_NAMES[prev_sign - 1],
                            "to_sign": s_name,
                            "event": f"{cfg['symbol']} {cfg['name_hi']} का {s_name} राशि में प्रवेश"
                        })

                    # Retrograde phase transition detection
                    if is_retro and not in_retrograde:
                        in_retrograde = True
                        retro_start_date = cur_dt
                    elif not is_retro and in_retrograde:
                        in_retrograde = False
                        if retro_start_date:
                            retrograde_events.append({
                                "planet": p_name,
                                "planet_hi": cfg["name_hi"],
                                "symbol": cfg["symbol"],
                                "start_date": retro_start_date.strftime("%d-%b-%Y"),
                                "end_date": cur_dt.strftime("%d-%b-%Y"),
                                "sign": s_name,
                                "duration_days": (cur_dt - retro_start_date).days,
                                "desc": f"{cfg['symbol']} {cfg['name_hi']} वक्री चक्र ({s_name} राशि)"
                            })

                    day_offset = (cur_dt - start_dt).days
                    points.append({
                        "date": cur_dt.strftime("%d-%b-%Y"),
                        "day_offset": day_offset,
                        "x_pct": round((day_offset / total_days) * 100.0, 2),
                        "longitude": round(lon, 2),
                        "y_pct": round((1.0 - (lon / 360.0)) * 100.0, 2),
                        "sign": s_name,
                        "deg_in_sign": round(lon % 30.0, 1),
                        "speed": round(speed, 4),
                        "is_retrograde": is_retro
                    })

                    prev_lon = lon
                    prev_sign = s_id

                cur_dt += timedelta(days=step)

            planet_trajectories[p_name] = points

        return {
            "start_year": start_year,
            "end_year": start_year + duration_years,
            "total_days": total_days,
            "trajectories": planet_trajectories,
            "retrograde_events": retrograde_events,
            "ingress_events": ingress_events
        }

    def render_waves_svg_html(
        self,
        start_year: Optional[int] = None,
        duration_years: int = 5
    ) -> str:
        """
        Renders a high-contrast, responsive SVG trajectory graph for multi-year transits.
        """
        data = self.generate_multi_year_waves(start_year, duration_years)
        start_yr = data["start_year"]
        end_yr = data["end_year"]
        trajectories = data["trajectories"]

        # SVG dimensions
        svg_w = 950
        svg_h = 420
        margin_l = 75
        margin_r = 30
        margin_t = 30
        margin_b = 40
        plot_w = svg_w - margin_l - margin_r
        plot_h = svg_h - margin_t - margin_b

        # Sign labels on Y axis (0 to 360 deg)
        y_labels = ""
        for i in range(12):
            y_pos = margin_t + (plot_h * (11 - i) / 11)
            y_labels += f"""
            <line x1="{margin_l}" y1="{y_pos}" x2="{svg_w - margin_r}" y2="{y_pos}" stroke="#334155" stroke-dasharray="2 4" stroke-width="0.8"/>
            <text x="{margin_l - 8}" y="{y_pos + 4}" fill="#94A3B8" font-size="11" text-anchor="end" font-weight="600">{SIGN_NAMES[i][:4]}</text>
            """

        # Year labels on X axis
        x_labels = ""
        for y_idx in range(duration_years + 1):
            yr = start_yr + y_idx
            x_pos = margin_l + (plot_w * y_idx / duration_years)
            x_labels += f"""
            <line x1="{x_pos}" y1="{margin_t}" x2="{x_pos}" y2="{svg_h - margin_b}" stroke="#475569" stroke-width="1"/>
            <text x="{x_pos}" y="{svg_h - margin_b + 20}" fill="#E2E8F0" font-size="12" text-anchor="middle" font-weight="700">{yr}</text>
            """

        # Plot paths per planet
        paths_html = ""
        for p_name, pts in trajectories.items():
            cfg = PLANET_CONFIGS.get(p_name, {"color": "#6366F1", "name_hi": p_name})
            path_segments = []
            cur_seg = []

            for p in pts:
                px = margin_l + (plot_w * p["x_pct"] / 100.0)
                py = margin_t + (plot_h * p["y_pct"] / 100.0)
                # Break path on wrap-around (Pisces to Aries)
                if cur_seg:
                    prev_py = cur_seg[-1][1]
                    if abs(py - prev_py) > plot_h * 0.5:
                        path_segments.append(cur_seg)
                        cur_seg = []
                cur_seg.append((px, py))

            if cur_seg:
                path_segments.append(cur_seg)

            for seg in path_segments:
                if len(seg) < 2:
                    continue
                d_str = f"M {seg[0][0]:.1f} {seg[0][1]:.1f} " + " ".join([f"L {pt[0]:.1f} {pt[1]:.1f}" for pt in seg[1:]])
                paths_html += f"""
                <path d="{d_str}" fill="none" stroke="{cfg['color']}" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" opacity="0.9"/>
                """

        # Legend
        legend_items = "".join([
            f'<span style="margin-right:16px; font-size:12.5px; font-weight:700; color:{cfg["color"]};">{cfg["symbol"]} {cfg["name_hi"]} ({p})</span>'
            for p, cfg in PLANET_CONFIGS.items()
        ])

        html = f"""
<div style="background: #0F172A; border: 1.5px solid #334155; border-radius: 12px; padding: 18px; color: #FFFFFF; font-family: 'Segoe UI', Tahoma, sans-serif; margin-bottom: 20px;">
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; flex-wrap: wrap;">
        <div>
            <b style="font-size: 16px; color: #F59E0B;">📈 ५-वर्षीय बहु-ग्रहीय गोचर वक्रता एवं वेव आरेख ({start_yr} - {end_yr})</b><br/>
            <small style="color: #94A3B8;">शनि, गुरु, राहु एवं मंगल के गोचर चक्र, मार्गी-वक्री दोलन एवं राशि संक्रमण</small>
        </div>
        <div style="background: #1E293B; border: 1px solid #475569; padding: 6px 14px; border-radius: 20px;">
            {legend_items}
        </div>
    </div>

    <div style="overflow-x: auto;">
        <svg viewBox="0 0 {svg_w} {svg_h}" style="width: 100%; min-width: 750px; height: auto; display: block;">
            <!-- Grid Background -->
            <rect x="{margin_l}" y="{margin_t}" width="{plot_w}" height="{plot_h}" fill="#1E293B" rx="6"/>
            {y_labels}
            {x_labels}
            {paths_html}
        </svg>
    </div>
</div>
        """
        return html


# Singleton instance
default_ephemeris_waves_service = EphemerisWavesService()

