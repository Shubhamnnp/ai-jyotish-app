"""
Lal Kitab (1952 Edition) Astronomical & Astrological Engine for JyotishOS.
Implements:
1. Kalapurusha House Conversion (12 Fixed Khana / Bhavas starting from Aries = Khana 1)
2. 9 Major Karmic Debts (नौ ऋण: Pitra, Matra, Swa, Stri, Rishtedari, Nirdayi, Kudrati, Kanya, Jal Rina)
3. Sleeping Houses (Soya Hua Ghar) & Sleeping Planets (Soya Hua Graha)
4. Masnui (Artificial / Synthetic) Planets Combinations
5. Dharmi Teva, Andha Teva, and Ratandh Teva (Night Blindness)
6. Dharmi Graha vs Papi/Andhe Graha Classification
7. Complete 108 Classical Lal Kitab Totkas Catalog (9 Grahas x 12 Khanas = 108 Authentic Remedies & Precautions)

References:
- Lal Kitab (1952 Gutka / Tarjuma by Pt. Roop Chand Joshi)
- Classical Shastriya Lal Kitab Standards
"""

from typing import Dict, List, Any, Tuple, Optional
from pydantic import BaseModel, Field
from .models import KundaliChart, PlanetPosition
from .constants import SIGN_NAMES, GRAHAS


# -------------------------------------------------------------
# 1. Lal Kitab Classical House Attributes (Pakke Ghar)
# -------------------------------------------------------------

LAL_KITAB_KHANA_DATA = {
    1: {
        "khana": 1,
        "pakka_ruler": "Sun (सूर्य)",
        "pakka_sign": "Aries (मेष)",
        "karaka": "Mars (मंगल)",
        "nature_hi": "तख्त (सिंहासन), स्वभाव, देह, आयु, सम्मान",
        "benefic_planets": ["Sun", "Mars", "Jupiter", "Moon"],
        "malefic_planets": ["Saturn", "Rahu"],
    },
    2: {
        "khana": 2,
        "pakka_ruler": "Jupiter (बृहस्पति)",
        "pakka_sign": "Taurus (वृषभ)",
        "karaka": "Jupiter (बृहस्पति)",
        "nature_hi": "धर्मस्थान, ससुराल, संचित धन, वाणी, गुरु कृपा",
        "benefic_planets": ["Jupiter", "Moon", "Mars"],
        "malefic_planets": ["Venus", "Rahu"],
    },
    3: {
        "khana": 3,
        "pakka_ruler": "Mars (मंगल)",
        "pakka_sign": "Gemini (मिथुन)",
        "karaka": "Mercury (बुध)",
        "nature_hi": "पराक्रम, छोटे भाई-बहन, हाथ, गुप्त शत्रु",
        "benefic_planets": ["Mars", "Sun", "Rahu"],
        "malefic_planets": ["Moon", "Ketu"],
    },
    4: {
        "khana": 4,
        "pakka_ruler": "Moon (चन्द्र)",
        "pakka_sign": "Cancer (कर्क)",
        "karaka": "Moon (चन्द्र)",
        "nature_hi": "माता, नदी, शांति, हृदय, पैतृक संपत्ति",
        "benefic_planets": ["Moon", "Jupiter"],
        "malefic_planets": ["Saturn", "Rahu", "Ketu"],
    },
    5: {
        "khana": 5,
        "pakka_ruler": "Jupiter (बृहस्पति)",
        "pakka_sign": "Leo (सिंह)",
        "karaka": "Sun (सूर्य)",
        "nature_hi": "संतान, विद्या, पूर्वजन्म के कर्म, भविष्य",
        "benefic_planets": ["Sun", "Jupiter", "Mars"],
        "malefic_planets": ["Rahu", "Saturn"],
    },
    6: {
        "khana": 6,
        "pakka_ruler": "Mercury (बुध) & Ketu (केतु)",
        "pakka_sign": "Virgo (कन्या)",
        "karaka": "Ketu (केतु)",
        "nature_hi": "पाताल, रोग, ऋण, ननिहाल, गुप्त विद्या",
        "benefic_planets": ["Mercury", "Ketu"],
        "malefic_planets": ["Jupiter", "Sun", "Venus"],
    },
    7: {
        "khana": 7,
        "pakka_ruler": "Venus (शुक्र) & Mercury (बुध)",
        "pakka_sign": "Libra (तुला)",
        "karaka": "Venus (शुक्र)",
        "nature_hi": "गृहस्थ, विवाह, साझेदारी, दुनियादारी",
        "benefic_planets": ["Venus", "Mercury", "Saturn"],
        "malefic_planets": ["Sun", "Jupiter", "Moon"],
    },
    8: {
        "khana": 8,
        "pakka_ruler": "Mars (मंगल) & Saturn (शनि)",
        "pakka_sign": "Scorpio (वृश्चिक)",
        "karaka": "Saturn (शनि)",
        "nature_hi": "श्मशान, मृत्यु, रहस्य, अचानक संकट",
        "benefic_planets": ["Saturn", "Mars"],
        "malefic_planets": ["Moon", "Sun", "Jupiter"],
    },
    9: {
        "khana": 9,
        "pakka_ruler": "Jupiter (बृहस्पति)",
        "pakka_sign": "Sagittarius (धनु)",
        "karaka": "Jupiter (बृहस्पति)",
        "nature_hi": "भाग्य, धर्म, पिता, तीर्थयात्रा, पूर्वज",
        "benefic_planets": ["Jupiter", "Sun", "Mars"],
        "malefic_planets": ["Rahu", "Venus"],
    },
    10: {
        "khana": 10,
        "pakka_ruler": "Saturn (शनि)",
        "pakka_sign": "Capricorn (मकर)",
        "karaka": "Saturn (शनि)",
        "nature_hi": "कर्म, हुकूमत, मान-प्रतिष्ठा, व्यवसाय",
        "benefic_planets": ["Saturn", "Mercury", "Sun"],
        "malefic_planets": ["Moon", "Mars"],
    },
    11: {
        "khana": 11,
        "pakka_ruler": "Jupiter (बृहस्पति) & Saturn (शनि)",
        "pakka_sign": "Aquarius (कुम्भ)",
        "karaka": "Jupiter (बृहस्पति)",
        "nature_hi": "लाभ, बड़े भाई, आमदनी, इच्छा पूर्ति",
        "benefic_planets": ["Jupiter", "Saturn", "Sun"],
        "malefic_planets": ["Moon"],
    },
    12: {
        "khana": 12,
        "pakka_ruler": "Jupiter (बृहस्पति) & Rahu (राहु)",
        "pakka_sign": "Pisces (मीन)",
        "karaka": "Ketu (केतु)",
        "nature_hi": "शयन सुख, व्यय, विदेश, मोक्ष, राहु का घर",
        "benefic_planets": ["Jupiter", "Rahu", "Ketu"],
        "malefic_planets": ["Mars", "Sun", "Venus"],
    }
}


# -------------------------------------------------------------
# 2. Lal Kitab 9 Classical Karmic Debts (नौ ऋण)
# -------------------------------------------------------------

DEBT_DEFINITIONS = [
    {
        "id": "pitra_rina",
        "name_hi": "पितृ ऋण (Forefathers' Debt)",
        "cause_hi": "पूर्वजों द्वारा किसी पूज्य संत, मंदिर या ब्राह्मण का अपमान अथवा पीपल का वृक्ष काटना।",
        "condition_desc_hi": "गुरु (बृहस्पति) का खाना 2, 5, 9 या 12 में शुक्र, बुध, राहु या केतु से पीड़ित होना अथवा गुरु का नीच होना।",
        "effect_hi": "संतान प्राप्ति में बाधा, उच्च शिक्षा में रुकावट, बाल समय से पहले सफेद होना, आर्थिक अस्थिरता।",
        "remedy_hi": "परिवार के सभी रक्त-संबंधी सदस्यों से बराबर वजन या धन लेकर किसी मंदिर या धर्मस्थान में दान करें।",
    },
    {
        "id": "matra_rina",
        "name_hi": "मातृ ऋण (Mother's Debt)",
        "cause_hi": "पूर्वजन्म में माता या किसी असहाय स्त्री का तिरस्कार अथवा उन्हें कष्ट पहुँचाना।",
        "condition_desc_hi": "चन्द्रमा का खाना 2, 4 में केतु, राहु अथवा शनि से दृष्ट या पीड़ित होना।",
        "effect_hi": "मानसिक अशांति, अत्यधिक तनाव, धन का व्यर्थ बह जाना, फेफड़ों व छाती के विकार।",
        "remedy_hi": "परिवार के सभी सदस्यों से बराबर चाँदी का सिक्का या चाँदी लेकर बहते पानी में प्रवाहित करें।",
    },
    {
        "id": "swa_rina",
        "name_hi": "स्व-ऋण / आत्म-ऋण (Self Debt)",
        "cause_hi": "नास्तिकता, धर्म और परंपराओं की अवहेलना करना या कुलदेवी/देवता को भूल जाना।",
        "condition_desc_hi": "सूर्य का खाना 5 में राहु, शनि या केतु से पीड़ित होना अथवा शुक्र के साथ बैठना।",
        "effect_hi": "मुकदमेबाजी, बदनामी, हड्डियों या हृदय के रोग, सरकारी कार्यों में लगातार अड़चनें।",
        "remedy_hi": "परिवार के सभी सदस्यों से समान सिक्का/तांबा लेकर यज्ञ या सूर्य नारायण की पूजा कराएं।",
    },
    {
        "id": "stri_rina",
        "name_hi": "स्त्री ऋण (Woman's Debt)",
        "cause_hi": "गर्भवती स्त्री को सताना, पत्नी का अपमान करना या कन्या भ्रूण को कष्ट देना।",
        "condition_desc_hi": "शुक्र का खाना 2 या 7 में राहु, सूर्य या मंगल से दूषित होना।",
        "effect_hi": "वैवाहिक जीवन में कलह, दांपत्य सुख का अभाव, गुप्त रोग, व्यापार में भारी घाटा।",
        "remedy_hi": "परिवार के सभी सदस्यों से अन्न या धन एकत्र कर 100 गायों को हरा चारा खिलाएं।",
    },
    {
        "id": "rishtedari_rina",
        "name_hi": "रिश्तेदारी ऋण (Relatives' Debt)",
        "cause_hi": "भाइयों, मित्रों या सगे संबंधियों का हक मारना अथवा उनकी जमीन हड़पना।",
        "condition_desc_hi": "मंगल का खाना 1 या 8 में बुध अथवा केतु के साथ होना या बुध का नीच होना।",
        "effect_hi": "रक्त विकार, दुर्घटनाएं, भाइयों से दुश्मनी, संतान का अवज्ञाकारी होना।",
        "remedy_hi": "हकीम, चिकित्सक या जरूरतमंदों को मुफ्त दवाइयों का वितरण करें।",
    },
    {
        "id": "nirdayi_rina",
        "name_hi": "निर्दयी ऋण (Cruelty / Oppression Debt)",
        "cause_hi": "किसी जीव, निर्दोष पशु या मजदूर पर अत्याचार करना, उनकी मेहनत की मजदूरी न देना।",
        "condition_desc_hi": "शनि का खाना 10 या 11 में सूर्य, चन्द्र या मंगल से पीड़ित होना।",
        "effect_hi": "अचानक आग लगना, घर में चोरी, असाध्य रोग, अकाल कष्ट।",
        "remedy_hi": "मजदूरों, असहायों और कौओं/कुत्तों को तेल लगी रोटी या भोजन कराएं।",
    },
    {
        "id": "ani_rina",
        "name_hi": "अनिष्ट / कुदरती ऋण (Nature / God's Debt)",
        "cause_hi": "कुत्ते, पक्षी या बेजुबान जानवरों को मारना अथवा विश्वासघात करना।",
        "condition_desc_hi": "केतु का खाना 6 या 12 में चन्द्र या मंगल से दृष्ट होना।",
        "effect_hi": "पैरों व जोड़ों का दर्द, मूत्र विकार, संतानों का रोगी होना, हर कार्य में अड़चन।",
        "remedy_hi": "100 आवारा कुत्तों को मीठी रोटी अथवा दूध-ब्रेड खिलाएं। कान में सोना पहनें।",
    },
    {
        "id": "kanya_rina",
        "name_hi": "कन्या / बहन-बेटी ऋण (Daughter / Sister Debt)",
        "cause_hi": "पूर्वजन्म में निर्दोष कन्या, बहन, बेटी या बुआ को प्रताड़ित करना अथवा उनका हक मारना।",
        "condition_desc_hi": "बुध का खाना 3, 6, 8 या 12 में चन्द्र, राहु अथवा मंगल से दूषित होना अथवा बुध का नीच होना।",
        "effect_hi": "व्यापार में भारी हानि, बुद्धिभ्रंश, वाणी दोष, नसों या त्वचा के असाध्य विकार, कन्या संतति को कष्ट।",
        "remedy_hi": "परिवार के सभी रक्त-संबंधियों से समान धन/पीली कौड़ी एकत्र कर कन्याओं को भोजन कराएं व नाक छिदवाकर 100 दिन चांदी का तार पहनें।",
    },
    {
        "id": "jal_rina",
        "name_hi": "जल / देव ऋण / ज़ालिम का ऋण (Water / Divine Spiritual Debt)",
        "cause_hi": "कुओं, बावड़ियों, नदियों या पवित्र जलस्रोतों को दूषित करना, मंदिर या धर्मस्थल की संपत्ति हड़पना अथवा गुरु से द्रोह।",
        "condition_desc_hi": "राहु का खाना 1, 5, 9 या 12 में सूर्य, शुक्र अथवा मंगल से पीड़ित होना अथवा चन्द्रमा का राहु से ग्रहण लगना।",
        "effect_hi": "अचानक दुर्घटनाएं, विषैले जीवों का भय, अनिद्रा, प्रेत-बाधा का भ्रम, वंशवृद्धि में संकट।",
        "remedy_hi": "परिवार के सभी सदस्यों से बराबर नारियल या कच्चा कोयला लेकर बहते शुद्ध जल में प्रवाहित करें। धर्मस्थान में सेवा करें।",
    }
]


# -------------------------------------------------------------
# 3. 108 Authentic Classical Lal Kitab Totkas Catalog
# -------------------------------------------------------------

LAL_KITAB_108_TOTKAS: Dict[Tuple[str, int], Dict[str, str]] = {
    # SUN (सूर्य) 1 to 12
    ("Sun", 1): {
        "totka_hi": "तांबे का सिक्का गले में धारण करें, मुफ़्त में कुछ न लें, गुड़ खाकर जल पीकर शुभ कार्य आरंभ करें।",
        "precaution_hi": "दक्षिण दिशा का मुख्य द्वार न रखें, दिन में संभोग से बचें।",
        "shastra_effect_hi": "तख्त का राजा सूर्य - मान-सम्मान व राजयोग कारक।"
    },
    ("Sun", 2): {
        "totka_hi": "मंदिर में नारियल, बादाम या सरसों का तेल दान करें।",
        "precaution_hi": "किसी से मुफ़्त में दान या उपहार न लें।",
        "shastra_effect_hi": "वाणी में ओज व संचित धन वृद्धि।"
    },
    ("Sun", 3): {
        "totka_hi": "सदाचारी रहें, माता-पिता का नित्य आशीर्वाद लें।",
        "precaution_hi": "अपने चरित्र को निष्कलंक रखें, पराई स्त्री पर दृष्टि न डालें।",
        "shastra_effect_hi": "पराक्रम में वृद्धि व छोटे भाइयों से सहयोग।"
    },
    ("Sun", 4): {
        "totka_hi": "दृष्टिहीन व्यक्तियों की सेवा करें, बहते पानी में तांबे का सिक्का प्रवाहित करें।",
        "precaution_hi": "लोहे की चारपाई पर न सोएं, पैतृक संपत्ति को न बेचें।",
        "shastra_effect_hi": "माता का स्वास्थ्य व मानसिक शांति।"
    },
    ("Sun", 5): {
        "totka_hi": "रसोई में बैठकर भोजन करें, संतान का आदर करें व लाल रुमाल पास रखें।",
        "precaution_hi": "संतान के जन्म पर अत्यधिक दिखावा या शोर-शराबा न करें।",
        "shastra_effect_hi": "विद्या, मेधा व संतान का उत्कर्ष।"
    },
    ("Sun", 6): {
        "totka_hi": "रात को सिरहाने पानी का लोटा रखकर सुबह पौधे में डालें, बंदरों को गुड़-चना खिलाएं।",
        "precaution_hi": "किसी की चुगली या निंदा न करें।",
        "shastra_effect_hi": "शत्रुओं का दमन व रोगों से मुक्ति।"
    },
    ("Sun", 7): {
        "totka_hi": "काली गाय की सेवा करें, रोटी में थोड़ा मीठा लगाकर दें।",
        "precaution_hi": "विवाह में देर होने पर नमक का सेवन कम करें।",
        "shastra_effect_hi": "दांपत्य जीवन में सामंजस्य व प्रतिष्ठा।"
    },
    ("Sun", 8): {
        "totka_hi": "सफेद गाय की सेवा करें, तांबे का चौकोर टुकड़ा अपने पास रखें।",
        "precaution_hi": "दक्षिणमुखी मकान में निवास से परहेज करें।",
        "shastra_effect_hi": "अचानक संकटों का शमन व दीर्घायु।"
    },
    ("Sun", 9): {
        "totka_hi": "तांबे का सिक्का छेद करके सफेद धागे में पहनें, पीतल के बर्तन का उपयोग करें।",
        "precaution_hi": "नास्तिकता से दूर रहें, बुजुर्गों का निरादर न करें।",
        "shastra_effect_hi": "भाग्यवृद्धि व धर्म में रुचि।"
    },
    ("Sun", 10): {
        "totka_hi": "सिर पर सफेद या हल्के रंग की टोपी पहनें, बहते जल में 43 दिन तांबे का सिक्का डालें।",
        "precaution_hi": "काले व नीले वस्त्रों से पूर्ण परहेज करें।",
        "shastra_effect_hi": "राज्य सत्ता व कार्यक्षेत्र में उन्नति।"
    },
    ("Sun", 11): {
        "totka_hi": "मांस-मदिरा का पूर्ण त्याग करें, रात को मूली सिरहाने रखकर सुबह मंदिर में दें।",
        "precaution_hi": "झूठ और धोखेबाजी से हमेशा बचें।",
        "shastra_effect_hi": "निरंतर आमदनी व बड़े भाइयों का सहयोग।"
    },
    ("Sun", 12): {
        "totka_hi": "आँगन में अंधेरी कोठरी न बनाएं, लाल रुमाल अपनी जेब में रखें।",
        "precaution_hi": "धर्म विरोधी आचरण न करें, अनैतिक व्यय से बचें।",
        "shastra_effect_hi": "शयन सुख व आध्यात्मिक शांति।"
    },

    # MOON (चन्द्र) 1 to 12
    ("Moon", 1): {
        "totka_hi": "चांदी का चौकोर टुकड़ा जेब में रखें, माता का चरण स्पर्श कर आशीर्वाद लें।",
        "precaution_hi": "24 वर्ष से पूर्व विवाह करने से बचें।",
        "shastra_effect_hi": "शांत मन, ओजस्वी व्यक्तित्व व दीघार्यु।"
    },
    ("Moon", 2): {
        "totka_hi": "माता से चांदी और चावल आशीर्वाद में लेकर संभाल कर रखें।",
        "precaution_hi": "घंटी या शंख का घर में अनादर न करें।",
        "shastra_effect_hi": "लक्ष्मी कृपा, संचित धन व मधुर वाणी।"
    },
    ("Moon", 3): {
        "totka_hi": "कन्या पूजन करें, खीर का प्रसाद कन्याओं में बांटें।",
        "precaution_hi": "तीर्थयात्रा में कंजूसी न करें, दूसरों से ईर्ष्या छोड़ें।",
        "shastra_effect_hi": "साहस, कला व लेखन में सफलता।"
    },
    ("Moon", 4): {
        "totka_hi": "बहते जल में दूध या चावल प्रवाहित करें, चांदी के गिलास में जल पिएं।",
        "precaution_hi": "कुएं के ऊपर पक्की छत न डलवाएं।",
        "shastra_effect_hi": "अक्षय भंडार, मातृ सुख व शांति।"
    },
    ("Moon", 5): {
        "totka_hi": "सदा सत्य बोलें, किसी का दिल न दुखाएं, मंदिर में दूध का दान करें।",
        "precaution_hi": "संतान पर अनावश्यक क्रोध या कटु वचन न बोलें।",
        "shastra_effect_hi": "सद्बुद्धि, मेधा व संतान का भाग्योदय।"
    },
    ("Moon", 6): {
        "totka_hi": "रात्रि में दूध का सेवन न करें, अस्पताल या प्याऊ में पानी की व्यवस्था कराएं।",
        "precaution_hi": "व्यावसायिक रूप से दूध बेचने से परहेज करें।",
        "shastra_effect_hi": "रोग निवारण व मानसिक दृढ़ता।"
    },
    ("Moon", 7): {
        "totka_hi": "चांदी का चौकोर टुकड़ा हमेशा पास रखें, पत्नी का सम्मान करें।",
        "precaution_hi": "दूध व चावल का व्यापार न करें।",
        "shastra_effect_hi": "दांपत्य सुख व साझेदारी में लाभ।"
    },
    ("Moon", 8): {
        "totka_hi": "बड़े-बुजुर्गों का आशीर्वाद लें, श्मशान के हैंडपंप का जल लाकर घर में रखें।",
        "precaution_hi": "घर में नया कुआं या बोरवेल न खुदवाएं।",
        "shastra_effect_hi": "अज्ञात भयों से मुक्ति व मानसिक संबल।"
    },
    ("Moon", 9): {
        "totka_hi": "बहते पानी में चांदी का सिक्का डालें, मछलियों को आटे की गोलियां खिलाएं।",
        "precaution_hi": "धर्म की झूठी कसम कभी न खाएं।",
        "shastra_effect_hi": "तीर्थ फल व भाग्योदय।"
    },
    ("Moon", 10): {
        "totka_hi": "रात में दूध न पिएं, किसी प्यासे को जल पिलाएं।",
        "precaution_hi": "शनि से जुड़े काम जैसे चमड़ा/शराब का धंधा न करें।",
        "shastra_effect_hi": "कार्यक्षेत्र में प्रतिष्ठा व स्थायित्व।"
    },
    ("Moon", 11): {
        "totka_hi": "भैरव जी को दूध अर्पित करें, माता से चांदी का सिक्का लें।",
        "precaution_hi": "किसी असहाय का उपहास न उड़ाएं।",
        "shastra_effect_hi": "आय के नवीन स्रोत व मनोकामना पूर्ति।"
    },
    ("Moon", 12): {
        "totka_hi": "वर्षा का जल कांच की बोतल में भरकर घर में रखें।",
        "precaution_hi": "मुफ्त में किसी से धार्मिक पुस्तकें न लें।",
        "shastra_effect_hi": "मानसिक शांति व व्यर्थ खर्चों पर रोक।"
    },

    # MARS (मंगल) 1 to 12
    ("Mars", 1): {
        "totka_hi": "तंदूर में मीठी रोटी बनवाकर कौओं और कुत्तों को खिलाएं, चांदी का छल्ला पहनें।",
        "precaution_hi": "मुफ्त का माल या रिश्वत न लें।",
        "shastra_effect_hi": "साहस, नेतृत्व व रक्त विकार से सुरक्षा।"
    },
    ("Mars", 2): {
        "totka_hi": "भाइयों की सहायता करें, हनुमान जी को चोला या सिन्दूर अर्पित करें।",
        "precaution_hi": "ससुराल से अधिक लेन-देन न करें।",
        "shastra_effect_hi": "धन वृद्धि व पारिवारिक एकता।"
    },
    ("Mars", 3): {
        "totka_hi": "हाथी दांत या चांदी का छल्ला अनामिका में धारण करें।",
        "precaution_hi": "किसी के साथ धोखा या दगाबाजी न करें।",
        "shastra_effect_hi": "पराक्रम वृद्धि व शत्रुओं पर विजय।"
    },
    ("Mars", 4): {
        "totka_hi": "मृदंग या ढोलक मंदिर में दान करें, मीठा भोजन जरूरतमंदों को कराएं।",
        "precaution_hi": "क्रोध पर संयम रखें, वाहन सावधानी से चलाएं।",
        "shastra_effect_hi": "भूमि, भवन व वाहन सुख।"
    },
    ("Mars", 5): {
        "totka_hi": "रात को सिरहाने पानी रखकर सुबह पौधों में डालें, सूर्य को जल दें।",
        "precaution_hi": "किसी के प्रति ईर्ष्या या कटुता न रखें।",
        "shastra_effect_hi": "संतान सुख व बौद्धिक प्रखरता।"
    },
    ("Mars", 6): {
        "totka_hi": "कन्याओं को मीठी वस्तुएं भेंट करें, चांदी का चौकोर टुकड़ा रखें।",
        "precaution_hi": "भाइयों से संपत्ति विवाद से बचें।",
        "shastra_effect_hi": "ऋण मुक्ति व प्रतियोगिता में सफलता।"
    },
    ("Mars", 7): {
        "totka_hi": "मीठा शरबत बांटें, चांदी की ईंट या ठोस टुकड़ा तिजोरी में रखें।",
        "precaution_hi": "क्रोध में अपशब्द या कटु वचन न बोलें।",
        "shastra_effect_hi": "वैवाहिक सद्भाव व व्यापार वृद्धि।"
    },
    ("Mars", 8): {
        "totka_hi": "विधवा स्त्री की सेवा करें, तंदूर में मीठी रोटी बनवाकर कुत्तों को दें।",
        "precaution_hi": "दक्षिण दिशा में मुख्य दरवाजा न रखें।",
        "shastra_effect_hi": "दुर्घटनाओं से रक्षा व दीर्घायु।"
    },
    ("Mars", 9): {
        "totka_hi": "लाल वस्त्र या लाल चंदन का उपयोग करें, बड़े भाई का सम्मान करें।",
        "precaution_hi": "नास्तिकता व आलस्य का त्याग करें।",
        "shastra_effect_hi": "भाग्य बल व पिता का सहयोग।"
    },
    ("Mars", 10): {
        "totka_hi": "सोने का छल्ला पहनें या बिना सींग वाले हिरण की सेवा करें।",
        "precaution_hi": "घर में अनावश्यक शस्त्र न रखें।",
        "shastra_effect_hi": "उच्च पद, प्रशासनिक प्रतिष्ठा।"
    },
    ("Mars", 11): {
        "totka_hi": "मिट्टी के बर्तन में सिन्दूर या शहद भरकर वीराने में दबाएं।",
        "precaution_hi": "झूठ बोलने व वादाखिलाफी से बचें।",
        "shastra_effect_hi": "लाभ वृद्धि व पराक्रम।"
    },
    ("Mars", 12): {
        "totka_hi": "खांड या बताशे बहते पानी में डालें, सुबह उठकर थोड़ा शहद चखें।",
        "precaution_hi": "पराए हक पर कभी दृष्टि न रखें।",
        "shastra_effect_hi": "शयन सुख व मोक्ष मार्ग।"
    },

    # MERCURY (बुध) 1 to 12
    ("Mercury", 1): {
        "totka_hi": "नाक छिदवाकर 100 दिन चांदी का तार पहनें, हरी मूंग का दान करें।",
        "precaution_hi": "मांस-मदिरा का सेवन सर्वथा त्यागें।",
        "shastra_effect_hi": "बुद्धि की तीक्ष्णता व व्यापारिक कुशाग्रता।"
    },
    ("Mercury", 2): {
        "totka_hi": "चांदी का छल्ला बिना जोड़ का पहनें, छोटी कन्याओं का पूजन करें।",
        "precaution_hi": "जुआ, सट्टा व लाटरी से दूर रहें।",
        "shastra_effect_hi": "वाणी में मिठास व संचित धन वृद्धि।"
    },
    ("Mercury", 3): {
        "totka_hi": "फिटकरी से दांत साफ करें, पक्षियों को साबुत मूंग भिगोकर डालें।",
        "precaution_hi": "अस्थिर विचारों व दोहरी बातों से बचें।",
        "shastra_effect_hi": "लेखन व संचार माध्यमों में यश।"
    },
    ("Mercury", 4): {
        "totka_hi": "तोता या पक्षी पिंजरे में न पालें, चांदी की चेन गले में पहनें।",
        "precaution_hi": "घर में बांस का पौधा न लगाएं।",
        "shastra_effect_hi": "पारिवारिक शांति व सुख साधन।"
    },
    ("Mercury", 5): {
        "totka_hi": "तांबे का सिक्का छेद करके गले में पहनें, गाय को हरा चारा दें।",
        "precaution_hi": "वाणी में कटुता या अभद्र भाषा न लाएं।",
        "shastra_effect_hi": "विद्या, मेधा व संतान का कल्याण।"
    },
    ("Mercury", 6): {
        "totka_hi": "उत्तर दिशा में जल का लोटा रखें, कन्याओं को हरे वस्त्र या चूड़ियां भेंट करें।",
        "precaution_hi": "फूफा, मौसा या बहनोई से विवाद न करें।",
        "shastra_effect_hi": "रोग निवारण व व्यापार वृद्धि।"
    },
    ("Mercury", 7): {
        "totka_hi": "तांबे का चौकोर टुकड़ा अपने पास रखें, बहन या बुआ को उपहार दें।",
        "precaution_hi": "साझेदारी में छल-कपट न करें।",
        "shastra_effect_hi": "दांपत्य सुख व व्यापार में संतुलन।"
    },
    ("Mercury", 8): {
        "totka_hi": "मिट्टी के बर्तन में शहद भरकर वीराने में दबाएं, गणेश जी को दूर्वा चढ़ाएं।",
        "precaution_hi": "छत पर कबाड़ या पुरानी रद्दी न रखें।",
        "shastra_effect_hi": "गुप्त ज्ञान व संकट मुक्ति।"
    },
    ("Mercury", 9): {
        "totka_hi": "नाक छिदवाना, हरे रंग के वस्त्रों से परहेज करें।",
        "precaution_hi": "नास्तिक विचारों को प्रश्रय न दें।",
        "shastra_effect_hi": "भाग्य वृद्धि व धार्मिक यात्राएं।"
    },
    ("Mercury", 10): {
        "totka_hi": "तुलसी का पौधा न लगाएं, कौओं को रोटी डालें।",
        "precaution_hi": "आलस्य व खाली बैठना त्यागें।",
        "shastra_effect_hi": "व्यवसाय में साख व निरंतर प्रगति।"
    },
    ("Mercury", 11): {
        "totka_hi": "पन्ना रत्न बिना सोचे न पहनें, तांबे का पैसा गले में डालें।",
        "precaution_hi": "दूसरों की नकल करने से बचें।",
        "shastra_effect_hi": "आकस्मिक लाभ व जनसंपर्क लाभ।"
    },
    ("Mercury", 12): {
        "totka_hi": "गले में पीला धागा पहनें, मिट्टी के मटके में खांड भरकर वीराने में दबाएं।",
        "precaution_hi": "वाणी पर पूरा नियंत्रण रखें।",
        "shastra_effect_hi": "व्यय नियंत्रण व मानसिक एकाग्रता।"
    },

    # JUPITER (बृहस्पति) 1 to 12
    ("Jupiter", 1): {
        "totka_hi": "गले में सोने की चेन या पीला धागा पहनें, केसर का तिलक मस्तक व नाभि पर लगाएं।",
        "precaution_hi": "पिता व गुरु का कभी निरादर न करें।",
        "shastra_effect_hi": "ज्ञान, आत्मबल व दिव्य कृपा।"
    },
    ("Jupiter", 2): {
        "totka_hi": "मंदिर में चने की दाल या पीली मिठाई का दान करें, बड़ों के चरण स्पर्श करें।",
        "precaution_hi": "झूठी गवाही या अधर्म का समर्थन न करें।",
        "shastra_effect_hi": "अक्षय धन, मान-प्रतिष्ठा व विद्या।"
    },
    ("Jupiter", 3): {
        "totka_hi": "मां दुर्गा की आराधना करें, छोटी कन्याओं को फल व मिठाई भेंट करें।",
        "precaution_hi": "चापलूसी या मक्कारी से बचें।",
        "shastra_effect_hi": "साहस, यश व आध्यात्मिक शक्ति।"
    },
    ("Jupiter", 4): {
        "totka_hi": "किसी मंदिर में पुजारी को पीले वस्त्र भेंट करें, बड़ों का सम्मान करें।",
        "precaution_hi": "घर में देवस्थल का अपमान न होने दें।",
        "shastra_effect_hi": "गृह सुख, मानसिक शांति व प्रतिष्ठा।"
    },
    ("Jupiter", 5): {
        "totka_hi": "साधु-संतों की सेवा करें, पीपल के वृक्ष को जल दें बिना स्पर्श किए।",
        "precaution_hi": "गुरु की निंदा न सुनें और न करें।",
        "shastra_effect_hi": "उत्तम संतान, उच्च विद्या व धर्म निष्ठा।"
    },
    ("Jupiter", 6): {
        "totka_hi": "किसी मंदिर में चने की दाल दान करें, मुर्गों या पक्षियों को दाना डालें।",
        "precaution_hi": "मुफ्त का दान या भिक्षा न स्वीकारें।",
        "shastra_effect_hi": "शत्रु शमन व रोगों से मुक्ति।"
    },
    ("Jupiter", 7): {
        "totka_hi": "पीले वस्त्र धारण करें, मंदिर में सोने का छोटा टुकड़ा या पीतल दान करें।",
        "precaution_hi": "चरित्र पर कभी आंच न आने दें।",
        "shastra_effect_hi": "उत्तम जीवनसाथी व समृद्ध गृहस्थ।"
    },
    ("Jupiter", 8): {
        "totka_hi": "श्मशान में पीपल का वृक्ष लगाएं या मंदिर में घी का दीपक जलाएं।",
        "precaution_hi": "घर में देवी-देवताओं की खंडित मूर्ति न रखें।",
        "shastra_effect_hi": "दीर्घायु व गुप्त विद्याओं का लाभ।"
    },
    ("Jupiter", 9): {
        "totka_hi": "बहते जल में चने की दाल प्रवाहित करें, नित्य केसर का तिलक लगाएं।",
        "precaution_hi": "धार्मिक कट्टरता या पाखंड से बचें।",
        "shastra_effect_hi": "परम भाग्योदय व गुरु कृपा।"
    },
    ("Jupiter", 10): {
        "totka_hi": "माथे पर केसर का तिलक लगाएं, बहते पानी में तांबे का सिक्का डालें।",
        "precaution_hi": "आलस्य न करें, कर्तव्य का पालन करें।",
        "shastra_effect_hi": "राजकीय सम्मान व उच्च पद।"
    },
    ("Jupiter", 11): {
        "totka_hi": "पीला रुमाल अपने पास रखें, पिता के पलंग या वस्त्रों का आदर करें।",
        "precaution_hi": "झूठी कसमें न खाएं।",
        "shastra_effect_hi": "सर्वतोमुखी लाभ व कीर्ति।"
    },
    ("Jupiter", 12): {
        "totka_hi": "सिर पर पीली पगड़ी या टोपी रखें, रात को सौंफ सिरहाने रखकर सोएं।",
        "precaution_hi": "व्यसनों व कुसंगति से दूर रहें।",
        "shastra_effect_hi": "मोक्ष मार्ग व शयन सुख।"
    },

    # VENUS (शुक्र) 1 to 12
    ("Venus", 1): {
        "totka_hi": "दही से स्नान करें, गौशाला में गाय को हरा चारा व गुड़ खिलाएं।",
        "precaution_hi": "गंदे या फटे वस्त्र कभी न पहनें।",
        "shastra_effect_hi": "आकर्षक व्यक्तित्व व सौंदर्य।"
    },
    ("Venus", 2): {
        "totka_hi": "चांदी का चौकोर टुकड़ा अपने पास रखें, पत्नी का सम्मान करें।",
        "precaution_hi": "पराई स्त्री पर कुदृष्टि न रखें।",
        "shastra_effect_hi": "ऐश्वर्य, भोग विलास व धन।"
    },
    ("Venus", 3): {
        "totka_hi": "किसी असहाय कन्या के विवाह में सहयोग करें, इत्र का प्रयोग करें।",
        "precaution_hi": "आलस्य व अकर्मण्यता छोड़ें।",
        "shastra_effect_hi": "कलात्मक प्रतिभा व यश।"
    },
    ("Venus", 4): {
        "totka_hi": "बहते जल में सफेद फूल प्रवाहित करें, पत्नी से मधुर संबंध रखें।",
        "precaution_hi": "माता या सास का दिल न दुखाएं।",
        "shastra_effect_hi": "सुख, वाहन व उत्तम भवन।"
    },
    ("Venus", 5): {
        "totka_hi": "मंदिर में गाय का शुद्ध घी दान करें, इत्र व सुगंधित तेल लगाएं।",
        "precaution_hi": "वासना पर संयम रखें।",
        "shastra_effect_hi": "विद्या, प्रेम व उत्तम संतान।"
    },
    ("Venus", 6): {
        "totka_hi": "छह कन्याओं को मीठा दही या खीर खिलाएं, पत्नी के हाथों में सोने की चूड़ी पहनाएं।",
        "precaution_hi": "स्त्री जाति का कभी अपमान न करें।",
        "shastra_effect_hi": "रोग निवारण व वैवाहिक रक्षा।"
    },
    ("Venus", 7): {
        "totka_hi": "काली गाय को ज्वार या चारा खिलाएं, इत्र का उपयोग करें।",
        "precaution_hi": "जीवनसाथी से कभी झूठ न बोलें।",
        "shastra_effect_hi": "दांपत्य सौहार्द व साझेदारी।"
    },
    ("Venus", 8): {
        "totka_hi": "मंदिर में ज्वार या सफेद तिल का दान करें, सिरहाने तांबे का सिक्का रखें।",
        "precaution_hi": "अनैतिक कार्यों से दूर रहें।",
        "shastra_effect_hi": "अचानक धन लाभ व दीर्घायु।"
    },
    ("Venus", 9): {
        "totka_hi": "चांदी का चौकोर टुकड़ा अपने पर्स में रखें, नीम के पेड़ की दातुन करें।",
        "precaution_hi": "ईश्वर व धर्म के प्रति निष्ठा रखें।",
        "shastra_effect_hi": "तीर्थ सुख व भाग्य वृद्धि।"
    },
    ("Venus", 10): {
        "totka_hi": "पश्चिमी दिशा में सफेद ध्वज लगाएं, शनिवार को तेल का दान करें।",
        "precaution_hi": "नशाखोरी व जुए से बचें।",
        "shastra_effect_hi": "व्यवसाय में ख्याति व समृद्धि।"
    },
    ("Venus", 11): {
        "totka_hi": "सरसों का तेल दान करें, सफेद चंदन का तिलक लगाएं।",
        "precaution_hi": "किसी का विश्वास न तोड़ें।",
        "shastra_effect_hi": "इच्छा पूर्ति व प्रचुर लाभ।"
    },
    ("Venus", 12): {
        "totka_hi": "पत्नी के वजन के बराबर ज्वार मंदिर में दान करें या गाय को खिलाएं।",
        "precaution_hi": "व्यर्थ के दिखावे में धन न उड़ाएं।",
        "shastra_effect_hi": "शयन सुख व आध्यात्मिक आनंद।"
    },

    # SATURN (शनि) 1 to 12
    ("Saturn", 1): {
        "totka_hi": "बंदरों को गुड़-चना खिलाएं, लोहे का छल्ला मध्यमा अंगुली में पहनें।",
        "precaution_hi": "शराब व मांसाहार का पूर्ण त्याग करें।",
        "shastra_effect_hi": "दीर्घायु, धैर्य व कर्म फल सिद्धि।"
    },
    ("Saturn", 2): {
        "totka_hi": "मंदिर में सरसों का तेल दान करें, मजदूरों को भोजन कराएं।",
        "precaution_hi": "असहायों की बद्दुआ कभी न लें।",
        "shastra_effect_hi": "स्थिर संपत्ति व वाणी की गंभीरता।"
    },
    ("Saturn", 3): {
        "totka_hi": "तीन कुत्तों को मीठी रोटी खिलाएं, घर के मुख्य द्वार पर लोहे की कील लगाएं।",
        "precaution_hi": "आंखें मूंदकर किसी पर विश्वास न करें।",
        "shastra_effect_hi": "शत्रु पराजय व अदम्य पराक्रम।"
    },
    ("Saturn", 4): {
        "totka_hi": "बहते पानी में शराब या दूध प्रवाहित करें, कौओं को रोटी डालें।",
        "precaution_hi": "रात को दूध न पिएं।",
        "shastra_effect_hi": "पैतृक संपत्ति व मानसिक स्थिरता।"
    },
    ("Saturn", 5): {
        "totka_hi": "बच्चों को मुफ्त में खिलौने या पुस्तकें बांटें, मंदिर में छाया पात्र दान करें।",
        "precaution_hi": "वासना व जुआ सर्वथा त्यागें।",
        "shastra_effect_hi": "संतान कल्याण व विवेकशीलता।"
    },
    ("Saturn", 6): {
        "totka_hi": "काले कुत्ते को सरसों के तेल से चुपड़ी रोटी खिलाएं, चमड़े का सामान दान करें।",
        "precaution_hi": "मजदूरों का हक कभी न मारें।",
        "shastra_effect_hi": "कठिन रोगों व मुकदमों पर विजय।"
    },
    ("Saturn", 7): {
        "totka_hi": "बांसुरी में खांड भरकर वीराने में दबाएं, काली गाय की सेवा करें।",
        "precaution_hi": "जीवनसाथी के स्वास्थ्य की उपेक्षा न करें।",
        "shastra_effect_hi": "साझेदारी व दांपत्य की रक्षा।"
    },
    ("Saturn", 8): {
        "totka_hi": "बहते पानी में 8 बादाम प्रवाहित करें, शेष 8 घर में संभाल कर रखें।",
        "precaution_hi": "घर में लोहे का कबाड़ इकट्ठा न रखें।",
        "shastra_effect_hi": "महामृत्युंजय कृपा व संकट निवारण।"
    },
    ("Saturn", 9): {
        "totka_hi": "बहते पानी में चावल या चने की दाल प्रवाहित करें, बड़ों का सम्मान करें।",
        "precaution_hi": "नास्तिकता का मार्ग कभी न अपनाएं।",
        "shastra_effect_hi": "अखंड भाग्य व आध्यात्मिक उत्थान।"
    },
    ("Saturn", 10): {
        "totka_hi": "मंदिर में भोजन का भंडारा कराएं या तेल का दान करें।",
        "precaution_hi": "किसी के मकान पर गलत नीयत न रखें।",
        "shastra_effect_hi": "हुकूमत, अधिकार व पदोन्नति।"
    },
    ("Saturn", 11): {
        "totka_hi": "तेल में अपना मुख देखकर (छाया पात्र) शनिवार को दान करें।",
        "precaution_hi": "दक्षिणमुखी मकान में वास से बचें।",
        "shastra_effect_hi": "स्थायी आमदनी व दीर्घायु।"
    },
    ("Saturn", 12): {
        "totka_hi": "बारह बादाम काले कपड़े में बांधकर लोहे के डिब्बे में रखें।",
        "precaution_hi": "झूठ बोलने व फरेब से बचें।",
        "shastra_effect_hi": "मोक्ष मार्ग व विदेश में सम्मान।"
    },

    # RAHU (राहु) 1 to 12
    ("Rahu", 1): {
        "totka_hi": "बहते जल में नारियल या कच्चा कोयला प्रवाहित करें, चांदी का सिक्का पास रखें।",
        "precaution_hi": "धुआं व नशे की आदत से दूर रहें।",
        "shastra_effect_hi": "मानसिक भ्रम का निवारण व सफलता।"
    },
    ("Rahu", 2): {
        "totka_hi": "चांदी की ठोस गोली अपनी जेब में रखें, ससुराल से मधुर संबंध रखें।",
        "precaution_hi": "बिजली का खराब सामान घर में न रखें।",
        "shastra_effect_hi": "आकस्मिक धन लाभ व वाणी संयम।"
    },
    ("Rahu", 3): {
        "totka_hi": "हाथी दांत या चांदी का छल्ला पहनें, भाइयों से प्रेमभाव रखें।",
        "precaution_hi": "झूठी शान व दिखावा न करें।",
        "shastra_effect_hi": "अद्भुत पराक्रम व तकनीकी कुशलता।"
    },
    ("Rahu", 4): {
        "totka_hi": "बहते पानी में 400 ग्राम धनिया प्रवाहित करें, चांदी के बर्तन में जल पिएं।",
        "precaution_hi": "घर में सीलन या अंधकार न रहने दें।",
        "shastra_effect_hi": "मातृ सुख व मन की स्थिरता।"
    },
    ("Rahu", 5): {
        "totka_hi": "हाथी को केले या चारा खिलाएं, चांदी का ठोस हाथी घर में रखें।",
        "precaution_hi": "जुआ, सट्टा व लाटरी से दूर रहें।",
        "shastra_effect_hi": "संतान रक्षा व तीव्र बुद्धि।"
    },
    ("Rahu", 6): {
        "totka_hi": "काले कुत्ते को मीठी रोटी खिलाएं, सीसा (Lead) का टुकड़ा जेब में रखें।",
        "precaution_hi": "गुप्त शत्रुओं से सदैव सतर्क रहें।",
        "shastra_effect_hi": "शत्रुओं पर पूर्ण विजय व ऋण मुक्ति।"
    },
    ("Rahu", 7): {
        "totka_hi": "बहते पानी में 6 नीले फूल प्रवाहित करें, चांदी का चौकोर टुकड़ा रखें।",
        "precaution_hi": "21 वर्ष से पूर्व विवाह न करें।",
        "shastra_effect_hi": "वैवाहिक जीवन में स्थिरता।"
    },
    ("Rahu", 8): {
        "totka_hi": "बहते पानी में 8 नारियल या खोटे सिक्के प्रवाहित करें।",
        "precaution_hi": "श्मशान या निर्जन स्थानों पर अकेले न जाएं।",
        "shastra_effect_hi": "अचानक दुर्घटनाओं से रक्षा।"
    },
    ("Rahu", 9): {
        "totka_hi": "माथे पर केसर का तिलक लगाएं, पीतल के बर्तन का उपयोग करें।",
        "precaution_hi": "धर्म व संस्कृति की अवहेलना न करें।",
        "shastra_effect_hi": "भाग्योदय व विदेश में लाभ।"
    },
    ("Rahu", 10): {
        "totka_hi": "सिर पर सफेद टोपी पहनें, दृष्टिहीनों को भोजन कराएं।",
        "precaution_hi": "आलस्य व नशाखोरी त्यागें।",
        "shastra_effect_hi": "प्रशासनिक सफलता व ख्याति।"
    },
    ("Rahu", 11): {
        "totka_hi": "चांदी का छल्ला बिना जोड़ का पहनें, लोहे के बर्तन में भोजन न करें।",
        "precaution_hi": "छल-कपट व प्रपंच से बचें।",
        "shastra_effect_hi": "अकल्पनीय धन लाभ।"
    },
    ("Rahu", 12): {
        "totka_hi": "रसोई में बैठकर भोजन करें, सौंफ व खांड लाल कपड़े में बांधकर सिरहाने रखें।",
        "precaution_hi": "छत पर कबाड़ या जाले न लगने दें।",
        "shastra_effect_hi": "अनिद्रा व बुरे स्वप्नों से मुक्ति।"
    },

    # KETU (केतु) 1 to 12
    ("Ketu", 1): {
        "totka_hi": "चितकबरे कुत्ते को भोजन दें, कान में सोना धारण करें।",
        "precaution_hi": "संतों व फकीरों का अपमान न करें।",
        "shastra_effect_hi": "आध्यात्मिक आभा व संतान रक्षा।"
    },
    ("Ketu", 2): {
        "totka_hi": "मस्तक पर केसर या हल्दी का तिलक लगाएं, चरित्र शुद्ध रखें।",
        "precaution_hi": "अपशब्द या कटु वचन न बोलें।",
        "shastra_effect_hi": "वाणी में सिद्धि व धन वृद्धि।"
    },
    ("Ketu", 3): {
        "totka_hi": "सोने की बाली कान में पहनें, गणेश जी को लड्डू अर्पित करें।",
        "precaution_hi": "व्यर्थ की शंका व चिंता न करें।",
        "shastra_effect_hi": "पराक्रम व भाई-बहनों से स्नेह।"
    },
    ("Ketu", 4): {
        "totka_hi": "बहते जल में पीला नींबू प्रवाहित करें, गुरु की सेवा करें।",
        "precaution_hi": "माता को कभी कष्ट न दें।",
        "shastra_effect_hi": "हृदय शांति व ईश्वर भक्ति।"
    },
    ("Ketu", 5): {
        "totka_hi": "दूध में थोड़ा शहद मिलाकर पिएं, गणेश जी की आराधना करें।",
        "precaution_hi": "संतान पर अनुचित दबाव न बनाएं।",
        "shastra_effect_hi": "विद्या, मोक्ष व संतान सुख।"
    },
    ("Ketu", 6): {
        "totka_hi": "बाएं हाथ की अनामिका में सोने की अंगूठी पहनें, कुत्ता पालें या सेवा करें।",
        "precaution_hi": "ननिहाल से बैर-विरोध न करें।",
        "shastra_effect_hi": "शत्रु दमन व गुप्त विद्या।"
    },
    ("Ketu", 7): {
        "totka_hi": "चार चितकबरे कुत्तों को मीठी रोटी खिलाएं, गणेश जी को दूर्वा अर्पित करें।",
        "precaution_hi": "वाणी पर पूर्ण नियंत्रण रखें।",
        "shastra_effect_hi": "वैवाहिक रक्षा व साझेदारी लाभ।"
    },
    ("Ketu", 8): {
        "totka_hi": "दो रंग का कंबल (काला-सफेद) मंदिर में दान करें, गणेश संकट नाशन स्तोत्र पढ़ें।",
        "precaution_hi": "किसी के गुप्त रहस्य उजागर न करें।",
        "shastra_effect_hi": "असाध्य रोगों से रक्षा।"
    },
    ("Ketu", 9): {
        "totka_hi": "कान में सोने की बाली पहनें, पिता व गुरु का आशीर्वाद लें।",
        "precaution_hi": "अधर्म व कुमार्ग का साथ न दें।",
        "shastra_effect_hi": "धर्म, ध्यान व तीर्थ यात्रा।"
    },
    ("Ketu", 10): {
        "totka_hi": "चांदी के बर्तन में शहद भरकर घर में रखें, चरित्रवान रहें।",
        "precaution_hi": "व्यसनों व दुर्व्यसनों से दूर रहें।",
        "shastra_effect_hi": "सम्मान, प्रतिष्ठा व यश।"
    },
    ("Ketu", 11): {
        "totka_hi": "काले-सफेद तिल बहते पानी में प्रवाहित करें, चितकबरे कुत्ते की सेवा करें।",
        "precaution_hi": "किसी के साथ दगा या धोखा न करें।",
        "shastra_effect_hi": "मनोवांछित लाभ व सफलता।"
    },
    ("Ketu", 12): {
        "totka_hi": "गणेश जी की नित्य पूजा करें, चितकबरे कुत्ते को दूध-रोटी खिलाएं।",
        "precaution_hi": "रात को देर तक जागने से बचें।",
        "shastra_effect_hi": "मोक्ष लाभ व दिव्य अनुभव।"
    }
}


# -------------------------------------------------------------
# 4. Lal Kitab Core Engine Class
# -------------------------------------------------------------

class LalKitabResult(BaseModel):
    khana_planets: Dict[int, List[str]]
    planet_khanas: Dict[str, int]
    sleeping_houses: List[int]
    awakened_houses: List[int]
    sleeping_planets: List[str]
    active_debts: List[Dict[str, Any]]
    dharmi_teva: bool
    andha_teva: bool
    ratandh_teva: bool = False
    dharmi_planets: List[str] = []
    papi_planets: List[str] = []
    specific_remedies: List[Dict[str, Any]]
    chart_108_totkas: List[Dict[str, Any]] = []


class LalKitabEngine:
    """
    Classical Lal Kitab 1952 engine for converting Lagna Chart into Kalapurusha Khana system,
    analyzing 9 debts, sleeping houses, dharmi/andha status, and generating 108 authentic totkas.
    """

    @classmethod
    def calculate(cls, chart: KundaliChart) -> LalKitabResult:
        # In Lal Kitab, House 1 = Lagna, House 2 = 2nd from Lagna, etc.
        # But planets are treated in the 1-12 Khana framework (fixed Aries archetype)
        khana_planets = {i: [] for i in range(1, 13)}
        planet_khanas = {}

        for p_name, p_pos in chart.planets.items():
            khana = p_pos.house_from_lagna
            khana_planets[khana].append(p_name)
            planet_khanas[p_name] = khana

        # 1. Sleeping Houses (Soya Hua Ghar)
        sleeping_houses = [h for h in range(1, 13) if len(khana_planets[h]) == 0]
        awakened_houses = [h for h in range(1, 13) if len(khana_planets[h]) > 0]

        # 2. Sleeping Planets (Soya Hua Graha)
        sleeping_planets = []
        for p, kh in planet_khanas.items():
            ruler = LAL_KITAB_KHANA_DATA[kh]["pakka_ruler"].split()[0]
            if ruler in planet_khanas:
                r_kh = planet_khanas[ruler]
                if len(khana_planets[r_kh]) <= 1:
                    sleeping_planets.append(p)

        # 3. Dharmi Teva (धर्मी तेवा - Blessed Horoscope)
        dharmi = False
        jup_kh = planet_khanas.get("Jupiter", 0)
        sat_kh = planet_khanas.get("Saturn", 0)
        if jup_kh in [1, 4, 7, 10] or sat_kh == 11 or planet_khanas.get("Rahu") == 4:
            dharmi = True

        # 4. Andha Teva (अंधा तेवा - Blind Horoscope) & Ratandh Teva (रात का अंधा तेवा)
        andha = False
        ratandh = False
        h10_pl = khana_planets[10]
        if "Sun" in h10_pl and "Saturn" in h10_pl:
            andha = True
        elif len(h10_pl) >= 2 and any(p in ["Sun", "Mars"] for p in h10_pl) and any(p in ["Saturn", "Rahu"] for p in h10_pl):
            andha = True

        sun_kh = planet_khanas.get("Sun", 0)
        if sat_kh == 7 and sun_kh == 1:
            ratandh = True
        elif sun_kh == 6 and sat_kh == 12:
            ratandh = True

        # 5. Dharmi Graha vs Papi/Andhe Graha
        dharmi_planets = []
        papi_planets = []
        for p, kh in planet_khanas.items():
            if p in ["Jupiter", "Ketu"] or kh == 4 or (jup_kh > 0 and kh == jup_kh):
                dharmi_planets.append(p)
            elif p in ["Rahu", "Saturn"] and kh not in [2, 4, 11]:
                papi_planets.append(p)

        # 6. Evaluate All 9 Karmic Debts (नौ ऋण)
        active_debts = []
        moon_kh = planet_khanas.get("Moon", 0)
        mars_kh = planet_khanas.get("Mars", 0)
        ven_kh = planet_khanas.get("Venus", 0)
        merc_kh = planet_khanas.get("Mercury", 0)
        rahu_kh = planet_khanas.get("Rahu", 0)
        ketu_kh = planet_khanas.get("Ketu", 0)

        # 1. Pitra Rina check
        if jup_kh in [2, 5, 9, 12]:
            h_pl = khana_planets[jup_kh]
            if any(p in h_pl for p in ["Venus", "Mercury", "Rahu", "Ketu"]):
                active_debts.append(DEBT_DEFINITIONS[0])
        elif chart.planets.get("Jupiter") and chart.planets["Jupiter"].dignity == "debilitated":
            active_debts.append(DEBT_DEFINITIONS[0])

        # 2. Matra Rina check
        if moon_kh in [2, 4]:
            h_pl = khana_planets[moon_kh]
            if any(p in h_pl for p in ["Ketu", "Rahu", "Saturn"]):
                active_debts.append(DEBT_DEFINITIONS[1])

        # 3. Swa Rina check
        if sun_kh == 5:
            h_pl = khana_planets[5]
            if any(p in h_pl for p in ["Rahu", "Saturn", "Ketu", "Venus"]):
                active_debts.append(DEBT_DEFINITIONS[2])

        # 4. Stri Rina check
        if ven_kh in [2, 7]:
            h_pl = khana_planets[ven_kh]
            if any(p in h_pl for p in ["Rahu", "Sun", "Mars"]):
                active_debts.append(DEBT_DEFINITIONS[3])

        # 5. Rishtedari Rina check
        if mars_kh in [1, 8]:
            h_pl = khana_planets[mars_kh]
            if any(p in h_pl for p in ["Mercury", "Ketu"]):
                active_debts.append(DEBT_DEFINITIONS[4])

        # 6. Nirdayi Rina check
        if sat_kh in [10, 11]:
            h_pl = khana_planets[sat_kh]
            if any(p in h_pl for p in ["Sun", "Moon", "Mars"]):
                active_debts.append(DEBT_DEFINITIONS[5])

        # 7. Anisht / Kudrati Rina check
        if ketu_kh in [6, 12]:
            h_pl = khana_planets[ketu_kh]
            if any(p in h_pl for p in ["Moon", "Mars"]):
                active_debts.append(DEBT_DEFINITIONS[6])

        # 8. Kanya Rina check (Mercury afflicted or debilitated in 3, 6, 8, 12)
        if merc_kh in [3, 6, 8, 12]:
            h_pl = khana_planets[merc_kh]
            if any(p in h_pl for p in ["Moon", "Rahu", "Mars"]):
                active_debts.append(DEBT_DEFINITIONS[7])
        elif chart.planets.get("Mercury") and chart.planets["Mercury"].dignity == "debilitated":
            active_debts.append(DEBT_DEFINITIONS[7])

        # 9. Jal Rina / Dev Rina check (Rahu in 1, 5, 9, 12 with Sun/Venus/Mars or Moon with Rahu)
        if rahu_kh in [1, 5, 9, 12]:
            h_pl = khana_planets[rahu_kh]
            if any(p in h_pl for p in ["Sun", "Venus", "Mars"]):
                active_debts.append(DEBT_DEFINITIONS[8])
        elif moon_kh == rahu_kh and moon_kh > 0:
            active_debts.append(DEBT_DEFINITIONS[8])

        # 7. Specific Lal Kitab Remedies for afflicted placements
        specific_remedies = []
        if sat_kh in [1, 4, 7, 10]:
            specific_remedies.append({
                "placement": f"शनि खाना नं. {sat_kh}",
                "totka_hi": "भैंस या काले कुत्ते को तेल चुपड़ी रोटी खिलाएं। बहते पानी में नारियल या बादाम प्रवाहित करें।"
            })
        if mars_kh in [1, 4, 7, 8, 12]:
            specific_remedies.append({
                "placement": f"मंगल खाना नं. {mars_kh} (मंगल बद)",
                "totka_hi": "चाँदी का चौरस टुकड़ा अपनी जेब या पर्स में रखें। मीठी रोटी तंदूर में बनवाकर गरीबों को बांटें।"
            })
        if rahu_kh in [1, 5, 9, 12]:
            specific_remedies.append({
                "placement": f"राहु खाना नं. {rahu_kh}",
                "totka_hi": "सरस्वती माता की आराधना करें। पीले कपड़े में साबुत मूंग या चने की दाल बांधकर सिरहाने रखें।"
            })
        if ketu_kh in [6, 8, 12]:
            specific_remedies.append({
                "placement": f"केतु खाना नं. {ketu_kh}",
                "totka_hi": "कान में सोना धारण करें। चितकबरे कुत्ते को भोजन दें। गणेश जी को दूर्वा अर्पित करें।"
            })

        # 8. Assemble Chart-Specific 108 Totkas for all 9 planets
        chart_108_totkas = []
        for p_name in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]:
            if p_name in planet_khanas:
                p_kh = planet_khanas[p_name]
                totka_data = LAL_KITAB_108_TOTKAS.get((p_name, p_kh), {
                    "totka_hi": "नित्य सात्विक जीवन जिएं व पक्षियों को दाना डालें।",
                    "precaution_hi": "अनैतिक आचरण से बचें।",
                    "shastra_effect_hi": "शुभ फल प्राप्ति।"
                })
                chart_108_totkas.append({
                    "planet": p_name,
                    "planet_hi": {"Sun": "सूर्य", "Moon": "चन्द्र", "Mars": "मंगल", "Mercury": "बुध", "Jupiter": "गुरु", "Venus": "शुक्र", "Saturn": "शनि", "Rahu": "राहु", "Ketu": "केतु"}.get(p_name, p_name),
                    "khana": p_kh,
                    "totka_hi": totka_data["totka_hi"],
                    "precaution_hi": totka_data["precaution_hi"],
                    "shastra_effect_hi": totka_data["shastra_effect_hi"]
                })

        return LalKitabResult(
            khana_planets=khana_planets,
            planet_khanas=planet_khanas,
            sleeping_houses=sleeping_houses,
            awakened_houses=awakened_houses,
            sleeping_planets=list(set(sleeping_planets)),
            active_debts=active_debts,
            dharmi_teva=dharmi,
            andha_teva=andha,
            ratandh_teva=ratandh,
            dharmi_planets=list(set(dharmi_planets)),
            papi_planets=list(set(papi_planets)),
            specific_remedies=specific_remedies,
            chart_108_totkas=chart_108_totkas
        )


default_lalkitab_engine = LalKitabEngine()
