import streamlit as st
from src.jyotish.services.shastriya_pramana import SHASTRIYA_SHLOKAS
import src.jyotish.core.lifestyle as life_mod


def render_ayurvedic_diet_view(chart, tabs=None):
    if tabs is None:
        tabs = [
            "🌿 त्रिदोष शारीरिक प्रकृति",
            "✅ अनुकूल आहार व रस",
            "❌ वर्जित आहार व परहेज",
            "⏰ भोजन नियम व उपवास"
        ]

    st.subheader("🍽️ खानपान एवं त्रिदोष आहार परामर्श (Diet & Ayurvedic Nutrition)")
    st.write("बृहत्पाराशर होराशास्त्र एवं चरक-सुश्रुत-अष्टांगहृदयम् अनुसार सक्रिय जातक की कुण्डली, ग्रह-नक्षत्र, लग्न, २य भाव (भोजन) एवं ६ठे भाव (पाचन) आधारित पूर्ण आहार परामर्श।")

    # Classical Shastriya Shloka Card
    ayur_pramana = SHASTRIYA_SHLOKAS.get("ayurveda_diet_tridosha", {})
    if ayur_pramana:
        with st.expander("📜 शास्त्रीय प्रमाण — अष्टांगहृदयम् एवं चरक संहिता (त्रिदोष एवं षड्रस सिद्धान्त)", expanded=False):
            st.markdown(f"""
            <div style="background:#FFFBEB; border-left:4px solid #D97706; padding:12px; border-radius:6px; margin-bottom:10px;">
                <b style="color:#B45309; font-size:15px;">📖 ग्रंथ संदर्भ: {ayur_pramana.get('grantha', '')}</b>
                <pre style="white-space:pre-wrap; font-family:serif; font-size:14px; color:#78350F; margin:8px 0; background:transparent; border:none; padding:0;">
{ayur_pramana.get('shloka_sanskrit', ayur_pramana.get('shloka', ''))}
                </pre>
                <div style="font-size:13px; color:#92400E; margin-top:6px;">
                    <b>हिंदी भावार्थ:</b> {ayur_pramana.get('anuvad_hi', ayur_pramana.get('hindi_translation', ''))}
                </div>
            </div>
            """, unsafe_allow_html=True)

    diet_res = life_mod.DietEngine.analyze(chart)

    # Top Status Banner - 4 Key Pillars
    c_d1, c_d2, c_d3, c_d4 = st.columns(4)
    c_d1.metric("प्राथमिक शारीरिक प्रकृति", diet_res.get("primary_dosha", "पित्त"), "लग्न तत्व आधारित")
    c_d2.metric("चंद्र नक्षत्र त्रिदोष", f"{diet_res.get('moon_nakshatra', 'अश्विनी')} (पद {diet_res.get('moon_pada', 1)})", diet_res.get("nakshatra_dosha", "सम"))
    c_d3.metric("सूर्य जठराग्नि स्थिति", diet_res.get("sun_jatharagni", "सम जठराग्नि").split(" (")[0], "चयापचय व पाचन")
    c_d4.metric("लवण (नमक) परामर्श", "सेंधा नमक (Rock Salt)", "दोष शमन")

    tab_d1, tab_d2, tab_d3, tab_d4 = st.tabs(tabs)

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

    with tab_d2:
        st.markdown("### ✅ आपके शरीर के लिए सर्वोत्तम अनुकूल खाद्य पदार्थ व षड्रस")
        st.caption("इन पदार्थों का नियमित सेवन आपके त्रिदोष को संतुलित रखेगा और ओज व रोग-प्रतिरोधक क्षमता बढ़ाएगा:")

        # Rasa pacification guide
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
