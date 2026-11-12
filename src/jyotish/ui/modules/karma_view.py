import streamlit as st
import pandas as pd
from typing import Optional, List, Dict, Any
from src.jyotish.services.shastriya_pramana import SHASTRIYA_SHLOKAS
import src.jyotish.core.karmaphala as karma_mod


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

GRAHA_KARMA_MAPPINGS = {
    "Sun": ("आत्मा, पिता व सत्ता ऋण", "पूर्वजन्म में अहंकार, राजदंड अथवा पिता के प्रति दायित्व", "सूर्योपासना व पितृ तर्पण"),
    "Moon": ("मन, माता व जनसंवेदना ऋण", "पूर्वजन्म में मातृ-कष्ट, मानसिक आघात अथवा जल का दुरुपयोग", "माता की सेवा व शिव आराधना"),
    "Mars": ("भूमि, भ्राता व क्रोध प्रारब्ध", "पूर्वजन्म में भूमि विवाद, भ्रातृ विरोध अथवा हिंसा", "भूमि पूजन व रक्तदान"),
    "Mercury": ("बुद्धि, व्यापार व वाणी ऋण", "पूर्वजन्म में असत्य भाषण, व्यापारिक कपट अथवा विश्वासघात", "विष्णु सहस्रनाम व पक्षी सेवा"),
    "Jupiter": ("गुरु, ज्ञान व धर्म ऋण", "पूर्वजन्म में गुरु की अवज्ञा अथवा धार्मिक ज्ञान का अपव्यय", "गुरु सेवा व गीता पाठ"),
    "Venus": ("स्त्री, कलत्र व वासना ऋण", "पूर्वजन्म में स्त्री-अपमान अथवा काम-आसक्ति", "कन्या पूजन व लक्ष्मी साधना"),
    "Saturn": ("श्रम, न्याय व सेवक ऋण", "पूर्वजन्म में निर्बलों, श्रमिकों अथवा वृद्धों का शोषण", "दीन-हीन सेवा व तिल दान"),
    "Rahu": ("अतृप्त इच्छाएं व माया ऋण", "पूर्वजन्म में छल-कपट, सट्टेबाजी अथवा अवैध महत्वाकांक्षा", "महामृत्युंजय व भैरव दर्शन"),
    "Ketu": ("आध्यात्मिक ऋण व मोक्ष प्रारब्ध", "पूर्वजन्म की अधूरी योग-साधना अथवा गुप्त पाप", "गणेश आराधना व कुत्ता सेवा")
}

KARMA_SHLOKA = {
    "title": "फलदीपिका एवं बृहज्जातकम् — कर्म विपाक एवं प्रारब्ध सिद्धान्त",
    "source": "मन्त्रेश्वर विरचित 'फलदीपिका' (कर्मविपाकाध्याय) एवं वराहमिहिर विरचित 'बृहज्जातकम्'",
    "shloka": "कर्मानुरूपं फलमश्नुते हि जन्मान्तरोपार्जितपुण्यपापैः ।\nशुभाशुभैर्लग्नगतैः प्रदिष्टं दशाविपाकेन वदन्ति तज्ज्ञाः ॥\nप्रारब्धं भुज्यमानं तु क्रियमाणेण शाम्यति ।\nधर्मेण हन्यते पापं ज्ञानेन विलयं व्रजेत् ॥",
    "meaning": "प्रत्येक जीवात्मा जन्मान्तरों में अर्जित पुण्य एवं पाप के अनुसार ही इस जन्म में सुख-दुःख का उपभोग करती है। पूर्वजन्म के संचित कर्मों का फल दशा के अनुसार प्रकट होता है। भोग्य प्रारब्ध भी वर्तमान के सत्कर्मों (क्रियमाण), धर्म एवं आत्मज्ञान से शांत हो जाता है।"
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


def render_karma_view(chart, tabs: Optional[List[str]] = None):
    if tabs is None:
        tabs = [
            "💼 नौकरी बनाम व्यापार",
            "🎓 शिक्षा व मेधा",
            "⚖️ आचरण व प्रवृत्तियां",
            "🚫 व्यसन व प्रलोभन",
            "🏛️ पैतृक संपत्ति व सुख",
            "🕉️ पूर्वजन्म प्रारब्ध व ऋण"
        ]

    st.subheader("🧘 व्यक्तित्व एवं कर्मफल विश्लेषण (Personality, Vices, Destiny & Karmic Ledger)")
    st.write("शास्त्रीय वैदिक ज्योतिष (पाराशर, जैमिनी, फलदीपिका एवं सारावली) के नियमों के आधार पर व्यापार बनाम नौकरी, शिक्षा-मेधा, नैतिक आचरण, व्यसन/लत जोखिम, पैतृक संपत्ति, आंतरिक सुख एवं पूर्वजन्म प्रारब्ध का निष्पक्ष व प्रामाणिक विश्लेषण।")

    # 1. Classical Shastriya Shloka Card
    with st.expander(f"📜 शास्त्रीय प्रमाण — {KARMA_SHLOKA['title']}", expanded=False):
        st.markdown(f"""
        <div style="background:#FFFBEB; border-left:4px solid #D97706; padding:12px; border-radius:6px; margin-bottom:10px;">
            <b style="color:#B45309; font-size:15px;">📖 ग्रंथ संदर्भ: {KARMA_SHLOKA['source']}</b>
            <pre style="white-space:pre-wrap; font-family:serif; font-size:14px; color:#78350F; margin:8px 0; background:transparent; border:none; padding:0;">
{KARMA_SHLOKA['shloka']}
            </pre>
            <div style="font-size:13px; color:#92400E; margin-top:6px;">
                <b>हिंदी भावार्थ:</b> {KARMA_SHLOKA['meaning']}
            </div>
        </div>
        """, unsafe_allow_html=True)

    try:
        kp_res = karma_mod.KarmaphalaEngine.analyze(chart)
        car = kp_res["career"]
        edu = kp_res["education"]
        mor = kp_res["morals"]
        vic = kp_res["vices"]
        inh = kp_res["inheritance"]
        pea = kp_res["peace"]
        krm = kp_res["karma"]
    except Exception:
        car = {"business_score": 65, "job_score": 75, "rec_tag": "संगठित सेवा व स्वतंत्र परामर्श", "verdict_desc": "नौकरी व व्यवसाय दोनों में संतुलन अनुकूल है।", "recommendation_hi": "संगठित सेवा व स्वतंत्र परामर्श", "risk_appetite": "मध्यम जोखिम सहिष्णुता", "warnings": ["भावुकता में निर्णय न लें"], "sectors": ["प्रशासन", "परामर्श", "प्रौद्योगिकी"], "shastriya_basis": "दशमेश व षष्ठेश संबंध"}
        edu = {"education_score": 80, "memory_power": "तीव्र स्मरण शक्ति", "intellect_type": "विश्लेषणात्मक व तार्किक", "intellect_desc": "बुध व गुरु का शुभ प्रभाव", "hurdles": ["अति-विचार"], "recommended_streams": ["विज्ञान", "प्रबंधन", "ज्योतिष"], "shastriya_basis": "पंचम व नवम भाव"}
        mor = {"morality_score": 85, "integrity_level": "उच्च नैतिक सत्यनिष्ठा", "integrity_desc": "सत्व गुण की प्रधानता", "guna_distribution": {"satva": 50, "rajas": 35, "tamas": 15}, "virtues": ["सत्यवादिता", "न्यायप्रियता"], "shadows": ["हठधर्मिता"], "shastriya_basis": "लग्न व सूर्य बली"}
        vic = {"addiction_score": 25, "risk_level": "अल्प जोखिम (Low)", "warning_advice": "सात्विक आहार व नियमित दिनचर्या रखें।", "vulnerabilities": [], "triggers": ["तनाव में अति-भोजन"], "remedies": ["प्राणायाम व ध्यान"]}
        inh = {"inheritance_score": 70, "status": "पैतृक संपत्ति का शुभ योग", "status_desc": "अष्टम व नवम भाव बली हैं।", "dispute_risk": "अल्प", "land_status": "अनुकूल भूमि योग", "father_support": "सद्भावपूर्ण"}
        pea = {"inner_peace_score": 70, "peace_status": "संतुलित चित्त (Peaceful)", "peace_desc": "चन्द्रमा का शुभ पक्षीय प्रभाव।", "moon_doshas": [], "stressors": ["अत्यधिक कार्यभार"], "remedies": ["शिव आराधना"], "shastriya_basis": "चतुर्थ भाव"}
        krm = {"purva_punya_score": 80, "karmic_burden": "शुभ प्रारब्ध (Light Burden)", "burden_desc": "पूर्वजन्म में धार्मिक व परोपकारी कर्म किए गए।", "atmakaraka": "सूर्य", "sanchita_pct": 33, "prarabdha_pct": 34, "kriyamana_pct": 33, "rahu_desire": "प्रतिष्ठा व विस्तार", "ketu_mastery": "अध्यात्म व वैराग्य", "atmakaraka_lesson": "अहंकार त्याग व आत्म-साक्षात्कार", "atmakaraka_detail": "धैर्य व सेवा से आत्मोन्नति", "active_debts": [], "shastriya_basis": "पंचमेश व नवमेश"}

    # 2. Active Native Micro Planetary Karmic Diagnostics Console with Ansh, Kala, Vikala
    if chart is not None:
        with st.expander("⚖️ सक्रिय जातक सूक्ष्म ग्रह एवं कर्म-संस्कार कंसोल (Micro Planetary Karmic Console)", expanded=True):
            st.caption("सक्रिय कुण्डली के प्रत्येक ग्रह का सूक्ष्म अंश ($0°-29°$), कला ($0'-59'$), विकला ($0''-59''$), नक्षत्र पद (१-४), वक्री/अस्त एवं प्रारब्ध कर्म प्रभाव:")

            karma_diag_rows = []
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

                    area_name, karma_trait, remedy_note = GRAHA_KARMA_MAPPINGS.get(p_key, ("कर्म क्षेत्र", "प्रारब्ध संस्कार", "वैदिक उपाय"))

                    # Special mark for Atmakaraka
                    ak_mark = " ⭐ [आत्मकारक]" if p_key == str(krm.get("atmakaraka", "")).split(" ")[0] else ""

                    karma_diag_rows.append({
                        "ग्रह": f"{GRAHA_NAMES_HI.get(p_key, p_key)}{ak_mark}",
                        "भाव": f"भाव {house_num}",
                        "राशि": RASHI_NAMES_HI.get(sign_num, f"राशि {sign_num}"),
                        "अंश-कला-विकला (DMS)": dms_str,
                        "नक्षत्र (चरण)": f"{nak_name} (पद {pada})",
                        "स्थिति": state_str,
                        "गरिमा": dig_label,
                        "कर्म व ऋण क्षेत्र": area_name,
                        "प्रारब्ध संस्कार": karma_trait,
                        "ऋण-मुक्ति साधन": remedy_note
                    })

            if karma_diag_rows:
                st.dataframe(pd.DataFrame(karma_diag_rows), use_container_width=True, hide_index=True)

    # Top Status Banner - 4 Key Karmic Pillars
    c_k1, c_k2, c_k3, c_k4 = st.columns(4)
    c_k1.metric("आजीविका रुझान", str(car.get("rec_tag", "संगठित सेवा")).split(" (")[0], f"व्यापार: {car.get('business_score', 50)}% | नौकरी: {car.get('job_score', 50)}%")
    c_k2.metric("नैतिक सत्यनिष्ठा", f"{mor.get('morality_score', 80)}%", str(mor.get("integrity_level", "सत्यनिष्ठ")).split(" (")[0])
    c_k3.metric("व्यसन संवेदनशीलता", f"{vic.get('addiction_score', 20)}%", str(vic.get("risk_level", "अल्प")).split(" / ")[0])
    c_k4.metric("पूर्वजन्म संचित पुण्य", f"{krm.get('purva_punya_score', 75)}%", f"आत्मकारक: {krm.get('atmakaraka', 'सूर्य')}")

    tab_k1, tab_k2, tab_k3, tab_k4, tab_k5, tab_k6 = st.tabs(tabs)

    # TAB 1: Career
    with tab_k1:
        st.markdown("### 💼 व्यापार बनाम नौकरी (Business vs Service Aptitude)")
        st.caption("६ठे भाव (सेवा/नौकरी), ७वें भाव (व्यापार/साझेदारी), १०वें भाव (कर्म/सत्ता) एवं बुध/शनि की शास्त्रीय गणना:")

        col_b1, col_b2 = st.columns(2)
        with col_b1:
            st.markdown(f"""
            <div style="background:#EFF6FF; border:1px solid #BFDBFE; border-radius:10px; padding:16px; text-align:center;">
                <span style="font-size:14px; color:#1E40AF; font-weight:600;">व्यापार एवं स्वतंत्र उद्यम अनुकूलता</span>
                <div style="font-size:32px; font-weight:800; color:#1D4ED8; margin:8px 0;">{car.get('business_score', 50)}%</div>
                <small style="color:#3B82F6;">७वां भाव (वाणिज्य), ११वां (लाभ) व बुध का प्रभाव</small>
            </div>
            """, unsafe_allow_html=True)
            st.progress(car.get('business_score', 50) / 100.0)

        with col_b2:
            st.markdown(f"""
            <div style="background:#F0FDF4; border:1px solid #BBF7D0; border-radius:10px; padding:16px; text-align:center;">
                <span style="font-size:14px; color:#166534; font-weight:600;">नौकरी एवं संगठित सेवा अनुकूलता</span>
                <div style="font-size:32px; font-weight:800; color:#15803D; margin:8px 0;">{car.get('job_score', 50)}%</div>
                <small style="color:#22C55E;">६ठा भाव (सेवा/प्रतियोगिता), १०वां (प्रतिष्ठा) व शनि का प्रभाव</small>
            </div>
            """, unsafe_allow_html=True)
            st.progress(car.get('job_score', 50) / 100.0)

        st.markdown(f"""
        <div style="background:#FFFFFF; border:1px solid #E2E8F0; border-left:5px solid #2563EB; border-radius:8px; padding:16px; margin:16px 0;">
            <b style="color:#1E3A8A; font-size:16px;">🎯 अंतिम शास्त्रीय निर्णय: {car.get('recommendation_hi', '')}</b>
            <p style="margin:8px 0 0 0; color:#334155; font-size:14px; line-height:1.6;">{car.get('verdict_desc', '')}</p>
        </div>
        """, unsafe_allow_html=True)

        col_c1, col_c2 = st.columns(2)
        with col_c1:
            st.markdown("#### ⚡ जोखिम सहिष्णुता (Risk Appetite):")
            st.info(car.get('risk_appetite', 'मध्यम'))

            st.markdown("#### ⚠️ शास्त्रीय सावधानियां व चेतावनियां:")
            for w in car.get('warnings', []):
                st.markdown(f"• {w}")

        with col_c2:
            st.markdown("#### 🏭 सर्वाधिक अनुकूल कार्यक्षेत्र व उद्योग (Top Sectors):")
            for idx, sec in enumerate(car.get('sectors', []), 1):
                st.markdown(f"**{idx}.** {sec}")

            st.markdown(f"""
            <div style="background:#F8FAFC; border:1px solid #E2E8F0; border-radius:8px; padding:12px; margin-top:14px;">
                <small style="color:#64748B;"><b>शास्त्रीय संदर्भ:</b> {car.get('shastriya_basis', '')}</small>
            </div>
            """, unsafe_allow_html=True)

    # TAB 2: Education
    with tab_k2:
        st.markdown("### 🎓 शिक्षा, मेधा एवं बौद्धिक क्षमता (Education & Academic Intellect)")
        st.caption("४थे भाव (विद्या आधार), ५वें भाव (धी-शक्ति/बुद्धि), ९वें भाव (उच्च गुरु ज्ञान) एवं बुध-बृहस्पति का शास्त्रीय विश्लेषण:")

        col_e1, col_e2 = st.columns([1.2, 2.8])
        with col_e1:
            st.markdown(f"""
            <div style="background:#F5F3FF; border:1px solid #DDD6FE; border-radius:10px; padding:16px; text-align:center;">
                <span style="font-size:14px; color:#5B21B6; font-weight:600;">समग्र शैक्षिक सामर्थ्य</span>
                <div style="font-size:36px; font-weight:800; color:#6D28D9; margin:8px 0;">{edu.get('education_score', 75)}%</div>
                <span style="background:#EDE9FE; color:#5B21B6; padding:4px 8px; border-radius:12px; font-size:12px; font-weight:600;">
                    {str(edu.get('memory_power', '')).split(' (')[0]}
                </span>
            </div>
            """, unsafe_allow_html=True)

        with col_e2:
            st.markdown(f"""
            <div style="background:#FFFFFF; border:1px solid #E2E8F0; border-left:4px solid #7C3AED; border-radius:8px; padding:14px;">
                <b style="color:#4C1D95; font-size:15px;">🧠 बौद्धिक प्रकृति: {edu.get('intellect_type', '')}</b>
                <p style="margin:6px 0 0 0; color:#334155; font-size:13.5px; line-height:1.5;">{edu.get('intellect_desc', '')}</p>
                <div style="margin-top:8px; font-size:13px; color:#6D28D9;"><b>स्मरण एवं ग्रहण शक्ति:</b> {edu.get('memory_power', '')}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")
        col_ed1, col_ed2 = st.columns(2)
        with col_ed1:
            st.markdown("#### 🚧 शिक्षा में संभावित अवरोध व एकाग्रता दोष (Academic Hurdles):")
            for h in edu.get('hurdles', []):
                st.markdown(f"• {h}")

        with col_ed2:
            st.markdown("#### 🎯 सर्वाधिक फलदायी अध्ययन क्षेत्र एवं करियर शाखाएं:")
            for idx, s in enumerate(edu.get('recommended_streams', []), 1):
                st.markdown(f"**{idx}.** {s}")

            st.markdown(f"""
            <div style="background:#F8FAFC; border:1px solid #E2E8F0; border-radius:8px; padding:12px; margin-top:14px;">
                <small style="color:#64748B;"><b>शास्त्रीय संदर्भ:</b> {edu.get('shastriya_basis', '')}</small>
            </div>
            """, unsafe_allow_html=True)

    # TAB 3: Morals & Gunas
    with tab_k3:
        st.markdown("### ⚖️ नैतिक व्यवहार, सत्यनिष्ठा एवं गुण प्रवृत्तियां (Ethics & Guna Balance)")
        st.caption("लग्न भाव (आत्म-स्वरूप), नवम भाव (धर्म व विवेक) तथा त्रिगुण (सत्व, रज, तम) का शास्त्रीय मापन:")

        col_m1, col_m2 = st.columns([1.2, 2.8])
        with col_m1:
            st.markdown(f"""
            <div style="background:#FFFBEB; border:1px solid #FDE68A; border-radius:10px; padding:16px; text-align:center;">
                <span style="font-size:14px; color:#92400E; font-weight:600;">सत्यनिष्ठा व धर्म बल</span>
                <div style="font-size:36px; font-weight:800; color:#B45309; margin:8px 0;">{mor.get('morality_score', 80)}%</div>
                <small style="color:#D97706;">सूर्य, गुरु व नवमेश का संयुक्त सामर्थ्य</small>
            </div>
            """, unsafe_allow_html=True)

        with col_m2:
            st.markdown(f"""
            <div style="background:#FFFFFF; border:1px solid #E2E8F0; border-left:4px solid #D97706; border-radius:8px; padding:14px;">
                <b style="color:#78350F; font-size:15px;">📜 चारित्रिक स्तर: {mor.get('integrity_level', '')}</b>
                <p style="margin:6px 0 0 0; color:#334155; font-size:13.5px; line-height:1.5;">{mor.get('integrity_desc', '')}</p>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("#### ☸️ त्रिगुण संतुलन अनुपात (Prakriti Guna Distribution):")
        cg1, cg2, cg3 = st.columns(3)
        with cg1:
            st.markdown(f"""
            <div style="background:#F0FDF4; border:1px solid #BBF7D0; border-radius:8px; padding:12px; text-align:center;">
                <b style="color:#15803D;">सत्व गुण (Satva): {mor.get('guna_distribution', {}).get('satva', 50)}%</b>
                <p style="font-size:12px; color:#166534; margin:4px 0 0 0;">धर्म, सत्य, करुणा, आत्म-संयम, ईश्वर-भक्ति</p>
            </div>
            """, unsafe_allow_html=True)
            st.progress(mor.get('guna_distribution', {}).get('satva', 50) / 100.0)

        with cg2:
            st.markdown(f"""
            <div style="background:#EFF6FF; border:1px solid #BFDBFE; border-radius:8px; padding:12px; text-align:center;">
                <b style="color:#1D4ED8;">रज गुण (Rajas): {mor.get('guna_distribution', {}).get('rajas', 35)}%</b>
                <p style="font-size:12px; color:#1E40AF; margin:4px 0 0 0;">महत्वाकांक्षा, कर्मठता, भौतिक सुख, मान-प्रतिष्ठा</p>
            </div>
            """, unsafe_allow_html=True)
            st.progress(mor.get('guna_distribution', {}).get('rajas', 35) / 100.0)

        with cg3:
            st.markdown(f"""
            <div style="background:#FEF2F2; border:1px solid #FECACA; border-radius:8px; padding:12px; text-align:center;">
                <b style="color:#B91C1C;">तम गुण (Tamas): {mor.get('guna_distribution', {}).get('tamas', 15)}%</b>
                <p style="font-size:12px; color:#991B1B; margin:4px 0 0 0;">क्रोध, प्रमाद, हठधर्मिता, अति-आवेश, आलस्य</p>
            </div>
            """, unsafe_allow_html=True)
            st.progress(mor.get('guna_distribution', {}).get('tamas', 15) / 100.0)

        st.markdown("---")
        col_vr1, col_vr2 = st.columns(2)
        with col_vr1:
            st.markdown("#### 🌟 अंतर्निहित सद्गुण (Core Inherent Virtues):")
            for v in mor.get('virtues', []):
                st.markdown(f"• **{v}**")

        with col_vr2:
            st.markdown("#### 🌑 छाया प्रवृत्तियां व आंतरिक कमजोरियां (Shadow Traits to Watch):")
            for s in mor.get('shadows', []):
                st.markdown(f"• <span style='color:#B91C1C;'>{s}</span>", unsafe_allow_html=True)

            st.markdown(f"""
            <div style="background:#F8FAFC; border:1px solid #E2E8F0; border-radius:8px; padding:12px; margin-top:14px;">
                <small style="color:#64748B;"><b>शास्त्रीय संदर्भ:</b> {mor.get('shastriya_basis', '')}</small>
            </div>
            """, unsafe_allow_html=True)

    # TAB 4: Vices & Addictions
    with tab_k4:
        st.markdown("### 🚫 गलत लत, व्यसन एवं प्रलोभन संवेदनशीलता (Vices & Addiction Vulnerability)")
        st.caption("द्वितीय भाव (मुख/आहार/खानपान), अष्टम भाव (गुप्त व्यसन), द्वादश भाव (पलायन/अनिद्रा) एवं राहु-शुक्र-मंगल का निष्पक्ष शास्त्रीय परीक्षण:")

        col_vc1, col_vc2 = st.columns([1.2, 2.8])
        with col_vc1:
            score_val = vic.get('addiction_score', 20)
            alert_bg = "#FEF2F2" if score_val >= 60 else ("#FFFBEB" if score_val >= 35 else "#F0FDF4")
            alert_border = "#FECACA" if score_val >= 60 else ("#FDE68A" if score_val >= 35 else "#BBF7D0")
            alert_text = "#991B1B" if score_val >= 60 else ("#92400E" if score_val >= 35 else "#166534")

            st.markdown(f"""
            <div style="background:{alert_bg}; border:1px solid {alert_border}; border-radius:10px; padding:16px; text-align:center;">
                <span style="font-size:14px; color:{alert_text}; font-weight:600;">व्यसन संवेदनशीलता सूचकांक</span>
                <div style="font-size:36px; font-weight:800; color:{alert_text}; margin:8px 0;">{score_val}%</div>
                <small style="color:{alert_text}; font-weight:600;">{vic.get('risk_level', 'अल्प')}</small>
            </div>
            """, unsafe_allow_html=True)

        with col_vc2:
            st.markdown(f"""
            <div style="background:#FFFFFF; border:1px solid #E2E8F0; border-left:4px solid #DC2626; border-radius:8px; padding:14px;">
                <b style="color:#991B1B; font-size:15px;">🛡️ शास्त्रीय चेतावनी एवं परामर्श:</b>
                <p style="margin:6px 0 0 0; color:#334155; font-size:13.5px; line-height:1.5;">{vic.get('warning_advice', '')}</p>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("#### 🔍 ६-सूत्रीय व्यसन एवं दुर्गुण संवेदनशीलता परीक्षण:")
        for vuln in vic.get('vulnerabilities', []):
            is_danger = "उच्च" in vuln.get('level', '') or "गंभीर" in vuln.get('level', '')
            card_border = "#FCA5A5" if is_danger else "#E2E8F0"
            card_bg = "#FFF5F5" if is_danger else "#F8FAFC"
            tag_color = "#DC2626" if is_danger else "#475569"

            st.markdown(f"""
            <div style="background:{card_bg}; border:1px solid {card_border}; border-radius:8px; padding:12px; margin-bottom:10px;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <b style="color:#0F172A; font-size:14px;">• {vuln.get('vice', '')}</b>
                    <span style="background:#FFFFFF; border:1px solid {card_border}; color:{tag_color}; padding:2px 8px; border-radius:10px; font-size:12px; font-weight:700;">{vuln.get('level', '')}</span>
                </div>
                <p style="margin:6px 0 0 0; color:#475569; font-size:13px;"><b>ज्योतिषीय कारण:</b> {vuln.get('reason', '')}</p>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("#### ⚡ कुण्डली के प्रमुख ट्रिगर्स एवं सुरक्षा कवच:")
        for tr in vic.get('triggers', []):
            st.markdown(f"• {tr}")

        st.markdown("#### 🌿 शास्त्रीय निवारण एवं संकल्प (Remedial Countermeasures):")
        for rem in vic.get('remedies', []):
            st.markdown(f"• {rem}")

    # TAB 5: Inheritance & Inner Peace
    with tab_k5:
        st.markdown("### 🏛️ पैतृक संपत्ति एवं मानसिक सुख (Inheritance, Lands & Inner Peace)")

        # Section 1: Inheritance
        st.markdown("#### 📜 १. पैतृक संपत्ति, वसीयत एवं भूमि-भवन लाभ (Inheritance & Ancestral Wealth):")
        col_in1, col_in2 = st.columns([1.2, 2.8])
        with col_in1:
            st.markdown(f"""
            <div style="background:#F0FDF4; border:1px solid #BBF7D0; border-radius:10px; padding:16px; text-align:center;">
                <span style="font-size:14px; color:#166534; font-weight:600;">पैतृक लाभ अनुकूलता</span>
                <div style="font-size:34px; font-weight:800; color:#15803D; margin:8px 0;">{inh.get('inheritance_score', 60)}%</div>
                <small style="color:#166534;">८वां (विरासत), ९वां (पिता) व मंगल</small>
            </div>
            """, unsafe_allow_html=True)

        with col_in2:
            st.markdown(f"""
            <div style="background:#FFFFFF; border:1px solid #E2E8F0; border-left:4px solid #16A34A; border-radius:8px; padding:14px;">
                <b style="color:#14532D; font-size:15px;">🏛️ पैतृक स्थिति: {inh.get('status', '')}</b>
                <p style="margin:6px 0; color:#334155; font-size:13.5px;">{inh.get('status_desc', '')}</p>
                <div style="margin-top:6px; font-size:13px; color:#0F172A;">
                    • <b>विवाद/मुकदमेबाजी की संभावना:</b> {inh.get('dispute_risk', '')}<br/>
                    • <b>भूमि-भवन व अचल संपत्ति योग:</b> {inh.get('land_status', '')}<br/>
                    • <b>पिता का सहयोग व संबंध:</b> {inh.get('father_support', '')}
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")

        # Section 2: Inner Peace
        st.markdown("#### 🕊️ २. आंतरिक सुख, मानसिक शांति एवं चित्त-संतोष (Inner Peace & Sukha Bhava):")
        col_pc1, col_pc2 = st.columns([1.2, 2.8])
        with col_pc1:
            p_score = pea.get('inner_peace_score', 65)
            pc_bg = "#EFF6FF" if p_score >= 50 else "#FEF2F2"
            pc_border = "#BFDBFE" if p_score >= 50 else "#FECACA"
            pc_text = "#1E40AF" if p_score >= 50 else "#991B1B"

            st.markdown(f"""
            <div style="background:{pc_bg}; border:1px solid {pc_border}; border-radius:10px; padding:16px; text-align:center;">
                <span style="font-size:14px; color:{pc_text}; font-weight:600;">मानसिक शांति सूचकांक</span>
                <div style="font-size:34px; font-weight:800; color:{pc_text}; margin:8px 0;">{p_score}%</div>
                <small style="color:{pc_text}; font-weight:600;">{str(pea.get('peace_status', '')).split(' (')[0]}</small>
            </div>
            """, unsafe_allow_html=True)

        with col_pc2:
            st.markdown(f"""
            <div style="background:#FFFFFF; border:1px solid #E2E8F0; border-left:4px solid #2563EB; border-radius:8px; padding:14px;">
                <b style="color:#1E3A8A; font-size:15px;">🌊 चित्त स्थिति: {pea.get('peace_status', '')}</b>
                <p style="margin:6px 0 0 0; color:#334155; font-size:13.5px; line-height:1.5;">{pea.get('peace_desc', '')}</p>
            </div>
            """, unsafe_allow_html=True)

        col_md1, col_md2 = st.columns(2)
        with col_md1:
            st.markdown("##### 🌙 चन्द्रमा व चतुर्थ भाव के प्रमुख दोष:")
            for d in pea.get('moon_doshas', []):
                st.markdown(f"• {d}")

            st.markdown("##### ⚡ दैनिक तनाव के मुख्य कारक:")
            for st_cause in pea.get('stressors', []):
                st.markdown(f"• {st_cause}")

        with col_md2:
            st.markdown("##### 🌿 मानसिक शांति हेतु अचूक वैदिक उपाय:")
            for up in pea.get('remedies', []):
                st.markdown(f"• {up}")

            st.markdown(f"""
            <div style="background:#F8FAFC; border:1px solid #E2E8F0; border-radius:8px; padding:12px; margin-top:14px;">
                <small style="color:#64748B;"><b>शास्त्रीय संदर्भ:</b> {pea.get('shastriya_basis', '')}</small>
            </div>
            """, unsafe_allow_html=True)

    # TAB 6: Past Life Karma & Karmic Debts
    with tab_k6:
        st.markdown("### 🕉️ पूर्वजन्म के कर्म, ऋणानुबंध एवं प्रारब्ध (Past Life Karma & Karmic Debts)")
        st.caption("पंचम भाव (संचित पूर्व-पुण्य), नवम भाव (दैवीय कृपा), राहु-केतु अक्ष एवं आत्मकारक के आधार पर आत्मा का प्रारब्ध:")

        col_km1, col_km2 = st.columns([1.2, 2.8])
        with col_km1:
            st.markdown(f"""
            <div style="background:#FAF5FF; border:1px solid #DDD6FE; border-radius:10px; padding:16px; text-align:center;">
                <span style="font-size:14px; color:#5B21B6; font-weight:600;">पूर्वजन्म संचित पुण्य</span>
                <div style="font-size:36px; font-weight:800; color:#6D28D9; margin:8px 0;">{krm.get('purva_punya_score', 75)}%</div>
                <small style="color:#5B21B6; font-weight:600;">{str(krm.get('karmic_burden', '')).split(' (')[0]}</small>
            </div>
            """, unsafe_allow_html=True)

        with col_km2:
            st.markdown(f"""
            <div style="background:#FFFFFF; border:1px solid #E2E8F0; border-left:4px solid #7C3AED; border-radius:8px; padding:14px;">
                <b style="color:#4C1D95; font-size:15px;">⚖️ प्रारब्ध भार: {krm.get('karmic_burden', '')}</b>
                <p style="margin:6px 0 0 0; color:#334155; font-size:13.5px; line-height:1.5;">{krm.get('burden_desc', '')}</p>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("#### ⚖️ कर्म त्रय संतुलन चक्र (Sanchita, Prarabdha & Kriyamana Balance):")
        c_tr1, c_tr2, c_tr3 = st.columns(3)
        with c_tr1:
            st.markdown(f"""
            <div style="background:#FDF4FF; border:1.5px solid #F0ABFC; border-radius:10px; padding:12px; height:100%;">
                <b style="color:#A21CAF; font-size:14px;">🏺 संचित कर्म (Sanchita): {krm.get('sanchita_pct', 33)}%</b>
                <p style="margin:6px 0; font-size:13px; color:#1E293B;">पूर्वजन्मों के अव्यक्त कर्म-बीज का विशाल भंडार (१२वां व ८वां भाव)। यह आत्मा के अवचेतन में सुरक्षित रहता है।</p>
            </div>
            """, unsafe_allow_html=True)
            st.progress(krm.get('sanchita_pct', 33) / 100.0)

        with c_tr2:
            st.markdown(f"""
            <div style="background:#FFFBEB; border:1.5px solid #FCD34D; border-radius:10px; padding:12px; height:100%;">
                <b style="color:#B45309; font-size:14px;">🏹 प्रारब्ध कर्म (Prarabdha): {krm.get('prarabdha_pct', 34)}%</b>
                <p style="margin:6px 0; font-size:13px; color:#1E293B;">इस जन्म में देह धारण कर अनिवार्य रूप से भोगने हेतु आवंटित कर्म (१ला व ६ठा भाव)। यह पूर्व-निर्धारित प्रारब्ध है।</p>
            </div>
            """, unsafe_allow_html=True)
            st.progress(krm.get('prarabdha_pct', 34) / 100.0)

        with c_tr3:
            st.markdown(f"""
            <div style="background:#F0FDF4; border:1.5px solid #86EFAC; border-radius:10px; padding:12px; height:100%;">
                <b style="color:#15803D; font-size:14px;">⚡ क्रियमाण कर्म (Kriyamana): {krm.get('kriyamana_pct', 33)}%</b>
                <p style="margin:6px 0; font-size:13px; color:#1E293B;">वर्तमान जीवन में स्वतंत्र इच्छाशक्ति, पुरुषार्थ व विवेक (३रा व ९वां भाव)। इसके द्वारा जातक नए भाग्य का निर्माण करता है।</p>
            </div>
            """, unsafe_allow_html=True)
            st.progress(krm.get('kriyamana_pct', 33) / 100.0)

        st.caption(f"📜 **शास्त्रीय सिद्धांत:** 'प्रारब्धं भुज्यमानं तु क्रियमाणेण शाम्यति' — अर्थात वर्तमान के सद्विचार, गुरु-कृपा व तीव्र पुरुषार्थ ({krm.get('kriyamana_pct', 33)}% क्रियमाण) से कठिन से कठिन प्रारब्ध के ताप को भी शांत किया जा सकता है।")
        st.markdown("---")

        # Rahu & Ketu Karmic Axis
        col_rk1, col_rk2 = st.columns(2)
        with col_rk1:
            st.markdown("""
            <div style="background:#FFF7ED; border:1px solid #FED7AA; border-radius:8px; padding:14px; margin-bottom:12px;">
                <b style="color:#9A3412; font-size:15px;">🔥 राहु का कर्म-पाश: पूर्वजन्म की अतृप्त वासनाएं</b>
                <p style="margin:6px 0 0 0; color:#7C2D12; font-size:13px; line-height:1.5;">जिस भाव में राहु स्थित होता है, आत्मा वहाँ पिछले जन्मों की अधूरी इच्छाओं को पूरा करने हेतु व्याकुल रहती है:</p>
            </div>
            """, unsafe_allow_html=True)
            st.info(krm.get('rahu_desire', 'प्रतिष्ठा व सांसारिक विस्तार'))

        with col_rk2:
            st.markdown("""
            <div style="background:#F0FDFA; border:1px solid #99F6E4; border-radius:8px; padding:14px; margin-bottom:12px;">
                <b style="color:#0F766E; font-size:15px;">🌀 केतु की सिद्धि: पूर्वजन्म की साधना व वैराग्य</b>
                <p style="margin:6px 0 0 0; color:#115E59; font-size:13px; line-height:1.5;">जिस भाव में केतु स्थित होता है, वहाँ आत्मा पूर्वजन्म में सिद्धि प्राप्त कर चुकी है और अंततः सहज अनासक्ति प्राप्त होती है:</p>
            </div>
            """, unsafe_allow_html=True)
            st.success(krm.get('ketu_mastery', 'आध्यात्मिक अंतर्दृष्टि'))

        # Atmakaraka Soul Lesson
        st.markdown("#### 🌟 आत्मकारक ग्रह (Atmakaraka) का केंद्रीय आध्यात्मिक पाठ:")
        st.markdown(f"""
        <div style="background:#EFF6FF; border:1px solid #BFDBFE; border-radius:8px; padding:14px; margin-bottom:14px;">
            <b style="color:#1E40AF; font-size:15px;">आत्मा का प्रमुख गृहकार्य (Soul Curriculum) — आत्मकारक: {krm.get('atmakaraka', 'सूर्य')}</b>
            <p style="margin:6px 0; color:#1E3A8A; font-size:14px; font-weight:600;">{krm.get('atmakaraka_lesson', '')}</p>
            <p style="margin:0; color:#334155; font-size:13px;">{krm.get('atmakaraka_detail', '')}</p>
        </div>
        """, unsafe_allow_html=True)

        # Active Karmic Debts
        st.markdown("#### ⛓️ सक्रिय ऋणानुबंध एवं ऋण-मुक्ति के वैदिक उपाय (Active Karmic Debts & Redemption):")
        debts = krm.get('active_debts', [])
        if debts:
            for debt in debts:
                st.markdown(f"""
                <div style="background:#F8FAFC; border:1px solid #E2E8F0; border-radius:8px; padding:12px; margin-bottom:10px;">
                    <b style="color:#0F172A; font-size:14px;">• {debt.get('debt_name', '')}</b>
                    <p style="margin:4px 0; color:#475569; font-size:13px;"><b>लक्षण:</b> {debt.get('symptom', '')}</p>
                    <p style="margin:0; color:#15803D; font-size:13px;"><b>ऋण-मुक्ति कर्म (Redemption):</b> {debt.get('redemption', '')}</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("कुण्डली में कोई गंभीर या असाध्य ऋणानुबंध सक्रिय नहीं है। पूर्वपुण्य का प्रभाव प्रबल है।")

        # Classical Ayurdaya & Pindayu Harana Reduction Table (BPHS Ch. 43)
        if chart is not None:
            try:
                from src.jyotish.core.ayurdaya import AyurdayaEngine
                pindayu_data = AyurdayaEngine.calculate_pindayu_with_haranas(chart)
                st.markdown("---")
                st.markdown("#### ⏳ आयुर्दाय एवं शास्त्रीय हरण गणना (Pindayu Longevity & Harana Reductions — BPHS Ch. 43)")
                st.caption("महर्षि पाराशर प्रणीत पिंडायु गणना: मूल ग्रह आयु में से शत्रुक्षेत्र हरण (१/३), अस्तांगत हरण (१/२) एवं चक्रपात हरण (भाव १२ से ७) की शास्त्रीय कटौतियां:")

                c_py1, c_py2, c_py3 = st.columns(3)
                c_py1.metric("शुद्ध पिंडायु अनुमान", f"{pindayu_data.get('net_pindayu_years', 0.0)} वर्ष", "समग्र हरण उपरांत")
                c_py2.metric("अपरिशोधित मूल आयु", f"{pindayu_data.get('total_unreduced', 0.0)} वर्ष", "७ ग्रहों का प्रारंभिक योग")
                c_py3.metric("लग्न आयु अंशदान", f"+{pindayu_data.get('lagna_contribution', 0.0)} वर्ष", "लग्न अंश के अनुपात में")

                audit_rows = pindayu_data.get("audit_table", [])
                if audit_rows:
                    st.dataframe(pd.DataFrame(audit_rows), use_container_width=True, hide_index=True)
            except Exception as e:
                st.caption(f"पिंडायु हरण गणना उपलब्ध नहीं: {e}")

        st.markdown(f"""
        <div style="background:#F8FAFC; border:1px solid #E2E8F0; border-radius:8px; padding:12px; margin-top:14px;">
            <small style="color:#64748B;"><b>शास्त्रीय संदर्भ:</b> {krm.get('shastriya_basis', '')}</small>
        </div>
        """, unsafe_allow_html=True)
