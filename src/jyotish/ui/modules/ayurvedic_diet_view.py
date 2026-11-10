# -*- coding: utf-8 -*-
"""
Module 23: Ayurvedic Diet & Tridosha Nutrition View.
Evaluates Tridosha Prakriti (Vata, Pitta, Kapha), Lagna & Moon Nakshatra-Pada,
Sun's Jatharagni, 2nd House (Food & Taste) and 6th House (Digestion & Disease),
with complete Ansh-Kala-Vikala (DMS) precision, Shad-Rasa balancing, and Charaka Viruddha Ahara guidelines.
"""

import streamlit as st
import pandas as pd
from typing import List, Optional
from src.jyotish.core.constants import SIGN_NAMES
from src.jyotish.services.shastriya_pramana import SHASTRIYA_SHLOKAS
import src.jyotish.core.lifestyle as life_mod

# Classical Graha Hindi Names & Natural Significations
GRAHA_NAMES_HI = {
    "Sun": "सूर्य", "Moon": "चंद्र", "Mars": "मंगल", "Mercury": "बुध",
    "Jupiter": "गुरु", "Venus": "शुक्र", "Saturn": "शनि", "Rahu": "राहु", "Ketu": "केतु",
    "Ascendant": "लग्न"
}

DIGNITY_HI = {
    "exalted": "उच्च (Exalted)",
    "moolatrikona": "मूलत्रिकोण (Moolatrikona)",
    "own": "स्वराशि (Own Sign)",
    "great_friend": "अधिमित्र (Great Friend)",
    "friend": "मित्र (Friend)",
    "neutral": "सम (Neutral)",
    "enemy": "शत्रु (Enemy)",
    "great_enemy": "अधिशत्रु (Great Enemy)",
    "debilitated": "नीच (Debilitated)"
}

GRAHA_AYURVEDIC_DHATU = {
    "Sun": ("पित्त दोष (Pitta)", "अस्थि धातु (Bones), हृदय व तेज"),
    "Moon": ("कफ दोष (Kapha)", "रस व रक्त धातु (Body Fluids & Plasma), मन"),
    "Mars": ("पित्त दोष (Pitta)", "मज्जा धातु व रक्त (Bone Marrow & Blood), पित्त पित्ताशय"),
    "Mercury": ("त्रिदोष सम (Tridosha)", "त्वचा व स्नायु धातु (Skin, Nerves & Brain)"),
    "Jupiter": ("कफ दोष (Kapha)", "मेद धातु (Body Fat), यकृत (Liver) व ओज"),
    "Venus": ("कफ-वात दोष (Kapha-Vata)", "शुक्र धातु (Reproductive Tissue & Vital Fluids)"),
    "Saturn": ("वात दोष (Vata)", "स्नायु, जोड़, नसें व अस्थि संधि (Nerves & Joints)"),
    "Rahu": ("तमोगुणी वात (Vata/Toxins)", "विषाक्त तत्व, गैस, एलर्जी व सूक्ष्म संक्रमण"),
    "Ketu": ("अग्नि-वात (Pitta-Vata)", "सूक्ष्म नाड़ियां, पाचन मन्दता व चर्म विकार")
}

AYURVEDA_SHLOKA = {
    "title": "अष्टांगहृदयम् एवं चरक संहिता — त्रिदोष एवं अन्नपानविधि",
    "source": "महर्षि वाग्भट विरचित 'अष्टांगहृदयम्' (सूत्रस्थान, अध्याय १) एवं महर्षि चरक 'चरक संहिता' (सूत्रस्थान, अध्याय २७)",
    "shloka": "वातः पित्तं कफश्चेति त्रयो दोषाः समासतः ।\nविकृताऽविकृता देहं घ्नन्ति ते वर्तयन्ति च ॥\nरसायनानि सर्वाणि आहाराधीनानि देहिनाम् ।\nतस्मादाहारनियमं कुर्यान्नित्यं विचक्षणः ॥",
    "meaning": "वात, पित्त और कफ—ये तीन शारीरिक दोष हैं। सम स्थिति में रहने पर ये देह का पोषण व स्वास्थ्य रक्षा करते हैं और विषम होने पर रोग उत्पन्न करते हैं। समस्त ओज, तेज और जीवन आहार के अधीन है, अतः बुद्धिमान मनुष्य को सदा शास्त्रोक्त आहार नियमों का पालन करना चाहिए।"
}


def _format_dms(deg_val):
    """Calculates classical Ansh (Degrees), Kala (Arcminutes), and Vikala (Arcseconds)."""
    deg = float(deg_val) if deg_val is not None else 0.0
    ansh = int(deg)
    rem_min = (deg - ansh) * 60.0
    kala = int(rem_min)
    vikala = int(round((rem_min - kala) * 60.0))
    if vikala >= 60:
        vikala = 0
        kala += 1
    if kala >= 60:
        kala = 0
        ansh += 1
    return ansh, kala, vikala, f"{ansh}° {kala:02d}' {vikala:02d}\""


def render_ayurvedic_diet_view(chart, tabs: Optional[List[str]] = None):
    if tabs is None:
        tabs = [
            "🌿 त्रिदोष शारीरिक प्रकृति",
            "✅ अनुकूल आहार व रस",
            "❌ वर्जित आहार व परहेज",
            "⏰ भोजन नियम व उपवास"
        ]

    st.subheader("🍽️ खानपान एवं त्रिदोष आहार परामर्श (Diet & Ayurvedic Nutrition)")
    st.write("बृहत्पाराशर होराशास्त्र एवं चरक-सुश्रुत-अष्टांगहृदयम् अनुसार सक्रिय जातक की कुण्डली, ग्रह-नक्षत्र, लग्न, २य भाव (भोजन) एवं ६ठे भाव (पाचन) आधारित पूर्ण आहार परामर्श।")

    # 1. Classical Shastriya Shloka Card
    with st.expander(f"📜 शास्त्रीय प्रमाण — {AYURVEDA_SHLOKA['title']}", expanded=False):
        st.markdown(f"""
        <div style="background:#FFFBEB; border-left:4px solid #D97706; padding:12px; border-radius:6px; margin-bottom:10px;">
            <b style="color:#B45309; font-size:15px;">📖 ग्रंथ संदर्भ: {AYURVEDA_SHLOKA['source']}</b>
            <pre style="white-space:pre-wrap; font-family:serif; font-size:14px; color:#78350F; margin:8px 0; background:transparent; border:none; padding:0;">
{AYURVEDA_SHLOKA['shloka']}
            </pre>
            <div style="font-size:13px; color:#92400E; margin-top:6px;">
                <b>हिंदी भावार्थ:</b> {AYURVEDA_SHLOKA['meaning']}
            </div>
        </div>
        """, unsafe_allow_html=True)

    diet_res = life_mod.DietEngine.analyze(chart)

    # 2. Active Native Micro Tridosha HUD Console with Ansh, Kala, Vikala
    if chart is not None:
        l_deg = getattr(chart, "lagna_degree", 0.0)
        if not isinstance(l_deg, (int, float)):
            l_deg = 0.0
        _, _, _, l_dms = _format_dms(l_deg)

        l_sign = getattr(chart, "lagna_sign", 1)
        if not isinstance(l_sign, int):
            l_sign = getattr(chart, "lagna_sign_id", 1)
        if not isinstance(l_sign, int):
            l_sign = 1
        l_sign_name = SIGN_NAMES[l_sign - 1] if 1 <= l_sign <= 12 else f"Sign {l_sign}"

        moon = chart.planets.get("Moon") if hasattr(chart, "planets") and isinstance(chart.planets, dict) else None
        if moon:
            m_deg = getattr(moon, "sign_degree", 0.0)
            if not isinstance(m_deg, (int, float)):
                m_deg = 0.0
            _, _, _, m_dms = _format_dms(m_deg)
            m_nak = getattr(moon, "nakshatra_name", getattr(moon, "nakshatra", "—"))
            m_pada = getattr(moon, "nakshatra_pada", getattr(moon, "pada", 1))
            m_sign = getattr(moon, "sign_id", getattr(moon, "sign", 1))
            if not isinstance(m_sign, int):
                m_sign = 1
            m_sign_name = SIGN_NAMES[m_sign - 1] if 1 <= m_sign <= 12 else f"Sign {m_sign}"
        else:
            m_dms, m_nak, m_pada, m_sign_name = "—", "—", 1, "—"

        st.markdown(f"""
        <div style="background:linear-gradient(135deg, #064E3B 0%, #065F46 100%); color:#FFFFFF; border-radius:10px; padding:14px 18px; margin-bottom:12px; box-shadow:0 4px 6px -1px rgba(0,0,0,0.1);">
            <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; margin-bottom:8px;">
                <span style="font-size:16px; font-weight:700;">🌿 सक्रिय जातक त्रिदोष वेध: <span style="color:#FDE047;">{getattr(chart, 'name', 'सक्रिय कुण्डली')}</span></span>
                <span style="font-size:13px; color:#A7F3D0;">🏛️ लग्न: <b>{l_sign_name} ({l_dms})</b> | 🌙 चंद्र: <b>{m_sign_name} ({m_dms})</b> | 🌟 <b>{m_nak} (पद {m_pada})</b></span>
            </div>
            <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(130px, 1fr)); gap:10px; font-size:12.5px; text-align:center;">
                <div style="background:rgba(255,255,255,0.08); padding:8px; border-radius:6px; border:1px solid rgba(255,255,255,0.15);">
                    <div style="color:#A7F3D0; font-size:11px;">प्राथमिक शारीरिक प्रकृति</div>
                    <div style="font-size:15px; font-weight:700; color:#FFFFFF;">{diet_res.get('primary_dosha', 'पित्त')}</div>
                    <div style="font-size:10px; color:#6EE7B7;">लग्न तत्व: {diet_res.get('lagna_element', 'अग्नि')}</div>
                </div>
                <div style="background:rgba(255,255,255,0.08); padding:8px; border-radius:6px; border:1px solid rgba(255,255,255,0.15);">
                    <div style="color:#FDE047; font-size:11px;">चंद्र नक्षत्र त्रिदोष</div>
                    <div style="font-size:15px; font-weight:700; color:#FEF08A;">{diet_res.get('nakshatra_dosha', 'सम')}</div>
                    <div style="font-size:10px; color:#FEF9C3;">{diet_res.get('moon_nakshatra', 'अश्विनी')} (पद {diet_res.get('moon_pada', 1)})</div>
                </div>
                <div style="background:rgba(255,255,255,0.08); padding:8px; border-radius:6px; border:1px solid rgba(255,255,255,0.15);">
                    <div style="color:#FCA5A5; font-size:11px;">सूर्य जठराग्नि स्थिति</div>
                    <div style="font-size:15px; font-weight:700; color:#FCA5A5;">{diet_res.get('sun_jatharagni', 'सम जठराग्नि').split(' (')[0]}</div>
                    <div style="font-size:10px; color:#FECACA;">चयापचय व पाचन</div>
                </div>
                <div style="background:rgba(255,255,255,0.08); padding:8px; border-radius:6px; border:1px solid rgba(255,255,255,0.15);">
                    <div style="color:#93C5FD; font-size:11px;">लवण व रस परामर्श</div>
                    <div style="font-size:15px; font-weight:700; color:#BFDBFE;">सेंधा नमक (Rock Salt)</div>
                    <div style="font-size:10px; color:#DBEAFE;">दोष शमन रस</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Micro Planetary Ayurvedic Status Grid Expander with Ansh-Kala-Vikala
        with st.expander("🪐 सक्रिय जातक सूक्ष्म ग्रह-स्थिति (अंश, कला, विकला, नक्षत्र, चरण व त्रिदोष-धातु प्रभाव)", expanded=False):
            planets_data = []
            if hasattr(chart, "planets") and isinstance(chart.planets, dict):
                for p_name, p_obj in chart.planets.items():
                    if p_name in ["Uranus", "Neptune", "Pluto"]:
                        continue
                    p_hi = GRAHA_NAMES_HI.get(p_name, p_name)
                    s_id = getattr(p_obj, "sign_id", getattr(p_obj, "sign", 1))
                    s_name = SIGN_NAMES[s_id - 1] if 1 <= s_id <= 12 else f"Sign {s_id}"
                    deg = getattr(p_obj, "sign_degree", 0.0)
                    _, _, _, dms_str = _format_dms(deg)
                    nak = getattr(p_obj, "nakshatra_name", getattr(p_obj, "nakshatra", "—"))
                    pada = getattr(p_obj, "nakshatra_pada", getattr(p_obj, "pada", 1))
                    house = getattr(p_obj, "house_from_lagna", getattr(p_obj, "house", "—"))

                    dignity_raw = getattr(p_obj, "dignity", "neutral")
                    dignity_hi = DIGNITY_HI.get(str(dignity_raw).lower(), str(dignity_raw))
                    is_retro = getattr(p_obj, "is_retrograde", False)
                    status_tag = " (🔄 वक्री)" if is_retro else ""

                    dhatu_info = GRAHA_AYURVEDIC_DHATU.get(p_name, ("त्रिदोष", "सामान्य"))

                    planets_data.append({
                        "ग्रह": f"{p_hi} ({p_name})",
                        "भाव": f"भाव {house}",
                        "राशि": s_name,
                        "अंश-कला-विकला (DMS)": dms_str,
                        "नक्षत्र व पद": f"{nak} (पद {pada})",
                        "अवस्था": f"{dignity_hi}{status_tag}",
                        "शारीरिक दोष प्रभाव": dhatu_info[0],
                        "अधिष्ठित धातु / अंग": dhatu_info[1]
                    })
            if planets_data:
                st.dataframe(pd.DataFrame(planets_data), use_container_width=True, hide_index=True)

    rendered_tabs = st.tabs(tabs)
    tab_d1, tab_d2, tab_d3, tab_d4 = rendered_tabs[0], rendered_tabs[1], rendered_tabs[2], rendered_tabs[3]

    # -------------------------------------------------------------
    # TAB 1: त्रिदोष शारीरिक प्रकृति
    # -------------------------------------------------------------
    with tab_d1:
        st.markdown(f"### 🌿 आपकी शारीरिक प्रकृति: {diet_res.get('dosha_title', '')}")
        st.info(diet_res.get("characteristics", ""))

        st.markdown("---")
        st.markdown("#### 🪐 सक्रिय जातक कुण्डली के ग्रह, नक्षत्र व भावों का सूक्ष्म विश्लेषण:")

        # 1. Lagna & Lagnesha
        st.markdown(f"""
        <div style="background:#F0FDF4; border-left:4px solid #16A34A; padding:12px 16px; margin-bottom:10px; border-radius:6px;">
            <b style="color:#15803D; font-size:15px;">🛡️ १. लग्न एवं लग्नेश (शारीरिक गठन व ओज):</b><br/>
            <span style="color:#1E293B; font-size:14px;">{diet_res.get('lagnesh_summary', '')} लग्न तत्व: <b>{diet_res.get('lagna_element', '')}</b> होने से देह का प्राथमिक दोष <b>{diet_res.get('primary_dosha', '')}</b> है।</span>
        </div>
        """, unsafe_allow_html=True)

        # 2. Moon & Nakshatra Dosha
        st.markdown(f"""
        <div style="background:#EFF6FF; border-left:4px solid #2563EB; padding:12px 16px; margin-bottom:10px; border-radius:6px;">
            <b style="color:#1D4ED8; font-size:15px;">🌙 २. चंद्र एवं नक्षत्र त्रिदोष (मनःस्थिति व जल-तत्व):</b><br/>
            <span style="color:#1E293B; font-size:14px;">चंद्रमा <b>{diet_res.get('moon_nakshatra', '')}</b> नक्षत्र के <b>पद {diet_res.get('moon_pada', 1)}</b> में स्थित हैं। शास्त्रीय आयुर्वेद अनुसार यह नक्षत्र <b>{diet_res.get('nakshatra_dosha', '')}</b> को नियंत्रित करता है। यह आपके मानसिक तनाव एवं भावनात्मक भूख (Emotional Eating) को सीधे प्रभावित करता है।</span>
        </div>
        """, unsafe_allow_html=True)

        # 3. Sun's Jatharagni
        st.markdown(f"""
        <div style="background:#FFF7ED; border-left:4px solid #EA580C; padding:12px 16px; margin-bottom:10px; border-radius:6px;">
            <b style="color:#C2410C; font-size:15px;">☀️ ३. सूर्य एवं जठराग्नि (पाचन अग्नि व चयापचय):</b><br/>
            <span style="color:#1E293B; font-size:14px;"><b>स्थिति:</b> {diet_res.get('sun_jatharagni', '')}<br/>
            <b>प्रभाव:</b> {diet_res.get('sun_status_note', '')}</span>
        </div>
        """, unsafe_allow_html=True)

        # 4. 2nd House Analysis (Food & Habits)
        st.markdown(f"#### 🍽️ द्वितीय भाव (खान-पान स्वभाव, रुचियां व संस्कार — स्वामी: {diet_res.get('h2_lord', '')}):")
        if diet_res.get("h2_occupants"):
            st.caption(f"द्वितीय भाव में स्थित ग्रह: {', '.join(diet_res.get('h2_occupants'))}")
        for note in diet_res.get("eating_habits", []):
            st.markdown(f"""
            <div style="background:#F8FAFC; border-left:4px solid #3B82F6; padding:10px 14px; margin-bottom:8px; border-radius:4px;">
                {note}
            </div>
            """, unsafe_allow_html=True)

        # 5. 6th House (Digestive Vulnerabilities)
        st.markdown(f"#### ⚠️ षष्ठ भाव (पाचन तंत्र संवेदनशीलता व रोग विचार — स्वामी: {diet_res.get('h6_lord', '')}):")
        if diet_res.get("h6_occupants"):
            st.caption(f"षष्ठ भाव में स्थित ग्रह: {', '.join(diet_res.get('h6_occupants'))}")
        for warn in diet_res.get("digestive_warnings", []):
            st.markdown(f"""
            <div style="background:#FFFBEB; border-left:4px solid #F59E0B; padding:10px 14px; margin-bottom:8px; border-radius:4px;">
                <b>सावधानी:</b> {warn}
            </div>
            """, unsafe_allow_html=True)

    # -------------------------------------------------------------
    # TAB 2: अनुकूल आहार व रस
    # -------------------------------------------------------------
    with tab_d2:
        st.markdown("### ✅ आपके शरीर के लिए सर्वोत्तम अनुकूल खाद्य पदार्थ व षड्रस")
        st.caption("इन पदार्थों का नियमित सेवन आपके त्रिदोष को संतुलित रखेगा और ओज व रोग-प्रतिरोधक क्षमता बढ़ाएगा:")

        p_dosha = diet_res.get("primary_dosha", "")
        if "Pitta" in p_dosha:
            rasa_text = "मधुर (मीठा), तिक्त (कड़वा/नीम-करेला), कषाय (कसैला/आंवला) रस पित्त का शमन करते हैं। अम्ल (खट्टा), लवण (नमकीन) व कटु (तीखा) रस पित्त को बढ़ाते हैं।"
        elif "Vata" in p_dosha:
            rasa_text = "मधुर (मीठा), अम्ल (हल्का खट्टा), लवण (सेंधा नमक) रस वात का शमन करते हैं। कटु (तीखा), तिक्त (कड़वा) व कषाय रस वात व गैस को बढ़ाते हैं।"
        else:
            rasa_text = "कटु (तीखा), तिक्त (कड़वा), कषाय (कसैला) रस कफ का शमन करते हैं। मधुर, अम्ल व लवण रस कफ व मेद (मोटापा) को बढ़ाते हैं।"

        st.markdown(f"""
        <div style="background:#F0FDF4; border:1.5px solid #86EFAC; border-radius:8px; padding:12px; margin-bottom:14px;">
            <b style="color:#15803D; font-size:15px;">👅 आपके दोष अनुसार अनुकूल रस (षड्रस सिद्धान्त):</b><br/>
            <span style="color:#1E293B; font-size:13.5px;">{rasa_text}</span>
        </div>
        """, unsafe_allow_html=True)

        for item in diet_res.get("favorable_foods", []):
            cat_name = item.split(":")[0] if ":" in item else "खाद्य"
            cat_items = item.split(":")[1] if ":" in item else item
            st.markdown(f"""
            <div style="background:#FFFFFF; border:1px solid #BBF7D0; border-left:4px solid #22C55E; border-radius:6px; padding:10px 14px; margin-bottom:8px;">
                <b style="color:#15803D;">🌱 {cat_name}:</b> <span style="color:#1E293B;">{cat_items}</span>
            </div>
            """, unsafe_allow_html=True)

        st.markdown(f"""
        <div style="background:#F8FAFC; border:1px solid #CBD5E1; border-radius:8px; padding:12px; margin-top:14px;">
            <b>🥤 अनुकूलतम पेय:</b> {diet_res.get('favorable_drink', 'गुनगुना पानी')}<br/>
            <b>🧂 लवण निर्देश:</b> {diet_res.get('salt_recommendation', 'सेंधा नमक')}
        </div>
        """, unsafe_allow_html=True)

    # -------------------------------------------------------------
    # TAB 3: वर्जित आहार व परहेज
    # -------------------------------------------------------------
    with tab_d3:
        st.markdown("### ❌ प्रतिकूल खाद्य पदार्थ (जिनसे परहेज रखें)")
        st.caption("ये खाद्य पदार्थ आपकी जठराग्नि को बिगाड़ते हैं और त्रिदोष असंतुलन, आलस्य व रोग उत्पन्न करते हैं:")

        for item in diet_res.get("unfavorable_foods", []):
            st.markdown(f"""
            <div style="background:#FEF2F2; border:1px solid #FCA5A5; border-left:4px solid #EF4444; border-radius:6px; padding:10px 14px; margin-bottom:8px;">
                <b style="color:#DC2626;">🚫 परहेज योग्य:</b> <span style="color:#1E293B;">{item}</span>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("#### ⚠️ चरक संहिता अनुसार विरुद्ध आहार (Incompatible Food Combinations):")
        st.markdown("""
        - 🥛 **दूध के साथ खट्टे फल या नमक:** कभी भी दूध के साथ नमक, दही, संतरा, नींबू या मछली का सेवन न करें। यह रक्तविकार एवं चर्मरोग उत्पन्न करता है।
        - 🍯 **शहद और गर्म जल/घी:** बराबर मात्रा में शहद और घी का मिश्रण विष समान है; शहद को कभी भी उबालें या गर्म न करें।
        - 🧊 **गरम भोजन के तुरंत बाद ठंडा जल:** गरम भोजन के साथ या तुरंत बाद फ्रिज का ठंडा पानी जठराग्नि को तुरंत बुझा देता है, जिससे आमाशय में 'आम' (Toxins) बनता है।
        - 🌙 **रात्रि में दही का सेवन वर्जित:** रात्रि में दही खाने से कफ स्रोत अवरुद्ध होते हैं और वात-कफ प्रकोप होता है।
        """)

    # -------------------------------------------------------------
    # TAB 4: भोजन नियम व उपवास
    # -------------------------------------------------------------
    with tab_d4:
        st.markdown("### ⏰ शास्त्रीय भोजन नियम एवं उपवास विधि")
        st.markdown(f"""
        <div style="background:#EFF6FF; border:1.5px solid #60A5FA; border-radius:10px; padding:14px; margin-bottom:14px;">
            <b style="color:#1D4ED8; font-size:16px;">🧘 आपकी कुण्डली अनुसार उपवास एवं शोधन परामर्श:</b><br/>
            <p style="margin-top:6px; color:#1E293B; font-size:14px;">{diet_res.get('fasting_remedy', '')}</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        #### 📜 चरक संहिता के ५ शाश्वत भोजन नियम:
        1. **काले भोजनम् (समय पर भोजन):** जब तीव्र भूख लगे तभी भोजन करें; बिना भूख के केवल स्वाद या आदत के लिए न खाएं।
        2. **हितभुक एवं मितभुक (हितकारी व संतुलित मात्रा):** आमाशय के २ भाग भोजन के लिए, १ भाग जल के लिए और १ भाग वायु संचरण हेतु रिक्त रखें।
        3. **अत्यधिक जल वर्जित:** भोजन के तुरंत बाद अधिक ठंडा पानी पीने से जठराग्नि बुझ जाती है; भोजन के मध्य में केवल गुनगुना पानी १-२ घूंट लें।
        4. **प्रसन्न चित्त व तन्मयता:** क्रोध, चिंता, भय, मोबाइल या टीवी देखते हुए भोजन न करें। भोजन सदैव एकाग्र व आदर भाव से करें।
        5. **सूर्यास्त के बाद हल्का भोजन:** रात्रि का भोजन सदैव सोने से कम से कम २.५ से ३ घंटे पूर्व कर लें और अत्यंत सुपाच्य रखें।
        """)
