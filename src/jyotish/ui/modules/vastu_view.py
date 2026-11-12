import streamlit as st
import math
import importlib
from src.jyotish.services.vastu import VastuJyotishEngine as _VastuEngine

def render_vastu_compass_wheel_svg(zones: list, is_dark: bool = False) -> str:
    def polar_to_cart(cx, cy, r, deg):
        rad = math.radians(deg - 90)
        return cx + r * math.cos(rad), cy + r * math.sin(rad)

    def get_arc_path(cx, cy, r_in, r_out, start_deg, end_deg):
        x1_out, y1_out = polar_to_cart(cx, cy, r_out, start_deg)
        x2_out, y2_out = polar_to_cart(cx, cy, r_out, end_deg)
        x2_in, y2_in = polar_to_cart(cx, cy, r_in, end_deg)
        x1_in, y1_in = polar_to_cart(cx, cy, r_in, start_deg)
        return f"M {x1_out:.1f} {y1_out:.1f} A {r_out} {r_out} 0 0 1 {x2_out:.1f} {y2_out:.1f} L {x2_in:.1f} {y2_in:.1f} A {r_in} {r_in} 0 0 0 {x1_in:.1f} {y1_in:.1f} Z"

    cx, cy = 250, 250
    bg_circle = "#0b1021" if is_dark else "#f8fafc"
    border_circle = "#334155" if is_dark else "#cbd5e1"
    text_main = "#f8fafc" if is_dark else "#0f172a"
    text_sub = "#94a3b8" if is_dark else "#64748b"

    zone_dict = {z.get("direction"): z for z in zones}

    dirs = [
        ("North", 0, "उत्तर (N)", "बुध (Mercury)"),
        ("North-East", 45, "ईशान (NE)", "गुरु (Jupiter)"),
        ("East", 90, "पूर्व (E)", "सूर्य (Sun)"),
        ("South-East", 135, "आग्नेय (SE)", "शुक्र (Venus)"),
        ("South", 180, "दक्षिण (S)", "मंगल (Mars)"),
        ("South-West", 225, "नैऋत्य (SW)", "राहु (Rahu)"),
        ("West", 270, "पश्चिम (W)", "शनि (Saturn)"),
        ("North-West", 315, "वायव्य (NW)", "चन्द्र (Moon)"),
    ]

    wedges_svg = []
    for d_name, mid_ang, label, fallback_lord in dirs:
        z = zone_dict.get(d_name, {})
        score = z.get("score", 70)
        lord = z.get("lord", fallback_lord)

        if score >= 75:
            color = "#10b981"
            fill_opacity = "0.22"
        elif score >= 50:
            color = "#f59e0b"
            fill_opacity = "0.22"
        else:
            color = "#ef4444"
            fill_opacity = "0.25"

        path_d = get_arc_path(cx, cy, 90, 230, mid_ang - 22.5, mid_ang + 22.5)
        tx, ty = polar_to_cart(cx, cy, 160, mid_ang)

        wedges_svg.append(
            f'<path d="{path_d}" fill="{color}" fill-opacity="{fill_opacity}" stroke="{color}" stroke-width="2"/>'
            f'<text x="{tx:.1f}" y="{(ty - 10):.1f}" text-anchor="middle" fill="{text_main}" font-size="12" font-weight="bold">{label}</text>'
            f'<text x="{tx:.1f}" y="{(ty + 6):.1f}" text-anchor="middle" fill="{text_sub}" font-size="10.5">{lord}</text>'
            f'<text x="{tx:.1f}" y="{(ty + 22):.1f}" text-anchor="middle" fill="{color}" font-size="12" font-weight="bold">{score}/100</text>'
        )

    b_zone = zone_dict.get("Center", {})
    b_score = b_zone.get("score", 85)
    b_color = "#3b82f6"

    center_svg = (
        f'<circle cx="{cx}" cy="{cy}" r="82" fill="{b_color}" fill-opacity="0.20" stroke="{b_color}" stroke-width="2.5"/>'
        f'<text x="{cx}" y="{cy - 12}" text-anchor="middle" fill="{text_main}" font-size="13" font-weight="bold">ब्रह्मस्थान</text>'
        f'<text x="{cx}" y="{cy + 5}" text-anchor="middle" fill="{text_sub}" font-size="10.5">Brahmasthan (Akasha)</text>'
        f'<text x="{cx}" y="{cy + 22}" text-anchor="middle" fill="{b_color}" font-size="12" font-weight="bold">{b_score}/100</text>'
    )

    svg_parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 500 500" width="100%" height="450" style="max-width: 500px; margin: 0 auto; display: block;">',
        f'<defs><radialGradient id="compassBg" cx="50%" cy="50%" r="50%">',
        f'<stop offset="0%" stop-color="{bg_circle}" stop-opacity="0.9"/>',
        f'<stop offset="100%" stop-color="{bg_circle}" stop-opacity="1"/>',
        f'</radialGradient></defs>',
        f'<circle cx="{cx}" cy="{cy}" r="240" fill="url(#compassBg)" stroke="{border_circle}" stroke-width="2"/>',
        f'<circle cx="{cx}" cy="{cy}" r="236" fill="none" stroke="{border_circle}" stroke-width="1" stroke-dasharray="4,4"/>',
        "".join(wedges_svg),
        center_svg,
        '</svg>'
    ]

    return "".join(svg_parts)

def render_vastu_view(chart, tabs=None):
    is_dark = st.session_state.get("dark_mode", False)
    is_astrallis_mode = st.session_state.get("astrallis_mode", False)
    is_night_mode = is_dark

    if tabs is None:
        tabs = [
            '🧭 सम्पूर्ण वास्तु मण्डल',
            '🌅 पूर्व (East)',
            '⚡ आग्नेय (SE)',
            '🔴 दक्षिण (South)',
            '⛰️ नैऋत्य (SW)',
            '🌊 पश्चिम (West)',
            '💨 वायव्य (NW)',
            '💰 उत्तर (North)',
            '🕉️ ईशान (NE)',
            '🌌 ब्रह्मस्थान (Center)'
        ]

    # Detect active Mahadasha lord if birth data is present
    active_dasha_lord = None
    try:
        from src.jyotish.core.dasha import default_dasha_engine
        from datetime import datetime
        if hasattr(chart, "birth_data") and chart.birth_data and "Moon" in chart.planets:
            _cur_dt = datetime.now()
            _b_full_dt = datetime.combine(chart.birth_data.birth_date, chart.birth_data.birth_time)
            _active_d = default_dasha_engine.get_active_dasha_at(_b_full_dt, chart.planets["Moon"].longitude, _cur_dt.date())
            if _active_d and _active_d.mahadasha:
                active_dasha_lord = _active_d.mahadasha.lord
    except Exception:
        active_dasha_lord = None

    vastu_engine = _VastuEngine(chart, current_dasha_lord=active_dasha_lord)
    v_zones = vastu_engine.evaluate_vastu_zones()
    zone_dict = {z.get("direction"): z for z in v_zones}
    _is_dark = (is_astrallis_mode or is_night_mode)

    card_bg = "#111827" if _is_dark else "#FFFFFF"
    card_bdr = "#374151" if _is_dark else "#E2E8F0"
    hdr_bg = "#1F2937" if _is_dark else "#F8FAFC"
    hdr_bdr = "#374151" if _is_dark else "#CBD5E1"
    row_bg = "#111827" if _is_dark else "#FFFFFF"
    row_alt_bg = "#1F2937" if _is_dark else "#F8FAFC"
    row_bdr = "#374151" if _is_dark else "#E2E8F0"
    text_primary = "#F9FAFB" if _is_dark else "#0F172A"
    text_secondary = "#9CA3AF" if _is_dark else "#475569"

    # Robust fallback dictionary guaranteeing no 'N/A' in 5-pillar remedies
    VASTU_PARAM_FALLBACKS = {
        "East": {
            "deity": "Indra / Surya Dev",
            "degree_range": "67.5° – 112.5° (मध्य 90°)",
            "associated_house": "१म भाव (तनु / लग्न - देह व आत्मशक्ति)",
            "vastu_purusha_organ": "वास्तु पुरुष का मस्तक, कपाल व नेत्र",
            "chakra_organ": "Vitality, Eye Sight, Heart, Head, Father, Social Prestige",
            "gemstone": "माणिक्य (Ruby)",
            "metal": "तांबा (Copper)",
            "botanical": "आक (मदार), लाल कनेर, जामुन",
            "color_therapy": "सूर्योदय नारंगी, स्वर्णिम, गहरा केसरिया (Sunrise Orange / Gold)",
            "symptoms_of_defect": "हृदय विकार, नेत्र रोग, सिरदर्द, पिता से मतभेद, सरकारी कार्यों में बाधा, मानहानि व ऊर्जाहीनता।",
            "mantra": "ॐ ह्रां ह्रीं ह्रौं सः सूर्याय नमः ॥",
            "remedy_hi": "पूर्व दिशा को स्वच्छ, खुला और हल्का रखें। भारी सामान न रखें। पूर्व की दीवार पर तांबे का सूर्य यंत्र या पीतल का सूर्य स्थापित करें। शुद्ध तांबे का जल पात्र रखें।",
            "non_destructive_remedy": "यदि पूर्व दिशा बंद या भारी हो तो दीवार पर 100% तांबे की पट्टी जमीन में स्थापित करें तथा पूर्व दिशा में सूर्य पिरामिड लगाएं।",
            "shastra_shloka": "पूर्वे शक्रः श्रियं दद्याद् दक्षिणे यमराड्भयम् । वरुणे पश्चिमे सौम्यं कुबेरश्चोत्तरे धनम् ॥"
        },
        "South-East": {
            "deity": "Agni Dev (अग्नि देव)",
            "degree_range": "112.5° – 157.5° (मध्य 135°)",
            "associated_house": "२य व ११वां भाव (धन प्रवाह, नकदी व भोग)",
            "vastu_purusha_organ": "वास्तु पुरुष का दक्षिण वक्षस्थल व दायां कंधा",
            "chakra_organ": "Hormones, Reproductive Health, Liquid Cash Flow, Marital Bliss, Cooking Fire",
            "gemstone": "हीरा / ओपल (Diamond / White Zircon)",
            "metal": "चांदी व कांसा (Silver / Bronze)",
            "botanical": "गूलर (Udumbara), अनार, गुलाब, पलाश",
            "color_therapy": "क्रीम, हल्का गुलाबी, चमकदार सफेद, पेस्टल पीच (Cream / Pastel Pink)",
            "symptoms_of_defect": "महिलाओं का निरंतर अस्वस्थ रहना, नकदी की तंगी, वैवाहिक कलह, अग्नि भय, दुर्घटना, हार्मोनल असंतुलन।",
            "mantra": "ॐ शुं शुक्राय नमः ॥",
            "remedy_hi": "रसोईघर और विद्युत उपकरण आग्नेय कोण में रखें। इस दिशा में पानी का बोरिंग या भूमिगत टंकी कभी न बनाएं। क्रीम या हल्का गुलाबी रंग प्रयोग करें।",
            "non_destructive_remedy": "यदि आग्नेय में जल तत्व या टॉयलेट हो तो जिंक/कॉपर स्ट्रिप से ऊर्जा सील करें और आग्नेय कोण में २४ घंटे जलने वाला शून्य वाट का लाल बल्ब लगाएं।",
            "shastra_shloka": "आग्नेय्यां हुतभुक् पाको भोक्ता चैव न सीदति । अत्रैव पावकस्थानं धनधान्यविवर्धनम् ॥"
        },
        "South": {
            "deity": "Yama (धर्मराज यम)",
            "degree_range": "157.5° – 202.5° (मध्य 180°)",
            "associated_house": "१०म भाव (कर्म, पद-प्रतिष्ठा, पराक्रम व कीर्ति)",
            "vastu_purusha_organ": "वास्तु पुरुष की दाईं कोहनी व पसलियां",
            "chakra_organ": "Blood, Bone Marrow, Muscular Strength, Courage, Siblings, Executive Action",
            "gemstone": "लाल मूंगा (Red Coral)",
            "metal": "तांबा (Copper) व पीतल",
            "botanical": "खैर (Khadira), नीम, अशोक, लाल कनेर",
            "color_therapy": "गहरा लाल, टेराकोटा, कत्थई, महोगनी (Deep Red / Terracotta)",
            "symptoms_of_defect": "रक्त विकार, कानूनी विवाद, भाइयों में वैमनस्य, दुर्घटना का भय, मान-प्रतिष्ठा में हानि, अनपेक्षित शत्रुता।",
            "mantra": "ॐ क्रां क्रीं क्रौं सः भौमाय नमः ॥",
            "remedy_hi": "दक्षिण की दीवारें उत्तर से ऊँची और भारी रखें। दक्षिण द्वार दोष पर तांबे की पट्टी व मंगल यंत्र स्थापित करें। नीम या अशोक का वृक्ष लगाएं।",
            "non_destructive_remedy": "दक्षिण दिशा में 3 ब्रास या कॉपर हेलिक्स लगाएं। यदि दक्षिण दिशा खुली हो तो वहां भारी वजनदार वस्तुएं अथवा लाल त्रिकोण पिरामिड रखें।",
            "shastra_shloka": "याम्ये यमः शमं कुर्याद् विश्रामं च विनिर्दिशेत् । उच्चता भारसंयुक्ता सर्वकल्याणकारिणी ॥"
        },
        "South-West": {
            "deity": "Nirriti / Pitrus (पितृ देव)",
            "degree_range": "202.5° – 247.5° (मध्य 225°)",
            "associated_house": "८म व १२वां भाव (आयु, स्थायित्व, मोक्ष व अवचेतन)",
            "vastu_purusha_organ": "वास्तु पुरुष की जांघ, गुदा व पैर",
            "chakra_organ": "Stability, Lifespan, Nervous Balance, Ancestral Blessings, Authority of Head of Family",
            "gemstone": "गोमेद (Hessonite)",
            "metal": "रांगा / सीसा (Lead) व भारी पीतल",
            "botanical": "दूर्वा, चंदन, भारी बड़े छायादार वृक्ष",
            "color_therapy": "पीला-भूरा, मिट्टी का रंग, खाकी, सरसों पीला (Earthy Brown / Ochre Yellow)",
            "symptoms_of_defect": "पारिवारिक अस्थिरता, अकाल मृत्यु भय, गृहस्वामी का कमजोर स्वास्थ्य, निर्णय दोष, कोर्ट कचहरी, असहनीय ऋण।",
            "mantra": "ॐ भ्रां भ्रीं भ्रौं सः राहवे नमः ॥",
            "remedy_hi": "नैऋत्य कोण को घर का सबसे भारी और ऊँचा कोना बनाएं। यहाँ बोरिंग, गड्ढा या शौचालय कभी न बनाएं। दोष निवारण हेतु राहु यंत्र एवं लेड पिरामिड लगाएं।",
            "non_destructive_remedy": "नैऋत्य में टॉयलेट या कट होने पर 3 लेड (सीसा) हेलिक्स जमीन में दबाएं तथा भारी ब्रास नंदी अथवा हाथी का जोड़ा रखें।",
            "shastra_shloka": "नैऋत्यां नैऋतो रक्षो भारं तत्र समाचरेत् । गभीरं न खनेद् भूमिं स्थिरत्वं तत्र संस्थितम् ॥"
        },
        "West": {
            "deity": "Varuna (वरुण देव)",
            "degree_range": "247.5° – 292.5° (मध्य 270°)",
            "associated_house": "७म व ११वां भाव (व्यापार, साझेदारी, लाभ व कर्मफल)",
            "vastu_purusha_organ": "वास्तु पुरुष का उदर व बायां घुटना",
            "chakra_organ": "Bones, Joints, Discipline, Long-term Gains, Longevity, Karma Realization",
            "gemstone": "नीलम (Blue Sapphire) / जामुनिया",
            "metal": "लोहा (Iron) व स्टेनलेस स्टील",
            "botanical": "शमी (खेजड़ी), पीपल (भवन से दूर), नीले पुष्प",
            "color_therapy": "गहरा नीला, जामुनी, स्लेटी, चारकोल (Navy Blue / Charcoal Gray)",
            "symptoms_of_defect": "गठिया, जोड़ों का दर्द, व्यापार में धोखा, कर्म का फल न मिलना, अकारण विलंब, सेवकों का विद्रोह, असंतोष।",
            "mantra": "ॐ प्रां प्रीं प्रौं सः शनैश्चराय नमः ॥",
            "remedy_hi": "पश्चिम दिशा में शमी का वृक्ष शनिवार या शनि होरा में लगाएं। लोहे का शनि यंत्र अथवा नीले क्रिस्टल स्थापित करें। ओवरहेड वाटर टैंक लगाएं।",
            "non_destructive_remedy": "पश्चिम दिशा के दोष पर स्टील या ब्रास हेलिक्स लगाएं और शनिवार को सरसों के तेल का दीपक पश्चिम दिशा में प्रज्वलित करें।",
            "shastra_shloka": "वारुणे वरुणो दद्याद् भोजनं पानमेव च । लाभस्थानं विदुः प्राज्ञाः पश्चिमे स्थिरवृद्धये ॥"
        },
        "North-West": {
            "deity": "Vayu Dev (वायु देव)",
            "degree_range": "292.5° – 337.5° (मध्य 315°)",
            "associated_house": "३य व १२वां भाव (यात्रा, गति, मनोभाव व संबंध)",
            "vastu_purusha_organ": "वास्तु पुरुष की बाईं कोहनी व पसलियां",
            "chakra_organ": "Mind, Mental Peace, Fluids, Mother's Health, Travel, Supportive Relationships",
            "gemstone": "मोती (Natural Pearl) / मूनस्टोन",
            "metal": "चांदी (Pure Silver) व कांस्य",
            "botanical": "पलाश (Dhak), चमेली, मोगरा, सफेद फूल",
            "color_therapy": "दूधिया सफेद, पर्ल व्हाइट, चमकदार सिल्वर (Milk White / Pearl Silver)",
            "symptoms_of_defect": "अनिद्रा, अत्यधिक मानसिक चंचलता व अवसाद, माता का अस्वस्थ रहना, यात्राओं में हानि, अनपेक्षित कानूनी उलझनें।",
            "mantra": "ॐ श्रां श्रीं श्रौं सः चन्द्रमसे नमः ॥",
            "remedy_hi": "वायव्य दिशा में हवा का आवागमन सुगम रखें। श्वेत रंग, चांदी का स्वास्तिक या बहते पानी का छोटा फव्वारा लगाएं। चंद्र यंत्र स्थापित करें।",
            "non_destructive_remedy": "वायव्य में 3 पीतल की विंड चाइम (Wind Chimes) लटकाएं। वायव्य कोण में सफेद संगमरमर की चौकी पर शंख में गंगाजल भरकर रखें।",
            "shastra_shloka": "वायव्ये मारुतः स्थानं गतिशीलं विधीयते । धान्यागारं च कुर्याद्धि पशुस्थानं तथैव च ॥"
        },
        "North": {
            "deity": "Kubera / Lord Vishnu",
            "degree_range": "337.5° – 22.5° (मध्य 0°/360°)",
            "associated_house": "४था व ११वां भाव (बुध, कुबेर व सुख-संपत्ति)",
            "vastu_purusha_organ": "वास्तु पुरुष का हृदय व वक्षस्थल",
            "chakra_organ": "Intellect, Communication, Financial Growth, Nervous System, Business Trade",
            "gemstone": "पन्ना (Emerald) / हरा ओनेक्स",
            "metal": "कांसा व पीतल (Bronze / Brass)",
            "botanical": "अपामार्ग, तुलसी, मनी प्लांट, हरसिंगार",
            "color_therapy": "हल्का हरा, पिस्ता, समुद्री हरा, पुदीना (Pista Green / Sea Green)",
            "symptoms_of_defect": "व्यापार में अचानक रुकावट, वाणी दोष, नए अवसर न मिलना, फेफड़े व स्नायु विकार, संचित कोष का विनाश।",
            "mantra": "ॐ ब्रां ब्रीं ब्रौं सः बुधाय नमः ॥",
            "remedy_hi": "उत्तर दिशा कुबेर का स्थान है। यहाँ तिजोरी उत्तर दिशा की ओर खुलती हुई रखें। तुलसी का पौधा, बुध यंत्र व कुबेर यंत्र लगाएं।",
            "non_destructive_remedy": "यदि उत्तर दिशा भारी या दोषयुक्त हो तो वहां ब्रास की सील पट्टी लगाएं तथा ग्रीन एवेंच्यूरिन पिरामिड व कुबेर पात्र स्थापित करें।",
            "shastra_shloka": "कौबेरे तु कुबेरः स्यात् सर्वद्रव्यप्रदायकः । खुला जलं च तत्रैव धनवृद्धिकरं परम् ॥"
        },
        "North-East": {
            "deity": "Shiva / Ishana (देवाधिदेव महादेव)",
            "degree_range": "22.5° – 67.5° (मध्य 45°)",
            "associated_house": "५म व ९वां भाव (धर्म, सात्विक बुद्धि व गुरु कृपा)",
            "vastu_purusha_organ": "वास्तु पुरुष का सिर, शिखा व ललाट",
            "chakra_organ": "Spiritual Wisdom, Progeny, Family Harmony, Higher Divine Knowledge, Brain Crown",
            "gemstone": "पीला पुखराज (Yellow Sapphire)",
            "metal": "स्वर्ण व पीतल (Gold / Brass)",
            "botanical": "केला, पीपल, चंपा, तुलसी, चंदन",
            "color_therapy": "हल्का पीला, नींबू पीला, स्वर्णिम, शुभ्र श्वेत (Lemon Yellow / Bright White)",
            "symptoms_of_defect": "संतान कष्ट, मानसिक अवसाद, भ्रम, पूजा-पाठ में मन न लगना, वंश वृद्धि में बाधा, घोर दरिद्रता व ज्ञान शून्यता।",
            "mantra": "ॐ ग्रां ग्रीं ग्रौं सः गुरवे नमः ॥",
            "remedy_hi": "ईशान कोण भगवान शिव और बृहस्पति का पावन स्थान है। यहाँ पूजा घर या भूमिगत जल स्रोत रखें। यहाँ शौचालय या भारी सीढ़ी महादोष उत्पन्न करती है।",
            "non_destructive_remedy": "ईशान में टॉयलेट या भारी सीढ़ी का दोष होने पर पीतल का गुरु यंत्र, स्फटिक श्रीयंत्र एवं 24 घंटे तांबे के पात्र में गंगाजल भरकर रखें।",
            "shastra_shloka": "ईशाने च महादेवो जलस्थानं प्रशस्यते । देवस्थानं च तत्रैव सर्वसिद्धिकरं भवेत् ॥"
        },
        "Center": {
            "deity": "Lord Brahma (सृष्टिकर्ता ब्रह्मा)",
            "degree_range": "केंद्रीय 9 पद (Central Cosmic Core)",
            "associated_house": "समस्त केंद्र भाव (१, ४, ७, १० - विष्णु स्थान)",
            "vastu_purusha_organ": "वास्तु पुरुष की नाभि व उदर केंद्र",
            "chakra_organ": "Universal Cosmic Energy, Life Equilibrium, Navel of Vastu Purusha",
            "gemstone": "नवरत्न (Navaratna)",
            "metal": "अष्टधातु व शुद्ध सोना (Ashtadhatu / Gold)",
            "botanical": "तुलसी क्यारी, सुगंधित पुष्प पात्र",
            "color_therapy": "पारदर्शी, प्राकृतिक प्रकाश, स्फटिक श्वेत (Crystal Clear / Sky White)",
            "symptoms_of_defect": "गृहस्वामी को हृदय व उदर विकार, पूरे परिवार में मानसिक अशान्ति, धन का निरंतर पलायन, जीवन में संतुलनहीनता।",
            "mantra": "ॐ नमो भगवते वासुदेवाय ॥",
            "remedy_hi": "घर के मध्य भाग को ब्रह्मस्थान कहते हैं। इसे पूर्णतः खुला, प्रकाशयुक्त और भारमुक्त रखें। यहां कोई खंभा या गड्ढा न बनाएं।",
            "non_destructive_remedy": "यदि ब्रह्मस्थान में बीम या दीवार हो तो बीम के दोनों ओर कॉपर हेलिक्स लगाएं तथा केंद्र में स्फटिक श्रीयंत्र अथवा ब्रास चक्र स्थापित करें।",
            "shastra_shloka": "ब्रह्मस्थाने स्वयं ब्रह्मा मध्यभागे प्रतिष्ठितः । भारस्तत्र न कर्तव्यः स्तम्भो वाऽपि जलाशयः ॥"
        }
    }

    # Helper function that eliminates any leading whitespace so Markdown never treats HTML as code blocks
    def _v_render(html_markup: str):
        compact = "".join(line.strip() for line in html_markup.splitlines() if line.strip())
        st.markdown(compact, unsafe_allow_html=True)

    # Active Native Micro-Planetary Longitudes & DMS Console
    lagna_sname = getattr(chart, "lagna_sign_name", "Aries")
    moon = chart.planets.get("Moon")
    if moon:
        m_deg = getattr(moon, "sign_degree", 0.0)
        m_ansh = int(m_deg)
        m_kala = int(round((m_deg - m_ansh) * 60.0))
        if m_kala >= 60:
            m_kala = 0
            m_ansh += 1
        m_dms = f"{m_ansh}° {m_kala:02d}'"
        m_nak = getattr(moon, "nakshatra_name", getattr(moon, "nakshatra", "—"))
        m_pada = getattr(moon, "nakshatra_pada", getattr(moon, "pada", 1))
        moon_str = f"{moon.sign_name} {m_dms} [{m_nak}-P{m_pada}]"
    else:
        moon_str = "—"

    # Active Dasha Lord Micro Coordinates
    dasha_p = chart.planets.get(active_dasha_lord) if active_dasha_lord else None
    if dasha_p:
        dp_deg = getattr(dasha_p, "sign_degree", 0.0)
        dp_ansh = int(dp_deg)
        dp_kala = int(round((dp_deg - dp_ansh) * 60.0))
        if dp_kala >= 60:
            dp_kala = 0
            dp_ansh += 1
        dp_dms = f"{dp_ansh}° {dp_kala:02d}'"
        dp_nak = getattr(dasha_p, "nakshatra_name", getattr(dasha_p, "nakshatra", "—"))
        dp_pada = getattr(dasha_p, "nakshatra_pada", getattr(dasha_p, "pada", 1))
        dasha_str = f"{active_dasha_lord} ({dasha_p.sign_name} {dp_dms} [{dp_nak}-P{dp_pada}])"
    else:
        dasha_str = active_dasha_lord or "—"

    active_zone = next((z for z in v_zones if z.get("is_active_dasha")), None)
    scores = [z.get("score", 70) for z in v_zones]
    avg_score = int(round(sum(scores) / len(scores))) if scores else 0

    # Module Specific Unified Compact Expanders & Tabs CSS
    st.markdown("""
    <style>
    /* Compact clean margin for Expanders in Vastu View */
    div[data-testid="stExpander"] {
        margin-top: 6px !important;
        margin-bottom: 6px !important;
    }
    div[data-testid="stExpander"] details {
        border-radius: 8px !important;
    }
    </style>
    """, unsafe_allow_html=True)

    v_tab_titles = tabs
    v_tabs = st.tabs(tabs)

    # -------------------------------------------------------------
    # TAB 0: समग्र वास्तु मण्डल (Overview, Compass & Comparative Table)
    # -------------------------------------------------------------
    with v_tabs[0]:
        sorted_zones = sorted(v_zones, key=lambda x: x.get("score", 70), reverse=True)
        best_zone = sorted_zones[0] if sorted_zones else None
        worst_zone = sorted_zones[-1] if sorted_zones else None

        # Subtabs under Tab 0: 360° दिशा चक्र एवं नवदिशा शास्त्रीय तुलनात्मक सारणी
        subtab_v_compass, subtab_v_table = st.tabs([
            "1. 🧭 360° वास्तु दिशा चक्र",
            "2. 📋 नवदिशा शास्त्रीय तुलनात्मक सारणी"
        ])

        with subtab_v_compass:
            compass_col, info_col = st.columns([1.1, 1.0])
            with compass_col:
                st.markdown("##### 🧭 360° वास्तु दिशा चक्र (Cosmic Compass Wheel)")
                compass_svg = render_vastu_compass_wheel_svg(v_zones, is_dark=_is_dark)
                _v_render(f'<div style="width:100%;display:flex;justify-content:center;margin:8px 0;">{compass_svg}</div>')
                st.caption("🟢 हरा (≥75): सुसंगत व शुभ | 🟡 पीला (50-74): मध्यम सतर्कता | 🔴 लाल (<50): संवेदनशील/दोष निवारण आवश्यक")

            with info_col:
                st.markdown("##### 📜 वास्तु-ज्योतिष आधार एवं कुण्डली समन्वय")
                _v_render(f"""
                <div style="background: {card_bg}; border: 1.5px solid {card_bdr}; border-radius: 12px; padding: 16px; font-size: 13px; line-height: 1.6; color: {text_primary};">
                    <p style="margin-top: 0;"><b>वास्तु-ज्योतिष का शास्त्रीय नियम:</b> जातक की जन्मकुण्डली में जिस दिशा का स्वामी ग्रह <b>उच्च, स्वराशि अथवा दिग्बली</b> होता है, भवन की वह दिशा स्वतः ऊर्जावान और भाग्यवर्धक सिद्ध होती है। इसके विपरीत जब दिशा स्वामी <b>नीच, शत्रु राशि, अस्त, वक्री अथवा ६, ८, १२वें भाव</b> में स्थित हो तो संबंधित दिशा में वास्तु दोष का दुष्प्रभाव कई गुना बढ़ जाता है।</p>
                    <div style="background: {row_alt_bg}; border-left: 4px solid #F59E0B; padding: 8px 12px; border-radius: 4px; margin: 10px 0; font-size: 12px;">
                        <i>"यस्मिन् देशे स्थिता देवा दिशामुख्याः समन्ततः । तं देशं वास्तुमित्याहुः सर्वकामफलप्रदम् ॥"</i><br>
                        <span style="color: {text_secondary};">— मयमतम् एवं विश्वकर्मा प्रकाश</span>
                    </div>
                    <p style="margin-bottom: 0;">ऊपर दिए गए प्रत्येक दिशा के स्वतंत्र टैब में जाकर आप अपनी कुण्डली के अनुसार उस दिशा के <b>विस्तृत पैरामीटर्स, आदर्श वास्तु नियोजन, वर्जित निर्माण, दोष के लक्षण एवं ५-आयामी अचूक शास्त्रीय उपचार</b> का अध्ययन कर सकते हैं।</p>
                </div>
                """)

        with subtab_v_table:
            st.markdown("##### 📋 नवदिशा शास्त्रीय तुलनात्मक सारणी (9-Direction Master Matrix)")

            tbl_html = f'<div style="overflow-x: auto; border: 1.5px solid {card_bdr}; border-radius: 10px; margin-bottom: 16px;">'
            tbl_html += f'<table style="width: 100%; border-collapse: collapse; text-align: left; background: {card_bg}; font-size: 12px;">'
            tbl_html += f'<thead><tr style="background: {hdr_bg}; border-bottom: 2px solid {hdr_bdr};">'
            tbl_html += f'<th style="padding: 10px 12px; font-weight: 800; color: {text_primary};">दिशा (Direction)</th>'
            tbl_html += f'<th style="padding: 10px 12px; font-weight: 800; color: {text_primary};">दिक्पाल व स्वामी</th>'
            tbl_html += f'<th style="padding: 10px 12px; font-weight: 800; color: {text_primary};">तत्व</th>'
            tbl_html += f'<th style="padding: 10px 12px; font-weight: 800; color: {text_primary};">कुण्डली भाव, सूक्ष्म अंश-कला व स्वभाव</th>'
            tbl_html += f'<th style="padding: 10px 12px; font-weight: 800; color: {text_primary};">दिग्बल</th>'
            tbl_html += f'<th style="padding: 10px 12px; font-weight: 800; color: {text_primary}; text-align: center;">सामंजस्य स्कोर</th>'
            tbl_html += f'<th style="padding: 10px 12px; font-weight: 800; color: {text_primary}; text-align: center;">दोष जोखिम</th>'
            tbl_html += f'<th style="padding: 10px 12px; font-weight: 800; color: {text_primary};">प्राथमिक शास्त्रीय उपचार</th>'
            tbl_html += '</tr></thead><tbody>'

            for idx, z in enumerate(v_zones):
                bg_r = row_alt_bg if idx % 2 == 1 else row_bg
                r_risk = z.get("defect_risk", "Moderate Risk")
                if r_risk == "Harmonious":
                    b_color = "#10B981"
                    b_bg = "#ECFDF5" if not _is_dark else "#064E3B"
                    b_txt = "✨ सुसंगत"
                elif r_risk == "Moderate Risk":
                    b_color = "#F59E0B"
                    b_bg = "#FFFBEB" if not _is_dark else "#78350F"
                    b_txt = "⚠️ मध्यम जोखिम"
                else:
                    b_color = "#EF4444"
                    b_bg = "#FEF2F2" if not _is_dark else "#7F1D1D"
                    b_txt = "🚨 उच्च दोष"

                h_val = z.get('house')
                dms_val = z.get('dms_str', z.get('degree_str', ''))
                nak_info = f"[{z.get('nakshatra_name', '')}-P{z.get('nakshatra_pada', '')}]" if z.get('nakshatra_name') else ""
                if h_val is not None and str(h_val) != "":
                    h_str = f"भाव {h_val}"
                    if z.get('sign_name') or dms_val:
                        h_str += f" ({z.get('sign_name', '')} {dms_val} {nak_info})".strip()
                else:
                    h_str = "केन्द्र भाव (1, 4, 7, 10)" if "ब्रह्म" in str(z.get('hindi', '')) or z.get('direction') == 'Center' else "तटस्थ"

                d_str = f"{z.get('swabhav', 'सामान्य')} • {z.get('status', 'सामान्य')}"
                if z.get('is_combust'): d_str += " [अस्त]"
                if z.get('is_retrograde'): d_str += " [वक्री]"

                meta_d = z.get("meta", {})
                fb_d = VASTU_PARAM_FALLBACKS.get(z.get("direction", ""), {})

                deity_name = meta_d.get("deity") or fb_d.get("deity", "")
                rem_text = meta_d.get("non_destructive_remedy") or meta_d.get("remedy_hi") or fb_d.get("non_destructive_remedy", "")

                tbl_html += f'<tr style="background-color: {bg_r}; border-bottom: 1px solid {row_bdr};">'
                tbl_html += f'<td style="padding: 8px 12px; font-weight: 700; color: {text_primary}; white-space: nowrap;">{z.get("hindi", "")}</td>'
                tbl_html += f'<td style="padding: 8px 12px; color: {text_secondary};">{deity_name} / <b>{z.get("lord", "")}</b></td>'
                tbl_html += f'<td style="padding: 8px 12px; color: {text_secondary};">{z.get("element", "")}</td>'
                tbl_html += f'<td style="padding: 8px 12px; color: {text_primary};">{h_str}<br><span style="font-size: 11px; color: {text_secondary};">{d_str}</span></td>'
                tbl_html += f'<td style="padding: 8px 12px; color: {text_secondary};">{z.get("digbala", "तटस्थ")}</td>'
                tbl_html += f'<td style="padding: 8px 12px; text-align: center;"><b style="color: {b_color}; font-size: 13px;">{z.get("score", 70)}/100</b></td>'
                tbl_html += f'<td style="padding: 8px 12px; text-align: center;"><span style="background: {b_bg}; color: {b_color}; border: 1px solid {b_color}; padding: 2px 8px; border-radius: 12px; font-weight: 700; font-size: 11px;">{b_txt}</span></td>'
                tbl_html += f'<td style="padding: 8px 12px; font-size: 11.5px; color: {text_secondary}; max-width: 250px;">{rem_text[:75]}...</td>'
                tbl_html += '</tr>'

            tbl_html += '</tbody></table></div>'
            _v_render(tbl_html)

        _v_render("<div style='height: 14px;'></div>")

        # Bottom Collapsible KPI Summary Cards & Dasha Alert under Tab 0
        with st.expander("📊 समग्र वास्तु सूचकांक, संवेदनशील दिशा एवं महादशा विश्लेषण (Executive Summary)", expanded=False):
            kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
            with kpi_col1:
                _v_render(f"""
                <div style="background: {card_bg}; border: 1.5px solid #10B981; border-radius: 12px; padding: 14px; text-align: center; box-shadow: 0 2px 8px rgba(0,0,0,0.05);">
                    <div style="font-size: 11.5px; font-weight: 700; color: #10B981; text-transform: uppercase;">🏆 सर्वोच्च सामंजस्य दिशा</div>
                    <div style="font-size: 18px; font-weight: 900; color: {text_primary}; margin: 4px 0;">{best_zone.get('hindi', 'N/A') if best_zone else 'N/A'}</div>
                    <div style="font-size: 12px; color: {text_secondary};">स्कोर: <b style="color: #10B981;">{best_zone.get('score', 0) if best_zone else 0}/100</b> | {best_zone.get('lord', '') if best_zone else ''}</div>
                </div>
                """)
            with kpi_col2:
                _v_render(f"""
                <div style="background: {card_bg}; border: 1.5px solid #EF4444; border-radius: 12px; padding: 14px; text-align: center; box-shadow: 0 2px 8px rgba(0,0,0,0.05);">
                    <div style="font-size: 11.5px; font-weight: 700; color: #EF4444; text-transform: uppercase;">⚠️ सर्वाधिक संवेदनशील दिशा</div>
                    <div style="font-size: 18px; font-weight: 900; color: {text_primary}; margin: 4px 0;">{worst_zone.get('hindi', 'N/A') if worst_zone else 'N/A'}</div>
                    <div style="font-size: 12px; color: {text_secondary};">स्कोर: <b style="color: #EF4444;">{worst_zone.get('score', 0) if worst_zone else 0}/100</b> | {worst_zone.get('lord', '') if worst_zone else ''}</div>
                </div>
                """)
            with kpi_col3:
                _v_render(f"""
                <div style="background: {card_bg}; border: 1.5px solid #3B82F6; border-radius: 12px; padding: 14px; text-align: center; box-shadow: 0 2px 8px rgba(0,0,0,0.05);">
                    <div style="font-size: 11.5px; font-weight: 700; color: #3B82F6; text-transform: uppercase;">🌿 पंचतत्व संतुलन</div>
                    <div style="font-size: 18px; font-weight: 900; color: {text_primary}; margin: 4px 0;">जल • अग्नि • वायु • पृथ्वी</div>
                    <div style="font-size: 12px; color: {text_secondary};">आकाश (ब्रह्मस्थान): <b style="color: #3B82F6;">{zone_dict.get('Center', {}).get('score', 85)}/100</b></div>
                </div>
                """)
            with kpi_col4:
                idx_color = "#10B981" if avg_score >= 75 else "#F59E0B" if avg_score >= 50 else "#EF4444"
                _v_render(f"""
                <div style="background: {card_bg}; border: 1.5px solid {idx_color}; border-radius: 12px; padding: 14px; text-align: center; box-shadow: 0 2px 8px rgba(0,0,0,0.05);">
                    <div style="font-size: 11.5px; font-weight: 700; color: {idx_color}; text-transform: uppercase;">📊 समग्र वास्तु सूचकांक</div>
                    <div style="font-size: 22px; font-weight: 900; color: {idx_color}; margin: 2px 0;">{avg_score}<span style="font-size: 14px; color: {text_secondary};">/100</span></div>
                    <div style="font-size: 12px; color: {text_secondary};">9 दिशाओं का औसत सामंजस्य</div>
                </div>
                """)

            active_zone = next((z for z in v_zones if z.get("is_active_dasha")), None)
            if active_zone and active_dasha_lord:
                _v_render(f"""
                <div style="background: {'#1E1B4B' if _is_dark else '#EEF2FF'}; border: 1.5px solid #6366F1; border-radius: 12px; padding: 12px 18px; margin-top: 14px; display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 10px;">
                    <div style="display: flex; align-items: center; gap: 12px;">
                        <span style="font-size: 26px;">⚡</span>
                        <div>
                            <div style="font-weight: 800; color: #4F46E5; font-size: 14px;">वर्तमान सक्रिय महादशा दिशा: {active_zone.get('hindi', '')} ({active_zone.get('direction', '')})</div>
                            <div style="font-size: 12px; color: {text_secondary};">आपकी वर्तमान विंशोत्तरी महादशा स्वामी <b>{active_dasha_lord}</b> हैं। इस समय भवन की <b>{active_zone.get('hindi', '')}</b> दिशा सर्वाधिक सक्रिय कंपन पैदा कर रही है, इसे वास्तु-दोषमुक्त व प्रकाशयुक्त रखें।</div>
                        </div>
                    </div>
                    <div style="text-align: right;">
                        <span style="background: #4F46E5; color: #FFFFFF; padding: 4px 10px; border-radius: 12px; font-weight: 700; font-size: 11.5px;">दिशा स्कोर: {active_zone.get('score', 70)}/100</span>
                    </div>
                </div>
                """)

    # -------------------------------------------------------------
    # TABS 1 to 9: INDIVIDUAL DIRECTION DEEP DIVE TABS
    # -------------------------------------------------------------
    dir_keys_order = [
        "East", "South-East", "South", "South-West",
        "West", "North-West", "North", "North-East", "Center"
    ]

    for tab_idx, d_key in enumerate(dir_keys_order, start=1):
        with v_tabs[tab_idx]:
            z = zone_dict.get(d_key)
            if not z:
                st.warning(f"{d_key} दिशा का विश्लेषण उपलब्ध नहीं है।")
                continue

            meta = z.get("meta", {})
            fb = VASTU_PARAM_FALLBACKS.get(d_key, {})
            score = z.get("score", 70)
            risk = z.get("defect_risk", "Harmonious")

            # Guaranteed non-empty values using fallbacks
            deity_val = meta.get("deity") or fb.get("deity", "")
            deg_val = meta.get("degree_range") or fb.get("degree_range", "")
            house_val = meta.get("associated_house") or fb.get("associated_house", "")
            organ_val = meta.get("vastu_purusha_organ") or fb.get("vastu_purusha_organ", "")
            chakra_val = meta.get("chakra_organ") or fb.get("chakra_organ", "")
            gem_val = meta.get("gemstone") or fb.get("gemstone", "")
            metal_val = meta.get("metal") or fb.get("metal", "")
            botanical_val = meta.get("botanical") or fb.get("botanical", "")
            color_val = meta.get("color_therapy") or fb.get("color_therapy", "")
            symptoms_val = meta.get("symptoms_of_defect") or fb.get("symptoms_of_defect", "")
            mantra_val = meta.get("mantra") or fb.get("mantra", "")
            remedy_val = meta.get("remedy_hi") or fb.get("remedy_hi", "")
            nondestr_val = meta.get("non_destructive_remedy") or fb.get("non_destructive_remedy", "")
            shloka_val = meta.get("shastra_shloka") or fb.get("shastra_shloka", "")

            if risk == "Harmonious":
                border_color = "#10B981"
                badge_bg = "#ECFDF5" if not _is_dark else "#064E3B"
                badge_color = "#10B981"
                badge_text = "✨ पूर्ण सुसंगत (Harmonious & Blessed)"
            elif risk == "Moderate Risk":
                border_color = "#F59E0B"
                badge_bg = "#FFFBEB" if not _is_dark else "#78350F"
                badge_color = "#F59E0B"
                badge_text = "⚠️ मध्यम जोखिम (Moderate Sensitivity)"
            else:
                border_color = "#EF4444"
                badge_bg = "#FEF2F2" if not _is_dark else "#7F1D1D"
                badge_color = "#EF4444"
                badge_text = "🚨 उच्च दोष जोखिम (High Risk / Requires Remediation)"

            # Direction Header Hero Card
            dasha_badge_html = '<span style="background: #4F46E5; color: white; border-radius: 12px; padding: 3px 9px; font-size: 11px; margin-left: 8px; font-weight: 700;">⚡ सक्रिय महादशा दिशा</span>' if z.get("is_active_dasha") else ''
            _v_render(f"""
            <div style="background: {card_bg}; border: 1.5px solid {border_color}; border-left: 6px solid {border_color}; border-radius: 12px; padding: 16px 20px; margin-bottom: 20px; box-shadow: 0 4px 14px rgba(0,0,0,0.06);">
                <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
                    <div>
                        <div style="font-size: 22px; font-weight: 900; color: {text_primary};">{z.get('hindi', '')} &nbsp;<span style="font-size: 15px; color: {text_secondary}; font-weight: 600;">({z.get('direction', '')} Zone)</span>{dasha_badge_html}</div>
                        <div style="font-size: 13px; color: {text_secondary}; margin-top: 4px;">
                            🏛️ <b>दिक्पाल:</b> {deity_val} &nbsp;|&nbsp; 
                            🪐 <b>स्वामी ग्रह:</b> {z.get('lord', '')} &nbsp;|&nbsp; 
                            🌿 <b>पंचतत्व:</b> {z.get('element', '')} &nbsp;|&nbsp; 
                            📐 <b>कोणीय विस्तार:</b> {deg_val}
                        </div>
                    </div>
                    <div style="text-align: right;">
                        <span style="background: {badge_bg}; color: {badge_color}; border: 1.5px solid {border_color}; border-radius: 16px; padding: 4px 12px; font-weight: 800; font-size: 12px;">
                            {badge_text}
                        </span>
                        <div style="font-size: 18px; font-weight: 900; color: {border_color}; margin-top: 6px;">
                            सामंजस्य स्कोर: {score}/100
                        </div>
                    </div>
                </div>
            </div>
            """)

            # Two Column Split
            col_left, col_right = st.columns([1, 1])

            # Left Column: Astrological Analysis & Functional Architecture
            with col_left:
                st.markdown("##### 🪐 जन्म कुण्डली गणना एवं ज्योतिषीय स्थिति")

                combust_badge = "🔥 अस्त (Combust)" if z.get("is_combust") else "☀️ उदित (Normal)"
                retro_badge = "🔄 वक्री (Retrograde)" if z.get("is_retrograde") else "➡️ मार्गी (Direct)"
                swabhav_badge = z.get("swabhav", "सामान्य")
                dms_disp = z.get("dms_str", z.get("degree_str", "N/A"))
                nak_disp = f"{z.get('nakshatra_name', '—')} (चरण {z.get('nakshatra_pada', '—')})"

                _v_render(f"""
                <div style="background: {card_bg}; border: 1.5px solid {card_bdr}; border-radius: 10px; padding: 14px; margin-bottom: 16px; font-size: 12.5px; line-height: 1.6; color: {text_primary};">
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-bottom: 10px;">
                        <div><b>स्वामी ग्रह व स्वभाव:</b> {z.get('lord', '')} ({swabhav_badge})</div>
                        <div><b>सूक्ष्म राशि व अंश-कला:</b> {z.get('sign_name', 'N/A')} {dms_disp}</div>
                        <div><b>नक्षत्र एवं चरण:</b> {nak_disp}</div>
                        <div><b>कुण्डली भाव:</b> भाव {z.get('house', 'N/A')}</div>
                        <div><b>ग्रह गरिमा व अवस्था:</b> {z.get('status', 'सामान्य')}</div>
                        <div><b>दिग्बल स्थिति:</b> {z.get('digbala', 'तटस्थ')}</div>
                        <div><b>अस्त/वक्री:</b> {combust_badge} | {retro_badge}</div>
                    </div>
                    <div style="border-top: 1px solid {card_bdr}; padding-top: 8px;">
                        <div><b>👤 वास्तु पुरुष अंग:</b> {organ_val}</div>
                        <div><b>🎯 संबद्ध जीवन आयाम:</b> {chakra_val}</div>
                    </div>
                </div>
                """)

                # Special Brahmasthan Kendra Energy Flow Analysis
                if d_key == "Center":
                    k_b = z.get("kendra_benefics", [])
                    k_m = z.get("kendra_malefics", [])
                    b_txt = ", ".join(k_b) if k_b else "कोई शुभ ग्रह नहीं"
                    m_txt = ", ".join(k_m) if k_m else "कोई पाप ग्रह नहीं (परम शुभ)"
                    _v_render(f"""
                    <div style="background: {'#0F172A' if _is_dark else '#F0F9FF'}; border: 1.5px solid #0284C7; border-radius: 10px; padding: 12px 14px; margin-bottom: 16px; font-size: 12.5px;">
                        <b style="color: #0284C7; font-size: 13px;">🌌 चतुष्कोण केंद्र-संतुलन (Brahmasthan Kendra Energy Flow):</b>
                        <div style="margin-top: 6px; display: grid; grid-template-columns: 1fr 1fr; gap: 8px;">
                            <div><b>🌿 केंद्र में शुभ ग्रह (बलवर्धक):</b><br><span style="color: {'#38BDF8' if _is_dark else '#0369A1'};">{b_txt}</span></div>
                            <div><b>⚠️ केंद्र में क्रूर ग्रह (वेध कारक):</b><br><span style="color: {'#FCA5A5' if _is_dark else '#B91C1C'};">{m_txt}</span></div>
                        </div>
                    </div>
                    """)

                st.markdown("##### 🏛️ वास्तु नियोजन: शुभ एवं वर्जित व्यवस्था")
                ideal_items = "".join([f"<li>{item}</li>" for item in meta.get("ideal_uses", [])])
                avoid_items = "".join([f"<li>{item}</li>" for item in meta.get("avoid", [])])

                _v_render(f"""
                <div style="display: flex; flex-direction: column; gap: 10px; margin-bottom: 16px;">
                    <div style="background: {'#064E3B' if _is_dark else '#F0FDF4'}; border: 1.5px solid #10B981; border-radius: 8px; padding: 10px 14px; color: {'#A7F3D0' if _is_dark else '#166534'}; font-size: 12.5px;">
                        <b style="color: #10B981; font-size: 13px;">✅ श्रेष्ठ एवं शुभ वास्तु उपयोग:</b>
                        <ul style="margin: 6px 0 0 16px; padding: 0;">
                            {ideal_items}
                        </ul>
                    </div>
                    <div style="background: {'#7F1D1D' if _is_dark else '#FEF2F2'}; border: 1.5px solid #EF4444; border-radius: 8px; padding: 10px 14px; color: {'#FECACA' if _is_dark else '#991B1B'}; font-size: 12.5px;">
                        <b style="color: #EF4444; font-size: 13px;">🚫 सर्वथा वर्जित निर्माण (Defects to Avoid):</b>
                        <ul style="margin: 6px 0 0 16px; padding: 0;">
                            {avoid_items}
                        </ul>
                    </div>
                </div>
                """)

                st.markdown("##### ⚠️ दिशा दोष के प्रमुख लक्षण (Affliction Symptoms)")
                _v_render(f"""
                <div style="background: {row_alt_bg}; border-left: 4px solid #F59E0B; border-radius: 4px; padding: 10px 14px; font-size: 12.5px; line-height: 1.5; color: {text_primary}; margin-bottom: 16px;">
                    {symptoms_val}
                </div>
                """)

            # Right Column: 5-Pillar Shastriya Remedies
            with col_right:
                st.markdown("##### 🪔 पंच-आयामी शास्त्रीय वास्तु उपाय (5-Pillar Remedy Suite)")

                _v_render(f"""
                <div style="display: flex; flex-direction: column; gap: 10px; margin-bottom: 16px; font-size: 12.5px;">
                    <div style="background: {card_bg}; border: 1.5px solid {card_bdr}; border-radius: 8px; padding: 10px 14px;">
                        <div style="font-weight: 800; color: #D97706; margin-bottom: 4px;">1. 🪔 यंत्र एवं धातु (Yantra & Metal):</div>
                        <div style="color: {text_primary};"><b>धातु:</b> {metal_val} &nbsp;|&nbsp; <b>रत्न:</b> {gem_val}</div>
                        <div style="color: {text_secondary}; font-size: 12px; margin-top: 2px;">{remedy_val}</div>
                    </div>
                    <div style="background: {'#78350F' if _is_dark else '#FFFBEB'}; border: 1.5px solid #F59E0B; border-radius: 8px; padding: 10px 14px;">
                        <div style="font-weight: 800; color: #D97706; margin-bottom: 4px;">2. 🕉️ वैदिक मंत्र एवं जप साधना:</div>
                        <div style="font-weight: 900; color: {'#FDE68A' if _is_dark else '#92400E'}; font-size: 13.5px; margin: 2px 0;">{mantra_val}</div>
                        <div style="color: {'#FDE68A' if _is_dark else '#B45309'}; font-size: 11.5px;">प्रतिदिन 108 बार अथवा दिशा शुद्धि के समय विधिवत पाठ करें।</div>
                    </div>
                    <div style="background: {card_bg}; border: 1.5px solid {card_bdr}; border-radius: 8px; padding: 10px 14px;">
                        <div style="font-weight: 800; color: #059669; margin-bottom: 4px;">3. 🌿 वनस्पति एवं कल्पवृक्ष (Botanical Plants):</div>
                        <div style="color: {text_primary};"><b>पूज्य वृक्ष/पौधे:</b> {botanical_val}</div>
                        <div style="color: {text_secondary}; font-size: 11.5px; margin-top: 2px;">इस दिशा की सकारात्मक ऊर्जा वृद्धि हेतु ये पौधे स्थापित करना अति-शुभ माना गया है।</div>
                    </div>
                    <div style="background: {card_bg}; border: 1.5px solid {card_bdr}; border-radius: 8px; padding: 10px 14px;">
                        <div style="font-weight: 800; color: #2563EB; margin-bottom: 4px;">4. 🎨 रंग चिकित्सा एवं प्रकाश व्यवस्था (Color Therapy):</div>
                        <div style="color: {text_primary};"><b>अनुकूल रंग:</b> {color_val}</div>
                        <div style="color: {text_secondary}; font-size: 11.5px; margin-top: 2px;">दीवारों के रंग, परदे, प्रकाश व्यवस्था एवं सजावट में इन रंगों का उपयोग ऊर्जा को संतुलित करता है।</div>
                    </div>
                    <div style="background: {'#1E1B4B' if _is_dark else '#EEF2FF'}; border: 1.5px solid #6366F1; border-radius: 8px; padding: 10px 14px;">
                        <div style="font-weight: 800; color: #4F46E5; margin-bottom: 4px;">5. 🛠️ बिना तोड़-फोड़ के शास्त्रीय वास्तु सुधार (Non-Destructive Fix):</div>
                        <div style="color: {'#C7D2FE' if _is_dark else '#312E81'}; font-weight: 600;">{nondestr_val}</div>
                    </div>
                </div>
                """)

            # Detailed Parameters Table for Direction
            st.markdown(f"##### 📊 {z.get('hindi', '')} दिशा के सम्पूर्ण शास्त्रीय मापदण्ड (15-Parameter Matrix)")

            p_rows = [
                ("दिशा एवं दिक्पाल (Direction & Deity)", f"{z.get('hindi', '')} ({z.get('direction', '')}) — {deity_val}"),
                ("दिशा स्वामी ग्रह व स्वभाव (Ruling Planet)", f"{z.get('lord', '')} ({z.get('swabhav', 'सामान्य')})"),
                ("पंचमहाभूत तत्व (Five Elements)", f"{z.get('element', '')}"),
                ("कोणीय विस्तार (Degree Range)", f"{deg_val}"),
                ("संबद्ध कुण्डली भाव (Kundali House)", f"{house_val}"),
                ("जातक की कुण्डली में ग्रह स्थिति", f"भाव {z.get('house', 'N/A')}, {z.get('sign_name', '')} {z.get('dms_str', z.get('degree_str', ''))} [{z.get('nakshatra_name', '')}-चरण {z.get('nakshatra_pada', '')}] — {z.get('swabhav', '')}"),
                ("ग्रह गरिमा एवं अवस्था (Dignity)", f"{z.get('status', 'सामान्य')} {'[अस्त]' if z.get('is_combust') else ''} {'[वक्री]' if z.get('is_retrograde') else ''}"),
                ("दिग्बल स्थिति (Directional Strength)", f"{z.get('digbala', 'तटस्थ')}"),
                ("वास्तु पुरुष शरीर अंग (Anatomy)", f"{organ_val}"),
                ("रत्न एवं उपरत्न (Gemstone)", f"{gem_val}"),
                ("शुभ धातु (Auspicious Metal)", f"{metal_val}"),
                ("पूज्य वनस्पति (Botanical Tree/Plant)", f"{botanical_val}"),
                ("रंग चिकित्सा (Color Therapy)", f"{color_val}"),
                ("सामंजस्य स्कोर एवं जोखिम स्तर", f"{score}/100 — {badge_text}"),
                ("अचूक बिना तोड़-फोड़ उपाय", f"{nondestr_val}")
            ]

            p_table_html = f'<div style="overflow-x: auto; border: 1.5px solid {card_bdr}; border-radius: 10px; margin-bottom: 20px;">'
            p_table_html += f'<table style="width: 100%; border-collapse: collapse; text-align: left; background: {card_bg}; font-size: 12.5px;">'
            p_table_html += f'<thead><tr style="background: {hdr_bg}; border-bottom: 2px solid {hdr_bdr};">'
            p_table_html += f'<th style="padding: 10px 14px; font-weight: 800; color: {text_primary}; width: 30%;">शास्त्रीय मापदण्ड (Parameter)</th>'
            p_table_html += f'<th style="padding: 10px 14px; font-weight: 800; color: {text_primary}; width: 70%;">कुण्डली एवं वास्तु विन्यास विवरण (Details)</th>'
            p_table_html += '</tr></thead><tbody>'

            for p_idx, (p_label, p_val) in enumerate(p_rows):
                p_bg = row_alt_bg if p_idx % 2 == 1 else row_bg
                p_table_html += f'<tr style="background-color: {p_bg}; border-bottom: 1px solid {row_bdr};">'
                p_table_html += f'<td style="padding: 8px 14px; font-weight: 700; color: {text_primary};">{p_label}</td>'
                p_table_html += f'<td style="padding: 8px 14px; color: {text_secondary};">{p_val}</td>'
                p_table_html += '</tr>'

            p_table_html += '</tbody></table></div>'
            _v_render(p_table_html)

            # Shastra Shloka Callout Box
            if shloka_val:
                _v_render(f"""
                <div style="background: {row_alt_bg}; border-left: 5px solid #6366F1; border-radius: 6px; padding: 12px 16px; margin-top: 10px; margin-bottom: 20px;">
                    <div style="font-weight: 800; color: #6366F1; font-size: 12px; text-transform: uppercase;">📜 शास्त्रीय प्रमाण एवं श्लोक (Classical Vedic Citation)</div>
                    <div style="font-size: 14px; font-weight: 700; color: {text_primary}; margin: 6px 0; font-family: serif;">
                        {shloka_val}
                    </div>
                    <div style="font-size: 12px; color: {text_secondary};">
                        — विश्वकर्मा प्रकाश / मयमतम् वास्तु शास्त्र प्रमाण
                    </div>
                </div>
                """)

    # ─── Bottom Information & Shastriya Pramana (Collapsible Expanders) ───
    with st.expander("🔮 लग्न, महादशा व समग्र वास्तु सूचकांक सारांश (Lagna, Dasha & Vastu Summary)", expanded=False):
        c_vn1, c_vn2, c_vn3, c_vn4 = st.columns(4)
        c_vn1.metric("लग्न एवं चन्द्र", f"{lagna_sname}", f"🌙 {moon_str}")
        c_vn2.metric("सक्रिय महादशा स्वामी", f"{active_dasha_lord or '—'}", f"🪐 {dasha_str}")
        c_vn3.metric("महादशा सक्रिय दिशा", f"{active_zone.get('hindi', '—') if active_zone else '—'}", f"तत्व: {active_zone.get('element', '') if active_zone else '—'}")
        c_vn4.metric("समग्र वास्तु सूचकांक", f"{avg_score} / 100", "९ दिशाओं का सामूहिक बल")

    vishwakarma_vastu_shloka = {
        "title": "विश्वकर्मा प्रकाश — वास्तु पुरुष एवं अष्टदिशा संस्थान विचार",
        "source": "महर्षि विश्वकर्मा विरचित 'विश्वकर्मा प्रकाश' (अध्याय १, श्लोक २-३)",
        "shloka": "ईशाने देवता गेहं पूर्वस्यां स्नानमन्दिरम् ।\nआग्नेय्यां पचनागारं याम्ये शयनमन्दिरम् ॥\nनैऋत्यां शस्त्रसदनं वारुणे भोजनालयम् ।\nवायव्यां धान्यगेहं स्यात् कोशगेहं तथोत्तरे ॥",
        "meaning": "ईशान (NE) में देवालय/पूजागृह, पूर्व (East) में स्नानागार, आग्नेय (SE) में पाकशाला (रसोई), दक्षिण (South) में शयनकक्ष, नैऋत्य (SW) में भारी उपकरण/शस्त्रगार, पश्चिम (West) में भोजनालय/डाइनिंग, वायव्य (NW) में अन्नभंडार/अतिथिगृह तथा उत्तर (North) में कुबेर का धनकोष (तिजोरी) स्थापित करना सर्वकल्याणकारी एवं वास्तु सम्मत होता है।"
    }
    with st.expander(f"📜 शास्त्रीय प्रमाण — {vishwakarma_vastu_shloka['title']}", expanded=False):
        st.markdown(f"""
        <div style="background:#FFFBEB; border-left:4px solid #D97706; padding:12px; border-radius:6px; margin-bottom:10px;">
            <b style="color:#B45309; font-size:15px;">📖 ग्रंथ संदर्भ: {vishwakarma_vastu_shloka['source']}</b>
            <pre style="white-space:pre-wrap; font-family:serif; font-size:14px; color:#78350F; margin:8px 0; background:transparent; border:none; padding:0;">
{vishwakarma_vastu_shloka['shloka']}
            </pre>
            <div style="font-size:13px; color:#92400E; margin-top:6px;">
                <b>हिंदी भावार्थ:</b> {vishwakarma_vastu_shloka['meaning']}
            </div>
        </div>
        """, unsafe_allow_html=True)



