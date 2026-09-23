"""
Dynamic Planetary Speed and Transit Wave Service for JyotishOS.
Calculates daily planetary velocities, stationary points (retrograde/direct transitions),
Atichara (accelerated motion), and Manda (retarded motion) curves matching Shri Jyoti Star & Jagannatha Hora.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, date, timedelta, timezone
from ..core.ephemeris import PyEphemProvider
from ..core.constants import SIGN_NAMES

PLANET_COLORS = {
    "Sun": "#EA580C",       # Deep Orange
    "Moon": "#0284C7",      # Sky Blue
    "Mars": "#DC2626",      # Bright Red
    "Mercury": "#16A34A",   # Emerald Green
    "Jupiter": "#D97706",   # Amber / Gold
    "Venus": "#DB2777",     # Pink / Magenta
    "Saturn": "#475569",    # Slate Grey
    "Rahu": "#7C3AED",      # Violet / Purple
}

PLANET_NAMES_HI = {
    "Sun": "सूर्य (Sun)",
    "Moon": "चन्द्र (Moon)",
    "Mars": "मंगल (Mars)",
    "Mercury": "बुध (Mercury)",
    "Jupiter": "गुरु (Jupiter)",
    "Venus": "शुक्र (Venus)",
    "Saturn": "शनि (Saturn)",
    "Rahu": "राहु (Rahu)",
}

# Classical Average Speeds (degrees per day)
MEAN_SPEEDS = {
    "Sun": 0.9856,
    "Moon": 13.176,
    "Mars": 0.524,
    "Mercury": 1.383,
    "Jupiter": 0.083,
    "Venus": 1.200,
    "Saturn": 0.033,
    "Rahu": -0.0529,
}


class TransitGraphService:
    """Calculates dynamic transit velocities and retrograde turning points."""

    def __init__(self):
        self.provider = PyEphemProvider()

    def calculate_speed_timeline(
        self,
        start_date: date,
        days: int = 90,
        step_days: int = 2,
        planet_names: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Calculates daily velocities for specified planets over a date range.
        Detects zero-crossing stationary points (retrograde/direct shifts).
        """
        if planet_names is None:
            planet_names = ["Mars", "Mercury", "Jupiter", "Venus", "Saturn"]

        timeline_points: List[Dict[str, Any]] = []
        turning_points: List[Dict[str, Any]] = []

        curr_dt = datetime.combine(start_date, datetime.min.time()).replace(tzinfo=timezone.utc)
        total_steps = max(1, days // step_days)

        prev_speeds: Dict[str, float] = {}

        for step in range(total_steps + 1):
            dt_step = curr_dt + timedelta(days=step * step_days)
            date_str = dt_step.strftime("%d %b %Y")
            iso_date = dt_step.strftime("%Y-%m-%d")

            positions, _ = self.provider.get_planet_positions(dt_step)

            pt_entry = {
                "date_str": date_str,
                "iso_date": iso_date,
                "day_offset": step * step_days,
                "speeds": {},
                "longitudes": {},
                "retrogrades": {}
            }

            for p in planet_names:
                if p in positions:
                    spd = float(positions[p].get("speed", 0.0))
                    lon = float(positions[p].get("longitude", 0.0))
                    retro = bool(positions[p].get("is_retrograde", False))

                    pt_entry["speeds"][p] = round(spd, 4)
                    pt_entry["longitudes"][p] = round(lon, 2)
                    pt_entry["retrogrades"][p] = retro

                    # Detect zero-crossing (turning point)
                    if p in prev_speeds:
                        prev_spd = prev_speeds[p]
                        if (prev_spd > 0 and spd < 0) or (prev_spd < 0 and spd > 0):
                            shift_type = "वक्र गति प्रारंभ (Turned Retrograde)" if spd < 0 else "मार्गी गति प्रारंभ (Turned Direct)"
                            s_idx = int(lon // 30.0)
                            sign_name = SIGN_NAMES[s_idx % 12]
                            deg_in_sign = lon % 30.0

                            turning_points.append({
                                "planet": p,
                                "planet_hi": PLANET_NAMES_HI.get(p, p),
                                "date": date_str,
                                "shift_type": shift_type,
                                "sign": sign_name,
                                "degree_str": f"{int(deg_in_sign)}° {int((deg_in_sign % 1)*60)}'",
                                "speed": round(spd, 4)
                            })

                    prev_speeds[p] = spd

            timeline_points.append(pt_entry)

        # Current planetary speed status analysis
        current_status = {}
        if timeline_points:
            today_entry = timeline_points[0]
            for p in planet_names:
                spd = today_entry["speeds"].get(p, 0.0)
                mean_spd = MEAN_SPEEDS.get(p, 1.0)
                retro = today_entry["retrogrades"].get(p, False)
                lon = today_entry["longitudes"].get(p, 0.0)

                s_idx = int(lon // 30.0)
                sign_name = SIGN_NAMES[s_idx % 12]

                if retro or spd < 0:
                    status = "वक्र (Retrograde)"
                    badge_color = "#DC2626"
                elif abs(spd) < 0.15 * abs(mean_spd):
                    status = "स्तम्भी (Stationary / Turning)"
                    badge_color = "#D97706"
                elif spd > 1.25 * mean_spd:
                    status = "अतिचारी (Accelerated / Fast)"
                    badge_color = "#16A34A"
                elif spd < 0.75 * mean_spd:
                    status = "मन्द (Slow / Retarded)"
                    badge_color = "#2563EB"
                else:
                    status = "सामान्य मार्गी (Normal Direct)"
                    badge_color = "#475569"

                current_status[p] = {
                    "planet_hi": PLANET_NAMES_HI.get(p, p),
                    "speed": spd,
                    "mean_speed": mean_spd,
                    "ratio": round(spd / mean_spd, 2) if mean_spd != 0 else 1.0,
                    "sign": sign_name,
                    "status": status,
                    "badge_color": badge_color
                }

        return {
            "start_date": str(start_date),
            "days": days,
            "planet_names": planet_names,
            "timeline": timeline_points,
            "turning_points": turning_points,
            "current_status": current_status
        }

    @classmethod
    def render_speed_svg(cls, timeline_data: Dict[str, Any], width: int = 860, height: int = 420) -> str:
        """Renders an SVG graph of planetary speed curves with zero-line and date axis."""
        timeline = timeline_data.get("timeline", [])
        if not timeline or len(timeline) < 2:
            return "<div style='color:red;'>पर्याप्त डेटा नहीं है।</div>"

        planets = timeline_data.get("planet_names", [])
        turning_points = timeline_data.get("turning_points", [])

        pad_left, pad_right, pad_top, pad_bot = 65, 40, 45, 60
        plot_w = width - pad_left - pad_right
        plot_h = height - pad_top - pad_bot

        # Find min and max speeds
        all_speeds = []
        for pt in timeline:
            for p, spd in pt["speeds"].items():
                all_speeds.append(spd)

        min_spd = min(all_speeds) if all_speeds else -0.5
        max_spd = max(all_speeds) if all_speeds else 1.5

        # Add padding to range
        spd_range = max(0.1, max_spd - min_spd)
        min_y = min_spd - 0.1 * spd_range
        max_y = max_spd + 0.1 * spd_range
        total_range = max_y - min_y

        def y_coord(val: float) -> float:
            return pad_top + plot_h - ((val - min_y) / total_range * plot_h)

        def x_coord(idx: int) -> float:
            return pad_left + (idx / (len(timeline) - 1)) * plot_w

        zero_y = y_coord(0.0)

        svg = [
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="100%" height="{height}" style="background:#FFFFFF; border:1.5px solid #CBD5E1; border-radius:12px; box-shadow:0 4px 12px rgba(0,0,0,0.05); font-family:-apple-system,BlinkMacSystemFont,sans-serif;">',
            f'<rect width="{width}" height="38" fill="#0F172A" rx="12 12 0 0"/>',
            f'<text x="{width//2}" y="24" text-anchor="middle" fill="#F8FAFC" font-size="14" font-weight="800">📊 डायनेमिक गोचर गति व वक्रता वक्र (Planetary Speed & Retrograde Curves — {timeline_data.get("days", 90)} Days)</text>',
            # Plot background
            f'<rect x="{pad_left}" y="{pad_top}" width="{plot_w}" height="{plot_h}" fill="#F8FAFC" rx="4" stroke="#E2E8F0"/>',
        ]

        # Horizontal Zero line (Retrograde vs Direct threshold)
        if pad_top <= zero_y <= pad_top + plot_h:
            svg.append(f'<line x1="{pad_left}" y1="{zero_y}" x2="{pad_left + plot_w}" y2="{zero_y}" stroke="#EF4444" stroke-width="2" stroke-dasharray="4 4"/>')
            svg.append(f'<text x="{pad_left + 8}" y="{zero_y - 6}" fill="#DC2626" font-size="10.5" font-weight="800">०°/दिन संधिकाल (Zero-Speed Line: ऊपर मार्गी ⬆ | नीचे वक्री ⬇)</text>')

        # Grid lines and Y-axis labels
        num_y_ticks = 5
        for i in range(num_y_ticks + 1):
            val = min_y + (i / num_y_ticks) * total_range
            y_pos = y_coord(val)
            if pad_top <= y_pos <= pad_top + plot_h:
                svg.append(f'<line x1="{pad_left}" y1="{y_pos}" x2="{pad_left + plot_w}" y2="{y_pos}" stroke="#E2E8F0" stroke-width="1"/>')
                svg.append(f'<text x="{pad_left - 8}" y="{y_pos + 4}" text-anchor="end" fill="#64748B" font-size="10">{val:.2f}°</text>')

        # Date X-axis labels
        num_x_ticks = min(6, len(timeline))
        step_idx = len(timeline) // num_x_ticks
        for i in range(0, len(timeline), max(1, step_idx)):
            x_pos = x_coord(i)
            dt_label = timeline[i]["date_str"]
            svg.append(f'<line x1="{x_pos}" y1="{pad_top + plot_h}" x2="{x_pos}" y2="{pad_top + plot_h + 6}" stroke="#94A3B8" stroke-width="1.5"/>')
            svg.append(f'<text x="{x_pos}" y="{pad_top + plot_h + 20}" text-anchor="middle" fill="#475569" font-size="10" font-weight="600">{dt_label}</text>')

        # Plot curves for each planet
        for p in planets:
            color = PLANET_COLORS.get(p, "#3B82F6")
            points = []
            for idx, pt in enumerate(timeline):
                if p in pt["speeds"]:
                    x = x_coord(idx)
                    y = y_coord(pt["speeds"][p])
                    points.append(f"{x:.1f},{y:.1f}")

            if points:
                poly_pts = " ".join(points)
                svg.append(f'<polyline fill="none" stroke="{color}" stroke-width="2.6" points="{poly_pts}"/>')

        # Legend at bottom
        leg_x = pad_left
        leg_y = height - 14
        for p in planets:
            color = PLANET_COLORS.get(p, "#3B82F6")
            p_hi = PLANET_NAMES_HI.get(p, p).split(" ")[0]
            svg.append(f'<circle cx="{leg_x}" cy="{leg_y}" r="5" fill="{color}"/>')
            svg.append(f'<text x="{leg_x + 9}" y="{leg_y + 4}" fill="#1E293B" font-size="11" font-weight="700">{p_hi}</text>')
            leg_x += 105

        svg.append('</svg>')
        return "".join(svg)


default_transit_graph_service = TransitGraphService()
