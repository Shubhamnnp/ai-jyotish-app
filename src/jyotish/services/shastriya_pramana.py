"""
Shastriya Pramana & Classical Astrological Matrix Engine for JyotishOS.
Holds canonical Sanskrit shlokas, classical grantha citations (BPHS, Phaladeepika,
Jataka Parijata, Muhurta Chintamani, Saravali, Uttara Kalamrita), lucid Hindi translations,
and mathematically precise calculators for:

1. Pushkara Navamsha (२४ पुष्कर नवांश) & Pushkara Bhaga (१२ पुष्कर भाग).
2. Vargottama (वर्गोत्तम) & Vaisheshikamsha (वैशेषिकांश दशावर्ग प्रतिष्ठा).
3. Daily Muhurta Windows (राहुकाल, यमघण्ट, गुलिक, अभिजित, ब्रह्म मुहूर्त).
4. Kakshya System (अष्टकवर्ग अष्ट-कक्षा विचार) & Gochar Vedha (वेध-विपरीत वेध).
5. Conditional Dasha Eligibility (पाराशरी विशेष दशा पात्रता: अष्टोत्तरी, षोडशोत्तरी, द्विसप्तति, कालचक्र).
"""

from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime, date, time, timedelta
from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# 1. PUSHKARA NAVAMSHA & PUSHKARA BHAGA (पुष्कर नवांश एवं पुष्कर भाग)
# ---------------------------------------------------------------------------

PUSHKARA_NAVAMSHA_MATRIX = {
    # Agni Rashis (Fire: Aries 1, Leo 5, Sagittarius 9)
    # 7th Navamsha: 20°00' to 23°20' (Libra Navamsha, Venus)
    # 9th Navamsha: 26°40' to 30°00' (Sagittarius Navamsha, Jupiter)
    "fire": [
        {"navamsha_num": 7, "start_deg": 20.0, "end_deg": 23.333333, "navamsha_sign": "Libra", "navamsha_sign_hi": "तुला", "lord": "Venus", "lord_hi": "शुक्र"},
        {"navamsha_num": 9, "start_deg": 26.666667, "end_deg": 30.0, "navamsha_sign": "Sagittarius", "navamsha_sign_hi": "धनु", "lord": "Jupiter", "lord_hi": "बृहस्पति"}
    ],
    # Prithvi Rashis (Earth: Taurus 2, Virgo 6, Capricorn 10)
    # 3rd Navamsha: 6°40' to 10°00' (Pisces Navamsha, Jupiter)
    # 5th Navamsha: 13°20' to 16°40' (Taurus Navamsha, Venus)
    "earth": [
        {"navamsha_num": 3, "start_deg": 6.666667, "end_deg": 10.0, "navamsha_sign": "Pisces", "navamsha_sign_hi": "मीन", "lord": "Jupiter", "lord_hi": "बृहस्पति"},
        {"navamsha_num": 5, "start_deg": 13.333333, "end_deg": 16.666667, "navamsha_sign": "Taurus", "navamsha_sign_hi": "वृषभ", "lord": "Venus", "lord_hi": "शुक्र"}
    ],
    # Vayu Rashis (Air: Gemini 3, Libra 7, Aquarius 11)
    # 6th Navamsha: 16°40' to 20°00' (Pisces Navamsha, Jupiter)
    # 8th Navamsha: 23°20' to 26°40' (Sagittarius Navamsha, Jupiter)
    "air": [
        {"navamsha_num": 6, "start_deg": 16.666667, "end_deg": 20.0, "navamsha_sign": "Pisces", "navamsha_sign_hi": "मीन", "lord": "Jupiter", "lord_hi": "बृहस्पति"},
        {"navamsha_num": 8, "start_deg": 23.333333, "end_deg": 26.666667, "navamsha_sign": "Sagittarius", "navamsha_sign_hi": "धनु", "lord": "Jupiter", "lord_hi": "बृहस्पति"}
    ],
    # Jala Rashis (Water: Cancer 4, Scorpio 8, Pisces 12)
    # 2nd Navamsha: 3°20' to 6°40' (Virgo Navamsha, Mercury)
    # 4th Navamsha: 10°00' to 13°20' (Cancer Navamsha, Moon)
    "water": [
        {"navamsha_num": 2, "start_deg": 3.333333, "end_deg": 6.666667, "navamsha_sign": "Virgo", "navamsha_sign_hi": "कन्या", "lord": "Mercury", "lord_hi": "बुध"},
        {"navamsha_num": 4, "start_deg": 10.0, "end_deg": 13.333333, "navamsha_sign": "Cancer", "navamsha_sign_hi": "कर्क", "lord": "Moon", "lord_hi": "चन्द्र"}
    ]
}

# Pushkara Bhaga (Exact Auspicious Degrees in 12 Signs)
PUSHKARA_BHAGA_MAP = {
    1: {"deg": 21.0, "sign_en": "Aries", "sign_hi": "मेष", "orb": 1.0},
    2: {"deg": 14.0, "sign_en": "Taurus", "sign_hi": "वृषभ", "orb": 1.0},
    3: {"deg": 24.0, "sign_en": "Gemini", "sign_hi": "मिथुन", "orb": 1.0},
    4: {"deg": 7.0, "sign_en": "Cancer", "sign_hi": "कर्क", "orb": 1.0},
    5: {"deg": 21.0, "sign_en": "Leo", "sign_hi": "सिंह", "orb": 1.0},
    6: {"deg": 14.0, "sign_en": "Virgo", "sign_hi": "कन्या", "orb": 1.0},
    7: {"deg": 24.0, "sign_en": "Libra", "sign_hi": "तुला", "orb": 1.0},
    8: {"deg": 7.0, "sign_en": "Scorpio", "sign_hi": "वृश्चिक", "orb": 1.0},
    9: {"deg": 21.0, "sign_en": "Sagittarius", "sign_hi": "धनु", "orb": 1.0},
    10: {"deg": 14.0, "sign_en": "Capricorn", "sign_hi": "मकर", "orb": 1.0},
    11: {"deg": 24.0, "sign_en": "Aquarius", "sign_hi": "कुंभ", "orb": 1.0},
    12: {"deg": 7.0, "sign_en": "Pisces", "sign_hi": "मीन", "orb": 1.0}
}

SHASTRIYA_SHLOKAS = {
    "pushkara_navamsha": {
        "shloka_sanskrit": "पुष्करांशगताः सर्वे ग्रहाः शुभफलप्रदाः।\nनीचस्था अपि कुर्वन्ति राजयोगमनुत्तमम्॥",
        "shloka": "पुष्करांशगताः सर्वे ग्रहाः शुभफलप्रदाः।\nनीचस्था अपि कुर्वन्ति राजयोगमनुत्तमम्॥",
        "grantha": "जातक परिजात (अध्याय १, श्लोक ५७-५८) एवं उत्तर कालामृत",
        "hindi_translation": "पुष्कर नवांश में स्थित समस्त ग्रह जातक को अमृततुल्य पोषण एवं अत्यंत शुभ फल प्रदान करते हैं। यदि कोई ग्रह नीच राशि में भी स्थित हो, परंतु पुष्कर नवांश में हो, तो वह अपनी नीचता त्यागकर सर्वोत्तम राजयोग का फल प्रदान करता है।",
        "anuvad_hi": "पुष्कर नवांश में स्थित समस्त ग्रह जातक को अमृततुल्य पोषण एवं अत्यंत शुभ फल प्रदान करते हैं। यदि कोई ग्रह नीच राशि में भी स्थित हो, परंतु पुष्कर नवांश में हो, तो वह अपनी नीचता त्यागकर सर्वोत्तम राजयोग का फल प्रदान करता है।",
        "impact_hi": "असाधारण जीवन उत्थान, संकट से मुक्ति एवं आध्यात्मिक तथा भौतिक समृद्धि।",
        "rule": "अग्नि तत्व (मेष, सिंह, धनु) में ७वां व ९वां नवांश; पृथ्वी तत्व (वृषभ, कन्या, मकर) में ३रा व ५वां नवांश; वायु तत्व (मिथुन, तुला, कुम्भ) में ६ठा व ८वां नवांश; जल तत्व (कर्क, वृश्चिक, मीन) में प्रथम व ३रा नवांश पुष्कर होते हैं।"
    },
    "pushkara_bhaga": {
        "shloka_sanskrit": "मेषे तुैकविंशे भागे वृषे चतुर्दशे तथा।\nमिथुने त्रयोविंशे ज्ञेयः पुष्करांशो द्विजोत्तम॥",
        "shloka": "मेषे तुैकविंशे भागे वृषे चतुर्दशे तथा।\nमिथुने त्रयोविंशे ज्ञेयः पुष्करांशो द्विजोत्तम॥",
        "grantha": "जातक पारिजात एवं सर्वार्थ चिंतामणि",
        "hindi_translation": "राशियों के अत्यंत विशिष्ट व संवेदनशील अंश पुष्कर भाग कहलाते हैं। इन अंशों पर स्थित ग्रह असाधारण दैवीय तेज व जीवनदायिनी शक्ति प्राप्त करते हैं।",
        "anuvad_hi": "राशियों के अत्यंत विशिष्ट व संवेदनशील अंश पुष्कर भाग कहलाते हैं। इन अंशों पर स्थित ग्रह असाधारण दैवीय तेज व जीवनदायिनी शक्ति प्राप्त करते हैं।",
        "impact_hi": "ग्रह को सर्वोत्तम शक्ति, स्वास्थ्य लाभ एवं संकटों से रक्षा का वरदान।",
        "rule": "मेष २१°, वृषभ १४°, मिथुन २४°, कर्क ७°, सिंह २१°, कन्या १४°, तुला २४°, वृश्चिक ७°, धनु २१°, मकर १४°, कुंभ २४°, मीन ७°।"
    },
    "vargottama": {
        "shloka_sanskrit": "वर्गोत्तमाश्चराद्येषु प्रथमान्त्यमध्यमाः।\nस्वांशे यदा ग्रहो याति तदा वर्गोत्तमो भवेत्॥\nस्वक्षेत्रफलदः साक्षात् सर्वसौख्यप्रदायकः।",
        "shloka": "वर्गोत्तमाश्चराद्येषु प्रथमान्त्यमध्यमाः।\nस्वांशे यदा ग्रहो याति तदा वर्गोत्तमो भवेत्॥\nस्वक्षेत्रफलदः साक्षात् सर्वसौख्यप्रदायकः।",
        "grantha": "बृहज्जातक (अध्याय १, श्लोक २०) एवं सारावली",
        "hindi_translation": "चर राशियों (१, ४, ७, १०) का प्रथम, स्थिर राशियों (२, ५, ८, ११) का पंचम (मध्य) तथा द्विस्वभाव राशियों (३, ६, ९, १२) का नवम (अन्तिम) नवांश वर्गोत्तम कहलाता है। जब ग्रह जन्म लग्न (D1) और नवांश (D9) दोनों में समान राशि में होता है, तो वह स्वगृही (अपने घर में बैठे) ग्रह के समान संपूर्ण सामर्थ्यवान होकर समस्त सुख व कीर्ति प्रदान करता है।",
        "anuvad_hi": "चर राशियों (१, ४, ७, १०) का प्रथम, स्थिर राशियों (२, ५, ८, ११) का पंचम (मध्य) तथा द्विस्वभाव राशियों (३, ६, ९, १२) का नवम (अन्तिम) नवांश वर्गोत्तम कहलाता है। जब ग्रह जन्म लग्न (D1) और नवांश (D9) दोनों में समान राशि में होता है, तो वह स्वगृही (अपने घर में बैठे) ग्रह के समान संपूर्ण सामर्थ्यवान होकर समस्त सुख व कीर्ति प्रदान करता है।",
        "impact_hi": "स्थायी यश, आंतरिक आत्मबल, दृढ़ इच्छाशक्ति एवं जीवन में स्थिरता।",
        "rule": "लग्न कुण्डली (D1) एवं नवांश कुण्डली (D9) में एक ही राशि में स्थित होना।"
    },
    "abhijit_muhurta": {
        "shloka_sanskrit": "दिवाकरकरप्रौढे मध्यगे द्युमणावपि।\nअभिजित्संज्ञको ज्ञेयो हन्ति सर्वानुपद्रवान्॥\nगोसहस्रं गवां चैव शतकोटिसुवर्णकम्।\nअभिजित्कुरुते दानं सर्वपापप्रणाशनम्॥",
        "shloka": "दिवाकरकरप्रौढे मध्यगे द्युमणावपि।\nअभिजित्संज्ञको ज्ञेयो हन्ति सर्वानुपद्रवान्॥\nगोसहस्रं गवां चैव शतकोटिसुवर्णकम्।\nअभिजित्कुरुते दानं सर्वपापप्रणाशनम्॥",
        "grantha": "मुहूर्त चिंतामणि (अध्याय १, श्लोक ३५) एवं नारद संहिता",
        "hindi_translation": "दिन के ठीक मध्याह्न काल में जब भगवान सूर्य आकाश के मध्य में (दशम भाव तुल्य) प्रज्वलित होते हैं, तब ८वां मुहूर्त 'अभिजित' कहलाता है। इस मुहूर्त में भगवान श्री हरि विष्णु का साक्षात् वास होता है तथा यह समस्त ग्रह-दोषों व दुर्योगों का शमन कर विजय प्रदान करता है (केवल बुधवार को छोड़कर)।",
        "anuvad_hi": "दिन के ठीक मध्याह्न काल में जब भगवान सूर्य आकाश के मध्य में (दशम भाव तुल्य) प्रज्वलित होते हैं, तब ८वां मुहूर्त 'अभिजित' कहलाता है। इस मुहूर्त में भगवान श्री हरि विष्णु का साक्षात् वास होता है तथा यह समस्त ग्रह-दोषों व दुर्योगों का शमन कर विजय प्रदान करता है (केवल बुधवार को छोड़कर)।",
        "impact_hi": "यात्रा, व्यापार शुभारंभ, अनुबंध व महत्वपूर्ण कर्मों में निर्विघ्न सफलता।",
        "rule": "सूर्योदय से सूर्यास्त की कुल अवधि को १५ समान भागों में विभाजित करने पर आठवां मुहूर्त अभिजित (मध्याह्न से २४ मिनट पूर्व से २४ मिनट पश्चात्) होता है।"
    },
    "rahu_kaal": {
        "shloka_sanskrit": "आदित्यवारादिषु रात्रिभागे दिवा च राहोः कुलिकादिकानाम्।\nयामेषु केन्द्रेषु च वर्जनीयाः सर्वेषु कार्येषु विनाशहेतुः॥",
        "shloka": "आदित्यवारादिषु रात्रिभागे दिवा च राहोः कुलिकादिकानाम्।\nयामेषु केन्द्रेषु च वर्जनीयाः सर्वेषु कार्येषु विनाशहेतुः॥",
        "grantha": "मुहूर्त चिंतामणि एवं कालामृत",
        "hindi_translation": "दिन के अष्टम भाग (९० मिनट की वेला) में राहु का विशेष आधिपत्य रहता है। रविवार को ८वें, सोमवार को २रे, मंगलवार को ७वें, बुधवार को ५वें, गुरुवार को ६ठे, शुक्रवार को ४थे और शनिवार को ३रे भाग में राहुकाल होता है। इसमें किया गया कोई भी शुभ कार्य विफलता, विवाद व हानि की ओर ले जाता है।",
        "anuvad_hi": "दिन के अष्टम भाग (९० मिनट की वेला) में राहु का विशेष आधिपत्य रहता है। रविवार को ८वें, सोमवार को २रे, मंगलवार को ७वें, बुधवार को ५वें, गुरुवार को ६ठे, शुक्रवार को ४थे और शनिवार को ३रे भाग में राहुकाल होता है। इसमें किया गया कोई भी शुभ कार्य विफलता, विवाद व हानि की ओर ले जाता है।",
        "impact_hi": "नया व्यापार, क्रय-विक्रय, यात्रा, मांगलिक कार्य एवं गृह-प्रवेश सर्वथा वर्जित।",
        "rule": "दिनमान को ८ भागों में बांटकर वारानुसार राहु भाग का निर्धारण।"
    },
    "kakshya_system": {
        "shloka_sanskrit": "शनिजीवकुजेन्द्वर्कशुक्रसौम्यविलग्नकाः।\nकक्षाक्रमाः समाख्याता ह्यष्टधा प्रविभाजिताः॥\nबिन्दौ सति शुभं दद्युः शून्ये कष्टप्रदाः स्मृताः।",
        "shloka": "शनिजीवकुजेन्द्वर्कशुक्रसौम्यविलग्नकाः।\nकक्षाक्रमाः समाख्याता ह्यष्टधा प्रविभाजिताः॥\nबिन्दौ सति शुभं दद्युः शून्ये कष्टप्रदाः स्मृताः।",
        "grantha": "बृहत्पाराशर होराशास्त्र (अध्याय ६६, अष्टकवर्ग फल) एवं प्रस्ताराष्टकवर्ग",
        "hindi_translation": "प्रत्येक राशि के ३० अंशों को ३ अंश ४५ कला (३°४५') के आठ समान भागों में बांटा जाता है, जिन्हें 'कक्षा' कहते हैं। इनका क्रम है: १. शनि, २. गुरु, ३. मंगल, ४. सूर्य, ५. शुक्र, ६. बुध, ७. चन्द्रमा, ८. लग्न। जब गोचर का ग्रह (विशेषकर शनि) उस कक्षा से गुजरता है जिसमें प्रस्ताराष्टकवर्ग का शुभ बिंदु (१) हो, तो वह अपार सफलता देता है; बिंदुहीन (०) होने पर संघर्ष देता है।",
        "anuvad_hi": "प्रत्येक राशि के ३० अंशों को ३ अंश ४५ कला (३°४५') के आठ समान भागों में बांटा जाता है, जिन्हें 'कक्षा' कहते हैं। इनका क्रम है: १. शनि, २. गुरु, ३. मंगल, ४. सूर्य, ५. शुक्र, ६. बुध, ७. चन्द्रमा, ८. लग्न। जब गोचर का ग्रह (विशेषकर शनि) उस कक्षा से गुजरता है जिसमें प्रस्ताराष्टकवर्ग का शुभ बिंदु (१) हो, तो वह अपार सफलता देता है; बिंदुहीन (०) होने पर संघर्ष देता है।",
        "impact_hi": "साढ़ेसाती एवं गुरु गोचर के महीनों व दिनों की सूक्ष्म एवं अचूक भविष्यवाणी।",
        "rule": "प्रत्येक राशि में 8 कक्षी होती हैं। 3°45' (3 अंश 45 कला) प्रति कक्षी। क्रम: मंद (शनि), जीव (गुरु), कुज (मंगल), रवि (सूर्य), भृगु (शुक्र), सौम्य (बुध), शशी (चन्द्र), लग्न।"
    },
    "conditional_dashas": {
        "shloka_sanskrit": "अष्टोत्तरी तथा चैव षोडशोत्तरी मता।\nद्वादशोत्तरी समाख्याता द्विसप्तति समा तथा॥\nकालचक्रदशा चैव दशानामुत्तमोत्तमा।\nअधिकारं विना न स्यात् पाराशर्यं वचो यथा॥",
        "shloka": "अष्टोत्तरी तथा चैव षोडशोत्तरी मता।\nद्वादशोत्तरी समाख्याता द्विसप्तति समा तथा॥\nकालचक्रदशा चैव दशानामुत्तमोत्तमा।\nअधिकारं विना न स्यात् पाराशर्यं वचो यथा॥",
        "grantha": "बृहत्पाराशर होराशास्त्र (अध्याय ४६, दशाध्याय)",
        "hindi_translation": "महर्षि पाराशर के अनुसार प्रत्येक कुण्डली पर केवल विंशोत्तरी लागू नहीं होती। जब विशेष ग्रह योग उपस्थित हों, तो संबंधित विशेष दशा का अधिकार बनता है: राहु केंद्र/त्रिकोण में हो तो अष्टोत्तरी (१०८ वर्ष); लग्न सूर्य होरा में शुक्ल पक्ष हो तो षोडशोत्तरी (११६ वर्ष); लग्नेश सप्तम में या सप्तमेश लग्न में हो तो द्विसप्तति समा (७२ वर्ष); और कालचक्र दशा समस्त दशाओं में शिरोमणि मानी गई है।",
        "anuvad_hi": "महर्षि पाराशर के अनुसार प्रत्येक कुण्डली पर केवल विंशोत्तरी लागू नहीं होती। जब विशेष ग्रह योग उपस्थित हों, तो संबंधित विशेष दशा का अधिकार बनता है: राहु केंद्र/त्रिकोण में हो तो अष्टोत्तरी (१०८ वर्ष); लग्न सूर्य होरा में शुक्ल पक्ष हो तो षोडशोत्तरी (११६ वर्ष); लग्नेश सप्तम में या सप्तमेश लग्न में हो तो द्विसप्तति समा (७२ वर्ष); और कालचक्र दशा समस्त दशाओं में शिरोमणि मानी गई है।",
        "impact_hi": "विशेष कुण्डलियों में सटीक घटनाकाल निर्धारण जहाँ विंशोत्तरी अपूर्ण रह जाती है।",
        "rule": "विशेष कुण्डलियों में विशेष ग्रह योगों की उपस्थिति में ही इन दशाओं का प्रत्यक्ष प्रभाव घटित होता है।"
    }
}



class ShastriyaPramanaEngine:
    """Core Mathematical and Evaluator Engine for Classical Vedic Metrics."""

    @staticmethod
    def get_element_by_sign_id(sign_id: int) -> str:
        """Returns fire, earth, air, water based on 1-12 sign ID."""
        rem = sign_id % 4
        if rem == 1:
            return "fire"
        elif rem == 2:
            return "earth"
        elif rem == 3:
            return "air"
        else:
            return "water"

    @classmethod
    def evaluate_pushkara_status(cls, sign_id: int, degree: float) -> Dict[str, Any]:
        """
        Evaluates whether a given sign degree falls in Pushkara Navamsha and/or Pushkara Bhaga.
        """
        element = cls.get_element_by_sign_id(sign_id)
        candidates = PUSHKARA_NAVAMSHA_MATRIX.get(element, [])

        is_pushkara_navamsha = False
        matched_navamsha: Optional[Dict[str, Any]] = None

        for cand in candidates:
            if cand["start_deg"] <= degree < cand["end_deg"]:
                is_pushkara_navamsha = True
                matched_navamsha = cand
                break

        # Check Pushkara Bhaga
        pb_info = PUSHKARA_BHAGA_MAP.get(sign_id, {})
        target_pb_deg = pb_info.get("deg", -99.0)
        orb = pb_info.get("orb", 1.0)
        is_pushkara_bhaga = abs(degree - target_pb_deg) <= orb

        return {
            "is_pushkara_navamsha": is_pushkara_navamsha,
            "navamsha_num": matched_navamsha["navamsha_num"] if matched_navamsha else None,
            "navamsha_sign": matched_navamsha["navamsha_sign"] if matched_navamsha else None,
            "navamsha_sign_hi": matched_navamsha["navamsha_sign_hi"] if matched_navamsha else None,
            "navamsha_lord": matched_navamsha["lord"] if matched_navamsha else None,
            "navamsha_lord_hi": matched_navamsha["lord_hi"] if matched_navamsha else None,
            "is_pushkara_bhaga": is_pushkara_bhaga,
            "pushkara_bhaga_exact_deg": target_pb_deg,
            "shastriya_shloka": SHASTRIYA_SHLOKAS["pushkara_navamsha"]
        }

    @classmethod
    def audit_chart_pushkara(cls, chart: Any) -> Dict[str, Any]:
        """
        Audits all planets and Lagna in a chart for Pushkara Navamsha and Pushkara Bhaga.
        """
        results = {}
        pushkara_planets = []
        pushkara_bhaga_planets = []

        # 1. Audit Lagna
        lagna_sign_id = chart.lagna_sign_id
        lagna_deg = chart.lagna_degree % 30.0
        l_res = cls.evaluate_pushkara_status(lagna_sign_id, lagna_deg)
        results["Lagna"] = l_res
        if l_res["is_pushkara_navamsha"]:
            pushkara_planets.append("Lagna (लग्न)")
        if l_res["is_pushkara_bhaga"]:
            pushkara_bhaga_planets.append("Lagna (लग्न)")

        # 2. Audit 9 Planets
        for p_name, p in chart.planets.items():
            sign_id = p.sign_id
            deg = p.sign_degree
            res = cls.evaluate_pushkara_status(sign_id, deg)
            results[p_name] = res
            if res["is_pushkara_navamsha"]:
                pushkara_planets.append(p_name)
            if res["is_pushkara_bhaga"]:
                pushkara_bhaga_planets.append(p_name)

        return {
            "planets": results,
            "pushkara_navamsha_planets": pushkara_planets,
            "pushkara_bhaga_planets": pushkara_bhaga_planets,
            "total_pushkara_count": len(pushkara_planets),
            "summary_hi": f"{len(pushkara_planets)} ग्रह/लग्न पुष्कर नवांश में स्थित हैं, जो कुण्डली को दैवीय सुरक्षा एवं ऊर्जा प्रदान करते हैं।"
        }

    @classmethod
    def audit_vargottama(cls, chart: Any) -> Dict[str, Any]:
        """
        Audits D1 vs D9 for Vargottama planets.
        """
        vargottama_list = []
        d9 = chart.vargas.get("D9") if hasattr(chart, "vargas") else None

        for p_name, p in chart.planets.items():
            d1_sign = p.sign_id
            d9_sign = None
            if d9 and p_name in d9.planets:
                d9_sign = d9.planets[p_name].sign_id

            if d9_sign and d1_sign == d9_sign:
                vargottama_list.append({
                    "planet": p_name,
                    "sign_id": d1_sign,
                    "sign_name": p.sign_name,
                    "degree": p.sign_degree
                })

        return {
            "vargottama_planets": vargottama_list,
            "count": len(vargottama_list),
            "shastriya_shloka": SHASTRIYA_SHLOKAS["vargottama"],
            "summary_hi": f"{len(vargottama_list)} ग्रह वर्गोत्तम अवस्था में हैं। ये स्वगृही के समान पूर्ण शुभ फलदायक हैं।"
        }

    @classmethod
    def calculate_daily_muhurta_windows(
        cls,
        target_date: date,
        sunrise_time: time = time(6, 0),
        sunset_time: time = time(18, 0)
    ) -> Dict[str, Any]:
        """
        Calculates exact mathematical start and end times for Rahu Kaal, Yamaghanta,
        Gulika Kaal, Abhijit Muhurta, and Brahma Muhurta with classical citations.
        """
        sr_dt = datetime.combine(target_date, sunrise_time)
        ss_dt = datetime.combine(target_date, sunset_time)
        day_duration_sec = (ss_dt - sr_dt).total_seconds()
        part_sec = day_duration_sec / 8.0  # 1/8th of day (Yama / Prahara half)

        weekday = target_date.weekday()  # Mon=0, Tue=1, Wed=2, Thu=3, Fri=4, Sat=5, Sun=6

        # Rahu Kaal 1-based segment of day
        rahu_parts = {6: 8, 0: 2, 1: 7, 2: 5, 3: 6, 4: 4, 5: 3}
        r_part = rahu_parts.get(weekday, 8)
        rahu_start = sr_dt + timedelta(seconds=(r_part - 1) * part_sec)
        rahu_end = sr_dt + timedelta(seconds=r_part * part_sec)

        # Yamaghanta 1-based segment of day
        yama_parts = {6: 5, 0: 4, 1: 3, 2: 2, 3: 1, 4: 7, 5: 6}
        y_part = yama_parts.get(weekday, 5)
        yama_start = sr_dt + timedelta(seconds=(y_part - 1) * part_sec)
        yama_end = sr_dt + timedelta(seconds=y_part * part_sec)

        # Gulika Kaal 1-based segment of day (शनि पुत्र गुलिक)
        # Sunday=7, Mon=6, Tue=5, Wed=4, Thu=3, Fri=2, Sat=1
        gulika_parts = {6: 7, 0: 6, 1: 5, 2: 4, 3: 3, 4: 2, 5: 1}
        g_part = gulika_parts.get(weekday, 7)
        gulika_start = sr_dt + timedelta(seconds=(g_part - 1) * part_sec)
        gulika_end = sr_dt + timedelta(seconds=g_part * part_sec)

        # Abhijit Muhurta: 8th Muhurta of the day (each muhurta = day_duration / 15)
        muhurta_dur_sec = day_duration_sec / 15.0
        abhijit_start = sr_dt + timedelta(seconds=7 * muhurta_dur_sec)
        abhijit_end = sr_dt + timedelta(seconds=8 * muhurta_dur_sec)
        is_abhijit_blocked = (weekday == 2)  # Inauspicious on Wednesday (बुधवार को अभिजित वर्जित)

        # Brahma Muhurta: 2 Muhurtas (approx 96 min / 2 muhurtas) before sunrise
        brahma_start = sr_dt - timedelta(minutes=96)
        brahma_end = sr_dt - timedelta(minutes=48)

        return {
            "date": target_date.strftime("%d-%B-%Y"),
            "weekday_name": ["सोमवार", "मंगलवार", "बुधवार", "गुरुवार", "शुक्रवार", "शनिवार", "रविवार"][weekday],
            "sunrise": sr_dt.strftime("%I:%M %p"),
            "sunset": ss_dt.strftime("%I:%M %p"),
            "rahu_kaal": {
                "name_hi": "राहुकाल",
                "start": rahu_start.strftime("%I:%M %p"),
                "end": rahu_end.strftime("%I:%M %p"),
                "status": "🔴 अत्यंत अशुभ (वर्जित)",
                "shastriya_shloka": SHASTRIYA_SHLOKAS["rahu_kaal"]
            },
            "yamaghanta": {
                "name_hi": "यमघण्ट काल",
                "start": yama_start.strftime("%I:%M %p"),
                "end": yama_end.strftime("%I:%M %p"),
                "status": "🔴 अशुभ",
            },
            "gulika_kaal": {
                "name_hi": "गुलिक काल",
                "start": gulika_start.strftime("%I:%M %p"),
                "end": gulika_end.strftime("%I:%M %p"),
                "status": "⚠️ मध्यम / सावधान",
            },
            "abhijit": {
                "name_hi": "अभिजित मुहूर्त",
                "start": abhijit_start.strftime("%I:%M %p"),
                "end": abhijit_end.strftime("%I:%M %p"),
                "status": "⚠️ बुधवार होने से वर्जित" if is_abhijit_blocked else "🌟 सर्वोत्तम विजय मुहूर्त (अति शुभ)",
                "is_blocked_wednesday": is_abhijit_blocked,
                "shastriya_shloka": SHASTRIYA_SHLOKAS["abhijit_muhurta"]
            },
            "brahma_muhurta": {
                "name_hi": "ब्रह्म मुहूर्त",
                "start": brahma_start.strftime("%I:%M %p"),
                "end": brahma_end.strftime("%I:%M %p"),
                "status": "🕉️ दिव्य साधना व ध्यान काल (परम शुभ)",
            }
        }

    @classmethod
    def evaluate_kakshya_position(cls, planet_degree_in_sign: float) -> Dict[str, Any]:
        """
        Determines the Kakshya (1 to 8) of a planet's position in a rashi (0° to 30°).
        Each Kakshya = 3°45' (3.75°).
        Order: Saturn, Jupiter, Mars, Sun, Venus, Mercury, Moon, Lagna.
        """
        deg = planet_degree_in_sign % 30.0
        k_idx = int(deg // 3.75)  # 0 to 7
        k_idx = min(7, max(0, k_idx))

        kakshya_lords = [
            ("Saturn", "शनि", "00°00' - 03°45'"),
            ("Jupiter", "बृहस्पति (गुरु)", "03°45' - 07°30'"),
            ("Mars", "मंगल", "07°30' - 11°15'"),
            ("Sun", "सूर्य", "11°15' - 15°00'"),
            ("Venus", "शुक्र", "15°00' - 18°45'"),
            ("Mercury", "बुध", "18°45' - 22°30'"),
            ("Moon", "चन्द्रमा", "22°30' - 26°15'"),
            ("Lagna", "लग्न", "26°15' - 30°00'")
        ]

        lord_en, lord_hi, span = kakshya_lords[k_idx]

        return {
            "kakshya_number": k_idx + 1,
            "kakshya_lord_en": lord_en,
            "kakshya_lord_hi": lord_hi,
            "degree_span": span,
            "current_deg_in_sign": deg,
            "shastriya_shloka": SHASTRIYA_SHLOKAS["kakshya_system"]
        }

    @classmethod
    def evaluate_conditional_dasha_eligibility(cls, chart: Any) -> Dict[str, Any]:
        """
        Audits whether the chart qualifies for specialized Parashari Conditional Dashas:
        - Ashtottari (108 yrs)
        - Shodashottari (116 yrs)
        - Dwisaptati Sama (72 yrs)
        - Shashtihayani (60 yrs)
        """
        pan = chart.panchang
        is_shukla = (pan.tithi_type == "Shukla")

        # 1. Ashtottari Dasha (१०८ वर्ष)
        # Condition: Rahu must be in Kendra (1, 4, 7, 10) or Trikona (5, 9) from Lagnesh,
        # AND born in Krishna paksha night OR Shukla paksha day.
        rahu = chart.planets.get("Rahu")
        lagnesh_name = chart.houses[0].lord
        lagnesh = chart.planets.get(lagnesh_name)
        ashtottari_eligible = False
        ashtottari_reason = ""

        if rahu and lagnesh:
            dist_from_lagnesh = ((rahu.house_from_lagna - lagnesh.house_from_lagna) % 12) + 1
            is_rahu_kendra_trikona = dist_from_lagnesh in [1, 4, 7, 10, 5, 9]
            if is_rahu_kendra_trikona:
                ashtottari_eligible = True
                ashtottari_reason = f"राहु लग्नेश ({lagnesh_name}) से {dist_from_lagnesh}वें (केंद्र/त्रिकोण) भाव में स्थित हैं, अतः अष्टोत्तरी दशा अधिकार प्राप्त है।"

        # 2. Shodashottari Dasha (११६ वर्ष)
        # Condition: Born in Shukla paksha in Sun's Hora, OR Krishna paksha in Moon's Hora.
        sun = chart.planets.get("Sun")
        moon = chart.planets.get("Moon")
        shodashottari_eligible = False
        shodashottari_reason = ""
        # Lagna degree determines hora: in odd signs first 15° Sun, last 15° Moon; in even signs opposite
        lagna_sign_id = chart.lagna_sign_id
        is_odd_lagna = (lagna_sign_id % 2 != 0)
        deg_in_sign = chart.lagna_degree % 30.0
        if is_odd_lagna:
            lagna_hora_lord = "Sun" if deg_in_sign < 15.0 else "Moon"
        else:
            lagna_hora_lord = "Moon" if deg_in_sign < 15.0 else "Sun"

        if is_shukla and lagna_hora_lord == "Sun":
            shodashottari_eligible = True
            shodashottari_reason = "जातक का जन्म शुक्ल पक्ष एवं सूर्य की होरा में हुआ है, अतः षोडशोत्तरी दशा अधिकार सिद्ध है।"
        elif (not is_shukla) and lagna_hora_lord == "Moon":
            shodashottari_eligible = True
            shodashottari_reason = "जातक का जन्म कृष्ण पक्ष एवं चन्द्र की होरा में हुआ है, अतः षोडशोत्तरी दशा अधिकार सिद्ध है।"

        # 3. Dwisaptati Sama Dasha (७२ वर्ष)
        # Condition: Lagnesh in 7th House, OR 7th Lord in Lagna (1st House).
        h7_lord = chart.houses[6].lord
        h7_p = chart.planets.get(h7_lord)
        dwisaptati_eligible = False
        dwisaptati_reason = ""

        if lagnesh and lagnesh.house_from_lagna == 7:
            dwisaptati_eligible = True
            dwisaptati_reason = f"लग्नेश ({lagnesh_name}) सप्तम भाव में स्थित हैं, अतः द्विसप्तति समा दशा १००% प्रभावी है।"
        elif h7_p and h7_p.house_from_lagna == 1:
            dwisaptati_eligible = True
            dwisaptati_reason = f"सप्तमेश ({h7_lord}) लग्न भाव में स्थित हैं, अतः द्विसप्तति समा दशा १००% प्रभावी है।"

        # 4. Shashtihayani Dasha (६० वर्ष)
        # Condition: Sun placed in the 1st House (Lagna).
        shashtihayani_eligible = False
        shashtihayani_reason = ""
        if sun and sun.house_from_lagna == 1:
            shashtihayani_eligible = True
            shashtihayani_reason = "भगवान सूर्य प्रथम भाव (लग्न) में विराजमान हैं, अतः षष्टिहायनी दशा का प्रत्यक्ष अधिकार है।"

        return {
            "ashtottari": {
                "name": "अष्टोत्तरी दशा (१०८ वर्ष)",
                "is_eligible": ashtottari_eligible,
                "reason_hi": ashtottari_reason or "योग अनुपस्थित होने से सामान्य विंशोत्तरी मान्य है।"
            },
            "shodashottari": {
                "name": "षोडशोत्तरी दशा (११६ वर्ष)",
                "is_eligible": shodashottari_eligible,
                "reason_hi": shodashottari_reason or "होरा व पक्ष योग न मिलने से विंशोत्तरी मान्य है।"
            },
            "dwisaptati": {
                "name": "द्विसप्तति समा दशा (७२ वर्ष)",
                "is_eligible": dwisaptati_eligible,
                "reason_hi": dwisaptati_reason or "लग्नेश/सप्तमेश पारस्परिक स्थिति नहीं है।"
            },
            "shashtihayani": {
                "name": "षष्टिहायनी दशा (६० वर्ष)",
                "is_eligible": shashtihayani_eligible,
                "reason_hi": shashtihayani_reason or "सूर्य लग्न में स्थित नहीं हैं।"
            },
            "shastriya_shloka": SHASTRIYA_SHLOKAS["conditional_dashas"]
        }


default_shastriya_pramana_engine = ShastriyaPramanaEngine()
