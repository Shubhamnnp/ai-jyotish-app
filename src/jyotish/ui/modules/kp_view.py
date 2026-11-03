import streamlit as st
import pandas as pd
from datetime import datetime, timezone, timedelta, date, time
import importlib
from src.jyotish.models import BirthData
from src.jyotish.core.calculator import default_chart_calculator
from src.jyotish.services.geocoding import default_geocoding_service
from src.jyotish.services.shastriya_pramana import SHASTRIYA_SHLOKAS

def get_live_local_now(tz_offset_hours: float = 5.5) -> datetime:
    return datetime.now(timezone.utc) + timedelta(hours=tz_offset_hours)

def render_kp_view(chart, tz_offset=5.5, default_city_name=None, tabs=None):
    if default_city_name is None:
        default_city_name = st.session_state.get("birth_city", "New Delhi, Delhi, India")
        
    if tabs is None:
        tabs = [
            '🪐 ग्रह एवं भाव उप-स्वामी (Cuspal Sublords)',
            '🔢 ४-चरणीय कारकत्व (4-Step Significators)',
            '🎯 केपी घटना विश्लेषण (KP Event Analysis)',
            '🔮 तात्कालिक प्रश्न (KP Horary 1-249)',
            '👑 रूलिंग प्लैनेट्स (KP Ruling Planets)'
        ]
    st.subheader("📐 के.पी. ज्योतिष प्रणाली (Krishnamurti Paddhati - Complete Professional KP System)")
    st.write("प्रोफेसर के.एस. कृष्णमूर्ति (KP Readers I-VI) प्रतिपादित ४-स्तरीय कार्यकत्व, कस्पल सब-लॉर्ड, रूलिंग प्लैनेट्स, १-२४९ होरारी, पाश्चात्य दृष्टि एवं अचूक भविष्य फलित निर्णय।")

    import importlib
    import src.jyotish.core.kp as kp_mod
    import src.jyotish.dasha.vimshottari as vim_mod
    if not hasattr(kp_mod.default_kp_engine, "predict_kp_query"):
        importlib.reload(kp_mod)
    k_engine = kp_mod.default_kp_engine
    d_engine = vim_mod.default_dasha_engine

    # =========================================================================
    # TWO WORKING MODES: 1. ACTIVE NATIVE  2. NEW NATIVE / HORARY PRASHNAKARTA
    # =========================================================================
    st.markdown("#### 🎯 के.पी. कार्यक्षेत्र एवं जातक मोड चयन (Working Mode):")
    col_m_sel1, col_m_sel2 = st.columns([2, 3])
    with col_m_sel1:
        kp_user_mode = st.radio(
            "मोड चुनें:",
            [
                "👤 १. सक्रिय जातक कुण्डली (Current Loaded Native)",
                "🔮 २. नवीन जातक / तत्कालिक प्रश्नकर्ता (New Native / Horary Prashnakarta)"
            ],
            key="kp_main_user_mode_radio"
        )

    active_kp_chart = chart
    chosen_horary_num = None
    live_kp_now = get_live_local_now(tz_offset)
    target_query_dt = live_kp_now

    if "१. सक्रिय जातक" in kp_user_mode:
        with col_m_sel2:
            st.markdown(f"""<div style="background:#F0FDF4; border:1.5px solid #22C55E; border-radius:10px; padding:12px 16px;">
    <b style="color:#15803D; font-size:14px;">👤 सक्रिय जातक विवरण (Active Native):</b><br/>
    • <b>नाम:</b> {chart.birth_data.name} &nbsp;|&nbsp; <b>जन्म दिनांक:</b> {chart.birth_data.birth_date.strftime('%d-%b-%Y')} ({chart.birth_data.birth_time.strftime('%H:%M')})<br/>
    • <b>स्थान:</b> {getattr(chart.birth_data, 'city_name', str(default_city_name))} &nbsp;|&nbsp; <b>लग्न:</b> {chart.lagna_sign_id} राशि ({chart.lagna_degree:.2f}°)
    </div>""", unsafe_allow_html=True)
    else:
        with col_m_sel2:
            sub_mode = st.radio(
                "प्रकार चुनें:",
                ["🔢 (क) तत्कालिक १-२४९ होरारी प्रश्न (KP 1-249 Horary)", "👶 (ख) नवीन जातक जन्म कुण्डली (New Native Birth Chart)"],
                horizontal=True,
                key="kp_new_sub_mode"
            )

        if "१-२४९ होरारी" in sub_mode:
            st.markdown("##### 🔮 तत्कालिक के.पी. १-२४९ होरारी प्रश्न विवरण दर्ज करें:")
            c_hq1, c_hq2, c_hq3, c_hq4 = st.columns([1.2, 1.2, 1.2, 1.4])
            with c_hq1:
                chosen_horary_num = st.number_input("🔢 होरारी संख्या (1 - 249)", min_value=1, max_value=249, value=108, step=1, key="kp_horary_input_num_14tab")
            with c_hq2:
                q_date = st.date_input("📅 प्रश्न दिनांक (Date)", value=live_kp_now.date(), format="DD/MM/YYYY", key="kp_q_date_14tab")
            with c_hq3:
                q_time = st.time_input("⏰ प्रश्न समय (Time)", value=live_kp_now.time().replace(microsecond=0), step=1, key="kp_q_time_14tab")
            with c_hq4:
                q_city = st.text_input("📍 प्रश्न स्थान (City)", value=default_city_name, key="kp_q_city_14tab")

            target_query_dt = datetime.combine(q_date, q_time)
            loc_res = default_geocoding_service.resolve(q_city)
            if loc_res:
                h_lat = float(loc_res.get("latitude", 28.6139))
                h_lon = float(loc_res.get("longitude", 77.2090))
                h_tz = float(loc_res.get("timezone_offset", 5.5))
                h_city = loc_res.get("city", q_city)
            else:
                h_lat, h_lon, h_tz, h_city = 28.6139, 77.2090, 5.5, q_city

            h_bdata = BirthData(
                name=f"KP Horary #{chosen_horary_num}",
                gender="Unknown",
                birth_date=q_date,
                birth_time=q_time,
                latitude=h_lat,
                longitude=h_lon,
                timezone_offset=h_tz,
                city_name=h_city
            )
            try:
                active_kp_chart = default_chart_calculator.calculate_full_chart(h_bdata)
                h_entry = k_engine.get_horary_number_detail(int(chosen_horary_num))
                active_kp_chart.lagna_longitude = h_entry["start_lon"]
                active_kp_chart.lagna_sign_id = h_entry["sign_id"]
                active_kp_chart.lagna_degree = h_entry["start_deg"]
            except Exception as e:
                st.warning(f"होरारी गणना में त्रुटि: {e}")
                active_kp_chart = chart
        else:
            st.markdown("##### 👶 नवीन जातक जन्म विवरण दर्ज करें:")
            c_nb1, c_nb2, c_nb3, c_nb4, c_nb5 = st.columns([1.5, 1, 1.2, 1.2, 1.5])
            with c_nb1:
                n_name = st.text_input("नाम (Name)", value="नवीन जातक", key="kp_new_name")
            with c_nb2:
                n_gender = st.selectbox("लिंग", ["पुरुष", "स्त्री", "अन्य"], key="kp_new_gender")
            with c_nb3:
                n_date = st.date_input("जन्म तिथि", value=date(2000, 1, 1), format="DD/MM/YYYY", key="kp_new_date")
            with c_nb4:
                n_time = st.time_input("जन्म समय", value=time(12, 0), key="kp_new_time")
            with c_nb5:
                n_city = st.text_input("जन्म स्थान", value=default_city_name, key="kp_new_city")

            target_query_dt = datetime.combine(n_date, n_time)
            loc_res = default_geocoding_service.resolve(n_city)
            if loc_res:
                n_lat = float(loc_res.get("latitude", 28.6139))
                n_lon = float(loc_res.get("longitude", 77.2090))
                n_tz = float(loc_res.get("timezone_offset", 5.5))
                n_city_str = loc_res.get("city", n_city)
            else:
                n_lat, n_lon, n_tz, n_city_str = 28.6139, 77.2090, 5.5, n_city

            n_bdata = BirthData(
                name=n_name,
                gender="Male" if n_gender == "पुरुष" else "Female",
                birth_date=n_date,
                birth_time=n_time,
                latitude=n_lat,
                longitude=n_lon,
                timezone_offset=n_tz,
                city_name=n_city_str
            )
            try:
                active_kp_chart = default_chart_calculator.calculate_full_chart(n_bdata)
            except Exception as e:
                st.warning(f"नवीन चार्ट गणना त्रुटि: {e}")
                active_kp_chart = chart

    # =========================================================================
    # KP CORE COMPUTATIONS & HUD
    # =========================================================================
    kp_chart_data = k_engine.calculate_chart_kp(active_kp_chart)
    rp_info = kp_chart_data["ruling_planets"]
    cusps_data = kp_chart_data["cusps_kp"]
    planets_kp_data = kp_chart_data["planets_kp"]
    p_sigs = kp_chart_data["planet_significations"]
    h_sigs = kp_chart_data["house_significators"]

    lagna_csl = cusps_data[0]
    moon_kp_obj = next((p for p in planets_kp_data if p["planet"] == "Moon"), planets_kp_data[1])

    b_str_kp = (
        f"<div style='background: #FFFBEB; border: 2px solid #F59E0B; padding: 14px 18px; border-radius: 12px; margin-bottom: 16px; box-shadow: 0 2px 10px rgba(0,0,0,0.06);'>"
        f"<div style='font-size: 13px; color: #92400E; font-weight: 800; margin-bottom: 8px;'>🧭 सक्रिय के.पी. लग्न व चन्द्र सब-लॉर्ड पदानुक्रम (Active KP Hierarchy & Ruling Planets):</div>"
        f"<div style='font-size: 15px; font-weight: 800; color: #1E293B; display: flex; flex-wrap: wrap; gap: 8px; align-items: center;'>"
        f"<span style='background:#EEF2FF; border:1.5px solid #6366F1; color:#312E81; padding:5px 12px; border-radius:8px;'>👑 लग्न CSL: {lagna_csl['sub_lord']} ({lagna_csl['sign']})</span> "
        f"<span style='color:#F59E0B; font-weight:900;'>➔</span> "
        f"<span style='background:#F0FDF4; border:1.5px solid #22C55E; color:#064E3B; padding:5px 12px; border-radius:8px;'>🌙 चन्द्र CSL: {moon_kp_obj['sub_lord']} (नक्षत्र: {moon_kp_obj['star_lord']})</span> "
        f"<span style='color:#F59E0B; font-weight:900;'>➔</span> "
        f"<span style='background:#FEF3C7; border:1.5px solid #F59E0B; color:#78350F; padding:5px 12px; border-radius:8px;'>⚡ वार स्वामी: {rp_info['day_lord']['planet']}</span> "
        f"<span style='color:#F59E0B; font-weight:900;'>➔</span> "
        f"<span style='background:#FDF2F8; border:1.5px solid #EC4899; color:#831843; padding:5px 12px; border-radius:8px;'>👑 मुख्य RPs: {', '.join(rp_info['all_rp_list'][:4])}</span>"
        f"</div>"
        f"</div>"
    )
    st.markdown(b_str_kp, unsafe_allow_html=True)

    c_k1, c_k2, c_k3, c_k4 = st.columns(4)
    with c_k1:
        st.markdown(f"""<div style="background:#EEF2FF; border: 2px solid #6366F1; border-radius:10px; padding:10px; text-align:center;">
    <div style="font-size:11.5px; color:#4338CA; font-weight:800;">👑 लग्न कस्पल सब-लॉर्ड (L1 CSL)</div>
    <div style="font-size:18px; font-weight:900; color:#1E1B4B;">{lagna_csl['sub_lord']}</div>
    <div style="font-size:10.5px; color:#475569;">Star: {lagna_csl['star_lord']} | SSL: {lagna_csl['sub_sub_lord']}</div>
    </div>""", unsafe_allow_html=True)
    with c_k2:
        st.markdown(f"""<div style="background:#F0FDF4; border: 2px solid #22C55E; border-radius:10px; padding:10px; text-align:center;">
    <div style="font-size:11.5px; color:#15803D; font-weight:800;">🌙 चन्द्र नक्षत्र व सब-लॉर्ड</div>
    <div style="font-size:18px; font-weight:900; color:#064E3B;">{moon_kp_obj['sub_lord']}</div>
    <div style="font-size:10.5px; color:#475569;">Star: {moon_kp_obj['star_lord']} ({moon_kp_obj['sign']})</div>
    </div>""", unsafe_allow_html=True)
    with c_k3:
        st.markdown(f"""<div style="background:#FEF3C7; border: 2px solid #F59E0B; border-radius:10px; padding:10px; text-align:center;">
    <div style="font-size:11.5px; color:#B45309; font-weight:800;">👑 वार स्वामी (Day Lord)</div>
    <div style="font-size:18px; font-weight:900; color:#78350F;">{rp_info['day_lord']['planet']}</div>
    <div style="font-size:10.5px; color:#475569;">{active_kp_chart.panchang.vara_name}</div>
    </div>""", unsafe_allow_html=True)
    with c_k4:
        st.markdown(f"""<div style="background:#FDF2F8; border: 2px solid #EC4899; border-radius:10px; padding:10px; text-align:center;">
    <div style="font-size:11.5px; color:#BE185D; font-weight:800;">🔢 होरारी / लग्न स्थिति</div>
    <div style="font-size:18px; font-weight:900; color:#831843;">{"होरारी #" + str(chosen_horary_num) if chosen_horary_num else "जन्म लग्न"}</div>
    <div style="font-size:10.5px; color:#475569;">{lagna_csl['sign']} ({lagna_csl['degree_formatted']})</div>
    </div>""", unsafe_allow_html=True)

    st.write("")

    # =========================================================================
    # 9 DEDICATED KP TABS
    # =========================================================================
    tab_kp1, tab_kp2, tab_kp3, tab_kp4, tab_kp5, tab_kp6, tab_kp7, tab_kp8, tab_kp9 = st.tabs(tabs)

    # -------------------------------------------------------------
    # TAB 1: KP FUTURE PREDICTION ENGINE
    # -------------------------------------------------------------
    with tab_kp1:
        st.markdown("#### 🔮 कृष्णमूर्ति पद्धति भविष्य फलित एवं कार्य सिद्धि विश्लेषक (KP Future Prediction Engine)")
        st.caption("के.पी. पद्धति के सार्वभौमिक स्वर्णिम नियमों (Golden Rules of KP) पर आधारित — मुख्य कस्पल सब-लॉर्ड, नक्षत्र स्वामी, ४-स्तरीय भाव कार्यकत्व एवं रूलिंग प्लैनेट्स के आधार पर अचूक भविष्यवाणी:")

        col_q1, col_q2 = st.columns([1.5, 2.5])
        with col_q1:
            q_cat_options = list(kp_mod.KP_QUERY_RULES.keys())
            selected_q_key = st.selectbox(
                "📋 प्रश्न / अभीष्ट कार्य क्षेत्र चुनें (Select Domain):",
                q_cat_options,
                format_func=lambda k: kp_mod.KP_QUERY_RULES[k]["name"],
                key="kp_query_domain_select_14tab"
            )
        with col_q2:
            user_q_text = st.text_input(
                "✍️ विशिष्ट प्रश्न लिखें (वैकल्पिक):",
                placeholder="उदा. क्या मुझे इस वर्ष पदोन्नति/नई नौकरी मिलेगी? क्या विवाह संपन्न होगा?",
                key="kp_user_q_text_14tab"
            )

        btn_pred = st.button("🔮 के.पी. शास्त्रीय फलित एवं कार्य सिद्धि निर्णय प्राप्त करें", type="primary", use_container_width=True)

        pred_res = k_engine.predict_kp_query(
            active_kp_chart,
            query_key=selected_q_key,
            horary_num=chosen_horary_num,
            query_text=user_q_text
        )

        st.markdown("---")
        c_theme = pred_res["color_theme"]
        score = pred_res["confidence_score"]

        st.markdown(f"""<div style="background: #FFFFFF; border: 2.5px solid {c_theme}; border-radius: 14px; padding: 18px 22px; box-shadow: 0 4px 14px rgba(0,0,0,0.06); margin-bottom: 16px;">
    <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; margin-bottom:10px;">
    <span style="font-size:20px; font-weight:900; color:{c_theme};">{pred_res['verdict_badge']}</span>
    <span style="font-size:16px; font-weight:800; background:{c_theme}15; color:{c_theme}; padding:4px 14px; border-radius:20px; border:1px solid {c_theme};">🎯 अनुकूलता स्कोर: {score}%</span>
    </div>
    <div style="font-size:14.5px; color:#1E293B; line-height:1.6; margin-bottom:10px;">
    {pred_res['verdict_desc']}
    </div>
    <div style="background:#F8FAFC; border-left:4px solid {c_theme}; padding:10px 14px; border-radius:6px; font-size:13px; color:#334155;">
    📖 <b>शास्त्रीय संदर्भ:</b> {pred_res['query_desc']}
    </div>
    </div>""", unsafe_allow_html=True)

        st.progress(score / 100.0)

        col_pa1, col_pa2, col_pa3 = st.columns(3)
        with col_pa1:
            csl = pred_res["primary_csl"]
            st.markdown(f"""<div style="background:#EEF2FF; border:1.5px solid #6366F1; border-radius:10px; padding:12px; height:100%;">
    <div style="font-weight:800; color:#4338CA; font-size:13px; margin-bottom:6px;">🎯 प्राथमिक कस्प एवं सब-लॉर्ड (CSL)</div>
    <div style="font-size:16px; font-weight:900; color:#1E1B4B;">भाव #{pred_res['primary_cusp']} कस्पल सब-लॉर्ड</div>
    <div style="font-size:13px; color:#312E81; margin-top:4px;">
    • <b>सब-लॉर्ड (CSL):</b> {csl['planet']}<br/>
    • <b>नक्षत्र स्वामी (Star Lord):</b> {csl['star_lord']}<br/>
    • <b>उप-उप स्वामी (SSL):</b> {csl['sub_sub_lord']}<br/>
    • <b>कस्प राशि व अंश:</b> {csl['sign']} ({csl['degree']})
    </div>
    </div>""", unsafe_allow_html=True)

        with col_pa2:
            fav_html = "".join([f"<span style='background:#DCFCE7; color:#15803D; font-weight:800; padding:2px 8px; border-radius:6px; border:1px solid #86EFAC; margin-right:4px;'>भाव {h}</span>" for h in pred_res['favorable_houses']])
            act_fav_html = "".join([f"<span style='background:#15803D; color:#FFFFFF; font-weight:900; padding:2px 8px; border-radius:6px; margin-right:4px;'>भाव {h} ✓</span>" for h in pred_res['signified_favorable']]) or "<span style='color:#94A3B8;'>कोई प्रत्यक्ष भाव नहीं</span>"
            st.markdown(f"""<div style="background:#F0FDF4; border:1.5px solid #22C55E; border-radius:10px; padding:12px; height:100%;">
    <div style="font-weight:800; color:#15803D; font-size:13px; margin-bottom:6px;">📈 अभीष्ट कार्य के अनुकूल भाव</div>
    <div style="font-size:12px; color:#166534; margin-bottom:6px;"><b>आवश्यक अनुकूल भाव:</b><br/>{fav_html}</div>
    <div style="font-size:12.5px; color:#14532D; margin-top:6px;">
    <b>CSL द्वारा सक्रिय अनुकूल भाव:</b><br/>{act_fav_html}
    </div>
    </div>""", unsafe_allow_html=True)

        with col_pa3:
            unfav_html = "".join([f"<span style='background:#FEE2E2; color:#B91C1C; font-weight:800; padding:2px 8px; border-radius:6px; border:1px solid #FCA5A5; margin-right:4px;'>भाव {h}</span>" for h in pred_res['unfavorable_houses']])
            act_unfav_html = "".join([f"<span style='background:#B91C1C; color:#FFFFFF; font-weight:900; padding:2px 8px; border-radius:6px; margin-right:4px;'>भाव {h} ✗</span>" for h in pred_res['signified_unfavorable']]) or "<span style='color:#15803D; font-weight:700;'>🛡️ कोई बाधक भाव सक्रिय नहीं</span>"
            st.markdown(f"""<div style="background:#FEF2F2; border:1.5px solid #EF4444; border-radius:10px; padding:12px; height:100%;">
    <div style="font-weight:800; color:#B91C1C; font-size:13px; margin-bottom:6px;">📉 बाधक एवं नकारात्मक भाव</div>
    <div style="font-size:12px; color:#991B1B; margin-bottom:6px;"><b>कार्य-विरोधी भाव:</b><br/>{unfav_html}</div>
    <div style="font-size:12.5px; color:#7F1D1D; margin-top:6px;">
    <b>CSL द्वारा सक्रिय बाधक भाव:</b><br/>{act_unfav_html}
    </div>
    </div>""", unsafe_allow_html=True)

        st.write("")
        col_rp_chk, col_timing = st.columns(2)
        with col_rp_chk:
            rp_status = "✅ पूर्ण समर्थन (Verified by RP)" if pred_res["rp_agreement"] else "⚠️ मध्यम संगति (Moderate RP Connection)"
            st.markdown(f"""<div style="background:#FFFBEB; border:1.5px solid #F59E0B; border-radius:10px; padding:14px;">
    <b style="color:#92400E; font-size:14px;">👑 रूलिंग प्लैनेट्स (RP) समर्थन:</b> &nbsp; <span style="color:#B45309; font-weight:800;">{rp_status}</span><br/>
    <div style="font-size:13px; color:#451A03; margin-top:6px;">
    • <b>सक्रिय रूलिंग प्लैनेट्स:</b> {', '.join(pred_res['ruling_planets_active'])}<br/>
    • <b>के.पी. सिद्धांत:</b> यदि मुख्य कस्पल सब-लॉर्ड अथवा उसका नक्षत्र स्वामी रूलिंग प्लैनेट्स का सदस्य हो, तो कार्य समय पर फलित होता है।
    </div>
    </div>""", unsafe_allow_html=True)

        with col_timing:
            st.markdown(f"""<div style="background:#F8FAFC; border:1.5px solid #64748B; border-radius:10px; padding:14px;">
    <b style="color:#1E293B; font-size:14px;">⏳ फलित काल एवं सटीक समय निर्धारण (Timing of Event):</b><br/>
    <div style="font-size:13px; color:#334155; margin-top:6px;">
    {pred_res['timing_estimate']}
    </div>
    </div>""", unsafe_allow_html=True)

    # -------------------------------------------------------------
    # TAB 2: PLANETARY SUB-LORDS & 4-FOLD SIGNIFICATORS
    # -------------------------------------------------------------
    with tab_kp2:
        st.markdown("#### 🪐 नवग्रह के.पी. स्थिति, उप-स्वामी एवं ४-स्तरीय कार्यकत्व (4-Fold Significators)")
        st.caption("के.पी. प्रणाली के अनुसार प्रत्येक ग्रह अपने **नक्षत्र स्वामी (Star Lord)** के भावों का फल देता है तथा **सब-लॉर्ड (Sub Lord)** फल की प्रकृति व कार्य सिद्धि (YES/NO) निर्धारित करता है:")

        p_rows = []
        for p in planets_kp_data:
            p_name = p["planet"]
            p_sig = p_sigs.get(p_name, {})
            p_rows.append({
                "ग्रह (Planet)": p_name,
                "राशि (Sign)": p["sign"],
                "सटीक अंश (Degree)": p["degree_formatted"],
                "राशि स्वामी (Sign Lord)": p["sign_lord"],
                "नक्षत्र स्वामी (Star Lord)": p["star_lord"],
                "उप-स्वामी (Sub Lord)": p["sub_lord"],
                "उप-उप स्वामी (SSL)": p["sub_sub_lord"],
                "गति": p["motion"],
                "कार्यकत्व भाव (Signified Houses)": ", ".join([f"#{h}" for h in p_sig.get("combined_houses", [])])
            })
        st.dataframe(pd.DataFrame(p_rows), use_container_width=True, hide_index=True)

        st.markdown("##### 📜 ४-स्तरीय ग्रह कार्यकत्व विवरण (Levels A, B, C, D Breakdown)")
        st.caption("Level A: नक्षत्र में स्थित ग्रह के भाव (अति प्रबल) | Level B: स्वयं स्थित भाव | Level C: नक्षत्र स्वामी के स्वामित्व वाले भाव | Level D: स्वयं के स्वामित्व वाले भाव:")
        sig_rows = []
        for p_name, s in p_sigs.items():
            sig_rows.append({
                "ग्रह": p_name,
                "Level A (अति प्रबल)": ", ".join([f"भाव {h}" for h in s["level_a_houses"]]) or "—",
                "Level B (प्रबल)": ", ".join([f"भाव {h}" for h in s["level_b_houses"]]) or "—",
                "Level C (मध्यम)": ", ".join([f"भाव {h}" for h in s["level_c_houses"]]) or "—",
                "Level D (सामान्य)": ", ".join([f"भाव {h}" for h in s["level_d_houses"]]) or "—",
                "कुल कार्यकत्व (Total Signified)": ", ".join([f"#{h}" for h in s["combined_houses"]])
            })
        st.dataframe(pd.DataFrame(sig_rows), use_container_width=True, hide_index=True)

    # -------------------------------------------------------------
    # TAB 3: 12 CUSPAL SUB-LORDS & HOUSE SIGNIFICATORS
    # -------------------------------------------------------------
    with tab_kp3:
        st.markdown("#### 🏰 द्वादश भाव संधि, कस्पल उप-स्वामी (Cuspal Sub-Lords) व भाव कार्यक")
        st.caption("के.पी. पद्धति में किसी भी भाव का फलित निर्णय उस भाव के **कस्पल सब-लॉर्ड (Cuspal Sub-Lord - CSL)** के नक्षत्र स्वामी द्वारा ही निर्धारित होता है:")

        c_rows = []
        for c in cusps_data:
            h_num = c["cusp_num"]
            h_sig = h_sigs.get(h_num, {})
            c_rows.append({
                "भाव (Cusp)": c["cusp"],
                "राशि (Sign)": c["sign"],
                "कस्प अंश (Degree)": c["degree_formatted"],
                "राशि स्वामी (Sign Lord)": c["sign_lord"],
                "नक्षत्र स्वामी (Star Lord)": c["star_lord"],
                "कस्पल सब-लॉर्ड (CSL)": c["sub_lord"],
                "उप-उप स्वामी (SSL)": c["sub_sub_lord"],
                "भाव के कार्यक ग्रह (Significators)": ", ".join(h_sig.get("all_significators", []))
            })
        st.dataframe(pd.DataFrame(c_rows), use_container_width=True, hide_index=True)

        st.markdown("##### 🏛️ द्वादश भावों के ४-स्तरीय नियंत्रक ग्रह (House Level A-D Significators)")
        h_table_rows = []
        for h_num, h_info in h_sigs.items():
            h_table_rows.append({
                "भाव": f"भाव #{h_num}",
                "भाव स्वामी (Lord)": h_info["lord"],
                "Level A (भाव में स्थित ग्रह के नक्षत्र में ग्रह)": ", ".join(h_info["level_a"]) or "—",
                "Level B (भाव में स्थित ग्रह)": ", ".join(h_info["level_b"]) or "—",
                "Level C (भाव स्वामी के नक्षत्र में ग्रह)": ", ".join(h_info["level_c"]) or "—",
                "Level D (भाव स्वामी स्वयं)": ", ".join(h_info["level_d"]) or "—",
                "समस्त कार्यक ग्रह": ", ".join(h_info["all_significators"])
            })
        st.dataframe(pd.DataFrame(h_table_rows), use_container_width=True, hide_index=True)

        st.markdown("##### 🎯 द्वादश भाव कस्पल सब-लॉर्ड (CSL 1-12) एवं शास्त्रीय कार्य सिद्धि मैट्रिक्स (KP Readers I-VI)")
        st.caption("प्रो. के.एस. कृष्णमूर्ति के अनुसार प्रत्येक भाव का अभीष्ट फल उस भाव के कस्पल सब-लॉर्ड (CSL) एवं उसके नक्षत्र स्वामी के कार्यकत्वों द्वारा निर्धारित होता है:")
        csl_matrix_data = kp_chart_data.get("csl_matrix", [])
        if csl_matrix_data:
            csl_display_rows = []
            for item in csl_matrix_data:
                csl_display_rows.append({
                    "भाव (Cusp)": f"#{item['cusp_num']} {item['sign']} ({item['cusp_degree']})",
                    "जीवन आयाम (Domain)": item["bhava_name"],
                    "CSL (उप-स्वामी)": item["csl"],
                    "नक्षत्र स्वामी": item["star_lord"],
                    "कार्यक भाव": ", ".join([f"#{h}" for h in item["signified_houses"]]),
                    "अनुकूल भाव": ", ".join([f"#{h}" for h in item["fav_hits"]]) or "—",
                    "बाधक भाव": ", ".join([f"#{h}" for h in item["unfav_hits"]]) or "—",
                    "कार्य सिद्धि निर्णय": item["promise_badge"],
                    "सहमति": f"{item['score']}%"
                })
            st.dataframe(pd.DataFrame(csl_display_rows), use_container_width=True, hide_index=True)

    # -------------------------------------------------------------
    # TAB 4: RULING PLANETS (RP)
    # -------------------------------------------------------------
    with tab_kp4:
        st.markdown("#### 👑 तात्कालिक रूलिंग प्लैनेट्स (Ruling Planets - RP Analysis)")
        st.caption("जन्म/प्रश्न क्षण के समय ब्रह्मांड के नियंत्रक ग्रह (वार स्वामी, चन्द्र राशि/नक्षत्र स्वामी, लग्न राशि/नक्षत्र स्वामी):")

        c_rp1, c_rp2, c_rp3 = st.columns(3)
        c_rp1.metric(rp_info["day_lord"]["title"], rp_info["day_lord"]["planet"])
        c_rp2.metric(rp_info["moon_sign_lord"]["title"], rp_info["moon_sign_lord"]["planet"])
        c_rp3.metric(rp_info["moon_star_lord"]["title"], rp_info["moon_star_lord"]["planet"])

        c_rp4, c_rp5, c_rp6 = st.columns(3)
        c_rp4.metric(rp_info["lagna_sign_lord"]["title"], rp_info["lagna_sign_lord"]["planet"])
        c_rp5.metric(rp_info["lagna_star_lord"]["title"], rp_info["lagna_star_lord"]["planet"])
        c_rp6.metric("लग्न उप-स्वामी (Lagna Sub Lord)", rp_info["lagna_sub_lord"]["planet"])

        if rp_info.get("node_agents"):
            st.markdown(f"""<div style="background:#F1F5F9; border:1.5px solid #64748B; border-radius:10px; padding:12px; margin-top:12px;">
    <b style="color:#0F172A; font-size:13.5px;">🐉 राहु / केतु नोड प्रतिनिधित्व (Node Agents of RPs):</b><br/>
    <span style="font-size:13px; color:#334155;">{', '.join(rp_info['node_agents'])} — के.पी. नियमानुसार यदि राहु/केतु किसी RP की राशि/नक्षत्र में हों तो वे उस RP से भी अधिक शक्तिशाली फल देते हैं।</span>
    </div>""", unsafe_allow_html=True)

        st.info("💡 **रूलिंग प्लैनेट्स का उपयोग:** जन्म समय शोधन (BTR), प्रश्न फलित निर्णय एवं कार्य सिद्धि के सटीक समय निर्धारण (Timing of Events) में रूलिंग प्लैनेट्स सर्वोच्च मार्गदर्शक होते हैं।")

    # -------------------------------------------------------------
    # TAB 5: 1-249 KP HORARY MASTER TABLE
    # -------------------------------------------------------------
    with tab_kp5:
        st.markdown("#### 🔢 1-249 कृष्णमूर्ति होरारी तालिका (KP Horary Master Table)")
        st.caption("१ से २४९ तक किसी भी होरारी संख्या का चयन करें अथवा सम्पूर्ण २४९ उप-विभाजनों की सूची देखें:")

        all_249 = k_engine.get_all_249_table()
        col_h_s1, col_h_s2 = st.columns([1.5, 2.5])
        with col_h_s1:
            inspect_h_num = st.number_input("होरारी संख्या चुनें (1 - 249)", min_value=1, max_value=249, value=int(chosen_horary_num) if chosen_horary_num else 108, step=1, key="inspect_h_num_single_14tab")

        h_detail = k_engine.get_horary_number_detail(int(inspect_h_num))
        with col_h_s2:
            st.markdown(f"""<div style="background:#FFFBEB; border:1.5px solid #F59E0B; border-radius:10px; padding:12px;">
    <b style="color:#92400E; font-size:14px;">🎯 होरारी संख्या #{inspect_h_num} का विवरण:</b><br/>
    • <b>राशि:</b> {h_detail['sign_name']} (स्वामी: <b>{h_detail['sign_lord']}</b>) &nbsp;|&nbsp; <b>नक्षत्र:</b> {h_detail['nakshatra']} (स्वामी: <b>{h_detail['star_lord']}</b>)<br/>
    • <b>उप-स्वामी (Sub Lord):</b> <span style="background:#EEF2FF; color:#312E81; padding:2px 8px; border-radius:4px; font-weight:800;">{h_detail['sub_lord']}</span><br/>
    • <b>राशि अंश विस्तार:</b> {h_detail['start_deg']:.2f}° से {h_detail['end_deg']:.2f}° (पूर्ण देशांतर: {h_detail['start_lon']:.2f}° ~ {h_detail['end_lon']:.2f}°)
    </div>""", unsafe_allow_html=True)

        st.write("")
        st.markdown("##### 📋 संपूर्ण 1-249 कृष्णमूर्ति उप-विभाजन तालिका")
        df_249 = pd.DataFrame([{
            "होरारी #": row["number"],
            "राशि (Sign)": row["sign_name"],
            "राशि स्वामी": row["sign_lord"],
            "नक्षत्र": row["nakshatra"],
            "नक्षत्र स्वामी": row["star_lord"],
            "उप-स्वामी (Sub Lord)": row["sub_lord"],
            "प्रारंभिक अंश": f"{row['start_deg']:.2f}°",
            "समाप्ति अंश": f"{row['end_deg']:.2f}°",
            "पूर्ण देशांतर": f"{row['start_lon']:.2f}° ~ {row['end_lon']:.2f}°"
        } for row in all_249])
        st.dataframe(df_249, use_container_width=True, hide_index=True)

    # -------------------------------------------------------------
    # TAB 6: KP WESTERN ASPECTS & CUSPAL DRISHTI
    # -------------------------------------------------------------
    with tab_kp6:
        st.markdown("#### 📐 के.पी. पाश्चात्य दृष्टि एवं भाव वेध (KP Planetary & Cuspal Aspects)")
        st.caption("कृष्णमूर्ति पद्धति में प्रयुक्त पाश्चात्य कोणीय दृष्टियां — ०° युति, ६०° लाभ, ९०° बाधा, १२०° त्रिकोण, १५०° षडष्टक एवं १८०° सम्मुख दृष्टि:")

        aspect_defs = [
            (0, "युति (Conjunction)", 8.0, "तटस्थ/तीव्र", "#3B82F6"),
            (60, "लाभ दृष्टि (Sextile)", 6.0, "अति शुभ", "#10B981"),
            (90, "केन्द्र बाधा दृष्टि (Square)", 8.0, "प्रतिकूल/संघर्ष", "#EF4444"),
            (120, "त्रिकोण दृष्टि (Trine)", 8.0, "परम शुभ/सौहार्द", "#059669"),
            (150, "षडष्टक दृष्टि (Quincunx)", 4.0, "असामंजस्य/स्वास्थ्य", "#F59E0B"),
            (180, "सम्मुख दृष्टि (Opposition)", 8.0, "विरोधी/अलगाव", "#DC2626")
        ]

        planet_names_list = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]
        aspect_rows = []

        for i, p1 in enumerate(planet_names_list):
            if p1 not in active_kp_chart.planets:
                continue
            lon1 = active_kp_chart.planets[p1].longitude
            for p2 in planet_names_list[i+1:]:
                if p2 not in active_kp_chart.planets:
                    continue
                lon2 = active_kp_chart.planets[p2].longitude
                diff = abs(lon1 - lon2) % 360.0
                if diff > 180.0:
                    diff = 360.0 - diff

                for asp_deg, asp_name, orb_limit, nature, col in aspect_defs:
                    orb = abs(diff - asp_deg)
                    if orb <= orb_limit:
                        aspect_rows.append({
                            "ग्रह १": p1,
                            "ग्रह २": p2,
                            "दृष्टि प्रकार (Aspect)": asp_name,
                            "सटीक कोण": f"{diff:.2f}°",
                            "ऑर्ब (Orb)": f"{orb:.2f}°",
                            "प्रभाव / प्रकृति": nature
                        })

        if aspect_rows:
            st.dataframe(pd.DataFrame(aspect_rows), use_container_width=True, hide_index=True)
        else:
            st.info("वर्तमान में कोई प्रमुख पाश्चात्य दृष्टि ऑर्ब सीमा के भीतर नहीं है।")

        st.markdown("##### 🏛️ ग्रहों की भाव कस्पों (House Cusps) पर प्रमुख दृष्टियां")
        cusp_aspect_rows = []
        for p in planet_names_list:
            if p not in active_kp_chart.planets:
                continue
            p_lon = active_kp_chart.planets[p].longitude
            for c_obj in cusps_data:
                c_lon = c_obj["longitude"]
                diff = abs(p_lon - c_lon) % 360.0
                if diff > 180.0:
                    diff = 360.0 - diff

                for asp_deg, asp_name, orb_limit, nature, col in aspect_defs:
                    orb = abs(diff - asp_deg)
                    if orb <= orb_limit:
                        cusp_aspect_rows.append({
                            "ग्रह": p,
                            "भाव कस्प": c_obj["cusp"],
                            "दृष्टि प्रकार": asp_name,
                            "कोण": f"{diff:.2f}°",
                            "ऑर्ब": f"{orb:.2f}°",
                            "प्रभाव": nature
                        })
        if cusp_aspect_rows:
            st.dataframe(pd.DataFrame(cusp_aspect_rows[:15]), use_container_width=True, hide_index=True)
        else:
            st.info("भाव कस्पों पर कोई प्रमुख दृष्टि सक्रिय नहीं है।")

    # -------------------------------------------------------------
    # TAB 7: KP VIMSHOTTARI DBA TIMING
    # -------------------------------------------------------------
    with tab_kp7:
        st.markdown("#### ⏱️ के.पी. विंशोत्तरी दशा-भुक्ति-अन्तर कालक्रम (KP DBA Event Timing)")
        st.caption("कृष्णमूर्ति पद्धति का स्वर्णिम सूत्र: 'दशा स्वामी अवसर प्रदान करता है, भुक्ति स्वामी फल का स्वरूप बनाता है, और अन्तर स्वामी घटना घटित कराता है':")

        b_dt = datetime.combine(active_kp_chart.birth_data.birth_date, active_kp_chart.birth_data.birth_time)
        m_lon = active_kp_chart.planets["Moon"].longitude
        h5_kp = d_engine.get_5level_hierarchy(b_dt, m_lon, target_query_dt)

        act_m = h5_kp["mahadasha"]
        act_a = h5_kp["antardasha"]
        act_pr = h5_kp["pratyantardasha"]

        cdb1, cdb2, cdb3 = st.columns(3)
        with cdb1:
            st.markdown(f"""<div style="background:#EEF2FF; border: 2px solid #6366F1; border-radius:10px; padding:12px; text-align:center;">
    <div style="font-size:12px; color:#4338CA; font-weight:800;">👑 महादशा स्वामी (MD)</div>
    <div style="font-size:20px; font-weight:900; color:#1E1B4B;">{act_m['lord']}</div>
    <div style="font-size:11px; color:#475569;">कार्यक भाव: {", ".join([f"#{h}" for h in p_sigs.get(act_m['lord'], {}).get('combined_houses', [])])}</div>
    </div>""", unsafe_allow_html=True)
        with cdb2:
            st.markdown(f"""<div style="background:#F0FDF4; border: 2px solid #22C55E; border-radius:10px; padding:12px; text-align:center;">
    <div style="font-size:12px; color:#15803D; font-weight:800;">🪐 भुक्ति स्वामी (Bhukti - AD)</div>
    <div style="font-size:20px; font-weight:900; color:#064E3B;">{act_a['lord']}</div>
    <div style="font-size:11px; color:#475569;">कार्यक भाव: {", ".join([f"#{h}" for h in p_sigs.get(act_a['lord'], {}).get('combined_houses', [])])}</div>
    </div>""", unsafe_allow_html=True)
        with cdb3:
            st.markdown(f"""<div style="background:#FEF3C7; border: 2px solid #F59E0B; border-radius:10px; padding:12px; text-align:center;">
    <div style="font-size:12px; color:#B45309; font-weight:800;">⚡ अन्तर स्वामी (Antara - PD)</div>
    <div style="font-size:20px; font-weight:900; color:#78350F;">{act_pr['lord']}</div>
    <div style="font-size:11px; color:#475569;">कार्यक भाव: {", ".join([f"#{h}" for h in p_sigs.get(act_pr['lord'], {}).get('combined_houses', [])])}</div>
    </div>""", unsafe_allow_html=True)

        st.write("")
        st.markdown("##### 🎯 वर्तमान सक्रिय D-B-A स्वामियों का संयुक्त कार्यकत्व समन्वय:")
        md_houses = set(p_sigs.get(act_m['lord'], {}).get('combined_houses', []))
        ad_houses = set(p_sigs.get(act_a['lord'], {}).get('combined_houses', []))
        pd_houses = set(p_sigs.get(act_pr['lord'], {}).get('combined_houses', []))
        common_all = sorted(list(md_houses.intersection(ad_houses).intersection(pd_houses)))
        common_two = sorted(list((md_houses.intersection(ad_houses)).union(ad_houses.intersection(pd_houses))))

        st.success(f"🌟 **त्रि-स्तरीय संयुक्त सक्रिय भाव (MD ∩ AD ∩ PD):** {', '.join([f'भाव #{h}' for h in common_all]) if common_all else 'विविध भाव सक्रिय'}")
        st.info(f"⚡ **द्वि-स्तरीय सक्रिय भाव (MD/AD/PD):** {', '.join([f'भाव #{h}' for h in common_two]) if common_two else 'सामान्य'}")

    # -------------------------------------------------------------
    # TAB 8: 22 LIFE EVENTS CSL FORMULA MATRIX
    # -------------------------------------------------------------
    with tab_kp8:
        st.markdown("#### 📊 २२ जीवन घटना सूत्र व कस्पल सब-लॉर्ड मैट्रिक्स (22 Life Events CSL Matrix)")
        st.caption("कृष्णमूर्ति रीडर्स के अनुसार मानव जीवन के २२ प्रमुख प्रसंगों के अनिवार्य भाव सूत्र एवं सक्रिय कुण्डली में उनकी फलित संभावना:")

        life_events_catalog = [
            ("१. विवाह (Marriage)", 7, [2, 7, 11], [1, 6, 10], "७वें कस्प का सब-लॉर्ड २, ७, ११ भावों का कार्यक हो।"),
            ("२. वैवाहिक विच्छेद / तलाक (Divorce)", 7, [1, 6, 10], [2, 7, 11], "७वें कस्प का सब-लॉर्ड १, ६, १० (अलगाव भाव) से संबंधित हो।"),
            ("३. संतान प्राप्ति (Childbirth)", 5, [2, 5, 11], [1, 4, 10], "५वें कस्प का सब-लॉर्ड २, ५, ११ भावों का कार्यक हो।"),
            ("४. नई नौकरी प्राप्ति (New Job)", 6, [2, 6, 10, 11], [5, 12], "६ठे कस्प का सब-लॉर्ड २, ६, १०, ११ भावों को सूचित करे।"),
            ("५. पदोन्नति / इन्क्रीमेंट (Promotion)", 10, [2, 6, 10, 11], [5, 8], "१०वें कस्प का सब-लॉर्ड ६, १०, ११ भावों से जुड़ा हो।"),
            ("६. नौकरी छूटना / निलंबन (Job Loss)", 10, [5, 8, 12], [2, 6, 10, 11], "१०वें कस्प का सब-लॉर्ड ५, ८, १२ भावों का कार्यक हो।"),
            ("७. नया व्यापार / साझेदारी (New Business)", 7, [2, 7, 10, 11], [5, 8], "७वें व १०वें कस्प का सब-लॉर्ड २, ७, १०, ११ को दर्शाए।"),
            ("८. विदेश यात्रा (Foreign Travel)", 9, [3, 9, 12], [2, 4, 11], "९वें कस्प का सब-लॉर्ड ३, ९, १२ भावों का कार्यक हो।"),
            ("९. स्थायी विदेश वास (Foreign Settlement)", 12, [3, 9, 12], [4], "१२वें कस्प का सब-लॉर्ड ४थे भाव (स्वदेश) को नकारकर ९, १२ से जुड़े।"),
            ("१०. भूमि / मकान क्रय (Buy House/Land)", 4, [4, 11, 12], [3, 6, 8], "४थे कस्प का सब-लॉर्ड ४, ११, १२ भावों को दर्शाए।"),
            ("११. संपत्ति विक्रय (Sell Property)", 10, [3, 5, 10], [4, 11], "१०वें कस्प का सब-लॉर्ड ३, ५, १० भावों का कार्यक हो।"),
            ("१२. वाहन क्रय (Buy Vehicle)", 4, [4, 11], [3, 8], "४थे कस्प का सब-लॉर्ड ४, ११ भावों को सूचित करे।"),
            ("१३. आकस्मिक धन लाभ / लॉटरी (Sudden Wealth)", 8, [2, 6, 8, 11], [5, 12], "८वें कस्प का सब-लॉर्ड २, ६, ८, ११ भावों से संबंधित हो।"),
            ("१४. भारी वित्तीय हानि / दिवालियापन (Financial Loss)", 12, [5, 8, 12], [2, 6, 11], "२रे व १२वें कस्प का सब-लॉर्ड ५, ८, १२ भावों को दर्शाए।"),
            ("१५. कोर्ट केस में विजय (Victory in Court)", 6, [6, 11], [12, 5], "६ठे कस्प का सब-लॉर्ड ६, ११ भावों का कार्यक हो।"),
            ("१६. रोगमुक्ति व स्वास्थ्य लाभ (Health Recovery)", 1, [1, 5, 11], [6, 8, 12], "१ले व ६ठे कस्प का सब-लॉर्ड ५, ११ भावों को दर्शाए।"),
            ("१७. उच्च शिक्षा में सफलता (Higher Studies)", 9, [4, 9, 11], [3, 8], "९वें कस्प का सब-लॉर्ड ४, ९, ११ भावों को सूचित करे।"),
            ("१८. प्रतियोगी परीक्षा में चयन (Competitive Exam)", 6, [6, 11], [5, 8, 12], "६ठे कस्प का सब-लॉर्ड ६, ११ भावों का कार्यक हो।"),
            ("१९. खोई वस्तु की पुनः प्राप्ति (Recovery of Lost Item)", 2, [2, 6, 11], [8, 12], "२रे कस्प का सब-लॉर्ड २, ६, ११ भावों से संबंधित हो।"),
            ("२०. राजनीति / चुनाव में विजय (Electoral Victory)", 10, [6, 10, 11], [12, 5], "१०वें कस्प का सब-लॉर्ड ६, १०, ११ भावों को सूचित करे।"),
            ("२१. आध्यात्मिक दीक्षा व संन्यास (Spiritual Initiation)", 9, [9, 11, 12], [2, 7], "९वें कस्प का सब-लॉर्ड ९, १२ भावों से संबंधित हो।"),
            ("२२. सामान्य कार्य सिद्धि (General Wish Fulfillment)", 11, [2, 11], [12], "११वें कस्प का सब-लॉर्ड २, ११ भावों का कार्यक हो।")
        ]

        matrix_rows = []
        for ev_title, cusp_idx, fav_h, unfav_h, shastra_rule in life_events_catalog:
            csl_item = cusps_data[cusp_idx - 1]
            csl_planet = csl_item["sub_lord"]
            csl_houses = p_sigs.get(csl_planet, {}).get("combined_houses", [])

            fav_matches = [h for h in csl_houses if h in fav_h]
            unfav_matches = [h for h in csl_houses if h in unfav_h]

            if len(fav_matches) >= 2 and len(unfav_matches) == 0:
                verdict = "🟢 पूर्ण अनुकूल (Promised)"
            elif len(fav_matches) > 0 and len(fav_matches) > len(unfav_matches):
                verdict = "🟡 मध्यम अनुकूल (Moderate)"
            elif len(unfav_matches) > 0:
                verdict = "🔴 बाधा / विलंब (Obstructed)"
            else:
                verdict = "⚪ सामान्य / तटस्थ (Neutral)"

            matrix_rows.append({
                "जीवन घटना प्रसंग": ev_title,
                "मुख्य CSL भाव": f"कस्प #{cusp_idx} ({csl_planet})",
                "अनिवार्य भाव": ", ".join([str(h) for h in fav_h]),
                "सक्रिय भाव (CSL)": ", ".join([str(h) for h in csl_houses]) or "—",
                "के.पी. फलित निर्णय": verdict,
                "शास्त्रीय सूत्र": shastra_rule
            })

        st.dataframe(pd.DataFrame(matrix_rows), use_container_width=True, hide_index=True)

    # -------------------------------------------------------------
    # TAB 9: KP GOLDEN RULES & REMEDIES
    # -------------------------------------------------------------
    with tab_kp9:
        st.markdown("#### 📜 के.पी. स्वर्णिम नियम, रीडर १-६ प्रमाण एवं वैदिक उपाय (KP Golden Rules & Remedies)")
        st.caption("प्रोफेसर के.एस. कृष्णमूर्ति (KP Readers I to VI) के मूल सिद्धांत एवं उप-स्वामी आधारित वैज्ञानिक उपाय:")

        kp_shl = SHASTRIYA_SHLOKAS.get("kp_sublord_system", {})
        if kp_shl:
            kp_lines = "<br/>".join(kp_shl['shloka'].splitlines())
            st.markdown(f"""
    <div style="background: rgba(16, 185, 129, 0.08); border-left: 4px solid #10B981; padding: 14px 18px; border-radius: 8px; margin: 10px 0 16px 0;">
    <div style="font-weight: 700; color: #047857; font-size: 13.5px; margin-bottom: 4px;">📖 {kp_shl['grantha']}</div>
    <div style="font-family: 'Devanagari Sangam MN', serif; font-size: 14px; font-weight: 600; line-height: 1.6; color: #0F172A;">
        {kp_lines}
    </div>
    <div style="margin-top: 6px; font-size: 12.5px; color: #334155; line-height: 1.5;">
        <b>हिंदी भावार्थ:</b> {kp_shl['anuvad_hi']}
    </div>
    <div style="margin-top: 4px; font-size: 11.5px; color: #64748B;">
        <b>शास्त्रीय नियम:</b> {kp_shl['rule']}
    </div>
    </div>
    """, unsafe_allow_html=True)

        with st.expander("📖 प्रोफेसर कृष्णमूर्ति के १० स्वर्णिम नियम (10 Golden Rules of KP)", expanded=True):
            st.markdown("""**१. नक्षत्र स्वामी का फल (Star Lord Rule):**
    > *'A planet offers the results of the house occupied and owned by its Star Lord.'*
    > ग्रह स्वयं जिस भाव में बैठा है या जिसका स्वामी है, उससे कहीं अधिक शक्तिशाली फल वह अपने नक्षत्र स्वामी के भावों का देता है।

    **२. सब-लॉर्ड का अंतिम निर्णय (Sub Lord Disposes):**
    > *'Star Lord proposes, but the Sub Lord disposes.'*
    > नक्षत्र स्वामी घटना की पृष्ठभूमि तैयार करता है, परंतु घटना फलित होगी (YES) अथवा निष्फल (NO) होगी — इसका निर्णय केवल कस्पल सब-लॉर्ड ही करता है।

    **३. कस्पल सब-लॉर्ड का वचन (Cuspal Promise):**
    > यदि किसी भाव के कस्पल सब-लॉर्ड (CSL) का नक्षत्र स्वामी उस भाव के सहायक भावों को सूचित करे, तो वह घटना जीवन में अवश्य घटित होती है।

    **४. वक्री ग्रह नियम (Retrograde Planet Rule):**
    > यदि कोई ग्रह किसी वक्री ग्रह के नक्षत्र में स्थित हो, तो वह अपने फल तब तक नहीं दे पाता जब तक वह नक्षत्र स्वामी मार्गी न हो जाए।

    **५. राहु व केतु का महा-कार्यकत्व (Nodes as Super-Significators):**
    > राहु और केतु जिस राशि में बैठते हैं, जिस ग्रह के नक्षत्र में होते हैं, तथा जिनसे युति या दृष्टि संबंध बनाते हैं — उनके संयुक्त कार्यकत्व को कई गुना बढ़ाकर फलित करते हैं।

    **६. बाधक एवं मारक भाव (Negating Houses):**
    > प्रत्येक भाव का १२वां भाव उस भाव के फल को समाप्त करता है। विवाह (७) के लिए ६ठा, नौकरी (६) के लिए ५वां, और लाभ (११) के लिए १०वां भाव नकारात्मक होता है।""")

        with st.expander("🪔 के.पी. उप-स्वामी आधारित वैज्ञानिक वैदिक उपाय (KP Remedial Suite)", expanded=True):
            st.markdown(f"""##### 👑 सक्रिय लग्न कस्पल सब-लॉर्ड ({lagna_csl['sub_lord']}) के उपाय:
    के.पी. पद्धति के अनुसार कभी भी उन ग्रहों का रत्न धारण नहीं करना चाहिए जो ६, ८, १२ भावों के कार्यक हों।
    - 💎 **रत्न धारण नियम:** केवल उन्हीं ग्रहों का रत्न धारण करें जो कुण्डली में २, १०, ११ भावों के बली कार्यक हों और बाधक भावों से मुक्त हों।
    - 📿 **मंत्र अनुष्ठान:** `{lagna_csl['sub_lord']}` के वैदिक बीज मंत्र का नित्य १०८ जप जातक के व्यक्तित्व एवं स्वास्थ्य को सुदृढ़ करता है।
    - 🎁 **दान नियम:** जो ग्रह अनिष्टकारी भावों (६, ८, १२) का कार्यक हो, उसकी दान सामग्री का त्याग करने से उन भावों की नकारात्मक ऊर्जा का शमन होता है।""")



