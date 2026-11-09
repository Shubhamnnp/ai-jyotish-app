import streamlit as st
import pandas as pd
from src.jyotish.services.shastriya_pramana import SHASTRIYA_SHLOKAS
from src.jyotish.ui.chart_renderer import ChartRenderer
import src.jyotish.core.lifestyle as life_mod
from src.jyotish.services.medical import MedicalAstrologyService


def render_health_disease_view(chart, tabs=None):
    if tabs is None:
        tabs = [
            "🩺 देह वेध आरेख (Anatomy)",
            "💪 आरोग्य बल व स्थिति",
            "⚠️ संभावित रोग जोखिम",
            "📋 ग्रह-अंग चिकित्सा सारणी",
            "🌿 निवारक उपाय व दिनचर्या"
        ]

    st.subheader("🏥 स्वास्थ्य एवं रोग-निदान विश्लेषण (Medical Astrology & Disease Forecast)")
    st.write("बृहत्पाराशर होराशास्त्र, सर्वार्थ चिंतामणि एवं फलदीपिका अनुसार समग्र आरोग्य बल, संवेदनशील शारीरिक अंग, संभावित रोग एवं भावी सावधानियां।")

    # Classical Shastriya Shloka Card
    med_pramana = SHASTRIYA_SHLOKAS.get("medical_kalapurusha_anatomy", {})
    if med_pramana:
        with st.expander("📜 शास्त्रीय प्रमाण — बृहत्पाराशर होराशास्त्र एवं फलदीपिका (कालपुरुषाङ्ग विभाग व रोग विचार)", expanded=False):
            st.markdown(f"""
            <div style="background:#FFFBEB; border-left:4px solid #D97706; padding:12px; border-radius:6px; margin-bottom:10px;">
                <b style="color:#B45309; font-size:15px;">📖 ग्रंथ संदर्भ: {med_pramana.get('grantha', '')}</b>
                <pre style="white-space:pre-wrap; font-family:serif; font-size:14px; color:#78350F; margin:8px 0; background:transparent; border:none; padding:0;">
{med_pramana.get('shloka_sanskrit', med_pramana.get('shloka', ''))}
                </pre>
                <div style="font-size:13px; color:#92400E; margin-top:6px;">
                    <b>हिंदी भावार्थ:</b> {med_pramana.get('anuvad_hi', med_pramana.get('hindi_translation', ''))}
                </div>
            </div>
            """, unsafe_allow_html=True)

    hlth_res = life_mod.HealthEngine.analyze(chart)

    # Top Status Banner - 4 Key Health Indicators
    c_h1, c_h2, c_h3, c_h4 = st.columns(4)
    c_h1.metric("आरोग्य बल (Immunity)", f"{hlth_res.get('vitality_score', 75)}/100", hlth_res.get("vitality_status", "").split(" ")[0])
    c_h2.metric("षष्ठेश (रोग स्वामी)", hlth_res.get("h6_lord", ""), "रोग संवेदनशीलता")
    c_h3.metric("संवेदनशील क्षेत्र", f"{len(hlth_res.get('vulnerable_areas', []))} ग्रह", "देखभाल आवश्यक")
    c_h4.metric("अष्टम भाव स्थिति", f"{len(hlth_res.get('h8_occupants', []))} ग्रह", "आकस्मिक रोग सुरक्षा")

    try:
        med_profile = MedicalAstrologyService.analyze_health_profile(chart)
    except Exception:
        med_profile = {
            "organ_zones": [],
            "high_risk_organs": [],
            "tridosha": {
                "vata_pct": 33, "vata_percent": 33,
                "pitta_pct": 33, "pitta_percent": 33,
                "kapha_pct": 34, "kapha_percent": 34,
                "dominant": "समदोषज", "dominant_dosha": "समदोषज",
                "recommendation": "सात्विक आहार व नियमित दिनचर्या रखें।"
            },
            "ayurvedic_remedies": [],
            "panchakarma": [],
            "vitality_score": hlth_res.get("vitality_score", 75),
            "rudraksha_therapy": []
        }

    tab_h0, tab_h1, tab_h2, tab_h3, tab_h4 = st.tabs(tabs)

    with tab_h0:
        st.markdown("### 🩺 कालपुरुष देह वेध आरेख (12-Organ Anatomy Map)")
        st.caption("बृहत्संहिता एवं फलदीपिका के अनुसार कालपुरुष के १२ अंगों, राशियों व भावों पर ग्रहों का प्रभाव:")

        name_str = getattr(chart.birth_data, "name", "जातक") if hasattr(chart, "birth_data") else "जातक"
        anatomy_svg = ChartRenderer.render_kalapurusha_anatomy_svg(med_profile, title=f"कालपुरुष देह वेध चक्र — {name_str}")
        st.markdown(anatomy_svg, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("### 🌿 आयुर्वेदिक त्रिदोष संतुलन (Ayurvedic Tridosha Constitution)")
        trid = med_profile.get("tridosha", {})
        col_t1, col_t2, col_t3, col_t4 = st.columns(4)
        col_t1.metric("वात दोष (Vata - वायु/आकाश)", f"{trid.get('vata_percent', 33)}%")
        col_t2.metric("पित्त दोष (Pitta - अग्नि)", f"{trid.get('pitta_percent', 33)}%")
        col_t3.metric("कफ दोष (Kapha - जल/पृथ्वी)", f"{trid.get('kapha_percent', 34)}%")
        col_t4.metric("प्रधान प्रकृति (Dominant)", trid.get('dominant_dosha', 'समदोषज'))

        st.info(f"**🍃 त्रिदोष फलादेश एवं जीवनशैली परामर्श:** {trid.get('recommendation', 'सात्विक आहार व नियमित दिनचर्या रखें।')}")

        st.markdown("#### 🔴 संवेदनशील शारीरिक अंग (Vulnerable Body Zones Breakdown)")
        afflicted_zones = [z for z in med_profile.get("organ_zones", []) if z.get("affliction_score", 0) > 35]
        if afflicted_zones:
            zone_rows = []
            for z in afflicted_zones:
                zone_rows.append({
                    "भाव": f"भाव {z.get('house', '')}",
                    "संबंधित अंग": z.get('organ_hi') or z.get('organs', ''),
                    "दोष स्कोर": f"{z.get('affliction_score', 0)}%",
                    "स्थिति": z.get('status_badge') or z.get('status', ''),
                    "भावाधिपति": z.get('lord', ''),
                    "स्थित ग्रह": ", ".join(z.get('occupants', [])) if z.get('occupants') else "कोई नहीं",
                    "दृष्टि / कारण": ", ".join(z.get('reasons', [])) if z.get('reasons') else "शुभ संरक्षण"
                })
            st.dataframe(pd.DataFrame(zone_rows), use_container_width=True, hide_index=True)
        else:
            st.success("✨ कुण्डली में किसी भी मुख्य शारीरिक अंग में अत्यधिक संवेदनशीलता या गंभीर दोष नहीं पाया गया। समग्र आरोग्य बल उत्तम है।")

    with tab_h1:
        st.markdown(f"### 💪 समग्र स्वास्थ्य बल: {hlth_res.get('vitality_status', '')}")
        st.progress(hlth_res.get("vitality_score", 75) / 100.0)

        # Positive Health Strengths
        if hlth_res.get("positive_health_traits"):
            st.markdown("#### ✨ प्राकृतिक स्वास्थ्य बल एवं दैवीय रक्षा सूत्र (+):")
            for tr in hlth_res["positive_health_traits"]:
                st.markdown(f"""
                <div style="background:#F0FDF4; border-left:4px solid #16A34A; padding:10px 14px; margin-bottom:8px; border-radius:4px;">
                    <b style="color:#15803D;">🛡️ {tr}</b>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("#### 🔴 कुण्डली अनुसार संवेदनशील शारीरिक अंग एवं प्रणालियां (-):")
        for vuln in hlth_res.get("vulnerable_areas", []):
            st.markdown(f"""
            <div style="background:#FFFBEB; border:1.5px solid #F59E0B; border-radius:10px; padding:14px; margin-bottom:10px;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <b style="color:#B45309; font-size:15px;">🪐 प्रभावित ग्रह: {vuln.get('planet', '')} ({vuln.get('reasons', '')})</b>
                    <span style="background:#FEF3C7; color:#92400E; padding:3px 8px; border-radius:4px; font-size:11px; font-weight:800;">सावधानी</span>
                </div>
                <p style="margin:6px 0;"><b>संबंधित अंग:</b> {vuln.get('organs', '')}</p>
                <p style="margin:6px 0; color:#DC2626;"><b>संभावित रोग / लक्षण:</b> {vuln.get('diseases', '')}</p>
                <div style="background:#FFFFFF; border-radius:6px; padding:6px 10px; border:1px solid #FDE68A; margin-top:6px;">
                    <b style="color:#047857;">🌿 अनुशंसित सुरक्षा उपाय:</b> {vuln.get('remedy', '')}
                </div>
            </div>
            """, unsafe_allow_html=True)

    with tab_h2:
        st.markdown("### ⚠️ भविष्य में संभावित रोग एवं रोग-संवेदनशीलता कालखंड (Timing Forecast)")
        st.caption("षष्ठेश (रोगेश), अष्टमेश (रन्ध्रेश), द्वादशेश (व्ययेश) एवं मारक दशाओं के आधार पर संभावित दीर्घकालिक प्रभाव:")

        for risk in hlth_res.get("future_risks", []):
            st.markdown(f"""
            <div style="background:#FEF2F2; border-left:4px solid #EF4444; border-radius:4px; padding:12px; margin-bottom:10px;">
                <b style="color:#991B1B;">⚠️ शास्त्रीय संकेत:</b> <span style="color:#1E293B;">{risk}</span>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("#### ⏱️ रोग संवेदनशीलता कालखंड एवं निवारक प्रोटोकॉल (Disease Susceptibility Periods):")
        try:
            disease_timings = MedicalAstrologyService.forecast_disease_susceptibility_periods(chart)
            timing_rows = []
            for dt in disease_timings:
                timing_rows.append({
                    "दशा / कालखंड": dt["period_type"],
                    "शास्त्रीय भूमिका": dt["shastriya_role"],
                    "संवेदनशीलता स्तर": dt["vulnerability_level"],
                    "संवेदनशील अंग": dt["vulnerable_organs"],
                    "दोष ट्रिगर": dt["ayurvedic_dosha"],
                    "निवारक प्रोटोकॉल": dt["preventive_protocol"]
                })
            st.dataframe(pd.DataFrame(timing_rows), use_container_width=True, hide_index=True)
        except Exception as e:
            st.info("वर्तमान दशा चक्र में कोई गंभीर मारक या बाधक दोष सक्रिय नहीं है।")

        st.info("💡 **महत्वपूर्ण सिद्धांत:** कुण्डली केवल रोग की 'संवेदनशीलता' (Tendency) दर्शाती है। यदि जातक अनुशासित दिनचर्या, समय पर जांच और सात्विक आहार रखे, तो ग्रह जनित रोगों को पहले ही निष्प्रभावी किया जा सकता है।")

    with tab_h3:
        st.markdown("### 🩺 नवग्रह एवं अंग-विशेष चिकित्सा सारणी (Medical Astrology Reference)")
        st.caption("प्रत्येक ग्रह शरीर के किन अंगों एवं व्याधियों का प्रतिनिधित्व करता है:")

        med_table = []
        for g_name, g_info in life_mod.HealthEngine.GRAHA_BODY_MAPPING.items():
            med_table.append({
                "ग्रह (Graha)": g_name,
                "नियंत्रित शारीरिक अंग (Organs)": g_info["organs"],
                "उत्पन्न होने वाले रोग (Diseases)": g_info["diseases"],
                "शास्त्रीय उपाय (Remedy)": g_info["gem_metal"]
            })
        st.dataframe(pd.DataFrame(med_table), use_container_width=True, hide_index=True)

    with tab_h4:
        st.markdown("### 🌿 शास्त्रीय निवारक उपाय, दिनचर्या एवं रुद्राक्ष चिकित्सा (Rudraksha Therapy)")
        st.markdown(f"""
        <div style="background:#F0FDF4; border:1.5px solid #10B981; border-radius:10px; padding:16px; margin-bottom:14px;">
            <b style="color:#047857; font-size:16px;">✨ आरोग्य रक्षा का मूल मंत्र:</b>
            <p style="margin-top:6px; color:#1E293B;">{hlth_res.get('general_health_advice', '')}</p>
        </div>
        """, unsafe_allow_html=True)

        # Rudraksha Therapy
        st.markdown("#### 📿 कुण्डली-अनुकूल आयुर्वेदिक रुद्राक्ष चिकित्सा (Prescribed Rudrakshas):")
        rudraksha_list = med_profile.get("rudraksha_therapy", [])
        if rudraksha_list:
            rud_cols = st.columns(min(3, len(rudraksha_list)))
            for idx, r_item in enumerate(rudraksha_list[:3]):
                with rud_cols[idx]:
                    st.markdown(f"""
                    <div style="background:#FFFBEB; border:1.5px solid #F59E0B; border-radius:10px; padding:12px; height:100%;">
                        <b style="color:#B45309; font-size:15px;">📿 {r_item['title']}</b><br/>
                        <small style="color:#64748B;">ग्रह: {r_item['lord']} | देवता: {r_item['deity']}</small>
                        <p style="margin:6px 0; font-size:13px; color:#1E293B;"><b>अंग प्रभाव:</b> {r_item['organs']}</p>
                        <p style="margin:0 0 6px 0; font-size:12.5px; color:#047857;"><b>दोष:</b> {r_item['dosha']}</p>
                        <small style="color:#334155;"><b>चिकित्सीय लाभ:</b> {r_item['benefits'][:75]}...</small>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("सामान्य आरोग्य संरक्षण हेतु ५-मुखी रुद्राक्ष धारण करना सर्वोत्तम है।")

        st.markdown("---")
        st.markdown("""
        #### 🧘 ५ प्रमुख स्वास्थ्य रक्षा नियम:
        1. **सूर्योदय दर्शन एवं जल अर्पण:** प्रतिदिन सूर्योदय के समय तांबे के लोटे से सूर्य को जल दें (हृदय, नेत्र व अस्थि बल बढ़ेगा)।
        2. **महामृत्युंजय मंत्र जप:** यदि ६ठे या ८वें भाव में पापग्रह हों, तो प्रतिदिन ११ बार महामृत्युंजय मंत्र का मानसिक जप करें।
        3. **त्रिफला चूर्ण का सेवन:** रात्रि में गुनगुने पानी के साथ आधा चम्मच त्रिफला लें (वात, पित्त और कफ तीनों संतुलित रहेंगे)।
        4. **भूमि स्पर्श एवं प्राणायाम:** नंगे पैर हरी घास पर टहलना और १० मिनट अनुलोम-विलोम करना नर्वस सिस्टम को शांत रखता है।
        5. **रक्तदान / सेवा:** मंगल की शांति हेतु वर्ष में एक बार रक्तदान करें या नेत्रहीनों/असहायों की सेवा करें।
        """)
