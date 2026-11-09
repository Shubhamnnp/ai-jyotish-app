import streamlit as st
from src.jyotish.services.shastriya_pramana import SHASTRIYA_SHLOKAS
import src.jyotish.core.ishta_devata as ishta_mod


def render_pooja_view(chart, tabs=None):
    if tabs is None:
        tabs = [
            "🕉️ इष्टदेवता व मोक्ष",
            "📿 कुलदेवता व मन्त्र साधना",
            "🪔 नित्य पूजा विधान",
            "📅 व्रत व उपवास नियम",
            "🚩 नवरात्रि ९ दिवसीय विधान"
        ]

    st.subheader("🕉️ इष्टदेवता, धर्मदेवता, नित्य पूजा विधान एवं व्रत निर्णय")
    st.write("महर्षि जैमिनी उपदेश सूत्र एवं बृहत्पाराशर होराशास्त्र अनुसार आत्मकारक (AK), कारकांश (D9) के १२वें भाव (मोक्ष भाव), ५वें भाव (मंत्र सिद्धि), धर्मदेवता, कुलदेवी/कुलदेवता, नित्य पूजा विधि, जप माला एवं पावन व्रत निर्णय।")

    # Classical Shastriya Shloka Card
    ishta_pramana = SHASTRIYA_SHLOKAS.get("jaimini_ishta_moksha", {})
    if ishta_pramana:
        with st.expander("📜 शास्त्रीय प्रमाण — महर्षि जैमिनी उपदेश सूत्राणि एवं बृहत्पाराशर होराशास्त्र (कारकांश द्वादश भाव एवं इष्ट निर्णय)", expanded=False):
            st.markdown(f"""
            <div style="background:#FFFBEB; border-left:4px solid #D97706; padding:12px; border-radius:6px; margin-bottom:10px;">
                <b style="color:#B45309; font-size:15px;">📖 ग्रंथ संदर्भ: {ishta_pramana.get('grantha', '')}</b>
                <pre style="white-space:pre-wrap; font-family:serif; font-size:14px; color:#78350F; margin:8px 0; background:transparent; border:none; padding:0;">
{ishta_pramana.get('shloka_sanskrit', ishta_pramana.get('shloka', ''))}
                </pre>
                <div style="font-size:13px; color:#92400E; margin-top:6px;">
                    <b>हिंदी भावार्थ:</b> {ishta_pramana.get('anuvad_hi', ishta_pramana.get('hindi_translation', ''))}
                </div>
            </div>
            """, unsafe_allow_html=True)

    ishta_res = ishta_mod.IshtaDevataEngine.analyze(chart)

    # Top Status Banner - 4 Key Spiritual Pillars
    c_i1, c_i2, c_i3, c_i4 = st.columns(4)
    c_i1.metric("प्रधान इष्टदेवता", ishta_res["ishta_deity"].split(" / ")[0], f"ग्रह: {ishta_res['ishta_planet']}")
    c_i2.metric("कारकांश लग्न (D9)", ishta_res["karakamsha_sign"], f"आत्मकारक: {ishta_res['atmakaraka']}")
    c_i3.metric("जप माला", ishta_res["ishta_mala"].split(" ")[0], "मंत्र सिद्धि")
    c_i4.metric("पावन व्रत दिवस", ishta_res["ishta_vrat_day"].split(" ")[0], ishta_res["ishta_vrat_tithi"].split(" ")[0])

    tab_i1, tab_i2, tab_i3, tab_i4, tab_i5 = st.tabs(tabs)

    with tab_i1:
        st.markdown(f"### 🕉️ आपके प्रधान इष्टदेवता: {ishta_res['ishta_deity']}")

        st.markdown(f"""
        <div style="background:#FFFBEB; border:1.5px solid #F59E0B; border-radius:10px; padding:16px; margin-bottom:14px; box-shadow:0 2px 8px rgba(0,0,0,0.04);">
            <div style="font-size:16px; font-weight:900; color:#B45309; margin-bottom:6px;">
                📜 शास्त्रीय जैमिनी कारकांश निर्णय (Shastriya Proof):
            </div>
            <p style="margin:4px 0; color:#1E293B; line-height:1.6; font-size:14px;">
                <b>१. आत्मकारक (Atmakaraka):</b> आपकी कुण्डली में <b>{ishta_res['atmakaraka']}</b> आत्मकारक हैं, जो आत्मा के पूर्वजन्म संचित संस्कारों के अधिपति हैं।<br/>
                <b>२. कारकांश राशि (Navamsha):</b> नवांश (D9) कुण्डली में आत्मकारक <b>{ishta_res['karakamsha_sign']}</b> राशि में स्थित हैं।<br/>
                <b>३. मोक्ष भाव (१२वां भाव):</b> कारकांश से १२वें भाव ({ishta_res['h12_sign']}) का स्वामी ग्रह <b>{ishta_res['h12_lord']}</b> है। {ishta_res['ishta_reason']}
            </p>
            <div style="background:#FFFFFF; border:1px solid #FCD34D; border-radius:6px; padding:10px; margin-top:8px;">
                <b style="color:#78350F;">✨ इष्टदेव स्वरूप एवं ध्यान:</b> {ishta_res['ishta_form']}<br/>
                <span style="color:#15803D;"><b>आध्यात्मिक फल:</b> {ishta_res['ishta_fruit']}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("#### 📿 सिद्ध इष्ट मंत्र:")
        st.code(ishta_res["ishta_mantra"], language="text")
        st.caption(f"**बीज मंत्र:** `{ishta_res['ishta_beej']}` | नित्य १०८ बार जप करने से आत्मिक शांति, संकट-निवारण व रक्षा प्राप्त होती है।")

    with tab_i2:
        st.markdown("### 📿 कुलदेवता, पालनकर्ता देवता, धर्मदेवता एवं मंत्र-साधना")
        st.caption("सनातन जैमिनी उपदेश सूत्र एवं पाराशरी परंपरा में इष्टदेव के साथ पालनकर्ता, धर्मदेवता व कुलदेवता की चतुर्दिक आराधना का विधान:")

        col_d1, col_d2, col_d3, col_d4 = st.columns(4)
        with col_d1:
            st.markdown(f"""
            <div style="background:#F0FDF4; border:1.5px solid #22C55E; border-radius:10px; padding:14px; height:100%;">
                <b style="color:#15803D; font-size:15px;">🌾 पालनकर्ता देवता (Palana Karta):</b><br/>
                <small style="color:#64748B;">(कारकांश से ६ठा भाव — {ishta_res.get('palana_sign', '')})</small>
                <p style="margin:8px 0; font-weight:800; color:#0F172A;">{ishta_res.get('palana_deity', 'भगवान विष्णु')}</p>
                <small style="color:#334155;">जैमिनी सूत्र अनुसार यह देव जीवन में आजीविका, भरण-पोषण, स्वास्थ्य-रक्षा एवं विपत्ति में सम्पोषण करते हैं।</small>
            </div>
            """, unsafe_allow_html=True)

        with col_d2:
            st.markdown(f"""
            <div style="background:#EFF6FF; border:1.5px solid #3B82F6; border-radius:10px; padding:14px; height:100%;">
                <b style="color:#1E40AF; font-size:15px;">🛡️ धर्मदेवता (Dharma Devata):</b><br/>
                <small style="color:#64748B;">(कारकांश से ९वां भाव)</small>
                <p style="margin:8px 0; font-weight:800; color:#0F172A;">{ishta_res['dharma_deity']}</p>
                <small style="color:#334155;">यह देव आपके धर्म, सदाचार एवं भाग्य के रक्षक हैं। इनकी कृपा से संकटों में सही दिशा व मार्गदर्शन मिलता है।</small>
            </div>
            """, unsafe_allow_html=True)

        with col_d3:
            st.markdown(f"""
            <div style="background:#FAF5FF; border:1.5px solid #A855F7; border-radius:10px; padding:14px; height:100%;">
                <b style="color:#7E22CE; font-size:15px;">⚡ मंत्र देवता (Mantra Devata):</b><br/>
                <small style="color:#64748B;">(लग्न से ५वां भाव — पूर्वपुण्य)</small>
                <p style="margin:8px 0; font-weight:800; color:#0F172A;">{ishta_res['mantra_deity']}</p>
                <small style="color:#334155;">इस देव के मंत्र का अनुष्ठान करने से सबसे तीव्र मंत्र-सिद्धि, पूर्वपुण्य जागृति एवं मेधा शक्ति प्राप्त होती है।</small>
            </div>
            """, unsafe_allow_html=True)

        with col_d4:
            st.markdown(f"""
            <div style="background:#FDF2F8; border:1.5px solid #EC4899; border-radius:10px; padding:14px; height:100%;">
                <b style="color:#BE185D; font-size:15px;">🏛️ कुलदेवता / कुलदेवी (Kula Devata):</b><br/>
                <small style="color:#64748B;">(कुटुम्ब भाव — द्वितीय भाव)</small>
                <p style="margin:8px 0; font-weight:800; color:#0F172A;">{ishta_res['kula_deity']}</p>
                <small style="color:#334155;">वंश परंपरा, कुल की रक्षा एवं संतान वृद्धि हेतु नित्य कुलदेवी/देवता का स्मरण अनिवार्य है।</small>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("#### 🌾 पालनकर्ता देवता सम्पोषण मंत्र:")
        st.code(ishta_res.get("palana_mantra", "ॐ नमो भगवते वासुदेवाय"), language="text")
        st.caption("दैनिक आजीविका, रोजगार में स्थिरता एवं आर्थिक पोषण हेतु इस मंत्र का नित्य ११ बार स्मरण करें।")

    with tab_i3:
        st.markdown("### 🪔 नित्य पूजा-उपासना, दीपक एवं पूजन सामग्री विधान")
        st.caption("आपकी कुण्डली के ग्रहों व इष्टदेवता के अनुसार अनुकूलतम पूजन विधि:")

        c_p1, c_p2 = st.columns(2)
        with c_p1:
            st.markdown(f"""
            <div style="background:#F0FDF4; border:1px solid #86EFAC; border-radius:8px; padding:14px; margin-bottom:12px;">
                <b style="color:#15803D; font-size:15px;">🪔 दीपक एवं धूप विधान:</b>
                <p style="margin:6px 0;">• <b>दीपक का तेल/घी:</b> <b>{ishta_res['ishta_deepa']}</b></p>
                <p style="margin:6px 0;">• <b>धूप / सुगंध:</b> {ishta_res['ishta_dhoop']}</p>
                <p style="margin:6px 0;">• <b>पूजा का मुख (दिशा):</b> <b>{ishta_res['ishta_direction']}</b> की ओर मुख करके बैठें।</p>
            </div>
            """, unsafe_allow_html=True)

            st.markdown(f"""
            <div style="background:#FFFBEB; border:1px solid #FDE68A; border-radius:8px; padding:14px; margin-bottom:12px;">
                <b style="color:#B45309; font-size:15px;">🌸 प्रिय पुष्प एवं माला:</b>
                <p style="margin:6px 0;">• <b>पुष्प अर्पण:</b> {ishta_res['ishta_flowers']}</p>
                <p style="margin:6px 0;">• <b>जप माला:</b> <b>{ishta_res['ishta_mala']}</b> से मंत्र जप करें।</p>
            </div>
            """, unsafe_allow_html=True)

        with c_p2:
            st.markdown(f"""
            <div style="background:#EFF6FF; border:1px solid #BFDBFE; border-radius:8px; padding:14px; margin-bottom:12px;">
                <b style="color:#1D4ED8; font-size:15px;">🍯 प्रिय नैवेद्य (प्रसाद / भोग):</b>
                <p style="margin:6px 0;">• <b>भोग:</b> {ishta_res['ishta_naivedya']}</p>
                <p style="margin:6px 0;">• <b>पवित्रता:</b> भोग अर्पित करने के बाद प्रसाद रूप में परिवार सहित ग्रहण करें।</p>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("""
            <div style="background:#FAF5FF; border:1px solid #E9D5FF; border-radius:8px; padding:14px; margin-bottom:12px;">
                <b style="color:#7E22CE; font-size:15px;">📜 नित्य पूजा का दैनिक क्रम:</b>
                <p style="margin:4px 0;">१. आचमन एवं पवित्रीकरण ➔ २. दीपक प्रज्वलन ➔ ३. गणेश वंदना ➔ ४. कुलदेवता व गुरु स्मरण ➔ ५. इष्टदेव स्तुति व १०८ जप ➔ ६. आरती व समर्पण।</p>
            </div>
            """, unsafe_allow_html=True)

    with tab_i4:
        st.markdown("### 📅 अनुकूल सामान्य व्रत, उपवास एवं पारण नियम")
        st.caption("धर्म सिंधु एवं निर्णय सिंधु अनुसार आपकी जन्म कुण्डली के लिए सर्वाधिक कल्याणकारी साप्ताहिक व मासिक व्रत:")

        st.markdown(f"""
        <div style="background:#FEF3C7; border:1.5px solid #D97706; border-radius:10px; padding:16px; margin-bottom:14px;">
            <div style="font-size:16px; font-weight:900; color:#78350F; margin-bottom:6px;">
                🌟 आपका मुख्य साप्ताहिक व्रत दिवस: <b>{ishta_res['ishta_vrat_day']}</b>
            </div>
            <p style="margin:6px 0;">• <b>मुख्य पावन तिथियाँ:</b> {ishta_res['ishta_vrat_tithi']}</p>
            <p style="margin:6px 0;">• <b>उपवास के शास्त्रीय नियम:</b> {ishta_res['ishta_vrat_rules']}</p>
            <p style="margin:6px 0; color:#92400E;">• <b>आध्यात्मिक व सांसारिक फल:</b> {ishta_res['ishta_fruit']}</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        #### 📜 उपवास एवं पारण के शाश्वत नियम:
        1. **संकल्प:** प्रातः स्नान के उपरांत पूर्व या उत्तर मुख होकर हाथ में जल, अक्षत व पुष्प लेकर व्रत का संकल्प लें।
        2. **इन्द्रिय संयम:** उपवास के दिन क्रोध, झूठ, निंदा, परनिंदा, दिन में सोना एवं तामसिक संगति सर्वथा वर्जित है।
        3. **पारण समय:** सायंकाल पूजा व आरती के पश्चात, अथवा अगले दिन सूर्योदय के उपरांत ही शुद्ध सात्विक भोजन से पारण करें।
        4. **दान की महिमा:** व्रत पूर्ण होने पर किसी ब्राह्मण, साधु अथवा निर्धन व्यक्ति को अपनी क्षमता अनुसार भोजन या अन्न-दान अवश्य करें।
        """)

    with tab_i5:
        st.markdown("### 🚩 नवरात्रि विशेष: कुण्डली अनुसार ९ दिवसीय पूजा, व्रत एवं संपूर्ण विधान")
        st.caption("देवी भागवत, निर्णय सिंधु, कालिका पुराण एवं चरक संहिता अनुसार आपकी कुण्डली के ग्रहों, आत्मकारक व भावों का सटीक विश्लेषण:")

        nv = ishta_res.get("navratri", {})
        if nv:
            # 1. Prominent Highlight: Optimal Navratri Fasting Tithi
            st.markdown(f"""
            <div style="background:#FFF1F2; border:2.5px solid #E11D48; border-radius:12px; padding:18px; margin-bottom:16px; box-shadow:0 4px 14px rgba(225,29,72,0.12);">
                <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; margin-bottom:10px;">
                    <span style="font-size:19px; font-weight:900; color:#9F1239;">🎯 सक्रिय जातक कुण्डली अनुसार नवरात्रि की सर्वोत्तम व्रत तिथि</span>
                    <span style="background:#FFE4E6; color:#BE123C; padding:5px 12px; border-radius:20px; font-size:13.5px; font-weight:800;">{nv.get('element')}</span>
                </div>
                <div style="background:#FFFFFF; border:1.5px solid #FDA4AF; border-radius:8px; padding:12px; margin-bottom:10px;">
                    <b style="color:#BE123C; font-size:16px;">🌟 अनुशंसित सर्वोत्तम व्रत तिथि:</b> <span style="color:#0F172A; font-size:16px; font-weight:800;">{nv.get('optimal_fasting_tithi', 'महाअष्टमी')}</span>
                    <p style="margin:8px 0 0 0; color:#334155; font-size:14px; line-height:1.6;">{nv.get('optimal_fasting_tithi_reason', '')}</p>
                </div>
                <p style="margin:6px 0; color:#1E293B; font-size:14px; line-height:1.6;"><b>उपवास प्रारूप:</b> {nv.get('vrat_pattern_desc')}</p>
                <div style="background:#FFFBEB; border-left:4px solid #F59E0B; padding:8px 12px; margin-top:8px; border-radius:0 6px 6px 0;">
                    <b style="color:#B45309;">📅 सर्वोत्तम व्रत दिवस क्रम:</b> <span style="color:#0F172A; font-weight:700;">{nv.get('recommended_days')}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # 2. Fasting Mode Decisions (Nirjala, Sajala, Dugdhahar, Phalahar, Naktam)
            st.markdown("#### 🥣 उपवास के ५ शास्त्रीय भेद — निर्जला, जलाहार व फलाहार निर्णय:")

            c_v1, c_v2 = st.columns(2)
            with c_v1:
                st.markdown(f"""
                <div style="background:#F8FAFC; border:1.5px solid #CBD5E1; border-radius:10px; padding:14px; margin-bottom:12px; height:100%;">
                    <b style="color:#0F172A; font-size:15px;">💧 १. निर्जला उपवास (Nirjala Vrata):</b><br/>
                    <div style="margin:6px 0; font-weight:800; font-size:14px; color:{'#15803D' if '✅' in nv.get('nirjala_status','') else '#B91C1C'};">
                        स्थिति: {nv.get('nirjala_status')}
                    </div>
                    <p style="margin:4px 0; font-size:13px; color:#334155; line-height:1.5;">{nv.get('nirjala_note')}</p>
                    <small style="color:#64748B;"><b>शास्त्रीय नियम:</b> सूर्योदय से अगले सूर्योदय तक जल की बूंद भी ग्रहण न करना। यदि कुण्डली में पित्त या वात दोष हो तो पूर्ण ९ दिन निर्जला रखना शास्त्रों में सर्वथा निषिद्ध है। केवल महाअष्टमी को १ दिन का निर्जला संकल्प लिया जा सकता है।</small>
                </div>
                """, unsafe_allow_html=True)

            with c_v2:
                st.markdown(f"""
                <div style="background:#F0FDF4; border:1.5px solid #86EFAC; border-radius:10px; padding:14px; margin-bottom:12px; height:100%;">
                    <b style="color:#15803D; font-size:15px;">🚰 २. सजला / जलाहार उपवास (Jalahar Vrata):</b><br/>
                    <div style="margin:6px 0; font-weight:800; font-size:14px; color:#166534;">
                        मुख्य विधान: {nv.get('primary_vidhan')}
                    </div>
                    <p style="margin:4px 0; font-size:13px; color:#14532D; line-height:1.5;">{nv.get('sajala_note')}</p>
                    <small style="color:#15803D;"><b>पेय पदार्थ:</b> शुद्ध गंगाजल मिश्रित जल, ताजा नारियल पानी, नींबू-मिश्री जल तथा बिना नमक के फलों का ताजा रस। यह शरीर की शुद्धि (डिटॉक्स) एवं साधना एकाग्रता हेतु सर्वोत्तम है।</small>
                </div>
                """, unsafe_allow_html=True)

            c_v3, c_v4 = st.columns(2)
            with c_v3:
                st.markdown("""
                <div style="background:#FFFBEB; border:1.5px solid #FDE68A; border-radius:10px; padding:14px; margin-bottom:12px; height:100%;">
                    <b style="color:#B45309; font-size:15px;">🥛 ३. दुग्धाहार (पयोव्रत) एवं ४. फलाहार:</b><br/>
                    <p style="margin:4px 0; font-size:13px; color:#78350F; line-height:1.5;">
                        • <b>पयोव्रत:</b> केवल देशी गाय का ताजा दूध, मखाना व मिश्री का सेवन।<br/>
                        • <b>फलाहार:</b> ऋतु फल (सेब, केला, अनार, पपीता), सूखे मेवे (बादाम, काजू, किशमिश), कुट्टू/सिंघाड़े का आटा एवं सेंधा नमक का दिन में केवल <b>एक बार</b> सेवन।
                    </p>
                    <small style="color:#92400E;"><b>सेंधा नमक नियम:</b> नमक का सेवन केवल सूर्यास्त से पूर्व या सायंकाल आरती के बाद ही एक बार करें। बार-बार नमक युक्त भोजन करने से उपवास खंडित माना जाता है।</small>
                </div>
                """, unsafe_allow_html=True)

            with c_v4:
                st.markdown("""
                <div style="background:#FAF5FF; border:1.5px solid #E9D5FF; border-radius:10px; padding:14px; margin-bottom:12px; height:100%;">
                    <b style="color:#7E22CE; font-size:15px;">🌙 ५. एकभुक्त / नक्तव्रत (Evening Satvik Meal):</b><br/>
                    <p style="margin:4px 0; font-size:13px; color:#581C87; line-height:1.5;">
                        • <b>विधान:</b> दिनभर पूर्ण उपवास (केवल जल या फल) रखें। सायंकाल माँ भगवती की आरती व दुर्गा चालीसा/सप्तशती पाठ के उपरांत केवल <b>एक समय शुद्ध सात्विक भोजन</b> ग्रहण करें।<br/>
                        • <b>किसके लिए:</b> जो जातक नौकरी/व्यवसाय में अत्यधिक श्रम करते हैं या जिन्हें शारीरिक दुर्बलता है।
                    </p>
                    <small style="color:#6B21A8;">शास्त्रों में नक्तव्रत को भी पूर्ण तपस्या के समतुल्य फलदायी घोषित किया गया है।</small>
                </div>
                """, unsafe_allow_html=True)

            # 3. 9-Day Calendar Accordion display
            st.markdown("#### 🗓️ प्रतिपदा से नवमी — ९ दिवसीय दैनन्दिन पूजा, कुण्डली फल, मंत्र व प्रिय भोग:")
            st.caption("आपकी कुण्डली के ग्रहों, आत्मकारक व भावों के आधार पर प्रत्येक दिन का विशिष्ट विश्लेषण:")

            for day in nv.get("nine_days", []):
                priority_label = " ⭐ [आपकी कुण्डली हेतु विशेष कल्याणकारी दिन]" if day["is_priority"] else ""
                with st.expander(f"{day['tithi']} — {day['deity']} (अधिपति: {day['graha']}){priority_label}", expanded=day["is_priority"]):
                    st.markdown(f"""
                    <div style="background:#FAF5FF; border:1px solid #D8B4FE; border-radius:8px; padding:12px; margin-bottom:10px;">
                        <b style="color:#6B21A8; font-size:15px;">🌸 अधिष्ठात्री देवी: {day['deity']}</b> | <b>अधिपति ग्रह:</b> {day['graha']} | <b>चक्र:</b> {day['chakra']}
                        <p style="margin:6px 0; color:#1E293B; font-size:13.5px;"><b>कुण्डली फल व संबंध:</b> {day['kundali_context']}</p>
                        <p style="margin:4px 0; color:#0F172A; font-size:13px;"><b>उपवास स्वरूप:</b> {day['vrat_type']}</p>
                        <p style="margin:4px 0; color:#78350F; font-size:13px;"><b>प्रिय नैवेद्य (भोग):</b> {day['bhog']}</p>
                        <p style="margin:4px 0; color:#15803D; font-size:13px;"><b>दैनिक पूजन विधान:</b> {day['vidhan']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    st.code(day['mantra'], language="text")

            # 4. Ghatasthapana, Kanya Poojan & Parana Vidhan
            st.markdown("""
            <div style="background:#F1F5F9; border:1px solid #CBD5E1; border-radius:8px; padding:14px; margin-top:14px; margin-bottom:14px;">
                <b style="color:#0F172A; font-size:15px;">🏺 घटस्थापना, कन्या पूजन एवं पारण के शास्त्रीय नियम:</b>
                <p style="margin:4px 0; font-size:13px; color:#334155;">
                    • <b>कलश स्थापना दिशा:</b> घर या पूजा कक्ष के <b>ईशान कोण (North-East)</b> अथवा पूर्व दिशा में शुद्ध मिट्टी की वेदी बनाकर जौ (ज्वारे) बोएं और उस पर जल-गंगाजल पूरित तांबे या मिट्टी का कलश स्थापित करें।<br/>
                    • <b>अखण्ड ज्योति विधान:</b> यदि घी का दीपक जलाएं तो वह देवी प्रतिमा के <b>दाहिनी ओर (Right Side)</b> रखें; यदि तिल के तेल का दीपक हो तो <b>बाईं ओर (Left Side)</b> रखें।<br/>
                    • <b>कन्या पूजन (Kanya Poojan):</b> अष्टमी अथवा नवमी के दिन २ वर्ष से ९ वर्ष तक की कन्याओं (कुमारिका, त्रिमूर्ति, कल्याणी, रोहिणी आदि) का पाद प्रक्षालन कर हलवा, पूरी व काले चने का भोग लगाकर दक्षिणा देकर आशीर्वाद लें।<br/>
                    • <b>पारण का शास्त्रीय समय:</b> नवमी तिथि के हवन व कन्या पूजन की समाप्ति के उपरांत अथवा दशमी तिथि के सूर्योदय पर ही व्रत का पारण करें। पारण में सर्वप्रथम माँ का चरणामृत व प्रसाद ग्रहण करें।
                </p>
            </div>
            """, unsafe_allow_html=True)
