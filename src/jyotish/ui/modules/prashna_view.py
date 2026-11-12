import streamlit as st
import pandas as pd
from datetime import datetime, timezone, timedelta, date, time
import re

from src.jyotish.core.models import KundaliChart
import importlib
import src.jyotish.services.prashna as prashna_mod
if not hasattr(prashna_mod.PrashnaService, "calculate_shodasha_sphutas") or not hasattr(prashna_mod.default_prashna_service, "calculate_shodasha_sphutas"):
    prashna_mod = importlib.reload(prashna_mod)
default_prashna_service = prashna_mod.default_prashna_service
PRASHNA_CATEGORIES = prashna_mod.PRASHNA_CATEGORIES
from src.jyotish.services.geocoding import default_geocoding_service
from src.jyotish.services.shastriya_pramana import SHASTRIYA_SHLOKAS
from src.jyotish.core.affliction import AfflictionEngine
from src.jyotish.ui.chart_renderer import ChartRenderer

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
        return "उच्च (Exalted)", 5, "#10B981"
    elif css == "moolatrikona":
        return "मूलत्रिकोण (Moolatrikona)", 4, "#059669"
    elif css == "own":
        return "स्वक्षेत्री (Own)", 3, "#3B82F6"
    elif css == "friendly":
        return "मित्रक्षेत्री (Friendly)", 2, "#6366F1"
    elif css == "neutral":
        return "सम (Neutral)", 1, "#64748B"
    elif css == "enemy":
        return "शत्रुक्षेत्री (Enemy)", -1, "#F59E0B"
    elif css == "debilitated":
        return "नीच (Debilitated)", -2, "#EF4444"
    return text, 0, "#64748B"

# Classical Deeptamsha Orbs
PRASHNA_DEEPTAMSHA = {
    "Sun": 15.0, "Moon": 12.0, "Mars": 8.0, "Mercury": 7.0,
    "Jupiter": 9.0, "Venus": 7.0, "Saturn": 9.0, "Rahu": 5.0, "Ketu": 5.0
}

def render_prashna_view(chart, tz_offset, latitude, longitude, default_city_name=None, render_chart_svg_fn=None, tabs=None):
    if default_city_name is None:
        default_city_name = st.session_state.get("birth_city", "New Delhi, Delhi, India")
    if render_chart_svg_fn is None:
        render_chart_svg_fn = render_chart_svg_default
    render_chart_svg = render_chart_svg_fn

    b_data = getattr(chart, "birth_data", None)
    name = b_data.name if (b_data and getattr(b_data, "name", None)) else st.session_state.get("birth_name", "सक्रिय जातक")
    
    is_dark = st.session_state.get("dark_mode", False)
    is_astrallis_mode = st.session_state.get("astrallis_mode", False)
    is_night_mode = is_dark

    if tabs is None:
        tabs = [
            '👤 जातक प्रश्न विश्लेषण',
            '✍️ नया तात्कालिक प्रश्न',
            '🪐 प्रश्न ग्रह स्थिति',
            '🎭 द्वादश भाव भूमिका',
            '📖 ताजिक व इत्थशाल',
            '📜 १०० शास्त्रीय प्रश्न नियम'
        ]

    def _clean_html(s: str) -> str:
        """Helper to ensure no 4+ indentation spaces for streamlit markdown HTML."""
        return "".join(line.strip() for line in s.splitlines() if line.strip())

    def _render_prashna_graha_bala_svg(graha_table: list, is_dark: bool = False) -> str:
        """Generates an aesthetic SVG bar chart for operational planetary strengths in Horary chart."""
        scores = {}
        for g in graha_table:
            p_name = g.get("graha", "")
            base = 12
            h_str = str(g.get("house", "1"))
            try:
                h_num = int(re.sub(r"[^\d]", "", h_str))
            except Exception:
                h_num = 1
            if h_num in [1, 4, 7, 10]:
                base += 7
            elif h_num in [5, 9]:
                base += 5
            elif h_num in [3, 11]:
                base += 3
            elif h_num in [6, 8, 12]:
                base -= 4
            if g.get("is_retrograde"):
                base += 3
            dig = g.get("dignity", "")
            if "उच्च" in dig or "Exalted" in dig:
                base += 5
            elif "मूल" in dig:
                base += 4
            elif "स्व" in dig or "Own" in dig:
                base += 3
            elif "नीच" in dig or "Debilitated" in dig:
                base -= 5
            scores[p_name] = max(3, min(25, base))

        bg = "#1e293b" if is_dark else "#f8fafc"
        text_c = "#f1f5f9" if is_dark else "#0f172a"
        card_border = "#334155" if is_dark else "#cbd5e1"
        bar_bg = "#334155" if is_dark else "#e2e8f0"

        planets_order = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]
        colors = {
            "Sun": "#f59e0b", "Moon": "#38bdf8", "Mars": "#ef4444", "Mercury": "#10b981",
            "Jupiter": "#eab308", "Venus": "#ec4899", "Saturn": "#6366f1", "Rahu": "#8b5cf6", "Ketu": "#64748b"
        }
        hi_names = {
            "Sun": "सूर्य (Surya)", "Moon": "चन्द्र (Chandra)", "Mars": "मंगल (Mangal)", "Mercury": "बुध (Budha)",
            "Jupiter": "गुरु (Guru)", "Venus": "शुक्र (Shukra)", "Saturn": "शनि (Shani)", "Rahu": "राहु (Rahu)", "Ketu": "केतु (Ketu)"
        }

        svg_parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 760 300" width="100%" style="background:{bg};border:1px solid {card_border};border-radius:12px;font-family:system-ui,-apple-system,sans-serif;">',
            f'<text x="24" y="26" fill="{text_c}" font-size="13" font-weight="700">🪐 प्रश्नकालीन नवग्रह सामर्थ्य व क्रियाशीलता सूचकांक (Planetary Horary Strength)</text>',
            f'<text x="640" y="26" fill="#64748b" font-size="11" font-weight="600">अधिकतम: 25 अंक</text>'
        ]

        y = 52
        for p in planets_order:
            sc = scores.get(p, 12)
            col = colors.get(p, "#3b82f6")
            hi = hi_names.get(p, p)
            bar_w = int((sc / 25.0) * 470)
            pct = int((sc / 25.0) * 100)

            svg_parts.append(f'<text x="24" y="{y+13}" fill="{text_c}" font-size="11" font-weight="600">{hi}</text>')
            svg_parts.append(f'<rect x="150" y="{y+2}" width="470" height="15" rx="4" fill="{bar_bg}" opacity="0.6" />')
            svg_parts.append(f'<rect x="150" y="{y+2}" width="{bar_w}" height="15" rx="4" fill="{col}" />')
            svg_parts.append(f'<text x="635" y="{y+13}" fill="{col}" font-size="11" font-weight="700">{sc}/25 ({pct}%)</text>')
            y += 26

        svg_parts.append('</svg>')
        return "".join(svg_parts)

    cat_options = [
        f"{c.get('icon', '🔮')} {c.get('Name_Hi', c.get('Name', 'Category'))} ({c.get('Name', '')})"
        for c in PRASHNA_CATEGORIES
    ]

    sample_queries = {
        "Health": "क्या मरीज को वर्तमान बीमारी से शीघ्र स्वास्थ्य लाभ मिलेगा?",
        "Marriage": "क्या इस वर्ष मेरा विवाह तय हो जाएगा?",
        "Relationship": "क्या हमारे प्रेम सम्बंध में सामंजस्य और स्थायित्व रहेगा?",
        "Child": "क्या संतान प्राप्ति के शुभ योग बन रहे हैं?",
        "Wealth": "क्या मुझे रुका हुआ धन वापस मिलेगा और आर्थिक स्थिति सुधरेगी?",
        "Career": "क्या मुझे कार्यक्षेत्र में उच्च पद और प्रतिष्ठा प्राप्त होगी?",
        "Job": "क्या मुझे नई नौकरी या पदोन्नति मिलेगी?",
        "Business": "क्या नया व्यापार प्रारंभ करना लाभदायक रहेगा?",
        "Property": "क्या यह भूमि या मकान खरीदना मेरे लिए शुभ रहेगा?",
        "Investment": "क्या इस निवेश या शेयर बाज़ार में मुझे अच्छा लाभ होगा?",
        "Litigation / Court": "क्या न्यायालय में चल रहे मुक़दमे में मेरी विजय होगी?",
        "Foreign Travel": "क्या मेरा विदेश यात्रा का वीज़ा स्वीकृत हो जाएगा?",
        "Education / Exam": "क्या मुझे इस प्रतियोगी परीक्षा में सफलता मिलेगी?",
        "Lost Item": "क्या खोई हुई वस्तु पुनः प्राप्त हो जाएगी?",
        "Purchase Vehicle": "क्या नया वाहन खरीदना इस समय अनुकूल रहेगा?",
        "Partnership": "क्या यह व्यापारिक साझेदारी दीर्घकालिक सफल होगी?",
        "Debt / Loan": "क्या मुझे क़र्ज़ से शीघ्र मुक्ति मिलेगी?",
        "Relocation / Transfer": "क्या मेरा वांछित स्थान पर तबादला हो जाएगा?",
        "Surgery / Diagnosis": "क्या शल्य चिकित्सा (सर्जरी) सकुशल संपन्न होगी?",
        "Spiritual Initiation": "क्या मुझे सद्गुरु की कृपा और मंत्र दीक्षा प्राप्त होगी?",
        "Construction / Vastu": "क्या नवीन गृह निर्माण निर्विघ्न संपन्न होगा?",
        "Friends / Enemies": "क्या शत्रु पक्ष शांत रहेगा और मित्रों का सहयोग मिलेगा?",
        "General Prashna": "क्या मेरा अभीष्ट कार्य सफलतापूर्वक सिद्ध होगा?"
    }

    # Classical Deeptamsha Orbs
    PRASHNA_DEEPTAMSHA = {
        "Sun": 15.0, "Moon": 12.0, "Mars": 8.0, "Mercury": 7.0,
        "Jupiter": 9.0, "Venus": 7.0, "Saturn": 9.0, "Rahu": 5.0, "Ketu": 5.0
    }

    # Ensure baseline calculation exists
    if "prashna_native_res" not in st.session_state or not isinstance(st.session_state.prashna_native_res, dict) or not st.session_state.prashna_native_res.get("all_rules"):
        try:
            st.session_state.prashna_native_res = default_prashna_service.generate_prashna_chart(
                query_text="क्या मेरा अभीष्ट कार्य सफलतापूर्वक सिद्ध होगा?",
                category_name="Job",
                latitude=latitude,
                longitude=longitude,
                timezone_offset=tz_offset,
                query_dt=get_live_local_now(tz_offset),
                questioner_name=name
            )
        except Exception:
            pass

    if "active_prashna_res" not in st.session_state or not st.session_state.active_prashna_res:
        st.session_state.active_prashna_res = st.session_state.get("prashna_native_res")

    # Active Native Micro-Planetary Longitudes & DMS Console
    lagna_sname = getattr(chart, "lagna_sign_name", "Aries")
    l_deg = getattr(chart, "lagna_degree", 0.0)
    l_ansh = int(l_deg)
    l_kala = int(round((l_deg - l_ansh) * 60.0))
    if l_kala >= 60:
        l_kala = 0
        l_ansh += 1
    l_dms = f"{l_ansh}° {l_kala:02d}'"

    moon = chart.planets.get("Moon")
    if moon:
        m_deg = getattr(moon, "sign_degree", 0.0)
        m_ansh = int(m_deg)
        m_kala = int(round((m_deg - m_ansh) * 60.0))
        if m_kala >= 60:
            m_kala = 0
            m_ansh += 1
        m_dms = f"{m_ansh}° {m_kala:02d}'"
        m_nak = getattr(moon, "nakshatra_name", getattr(moon, "nakshatra", "—"))
        m_pada = getattr(moon, "nakshatra_pada", getattr(moon, "pada", 1))
        moon_str = f"{moon.sign_name} {m_dms} [{m_nak}-P{m_pada}]"
    else:
        moon_str = "—"

    # Active Prashna baseline details
    cur_p_init = st.session_state.get("active_prashna_res") or st.session_state.get("prashna_native_res") or {}
    p_lagna_str = cur_p_init.get("prashna_lagna", "—")
    p_lagnesh_str = cur_p_init.get("lagnesh", "—")
    p_karyesh_str = cur_p_init.get("karyesh", "—")
    p_yoga_str = cur_p_init.get("tajika_yoga", "—")
    p_verdict_str = str(cur_p_init.get("verdict", "उत्कृष्ट")).split(" (")[0]

    # CSS for compact unified expanders & zero top scroll
    st.markdown("""
    <style>
    div[data-testid="stExpander"] {
        margin-top: 6px !important;
        margin-bottom: 6px !important;
    }
    div[data-testid="stExpander"] details {
        border-radius: 8px !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # 6 Main Tabs as requested by user
    ptab1, ptab2, ptab3, ptab4, ptab5, ptab6 = st.tabs(tabs)

    # =========================================================================
    # TAB 1: सक्रिय जातक प्रश्न विश्लेषण (Active Native Dual Synthesis)
    # =========================================================================
    with ptab1:
        # Sub-tabs for Tab 1: सक्रिय जातक प्रश्न विश्लेषण
        subtab_p1_charts, subtab_p1_synthesis = st.tabs([
            "1. ♊ जन्म कुण्डली एवं तात्कालिक प्रश्न कुण्डली द्वि-चक्र दर्शन",
            "2. ⚖️ जन्म कुण्डली vs प्रश्न कुण्डली शास्त्रीय समन्वय"
        ])

        with subtab_p1_charts:
            with st.expander("👤 सक्रिय जातक प्रश्न विश्लेषण (Active Native Dual Horary Synthesis)", expanded=True):
                st.caption(f"सक्रिय जातक: **{name}** | जन्म स्थान: **{default_city_name}** | तात्कालिक प्रश्न कुण्डली एवं जन्म कुण्डली का शास्त्रीय समन्वय।")

                col_t1_c1, col_t1_c2 = st.columns([1, 2])
                with col_t1_c1:
                    cat_choice_nat = st.selectbox(
                        "प्रश्न श्रेणी चुनें (Select Category)",
                        range(len(cat_options)),
                        format_func=lambda i: cat_options[i] if i < len(cat_options) else "",
                        index=min(6, max(0, len(cat_options) - 1)),
                        key="nat_prashna_cat_idx"
                    )
                    nat_cat_meta = PRASHNA_CATEGORIES[cat_choice_nat] if cat_choice_nat < len(PRASHNA_CATEGORIES) else PRASHNA_CATEGORIES[0]
                    nat_cat_name = nat_cat_meta.get("Name", "Job")
                with col_t1_c2:
                    nat_default_q = sample_queries.get(nat_cat_name, "क्या मेरा अभीष्ट कार्य सिद्ध होगा?")
                    nat_query_text = st.text_input("अपना प्रश्न दर्ज करें (Enter Native Query)", value=nat_default_q, key="nat_prashna_query_text")

                # Live Vartaman Date, Time & GPS Controls for Tab 1
                live_now_nat = get_live_local_now(tz_offset)
                if "nat_prashna_date_val" not in st.session_state:
                    st.session_state.nat_prashna_date_val = live_now_nat.date()
                if "nat_prashna_time_val" not in st.session_state:
                    st.session_state.nat_prashna_time_val = live_now_nat.time().replace(microsecond=0)

                def _cb_nat_set_live_now():
                    upd_now = get_live_local_now(tz_offset)
                    st.session_state.nat_prashna_date_val = upd_now.date()
                    st.session_state.nat_prashna_time_val = upd_now.time().replace(microsecond=0)
                    st.session_state.nat_prashna_d_picker = upd_now.date()
                    st.session_state.nat_prashna_t_picker = upd_now.time().replace(microsecond=0)

                col_nt1, col_nt2, col_nt3, col_nt4 = st.columns([1.4, 1.4, 1.2, 1.2])
                with col_nt1:
                    nat_q_date = st.date_input("📅 प्रश्न तिथि (Query Date)", value=st.session_state.nat_prashna_date_val, format="DD/MM/YYYY", key="nat_prashna_d_picker")
                    st.session_state.nat_prashna_date_val = nat_q_date
                with col_nt2:
                    nat_q_time = st.time_input("⏱️ प्रश्न समय (Time - सेकंड सहित)", value=st.session_state.nat_prashna_time_val, step=1, key="nat_prashna_t_picker")
                    st.session_state.nat_prashna_time_val = nat_q_time
                with col_nt3:
                    st.write("")
                    st.write("")
                    if st.button("⏱️ वर्तमान समय लोड करें", use_container_width=True, key="btn_nat_set_live_now", help="सटीक वर्तमान सेकंड-लेवल समय लोड करें", on_click=_cb_nat_set_live_now):
                        st.toast("✅ वर्तमान समय सेट किया गया!", icon="⏱️")
                with col_nt4:
                    st.write("")
                    st.write("")
                    if st.button("🛰️ वर्तमान GPS स्थान", use_container_width=True, key="btn_nat_set_gps", help="डिवाइस GPS अनुमति मांगकर सटीक वर्तमान स्थान लें"):
                        st.session_state.trigger_browser_gps = "nat_prashna"
                        st.rerun()

                calc_nat_btn = st.button("🔮 सक्रिय जातक प्रश्न विश्लेषण प्राप्त करें (Analyze Native Horary Query)", type="primary", use_container_width=True, key="btn_calc_nat_prashna")

            nat_target_dt = datetime.combine(st.session_state.nat_prashna_date_val, st.session_state.nat_prashna_time_val)

            need_nat_recalc = (
                calc_nat_btn
                or "prashna_native_res" not in st.session_state
                or not st.session_state.prashna_native_res
                or st.session_state.prashna_native_res.get("category") != nat_cat_name
            )

            if need_nat_recalc:
                try:
                    st.session_state.prashna_native_res = default_prashna_service.generate_prashna_chart(
                        query_text=nat_query_text,
                        category_name=nat_cat_name,
                        latitude=latitude,
                        longitude=longitude,
                        timezone_offset=tz_offset,
                        query_dt=nat_target_dt,
                        questioner_name=name
                    )
                    st.session_state.active_prashna_res = st.session_state.prashna_native_res
                    if calc_nat_btn:
                        st.toast("✅ सक्रिय जातक प्रश्न कुण्डली एवं समन्वय सफलतापूर्वक परिकलित!", icon="🔮")
                except Exception as e:
                    st.error(f"प्रश्न परिकलन में त्रुटि: {e}")

            p_nat_res = st.session_state.get("prashna_native_res") or default_prashna_service.generate_prashna_chart(
                query_text=nat_query_text, category_name=nat_cat_name, latitude=latitude, longitude=longitude, timezone_offset=tz_offset, query_dt=nat_target_dt, questioner_name=name
            )
            p_nat_chart: KundaliChart = p_nat_res.get("chart", chart)

            # 4 Top KPI Cards wrapped in Collapsible Expander
            with st.expander("🎯 प्रश्न फलसिद्धि निर्णय, समय एवं नियम सारांश (Horary Verdict & Timing Summary)", expanded=True):
                kpi1, kpi2, kpi3, kpi4 = st.columns(4)
                v_text_nat = str(p_nat_res.get("verdict", "उत्कृष्ट")).split(" (")[0]
                v_badge_nat = str(p_nat_res.get("verdict_badge", "✅ शुभ"))
                t_text_nat = str(p_nat_res.get("timing", "1 से 3 सप्ताह")).split(" (")[0]
                v_score_nat = float(p_nat_res.get("verdict_score", 0.75))
                pos_c_nat = p_nat_res.get("active_positive_count", 0)
                neg_c_nat = p_nat_res.get("active_negative_count", 0)

                kpi1.metric("🎯 शास्त्रीय निर्णय", v_text_nat, v_badge_nat)
                kpi2.metric("⏳ संभावित समय", t_text_nat)
                kpi3.metric("📊 सहमति व सिद्धि स्कोर", f"{int(v_score_nat * 100)}%")
                kpi4.metric("📜 100 शास्त्रीय नियम", f"✅ {pos_c_nat} शुभ | ⚠️ {neg_c_nat} बाधाएं")

                # Visual Probability Bar
                st.markdown(f"**फलसिद्धि संभावना सूचकांक (Success Probability): {int(v_score_nat * 100)}%**")
                st.progress(v_score_nat)

            # Dual Chart Display (Side-by-side)
            st.markdown("##### ♊ जन्म कुण्डली एवं तात्कालिक प्रश्न कुण्डली द्वि-चक्र दर्शन (Dual Chart View)")
            col_c_natal, col_c_prashna = st.columns(2)

            with col_c_natal:
                st.markdown(f"###### 📜 चक्र 1: जन्म कुण्डली (Natal D1 — {name})")
                natal_svg = render_chart_svg(chart, f"Natal D1 — {name}", varga_code="D1")
                st.markdown(f'<div style="max-width:90%;margin:0 auto;">{natal_svg}</div>', unsafe_allow_html=True)
                st.caption(f"जन्म लग्न: **{chart.lagna_sign_name} ({l_dms})** | जातक: **{name}**")

            with col_c_prashna:
                c_icon_nat = p_nat_res.get("category_icon", "🔮")
                c_hi_nat = p_nat_res.get("category_hi", nat_cat_name)
                st.markdown(f"###### 🔮 चक्र 2: तात्कालिक प्रश्न कुण्डली (Instant Prashna — {c_icon_nat} {c_hi_nat})")
                prashna_svg = render_chart_svg(p_nat_chart, f"Prashna D1 — {nat_cat_name}", varga_code="D1")
                st.markdown(f'<div style="max-width:90%;margin:0 auto;">{prashna_svg}</div>', unsafe_allow_html=True)
                st.caption(f"प्रश्न लग्न: **{p_nat_res.get('prashna_lagna', '-')}** | समय: **{p_nat_res.get('query_time', '')}**")

        with subtab_p1_synthesis:
            # Dual Synthesis Engine
            st.markdown("##### ⚖️ जन्म कुण्डली vs प्रश्न कुण्डली शास्त्रीय समन्वय (Dual Kundali Synthesis Matrix)")

            p_lagna_id_val = p_nat_chart.lagna_sign_id
            natal_lagna_id_val = chart.lagna_sign_id
            lagna_rel_house = ((p_lagna_id_val - natal_lagna_id_val) % 12) + 1

            if lagna_rel_house in [1, 4, 7, 10]:
                rel_desc = f"🌟 **केंद्र सम्बंध ({lagna_rel_house}वां भाव):** प्रश्न लग्न जातक के जन्म लग्न से केंद्र में है। यह कार्य में तात्कालिक गतिशीलता, सामाजिक प्रभाव एवं प्रत्यक्ष सफलता का प्रबल शास्त्रीय सूचक है।"
                rel_color = "#15803d"
                rel_bg = "#f0fdf4"
                rel_border = "#86efac"
            elif lagna_rel_house in [5, 9]:
                rel_desc = f"✨ **त्रिकोण सम्बंध ({lagna_rel_house}वां भाव):** प्रश्न लग्न जातक के जन्म लग्न से त्रिकोण में स्थित है। यह पूर्वपुण्य, ईश्वरीय कृपा एवं सहज सौभाग्य से कार्य सिद्ध होने का प्रमाण है।"
                rel_color = "#047857"
                rel_bg = "#ecfdf5"
                rel_border = "#6ee7b7"
            elif lagna_rel_house in [3, 11]:
                rel_desc = f"🚀 **उपचय सम्बंध ({lagna_rel_house}वां भाव):** प्रश्न लग्न जातक के जन्म लग्न से उपचय भाव में है। जातक के निरंतर पुरुषार्थ, मित्रों के सहयोग एवं पराक्रम से निश्चित सिद्धि प्राप्त होगी।"
                rel_color = "#1d4ed8"
                rel_bg = "#eff6ff"
                rel_border = "#93c5fd"
            elif lagna_rel_house in [6, 8, 12]:
                rel_desc = f"⚠️ **त्रिक सम्बंध ({lagna_rel_house}वां भाव):** प्रश्न लग्न जातक के जन्म लग्न से दुस्थान (त्रिक) भाव में है। अभीष्ट कार्य में अज्ञात रुकावटें, तनाव अथवा विलंब की संभावना है; अतिरिक्त सावधानी व शास्त्रीय उपाय अपेक्षित हैं।"
                rel_color = "#b91c1c"
                rel_bg = "#fef2f2"
                rel_border = "#fca5a5"
            else:
                rel_desc = f"⚖️ **द्वितीय भाव सम्बंध ({lagna_rel_house}वां भाव):** प्रश्न लग्न जातक के जन्म लग्न से द्वितीय भाव में है। आर्थिक व पारिवारिक संसाधनों के सदुपयोग से मध्यम गति से कार्य सिद्धि होगी।"
                rel_color = "#b45309"
                rel_bg = "#fffbeb"
                rel_border = "#fcd34d"

            col_syn1, col_syn2 = st.columns(2)
            with col_syn1:
                st.markdown(_clean_html(f"""
                <div style="background:{rel_bg};border:1px solid {rel_border};border-radius:10px;padding:14px;margin-bottom:12px;">
                    <div style="font-weight:700;color:{rel_color};font-size:14px;">1. लग्न-सम्बन्ध विश्लेषण (Lagna Inter-Relation)</div>
                    <div style="font-size:13px;color:#1e293b;margin-top:6px;line-height:1.5;">{rel_desc}</div>
                    <div style="font-size:12px;color:#64748b;margin-top:6px;">जन्म लग्न: {chart.lagna_sign_name} ➔ प्रश्न लग्न: {p_nat_res.get('prashna_lagna_sign', '')} ({lagna_rel_house}वां भाव)</div>
                </div>
                """), unsafe_allow_html=True)

                tajika_yoga_str = p_nat_res.get("tajika_yoga", "")
                st.markdown(_clean_html(f"""
                <div style="background:#f8fafc;border:1px solid #cbd5e1;border-radius:10px;padding:14px;">
                    <div style="font-weight:700;color:#0f172a;font-size:14px;">2. कार्येश एवं ताजिक सम्बंध (Karyesha & Tajika Alignment)</div>
                    <div style="font-size:13px;color:#334155;margin-top:6px;line-height:1.5;">
                        • <b>प्रश्न लग्नेश:</b> {p_nat_res.get('lagnesh', '-')}<br/>
                        • <b>अभीष्ट कार्येश:</b> {p_nat_res.get('karyesh', '-')}<br/>
                        • <b>सक्रिय ताजिक योग:</b> {tajika_yoga_str}
                    </div>
                </div>
                """), unsafe_allow_html=True)

            with col_syn2:
                moon_plc_str = p_nat_res.get("moon_placement", "-")
                expl_str = p_nat_res.get("explanation_hi", "")
                st.markdown(_clean_html(f"""
                <div style="background:#f8fafc;border:1px solid #cbd5e1;border-radius:10px;padding:14px;margin-bottom:12px;">
                    <div style="font-weight:700;color:#0f172a;font-size:14px;">3. प्रश्नकालीन चन्द्र मनःस्थिति (Querent's Mental Readiness)</div>
                    <div style="font-size:13px;color:#334155;margin-top:6px;line-height:1.5;">
                        {moon_plc_str}<br/>
                        <span style="font-size:12px;color:#64748b;">(चन्द्रमा प्रश्नकर्ता की मानसिक तत्परता एवं अनुकूल वातावरण का नियामक है।)</span>
                    </div>
                </div>
                <div style="background:#f1f5f9;border-left:4px solid #3b82f6;border-radius:4px;padding:14px;">
                    <div style="font-weight:700;color:#1e3a8a;font-size:14px;">4. शास्त्रीय निष्कर्ष एवं दिशानिर्देश (Shastriya Synthesis Verdict)</div>
                    <div style="font-size:13px;color:#1e293b;margin-top:6px;line-height:1.5;">{expl_str}</div>
                </div>
                """), unsafe_allow_html=True)

                # 5. केरलीय प्रश्नमार्ग षोडश स्फुट (16 Sensitive Horary Sphutas)
                st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)
                with st.expander("🔮 केरलीय प्रश्नमार्ग षोडश स्फुट (16 Sensitive Horary Sphutas)", expanded=False):
                    st.caption("केरलीय प्रश्न मार्ग एवं माधव दीपिका प्रतिपादित त्रिक-स्फुट, पञ्च-स्फुट, प्राण, देह, मृत्यु, बीज, क्षेत्र एवं कार्य स्फुटों का सूक्ष्म विन्यास:")
                    try:
                        calc_fn = getattr(default_prashna_service, "calculate_shodasha_sphutas", None)
                        if not calc_fn:
                            import src.jyotish.services.prashna as _p_dyn
                            _p_dyn = importlib.reload(_p_dyn)
                            calc_fn = getattr(_p_dyn.PrashnaService, "calculate_shodasha_sphutas", None) or getattr(_p_dyn.default_prashna_service, "calculate_shodasha_sphutas", None)
                        if calc_fn:
                            karyesha_p = p_nat_res.get("karyesh", "Jupiter")
                            sphutas_data = calc_fn(chart, karyesha=karyesha_p)
                            df_sphutas = pd.DataFrame(sphutas_data)
                            st.dataframe(df_sphutas, use_container_width=True, hide_index=True)
                        else:
                            st.info("षोडश स्फुट सेवा मॉड्यूल रीलोड हो रहा है, कृपया पृष्ठ रिफ्रेश करें...")
                    except Exception as _e_sph:
                        st.warning(f"षोडश स्फुट गणना उपलब्ध नहीं: {_e_sph}")

    # =========================================================================
    # TAB 2: नवीन प्रश्नकर्ता एवं तात्कालिक प्रश्न (New / Custom Querent)
    # =========================================================================
    with ptab2:
        with st.expander("✍️ नवीन प्रश्नकर्ता एवं तात्कालिक प्रश्न (New / Custom Querent Horary)", expanded=True):
            st.caption("किसी भी नए अथवा आगंतुक प्रश्नकर्ता के लिए तात्कालिक होरारी कुण्डली का स्वतंत्र निर्माण, शास्त्रीय गणना एवं निष्पक्ष निर्णय।")

            # Initialize custom querent session state if not already set
            live_now_new = get_live_local_now(tz_offset)
            if "new_prashna_date_val" not in st.session_state:
                st.session_state.new_prashna_date_val = live_now_new.date()
            if "new_prashna_time_val" not in st.session_state:
                st.session_state.new_prashna_time_val = live_now_new.time().replace(microsecond=0)
            if "new_prashna_city" not in st.session_state:
                st.session_state.new_prashna_city = default_city_name
            if "new_prashna_lat" not in st.session_state:
                st.session_state.new_prashna_lat = float(latitude)
            if "new_prashna_lon" not in st.session_state:
                st.session_state.new_prashna_lon = float(longitude)
            if "new_prashna_tz" not in st.session_state:
                st.session_state.new_prashna_tz = float(tz_offset)

            # Row 1: Name and Place lookup
            col_nq1, col_nq2 = st.columns([1.5, 2.5])
            with col_nq1:
                new_q_name = st.text_input("प्रश्नकर्ता का नाम (Questioner Name)", value="नवीन प्रश्नकर्ता", key="new_prashna_name_input")
            with col_nq2:
                new_city_input = st.text_input("स्थान / नगर (City / Place)", value=st.session_state.new_prashna_city, key="new_prashna_city_input")
                if new_city_input and new_city_input.strip() != st.session_state.new_prashna_city:
                    try:
                        geo_lookup = default_geocoding_service.resolve(new_city_input.strip())
                        if geo_lookup:
                            st.session_state.new_prashna_city = new_city_input.strip()
                            st.session_state.new_prashna_lat = float(geo_lookup.get("latitude", st.session_state.new_prashna_lat))
                            st.session_state.new_prashna_lon = float(geo_lookup.get("longitude", st.session_state.new_prashna_lon))
                            st.session_state.new_prashna_tz = float(geo_lookup.get("timezone_offset", st.session_state.new_prashna_tz))
                    except Exception:
                        pass

            def _cb_new_set_live_now():
                upd_now = get_live_local_now(st.session_state.new_prashna_tz)
                st.session_state.new_prashna_date_val = upd_now.date()
                st.session_state.new_prashna_time_val = upd_now.time().replace(microsecond=0)
                st.session_state.new_prashna_d_picker = upd_now.date()
                st.session_state.new_prashna_t_picker = upd_now.time().replace(microsecond=0)

            # Row 2: Vartaman Date, Time (with seconds), Live Now Button, GPS Button
            col_nt1, col_nt2, col_nt3, col_nt4 = st.columns([1.4, 1.4, 1.2, 1.2])
            with col_nt1:
                new_q_date = st.date_input("📅 प्रश्न तिथि (Query Date)", value=st.session_state.new_prashna_date_val, format="DD/MM/YYYY", key="new_prashna_d_picker")
                st.session_state.new_prashna_date_val = new_q_date
            with col_nt2:
                new_q_time = st.time_input("⏱️ प्रश्न समय (Time - सेकंड सहित)", value=st.session_state.new_prashna_time_val, step=1, key="new_prashna_t_picker")
                st.session_state.new_prashna_time_val = new_q_time
            with col_nt3:
                st.write("")
                st.write("")
                if st.button("⏱️ वर्तमान समय लोड करें", use_container_width=True, key="btn_new_set_live_now", help="सटीक वर्तमान सेकंड-लेवल समय लोड करें", on_click=_cb_new_set_live_now):
                    st.toast("✅ वर्तमान समय सेट किया गया!", icon="⏱️")
            with col_nt4:
                st.write("")
                st.write("")
                if st.button("🛰️ वर्तमान GPS स्थान", use_container_width=True, key="btn_new_set_gps", help="डिवाइस GPS अनुमति मांगकर सटीक वर्तमान स्थान लें"):
                    st.session_state.trigger_browser_gps = "new_prashna"
                    st.rerun()

            # Row 3: Coordinate fine-tuning
            col_c1, col_c2, col_c3 = st.columns(3)
            with col_c1:
                new_lat = st.number_input("अक्षांश (Latitude)", value=float(st.session_state.new_prashna_lat), format="%.4f", key="new_prashna_lat_num")
                st.session_state.new_prashna_lat = new_lat
            with col_c2:
                new_lon = st.number_input("देशांतर (Longitude)", value=float(st.session_state.new_prashna_lon), format="%.4f", key="new_prashna_lon_num")
                st.session_state.new_prashna_lon = new_lon
            with col_c3:
                new_tz = st.number_input("समय क्षेत्र (Timezone Offset)", value=float(st.session_state.new_prashna_tz), format="%.2f", key="new_prashna_tz_num")
                st.session_state.new_prashna_tz = new_tz

            # Row 4: Category and Query Text
            col_nqc1, col_nqc2 = st.columns([1, 2])
            with col_nqc1:
                cat_choice_new = st.selectbox(
                    "प्रश्न श्रेणी (Question Category)",
                    range(len(cat_options)),
                    format_func=lambda i: cat_options[i] if i < len(cat_options) else "",
                    index=min(6, max(0, len(cat_options) - 1)),
                    key="new_prashna_cat_idx"
                )
                new_cat_meta = PRASHNA_CATEGORIES[cat_choice_new] if cat_choice_new < len(PRASHNA_CATEGORIES) else PRASHNA_CATEGORIES[0]
                new_cat_name = new_cat_meta.get("Name", "Job")
            with col_nqc2:
                new_default_q = sample_queries.get(new_cat_name, "क्या मेरा अभीष्ट कार्य सिद्ध होगा?")
                new_query_text = st.text_input("प्रश्न विवरण दर्ज करें (Enter Question)", value=new_default_q, key="new_prashna_query_text")

            col_kp1, col_kp2 = st.columns([1, 2])
            with col_kp1:
                new_kp_seed = st.number_input("केपी होरारी संख्या (KP Seed 1-249, ऐच्छिक)", min_value=0, max_value=249, value=0, help="0 = समय आधारित लग्न; 1 से 249 = केपी सूक्ष्म उप-स्वामी बीज", key="new_prashna_kp_seed")
            with col_kp2:
                st.caption("ℹ️ यदि प्रश्नकर्ता ने 1 से 249 के बीच कोई संख्या चुनी है तो उसे दर्ज करें, अन्यथा सामान्य समय आधारित लग्न लिया जाएगा।")

            calc_new_btn = st.button("🔮 नवीन प्रश्न कुण्डली परिकलन एवं निर्णय (Calculate Horary Chart)", type="primary", use_container_width=True, key="btn_calc_new_prashna")

        new_query_dt = datetime.combine(st.session_state.new_prashna_date_val, st.session_state.new_prashna_time_val)

        need_new_recalc = (
            calc_new_btn
            or "prashna_new_res" not in st.session_state
            or not st.session_state.prashna_new_res
            or st.session_state.prashna_new_res.get("category") != new_cat_name
        )

        if need_new_recalc:
            try:
                st.session_state.prashna_new_res = default_prashna_service.generate_prashna_chart(
                    query_text=new_query_text,
                    category_name=new_cat_name,
                    latitude=new_lat,
                    longitude=new_lon,
                    timezone_offset=new_tz,
                    query_dt=new_query_dt,
                    questioner_name=new_q_name
                )
                st.session_state.active_prashna_res = st.session_state.prashna_new_res
                if calc_new_btn:
                    st.toast("✅ नवीन प्रश्न कुण्डली एवं शास्त्रीय निर्णय सफलतापूर्वक परिकलित!", icon="🔮")
            except Exception as e:
                st.error(f"नवीन प्रश्न परिकलन में त्रुटि: {e}")

        p_new_res = st.session_state.get("prashna_new_res") or st.session_state.get("prashna_native_res")
        p_new_chart: KundaliChart = p_new_res.get("chart", chart)

        # 4 Top KPI Cards
        st.markdown("---")
        nkpi1, nkpi2, nkpi3, nkpi4 = st.columns(4)
        v_text_new = str(p_new_res.get("verdict", "उत्कृष्ट")).split(" (")[0]
        v_badge_new = str(p_new_res.get("verdict_badge", "✅ शुभ"))
        t_text_new = str(p_new_res.get("timing", "1 से 3 सप्ताह")).split(" (")[0]
        v_score_new = float(p_new_res.get("verdict_score", 0.75))
        pos_c_new = p_new_res.get("active_positive_count", 0)
        neg_c_new = p_new_res.get("active_negative_count", 0)

        nkpi1.metric("🎯 शास्त्रीय निर्णय", v_text_new, v_badge_new)
        nkpi2.metric("⏳ संभावित समय", t_text_new)
        nkpi3.metric("📊 सहमति व सिद्धि स्कोर", f"{int(v_score_new * 100)}%")
        nkpi4.metric("📜 100 शास्त्रीय नियम", f"✅ {pos_c_new} शुभ | ⚠️ {neg_c_new} बाधाएं")

        # Layout: Left SVG Chart, Right Summary HUD
        st.markdown("---")
        col_nchart, col_nsum = st.columns([1, 1])
        with col_nchart:
            c_icon_new = p_new_res.get("category_icon", "🔮")
            c_hi_new = p_new_res.get("category_hi", new_cat_name)
            st.markdown(f"##### 🔮 तात्कालिक प्रश्न कुण्डली चक्र ({c_icon_new} {c_hi_new})")
            new_chart_title = f"Prashna Chart — {p_new_res.get('category', new_cat_name)}"
            svg_new = render_chart_svg(p_new_chart, new_chart_title, varga_code="D1")
            st.markdown(f'<div style="max-width:90%;margin:0 auto;">{svg_new}</div>', unsafe_allow_html=True)
            st.caption(f"📍 स्थान: {new_city_input} (Lat: {new_lat:.2f}°, Lon: {new_lon:.2f}°) | समय: {p_new_res.get('query_time', '')}")

        with col_nsum:
            st.markdown("##### 🌟 प्रश्न सारांश एवं मुख्य शास्त्रीय कारकत्व")
            sum_c1, sum_c2 = st.columns(2)
            with sum_c1:
                st.markdown(f"- **प्रश्नकर्ता:** {p_new_res.get('questioner_name', new_q_name)}")
                st.markdown(f"- **प्रश्न लग्न:** {p_new_res.get('prashna_lagna', '-')}")
                st.markdown(f"- **लग्नेश (1st Lord):** {p_new_res.get('lagnesh', '-')}")
                st.markdown(f"- **कार्य भाव:** {p_new_res.get('karya_bhava', '-')}")
            with sum_c2:
                st.markdown(f"- **प्रश्न समय:** {p_new_res.get('query_time', '-')}")
                st.markdown(f"- **कार्येश (Karyesha):** {p_new_res.get('karyesh', '-')}")
                st.markdown(f"- **चन्द्रमा स्थिति:** {p_new_res.get('moon_placement', '-')}")
                st.markdown(f"- **ताजिक योग:** {p_new_res.get('tajika_yoga', '-')}")

            st.info(f"📜 **शास्त्रीय निष्कर्ष:** {p_new_res.get('explanation_hi', '')}")
            st.markdown(f"**फलसिद्धि संभावना सूचकांक (Success Probability): {int(v_score_new * 100)}%**")
            st.progress(v_score_new)

    # Active Result reference for Tabs 3, 4, 5, 6
    cur_p_res = st.session_state.get("active_prashna_res") or st.session_state.get("prashna_native_res") or st.session_state.get("prashna_new_res")
    if not cur_p_res or not cur_p_res.get("all_rules"):
        cur_p_res = default_prashna_service.generate_prashna_chart(
            query_text="क्या मेरा अभीष्ट कार्य सिद्ध होगा?", category_name="Job", latitude=latitude, longitude=longitude, timezone_offset=tz_offset, query_dt=get_live_local_now(tz_offset), questioner_name=name
        )
        st.session_state.active_prashna_res = cur_p_res
    cur_p_chart: KundaliChart = cur_p_res.get("chart", chart)

    # =========================================================================
    # TAB 3: प्रश्नकालीन नवग्रह स्थिति तालिका एवं सामर्थ्य
    # =========================================================================
    with ptab3:
        st.markdown("#### 🪐 प्रश्नकालीन नवग्रह स्थिति तालिका एवं खगोलीय सामर्थ्य (Planetary Horary Metrics)")
        st.info(f"📍 वर्तमान सक्रिय विश्लेषण: **{cur_p_res.get('questioner_name', 'जातक')}** | श्रेणी: **{cur_p_res.get('category_icon', '🔮')} {cur_p_res.get('category_hi', cur_p_res.get('category', ''))}** | प्रश्न: *'{cur_p_res.get('query_text', '')}'*")

        # Subtabs for Tab 3: प्रश्न ग्रह स्थिति
        subtab_p3_table, subtab_p3_chart = st.tabs([
            "1. 📋 प्रश्नकालीन नवग्रह स्थिति तालिका एवं खगोलीय सामर्थ्य",
            "2. 📊 नवग्रह तात्कालिक क्रियाशीलता व सामर्थ्य आलेख"
        ])

        with subtab_p3_table:
            # Planetary Astronomical Metrics Table (Premium HTML Styling)
            card_bg_p = "#111827" if (is_night_mode or is_astrallis_mode) else "#FFFFFF"
            card_bdr_p = "rgba(255,255,255,0.12)" if (is_night_mode or is_astrallis_mode) else "#E2E8F0"
            hdr_bg_p = "#1F2937" if (is_night_mode or is_astrallis_mode) else "#F1F5F9"
            hdr_bdr_p = "#374151" if (is_night_mode or is_astrallis_mode) else "#CBD5E1"
            text_p1 = "#F8FAFC" if (is_night_mode or is_astrallis_mode) else "#0F172A"
            text_p2 = "#94A3B8" if (is_night_mode or is_astrallis_mode) else "#475569"
            row_alt_p = "#1F2937" if (is_night_mode or is_astrallis_mode) else "#FCFCFD"
            row_bg_p = "#111827" if (is_night_mode or is_astrallis_mode) else "#FFFFFF"
            row_bdr_p = "#374151" if (is_night_mode or is_astrallis_mode) else "#F1F5F9"

            tbl_pr_html = f'<div style="width: 100%; max-width: 100%; overflow-x: auto; -webkit-overflow-scrolling: touch; border: 1.5px solid {card_bdr_p}; border-radius: 10px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); margin-top: 6px; margin-bottom: 16px;">'
            tbl_pr_html += f'<table style="width: 100%; border-collapse: collapse; text-align: left; background: {card_bg_p}; font-size: 12px; table-layout: auto;">'
            tbl_pr_html += f'<thead><tr style="background: {hdr_bg_p}; border-bottom: 2px solid {hdr_bdr_p};">'
            tbl_pr_html += f'<th style="padding: 9px 12px; font-weight: 800; color: {text_p1};">ग्रह (Graha)</th>'
            tbl_pr_html += f'<th style="padding: 9px 10px; font-weight: 800; color: {text_p1};">स्वभाव</th>'
            tbl_pr_html += f'<th style="padding: 9px 10px; font-weight: 800; color: {text_p1};">राशि व स्वामी</th>'
            tbl_pr_html += f'<th style="padding: 9px 10px; font-weight: 800; color: {text_p1};">भाव</th>'
            tbl_pr_html += f'<th style="padding: 9px 10px; font-weight: 800; color: {text_p1};">अंश-कला (DMS)</th>'
            tbl_pr_html += f'<th style="padding: 9px 10px; font-weight: 800; color: {text_p1};">नक्षत्र व चरण</th>'
            tbl_pr_html += f'<th style="padding: 9px 10px; font-weight: 800; color: {text_p1}; text-align: center;">गति व अवस्था</th>'
            tbl_pr_html += f'<th style="padding: 9px 10px; font-weight: 800; color: {text_p1}; text-align: center;">गरिमा (Dignity)</th>'
            tbl_pr_html += f'<th style="padding: 9px 10px; font-weight: 800; color: {text_p1}; text-align: center;">दीप्तांश (Orb)</th>'
            tbl_pr_html += '</tr></thead><tbody>'

            for idx, g_row in enumerate(cur_p_res.get("graha_table", [])):
                g_name = g_row.get("graha", "")
                dignity_label, _, _ = get_varga_dignity_info(g_name, g_row.get("sign", ""), affliction_engine)
                deeptamsha_val = PRASHNA_DEEPTAMSHA.get(g_name, 10.0)
                p_obj = cur_p_chart.planets.get(g_name)
                is_comb = bool(p_obj and getattr(p_obj, "is_combust", False))

                dms_val = g_row.get("dms_str")
                if not dms_val and p_obj:
                    deg_val = getattr(p_obj, "sign_degree", 0.0)
                    ansh = int(deg_val)
                    kala = int(round((deg_val - ansh) * 60.0))
                    if kala >= 60:
                        kala = 0
                        ansh += 1
                    dms_val = f"{ansh}° {kala:02d}'"
                elif not dms_val:
                    dms_val = g_row.get("degree", "—")

                swabhav_val = g_row.get("swabhav")
                if not swabhav_val:
                    swabhav_val = "नैसर्गिक शुभ" if g_name in ["Jupiter", "Venus", "Mercury", "Moon"] else "नैसर्गिक क्रूर"

                nak_val = g_row.get("nakshatra", "—")
                if g_row.get("nakshatra_name") and g_row.get("nakshatra_pada"):
                    nak_val = f"{g_row.get('nakshatra_name')} (च. {g_row.get('nakshatra_pada')})"

                # Dignity Badge styling
                if "उच्च" in dignity_label:
                    dig_badge = '<span style="background:#DBEAFE;color:#1E40AF;padding:3px 7px;border-radius:4px;font-weight:700;">🌟 उच्च</span>'
                elif "मूल" in dignity_label:
                    dig_badge = '<span style="background:#CCFBF1;color:#0F766E;padding:3px 7px;border-radius:4px;font-weight:700;">👑 मूलत्रिकोण</span>'
                elif "स्व" in dignity_label:
                    dig_badge = '<span style="background:#DCFCE7;color:#166534;padding:3px 7px;border-radius:4px;font-weight:700;">🏠 स्वगृही</span>'
                elif "नीच" in dignity_label:
                    dig_badge = '<span style="background:#FEE2E2;color:#991B1B;padding:3px 7px;border-radius:4px;font-weight:700;">🔻 नीच</span>'
                elif "मित्र" in dignity_label:
                    dig_badge = '<span style="background:#F0FDF4;color:#15803D;padding:3px 7px;border-radius:4px;font-weight:600;">🤝 मित्र</span>'
                elif "शत्रु" in dignity_label:
                    dig_badge = '<span style="background:#FFF7ED;color:#C2410C;padding:3px 7px;border-radius:4px;font-weight:600;">⚔️ शत्रु</span>'
                else:
                    dig_badge = f'<span style="background:#F1F5F9;color:#475569;padding:3px 7px;border-radius:4px;">{dignity_label}</span>'

                motion_str = g_row.get("motion", "मार्गी")
                if is_comb:
                    motion_str += " <span style='color:#EF4444;font-weight:700;'>[अस्त]</span>"

                bg_row = row_alt_p if idx % 2 == 1 else row_bg_p
                tbl_pr_html += f'<tr style="background-color: {bg_row}; border-bottom: 1px solid {row_bdr_p};">'
                tbl_pr_html += f'<td style="padding: 8px 12px; font-weight: 700; color: {text_p1}; white-space: nowrap;">{g_name}</td>'
                tbl_pr_html += f'<td style="padding: 8px 10px; color: {text_p2};">{swabhav_val}</td>'
                tbl_pr_html += f'<td style="padding: 8px 10px; color: {text_p1};"><b>{g_row.get("sign", "")}</b> <span style="font-size:11px;color:{text_p2};">({g_row.get("lord", "")})</span></td>'
                tbl_pr_html += f'<td style="padding: 8px 10px; color: {text_p1}; font-weight:600;">{g_row.get("house", "")}</td>'
                tbl_pr_html += f'<td style="padding: 8px 10px; color: {text_p1}; font-family:monospace;">{dms_val}</td>'
                tbl_pr_html += f'<td style="padding: 8px 10px; color: {text_p2};">{nak_val}</td>'
                tbl_pr_html += f'<td style="padding: 8px 10px; text-align: center; color: {text_p1};">{motion_str}</td>'
                tbl_pr_html += f'<td style="padding: 8px 10px; text-align: center;">{dig_badge}</td>'
                tbl_pr_html += f'<td style="padding: 8px 10px; text-align: center; color: {text_p1}; font-weight:700;">{deeptamsha_val:.1f}°</td>'
                tbl_pr_html += '</tr>'

            tbl_pr_html += '</tbody></table></div>'
            st.markdown(_clean_html(tbl_pr_html), unsafe_allow_html=True)

            # Lagna Spashta & Bhava Sandhi Card
            st.markdown("##### 📐 प्रश्न लग्न स्पष्ट एवं भाव संधि सारांश (Lagna & Cuspal Summary)")
            l_col1, l_col2, l_col3 = st.columns(3)
            l_col1.markdown(f"- **प्रश्न लग्न स्पष्ट:** {cur_p_res.get('prashna_lagna', '-')}")
            l_col1.markdown(f"- **लग्नेश:** {cur_p_res.get('lagnesh', '-')}")
            l_col2.markdown(f"- **उदित राशि तत्व:** {cur_p_res.get('prashna_lagna_sign', '-')}")
            l_col2.markdown(f"- **कार्येश:** {cur_p_res.get('karyesh', '-')}")
            l_col3.markdown(f"- **अयनांश:** {cur_p_chart.ayanamsa_name} ({cur_p_chart.ayanamsa_value:.4f}°)")
            l_col3.markdown(f"- **प्रश्न काल समय:** {cur_p_res.get('query_time', '-')}")

            # 16 Shodasha Sphutas (Kerala Prashna Marga)
            with st.expander("🔮 केरलीय प्रश्नमार्ग षोडश स्फुट (16 Sensitive Horary Sphutas)", expanded=False):
                st.caption("केरलीय प्रश्न मार्ग एवं माधव दीपिका प्रतिपादित त्रिक-स्फुट, पञ्च-स्फुट, प्राण, देह, मृत्यु, बीज, क्षेत्र एवं कार्य स्फुटों का सूक्ष्म विन्यास:")
                try:
                    calc_fn = getattr(default_prashna_service, "calculate_shodasha_sphutas", None)
                    if not calc_fn:
                        import src.jyotish.services.prashna as _p_dyn
                        _p_dyn = importlib.reload(_p_dyn)
                        calc_fn = getattr(_p_dyn.PrashnaService, "calculate_shodasha_sphutas", None) or getattr(_p_dyn.default_prashna_service, "calculate_shodasha_sphutas", None)
                    if calc_fn:
                        kary_name = cur_p_res.get("karyesh", "Jupiter")
                        s_sphutas = calc_fn(cur_p_chart, karyesha=kary_name)
                        df_sphutas = pd.DataFrame(s_sphutas)
                        st.dataframe(df_sphutas, use_container_width=True, hide_index=True)
                    else:
                        st.info("षोडश स्फुट सेवा मॉड्यूल रीलोड हो रहा है, कृपया पृष्ठ रिफ्रेश करें...")
                except Exception as _e_sph:
                    st.warning(f"षोडश स्फुट गणना उपलब्ध नहीं: {_e_sph}")

        with subtab_p3_chart:
            st.markdown("##### 📊 नवग्रह तात्कालिक क्रियाशीलता व सामर्थ्य आलेख (Graha Horary Strength Chart)")
            svg_graha_bala = _render_prashna_graha_bala_svg(cur_p_res.get("graha_table", []), is_dark=is_night_mode or is_astrallis_mode)
            st.markdown(svg_graha_bala, unsafe_allow_html=True)
            st.caption("यह आलेख प्रश्न कुंडली में नवग्रहों के केंद्र, त्रिकोण, उपचय एवं उच्च/स्वक्षेत्रीय बल के आधार पर तात्कालिक क्रियाशीलता (Horary Operational Strength) को प्रदर्शित करता है।")

    # =========================================================================
    # TAB 4: द्वादश भाव भूमिका एवं प्रभाव
    # =========================================================================
    with ptab4:
        st.markdown("#### 🎭 द्वादश भाव भूमिका, कार्येश एवं प्रभाव (12 Houses Role & Functional Matrix)")
        st.info(f"📍 वर्तमान सक्रिय विश्लेषण: **{cur_p_res.get('questioner_name', 'जातक')}** — प्रश्न: *'{cur_p_res.get('query_text', '')}'*")

        # Category Triad Focus
        k_house_num = cur_p_res.get("karya_house_num", 10)
        st.markdown("##### 🎯 प्रश्न सम्बंधी मुख्य त्रि-भाव धुरी (The Primary Horary Triad)")
        triad1, triad2, triad3 = st.columns(3)

        triad1.markdown(_clean_html("""
        <div style="background:#eff6ff;border:1px solid #bfdbfe;border-radius:10px;padding:12px;">
            <div style="font-weight:700;color:#1d4ed8;font-size:13px;">🫵 प्रथम भाव (1st House — प्रश्नकर्ता)</div>
            <div style="font-size:12px;color:#1e293b;margin-top:4px;">प्रश्नकर्ता की शारीरिक व मानसिक स्थिति, संकल्प शक्ति एवं प्रश्न का मूल कारण।</div>
        </div>
        """), unsafe_allow_html=True)

        triad2.markdown(_clean_html(f"""
        <div style="background:#fef3c7;border:1px solid #fde68a;border-radius:10px;padding:12px;">
            <div style="font-weight:700;color:#b45309;font-size:13px;">🌟 {k_house_num}वां भाव (Karya House — अभीष्ट कार्य)</div>
            <div style="font-size:12px;color:#1e293b;margin-top:4px;">श्रेणी '{cur_p_res.get('category_hi', cur_p_res.get('category', ''))}' का प्रत्यक्ष कार्य भाव एवं फलसिद्धि का आधार।</div>
        </div>
        """), unsafe_allow_html=True)

        triad3.markdown(_clean_html("""
        <div style="background:#f0fdf4;border:1px solid #bbf7d0;border-radius:10px;padding:12px;">
            <div style="font-weight:700;color:#15803d;font-size:13px;">🏆 एकादश भाव (11th House — लाभ व सिद्धि)</div>
            <div style="font-size:12px;color:#1e293b;margin-top:4px;">मनोरथ सिद्धि, अभीष्ट लाभ एवं समस्त प्रयत्नों की अंतिम सफलता का नियामक।</div>
        </div>
        """), unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("##### 📜 संपूर्ण द्वादश भाव भूमिका एवं ग्रह स्थिति तालिका")
        house_matrix = []
        for hr in cur_p_res.get("house_roles", []):
            h_num = hr.get("house", 1)
            h_sign = hr.get("sign", "")
            h_lord = hr.get("lord", "")
            h_icon = hr.get("icon", "📍")
            h_text = hr.get("text", "")
            h_imp = hr.get("is_important", False)
            h_occ = hr.get("occupants", [])

            # Find aspects on this house from cur_p_chart
            h_aspects = []
            if h_num <= len(cur_p_chart.houses):
                h_aspects = cur_p_chart.houses[h_num - 1].aspecting_planets or []

            status_tag = "🌟 मुख्य कार्य भाव" if h_num == k_house_num else ("🫵 प्रश्नकर्ता" if h_num == 1 else ("🎯 लाभ/सिद्धि भाव" if h_num == 11 else ("⭐ महत्वपूर्ण" if h_imp else "सामान्य")))

            house_matrix.append({
                "भाव (House)": f"{h_num} ({h_sign})",
                "भावेश (Lord)": h_lord,
                "प्रश्न में भूमिका (Role)": f"{h_icon} {h_text}",
                "महत्व (Status)": status_tag,
                "भावस्थ ग्रह (Occupants)": ", ".join(h_occ) if h_occ else "—",
                "दृष्टि डालने वाले ग्रह (Aspects)": ", ".join(h_aspects) if h_aspects else "—"
            })

        st.dataframe(pd.DataFrame(house_matrix), use_container_width=True, hide_index=True)

    # =========================================================================
    # TAB 5: ताजिक एवं प्रश्न मार्ग सिद्धांत
    # =========================================================================
    with ptab5:
        st.markdown("#### 📖 ताजिक नीलकण्ठी एवं प्रश्न मार्ग के प्रामाणिक सिद्धांत")
        st.write("होरारी फलकथन के मूल स्तंभ: 16 ताजिक योग, ग्रहों के दीप्तांश, केरल प्रश्न मार्ग पद्धतियां एवं सटीक काल निर्धारण सूत्र।")

        taj_shl = SHASTRIYA_SHLOKAS.get("tajika_prashna", {})
        if taj_shl:
            taj_lines = "<br/>".join(taj_shl['shloka'].splitlines())
            st.markdown(f"""
    <div style="background: rgba(147, 51, 234, 0.08); border-left: 4px solid #9333EA; padding: 14px 18px; border-radius: 8px; margin: 10px 0 16px 0;">
    <div style="font-weight: 700; color: #7E22CE; font-size: 13.5px; margin-bottom: 4px;">📖 {taj_shl['grantha']}</div>
    <div style="font-family: 'Devanagari Sangam MN', serif; font-size: 14px; font-weight: 600; line-height: 1.6; color: #0F172A;">
        {taj_lines}
    </div>
    <div style="margin-top: 6px; font-size: 12.5px; color: #334155; line-height: 1.5;">
        <b>हिंदी भावार्थ:</b> {taj_shl['anuvad_hi']}
    </div>
    <div style="margin-top: 4px; font-size: 11.5px; color: #64748B;">
        <b>शास्त्रीय नियम:</b> {taj_shl['rule']}
    </div>
    </div>
    """, unsafe_allow_html=True)

        t_sub1, t_sub2, t_sub3, t_sub4 = st.tabs([
            "1. 🔯 16 ताजिक योग संदर्भ",
            "2. 📐 दीप्तांश एवं दृष्टि सिद्धांत",
            "3. 🌿 केरल प्रश्न मार्ग गूढ़ रहस्य",
            "4. ⏳ काल निर्धारण शास्त्रीय सूत्र"
        ])

        with t_sub1:
            st.markdown("##### 🔯 16 ताजिक योगों की प्रामाणिक संदर्भ तालिका (The 16 Classical Tajika Yogas)")
            tajika_yogas_list = [
                {"योग": "1. इत्थशाल (Ithasala / Muthasila)", "परिभाषा": "तीव्र गति का ग्रह कम अंश पर मंद ग्रह की ओर दीप्तांश के भीतर अग्रसर हो।", "फल": "✅ कार्य की निश्चित व त्वरित सिद्धि।"},
                {"योग": "2. ईशराफ / मुसरिफ़ (Esharpha / Musrif)", "परिभाषा": "तीव्र ग्रह मंद ग्रह के अंशों को पार कर 1° या अधिक आगे निकल जाए।", "फल": "⚠️ अवसर हाथ से निकल जाना, विलंब या विफलता।"},
                {"योग": "3. नक्त (Nakta Yoga)", "परिभाषा": "लग्नेश व कार्येश में दृष्टि न हो, परंतु मध्यवर्ती तीव्र ग्रह दोनों से इत्थशाल करे।", "फल": "🤝 किसी तीसरे व्यक्ति या मध्यस्थ की सहायता से कार्य सिद्धि।"},
                {"योग": "4. यमया (Yamaya Yoga)", "परिभाषा": "धीमी गति का ग्रह दोनों कार्येश-लग्नेश के बीच संबंध स्थापित करे।", "फल": "👑 किसी वरिष्ठ अधिकारी या मार्गदर्शक के हस्तक्षेप से सफलता।"},
                {"योग": "5. मणऊ (Manau Yoga)", "परिभाषा": "इत्थशाल होने पर भी पापी ग्रह (शनि/मंगल) दृष्टि डालकर विघ्न उत्पन्न करे।", "फल": "⚔️ विरोधियों या अप्रत्याशित कारणों से कार्य में बाधा।"},
                {"योग": "6. कम्बूल (Kamboola Yoga)", "परिभाषा": "लग्नेश और कार्येश के इत्थशाल में चन्द्रमा भी सम्मिलित होकर शुभ संबंध बनाए।", "फल": "🌟 अति प्रबल एवं निर्विघ्न कार्य सिद्धि; अत्यधिक शुभ।"},
                {"योग": "7. गैर-कम्बूल (Gairi-Kamboola)", "परिभाषा": "कम्बूल योग में चन्द्रमा नीच या शत्रु राशि में हो अथवा पीड़ित हो।", "फल": "⚖️ अत्यधिक परिश्रम के उपरांत अल्प या विलंबित फल।"},
                {"योग": "8. खल्लासर (Khallasar Yoga)", "परिभाषा": "चन्द्रमा किसी भी ग्रह से दृष्टि संबंध न बनाकर शून्य अंश में हो।", "फल": "🌫️ अनिश्चितता, प्रयास व्यर्थ जाने की आशंका।"},
                {"योग": "9. रद्दा (Radda Yoga)", "परिभाषा": "इत्थशाल करने वाला ग्रह वक्री या अस्त हो जाए।", "फल": "🔄 अंतिम क्षणों में योजना भंग होना या उलटा परिणाम।"},
                {"योग": "10. दुफालि-कुत्थ (Dupphali-Kuttha)", "परिभाषा": "दोनों ग्रह अपनी उच्च या स्वराशि में होकर परस्पर दृष्टि रखें।", "फल": "💎 राजसी सम्मान, उच्च लाभ एवं स्थाई सफलता।"},
                {"योग": "11. दुत्थोत्थ-दिबीर (Dutthotha-Dibir)", "परिभाषा": "एक ग्रह बलवान और दूसरा निर्बल होकर दृष्टि संबंध बनाए।", "फल": "⚡ आंशिक सफलता, एक पक्ष की ओर से ढिलाई।"},
                {"योग": "12. तम्बिर (Tambir Yoga)", "परिभाषा": "ग्रह राशि के अंतिम अंश (29°-30°) पर होकर अगली राशि की ओर अग्रसर हो।", "फल": "⏳ परिवर्तन के पश्चात ही कार्य संपन्न होगा।"},
                {"योग": "13. कुत्थ (Kuttha Yoga)", "परिभाषा": "केंद्र भाव में स्थित ग्रह दूसरे भाव के ग्रह को पूर्ण बल प्रदान करे।", "फल": "🛡️ संस्थागत समर्थन से कार्य की पूर्ति।"},
                {"योग": "14. दुरुफ (Durupha Yoga)", "परिभाषा": "दोनों मुख्य ग्रह 6, 8 या 12वें भाव में कमजोर अवस्था में हों।", "फल": "❌ पराजय, वित्तीय हानि या प्रयास में निराशा।"},
                {"योग": "15. सुदर्शन (Sudarshana Yoga)", "परिभाषा": "शुभ ग्रहों की त्रिकोण व केंद्र में पूर्ण दृष्टि विद्यमान हो।", "फल": "🌈 चौतरफा अनुकूलता एवं प्रतिष्ठा में वृद्धि।"},
                {"योग": "16. हद्द (Hadda / Term Yoga)", "परिभाषा": "ग्रह अपने ही शास्त्रीय हद्द (शब्दांश/दीप्तांश) में स्थित हो।", "फल": "✨ स्वप्रयास एवं व्यक्तिगत कौशल से सफलता।"}
            ]
            st.dataframe(pd.DataFrame(tajika_yogas_list), use_container_width=True, hide_index=True)

        with t_sub2:
            st.markdown("##### 📐 ग्रहों के शास्त्रीय दीप्तांश (Deeptamsha Orbs) एवं दृष्टि सिद्धांत")
            st.markdown("""
            ताजिक नीलकण्ठी के अनुसार, प्रत्येक ग्रह का एक निश्चित **दीप्तांश प्रभाव मंडल (Orb of Influence)** होता है। जब दो ग्रह एक-दूसरे की दृष्टि में आकर अपने दीप्तांशों के योग के आधे भाग के भीतर होते हैं, तभी पूर्ण योग बनता है:
            """)
            col_d1, col_d2 = st.columns(2)
            with col_d1:
                deeptamsha_table = [
                    {"ग्रह (Planet)": "सूर्य (Sun)", "दीप्तांश (Orb)": "15°", "महत्व": "आत्मा, राज्य, पिता व अधिकार"},
                    {"ग्रह (Planet)": "चन्द्र (Moon)", "दीप्तांश (Orb)": "12°", "महत्व": "मन, जनसाधारण व कार्य गति"},
                    {"ग्रह (Planet)": "मंगल (Mars)", "दीप्तांश (Orb)": "8°", "महत्व": "साहस, भूमि व पराक्रम"},
                    {"ग्रह (Planet)": "बुध (Mercury)", "दीप्तांश (Orb)": "7°", "महत्व": "बुद्धि, व्यापार व दस्तावेज"}
                ]
                st.dataframe(pd.DataFrame(deeptamsha_table), use_container_width=True, hide_index=True)
            with col_d2:
                deeptamsha_table2 = [
                    {"ग्रह (Planet)": "गुरु (Jupiter)", "दीप्तांश (Orb)": "9°", "महत्व": "ज्ञान, वित्त, संतान व दैवीय कृपा"},
                    {"ग्रह (Planet)": "शुक्र (Venus)", "दीप्तांश (Orb)": "7°", "महत्व": "विवाह, वाहन, कला व सुख"},
                    {"ग्रह (Planet)": "शनि (Saturn)", "दीप्तांश (Orb)": "9°", "महत्व": "कर्म, विलंब, श्रम व स्थायित्व"},
                    {"ग्रह (Planet)": "राहु/केतु (Nodes)", "दीप्तांश (Orb)": "5°", "महत्व": "आकस्मिकता, भ्रम व शोध"}
                ]
                st.dataframe(pd.DataFrame(deeptamsha_table2), use_container_width=True, hide_index=True)

        with t_sub3:
            st.markdown("##### 🌿 केरल प्रश्न मार्ग के गूढ़ सिद्धांत (Kerala Prashna Marga Fundamentals)")
            st.markdown("""
            **1. आरूढ़ लग्न एवं छत्र लग्न (Arudha & Chhatra Lagna):**
            - प्रश्नकर्ता जब ज्योतिषी के सम्मुख आकर बैठता है, तो उसके बैठने की दिशा, स्वर्ण स्पर्श अथवा चुने गए अंक से **आरूढ़ लग्न** का निर्धारण होता है।
            - यदि प्रश्न लग्न और आरूढ़ लग्न दोनों शुभ ग्रहों से युक्त या दृष्ट हों, तो कार्य सिद्धि 100% सुनिश्चित मानी जाती है।

            **2. अष्टमंगल प्रश्न विधान (Ashtamangala Prashna):**
            - 108 कौड़ियों के त्रिविध विभाजन द्वारा निकाले गए अवशेष से ग्रह दोष, कुलदेवता की प्रसन्नता एवं छिपे हुए कारणों का सटीक पता लगाया जाता है।

            **3. दूत लक्षण एवं निमित्त शास्त्र (Omens & Duta Lakshana):**
            - प्रश्नकर्ता का आगमन समय, उसके हाथ की मुद्रा, वस्त्र का रंग, श्वास का स्वर (सूर्य स्वर या चन्द्र स्वर) प्रश्न के फल को तत्काल इंगित करते हैं।
            """)

        with t_sub4:
            st.markdown("##### ⏳ काल निर्धारण के शास्त्रीय सूत्र (Classical Timing of Events)")
            st.markdown("""
            प्रश्न कुण्डली में कार्य संपन्न होने का समय निर्धारित करने हेतु तीन प्रमुख शास्त्रीय विधियाँ उपयोग की जाती हैं:

            **1. लग्न राशि की प्रकृति अनुसार:**
            - **चर राशि (Movable - मेष, कर्क, तुला, मकर):** कार्य बहुत शीघ्र (घंटों से दिनों में) संपन्न होता है।
            - **द्विस्वभाव राशि (Dual - मिथुन, कन्या, धनु, मीन):** कार्य मध्यम गति (सप्ताहों से कुछ महीनों) में सिद्ध होता है।
            - **स्थिर राशि (Fixed - वृषभ, सिंह, वृश्चिक, कुंभ):** कार्य में भारी विलंब (मासों से वर्षों) होता है अथवा स्थिति यथावत रहती है।

            **2. लग्नेश एवं कार्येश के अंशों का अंतर (Orb Difference Formula):**
            - यदि तीव्र ग्रह और मंद ग्रह के बीच 3° का अंतर है और दोनों चर राशि में हैं ➔ **3 दिन** में फल।
            - यदि द्विस्वभाव राशि में हैं ➔ **3 सप्ताह / 3 मास** में फल।
            - यदि स्थिर राशि में हैं ➔ **3 मास / 3 वर्ष** में फल।
            """)

    # =========================================================================
    # TAB 6: 100 शास्त्रीय प्रश्न नियम एवं प्रमाण संदर्भ
    # =========================================================================
    with ptab6:
        st.markdown("#### 📜 100 शास्त्रीय प्रश्न नियम एवं प्रमाण संदर्भ (100 Classical Rules Engine)")
        st.caption("प्रश्न मार्ग, ताजिक नीलकण्ठी, षट्पंचाशिका, दैवज्ञ वल्लभ एवं केपी होरारी के 100 शास्त्रीय नियमों का स्वचालित मूल्यांकन।")

        r_pos_c = cur_p_res.get("active_positive_count", 0)
        r_neg_c = cur_p_res.get("active_negative_count", 0)
        r_pos_pts = cur_p_res.get("total_positive_points", 0)
        r_neg_pts = cur_p_res.get("total_negative_points", 0)
        r_net_bal = cur_p_res.get("net_balance_score", 0)

        # 3 Top KPI Cards
        rkpi1, rkpi2, rkpi3 = st.columns(3)
        rkpi1.markdown(_clean_html(f"""
        <div style="background:#f0fdf4;border:2px solid #86efac;border-radius:10px;padding:12px;text-align:center;">
            <div style="font-size:13px;color:#166534;font-weight:700;">🟢 सक्रिय शुभ नियम (Active Positive Rules)</div>
            <div style="font-size:22px;font-weight:900;color:#15803d;margin-top:4px;">{r_pos_c} नियम (+{r_pos_pts} अंक)</div>
        </div>
        """), unsafe_allow_html=True)

        rkpi2.markdown(_clean_html(f"""
        <div style="background:#fef2f2;border:2px solid #fecaca;border-radius:10px;padding:12px;text-align:center;">
            <div style="font-size:13px;color:#991b1b;font-weight:700;">🔴 सक्रिय अशुभ बाधाएं (Active Obstacles)</div>
            <div style="font-size:22px;font-weight:900;color:#dc2626;margin-top:4px;">{r_neg_c} नियम (-{r_neg_pts} अंक)</div>
        </div>
        """), unsafe_allow_html=True)

        bal_color = "#15803d" if r_net_bal > 0 else ("#dc2626" if r_net_bal < 0 else "#b45309")
        bal_bg = "#f0fdf4" if r_net_bal > 0 else ("#fef2f2" if r_net_bal < 0 else "#fffbeb")
        bal_border = "#86efac" if r_net_bal > 0 else ("#fecaca" if r_net_bal < 0 else "#fde68a")
        rkpi3.markdown(_clean_html(f"""
        <div style="background:{bal_bg};border:2px solid {bal_border};border-radius:10px;padding:12px;text-align:center;">
            <div style="font-size:13px;color:{bal_color};font-weight:700;">⚖️ शुद्ध शास्त्रीय संतुलन अंक (Net Balance)</div>
            <div style="font-size:22px;font-weight:900;color:{bal_color};margin-top:4px;">{r_net_bal:+d} अंक</div>
        </div>
        """), unsafe_allow_html=True)

        st.markdown("---")
        # 3 Sub-tabs for the 100 Rules
        rsub1, rsub2, rsub3 = st.tabs([
            "🟢 सक्रिय शुभ नियम तालिका",
            "🔴 सक्रिय अशुभ बाधा तालिका",
            "📚 संपूर्ण 100 शास्त्रीय नियम संदर्भ (Full Dossier)"
        ])

        with rsub1:
            st.markdown("##### 🟢 सक्रिय शुभ नियम (Active Positive Indicators)")
            active_pos_list = cur_p_res.get("positive_rules", [])
            if active_pos_list:
                pos_df = []
                for r in active_pos_list:
                    pos_df.append({
                        "नियम ID": r.get("rule_id"),
                        "क्षेत्र / विषय": r.get("domain"),
                        "शास्त्रीय नियम नाम": r.get("name_hi"),
                        "मूल ग्रंथ संदर्भ (Source)": r.get("source"),
                        "शुभ अंक": f"+{abs(r.get('weight', 0))}",
                        "शास्त्रीय विवरण व प्रमाण": r.get("description_hi")
                    })
                st.dataframe(pd.DataFrame(pos_df), use_container_width=True, hide_index=True)
            else:
                st.info("वर्तमान प्रश्न में कोई विशिष्ट शुभ नियम सक्रिय नहीं है।")

        with rsub2:
            st.markdown("##### 🔴 सक्रिय अशुभ बाधाएं (Active Negative Obstacles)")
            active_neg_list = cur_p_res.get("negative_rules", [])
            if active_neg_list:
                neg_df = []
                for r in active_neg_list:
                    neg_df.append({
                        "नियम ID": r.get("rule_id"),
                        "क्षेत्र / विषय": r.get("domain"),
                        "शास्त्रीय नियम नाम": r.get("name_hi"),
                        "मूल ग्रंथ संदर्भ (Source)": r.get("source"),
                        "बाधा अंक": f"-{abs(r.get('weight', 0))}",
                        "शास्त्रीय विवरण व प्रमाण": r.get("description_hi")
                    })
                st.dataframe(pd.DataFrame(neg_df), use_container_width=True, hide_index=True)
            else:
                st.success("अत्यंत शुभ! वर्तमान प्रश्न में कोई भी गंभीर शास्त्रीय बाधा सक्रिय नहीं है।")

        with rsub3:
            st.markdown("##### 📚 संपूर्ण 100 शास्त्रीय प्रश्न नियमों की संदर्भ संचिका")
            all_r_list = cur_p_res.get("all_rules", [])

            col_rf1, col_rf2, col_rf3 = st.columns([1, 1, 2])
            with col_rf1:
                st_flt = st.selectbox(
                    "स्थिति फ़िल्टर",
                    ["समस्त नियम (All 100)", "केवल सक्रिय शुभ (Active +)", "केवल सक्रिय अशुभ (Active -)", "केवल निष्क्रिय (Inactive)"],
                    key="p100_st_filter"
                )
            with col_rf2:
                dom_options = ["समस्त ग्रंथ / क्षेत्र (All Domains)"] + sorted(list(set(r.get("domain", "") for r in all_r_list if r.get("domain"))))
                dom_flt = st.selectbox("क्षेत्र फ़िल्टर", dom_options, key="p100_dom_filter")
            with col_rf3:
                srch_txt = st.text_input("नियम खोजें (ID, नाम, ग्रंथ, कीवर्ड)", "", key="p100_srch")

            filtered_100 = []
            for ar in all_r_list:
                is_trig = ar.get("triggered", False)
                tp = ar.get("type", "")

                if st_flt.startswith("केवल सक्रिय शुभ") and not (is_trig and tp == "POSITIVE"):
                    continue
                if st_flt.startswith("केवल सक्रिय अशुभ") and not (is_trig and tp == "NEGATIVE"):
                    continue
                if st_flt.startswith("केवल निष्क्रिय") and is_trig:
                    continue

                if dom_flt != "समस्त ग्रंथ / क्षेत्र (All Domains)" and ar.get("domain") != dom_flt:
                    continue

                if srch_txt and srch_txt.strip():
                    sterm = srch_txt.strip().lower()
                    m = (
                        sterm in str(ar.get("rule_id", "")).lower()
                        or sterm in str(ar.get("name_hi", "")).lower()
                        or sterm in str(ar.get("source", "")).lower()
                        or sterm in str(ar.get("domain", "")).lower()
                        or sterm in str(ar.get("description_hi", "")).lower()
                    )
                    if not m:
                        continue

                filtered_100.append({
                    "ID": ar.get("rule_id"),
                    "क्षेत्र": ar.get("domain"),
                    "शास्त्रीय नियम नाम": ar.get("name_hi"),
                    "मूल ग्रंथ (Source)": ar.get("source"),
                    "प्रकार": "🟢 शुभ (+)" if tp == "POSITIVE" else "🔴 अशुभ (-)",
                    "प्रभाव अंक": f"+{abs(ar.get('weight', 0))}" if tp == "POSITIVE" else f"-{abs(ar.get('weight', 0))}",
                    "सक्रियता स्थिति": "🌟 सक्रिय (Active)" if is_trig else "⚪ निष्क्रिय",
                    "शास्त्रीय विवरण व प्रमाण": ar.get("description_hi")
                })

            st.caption(f"प्रदर्शित नियम: **{len(filtered_100)} / 100**")
            st.dataframe(pd.DataFrame(filtered_100), use_container_width=True, hide_index=True)

    # ─── Bottom Information & Shastriya Pramana (Collapsible Expanders) ───
    st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)
    with st.expander("🔮 जन्म लग्न, तात्कालिक प्रश्न लग्न व शास्त्रीय निर्णय सारांश (Prashna Key Metrics)", expanded=False):
        c_pn1, c_pn2, c_pn3, c_pn4 = st.columns(4)
        c_pn1.metric("जन्म लग्न एवं चन्द्र", f"{lagna_sname} {l_dms}", f"🌙 {moon_str}")
        c_pn2.metric("तात्कालिक प्रश्न लग्न", f"{p_lagna_str}", f"लग्नेश: {p_lagnesh_str}")
        c_pn3.metric("कार्येश एवं ताजिक योग", f"{p_karyesh_str}", f"योग: {p_yoga_str}")
        c_pn4.metric("तात्कालिक शास्त्रीय निर्णय", f"{p_verdict_str}", f"सिद्धि स्कोर: {int(cur_p_init.get('verdict_score', 0.75) * 100)}%")

    prashna_marga_shloka = {
        "title": "प्रश्नमार्ग एवं ताजिक नीलकण्ठी — होरारी प्रश्न रहस्य एवं कार्य सिद्धि विचार",
        "source": "केरलीय 'प्रश्नमार्ग' (अध्याय २, श्लोक १) एवं 'ताजिक नीलकण्ठी' (प्रश्न तंत्र)",
        "shloka": "यदुपचितमन्यजन्मनि शुभाशुभं तस्य कर्मणः पुंसाम्।\nव्यञ्जयति शास्त्रमेतत् तमसि द्रव्याणि दीप इव॥\nलग्नेशकार्येशसुदृष्टियोगे सौम्येक्षिते वा बलसंयुते च।\nकार्यस्य सिद्धिं प्रवदन्ति सन्तो हीने विलोमं मुनयो वदन्ति॥",
        "meaning": "पूर्वजन्मों में उपार्जित मनुष्य के शुभाशुभ कर्मफल को यह प्रश्न शास्त्र उसी प्रकार प्रत्यक्ष कर देता है जैसे घोर अन्धकार में प्रज्वलित दीपक समस्त पदार्थों को प्रकाशित कर देता है। जब प्रश्न लग्नेश एवं कार्येश में परस्पर शुभ दृष्टि, युति या इत्थशाल योग हो और वे शुभ ग्रहों से दृष्ट व बलवान हों, तो अभीष्ट कार्य की सिद्धि निश्चित होती है।"
    }
    with st.expander(f"📜 शास्त्रीय प्रमाण — {prashna_marga_shloka['title']}", expanded=False):
        st.markdown(f"""
        <div style="background:#FFFBEB; border-left:4px solid #D97706; padding:12px; border-radius:6px; margin-bottom:10px;">
            <b style="color:#B45309; font-size:15px;">📖 ग्रंथ संदर्भ: {prashna_marga_shloka['source']}</b>
            <pre style="white-space:pre-wrap; font-family:serif; font-size:14px; color:#78350F; margin:8px 0; background:transparent; border:none; padding:0;">
{prashna_marga_shloka['shloka']}
            </pre>
            <div style="font-size:13px; color:#92400E; margin-top:6px;">
                <b>हिंदी भावार्थ:</b> {prashna_marga_shloka['meaning']}
            </div>
        </div>
        """, unsafe_allow_html=True)



