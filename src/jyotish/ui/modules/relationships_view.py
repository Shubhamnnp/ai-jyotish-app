import streamlit as st
import importlib

def render_relationships_view(chart, tabs=None):
    if tabs is None:
        tabs = [
            '💑 विवाह एवं जीवनसाथी',
            '⚖️ सुख, सामंजस्य एवं विच्छेद योग',
            '🌿 वैदिक एवं ज्योतिषीय समाधान'
        ]
    st.subheader("🤝 संबंध एवं स्वजन-मित्र-शत्रु विश्लेषण (Relationship & Compatibility Matrix)")
    st.write("बृहत्पाराशर होराशास्त्र एवं फलदीपिका अनुसार दांपत्य, माता-पिता, संतान, मित्र, सहायक पक्ष एवं कष्ट देने वाले विरोधी पक्षों का समग्र विश्लेषण।")

    import importlib
    import src.jyotish.core.lifestyle as life_mod
    importlib.reload(life_mod)

    rel_res = life_mod.RelationshipEngine.analyze(chart)

    # Top Status Banner
    c_r1, c_r2, c_r3, c_r4 = st.columns(4)
    c_r1.metric("लग्नेश (व्यक्तित्व स्वामी)", rel_res["lagnesh"], "स्वाभिमान एवं मूल तत्व")
    c_r2.metric("सर्वाधिक सहयोगी पक्ष", rel_res["greatest_helper_side"].split(" ")[0], "भाग्यवर्धक संबंध")
    c_r3.metric("विशेष सतर्कता पक्ष", "सट्टेबाज़ / धोखेबाज़", "६/१२ भाव प्रभाव")
    c_r4.metric("संबंध नीति", "पारदर्शिता एवं आदर", "स्थायी सुख")

    tab_r1, tab_r2, tab_r3, tab_r4 = st.tabs(tabs)

    with tab_r1:
        st.markdown("### 👫 दांपत्य एवं जीवनसाथी संबंध (सप्तम भाव विचार)")
        sp_data = rel_res["relations"].get("spouse", {})
        bp_data = rel_res["relations"].get("partners", {})

        st.markdown(f"""
        <div style="background:#FDF4FF; border:1.5px solid #F472B6; border-radius:10px; padding:16px; margin-bottom:14px;">
            <b style="color:#BE185D; font-size:16px;">💍 जीवनसाथी (Spouse): {sp_data.get('title', '')}</b>
            <p style="margin:6px 0;"><b>सप्तमेश ग्रह:</b> {sp_data.get('lord', '')} | <b>भाव में स्थित ग्रह:</b> {', '.join(sp_data.get('occupants', [])) if sp_data.get('occupants') else 'रिक्त (शुभ दृष्टि)'}</p>
            <p style="margin:6px 0;"><b>संबंध स्वरूप:</b> <span style="color:#059669; font-weight:800;">{sp_data.get('status', '')}</span></p>
            <p style="margin:6px 0;"><b>शास्त्रीय फल:</b> {sp_data.get('nature_hi', '')}</p>
            <div style="background:#FFFFFF; border-radius:6px; padding:8px; border:1px solid #FBCFE8; margin-top:8px;">
                <b style="color:#9D174D;">💡 संबंध परामर्श:</b> {sp_data.get('advice_hi', '')}
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div style="background:#F8FAFC; border:1px solid #CBD5E1; border-radius:8px; padding:12px;">
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
                <b style="color:#B45309;">👑 पिता एवं वरिष्ठजन (९वां भाव):</b><br/>
                <b>स्वामी:</b> {fa_data.get('lord', '')} | <b>स्थिति:</b> {fa_data.get('status', '')}<br/>
                <small>{fa_data.get('nature_hi', '')}</small>
            </div>
            """, unsafe_allow_html=True)

            mo_data = rel_res["relations"].get("mother", {})
            st.markdown(f"""
            <div style="background:#F0FDF4; border:1px solid #86EFAC; border-radius:8px; padding:12px; margin-bottom:10px;">
                <b style="color:#15803D;">🤱 माता एवं मातृपक्ष (४था भाव):</b><br/>
                <b>स्वामी:</b> {mo_data.get('lord', '')} | <b>स्थिति:</b> {mo_data.get('status', '')}<br/>
                <small>{mo_data.get('nature_hi', '')}</small>
            </div>
            """, unsafe_allow_html=True)

        with col_fam2:
            sib_data = rel_res["relations"].get("siblings", {})
            st.markdown(f"""
            <div style="background:#EFF6FF; border:1px solid #93C5FD; border-radius:8px; padding:12px; margin-bottom:10px;">
                <b style="color:#1D4ED8;">👦 भाई-बहन एवं सहकर्मी (३रा भाव):</b><br/>
                <b>स्वामी:</b> {sib_data.get('lord', '')} | <b>स्थिति:</b> {sib_data.get('status', '')}<br/>
                <small>{sib_data.get('nature_hi', '')}</small>
            </div>
            """, unsafe_allow_html=True)

            ch_data = rel_res["relations"].get("children", {})
            st.markdown(f"""
            <div style="background:#FAF5FF; border:1px solid #D8B4FE; border-radius:8px; padding:12px; margin-bottom:10px;">
                <b style="color:#7E22CE;">👶 संतान एवं शिष्य वर्ग (५वां भाव):</b><br/>
                <b>स्वामी:</b> {ch_data.get('lord', '')} | <b>स्थिति:</b> {ch_data.get('status', '')}<br/>
                <small>{ch_data.get('nature_hi', '')}</small>
            </div>
            """, unsafe_allow_html=True)

    with tab_r3:
        st.markdown("### 🌟 मित्र, उच्चाधिकारी एवं सर्वाधिक सहायक लोग (११वां भाव)")
        fr_data = rel_res["relations"].get("friends", {})

        st.markdown(f"""
        <div style="background:#ECFDF5; border:1.5px solid #10B981; border-radius:10px; padding:16px; margin-bottom:14px;">
            <b style="color:#047857; font-size:16px;">🤝 {fr_data.get('title', '')}</b>
            <p style="margin:6px 0;"><b>एकादशेश स्वामी:</b> {fr_data.get('lord', '')} | <b>सहयोग बल:</b> <span style="color:#059669; font-weight:800;">{fr_data.get('status', '')}</span></p>
            <p style="margin:6px 0;"><b>शास्त्रीय प्रभाव:</b> {fr_data.get('nature_hi', '')}</p>
            <div style="background:#FFFFFF; border-radius:6px; padding:8px; border:1px solid #A7F3D0; margin-top:8px;">
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
            <b style="color:#991B1B; font-size:16px;">⚠️ {en_data.get('title', '')}</b>
            <p style="margin:6px 0;"><b>षष्ठेश ग्रह:</b> {en_data.get('lord', '')} | <b>शत्रु संकट स्तर:</b> <span style="color:#DC2626; font-weight:800;">{en_data.get('status', '')}</span></p>
            <p style="margin:6px 0;"><b>ग्रह स्थिति:</b> {en_data.get('nature_hi', '')}</p>
            <div style="background:#FFFFFF; border-radius:6px; padding:8px; border:1px solid #FECACA; margin-top:8px;">
                <b style="color:#B91C1C;">🛡️ बचाव एवं सावधानी सूत्र:</b> {en_data.get('advice_hi', '')}
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.warning("⚠️ **सावधानी परामर्श:** बिना लिखा-पढ़ी के किसी को ऋण या जमानत न दें। गुप्त योजनाओं को समय से पूर्व साझा न करें।")

