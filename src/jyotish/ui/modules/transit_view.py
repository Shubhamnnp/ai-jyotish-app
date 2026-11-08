import streamlit as st
import pandas as pd
from datetime import datetime, timezone, timedelta, date, time
import importlib

from src.jyotish.core.models import BirthData
from src.jyotish.core.calculator import default_chart_calculator
from src.jyotish.services.shastriya_pramana import SHASTRIYA_SHLOKAS
from src.jyotish.ui.sudarshan import PLANET_NAMES_HI
import src.jyotish.ui.chart_renderer as cr_mod
try:
    from src.jyotish.services.transit_calendar import default_transit_calendar_service, PersonalTransitCalendarService
except Exception:
    default_transit_calendar_service = None
    PersonalTransitCalendarService = None
try:
    from src.jyotish.services.transit_graph import default_transit_graph_service
except Exception:
    default_transit_graph_service = None
try:
    from src.jyotish.core.chakras import default_kota_chakra_engine, default_sarvatobhadra_engine
except Exception:
    default_kota_chakra_engine = None
    default_sarvatobhadra_engine = None

def get_live_local_now(tz_offset_hours: float = 5.5) -> datetime:
    return datetime.now(timezone.utc) + timedelta(hours=tz_offset_hours)

def _calc_paya(moon_house_from_transit):
    if moon_house_from_transit in [1, 6, 11]:
        return "स्वर्ण पाया (Gold)", "अत्यंत शुभ, राज सम्मान व धनागम", "#10B981"
    elif moon_house_from_transit in [2, 5, 9]:
        return "रजत पाया (Silver)", "सर्वोत्तम, सुख-शांति व भाग्यवृद्धि", "#3B82F6"
    elif moon_house_from_transit in [3, 7, 10]:
        return "ताम्र पाया (Copper)", "मध्यम शुभ, पुरुषार्थ से कार्य सिद्धि", "#F59E0B"
    else:
        return "लौह पाया (Iron)", "कष्टप्रद, मानसिक तनाव व व्यय", "#EF4444"

def render_transit_view(chart, ayanamsa, house_system, node_type_val, tz_offset, latitude, longitude, default_city_name=None, tabs=None):
    if default_city_name is None:
        default_city_name = st.session_state.get("birth_city", "New Delhi, Delhi, India")
        
    if tabs is None or len(tabs) < 14:
        tabs = [
            "🎯 जन्म-गोचर चक्र",
            "🪐 दैनिक गोचर",
            "⌛ साढ़ेसाती व ढैया",
            "⚡ दोहरा गोचर (गुरु-शनि)",
            "📊 अष्टकवर्ग (SAV/BAV)",
            "⚖️ त्रिकोण शोधन",
            "🔬 कक्षी गोचर",
            "📋 प्रस्ताराष्टकवर्ग",
            "🔵 भृगु बिन्दु",
            "🛡️ सर्वतोभद्र चक्र",
            "🏰 कोटा चक्र दुर्ग",
            "📈 वित्तीय ज्योतिष वेध",
            "📊 ग्रह गति व तरंग",
            "📅 मासिक गोचर कैलेंडर"
        ]
    st.subheader("🪐 गोचर, अष्टकवर्ग, सर्वतोभद्र चक्र एवं कोटा चक्र")
    st.write("तात्कालिक ग्रह गोचर, साढ़ेसाती व ढैया, ८x१२ भिन्नाष्टकवर्ग, शोधन व शोधित पिण्ड, कक्षी गोचर, प्रस्तार, भृगु बिन्दु, सर्वतोभद्र, कोटा चक्र व वित्तीय वेध।")

    # Initialize interactive transit datetime in session state
    now_live = get_live_local_now(tz_offset)
    if "t_manual_date" not in st.session_state:
        st.session_state.t_manual_date = now_live.date()
    if "t_manual_time" not in st.session_state:
        st.session_state.t_manual_time = now_live.time().replace(microsecond=0)

    active_t_dt = datetime.combine(st.session_state.t_manual_date, st.session_state.t_manual_time)
    expander_title = f"⏱️ गोचर काल-घड़ी एवं टाइम-मशीन (सक्रिय: {active_t_dt.strftime('%d-%b-%Y %I:%M %p')}) — क्लिक करके खोलें/बंद करें"

    # Floating active indicator when auto-play is running
    if st.session_state.get("transit_autoplay", False):
        c_p_bar1, c_p_bar2 = st.columns([4, 1.2], vertical_alignment="center")
        with c_p_bar1:
            st.success(f"🟢 **गोचर एनीमेशन सक्रिय (Auto-Playing...)** — वर्तमान: `{active_t_dt.strftime('%d-%b-%Y %I:%M %p')}`")
        with c_p_bar2:
            if st.button("⏸️ एनीमेशन रोकें (Pause)", key="btn_floating_pause", type="primary", use_container_width=True):
                st.session_state.transit_autoplay = False
                st.rerun()

    # Interactive Step Clock & Time-Machine (Collapsible Expander)
    with st.expander(expander_title, expanded=st.session_state.get("tm_expanded", False)):
        c_btn = st.columns(11)
        step_actions = [
            ("-1Y", timedelta(days=-365), "१ वर्ष पीछे"),
            ("-1M", timedelta(days=-30), "१ माह पीछे"),
            ("-1W", timedelta(days=-7), "१ सप्ताह पीछे"),
            ("-1D", timedelta(days=-1), "१ दिन पीछे"),
            ("-1h", timedelta(hours=-1), "१ घंटा पीछे"),
            ("NOW", None, "वर्तमान तात्कालिक समय"),
            ("+1h", timedelta(hours=1), "१ घंटा आगे"),
            ("+1D", timedelta(days=1), "१ दिन आगे"),
            ("+1W", timedelta(days=7), "१ सप्ताह आगे"),
            ("+1M", timedelta(days=30), "१ माह आगे"),
            ("+1Y", timedelta(days=365), "१ वर्ष आगे"),
        ]
        for col_i, (lbl, delta, help_txt) in enumerate(step_actions):
            is_now = (lbl == "NOW")
            if c_btn[col_i].button(lbl, key=f"t_clk_btn_{lbl}", use_container_width=True, type="primary" if is_now else "secondary", help=help_txt):
                st.session_state.tm_expanded = True
                if is_now:
                    curr_now = get_live_local_now(tz_offset)
                    st.session_state.t_manual_date = curr_now.date()
                    st.session_state.t_manual_time = curr_now.time().replace(microsecond=0)
                else:
                    comb = datetime.combine(st.session_state.t_manual_date, st.session_state.t_manual_time)
                    new_dt = comb + delta
                    st.session_state.t_manual_date = new_dt.date()
                    st.session_state.t_manual_time = new_dt.time().replace(microsecond=0)
                st.rerun()

        col_gt1, col_gt2, col_gt3, col_gt4 = st.columns([1.5, 1.5, 2, 1.2])
        with col_gt1:
            st.date_input("📅 गोचर दिनांक (Transit Date)", key="t_manual_date", format="DD/MM/YYYY")
        with col_gt2:
            st.time_input("🕒 गोचर समय (Transit Time)", key="t_manual_time", step=60)
        with col_gt3:
            st.caption(f"📍 स्थान: **{default_city_name}** ({latitude:.2f}°, {longitude:.2f}°)")
            st.info(f"सक्रिय गोचर: **{active_t_dt.strftime('%d-%b-%Y %I:%M:%S %p')}**")
        with col_gt4:
            st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
            if st.button("✖️ संक्षिप्त करें", key="btn_collapse_tm", use_container_width=True, help="टाइम-मशीन को बंद करें"):
                st.session_state.tm_expanded = False
                st.rerun()

        # Auto-Play Continuous Motion Controls
        st.markdown("<div style='height: 4px;'></div>", unsafe_allow_html=True)
        col_ap1, col_ap2, col_ap3 = st.columns([1.6, 2.4, 2.0], vertical_alignment="center")
        is_playing = st.session_state.get("transit_autoplay", False)
        with col_ap1:
            if is_playing:
                if st.button("⏸️ एनीमेशन रोकें (Pause)", key="btn_transit_pause", type="primary", use_container_width=True):
                    st.session_state.transit_autoplay = False
                    st.rerun()
            else:
                if st.button("▶️ ऑटो-प्ले (Auto-Play)", key="btn_transit_play", type="secondary", use_container_width=True, help="ग्रहों को निरंतर समय के साथ घूमते हुए देखने के लिए चलाएं"):
                    st.session_state.transit_autoplay = True
                    st.session_state.tm_expanded = True
                    st.rerun()
        with col_ap2:
            step_mode_options = [
                "+1 दिन प्रति कदम (+1 Day/step)",
                "+1 सप्ताह प्रति कदम (+1 Week/step)",
                "+1 माह प्रति कदम (+1 Month/step)",
                "+1 घंटा प्रति कदम (+1 Hour/step - सूक्ष्म)"
            ]
            cur_ap_step = st.session_state.get("transit_play_step_choice", step_mode_options[0])
            sel_ap_step = st.selectbox(
                "एनिमेशन गति (Animation Step)",
                step_mode_options,
                index=step_mode_options.index(cur_ap_step) if cur_ap_step in step_mode_options else 0,
                key="sel_transit_play_step"
            )
            st.session_state.transit_play_step_choice = sel_ap_step
        with col_ap3:
            if is_playing:
                st.markdown("<span style='color:#10B981; font-weight:800; font-size:13px;'>🟢 एनीमेशन सक्रिय (Playing...)</span>", unsafe_allow_html=True)
            else:
                st.caption("स्वचालित गोचर भ्रमण चक्र — ग्रहों की गति को सजीव देखें")

    t_date = st.session_state.t_manual_date
    t_time = st.session_state.t_manual_time

    is_topo = bool(st.session_state.get("app_is_topocentric", False))
    alt_val = float(st.session_state.get("app_altitude", 0.0))

    # Calculate live transit chart
    t_birth = BirthData(
        name="Transit",
        birth_date=t_date,
        birth_time=t_time,
        latitude=latitude,
        longitude=longitude,
        timezone_offset=tz_offset,
        city=default_city_name,
        altitude=alt_val,
        is_topocentric=is_topo
    )
    try:
        t_chart = default_chart_calculator.calculate_full_chart(t_birth, ayanamsa_name=ayanamsa, house_system=house_system, node_type=node_type_val, topocentric_moon=is_topo, elevation=alt_val, use_cache=False)
    except TypeError:
        t_chart = default_chart_calculator.calculate_full_chart(t_birth, ayanamsa_name=ayanamsa, house_system=house_system, topocentric_moon=is_topo, elevation=alt_val, use_cache=False)

    rashi_names_hi = ["मेष", "वृषभ", "मिथुन", "कर्क", "सिंह", "कन्या", "तुला", "वृश्चिक", "धनु", "मकर", "कुम्भ", "मीन"]
    rashi_symbols = ["♈", "♉", "♊", "♋", "♌", "♍", "♎", "♏", "♐", "♑", "♒", "♓"]
    natal_lagna_id = chart.lagna_sign_id
    natal_moon_id = chart.planets["Moon"].sign_id if "Moon" in chart.planets else 1

    planet_icons = {
        "Sun": "☀️ सूर्य",
        "Moon": "🌙 चन्द्र",
        "Mars": "⚔️ मंगल",
        "Mercury": "☿️ बुध",
        "Jupiter": "🪐 गुरु",
        "Venus": "💎 शुक्र",
        "Saturn": "⚖️ शनि",
        "Rahu": "🐉 राहु",
        "Ketu": "☄️ केतु"
    }

    tab_g1, tab_g2, tab_g3, tab_g4, tab_g5, tab_g6, tab_g7, tab_g8, tab_g9, tab_g10, tab_g11, tab_g12, tab_g13, tab_g14 = st.tabs(tabs)

    # =========================================================================
    # TAB 1: DUAL-RING BI-WHEEL OVERLAY & TRANSIT LAGNA CHART
    # =========================================================================
    with tab_g1:
        import src.jyotish.ui.chart_renderer as cr_mod
        ChartRenderer = cr_mod.ChartRenderer

        c_tmode1, c_tmode2 = st.columns([2.5, 1.5], vertical_alignment="center")
        with c_tmode1:
            transit_chart_type = st.radio(
                "गोचर चक्र प्रदर्शन रूप (Transit Chart Mode)",
                ["🎯 जन्म-गोचर संयुक्त ओवरले (Dual Bi-Wheel)", "🪐 तात्कालिक गोचर लग्न चक्र (Transit Lagna Kundali)"],
                horizontal=True,
                key="transit_view_chart_type_radio"
            )
        with c_tmode2:
            st.caption(f"**गोचर लग्न:** {rashi_names_hi[t_chart.lagna_sign_id - 1]} ({t_chart.lagna_sign_id}) | **समय:** {t_date.strftime('%d-%b-%Y')} {t_time.strftime('%I:%M %p')}")

        c_bw1, c_bw2 = st.columns([1.2, 0.8])
        with c_bw1:
            if "Bi-Wheel" in transit_chart_type:
                st.caption("अंदर जन्म के ग्रह (नीले रंग में) और बाहर तात्कालिक गोचर ग्रह अंश-कला सहित (सुनहरे रंग में ⚡ चिन्ह के साथ):")
                bw_svg = ChartRenderer.render_transit_biwheel_svg(chart, t_chart.planets, title=f"जन्म-गोचर ओवरले कुण्डली ({t_date.strftime('%d-%b-%Y')} {t_time.strftime('%I:%M %p')})")
                st.markdown(bw_svg, unsafe_allow_html=True)
            else:
                st.caption("तात्कालिक आकाश की स्वतंत्र गोचर कुण्डली (समय बदलने पर गोचर लग्न व भाव निरंतर घूमते हैं):")
                c_style = st.session_state.get("app_chart_style", "North Indian")
                if "South" in c_style:
                    t_svg = ChartRenderer.render_south_indian_svg(t_chart, title=f"तात्कालिक गोचर लग्न कुण्डली ({t_date.strftime('%d-%b-%Y')} {t_time.strftime('%I:%M %p')})")
                elif "East" in c_style:
                    t_svg = ChartRenderer.render_east_indian_svg(t_chart, title=f"तात्कालिक गोचर लग्न कुण्डली ({t_date.strftime('%d-%b-%Y')} {t_time.strftime('%I:%M %p')})")
                else:
                    t_svg = ChartRenderer.render_north_indian_svg(t_chart, title=f"तात्कालिक गोचर लग्न कुण्डली ({t_date.strftime('%d-%b-%Y')} {t_time.strftime('%I:%M %p')})")
                st.markdown(t_svg, unsafe_allow_html=True)
        with c_bw2:
            st.markdown("##### ⚡ गोचर एवं जन्म ग्रह युति वेध (Direct Conjunctions)")
            natal_h_map = {p: chart.planets[p].house_from_lagna for p in chart.planets}
            transit_h_map = {p: ((t_chart.planets[p].sign_id - chart.lagna_sign_id) % 12) + 1 for p in t_chart.planets}

            co_presence_found = False
            for h in range(1, 13):
                n_here = [p for p, h_num in natal_h_map.items() if h_num == h]
                t_here = [p for p, h_num in transit_h_map.items() if h_num == h]
                if n_here and t_here:
                    co_presence_found = True
                    s_id = ((chart.lagna_sign_id - 1 + (h - 1)) % 12) + 1
                    s_name = rashi_names_hi[s_id - 1]
                    st.markdown(f"""<div style="background:#FFFBEB; border:1.5px solid #F59E0B; border-radius:8px; padding:10px; margin-bottom:8px;">
    <b style="color:#B45309;">📍 भाव {h} ({s_name}):</b><br/>
    🔵 <b>जन्म ग्रह:</b> {', '.join(n_here)}<br/>
    🟧 <b>गोचर ग्रह:</b> {', '.join(t_here)}<br/>
    <small style="color:#475569;">वर्तमान में गोचर ग्रह जन्म ग्रहों के साथ एक ही भाव में युति संबंध बना रहे हैं।</small>
    </div>""", unsafe_allow_html=True)

            if not co_presence_found:
                st.info("वर्तमान गोचर ग्रह जन्म ग्रहों से अलग भावों में स्वतंत्र संचरण कर रहे हैं।")

    # =========================================================================
    # TAB 2: LIVE TRANSIT PLANETARY TABLE & DIGNITY
    # =========================================================================
    with tab_g2:
        st.markdown("#### 🔴 तात्कालिक ग्रह गोचर तालिका (Real-Time Planetary Transits)")
        st.caption("लक्षित दिनांक व समय पर सौरमंडल के समस्त ग्रहों की स्पष्ट स्थिति, नक्षत्र, गति, भाव एवं अष्टकवर्ग सामर्थ्य:")

        sav_list = chart.ashtakavarga.sav if chart.ashtakavarga else [28]*12
        gochar_rows = []
        for p_name in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]:
            if p_name in t_chart.planets:
                tp = t_chart.planets[p_name]
                s_idx = tp.sign_id - 1
                s_name = rashi_names_hi[s_idx]
                s_sym = rashi_symbols[s_idx]
                deg_str = f"{int(tp.sign_degree)}° {int((tp.sign_degree % 1)*60)}'"
                h_from_lagna = (tp.sign_id - natal_lagna_id) % 12 + 1
                h_from_moon = (tp.sign_id - natal_moon_id) % 12 + 1
                sign_sav = sav_list[s_idx]
                sav_status = "🌟 उत्तम (" + str(sign_sav) + ")" if sign_sav >= 30 else ("✅ शुभ (" + str(sign_sav) + ")" if sign_sav >= 28 else "⚠️ न्यून (" + str(sign_sav) + ")")
                motion_str = "⚡ वक्री (R)" if tp.is_retrograde else "मार्गी (D)"

                gochar_rows.append({
                    "ग्रह (Planet)": planet_icons.get(p_name, p_name),
                    "गोचर राशि (Sign)": f"{s_sym} {s_name}",
                    "अंश (Degree)": deg_str,
                    "नक्षत्र (Nakshatra)": f"{tp.nakshatra_name} (पद {tp.nakshatra_pada})",
                    "गति (Motion)": motion_str,
                    "लग्न से भाव": f"{h_from_lagna} भाव",
                    "चन्द्र से भाव": f"{h_from_moon} भाव",
                    "SAV सामर्थ्य": sav_status
                })
        st.dataframe(pd.DataFrame(gochar_rows), use_container_width=True)

    # =========================================================================
    # TAB 3: SATURN SADE SATI & DHAIYA TRACKER
    # =========================================================================
    with tab_g3:
        st.markdown("#### 🪐 साढ़ेसाती एवं ढैया लाइव ट्रैकर (Saturn Sade Sati & Dhaiya Tracker)")
        st.caption("शनिदेव का जन्म चन्द्र से १२वें, प्रथम व द्वितीय भाव संचरण (साढ़ेसाती) तथा चतुर्थ व अष्टम भाव संचरण (ढैया):")

        sat_sign_id = t_chart.planets["Saturn"].sign_id if "Saturn" in t_chart.planets else 11
        sat_diff = (sat_sign_id - natal_moon_id) % 12

        sat_phase_title = "सामान्य गोचर"
        sat_badge_class = "harmonious"
        sat_desc = ""

        if sat_diff == 11:
            sat_phase_title = "साढ़ेसाती: प्रथम चरण (Rising Phase - 12th House)"
            sat_badge_class = "high-risk"
            sat_desc = "शनि जन्म चन्द्र से 12वें भाव में गोचरस्थ हैं। मानसिक तनाव, व्यय एवं दूरस्थ यात्राओं के संकेत।"
        elif sat_diff == 0:
            sat_phase_title = "साढ़ेसाती: द्वितीय चरण (Peak / Janma Shani - 1st House)"
            sat_badge_class = "high-risk"
            sat_desc = "शनि चन्द्र के ऊपर से गोचर कर रहे हैं। धैर्य, अनुशासन एवं स्वास्थ्य पर विशेष ध्यान अपेक्षित है।"
        elif sat_diff == 1:
            sat_phase_title = "साढ़ेसाती: तृतीय चरण (Setting Phase - 2nd House)"
            sat_badge_class = "moderate-risk"
            sat_desc = "शनि चन्द्र से द्वितीय भाव (धन भाव) में हैं। आर्थिक संतुलन एवं वाणी पर नियंत्रण लाभप्रद रहेगा।"
        elif sat_diff == 3:
            sat_phase_title = "कंटक शनि / लघु कल्याणी ढैया (4th House)"
            sat_badge_class = "moderate-risk"
            sat_desc = "शनि चन्द्र से चतुर्थ भाव में हैं। गृह-सुख, वाहन एवं माता के स्वास्थ्य में सावधानी बरतें।"
        elif sat_diff == 7:
            sat_phase_title = "अष्टम शनि / कंटक ढैया (8th House)"
            sat_badge_class = "high-risk"
            sat_desc = "शनि चन्द्र से अष्टम भाव में हैं। आकस्मिक बदलाव, गूढ़ ज्ञान में वृद्धि परंतु स्वास्थ्य में सावधानी।"
        else:
            sat_phase_title = f"अनुकूल गोचर (चन्द्र से {sat_diff + 1}वें भाव में)"
            sat_badge_class = "harmonious"
            sat_desc = f"शनि का वर्तमान गोचर चन्द्र राशि ({rashi_names_hi[natal_moon_id-1]}) से {sat_diff + 1}वें भाव में अनुकूल फलदायक है।"

        bg_col = "#FEF2F2" if "high" in sat_badge_class else ("#FFFBEB" if "moderate" in sat_badge_class else "#ECFDF5")
        border_col = "#EF4444" if "high" in sat_badge_class else ("#F59E0B" if "moderate" in sat_badge_class else "#10B981")
        text_col = "#991B1B" if "high" in sat_badge_class else ("#92400E" if "moderate" in sat_badge_class else "#065F46")

        st.markdown(f"""<div style="background:#FFFFFF; border:1.5px solid {border_col}; border-radius:10px; padding:16px; box-shadow:0 2px 8px rgba(0,0,0,0.04); margin-bottom:16px;">
    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
    <b style="font-size:15px; color:#0F172A;">🌙 जातक चन्द्र राशि: {rashi_names_hi[natal_moon_id-1]}</b>
    <span style="background:{bg_col}; color:{text_col}; border:1.5px solid {border_col}; border-radius:8px; padding:4px 12px; font-weight:800; font-size:12px;">{sat_phase_title.split('(')[0]}</span>
    </div>
    <div style="font-size:13px; color:#1E293B; line-height:1.6; margin-bottom:10px;">
    🪐 <b>वर्तमान शनि गोचर:</b> {rashi_symbols[sat_sign_id-1]} {rashi_names_hi[sat_sign_id-1]} राशि<br/>
    📜 <b>शास्त्रीय प्रभाव:</b> {sat_desc}
    </div>
    <div style="background:#F8FAFC; border:1px solid #CBD5E1; border-radius:6px; padding:8px 12px; font-size:12px; color:#334155;">
    🪔 <b>शास्त्रीय उपाय:</b> प्रत्येक शनिवार को पीपल के वृक्ष पर तिल के तेल का दीपक प्रज्वलित करें एवं ॐ शं शनैश्चराय नमः का नियमित जप करें।
    </div>
    </div>""", unsafe_allow_html=True)

        st.markdown("##### 📜 शनि गोचर के शास्त्रीय चरण व कालखंड")
        sade_table = [
            {"चरण / ढैया": "१२वां भाव (द्वादश)", "नाम": "साढ़ेसाती उदय चरण (Rising)", "प्रभाव क्षेत्र": "स्थान परिवर्तन, व्यय, अनिद्रा, विदेश गमन", "तीव्रता": "मध्यम"},
            {"चरण / ढैया": "प्रथम भाव (जन्म शनि)", "नाम": "साढ़ेसाती शिखर चरण (Peak)", "प्रभाव क्षेत्र": "मानसिक तनाव, शारीरिक श्रम, व्यक्तिगत परीक्षा", "तीव्रता": "अति गंभीर"},
            {"चरण / ढैया": "द्वितीय भाव (धन शनि)", "नाम": "साढ़ेसाती अस्त चरण (Setting)", "प्रभाव क्षेत्र": "आर्थिक दबाव, पारिवारिक दायित्व, वाणी नियंत्रण", "तीव्रता": "मध्यम"},
            {"चरण / ढैया": "चतुर्थ भाव (कंटक ढैया)", "नाम": "लघु कल्याणी ढैया (Kantaka)", "प्रभाव क्षेत्र": "गृह-सुख में विघ्न, वाहन समस्या, माता का स्वास्थ्य", "तीव्रता": "संवेदनशील"},
            {"चरण / ढैया": "अष्टम भाव (अष्टम शनि)", "नाम": "अष्टम कंटक ढैया (Ashtama)", "प्रभाव क्षेत्र": "आकस्मिक बाधाएं, स्वास्थ्य संकट, गूढ़ साधना", "तीव्रता": "अति संवेदनशील"}
        ]
        st.dataframe(pd.DataFrame(sade_table), use_container_width=True, hide_index=True)

        st.markdown("---")
        st.markdown("##### 🪙 शनि व गुरु का शास्त्रीय पाया विचार (Transit Paya / Footing)")
        st.caption("गोचर में चन्द्रमा के जन्म चन्द्र से स्थान के आधार पर पाया निर्णय (१,६,११: स्वर्ण | २,५,९: रजत | ३,७,१०: ताम्र | ४,८,१२: लौह):")

        t_moon_id = t_chart.planets["Moon"].sign_id if "Moon" in t_chart.planets else 1
        moon_diff = ((t_moon_id - natal_moon_id) % 12) + 1

        def _calc_paya(m_h: int):
            if m_h in (1, 6, 11):
                return "स्वर्ण पाया (Gold)", "#F59E0B", "#FEF3C7", "50% (मध्यम)", "प्रारंभिक संघर्षोपरांत लाभ"
            elif m_h in (2, 5, 9):
                return "रजत पाया (Silver)", "#10B981", "#D1FAE5", "100% (सर्वोत्तम)", "धन वृद्धि, यश व सर्वतोमुखी सिद्धि"
            elif m_h in (3, 7, 10):
                return "ताम्र पाया (Copper)", "#3B82F6", "#DBEAFE", "75% (उत्तम)", "साहस, पराक्रम व व्यापार विस्तार"
            else:
                return "लौह पाया (Iron)", "#EF4444", "#FEE2E2", "25% (कष्टप्रद)", "मानसिक तनाव, शारीरिक श्रम व सतर्कता"

        p_name, p_bd, p_bg, p_rating, p_desc = _calc_paya(moon_diff)

        c_py1, c_py2 = st.columns(2)
        with c_py1:
            st.markdown(f"""
    <div style="background:{p_bg}; border:1.5px solid {p_bd}; border-radius:10px; padding:14px;">
    <div style="font-size:15px; font-weight:900; color:{p_bd};">🪐 शनि पाया: {p_name}</div>
    <div style="font-size:12px; color:#1E293B; margin-top:6px;">
        • <b>गोचर चन्द्र भाव:</b> जन्म चन्द्र से {moon_diff}वां भाव<br/>
        • <b>शुभता सामर्थ्य:</b> <b>{p_rating}</b><br/>
        • <b>शास्त्रीय फल:</b> {p_desc}
    </div>
    </div>
    """, unsafe_allow_html=True)

        with c_py2:
            st.markdown(f"""
    <div style="background:{p_bg}; border:1.5px solid {p_bd}; border-radius:10px; padding:14px;">
    <div style="font-size:15px; font-weight:900; color:{p_bd};">🪐 गुरु पाया: {p_name}</div>
    <div style="font-size:12px; color:#1E293B; margin-top:6px;">
        • <b>गोचर चन्द्र भाव:</b> जन्म चन्द्र से {moon_diff}वां भाव<br/>
        • <b>शुभता सामर्थ्य:</b> <b>{p_rating}</b><br/>
        • <b>शास्त्रीय फल:</b> {p_desc}
    </div>
    </div>
    """, unsafe_allow_html=True)

    # =========================================================================
    # TAB 4: JUPITER-SATURN DOUBLE TRANSIT
    # =========================================================================
    with tab_g4:
        st.markdown("#### ⚡ गुरु-शनि दोहरा गोचर (Jupiter-Saturn Double Transit Activation)")
        st.caption("पाराशरी ज्योतिष का सर्वमान्य नियम: जिस भाव पर गुरु एवं शनि दोनों की संयुक्त दृष्टि अथवा गोचर प्रभाव होता है, वही भाव जीवन में फलीभूत होता है:")

        j_sign_id = t_chart.planets["Jupiter"].sign_id if "Jupiter" in t_chart.planets else 2
        s_sign_id = t_chart.planets["Saturn"].sign_id if "Saturn" in t_chart.planets else 11

        j_asp_signs = [j_sign_id, (j_sign_id - 1 + 4) % 12 + 1, (j_sign_id - 1 + 6) % 12 + 1, (j_sign_id - 1 + 8) % 12 + 1]
        s_asp_signs = [s_sign_id, (s_sign_id - 1 + 2) % 12 + 1, (s_sign_id - 1 + 6) % 12 + 1, (s_sign_id - 1 + 9) % 12 + 1]
        common_signs = sorted(list(set(j_asp_signs).intersection(set(s_asp_signs))))

        house_significances = {
            1: "व्यक्तिगत स्वास्थ्य, प्रतिष्ठा एवं नई शुरुआत",
            2: "धन, पैतृक संपत्ति एवं पारिवारिक वृद्धि",
            3: "पराक्रम, नए अनुबंध एवं छोटे भाई-बहन",
            4: "भूमि, भवन, वाहन एवं पारिवारिक सुख",
            5: "संतान, विद्या, निवेश एवं मंत्र सिद्धि",
            6: "ऋण मुक्ति, रोग निवारण एवं प्रतियोगिता में विजय",
            7: "विवाह, व्यापारिक साझेदारी एवं जन-सम्बंध",
            8: "गूढ़ शोध, वसीयत एवं आकस्मिक लाभ",
            9: "उच्च शिक्षा, तीर्थाटन एवं भाग्योदय",
            10: "कार्यक्षेत्र, पदोन्नति, मान-सम्मान एवं व्यवसाय",
            11: "आय वृद्धि, महत्वाकांक्षा पूर्ति एवं लाभ",
            12: "विदेश यात्रा, आध्यात्मिक सिद्धि एवं शुभ व्यय"
        }

        st.markdown(f"""<div style="background:#FFFFFF; border:1.5px solid #2563EB; border-radius:10px; padding:16px; box-shadow:0 2px 8px rgba(37,99,235,0.06); margin-bottom:16px;">
    <div style="font-weight:800; color:#1E40AF; font-size:15px; margin-bottom:6px;">
    🎯 जीवन के सक्रिय भाव (Doubly Activated Houses by Jupiter & Saturn)
    </div>
    <div style="font-size:13px; color:#1E293B; margin-bottom:10px; line-height:1.5;">
    गुरु ({rashi_names_hi[j_sign_id-1]}) और शनि ({rashi_names_hi[s_sign_id-1]}) दोनों का संयुक्त प्रभाव निम्न राशियों व भावों पर केंद्रित है:
    </div>
    <div style="display:flex; flex-direction:column; gap:8px;">""", unsafe_allow_html=True)

        for c_sign in common_signs:
            h_lagna = (c_sign - natal_lagna_id) % 12 + 1
            h_meaning = house_significances.get(h_lagna, "शुभ फलदायक")
            st.markdown(f"""<div style="background:#EFF6FF; border:1px solid #93C5FD; border-radius:6px; padding:8px 12px; font-size:13px; color:#1E3A8A;">
    ✨ <b>{rashi_symbols[c_sign-1]} {rashi_names_hi[c_sign-1]} (लग्न से {h_lagna} भाव):</b> {h_meaning}
    </div>""", unsafe_allow_html=True)

        st.markdown("</div></div>", unsafe_allow_html=True)
        st.info("💡 **फलित सूत्र:** जब किसी जातक के विवाह, संतान अथवा करियर का समय देखना हो, तो ७वें, ५वें या १०वें भाव पर गुरु-शनि दोनों की संयुक्त दृष्टि का होना उस घटना के घटित होने की अनिवार्य शर्त मानी जाती है।")

    # =========================================================================
    # TAB 5: SAV & BAV 8x12 MATRIX
    # =========================================================================
    with tab_g5:
        st.markdown("#### 📊 सम्पूर्ण भिन्नाष्टकवर्ग (BAV 8x12) एवं सर्व अष्टकवर्ग (SAV) तालिका")
        st.caption("७ प्रमुख ग्रहों का द्वादश राशियों में बिन्दु आवंटन (०-३: न्यून/लाल, ४: सम, ५-८: शुभ/हरा, कुल: ३३७ बिन्दु):")

        if chart.ashtakavarga and chart.ashtakavarga.bav:
            bav_matrix = chart.ashtakavarga.bav
            sav_array = chart.ashtakavarga.sav

            bav_html = '<div style="overflow-x: auto; border: 1.5px solid #CBD5E1; border-radius: 10px; margin-bottom: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.04);">'
            bav_html += '<table style="width: 100%; border-collapse: collapse; text-align: center; background: #FFFFFF; font-family: Segoe UI, Arial, sans-serif;">'
            bav_html += '<thead><tr style="background: #F1F5F9; border-bottom: 2px solid #CBD5E1;">'
            bav_html += '<th style="padding: 10px 12px; font-weight: 800; color: #0F172A; font-size: 13px; text-align: left;">ग्रह / राशि</th>'
            for s_i, r_name in enumerate(rashi_names_hi):
                bav_html += f'<th style="padding: 10px 6px; font-weight: 800; color: #0F172A; font-size: 12px;">{rashi_symbols[s_i]}<br/>{r_name}</th>'
            bav_html += '<th style="padding: 10px 8px; font-weight: 900; color: #1E3A8A; font-size: 13px; background: #DBEAFE;">कुल</th>'
            bav_html += '</tr></thead><tbody>'

            planet_order = [
                ("Sun", "☀️ सूर्य (Sun)"), ("Moon", "🌙 चन्द्र (Moon)"), ("Mars", "⚔️ मंगल (Mars)"),
                ("Mercury", "☿️ बुध (Mercury)"), ("Jupiter", "🪐 गुरु (Jupiter)"), ("Venus", "💎 शुक्र (Venus)"),
                ("Saturn", "⚖️ शनि (Saturn)")
            ]
            for p_k, p_label in planet_order:
                bav_row = bav_matrix.get(p_k, [0]*12)
                row_total = sum(bav_row)
                bav_html += '<tr style="border-bottom: 1px solid #E2E8F0;">'
                bav_html += f'<td style="padding: 8px 12px; font-weight: 700; color: #0F172A; font-size: 12.5px; text-align: left; background: #F8FAFC;">{p_label}</td>'
                for b_val in bav_row:
                    if b_val <= 3:
                        cell_bg = "#FEE2E2"
                        cell_color = "#991B1B"
                    elif b_val == 4:
                        cell_bg = "#F8FAFC"
                        cell_color = "#334155"
                    else:
                        cell_bg = "#DCFCE7"
                        cell_color = "#166534"
                    bav_html += f'<td style="padding: 6px 4px; font-weight: 800; font-size: 13px; background: {cell_bg}; color: {cell_color}; border: 1px solid #E2E8F0;">{b_val}</td>'
                bav_html += f'<td style="padding: 6px 8px; font-weight: 900; font-size: 13px; background: #EFF6FF; color: #1E40AF; border: 1px solid #CBD5E1;">{row_total}</td>'
                bav_html += '</tr>'

            bav_html += '<tr style="background: linear-gradient(135deg, #FEF3C7 0%, #FDE68A 100%); border-top: 2.5px solid #D97706; font-weight: 900;">'
            bav_html += '<td style="padding: 10px 12px; color: #78350F; font-size: 13.5px; text-align: left;">🌟 सर्व अष्टकवर्ग (SAV)</td>'
            for sav_val in sav_array:
                sav_color = "#166534" if sav_val >= 28 else "#991B1B"
                bav_html += f'<td style="padding: 8px 4px; color: {sav_color}; font-size: 14px; border: 1px solid #FCD34D;">{sav_val}</td>'
            bav_html += f'<td style="padding: 8px 8px; color: #78350F; font-size: 15px; border: 1.5px solid #D97706; background: #FDE68A;">{sum(sav_array)}</td>'
            bav_html += '</tr></tbody></table></div>'
            st.markdown(bav_html, unsafe_allow_html=True)

        col_av1, col_av2 = st.columns(2)
        with col_av1:
            st.markdown("#### 📈 सर्व अष्टकवर्ग (SAV) बिन्दु वितरण आरेख")
            sav_df = pd.DataFrame({"Rashi": rashi_names_hi, "Bindus": chart.ashtakavarga.sav}).set_index("Rashi")
            st.bar_chart(sav_df)
        with col_av2:
            st.markdown("#### 🎯 अष्टकवर्ग सामर्थ्य मूल्यांकन")
            high_houses = [f"{rashi_names_hi[i]} ({chart.ashtakavarga.sav[i]} बिन्दु)" for i in range(12) if chart.ashtakavarga.sav[i] >= 30]
            low_houses = [f"{rashi_names_hi[i]} ({chart.ashtakavarga.sav[i]} बिन्दु)" for i in range(12) if chart.ashtakavarga.sav[i] < 25]
            st.success(f"🟢 **सर्वश्रेष्ठ बली राशियाँ (SAV ≥ 30):** {', '.join(high_houses) if high_houses else 'सामान्य'}")
            st.warning(f"🔴 **कमजोर राशियाँ (SAV < 25):** {', '.join(low_houses) if low_houses else 'कोई नहीं'}")
            st.caption("२८ बिन्दु औसत माने जाते हैं। २८ से अधिक बिन्दु वाले भाव में ग्रहों का गोचर सफलता देता है, जबकि २५ से कम बिन्दु वाले भाव में गोचर संघर्षकारी होता है।")

    # =========================================================================
    # TAB 6: TRIKONA & EKADHIPATYA SHODHANA & SHODHITA PINDA
    # =========================================================================
    with tab_g6:
        st.markdown("#### ⚖️ त्रिकोण व एकाधिपत्य शोधन एवं शोधित पिण्ड (Shodhana & Shodhita Pinda)")
        st.caption("बृहत्पाराशर होरा शास्त्र अध्याय ६९-७० — त्रिकोण शोधन (१-५-९ त्रिक), एकाधिपत्य शोधन एवं राशि/ग्रह/योग पिण्ड गणना:")

        if chart.ashtakavarga and chart.ashtakavarga.shodhana:
            sh = chart.ashtakavarga.shodhana

            # KPI Summary
            col_sh_k1, col_sh_k2, col_sh_k3 = st.columns(3)
            tot_yoga_pinda = sum(sh.yoga_pinda.values())
            max_p_pinda = max(sh.yoga_pinda.items(), key=lambda x: x[1])
            min_p_pinda = min(sh.yoga_pinda.items(), key=lambda x: x[1])

            with col_sh_k1:
                st.metric("कुल शोधित योग पिण्ड", f"{tot_yoga_pinda} बिन्दु", "समस्त ७ ग्रह")
            with col_sh_k2:
                st.metric("सर्वोच्च पिण्ड ग्रह", f"{planet_icons.get(max_p_pinda[0], max_p_pinda[0])}", f"{max_p_pinda[1]} बिन्दु (सर्वाधिक बली)")
            with col_sh_k3:
                st.metric("न्यूनतम पिण्ड ग्रह", f"{planet_icons.get(min_p_pinda[0], min_p_pinda[0])}", f"{min_p_pinda[1]} बिन्दु (उपाय अपेक्षित)")

            st.write("")
            tab_sh1, tab_sh2, tab_sh3 = st.tabs([
                "📊 शोधित पिण्ड एवं आयुर्दाय तालिका",
                "🔻 त्रिकोण शोधन ग्रिड (Trikona Shodhana)",
                "👑 एकाधिपत्य शोधन ग्रिड (Ekadhipatya Shodhana)"
            ])

            with tab_sh1:
                st.markdown("##### ⚖️ ग्रहवार राशि पिण्ड, ग्रह पिण्ड एवं शोधित योग पिण्ड")
                pinda_table = []
                for p_k in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]:
                    rp = sh.rashi_pinda.get(p_k, 0)
                    gp = sh.graha_pinda.get(p_k, 0)
                    yp = sh.yoga_pinda.get(p_k, 0)
                    pinda_table.append({
                        "ग्रह (Planet)": planet_icons.get(p_k, p_k),
                        "राशि पिण्ड (Rashi Pinda)": rp,
                        "ग्रह पिण्ड (Graha Pinda)": gp,
                        "शोधित योग पिण्ड (Yoga Pinda)": yp,
                        "सामर्थ्य स्तर": "🌟 अति बली" if yp >= 140 else ("✅ मध्यम" if yp >= 100 else "⚠️ निर्बल")
                    })
                st.dataframe(pd.DataFrame(pinda_table), use_container_width=True, hide_index=True)
                st.info("💡 **शोधित पिण्ड शास्त्रीय रहस्य:** जब गुरु अथवा शनि उस राशि में गोचर करते हैं जिसका संबंध सर्वाधिक योग पिण्ड वाले ग्रह से हो, तो जीवन में अत्यंत सुखद व युगांतरकारी घटनाएं (विवाह, भाग्योदय, पद) घटित होती हैं।")

            with tab_sh2:
                st.markdown("##### 🔻 त्रिकोण शोधन के पश्चात अवशिष्ट बिन्दु (Trikona Shodhana Reduced BAV)")
                st.caption("मेष-सिंह-धनु, वृषभ-कन्या-मकर, मिथुन-तुला-कुम्भ, कर्क-वृश्चिक-मीन त्रिकोणों में न्यूनतम बिन्दु घटाने के बाद:")
                trik_rows = []
                for p_k in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]:
                    t_vals = sh.trikona_reduced_bav.get(p_k, [0]*12)
                    r_dict = {"ग्रह": planet_icons.get(p_k, p_k)}
                    for s_idx, s_n in enumerate(rashi_names_hi):
                        r_dict[f"{s_n[:3]} ({s_idx+1})"] = t_vals[s_idx]
                    r_dict["योग"] = sum(t_vals)
                    trik_rows.append(r_dict)
                st.dataframe(pd.DataFrame(trik_rows), use_container_width=True, hide_index=True)

            with tab_sh3:
                st.markdown("##### 👑 एकाधिपत्य शोधन के पश्चात अवशिष्ट बिन्दु (Ekadhipatya Shodhana Reduced BAV)")
                st.caption("एक ही ग्रह के स्वामित्व वाली दोनों राशियों (यथा मेष-वृश्चिक, वृषभ-तुला, मिथुन-कन्या, धनु-मीन, मकर-कुंभ) में ग्रहों की उपस्थिति व बिन्दुओं का शास्त्रीय परिशोधन:")
                eka_rows = []
                for p_k in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]:
                    e_vals = sh.ekadhipatya_reduced_bav.get(p_k, [0]*12)
                    r_dict = {"ग्रह": planet_icons.get(p_k, p_k)}
                    for s_idx, s_n in enumerate(rashi_names_hi):
                        r_dict[f"{s_n[:3]} ({s_idx+1})"] = e_vals[s_idx]
                    r_dict["योग"] = sum(e_vals)
                    eka_rows.append(r_dict)
                st.dataframe(pd.DataFrame(eka_rows), use_container_width=True, hide_index=True)
        else:
            st.info("अष्टकवर्ग शोधन गणना उपलब्ध नहीं।")

    # =========================================================================
    # TAB 7: KAKSHYA 3°45' TRANSIT SCANNER
    # =========================================================================
    with tab_g7:
        st.markdown("### 🔬 अष्टकवर्ग कक्षी गोचर स्कैनर (Kakshya 3°45' Transit Scanner)")
        st.caption("शास्त्रीय शोध स्तरीय ३°४५' (3.75°) अष्ट-कक्षी सूक्ष्म गोचर वेध — शनि, गुरु, मंगल, सूर्य, शुक्र, बुध, चन्द्र एवं लग्न कक्षी में बिन्दु (१=शुभ / ०=रिक्ता) परीक्षण:")

        k_shloka = SHASTRIYA_SHLOKAS.get("kakshya_system", {})
        if k_shloka:
            k_lines = "<br/>".join(k_shloka['shloka'].splitlines())
            st.markdown(f"""
    <div style="background: rgba(16, 185, 129, 0.08); border-left: 4px solid #10B981; padding: 12px 16px; border-radius: 6px; margin: 10px 0 16px 0;">
    <div style="font-weight: 700; color: #047857; font-size: 13px; margin-bottom: 4px;">📖 {k_shloka['grantha']}</div>
    <div style="font-family: 'Devanagari Sangam MN', serif; font-size: 14px; font-weight: 600; line-height: 1.6; color: #0F172A;">
        {k_lines}
    </div>
    <div style="margin-top: 6px; font-size: 12px; color: #334155; line-height: 1.5;">
        <b>हिंदी भावार्थ:</b> {k_shloka['anuvad_hi']}
    </div>
    <div style="margin-top: 4px; font-size: 11px; color: #64748B;">
        <b>शास्त्रीय कक्षी विभाजन नियम:</b> {k_shloka['rule']}
    </div>
    </div>
    """, unsafe_allow_html=True)

        try:
            import src.jyotish.services.kakshya as kakshya_mod
            kak_svc = kakshya_mod.default_kakshya_service

            kak_res = kak_svc.scan_all_transits(chart, target_date=t_date)
            planets_data = kak_res["planets"]

            ck_kpi1, ck_kpi2, ck_kpi3, ck_kpi4, ck_kpi5 = st.columns(5)
            with ck_kpi1:
                st.metric("कुल शुभ कक्षी (Subha)", f"{kak_res['subha_count']} / {kak_res['total_count']} ग्रह", f"{kak_res['overall_kakshya_pct']}% अनुकूलता")
            with ck_kpi2:
                st.metric("अवरुद्ध कक्षी (Asubha)", f"{kak_res['asubha_count']} ग्रह", "रिक्ता / संघर्ष")
            with ck_kpi3:
                sat_info = planets_data.get("Saturn", {})
                st.metric("🪐 शनि कक्षी गोचर", f"कक्षी {sat_info.get('kakshya_num', '-')}: {sat_info.get('kakshya_lord_hi', '-')}", "🟢 १ बिन्दु (शुभ)" if sat_info.get('bindu_val') == 1 else "🔴 ० बिन्दु (अशुभ)")
            with ck_kpi4:
                jup_info = planets_data.get("Jupiter", {})
                st.metric("♃ गुरु कक्षी गोचर", f"कक्षी {jup_info.get('kakshya_num', '-')}: {jup_info.get('kakshya_lord_hi', '-')}", "🟢 १ बिन्दु (शुभ)" if jup_info.get('bindu_val') == 1 else "🔴 ० बिन्दु (अशुभ)")
            with ck_kpi5:
                rahu_info = planets_data.get("Rahu", {})
                st.metric("🐉 राहु कक्षी गोचर", f"कक्षी {rahu_info.get('kakshya_num', '-')}: {rahu_info.get('kakshya_lord_hi', '-')}", "🟢 १ बिन्दु (शुभ)" if rahu_info.get('bindu_val') == 1 else "🔴 ० बिन्दु (अशुभ)")

            st.markdown("#### ⚡ तात्कालिक कक्षी स्थिति एवं ८-खंडीय अष्टकवर्ग पट्टी")
            for p_name, p_d in planets_data.items():
                p_badge_color = "#10B981" if p_d["bindu_val"] == 1 else "#EF4444"
                p_badge_bg = "#DCFCE7" if p_d["bindu_val"] == 1 else "#FEE2E2"

                strip_cells = ""
                for k in p_d["full_kakshyas"]:
                    is_curr = k["is_current"]
                    has_b = (k["bindu"] == 1)
                    bg = "#10B981" if has_b else "#E2E8F0"
                    txt_color = "#FFFFFF" if has_b else "#64748B"
                    box_border = "border: 2.5px solid #F59E0B; box-shadow: 0 0 8px rgba(245,158,11,0.8);" if is_curr else "border: 1px solid rgba(0,0,0,0.12);"
                    curr_marker = "<div style='font-size:9px; background:#F59E0B; color:#000; font-weight:900; border-radius:3px; padding:1px;'>सक्रिय</div>" if is_curr else ""
                    cell_html = (
                        f'<div style="flex:1; background:{bg}; color:{txt_color}; {box_border} '
                        f'border-radius:6px; padding:6px 2px; text-align:center; min-width:38px;">'
                        f'{curr_marker}'
                        f'<div style="font-size:11px; font-weight:700;">{k["icon"]} {k["lord_hi"]}</div>'
                        f'<div style="font-size:12px; font-weight:900; margin-top:2px;">{k["bindu"]}</div>'
                        f'</div>'
                    )
                    strip_cells += cell_html

                card_html = (
                    f'<div style="background:#F8FAFC; border:1.5px solid #CBD5E1; border-radius:10px; padding:14px; margin-bottom:12px;">'
                    f'<div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; margin-bottom:8px;">'
                    f'<div>'
                    f'<b style="font-size:15px; color:#0F172A;">{p_d["planet_hi"]} ({p_name})</b> — '
                    f'<span style="color:#2563EB; font-weight:600;">{p_d["sign_name"]} राशि ({p_d["deg_in_sign"]:.2f}°)</span> | '
                    f'<span>कक्षी {p_d["kakshya_num"]}: <b>{p_d["kakshya_icon"]} {p_d["kakshya_lord_hi"]}</b> ({p_d["start_deg"]:.2f}° - {p_d["end_deg"]:.2f}°)</span>'
                    f'</div>'
                    f'<span style="background:{p_badge_bg}; color:{p_badge_color}; padding:3px 10px; border-radius:12px; font-size:12px; font-weight:800;">'
                    f'{p_d["verdict_badge"]}'
                    f'</span>'
                    f'</div>'
                    f'<div style="display:flex; gap:6px; margin:8px 0; overflow-x:auto;">'
                    f'{strip_cells}'
                    f'</div>'
                    f'<small style="color:#475569; font-size:12px;">💡 <b>शास्त्रीय वेध:</b> {p_d["verdict_desc"]} (इस राशि में कुल BAV बिन्दु: <b>{p_d["bav_sign_score"]}/8</b>)</small>'
                    f'</div>'
                )
                st.markdown(card_html, unsafe_allow_html=True)

            st.markdown("---")
            st.markdown("#### ⏳ ३०-दिवसीय आगामी कक्षी संक्रमण कालक्रम (30-Day Forward Kakshya Timeline)")
            k_timeline = kak_svc.generate_30day_kakshya_timeline(chart, start_date=t_date, days=30)
            tl_rows = []
            for item in k_timeline:
                sat_b = f"{'🟢 1 (शुभ)' if item['saturn']['bindu_val']==1 else '🔴 0 (अशुभ)'} - {item['saturn']['kakshya_lord_hi']}" if item['saturn'] else "-"
                jup_b = f"{'🟢 1 (शुभ)' if item['jupiter']['bindu_val']==1 else '🔴 0 (अशुभ)'} - {item['jupiter']['kakshya_lord_hi']}" if item['jupiter'] else "-"
                ev_str = " | ".join(item['events']) if item['events'] else "—"
                tl_rows.append({
                    "दिनांक": item["date_str"],
                    "🪐 शनि कक्षी (Bindu)": sat_b,
                    "♃ गुरु कक्षी (Bindu)": jup_b,
                    "⚡ कक्षी परिवर्तन / घटना": ev_str
                })
            st.dataframe(pd.DataFrame(tl_rows), use_container_width=True, hide_index=True)
        except Exception as _e_kak:
            st.error(f"कक्षी गोचर गणना में त्रुटि: {_e_kak}")

    # =========================================================================
    # TAB 8: PRASTARA ASHTAKAVARGA 8x12 GRID
    # =========================================================================
    with tab_g8:
        st.markdown("### 📊 प्रस्तार अष्टकवर्ग (Prastara Ashtakvarga — 8×12 Matrix Grid)")
        st.caption("८ योगदानकर्ता (सूर्य, चन्द्र, मंगल, बुध, गुरु, शुक्र, शनि, लग्न) × १२ राशियां = प्रत्येक ग्रह का बिन्दु/रेखा ग्रिड:")
        try:
            import src.jyotish.core.ashtakavarga as ak_mod
            if chart.ashtakavarga:
                _prastara = ak_mod.AshtakavargaCalculator.calculate_prastara(chart, chart.ashtakavarga)
                if _prastara:
                    _psel = st.selectbox("ग्रह चुनें (Select Planet for Prastara)", list(_prastara.keys()), key="prastara_sel_14tab")
                    if _psel and _psel in _prastara:
                        _p_data = _prastara[_psel]
                        _grid_rows = _p_data.get("grid", [])
                        _sign_names = _p_data.get("sign_names", rashi_names_hi)
                        _bav_total = _p_data.get("bav_total", [])
                        if _grid_rows:
                            _pr_rows = []
                            for _r in _grid_rows:
                                _c_name = _r.get("contributor", "")
                                _bindus = _r.get("bindus", [0]*12)
                                _row = {"योगदानकर्ता (Contributor)": _c_name}
                                for _idx, _sname in enumerate(_sign_names):
                                    _col_title = f"{_sname[:3]} ({_idx+1})"
                                    _row[_col_title] = "● 1" if (_idx < len(_bindus) and _bindus[_idx] == 1) else "—"
                                _row["योग (Total)"] = sum(_bindus)
                                _pr_rows.append(_row)

                            _tot = {"योगदानकर्ता (Contributor)": "कुल बिन्दु (BAV Total)"}
                            for _idx, _sname in enumerate(_sign_names):
                                _col_title = f"{_sname[:3]} ({_idx+1})"
                                _tot[_col_title] = _bav_total[_idx] if _idx < len(_bav_total) else sum(r.get("bindus", [0]*12)[_idx] for r in _grid_rows)
                            _tot["योग (Total)"] = sum(_bav_total) if _bav_total else sum(sum(r.get("bindus", [0]*12)) for r in _grid_rows)
                            _pr_rows.append(_tot)

                            st.dataframe(pd.DataFrame(_pr_rows), use_container_width=True, hide_index=True)
                            st.success(f"📌 **{_psel}** का कुल भिन्नाष्टकवर्ग (BAV) योग: **{_tot['योग (Total)']}** बिन्दु")
                else:
                    st.info("प्रस्तार डेटा उपलब्ध नहीं।")
        except Exception as _epr:
            st.error(f"प्रस्तार त्रुटि: {str(_epr)[:200]}")

    # =========================================================================
    # TAB 9: BHRIGU BINDU & SENSITIVE TRANSIT POINT
    # =========================================================================
    with tab_g9:
        st.markdown("### 🔵 भृगु बिन्दु एवं संवेदनशील गोचर वेध (Bhrigu Bindu)")
        st.caption("राहु और चन्द्रमा का स्पष्ट मध्य बिन्दु — जब कोई ग्रह इस बिन्दु पर या ५° की परिधि में गोचर करता है, तो जीवन में बड़ी नियति-घटना घटित होती है:")
        try:
            import src.jyotish.core.ashtakavarga as ak_mod
            _bb = ak_mod.AshtakavargaCalculator.calculate_bhrigu_bindu(chart)
            if _bb:
                _bbc1, _bbc2, _bbc3 = st.columns(3)
                _bbc1.metric("🔵 देशांतर (Longitude)", f"{_bb.get('longitude', 0):.2f}°")
                _bbc2.metric("🌌 राशि (Sign)", _bb.get('sign_name', '—'))
                _bbc3.metric("⭐ नक्षत्र (Nakshatra)", _bb.get('nakshatra', '—'))

                st.markdown(f"""<div style="background:#EFF6FF; border:1.5px solid #3B82F6; border-radius:10px; padding:12px; margin:12px 0;">
    📐 <b>भृगु बिन्दु सूत्र:</b> (राहु {chart.planets['Rahu'].longitude:.2f}° + चन्द्र {chart.planets['Moon'].longitude:.2f}°) ÷ २ = <b>{_bb.get('longitude', 0):.4f}°</b> | लग्न से भाव: <b>भाव {_bb.get('house_from_lagna', '—')}</b>
    </div>""", unsafe_allow_html=True)

                _bb_lon = _bb.get('longitude', 0)
                _near_natal = [{"ग्रह (Natal)": pn, "देशांतर": f"{pp.longitude:.2f}°", "अंतर": f"{abs((pp.longitude - _bb_lon + 180) % 360 - 180):.2f}°"} for pn, pp in chart.planets.items() if abs((pp.longitude - _bb_lon + 180) % 360 - 180) < 5]
                _near_transit = [{"ग्रह (Transit)": pn, "देशांतर": f"{pp.longitude:.2f}°", "अंतर": f"{abs((pp.longitude - _bb_lon + 180) % 360 - 180):.2f}°"} for pn, pp in t_chart.planets.items() if abs((pp.longitude - _bb_lon + 180) % 360 - 180) < 5]

                c_bb1, c_bb2 = st.columns(2)
                with c_bb1:
                    st.markdown("##### 📍 जन्म कुण्डली के ग्रह (Natal Planets near BB):")
                    if _near_natal:
                        st.dataframe(pd.DataFrame(_near_natal), use_container_width=True, hide_index=True)
                    else:
                        st.success("✅ जन्म कुण्डली में कोई ग्रह भृगु बिन्दु के ५° के भीतर नहीं है।")
                with c_bb2:
                    st.markdown("##### ⚡ तात्कालिक गोचर ग्रह (Transit Planets near BB):")
                    if _near_transit:
                        st.warning("⚠️ निम्न गोचर ग्रह भृगु बिन्दु के ५° के भीतर संचरण कर रहे हैं:")
                        st.dataframe(pd.DataFrame(_near_transit), use_container_width=True, hide_index=True)
                    else:
                        st.success("✅ वर्तमान गोचर में कोई ग्रह भृगु बिन्दु के अति-समीप नहीं है।")
        except Exception as _ebb:
            st.error(f"भृगु बिन्दु गणना त्रुटि: {str(_ebb)[:200]}")

    # =========================================================================
    # TAB 10: SARVATOBHADRA 9x9 VEDHA MATRIX
    # =========================================================================
    with tab_g10:
        st.markdown("#### 🛡️ सर्वतोभद्र चक्र (9x9 Sarvatobhadra Vedha Matrix)")
        st.caption("२८ नक्षत्र (अभिजित सहित), १२ राशियां, स्वर, तिथियां एवं संवेदनशील नक्षत्रों पर सम्मुख व तिर्यक गोचर वेध:")

        sbc_res = default_sarvatobhadra_engine.calculate(chart, t_chart)
        sbc_grid = sbc_res["grid_layout"]
        grid_html = '<div style="overflow-x: auto; border: 1.5px solid #CBD5E1; border-radius: 10px; padding: 10px; background: #FFFFFF; box-shadow: 0 2px 8px rgba(0,0,0,0.04); margin-bottom: 16px;">'
        grid_html += '<table style="margin: 0 auto; border-collapse: collapse; text-align: center; font-size: 11.5px;">'

        for row_idx, row in enumerate(sbc_grid):
            grid_html += '<tr>'
            for col_idx, (c_type, c_val) in enumerate(row):
                bg_col = "#FFFFFF"
                fg_col = "#0F172A"
                border_col = "#E2E8F0"
                font_weight = "600"

                if c_type == "center":
                    bg_col = "#FEF3C7"
                    fg_col = "#78350F"
                    font_weight = "900"
                    border_col = "#D97706"
                elif c_type == "nak":
                    if c_val == sbc_res["janma_nakshatra_28"]:
                        bg_col = "#DCFCE7"
                        fg_col = "#166534"
                        font_weight = "900"
                        border_col = "#10B981"
                    else:
                        bg_col = "#F0FDF4"
                        fg_col = "#15803D"
                elif c_type == "rashi":
                    bg_col = "#EFF6FF"
                    fg_col = "#1E40AF"
                    font_weight = "700"
                elif c_type == "vowel":
                    bg_col = "#FFFBEB"
                    fg_col = "#92400E"
                elif c_type == "tithi":
                    bg_col = "#F8FAFC"
                    fg_col = "#475569"
                elif c_type == "dir":
                    bg_col = "#F1F5F9"
                    fg_col = "#0F172A"
                    font_weight = "800"

                grid_html += f'<td style="padding: 7px 8px; border: 1px solid {border_col}; background: {bg_col}; color: {fg_col}; font-weight: {font_weight}; min-width: 48px; max-width: 90px; height: 36px; white-space: nowrap;">{c_val}</td>'
            grid_html += '</tr>'
        grid_html += '</table></div>'
        st.markdown(grid_html, unsafe_allow_html=True)

        col_sb_v1, col_sb_v2 = st.columns([1.2, 1.8])
        with col_sb_v1:
            st.markdown("#### ⚡ सक्रिय गोचर वेध (Active Vedhas)")
            if sbc_res["vedhas"]:
                v_df = pd.DataFrame(sbc_res["vedhas"])
                st.dataframe(v_df[["planet", "planet_nak", "target_point", "vedha_type", "impact"]], use_container_width=True)
            else:
                st.success("✅ कोई प्रत्यक्ष अनिष्टकारी वेध सक्रिय नहीं है।")

        with col_sb_v2:
            st.markdown("#### 🎯 जातक के 16 संवेदनशील नक्षत्र (Sensitive Points)")
            sp_df = pd.DataFrame(sbc_res["sensitive_points"])
            st.dataframe(sp_df[["hi_name", "nakshatra", "desc"]], use_container_width=True)

    # =========================================================================
    # TAB 11: KOTA CHAKRA 4-ZONE FORTRESS
    # =========================================================================
    with tab_g11:
        st.markdown("#### 🏰 कोटा चक्र (Kota Chakra 4-Zone Durga Fortress)")
        st.caption("जन्म नक्षत्र आधारित ४-क्षेत्रीय दुर्ग (स्तम्भ, मध्य, प्राकार, बाह्य) एवं गोचर ग्रहों के प्रवेश/निर्गम द्वारा रक्षा व संकट का मूल्यांकन:")

        kota_res = default_kota_chakra_engine.calculate(chart, t_chart)
        st.markdown(f"""<div style="background:#FFFFFF; border:1.5px solid #2563EB; border-radius:10px; padding:16px; margin-bottom:16px; box-shadow:0 2px 8px rgba(0,0,0,0.04);">
    <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px; margin-bottom:8px;">
    <div>
    <span style="font-size:16px; font-weight:900; color:#1E40AF;">🛡️ कोटा स्वामी: <b>{kota_res['kota_swami']}</b></span>
    &nbsp;&nbsp;|&nbsp;&nbsp;
    <span style="font-size:16px; font-weight:900; color:#0F766E;">⚔️ कोटा पाल: <b>{kota_res['kota_pala']}</b></span>
    </div>
    <div style="font-size:13px; font-weight:800; background:#EFF6FF; color:#1E40AF; border:1.5px solid #3B82F6; border-radius:8px; padding:4px 10px;">
    {kota_res['defense_status']}
    </div>
    </div>
    <div style="font-size:13px; color:#1E293B; line-height:1.6;">
    📜 <b>दुर्ग स्थिति विश्लेषण:</b> {kota_res['defense_summary']}
    </div>
    </div>""", unsafe_allow_html=True)

        try:
            import src.jyotish.ui.chart_renderer as cr_mod
            kota_svg_m10 = cr_mod.ChartRenderer.render_kota_chakra_svg(kota_res, title=f"कोटा चक्र दुर्ग आरेख (Kota Chakra — {t_date.strftime('%d-%b-%Y')})")
            st.markdown(kota_svg_m10, unsafe_allow_html=True)
            st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
        except Exception as _ekc:
            pass

        col_kt1, col_kt2 = st.columns(2)
        with col_kt1:
            st.markdown("#### 🪐 गोचर ग्रहों का दुर्ग में स्थान व गति")
            st.dataframe(pd.DataFrame(kota_res["planet_allocations"]), use_container_width=True)
        with col_kt2:
            st.markdown("#### 🏰 कोटा चक्र के ४ क्षेत्र एवं नक्षत्र विभाजन")
            zone_data = [{"क्षेत्र (Zone)": z_name, "समाहित नक्षत्र (Nakshatras)": ", ".join(nak_list)} for z_name, nak_list in kota_res["zones_map"].items()]
            st.dataframe(pd.DataFrame(zone_data), use_container_width=True)

    # =========================================================================
    # TAB 12: FINANCIAL ASTROLOGY & COMMODITY TRADER
    # =========================================================================
    with tab_g12:
        st.markdown("#### 📈 वित्तीय ज्योतिष, कमोडिटी एवं शेयर बाज़ार वेध (Financial Astrology & Trader Radar)")
        st.caption("बृहत्संहिता, नारद संहिता एवं सर्वतोभद्र चक्र वेध अनुसार स्वर्ण, चांदी, कच्चा तेल, धातु, निफ्टी/इक्विटी का बाजार रुख एवं जातक की व्यक्तिगत ट्रेडिंग/निवेश कुण्डली:")

        try:
            import src.jyotish.services.financial as fin_mod
            fin_service = fin_mod.default_financial_service

            c_f_radar, c_f_personal = st.tabs([
                "🌐 बाज़ार कमोडिटी व शेयर वेध राडार (Market Trends)",
                "👤 जातक व्यक्तिगत ट्रेडिंग व निवेश कुण्डली (Personal Wealth & Trading)"
            ])

            with c_f_radar:
                st.markdown("##### 🪙 प्रमुख कमोडिटी व शेयर बाज़ार तात्कालिक वेध रुझान:")
                comm_trends = fin_service.analyze_commodity_market_trends(t_chart)
                c_c1, c_c2 = st.columns(2)
                for idx, c_item in enumerate(comm_trends):
                    target_col = c_c1 if idx % 2 == 0 else c_c2
                    with target_col:
                        st.markdown(f"""<div style="background:#F8FAFC; border:1.5px solid #CBD5E1; border-left:5px solid {c_item['badge_color']}; border-radius:10px; padding:12px 14px; margin-bottom:12px; box-shadow:0 1px 3px rgba(0,0,0,0.04);">
    <div style="display:flex; justify-content:space-between; align-items:center;">
    <b style="font-size:14.5px; color:#0F172A;">{c_item['icon']} {c_item['commodity']}</b>
    <span style="background:#FFFFFF; color:{c_item['badge_color']}; border:1.5px solid {c_item['badge_color']}; padding:2px 8px; border-radius:10px; font-size:11.5px; font-weight:800;">{c_item['trend']}</span>
    </div>
    <div style="font-size:12px; color:#475569; margin-top:4px;">{c_item['description']}</div>
    <div style="font-size:11.5px; color:#1E40AF; margin-top:4px; font-weight:600;">🎯 संवेदनशील नक्षत्र: {c_item['sensitive_nakshatras']}</div>
    <div style="background:#FFFFFF; border:1px solid #E2E8F0; border-radius:6px; padding:6px 10px; margin-top:8px; font-size:12px; color:#334155;">
    <b>🔍 वेध शास्त्रीय कारण:</b> {' | '.join(c_item['reasons'])}
    </div>
    </div>""", unsafe_allow_html=True)

            with c_f_personal:
                st.markdown("##### 👤 जातक की कुण्डली अनुसार व्यक्तिगत निवेश व ट्रेडिंग अनुकूलता:")
                p_wealth = fin_service.evaluate_personal_wealth_and_trading(chart)
                col_pw1, col_pw2, col_pw3, col_pw4 = st.columns(4)
                col_pw1.metric("⚡ डे ट्रेडिंग / इंट्राडे", f"{p_wealth['day_trading_score']}%", "अल्पकालिक सट्टा")
                col_pw2.metric("📈 दीर्घकालिक शेयर निवेश", f"{p_wealth['long_term_score']}%", "म्यूचुअल फंड्स")
                col_pw3.metric("🏛️ रियल एस्टेट / भूमि", f"{p_wealth['property_score']}%", "अचल संपत्ति")
                col_pw4.metric("🪙 स्वर्ण व सॉवरेन बॉन्ड", f"{p_wealth['gold_score']}%", "कीमती धातु")

                st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
                for adv in p_wealth["strategic_advice"]:
                    st.info(adv)
        except Exception as _efin:
            st.error(f"वित्तीय ज्योतिष गणना त्रुटि: {str(_efin)[:300]}")

    # =========================================================================
    # TAB 13: PLANETARY SPEEDS & 5-YEAR EPHEMERIS WAVES
    # =========================================================================
    with tab_g13:
        sub_spd, sub_wave = st.tabs([
            "⚡ अल्पकालिक ग्रह गति व मोड़ बिंदु (Speed & Stations)",
            "📈 ५-वर्षीय बहु-ग्रहीय वेव व राशि संक्रमण (5-Year Ephemeris Waves)"
        ])

        with sub_spd:
            st.markdown("### 📊 डायनेमिक गोचर गति व वक्रता वक्र (Dynamic Planetary Speed & Retrograde Curves)")
            st.caption("ग्रहों की दैनिक कोणीय गति (°/दिन), वक्र-मार्गी मोड़ बिंदु (Stationary Points), अतिचार व मन्द गति का शास्त्रीय दृश्य वक्र:")

            from src.jyotish.services.transit_graph import default_transit_graph_service, PLANET_NAMES_HI, PLANET_COLORS
            col_sp1, col_sp2, col_sp3 = st.columns([1.5, 1.5, 3])
            with col_sp1:
                spd_start_date = st.date_input("आरंभिक तिथि (Start Date)", value=t_date, key="spd_start_d_14tab")
            with col_sp2:
                spd_days = st.selectbox("अवधि (Time Horizon)", [30, 60, 90, 180, 365], index=2, format_func=lambda x: f"{x} दिन", key="spd_days_sel_14tab")
            with col_sp3:
                all_pl_opts = ["Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Sun", "Moon", "Rahu"]
                spd_planets = st.multiselect("ग्रह चयन (Select Planets)", all_pl_opts, default=["Mars", "Mercury", "Jupiter", "Venus", "Saturn"], format_func=lambda x: PLANET_NAMES_HI.get(x, x), key="spd_pl_sel_14tab")

            if not spd_planets:
                spd_planets = ["Mars", "Mercury", "Jupiter", "Venus", "Saturn"]

            with st.spinner("ग्रह गति वक्र की खगोलीय गणना जारी..."):
                spd_res = default_transit_graph_service.calculate_speed_timeline(spd_start_date, days=spd_days, planet_names=spd_planets)

            spd_svg = default_transit_graph_service.render_speed_svg(spd_res)
            st.markdown(spd_svg, unsafe_allow_html=True)

            st.markdown("---")
            st.markdown("#### ⚡ तात्कालिक ग्रह गति एवं खगोलीय स्थिति (Current Motion Status):")
            cols_st = st.columns(len(spd_planets))
            for idx, p in enumerate(spd_planets):
                info = spd_res["current_status"].get(p)
                if info:
                    with cols_st[idx]:
                        st.metric(
                            info["planet_hi"].split(" ")[0],
                            f"{info['speed']:+.3f}°/दिन",
                            f"{info['status'].split(' ')[0]} ({info['sign']})"
                        )

            st.markdown("#### 🔄 आगामी वक्र/मार्गी मोड़ बिंदु (Upcoming Stationary Turning Points):")
            if spd_res.get("turning_points"):
                tp_rows = []
                for tp in spd_res["turning_points"]:
                    tp_rows.append({
                        "दिनांक (Date)": tp["date"],
                        "ग्रह (Planet)": tp["planet_hi"],
                        "परिवर्तन (Event)": tp["shift_type"],
                        "गोचर राशि (Sign)": tp["sign"],
                        "स्पष्ट अंश (Degree)": tp["degree_str"],
                        "गति (Speed)": f"{tp['speed']:+.4f}°/दिन"
                    })
                st.dataframe(pd.DataFrame(tp_rows), use_container_width=True, hide_index=True)
            else:
                st.info("💡 चुने गए कालखंड में किसी चयनित ग्रह के वक्र/मार्गी मोड़ बिंदु (Zero Crossing) नहीं हैं।")

        with sub_wave:
            st.markdown("### 📈 ५-वर्षीय बहु-ग्रहीय वेव आरेख व राशि संक्रमण (5-Year Ephemeris Waves)")
            st.caption("शास्त्रीय ५-वर्षीय दीर्घकालिक गोचर वेव आरेख — शनि, गुरु, राहु एवं मंगल के राशि संचरण, वक्र-मार्गी दोलन (Retrograde Loops) एवं राशि संक्रमण (Ingress):")

            try:
                import src.jyotish.services.ephemeris_waves as ew_mod
                ew_svc = ew_mod.default_ephemeris_waves_service

                c_w1, c_w2 = st.columns([1.5, 3])
                with c_w1:
                    w_start_year = st.selectbox("आरंभिक वर्ष (Start Year)", [2024, 2025, 2026, 2027, 2028, 2029, 2030], index=2, key="ew_start_yr_14tab")
                with c_w2:
                    w_duration = st.slider("अवधि (Duration in Years)", min_value=2, max_value=7, value=5, step=1, key="ew_duration_yr_14tab")

                with st.spinner("५-वर्षीय खगोलीय वेव चक्र एवं राशि परिवर्तन की गणना जारी..."):
                    waves_data = ew_svc.generate_multi_year_waves(start_year=w_start_year, duration_years=w_duration)
                    waves_svg = ew_svc.render_waves_svg_html(start_year=w_start_year, duration_years=w_duration)

                st.markdown(waves_svg.strip(), unsafe_allow_html=True)

                col_we1, col_we2 = st.columns(2)
                with col_we1:
                    st.markdown("#### 🔄 आगामी वक्री-मार्गी चक्र (Upcoming Retrograde Intervals)")
                    if waves_data.get("retrograde_events"):
                        r_rows = []
                        for rev in waves_data["retrograde_events"][:12]:
                            r_rows.append({
                                "ग्रह": rev["planet_hi"],
                                "वक्री आरंभ": rev["retro_start"],
                                "मार्गी वापसी": rev["direct_date"],
                                "अवधि": f"{rev['duration_days']} दिन",
                                "राशि": rev["sign"]
                            })
                        st.dataframe(pd.DataFrame(r_rows), use_container_width=True, hide_index=True)
                    else:
                        st.info("इस कालखंड में कोई वक्री चक्र नहीं है।")

                with col_we2:
                    st.markdown("#### 🚪 आगामी प्रमुख राशि संक्रमण (Upcoming Rashi Ingress)")
                    if waves_data.get("ingress_events"):
                        ing_rows = []
                        for ing in waves_data["ingress_events"][:12]:
                            ing_rows.append({
                                "दिनांक": ing["date"],
                                "ग्रह": ing["planet_hi"],
                                "पूर्व राशि": ing["from_sign"],
                                "प्रवेश राशि": f"➡️ {ing['to_sign']}",
                            })
                        st.dataframe(pd.DataFrame(ing_rows), use_container_width=True, hide_index=True)
                    else:
                        st.info("इस कालखंड में कोई राशि संक्रमण नहीं है।")
            except Exception as _e_ew:
                st.error(f"Ephemeris Waves गणना त्रुटि: {_e_ew}")

    # =========================================================================
    # TAB 14: MONTHLY TRANSIT CALENDAR, RULES & REMEDIES
    # =========================================================================
    with tab_g14:
        st.markdown("### 📅 मासिक व्यक्तिगत गोचर पंचांग, नियम व वैदिक उपाय (Personal Transit Calendar & Remedies)")
        st.caption("मासिक कैलेंडर ग्रिड (१-५ स्टार रेटिंग), गोचर संक्रांतियां, बृहत्पाराशर होरा शास्त्र नियम एवं अशुभ गोचर शांति उपाय:")

        t_cal = default_transit_calendar_service
        if t_cal is None:
            from src.jyotish.services.transit_calendar import PersonalTransitCalendarService
            t_cal = PersonalTransitCalendarService()

        col_cal1, col_cal2 = st.columns(2)
        with col_cal1:
            cal_month = st.selectbox(
                "माह चुनें (Select Month)",
                list(range(1, 13)),
                index=get_live_local_now(tz_offset).month - 1,
                format_func=lambda x: datetime(2026, x, 1).strftime("%B"),
                key="cal_m_sel_14tab"
            )
        with col_cal2:
            cal_year = st.selectbox(
                "वर्ष चुनें (Select Year)",
                [2024, 2025, 2026, 2027, 2028, 2029, 2030],
                index=2,
                key="cal_y_sel_14tab"
            )

        with st.spinner("मासिक गोचर पंचांग व चंद्र शुद्धि की गणना जारी..."):
            cal_data = t_cal.generate_monthly_calendar(cal_year, cal_month, chart)

        days_5star = sum(1 for d in cal_data["days"] if d["stars"] == 5)
        days_4star = sum(1 for d in cal_data["days"] if d["stars"] == 4)
        days_caution = sum(1 for d in cal_data["days"] if d["stars"] <= 2)

        c_ck1, c_ck2, c_ck3, c_ck4 = st.columns(4)
        c_ck1.metric("उत्कृष्ट कार्य सिद्धि दिवस", f"{days_5star} दिन", "५-स्टार ⭐⭐⭐⭐⭐")
        c_ck2.metric("शुभ व सामान्य अनुकूल", f"{days_4star} दिन", "४-स्टार ⭐⭐⭐⭐")
        c_ck3.metric("सतर्कता दिवस (घात चंद्र)", f"{days_caution} दिन", "१-२ स्टार ⚠️")
        c_ck4.metric("ग्रह राशि परिवर्तन (Ingress)", f"{len(cal_data['ingress_events'])} घटनाएं", "संक्रांति")

        cal_html = t_cal.render_calendar_html(cal_data)
        st.components.v1.html(cal_html, height=760, scrolling=True)

        if cal_data["ingress_events"]:
            st.markdown("#### ⚡ इस माह में होने वाले मुख्य ग्रह राशि परिवर्तन (Planetary Ingresses):")
            ing_df = pd.DataFrame(cal_data["ingress_events"]).rename(columns={
                "date": "दिनांक", "planet": "ग्रह", "sign": "प्रवेश राशि", "house": "जातक का भाव", "event": "घटना विवरण"
            })
            st.dataframe(ing_df, use_container_width=True, hide_index=True)

        st.markdown("---")
        with st.expander("📖 बृहत्पाराशर होरा शास्त्र (BPHS) गोचर एवं अष्टकवर्ग शास्त्रीय नियम", expanded=True):
            st.markdown("""**१. गोचर फलादेश का मूल आधार (BPHS Ch. 66):**
    > *चन्द्रादुपचयस्थाने गोचरे शुभदा ग्रहाः। त्रियायेकादशे सौम्याः क्रूराश्चापि तथैव च॥*
    > *गोचर का विचार सदैव जन्म लग्न के साथ-साथ जन्म चन्द्र राशि से भी किया जाना चाहिए। उपचय भावों (३, ६, १०, ११) में क्रूर ग्रह भी उत्तम फल प्रदान करते हैं।*

    **२. अष्टकवर्ग की सर्वोच्चता:**
    > *अष्टकवर्गं प्रवक्ष्यामि नराणां प्रीतिवर्धनम्। यस्य विज्ञानमात्रेण शुभाशुभफलं विदुः॥*
    > यदि कोई ग्रह गोचर में शुभ भाव में हो, परंतु उस भाव में अष्टकवर्ग बिन्दु २८ से कम हों, तो वह शुभ फल नहीं दे पाता। इसके विपरीत, अशुभ भाव में भी यदि ३०+ बिन्दु हों, तो अनिष्ट का निवारण हो जाता है।

    **३. गोचर वेध नियम (Obstructed Transits):**
    > जब कोई ग्रह अपने शुभ भाव में गोचर कर रहा हो, और उसी समय कोई अन्य ग्रह उसके वेध भाव में आ जाए, तो उसका शुभ फल अवरुद्ध (प्रतिबंधित) हो जाता है (सूर्य-शनि और चन्द्र-बुध के परस्पर वेध को छोड़कर)।""")

        with st.expander("🪔 गोचर पीड़ा निवारण एवं वैदिक शास्त्रीय उपाय (Transit Remedies)", expanded=True):
            st.markdown("""##### 🪐 शनि गोचर (साढ़ेसाती व ढैया) शांति अनुष्ठान:
    - 📿 **मंत्र:** `ॐ शं शनैश्चराय नमः` अथवा `ॐ प्रां प्रीं प्रौं सः शनैश्चराय नमः` (प्रतिदिन १०८ जप)
    - 🪔 **दीपदान:** शनिवार संध्याकाल में पीपल वृक्ष की जड़ में सरसों के तेल का दीपक प्रज्वलित करें।
    - 🎁 **दान:** काले उड़द, काला तिल, लोहा, सरसों का तेल, काला कंबल किसी जरूरतमंद को दान करें।

    ##### 🪐 गुरु गोचर प्रतिकूलता निवारण:
    - 📿 **मंत्र:** `ॐ बृं बृहस्पतये नमः` (१०८ जप)
    - 🎁 **दान:** चने की दाल, हल्दी, पीला वस्त्र, केसर अथवा धार्मिक पुस्तकों का दान।

    ##### 🐉 राहु-केतु गोचर संक्रांति उपाय:
    - 📿 **मंत्र:** `ॐ भ्रां भ्रीं भ्रौं सः राहवे नमः` / `ॐ स्रां स्रीं स्रौं सः केतवे नमः`
    - 🛕 **स्तोत्र:** श्री दुर्गा सप्तशती का पाठ अथवा भैरव कवच। पक्षियों को बाजरा/सप्तधान्य डालें।""")

    # -------------------------------------------------------------------------
    # TRANSIT CONTINUOUS AUTOPLAY LOOP HANDLER
    # -------------------------------------------------------------------------
    if st.session_state.get("transit_autoplay", False):
        import time
        time.sleep(0.7)
        step_choice = st.session_state.get("transit_play_step_choice", "+1 दिन")
        if "घंटा" in step_choice:
            delta = timedelta(hours=1)
        elif "सप्ताह" in step_choice:
            delta = timedelta(days=7)
        elif "माह" in step_choice:
            delta = timedelta(days=30)
        else:
            delta = timedelta(days=1)
        comb = datetime.combine(st.session_state.t_manual_date, st.session_state.t_manual_time)
        new_dt = comb + delta
        st.session_state.t_manual_date = new_dt.date()
        st.session_state.t_manual_time = new_dt.time().replace(microsecond=0)
        st.rerun()



