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
    },
    "badhaka_maraka": {
        "shloka_sanskrit": "चरे त्वेकादशो ज्ञेयः स्थिरे नवम एव च।\nद्विस्वभावे भवेत् सप्तो बाधकेशः प्रकीर्तितः॥\nद्वितीये सप्तमे स्थाने मारकाख्यौ प्रकीर्तितौ।\nतयोर्मध्ये द्वितीयोऽपि महामारकसंज्ञितः॥",
        "shloka": "चरे त्वेकादशो ज्ञेयः स्थिरे नवम एव च।\nद्विस्वभावे भवेत् सप्तो बाधकेशः प्रकीर्तितः॥\nद्वितीये सप्तमे स्थाने मारकाख्यौ प्रकीर्तितौ।\nतयोर्मध्ये द्वितीयोऽपि महामारकसंज्ञितः॥",
        "grantha": "प्रश्नमार्ग (अध्याय १४), बृहत्पाराशर होराशास्त्र (अध्याय ४३-४४) एवं जातक पारिजात (२.४८)",
        "hindi_translation": "चर लग्न (मेष, कर्क, तुला, मकर) के लिए ११वां भाव बाधक स्थान व उसका स्वामी बाधकेश होता है; स्थिर लग्न (वृषभ, सिंह, वृश्चिक, कुंभ) के लिए ९वां भाव बाधक स्थान व उसका स्वामी बाधकेश होता है; तथा द्विस्वभाव लग्न (मिथुन, कन्या, धनु, मीन) के लिए ७वां भाव बाधक स्थान व उसका स्वामी बाधकेश होता है। द्वितीय और सप्तम भाव मारक स्थान कहलाते हैं, जिनमें द्वितीय भाव प्रबल महा-मारक संज्ञक है।",
        "anuvad_hi": "चर लग्न (मेष, कर्क, तुला, मकर) के लिए ११वां भाव बाधक स्थान व उसका स्वामी बाधकेश होता है; स्थिर लग्न (वृषभ, सिंह, वृश्चिक, कुंभ) के लिए ९वां भाव बाधक स्थान व उसका स्वामी बाधकेश होता है; तथा द्विस्वभाव लग्न (मिथुन, कन्या, धनु, मीन) के लिए ७वां भाव बाधक स्थान व उसका स्वामी बाधकेश होता है। द्वितीय और सप्तम भाव मारक स्थान कहलाते हैं, जिनमें द्वितीय भाव प्रबल महा-मारक संज्ञक है।",
        "impact_hi": "जीवन में अकस्मात उत्पन्न होने वाले अदृश्य अवरोध, स्वास्थ्य संकट एवं मारक दशा की अचूक पहचान।",
        "rule": "चर लग्न -> ११वां भाव बाधक; स्थिर लग्न -> ९वां भाव बाधक; द्विस्वभाव लग्न -> ७वां भाव बाधक। मारक -> २रा एवं ७वां भाव।"
    },
    "shadbala_pramana": {
        "shloka_sanskrit": "षड्विधं बलमेतेषां ग्रहाणां कथयाम्यहम्।\nस्थानदिग्कालचेष्टाख्या नैसर्गदृग्बलं तथा॥\nएतेषां योगतः सिद्धं षड्बलं परिकीर्तितम्।\nस्वल्पे बले फलं हीनं पूर्णे पूर्णफलं स्मृतम्॥",
        "shloka": "षड्विधं बलमेतेषां ग्रहाणां कथयाम्यहम्।\nस्थानदिग्कालचेष्टाख्या नैसर्गदृग्बलं तथा॥\nएतेषां योगतः सिद्धं षड्बलं परिकीर्तितम्।\nस्वल्पे बले फलं हीनं पूर्णे पूर्णफलं स्मृतम्॥",
        "grantha": "बृहत्पाराशर होराशास्त्र (अध्याय २७, षड्बल साधन अध्याय)",
        "hindi_translation": "महर्षि पाराशर कहते हैं: ग्रहों के छह प्रकार के बल होते हैं — स्थान बल, दिग् बल, काल बल, चेष्टा बल, नैसर्गिक बल और दृग् बल। इन छहों बलों के सम्मिलित योग को 'षड्बल' कहा जाता है। बलहीन ग्रह अपनी दशा में फल देने में अक्षम रहता है, जबकि षड्बली ग्रह अपना पूर्ण फल प्रदान करता है।",
        "anuvad_hi": "महर्षि पाराशर कहते हैं: ग्रहों के छह प्रकार के बल होते हैं — स्थान बल, दिग् बल, काल बल, चेष्टा बल, नैसर्गिक बल और दृग् बल। इन छहों बलों के सम्मिलित योग को 'षड्बल' कहा जाता है। बलहीन ग्रह अपनी दशा में फल देने में अक्षम रहता है, जबकि षड्बली ग्रह अपना पूर्ण फल प्रदान करता है।",
        "impact_hi": "ग्रहों की वास्तविक कार्यात्मक शक्ति का ६-आयामी वैज्ञानिक मापन।",
        "rule": "स्थानबल + दिग्बल + कालबल + चेष्टाबल + नैसर्गिकबल + दृग्बल = कुल षड्बल (रूपा एवं विरूपा में)।"
    },
    "ishta_kashta_pramana": {
        "shloka_sanskrit": "सप्तविंशत्युच्चबलेन चेष्टाबलं संगुण्य तन्मूलं तु इष्टफलम्।\nषष्टितः परिशोधितं कष्टफलमिति कीर्तितम्॥\nइष्टेऽधिके भवेत् सौख्यं कष्टे क्लेशमुदीरयेत्॥",
        "shloka": "सप्तविंशत्युच्चबलेन चेष्टाबलं संगुण्य तन्मूलं तु इष्टफलम्।\nषष्टितः परिशोधितं कष्टफलमिति कीर्तितम्॥\nइष्टेऽधिके भवेत् सौख्यं कष्टे क्लेशमुदीरयेत्॥",
        "grantha": "बृहत्पाराशर होराशास्त्र (अध्याय २९, श्लोक १-४) एवं फलदीपिका (अध्याय ४)",
        "hindi_translation": "ग्रह के उच्च बल तथा चेष्टा बल के गुणनफल का वर्गमूल (Geometric Mean) 'इष्ट फल' कहलाता है। साठ (६०) में से इष्ट फल घटाने पर जो प्राप्त होता है, वह 'कष्ट फल' कहलाता है। जब किसी ग्रह का इष्ट फल कष्ट फल से अधिक होता है, तो वह ग्रह अपनी दशा में सुख, समृद्धि व विजय देता है; कष्ट फल अधिक होने पर संघर्ष व क्लेश की प्राप्ति होती है।",
        "anuvad_hi": "ग्रह के उच्च बल तथा चेष्टा बल के गुणनफल का वर्गमूल (Geometric Mean) 'इष्ट फल' कहलाता है। साठ (६०) में से इष्ट फल घटाने पर जो प्राप्त होता है, वह 'कष्ट फल' कहलाता है। जब किसी ग्रह का इष्ट फल कष्ट फल से अधिक होता है, तो वह ग्रह अपनी दशा में सुख, समृद्धि व विजय देता है; कष्ट फल अधिक होने पर संघर्ष व क्लेश की प्राप्ति होती है।",
        "impact_hi": "दशा फलकथन में ग्रह का शुभत्व बनाम संघर्ष संतुलन जानने का अचूक शास्त्रीय पैमाना।",
        "rule": "इष्ट फल = √(उच्च बल × चेष्टा बल); कष्ट फल = ६० - इष्ट फल। (सीमा: ० से ६० विरूपा)।"
    },
    "bhavabala_pramana": {
        "shloka_sanskrit": "भावाधिपबलं पूर्वं भावदिग्बलमेव च।\nभावदृग्बलमित्येतद् भावबलमुदाहृतम्॥\nभावबले सति ज्ञात्वा फलानि कथयेद् बुधः।",
        "shloka": "भावाधिपबलं पूर्वं भावदिग्बलमेव च।\nभावदृग्बलमित्येतद् भावबलमुदाहृतम्॥\nभावबले सति ज्ञात्वा फलानि कथयेद् बुधः।",
        "grantha": "बृहत्पाराशर होराशास्त्र (अध्याय २८, भावबल साधन अध्याय)",
        "hindi_translation": "भाव के फल का निर्धारण तीन घटकों के योग से होता है: १. भावेश (भाव के स्वामी) का षड्बल, २. भाव का दिग्बल, तथा ३. भाव पर पड़ने वाली ग्रहों की दृष्टि का बल (भावदृग्बल)। इन तीनों के योग को 'भाव बल' कहते हैं। केवल भाव में बैठे ग्रहों से नहीं, अपितु भाव बल जानकर ही फलकथन करना चाहिए।",
        "anuvad_hi": "भाव के फल का निर्धारण तीन घटकों के योग से होता है: १. भावेश (भाव के स्वामी) का षड्बल, २. भाव का दिग्बल, तथा ३. भाव पर पड़ने वाली ग्रहों की दृष्टि का बल (भावदृग्बल)। इन तीनों के योग को 'भाव बल' कहते हैं। केवल भाव में बैठे ग्रहों से नहीं, अपितु भाव बल जानकर ही फलकथन करना चाहिए।",
        "impact_hi": "द्वादश भावों की कार्यसिद्धि क्षमता, स्थिरता एवं समृद्धि का समग्र मापन।",
        "rule": "भाव बल = भावाधिपति षड्बल + भाव दिग्बल + भाव दृष्टि बल। मानक: >४०० विरूपा = उत्तम, ३३०-४०० = मध्यम, <३३० = निर्बल।"
    },
    "jaimini_sutras": {
        "shloka_sanskrit": "अथात्मकारकः सांशोऽधिककलस्तत्र कारकांशः।\nअभिपश्यन्ति रिक्षाणि न स्वाभिमुखं तत्रस्थम्॥\nदारादिभ्यश्चार्गला न निहन्त्री रिपुकेवला।\nकेतौ कैवल्यं क्रियावान् उपपदं पदं पितुश्च॥",
        "shloka": "अथात्मकारकः सांशोऽधिककलस्तत्र कारकांशः।\nअभिपश्यन्ति रिक्षाणि न स्वाभिमुखं तत्रस्थम्॥\nदारादिभ्यश्चार्गला न निहन्त्री रिपुकेवला।\nकेतौ कैवल्यं क्रियावान् उपपदं पदं पितुश्च॥",
        "grantha": "महर्षि जैमिनी विरचित 'उपदेश सूत्राणि' (अध्याय १ व २)",
        "hindi_translation": "जो ग्रह सर्वोच्च भोगांश पर स्थित हो वह आत्मकारक है और नवांश में उसकी स्थिति कारकांश कहलाती है। राशियाँ सम्मुख के अतिरिक्त अन्य पर दृष्टि डालती हैं। २, ४, ११वें भाव अर्गला व १२, १०, ३रे भाव विरोधार्गला हैं। १२वें में केतु मोक्ष का कारक है तथा द्वादशेश का आरूढ़ उपपद लग्न कहलाता है।",
        "anuvad_hi": "जो ग्रह सर्वोच्च भोगांश पर स्थित हो वह आत्मकारक है और नवांश में उसकी स्थिति कारकांश कहलाती है। राशियाँ सम्मुख के अतिरिक्त अन्य पर दृष्टि डालती हैं। २, ४, ११वें भाव अर्गला व १२, १०, ३रे भाव विरोधार्गला हैं। १२वें में केतु मोक्ष का कारक है तथा द्वादशेश का आरूढ़ उपपद लग्न कहलाता है।",
        "impact_hi": "आत्मिक प्रयोजन, इष्ट देव, दांपत्य एवं गुप्त प्रारब्ध का अचूक उद्घाटन।",
        "rule": "चर कारक (७ ग्रह भोगांश क्रम), राशि दृष्टि (चर-स्थिर-द्विस्वभाव), अर्गला एवं उपपद लग्न।"
    },
    "double_transit": {
        "shloka_sanskrit": "यस्मिन् भावे गुरुर्गच्छेत् शनिना सह संस्थितः।\nतद्भावजं फलं सर्वं साधयत्येव नान्यथा॥\nदशापतिर्बली यत्र गोचरे च बली भवेत्।\nतदा तस्य फलं पूर्णं विपरीतं विपर्यये॥",
        "shloka": "यस्मिन् भावे गुरुर्गच्छेत् शनिना सह संस्थितः।\nतद्भावजं फलं सर्वं साधयत्येव नान्यथा॥\nदशापतिर्बली यत्र गोचरे च बली भवेत्।\nतदा तस्य फलं पूर्णं विपरीतं विपर्यये॥",
        "grantha": "बृहत्पाराशर होराशास्त्रम् (गोचराध्याय) एवं फलदीपिका (अध्याय २०, श्लोक २५)",
        "hindi_translation": "जिस भाव अथवा भावेश पर शनि और गुरु दोनों का संयुक्त प्रभाव (स्थिति या दृष्टि) पड़ता है, उस भाव का फल निश्चित रूप से घटित होता है। शनि कर्म का संपादन और काल की परिपक्वता निर्धारित करता है, जबकि देवगुरु बृहस्पति ईश्वरीय कृपा व सिद्धि प्रदान करते हैं। जब दशा स्वामी भी गोचर में बली हो, तो घटना का शत-प्रतिशत फलित होना निश्चित हो जाता है।",
        "anuvad_hi": "जिस भाव अथवा भावेश पर शनि और गुरु दोनों का संयुक्त प्रभाव (स्थिति या दृष्टि) पड़ता है, उस भाव का फल निश्चित रूप से घटित होता है। शनि कर्म का संपादन और काल की परिपक्वता निर्धारित करता है, जबकि देवगुरु बृहस्पति ईश्वरीय कृपा व सिद्धि प्रदान करते हैं। जब दशा स्वामी भी गोचर में बली हो, तो घटना का शत-प्रतिशत फलित होना निश्चित हो जाता है।",
        "impact_hi": "विवाह, संतान, पदोन्नति, गृह-निर्माण जैसी प्रमुख जीवन घटनाओं का काल निर्धारण।",
        "rule": "शनि दृष्टि/स्थिति + गुरु दृष्टि/स्थिति (एक ही भाव या भावेश पर) = दोहरा गोचर फलित ट्रिगर।"
    },
    "shodashvarga_vaisheshikamsa": {
        "shloka_sanskrit": "क्षेत्रं होराऽथ दृक्काणस्तुरियांशस्ततः परम्।\nसप्तमांशो नवांशश्च दशमांशोऽथ द्वादशः॥\nषोडशांशस्तथा ज्ञेयः विंशांशश्च ततः परम्।\nचतुर्विंशांशकश्चैव सप्तविंशांशकस्तथा॥\nत्रिंशांशकः खवेदांशस्तथा चाक्षवेदांशकः।\nषष्ट्यंशश्चैव वर्गाणां षोडशैव प्रकीर्तिताः॥\nद्वाभ्यां स्यात् पारिजाताख्यो त्रिभिरुत्तमसंज्ञकः।\nचतुर्भिर्गोपुराख्यो हि पञ्चभिः सिंहनामकः॥",
        "shloka": "क्षेत्रं होराऽथ दृक्काणस्तुरियांशस्ततः परम्।\nसप्तमांशो नवांशश्च दशमांशोऽथ द्वादशः॥\nषोडशांशस्तथा ज्ञेयः विंशांशश्च ततः परम्।\nचतुर्विंशांशकश्चैव सप्तविंशांशकस्तथा॥\nत्रिंशांशकः खवेदांशस्तथा चाक्षवेदांशकः।\nषष्ट्यंशश्चैव वर्गाणां षोडशैव प्रकीर्तिताः॥\nद्वाभ्यां स्यात् पारिजाताख्यो त्रिभिरुत्तमसंज्ञकः।\nचतुर्भिर्गोपुराख्यो हि पञ्चभिः सिंहनामकः॥",
        "grantha": "बृहत्पाराशर होराशास्त्रम् (अध्याय ६, षोडशवर्गाध्याय एवं अध्याय ४५, वैशेषिकांश)",
        "hindi_translation": "महर्षि पराशर द्वारा प्रतिपादित १६ मुख्य वर्ग — D1 से D60 हैं। जब कोई ग्रह अपने उच्च, स्वराशि अथवा मित्रराशि के वर्गों में स्थित होता है, तो दो वर्गों में 'पारिजात', तीन में 'उत्तम', चार में 'गोपुर', पांच में 'सिंहासन', छह में 'पारावत', सात में 'देवलोक', आठ में 'ऐरावत' और नौ वर्गों में 'वैशेषिक' संज्ञक होकर जीवन में अखंड राजयोग व प्रतिष्ठा प्रदान करता है।",
        "anuvad_hi": "महर्षि पराशर द्वारा प्रतिपादित १६ मुख्य वर्ग — D1 से D60 हैं। जब कोई ग्रह अपने उच्च, स्वराशि अथवा मित्रराशि के वर्गों में स्थित होता है, तो दो वर्गों में 'पारिजात', तीन में 'उत्तम', चार में 'गोपुर', पांच में 'सिंहासन', छह में 'पारावत', सात में 'देवलोक', आठ में 'ऐरावत' और नौ वर्गों में 'वैशेषिक' संज्ञक होकर जीवन में अखंड राजयोग व प्रतिष्ठा प्रदान करता है।",
        "impact_hi": "ग्रहों की सूक्ष्म गरिमा, विंशोपक बल एवं जीवन में राजयोग सामर्थ्य का निर्धारण।",
        "rule": "२ से लेकर १०+ शुभ वर्गों में उपस्थिति अनुसार पारिजात से कामधेनु तक वैशेषिकांश फल।"
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

    @classmethod
    def audit_badhaka_maraka(cls, chart: Any) -> Dict[str, Any]:
        """
        Audits Badhaka Sthana/Badhakesh and Maraka Sthanas/Marakeshas
        according to Parashara and Prashna Marga.
        """
        lagna_sign_id = chart.lagna_sign_id
        if lagna_sign_id in [1, 4, 7, 10]:
            r_type = "चर (Movable)"
            badhaka_house = 11
        elif lagna_sign_id in [2, 5, 8, 11]:
            r_type = "स्थिर (Fixed)"
            badhaka_house = 9
        else:
            r_type = "द्विस्वभाव (Dual)"
            badhaka_house = 7

        badhaka_h_idx = badhaka_house - 1
        badhakesh = chart.houses[badhaka_h_idx].lord
        badhaka_sign_name = chart.houses[badhaka_h_idx].sign_name
        badhakesh_p = chart.planets.get(badhakesh)
        badhakesh_pos = f"भाव {badhakesh_p.house_from_lagna} ({badhakesh_p.sign_name})" if badhakesh_p else "अज्ञात"

        # Maraka: 2nd and 7th houses
        h2_lord = chart.houses[1].lord
        h2_p = chart.planets.get(h2_lord)
        h7_lord = chart.houses[6].lord
        h7_p = chart.planets.get(h7_lord)

        return {
            "lagna_type": r_type,
            "badhaka_house": badhaka_house,
            "badhaka_sign": badhaka_sign_name,
            "badhakesh": badhakesh,
            "badhakesh_placement": badhakesh_pos,
            "maraka_primary": {
                "house": 2,
                "lord": h2_lord,
                "placement": f"भाव {h2_p.house_from_lagna} ({h2_p.sign_name})" if h2_p else "—",
                "label": "प्रबल महा-मारक (Primary Maraka)"
            },
            "maraka_secondary": {
                "house": 7,
                "lord": h7_lord,
                "placement": f"भाव {h7_p.house_from_lagna} ({h7_p.sign_name})" if h7_p else "—",
                "label": "द्वितीयक मारक (Secondary Maraka)"
            },
            "shastriya_shloka": SHASTRIYA_SHLOKAS["badhaka_maraka"]
        }


default_shastriya_pramana_engine = ShastriyaPramanaEngine()

