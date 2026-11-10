import streamlit as st
import pandas as pd
from typing import Optional, List, Dict, Any
from src.jyotish.services.shastriya_pramana import SHASTRIYA_SHLOKAS
import src.jyotish.core.ishta_devata as ishta_mod


GRAHA_NAMES_HI = {
    "Sun": "सूर्य (Sun)",
    "Moon": "चन्द्र (Moon)",
    "Mars": "मंगल (Mars)",
    "Mercury": "बुध (Mercury)",
    "Jupiter": "गुरु (Jupiter)",
    "Venus": "शुक्र (Venus)",
    "Saturn": "शनि (Saturn)",
    "Rahu": "राहु (Rahu)",
    "Ketu": "केतु (Ketu)",
    "Ascendant": "लग्न"
}

RASHI_NAMES_HI = {
    1: "मेष (Aries)", 2: "वृषभ (Taurus)", 3: "मिथुन (Gemini)", 4: "कर्क (Cancer)",
    5: "सिंह (Leo)", 6: "कन्या (Virgo)", 7: "तुला (Libra)", 8: "वृश्चिक (Scorpio)",
    9: "धनु (Sagittarius)", 10: "मकर (Capricorn)", 11: "कुंभ (Aquarius)", 12: "मीन (Pisces)"
}

NAKSHATRA_NAMES = [
    "अश्विनी", "भरणी", "कृत्तिका", "रोहिणी", "मृगशिरा", "आर्द्रा",
    "पुनर्वसु", "पुष्य", "आश्लेषा", "मघा", "पूर्वाफाल्गुनी", "उत्तराफाल्गुनी",
    "हस्त", "चित्रा", "स्वाति", "विशाखा", "अनुराधा", "ज्येष्ठा",
    "मूल", "पूर्वाषाढ़ा", "उत्तराषाढ़ा", "श्रवण", "धनिष्ठा", "शतभिषा",
    "पूर्वाभाद्रपद", "उत्तराभाद्रपद", "रेवती"
]

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

GRAHA_DEITY_MAPPINGS = {
    "Sun": ("भगवान शिव / श्री गायत्री", "रुद्राक्ष या रक्त चन्दन", "ॐ ह्रां ह्रीं ह्रौं सः सूर्याय नमः"),
    "Moon": ("माता पार्वती / श्री गौरी", "स्फटिक या श्वेत चन्दन", "ॐ श्रां श्रीं श्रौं सः चन्द्रमसे नमः"),
    "Mars": ("श्री कार्तिकेय / हनुमान जी", "लाल चन्दन या मूंगा", "ॐ क्रां क्रीं क्रौं सः भौमाय नमः"),
    "Mercury": ("भगवान विष्णु / श्री हरि", "तुलसी माला", "ॐ ब्रां ब्रीं ब्रौं सः बुधाय नमः"),
    "Jupiter": ("परब्रह्म शिव / श्री दक्षिणामूर्ति", "हल्दी माला या पंचमुखी रुद्राक्ष", "ॐ ग्रां ग्रीं ग्रौं सः गुरवे नमः"),
    "Venus": ("माता महालक्ष्मी / श्री भुवनेश्वरी", "कमलगट्टा या स्फटिक", "ॐ द्रां द्रीं द्रौं सः शुक्राय नमः"),
    "Saturn": ("श्री कालभैरव / शनिदेव", "काले अकीक या रुद्राक्ष", "ॐ प्रां प्रीं प्रौं सः शनैश्चराय नमः"),
    "Rahu": ("माता दुर्गा / माँ सरस्वती", "अकीक या चन्दन", "ॐ भ्रां भ्रीं भ्रौं सः राहवे नमः"),
    "Ketu": ("भगवान श्री गणेश / माँ चामुण्डा", "अश्वत्थ (पीपल) या रुद्राक्ष", "ॐ स्रां स्रीं स्रौं सः केतवे नमः")
}

POOJA_SHLOKA = {
    "title": "जैमिनी उपदेश सूत्राणि एवं बृहत्पाराशर होराशास्त्र — कारकांश द्वादश भाव एवं इष्ट निर्णय",
    "source": "महर्षि जैमिनी विरचित 'जैमिनी उपदेश सूत्राणि' (कारकांशाध्याय) एवं 'बृहत्पाराशर होराशास्त्रम्'",
    "shloka": "कारकांशाद् व्यये केतौ कैवल्यं तत्र जायते ।\nशुभदृष्टे तथा मोक्षो रविणा शिवभक्तिमान् ॥\nचन्द्रेण शक्तिपूजा स्यात् कुजेन स्कन्दपूजनम् ।\nगुरौ शिवः शशाङ्केन विष्णुभक्तिः प्रजायते ॥",
    "meaning": "कारकांश कुण्डली के द्वादश भाव (मोक्ष भाव) में केतु या शुभ ग्रह की स्थिति से कैवल्य (मोक्ष) की प्राप्ति होती है। सूर्य से शिव भक्ति, चन्द्र से शक्ति उपासना, मंगल से स्कन्द/हनुमान, बुध से विष्णु, गुरु से परब्रह्म शिव, शुक्र से लक्ष्मी एवं शनि से भैरव साधना का मार्ग प्रशस्त होता है।"
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


def render_pooja_view(chart, tabs: Optional[List[str]] = None):
    if tabs is None:
        tabs = [
            "🕉️ इष्टदेवता व मोक्ष",
            "📿 कुलदेवता व मन्त्र साधना",
            "🪔 नित्य पूजा विधान",
            "📅 व्रत व उपवास नियम",
            "🚩 नवरात्रि ९ दिवसीय विधान"
        ]

    st.subheader("🕉️ इष्टदेवता, धर्मदेवता, नित्य पूजा विधान एवं व्रत निर्णय")
    st.write("महर्षि जैमिनी उपदेश सूत्र एवं बृहत्पाराशर होराशास्त्र अनुसार आत्मकारक (AK), कारकांश (D9) के १२वें भाव (मोक्ष भाव), ५वें भाव (मंत्र सिद्धि), धर्मदेवता, कुलदेवी/कुलदेवता, नित्य पूजा विधि, जप माला एवं पावन व्रत निर्णय।")

    # 1. Classical Shastriya Shloka Card
    with st.expander(f"📜 शास्त्रीय प्रमाण — {POOJA_SHLOKA['title']}", expanded=False):
        st.markdown(f"""
        <div style="background:#FFFBEB; border-left:4px solid #D97706; padding:12px; border-radius:6px; margin-bottom:10px;">
            <b style="color:#B45309; font-size:15px;">📖 ग्रंथ संदर्भ: {POOJA_SHLOKA['source']}</b>
            <pre style="white-space:pre-wrap; font-family:serif; font-size:14px; color:#78350F; margin:8px 0; background:transparent; border:none; padding:0;">
{POOJA_SHLOKA['shloka']}
            </pre>
            <div style="font-size:13px; color:#92400E; margin-top:6px;">
                <b>हिंदी भावार्थ:</b> {POOJA_SHLOKA['meaning']}
            </div>
        </div>
        """, unsafe_allow_html=True)

    try:
        ishta_res = ishta_mod.IshtaDevataEngine.analyze(chart)
    except Exception:
        ishta_res = {
            "ishta_deity": "भगवान शिव (Mahadeva)",
            "ishta_planet": "गुरु (Jupiter)",
            "atmakaraka": "सूर्य (Sun)",
            "karakamsha_sign": "धनु (Sagittarius)",
            "h12_sign": "वृश्चिक",
            "h12_lord": "मंगल",
            "ishta_reason": "कारकांश से द्वादश भाव के आधार पर मोक्ष कारक देव निर्णय।",
            "ishta_form": "सर्वव्यापी, शांत, नीलकण्ठ स्वरूप का ध्यान करें।",
            "ishta_fruit": "आत्मिक शांति, मोक्ष मार्ग प्रशस्त, समस्त व्याधियों से मुक्ति।",
            "ishta_mantra": "ॐ नमः शिवाय",
            "ishta_beej": "ह्रौं",
            "ishta_mala": "रुद्राक्ष माला (१०८ दाने)",
            "ishta_vrat_day": "सोमवार",
            "ishta_vrat_tithi": "त्रयोदशी (प्रदोष) व शिवरात्रि",
            "ishta_vrat_rules": "फलाहार अथवा जलाहार, सात्विक आचरण, क्रोध त्याग।",
            "dharma_deity": "भगवान विष्णु",
            "mantra_deity": "माता गायत्री",
            "kula_deity": "कुलदेवी माँ दुर्गा",
            "palana_deity": "भगवान विष्णु",
            "palana_mantra": "ॐ नमो भगवते वासुदेवाय",
            "palana_sign": "कर्क",
            "ishta_deepa": "शुद्ध देशी गाय का घी",
            "ishta_dhoop": "गुग्गुल, लोबान एवं चन्दन",
            "ishta_direction": "ईशान कोण (North-East)",
            "ishta_flowers": "बिल्वपत्र, श्वेत मन्दार, कनेर",
            "ishta_naivedya": "पंचामृत, फल एवं मिश्री",
            "navratri": {}
        }

    # 2. Active Native Micro Spiritual Planetary Diagnostics Console with Ansh, Kala, Vikala
    if chart is not None:
        with st.expander("🕉️ सक्रिय जातक सूक्ष्म ग्रह, आत्मकारक एवं देव-संरेखण कंसोल (Micro Spiritual Planetary Console)", expanded=True):
            st.caption("सक्रिय कुण्डली के प्रत्येक ग्रह का सूक्ष्म अंश ($0°-29°$), कला ($0'-59'$), विकला ($0''-59''$), नक्षत्र पद (१-४), आत्मकारक स्थिति एवं संबंधित अधिष्ठाता देवता:")

            pooja_diag_rows = []
            for p_key in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]:
                p_obj = getattr(chart, "planets", {}).get(p_key) if hasattr(chart, "planets") else None
                if not p_obj and isinstance(getattr(chart, "planets", None), dict):
                    p_obj = chart.planets.get(p_key)

                if p_obj:
                    lon = getattr(p_obj, "longitude", 0.0) or 0.0
                    sign_num = getattr(p_obj, "sign_num", int(lon // 30) + 1)
                    deg_in_sign = lon % 30.0
                    ansh, kala, vikala, dms_str = _format_dms(deg_in_sign)

                    # Nakshatra and Pada calculation
                    nak_idx = int(lon / (360.0 / 27.0)) % 27
                    nak_name = NAKSHATRA_NAMES[nak_idx]
                    pada = int((lon % (360.0 / 27.0)) / (360.0 / 108.0)) + 1

                    house_num = getattr(p_obj, "house", "-")
                    is_retro = getattr(p_obj, "is_retrograde", False)
                    is_comb = getattr(p_obj, "is_combust", False)

                    state_flags = []
                    if is_retro:
                        state_flags.append("वक्री (R)")
                    if is_comb:
                        state_flags.append("अस्त (C)")
                    state_str = ", ".join(state_flags) if state_flags else "मार्गी (Direct)"

                    raw_dig = getattr(p_obj, "dignity", "neutral")
                    dig_label = DIGNITY_HI.get(raw_dig, str(raw_dig))

                    deity_name, mala_name, beej_mantra = GRAHA_DEITY_MAPPINGS.get(p_key, ("परब्रह्म", "रुद्राक्ष", "ॐ नमः"))

                    # Atmakaraka check
                    ak_mark = " ⭐ [आत्मकारक]" if p_key == ishta_res.get("atmakaraka", "").split(" ")[0] else ""

                    pooja_diag_rows.append({
                        "ग्रह": f"{GRAHA_NAMES_HI.get(p_key, p_key)}{ak_mark}",
                        "भाव": f"भाव {house_num}",
                        "राशि": RASHI_NAMES_HI.get(sign_num, f"राशि {sign_num}"),
                        "अंश-कला-विकला (DMS)": dms_str,
                        "नक्षत्र (चरण)": f"{nak_name} (पद {pada})",
                        "स्थिति": state_str,
                        "गरिमा": dig_label,
                        "अधिष्ठाता देव स्वरूप": deity_name,
                        "अनुकूल जप माला": mala_name,
                        "तांत्रिक / बीज मंत्र": beej_mantra
                    })

            if pooja_diag_rows:
                st.dataframe(pd.DataFrame(pooja_diag_rows), use_container_width=True, hide_index=True)

    # Top Status Banner - 4 Key Spiritual Pillars
    c_i1, c_i2, c_i3, c_i4 = st.columns(4)
    c_i1.metric("प्रधान इष्टदेवता", str(ishta_res.get("ishta_deity", "भगवान शिव")).split(" / ")[0], f"ग्रह: {ishta_res.get('ishta_planet', 'गुरु')}")
    c_i2.metric("कारकांश लग्न (D9)", str(ishta_res.get("karakamsha_sign", "धनु")), f"आत्मकारक: {ishta_res.get('atmakaraka', 'सूर्य')}")
    c_i3.metric("जप माला", str(ishta_res.get("ishta_mala", "रुद्राक्ष")).split(" ")[0], "मंत्र सिद्धि")
    c_i4.metric("पावन व्रत दिवस", str(ishta_res.get("ishta_vrat_day", "सोमवार")).split(" ")[0], str(ishta_res.get("ishta_vrat_tithi", "त्रयोदशी")).split(" ")[0])

    tab_i1, tab_i2, tab_i3, tab_i4, tab_i5 = st.tabs(tabs)

    with tab_i1:
        st.markdown(f"### 🕉️ आपके प्रधान इष्टदेवता: {ishta_res.get('ishta_deity', '')}")

        st.markdown(f"""
        <div style="background:#FFFBEB; border:1.5px solid #F59E0B; border-radius:10px; padding:16px; margin-bottom:14px; box-shadow:0 2px 8px rgba(0,0,0,0.04);">
            <div style="font-size:16px; font-weight:900; color:#B45309; margin-bottom:6px;">
                📜 शास्त्रीय जैमिनी कारकांश निर्णय (Shastriya Proof):
            </div>
            <p style="margin:4px 0; color:#1E293B; line-height:1.6; font-size:14px;">
                <b>१. आत्मकारक (Atmakaraka):</b> आपकी कुण्डली में <b>{ishta_res.get('atmakaraka', '')}</b> आत्मकारक हैं, जो आत्मा के पूर्वजन्म संचित संस्कारों के अधिपति हैं।<br/>
                <b>२. कारकांश राशि (Navamsha):</b> नवांश (D9) कुण्डली में आत्मकारक <b>{ishta_res.get('karakamsha_sign', '')}</b> राशि में स्थित हैं।<br/>
                <b>३. मोक्ष भाव (१२वां भाव):</b> कारकांश से १२वें भाव ({ishta_res.get('h12_sign', '')}) का स्वामी ग्रह <b>{ishta_res.get('h12_lord', '')}</b> है। {ishta_res.get('ishta_reason', '')}
            </p>
            <div style="background:#FFFFFF; border:1px solid #FCD34D; border-radius:6px; padding:10px; margin-top:8px;">
                <b style="color:#78350F;">✨ इष्टदेव स्वरूप एवं ध्यान:</b> {ishta_res.get('ishta_form', '')}<br/>
                <span style="color:#15803D;"><b>आध्यात्मिक फल:</b> {ishta_res.get('ishta_fruit', '')}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("#### 📿 सिद्ध इष्ट मंत्र:")
        st.code(ishta_res.get("ishta_mantra", "ॐ नमः शिवाय"), language="text")
        st.caption(f"**बीज मंत्र:** `{ishta_res.get('ishta_beej', 'ह्रौं')}` | नित्य १०८ बार जप करने से आत्मिक शांति, संकट-निवारण व रक्षा प्राप्त होती है।")

    with tab_i2:
        st.markdown("### 📿 कुलदेवता, पालनकर्ता देवता, धर्मदेवता एवं मंत्र-साधना")
        st.caption("सनातन जैमिनी उपदेश सूत्र एवं पाराशरी परंपरा में इष्टदेव के साथ पालनकर्ता, धर्मदेवता व कुलदेवता की चतुर्दिक आराधना का विधान:")

        col_d1, col_d2, col_d3, col_d4 = st.columns(4)
        with col_d1:
            st.markdown(f"""
            <div style="background:#F0FDF4; border:1.5px solid #22C55E; border-radius:10px; padding:14px; height:100%;">
                <b style="color:#15803D; font-size:15px;">🌾 पालनकर्ता देवता (Palana Karta):</b><br/>
                <small style="color:#64748B;">(कारकांश से ६ठा भाव — {ishta_res.get('palana_sign', '')})</small>
                <p style="margin:8px 0; font-weight:800; color:#0F172A;">{ishta_res.get('palana_deity', 'भगवान विष्णु')}</p>
                <small style="color:#334155;">जैमिनी सूत्र अनुसार यह देव जीवन में आजीविका, भरण-पोषण, स्वास्थ्य-रक्षा एवं विपत्ति में सम्पोषण करते हैं।</small>
            </div>
            """, unsafe_allow_html=True)

        with col_d2:
            st.markdown(f"""
            <div style="background:#EFF6FF; border:1.5px solid #3B82F6; border-radius:10px; padding:14px; height:100%;">
                <b style="color:#1E40AF; font-size:15px;">🛡️ धर्मदेवता (Dharma Devata):</b><br/>
                <small style="color:#64748B;">(कारकांश से ९वां भाव)</small>
                <p style="margin:8px 0; font-weight:800; color:#0F172A;">{ishta_res.get('dharma_deity', 'भगवान विष्णु')}</p>
                <small style="color:#334155;">यह देव आपके धर्म, सदाचार एवं भाग्य के रक्षक हैं। इनकी कृपा से संकटों में सही दिशा व मार्गदर्शन मिलता है।</small>
            </div>
            """, unsafe_allow_html=True)

        with col_d3:
            st.markdown(f"""
            <div style="background:#FAF5FF; border:1.5px solid #A855F7; border-radius:10px; padding:14px; height:100%;">
                <b style="color:#7E22CE; font-size:15px;">⚡ मंत्र देवता (Mantra Devata):</b><br/>
                <small style="color:#64748B;">(लग्न से ५वां भाव — पूर्वपुण्य)</small>
                <p style="margin:8px 0; font-weight:800; color:#0F172A;">{ishta_res.get('mantra_deity', 'माता गायत्री')}</p>
                <small style="color:#334155;">इस देव के मंत्र का अनुष्ठान करने से सबसे तीव्र मंत्र-सिद्धि, पूर्वपुण्य जागृति एवं मेधा शक्ति प्राप्त होती है।</small>
            </div>
            """, unsafe_allow_html=True)

        with col_d4:
            st.markdown(f"""
            <div style="background:#FDF2F8; border:1.5px solid #EC4899; border-radius:10px; padding:14px; height:100%;">
                <b style="color:#BE185D; font-size:15px;">🏛️ कुलदेवता / कुलदेवी (Kula Devata):</b><br/>
                <small style="color:#64748B;">(कुटुम्ब भाव — द्वितीय भाव)</small>
                <p style="margin:8px 0; font-weight:800; color:#0F172A;">{ishta_res.get('kula_deity', 'माँ दुर्गा')}</p>
                <small style="color:#334155;">वंश परंपरा, कुल की रक्षा एवं संतान वृद्धि हेतु नित्य कुलदेवी/देवता का स्मरण अनिवार्य है।</small>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("#### 🌾 पालनकर्ता देवता सम्पोषण मंत्र:")
        st.code(ishta_res.get("palana_mantra", "ॐ नमो भगवते वासुदेवाय"), language="text")
        st.caption("दैनिक आजीविका, रोजगार में स्थिरता एवं आर्थिक पोषण हेतु इस मंत्र का नित्य ११ बार स्मरण करें।")

    with tab_i3:
        st.markdown("### 🪔 नित्य पूजा-उपासना, दीपक एवं पूजन सामग्री विधान")
        st.caption("आपकी कुण्डली के ग्रहों व इष्टदेवता के अनुसार अनुकूलतम पूजन विधि:")

        c_p1, c_p2 = st.columns(2)
        with c_p1:
            st.markdown(f"""
            <div style="background:#F0FDF4; border:1px solid #86EFAC; border-radius:8px; padding:14px; margin-bottom:12px;">
                <b style="color:#15803D; font-size:15px;">🪔 दीपक एवं धूप विधान:</b>
                <p style="margin:6px 0;">• <b>दीपक का तेल/घी:</b> <b>{ishta_res.get('ishta_deepa', '')}</b></p>
                <p style="margin:6px 0;">• <b>धूप / सुगंध:</b> {ishta_res.get('ishta_dhoop', '')}</p>
                <p style="margin:6px 0;">• <b>पूजा का मुख (दिशा):</b> <b>{ishta_res.get('ishta_direction', '')}</b> की ओर मुख करके बैठें।</p>
            </div>
            """, unsafe_allow_html=True)

            st.markdown(f"""
            <div style="background:#FFFBEB; border:1px solid #FDE68A; border-radius:8px; padding:14px; margin-bottom:12px;">
                <b style="color:#B45309; font-size:15px;">🌸 प्रिय पुष्प एवं माला:</b>
                <p style="margin:6px 0;">• <b>पुष्प अर्पण:</b> {ishta_res.get('ishta_flowers', '')}</p>
                <p style="margin:6px 0;">• <b>जप माला:</b> <b>{ishta_res.get('ishta_mala', '')}</b> से मंत्र जप करें।</p>
            </div>
            """, unsafe_allow_html=True)

        with c_p2:
            st.markdown(f"""
            <div style="background:#EFF6FF; border:1px solid #BFDBFE; border-radius:8px; padding:14px; margin-bottom:12px;">
                <b style="color:#1D4ED8; font-size:15px;">🍯 प्रिय नैवेद्य (प्रसाद / भोग):</b>
                <p style="margin:6px 0;">• <b>भोग:</b> {ishta_res.get('ishta_naivedya', '')}</p>
                <p style="margin:6px 0;">• <b>पवित्रता:</b> भोग अर्पित करने के बाद प्रसाद रूप में परिवार सहित ग्रहण करें।</p>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("""
            <div style="background:#FAF5FF; border:1px solid #E9D5FF; border-radius:8px; padding:14px; margin-bottom:12px;">
                <b style="color:#7E22CE; font-size:15px;">📜 नित्य पूजा का दैनिक क्रम:</b>
                <p style="margin:4px 0;">१. आचमन एवं पवित्रीकरण ➔ २. दीपक प्रज्वलन ➔ ३. गणेश वंदना ➔ ४. कुलदेवता व गुरु स्मरण ➔ ५. इष्टदेव स्तुति व १०८ जप ➔ ६. आरती व समर्पण।</p>
            </div>
            """, unsafe_allow_html=True)

    with tab_i4:
        st.markdown("### 📅 अनुकूल सामान्य व्रत, उपवास एवं पारण नियम")
        st.caption("धर्म सिंधु एवं निर्णय सिंधु अनुसार आपकी जन्म कुण्डली के लिए सर्वाधिक कल्याणकारी साप्ताहिक व मासिक व्रत:")

        st.markdown(f"""
        <div style="background:#FEF3C7; border:1.5px solid #D97706; border-radius:10px; padding:16px; margin-bottom:14px;">
            <div style="font-size:16px; font-weight:900; color:#78350F; margin-bottom:6px;">
                🌟 आपका मुख्य साप्ताहिक व्रत दिवस: <b>{ishta_res.get('ishta_vrat_day', '')}</b>
            </div>
            <p style="margin:6px 0;">• <b>मुख्य पावन तिथियाँ:</b> {ishta_res.get('ishta_vrat_tithi', '')}</p>
            <p style="margin:6px 0;">• <b>उपवास के शास्त्रीय नियम:</b> {ishta_res.get('ishta_vrat_rules', '')}</p>
            <p style="margin:6px 0; color:#92400E;">• <b>आध्यात्मिक व सांसारिक फल:</b> {ishta_res.get('ishta_fruit', '')}</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        #### 📜 उपवास एवं पारण के शाश्वत नियम:
        1. **संकल्प:** प्रातः स्नान के उपरांत पूर्व या उत्तर मुख होकर हाथ में जल, अक्षत व पुष्प लेकर व्रत का संकल्प लें।
        2. **इन्द्रिय संयम:** उपवास के दिन क्रोध, झूठ, निंदा, परनिंदा, दिन में सोना एवं तामसिक संगति सर्वथा वर्जित है।
        3. **पारण समय:** सायंकाल पूजा व आरती के पश्चात, अथवा अगले दिन सूर्योदय के उपरांत ही शुद्ध सात्विक भोजन से पारण करें।
        4. **दान की महिमा:** व्रत पूर्ण होने पर किसी ब्राह्मण, साधु अथवा निर्धन व्यक्ति को अपनी क्षमता अनुसार भोजन या अन्न-दान अवश्य करें।
        """)

    with tab_i5:
        st.markdown("### 🚩 नवरात्रि विशेष: कुण्डली अनुसार ९ दिवसीय पूजा, व्रत एवं संपूर्ण विधान")
        st.caption("देवी भागवत, निर्णय सिंधु, कालिका पुराण एवं चरक संहिता अनुसार आपकी कुण्डली के ग्रहों, आत्मकारक व भावों का सटीक विश्लेषण:")

        nv = ishta_res.get("navratri", {})
        if nv:
            st.markdown(f"""
            <div style="background:#FFF1F2; border:2.5px solid #E11D48; border-radius:12px; padding:18px; margin-bottom:16px; box-shadow:0 4px 14px rgba(225,29,72,0.12);">
                <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; margin-bottom:10px;">
                    <span style="font-size:19px; font-weight:900; color:#9F1239;">🎯 सक्रिय जातक कुण्डली अनुसार नवरात्रि की सर्वोत्तम व्रत तिथि</span>
                    <span style="background:#FFE4E6; color:#BE123C; padding:5px 12px; border-radius:20px; font-size:13.5px; font-weight:800;">{nv.get('element', '')}</span>
                </div>
                <div style="background:#FFFFFF; border:1.5px solid #FDA4AF; border-radius:8px; padding:12px; margin-bottom:10px;">
                    <b style="color:#BE123C; font-size:16px;">🌟 अनुशंसित सर्वोत्तम व्रत तिथि:</b> <span style="color:#0F172A; font-size:16px; font-weight:800;">{nv.get('optimal_fasting_tithi', 'महाअष्टमी')}</span>
                    <p style="margin:8px 0 0 0; color:#334155; font-size:14px; line-height:1.6;">{nv.get('optimal_fasting_tithi_reason', '')}</p>
                </div>
                <p style="margin:6px 0; color:#1E293B; font-size:14px; line-height:1.6;"><b>उपवास प्रारूप:</b> {nv.get('vrat_pattern_desc', '')}</p>
                <div style="background:#FFFBEB; border-left:4px solid #F59E0B; padding:8px 12px; margin-top:8px; border-radius:0 6px 6px 0;">
                    <b style="color:#B45309;">📅 सर्वोत्तम व्रत दिवस क्रम:</b> <span style="color:#0F172A; font-weight:700;">{nv.get('recommended_days', '')}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("#### 🥣 उपवास के ५ शास्त्रीय भेद — निर्जला, जलाहार व फलाहार निर्णय:")

            c_v1, c_v2 = st.columns(2)
            with c_v1:
                st.markdown(f"""
                <div style="background:#F8FAFC; border:1.5px solid #CBD5E1; border-radius:10px; padding:14px; margin-bottom:12px; height:100%;">
                    <b style="color:#0F172A; font-size:15px;">💧 १. निर्जला उपवास (Nirjala Vrata):</b><br/>
                    <div style="margin:6px 0; font-weight:800; font-size:14px; color:{'#15803D' if '✅' in nv.get('nirjala_status','') else '#B91C1C'};">
                        स्थिति: {nv.get('nirjala_status', '')}
                    </div>
                    <p style="margin:4px 0; font-size:13px; color:#334155; line-height:1.5;">{nv.get('nirjala_note', '')}</p>
                    <small style="color:#64748B;"><b>शास्त्रीय नियम:</b> सूर्योदय से अगले सूर्योदय तक जल की बूंद भी ग्रहण न करना। यदि कुण्डली में पित्त या वात दोष हो तो पूर्ण ९ दिन निर्जला रखना शास्त्रों में सर्वथा निषिद्ध है। केवल महाअष्टमी को १ दिन का निर्जला संकल्प लिया जा सकता है।</small>
                </div>
                """, unsafe_allow_html=True)

            with c_v2:
                st.markdown(f"""
                <div style="background:#F0FDF4; border:1.5px solid #86EFAC; border-radius:10px; padding:14px; margin-bottom:12px; height:100%;">
                    <b style="color:#15803D; font-size:15px;">🚰 २. सजला / जलाहार उपवास (Jalahar Vrata):</b><br/>
                    <div style="margin:6px 0; font-weight:800; font-size:14px; color:#166534;">
                        मुख्य विधान: {nv.get('primary_vidhan', '')}
                    </div>
                    <p style="margin:4px 0; font-size:13px; color:#14532D; line-height:1.5;">{nv.get('sajala_note', '')}</p>
                    <small style="color:#15803D;"><b>पेय पदार्थ:</b> शुद्ध गंगाजल मिश्रित जल, ताजा नारियल पानी, नींबू-मिश्री जल तथा बिना नमक के फलों का ताजा रस। यह शरीर की शुद्धि (डिटॉक्स) एवं साधना एकाग्रता हेतु सर्वोत्तम है।</small>
                </div>
                """, unsafe_allow_html=True)

            c_v3, c_v4 = st.columns(2)
            with c_v3:
                st.markdown("""
                <div style="background:#FFFBEB; border:1.5px solid #FDE68A; border-radius:10px; padding:14px; margin-bottom:12px; height:100%;">
                    <b style="color:#B45309; font-size:15px;">🥛 ३. दुग्धाहार (पयोव्रत) एवं ४. फलाहार:</b><br/>
                    <p style="margin:4px 0; font-size:13px; color:#78350F; line-height:1.5;">
                        • <b>पयोव्रत:</b> केवल देशी गाय का ताजा दूध, मखाना व मिश्री का सेवन।<br/>
                        • <b>फलाहार:</b> ऋतु फल (सेब, केला, अनार, पपीता), सूखे मेवे (बादाम, काजू, किशमिश), कुट्टू/सिंघाड़े का आटा एवं सेंधा नमक का दिन में केवल <b>एक बार</b> सेवन।
                    </p>
                    <small style="color:#92400E;"><b>सेंधा नमक नियम:</b> नमक का सेवन केवल सूर्यास्त से पूर्व या सायंकाल आरती के बाद ही एक बार करें। बार-बार नमक युक्त भोजन करने से उपवास खंडित माना जाता है।</small>
                </div>
                """, unsafe_allow_html=True)

            with c_v4:
                st.markdown("""
                <div style="background:#FAF5FF; border:1.5px solid #E9D5FF; border-radius:10px; padding:14px; margin-bottom:12px; height:100%;">
                    <b style="color:#7E22CE; font-size:15px;">🌙 ५. एकभुक्त / नक्तव्रत (Evening Satvik Meal):</b><br/>
                    <p style="margin:4px 0; font-size:13px; color:#581C87; line-height:1.5;">
                        • <b>विधान:</b> दिनभर पूर्ण उपवास (केवल जल या फल) रखें। सायंकाल माँ भगवती की आरती व दुर्गा चालीसा/सप्तशती पाठ के उपरांत केवल <b>एक समय शुद्ध सात्विक भोजन</b> ग्रहण करें।<br/>
                        • <b>किसके लिए:</b> जो जातक नौकरी/व्यवसाय में अत्यधिक श्रम करते हैं या जिन्हें शारीरिक दुर्बलता है।
                    </p>
                    <small style="color:#6B21A8;">शास्त्रों में नक्तव्रत को भी पूर्ण तपस्या के समतुल्य फलदायी घोषित किया गया है।</small>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("#### 🗓️ प्रतिपदा से नवमी — ९ दिवसीय दैनन्दिन पूजा, कुण्डली फल, मंत्र व प्रिय भोग:")
            st.caption("आपकी कुण्डली के ग्रहों, आत्मकारक व भावों के आधार पर प्रत्येक दिन का विशिष्ट विश्लेषण:")

            for day in nv.get("nine_days", []):
                priority_label = " ⭐ [आपकी कुण्डली हेतु विशेष कल्याणकारी दिन]" if day.get("is_priority") else ""
                with st.expander(f"{day.get('tithi', '')} — {day.get('deity', '')} (अधिपति: {day.get('graha', '')}){priority_label}", expanded=day.get("is_priority", False)):
                    st.markdown(f"""
                    <div style="background:#FAF5FF; border:1px solid #D8B4FE; border-radius:8px; padding:12px; margin-bottom:10px;">
                        <b style="color:#6B21A8; font-size:15px;">🌸 अधिष्ठात्री देवी: {day.get('deity', '')}</b> | <b>अधिपति ग्रह:</b> {day.get('graha', '')} | <b>चक्र:</b> {day.get('chakra', '')}
                        <p style="margin:6px 0; color:#1E293B; font-size:13.5px;"><b>कुण्डली फल व संबंध:</b> {day.get('kundali_context', '')}</p>
                        <p style="margin:4px 0; color:#0F172A; font-size:13px;"><b>उपवास स्वरूप:</b> {day.get('vrat_type', '')}</p>
                        <p style="margin:4px 0; color:#78350F; font-size:13px;"><b>प्रिय नैवेद्य (भोग):</b> {day.get('bhog', '')}</p>
                        <p style="margin:4px 0; color:#15803D; font-size:13px;"><b>दैनिक पूजन विधान:</b> {day.get('vidhan', '')}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    st.code(day.get('mantra', ''), language="text")

            st.markdown("""
            <div style="background:#F1F5F9; border:1px solid #CBD5E1; border-radius:8px; padding:14px; margin-top:14px; margin-bottom:14px;">
                <b style="color:#0F172A; font-size:15px;">🏺 घटस्थापना, कन्या पूजन एवं पारण के शास्त्रीय नियम:</b>
                <p style="margin:4px 0; font-size:13px; color:#334155;">
                    • <b>कलश स्थापना दिशा:</b> घर या पूजा कक्ष के <b>ईशान कोण (North-East)</b> अथवा पूर्व दिशा में शुद्ध मिट्टी की वेदी बनाकर जौ (ज्वारे) बोएं और उस पर जल-गंगाजल पूरित तांबे या मिट्टी का कलश स्थापित करें।<br/>
                    • <b>अखण्ड ज्योति विधान:</b> यदि घी का दीपक जलाएं तो वह देवी प्रतिमा के <b>दाहिनी ओर (Right Side)</b> रखें; यदि तिल के तेल का दीपक हो तो <b>बाईं ओर (Left Side)</b> रखें।<br/>
                    • <b>कन्या पूजन (Kanya Poojan):</b> अष्टमी अथवा नवमी के दिन २ वर्ष से ९ वर्ष तक की कन्याओं (कुमारिका, त्रिमूर्ति, कल्याणी, रोहिणी आदि) का पाद प्रक्षालन कर हलवा, पूरी व काले चने का भोग लगाकर दक्षिणा देकर आशीर्वाद लें।<br/>
                    • <b>पारण का शास्त्रीय समय:</b> नवमी तिथि के हवन व कन्या पूजन की समाप्ति के उपरांत अथवा दशमी तिथि के सूर्योदय पर ही व्रत का पारण करें। पारण में सर्वप्रथम माँ का चरणामृत व प्रसाद ग्रहण करें।
                </p>
            </div>
            """, unsafe_allow_html=True)
