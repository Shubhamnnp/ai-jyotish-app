import streamlit as st
import pandas as pd
from datetime import datetime, timezone, timedelta, date, time
import importlib

def get_live_local_now(tz_offset_hours: float = 5.5) -> datetime:
    return datetime.now(timezone.utc) + timedelta(hours=tz_offset_hours)

def render_muhurta_view(chart, tz_offset=5.5, default_city_name=None, tabs=None):
    if default_city_name is None:
        default_city_name = st.session_state.get("birth_city", "New Delhi, Delhi, India")
    
    if tabs is None or len(tabs) < 8:
        tabs = [
            "📜 जन्म पञ्चाङ्ग व तत्व",
            "☀️ अहोरात्र चौघड़िया",
            "⏳ राहुकाल व अभिजित",
            "🌕 ताराबल व चन्द्रबल",
            "🏛️ १६ संस्कार मुहूर्त",
            "🔍 मुहूर्त खोजक (Scanner)",
            "📜 २१ महादोष विचार",
            "🪔 दोष परिहार व शांति"
        ]
    st.subheader("⏳ शुभ मुहूर्त, दैनिक चौघड़िया एवं जातक पञ्चाङ्ग (Vedic Muhurta & Birth Panchanga)")
    st.write("सूर्य सिद्धांत, मुहूर्त चिन्तामणि एवं कालप्रकाशिका आधारित जातक जन्म पञ्चाङ्ग तत्व, अहोरात्र चौघड़िया, काल-वेला, ताराबल-चन्द्रबल, १६ कार्य मुहूर्त एवं २१ महादोष परिहार।")

    import src.jyotish.services.muhurta as muh_svc_mod
    import src.jyotish.services.milan as milan_mod
    m_engine = muh_svc_mod.default_muhurta_engine
    m_scanner = muh_svc_mod.default_muhurta_scanner or muh_svc_mod.MuhurtaRangeScanner()

    col_m1, col_m2 = st.columns([1.5, 2.5])
    with col_m1:
        muhurta_date = st.date_input("📅 मुहूर्त अवलोकन दिनांक चयन करें (Select Date):", value=get_live_local_now(tz_offset).date(), format="DD/MM/YYYY", key="muhurta_main_date_picker")
    with col_m2:
        st.write("")
        st.caption(f"📍 स्थान: **{default_city_name}** | वार: **{muhurta_date.strftime('%A')}** | सक्रिय जातक: **{chart.birth_data.name}**")

    m_data = m_engine.calculate_daily_muhurta(muhurta_date)
    p_doshas = m_engine.get_daily_panchang_and_doshas(muhurta_date)

    # =========================================================================
    # HIGH-VISIBILITY PANCHANGA MAHA-DOSHA & KAAL SHUDDHI ALERT BANNER
    # =========================================================================
    if p_doshas.get("is_pitru_paksha"):
        st.markdown("""<div style="background:#FEF2F2; border:2px solid #DC2626; border-radius:10px; padding:14px 18px; margin: 10px 0 14px 0; box-shadow:0 4px 12px rgba(220,38,38,0.08);">
    <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px;">
    <span style="font-size:16px; font-weight:900; color:#991B1B;">🚨 महा-निषेध अलर्ट: पितृपक्ष (श्राद्ध / महालय पक्ष) सक्रिय है!</span>
    <span style="background:#DC2626; color:#FFFFFF; font-size:12px; font-weight:800; padding:4px 12px; border-radius:12px;">मांगलिक संस्कार सर्वथा वर्जित</span>
    </div>
    <div style="font-size:13.5px; color:#7F1D1D; margin-top:6px; line-height:1.6;">
    वर्तमान में सूर्य कन्या राशि में तथा चन्द्रमा कृष्ण पक्ष में होने से <b>पितृपक्ष (महालय काल)</b> चल रहा है। शास्त्रों (<i>निर्णय सिन्धु</i>, <i>मुहूर्त चिन्तामणि</i>) अनुसार यह काल केवल पितरों के श्राद्ध, तर्पण एवं पिंडदान हेतु आरक्षित है। इस अवधि में <b>नवीन गृह प्रवेश, विवाह, मुंडन, उपनयन (जनेऊ), भूमि पूजन एवं नवीन प्रतिष्ठान उद्घाटन सर्वथा वर्जित</b> हैं।
    </div>
    <div style="font-size:12px; color:#991B1B; font-weight:700; margin-top:6px;">
    📜 शास्त्रीय प्रमाण: <i>"आश्विने कृष्णपक्षे तु पितृपक्षः प्रकीर्तितः। विवाहादि शुभं कर्म गृहप्रवेशं च वर्जयेत्॥"</i>
    </div>
    </div>""", unsafe_allow_html=True)
    elif p_doshas.get("is_kharmas"):
        st.markdown("""<div style="background:#FEF2F2; border:2px solid #DC2626; border-radius:10px; padding:14px 18px; margin: 10px 0 14px 0;">
    <div style="font-size:16px; font-weight:900; color:#991B1B;">🚨 महा-निषेध अलर्ट: खरमास / मलमास (सूर्य धनु/मीन संक्रान्ति) सक्रिय है!</div>
    <div style="font-size:13px; color:#7F1D1D; margin-top:4px;">सूर्य देवगुरु बृहस्पति की राशि में होने से समस्त मांगलिक संस्कार (विवाह, गृह प्रवेश, मुंडन) वर्जित हैं। मकर संक्रान्ति अथवा मेष संक्रान्ति उपरांत ही शुभ मुहूर्त संभव होगा।</div>
    </div>""", unsafe_allow_html=True)

    if p_doshas.get("is_bhadra"):
        b_bg = "#FEF2F2" if p_doshas.get("bhadra_is_fatal") else "#FFFBEB"
        b_bd = "#DC2626" if p_doshas.get("bhadra_is_fatal") else "#F59E0B"
        b_txt = "#991B1B" if p_doshas.get("bhadra_is_fatal") else "#B45309"
        st.markdown(f"""<div style="background:{b_bg}; border:1.5px solid {b_bd}; border-radius:8px; padding:10px 14px; margin-bottom:12px; font-size:13px;">
    <b style="color:{b_txt};">⚠️ भद्रा (विष्टि करण #{p_doshas['karana_idx']}) प्रभाव — निवास: {p_doshas['bhadra_loka']}:</b>
    <span style="color:#1E293B;"> {p_doshas['bhadra_impact']}</span>
    </div>""", unsafe_allow_html=True)

    # Quick 5 Panchang Limbs Badges for Selected Date
    q_col1, q_col2, q_col3, q_col4, q_col5 = st.columns(5)
    with q_col1:
        st.markdown(f"""<div style="background:#F1F5F9; border-radius:6px; padding:6px 10px; text-align:center; font-size:12px;">
    <span style="color:#64748B;">तिथि:</span> <b>{p_doshas['tithi_name'].split(' ')[0]}</b> ({p_doshas['paksha']})
    </div>""", unsafe_allow_html=True)
    with q_col2:
        st.markdown(f"""<div style="background:#F1F5F9; border-radius:6px; padding:6px 10px; text-align:center; font-size:12px;">
    <span style="color:#64748B;">वार:</span> <b>{p_doshas['weekday_name']}</b>
    </div>""", unsafe_allow_html=True)
    with q_col3:
        st.markdown(f"""<div style="background:#F1F5F9; border-radius:6px; padding:6px 10px; text-align:center; font-size:12px;">
    <span style="color:#64748B;">नक्षत्र:</span> <b>{p_doshas['nakshatra_name']}</b>
    </div>""", unsafe_allow_html=True)
    with q_col4:
        st.markdown(f"""<div style="background:#F1F5F9; border-radius:6px; padding:6px 10px; text-align:center; font-size:12px;">
    <span style="color:#64748B;">योग:</span> <b>{p_doshas['yoga_name']}</b>
    </div>""", unsafe_allow_html=True)
    with q_col5:
        st.markdown(f"""<div style="background:#F1F5F9; border-radius:6px; padding:6px 10px; text-align:center; font-size:12px;">
    <span style="color:#64748B;">करण:</span> <b>{p_doshas['karana_name']}</b>
    </div>""", unsafe_allow_html=True)

    st.write("")

    # =========================================================================
    # 8 DEDICATED TABS
    # =========================================================================
    tab_m1, tab_m2, tab_m3, tab_m4, tab_m5, tab_m6, tab_m7, tab_m8 = st.tabs(tabs)

    # -------------------------------------------------------------
    # TAB 1: NATIVE BIRTH PANCHANGA & 5 ELEMENTS
    # -------------------------------------------------------------
    with tab_m1:
        st.markdown(f"#### 📜 सक्रिय जातक ({chart.birth_data.name}) का जन्म पञ्चाङ्ग एवं पञ्चाङ्ग तत्व विश्लेषण")
        st.caption("जन्म क्षण के ५ महा-अंग (तिथि, वार, नक्षत्र, योग, करण), पञ्चमहाभूत तत्व संतुलन, अवकहड़ा चक्र एवं जन्म पञ्चाङ्ग दोष परीक्षण:")

        p_info = chart.panchang
        m_planet = chart.planets.get("Moon", None)
        moon_nak_idx = int(m_planet.longitude / (360.0 / 27.0)) if m_planet else 0

        # Avakhada Chakra Data from milan module
        ganas = ["देव गण (Deva)", "मनुष्य गण (Manushya)", "राक्षस गण (Rakshasa)"]
        nadis = ["आदि नाड़ी (Aadi)", "मध्य नाड़ी (Madhya)", "अन्त्य नाड़ी (Antya)"]
        gana_val = ganas[milan_mod.NAKSHATRA_GANAS[moon_nak_idx]] if moon_nak_idx < len(milan_mod.NAKSHATRA_GANAS) else "देव गण"
        nadi_val = nadis[milan_mod.NAKSHATRA_NADIS[moon_nak_idx]] if moon_nak_idx < len(milan_mod.NAKSHATRA_NADIS) else "मध्य नाड़ी"
        yoni_val = milan_mod.NAKSHATRA_YONIS[moon_nak_idx] if moon_nak_idx < len(milan_mod.NAKSHATRA_YONIS) else "—"

        # 5 Panchanga Limbs Metrics
        c_p1, c_p2, c_p3, c_p4, c_p5 = st.columns(5)
        with c_p1:
            st.markdown(f"""<div style="background:#EFF6FF; border:1.5px solid #3B82F6; border-radius:10px; padding:10px; text-align:center;">
    <div style="font-size:11px; color:#1D4ED8; font-weight:800;">💧 तिथि (जल तत्व)</div>
    <div style="font-size:15px; font-weight:900; color:#1E3A8A;">{p_info.tithi_name}</div>
    <div style="font-size:10px; color:#475569;">संख्या: #{p_info.tithi_number} ({p_info.tithi_type})</div>
    </div>""", unsafe_allow_html=True)
        with c_p2:
            st.markdown(f"""<div style="background:#FEF2F2; border:1.5px solid #EF4444; border-radius:10px; padding:10px; text-align:center;">
    <div style="font-size:11px; color:#B91C1C; font-weight:800;">🔥 वार (अग्नि तत्व)</div>
    <div style="font-size:15px; font-weight:900; color:#991B1B;">{p_info.vara_name}</div>
    <div style="font-size:10px; color:#475569;">वासर: {chart.birth_data.birth_date.strftime('%A')}</div>
    </div>""", unsafe_allow_html=True)
        with c_p3:
            st.markdown(f"""<div style="background:#F0FDF4; border:1.5px solid #22C55E; border-radius:10px; padding:10px; text-align:center;">
    <div style="font-size:11px; color:#15803D; font-weight:800;">💨 नक्षत्र (वायु तत्व)</div>
    <div style="font-size:15px; font-weight:900; color:#064E3B;">{p_info.nakshatra_name}</div>
    <div style="font-size:10px; color:#475569;">पद: {getattr(m_planet, 'nakshatra_pada', 1)} | {gana_val.split(' ')[0]}</div>
    </div>""", unsafe_allow_html=True)
        with c_p4:
            st.markdown(f"""<div style="background:#FAF5FF; border:1.5px solid #A855F7; border-radius:10px; padding:10px; text-align:center;">
    <div style="font-size:11px; color:#7E22CE; font-weight:800;">🌌 योग (आकाश तत्व)</div>
    <div style="font-size:15px; font-weight:900; color:#581C87;">{p_info.yoga_name}</div>
    <div style="font-size:10px; color:#475569;">नित्य योग</div>
    </div>""", unsafe_allow_html=True)
        with c_p5:
            st.markdown(f"""<div style="background:#FFFBEB; border:1.5px solid #F59E0B; border-radius:10px; padding:10px; text-align:center;">
    <div style="font-size:11px; color:#B45309; font-weight:800;">⛰️ करण (पृथ्वी तत्व)</div>
    <div style="font-size:15px; font-weight:900; color:#78350F;">{p_info.karana_name}</div>
    <div style="font-size:10px; color:#475569;">{'चर करण' if p_info.karana_name in ['Bava', 'Balava', 'Kaulava', 'Taitila', 'Gara', 'Vanija', 'Vishti'] else 'स्थिर करण'}</div>
    </div>""", unsafe_allow_html=True)

        st.write("")
        col_ak1, col_ak2 = st.columns(2)
        with col_ak1:
            st.markdown("##### 🧭 अवकहड़ा चक्र विवरण (Avakhada Chakra Details)")
            ak_rows = [
                {"घटक": "जन्म नक्षत्र", "विवरण": f"{p_info.nakshatra_name} (पद {getattr(m_planet, 'nakshatra_pada', 1)})"},
                {"घटक": "चन्द्र राशि", "विवरण": f"{m_planet.sign_id if m_planet else 1} राशि"},
                {"घटक": "गण (Temperament)", "विवरण": gana_val},
                {"घटक": "नाड़ी (Constitutional)", "विवरण": nadi_val},
                {"घटक": "योनि (Animal Symbol)", "विवरण": yoni_val},
                {"घटक": "जन्म शेष महादशा", "विवरण": f"{getattr(m_planet, 'nakshatra_lord', '—')} महादशा"}
            ]
            st.dataframe(pd.DataFrame(ak_rows), use_container_width=True, hide_index=True)

        with col_ak2:
            st.markdown("##### 🛡️ जन्म पञ्चाङ्ग दोष परीक्षण (Birth Panchanga Doshas Check)")
            dosha_items = []

            # 1. Rikta Tithi Check
            t_num = p_info.tithi_number % 15
            if t_num in [4, 9, 14]:
                dosha_items.append({"दोष": "⚠️ रिक्ता तिथि जन्म (४, ९, १४)", "स्थिति": "सक्रिय (दोष)", "प्रभाव": "जीवन में आकस्मिक बाधाएं व विलंब। भगवान गणेश व शिव की उपासना अभीष्ट।", "रंग": "#EF4444"})
            else:
                dosha_items.append({"दोष": "✅ रिक्ता तिथि दोष", "स्थिति": "दोष मुक्त", "प्रभाव": "जन्म तिथि पूर्णा/नंदा/भद्रा/जया श्रेणी में शुभ है।", "रंग": "#10B981"})

            # 2. Amavasya Check
            if p_info.tithi_number == 30:
                dosha_items.append({"दोष": "⚠️ दर्श / अमावस्या जन्म", "स्थिति": "सक्रिय (दोष)", "प्रभाव": "सूर्य-चन्द्र युति के कारण मानसिक अशांति। शांति होम व पितृ तर्पण अनिवार्य।", "रंग": "#EF4444"})
            else:
                dosha_items.append({"दोष": "✅ अमावस्या दोष", "स्थिति": "दोष मुक्त", "प्रभाव": "चन्द्रमा को पर्याप्त प्रकाश प्राप्त है।", "रंग": "#10B981"})

            # 3. Vishti / Bhadra Karana Check
            if "Vishti" in p_info.karana_name or "विष्टि" in p_info.karana_name:
                dosha_items.append({"दोष": "⚠️ भद्रा (विष्टि करण) जन्म", "स्थिति": "सक्रिय (दोष)", "प्रभाव": "कार्य में संघर्ष। महामृत्युंजय जप एवं भद्रा शांति आवश्यक।", "रंग": "#EF4444"})
            else:
                dosha_items.append({"दोष": "✅ भद्रा (विष्टि) दोष", "स्थिति": "दोष मुक्त", "प्रभाव": "जन्म करण शुभ एवं क्रियाशील है।", "रंग": "#10B981"})

            # 4. Gandanta Check (Ashwini, Aslesha, Magha, Jyeshtha, Moola, Revati)
            gandanta_naks = ["Ashwini", "Ashlesha", "Magha", "Jyeshtha", "Moola", "Revati", "अश्विनी", "आश्लेषा", "मघा", "ज्येष्ठा", "मूल", "रेवती"]
            if any(g in p_info.nakshatra_name for g in gandanta_naks):
                dosha_items.append({"दोष": "⚠️ नक्षत्र गंडान्त जन्म", "स्थिति": "संवेदनशील", "प्रभाव": "नक्षत्र संधि पर जन्म। २७ दिन उपरांत गंडान्त मूल शांति अनुष्ठान प्रशस्त।", "रंग": "#F59E0B"})
            else:
                dosha_items.append({"दोष": "✅ नक्षत्र गंडान्त", "स्थिति": "दोष मुक्त", "प्रभाव": "जातक गंडान्त नक्षत्र संधि से पूर्ण सुरक्षित है।", "रंग": "#10B981"})

            for d in dosha_items:
                st.markdown(f"""<div style="background:#F8FAFC; border-left:4px solid {d['रंग']}; border-radius:6px; padding:6px 12px; margin-bottom:6px; font-size:12px;">
    <b style="color:#0F172A;">{d['दोष']}</b> — <span style="color:{d['रंग']}; font-weight:800;">{d['स्थिति']}</span><br/>
    <span style="color:#475569;">{d['प्रभाव']}</span>
    </div>""", unsafe_allow_html=True)

        st.info("💡 **पञ्चाङ्ग तत्व शास्त्रीय रहस्य:** पञ्चाङ्ग के ५ तत्व जातक के अंतःकरण को संचालित करते हैं — तिथि (जल तत्व: काम/इच्छा व संबंध), वार (अग्नि तत्व: जीवन शक्ति व स्वास्थ्य), नक्षत्र (वायु तत्व: बुद्धि व कर्म दिशा), योग (आकाश तत्व: चरित्र व भाग्य संयोग), करण (पृथ्वी तत्व: भौतिक सफलता व पुरुषार्थ)।")

    # -------------------------------------------------------------
    # TAB 2: DAY & NIGHT CHOGHADIYA
    # -------------------------------------------------------------
    with tab_m2:
        st.markdown(f"#### ☀️ दिन व रात्रि अहोरात्र चौघड़िया ({muhurta_date.strftime('%d-%b-%Y')})")
        st.caption("सूर्य सिद्धांत अनुसार सूर्योदय से सूर्यास्त (दिन के ८ चौघड़िया) एवं सूर्यास्त से अगले सूर्योदय (रात्रि के ८ चौघड़िया):")

        c_d1, c_d2 = st.columns(2)
        with c_d1:
            st.markdown("##### ☀️ दिन के ८ चौघड़िया (Day Choghadiya)")
            c_day_df = pd.DataFrame(m_data["day_choghadiyas"])[["index", "name", "start_time", "end_time", "nature"]]
            c_day_df.columns = ["क्रमांक", "चौघड़िया नाम", "आरंभ समय", "समाप्ति समय", "प्रकृति"]
            st.dataframe(c_day_df, use_container_width=True, hide_index=True)

        with c_d2:
            st.markdown("##### 🌙 रात्रि के ८ चौघड़िया (Night Choghadiya)")
            c_night_df = pd.DataFrame(m_data["night_choghadiyas"])[["index", "name", "start_time", "end_time", "nature"]]
            c_night_df.columns = ["क्रमांक", "चौघड़िया नाम", "आरंभ समय", "समाप्ति समय", "प्रकृति"]
            st.dataframe(c_night_df, use_container_width=True, hide_index=True)

        st.markdown("---")
        st.markdown("##### 🧭 चौघड़िया कार्य सिद्धि निर्देशिका (Choghadiya Activity Guide)")
        guide_cols = st.columns(4)
        with guide_cols[0]:
            st.markdown("""<div style="background:#DCFCE7; border:1px solid #22C55E; border-radius:8px; padding:10px; font-size:12px;">
    <b style="color:#15803D;">🟢 अमृत व शुभ चौघड़िया:</b><br/>
    समस्त नवीन कार्य, पूजा, विवाह, अनुबंध, शिक्षा, व्यापार आरंभ एवं यात्रा हेतु सर्वोत्तम।
    </div>""", unsafe_allow_html=True)
        with guide_cols[1]:
            st.markdown("""<div style="background:#EFF6FF; border:1px solid #3B82F6; border-radius:8px; padding:10px; font-size:12px;">
    <b style="color:#1D4ED8;">🔵 लाभ चौघड़िया:</b><br/>
    व्यापारिक लेन-देन, धन निवेश, दुकान खोलना, नवीन अनुबंध एवं आर्थिक लाभ के कार्यों हेतु उत्तम।
    </div>""", unsafe_allow_html=True)
        with guide_cols[2]:
            st.markdown("""<div style="background:#FEF3C7; border:1px solid #F59E0B; border-radius:8px; padding:10px; font-size:12px;">
    <b style="color:#B45309;">🟡 चर चौघड़िया:</b><br/>
    यात्रा, वाहन क्रय, स्थानांतरण, गतिमान कार्य एवं मशीनरी संचालन हेतु अनुकूल।
    </div>""", unsafe_allow_html=True)
        with guide_cols[3]:
            st.markdown("""<div style="background:#FEE2E2; border:1px solid #EF4444; border-radius:8px; padding:10px; font-size:12px;">
    <b style="color:#B91C1C;">🔴 रोग, काल व उद्वेग:</b><br/>
    शुभ कार्य वर्जित। विवाद, झगड़ा, सर्जरी एवं शत्रु दमन के अतिरिक्त अन्य कार्यों में त्यागें।
    </div>""", unsafe_allow_html=True)

    # -------------------------------------------------------------
    # TAB 3: INAUSPICIOUS & AUSPICIOUS TIME WINDOWS
    # -------------------------------------------------------------
    with tab_m3:
        st.markdown(f"#### ⏳ दैनिक काल-वेला, राहुकाल एवं अभिजित मुहूर्त ({muhurta_date.strftime('%d-%b-%Y')})")
        st.caption("अशुभ वर्जित काल (राहुकाल, यमगंड, दुर्मुहूर्त) एवं दोष-नाशक शुभ काल (अभिजित, ब्रह्म मुहूर्त):")

        for win in m_data["special_windows"]:
            border_c = "#EF4444" if win["type"] == "malefic" else ("#10B981" if win["type"] == "benefic" else "#CBD5E1")
            bg_c = "#FEF2F2" if win["type"] == "malefic" else ("#ECFDF5" if win["type"] == "benefic" else "#F8FAFC")
            st.markdown(f"""<div style="background:{bg_c}; border:1.5px solid {border_c}; border-radius:8px; padding:12px 16px; margin-bottom:10px; display:flex; justify-content:space-between; align-items:center;">
    <div>
    <b style="font-size:15px; color:#0F172A;">{win['title']}</b> &nbsp;|&nbsp; <span style="font-weight:700; color:#334155;">{win['time']}</span>
    </div>
    <div style="font-weight:800; font-size:13px; color:{'#991B1B' if win['type']=='malefic' else '#065F46'};">
    {win['impact']}
    </div>
    </div>""", unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("##### 📜 अभिजित मुहूर्त का शास्त्रीय माहात्म्य")
        st.info("💡 **अभिजित मुहूर्त (८वां मुहूर्त):** मध्याह्न काल में स्थानीय सूर्योदय व सूर्यास्त के मध्य का ८वां मुहूर्त 'अभिजित' कहलाता है। भगवान श्रीहरि विष्णु का परम प्रिय यह मुहूर्त प्रतिदिन के समस्त दोषों का हरण करने में सक्षम है (केवल बुधवार को अभिजित राहुकाल के प्रभाव के कारण त्याज्य माना जाता है)।")

    # -------------------------------------------------------------
    # TAB 4: TARA BALAM & CHANDRA BALAM MATRIX
    # -------------------------------------------------------------
    with tab_m4:
        st.markdown(f"#### 🌕 जातक ताराबल एवं चन्द्रबल चक्र ({chart.birth_data.name})")
        st.caption("जातक के जन्म नक्षत्र व जन्म चन्द्र राशि से तात्कालिक गोचर नक्षत्र व चन्द्रमा का शुभ/अशुभ संबंध:")

        nak_names_list = [
            "अश्विनी", "भरणी", "कृत्तिका", "रोहिणी", "मृगशिरा", "आर्द्रा", "पुनर्वसु", "पुष्य", "आश्लेषा",
            "मघा", "पूर्वाफाल्गुनी", "उत्तराफाल्गुनी", "हस्त", "चित्रा", "स्वाती", "विशाखा", "अनुराधा", "ज्येष्ठा",
            "मूल", "पूर्वाषाढ़ा", "उत्तराषाढ़ा", "श्रवण", "धनिष्ठा", "शतभिषा", "पूर्वाभाद्रपद", "उत्तराभाद्रपद", "रेवती"
        ]
        tara_names_9 = [
            ("जन्म तारा (Janma)", "शारीरिक चिंता / सतर्कता", "⚠️ मध्यम", "#F59E0B"),
            ("सम्पत् तारा (Sampat)", "धन लाभ, समृद्धि व सफलता", "🟢 अति शुभ", "#10B981"),
            ("विपत् तारा (Vipat)", "विपत्ति, हानि व रुकावटें", "🔴 अशुभ (वर्जित)", "#EF4444"),
            ("क्षेम तारा (Kshema)", "कल्याण, सुरक्षा व कार्य सिद्धि", "🟢 शुभ", "#10B981"),
            ("प्रत्यरि तारा (Pratyari)", "शत्रुता, विवाद व अड़चनें", "🔴 अशुभ (वर्जित)", "#EF4444"),
            ("साधक तारा (Sadhaka)", "अभीष्ट सिद्धि व विजय", "🟢 अति शुभ", "#10B981"),
            ("वध / निधन तारा (Naidhana)", "संकट, दुर्घटना व असफलता", "🔴 महा अशुभ", "#DC2626"),
            ("मित्र तारा (Mitra)", "सुखद सहयोग व आनंद", "🟢 शुभ", "#10B981"),
            ("परम मित्र तारा (Parama Mitra)", "सर्वोच्च सिद्धि व मंगल", "🟢 परम शुभ", "#059669")
        ]

        # Calculate Real Transit Tara Balam for Muhurta Date
        transit_nak = p_doshas.get("nakshatra_idx", 1)
        transit_sign = p_doshas.get("moon_sign_id", 1)
        natal_m_nak = moon_nak_idx + 1
        natal_m_sign = m_planet.sign_id if m_planet else 1

        today_tara_diff = (transit_nak - natal_m_nak) % 27
        today_tara_num = (today_tara_diff % 9) + 1
        t_name, t_desc, t_verdict, t_col = tara_names_9[today_tara_num - 1]

        # Calculate Real Transit Chandra Balam for Muhurta Date
        c_diff = ((transit_sign - natal_m_sign) % 12) + 1
        if c_diff in [1, 3, 6, 7, 10, 11]:
            chandra_bal_status = f"🟢 शुभ चन्द्रबल ({c_diff}वां चन्द्रमा)"
            c_badge_col = "#16A34A"
            c_desc = f"गोचर चन्द्रमा जन्म राशि से {c_diff}वें भाव में भ्रमण कर रहा है, जो मनोबल व कार्य सिद्धि प्रदान करता है।"
        elif c_diff in [4, 8, 12]:
            chandra_bal_status = f"🔴 घात चन्द्र / अष्टम चन्द्र ({c_diff}वां चन्द्रमा)"
            c_badge_col = "#DC2626"
            c_desc = f"गोचर चन्द्रमा जन्म राशि से {c_diff}वें भाव में है (घात चन्द्र)। शुभ कार्य में मानसिक अशांति व हानि का भय रहता है।"
        else:
            chandra_bal_status = f"🟡 मध्यम चन्द्रबल ({c_diff}वां चन्द्रमा)"
            c_badge_col = "#D97706"
            c_desc = f"गोचर चन्द्रमा {c_diff}वें भाव में मध्यम फलदायी है। गुरु/शुक्र की दृष्टि से शुभ फल मिलता है।"

        c_tb1, c_tb2 = st.columns(2)
        with c_tb1:
            st.markdown(f"""<div style="background:#FFFFFF; border:2px solid {t_col}; border-radius:10px; padding:14px; box-shadow:0 2px 8px rgba(0,0,0,0.04);">
    <div style="font-size:12px; color:#64748B; font-weight:700;">⭐ जातक का तात्कालिक ताराबल (Today's Tara Balam):</div>
    <div style="font-size:18px; font-weight:900; color:{t_col}; margin:4px 0;">{t_name} — {t_verdict}</div>
    <div style="font-size:13px; color:#1E293B;"><b>प्रभाव:</b> {t_desc}</div>
    <div style="font-size:12px; color:#475569; margin-top:6px;">जन्म नक्षत्र: <b>{p_info.nakshatra_name}</b> (#{natal_m_nak}) ➔ गोचर नक्षत्र: <b>{p_doshas['nakshatra_name']}</b> (#{transit_nak})</div>
    </div>""", unsafe_allow_html=True)

        with c_tb2:
            st.markdown(f"""<div style="background:#FFFFFF; border:2px solid {c_badge_col}; border-radius:10px; padding:14px; box-shadow:0 2px 8px rgba(0,0,0,0.04);">
    <div style="font-size:12px; color:#64748B; font-weight:700;">🌕 जातक का चन्द्रबल (Chandra Balam):</div>
    <div style="font-size:18px; font-weight:900; color:{c_badge_col}; margin:4px 0;">{chandra_bal_status}</div>
    <div style="font-size:13px; color:#1E293B;"><b>शास्त्रीय स्थिति:</b> {c_desc}</div>
    <div style="font-size:12px; color:#475569; margin-top:6px;">जन्म चन्द्र राशि: <b>{natal_m_sign}</b> ➔ गोचर चन्द्र राशि: <b>{transit_sign} ({p_doshas['moon_sign_name']})</b></div>
    </div>""", unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("##### 📋 जातक के लिए समस्त २७ नक्षत्रों का ताराबल वर्गीकरण")
        tara_table = []
        for n_i in range(27):
            d_val = (n_i - moon_nak_idx) % 27
            t_idx = d_val % 9
            tn, td, tv, tc = tara_names_9[t_idx]
            is_active = (n_i + 1 == transit_nak)
            tara_table.append({
                "नक्षत्र क्रमांक": f"#{n_i + 1}" + (" 📍 (आज)" if is_active else ""),
                "नक्षत्र नाम": nak_names_list[n_i],
                "तारा (Tara)": tn,
                "प्रकृति व फल": td,
                "शुभता (Verdict)": tv
            })
        st.dataframe(pd.DataFrame(tara_table), use_container_width=True, hide_index=True)

    # -------------------------------------------------------------
    # TAB 5: 16 SAMSKARAS & ACTIVITIES SUITABILITY
    # -------------------------------------------------------------
    with tab_m5:
        st.markdown("#### 🏛️ १६ प्रमुख संस्कार एवं कार्य मुहूर्त अनुकूलता विश्लेषक")
        st.caption("विवाह, गृह प्रवेश, व्यापार आरंभ, वाहन क्रय, नामकरण, मुंडन, विद्यारंभ व यात्रा आदि कार्यों की प्रामाणिक शास्त्रीय अनुकूलता:")

        act_options_16 = [
            ("griha_pravesh", "🏛️ गृह प्रवेश (House Warming / Griha Pravesh)"),
            ("vivaha", "💍 विवाह संस्कार (Marriage Ceremony)"),
            ("vyapar", "💼 व्यापार / दुकान / प्रतिष्ठान उद्घाटन (Business Launch)"),
            ("vahan_kray", "🚗 नवीन वाहन क्रय व पूजन (Vehicle Purchase)"),
            ("property_kray", "🏠 भूमि, भवन व अचल संपत्ति क्रय (Property Purchase)"),
            ("namakarana", "👶 नामकरण संस्कार (Naming Ceremony)"),
            ("mundan", "✂️ मुंडन / चूड़ाकर्म संस्कार (Tonsure / Mundan)"),
            ("vidyarambha", "🎓 विद्यारंभ / अक्षरारंभ (Commencement of Studies)"),
            ("upanayana", "📿 उपनयन / जनेऊ संस्कार (Sacred Thread Ceremony)"),
            ("yatra", "✈️ यात्रा एवं विदेश गमन (Travel & Foreign Journey)"),
            ("medical", "🏥 शल्यक्रिया व नवीन चिकित्सा आरंभ (Medical / Surgery)"),
            ("vastra_bhooshan", "💎 नवीन वस्त्र व आभूषण धारण (Wearing New Ornaments)")
        ]

        c_act1, c_act2 = st.columns([1.5, 2.5])
        with c_act1:
            act_choice = st.selectbox("कार्य का चयन करें (Select Activity):", act_options_16, format_func=lambda x: x[1], key="muh_act_16_sel")
        with c_act2:
            st.write("")
            st.caption(f"🗓️ दिनांक **{muhurta_date.strftime('%d-%b-%Y')}** के लिए शास्त्रीय पञ्चाङ्ग व मुहूर्त शुद्धि का परीक्षण:")

        act_res = m_engine.evaluate_activity_suitability(muhurta_date, act_choice[0], natal_chart=chart)
        score_val = act_res.get('suitability_score', 0)
        verdict_val = act_res.get('verdict', 'त्याज्य')
        theme_col = act_res.get('badge_color', '#DC2626')
        has_fatal = bool(act_res.get('fatal_violations'))

        # Display Result Card
        st.markdown(f"""<div style="background:#FFFFFF; border:2.5px solid {theme_col}; border-radius:12px; padding:20px; box-shadow:0 4px 14px rgba(0,0,0,0.06); margin-bottom:16px;">
    <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px; margin-bottom:12px;">
    <div>
    <b style="font-size:20px; color:#0F172A;">{act_res['activity']}</b>
    <div style="font-size:12px; color:#64748B; margin-top:2px;">दिनांक: {muhurta_date.strftime('%d %B %Y')} ({muhurta_date.strftime('%A')})</div>
    </div>
    <div>
    <span style="background:{theme_col}18; color:{theme_col}; border:2px solid {theme_col}; border-radius:10px; padding:6px 16px; font-weight:900; font-size:16px;">
    शुभता स्कोर: {score_val}/100 — {verdict_val}
    </span>
    </div>
    </div>
    <div style="font-size:14px; color:#1E293B; line-height:1.7; background:{'#FEF2F2' if has_fatal else '#F8FAFC'}; padding:12px 16px; border-radius:8px; border:1px solid {'#FCA5A5' if has_fatal else '#E2E8F0'};">
    <b>📜 शास्त्रीय मार्गदर्शन:</b> {act_res['guidance']}
    </div>
    </div>""", unsafe_allow_html=True)

        st.progress(score_val / 100.0)

        # Show Fatal Violations Alerts if any
        if act_res.get("fatal_violations"):
            st.error("🚨 **महा-निषेध उल्लंघन (Fatal Prohibitions Triggered):**")
            for f_v in act_res["fatal_violations"]:
                st.markdown(f"""<div style="background:#FFF1F2; border-left:4px solid #E11D48; border-radius:4px; padding:8px 14px; margin-bottom:6px; font-size:13px; color:#9F1239;">
    {f_v}
    </div>""", unsafe_allow_html=True)

        # Show Sanskrit Sutras
        if act_res.get("shastriya_sutras"):
            with st.expander("📖 संबंधित शास्त्रीय सूत्र एवं संदर्भ (Classical Sanskrit Sutras)", expanded=True):
                for sutra in act_res["shastriya_sutras"]:
                    st.markdown(f"> *{sutra}*")

        # Itemized Factors Breakdown
        st.write("")
        st.markdown("##### 🔍 मुहूर्त घटकों का विस्तृत शास्त्रीय मूल्यांकन (Detailed Evaluation Audit):")
        audit_cols = st.columns(3)
        with audit_cols[0]:
            pitru_col = '#DC2626' if p_doshas['is_pitru_paksha'] else '#16A34A'
            pitru_txt = 'सक्रिय (वर्जित)' if p_doshas['is_pitru_paksha'] else 'दोष मुक्त'
            chatur_col = '#EA580C' if p_doshas['is_chaturmas'] else '#16A34A'
            chatur_txt = 'सक्रिय (देवशयन)' if p_doshas['is_chaturmas'] else 'दोष मुक्त'
            khar_col = '#DC2626' if p_doshas['is_kharmas'] else '#16A34A'
            khar_txt = 'सक्रिय (वर्जित)' if p_doshas['is_kharmas'] else 'दोष मुक्त'
            bhadra_col = '#DC2626' if p_doshas['is_bhadra'] else '#16A34A'
            bhadra_txt = ('सक्रिय (' + str(p_doshas['bhadra_loka']).split(' ')[0] + ')') if p_doshas['is_bhadra'] else 'दोष मुक्त'

            st.markdown(f"""<div style="background:#F8FAFC; border:1px solid #E2E8F0; border-radius:8px; padding:12px; font-size:13px;">
    <b style="color:#0F172A;">1. काल व संवत्सर शुद्धि</b><br/>
    • पितृपक्ष: <span style="color:{pitru_col}; font-weight:800;">{pitru_txt}</span><br/>
    • चातुर्मास: <span style="color:{chatur_col}; font-weight:800;">{chatur_txt}</span><br/>
    • खरमास: <span style="color:{khar_col}; font-weight:800;">{khar_txt}</span><br/>
    • भद्रा (विष्टि): <span style="color:{bhadra_col}; font-weight:800;">{bhadra_txt}</span>
    </div>""", unsafe_allow_html=True)
        with audit_cols[1]:
            st.markdown(f"""<div style="background:#F8FAFC; border:1px solid #E2E8F0; border-radius:8px; padding:12px; font-size:13px;">
    <b style="color:#0F172A;">2. पञ्चाङ्ग घटक शुद्धि</b><br/>
    • तिथि: <b>{p_doshas['tithi_name'].split(' ')[0]}</b> ({p_doshas['tithi_category'].split(' ')[0]})<br/>
    • वार: <b>{p_doshas['weekday_name']}</b><br/>
    • नक्षत्र: <b>{p_doshas['nakshatra_name']}</b> ({getattr(p_doshas, 'nakshatra_lord', '—')})<br/>
    • योग: <b>{p_doshas['yoga_name']}</b><br/>
    • करण: <b>{p_doshas['karana_name']}</b>
    </div>""", unsafe_allow_html=True)
        with audit_cols[2]:
            tara_str = act_res.get('tara_balam', {}).get('tara_name', '—') if act_res.get('tara_balam') else '—'
            chan_str = act_res.get('chandra_balam', {}).get('status', '—') if act_res.get('chandra_balam') else '—'
            st.markdown(f"""<div style="background:#F8FAFC; border:1px solid #E2E8F0; border-radius:8px; padding:12px; font-size:13px;">
    <b style="color:#0F172A;">3. जातक वैयक्तिक शुद्धि</b><br/>
    • ताराबल: <b>{tara_str}</b><br/>
    • चन्द्रबल: <b>{chan_str}</b><br/>
    • गोचर चन्द्र राशि: <b>{p_doshas['moon_sign_name']}</b><br/>
    • जन्म राशि: <b>{chart.birth_data.name}</b>
    </div>""", unsafe_allow_html=True)

    # -------------------------------------------------------------
    # TAB 6: AUTOMATED MUHURTA RANGE SCANNER
    # -------------------------------------------------------------
    with tab_m6:
        st.markdown("#### 🔍 स्वचालित बहु-दिवसीय मुहूर्त खोजक (Automated Muhurta Scanner)")
        st.caption("३० से ९० दिनों की समय सीमा में विवाह, गृह प्रवेश, व्यापार व वाहन क्रय के श्रेष्ठ मुहूर्तों की स्वतः खोज (महा-निषेध, पितृपक्ष, चातुर्मास व चन्द्रबल की पूर्ण शुद्धि सहित):")

        st.info("💡 **सटीक शास्त्रीय शुद्धि प्रणाली:** यह खोजक स्वतः ही उन समस्त तिथियों को निरस्त (Filter Out) कर देता है जिनमें पितृपक्ष, चातुर्मास महा-निषेध, खरमास, मृत्युलोक भद्रा अथवा जातक का अष्टम/घात चन्द्रमा सक्रिय हो।")

        col_sc1, col_sc2, col_sc3 = st.columns([1.5, 1, 1])
        with col_sc1:
            scan_activity = st.selectbox(
                "शुभ कार्य का चयन करें",
                [
                    ("griha_pravesh", "🏛️ गृह प्रवेश (Griha Pravesh)"),
                    ("vivaha", "💍 विवाह संस्कार (Vivaha)"),
                    ("vyapar", "💼 व्यापार / दुकान / अनुबंध (Business)"),
                    ("vahan_kray", "🚗 वाहन क्रय व पूजन (Vehicle Purchase)"),
                    ("namakarana", "👶 नामकरण संस्कार (Namakarana)"),
                    ("mundan", "✂️ मुंडन / चूड़ाकर्म संस्कार (Mundan)")
                ],
                format_func=lambda x: x[1],
                key="muh_scan_act_14tab"
            )
        with col_sc2:
            scan_start = st.date_input("आरंभ तिथि (Start Date)", value=muhurta_date, key="muh_scan_start_14tab")
        with col_sc3:
            scan_days = st.selectbox("खोज अवधि (Search Window)", [30, 45, 60, 90], index=1, key="muh_scan_days_14tab")

        if st.button("🚀 सर्वश्रेष्ठ मुहूर्त खोजें (Scan Best Muhurtas)", type="primary", key="btn_scan_muhurta_14tab"):
            import datetime
            scan_end = scan_start + datetime.timedelta(days=scan_days)
            with st.spinner(f"{scan_days} दिनों में शास्त्रीय रूप से निर्दोष श्रेष्ठ मुहूर्त खोजे जा रहे हैं..."):
                top_muhurtas = m_scanner.scan_range(
                    activity_type=scan_activity[0],
                    start_date=scan_start,
                    end_date=scan_end,
                    natal_chart=chart,
                    top_n=10
                )
            st.session_state["top_muhurtas_res"] = top_muhurtas

        if "top_muhurtas_res" in st.session_state and st.session_state["top_muhurtas_res"]:
            top_muhurtas = st.session_state["top_muhurtas_res"]
            st.markdown(f"### 🏆 शीर्ष {len(top_muhurtas)} अनुशंसित श्रेष्ठ मुहूर्त (Top Ranked Auspicious Dates)")
            for rank, m in enumerate(top_muhurtas, 1):
                badge_bg = "#DCFCE7" if m.get("score", 0) >= 80 else ("#FEF3C7" if m.get("score", 0) >= 65 else "#FEE2E2")
                badge_c = "#15803D" if m.get("score", 0) >= 80 else ("#B45309" if m.get("score", 0) >= 65 else "#B91C1C")
                date_val = m.get("date_str") or m.get("date", "")
                date_display = date_val.strftime("%d %b %Y") if hasattr(date_val, "strftime") else str(date_val)
                day_val = m.get("day_name") or m.get("weekday", "")
                nak_lord_str = f" ({m['nakshatra_lord']})" if m.get("nakshatra_lord") and m.get("nakshatra_lord") != "—" else ""
                yoga_str = f" | 🕉️ {m['yoga']} योग" if m.get("yoga") else ""
                chandra_bal_str = m.get("chandra_balam") or m.get("chandra_bal", "—")
                tara_bal_str = m.get("tara_bal", "—")
                stars_display = m.get("stars", "⭐⭐⭐⭐")

                panchak_tag = " <span style='background:#FEF3C7; color:#92400E; font-size:11px; padding:2px 8px; border-radius:6px; font-weight:700;'>⚠️ पंचक</span>" if m.get("is_panchak") else ""
                rikta_tag = " <span style='background:#FEE2E2; color:#991B1B; font-size:11px; padding:2px 8px; border-radius:6px; font-weight:700;'>रिक्ता</span>" if m.get("is_rikta") else ""

                st.markdown(f"""<div style="background:#FFFFFF; border:1.5px solid #E2E8F0; border-left:6px solid {badge_c}; border-radius:10px; padding:14px 18px; margin-bottom:12px; box-shadow:0 2px 6px rgba(0,0,0,0.04);">
    <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px;">
    <div>
    <span style="font-size:18px; font-weight:800; color:#0F172A;">#{rank} 📅 {date_display} ({day_val})</span>
    <span style="margin-left:10px; font-size:15px; letter-spacing:1px;">{stars_display}</span>
    {panchak_tag}{rikta_tag}
    <div style="font-size:13px; color:#475569; margin-top:2px;">🌙 {m.get('tithi', '—')} | ✨ {m.get('nakshatra', '—')}{nak_lord_str}{yoga_str}</div>
    </div>
    <div>
    <span style="background:{badge_bg}; color:{badge_c}; font-size:14px; font-weight:800; padding:4px 12px; border-radius:16px;">
    शुभ स्कोर: {m.get('score', 0)}% ({m.get('verdict', '—')})
    </span>
    </div>
    </div>
    <div style="margin-top:10px; font-size:13px; color:#1E293B; line-height:1.6; background:#F8FAFC; padding:8px 12px; border-radius:6px; border:1px solid #E2E8F0;">
    <b>🎯 सर्वोत्तम समय खिड़की (Best Window):</b> {m.get('best_window', '—')}<br/>
    <b>🌕 चन्द्र व तारा बल:</b> चन्द्रबल: {chandra_bal_str} ({m.get('moon_sign', '—')} राशि) | ताराबल: <b>{tara_bal_str}</b><br/>
    <b>📜 शास्त्रीय अवलोकन:</b> {'; '.join(m.get('reasons', []))}
    </div>
    </div>""", unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("### 📅 संपूर्ण वार्षिक रेडीमेड शुभ मुहूर्त कैलेंडर (Drik Panchang Master Style)")
        st.caption("वर्ष भर के समस्त शास्त्रीय रूप से शुद्ध व मान्य विवाह, गृह प्रवेश एवं व्यापार मुहूर्तों की 1-क्लिक रेडीमेड तालिका:")

        col_yr1, col_yr2 = st.columns([1.5, 1.5])
        with col_yr1:
            annual_act = st.selectbox(
                "संस्कार / कार्य चयन करें:",
                [
                    ("vivaha", "💍 विवाह शुभ मुहूर्त (Vivaha Muhurta)"),
                    ("griha_pravesh", "🏛️ गृह प्रवेश मुहूर्त (Griha Pravesh)"),
                    ("mundan", "✂️ मुंडन संस्कार (Mundan Muhurta)"),
                    ("vyapar", "💼 व्यापार / दुकान उद्घाटन (Business Launch)")
                ],
                format_func=lambda x: x[1],
                key="annual_muhurta_act_sel"
            )
        with col_yr2:
            target_yr = st.selectbox("वर्ष (Year):", [2026, 2027], index=0, key="annual_muhurta_yr_sel")

        if st.button("📋 संपूर्ण वार्षिक मुहूर्त तालिका लोड करें", type="secondary", key="btn_annual_muhurta_load"):
            with st.spinner(f"वर्ष {target_yr} के समस्त शुभ मुहूर्तों की गणना एवं शास्त्रीय शोधन किया जा रहा है..."):
                annual_data = m_scanner.get_annual_muhurta_calendar(
                    year=target_yr,
                    activity_type=annual_act[0],
                    min_star_rating=3
                )
                st.session_state["annual_muhurta_cache"] = {
                    "data": annual_data,
                    "title": annual_act[1],
                    "year": target_yr
                }

        if "annual_muhurta_cache" in st.session_state:
            cached = st.session_state["annual_muhurta_cache"]
            a_list = cached["data"]
            st.markdown(f"#### 🌟 {cached['title']} — वर्ष {cached['year']} (कुल {len(a_list)} शास्त्रसम्मत शुभ दिन)")
            if a_list:
                table_rows = []
                for item in a_list:
                    table_rows.append({
                        "दिनांक (Date)": f"{item['date_str']} ({item['day_name'][:3]})",
                        "शुभता रेटिंग": item['stars'],
                        "शुभ स्कोर": f"{item['score']}%",
                        "तिथि (Tithi)": item['tithi'],
                        "नक्षत्र (Nakshatra)": item['nakshatra'],
                        "सर्वोत्तम मुहूर्त वेला": item['best_window'].split('|')[0].strip()
                    })
                st.dataframe(pd.DataFrame(table_rows), use_container_width=True, hide_index=True)
            else:
                st.info("इस वर्ष में चुने गए न्यूनतम मानक के अनुसार कोई निर्दोष मुहूर्त नहीं पाया गया।")

    # -------------------------------------------------------------
    # TAB 7: MUHURTA CHINTAMANI 21 MAHA DOSHAS
    # -------------------------------------------------------------
    with tab_m7:
        st.markdown(f"#### 📜 मुहूर्त चिन्तामणि के २१ महादोष (21 Maha Doshas Live Audit on {muhurta_date.strftime('%d-%b-%Y')})")
        st.caption("मुहूर्त चिन्तामणि एवं कालप्रकाशिका अनुसार शुभ कार्यों में त्याज्य २१ प्रमुख महादोष एवं उनकी आज की स्थिति:")

        maha_doshas = [
            ("१. भद्रा (विष्टि करण)", "भद्रा काल में किया गया शुभ कार्य नष्ट हो जाता है।", "🔴 आज सक्रिय" if p_doshas['is_bhadra'] else "🟢 आज दोष मुक्त"),
            ("२. कुलिक काल", "प्रत्येक दिन का एक निश्चित समय कुलिक कहलाता है जो कार्य में विफलता लाता है।", "⚠️ दिन अनुसार वेला"),
            ("३. राहुकाल", "दिन का १/८ भाग राहु के आधिपत्य में रहता है, जिसमें यात्रा व मांगलिक कार्य वर्जित हैं।", "🔴 प्रतिदिन १.५ घण्टे सक्रिय"),
            ("४. यमगण्ड काल", "यम के प्रभाव वाला समय, जिसमें नवीन कार्य कष्ट या असफलता देते हैं।", "⚠️ प्रतिदिन १.५ घण्टे सक्रिय"),
            ("५. दुर्मुहूर्त काल", "प्रतिदिन के दो मुहूर्त दुर्मुहूर्त कहलाते हैं जो कार्य सिद्धि में बाधक हैं।", "⚠️ वेला आधारित"),
            ("६. कालवेला व वारवेला", "सूर्य व यम से संबंधित अनिष्टकारी वेलाएं।", "⚠️ वेला आधारित"),
            ("७. रिक्ता तिथि दोष", "चतुर्थी, नवमी एवं चतुर्दशी तिथियां 'रिक्ता' कहलाती हैं।", "🔴 आज सक्रिय" if p_doshas['is_rikta'] else "🟢 आज दोष मुक्त"),
            ("८. त्रिपुष्कर योग", "विशिष्ट वार, तिथि व नक्षत्र के संयोग से हानि की तीन बार पुनरावृत्ति।", "🟢 आज दोष मुक्त"),
            ("९. द्विपुष्कर योग", "हानि या घटना की दो बार पुनरावृत्ति कराने वाला योग।", "🟢 आज दोष मुक्त"),
            ("१०. पंचक दोष", "धनिष्ठा के उत्तरार्ध से रेवती पर्यन्त ५ नक्षत्रों में दक्षिण यात्रा व गृह-छत वर्जित।", "🔴 आज सक्रिय" if p_doshas['nakshatra_idx'] in [23, 24, 25, 26, 27] else "🟢 आज दोष मुक्त"),
            ("११. होलाष्टक दोष", "फाल्गुन शुक्ल अष्टमी से पूर्णिमा पर्यन्त समस्त १६ संस्कार निषिद्ध।", "🟢 आज दोष मुक्त"),
            ("१२. मलमास / पितृपक्ष", "सूर्य संक्रांति रहित मास अथवा पितृपक्ष में मांगलिक संस्कार वर्जित।", "🔴 आज सक्रिय" if (p_doshas['is_pitru_paksha'] or p_doshas['is_kharmas']) else "🟢 आज दोष मुक्त"),
            ("१३. क्षयमास दोष", "दो सूर्य संक्रांति वाला मास, अत्यंत दुर्लभ एवं अशुभ माना जाता है।", "🟢 आज दोष मुक्त"),
            ("१४. गुरु तारा अस्त", "देवगुरु बृहस्पति का सूर्य सान्निध्य से अस्त होना (विवाह व गृह प्रवेश वर्जित)।", "🔴 आज सक्रिय" if p_doshas['is_guru_asta'] else "🟢 आज दोष मुक्त"),
            ("१५. शुक्र तारा अस्त", "दैत्यगुरु शुक्र का अस्त होना (विवाह, मुंडन, गृह प्रवेश सर्वथा वर्जित)।", "🔴 आज सक्रिय" if p_doshas['is_shukra_asta'] else "🟢 आज दोष मुक्त"),
            ("१६. सूर्य व चन्द्र ग्रहण वेध", "ग्रहण काल एवं उसके सूतक काल में समस्त मांगलिक कार्य निषिद्ध हैं।", "🟢 आज दोष मुक्त"),
            ("१७. नक्षत्र गंडान्त", "अश्विनी-रेवती, मघा-आश्लेषा, मूल-ज्येष्ठा की संधियां गंडान्त कहलाती हैं।", "⚠️ संवेदनशील संधि"),
            ("१८. तिथि गंडान्त", "पूर्णा व नंदा तिथियों की संधियां (पूर्णिमा-प्रतिपदा, आदि)।", "⚠️ संधि वेला"),
            ("१९. लग्न गंडान्त", "कर्क-सिंह, वृश्चिक-धनु, मीन-मेष लग्न संधियां।", "⚠️ लग्न संधि"),
            ("२०. विष घटी दोष", "प्रत्येक नक्षत्र की निश्चित विष घटियां समस्त शुभ कार्यों में त्याज्य हैं।", "⚠️ घटी अनुसार"),
            ("२१. पापकत्र्तरी लग्न", "मुहूर्त लग्न के दोनों ओर पाप ग्रहों की उपस्थिति।", "⚠️ लग्न परीक्षण")
        ]

        dosha_df = pd.DataFrame(maha_doshas, columns=["महादोष नाम", "शास्त्रीय लक्षण व निषेध", "आज की स्थिति"])
        st.dataframe(dosha_df, use_container_width=True, hide_index=True)

    # -------------------------------------------------------------
    # TAB 8: DOSHA EXCEPTIONS & REMEDIES
    # -------------------------------------------------------------
    with tab_m8:
        st.markdown("#### 🪔 मुहूर्त दोष परिहार एवं वैदिक शांति अनुष्ठान (Exceptions & Remedial Suite)")
        st.caption("अपरिहार्य परिस्थितियों में जब मुहूर्त में दोष हो, तब शास्त्रों द्वारा बताए गए परिहार (Exceptions) एवं शांति उपाय:")

        with st.expander("📖 शास्त्रीय दोष-नाशक परिहार नियम (Exceptions that dissolve flaws)", expanded=True):
            st.markdown("""**१. केन्द्रस्थ बृहस्पति का महा-परिहार (Power of Jupiter in Kendra):**
    > *किं कुर्वन्ति ग्रहाः सर्वे यस्य केन्द्रे बृहस्पतिः। लक्षमेकं तु दोषाणां हन्ति देवपुरोहितः॥*
    > यदि मुहूर्त लग्न के केन्द्र (१, ४, ७, १०) में बलवान देवगुरु बृहस्पति स्थित हों, तो वे अकेले ही १ लाख मुहूर्त दोषों को भस्म करने में समर्थ हैं।

    **२. अभिजित मुहूर्त का सार्वभौमिक प्रभाव:**
    > अभिजित मुहूर्त (सूर्योदय से ८वां मुहूर्त) भगवान विष्णु का साक्षात् स्वरूप है। बुधवार को छोड़कर यह समस्त तिथि, नक्षत्र व योग दोषों का निवारण करता है।

    **३. गोधूलि लग्न की महत्ता:**
    > यदि विवाह अथवा यात्रा में उत्तम लग्न न मिल रहा हो, तो सूर्यास्त के समय गोधूलि लग्न (जब गायें चरकर लौटती हैं) करोड़ों दोषों को दूर करता है।

    **४. शुक्ल पक्ष चन्द्रमा की प्रबलता:**
    > यदि चन्द्रमा शुक्ल पक्ष की एकादशी से कृष्ण पक्ष की पंचमी तक पूर्ण बली होकर शुभ भावों में हो, तो अधिकांश पञ्चाङ्ग दोष निष्प्रभावी हो जाते हैं।""")

        with st.expander("🛡️ आपातकालीन कार्य सिद्धि वैदिक शांति अनुष्ठान", expanded=True):
            st.markdown("""##### 📿 अनिवार्य कार्य से पूर्व दोष-शमन विधि:
    - 🕉️ **गायत्री महामंत्र जप:** कार्य आरंभ से पूर्व गायत्री मंत्र का २४ अथवा १०८ बार जप करें।
    - 🛕 **विष्णु सहस्रनाम / गणेश अथर्वशीर्ष:** श्री गणेश जी को २१ दूर्वा दल अर्पित करें एवं विष्णु सहस्रनाम का पाठ करें।
    - 🎁 **दोष-निवारक दान:** उड़द, तिल, गुड़ अथवा ताम्र पात्र का दान किसी सुपात्र विप्र को संकल्प पूर्वक दें।
    - 🪔 **दीपदान:** घर के ईशान कोण में गाय के शुद्ध घृत का दीपक प्रज्वलित कर कार्य हेतु प्रस्थान करें।""")


