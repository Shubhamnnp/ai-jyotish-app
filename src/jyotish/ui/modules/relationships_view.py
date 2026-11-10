# -*- coding: utf-8 -*-
"""
Module 24: Relationships & Compatibility Matrix View.
Evaluates Spouse (7th House), Family (Father 9th, Mother 4th, Siblings 3rd, Children 5th),
Friends & Benefactors (11th House), and Enemies & Competitors (6th House),
with Ansh-Kala-Vikala (DMS) precision, Karaka associations, and BPHS Sambandha guidelines.
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

GRAHA_RELATIONSHIP_KARAKAS = {
    "Sun": ("पिता व उच्चाधिकारी", "आत्मबल, पिता, वरिष्ठ अधिकारी, मान-प्रतिष्ठा व शासन पक्ष"),
    "Moon": ("माता व जनसम्पर्क", "माता, मातृपक्ष, मानसिक शांति, जनता व स्त्री सुख"),
    "Mars": ("भाई व पराक्रम", "छोटे भाई-बहन, सेना/प्रशासन, सहयोगी मित्र व साहसी स्वजन"),
    "Mercury": ("मित्र व ननिहाल", "ननिहाल, मामा, व्यापारिक साझेदार, सहपाठी व बौद्धिक मित्र"),
    "Jupiter": ("संतान व गुरुजन", "संतान, गुरु, मार्गदर्शक, वृद्ध विद्वान व धर्मात्मा स्वजन"),
    "Venus": ("जीवनसाथी व कला", "पत्नी/पति, दांपत्य साथी, ससुराल, स्त्री वर्ग व कला सहयोगी"),
    "Saturn": ("सेवक व अधीन कर्मचारी", "कर्मचारी, मजदूर, वृद्ध परिजन, चाचा व अनुज स्वजन"),
    "Rahu": ("सट्टेबाज व विदेशी", "कपटपूर्ण संगति, विदेशी संपर्क, ससुराल पक्ष व अप्रत्याशित संबंध"),
    "Ketu": ("नाना व आध्यात्मिक साधक", "नाना-नानी, त्यागी/साधु संगति व गूढ़ मित्र")
}

RELATIONSHIPS_SHLOKA = {
    "title": "बृहत्पाराशर होराशास्त्र एवं फलदीपिका — कलत्रभाव व सम्बंध मैत्री",
    "source": "महर्षि पराशर विरचित 'बृहत्पाराशर होराशास्त्रम्' (कलत्रभावाध्याय) एवं मन्त्रेश्वर विरचित 'फलदीपिका' (अध्याय १०)",
    "shloka": "सप्तमेशे बलोपेते शुभग्रहनिरीक्षिते ।\nकलत्रसुखमाप्नोति धर्मपत्नीसमन्विता ॥\nबन्धुस्थानाधिपे सौम्ये मित्रवर्गसमन्विते ।\nस्वजनानां भवेत् सौख्यं रिपुनाशश्च जायते ॥",
    "meaning": "सप्तमेश के बलवान व शुभ ग्रहों से दृष्ट होने पर श्रेष्ठ दांपत्य व जीवनसाथी का सुख प्राप्त होता है; तथा चतुर्थ (बन्धुभाव) व एकादश (मित्रभाव) के स्वामियों के शुभ होने पर स्वजनों का स्नेह एवं विरोधियों का शमन होता है।"
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


def render_relationships_view(chart, tabs: Optional[List[str]] = None):
    if tabs is None:
        tabs = [
            "👫 जीवनसाथी व दांपत्य",
            "👨‍👩‍👦 परिवार व स्वजन",
            "🌟 मित्र व सहायक",
            "⚔️ शत्रु व विरोधी"
        ]

    st.subheader("🤝 संबंध एवं स्वजन-मित्र-शत्रु विश्लेषण (Relationship & Compatibility Matrix)")
    st.write("बृहत्पाराशर होराशास्त्र एवं फलदीपिका अनुसार दांपत्य, माता-पिता, संतान, मित्र, सहायक पक्ष एवं कष्ट देने वाले विरोधी पक्षों का समग्र विश्लेषण।")

    # 1. Classical Shastriya Shloka Card
    with st.expander(f"📜 शास्त्रीय प्रमाण — {RELATIONSHIPS_SHLOKA['title']}", expanded=False):
        st.markdown(f"""
        <div style="background:#FFFBEB; border-left:4px solid #D97706; padding:12px; border-radius:6px; margin-bottom:10px;">
            <b style="color:#B45309; font-size:15px;">📖 ग्रंथ संदर्भ: {RELATIONSHIPS_SHLOKA['source']}</b>
            <pre style="white-space:pre-wrap; font-family:serif; font-size:14px; color:#78350F; margin:8px 0; background:transparent; border:none; padding:0;">
{RELATIONSHIPS_SHLOKA['shloka']}
            </pre>
            <div style="font-size:13px; color:#92400E; margin-top:6px;">
                <b>हिंदी भावार्थ:</b> {RELATIONSHIPS_SHLOKA['meaning']}
            </div>
        </div>
        """, unsafe_allow_html=True)

    rel_res = life_mod.RelationshipEngine.analyze(chart)

    # 2. Active Native Micro Relationship HUD Console with Ansh, Kala, Vikala
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
        <div style="background:linear-gradient(135deg, #1E1B4B 0%, #312E81 100%); color:#FFFFFF; border-radius:10px; padding:14px 18px; margin-bottom:12px; box-shadow:0 4px 6px -1px rgba(0,0,0,0.1);">
            <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; margin-bottom:8px;">
                <span style="font-size:16px; font-weight:700;">🤝 सक्रिय जातक संबंध वेध: <span style="color:#FDE047;">{getattr(chart, 'name', 'सक्रिय कुण्डली')}</span></span>
                <span style="font-size:13px; color:#C7D2FE;">🏛️ लग्न: <b>{l_sign_name} ({l_dms})</b> | 🌙 चंद्र: <b>{m_sign_name} ({m_dms})</b> | 🌟 <b>{m_nak} (पद {m_pada})</b></span>
            </div>
            <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(130px, 1fr)); gap:10px; font-size:12.5px; text-align:center;">
                <div style="background:rgba(255,255,255,0.08); padding:8px; border-radius:6px; border:1px solid rgba(255,255,255,0.15);">
                    <div style="color:#86EFAC; font-size:11px;">🛡️ लग्नेश (आत्मबल)</div>
                    <div style="font-size:15px; font-weight:700; color:#4ADE80;">{rel_res.get('lagnesh', 'मंगल')}</div>
                    <div style="font-size:10px; color:#BBF7D0;">व्यक्तित्व अधिपति</div>
                </div>
                <div style="background:rgba(255,255,255,0.08); padding:8px; border-radius:6px; border:1px solid rgba(255,255,255,0.15);">
                    <div style="color:#F472B6; font-size:11px;">💍 सप्तमेश (जीवनसाथी)</div>
                    <div style="font-size:15px; font-weight:700; color:#FBCFE8;">{rel_res['relations'].get('spouse', {}).get('lord', 'शुक्र')}</div>
                    <div style="font-size:10px; color:#FDF2F8;">दांपत्य सामंजस्य</div>
                </div>
                <div style="background:rgba(255,255,255,0.08); padding:8px; border-radius:6px; border:1px solid rgba(255,255,255,0.15);">
                    <div style="color:#93C5FD; font-size:11px;">🌟 एकादशेश (मित्र/सहायक)</div>
                    <div style="font-size:15px; font-weight:700; color:#BFDBFE;">{rel_res['relations'].get('friends', {}).get('lord', 'शनि')}</div>
                    <div style="font-size:10px; color:#DBEAFE;">सहयोगी वर्ग</div>
                </div>
                <div style="background:rgba(255,255,255,0.08); padding:8px; border-radius:6px; border:1px solid rgba(255,255,255,0.15);">
                    <div style="color:#FCA5A5; font-size:11px;">⚔️ षष्ठेश (विरोधी पक्ष)</div>
                    <div style="font-size:15px; font-weight:700; color:#FCA5A5;">{rel_res['relations'].get('enemies', {}).get('lord', 'बुध')}</div>
                    <div style="font-size:10px; color:#FECACA;">सतर्कता अपेक्षित</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Micro Planetary Status Grid Expander with Ansh-Kala-Vikala & Relationship Karakas
        with st.expander("🪐 सक्रिय जातक सूक्ष्म ग्रह-स्थिति (अंश, कला, विकला, नक्षत्र, चरण व संबंध कारकत्व)", expanded=False):
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

                    karaka_info = GRAHA_RELATIONSHIP_KARAKAS.get(p_name, ("सामान्य", "स्वजन"))

                    planets_data.append({
                        "ग्रह": f"{p_hi} ({p_name})",
                        "भाव": f"भाव {house}",
                        "राशि": s_name,
                        "अंश-कला-विकला (DMS)": dms_str,
                        "नक्षत्र व पद": f"{nak} (पद {pada})",
                        "अवस्था": f"{dignity_hi}{status_tag}",
                        "मुख्य संबंध कारक": karaka_info[0],
                        "शास्त्रीय स्वजन क्षेत्र": karaka_info[1]
                    })
            if planets_data:
                st.dataframe(pd.DataFrame(planets_data), use_container_width=True, hide_index=True)

    rendered_tabs = st.tabs(tabs)
    tab_r1, tab_r2, tab_r3, tab_r4 = rendered_tabs[0], rendered_tabs[1], rendered_tabs[2], rendered_tabs[3]

    # -------------------------------------------------------------
    # TAB 1: जीवनसाथी व दांपत्य
    # -------------------------------------------------------------
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

    # -------------------------------------------------------------
    # TAB 2: परिवार व स्वजन
    # -------------------------------------------------------------
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

    # -------------------------------------------------------------
    # TAB 3: मित्र व सहायक
    # -------------------------------------------------------------
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

    # -------------------------------------------------------------
    # TAB 4: शत्रु व विरोधी
    # -------------------------------------------------------------
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
