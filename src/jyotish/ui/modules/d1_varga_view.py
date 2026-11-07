import streamlit as st
import pandas as pd
from datetime import datetime, timezone, timedelta, date, time
import importlib

from src.jyotish.core.varga import VargaCalculator, VargaChart, VargaPlanetPosition
from src.jyotish.core.constants import SIGN_NAMES, SIGN_LORDS, NAKSHATRAS
from src.jyotish.ui.sudarshan import PLANET_NAMES_HI
from src.jyotish.dasha.vimshottari import default_dasha_engine
from src.jyotish.services.shastriya_pramana import default_shastriya_pramana_engine
from src.jyotish.core.chakras import default_kota_chakra_engine
from src.jyotish.core.calculator import default_chart_calculator
from src.jyotish.core.affliction import AfflictionEngine
from src.jyotish.ui.chart_renderer import ChartRenderer, render_aspect_orb_matrix_html

affliction_engine = AfflictionEngine()

def get_live_local_now(tz_offset_hours: float = 5.5) -> datetime:
    return datetime.now(timezone.utc) + timedelta(hours=tz_offset_hours)

def render_chart_svg_default(c_obj, chart_title, varga_code="D1"):
    chart_style = st.session_state.get("chart_style", "North Indian")
    if "South" in chart_style:
        return ChartRenderer.render_south_indian_svg(c_obj, title=chart_title, varga_code=varga_code)
    elif "East" in chart_style:
        return ChartRenderer.render_east_indian_svg(c_obj, title=chart_title, varga_code=varga_code)
    return ChartRenderer.render_north_indian_svg(c_obj, title=chart_title, varga_code=varga_code)

def get_varga_dignity_info(planet: str, sign_name: str, aff_eng=None):
    target_aff = aff_eng or affliction_engine
    text, css = target_aff.get_dignity(planet, sign_name)
    if css == "exalt":
        return "🌟 उच्च (Exalted)", 20, "परमोच्च बल एवं अत्यंत शुभ फल"
    elif css in ("mool", "moolatrikona"):
        return "💎 मूलत्रिकोण (Moolatrikona)", 18, "प्रबल शुभ एवं फलदायक"
    elif css in ("own", "swakshetra"):
        return "👑 स्वराशि (Own Sign)", 15, "सशक्त एवं अनुकूल आधार"
    elif css in ("friend", "friendly"):
        return "🤝 मित्र राशि (Friend Sign)", 11, "मित्रवत एवं सहयोगी प्रभाव"
    elif css in ("neutral", "sama"):
        return "⚖️ सम राशि (Neutral)", 7, "तटस्थ / सामान्य संतुलित फल"
    elif css in ("enemy", "shatru"):
        return "⚔️ शत्रु राशि (Enemy Sign)", 4, "प्रतिरोधी एवं संघर्षपूर्ण फल"
    elif css in ("deb", "debilitated"):
        return "⚠️ नीच (Debilitated)", 0, "कमजोर स्थिति / उपाय आवश्यक"
    return "⚖️ सामान्य", 7, "सामान्य प्रभाव" 

def render_styled_meters_html(items, max_val=20, is_dark=False):
    card_bg = "#111827" if is_dark else "#FFFFFF"
    card_bdr = "#374151" if is_dark else "#E2E8F0"
    track_bg = "#1F2937" if is_dark else "#F1F5F9"
    track_bdr = "#374151" if is_dark else "#CBD5E1"
    val_color = "#F8FAFC" if is_dark else "#0F172A"
    dim_color = "#94A3B8" if is_dark else "#64748B"

    rows_html = []
    for item in items:
        p_name = item["name"]
        sym = item.get("symbol", p_name)
        p_color = item.get("color", "#2563EB")
        d_lbl = item.get("dignity", "")
        score = float(item.get("score", 0.0))
        pct = min(100.0, max(4.0, (score / max_val) * 100.0))

        if "उच्च" in d_lbl or score >= 17:
            bar_grad = "linear-gradient(90deg, #10B981 0%, #059669 100%)"
            b_bg, b_fg, b_bdr = ("#064E3B", "#6EE7B7", "#059669") if is_dark else ("#DCFCE7", "#166534", "#86EFAC")
        elif "मूलत्रिकोण" in d_lbl or "स्वराशि" in d_lbl or score >= 14:
            bar_grad = "linear-gradient(90deg, #3B82F6 0%, #1D4ED8 100%)"
            b_bg, b_fg, b_bdr = ("#1E3A8A", "#93C5FD", "#2563EB") if is_dark else ("#DBEAFE", "#1D4ED8", "#93C5FD")
        elif "मित्र" in d_lbl or score >= 11:
            bar_grad = "linear-gradient(90deg, #06B6D4 0%, #0284C7 100%)"
            b_bg, b_fg, b_bdr = ("#164E63", "#7DD3FC", "#0284C7") if is_dark else ("#E0F2FE", "#0284C7", "#7DD3FC")
        elif "सम" in d_lbl or score >= 8:
            bar_grad = "linear-gradient(90deg, #F59E0B 0%, #D97706 100%)"
            b_bg, b_fg, b_bdr = ("#78350F", "#FDE68A", "#D97706") if is_dark else ("#FEF3C7", "#92400E", "#FCD34D")
        elif "शत्रु" in d_lbl or score >= 5:
            bar_grad = "linear-gradient(90deg, #F97316 0%, #EA580C 100%)"
            b_bg, b_fg, b_bdr = ("#7C2D12", "#FED7AA", "#EA580C") if is_dark else ("#FFEDD5", "#C2410C", "#FDBA74")
        else:
            bar_grad = "linear-gradient(90deg, #EF4444 0%, #DC2626 100%)"
            b_bg, b_fg, b_bdr = ("#7F1D1D", "#FCA5A5", "#DC2626") if is_dark else ("#FEE2E2", "#991B1B", "#FCA5A5")

        dignity_badge_html = f'<div style="width:84px; text-align:center;"><span style="background:{b_bg}; color:{b_fg}; border:1px solid {b_bdr}; border-radius:4px; padding:1px 5px; font-size:10px; font-weight:800; display:inline-block; width:100%; text-overflow:ellipsis; overflow:hidden; white-space:nowrap;">{d_lbl}</span></div>' if d_lbl else ''

        row = f'''<div style="display:flex; align-items:center; gap:8px; margin-bottom:7px;">
  <div style="width:105px; font-weight:800; font-size:12px; color:{p_color}; display:flex; align-items:center; gap:4px; white-space:nowrap;">
    <span>{sym}</span>
  </div>
  {dignity_badge_html}
  <div style="flex:1; background:{track_bg}; border-radius:6px; height:12px; overflow:hidden; position:relative; border:1px solid {track_bdr};">
    <div style="width:{pct:.1f}%; height:100%; background:{bar_grad}; border-radius:5px;"></div>
  </div>
  <div style="width:58px; text-align:right; font-weight:900; font-size:11.5px; color:{val_color}; font-family:monospace;">
    {score:.1f} <span style="font-size:9.5px; color:{dim_color}; font-weight:600;">/{int(max_val)}</span>
  </div>
</div>'''
        rows_html.append(row)

    return f'<div style="background:{card_bg}; border:1.5px solid {card_bdr}; border-radius:10px; padding:12px 14px; box-shadow:0 2px 8px rgba(0,0,0,0.04); margin-bottom:12px;">' + "".join(rows_html) + '</div>'


def generate_styled_vertical_svg(items, max_val=20, is_dark=False):
    svg_bg = "#111827" if is_dark else "#FFFFFF"
    svg_bdr = "#374151" if is_dark else "#E2E8F0"
    grid_col = "#374151" if is_dark else "#E2E8F0"
    base_col = "#64748B" if is_dark else "#94A3B8"
    score_col = "#FFFFFF" if is_dark else "#0F172A"

    n = len(items)
    w_svg = 540
    h_svg = 215
    top_y = 28
    base_y = 160
    chart_h = base_y - top_y

    pad_left = 32
    col_w = (w_svg - pad_left - 10) / n
    bar_w = min(30, col_w - 8)

    grid_lines = []
    for g_val in [5, 10, 15, 20]:
        g_y = base_y - (g_val / max_val) * chart_h
        grid_lines.append(f'<line x1="{pad_left}" y1="{g_y:.1f}" x2="{w_svg-10}" y2="{g_y:.1f}" stroke="{grid_col}" stroke-dasharray="3,3" stroke-width="1"/>')
        grid_lines.append(f'<text x="{pad_left - 6}" y="{g_y + 3:.1f}" font-size="9" fill="{base_col}" font-family="sans-serif" text-anchor="end">{g_val}</text>')

    bars_svg = []
    for i, item in enumerate(items):
        p_name = item["name"]
        sym = item.get("symbol", p_name)
        p_color = item.get("color", "#2563EB")
        d_lbl = item.get("dignity", "")
        score = float(item.get("score", 0.0))
        bar_h = max(4.0, (score / max_val) * chart_h)
        bar_x = pad_left + i * col_w + (col_w - bar_w) / 2
        bar_y = base_y - bar_h

        if "उच्च" in d_lbl or score >= 17:
            fill_c = "#10B981"
        elif "मूलत्रिकोण" in d_lbl or "स्वराशि" in d_lbl or score >= 14:
            fill_c = "#3B82F6"
        elif "मित्र" in d_lbl or score >= 11:
            fill_c = "#06B6D4"
        elif "सम" in d_lbl or score >= 8:
            fill_c = "#F59E0B"
        elif "शत्रु" in d_lbl or score >= 5:
            fill_c = "#F97316"
        else:
            fill_c = "#EF4444"

        bars_svg.append(f'<rect x="{bar_x:.1f}" y="{bar_y:.1f}" width="{bar_w:.1f}" height="{bar_h:.1f}" rx="4" ry="4" fill="{fill_c}" opacity="0.9"/>')
        bars_svg.append(f'<text x="{bar_x + bar_w/2:.1f}" y="{bar_y - 5:.1f}" font-size="10.5" font-weight="bold" fill="{score_col}" font-family="sans-serif" text-anchor="middle">{score:.1f}</text>')
        short_sym = sym.split()[0] if " " in sym else sym
        short_hi = sym.split()[1] if " " in sym else p_name[:3]
        bars_svg.append(f'<text x="{bar_x + bar_w/2:.1f}" y="{base_y + 16:.1f}" font-size="10" font-weight="bold" fill="{p_color}" font-family="sans-serif" text-anchor="middle">{short_sym} {short_hi}</text>')
        if d_lbl:
            short_d = d_lbl.split()[0] if "(" in d_lbl else d_lbl
            bars_svg.append(f'<text x="{bar_x + bar_w/2:.1f}" y="{base_y + 30:.1f}" font-size="9" font-weight="bold" fill="{fill_c}" font-family="sans-serif" text-anchor="middle">{short_d[:4]}</text>')

    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w_svg} {h_svg}" style="width:100%; height:auto; background:{svg_bg}; border:1.5px solid {svg_bdr}; border-radius:10px; box-shadow:0 2px 8px rgba(0,0,0,0.04); margin-bottom:12px;">
  {"".join(grid_lines)}
  <line x1="{pad_left}" y1="{base_y}" x2="{w_svg-10}" y2="{base_y}" stroke="{base_col}" stroke-width="1.5"/>
  {"".join(bars_svg)}
</svg>'''



def render_d1_varga_view(chart, birth_profile, tz_offset=5.5, default_city_name=None, render_chart_svg_fn=None, tabs=None):
    if default_city_name is None:
        default_city_name = st.session_state.get("birth_city", "New Delhi, Delhi, India")
    if render_chart_svg_fn is None:
        render_chart_svg_fn = render_chart_svg_default
    render_chart_svg = render_chart_svg_fn
    
    is_dark = st.session_state.get("dark_mode", False)
    is_astrallis_mode = st.session_state.get("astrallis_mode", False)
    is_night_mode = is_dark
    is_parashara_layout = st.session_state.get("parashara_layout", False)
    name = birth_profile.name if birth_profile else chart.birth_data.name
    birth_d = birth_profile.birth_date if birth_profile else chart.birth_data.birth_date
    birth_t = birth_profile.birth_time if birth_profile else chart.birth_data.birth_time
    city = default_city_name

    if tabs is None:
        tabs = [
            '☸️ लग्न व वर्ग चक्र (D1-D60)',
            '🌟 पुष्कर व वर्गोत्तम',
            '👑 जैमिनी विशेष लग्न',
            '🏠 भाव चलित',
            '🌙 चन्द्र कुण्डली',
            '☀️ सूर्य कुण्डली',
            '⚔️ ग्रह युद्ध',
            '🏰 १२ आरूढ़ पद (Arudha Padas)',
            '🏰 कोटा चक्र'
        ]
    st.subheader("📜 जन्म कुण्डली एवं षोडशवर्ग चक्र (Natal & Divisional Charts)")

    tab_d1, tab_pushkara, tab_jm_hud, tab_bhav, tab_chandra, tab_surya, tab_yuddha, tab_vishesh, tab_kota = st.tabs(tabs)

    with tab_d1:
        VARGA_SIGNIFICANCE = {
            "D1": "समस्त जीवन, शारीरिक गठन एवं आत्म-व्यक्तित्व (General Life & Body)",
            "D2": "धन, संपत्ति, वित्तीय स्थिति एवं कुटुम्ब (Wealth & Family Prosperity)",
            "D3": "पराक्रम, भ्रातृ सुख, साहस एवं ऊर्जा (Courage, Siblings & Valor)",
            "D4": "अचल संपत्ति, भवन, वाहन एवं भाग्य (Fixed Assets, Property & Fortune)",
            "D7": "संतान सुख, वंश वृद्धि एवं रचनात्मकता (Children & Progeny)",
            "D9": "धर्म, वैवाहिक जीवन, जीवनसाथी एवं आत्मबल (Dharma, Marriage & Destiny)",
            "D10": "कर्म, आजीविका, प्रतिष्ठा, पद एवं अधिकार (Career, Profession & Power)",
            "D12": "माता-पिता, पितृ ऋण एवं पैतृक विरासत (Parents & Ancestral Lineage)",
            "D16": "वाहन, भौतिक सुख-साधन एवं अंतःकरण (Vehicles, Luxuries & Mind)",
            "D20": "आध्यात्मिक साधना, उपासना एवं ईश्वरीय कृपा (Spiritual Quest & Bhakti)",
            "D24": "उच्च विद्या, ज्ञान, मेधा शक्ति एवं कौशल (Higher Learning & Intellect)",
            "D27": "शारीरिक बल, सामर्थ्य, गुण एवं दुर्बलताएं (Strengths & Weaknesses)",
            "D30": "अरिष्ट, रोग, पाप प्रभाव एवं संकट (Misfortunes, Evils & Challenges)",
            "D60": "पूर्वजन्म के संचित कर्म एवं अंतिम प्रारब्ध (Past Life Karma & Core Destiny)",
        }

        curr_style = st.session_state.get("app_chart_style", "North Indian (Diamond)")
        chart_view_mode = st.session_state.get("app_chart_view_mode", "Single")

        if chart_view_mode == "Quad":
            st.markdown("#### 🖥️ ४-कुण्डली एकीकृत्त कस्टम वर्कबेंच (Multi-Chart Split-Screen Worksheet)")
            st.caption("विश्वस्तरीय वैदिक ज्योतिष वर्कबेंच समान एक ही स्क्रीन पर किसी भी ४ वर्ग चक्रों का एक साथ अध्ययन:")

            v_opts = list(chart.vargas.keys()) if chart.vargas else ["D1"]
            if "D1" not in v_opts:
                v_opts = ["D1"] + v_opts

            # Classical Focus Presets
            st.markdown("##### 🎯 शास्त्रीय अध्ययन प्रीसेट्स (Quick Focus Presets):")
            c_ps1, c_ps2, c_ps3, c_ps4, c_ps5 = st.columns(5)
            if c_ps1.button("👑 सामान्य दैवज्ञ", key="btn_preset_general", use_container_width=True, help="D1 लग्न + D9 नवांश + D10 दशमांश + D7 सप्तांश"):
                st.session_state.quad_slot_1 = "D1"
                st.session_state.quad_slot_2 = "D9"
                st.session_state.quad_slot_3 = "D10"
                st.session_state.quad_slot_4 = "D7"
                st.rerun()
            if c_ps2.button("💼 करियर व अर्थ", key="btn_preset_career", use_container_width=True, help="D1 लग्न + D9 नवांश + D10 दशमांश + D11 एकादशांश"):
                st.session_state.quad_slot_1 = "D1"
                st.session_state.quad_slot_2 = "D9"
                st.session_state.quad_slot_3 = "D10"
                st.session_state.quad_slot_4 = "D11" if "D11" in v_opts else "D2"
                st.rerun()
            if c_ps3.button("💍 विवाह व संबंध", key="btn_preset_marriage", use_container_width=True, help="D1 लग्न + D9 नवांश + D7 सप्तांश + D3 द्रेष्काण"):
                st.session_state.quad_slot_1 = "D1"
                st.session_state.quad_slot_2 = "D9"
                st.session_state.quad_slot_3 = "D7"
                st.session_state.quad_slot_4 = "D3"
                st.rerun()
            if c_ps4.button("🏥 स्वास्थ्य व अरिष्ट", key="btn_preset_health", use_container_width=True, help="D1 लग्न + D6 षष्ठांश + D8 अष्टांश + D30 त्रिंशांश"):
                st.session_state.quad_slot_1 = "D1"
                st.session_state.quad_slot_2 = "D6" if "D6" in v_opts else "D9"
                st.session_state.quad_slot_3 = "D8" if "D8" in v_opts else "D3"
                st.session_state.quad_slot_4 = "D30" if "D30" in v_opts else "D12"
                st.rerun()
            if c_ps5.button("🧘 साधना व प्रारब्ध", key="btn_preset_spiritual", use_container_width=True, help="D1 लग्न + D9 नवांश + D20 विंशांश + D60 षष्ट्यंश"):
                st.session_state.quad_slot_1 = "D1"
                st.session_state.quad_slot_2 = "D9"
                st.session_state.quad_slot_3 = "D20" if "D20" in v_opts else "D12"
                st.session_state.quad_slot_4 = "D60" if "D60" in v_opts else "D7"
                st.rerun()

            st.markdown("<div style='height: 4px;'></div>", unsafe_allow_html=True)

            def render_quad_slot(col, slot_key, label, default_code):
                with col:
                    cur_code = st.session_state.get(slot_key, default_code)
                    if cur_code not in v_opts:
                        cur_code = default_code if default_code in v_opts else v_opts[0]
                    sel_code = st.selectbox(
                        label,
                        v_opts,
                        index=v_opts.index(cur_code),
                        key=f"quad_sel_{slot_key}",
                        format_func=lambda x: f"{x} - {chart.vargas[x].varga_name}" if (chart.vargas and x in chart.vargas and hasattr(chart.vargas[x], 'varga_name')) else x
                    )
                    if sel_code != cur_code:
                        st.session_state[slot_key] = sel_code
                        st.rerun()

                    # Dynamic Sampradaya Variation Allocation if needed
                    cur_d3_act = st.session_state.get("v_d3_meth", "parashari")
                    cur_d9_act = st.session_state.get("v_d9_meth", "parashari")
                    cur_d2_act = st.session_state.get("v_d2_meth", "parashari")
                    if sel_code == "D3" and cur_d3_act != "parashari":
                        chart.vargas["D3"] = VargaCalculator.calculate_d3(chart, variation=cur_d3_act)
                    elif sel_code == "D9" and cur_d9_act != "parashari":
                        chart.vargas["D9"] = VargaCalculator.calculate_d9(chart, variation=cur_d9_act)
                    elif sel_code == "D2" and cur_d2_act != "parashari":
                        chart.vargas["D2"] = VargaCalculator.calculate_d2(chart, variation=cur_d2_act)

                    target_v = chart.vargas.get(sel_code) if (chart.vargas and sel_code in chart.vargas) else None
                    v_name = target_v.varga_name if target_v else sel_code
                    v_title = f"{sel_code} - {v_name}"
                    svg_out = render_chart_svg(chart, v_title, varga_code=sel_code)
                    st.markdown(f'<div class="kundali-chart" style="width:100%;">{svg_out}</div>', unsafe_allow_html=True)
                    l_sign = target_v.lagna_sign_name if target_v else chart.lagna_sign_name
                    l_id = target_v.lagna_sign_id if target_v else chart.lagna_sign_id
                    st.caption(f"**{sel_code} लग्न:** {l_sign} ({l_id})")

            q_col1, q_col2 = st.columns(2, gap="medium")
            render_quad_slot(q_col1, "quad_slot_1", "चक्र १ (Slot 1)", "D1")
            render_quad_slot(q_col2, "quad_slot_2", "चक्र २ (Slot 2)", "D9")

            q_col3, q_col4 = st.columns(2, gap="medium")
            render_quad_slot(q_col3, "quad_slot_3", "चक्र ३ (Slot 3)", "D10")
            render_quad_slot(q_col4, "quad_slot_4", "चक्र ४ (Slot 4)", "D7")

        # =========================================================================
        # 🏛️ PARASHARA'S LIGHT AUTHENTIC 2x2 WORKSTATION GRID (70% RIGHT PANEL)
        # =========================================================================
        if is_parashara_layout:
            # Row 1: Box 1 (Vimshottari Dasha 5-Level) & Box 2 (Shadbala & Vimsopaka Strength)
            pl_r1_c1, pl_r1_c2 = st.columns(2, gap="small")
            with pl_r1_c1:
                st.markdown("""<div class="pl-box-header"><span>⏱️ विंशोत्तरी दशा (Vimshottari Dasha — 5-स्तरीय)</span><span style="font-size:11px;">सक्रिय काल</span></div>""", unsafe_allow_html=True)
                try:
                    _b_dt = datetime.combine(birth_d, birth_t)
                    _m_lon = chart.planets["Moon"].longitude if "Moon" in chart.planets else 0.0
                    _h5 = default_dasha_engine.get_5level_hierarchy(_b_dt, _m_lon, get_live_local_now(tz_offset))
                    _m_lord = _h5["mahadasha"]["lord"]
                    _a_lord = _h5["antardasha"]["lord"]
                    _pr_lord = _h5["pratyantardasha"]["lord"]
                    _s_lord = _h5["sookshmadasha"]["lord"]
                    _p_lord = _h5["pranadasha"]["lord"]

                    _m_s = _h5["mahadasha"]["start_date"].strftime("%d-%b-%y")
                    _m_e = _h5["mahadasha"]["end_date"].strftime("%d-%b-%y")
                    _a_s = _h5["antardasha"]["start_date"].strftime("%d-%b-%y")
                    _a_e = _h5["antardasha"]["end_date"].strftime("%d-%b-%y")
                    _pr_s = _h5["pratyantardasha"]["start_date"].strftime("%d-%b-%y")
                    _pr_e = _h5["pratyantardasha"]["end_date"].strftime("%d-%b-%y")
                    _s_s = _h5["sookshmadasha"]["start_date"].strftime("%d-%b-%y")
                    _s_e = _h5["sookshmadasha"]["end_date"].strftime("%d-%b-%y")
                    _p_s = _h5["pranadasha"]["start_date"].strftime("%d-%b-%y")
                    _p_e = _h5["pranadasha"]["end_date"].strftime("%d-%b-%y")

                    _dasha_html = f'<div style="background:#FFFFFF; border:1px solid #CBD5E1; border-top:none; border-radius:0 0 6px 6px; padding:6px; font-size:11.5px;"><div style="display:flex; justify-content:space-between; align-items:center; background:#EEF2FF; border:1px solid #C7D2FE; border-radius:4px; padding:3px 6px; margin-bottom:4px;"><span style="font-weight:800; color:#312E81;">👑 महादशा (L1):</span><span style="font-weight:900; color:#1E1B4B; background:#C7D2FE; padding:1px 6px; border-radius:4px;">{_m_lord}</span><span style="color:#475569; font-size:10.5px;">{_m_s} ~ {_m_e}</span></div><div style="display:flex; justify-content:space-between; align-items:center; background:#F0FDF4; border:1px solid #BBF7D0; border-radius:4px; padding:3px 6px; margin-bottom:4px;"><span style="font-weight:800; color:#064E3B;">🪐 अंतर्दशा (L2):</span><span style="font-weight:900; color:#065F46; background:#BBF7D0; padding:1px 6px; border-radius:4px;">{_a_lord}</span><span style="color:#475569; font-size:10.5px;">{_a_s} ~ {_a_e}</span></div><div style="display:flex; justify-content:space-between; align-items:center; background:#FFFBEB; border:1px solid #FDE68A; border-radius:4px; padding:3px 6px; margin-bottom:4px;"><span style="font-weight:800; color:#78350F;">⚡ प्रत्यंतर (L3):</span><span style="font-weight:900; color:#92400E; background:#FDE68A; padding:1px 6px; border-radius:4px;">{_pr_lord}</span><span style="color:#475569; font-size:10.5px;">{_pr_s} ~ {_pr_e}</span></div><div style="display:flex; justify-content:space-between; align-items:center; background:#FDF2F8; border:1px solid #FBCFE8; border-radius:4px; padding:3px 6px; margin-bottom:4px;"><span style="font-weight:800; color:#831843;">🔍 सूक्ष्मदशा (L4):</span><span style="font-weight:900; color:#9D174D; background:#FBCFE8; padding:1px 6px; border-radius:4px;">{_s_lord}</span><span style="color:#475569; font-size:10.5px;">{_s_s} ~ {_s_e}</span></div><div style="display:flex; justify-content:space-between; align-items:center; background:#F8FAFC; border:1px solid #E2E8F0; border-radius:4px; padding:3px 6px;"><span style="font-weight:800; color:#0F172A;">🧬 प्राणदशा (L5):</span><span style="font-weight:900; color:#1E293B; background:#E2E8F0; padding:1px 6px; border-radius:4px;">{_p_lord}</span><span style="color:#475569; font-size:10.5px;">{_p_s} ~ {_p_e}</span></div></div>'
                    st.markdown(_dasha_html, unsafe_allow_html=True)
                except Exception as _e_d:
                    st.caption(f"दशा लोड हो रही है: {_e_d}")


            with pl_r1_c2:
                st.markdown("""<div class="pl-box-header"><span>⚖️ षड्बल एवं विंशोपक बल (Shadbala & Strength)</span><span style="font-size:11px;">7 ग्रह शक्ति</span></div>""", unsafe_allow_html=True)
                try:
                    _sb_res = chart.shadbala
                    _vimsopaka = VargaCalculator.calculate_vimsopaka_bala(chart)
                    _sb_p_list = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
                    _sb_rows = []
                    for _pn in _sb_p_list:
                        _sb_o = _sb_res.planets.get(_pn) if _sb_res else None
                        _rupas = f"{_sb_o.total_rupas:.2f}" if _sb_o else "—"
                        _ratio = _sb_o.strength_ratio if _sb_o else 1.0
                        _is_str = _sb_o.is_strong if _sb_o else True
                        _str_badge = f'<span style="background:{"#DCFCE7" if _is_str else "#FEE2E2"}; color:{"#166534" if _is_str else "#991B1B"}; font-weight:800; padding:1px 6px; border-radius:4px;">{"बलवान" if _is_str else "निर्बल"}</span>'
                        _v_score = _vimsopaka.get(_pn, 10.0)
                        _sb_rows.append(f'<tr style="border-bottom:1px solid #E2E8F0;"><td style="padding:4px 6px; font-weight:800; color:#1E293B;">{_pn}</td><td style="padding:4px 6px; text-align:center;">{_rupas} R</td><td style="padding:4px 6px; text-align:center;">{_ratio:.2f}</td><td style="padding:4px 6px; text-align:center;">{_v_score:.1f}/20</td><td style="padding:4px 6px; text-align:center;">{_str_badge}</td></tr>')

                    _sb_table_html = f'<div style="background:#FFFFFF; border:1px solid #CBD5E1; border-top:none; border-radius:0 0 6px 6px; padding:4px; max-height:175px; overflow-y:auto;"><table style="width:100%; border-collapse:collapse; font-size:11px;"><thead><tr style="background:#F1F5F9; color:#475569; font-weight:800; border-bottom:1.5px solid #CBD5E1;"><th style="padding:3px 6px; text-align:left;">ग्रह</th><th style="padding:3px 6px; text-align:center;">रूप</th><th style="padding:3px 6px; text-align:center;">अनुपात</th><th style="padding:3px 6px; text-align:center;">विंशोपक</th><th style="padding:3px 6px; text-align:center;">स्थिति</th></tr></thead><tbody>{"".join(_sb_rows)}</tbody></table></div>'
                    st.markdown(_sb_table_html, unsafe_allow_html=True)
                except Exception as _e_sb:
                    st.caption(f"षड्बल लोड हो रहा है: {_e_sb}")

            st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

            # Row 2: Box 3 (Planetary Longitudes & Dignity Table) & Box 4 (Sarvashtakavarga 12-Sign Matrix)
            pl_r2_c1, pl_r2_c2 = st.columns(2, gap="small")
            with pl_r2_c1:
                st.markdown("""<div class="pl-box-header"><span>🪐 ग्रह स्पष्ट तालिका (Planetary Longitudes & Dignity)</span><span style="font-size:11px;">D1 स्पष्ट</span></div>""", unsafe_allow_html=True)
                _p_rows_box = []
                _p_order = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]
                for _pn in _p_order:
                    _po = chart.planets.get(_pn)
                    if not _po: continue
                    _sym = {"Sun":"☉ सूर्य","Moon":"☽ चन्द्र","Mars":"♂ मंगल","Mercury":"☿ बुध","Jupiter":"♃ गुरु","Venus":"♀ शुक्र","Saturn":"♄ शनि","Rahu":"☊ राहु","Ketu":"☋ केतु"}.get(_pn, _pn)
                    _d_lbl, _, _ = get_varga_dignity_info(_pn, _po.sign_name, affliction_engine)
                    _motion = "℞" if _po.is_retrograde else ""
                    _comb = "☌" if _po.is_combust else ""
                    _badge_color = "#1E40AF" if "उच्च" in _d_lbl else ("#047857" if "स्वराशि" in _d_lbl or "मूल" in _d_lbl else ("#B91C1C" if "नीच" in _d_lbl else "#475569"))
                    _p_rows_box.append(f'<tr style="border-bottom:1px solid #E2E8F0;"><td style="padding:3px 5px; font-weight:800; color:#0F172A; white-space:nowrap;">{_sym} <span style="color:#DC2626; font-size:10px;">{_motion}{_comb}</span></td><td style="padding:3px 5px; font-weight:700; color:#1E3A8A;">{_po.sign_name[:4]}</td><td style="padding:3px 5px; font-family:monospace; font-weight:700; color:#0F172A;">{_po.sign_degree:.2f}°</td><td style="padding:3px 5px; font-size:10px; color:#475569;">{_po.nakshatra_name[:4]}-P{_po.nakshatra_pada}</td><td style="padding:3px 5px; font-weight:800; color:{_badge_color}; font-size:10px;">{_d_lbl[:6]}</td></tr>')

                _p_table_html = f'<div style="background:#FFFFFF; border:1px solid #CBD5E1; border-top:none; border-radius:0 0 6px 6px; padding:4px; max-height:190px; overflow-y:auto;"><table style="width:100%; border-collapse:collapse; font-size:11px;"><thead><tr style="background:#F1F5F9; color:#475569; font-weight:800; border-bottom:1.5px solid #CBD5E1;"><th style="padding:3px 5px; text-align:left;">ग्रह</th><th style="padding:3px 5px; text-align:left;">राशि</th><th style="padding:3px 5px; text-align:left;">अंश</th><th style="padding:3px 5px; text-align:left;">नक्षत्र</th><th style="padding:3px 5px; text-align:left;">गरिमा</th></tr></thead><tbody>{"".join(_p_rows_box)}</tbody></table></div>'
                st.markdown(_p_table_html, unsafe_allow_html=True)

            with pl_r2_c2:
                st.markdown("""<div class="pl-box-header"><span>📊 सर्वाष्टकवर्ग सारणी (Sarvashtakavarga 12 Signs)</span><span style="font-size:11px;">बिन्दु योग (337)</span></div>""", unsafe_allow_html=True)
                try:
                    _sav_arr = chart.ashtakavarga.sav if chart.ashtakavarga else [28]*12
                    _rashi_names_12 = ["मेष", "वृषभ", "मिथुन", "कर्क", "सिंह", "कन्या", "तुला", "वृश्चिक", "धनु", "मकर", "कुंभ", "मीन"]
                    _sav_cells = []
                    for _s_idx in range(12):
                        _pts = _sav_arr[_s_idx]
                        _bg = "#DCFCE7" if _pts >= 30 else ("#FEF3C7" if _pts >= 25 else "#FEE2E2")
                        _fg = "#166534" if _pts >= 30 else ("#92400E" if _pts >= 25 else "#991B1B")
                        _sav_cells.append(f'<div style="background:{_bg}; border:1px solid #CBD5E1; border-radius:6px; padding:4px 6px; text-align:center;"><div style="font-size:10px; color:#475569; font-weight:700;">{_s_idx+1}. {_rashi_names_12[_s_idx]}</div><div style="font-size:14px; font-weight:900; color:{_fg};">{_pts}</div></div>')

                    _sav_html = f'<div style="background:#FFFFFF; border:1px solid #CBD5E1; border-top:none; border-radius:0 0 6px 6px; padding:6px;"><div style="display:grid; grid-template-columns: repeat(4, 1fr); gap:6px;">{"".join(_sav_cells)}</div><div style="display:flex; justify-content:space-between; margin-top:6px; font-size:10.5px; color:#64748B; padding:2px 4px; background:#F8FAFC; border-radius:4px;"><span>🟢 ≥30 शुभ</span><span>🟡 25-29 मध्यम</span><span>🔴 &lt;25 शोधन आवश्यक</span><span>कुल: <b>{sum(_sav_arr)}</b></span></div></div>'
                    st.markdown(_sav_html, unsafe_allow_html=True)
                except Exception as _e_sav:
                    st.caption(f"अष्टकवर्ग लोड हो रहा है: {_e_sav}")

            st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

            # Beneath 2x2: Expander for Varga Selector & Sub-analysis
            with st.expander("🔍 षोडशवर्ग चक्र (D2 to D60 Deep Dive) एवं अतिरिक्त विश्लेषण", expanded=False):
                st.markdown("##### वर्ग चक्र चयन एवं सूक्ष्म अध्ययन:")
                v_opts = list(chart.vargas.keys()) if chart.vargas else ["D1"]
                sel_pl_varga = st.selectbox(
                    "वर्ग चक्र चुनें (Select Varga Chart)",
                    v_opts,
                    index=0,
                    format_func=lambda x: f"{x} - {chart.vargas[x].varga_name}" if x in chart.vargas else x,
                    key="pl_deep_varga_sel"
                )
                col_pv1, col_pv2 = st.columns([1, 1])
                with col_pv1:
                    svg_pv = render_chart_svg(chart, f"{sel_pl_varga} {chart.vargas.get(sel_pl_varga, chart.vargas.get('D1')).varga_name}", varga_code=sel_pl_varga)
                    st.markdown(svg_pv, unsafe_allow_html=True)
                with col_pv2:
                    pv_desc = VARGA_SIGNIFICANCE.get(sel_pl_varga, "शास्त्रीय सूक्ष्म विश्लेषण")
                    st.info(f"🎯 **{sel_pl_varga} शास्त्रीय प्रयोजन:** {pv_desc}")
                    vims_score = VargaCalculator.calculate_vimsopaka_bala(chart)
                    st.bar_chart(pd.DataFrame(list(vims_score.items()), columns=["Planet", "Vimsopaka"]).set_index("Planet"))

            varga_choice = sel_pl_varga
            target_varga = chart.vargas.get(varga_choice, chart.vargas.get("D1"))
            v_name = target_varga.varga_name if target_varga else "Rashi"
            v_lagna_sign = target_varga.lagna_sign_name if target_varga else chart.lagna_sign_name
            v_lagna_id = target_varga.lagna_sign_id if target_varga else chart.lagna_sign_id
        else:
            # Standard Single / Quad Dashboard Layout (Classic 2-Column Split: Left Chart, Right Analysis)
            col_chart1, col_chart2 = st.columns([1, 1], gap="medium")
            with col_chart1:
                varga_options = list(chart.vargas.keys()) if chart.vargas else ["D1"]
                varga_choice = st.selectbox(
                    "वर्ग चक्र चयन (Select Varga Chart)",
                    varga_options,
                    format_func=lambda x: f"{x} - {chart.vargas[x].varga_name}" if x in chart.vargas else x
                )
                # Dynamic Sampradaya Variation Allocation
                cur_d3_act = st.session_state.get("v_d3_meth", "parashari")
                cur_d9_act = st.session_state.get("v_d9_meth", "parashari")
                cur_d2_act = st.session_state.get("v_d2_meth", "parashari")
                if varga_choice == "D3" and cur_d3_act != "parashari":
                    target_varga = VargaCalculator.calculate_d3(chart, variation=cur_d3_act)
                    chart.vargas["D3"] = target_varga
                elif varga_choice == "D9" and cur_d9_act != "parashari":
                    target_varga = VargaCalculator.calculate_d9(chart, variation=cur_d9_act)
                    chart.vargas["D9"] = target_varga
                elif varga_choice == "D2" and cur_d2_act != "parashari":
                    target_varga = VargaCalculator.calculate_d2(chart, variation=cur_d2_act)
                    chart.vargas["D2"] = target_varga
                else:
                    target_varga = chart.vargas.get(varga_choice, chart.vargas.get("D1"))
                v_name = target_varga.varga_name if target_varga else "Rashi"
                v_lagna_sign = target_varga.lagna_sign_name if target_varga else chart.lagna_sign_name
                v_lagna_id = target_varga.lagna_sign_id if target_varga else chart.lagna_sign_id

                title = f"{varga_choice} {v_name} Kundali"
                svg_code = render_chart_svg(chart, title, varga_code=varga_choice)
                st.markdown(f'<div class="kundali-chart" style="width:100%; display:flex; justify-content:center; margin-bottom:10px;">{svg_code}</div>', unsafe_allow_html=True)

                v_desc = VARGA_SIGNIFICANCE.get(varga_choice, "शास्त्रीय सूक्ष्म विश्लेषण")
                st.info(f"🎯 **{varga_choice} ({v_name}) शास्त्रीय प्रयोजन:** {v_desc}")

                # ─── Dynamic Varga Phalit Synthesis Card ───
                try:
                    _v_planets = getattr(target_varga, 'planets', {}) if target_varga else {}
                    _v_exalted, _v_own, _v_deb = [], [], []
                    _EXALT_SIGNS = {"Sun": "Aries", "Moon": "Taurus", "Mars": "Capricorn", "Mercury": "Virgo", "Jupiter": "Cancer", "Venus": "Pisces", "Saturn": "Libra", "Rahu": "Taurus", "Ketu": "Scorpio"}
                    _DEB_SIGNS = {"Sun": "Libra", "Moon": "Scorpio", "Mars": "Cancer", "Mercury": "Pisces", "Jupiter": "Capricorn", "Venus": "Virgo", "Saturn": "Aries", "Rahu": "Scorpio", "Ketu": "Taurus"}
                    
                    for _pname, _ppos in _v_planets.items():
                        _psign = getattr(_ppos, 'sign_name', '')
                        if _psign == _EXALT_SIGNS.get(_pname):
                            _v_exalted.append(_pname)
                        elif _psign == _DEB_SIGNS.get(_pname):
                            _v_deb.append(_pname)
                        elif _psign in SIGN_LORDS and SIGN_LORDS.get(_psign) == _pname:
                            _v_own.append(_pname)

                    _v_lagna_lord = SIGN_LORDS.get(v_lagna_sign, "—")
                    _v_synthesis_points = []
                    if _v_exalted:
                        _v_synthesis_points.append(f"🌟 **उच्च ग्रह ({', '.join(_v_exalted)}):** इस वर्ग के कार्यक्षेत्र में असाधारण सफलता एवं प्रभुत्व का संकेत देते हैं।")
                    if _v_own:
                        _v_synthesis_points.append(f"🏰 **स्वगृही ग्रह ({', '.join(_v_own)}):** वर्ग फल में स्थायित्व एवं आत्म-निर्भरता का निर्माण करते हैं।")
                    if _v_deb:
                        _v_synthesis_points.append(f"⚠️ **नीच ग्रह ({', '.join(_v_deb)}):** संबंधित विषय में अतिरिक्त पुरुषार्थ, जागरूकता एवं शांति उपायों की आवश्यकता दर्शाते हैं।")
                    if not _v_synthesis_points:
                        _v_synthesis_points.append("⚖️ **संतुलित ग्रह प्रभाव:** ग्रह सामान्य गरिमा के साथ स्थित होकर मध्यम एवं क्रमिक परिणाम प्रदान कर रहे हैं।")

                    st.markdown(f"""
                    <div style="background: linear-gradient(135deg, #F8FAFC 0%, #F1F5F9 100%); border: 1px solid #CBD5E1; border-radius: 8px; padding: 10px 14px; margin-top: 8px; font-size: 12px; color: #1E293B;">
                        <div style="font-weight: 800; color: #1E40AF; margin-bottom: 4px; display:flex; justify-content:space-between;">
                            <span>🔬 <b>{varga_choice} शास्त्रीय फलित समन्वय (Varga Synthesis)</b></span>
                            <span style="color: #64748B;">वर्ग लग्न: <b>{v_lagna_sign}</b> (स्वामी: <b>{_v_lagna_lord}</b>)</span>
                        </div>
                        <div style="line-height: 1.5;">
                            {'<br/>'.join(_v_synthesis_points)}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                except Exception as _e_syn:
                    st.caption(f"वर्ग समन्वय लोड हो रहा है: {_e_syn}")

            with col_chart2:
                _is_astrallis_chart = ("Astrallis" in curr_style or "Circular" in curr_style)
                if _is_astrallis_chart:
                    # ─── Astrallis Scientific Observatory Data Console ───
                    if is_astrallis_mode:
                        _dc_bg  = "#050811"
                        _dc_row = "#0A1628"
                        _dc_bdr = "#1E3A5F"
                        _dc_hdr = "#00E5FF"
                        _dc_txt = "#CBD5E1"
                        _dc_val = "#E2E8F0"
                        _dc_th_col = "#00E5FF"
                        _pts_good = "#44FF88"
                        _pts_mid  = "#FFD700"
                        _pts_low  = "#FF4444"
                    elif is_night_mode:
                        _dc_bg  = "#111827"
                        _dc_row = "#1F2937"
                        _dc_bdr = "#374151"
                        _dc_hdr = "#F59E0B"
                        _dc_txt = "#D1D5DB"
                        _dc_val = "#F8FAFC"
                        _dc_th_col = "#F59E0B"
                        _pts_good = "#44FF88"
                        _pts_mid  = "#FFD700"
                        _pts_low  = "#FF4444"
                    else:  # Day Mode (Royal Pearl / Vedic Classic)
                        _dc_bg  = "#FFFFFF"
                        _dc_row = "#F8FAFC"
                        _dc_bdr = "#CBD5E1"
                        _dc_hdr = "#1E40AF"
                        _dc_txt = "#475569"
                        _dc_val = "#0F172A"
                        _dc_th_col = "#1E3A8A"
                        _pts_good = "#059669"
                        _pts_mid  = "#D97706"
                        _pts_low  = "#DC2626"

                    # Jataka Info Console
                    _j_name = chart.birth_data.name if (chart.birth_data and chart.birth_data.name) else (name if 'name' in locals() else "Jataka")
                    _j_city = (getattr(chart.birth_data, 'city', None) or (default_city_name if 'default_city_name' in locals() else (city if 'city' in locals() else "New Delhi")))
                    _j_bdate = chart.birth_data.birth_date if (chart.birth_data and hasattr(chart.birth_data, 'birth_date')) else (birth_d if 'birth_d' in locals() else None)
                    _j_btime = chart.birth_data.birth_time if (chart.birth_data and hasattr(chart.birth_data, 'birth_time')) else (birth_t if 'birth_t' in locals() else None)
                    _j_dt_str = f"{_j_bdate.strftime('%d-%b-%Y') if _j_bdate else ''} {_j_btime.strftime('%I:%M %p') if _j_btime else ''}".strip()

                    st.markdown(f"""
        <div style="background:{_dc_bg};border:1px solid {_dc_bdr};border-radius:8px;padding:10px 12px;margin-bottom:8px;font-size:12px;box-shadow: 0 1px 4px rgba(0,0,0,0.05);">
          <div style="color:{_dc_hdr};font-weight:900;font-size:13px;margin-bottom:8px;letter-spacing:0.5px;">⚡ JATAKA DATA CONSOLE</div>
          <table style="width:100%;border-collapse:collapse;">
            <tr><td style="color:{_dc_txt};padding:2px 4px;">Name</td><td style="color:{_dc_val};font-weight:800;padding:2px 4px;">{_j_name}</td></tr>
            <tr style="background:{_dc_row};"><td style="color:{_dc_txt};padding:2px 4px;">Place</td><td style="color:{_dc_val};font-weight:800;padding:2px 4px;">{_j_city}</td></tr>
            <tr><td style="color:{_dc_txt};padding:2px 4px;">Date &amp; Time</td><td style="color:{_dc_val};font-weight:800;padding:2px 4px;">{_j_dt_str}</td></tr>
            <tr style="background:{_dc_row};"><td style="color:{_dc_txt};padding:2px 4px;">Ayanamsa</td><td style="color:{_dc_val};font-weight:800;padding:2px 4px;">{chart.ayanamsa_name} ({chart.ayanamsa_value:.4f}°)</td></tr>
            <tr><td style="color:{_dc_txt};padding:2px 4px;">Lagna (Asc)</td><td style="color:{_dc_hdr};font-weight:900;padding:2px 4px;">{chart.lagna_sign_name} ({chart.lagna_sign_id})</td></tr>
            <tr style="background:{_dc_row};"><td style="color:{_dc_txt};padding:2px 4px;">Atmakaraka</td><td style="color:{_pts_mid};font-weight:900;padding:2px 4px;">{chart.atmakaraka}</td></tr>
            <tr><td style="color:{_dc_txt};padding:2px 4px;">House System</td><td style="color:{_dc_val};font-weight:800;padding:2px 4px;">Equal (Vedic) / Placidus</td></tr>
          </table>
        </div>""", unsafe_allow_html=True)

                    # Swiss Ephemeris Planet Table
                    SYMS_CONS = {"Sun":"☉","Moon":"☽","Mars":"♂","Mercury":"☿","Jupiter":"♃","Venus":"♀","Saturn":"♄","Rahu":"☊","Ketu":"☋"}
                    P_NC = {"Sun":"#FFB800","Moon":"#88AAFF","Mars":"#FF4444","Mercury":"#44DD88","Jupiter":"#FFD700","Venus":"#FF88CC","Saturn":"#AAAACC","Rahu":"#CC88FF","Ketu":"#AA6633"}
                    eph_rows = []
                    for pn in ["Sun","Moon","Mars","Mercury","Jupiter","Venus","Saturn","Rahu","Ketu"]:
                        pp_o = chart.planets.get(pn)
                        if not pp_o:
                            continue
                        sym = SYMS_CONS.get(pn, pn[:2])
                        nc = P_NC.get(pn, "#CCC")
                        retro = "℞" if pp_o.is_retrograde else ""
                        combust = "☌" if pp_o.is_combust else ""
                        d_label, d_pts, _ = get_varga_dignity_info(pn, pp_o.sign_name, affliction_engine)
                        eph_rows.append(
                            f'<tr><td style="color:{nc};font-weight:900;padding:2px 5px;font-size:13px;">{sym}</td>'
                            f'<td style="color:{_dc_val};padding:2px 4px;font-size:11px;">{pn}{retro}{combust}</td>'
                            f'<td style="color:{nc};padding:2px 4px;font-size:11px;">{pp_o.sign_name[:3]}</td>'
                            f'<td style="color:{_dc_txt};padding:2px 4px;font-size:11px;">{pp_o.sign_degree:.2f}°</td>'
                            f'<td style="color:{_dc_txt};padding:2px 4px;font-size:10px;">{pp_o.nakshatra_name[:5]}-P{pp_o.nakshatra_pada}</td>'
                            f'<td style="color:{_pts_good if d_pts>=15 else (_pts_mid if d_pts>=10 else _pts_low)};padding:2px 4px;font-size:10px;font-weight:700;">{d_pts}pts</td>'
                            f'</tr>'
                        )
                    st.markdown(f"""
        <div style="background:{_dc_bg};border:1px solid {_dc_bdr};border-radius:8px;padding:8px 10px;margin-bottom:8px;box-shadow: 0 1px 4px rgba(0,0,0,0.05);">
          <div style="color:{_dc_hdr};font-weight:900;font-size:12px;margin-bottom:6px;letter-spacing:0.5px;">🪐 SWISS EPHEMERIS — {varga_choice} {v_name}</div>
          <table style="width:100%;border-collapse:collapse;font-size:11px;">
            <tr style="background:{_dc_row};">
              <th style="color:{_dc_th_col};padding:2px 4px;text-align:left;font-size:10px;">Sym</th>
              <th style="color:{_dc_th_col};padding:2px 4px;text-align:left;font-size:10px;">Planet</th>
              <th style="color:{_dc_th_col};padding:2px 4px;text-align:left;font-size:10px;">Sign</th>
              <th style="color:{_dc_th_col};padding:2px 4px;text-align:left;font-size:10px;">Deg°</th>
              <th style="color:{_dc_th_col};padding:2px 4px;text-align:left;font-size:10px;">Nakshatra</th>
              <th style="color:{_dc_th_col};padding:2px 4px;text-align:left;font-size:10px;">Bala</th>
            </tr>
            {"".join(eph_rows)}
          </table>
        </div>""", unsafe_allow_html=True)

                    # Panchang Quick Console
                    st.markdown(f"""
        <div style="background:{_dc_bg};border:1px solid {_dc_bdr};border-radius:8px;padding:8px 10px;margin-bottom:8px;">
          <div style="color:{_dc_hdr};font-weight:900;font-size:12px;margin-bottom:6px;">🌙 PANCHANG CONSOLE</div>
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:4px;font-size:11px;">
            <div style="color:{_dc_txt};">Tithi: <span style="color:{_dc_val};font-weight:800;">{chart.panchang.tithi_name}</span></div>
            <div style="color:{_dc_txt};">Vara: <span style="color:{_dc_val};font-weight:800;">{chart.panchang.vara_name}</span></div>
            <div style="color:{_dc_txt};">Nakshatra: <span style="color:{_dc_val};font-weight:800;">{chart.panchang.nakshatra_name}</span></div>
            <div style="color:{_dc_txt};">Yoga: <span style="color:{_dc_val};font-weight:800;">{chart.panchang.yoga_name}</span></div>
            <div style="color:{_dc_txt};">Karana: <span style="color:{_dc_val};font-weight:800;">{chart.panchang.karana_name}</span></div>
            <div style="color:{_dc_txt};">Atmakaraka: <span style="color:{_pts_mid};font-weight:900;">{chart.atmakaraka}</span></div>
          </div>
        </div>""", unsafe_allow_html=True)

                    # 9×9 Aspect Orb Matrix
                    st.markdown(f'<div style="color:{_dc_hdr};font-weight:900;font-size:12px;margin-bottom:4px;letter-spacing:0.5px;">🔬 NATAL ASPECT ORB MATRIX (9×9)</div>', unsafe_allow_html=True)
                    orb_html = render_aspect_orb_matrix_html(chart, dark_bg=is_astrallis_mode or is_night_mode)
                    st.markdown(orb_html, unsafe_allow_html=True)

                else:
                    # Standard panel for non-Astrallis modes
                    st.markdown(f"#### 🌟 {varga_choice} ({v_name}) सारांश एवं पंचांग")
                    p_col1, p_col2 = st.columns(2)
                    p_col1.markdown(f"- **वर्ग लग्न:** {v_lagna_sign} ({v_lagna_id})")
                    p_col1.markdown(f"- **जन्म लग्न (D1):** {chart.lagna_sign_name} ({chart.lagna_sign_id})")
                    p_col1.markdown(f"- **आत्मकारक (AK):** {chart.atmakaraka}")
                    p_col2.markdown(f"- **तिथि:** {chart.panchang.tithi_name}")
                    p_col2.markdown(f"- **नक्षत्र:** {chart.panchang.nakshatra_name}")
                    p_col2.markdown(f"- **वार:** {chart.panchang.vara_name}")

                    # Dynamic Planetary Dignity & Strength Chart with Toggle Switch (Meters vs Columns)
                    c_gh1, c_gh2 = st.columns([1.5, 1.2])
                    with c_gh1:
                        st.markdown(f"#### 📊 {varga_choice} ({v_name}) ग्रह गरिमा एवं बल")
                    with c_gh2:
                        graph_style_choice = st.radio(
                            "ग्राफ़ शैली",
                            ["📊 हॉरिजॉन्टल मीटर", "📈 वर्टिकल कॉलम"],
                            index=0 if "हॉरिजॉन्टल" in st.session_state.get("varga_graph_style", "हॉरिजॉन्टल") else 1,
                            horizontal=True,
                            key="varga_graph_style_radio",
                            label_visibility="collapsed"
                        )
                        st.session_state.varga_graph_style = graph_style_choice

                    varga_items = []
                    target_planets_order = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]
                    _GRAHA_SYMS = {"Sun": "☉ सूर्य", "Moon": "☽ चन्द्र", "Mars": "♂ मंगल", "Mercury": "☿ बुध", "Jupiter": "♃ गुरु", "Venus": "♀ शुक्र", "Saturn": "♄ शनि", "Rahu": "☊ राहु", "Ketu": "☋ केतु"}
                    _P_COLS = {"Sun":"#E11D48","Moon":"#2563EB","Mars":"#DC2626","Mercury":"#059669","Jupiter":"#D97706","Venus":"#DB2777","Saturn":"#475569","Rahu":"#7C3AED","Ketu":"#B45309"}

                    for p_name in target_planets_order:
                        vp_obj = target_varga.planets.get(p_name) if target_varga else None
                        if vp_obj:
                            d_lbl, d_pts, _ = get_varga_dignity_info(p_name, vp_obj.sign_name, affliction_engine)
                        else:
                            d_lbl, d_pts = "सम (Neutral)", 7.0
                        varga_items.append({
                            "name": p_name,
                            "symbol": _GRAHA_SYMS.get(p_name, p_name),
                            "color": _P_COLS.get(p_name, "#2563EB"),
                            "dignity": d_lbl,
                            "score": d_pts
                        })

                    _is_dark = is_astrallis_mode or is_night_mode
                    if "हॉरिजॉन्टल" in graph_style_choice:
                        st.markdown(render_styled_meters_html(varga_items, max_val=20, is_dark=_is_dark), unsafe_allow_html=True)
                    else:
                        st.markdown(generate_styled_vertical_svg(varga_items, max_val=20, is_dark=_is_dark), unsafe_allow_html=True)

                    with st.expander("🏆 समग्र विंशोपक बल (20 Point Shadvarga Bala)", expanded=False):
                        vimsopaka = VargaCalculator.calculate_vimsopaka_bala(chart)
                        vims_items = []
                        for p_name in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]:
                            v_sc = float(vimsopaka.get(p_name, 10.0))
                            v_qual = "अति उत्तम" if v_sc >= 15 else ("उत्तम" if v_sc >= 10 else "मध्यम")
                            vims_items.append({
                                "name": p_name,
                                "symbol": _GRAHA_SYMS.get(p_name, p_name),
                                "color": _P_COLS.get(p_name, "#2563EB"),
                                "dignity": f"{v_qual} ({v_sc:.1f})",
                                "score": v_sc
                            })
                        if "हॉरिजॉन्टल" in graph_style_choice:
                            st.markdown(render_styled_meters_html(vims_items, max_val=20, is_dark=_is_dark), unsafe_allow_html=True)
                        else:
                            st.markdown(generate_styled_vertical_svg(vims_items, max_val=20, is_dark=_is_dark), unsafe_allow_html=True)

        # ─── Pancha Mahapurusha Yogas & Key Yogas Banner ───
        try:
            _yogas_found = []
            # Pancha Mahapurusha Yogas
            _kendra_houses = [1, 4, 7, 10]
            _mars = chart.planets.get("Mars")
            if _mars and _mars.house_from_lagna in _kendra_houses and _mars.sign_name in ["Aries", "Scorpio", "Capricorn"]:
                _yogas_found.append(("🔴 रुचक महापुरुष योग (Ruchaka)", "मंगल केंद्र में स्व/उच्च राशि — अदम्य साहस, भूमि-भवन लाभ, नेतृत्व एवं सैन्य/प्रशासनिक पराक्रम।"))
            _merc = chart.planets.get("Mercury")
            if _merc and _merc.house_from_lagna in _kendra_houses and _merc.sign_name in ["Gemini", "Virgo"]:
                _yogas_found.append(("🟢 भद्र महापुरुष योग (Bhadra)", "बुध केंद्र में स्व/उच्च राशि — असाधारण बौद्धिक प्रखरता, वाणी प्रभाव, व्यापारिक कुशलता एवं दीर्घायु।"))
            _jup = chart.planets.get("Jupiter")
            if _jup and _jup.house_from_lagna in _kendra_houses and _jup.sign_name in ["Sagittarius", "Pisces", "Cancer"]:
                _yogas_found.append(("🟡 हंस महापुरुष योग (Hamsa)", "गुरु केंद्र में स्व/उच्च राशि — सात्विक बुद्धि, आध्यात्मिक तेज, पूज्य सम्मान एवं सदाचार।"))
            _ven = chart.planets.get("Venus")
            if _ven and _ven.house_from_lagna in _kendra_houses and _ven.sign_name in ["Taurus", "Libra", "Pisces"]:
                _yogas_found.append(("🌸 मालव्य महापुरुष योग (Malavya)", "शुक्र केंद्र में स्व/उच्च राशि — राजसी वैभव, कलात्मक सौंदर्य, ऐश्वर्य, सुखी वैवाहिक जीवन व वाहन सुख।"))
            _sat = chart.planets.get("Saturn")
            if _sat and _sat.house_from_lagna in _kendra_houses and _sat.sign_name in ["Capricorn", "Aquarius", "Libra"]:
                _yogas_found.append(("🪐 शश महापुरुष योग (Sasa)", "शनि केंद्र में स्व/उच्च राशि — जननायक, अपार धैर्य, गुप्त अधिकार, राजनीतिक प्रभाव एवं स्थिर सत्ता।"))

            # Gajakesari Yoga
            _moon = chart.planets.get("Moon")
            if _jup and _moon:
                _jm_dist = ((_jup.house_from_lagna - _moon.house_from_lagna + 12) % 12) + 1
                if _jm_dist in [1, 4, 7, 10]:
                    _yogas_found.append(("🐘 गजकेसरी योग (Gajakesari)", "गुरु चन्द्र से केंद्र में स्थित — अपार यश, विद्वता, निर्भय व्यक्तित्व एवं सर्वत्र आदर-सत्कार।"))

            # Budhaditya Yoga
            _sun = chart.planets.get("Sun")
            if _sun and _merc and _sun.sign_id == _merc.sign_id:
                _diff = abs(_sun.longitude - _merc.longitude)
                if _diff > 180: _diff = 360 - _diff
                if _diff <= 10.0:
                    _comb_txt = " (बुध अस्त नहीं)" if not _merc.is_combust else " (अंश निकट)"
                    _yogas_found.append(("⚡ बुधादित्य योग (Budhaditya)", f"सूर्य-बुध युति (अंतर: {_diff:.1f}°){_comb_txt} — तीक्ष्ण बुद्धि, प्रशासनिक कुशलता व व्यावसायिक सफलता।"))

            if _yogas_found:
                _y_cards = []
                for _yt, _yd in _yogas_found:
                    _y_cards.append(f'<div style="background:#FFFFFF; border:1px solid #CBD5E1; border-radius:6px; padding:6px 10px; margin-bottom:4px;"><span style="font-weight:900; color:#1E3A8A; font-size:12px;">{_yt}</span>: <span style="font-size:11.5px; color:#334155;">{_yd}</span></div>')
                _yoga_banner_html = f'<div style="background:linear-gradient(135deg, #EFF6FF 0%, #F0FDF4 100%); border:1.5px solid #93C5FD; border-radius:8px; padding:10px 12px; margin-bottom:12px;"><div style="font-weight:900; color:#1E40AF; font-size:13px; margin-bottom:6px; display:flex; align-items:center; gap:6px;"><span>🏆 <b>कुण्डली प्रमुख महा-योग उद्घोष (Major Planetary Yogas Detected)</b></span></div>{"".join(_y_cards)}</div>'
                st.markdown(_yoga_banner_html, unsafe_allow_html=True)
        except Exception as _ey:
            pass

        st.markdown(f"### 🪐 {varga_choice} ({v_name}) चक्र — नवग्रह स्पष्ट स्थिति, भाव एवं गरिमा तालिका")
        p_data = []
        target_planets_order = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]
        for name_p in target_planets_order:
            vp_obj = target_varga.planets.get(name_p) if target_varga else None
            if not vp_obj:
                continue
            d1_p = chart.planets.get(name_p)

            d_label, d_pts, d_impact = get_varga_dignity_info(name_p, vp_obj.sign_name, affliction_engine)
            h_lord = SIGN_LORDS.get(vp_obj.sign_name, "-")

            h_num = vp_obj.house_number
            h_suffix = "st" if h_num == 1 else "nd" if h_num == 2 else "rd" if h_num == 3 else "th"
            h_name_hi = {
                1: "तनु (1st)", 2: "धन (2nd)", 3: "सहज (3rd)", 4: "सुख (4th)",
                5: "सुत (5th)", 6: "रिपु (6th)", 7: "जाया (7th)", 8: "आयु (8th)",
                9: "धर्म (9th)", 10: "कर्म (10th)", 11: "लाभ (11th)", 12: "व्यय (12th)"
            }.get(h_num, f"{h_num}{h_suffix}")

            p_data.append({
                "ग्रह (Graha)": name_p,
                "वर्ग राशि (Sign)": vp_obj.sign_name,
                "राशि स्वामी (Lord)": h_lord,
                "वर्ग अंश (Degree)": f"{vp_obj.degree_in_varga:.2f}°",
                "वर्ग भाव (Varga House)": f"{h_num}{h_suffix} भाव ({h_name_hi})",
                "वर्ग गरिमा (Dignity)": d_label,
                "D1 राशि (Ref)": d1_p.sign_name if d1_p else "-",
                "D1 भाव (Ref)": f"{d1_p.house_from_lagna}th House" if d1_p else "-",
                "गति (Motion)": "वक्री (R)" if (d1_p and d1_p.is_retrograde) else "मार्गी",
                "अवस्था / शास्त्रीय प्रभाव": d_impact,
            })

        # ─── Render Rich Classical Planetary Dignity HTML Table ───
        if is_astrallis_mode:
            _t_bg = "#050811"; _t_th_bg = "#0A1628"; _t_bdr = "#1E3A5F"; _t_txt = "#CBD5E1"; _t_th = "#00E5FF"; _t_alt = "#070E1C"
        elif is_night_mode:
            _t_bg = "#111827"; _t_th_bg = "#1F2937"; _t_bdr = "#374151"; _t_txt = "#E2E8F0"; _t_th = "#F59E0B"; _t_alt = "#172033"
        else:  # Day Mode (Grahalakshanam Royal Azure & Cyan)
            _t_bg = "#FFFFFF"; _t_th_bg = "#0070C0"; _t_bdr = "#00B0F0"; _t_txt = "#0F172A"; _t_th = "#FFFFFF"; _t_alt = "#F2F4F7"

        _GRAHA_SYMS = {"Sun": "☉ सूर्य", "Moon": "☽ चन्द्र", "Mars": "♂ मंगल", "Mercury": "☿ बुध", "Jupiter": "♃ गुरु", "Venus": "♀ शुक्र", "Saturn": "♄ शनि", "Rahu": "☊ राहु", "Ketu": "☋ केतु"}
        _P_COLS = {"Sun":"#E11D48","Moon":"#2563EB","Mars":"#DC2626","Mercury":"#059669","Jupiter":"#D97706","Venus":"#DB2777","Saturn":"#475569","Rahu":"#7C3AED","Ketu":"#B45309"}

        t_rows = []
        for idx, row in enumerate(p_data):
            p_nm = row["ग्रह (Graha)"]
            sym_nm = _GRAHA_SYMS.get(p_nm, p_nm)
            pc = _P_COLS.get(p_nm, "#2563EB")
            d_lbl = row["वर्ग गरिमा (Dignity)"]

            # Dignity badge styling (Authentic Grahalakshanam: Lime Exalted, Red Debilitated, Cobalt Own)
            if "उच्च" in d_lbl:
                b_bg, b_fg, b_bdr = "#BCE636", "#1E293B", "#A4D024"
            elif "मूलत्रिकोण" in d_lbl:
                b_bg, b_fg, b_bdr = "#CAF0F8", "#0077B6", "#00B4D8"
            elif "स्व" in d_lbl:
                b_bg, b_fg, b_bdr = "#0073CF", "#FFFFFF", "#00B0F0"
            elif "नीच" in d_lbl:
                b_bg, b_fg, b_bdr = "#FF0000", "#FFFFFF", "#CC0000"
            elif "शत्रु" in d_lbl:
                b_bg, b_fg, b_bdr = "#FFE2E5", "#D92D20", "#FCA5A5"
            elif "मित्र" in d_lbl:
                b_bg, b_fg, b_bdr = "#E0F2FE", "#0284C7", "#7DD3FC"
            else:
                b_bg, b_fg, b_bdr = "#F2F4F7", "#334155", "#CBD5E1"

            # Motion badge
            is_ret = "वक्री" in row["गति (Motion)"]
            m_bg = "#FEE2E2" if is_ret else "#ECFDF5"
            m_fg = "#DC2626" if is_ret else "#059669"
            m_bdr = "#F87171" if is_ret else "#86EFAC"

            row_bg = _t_alt if idx % 2 == 1 else _t_bg

            t_rows.append(
                f'<tr style="background:{row_bg};border-bottom:1px solid {_t_bdr};">'
                f'<td style="padding:7px 10px;font-weight:900;color:{pc};white-space:nowrap;font-size:12.5px;">{sym_nm}</td>'
                f'<td style="padding:7px 10px;font-weight:700;color:{_t_txt};font-size:12px;">{row["वर्ग राशि (Sign)"]}</td>'
                f'<td style="padding:7px 10px;color:{_t_txt};font-size:12px;">{row["राशि स्वामी (Lord)"]}</td>'
                f'<td style="padding:7px 10px;font-weight:700;color:{pc};font-size:12px;font-family:monospace;">{row["वर्ग अंश (Degree)"]}</td>'
                f'<td style="padding:7px 10px;color:{_t_txt};font-size:12px;">{row["वर्ग भाव (Varga House)"]}</td>'
                f'<td style="padding:7px 10px;"><span style="background:{b_bg};color:{b_fg};border:1px solid {b_bdr};padding:2px 8px;border-radius:6px;font-size:11px;font-weight:800;white-space:nowrap;">{d_lbl}</span></td>'
                f'<td style="padding:7px 10px;color:{_t_txt};font-size:11.5px;">{row["D1 राशि (Ref)"]} / {row["D1 भाव (Ref)"]}</td>'
                f'<td style="padding:7px 10px;"><span style="background:{m_bg};color:{m_fg};border:1px solid {m_bdr};padding:2px 7px;border-radius:6px;font-size:11px;font-weight:800;">{row["गति (Motion)"]}</span></td>'
                f'<td style="padding:7px 10px;color:{_t_txt};font-size:11.5px;">{row["अवस्था / शास्त्रीय प्रभाव"]}</td>'
                f'</tr>'
            )

        table_html = f"""
    <div style="width:100%;overflow-x:auto;background:{_t_bg};border:1.5px solid {_t_bdr};border-radius:10px;box-shadow:0 2px 8px rgba(0,0,0,0.04);margin-bottom:14px;">
      <table style="width:100%;border-collapse:collapse;text-align:left;font-family:inherit;">
        <thead>
          <tr style="background:{_t_th_bg};border-bottom:2px solid {_t_bdr};">
            <th style="padding:9px 10px;color:{_t_th};font-weight:900;font-size:12px;letter-spacing:0.3px;">ग्रह (Graha)</th>
            <th style="padding:9px 10px;color:{_t_th};font-weight:900;font-size:12px;letter-spacing:0.3px;">वर्ग राशि (Sign)</th>
            <th style="padding:9px 10px;color:{_t_th};font-weight:900;font-size:12px;letter-spacing:0.3px;">स्वामी (Lord)</th>
            <th style="padding:9px 10px;color:{_t_th};font-weight:900;font-size:12px;letter-spacing:0.3px;">वर्ग अंश (Deg)</th>
            <th style="padding:9px 10px;color:{_t_th};font-weight:900;font-size:12px;letter-spacing:0.3px;">वर्ग भाव (House)</th>
            <th style="padding:9px 10px;color:{_t_th};font-weight:900;font-size:12px;letter-spacing:0.3px;">गरिमा (Dignity)</th>
            <th style="padding:9px 10px;color:{_t_th};font-weight:900;font-size:12px;letter-spacing:0.3px;">D1 संदर्भ (Ref)</th>
            <th style="padding:9px 10px;color:{_t_th};font-weight:900;font-size:12px;letter-spacing:0.3px;">गति (Motion)</th>
            <th style="padding:9px 10px;color:{_t_th};font-weight:900;font-size:12px;letter-spacing:0.3px;">अवस्था / शास्त्रीय फल</th>
          </tr>
        </thead>
        <tbody>
          {"".join(t_rows)}
        </tbody>
      </table>
    </div>"""
        st.markdown(table_html, unsafe_allow_html=True)

        # ═══════════════════════════════════════════════════════════════════════
        # 🏛️ द्वादश भाव सम्पूर्ण शास्त्रीय तालिका (12 Houses Master Analysis Table)
        # ═══════════════════════════════════════════════════════════════════════
        st.markdown(f"### 🏛️ {varga_choice} ({v_name}) चक्र — द्वादश भाव सम्पूर्ण शास्त्रीय स्थिति, दृष्टि, गरिमा व गुणधर्म तालिका")
        if varga_choice == "D1":
            st.caption("महर्षि पराशर (BPHS), श्रीपति एवं फलदीपिका अनुसार जन्म लग्न (D1) व भाव चलित चक्र के द्वादश भावों की सूक्ष्म स्थिति, स्थित ग्रह, दृष्टियां, भाव मध्य, नक्षत्र-पद व गुणधर्म:")
        else:
            st.caption(f"महर्षि पराशर (BPHS) अनुसार **{varga_choice} ({v_name})** चक्र के द्वादश भावों ({v_lagna_sign} लग्न से), वर्ग में स्थित ग्रह, दृष्टि संबंध, मूल D1 संदर्भ, वर्ग गरिमा व गुणधर्म:")

        try:
            _BHAVA_META = {
                1: {"name": "तनु (Lagna)", "sanskrit": "प्रथम", "sannya": "🏛️ केंद्र / 👑 त्रिकोण", "tattva": "धर्म • अग्नि", "karakas": "☉ सूर्य (काया/आरोग्य)", "signif": "शारीरिक गठन, स्वास्थ्य, वर्ण, आत्मबल, स्वभाव"},
                2: {"name": "धन (Dhana)", "sanskrit": "द्वितीय", "sannya": "🛡️ मारक / पणफर", "tattva": "अर्थ • पृथ्वी", "karakas": "♃ गुरु (धन), ☿ बुध (वाणी)", "signif": "धन-संपत्ति, कुटुंब, वाणी, प्रारंभिक शिक्षा, मुख"},
                3: {"name": "सहज (Bhratri)", "sanskrit": "तृतीय", "sannya": "📈 उपचय / आपोक्लिम", "tattva": "काम • वायु", "karakas": "♂ मंगल (पराक्रम, भ्रातृ)", "signif": "साहस, पराक्रम, छोटे भाई-बहन, लघु यात्रा, लेखन"},
                4: {"name": "सुख (Matri)", "sanskrit": "चतुर्थ", "sannya": "🏛️ केंद्र (सुख स्थान)", "tattva": "मोक्ष • जल", "karakas": "☽ चन्द्र (माता), ♀ शुक्र (वाहन)", "signif": "माता, गृह, भूमि, वाहन, मानसिक शांति, हृदय"},
                5: {"name": "सुत (Putra)", "sanskrit": "पंचम", "sannya": "👑 त्रिकोण (पुण्य स्थान)", "tattva": "धर्म • अग्नि", "karakas": "♃ गुरु (संतान, बुद्धि)", "signif": "संतान, बुद्धि, विद्या, पूर्वपुण्य, मंत्र-साधना"},
                6: {"name": "रिपु (Ari)", "sanskrit": "षष्ठ", "sannya": "⚡ त्रिक/दुःस्थान • 📈 उपचय", "tattva": "अर्थ • पृथ्वी", "karakas": "♂ मंगल (शत्रु), ♄ शनि (रोग/ऋण)", "signif": "शत्रु, रोग, ऋण, प्रतियोगिता, सेवा, ननिहाल"},
                7: {"name": "जाया (Kalatra)", "sanskrit": "सप्तम", "sannya": "🏛️ केंद्र • 🛡️ मारक", "tattva": "काम • वायु", "karakas": "♀ शुक्र (दाम्पत्य/काम)", "signif": "जीवनसाथी, विवाह, व्यापार, साझेदारी, लोक-संबंध"},
                8: {"name": "आयु (Randhra)", "sanskrit": "अष्टम", "sannya": "⚡ त्रिक/दुःस्थान • पणफर", "tattva": "मोक्ष • जल", "karakas": "♄ शनि (आयु/गूढ़ रहस्य)", "signif": "आयु, मृत्यु, गूढ़ ज्ञान, संकट, गुप्त धन, आकस्मिकता"},
                9: {"name": "धर्म (Bhagya)", "sanskrit": "नवम", "sannya": "👑 त्रिकोण (भाग्य स्थान)", "tattva": "धर्म • अग्नि", "karakas": "♃ गुरु (धर्म/भाग्य), ☉ सूर्य (पिता)", "signif": "भाग्य, धर्म, गुरु, पिता, तीर्थाटन, उच्च शिक्षा"},
                10: {"name": "कर्म (Karma)", "sanskrit": "दशम", "sannya": "🏛️ केंद्र • 📈 उपचय (राज्य)", "tattva": "अर्थ • पृथ्वी", "karakas": "☉ सूर्य, ☿ बुध, ♃ गुरु, ♄ शनि", "signif": "आजीविका, पद-प्रतिष्ठा, राज्य, अधिकार, कीर्ति"},
                11: {"name": "लाभ (Labha)", "sanskrit": "एकादश", "sannya": "📈 उपचय • पणफर", "tattva": "काम • वायु", "karakas": "♃ गुरु (लाभ/आय)", "signif": "आय, लाभ, ज्येष्ठ भ्राता, मित्र, मनोरथ सिद्धि"},
                12: {"name": "व्यय (Vyaya)", "sanskrit": "द्वादश", "sannya": "⚡ त्रिक/दुःस्थान • आपोक्लिम", "tattva": "मोक्ष • जल", "karakas": "♄ शनि (व्यय), ☋ केतु (मोक्ष)", "signif": "व्यय, मोक्ष, विदेश गमन, अस्पताल, शयन सुख"}
            }

            _SIGN_HI = {
                'Aries': 'मेष', 'Taurus': 'वृषभ', 'Gemini': 'मिथुन', 'Cancer': 'कर्क',
                'Leo': 'सिंह', 'Virgo': 'कन्या', 'Libra': 'तुला', 'Scorpio': 'वृश्चिक',
                'Sagittarius': 'धनु', 'Capricorn': 'मकर', 'Aquarius': 'कुम्भ', 'Pisces': 'मीन'
            }

            _SIGN_NATURE = {
                'Aries': 'चर (Movable)', 'Taurus': 'स्थिर (Fixed)', 'Gemini': 'द्विस्वभाव (Dual)',
                'Cancer': 'चर (Movable)', 'Leo': 'स्थिर (Fixed)', 'Virgo': 'द्विस्वभाव (Dual)',
                'Libra': 'चर (Movable)', 'Scorpio': 'स्थिर (Fixed)', 'Sagittarius': 'द्विस्वभाव (Dual)',
                'Capricorn': 'चर (Movable)', 'Aquarius': 'स्थिर (Fixed)', 'Pisces': 'द्विस्वभाव (Dual)'
            }

            _GRAHA_SYMS = {
                'Sun': '☉ सूर्य', 'Moon': '☽ चन्द्र', 'Mars': '♂ मंगल', 'Mercury': '☿ बुध',
                'Jupiter': '♃ गुरु', 'Venus': '♀ शुक्र', 'Saturn': '♄ शनि', 'Rahu': '☊ राहु', 'Ketu': '☋ केतु'
            }

            _GRAHA_COLS = {
                'Sun': '#E11D48', 'Moon': '#2563EB', 'Mars': '#DC2626', 'Mercury': '#059669',
                'Jupiter': '#D97706', 'Venus': '#DB2777', 'Saturn': '#475569', 'Rahu': '#7C3AED', 'Ketu': '#B45309'
            }

            # Active varga reference
            _cur_v = target_varga if target_varga else chart.vargas.get("D1")
            _cur_v_planets = _cur_v.planets if _cur_v else {}
            _active_lagna_id = _cur_v.lagna_sign_id if _cur_v else chart.lagna_sign_id
            _active_lagna_name = _cur_v.lagna_sign_name if _cur_v else chart.lagna_sign_name

            # D1 Bhava chalit calculation (for D1 specific comparison)
            _bc_res = default_chart_calculator.calculate_bhava_chalit(chart)
            _bc_items = _bc_res.get('planet_positions', []) if isinstance(_bc_res, dict) else []
            _cusps_list = _bc_res.get('bhava_cusps', []) if isinstance(_bc_res, dict) else []

            # Parashari Drishtis helper for the ACTIVE varga
            def _get_active_varga_drishtis(target_h):
                asp_list = []
                for p_name, vp in _cur_v_planets.items():
                    src_h = vp.house_number
                    dist = ((target_h - src_h + 12) % 12) + 1
                    is_asp = False
                    asp_lbl = ""
                    if dist == 7:
                        is_asp = True
                        asp_lbl = "७म दृष्टि"
                    elif p_name == "Mars" and dist in (4, 8):
                        is_asp = True
                        asp_lbl = f"{dist}थी दृष्टि"
                    elif p_name in ("Jupiter", "Rahu", "Ketu") and dist in (5, 9):
                        is_asp = True
                        asp_lbl = f"{dist}वीं दृष्टि"
                    elif p_name == "Saturn" and dist in (3, 10):
                        is_asp = True
                        asp_lbl = f"{dist}री दृष्टि"

                    if is_asp:
                        d1_ref = chart.planets.get(p_name)
                        is_combust = d1_ref.is_combust if d1_ref else False
                        is_benefic = p_name in ("Jupiter", "Venus") or (p_name == "Mercury" and not is_combust) or (p_name == "Moon" and vp.degree_in_varga > 10)
                        asp_list.append((p_name, asp_lbl, is_benefic))
                return asp_list

            # Summary metrics counts for this active varga
            _occ_h_count = len(set(vp.house_number for vp in _cur_v_planets.values()))
            _vac_h_count = 12 - _occ_h_count
            _kendra_occ = sum(1 for vp in _cur_v_planets.values() if vp.house_number in (1, 4, 7, 10))
            _trik_occ = sum(1 for vp in _cur_v_planets.values() if vp.house_number in (1, 5, 9))
            _upachaya_occ = sum(1 for vp in _cur_v_planets.values() if vp.house_number in (3, 6, 10, 11))

            # ─── Top Bhava Vital Summary Cards for Active Varga ───
            bc_col_m1, bc_col_m2, bc_col_m3, bc_col_m4 = st.columns(4)
            with bc_col_m1:
                st.metric("🏛️ केंद्र भाव (1, 4, 7, 10)", f"{_kendra_occ} ग्रह स्थित", "विष्णु स्थान • जीवन आधार")
            with bc_col_m2:
                st.metric("👑 त्रिकोण भाव (1, 5, 9)", f"{_trik_occ} ग्रह स्थित", "लक्ष्मी स्थान • धर्म व पुण्य")
            with bc_col_m3:
                st.metric("📈 उपचय भाव (3, 6, 10, 11)", f"{_upachaya_occ} ग्रह स्थित", "पुरुषार्थ व सतत प्रगति")
            with bc_col_m4:
                if varga_choice == "D1":
                    _tot_shift = sum(1 for it in _bc_items if it.get("rashi_house") != it.get("chalit_house"))
                    shift_badge_txt = f"{_tot_shift} ग्रह चलित शिफ्ट" if _tot_shift > 0 else "पूर्ण समरूप (0 शिफ्ट)"
                    st.metric("🔄 चलित चक्र स्थिति", shift_badge_txt, f"{_occ_h_count} भाव सक्रिय / {_vac_h_count} रिक्त")
                else:
                    st.metric(f"🎯 {varga_choice} वर्ग लग्न", f"{_active_lagna_name} ({_active_lagna_id})", f"{_occ_h_count} भाव सक्रिय / {_vac_h_count} रिक्त")

            b_rows = []
            for b in range(1, 13):
                meta = _BHAVA_META[b]
                # Sign on this house in the active varga
                s_id = ((_active_lagna_id - 1 + b - 1) % 12) + 1
                s_name = SIGN_NAMES[s_id - 1]
                s_name_hi = _SIGN_HI.get(s_name, s_name)
                s_nat = _SIGN_NATURE.get(s_name, "स्थिर")
                s_lord = SIGN_LORDS.get(s_name, "-")

                # Lord in the active varga
                vp_lord = _cur_v_planets.get(s_lord)
                if vp_lord:
                    d_lbl, _, _ = get_varga_dignity_info(s_lord, vp_lord.sign_name, affliction_engine)
                    lord_txt = f"<b style='color:{_GRAHA_COLS.get(s_lord, '#1E40AF')};'>{_GRAHA_SYMS.get(s_lord, s_lord)}</b><br><span style='font-size:11px;color:{_t_txt};'>{vp_lord.house_number}वें भाव ({_SIGN_HI.get(vp_lord.sign_name, vp_lord.sign_name)} {vp_lord.degree_in_varga:.1f}°)<br><span style='font-size:10.5px;color:#0284C7;font-weight:700;'>[{d_lbl}]</span></span>"
                else:
                    lord_txt = s_lord

                # Cusp or Varga span column
                if varga_choice == "D1":
                    cusp = next((c for c in _cusps_list if c.get('bhava') == b), None)
                    c_deg = cusp.get('cusp_degree', 0.0) if cusp else 0.0
                    c_lon = cusp.get('cusp_longitude', 0.0) if cusp else 0.0
                    arambha_deg = (c_deg - 15.0 + 30.0) % 30.0
                    anta_deg = (c_deg + 15.0) % 30.0
                    nak_idx = int((c_lon % 360.0) / (360.0 / 27.0))
                    nak = NAKSHATRAS[nak_idx]
                    deg_in_nak = (c_lon % 360.0) - (nak_idx * (360.0 / 27.0))
                    pada = int(deg_in_nak / (360.0 / 108.0)) + 1
                    cusp_html = f"<b style='font-family:monospace;color:{_t_th if is_night_mode or is_astrallis_mode else '#0070C0'};font-size:12px;'>{c_deg:.2f}°</b><br><span style='font-size:11px;color:{_t_txt};'>विस्तार: {arambha_deg:.1f}°–{anta_deg:.1f}°<br>🌟 <b>{nak['name']}</b> ({nak['lord']}) पद-{pada}</span>"
                else:
                    _v_div = getattr(_cur_v, 'division', 1) or 1
                    _v_span = 30.0 / _v_div
                    cusp_html = f"<b style='font-family:monospace;color:{_t_th if is_night_mode or is_astrallis_mode else '#0070C0'};font-size:12px;'>{varga_choice} वर्ग</b><br><span style='font-size:11px;color:{_t_txt};'>विभाजन: {_v_span:.2f}° प्रति भाग<br>लग्न: {_active_lagna_name} ({_active_lagna_id})</span>"

                # Occupying planets in this varga house
                occ = [vp for vp in _cur_v_planets.values() if vp.house_number == b]
                if occ:
                    occ_parts = []
                    for vp in occ:
                        pc = _GRAHA_COLS.get(vp.name, "#1E40AF")
                        d1_ref = chart.planets.get(vp.name)
                        ret_txt = " <span style='color:#DC2626;font-weight:800;'>(R)</span>" if (d1_ref and d1_ref.is_retrograde) else ""
                        comb_txt = " <span style='color:#EA580C;font-weight:800;'>(अस्त)</span>" if (d1_ref and d1_ref.is_combust) else ""
                        d_lbl, _, _ = get_varga_dignity_info(vp.name, vp.sign_name, affliction_engine)
                        d1_h_txt = f"<span style='color:#64748B;font-size:10px;'>(D1: {d1_ref.house_from_lagna} भाव)</span>" if d1_ref else ""
                        occ_parts.append(f"<div style='margin-bottom:4px;font-size:11.5px;'><b style='color:{pc};'>{_GRAHA_SYMS.get(vp.name, vp.name)}</b> {vp.degree_in_varga:.1f}°{ret_txt}{comb_txt}<br><span style='font-size:10.5px;color:#0284C7;font-weight:700;'>[{d_lbl}]</span> {d1_h_txt}</div>")
                    occ_html = "".join(occ_parts)
                else:
                    occ_html = "<span style='color:#94A3B8;font-size:11.5px;font-style:italic;'>— रिक्त भाव —</span>"

                # 5th Column: Chalit Shift (for D1) or D1 vs Varga Correlation (for D2..D60)
                if varga_choice == "D1":
                    shifts = []
                    for it in _bc_items:
                        pn = it.get('planet')
                        rh = it.get('rashi_house')
                        ch = it.get('chalit_house')
                        sym = _GRAHA_SYMS.get(pn, pn)
                        if rh == b and ch != b:
                            shifts.append(f"<span style='background:#FEE2E2;color:#DC2626;border:1px solid #FCA5A5;padding:1px 6px;border-radius:4px;font-size:10.5px;font-weight:700;display:inline-block;margin:1px;'>⚠️ {sym} ({b}➔{ch} भाव)</span>")
                        elif rh != b and ch == b:
                            shifts.append(f"<span style='background:#FEF3C7;color:#D97706;border:1px solid #FCD34D;padding:1px 6px;border-radius:4px;font-size:10.5px;font-weight:700;display:inline-block;margin:1px;'>🔄 {sym} ({rh}➔{b} भाव)</span>")
                    if shifts:
                        chalit_html = "".join(shifts)
                    else:
                        chalit_html = "<span style='background:#ECFDF5;color:#059669;border:1px solid #A7F3D0;padding:2px 7px;border-radius:4px;font-size:11px;font-weight:700;'>✅ स्थिर (समान)</span>"
                else:
                    if occ:
                        v_rel_parts = []
                        for vp in occ:
                            d1_ref = chart.planets.get(vp.name)
                            sym = _GRAHA_SYMS.get(vp.name, vp.name)
                            if d1_ref:
                                if d1_ref.house_from_lagna == b:
                                    v_rel_parts.append(f"<span style='background:#DCFCE7;color:#15803D;border:1px solid #86EFAC;padding:1px 5px;border-radius:4px;font-size:10.5px;font-weight:800;display:inline-block;margin:1px;'>🎯 {sym} समान भाव ({b}H)</span>")
                                else:
                                    v_rel_parts.append(f"<span style='background:#EFF6FF;color:#1E40AF;border:1px solid #BFDBFE;padding:1px 5px;border-radius:4px;font-size:10.5px;font-weight:700;display:inline-block;margin:1px;'>{sym} (D1: {d1_ref.house_from_lagna}H ➔ {varga_choice}: {b}H)</span>")
                        chalit_html = "".join(v_rel_parts)
                    else:
                        chalit_html = "<span style='color:#94A3B8;font-size:11px;'>— रिक्त —</span>"

                # Drishtis on this house in the active varga
                drishtis = _get_active_varga_drishtis(b)
                if drishtis:
                    d_parts = []
                    for pn, asp_lbl, is_b in drishtis:
                        sym = _GRAHA_SYMS.get(pn, pn)
                        if is_b:
                            d_parts.append(f"<span style='background:#F0FDF4;color:#16A34A;border:1px solid #BBF7D0;padding:1px 5px;border-radius:4px;font-size:10.5px;font-weight:700;margin:1px;display:inline-block;'>🟢 {sym} ({asp_lbl})</span>")
                        else:
                            d_parts.append(f"<span style='background:#FFF1F2;color:#E11D48;border:1px solid #FECDD3;padding:1px 5px;border-radius:4px;font-size:10.5px;font-weight:700;margin:1px;display:inline-block;'>🔴 {sym} ({asp_lbl})</span>")
                    drishti_html = "".join(d_parts)
                else:
                    drishti_html = "<span style='color:#94A3B8;font-size:11px;'>— दृष्टि रहित —</span>"

                # Ashtakavarga SAV points for the sign occupying this house
                sav_pts = chart.ashtakavarga.sav[s_id - 1] if hasattr(chart, 'ashtakavarga') and chart.ashtakavarga and chart.ashtakavarga.sav else 28
                if sav_pts >= 30:
                    sav_badge = f"<span style='background:#DCFCE7;color:#15803D;border:1px solid #86EFAC;padding:2px 6px;border-radius:4px;font-weight:900;font-size:11px;'>🟢 {sav_pts} (अति बलिष्ठ)</span>"
                elif sav_pts >= 28:
                    sav_badge = f"<span style='background:#E0F2FE;color:#0369A1;border:1px solid #7DD3FC;padding:2px 6px;border-radius:4px;font-weight:800;font-size:11px;'>🔵 {sav_pts} (शुभ/सामान्य)</span>"
                else:
                    sav_badge = f"<span style='background:#FFEDD5;color:#C2410C;border:1px solid #FDBA74;padding:2px 6px;border-radius:4px;font-weight:800;font-size:11px;'>🟠 {sav_pts} (अल्प बल)</span>"

                row_bg = _t_alt if b % 2 == 0 else _t_bg

                b_rows.append(
                    f'<tr style="background:{row_bg};border-bottom:1px solid {_t_bdr};">'
                    f'<td style="padding:8px 10px;font-weight:900;color:{_t_th if is_night_mode or is_astrallis_mode else "#1E3A8A"};font-size:12.5px;white-space:nowrap;">'
                    f'<b>{b} भाव</b><br><span style="font-size:12px;color:{_t_txt};">{meta["name"]}</span><br>'
                    f'<span style="font-size:10px;background:#E2E8F0;color:#334155;padding:1px 5px;border-radius:3px;font-weight:700;">{meta["sannya"]}</span><br>'
                    f'<span style="font-size:10px;color:#64748B;">{meta["tattva"]}</span></td>'
                    f'<td style="padding:8px 10px;font-size:12px;color:{_t_txt};">'
                    f'<b style="font-size:12.5px;">{s_name_hi} ({s_name})</b><br><span style="font-size:10.5px;color:#64748B;">{s_nat}</span><br>'
                    f'<div style="margin-top:4px;">{lord_txt}</div></td>'
                    f'<td style="padding:8px 10px;font-size:11.5px;color:{_t_txt};">{cusp_html}</td>'
                    f'<td style="padding:8px 10px;font-size:11.5px;color:{_t_txt};min-width:130px;">{occ_html}</td>'
                    f'<td style="padding:8px 10px;font-size:11.5px;color:{_t_txt};">{chalit_html}</td>'
                    f'<td style="padding:8px 10px;font-size:11px;color:{_t_txt};max-width:180px;">{drishti_html}</td>'
                    f'<td style="padding:8px 10px;font-size:11.5px;color:{_t_txt};white-space:nowrap;">{meta["karakas"]}</td>'
                    f'<td style="padding:8px 10px;text-align:center;">{sav_badge}</td>'
                    f'<td style="padding:8px 10px;font-size:11px;color:{_t_txt};max-width:180px;">{meta["signif"]}</td>'
                    f'</tr>'
                )

            _col5_hdr = "भाव चलित स्थानांतरण" if varga_choice == "D1" else f"D1 ➔ {varga_choice} भाव सम्बंध"
            _col3_hdr = "भाव मध्य, संधि व नक्षत्र" if varga_choice == "D1" else f"{varga_choice} वर्ग विस्तार व स्थिति"
            bhav_table_html = f"""
    <div style="width:100%;overflow-x:auto;background:{_t_bg};border:1.5px solid {_t_bdr};border-radius:10px;box-shadow:0 2px 8px rgba(0,0,0,0.04);margin-top:10px;margin-bottom:14px;">
      <table style="width:100%;border-collapse:collapse;text-align:left;font-family:inherit;">
        <thead>
          <tr style="background:{_t_th_bg};border-bottom:2px solid {_t_bdr};">
            <th style="padding:9px 10px;color:{_t_th};font-weight:900;font-size:12px;letter-spacing:0.3px;">भाव व संज्ञा (House)</th>
            <th style="padding:9px 10px;color:{_t_th};font-weight:900;font-size:12px;letter-spacing:0.3px;">राशि एवं भावेश (Sign & Lord)</th>
            <th style="padding:9px 10px;color:{_t_th};font-weight:900;font-size:12px;letter-spacing:0.3px;">{_col3_hdr}</th>
            <th style="padding:9px 10px;color:{_t_th};font-weight:900;font-size:12px;letter-spacing:0.3px;">भाव में स्थित ग्रह (Occupants)</th>
            <th style="padding:9px 10px;color:{_t_th};font-weight:900;font-size:12px;letter-spacing:0.3px;">{_col5_hdr}</th>
            <th style="padding:9px 10px;color:{_t_th};font-weight:900;font-size:12px;letter-spacing:0.3px;">भाव पर दृष्टियां (Parashari Drishti)</th>
            <th style="padding:9px 10px;color:{_t_th};font-weight:900;font-size:12px;letter-spacing:0.3px;">प्राकृतिक कारक (Karaka)</th>
            <th style="padding:9px 10px;color:{_t_th};font-weight:900;font-size:12px;letter-spacing:0.3px;text-align:center;">अष्टकवर्ग रेखाएं</th>
            <th style="padding:9px 10px;color:{_t_th};font-weight:900;font-size:12px;letter-spacing:0.3px;">मुख्य विचारणीय विषय (Significations)</th>
          </tr>
        </thead>
        <tbody>
          {"".join(b_rows)}
        </tbody>
      </table>
    </div>"""
            st.markdown(bhav_table_html, unsafe_allow_html=True)

            # Shastriya Rules Explanatory Expander
            with st.expander(f"📖 {varga_choice} ({v_name}) भाव फलादेश के मूलभूत शास्त्रीय नियम एवं सिद्धांत"):
                if varga_choice == "D1":
                    st.markdown("""
                    - **१. भाव, भावेश व कारक सिद्धांत:** किसी भी भाव का शुभ फल तब मिलता है जब — (क) भाव पर शुभ ग्रहों (गुरु, शुक्र, बुध) की दृष्टि हो, (ख) भावेश केंद्र/त्रिकोण में स्वराशि या उच्च का हो, और (ग) उस भाव का प्राकृतिक कारक ग्रह कुंडली में बलवान हो।
                    - **२. चलित चक्र एवं संधि रहस्य:** यदि कोई ग्रह राशि में किसी भाव में बैठा है किंतु भाव मध्य सीमा पार करके संधि में चला जाता है, तो फलदीपिका के अनुसार वह भौतिक रूप से अगले/पिछले भाव का ही कार्य सिद्धि फल प्रदान करता है।
                    - **३. उपचय भावों में पाप ग्रह:** ३, ६, १० एवं ११वें भावों में पाप ग्रह (सूर्य, मंगल, शनि, राहु) अत्यंत बलवान होकर जातक को शत्रुओं पर विजय, रोग मुक्ति और असीम पुरुषार्थ प्रदान करते हैं।
                    - **४. अष्टकवर्ग समन्वय:** जिस भाव की राशि में २८ से अधिक बिंदु हों, वह भाव गोचर एवं दशा में अत्यंत अनुकूल और फलदायक सिद्ध होता है।
                    """)
                else:
                    st.markdown(f"""
                    - **१. वर्ग भाव सिद्धांत (Varga Bhava Rule):** किसी भी वर्ग चक्र (जैसे {varga_choice}) के भाव उस वर्ग के विशिष्ट कार्यक्षेत्र (उदा. D9: विवाह/धर्म, D10: कर्म/पद, D7: संतान) को सूक्ष्म रूप से दर्शाते हैं।
                    - **२. वर्ग भावेश की गरिमा:** वर्ग चक्र में जिस भाव का स्वामी उसी वर्ग में केंद्र/त्रिकोण अथवा स्वराशि/उच्च राशि में हो, वह कार्यक्षेत्र जातक के जीवन में अत्यंत फलदायी और प्रतिष्ठित होता है।
                    - **३. D1 बनाम {varga_choice} सम्बंध:** यदि कोई ग्रह मूल जन्मकुंडली (D1) और इस वर्ग ({varga_choice}) दोनों में समान भाव या समान राशि (वर्गोत्तम) में हो, तो उसका फल अकाट्य और स्थाई होता है।
                    """)
        except Exception as _ebh:
            st.error(f"द्वादश भाव तालिका निर्माण त्रुटि: {_ebh}")
        p = chart.panchang

    with tab_pushkara:
        st.markdown("### 🌟 पुष्कर नवांश, पुष्कर भाग एवं वर्गोत्तम शास्त्रीय विवेचन")
        st.caption("महर्षि पराशर, जातक पारिजात एवं उत्तर कालामृत के अनुसार कुण्डली को अमृततुल्य पोषण एवं राजयोग प्रदान करने वाले दुर्लभ अंश:")

        p_audit = default_shastriya_pramana_engine.audit_chart_pushkara(chart)
        v_audit = default_shastriya_pramana_engine.audit_vargottama(chart)

        col_pk1, col_pk2, col_pk3 = st.columns(3)
        with col_pk1:
            p_nav_str = ", ".join(p_audit["pushkara_navamsha_planets"]) if p_audit["pushkara_navamsha_planets"] else "कोई नहीं"
            st.metric("🌟 पुष्कर नवांश (Pushkara Navamsha)", f"{len(p_audit['pushkara_navamsha_planets'])} ग्रह/लग्न", p_nav_str)
        with col_pk2:
            p_bhaga_str = ", ".join(p_audit["pushkara_bhaga_planets"]) if p_audit["pushkara_bhaga_planets"] else "कोई नहीं"
            st.metric("🎯 पुष्कर भाग (Pushkara Bhaga)", f"{len(p_audit['pushkara_bhaga_planets'])} ग्रह/लग्न", p_bhaga_str)
        with col_pk3:
            v_str = ", ".join([v["planet"] for v in v_audit["vargottama_planets"]]) if v_audit["vargottama_planets"] else "कोई नहीं"
            st.metric("👑 वर्गोत्तम ग्रह (Vargottama D1=D9)", f"{v_audit['count']} ग्रह", v_str)

        st.markdown("#### 📜 नवग्रह एवं लग्न पुष्करांश-वर्गोत्तम स्थिति तालिका")
        rows_html = []
        d9_chart_obj = chart.vargas.get("D9") if hasattr(chart, "vargas") else None

        for p_name in ["Lagna", "Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]:
            if p_name == "Lagna":
                sign_nm = chart.lagna_sign_name
                deg_val = chart.lagna_degree % 30.0
                d9_sign_nm = d9_chart_obj.lagna_sign_name if d9_chart_obj else "-"
                is_varg = (chart.lagna_sign_name == d9_sign_nm)
                p_display = "लग्न (Lagna/Ascendant)"
            else:
                p_obj = chart.planets.get(p_name)
                if not p_obj:
                    continue
                sign_nm = p_obj.sign_name
                deg_val = p_obj.sign_degree
                d9_p = d9_chart_obj.planets.get(p_name) if d9_chart_obj else None
                d9_sign_nm = d9_p.sign_name if d9_p else "-"
                is_varg = (p_obj.sign_name == d9_sign_nm)
                p_display = f"{PLANET_NAMES_HI.get(p_name, p_name)} ({p_name})"

            pk_info = p_audit["planets"].get(p_name, {})
            is_pn = pk_info.get("is_pushkara_navamsha", False)
            pn_sign = pk_info.get("navamsha_sign_hi", "-")
            pn_lord = pk_info.get("navamsha_lord_hi", "-")
            is_pb = pk_info.get("is_pushkara_bhaga", False)
            pb_deg = pk_info.get("pushkara_bhaga_exact_deg", "-")

            pn_badge = f'<span style="background:#DCFCE7; color:#15803D; font-weight:800; padding:2px 8px; border-radius:4px; border:1px solid #86EFAC;">🌟 हाँ ({pn_sign} नवांश, स्वामी: {pn_lord})</span>' if is_pn else '<span style="color:#94A3B8;">—</span>'
            pb_badge = f'<span style="background:#FEF3C7; color:#B45309; font-weight:800; padding:2px 8px; border-radius:4px; border:1px solid #FCD34D;">🎯 हाँ ({pb_deg}°)</span>' if is_pb else '<span style="color:#94A3B8;">—</span>'
            vg_badge = '<span style="background:#EFF6FF; color:#1D4ED8; font-weight:800; padding:2px 8px; border-radius:4px; border:1px solid #93C5FD;">👑 वर्गोत्तम (स्वगृहीतुल्य)</span>' if is_varg else '<span style="color:#94A3B8;">—</span>'

            row = (
                f'<tr style="border-bottom: 1px solid #E2E8F0;">'
                f'<td style="padding: 7px 10px; font-weight: 700;">{p_display}</td>'
                f'<td style="padding: 7px 10px;">{sign_nm} ({deg_val:.2f}°)</td>'
                f'<td style="padding: 7px 10px;">{d9_sign_nm}</td>'
                f'<td style="padding: 7px 10px;">{pn_badge}</td>'
                f'<td style="padding: 7px 10px;">{pb_badge}</td>'
                f'<td style="padding: 7px 10px;">{vg_badge}</td>'
                f'</tr>'
            )
            rows_html.append(row)

        tbody_html = "".join(rows_html)
        table_html = (
            f'<div style="background:#FFFFFF; border:1.5px solid #CBD5E1; border-radius:10px; padding:12px; margin-bottom:15px; box-shadow:0 2px 6px rgba(0,0,0,0.05); overflow-x:auto;">'
            f'<table style="width:100%; border-collapse:collapse; font-size:12px; text-align:left;">'
            f'<thead>'
            f'<tr style="background:#F1F5F9; border-bottom:2px solid #CBD5E1; color:#1E293B;">'
            f'<th style="padding:8px 10px;">ग्रह / लग्न</th>'
            f'<th style="padding:8px 10px;">D1 राशि एवं अंश</th>'
            f'<th style="padding:8px 10px;">D9 नवांश राशि</th>'
            f'<th style="padding:8px 10px;">पुष्कर नवांश</th>'
            f'<th style="padding:8px 10px;">पुष्कर भाग</th>'
            f'<th style="padding:8px 10px;">वर्गोत्तम स्थिति</th>'
            f'</tr>'
            f'</thead>'
            f'<tbody>{tbody_html}</tbody>'
            f'</table>'
            f'</div>'
        )
        st.markdown(table_html, unsafe_allow_html=True)

        # ─── Pushkara & Vargottama Dynamic Timing & Auspicious Elevation Card ───
        try:
            _p_pn_names = [p for p, info in p_audit.get("planets", {}).items() if info.get("is_pushkara_navamsha")]
            _p_pb_names = [p for p, info in p_audit.get("planets", {}).items() if info.get("is_pushkara_bhaga")]
            _p_vg_names = [p for p, pos in chart.planets.items() if d9_chart and pos.sign_name == d9_chart.planets.get(p, pos).sign_name]
            
            _elev_items = []
            if _p_pn_names:
                _elev_items.append(f"🌟 **पुष्कर नवांश स्थित ग्रह ({', '.join(_p_pn_names)}):** इनकी विंशोत्तरी महादशा व अंतर्दशा में जातक को अमृततुल्य पोषण, आकस्मिक भाग्योदय एवं संकटों से दैवीय सुरक्षा प्राप्त होती है।")
            if _p_pb_names:
                _elev_items.append(f"🎯 **पुष्कर भाग स्थित ग्रह ({', '.join(_p_pb_names)}):** यह ग्रह परम राजयोगकारक हैं; अपने समय में समाज में शीर्ष प्रतिष्ठा, राजकीय सम्मान व स्थायी समृद्धि प्रदान करते हैं।")
            if _p_vg_names:
                _elev_items.append(f"👑 **वर्गोत्तम ग्रह ({', '.join(_p_vg_names)}):** स्वक्षेत्री बल से युक्त होकर दृढ़ इच्छाशक्ति, मानसिक स्थिरता एवं आजीवन निर्बाध कार्य-सिद्धि प्रदान करते हैं।")
            if not _elev_items:
                _elev_items.append("⚖️ **सामान्य शुभ स्थिति:** कुण्डली में अन्य शुभ योगों (केंद्र-त्रिकोण राजयोग, गजकेसरी) के आधार पर दशा-अंतर्दशा का फल संचालित होगा।")

            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #ECFDF5 0%, #F0FDF4 100%); border: 1.5px solid #10B981; border-radius: 10px; padding: 12px 16px; margin-bottom: 14px; box-shadow: 0 2px 6px rgba(16, 185, 129, 0.1);">
                <div style="color: #065F46; font-size: 13px; font-weight: 900; margin-bottom: 6px; display:flex; align-items:center; gap:6px;">
                    <span>🛡️ <b>पुष्कर व वर्गोत्तम सक्रिय फलित एवं दशा समय (Auspicious Dasha Timing)</b></span>
                </div>
                <div style="font-size: 12px; color: #1E293B; line-height: 1.6;">
                    {'<br/>'.join(_elev_items)}
                </div>
            </div>
            """, unsafe_allow_html=True)
        except Exception as _e_pk_syn:
            st.caption(f"पुष्कर फलित समन्वय: {_e_pk_syn}")

        with st.expander("📜 पुष्कर नवांश एवं वर्गोत्तम शास्त्रीय श्लोक व प्रमाण", expanded=True):
            st.markdown("""
            **🌟 पुष्कर नवांश महात्म्य (*जातक पारिजात*, अध्याय १, श्लोक ५७-५८):**
            ```text
            पुष्करांशगताः सर्वे ग्रहाः शुभफलप्रदाः।
            नीचस्था अपि कुर्वन्ति राजयोगमनुत्तमम्॥
            ```
            > **हिंदी अनुवाद एवं फल:** पुष्कर नवांश में स्थित समस्त ग्रह जातक को अमृततुल्य पोषण एवं अत्यंत शुभ फल प्रदान करते हैं। यदि कोई ग्रह जन्म कुण्डली में नीच राशि में भी बैठा हो, परंतु पुष्कर नवांश में हो, तो वह अपनी नीचता त्यागकर सर्वोत्तम राजयोग का फल प्रदान करता है।

            **🎯 पुष्कर भाग विचार (*उत्तर कालामृत*, काण्ड २, श्लोक २४):**
            ```text
            वर्गोत्तमे पुष्करांशे स्थितो वा स्वगृहेऽपि वा।
            करोति कीर्तिं विपुलां नृपतिं वा न संशयः॥
            ```
            > **हिंदी अनुवाद एवं फल:** जब ग्रह पुष्कर भाग (प्रत्येक राशि के अत्यंत गोपनीय व शुभ अंश) में होता है, तो वह जातक को विपुल कीर्ति, स्थायी आरोग्य एवं राजकीय सम्मान प्रदान करता है।

            **👑 वर्गोत्तम ग्रह फल (*बृहज्जातक*, अध्याय १, श्लोक २०):**
            ```text
            वर्गोत्तमाश्चराद्येषु प्रथमान्त्यमध्यमाः।
            स्वांशे यदा ग्रहो याति तदा वर्गोत्तमो भवेत्॥
            स्वक्षेत्रफलदः साक्षात् सर्वसौख्यप्रदायकः।
            ```
            > **हिंदी अनुवाद एवं फल:** चर राशियों (१, ४, ७, १०) का प्रथम नवांश, स्थिर राशियों (२, ५, ८, ११) का पंचम नवांश, और द्विस्वभाव राशियों (३, ६, ९, १२) का नवम नवांश वर्गोत्तम कहलाता है। जब ग्रह D1 और D9 दोनों में समान राशि में होता है, तो वह स्वगृही (अपने घर में बैठे) ग्रह के समान पूर्ण सामर्थ्यवान होकर जीवन में स्थिरता, दृढ़ इच्छाशक्ति एवं कार्य-सिद्धि प्रदान करता है।
            """)

    with tab_jm_hud:
        st.markdown("### 👑 विशेष जैमिनी लग्न (Special Lagnas - Shastriya Standard)")
        st.info("महर्षि पराशर (BPHS) एवं जैमिनी उपदेश सूत्रों के अनुसार जीवन के विशिष्ट क्षेत्रों (धन, पद, सत्ता, आयुष्य एवं भाग्य) के सूक्ष्म आकलन हेतु विशेष लग्नों की गणितीय स्पष्ट स्थिति:")

        if chart.jaimini:
            jm = chart.jaimini
            sl_details = getattr(jm, 'special_lagnas_detail', {}) or {}

            # ─── Top 6 HUD Cards ───
            hl_o = sl_details.get('HL', {})
            gl_o = sl_details.get('GL', {})
            sl_o = sl_details.get('SL', {})
            il_o = sl_details.get('IL', {})
            pp_o = sl_details.get('PP', {})
            vl_o = sl_details.get('VL', {})

            st.markdown(f"""
            <div style="background: linear-gradient(90deg, #FFFBEB 0%, #FEF3C7 100%); border: 1.5px solid #F59E0B; border-radius: 10px; padding: 12px 18px; margin: 10px 0 15px 0; box-shadow: 0 2px 6px rgba(217, 119, 6, 0.1);">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                    <div style="color: #92400E; font-size: 13.5px; font-weight: 900; display: flex; align-items: center; gap: 6px;">
                        <span>👑 <b>जैमिनी विशेष लग्न त्वरित अवलोकन (Quick HUD Console)</b></span>
                    </div>
                    <div style="font-size: 11.5px; color: #78350F; font-weight: 800; background: #FDE68A; padding: 2px 8px; border-radius: 6px;">
                        अयनांश: {chart.ayanamsa_name} ({chart.ayanamsa_value:.2f}°) | नोड: {st.session_state.get('app_node_type', 'Mean Node').split('(')[0]}
                    </div>
                </div>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 10px;">
                    <div style="background: #FFFFFF; border: 1px solid #FCD34D; border-radius: 8px; padding: 8px 10px;">
                        <div style="font-size: 11px; color: #B45309; font-weight: 800;">💰 होरा लग्न (HL)</div>
                        <div style="font-size: 14.5px; font-weight: 900; color: #1E293B;">{jm.hora_lagna_sign_name}</div>
                        <div style="font-size: 10px; color: #64748B;">अंश: {hl_o.get('degree', 0.0):.2f}° | स्वामी: {hl_o.get('lord', '—')}</div>
                        <div style="font-size: 10px; color: #047857; font-weight:700;">धन, संचित संपदा</div>
                    </div>
                    <div style="background: #FFFFFF; border: 1px solid #FCD34D; border-radius: 8px; padding: 8px 10px;">
                        <div style="font-size: 11px; color: #B45309; font-weight: 800;">🏛️ घटी लग्न (GL)</div>
                        <div style="font-size: 14.5px; font-weight: 900; color: #1E293B;">{jm.ghati_lagna_sign_name}</div>
                        <div style="font-size: 10px; color: #64748B;">अंश: {gl_o.get('degree', 0.0):.2f}° | स्वामी: {gl_o.get('lord', '—')}</div>
                        <div style="font-size: 10px; color: #1D4ED8; font-weight:700;">सत्ता, अधिकार, पद</div>
                    </div>
                    <div style="background: #FFFFFF; border: 1px solid #FCD34D; border-radius: 8px; padding: 8px 10px;">
                        <div style="font-size: 11px; color: #B45309; font-weight: 800;">🪷 श्री लग्न (SL)</div>
                        <div style="font-size: 14.5px; font-weight: 900; color: #1E293B;">{jm.sri_lagna_sign_name}</div>
                        <div style="font-size: 10px; color: #64748B;">अंश: {sl_o.get('degree', 0.0):.2f}° | स्वामी: {sl_o.get('lord', '—')}</div>
                        <div style="font-size: 10px; color: #D97706; font-weight:700;">महालक्ष्मी कृपा, समृद्धि</div>
                    </div>
                    <div style="background: #FFFFFF; border: 1px solid #FCD34D; border-radius: 8px; padding: 8px 10px;">
                        <div style="font-size: 11px; color: #B45309; font-weight: 800;">💎 इन्दु लग्न (IL)</div>
                        <div style="font-size: 14.5px; font-weight: 900; color: #1E293B;">{jm.indu_lagna_sign_name}</div>
                        <div style="font-size: 10px; color: #64748B;">स्वामी: {il_o.get('lord', '—')}</div>
                        <div style="font-size: 10px; color: #7C3AED; font-weight:700;">कोटिपतित्व / धनागमन</div>
                    </div>
                    <div style="background: #FFFFFF; border: 1px solid #FCD34D; border-radius: 8px; padding: 8px 10px;">
                        <div style="font-size: 11px; color: #B45309; font-weight: 800;">💨 प्राणपद लग्न (PP)</div>
                        <div style="font-size: 14.5px; font-weight: 900; color: #1E293B;">{jm.pranapada_lagna_sign_name}</div>
                        <div style="font-size: 10px; color: #64748B;">अंश: {pp_o.get('degree', 0.0):.2f}° | स्वामी: {pp_o.get('lord', '—')}</div>
                        <div style="font-size: 10px; color: #059669; font-weight:700;">प्राण शक्ति, BTR शोधन</div>
                    </div>
                    <div style="background: #FFFFFF; border: 1px solid #FCD34D; border-radius: 8px; padding: 8px 10px;">
                        <div style="font-size: 11px; color: #B45309; font-weight: 800;">⚔️ वर्णद लग्न (VL)</div>
                        <div style="font-size: 14.5px; font-weight: 900; color: #1E293B;">{jm.varnada_lagna_sign_name}</div>
                        <div style="font-size: 10px; color: #64748B;">स्वामी: {vl_o.get('lord', '—')}</div>
                        <div style="font-size: 10px; color: #DC2626; font-weight:700;">सामाजिक दायित्व, आजीविका</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # ─── Detailed Comparative Table ───
            st.markdown("#### 📊 विशेष लग्न स्पष्ट गणितीय तालिका (Shastriya Standard Mathematical Details)")
            sl_rows = []
            order_keys = ["HL", "GL", "SL", "IL", "BL", "PP", "VL"]
            for k in order_keys:
                v = sl_details.get(k)
                if not v:
                    continue
                h_from_lag = ((SIGN_NAMES.index(v['sign']) - chart.lagna_sign_id + 12) % 12) + 1 if v.get('sign') in SIGN_NAMES else 1
                sl_rows.append({
                    "विशेष लग्न": v.get('name_hi', k),
                    "प्रतीक": k,
                    "राशि": v.get('sign', '—'),
                    "स्पष्ट अंश": f"{v.get('degree', 0.0):.2f}°",
                    "सम्पूर्ण देशांतर": f"{v.get('longitude', 0.0):.2f}°",
                    "राशि स्वामी": v.get('lord', '—'),
                    "लग्न से भाव": f"{h_from_lag} भाव",
                    "शास्त्रीय प्रयोजन एवं नियम": v.get('purpose_hi', '')
                })
            st.dataframe(pd.DataFrame(sl_rows), use_container_width=True, hide_index=True)

            # ─── 3 Jaimini Special Yoga Analysis Cards ───
            st.markdown("#### 🔬 विशेष लग्न आधारित शास्त्रीय योग फलादेश (Jaimini Classical Yoga Engine)")
            col_y1, col_y2, col_y3 = st.columns(3)

            # 1. Dhana Yoga (HL & SL)
            with col_y1:
                hl_s = jm.hora_lagna_sign_name
                sl_s = jm.sri_lagna_sign_name
                hl_lord = SIGN_LORDS.get(hl_s, '')
                is_hl_benefic = hl_lord in ["Jupiter", "Venus", "Mercury", "Moon"]
                st.markdown(f"""
                <div style="background:#FFFBEB; border:1.5px solid #F59E0B; border-radius:10px; padding:12px; height:100%;">
                    <h5 style="color:#B45309; margin:0 0 6px 0;">💰 जैमिनी धन योग (HL &amp; SL)</h5>
                    <div style="font-size:12px; color:#1E293B; line-height:1.5;">
                        <b>होरा लग्न (HL):</b> {hl_s} (स्वामी: {hl_lord})<br/>
                        <b>श्री लग्न (SL):</b> {sl_s}<br/>
                        <div style="margin:6px 0; padding:6px; background:#FEF3C7; border-radius:6px; font-weight:800; font-size:11.5px; color:#78350F;">
                            {'🌟 प्रबल धन योग: होरा लग्न का स्वामी शुभ ग्रह है तथा वित्तीय संचय में स्थायित्व प्रदान करता है।' if is_hl_benefic else '⚡ कर्मप्रधान धन योग: वित्तीय सफलता पुरुषार्थ एवं निरंतर उद्यम से निर्मित होगी।'}
                        </div>
                        <b>शास्त्रीय सूत्र:</b> होरा लग्न और श्री लग्न पर शुभ ग्रहों (गुरु, शुक्र, बुध) की दृष्टि या युति जातक को विपुल संपदा एवं महालक्ष्मी का स्थायी अनुग्रह प्रदान करती है।
                    </div>
                </div>
                """, unsafe_allow_html=True)

            # 2. Raja Yoga (GL & Janma Lagna)
            with col_y2:
                gl_s = jm.ghati_lagna_sign_name
                gl_lord = SIGN_LORDS.get(gl_s, '')
                gl_h = ((SIGN_NAMES.index(gl_s) - chart.lagna_sign_id + 12) % 12) + 1 if gl_s in SIGN_NAMES else 1
                is_gl_kendra = gl_h in [1, 4, 7, 10, 5, 9]
                st.markdown(f"""
                <div style="background:#EFF6FF; border:1.5px solid #3B82F6; border-radius:10px; padding:12px; height:100%;">
                    <h5 style="color:#1D4ED8; margin:0 0 6px 0;">🏛️ जैमिनी राज योग (GL &amp; Lagna)</h5>
                    <div style="font-size:12px; color:#1E293B; line-height:1.5;">
                        <b>घटी लग्न (GL):</b> {gl_s} ({gl_h} भाव)<br/>
                        <b>घटी लग्न स्वामी:</b> {gl_lord}<br/>
                        <div style="margin:6px 0; padding:6px; background:#DBEAFE; border-radius:6px; font-weight:800; font-size:11.5px; color:#1E3A8A;">
                            {'👑 प्रतिष्ठित राजयोग: घटी लग्न केंद्र/त्रिकोण में स्थित होकर शासकीय प्रभुत्व एवं यश देता है।' if is_gl_kendra else '📈 प्रतिष्ठा योग: घटी लग्न जातक को सामाजिक दायित्व एवं प्रशासनिक प्रभाव प्रदान करता है।'}
                        </div>
                        <b>शास्त्रीय सूत्र:</b> यदि जन्म लग्न और घटी लग्न दोनों पर किसी एक ही ग्रह की दृष्टि हो, तो महर्षि जैमिनी अनुसार जातक को राजा समान पद, सत्ता एवं समाज में सर्वोच्च सम्मान प्राप्त होता है।
                    </div>
                </div>
                """, unsafe_allow_html=True)

            # 3. Indu Lagna Wealth Engine
            with col_y3:
                il_s = jm.indu_lagna_sign_name
                il_lord = SIGN_LORDS.get(il_s, '')
                il_planets = [pn for pn, p in chart.planets.items() if p.sign_name == il_s]
                il_benefics = [p for p in il_planets if p in ["Jupiter", "Venus", "Mercury", "Moon"]]
                st.markdown(f"""
                <div style="background:#FAF5FF; border:1.5px solid #8B5CF6; border-radius:10px; padding:12px; height:100%;">
                    <h5 style="color:#6D28D9; margin:0 0 6px 0;">💎 इन्दु लग्न कोटिपतित्व योग</h5>
                    <div style="font-size:12px; color:#1E293B; line-height:1.5;">
                        <b>इन्दु लग्न:</b> {il_s} (स्वामी: {il_lord})<br/>
                        <b>इन्दु लग्न में स्थित ग्रह:</b> {', '.join(il_planets) if il_planets else 'शुभ दृष्टि प्रभाव'}<br/>
                        <div style="margin:6px 0; padding:6px; background:#F3E8FF; border-radius:6px; font-weight:800; font-size:11.5px; color:#581C87;">
                            {'🏆 कोटिपतित्व योग: शुभ ग्रह इन्दु लग्न में विद्यमान होकर अकूत संपदा का सृजन कर रहे हैं!' if il_benefics else ('⚡ उद्योगी धन योग: इन्दु लग्न स्वामी ' + il_lord + ' के बल से वित्तीय साम्राज्य खड़ा होगा।')}
                        </div>
                        <b>शास्त्रीय सूत्र:</b> इन्दु लग्न में केवल एक भी उच्च या शुभ ग्रह स्थित हो तो जातक बहु-करोड़पति बनता है; पाप ग्रह हों तो धन का प्रवाह उद्यम के साथ आता है।
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("जैमिनी विशेष लग्न गणना उपलब्ध नहीं।")


    with tab_bhav:
        st.markdown("### 🏠 भाव चलित चक्र (Bhava Chalit Chart — Equal / Sripati Cusp System)")
        st.info("श्रीपति एवं समभाव पद्धति अनुसार भाव के मध्य बिंदु (Cusp) से आरंभ व अंत सीमा का निर्धारण होता है। यदि कोई ग्रह राशि में होते हुए भी भाव सीमा पार कर जाता है, तो उसका प्रभाव वास्तविक चलित भाव से ही फलित होता है:")

        try:
            _bc_res = default_chart_calculator.calculate_bhava_chalit(chart)
            _bc_items = _bc_res.get("planet_positions", []) if isinstance(_bc_res, dict) else _bc_res
            _cusps_list = _bc_res.get("bhava_cusps", []) if isinstance(_bc_res, dict) else []

            # Construct Chalit VargaChart for dynamic SVG Kundali rendering
            _chalit_planets = {}
            for _it in _bc_items:
                _pn = _it.get("planet")
                _ch = _it.get("chalit_house", 1)
                _sn = _it.get("sign", _it.get("sign_name", "Aries"))
                _p_orig = chart.planets.get(_pn)
                _chalit_planets[_pn] = VargaPlanetPosition(
                    name=_pn,
                    sign_id=_p_orig.sign_id if _p_orig else 1,
                    sign_name=_sn,
                    degree_in_varga=_p_orig.sign_degree if _p_orig else 0.0,
                    house_number=_ch
                )
            _v_chalit = VargaChart(
                varga_code="CHALIT",
                varga_name="भाव चलित",
                division=1,
                lagna_sign_id=chart.lagna_sign_id,
                lagna_sign_name=chart.lagna_sign_name,
                planets=_chalit_planets
            )
            chart.vargas["CHALIT"] = _v_chalit

            bc_col1, bc_col2 = st.columns([1, 1], gap="medium")
            with bc_col1:
                svg_chalit = render_chart_svg(chart, "🏠 भाव चलित चक्र (Bhava Chalit)", varga_code="CHALIT")
                st.markdown(f'<div class="kundali-chart" style="width:100%; display:flex; justify-content:center; margin-bottom:10px;">{svg_chalit}</div>', unsafe_allow_html=True)
                st.caption(f"**लग्न:** {chart.lagna_sign_name} ({chart.lagna_sign_id}) | चलित चक्र में ग्रहों का स्थान उनकी वास्तविक भाव स्थिति को दर्शाता है।")

                # Cusp Methodology Explanatory Box
                st.markdown("""
                <div style="background:#F8FAFC; border:1px solid #CBD5E1; border-radius:8px; padding:10px; font-size:12px; color:#334155; line-height:1.5;">
                    <b>💡 चलित चक्र रहस्य (Astrological Rule):</b><br/>
                    • <b>राशि चक्र (D1):</b> ग्रह का राशिगत बल, गरिमा (उच्च/नीच) व सम्बंध दर्शाता है।<br/>
                    • <b>भाव चलित चक्र:</b> ग्रह वास्तव में किस भाव का भौतिक व व्यावहारिक परिणाम देगा, यह निश्चित करता है।
                </div>
                """, unsafe_allow_html=True)

            with bc_col2:
                st.markdown("#### 🔄 ग्रह भाव परिवर्तन विश्लेषण (Planetary House Shifts)")
                _shift_rows = []
                _shifted_planets = []
                for _it in _bc_items:
                    _pn = _it.get("planet", "")
                    _rh = _it.get("rashi_house", 1)
                    _ch = _it.get("chalit_house", 1)
                    _is_diff = (_rh != _ch)
                    if _is_diff:
                        _shifted_planets.append(f"{_pn} ({_rh}→{_ch})")
                        _status_badge = '<span style="background:#FEF3C7; color:#B45309; font-weight:800; padding:2px 8px; border-radius:4px; font-size:11px;">⚠️ स्थानांतरित</span>'
                        _impact_txt = f"{_rh}वें भाव से {_ch}वें भाव का फल प्रभावी रहेगा।"
                    else:
                        _status_badge = '<span style="background:#DCFCE7; color:#15803D; font-weight:800; padding:2px 8px; border-radius:4px; font-size:11px;">✅ स्थिर</span>'
                        _impact_txt = f"{_rh}वें भाव में स्थिर पूर्ण फल।"

                    _shift_rows.append(f'<tr style="border-bottom:1px solid #E2E8F0;"><td style="padding:5px 8px; font-weight:800; color:#1E293B;">{_pn}</td><td style="padding:5px 8px; color:#475569;">{_it.get("sign", "")}</td><td style="padding:5px 8px; text-align:center; font-weight:700;">{_rh} भाव</td><td style="padding:5px 8px; text-align:center; font-weight:900; color:#1E40AF;">{_ch} भाव</td><td style="padding:5px 8px; text-align:center;">{_status_badge}</td><td style="padding:5px 8px; font-size:11px; color:#334155;">{_impact_txt}</td></tr>')

                _shift_table_html = f'<div style="background:#FFFFFF; border:1px solid #CBD5E1; border-radius:8px; padding:4px; max-height:220px; overflow-y:auto; margin-bottom:10px;"><table style="width:100%; border-collapse:collapse; font-size:11.5px;"><thead><tr style="background:#F1F5F9; color:#475569; font-weight:800; border-bottom:1.5px solid #CBD5E1;"><th style="padding:4px 8px; text-align:left;">ग्रह</th><th style="padding:4px 8px; text-align:left;">राशि</th><th style="padding:4px 8px; text-align:center;">राशि भाव</th><th style="padding:4px 8px; text-align:center;">चलित भाव</th><th style="padding:4px 8px; text-align:center;">स्थिति</th><th style="padding:4px 8px; text-align:left;">फल प्रभाव</th></tr></thead><tbody>{"".join(_shift_rows)}</tbody></table></div>'
                st.markdown(_shift_table_html, unsafe_allow_html=True)

                if _shifted_planets:
                    st.warning("⚠️ **भाव परिवर्तन प्रभाव:** " + ", ".join(_shifted_planets) + " ग्रह चलित चक्र में स्थानांतरित हो गए हैं। दशा विश्लेषण में इन ग्रहों का फल इनके चलित भाव के अनुसार घटित होगा।")
                else:
                    st.success("✅ **पूर्ण समरूपता:** इस कुण्डली में सभी ग्रह राशि-भाव और चलित-भाव में समान हैं।")

                # Cusp Coordinates Table
                st.markdown("#### 📐 १२ भाव मध्य (Cusps) एवं संधि स्पष्ट")
                if _cusps_list:
                    _c_tbl_rows = []
                    for _c in _cusps_list:
                        _b_num = _c.get("bhava", 1)
                        _c_deg = _c.get("cusp_degree", 0.0)
                        _arambha = (_c_deg - 15.0 + 30.0) % 30.0
                        _anta = (_c_deg + 15.0) % 30.0
                        _c_tbl_rows.append(f'<tr style="border-bottom:1px solid #E2E8F0;"><td style="padding:4px 8px; font-weight:800; color:#1E3A8A;">{_b_num} भाव</td><td style="padding:4px 8px; font-weight:700;">{_c.get("sign_name", "")}</td><td style="padding:4px 8px; font-family:monospace; color:#475569;">{_arambha:.2f}°</td><td style="padding:4px 8px; font-family:monospace; font-weight:800; color:#0F172A;">{_c_deg:.2f}°</td><td style="padding:4px 8px; font-family:monospace; color:#475569;">{_anta:.2f}°</td></tr>')
                    _c_tbl_html = f'<div style="background:#FFFFFF; border:1px solid #CBD5E1; border-radius:8px; padding:4px; max-height:180px; overflow-y:auto;"><table style="width:100%; border-collapse:collapse; font-size:11.5px;"><thead><tr style="background:#F1F5F9; color:#475569; font-weight:800; border-bottom:1.5px solid #CBD5E1;"><th style="padding:4px 8px; text-align:left;">भाव</th><th style="padding:4px 8px; text-align:left;">राशि</th><th style="padding:4px 8px; text-align:left;">आरंभ</th><th style="padding:4px 8px; text-align:left;">मध्य (Cusp)</th><th style="padding:4px 8px; text-align:left;">संधि (अंत)</th></tr></thead><tbody>{"".join(_c_tbl_rows)}</tbody></table></div>'
                    st.markdown(_c_tbl_html, unsafe_allow_html=True)

                # ─── Bhava Sandhi Alert (Zero Bhava Bala Check) ───
                _sandhi_alerts = []
                for _pname, _ppos in chart.planets.items():
                    _plon = _ppos.longitude
                    for _h in getattr(chart, 'houses', []):
                        _s_start = getattr(_h, 'sandhi_start', None)
                        _s_end = getattr(_h, 'sandhi_end', None)
                        if _s_start is not None:
                            _d_start = abs((_plon - _s_start + 180.0) % 360.0 - 180.0)
                            if _d_start <= 1.0:
                                _sandhi_alerts.append(f"**{_pname}** ({_h.house_number} भाव आरंभ संधि से केवल {_d_start:.2f}°)")
                        if _s_end is not None:
                            _d_end = abs((_plon - _s_end + 180.0) % 360.0 - 180.0)
                            if _d_end <= 1.0:
                                _sandhi_alerts.append(f"**{_pname}** ({_h.house_number} भाव विराम संधि से केवल {_d_end:.2f}°)")

                if _sandhi_alerts:
                    st.warning(f"⚠️ **भाव संधि दोष (Sandhi Grihas — निस्तेज / फल शून्य):** {', '.join(_sandhi_alerts)}। शास्त्रीय नियमानुसार जो ग्रह भाव के आरंभ या अंत सीमा के १° के भीतर स्थित होते हैं, उनका भाव-फल सामर्थ्य क्षीण अथवा निष्प्रभावी हो जाता है।")
                else:
                    st.success("✅ **संधि दोष रहित:** इस कुण्डली में कोई भी ग्रह भाव संधि के १° के भीतर नहीं है; सभी ग्रह अपने-अपने भाव का पूर्ण एवं स्वतंत्र फल प्रदान कर रहे हैं।")

        except Exception as _ebc:
            st.error(f"भाव चलित गणना त्रुटि: {_ebc}")


    with tab_chandra:
        st.markdown("### 🌙 चन्द्र कुण्डली (Chandra Kundali — Mind & Emotional Consciousness)")
        _moon = chart.planets.get("Moon")
        if _moon:
            st.info(f"चन्द्रमा मन, माता, जन-समर्थन एवं भौतिक जीवन का मुख्य कारक है। चन्द्र कुण्डली में चन्द्रमा की राशि (**{_moon.sign_name}**) को प्रथम भाव (लग्न) मानकर सम्पूर्ण जीवन का अध्ययन किया जाता है:")

            # Construct Chandra VargaChart
            _chandra_planets = {
                _pn: VargaPlanetPosition(
                    name=_pn,
                    sign_id=_p.sign_id,
                    sign_name=_p.sign_name,
                    degree_in_varga=_p.sign_degree,
                    house_number=((_p.sign_id - _moon.sign_id + 12) % 12) + 1
                ) for _pn, _p in chart.planets.items()
            }
            _v_chandra = VargaChart(
                varga_code="CHANDRA",
                varga_name="चन्द्र कुण्डली",
                division=1,
                lagna_sign_id=_moon.sign_id,
                lagna_sign_name=_moon.sign_name,
                planets=_chandra_planets
            )
            chart.vargas["CHANDRA"] = _v_chandra

            cc_col1, cc_col2 = st.columns([1, 1], gap="medium")
            with cc_col1:
                svg_chandra = render_chart_svg(chart, f"🌙 चन्द्र कुण्डली ({_moon.sign_name} लग्न)", varga_code="CHANDRA")
                st.markdown(f'<div class="kundali-chart" style="width:100%; display:flex; justify-content:center; margin-bottom:10px;">{svg_chandra}</div>', unsafe_allow_html=True)

                st.markdown(f"""
                <div style="background:#EFF6FF; border:1px solid #93C5FD; border-radius:8px; padding:10px 14px; font-size:12px; color:#1E3A8A; line-height:1.6;">
                    <b>🌕 चन्द्रमा का स्पष्ट परिचय:</b><br/>
                    • <b>राशि:</b> {_moon.sign_name} ({_moon.sign_degree:.2f}°)<br/>
                    • <b>नक्षत्र:</b> {_moon.nakshatra_name} (पाद {_moon.nakshatra_pada}) — स्वामी: {_moon.nakshatra_lord}<br/>
                    • <b>तिथि:</b> {chart.panchang.tithi_name} ({chart.panchang.tithi_type})<br/>
                    • <b>चन्द्र बल:</b> {'शुक्ल पक्ष बलिष्ठ' if 'Shukla' in (chart.panchang.tithi_type or '') else 'कृष्ण पक्ष सौम्य'}
                </div>
                """, unsafe_allow_html=True)

            with cc_col2:
                st.markdown("#### 🪐 चन्द्र लग्न से १२ भाव स्थिति")
                _c_house_rows = []
                _c_signifs = [
                    "मन, स्वभाव, मानसिक शक्ति व काया", "वाणी, संचित धन, कुटुंब व आहार", "पराक्रम, भाई-बहन, साहस व संचार",
                    "मातृ सुख, भवन, वाहन व आंतरिक शांति", "बुद्धि, विद्या, पूर्वपुण्य व संतान", "रोग, ऋण, शत्रु व सेवा कार्य",
                    "दांपत्य, जीवनसाथी, साझेदारी व लोक संपर्क", "आयु, मानसिक संघर्ष व गूढ़ ज्ञान", "धर्म, भाग्य, गुरु व तीर्थाटन",
                    "कर्म, आजीविका, सामाजिक पद व कीर्ति", "लाभ, आय, मित्र व मनोकामना पूर्ति", "व्यय, शयन सुख, विदेश व मोक्ष"
                ]
                for _h_idx in range(1, 13):
                    _target_sid = ((_moon.sign_id - 1 + (_h_idx - 1)) % 12) + 1
                    _target_sname = SIGN_NAMES[_target_sid - 1]
                    _h_lord = SIGN_LORDS.get(_target_sname, "")
                    _occ_p = [_pn for _pn, _pp in chart.planets.items() if _pp.sign_id == _target_sid]
                    _occ_str = ", ".join(_occ_p) if _occ_p else "—"
                    _c_house_rows.append(f'<tr style="border-bottom:1px solid #E2E8F0;"><td style="padding:4px 6px; font-weight:800; color:#1E40AF;">{_h_idx} भाव</td><td style="padding:4px 6px; font-weight:700;">{_target_sname}</td><td style="padding:4px 6px; color:#475569;">{_h_lord}</td><td style="padding:4px 6px; font-weight:800; color:#0F172A;">{_occ_str}</td><td style="padding:4px 6px; font-size:10.5px; color:#475569;">{_c_signifs[_h_idx-1]}</td></tr>')

                _ch_tbl_html = f'<div style="background:#FFFFFF; border:1px solid #CBD5E1; border-radius:8px; padding:4px; max-height:220px; overflow-y:auto; margin-bottom:10px;"><table style="width:100%; border-collapse:collapse; font-size:11.5px;"><thead><tr style="background:#F1F5F9; color:#475569; font-weight:800; border-bottom:1.5px solid #CBD5E1;"><th style="padding:4px 6px; text-align:left;">भाव</th><th style="padding:4px 6px; text-align:left;">राशि</th><th style="padding:4px 6px; text-align:left;">स्वामी</th><th style="padding:4px 6px; text-align:left;">स्थित ग्रह</th><th style="padding:4px 6px; text-align:left;">जीवन क्षेत्र</th></tr></thead><tbody>{"".join(_c_house_rows)}</tbody></table></div>'
                st.markdown(_ch_tbl_html, unsafe_allow_html=True)

                # ─── Lunar Yogas Engine ───
                st.markdown("#### 🌟 चन्द्र आधारित प्रमुख योग (Classical Lunar Yogas)")
                _lunar_yogas = []

                # 1. Gajakesari
                _jup = chart.planets.get("Jupiter")
                if _jup:
                    _j_dist = ((_jup.sign_id - _moon.sign_id + 12) % 12) + 1
                    if _j_dist in [1, 4, 7, 10]:
                        _lunar_yogas.append(("🐘 गजकेसरी योग", f"गुरु चन्द्रमा से {_j_dist}वें (केंद्र) भाव में स्थित है। जातक अत्यंत मेधावी, पूज्य, कीर्तिवान एवं संकटों को परास्त करने वाला होता है।", "#DCFCE7", "#166534"))

                # 2. Sunapha, Anapha, Durdhara, Kemadruma
                _h2_planets = [pn for pn, p in chart.planets.items() if p.sign_id == (((_moon.sign_id) % 12) + 1) and pn not in ["Sun", "Rahu", "Ketu"]]
                _h12_planets = [pn for pn, p in chart.planets.items() if p.sign_id == (((_moon.sign_id - 2 + 12) % 12) + 1) and pn not in ["Sun", "Rahu", "Ketu"]]

                if _h2_planets and _h12_planets:
                    _lunar_yogas.append(("👑 दुरुधरा योग (Durdhara)", f"चन्द्रमा के दोनों ओर (द्वितीय में {', '.join(_h2_planets)} एवं द्वादश में {', '.join(_h12_planets)}) ग्रह विद्यमान हैं। जातक अतुल संपदा, वाहन एवं सुख-समृद्धि का स्वामी बनता है।", "#FEF3C7", "#92400E"))
                elif _h2_planets:
                    _lunar_yogas.append(("💰 सुनफा योग (Sunapha)", f"चन्द्रमा से द्वितीय भाव में {', '.join(_h2_planets)} स्थित हैं। जातक स्व-अर्जित धन, चतुर बुद्धि एवं उच्च सामाजिक प्रतिष्ठा प्राप्त करता है।", "#EFF6FF", "#1E40AF"))
                elif _h12_planets:
                    _lunar_yogas.append(("🕊️ अनफा योग (Anapha)", f"चन्द्रमा से द्वादश भाव में {', '.join(_h12_planets)} स्थित हैं। जातक निरोगी, विनम्र, उदार, आध्यात्मिक एवं नीतिवान होता है।", "#F0FDF4", "#065F46"))
                else:
                    # Kemadruma & Shastric Bhanga check (Phaladeepika Ch. 6, Sloka 5-7)
                    _kendra_planets = [pn for pn, p in chart.planets.items() if ((p.sign_id - _moon.sign_id + 12) % 12) + 1 in [1, 4, 7, 10] and pn not in ["Moon", "Rahu", "Ketu"]]
                    _lagna_kendra_planets = [pn for pn, p in chart.planets.items() if p.house_from_lagna in [1, 4, 7, 10] and pn not in ["Moon", "Rahu", "Ketu"]]
                    _jup_aspects_moon = False
                    if _jup:
                        _jm_dist = ((_moon.sign_id - _jup.sign_id + 12) % 12) + 1
                        _jup_aspects_moon = (_jm_dist in [5, 7, 9])

                    _bhanga_points = []
                    if _kendra_planets:
                        _bhanga_points.append(f"चन्द्र केंद्र में स्थित ग्रह ({', '.join(_kendra_planets)})")
                    if _jup_aspects_moon:
                        _bhanga_points.append("देवगुरु बृहस्पति की पूर्ण दृष्टि")
                    if _moon.house_from_lagna in [1, 4, 7, 10]:
                        _bhanga_points.append("चन्द्रमा का स्वयं लग्न केंद्र में होना")
                    elif _lagna_kendra_planets:
                        _bhanga_points.append(f"लग्न केंद्र में स्थित ग्रह ({', '.join(_lagna_kendra_planets)})")

                    if _bhanga_points:
                        _lunar_yogas.append(("⚖️ केमद्रुम भंग राजयोग", f"चन्द्रमा से द्वितीय/द्वादश रिक्त होने पर भी {', '.join(_bhanga_points)} के प्रभाव से केमद्रुम दोष सर्वथा भंग होकर उच्च कोटि के राजयोग में परिवर्तित हो गया है। (फलदीपिका अ. ६)", "#ECFDF5", "#047857"))
                    else:
                        _lunar_yogas.append(("⚠️ केमद्रुम योग (Kemadruma)", "चन्द्रमा से द्वितीय एवं द्वादश दोनों रिक्त हैं। जीवन में कभी-कभी मानसिक एकाकीपन या वित्तीय उतार-चढ़ाव संभव है; शिव आराधना एवं चंद्र कवच पाठ शुभप्रद है।", "#FEE2E2", "#991B1B"))

                # 3. Chandra-Mangala Yoga
                _mars = chart.planets.get("Mars")
                if _mars:
                    _m_dist = ((_mars.sign_id - _moon.sign_id + 12) % 12) + 1
                    if _m_dist in [1, 7]:
                        _lunar_yogas.append(("💎 चन्द्र-मंगल महालक्ष्मी योग", f"चन्द्रमा एवं मंगल परस्पर {_m_dist}वें भाव में युत/दृष्ट हैं। यह व्यापारिक सफलता, उद्योग में धन लाभ एवं तीव्र क्रियाशीलता का कारक है।", "#FAF5FF", "#6B21A8"))

                # Render Yoga Cards
                for _yt, _yd, _bg, _fg in _lunar_yogas:
                    st.markdown(f'<div style="background:{_bg}; border:1px solid #CBD5E1; border-radius:6px; padding:6px 10px; margin-bottom:5px;"><span style="font-weight:900; color:{_fg}; font-size:12px;">{_yt}:</span> <span style="font-size:11.5px; color:#1E293B;">{_yd}</span></div>', unsafe_allow_html=True)
        else:
            st.warning("चन्द्रमा की स्थिति उपलब्ध नहीं।")


    with tab_surya:
        st.markdown("### ☀️ सूर्य कुण्डली (Surya Kundali — Soul, Vitality & Social Stature)")
        _sun = chart.planets.get("Sun")
        if _sun:
            st.info(f"भगवान सूर्य आत्मा, पिता, जीवनी शक्ति, शासकीय प्रभुत्व एवं आजीविका के मूल कारक हैं। सूर्य राशि (**{_sun.sign_name}**) को प्रथम भाव मानकर जातक के आत्मबल एवं सामाजिक प्रभाव का अध्ययन किया जाता है:")

            # Construct Surya VargaChart
            _surya_planets = {
                _pn: VargaPlanetPosition(
                    name=_pn,
                    sign_id=_p.sign_id,
                    sign_name=_p.sign_name,
                    degree_in_varga=_p.sign_degree,
                    house_number=((_p.sign_id - _sun.sign_id + 12) % 12) + 1
                ) for _pn, _p in chart.planets.items()
            }
            _v_surya = VargaChart(
                varga_code="SURYA",
                varga_name="सूर्य कुण्डली",
                division=1,
                lagna_sign_id=_sun.sign_id,
                lagna_sign_name=_sun.sign_name,
                planets=_surya_planets
            )
            chart.vargas["SURYA"] = _v_surya

            sc_col1, sc_col2 = st.columns([1, 1], gap="medium")
            with sc_col1:
                svg_surya = render_chart_svg(chart, f"☀️ सूर्य कुण्डली ({_sun.sign_name} लग्न)", varga_code="SURYA")
                st.markdown(f'<div class="kundali-chart" style="width:100%; display:flex; justify-content:center; margin-bottom:10px;">{svg_surya}</div>', unsafe_allow_html=True)

                _sun_dignity, _, _ = get_varga_dignity_info("Sun", _sun.sign_name, affliction_engine)
                st.markdown(f"""
                <div style="background:#FFFBEB; border:1px solid #FCD34D; border-radius:8px; padding:10px 14px; font-size:12px; color:#78350F; line-height:1.6;">
                    <b>☀️ सूर्य देव का स्पष्ट परिचय:</b><br/>
                    • <b>राशि:</b> {_sun.sign_name} ({_sun.sign_degree:.2f}°)<br/>
                    • <b>नक्षत्र:</b> {_sun.nakshatra_name} (पाद {_sun.nakshatra_pada}) — स्वामी: {_sun.nakshatra_lord}<br/>
                    • <b>गरिमा:</b> {_sun_dignity}<br/>
                    • <b>सम्पूर्ण निरयण देशांतर:</b> {_sun.longitude:.2f}°
                </div>
                """, unsafe_allow_html=True)

            with sc_col2:
                st.markdown("#### 🪐 सूर्य लग्न से १२ भाव स्थिति")
                _s_house_rows = []
                _s_signifs = [
                    "आत्मा, तेज, जीवन शक्ति व संकल्प", "राजकोष, पैतृक संपदा, सत्य वाणी", "शौर्य, उद्यम, शासकीय अधिकार",
                    "आंतरिक संतोष, उच्च वाहन, जनता में प्रतिष्ठा", "प्रज्ञा, राजनीतिक सूझबूझ, मंत्र शक्ति", "प्रतिस्पर्धा, विजय, प्रशासनिक सेवा",
                    "व्यापारिक साझेदार, संबंध व बाह्य प्रभाव", "गूढ़ रहस्य, पितृ ऋण, गुप्त संपदा", "धर्म, उच्च संस्कार, पिता का मार्गदर्शन",
                    "शासन में पद, शासकीय मान्यता व आजीविका", "महत्वाकांक्षा पूर्ति, राजकीय लाभ, पुरस्कार", "दान, आध्यात्मिक त्याग, मोक्ष साधना"
                ]
                for _h_idx in range(1, 13):
                    _target_sid = ((_sun.sign_id - 1 + (_h_idx - 1)) % 12) + 1
                    _target_sname = SIGN_NAMES[_target_sid - 1]
                    _h_lord = SIGN_LORDS.get(_target_sname, "")
                    _occ_p = [_pn for _pn, _pp in chart.planets.items() if _pp.sign_id == _target_sid]
                    _occ_str = ", ".join(_occ_p) if _occ_p else "—"
                    _s_house_rows.append(f'<tr style="border-bottom:1px solid #E2E8F0;"><td style="padding:4px 6px; font-weight:800; color:#B45309;">{_h_idx} भाव</td><td style="padding:4px 6px; font-weight:700;">{_target_sname}</td><td style="padding:4px 6px; color:#475569;">{_h_lord}</td><td style="padding:4px 6px; font-weight:800; color:#0F172A;">{_occ_str}</td><td style="padding:4px 6px; font-size:10.5px; color:#475569;">{_s_signifs[_h_idx-1]}</td></tr>')

                _sh_tbl_html = f'<div style="background:#FFFFFF; border:1px solid #CBD5E1; border-radius:8px; padding:4px; max-height:220px; overflow-y:auto; margin-bottom:10px;"><table style="width:100%; border-collapse:collapse; font-size:11.5px;"><thead><tr style="background:#F1F5F9; color:#475569; font-weight:800; border-bottom:1.5px solid #CBD5E1;"><th style="padding:4px 6px; text-align:left;">भाव</th><th style="padding:4px 6px; text-align:left;">राशि</th><th style="padding:4px 6px; text-align:left;">स्वामी</th><th style="padding:4px 6px; text-align:left;">स्थित ग्रह</th><th style="padding:4px 6px; text-align:left;">जीवन क्षेत्र</th></tr></thead><tbody>{"".join(_s_house_rows)}</tbody></table></div>'
                st.markdown(_sh_tbl_html, unsafe_allow_html=True)

                # ─── Solar Yogas Engine ───
                st.markdown("#### 🌟 सूर्य आधारित प्रमुख योग (Classical Solar Yogas)")
                _solar_yogas = []

                # 1. Budhaditya
                _merc = chart.planets.get("Mercury")
                if _merc and _merc.sign_id == _sun.sign_id:
                    _b_diff = abs(_sun.longitude - _merc.longitude)
                    if _b_diff > 180: _b_diff = 360 - _b_diff
                    if _b_diff <= 10.0:
                        _comb_label = " (बुध अस्त नहीं / पूर्ण प्रखर)" if not _merc.is_combust else " (बुध अस्त / ज्ञान प्रबल)"
                        _solar_yogas.append(("⚡ बुधादित्य योग (Budhaditya)", f"सूर्य एवं बुध की एक ही राशि में युति (अंतर: {_b_diff:.2f}°){_comb_label}। जातक असाधारण मेधावी, विश्लेषण में दक्ष एवं प्रशासनिक क्षमता से युक्त होता है।", "#EFF6FF", "#1E40AF"))

                # 2. Vesi, Vosi, Ubhayachari
                _h2_s_planets = [pn for pn, p in chart.planets.items() if p.sign_id == (((_sun.sign_id) % 12) + 1) and pn not in ["Moon", "Rahu", "Ketu"]]
                _h12_s_planets = [pn for pn, p in chart.planets.items() if p.sign_id == (((_sun.sign_id - 2 + 12) % 12) + 1) and pn not in ["Moon", "Rahu", "Ketu"]]

                if _h2_s_planets and _h12_s_planets:
                    _solar_yogas.append(("👑 उभयाचारी योग (Ubhayachari)", f"सूर्य के दोनों ओर (द्वितीय में {', '.join(_h2_s_planets)} एवं द्वादश में {', '.join(_h12_s_planets)}) ग्रह स्थित हैं। जातक राजा समान सम्मानित, वक्तृत्व कला में निपुण, स्थिर वैभव व सुखी होता है।", "#FEF3C7", "#92400E"))
                elif _h2_s_planets:
                    _is_subha = any(p in ["Jupiter", "Venus", "Mercury"] for p in _h2_s_planets)
                    if _is_subha:
                        _solar_yogas.append(("🏛️ शुभ-वेसि योग (Subha-Vesi)", f"सूर्य से द्वितीय भाव में शुभ ग्रह ({', '.join(_h2_s_planets)}) स्थित हैं। जातक सत्यवादी, वाक्पटु, उदार, धैर्यवान एवं प्रचुर धन-धान्य से संपन्न होता है। (BPHS)", "#DCFCE7", "#166534"))
                    else:
                        _solar_yogas.append(("🏛️ पाप-वेसि योग (Papa-Vesi)", f"सूर्य से द्वितीय भाव में क्रूर ग्रह ({', '.join(_h2_s_planets)}) स्थित हैं। जातक तीव्र पराक्रमी, साहसी एवं स्वतंत्र आजीविका का स्वामी होता है।", "#FEF3C7", "#B45309"))
                elif _h12_s_planets:
                    _is_subha_v = any(p in ["Jupiter", "Venus", "Mercury"] for p in _h12_s_planets)
                    if _is_subha_v:
                        _solar_yogas.append(("📚 शुभ-वोसि योग (Subha-Vosi)", f"सूर्य से द्वादश भाव में शुभ ग्रह ({', '.join(_h12_s_planets)}) स्थित हैं। जातक बुद्धिमान, विद्यावान, परोपकारी, यशस्वी एवं उच्च संस्कारों से युक्त होता है। (BPHS)", "#F0FDF4", "#065F46"))
                    else:
                        _solar_yogas.append(("📚 पाप-वोसि योग (Papa-Vosi)", f"सूर्य से द्वादश भाव में क्रूर ग्रह ({', '.join(_h12_s_planets)}) स्थित हैं। जातक कर्मठ, यात्राप्रिय एवं गुप्त युक्तियों में कुशल होता है।", "#FEF3C7", "#B45309"))
                else:
                    _solar_yogas.append(("☀️ स्वतंत्र सौर तेज (Independent Sun)", "सूर्य के अगल-बगल कोई ग्रह नहीं है; जातक आत्मनिर्भर, आत्म-प्रेरित एवं स्वतंत्र व्यक्तित्व का धनी होता है।", "#F8FAFC", "#334155"))

                for _yt, _yd, _bg, _fg in _solar_yogas:
                    st.markdown(f'<div style="background:{_bg}; border:1px solid #CBD5E1; border-radius:6px; padding:6px 10px; margin-bottom:5px;"><span style="font-weight:900; color:{_fg}; font-size:12px;">{_yt}:</span> <span style="font-size:11.5px; color:#1E293B;">{_yd}</span></div>', unsafe_allow_html=True)
        else:
            st.warning("सूर्य की स्थिति उपलब्ध नहीं।")


    with tab_yuddha:
        st.markdown("### ⚔️ ग्रह युद्ध (Graha Yuddha — Classical Planetary War Engine)")
        st.info("बृहत्संहिता (अध्याय १७) एवं सूर्य सिद्धांत अनुसार जब पांच तारा ग्रह (मंगल, बुध, गुरु, शुक्र, शनि) परस्पर १° (६० कला) के भीतर आ जाते हैं, तो उनके मध्य 'ग्रह युद्ध' घटित होता है। उत्तर अक्षांश (Greater North Latitude) वाला ग्रह विजयी होकर बलवान होता है तथा पराजित ग्रह अपनी प्राकृतिक शक्ति (षड्बल) खो देता है:")

        try:
            _yw_list = default_chart_calculator.detect_graha_yuddha(chart)
            _tara_grahas = ["Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
            _GRAHA_HINDI = {"Mars": "♂ मंगल", "Mercury": "☿ बुध", "Jupiter": "♃ गुरु", "Venus": "♀ शुक्र", "Saturn": "♄ शनि"}

            # ─── 5×5 Tara Grahas Distance Matrix ───
            st.markdown("#### 🔬 पंचतारा ग्रह परस्पर कोणीय दूरी मैट्रिक्स (5×5 Angular Separation Matrix)")
            _matrix_headers = "".join([f'<th style="padding:6px 8px; text-align:center; background:#1E293B; color:#F8FAFC; font-size:11.5px;">{_GRAHA_HINDI.get(p, p)}</th>' for p in _tara_grahas])
            _matrix_rows = []

            for p1 in _tara_grahas:
                _cells = [f'<td style="padding:6px 8px; font-weight:800; background:#F1F5F9; color:#1E293B;">{_GRAHA_HINDI.get(p1, p1)}</td>']
                for p2 in _tara_grahas:
                    if p1 == p2:
                        _cells.append('<td style="padding:6px 8px; text-align:center; background:#E2E8F0; color:#94A3B8; font-weight:700;">—</td>')
                    else:
                        _p1_obj = chart.planets.get(p1)
                        _p2_obj = chart.planets.get(p2)
                        if _p1_obj and _p2_obj:
                            _d = abs(_p1_obj.longitude - _p2_obj.longitude) % 360.0
                            if _d > 180.0: _d = 360.0 - _d
                            if _d <= 1.0:
                                _bg, _fg, _sym = "#FEE2E2", "#991B1B", "⚔️ "
                            elif _d <= 3.0:
                                _bg, _fg, _sym = "#FEF3C7", "#92400E", "⚠️ "
                            elif _d <= 5.0:
                                _bg, _fg, _sym = "#EFF6FF", "#1E40AF", "🟡 "
                            else:
                                _bg, _fg, _sym = "#F8FAFC", "#475569", ""
                            _cells.append(f'<td style="padding:6px 8px; text-align:center; background:{_bg}; color:{_fg}; font-family:monospace; font-weight:800;">{_sym}{_d:.2f}°</td>')
                        else:
                            _cells.append('<td style="padding:6px 8px; text-align:center;">—</td>')
                _matrix_rows.append(f'<tr style="border-bottom:1px solid #CBD5E1;">{"".join(_cells)}</tr>')

            _mat_html = f'<div style="overflow-x:auto; background:#FFFFFF; border:1.5px solid #CBD5E1; border-radius:8px; margin-bottom:14px;"><table style="width:100%; border-collapse:collapse; font-size:11.5px;"><thead><tr><th style="padding:6px 8px; text-align:left; background:#0F172A; color:#F8FAFC;">तारा ग्रह</th>{_matrix_headers}</tr></thead><tbody>{"".join(_matrix_rows)}</tbody></table></div>'
            st.markdown(_mat_html, unsafe_allow_html=True)
            st.caption("🟢 >5° शांत | 🟡 3°-5° युति क्षेत्र | ⚠️ 1°-3° सन्निकट संपर्क | ⚔️ ≤1°00' प्रत्यक्ष ग्रह युद्ध")

            # ─── War Status Verdict Cards ───
            if _yw_list:
                st.markdown("#### ⚔️ सक्रिय ग्रह युद्ध विवरण एवं फल प्रभाव")
                for _yw in _yw_list:
                    _p1 = _yw.get('planet1')
                    _p2 = _yw.get('planet2')
                    _sep = _yw.get('separation_deg', 0.0)
                    _win = _yw.get('winner')
                    _los = _yw.get('loser')

                    # Brihat Samhita War Classification
                    if _sep < 0.25:
                        _w_type = "भेदम (Bhedam — पूर्ण ग्रसन / परस्पर भेदन)"
                    elif _sep < 0.50:
                        _w_type = "उल्लेखम (Ullekham — कोर स्पर्श / संघर्ष)"
                    elif _sep < 0.75:
                        _w_type = "अंशुमर्दम (Amshumardam — किरणों का टकराव)"
                    else:
                        _w_type = "अपसव्यम (Apasavyam — वक्र गति युक्त युद्ध)"

                    _w_lord, _l_lord = [], []
                    if hasattr(chart, 'houses') and chart.houses:
                        if isinstance(chart.houses, dict):
                            _w_lord = [f"{h}वें" for h, s in chart.houses.items() if getattr(s, 'lord', '') == _win]
                            _l_lord = [f"{h}वें" for h, s in chart.houses.items() if getattr(s, 'lord', '') == _los]
                        elif isinstance(chart.houses, (list, tuple)):
                            _w_lord = [f"{getattr(s, 'house_number', idx+1)}वें" for idx, s in enumerate(chart.houses) if getattr(s, 'lord', '') == _win]
                            _l_lord = [f"{getattr(s, 'house_number', idx+1)}वें" for idx, s in enumerate(chart.houses) if getattr(s, 'lord', '') == _los]

                    _w_lord_str = f" ({', '.join(_w_lord)} भाव का स्वामी)" if _w_lord else ""
                    _l_lord_str = f" ({', '.join(_l_lord)} भाव का स्वामी)" if _l_lord else ""

                    st.markdown(f"""
                    <div style="background:#FEF2F2; border:1.5px solid #EF4444; border-radius:10px; padding:14px; margin-bottom:12px;">
                        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                            <span style="font-weight:900; color:#B91C1C; font-size:14px;">⚔️ {_GRAHA_HINDI.get(_p1, _p1)} बनाम {_GRAHA_HINDI.get(_p2, _p2)}</span>
                            <span style="background:#FEE2E2; color:#991B1B; font-weight:800; padding:2px 8px; border-radius:4px; font-size:11.5px;">अंतर: {_sep:.3f}° ({_sep*60:.1f} कला)</span>
                        </div>
                        <div style="font-size:12.5px; color:#1E293B; line-height:1.6;">
                            • <b>युद्ध प्रकार:</b> {_w_type}<br/>
                            • 🏆 <b>विजेता ग्रह:</b> <b style="color:#047857;">{_GRAHA_HINDI.get(_win, _win)}</b>{_w_lord_str} (उत्तर अक्षांश की प्रधानता के कारण विजयी)<br/>
                            • ⚠️ <b>पराजित ग्रह:</b> <b style="color:#DC2626;">{_GRAHA_HINDI.get(_los, _los)}</b>{_l_lord_str} (षड्बल व चेष्टा बल हरण के कारण निर्बल)<br/>
                            • <b>फल प्रभाव:</b> विजयी ग्रह के स्वामित्व वाले भावों के शुभ फल में वृद्धि होगी; पराजित ग्रह के स्वामित्व वाले भावों से संबंधित विषयों में संघर्ष अथवा विलम्ब का सामना करना पड़ सकता है।<br/>
                            • 📜 <b>चेष्टा बल हरण सूत्र (सूर्य सिद्धांत व फलदीपिका):</b> पराजित ग्रह की विंशोत्तरी महादशा या अंतर्दशा के दौरान संबंधित भावों के फल में गतिरोध रहता है, जबकि विजयी ग्रह जीवन में अप्रत्याशित विजय एवं वर्चस्व दिलाता है।
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                # Find closest approach among Tara Grahas
                _min_sep = 999.0
                _close_pair = ("", "")
                for i, p1 in enumerate(_tara_grahas):
                    for p2 in _tara_grahas[i+1:]:
                        if p1 in chart.planets and p2 in chart.planets:
                            _d = abs(chart.planets[p1].longitude - chart.planets[p2].longitude) % 360.0
                            if _d > 180.0: _d = 360.0 - _d
                            if _d < _min_sep:
                                _min_sep = _d
                                _close_pair = (p1, p2)

                st.markdown(f"""
                <div style="background:linear-gradient(135deg, #ECFDF5 0%, #F0FDF4 100%); border:1.5px solid #10B981; border-radius:10px; padding:16px; margin-bottom:12px; box-shadow:0 2px 6px rgba(16, 185, 129, 0.1);">
                    <div style="display:flex; align-items:center; gap:8px; margin-bottom:6px;">
                        <span style="font-size:18px;">🛡️</span>
                        <span style="font-size:14.5px; font-weight:900; color:#065F46;">ग्रह मैत्री एवं शांति प्रशस्ति (No Planetary War Detected)</span>
                    </div>
                    <div style="font-size:12.5px; color:#1E293B; line-height:1.6;">
                        इस जन्म पत्रिका में पांचों तारा ग्रह (मंगल, बुध, गुरु, शुक्र, शनि) परस्पर सुरक्षित कोणीय दूरी पर स्थित हैं। किसी भी ग्रह के मध्य १° के भीतर का संघर्ष (युद्ध) नहीं है।<br/>
                        • <b>निकटतम संपर्क:</b> {_GRAHA_HINDI.get(_close_pair[0], _close_pair[0])} एवं {_GRAHA_HINDI.get(_close_pair[1], _close_pair[1])} — कोणीय अंतर: <b>{_min_sep:.2f}°</b><br/>
                        • <b>शास्त्रीय लाभ:</b> समस्त ग्रह स्वतंत्र होकर अपने पूर्ण षड्बल एवं नैसर्गिक सामर्थ्य के साथ अपना शुभाशुभ फल प्रदान करने में सक्षम हैं। किसी भी ग्रह का बल हरण (Bala Harana) नहीं हुआ है।
                    </div>
                </div>
                """, unsafe_allow_html=True)

        except Exception as _egy:
            st.error(f"ग्रह युद्ध गणना त्रुटि: {_egy}")


    with tab_vishesh:
        st.markdown("### 🌟 विशेष लग्न एवं १२ आरूढ़ पद महा-विश्लेषण (All 12 Arudha Padas & Special Lagnas Deep Dive)")
        st.info("महर्षि जैमिनी के सूत्र अनुसार 'पदं पितृभ्यः' — प्रत्येक भाव का आरूढ़ पद उस भाव का सांसारिक प्रतिबिंब (Maya / Worldly Manifestation) होता है। लोग जातक को सांसारिक रूप में कैसा देखते हैं, इसका रहस्य आरूढ़ पदों में समाहित है:")

        if chart.jaimini and getattr(chart.jaimini, 'arudha_details', None):
            jm = chart.jaimini
            a_details = jm.arudha_details

            # ─── Complete 12 Arudha Master Table ───
            st.markdown("#### 📜 समस्त १२ आरूढ़ पद संपूर्ण विवरण (Master Arudha Padas Matrix)")
            _arudha_order = ["AL", "A2", "A3", "A4", "A5", "A6", "A7", "A8", "A9", "A10", "A11", "UL"]
            _ar_rows = []
            for _ak in _arudha_order:
                _ad = a_details.get(_ak)
                if not _ad:
                    continue
                _is_special = _ak in ["AL", "UL"]
                _lbl_col = "#B45309" if _is_special else "#1E3A8A"
                _ar_rows.append({
                    "आरूढ़ पद": _ak,
                    "स्रोत भाव": f"{_ad.get('house_num', 1)} भाव",
                    "स्रोत राशि": _ad.get('house_sign', ''),
                    "भाव स्वामी": _ad.get('lord_name', ''),
                    "स्वामी की राशि": _ad.get('lord_sign', ''),
                    "दूरी (कदम)": f"{_ad.get('distance', 1)} राशि",
                    "लागू नियम": _ad.get('exception', 'सामान्य'),
                    "आरूढ़ राशि": _ad.get('pada_sign_name', ''),
                    "लग्न से भाव": f"{_ad.get('pada_house_from_lagna', 1)} भाव",
                    "शास्त्रीय प्रयोजन / फल": _ad.get('signification_hi', '').split(':', 1)[-1].strip()
                })
            st.dataframe(pd.DataFrame(_ar_rows), use_container_width=True, hide_index=True)

            # ─── Deep Dive Analytical Cards: AL, UL & Wealth ───
            st.markdown("#### 🔬 प्रमुख आरूढ़ पदों का गहन विश्लेषण (Arudha Lagna & Upapada Deep Dive)")
            col_ad1, col_ad2 = st.columns(2, gap="medium")

            with col_ad1:
                _al_data = a_details.get("AL", {})
                _al_h = _al_data.get("pada_house_from_lagna", 1)
                _al_sign = _al_data.get("pada_sign_name", "")

                if _al_h in [1, 4, 7, 10]:
                    _al_rel = "केंन्द्र संबंध (1/4/7/10 Axis) — जातक की आंतरिक क्षमता एवं बाह्य सामाजिक छवि में श्रेष्ठ सामंजस्य है।"
                    _al_bg, _al_bdr = "#F0FDF4", "#86EFAC"
                elif _al_h in [5, 9]:
                    _al_rel = "त्रिकोण संबंध (5/9 Axis) — पूर्वपुण्य एवं धर्म का प्रबल प्रभाव; समाज में जातक को स्वाभाविक आदर व सम्मान प्राप्त होता है।"
                    _al_bg, _al_bdr = "#ECFDF5", "#6EE7B7"
                elif _al_h in [3, 6, 11]:
                    _al_rel = "उपचय संबंध (3/6/11 Axis) — जातक निरंतर पुरुषार्थ एवं उद्योग द्वारा अपनी सामाजिक छवि को विशाल बनाता है।"
                    _al_bg, _al_bdr = "#EFF6FF", "#93C5FD"
                else:
                    _al_rel = "षडाष्टक/व्यय संबंध (6/8/12 Axis) — जातक का आंतरिक सत्य एवं बाह्य छवि भिन्न हो सकती है; जनसामान्य द्वारा गलत समझे जाने का अंदेशा।"
                    _al_bg, _al_bdr = "#FFFBEB", "#FCD34D"

                st.markdown(f"""
                <div style="background:{_al_bg}; border:1.5px solid {_al_bdr}; border-radius:10px; padding:14px; height:100%;">
                    <h5 style="color:#1E3A8A; margin:0 0 6px 0;">👑 आरूढ़ लग्न (AL): {_al_sign} (लग्न से {_al_h} भाव)</h5>
                    <div style="font-size:12.5px; color:#1E293B; line-height:1.6;">
                        <b>संबंध स्वरूप:</b> {_al_rel}<br/>
                        • <b>सामाजिक प्रतिष्ठा:</b> आरूढ़ लग्न जातक की सामाजिक स्थिति, करियर में यश एवं जनता में पहचान का निर्णायक है।<br/>
                        • <b>शास्त्रीय नियम:</b> यदि आरूढ़ लग्न से एकादश भाव में शुभ ग्रह स्थित हों, तो जातक निरंतर प्रचुर मात्रा में धन अर्जित करता है; दशम भाव में शुभ ग्रह होने पर व्यक्ति की आजीविका स्वच्छ एवं सम्मानित होती है।
                    </div>
                </div>
                """, unsafe_allow_html=True)

            with col_ad2:
                _ul_data = a_details.get("UL", {})
                _ul_h = _ul_data.get("pada_house_from_lagna", 1)
                _ul_sign = _ul_data.get("pada_sign_name", "")
                _ul_lord = _ul_data.get("lord_name", "")

                st.markdown(f"""
                <div style="background:#FDF2F8; border:1.5px solid #F472B6; border-radius:10px; padding:14px; height:100%;">
                    <h5 style="color:#9D174D; margin:0 0 6px 0;">💍 उपपद लग्न (UL / A12): {_ul_sign} (लग्न से {_ul_h} भाव)</h5>
                    <div style="font-size:12.5px; color:#1E293B; line-height:1.6;">
                        <b>उपपद लग्न स्वामी:</b> {_ul_lord}<br/>
                        • <b>दांपत्य स्थायित्व:</b> उपपद लग्न जीवनसाथी के कुल, वैवाहिक जीवन की स्थिरता एवं जीवनसाथी के स्वभाव का मुख्य दर्पण है।<br/>
                        • <b>द्वितीय भाव सूत्र:</b> उपपद से द्वितीय भाव वैवाहिक संबंध के पालन-पोषण (Sustenance) का कारक है। यदि उपपद से द्वितीय भाव में शुभ ग्रह (गुरु, शुक्र) हों तो दांपत्य जीवन सुदीर्घ एवं सुखमय रहता है; पाप ग्रहों का प्रभाव रहने पर वैवाहिक समायोजन आवश्यक होता है।
                    </div>
                </div>
                """, unsafe_allow_html=True)

            # ─── Jaimini Rashi Drishti on AL and UL ───
            st.markdown("#### 👁️ आरूढ़ लग्न एवं उपपद पर जैमिनी राशि दृष्टि (Jaimini Rashi Drishti on AL & UL)")
            try:
                def _get_j_aspecting_signs(sid):
                    if sid in [1, 4, 7, 10]: # चर राशि -> स्थिर (निकटवर्ती छोड़कर)
                        fixed_s = [2, 5, 8, 11]
                        adj = (sid % 12) + 1
                        return [s for s in fixed_s if s != adj]
                    elif sid in [2, 5, 8, 11]: # स्थिर राशि -> चर (निकटवर्ती छोड़कर)
                        mov_s = [1, 4, 7, 10]
                        adj = ((sid - 2 + 12) % 12) + 1
                        return [s for s in mov_s if s != adj]
                    else: # द्विस्वभाव राशि -> अन्य 3 द्विस्वभाव
                        return [s for s in [3, 6, 9, 12] if s != sid]

                _al_sid = SIGN_NAMES.index(_al_sign) + 1 if _al_sign in SIGN_NAMES else 1
                _ul_sid = SIGN_NAMES.index(_ul_sign) + 1 if _ul_sign in SIGN_NAMES else 1

                _al_asp_sids = _get_j_aspecting_signs(_al_sid)
                _ul_asp_sids = _get_j_aspecting_signs(_ul_sid)

                _al_planets_asp = [pn for pn, p in chart.planets.items() if p.sign_id in _al_asp_sids]
                _ul_planets_asp = [pn for pn, p in chart.planets.items() if p.sign_id in _ul_asp_sids]

                col_jrd1, col_jrd2 = st.columns(2, gap="medium")
                with col_jrd1:
                    _al_asp_names = [SIGN_NAMES[s-1] for s in _al_asp_sids]
                    st.markdown(f"""
                    <div style="background:#F8FAFC; border:1px solid #CBD5E1; border-radius:8px; padding:10px 14px; font-size:12px; color:#1E293B;">
                        <b>👑 AL ({_al_sign}) पर दृष्टि देने वाली राशियां:</b> {', '.join(_al_asp_names)}<br/>
                        • <b>दृष्टि देने वाले ग्रह:</b> <b>{', '.join(_al_planets_asp) if _al_planets_asp else 'कोई प्रत्यक्ष ग्रह नहीं (केवल राशि दृष्टि)'}</b><br/>
                        • <b>प्रभाव:</b> शुभ ग्रहों की दृष्टि सामाजिक यश, सम्मान व पद-प्रतिष्ठा में वृद्धि करती है।
                    </div>
                    """, unsafe_allow_html=True)

                with col_jrd2:
                    _ul_asp_names = [SIGN_NAMES[s-1] for s in _ul_asp_sids]
                    st.markdown(f"""
                    <div style="background:#FDF2F8; border:1px solid #FBCFE8; border-radius:8px; padding:10px 14px; font-size:12px; color:#1E293B;">
                        <b>💍 UL ({_ul_sign}) पर दृष्टि देने वाली राशियां:</b> {', '.join(_ul_asp_names)}<br/>
                        • <b>दृष्टि देने वाले ग्रह:</b> <b>{', '.join(_ul_planets_asp) if _ul_planets_asp else 'कोई प्रत्यक्ष ग्रह नहीं (केवल राशि दृष्टि)'}</b><br/>
                        • <b>प्रभाव:</b> उपपद पर गुरु/शुक्र की राशि दृष्टि वैवाहिक सद्भाव, जीवनसाथी के परिवार से सहयोग एवं प्रेम में प्रगाढ़ता लाती है।
                    </div>
                    """, unsafe_allow_html=True)
            except Exception as _e_jrd:
                st.caption(f"जैमिनी दृष्टि गणना: {_e_jrd}")
        else:
            st.info("आरूढ़ पद गणना लोड हो रही है...")


    with tab_kota:
        st.markdown("### 🏰 कोटा चक्र दुर्ग आरेख (Kota Chakra Durga Fortress)")
        st.info("कोटा चक्र जातक के जन्म नक्षत्र पर आधारित एक प्राचीन रक्षात्मक दुर्ग (Fortress) संरचना है। यह चार संकेन्द्री सुरक्षा दीवारों में विभाजित होता है, जो जातक की आंतरिक जीवन शक्ति, स्वास्थ्य, संकटों से सुरक्षा एवं विजय का अचूक संकेत देता है:")

        try:
            kota_engine = default_kota_chakra_engine
            kota_data_m0 = kota_engine.calculate(chart)

            kc_col1, kc_col2 = st.columns([1, 1], gap="medium")
            with kc_col1:
                kota_svg_m0 = ChartRenderer.render_kota_chakra_svg(kota_data_m0, title=f"कोटा चक्र दुर्ग — {chart.birth_data.name if chart.birth_data else 'जातक'}")
                st.markdown(f'<div class="kundali-chart" style="width:100%; display:flex; justify-content:center; margin-bottom:10px;">{kota_svg_m0}</div>', unsafe_allow_html=True)

                st.markdown("""
                <div style="background:#F8FAFC; border:1px solid #CBD5E1; border-radius:8px; padding:10px; font-size:12px; color:#334155; line-height:1.5;">
                    <b>🏰 दुर्ग की ४ रक्षात्मक दीवारें (Concentric Enclosures):</b><br/>
                    • <b>१. स्तम्भ (Stambha):</b> दुर्ग का गर्भगृह (Heart/Core) — जीवन शक्ति व आरोग्य।<br/>
                    • <b>२. मध्य (Madhya):</b> दुर्ग का अन्तःपुर (Citadel) — आंतरिक संबल व परिवार।<br/>
                    • <b>३. प्राकार (Prakaara):</b> दुर्ग का परकोटा (Outer Rampart) — सुरक्षा प्राचीर।<br/>
                    • <b>४. बाह्य (Bahya):</b> दुर्ग के बाहर का क्षेत्र — बाह्य जगत एवं आने-जाने वाले ग्रह।
                </div>
                """, unsafe_allow_html=True)

            with kc_col2:
                _k_swami = kota_data_m0.get("kota_swami", "—")
                _k_pala = kota_data_m0.get("kota_pala", "—")
                _def_status = kota_data_m0.get("defense_status", "🛡️ सुरक्षित")
                _def_sum = kota_data_m0.get("defense_summary", "")

                # Strategic Defense Scorecard
                st.markdown(f"""
                <div style="display:grid; grid-template-columns:1fr 1fr; gap:8px; margin-bottom:10px;">
                    <div style="background:#EFF6FF; border:1px solid #93C5FD; border-radius:8px; padding:8px 12px;">
                        <div style="font-size:11px; color:#1E40AF; font-weight:800;">👑 दुर्ग स्वामी (Kota Swami)</div>
                        <div style="font-size:15px; font-weight:900; color:#1E293B;">{_k_swami}</div>
                        <div style="font-size:10px; color:#64748B;">दुर्ग का राजा / मूल जीवन शक्ति</div>
                    </div>
                    <div style="background:#F0FDF4; border:1px solid #86EFAC; border-radius:8px; padding:8px 12px;">
                        <div style="font-size:11px; color:#166534; font-weight:800;">🛡️ दुर्ग रक्षक (Kota Pala)</div>
                        <div style="font-size:15px; font-weight:900; color:#1E293B;">{_k_pala}</div>
                        <div style="font-size:10px; color:#64748B;">दुर्ग का सेनापति / सुरक्षा कवच</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                st.markdown(f"""
                <div style="background:#FFFBEB; border:1.5px solid #FCD34D; border-radius:8px; padding:10px 12px; margin-bottom:10px;">
                    <div style="font-weight:900; color:#92400E; font-size:12.5px; margin-bottom:4px;">दुर्ग रक्षा मूल्यांकन: {_def_status}</div>
                    <div style="font-size:11.5px; color:#1E293B; line-height:1.5;">{_def_sum}</div>
                </div>
                """, unsafe_allow_html=True)

                # Planet Allocations Table
                st.markdown("#### 🪐 दुर्ग में ग्रहों की स्थिति एवं गति")
                _p_allocs = kota_data_m0.get("planet_allocations", [])
                if _p_allocs:
                    _pl_k_rows = []
                    for _pa in _p_allocs:
                        _pn = _pa.get("planet", "")
                        _zn = _pa.get("zone", "")
                        _mo = _pa.get("motion", "")
                        _nat = _pa.get("nature", "Benefic")
                        _is_mal = ("Malefic" in _nat or _pn in ["Mars", "Saturn", "Rahu", "Ketu", "Sun"])
                        _p_col = "#DC2626" if _is_mal else "#059669"
                        _role_badge = f'<span style="background:{"#FEE2E2" if _is_mal else "#DCFCE7"}; color:{_p_col}; font-weight:800; padding:1px 6px; border-radius:4px; font-size:10.5px;">{"आक्रांता" if _is_mal else "रक्षक"}</span>'
                        _pl_k_rows.append(f'<tr style="border-bottom:1px solid #E2E8F0;"><td style="padding:4px 6px; font-weight:800; color:#1E293B;">{_pn}</td><td style="padding:4px 6px; color:#475569;">{_pa.get("nakshatra", "")}</td><td style="padding:4px 6px; font-weight:700;">{_zn}</td><td style="padding:4px 6px; font-size:11px;">{_mo}</td><td style="padding:4px 6px; text-align:center;">{_role_badge}</td></tr>')

                    _k_tbl_html = f'<div style="background:#FFFFFF; border:1px solid #CBD5E1; border-radius:8px; padding:4px; max-height:220px; overflow-y:auto;"><table style="width:100%; border-collapse:collapse; font-size:11.5px;"><thead><tr style="background:#F1F5F9; color:#475569; font-weight:800; border-bottom:1.5px solid #CBD5E1;"><th style="padding:4px 6px; text-align:left;">ग्रह</th><th style="padding:4px 6px; text-align:left;">नक्षत्र</th><th style="padding:4px 6px; text-align:left;">दुर्ग क्षेत्र</th><th style="padding:4px 6px; text-align:left;">गति दिशा</th><th style="padding:4px 6px; text-align:center;">भूमिका</th></tr></thead><tbody>{"".join(_pl_k_rows)}</tbody></table></div>'
                    st.markdown(_k_tbl_html, unsafe_allow_html=True)

                # ─── Live Transit Defense Assessment Overlay ───
                _stambha_malefics = [pa["planet"] for pa in _p_allocs if pa.get("zone") == "Stambha" and ("Malefic" in pa.get("nature", "") or pa["planet"] in ["Mars", "Saturn", "Rahu", "Ketu"])]
                _madhya_malefics = [pa["planet"] for pa in _p_allocs if pa.get("zone") == "Madhya" and ("Malefic" in pa.get("nature", "") or pa["planet"] in ["Mars", "Saturn", "Rahu", "Ketu"])]

                if _stambha_malefics:
                    st.warning(f"🚨 **दुर्ग स्तम्भ वेध संकट:** क्रूर ग्रह ({', '.join(_stambha_malefics)}) सीधे दुर्ग के स्तम्भ (गर्भगृह) में स्थित हैं। स्वास्थ्य, मानसिक शांति एवं सुरक्षा हेतु विशेष सावधानी अपेक्षित है।")
                elif _madhya_malefics:
                    st.info(f"⚠️ **मध्य परकोटा वेध:** क्रूर ग्रह ({', '.join(_madhya_malefics)}) मध्य प्राचीर में स्थित हैं। परिवार व वित्तीय सुरक्षा पर सतर्क दृष्टि रखें।")
                else:
                    st.success("🛡️ **दुर्ग गर्भगृह अभेद्य व सुरक्षित:** स्तम्भ एवं मध्य प्राचीर में किसी भी प्रमुख क्रूर ग्रह का वेध नहीं है; जातक का जीवन दुर्ग सुदृढ़ है।")

        except Exception as _ekc:
            st.error(f"कोटा चक्र गणना त्रुटि: {_ekc}")


    # =============================================================
    # TAB 3: AFFLICTION & FREE WILL ANALYSIS (GRAHALAKSHANAM CORE)

