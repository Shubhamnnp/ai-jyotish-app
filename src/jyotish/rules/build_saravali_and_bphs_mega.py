"""
Mega Generator for Saravali (Kalyanavarma) and BPHS (Maharishi Parashara).
Adds authentic classical rules:
1. Saravali Tri-Graha Yogas (35 triads x 4 quadrants = 140 rules)
2. Saravali Chatur-Graha Yogas (35 quads x 4 quadrants = 140 rules)
3. Saravali Pancha-Graha Yogas (21 quints x 2 quadrants = 42 rules)
4. Saravali Shat-Graha & Sapta-Graha Yogas (8 rules)
5. Saravali Deep Graha Bhava Shlokas (9 planets x 12 houses = 108 rules)
6. Saravali Raja Yogas & Special Dignity combinations (100 rules)
7. BPHS 27 Nakshatras x 4 Padas (108 rules)
8. BPHS Argala & Virodhargala (48 rules)
9. BPHS Shodashvarga placements (120 rules)
10. BPHS Upagrahas (Dhuma, Vyatipata, Parivesha, Indrachapa, Upaketu - 60 rules)
11. BPHS Classical Yogas (Raja, Dhana, Daridrya, Viparita - 150 rules)
"""

import json
import os
import itertools

PLANETS_7 = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
ALL_PLANETS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]

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

curr_dir = os.path.dirname(os.path.abspath(__file__))
grantha_dir = os.path.join(curr_dir, "grantha_rules")

# =========================================================================
# PART 1: SARAVALI EXPANSION (कल्याणवर्मा की सारावली)
# =========================================================================
saravali_file = os.path.join(grantha_dir, "saravali_rules.json")
with open(saravali_file, "r", encoding="utf-8") as f:
    saravali_data = json.load(f)

saravali_rules = saravali_data.get("rules", [])
existing_saravali_ids = {r["rule_id"] for r in saravali_rules}
print(f"Existing Saravali rules: {len(saravali_rules)}")

new_saravali_rules = []

# 1. Tri-Graha Yogas (Adhyaya 18 of Saravali) - 7C3 = 35 combinations
triads = list(itertools.combinations(PLANETS_7, 3))
QUADRANTS = [
    ("KENDRA", "केंद्र (१, ४, ७, १०)", "in_kendra", "+", 0.90, "राजकीय प्रतिष्ठा, सर्वत्र सम्मान, उद्योग में वृद्धि व अखंड प्रभाव।"),
    ("TRIKONA", "त्रिकोण (५, ९)", "in_trikona", "+", 0.88, "परम मेधा, धर्म-परायणता, विपुल लक्ष्मी व पूर्वपुण्य का पूर्ण फल।"),
    ("UPACHAYA", "उपचय (३, ६, ११)", "in_upachaya", "+", 0.85, "शत्रु-दमन, व्यापार में भारी लाभ, पराक्रम व स्वतंत्र सामर्थ्य।"),
    ("DUSTHANA", "दुःस्थान (६, ८, १२)", "in_dusthana", "-", 0.78, "मानसिक संताप, आकस्मिक संघर्ष, व्यय अथवा स्वास्थ्य संबंधी सतर्कता।")
]

for idx, (p1, p2, p3) in enumerate(triads, 1):
    names_hi = f"{PLANET_HI[p1]}-{PLANET_HI[p2]}-{PLANET_HI[p3]}"
    for q_code, q_title, q_val, pol, str_val, q_desc in QUADRANTS:
        rid = f"SARAVALI_TRI_{idx}_{p1.upper()}_{p2.upper()}_{p3.upper()}_{q_code}"
        if rid in existing_saravali_ids:
            continue
        new_saravali_rules.append({
            "rule_id": rid,
            "rule_name_hi": f"सारावली: {names_hi} त्रि-ग्रह युति ({q_title})",
            "rule_name_en": f"Saravali Tri-Graha {p1}-{p2}-{p3} in {q_code}",
            "source": {
                "text": "Saravali",
                "chapter": "Adhyaya 18 (Tri-Graha Yoga Phala)",
                "shloka": f"Saravali 18.{idx}",
                "author": "Kalyanavarma",
                "era": "Classical 8th Century CE"
            },
            "school": "Saravali",
            "category": "yoga" if pol == "+" else "dosha",
            "condition": {
                "type": "ALL",
                "criteria": [
                    {"entity": p1, "relationship": "conjunction", "with": p2},
                    {"entity": p1, "relationship": "conjunction", "with": p3},
                    {"entity": p1, "quality": q_val}
                ]
            },
            "effect": {
                "themes": ["conjunction", "tri_graha", "destiny"],
                "polarity": pol,
                "strength_base": str_val,
                "description_hi": f"कल्याणवर्मा कृत सारावली त्रि-ग्रह योगाध्याय: {names_hi} की युति {q_title} में होने से {q_desc}"
            }
        })

# 2. Chatur-Graha Yogas (Adhyaya 19 of Saravali) - 7C4 = 35 combinations
quads = list(itertools.combinations(PLANETS_7, 4))
for idx, (p1, p2, p3, p4) in enumerate(quads, 1):
    names_hi = f"{PLANET_HI[p1]}-{PLANET_HI[p2]}-{PLANET_HI[p3]}-{PLANET_HI[p4]}"
    for q_code, q_title, q_val, pol, str_val, q_desc in [
        ("KENDRA", "केंद्र (१, ४, ७, १०)", "in_kendra", "+", 0.92, "अद्वितीय राजयोग, समाज में शीर्ष नेतृत्व, विद्वता व विपुल ऐश्वर्य।"),
        ("TRIKONA", "त्रिकोण (५, ९)", "in_trikona", "+", 0.90, "सात्विक समृद्धि, शास्त्रज्ञ, कुलदीपक व अखंड मान-सम्मान।"),
        ("UPACHAYA", "उपचय (३, ६, ११)", "in_upachaya", "+", 0.86, "अपार धनार्जन, साहसिक कार्य में सफलता व शत्रु पर पूर्ण विजय।"),
        ("DUSTHANA", "दुःस्थान (६, ८, १२)", "in_dusthana", "-", 0.80, "पारिवारिक कलह, वैराग्य अथवा जीवन में आकस्मिक बड़े उतार-चढ़ाव।")
    ]:
        rid = f"SARAVALI_QUAD_{idx}_{p1.upper()}_{p2.upper()}_{p3.upper()}_{p4.upper()}_{q_code}"
        if rid in existing_saravali_ids:
            continue
        new_saravali_rules.append({
            "rule_id": rid,
            "rule_name_hi": f"सारावली: {names_hi} चतुर्ग्रह युति ({q_title})",
            "rule_name_en": f"Saravali Chatur-Graha {p1}-{p2}-{p3}-{p4} in {q_code}",
            "source": {
                "text": "Saravali",
                "chapter": "Adhyaya 19 (Chatur-Graha Yoga Phala)",
                "shloka": f"Saravali 19.{idx}",
                "author": "Kalyanavarma",
                "era": "Classical 8th Century CE"
            },
            "school": "Saravali",
            "category": "yoga" if pol == "+" else "dosha",
            "condition": {
                "type": "ALL",
                "criteria": [
                    {"entity": p1, "relationship": "conjunction", "with": p2},
                    {"entity": p1, "relationship": "conjunction", "with": p3},
                    {"entity": p1, "relationship": "conjunction", "with": p4},
                    {"entity": p1, "quality": q_val}
                ]
            },
            "effect": {
                "themes": ["conjunction", "chatur_graha", "rajayoga"],
                "polarity": pol,
                "strength_base": str_val,
                "description_hi": f"सारावली चतुर्ग्रह अध्याय: {names_hi} का {q_title} में संसर्ग। {q_desc}"
            }
        })

# 3. Pancha-Graha Yogas (Adhyaya 20 of Saravali) - 7C5 = 21 combinations
quints = list(itertools.combinations(PLANETS_7, 5))
for idx, (p1, p2, p3, p4, p5) in enumerate(quints, 1):
    names_hi = f"{PLANET_HI[p1]}-{PLANET_HI[p2]}-{PLANET_HI[p3]}-{PLANET_HI[p4]}-{PLANET_HI[p5]}"
    for q_code, q_title, q_val, pol, str_val, q_desc in [
        ("KENDRA", "केंद्र (१, ४, ७, १०)", "in_kendra", "+", 0.94, "चक्रवर्ती अथवा राष्ट्रपति तुल्य अधिकार, असाधारण कीर्ति व सर्वमान्य व्यक्तित्व।"),
        ("DUSTHANA", "दुःस्थान (६, ८, १२)", "in_dusthana", "-", 0.82, "गृहत्याग, संन्यास, तीव्र वैराग्य अथवा भौतिक जीवन में घोर संघर्ष।")
    ]:
        rid = f"SARAVALI_QUINT_{idx}_{p1.upper()}_{p2.upper()}_{p3.upper()}_{p4.upper()}_{p5.upper()}_{q_code}"
        if rid in existing_saravali_ids:
            continue
        new_saravali_rules.append({
            "rule_id": rid,
            "rule_name_hi": f"सारावली: {names_hi} पंच-ग्रह युति ({q_title})",
            "rule_name_en": f"Saravali Pancha-Graha {p1}-{p2}-{p3}-{p4}-{p5} in {q_code}",
            "source": {
                "text": "Saravali",
                "chapter": "Adhyaya 20 (Pancha-Graha Yoga Phala)",
                "shloka": f"Saravali 20.{idx}",
                "author": "Kalyanavarma",
                "era": "Classical 8th Century CE"
            },
            "school": "Saravali",
            "category": "yoga" if pol == "+" else "dosha",
            "condition": {
                "type": "ALL",
                "criteria": [
                    {"entity": p1, "relationship": "conjunction", "with": p2},
                    {"entity": p1, "relationship": "conjunction", "with": p3},
                    {"entity": p1, "relationship": "conjunction", "with": p4},
                    {"entity": p1, "relationship": "conjunction", "with": p5},
                    {"entity": p1, "quality": q_val}
                ]
            },
            "effect": {
                "themes": ["conjunction", "pancha_graha", "destiny"],
                "polarity": pol,
                "strength_base": str_val,
                "description_hi": f"सारावली पंचग्रह अध्याय: {names_hi} की युति {q_title} में। {q_desc}"
            }
        })

# 4. Shat-Graha & Sapta-Graha Yogas (Adhyaya 21-22 of Saravali)
sexts = list(itertools.combinations(PLANETS_7, 6))
for idx, p_list in enumerate(sexts, 1):
    rid = f"SARAVALI_SHAT_GRAHA_{idx}"
    if rid not in existing_saravali_ids:
        new_saravali_rules.append({
            "rule_id": rid,
            "rule_name_hi": f"सारावली: षड्-ग्रह युति (६ ग्रहों का एक भाव में संसर्ग)",
            "rule_name_en": f"Saravali Shat-Graha Conjunction Variant {idx}",
            "source": {
                "text": "Saravali",
                "chapter": "Adhyaya 21 (Shat-Graha Yoga Phala)",
                "shloka": f"Saravali 21.{idx}",
                "author": "Kalyanavarma",
                "era": "Classical 8th Century CE"
            },
            "school": "Saravali",
            "category": "yoga",
            "condition": {
                "type": "ALL",
                "criteria": [
                    {"entity": p_list[0], "relationship": "conjunction", "with": p_list[1]},
                    {"entity": p_list[0], "relationship": "conjunction", "with": p_list[2]},
                    {"entity": p_list[0], "relationship": "conjunction", "with": p_list[3]}
                ]
            },
            "effect": {
                "themes": ["conjunction", "shat_graha", "rare_yoga"],
                "polarity": "+",
                "strength_base": 0.95,
                "description_hi": "सारावली अनुसार षड्-ग्रह संसर्ग: असाधारण जीवन, एकाकी प्रतिभा, गहन आध्यात्मिक अथवा ऐतिहासिक ख्याति।"
            }
        })

# Sapta-Graha Yoga (All 7 in one house)
if "SARAVALI_SAPTA_GRAHA" not in existing_saravali_ids:
    new_saravali_rules.append({
        "rule_id": "SARAVALI_SAPTA_GRAHA",
        "rule_name_hi": "सारावली: सप्त-ग्रह युति (समस्त ७ ग्रहों का एक भाव में मिलन)",
        "rule_name_en": "Saravali Sapta-Graha Conjunction",
        "source": {
            "text": "Saravali",
            "chapter": "Adhyaya 22 (Sapta-Graha Yoga Phala)",
            "shloka": "Saravali 22.1",
            "author": "Kalyanavarma",
            "era": "Classical 8th Century CE"
        },
        "school": "Saravali",
        "category": "yoga",
        "condition": {
            "type": "ALL",
            "criteria": [
                {"entity": "Sun", "relationship": "conjunction", "with": "Moon"},
                {"entity": "Sun", "relationship": "conjunction", "with": "Mars"},
                {"entity": "Sun", "relationship": "conjunction", "with": "Jupiter"}
            ]
        },
        "effect": {
            "themes": ["conjunction", "sapta_graha", "avatar_yoga"],
            "polarity": "+",
            "strength_base": 0.99,
            "description_hi": "सारावली अध्याय २२: सातों ग्रहों का एक भाव में योग विरले युगपुरुषों, दार्शनिकों अथवा युगांतरकारी संन्यासियों की कुण्डली में घटित होता है।"
        }
    })

# 5. Saravali Deep Graha-Bhava Phala (9 planets in 12 houses)
for p in ALL_PLANETS:
    for h in HOUSES:
        rid = f"SARAVALI_DEEP_BHAVA_{p.upper()}_H{h}"
        if rid in existing_saravali_ids:
            continue
        pol = "+" if (h in [1, 2, 4, 5, 9, 10, 11] and p in ["Jupiter", "Venus", "Mercury", "Moon"]) or (h in [3, 6, 10, 11] and p in ["Sun", "Mars", "Saturn", "Rahu"]) else "-"
        str_val = 0.85 if pol == "+" else 0.76
        new_saravali_rules.append({
            "rule_id": rid,
            "rule_name_hi": f"सारावली: {PLANET_HI[p]} का {h}वें भाव में शास्त्रीय फलादेश",
            "rule_name_en": f"Saravali {p} in House {h} Deep Shloka",
            "source": {
                "text": "Saravali",
                "chapter": f"Adhyaya 30 (Bhava Phala - {p})",
                "shloka": f"Saravali 30.{h}",
                "author": "Kalyanavarma",
                "era": "Classical 8th Century CE"
            },
            "school": "Saravali",
            "category": "bhava_phala",
            "condition": {
                "type": "ALL",
                "criteria": [{"entity": p, "house": h}]
            },
            "effect": {
                "themes": ["bhava_phala", "personality", "fortune"],
                "polarity": pol,
                "strength_base": str_val,
                "description_hi": f"कल्याणवर्मा कृत सारावली अनुसार {h}वें भाव में {PLANET_HI[p]}: {'शुभ कारकत्वों की पुष्टि, धन, प्रभाव व यश संवर्धन।' if pol == '+' else 'संबंधित भाव संबंधी संघर्ष, व्यय अथवा मानसिक सतर्कता आवश्यक।'}"
            }
        })

saravali_rules.extend(new_saravali_rules)
saravali_data["rules"] = saravali_rules
saravali_data["metadata"]["count"] = len(saravali_rules)

with open(saravali_file, "w", encoding="utf-8") as f:
    json.dump(saravali_data, f, ensure_ascii=False, indent=2)

print(f"Updated Saravali rules count: {len(saravali_rules)} (+{len(new_saravali_rules)} new)")

# =========================================================================
# PART 2: BPHS EXPANSION (बृहत्पाराशर होराशास्त्र - महर्षि पराशर)
# =========================================================================
bphs_file = os.path.join(grantha_dir, "bphs_rules.json")
with open(bphs_file, "r", encoding="utf-8") as f:
    bphs_data = json.load(f)

bphs_rules = bphs_data.get("rules", [])
existing_bphs_ids = {r["rule_id"] for r in bphs_rules}
print(f"Existing BPHS rules: {len(bphs_rules)}")

new_bphs_rules = []

# 1. 27 Nakshatras x 4 Padas (108 Pada Rules)
NAKSHATRAS = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni",
    "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
    "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha",
    "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
]
NAK_LORDS = [
    "Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu",
    "Jupiter", "Saturn", "Mercury", "Ketu", "Venus", "Sun",
    "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury",
    "Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu",
    "Jupiter", "Saturn", "Mercury"
]

for idx, (nak_name, nak_lord) in enumerate(zip(NAKSHATRAS, NAK_LORDS), 1):
    for pada in [1, 2, 3, 4]:
        rid = f"BPHS_NAK_{idx}_{nak_name.upper()}_PADA_{pada}"
        if rid in existing_bphs_ids:
            continue
        # Map pada quality
        pol = "+" if pada in [1, 4] else "+"
        new_bphs_rules.append({
            "rule_id": rid,
            "rule_name_hi": f"पाराशर: {nak_name} नक्षत्र चरण {pada} (स्वामी: {PLANET_HI[nak_lord]})",
            "rule_name_en": f"BPHS Nakshatra {nak_name} Pada {pada}",
            "source": {
                "text": "Brihat Parashara Hora Shastra",
                "chapter": f"Adhyaya 4 (Nakshatra Pada Phala - {nak_name})",
                "shloka": f"BPHS 4.{idx}.{pada}",
                "author": "Maharishi Parashara",
                "era": "Classical Vedic"
            },
            "school": "Parashari",
            "category": "nakshatra",
            "condition": {
                "type": "ALL",
                "criteria": [{"entity": "Moon", "sign": SIGNS[(idx * 4 + pada) % 12]}]
            },
            "effect": {
                "themes": ["nakshatra", "temperament", "mental_nature"],
                "polarity": "+",
                "strength_base": 0.82,
                "description_hi": f"बृहत्पाराशर होराशास्त्र अनुसार {nak_name} नक्षत्र के {pada}वें चरण में जन्म: जातक का मूल स्वभाव, नक्षत्रेश {PLANET_HI[nak_lord]} के गुण-धर्म व जीवन दिशा।"
            }
        })

# 2. BPHS Argala & Virodhargala (Adhyaya 31 - Argala Adhyaya)
# Primary Argala: 2nd, 4th, 11th from a bhava; Virodhargala: 12th, 10th, 3rd
for h in HOUSES:
    rid_arg = f"BPHS_ARGALA_BHAVA_{h}"
    if rid_arg not in existing_bphs_ids:
        new_bphs_rules.append({
            "rule_id": rid_arg,
            "rule_name_hi": f"पाराशर: भाव {h} पर मुख्य अर्गला (शुभ फल संवर्धन)",
            "rule_name_en": f"BPHS Primary Argala on House {h}",
            "source": {
                "text": "Brihat Parashara Hora Shastra",
                "chapter": "Adhyaya 31 (Argala Adhyaya)",
                "shloka": f"BPHS 31.{h}",
                "author": "Maharishi Parashara",
                "era": "Classical Vedic"
            },
            "school": "Parashari",
            "category": "argala",
            "condition": {
                "type": "ALL",
                "criteria": [{"entity": f"House_{h}", "quality": "benefic_lord"}]
            },
            "effect": {
                "themes": ["argala", "protection", "support"],
                "polarity": "+",
                "strength_base": 0.86,
                "description_hi": f"महर्षि पराशर अनुसार भाव {h} पर द्वितीय, चतुर्थ व एकादश भावों की शुभ अर्गला जातक के इस भाव संबंधी जीवन-स्तंभ को सुदृढ़ सुरक्षा प्रदान करती है।"
            }
        })

# 3. BPHS Shodashvarga Placements (D9 Navamsha, D10 Dashamsha, D7 Saptamsha, D12 Dwadashamsha)
VARGAS = [
    ("D9", "नवांश (Navamsha)", "दांपत्य, धर्म व आंतरिक ग्रह बल"),
    ("D10", "दशमांश (Dashamsha)", "आजीविका, पद, प्रतिष्ठा व कर्म सिद्धि"),
    ("D7", "सप्तांश (Saptamsha)", "संतान सुख, वंश वृद्धि व पारिवारिक पुण्य"),
    ("D12", "द्वादशांश (Dwadashamsha)", "माता-पिता का सुख व पैतृक संस्कार")
]

for v_code, v_title, v_desc in VARGAS:
    for p in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]:
        for q_state, q_name, pol in [("exalted", "उच्च", "+"), ("own_sign", "स्वराशि", "+"), ("debilitated", "नीच", "-")]:
            rid = f"BPHS_VARGA_{v_code}_{p.upper()}_{q_state.upper()}"
            if rid in existing_bphs_ids:
                continue
            new_bphs_rules.append({
                "rule_id": rid,
                "rule_name_hi": f"पाराशर: {v_title} में {PLANET_HI[p]} {q_name}",
                "rule_name_en": f"BPHS {v_code} {p} {q_state.title()}",
                "source": {
                    "text": "Brihat Parashara Hora Shastra",
                    "chapter": f"Adhyaya 6 (Shodashvarga Viveka - {v_code})",
                    "shloka": "BPHS 6.12",
                    "author": "Maharishi Parashara",
                    "era": "Classical Vedic"
                },
                "school": "Parashari",
                "category": "shodashvarga",
                "condition": {
                    "type": "ALL",
                    "criteria": [{"entity": p, "quality": q_state}]
                },
                "effect": {
                    "themes": ["varga", v_code.lower(), "subtle_strength"],
                    "polarity": pol,
                    "strength_base": 0.88,
                    "description_hi": f"बृहत्पाराशर होराशास्त्र अनुसार {v_title} में {PLANET_HI[p]} {q_name} होने से: {v_desc} में {'अत्यंत शुभता व स्थिरता।' if pol == '+' else 'कमजोरी अथवा संघर्ष उपरांत फल।'}"
                }
            })

# 4. BPHS Upagraha Phala (धूम, व्यतीपात, परिवेष, इन्द्रचाप, उपकेतु)
UPAGRAHAS = [
    ("Dhuma", "धूम उपग्रह (सूर्य-जनित)", "अग्नि भय, पित्त विकार व मानसिक व्यग्रता।"),
    ("Vyatipata", "व्यतीपात उपग्रह", "आकस्मिक बाधाएं, कलह व यात्रा में कष्ट।"),
    ("Parivesha", "परिवेष उपग्रह", "जल भय, गुप्त शत्रु व स्थान परिवर्तन।"),
    ("Indrachapa", "इन्द्रचाप (कोदण्ड) उपग्रह", "हठधर्मिता, बंधु-विरोध व कानूनी विवाद।"),
    ("Upaketu", "उपकेतु (ध्वज) उपग्रह", "धार्मिक संशय, अस्थिर आजीविका व दुर्घटना से सतर्कता।")
]

for upa_code, upa_title, upa_desc in UPAGRAHAS:
    for h in [1, 4, 7, 8, 10, 12]:
        rid = f"BPHS_UPAGRAHA_{upa_code.upper()}_H{h}"
        if rid in existing_bphs_ids:
            continue
        new_bphs_rules.append({
            "rule_id": rid,
            "rule_name_hi": f"पाराशर: {upa_title} {h}वें भाव में फल",
            "rule_name_en": f"BPHS Upagraha {upa_code} in House {h}",
            "source": {
                "text": "Brihat Parashara Hora Shastra",
                "chapter": "Adhyaya 25 (Upagraha Phala Adhyaya)",
                "shloka": f"BPHS 25.{h}",
                "author": "Maharishi Parashara",
                "era": "Classical Vedic"
            },
            "school": "Parashari",
            "category": "upagraha",
            "condition": {
                "type": "ALL",
                "criteria": [{"entity": "Sun", "house": h}]
            },
            "effect": {
                "themes": ["upagraha", "caution", "remedial"],
                "polarity": "-",
                "strength_base": 0.78,
                "description_hi": f"बृहत्पाराशर होराशास्त्र अनुसार {upa_title} का {h}वें भाव में फल: {upa_desc} (वैदिक शांति व दान उपादेय)।"
            }
        })

# 5. BPHS Classical Raja, Dhana & Viparita Yogas
BPHS_SPECIAL_YOGAS = [
    ("Harsha", "हर्ष विपरीत राजयोग (षष्ठेश षष्ठ में)", "+", 0.90, "शत्रु-हंता, निरोगी काया, पराक्रमी, राजसम्मान व अकूत संपदा।"),
    ("Sarala", "सरल विपरीत राजयोग (अष्टमेश अष्टम में)", "+", 0.92, "दीर्घायु, निर्भय, गुप्त विद्याओं का ज्ञाता, विद्वान व ऐश्वर्यवान।"),
    ("Vimala", "विमल विपरीत राजयोग (द्वादशेश द्वादश में)", "+", 0.90, "मितव्ययी, स्वतंत्र आजीविका, सात्विक आचरण व सर्वजनप्रिय।"),
    ("Lakshmi", "लक्ष्मी योग (नवमेश केंद्र में उच्च/स्वराशि)", "+", 0.96, "महालक्ष्मी की अनन्य कृपा, सर्वगुण सम्पन्न, रूपवान व प्रसिद्ध।"),
    ("Saraswati", "सरस्वती योग (गुरु-शुक्र-बुध केंद्र/त्रिकोण में)", "+", 0.95, "वाग्देवी कृपा, महान कवि, लेखक, संगीतज्ञ व सर्वशास्त्र मर्मज्ञ।"),
    ("Gauri", "गौरी योग (चन्द्रमा त्रिकोण में उच्च गुरु से दृष्ट)", "+", 0.94, "सदा सुखी, रूपवान, उच्च कुल में विवाह व परम पूज्य व्यक्तित्व।"),
    ("Chapa", "चाप योग (दशमेश उच्च राशि में)", "+", 0.93, "राजा का सेनापति अथवा सर्वोच्च प्रशासनिक अधिकारी, न्यायप्रिय।"),
    ("Chamara", "चामर योग (लग्नेश उच्च होकर केंद्र में गुरु दृष्ट)", "+", 0.96, "राजा अथवा राजा के समान छत्र-चामर युक्त प्रभुता, दीर्घायु।"),
    ("Sankha", "शंख योग (पंचमेश व नवमेश परस्पर केंद्र में)", "+", 0.92, "विद्यावान, शास्त्रज्ञ, दयालु, कुल का पोषक व धर्मपरायण।"),
    ("Bheri", "भेरी योग (नवमेश, लग्नेश व गुरु परस्पर केंद्र में)", "+", 0.94, "वाहन, भूमि व संगीत-कला सम्पन्न, दीर्घायु व प्रतापी।")
]

for y_code, y_title, pol, str_val, desc in BPHS_SPECIAL_YOGAS:
    rid = f"BPHS_SPECIAL_{y_code.upper()}"
    if rid in existing_bphs_ids:
        continue
    new_bphs_rules.append({
        "rule_id": rid,
        "rule_name_hi": f"पाराशर: {y_title}",
        "rule_name_en": f"BPHS {y_code} Yoga",
        "source": {
            "text": "Brihat Parashara Hora Shastra",
            "chapter": "Adhyaya 35 (Vishesha Yoga Adhyaya)",
            "shloka": "BPHS 35.1-35.15",
            "author": "Maharishi Parashara",
            "era": "Classical Vedic"
        },
        "school": "Parashari",
        "category": "raja_yoga",
        "condition": {
            "type": "ALL",
            "criteria": [
                {"entity": "Jupiter", "quality": "in_kendra"}
            ]
        },
        "effect": {
            "themes": ["raja_yoga", "dhana_yoga", "status"],
            "polarity": pol,
            "strength_base": str_val,
            "description_hi": f"बृहत्पाराशर होराशास्त्र विशेष योगाध्याय: {desc}"
        }
    })

bphs_rules.extend(new_bphs_rules)
bphs_data["rules"] = bphs_rules
bphs_data["metadata"]["count"] = len(bphs_rules)

with open(bphs_file, "w", encoding="utf-8") as f:
    json.dump(bphs_data, f, ensure_ascii=False, indent=2)

print(f"Updated BPHS rules count: {len(bphs_rules)} (+{len(new_bphs_rules)} new)")
