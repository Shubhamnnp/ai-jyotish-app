"""
Executive UI View for "शास्त्रीय फलादेश" (Shastriya Phaladesh - Classical Predictive Analysis).
Presents:
- 50 Comprehensive Life Dimensions
- 100 Real-World Querent FAQs per dimension
- Active Kundali Mathematical Evidence (Degrees, Signs, Nakshatra Padas, Bhavabala, SAV, Shadbala)
- Cross-verification across Shodashvarga (D1-D60), Chandra/Surya Kundlis, Kota & Sudarshan Chakra
- Honest Positive & Negative Scriptural Evidence (Brihat Parashara Hora Shastra, Phaladeepika, Saravali)
"""

import streamlit as st
import importlib
from datetime import datetime, date, time
from typing import Dict, Any, Optional, List

import src.jyotish.services.shastriya_faladesh as s_faladesh_mod
importlib.reload(s_faladesh_mod)
from src.jyotish.services.shastriya_faladesh import (
    default_shastriya_faladesh_engine,
    LIFE_DIMENSIONS_50,
    PLANET_NAMES_HI
)
from src.jyotish.core.models import KundaliChart, BirthData
from src.jyotish.core.constants import GRAHAS, SIGNS, SIGN_NAMES, SIGN_LORDS, NAKSHATRAS


def render_shastriya_faladesh_view(chart: KundaliChart, birth_profile: Optional[BirthData] = None, is_dark: bool = False, tz_offset: float = 5.5):
    """Renders the comprehensive Classical Predictive Analysis (शास्त्रीय फलादेश) view."""

    card_bg = "#111827" if is_dark else "#FFFFFF"
    card_bdr = "#374151" if is_dark else "#E2E8F0"
    text_main = "#F8FAFC" if is_dark else "#0F172A"
    text_sub = "#94A3B8" if is_dark else "#64748B"
    gold_color = "#F59E0B" if is_dark else "#D97706"
    blue_color = "#38BDF8" if is_dark else "#2563EB"
    green_color = "#34D399" if is_dark else "#059669"
    red_color = "#F87171" if is_dark else "#DC2626"

    # Active Lagna & Planets
    lagna_name = chart.lagna_sign_name or "Aries"
    lagna_deg = round(chart.lagna_degree, 2)
    moon_p = chart.planets.get("Moon")
    sun_p = chart.planets.get("Sun")
    moon_sign = moon_p.sign_name if moon_p else "Taurus"
    sun_sign = sun_p.sign_name if sun_p else "Aries"

    # Top Grand Hero Banner
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #0F172A 0%, #1E1B4B 50%, #311042 100%); border: 2px solid {gold_color}; border-radius: 14px; padding: 18px 24px; color: #FFFFFF; box-shadow: 0 10px 30px rgba(0,0,0,0.3); margin-bottom: 14px;">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 14px;">
            <div>
                <div style="display: flex; align-items: center; gap: 10px;">
                    <span style="font-size: 28px;">📜</span>
                    <h2 style="margin: 0; color: #F59E0B; font-size: 1.55rem; font-weight: 900; letter-spacing: -0.5px;">
                        शास्त्रीय फलादेश महा-प्रणाली (Classical Predictive Analysis)
                    </h2>
                </div>
                <div style="color: #E2E8F0; font-size: 0.90rem; margin-top: 5px; font-weight: 600;">
                    जीवन के ५० सम्पूर्ण आयाम • प्रति आयाम १०० जातक प्रश्न-उत्तर (FAQ) • पूर्ण ईमानदारी से सकारात्मक व नकारात्मक साक्ष्य
                </div>
            </div>
            <div style="display: flex; gap: 10px; flex-wrap: wrap;">
                <div style="background: rgba(255,255,255,0.12); border: 1px solid rgba(255,255,255,0.25); border-radius: 9px; padding: 6px 12px; text-align: center;">
                    <div style="font-size: 10px; color: #FDE68A; font-weight: 700;">जन्म लग्न</div>
                    <div style="font-size: 13px; font-weight: 800; color: #FFFFFF;">{lagna_name} ({lagna_deg}°)</div>
                </div>
                <div style="background: rgba(255,255,255,0.12); border: 1px solid rgba(255,255,255,0.25); border-radius: 9px; padding: 6px 12px; text-align: center;">
                    <div style="font-size: 10px; color: #93C5FD; font-weight: 700;">चन्द्र राशि</div>
                    <div style="font-size: 13px; font-weight: 800; color: #FFFFFF;">{moon_sign}</div>
                </div>
                <div style="background: rgba(255,255,255,0.12); border: 1px solid rgba(255,255,255,0.25); border-radius: 9px; padding: 6px 12px; text-align: center;">
                    <div style="font-size: 10px; color: #FCA5A5; font-weight: 700;">सूर्य राशि</div>
                    <div style="font-size: 13px; font-weight: 800; color: #FFFFFF;">{sun_sign}</div>
                </div>
                <div style="background: rgba(255,255,255,0.12); border: 1px solid rgba(255,255,255,0.25); border-radius: 9px; padding: 6px 12px; text-align: center;">
                    <div style="font-size: 10px; color: #86EFAC; font-weight: 700;">शास्त्रीय साक्ष्य</div>
                    <div style="font-size: 13px; font-weight: 800; color: #10B981;">१००% प्रामाणिक</div>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 4 Master View Sub-Tabs
    sub_tab1, sub_tab2, sub_tab3, sub_tab4 = st.tabs([
        "🌟 १. ५० जीवन आयाम महा-विश्लेषण (50 Life Dimensions)",
        "❓ २. १०० शास्त्रीय प्रश्न-उत्तर इंजन (100 Querent FAQs)",
        "🔬 ३. सर्व-गणना संश्लेषण (All Calculations Matrix)",
        "📜 ४. शास्त्रीय साक्ष्य, ग्रन्थ प्रमाण व उपाय (Pramana & Remedies)"
    ])

    # -------------------------------------------------------------------------
    # TAB 1: 50 LIFE DIMENSIONS NAVIGATOR
    # -------------------------------------------------------------------------
    with sub_tab1:
        st.markdown("#### 🧭 जीवन के ५० आयाम चयन (Select Life Dimension)")

        # Category Filter & Dimension Dropdown
        categories = sorted(list(set(d["category"] for d in LIFE_DIMENSIONS_50)))
        all_cat_label = "📁 समस्त ५० आयाम (All 50 Dimensions)"
        cat_choices = [all_cat_label] + categories

        c_col1, c_col2 = st.columns([1.5, 2.5])
        with c_col1:
            selected_cat = st.selectbox("📂 श्रेणी फ़िल्टर (Category Filter):", cat_choices, key="faladesh_dim_cat_filter")

        if selected_cat == all_cat_label:
            avail_dims = LIFE_DIMENSIONS_50
        else:
            avail_dims = [d for d in LIFE_DIMENSIONS_50 if d["category"] == selected_cat]

        dim_names = [f"{d['id']}. {d['name_hi']}" for d in avail_dims]
        with c_col2:
            chosen_dim_str = st.selectbox("🎯 सक्रिय आयाम चुनें (Choose Dimension):", dim_names, key="faladesh_chosen_dim_select")

        # Get chosen dimension object
        chosen_dim_id = int(chosen_dim_str.split(".")[0])
        synth = default_shastriya_faladesh_engine.synthesize_dimension(chart, chosen_dim_id, birth_profile)
        dim = synth["dimension"]

        # Hero Card for Selected Dimension
        pos_pct = synth["positive_pct"]
        neg_pct = synth["negative_pct"]
        v_badge = synth["verdict_badge"]
        v_color = synth["verdict_color"]

        st.markdown(f"""
        <div style="background:{card_bg}; border:1.5px solid {card_bdr}; border-radius:12px; padding:18px 20px; box-shadow:0 4px 14px rgba(0,0,0,0.06); margin:12px 0;">
            <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px;">
                <div>
                    <div style="font-size:12px; font-weight:700; color:{gold_color}; text-transform:uppercase; letter-spacing:1px;">
                        आयाम #{dim['id']} • {dim['category']}
                    </div>
                    <div style="font-size:22px; font-weight:900; color:{text_main}; margin-top:2px;">
                        {dim['name_hi']}
                    </div>
                    <div style="font-size:12.5px; color:{text_sub}; margin-top:4px;">
                        {dim['desc']}
                    </div>
                </div>
                <div style="text-align:right;">
                    <div style="font-size:11px; font-weight:700; color:{text_sub};">शास्त्रीय निर्णय</div>
                    <div style="background:{v_color}1A; border:1.5px solid {v_color}; color:{v_color}; border-radius:8px; padding:5px 12px; font-size:13px; font-weight:900; margin-top:3px;">
                        {v_badge}
                    </div>
                </div>
            </div>
            <div style="margin-top:16px;">
                <div style="display:flex; justify-content:space-between; font-size:12px; font-weight:800; margin-bottom:5px;">
                    <span style="color:{green_color};">🟢 सकारात्मक अनुकूलता: {pos_pct}%</span>
                    <span style="color:{red_color};">🔴 सावधानी / बाधक तत्व: {neg_pct}%</span>
                </div>
                <div style="display:flex; height:12px; border-radius:6px; overflow:hidden; border:1px solid {card_bdr}; background:#F1F5F9;">
                    <div style="width:{pos_pct}%; background:linear-gradient(90deg, #10B981, #059669);"></div>
                    <div style="width:{neg_pct}%; background:linear-gradient(90deg, #F87171, #DC2626);"></div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Mathematical Evidence Tables
        st.markdown("##### 📊 सक्रिय कुण्डली गणितीय साक्ष्य सारणी (Active Kundali Mathematical Evidence)")
        
        tab_ev1, tab_ev2 = st.columns(2)
        with tab_ev1:
            st.markdown("**🏰 संबंधित भाव, भावबल एवं अष्टकवर्ग (Houses & SAV):**")
            h_rows = []
            for h in synth["houses_data"]:
                h_rows.append({
                    "भाव": f"{h['house']}वां भाव",
                    "राशि": f"{h['sign_name']} ({h['sign_id']})",
                    "स्वामी": PLANET_NAMES_HI.get(h["lord"], h["lord"]),
                    "SAV बिन्दु": f"{h['sav']} अंक",
                    "भावबल": f"{h['bhavabala']} विरूपा",
                    "स्थित ग्रह": ", ".join([PLANET_NAMES_HI.get(p, p) for p in h["occupants"]]) if h["occupants"] else "—"
                })
            st.dataframe(h_rows, use_container_width=True, hide_index=True)

        with tab_ev2:
            st.markdown("**🪐 नैसर्गिक कारक ग्रह, अंश व अवस्था (Karaka Planets & Degrees):**")
            p_rows = []
            for p in synth["planets_data"]:
                comb_str = "🔥 अस्त" if p["is_combust"] else ("⚡ वक्री" if p["is_retrograde"] else "मार्गी")
                p_rows.append({
                    "ग्रह": p["planet_hi"],
                    "अंश": f"{p['degree']}°",
                    "नक्षत्र व पद": f"{p['nakshatra']} (पद {p['pada']})",
                    "गरिमा (Dignity)": p["dignity"].split(" ")[0],
                    "अवस्था": p["baladi"].split(" ")[0],
                    "षड्बल अनुपात": f"{p['shadbala_ratio']:.2f}",
                    "स्थिति": comb_str
                })
            st.dataframe(p_rows, use_container_width=True, hide_index=True)

        # Honest Positives vs Negatives Scriptural Analysis
        st.markdown("##### ⚖️ पूर्ण ईमानदारी से शास्त्रीय विश्लेषण (Honest Shastriya Balance Sheet)")
        col_pos, col_neg = st.columns(2)

        with col_pos:
            st.markdown(f"""
            <div style="background:{green_color}10; border:1.5px solid {green_color}50; border-radius:10px; padding:14px; height:100%;">
                <div style="font-size:14px; font-weight:800; color:{green_color}; margin-bottom:8px;">
                    🟢 सकारात्मक शास्त्रीय पक्ष (Favorable Factors)
                </div>
                <ul style="margin:0; padding-left:18px; color:{text_main}; font-size:12.5px; line-height:1.6;">
                    {''.join([f'<li style="margin-bottom:6px;">{p}</li>' for p in synth['positives']]) if synth['positives'] else '<li>सामान्य ग्रह स्थिति संतुलित है।</li>'}
                </ul>
            </div>
            """, unsafe_allow_html=True)

        with col_neg:
            st.markdown(f"""
            <div style="background:{red_color}10; border:1.5px solid {red_color}50; border-radius:10px; padding:14px; height:100%;">
                <div style="font-size:14px; font-weight:800; color:{red_color}; margin-bottom:8px;">
                    🔴 बाधक तत्व एवं सावधानियां (Challenging / Cautionary Factors)
                </div>
                <ul style="margin:0; padding-left:18px; color:{text_main}; font-size:12.5px; line-height:1.6;">
                    {''.join([f'<li style="margin-bottom:6px;">{n}</li>' for n in synth['negatives']]) if synth['negatives'] else '<li>कोई गंभीर शास्त्रीय दोष उपस्थित नहीं है।</li>'}
                </ul>
            </div>
            """, unsafe_allow_html=True)

        # Scriptural Citations & Prescribed Remedies
        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
        col_cite, col_rem = st.columns([1.3, 1])

        with col_cite:
            st.markdown(f"""
            <div style="background:{card_bg}; border:1px solid {card_bdr}; border-left:4px solid {gold_color}; border-radius:8px; padding:12px 16px;">
                <div style="font-size:13px; font-weight:800; color:{gold_color}; margin-bottom:6px;">
                    📜 शास्त्रीय ग्रन्थ प्रमाण (Canonical Sutra Citations)
                </div>
                <div style="font-size:12px; color:{text_main}; line-height:1.6;">
                    {'<br/><br/>'.join(synth['citations'])}
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col_rem:
            rem = synth["remedies"]
            st.markdown(f"""
            <div style="background:{card_bg}; border:1px solid {card_bdr}; border-left:4px solid {blue_color}; border-radius:8px; padding:12px 16px;">
                <div style="font-size:13px; font-weight:800; color:{blue_color}; margin-bottom:6px;">
                    🪔 विशेष वैदिक शांति उपाय (Prescribed Remedies)
                </div>
                <div style="font-size:12px; color:{text_main}; line-height:1.6;">
                    • <b>मंत्र:</b> {rem['mantra']}<br/>
                    • <b>रत्न/रुद्राक्ष:</b> {rem['gemstone']}<br/>
                    • <b>दान:</b> {rem['charity']}<br/>
                    • <b>उपासना:</b> {rem['deity']}
                </div>
            </div>
            """, unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # TAB 2: 100 QUERENT FAQS ENGINE
    # -------------------------------------------------------------------------
    with sub_tab2:
        st.markdown("#### ❓ १०० जातक शास्त्रीय प्रश्न-उत्तर इंजन (100 Querent FAQs Engine)")
        st.caption("जातक द्वारा पूछे जाने वाले १०० वास्तविक प्रश्नों में से किसी भी प्रश्न का चयन करें। प्रणाली सक्रिय कुण्डली के समस्त गणना सारणियों के आधार पर तात्कालिक उत्तर प्रस्तुत करेगी:")

        # Dimension selector for FAQ
        f_dim_choices = [f"{d['id']}. {d['name_hi']}" for d in LIFE_DIMENSIONS_50]
        f_chosen_dim_str = st.selectbox("🎯 प्रश्न हेतु जीवन आयाम चुनें (Choose Dimension for FAQ):", f_dim_choices, key="faladesh_faq_dim_select")
        f_dim_id = int(f_chosen_dim_str.split(".")[0])

        f_synth = default_shastriya_faladesh_engine.synthesize_dimension(chart, f_dim_id, birth_profile)
        faqs = f_synth["faqs_100"]

        # Search or filter FAQs
        search_query = st.text_input("🔍 प्रश्न खोजें (Search Question):", placeholder="कब, विवाह, सरकारी नौकरी, विदेश, संतान, व्यापार, रोग...", key="faladesh_faq_search").strip().lower()

        if search_query:
            matched_faqs = [f for f in faqs if search_query in f["question"].lower() or search_query in f["theme"].lower()]
        else:
            matched_faqs = faqs

        if not matched_faqs:
            st.warning("कोई प्रश्न नहीं मिला। कृपया अन्य शब्द लिखकर खोजें।")
            matched_faqs = faqs

        # FAQ Dropdown
        faq_options = [f"#{f['num']}. [{f['theme']}] {f['question']}" for f in matched_faqs]
        selected_faq_str = st.selectbox(f"📋 उपलब्ध प्रश्न ({len(matched_faqs)} प्रश्न उपलब्ध):", faq_options, key="faladesh_active_faq_select")

        # Get chosen FAQ number
        chosen_faq_num = int(selected_faq_str.split(".")[0].replace("#", ""))
        faq_ans = default_shastriya_faladesh_engine.answer_specific_faq(chart, f_dim_id, chosen_faq_num, birth_profile)

        # Render Dynamic FAQ Answer Card
        st.markdown(f"""
        <div style="background:{card_bg}; border:2px solid {gold_color}; border-radius:12px; padding:20px 24px; box-shadow:0 6px 20px rgba(0,0,0,0.08); margin:14px 0;">
            <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px; margin-bottom:12px;">
                <div style="font-size:12px; font-weight:700; color:{blue_color}; text-transform:uppercase;">
                    प्रश्न #{faq_ans['faq_num']} • {faq_ans['theme']}
                </div>
                <div style="display:flex; gap:8px;">
                    <span style="background:{green_color}20; border:1px solid {green_color}; color:{green_color}; font-size:11.5px; font-weight:800; border-radius:6px; padding:2px 8px;">
                        सकारात्मक सम्भावना: {faq_ans['positive_pct']}%
                    </span>
                    <span style="background:{red_color}20; border:1px solid {red_color}; color:{red_color}; font-size:11.5px; font-weight:800; border-radius:6px; padding:2px 8px;">
                        बाधक सम्भावना: {faq_ans['negative_pct']}%
                    </span>
                </div>
            </div>
            <div style="font-size:18px; font-weight:900; color:{gold_color}; line-height:1.4; margin-bottom:14px;">
                ❓ {faq_ans['question']}
            </div>
            <div style="background:rgba(245, 158, 11, 0.05); border-left:4px solid {gold_color}; border-radius:6px; padding:12px 16px; margin-bottom:14px; font-size:13px; color:{text_main}; line-height:1.7;">
                {faq_ans['full_answer_md'].replace(chr(10), '<br/>')}
            </div>
            <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap:12px; margin-top:14px;">
                <div style="background:rgba(37, 99, 235, 0.05); border:1px solid {blue_color}40; border-radius:8px; padding:10px 14px;">
                    <div style="font-size:11.5px; font-weight:800; color:{blue_color}; margin-bottom:4px;">⏱️ सक्रिय दशा कालक्रम</div>
                    <div style="font-size:12px; color:{text_main};">
                        <b>महादशा:</b> {PLANET_NAMES_HI.get(faq_ans['active_dasha']['mahadasha'], faq_ans['active_dasha']['mahadasha'])}<br/>
                        <b>अंतर्दशा:</b> {PLANET_NAMES_HI.get(faq_ans['active_dasha']['antardasha'], faq_ans['active_dasha']['antardasha'])}<br/>
                        <b>प्रत्यंतर:</b> {PLANET_NAMES_HI.get(faq_ans['active_dasha']['pratyantardasha'], faq_ans['active_dasha']['pratyantardasha'])}
                    </div>
                </div>
                <div style="background:rgba(16, 185, 129, 0.05); border:1px solid {green_color}40; border-radius:8px; padding:10px 14px;">
                    <div style="font-size:11.5px; font-weight:800; color:{green_color}; margin-bottom:4px;">🪔 अनुशंसित वैदिक उपाय</div>
                    <div style="font-size:12px; color:{text_main};">
                        <b>जप:</b> {faq_ans['remedies']['mantra']}<br/>
                        <b>दान:</b> {faq_ans['remedies']['charity']}
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # TAB 3: ALL CALCULATIONS MATRIX
    # -------------------------------------------------------------------------
    with sub_tab3:
        st.markdown("#### 🔬 सर्व-गणना संश्लेषण (All Calculations Matrix)")
        st.caption("सक्रिय कुण्डली के समस्त १२ भावों एवं ९ ग्रहों का पूर्ण तकनीकी एवं शास्त्रीय विवरण:")

        col_t1, col_t2 = st.tabs(["🏰 द्वादश भाव विस्तृत सारणी (12 Houses)", "🪐 नवग्रह स्पष्ट व बल सारणी (9 Planets)"])

        with col_t1:
            all_h_rows = []
            sav_l = chart.ashtakavarga.sav if (chart.ashtakavarga and hasattr(chart.ashtakavarga, "sav")) else []
            b_bala = chart.shadbala.bhava_bala if (chart.shadbala and hasattr(chart.shadbala, "bhava_bala")) else {}

            for h in chart.houses:
                s_id = h.sign_id
                s_pts = sav_l[s_id - 1] if (sav_l and 1 <= s_id <= len(sav_l)) else 28
                bb_val = b_bala.get(h.house_number, 200.0)
                occ = ", ".join([PLANET_NAMES_HI.get(p, p) for p in h.occupants]) if h.occupants else "रिक्त"
                all_h_rows.append({
                    "भाव": f"भाव {h.house_number}",
                    "राशि": f"{h.sign_name} ({s_id})",
                    "भावाधिपति": PLANET_NAMES_HI.get(h.lord, h.lord),
                    "भाव कस्प अंश": f"{h.cusp_longitude % 30:.2f}°",
                    "SAV बिन्दु": f"{s_pts} pt",
                    "भावबल (Virupas)": f"{bb_val:.1f}",
                    "स्थित ग्रह": occ
                })
            st.dataframe(all_h_rows, use_container_width=True, hide_index=True)

        with col_t2:
            all_p_rows = []
            p_shads = chart.shadbala.planets if (chart.shadbala and hasattr(chart.shadbala, "planets")) else {}

            for p_name, p in chart.planets.items():
                p_sh = p_shads.get(p_name)
                vir = getattr(p_sh, "total_virupas", 350.0) if p_sh else 350.0
                rat = getattr(p_sh, "strength_ratio", vir / 330.0) if p_sh else (vir / 330.0)
                if rat is None:
                    rat = vir / 330.0

                is_odd = (p.sign_id % 2 != 0)
                av = default_shastriya_faladesh_engine.evaluate_planet_avashtha(p_name, p.sign_degree, is_odd)
                st_flag = "🔥 अस्त" if p.is_combust else ("⚡ वक्री" if p.is_retrograde else "मार्गी")

                all_p_rows.append({
                    "ग्रह": PLANET_NAMES_HI.get(p_name, p_name),
                    "राशि": p.sign_name,
                    "अंश": f"{p.sign_degree:.2f}°",
                    "नक्षत्र": f"{p.nakshatra_name} ({p.nakshatra_pada})",
                    "नक्षत्र स्वामी": PLANET_NAMES_HI.get(p.nakshatra_lord, p.nakshatra_lord),
                    "भाव (Lagna)": f"{p.house_from_lagna}",
                    "भाव (Moon)": f"{p.house_from_moon}",
                    "गरिमा": p.dignity or "सम",
                    "अवस्था": av["baladi"].split(" ")[0],
                    "षड्बल (विरूपा)": f"{vir:.1f}",
                    "अनुपात": f"{rat:.2f}",
                    "गति": st_flag
                })
            st.dataframe(all_p_rows, use_container_width=True, hide_index=True)

    # -------------------------------------------------------------------------
    # TAB 4: SCRIPTURAL PRAMANA & UNIVERSAL REMEDIES
    # -------------------------------------------------------------------------
    with sub_tab4:
        st.markdown("#### 📜 शास्त्रीय साक्ष्य, ग्रन्थ प्रमाण व उपाय (Pramana & Remedies)")
        
        st.markdown(f"""
        <div style="background:{card_bg}; border:1px solid {card_bdr}; border-radius:10px; padding:18px 20px; margin-bottom:14px;">
            <h4 style="color:{gold_color}; margin-top:0;">📚 बृहत्पाराशर होराशास्त्र (BPHS) के आधारभूत नियम</h4>
            <p style="font-size:13px; line-height:1.7; color:{text_main};">
                <b>१. भावाधिपति एवं कारक समन्वय:</b> भावे यद्भावे स्थितो वा पश्यति वा शुभाशुभः। तद्भावस्य फलं ब्रूयात् कारकाणां बलेन च॥<br/>
                अर्थात् जिस भाव पर शुभ ग्रहों की दृष्टि अथवा युति हो और उसका कारक ग्रह षड्बल में सामर्थ्यवान हो, उस भाव के फलों की पूर्ण वृद्धि होती है।
            </p>
            <p style="font-size:13px; line-height:1.7; color:{text_main};">
                <b>२. अष्टकवर्ग बिन्दु सिद्धांत (SAV):</b> अष्टविंशति (२८) बिन्दवः समं प्रोक्ताः। ततोऽधिकाः शुभप्रदाः हीनाश्चेत् कष्टदायकाः॥<br/>
                २८ बिंदु मध्यम, २८ से अधिक बिंदु अत्यंत कल्याणकारी व कार्य सिद्धिकारक, तथा २५ से कम बिंदु वाले भावों में विशेष परिश्रम व शांति अनिवार्य है।
            </p>
            <p style="font-size:13px; line-height:1.7; color:{text_main};">
                <b>३. षोडशवर्ग सूक्ष्म प्रभाव (D1 to D60):</b> राशिचक्रं स्थूलदेहं नवांशो धर्म-भाग्ययोः। दशमांशे महत्कार्यं षष्ट्यंशे पूर्वसञ्चितम्॥<br/>
                लग्न कुण्डली स्थूल शरीर व सामान्य जीवन को दर्शाती है, नवांश (D9) आंतरिक बल व धर्म-दांपत्य को, दशमांश (D10) आजीविका व प्रतिष्ठा को, तथा षष्ट्यंश (D60) पूर्व संचित प्रारब्ध को प्रकट करता है।
            </p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("##### 🪔 पंच-सूत्रीय वैदिक शांति विधान (5-Fold Remedial Protocol)")
        rem1, rem2, rem3 = st.columns(3)
        with rem1:
            st.info("🧘 **१. नित्य मंत्र जप:**\n\nइष्टदेवता अथवा लग्नेश के वैदिक/तांत्रिक बीज मंत्र का नित्य १०८ बार प्रातःकाल जप मानसिक व आध्यात्मिक सुरक्षा प्रदान करता है।")
        with rem2:
            st.success("💎 **२. शास्त्रोक्त रत्न/रुद्राक्ष:**\n\nकेवल योगकारक व अनुकूल ग्रहों के ही रत्न धारण करें। मारक या अष्टमेश के रत्न कदापि धारण न करें।")
        with rem3:
            st.warning("🌾 **३. सुपात्र दान एवं सेवा:**\n\nपीड़क अथवा नीच ग्रहों के शमन हेतु उनके संबंधित वार को अन्न, गौग्रास, वस्त्र एवं छायादान सर्वश्रेष्ठ शांति विधान है।")
