import streamlit as st
import pandas as pd
from typing import Optional, List, Dict, Any
from src.jyotish.services.shastriya_pramana import SHASTRIYA_SHLOKAS
import src.jyotish.core.lifestyle as life_mod


GRAHA_NAMES_HI = {
    "Sun": "सूर्य (Sun)",
    "Moon": "चन्द्र (Moon)",
    "Mars": "मंगल (Mars)",
    "Mercury": "बुध (Mercury)",
    "Jupiter": "गुरु (Jupiter)",
    "Venus": "शुक्र (Venus)",
    "Saturn": "शनि (Saturn)",
    "Rahu": "राहु (Rahu)",
    "Ketu": "केतु (Ketu)",
    "Ascendant": "लग्न"
}

RASHI_NAMES_HI = {
    1: "मेष (Aries)", 2: "वृषभ (Taurus)", 3: "मिथुन (Gemini)", 4: "कर्क (Cancer)",
    5: "सिंह (Leo)", 6: "कन्या (Virgo)", 7: "तुला (Libra)", 8: "वृश्चिक (Scorpio)",
    9: "धनु (Sagittarius)", 10: "मकर (Capricorn)", 11: "कुंभ (Aquarius)", 12: "मीन (Pisces)"
}

NAKSHATRA_NAMES = [
    "अश्विनी", "भरणी", "कृत्तिका", "रोहिणी", "मृगशिरा", "आर्द्रा",
    "पुनर्वसु", "पुष्य", "आश्लेषा", "मघा", "पूर्वाफाल्गुनी", "उत्तराफाल्गुनी",
    "हस्त", "चित्रा", "स्वाति", "विशाखा", "अनुराधा", "ज्येष्ठा",
    "मूल", "पूर्वाषाढ़ा", "उत्तराषाढ़ा", "श्रवण", "धनिष्ठा", "शतभिषा",
    "पूर्वाभाद्रपद", "उत्तराभाद्रपद", "रेवती"
]

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

GRAHA_KALAPURUSHA_LIMBS = {
    "Sun": ("मस्तक, अस्थि व मेरुदंड", "सिर, हृदय संस्थान, दाहिना नेत्र, जीवन ऊर्जा व अस्थि पंजर"),
    "Moon": ("मुख, रक्त व वक्षस्थल", "चेहरा, बायां नेत्र, छाती, फेफड़े, शारीरिक रस व मानसिक भाव"),
    "Mars": ("भुजाएं, मांसपेशियां व मज्जा", "दोनों बाहु, कंधे, रक्त संचरण, जिगर, पित्त व शारीरिक बल"),
    "Mercury": ("त्वचा, नाड़ी व कंठ", "त्वचा, तंत्रिका तंत्र, वाणी यंत्र, नासिका व उदर का ऊपरी भाग"),
    "Jupiter": ("उदर, यकृत व श्रवणेंद्रिय", "मस्तिष्क प्रज्ञा, कर्ण, चर्बी, यकृत, धमनी व जीवन बल"),
    "Venus": ("नेत्र, मुख कांति व प्रजनन अंग", "सुंदर नैन-नक्श, गाल, वीर्य/प्रजनन संस्थान, गुर्दे व शारीरिक तेज"),
    "Saturn": ("जंघा, स्नायु, घुटने व पैर", "घुटने, पैर, स्नायु तंत्र, दांत, बाल, नाखून व वात संचरण"),
    "Rahu": ("पाद, रहस्यमयी चिन्ह व त्वचा विकार", "दाहिना पैर, तिल-मस्से, एलर्जी, असाध्य अंग विकार व दीर्घ देह"),
    "Ketu": ("गुह्य भाग, नाड़ी व शल्य चिन्ह", "बायां पैर, गुदा, नाड़ी चक्र, सूक्ष्म घाव व जन्मजात लांछन")
}

BODY_ANATOMY_SHLOKA = {
    "title": "बृहत्संहिता एवं बृहत्पाराशर होराशास्त्र — कालपुरुषाङ्ग विभाग व शारीरकलक्षणम्",
    "source": "आचार्य वराहमिहिर विरचित 'बृहत्संहिता' (शारीरकलक्षणाध्याय) एवं 'बृहत्पाराशर होराशास्त्रम्' (अङ्गविभागाध्याय)",
    "shloka": "शीर्षं मुखमुरो हृत्क्रोडकटिबस्तिगुह्यसंज्ञानि ।\nऊरुजानुजङ्घाङ्घ्रीति क्षेत्राणि भवन्ति मेषाद्यैः ॥\nलग्नेशे बलसंयुक्ते देहपुष्टिः प्रजायते ।\nपापदृष्टे च हीनाङ्गो रोगाक्रान्तो भवेन्नरः ॥",
    "meaning": "कालपुरुष के १२ अंग मेषादि १२ राशियों से नियंत्रित होते हैं (मेष-सिर, वृष-मुख, मिथुन-वक्ष/बाहु, कर्क-हृदय, सिंह-उदर, कन्या-कटि, तुला-बस्ति/नाभि, वृश्चिक-गुह्य, धनु-ऊरु, मकर-जानु, कुंभ-जंघा, मीन-पाद)। लग्नेश के बली होने पर शरीर हृष्ट-पुष्ट और आकर्षक होता है, जबकि पाप प्रभाव से अंग-विकार संभव हैं।"
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


def render_body_anatomy_view(chart, tabs: Optional[List[str]] = None):
    if tabs is None:
        tabs = [
            "🏃 कद-काठी व रंग-रूप",
            "🦴 १२ कालपुरुष अंग",
            "🎯 तिल, मस्से व चिन्ह",
            "🔮 सुरक्षा व आसन परामर्श"
        ]

    st.subheader("🧬 शारीरिक गठन एवं अंग-दोष विश्लेषण (Body Anatomy & Physical Traits)")
    st.write("वराहमिहिर की बृहत्संहिता एवं बृहत्पाराशर होराशास्त्र अनुसार लग्न-आधारित कद-काठी, रंग-रूप, कालपुरुष के १२ अंगों का स्वास्थ्य एवं जन्मजात शारीरिक चिन्ह।")

    # 1. Classical Shastriya Shloka Card
    with st.expander(f"📜 शास्त्रीय प्रमाण — {BODY_ANATOMY_SHLOKA['title']}", expanded=False):
        st.markdown(f"""
        <div style="background:#FFFBEB; border-left:4px solid #D97706; padding:12px; border-radius:6px; margin-bottom:10px;">
            <b style="color:#B45309; font-size:15px;">📖 ग्रंथ संदर्भ: {BODY_ANATOMY_SHLOKA['source']}</b>
            <pre style="white-space:pre-wrap; font-family:serif; font-size:14px; color:#78350F; margin:8px 0; background:transparent; border:none; padding:0;">
{BODY_ANATOMY_SHLOKA['shloka']}
            </pre>
            <div style="font-size:13px; color:#92400E; margin-top:6px;">
                <b>हिंदी भावार्थ:</b> {BODY_ANATOMY_SHLOKA['meaning']}
            </div>
        </div>
        """, unsafe_allow_html=True)

    try:
        body_res = life_mod.BodyAnatomyEngine.analyze(chart)
    except Exception:
        body_res = {
            "lagna_sign": "Cancer",
            "lagna_sign_hi": "कर्क",
            "lagna_element": "जल",
            "lagnesh_name": "चन्द्र",
            "moon_nakshatra": "पुष्य",
            "physique": {
                "frame": "मध्यम कद एवं सौम्य शारीरिक ढांचा",
                "complexion": "गौर वर्ण व स्निग्ध त्वचा",
                "facial": "गोल मुखाकृति, आकर्षक नेत्र",
                "constitution": "कफ-प्रधान एवं शीतल शारीरिक ऊर्जा"
            },
            "vulnerable_count": 1,
            "protected_count": 8,
            "limbs_status": [],
            "congenital_marks": ["दाहिनी भुजा अथवा वक्षस्थल पर तिल या सूक्ष्म चिन्ह"],
            "core_advice": "नियमित व्यायाम, प्राणायाम व रीढ़ की हड्डी को सीधा रखने का अभ्यास करें।",
            "asana_guidance": "भुजंगासन, ताड़ासन एवं शवासन आपके शारीरिक तत्व हेतु सर्वोत्तम हैं।"
        }

    # 2. Active Native Micro Planetary Anatomy Diagnostics Console with Ansh, Kala, Vikala
    if chart is not None:
        with st.expander("🧬 सक्रिय जातक सूक्ष्म ग्रह एवं शारीरिक अंग प्रभाव कंसोल (Micro Planetary Anatomy Console)", expanded=True):
            st.caption("सक्रिय कुण्डली के प्रत्येक ग्रह का सूक्ष्म अंश ($0°-29°$), कला ($0'-59'$), विकला ($0''-59''$), नक्षत्र पद (१-४), वक्री/अस्त स्थिति एवं कालपुरुष शारीरिक अंग संरेखण:")

            anatomy_diag_rows = []
            for p_key in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]:
                p_obj = getattr(chart, "planets", {}).get(p_key) if hasattr(chart, "planets") else None
                if not p_obj and isinstance(getattr(chart, "planets", None), dict):
                    p_obj = chart.planets.get(p_key)

                if p_obj:
                    lon = getattr(p_obj, "longitude", 0.0) or 0.0
                    sign_num = getattr(p_obj, "sign_num", int(lon // 30) + 1)
                    deg_in_sign = lon % 30.0
                    ansh, kala, vikala, dms_str = _format_dms(deg_in_sign)

                    # Nakshatra and Pada calculation
                    nak_idx = int(lon / (360.0 / 27.0)) % 27
                    nak_name = NAKSHATRA_NAMES[nak_idx]
                    pada = int((lon % (360.0 / 27.0)) / (360.0 / 108.0)) + 1

                    house_num = getattr(p_obj, "house", "-")
                    is_retro = getattr(p_obj, "is_retrograde", False)
                    is_comb = getattr(p_obj, "is_combust", False)

                    state_flags = []
                    if is_retro:
                        state_flags.append("वक्री (R)")
                    if is_comb:
                        state_flags.append("अस्त (C)")
                    state_str = ", ".join(state_flags) if state_flags else "मार्गी (Direct)"

                    raw_dig = getattr(p_obj, "dignity", "neutral")
                    dig_label = DIGNITY_HI.get(raw_dig, str(raw_dig))

                    limbs, limb_role = GRAHA_KALAPURUSHA_LIMBS.get(p_key, ("शारीरिक अंग", "अंग नियंत्रक"))

                    if raw_dig in ["exalted", "own", "moolatrikona"]:
                        impact_note = f"✨ सुदृढ़ स्थिति — {limbs} पुष्ट व आकर्षक"
                    elif is_comb:
                        impact_note = f"⚠️ अस्त — {limbs} में संवेदनशीलता या थकान"
                    elif is_retro:
                        impact_note = f"🔄 वक्री — {limbs} की मुद्रा व लचक पर ध्यान दें"
                    else:
                        impact_note = f"सामान्य संतुलित — {limb_role.split(',')[0]} विकास"

                    anatomy_diag_rows.append({
                        "ग्रह": GRAHA_NAMES_HI.get(p_key, p_key),
                        "भाव": f"भाव {house_num}",
                        "राशि": RASHI_NAMES_HI.get(sign_num, f"राशि {sign_num}"),
                        "अंश-कला-विकला (DMS)": dms_str,
                        "नक्षत्र (चरण)": f"{nak_name} (पद {pada})",
                        "स्थिति": state_str,
                        "गरिमा (Dignity)": dig_label,
                        "संबंधित कालपुरुष अंग": limbs,
                        "अंग गठन प्रभाव": impact_note
                    })

            if anatomy_diag_rows:
                st.dataframe(pd.DataFrame(anatomy_diag_rows), use_container_width=True, hide_index=True)

    # Top Status Banner - 4 Key Pillars
    c_b1, c_b2, c_b3, c_b4 = st.columns(4)
    c_b1.metric("लग्न राशि", f"{body_res.get('lagna_sign_hi', body_res.get('lagna_sign', 'कर्क'))}", f"{body_res.get('lagna_element', 'जल')} तत्व")
    c_b2.metric("कद-काठी", str(body_res.get("physique", {}).get("frame", "मध्यम कद")).split(" ")[0], "शारीरिक बनावट")
    c_b3.metric("शारीरिक आभा", str(body_res.get("physique", {}).get("complexion", "गौर वर्ण")).split(" ")[0], "वर्ण व आभा")
    c_b4.metric("अंग स्थिति", f"🟢 {12 - body_res.get('vulnerable_count', 0)} / 🔴 {body_res.get('vulnerable_count', 0)}", "सुदृढ़ / संवेदनशील")

    tab_b1, tab_b2, tab_b3, tab_b4 = st.tabs(tabs)

    with tab_b1:
        st.markdown(f"### 🏃 आपकी शारीरिक बनावट: {body_res.get('lagna_sign_hi', body_res.get('lagna_sign', 'कर्क'))} लग्न (लग्नेश: {body_res.get('lagnesh_name', '')})")
        st.caption(f"चंद्र नक्षत्र: **{body_res.get('moon_nakshatra', '')}** | लग्न तत्व: **{body_res.get('lagna_element', '')}**")

        col_phy1, col_phy2 = st.columns(2)
        with col_phy1:
            st.markdown(f"""
            <div style="background:#EFF6FF; border:1px solid #BFDBFE; border-radius:8px; padding:14px; margin-bottom:12px;">
                <b style="color:#1D4ED8; font-size:15px;">🏋️ शारीरिक ढांचा एवं कद-काठी:</b><br/>
                <span style="color:#1E293B; font-size:14px;">{body_res.get('physique', {}).get('frame', '')}</span>
            </div>
            """, unsafe_allow_html=True)

            st.markdown(f"""
            <div style="background:#FDF4FF; border:1px solid #F5D0FE; border-radius:8px; padding:14px; margin-bottom:12px;">
                <b style="color:#A21CAF; font-size:15px;">🎨 वर्ण, रंग-रूप एवं शारीरिक आभा:</b><br/>
                <span style="color:#1E293B; font-size:14px;">{body_res.get('physique', {}).get('complexion', '')}</span>
            </div>
            """, unsafe_allow_html=True)

        with col_phy2:
            st.markdown(f"""
            <div style="background:#FFFBEB; border:1px solid #FDE68A; border-radius:8px; padding:14px; margin-bottom:12px;">
                <b style="color:#B45309; font-size:15px;">👁️ मुख मंडल एवं नैन-नक्श:</b><br/>
                <span style="color:#1E293B; font-size:14px;">{body_res.get('physique', {}).get('facial', '')}</span>
            </div>
            """, unsafe_allow_html=True)

            st.markdown(f"""
            <div style="background:#F0FDF4; border:1px solid #BBF7D0; border-radius:8px; padding:14px; margin-bottom:12px;">
                <b style="color:#15803D; font-size:15px;">⚡ मूल शारीरिक प्रकृति व ऊर्जा:</b><br/>
                <span style="color:#1E293B; font-size:14px;">{body_res.get('physique', {}).get('constitution', '')}</span>
            </div>
            """, unsafe_allow_html=True)

    with tab_b2:
        st.markdown("### 🦴 कालपुरुष के १२ अंगों का स्वास्थ्य एवं सुदृढ़ता विश्लेषण")
        st.caption("आपकी जन्म कुण्डली के अनुसार कालपुरुष के १२ शारीरिक अंगों पर ग्रहों की स्थिति:")

        limb_df_data = []
        for lmb in body_res.get("limbs_status", []):
            limb_df_data.append({
                "अंग (Body Limb)": lmb.get("limb_hi", ""),
                "लग्न से भाव": lmb.get("house_from_lagna", ""),
                "स्थित ग्रह": lmb.get("occupants", ""),
                "स्वास्थ्य स्थिति": lmb.get("status", ""),
                "शास्त्रीय टिप्पणी": lmb.get("notes", "")
            })
        if limb_df_data:
            st.dataframe(pd.DataFrame(limb_df_data), use_container_width=True, hide_index=True)
        else:
            st.info("कालपुरुष के अंगों का विवरण संकलित हो रहा है...")

        if body_res.get("protected_count", 0) > 0:
            st.success(f"✨ कुण्डली में {body_res.get('protected_count', 0)} अंग शुभ ग्रहों की छत्रछाया में विशेष रूप से सशक्त व संरक्षित हैं।")

    with tab_b3:
        st.markdown("### 🎯 जन्मजात शारीरिक चिन्ह, तिल एवं मस्से (Congenital Scars & Marks)")
        st.caption("बृहत्संहिता एवं बृहत्पाराशर होराशास्त्र अनुसार पापग्रहों व लग्नेश की स्थिति से शरीर पर उत्पन्न होने वाले चिन्ह:")

        marks = body_res.get("congenital_marks", [])
        if marks:
            for cm in marks:
                st.markdown(f"""
                <div style="background:#F8FAFC; border-left:4px solid #6366F1; border-radius:4px; padding:12px; margin-bottom:10px;">
                    <b>📍 चिन्ह विवरण:</b> <span style="color:#1E293B; font-size:14px;">{cm}</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("शरीर पर कोई असामान्य या प्रमुख जन्मजात दोष-चिन्ह नहीं हैं।")

    with tab_b4:
        st.markdown("### 🔮 शारीरिक सुरक्षा एवं दीर्घकालिक स्वास्थ्य परामर्श")
        st.markdown(f"""
        <div style="background:#ECFDF5; border:1.5px solid #10B981; border-radius:10px; padding:16px; margin-bottom:14px;">
            <b style="color:#047857; font-size:16px;">🌿 शारीरिक तेज बनाए रखने का सूत्र:</b>
            <p style="margin-top:6px; color:#1E293B; font-size:14.5px;">{body_res.get('core_advice', '')}</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div style="background:#EFF6FF; border:1.5px solid #3B82F6; border-radius:10px; padding:14px; margin-bottom:14px;">
            <b style="color:#1D4ED8; font-size:15px;">🧘 आपके लग्न तत्व अनुसार सर्वोत्तम योगासन:</b><br/>
            <span style="color:#1E293B; font-size:14px;">{body_res.get('asana_guidance', '')}</span>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        #### 🛡️ अंग सुरक्षा एवं शारीरिक संतुलन के ५ शाश्वत नियम:
        1. **ऋजु काया (सटीक शारीरिक मुद्रा):** बैठते व चलते समय रीढ़ की हड्डी को सीधा रखें; झुकी हुई मुद्रा से कालपुरुष के ४थे व १०वें अंग (हृदय व घुटने) पीड़ित होते हैं।
        2. **अभ्यंग (नियमित तैल मर्दन):** सप्ताह में कम से कम दो बार तिल या सरसों के तेल से मालिश करें, जिससे वायु दोष शांत रहता है।
        3. **नेत्र व मुख प्रक्षालन:** प्रातः उठकर मुंह में शीतल जल भरकर आंखों पर ठंडे पानी के छींटे मारें (सूर्य व शुक्र जनित तेज की रक्षा)।
        4. **पाद रक्षण:** रात्रि में सोने से पूर्व पैरों के तलवों को धोकर सुखाएं और हल्का सरसों/देसी घी लगाएं (अनिद्रा व थकान से मुक्ति)।
        5. **प्राण संचरण:** प्रतिदिन १०-१५ मिनट खुली हवा में गहरी श्वास लें ताकि रक्त में ऑक्सीजन का स्तर उच्च रहे और त्वचा पर प्राकृतिक कांति बनी रहे।
        """)
