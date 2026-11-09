import streamlit as st
import pandas as pd
from src.jyotish.services.shastriya_pramana import SHASTRIYA_SHLOKAS
import src.jyotish.core.lifestyle as life_mod


def render_body_anatomy_view(chart, tabs=None):
    if tabs is None:
        tabs = [
            "🏃 कद-काठी व रंग-रूप",
            "🦴 १२ कालपुरुष अंग",
            "🎯 तिल, मस्से व चिन्ह",
            "🔮 सुरक्षा व आसन परामर्श"
        ]

    st.subheader("🧬 शारीरिक गठन एवं अंग-दोष विश्लेषण (Body Anatomy & Physical Traits)")
    st.write("वराहमिहिर की बृहत्संहिता एवं बृहत्पाराशर होराशास्त्र अनुसार लग्न-आधारित कद-काठी, रंग-रूप, कालपुरुष के १२ अंगों का स्वास्थ्य एवं जन्मजात शारीरिक चिन्ह।")

    # Classical Shastriya Shloka Card
    samhita_pramana = SHASTRIYA_SHLOKAS.get("brihat_samhita_sharirika_lakshana", {})
    if samhita_pramana:
        with st.expander("📜 शास्त्रीय प्रमाण — बृहत्संहिता एवं बृहत्पाराशर होराशास्त्र (शारीरकलक्षणम् एवं लाञ्छन विचार)", expanded=False):
            st.markdown(f"""
            <div style="background:#FFFBEB; border-left:4px solid #D97706; padding:12px; border-radius:6px; margin-bottom:10px;">
                <b style="color:#B45309; font-size:15px;">📖 ग्रंथ संदर्भ: {samhita_pramana.get('grantha', '')}</b>
                <pre style="white-space:pre-wrap; font-family:serif; font-size:14px; color:#78350F; margin:8px 0; background:transparent; border:none; padding:0;">
{samhita_pramana.get('shloka_sanskrit', samhita_pramana.get('shloka', ''))}
                </pre>
                <div style="font-size:13px; color:#92400E; margin-top:6px;">
                    <b>हिंदी भावार्थ:</b> {samhita_pramana.get('anuvad_hi', samhita_pramana.get('hindi_translation', ''))}
                </div>
            </div>
            """, unsafe_allow_html=True)

    body_res = life_mod.BodyAnatomyEngine.analyze(chart)

    # Top Status Banner - 4 Key Pillars
    c_b1, c_b2, c_b3, c_b4 = st.columns(4)
    c_b1.metric("लग्न राशि", f"{body_res.get('lagna_sign_hi', body_res['lagna_sign'])}", f"{body_res.get('lagna_element', '')} तत्व")
    c_b2.metric("कद-काठी", body_res["physique"]["frame"].split(" ")[0], "शारीरिक बनावट")
    c_b3.metric("शारीरिक आभा", body_res["physique"]["complexion"].split(" ")[0], "वर्ण व आभा")
    c_b4.metric("अंग स्थिति", f"🟢 {12 - body_res.get('vulnerable_count', 0)} / 🔴 {body_res.get('vulnerable_count', 0)}", "सुदृढ़ / संवेदनशील")

    tab_b1, tab_b2, tab_b3, tab_b4 = st.tabs(tabs)

    with tab_b1:
        st.markdown(f"### 🏃 आपकी शारीरिक बनावट: {body_res.get('lagna_sign_hi', body_res['lagna_sign'])} लग्न (लग्नेश: {body_res.get('lagnesh_name', '')})")
        st.caption(f"चंद्र नक्षत्र: **{body_res.get('moon_nakshatra', '')}** | लग्न तत्व: **{body_res.get('lagna_element', '')}**")

        col_phy1, col_phy2 = st.columns(2)
        with col_phy1:
            st.markdown(f"""
            <div style="background:#EFF6FF; border:1px solid #BFDBFE; border-radius:8px; padding:14px; margin-bottom:12px;">
                <b style="color:#1D4ED8; font-size:15px;">🏋️ शारीरिक ढांचा एवं कद-काठी:</b><br/>
                <span style="color:#1E293B; font-size:14px;">{body_res['physique']['frame']}</span>
            </div>
            """, unsafe_allow_html=True)

            st.markdown(f"""
            <div style="background:#FDF4FF; border:1px solid #F5D0FE; border-radius:8px; padding:14px; margin-bottom:12px;">
                <b style="color:#A21CAF; font-size:15px;">🎨 वर्ण, रंग-रूप एवं शारीरिक आभा:</b><br/>
                <span style="color:#1E293B; font-size:14px;">{body_res['physique']['complexion']}</span>
            </div>
            """, unsafe_allow_html=True)

        with col_phy2:
            st.markdown(f"""
            <div style="background:#FFFBEB; border:1px solid #FDE68A; border-radius:8px; padding:14px; margin-bottom:12px;">
                <b style="color:#B45309; font-size:15px;">👁️ मुख मंडल एवं नैन-नक्श:</b><br/>
                <span style="color:#1E293B; font-size:14px;">{body_res['physique']['facial']}</span>
            </div>
            """, unsafe_allow_html=True)

            st.markdown(f"""
            <div style="background:#F0FDF4; border:1px solid #BBF7D0; border-radius:8px; padding:14px; margin-bottom:12px;">
                <b style="color:#15803D; font-size:15px;">⚡ मूल शारीरिक प्रकृति व ऊर्जा:</b><br/>
                <span style="color:#1E293B; font-size:14px;">{body_res['physique']['constitution']}</span>
            </div>
            """, unsafe_allow_html=True)

    with tab_b2:
        st.markdown("### 🦴 कालपुरुष के १२ अंगों का स्वास्थ्य एवं सुदृढ़ता विश्लेषण")
        st.caption("आपकी जन्म कुण्डली के अनुसार कालपुरुष के १२ शारीरिक अंगों पर ग्रहों की स्थिति:")

        limb_df_data = []
        for lmb in body_res.get("limbs_status", []):
            limb_df_data.append({
                "अंग (Body Limb)": lmb["limb_hi"],
                "लग्न से भाव": lmb["house_from_lagna"],
                "स्थित ग्रह": lmb["occupants"],
                "स्वास्थ्य स्थिति": lmb["status"],
                "शास्त्रीय टिप्पणी": lmb["notes"]
            })
        st.dataframe(pd.DataFrame(limb_df_data), use_container_width=True, hide_index=True)

        if body_res.get("protected_count", 0) > 0:
            st.success(f"✨ कुण्डली में {body_res.get('protected_count', 0)} अंग शुभ ग्रहों की छत्रछाया में विशेष रूप से सशक्त व संरक्षित हैं।")

    with tab_b3:
        st.markdown("### 🎯 जन्मजात शारीरिक चिन्ह, तिल एवं मस्से (Congenital Scars & Marks)")
        st.caption("बृहत्संहिता एवं बृहत्पाराशर होराशास्त्र अनुसार पापग्रहों व लग्नेश की स्थिति से शरीर पर उत्पन्न होने वाले चिन्ह:")

        for cm in body_res.get("congenital_marks", []):
            st.markdown(f"""
            <div style="background:#F8FAFC; border-left:4px solid #6366F1; border-radius:4px; padding:12px; margin-bottom:10px;">
                <b>📍 चिन्ह विवरण:</b> <span style="color:#1E293B; font-size:14px;">{cm}</span>
            </div>
            """, unsafe_allow_html=True)

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
