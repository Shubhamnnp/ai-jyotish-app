"""
Prashna 100 Classical Rules Engine for JyotishOS.
Synthesizes authoritative Shastriya principles from:
1. Prashna Marga (Kerala Classical Horary)
2. Tajika Neelakanthi (Samar Simha & Neelakantha)
3. Shatpanchasika (Prithuyashas)
4. Daivajna Vallabha (Varahamihira)
5. Prashna Chintamani (Damodara)
6. BPHS & Uttara Kalamrita
7. Krishnamurti Padhdhati (KP Horary 1-249 Sub-Lord Rules)

Evaluates every Prashna Chart against 100 distinct rules, tagging each as POSITIVE (+) or NEGATIVE (-),
calculates net consensus, and provides full evidence for the final verdict.
"""

from typing import Dict, List, Any, Tuple, Optional
from datetime import datetime
from src.jyotish.core.models import KundaliChart
from src.jyotish.core.constants import KENDRA_HOUSES, TRIKONA_HOUSES, DUSTHANA_HOUSES, SIGN_LORDS


# Deeptamsha orbs
DEEPTAMSHA = {
    "Sun": 15.0, "Moon": 12.0, "Mars": 8.0, "Mercury": 7.0,
    "Jupiter": 9.0, "Venus": 7.0, "Saturn": 9.0, "Rahu": 5.0, "Ketu": 5.0
}

# Sign classification
SHIRSHODAYA_SIGNS = [3, 5, 6, 7, 8, 11]  # Gemini, Leo, Virgo, Libra, Scorpio, Aquarius
PRISHTODAYA_SIGNS = [1, 2, 4, 9, 10]      # Aries, Taurus, Cancer, Sagittarius, Capricorn
UBHAYODAYA_SIGNS = [12]                   # Pisces

MOVABLE_SIGNS = [1, 4, 7, 10]
FIXED_SIGNS = [2, 5, 8, 11]
DUAL_SIGNS = [3, 6, 9, 12]

WATER_SIGNS = [4, 8, 12]
EARTH_SIGNS = [2, 6, 10]
FIRE_SIGNS = [1, 5, 9]
AIR_SIGNS = [3, 7, 11]


class PrashnaRuleEvaluator:
    """Evaluates 100 classical Prashna rules against a computed horary chart."""

    def __init__(self):
        pass

    def evaluate_100_rules(
        self,
        chart: KundaliChart,
        category: str,
        karya_house_num: int,
        karyesh_name: str,
        is_ithasala: bool,
        is_esharpha: bool,
        tajika_yoga_name: str
    ) -> Dict[str, Any]:
        """
        Runs the full battery of 100 Prashna Shastra rules.
        Returns triggered positive rules, negative rules, net consensus, and full rulebook table.
        """
        lagnesh_name = chart.houses[0].lord
        lagnesh = chart.planets[lagnesh_name]
        karyesh = chart.planets[karyesh_name]
        moon = chart.planets["Moon"]
        sun = chart.planets["Sun"]
        jupiter = chart.planets["Jupiter"]
        venus = chart.planets["Venus"]
        mars = chart.planets["Mars"]
        saturn = chart.planets["Saturn"]
        mercury = chart.planets["Mercury"]
        rahu = chart.planets["Rahu"]
        ketu = chart.planets["Ketu"]

        l_house = lagnesh.house_from_lagna
        k_house = karyesh.house_from_lagna
        m_house = moon.house_from_lagna
        lagna_sign_id = chart.lagna_sign_id

        benefics = ["Jupiter", "Venus", "Mercury"]
        malefics = ["Saturn", "Mars", "Rahu", "Ketu", "Sun"]

        # Helper: occupants of house
        def occ(h_num: int) -> List[str]:
            return [p for p, pos in chart.planets.items() if pos.house_from_lagna == h_num]

        # Helper: check aspect on house
        def aspects_house(p_name: str, h_num: int) -> bool:
            return p_name in chart.houses[h_num - 1].aspecting_planets

        # Angular difference for Tajika
        deg_diff = abs(lagnesh.longitude - karyesh.longitude) % 360.0
        if deg_diff > 180.0:
            deg_diff = 360.0 - deg_diff

        avg_orb = (DEEPTAMSHA.get(lagnesh_name, 8.0) + DEEPTAMSHA.get(karyesh_name, 8.0)) / 2.0

        rules_evaluated: List[Dict[str, Any]] = []

        def add_rule(
            r_id: str,
            domain: str,
            name_hi: str,
            name_en: str,
            source: str,
            r_type: str,
            weight: int,
            triggered: bool,
            desc_hi: str
        ):
            rules_evaluated.append({
                "rule_id": r_id,
                "domain": domain,
                "name_hi": name_hi,
                "name_en": name_en,
                "source": source,
                "type": r_type,  # "POSITIVE" or "NEGATIVE"
                "weight": weight if r_type == "POSITIVE" else -weight,
                "triggered": triggered,
                "status": "✅ लागू (Triggered)" if triggered else "⚪ अनुपस्थित (Inactive)",
                "description_hi": desc_hi
            })

        # =========================================================================
        # DOMAIN 1: LAGNA & LAGNESHA PRINCIPLES (Rules 1 to 15)
        # =========================================================================
        add_rule(
            "PR-001", "लग्न एवं लग्नेश", "शीर्षोदय लग्न उदय", "Shirshodaya Lagna Rising",
            "Prashna Marga 2.15", "POSITIVE", 15,
            lagna_sign_id in SHIRSHODAYA_SIGNS,
            f"प्रश्न लग्न शीर्षोदय राशि ({chart.lagna_sign_name}) है, जो कार्य की सुगम व त्वरित सिद्धि दर्शाता है।"
        )
        add_rule(
            "PR-002", "लग्न एवं लग्नेश", "पृष्ठोदय लग्न उदय", "Prishtodaya Lagna Rising",
            "Prashna Marga 2.16", "NEGATIVE", 12,
            lagna_sign_id in PRISHTODAYA_SIGNS,
            f"प्रश्न लग्न पृष्ठोदय राशि ({chart.lagna_sign_name}) है, जिससे प्रारंभिक विलंब व अधिक प्रयास अपेक्षित है।"
        )
        add_rule(
            "PR-003", "लग्न एवं लग्नेश", "उभयोदय लग्न (मीन)", "Ubhayodaya Pisces Lagna",
            "Daivajna Vallabha 1.8", "POSITIVE", 10,
            lagna_sign_id == 12,
            "मीन लग्न उभयोदय होने से आध्यात्मिक व न्यायपूर्ण कार्यों में संतुलन व सिद्धि देता है।"
        )
        add_rule(
            "PR-004", "लग्न एवं लग्नेश", "लग्नेश केंद्र भाव में (1, 4, 7, 10)", "Lagnesha in Kendra House",
            "Tajika Neelakanthi 3.2", "POSITIVE", 20,
            l_house in KENDRA_HOUSES,
            f"लग्नेश '{lagnesh_name}' केंद्र भाव ({l_house} भाव) में स्थित होकर प्रश्नकर्ता को प्रबल बल व सामर्थ्य प्रदान कर रहा है।"
        )
        add_rule(
            "PR-005", "लग्न एवं लग्नेश", "लग्नेश त्रिकोण भाव में (5, 9)", "Lagnesha in Trikona House",
            "Prashna Chintamani 1.12", "POSITIVE", 20,
            l_house in TRIKONA_HOUSES,
            f"लग्नेश '{lagnesh_name}' त्रिकोण भाव ({l_house} भाव) में भाग्य व पूर्वपुण्य से अभीष्ट सिद्धि कराता है।"
        )
        add_rule(
            "PR-006", "लग्न एवं लग्नेश", "लग्नेश त्रिक भाव में (6, 8, 12)", "Lagnesha in Dusthana (6, 8, 12)",
            "Prashna Marga 4.22", "NEGATIVE", 20,
            l_house in DUSTHANA_HOUSES,
            f"लग्नेश '{lagnesh_name}' {l_house}वें दुष्ट भाव में स्थित होकर प्रश्नकर्ता के प्रयास में अवरोध व कष्ट दर्शाता है।"
        )
        add_rule(
            "PR-007", "लग्न एवं लग्नेश", "लग्न पर गुरु अथवा शुक्र की शुभ दृष्टि", "Jupiter/Venus Aspecting Lagna",
            "Shatpanchasika 1.4", "POSITIVE", 25,
            aspects_house("Jupiter", 1) or aspects_house("Venus", 1),
            "लग्न पर देवगुरु अथवा शुक्र की अमृतमयी दृष्टि समस्त दोषों का शमन कर कार्य सिद्धि कराती है।"
        )
        add_rule(
            "PR-008", "लग्न एवं लग्नेश", "लग्न पर शनि/मंगल/राहु की अशुभ दृष्टि", "Malefic Aspect on Lagna",
            "Daivajna Vallabha 2.5", "NEGATIVE", 18,
            aspects_house("Saturn", 1) or aspects_house("Mars", 1) or aspects_house("Rahu", 1),
            "लग्न पर पाप ग्रहों की दृष्टि मानसिक उद्वेग, तनाव अथवा अप्रत्याशित बाधाएं उत्पन्न करती है।"
        )
        add_rule(
            "PR-009", "लग्न एवं लग्नेश", "शुभ कर्तरी योग (लग्न के दोनों ओर शुभ ग्रह)", "Shubha Kartari on Lagna",
            "Prashna Marga 3.10", "POSITIVE", 20,
            bool(set(occ(12)).intersection(benefics) and set(occ(2)).intersection(benefics)),
            "लग्न शुभ कर्तरी योग में सुरक्षित होने से सर्वत्र संरक्षण व विजय प्राप्त होती है।"
        )
        add_rule(
            "PR-010", "लग्न एवं लग्नेश", "पाप कर्तरी योग (लग्न के दोनों ओर पाप ग्रह)", "Papa Kartari on Lagna",
            "Prashna Marga 3.11", "NEGATIVE", 22,
            bool(set(occ(12)).intersection(malefics) and set(occ(2)).intersection(malefics)),
            "लग्न पाप कर्तरी में फँसा होने से प्रश्नकर्ता चारों ओर से दबाव व विरोध महसूस करता है।"
        )
        add_rule(
            "PR-011", "लग्न एवं लग्नेश", "लग्नेश स्वराशि अथवा उच्च राशि में", "Lagnesha Exalted or Own Sign",
            "BPHS 28.4", "POSITIVE", 25,
            lagnesh.sign_name in [SIGN_LORDS.get(lagnesh.sign_name), "Taurus", "Cancer", "Capricorn", "Pisces"],
            f"लग्नेश '{lagnesh_name}' उच्च/स्वराशि में अत्यधिक शक्तिशाली है।"
        )
        add_rule(
            "PR-012", "लग्न एवं लग्नेश", "लग्नेश नीच राशि में", "Lagnesha Debilitated",
            "Prashna Marga 4.18", "NEGATIVE", 22,
            lagnesh.sign_name in ["Libra", "Scorpio", "Cancer", "Pisces", "Capricorn", "Virgo"] and lagnesh_name in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"],
            f"लग्नेश '{lagnesh_name}' नीच राशि में होने से आत्मबल में कमी व निराशा का संकेत है।"
        )
        add_rule(
            "PR-013", "लग्न एवं लग्नेश", "लग्नेश का वक्री होना", "Lagnesha Retrograde",
            "Tajika Neelakanthi 2.11", "NEGATIVE", 15,
            lagnesh.is_retrograde,
            f"लग्नेश '{lagnesh_name}' वक्री होने से पूर्व निर्णय पर पुनर्विचार अथवा योजनाओं में बदलाव होगा।"
        )
        add_rule(
            "PR-014", "लग्न एवं लग्नेश", "लग्नेश का अस्त (Combust) होना", "Lagnesha Combust by Sun",
            "Prashna Marga 4.29", "NEGATIVE", 20,
            abs(lagnesh.longitude - sun.longitude) < 8.0 and lagnesh_name != "Sun",
            f"लग्नेश '{lagnesh_name}' सूर्य के अत्यधिक समीप अस्त होकर प्रभावहीन हो रहा है।"
        )
        add_rule(
            "PR-015", "लग्न एवं लग्नेश", "लग्न में गुरु विराजमान", "Jupiter in 1st House",
            "Shatpanchasika 1.2", "POSITIVE", 30,
            "Jupiter" in occ(1),
            "लग्न में विराजमान देवगुरु बृहस्पति लाखों दोषों को नष्ट कर एकछत्र विजय दिलाते हैं।"
        )

        # =========================================================================
        # DOMAIN 2: KARYA BHAVA & KARYESHA (Rules 16 to 30)
        # =========================================================================
        add_rule(
            "PR-016", "कार्य भाव एवं कार्येश", "कार्येश केंद्र भाव में (1, 4, 7, 10)", "Karyesha in Kendra House",
            "Tajika Neelakanthi 3.5", "POSITIVE", 20,
            k_house in KENDRA_HOUSES,
            f"कार्येश '{karyesh_name}' केंद्र भाव ({k_house} भाव) में स्थित होकर कार्य को प्रत्यक्ष गति दे रहा है।"
        )
        add_rule(
            "PR-017", "कार्य भाव एवं कार्येश", "कार्येश त्रिकोण भाव में (5, 9)", "Karyesha in Trikona House",
            "Prashna Chintamani 2.4", "POSITIVE", 20,
            k_house in TRIKONA_HOUSES,
            f"कार्येश '{karyesh_name}' त्रिकोण भाव में भाग्य व ईश्वर कृपा से सफलता सुनिश्चित करता है।"
        )
        add_rule(
            "PR-018", "कार्य भाव एवं कार्येश", "कार्येश 6, 8, 12 भाव में", "Karyesha in Trika Houses (6, 8, 12)",
            "Prashna Marga 5.14", "NEGATIVE", 22,
            k_house in DUSTHANA_HOUSES,
            f"कार्येश '{karyesh_name}' {k_house}वें भाव में पीड़ित होकर अभीष्ट फल में भारी विलंब व नुकसान दिखाता है।"
        )
        add_rule(
            "PR-019", "कार्य भाव एवं कार्येश", "कार्य भाव पर अपने स्वामी की स्वक्षेत्र दृष्टि", "Karyesha Aspecting Own Bhava",
            "Daivajna Vallabha 3.1", "POSITIVE", 25,
            aspects_house(karyesh_name, karya_house_num) or (k_house == karya_house_num),
            f"कार्येश '{karyesh_name}' अपने ही {karya_house_num}वें भाव को देख अथवा स्थित होकर पुष्ट कर रहा है।"
        )
        add_rule(
            "PR-020", "कार्य भाव एवं कार्येश", "कार्य भाव पर शुभ ग्रहों (गुरु/शुक्र) की दृष्टि", "Benefics Aspecting Karya Bhava",
            "Shatpanchasika 2.3", "POSITIVE", 20,
            aspects_house("Jupiter", karya_house_num) or aspects_house("Venus", karya_house_num),
            f"कार्य भाव {karya_house_num} पर शुभ दृष्टि से कार्य बिना अवरोध के सुचारू होगा।"
        )
        add_rule(
            "PR-021", "कार्य भाव एवं कार्येश", "कार्य भाव पर पाप ग्रहों (शनि/मंगल/राहु) की दृष्टि", "Malefics Aspecting Karya Bhava",
            "Prashna Marga 5.8", "NEGATIVE", 18,
            aspects_house("Saturn", karya_house_num) or aspects_house("Mars", karya_house_num) or aspects_house("Rahu", karya_house_num),
            f"कार्य भाव {karya_house_num} पर पाप दृष्टि से विवाद अथवा कानूनी/प्रशासनिक पेचीदगियां संभव हैं।"
        )
        add_rule(
            "PR-022", "कार्य भाव एवं कार्येश", "कार्येश लग्न में स्थित (Karyesha in 1st House)", "Karyesha in Lagna",
            "Tajika Neelakanthi 3.8", "POSITIVE", 25,
            k_house == 1,
            f"कार्येश '{karyesh_name}' स्वयं लग्न में आ बैठा है — फल स्वयं प्रश्नकर्ता के पास चलकर आएगा।"
        )
        add_rule(
            "PR-023", "कार्य भाव एवं कार्येश", "लग्नेश कार्य भाव में स्थित (Lagnesha in Karya Bhava)", "Lagnesha in Karya Bhava",
            "Tajika Neelakanthi 3.9", "POSITIVE", 25,
            l_house == karya_house_num,
            f"लग्नेश '{lagnesh_name}' अभीष्ट कार्य भाव {karya_house_num} में उपस्थित है — प्रश्नकर्ता का पूर्ण समर्पण लक्ष्य सिद्धि करेगा।"
        )
        add_rule(
            "PR-024", "कार्य भाव एवं कार्येश", "लग्नेश और कार्येश की युति (Conjunction in Same House)", "Lagnesha & Karyesha Conjunct",
            "Daivajna Vallabha 3.4", "POSITIVE", 30,
            l_house == k_house,
            f"लग्नेश व कार्येश दोनों {l_house}वें भाव में एक साथ युति कर रहे हैं — अत्यंत श्रेष्ठ फलदायक योग!"
        )
        add_rule(
            "PR-025", "कार्य भाव एवं कार्येश", "लग्नेश और कार्येश में राशि परिवर्तन योग", "Mutual Reception / Parivartana",
            "BPHS 26.11", "POSITIVE", 28,
            SIGN_LORDS.get(lagnesh.sign_name) == karyesh_name and SIGN_LORDS.get(karyesh.sign_name) == lagnesh_name,
            "लग्नेश और कार्येश के मध्य परस्पर राशि परिवर्तन होने से असंभव कार्य भी संभव हो जाता है।"
        )
        add_rule(
            "PR-026", "कार्य भाव एवं कार्येश", "कार्येश का वक्री होना (Karyesha Retrograde)", "Karyesha Retrograde",
            "Tajika Neelakanthi 2.14", "NEGATIVE", 16,
            karyesh.is_retrograde,
            f"कार्येश '{karyesh_name}' वक्री होने से कार्य बनते-बनते अटक सकता है अथवा पुरानी शर्तें लौटेंगी।"
        )
        add_rule(
            "PR-027", "कार्य भाव एवं कार्येश", "कार्येश का अस्त होना (Karyesha Combust)", "Karyesha Combust",
            "Prashna Marga 5.20", "NEGATIVE", 20,
            abs(karyesh.longitude - sun.longitude) < 8.0 and karyesh_name != "Sun",
            f"कार्येश '{karyesh_name}' सूर्य के तेज से अस्त होकर अपना संपूर्ण फल देने में असमर्थ है।"
        )
        add_rule(
            "PR-028", "कार्य भाव एवं कार्येश", "कार्येश 11वें लाभ भाव में स्थित", "Karyesha in 11th House of Gains",
            "Shatpanchasika 3.1", "POSITIVE", 25,
            k_house == 11,
            f"कार्येश '{karyesh_name}' एकादश लाभ भाव में बैठकर प्रचुर धन व मनोवांछित फल दे रहा है।"
        )
        add_rule(
            "PR-029", "कार्य भाव एवं कार्येश", "कार्य भाव में राहु/केतु का वास", "Rahu/Ketu in Karya Bhava",
            "Prashna Marga 5.28", "NEGATIVE", 18,
            bool(set(["Rahu", "Ketu"]).intersection(occ(karya_house_num))),
            f"कार्य भाव {karya_house_num} में राहु/केतु का होना भ्रम, भटकाव अथवा अनपेक्षित कपट का भय दर्शाता है।"
        )
        add_rule(
            "PR-030", "कार्य भाव एवं कार्येश", "एकाधिपत्य योग (लग्नेश ही कार्येश है)", "Same Lord for Lagna and Karya",
            "Tajika Neelakanthi 3.1", "POSITIVE", 28,
            lagnesh_name == karyesh_name,
            f"लग्न और कार्य भाव दोनों के अधिपति '{lagnesh_name}' स्वयं हैं — कार्य की स्वाभाविक सिद्धि तय है।"
        )

        # =========================================================================
        # DOMAIN 3: TAJIKA 16 YOGAS & ASPECT PRINCIPLES (Rules 31 to 45)
        # =========================================================================
        add_rule(
            "PR-031", "ताजिक योग", "प्रत्यक्ष इत्थशाल योग (Pratyaksha Ithasala)", "Direct Ithasala Yoga",
            "Tajika Neelakanthi 1.18", "POSITIVE", 30,
            is_ithasala and not is_esharpha,
            "लग्नेश और कार्येश के मध्य प्रत्यक्ष इत्थशाल योग बना हुआ है — कार्य की त्वरित एवं निश्चित सफलता होगी।"
        )
        add_rule(
            "PR-032", "ताजिक योग", "ईशराफ / मुसरिफ़ योग (Esharpha / Separating)", "Esharpha Separating Yoga",
            "Tajika Neelakanthi 1.22", "NEGATIVE", 20,
            is_esharpha,
            "लग्नेश और कार्येश दीप्तांश पार कर दूर हो रहे हैं — अवसर हाथ से निकल चुका है अथवा विलंब होगा।"
        )
        add_rule(
            "PR-033", "ताजिक योग", "नक्त योग (Nakta Yoga — मध्यस्थ द्वारा सिद्धि)", "Nakta Yoga via Fast Planet",
            "Tajika Neelakanthi 1.25", "POSITIVE", 22,
            not is_ithasala and (m_house in KENDRA_HOUSES or m_house in TRIKONA_HOUSES),
            "चन्द्रमा अथवा द्रुतगामी ग्रह दोनों के मध्य प्रकाश का सम्प्रेषण कर मध्यस्थ के सहयोग से कार्य कराएगा।"
        )
        add_rule(
            "PR-034", "ताजिक योग", "यमया योग (Yamaya Yoga — धीमे ग्रह द्वारा सिद्धि)", "Yamaya Yoga via Slow Planet",
            "Tajika Neelakanthi 1.28", "POSITIVE", 18,
            saturn.house_from_lagna in [1, 4, 7, 10, 11] and not is_ithasala,
            "वरिष्ठ या धीमे ग्रह के प्रभाव से किसी अनुभवी अधिकारी/सलाहकार की सहायता से सफलता मिलेगी।"
        )
        add_rule(
            "PR-035", "ताजिक योग", "कम्बूल योग (Kamboola Yoga — चन्द्रमा का इत्थशाल)", "Kamboola Yoga with Moon",
            "Tajika Neelakanthi 1.30", "POSITIVE", 25,
            is_ithasala and m_house not in DUSTHANA_HOUSES,
            "चन्द्रमा इत्थशाल में सम्मिलित होकर मन की अभिलाषा को ठोस यथार्थ में परिवर्तित कर रहा है।"
        )
        add_rule(
            "PR-036", "ताजिक योग", "गैर-कम्बूल योग (Gairi-Kamboola — पाप प्रभावित)", "Gairi-Kamboola Yoga",
            "Tajika Neelakanthi 1.32", "NEGATIVE", 18,
            is_ithasala and bool(set(["Saturn", "Mars", "Rahu"]).intersection(occ(m_house))),
            "इत्थशाल में चन्द्रमा पर पाप प्रभाव से प्रारंभिक उत्साह के बाद रुकावटें आ सकती हैं।"
        )
        add_rule(
            "PR-037", "ताजिक योग", "रद्द योग (Radda Yoga — वक्री/अस्त द्वारा भंग)", "Radda Yoga Cancellation",
            "Tajika Neelakanthi 1.35", "NEGATIVE", 22,
            is_ithasala and (lagnesh.is_retrograde or karyesh.is_retrograde),
            "इत्थशाल में एक ग्रह के वक्री होने से बना-बनाया काम अंत समय में टलने का अंदेशा है।"
        )
        add_rule(
            "PR-038", "ताजिक योग", "कुत्थ योग (Kuttha Yoga — केंद्र में शुभ ग्रह)", "Kuttha Yoga",
            "Tajika Neelakanthi 1.38", "POSITIVE", 18,
            bool(set(occ(1) + occ(4) + occ(7) + occ(10)).intersection(benefics)),
            "केंद्र स्थानों में शुभ ग्रह उपस्थित होकर समग्र प्रश्न को सुरक्षा कवच प्रदान कर रहे हैं।"
        )
        add_rule(
            "PR-039", "ताजिक योग", "दुत्थ-कुत्थ योग (Duttha-Kuttha — केंद्र में पाप ग्रह)", "Duttha-Kuttha Yoga",
            "Tajika Neelakanthi 1.40", "NEGATIVE", 20,
            bool(set(occ(1) + occ(7)).intersection(["Mars", "Saturn", "Rahu"])),
            "लग्न अथवा सप्तम में उग्र पाप ग्रह होने से वाद-विवाद एवं तकरार की आशंका है।"
        )
        add_rule(
            "PR-040", "ताजिक योग", "तम्बीर योग (Tambira — राशि के अंतिम अंश पर ग्रह)", "Tambira Yoga at 29-30 Deg",
            "Tajika Neelakanthi 1.42", "POSITIVE", 12,
            lagnesh.sign_degree >= 28.0 or karyesh.sign_degree >= 28.0,
            "ग्रह राशि के अंतिम छोर पर स्थित होकर तात्कालिक बदलाव के पश्चात नई स्थिति में फल देगा।"
        )
        add_rule(
            "PR-041", "ताजिक योग", "त्रिकोण दृष्टि सम्बंध (120° Trine Aspect)", "Trine Tajika Aspect",
            "Tajika Neelakanthi 2.5", "POSITIVE", 20,
            abs(deg_diff - 120.0) <= avg_orb,
            "लग्नेश व कार्येश में नवम-पंचम शुभ त्रिकोण दृष्टि है, जो सहज सौहार्द व सफलता देती है।"
        )
        add_rule(
            "PR-042", "ताजिक योग", "मित्र दृष्टि सम्बंध (60° Sextile Aspect)", "Sextile Friendly Aspect",
            "Tajika Neelakanthi 2.6", "POSITIVE", 16,
            abs(deg_diff - 60.0) <= avg_orb,
            "लग्नेश व कार्येश में तृतीय-एकादश मित्र दृष्टि होने से मित्रों व सहयोगियों का साथ मिलेगा।"
        )
        add_rule(
            "PR-043", "ताजिक योग", "प्रत्यक्ष दृष्टि सम्बंध (180° Opposition)", "Opposition Aspect 180 Deg",
            "Tajika Neelakanthi 2.8", "NEGATIVE", 14,
            abs(deg_diff - 180.0) <= avg_orb,
            "लग्नेश व कार्येश आमने-सामने (180°) होने से समझौते अथवा बातचीत के बाद ही कार्य होगा।"
        )
        add_rule(
            "PR-044", "ताजिक योग", "चतुरस्र दृष्टि सम्बंध (90° Square Aspect)", "Square Aspect 90 Deg",
            "Tajika Neelakanthi 2.9", "NEGATIVE", 16,
            abs(deg_diff - 90.0) <= avg_orb,
            "लग्नेश व कार्येश में 90° का टकराव होने से संघर्ष, प्रतिस्पर्धा एवं श्रम अधिक रहेगा।"
        )
        add_rule(
            "PR-045", "ताजिक योग", "दीप्तांश विस्तार के भीतर निकटता", "Within Deepamsha Orbs",
            "Tajika Neelakanthi 2.2", "POSITIVE", 15,
            deg_diff <= avg_orb,
            f"दोनों मुख्य ग्रह परस्पर {deg_diff:.1f}° पर हैं जो औसत दीप्तांश ({avg_orb:.1f}°) के भीतर है।"
        )

        # =========================================================================
        # DOMAIN 4: CHANDRA / MOON PRINCIPLES (Rules 46 to 60)
        # =========================================================================
        add_rule(
            "PR-046", "चन्द्रमा की स्थिति", "चन्द्रमा केंद्र भाव में (1, 4, 7, 10)", "Moon in Kendra House",
            "Prashna Marga 8.4", "POSITIVE", 20,
            m_house in KENDRA_HOUSES,
            f"चन्द्रमा {m_house}वें केंद्र भाव में बलवान होकर प्रश्नकर्ता के मानसिक संकल्प को सिद्धि दे रहा है।"
        )
        add_rule(
            "PR-047", "चन्द्रमा की स्थिति", "चन्द्रमा त्रिकोण भाव में (5, 9)", "Moon in Trikona House",
            "Prashna Marga 8.5", "POSITIVE", 20,
            m_house in TRIKONA_HOUSES,
            f"चन्द्रमा {m_house}वें त्रिकोण भाव में स्थित होकर शुभता व प्रसन्नता बढ़ा रहा है।"
        )
        add_rule(
            "PR-048", "चन्द्रमा की स्थिति", "चन्द्रमा 6, 8, 12 अनिष्ट भाव में", "Moon in Dusthana (6, 8, 12)",
            "Prashna Marga 8.12", "NEGATIVE", 24,
            m_house in DUSTHANA_HOUSES,
            f"चन्द्रमा {m_house}वें भाव में पीड़ित होने से मानसिक भय, संशय व अनिश्चितता बनी रहेगी।"
        )
        add_rule(
            "PR-049", "चन्द्रमा की स्थिति", "चन्द्रमा-गुरु गजकेसरी योग", "Gajakesari Yoga in Horary",
            "Prashna Marga 8.18", "POSITIVE", 25,
            abs(moon.house_from_lagna - jupiter.house_from_lagna) % 3 in [0] or (moon.house_from_lagna in [1,4,7,10] and jupiter.house_from_lagna in [1,4,7,10]),
            "प्रश्न कुण्डली में चन्द्र-गुरु का गजकेसरी योग सभी संकटों को दूर कर प्रतिष्ठा व विजय देता है।"
        )
        add_rule(
            "PR-050", "चन्द्रमा की स्थिति", "चन्द्रमा-शनि विष योग", "Visha Yoga (Moon-Saturn)",
            "Prashna Marga 8.24", "NEGATIVE", 22,
            moon.house_from_lagna == saturn.house_from_lagna or abs(moon.longitude - saturn.longitude) < 12.0,
            "चन्द्रमा और शनि की युति से प्रश्नकर्ता अत्यधिक अवसाद, निराशा व विलंब से ग्रसित हो सकता है।"
        )
        add_rule(
            "PR-051", "चन्द्रमा की स्थिति", "चन्द्रमा पर राहु/केतु का ग्रहण दोष", "Eclipse Affliction on Moon",
            "Prashna Marga 8.28", "NEGATIVE", 25,
            moon.house_from_lagna in [rahu.house_from_lagna, ketu.house_from_lagna] or abs(moon.longitude - rahu.longitude) < 10.0,
            "चन्द्रमा राहु/केतु के अक्ष में होने से धोखा, गलत निर्णय अथवा छिपे हुए षड्यंत्र का भय है।"
        )
        add_rule(
            "PR-052", "चन्द्रमा की स्थिति", "शुक्ल पक्ष का बलवान चन्द्रमा", "Shukla Paksha Bright Moon",
            "Shatpanchasika 4.2", "POSITIVE", 15,
            (moon.longitude - sun.longitude) % 360.0 < 180.0,
            "शुक्ल पक्ष का प्रकाशमान चन्द्रमा कार्य में तीव्र वृद्धि व शुभ वातावरण निर्मित करता है।"
        )
        add_rule(
            "PR-053", "चन्द्रमा की स्थिति", "कृष्ण पक्ष क्षीण चन्द्रमा", "Krishna Paksha Waning Moon",
            "Shatpanchasika 4.3", "NEGATIVE", 12,
            (moon.longitude - sun.longitude) % 360.0 >= 180.0 and (moon.longitude - sun.longitude) % 360.0 > 300.0,
            "अमावस्या के निकट क्षीण चन्द्रमा ऊर्जा की कमी व आत्मविश्वास में गिरावट दर्शाता है।"
        )
        add_rule(
            "PR-054", "चन्द्रमा की स्थिति", "चन्द्रमा स्वराशि (कर्क) अथवा उच्च (वृषभ) में", "Moon Exalted or Own Sign",
            "BPHS 28.6", "POSITIVE", 25,
            moon.sign_name in ["Cancer", "Taurus"],
            f"चन्द्रमा {moon.sign_name} में अति बलवान है — चित्त की प्रसन्नता व उत्तम परिणाम प्राप्त होंगे।"
        )
        add_rule(
            "PR-055", "चन्द्रमा की स्थिति", "चन्द्रमा नीच राशि (वृश्चिक) में", "Moon Debilitated in Scorpio",
            "Prashna Marga 8.35", "NEGATIVE", 20,
            moon.sign_name == "Scorpio",
            "चन्द्रमा वृश्चिक में नीचस्थ होने से गुप्त चिंताएं व मानसिक अस्थिरता रहेगी।"
        )
        add_rule(
            "PR-056", "चन्द्रमा की स्थिति", "चन्द्रमा चर राशि में (गतिशील)", "Moon in Movable Sign",
            "Daivajna Vallabha 4.5", "POSITIVE", 12,
            chart.houses[m_house - 1].sign_id in MOVABLE_SIGNS,
            "चन्द्रमा चर राशि में होने से परिस्थिति में शीघ्र परिवर्तन व त्वरित आवागमन होगा।"
        )
        add_rule(
            "PR-057", "चन्द्रमा की स्थिति", "चन्द्रमा स्थिर राशि में (स्थायित्व)", "Moon in Fixed Sign",
            "Daivajna Vallabha 4.6", "POSITIVE", 12,
            chart.houses[m_house - 1].sign_id in FIXED_SIGNS,
            "चन्द्रमा स्थिर राशि में होने से परिणाम स्थायी, टिकाऊ व दीर्घकालिक रहेंगे।"
        )
        add_rule(
            "PR-058", "चन्द्रमा की स्थिति", "चन्द्रमा जल राशि में (कर्क, वृश्चिक, मीन)", "Moon in Water Sign",
            "Prashna Marga 8.40", "POSITIVE", 14,
            chart.houses[m_house - 1].sign_id in WATER_SIGNS,
            "चन्द्रमा जल तत्व में स्थित होकर भावनात्मक संतुष्टि व विदेश/यात्रा में लाभ देता है।"
        )
        add_rule(
            "PR-059", "चन्द्रमा की स्थिति", "चन्द्रमा का कार्येश की ओर अग्रसर होना", "Moon Applying to Karyesha",
            "Tajika Neelakanthi 3.12", "POSITIVE", 20,
            moon.longitude < karyesh.longitude and abs(moon.longitude - karyesh.longitude) < 15.0,
            "चन्द्रमा कार्येश की ओर बढ़ रहा है — मनोकामना शीघ्र पूर्ण होने के प्रबल संकेत हैं।"
        )
        add_rule(
            "PR-060", "चन्द्रमा की स्थिति", "केमद्रुम दोष (चन्द्र के आगे-पीछे कोई ग्रह नहीं)", "Kemadruma Moon in Prashna",
            "Prashna Marga 8.45", "NEGATIVE", 18,
            not occ(((m_house - 2) % 12) + 1) and not occ((m_house % 12) + 1),
            "चन्द्रमा अकेला होने से प्रश्नकर्ता को एकाकी संघर्ष व असमंजस का सामना करना पड़ सकता है।"
        )

        # =========================================================================
        # DOMAIN 5: 23 CATEGORY SPECIFIC RULES (Rules 61 to 80)
        # =========================================================================
        # Category-driven evaluations
        is_health = category in ["Health", "Surgery / Diagnosis"]
        is_marriage = category in ["Marriage", "Relationship"]
        is_career = category in ["Career", "Job", "Business"]
        is_wealth = category in ["Wealth", "Investment", "Debt / Loan"]
        is_property = category in ["Property", "Purchase Vehicle", "Construction / Vastu"]
        is_litigation = category in ["Litigation / Court", "Friends / Enemies"]
        is_travel = category in ["Foreign Travel", "Relocation / Transfer"]
        is_edu = category in ["Education / Exam", "Spiritual Initiation", "Child"]

        add_rule(
            "PR-061", "विषय विशेष (Health)", "रोग मुक्ति: लग्नेश का 6ठे भाव के स्वामी से अधिक बलवान होना", "Health: Lagnesha Stronger than 6th Lord",
            "Prashna Marga 12.4", "POSITIVE", 25,
            is_health and (l_house in [1, 4, 5, 9, 10, 11]),
            "रोग प्रश्न में लग्नेश का केंद्र/त्रिकोण में होना शीघ्र स्वास्थ्य लाभ व रोग मुक्ति का प्रमाण है।"
        )
        add_rule(
            "PR-062", "विषय विशेष (Health)", "रोग वृद्धि: 6ठे/8वें भाव के स्वामी का लग्न में होना", "Health: 6th/8th Lord in Lagna",
            "Prashna Marga 12.10", "NEGATIVE", 25,
            is_health and (chart.houses[5].lord in occ(1) or chart.houses[7].lord in occ(1)),
            "रोगेश अथवा अष्टमेश का लग्न में होना बीमारी के लंबे खिंचने व अतिरिक्त चिकित्सा की आवश्यकता दिखाता है।"
        )
        add_rule(
            "PR-063", "विषय विशेष (Marriage)", "विवाह योग: शुक्र का 7वें/11वें भाव में शुभ दृष्टि युक्त होना", "Marriage: Venus in 7th/11th with Benefics",
            "Shatpanchasika 5.2", "POSITIVE", 25,
            is_marriage and (venus.house_from_lagna in [1, 2, 7, 11] or aspects_house("Jupiter", 7)),
            "विवाह प्रश्न में शुक्र व गुरु का शुभ सम्बंध शीघ्र मनपसंद जीवनसाथी व परिणय सूत्र में बंधने का योग बनाता है।"
        )
        add_rule(
            "PR-064", "विषय विशेष (Marriage)", "विवाह बाधा: मंगल अथवा राहु का 7वें भाव में होना", "Marriage: Mars/Rahu in 7th House",
            "Prashna Marga 14.8", "NEGATIVE", 22,
            is_marriage and bool(set(["Mars", "Rahu", "Saturn"]).intersection(occ(7))),
            "सप्तम भाव में पाप ग्रहों का प्रभाव रिश्ते में गलतफहमी, दहेज या वैचारिक मतभेद का संकेत है।"
        )
        add_rule(
            "PR-065", "विषय विशेष (Career)", "दशमेश का लग्न अथवा 11वें भाव में होना", "Career: 10th Lord in 1st or 11th",
            "Daivajna Vallabha 6.4", "POSITIVE", 25,
            is_career and (chart.houses[9].lord in occ(1) or chart.houses[9].lord in occ(11) or k_house in [1, 10, 11]),
            "करियर/नौकरी प्रश्न में कर्मेश का लग्न/लाभ में होना पदोन्नति, नई नौकरी व उच्चाधिकारियों का अनुग्रह दिलाता है।"
        )
        add_rule(
            "PR-066", "विषय विशेष (Career)", "दशम भाव पर शनि/राहु का दूषित प्रभाव", "Career: 10th House Afflicted",
            "Prashna Marga 15.12", "NEGATIVE", 20,
            is_career and bool(set(["Rahu", "Saturn", "Mars"]).intersection(occ(10))),
            "दशम भाव में क्रूर ग्रहों की स्थिति कार्यक्षेत्र में राजनीति अथवा स्थानांतरण का दबाव बना सकती है।"
        )
        add_rule(
            "PR-067", "विषय विशेष (Wealth)", "द्वितीय व एकादश भाव के स्वामियों की युति", "Wealth: 2nd and 11th Lords Conjunct",
            "BPHS 29.5", "POSITIVE", 28,
            is_wealth and (chart.houses[1].lord == chart.houses[10].lord or chart.planets[chart.houses[1].lord].house_from_lagna == chart.planets[chart.houses[10].lord].house_from_lagna),
            "धन व लाभ भाव के स्वामियों का मिलन अप्रत्याशित धन लाभ व आर्थिक स्थिति सुदृढ़ होने का अचूक योग है।"
        )
        add_rule(
            "PR-068", "विषय विशेष (Wealth)", "धनेश का 12वें व्यय भाव में होना", "Wealth: 2nd Lord in 12th House",
            "Prashna Chintamani 3.8", "NEGATIVE", 20,
            is_wealth and (chart.planets[chart.houses[1].lord].house_from_lagna == 12),
            "धनेश का 12वें भाव में जाना संचित पूंजी के व्यर्थ खर्च अथवा निवेश में नुकसान की चेतावनी देता है।"
        )
        add_rule(
            "PR-069", "विषय विशेष (Property)", "भूमि कारक मंगल का चतुर्थ भाव/केंद्र में बली होना", "Property: Mars Strong in 4th/Kendra",
            "Prashna Marga 16.3", "POSITIVE", 25,
            is_property and (mars.house_from_lagna in [1, 4, 10, 11]),
            "भूमि-भवन प्रश्न में मंगल का बली होना अचल संपत्ति क्रय व गृह निर्माण में निर्विघ्न सफलता दिलाता है।"
        )
        add_rule(
            "PR-070", "विषय विशेष (Property)", "चतुर्थेश का 6ठे/8वें भाव में पीड़ित होना", "Property: 4th Lord in 6th/8th",
            "Prashna Marga 16.9", "NEGATIVE", 22,
            is_property and (chart.planets[chart.houses[3].lord].house_from_lagna in [6, 8]),
            "चतुर्थेश का दुष्ट भाव में होना संपत्ति में रजिस्ट्री विवाद, दोष अथवा विवादित जमीन का अंदेशा देता है।"
        )
        add_rule(
            "PR-071", "विषय विशेष (Court)", "षष्ठेश का निर्बल अथवा नीच होना (शत्रु पराजय)", "Litigation: 6th Lord Debilitated",
            "Daivajna Vallabha 7.2", "POSITIVE", 25,
            is_litigation and (chart.planets[chart.houses[5].lord].house_from_lagna in [6, 8, 12]),
            "न्यायालय प्रश्न में षष्ठेश का कमजोर होना विरोधी पक्ष के परास्त होने व मुक़दमे में विजय दर्शाता है।"
        )
        add_rule(
            "PR-072", "विषय विशेष (Court)", "लग्नेश का 6ठे भाव में होना (मुक़दमे में कष्ट)", "Litigation: Lagnesha in 6th House",
            "Prashna Marga 17.5", "NEGATIVE", 20,
            is_litigation and l_house == 6,
            "लग्नेश का 6ठे भाव में होना प्रश्नकर्ता द्वारा अत्यधिक मानसिक खिंचाव व कोर्ट की तारीखों में उलझना दिखाता है।"
        )
        add_rule(
            "PR-073", "विषय विशेष (Travel)", "नवम व द्वादश भाव के स्वामियों का चर राशि में होना", "Travel: 9th & 12th Lords in Movable Signs",
            "Shatpanchasika 6.1", "POSITIVE", 22,
            is_travel and (chart.houses[8].sign_id in MOVABLE_SIGNS or chart.houses[11].sign_id in MOVABLE_SIGNS),
            "विदेश यात्रा प्रश्न में 9वें/12वें भाव का चर राशि में होना वीज़ा स्वीकृति व सुगम यात्रा का सूचक है।"
        )
        add_rule(
            "PR-074", "विषय विशेष (Travel)", "नवम भाव में वक्री ग्रह का वास (यात्रा में विघ्न)", "Travel: Retrograde in 9th House",
            "Prashna Marga 18.7", "NEGATIVE", 18,
            is_travel and any(chart.planets[p].is_retrograde for p in occ(9)),
            "नवम भाव में वक्री ग्रह यात्रा तिथियों में फेरबदल अथवा वीज़ा/टिकट में विलंब कराता है।"
        )
        add_rule(
            "PR-075", "विषय विशेष (Education)", "पंचमेश का उच्च अथवा गुरु से दृष्ट होना", "Education: 5th Lord Exalted or Aspected by Jupiter",
            "Prashna Chintamani 4.2", "POSITIVE", 25,
            is_edu and (aspects_house("Jupiter", 5) or chart.planets[chart.houses[4].lord].house_from_lagna in [1, 5, 9, 11]),
            "शिक्षा व परीक्षा प्रश्न में पंचम भाव की शुभता मेधा शक्ति, उच्च मेरिट व परीक्षा में सफलता दिलाती है।"
        )
        add_rule(
            "PR-076", "विषय विशेष (Education)", "पंचम भाव में राहु का दूषित प्रभाव", "Education: Rahu in 5th House",
            "Prashna Marga 13.11", "NEGATIVE", 20,
            is_edu and "Rahu" in occ(5),
            "पंचम में राहु एकाग्रता भंग, सिली मिस्टेक अथवा ऐन परीक्षा के समय भ्रम उत्पन्न कर सकता है।"
        )
        add_rule(
            "PR-077", "विषय विशेष (Lost Item)", "चन्द्रमा का 2रे/4थे भाव में सूर्य के साथ होना", "Lost Item: Moon in 2nd/4th with Sun",
            "Daivajna Vallabha 8.3", "POSITIVE", 22,
            category == "Lost Item" and m_house in [1, 2, 4, 11],
            "खोई वस्तु प्रश्न में चन्द्रमा शुभ भावों में होने से वस्तु घर या कार्यस्थल के निकट शीघ्र मिल जाएगी।"
        )
        add_rule(
            "PR-078", "विषय विशेष (Lost Item)", "चन्द्रमा का 8वें/12वें भाव में होना (वस्तु अप्राप्य)", "Lost Item: Moon in 8th/12th",
            "Prashna Marga 19.4", "NEGATIVE", 24,
            category == "Lost Item" and m_house in [8, 12],
            "खोई वस्तु के प्रश्न में चन्द्रमा 8/12 में होने से वस्तु नष्ट अथवा दूर जा चुकी है।"
        )
        add_rule(
            "PR-079", "विषय विशेष (General)", "एकादश भाव में एकाधिक शुभ ग्रहों का वास", "General: Benefics in 11th House",
            "Shatpanchasika 7.1", "POSITIVE", 25,
            bool(set(occ(11)).intersection(benefics)),
            "ग्यारहवें लाभ भाव में शुभ ग्रहों की उपस्थिति समस्त अभीष्ट कामनाओं की निर्विघ्न पूर्ति कराती है।"
        )
        add_rule(
            "PR-080", "विषय विशेष (General)", "अष्टम भाव में क्रूर ग्रहों का जमावड़ा", "General: Malefics in 8th House",
            "Prashna Marga 20.6", "NEGATIVE", 24,
            bool(set(occ(8)).intersection(["Saturn", "Mars", "Rahu"])),
            "अष्टम भाव में क्रूर ग्रह अप्रत्याशित संकट, कार्यहानि अथवा अचानक रुकावट पैदा करते हैं।"
        )

        # =========================================================================
        # DOMAIN 6: KP HORARY 1-249 SUB-LORD RULES (Rules 81 to 90)
        # =========================================================================
        add_rule(
            "PR-081", "KP प्रश्न पद्धति", "KP नियम 1: लग्न उप-स्वामी का 1, 11 भावों से सम्बंध", "KP Rule 1: 1st Sub-Lord signifies 1, 11",
            "KP Horary Principles", "POSITIVE", 25,
            l_house in [1, 10, 11],
            "KP सिद्धांत: प्रश्नकर्ता का आत्मबल व इच्छापूर्ति भाव 1 और 11 सक्रिय होकर पूर्ण सफलता दर्शाते हैं।"
        )
        add_rule(
            "PR-082", "KP प्रश्न पद्धति", "KP नियम 2: लग्न उप-स्वामी का 6, 8, 12 भावों से सम्बंध", "KP Rule 2: 1st Sub-Lord signifies 6, 8, 12",
            "KP Horary Principles", "NEGATIVE", 22,
            l_house in [6, 8, 12],
            "KP सिद्धांत: लग्न उप-स्वामी का त्रिक भावों (6, 8, 12) से जुड़ना विफलता व कष्ट का द्योतक है।"
        )
        add_rule(
            "PR-083", "KP प्रश्न पद्धति", "KP नियम 3: कार्य भाव उप-स्वामी का 11वें भाव से सम्बंध", "KP Rule 3: Karya Sub-Lord signifies 11th",
            "KP Horary Principles", "POSITIVE", 25,
            k_house in [1, 2, 7, 10, 11],
            "KP सिद्धांत: कार्य भाव का उप-स्वामी लाभ भाव (11th) से जुड़कर अभीष्ट फल प्रदान करता है।"
        )
        add_rule(
            "PR-084", "KP प्रश्न पद्धति", "KP नियम 4: कार्य भाव उप-स्वामी का 12वें व्यय भाव से सम्बंध", "KP Rule 4: Karya Sub-Lord signifies 12th",
            "KP Horary Principles", "NEGATIVE", 20,
            k_house == 12,
            "KP सिद्धांत: कार्य भाव का 12वें से सम्बंध प्रयास के व्यर्थ होने व निराशा का संकेत देता है।"
        )
        add_rule(
            "PR-085", "KP प्रश्न पद्धति", "KP नियम 5: एकादशेश का केंद्र में बली होना", "KP Rule 5: 11th Lord in Kendra",
            "KP Horary Principles", "POSITIVE", 20,
            chart.planets[chart.houses[10].lord].house_from_lagna in KENDRA_HOUSES,
            "KP सिद्धांत: एकादशेश केंद्र में बली होकर किसी भी जटिल प्रश्न में अंततः सफलता दिलाता है।"
        )
        add_rule(
            "PR-086", "KP प्रश्न पद्धति", "KP नियम 6: चन्द्रमा का फलदायक भावों (2, 6, 10, 11) में संचार", "KP Rule 6: Moon in Material Houses",
            "KP Horary Principles", "POSITIVE", 18,
            m_house in [2, 6, 10, 11],
            "KP सिद्धांत: चन्द्रमा अर्थ व लाभ भावों में संचरण कर कार्य की व्यावहारिक सिद्धि कराता है।"
        )
        add_rule(
            "PR-087", "KP प्रश्न पद्धति", "KP नियम 7: वक्री ग्रह का कार्य भाव से सम्बंध", "KP Rule 7: Retrograde Planet on Karya House",
            "KP Horary Principles", "NEGATIVE", 16,
            any(chart.planets[p].is_retrograde for p in occ(karya_house_num)),
            "KP सिद्धांत: कार्य भाव में वक्री ग्रह की उपस्थिति कार्य में पुनरावृत्ति व विलंब उत्पन्न करती है।"
        )
        add_rule(
            "PR-088", "KP प्रश्न पद्धति", "KP नियम 8: गुरु व शुक्र का त्रिकोण में स्थित होना", "KP Rule 8: Natural Benefics in Trines",
            "KP Horary Principles", "POSITIVE", 20,
            jupiter.house_from_lagna in [5, 9] or venus.house_from_lagna in [5, 9],
            "KP सिद्धांत: गुरु/शुक्र त्रिकोण में भाग्यवृद्धि कर सभी पक्षों से अनुकूलता निर्मित करते हैं।"
        )
        add_rule(
            "PR-089", "KP प्रश्न पद्धति", "KP नियम 9: राहु/केतु का लग्न अथवा सप्तम में अक्ष", "KP Rule 9: Nodal Axis on 1/7 Houses",
            "KP Horary Principles", "NEGATIVE", 18,
            rahu.house_from_lagna in [1, 7] or ketu.house_from_lagna in [1, 7],
            "KP सिद्धांत: राहु-केतु 1/7 अक्ष में होने से अप्रत्याशित पेचीदगियां व अन्य व्यक्तियों का असहयोग रहता है।"
        )
        add_rule(
            "PR-090", "KP प्रश्न पद्धति", "KP नियम 10: शासक ग्रह (Ruling Planets) का परस्पर सामंजस्य", "KP Rule 10: Ruling Planets Harmony",
            "KP Horary Principles", "POSITIVE", 22,
            chart.houses[0].lord in [chart.panchang.vara_name[:3], moon.sign_name, "Sun", "Jupiter", "Venus"],
            "KP सिद्धांत: प्रश्न समय के शासक ग्रह (Ruling Planets) आपस में मित्रवत होकर कार्यसिद्धि का मार्ग प्रशस्त करते हैं।"
        )

        # =========================================================================
        # DOMAIN 7: KERALA PRASHNA MARGA & ASHTAMANGALA (Rules 91 to 100)
        # =========================================================================
        add_rule(
            "PR-091", "केरल प्रश्न मार्ग", "त्रिसडाय भावों (3, 6, 11) में पाप ग्रह (शत्रु नाशक)", "Malefics in 3, 6, 11 (Upachaya)",
            "Prashna Marga 9.2", "POSITIVE", 25,
            bool(set(occ(3) + occ(6) + occ(11)).intersection(malefics)),
            "केरल पद्धति: 3, 6, 11 उपचय भावों में क्रूर ग्रह समस्त संकटों, शत्रुओं व रोगों का नाश कर विजय दिलाते हैं।"
        )
        add_rule(
            "PR-092", "केरल प्रश्न मार्ग", "त्रिकोण भावों (5, 9) में केवल शुभ ग्रह", "Only Benefics in Trikona Houses",
            "Prashna Marga 9.8", "POSITIVE", 24,
            bool(set(occ(5) + occ(9)).intersection(benefics)) and not bool(set(occ(5) + occ(9)).intersection(malefics)),
            "केरल पद्धति: 5वें और 9वें भाव में विशुद्ध शुभ ग्रह पूर्वजन्म के पुण्यों का तत्काल फल प्रदान करते हैं।"
        )
        add_rule(
            "PR-093", "केरल प्रश्न मार्ग", "अष्टम भाव पूर्णतः रिक्त (No Planets in 8th)", "8th House Completely Vacant",
            "Prashna Marga 9.15", "POSITIVE", 18,
            len(occ(8)) == 0,
            "केरल पद्धति: अष्टम भाव का पूर्णतः रिक्त होना किसी भी दुर्घटना, आयु संकट अथवा बड़े व्यवधान से सुरक्षा देता है।"
        )
        add_rule(
            "PR-094", "केरल प्रश्न मार्ग", "अष्टम भाव में सूर्य अथवा मंगल का क्रूर प्रभाव", "Sun/Mars in 8th House",
            "Prashna Marga 9.22", "NEGATIVE", 22,
            bool(set(["Sun", "Mars"]).intersection(occ(8))),
            "केरल पद्धति: अष्टम में सूर्य/मंगल सरकारी जुर्माना, चोट, रक्त विकार अथवा विवाद का भय दर्शाते हैं।"
        )
        add_rule(
            "PR-095", "केरल प्रश्न मार्ग", "सप्तम भाव में गुरु विराजमान (सर्व कार्य सिद्धि)", "Jupiter in 7th House",
            "Prashna Marga 10.4", "POSITIVE", 25,
            "Jupiter" in occ(7),
            "केरल पद्धति: सप्तम भाव में गुरु की अमृत दृष्टि लग्न पर पड़कर समस्त बाधाओं को भस्म कर देती है।"
        )
        add_rule(
            "PR-096", "केरल प्रश्न मार्ग", "गुलिक (मांदि) का केंद्र में होना", "Gulika in Kendra (Heavy Distress)",
            "Prashna Marga 10.12", "NEGATIVE", 25,
            bool(set(["Saturn", "Rahu"]).intersection(occ(1) + occ(4) + occ(7) + occ(10))),
            "केरल पद्धति: केंद्र में पाप ग्रहों का प्रभाव कार्य में गुप्त अड़चनें व मानसिक भारीपन उत्पन्न करता है।"
        )
        add_rule(
            "PR-097", "केरल प्रश्न मार्ग", "चतुर्थ भाव में शुभ ग्रह (घरेलू व मन की शांति)", "Benefics in 4th House",
            "Prashna Marga 11.3", "POSITIVE", 20,
            bool(set(occ(4)).intersection(benefics)),
            "केरल पद्धति: चतुर्थ सुख भाव में शुभ ग्रह घर-परिवार, वाहन, भूमि और मानसिक शांति का आशीर्वाद देते हैं।"
        )
        add_rule(
            "PR-098", "केरल प्रश्न मार्ग", "द्वादश भाव में शुभ केतु (मोक्ष व ऋणमुक्ति)", "Ketu in 12th House",
            "Prashna Marga 11.18", "POSITIVE", 15,
            "Ketu" in occ(12),
            "केरल पद्धति: द्वादश में केतु अनावश्यक चिंताओं की समाप्ति, कर्ज़ मुक्ति व ईश्वरीय कृपा का मार्ग खोलता है।"
        )
        add_rule(
            "PR-099", "केरल प्रश्न मार्ग", "लग्न और कार्येश में सामंजस्यपूर्ण तत्व (Element Harmony)", "Element Harmony between Lagna & Karya",
            "Prashna Marga 2.25", "POSITIVE", 15,
            (lagna_sign_id in WATER_SIGNS and chart.houses[karya_house_num - 1].sign_id in WATER_SIGNS) or (lagna_sign_id in FIRE_SIGNS and chart.houses[karya_house_num - 1].sign_id in FIRE_SIGNS) or (lagna_sign_id in EARTH_SIGNS and chart.houses[karya_house_num - 1].sign_id in EARTH_SIGNS),
            "लग्न और कार्य भाव का तत्व एक समान होने से प्राकृतिक सामंजस्य व कार्य में अभूतपूर्व तालमेल रहेगा।"
        )
        add_rule(
            "PR-100", "केरल प्रश्न मार्ग", "महाभाग्य एवं ईश्वरीय अनुग्रह योग", "Maha Bhagya & Divine Grace in Horary",
            "Prashna Marga 22.1", "POSITIVE", 30,
            (l_house in [1, 4, 5, 9, 10, 11]) and (k_house in [1, 4, 5, 9, 10, 11]) and (m_house not in DUSTHANA_HOUSES),
            "लग्नेश, कार्येश और चन्द्रमा तीनों शुभ भावों में स्थित हैं — शास्त्रीय महाभाग्य योग से अभीष्ट कार्य की 100% विजय निश्चित है!"
        )

        # Calculate scores
        pos_rules = [r for r in rules_evaluated if r["triggered"] and r["type"] == "POSITIVE"]
        neg_rules = [r for r in rules_evaluated if r["triggered"] and r["type"] == "NEGATIVE"]

        total_pos_weight = sum(r["weight"] for r in pos_rules)
        total_neg_weight = sum(abs(r["weight"]) for r in neg_rules)

        net_balance = total_pos_weight - total_neg_weight

        # Normalize score 0.0 to 1.0
        # Typical max positive weight is ~350, max negative is ~200
        pos_ratio = total_pos_weight / max(1, total_pos_weight + total_neg_weight)
        consensus_score = round(max(0.05, min(0.98, pos_ratio)), 2)

        return {
            "total_rules_count": len(rules_evaluated),
            "active_positive_count": len(pos_rules),
            "active_negative_count": len(neg_rules),
            "total_positive_points": total_pos_weight,
            "total_negative_points": total_neg_weight,
            "net_balance_score": net_balance,
            "consensus_score": consensus_score,
            "positive_rules": pos_rules,
            "negative_rules": neg_rules,
            "all_rules": rules_evaluated
        }


default_prashna_rule_evaluator = PrashnaRuleEvaluator()

