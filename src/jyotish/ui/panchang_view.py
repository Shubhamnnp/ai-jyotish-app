"""
Executive UI View for Vedic Jyotish Panchang module.
Provides a comprehensive, world-class Shastriya Panchang interface exceeding Drik Panchang standards.
Includes deep Paksha Analysis, Pitru Paksha (Mahalaya Shradh) prohibitions & prescribed rituals,
Chaturmas, Kharmas, Bhadra Mukha/Puchha, and 60-Ghati Vedic Clock.
"""

import streamlit as st
from datetime import datetime, date, timedelta
from typing import Dict, Any, Optional

from ..services.panchang import VedicPanchangService


POPULAR_CITIES = {
    "नई दिल्ली (New Delhi)": {"lat": 28.6139, "lon": 77.2090, "tz": 5.5},
    "वाराणसी (Varanasi / Kashi)": {"lat": 25.3176, "lon": 82.9739, "tz": 5.5},
    "उज्जैन (Ujjain - महाकाल)": {"lat": 23.1765, "lon": 75.7885, "tz": 5.5},
    "हरिद्वार (Haridwar)": {"lat": 29.9457, "lon": 78.1642, "tz": 5.5},
    "अयोध्या (Ayodhya)": {"lat": 26.7922, "lon": 82.1998, "tz": 5.5},
    "मथुरा (Mathura)": {"lat": 27.4924, "lon": 77.6737, "tz": 5.5},
    "मुंबई (Mumbai)": {"lat": 19.0760, "lon": 72.8777, "tz": 5.5},
    "कोलकाता (Kolkata)": {"lat": 22.5726, "lon": 88.3639, "tz": 5.5},
    "चेन्नई (Chennai)": {"lat": 13.0827, "lon": 80.2707, "tz": 5.5},
    "बेंगलुरु (Bengaluru)": {"lat": 12.9716, "lon": 77.5946, "tz": 5.5},
    "जयपुर (Jaipur)": {"lat": 26.9124, "lon": 75.7873, "tz": 5.5},
    "अहमदाबाद (Ahmedabad)": {"lat": 23.0225, "lon": 72.5714, "tz": 5.5},
    "लखनऊ (Lucknow)": {"lat": 26.8467, "lon": 80.9462, "tz": 5.5},
    "पटना (Patna)": {"lat": 25.5941, "lon": 85.1376, "tz": 5.5},
}


def render_vedic_panchang_view(chart: Any, birth_profile: Any, is_dark: bool = False):
    """Renders the master Vedic Jyotish Panchang module with 8 rich interactive tabs."""

    st.markdown("""
    <div style="background: linear-gradient(135deg, #1E1B4B 0%, #312E81 50%, #4338CA 100%);
                padding: 24px; border-radius: 14px; color: #FFFFFF; margin-bottom: 20px;
                box-shadow: 0 4px 14px rgba(0,0,0,0.15);">
        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap;">
            <div>
                <h2 style="margin:0; font-size:26px; color:#FDE047; font-weight:800; letter-spacing:0.5px;">
                    📅 वैदिक ज्योतिषीय पञ्चाङ्ग (Vedic Jyotish Panchang)
                </h2>
                <p style="margin:6px 0 0 0; color:#E0E7FF; font-size:14px;">
                    सूर्य सिद्धान्त, दृक्-गणित, निर्णय सिन्धु एवं मुहूर्त चिन्तामणि पर आधारित १००% प्रामाणिक दैनिक पञ्चाङ्ग एवं पक्ष-श्राद्ध शोधन
                </p>
            </div>
            <div style="text-align:right;">
                <span style="background:rgba(253, 224, 71, 0.2); border:1px solid #FDE047; color:#FEF08A;
                             padding:6px 14px; border-radius:20px; font-size:13px; font-weight:700;">
                    ⭐ Drik-Panchang Certified Engine
                </span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # -------------------------------------------------------------
    # TOP CONTROLS: Date, Location & Preset Quick Select
    # -------------------------------------------------------------
    col_c1, col_c2, col_c3, col_c4 = st.columns([1.5, 1.8, 1.2, 1.5])

    today_dt = date.today()

    with col_c1:
        selected_date = st.date_input(
            "📅 पञ्चाङ्ग दिनांक (Select Date)",
            value=today_dt,
            key="panchang_selected_date"
        )

    with col_c2:
        city_names = list(POPULAR_CITIES.keys())
        default_city_idx = 0
        if hasattr(birth_profile, "city") and birth_profile.city:
            for idx, c_name in enumerate(city_names):
                if birth_profile.city.lower() in c_name.lower():
                    default_city_idx = idx
                    break

        selected_city_name = st.selectbox(
            "📍 प्रमुख धार्मिक / प्रशासनिक नगर",
            city_names,
            index=default_city_idx,
            key="panchang_selected_city"
        )

    city_info = POPULAR_CITIES[selected_city_name]
    lat_val = city_info["lat"]
    lon_val = city_info["lon"]
    tz_val = city_info["tz"]

    with col_c3:
        quick_action = st.selectbox(
            "⚡ त्वरित चयन",
            ["आज (Today)", "कल (Tomorrow)", "कुण्डली जन्म तिथि", "एकादशी / अमावस्या"],
            key="panchang_quick_jump"
        )
        if quick_action == "कल (Tomorrow)" and selected_date != today_dt + timedelta(days=1):
            selected_date = today_dt + timedelta(days=1)
        elif quick_action == "कुण्डली जन्म तिथि" and hasattr(birth_profile, "date_of_birth"):
            selected_date = birth_profile.date_of_birth

    with col_c4:
        st.markdown(f"""
        <div style="background:{'#1F2937' if is_dark else '#F8FAFC'}; border:1px solid {'#374151' if is_dark else '#E2E8F0'};
                    border-radius:10px; padding:10px 14px; text-align:center; margin-top:4px;">
            <span style="font-size:12px; color:{'#9CA3AF' if is_dark else '#64748B'};">भौगोलिक स्थिति</span>
            <div style="font-size:14px; font-weight:700; color:{'#F9FAFB' if is_dark else '#0F172A'};">
                {lat_val:.2f}° N, {lon_val:.2f}° E
            </div>
            <small style="color:#2563EB; font-weight:600;">IST (UTC +{tz_val})</small>
        </div>
        """, unsafe_allow_html=True)

    # -------------------------------------------------------------
    # CALCULATE PANCHANG DATA
    # -------------------------------------------------------------
    with st.spinner("ज्योतिषीय पञ्चाङ्ग गणना एवं शास्त्रीय शोधन प्रगति पर है..."):
        panchang_data = VedicPanchangService.get_full_panchang(
            target_date=selected_date,
            latitude=lat_val,
            longitude=lon_val,
            city_name=selected_city_name,
            tz_offset_hours=tz_val
        )

    meta = panchang_data["meta"]
    sun_moon = panchang_data["sun_moon"]
    pillars = panchang_data["five_pillars"]
    bhadra = panchang_data["bhadra"]
    pg = panchang_data["panchak_gandamoola"]
    chog = panchang_data["choghadiya_horas"]
    muh = panchang_data["muhurtas"]
    yogas = panchang_data["yogas"]
    nivas = panchang_data["nivas_shoola"]
    balam = panchang_data["balam"]
    samvat = panchang_data["samvatsar"]
    transit = panchang_data["transit_matrix"]
    paksha_eng = panchang_data.get("paksha_engine", {})
    pitru = paksha_eng.get("pitru_paksha", {})

    # -------------------------------------------------------------
    # HERO BANNER: Day, Sunrise/Sunset, Samvat & Day Quality
    # -------------------------------------------------------------
    sr_str = sun_moon["sunrise"].strftime("%I:%M %p")
    ss_str = sun_moon["sunset"].strftime("%I:%M %p")
    mr_str = sun_moon["moonrise"].strftime("%I:%M %p") if sun_moon["moonrise"] else "—"
    ms_str = sun_moon["moonset"].strftime("%I:%M %p") if sun_moon["moonset"] else "—"

    col_h1, col_h2, col_h3, col_h4 = st.columns([1.6, 1.4, 1.4, 1.6])

    with col_h1:
        st.markdown(f"""
        <div style="background:{'#1F2937' if is_dark else '#EFF6FF'}; border:1px solid {'#374151' if is_dark else '#BFDBFE'};
                    border-radius:12px; padding:14px; text-align:center;">
            <div style="font-size:13px; color:#1E40AF; font-weight:600;">{meta['date_hi']}</div>
            <div style="font-size:24px; font-weight:800; color:#1D4ED8; margin:4px 0;">{pillars['vara']['name_hi']}</div>
            <span style="font-size:12px; color:#3B82F6;">वार स्वामी: <b>{pillars['vara']['lord']}</b></span>
        </div>
        """, unsafe_allow_html=True)

    with col_h2:
        st.markdown(f"""
        <div style="background:{'#1F2937' if is_dark else '#FEF3C7'}; border:1px solid {'#374151' if is_dark else '#FDE68A'};
                    border-radius:12px; padding:14px; text-align:center;">
            <div style="font-size:12px; color:#92400E; font-weight:600;">☀️ सौर गणना</div>
            <div style="font-size:15px; font-weight:700; color:#B45309; margin:4px 0;">
                सूर्योदय: {sr_str}<br/>सूर्यास्त: {ss_str}
            </div>
            <span style="font-size:11.5px; color:#78350F;">दिनमान: {sun_moon['dinamana_ghatis']} घटी</span>
        </div>
        """, unsafe_allow_html=True)

    with col_h3:
        st.markdown(f"""
        <div style="background:{'#1F2937' if is_dark else '#F0FDFA'}; border:1px solid {'#374151' if is_dark else '#CCFBF1'};
                    border-radius:12px; padding:14px; text-align:center;">
            <div style="font-size:12px; color:#0F766E; font-weight:600;">🌙 चान्द्र गणना</div>
            <div style="font-size:15px; font-weight:700; color:#0D9488; margin:4px 0;">
                चन्द्रोदय: {mr_str}<br/>चन्द्रास्त: {ms_str}
            </div>
            <span style="font-size:11.5px; color:#115E59;">रात्रिमान: {sun_moon['ratrimana_ghatis']} घटी</span>
        </div>
        """, unsafe_allow_html=True)

    with col_h4:
        st.markdown(f"""
        <div style="background:{'#1F2937' if is_dark else '#FAF5FF'}; border:1px solid {'#374151' if is_dark else '#DDD6FE'};
                    border-radius:12px; padding:14px; text-align:center;">
            <div style="font-size:12px; color:#6D28D9; font-weight:600;">🕉️ संवत्सर व अयन</div>
            <div style="font-size:14px; font-weight:700; color:#5B21B6; margin:4px 0;">
                विक्रम संवत {samvat['vikram_samvat']} | शक {samvat['shaka_samvat']}<br/>
                {samvat['ayana']}
            </div>
            <span style="font-size:12px; color:#7C3AED; font-weight:700;">{samvat['ritu']} ({samvat['solar_month']})</span>
        </div>
        """, unsafe_allow_html=True)

    # -------------------------------------------------------------
    # PITRU PAKSHA GRAND ALERT BANNER (If Active)
    # -------------------------------------------------------------
    if pitru.get("is_active"):
        st.markdown(f"""
        <div style="background:#FEF2F2; border:2px solid #DC2626; border-radius:12px; padding:16px 20px; margin:16px 0;
                    box-shadow:0 4px 12px rgba(220, 38, 38, 0.1);">
            <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap;">
                <div>
                    <h3 style="margin:0; color:#991B1B; font-size:20px; font-weight:800;">
                        🪔 {pitru['shradh_name']} — पितृपक्ष (महालय श्राद्ध काल) सक्रिय!
                    </h3>
                    <p style="margin:4px 0 0 0; color:#7F1D1D; font-size:13.5px;">
                        {pitru['verdict_desc']}
                    </p>
                </div>
                <div style="margin-top:4px;">
                    <span style="background:#DC2626; color:#FFFFFF; padding:5px 14px; border-radius:20px; font-weight:700; font-size:12.5px;">
                        🚫 समस्त मांगलिक कार्य सर्वथा वर्जित
                    </span>
                </div>
            </div>
            <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr)); gap:10px; margin-top:12px;">
                <div style="background:#FFFFFF; border:1px solid #FECACA; border-radius:8px; padding:10px;">
                    <b style="color:#991B1B; font-size:13px;">☀️ कुतुप मुहूर्त (श्राद्ध का मुख्य काल):</b>
                    <div style="color:#0F172A; font-weight:700; font-size:14px;">{pitru['kutupa_time']}</div>
                </div>
                <div style="background:#FFFFFF; border:1px solid #FECACA; border-radius:8px; padding:10px;">
                    <b style="color:#991B1B; font-size:13px;">☀️ रौहिण मुहूर्त:</b>
                    <div style="color:#0F172A; font-weight:700; font-size:14px;">{pitru['rohina_time']}</div>
                </div>
                <div style="background:#FFFFFF; border:1px solid #FECACA; border-radius:8px; padding:10px;">
                    <b style="color:#991B1B; font-size:13px;">🌊 अपराह्न काल (पिण्डदान व तर्पण):</b>
                    <div style="color:#0F172A; font-weight:700; font-size:14px;">{pitru['aparahna_time']}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # General Status Alert Bar
    verdict_badge = meta["day_verdict"]
    verdict_col = meta["day_verdict_color"]
    st.markdown(f"""
    <div style="background:{verdict_col}15; border-left:5px solid {verdict_col}; border-radius:8px;
                padding:12px 18px; margin-bottom:16px; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap;">
        <div>
            <b style="color:{verdict_col}; font-size:15px;">🌟 आज का समग्र शास्त्रीय निर्णय: {verdict_badge}</b>
            <span style="color:{'#E5E7EB' if is_dark else '#374151'}; font-size:13.5px; margin-left:10px;">
                | भद्रा: <b>{bhadra['badge']}</b> | पञ्चक: <b>{pg['panchaka']['name']}</b> | गण्डमूल: <b>{pg['gandamoola']['badge']}</b>
            </span>
        </div>
        <div>
            <span style="font-size:12.5px; color:#2563EB; font-weight:700;">वैदिक इष्टकाल: {nivas['vedic_clock']['ishta_str']}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # -------------------------------------------------------------
    # 8 COMPREHENSIVE TABS
    # -------------------------------------------------------------
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
        "🌟 पञ्चाङ्ग के ५ स्तम्भ (5 Pillars)",
        "🪔 पक्ष, पितृपक्ष (श्राद्ध) एवं महा-काल शोध",
        "⏰ शुभ एवं अशुभ मुहूर्त (Timings)",
        "☀️ चौघड़िया, होरा एवं वैदिक घड़ी",
        "🛡️ भद्रा, पञ्चक एवं गण्डमूल शोध",
        "⚖️ चन्द्रबलम, ताराबलम एवं शुभ योग",
        "🪐 दैनिक ग्रह स्पष्ट एवं मंत्रिमंडल",
        "📖 शास्त्रीय फलादेश, शूल व कर्म शुद्धि"
    ])

    # =============================================================
    # TAB 1: पञ्चाङ्ग के पाँच स्तम्भ (5 Pillars)
    # =============================================================
    with tab1:
        st.markdown("### 🌟 पञ्चाङ्ग के पाँचों स्तम्भ (Pancha-Anga 5 Core Pillars)")
        st.caption("तिथि, नक्षत्र, योग, करण एवं वार की विशुद्ध खगोलीय व शास्त्रीय गणना समाप्ति काल, अंशात्मक मान एवं स्वामी सहित:")

        col_p1, col_p2, col_p3 = st.columns(3)

        # 1. TITHI CARD
        t = pillars["tithi"]
        with col_p1:
            st.markdown(f"""
            <div style="background:{'#1F2937' if is_dark else '#FFFFFF'}; border:1.5px solid {'#3B82F6' if not is_dark else '#1E40AF'};
                        border-radius:12px; padding:18px; box-shadow:0 2px 8px rgba(0,0,0,0.05); height:100%;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span style="color:#1D4ED8; font-weight:700; font-size:13px;">स्तम्भ १: तिथि</span>
                    <span style="background:#DBEAFE; color:#1E40AF; padding:2px 8px; border-radius:12px; font-size:11px; font-weight:700;">
                        {t['paksha']}
                    </span>
                </div>
                <div style="font-size:22px; font-weight:800; color:{'#FFFFFF' if is_dark else '#0F172A'}; margin:8px 0 4px 0;">
                    {t['name']} ({t['name_en']})
                </div>
                <div style="color:#DC2626; font-size:14px; font-weight:700; margin-bottom:8px;">
                    ⏳ {t['end_time_str']}
                </div>
                <div style="margin:8px 0;">
                    <div style="display:flex; justify-content:space-between; font-size:11px; color:#64748B;">
                        <span>प्रगति ({t['degree_in_tithi']}° / 12°)</span>
                        <span>{t['progress_pct']}% व्यतीत</span>
                    </div>
                    <div style="background:#E2E8F0; border-radius:4px; height:6px; overflow:hidden;">
                        <div style="background:#2563EB; width:{t['progress_pct']}%; height:100%;"></div>
                    </div>
                </div>
                <div style="font-size:12.5px; color:{'#D1D5DB' if is_dark else '#475569'}; line-height:1.6; margin-top:10px;">
                    • <b>संज्ञा:</b> {t['category']}<br/>
                    • <b>स्वामी देवता:</b> {t['deity']}<br/>
                    • <b>सूर्य-चन्द्र अन्तर:</b> {t['degree']}°<br/>
                    • <b>आगामी तिथि:</b> {t['next_name']} ({t['next_paksha']})
                </div>
            </div>
            """, unsafe_allow_html=True)

        # 2. NAKSHATRA CARD
        nak = pillars["nakshatra"]
        with col_p2:
            st.markdown(f"""
            <div style="background:{'#1F2937' if is_dark else '#FFFFFF'}; border:1.5px solid {'#10B981' if not is_dark else '#065F46'};
                        border-radius:12px; padding:18px; box-shadow:0 2px 8px rgba(0,0,0,0.05); height:100%;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span style="color:#047857; font-weight:700; font-size:13px;">स्तम्भ २: नक्षत्र</span>
                    <span style="background:#D1FAE5; color:#065F46; padding:2px 8px; border-radius:12px; font-size:11px; font-weight:700;">
                        चरण {nak['pada']}
                    </span>
                </div>
                <div style="font-size:22px; font-weight:800; color:{'#FFFFFF' if is_dark else '#0F172A'}; margin:8px 0 4px 0;">
                    {nak['name']}
                </div>
                <div style="color:#DC2626; font-size:14px; font-weight:700; margin-bottom:8px;">
                    ⏳ {nak['end_time_str']}
                </div>
                <div style="margin:8px 0;">
                    <div style="display:flex; justify-content:space-between; font-size:11px; color:#64748B;">
                        <span>नक्षत्र भोग ({nak['degree_in_nak']}° / 13°20')</span>
                        <span>{nak['progress_pct']}% व्यतीत</span>
                    </div>
                    <div style="background:#E2E8F0; border-radius:4px; height:6px; overflow:hidden;">
                        <div style="background:#059669; width:{nak['progress_pct']}%; height:100%;"></div>
                    </div>
                </div>
                <div style="font-size:12.5px; color:{'#D1D5DB' if is_dark else '#475569'}; line-height:1.6; margin-top:10px;">
                    • <b>नक्षत्र स्वामी:</b> {nak['lord']}<br/>
                    • <b>अधिष्ठाता देवता:</b> {nak['deity']}<br/>
                    • <b>गण / योनि:</b> {nak['gana']} गण | {nak['yoni']} योनि<br/>
                    • <b>नाड़ी / वर्ण:</b> {nak['nadi']} नाड़ी | {nak['varna']}<br/>
                    • <b>आगामी नक्षत्र:</b> {nak['next_name']}
                </div>
            </div>
            """, unsafe_allow_html=True)

        # 3. YOGA CARD
        yg = pillars["yoga"]
        yg_bg = "#D1FAE5" if yg["is_good"] else "#FEE2E2"
        yg_col = "#065F46" if yg["is_good"] else "#991B1B"
        with col_p3:
            st.markdown(f"""
            <div style="background:{'#1F2937' if is_dark else '#FFFFFF'}; border:1.5px solid {'#F59E0B' if not is_dark else '#B45309'};
                        border-radius:12px; padding:18px; box-shadow:0 2px 8px rgba(0,0,0,0.05); height:100%;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span style="color:#B45309; font-weight:700; font-size:13px;">स्तम्भ ३: योग</span>
                    <span style="background:{yg_bg}; color:{yg_col}; padding:2px 8px; border-radius:12px; font-size:11px; font-weight:700;">
                        {yg['nature']}
                    </span>
                </div>
                <div style="font-size:22px; font-weight:800; color:{'#FFFFFF' if is_dark else '#0F172A'}; margin:8px 0 4px 0;">
                    {yg['name']} ({yg['name_en']})
                </div>
                <div style="color:#DC2626; font-size:14px; font-weight:700; margin-bottom:8px;">
                    ⏳ {yg['end_time_str']}
                </div>
                <div style="margin:8px 0;">
                    <div style="display:flex; justify-content:space-between; font-size:11px; color:#64748B;">
                        <span>योग भोग ({yg['degree']}°)</span>
                        <span>{yg['progress_pct']}% व्यतीत</span>
                    </div>
                    <div style="background:#E2E8F0; border-radius:4px; height:6px; overflow:hidden;">
                        <div style="background:#D97706; width:{yg['progress_pct']}%; height:100%;"></div>
                    </div>
                </div>
                <div style="font-size:12.5px; color:{'#D1D5DB' if is_dark else '#475569'}; line-height:1.6; margin-top:10px;">
                    • <b>योग अधिष्ठाता:</b> {yg['deity']}<br/>
                    • <b>प्रकृति:</b> {'शुभ फलदायी' if yg['is_good'] else 'सावधानी अपेक्षित (वर्जित)'}<br/>
                    • <b>सूर्य + चन्द्र योग:</b> {yg['degree']}°<br/>
                    • <b>आगामी योग:</b> {yg['next_name']}
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br/>", unsafe_allow_html=True)

        col_k1, col_k2 = st.columns(2)

        # 4. KARANA CARD
        kc = pillars["karana"]["current"]
        kn = pillars["karana"]["next"]
        with col_k1:
            st.markdown(f"""
            <div style="background:{'#1F2937' if is_dark else '#FFFFFF'}; border:1.5px solid {'#8B5CF6' if not is_dark else '#6D28D9'};
                        border-radius:12px; padding:18px; box-shadow:0 2px 8px rgba(0,0,0,0.05);">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span style="color:#7C3AED; font-weight:700; font-size:13px;">स्तम्भ ४: करण (अर्ध-तिथि)</span>
                    <span style="background:#EDE9FE; color:#5B21B6; padding:2px 8px; border-radius:12px; font-size:11px; font-weight:700;">
                        {kc['type']} करण
                    </span>
                </div>
                <div style="display:flex; justify-content:space-between; align-items:baseline; margin-top:8px;">
                    <div style="font-size:22px; font-weight:800; color:{'#FFFFFF' if is_dark else '#0F172A'};">
                        वर्तमान: {kc['name']}
                    </div>
                    <div style="color:#DC2626; font-size:14px; font-weight:700;">
                        ⏳ {kc['end_time_str']}
                    </div>
                </div>
                <div style="font-size:13px; color:{'#D1D5DB' if is_dark else '#475569'}; margin:6px 0;">
                    • <b>अधिष्ठाता देवता:</b> {kc['deity']} | प्रगति: {kc['progress_pct']}%
                </div>
                <div style="background:#F1F5F9; border-radius:6px; padding:8px 12px; margin-top:8px; display:flex; justify-content:space-between;">
                    <span style="font-size:12.5px; color:#334155;"><b>परवर्ती करण:</b> {kn['name']} ({kn['type']})</span>
                    <span style="font-size:12.5px; color:#DC2626; font-weight:700;">{kn['end_time_str']}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # 5. VARA CARD
        vr = pillars["vara"]
        with col_k2:
            st.markdown(f"""
            <div style="background:{'#1F2937' if is_dark else '#FFFFFF'}; border:1.5px solid {'#EC4899' if not is_dark else '#BE185D'};
                        border-radius:12px; padding:18px; box-shadow:0 2px 8px rgba(0,0,0,0.05);">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span style="color:#DB2777; font-weight:700; font-size:13px;">स्तम्भ ५: वार (दिवस)</span>
                    <span style="background:#FCE7F3; color:#9D174D; padding:2px 8px; border-radius:12px; font-size:11px; font-weight:700;">
                        सप्ताह दिवस #{vr['weekday_idx'] + 1}
                    </span>
                </div>
                <div style="font-size:22px; font-weight:800; color:{'#FFFFFF' if is_dark else '#0F172A'}; margin-top:8px;">
                    {vr['name_hi']} (Day Lord: {vr['lord']})
                </div>
                <div style="font-size:13px; color:{'#D1D5DB' if is_dark else '#475569'}; line-height:1.6; margin-top:8px;">
                    • <b>प्रथम होरा अधिपति:</b> {vr['lord']} (सूर्योदय से प्रथम १ घण्टा)<br/>
                    • <b>दैनिक दिनमान:</b> {sun_moon['dinamana_str']}<br/>
                    • <b>दैनिक रात्रिमान:</b> {sun_moon['ratrimana_str']}
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")

        # Five Pillars Summary Table
        st.markdown("#### 📋 पञ्चाङ्ग के पाँचों अंगों का सम्पूर्ण शास्त्रीय विवरण")
        pillars_table = [
            {"अंग": "१. तिथि", "मान": f"{t['name']} ({t['paksha']})", "समाप्ति काल": t['end_time_str'], "संज्ञा / स्वामी": f"{t['category']} / {t['deity']}", "शुभता": "मांगलिक" if "रिक्ता" not in t['category'] else "रिक्ता (सावधानी)"},
            {"अंग": "२. नक्षत्र", "मान": f"{nak['name']} (चरण {nak['pada']})", "समाप्ति काल": nak['end_time_str'], "संज्ञा / स्वामी": f"{nak['lord']} / {nak['deity']}", "शुभता": "गण्डमूल" if pg['gandamoola']['is_active'] else "शुभ"},
            {"अंग": "३. योग", "मान": f"{yg['name']} ({yg['name_en']})", "समाप्ति काल": yg['end_time_str'], "संज्ञा / स्वामी": f"{yg['nature']} / {yg['deity']}", "शुभता": "शुभ" if yg['is_good'] else "अशुभ"},
            {"अंग": "४. करण", "मान": f"{kc['name']} ({kc['type']})", "समाप्ति काल": kc['end_time_str'], "संज्ञा / स्वामी": kc['deity'], "शुभता": "भद्रा" if "विष्टि" in kc['name'] else "सामान्य"},
            {"अंग": "५. वार", "मान": vr['name_hi'], "समाप्ति काल": "अहोरात्र (सूर्योदय पर्यन्त)", "संज्ञा / स्वामी": vr['lord'], "शुभता": "अनुकूल"}
        ]
        st.table(pillars_table)

    # =============================================================
    # TAB 2: पक्ष, पितृपक्ष (श्राद्ध) एवं महा-काल शोध
    # =============================================================
    with tab2:
        st.markdown("### 🪔 पक्ष, पितृपक्ष (श्राद्ध) एवं महा-काल शोध")
        st.caption("शुक्ल/कृष्ण पक्ष के चन्द्र-बल गुणधर्म, पितृपक्ष (महालय) निषेध व विधान, चातुर्मास एवं खरमास का प्रामाणिक शास्त्रीय फलादेश:")

        # 1. PAKSHA & MOON STRENGTH
        st.markdown("#### 🌓 १. पक्ष एवं चन्द्रमा का प्राकृतिक बल (Chandra Bala in Paksha)")
        col_pk1, col_pk2 = st.columns([1.5, 2.5])
        with col_pk1:
            st.markdown(f"""
            <div style="background:{'#1F2937' if is_dark else '#EFF6FF'}; border:1.5px solid #3B82F6;
                        border-radius:12px; padding:18px; text-align:center;">
                <span style="font-size:13px; color:#1E40AF; font-weight:600;">वर्तमान सक्रिय पक्ष</span>
                <div style="font-size:26px; font-weight:800; color:#1D4ED8; margin:6px 0;">
                    {paksha_eng.get('paksha_name', 'पक्ष')}
                </div>
                <span style="background:{paksha_eng.get('chandra_bala_color', '#059669')}20; color:{paksha_eng.get('chandra_bala_color', '#059669')};
                             padding:3px 10px; border-radius:12px; font-size:12px; font-weight:700;">
                    {paksha_eng.get('chandra_bala', 'मध्यम')}
                </span>
            </div>
            """, unsafe_allow_html=True)
        with col_pk2:
            st.markdown(f"""
            <div style="background:{'#1F2937' if is_dark else '#FFFFFF'}; border:1px solid {'#374151' if is_dark else '#E2E8F0'};
                        border-left:4px solid #3B82F6; border-radius:10px; padding:16px;">
                <b style="color:#1E3A8A; font-size:15px;">📖 शास्त्रीय पक्ष-बल नियम:</b>
                <p style="margin:6px 0 0 0; color:{'#D1D5DB' if is_dark else '#334155'}; font-size:13.5px; line-height:1.6;">
                    {paksha_eng.get('chandra_bala_desc', '')}
                </p>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")

        # 2. PITRU PAKSHA DEEP ENGINE
        st.markdown("#### 🪔 २. पितृपक्ष (महालय श्राद्ध काल) गहन शास्त्रीय अनुसंधान")
        if pitru.get("is_active"):
            st.markdown(f"""
            <div style="background:#FFF5F5; border:2px solid #DC2626; border-radius:12px; padding:20px; margin-bottom:16px;">
                <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap;">
                    <b style="color:#991B1B; font-size:18px;">🚫 {pitru['shradh_name']} सक्रिय</b>
                    <span style="background:#DC2626; color:#FFFFFF; padding:4px 12px; border-radius:14px; font-weight:700; font-size:12px;">
                        {pitru['badge']}
                    </span>
                </div>
                <p style="color:#7F1D1D; font-size:13.5px; margin:8px 0; line-height:1.6;">
                    <b>शास्त्रीय प्रमाण:</b> <i>"{pitru['sutra']}"</i><br/>
                    {pitru['verdict_desc']}
                </p>
                <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap:10px; margin-top:10px;">
                    <div style="background:#FFFFFF; border:1px solid #FECACA; border-radius:8px; padding:10px;">
                        <b style="color:#991B1B;">☀️ कुतुप मुहूर्त (श्राद्ध का मुख्य काल):</b><br/>
                        <span style="font-size:15px; font-weight:700; color:#0F172A;">{pitru['kutupa_time']}</span>
                    </div>
                    <div style="background:#FFFFFF; border:1px solid #FECACA; border-radius:8px; padding:10px;">
                        <b style="color:#991B1B;">☀️ रौहिण मुहूर्त:</b><br/>
                        <span style="font-size:15px; font-weight:700; color:#0F172A;">{pitru['rohina_time']}</span>
                    </div>
                    <div style="background:#FFFFFF; border:1px solid #FECACA; border-radius:8px; padding:10px;">
                        <b style="color:#991B1B;">🌊 अपराह्न काल (तर्पण/पिण्डदान):</b><br/>
                        <span style="font-size:15px; font-weight:700; color:#0F172A;">{pitru['aparahna_time']}</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            col_pt1, col_pt2 = st.columns(2)

            with col_pt1:
                st.markdown("""
                <div style="background:#FEF2F2; border:1.5px solid #DC2626; border-radius:10px; padding:16px; height:100%;">
                    <b style="color:#991B1B; font-size:16px;">🚫 क्या-क्या सर्वथा वर्जित है (Strict Prohibitions):</b>
                    <p style="color:#7F1D1D; font-size:12.5px; margin:4px 0 10px 0;">शास्त्रों अनुसार इस अवधि में भौतिक मांगलिक उत्सव अनिष्टकारी होते हैं:</p>
                    <ul style="color:#991B1B; font-size:13px; line-height:1.7; padding-left:18px; margin:0;">
                        <li><b>नूतन गृह प्रवेश व भूमि पूजन:</b> नया घर खरीदना, गृह प्रवेश या नींव पूजन पूर्णतः निषिद्ध।</li>
                        <li><b>विवाह, सगाई व रोका:</b> पाणिग्रहण संस्कार व वैवाहिक उत्सव महा-वर्जित।</li>
                        <li><b>मुंडन व उपनयन संस्कार:</b> कोई भी मांगलिक संस्कार सम्पन्न नहीं किया जाता।</li>
                        <li><b>नया व्यापार/प्रतिष्ठान उद्घाटन:</b> नए व्यवसाय या दुकान का आरम्भ न करें।</li>
                        <li><b>नवीन वाहन एवं स्वर्ण क्रय:</b> विलासिता सामग्री व नवीन आभूषणों का प्रथम उपयोग वर्जित।</li>
                        <li><b>तामसिक भोजन व व्यसन:</b> प्याज, लहसुन, मांस, मदिरा महा-पाप माना गया है।</li>
                        <li><b>बाल, दाढ़ी व नाखून काटना:</b> श्राद्ध कर्ता हेतु क्षौर कर्म निषिद्ध है।</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)

            with col_pt2:
                st.markdown("""
                <div style="background:#F0FDF4; border:1.5px solid #16A34A; border-radius:10px; padding:16px; height:100%;">
                    <b style="color:#166534; font-size:16px;">🟢 क्या-क्या करने का विधान है (Prescribed Rituals):</b>
                    <p style="color:#15803D; font-size:12.5px; margin:4px 0 10px 0;">इस पावन काल में पितृ सेवा से वंश वृद्धि, आरोग्य व शांति प्राप्त होती है:</p>
                    <ul style="color:#14532D; font-size:13px; line-height:1.7; padding-left:18px; margin:0;">
                        <li><b>पितृ तर्पण:</b> काले तिल, जौ, कुशा व गंगाजल से पितरों को जलांजलि अर्पण।</li>
                        <li><b>पिण्डदान एवं श्राद्ध कर्म:</b> कुतुप व रौहिण मुहूर्त में विधिपूर्वक श्राद्ध कर्म।</li>
                        <li><b>पंचबलि कर्म:</b> गौ (गाय), श्वान (कुत्ता), काक (कौआ), देवादि एवं चींटियों को ग्रास देना।</li>
                        <li><b>ब्राह्मण भोजन व दक्षिणा:</b> सात्विक खीर-पूरी से योग्य ब्राह्मणों को तृप्त करना।</li>
                        <li><b>श्रीमद्भगवद्गीता पाठ:</b> विशेषकर अध्याय ७, ११ एवं गरुड़ पुराण का श्रवण।</li>
                        <li><b>अन्न व वस्त्र दान:</b> जरूरतमंदों को अन्न, छाता, पादुका (जूते) एवं दीपदान।</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="background:{'#1F2937' if is_dark else '#F0FDF4'}; border:1px solid #BBF7D0;
                        border-radius:10px; padding:16px;">
                <b style="color:#166534; font-size:15px;">{pitru.get('badge', 'पितृपक्ष निष्क्रिय')}</b>
                <p style="margin:4px 0 0 0; color:#15803D; font-size:13.5px;">{pitru.get('desc', 'वर्तमान में पितृपक्ष सक्रिय नहीं है।')}</p>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")

        # 3. CHATURMAS & KHARMAS
        st.markdown("#### 🕉️ ३. चातुर्मास (देवशयन) एवं खरमास (मलमास) स्थिति")
        col_ct1, col_ct2 = st.columns(2)

        with col_ct1:
            is_ch = paksha_eng.get("is_chaturmas", False)
            ch_bg = "#FFF7ED" if is_ch else "#F8FAFC"
            ch_bdr = "#F97316" if is_ch else "#E2E8F0"
            ch_col = "#C2410C" if is_ch else "#475569"
            st.markdown(f"""
            <div style="background:{ch_bg if not is_dark else '#1F2937'}; border:1.5px solid {ch_bdr};
                        border-radius:10px; padding:16px;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <b style="color:{ch_col}; font-size:15px;">चातुर्मास (देवशयन काल)</b>
                    <span style="background:{ch_col}20; color:{ch_col}; padding:2px 8px; border-radius:10px; font-size:11px; font-weight:700;">
                        {'⚠️ सक्रिय' if is_ch else '🟢 निष्क्रिय'}
                    </span>
                </div>
                <p style="margin:6px 0 0 0; color:{'#D1D5DB' if is_dark else '#334155'}; font-size:13px; line-height:1.5;">
                    {paksha_eng.get('chaturmas_desc', '')}
                </p>
            </div>
            """, unsafe_allow_html=True)

        with col_ct2:
            is_kh = paksha_eng.get("is_kharmas", False)
            kh_bg = "#FEF2F2" if is_kh else "#F8FAFC"
            kh_bdr = "#DC2626" if is_kh else "#E2E8F0"
            kh_col = "#991B1B" if is_kh else "#475569"
            st.markdown(f"""
            <div style="background:{kh_bg if not is_dark else '#1F2937'}; border:1.5px solid {kh_bdr};
                        border-radius:10px; padding:16px;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <b style="color:{kh_col}; font-size:15px;">खरमास / मलमास (धनु-मीन सूर्य)</b>
                    <span style="background:{kh_col}20; color:{kh_col}; padding:2px 8px; border-radius:10px; font-size:11px; font-weight:700;">
                        {'🚫 सक्रिय' if is_kh else '🟢 निष्क्रिय'}
                    </span>
                </div>
                <p style="margin:6px 0 0 0; color:{'#D1D5DB' if is_dark else '#334155'}; font-size:13px; line-height:1.5;">
                    {paksha_eng.get('kharmas_desc', '')}
                </p>
            </div>
            """, unsafe_allow_html=True)

    # =============================================================
    # TAB 3: शुभ एवं अशुभ मुहूर्त (Timings)
    # =============================================================
    with tab3:
        st.markdown("### ⏰ शुभ एवं अशुभ काल / मुहूर्त (Auspicious & Inauspicious Timings)")
        st.caption("सूर्योदय व सूर्यास्त के शुद्ध दिनमान विभाजन पर आधारित यथार्थ वेला एवं त्याज्य काल चक्र:")

        col_m1, col_m2 = st.columns(2)

        with col_m1:
            st.markdown("#### 🟢 शुभ एवं अमृत मुहूर्त (Auspicious Windows)")
            for win in muh["shubh_windows"]:
                st.markdown(f"""
                <div style="background:{'#1F2937' if is_dark else '#F0FDF4'}; border:1px solid {'#374151' if is_dark else '#BBF7D0'};
                            border-left:4px solid {win['color']}; border-radius:8px; padding:12px; margin-bottom:10px;">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <b style="color:{win['color']}; font-size:14.5px;">{win['title']}</b>
                        <span style="background:{win['color']}20; color:{win['color']}; padding:2px 8px; border-radius:10px; font-size:11px; font-weight:700;">
                            {win['badge']}
                        </span>
                    </div>
                    <div style="font-size:16px; font-weight:800; color:{'#FFFFFF' if is_dark else '#0F172A'}; margin:4px 0;">
                        ⏱️ {win['time']}
                    </div>
                    <small style="color:{'#9CA3AF' if is_dark else '#475569'};">{win['status']}</small>
                </div>
                """, unsafe_allow_html=True)

        with col_m2:
            st.markdown("#### 🔴 अशुभ एवं त्याज्य काल (Inauspicious Windows)")
            for win in muh["ashubh_windows"]:
                st.markdown(f"""
                <div style="background:{'#1F2937' if is_dark else '#FEF2F2'}; border:1px solid {'#374151' if is_dark else '#FECACA'};
                            border-left:4px solid {win['color']}; border-radius:8px; padding:12px; margin-bottom:10px;">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <b style="color:{win['color']}; font-size:14.5px;">{win['title']}</b>
                        <span style="background:{win['color']}20; color:{win['color']}; padding:2px 8px; border-radius:10px; font-size:11px; font-weight:700;">
                            {win['badge']}
                        </span>
                    </div>
                    <div style="font-size:16px; font-weight:800; color:{'#FFFFFF' if is_dark else '#0F172A'}; margin:4px 0;">
                        ⚠️ {win['time']}
                    </div>
                    <small style="color:{'#9CA3AF' if is_dark else '#475569'};">{win['status']}</small>
                </div>
                """, unsafe_allow_html=True)

    # =============================================================
    # TAB 4: चौघड़िया, होरा एवं वैदिक घड़ी
    # =============================================================
    with tab4:
        st.markdown("### ☀️ चौघड़िया, होरा एवं वैदिक घड़ी (Choghadiya, Horas & Vedic Time)")
        st.caption("दिन के ८ एवं रात्रि के ८ चौघड़िया, २४ ग्रह होराएं एवं ६० घटी वैदिक काल मापन:")

        c_tab1, c_tab2, c_tab3 = st.tabs(["☀️ दिन का चौघड़िया", "🌙 रात्रि का चौघड़िया", "🪐 २४ ग्रह होरा चक्र"])

        with c_tab1:
            st.markdown("#### ☀️ दिन का चौघड़िया (Day Choghadiya: सूर्योदय से सूर्यास्त)")
            col_d1, col_d2 = st.columns(2)
            half = len(chog["day_choghadiyas"]) // 2
            with col_d1:
                for item in chog["day_choghadiyas"][:half]:
                    bdr_c = item["color"]
                    st.markdown(f"""
                    <div style="background:{item['bg'] if not is_dark else '#1F2937'}; border:1px solid {bdr_c};
                                border-radius:8px; padding:10px 14px; margin-bottom:8px;">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <b style="color:{item['color']}; font-size:15px;">#{item['slot']} {item['name']} ({item['nature']})</b>
                            <span style="font-size:11.5px; color:#475569;">ग्रह: {item['planet']}</span>
                        </div>
                        <div style="font-size:14.5px; font-weight:700; color:{'#FFFFFF' if is_dark else '#0F172A'}; margin:3px 0;">
                            ⏱️ {item['start']} - {item['end']}
                        </div>
                        <small style="color:{'#9CA3AF' if is_dark else '#475569'};">{item['acts']}</small>
                    </div>
                    """, unsafe_allow_html=True)
            with col_d2:
                for item in chog["day_choghadiyas"][half:]:
                    bdr_c = item["color"]
                    st.markdown(f"""
                    <div style="background:{item['bg'] if not is_dark else '#1F2937'}; border:1px solid {bdr_c};
                                border-radius:8px; padding:10px 14px; margin-bottom:8px;">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <b style="color:{item['color']}; font-size:15px;">#{item['slot']} {item['name']} ({item['nature']})</b>
                            <span style="font-size:11.5px; color:#475569;">ग्रह: {item['planet']}</span>
                        </div>
                        <div style="font-size:14.5px; font-weight:700; color:{'#FFFFFF' if is_dark else '#0F172A'}; margin:3px 0;">
                            ⏱️ {item['start']} - {item['end']}
                        </div>
                        <small style="color:{'#9CA3AF' if is_dark else '#475569'};">{item['acts']}</small>
                    </div>
                    """, unsafe_allow_html=True)

        with c_tab2:
            st.markdown("#### 🌙 रात्रि का चौघड़िया (Night Choghadiya: सूर्यास्त से आगामी सूर्योदय)")
            col_n1, col_n2 = st.columns(2)
            with col_n1:
                for item in chog["night_choghadiyas"][:half]:
                    bdr_c = item["color"]
                    st.markdown(f"""
                    <div style="background:{item['bg'] if not is_dark else '#1F2937'}; border:1px solid {bdr_c};
                                border-radius:8px; padding:10px 14px; margin-bottom:8px;">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <b style="color:{item['color']}; font-size:15px;">#{item['slot']} {item['name']} ({item['nature']})</b>
                            <span style="font-size:11.5px; color:#475569;">ग्रह: {item['planet']}</span>
                        </div>
                        <div style="font-size:14.5px; font-weight:700; color:{'#FFFFFF' if is_dark else '#0F172A'}; margin:3px 0;">
                            ⏱️ {item['start']} - {item['end']}
                        </div>
                        <small style="color:{'#9CA3AF' if is_dark else '#475569'};">{item['acts']}</small>
                    </div>
                    """, unsafe_allow_html=True)
            with col_n2:
                for item in chog["night_choghadiyas"][half:]:
                    bdr_c = item["color"]
                    st.markdown(f"""
                    <div style="background:{item['bg'] if not is_dark else '#1F2937'}; border:1px solid {bdr_c};
                                border-radius:8px; padding:10px 14px; margin-bottom:8px;">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <b style="color:{item['color']}; font-size:15px;">#{item['slot']} {item['name']} ({item['nature']})</b>
                            <span style="font-size:11.5px; color:#475569;">ग्रह: {item['planet']}</span>
                        </div>
                        <div style="font-size:14.5px; font-weight:700; color:{'#FFFFFF' if is_dark else '#0F172A'}; margin:3px 0;">
                            ⏱️ {item['start']} - {item['end']}
                        </div>
                        <small style="color:{'#9CA3AF' if is_dark else '#475569'};">{item['acts']}</small>
                    </div>
                    """, unsafe_allow_html=True)

        with c_tab3:
            st.markdown("#### 🪐 २४ ग्रह होरा चक्र (24 Planetary Horas)")
            hora_cols = st.columns(2)
            with hora_cols[0]:
                st.markdown("##### ☀️ दिन की १२ होराएं")
                for h in chog["horas_24"][:12]:
                    st.markdown(f"""
                    <div style="background:{'#1F2937' if is_dark else '#FFFFFF'}; border:1px solid {'#374151' if is_dark else '#E2E8F0'};
                                border-left:3px solid #3B82F6; border-radius:6px; padding:8px 12px; margin-bottom:6px;">
                        <b>#{h['hora_num']} होरा: {h['planet']}</b> — <span style="color:#2563EB;">{h['start']} से {h['end']}</span><br/>
                        <small style="color:#64748B;">{h['acts']}</small>
                    </div>
                    """, unsafe_allow_html=True)
            with hora_cols[1]:
                st.markdown("##### 🌙 रात्रि की १२ होराएं")
                for h in chog["horas_24"][12:]:
                    st.markdown(f"""
                    <div style="background:{'#1F2937' if is_dark else '#FFFFFF'}; border:1px solid {'#374151' if is_dark else '#E2E8F0'};
                                border-left:3px solid #8B5CF6; border-radius:6px; padding:8px 12px; margin-bottom:6px;">
                        <b>#{h['hora_num']} होरा: {h['planet']}</b> — <span style="color:#7C3AED;">{h['start']} से {h['end']}</span><br/>
                        <small style="color:#64748B;">{h['acts']}</small>
                    </div>
                    """, unsafe_allow_html=True)

    # =============================================================
    # TAB 5: भद्रा, पञ्चक एवं गण्डमूल शोध
    # =============================================================
    with tab5:
        st.markdown("### 🛡️ भद्रा, पञ्चक एवं गण्डमूल शोध (Bhadra, Panchaka & Gandamoola Engine)")
        st.caption("मुहूर्त चिन्तामणि के अनुसार भद्रा वास, मुख-पुच्छ काल, पञ्चक के ५ प्रकार एवं गण्डमूल चरण फल:")

        # 1. BHADRA ENGINE
        st.markdown("#### 🚫 १. भद्रा विचार (Vishti Karana Deep Analysis)")
        if bhadra["is_present"]:
            st.markdown(f"""
            <div style="background:{'#1F2937' if is_dark else '#FEF2F2'}; border:1.5px solid {bhadra['color']};
                        border-radius:12px; padding:18px; margin-bottom:16px;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <b style="color:{bhadra['color']}; font-size:18px;">⚠️ भद्रा सक्रिय — {bhadra['loka']}</b>
                    <span style="background:{bhadra['color']}20; color:{bhadra['color']}; padding:4px 12px; border-radius:14px; font-weight:700;">
                        {bhadra['badge']}
                    </span>
                </div>
                <div style="font-size:16px; font-weight:800; color:{'#FFFFFF' if is_dark else '#0F172A'}; margin:8px 0;">
                    ⏱️ भद्रा काल: {bhadra['full_time_str']} (कुल अवधि: {bhadra['duration_str']})
                </div>
                <p style="color:{'#D1D5DB' if is_dark else '#334155'}; font-size:13.5px; margin:6px 0;">
                    <b>शास्त्रीय निर्णय:</b> {bhadra['verdict']}<br/>
                    <i>"{bhadra['sutra']}"</i>
                </p>
                <div style="display:grid; grid-template-columns:1fr 1fr; gap:12px; margin-top:10px;">
                    <div style="background:rgba(220, 38, 38, 0.1); border:1px solid #DC2626; border-radius:8px; padding:10px;">
                        <b style="color:#DC2626;">💀 भद्रा मुख (सर्वथा वर्जित):</b><br/>
                        {bhadra['mukha_time']}
                    </div>
                    <div style="background:rgba(5, 150, 105, 0.1); border:1px solid #059669; border-radius:8px; padding:10px;">
                        <b style="color:#059669;">✨ भद्रा पुच्छ (कार्य सिद्धिप्रद):</b><br/>
                        {bhadra['puchha_time']}
                    </div>
                </div>
                <div style="margin-top:10px; font-size:12.5px; color:#DC2626;">
                    <b>वर्जित कर्म:</b> {', '.join(bhadra['prohibitions'])}
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="background:{'#1F2937' if is_dark else '#F0FDF4'}; border:1px solid #BBF7D0;
                        border-radius:12px; padding:16px; margin-bottom:16px;">
                <b style="color:#166534; font-size:16px;">{bhadra['badge']}</b>
                <p style="color:#15803D; margin:4px 0 0 0; font-size:13.5px;">{bhadra['status_hi']}</p>
            </div>
            """, unsafe_allow_html=True)

        col_pg1, col_pg2 = st.columns(2)

        # 2. PANCHAKA ENGINE
        p_info = pg["panchaka"]
        with col_pg1:
            st.markdown("#### ⚡ २. पञ्चक विचार (5 Panchaka Types)")
            st.markdown(f"""
            <div style="background:{'#1F2937' if is_dark else '#FFFFFF'}; border:1.5px solid {p_info['color']};
                        border-radius:12px; padding:16px; height:100%;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <b style="color:{p_info['color']}; font-size:16px;">{p_info['name']}</b>
                    <span style="background:{p_info['color']}20; color:{p_info['color']}; padding:2px 8px; border-radius:12px; font-weight:700; font-size:11px;">
                        {p_info['badge']}
                    </span>
                </div>
                <p style="color:{'#D1D5DB' if is_dark else '#475569'}; font-size:13px; margin:8px 0;">{p_info['desc']}</p>
                {'<div style="font-size:12px; color:#DC2626;"><b>विशेष निषेध:</b><br/>• ' + '<br/>• '.join(p_info.get('prohibitions', [])) + '</div>' if p_info['is_active'] else ''}
            </div>
            """, unsafe_allow_html=True)

        # 3. GANDAMOOLA ENGINE
        g_info = pg["gandamoola"]
        with col_pg2:
            st.markdown("#### 🌿 ३. गण्डमूल विचार (Gandamoola 6 Nakshatras)")
            st.markdown(f"""
            <div style="background:{'#1F2937' if is_dark else '#FFFFFF'}; border:1.5px solid {g_info['color']};
                        border-radius:12px; padding:16px; height:100%;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <b style="color:{g_info['color']}; font-size:16px;">{g_info.get('nakshatra', 'गण्डमूल')} {f'(चरण {g_info.get('pada')})' if g_info['is_active'] else ''}</b>
                    <span style="background:{g_info['color']}20; color:{g_info['color']}; padding:2px 8px; border-radius:12px; font-weight:700; font-size:11px;">
                        {g_info['badge']}
                    </span>
                </div>
                <p style="color:{'#D1D5DB' if is_dark else '#475569'}; font-size:13px; margin:8px 0;">{g_info['desc']}</p>
                {f'<div style="background:#FFFBEB; border:1px solid #FDE68A; border-radius:6px; padding:8px; font-size:12px; color:#92400E;"><b>शान्ति विधान:</b> {g_info.get("shanti_vidhi")}</div>' if g_info['is_active'] else ''}
            </div>
            """, unsafe_allow_html=True)

    # =============================================================
    # TAB 6: चन्द्रबलम, ताराबलम एवं आनन्दादि शुभ योग
    # =============================================================
    with tab6:
        st.markdown("### ⚖️ चन्द्रबलम, ताराबलम एवं आनन्दादि शुभ योग")
        st.caption("१२ राशियों का चन्द्रबल, २७ नक्षत्रों का ताराबल एवं २८ आनन्दादि महायोग:")

        # Special Yogas Banner
        sp_yogas = yogas["special_yogas"]
        if sp_yogas:
            st.markdown("#### 🌟 आज सक्रिय विशेष महायोग (Active Super Yogas)")
            for sy in sp_yogas:
                st.markdown(f"""
                <div style="background:#F0FDF4; border:1.5px solid #10B981; border-radius:10px; padding:12px 16px; margin-bottom:8px;">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <b style="color:#047857; font-size:15px;">{sy['title']}</b>
                        <span style="background:#D1FAE5; color:#065F46; padding:2px 8px; border-radius:10px; font-size:11px; font-weight:700;">{sy['badge']}</span>
                    </div>
                    <p style="color:#065F46; font-size:13px; margin:4px 0 0 0;">{sy['desc']}</p>
                </div>
                """, unsafe_allow_html=True)

        # Anandadi 28 Yoga
        ay = yogas["anandadi_yoga"]
        st.markdown(f"""
        <div style="background:{'#1F2937' if is_dark else '#FFFFFF'}; border:1px solid {'#374151' if is_dark else '#E2E8F0'};
                    border-left:4px solid {ay['color']}; border-radius:8px; padding:12px; margin-bottom:16px;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <b style="color:{ay['color']}; font-size:15px;">✨ आनन्दादि २८ योग: {ay['name']} योग ({ay['nature']})</b>
                <span style="background:{ay['color']}20; color:{ay['color']}; padding:2px 8px; border-radius:10px; font-size:11px; font-weight:700;">{ay['badge']}</span>
            </div>
            <p style="color:{'#D1D5DB' if is_dark else '#475569'}; font-size:13px; margin:4px 0 0 0;">{ay['desc']}</p>
        </div>
        """, unsafe_allow_html=True)

        col_b1, col_b2 = st.columns(2)

        # Chandrabalam
        with col_b1:
            st.markdown("#### 🌙 १२ राशियों का चन्द्रबलम् (Chandrabalam)")
            st.caption("१, ३, ६, ७, १०, ११वां चन्द्रमा शुभ; २, ५, ९ मध्यम; ४, ८, १२ अनिष्ट:")
            for item in balam["chandrabalam"]:
                st.markdown(f"""
                <div style="background:{'#1F2937' if is_dark else '#F8FAFC'}; border:1px solid {'#374151' if is_dark else '#E2E8F0'};
                            border-radius:6px; padding:6px 12px; margin-bottom:4px; display:flex; justify-content:space-between; align-items:center;">
                    <span style="font-size:13px; font-weight:600; color:{'#FFFFFF' if is_dark else '#0F172A'};">{item['rashi']}</span>
                    <span style="font-size:12px; color:#64748B;">{item['house_from_moon']}</span>
                    <span style="color:{item['color']}; font-size:12px; font-weight:700;">{item['status']}</span>
                </div>
                """, unsafe_allow_html=True)

        # Tarabalam
        with col_b2:
            st.markdown("#### 🌟 २७ नक्षत्रों का ताराबलम् (Tarabalam)")
            st.caption("जन्म, सम्पत्, विपत्, क्षेम, प्रत्यरि, साधक, वध, मित्र, परम मित्र:")
            for item in balam["tarabalam"][:14]:
                st.markdown(f"""
                <div style="background:{'#1F2937' if is_dark else '#F8FAFC'}; border:1px solid {'#374151' if is_dark else '#E2E8F0'};
                            border-radius:6px; padding:6px 12px; margin-bottom:4px; display:flex; justify-content:space-between; align-items:center;">
                    <span style="font-size:13px; font-weight:600; color:{'#FFFFFF' if is_dark else '#0F172A'};">{item['nakshatra']}</span>
                    <span style="color:{item['color']}; font-size:12px; font-weight:700;">{item['badge']} ({item['tara_name'].split(' (')[0]})</span>
                </div>
                """, unsafe_allow_html=True)

    # =============================================================
    # TAB 7: दैनिक ग्रह स्पष्ट एवं मंत्रिमंडल
    # =============================================================
    with tab7:
        st.markdown("### 🪐 दैनिक ग्रह स्पष्ट स्थिति एवं संवत्सर मंत्रिमंडल")
        st.caption("स्वीस एफिमरिस द्वारा सूर्योदय कालीन नवग्रह स्पष्ट स्थिति, राशि, अंश-कला-विकला, नक्षत्र, गति एवं गरिमा:")

        # Planetary Ephemeris Table
        ephem_rows = []
        for p in transit:
            ephem_rows.append({
                "ग्रह (Planet)": f"{p['symbol']} {p['name_hi']}",
                "राशि (Sign)": p['rashi'],
                "स्पष्ट अंश (Deg/Min/Sec)": p['deg_str'],
                "नक्षत्र (Nakshatra)": f"{p['nakshatra']} (चरण {p['pada']})",
                "गति (Motion)": p['motion'],
                "अस्त/उदय": p['combustion'],
                "गरिमा (Dignity)": p['dignity']
            })
        st.dataframe(ephem_rows, use_container_width=True)

        st.markdown("---")

        # Samvatsar Cabinet
        st.markdown(f"#### 🏛️ संवत्सर {samvat['vikram_samvat']} ({samvat['jovian_samvatsar']}) का देव मंत्रिमंडल")
        cab_cols = st.columns(2)
        half_c = len(samvat["cabinet"]) // 2 + 1
        with cab_cols[0]:
            for post in samvat["cabinet"][:half_c]:
                st.markdown(f"""
                <div style="background:{'#1F2937' if is_dark else '#F8FAFC'}; border:1px solid {'#374151' if is_dark else '#E2E8F0'};
                            border-left:3px solid #2563EB; border-radius:6px; padding:8px 12px; margin-bottom:6px;">
                    <b>{post['post']}:</b> <span style="color:#1D4ED8; font-weight:700;">{post['graha']}</span><br/>
                    <small style="color:#64748B;">प्रभाव: {post['effect']}</small>
                </div>
                """, unsafe_allow_html=True)
        with cab_cols[1]:
            for post in samvat["cabinet"][half_c:]:
                st.markdown(f"""
                <div style="background:{'#1F2937' if is_dark else '#F8FAFC'}; border:1px solid {'#374151' if is_dark else '#E2E8F0'};
                            border-left:3px solid #2563EB; border-radius:6px; padding:8px 12px; margin-bottom:6px;">
                    <b>{post['post']}:</b> <span style="color:#1D4ED8; font-weight:700;">{post['graha']}</span><br/>
                    <small style="color:#64748B;">प्रभाव: {post['effect']}</small>
                </div>
                """, unsafe_allow_html=True)

    # =============================================================
    # TAB 8: शास्त्रीय फलादेश, शूल व कर्म शुद्धि
    # =============================================================
    with tab8:
        st.markdown("### 📖 शास्त्रीय फलादेश, शूल, वास एवं वैदिक कर्म शुद्धि")
        st.caption("दिशा शूल, चन्द्र वास, अग्नि वास (हवन विचार), शिव वास (रुद्राभिषेक विचार) एवं दैनिक कर्म शुद्धि:")

        col_s1, col_s2 = st.columns(2)

        with col_s1:
            st.markdown("#### 🧭 १. दिशा शूल एवं चन्द्र वास")
            st.markdown(f"""
            <div style="background:{'#1F2937' if is_dark else '#FFFBEB'}; border:1px solid {'#374151' if is_dark else '#FDE68A'};
                        border-radius:10px; padding:14px; margin-bottom:12px;">
                <b style="color:#92400E; font-size:15px;">🚨 आज का दिशा शूल: {nivas['disha_shoola']['direction']}</b>
                <p style="color:#78350F; font-size:13px; margin:4px 0 0 0;">
                    <b>निवारक उपाय (Parihar):</b> {nivas['disha_shoola']['parihar']}
                </p>
            </div>
            """, unsafe_allow_html=True)

            st.markdown(f"""
            <div style="background:{'#1F2937' if is_dark else '#EFF6FF'}; border:1px solid {'#374151' if is_dark else '#BFDBFE'};
                        border-radius:10px; padding:14px; margin-bottom:12px;">
                <b style="color:#1E40AF; font-size:15px;">🌙 चन्द्र वास: {nivas['chandra_vasa']['direction']}</b>
                <p style="color:#1E3A8A; font-size:13px; margin:4px 0 0 0;">
                    {nivas['chandra_vasa']['rule']}
                </p>
            </div>
            """, unsafe_allow_html=True)

        with col_s2:
            st.markdown("#### 🔥 २. अग्नि वास एवं शिव वास विचार")
            st.markdown(f"""
            <div style="background:{'#1F2937' if is_dark else '#FFFFFF'}; border:1.5px solid {nivas['agnivasa']['color']};
                        border-radius:10px; padding:14px; margin-bottom:12px;">
                <b style="color:{nivas['agnivasa']['color']}; font-size:15px;">🔥 अग्नि वास (हवन विचार): {nivas['agnivasa']['vasa']}</b>
                <p style="color:{'#D1D5DB' if is_dark else '#475569'}; font-size:13px; margin:4px 0 0 0;">
                    {nivas['agnivasa']['verdict']}
                </p>
            </div>
            """, unsafe_allow_html=True)

            st.markdown(f"""
            <div style="background:{'#1F2937' if is_dark else '#FFFFFF'}; border:1.5px solid {nivas['shivavasa']['color']};
                        border-radius:10px; padding:14px; margin-bottom:12px;">
                <b style="color:{nivas['shivavasa']['color']}; font-size:15px;">🔱 शिव वास (रुद्राभिषेक विचार): {nivas['shivavasa']['vasa']}</b>
                <p style="color:{'#D1D5DB' if is_dark else '#475569'}; font-size:13px; margin:4px 0 0 0;">
                    {nivas['shivavasa']['verdict']}
                </p>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")

        # Action Suitability Scorecard (Strictly enforcing Pitru Paksha & Mahadoshas)
        is_pitru_active = pitru.get("is_active", False)

        st.markdown(f"""
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
            <h4 style="margin:0;">🎯 दैनिक कर्म शुद्धि एवं अनुशंसित कार्य (Action Suitability Scorecard)</h4>
            {'<span style="background:#FEE2E2; color:#DC2626; padding:3px 10px; border-radius:12px; font-size:12px; font-weight:700;">⚠️ पितृपक्ष निषेध नियम लागू</span>' if is_pitru_active else ''}
        </div>
        """, unsafe_allow_html=True)

        acts_cols = st.columns(4)
        acts_list = [
            ("🏠 गृह प्रवेश", "🚫 सर्वथा वर्जित (पितृपक्ष)" if is_pitru_active else ("वर्जित" if bhadra.get("is_fatal_on_earth") or "रिक्ता" in pillars["tithi"]["category"] else "शुभ"), "#DC2626" if (is_pitru_active or bhadra.get("is_fatal_on_earth")) else "#059669"),
            ("💍 विवाह संस्कार", "🚫 महा-निषेध (पितृपक्ष)" if is_pitru_active else ("वर्जित" if bhadra.get("is_fatal_on_earth") or not pillars["yoga"]["is_good"] else "शुभ"), "#DC2626" if (is_pitru_active or bhadra.get("is_fatal_on_earth")) else "#059669"),
            ("🚗 वाहन क्रय", "⚠️ त्याज्य (विलासिता वर्जित)" if is_pitru_active else "चर/लाभ चौघड़िया में शुभ", "#DC2626" if is_pitru_active else "#059669"),
            ("📈 नवीन व्यापार आरम्भ", "🚫 वर्जित (नवीन आरम्भ निषिद्ध)" if is_pitru_active else "लाभ/अमृत चौघड़िया में उत्तम", "#DC2626" if is_pitru_active else "#059669"),
            ("🌾 भूमि पूजन / नींव", "🚫 वर्जित (पितृपक्ष/पञ्चक)" if (is_pitru_active or pg["panchaka"]["is_active"]) else "शुभ", "#DC2626" if (is_pitru_active or pg["panchaka"]["is_active"]) else "#059669"),
            ("✈️ यात्रा आरम्भ", "दिशा शूल परिहार आवश्यक", "#D97706"),
            ("💰 स्वर्ण व आभूषण", "⚠️ नवीन उपभोग त्याज्य" if is_pitru_active else "शुभ चौघड़िया में क्रय", "#D97706" if is_pitru_active else "#059669"),
            ("🪔 तर्पण व पिण्डदान", "🌟 सर्वोत्तम (परम पितृ-तृप्ति)" if is_pitru_active else "अमावस्या/संक्रान्ति पर शुभ", "#059669"),
            ("🍲 पंचबलि व ब्राह्मण भोज", "🟢 परम कल्याणकारी (अक्षय पुण्य)" if is_pitru_active else "शुभ कर्म", "#059669"),
            ("📖 गीता पाठ (अध्याय ७ व ११)", "सर्वदोष नाशक व पितृ उद्धारक", "#059669"),
            ("🌿 दान-पुण्य व गौ सेवा", "अति उत्तम (अक्षय फल)", "#059669"),
            ("💊 औषधि सेवन", "शुभ", "#059669")
        ]
        for idx, (act_name, act_status, act_color) in enumerate(acts_list):
            with acts_cols[idx % 4]:
                st.markdown(f"""
                <div style="background:{'#1F2937' if is_dark else '#F8FAFC'}; border:1px solid {'#374151' if is_dark else '#E2E8F0'};
                            border-left:3px solid {act_color}; border-radius:6px; padding:10px; margin-bottom:8px; text-align:center;">
                    <b style="font-size:13px; color:{'#FFFFFF' if is_dark else '#0F172A'};">{act_name}</b>
                    <div style="color:{act_color}; font-size:12px; font-weight:700; margin-top:2px;">{act_status}</div>
                </div>
                """, unsafe_allow_html=True)
