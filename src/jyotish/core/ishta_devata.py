"""
Classical Ishta Devata, Dharma Devata, Kula Devata, Pooja Vidhan,
and Vrat / Upavasa Engine for JyotishOS.
Rooted in:
- Maharishi Jaimini Upadesha Sutras (Adhyaya 1, Pada 2: Karakamsha & 12th Bhava Jivanmukti)
- Brihat Parashara Hora Shastra (BPHS: Ch. 33 Karakamsha Phala & Ch. 32 Atmakaraka)
- Narada Purana & Agni Purana (Mantra Japa, Mala, Pooja Vidhana)
- Nirnaya Sindhu & Dharma Sindhu (Vrat, Upavasa, Tithi & Vara Niyama)
"""

from typing import Dict, List, Tuple, Optional, Any
from .constants import (
    SIGNS, SIGN_NAMES, SIGN_LORDS, GRAHAS
)
from .models import KundaliChart, PlanetPosition


class IshtaDevataEngine:
    """Calculates Ishta Devata (from 12th of Karakamsha in D9), Dharma Devata,

    Mantra Devata, Kula Devata, Daily Pooja Vidhi, Mantras, and Auspicious Vrats.
    """

    # Classical Planetary Deities according to Jaimini Sutras 1.2.72-85 & BPHS
    DEITY_ATTRIBUTES = {
        "Sun": {
            "ishta_hi": "भगवान सूर्य नारायण / श्री रामचन्द्र जी / गायत्री माता / शिव",
            "ishta_en": "Lord Surya Narayana / Lord Rama / Shiva / Gayatri Devi",
            "form_desc_hi": "तेजस्वी, पराक्रमी एवं मर्यादा पुरुषोत्तम स्वरूप; आत्मिक तेज एवं आरोग्य प्रदान करने वाले।",
            "primary_mantra": "ॐ ह्रां ह्रीं ह्रौं सः सूर्याय नमः || अथवा || ॐ घृणि सूर्याय नमः || अथवा || ॐ रां रामाय नमः",
            "beej_mantra": "ॐ ह्रां ह्रीं ह्रौं सः",
            "mala": "रुद्राक्ष माला (Rudraksha) अथवा रक्त चन्दन माला (Red Sandalwood)",
            "flowers": "लाल कमल, लाल गुड़हल (मंदार) या लाल गुलाब",
            "incense_dhoop": "गुग्गुल, लोबान एवं शुद्ध गाय का घी का दीपक",
            "deepa_oil": "शुद्ध गाय का घी (Pure Cow Ghee)",
            "naivedya_bhog": "गेहूं का हलवा, गुड़-रोटी, खीर, लाल फल (अनार/सेब)",
            "direction": "पूर्व दिशा (East) अथवा ईशान कोण (North-East)",
            "vrat_day": "रविवार (Sunday)",
            "vrat_tithi": "शुक्ल पक्ष सप्तमी, रथ सप्तमी, भानु सप्तमी",
            "vrat_rules_hi": "नमक का त्याग रखें, केवल मीठा भोजन या दलिया लें। सूर्योदय के समय तांबे के लोटे से अर्घ्य दें।",
            "spiritual_fruit_hi": "आत्मबल, यश-कीर्ति, सरकारी कार्यों में सफलता, नेत्र व हृदय आरोग्य तथा पितृ-ऋण मुक्ति।"
        },
        "Moon": {
            "ishta_hi": "माता गौरी / ललिता त्रिपुरसुंदरी / भगवान श्री कृष्ण / शिव-पार्वती",
            "ishta_en": "Goddess Gauri / Lalita Tripurasundari / Lord Krishna / Shiva-Parvati",
            "form_desc_hi": "सौम्य, वात्सल्यमयी एवं करुणामयी स्वरूप; मन की शांति, एकाग्रता एवं सुख-शांति प्रदायक।",
            "primary_mantra": "ॐ सों सोमाय नमः || अथवा || ॐ क्लीं कृष्णाय गोविंदाय गोपीजनवल्लभाय नमः || अथवा || ॐ नमः शिवाय",
            "beej_mantra": "ॐ श्रां श्रीं श्रौं सः चन्द्रमसे नमः",
            "mala": "सफेद स्फटिक माला (Quartz Crystal) अथवा मोती माला (Pearl) या कमलगट्टा",
            "flowers": "सफेद कमल, चमेली, मोगरा, चांदनी या बेला",
            "incense_dhoop": "चन्दन धूप एवं कपूर आरती",
            "deepa_oil": "गाय का घी अथवा तिल का तेल",
            "naivedya_bhog": "चावल की खीर, माखन-मिश्री, बताशा, दूध-पेड़ा",
            "direction": "वायव्य कोण (North-West) अथवा ईशान (North-East)",
            "vrat_day": "सोमवार (Monday)",
            "vrat_tithi": "पूर्णिमा (Purnima) अथवा संकष्टी चतुर्थी",
            "vrat_rules_hi": "दूध, दही, फल आधारित अल्पाहार रखें; रात्रि में चंद्रोदय पर जल देकर फलाहार करें।",
            "spiritual_fruit_hi": "मानसिक शांति, तनाव-अनिद्रा से मुक्ति, पारिवारिक सौहार्द, मातृ सुख एवं भक्ति सिद्धि।"
        },
        "Mars": {
            "ishta_hi": "श्री हनुमान जी / भगवान कार्तिकेय (स्कंद) / नृसिंह भगवान / माँ बगलामुखी",
            "ishta_en": "Lord Hanuman / Lord Kartikeya (Murugan) / Narasimha / Maa Baglamukhi",
            "form_desc_hi": "परम पराक्रमी, संकटमोचक एवं शत्रुहंता स्वरूप; समस्त भयों व बाधाओं का नाश करने वाले।",
            "primary_mantra": "ॐ हं हनुमते रुद्रात्मकाय हुं फट् || अथवा || ॐ नमो भगवते नारसिंहाय || अथवा || ॐ क्रौं भौमाय नमः",
            "beej_mantra": "ॐ क्रां क्रीं क्रौं सः भौमाय नमः",
            "mala": "मूंगा माला (Red Coral) अथवा रक्त चन्दन माला (Red Sandalwood)",
            "flowers": "लाल कनेर, लाल गुलाब, गेंदा या तुलसी दल",
            "incense_dhoop": "गुग्गुल, कपूर एवं चमेली के तेल का सिंदूरी दीप",
            "deepa_oil": "चमेली का तेल (Jasmine Oil) अथवा तिल का तेल",
            "naivedya_bhog": "बूंदी के लड्डू, गुड़-चना, चूरमा, अनार",
            "direction": "दक्षिण दिशा (South) अथवा पूर्व दिशा",
            "vrat_day": "मंगलवार (Tuesday)",
            "vrat_tithi": "हनुमान जयंती, भौम प्रदोष, कृष्ण पक्ष चतुर्दशी",
            "vrat_rules_hi": "नमक वर्जित; केवल एक समय शाम को मीठा हलवा या फल लें। हनुमान चालीसा व सुंदरकांड का पाठ करें।",
            "spiritual_fruit_hi": "शत्रुओं पर विजय, भयमुक्ति, रक्तविकार शांति, पराक्रम वृद्धि एवं भूमि-भवन लाभ।"
        },
        "Mercury": {
            "ishta_hi": "भगवान श्री हरि विष्णु / नारायण / माँ दुर्गा / श्री गणेश",
            "ishta_en": "Lord Maha Vishnu / Narayana / Goddess Durga / Lord Ganesha",
            "form_desc_hi": "ज्ञानानंदमय, चतुर्भुज शंख-चक्र-गदा-पद्म धारी स्वरूप; मेधा, वाणी एवं सद्बुद्धि प्रदायक।",
            "primary_mantra": "ॐ नमो भगवते वासुदेवाय || अथवा || ॐ विष्णवे नमः || अथवा || ॐ ऐं ह्रीं क्लीं चामुण्डायै विच्चे",
            "beej_mantra": "ॐ ब्रां ब्रीं ब्रौं सः बुधाय नमः",
            "mala": "तुलसी माला (Tulsi Beads) अथवा हरी हकीक माला (Green Agate)",
            "flowers": "दूर्वा (दूब घास), पीले गेंदे के फूल, अपराजिता (नीले फूल)",
            "incense_dhoop": "तुलसी-चन्दन अगरबत्ती एवं घी का दीपक",
            "deepa_oil": "शुद्ध गाय का घी",
            "naivedya_bhog": "पंचामृत, पंजीरी, तुलसी पत्र, मूंग के लड्डू, हरे फल",
            "direction": "उत्तर दिशा (North) अथवा ईशान कोण",
            "vrat_day": "बुधवार (Wednesday)",
            "vrat_tithi": "एकादशी (Ekadashi) अथवा दुर्गाष्टमी",
            "vrat_rules_hi": "हरी मूंग की दाल व दलिया आधारित भोजन; अन्न का दान करें व विष्णु सहस्रनाम का पाठ करें।",
            "spiritual_fruit_hi": "बुद्धि-विवेक, वाणी सिद्धि, व्यापार-व्यवसाय में उन्नति, विद्या लाभ एवं विघ्न शांति।"
        },
        "Jupiter": {
            "ishta_hi": "भगवान सदाशिव / श्री हरि विष्णु / भगवान दत्तात्रेय / दक्षिणामूर्ति / देवगुरु",
            "ishta_en": "Lord Sadashiva / Maha Vishnu / Dattatreya / Dakshinamurti / Brihaspati",
            "form_desc_hi": "ब्रह्मज्ञानी, सौम्य गुरु स्वरूप; परम ज्ञान, मोक्ष, धर्म एवं सन्तान सुख के दाता।",
            "primary_mantra": "ॐ नमो भगवते दक्षिणामूर्तये मह्यं मेधां प्रज्ञां प्रयच्छ स्वाहा || अथवा || ॐ ग्रां ग्रीं ग्रौं सः गुरवे नमः",
            "beej_mantra": "ॐ ग्रां ग्रीं ग्रौं सः",
            "mala": "हल्दी माला (Turmeric Mala) अथवा पीले चंदन की माला या पंचमुखी रुद्राक्ष",
            "flowers": "पीले कनेर, पीला गेंदा, पीला गुलाब या कमल",
            "incense_dhoop": "केसर-चंदन धूप एवं घी का दीपक",
            "deepa_oil": "गाय का शुद्ध घी (Pure Cow Ghee)",
            "naivedya_bhog": "चने की दाल व गुड़, बेसन के लड्डू, पीले पके केले, केसर खीर",
            "direction": "ईशान कोण (North-East — देव कोण)",
            "vrat_day": "गुरुवार (Thursday)",
            "vrat_tithi": "एकादशी (Ekadashi) अथवा गुरु पूर्णिमा",
            "vrat_rules_hi": "पीले वस्त्र पहनें; नमक रहित चना-बेसन का पीला भोजन लें; केले के वृक्ष में जल व हल्दी अर्पित करें।",
            "spiritual_fruit_hi": "उच्च विद्या, संतान सुख, मान-सम्मान, दांपत्य शांति, आध्यात्मिक उन्नति एवं गुरु कृपा।"
        },
        "Venus": {
            "ishta_hi": "माता महालक्ष्मी / राधा रानी / माँ अन्नपूर्णा / भुवनेश्वरी",
            "ishta_en": "Goddess Mahalakshmi / Radha Rani / Maa Annapurna / Bhuvaneshwari",
            "form_desc_hi": "अष्टैश्वर्य प्रदायिनी, स्वर्णिम आभा युक्त माँ लक्ष्मी स्वरूप; धन, वैभव, सौंदर्य व सुखदात्री।",
            "primary_mantra": "ॐ श्रीं ह्रीं क्लीं त्रिभुवन महालक्ष्म्यै अस्मांक दारिद्र्य नाशय प्रचुर धन देहि देहि क्लीं ह्रीं श्रीं ॐ || अथवा || ॐ द्रां द्रीं द्रौं सः शुक्राय नमः",
            "beej_mantra": "ॐ द्रां द्रीं द्रौं सः",
            "mala": "कमलगट्टा माला (Lotus Seed) अथवा स्फटिक माला (Clear Quartz)",
            "flowers": "गुलाबी/सफेद कमल, लाल गुलाब, सुगंधित मोगरा",
            "incense_dhoop": "गुलाब-चंदन धूप, अष्टगंध एवं घी का दीपक",
            "deepa_oil": "गाय का घी अथवा तिल तेल",
            "naivedya_bhog": "मिश्री, खीर, सफेद बताशे, काजू कतली, मखाने की खीर",
            "direction": "आग्नेय कोण (South-East) अथवा पूर्व दिशा",
            "vrat_day": "शुक्रवार (Friday)",
            "vrat_tithi": "वैभव लक्ष्मी व्रत, पूर्णिमा, नवरात्रि",
            "vrat_rules_hi": "सफेद वस्त्र धारण करें; खटाई का सर्वथा त्याग रखें; शाम को खीर का भोग लगाकर कन्या पूजन करें।",
            "spiritual_fruit_hi": "अखण्ड धन-संपदा, वाहन-भवन सुख, वैवाहिक आनंद, कला-सौंदर्य में सिद्धि एवं आकर्षण बल।"
        },
        "Saturn": {
            "ishta_hi": "भगवान कालभैरव / श्री हनुमान जी / शनिदेव / भगवान शिव (महाकाल)",
            "ishta_en": "Lord Kalabhairava / Hanuman Ji / Shani Deva / Mahakala Shiva",
            "form_desc_hi": "न्यायप्रिय, वैराग्यमय एवं तपस्वी स्वरूप; कर्म सुधारक, अहंकार नाशक एवं मोक्ष प्रदायक।",
            "primary_mantra": "ॐ प्रां प्रीं प्रौं सः शनैश्चराय नमः || अथवा || ॐ भं भैरवाय नमः || अथवा || ॐ शं शनैश्चराय नमः",
            "beej_mantra": "ॐ प्रां प्रीं प्रौं सः",
            "mala": "रुद्राक्ष माला (Rudraksha) अथवा नीले हकीक की माला",
            "flowers": "नीले अपराजिता के फूल, नीले कमल या जामुनी फूल",
            "incense_dhoop": "गुग्गुल, लोबान एवं सरसों/तिल के तेल का अखंड दीपक",
            "deepa_oil": "सरसों का तेल (Mustard Oil) अथवा काले तिल का तेल",
            "naivedya_bhog": "उड़द की दाल की खिचड़ी, तिल-गुड़ के लड्डू, इमरती, काले चने",
            "direction": "पश्चिम दिशा (West)",
            "vrat_day": "शनिवार (Saturday)",
            "vrat_tithi": "शनि अमावस्या, प्रदोष व्रत, कालभैरवाष्टमी",
            "vrat_rules_hi": "सूर्यास्त के बाद एक समय तिल-उड़द का सादा भोजन करें; पीपल के नीचे दीप दान करें; असहायों की सेवा करें।",
            "spiritual_fruit_hi": "साढ़ेसाती व ढैया से रक्षा, दीर्घायु, असाध्य रोगों का नाश, स्थिर संपत्ति एवं वैराग्य सिद्धि।"
        },
        "Rahu": {
            "ishta_hi": "माता दुर्गा / महाकाली / माता सरस्वती / भैरव देव",
            "ishta_en": "Maa Durga / Mahakali / Saraswati / Bhairava",
            "form_desc_hi": "असुर संहारिणी, महिषासुरमर्दिनी, दुष्ट-दलन रूप; माया एवं भ्रम को नष्ट कर सत्य ज्ञान देने वाली।",
            "primary_mantra": "ॐ ऐं ह्रीं क्लीं चामुण्डायै विच्चे || अथवा || ॐ भ्रां भ्रीं भ्रौं सः राहवे नमः",
            "beej_mantra": "ॐ भ्रां भ्रीं भ्रौं सः",
            "mala": "रुद्राक्ष माला अथवा काली हकीक माला",
            "flowers": "नीले फूल, लाल गुड़हल या कनेर",
            "incense_dhoop": "गुग्गुल, लोबान एवं सरसों के तेल का दीपक",
            "deepa_oil": "तिल का तेल अथवा सरसों का तेल",
            "naivedya_bhog": "उड़द के बड़े, नारियल, गुड़, काले तिल के लड्डू",
            "direction": "नैऋत्य कोण (South-West)",
            "vrat_day": "शनिवार अथवा बुधवार",
            "vrat_tithi": "दुर्गाष्टमी, नवरात्रि, कालरात्रि",
            "vrat_rules_hi": "दुर्गा सप्तशती का पाठ करें; पक्षियों को दाना दें; तामसिक आहार से सर्वथा दूर रहें।",
            "spiritual_fruit_hi": "भ्रम, भय व तंत्र-बाधा से मुक्ति, अचानक लाभ, कूटनीति में सफलता एवं मानसिक संबल।"
        },
        "Ketu": {
            "ishta_hi": "भगवान श्री गणेश / मत्स्य अवतार / भगवान शिव (अवधूत स्वरूप)",
            "ishta_en": "Lord Ganesha / Matsya Avatar / Lord Shiva (Avadhuta)",
            "form_desc_hi": "विघ्नहर्ता, मोक्षदाता, गजानन स्वरूप; परम कैवल्य, सूक्ष्म दृष्टि एवं मोक्ष प्रदान करने वाले।",
            "primary_mantra": "ॐ गं गणपतये नमः || अथवा || ॐ स्त्रां स्त्रीं स्त्रौं सः केतवे नमः || अथवा || ॐ वक्रतुण्डाय हुम्",
            "beej_mantra": "ॐ स्त्रां स्त्रीं स्त्रौं सः",
            "mala": "रुद्राक्ष माला अथवा हल्दी माला",
            "flowers": "२१ दूर्वा दल (दूब), लाल गुड़हल या पीले गेंदे के फूल",
            "incense_dhoop": "चन्दन धूप एवं घी का दीपक",
            "deepa_oil": "शुद्ध गाय का घी अथवा तिल तेल",
            "naivedya_bhog": "मोदक, मोतीचूर के लड्डू, केला, पंचमेवा",
            "direction": "वायव्य अथवा ईशान कोण",
            "vrat_day": "मंगलवार अथवा बुधवार",
            "vrat_tithi": "संकष्टी चतुर्थी, विनायक चतुर्थी, गणेश जन्मोत्सव",
            "vrat_rules_hi": "दिनभर निराहार या फलाहार रहें; चंद्रोदय के समय गणेश जी को अर्घ्य देकर मोदक से पारण करें।",
            "spiritual_fruit_hi": "परम मोक्ष, समस्त विघ्नों का अंत, आध्यात्मिक सिद्धियां, अंतर्ज्ञान (Intuition) एवं कुण्डलिनी जागरण।"
        }
    }

    @classmethod
    def analyze(cls, chart: KundaliChart) -> Dict[str, Any]:
        """Scans the computed natal chart and Navamsha (D9) to extract:

        1. Atmakaraka (AK) and Karakamsha
        2. 12th house from Karakamsha in D9 (Ishta Devata / Moksha)
        3. 9th house from Karakamsha (Dharma Devata)
        4. 5th house from Lagna & Karakamsha (Mantra Devata)
        5. 2nd house from Lagna (Kula Devata / Kula Devi)
        6. Complete Pooja Vidhi, Mantras, Japa Mala & Vrat Niyama
        """
        ak_planet = chart.atmakaraka or "Sun"

        # 1. Determine Karakamsha Sign ID in D9
        karakamsha_s_id = 1
        karakamsha_s_name = "Aries"
        if chart.jaimini and chart.jaimini.karakamsha_sign_id:
            karakamsha_s_id = chart.jaimini.karakamsha_sign_id
            karakamsha_s_name = chart.jaimini.karakamsha_sign_name
        elif "D9" in chart.vargas and ak_planet in chart.vargas["D9"].planets:
            karakamsha_s_id = chart.vargas["D9"].planets[ak_planet].sign_id
            karakamsha_s_name = chart.vargas["D9"].planets[ak_planet].sign_name
        else:
            # Fallback to AK sign in D1
            karakamsha_s_id = chart.planets[ak_planet].sign_id
            karakamsha_s_name = chart.planets[ak_planet].sign_name

        # 2. 12th House from Karakamsha in D9 (The Ishta Devata / Moksha Bhava)
        h12_from_kk_id = ((karakamsha_s_id - 1 + 11) % 12) + 1
        h12_from_kk_name = SIGN_NAMES[h12_from_kk_id - 1]
        h12_from_kk_lord = SIGN_LORDS[h12_from_kk_name]

        # Check occupants in 12th from Karakamsha in D9
        d9_chart = chart.vargas.get("D9")
        d9_h12_occupants = []
        if d9_chart:
            for p_name, vp in d9_chart.planets.items():
                if vp.sign_id == h12_from_kk_id:
                    d9_h12_occupants.append(p_name)

        # Decide Primary Ishta Planet
        if d9_h12_occupants:
            # If multiple, take strongest (e.g. Ketu takes precedence for Moksha in Jaimini, else first benefic/strongest)
            if "Ketu" in d9_h12_occupants:
                ishta_planet = "Ketu"
            elif "Jupiter" in d9_h12_occupants:
                ishta_planet = "Jupiter"
            elif "Sun" in d9_h12_occupants:
                ishta_planet = "Sun"
            else:
                ishta_planet = d9_h12_occupants[0]
            ishta_reason = f"नवांश (D9) में कारकांश ({karakamsha_s_name}) से १२वें भाव ({h12_from_kk_name}) में {', '.join(d9_h12_occupants)} स्थित हैं।"
        else:
            ishta_planet = h12_from_kk_lord
            ishta_reason = f"नवांश (D9) में कारकांश ({karakamsha_s_name}) से १२वें भाव ({h12_from_kk_name}) में कोई ग्रह नहीं है, अतः इस भाव के स्वामी ग्रह {h12_from_kk_lord} इष्ट नियामक हैं।"

        # 3. 9th House from Karakamsha in D9 (Dharma Devata)
        h9_from_kk_id = ((karakamsha_s_id - 1 + 8) % 12) + 1
        h9_from_kk_name = SIGN_NAMES[h9_from_kk_id - 1]
        h9_from_kk_lord = SIGN_LORDS[h9_from_kk_name]
        d9_h9_occupants = []
        if d9_chart:
            for p_name, vp in d9_chart.planets.items():
                if vp.sign_id == h9_from_kk_id:
                    d9_h9_occupants.append(p_name)
        dharma_planet = d9_h9_occupants[0] if d9_h9_occupants else h9_from_kk_lord

        # 4. 5th House from Lagna (Mantra Devata / Purva Punya)
        lagna_s_id = chart.lagna_sign_id
        h5_lagna_id = ((lagna_s_id - 1 + 4) % 12) + 1
        h5_lagna_name = SIGN_NAMES[h5_lagna_id - 1]
        h5_lagna_lord = SIGN_LORDS[h5_lagna_name]
        h5_occupants = [p_name for p_name, p in chart.planets.items() if p.house_from_lagna == 5]
        mantra_planet = h5_occupants[0] if h5_occupants else h5_lagna_lord

        # 5. 2nd House from Lagna (Kula Devata / Kula Devi)
        h2_lagna_id = ((lagna_s_id - 1 + 1) % 12) + 1
        h2_lagna_name = SIGN_NAMES[h2_lagna_id - 1]
        h2_lagna_lord = SIGN_LORDS[h2_lagna_name]
        kula_planet = h2_lagna_lord

        # Retrieve Deity Profiles
        ishta_info = cls.DEITY_ATTRIBUTES.get(ishta_planet, cls.DEITY_ATTRIBUTES["Jupiter"])
        dharma_info = cls.DEITY_ATTRIBUTES.get(dharma_planet, cls.DEITY_ATTRIBUTES["Sun"])
        mantra_info = cls.DEITY_ATTRIBUTES.get(mantra_planet, cls.DEITY_ATTRIBUTES["Mercury"])
        kula_info = cls.DEITY_ATTRIBUTES.get(kula_planet, cls.DEITY_ATTRIBUTES["Venus"])

        return {
            "atmakaraka": ak_planet,
            "karakamsha_sign": karakamsha_s_name,
            "h12_sign": h12_from_kk_name,
            "h12_lord": h12_from_kk_lord,
            "ishta_planet": ishta_planet,
            "ishta_reason": ishta_reason,
            "ishta_deity": ishta_info["ishta_hi"],
            "ishta_deity_en": ishta_info["ishta_en"],
            "ishta_form": ishta_info["form_desc_hi"],
            "ishta_mantra": ishta_info["primary_mantra"],
            "ishta_beej": ishta_info["beej_mantra"],
            "ishta_mala": ishta_info["mala"],
            "ishta_flowers": ishta_info["flowers"],
            "ishta_dhoop": ishta_info["incense_dhoop"],
            "ishta_deepa": ishta_info["deepa_oil"],
            "ishta_naivedya": ishta_info["naivedya_bhog"],
            "ishta_direction": ishta_info["direction"],
            "ishta_vrat_day": ishta_info["vrat_day"],
            "ishta_vrat_tithi": ishta_info["vrat_tithi"],
            "ishta_vrat_rules": ishta_info["vrat_rules_hi"],
            "ishta_fruit": ishta_info["spiritual_fruit_hi"],
            "dharma_planet": dharma_planet,
            "dharma_deity": dharma_info["ishta_hi"],
            "mantra_planet": mantra_planet,
            "mantra_deity": mantra_info["ishta_hi"],
            "mantra_sadhana": mantra_info["primary_mantra"],
            "kula_planet": kula_planet,
            "kula_deity": kula_info["ishta_hi"]
        }
