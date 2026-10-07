"""
Visual Multi-Tier Dasha Gantt Timeline Service for JyotishOS.
Generates interactive, proportional 120-year Vimshottari Gantt timelines
with Mahadasha, Antardasha, and Pratyantardasha tiers, along with a live
'TODAY' marker indicating native's exact life coordinates.
"""

from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional
try:
    from ..core.models import KundaliChart
    from ..core.constants import SIGN_NAMES, SIGN_LORDS
    from ..dasha.vimshottari import default_dasha_engine
    from ..dasha.yogini import default_yogini_engine
    from ..dasha.chara import default_chara_engine
    from ..dasha.kcd import default_kcd_engine
except (ImportError, ValueError):
    from src.jyotish.core.models import KundaliChart
    from src.jyotish.core.constants import SIGN_NAMES, SIGN_LORDS
    from src.jyotish.dasha.vimshottari import default_dasha_engine
    from src.jyotish.dasha.yogini import default_yogini_engine
    from src.jyotish.dasha.chara import default_chara_engine
    from src.jyotish.dasha.kcd import default_kcd_engine


PLANET_THEME = {
    "Sun": {"name_hi": "सूर्य", "color": "#EAB308", "bg": "#FEF9C3", "border": "#CA8A04", "symbol": "☀️"},
    "Moon": {"name_hi": "चन्द्र", "color": "#64748B", "bg": "#F1F5F9", "border": "#475569", "symbol": "🌙"},
    "Mars": {"name_hi": "मंगल", "color": "#EF4444", "bg": "#FEE2E2", "border": "#DC2626", "symbol": "♂️"},
    "Rahu": {"name_hi": "राहु", "color": "#334155", "bg": "#E2E8F0", "border": "#1E293B", "symbol": "☊"},
    "Jupiter": {"name_hi": "गुरु", "color": "#D97706", "bg": "#FEF3C7", "border": "#B45309", "symbol": "♃"},
    "Saturn": {"name_hi": "शनि", "color": "#2563EB", "bg": "#DBEAFE", "border": "#1D4ED8", "symbol": "🪐"},
    "Mercury": {"name_hi": "बुध", "color": "#059669", "bg": "#D1FAE5", "border": "#047857", "symbol": "☿"},
    "Ketu": {"name_hi": "केतु", "color": "#7C3AED", "bg": "#EDE9FE", "border": "#6D28D9", "symbol": "☋"},
    "Venus": {"name_hi": "शुक्र", "color": "#DB2777", "bg": "#FCE7F3", "border": "#BE185D", "symbol": "♀️"},
}


class DashaTimelineService:
    """Renders visual Gantt charts and timelines for Vimshottari Dasha."""

    def __init__(self, dasha_engine=None):
        self.engine = dasha_engine or default_dasha_engine

    def render_gantt_html(
        self,
        chart: KundaliChart,
        target_date: Optional[date] = None,
        selected_maha_idx: Optional[int] = None,
        theme_mode: str = "day"
    ) -> str:
        """
        Generates responsive HTML/CSS Gantt timeline with:
        - Top active Dasha status dashboard
        - Proportional 120-year Mahadasha Gantt bar
        - Expandable Antardasha breakdown for active/selected Mahadasha
        - Active Antardasha's Pratyantardasha breakdown
        - Glowing 'TODAY' indicator line with exact percentage progress
        - Supports Day Mode (Pearl White) and Night/Astrallis Mode
        """
        if target_date is None:
            target_date = date.today()

        birth_dt = datetime.combine(chart.birth_data.birth_date, chart.birth_data.birth_time)
        target_dt = datetime.combine(target_date, datetime.min.time())

        # Generate Mahadashas (covers full 120y cycle)
        mahadashas = self.engine.generate_timeline(chart)
        if not mahadashas:
            return "<div style='color:red;'>दशा समय गणना उपलब्ध नहीं है।</div>"

        timeline_start = mahadashas[0]["start_date"]
        timeline_end = mahadashas[-1]["end_date"]
        total_days = max(1.0, (timeline_end - timeline_start).total_seconds() / 86400.0)

        # Active Dasha hierarchy
        try:
            active_hier = self.engine.get_active_hierarchy(chart, target_date)
            active_m_lord = active_hier.mahadasha.lord
            active_a_lord = active_hier.antardasha.lord
            active_p_lord = active_hier.pratyantardasha.lord
        except Exception:
            active_hier = None
            active_m_lord = mahadashas[0]["lord"]
            active_a_lord = "Sun"
            active_p_lord = "Sun"

        # Determine which Mahadasha is currently active or selected
        active_m_idx = 0
        for idx, m in enumerate(mahadashas):
            if m["start_date"] <= target_dt <= m["end_date"]:
                active_m_idx = idx
                break

        display_m_idx = selected_maha_idx if (selected_maha_idx is not None and 0 <= selected_maha_idx < len(mahadashas)) else active_m_idx
        display_m = mahadashas[display_m_idx]

        # Calculate TODAY position in full 120y cycle
        today_days = (target_dt - timeline_start).total_seconds() / 86400.0
        today_pct = max(0.0, min(100.0, (today_days / total_days) * 100.0))

        # Calculate progress within active Mahadasha
        active_m = mahadashas[active_m_idx]
        active_m_span = max(1.0, (active_m["end_date"] - active_m["start_date"]).total_seconds() / 86400.0)
        active_m_elapsed = max(0.0, min(active_m_span, (target_dt - active_m["start_date"]).total_seconds() / 86400.0))
        active_m_pct = (active_m_elapsed / active_m_span) * 100.0

        # Generate Antardashas for the display Mahadasha
        antardashas = self.engine.generate_antardashas(
            display_m["lord"],
            display_m["start_date"],
            display_m["end_date"]
        )

        # Find active Antardasha within display Mahadasha (if display_m is active)
        active_a_idx = -1
        if display_m_idx == active_m_idx:
            for idx, a in enumerate(antardashas):
                if a["start_date"] <= target_dt <= a["end_date"]:
                    active_a_idx = idx
                    break

        # Calculate TODAY position inside display Mahadasha
        m_display_span = max(1.0, (display_m["end_date"] - display_m["start_date"]).total_seconds() / 86400.0)
        m_today_elapsed = (target_dt - display_m["start_date"]).total_seconds() / 86400.0
        m_today_pct = (m_today_elapsed / m_display_span) * 100.0 if (display_m_idx == active_m_idx) else -1.0

        # Generate Pratyantardashas if active Antardasha exists
        pratyantardashas = []
        active_p_idx = -1
        p_today_pct = -1.0
        if active_a_idx >= 0 and active_a_idx < len(antardashas):
            active_a = antardashas[active_a_idx]
            pratyantardashas = self.engine.generate_pratyantardashas(
                display_m["lord"],
                active_a["lord"],
                active_a["start_date"],
                active_a["end_date"]
            )
            for idx, p in enumerate(pratyantardashas):
                if p["start_date"] <= target_dt <= p["end_date"]:
                    active_p_idx = idx
                    break
            a_span = max(1.0, (active_a["end_date"] - active_a["start_date"]).total_seconds() / 86400.0)
            a_today_elapsed = (target_dt - active_a["start_date"]).total_seconds() / 86400.0
            p_today_pct = max(0.0, min(100.0, (a_today_elapsed / a_span) * 100.0))

        # Native's age calculation
        years_age = round((target_dt - birth_dt).days / 365.2425, 1)

        # ---------------- HTML Construction ----------------
        # 1. Tier 1: Mahadasha Gantt Blocks
        m_blocks_html = ""
        for idx, m in enumerate(mahadashas):
            dur_days = (m["end_date"] - m["start_date"]).total_seconds() / 86400.0
            width_pct = (dur_days / total_days) * 100.0
            lord = m["lord"]
            theme = PLANET_THEME.get(lord, {"name_hi": lord, "color": "#6366F1", "bg": "#EEF2FF", "border": "#4F46E5", "symbol": "🪐"})
            is_active = (idx == active_m_idx)
            is_selected = (idx == display_m_idx)

            active_border = "border: 2.5px solid #F59E0B; box-shadow: 0 0 10px rgba(245, 158, 11, 0.6);" if is_active else "border: 1px solid rgba(255,255,255,0.4);"
            active_badge = "<span style='position:absolute; top:2px; right:4px; font-size:10px; background:#F59E0B; color:#000; padding:1px 4px; border-radius:4px; font-weight:900;'>सक्रिय</span>" if is_active else ""

            s_yr = m["start_date"].strftime("%Y")
            e_yr = m["end_date"].strftime("%Y")

            m_blocks_html += f"""
            <div style="flex: 0 0 {width_pct:.2f}%; min-width: 48px; background: {theme['color']}; color: #FFFFFF; position: relative; {active_border} padding: 6px 4px; box-sizing: border-box; display: flex; flex-direction: column; justify-content: center; align-items: center; cursor: pointer; transition: transform 0.15s ease;"
                 title="{theme['name_hi']} ({lord}) महादशा: {m['start_date'].strftime('%d-%m-%Y')} से {m['end_date'].strftime('%d-%m-%Y')} ({m['duration_years']:.1f} वर्ष)">
                {active_badge}
                <div style="font-weight: 800; font-size: 13px; text-shadow: 0 1px 2px rgba(0,0,0,0.4);">{theme['symbol']} {theme['name_hi']}</div>
                <div style="font-size: 10px; opacity: 0.9; margin-top: 2px;">{m['duration_years']:.1f}व</div>
                <div style="font-size: 9px; opacity: 0.8; margin-top: 1px;">{s_yr}-{e_yr}</div>
            </div>
            """

        # 2. Tier 2: Antardasha Blocks
        a_blocks_html = ""
        for idx, a in enumerate(antardashas):
            dur_days = (a["end_date"] - a["start_date"]).total_seconds() / 86400.0
            width_pct = (dur_days / m_display_span) * 100.0
            lord = a["lord"]
            theme = PLANET_THEME.get(lord, {"name_hi": lord, "color": "#6366F1", "bg": "#EEF2FF", "border": "#4F46E5", "symbol": "🪐"})
            is_active = (idx == active_a_idx)

            active_border = "border: 2px solid #EF4444; box-shadow: 0 0 8px rgba(239, 68, 68, 0.6);" if is_active else "border: 1px solid rgba(255,255,255,0.3);"
            active_badge = "<span style='position:absolute; top:2px; right:3px; font-size:9px; background:#EF4444; color:#FFF; padding:1px 3px; border-radius:3px; font-weight:800;'>आज</span>" if is_active else ""

            s_date = a["start_date"].strftime("%d/%m/%y")
            e_date = a["end_date"].strftime("%d/%m/%y")

            a_blocks_html += f"""
            <div style="flex: 0 0 {width_pct:.2f}%; min-width: 44px; background: {theme['color']}; color: #FFFFFF; position: relative; {active_border} padding: 6px 3px; box-sizing: border-box; display: flex; flex-direction: column; justify-content: center; align-items: center;"
                 title="{display_m['lord']}-{lord} अंतर्दशा: {a['start_date'].strftime('%d-%m-%Y')} से {a['end_date'].strftime('%d-%m-%Y')}">
                {active_badge}
                <div style="font-weight: 700; font-size: 12px; text-shadow: 0 1px 2px rgba(0,0,0,0.4);">{theme['name_hi']}</div>
                <div style="font-size: 9.5px; opacity: 0.9; margin-top: 1px;">{round(dur_days/30.4, 1)}मा</div>
                <div style="font-size: 8.5px; opacity: 0.8;">{s_date}</div>
            </div>
            """

        # 3. Tier 3: Pratyantardasha Blocks
        p_blocks_html = ""
        if pratyantardashas and active_a_idx >= 0:
            active_a = antardashas[active_a_idx]
            a_total_days = max(1.0, (active_a["end_date"] - active_a["start_date"]).total_seconds() / 86400.0)
            for idx, p in enumerate(pratyantardashas):
                dur_days = (p["end_date"] - p["start_date"]).total_seconds() / 86400.0
                width_pct = (dur_days / a_total_days) * 100.0
                lord = p["lord"]
                theme = PLANET_THEME.get(lord, {"name_hi": lord, "color": "#6366F1", "bg": "#EEF2FF", "border": "#4F46E5", "symbol": "🪐"})
                is_active = (idx == active_p_idx)

                active_border = "border: 2px solid #10B981; box-shadow: 0 0 6px rgba(16, 185, 129, 0.7);" if is_active else "border: 1px solid rgba(255,255,255,0.25);"
                active_badge = "★" if is_active else ""

                p_blocks_html += f"""
                <div style="flex: 0 0 {width_pct:.2f}%; min-width: 32px; background: {theme['color']}; color: #FFFFFF; position: relative; {active_border} padding: 4px 2px; box-sizing: border-box; display: flex; flex-direction: column; justify-content: center; align-items: center;"
                     title="{display_m['lord']}-{antardashas[active_a_idx]['lord']}-{lord} प्रत्यन्तर्दशा: {p['start_date'].strftime('%d-%m-%Y')} से {p['end_date'].strftime('%d-%m-%Y')}">
                    <div style="font-weight: 700; font-size: 11px;">{active_badge} {theme['name_hi'][:2]}</div>
                    <div style="font-size: 8.5px; opacity: 0.9;">{round(dur_days, 0):.0f}दिन</div>
                </div>
                """

        # Today marker HTML for Tier 1
        today_marker_t1 = f"""
        <div style="position: absolute; left: {today_pct:.2f}%; top: -8px; bottom: -8px; width: 3px; background: #EF4444; z-index: 20; box-shadow: 0 0 10px #EF4444, 0 0 4px #FFFFFF; pointer-events: none;">
            <div style="position: absolute; top: -20px; left: 50%; transform: translateX(-50%); background: #EF4444; color: #FFFFFF; font-size: 10px; font-weight: 800; padding: 2px 6px; border-radius: 4px; white-space: nowrap; box-shadow: 0 2px 4px rgba(0,0,0,0.2);">
                📍 आज ({target_date.strftime('%d-%b-%Y')})
            </div>
        </div>
        """

        # Today marker for Tier 2 (if display_m is active)
        today_marker_t2 = ""
        if m_today_pct >= 0.0 and m_today_pct <= 100.0:
            today_marker_t2 = f"""
            <div style="position: absolute; left: {m_today_pct:.2f}%; top: -6px; bottom: -6px; width: 3px; background: #EF4444; z-index: 20; box-shadow: 0 0 8px #EF4444; pointer-events: none;">
                <div style="position: absolute; top: -18px; left: 50%; transform: translateX(-50%); background: #EF4444; color: #FFFFFF; font-size: 9px; font-weight: 800; padding: 1px 5px; border-radius: 3px; white-space: nowrap;">
                    📍 आज
                </div>
            </div>
            """

        # Today marker for Tier 3
        today_marker_t3 = ""
        if p_today_pct >= 0.0 and p_today_pct <= 100.0:
            today_marker_t3 = f"""
            <div style="position: absolute; left: {p_today_pct:.2f}%; top: -4px; bottom: -4px; width: 2.5px; background: #10B981; z-index: 20; box-shadow: 0 0 6px #10B981; pointer-events: none;"></div>
            """

        active_m_theme = PLANET_THEME.get(active_m_lord, {"name_hi": active_m_lord, "color": "#EAB308", "symbol": "☀️"})
        active_a_theme = PLANET_THEME.get(active_a_lord, {"name_hi": active_a_lord, "color": "#3B82F6", "symbol": "🪐"})
        active_p_theme = PLANET_THEME.get(active_p_lord, {"name_hi": active_p_lord, "color": "#10B981", "symbol": "☿"})

        is_day = (theme_mode.lower() == "day")

        # Color tokens based on theme
        main_bg = "#FFFFFF" if is_day else "#0F172A"
        main_border = "#CBD5E1" if is_day else "#334155"
        main_color = "#0F172A" if is_day else "#F8FAFC"
        main_shadow = "0 4px 16px rgba(15, 23, 42, 0.08)" if is_day else "0 8px 24px rgba(0,0,0,0.25)"

        hud_bg = "#F8FAFC" if is_day else "rgba(30, 41, 59, 0.85)"
        hud_label_color = "#475569" if is_day else "#94A3B8"
        hud_sub_color = "#334155" if is_day else "#CBD5E1"
        hud_strong_color = "#0F172A" if is_day else "#F8FAFC"
        hud_progress_bg = "#E2E8F0" if is_day else "#334155"

        t1_title_color = "#0F172A" if is_day else "#E2E8F0"
        t1_sub_color = "#475569" if is_day else "#94A3B8"
        t1_bar_shadow = "inset 0 1px 3px rgba(0,0,0,0.15)" if is_day else "inset 0 2px 4px rgba(0,0,0,0.4)"

        tier2_bg = "#F8FAFC" if is_day else "rgba(30, 41, 59, 0.6)"
        tier2_border = "#CBD5E1" if is_day else "#334155"
        tier2_title = "#B45309" if is_day else "#F59E0B"

        tier3_bg = "#F1F5F9" if is_day else "rgba(30, 41, 59, 0.4)"
        tier3_border = "#94A3B8" if is_day else "#475569"
        tier3_title = "#047857" if is_day else "#10B981"

        html = f"""
<div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: {main_bg}; color: {main_color}; border: 1.5px solid {main_border}; border-radius: 14px; padding: 20px; box-shadow: {main_shadow}; margin-bottom: 20px;">
    
    <!-- Top Active Dasha HUD -->
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 14px; margin-bottom: 22px;">
        <div style="background: {hud_bg}; border: 1.5px solid {active_m_theme['color']}; border-radius: 10px; padding: 12px 14px;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="font-size: 11.5px; text-transform: uppercase; letter-spacing: 0.5px; color: {hud_label_color}; font-weight: 700;">सक्रिय महादशा (Tier 1)</span>
                <span style="font-size: 18px;">{active_m_theme['symbol']}</span>
            </div>
            <div style="font-size: 20px; font-weight: 900; color: {active_m_theme['color']}; margin: 4px 0 2px 0;">
                {active_m_theme['name_hi']} ({active_m_lord})
            </div>
            <div style="font-size: 11.5px; color: {hud_sub_color};">
                {active_m['start_date'].strftime('%d %b %Y')} → {active_m['end_date'].strftime('%d %b %Y')}
            </div>
            <div style="margin-top: 8px;">
                <div style="display: flex; justify-content: space-between; font-size: 11px; margin-bottom: 3px; color: {hud_label_color};">
                    <span>प्रगति: {active_m_pct:.1f}%</span>
                    <span>शेष: {100.0 - active_m_pct:.1f}%</span>
                </div>
                <div style="background: {hud_progress_bg}; border-radius: 4px; height: 6px; overflow: hidden;">
                    <div style="background: {active_m_theme['color']}; width: {active_m_pct:.1f}%; height: 100%;"></div>
                </div>
            </div>
        </div>

        <div style="background: {hud_bg}; border: 1.5px solid {active_a_theme['color']}; border-radius: 10px; padding: 12px 14px;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="font-size: 11.5px; text-transform: uppercase; letter-spacing: 0.5px; color: {hud_label_color}; font-weight: 700;">सक्रिय अंतर्दशा (Tier 2)</span>
                <span style="font-size: 18px;">{active_a_theme['symbol']}</span>
            </div>
            <div style="font-size: 20px; font-weight: 900; color: {active_a_theme['color']}; margin: 4px 0 2px 0;">
                {active_m_theme['name_hi']}-{active_a_theme['name_hi']} ({active_a_lord})
            </div>
            <div style="font-size: 11.5px; color: {hud_sub_color};">
                {active_hier.antardasha.start_date.strftime('%d %b %Y') if active_hier else ''} → {active_hier.antardasha.end_date.strftime('%d %b %Y') if active_hier else ''}
            </div>
            <div style="font-size: 11px; color: {hud_label_color}; margin-top: 8px;">
                वर्तमान आयु: <b style="color: {hud_strong_color};">{years_age} वर्ष</b> | चक्र प्रगति: <b style="color: {hud_strong_color};">{today_pct:.1f}%</b>
            </div>
        </div>

        <div style="background: {hud_bg}; border: 1.5px solid {active_p_theme['color']}; border-radius: 10px; padding: 12px 14px;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="font-size: 11.5px; text-transform: uppercase; letter-spacing: 0.5px; color: {hud_label_color}; font-weight: 700;">सक्रिय प्रत्यन्तर्दशा (Tier 3)</span>
                <span style="font-size: 18px;">{active_p_theme['symbol']}</span>
            </div>
            <div style="font-size: 18px; font-weight: 800; color: {active_p_theme['color']}; margin: 4px 0 2px 0;">
                {active_m_theme['name_hi']}-{active_a_theme['name_hi']}-{active_p_theme['name_hi']}
            </div>
            <div style="font-size: 11.5px; color: {hud_sub_color};">
                {active_hier.pratyantardasha.start_date.strftime('%d %b %Y') if active_hier else ''} → {active_hier.pratyantardasha.end_date.strftime('%d %b %Y') if active_hier else ''}
            </div>
            <div style="font-size: 11px; color: #047857; margin-top: 8px; font-weight: 700;">
                ✓ सूक्ष्म कालखंड (Point-in-Time Event Precision)
            </div>
        </div>
    </div>

    <!-- Tier 1: 120-Year Full Cycle Gantt Bar -->
    <div style="margin-bottom: 26px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
            <span style="font-size: 13.5px; font-weight: 800; color: {t1_title_color};">
                📊 १२०-वर्षीय सम्पूर्ण महादशा चक्र (Lifetime Vimshottari Cycle)
            </span>
            <span style="font-size: 11.5px; color: {t1_sub_color}; font-weight: 600;">
                जन्म: {timeline_start.strftime('%d-%b-%Y')} • पूर्ण: {timeline_end.strftime('%d-%b-%Y')}
            </span>
        </div>
        
        <div style="position: relative; padding-top: 14px; padding-bottom: 6px;">
            {today_marker_t1}
            <div style="display: flex; width: 100%; border-radius: 8px; overflow: hidden; height: 58px; box-shadow: {t1_bar_shadow};">
                {m_blocks_html}
            </div>
        </div>
        <div style="font-size: 11px; color: #64748B; margin-top: 4px; text-align: right;">
            * प्रत्येक महादशा खंड की चौड़ाई उसकी शास्त्रीय वर्ष अवधि के अनुपात में है
        </div>
    </div>

    <!-- Tier 2: Selected / Active Mahadasha Expanded (Antardashas) -->
    <div style="background: {tier2_bg}; border: 1px solid {tier2_border}; border-radius: 10px; padding: 16px; margin-bottom: 20px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
            <span style="font-size: 13px; font-weight: 800; color: {tier2_title};">
                🔍 महादशा विस्तार (Tier 2 Antardasha Breakdown): {PLANET_THEME.get(display_m['lord'], {}).get('name_hi', display_m['lord'])} महादशा ({display_m['start_date'].strftime('%d-%b-%Y')} से {display_m['end_date'].strftime('%d-%b-%Y')})
            </span>
            <span style="font-size: 11px; color: {t1_sub_color};">
                अवधि: {display_m['duration_years']:.1f} वर्ष
            </span>
        </div>

        <div style="position: relative; padding-top: 10px; padding-bottom: 4px;">
            {today_marker_t2}
            <div style="display: flex; width: 100%; border-radius: 6px; overflow: hidden; height: 48px; box-shadow: {t1_bar_shadow};">
                {a_blocks_html}
            </div>
        </div>
    </div>

    <!-- Tier 3: Active Antardasha Expanded (Pratyantardashas) -->
    {f'''
    <div style="background: {tier3_bg}; border: 1px dashed {tier3_border}; border-radius: 10px; padding: 14px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
            <span style="font-size: 12.5px; font-weight: 800; color: {tier3_title};">
                ⚡ सूक्ष्म प्रत्यन्तर्दशा स्तर (Tier 3 Pratyantardasha Breakdown)
            </span>
            <span style="font-size: 11px; color: {t1_sub_color};">
                दैनिक/साप्ताहिक घटना वेध
            </span>
        </div>
        <div style="position: relative; padding-top: 6px;">
            {today_marker_t3}
            <div style="display: flex; width: 100%; border-radius: 6px; overflow: hidden; height: 38px;">
                {p_blocks_html}
            </div>
        </div>
    </div>
    ''' if p_blocks_html else ''}

</div>
        """
        return html

    def render_multi_dasha_parallel_timeline_html(
        self,
        chart: KundaliChart,
        target_date: Optional[date] = None,
        theme_mode: str = "day"
    ) -> str:
        """
        Renders a synchronized 4-lane parallel visual comparison across:
        1. विंशोत्तरी दशा (Vimshottari 120y)
        2. योगिनी दशा (Yogini 36y cycle)
        3. जैमिनी चर दशा (Jaimini Chara Rashi)
        4. कालचक्र दशा (Kaalachakra KCD)
        Synchronized across 0-100 years with a glowing 'TODAY' indicator line.
        """
        if target_date is None:
            target_date = date.today()

        birth_dt = datetime.combine(chart.birth_data.birth_date, chart.birth_data.birth_time)
        target_dt = datetime.combine(target_date, datetime.min.time())
        timeline_end_dt = birth_dt + timedelta(days=100.0 * 365.2425)
        total_span_days = 100.0 * 365.2425

        today_days = max(0.0, (target_dt - birth_dt).total_seconds() / 86400.0)
        today_pct = max(0.0, min(100.0, (today_days / total_span_days) * 100.0))
        today_age = today_days / 365.2425

        try:
            v_list = self.engine.generate_timeline(chart)
        except Exception:
            v_list = []

        try:
            y_list = default_yogini_engine.generate_timeline(chart)
        except Exception:
            y_list = []

        try:
            c_list = default_chara_engine.generate_timeline(chart)
        except Exception:
            c_list = []

        try:
            k_list = default_kcd_engine.generate_timeline(chart)
        except Exception:
            k_list = []

        is_dark = (theme_mode.lower() in ("night", "dark", "astrallis"))
        bg_card = "#0F172A" if is_dark else "#FFFFFF"
        border_card = "#334155" if is_dark else "#E2E8F0"
        txt_main = "#F8FAFC" if is_dark else "#0F172A"
        txt_sub = "#94A3B8" if is_dark else "#64748B"
        lane_bg = "#1E293B" if is_dark else "#F8FAFC"

        def build_lane_blocks(period_list, lord_key="lord", label_prefix=""):
            blocks = []
            for p in period_list:
                s_dt = p["start_date"]
                e_dt = p["end_date"]
                if e_dt <= birth_dt or s_dt >= timeline_end_dt:
                    continue
                clamped_s = max(birth_dt, s_dt)
                clamped_e = min(timeline_end_dt, e_dt)
                dur_days = (clamped_e - clamped_s).total_seconds() / 86400.0
                if dur_days <= 0:
                    continue
                w_pct = (dur_days / total_span_days) * 100.0

                lord_val = p.get(lord_key, p.get("rashi", "Sun"))
                th = PLANET_THEME.get(lord_val, {"color": "#6366F1", "bg": "#EEF2FF", "border": "#4F46E5", "name_hi": lord_val})
                is_active = (s_dt <= target_dt <= e_dt)

                b_bg = th["color"] if is_active else (th["border"] if is_dark else th["bg"])
                b_color = "#FFFFFF" if (is_active or is_dark) else th["color"]
                b_border = f"2px solid #FFFFFF" if is_active else f"1px solid {th['border']}"
                active_pulse = "box-shadow: 0 0 10px rgba(234, 179, 8, 0.85); z-index: 2;" if is_active else ""

                lbl = f"{th['name_hi']}" if "name_hi" in th else str(lord_val)
                yrs = p.get("duration_years", 0)
                yrs_str = f" ({yrs:.0f}y)" if w_pct >= 4.0 else ""

                blocks.append(f"""<div style="width: {w_pct:.2f}%; height: 36px; background: {b_bg}; color: {b_color}; border: {b_border}; display: flex; align-items: center; justify-content: center; font-size: 11px; font-weight: {900 if is_active else 700}; overflow: hidden; white-space: nowrap; text-overflow: ellipsis; padding: 0 2px; position: relative; {active_pulse}" title="{label_prefix}{lbl} ({s_dt.strftime('%d-%b-%Y')} से {e_dt.strftime('%d-%b-%Y')}){' [सक्रिय]' if is_active else ''}">{lbl}{yrs_str}</div>""")
            return "".join(blocks)

        v_blocks = build_lane_blocks(v_list, lord_key="lord", label_prefix="विंशोत्तरी: ")
        y_blocks = build_lane_blocks(y_list, lord_key="lord", label_prefix="योगिनी: ")
        c_blocks = build_lane_blocks(c_list, lord_key="rashi", label_prefix="चर दशा: ")
        k_blocks = build_lane_blocks(k_list, lord_key="rashi", label_prefix="कालचक्र: ")

        today_marker_html = f"""<div style="position: absolute; left: {today_pct:.2f}%; top: -18px; bottom: -8px; width: 2.5px; background: #EF4444; z-index: 10; pointer-events: none; box-shadow: 0 0 10px #EF4444, 0 0 20px #F87171;"><div style="position: absolute; top: -14px; left: 50%; transform: translateX(-50%); background: #EF4444; color: #FFFFFF; font-size: 10px; font-weight: 900; padding: 1px 6px; border-radius: 4px; white-space: nowrap; box-shadow: 0 2px 6px rgba(0,0,0,0.3);">📍 आज ({target_date.strftime('%d-%b-%Y')} | {today_age:.1f}y)</div><div style="position: absolute; bottom: -8px; left: 50%; transform: translateX(-50%); width: 8px; height: 8px; border-radius: 50%; background: #EF4444; box-shadow: 0 0 8px #EF4444;"></div></div>"""

        ticks_html = "".join([f'<div style="position:absolute; left:{age}%; transform:translateX(-50%); font-size:10px; color:{txt_sub}; font-weight:700;">{age}y</div>' for age in range(0, 101, 20)])

        html = f"""
<div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: {bg_card}; border: 1.5px solid {border_card}; border-radius: 14px; padding: 20px 22px; box-shadow: 0 4px 20px rgba(0,0,0,0.06); margin-bottom: 20px;">
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; flex-wrap: wrap;">
        <div>
            <h4 style="margin: 0; color: {txt_main}; font-size: 16px; font-weight: 800; display: flex; align-items: center; gap: 8px;">
                ⏱️ बहु-दशा समानांतर जीवन टाइमलाइन (Multi-Dasha Parallel Lifeline 0-100 Years)
            </h4>
            <div style="font-size: 12px; color: {txt_sub}; margin-top: 3px;">
                विंशोत्तरी (१२० वर्ष), योगिनी (३६ वर्ष चक्र), जैमिनी चर एवं कालचक्र दशा का एक साथ आनुपातिक दृश्य मिलान
            </div>
        </div>
        <div style="background: rgba(239,68,68,0.1); border: 1px solid #EF4444; border-radius: 20px; padding: 4px 12px; font-size: 11.5px; font-weight: 800; color: #EF4444;">
            📍 लक्षित आयु: {today_age:.1f} वर्ष ({target_date.strftime('%d-%b-%Y')})
        </div>
    </div>

    <div style="position: relative; padding-top: 24px; padding-bottom: 24px;">
        {today_marker_html}

        <div style="margin-bottom: 12px;">
            <div style="display: flex; justify-content: space-between; font-size: 11px; font-weight: 800; color: {txt_main}; margin-bottom: 4px;">
                <span>🌟 १. विंशोत्तरी महादशा (Vimshottari 120y)</span>
                <span style="color: {txt_sub};">पाराशर मूल आधार</span>
            </div>
            <div style="display: flex; width: 100%; border-radius: 6px; overflow: hidden; background: {lane_bg};">
                {v_blocks}
            </div>
        </div>

        <div style="margin-bottom: 12px;">
            <div style="display: flex; justify-content: space-between; font-size: 11px; font-weight: 800; color: {txt_main}; margin-bottom: 4px;">
                <span>🌸 २. योगिनी दशा (Yogini 36-Year Cycle)</span>
                <span style="color: {txt_sub};">तात्कालिक मनोदशा व स्वास्थ्य</span>
            </div>
            <div style="display: flex; width: 100%; border-radius: 6px; overflow: hidden; background: {lane_bg};">
                {y_blocks}
            </div>
        </div>

        <div style="margin-bottom: 12px;">
            <div style="display: flex; justify-content: space-between; font-size: 11px; font-weight: 800; color: {txt_main}; margin-bottom: 4px;">
                <span>🔱 ३. जैमिनी चर दशा (Jaimini Chara Rashi)</span>
                <span style="color: {txt_sub};">कारक ग्रह व सामाजिक प्रतिष्ठा</span>
            </div>
            <div style="display: flex; width: 100%; border-radius: 6px; overflow: hidden; background: {lane_bg};">
                {c_blocks}
            </div>
        </div>

        <div style="margin-bottom: 16px;">
            <div style="display: flex; justify-content: space-between; font-size: 11px; font-weight: 800; color: {txt_main}; margin-bottom: 4px;">
                <span>🔄 ४. कालचक्र दशा (Kaalachakra KCD)</span>
                <span style="color: {txt_sub};">देह-जीव संतुलन व आकस्मिक गति</span>
            </div>
            <div style="display: flex; width: 100%; border-radius: 6px; overflow: hidden; background: {lane_bg};">
                {k_blocks}
            </div>
        </div>

        <div style="position: relative; height: 16px; border-top: 1px dashed {border_card}; margin-top: 8px;">
            {ticks_html}
        </div>
    </div>

    <div style="display: flex; gap: 12px; flex-wrap: wrap; margin-top: 10px; font-size: 11px; color: {txt_sub};">
        <span>💡 <b>संकेत:</b> सुनहरे बॉर्डर एवं चमक से युक्त ब्लॉक जातक की वर्तमान आयु पर सक्रिय दशा को दर्शाते हैं।</span>
    </div>
</div>
        """
        return html

    def calculate_multi_dasha_agreement_index(
        self,
        chart: KundaliChart,
        target_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        Calculates mathematical agreement index (% convergence) across the 4 major
        dashas (Vimshottari, Yogini, Chara, KCD) for 5 core life domains on target_date.
        """
        if target_date is None:
            target_date = date.today()

        target_dt = datetime.combine(target_date, datetime.min.time())

        # 1. Vimshottari
        try:
            v_hier = self.engine.get_active_hierarchy(chart, target_date)
            v_m_lord = v_hier.mahadasha.lord
            v_a_lord = v_hier.antardasha.lord
        except Exception:
            v_m_lord, v_a_lord = "Sun", "Moon"

        # 2. Yogini
        try:
            y_hier = default_yogini_engine.get_active_hierarchy(chart, target_date)
            y_lord = y_hier["major"]["lord"]
        except Exception:
            y_lord = "Moon"

        # 3. Chara
        try:
            c_tl = default_chara_engine.generate_timeline(chart)
            c_act = next((p for p in c_tl if p["start_date"] <= target_dt <= p["end_date"]), c_tl[0])
            c_rashi = c_act.get("rashi", "Aries")
            c_lord = SIGN_LORDS.get(c_rashi, "Mars")
        except Exception:
            c_rashi, c_lord = "Aries", "Mars"

        # 4. KCD
        try:
            k_tl = default_kcd_engine.generate_timeline(chart)
            k_act = next((p for p in k_tl if p["start_date"] <= target_dt <= p["end_date"]), k_tl[0])
            k_rashi = k_act.get("rashi", "Aries")
            k_gati = k_act.get("gati", "Regular")
        except Exception:
            k_rashi, k_gati = "Aries", "Regular"

        # Domain Scoring
        # Career
        c_score = 45
        if any(p in ["Sun", "Mars", "Jupiter", "Saturn", "Mercury"] for p in [v_m_lord, v_a_lord]):
            c_score += 20
        if y_lord in ["Sun", "Mars", "Jupiter", "Mercury"]:
            c_score += 15
        if c_rashi in ["Aries", "Leo", "Sagittarius", "Capricorn", "Aquarius"]:
            c_score += 10
        if any(w in k_gati for w in ["मण्डूक", "मर्कटी", "सिंहावलोकन", "Jump"]):
            c_score += 10
        c_score = min(96, max(30, c_score))

        # Wealth
        w_score = 40
        if any(p in ["Jupiter", "Venus", "Mercury", "Moon"] for p in [v_m_lord, v_a_lord]):
            w_score += 25
        if y_lord in ["Jupiter", "Venus", "Moon", "Mercury"]:
            w_score += 15
        if c_rashi in ["Taurus", "Gemini", "Libra", "Cancer", "Pisces"]:
            w_score += 12
        w_score = min(95, max(32, w_score))

        # Marriage / Relationship
        r_score = 42
        if any(p in ["Venus", "Jupiter", "Moon"] for p in [v_m_lord, v_a_lord]):
            r_score += 28
        if y_lord in ["Venus", "Jupiter", "Moon"]:
            r_score += 16
        if c_rashi in ["Taurus", "Libra", "Cancer", "Pisces"]:
            r_score += 12
        r_score = min(94, max(28, r_score))

        # Health / Vitality
        h_score = 75
        if any(p in ["Saturn", "Rahu", "Mars", "Ketu"] for p in [v_m_lord, v_a_lord]):
            h_score -= 18
        if y_lord in ["Rahu", "Saturn", "Ketu"]:
            h_score -= 12
        if any(w in k_gati for w in ["मण्डूक", "मर्कटी", "सिंहावलोकन"]):
            h_score -= 10
        h_score = min(95, max(35, h_score))

        # Spiritual
        s_score = 40
        if any(p in ["Jupiter", "Ketu", "Sun", "Saturn"] for p in [v_m_lord, v_a_lord]):
            s_score += 25
        if y_lord in ["Jupiter", "Ketu", "Sun"]:
            s_score += 18
        if c_rashi in ["Sagittarius", "Pisces", "Scorpio", "Cancer"]:
            s_score += 14
        s_score = min(96, max(35, s_score))

        overall_index = round((c_score + w_score + r_score + h_score + s_score) / 5.0, 1)

        if overall_index >= 70:
            consensus_badge = "🌟 उच्च बहु-दशा सहमति (High Consensus)"
            consensus_color = "#059669"
            consensus_desc = "विंशोत्तरी, योगिनी, जैमिनी चर एवं कालचक्र चारों दशा प्रणालियां एक ही दिशा में शुभ ऊर्जा का संचार कर रही हैं। इस कालखंड में महत्वपूर्ण जीवन घटनाएं निर्विघ्न घटित होंगी।"
        elif overall_index >= 55:
            consensus_badge = "⚡ मध्यम बहु-दशा सहमति (Moderate Consensus)"
            consensus_color = "#D97706"
            consensus_desc = "दशाओं में संतुलित व मिश्रित प्रभाव है। कुछ दशाएं प्रगति दर्शा रही हैं, जबकि कुछ अतिरिक्त परिश्रम की मांग करती हैं।"
        else:
            consensus_badge = "⏳ साधना व संयम काल (Developing Phase)"
            consensus_color = "#6366F1"
            consensus_desc = "दशाएं आंतरिक शुद्धि व आधारभूत तैयारी का कालखंड दर्शा रही हैं। नवीन जोखिम से बचें व नियमित वैदिक अनुष्ठान करें।"

        return {
            "target_date": target_date,
            "career_score": c_score,
            "wealth_score": w_score,
            "marriage_score": r_score,
            "health_score": h_score,
            "spiritual_score": s_score,
            "overall_index": overall_index,
            "consensus_badge": consensus_badge,
            "consensus_color": consensus_color,
            "consensus_desc": consensus_desc,
            "active_periods": {
                "vimshottari": f"{v_m_lord} / {v_a_lord}",
                "yogini": f"{y_lord}",
                "chara": f"{c_rashi} ({c_lord})",
                "kcd": f"{k_rashi} ({k_gati})"
            }
        }


# Singleton instance
default_dasha_timeline_service = DashaTimelineService()


