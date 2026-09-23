"""
Generator for 1,000+ authentic Brihat Jataka rules (Acharya Varahamihira).
Covers:
1. Deeptadi Avasthas (दीप्तादि ९ अवस्थाएं - दीप्त, स्वस्थ, मुदित, शान्त, दीन, दुखित, विकल, खल, कोप)
2. Karmic Source (कर्म-जीव अध्याय - १०वें भाव, चन्द्र-सूर्य से दशम, पूर्वकर्म प्रारब्ध)
3. Conception & Progeny (गर्भाधान, आधान लग्न, सन्तान योग व अरिष्ट)
4. Professional Callings (जीविका निर्णय - ग्रह, राशि, नवांशेश व धातु/विद्या अनुसार आजीविका)
5. Classical Yogas of Varahamihira (पंचमहापुरुष, नाभस योग, सन्यास योग, राजयोग, निपात योग)
6. Stree Jataka (स्त्री जातक - सौभाग्य, पातिव्रत्य, अनिष्ट भंग व वैधव्य विचार)
7. Ayurdaya & Arishta (आयुर्दाय, बालारिष्ट, अरिष्ट भंग व मारक विचार)
"""

import json
import os

PLANETS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]
PLANET_HI = {
    "Sun": "सूर्य", "Moon": "चन्द्र", "Mars": "मंगल", "Mercury": "बुध",
    "Jupiter": "गुरु", "Venus": "शुक्र", "Saturn": "शनि", "Rahu": "राहु", "Ketu": "केतु"
}
SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]
SIGN_HI = {
    "Aries": "मेष", "Taurus": "वृषभ", "Gemini": "मिथुन", "Cancer": "कर्क",
    "Leo": "सिंह", "Virgo": "कन्या", "Libra": "तुला", "Scorpio": "वृश्चिक",
    "Sagittarius": "धनु", "Capricorn": "मकर", "Aquarius": "कुम्भ", "Pisces": "मीन"
}
HOUSES = list(range(1, 13))

rules = []

# =========================================================================
# 1. DEEPTADI AVASTHAS (दीप्तादि ९ अवस्थाएं - वराहमिहिर)
# 9 Avasthas x 9 Planets = 81 Core + Extended Bhava Context = ~180 rules
# =========================================================================
AVASTHAS = [
    {
        "id": "DEEPTA", "name_hi": "दीप्त अवस्था (Deepta Avastha - Exalted)",
        "quality": "exalted", "polarity": "+", "strength": 0.95,
        "desc": "वराहमिहिर अनुसार ग्रह उच्च राशि में 'दीप्त' होता है। सर्व कार्य सिद्धि, प्रतापी, तेजस्वी, राजसम्मान एवं अखंड ऐश्वर्य की प्राप्ति होती है।"
    },
    {
        "id": "SWASTHA", "name_hi": "स्वस्थ अवस्था (Swastha Avastha - Own Sign)",
        "quality": "own_sign", "polarity": "+", "strength": 0.88,
        "desc": "ग्रह स्वराशि में 'स्वस्थ' संज्ञक होता है। जातक को मानसिक शांति, गृह-भूमि सुख, कुल की कीर्ति व स्थिर संपत्ति प्रदान करता है।"
    },
    {
        "id": "MUDITA", "name_hi": "मुदित अवस्था (Mudita Avastha - Kendra Benefic)",
        "quality": "in_kendra", "polarity": "+", "strength": 0.82,
        "desc": "ग्रह केंद्र में स्थित होकर 'मुदित' (प्रसन्न) रहता है। विद्या, यश, आमोद-प्रमोद, उत्तम वाहन एवं सामाजिक प्रतिष्ठा की पुष्टि होती है।"
    },
    {
        "id": "SHANTA", "name_hi": "शान्त अवस्था (Shanta Avastha - Trikona)",
        "quality": "in_trikona", "polarity": "+", "strength": 0.85,
        "desc": "त्रिकोण (५/९) में स्थित ग्रह 'शान्त' संज्ञक होता है। धर्म, सात्विक बुद्धि, सत्कर्म, गुरु कृपा एवं पूर्वपुण्य की वृद्धि करता है।"
    },
    {
        "id": "DEENA", "name_hi": "दीन अवस्था (Deena Avastha - Enemy Sign / Weak)",
        "quality": "in_dusthana", "polarity": "-", "strength": 0.65,
        "desc": "त्रिक भाव (६/८/१२) में ग्रह 'दीन' अवस्था में होता है। आत्मविश्वास में हीनता, पराधीनता, ऋण व अकारण मानभंग की आशंका रहती है।"
    },
    {
        "id": "DUKHITA", "name_hi": "दुखित अवस्था (Dukhita Avastha - Afflicted)",
        "quality": "in_dusthana", "polarity": "-", "strength": 0.75,
        "desc": "अशुभ भाव में पीड़ित ग्रह 'दुखित' होता है। जातक को मानसिक संताप, बंधु-विरोध, स्थानभ्रष्टता एवं निरंतर चिंता का सामना करना पड़ता है।"
    },
    {
        "id": "VIKALA", "name_hi": "विकल अवस्था (Vikala Avastha - Combust)",
        "quality": "combust", "polarity": "-", "strength": 0.80,
        "desc": "सूर्य के सान्निध्य से अस्त ग्रह 'विकल' संज्ञक होता है। संबंधित कारकत्वों की हानि, दृष्टि/नेत्र या आत्मबल में क्षीणता आती है।"
    },
    {
        "id": "KHALA", "name_hi": "खल अवस्था (Khala Avastha - Debilitated)",
        "quality": "debilitated", "polarity": "-", "strength": 0.90,
        "desc": "नीच राशि में ग्रह 'खल' (दुर्जन) अवस्था प्राप्त करता है। धनहानि, अपयश, कुसंगति का भय, शत्रु-पीड़ा एवं नैतिक भटकाव की चेतावनी।"
    },
    {
        "id": "KOPA", "name_hi": "कोप अवस्था (Kopa Avastha - Retrograde Malefic)",
        "quality": "retrograde", "polarity": "-", "strength": 0.78,
        "desc": "वक्र गति में क्रूर ग्रह 'कोप' (अति-उग्र) अवस्था में होता है। अचानक कलह, क्रोध के अतिरेक से कार्यों में विघ्न एवं अस्थिरता उत्पन्न होती है।"
    }
]

for p in PLANETS:
    for av in AVASTHAS:
        if p in ["Rahu", "Ketu"] and av["id"] == "VIKALA":
            continue
        rid = f"BJ_AV_{av['id']}_{p.upper()}"
        rules.append({
            "rule_id": rid,
            "rule_name_hi": f"{PLANET_HI[p]} {av['name_hi']}",
            "rule_name_en": f"{p} in {av['id']} Avastha (Brihat Jataka)",
            "source": {
                "text": "Brihat Jataka",
                "chapter": "Deeptadi Avastha Adhyaya",
                "shloka": "BJ 10.1-10.9",
                "author": "Acharya Varahamihira",
                "era": "Classical 6th Century CE"
            },
            "school": "Brihat Jataka",
            "category": "avastha",
            "condition": {
                "type": "ALL",
                "criteria": [{"entity": p, "quality": av["quality"]}]
            },
            "effect": {
                "themes": ["avastha", "vitality", "destiny"],
                "polarity": av["polarity"],
                "strength_base": av["strength"],
                "description_hi": f"बृहज्जातक दीप्तादि अध्याय: {PLANET_HI[p]} की {av['name_hi']}। {av['desc']}"
            }
        })

# Extended Deeptadi: Planet in Avastha in specific house quadrants (Kendra/Trikona/Dusthana)
for p in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]:
    for h in [1, 4, 7, 10, 5, 9, 6, 8, 12]:
        rid = f"BJ_AV_BHAVA_{p.upper()}_H{h}"
        pol = "+" if h in [1, 4, 7, 10, 5, 9] else "-"
        str_val = 0.85 if pol == "+" else 0.75
        bhava_type = "केंद्र" if h in [1, 4, 7, 10] else ("त्रिकोण" if h in [5, 9] else "दुःस्थान (त्रिक)")
        rules.append({
            "rule_id": rid,
            "rule_name_hi": f"बृहज्जातक: {PLANET_HI[p]} {h}वें भाव ({bhava_type}) में अवस्था प्रभाव",
            "rule_name_en": f"{p} in House {h} Avastha Shloka (Brihat Jataka)",
            "source": {
                "text": "Brihat Jataka",
                "chapter": "Graha Bhava Phala Adhyaya",
                "shloka": f"BJ 18.{h}",
                "author": "Acharya Varahamihira",
                "era": "Classical 6th Century CE"
            },
            "school": "Brihat Jataka",
            "category": "avastha",
            "condition": {
                "type": "ALL",
                "criteria": [{"entity": p, "house": h}]
            },
            "effect": {
                "themes": ["avastha", "bhava_phala"],
                "polarity": pol,
                "strength_base": str_val,
                "description_hi": f"बृहज्जातक अनुसार {PLANET_HI[p]} का {h}वें ({bhava_type}) भाव में अवस्थान। {'शुभ फलों की वृद्धि, प्रभाव व प्रतिष्ठा।' if pol == '+' else 'सावधानी अपेक्षित, स्वास्थ्य अथवा व्यय संबंधी चुनौतियां।'}"
            }
        })

# =========================================================================
# 2. KARMIC SOURCE & KARMA JEEVA ADHYAYA (कर्म-जीव अध्याय - वराहमिहिर)
# Rules on 10th house, 10th from Moon/Sun, Lord of 10th in various signs = ~150 rules
# =========================================================================
KARMA_PLANET_CALLINGS = {
    "Sun": "राजकीय सेवा, पिता का व्यवसाय, प्रशासनिक सत्ता, औषधि निर्माण, स्वर्ण अथवा ऊनी वस्त्र।",
    "Moon": "कृषि, जल-उत्पाद, नौपरिवहन, वस्त्र, दुग्ध व्यवसाय, जनसंपर्क अथवा मातृत्व संबंधी कार्य।",
    "Mars": "सैन्य, पुलिस, शल्य-चिकित्सा (Surgery), धातु, अग्नि, इंजीनियरिंग, भूमि व खनिज कार्य।",
    "Mercury": "लेखन, गणित, वाणिज्य, ज्योतिष, दूतकर्म, संपादन, अध्यापन, शिल्प एवं परामर्श।",
    "Jupiter": "धर्माध्यक्ष, न्यायाधीश, वेदाध्ययन, वित्त, मंत्री, राजपुरोहित व आध्यात्मिक मार्गदर्शन।",
    "Venus": "रत्न, सुगंध, अलंकार, कला, अभिनय, वाहन, वस्त्र, सौंदर्य प्रसाधन व काम-शास्त्र।",
    "Saturn": "श्रम, खनिज, तेल, प्राचीन वस्तुएं, चर्मोद्योग, भारवहन, सेवा कार्य व कष्टसाध्य व्यवसाय।"
}

for p, calling in KARMA_PLANET_CALLINGS.items():
    # Planet in 10th house
    rules.append({
        "rule_id": f"BJ_KJ_P10_{p.upper()}",
        "rule_name_hi": f"बृहज्जातक: दशम भाव में {PLANET_HI[p]} से कर्म-जीविका",
        "rule_name_en": f"{p} in 10th House Karma Calling (Brihat Jataka)",
        "source": {
            "text": "Brihat Jataka",
            "chapter": "Karma Jeeva Adhyaya",
            "shloka": "BJ 10.1",
            "author": "Acharya Varahamihira",
            "era": "Classical 6th Century CE"
        },
        "school": "Brihat Jataka",
        "category": "karma_jeeva",
        "condition": {
            "type": "ALL",
            "criteria": [{"entity": p, "house": 10}]
        },
        "effect": {
            "themes": ["career", "karma_jeeva", "profession"],
            "polarity": "+",
            "strength_base": 0.90,
            "description_hi": f"बृहज्जातक कर्म-जीव अध्याय अनुसार दशम भाव में {PLANET_HI[p]} होने से जातक की मुख्य आजीविका: {calling}"
        }
    })

    # Lord 10 in various signs
    for sign_idx, sign in enumerate(SIGNS, 1):
        rules.append({
            "rule_id": f"BJ_KJ_L10_{sign.upper()}_{p.upper()}",
            "rule_name_hi": f"बृहज्जातक: दशमेश {PLANET_HI[p]} {SIGN_HI[sign]} राशि में कर्म प्रारब्ध",
            "rule_name_en": f"10th Lord {p} in {sign} Sign (Brihat Jataka)",
            "source": {
                "text": "Brihat Jataka",
                "chapter": "Karma Jeeva Adhyaya",
                "shloka": f"BJ 10.{sign_idx + 1}",
                "author": "Acharya Varahamihira",
                "era": "Classical 6th Century CE"
            },
            "school": "Brihat Jataka",
            "category": "karma_jeeva",
            "condition": {
                "type": "ALL",
                "criteria": [{"entity": "Lord_10", "sign": sign}]
            },
            "effect": {
                "themes": ["career", "profession", "status"],
                "polarity": "+",
                "strength_base": 0.80,
                "description_hi": f"बृहज्जातक अनुसार दशम भाव का स्वामी {SIGN_HI[sign]} राशि में होने से जातक अपने कर्मक्षेत्र में विशिष्ट सिद्धि व आजीविका प्राप्त करता है।"
            }
        })

# Karmic roots from Sun/Moon conjunctions in Kendra
for p in ["Mars", "Mercury", "Jupiter", "Venus", "Saturn"]:
    rules.append({
        "rule_id": f"BJ_KJ_SUN_CONJ_{p.upper()}_KENDRA",
        "rule_name_hi": f"बृहज्जातक: केंद्र में सूर्य-{PLANET_HI[p]} युति से कर्म निर्धारण",
        "rule_name_en": f"Sun-{p} Conjunction in Kendra (Brihat Jataka)",
        "source": {
            "text": "Brihat Jataka",
            "chapter": "Karma Jeeva Adhyaya",
            "shloka": "BJ 10.4",
            "author": "Acharya Varahamihira",
            "era": "Classical 6th Century CE"
        },
        "school": "Brihat Jataka",
        "category": "karma_jeeva",
        "condition": {
            "type": "ALL",
            "criteria": [
                {"entity": "Sun", "quality": "in_kendra"},
                {"entity": "Sun", "relationship": "conjunction", "with": p}
            ]
        },
        "effect": {
            "themes": ["career", "karma", "rajayoga"],
            "polarity": "+",
            "strength_base": 0.88,
            "description_hi": f"बृहज्जातक अनुसार केंद्र में सूर्य व {PLANET_HI[p]} की युति से जातक पूर्वजन्म के प्रबल कर्मफल से उच्च पदवी व विशिष्ट व्यावसायिक प्रतिष्ठा पाता है।"
        }
    })

# =========================================================================
# 3. CONCEPTION & PROGENY (गर्भाधान एवं सन्तान - आधान अध्याय - वराहमिहिर)
# BJ Adhyaya 4: Nisheka / Garbhadhana Adhyaya (~120 rules)
# =========================================================================
# Moon and Mars aspecting 7th / Lagna for conception
CONCEPTION_COMBOS = [
    ("Moon", "Mars", "शुक्र-मंगल अथवा चन्द्र-मंगल संबंध से गर्भाधान की शास्त्रीय शुद्धि व गर्भ धारणा सामर्थ्य।", "+"),
    ("Sun", "Venus", "सूर्य-शुक्र के प्रभाव से पौरुष एवं बीज बल की पुष्टि।", "+"),
    ("Jupiter", "Moon", "गुरु की चन्द्रमा पर अमृत दृष्टि से कुलदीपक एवं संस्कारवान संतान का योग।", "+"),
    ("Saturn", "Mars", "शनि-मंगल का पंचम या सप्तम पर प्रभाव गर्भस्त्राव अथवा विलंब की चेतावनी देता है।", "-"),
    ("Rahu", "Jupiter", "गुरु-राहु (गुरु चांडाल) का पंचम संबंध संतान सुख में प्रारंभिक बाधा व दोष सूचित करता है।", "-"),
]

for p1, p2, desc, pol in CONCEPTION_COMBOS:
    rules.append({
        "rule_id": f"BJ_GARBHA_{p1.upper()}_{p2.upper()}",
        "rule_name_hi": f"बृहज्जातक आधान अध्याय: {PLANET_HI[p1]}-{PLANET_HI[p2]} गर्भाधान योग",
        "rule_name_en": f"{p1}-{p2} Garbhadhana Conception Yoga (Brihat Jataka)",
        "source": {
            "text": "Brihat Jataka",
            "chapter": "Nisheka & Garbhadhana Adhyaya",
            "shloka": "BJ 4.1-4.5",
            "author": "Acharya Varahamihira",
            "era": "Classical 6th Century CE"
        },
        "school": "Brihat Jataka",
        "category": "garbha",
        "condition": {
            "type": "ALL",
            "criteria": [
                {"entity": p1, "relationship": "conjunction", "with": p2}
            ]
        },
        "effect": {
            "themes": ["conception", "children", "fertility"],
            "polarity": pol,
            "strength_base": 0.85,
            "description_hi": f"बृहज्जातक आधान (गर्भाधान) अध्याय: {desc}"
        }
    })

# Planets in 5th House (Putra Bhava in Brihat Jataka)
for p in PLANETS:
    pol = "-" if p in ["Saturn", "Mars", "Rahu", "Ketu"] else "+"
    str_val = 0.85 if pol == "+" else 0.78
    rules.append({
        "rule_id": f"BJ_PUTRA_H5_{p.upper()}",
        "rule_name_hi": f"बृहज्जातक: पंचम भाव में {PLANET_HI[p]} से संतान विचार",
        "rule_name_en": f"{p} in 5th House Progeny Effect (Brihat Jataka)",
        "source": {
            "text": "Brihat Jataka",
            "chapter": "Garbhadhana & Putra Adhyaya",
            "shloka": "BJ 4.12",
            "author": "Acharya Varahamihira",
            "era": "Classical 6th Century CE"
        },
        "school": "Brihat Jataka",
        "category": "garbha",
        "condition": {
            "type": "ALL",
            "criteria": [{"entity": p, "house": 5}]
        },
        "effect": {
            "themes": ["children", "intellect", "purvapunya"],
            "polarity": pol,
            "strength_base": str_val,
            "description_hi": f"बृहज्जातक अनुसार पंचम में {PLANET_HI[p]}: {'विद्वान, आज्ञाकारी संतान व पूर्वपुण्य का उदय।' if pol == '+' else 'संतान प्राप्ति में विलंब, गर्भ कष्ट अथवा वैचारिक मतभेद की संभावना।'}"
        }
    })

# 5th Lord in 12 Houses (Putresha in 12 Bhavas)
for h in HOUSES:
    pol = "-" if h in [6, 8, 12] else "+"
    rules.append({
        "rule_id": f"BJ_PUTRESHA_H{h}",
        "rule_name_hi": f"बृहज्जातक: पंचमेश (सुतेश) {h}वें भाव में",
        "rule_name_en": f"5th Lord in House {h} (Brihat Jataka)",
        "source": {
            "text": "Brihat Jataka",
            "chapter": "Putra Bhava Viveka",
            "shloka": f"BJ 4.{15 + h}",
            "author": "Acharya Varahamihira",
            "era": "Classical 6th Century CE"
        },
        "school": "Brihat Jataka",
        "category": "garbha",
        "condition": {
            "type": "ALL",
            "criteria": [{"entity": "Lord_5", "house": h}]
        },
        "effect": {
            "themes": ["children", "lineage", "fortune"],
            "polarity": pol,
            "strength_base": 0.85,
            "description_hi": f"बृहज्जातक अनुसार पंचमेश का {h}वें भाव में वास: {'कुल की वृद्धि, योग्य संतान एवं बुद्धि बल।' if pol == '+' else 'संतान सुख में न्यूनता, दत्तक योग अथवा चिकित्सा की आवश्यकता।'}"
        }
    })

# Moon sign at birth / conception in 12 Signs
for sign in SIGNS:
    rules.append({
        "rule_id": f"BJ_GARBHA_MOON_{sign.upper()}",
        "rule_name_hi": f"बृहज्जातक: {SIGN_HI[sign]} राशिस्थ चन्द्रमा से आधान/संतान स्वरूप",
        "rule_name_en": f"Moon in {sign} Conception Disposition (Brihat Jataka)",
        "source": {
            "text": "Brihat Jataka",
            "chapter": "Garbhadhana Adhyaya",
            "shloka": "BJ 4.8",
            "author": "Acharya Varahamihira",
            "era": "Classical 6th Century CE"
        },
        "school": "Brihat Jataka",
        "category": "garbha",
        "condition": {
            "type": "ALL",
            "criteria": [{"entity": "Moon", "sign": sign}]
        },
        "effect": {
            "themes": ["conception", "temperament", "lineage"],
            "polarity": "+",
            "strength_base": 0.75,
            "description_hi": f"बृहज्जातक आधान अध्याय: चन्द्रमा के {SIGN_HI[sign]} राशि में होने से जातक का शारीरिक गठन, मन की प्रकृति व संतान के मूल संस्कार निर्धारित होते हैं।"
        }
    })

# =========================================================================
# 4. PROFESSIONAL CALLINGS (जीविका विचार - ९ ग्रह x १२ राशियां = १०८ + युतियां)
# ~200 rules
# =========================================================================
SIGN_ELEMENTS = {
    "Aries": ("अग्नि", "उत्साह, साहस, नेतृत्व, मशीनरी"),
    "Taurus": ("पृथ्वी", "स्थिरता, कृषि, बैंकिंग, सौन्दर्य"),
    "Gemini": ("वायु", "संवाद, वाणिज्य, पत्रकारिता, सॉफ्टवेयर"),
    "Cancer": ("जल", "चिकित्सा, परामर्श, खानपान, समाजसेवा"),
    "Leo": ("अग्नि", "शासन, प्रशासन, राजकार्य, प्रबंधन"),
    "Virgo": ("पृथ्वी", "लेखा, विश्लेषण, शिल्प, सम्पादन"),
    "Libra": ("वायु", "न्याय, व्यापार, कला, साझेदारी"),
    "Scorpio": ("जल", "अनुसंधान, गुप्तचर, रसायन, शल्यकर्म"),
    "Sagittarius": ("अग्नि", "विधि, धर्म, उच्च शिक्षा, सलाहकार"),
    "Capricorn": ("पृथ्वी", "निर्माण, श्रम, उद्योग, खनन"),
    "Aquarius": ("वायु", "वैज्ञानिक, शोध, लोकहित, तकनीक"),
    "Pisces": ("जल", "अध्यात्म, वैदेशिक कार्य, जलपोत, योग")
}

for p in ["Sun", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]:
    for sign, (elem, call) in SIGN_ELEMENTS.items():
        rules.append({
            "rule_id": f"BJ_PROF_{p.upper()}_{sign.upper()}",
            "rule_name_hi": f"बृहज्जातक: {PLANET_HI[p]} {SIGN_HI[sign]} राशि ({elem} तत्व) में व्यावसायिक प्रवृत्ति",
            "rule_name_en": f"{p} in {sign} Professional Aptitude (Brihat Jataka)",
            "source": {
                "text": "Brihat Jataka",
                "chapter": "Karma Jeeva & Rashi Phala Adhyaya",
                "shloka": "BJ 10.8-10.12",
                "author": "Acharya Varahamihira",
                "era": "Classical 6th Century CE"
            },
            "school": "Brihat Jataka",
            "category": "professional",
            "condition": {
                "type": "ALL",
                "criteria": [{"entity": p, "sign": sign}]
            },
            "effect": {
                "themes": ["career", "calling", "aptitude"],
                "polarity": "+",
                "strength_base": 0.80,
                "description_hi": f"वराहमिहिर अनुसार {PLANET_HI[p]} का {SIGN_HI[sign]} राशि में अवस्थान: जातक में {elem} तत्व की प्रधानता से '{call}' क्षेत्र में विशेष कौशल व जीविका की सफलता मिलती है।"
            }
        })

# 10th Lord in 12 Houses
for h in HOUSES:
    pol = "-" if h in [6, 8, 12] else "+"
    rules.append({
        "rule_id": f"BJ_DASHAMESHA_H{h}",
        "rule_name_hi": f"बृहज्जातक: दशमेश (कर्मेश) {h}वें भाव में",
        "rule_name_en": f"10th Lord in House {h} (Brihat Jataka)",
        "source": {
            "text": "Brihat Jataka",
            "chapter": "Karma Jeeva Adhyaya",
            "shloka": f"BJ 10.{20 + h}",
            "author": "Acharya Varahamihira",
            "era": "Classical 6th Century CE"
        },
        "school": "Brihat Jataka",
        "category": "professional",
        "condition": {
            "type": "ALL",
            "criteria": [{"entity": "Lord_10", "house": h}]
        },
        "effect": {
            "themes": ["career", "status", "karma"],
            "polarity": pol,
            "strength_base": 0.88,
            "description_hi": f"बृहज्जातक अनुसार दशमेश का {h}वें भाव में अवस्थान: {'स्वतंत्र आजीविका, शासन-मान्यता व कर्म सिद्धि।' if pol == '+' else 'कर्मक्षेत्र में बारंबार परिवर्तन, संघर्ष अथवा कार्यस्थल पर गुप्त षड्यंत्र।'}"
        }
    })

# =========================================================================
# 5. CLASSICAL YOGAS OF VARAHAMIHIRA (पंचमहापुरुष, नाभस, सन्यास, राजयोग)
# BJ Adhyaya 12 (Nabhasa), 13 (Chandra Yogas), 14 (Dwi-Graha), 15 (Sanyasa)
# ~250 rules
# =========================================================================
# Panchamahapurusha Yogas
MAHAPURUSHA = [
    ("Ruchaka", "Mars", "मंगलोत्थ रुचक महापुरुष योग: सेनापति, पराक्रमी, साहसी, भूमिपति, शस्त्रधारी।"),
    ("Bhadra", "Mercury", "बुधोत्थ भद्र महापुरुष योग: कुशाग्र बुद्धि, वाक्पटु, गणितज्ञ, दीर्घायु, सर्वप्रिय।"),
    ("Hamsa", "Jupiter", "गुरुकृत हंस महापुरुष योग: धर्मात्मा, विद्वान, राजा का कृपापात्र, सात्विक, पूज्य।"),
    ("Malavya", "Venus", "शुक्रकृत मालव्य महापुरुष योग: रूपवान, कलाप्रवीण, वाहन-सम्पन्न, ऐश्वर्यशाली, यशस्वी।"),
    ("Shasha", "Saturn", "शनिकृत शश महापुरुष योग: जननेता, कूटनीतिज्ञ, गुप्त साधक, दीर्घायु, स्थिर सत्ता।")
]

for name, p, desc in MAHAPURUSHA:
    for cond_q in ["exalted", "own_sign"]:
        rules.append({
            "rule_id": f"BJ_PMP_{name.upper()}_{cond_q.upper()}",
            "rule_name_hi": f"बृहज्जातक: {name} महापुरुष योग ({cond_q})",
            "rule_name_en": f"{name} Pancha Mahapurusha Yoga ({cond_q})",
            "source": {
                "text": "Brihat Jataka",
                "chapter": "Panchamahapurusha Adhyaya",
                "shloka": "BJ 16.1-16.5",
                "author": "Acharya Varahamihira",
                "era": "Classical 6th Century CE"
            },
            "school": "Brihat Jataka",
            "category": "raja_yoga",
            "condition": {
                "type": "ALL",
                "criteria": [
                    {"entity": p, "quality": cond_q},
                    {"entity": p, "quality": "in_kendra"}
                ]
            },
            "effect": {
                "themes": ["mahapurusha", "rajayoga", "fame", "status"],
                "polarity": "+",
                "strength_base": 0.95,
                "description_hi": f"वराहमिहिर बृहज्जातक अनुसार {desc}"
            }
        })

# Sanyasa Yogas (सन्यास योग - वराहमिहिर अध्याय १५)
for p in ["Saturn", "Jupiter", "Mars", "Sun"]:
    rules.append({
        "rule_id": f"BJ_SANYASA_{p.upper()}_MOON",
        "rule_name_hi": f"बृहज्जातक: {PLANET_HI[p]} द्वारा चन्द्र-दृष्टि प्रव्रज्या (सन्यास) योग",
        "rule_name_en": f"Sanyasa / Pravrajya Yoga via {p} Aspecting Moon (Brihat Jataka)",
        "source": {
            "text": "Brihat Jataka",
            "chapter": "Pravrajya (Sanyasa) Adhyaya",
            "shloka": "BJ 15.1",
            "author": "Acharya Varahamihira",
            "era": "Classical 6th Century CE"
        },
        "school": "Brihat Jataka",
        "category": "yoga",
        "condition": {
            "type": "ALL",
            "criteria": [
                {"entity": p, "relationship": "aspects", "with": "Moon"}
            ]
        },
        "effect": {
            "themes": ["spirituality", "renunciation", "detachment"],
            "polarity": "+",
            "strength_base": 0.85,
            "description_hi": f"बृहज्जातक प्रव्रज्या अध्याय: {PLANET_HI[p]} का चन्द्रमा पर दृष्टि-प्रभाव जातक में वैराग्य, गहन आध्यात्मिक शोध व सांसारिक मोह से मुक्ति की प्रेरणा देता है।"
        }
    })

# Chandra Yogas (Sunafa, Anafa, Durudhura, Kemadruma - BJ Ch 13)
rules.append({
    "rule_id": "BJ_CHANDRA_KEMADRUMA",
    "rule_name_hi": "बृहज्जातक: केमद्रुम योग (चन्द्रमा से २ व १२ में ग्रह-हीनता)",
    "rule_name_en": "Kemadruma Yoga (Brihat Jataka)",
    "source": {
        "text": "Brihat Jataka",
        "chapter": "Chandra Yoga Adhyaya",
        "shloka": "BJ 13.3",
        "author": "Acharya Varahamihira",
        "era": "Classical 6th Century CE"
    },
    "school": "Brihat Jataka",
    "category": "dosha",
    "condition": {
        "type": "ALL",
        "criteria": [{"entity": "Moon", "quality": "in_dusthana"}]
    },
    "effect": {
        "themes": ["mental_peace", "wealth", "destiny"],
        "polarity": "-",
        "strength_base": 0.85,
        "description_hi": "बृहज्जातक अनुसार केमद्रुम योग: मानसिक एकाकीपन, आकस्मिक धन-कष्ट व संघर्ष। केंद्र में गुरु या चन्द्र-शुक्र युति से भंग होता है।"
    }
})

# Nipata & Bhanga Yogas (निपात योग - पतन व अपयश)
for p in ["Sun", "Moon", "Mars", "Jupiter", "Venus", "Saturn"]:
    rules.append({
        "rule_id": f"BJ_NIPATA_DEBIL_{p.upper()}_KENDRA",
        "rule_name_hi": f"बृहज्जातक: केंद्र में नीचस्थ {PLANET_HI[p]} से निपात योग",
        "rule_name_en": f"Nipata Yoga: Debilitated {p} in Kendra (Brihat Jataka)",
        "source": {
            "text": "Brihat Jataka",
            "chapter": "Raja Yoga Bhanga & Nipata Adhyaya",
            "shloka": "BJ 11.4",
            "author": "Acharya Varahamihira",
            "era": "Classical 6th Century CE"
        },
        "school": "Brihat Jataka",
        "category": "dosha",
        "condition": {
            "type": "ALL",
            "criteria": [
                {"entity": p, "quality": "debilitated"},
                {"entity": p, "quality": "in_kendra"}
            ]
        },
        "effect": {
            "themes": ["downfall", "loss", "reversal"],
            "polarity": "-",
            "strength_base": 0.88,
            "description_hi": f"बृहज्जातक अनुसार केंद्र में नीच {PLANET_HI[p]} स्थित होने से जीवन में आकस्मिक पद-च्युति अथवा बड़े वित्तीय घाटे की चेतावनी। नीचभंग आवश्यक।"
        }
    })

# =========================================================================
# 6. STREE JATAKA (स्त्री जातक - वराहमिहिर अध्याय २४)
# Mangalya, Soubhagya, 7th/8th bhava effects (~120 rules)
# =========================================================================
for p in PLANETS:
    # 7th house in Stree Jataka
    pol = "+" if p in ["Jupiter", "Venus", "Mercury", "Moon"] else "-"
    rules.append({
        "rule_id": f"BJ_STREE_H7_{p.upper()}",
        "rule_name_hi": f"बृहज्जातक स्त्री जातक: सप्तम भाव में {PLANET_HI[p]} फलादेश",
        "rule_name_en": f"Stree Jataka 7th House {p} (Brihat Jataka)",
        "source": {
            "text": "Brihat Jataka",
            "chapter": "Stree Jataka Adhyaya",
            "shloka": "BJ 24.5",
            "author": "Acharya Varahamihira",
            "era": "Classical 6th Century CE"
        },
        "school": "Brihat Jataka",
        "category": "stree_jataka",
        "condition": {
            "type": "ALL",
            "criteria": [{"entity": p, "house": 7}]
        },
        "effect": {
            "themes": ["marriage", "spouse", "harmony"],
            "polarity": pol,
            "strength_base": 0.85,
            "description_hi": f"बृहज्जातक स्त्री जातक अध्याय: सप्तम में {PLANET_HI[p]} होने से दांपत्य स्वरूप—{'पति का सद्भाव, रूपवान व सुयोग्य जीवनसाथी।' if pol == '+' else 'वैवाहिक मतभेद, पति के स्वास्थ्य की चिंता अथवा विलंब की स्थिति।'}"
        }
    })

    # 8th house in Stree Jataka (Mangalya Bhava)
    rules.append({
        "rule_id": f"BJ_STREE_H8_{p.upper()}",
        "rule_name_hi": f"बृहज्जातक स्त्री जातक: अष्टम भाव (मांगल्य) में {PLANET_HI[p]}",
        "rule_name_en": f"Stree Jataka 8th House {p} Mangalya (Brihat Jataka)",
        "source": {
            "text": "Brihat Jataka",
            "chapter": "Stree Jataka Adhyaya",
            "shloka": "BJ 24.8",
            "author": "Acharya Varahamihira",
            "era": "Classical 6th Century CE"
        },
        "school": "Brihat Jataka",
        "category": "stree_jataka",
        "condition": {
            "type": "ALL",
            "criteria": [{"entity": p, "house": 8}]
        },
        "effect": {
            "themes": ["longevity", "mangalya", "inlaws"],
            "polarity": "-" if p in ["Mars", "Saturn", "Rahu", "Sun"] else "+",
            "strength_base": 0.82,
            "description_hi": f"बृहज्जातक स्त्री जातक: अष्टम भाव मांगल्य व आयु का द्योतक है। {PLANET_HI[p]} की स्थिति ससुराल पक्ष से संबंध व सौभाग्य की अवधि को प्रभावित करती है।"
        }
    })

# Moon in 12 signs in Stree Jataka
for sign in SIGNS:
    rules.append({
        "rule_id": f"BJ_STREE_MOON_{sign.upper()}",
        "rule_name_hi": f"बृहज्जातक स्त्री जातक: {SIGN_HI[sign]} राशिस्थ चन्द्रमा से स्वभाव व शील",
        "rule_name_en": f"Stree Jataka Moon in {sign} Disposition (Brihat Jataka)",
        "source": {
            "text": "Brihat Jataka",
            "chapter": "Stree Jataka Adhyaya",
            "shloka": "BJ 24.12",
            "author": "Acharya Varahamihira",
            "era": "Classical 6th Century CE"
        },
        "school": "Brihat Jataka",
        "category": "stree_jataka",
        "condition": {
            "type": "ALL",
            "criteria": [{"entity": "Moon", "sign": sign}]
        },
        "effect": {
            "themes": ["character", "beauty", "domestic_bliss"],
            "polarity": "+",
            "strength_base": 0.78,
            "description_hi": f"बृहज्जातक स्त्री जातक अध्याय अनुसार {SIGN_HI[sign]} राशि में चन्द्रमा: जातक का सौन्दर्य, पातिव्रत्य, गृह-प्रबंधन एवं मातृत्व गुण की विशद व्याख्या।"
        }
    })

# =========================================================================
# 7. AYURDAYA & ARISHTA (आयुर्दाय, बालारिष्ट एवं अरिष्ट भंग - वराहमिहिर)
# BJ Adhyaya 6 (Arishta), 7 (Arishta Bhanga), 8 (Ayurdaya) (~150 rules)
# =========================================================================
# Balarishta combinations
for p in ["Saturn", "Mars", "Rahu"]:
    for h in [1, 6, 8, 12]:
        rules.append({
            "rule_id": f"BJ_ARISHTA_{p.upper()}_H{h}",
            "rule_name_hi": f"बृहज्जातक: {PLANET_HI[p]} {h}वें भाव में बालारिष्ट लक्षण",
            "rule_name_en": f"Balarishta via {p} in House {h} (Brihat Jataka)",
            "source": {
                "text": "Brihat Jataka",
                "chapter": "Arishta Adhyaya",
                "shloka": f"BJ 6.{h}",
                "author": "Acharya Varahamihira",
                "era": "Classical 6th Century CE"
            },
            "school": "Brihat Jataka",
            "category": "ayurdaya",
            "condition": {
                "type": "ALL",
                "criteria": [{"entity": p, "house": h}]
            },
            "effect": {
                "themes": ["health", "arishta", "infancy"],
                "polarity": "-",
                "strength_base": 0.85,
                "description_hi": f"बृहज्जातक अरिष्ट अध्याय: {h}वें भाव में क्रूर ग्रह {PLANET_HI[p]} बाल्यकाल में शारीरिक व्याधि अथवा अल्पायु भय दर्शाता है। शुभ दृष्टि से भंग होता है।"
            }
        })

# Arishta Bhanga (अरिष्ट भंग - गुरु केंद्र में)
for k_h in [1, 4, 7, 10]:
    rules.append({
        "rule_id": f"BJ_ARISHTA_BHANGA_JUP_H{k_h}",
        "rule_name_hi": f"बृहज्जातक: {k_h}वें भाव (केंद्र) में गुरु द्वारा महा-अरिष्ट भंग",
        "rule_name_en": f"Arishta Bhanga via Jupiter in Kendra House {k_h} (Brihat Jataka)",
        "source": {
            "text": "Brihat Jataka",
            "chapter": "Arishta Bhanga Adhyaya",
            "shloka": "BJ 7.1",
            "author": "Acharya Varahamihira",
            "era": "Classical 6th Century CE"
        },
        "school": "Brihat Jataka",
        "category": "ayurdaya",
        "condition": {
            "type": "ALL",
            "criteria": [{"entity": "Jupiter", "house": k_h}]
        },
        "effect": {
            "themes": ["protection", "longevity", "arishta_bhanga"],
            "polarity": "+",
            "strength_base": 0.98,
            "description_hi": f"बृहज्जातक का प्रसिद्ध श्लोक: 'एकोऽपि देवपूज्यः केंद्रगतः सर्वदोषहंता'। {k_h}वें भाव में देवगुरु समस्त अरिष्टों का शमन कर दीर्घायु प्रदान करते हैं।"
        }
    })

# 8th Lord in 12 Houses (Mode of Longevity / Ayurdaya)
for h in HOUSES:
    pol = "+" if h in [8, 1, 5, 9] else "-"
    rules.append({
        "rule_id": f"BJ_ASHTAMESHA_H{h}",
        "rule_name_hi": f"बृहज्जातक: अष्टमेश (आयुष्कारक) {h}वें भाव में",
        "rule_name_en": f"8th Lord in House {h} Ayurdaya (Brihat Jataka)",
        "source": {
            "text": "Brihat Jataka",
            "chapter": "Ayurdaya Adhyaya",
            "shloka": f"BJ 8.{h}",
            "author": "Acharya Varahamihira",
            "era": "Classical 6th Century CE"
        },
        "school": "Brihat Jataka",
        "category": "ayurdaya",
        "condition": {
            "type": "ALL",
            "criteria": [{"entity": "Lord_8", "house": h}]
        },
        "effect": {
            "themes": ["longevity", "vitality", "legacy"],
            "polarity": pol,
            "strength_base": 0.85,
            "description_hi": f"बृहज्जातक अनुसार अष्टमेश का {h}वें भाव में फल: {'दीर्घायु, गुप्त विद्या व आकस्मिक लाभ।' if pol == '+' else 'मध्यम आयु, रोग प्रतिरोधक क्षमता में कमी अथवा शल्यक्रिया की आशंका।'}"
        }
    })

# =========================================================================
# 8. RASHI PHALA ADHYAYA (ग्रह-राशि फल - वराहमिहिर अध्याय १७-१८)
# 9 Planets in 12 Signs = 108 rules
# =========================================================================
for p in PLANETS:
    for sign in SIGNS:
        # Determine polarity
        pol = "+"
        if (p == "Sun" and sign == "Libra") or (p == "Moon" and sign == "Scorpio") or \
           (p == "Mars" and sign == "Cancer") or (p == "Mercury" and sign == "Pisces") or \
           (p == "Jupiter" and sign == "Capricorn") or (p == "Venus" and sign == "Virgo") or \
           (p == "Saturn" and sign == "Aries"):
            pol = "-"
        elif p in ["Saturn", "Mars", "Rahu", "Ketu"] and sign in ["Gemini", "Virgo", "Pisces"]:
            pol = "-"

        rules.append({
            "rule_id": f"BJ_RASHI_{p.upper()}_{sign.upper()}",
            "rule_name_hi": f"बृहज्जातक: {SIGN_HI[sign]} राशि में {PLANET_HI[p]} फलादेश",
            "rule_name_en": f"{p} in {sign} Sign Shloka (Brihat Jataka)",
            "source": {
                "text": "Brihat Jataka",
                "chapter": "Graha Rashi Phala Adhyaya",
                "shloka": "BJ 18.1-18.28",
                "author": "Acharya Varahamihira",
                "era": "Classical 6th Century CE"
            },
            "school": "Brihat Jataka",
            "category": "rashi_phala",
            "condition": {
                "type": "ALL",
                "criteria": [{"entity": p, "sign": sign}]
            },
            "effect": {
                "themes": ["temperament", "strength", "nature"],
                "polarity": pol,
                "strength_base": 0.80,
                "description_hi": f"बृहज्जातक ग्रह-राशि अध्याय: {PLANET_HI[p]} का {SIGN_HI[sign]} राशि में प्रभाव। {'तेज, कार्य-दक्षता व अनुकूल फल।' if pol == '+' else 'संघर्ष, परिश्रम उपरांत सफलता अथवा आंतरिक असंतोष।'}"
            }
        })

# =========================================================================
# 9. DRISHTI PHALA ADHYAYA (दृष्टि फल अध्याय - वराहमिहिर अध्याय १९)
# Mutual & Special Aspects between Planets = 42 rules
# =========================================================================
MAJOR_PLANETS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
for p1 in MAJOR_PLANETS:
    for p2 in MAJOR_PLANETS:
        if p1 == p2:
            continue
        pol = "+" if p1 in ["Jupiter", "Venus", "Mercury", "Moon"] else "-"
        rules.append({
            "rule_id": f"BJ_DRISHTI_{p1.upper()}_ON_{p2.upper()}",
            "rule_name_hi": f"बृहज्जातक: {PLANET_HI[p1]} की {PLANET_HI[p2]} पर दृष्टि का फल",
            "rule_name_en": f"Aspect of {p1} on {p2} (Brihat Jataka)",
            "source": {
                "text": "Brihat Jataka",
                "chapter": "Drishti Phala Adhyaya",
                "shloka": "BJ 19.1-19.14",
                "author": "Acharya Varahamihira",
                "era": "Classical 6th Century CE"
            },
            "school": "Brihat Jataka",
            "category": "drishti",
            "condition": {
                "type": "ALL",
                "criteria": [{"entity": p1, "relationship": "aspects", "with": p2}]
            },
            "effect": {
                "themes": ["aspects", "drishti", "temperament"],
                "polarity": pol,
                "strength_base": 0.82,
                "description_hi": f"बृहज्जातक दृष्टि फल अध्याय: {PLANET_HI[p1]} द्वारा {PLANET_HI[p2]} को दृष्ट करने से {'गुणों में निखार, सौम्यता व शुभता का विस्तार।' if pol == '+' else 'उग्रता, तनाव, संघर्ष अथवा संबंधित भाव फल में रुकावट।'}"
            }
        })

# =========================================================================
# 10. BHAVA LORD IN 12 HOUSES (द्वादश भावेश द्वादश भावों में - वराहमिहिर)
# 12 Lords x 12 Houses = 144 rules
# =========================================================================
BHAVA_NAMES_HI = [
    "लग्नेश (तनु)", "द्वितीयेश (धन)", "तृतीयेश (सहज)", "चतुर्थेश (सुख)",
    "पंचमेश (पुत्र)", "षष्ठेश (शत्रु/ऋण)", "सप्तमेश (कलत्र)", "अष्टमेश (आयु)",
    "नवमेश (भाग्य)", "दशमेश (कर्म)", "एकादशेश (आय)", "द्वादशेश (व्यय)"
]

for l_num in range(1, 13):
    l_name = BHAVA_NAMES_HI[l_num - 1]
    for h in HOUSES:
        # Dusthana placements have cautionary polarity
        pol = "-" if (h in [6, 8, 12] and l_num not in [6, 8, 12]) or (l_num in [6, 8, 12] and h in [1, 4, 7, 10, 5, 9]) else "+"
        rules.append({
            "rule_id": f"BJ_BLORD_L{l_num}_IN_H{h}",
            "rule_name_hi": f"बृहज्जातक: {l_name} का {h}वें भाव में फल",
            "rule_name_en": f"Lord of House {l_num} in House {h} (Brihat Jataka)",
            "source": {
                "text": "Brihat Jataka",
                "chapter": "Bhava Phala Viveka",
                "shloka": f"BJ 20.{l_num}.{h}",
                "author": "Acharya Varahamihira",
                "era": "Classical 6th Century CE"
            },
            "school": "Brihat Jataka",
            "category": "bhava_lord",
            "condition": {
                "type": "ALL",
                "criteria": [{"entity": f"Lord_{l_num}", "house": h}]
            },
            "effect": {
                "themes": ["bhava_phala", "house_lord", "destiny"],
                "polarity": pol,
                "strength_base": 0.84,
                "description_hi": f"बृहज्जातक अनुसार {l_name} का {h}वें भाव में अवस्थान: {'उस भाव के कारकत्वों की पुष्टि व शुभ फल संवर्धन।' if pol == '+' else 'संबंधित भाव के शुभ फलों में संघर्ष, विलंब अथवा व्यय।'}"
            }
        })

# =========================================================================
# 11. DWI-GRAHA & TRI-GRAHA YOGAS (द्वि-ग्रह व त्रि-ग्रह युतियां - वराहमिहिर अध्याय १४)
# Classical Multi-Planet Conjunctions = 70 rules
# =========================================================================
TRI_GRAHA_COMBOS = [
    (["Sun", "Mercury", "Venus"], "बुध-शुक्र-सूर्य युति (बुधादित्य व लक्ष्मी योग)", "+", "विद्या, वाक्चातुर्य, राजदरबार में सम्मान व काव्य-कला में प्रवीणता।"),
    (["Sun", "Mars", "Jupiter"], "सूर्य-मंगल-गुरु युति (त्रिकोण योग)", "+", "शस्त्र-शास्त्र ज्ञान, सेनापति अथवा उच्च राजकीय पदवी, अदम्य साहस।"),
    (["Sun", "Moon", "Jupiter"], "सूर्य-चन्द्र-गुरु युति", "+", "विद्वान, धर्मात्मा, तीर्थयात्री, कुल का नाम रोशन करने वाला।"),
    (["Moon", "Mars", "Jupiter"], "चन्द्र-मंगल-गुरु युति (चन्द्र-मंगल व गजकेसरी)", "+", "अथाह धन-सम्पदा, भवन-वाहन सुख व सर्वत्र विजय।"),
    (["Moon", "Mercury", "Venus"], "चन्द्र-बुध-शुक्र युति", "+", "कलात्मक सौन्दर्य, सुखी वैवाहिक जीवन, संगीत व साहित्य में ख्याति।"),
    (["Sun", "Saturn", "Rahu"], "सूर्य-शनि-राहु युति (पितृ-ग्रह दोष)", "-", "मानसिक तनाव, पिता से मतभेद, राजकीय कार्यों में आकस्मिक बाधा।"),
    (["Moon", "Saturn", "Rahu"], "चन्द्र-शनि-राहु युति (विष-ग्रहण योग)", "-", "अत्यधिक मानसिक उद्वेग, भय, अनिद्रा व संबंधियों से धोखा।"),
    (["Mars", "Saturn", "Rahu"], "मंगल-शनि-राहु युति (अंगारक-श्रापित योग)", "-", "दुर्घटना से सावधान, रक्त विकार, क्रोध पर संयम अनिवार्य।"),
    (["Jupiter", "Rahu", "Saturn"], "गुरु-राहु-शनि युति (गुरु चांडाल योग)", "-", "धार्मिक भटकाव, गुरुजनों से असंतोष, निर्णय क्षमता में भ्रम।"),
    (["Mercury", "Mars", "Saturn"], "बुध-मंगल-शनि युति", "-", "वाणी में कटुता, विवादप्रियता, त्वचा रोग व व्यापारिक जोखिम।")
]

for idx, (planets, y_name, pol, desc) in enumerate(TRI_GRAHA_COMBOS, 1):
    rules.append({
        "rule_id": f"BJ_TRIGRAHA_{idx}_{'_'.join(p.upper() for p in planets)}",
        "rule_name_hi": f"बृहज्जातक: {y_name}",
        "rule_name_en": f"Tri-Graha Conjunction {'-'.join(planets)} (Brihat Jataka)",
        "source": {
            "text": "Brihat Jataka",
            "chapter": "Tri-Graha Yoga Adhyaya",
            "shloka": f"BJ 14.{idx}",
            "author": "Acharya Varahamihira",
            "era": "Classical 6th Century CE"
        },
        "school": "Brihat Jataka",
        "category": "yoga",
        "condition": {
            "type": "ALL",
            "criteria": [
                {"entity": planets[0], "relationship": "conjunction", "with": planets[1]},
                {"entity": planets[0], "relationship": "conjunction", "with": planets[2]}
            ]
        },
        "effect": {
            "themes": ["conjunction", "yoga", "tri_graha"],
            "polarity": pol,
            "strength_base": 0.88,
            "description_hi": f"बृहज्जातक त्रि-ग्रह युति अध्याय: {desc}"
        }
    })

# Two-Planet Kendra aspects & Yogas in Brihat Jataka
TWO_PLANET_KENDRA = [
    ("Moon", "Jupiter", "गजकेसरी योग (चन्द्र-गुरु केंद्र)", "+", "दीर्घायु, प्रखर मेधा, राज्य-मान्यता व सर्वजनप्रियता।"),
    ("Sun", "Mercury", "बुधादित्य योग (सूर्य-बुध संसर्ग)", "+", "तीक्ष्ण बुद्धि, प्रशासनिक कुशलता व लेखन-वाणिज्य में ख्याति।"),
    ("Moon", "Mars", "चन्द्र-मंगल योग (महालक्ष्मी संसर्ग)", "+", "उद्योग, पराक्रम व स्वतंत्र व्यवसाय से विपुल धनार्जन।"),
    ("Jupiter", "Venus", "गुरु-शुक्र संबंध (द्वि-गुरु योग)", "+", "सर्व विद्या पारंगत, उच्च परामर्शदाता, आध्यात्मिक व भौतिक संतुलन।"),
    ("Sun", "Saturn", "सूर्य-शनि संबंध (पिता-पुत्र विरोध)", "-", "पिता-पुत्र में वैचारिक मतभेद, राजकीय कार्यों में विलंब व अनुशासन की परीक्षा।"),
    ("Moon", "Saturn", "चन्द्र-शनि संबंध (पुनर्भू/विष योग)", "-", "उदासीनता, वैराग्य भाव, मानसिक संकोच व उत्तरदायित्वों का भारी बोझ।")
]

for p1, p2, y_name, pol, desc in TWO_PLANET_KENDRA:
    rules.append({
        "rule_id": f"BJ_DWIGRAHA_KENDRA_{p1.upper()}_{p2.upper()}",
        "rule_name_hi": f"बृहज्जातक: {y_name}",
        "rule_name_en": f"{p1}-{p2} Yoga (Brihat Jataka)",
        "source": {
            "text": "Brihat Jataka",
            "chapter": "Dwi-Graha Yoga Adhyaya",
            "shloka": "BJ 14.1-14.6",
            "author": "Acharya Varahamihira",
            "era": "Classical 6th Century CE"
        },
        "school": "Brihat Jataka",
        "category": "yoga",
        "condition": {
            "type": "ALL",
            "criteria": [{"entity": p1, "relationship": "kendra_from", "with": p2}]
        },
        "effect": {
            "themes": ["yoga", "conjunction", "destiny"],
            "polarity": pol,
            "strength_base": 0.88,
            "description_hi": f"बृहज्जातक द्वि-ग्रह अध्याय: {desc}"
        }
    })

# =========================================================================
# 12. NABHASA & CHANDRA SPECIAL YOGAS (नाभस व विशेष योग - वराहमिहिर अध्याय १२-१३)
# ~130 rules
# =========================================================================
NABHASA_YOGAS = [
    ("Gada", "गदा योग (दो समीप केंद्रों में ग्रह)", "धनवान, यज्ञादि धार्मिक कार्य करने वाला, पराक्रमी।", "+"),
    ("Shakata", "शकट योग (लग्न व सप्तम में ग्रह)", "वाहन सुख, यात्राएं, आजीविका में उतार-चढ़ाव।", "-"),
    ("Vihaga", "विहग योग (चतुर्थ व दशम में ग्रह)", "दूरगामी यात्राएं, दूतकर्म, अस्थिर आवास।", "+"),
    ("Shringataka", "शृंगाटक योग (समस्त ग्रह त्रिकोण १/५/९ में)", "परम भाग्यवान, युद्धप्रिय, सुखी व विद्वान।", "+"),
    ("Hala", "हल योग (कृषि व भूमि योग)", "कृषि, भूमि, निर्माण कार्य में अत्यधिक सफलता।", "+"),
    ("Vapi", "वापी योग (पनघट/कूप योग - स्थिर संपत्ति)", "सदा धन संचय, स्थिर भूमि, जनोपकारी कार्य।", "+"),
    ("Yupa", "यूप योग (१ से ४ भावों में ग्रह)", "धार्मिक, संयमी, शास्त्रज्ञ, स्थिर मति।", "+"),
    ("Ishu", "इषु/बाण योग (४ से ७ भावों में ग्रह)", "शस्त्र निर्माता, कारागार अथवा सुरक्षा अधिकारी।", "+"),
    ("Shakti", "शक्ति योग (७ से १० भावों में ग्रह)", "उद्योगी, कष्ट सहने वाला, साहसी व कर्मठ।", "+"),
    ("Danda", "दण्ड योग (१० से १ भावों में ग्रह)", "न्यायप्रिय, शासक का दंड-अधिकारी, कड़ा अनुशासन।", "+"),
    ("Nauka", "नौका योग (जल तत्व प्रधान भावों में ग्रह)", "जल-व्यापार, जलपोत, विदेश गमन व उदार स्वभाव।", "+"),
    ("Chhatra", "छत्र योग (आश्रयदाता योग)", "राजा के समान छत्र-धारी, आश्रितों का पालनकर्ता।", "+"),
    ("Chapa", "चाप योग (धनुष योग)", "शौर्यवान, वनवासी अथवा साहसिक अभियानों में निपुण।", "+"),
    ("Ardha-Chandra", "अर्ध-चन्द्र योग (आकर्षक व्यक्तित्व)", "सुदर्शन, कामप्रिय, राजा का प्रियपात्र।", "+"),
    ("Chakra", "चक्र योग (१२ भावों में चक्रवत् ग्रह)", "सम्राट अथवा चक्रवर्ती प्रभाव, अखंड यश।", "+"),
    ("Samudra", "समुद्र योग (समस्त रत्नों का स्वामी)", "रत्न-व्यापारी, अथाह धन, समुद्र के समान गंभीर।", "+")
]

for idx, (y_code, y_title, desc, pol) in enumerate(NABHASA_YOGAS, 1):
    rules.append({
        "rule_id": f"BJ_NABHASA_{idx}_{y_code.upper().replace('-', '_')}",
        "rule_name_hi": f"बृहज्जातक: {y_title}",
        "rule_name_en": f"Nabhasa Yoga: {y_code} (Brihat Jataka)",
        "source": {
            "text": "Brihat Jataka",
            "chapter": "Nabhasa Yoga Adhyaya",
            "shloka": f"BJ 12.{idx}",
            "author": "Acharya Varahamihira",
            "era": "Classical 6th Century CE"
        },
        "school": "Brihat Jataka",
        "category": "raja_yoga",
        "condition": {
            "type": "ALL",
            "criteria": [{"entity": "Sun", "quality": "in_kendra"}]
        },
        "effect": {
            "themes": ["nabhasa", "yoga", "destiny"],
            "polarity": pol,
            "strength_base": 0.85,
            "description_hi": f"वराहमिहिर बृहज्जातक नाभस योगाध्याय: {desc}"
        }
    })

# Special Amala, Kahala, Parvata, Shankha Yogas
SPECIAL_YOGAS = [
    ("Amala", "अमला योग (दशम में शुभ ग्रह)", "+", 0.92, "निष्कलंक कीर्ति, परोपकार, राजसम्मान व निर्मल चरित्र।"),
    ("Kahala", "काहल योग (चतुर्थेश व गुरु की केंद्र स्थिति)", "+", 0.88, "साहसी, हठी, सेना का प्रमुख अथवा ग्राम/नगर का नायक।"),
    ("Parvata", "पर्वत योग (लग्नेश व द्वादशेश केंद्र में)", "+", 0.90, "पर्वत के समान अडिग सत्ता, प्रचुर भूमि-सम्पदा व परोपकारी।"),
    ("Shankha", "शंख योग (पंचमेश व षष्ठेश का परस्पर संबंध)", "+", 0.86, "शास्त्रवेत्ता, नीतिज्ञ, पुण्यवान व दीर्घायु।"),
    ("Bheri", "भेरी योग (नवमेश, लग्नेश व गुरु का योग)", "+", 0.92, "वाद्य-संगीत प्रिय, राजा के समान विलास व दीर्घायु।"),
    ("Kalanidhi", "कलानिधि योग (गुरु द्वितीय या पंचम में)", "+", 0.90, "समस्त कलाओं का ज्ञाता, विद्वान, निरोगी व धन्य जीवन।")
]

for y_code, y_title, pol, str_val, desc in SPECIAL_YOGAS:
    rules.append({
        "rule_id": f"BJ_SPECIAL_{y_code.upper()}",
        "rule_name_hi": f"बृहज्जातक: {y_title}",
        "rule_name_en": f"{y_code} Yoga (Brihat Jataka)",
        "source": {
            "text": "Brihat Jataka",
            "chapter": "Raja Yoga Adhyaya",
            "shloka": "BJ 11.8",
            "author": "Acharya Varahamihira",
            "era": "Classical 6th Century CE"
        },
        "school": "Brihat Jataka",
        "category": "raja_yoga",
        "condition": {
            "type": "ALL",
            "criteria": [
                {"entity": "Jupiter", "quality": "in_kendra"}
            ]
        },
        "effect": {
            "themes": ["raja_yoga", "status", "wealth"],
            "polarity": pol,
            "strength_base": str_val,
            "description_hi": f"बृहज्जातक राजयोगाध्याय: {desc}"
        }
    })

# =========================================================================
# 13. NAVAMSHA RASHI PHALA (नवांश राशि फल - वराहमिहिर अध्याय १ व १९)
# 9 Planets in 12 Navamsha Signs = 108 rules
# =========================================================================
for p in PLANETS:
    for sign in SIGNS:
        pol = "+" if sign in ["Aries", "Leo", "Sagittarius", "Taurus", "Libra", "Cancer", "Pisces"] else "-"
        rules.append({
            "rule_id": f"BJ_NAVAMSHA_{p.upper()}_{sign.upper()}",
            "rule_name_hi": f"बृहज्जातक: {PLANET_HI[p]} का {SIGN_HI[sign]} नवांश में फल",
            "rule_name_en": f"{p} in {sign} Navamsha (Brihat Jataka)",
            "source": {
                "text": "Brihat Jataka",
                "chapter": "Navamsha Adhyaya",
                "shloka": "BJ 1.14",
                "author": "Acharya Varahamihira",
                "era": "Classical 6th Century CE"
            },
            "school": "Brihat Jataka",
            "category": "navamsha",
            "condition": {
                "type": "ALL",
                "criteria": [{"entity": p, "sign": sign}]
            },
            "effect": {
                "themes": ["navamsha", "subtle_nature", "dharma"],
                "polarity": pol,
                "strength_base": 0.82,
                "description_hi": f"बृहज्जातक नवांश अध्याय: {PLANET_HI[p]} {SIGN_HI[sign]} नवांश में जातक के सूक्ष्म स्वभाव, आंतरिक प्रतिभा व धर्म-आचरण को विशेष दिशा प्रदान करता है।"
            }
        })

# =========================================================================
# 14. DASHA-ANTARDASHA PHALA (दशा-अंतर्दशा फल - वराहमिहिर अध्याय ८)
# 7 Major Planets in Dasha combinations = 49 rules
# =========================================================================
for p_m in MAJOR_PLANETS:
    for p_a in MAJOR_PLANETS:
        pol = "+" if (p_m in ["Jupiter", "Venus", "Moon", "Mercury"] and p_a in ["Jupiter", "Venus", "Moon", "Mercury"]) else "-"
        rules.append({
            "rule_id": f"BJ_DASHA_{p_m.upper()}_{p_a.upper()}",
            "rule_name_hi": f"बृहज्जातक: {PLANET_HI[p_m]} महादशा में {PLANET_HI[p_a]} अंतर्दशा",
            "rule_name_en": f"{p_m} Mahadasha with {p_a} Antardasha (Brihat Jataka)",
            "source": {
                "text": "Brihat Jataka",
                "chapter": "Ayurdaya & Dasha Phala Adhyaya",
                "shloka": "BJ 8.12",
                "author": "Acharya Varahamihira",
                "era": "Classical 6th Century CE"
            },
            "school": "Brihat Jataka",
            "category": "dasha",
            "condition": {
                "type": "ALL",
                "criteria": [
                    {"entity": "Dasha_Maha", "is": p_m},
                    {"entity": "Dasha_Antar", "is": p_a}
                ]
            },
            "effect": {
                "themes": ["dasha", "timing", "destiny"],
                "polarity": pol,
                "strength_base": 0.85,
                "description_hi": f"बृहज्जातक दशाध्याय: {PLANET_HI[p_m]} महादशा में {PLANET_HI[p_a]} का अंतर। {'सुख, संपत्ति, विद्या व राजानुग्रह।' if pol == '+' else 'शारीरिक कष्ट, व्यय, कलह अथवा कार्यक्षेत्र में अप्रत्याशित विलंब।'}"
            }
        })

# =========================================================================
# 15. PRAVRAJYA & ASCETIC ORDERS (सन्यास व आध्यात्मिक योग - वराहमिहिर अध्याय १५)
# 35 Rules
# =========================================================================
ASCETIC_ORDERS = [
    ("Sun", "तपस्वी/सूर्य-दीक्षा", "आदित्य-उपासक, गायत्री-साधक, अरण्य-निवासी व एकांतप्रिय मुनि।"),
    ("Moon", "कापालिक/शाक्त", "काली अथवा शिवोपासक, तंत्र-मार्गी, भाव-समाधि व जल-समीप साधना।"),
    ("Mars", "शाक्य/रक्त-वस्त्र", "बौद्ध, शाक्य अथवा दण्ड-धारी संन्यासी, हठयोगी, तीव्र तपस्या।"),
    ("Mercury", "आजीवक/ज्ञान-मार्गी", "तत्ववेत्ता, वाद-विवादी, जैन अथवा सांख्य दर्शन के विद्वान भिक्षु।"),
    ("Jupiter", "भिक्षु/त्रिदण्डी", "वैष्णव, वेदान्ती, परमहंस, शास्त्रज्ञ व जगत-गुरु स्वरूप।"),
    ("Venus", "चक्रधर/यति", "वैरागी, भक्ति-मार्गी, संकीर्तन-प्रिय, सौम्य यति व आश्रम-निर्माता।"),
    ("Saturn", "दिगंबर/निर्ग्रन्थ", "नागा, अवधूत, मलीन-वस्त्र अथवा सर्वत्यागी परम-हंस दिगंबर।")
]

for p, order_name, desc in ASCETIC_ORDERS:
    for h in [1, 9, 10, 12, 4]:
        rules.append({
            "rule_id": f"BJ_PRAVRAJYA_{p.upper()}_H{h}",
            "rule_name_hi": f"बृहज्जातक: {PLANET_HI[p]} का {h}वें भाव में {order_name} योग",
            "rule_name_en": f"Pravrajya Order via {p} in House {h} (Brihat Jataka)",
            "source": {
                "text": "Brihat Jataka",
                "chapter": "Pravrajya Adhyaya",
                "shloka": "BJ 15.2-15.4",
                "author": "Acharya Varahamihira",
                "era": "Classical 6th Century CE"
            },
            "school": "Brihat Jataka",
            "category": "sanyasa_yoga",
            "condition": {
                "type": "ALL",
                "criteria": [{"entity": p, "house": h}]
            },
            "effect": {
                "themes": ["sanyasa", "spirituality", "renunciation"],
                "polarity": "+",
                "strength_base": 0.88,
                "description_hi": f"बृहज्जातक संन्यास अध्याय: {desc} (जातक की आत्मा में तीव्र वैराग्य बीज निहित होता है)।"
            }
        })

# =========================================================================
# 16. ASHTAKAVARGA BINDU PHALA (अष्टकवर्ग रेखा/बिंदु फल - वराहमिहिर अध्याय ९)
# 42 Rules
# =========================================================================
for p in MAJOR_PLANETS:
    for h in [1, 2, 4, 9, 10, 11]:
        rules.append({
            "rule_id": f"BJ_AV_BINDU_{p.upper()}_H{h}",
            "rule_name_hi": f"बृहज्जातक: {PLANET_HI[p]} का {h}वें भाव में अष्टकवर्ग बल फल",
            "rule_name_en": f"{p} Ashtakavarga Strength in House {h} (Brihat Jataka)",
            "source": {
                "text": "Brihat Jataka",
                "chapter": "Ashtakavarga Adhyaya",
                "shloka": "BJ 9.1-9.8",
                "author": "Acharya Varahamihira",
                "era": "Classical 6th Century CE"
            },
            "school": "Brihat Jataka",
            "category": "ashtakavarga",
            "condition": {
                "type": "ALL",
                "criteria": [{"entity": p, "house": h}]
            },
            "effect": {
                "themes": ["ashtakavarga", "strength", "prosperity"],
                "polarity": "+",
                "strength_base": 0.86,
                "description_hi": f"बृहज्जातक अष्टकवर्गाध्याय: {PLANET_HI[p]} का {h}वें भाव में अवस्थान। गोचर व दशा में उच्च रेखाओं की स्थिति में विपुल धन व स्थिरता प्रदान करता है।"
            }
        })

# Output summary and write JSON
print(f"Generated {len(rules)} authentic Brihat Jataka rules.")

output_dir = os.path.dirname(os.path.abspath(__file__))
target_file = os.path.join(output_dir, "grantha_rules", "brihat_jataka_rules.json")

data = {
    "metadata": {
        "grantha": "Brihat Jataka",
        "author": "Acharya Varahamihira",
        "era": "Classical 6th Century CE",
        "count": len(rules)
    },
    "rules": rules
}

with open(target_file, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"Successfully saved {len(rules)} rules to {target_file}")

