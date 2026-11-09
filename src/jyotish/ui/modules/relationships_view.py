import streamlit as st
from src.jyotish.services.shastriya_pramana import SHASTRIYA_SHLOKAS
import src.jyotish.core.lifestyle as life_mod


def render_relationships_view(chart, tabs=None):
    if tabs is None:
        tabs = [
            "👫 जीवनसाथी व दांपत्य",
            "👨‍👩‍👦 परिवार व स्वजन",
            "🌟 मित्र व सहायक",
            "⚔️ शत्रु व विरोधी"
        ]

    st.subheader("🤝 संबंध एवं स्वजन-मित्र-शत्रु विश्लेषण (Relationship & Compatibility Matrix)")
    st.write("बृहत्पाराशर होराशास्त्र एवं फलदीपिका अनुसार दांपत्य, माता-पिता, संतान, मित्र, सहायक पक्ष एवं कष्ट देने वाले विरोधी पक्षों का समग्र विश्लेषण।")

    # Classical Shastriya Shloka Card
    rel_pramana = SHASTRIYA_SHLOKAS.get("bphs_kalatra_sambandha", {})
    if rel_pramana:
        with st.expander("📜 शास्त्रीय प्रमाण — बृहत्पाराशर होराशास्त्र (कलत्रभाव एवं सम्बंध मैत्री सिद्धान्त)", expanded=False):
            st.markdown(f"""
            <div style="background:#FFFBEB; border-left:4px solid #D97706; padding:12px; border-radius:6px; margin-bottom:10px;">
                <b style="color:#B45309; font-size:15px;">📖 ग्रंथ संदर्भ: {rel_pramana.get('grantha', '')}</b>
                <pre style="white-space:pre-wrap; font-family:serif; font-size:14px; color:#78350F; margin:8px 0; background:transparent; border:none; padding:0;">
{rel_pramana.get('shloka_sanskrit', rel_pramana.get('shloka', ''))}
                </pre>
                <div style="font-size:13px; color:#92400E; margin-top:6px;">
                    <b>हिंदी भावार्थ:</b> {rel_pramana.get('anuvad_hi', rel_pramana.get('hindi_translation', ''))}
                </div>
            </div>
            """, unsafe_allow_html=True)

    rel_res = life_mod.RelationshipEngine.analyze(chart)

    # Top Status Banner - 4 Key Relationship Pillars
    c_r1, c_r2, c_r3, c_r4 = st.columns(4)
    c_r1.metric("लग्नेश (व्यक्तित्व अधिपति)", rel_res.get("lagnesh", "मंगल"), "मूल आत्मबल")
    c_r2.metric("सर्वाधिक सहयोगी पक्ष", rel_res.get("greatest_helper_side", "मित्र व गुरु").split(" ")[0], "भाग्य संवर्धन")
    c_r3.metric("विशेष सतर्कता पक्ष", rel_res.get("caution_side", "सट्टेबाज़").split(" ")[0], "सावधानी अपेक्षित")
    c_r4.metric("संबंध नीति सूत्र", "पारदर्शिता एवं आदर", "स्थायी सुख")

    tab_r1, tab_r2, tab_r3, tab_r4 = st.tabs(tabs)

    with tab_r1:
        st.markdown("### 👫 दांपत्य एवं जीवनसाथी संबंध (सप्तम भाव विचार)")
        sp_data = rel_res["relations"].get("spouse", {})
        bp_data = rel_res["relations"].get("partners", {})

        st.markdown(f"""
        <div style="background:#FDF4FF; border:1.5px solid #F472B6; border-radius:10px; padding:16px; margin-bottom:14px;">
            <b style="color:#BE185D; font-size:17px;">💍 जीवनसाथी (Spouse): {sp_data.get('title', '')}</b>
            <div style="margin:8px 0; font-size:14px; color:#374151;">
                • <b>सप्तम भाव राशि:</b> {sp_data.get('sign_name', '')} | <b>सप्तमेश:</b> {sp_data.get('lord', '')} (भाव {sp_data.get('lord_house', 7)}, गरिमा: {sp_data.get('lord_dignity', 'neutral')})<br/>
                • <b>भाव में स्थित ग्रह:</b> {', '.join(sp_data.get('occupants', [])) if sp_data.get('occupants') else 'रिक्त (शुभ दृष्टि)'}<br/>
                • <b>संबंध स्वरूप:</b> <span style="color:#059669; font-weight:800;">{sp_data.get('status', '')}</span>
            </div>
            <p style="margin:8px 0; font-size:14px; color:#1E293B;"><b>शास्त्रीय स्थिति:</b> {sp_data.get('nature_hi', '')}</p>
        </div>
        """, unsafe_allow_html=True)

        col_sp1, col_sp2 = st.columns(2)
        with col_sp1:
            st.markdown("""
            <div style="background:#F0FDF4; border:1px solid #86EFAC; border-radius:8px; padding:12px; margin-bottom:10px;">
                <b style="color:#15803D;">✨ सकारात्मक दांपत्य बिंदु (+) :</b>
            """, unsafe_allow_html=True)
            for pt in sp_data.get("positive_points", []):
                st.markdown(f"• <span style='color:#14532D;'>{pt}</span>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with col_sp2:
            st.markdown("""
            <div style="background:#FFFBEB; border:1px solid #FCD34D; border-radius:8px; padding:12px; margin-bottom:10px;">
                <b style="color:#B45309;">⚠️ ध्यान रखने योग्य बातें (-) :</b>
            """, unsafe_allow_html=True)
            for cpt in sp_data.get("caution_points", []):
                st.markdown(f"• <span style='color:#78350F;'>{cpt}</span>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown(f"""
        <div style="background:#F8FAFC; border:1px solid #CBD5E1; border-radius:8px; padding:12px; margin-top:8px;">
            <b style="color:#334155;">💼 व्यावसायिक साझेदारी (Business Partnerships):</b><br/>
            <span>{bp_data.get('nature_hi', '')}</span><br/>
            <small style="color:#64748B;">{bp_data.get('advice_hi', '')}</small>
        </div>
        """, unsafe_allow_html=True)

    with tab_r2:
        st.markdown("### 👨‍👩‍👦 परिवार, माता-पिता, संतान एवं भाई-बहन")

        col_fam1, col_fam2 = st.columns(2)
        with col_fam1:
            fa_data = rel_res["relations"].get("father", {})
            st.markdown(f"""
            <div style="background:#FFFBEB; border:1px solid #FCD34D; border-radius:8px; padding:12px; margin-bottom:10px;">
                <b style="color:#B45309; font-size:15px;">👑 पिता एवं वरिष्ठजन (९वां भाव):</b><br/>
                <b>स्वामी:</b> {fa_data.get('lord', '')} ({fa_data.get('sign_name', '')}) | <b>भाव स्थिति:</b> {fa_data.get('lord_house', 9)}<br/>
                <b>संबंध स्थिति:</b> <span style="color:#059669; font-weight:700;">{fa_data.get('status', '')}</span><br/>
                <span style="font-size:13px; color:#4B5563;">{fa_data.get('nature_hi', '')}</span><br/>
                <small style="color:#15803D;">• {fa_data.get('positive_points', ['आदर व संस्कार'])[0]}</small>
            </div>
            """, unsafe_allow_html=True)

            mo_data = rel_res["relations"].get("mother", {})
            st.markdown(f"""
            <div style="background:#F0FDF4; border:1px solid #86EFAC; border-radius:8px; padding:12px; margin-bottom:10px;">
                <b style="color:#15803D; font-size:15px;">🤱 माता एवं मातृपक्ष (४था भाव):</b><br/>
                <b>स्वामी:</b> {mo_data.get('lord', '')} ({mo_data.get('sign_name', '')}) | <b>भाव स्थिति:</b> {mo_data.get('lord_house', 4)}<br/>
                <b>संबंध स्थिति:</b> <span style="color:#059669; font-weight:700;">{mo_data.get('status', '')}</span><br/>
                <span style="font-size:13px; color:#4B5563;">{mo_data.get('nature_hi', '')}</span><br/>
                <small style="color:#15803D;">• {mo_data.get('positive_points', ['स्नेह व सुख'])[0]}</small>
            </div>
            """, unsafe_allow_html=True)

        with col_fam2:
            sib_data = rel_res["relations"].get("siblings", {})
            st.markdown(f"""
            <div style="background:#EFF6FF; border:1px solid #93C5FD; border-radius:8px; padding:12px; margin-bottom:10px;">
                <b style="color:#1D4ED8; font-size:15px;">👦 भाई-बहन एवं सहकर्मी (३रा भाव):</b><br/>
                <b>स्वामी:</b> {sib_data.get('lord', '')} ({sib_data.get('sign_name', '')}) | <b>भाव स्थिति:</b> {sib_data.get('lord_house', 3)}<br/>
                <b>संबंध स्थिति:</b> <span style="color:#059669; font-weight:700;">{sib_data.get('status', '')}</span><br/>
                <span style="font-size:13px; color:#4B5563;">{sib_data.get('nature_hi', '')}</span><br/>
                <small style="color:#1D4ED8;">• {sib_data.get('positive_points', ['सहयोग व पराक्रम'])[0]}</small>
            </div>
            """, unsafe_allow_html=True)

            ch_data = rel_res["relations"].get("children", {})
            st.markdown(f"""
            <div style="background:#FAF5FF; border:1px solid #D8B4FE; border-radius:8px; padding:12px; margin-bottom:10px;">
                <b style="color:#7E22CE; font-size:15px;">👶 संतान एवं शिष्य वर्ग (५वां भाव):</b><br/>
                <b>स्वामी:</b> {ch_data.get('lord', '')} ({ch_data.get('sign_name', '')}) | <b>भाव स्थिति:</b> {ch_data.get('lord_house', 5)}<br/>
                <b>संबंध स्थिति:</b> <span style="color:#059669; font-weight:700;">{ch_data.get('status', '')}</span><br/>
                <span style="font-size:13px; color:#4B5563;">{ch_data.get('nature_hi', '')}</span><br/>
                <small style="color:#7E22CE;">• {ch_data.get('positive_points', ['संतान सुख व यश'])[0]}</small>
            </div>
            """, unsafe_allow_html=True)

    with tab_r3:
        st.markdown("### 🌟 मित्र, उच्चाधिकारी एवं सर्वाधिक सहायक लोग (११वां भाव)")
        fr_data = rel_res["relations"].get("friends", {})

        st.markdown(f"""
        <div style="background:#ECFDF5; border:1.5px solid #10B981; border-radius:10px; padding:16px; margin-bottom:14px;">
            <b style="color:#047857; font-size:17px;">🤝 {fr_data.get('title', '')}</b>
            <div style="margin:8px 0; font-size:14px; color:#374151;">
                • <b>एकादशेश स्वामी:</b> {fr_data.get('lord', '')} ({fr_data.get('sign_name', '')}) | <b>भाव:</b> {fr_data.get('lord_house', 11)}<br/>
                • <b>सहयोग बल स्तर:</b> <span style="color:#059669; font-weight:800;">{fr_data.get('status', '')}</span><br/>
                • <b>शास्त्रीय प्रभाव:</b> {fr_data.get('nature_hi', '')}
            </div>
            <div style="background:#FFFFFF; border-radius:6px; padding:10px; border:1px solid #A7F3D0; margin-top:8px;">
                <b style="color:#065F46;">💎 सहयोगी पक्ष:</b> {fr_data.get('advice_hi', '')}
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.info("💡 **ज्योतिषीय सूत्र:** ११वें भाव का स्वामी जिन-जिन ग्रहों का मित्र होगा, उन-उन ग्रहों से जुड़े व्यवसाय, संबंध व मित्र जीवन में अचानक बड़े अवसर और वित्तीय उन्नति प्रदान करेंगे।")

    with tab_r4:
        st.markdown("### ⚔️ विरोधी, शत्रु, विश्वासघात एवं सावधान रहने योग्य पक्ष (६ठा भाव)")
        en_data = rel_res["relations"].get("enemies", {})

        st.markdown(f"""
        <div style="background:#FEF2F2; border:1.5px solid #EF4444; border-radius:10px; padding:16px; margin-bottom:14px;">
            <b style="color:#991B1B; font-size:17px;">⚠️ {en_data.get('title', '')}</b>
            <div style="margin:8px 0; font-size:14px; color:#374151;">
                • <b>षष्ठेश ग्रह:</b> {en_data.get('lord', '')} ({en_data.get('sign_name', '')}) | <b>भाव:</b> {en_data.get('lord_house', 6)}<br/>
                • <b>शत्रु संकट स्तर:</b> <span style="color:#DC2626; font-weight:800;">{en_data.get('status', '')}</span><br/>
                • <b>ग्रह स्थिति:</b> {en_data.get('nature_hi', '')}
            </div>
            <div style="background:#FFFFFF; border-radius:6px; padding:10px; border:1px solid #FECACA; margin-top:8px;">
                <b style="color:#B91C1C;">🛡️ बचाव एवं सावधानी सूत्र:</b> {en_data.get('advice_hi', '')}
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.warning("⚠️ **सावधानी परामर्श:** बिना लिखा-पढ़ी के किसी को ऋण या जमानत न दें। अपनी गोपनीय योजनाओं को समय से पूर्व किसी से साझा न करें।")
