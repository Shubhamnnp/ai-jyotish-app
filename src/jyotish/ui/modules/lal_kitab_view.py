# -*- coding: utf-8 -*-
"""
Module 22: Lal Kitab 1952 Teva & Classical Remedies View.
Evaluates 12 Pakka Khanas (Houses), 9 Karmic Rinas (Debts), Sleeping Houses & Planets,
Dharmi Teva, Andha Teva, Multi-Planet Khana Conjunctions & Masnui Planets,
and 108 authentic Lal Kitab Totkas with classical guidelines.
"""

import streamlit as st
import pandas as pd
from typing import List, Optional, Dict, Any
from src.jyotish.core.constants import SIGN_NAMES
import src.jyotish.core.lalkitab as lk_mod
from src.jyotish.services.shastriya_pramana import SHASTRIYA_SHLOKAS

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

LAL_KITAB_SHLOKA = {
    "title": "लाल किताब १९५२ फरमान — कुण्डली का बुनियादी फरमान एवं नेकी-बदी विचार",
    "source": "पं. रूपचंद जोशी विरचित 'लाल किताब १९५२' (बुनियादी फरमान एवं कालपुरुष तेवा)",
    "shloka": "किस्मत का लिखा कोई टाल न सके, पर नेकी से बुराई टलती है ।\nग्रहों का असर जब नेक होवे, तो मिट्टी भी सोना बनती है ॥\nफर्माने लाल किताब ये कहता है, कर नेक कमाई धर्म के साथ ।\nसोया घर भी जागेगा तेरा, जब पकड़ेगा तू सत्य का हाथ ॥",
    "meaning": "लाल किताब का शाश्वत सिद्धांत है कि सात्विक आचरण, सत्यनिष्ठा एवं बिना स्वार्थ के किए गए शास्त्रीय टोटकों से सोए हुए घर व ग्रह जाग्रत होकर कष्टों का निवारण करते हैं।"
}

# Classical Multi-Planet Khana Conjunctions & Masnui (Synthetic) Rules
LAL_KITAB_CONJUNCTION_RULES = {
    frozenset(["Sun", "Mercury"]): {
        "title": "सूर्य + बुध (बुधादित्य / नेक असर)",
        "nature": "🟢 अत्यंत शुभ (नेक)",
        "masnui": "मंगल नेक (शुभ ऊर्जा)",
        "phala": "बुद्धि, व्यापार, सरकारी सम्मान और वाणी में ओजस्विता। जातक अपने पुरुषार्थ से धन और मान-प्रतिष्ठा कमाता है।",
        "how_to_see": "यह युति जिस खाने में हो, वहाँ बुध का विवेक सूर्य के प्रचंड तेज को संतुलित रखता है। यदि खाना १, ५ या ११ में हो तो राजयोग फलित होता है।",
        "remedy": "तांबे का छेद वाला सिक्का या चांदी का छल्ला धारण करें।"
    },
    frozenset(["Sun", "Saturn"]): {
        "title": "सूर्य + शनि (पिता-पुत्र का टकराव)",
        "nature": "🔴 शत्रु युति (सावधानी)",
        "masnui": "मंगल बद (क्रोध व संघर्ष)",
        "phala": "पिता-पुत्र के विचारों में मतभेद, हड्डियों या नेत्रों में कमजोरी, सरकारी कार्यों में अनावश्यक अड़चनें।",
        "how_to_see": "सूर्य आग है और शनि धुआं। दोनों मिलकर दृष्टि को धुंधला करते हैं। जिस खाने में बैठें, उस खाने के पक्के स्वामी को कष्ट पहुंचता है।",
        "remedy": "तांबे का बर्तन जमीन में दबाएं अथवा दान करें, सरसों के तेल में अपनी छाया देखकर दान करें।"
    },
    frozenset(["Sun", "Rahu"]): {
        "title": "सूर्य + राहु (ग्रहण योग / मंदा असर)",
        "nature": "🔴 अनिष्ट युति (ग्रहण)",
        "masnui": "शनि बद (धोखा व भ्रम)",
        "phala": "आत्मविश्वास में कमी, पिता के स्वास्थ्य पर प्रतिकूल प्रभाव, झूठे आरोप या अपमान की आशंका।",
        "how_to_see": "राहु सूर्य के तेज को ग्रसित करता है। यह जिस खाने में बैठे, वहां की मान-प्रतिष्ठा को चोट लगती है।",
        "remedy": "बहते जल में नारियल या कच्चा कोयला प्रवाहित करें। सूर्य को नित्य तांबे के पात्र से जल दें।"
    },
    frozenset(["Sun", "Venus"]): {
        "title": "सूर्य + शुक्र (तेज व सौंदर्य का योग)",
        "nature": "🟡 मध्यम / मसनूई राहु",
        "masnui": "राहु नीच (असंतोष)",
        "phala": "भौतिक आकर्षण व कला में रुचि, किंतु दांपत्य जीवन में अहं का टकराव या स्वास्थ्य में नरमी।",
        "how_to_see": "सूर्य की अग्नि में शुक्र (सौंदर्य) पिघलता है। स्त्री वर्ग से मधुर संबंध रखना अत्यंत आवश्यक है।",
        "remedy": "कपूर या दही का मंदिर में दान करें, पत्नी का सदैव आदर करें।"
    },
    frozenset(["Moon", "Jupiter"]): {
        "title": "चन्द्र + गुरु (गजकेसरी / धर्म का सागर)",
        "nature": "🟢 अत्यंत शुभ (महा-नेक)",
        "masnui": "सूर्य उच्च (आध्यात्मिक तेज)",
        "phala": "उच्च विद्या, मानसिक शांति, माता का सुख, समाज में परम सम्मान व ईश्वरीय कृपा।",
        "how_to_see": "यह युति अमृत के समान है। जहाँ भी बैठे, उस खाने के सभी दोषों को धो डालती है।",
        "remedy": "पीपल के वृक्ष में जल दें, बुजुर्गों का चरण स्पर्श कर आशीर्वाद लें।"
    },
    frozenset(["Moon", "Saturn"]): {
        "title": "चन्द्र + शनि (विष योग / कफ व अंधकार)",
        "nature": "🔴 अनिष्ट युति (विष प्रभाव)",
        "masnui": "केतु नीच (अवसाद व चिंता)",
        "phala": "मानसिक तनाव, अवसाद, माता के स्वास्थ्य में नरमी, तरल धन का अचानक व्यय।",
        "how_to_see": "चन्द्रमा पानी है और शनि जहर/स्याही। पानी में स्याही मिलने से मन विचलित होता है।",
        "remedy": "शिवलिंग पर कच्चा दूध अर्पित करें, शनिवार को कुएं या नदी में दूध प्रवाहित करें।"
    },
    frozenset(["Moon", "Rahu"]): {
        "title": "चन्द्र + राहु (चन्द्र ग्रहण / मानसिक भ्रम)",
        "nature": "🔴 अनिष्ट युति (ग्रहण)",
        "masnui": "केतु बद (भ्रम व भय)",
        "phala": "अकारण भय, अनिद्रा, जल से संकट, माता को कष्ट, निर्णय लेने में असमंजस।",
        "how_to_see": "राहु का धुआं चन्द्रमा की चांदनी को ढक लेता है। गुप्त शत्रु सक्रिय रहते हैं।",
        "remedy": "चांदी की ठोस गोली अपनी जेब में रखें, भैरव जी के मंदिर में कच्चा दूध चढ़ाएं।"
    },
    frozenset(["Mars", "Mercury"]): {
        "title": "मंगल + बुध (अक्लमंद की नासमझी)",
        "nature": "🔴 शत्रु युति (अग्नि व वायु)",
        "masnui": "शनि बद (हठ व नुकसान)",
        "phala": "जल्दबाजी में गलत निर्णय, क्रोध में अपशब्द, नसों व दांतों के विकार, व्यापार में जोखिम।",
        "how_to_see": "मंगल शक्ति है और बुध बुद्धि। जब दोनों टकराते हैं तो शक्ति बुद्धि पर हावी हो जाती है।",
        "remedy": "चांदी का छल्ला बिना जोड़ का कनिष्ठिका में पहनें, मिट्टी के बर्तन में शहद भरकर वीराने में दबाएं।"
    },
    frozenset(["Jupiter", "Rahu"]): {
        "title": "गुरु + राहु (गुरु-चांडाल योग)",
        "nature": "🔴 दोष युति (धर्म संकट)",
        "masnui": "केतु बद (अपयश)",
        "phala": "ज्ञान का दुरुपयोग, गुरुजनों से मतभेद, पाचन तंत्र के विकार, धार्मिक कार्यों में विघ्न।",
        "how_to_see": "राहु गुरु की सात्विक ऊर्जा में धुआं घोलता है।",
        "remedy": "पीले वस्त्र में हल्दी की 5 गांठें बांधकर विष्णु मंदिर में रखें, कान में सोना पहनें।"
    },
    frozenset(["Venus", "Saturn"]): {
        "title": "शुक्र + शनि (कला व स्थिरता)",
        "nature": "🟢 मित्र युति (स्थिर धन)",
        "masnui": "मंगल नेक (शिल्प व उद्योग)",
        "phala": "कला, फैशन, उद्योग, जमीन-जायदाद में भारी सफलता, ऐश्वर्य व दीर्घायु।",
        "how_to_see": "शुक्र विलासिता है और शनि उसका आधार। दोनों मिलकर स्थायी संपत्ति देते हैं।",
        "remedy": "काली गाय को हरा चारा खिलाएं, सुगंधित इत्र का प्रयोग करें।"
    },
    frozenset(["Venus", "Rahu"]): {
        "title": "शुक्र + राहु (मायावी आकर्षण)",
        "nature": "🔴 दोष युति (अति-कामुकता व व्यय)",
        "masnui": "केतु नीच (धोखा)",
        "phala": "अत्यधिक विलासिता में धन की बर्बादी, वैवाहिक कलह, गुप्त रोग, बदनामी की आशंका।",
        "how_to_see": "राहु शुक्र की पवित्रता को कामुकता व मायाजाल में उलझाता है।",
        "remedy": "चांदी का टुकड़ा सदैव साथ रखें, नीले वस्त्र पहनने से बचें, पराई स्त्री से दूर रहें।"
    },
    frozenset(["Mars", "Saturn"]): {
        "title": "मंगल + शनि (अंगारक / तकरार योग)",
        "nature": "🔴 अति-क्रूर युति (दुर्घटना भय)",
        "masnui": "राहु उच्च या नीच (अति-उग्रता)",
        "phala": "रक्त विकार, चोट-चपेट का भय, भाइयों से विवाद, अत्यधिक उत्तेजना।",
        "how_to_see": "मंगल आग है और शनि हवा/लोहा। आग और लोहे की टक्कर से चिंगारियां निकलती हैं।",
        "remedy": "मीठी तंदूरी रोटी बनाकर कुत्तों को खिलाएं, बंदरों को गुड़-चना दें।"
    }
}


def _format_dms(deg_val):
    deg = float(deg_val) if deg_val is not None else 0.0
    ansh = int(deg)
    kala = int(round((deg - ansh) * 60.0))
    if kala >= 60:
        kala = 0
        ansh += 1
    return ansh, kala, f"{ansh}° {kala:02d}'"


def analyze_khana_conjunctions(khana_planets: Dict[int, List[str]], chart=None) -> List[Dict[str, Any]]:
    """Identifies khanas with 2 or more planets, assesses harmony/clash, masnui effects, and how to evaluate."""
    results = []
    for kh, pls in khana_planets.items():
        if len(pls) > 1:
            kh_info = lk_mod.LAL_KITAB_KHANA_DATA.get(kh, {})
            pakka_ruler = kh_info.get("pakka_ruler", "Unknown")

            # Collect planet detailed strings
            pls_dms = []
            if chart and hasattr(chart, "planets"):
                for p in pls:
                    p_obj = chart.planets.get(p)
                    if p_obj:
                        _, _, dms_str = _format_dms(getattr(p_obj, "sign_degree", 0.0))
                        pls_dms.append(f"{GRAHA_NAMES_HI.get(p, p)} ({dms_str})")
                    else:
                        pls_dms.append(GRAHA_NAMES_HI.get(p, p))
            else:
                pls_dms = [GRAHA_NAMES_HI.get(p, p) for p in pls]

            # Find pairwise conjunctions
            conj_details = []
            for i in range(len(pls)):
                for j in range(i + 1, len(pls)):
                    p1, p2 = pls[i], pls[j]
                    pair_key = frozenset([p1, p2])
                    rule = LAL_KITAB_CONJUNCTION_RULES.get(pair_key)
                    if rule:
                        conj_details.append(rule)
                    else:
                        conj_details.append({
                            "title": f"{GRAHA_NAMES_HI.get(p1, p1)} + {GRAHA_NAMES_HI.get(p2, p2)} युति",
                            "nature": "🟡 सामान्य युति",
                            "masnui": "परस्पर संयुक्त प्रभाव",
                            "phala": f"खाना नं. {kh} में {GRAHA_NAMES_HI.get(p1, p1)} और {GRAHA_NAMES_HI.get(p2, p2)} की संयुक्त उपस्थिति से दोनों ग्रहों का मिला-जुला फल प्राप्त होगा।",
                            "how_to_see": f"पक्के मालिक ({pakka_ruler}) के साथ दोनों ग्रहों की मित्रता/शत्रुता देखें। जो ग्रह अंश में बलि होगा, उसका प्राथमिक प्रभाव रहेगा।",
                            "remedy": "दोनों ग्रहों के आराध्य देव की उपासना करें एवं दान-पुण्य से संतुलन बनाएं।"
                        })

            results.append({
                "khana": kh,
                "pakka_ruler": pakka_ruler,
                "planets": pls,
                "planets_dms": pls_dms,
                "conjunctions": conj_details
            })
    return results


def render_lal_kitab_view(chart, tabs: Optional[List[str]] = None):
    if tabs is None:
        tabs = [
            "🏠 १२ पक्के खाने व ग्रह स्थिति",
            "⚠️ ९ कर्मिक ऋण व पितृ दोष",
            "💤 सोए हुए घर व ग्रह विचार",
            "🌿 १०८ प्रामाणिक टोटके व उपाय"
        ]

    st.subheader("📕 लाल किताब 1952 तेवा एवं शास्त्रीय उपाय (Lal Kitab 1952 Engine)")
    st.caption("कालपुरुष पक्के घर (खाना नं. १ से १२), ९ प्रकार के कर्मिक ऋण, सोया हुआ घर/ग्रह, धर्मी व अंधा तेवा एवं १०८ प्रामाणिक अचूक टोटके।")

    # 1. Classical Shastriya Farman Card
    with st.expander(f"📜 शास्त्रीय प्रमाण — {LAL_KITAB_SHLOKA['title']}", expanded=False):
        st.markdown(f"""
        <div style="background:#FFFBEB; border-left:4px solid #D97706; padding:12px; border-radius:6px; margin-bottom:10px;">
            <b style="color:#B45309; font-size:15px;">📖 ग्रंथ संदर्भ: {LAL_KITAB_SHLOKA['source']}</b>
            <pre style="white-space:pre-wrap; font-family:serif; font-size:14px; color:#78350F; margin:8px 0; background:transparent; border:none; padding:0;">
{LAL_KITAB_SHLOKA['shloka']}
            </pre>
            <div style="font-size:13px; color:#92400E; margin-top:6px;">
                <b>हिंदी भावार्थ:</b> {LAL_KITAB_SHLOKA['meaning']}
            </div>
        </div>
        """, unsafe_allow_html=True)

    lk_res = lk_mod.default_lalkitab_engine.calculate(chart)

    # 2. Active Native Micro Lal Kitab Teva HUD Console
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
                <span style="font-size:16px; font-weight:700;">🪐 सक्रिय जातक लाल किताब तेवा: <span style="color:#FDE047;">{getattr(chart, 'name', 'सक्रिय कुण्डली')}</span></span>
                <span style="font-size:13px; color:#C7D2FE;">🏛️ लग्न: <b>{l_sign_name} ({l_dms})</b> | 🌙 चंद्र: <b>{m_sign_name} ({m_dms})</b> | 🌟 <b>{m_nak} (पद {m_pada})</b></span>
            </div>
            <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(130px, 1fr)); gap:10px; font-size:12.5px; text-align:center;">
                <div style="background:rgba(255,255,255,0.08); padding:8px; border-radius:6px; border:1px solid rgba(255,255,255,0.15);">
                    <div style="color:#86EFAC; font-size:11px;">🛡️ कुण्डली प्रकार</div>
                    <div style="font-size:15px; font-weight:700; color:#4ADE80;">{'धर्मी तेवा' if lk_res.dharmi_teva else 'सामान्य तेवा'}</div>
                    <div style="font-size:10px; color:#BBF7D0;">{'ईश्वरीय सुरक्षा' if lk_res.dharmi_teva else 'कर्म प्रधान'}</div>
                </div>
                <div style="background:rgba(255,255,255,0.08); padding:8px; border-radius:6px; border:1px solid rgba(255,255,255,0.15);">
                    <div style="color:#93C5FD; font-size:11px;">👁️ नेत्र दृष्टि स्थिति</div>
                    <div style="font-size:15px; font-weight:700; color:#93C5FD;">{'⚠️ अंधा तेवा' if lk_res.andha_teva else ('🌙 रात का अंधा' if getattr(lk_res, 'ratandh_teva', False) else '✅ नेत्रवान')}</div>
                    <div style="font-size:10px; color:#C7D2FE;">दृष्टि सामर्थ्य</div>
                </div>
                <div style="background:rgba(255,255,255,0.08); padding:8px; border-radius:6px; border:1px solid rgba(255,255,255,0.15);">
                    <div style="color:#FCA5A5; font-size:11px;">⚠️ सक्रिय कर्मिक ऋण</div>
                    <div style="font-size:15px; font-weight:700; color:#F87171;">{len(lk_res.active_debts)} / 9 ऋण</div>
                    <div style="font-size:10px; color:#FECACA;">{len(lk_res.active_debts) and 'निवारण अपेक्षित' or 'पूर्ण ऋण-मुक्त'}</div>
                </div>
                <div style="background:rgba(255,255,255,0.08); padding:8px; border-radius:6px; border:1px solid rgba(255,255,255,0.15);">
                    <div style="color:#FDE047; font-size:11px;">💤 सोए हुए घर</div>
                    <div style="font-size:15px; font-weight:700; color:#FEF08A;">{len(lk_res.sleeping_houses)} / 12</div>
                    <div style="font-size:10px; color:#FEF9C3;">जाग्रत करने योग्य</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Micro Planetary Status Grid Expander
        with st.expander("🪐 सक्रिय जातक सूक्ष्म ग्रह-स्थिति व लाल किताब खाना (DMS, नक्षत्र, चरण व स्वभाव)", expanded=False):
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

                    # Lal Kitab Khana conversion
                    lk_khana = "—"
                    for kh, pls in lk_res.khana_planets.items():
                        if p_name in pls:
                            lk_khana = f"खाना {kh}"
                            break

                    dignity_raw = getattr(p_obj, "dignity", "neutral")
                    dignity_hi = DIGNITY_HI.get(str(dignity_raw).lower(), str(dignity_raw))
                    is_retro = getattr(p_obj, "is_retrograde", False)
                    is_comb = getattr(p_obj, "is_combust", False)

                    status_tags = []
                    if is_retro:
                        status_tags.append("🔄 वक्री")
                    if is_comb:
                        status_tags.append("🔥 अस्त")
                    tag_str = f" ({', '.join(status_tags)})" if status_tags else ""

                    planets_data.append({
                        "ग्रह": f"{p_hi} ({p_name})",
                        "लाल किताब खाना": lk_khana,
                        "वैदिक भाव": f"भाव {house}",
                        "राशि": s_name,
                        "अंश-कला (DMS)": dms_str,
                        "नक्षत्र व पद": f"{nak} (पद {pada})",
                        "अवस्था": f"{dignity_hi}{tag_str}",
                        "लाल किताब स्वभाव": "धर्मी / नेक" if lk_res.dharmi_teva else "सामान्य असर"
                    })
            if planets_data:
                st.dataframe(pd.DataFrame(planets_data), use_container_width=True, hide_index=True)

        # 3. Dedicated Multi-Planet Khana Conjunctions Expander (as requested by user)
        conjunction_analysis = analyze_khana_conjunctions(lk_res.khana_planets, chart)
        with st.expander("🤝 एक ही खाने में एकाधिक ग्रह युति फलादेश एवं देखने की शास्त्रीय विधि (Multi-Planet Khana Conjunctions)", expanded=bool(conjunction_analysis)):
            st.markdown("""
            <div style="background:#EFF6FF; border-left:4px solid #2563EB; padding:10px 14px; border-radius:6px; margin-bottom:12px; font-size:13.5px; color:#1E3A8A;">
                <b>📖 लाल किताब युति नियम — किसी भाव/खाने में एक से अधिक ग्रह हों तो कैसे देखें?</b><br/>
                1. <b>पक्के मालिक का अधिकार:</b> सबसे पहले देखें कि उस खाने का कालपुरुष पक्का मालिक कौन है। यदि बैठे हुए ग्रह पक्के मालिक के मित्र हैं, तो श्रेष्ठ फल मिलेगा।<br/>
                2. <b>आपसी तकरार या दोस्ताना:</b> बैठे ग्रह आपस में मित्र (दोस्त) हैं या शत्रु (दुश्मन)? शत्रु होने पर दोनों के कारकत्व में टकराव होगा।<br/>
                3. <b>बलि ग्रह का प्रभाव:</b> जो ग्रह अंश-कला में बलिष्ठ होगा, वह दूसरे ग्रह को दबाएगा और उसका फल पहले प्रकट होगा।<br/>
                4. <b>मसनूई (बनावटी) ग्रह सिद्धांत:</b> दो ग्रहों के मिलने से तीसरे बनावटी ग्रह की शक्ति उत्पन्न होती है, जिसका विचार फलादेश में अनिवार्य है।
            </div>
            """, unsafe_allow_html=True)

            if conjunction_analysis:
                for c_item in conjunction_analysis:
                    kh_num = c_item["khana"]
                    p_names_str = ", ".join(c_item["planets_dms"])
                    p_ruler = c_item["pakka_ruler"]

                    st.markdown(f"""
                    <div style="background:#FFFFFF; border:1.5px solid #CBD5E1; border-radius:10px; padding:14px; margin-bottom:12px; box-shadow:0 2px 4px rgba(0,0,0,0.05);">
                        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; border-bottom:1px solid #E2E8F0; padding-bottom:8px; margin-bottom:10px;">
                            <span style="font-size:16px; font-weight:800; color:#1E293B;">🏠 खाना नं. {kh_num} में युति: <span style="color:#2563EB;">{p_names_str}</span></span>
                            <span style="background:#EFF6FF; color:#1D4ED8; padding:3px 10px; border-radius:12px; font-size:12px; font-weight:700;">पक्का मालिक: {p_ruler}</span>
                        </div>
                    """, unsafe_allow_html=True)

                    for c_rule in c_item["conjunctions"]:
                        st.markdown(f"""
                        <div style="background:#F8FAFC; border-left:3px solid #3B82F6; padding:10px 12px; border-radius:6px; margin-bottom:8px;">
                            <div style="display:flex; justify-content:space-between; align-items:center;">
                                <b style="color:#0F172A; font-size:14px;">✨ {c_rule['title']}</b>
                                <span style="font-size:12px; font-weight:700;">{c_rule['nature']}</span>
                            </div>
                            <p style="margin:6px 0; font-size:13px; color:#1E293B;"><b>📜 फलादेश:</b> {c_rule['phala']}</p>
                            <p style="margin:4px 0; font-size:12.5px; color:#475569;"><b>🧬 मसनूई (बनावटी) ग्रह प्रभाव:</b> {c_rule['masnui']}</p>
                            <p style="margin:4px 0; font-size:12.5px; color:#1E40AF;"><b>🔍 कैसे देखें:</b> {c_rule['how_to_see']}</p>
                            <p style="margin:4px 0; font-size:12.5px; color:#047857;"><b>🌿 शास्त्रीय लाल किताब उपाय:</b> {c_rule['remedy']}</p>
                        </div>
                        """, unsafe_allow_html=True)

                    st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.success("🎉 **अद्भुत समन्वय!** इस कुण्डली में प्रत्येक ग्रह स्वतंत्र खानों में स्थित है। किसी भी एक खाने में २ या अधिक ग्रहों का टकराव अथवा मसनूई दोष नहीं है।")

    rendered_tabs = st.tabs(tabs)
    tab_lk1 = rendered_tabs[0]
    tab_lk2 = rendered_tabs[1]
    tab_lk3 = rendered_tabs[2]
    tab_lk4 = rendered_tabs[3]

    # -------------------------------------------------------------
    # TAB 1: १२ पक्के खाने व ग्रह स्थिति
    # -------------------------------------------------------------
    with tab_lk1:
        st.markdown("### 🏠 लाल किताब अनुसार १२ खानों में ग्रह स्थिति")
        st.caption("लाल किताब में राशि नहीं, बल्कि कालपुरुष के पक्के घर (खाना नं. १ से १२) सर्वोपरि होते हैं:")

        khana_table = []
        for kh in range(1, 13):
            kh_info = lk_mod.LAL_KITAB_KHANA_DATA[kh]
            pls = lk_res.khana_planets.get(kh, [])
            pls_hi = [GRAHA_NAMES_HI.get(p, p) for p in pls]
            khana_tag = f" ({len(pls)} ग्रह युति)" if len(pls) > 1 else ""
            khana_table.append({
                "खाना नं.": f"खाना {kh}{khana_tag}",
                "पक्का स्वामी": kh_info["pakka_ruler"],
                "कारक": kh_info["karaka"],
                "स्थित ग्रह": ", ".join(pls_hi) if pls_hi else "⚪ रिक्त (सोया घर)",
                "महत्व / क्षेत्र": kh_info["nature_hi"]
            })
        st.dataframe(pd.DataFrame(khana_table), use_container_width=True, hide_index=True)

        st.info("ℹ️ **लाल किताब सिद्धांत:** लाल किताब में मेष राशि सदा लग्न (खाना १) मानी जाती है, चाहे जन्म लग्न कोई भी हो। सभी ग्रह अपनी खाना स्थिति के अनुसार विशिष्ट फल व टोटके निर्धारित करते हैं।")

    # -------------------------------------------------------------
    # TAB 2: ९ कर्मिक ऋण व पितृ दोष
    # -------------------------------------------------------------
    with tab_lk2:
        st.markdown("### ⚠️ लाल किताब के ९ शास्त्रीय कर्मिक ऋण (9 Karmic Debts)")
        rina_pramana = SHASTRIYA_SHLOKAS.get("lalkitab_rina_parihara", {})
        if rina_pramana:
            st.markdown(f"""
            <div style="background:#FEF2F2; border-left:3px solid #EF4444; padding:8px 12px; margin-bottom:12px; border-radius:6px; font-size:13px; color:#991B1B;">
                <b>📜 शास्त्रीय ऋण परिहार प्रमाण:</b><br/>
                <i>{rina_pramana.get('shloka_sanskrit', '').replace(chr(10), '<br/>')}</i><br/>
                <small style="color:#7F1D1D;"><b>ग्रन्थ:</b> {rina_pramana.get('grantha', '')}</small>
            </div>
            """, unsafe_allow_html=True)

        if lk_res.active_debts:
            for d in lk_res.active_debts:
                st.markdown(f"""
                <div style="background:#FEF2F2; border:1.5px solid #EF4444; border-radius:10px; padding:14px; margin-bottom:12px;">
                    <b style="color:#991B1B; font-size:16px;">⚠️ {d['name_hi']}</b>
                    <p style="margin:5px 0;"><b>कारण:</b> {d['cause_hi']}</p>
                    <p style="margin:5px 0;"><b>जीवन पर प्रभाव:</b> {d['effect_hi']}</p>
                    <div style="background:#FFFFFF; border-radius:6px; padding:8px; border:1px solid #FCA5A5; margin-top:6px;">
                        <b style="color:#047857;">🌿 लाल किताब निवारण उपाय:</b> {d['remedy_hi']}
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.success("🎉 अत्यंत शुभ! आपकी कुण्डली लाल किताब के समस्त ९ कर्मिक ऋणों (पितृ, मातृ, स्व, स्त्री, रिश्तेदारी, निर्दयी, कुदरती, कन्या व जल ऋण) से पूर्णतः मुक्त है!")

        with st.expander("📖 लाल किताब के सभी ९ कर्मिक ऋणों की प्रामाणिक सूची एवं लक्षण", expanded=False):
            for all_d in lk_mod.DEBT_DEFINITIONS:
                st.markdown(f"""
                <div style="background:#F8FAFC; border:1px solid #CBD5E1; border-radius:8px; padding:10px; margin-bottom:8px;">
                    <b>{all_d['name_hi']}</b>: {all_d['condition_desc_hi']}<br/>
                    <small style="color:#059669;"><b>उपाय:</b> {all_d['remedy_hi']}</small>
                </div>
                """, unsafe_allow_html=True)

    # -------------------------------------------------------------
    # TAB 3: सोए हुए घर व ग्रह विचार
    # -------------------------------------------------------------
    with tab_lk3:
        st.markdown("### 💤 सोए हुए घर एवं ग्रह विचार (Sleeping Houses & Planets)")
        dharmi_pramana = SHASTRIYA_SHLOKAS.get("lalkitab_farman_dharmi", {})
        if dharmi_pramana:
            st.markdown(f"""
            <div style="background:#FFFBEB; border-left:3px solid #D97706; padding:8px 12px; margin-bottom:12px; border-radius:6px; font-size:13px; color:#78350F;">
                <b>📜 धर्मी तेवा फरमान प्रमाण:</b><br/>
                <i>{dharmi_pramana.get('shloka_sanskrit', '').replace(chr(10), '<br/>')}</i><br/>
                <small style="color:#92400E;"><b>ग्रन्थ:</b> {dharmi_pramana.get('grantha', '')}</small>
            </div>
            """, unsafe_allow_html=True)

        col_sl1, col_sl2 = st.columns(2)
        with col_sl1:
            st.markdown("#### 🏠 सोए हुए घर (Sleeping Houses)")
            st.write("जिन घरों में कोई ग्रह स्थित नहीं होता, वे सोए हुए माने जाते हैं। उनके पक्के स्वामियों की सेवा व अनुकूल उपायों से वे जाग्रत होते हैं:")
            st.info(", ".join(f"खाना {h}" for h in lk_res.sleeping_houses) if lk_res.sleeping_houses else "कोई घर सोया हुआ नहीं है।")

        with col_sl2:
            st.markdown("#### 🪐 सोए हुए ग्रह (Sleeping Planets)")
            st.write("जो ग्रह अपने कारक घर या मित्र ग्रहों से दृष्टि-संपर्क स्थापित नहीं कर पाते:")
            st.warning(", ".join(lk_res.sleeping_planets) if lk_res.sleeping_planets else "सभी ग्रह सक्रिय व जाग्रत हैं।")

    # -------------------------------------------------------------
    # TAB 4: १०८ प्रामाणिक टोटके व उपाय
    # -------------------------------------------------------------
    with tab_lk4:
        st.markdown("### 🌿 कुण्डली-आधारित लाल किताब टोटके एवं १०८ उपाय")
        st.caption("आपकी कुण्डली के ग्रहों की खाना स्थिति अनुसार तत्काल प्रभावी लाल किताब उपाय:")

        # 1. Custom Totkas for Current Chart
        chart_totkas = getattr(lk_res, "chart_108_totkas", getattr(lk_res, "specific_remedies", []))
        if chart_totkas:
            c_cols = st.columns(3)
            for idx, c_t in enumerate(chart_totkas):
                with c_cols[idx % 3]:
                    st.markdown(f"""
                    <div style="background:#FFFBEB; border:1.5px solid #F59E0B; border-radius:10px; padding:14px; margin-bottom:12px; min-height:220px;">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <span style="font-size:15px; font-weight:900; color:#B45309;">{c_t['planet_hi']} (खाना नं. {c_t['khana']})</span>
                            <span style="font-size:11px; background:#FEF3C7; color:#92400E; padding:2px 6px; border-radius:4px; font-weight:700;">लाल किताब 1952</span>
                        </div>
                        <div style="font-size:12px; color:#1E293B; margin-top:8px; line-height:1.5;">
                            <b>🌿 अचूक टोटका:</b> {c_t['totka_hi']}
                        </div>
                        <div style="font-size:11px; color:#991B1B; margin-top:6px; line-height:1.4;">
                            <b>⚠️ विशेष सावधानी:</b> {c_t['precaution_hi']}
                        </div>
                        <div style="font-size:11px; color:#065F46; margin-top:6px; font-style:italic;">
                            ✨ {c_t['shastra_effect_hi']}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

        st.markdown("---")
        # 2. Comprehensive 108 Totkas Explorer
        st.markdown("#### 📚 सम्पूर्ण १०८ लाल किताब टोटके पुस्तकालय (108 Totkas Explorer)")
        st.caption("लाल किताब (१९५२ संस्करण) के सभी ९ ग्रहों एवं १२ खानों के १०८ प्रामाणिक उपाय खोजें:")

        col_ex_p, col_ex_kh = st.columns([1.5, 1.5])
        with col_ex_p:
            sel_pl = st.selectbox(
                "ग्रह चुनें (Select Planet):",
                ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"],
                format_func=lambda x: {"Sun": "☀️ सूर्य (Sun)", "Moon": "🌙 चन्द्र (Moon)", "Mars": "⚔️ मंगल (Mars)", "Mercury": "☿️ बुध (Mercury)", "Jupiter": "🪐 गुरु (Jupiter)", "Venus": "💎 शुक्र (Venus)", "Saturn": "⚖️ शनि (Saturn)", "Rahu": "🌪️ राहु (Rahu)", "Ketu": "🚩 केतु (Ketu)"}.get(x, x),
                key="lk_explorer_planet"
            )
        with col_ex_kh:
            sel_kh = st.selectbox(
                "खाना चुनें (Select Khana 1-12):",
                list(range(1, 13)),
                format_func=lambda x: f"खाना नं. {x} ({lk_mod.LAL_KITAB_KHANA_DATA[x]['pakka_sign']})",
                key="lk_explorer_khana"
            )

        exp_data = lk_mod.LAL_KITAB_108_TOTKAS.get((sel_pl, sel_kh), None)
        if exp_data:
            st.markdown(f"""
            <div style="background:#F0FDF4; border:1.5px solid #10B981; border-radius:10px; padding:16px; margin:10px 0;">
                <div style="font-size:16px; font-weight:900; color:#065F46;">
                    📜 {sel_pl} खाना नं. {sel_kh} का प्रामाणिक लाल किताब उपाय
                </div>
                <div style="font-size:14px; color:#0F172A; margin-top:10px; line-height:1.6;">
                    <b>🌿 अचूक टोटका:</b> {exp_data['totka_hi']}
                </div>
                <div style="font-size:13px; color:#991B1B; margin-top:8px;">
                    <b>⚠️ जीवन रक्षा सावधानी:</b> {exp_data['precaution_hi']}
                </div>
                <div style="font-size:12px; color:#047857; margin-top:8px; font-style:italic;">
                    <b>फल प्रभाव:</b> {exp_data['shastra_effect_hi']}
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("""
        #### 📜 लाल किताब के १० शाश्वत नियम:
        1. किसी भी उपाय को सूर्योदय के पश्चात और सूर्यास्त से पहले करें (दिन के समय)।
        2. एक समय में एक ही उपाय करें, कम से कम ४० से ४३ दिन तक नियम न टूटे।
        3. मुफ्त में कोई वस्तु या ताबीज न लें, न ही बिना दक्षिणा के ज्योतिषीय परामर्श करें।
        4. घर के मंदिर में भारी घंटियां या ऊंची मूर्तियां न रखें।
        5. मांस, मदिरा एवं पराई स्त्री के संग से सदा दूर रहें।
        """)
