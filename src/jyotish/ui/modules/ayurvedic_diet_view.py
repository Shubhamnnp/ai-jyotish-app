import streamlit as st
import importlib

def render_ayurvedic_diet_view(chart, tabs=None):
    if tabs is None:
        tabs = [
            '🥗 अनुकूल व वर्जित आहार',
            '🍵 औषधीय काढ़े व हर्ब्स',
            '⏰ दिनचर्या व भोजन समय'
        ]
    st.subheader("🍽️ खानपान एवं त्रिदोष आहार परामर्श (Diet & Ayurvedic Nutrition)")
    st.write("बृहत्पाराशर होराशास्त्र एवं चरक संहिता अनुसार त्रिदोष (वात, पित्त, कफ), द्वितीय भाव (भोजन-संस्कार), अनुकूल-प्रतिकूल खाद्य एवं उपवास निर्णय।")

    import importlib
    import src.jyotish.core.lifestyle as life_mod
    importlib.reload(life_mod)

    diet_res = life_mod.DietEngine.analyze(chart)

    # Top Status Banner
    c_d1, c_d2, c_d3, c_d4 = st.columns(4)
    c_d1.metric("प्राथमिक शारीरिक प्रकृति", diet_res["primary_dosha"], "लग्न तत्व आधारित")
    c_d2.metric("जठराग्नि स्वभाव", "प्रदीप्त एवं तीव्र" if "Pitta" in diet_res["primary_dosha"] else ("परिवर्तनशील (वात)" if "Vata" in diet_res["primary_dosha"] else "मंद (कफ)"), "पाचन शक्ति")
    c_d3.metric("अनुकूलतम पेय", "नारियल जल / सौंफ" if "Pitta" in diet_res["primary_dosha"] else ("अदरक काढ़ा" if "Vata" in diet_res["primary_dosha"] else "त्रिकटु जल / छाछ"), "दोष संतुलन")
    c_d4.metric("लवण (नमक) परामर्श", "सेंधा नमक (Rock Salt)", "स्वास्थ्य रक्षा")

    tab_d1, tab_d2, tab_d3, tab_d4 = st.tabs(tabs)

    with tab_d1:
        st.markdown(f"### 🌿 आपकी शारीरिक प्रकृति: {diet_res['dosha_title']}")
        st.info(diet_res["characteristics"])

        st.markdown("#### 🍽️ द्वितीय भाव अनुसार आपकी खान-पान शैली एवं रुचियां:")
        for note in diet_res["eating_habits"]:
            st.markdown(f"""
            <div style="background:#F8FAFC; border-left:4px solid #3B82F6; padding:10px 14px; margin-bottom:8px; border-radius:4px;">
                {note}
            </div>
            """, unsafe_allow_html=True)

        st.markdown("#### ⚠️ पाचन तंत्र एवं जठराग्नि संवेदनशीलता (६ठे भाव का प्रभाव):")
        for warn in diet_res["digestive_warnings"]:
            st.markdown(f"""
            <div style="background:#FFFBEB; border-left:4px solid #F59E0B; padding:10px 14px; margin-bottom:8px; border-radius:4px;">
                <b>सावधानी:</b> {warn}
            </div>
            """, unsafe_allow_html=True)

    with tab_d2:
        st.markdown("### ✅ आपके शरीर के लिए सर्वोत्तम अनुकूल खाद्य पदार्थ")
        st.caption("इन पदार्थों का नियमित सेवन आपके त्रिदोष को संतुलित रखेगा और ऊर्जा बढ़ाएगा:")

        for item in diet_res["favorable_foods"]:
            cat_name = item.split(":")[0] if ":" in item else "खाद्य"
            cat_items = item.split(":")[1] if ":" in item else item
            st.markdown(f"""
            <div style="background:#F0FDF4; border:1px solid #86EFAC; border-radius:8px; padding:10px 14px; margin-bottom:8px;">
                <b style="color:#15803D;">🌱 {cat_name}:</b> <span style="color:#1E293B;">{cat_items}</span>
            </div>
            """, unsafe_allow_html=True)

    with tab_d3:
        st.markdown("### ❌ प्रतिकूल खाद्य पदार्थ (जिनसे सख्त परहेज रखें)")
        st.caption("ये खाद्य पदार्थ आपकी जठराग्नि को बिगाड़ते हैं और रोग/आलस्य उत्पन्न करते हैं:")

        for item in diet_res["unfavorable_foods"]:
            st.markdown(f"""
            <div style="background:#FEF2F2; border:1px solid #FCA5A5; border-radius:8px; padding:10px 14px; margin-bottom:8px;">
                <b style="color:#DC2626;">🚫 परहेज योग्य:</b> <span style="color:#1E293B;">{item}</span>
            </div>
            """, unsafe_allow_html=True)

    with tab_d4:
        st.markdown("### ⏰ शास्त्रीय भोजन नियम एवं उपवास विधि")
        st.markdown(f"""
        <div style="background:#EFF6FF; border:1.5px solid #60A5FA; border-radius:10px; padding:14px; margin-bottom:14px;">
            <b style="color:#1D4ED8; font-size:16px;">🧘 उपवास एवं शोधन परामर्श:</b><br/>
            <p style="margin-top:6px; color:#1E293B;">{diet_res['fasting_remedy']}</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        #### 📜 चरक संहिता के ५ शाश्वत भोजन नियम:
        1. **काले भोजनम् (समय पर भोजन):** जब तीव्र भूख लगे तभी भोजन करें; बिना भूख के केवल स्वाद के लिए न खाएं।
        2. **हितभुक एवं मितभुक (हितकारी व संतुलित):** पेट के २ भाग भोजन के लिए, १ भाग जल के लिए और १ भाग वायु के लिए रिक्त रखें।
        3. **अत्यधिक जल वर्जित:** भोजन के तुरंत बाद अधिक ठंडा पानी पीने से जठराग्नि बुझ जाती है; केवल गुनगुना पानी १-२ घूंट लें।
        4. **प्रसन्न चित्त:** क्रोध, चिंता, भय या मोबाइल देखते हुए भोजन न करें। भोजन सदैव एकाग्र मन से करें।
        5. **सूर्यास्त के बाद हल्का भोजन:** रात्रि का भोजन सदैव सोने से कम से कम २.५ से ३ घंटे पूर्व कर लें।
        """)

