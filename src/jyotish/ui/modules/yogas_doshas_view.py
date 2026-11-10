# -*- coding: utf-8 -*-
"""
Module 20: Yogas & Doshas Analysis and Specific Shastriya Remedies View.
Evaluates classical rules, identifies active and inactive afflictions (Doshas) and blessings (Yogas),
provides full 12,500 rule evidence scan, and matches targeted Vedic remedies.
"""

import streamlit as st
import pandas as pd
from datetime import datetime, date
from typing import List, Optional
from src.jyotish.core.constants import SIGN_NAMES
import src.jyotish.rules.engine as r_mod
import src.jyotish.dasha.vimshottari as vim_mod
import src.jyotish.core.gochar as goc_mod

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

NATURAL_SWABHAV = {
    "Sun": "नैसर्गिक क्रूर / आत्मा कारक",
    "Moon": "नैसर्गिक शुभ / मन कारक",
    "Mars": "नैसर्गिक क्रूर / पराक्रम कारक",
    "Mercury": "नैसर्गिक शुभ / बुद्धि कारक",
    "Jupiter": "नैसर्गिक परम शुभ / ज्ञान कारक",
    "Venus": "नैसर्गिक शुभ / सुख-कला कारक",
    "Saturn": "नैसर्गिक मंद-क्रूर / कर्म व न्याय कारक",
    "Rahu": "छाया ग्रह / तमोगुणी कारक",
    "Ketu": "छाया ग्रह / मोक्ष कारक"
}

BPHS_YOGA_SHLOKA = {
    "title": "बृहत्पाराशर होराशास्त्र एवं फलदीपिका — योगकारक व दोष शांति विचार",
    "source": "महर्षि पराशर विरचित 'बृहत्पाराशर होराशास्त्रम्' (योगकारकाध्याय) एवं मन्त्रेश्वर विरचित 'फलदीपिका' (अध्याय ६)",
    "shloka": "केन्द्रत्रिकोणपतयः परस्परमथापि वा ।\nसम्बन्धमात्रेणैव स्याद्योगोऽयं राजयोगकृत् ॥\nयद्यद्भावे स्थितो मन्दः कुजो वा राहुसंयुतः ।\nतत्तद्भावफलं हन्ति शान्त्या शुभत्वमाप्नुयात् ॥",
    "meaning": "केन्द्र एवं त्रिकोण के स्वामियों का परस्पर संबंध राजयोग का निर्माण करता है; जबकि अशुभ व क्रूर ग्रहों की युति अथवा दृष्टि से उत्पन्न होने वाले भाव दोषों का शमन शास्त्रोक्त जप, तप, दान व सात्विक आचरण से होकर शुभत्व की प्राप्ति होती है।"
}


def _format_dms(deg_val):
    deg = float(deg_val) if deg_val is not None else 0.0
    ansh = int(deg)
    kala = int(round((deg - ansh) * 60.0))
    if kala >= 60:
        kala = 0
        ansh += 1
    return ansh, kala, f"{ansh}° {kala:02d}'"


# Specific Remedial Mapping Database per Dosha / Affliction
REMEDY_MAP = {
    "BPHS_KAAL_SARPA_DOSHA": {
        "title": "काल सर्प दोष निवारण",
        "vedic_mantra": "ॐ नमः शिवाय | महामृत्युंजय मंत्र",
        "remedy": "सोमवार को शिवलिंग पर कच्चा दूध, बेलपत्र एवं चाँदी के नाग-नागिन का जोड़ा अर्पित करें। नागपंचमी पर रुद्राभिषेक कराएं।",
        "gem_color": "चाँदी का कड़ा / गोमेद एवं लहसुनिया केवल विद्वान ज्योतिषी के परामर्श से",
        "dan": "काले-सफेद कंबल, तिल, उड़द का दान शनिवार को करें।",
        "precaution": "पक्षियों को दाना डालें, साँपों को कभी न सताएं या मारें।"
    },
    "BPHS_MANGAL_DOSHA_VIVAH": {
        "title": "मांगलिक दोष शांति उपाय",
        "vedic_mantra": "ॐ अं अंगारकाय नमः | हनुमान चालीसा / सुंदरकांड",
        "remedy": "नित्य अथवा प्रत्येक मंगलवार को श्री हनुमान चालीसा या बजरंग बाण का पाठ करें। कुंभ विवाह / अर्क विवाह शास्त्रोक्त विधि से संभव है।",
        "gem_color": "लाल मूंगा (यदि मंगल योगकारक हो) अथवा ताम्बे का कड़ा धारण करें।",
        "dan": "गुड़, मसूर दाल, लाल वस्त्र अथवा तांबे के पात्र का दान करें।",
        "precaution": "क्रोध, जल्दबाजी और कटु वचनों से बचें, विशेषकर वैवाहिक वार्ता में।"
    },
    "BPHS_PITRA_DOSHA": {
        "title": "पितृ दोष निवारण उपाय",
        "vedic_mantra": "ॐ पितृभ्यो नमः | पितृ गायत्री मंत्र",
        "remedy": "अमावस्या को पितरों के निमित्त तर्पण, पिंडदान अथवा ब्राह्मण भोजन कराएं। पीपल के वृक्ष में जल अर्पित कर दीप प्रज्वलित करें।",
        "gem_color": "सूर्य देव को नित्य तांबे के लोटे से रोली-अक्षत मिलाकर अर्घ्य दें।",
        "dan": "अमावस्या को खीर, अन्न, वस्त्र और छाता जरूरतमंदों को दान करें।",
        "precaution": "माता-पिता एवं परिवार के वृद्धजनों का सदैव सम्मान व सेवा करें।"
    },
    "BPHS_KEMADRUMA_DOSHA": {
        "title": "केमद्रुम दोष (मानसिक अस्थिरता) उपाय",
        "vedic_mantra": "ॐ सों सोमाय नमः | श्री सूक्तम",
        "remedy": "पूर्णिमा का व्रत रखें, माता का चरण स्पर्श कर आशीर्वाद लें। भगवान शिव का जलाभिषेक करें।",
        "gem_color": "चाँदी के पात्र में जल पीने का नियम बनाएं, कनिष्ठिका में चाँदी की अंगूठी पहनें।",
        "dan": "दूध, चावल, मिश्री, चीनी अथवा सफेद वस्त्र का सोमवार को दान।",
        "precaution": "अकेलेपन व नकारात्मक विचारों से दूर रहें, नित्य ध्यान (Meditation) करें।"
    },
    "GOCHARA_SHANI_SADE_SATI": {
        "title": "शनि साढ़ेसाती एवं ढैया रक्षा कवच",
        "vedic_mantra": "ॐ प्रां प्रीं प्रौं सः शनैश्चराय नमः | दशरथ कृत शनि स्तोत्र",
        "remedy": "शनिवार को पीपल के नीचे सरसों के तेल का दीपक जलाएं। नित्य हनुमान चालीसा का पाठ करें।",
        "gem_color": "लोहे का छल्ला (काले घोड़े की नाल का) मध्यमा अंगुली में शनिवार को पहनें।",
        "dan": "काले तिल, उड़द की दाल, सरसों का तेल, चमड़े के जूते अथवा लोहा दान करें।",
        "precaution": "मदिरा, जुआ, असत्य भाषण व कर्मचारियों/मजदूरों का अहित कभी न करें।"
    },
    "GOCHARA_SHANI_DHAIYA": {
        "title": "शनि ढैया शांति उपाय",
        "vedic_mantra": "ॐ शं शनैश्चराय नमः",
        "remedy": "शनिवार को हनुमान मंदिर में सिंदूर व चमेली का तेल चढ़ाएं। सुंदरकांड का पाठ करें।",
        "gem_color": "शनि यंत्र की स्थापना कर धूप-दीप दें।",
        "dan": "गरीबों को भोजन अथवा सरसों के तेल में छाया दान करें।",
        "precaution": "आलस्य से बचें और समय का सदुपयोग करें।"
    },
    "GOCHARA_GURU_CHANDAL_YOG": {
        "title": "गुरु-चांडाल दोष निवारण",
        "vedic_mantra": "ॐ बृं बृहस्पतये नमः | विष्णु सहस्रनाम",
        "remedy": "गुरुवार को भगवान विष्णु की पूजा करें, केले के पेड़ में जल दें, गाय को गुड़-चना खिलाएं।",
        "gem_color": "पुखराज अथवा सुनहला (विद्वान परामर्श से) या हल्दी की गांठ बांधें।",
        "dan": "पीले वस्त्र, चने की दाल, हल्दी, बेसन के लड्डू व धार्मिक पुस्तकें दान करें।",
        "precaution": "गुरु, शिक्षक और ज्ञानियों का उपहास न उड़ाएं।"
    },
    "BPHS_RUDRA_YOGA_MARS_AFFLICTED": {
        "title": "रुद्र योग / अंगारक योग शांति",
        "vedic_mantra": "ॐ रुद्राय नमः | महामृत्युंजय मंत्र",
        "remedy": "भगवान कार्तिकेय अथवा भैरव जी की आराधना करें। शिवलिंग पर गन्ने का रस या शहद अर्पित करें।",
        "gem_color": "चांदी में जड़ा मूंगा अथवा लाल चंदन का टीका लगाएं।",
        "dan": "तांबा, मसूर, लाल मिठाई और रक्तदान करें।",
        "precaution": "अग्नि, वाहन और धारदार हथियारों के प्रयोग में सदैव सावधानी रखें।"
    }
}


def render_yogas_doshas_view(chart, tabs: Optional[List[str]] = None):
    if tabs is None:
        tabs = [
            "🔴 सक्रिय दोष एवं कुण्डली वेध",
            "🟢 राजयोग, धनयोग व महापुरुष योग",
            "📋 १२,५०० महा-शास्त्रीय नियम स्कैन",
            "💊 कुण्डली-आधारित विशिष्ट उपाय"
        ]
    st.subheader("⚡ सम्पूर्ण दोष एवं योग विश्लेषण एवं कुण्डली आधारित उपाय")
    st.caption("बृहत्पाराशर होराशास्त्र, फलदीपिका, सारावली एवं जातक पारिजात अनुसार कुण्डली के समस्त सक्रिय/निष्क्रिय दोषों, राजयोगों, धनयोगों तथा कुण्डली-आधारित अचूक उपायों का पूर्ण विश्लेषण।")

    # 1. Classical Shastriya Shloka Card
    with st.expander(f"📜 शास्त्रीय प्रमाण — {BPHS_YOGA_SHLOKA['title']}", expanded=False):
        st.markdown(f"""
        <div style="background:#FFFBEB; border-left:4px solid #D97706; padding:12px; border-radius:6px; margin-bottom:10px;">
            <b style="color:#B45309; font-size:15px;">📖 ग्रंथ संदर्भ: {BPHS_YOGA_SHLOKA['source']}</b>
            <pre style="white-space:pre-wrap; font-family:serif; font-size:14px; color:#78350F; margin:8px 0; background:transparent; border:none; padding:0;">
{BPHS_YOGA_SHLOKA['shloka']}
            </pre>
            <div style="font-size:13px; color:#92400E; margin-top:6px;">
                <b>हिंदी भावार्थ:</b> {BPHS_YOGA_SHLOKA['meaning']}
            </div>
        </div>
        """, unsafe_allow_html=True)

    # 2. Compute Active Dasha & Transit Context required by the Rules Library
    try:
        _eval_date = date.today()
        _full_bdt = datetime.combine(chart.birth_data.birth_date, chart.birth_data.birth_time)
        _moon_lon = chart.planets["Moon"].longitude
        _active_dasha = vim_mod.default_dasha_engine.get_active_dasha_at(_full_bdt, _moon_lon, _eval_date)
        _transits, _tr_summary = goc_mod.default_transit_engine.compute_transit_snapshot(chart, _eval_date, chart.ayanamsa_name)

        _evidences = r_mod.default_rules_engine.evaluate_all(
            chart=chart,
            active_dasha=_active_dasha,
            transits=_transits,
            transit_summary=_tr_summary
        )
    except Exception as _r_err:
        _evidences = []
        st.warning(f"नियम मूल्यांकन प्रणाली सूचना: {_r_err}")

    # Categorize Evidences into Doshas (Negative Polarity) and Yogas (Positive Polarity)
    _doshas_ev = [e for e in _evidences if e.polarity == '-']
    _yogas_ev = [e for e in _evidences if e.polarity == '+']

    _active_doshas = [e for e in _doshas_ev if e.fired]
    _active_yogas = [e for e in _yogas_ev if e.fired]

    # 3. Active Native Micro Planetary HUD Console
    if chart is not None:
        l_deg = getattr(chart, "lagna_degree", 0.0)
        _, _, l_dms = _format_dms(l_deg)
        l_sign = getattr(chart, "lagna_sign", 1)
        l_sign_name = SIGN_NAMES[l_sign - 1] if 1 <= l_sign <= 12 else f"Sign {l_sign}"

        moon = chart.planets.get("Moon") if hasattr(chart, "planets") else None
        if moon:
            m_deg = getattr(moon, "sign_degree", 0.0)
            _, _, m_dms = _format_dms(m_deg)
            m_nak = getattr(moon, "nakshatra_name", getattr(moon, "nakshatra", "—"))
            m_pada = getattr(moon, "nakshatra_pada", getattr(moon, "pada", 1))
            m_sign = getattr(moon, "sign_id", getattr(moon, "sign", 1))
            m_sign_name = SIGN_NAMES[m_sign - 1] if 1 <= m_sign <= 12 else f"Sign {m_sign}"
        else:
            m_dms, m_nak, m_pada, m_sign_name = "—", "—", 1, "—"

        st.markdown(f"""
        <div style="background:linear-gradient(135deg, #1E1B4B 0%, #312E81 100%); color:#FFFFFF; border-radius:10px; padding:14px 18px; margin-bottom:12px; box-shadow:0 4px 6px -1px rgba(0,0,0,0.1);">
            <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; margin-bottom:8px;">
                <span style="font-size:16px; font-weight:700;">🪐 सक्रिय जातक योग-दोष वेध: <span style="color:#FDE047;">{getattr(chart, 'name', 'सक्रिय कुण्डली')}</span></span>
                <span style="font-size:13px; color:#C7D2FE;">🏛️ लग्न: <b>{l_sign_name} ({l_dms})</b> | 🌙 चंद्र: <b>{m_sign_name} ({m_dms})</b> | 🌟 <b>{m_nak} (पद {m_pada})</b></span>
            </div>
            <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(130px, 1fr)); gap:10px; font-size:12.5px; text-align:center;">
                <div style="background:rgba(255,255,255,0.08); padding:8px; border-radius:6px; border:1px solid rgba(255,255,255,0.15);">
                    <div style="color:#FCA5A5; font-size:11px;">⚠️ सक्रिय दोष</div>
                    <div style="font-size:16px; font-weight:700; color:#F87171;">{len(_active_doshas)}</div>
                    <div style="font-size:10px; color:#FECACA;">{len(_active_doshas) and 'सावधानी व शांति' or 'सुरक्षित / निर्दोष'}</div>
                </div>
                <div style="background:rgba(255,255,255,0.08); padding:8px; border-radius:6px; border:1px solid rgba(255,255,255,0.15);">
                    <div style="color:#86EFAC; font-size:11px;">✨ सक्रिय शुभ योग</div>
                    <div style="font-size:16px; font-weight:700; color:#4ADE80;">{len(_active_yogas)}</div>
                    <div style="font-size:10px; color:#BBF7D0;">राजयोग व धनयोग</div>
                </div>
                <div style="background:rgba(255,255,255,0.08); padding:8px; border-radius:6px; border:1px solid rgba(255,255,255,0.15);">
                    <div style="color:#93C5FD; font-size:11px;">📋 मूल्यांकित नियम</div>
                    <div style="font-size:16px; font-weight:700; color:#FFFFFF;">{len(_evidences):,}</div>
                    <div style="font-size:10px; color:#C7D2FE;">१६+ महा-ग्रन्थ</div>
                </div>
                <div style="background:rgba(255,255,255,0.08); padding:8px; border-radius:6px; border:1px solid rgba(255,255,255,0.15);">
                    <div style="color:#FDE047; font-size:11px;">💊 कुण्डली उपाय</div>
                    <div style="font-size:16px; font-weight:700; color:#FEF08A;">{len(_active_doshas) + (1 if not _active_doshas else 0)}</div>
                    <div style="font-size:10px; color:#FEF9C3;">वैदिक शांति विधान</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Micro Planetary Status Grid Expander
        with st.expander("🪐 सक्रिय जातक सूक्ष्म ग्रह-स्थिति (अंश, कला, नक्षत्र, चरण व स्वभाव)", expanded=False):
            planets_data = []
            if hasattr(chart, "planets") and isinstance(chart.planets, dict):
                for p_name, p_obj in chart.planets.items():
                    if p_name in ["Uranus", "Neptune", "Pluto"]:
                        continue
                    p_hi = GRAHA_NAMES_HI.get(p_name, p_name)
                    s_id = getattr(p_obj, "sign_id", getattr(p_obj, "sign", 1))
                    s_name = SIGN_NAMES[s_id - 1] if 1 <= s_id <= 12 else f"Sign {s_id}"
                    deg = getattr(p_obj, "sign_degree", 0.0)
                    _, _, dms_str = _format_dms(deg)
                    nak = getattr(p_obj, "nakshatra_name", getattr(p_obj, "nakshatra", "—"))
                    pada = getattr(p_obj, "nakshatra_pada", getattr(p_obj, "pada", 1))
                    house = getattr(p_obj, "house_from_lagna", getattr(p_obj, "house", "—"))
                    dignity_raw = getattr(p_obj, "dignity", "neutral")
                    dignity_hi = DIGNITY_HI.get(str(dignity_raw).lower(), str(dignity_raw))
                    is_retro = getattr(p_obj, "is_retrograde", False)
                    is_comb = getattr(p_obj, "is_combust", False)
                    swabhav = NATURAL_SWABHAV.get(p_name, "सामान्य")

                    status_tags = []
                    if is_retro:
                        status_tags.append("🔄 वक्री")
                    if is_comb:
                        status_tags.append("🔥 अस्त")
                    tag_str = f" ({', '.join(status_tags)})" if status_tags else ""

                    planets_data.append({
                        "ग्रह": f"{p_hi} ({p_name})",
                        "भाव": f"भाव {house}",
                        "राशि": s_name,
                        "अंश-कला (DMS)": dms_str,
                        "नक्षत्र व चरण": f"{nak} (पद {pada})",
                        "अवस्था (Dignity)": f"{dignity_hi}{tag_str}",
                        "नैसर्गिक स्वभाव": swabhav
                    })
            if planets_data:
                st.dataframe(pd.DataFrame(planets_data), use_container_width=True, hide_index=True)

    # 4. Polarity Balance & Shastriya Synthesis Card
    net_balance = len(_active_yogas) - len(_active_doshas)
    if net_balance >= 5:
        bal_color = "#15803D"
        bal_bg = "#F0FDF4"
        bal_verdict = "अत्यंत शुभ एवं राजयोग प्रधान कुण्डली। शुभ योगों का प्राबल्य दोषों का शमन कर जीवन में निरंतर उन्नति व यश प्रदान करता है।"
    elif net_balance >= 0:
        bal_color = "#1D4ED8"
        bal_bg = "#EFF6FF"
        bal_verdict = "संतुलित एवं पुरुषार्थ प्रधान कुण्डली। शुभ एवं अशुभ नियमों का सम्यक संतुलन है; सद्कर्म एवं नियम पालन से श्रेष्ठ फल की प्राप्ति।"
    else:
        bal_color = "#B91C1C"
        bal_bg = "#FEF2F2"
        bal_verdict = "सावधानी एवं वैदिक शांति अपेक्षित कुण्डली। ग्रह दोषों एवं अनिष्ट योगों के शमन हेतु शास्त्रोक्त जप-दान व यम-नियम का आश्रय लाभप्रद।"

    st.markdown(f"""
    <div style="background:{bal_bg}; border-left:4px solid {bal_color}; padding:10px 14px; border-radius:6px; margin:10px 0;">
        <b style="color:{bal_color}; font-size:14px;">⚖️ शास्त्रीय योग-दोष संतुलन मीमांसा:</b> 
        <span style="font-size:13px; color:#1E293B;">सक्रिय राजयोग ({len(_active_yogas)}) vs सक्रिय दोष ({len(_active_doshas)}) | <b>निष्कर्ष:</b> {bal_verdict}</span>
    </div>
    """, unsafe_allow_html=True)

    _dy_t1, _dy_t2, _dy_t3, _dy_t4 = st.tabs(tabs)

    with _dy_t1:
        st.markdown("### 🔴 कुण्डली में शास्त्रीय दोष विश्लेषण (Dosha Analysis)")
        st.caption("बृहत्पाराशर होराशास्त्र एवं गोचर के आधार पर कुण्डली में सक्रिय और निष्क्रिय दोषों की प्रमाणिक स्थिति:")

        if _active_doshas:
            st.error(f"⚠️ आपकी कुण्डली एवं तात्कालिक गोचर/दशा में **{len(_active_doshas)} दोष** सक्रिय पाए गए हैं:")
            for d in _active_doshas:
                st.markdown(
                    f"""<div style="background:#FEF2F2;border:1.5px solid #EF4444;border-radius:10px;padding:14px;margin:10px 0;">
                    <div style="display:flex;justify-content:space-between;align-items:center;">
                        <b style="font-size:16px;color:#991B1B;">⚠️ {d.rule_name_hi} ({d.rule_name_en})</b>
                        <span style="background:#FEE2E2;color:#991B1B;padding:3px 10px;border-radius:12px;font-weight:700;font-size:12px;">🔴 सक्रिय (Active)</span>
                    </div>
                    <p style="margin:8px 0;color:#1F2937;font-size:14px;">{d.explanation_hi}</p>
                    <small style="color:#6B7280;">📖 <b>शास्त्र प्रमाण:</b> {d.source_text} (अध्याय: {d.source_chapter}) | <b>प्रभाव तीव्रता:</b> {round(d.signal_score * 100)}%</small>
                    </div>""",
                    unsafe_allow_html=True
                )
        else:
            st.success("🎉 **अति उत्तम!** इस कुण्डली में कोई भी गंभीर मारक अथवा पाशविक दोष सक्रिय नहीं पाया गया।")

        # Inactive Doshas Expander for complete visibility
        _inactive_doshas = [e for e in _doshas_ev if not e.fired]
        with st.expander(f"⚪ निष्क्रिय दोष जिन्हें यह कुण्डली पार कर चुकी है ({len(_inactive_doshas)} दोष)", expanded=False):
            for ind in _inactive_doshas:
                st.markdown(
                    f"""<div style="background:#F9FAFB;border:1px solid #E5E7EB;border-radius:8px;padding:10px;margin:6px 0;">
                    <b>⚪ {ind.rule_name_hi}</b> — <span style="color:#6B7280;">{ind.explanation_hi}</span>
                    </div>""",
                    unsafe_allow_html=True
                )

    with _dy_t2:
        st.markdown("### 🟢 शुभ राजयोग, धनयोग एवं महापुरुष योग (Yogas Dashboard)")
        st.caption("कुण्डली में विद्यमान केन्द्र-त्रिकोण राजयोग, धनयोग, गजकेसरी आदि की सक्रियता एवं फलित शक्ति:")

        if _active_yogas:
            st.success(f"✨ इस कुण्डली में **{len(_active_yogas)} अत्यंत शुभ योग** सक्रिय हैं:")
            for y in _active_yogas:
                _score_pct = round(y.signal_score * 100)
                _v_note = f" | 🛡️ {y.varga_notes}" if y.varga_confirmed else ""
                st.markdown(
                    f"""<div style="background:#ECFDF5;border:1.5px solid #10B981;border-radius:10px;padding:14px;margin:10px 0;">
                    <div style="display:flex;justify-content:space-between;align-items:center;">
                        <b style="font-size:16px;color:#065F46;">🌟 {y.rule_name_hi} ({y.rule_name_en})</b>
                        <span style="background:#D1FAE5;color:#065F46;padding:3px 10px;border-radius:12px;font-weight:700;font-size:12px;">🟢 सक्रिय (बल: {_score_pct}%)</span>
                    </div>
                    <p style="margin:8px 0;color:#1F2937;font-size:14px;">{y.explanation_hi}</p>
                    <small style="color:#047857;">📖 <b>शास्त्र प्रमाण:</b> {y.source_text} | <b>श्रेणी:</b> {y.category}{_v_note}</small>
                    </div>""",
                    unsafe_allow_html=True
                )
        else:
            st.info("वर्तमान गोचर/दशा में सामान्य ग्रह स्थिति है, कोई अति-विशिष्ट महायोग तात्कालिक रूप से सक्रिय नहीं है।")

        _inactive_yogas = [e for e in _yogas_ev if not e.fired]
        with st.expander(f"⚪ अन्य शास्त्रीय योग जो इस कुण्डली में अनुपस्थित हैं ({len(_inactive_yogas)} योग)", expanded=False):
            for iny in _inactive_yogas:
                st.markdown(
                    f"""<div style="background:#F9FAFB;border:1px solid #E5E7EB;border-radius:8px;padding:8px;margin:5px 0;">
                    <b>{iny.rule_name_hi}</b>: <span style="color:#6B7280;">{iny.explanation_hi}</span>
                    </div>""",
                    unsafe_allow_html=True
                )

    with _dy_t3:
        st.markdown(f"### 📋 सम्पूर्ण १२,५००+ महा-शास्त्रीय नियमों का लाइव स्कैन ({len(_evidences):,} नियम)")
        st.caption("१६ प्राचीन ग्रन्थों से संकलित नियमों की तात्कालिक स्थिति, शास्त्र प्रमाण, प्रभाव प्रकार एवं स्कोर:")

        _table_data = []
        for ev in _evidences:
            _table_data.append({
                "नियम (Rule Name)": ev.rule_name_hi,
                "प्रकार": "🟢 योग (+)" if ev.polarity == '+' else "🔴 दोष (-)",
                "स्थिति (Status)": "✅ सक्रिय (Fired)" if ev.fired else "⚪ निष्क्रिय",
                "बल (Score)": f"{round(ev.signal_score * 100)}%" if ev.fired else "0%",
                "वर्ग पुष्टि (D9)": "🛡️ पुष्ट" if ev.varga_confirmed else "—",
                "ग्रन्थ (Source)": f"{ev.source_text} (अध्याय {ev.source_chapter})",
            })
        st.dataframe(pd.DataFrame(_table_data), use_container_width=True, hide_index=True)

    with _dy_t4:
        st.markdown("### 💊 कुण्डली के दोषों एवं पीड़ा निवारण हेतु विशेष उपाय")
        st.caption("यह उपाय किसी सामान्य सूची से नहीं, बल्कि आपकी कुण्डली में डिटेक्ट हुए सक्रिय दोषों और ग्रह पीड़ा के आधार पर दिए गए हैं:")

        if _active_doshas:
            for ad in _active_doshas:
                r_info = REMEDY_MAP.get(ad.rule_id, None)
                if not r_info:
                    for k_id, v_val in REMEDY_MAP.items():
                        if k_id in ad.rule_id or ad.rule_id in k_id:
                            r_info = v_val
                            break
                if not r_info:
                    r_info = {
                        "title": f"{ad.rule_name_hi} शांति उपाय",
                        "vedic_mantra": "ॐ नमः शिवाय | गायत्री मंत्र जप",
                        "remedy": f"{ad.rule_name_hi} के प्रभाव को शांत करने हेतु नित्य स्तोत्र पाठ एवं नियमित पूजा करें।",
                        "gem_color": "विद्वान ज्योतिषी से परामर्श कर अनुकूल रत्न पहनें।",
                        "dan": "अन्न, वस्त्र एवं यथाशक्ति तिल का दान करें।",
                        "precaution": "सदाचार का पालन करें एवं तामसिक भोजन से दूर रहें।"
                    }

                st.markdown(
                    f"""<div style="background:#FFFBEB;border:2px solid #F59E0B;border-radius:12px;padding:16px;margin:12px 0;">
                    <h4 style="color:#B45309;margin-top:0;">🛡️ {r_info['title']}</h4>
                    <p><b>⚠️ सक्रिय कारण:</b> {ad.explanation_hi}</p>
                    <div style="background:#FFFFFF;border-radius:8px;padding:12px;margin:8px 0;border:1px solid #FDE68A;">
                        <p style="margin:4px 0;"><b>🕉️ वैदिक मंत्र:</b> <code style="color:#B45309;font-size:14px;">{r_info['vedic_mantra']}</code></p>
                        <p style="margin:4px 0;"><b>🌿 मुख्य शास्त्रीय उपाय:</b> {r_info['remedy']}</p>
                        <p style="margin:4px 0;"><b>💎 रत्न / धातु सुझाव:</b> {r_info['gem_color']}</p>
                        <p style="margin:4px 0;"><b>🎁 विशेष दान सामग्री:</b> {r_info['dan']}</p>
                        <p style="margin:4px 0;color:#DC2626;"><b>⚠️ मुख्य सावधानी:</b> {r_info['precaution']}</p>
                    </div>
                    </div>""",
                    unsafe_allow_html=True
                )
        else:
            st.success("🌟 **बधाई!** आपकी कुण्डली में इस समय कोई अशुभ दोष सक्रिय नहीं है। सुख, शांति व आध्यात्मिक उन्नति हेतु सामान्य सात्विक उपाय नीचे दिए गए हैं:")
            st.markdown(
                """<div style="background:#ECFDF5;border:1.5px solid #10B981;border-radius:10px;padding:14px;margin:10px 0;">
                <h4 style="color:#065F46;margin-top:0;">🌿 सामान्य दैनिक सात्विक सुरक्षा कवच</h4>
                <p>• <b>दैनिक गायत्री मंत्र:</b> प्रातः सूर्योदय के समय 108 बार <code>ॐ भूर्भुवः स्वः तत्सवितुर्वरेण्यं भर्गो देवस्य धीमहि धियो यो नः प्रचोदयात्</code> का जप करें।</p>
                • <b>भगवान शिव अभिषेक:</b> नित्य शिवलिंग पर तांबे के पात्र से शुद्ध जल अर्पित करें।</p>
                • <b>माता-पिता का आशीर्वाद:</b> प्रतिदिन प्रातः माता-पिता के चरण स्पर्श कर दिन की शुरुआत करें।</p>
                • <b>पक्षी/गौ सेवा:</b> गाय को हरा चारा व रोटी तथा पक्षियों को दाना-पानी अवश्य दें।</p>
                </div>""",
                unsafe_allow_html=True
            )

        st.markdown("---")
        st.info("📌 **ज्योतिषीय परामर्श नियम:** कोई भी रत्न धारण करने या तंत्र-मंत्र का अनुष्ठान करने से पूर्व योग्य ज्योतिषी से अपनी लग्न कुण्डली की ग्रह दशा एवं महादशा का व्यक्तिगत विश्लेषण अवश्य कराएं।")
