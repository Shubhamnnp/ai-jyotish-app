"""
Kundali Milan (Horoscope Matching / Synastry) Engine for JyotishOS.
Implements the classical 36-Guna Ashtakoota matching system:
Varna (1), Vashya (2), Tara (3), Yoni (4), Graha Maitri (5), Gana (6), Bhakoot (7), Nadi (8),
along with classical cancellations (Nadi/Bhakoot dosha) and mutual Manglik Dosha analysis.
"""

from typing import Dict, Any, List, Tuple
from typing import Dict, Any, List, Tuple, Optional
from pydantic import BaseModel, Field
from ..core.constants import SIGN_LORDS, NATURAL_FRIENDS, NATURAL_ENEMIES
from ..core.constants import SIGN_LORDS, NATURAL_FRIENDS, NATURAL_ENEMIES, SIGN_NAMES
from ..core.models import BirthData, KundaliChart
from ..core.calculator import default_chart_calculator


# 27 Nakshatra Yonis (Animal Symbols)
NAKSHATRA_YONIS = [
    "Ashwa", "Gaja", "Mesha", "Sarpa", "Mriga", "Shwana", "Marjara", "Mushaka", "Gau",
    "Mahisha", "Vyaghra", "Vanara", "Nakula", "Simha", "Ashwa", "Gaja", "Mesha", "Sarpa",
    "Mriga", "Shwana", "Marjara", "Mushaka", "Gau", "Mahisha", "Vyaghra", "Vanara", "Nakula"
]

# Sworn Enemy Yoni pairs (0 points)
ENEMY_YONIS = [
    ("Gau", "Vyaghra"), ("Ashwa", "Mahisha"), ("Gaja", "Simha"),
    ("Sarpa", "Nakula"), ("Shwana", "Mriga"), ("Marjara", "Mushaka"), ("Mesha", "Vanara")
]

# 27 Nakshatra Ganas (0: Deva, 1: Manushya, 2: Rakshasa)
NAKSHATRA_GANAS = [
    0, 1, 2, 1, 0, 1, 0, 0, 2,
    2, 1, 1, 0, 2, 0, 2, 0, 2,
    2, 1, 1, 0, 2, 1, 1, 1, 0
]

# 27 Nakshatra Nadis (0: Adi, 1: Madhya, 2: Antya)
NAKSHATRA_NADIS = [
    0, 1, 2, 2, 1, 0, 0, 1, 2,
    2, 1, 0, 0, 1, 2, 2, 1, 0,
    0, 1, 2, 2, 1, 0, 0, 1, 2
]


class AshtakootaScore(BaseModel):
    varna: float
    vashya: float
    tara: float
    yoni: float
    graha_maitri: float
    gana: float
    bhakoot: float
    nadi: float
    total_score: float
    max_score: float = 36.0
    verdict: str
    nadi_dosha: bool = False
    nadi_dosha_cancelled: bool = False
    bhakoot_dosha: bool = False
    bhakoot_dosha_cancelled: bool = False
    groom_manglik: bool = False
    bride_manglik: bool = False
    manglik_match: bool = False
    manglik_cancellation_reason: str = ""
    nadi_cancellation_reason: str = ""
    recommendation_hi: str
    recommendation_en: str
    deep_analysis: Optional[Dict[str, Any]] = None


class MilanService:
    """Calculates 36-Guna Ashtakoota and synastry compatibility."""

    def match_charts(self, groom_data: BirthData, bride_data: BirthData) -> AshtakootaScore:
        """Runs full Ashtakoota and Manglik matching between Groom and Bride."""
        groom_chart = default_chart_calculator.calculate_chart(groom_data)
        bride_chart = default_chart_calculator.calculate_chart(bride_data)
        return self.match_computed_charts(groom_chart, bride_chart)

    def match_computed_charts(self, groom_chart: KundaliChart, bride_chart: KundaliChart) -> AshtakootaScore:
        """Matches pre-computed charts."""
        g_moon = groom_chart.planets["Moon"]
        b_moon = bride_chart.planets["Moon"]

        g_nak_idx = g_moon.nakshatra_id - 1
        b_nak_idx = b_moon.nakshatra_id - 1

        g_sign_id = g_moon.sign_id
        b_sign_id = b_moon.sign_id

        # 1. Varna (1 pt)
        varna_score = self._calc_varna(g_sign_id, b_sign_id)

        # 2. Vashya (2 pts)
        vashya_score = self._calc_vashya(g_sign_id, b_sign_id)

        # 3. Tara (3 pts)
        tara_score = self._calc_tara(g_nak_idx, b_nak_idx)

        # 4. Yoni (4 pts)
        yoni_score = self._calc_yoni(g_nak_idx, b_nak_idx)

        # 5. Graha Maitri (5 pts)
        maitri_score = self._calc_graha_maitri(g_sign_id, b_sign_id)

        # 6. Gana (6 pts)
        gana_score = self._calc_gana(g_nak_idx, b_nak_idx)

        # 7. Bhakoot (7 pts) with cancellation
        bhakoot_score, bhakoot_dosha, bhakoot_canc = self._calc_bhakoot(g_sign_id, b_sign_id)

        # 8. Nadi (8 pts) with cancellation
        nadi_score, nadi_dosha, nadi_canc, nadi_reason = self._calc_nadi(g_nak_idx, b_nak_idx, g_moon.nakshatra_pada, b_moon.nakshatra_pada, g_sign_id, b_sign_id)

        total = round(varna_score + vashya_score + tara_score + yoni_score + maitri_score + gana_score + bhakoot_score + nadi_score, 1)

        # Advanced Manglik Analysis & Cancellations
        g_manglik = self._is_manglik(groom_chart)
        b_manglik = self._is_manglik(bride_chart)
        manglik_match, manglik_canc_reason = self._evaluate_manglik_cancellation(groom_chart, bride_chart, g_manglik, b_manglik)

        if total >= 28:
            verdict = "उत्कृष्ट (Excellent)"
            rec_hi = f"कुल 36 में से {total} गुण मिलते हैं। विवाह अत्यन्त शुभ और अनुकूल है।"
            rec_en = f"Outstanding compatibility with {total}/36 gunas. Highly recommended."
        elif total >= 18:
            verdict = "मध्यम (Favorable)"
            rec_hi = f"कुल 36 में से {total} गुण मिलते हैं। विवाह उत्तम रहेगा।"
            rec_en = f"Favorable match with {total}/36 gunas. Suitable for marriage."
        else:
            verdict = "अल्प अनुकूल (Challenging)"
            rec_hi = f"कुल 36 में से {total} गुण मिलते हैं। गुणों की संख्या 18 से कम है।"
            rec_en = f"Low compatibility ({total}/36 gunas). Astrological remedies recommended."

        # Deep Shastriya Synastry Analysis
        deep_analysis = self.analyze_deep_synastry(groom_chart, bride_chart)

        return AshtakootaScore(
            varna=varna_score,
            vashya=vashya_score,
            tara=tara_score,
            yoni=yoni_score,
            graha_maitri=maitri_score,
            gana=gana_score,
            bhakoot=bhakoot_score,
            nadi=nadi_score,
            total_score=total,
            verdict=verdict,
            nadi_dosha=nadi_dosha,
            nadi_dosha_cancelled=nadi_canc,
            nadi_cancellation_reason=nadi_reason,
            bhakoot_dosha=bhakoot_dosha,
            bhakoot_dosha_cancelled=bhakoot_canc,
            groom_manglik=g_manglik,
            bride_manglik=b_manglik,
            manglik_match=manglik_match,
            manglik_cancellation_reason=manglik_canc_reason,
            recommendation_hi=rec_hi,
            recommendation_en=rec_en
            recommendation_en=rec_en,
            deep_analysis=deep_analysis
        )

    def _calc_varna(self, g_sign: int, b_sign: int) -> float:
        """Varna Koota (1 pt): Brahmin (Water), Kshatriya (Fire), Vaishya (Earth), Shudra (Air)."""
        ranks = {4: 4, 8: 4, 12: 4, 1: 3, 5: 3, 9: 3, 2: 2, 6: 2, 10: 2, 3: 1, 7: 1, 11: 1}
        return 1.0 if ranks.get(g_sign, 2) >= ranks.get(b_sign, 2) else 0.0

    def _calc_vashya(self, g_sign: int, b_sign: int) -> float:
        """Vashya Koota (2 pts)."""
        if g_sign == b_sign:
            return 2.0
        # Same element harmonic
        if (g_sign - 1) % 4 == (b_sign - 1) % 4:
            return 1.5
        return 1.0

    def _calc_tara(self, g_nak: int, b_nak: int) -> float:
        """Tara Koota (3 pts): Birth star distance compatibility."""
        diff_gb = (b_nak - g_nak) % 9
        diff_bg = (g_nak - b_nak) % 9
        subh = [2, 4, 6, 8, 9]
        pts = 0.0
        if diff_gb in subh: pts += 1.5
        if diff_bg in subh: pts += 1.5
        return pts

    def _calc_yoni(self, g_nak: int, b_nak: int) -> float:
        """Yoni Koota (4 pts): Animal compatibility."""
        y_g = NAKSHATRA_YONIS[g_nak]
        y_b = NAKSHATRA_YONIS[b_nak]
        if y_g == y_b:
            return 4.0
        if (y_g, y_b) in ENEMY_YONIS or (y_b, y_g) in ENEMY_YONIS:
            return 0.0
        return 2.0

    def _calc_graha_maitri(self, g_sign: int, b_sign: int) -> float:
        """Graha Maitri (5 pts): Sign lord friendship."""
        from ..core.constants import SIGN_NAMES
        g_lord = SIGN_LORDS[SIGN_NAMES[g_sign - 1]]
        b_lord = SIGN_LORDS[SIGN_NAMES[b_sign - 1]]
        if g_lord == b_lord:
            return 5.0
        g_friends = NATURAL_FRIENDS.get(g_lord, [])
        b_friends = NATURAL_FRIENDS.get(b_lord, [])
        if b_lord in g_friends and g_lord in b_friends:
            return 5.0
        if b_lord in g_friends or g_lord in b_friends:
            return 3.0
        return 1.0

    def _calc_gana(self, g_nak: int, b_nak: int) -> float:
        """Gana Koota (6 pts): Deva, Manushya, Rakshasa."""
        g_gana = NAKSHATRA_GANAS[g_nak]
        b_gana = NAKSHATRA_GANAS[b_nak]
        if g_gana == b_gana:
            return 6.0
        if (g_gana == 0 and b_gana == 1) or (g_gana == 1 and b_gana == 0):
            return 5.0
        if g_gana == 2 or b_gana == 2:
            return 0.0
        return 3.0

    def _calc_bhakoot(self, g_sign: int, b_sign: int) -> Tuple[float, bool, bool]:
        """Bhakoot (7 pts) with classical cancellation."""
        from ..core.constants import SIGN_NAMES
        diff = ((g_sign - b_sign) % 12) + 1
        # Inauspicious: 2-12, 6-8, 9-5
        if diff in (2, 12, 6, 8, 5, 9):
            # Check cancellation: same sign lords or mutual friends
            g_lord = SIGN_LORDS[SIGN_NAMES[g_sign - 1]]
            b_lord = SIGN_LORDS[SIGN_NAMES[b_sign - 1]]
            if g_lord == b_lord or b_lord in NATURAL_FRIENDS.get(g_lord, []):
                return 7.0, True, True  # Cancelled
            return 0.0, True, False  # Dosha active
        return 7.0, False, False

    def _calc_nadi(self, g_nak: int, b_nak: int, g_pada: int, b_pada: int, g_sign: int, b_sign: int) -> Tuple[float, bool, bool, str]:
        """Nadi (8 pts) with classical shastriya cancellations."""
        g_nadi = NAKSHATRA_NADIS[g_nak]
        b_nadi = NAKSHATRA_NADIS[b_nak]
        if g_nadi != b_nadi:
            return 8.0, False, False, "नाड़ी दोष नहीं है (भिन्न नाड़ी)।"

        # Same Nadi -> Check classical cancellations
        # Cancellation 1: Same nakshatra but different charan/pada
        if g_nak == b_nak and g_pada != b_pada:
            return 8.0, True, True, "नाड़ी दोष परिहार: एक ही नक्षत्र है परन्तु चरण/पाद भिन्न हैं, अतः दोष निष्प्रभावी।"

        # Cancellation 2: Different rashi same nakshatra (cross-boundary)
        if g_sign != b_sign:
            return 8.0, True, True, "नाड़ी दोष परिहार: राशि भिन्न होने के कारण नाड़ी दोष स्वतः समाप्त माना जाता है।"

        # Cancellation 3: Rohini, Ardra, Pushya, Vishakha, Anuradha, Shravana exempt
        exempt_naks = [2, 5, 7, 15, 16, 21, 25] # Krittika, Mrigashira, Pushya, etc.
        if g_nak in exempt_naks or b_nak in exempt_naks:
            return 8.0, True, True, "नाड़ी दोष परिहार: शास्त्रीय मान्यतानुसार यह नक्षत्र नाड़ी दोष से मुक्त माना गया है।"

        return 0.0, True, False, "गंभीर नाड़ी दोष सक्रिय है। स्वास्थ्य एवं संतान पक्ष में ध्यान देने की आवश्यकता है।"

    def _is_manglik(self, chart: KundaliChart) -> bool:
        """Checks Manglik Dosha from Lagna and Moon (houses 1, 2, 4, 7, 8, 12)."""
        mars = chart.planets.get("Mars")
        if not mars:
            return False
        manglik_houses = [1, 2, 4, 7, 8, 12]
        return mars.house_from_lagna in manglik_houses or getattr(mars, 'house_from_moon', mars.house_from_lagna) in manglik_houses

    def _evaluate_manglik_cancellation(
        self,
        groom_chart: KundaliChart,
        bride_chart: KundaliChart,
        g_manglik: bool,
        b_manglik: bool
    ) -> Tuple[bool, str]:
        """
        Evaluates classical Manglik cancellations and balancing:
        - Both Manglik: Perfect mutual cancellation
        - One Manglik: Check Saturn, Rahu, or Mars in counterpart's afflicted house
        - Sign specific cancellations (Mars in Aries in 1st, Scorpio in 4th, Capricorn in 7th, etc.)
        """
        if g_manglik and b_manglik:
            return True, "समान मांगलिक सामंजस्य: वर और कन्या दोनों मांगलिक हैं, अतः एक-दूसरे का दोष स्वतः संतुलित हो जाता है।"

        if not g_manglik and not b_manglik:
            return True, "दोष रहित: वर और कन्या दोनों की कुण्डली मांगलिक दोष से पूर्णतः मुक्त है।"

        # If one is manglik and other is not -> check counterpart malefic counter-balance
        manglik_chart = groom_chart if g_manglik else bride_chart
        counter_chart = bride_chart if g_manglik else groom_chart
        m_person = "वर" if g_manglik else "कन्या"
        c_person = "कन्या" if g_manglik else "वर"

        mars_h = manglik_chart.planets["Mars"].house_from_lagna
        mars_sign = manglik_chart.planets["Mars"].sign_name

        # Sign-specific exemptions (BPHS / Muhurta Chintamani)
        # Mars in Aries in 1st, Scorpio in 4th, Capricorn in 7th, Aquarius in 8th, Sagittarius in 12th
        if (mars_h == 1 and mars_sign == "Aries") or \
           (mars_h == 4 and mars_sign == "Scorpio") or \
           (mars_h == 7 and mars_sign == "Capricorn") or \
           (mars_h == 8 and mars_sign == "Aquarius") or \
           (mars_h == 12 and mars_sign == "Sagittarius"):
            return True, f"मांगलिक परिहार: {m_person} का मंगल अपनी स्वराशि/उच्च राशि (भाव {mars_h} में {mars_sign}) में होने से दोष प्रभावहीन हो गया है।"

        # Counter-balance: If counterpart has Saturn, Rahu or Mars in same afflicted houses
        c_sat_h = counter_chart.planets.get("Saturn", None)
        c_rahu_h = counter_chart.planets.get("Rahu", None)
        counter_malefic_houses = []
        if c_sat_h: counter_malefic_houses.append(c_sat_h.house_from_lagna)
        if c_rahu_h: counter_malefic_houses.append(c_rahu_h.house_from_lagna)

        if mars_h in counter_malefic_houses or 7 in counter_malefic_houses:
            return True, f"ग्रह साम्य परिहार: {m_person} के भाव {mars_h} के मंगल के सामने {c_person} की कुण्डली में शनि/राहु की स्थिति होने से मंगल दोष का शमन हो जाता है।"

        # Check Jupiter aspect on Mars
        jup = manglik_chart.planets.get("Jupiter")
        if jup and jup.house_from_lagna in [1, 4, 7, 10]:
            return True, f"गुरु दृष्टि परिहार: {m_person} की कुण्डली में देवगुरु बृहस्पति केन्द्र में स्थित होकर मांगलिक दोष का शमन कर रहे हैं।"

        return False, f"असंतुलित मांगलिक: केवल {m_person} मांगलिक हैं और {c_person} की कुण्डली में पर्याप्त परिहार नहीं है। विवाह पूर्व कुंभ/अर्क विवाह उपाय अनुशंसित है।"

    def _get_sphuta_details(self, long_val: float) -> Tuple[int, str, int, str, bool, bool]:
        norm_long = long_val % 360.0
        sign_id = int(norm_long / 30.0) + 1
        sign_name = SIGN_NAMES[sign_id - 1]
        deg_in_sign = norm_long % 30.0
        nav_div = int(deg_in_sign / (30.0 / 9.0))
        sign_idx = sign_id - 1
        # Element: 0=Fire, 1=Earth, 2=Air, 3=Water
        elem = sign_idx % 4
        start_signs = {0: 0, 1: 9, 2: 6, 3: 3}  # Aries, Cap, Libra, Cancer
        nav_sign_idx = (start_signs[elem] + nav_div) % 12
        nav_sign_id = nav_sign_idx + 1
        nav_sign_name = SIGN_NAMES[nav_sign_idx]
        is_sign_odd = (sign_id % 2 != 0)
        is_nav_odd = (nav_sign_id % 2 != 0)
        return sign_id, sign_name, nav_sign_id, nav_sign_name, is_sign_odd, is_nav_odd

    def analyze_deep_synastry(self, g_chart: KundaliChart, b_chart: KundaliChart) -> Dict[str, Any]:
        """Calculates in-depth Shastriya Synastry for Groom and Bride:

        1. Husband-Wife Temperament & Mutual Behavior
        2. Relationship Reliability & Marital Longevity (Upapada Lagna)
        3. Progeny / Children Analysis (Beeja & Kshetra Sphuta)
        4. In-Laws Support & Relations (Sasural Paksha)
        5. Spouse Support & Post-Marital Prosperity (Bhagyodaya)
        6. Summary Compatibility & Vedic Remedies
        """
        # 1. Pati-Patni Vyavahar & Svabhav
        g_lagna_lord = SIGN_LORDS.get(g_chart.lagna_sign_name, "Mars")
        b_lagna_lord = SIGN_LORDS.get(b_chart.lagna_sign_name, "Venus")

        if g_lagna_lord == b_lagna_lord:
            vyavahar_title = "समान लग्नेश (अत्युत्तम वैचारिक सामंजस्य)"
            vyavahar_score = 95
            vyavahar_desc = (
                f"वर और कन्या दोनों के लग्नेश एक ही ग्रह ({g_lagna_lord}) हैं। "
                "दोनों के जीवन मूल्य, रुचियां एवं सोचने का दृष्टिकोण एक जैसा रहेगा। "
                "पारस्परिक समझदारी, आदर एवं भावनात्मक निकटता उच्च कोटि की रहेगी।"
            )
        elif b_lagna_lord in NATURAL_FRIENDS.get(g_lagna_lord, []) and g_lagna_lord in NATURAL_FRIENDS.get(b_lagna_lord, []):
            vyavahar_title = "परस्पर स्वाभाविक मित्र लग्नेश (सद्भाव एवं सहयोग)"
            vyavahar_score = 88
            vyavahar_desc = (
                f"वर के लग्नेश ({g_lagna_lord}) एवं कन्या के लग्नेश ({b_lagna_lord}) आपस में स्वाभाविक मित्र हैं। "
                "विपरीत परिस्थितियों में भी दोनों एक-दूसरे का संबल बनेंगे। आपसी संवाद मधुर एवं उत्साहवर्धक रहेगा।"
            )
        elif b_lagna_lord in NATURAL_ENEMIES.get(g_lagna_lord, []) or g_lagna_lord in NATURAL_ENEMIES.get(b_lagna_lord, []):
            vyavahar_title = "भिन्न दृष्टिकोण (परस्पर धैर्य एवं समझदारी आवश्यक)"
            vyavahar_score = 65
            vyavahar_desc = (
                f"वर के लग्नेश ({g_lagna_lord}) और कन्या के लग्नेश ({b_lagna_lord}) में नैसर्गिक शत्रुता है। "
                "स्वभाव, निर्णय लेने की गति अथवा प्राथमिकताओं में अंतर हो सकता है। "
                "अहंकार के टकराव से बचकर परस्पर विचारों का सम्मान करना दांपत्य को सुखद बनाएगा।"
            )
        else:
            vyavahar_title = "तटस्थ/सम भाव लग्नेश (व्यावहारिक संतुलन)"
            vyavahar_score = 78
            vyavahar_desc = (
                f"वर के लग्नेश ({g_lagna_lord}) व कन्या के लग्नेश ({b_lagna_lord}) सम भाव में हैं। "
                "दांपत्य जीवन में व्यावहारिक संतुलन रहेगा। सामान्य समझदारी से सभी पारिवारिक दायित्व सुचारू रहेंगे।"
            )

        # Moon Elements
        elem_names = ["अग्नि तत्त्व (Fire)", "पृथ्वी तत्त्व (Earth)", "वायु तत्त्व (Air)", "जल तत्त्व (Water)"]
        g_elem_idx = (g_chart.planets["Moon"].sign_id - 1) % 4
        b_elem_idx = (b_chart.planets["Moon"].sign_id - 1) % 4
        g_elem = elem_names[g_elem_idx]
        b_elem = elem_names[b_elem_idx]

        if g_elem_idx == b_elem_idx:
            element_desc = f"दोनों की चंद्र राशि एक ही तत्त्व ({g_elem}) में है, जिससे मन का स्पंदन और भावनाएं एक समान रहेंगी।"
        elif (g_elem_idx, b_elem_idx) in [(0, 2), (2, 0), (1, 3), (3, 1)]:
            element_desc = f"वर ({g_elem}) और कन्या ({b_elem}) पूरक तत्त्व हैं। यह योग एक-दूसरे को नई ऊर्जा, प्रेरणा व संबल प्रदान करता है।"
        elif (g_elem_idx, b_elem_idx) in [(0, 3), (3, 0)]:
            element_desc = f"वर ({g_elem}) और कन्या ({b_elem}) अग्नि-जल संयोग में हैं। कभी-कभी क्रोध या अति-भावुकता से बचें; शांत मन से संवाद रखें।"
        else:
            element_desc = f"वर ({g_elem}) व कन्या ({b_elem}) का स्वभाव भिन्न शैलियों का है; व्यावहारिक तालमेल से मधुरता रहेगी।"

        # 2. Relationship Reliability & Marital Longevity
        g_ul_name = "Libra"
        b_ul_name = "Gemini"
        g_ul_id = 7
        b_ul_id = 3
        if g_chart.jaimini and g_chart.jaimini.arudha_padas:
            g_ul_id = g_chart.jaimini.arudha_padas.get("UL", 7)
            g_ul_name = g_chart.jaimini.arudha_pada_names.get("UL", "Libra")
        if b_chart.jaimini and b_chart.jaimini.arudha_padas:
            b_ul_id = b_chart.jaimini.arudha_padas.get("UL", 3)
            b_ul_name = b_chart.jaimini.arudha_pada_names.get("UL", "Gemini")

        ul_dist = ((b_ul_id - g_ul_id) % 12) + 1
        if ul_dist in (1, 5, 9, 7):
            rel_title = "अटूट दांपत्य निष्ठा एवं दीर्घायु संबंध"
            rel_score = 92
            rel_desc = (
                f"महर्षि जैमिनी के उपपद लग्न (UL) सूत्र अनुसार वर का उपपद ({g_ul_name}) व कन्या का उपपद ({b_ul_name}) "
                "परस्पर त्रिकोण अथवा समसप्तक में हैं। यह जीवनभर एक-दूसरे के प्रति समर्पण, विश्वास, सामाजिक मर्यादा "
                "तथा संकटों में भी कभी साथ न छोड़ने का पक्का योग बनाता है।"
            )
        elif ul_dist in (3, 4, 10, 11):
            rel_title = "स्थिर एवं अनुकूल दांपत्य निष्ठा"
            rel_score = 82
            rel_desc = (
                f"दोनों के उपपद लग्न ({g_ul_name} व {b_ul_name}) केंद्र व उपचय संबंध में हैं। "
                "विवाह के उपरांत दोनों में आपसी भरोसा दिनों-दिन गहरा होगा और पारिवारिक संबंध सुदृढ़ रहेंगे।"
            )
        else:
            rel_title = "पारदर्शिता एवं सतर्कता आवश्यक"
            rel_score = 68
            rel_desc = (
                f"दोनों के उपपद लग्न ({g_ul_name} व {b_ul_name}) परस्पर २/१२ या ६/८ स्थिति में हैं। "
                "दांपत्य में किसी तीसरे व्यक्ति या बाहरी रिश्तेदारों की बातों में आकर संदेह न करें; "
                "आपसी खुलापन व पारदर्शिता संबंध को अटूट बनाए रखेगी।"
            )

        # 3. Progeny / Children Analysis & Beeja/Kshetra Sphuta
        bs_long = (g_chart.planets["Sun"].longitude + g_chart.planets["Venus"].longitude + g_chart.planets["Jupiter"].longitude) % 360.0
        bs_sign_id, bs_sign_name, bs_nav_id, bs_nav_name, bs_s_odd, bs_n_odd = self._get_sphuta_details(bs_long)

        if bs_s_odd and bs_n_odd:
            bs_status = "उत्कृष्ट एवं परम ओजस्वी बीज बल"
            bs_desc = f"बीज स्फुट ({bs_sign_name} राशि, {bs_nav_name} नवांश) दोनों विषम राशियों में हैं। वर का बीज बल शास्त्रानुसार परम पुष्ट व ओजस्वी है।"
            bs_score = 95
        elif bs_s_odd or bs_n_odd:
            bs_status = "मध्यम बीज बल"
            bs_desc = f"बीज स्फुट ({bs_sign_name} राशि, {bs_nav_name} नवांश) में एक विषम व एक सम है। वर का बीज बल संतुलित है, समय पर संतान प्राप्ति होगी।"
            bs_score = 75
        else:
            bs_status = "अल्प/संवेदनशील बीज बल"
            bs_desc = f"बीज स्फुट ({bs_sign_name} राशि, {bs_nav_name} नवांश) दोनों सम राशियों में हैं। सूर्य अर्घ्य व देवगुरु बृहस्पति की उपासना हितकर रहेगी।"
            bs_score = 55

        ks_long = (b_chart.planets["Moon"].longitude + b_chart.planets["Mars"].longitude + b_chart.planets["Jupiter"].longitude) % 360.0
        ks_sign_id, ks_sign_name, ks_nav_id, ks_nav_name, ks_s_odd, ks_n_odd = self._get_sphuta_details(ks_long)

        if (not ks_s_odd) and (not ks_n_odd):
            ks_status = "उत्कृष्ट एवं परम फलदायी क्षेत्र बल"
            ks_desc = f"क्षेत्र स्फुट ({ks_sign_name} राशि, {ks_nav_name} नवांश) दोनों सम राशियों में हैं। कन्या का क्षेत्र बल परम उर्वर व पुष्ट है। मातृत्व क्षमता उत्तम है।"
            ks_score = 95
        elif (not ks_s_odd) or (not ks_n_odd):
            ks_status = "मध्यम क्षेत्र बल"
            ks_desc = f"क्षेत्र स्फुट ({ks_sign_name} राशि, {ks_nav_name} नवांश) में एक सम व एक विषम है। मातृत्व क्षमता सामान्य व संतुलित है।"
            ks_score = 75
        else:
            ks_status = "अल्प/संवेदनशील क्षेत्र बल"
            ks_desc = f"क्षेत्र स्फुट ({ks_sign_name} राशि, {ks_nav_name} नवांश) दोनों विषम राशियों में हैं। गर्भाधान पूर्व संतान गोपाल मंत्र का जप कल्याणकारी रहेगा।"
            ks_score = 55

        santana_avg = round((bs_score + ks_score) / 2)
        if santana_avg >= 85:
            children_count = "२ से ३ संतान का प्रबल एवं उत्तम योग"
            lineage_text = (
                "बीज व क्षेत्र स्फुट के अत्यंत अनुकूल होने से वंश वृद्धि निर्बाध रूप से होगी। "
                "संतान सद्गुणी, आज्ञाकारी, कुलदीपक एवं परिवार का यश बढ़ाने वाली होगी। "
                "माता-पिता को संतान का पूर्ण सुख एवं वृद्धावस्था में उत्तम सेवा प्राप्त होगी।"
            )
            first_child_desc = "प्रथम संतान ओजस्वी, नेतृत्व क्षमता से युक्त एवं परिवार के लिए भाग्यशाली सिद्ध होगी।"
        elif santana_avg >= 70:
            children_count = "१ से २ संतान का सुखद योग"
            lineage_text = (
                "संतान सुख सामान्य समय पर प्राप्त होगा। परिवार में खुशहाली रहेगी तथा संतान विद्या व संस्कार में आगे रहेगी।"
            )
            first_child_desc = "प्रथम संतान बुद्धिमान, शांत स्वभाव एवं माता-पिता के प्रति समर्पित रहेगी।"
        else:
            children_count = "१ संतान का योग (धार्मिक अनुष्ठान अनुशंसित)"
            lineage_text = (
                "संतान प्राप्ति में किंचित विलंब या संवेदनशीलता संभव है। विवाह उपरांत भगवान कृष्ण के "
                "संतान गोपाल स्वरूप का नियमित पूजन व चिकित्सकीय मार्गदर्शन से पूर्ण संतति सुख मिलेगा।"
            )
            first_child_desc = "संतान धर्मपरायण एवं कुल परंपरा का निर्वहन करने वाली होगी।"

        # 4. Sasural Paksha se Sahayog
        g_h8_planets = [p for p, obj in g_chart.planets.items() if obj.house_from_lagna == 8]
        if not g_h8_planets:
            groom_sasural_desc = "वर को ससुराल पक्ष से भरपूर मान-सम्मान, आतिथ्य एवं स्नेह मिलेगा। ससुर व सासू माँ का वर के प्रति अपनत्व रहेगा।"
        else:
            groom_sasural_desc = "वर को ससुराल पक्ष से औपचारिक व आदरयुक्त संबंध बनाए रखना चाहिए। आर्थिक लेन-देन में पारदर्शिता रखें।"

        bride_sasural_desc = (
            "कन्या को ससुराल में कुलवधू के रूप में उचित सम्मान व बेटी जैसा स्नेह मिलने का सुंदर योग है। "
            "कन्या अपनी समझदारी व सेवाभाव से ससुराल के सभी सदस्यों का दिल जीत लेगी।"
        )
        sasural_score = 85

        # 5. Patni ka Sahayog & Bhagyodaya
        g_7th_sign_id = ((g_chart.lagna_sign_id - 1 + 6) % 12) + 1
        g_7th_lord = SIGN_LORDS.get(SIGN_NAMES[g_7th_sign_id - 1], "Venus")
        g_7th_lord_h = g_chart.planets.get(g_7th_lord).house_from_lagna if g_chart.planets.get(g_7th_lord) else 7

        if g_7th_lord_h in (1, 2, 4, 7, 9, 10, 11):
            bhagyodaya_title = "विवाह उपरांत तीव्र भाग्योदय योग (Post-Marital Prosperity)"
            prosperity_score = 92
            bhagyodaya_desc = (
                f"वर की कुण्डली में सप्तमेश ({g_7th_lord}) केंद्र/त्रिकोण अथवा धन भाव ({g_7th_lord_h}वें भाव) में स्थित हैं। "
                "बृहत्पाराशर होराशास्त्र अनुसार विवाह के पश्चात जातक का वास्तविक भाग्योदय होगा। "
                "करियर में पदोन्नति, व्यापार में विस्तार, नया गृह/वाहन तथा आर्थिक समृद्धि में तेजी से वृद्धि होगी।"
            )
        else:
            bhagyodaya_title = "स्थिर एवं संतुलित भाग्योदय"
            prosperity_score = 78
            bhagyodaya_desc = (
                "विवाह के बाद दोनों के संयुक्त प्रयासों व बचत की नीति से परिवार की वित्तीय स्थिति निरंतर सुदृढ़ होगी।"
            )

        b_10th_planets = [p for p, obj in b_chart.planets.items() if obj.house_from_lagna == 10]
        sun_obj = b_chart.planets.get("Sun")
        if b_10th_planets or (sun_obj and sun_obj.house_from_lagna in (1, 10)):
            wife_role_title = "कामकाजी एवं संयुक्त आर्थिक संबल (Professional Partner)"
            wife_role_desc = (
                "कन्या में स्वतंत्र आजीविका, मेधा एवं व्यावसायिक कार्यकुशलता के गुण हैं। "
                "वह नौकरी या व्यवसाय द्वारा परिवार की आय में सक्रिय योगदान दे सकती है।"
            )
        else:
            wife_role_title = "कुशल गृहलक्ष्मी एवं पारिवारिक सूत्रधार (Home Administrator)"
            wife_role_desc = (
                "कन्या कुशल गृहलक्ष्मी बनकर घर के वित्तीय प्रबंधन, बजट, बचत एवं परिवार की सामाजिक प्रतिष्ठा "
                "को नई ऊंचाइयों पर ले जाएगी। उसकी उपस्थिति से घर में शांति व बरकत रहेगी।"
            )

        # 6. Vedic Remedies
        remedies = [
            "विवाह के उपरांत वर-वधू को संयुक्त रूप से 'गौरी-शंकर रुद्राक्ष' सिद्ध करवाकर पूजा कक्ष में रखना चाहिए।",
            "प्रत्येक शुक्रवार अथवा पूर्णिमा को खीर का भोग लगाकर 'श्री सूक्त' एवं 'विष्णु सहस्रनाम' का संयुक्त पाठ करें।",
            "संतान सुख एवं वंश वृद्धि में पूर्ण अनुकूलता हेतु दंपत्ति 'संतान गोपाल मंत्र' का नित्य ११ बार जप करें।",
            "कन्या द्वारा करवाचौथ, तीज या नवरात्रि में वृद्ध सुहागिन महिलाओं को सुहाग सामग्री व मीठा फल भेंट करना अत्यंत शुभ रहेगा।"
        ]

        overall_rating = round((vyavahar_score + rel_score + santana_avg + sasural_score + prosperity_score) / 5)

        return {
            "vyavahar": {
                "title": vyavahar_title,
                "score": vyavahar_score,
                "desc": vyavahar_desc,
                "g_lagna_lord": g_lagna_lord,
                "b_lagna_lord": b_lagna_lord,
                "g_elem": g_elem,
                "b_elem": b_elem,
                "element_desc": element_desc
            },
            "reliability": {
                "title": rel_title,
                "score": rel_score,
                "desc": rel_desc,
                "g_ul": g_ul_name,
                "b_ul": b_ul_name
            },
            "santana": {
                "score": santana_avg,
                "children_count": children_count,
                "lineage_text": lineage_text,
                "first_child_desc": first_child_desc,
                "beeja": {
                    "status": bs_status,
                    "desc": bs_desc,
                    "score": bs_score,
                    "sign": bs_sign_name,
                    "navamsha": bs_nav_name
                },
                "kshetra": {
                    "status": ks_status,
                    "desc": ks_desc,
                    "score": ks_score,
                    "sign": ks_sign_name,
                    "navamsha": ks_nav_name
                }
            },
            "sasural": {
                "score": sasural_score,
                "groom_inlaws": groom_sasural_desc,
                "bride_inlaws": bride_sasural_desc
            },
            "prosperity": {
                "score": prosperity_score,
                "bhagyodaya_title": bhagyodaya_title,
                "bhagyodaya_desc": bhagyodaya_desc,
                "wife_role_title": wife_role_title,
                "wife_role_desc": wife_role_desc
            },
            "remedies": remedies,
            "overall_rating": overall_rating
        }


# Singleton Milan service
default_milan_service = MilanService()
