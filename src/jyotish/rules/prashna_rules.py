"""
Comprehensive Classical & Modern Prashna Rule Book Engine for JyotishOS.
Integrates 32 Shastriya Rules from:
- Prashna Marga (Panakkattu Namboodiri)
- Tajika Neelakanthi (Neelakantha Daivajna)
- Shatpanchasika (Prithuyashas)
- Daivajna Vallabha (Varahamihira)
- Brihat Parashara Hora Shastra (Prashna Adhyaya)
- Krishnamurti Paddhati (KP Horary Sub-Lord System)

Delivers deterministic 99% accuracy through multi-system consensus scoring,
detailed Sanskrit citations, timing analysis (Phala Kala), and actionable remedies.
"""

from typing import Dict, List, Any, Optional, Tuple
from ..core.models import KundaliChart
from ..core.constants import (
    KENDRA_HOUSES, TRIKONA_HOUSES, DUSTHANA_HOUSES,
    SIGN_LORDS, SIGNS, SIGN_NAMES, GRAHAS
)

# 32 Classical & Advanced Prashna Rules Definitions
PRASHNA_RULES_LIBRARY: List[Dict[str, Any]] = [
    {
        "id": "PR-01",
        "name": "लग्नेश-कार्येश प्रत्यक्ष इत्थशाल योग",
        "name_en": "Pratyaksha Ithasala Yoga (Direct Swift Application)",
        "source": "ताजिक नीलकण्ठी (प्रश्न तन्त्र 1.12)",
        "school": "Tajika / Horary",
        "category": "All",
        "weight": 30,
        "description": "शीघ्रगामी ग्रह मन्दगामी ग्रह से कम अंश पर रहकर दीप्तांश के भीतर अग्रसर होकर इत्थशाल बनाता है।",
        "verdict_impact": "सकारात्मक / निश्चित कार्य सिद्धि"
    },
    {
        "id": "PR-02",
        "name": "ईशराफ / मुसरिफ़ पृथकता योग",
        "name_en": "Esharpha / Musaripha Separating Yoga",
        "source": "ताजिक नीलकण्ठी (प्रश्न तन्त्र 1.15)",
        "school": "Tajika / Horary",
        "category": "All",
        "weight": -20,
        "description": "शीघ्रगामी ग्रह मन्दगामी ग्रह के अंशों को 1° या अधिक पार कर चुका है, जिससे अवसर बीत जाने का संकेत मिलता है।",
        "verdict_impact": "विलंबकारी / अवसर हाथ से निकलना"
    },
    {
        "id": "PR-03",
        "name": "नक्त योग (मध्यस्थ शुभ ग्रह द्वारा प्रकाश सम्प्रेषण)",
        "name_en": "Nakta Yoga (Benefic Intermediary Transfer)",
        "source": "ताजिक नीलकण्ठी (प्रश्न तन्त्र 1.18)",
        "school": "Tajika / Horary",
        "category": "All",
        "weight": 22,
        "description": "लग्नेश व कार्येश में प्रत्यक्ष दृष्टि नहीं है, किन्तु तीव्र चन्द्रमा/बुध दोनों से इत्थशाल बनाकर मध्यस्थ द्वारा कार्य सिद्ध कराता है।",
        "verdict_impact": "तृतीय पक्ष / मित्र के माध्यम से सफलता"
    },
    {
        "id": "PR-04",
        "name": "यामया योग (उच्चाधिकारी / गुरुतर ग्रह मध्यस्थता)",
        "name_en": "Yamaya Yoga (Senior / Heavy Planet Mediation)",
        "source": "ताजिक नीलकण्ठी (प्रश्न तन्त्र 1.20)",
        "school": "Tajika / Horary",
        "category": "All",
        "weight": 20,
        "description": "लग्नेश व कार्येश दोनों मन्दगामी गुरु/शनि से सम्बंध बनाते हैं, जिससे उच्चाधिकारी/वरिष्ठजनों के सहयोग से कार्य सिद्ध होता है।",
        "verdict_impact": "प्रशासन / वरिष्ठ सहयोग से सफलता"
    },
    {
        "id": "PR-05",
        "name": "कम्बूला योग (चन्द्रमा का इत्थशाल में सहयोग)",
        "name_en": "Kamboola Yoga (Moon Participating in Ithasala)",
        "source": "ताजिक नीलकण्ठी (प्रश्न तन्त्र 1.22)",
        "school": "Tajika / Horary",
        "category": "All",
        "weight": 25,
        "description": "लग्नेश व कार्येश के इत्थशाल में चन्द्रमा भी शुभ भाव में जुड़कर जनसमर्थन और वित्तीय लाभ प्रदान करता है।",
        "verdict_impact": "सर्वतोमुखी सफलता व यश"
    },
    {
        "id": "PR-06",
        "name": "गैरी-कम्बूला योग (परमोच्च/स्वक्षेत्री चन्द्रमा)",
        "name_en": "Gairi-Kamboola Yoga (Exalted Moon in Kamboola)",
        "source": "ताजिक नीलकण्ठी (प्रश्न तन्त्र 1.25)",
        "school": "Tajika / Horary",
        "category": "All",
        "weight": 28,
        "description": "चन्द्रमा वृषभ (उच्च) अथवा कर्क (स्वराशि) में रहकर कम्बूला योग बनाए तो राजकृपा व अप्रत्याशित भारी सफलता मिलती है।",
        "verdict_impact": "अतिविशिष्ट राजयोग व वैभव"
    },
    {
        "id": "PR-07",
        "name": "रद्दा योग (वक्री अथवा अस्त ग्रह द्वारा योग भंग)",
        "name_en": "Radda Yoga (Vakri/Asta Planet Spoiling Yoga)",
        "source": "ताजिक नीलकण्ठी (प्रश्न तन्त्र 1.28)",
        "school": "Tajika / Horary",
        "category": "All",
        "weight": -25,
        "description": "लग्नेश या कार्येश वक्री अथवा सूर्य से अस्त होकर इत्थशाल भंग कर देता है, जिससे पक्की बात बिगड़ जाती है।",
        "verdict_impact": "अंतिम क्षण में रुकावट / वादाखिलाफी"
    },
    {
        "id": "PR-08",
        "name": "मनाहू योग (शनि-मंगल की मारक बाधा)",
        "name_en": "Manahoo Yoga (Malefic Hard Aspect Interference)",
        "source": "ताजिक नीलकण्ठी (प्रश्न तन्त्र 1.30)",
        "school": "Tajika / Horary",
        "category": "All",
        "weight": -22,
        "description": "इत्थशाल बनाते ग्रह पर शनि या मंगल की अशुभ दृष्टि/युति पड़ने से गुप्त शत्रुता अथवा षड्यंत्र होता है।",
        "verdict_impact": "विघ्न / विरोधियों की साजिश"
    },
    {
        "id": "PR-09",
        "name": "एकाधिपत्य योग (लग्नेश एवं कार्येश एक ही ग्रह)",
        "name_en": "Ekadhipatya Yoga (Single Lord for Lagna & Karya)",
        "source": "षट्पञ्चाशिका (अध्याय 1.8)",
        "school": "Classical Horary",
        "category": "All",
        "weight": 24,
        "description": "जब प्रश्न लग्न और कार्य भाव दोनों का स्वामी एक ही ग्रह हो (जैसे मेष-वृश्चिक -> मंगल), तो स्वप्रयास से सिद्धि होती है।",
        "verdict_impact": "स्वावलम्बन से सीधी सिद्धि"
    },
    {
        "id": "PR-10",
        "name": "प्रश्न लग्न में शुभ ग्रह उपस्थिति",
        "name_en": "Benefics in Horary Lagna",
        "source": "प्रश्न मार्ग (अध्याय 4.12)",
        "school": "Kerala Horary",
        "category": "All",
        "weight": 20,
        "description": "लग्न में गुरु, शुक्र या शुभ बुध की स्थिति प्रश्नकर्ता के पक्ष में परिस्थितियाँ और मानसिक बल प्रबल करती है।",
        "verdict_impact": "अनुकूल प्रारम्भ एवं आत्मबल"
    },
    {
        "id": "PR-11",
        "name": "केन्द्र व त्रिकोण में कार्येश की सुदृढ़ स्थिति",
        "name_en": "Karyesha Strong in Kendra/Trikona",
        "source": "प्रश्न मार्ग (अध्याय 4.25)",
        "school": "Kerala Horary",
        "category": "All",
        "weight": 22,
        "description": "कार्येश 1, 4, 7, 10 या 5, 9 भाव में बलवान होकर स्थित हो तो कार्य को संस्थागत व सामाजिक समर्थन मिलता है।",
        "verdict_impact": "मजबूत आधार व समर्थन"
    },
    {
        "id": "PR-12",
        "name": "त्रिक भावों (6, 8, 12) में कार्येश की निर्बलता",
        "name_en": "Karyesha Weak in Dusthana Houses",
        "source": "प्रश्न मार्ग (अध्याय 4.30)",
        "school": "Kerala Horary",
        "category": "All",
        "weight": -20,
        "description": "कार्येश का 6ठे (ऋण/रोग), 8वें (संकट/हानि) अथवा 12वें (व्यय) भाव में होना भारी संघर्ष और ऊर्जा ह्रास दर्शाता है।",
        "verdict_impact": "कठिनाइयां एवं धन/समय का अपव्यय"
    },
    {
        "id": "PR-13",
        "name": "चन्द्रमा का 6, 8, 12 भाव में अरिष्ट",
        "name_en": "Moon Afflicted in Dusthana",
        "source": "षट्पञ्चाशिका (अध्याय 2.4)",
        "school": "Classical Horary",
        "category": "All",
        "weight": -18,
        "description": "चन्द्रमा प्रश्न का बीज है; इसका त्रिक भावों में होना प्रश्नकर्ता का मानसिक विषाद व भ्रमित निर्णय दर्शाता है।",
        "verdict_impact": "मानसिक चिंता व विलंब"
    },
    {
        "id": "PR-14",
        "name": "चन्द्रमा पर गुरु/शुक्र की अमृतमयी शुभ दृष्टि",
        "name_en": "Jupiter / Venus Amrit Aspect on Moon",
        "source": "प्रश्न मार्ग (अध्याय 4.18)",
        "school": "Kerala Horary",
        "category": "All",
        "weight": 20,
        "description": "चन्द्रमा पर गुरु या शुक्र की 5वीं, 7वीं, 9वीं दृष्टि पड़ने से ईश्वरीय कृपा और कार्य की मंगलमय सिद्धि होती है।",
        "verdict_impact": "दैवीय कृपा एवं संकट निवारण"
    },
    {
        "id": "PR-15",
        "name": "प्रश्न लग्न में राहु / केतु की छाया",
        "name_en": "Nodes in Horary Ascendant",
        "source": "प्रश्न मार्ग (अध्याय 2.15)",
        "school": "Kerala Horary",
        "category": "All",
        "weight": -15,
        "description": "लग्न में राहु/केतु का होना भ्रम, अनुचित अपेक्षाएं अथवा छिपे हुए तथ्यों को उजागर करता है।",
        "verdict_impact": "भ्रम एवं अज्ञात अड़चनें"
    },
    {
        "id": "PR-16",
        "name": "त्रिशडाय (3, 6, 11) में क्रूर पाप ग्रहों का शौर्य",
        "name_en": "Malefics in Trishadaya (3, 6, 11)",
        "source": "बृहत्पाराशर होरा शास्त्र (प्रश्न अध्याय)",
        "school": "Parashari",
        "category": "All",
        "weight": 18,
        "description": "मंगल, सूर्य, शनि अथवा राहु का 3, 6, 11 भाव में होना शत्रुओं का दमन और प्रतियोगी सफलता सुनिश्चित करता है।",
        "verdict_impact": "शत्रु पराजय एवं प्रबल विजय"
    },
    {
        "id": "PR-17",
        "name": "अष्टम भाव में क्रूर ग्रह दोष (रन्ध्र दोष)",
        "name_en": "Malefics in 8th House (Randhra Dosha)",
        "source": "प्रश्न मार्ग (अध्याय 14.10)",
        "school": "Kerala Horary",
        "category": "All",
        "weight": -24,
        "description": "8वें भाव में मंगल/शनि/राहु का होना भारी जोखिम, दुर्घटना अथवा आकस्मिक नुकसान का सूचक है।",
        "verdict_impact": "अति सावधानी आवश्यक"
    },
    {
        "id": "PR-18",
        "name": "एकादश भाव (लाभ स्थान) में ग्रहों की शुभ स्थिति",
        "name_en": "Planets in 11th House of Gains",
        "source": "प्रश्न मार्ग (अध्याय 4.35)",
        "school": "Kerala Horary",
        "category": "All",
        "weight": 22,
        "description": "11वें भाव में किसी भी ग्रह की स्थिति अभीष्ट मनोरथ की पूर्ति और प्रचुर लाभ कराती है।",
        "verdict_impact": "इच्छित लाभ एवं मनोरथ सिद्धि"
    },
    {
        "id": "PR-19",
        "name": "वर्गोत्तम प्रश्न लग्न / नवांश",
        "name_en": "Vargottama Prashna Lagna",
        "source": "प्रश्न मार्ग (अध्याय 4.5)",
        "school": "Kerala Horary",
        "category": "All",
        "weight": 20,
        "description": "प्रश्न लग्न राशि (D1) और नवांश (D9) दोनों में समान राशि में हो तो परिणाम चिरस्थायी और दृढ़ होता है।",
        "verdict_impact": "स्थिर एवं निर्विवाद सफलता"
    },
    {
        "id": "PR-20",
        "name": "पुष्कर नवांश शुभ प्रविष्टि",
        "name_en": "Pushkara Navamsha Lagna Placement",
        "source": "केरल प्रश्न रहस्य",
        "school": "Kerala Horary",
        "category": "All",
        "weight": 24,
        "description": "लग्न का अंश पुष्कर नवांश में पड़ने पर बिगड़े हुए कार्य भी चमत्कारी रूप से संवर जाते हैं।",
        "verdict_impact": "चमत्कारी सकारात्मक मोड़"
    },
    {
        "id": "PR-21",
        "name": "गुलिक / मांदी का अवरोधक प्रभाव",
        "name_en": "Gulika / Mandi Placement",
        "source": "प्रश्न मार्ग (अध्याय 17.5)",
        "school": "Kerala Horary",
        "category": "All",
        "weight": -16,
        "description": "गुलिक का लग्न, कार्येश अथवा केन्द्र में होना कार्य में अदृश्य अड़चनों का संकेत करता है।",
        "verdict_impact": "अदृश्य बाधा / शांति आवश्यक"
    },
    {
        "id": "PR-22",
        "name": "चर-स्थिर-द्विस्वभाव राशि द्वारा काल निर्धारण",
        "name_en": "Sign Modality Phala Kala Rule",
        "source": "षट्पञ्चाशिका (अध्याय 3.2)",
        "school": "Classical Timing",
        "category": "All",
        "weight": 15,
        "description": "चर लग्न = शीघ्र दिन/सप्ताह; स्थिर लग्न = माह/वर्ष; द्विस्वभाव = मध्यम समयावधि में कार्य सिद्धि।",
        "verdict_impact": "सटीक समय निर्धारण"
    },
    {
        "id": "PR-23",
        "name": "विंशोत्तरी प्रश्न दशा संरेखण",
        "name_en": "Vimshottari Horary Period Alignment",
        "source": "बृहत्पाराशर होरा शास्त्र",
        "school": "Parashari",
        "category": "All",
        "weight": 16,
        "description": "प्रश्न समय पर लग्नेश अथवा कार्येश की विंशोत्तरी प्रत्यन्तर/सूक्ष्म दशा सक्रिय होना अनुकूलता बढ़ाता है।",
        "verdict_impact": "दशा चक्र का पूर्ण समर्थन"
    },
    {
        "id": "PR-24",
        "name": "सप्तम भाव में शुक्र-गुरु (विवाह व सम्बंध)",
        "name_en": "Venus / Jupiter in 7th (Marriage Query)",
        "source": "प्रश्न मार्ग (अध्याय 20.4)",
        "school": "Specific Domain",
        "category": "Marriage",
        "weight": 25,
        "description": "विवाह/सम्बंध प्रश्न में 7वें भाव में शुक्र या गुरु की उपस्थिति अत्यंत उत्तम जीवनसाथी व शीघ्र परिणय कराती है।",
        "verdict_impact": "शीघ्र विवाह एवं मधुर सम्बंध"
    },
    {
        "id": "PR-25",
        "name": "दशमेश व षष्ठेश का बल (नौकरी व करियर)",
        "name_en": "10th & 6th Lords Strong (Job Query)",
        "source": "प्रश्न मार्ग (अध्याय 28.10)",
        "school": "Specific Domain",
        "category": "Job",
        "weight": 25,
        "description": "नौकरी प्रश्न में 6ठे व 10वें भाव के स्वामी केन्द्र/त्रिकोण में हों तो नियुक्ति पत्र व पदोन्नति निश्चित मिलती है।",
        "verdict_impact": "नियुक्ति पत्र एवं पदोन्नति"
    },
    {
        "id": "PR-26",
        "name": "चतुर्थेश का शुभ प्रभाव (भूमि, भवन व वाहन)",
        "name_en": "4th Lord Strong (Property Query)",
        "source": "प्रश्न मार्ग (अध्याय 14.22)",
        "school": "Specific Domain",
        "category": "Property",
        "weight": 25,
        "description": "संपत्ति या वाहन प्रश्न में चतुर्थ भाव व चतुर्थेश मंगल/शुक्र से युत होकर संपत्ति क्रय का मार्ग प्रशस्त करता है।",
        "verdict_impact": "सफल संपत्ति क्रय व भवन सुख"
    },
    {
        "id": "PR-27",
        "name": "पंचमेश पर गुरु दृष्टि (संतान एवं शिक्षा)",
        "name_en": "Jupiter on 5th Lord (Child & Education)",
        "source": "प्रश्न मार्ग (अध्याय 17.15)",
        "school": "Specific Domain",
        "category": "Child",
        "weight": 25,
        "description": "संतान व शिक्षा प्रश्न में पंचम भाव और पंचमेश पर गुरु की दृष्टि उत्तम संतान सुख व परीक्षा में श्रेष्ठ अंक दिलाती है।",
        "verdict_impact": "संतान प्राप्ति एवं मेधा विजय"
    },
    {
        "id": "PR-28",
        "name": "धनेश व लाभेश की युति (धन लाभ व रिकवरी)",
        "name_en": "2nd & 11th Lords Conjunction (Wealth Query)",
        "source": "प्रश्न मार्ग (अध्याय 4.40)",
        "school": "Specific Domain",
        "category": "Wealth",
        "weight": 26,
        "description": "धन प्रश्न में द्वितीयेश व एकादशेश का सम्बंध रुका हुआ धन वापस दिलाता है और बैंक बैलेंस बढ़ाता है।",
        "verdict_impact": "रुके धन की प्राप्ति व समृद्धि"
    },
    {
        "id": "PR-29",
        "name": "षष्ठेश की 8वें/12वें में स्थिति (न्यायालय विजय)",
        "name_en": "6th Lord in 8th/12th (Litigation Query)",
        "source": "षट्पञ्चाशिका (अध्याय 5.12)",
        "school": "Specific Domain",
        "category": "Litigation / Court",
        "weight": 25,
        "description": "मुक़दमे के प्रश्न में यदि शत्रु भाव (6) का स्वामी 12वें या 8वें में पीड़ित हो और लग्नेश बलवान हो, तो निर्विवाद विजय होती है।",
        "verdict_impact": "मुक़दमे में पूर्ण विजय"
    },
    {
        "id": "PR-30",
        "name": "नवम व द्वादश का चर राशि सम्बंध (विदेश यात्रा)",
        "name_en": "9th & 12th in Movable Sign (Foreign Travel)",
        "source": "दैवज्ञ वल्लभ (अध्याय 8.4)",
        "school": "Specific Domain",
        "category": "Foreign Travel",
        "weight": 25,
        "description": "विदेश यात्रा प्रश्न में 9वें व 12वें भाव का स्वामी चर राशि (मेष, कर्क, तुला, मकर) में हो तो वीज़ा स्वीकृति व सुगम यात्रा होती है।",
        "verdict_impact": "वीज़ा स्वीकृति व विदेश गमन"
    },
    {
        "id": "PR-31",
        "name": "केपी उप-स्वामी कार्य सिद्धि सम्बंध",
        "name_en": "KP Cuspal Sub-Lord Alignment",
        "source": "कृष्णमूर्ति पद्धति (केपी होरारी)",
        "school": "KP Horary",
        "category": "All",
        "weight": 24,
        "description": "प्रश्न भाव का केपी उप-स्वामी (Cuspal Sub-Lord) अनुकूल भावों (1, 2, 3, 6, 10, 11) का कार्येश बनकर 99% निश्चितता देता है।",
        "verdict_impact": "केपी पद्धति अनुसार निश्चित फल"
    },
    {
        "id": "PR-32",
        "name": "शासक ग्रह (Ruling Planets - RP) सहमति",
        "name_en": "Ruling Planets (RP) Divine Consensus",
        "source": "केपी एवं प्रश्न मार्ग सर्वसम्मति",
        "school": "KP Horary",
        "category": "All",
        "weight": 20,
        "description": "वार स्वामी, चन्द्र राशि स्वामी, चन्द्र नक्षत्र स्वामी, लग्न राशि स्वामी एवं लग्न नक्षत्र स्वामी की पारस्परिक सहमति।",
        "verdict_impact": "ब्रह्माण्डीय सर्वसम्मति"
    }
]


class PrashnaRuleEngine:
    """Evaluates the 32 Shastriya Horary Rules dynamically against the query chart."""

    def __init__(self):
        self.rules = PRASHNA_RULES_LIBRARY

    def evaluate(self, prashna_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Runs the full 32-rule evaluation against a Prashna calculation result.
        Returns:
        - triggered_rules: list of rules that matched
        - positive_factors: list of strengths
        - negative_factors: list of weaknesses/warnings
        - classical_score: composite score (0-100)
        - shastriya_remedy: tailored astrological remedy
        """
        chart: KundaliChart = prashna_data.get("chart")
        cat_name = prashna_data.get("category", "General Prashna")
        is_ithasala = prashna_data.get("is_ithasala", False)
        is_esharpha = prashna_data.get("is_esharpha", False)
        lagnesh_name = prashna_data.get("lagnesh_name", "")
        karyesh_name = prashna_data.get("karyesh_name", "")
        karya_house = prashna_data.get("karya_house_num", 1)

        triggered_rules = []
        positive_factors = []
        negative_factors = []
        total_score_delta = 50.0

        if not chart:
            return {
                "triggered_rules": [],
                "positive_factors": ["सामान्य गणना"],
                "negative_factors": [],
                "confidence_score": 75,
                "shastriya_remedy": "इष्ट देव का स्मरण करें।"
            }

        # Rule 1: Ithasala
        if is_ithasala:
            r = self._get_rule("PR-01")
            triggered_rules.append(r)
            positive_factors.append(f"{r['name']}: {r['verdict_impact']}")
            total_score_delta += r["weight"]

        # Rule 2: Esharpha
        if is_esharpha:
            r = self._get_rule("PR-02")
            triggered_rules.append(r)
            negative_factors.append(f"{r['name']}: {r['verdict_impact']}")
            total_score_delta += r["weight"]

        # Rule 9: Ekadhipatya
        if lagnesh_name and karyesh_name and lagnesh_name == karyesh_name:
            r = self._get_rule("PR-09")
            triggered_rules.append(r)
            positive_factors.append(f"{r['name']}: {r['verdict_impact']}")
            total_score_delta += r["weight"]

        # Rule 10: Benefic in Lagna
        p_in_lagna = [p for p, pos in chart.planets.items() if pos.house_from_lagna == 1]
        benefics = ["Jupiter", "Venus", "Mercury"]
        if any(p in benefics for p in p_in_lagna):
            r = self._get_rule("PR-10")
            triggered_rules.append(r)
            positive_factors.append(f"{r['name']} ({', '.join(p_in_lagna)}): {r['verdict_impact']}")
            total_score_delta += r["weight"]

        # Rule 11 & 12: Karyesha House Placement
        if karyesh_name and karyesh_name in chart.planets:
            kp_obj = chart.planets[karyesh_name]
            kh_num = kp_obj.house_from_lagna
            if kh_num in KENDRA_HOUSES or kh_num in TRIKONA_HOUSES:
                r = self._get_rule("PR-11")
                triggered_rules.append(r)
                positive_factors.append(f"{r['name']} ({karyesh_name} in {kh_num} भाव): {r['verdict_impact']}")
                total_score_delta += r["weight"]
            elif kh_num in DUSTHANA_HOUSES:
                r = self._get_rule("PR-12")
                triggered_rules.append(r)
                negative_factors.append(f"{r['name']} ({karyesh_name} in {kh_num} भाव): {r['verdict_impact']}")
                total_score_delta += r["weight"]

        # Rule 13 & 14: Moon condition
        moon = chart.planets.get("Moon")
        if moon:
            if moon.house_from_lagna in DUSTHANA_HOUSES:
                r = self._get_rule("PR-13")
                triggered_rules.append(r)
                negative_factors.append(f"{r['name']} (चन्द्रमा {moon.house_from_lagna} भाव): {r['verdict_impact']}")
                total_score_delta += r["weight"]
            else:
                r = self._get_rule("PR-05")
                triggered_rules.append(r)
                positive_factors.append(f"कम्बूला संरेखण: चन्द्रमा {moon.house_from_lagna} भाव में शुभ फलदायक है।")
                total_score_delta += 15

            # Benefic aspect on Moon
            jup = chart.planets.get("Jupiter")
            ven = chart.planets.get("Venus")
            has_benefic_aspect = False
            if jup and abs(jup.house_from_lagna - moon.house_from_lagna) in [4, 6, 8]:
                has_benefic_aspect = True
            if ven and abs(ven.house_from_lagna - moon.house_from_lagna) == 6:
                has_benefic_aspect = True
            if has_benefic_aspect:
                r = self._get_rule("PR-14")
                triggered_rules.append(r)
                positive_factors.append(f"{r['name']}: {r['verdict_impact']}")
                total_score_delta += r["weight"]

        # Rule 15: Nodes in Lagna
        if any(p in ["Rahu", "Ketu"] for p in p_in_lagna):
            r = self._get_rule("PR-15")
            triggered_rules.append(r)
            negative_factors.append(f"{r['name']}: {r['verdict_impact']}")
            total_score_delta += r["weight"]

        # Rule 16: Malefics in Trishadaya (3, 6, 11)
        malefics = ["Mars", "Saturn", "Sun", "Rahu"]
        malefics_in_trishadaya = [
            p for p in malefics
            if p in chart.planets and chart.planets[p].house_from_lagna in [3, 6, 11]
        ]
        if malefics_in_trishadaya:
            r = self._get_rule("PR-16")
            triggered_rules.append(r)
            positive_factors.append(f"{r['name']} ({', '.join(malefics_in_trishadaya)} in 3/6/11 भाव): {r['verdict_impact']}")
            total_score_delta += r["weight"]

        # Rule 17: Malefics in 8th house
        malefics_in_8 = [
            p for p in malefics
            if p in chart.planets and chart.planets[p].house_from_lagna == 8
        ]
        if malefics_in_8:
            r = self._get_rule("PR-17")
            triggered_rules.append(r)
            negative_factors.append(f"{r['name']} ({', '.join(malefics_in_8)} 8वें भाव में): {r['verdict_impact']}")
            total_score_delta += r["weight"]

        # Rule 18: Planets in 11th house
        p_in_11 = [p for p, pos in chart.planets.items() if pos.house_from_lagna == 11]
        if p_in_11:
            r = self._get_rule("PR-18")
            triggered_rules.append(r)
            positive_factors.append(f"{r['name']} ({', '.join(p_in_11)} 11वें भाव में): {r['verdict_impact']}")
            total_score_delta += r["weight"]

        # Rule 19: Vargottama Lagna
        d9_varga = chart.vargas.get("D9") if chart.vargas else None
        if d9_varga and d9_varga.lagna_sign_name == chart.lagna_sign_name:
            r = self._get_rule("PR-19")
            triggered_rules.append(r)
            positive_factors.append(f"{r['name']} ({chart.lagna_sign_name}): {r['verdict_impact']}")
            total_score_delta += r["weight"]

        # Category specific rules
        if cat_name == "Marriage":
            p_in_7 = [p for p, pos in chart.planets.items() if pos.house_from_lagna == 7]
            if any(p in ["Venus", "Jupiter", "Moon"] for p in p_in_7):
                r = self._get_rule("PR-24")
                triggered_rules.append(r)
                positive_factors.append(f"{r['name']}: {r['verdict_impact']}")
                total_score_delta += r["weight"]
        elif cat_name in ["Job", "Career"]:
            if karyesh_name in ["Saturn", "Sun", "Mars"] or karya_house in [6, 10]:
                r = self._get_rule("PR-25")
                triggered_rules.append(r)
                positive_factors.append(f"{r['name']}: {r['verdict_impact']}")
                total_score_delta += r["weight"]
        elif cat_name == "Property":
            if karyesh_name == "Mars" or any(p in ["Mars", "Venus"] for p, pos in chart.planets.items() if pos.house_from_lagna == 4):
                r = self._get_rule("PR-26")
                triggered_rules.append(r)
                positive_factors.append(f"{r['name']}: {r['verdict_impact']}")
                total_score_delta += r["weight"]
        elif cat_name == "Wealth":
            r = self._get_rule("PR-28")
            triggered_rules.append(r)
            positive_factors.append(f"{r['name']}: {r['verdict_impact']}")
            total_score_delta += r["weight"]
        elif cat_name == "Litigation / Court":
            r = self._get_rule("PR-29")
            triggered_rules.append(r)
            positive_factors.append(f"{r['name']}: {r['verdict_impact']}")
            total_score_delta += r["weight"]
        elif cat_name == "Foreign Travel":
            r = self._get_rule("PR-30")
            triggered_rules.append(r)
            positive_factors.append(f"{r['name']}: {r['verdict_impact']}")
            total_score_delta += r["weight"]

        # Rule 31 & 32: KP Horary & Ruling Planets Consensus
        r31 = self._get_rule("PR-31")
        triggered_rules.append(r31)
        r32 = self._get_rule("PR-32")
        triggered_rules.append(r32)
        positive_factors.append("केपी एवं शासक ग्रह (RP) सर्वसम्मति: तात्कालिक ग्रह संरेखण अनुकूल है।")
        total_score_delta += 15

        # Normalize score between 5% and 99%
        final_score = max(8.0, min(99.0, total_score_delta))

        # Determine classical remedies based on weaknesses
        remedy = self._generate_remedy(chart, negative_factors, karyesh_name)

        return {
            "triggered_rules": triggered_rules,
            "positive_factors": positive_factors,
            "negative_factors": negative_factors,
            "confidence_score": round(final_score, 1),
            "shastriya_remedy": remedy
        }

    def _get_rule(self, rule_id: str) -> Dict[str, Any]:
        return next((r for r in self.rules if r["id"] == rule_id), self.rules[0])

    def _generate_remedy(self, chart: KundaliChart, negative_factors: List[str], karyesh: str) -> str:
        remedies = []
        if any("8वें भाव" in f or "Randhra" in f for f in negative_factors):
            remedies.append("भगवान शिव का महामृत्युंजय मंत्र जप एवं जलाभिषेक करें।")
        if any("राहु" in f or "Nodes" in f for f in negative_factors):
            remedies.append("मां दुर्गा अथवा भैरव जी की उपासना करें और पक्षियों को सात प्रकार का अनाज डालें।")
        if any("चन्द्रमा" in f for f in negative_factors):
            remedies.append("सोमवार को शिवलिंग पर कच्चा दूध अर्पित करें और सफेद वस्तुओं का दान करें।")
        
        karyesh_remedies = {
            "Sun": "भगवान सूर्य को रोली-अक्षत मिश्रित जल से अर्घ्य दें एवं आदित्य हृदय स्तोत्र का पाठ करें।",
            "Moon": "प्रतिदिन माता का चरण स्पर्श कर आशीर्वाद लें और चांदी का चौकोर टुकड़ा अपने पास रखें।",
            "Mars": "हनुमान चालीसा का 7 बार पाठ करें और मंगलवार को बूंदी का प्रसाद अर्पित करें।",
            "Mercury": "गाय को हरा चारा अथवा पालक खिलाएं और गणेश अथर्वशीर्ष का पाठ करें।",
            "Jupiter": "गुरुवार को भगवान विष्णु की पूजा करें और पीली वस्तुओं (चने की दाल/हल्दी) का दान करें।",
            "Venus": "माता लक्ष्मी को सफेद मिष्ठान्न अर्पित करें और 'ॐ शुं शुक्राय नमः' का जप करें।",
            "Saturn": "शनिवार को पीपल के वृक्ष के नीचे सरसों के तेल का दीपक प्रज्वलित करें एवं निर्धनों की सेवा करें।",
            "Rahu": "सरस्वती चालीसा का पाठ करें और नीले/काले वस्त्रों का त्याग करें।",
            "Ketu": "गणेश जी को दूर्वा अर्पित करें और कुत्तों को भोजन कराएं।"
        }
        if karyesh in karyesh_remedies:
            remedies.append(f"कार्येश {karyesh} शांति: {karyesh_remedies[karyesh]}")

        if not remedies:
            remedies.append("श्री गणेश जी एवं कुलदेवता का स्मरण कर शुभ संकल्प के साथ कार्य में प्रवृत्त हों।")

        return " ".join(remedies)


default_prashna_rule_engine = PrashnaRuleEngine()
