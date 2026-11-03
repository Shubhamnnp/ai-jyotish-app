import streamlit as st
import importlib

def render_body_anatomy_view(chart, tabs=None):
    if tabs is None:
        tabs = [
            '🏃 कद-काठी व बनावट',
            '🎨 वर्ण एवं शारीरिक आभा',
            '🩺 कालपुरुष अंग-स्वास्थ्य',
            '✨ जन्मजात शारीरिक लक्षण'
        ]
    st.subheader("🧬 शारीरिक गठन एवं अंग-दोष विश्लेषण (Body Anatomy & Physical Traits)")
    st.write("बृहत्संहिता एवं बृहत्पाराशर होराशास्त्र अनुसार लग्न-आधारित कद-काठी, रंग-रूप, कालपुरुष के १२ अंगों का स्वास्थ्य एवं जन्मजात शारीरिक चिन्ह।")

    import importlib
    import src.jyotish.core.lifestyle as life_mod
    importlib.reload(life_mod)

    body_res = life_mod.BodyAnatomyEngine.analyze(chart)

    # Top Status Banner
    c_b1, c_b2, c_b3, c_b4 = st.columns(4)
    c_b1.metric("लग्न राशि", body_res["lagna_sign"], "शारीरिक ढांचा")
    c_b2.metric("कद-काठी", body_res["physique"]["frame"].split(" ")[0], "शारीरिक बनावट")
    c_b3.metric("शारीरिक आभा", body_res["physique"]["complexion"].split(" ")[0], "वर्ण व आभा")
    c_b4.metric("तत्व प्रधानता", body_res["physique"]["constitution"].split(" ")[0], "मूल ऊर्जा")

    tab_b1, tab_b2, tab_b3, tab_b4 = st.tabs(tabs)

    with tab_b1:
        st.markdown(f"### 🏃 आपकी शारीरिक बनावट: {body_res['lagna_sign']} लग्न")

        col_phy1, col_phy2 = st.columns(2)
        with col_phy1:
            st.markdown(f"""
            <div style="background:#EFF6FF; border:1px solid #BFDBFE; border-radius:8px; padding:14px; margin-bottom:12px;">
                <b style="color:#1D4ED8;">🏋️ शारीरिक ढांचा एवं कद-काठी:</b><br/>
                <span style="color:#1E293B;">{body_res['physique']['frame']}</span>
            </div>
            """, unsafe_allow_html=True)

            st.markdown(f"""
            <div style="background:#FDF4FF; border:1px solid #F5D0FE; border-radius:8px; padding:14px; margin-bottom:12px;">
                <b style="color:#A21CAF;">🎨 वर्ण, रंग-रूप एवं आभा:</b><br/>
                <span style="color:#1E293B;">{body_res['physique']['complexion']}</span>
            </div>
            """, unsafe_allow_html=True)

        with col_phy2:
            st.markdown(f"""
            <div style="background:#FFFBEB; border:1px solid #FDE68A; border-radius:8px; padding:14px; margin-bottom:12px;">
                <b style="color:#B45309;">👁️ मुख मंडल एवं नैन-नक्श:</b><br/>
                <span style="color:#1E293B;">{body_res['physique']['facial']}</span>
            </div>
            """, unsafe_allow_html=True)

            st.markdown(f"""
            <div style="background:#F0FDF4; border:1px solid #BBF7D0; border-radius:8px; padding:14px; margin-bottom:12px;">
                <b style="color:#15803D;">⚡ मूल शारीरिक प्रकृति:</b><br/>
                <span style="color:#1E293B;">{body_res['physique']['constitution']}</span>
            </div>
            """, unsafe_allow_html=True)

    with tab_b2:
        st.markdown("### 🦴 कालपुरुष के १२ अंगों का स्वास्थ्य एवं सुदृढ़ता विश्लेषण")
        st.caption("आपकी जन्म कुण्डली के अनुसार शरीर के विभिन्न अंगों की स्थिति:")

        limb_df_data = []
        for lmb in body_res["limbs_status"]:
            limb_df_data.append({
                "अंग (Body Limb)": lmb["limb_hi"],
                "लग्न से भाव": lmb["house_from_lagna"],
                "स्थित ग्रह": lmb["occupants"],
                "स्वास्थ्य स्थिति": lmb["status"],
                "विस्तृत टिप्पणी": lmb["notes"]
            })
        st.dataframe(pd.DataFrame(limb_df_data), use_container_width=True, hide_index=True)

    with tab_b3:
        st.markdown("### 🎯 जन्मजात शारीरिक चिन्ह, तिल एवं मस्से (Congenital Scars & Marks)")
        st.caption("बृहत्पाराशर होराशास्त्र अनुसार ग्रहों की दृष्टि व स्थिति से शरीर पर उत्पन्न होने वाले चिन्ह:")

        for cm in body_res["congenital_marks"]:
            st.markdown(f"""
            <div style="background:#F8FAFC; border-left:4px solid #6366F1; border-radius:4px; padding:12px; margin-bottom:10px;">
                <b>📍 चिन्ह विवरण:</b> <span style="color:#1E293B;">{cm}</span>
            </div>
            """, unsafe_allow_html=True)

    with tab_b4:
        st.markdown("### 🔮 शारीरिक सुरक्षा एवं दीर्घकालिक स्वास्थ्य परामर्श")
        st.markdown(f"""
        <div style="background:#ECFDF5; border:1.5px solid #10B981; border-radius:10px; padding:16px; margin-bottom:14px;">
            <b style="color:#047857; font-size:16px;">🌿 शारीरिक तेज बनाए रखने का सूत्र:</b>
            <p style="margin-top:6px; color:#1E293B;">{body_res['core_advice']}</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        #### 🧘 अंग सुरक्षा के विशेष शास्त्रीय सुझाव:
        1. **रीढ़ व गर्दन की सुरक्षा:** कार्य करते समय झुककर न बैठें; मेरुदंड को सीधा रखें।
        2. **तिल तेल मालिश (अभ्यंग):** सप्ताह में कम से कम एक बार पैरों के तलवों और सिर पर तिल के तेल की मालिश करें।
        3. **अंग-विशेष व्यायाम:** यदि किसी अंग में पापग्रह की स्थिति है (जैसे घुटनों या कमर में), तो भारी वजन उठाने से बचें और सूक्ष्म व्यायाम करें।
        """)

