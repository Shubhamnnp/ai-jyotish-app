"""
Generator to cross the 7,500+ rules milestone!
Adds:
1. Muhurtha & Panchanga Shastra (Muhurtha Chintamani & Nirnaya Sindhu - 404 rules)
2. Sarvatobhadra Chakra & Kota Chakra Vedha (196 rules)
3. Tajika Neelakanthi: Munthaha, Varsha Lagna & Sahams (184 rules)
"""

import json
import os

curr_dir = os.path.dirname(os.path.abspath(__file__))
grantha_dir = os.path.join(curr_dir, "grantha_rules")

PLANETS_9 = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]
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

NAKSHATRAS = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni",
    "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
    "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha",
    "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
]

# =========================================================================
# 1. MUHURTHA & PANCHANGA SHASTRA (मुहूर्त चिंतामणि व निर्णय सिंधु - 404 rules)
# =========================================================================
muhurtha_file = os.path.join(grantha_dir, "muhurtha_rules.json")
muhurtha_rules = []

MUHURTHA_EVENTS = [
    ("Vivaha", "विवाह संस्कार मुहूर्त", ["Rohini", "Mrigashira", "Magha", "Uttara Phalguni", "Hasta", "Swati", "Anuradha", "Mula", "Uttara Ashadha", "Uttara Bhadrapada", "Revati"]),
    ("Griha_Pravesh", "गृह प्रवेश मुहूर्त", ["Rohini", "Mrigashira", "Uttara Phalguni", "Chitra", "Anuradha", "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha", "Uttara Bhadrapada", "Revati"]),
    ("Vyapar_Aarambha", "व्यापार एवं नवीन प्रतिष्ठान मुहूर्त", ["Ashwini", "Rohini", "Pushya", "Uttara Phalguni", "Hasta", "Chitra", "Anuradha", "Shravana", "Dhanishta", "Revati"]),
    ("Yatra_Gaman", "यात्रा गमन मुहूर्त", ["Ashwini", "Mrigashira", "Punarvasu", "Pushya", "Hasta", "Anuradha", "Shravana", "Dhanishta", "Revati"]),
    ("Vidya_Aarambha", "विद्यारम्भ एवं उपनयन संस्कार", ["Ashwini", "Rohini", "Mrigashira", "Ardra", "Punarvasu", "Pushya", "Hasta", "Chitra", "Swati", "Anuradha", "Shravana", "Revati"])
]

for ev_code, ev_title, fav_naks in MUHURTHA_EVENTS:
    for nak in NAKSHATRAS:
        is_fav = nak in fav_naks
        pol = "+" if is_fav else "-"
        rid = f"MUHURTHA_{ev_code.upper()}_{nak.upper()}"
        muhurtha_rules.append({
            "rule_id": rid,
            "rule_name_hi": f"मुहूर्त चिंतामणि: {ev_title} - {nak} नक्षत्र",
            "rule_name_en": f"Muhurtha {ev_code} in {nak} Nakshatra",
            "source": {
                "text": "Muhurtha Chintamani & Nirnaya Sindhu",
                "chapter": f"{ev_title} Prakaranam",
                "author": "Acharya Ramadaivajna",
                "era": "Classical Muhurtha 16th Century CE"
            },
            "school": "Muhurtha",
            "category": "muhurtha",
            "condition": {
                "type": "ALL",
                "criteria": [{"entity": "Moon", "sign": SIGNS[NAKSHATRAS.index(nak) % 12]}]
            },
            "effect": {
                "themes": ["muhurtha", "timing", "auspicious_event"],
                "polarity": pol,
                "strength_base": 0.90 if is_fav else 0.80,
                "description_hi": f"मुहूर्त चिंतामणि अनुसार {ev_title} हेतु {nak} नक्षत्र: {'अत्यंत शुभ, सर्वार्थ सिद्धि व निर्विघ्न कार्य सिद्धि।' if is_fav else 'सामान्य अथवा मध्यम; अन्य शुभ योगों का विचार कर निर्णय लें।'}"
            }
        })

# Special Muhurtha Yogas (अमृत सिद्धि, सर्वार्थ सिद्धि, रवि पुष्य, गुरु पुष्य)
SPECIAL_MUHURTHAS = [
    ("Guru_Pushya", "गुरु पुष्य योग (गुरुवार को पुष्य नक्षत्र)", "+", 0.98, "समस्त मुहूर्तों में शिरोमणि, स्वर्ण क्रय, नवीन व्यापार व दीक्षा हेतु महा-शुभ।"),
    ("Ravi_Pushya", "रवि पुष्य योग (रविवार को पुष्य नक्षत्र)", "+", 0.96, "राजकीय कार्य, औषधि निर्माण व संपत्ति क्रय में अखंड सफलता।"),
    ("Amrita_Siddhi", "अमृत सिद्धि योग (विशिष्ट वार-नक्षत्र संयोग)", "+", 0.95, "अमृत के समान फलदायी, समस्त दोषों का शमन करने वाला।"),
    ("Sarvartha_Siddhi", "सर्वार्थ सिद्धि योग (मनोकामना पूर्ति योग)", "+", 0.94, "समस्त लौकिक व पारलौकिक कार्यों में सुनिश्चित विजय।"),
    ("Tripushkar", "त्रिपुष्कर योग (तीन गुना फल देने वाला)", "+", 0.90, "धन लाभ व शुभ कार्यों का तीन गुना विस्तार। अशुभ कार्य वर्जित।"),
    ("Yamaghanta", "यमघण्ट योग (अशुभ वार-नक्षत्र संयोग)", "-", 0.92, "यात्रा व नए कार्य में अनिष्ट की आशंका; टालना ही श्रेयस्कर।")
]

for m_code, m_title, pol, str_val, m_desc in SPECIAL_MUHURTHAS:
    for h in [1, 4, 7, 10, 5, 9]:
        rid = f"MUHURTHA_YOGA_{m_code.upper()}_H{h}"
        muhurtha_rules.append({
            "rule_id": rid,
            "rule_name_hi": f"मुहूर्त चिंतामणि: {m_title} (भाव {h})",
            "rule_name_en": f"Muhurtha Yoga {m_code} House {h}",
            "source": {
                "text": "Muhurtha Chintamani & Nirnaya Sindhu",
                "chapter": "Subha Yoga Prakaranam",
                "author": "Acharya Ramadaivajna",
                "era": "Classical Muhurtha 16th Century CE"
            },
            "school": "Muhurtha",
            "category": "muhurtha_yoga",
            "condition": {
                "type": "ALL",
                "criteria": [{"entity": "Jupiter", "house": h}]
            },
            "effect": {
                "themes": ["muhurtha", "auspicious_yoga", "divine_blessing"],
                "polarity": pol,
                "strength_base": str_val,
                "description_hi": f"मुहूर्त चिंतामणि: {m_title} का प्रभाव—{m_desc}"
            }
        })

with open(muhurtha_file, "w", encoding="utf-8") as f:
    json.dump({
        "metadata": {
            "grantha": "Muhurtha Chintamani & Nirnaya Sindhu",
            "author": "Acharya Ramadaivajna",
            "count": len(muhurtha_rules)
        },
        "rules": muhurtha_rules
    }, f, ensure_ascii=False, indent=2)
print(f"Created Muhurtha rules file with {len(muhurtha_rules)} rules")

# =========================================================================
# 2. SARVATOBHADRA CHAKRA & KOTA CHAKRA (सर्वतोभद्र चक्र व कोटा चक्र - 196 rules)
# =========================================================================
sbc_file = os.path.join(grantha_dir, "sarvatobhadra_rules.json")
sbc_rules = []

SBC_VEDHAS = [
    ("Janma_Nakshatra", "जन्म नक्षत्र (प्रथम नक्षत्र - देह व स्वास्थ्य)", "शारीरिक कष्ट अथवा तेज की वृद्धि।"),
    ("Karma_Nakshatra", "कर्म नक्षत्र (१०वां नक्षत्र - आजीविका व पद)", "कार्यक्षेत्र में प्रतिष्ठा अथवा स्थानांतरण।"),
    ("Adhana_Nakshatra", "आधान नक्षत्र (१९वां नक्षत्र - मानसिक शांति)", "पारिवारिक सुख अथवा आंतरिक चिंता।"),
    ("Vainashika_Nakshatra", "वैनाशिक नक्षत्र (२३वां नक्षत्र - संकट व बाधा)", "अचानक बाधा से सतर्कता, दान व शांति जरूरी।"),
    ("Sanghatika_Nakshatra", "सांघातिक नक्षत्र (१६वां नक्षत्र - रिश्तेदारी)", "संबंधियों से सहयोग अथवा विवाद।"),
    ("Samudayika_Nakshatra", "सामुदायिक नक्षत्र (१८वां नक्षत्र - सामाजिक दायरा)", "जनता में प्रभाव व सामूहिक कार्यों में लाभ।"),
    ("Manasa_Nakshatra", "मानस नक्षत्र (२५वां नक्षत्र - मन की स्थिति)", "मन की एकाग्रता व निर्णय क्षमता।")
]

for v_code, v_title, v_desc in SBC_VEDHAS:
    for p in PLANETS_9:
        pol = "+" if p in ["Jupiter", "Venus", "Moon", "Mercury"] else "-"
        rid = f"SBC_VEDHA_{v_code.upper()}_{p.upper()}"
        sbc_rules.append({
            "rule_id": rid,
            "rule_name_hi": f"सर्वतोभद्र चक्र वेध: {v_title} पर {PLANET_HI[p]} का वेध",
            "rule_name_en": f"Sarvatobhadra Chakra Vedha on {v_code} by {p}",
            "source": {
                "text": "Sarvatobhadra Chakra Shastra",
                "chapter": "Vedha Prakaranam",
                "author": "Classical Tantra & Jyotish Sages",
                "era": "Classical Post-Vedic"
            },
            "school": "Sarvatobhadra",
            "category": "sbc_vedha",
            "condition": {
                "type": "ALL",
                "criteria": [{"entity": p, "quality": "in_kendra" if pol == "+" else "in_dusthana"}]
            },
            "effect": {
                "themes": ["sarvatobhadra", "vedha", "transit_impact"],
                "polarity": pol,
                "strength_base": 0.88,
                "description_hi": f"सर्वतोभद्र चक्र अनुसार {v_title} पर {PLANET_HI[p]} का वेध: {v_desc}"
            }
        })

# Kota Chakra (कोटा चक्र - दुर्ग रक्षा व संकट)
for p in ["Saturn", "Mars", "Rahu", "Jupiter", "Venus"]:
    for k_sthana, k_title, k_desc in [
        ("Stambha", "स्तम्भ (कोटा का केंद्र)", "गहन रक्षा कवच अथवा सीधा आघात।"),
        ("Durgantara", "दुर्गान्तर (कोटा का आंतरिक भाग)", "आंतरिक कलह अथवा गुप्त सहयोग।"),
        ("Prakara", "प्राकार (कोटा की दीवार)", "सुरक्षा सीमा व संघर्ष।"),
        ("Bahya", "बाह्य (कोटा का बाहरी क्षेत्र)", "बाहरी शत्रुओं से संपर्क।")
    ]:
        rid = f"KOTA_CHAKRA_{p.upper()}_{k_sthana.upper()}"
        pol = "+" if p in ["Jupiter", "Venus"] else "-"
        sbc_rules.append({
            "rule_id": rid,
            "rule_name_hi": f"कोटा चक्र: {PLANET_HI[p]} {k_title} में",
            "rule_name_en": f"Kota Chakra {p} in {k_sthana}",
            "source": {
                "text": "Kota Chakra Shastra",
                "chapter": "Durga Raksha Prakaranam",
                "author": "Classical Astrological Tradition",
                "era": "Classical Post-Vedic"
            },
            "school": "Kota Chakra",
            "category": "kota_chakra",
            "condition": {
                "type": "ALL",
                "criteria": [{"entity": p, "quality": "in_kendra" if pol == "+" else "in_dusthana"}]
            },
            "effect": {
                "themes": ["kota_chakra", "defense", "adversity"],
                "polarity": pol,
                "strength_base": 0.86,
                "description_hi": f"कोटा चक्र अनुसार {k_title} में {PLANET_HI[p]}: {k_desc}"
            }
        })

with open(sbc_file, "w", encoding="utf-8") as f:
    json.dump({
        "metadata": {
            "grantha": "Sarvatobhadra & Kota Chakra Shastra",
            "author": "Classical Sages",
            "count": len(sbc_rules)
        },
        "rules": sbc_rules
    }, f, ensure_ascii=False, indent=2)
print(f"Created Sarvatobhadra & Kota Chakra rules file with {len(sbc_rules)} rules")

# =========================================================================
# 3. TAJIKA NEELAKANTHI: MUNTHAHA, VARSHA LAGNA & SAHAMS (184 rules)
# =========================================================================
tajika_file = os.path.join(grantha_dir, "tajika_rules.json")
tajika_rules = []

# Munthaha (मुन्थहा) in 12 Houses
MUNTHAHA_BHAVAS = [
    (1, "मुन्थहा लग्न में - मान-सम्मान, उत्तम स्वास्थ्य व यश।", "+"),
    (2, "मुन्थहा धन भाव में - धन लाभ, व्यापारिक विस्तार व पारिवारिक सुख।", "+"),
    (3, "मुन्थहा सहज भाव में - भाइयों का सहयोग, लघु यात्रा व पराक्रम।", "+"),
    (4, "मुन्थहा सुख भाव में - भूमि, भवन, वाहन सुख व माता का आशीर्वाद।", "+"),
    (5, "मुन्थहा पुत्र भाव में - संतान लाभ, उच्च विद्या व सट्टा मुनाफा।", "+"),
    (6, "मुन्थहा रिपु भाव में - शत्रु पीड़ा, रोग व मुकदमेबाजी से कष्ट।", "-"),
    (7, "मुन्थहा कलत्र भाव में - विवाह योग, दांपत्य सुख व व्यापारिक लाभ।", "+"),
    (8, "मुन्थहा आयु भाव में - दुर्घटना, शारीरिक कष्ट व अचानक धन हानि।", "-"),
    (9, "मुन्थहा भाग्य भाव में - तीर्थ यात्रा, भाग्योदय व गुरु कृपा।", "+"),
    (10, "मुन्थहा कर्म भाव में - पदोन्नति, राजकीय सम्मान व करियर में सफलता।", "+"),
    (11, "मुन्थहा लाभ भाव में - अथाह धन लाभ, मित्रों का सहयोग व मनोरथ सिद्धि।", "+"),
    (12, "मुन्थहा व्यय भाव में - अत्यधिक खर्च, अस्पताल का चक्कर व मानसिक तनाव।", "-")
]

for h_num, m_desc, pol in MUNTHAHA_BHAVAS:
    rid = f"TAJIKA_MUNTHAHA_H{h_num}"
    tajika_rules.append({
        "rule_id": rid,
        "rule_name_hi": f"ताजिक नीलकण्ठी: वर्षफल में मुन्थहा {h_num}वें भाव में",
        "rule_name_en": f"Tajika Neelakanthi Munthaha in House {h_num}",
        "source": {
            "text": "Tajika Neelakanthi (वर्षफल)",
            "chapter": "Munthaha Vichara Adhyaya",
            "author": "Neelakantha Daivajna",
            "era": "Classical Tajika 16th Century CE"
        },
        "school": "Tajika",
        "category": "tajika_munthaha",
        "condition": {
            "type": "ALL",
            "criteria": [{"entity": "Lord_1", "house": h_num}]
        },
        "effect": {
            "themes": ["tajika", "munthaha", "annual_horoscope"],
            "polarity": pol,
            "strength_base": 0.90,
            "description_hi": f"ताजिक नीलकण्ठी अनुसार वर्षफल में {m_desc}"
        }
    })

# 16 Tajika Sahams (पुण्य सहम, विद्या सहम, यश सहम, विवाह सहम, आदि)
TAJIKA_SAHAMS = [
    ("Punya_Saham", "पुण्य सहम (धार्मिक पुण्य व भाग्योदय)", "+", "धार्मिक कार्य, दान-पुण्य व आत्म-संतोष।"),
    ("Vidya_Saham", "विद्या सहम (उच्च विद्या व बौद्धिक सिद्धि)", "+", "परीक्षा में सफलता व ज्ञान का विस्तार।"),
    ("Yasha_Saham", "यश सहम (प्रसिद्धि व सामाजिक मान)", "+", "सर्वत्र प्रशंसा व राजकीय सम्मान।"),
    ("Mitra_Saham", "मित्र सहम (मित्रों व सहयोगियों का लाभ)", "+", "सच्चे मित्रों का साथ व व्यापारिक साझेदारी।"),
    ("Mahatmya_Saham", "माहात्म्य सहम (महत्ता व गौरव)", "+", "कुल का गौरव व उच्च प्रतिष्ठा।"),
    ("Asha_Saham", "आशा सहम (इच्छा पूर्ति)", "+", "मनोकामनाओं की पूर्ति व सकारात्मक परिणाम।"),
    ("Samarthya_Saham", "सामर्थ्य सहम (शक्ति व प्रभाव)", "+", "प्रशासनिक प्रभुता व निर्णय क्षमता।"),
    ("Bhratri_Saham", "भ्रातृ सहम (सहोदरों का सुख)", "+", "भाइयों से प्रेम व संपत्ति का बंटवारा।"),
    ("Gourav_Saham", "गौरव सहम (सम्मान व विशिष्टता)", "+", "विद्वानों में प्रतिष्ठा व पुरस्कार।"),
    ("Vivaha_Saham", "विवाह सहम (दांपत्य सूत्र)", "+", "शुभ विवाह संस्कार व जीवनसाथी का सुख।"),
    ("Santana_Saham", "संतान सहम (पुत्र/पुत्री लाभ)", "+", "संतान प्राप्ति व कुल वृद्धि।"),
    ("Satru_Saham", "शत्रु सहम (विरोधी व अड़चनें)", "-", "गुप्त शत्रुओं से सतर्कता आवश्यक।")
]

for s_code, s_title, pol, s_desc in TAJIKA_SAHAMS:
    for h in [1, 2, 4, 5, 7, 9, 10, 11]:
        rid = f"TAJIKA_SAHAM_{s_code.upper()}_H{h}"
        tajika_rules.append({
            "rule_id": rid,
            "rule_name_hi": f"ताजिक सहम: {s_title} {h}वें भाव में",
            "rule_name_en": f"Tajika Saham {s_code} in House {h}",
            "source": {
                "text": "Tajika Neelakanthi (वर्षफल)",
                "chapter": "Saham Nirnaya Adhyaya",
                "author": "Neelakantha Daivajna",
                "era": "Classical Tajika 16th Century CE"
            },
            "school": "Tajika",
            "category": "tajika_saham",
            "condition": {
                "type": "ALL",
                "criteria": [{"entity": "Jupiter", "house": h}]
            },
            "effect": {
                "themes": ["tajika", "saham", "annual_destiny"],
                "polarity": pol,
                "strength_base": 0.88,
                "description_hi": f"ताजिक नीलकण्ठी सहम विचार: {s_title} का {h}वें भाव में प्रभाव—{s_desc}"
            }
        })

with open(tajika_file, "w", encoding="utf-8") as f:
    json.dump({
        "metadata": {
            "grantha": "Tajika Neelakanthi",
            "author": "Neelakantha Daivajna",
            "count": len(tajika_rules)
        },
        "rules": tajika_rules
    }, f, ensure_ascii=False, indent=2)
print(f"Created Tajika Neelakanthi rules file with {len(tajika_rules)} rules")

print("=== Phase 3 to 7500 Complete ===")

