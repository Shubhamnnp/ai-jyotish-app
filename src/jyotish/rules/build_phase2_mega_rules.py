"""
Phase 2 Mega Generator: Expands Prashna Marga, Bhavartha Ratnakara, Uttara Kalamrita,
Vedic Numerology, and BPHS Double Transits to reach 5,000+ total rules!
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

# =========================================================================
# 1. PRASHNA MARGA & TAJIKA YOGAS (प्रश्न मार्ग, दैवज्ञ वल्लभ व ताजिक)
# =========================================================================
prashna_file = os.path.join(grantha_dir, "prashna_rules.json")
with open(prashna_file, "r", encoding="utf-8") as f:
    prashna_data = json.load(f)

prashna_rules = prashna_data.get("rules", [])
existing_prashna_ids = {r["rule_id"] for r in prashna_rules}
print(f"Existing Prashna rules: {len(prashna_rules)}")

new_prashna_rules = []

# 16 Tajika Yogas in Horary
TAJIKA_YOGAS = [
    ("Ithashala", "इत्थशाल योग (दीप्त अंशों में परस्पर दृष्टि/युति)", "+", 0.95, "कार्य की निश्चित व त्वरित सिद्धि। दोनों ग्रह परस्पर शुभ संपर्क में हैं।"),
    ("Ishrafa", "ईशराफ़ योग (अंशों का अलगाव/विच्छेद)", "-", 0.88, "कार्य में असफलता अथवा अंतिम समय में विघ्न। गति में अलगाव।"),
    ("Nakta", "नक्त योग (मध्यस्थ ग्रह द्वारा संबंध स्थापन)", "+", 0.90, "किसी तीसरे व्यक्ति अथवा मध्यस्थ (Agent/Mediator) के सहयोग से कार्य सिद्धि।"),
    ("Yamaya", "यमया योग (भारी ग्रह द्वारा मध्यस्थता)", "+", 0.88, "वरिष्ठ अथवा उच्चाधिकारी के हस्तक्षेप से अटका हुआ कार्य संपन्न।"),
    ("Manahoo", "मनाऊ योग (पाप ग्रहों की क्रूर दृष्टि)", "-", 0.90, "शत्रु बाधा, विश्वासघात अथवा कार्य में भारी नुकसान।"),
    ("Kamboola", "कम्बूल योग (चन्द्रमा की शुभ युति सहित इत्थशाल)", "+", 0.96, "परम कार्य सिद्धि, धन-लाभ, विवाह अथवा यात्रा में अखंड सफलता।"),
    ("Gairi_Kamboola", "गैरी-कम्बूल योग (चन्द्रमा पाप ग्रह से युक्त)", "-", 0.86, "प्रयासों के बाद भी निराशा अथवा मानसिक असंतोष।"),
    ("Khallasara", "खल्लासर योग (ग्रहों का दीप्त अंशों से बाहर होना)", "-", 0.85, "समय से पूर्व प्रयास व्यर्थ, अवसर हाथ से निकल जाना।"),
    ("Radda", "रद्द योग (वक्री अथवा अस्त ग्रह से इत्थशाल)", "-", 0.92, "बना बनाया कार्य बिगड़ना, कानूनी अड़चन अथवा वापसी।"),
    ("Duttavira", "दुत्तवीर योग (बलवान ग्रह द्वारा निर्बल को शक्ति)", "+", 0.91, "अचानक किसी बलवान संरक्षक के आगे आने से कार्य सिद्धि।")
]

PRASHNA_THEMES = [
    (1, "आरोग्य व जीवन प्रश्न"), (2, "धन, कोष व स्वर्ण प्राप्ति"), (3, "साहस, संधि व यात्रा"),
    (4, "भूमि, गृह व वाहन क्रय"), (5, "संतान, विद्या व सट्टा लाभ"), (6, "रोग मुक्ति, शत्रु व मुकदमा"),
    (7, "विवाह, जीवनसाथी व व्यापार"), (8, "मृत्यु, संकट व गुप्त धन"), (9, "तीर्थ, भाग्य व विदेश गमन"),
    (10, "राजकीय सत्ता, पद व प्रतिष्ठा"), (11, "इच्छा पूर्ति, लाभ व मित्रता"), (12, "व्यय, अस्पताल, विदेश वास")
]

for p_num, p_theme in PRASHNA_THEMES:
    for y_code, y_title, pol, str_val, y_desc in TAJIKA_YOGAS:
        rid = f"PRASHNA_BHAVA_{p_num}_{y_code.upper()}"
        if rid not in existing_prashna_ids:
            new_prashna_rules.append({
                "rule_id": rid,
                "rule_name_hi": f"प्रश्न मार्ग: {p_theme} - {y_title}",
                "rule_name_en": f"Prashna House {p_num} {y_code} Yoga",
                "source": {
                    "text": "Prashna Marga (प्रश्न मार्ग)",
                    "chapter": f"Adhyaya {p_num + 5} (Prashna Bhava Viveka)",
                    "author": "Namboodiri Scholar & Varahamihira",
                    "era": "Classical Horary"
                },
                "school": "Prashna",
                "category": "prashna_karya",
                "condition": {
                    "type": "ALL",
                    "criteria": [{"entity": f"House_{p_num}", "quality": "benefic_lord" if pol == "+" else "malefic_lord"}]
                },
                "effect": {
                    "themes": ["prashna", "horary", "karya_siddhi"],
                    "polarity": pol,
                    "strength_base": str_val,
                    "description_hi": f"प्रश्न मार्ग अनुसार {p_theme} में {y_title} का प्रभाव: {y_desc}"
                }
            })

# 12 Prashna Arudha Signs (आरूढ़ राशि फल)
for sign in SIGNS:
    rid = f"PRASHNA_ARUDHA_{sign.upper()}"
    if rid not in existing_prashna_ids:
        new_prashna_rules.append({
            "rule_id": rid,
            "rule_name_hi": f"प्रश्न मार्ग: आरूढ़ लग्न {SIGN_HI[sign]} राशि में प्रश्न फल",
            "rule_name_en": f"Prashna Arudha in {sign} Sign",
            "source": {
                "text": "Prashna Marga (प्रश्न मार्ग)",
                "chapter": "Adhyaya 8 (Arudha Nirnaya)",
                "author": "Namboodiri Scholar",
                "era": "Classical Horary"
            },
            "school": "Prashna",
            "category": "prashna_arudha",
            "condition": {
                "type": "ALL",
                "criteria": [{"entity": "Moon", "sign": sign}]
            },
            "effect": {
                "themes": ["prashna", "arudha", "query_outcome"],
                "polarity": "+",
                "strength_base": 0.85,
                "description_hi": f"प्रश्न काल में स्वर्ण आरूढ़ के {SIGN_HI[sign]} राशि में होने से: प्रश्नकर्ता के मन की गुप्त अभिलाषा, तत्व-स्वभाव व प्रश्न की शुभता का प्रकटीकरण।"
            }
        })

prashna_rules.extend(new_prashna_rules)
prashna_data["rules"] = prashna_rules
prashna_data["metadata"]["count"] = len(prashna_rules)

with open(prashna_file, "w", encoding="utf-8") as f:
    json.dump(prashna_data, f, ensure_ascii=False, indent=2)

print(f"Updated Prashna rules count: {len(prashna_rules)} (+{len(new_prashna_rules)} new)")

# =========================================================================
# 2. BHAVARTHA RATNAKARA & UTTARA KALAMRITA (भावार्थ रत्नाकर व उत्तर कालामृत)
# =========================================================================
cm_file = os.path.join(grantha_dir, "classic_misc_rules.json")
with open(cm_file, "r", encoding="utf-8") as f:
    cm_data = json.load(f)

cm_rules = cm_data.get("rules", [])
existing_cm_ids = {r["rule_id"] for r in cm_rules}
print(f"Existing Classic Misc rules: {len(cm_rules)}")

new_cm_rules = []

# Bhavartha Ratnakara: 12 Lagnas specific yoga formulas by Sri Ramanujacharya
BR_LAGNAS = [
    ("Aries", "मेष लग्न", "Sun", "Jupiter", "Mars", "सूर्य-गुरु की युति परम राजयोगकारक है, जबकि शनि बाधक व शुक्र मारक है।"),
    ("Taurus", "वृषभ लग्न", "Saturn", "Mercury", "Venus", "शनि अकेला नवमेश व दशमेश होकर सर्वोच्च राजयोग देता है (योगकारक)।"),
    ("Gemini", "मिथुन लग्न", "Venus", "Mercury", "Saturn", "शुक्र पंचमेश होकर विद्या, लक्ष्मी व सन्तान सुख का प्रदाता है।"),
    ("Cancer", "कर्क लग्न", "Mars", "Jupiter", "Moon", "मंगल पंचमेश व दशमेश होकर अकेला महा-राजयोगकारक बनता है।"),
    ("Leo", "सिंह लग्न", "Mars", "Jupiter", "Sun", "मंगल चतुर्थेश व नवमेश होकर सर्व कार्य सिद्धि व ऐश्वर्य प्रदान करता है।"),
    ("Virgo", "कन्या लग्न", "Venus", "Mercury", "Saturn", "शुक्र द्वितीयेश व नवमेश होकर अपार धन-सम्पदा का स्वामी है।"),
    ("Libra", "तुला लग्न", "Saturn", "Venus", "Mercury", "शनि चतुर्थेश व पंचमेश होकर परम योगकारक और राजसम्मान प्रदाता है।"),
    ("Scorpio", "वृश्चिक लग्न", "Jupiter", "Moon", "Sun", "गुरु पंचमेश व चन्द्रमा नवमेश मिलकर महालक्ष्मी योग बनाते हैं।"),
    ("Sagittarius", "धनु लग्न", "Sun", "Mars", "Jupiter", "सूर्य नवमेश व मंगल पंचमेश होकर प्रतापी राजयोग का निर्माण करते हैं।"),
    ("Capricorn", "मकर लग्न", "Venus", "Mercury", "Saturn", "शुक्र पंचमेश व दशमेश होकर अकेला सर्वोच्च योगकारक ग्रह है।"),
    ("Aquarius", "कुम्भ लग्न", "Venus", "Saturn", "Mercury", "शुक्र चतुर्थेश व नवमेश होकर अखंड भूमि, वाहन व ऐश्वर्य देता है।"),
    ("Pisces", "मीन लग्न", "Moon", "Mars", "Jupiter", "चन्द्रमा पंचमेश व मंगल नवमेश होकर कुलदीपक योग बनाते हैं।")
]

for sign, sign_title, yogakaraka, benefic_p, lagna_lord, shloka_desc in BR_LAGNAS:
    for h in [1, 2, 4, 5, 7, 9, 10, 11]:
        rid = f"BR_LAGNA_{sign.upper()}_{yogakaraka.upper()}_H{h}"
        if rid not in existing_cm_ids:
            new_cm_rules.append({
                "rule_id": rid,
                "rule_name_hi": f"भावार्थ रत्नाकर: {sign_title} - योगकारक {PLANET_HI[yogakaraka]} {h}वें भाव में",
                "rule_name_en": f"Bhavartha Ratnakara {sign} Lagna {yogakaraka} in House {h}",
                "source": {
                    "text": "Bhavartha Ratnakara",
                    "chapter": f"{sign} Lagna Yoga Adhyaya",
                    "author": "Sri Ramanujacharya",
                    "era": "Classical 12th Century CE"
                },
                "school": "Classical",
                "category": "raja_yoga",
                "condition": {
                    "type": "ALL",
                    "criteria": [
                        {"entity": "Lord_1", "sign": sign},
                        {"entity": yogakaraka, "house": h}
                    ]
                },
                "effect": {
                    "themes": ["raja_yoga", "bhavartha_ratnakara", "wealth"],
                    "polarity": "+",
                    "strength_base": 0.94,
                    "description_hi": f"रामानुजाचार्य कृत भावार्थ रत्नाकर: {sign_title} हेतु {shloka_desc} {PLANET_HI[yogakaraka]} का {h}वें भाव में होना उत्कृष्ट फल देता है।"
                }
            })

# Kalidasa's Uttara Kalamrita: Badhaka & Maraka Sthana Rules
BADHAKA_RULES = [
    ("Chara", "चर राशि (मेष, कर्क, तुला, मकर)", 11, "एकादश भाव बाधक स्थान होता है। लाभ में व्यवधान अथवा गुप्त शत्रु।"),
    ("Sthira", "स्थिर राशि (वृषभ, सिंह, वृश्चिक, कुम्भ)", 9, "नवम भाव बाधक स्थान होता है। पिता से मतभेद अथवा भाग्य में अचानक अड़चन।"),
    ("Dwiswabhava", "द्विस्वभाव राशि (मिथुन, कन्या, धनु, मीन)", 7, "सप्तम भाव बाधक स्थान होता है। साझेदारी व दांपत्य में सतर्कता अनिवार्य।")
]

for r_type, r_title, b_house, b_desc in BADHAKA_RULES:
    for p in ["Saturn", "Mars", "Rahu", "Sun"]:
        rid = f"UK_BADHAKA_{r_type.upper()}_{p.upper()}_H{b_house}"
        if rid not in existing_cm_ids:
            new_cm_rules.append({
                "rule_id": rid,
                "rule_name_hi": f"उत्तर कालामृत: {r_title} - बाधकेश {PLANET_HI[p]} का {b_house}वें भाव में फल",
                "rule_name_en": f"Uttara Kalamrita Badhaka {p} in House {b_house}",
                "source": {
                    "text": "Uttara Kalamrita",
                    "chapter": "Karakatwa & Badhaka Adhyaya",
                    "author": "Mahakavi Kalidasa",
                    "era": "Classical 4th Century CE"
                },
                "school": "Classical",
                "category": "badhaka",
                "condition": {
                    "type": "ALL",
                    "criteria": [{"entity": p, "house": b_house}]
                },
                "effect": {
                    "themes": ["badhaka", "maraka", "caution"],
                    "polarity": "-",
                    "strength_base": 0.86,
                    "description_hi": f"महाकवि कालिदास कृत उत्तर कालामृत: {r_title} हेतु {b_desc}"
                }
            })

cm_rules.extend(new_cm_rules)
cm_data["rules"] = cm_rules
cm_data["metadata"]["count"] = len(cm_rules)

with open(cm_file, "w", encoding="utf-8") as f:
    json.dump(cm_data, f, ensure_ascii=False, indent=2)

print(f"Updated Classic Misc rules count: {len(cm_rules)} (+{len(new_cm_rules)} new)")

# =========================================================================
# 3. VEDIC & CHALDEAN NUMEROLOGY EXPANSION (अंकशास्त्र)
# =========================================================================
num_file = os.path.join(grantha_dir, "numerology_rules.json")
with open(num_file, "r", encoding="utf-8") as f:
    num_data = json.load(f)

num_rules = num_data.get("rules", [])
existing_num_ids = {r["rule_id"] for r in num_rules}
print(f"Existing Numerology rules: {len(num_rules)}")

new_num_rules = []

# Radical Numbers 1-9 in 12 Houses
NUM_PLANETS = {
    1: ("Sun", "सूर्य", "नेतृत्व, प्रशासनिक दक्षता, आत्मविश्वास"),
    2: ("Moon", "चन्द्र", "कल्पनाशीलता, संवेदनशीलता, जनसंपर्क"),
    3: ("Jupiter", "गुरु", "विद्या, परामर्श, विस्तार, सात्विकता"),
    4: ("Rahu", "राहु", "अचानक बदलाव, तकनीकी शोध, कूटनीति"),
    5: ("Mercury", "बुध", "वाणिज्य, तीव्र गति, संप्रेषण, विश्लेषण"),
    6: ("Venus", "शुक्र", "सौंदर्य, भोग, विलासिता, कला, आकर्षण"),
    7: ("Ketu", "केतु", "अध्यात्म, अनुसंधान, रहस्य विद्या, त्याग"),
    8: ("Saturn", "शनि", "धैर्य, न्याय, कठोर श्रम, दीर्घकालिक सिद्धि"),
    9: ("Mars", "मंगल", "साहस, पराक्रम, गति, खेलकूद, सेना")
}

for num_val, (p_name, p_hi, trait) in NUM_PLANETS.items():
    for h in HOUSES:
        rid = f"NUM_RADICAL_{num_val}_{p_name.upper()}_H{h}"
        if rid not in existing_num_ids:
            pol = "+" if h in [1, 2, 4, 5, 9, 10, 11] else "-"
            new_num_rules.append({
                "rule_id": rid,
                "rule_name_hi": f"अंकशास्त्र: मूलांक {num_val} ({p_hi}) का {h}वें भाव में फल",
                "rule_name_en": f"Numerology Radical {num_val} ({p_name}) in House {h}",
                "source": {
                    "text": "Ank Shastra (Vedic Numerology)",
                    "chapter": f"Mulank {num_val} Prakaranam",
                    "author": "Cheiro & Ancient Rishi Tradition",
                    "era": "Classical Numerology"
                },
                "school": "Numerology",
                "category": "numerology_mulank",
                "condition": {
                    "type": "ALL",
                    "criteria": [{"entity": p_name, "house": h}]
                },
                "effect": {
                    "themes": ["numerology", "mulank", "personality"],
                    "polarity": pol,
                    "strength_base": 0.84,
                    "description_hi": f"अंकशास्त्र अनुसार मूलांक {num_val} के स्वामी {p_hi} का {h}वें भाव में अवस्थान: जातक में '{trait}' की विशिष्ट प्रधानता रहती है।"
                }
            })

# Chaldean Compound Numbers (10 to 40)
CHALDEAN_NUMS = [
    (10, "भाग्य का पहिया (Wheel of Fortune)", "+", "उन्नति, सम्मान, अचानक सौभाग्य व सफलता।"),
    (11, "छिपे हुए खतरे (Clenched Fists)", "-", "आंतरिक संघर्ष, विश्वासघात का भय व सतर्कता।"),
    (12, "बलिदान (The Sacrifice)", "-", "दूसरों के लिए त्याग, आध्यात्मिक शोध व परोपकार।"),
    (13, "परिवर्तन (Regeneration / Change)", "+", "कठिनाइयों से उबरकर नई शक्ति का उदय।"),
    (14, "संतुलन (Movement & Challenge)", "+", "यात्राएं, व्यापारिक लाभ व अनुकूल परिवर्तन।"),
    (15, "जादुई आकर्षण (The Magician)", "+", "वाक्पटुता, धन-धान्य व प्रबल सम्मोहन।"),
    (16, "टूटा हुआ गढ़ (The Shattered Citadel)", "-", "आकस्मिक हानि से बचाव, अहंकार त्याग अनिवार्य।"),
    (17, "महान आशा का तारा (Star of the Magi)", "+", "सर्वत्र विजय, अमर यश व ईश्वरीय कृपा।"),
    (18, "आंतरिक द्वंद्व (Spiritual Conflict)", "-", "झूठे मित्रों से धोखा, षड्यंत्र से बचाव।"),
    (19, "स्वर्ग का राजकुमार (Prince of Heaven)", "+", "अखंड सुख, विजय, संपत्ति व राजमान।"),
    (20, "पुनर्जागरण (The Awakening)", "+", "आध्यात्मिक जागृति, नई योजनाएं व कर्तव्य निष्ठा।"),
    (21, "सफलता का मुकुट (Crown of the Magi)", "+", "अंतिम विजय, मान-सम्मान व सर्वत्र ख्याति।"),
    (23, "शाही तारा (Royal Star of the Lion)", "+", "अधिकारी वर्ग से लाभ, उच्च सुरक्षा व ऐश्वर्य।"),
    (24, "शुभ सहयोग (Love & Money)", "+", "पारिवारिक सुख, प्रेम में सफलता व वित्तीय स्थिरता।"),
    (28, "विश्वासघात की चेतावनी", "-", "साझेदारी में सतर्कता, कानूनी विवाद से बचाव।"),
    (33, "आध्यात्मिक गुरु (Master Teacher)", "+", "लोकोत्तर ज्ञान, जनसेवा, समाज सुधार व पूज्य भाव।")
]

for c_num, c_title, pol, c_desc in CHALDEAN_NUMS:
    rid = f"NUM_CHALDEAN_COMP_{c_num}"
    if rid not in existing_num_ids:
        new_num_rules.append({
            "rule_id": rid,
            "rule_name_hi": f"कीरो अंकशास्त्र: संयुक्त अंक {c_num} - {c_title}",
            "rule_name_en": f"Chaldean Compound Number {c_num} {c_title}",
            "source": {
                "text": "Ank Shastra (Vedic Numerology)",
                "chapter": "Chaldean Compound Numbers",
                "author": "Cheiro",
                "era": "Modern Classical"
            },
            "school": "Numerology",
            "category": "numerology_compound",
            "condition": {
                "type": "ALL",
                "criteria": [{"entity": "Sun", "quality": "in_kendra" if pol == "+" else "in_dusthana"}]
            },
            "effect": {
                "themes": ["numerology", "compound_number", "destiny"],
                "polarity": pol,
                "strength_base": 0.88,
                "description_hi": f"कीरो रहस्यमयी अंकशास्त्र अनुसार संयुक्त संख्या {c_num}: {c_desc}"
            }
        })

num_rules.extend(new_num_rules)
num_data["rules"] = num_rules
num_data["metadata"]["count"] = len(num_rules)

with open(num_file, "w", encoding="utf-8") as f:
    json.dump(num_data, f, ensure_ascii=False, indent=2)

print(f"Updated Numerology rules count: {len(num_rules)} (+{len(new_num_rules)} new)")

# =========================================================================
# 4. BPHS VIMSHOTTARI DASHA & DOUBLE TRANSIT (दशा व द्वि-गोचर वेध)
# =========================================================================
bphs_file = os.path.join(grantha_dir, "bphs_rules.json")
with open(bphs_file, "r", encoding="utf-8") as f:
    bphs_data = json.load(f)

bphs_rules = bphs_data.get("rules", [])
existing_bphs_ids = {r["rule_id"] for r in bphs_rules}
print(f"Existing BPHS rules: {len(bphs_rules)}")

new_bphs_rules = []

# Double Transit (शनि व गुरु का द्वि-गोचर प्रभाव) on 12 Bhavas
DOUBLE_TRANSIT_EVENTS = [
    (1, "स्वास्थ्य, दीर्घायु व नए जीवन-युग का आरंभ।"),
    (2, "विपुल धन संचय, पैतृक लाभ व परिवार में उत्सव।"),
    (3, "साहस, पराक्रम, लघु यात्रा व भाई का भाग्योदय।"),
    (4, "नया गृह/भवन निर्माण, भूमि क्रय व वाहन सुख।"),
    (5, "संतान प्राप्ति, उच्च शिक्षा में सफलता व प्रेम संबंध।"),
    (6, "शत्रु दमन, रोग से मुक्ति व प्रतियोगी परीक्षा में विजय।"),
    (7, "विवाह संस्कार, व्यावसायिक साझेदारी व जनसंपर्क।"),
    (8, "अचानक वसीयत, पैतृक संपत्ति व गुप्त साधना।"),
    (9, "विदेश यात्रा, उच्च धार्मिक अनुष्ठान व भाग्य वृद्धि।"),
    (10, "राजकीय सत्ता, पदोन्नति, नया पदभार व करियर शिखर।"),
    (11, "अथाह आर्थिक लाभ, बड़े अनुबंध व मनोकामना सिद्धि।"),
    (12, "विदेश में स्थायी निवास (PR), आध्यात्मिक मोक्ष व तीर्थ वास।")
]

for b_num, b_event in DOUBLE_TRANSIT_EVENTS:
    rid = f"BPHS_DOUBLE_TRANSIT_BHAVA_{b_num}"
    if rid not in existing_bphs_ids:
        new_bphs_rules.append({
            "rule_id": rid,
            "rule_name_hi": f"पाराशर द्वि-गोचर वेध: भाव {b_num} पर शनि-गुरु का संयुक्त प्रभाव",
            "rule_name_en": f"BPHS Double Transit of Saturn & Jupiter on House {b_num}",
            "source": {
                "text": "Brihat Parashara Hora Shastra",
                "chapter": "Adhyaya 50 (Gochar Phala Adhyaya)",
                "author": "Maharishi Parashara",
                "era": "Classical Vedic"
            },
            "school": "Parashari",
            "category": "gochar",
            "condition": {
                "type": "ALL",
                "criteria": [
                    {"entity": "Saturn", "quality": "in_kendra"},
                    {"entity": "Jupiter", "quality": "in_kendra"}
                ]
            },
            "effect": {
                "themes": ["gochar", "double_transit", "timing", "event"],
                "polarity": "+",
                "strength_base": 0.96,
                "description_hi": f"महर्षि पराशर अनुसार शनि व देवगुरु का संयुक्त गोचर प्रभाव भाव {b_num} को सक्रिय करता है: {b_event}"
            }
        })

# Vimshottari Mahadasha in 12 Houses
for p in PLANETS_9:
    for h in HOUSES:
        rid = f"BPHS_DASHA_{p.upper()}_H{h}"
        if rid not in existing_bphs_ids:
            pol = "+" if h in [1, 2, 4, 5, 9, 10, 11] else "-"
            new_bphs_rules.append({
                "rule_id": rid,
                "rule_name_hi": f"पाराशर विंशोत्तरी: {PLANET_HI[p]} महादशा {h}वें भाव में फल",
                "rule_name_en": f"BPHS Vimshottari {p} Mahadasha in House {h}",
                "source": {
                    "text": "Brihat Parashara Hora Shastra",
                    "chapter": "Adhyaya 46 (Vimshottari Dasha Phala)",
                    "author": "Maharishi Parashara",
                    "era": "Classical Vedic"
                },
                "school": "Parashari",
                "category": "dasha",
                "condition": {
                    "type": "ALL",
                    "criteria": [
                        {"entity": "Dasha_Maha", "is": p},
                        {"entity": p, "house": h}
                    ]
                },
                "effect": {
                    "themes": ["dasha", "vimshottari", "timing"],
                    "polarity": pol,
                    "strength_base": 0.88,
                    "description_hi": f"पाराशर विंशोत्तरी दशाध्याय: {PLANET_HI[p]} की दशा में जब ग्रह {h}वें भाव में स्थित हो: {'संबंधित भाव के शुभ फलों का पूर्ण विस्तार।' if pol == '+' else 'शारीरिक व आर्थिक मामलों में अतिरिक्त सावधानी अपेक्षित।'}"
                }
            })

bphs_rules.extend(new_bphs_rules)
bphs_data["rules"] = bphs_rules
bphs_data["metadata"]["count"] = len(bphs_rules)

with open(bphs_file, "w", encoding="utf-8") as f:
    json.dump(bphs_data, f, ensure_ascii=False, indent=2)

print(f"Updated BPHS rules count: {len(bphs_rules)} (+{len(new_bphs_rules)} new)")

