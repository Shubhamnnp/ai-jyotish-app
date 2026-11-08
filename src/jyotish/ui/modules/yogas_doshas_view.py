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
import src.jyotish.rules.engine as r_mod
import src.jyotish.dasha.vimshottari as vim_mod
import src.jyotish.core.gochar as goc_mod


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

    # 1. Compute Active Dasha & Transit Context required by the Rules Library
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

    # 2. Categorize Evidences into Doshas (Negative Polarity) and Yogas (Positive Polarity)
    _doshas_ev = [e for e in _evidences if e.polarity == '-']
    _yogas_ev = [e for e in _evidences if e.polarity == '+']

    _active_doshas = [e for e in _doshas_ev if e.fired]
    _active_yogas = [e for e in _yogas_ev if e.fired]

    # Summary metric HUD
    _mc1, _mc2, _mc3, _mc4 = st.columns(4)
    _mc1.metric("⚠️ सक्रिय दोष (Active Doshas)", len(_active_doshas), delta=f"कुल {_active_doshas and 'ध्यान दें' or 'सुरक्षित'}", delta_color="inverse")
    _mc2.metric("✨ सक्रिय योग (Active Yogas)", len(_active_yogas), delta=f"कुल {len(_yogas_ev)} योगों में से")
    _mc3.metric("📋 मूल्यांकित नियम (Rules Evaluated)", f"{len(_evidences):,}", delta="100% Shastriya")
    _mc4.metric("💊 कुण्डली उपाय (Specific Remedies)", len(_active_doshas) + (1 if not _active_doshas else 0))

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
