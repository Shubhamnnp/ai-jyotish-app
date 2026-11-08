import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, date
from src.jyotish.core.models import BirthData
from src.jyotish.core.varga import VargaCalculator
from src.jyotish.core.calculator import default_chart_calculator
from src.jyotish.services.btr import default_btr_service, LifeEvent, BTRCandidate

def render_btr_view(chart, birth_profile, tabs=None):
    if tabs is None or len(tabs) < 8:
        tabs = [
            "🏆 घटना मिलान शोधन",
            "🌿 तत्व व लिंग शोधन",
            "☸️ कुण्ड व प्राणपद लग्न",
            "📐 D9 व D60 सीमा",
            "👑 के.पी. रूलिंग प्लैनेट्स",
            "⚖️ पूर्व व शोधित तुलना",
            "🎯 सेकंड्स सूक्ष्म स्लाइडर",
            "📜 शास्त्रीय सूत्र व प्रमाण"
        ]

    st.subheader("⏳ जन्म समय शोधन महा-प्रणाली (Vedic & KP Birth Time Rectification - BTR)")
    st.write(
        "महर्षि पराशर, उत्तरकालामृत, चन्द्रकला नाड़ी एवं के.पी. प्रणाली के अकाट्य शास्त्रीय सिद्धांतों पर आधारित ९९.९% प्रामाणिक जन्म समय परिशोधन। "
        "तत्व शोधन, कुण्ड शोधन, प्राणपद लग्न, षष्ट्यंश (D60) सीमा विश्लेषण एवं जीवन की ऐतिहासिक घटनाओं के समन्वय से सटीक इष्टकाल निर्धारण।"
    )

    # Native Profile Metrics
    calc_chart = chart if ('chart' in locals() and chart is not None) else default_chart_calculator.calculate_chart(birth_profile)
    if not hasattr(calc_chart, 'vargas') or not calc_chart.vargas:
        calc_chart.vargas = VargaCalculator.calculate_all_vargas(calc_chart)
    b_nat_d = birth_profile.birth_date
    b_nat_t = birth_profile.birth_time
    nat_dt = datetime.combine(b_nat_d, b_nat_t)

    col_mb1, col_mb2, col_mb3, col_mb4 = st.columns(4)
    col_mb1.metric("मूल जन्म समय", nat_dt.strftime("%I:%M:%S %p"), "पंजीकृत समय")
    col_mb2.metric("जन्म लग्न (D1)", f"{calc_chart.lagna_sign_name}", f"{round(calc_chart.lagna_degree, 2)}°")
    col_mb3.metric("चन्द्र नक्षत्र", f"{calc_chart.panchang.nakshatra_name}", f"पाद {calc_chart.planets['Moon'].nakshatra_pada}")
    col_mb4.metric("जन्म वार", f"{calc_chart.panchang.vara_name}", "वार स्वामी")

    # 8 Dedicated Tabs
    tab_btr1, tab_btr2, tab_btr3, tab_btr4, tab_btr5, tab_btr6, tab_btr7, tab_btr8 = st.tabs(tabs)

    # -------------------------------------------------------------------------
    # TAB 1: MULTI-EVENT SCANNER
    # -------------------------------------------------------------------------
    with tab_btr1:
        st.markdown("### 🏆 बहु-घटना आधारित काल शोधन एवं संभाव्यता स्कैनर")
        st.write("जातक के जीवन में घटित वास्तविक ऐतिहासिक घटनाओं की तिथियां दर्ज करें। विंशोत्तरी दशा, गोचर (गुरु-शनि दोहरा गोचर) एवं वर्ग कुण्डलियों (D9, D10, D7, D4) से गणितीय मिलान किया जाएगा:")

        if "btr_events_store" not in st.session_state:
            st.session_state["btr_events_store"] = [
                {"event_date": date(2015, 6, 15), "event_category": "career", "description": "प्रथम स्थायी नौकरी / पदोन्नति"},
                {"event_date": date(2018, 11, 24), "event_category": "marriage", "description": "विवाह संस्कार संपन्न"}
            ]

        with st.expander("➕ नई ऐतिहासिक जीवन घटना जोड़ें (Add Life Event)", expanded=False):
            c_ev1, c_ev2, c_ev3 = st.columns(3)
            with c_ev1:
                new_ev_date = st.date_input("घटना तिथि", value=date(2020, 1, 1), format="DD/MM/YYYY", key="btr_new_d")
            with c_ev2:
                new_ev_cat = st.selectbox(
                    "घटना श्रेणी",
                    options=[
                        ("career", "💼 नौकरी / करियर / पदोन्नति (Career)"),
                        ("marriage", "💍 विवाह / सगाई (Marriage)"),
                        ("child", "👶 प्रथम / द्वितीय संतान जन्म (Childbirth)"),
                        ("property", "🏠 भूमि / भवन / वाहन क्रय (Property)"),
                        ("travel", "✈️ विदेश गमन / दूरस्थ यात्रा (Foreign Travel)"),
                        ("health_accident", "🏥 रोग / दुर्घटना / शल्य चिकित्सा (Health)"),
                        ("education", "🎓 उच्च शिक्षा / उपाधि / परीक्षा (Education)")
                    ],
                    format_func=lambda x: x[1],
                    key="btr_new_c"
                )[0]
            with c_ev3:
                new_ev_desc = st.text_input("घटना विवरण", value="महत्वपूर्ण जीवन घटना", key="btr_new_desc")

            if st.button("➕ घटना सूची में सम्मिलित करें", key="btr_add_btn"):
                st.session_state["btr_events_store"].append({
                    "event_date": new_ev_date,
                    "event_category": new_ev_cat,
                    "description": new_ev_desc
                })
                st.success("✅ घटना सफलतापूर्वक जोड़ी गई!")

        st.markdown("##### 📋 दर्ज की गई ऐतिहासिक घटनाएं:")
        ev_disp = []
        cat_labels = {
            "career": "💼 नौकरी / पदोन्नति", "marriage": "💍 विवाह", "child": "👶 संतान जन्म",
            "property": "🏠 भूमि / भवन", "travel": "✈️ विदेश यात्रा", "health_accident": "🏥 रोग / शल्य", "education": "🎓 शिक्षा"
        }
        for idx, ev in enumerate(st.session_state["btr_events_store"], 1):
            ev_disp.append({
                "क्र.": idx,
                "घटना तिथि": ev["event_date"].strftime("%d/%m/%Y"),
                "श्रेणी": cat_labels.get(ev["event_category"], ev["event_category"]),
                "विवरण": ev["description"]
            })
        st.dataframe(pd.DataFrame(ev_disp), use_container_width=True, hide_index=True)

        col_clr, col_dum = st.columns([1, 4])
        with col_clr:
            if st.button("🗑️ घटनाएं रीसेट करें", key="btr_clr_ev"):
                st.session_state["btr_events_store"] = [
                    {"event_date": date(2015, 6, 15), "event_category": "career", "description": "प्रथम स्थायी नौकरी / पदोन्नति"}
                ]
                st.rerun()

        st.markdown("---")
        st.markdown("##### ⚙️ शोधन स्कैन सेटिंग्स:")
        col_sc1, col_sc2, col_sc3 = st.columns(3)
        with col_sc1:
            scan_window = st.selectbox("स्कैन समय विंडो (खोज दायरा)", [15, 30, 45, 60, 90, 120], index=1, format_func=lambda x: f"±{x} मिनट ({x*2} मिनट कुल)")
        with col_sc2:
            scan_step = st.selectbox("स्कैन समय अंतराल (Resolution)", [1, 2, 3, 5], index=0, format_func=lambda x: f"{x} मिनट अंतराल")
        with col_sc3:
            native_gender = st.selectbox("जातक लिंग (तत्व शोधन हेतु)", ["male", "female"], format_func=lambda x: "पुरुष (Male)" if x == "male" else "स्त्री (Female)")

        if st.button("⚡ बहु-आयामी जन्म समय शोधन स्कैन चलाएं", type="primary", key="btr_run_scan_btn"):
            ev_objs = [
                LifeEvent(event_date=e["event_date"], event_category=e["event_category"], description=e.get("description", ""))
                for e in st.session_state["btr_events_store"]
            ]
            with st.spinner("विंशोत्तरी दशा, गोचर व षोडशवर्ग सीमा का गहन विश्लेषण जारी है..."):
                btr_candidates = default_btr_service.rectify_birth_time(
                    birth_profile,
                    ev_objs,
                    window_minutes=scan_window,
                    step_minutes=scan_step,
                    gender=native_gender
                )
                st.session_state["btr_latest_candidates"] = btr_candidates

        if "btr_latest_candidates" in st.session_state and st.session_state["btr_latest_candidates"]:
            cand_list = st.session_state["btr_latest_candidates"]
            st.markdown(f"### 🏆 शीर्ष प्रमाणित जन्म समय क्रम (शीर्ष {len(cand_list)} विकल्प):")

            for idx, cand in enumerate(cand_list, 1):
                card_bg = "#ECFDF5" if cand.fit_score >= 80 else ("#FFFBEB" if cand.fit_score >= 65 else "#F8FAFC")
                card_bd = "#10B981" if cand.fit_score >= 80 else ("#F59E0B" if cand.fit_score >= 65 else "#94A3B8")
                st.markdown(f"""
    <div style="background:{card_bg}; border:1.5px solid {card_bd}; border-radius:10px; padding:16px; margin:12px 0 6px 0;">
    <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap;">
    <span style="font-size:16px; font-weight:900; color:#0F172A;">#{idx} संभावित समय: {cand.candidate_time} (विचलन: {cand.offset_minutes:+} मिनट)</span>
    <span style="font-size:13px; font-weight:800; background:#FFFFFF; border:1px solid {card_bd}; padding:3px 10px; border-radius:6px; color:#0F172A;">
    फिट स्कोर: <b>{cand.fit_score}%</b> | {cand.confidence}
    </span>
    </div>
    <div style="font-size:13px; color:#334155; margin-top:8px;">
    • <b>D1 लग्न:</b> {cand.lagna_sign} &nbsp;|&nbsp; <b>D9 नवांश:</b> {cand.navamsha_lagna_sign} &nbsp;|&nbsp; <b>D10 Dashamsha:</b> {cand.dashamsha_lagna_sign} &nbsp;|&nbsp; <b>D60 देवता:</b> {cand.d60_deity}
    </div>
    <div style="font-size:12px; color:#065F46; margin-top:6px; line-height:1.5;">
    📜 <b>शास्त्रीय प्रमाण:</b> {' • '.join(cand.evidence_breakdown)}
    </div>
    </div>
    """, unsafe_allow_html=True)
                col_btn_apply, col_btn_spc = st.columns([2, 3])
                with col_btn_apply:
                    if st.button(f"✅ यह शोधित समय ({cand.candidate_time}) मुख्य कुण्डली में लागू करें", key=f"apply_btr_cand_{idx}", type="primary"):
                        from datetime import datetime as dt_cls
                        parsed_t = dt_cls.strptime(cand.candidate_time, "%H:%M:%S").time()
                        st.session_state["birth_time"] = parsed_t
                        if "birth_profile" in locals() and birth_profile:
                            birth_profile.birth_time = parsed_t
                        st.success(f"🎉 बधाई! जन्म समय को सफलतापूर्वक {cand.candidate_time} पर शोधित कर संपूर्ण सॉफ्टवेयर में लागू कर दिया गया है।")
                        st.rerun()

    # -------------------------------------------------------------------------
    # TAB 2: TATTWA SHODHANA
    # -------------------------------------------------------------------------
    with tab_btr2:
        st.markdown("### 🌿 तत्व शोधन एवं लिंग निर्णय (Tattwa Shodhana & Antar-Tattwa)")
        st.write(
            "उत्तरकालामृत एवं नाड़ी ग्रंथों के अनुसार सूर्योदय से प्रारंभ होकर पंच महाभूत (पृथ्वी, जल, अग्नि, वायु, आकाश) ९०-९० मिनट के चक्र में चलते हैं। "
            "प्रत्येक तत्व में सूक्ष्म अंतर-तत्व होते हैं। जातक के लिंग (स्त्री/पुरुष) के अनुसार जन्म का अंतर-तत्व अनिवार्य रूप से मेल खाना चाहिए।"
        )

        tat_gender = st.radio("जातक लिंग चुनें:", ["male", "female"], format_func=lambda x: "पुरुष (Male)" if x == "male" else "स्त्री (Female)", horizontal=True, key="tat_gen_rad")
        tat_res = default_btr_service.calculate_tattwa_shodhana(birth_profile, tat_gender)

        c_tt1, c_tt2, c_tt3 = st.columns(3)
        c_tt1.metric("स्थानीय सूर्योदय", f"🌅 {tat_res['sunrise_time']}", "खगोलीय वेध")
        c_tt2.metric("इष्टकाल", f"{tat_res['ishta_kala']}", "सूर्योदय से जन्म तक")
        c_tt3.metric("वार प्रारंभ तत्व", f"{tat_res['day_lord_tattwa']}", f"{calc_chart.panchang.vara_name} का अधिपति तत्व")

        st.markdown(f"""
    <div style="background:{tat_res['gender_match_color']}15; border:1.5px solid {tat_res['gender_match_color']}; border-radius:10px; padding:16px; margin:14px 0;">
    <div style="display:flex; justify-content:space-between; align-items:center;">
    <span style="font-size:16px; font-weight:900; color:#0F172A;">सक्रिय महा-तत्व: {tat_res['maha_tattwa']} ({tat_res['maha_tattwa_gender']})</span>
    <span style="font-size:13px; font-weight:800; background:#FFFFFF; border:1px solid {tat_res['gender_match_color']}; padding:3px 10px; border-radius:6px;">
    {tat_res['gender_match_status']}
    </span>
    </div>
    <div style="font-size:13px; color:#1E293B; margin-top:8px; line-height:1.6;">
    • <b>सक्रिय अंतर-तत्व (Sub-Tattwa):</b> {tat_res['antar_tattwa']} ({tat_res['antar_tattwa_gender']})<br/>
    • <b>प्रकृति व गुण:</b> {tat_res['antar_tattwa_nature']}<br/>
    • <b>सक्रिय समय सीमा (Active Window):</b> <code style="font-size:14px; font-weight:800;">{tat_res['current_window']}</code><br/>
    • <b>तत्व शोधन स्कोर:</b> <b>{tat_res['score']}/100</b>
    </div>
    </div>
    """, unsafe_allow_html=True)

        st.markdown("##### ⏱️ जन्म समय के आसपास अंतर-तत्व काल विभाजन सारणी:")
        st.dataframe(pd.DataFrame(tat_res["sub_tattwa_schedule"]), use_container_width=True, hide_index=True)

        st.caption(f"💡 {tat_res['shastric_rule']}")

    # -------------------------------------------------------------------------
    # TAB 3: KUNDA & PRANAPADA
    # -------------------------------------------------------------------------
    with tab_btr3:
        st.markdown("### ☸️ कुण्ड शोधन एवं प्राणपद लग्न (Kunda & Pranapada Shodhana)")
        st.write("बृहत्पाराशर होराशास्त्र (अध्याय ३ व ४) के अनुसार जन्म समय की प्रामाणिकता हेतु कुण्ड नक्षत्र एवं प्राणपद लग्न का त्रिकोण संरेखण अनिवार्य नियम है:")

        kp_kun_res = default_btr_service.calculate_kunda_pranapada(calc_chart, birth_profile)

        col_k1, col_k2 = st.columns(2)
        with col_k1:
            st.markdown("#### ☸️ कुण्ड शोधन (Kunda Shodhana)")
            st.markdown(f"""
    <div style="background:{kp_kun_res['kunda_color']}15; border:1.5px solid {kp_kun_res['kunda_color']}; border-radius:10px; padding:16px;">
    <div style="font-size:16px; font-weight:900; color:#0F172A;">कुण्ड नक्षत्र: #{kp_kun_res['kunda_nakshatra_num']} {kp_kun_res['kunda_nakshatra_name']}</div>
    <div style="font-size:13px; color:#1E293B; margin-top:8px; line-height:1.6;">
    • <b>कुण्ड मान:</b> {kp_kun_res['kunda_nakshatra_val']} (सूत्र: लग्न स्पष्ट × ८१ ÷ २७)<br/>
    • <b>जन्म चन्द्र नक्षत्र:</b> {kp_kun_res['janma_nakshatra_name']}<br/>
    • <b>जन्म लग्न नक्षत्र:</b> {kp_kun_res['lagna_nakshatra_name']}<br/>
    • <b>त्रिकोण स्थिति:</b> {kp_kun_res['kunda_status']}
    </div>
    </div>
    """, unsafe_allow_html=True)
            st.caption("📜 **नियम:** कुण्ड नक्षत्र चन्द्र नक्षत्र या लग्न नक्षत्र से १, १०, अथवा १९वें (त्रिकोण) नक्षत्र में होना चाहिए।")

        with col_k2:
            st.markdown("#### 🕉️ प्राणपद लग्न शोधन (Pranapada Lagna)")
            st.markdown(f"""
    <div style="background:{kp_kun_res['pranapada_color']}15; border:1.5px solid {kp_kun_res['pranapada_color']}; border-radius:10px; padding:16px;">
    <div style="font-size:16px; font-weight:900; color:#0F172A;">प्राणपद राशि: {kp_kun_res['pranapada_sign']} ({kp_kun_res['pranapada_deg']}°)</div>
    <div style="font-size:13px; color:#1E293B; margin-top:8px; line-height:1.6;">
    • <b>प्राणपद स्पष्ट:</b> {kp_kun_res['pranapada_longitude']}°<br/>
    • <b>जन्म लग्न से भाव स्थिति:</b> <b>{kp_kun_res['house_from_lagna']}वां भाव</b><br/>
    • <b>पाराशर शुद्धि निर्णय:</b> {kp_kun_res['pranapada_status']}
    </div>
    </div>
    """, unsafe_allow_html=True)
            st.caption("📜 **पाराशर वचन:** प्राणपद लग्न से केन्द्र, त्रिकोण, द्वितीय या एकादश भाव में हो तो समय शुद्ध होता है। ६, ८, १२ भाव में होना अशुद्धि दर्शाता है।")

    # -------------------------------------------------------------------------
    # TAB 4: DIVISIONAL BOUNDARIES (D9 & D60)
    # -------------------------------------------------------------------------
    with tab_btr4:
        st.markdown("### 📐 षोडशवर्ग D9 व D60 सीमा संवेदनशीलता (Divisional Boundary Precision Scan)")
        st.write(
            "नवांश (D9) मात्र १३ मिनट में और षष्ट्यंश (D60) केवल २ मिनट (१२० सेकंड) में बदल जाता है। "
            "यदि जन्म समय किसी षष्ट्यंश सीमा के निकट हो, तो कुछ ही सेकंड के अंतर से पूरा भाग्य और इष्ट-देवता परिवर्तित हो जाता है:"
        )

        b_scan = default_btr_service.calculate_divisional_boundaries(calc_chart, birth_profile)

        st.markdown(f"""
    <div style="background:{b_scan['vulnerability_color']}15; border:1.5px solid {b_scan['vulnerability_color']}; border-radius:10px; padding:16px; margin-bottom:16px;">
    <div style="font-size:16px; font-weight:900; color:#0F172A;">सीमा संवेदनशीलता स्तर: {b_scan['vulnerability_status']}</div>
    <div style="font-size:13px; color:#1E293B; margin-top:6px; line-height:1.5;">
    निकटतम D60 सीमा से केवल <b>{b_scan['min_d60_border_sec']} सेकंड</b> की दूरी शेष है। इस सूक्ष्म अंतराल पर जन्म समय का सूक्ष्म शोधन अत्यावश्यक है।
    </div>
    </div>
    """, unsafe_allow_html=True)

        col_bd1, col_bd2 = st.columns(2)
        with col_bd1:
            st.markdown("#### 🧘 षष्ट्यंश (D60 - 30 कला = 120 सेकंड)")
            st.write(f"• **षष्ट्यंश भाग संख्या:** भाग #{b_scan['d60_part_num']} / 60")
            st.write(f"• **षष्ट्यंश देवता:** **{b_scan['d60_deity_name']}**")
            st.write(f"• **देवता प्रकृति:** {b_scan['d60_deity_nature']}")
            st.write(f"• **फलित प्रभाव:** {b_scan['d60_deity_meaning']}")
            st.progress(b_scan['d60_progress_pct'] / 100.0, text=f"D60 प्रगति: {b_scan['d60_progress_pct']}% ({b_scan['d60_time_elapsed_sec']}s व्यतीत / {b_scan['d60_time_remain_sec']}s शेष)")

        with col_bd2:
            st.markdown("#### 💍 नवांश (D9 - 3°20' = 800 सेकंड)")
            st.write(f"• **नवांश संख्या:** नवांश #{b_scan['d9_navamsha_num']} / 9")
            st.write(f"• **D1 लग्न अंश:** {b_scan['d1_lagna_deg_str']}")
            st.write(f"• **नवांश में व्यतीत समय:** {b_scan['d9_time_elapsed']}")
            st.write(f"• **अगले नवांश तक शेष समय:** {b_scan['d9_time_remain']}")
            st.progress(b_scan['d9_progress_pct'] / 100.0, text=f"D9 प्रगति: {b_scan['d9_progress_pct']}%")

    # -------------------------------------------------------------------------
    # TAB 5: KP RULING PLANETS
    # -------------------------------------------------------------------------
    with tab_btr5:
        st.markdown("### 👑 के.पी. रूलिंग प्लैनेट्स एवं उप-स्वामी शोधन (KP Ruling Planets BTR)")
        st.write(
            "कृष्णमूर्ति पद्धति (KP System) के अनुसार जन्म समय का अंतिम सत्यापन 'रूलिंग प्लैनेट्स' (Ruling Planets - RPs) एवं "
            "लग्न के 'सब-लॉर्ड' (Sub-Lord) के आपसी संबंध से किया जाता है। जन्म लग्न का सब-लॉर्ड तात्कालिक आर.पी. का सदस्य अथवा उसका कार्यक होना चाहिए:"
        )

        kp_rp_res = default_btr_service.calculate_kp_ruling_planets(calc_chart)

        st.markdown(f"""
    <div style="background:{kp_rp_res['match_color']}15; border:1.5px solid {kp_rp_res['match_color']}; border-radius:10px; padding:16px; margin-bottom:14px;">
    <div style="display:flex; justify-content:space-between; align-items:center;">
    <span style="font-size:16px; font-weight:900; color:#0F172A;">लग्न उप-स्वामी (Lagna Sub-Lord): 👑 {kp_rp_res['lagna_sub_lord']}</span>
    <span style="font-size:13px; font-weight:800; background:#FFFFFF; border:1px solid {kp_rp_res['match_color']}; padding:3px 10px; border-radius:6px;">
    {kp_rp_res['match_rating']}
    </span>
    </div>
    <div style="font-size:13px; color:#1E293B; margin-top:8px;">
    • <b>लग्न स्वामी:</b> {kp_rp_res['lagna_sign_lord']} &nbsp;|&nbsp; <b>लग्न नक्षत्र स्वामी:</b> {kp_rp_res['lagna_star_lord']} &nbsp;|&nbsp; <b>उप-उप स्वामी (SSL):</b> {kp_rp_res['lagna_sub_sub_lord']}
    </div>
    </div>
    """, unsafe_allow_html=True)

        col_rp1, col_rp2 = st.columns(2)
        with col_rp1:
            st.markdown("##### 🏛️ तात्कालिक रूलिंग प्लैनेट्स (Ruling Planets - RPs):")
            st.dataframe(pd.DataFrame(kp_rp_res["ruling_planets_table"]), use_container_width=True, hide_index=True)

        with col_rp2:
            st.markdown("##### 🧬 राहु / केतु नोडल एजेंट (Node Agents):")
            if kp_rp_res["node_agents"]:
                for ag in kp_rp_res["node_agents"]:
                    st.info(f"• {ag}")
            else:
                st.write("कोई प्रत्यक्ष नोडल एजेंट संबद्ध नहीं है।")

            st.caption("📜 **के.पी. रीडर VI नियम:** जब लग्न का सब-लॉर्ड रूलिंग प्लैनेट्स के नक्षत्र या राशि में हो, तब जन्म समय ९९.९% निर्विवाद सिद्ध होता है।")

    # -------------------------------------------------------------------------
    # TAB 6: BEFORE VS AFTER COMPARISON
    # -------------------------------------------------------------------------
    with tab_btr6:
        st.markdown("### ⚖️ मूल बनाम शोधित जन्म समय तुलना सारणी (Before vs After Comparison)")
        st.write("शोधित समय और मूल समय के मध्य कुण्डली, वर्ग, नक्षत्र व दशा में आए परिवर्तनों का प्रत्यक्ष तुलनात्मक अवलोकन:")

        offset_sel = st.slider("शोधन विचलन चुनें (मिनट):", min_value=-60, max_value=60, value=2, step=1, key="comp_offset_slider")
        comp_res = default_btr_service.compare_charts(birth_profile, offset_sel)

        st.dataframe(pd.DataFrame(comp_res["comparison_table"]), use_container_width=True, hide_index=True)

        col_cp1, col_cp2 = st.columns(2)
        with col_cp1:
            st.markdown(f"#### 📜 मूल कुण्डली ({comp_res['original_time']})")
            o_c = comp_res["orig_chart"]
            st.write(f"• **लग्न:** {o_c.lagna_sign_name} ({round(o_c.lagna_degree, 2)}°)")
            st.write(f"• **चन्द्र नक्षत्र:** {o_c.panchang.nakshatra_name} (पाद {o_c.planets['Moon'].nakshatra_pada})")
            st.write(f"• **D9 नवांश लग्न:** {o_c.vargas.get('D9', o_c.vargas.get('D1')).lagna_sign_name}")
            st.write(f"• **D10 दशमांश लग्न:** {o_c.vargas.get('D10', o_c.vargas.get('D1')).lagna_sign_name}")

        with col_cp2:
            st.markdown(f"#### 🎯 शोधित कुण्डली ({comp_res['rectified_time']})")
            r_c = comp_res["rect_chart"]
            st.write(f"• **लग्न:** {r_c.lagna_sign_name} ({round(r_c.lagna_degree, 2)}°)")
            st.write(f"• **चन्द्र नक्षत्र:** {r_c.panchang.nakshatra_name} (पाद {r_c.planets['Moon'].nakshatra_pada})")
            st.write(f"• **D9 नवांश लग्न:** {r_c.vargas.get('D9', r_c.vargas.get('D1')).lagna_sign_name}")
            st.write(f"• **D10 दशमांश लग्न:** {r_c.vargas.get('D10', r_c.vargas.get('D1')).lagna_sign_name}")

    # -------------------------------------------------------------------------
    # TAB 7: MICRO-TUNING SECONDS SLIDER
    # -------------------------------------------------------------------------
    with tab_btr7:
        st.markdown("### 🎯 त्वरित सेकंड्स सूक्ष्म संशोधन स्लाइडर (Interactive Micro-Tuning Seconds Slider)")
        st.write("१ सेकंड से १८० सेकंड (३ मिनट) के अंतर पर D60 षष्ट्यंश, नवांश व लग्न कलाओं का सजीव संशोधन:")

        sec_offset = st.slider("सूक्ष्म सेकंड्स विचलन (Seconds Offset):", min_value=-180, max_value=180, value=0, step=5, key="micro_sec_slider")

        cand_sec_dt = nat_dt + timedelta(seconds=sec_offset)
        temp_data = BirthData(
            name=birth_profile.name,
            birth_date=cand_sec_dt.date(),
            birth_time=cand_sec_dt.time(),
            latitude=birth_profile.latitude,
            longitude=birth_profile.longitude,
            timezone_offset=birth_profile.timezone_offset,
            city=birth_profile.city
        )
        temp_chart = default_chart_calculator.calculate_chart(temp_data)
        temp_chart.vargas = VargaCalculator.calculate_all_vargas(temp_chart)
        temp_b = default_btr_service.calculate_divisional_boundaries(temp_chart, temp_data)
        temp_k = default_btr_service.calculate_kunda_pranapada(temp_chart, temp_data)

        c_sc1, c_sc2, c_sc3 = st.columns(3)
        c_sc1.metric("संशोधित समय", cand_sec_dt.strftime("%H:%M:%S"), f"{sec_offset:+} सेकंड")
        c_sc2.metric("लग्न स्पष्ट", f"{temp_chart.lagna_sign_name}", f"{temp_b['d1_lagna_deg_str']}")
        c_sc3.metric("D60 देवता", f"{temp_b['d60_deity_name']}", f"{temp_b['d60_deity_nature']}")

        st.markdown(f"""
    <div style="background:#F1F5F9; border:1px solid #CBD5E1; border-radius:10px; padding:16px; margin-top:14px;">
    <div style="font-size:15px; font-weight:800; color:#0F172A;">📊 सेकंड्स संशोधन की वास्तविक स्थिति:</div>
    <div style="font-size:13px; color:#334155; margin-top:8px; line-height:1.6;">
    • <b>नवांश (D9):</b> #{temp_b['d9_navamsha_num']} नवांश ({temp_b['d9_progress_pct']}% प्रगति)<br/>
    • <b>षष्ट्यंश सीमा दूरी:</b> {temp_b['d60_time_remain_sec']} सेकंड अगले D60 तक शेष<br/>
    • <b>कुण्ड नक्षत्र स्थिति:</b> {temp_k['kunda_status']}<br/>
    • <b>प्राणपद निर्णय:</b> {temp_k['pranapada_status']}
    </div>
    </div>
    """, unsafe_allow_html=True)

        if sec_offset != 0:
            if st.button(f"✅ इस सूक्ष्म सेकंड्स समय ({cand_sec_dt.strftime('%H:%M:%S')}) को मुख्य कुण्डली में लागू करें", key="btr_apply_micro_sec", type="primary"):
                st.session_state["birth_time"] = cand_sec_dt.time()
                if "birth_profile" in locals() and birth_profile:
                    birth_profile.birth_time = cand_sec_dt.time()
                st.success(f"🎉 बधाई! जन्म समय को सूक्ष्मता से {cand_sec_dt.strftime('%H:%M:%S')} पर संशोधित कर दिया गया है।")
                st.rerun()

    # -------------------------------------------------------------------------
    # TAB 8: CLASSICAL SUTRAS & RULES
    # -------------------------------------------------------------------------
    with tab_btr8:
        st.markdown("### 📜 बृहत्पाराशर एवं नाड़ी शास्त्रीय प्रमाण (Classical Sutras & Rules)")
        st.write("वैदिक ज्योतिष के मूल ग्रंथों से जन्म समय शोधन के अकाट्य सूत्र एवं प्रमाणिक संदर्भ:")

        st.markdown("""
    <div style="background:#FFFBEB; border:1.5px solid #F59E0B; border-radius:10px; padding:16px; margin-bottom:14px;">
    <div style="font-size:16px; font-weight:900; color:#92400E;">📜 बृहत्पाराशर होराशास्त्र (कुण्ड शोधन - अध्याय ४)</div>
    <div style="font-size:14px; font-style:italic; color:#78350F; margin-top:6px;">
    "लग्नं स्पष्टीकृतं कृत्वा गुणयेदेकाशीत्या ततः। भजेत्सप्तविंशत्या यच्छेषं तद्भं कुण्डमुच्यते॥"<br/>
    <b>अर्थ:</b> स्पष्ट लग्न को ८१ से गुणा करके २७ का भाग दें। जो शेष बचे, वह 'कुण्ड नक्षत्र' कहलाता है। यदि कुण्ड नक्षत्र जन्म नक्षत्र के त्रिकोण (१, १०, १९) में हो, तो जन्म समय पूर्णतः शुद्ध होता है।
    </div>
    </div>

    <div style="background:#EFF6FF; border:1.5px solid #3B82F6; border-radius:10px; padding:16px; margin-bottom:14px;">
    <div style="font-size:16px; font-weight:900; color:#1E40AF;">📜 बृहत्पाराशर होराशास्त्र (प्राणपद लग्न - अध्याय ३)</div>
    <div style="font-size:14px; font-style:italic; color:#1E3A8A; margin-top:6px;">
    "इष्टघट्यादिपंक्तिं च पंचदशभिर्विभाजयेत्। लब्धं राश्यादिकं योज्यं भानौ प्राणपदं भवेत्॥"<br/>
    <b>अर्थ:</b> सूर्योदय से इष्टकाल के विलों (विघटियों) को १५ से भाग देकर जो लब्धि आए, उसे सूर्य के स्पष्ट अंशों में जोड़ने पर 'प्राणपद लग्न' प्राप्त होता है। यह लग्न से ६, ८, १२ भाव में न होकर शुभ भावों में होना चाहिए।
    </div>
    </div>

    <div style="background:#ECFDF5; border:1.5px solid #10B981; border-radius:10px; padding:16px; margin-bottom:14px;">
    <div style="font-size:16px; font-weight:900; color:#065F46;">📜 उत्तरकालामृत एवं चन्द्रकला नाड़ी (तत्व शोधन नियम)</div>
    <div style="font-size:13px; color:#064E3B; margin-top:6px; line-height:1.6;">
    • <b>दिनमान विभाजन:</b> सूर्योदय से प्रति ९० मिनट में पंचतत्व (पृथ्वी ६ मि., जल १२ मि., अग्नि १८ मि., वायु २४ मि., आकाश ३० मि.) भ्रमण करते हैं।<br/>
    • <b>वार अधिपति:</b> रविवार/मंगलवार = अग्नि, सोमवार/शुक्रवार = जल, बुधवार = पृथ्वी, गुरुवार = आकाश, शनिवार = वायु तत्व से प्रारंभ होते हैं।<br/>
    • <b>लिंग शुद्धि:</b> पुरुष जातक का जन्म पुरुष तत्व तथा स्त्री जातक का जन्म स्त्री तत्व के अंतर-तत्व में ही संभव है।
    </div>
    </div>
    """, unsafe_allow_html=True)

        st.markdown("""
    ##### 🧭 दैवज्ञ शोधन मार्गदर्शिका (Astrologer's Master Workflow Checklist):
    1. **चरण १ (Macro Check):** लग्न परिवर्तन (D1) व नवांश (D9) की जांच करें कि क्या जातक का स्वभाव और वैवाहिक स्थिति नवांश लग्न के अनुकूल है।
    2. **चरण २ (Event Fitting):** विवाह, प्रथम संतान, व मुख्य करियर उन्नयन की तिथि पर विंशोत्तरी दशा व गुरु-शनि के दोहरे गोचर का मिलान करें।
    3. **चरण ३ (Tattwa Alignment):** इष्टकाल निकालकर वार स्वामी से तत्व व अंतर-तत्व का लिंग से मिलान करें।
    4. **चरण ४ (Kunda & Pranapada Verification):** कुण्ड नक्षत्र एवं प्राणपद लग्न की शुभता सिद्ध करें।
    5. **चरण ५ (Micro-Tuning D60):** षष्ट्यंश (D60) देवता के सात्विक/शुभ स्वभाव और के.पी. सब-लॉर्ड के आर.पी. मिलान से सेकंड्स का अंतिम परिशोधन पूर्ण करें।
    """)


    # =============================================================
    # TAB 14: KUNDALI MILAN & SYNASTRY - SUPREME 10-TAB VEDIC SUITE
    # =============================================================

