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

        # Determine strict, honest Shastriya Verdict based on Gunas AND Doshas
        has_uncancelled_nadi = (nadi_dosha and not nadi_canc)
        has_uncancelled_bhakoot = (bhakoot_dosha and not bhakoot_canc)
        has_manglik_conflict = (not manglik_match)

        if has_uncancelled_nadi:
            verdict = "नाड़ी महादोष (विवाह वर्जित / High Risk)"
            rec_hi = (
                f"कुल 36 में से {total} गुण मिलने के उपरांत भी 'नाड़ी महादोष' (बिना परिहार) उपस्थित है। "
                "मुहूर्त चिंतामणि व बृहत्पाराशर अनुसार नाड़ी दोष संतान कष्ट, स्वास्थ्य हानि व वियोग का प्रबल कारक माना गया है। "
                "शास्त्रानुसार यह विवाह उचित नहीं है। यदि विवाह करना ही हो तो महामृत्युंजय अनुष्ठान व सुवर्ण/गौ दान अनिवार्य है।"
            )
            rec_en = f"Critical Nadi Dosha without cancellation ({total}/36 gunas). Marriage not recommended as per classical texts."
        elif has_uncancelled_bhakoot:
            verdict = "भकूट दोष (गंभीर कलह व आर्थिक संकट)"
            rec_hi = (
                f"कुल 36 में से {total} गुण हैं, किंतु 'भकूट दोष' (बिना परिहार) विद्यमान है। "
                "षडाष्टक/द्विर्द्वादश राशि संबंध के कारण दांपत्य में आर्थिक तंगी, भारी वैचारिक कलह अथवा वियोग की आशंका रहती है। "
                "विशेष सावधानी, गुरु-शुक्र बल का विचार व शांति पूजा आवश्यक है।"
            )
            rec_en = f"Bhakoot Dosha present without cancellation ({total}/36 gunas). Caution advised for harmony and finances."
        elif has_manglik_conflict:
            verdict = "असंतुलित मांगलिक दोष (विवाह पूर्व शांति अनिवार्य)"
            rec_hi = (
                f"कुल 36 में से {total} गुण मिलते हैं, परंतु {manglik_canc_reason} "
                "भौम (मंगल) के असंतुलन से दांपत्य में क्रोध, दुर्घटना, स्वास्थ्य संकट या कलह का योग बनता है। "
                "विवाह पूर्व कुंभ विवाह अथवा मंगल शांति आवश्यक है।"
            )
            rec_en = f"Manglik imbalance detected ({total}/36 gunas). Pre-marital remedies required."
        elif total < 18:
            verdict = "अधम / विवाह अनुचित (Strictly Incompatible)"
            rec_hi = (
                f"कुल 36 में से केवल {total} गुण मिलते हैं (न्यूनतम १८ गुणों से कम)। "
                "शास्त्रों के अनुसार १८ से कम गुण होने पर मानसिक तालमेल, स्वास्थ्य व दांपत्य सुख में घोर कमी रहती है। "
                "यह मिलान विवाह हेतु शास्त्रसम्मत नहीं है।"
            )
            rec_en = f"Strictly incompatible ({total}/36 gunas). Below minimum 18 points threshold."
        elif total >= 28:
            verdict = "उत्कृष्ट (Excellent)"
            rec_hi = f"कुल 36 में से {total} गुण मिलते हैं। नाड़ी व भकूट दोष से मुक्त अत्यंत शुभ, दीर्घायु एवं सुखद दांपत्य योग है।"
            rec_en = f"Outstanding compatibility with {total}/36 gunas without dosha. Highly recommended."
        else:
            verdict = "मध्यम एवं अनुकूल (Favorable)"
            rec_hi = f"कुल 36 में से {total} गुण मिलते हैं और प्रमुख दोषों का परिहार है। सामान्य समझदारी से दांपत्य उत्तम रहेगा।"
            rec_en = f"Favorable match with {total}/36 gunas. Suitable for marriage."

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

        # Same Nadi -> Check authentic classical cancellations (मुहूर्त चिंतामणि व बृहत्पाराशर)
        # Cancellation 1: एक राशि भिन्न नक्षत्र (Same rashi, different nakshatras)
        if g_sign == b_sign and g_nak != b_nak:
            return 8.0, True, True, "नाड़ी दोष परिहार: एक ही राशि में भिन्न नक्षत्र होने से नाड़ी दोष का शास्त्रीय परिहार हो जाता है।"

        # Cancellation 2: एक नक्षत्र भिन्न राशि (Same nakshatra divided across two different rashis)
        if g_nak == b_nak and g_sign != b_sign:
            return 8.0, True, True, "नाड़ी दोष परिहार: एक ही नक्षत्र दो भिन्न राशियों में विभाजित होने से नाड़ी दोष निष्प्रभावी हो जाता है।"

        # Cancellation 3: एक नक्षत्र भिन्न चरण (Same nakshatra different padas, excluding critical nakshatras)
        # In Shastras, Ashwini(0), Bharani(1), Ardra(5), Ashlesha(8), Magha(9), Jyeshtha(17), Mula(18) have no pada cancellation
        critical_naks = [0, 1, 5, 8, 9, 17, 18]
        if g_nak == b_nak and g_pada != b_pada and g_nak not in critical_naks:
            return 8.0, True, True, "नाड़ी दोष परिहार: एक ही नक्षत्र में भिन्न चरण होने से शास्त्रीय परिहार मान्य है।"

        # Cancellation 4: शास्त्रीय नाड़ी दोष मुक्त नक्षत्र युग्म (विशेष मान्यता)
        exempt_naks = [2, 6, 7, 15, 16, 21]  # Krittika(2), Punarvasu(6), Pushya(7), Vishakha(15), Anuradha(16), Shravana(21)
        if (g_nak in exempt_naks and b_nak in exempt_naks) and g_nak != b_nak:
            return 8.0, True, True, "नाड़ी दोष परिहार: दोनों नक्षत्र विशिष्ट नाड़ी दोष मुक्त वर्ग में आते हैं।"

        return 0.0, True, False, "गंभीर नाड़ी महादोष सक्रिय है (बिना परिहार)। स्वास्थ्य, जीवनशक्ति एवं संतान सुख में बाधा का प्रबल योग है।"

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
        # 1. Pati-Patni Vyavahar & Svabhav (बृहत्पाराशर होराशास्त्र अनुसार लग्नेश व तत्त्व साम्य)
        g_lagna_lord = SIGN_LORDS.get(g_chart.lagna_sign_name, "Mars")
        b_lagna_lord = SIGN_LORDS.get(b_chart.lagna_sign_name, "Venus")
        lagna_dist = ((b_chart.lagna_sign_id - g_chart.lagna_sign_id) % 12) + 1

        is_enemy_lords = (b_lagna_lord in NATURAL_ENEMIES.get(g_lagna_lord, []) or g_lagna_lord in NATURAL_ENEMIES.get(b_lagna_lord, []))
        is_friend_lords = (b_lagna_lord in NATURAL_FRIENDS.get(g_lagna_lord, []) and g_lagna_lord in NATURAL_FRIENDS.get(b_lagna_lord, []))

        if lagna_dist in (6, 8) and is_enemy_lords:
            vyavahar_title = "लग्न षडाष्टक महादोष (तीव्र कलह, अहंकार का टकराव व अशांति)"
            vyavahar_score = 36
            vyavahar_desc = (
                f"वर का लग्न ({g_chart.lagna_sign_name}) एवं कन्या का लग्न ({b_chart.lagna_sign_name}) परस्पर षडाष्टक (६/८) संबंध में हैं, "
                f"तथा लग्नेश ({g_lagna_lord} व {b_lagna_lord}) में नैसर्गिक शत्रुता है। "
                "बृहत्पाराशर अनुसार यह योग विचारों में कभी सहमति न बनने, बार-बार क्रोध व कटु विवाद, वर्चस्व की होड़ तथा "
                "वैवाहिक जीवन में भारी मानसिक अशांति का संकेत देता है। दोनों में अहंकार का त्याग व धैर्य अत्यंत आवश्यक होगा।"
            )
        elif is_enemy_lords:
            vyavahar_title = "लग्नेश शत्रुता (वैचारिक द्वंद्व, हठ व मतभेद)"
            vyavahar_score = 48
            vyavahar_desc = (
                f"वर के लग्नेश ({g_lagna_lord}) और कन्या के लग्नेश ({b_lagna_lord}) में नैसर्गिक शत्रुता है। "
                "दोनों की कार्यशैली, प्राथमिकताओं और सोचने के तरीके में बड़ा अंतर रहेगा। "
                "एक-दूसरे पर अपनी राय थोपने से दैनिक जीवन में बार-बार तनाव व मनमुटाव की स्थिति बनेगी।"
            )
        elif lagna_dist in (2, 12):
            vyavahar_title = "लग्न द्विर्द्वादश स्थिति (प्राथमिकताओं व सोच में अंतर)"
            vyavahar_score = 56
            vyavahar_desc = (
                f"वर व कन्या के लग्न परस्पर २/१२ संबंध में हैं। जीवन मूल्यों, खर्च करने की आदत तथा प्राथमिकताओं में भिन्नता रहेगी। "
                "धीरज व एक-दूसरे की व्यक्तिगत स्वतंत्रता का आदर करने पर ही दांपत्य संतुलित रहेगा।"
            )
        elif g_lagna_lord == b_lagna_lord:
            vyavahar_title = "समान लग्नेश (अत्युत्तम वैचारिक सामंजस्य)"
            vyavahar_score = 95
            vyavahar_desc = (
                f"वर और कन्या दोनों के लग्नेश एक ही ग्रह ({g_lagna_lord}) हैं। "
                "दोनों के जीवन मूल्य, रुचियां एवं सोचने का दृष्टिकोण एक जैसा रहेगा। "
                "पारस्परिक समझदारी, आदर एवं भावनात्मक निकटता उच्च कोटि की रहेगी।"
            )
        elif is_friend_lords:
            vyavahar_title = "परस्पर स्वाभाविक मित्र लग्नेश (सद्भाव एवं सहयोग)"
            vyavahar_score = 88
            vyavahar_desc = (
                f"वर के लग्नेश ({g_lagna_lord}) एवं कन्या के लग्नेश ({b_lagna_lord}) आपस में स्वाभाविक मित्र हैं। "
                "विपरीत परिस्थितियों में भी दोनों एक-दूसरे का संबल बनेंगे। आपसी संवाद मधुर एवं उत्साहवर्धक रहेगा।"
            )
        else:
            vyavahar_title = "तटस्थ/सम भाव लग्नेश (व्यावहारिक संतुलन)"
            vyavahar_score = 75
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

        # 2. Relationship Reliability & Marital Longevity (महर्षि जैमिनी उपपद लग्न UL सूत्र)
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
        if ul_dist in (6, 8):
            rel_title = "उपपद षडाष्टक दोष (अविश्वास, दरार व विच्छेद का जोखिम)"
            rel_score = 38
            rel_desc = (
                f"महर्षि जैमिनी उपपद सूत्र अनुसार वर का उपपद ({g_ul_name}) व कन्या का उपपद ({b_ul_name}) "
                "परस्पर ६/८ (षडाष्टक) स्थिति में हैं। यह योग दांपत्य में अविश्वास, भावनात्मक अलगाव, बाहरी हस्तक्षेप "
                "अथवा विधिक विवाद/दांपत्य विच्छेद (Separation/Divorce) का प्रबल जोखिम दर्शाता है। अत्यंत धैर्य व सतर्कता आवश्यक है।"
            )
        elif ul_dist in (2, 12):
            rel_title = "उपपद द्विर्द्वादश स्थिति (पारिवारिक दूरी व व्यय)"
            rel_score = 52
            rel_desc = (
                f"उपपद लग्न परस्पर २/१२ स्थिति में हैं। दोनों के मध्य भावनात्मक दूरी, किसी एक का बाहर रहना "
                "अथवा ससुराल पक्ष से तनाव की आशंका रहती है। खुलापन व पारदर्शिता जरूरी है।"
            )
        elif ul_dist in (1, 5, 9, 7):
            rel_title = "अटूट दांपत्य निष्ठा एवं दीर्घायु संबंध"
            rel_score = 92
            rel_desc = (
                f"महर्षि जैमिनी के उपपद लग्न (UL) सूत्र अनुसार वर का उपपद ({g_ul_name}) व कन्या का उपपद ({b_ul_name}) "
                "परस्पर त्रिकोण अथवा समसप्तक में हैं। यह जीवनभर एक-दूसरे के प्रति समर्पण, विश्वास, सामाजिक मर्यादा "
                "तथा संकटों में भी कभी साथ न छोड़ने का पक्का योग बनाता है।"
            )
        else:
            rel_title = "स्थिर एवं सामान्य दांपत्य निष्ठा"
            rel_score = 76
            rel_desc = (
                f"दोनों के उपपद लग्न ({g_ul_name} व {b_ul_name}) केंद्र व उपचय संबंध में हैं। "
                "विवाह के उपरांत दोनों में आपसी भरोसा सामान्य रूप से बना रहेगा।"
            )

        # 3. Progeny / Children Analysis & Beeja/Kshetra Sphuta (फलदीपिका व जातक पारिजात)
        bs_long = (g_chart.planets["Sun"].longitude + g_chart.planets["Venus"].longitude + g_chart.planets["Jupiter"].longitude) % 360.0
        bs_sign_id, bs_sign_name, bs_nav_id, bs_nav_name, bs_s_odd, bs_n_odd = self._get_sphuta_details(bs_long)

        if bs_s_odd and bs_n_odd:
            bs_status = "उत्कृष्ट एवं परम ओजस्वी बीज बल"
            bs_desc = f"बीज स्फुट ({bs_sign_name} राशि, {bs_nav_name} नवांश) दोनों विषम राशियों में हैं। वर का बीज बल शास्त्रानुसार परम पुष्ट व ओजस्वी है।"
            bs_score = 95
        elif bs_s_odd or bs_n_odd:
            bs_status = "मध्यम बीज बल"
            bs_desc = f"बीज स्फुट ({bs_sign_name} राशि, {bs_nav_name} नवांश) में एक विषम व एक सम है। वर का बीज बल संतुलित है, समय पर संतान प्राप्ति होगी।"
            bs_score = 72
        else:
            bs_status = "अल्प/कमजोर बीज बल (दोष युक्त)"
            bs_desc = f"बीज स्फुट ({bs_sign_name} राशि, {bs_nav_name} नवांश) दोनों सम राशियों में हैं। शास्त्रानुसार यह शुक्र/वीर्य दुर्बलता व संतान प्राप्ति में बाधा दर्शाता है।"
            bs_score = 42

        ks_long = (b_chart.planets["Moon"].longitude + b_chart.planets["Mars"].longitude + b_chart.planets["Jupiter"].longitude) % 360.0
        ks_sign_id, ks_sign_name, ks_nav_id, ks_nav_name, ks_s_odd, ks_n_odd = self._get_sphuta_details(ks_long)

        if (not ks_s_odd) and (not ks_n_odd):
            ks_status = "उत्कृष्ट एवं परम फलदायी क्षेत्र बल"
            ks_desc = f"क्षेत्र स्फुट ({ks_sign_name} राशि, {ks_nav_name} नवांश) दोनों सम राशियों में हैं। कन्या का क्षेत्र बल परम उर्वर व पुष्ट है। मातृत्व क्षमता उत्तम है।"
            ks_score = 95
        elif (not ks_s_odd) or (not ks_n_odd):
            ks_status = "मध्यम क्षेत्र बल"
            ks_desc = f"क्षेत्र स्फुट ({ks_sign_name} राशि, {ks_nav_name} नवांश) में एक सम व एक विषम है। मातृत्व क्षमता सामान्य व संतुलित है।"
            ks_score = 72
        else:
            ks_status = "अल्प/कमजोर क्षेत्र बल (दोष युक्त)"
            ks_desc = f"क्षेत्र स्फुट ({ks_sign_name} राशि, {ks_nav_name} नवांश) दोनों विषम राशियों में हैं। शास्त्रानुसार यह गर्भाधान में संवेदनशीलता व बाधा का संकेत है।"
            ks_score = 42

        santana_avg = round((bs_score + ks_score) / 2)
        if (bs_score <= 45) and (ks_score <= 45):
            children_count = "संतान हीनता / घोर विलंब व बाधा (Severe Progeny Affliction)"
            santana_avg = 35
            lineage_text = (
                "फलदीपिका व जातक पारिजात अनुसार वर का बीज स्फुट और कन्या का क्षेत्र स्फुट दोनों ही पूर्णतः कमजोर व प्रतिकूल स्थिति में हैं। "
                "यह योग प्राकृतिक गर्भाधान में भारी अवरोध, शुक्राणु/अंडाणु दुर्बलता, गर्भस्राव अथवा संतानहीनता का संकेत देता है। "
                "बिना गहन चिकित्सकीय उपचार एवं संतान गोपाल/हरिवंश पुराण अनुष्ठान के संतान सुख में घोर संशय रहेगा।"
            )
            first_child_desc = "प्राकृतिक रूप से प्रथम संतान में अत्यधिक विलंब अथवा गहन चिकित्सकीय प्रक्रिया का संकेत।"
        elif (bs_score <= 45) or (ks_score <= 45):
            children_count = "संतान में विलंब व संवेदनशीलता (Medical & Astrological Care Needed)"
            santana_avg = 52
            lineage_text = (
                "एक पक्ष का स्फुट पूर्णतः कमजोर है, जिससे प्राकृतिक गर्भधारण में संवेदनशीलता व २ से ४ वर्ष का विलंब संभव है। "
                "चिकित्सकीय परामर्श तथा धार्मिक अनुष्ठान के उपरांत ही संतान सुख की प्राप्ति होगी।"
            )
            first_child_desc = "प्रथम संतान प्राप्ति में समय लग सकता है; धैर्य व चिकित्सकीय देखरेख आवश्यक है।"
        elif santana_avg >= 85:
            children_count = "२ से ३ संतान का प्रबल एवं उत्तम योग"
            lineage_text = (
                "बीज व क्षेत्र स्फुट के अत्यंत अनुकूल होने से वंश वृद्धि निर्बाध रूप से होगी। "
                "संतान सद्गुणी, आज्ञाकारी, कुलदीपक एवं परिवार का यश बढ़ाने वाली होगी।"
            )
            first_child_desc = "प्रथम संतान ओजस्वी, नेतृत्व क्षमता से युक्त एवं परिवार के लिए भाग्यशाली सिद्ध होगी।"
        else:
            children_count = "१ से २ संतान का सुखद योग"
            lineage_text = (
                "संतान सुख सामान्य समय पर प्राप्त होगा। परिवार में खुशहाली रहेगी तथा संतान विद्या व संस्कार में आगे रहेगी।"
            )
            first_child_desc = "प्रथम संतान बुद्धिमान, शांत स्वभाव एवं माता-पिता के प्रति समर्पित रहेगी।"

        # 4. Sasural Paksha se Sahayog & Relatives (ससुराल पक्ष, सास, ससुर, देवर, ननद आदि - भावत् भावम् व BPHS)
        # 4.1 Groom's Sasural (वर का ससुराल पक्ष - अष्टम भाव):
        g_h8_planets = [p for p, obj in g_chart.planets.items() if obj.house_from_lagna == 8]
        has_g_8th_malefic = any(p in ["Mars", "Saturn", "Rahu", "Ketu"] for p in g_h8_planets)
        if has_g_8th_malefic:
            groom_sasural_desc = "वर के ८वें भाव में क्रूर/पाप ग्रह होने से ससुराल पक्ष से अनावश्यक दखलंदाजी, आर्थिक विवाद, अपमान अथवा धोखे का योग है। वर को ससुराल से आर्थिक लेन-देन या साझेदारी पूर्णतः टालनी चाहिए।"
            groom_sasural_score = 42
        elif not g_h8_planets:
            groom_sasural_desc = "वर को ससुराल पक्ष से भरपूर मान-सम्मान, आतिथ्य एवं स्नेह मिलेगा। ससुराल वाले वर की प्रतिष्ठा व निर्णयों का पूर्ण आदर करेंगे।"
            groom_sasural_score = 88
        else:
            groom_sasural_desc = "वर को ससुराल पक्ष से औपचारिक व आदरयुक्त संबंध बनाए रखना चाहिए। आर्थिक लेन-देन में पूर्ण पारदर्शिता रखें।"
            groom_sasural_score = 74

        # 4.2 Bride's general Sasural (कन्या का ससुराल में स्थान - अष्टम भाव):
        b_h8_planets = [p for p, obj in b_chart.planets.items() if obj.house_from_lagna == 8]
        has_b_8th_malefic = any(p in ["Mars", "Saturn", "Rahu", "Ketu"] for p in b_h8_planets)
        if has_b_8th_malefic:
            bride_sasural_desc = "कन्या के ८वें (मांगल्य व ससुराल सुख) भाव में पाप प्रभाव होने से ससुराल में उपेक्षा, कठोर नियम, मानसिक तनाव अथवा प्रताड़ना की आशंका का योग है। कन्या को ससुराल में बहुत सतर्क, धैर्यवान व आत्मविश्वासी रहना होगा।"
            bride_sasural_score = 40
        else:
            bride_sasural_desc = "कन्या को ससुराल में कुलवधू के रूप में उचित सम्मान व बेटी जैसा स्नेह मिलने का सुंदर योग है। कन्या अपनी समझदारी से ससुराल के सभी सदस्यों का दिल जीत लेगी।"
            bride_sasural_score = 88

        # 4.3 ससुर (Father-in-law / श्वसुर संबंध):
        # Shastriya rule: 9th from 7th = 3rd house of Bride
        b_3rd_planets = [p for p, obj in b_chart.planets.items() if obj.house_from_lagna == 3]
        b_3rd_sign_id = ((b_chart.lagna_sign_id - 1 + 2) % 12) + 1
        b_3rd_lord = SIGN_LORDS.get(SIGN_NAMES[b_3rd_sign_id - 1], "Mars")
        b_3rd_lord_obj = b_chart.planets.get(b_3rd_lord)
        b_3rd_lord_h = b_3rd_lord_obj.house_from_lagna if b_3rd_lord_obj else 3

        has_benefic_3rd = any(p in ["Jupiter", "Venus", "Mercury", "Moon"] for p in b_3rd_planets)
        has_malefic_3rd = any(p in ["Saturn", "Rahu", "Ketu", "Mars"] for p in b_3rd_planets)
        is_3rd_lord_trika = (b_3rd_lord_h in (6, 8, 12))

        if has_malefic_3rd or is_3rd_lord_trika:
            sasur_title = "ससुर से वैचारिक दूरी, कठोरता व आलोचना योग (Critical & Strained)"
            sasur_status = "कटु / तनावपूर्ण संबंध (High Tension)"
            sasur_score = 38
            sasur_desc = (
                "कन्या के ३रे भाव (सप्तम से नवम - ससुर स्थान) पर क्रूर/पाप प्रभाव है। "
                "ससुर का दृष्टिकोण कन्या के प्रति अत्यधिक आलोचनात्मक, शंकालु, कठोर या उपेक्षापूर्ण हो सकता है। "
                "छोटी बातों पर असंतोष प्रकट हो सकता है। कन्या को ससुर के समक्ष अत्यधिक मौन, संयम व विनम्रता बरतनी होगी।"
            )
        elif has_benefic_3rd or b_3rd_lord_h in (1, 3, 5, 9, 10, 11):
            sasur_title = "पुत्रीवत वात्सल्य एवं संरक्षक ससुर योग (Paternal Guidance & Blessings)"
            sasur_status = "अत्यंत अनुकूल एवं स्नेहमयी"
            sasur_score = 92
            sasur_desc = (
                "ससुर का दृष्टिकोण अत्यंत उदार, संरक्षक एवं मार्गदर्शक रहेगा। कन्या को ससुर से पिता तुल्य मान-सम्मान व आशीर्वाद प्राप्त होगा। "
                "परिवार के महत्वपूर्ण निर्णयों में कन्या के विचारों को सम्मान दिया जाएगा तथा वर के पिता हर परिस्थिति में उसके संबल बनेंगे।"
            )
        else:
            sasur_title = "संतुलित सौहार्द एवं पारस्परिक आदर (Balanced & Formal)"
            sasur_status = "संतुलित एवं शिष्टाचारपूर्ण"
            sasur_score = 75
            sasur_desc = (
                "ससुर के साथ व्यावहारिक, शांत व सौहार्दपूर्ण संबंध रहेंगे। दैनिक पारिवारिक कार्यों में कोई अनावश्यक हस्तक्षेप नहीं होगा "
                "और परस्पर मान-सम्मान सदैव बना रहेगा।"
            )

        # 4.4 सासू माँ (Mother-in-law / सासू माँ संबंध):
        # Shastriya rule: 4th from 7th = 10th house of Bride
        b_10th_planets = [p for p, obj in b_chart.planets.items() if obj.house_from_lagna == 10]
        b_10th_sign_id = ((b_chart.lagna_sign_id - 1 + 9) % 12) + 1
        b_10th_lord = SIGN_LORDS.get(SIGN_NAMES[b_10th_sign_id - 1], "Saturn")
        b_10th_lord_obj = b_chart.planets.get(b_10th_lord)
        b_10th_lord_h = b_10th_lord_obj.house_from_lagna if b_10th_lord_obj else 10

        has_benefic_10th = any(p in ["Jupiter", "Venus", "Mercury", "Moon"] for p in b_10th_planets)
        has_malefic_10th = any(p in ["Mars", "Saturn", "Rahu", "Ketu", "Sun"] for p in b_10th_planets)
        is_10th_lord_trika = (b_10th_lord_h in (6, 8, 12))

        if has_malefic_10th or is_10th_lord_trika:
            saas_title = "सास-बहू अधिकार संघर्ष एवं शीतयुद्ध योग (High Friction & Dominance)"
            saas_status = "गंभीर कलह व प्रभुत्व संघर्ष (Severe Friction)"
            saas_score = 35
            saas_desc = (
                "कन्या के १०वें भाव (सप्तम से चतुर्थ - सासू माँ स्थान) पर क्रूर ग्रहों का प्रभाव है। "
                "सासू माँ का स्वभाव अत्यधिक अधिकारवादी, टोका-टोकी करने वाला अथवा असंतुष्ट रहने वाला हो सकता है। "
                "गृह-प्रबंधन, रीति-रिवाजों और रसोई पर नियंत्रण को लेकर सास-बहू में लगातार तनातनी, शीतयुद्ध या तीखी बहस की प्रबल आशंका है। "
                "परिवार में शांति हेतु अलग आवास (nuclear setup) या असीम धैर्य की आवश्यकता पड़ेगी।"
            )
        elif has_benefic_10th or (b_10th_lord_h in (1, 2, 4, 5, 7, 9, 10, 11) and not has_malefic_10th):
            saas_title = "मातृवत वात्सल्य एवं उत्तम गृह-प्रबंधन योग (Motherly Affection & Household Synergy)"
            saas_status = "मातृवत स्नेह एवं कुशल तालमेल"
            saas_score = 91
            saas_desc = (
                "सासू माँ ममतामयी, कुशल गृहस्वामिनी एवं कन्या को सगी पुत्री जैसा स्नेह देने वाली होंगी। "
                "रसोई, रीति-रिवाजों व गृहस्थी के संचालन में दोनों के बीच सुंदर तालमेल रहेगा। "
                "सासू माँ कन्या को घर की बागडोर सौंपकर प्रसन्न रहेंगी तथा सास-बहू में मां-बेटी जैसा प्यार रहेगा।"
            )
        else:
            saas_title = "सहज तालमेल एवं परस्पर सम्मान (Cooperative & Respectful)"
            saas_status = "सहयोगात्मक एवं शांत"
            saas_score = 75
            saas_desc = (
                "सासू माँ और बहू के मध्य व्यावहारिक, सहयोगात्मक और सम्मानजनक संबंध रहेंगे। "
                "दोनों एक-दूसरे के कार्यक्षेत्र व स्वतंत्रता का आदर करेंगे और घर का वातावरण शांत रहेगा।"
            )

        # 4.5 देवर / जेठ (Husband's Brothers):
        # Shastriya rule: 3rd from 7th = 9th house (Younger / Devar), 11th from 7th = 5th house (Elder / Jeth)
        b_9th_planets = [p for p, obj in b_chart.planets.items() if obj.house_from_lagna == 9]
        b_5th_planets = [p for p, obj in b_chart.planets.items() if obj.house_from_lagna == 5]
        has_affliction_brothers = any(p in ["Saturn", "Rahu", "Mars", "Ketu"] for p in b_9th_planets + b_5th_planets)

        if has_affliction_brothers:
            devar_title = "देवर/जेठ से तनातनी व संपत्ति/अहंकार विवाद योग (Conflict & Distance)"
            devar_status = "तनाव व विवाद की आशंका (High Risk)"
            devar_score = 40
            devar_desc = (
                "देवर या जेठ के साथ वैचारिक मतभेद, पारिवारिक राजनीति, संपत्ति या व्यवहार को लेकर कड़वाहट पैदा हो सकती है। "
                "आदर में कमी या घरेलू मामलों में अवांछित हस्तक्षेप का जोखिम है। पारिवारिक मामलों में स्पष्ट दूरी व सतर्कता जरूरी है।"
            )
        else:
            devar_title = "स्नेहपूर्ण देवर-भाभी व जेठ आदर योग (Harmonious Brother-in-Law Bond)"
            devar_status = "मित्रवत, आदरयुक्त एवं सहयोगात्मक"
            devar_score = 90
            devar_desc = (
                "देवर भाभी को बड़ी बहन अथवा माँ तुल्य आदर देगा और हर घरेलू व सामाजिक कार्य में बढ़-चढ़कर साथ देगा। "
                "जेठ के साथ अत्यंत मर्यादित, सौम्य व सम्माननीय संबंध रहेंगे। परिवार में भ्रातृ-सौहार्द बना रहेगा।"
            )

        # 4.6 ननद (Husband's Sister) एवं साला/साली (Wife's Siblings):
        # Mercury & Venus karakas, plus 3rd from lagna / 9th from lagna
        merc_obj = b_chart.planets.get("Mercury")
        merc_h = merc_obj.house_from_lagna if merc_obj else 1
        if merc_h in (6, 8, 12):
            nanad_title = "ननद से वैमनस्य एवं साले-साली से कलह योग (Gossip & Jealousy Risk)"
            nanad_status = "ईर्ष्या व व्यंग्य का जोखिम (Tension Prone)"
            nanad_score = 42
            nanad_desc = (
                "ननद के साथ ईर्ष्या, व्यंग्यात्मक बातें, चुगली या मायके-ससुराल की तुलना के कारण दांपत्य में दरार पड़ने का जोखिम है। "
                "वर को भी साले-साली से कटाक्ष या असहयोग मिल सकता है। आंतरिक बातों को इनके सामने साझा करने से पूर्ण परहेज करें।"
            )
        else:
            nanad_title = "सखीवत ननद-भाभी एवं मधुर साला-साली संबंध (Sisterly Warmth & Joyful Bond)"
            nanad_status = "सहेलीवत स्नेह एवं सखी भाव"
            nanad_score = 90
            nanad_desc = (
                "कन्या और ननद के बीच सहेलियों (बहनों) जैसा सहज, खुला व आत्मीय संबंध रहेगा। दोनों सुख-दुख साझा करेंगी। "
                "वहीं वर को भी अपने साले व सालियों से भरपूर आदर, अपनत्व एवं हास्य-विनोद पूर्ण वातावरण प्राप्त होगा।"
            )

        sasural_score = round((sasur_score * 0.25) + (saas_score * 0.30) + (devar_score * 0.25) + (nanad_score * 0.20))

        # 5. Patni ka Sahayog & Bhagyodaya (सप्तमेश भाव स्थिति - BPHS)
        g_7th_sign_id = ((g_chart.lagna_sign_id - 1 + 6) % 12) + 1
        g_7th_lord = SIGN_LORDS.get(SIGN_NAMES[g_7th_sign_id - 1], "Venus")
        g_7th_lord_h = g_chart.planets.get(g_7th_lord).house_from_lagna if g_chart.planets.get(g_7th_lord) else 7

        if g_7th_lord_h in (6, 8, 12):
            bhagyodaya_title = "विवाह उपरांत वित्तीय बाधाएं व व्यय योग (Post-Marital Financial Hurdles)"
            prosperity_score = 42
            bhagyodaya_desc = (
                f"वर की कुण्डली में सप्तमेश ({g_7th_lord}) {g_7th_lord_h}वें (त्रिक/हानि) भाव में स्थित हैं। "
                "बृहत्पाराशर होराशास्त्र अनुसार विवाह के पश्चात अचानक अनपेक्षित खर्च, कर्ज, व्यापार/नौकरी में उतार-चढ़ाव या "
                "स्वास्थ्य पर व्यय का योग बनता है। किसी भी बड़े वित्तीय निर्णय में जल्दबाजी न करें तथा बचत पर विशेष ध्यान दें।"
            )
        elif g_7th_lord_h in (1, 2, 4, 7, 9, 10, 11):
            bhagyodaya_title = "विवाह उपरांत तीव्र भाग्योदय योग (Post-Marital Prosperity)"
            prosperity_score = 92
            bhagyodaya_desc = (
                f"वर की कुण्डली में सप्तमेश ({g_7th_lord}) केंद्र/त्रिकोण अथवा धन भाव ({g_7th_lord_h}वें भाव) में स्थित हैं। "
                "बृहत्पाराशर होराशास्त्र अनुसार विवाह के पश्चात जातक का वास्तविक भाग्योदय होगा। "
                "करियर में पदोन्नति, व्यापार में विस्तार, नया गृह/वाहन तथा आर्थिक समृद्धि में तेजी से वृद्धि होगी।"
            )
        else:
            bhagyodaya_title = "स्थिर एवं संतुलित भाग्योदय"
            prosperity_score = 74
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

        # 6. Vedic Remedies (दोषों के आधार पर वास्तविक विशिष्ट शास्त्रीय उपाय)
        remedies = []
        if vyavahar_score < 50:
            remedies.append("लग्न षडाष्टक / शत्रुता निवारण हेतु वर-वधू को भगवान शिव व माता पार्वती का संयुक्त रुद्राभिषेक कराना चाहिए।")
        if rel_score < 50:
            remedies.append("उपपद दोष व दांपत्य स्थायित्व हेतु दोनों को संयुक्त रूप से 'गौरी-शंकर रुद्राक्ष' सिद्ध करवाकर पूजा कक्ष में स्थापित करना चाहिए।")
        if santana_avg < 60:
            remedies.append("संतान बाधा निवारण एवं वंश वृद्धि हेतु दंपत्ति को नित्य 'संतान गोपाल मंत्र' (ॐ देवकीसुत गोविंद...) का १०८ बार जप करना चाहिए।")
        if saas_score < 50:
            remedies.append("सास-बहू कलह शांति हेतु कन्या को चांदी का चौकोर टुकड़ा अपने पास रखना चाहिए एवं पूर्णिमा को सासू माँ के चरण स्पर्श करने चाहिए।")
        if prosperity_score < 50:
            remedies.append("सप्तमेश के त्रिक भाव में होने पर ऋण व आर्थिक हानि से बचने हेतु दंपत्ति को शुक्रवार को 'श्री सूक्त' व 'कनकधारा स्तोत्र' का पाठ करना चाहिए।")

        # General standard remedies
        remedies.append("प्रत्येक शुक्रवार अथवा पूर्णिमा को खीर का भोग लगाकर 'विष्णु सहस्रनाम' का संयुक्त पाठ करें।")
        remedies.append("कन्या द्वारा करवाचौथ, तीज या नवरात्रि में वृद्ध सुहागिन महिलाओं को सुहाग सामग्री व मीठा फल भेंट करना अत्यंत शुभ रहेगा।")

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
                "bride_inlaws": bride_sasural_desc,
                "sasur": {
                    "title": sasur_title,
                    "status": sasur_status,
                    "desc": sasur_desc,
                    "score": sasur_score,
                    "bhavat_bhavam": "७वें से ९वां (तृतीय भाव) - ससुर स्थान"
                },
                "saas": {
                    "title": saas_title,
                    "status": saas_status,
                    "desc": saas_desc,
                    "score": saas_score,
                    "bhavat_bhavam": "७वें से ४था (दशम भाव) - सासू माँ स्थान"
                },
                "devar_jeth": {
                    "title": devar_title,
                    "status": devar_status,
                    "desc": devar_desc,
                    "score": devar_score,
                    "bhavat_bhavam": "७वें से ३रा (९वां - देवर) व ११वां (५वां - जेठ)"
                },
                "nanad_sala": {
                    "title": nanad_title,
                    "status": nanad_status,
                    "desc": nanad_desc,
                    "score": nanad_score,
                    "bhavat_bhavam": "बुध/शुक्र कारक एवं सहोदर भाव"
                }
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
