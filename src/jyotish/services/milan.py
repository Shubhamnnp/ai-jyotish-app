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
        nadi_score, nadi_dosha, nadi_canc = self._calc_nadi(g_nak_idx, b_nak_idx, g_moon.nakshatra_pada, b_moon.nakshatra_pada, g_sign_id, b_sign_id)

        total = round(varna_score + vashya_score + tara_score + yoni_score + maitri_score + gana_score + bhakoot_score + nadi_score, 1)

        # Manglik Analysis
        g_manglik = self._is_manglik(groom_chart)
        b_manglik = self._is_manglik(bride_chart)
        manglik_match = (g_manglik == b_manglik)

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
            bhakoot_dosha=bhakoot_dosha,
            bhakoot_dosha_cancelled=bhakoot_canc,
            groom_manglik=g_manglik,
            bride_manglik=b_manglik,
            manglik_match=manglik_match,
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
        """Tara Koota (3 pts): Navatara mutual auspiciousness."""
        diff_gb = ((g_nak - b_nak) % 9) + 1
        diff_bg = ((b_nak - g_nak) % 9) + 1
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

    def _calc_nadi(self, g_nak: int, b_nak: int, g_pada: int, b_pada: int, g_sign: int, b_sign: int) -> Tuple[float, bool, bool]:
        """Nadi (8 pts) with classical cancellation."""
        g_nadi = NAKSHATRA_NADIS[g_nak]
        b_nadi = NAKSHATRA_NADIS[b_nak]
        if g_nadi != b_nadi:
            return 8.0, False, False
        # Same Nadi -> Check cancellation: same nakshatra but different pada
        if g_nak == b_nak and g_pada != b_pada:
            return 8.0, True, True
        # Different rashi same nakshatra
        if g_sign != b_sign:
            return 8.0, True, True
        return 0.0, True, False

    def _is_manglik(self, chart: KundaliChart) -> bool:
        """Checks Manglik Dosha from Lagna and Moon (houses 1, 2, 4, 7, 8, 12)."""
        mars = chart.planets["Mars"]
        manglik_houses = [1, 2, 4, 7, 8, 12]
        return mars.house_from_lagna in manglik_houses or mars.house_from_moon in manglik_houses


# Singleton Milan service
default_milan_service = MilanService()

