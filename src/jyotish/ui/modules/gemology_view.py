"""
Module 32: Classical Gemology, Rudraksha & Shastriya Upay View for JyotishOS.
References:
- Brihat Samhita (Varahamihira, Ch. 80-83 Ratna Pariksha)
- Garuda Purana (Ch. 68 Ratna Dhyana)
- Phaladeepika & Jataka Parijata (Dusthana Ratna Nishedha)
- Mantra Mahodadhi & Shiva Purana (Rudraksha & Japa Vidhana)
"""

import streamlit as st
import pandas as pd
from typing import Optional, List
from src.jyotish.services.gemology import (
    default_gemology_service,
    SHASTRIYA_GEMOLOGY_SHLOKAS,
    INCOMPATIBLE_GEM_COMBINATIONS,
    GEMSTONE_CATALOG
)


def render_gemology_view(chart, tabs: Optional[List[str]] = None):
    if tabs is None:
        tabs = [
            "💎 १. शास्त्रीय रत्न ऑडिट व संस्तुति (Gemstone Audit)",
            "🚫 २. सर्वथा वर्जित रत्न व त्रिक दोष (Prohibited Dusthana Gems)",
            "📿 ३. कुण्डली-सम्मत रुद्राक्ष विधान (Rudraksha Therapy)",
            "🌿 ४. दान, व्रत, मन्त्र एवं सात्विक शांति (Mantra, Daan & Vrata)",
            "💍 ५. विवाह व मांगलिक रत्न शुद्धि (Vivaha & Manglik Gem Shuddhi)",
            "📜 ६. बृहत्संहिता व गरुड़ पुराण प्रमाण (Classical Shlokas)"
        ]

    st.subheader("💎 रत्न, रुद्राक्ष एवं वैदिक उपचार विज्ञान (Gemology, Rudraksha & Shastriya Upay)")
    st.write(
        "वराहमिहिर विरचित बृहत्संहिता, गरुड़ पुराण एवं फलदीपिका के शास्त्रीय नियमों के आधार पर "
        "सक्रिय जातक की कुण्डली के सूक्ष्म अंश-कला, नक्षत्र-पद, लग्नेश व योगकारक स्थिति का निष्पक्ष विश्लेषण।"
    )

    # Shastriya Pramana Expandable Banner
    shloka_main = SHASTRIYA_GEMOLOGY_SHLOKAS.get("brihat_samhita_ratna_pariksha", {})
    if shloka_main:
        with st.expander(f"📜 शास्त्रीय प्रमाण — {shloka_main.get('title', 'रत्नपरीक्षा')}", expanded=False):
            st.markdown(f"""
            <div style="background:#FFFBEB; border-left:4px solid #D97706; padding:12px; border-radius:6px; margin-bottom:10px;">
                <b style="color:#B45309; font-size:15px;">📖 ग्रंथ संदर्भ: {shloka_main.get('source', '')}</b>
                <pre style="white-space:pre-wrap; font-family:serif; font-size:14px; color:#78350F; margin:8px 0; background:transparent; border:none; padding:0;">
{shloka_main.get('shloka', '')}
                </pre>
                <div style="font-size:13px; color:#92400E; margin-top:6px;">
                    <b>हिंदी भावार्थ:</b> {shloka_main.get('meaning', '')}
                </div>
            </div>
            """, unsafe_allow_html=True)

    # Compute Core Data
    audit = default_gemology_service.audit_all_planets(chart)
    fasting = default_gemology_service.get_navratri_fasting_tithi(chart)
    vivaha = default_gemology_service.get_vivaha_gem_muhurta_compatibility(chart)

    # Top KPI Metrics
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("लग्न एवं लग्नेश", f"{audit['lagna_name'].split(' (')[0]}", f"लग्नेश: {audit['lagnesh']}")
    c2.metric("संस्तुत शुभ रत्न", f"{len(audit['recommended_gems'])} रत्न", "🟢 धारण योग्य")
    c3.metric("सर्वथा वर्जित रत्न", f"{len(audit['strictly_prohibited_gems'])} रत्न", "🚫 त्रिक/नीच दोष")
    c4.metric("नवरात्रि व्रत तिथि", f"{fasting['optimal_tithi'].split(' (')[0]}", f"देवी: {fasting['devi_form'].split(' ')[1] if ' ' in fasting['devi_form'] else fasting['devi_form']}")

    t1, t2, t3, t4, t5, t6 = st.tabs(tabs)

    # -------------------------------------------------------------
    # TAB 1: शास्त्रीय रत्न ऑडिट व संस्तुति
    # -------------------------------------------------------------
    with t1:
        st.markdown("### 💎 सक्रिय जातक की कुण्डली अनुसार नवग्रह रत्न ऑडिट")
        st.caption("प्रत्येक ग्रह की स्पष्ट राशि, भाव, स्पष्ट अंश-कला, नक्षत्र-चरण एवं रत्न पात्रता:")

        table_data = []
        for p_name, p_info in audit["planets_audit"].items():
            status_symbol = "🟢 शुभ" if p_info["is_recommended"] else ("🚫 वर्जित" if p_info["status_code"] in ["STRICTLY_PROHIBITED", "PROHIBITED"] else "🟡 मध्यम")
            dms_str = p_info.get("dms_str") or f"{p_info['ansh']}° {p_info['kala']}'"
            table_data.append({
                "ग्रह": p_name,
                "भाव": f"{p_info['house']} भाव",
                "अंश-कला-विकला (DMS)": dms_str,
                "नक्षत्र एवं पद": f"{p_info['nakshatra']} (पद {p_info['pada']})",
                "रत्न": p_info["gem_hi"],
                "उपरत्न": p_info["substitute"],
                "निर्णय": f"{status_symbol} — {p_info['status_code']}",
                "उंगली / धातु": f"{p_info['finger']} / {p_info['metal']}",
                "धारण दिवस": p_info["day"]
            })

        df_gems = pd.DataFrame(table_data)
        st.dataframe(df_gems, use_container_width=True, hide_index=True)

        st.markdown("---")
        st.markdown("#### 🌟 विशेष धारण योग्य (Recommended) रत्नों का विवरण:")
        if audit["recommended_gems"]:
            for rg in audit["recommended_gems"]:
                p_item = audit["planets_audit"][rg["planet"]]
                with st.container(border=True):
                    c_g1, c_g2 = st.columns([1, 2.5])
                    with c_g1:
                        st.markdown(f"### {rg['gem']}")
                        st.markdown(f"**स्वामी ग्रह:** `{rg['planet']}` ({rg['role']})")
                        p_dms = p_item.get("dms_str") or f"{p_item['ansh']}° {p_item['kala']}'"
                        st.markdown(f"**स्थिति:** `{p_item['house']} भाव` | `{p_dms}`")
                        st.markdown(f"**नक्षत्र:** `{p_item['nakshatra']} (पद {p_item['pada']})`")
                    with c_g2:
                        st.success(f"**सकारात्मक फल (+):** {p_item['positive_verdict']}")
                        st.info(f"**धारण विधि:** {p_item['metal']} में {p_item['finger']} में {p_item['day']} को धारण करें।")
                        st.warning(f"**सावधानी (-):** {p_item['negative_caution']}")
        else:
            st.info("ℹ️ इस कुण्डली में किसी भी रत्न की बिना ज्योतिषी परामर्श के खुली संस्तुति नहीं है। रुद्राक्ष व मन्त्र साधना सर्वोत्तम रहेगी।")

    # -------------------------------------------------------------
    # TAB 2: सर्वथा वर्जित रत्न व त्रिक दोष
    # -------------------------------------------------------------
    with t2:
        st.markdown("### 🚫 सर्वथा वर्जित रत्न एवं त्रिक (६, ८, १२ भाव) दोष")
        shloka_trik = SHASTRIYA_GEMOLOGY_SHLOKAS.get("phaladeepika_dusthana_ratna_nishedha", {})
        if shloka_trik:
            st.markdown(f"""
            <div style="background:#FEF2F2; border-left:4px solid #EF4444; padding:12px; border-radius:6px; margin-bottom:12px;">
                <b style="color:#B91C1C; font-size:15px;">📜 {shloka_trik.get('title', '')}</b>
                <pre style="white-space:pre-wrap; font-family:serif; font-size:14px; color:#991B1B; margin:8px 0; background:transparent; border:none; padding:0;">
{shloka_trik.get('shloka', '')}
                </pre>
                <div style="font-size:13px; color:#7F1D1D; margin-top:6px;">
                    <b>शास्त्रीय नियम:</b> {shloka_trik.get('meaning', '')}
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("#### 🚨 इस कुण्डली में प्रतिबंधित रत्न:")
        if audit["strictly_prohibited_gems"]:
            for pg in audit["strictly_prohibited_gems"]:
                p_item = audit["planets_audit"][pg["planet"]]
                with st.container(border=True):
                    st.markdown(f"#### 🚫 {pg['gem']} ({pg['planet']} — {pg['house']} भाव)")
                    st.error(f"**निषेध कारण:** {pg['reason']}")
                    st.markdown(f"**हानि की आशंका (-):** {p_item['negative_caution']}")
                    st.markdown(f"**सुरक्षित सात्विक विकल्प (+):** {p_item['positive_verdict']} — `{p_item['rudraksha']}` एवं मन्त्र: `{p_item['beej_mantra']}`")
        else:
            st.success("✅ इस कुण्डली में त्रिक भावों में कोई गंभीर ग्रह दोष नहीं है।")

    # -------------------------------------------------------------
    # TAB 3: कुण्डली-सम्मत रुद्राक्ष विधान
    # -------------------------------------------------------------
    with t3:
        st.markdown("### 📿 कुण्डली-सम्मत प्रामाणिक रुद्राक्ष विधान")
        st.caption("रत्नों के विपरीत रुद्राक्ष में कोई नकारात्मक विकिरण नहीं होता। यह पीड़ित ग्रहों की भी निर्दोष शांति करता है:")

        rudra_data = []
        for p_name, p_info in audit["planets_audit"].items():
            r_dms = p_info.get("dms_str") or f"{p_info['ansh']}° {p_info['kala']}'"
            rudra_data.append({
                "सम्बन्धित ग्रह": p_name,
                "ग्रह स्थिति": f"{p_info['house']} भाव ({r_dms})",
                "प्रशस्त रुद्राक्ष": p_info["rudraksha"],
                "इष्ट देवता": p_info["deity"],
                "शांति मन्त्र": p_info["beej_mantra"],
                "जप संख्या": f"{p_info['japa_count']:,} बार"
            })

        st.dataframe(pd.DataFrame(rudra_data), use_container_width=True, hide_index=True)

        st.markdown("---")
        with st.container(border=True):
            st.markdown("#### 🕉️ रुद्राक्ष धारण एवं शुद्धि नियम:")
            st.markdown("""
            1. **धारण काल:** सोमवार, मासिक शिवरात्रि, महाशिवरात्रि, अथवा प्रदोष काल में धारण करें।
            2. **शुद्धि संस्कार:** कच्चे दूध, गंगाजल, पंचामृत से स्नान कराकर भस्म व चन्दन अर्पित करें।
            3. **प्राण प्रतिष्ठा मन्त्र:** `ॐ नमः शिवाय` अथवा महामृत्युंजय मन्त्र की ११ माला जप कर धारण करें।
            4. **सावधानी:** सूतक, श्मशान वेला एवं मद्य-मांस सेवन के समय रुद्राक्ष उतारकर पवित्र स्थान पर रखें।
            """)

    # -------------------------------------------------------------
    # TAB 4: दान, व्रत, मन्त्र एवं सात्विक शांति
    # -------------------------------------------------------------
    with t4:
        st.markdown("### 🌿 सात्विक दान, व्रत, मन्त्र एवं साधना")
        st.caption("अनिष्ट ग्रहों के शमन हेतु सात्विक दान, उपवास एवं मन्त्र साधना:")

        # Navratri Fasting Tithi Card
        with st.container(border=True):
            st.markdown(f"#### 🚩 सक्रिय जातक हेतु अनुशंसित नवरात्रि व्रत तिथि")
            c_nv1, c_nv2 = st.columns([1.2, 2.5])
            with c_nv1:
                st.markdown(f"**सर्वोत्तम तिथि:** `{fasting['optimal_tithi']}`")
                st.markdown(f"**उपास्य स्वरूप:** `{fasting['devi_form']}`")
                st.markdown(f"**लग्नेश व चंद्र नक्षत्र:** `{fasting['lagnesh']}` | `{fasting['moon_nakshatra']} (पद {fasting['moon_pada']})`")
            with c_nv2:
                st.success(f"**साधना फल (+):** {fasting['positive_verdict']}")
                st.info(f"**विधान:** {fasting['fasting_guideline']}")
                st.warning(f"**सावधानी (-):** {fasting['negative_caution']}")

        st.markdown("---")
        st.markdown("#### 📋 नवग्रह दान एवं जप निर्देशिका:")
        daan_list = []
        for p_name, p_info in audit["planets_audit"].items():
            daan_list.append({
                "ग्रह": p_name,
                "बीज मन्त्र": p_info["beej_mantra"],
                "जप संख्या": f"{p_info['japa_count']:,}",
                "दान सामग्री": p_info["daan_items"],
                "दान दिन": p_info["daan_day"],
                "व्रत निर्देश": p_info["vrata"]
            })
        st.dataframe(pd.DataFrame(daan_list), use_container_width=True, hide_index=True)

    # -------------------------------------------------------------
    # TAB 5: विवाह व मांगलिक रत्न शुद्धि
    # -------------------------------------------------------------
    with t5:
        st.markdown("### 💍 विवाह व मांगलिक कार्यों हेतु रत्न शुद्धि एवं मुहूर्त")
        st.caption("विवाह, सगाई, उपनयन एवं प्रथम रत्न धारण हेतु त्रिबल शुद्धि व निषेध विचार:")

        c_v1, c_v2, c_v3 = st.columns(3)
        c_v1.metric("सूर्य बल (Surya Balam)", "विशुद्ध (+)" if vivaha["sun_shuddhi"] else "अल्प (-)", "तेज व प्रतिष्ठा")
        c_v2.metric("चन्द्र बल (Chandra Balam)", "विशुद्ध (+)" if vivaha["chandra_shuddhi"] else "अल्प (-)", "मन व भावना")
        c_v3.metric("गुरु बल (Guru Balam)", "विशुद्ध (+)" if vivaha["guru_shuddhi"] else "अल्प (-)", "ज्ञान व सौभाग्य")

        if vivaha["combustion_warning"]:
            st.warning(vivaha["combustion_warning"])

        st.markdown("---")
        st.markdown("#### 🚫 परस्पर विरोधी व घातक रत्न संयोजन (Incompatible Combinations):")
        st.caption("इन रत्नों को कभी भी एक साथ एक ही शरीर पर धारण नहीं करना चाहिए:")

        incomp_rows = []
        for inc in vivaha["incompatible_combinations"]:
            incomp_rows.append({
                "वर्जित रत्न युगल": f"{inc['pair'][0]} + {inc['pair'][1]}",
                "शास्त्रीय अनिष्ट कारण (-)": inc["reason"]
            })
        st.dataframe(pd.DataFrame(incomp_rows), use_container_width=True, hide_index=True)

        st.markdown("---")
        with st.container(border=True):
            st.markdown("#### ⏳ नवीन रत्न धारण हेतु शुभ नक्षत्र:")
            st.markdown(f"**प्रशस्त नक्षत्र:** {', '.join(vivaha['auspicious_wearing_nakshatras'])}")
            st.success(f"**सकारात्मक मुहूर्त निर्देश (+):** {vivaha['positive_verdict']}")
            st.error(f"**कदापि न करें (-):** {vivaha['negative_caution']}")

    # -------------------------------------------------------------
    # TAB 6: शास्त्रीय प्रमाण एवं श्लोक
    # -------------------------------------------------------------
    with t6:
        st.markdown("### 📜 बृहत्संहिता, गरुड़ पुराण एवं फलदीपिका — मूल श्लोक")
        st.caption("ज्योतिष ग्रन्थों के प्रामाणिक संदर्भ एवं महर्षियों के आदेश:")

        for k, sh in SHASTRIYA_GEMOLOGY_SHLOKAS.items():
            with st.container(border=True):
                st.markdown(f"#### 📖 {sh['title']}")
                st.markdown(f"**स्रोत:** *{sh['source']}*")
                st.code(sh["shloka"], language="text")
                st.markdown(f"**शास्त्रीय भावार्थ:** {sh['meaning']}")
