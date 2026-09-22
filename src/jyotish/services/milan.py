"""
Kundali Milan (Horoscope Matching / Synastry) Engine for JyotishOS.
Implements the classical 36-Guna Ashtakoota matching system:
Varna (1), Vashya (2), Tara (3), Yoni (4), Graha Maitri (5), Gana (6), Bhakoot (7), Nadi (8),
along with classical cancellations (Nadi/Bhakoot dosha) and mutual Manglik Dosha analysis.
"""

from typing import Dict, Any, List, Tuple
from pydantic import BaseModel, Field
from ..core.constants import SIGN_LORDS, NATURAL_FRIENDS, NATURAL_ENEMIES
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


# Singleton Milan service
default_milan_service = MilanService()
