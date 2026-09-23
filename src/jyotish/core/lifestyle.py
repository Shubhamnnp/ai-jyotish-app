"""
Lifestyle, Health, Diet, Relationship, and Physical Anatomy Engine for JyotishOS.
Rooted in Classical Vedic Astrology and Ayurvedic texts:
- Brihat Parashara Hora Shastra (BPHS) - Anga Vibhaga, Bhava Karakatvas, Rogas
- Charaka Samhita & Sushruta Samhita - Tridosha (Vata, Pitta, Kapha) & Ahara Niyama
- Phaladeepika (Mantreshwara) - Planetary Diseases, Relationships & Body Constitution
- Sarvartha Chintamani & Jataka Parijata - Vulnerable Limbs & Medical Astrology
"""

from typing import Dict, List, Tuple, Optional, Any
from .constants import (
    SIGNS, SIGN_NAMES, SIGN_LORDS, GRAHAS,
    NATURAL_FRIENDS, NATURAL_ENEMIES
)
from .models import KundaliChart, PlanetPosition, HouseCusp


# =============================================================================
# 1. DIET & AYURVEDIC NUTRITION ENGINE (खानपान विश्लेषण)
# =============================================================================

class DietEngine:
    """Calculates Ayurvedic Tridosha Prakriti, 2nd house eating patterns,

    favorable & unfavorable foods, and dietary remedies based on BPHS & Charaka Samhita.
    """

    # Element to Dosha mapping
    ELEMENT_DOSHA = {
        "Fire": "Pitta (पित्त)",
        "Earth": "Vata (वात)",
        "Air": "Vata-Kapha (वात-कफ)",
        "Water": "Kapha (कफ)"
    }

    DOSHA_DETAILS = {
        "Pitta (पित्त)": {
            "title_hi": "पित्त प्रकृति (Pitta - Fire/Agni)",
            "characteristics_hi": "तीव्र जठराग्नि (मजबूत भूख), गर्म तासीर, पसीना अधिक आना, तीखा/खट्टा खाने की तीव्र लालसा। अत्यधिक तनाव में एसिडिटी या अल्सर की संभावना।",
            "favorable_hi": [
                "अनाज: जौ, गेहूं, बासमती चावल, जई (Oats)",
                "दालें: मूंग दाल, मसूर (सीमित), अरहर",
                "सब्जियां: लौकी, तोरी, परवल, ककड़ी, खीरा, पत्तागोभी, ब्रोकली",
                "फल: मीठा सेब, अनार, पके आम, नारियल, अंगूर, पपीता",
                "दुग्ध उत्पाद: ठंडा गाय का दूध, ताज़ा मक्खन, घी (सर्वोत्तम)",
                "मसाले: सौंफ, धनिया, इलायची, पुदीना, जीरा (शीतल मसाले)"
            ],
            "unfavorable_hi": [
                "अत्यधिक लाल मिर्च, गरम मसाला, सिरका, इमली, खटाई",
                "तला-भुना, बासी एवं अत्यधिक तैलीय जंक फूड",
                "शराब, बियर, अत्यधिक काली चाय व कॉफ़ी",
                "खट्टे फल (कच्चा आम, नींबू का अतिसेवन), खमीरीकृत खाद्य (Pickles)"
            ],
            "fasting_remedy_hi": "सोमवार या एकादशी को शीतल जल, नारियल पानी व दूध आधारित फलाहार रखें।"
        },
        "Vata (वात)": {
            "title_hi": "वात प्रकृति (Vata - Air & Space)",
            "characteristics_hi": "अनियमित भूख (कभी बहुत तेज़, कभी भूख न लगना), गैस, पेट फूलना, रूखापन, चंचल मन। ठंडा व सूखा भोजन तुरंत कष्ट देता है।",
            "favorable_hi": [
                "अनाज: गेहूं, गर्म दलिया, तिल, भुने चने, भूरा चावल",
                "दालें: उड़द (हिंग युक्त), मूंग दाल, तुअर दाल",
                "सब्जियां: गाजर, चुकंदर, शकरकंद, पकी पालक, मेथी, घीया",
                "फल: केला, भीगे बादाम, खजूर, अंजीर, पका पपीता, चीकू",
                "दुग्ध उत्पाद: गर्म गुनगुना दूध (हल्दी/केसर युक्त), ताजा पनीर, शुद्ध घी",
                "मसाले: अदरक, लहसुन, हींग, अजवाइन, दालचीनी, सेंधा नमक"
            ],
            "unfavorable_hi": [
                "सूखे, कड़क, ठंडे खाद्य पदार्थ (चिप्स, नमकीन, ड्राई टोस्ट)",
                "फूलगोभी, पत्तागोभी, राजमा, छोले (बिना हींग-अजवाइन के गैस करते हैं)",
                "फ्रिज का ठंडा बासी पानी, कोल्ड ड्रिंक्स व बर्फ",
                "अत्यधिक कड़वे व कसैले खाद्य, समय पर भोजन न करना"
            ],
            "fasting_remedy_hi": "गुरुवार या शनिवार को तिल-गुड़ या हल्के दलिया का सेवन करें; निर्जला उपवास से बचें।"
        },
        "Kapha (कफ)": {
            "title_hi": "कफ प्रकृति (Kapha - Water & Earth)",
            "characteristics_hi": "मंद जठराग्नि (धीमा मेटाबॉलिज्म), भोजन धीरे पचना, आलस्य, वजन तेजी से बढ़ना, मीठे का अत्यधिक शौकीन।",
            "favorable_hi": [
                "अनाज: बाजरा, मक्का, जौ, रागी, ब्राउन राइस",
                "दालें: मूंग, चना दाल, कुल्थी दाल (कफ नाशक)",
                "सब्जियां: करेला, मेथी, परवल, मूली, सहजन (ड्रमस्टिक), हरी मिर्च",
                "फल: सेब, अनार, पपीता, जामुन, संतरा (कम मीठे फल)",
                "दुग्ध उत्पाद: कम वसा वाला मट्ठा (छाछ भुने जीरे के साथ), हल्का गाय का दूध",
                "मसाले: त्रिकटु (सोंठ, काली मिर्च, पिप्पली), दालचीनी, लौंग, मेथीदाना"
            ],
            "unfavorable_hi": [
                "अत्यधिक मिठाई, हलवा, आइसक्रीम, पेस्ट्री, क्रीम",
                "भारी चिकनाई, पनीर, दही (विशेषकर रात्रि में बिल्कुल वर्जित)",
                "दिन में सोने की आदत और भोजन के तुरंत बाद लेटना",
                "मैदा, सफेद ब्रेड, केला व अत्यधिक केला/चीकू"
            ],
            "fasting_remedy_hi": "मंगलवार या एकादशी को केवल गरम पानी और त्रिफला या शहद-पानी पर उपवास रखें।"
        },
        "Vata-Kapha (वात-कफ)": {
            "title_hi": "वात-कफ मिश्रित प्रकृति (Vata-Kapha)",
            "characteristics_hi": "परिवर्तनशील पाचन, मौसम बदलते ही जुकाम/गैस, जोड़ों में जकड़न एवं सुस्ती का अनुभव।",
            "favorable_hi": [
                "अनाज: गेहूं, जौ, ज्वार, दलिया",
                "दालें: मूंग, मसूर, अरहर (हल्की सुपाच्य)",
                "सब्जियां: लौकी, परवल, गाजर, पालक, तोरी",
                "फल: अनार, सेब, पपीता, चीकू, खजूर",
                "दुग्ध उत्पाद: ताज़ा छाछ (दोपहर में), गुनगुना हल्दी दूध",
                "मसाले: जीरा, अजवाइन, सोंठ, दालचीनी, तेजपत्ता"
            ],
            "unfavorable_hi": [
                "ठंडा बासी भोजन, फ्रिज का पानी, कोल्डड्रिंक",
                "अत्यधिक खट्टा, भारी मिठाई, राजमा, मैदा",
                "देर रात का भारी भोजन"
            ],
            "fasting_remedy_hi": "शुक्रवार या सोमवार को अल्पाहार (दूध-फल) आधारित व्रत रखें।"
        }
    }

    @classmethod
    def analyze(cls, chart: KundaliChart) -> Dict[str, Any]:
        lagna_sign_id = chart.lagna_sign_id
        lagna_sign = SIGNS[lagna_sign_id - 1]
        lagna_elem = lagna_sign["element"]
        primary_dosha = cls.ELEMENT_DOSHA.get(lagna_elem, "Pitta (पित्त)")

        # Moon sign dosha influence
        moon_pos = chart.planets.get("Moon")
        moon_sign_elem = "Water"
        if moon_pos:
            moon_sign_elem = SIGNS[moon_pos.sign_id - 1]["element"]

        # 2nd House Analysis (Food & Habits)
        h2_sign_id = ((lagna_sign_id) % 12) + 1  # 2nd house
        h2_sign = SIGNS[h2_sign_id - 1]
        h2_lord = h2_sign["lord"]

        h2_occupants = [p_name for p_name, p in chart.planets.items() if p.house_from_lagna == 2]

        # 2nd house eating psychology
        eating_habit_notes = []
        if "Rahu" in h2_occupants:
            eating_habit_notes.append("⚠️ राहु द्वितीय भाव में: असामान्य या तीखे, फास्ट-फूड और होटल के भोजन की ओर अधिक खिंचाव। मिलावटी या बासी भोजन से पेट में संक्रमण की आशंका, अतः स्वच्छता अनिवार्य है।")
        if "Mars" in h2_occupants:
            eating_habit_notes.append("🔥 मंगल द्वितीय भाव में: अत्यधिक गरम, मसालेदार, मिर्च युक्त एवं तामसिक भोजन की लालसा। जल्दी-जल्दी खाने की आदत से बचें।")
        if "Saturn" in h2_occupants:
            eating_habit_notes.append("🪐 शनि द्वितीय भाव में: खानपान में अनियमितता, देर से खाना या रूखा-सूखा भोजन। ताज़ा, गर्म और शुद्ध सात्विक भोजन ही लाभप्रद रहेगा।")
        if "Jupiter" in h2_occupants:
            eating_habit_notes.append("👑 गुरु द्वितीय भाव में: स्वादिष्ट, मीठा व गरिष्ठ भोजन प्रिय। भोजन की शुद्धता और सात्विकता पर विशेष ध्यान दें; अधिक मीठे से लीवर/मोटापा पर नियंत्रण रखें।")
        if "Venus" in h2_occupants:
            eating_habit_notes.append("✨ शुक्र द्वितीय भाव में: कलात्मक व्यंजन, मिष्ठान्न, रसदार फल व दुग्ध उत्पाद प्रिय। स्वादिष्ट भोजन के शौकीन।")
        if "Sun" in h2_occupants:
            eating_habit_notes.append("☀️ सूर्य द्वितीय भाव में: सात्विक परंतु पित्तकारक भोजन पसंद; अधिक नमक व तीखे से रक्तचाप बढ़ सकता है।")
        if "Moon" in h2_occupants:
            eating_habit_notes.append("🌙 चंद्र द्वितीय भाव में: जलीय तत्व, दूध, खीर, सूप व रसदार फल प्रिय। रात्रि में भारी भोजन से बचें।")
        if not eating_habit_notes:
            eating_habit_notes.append(f"द्वितीय भाव का स्वामी ग्रह {h2_lord} है। सामान्य सात्विक व समयबद्ध भोजन आपके शरीर के अनुकूल है।")

        dosha_info = cls.DOSHA_DETAILS.get(primary_dosha, cls.DOSHA_DETAILS["Pitta (पित्त)"])

        # 6th house (digestive vulnerabilities)
        h6_occupants = [p_name for p_name, p in chart.planets.items() if p.house_from_lagna == 6]
        digestive_warnings = []
        if "Mars" in h6_occupants or "Rahu" in h6_occupants:
            digestive_warnings.append("पेट में जलन, अल्सर या फूड पॉइजनिंग की संवेदनशीलता — तली-भुनी चीज़ों से सख्त परहेज रखें।")
        if "Saturn" in h6_occupants:
            digestive_warnings.append("पाचन धीमा (कब्ज / गैस) होने की प्रवृत्ति — पर्याप्त गुनगुना पानी व फाइबर युक्त भोजन लें।")
        if "Jupiter" in h6_occupants:
            digestive_warnings.append("लीवर व वसा (Cholesterol/Fat) की पाचन क्षमता संवेदनशील — घी-तेल सीमित रखें।")
        if not digestive_warnings:
            digestive_warnings.append("जठराग्नि संतुलित है। भोजन के उपरांत आधा घंटा टहलना और समयबद्ध भोजन उत्तम रहेगा।")

        return {
            "primary_dosha": primary_dosha,
            "dosha_title": dosha_info["title_hi"],
            "characteristics": dosha_info["characteristics_hi"],
            "favorable_foods": dosha_info["favorable_hi"],
            "unfavorable_foods": dosha_info["unfavorable_hi"],
            "eating_habits": eating_habit_notes,
            "digestive_warnings": digestive_warnings,
            "fasting_remedy": dosha_info["fasting_remedy_hi"],
            "favorable_drink": "ताज़ा नारियल पानी, सौंफ-मिश्री अर्क एवं गुनगुना गाय का दूध" if "Pitta" in primary_dosha else ("अदरक-तुलसी काढ़ा व गुनगुना पानी" if "Vata" in primary_dosha else "त्रिकटु जल, छाछ व ग्रीन टी"),
            "salt_recommendation": "सेंधा नमक (Rock Salt) सर्वोत्तम है, सादे समुद्री नमक का अतिसेवन न करें।"
        }


# =============================================================================
# 2. RELATIONSHIP MATRIX ENGINE (संबंध विश्लेषण)
# =============================================================================

class RelationshipEngine:
    """Analyzes relationships with Spouse, Family, Friends, Benefactors,

    and Opponents according to BPHS House Lords and Planetary Naisargika Maitri.
    """

    RELATION_HOUSES = {
        "spouse": {"house": 7, "karaka": "Venus", "title_hi": "जीवनसाथी / दांपत्य (Spouse & Partner)"},
        "father": {"house": 9, "karaka": "Sun", "title_hi": "पिता एवं गुरुजन (Father & Mentors)"},
        "mother": {"house": 4, "karaka": "Moon", "title_hi": "माता एवं मातृपक्ष (Mother & Maternal Side)"},
        "siblings": {"house": 3, "karaka": "Mars", "title_hi": "भाई-बहन एवं सहकर्मी (Siblings & Peers)"},
        "children": {"house": 5, "karaka": "Jupiter", "title_hi": "संतान एवं शिष्य (Children & Students)"},
        "friends": {"house": 11, "karaka": "Jupiter", "title_hi": "मित्र, समर्थक एवं शुभचिंतक (Friends & Well-wishers)"},
        "enemies": {"house": 6, "karaka": "Mars", "title_hi": "विरोधी, शत्रु एवं प्रतिस्पर्धी (Opponents & Challengers)"},
        "partners": {"house": 7, "karaka": "Mercury", "title_hi": "व्यावसायिक साझेदार (Business Partners)"}
    }

    @classmethod
    def analyze(cls, chart: KundaliChart) -> Dict[str, Any]:
        lagna_sign_id = chart.lagna_sign_id
        lagnesh = SIGN_LORDS[SIGNS[lagna_sign_id - 1]["name_en"]]

        results = {}
        for rel_key, rel_meta in cls.RELATION_HOUSES.items():
            h_num = rel_meta["house"]
            target_sign_id = ((lagna_sign_id + h_num - 2) % 12) + 1
            target_sign_name = SIGNS[target_sign_id - 1]["name_en"]
            house_lord = SIGN_LORDS[target_sign_name]
            karaka = rel_meta["karaka"]

            # Occupants in this house
            occupants = [p_name for p_name, p in chart.planets.items() if p.house_from_lagna == h_num]

            # Relationship harmony score:
            # Check friendship between Lagnesh and House Lord
            is_friend = house_lord in NATURAL_FRIENDS.get(lagnesh, []) or house_lord == lagnesh
            is_enemy = house_lord in NATURAL_ENEMIES.get(lagnesh, [])

            # Check house lord dignity
            lord_pos = chart.planets.get(house_lord)
            lord_dignity = lord_pos.dignity if lord_pos else "neutral"

            # Determine status & description
            if h_num == 6:
                # Enemies
                harm_level = "उच्च (सावधानी आवश्यक)" if occupants or is_enemy else "मध्यम (नियंत्रण में)"
                nature_hi = f"६ठे भाव में {', '.join(occupants) if occupants else 'कोई पापग्रह नहीं'} है। गुप्त प्रतिस्पर्धियों से सतर्क रहें।"
                if "Mars" in occupants or "Saturn" in occupants or "Rahu" in occupants:
                    advice_hi = "शत्रुहंता योग: विरोधी आप पर हावी नहीं हो पाएंगे, अंततः आपकी ही विजय होगी।"
                else:
                    advice_hi = "ऋण देने या अजनबियों पर अंधविश्वास करने से बचें; लिखा-पढ़ी में सावधानी रखें।"
                results[rel_key] = {
                    "title": rel_meta["title_hi"],
                    "lord": house_lord,
                    "occupants": occupants,
                    "status": harm_level,
                    "nature_hi": nature_hi,
                    "advice_hi": advice_hi
                }
            elif h_num == 11:
                # Friends & Benefactors
                benefit_level = "अत्यधिक लाभकारी (Strong Benefactors)" if (is_friend and lord_dignity in ("exalted", "own", "friend")) else "सामान्य सहयोगी"
                nature_hi = f"११वें भाव के स्वामी {house_lord} हैं। {', '.join(occupants) if occupants else 'शुभ भाव'} द्वारा समर्थित।"
                advice_hi = "बुजुर्गों, उच्चाधिकारियों और विद्वान मित्रों से जीवन में अकस्मात बड़ा सहयोग और आर्थिक लाभ प्राप्त होगा।"
                results[rel_key] = {
                    "title": rel_meta["title_hi"],
                    "lord": house_lord,
                    "occupants": occupants,
                    "status": benefit_level,
                    "nature_hi": nature_hi,
                    "advice_hi": advice_hi
                }
            elif h_num == 7:
                # Spouse
                status = "सद्भावपूर्ण एवं भाग्यवर्धक" if is_friend else ("तार्किक / विचार-भेद परंतु सहयोगात्मक" if not is_enemy else "धीरज व तालमेल आवश्यक")
                if "Venus" in occupants or "Jupiter" in occupants:
                    status += " (अत्यंत शुभ ग्रह दृष्टि)"
                nature_hi = f"सप्तमेश {house_lord} की स्थिति अनुसार जीवनसाथी बुद्धिमान व कर्मठ होंगे।"
                advice_hi = "आपसी समझ और संवाद खुला रखें; जीवनसाथी के नाम से किया गया कार्य फलीभूत होगा।"
                results[rel_key] = {
                    "title": rel_meta["title_hi"],
                    "lord": house_lord,
                    "occupants": occupants,
                    "status": status,
                    "nature_hi": nature_hi,
                    "advice_hi": advice_hi
                }
            else:
                status = "प्रगाढ़ एवं सहयोगी" if is_friend else ("सामान्य संबंध" if not is_enemy else "सहनशीलता अपेक्षित")
                results[rel_key] = {
                    "title": rel_meta["title_hi"],
                    "lord": house_lord,
                    "occupants": occupants,
                    "status": status,
                    "nature_hi": f"भाव स्वामी {house_lord} तथा कारक {karaka} की स्थिति अनुसार।",
                    "advice_hi": "सद्भाव बनाए रखने से इस पक्ष से मानसिक संबल व सुख मिलेगा।"
                }

        # Overall relationship summary
        benefactor_side = "मित्र, गुरुजन एवं मामा/नानिहाल पक्ष" if "Jupiter" in NATURAL_FRIENDS.get(lagnesh, []) else "भाई-बंधु, सहकर्मी एवं पिता"
        caution_side = "सट्टेबाज़, अनपेक्षित साझेदार या गुप्त आलोचक"

        return {
            "lagnesh": lagnesh,
            "relations": results,
            "greatest_helper_side": benefactor_side,
            "caution_side": caution_side,
            "core_mantra": "लग्नेश की अनुकूलता के आधार पर जिन संबंधों में आदर और पारदर्शिता रहेगी, वे जीवन के हर मोड़ पर सहायक सिद्ध होंगे।"
        }


# =============================================================================
# 3. HEALTH & DISEASE PREDICTOR (स्वास्थ्य एवं भावी रोग विश्लेषण)
# =============================================================================

class HealthEngine:
    """Evaluates Overall Vitality, Current Weak Points, and Future Disease Risks

    based on 6th/8th/12th houses, afflicted planets, and classical Graha Karakatvas.
    """

    GRAHA_BODY_MAPPING = {
        "Sun": {
            "organs": "हृदय, अस्थि (हड्डियां), नेत्र दृष्टि, सिर, प्राण शक्ति, पित्त",
            "diseases": "हृदय रोग, उच्च रक्तचाप, आंखों में जलन/कमजोरी, हड्डियों की दुर्बलता, सिरदर्द/माइग्रेन",
            "gem_metal": "माणिक्य (Ruby) / तांबा / सूर्य नमस्कार"
        },
        "Moon": {
            "organs": "मन, मस्तिष्क, फेफड़े, रक्त प्रवाह, शारीरिक तरल, कफ",
            "diseases": "मानसिक तनाव, अनिद्रा, अवसाद, कफ/खांसी, निमोनिया, जल-जनित रोग",
            "gem_metal": "मोती (Pearl) / चांदी / ॐ नमः शिवाय जप"
        },
        "Mars": {
            "organs": "रक्त मज्जा, मांसपेशियां, नाक, पित्त, जननांग, ऊर्जा",
            "diseases": "रक्त विकार, फोड़े-फुंसी, उच्च रक्तचाप, कटने-जलने की चोट, सर्जरी/शल्य क्रिया",
            "gem_metal": "मूंगा (Coral) / हनुमान चालीसा / रक्त दान"
        },
        "Mercury": {
            "organs": "तंत्रिका तंत्र (Nervous system), त्वचा (Skin), वाणी, फेफड़े की नलिकाएं",
            "diseases": "चर्म रोग (एलर्जी, खुजली), नसों में खिंचाव, हकलाहट/वाणी विकार, अनिद्रा",
            "gem_metal": "पन्ना (Emerald) / कांसा / हरी मूंग दान"
        },
        "Jupiter": {
            "organs": "यकृत (Liver), प्लीहा, वसा (Fat), कान, मस्तिष्क का विवेक केंद्र",
            "diseases": "मधुमेह (Diabetes), पीलिया/लीवर विकार, मोटापा, कान का दर्द, कोलेस्ट्रॉल",
            "gem_metal": "पुखराज (Yellow Sapphire) / हल्दी / गुरु सेवा"
        },
        "Venus": {
            "organs": "गुर्दा (Kidney), प्रजनन अंग, वीर्य/रज, आंखें, सौंदर्य, हार्मोन",
            "diseases": "मूत्र रोग, पथरी, किडनी संवेदनशीलता, हार्मोनल असंतुलन, मधुमेह",
            "gem_metal": "हीरा (Diamond) / सफेद चंदन / गौ सेवा"
        },
        "Saturn": {
            "organs": "जोड़, घुटने, दांत, रीढ़ की हड्डी, पैर की नसें, वायु विकार",
            "diseases": "गठिया (Arthritis), नसों में दर्द (Sciatica), लकवा, दांतों का गिरना, पुराना कब्ज",
            "gem_metal": "नीलम / तिल का तेल मालिश / पीपल दीप"
        },
        "Rahu": {
            "organs": "अज्ञात तंत्रिकाएं, आंतें, श्वास नलिका, भय/वहम",
            "diseases": "अस्पष्ट रोग (जिसकी रिपोर्ट सामान्य आए पर दर्द रहे), फूड पॉइजनिंग, एलर्जी, गैस",
            "gem_metal": "गोमेद / नारियल जल प्रवाह / भैरव साधना"
        },
        "Ketu": {
            "organs": "त्वचा, सूक्ष्म नसें, रीढ़ का निचला हिस्सा",
            "diseases": "अकस्मात घाव, फोड़े, वायरल संक्रमण, कीड़े का काटना, बवासीर",
            "gem_metal": "लहसुनिया / कंबल दान / गणेश उपासना"
        }
    }

    @classmethod
    def analyze(cls, chart: KundaliChart) -> Dict[str, Any]:
        lagna_sign_id = chart.lagna_sign_id
        lagnesh = SIGN_LORDS[SIGNS[lagna_sign_id - 1]["name_en"]]

        # 1. Overall Vitality Assessment
        sun_pos = chart.planets.get("Sun")
        moon_pos = chart.planets.get("Moon")
        lagnesh_pos = chart.planets.get(lagnesh)

        vitality_score = 75  # base
        if lagnesh_pos and lagnesh_pos.dignity in ("exalted", "own", "moolatrikona"):
            vitality_score += 15
        elif lagnesh_pos and lagnesh_pos.dignity in ("debilitated", "enemy"):
            vitality_score -= 15

        if sun_pos and sun_pos.dignity in ("exalted", "own"):
            vitality_score += 10
        elif sun_pos and sun_pos.dignity == "debilitated":
            vitality_score -= 10

        vitality_score = max(40, min(98, vitality_score))
        vitality_status = "उत्कृष्ट एवं सुदृढ़ (Strong Immunity)" if vitality_score >= 80 else ("मध्यम एवं संतुलित" if vitality_score >= 60 else "संवेदनशील (विशेष देखभाल आवश्यक)")

        # 2. 6th House (Diseases) & 8th House (Chronic Illness)
        h6_sign_id = ((lagna_sign_id + 4) % 12) + 1
        h6_lord = SIGN_LORDS[SIGNS[h6_sign_id - 1]["name_en"]]
        h6_occupants = [p_name for p_name, p in chart.planets.items() if p.house_from_lagna == 6]

        h8_occupants = [p_name for p_name, p in chart.planets.items() if p.house_from_lagna == 8]
        h12_occupants = [p_name for p_name, p in chart.planets.items() if p.house_from_lagna == 12]

        # 3. Identify Afflicted/Sensitive Planets
        vulnerable_areas = []
        for p_name, p in chart.planets.items():
            is_afflicted = False
            reasons = []
            if p.dignity == "debilitated":
                is_afflicted = True
                reasons.append("नीच राशि में स्थित")
            if p.is_combust:
                is_afflicted = True
                reasons.append("सूर्य से अस्त")
            if p.house_from_lagna in (6, 8, 12):
                is_afflicted = True
                reasons.append(f"त्रिक भाव (घर {p.house_from_lagna}) में स्थित")

            if is_afflicted and p_name in cls.GRAHA_BODY_MAPPING:
                meta = cls.GRAHA_BODY_MAPPING[p_name]
                vulnerable_areas.append({
                    "planet": p_name,
                    "reasons": ", ".join(reasons),
                    "organs": meta["organs"],
                    "diseases": meta["diseases"],
                    "remedy": meta["gem_metal"]
                })

        # Future Warning based on 6th & 8th lord
        future_risks = []
        if h6_lord in cls.GRAHA_BODY_MAPPING:
            m6 = cls.GRAHA_BODY_MAPPING[h6_lord]
            future_risks.append(f"षष्ठेश {h6_lord} का प्रभाव: मध्यम आयु में {m6['diseases'].split(',')[0]} या {m6['diseases'].split(',')[1] if len(m6['diseases'].split(',')) > 1 else ''} के प्रति नियमित जांच आवश्यक।")

        if h8_occupants:
            pls_str = ", ".join(h8_occupants)
            future_risks.append(f"अष्टम भाव में स्थित {pls_str}: अकस्मात स्वास्थ्य गिरावट या दुर्घटना से बचाव हेतु वाहन सावधानी से चलाएं और योग-प्राणायाम नियमित रखें।")
        else:
            future_risks.append("अष्टम भाव रिक्त व शांत है — दीर्घायु योग एवं आकस्मिक गंभीर संकटों से सुरक्षा।")

        if not vulnerable_areas:
            # Fallback if chart is exceptionally clean
            vulnerable_areas.append({
                "planet": "Lagna Lord " + lagnesh,
                "reasons": "सामान्य प्राकृतिक चक्र",
                "organs": "संपूर्ण शारीरिक स्फूर्ति",
                "diseases": "मौसमी सर्दी-जुकाम या थकान",
                "remedy": "प्रातः सूर्य दर्शन एवं हल्का योग"
            })

        return {
            "vitality_score": vitality_score,
            "vitality_status": vitality_status,
            "lagnesh": lagnesh,
            "h6_lord": h6_lord,
            "h6_occupants": h6_occupants,
            "h8_occupants": h8_occupants,
            "h12_occupants": h12_occupants,
            "vulnerable_areas": vulnerable_areas,
            "future_risks": future_risks,
            "general_health_advice": "नियमित दिनचर्या, सूर्य नमस्कार, सात्विक आहार और रात्रि में समय पर शयन आपके आरोग्य की कुंजी है।"
        }


# =============================================================================
# 4. PHYSICAL ANATOMY & BODY ENGINE (शारीरिक गठन एवं अंग-विकार)
# =============================================================================

class BodyAnatomyEngine:
    """Determines Physical Constitution, Height/Frame/Complexion traits,

    and analyzes all 12 Kalapurusha Body Limbs for congenital/future marks or sensitivities.
    """

    # 12 Signs Kalapurusha Limbs
    KALAPURUSHA_LIMBS = [
        {"sign_id": 1, "limb_hi": "शिर एवं मस्तिष्क (Head & Brain)", "sign_name": "Aries"},
        {"sign_id": 2, "limb_hi": "मुख, नेत्र, गला, दांत (Face, Eyes, Throat)", "sign_name": "Taurus"},
        {"sign_id": 3, "limb_hi": "कंधे, भुजाएं, बांह, श्वसन नलिका (Shoulders & Arms)", "sign_name": "Gemini"},
        {"sign_id": 4, "limb_hi": "हृदय, छाती, फेफड़े (Chest & Lungs)", "sign_name": "Cancer"},
        {"sign_id": 5, "limb_hi": "ऊपरी पेट, यकृत, पित्ताशय (Upper Abdomen & Liver)", "sign_name": "Leo"},
        {"sign_id": 6, "limb_hi": "आंतें, निचला उदर, नाभि (Intestines & Digestion)", "sign_name": "Virgo"},
        {"sign_id": 7, "limb_hi": "कमर, पेडू, मूत्राशय (Lumbar, Pelvis, Bladder)", "sign_name": "Libra"},
        {"sign_id": 8, "limb_hi": "गुप्तांग, जननांग, गुदा (External Genitals & Vital Organs)", "sign_name": "Scorpio"},
        {"sign_id": 9, "limb_hi": "जांघें, कूल्हे, अस्थि मज्जा (Thighs & Hips)", "sign_name": "Sagittarius"},
        {"sign_id": 10, "limb_hi": "घुटने, संधियां, जोड़ (Knees & Joints)", "sign_name": "Capricorn"},
        {"sign_id": 11, "limb_hi": "पिंडलियां, पैर के टखने, बायां कान (Calves & Ankles)", "sign_name": "Aquarius"},
        {"sign_id": 12, "limb_hi": "पैर, तलवे, बायां नेत्र, लिम्फ (Feet & Toes)", "sign_name": "Pisces"},
    ]

    LAGNA_PHYSIQUE = {
        "Aries": {
            "frame": "मध्यम कद, सुगठित मांसपेशियां, फुर्तीला शरीर",
            "complexion": "लालित्य युक्त गेहुंआ, तीक्ष्ण दृष्टि",
            "facial": "सिर या चेहरे पर तिल, मस्सा या कटने का सूक्ष्म चिन्ह संभव",
            "constitution": "अग्नि तत्व प्रधान, उच्च शारीरिक सहनशक्ति"
        },
        "Taurus": {
            "frame": "मजबूत चौड़ी हड्डियां, गठीला शरीर, मजबूत गर्दन",
            "complexion": "उज्ज्वल, आकर्षक व शांत चेहरा",
            "facial": "सुंदर नैन-नक्श, भरे हुए गाल व आकर्षक मुस्कान",
            "constitution": "पृथ्वी तत्व प्रधान, स्थिर व धैर्यवान चाल-ढाल"
        },
        "Gemini": {
            "frame": "लंबा-पतला कद, लचीला शरीर, सक्रिय हाथ",
            "complexion": "साफ, हल्का सांवला या गेहुंआ",
            "facial": "तेजस्वी आंखें, विचारमग्न भाव, युवा दिखने वाला चेहरा",
            "constitution": "वायु तत्व प्रधान, निरंतर गतिशील रहने की प्रवृत्ति"
        },
        "Cancer": {
            "frame": "मध्यम कद, गोल चेहरा, संवेदनशील शारीरिक बनावट",
            "complexion": "गोरा या दूधिया आभा, कोमल त्वचा",
            "facial": "सौम्य आंखें, चंद्र जैसा गोल मुखड़ा",
            "constitution": "जल तत्व प्रधान, मौसम के प्रति अत्यधिक संवेदनशील"
        },
        "Leo": {
            "frame": "चौड़ा सीना, रोबीला व्यक्तित्व, प्रतापी शारीरिक मुद्रा",
            "complexion": "तेजस्वी, चमकदार आभा, प्रभावशाली उपस्थिति",
            "facial": "सिंह समान गरिमामयी आंखें, चौड़ा ललाट",
            "constitution": "अग्नि तत्व प्रधान, स्वाभाविक नेतृत्वकारी देहयष्टि"
        },
        "Virgo": {
            "frame": "सुडौल, संतुलित कद, सुगठित अंग",
            "complexion": "स्वच्छ, आकर्षक व सौम्य",
            "facial": "बुद्धिमत्ता पूर्ण मुखाकृति, साफ़ नैन-नक्श",
            "constitution": "पृथ्वी तत्व प्रधान, अपनी आयु से कम प्रतीत होने वाला रूप"
        },
        "Libra": {
            "frame": "आनुपातिक (Well-proportioned), सुरुचिपूर्ण, मध्यम-लंबा कद",
            "complexion": "उज्ज्वल, गोरा या साफ गेहुंआ",
            "facial": "अत्यंत सम्मोहक आंखें, डिंपल या गालों पर आकर्षक बनावट",
            "constitution": "वायु तत्व प्रधान, सौंदर्य और शिष्टता की प्रतिमूर्ति"
        },
        "Scorpio": {
            "frame": "मजबूत, चुंबकीय व्यक्तित्व, दृढ़ शारीरिक गठन",
            "complexion": "गहरा गेहुंआ या रहस्यमयी आभा",
            "facial": "तीखी भेदक आंखें जो सीधे मन को पढ़ लें",
            "constitution": "जल तत्व प्रधान, रहस्यमयी आकर्षण एवं अत्यधिक ऊर्जा"
        },
        "Sagittarius": {
            "frame": "लंबा कद, सुडौल जांघें, एथलेटिक व मजबूत ढांचा",
            "complexion": "स्वर्ण आभा युक्त, खुली प्रसन्न मुद्रा",
            "facial": "चौड़ा माथा, आनंदित व दार्शनिक मुखमंडल",
            "constitution": "अग्नि तत्व प्रधान, खेलकूद व यात्राओं के लिए अनुकूल देह"
        },
        "Capricorn": {
            "frame": "गंभीर, दुबला-मजबूत शरीर, कड़ी हड्डियां",
            "complexion": "सांवला या गहरा गेहुंआ, परिपक्व रूप",
            "facial": "गंभीर व धैर्यवान आंखें, दृढ़ ठोड़ी (Jawline)",
            "constitution": "पृथ्वी तत्व प्रधान, अत्यधिक सहनशील व परिश्रमी देह"
        },
        "Aquarius": {
            "frame": "मध्यम से लंबा कद, मजबूत पिंडलियां, विशिष्ट शारीरिक शैली",
            "complexion": "स्वच्छ, विचारवान आभा",
            "facial": "बुद्धिजीवी चेहरा, स्वतंत्र व स्पष्ट दृष्टि",
            "constitution": "वायु तत्व प्रधान, आधुनिक व चुंबकीय व्यक्तित्व"
        },
        "Pisces": {
            "frame": "मध्यम कद, मांसल व कोमल शरीर, सुंदर पैर",
            "complexion": "उज्ज्वल, सौम्य व शांत",
            "facial": "बड़ी करुणामयी मत्स्य समान आंखें",
            "constitution": "जल तत्व प्रधान, आध्यात्मिक व संवेदनशील शारीरिक आभा"
        }
    }

    @classmethod
    def analyze(cls, chart: KundaliChart) -> Dict[str, Any]:
        lagna_sign_id = chart.lagna_sign_id
        lagna_sign_name = SIGNS[lagna_sign_id - 1]["name_en"]
        physique_data = cls.LAGNA_PHYSIQUE.get(lagna_sign_name, cls.LAGNA_PHYSIQUE["Aries"])

        # 12 Limbs Assessment
        limbs_status = []
        for limb in cls.KALAPURUSHA_LIMBS:
            s_id = limb["sign_id"]
            # Find which house corresponds to this sign or where malefic planets sit
            h_from_lagna = ((s_id - lagna_sign_id) % 12) + 1
            occupants = [p_name for p_name, p in chart.planets.items() if p.sign_id == s_id]

            status = "🟢 स्वस्थ एवं सुदृढ़ (Healthy)"
            notes = "सामान्य स्थिति"
            has_malefic = any(p in ["Saturn", "Mars", "Rahu", "Ketu"] for p in occupants)
            has_benefic = any(p in ["Jupiter", "Venus", "Mercury", "Moon"] for p in occupants)

            if has_malefic and not has_benefic:
                status = "🔴 संवेदनशील / दुर्बल (Afflicted/Vulnerable)"
                notes = f"पापग्रह {', '.join(occupants)} की उपस्थिति: इस अंग में चोट, दर्द या खिंचाव की संवेदनशीलता।"
            elif has_malefic and has_benefic:
                status = "🟡 मिश्रित प्रभाव (Moderate)"
                notes = f"मिश्रित ग्रह ({', '.join(occupants)}): समय-समय पर देखभाल आवश्यक।"
            elif has_benefic:
                status = "✨ विशेष शुभ एवं सशक्त (Protected)"
                notes = f"शुभ ग्रह {', '.join(occupants)} द्वारा पोषित।"

            limbs_status.append({
                "sign_id": s_id,
                "limb_hi": limb["limb_hi"],
                "house_from_lagna": f"भाव {h_from_lagna}",
                "occupants": ", ".join(occupants) if occupants else "—",
                "status": status,
                "notes": notes
            })

        # Congenital Marks (तिल / मस्सा / जन्मजात चिन्ह)
        # BPHS Rule: Malefics in Lagna or 6th house indicate scars or marks
        congenital_marks = []
        h1_occupants = [p_name for p_name, p in chart.planets.items() if p.house_from_lagna == 1]
        if "Mars" in h1_occupants:
            congenital_marks.append("मस्तक, चेहरे या भौंहों के पास तिल, कटने का हल्का निशान या बचपन की चोट का चिन्ह संभव।")
        if "Saturn" in h1_occupants:
            congenital_marks.append("चेहरे या दाहिने कंधे पर गहरा तिल या मस्सा होना संभव।")
        if "Rahu" in h1_occupants:
            congenital_marks.append("सिर के पिछले हिस्से, गले या होंठों के आसपास तिल या जन्मजात चिन्ह।")
        if not congenital_marks:
            congenital_marks.append("शरीर पर स्वाभाविक सौंदर्य व संतुलित चिन्ह हैं; कोई हानिकारक जन्मजात विकार नहीं है।")

        return {
            "lagna_sign": lagna_sign_name,
            "physique": physique_data,
            "limbs_status": limbs_status,
            "congenital_marks": congenital_marks,
            "core_advice": "प्रतिदिन सूर्योदय के समय योग, नियमित तेल मालिश (अभ्यंग) और शारीरिक मुद्रा (Posture) सीधी रखने से आपका शारीरिक तेज सदा बना रहेगा।"
        }
