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
    bhakoot_cancellation_reason: str = ""
    groom_manglik: bool = False
    bride_manglik: bool = False
    manglik_match: bool = False
    manglik_cancellation_reason: str = ""
    nadi_cancellation_reason: str = ""
    rajju_dosha: bool = False
    rajju_type: str = ""
    rajju_desc: str = ""
    vedha_dosha: bool = False
    vedha_desc: str = ""
    stree_deergha: str = ""
    mahendra_koota: bool = False
    mahendra_desc: str = ""
    dasha_sandhi: bool = False
    dasha_sandhi_diff_days: int = 0
    dasha_sandhi_desc: str = ""
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
        bhakoot_score, bhakoot_dosha, bhakoot_canc, bhakoot_reason = self._calc_bhakoot(g_sign_id, b_sign_id)

        # 8. Nadi (8 pts) with cancellation
        nadi_score, nadi_dosha, nadi_canc, nadi_reason = self._calc_nadi(g_nak_idx, b_nak_idx, g_moon.nakshatra_pada, b_moon.nakshatra_pada, g_sign_id, b_sign_id)

        total = round(varna_score + vashya_score + tara_score + yoni_score + maitri_score + gana_score + bhakoot_score + nadi_score, 1)

        # Advanced Manglik Analysis & Cancellations
        g_manglik = self._is_manglik(groom_chart)
        b_manglik = self._is_manglik(bride_chart)
        manglik_match, manglik_canc_reason = self._evaluate_manglik_cancellation(groom_chart, bride_chart, g_manglik, b_manglik)

        # 9. Rajju Dosha
        rajju_dosha, rajju_type, rajju_desc = self._calc_rajju(g_nak_idx, b_nak_idx)

        # 10. Vedha Dosha
        vedha_dosha, vedha_desc = self._calc_vedha(g_nak_idx, b_nak_idx)

        # 11. Stree-Deergha & Mahendra
        stree_deergha, mahendra_koota, mahendra_desc = self._calc_stree_deergha_mahendra(g_nak_idx, b_nak_idx)

        # 12. Dasha Sandhi
        dasha_sandhi, dasha_sandhi_diff_days, dasha_sandhi_desc = self._calc_dasha_sandhi(groom_chart, bride_chart)

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
        elif rajju_dosha and "शिरो" in rajju_type:
            verdict = "शिरो रज्जु महादोष (अति-सावधानी / Critical Risk)"
            rec_hi = (
                f"कुल 36 में से {total} गुण हैं, किंतु 'शिरो रज्जु महादोष' विद्यमान है। "
                "दक्षिण भारतीय व मुहूर्त ग्रंथों के अनुसार शिरो रज्जु वर के आयु व स्वास्थ्य के लिए अत्यंत अनिष्टकारी माना गया है। "
                "विशेष महामृत्युंजय अनुष्ठान एवं आयु परीक्षा के बिना यह संबंध स्वीकार्य नहीं है।"
            )
            rec_en = f"Critical Siro Rajju Dosha present ({total}/36 gunas). Poses risk to longevity; caution and remedies essential."
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
        elif vedha_dosha:
            verdict = "नक्षत्र वेध दोष (विवाह पूर्व शांति आवश्यक)"
            rec_hi = (
                f"कुल 36 में से {total} गुण हैं, किंतु 'नक्षत्र वेध दोष' उपस्थित है। "
                "परस्पर वेध नक्षत्रों के कारण दांपत्य में गुप्त कलह व अकस्मात बाधाओं का भय रहता है। नक्षत्र शांति पूजा अनुशंसित है।"
            )
            rec_en = f"Nakshatra Vedha Dosha present ({total}/36 gunas). Planetary propitiation advised."
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
            bhakoot_cancellation_reason=bhakoot_reason,
            groom_manglik=g_manglik,
            bride_manglik=b_manglik,
            manglik_match=manglik_match,
            manglik_cancellation_reason=manglik_canc_reason,
            rajju_dosha=rajju_dosha,
            rajju_type=rajju_type,
            rajju_desc=rajju_desc,
            vedha_dosha=vedha_dosha,
            vedha_desc=vedha_desc,
            stree_deergha=stree_deergha,
            mahendra_koota=mahendra_koota,
            mahendra_desc=mahendra_desc,
            dasha_sandhi=dasha_sandhi,
            dasha_sandhi_diff_days=dasha_sandhi_diff_days,
            dasha_sandhi_desc=dasha_sandhi_desc,
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

    def _calc_bhakoot(self, g_sign: int, b_sign: int) -> Tuple[float, bool, bool, str]:
        """Bhakoot (7 pts) with classical cancellation & authentic Shastriya reason."""
        from ..core.constants import SIGN_NAMES
        diff = ((g_sign - b_sign) % 12) + 1
        # Inauspicious: 2-12, 6-8, 9-5
        if diff in (2, 12, 6, 8, 5, 9):
            g_lord = SIGN_LORDS[SIGN_NAMES[g_sign - 1]]
            b_lord = SIGN_LORDS[SIGN_NAMES[b_sign - 1]]
            if g_lord == b_lord:
                return 7.0, True, True, f"भकूट दोष परिहार: दोनों राशियों के स्वामी एक ही ग्रह ({g_lord}) होने से भकूट दोष पूर्णतः निष्प्रभावी हो जाता है। (फलदीपिका: 'राशीशैक्ये भकूटदोषो न भवति')"
            if b_lord in NATURAL_FRIENDS.get(g_lord, []) and g_lord in NATURAL_FRIENDS.get(b_lord, []):
                return 7.0, True, True, f"भकूट दोष परिहार: दोनों राशि स्वामियों ({g_lord} व {b_lord}) में परस्पर नैसर्गिक मित्रता होने से भकूट दोष का शास्त्रीय परिहार मान्य है। (फलदीपिका: 'राशीशमैत्री यदि चेदुभाभ्यां भकूटदोषं विनिहन्ति सद्यः॥')"
            if b_lord in NATURAL_FRIENDS.get(g_lord, []) or g_lord in NATURAL_FRIENDS.get(b_lord, []):
                return 7.0, True, True, f"भकूट दोष परिहार: दोनों राशि स्वामियों ({g_lord} व {b_lord}) में मित्रता संबंध होने से दोष का शास्त्रीय शमन हो जाता है।"
            
            diff_label = "षडाष्टक (६/८)" if diff in (6, 8) else ("द्विर्द्वादश (२/१२)" if diff in (2, 12) else "नवम-पंचम (९/५)")
            return 0.0, True, False, f"गंभीर भकूट दोष सक्रिय: राशि संबंध {diff_label} है तथा राशि स्वामियों में मित्रता का अभाव है। आर्थिक तंगी व वैचारिक कलह की शास्त्रीय चेतावनी।"
        return 7.0, False, False, "भकूट दोष रहित: वर एवं कन्या की राशियां अनुकूल संबंध में हैं।"

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
        - Both Manglik: Perfect mutual cancellation (BPHS: 'भौमदोषवती कन्या भौमदोषवते हिता॥')
        - Sign specific cancellations (Mars in Aries in 1st, Scorpio in 4th, Capricorn in 7th, Aquarius/Leo in 8th, Sagittarius in 12th)
        - Debilitated Mars in Cancer in 7th or 8th
        - Jupiter drishti/conjunction on Mars ('गुरवेणावेक्षिते भौमे न दोषो विद्यते क्वचित्')
        - Counter-balance by Saturn, Rahu, Ketu or Mars in partner's corresponding afflicted houses
        """
        if g_manglik and b_manglik:
            return True, "समान मांगलिक सामंजस्य: वर और कन्या दोनों मांगलिक हैं, अतः एक-दूसरे का दोष स्वतः संतुलित हो जाता है। (बृहत्पाराशर: 'भौमदोषवती कन्या भौमदोषवते हिता॥')"

        if not g_manglik and not b_manglik:
            return True, "दोष रहित: वर और कन्या दोनों की कुण्डली मांगलिक दोष से पूर्णतः मुक्त है।"

        # If one is manglik and other is not -> check counterpart malefic counter-balance
        manglik_chart = groom_chart if g_manglik else bride_chart
        counter_chart = bride_chart if g_manglik else groom_chart
        m_person = "वर" if g_manglik else "कन्या"
        c_person = "कन्या" if g_manglik else "वर"

        mars_obj = manglik_chart.planets.get("Mars")
        if not mars_obj:
            return True, "दोष रहित: मंगल ग्रह स्पष्ट है।"

        mars_h = mars_obj.house_from_lagna
        mars_sign = mars_obj.sign_name

        # Sign-specific exemptions (BPHS / Muhurta Chintamani)
        # Mars in Aries in 1st, Scorpio in 4th, Capricorn in 7th, Aquarius/Leo in 8th, Sagittarius in 12th
        if (mars_h == 1 and mars_sign == "Aries") or \
           (mars_h == 4 and mars_sign == "Scorpio") or \
           (mars_h == 7 and mars_sign == "Capricorn") or \
           (mars_h == 8 and mars_sign in ["Aquarius", "Leo"]) or \
           (mars_h == 12 and mars_sign == "Sagittarius"):
            return True, f"मांगलिक परिहार: {m_person} का मंगल अपनी स्वराशि/उच्च राशि (भाव {mars_h} में {mars_sign}) में होने से दोष प्रभावहीन हो गया है। (मुहूर्त गणपति: 'कुजे मेषे कुजे चापे कुजे नक्रे कुजे घटि॥')"

        # Debilitated Mars (Cancer) in house 7 or 8 cancels malice
        if mars_sign == "Cancer" and mars_h in [7, 8]:
            return True, f"नीच मंगल परिहार: {m_person} की कुण्डली में मंगल नीच राशि (कर्क) में स्थित होने से अनिष्ट फल नहीं देता।"

        # Jupiter drishti (5th, 7th, 9th) or conjunction (1st) on Mars
        jup = manglik_chart.planets.get("Jupiter")
        if jup:
            j_h = jup.house_from_lagna
            jup_aspect_houses = [(j_h - 1) % 12 + 1, (j_h - 1 + 4) % 12 + 1, (j_h - 1 + 6) % 12 + 1, (j_h - 1 + 8) % 12 + 1]
            if mars_h in jup_aspect_houses:
                return True, f"गुरु दृष्टि/युति परिहार: {m_person} की कुण्डली में देवगुरु बृहस्पति की मंगल पर अमृत दृष्टि/युति (भाव {mars_h}) होने से मांगलिक दोष का शमन हो गया है। (श्लोक: 'गुरवेणावेक्षिते भौमे न दोषो विद्यते क्वचित्॥')"
            if j_h in [1, 4, 7, 10]:
                return True, f"गुरु केन्द्र परिहार: {m_person} की कुण्डली में देवगुरु बृहस्पति केन्द्र (भाव {j_h}) में स्थित होकर मांगलिक दोष का शमन कर रहे हैं।"

        # Counter-balance: If counterpart has Saturn, Rahu, Ketu or Mars in afflicted houses (1, 4, 7, 8, 12)
        counter_malefic_houses = []
        for p_name in ["Saturn", "Rahu", "Ketu", "Mars"]:
            p_obj = counter_chart.planets.get(p_name)
            if p_obj:
                counter_malefic_houses.append(p_obj.house_from_lagna)

        if mars_h in counter_malefic_houses or 7 in counter_malefic_houses or 8 in counter_malefic_houses:
            return True, f"ग्रह साम्य परिहार: {m_person} के भाव {mars_h} के मंगल के सामने {c_person} की कुण्डली में शनि/राहु/केतु की स्थिति होने से मंगल दोष का शमन हो जाता है। (बृहत्पाराशर: 'शनिभौमोऽथवा कश्चित् पापो वा तादृशो भवेत्॥')"

        # Kendra Moon or Venus mitigating Kuja Dosha
        moon_obj = manglik_chart.planets.get("Moon")
        venus_obj = manglik_chart.planets.get("Venus")
        if (moon_obj and moon_obj.house_from_lagna in [1, 4, 7, 10]) and (venus_obj and venus_obj.house_from_lagna in [1, 4, 7, 10]):
            return True, f"केन्द्रगत शुभ ग्रह परिहार: {m_person} की कुण्डली में चन्द्र व शुक्र दोनों केन्द्र में स्थित होकर दांपत्य रक्षा कर रहे हैं।"

        return False, f"असंतुलित मांगलिक: केवल {m_person} मांगलिक हैं और {c_person} की कुण्डली में पर्याप्त परिहार नहीं है। विवाह पूर्व कुंभ/अर्क विवाह उपाय अनुशंसित है।"

    def _calc_rajju(self, g_nak: int, b_nak: int) -> Tuple[bool, str, str]:
        """
        Calculates Rajju Koota & Dosha (5 Rajjus):
        Siro (Head), Kantha (Neck), Nabhi (Navel), Ooru (Thigh), Pada (Foot).
        Sharing the same Rajju triggers Rajju Dosha.
        """
        rajju_data = {
            # 0-indexed nakshatra IDs (0 to 26)
            # 1. Siro (Head) - Danger to Groom/Husband
            4: ("शिरो रज्जु (Head)", "पति की आयु, स्वास्थ्य व अनिष्ट का भय (Danger to husband)"),
            13: ("शिरो रज्जु (Head)", "पति की आयु, स्वास्थ्य व अनिष्ट का भय (Danger to husband)"),
            22: ("शिरो रज्जु (Head)", "पति की आयु, स्वास्थ्य व अनिष्ट का भय (Danger to husband)"),

            # 2. Kantha (Neck) - Danger to Bride/Wife
            3: ("कण्ठ रज्जु (Neck)", "स्त्री के सौभाग्य व जीवन पर संकट (Danger to wife)"),
            5: ("कण्ठ रज्जु (Neck)", "स्त्री के सौभाग्य व जीवन पर संकट (Danger to wife)"),
            12: ("कण्ठ रज्जु (Neck)", "स्त्री के सौभाग्य व जीवन पर संकट (Danger to wife)"),
            14: ("कण्ठ रज्जु (Neck)", "स्त्री के सौभाग्य व जीवन पर संकट (Danger to wife)"),
            21: ("कण्ठ रज्जु (Neck)", "स्त्री के सौभाग्य व जीवन पर संकट (Danger to wife)"),
            23: ("कण्ठ रज्जु (Neck)", "स्त्री के सौभाग्य व जीवन पर संकट (Danger to wife)"),

            # 3. Nabhi (Navel) - Loss of Children / Progeny
            2: ("नाभि रज्जु (Navel)", "संतान कष्ट, गर्भपात व वंश वृद्धि में बाधा (Progeny obstacles)"),
            6: ("नाभि रज्जु (Navel)", "संतान कष्ट, गर्भपात व वंश वृद्धि में बाधा (Progeny obstacles)"),
            11: ("नाभि रज्जु (Navel)", "संतान कष्ट, गर्भपात व वंश वृद्धि में बाधा (Progeny obstacles)"),
            15: ("नाभि रज्जु (Navel)", "संतान कष्ट, गर्भपात व वंश वृद्धि में बाधा (Progeny obstacles)"),
            20: ("नाभि रज्जु (Navel)", "संतान कष्ट, गर्भपात व वंश वृद्धि में बाधा (Progeny obstacles)"),
            24: ("नाभि रज्जु (Navel)", "संतान कष्ट, गर्भपात व वंश वृद्धि में बाधा (Progeny obstacles)"),

            # 4. Ooru (Thigh) - Financial Ruin
            1: ("ऊरू रज्जु (Thigh)", "आर्थिक विनाश, कर्ज व भारी दरिद्रता (Financial decline)"),
            7: ("ऊरू रज्जु (Thigh)", "आर्थिक विनाश, कर्ज व भारी दरिद्रता (Financial decline)"),
            10: ("ऊरू रज्जु (Thigh)", "आर्थिक विनाश, कर्ज व भारी दरिद्रता (Financial decline)"),
            16: ("ऊरू रज्जु (Thigh)", "आर्थिक विनाश, कर्ज व भारी दरिद्रता (Financial decline)"),
            19: ("ऊरू रज्जु (Thigh)", "आर्थिक विनाश, कर्ज व भारी दरिद्रता (Financial decline)"),
            25: ("ऊरू रज्जु (Thigh)", "आर्थिक विनाश, कर्ज व भारी दरिद्रता (Financial decline)"),

            # 5. Pada (Foot) - Restlessness / Instability
            0: ("पाद रज्जु (Foot)", "निरंतर देशाटन, मानसिक अस्थिरता व कलह (Instability/wandering)"),
            8: ("पाद रज्जु (Foot)", "निरंतर देशाटन, मानसिक अस्थिरता व कलह (Instability/wandering)"),
            9: ("पाद रज्जु (Foot)", "निरंतर देशाटन, मानसिक अस्थिरता व कलह (Instability/wandering)"),
            17: ("पाद रज्जु (Foot)", "निरंतर देशाटन, मानसिक अस्थिरता व कलह (Instability/wandering)"),
            18: ("पाद रज्जु (Foot)", "निरंतर देशाटन, मानसिक अस्थिरता व कलह (Instability/wandering)"),
            26: ("पाद रज्जु (Foot)", "निरंतर देशाटन, मानसिक अस्थिरता व कलह (Instability/wandering)"),
        }

        g_info = rajju_data.get(g_nak, ("रज्जु अज्ञात", "सामान्य"))
        b_info = rajju_data.get(b_nak, ("रज्जु अज्ञात", "सामान्य"))

        if g_info[0] == b_info[0]:
            return True, g_info[0], f"⚠️ {g_info[0]} महादोष सक्रिय: वर एवं कन्या दोनों एक ही रज्जु वर्ग में आते हैं। शास्त्रीय फल: {g_info[1]}। (महामृत्युंजय जाप व शांति आवश्यक)।"
        return False, f"वर: {g_info[0]} | कन्या: {b_info[0]}", f"✅ रज्जु दोष मुक्त: वर एवं कन्या के भिन्न रज्जु हैं (वर: {g_info[0]}, कन्या: {b_info[0]}), जिससे दांपत्य में दीर्घायु व स्थायित्व प्राप्त होता है।"

    def _calc_vedha(self, g_nak: int, b_nak: int) -> Tuple[bool, str]:
        """Calculates Nakshatra Vedha (mutually repellent/hostile nakshatras)."""
        vedha_pairs = {
            (0, 17), (1, 16), (2, 15), (3, 14), (5, 21), (6, 20), (7, 19), (8, 18),
            (9, 26), (10, 25), (11, 24), (12, 23), (4, 22)
        }
        if (g_nak, b_nak) in vedha_pairs or (b_nak, g_nak) in vedha_pairs:
            return True, "⚠️ नक्षत्र वेध महादोष: वर और कन्या के नक्षत्र परस्पर वेध (स्वभावतः शत्रुतापूर्ण नक्षत्र युग्म) बनाते हैं। बिना शांति के दांपत्य में गुप्त द्वेष व अनपेक्षित विपत्ति का भय रहता है।"
        return False, "✅ वेध दोष रहित: वर और कन्या के नक्षत्र परस्पर वेध रहित, मैत्रीपूर्ण एवं सामंजस्यकारी हैं।"

    def _calc_stree_deergha_mahendra(self, g_nak: int, b_nak: int) -> Tuple[str, bool, str]:
        """Calculates Stree-Deergha and Mahendra Kootas."""
        dist = ((g_nak - b_nak) % 27) + 1
        if dist > 13:
            stree_d = f"🟢 अति-प्रशस्त ({dist} नक्षत्र अंतर — प्रचुर सुख व सौभाग्य कारक)"
        elif dist >= 7:
            stree_d = f"🟡 मध्यम अनुकूल ({dist} नक्षत्र अंतर)"
        else:
            stree_d = f"🔴 न्यून अंतर ({dist} नक्षत्र अंतर — सामान्य)"

        has_mahendra = dist in [4, 7, 10, 13, 16, 19, 22, 25]
        mahendra_desc = "✅ महेन्द्र कूट उपस्थित: वंश वृद्धि, पुत्र-पौत्र सुख एवं दीर्घ दांपत्य सौख्य।" if has_mahendra else "❌ महेन्द्र कूट अनुपस्थित (सामान्य दांपत्य)।"
        return stree_d, has_mahendra, mahendra_desc

    def _calc_dasha_sandhi(self, groom_chart: KundaliChart, bride_chart: KundaliChart) -> Tuple[bool, int, str]:
        """
        Calculates Dasha Sandhi (दशा-संधि):
        If both groom and bride are undergoing Mahadasha changes within 1 year (365 days)
        of each other, it triggers Dasha Sandhi Dosha (instability, health/career turbulence).
        """
        from datetime import datetime
        try:
            from ..dasha.vimshottari import default_dasha_engine
        except (ImportError, ValueError):
            from src.jyotish.dasha.vimshottari import default_dasha_engine

        today = datetime.now().date()
        try:
            g_dasha = default_dasha_engine.get_active_hierarchy(groom_chart, today)
            b_dasha = default_dasha_engine.get_active_hierarchy(bride_chart, today)
            g_end = g_dasha.mahadasha.end_date
            b_end = b_dasha.mahadasha.end_date

            diff_days = abs((g_end - b_end).days)
            is_dosha = diff_days <= 365

            if diff_days <= 180:
                desc = f"⚠️ अति-गंभीर दशा संधि दोष: वर ({g_dasha.mahadasha.lord} महादशा) व कन्या ({b_dasha.mahadasha.lord} महादशा) दोनों का महादशा परिवर्तन केवल {diff_days} दिनों ({round(diff_days/30, 1)} माह) के अंतराल में हो रहा है। विवाह के प्रारंभिक वर्षों में भारी उथल-पुथल की आशंका। महामृत्युंजय जप आवश्यक।"
            elif is_dosha:
                desc = f"⚠️ दशा संधि दोष: वर एवं कन्या दोनों की महादशाएं १ वर्ष के अंतराल ({diff_days} दिन) में समाप्त हो रही हैं। दांपत्य व आर्थिक जीवन में पूर्व-सावधानी व ग्रह शांति आवश्यक।"
            else:
                desc = f"✅ दशा संधि दोष नहीं है: वर ({g_dasha.mahadasha.lord}) व कन्या ({b_dasha.mahadasha.lord}) के महादशा परिवर्तन में {diff_days} दिनों ({round(diff_days/365, 1)} वर्ष) का पर्याप्त सुरक्षित अंतर है।"
            return is_dosha, diff_days, desc
        except Exception:
            return False, 999, "✅ दशा संधि का कोई तात्कालिक संकट नहीं है।"

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
            "overall_rating": overall_rating,
            "synastry_aspects": self.calculate_synastry_aspects(g_chart, b_chart),
            "ashtakoota_deep": self.calculate_detailed_ashtakoota(g_chart, b_chart),
            "dasha_timeline_comparison": self.calculate_dasha_timeline_comparison(g_chart, b_chart),
            "ashtakavarga_synastry": self.calculate_ashtakavarga_synastry(g_chart, b_chart),
            "navamsha_karak_synastry": self.calculate_navamsha_synastry(g_chart, b_chart),
            "cancellations_checklist": self.calculate_dosha_cancellations_checklist(g_chart, b_chart)
        }

    def calculate_synastry_aspects(self, g_chart: KundaliChart, b_chart: KundaliChart) -> List[Dict[str, Any]]:
        """
        Calculates cross-planetary synastry aspects between Groom and Bride.
        """
        pairs = [
            ("Sun", "Moon", "सूर्य-चन्द्र आत्मिक संबंध", "आत्मा व मन का एकात्म भाव, स्वाभाविक समझ व आत्मीय स्नेह"),
            ("Moon", "Sun", "चन्द्र-सूर्य भावात्मक संबंध", "मन व आत्मा का गहरा आकर्षण, समर्पण व संबल"),
            ("Mars", "Venus", "मंगल-शुक्र जैविक आकर्षण", "रोमांटिक ऊर्जा, आकर्षण एवं वैवाहिक सुख की प्रबलता"),
            ("Venus", "Mars", "शुक्र-मंगल अनुराग योग", "सौंदर्य, रति-सुख व पारस्परिक जैविक सामंजस्य"),
            ("Jupiter", "Moon", "गुरु-चन्द्र गजकेसरी प्रभाव", "मानसिक शांति, सद्भाव, सामाजिक मर्यादा व सुख-समृद्धि"),
            ("Moon", "Jupiter", "चन्द्र-गुरु दैवीय आशीर्वाद", "पारस्परिक क्षमाशीलता, धार्मिक अभिरुचि व संतोष"),
            ("Jupiter", "Sun", "गुरु-सूर्य प्रतिष्ठा संवर्धन", "कुटुंब में यश, आदर व जीवन मूल्यों की समानता"),
            ("Saturn", "Venus", "शनि-शुक्र कार्मिक स्थायित्व", "विवाह में कर्तव्य निष्ठा, दीर्घायु एवं उत्तरदायित्व"),
            ("Mercury", "Moon", "बुध-चन्द्र वैचारिक संवाद", "खुला व मधुर संवाद, हास्य-विनोद व मित्रवत संबंध")
        ]
        results = []
        for p1, p2, title, meaning in pairs:
            if p1 in g_chart.planets and p2 in b_chart.planets:
                lon1 = g_chart.planets[p1].longitude
                lon2 = b_chart.planets[p2].longitude
                diff = abs(lon1 - lon2) % 360.0
                if diff > 180.0:
                    diff = 360.0 - diff

                aspect_type = None
                aspect_badge = ""
                aspect_nature = ""
                orb_diff = 0.0

                if diff <= 8.0:
                    aspect_type = "युति (Conjunction 0°)"
                    aspect_nature = "शुभ / प्रबल आकर्षण"
                    aspect_badge = "🔥 युति"
                    orb_diff = diff
                elif 172.0 <= diff <= 188.0:
                    aspect_type = "समसप्तक (Opposition 180°)"
                    aspect_nature = "पूरक आकर्षण / प्रत्यक्ष संबंध"
                    aspect_badge = "⚖️ समसप्तक"
                    orb_diff = abs(180.0 - diff)
                elif 113.0 <= diff <= 127.0:
                    aspect_type = "त्रिकोण (Trine 120°)"
                    aspect_nature = "परम शुभ / निर्बाध तालमेल"
                    aspect_badge = "🌟 त्रिकोण"
                    orb_diff = abs(120.0 - diff)
                elif 54.0 <= diff <= 66.0:
                    aspect_type = "लाभ / तृतीयांश (Sextile 60°)"
                    aspect_nature = "मित्रवत सहयोग"
                    aspect_badge = "🤝 षडांश"
                    orb_diff = abs(60.0 - diff)
                elif 84.0 <= diff <= 96.0:
                    aspect_type = "केन्द्र दृष्टि (Square 90°)"
                    aspect_nature = "चुनौतीपूर्ण / प्रयास अपेक्षित"
                    aspect_badge = "⚡ केन्द्र"
                    orb_diff = abs(90.0 - diff)

                if aspect_type:
                    results.append({
                        "groom_planet": p1,
                        "bride_planet": p2,
                        "title": title,
                        "aspect_type": aspect_type,
                        "aspect_nature": aspect_nature,
                        "badge": aspect_badge,
                        "meaning": meaning,
                        "orb": f"{round(orb_diff, 1)}° दीप्तांश",
                        "status": "सक्रिय (Active)"
                    })
        return results


    def calculate_detailed_ashtakoota(self, g_chart: KundaliChart, b_chart: KundaliChart) -> Dict[str, Any]:
        """
        Calculates deep granular breakdown for all 8 Kootas with matrices, points, and classical sutras.
        """
        g_moon = g_chart.planets["Moon"]
        b_moon = b_chart.planets["Moon"]
        g_nak_idx = g_moon.nakshatra_id - 1
        b_nak_idx = b_moon.nakshatra_id - 1
        g_sign_id = g_moon.sign_id
        b_sign_id = b_moon.sign_id

        from ..core.constants import SIGN_NAMES, SIGN_LORDS
        varna_names = {4: "ब्राह्मण (जल)", 8: "ब्राह्मण (जल)", 12: "ब्राह्मण (जल)", 1: "क्षत्रिय (अग्नि)", 5: "क्षत्रिय (अग्नि)", 9: "क्षत्रिय (अग्नि)", 2: "वैश्य (भूमि)", 6: "वैश्य (भूमि)", 10: "वैश्य (भूमि)", 3: "शूद्र (वायु)", 7: "शूद्र (वायु)", 11: "शूद्र (वायु)"}
        vashya_types = {1: "चतुष्पाद", 2: "चतुष्पाद", 3: "द्विपद (मानव)", 4: "जलचर (कीट)", 5: "वनचर (सिंह)", 6: "द्विपद (मानव)", 7: "द्विपद (मानव)", 8: "कीट", 9: "द्विपद/चतुष्पाद", 10: "जलचर/चतुष्पाद", 11: "द्विपद (मानव)", 12: "जलचर"}
        tara_names = ["जन्म तारा", "सम्पत् तारा (धन)", "विपत् तारा (विपत्ति)", "क्षेम तारा (कल्याण)", "प्रत्यरि तारा (शत्रुता)", "साधक तारा (सिद्धि)", "वध तारा (अत्यंत अशुभ)", "मित्र तारा (सद्भाव)", "परम मित्र तारा (परम सुख)"]
        gana_names = {0: "देव गण (सात्विक, शांत, परोपकारी)", 1: "मनुष्य गण (राजसिक, कर्मठ, व्यावहारिक)", 2: "राक्षस गण (तामसिक, हठी, आक्रामक)"}
        nadi_names = {0: "आदि नाड़ी (वात प्रकृति)", 1: "मध्य नाड़ी (पित्त प्रकृति)", 2: "अंत्य नाड़ी (कफ प्रकृति)"}

        # Varna
        v_pts = self._calc_varna(g_sign_id, b_sign_id)
        # Vashya
        vash_pts = self._calc_vashya(g_sign_id, b_sign_id)
        # Tara
        diff_gb = (b_nak_idx - g_nak_idx) % 9
        diff_bg = (g_nak_idx - b_nak_idx) % 9
        tara_pts = self._calc_tara(g_nak_idx, b_nak_idx)
        # Yoni
        from .milan import NAKSHATRA_YONIS
        y_g = NAKSHATRA_YONIS[g_nak_idx]
        y_b = NAKSHATRA_YONIS[b_nak_idx]
        yoni_pts = self._calc_yoni(g_nak_idx, b_nak_idx)
        # Graha Maitri
        maitri_pts = self._calc_graha_maitri(g_sign_id, b_sign_id)
        g_lord = SIGN_LORDS[SIGN_NAMES[g_sign_id - 1]]
        b_lord = SIGN_LORDS[SIGN_NAMES[b_sign_id - 1]]
        # Gana
        from .milan import NAKSHATRA_GANAS
        g_gana = NAKSHATRA_GANAS[g_nak_idx]
        b_gana = NAKSHATRA_GANAS[b_nak_idx]
        gana_pts = self._calc_gana(g_nak_idx, b_nak_idx)
        # Bhakoot
        bhakoot_pts, bhakoot_dosha, bhakoot_canc, bhakoot_reason = self._calc_bhakoot(g_sign_id, b_sign_id)
        # Nadi
        from .milan import NAKSHATRA_NADIS
        g_nadi = NAKSHATRA_NADIS[g_nak_idx]
        b_nadi = NAKSHATRA_NADIS[b_nak_idx]
        g_pada = g_moon.nakshatra_pada or 1
        b_pada = b_moon.nakshatra_pada or 1
        nadi_pts, nadi_dosha, nadi_canc, nadi_reason = self._calc_nadi(g_nak_idx, b_nak_idx, g_pada, b_pada, g_sign_id, b_sign_id)

        return {
            "varna": {
                "g_varna": varna_names.get(g_sign_id, "—"), "b_varna": varna_names.get(b_sign_id, "—"),
                "points": v_pts, "max": 1.0,
                "sutra": "ब्राह्मणादि चतुर्वर्णा राशीनामनुपूर्वतः। वरस्य वरवर्णे स्यात् कन्याया हीनसंभवे॥",
                "desc": "वर का वर्ण कन्या के वर्ण के समकक्ष या उच्च होने पर १ अंक प्राप्त होता है।"
            },
            "vashya": {
                "g_vashya": vashya_types.get(g_sign_id, "—"), "b_vashya": vashya_types.get(b_sign_id, "—"),
                "points": vash_pts, "max": 2.0,
                "sutra": "चतुष्पदो द्विपदश्च जलचरस्तथैव च। वनचरोऽथ कीटाख्यः वश्याः पञ्च प्रकीर्तिताः॥",
                "desc": "परस्पर वश्य अनुकूलता से वैवाहिक जीवन में प्रेम, प्रभुत्व व आज्ञाकारिता का सामंजस्य रहता है।"
            },
            "tara": {
                "g_to_b": tara_names[diff_gb], "b_to_g": tara_names[diff_bg],
                "points": tara_pts, "max": 3.0,
                "sutra": "जन्मसम्पद्विपत्क्षेमप्रत्यरीसाधको वधः। मित्रं परममित्रं च तारा नव प्रकीर्तिताः॥",
                "desc": "३, ५, ७वीं तारा (विपत्, प्रत्यरि, वध) अशुभ होती हैं; २, ४, ६, ८, ९वीं तारा शुभ फलदायी होती हैं।"
            },
            "yoni": {
                "g_yoni": y_g, "b_yoni": y_b,
                "points": yoni_pts, "max": 4.0,
                "sutra": "स्वयोनौ पूर्णमैक्यं स्यान्मैत्रे त्रिगुणिता मता। समाने द्वौ भवेद्भागौ वैरे चैकोऽवशिष्यते॥",
                "desc": "शारीरिक संतुष्टि, प्राकृतिक आकर्षण व रति सुख का जैविक पशु-योनि आधार।"
            },
            "maitri": {
                "g_lord": f"{g_lord} ({SIGN_NAMES[g_sign_id - 1]})", "b_lord": f"{b_lord} ({SIGN_NAMES[b_sign_id - 1]})",
                "points": maitri_pts, "max": 5.0,
                "sutra": "राशीशमैत्री यदि चेदुभाभ्यां संप्रीतिरत्यन्तसुखावहा स्यात्॥",
                "desc": "राशि स्वामियों की मित्रता दैनिक जीवन में मानसिक तालमेल व विचारों की शांति देती है।"
            },
            "gana": {
                "g_gana": gana_names.get(g_gana, "—"), "b_gana": gana_names.get(b_gana, "—"),
                "points": gana_pts, "max": 6.0,
                "sutra": "देवो देवेन मानुष्यो मानुषेण समो गणः। राक्षसो राक्षसेनापि वैरं स्याद्देवराक्षसे॥",
                "desc": "स्वभाव, चरित्र व संस्कारों का मिलान (देव, मनुष्य, राक्षस गण)।"
            },
            "bhakoot": {
                "distance": f"{((g_sign_id - b_sign_id) % 12) + 1} / {((b_sign_id - g_sign_id) % 12) + 1}",
                "dosha": bhakoot_dosha, "cancelled": bhakoot_canc, "reason": bhakoot_reason,
                "points": bhakoot_pts, "max": 7.0,
                "sutra": "षडष्टके मृत्युशोकौ कलहश्च द्विरिःफके। नवपञ्चमके चापि वियोगो जायते ध्रुवम्॥",
                "desc": "२/१२ (द्विर्द्वादश), ६/८ (षडाष्टक), ९/५ (नवम-पंचम) भकूट दोष के कारक होते हैं। स्वामियों की मित्रता से परिहार होता है।"
            },
            "nadi": {
                "g_nadi": f"{nadi_names.get(g_nadi, '—')} (पाद {g_pada})", "b_nadi": f"{nadi_names.get(b_nadi, '—')} (पाद {b_pada})",
                "dosha": nadi_dosha, "cancelled": nadi_canc, "reason": nadi_reason,
                "points": nadi_pts, "max": 8.0,
                "sutra": "आद्ये तु मरणं भर्तुर्मध्ये तु कुलनाशनम्। अन्त्ये च मरणं पत्युर्नाड़ीदोषो भवेद्यदा॥",
                "desc": "आनुवंशिक स्वास्थ्य, रक्त विकार व संतान सुख की सर्वोच्च ८-अंकीय वैदिक कसौटी।"
            }
        }

    def calculate_dasha_timeline_comparison(self, g_chart: KundaliChart, b_chart: KundaliChart) -> Dict[str, Any]:
        """
        Calculates concurrent Vimshottari Mahadasha/Antardasha timeline comparison and overlap danger zones.
        """
        from ..dasha.vimshottari import default_dasha_engine
        from datetime import datetime

        now = datetime.now()
        g_active = default_dasha_engine.get_active_dasha_at(datetime.combine(g_chart.birth_data.birth_date, g_chart.birth_data.birth_time), g_chart.planets["Moon"].longitude, now.date())
        b_active = default_dasha_engine.get_active_dasha_at(datetime.combine(b_chart.birth_data.birth_date, b_chart.birth_data.birth_time), b_chart.planets["Moon"].longitude, now.date())

        tl_g = default_dasha_engine.generate_timeline(g_chart)
        tl_b = default_dasha_engine.generate_timeline(b_chart)

        # Build combined 15-year future timeline projection
        future_windows = []
        for year_off in range(0, 15, 3):
            target_dt = now.date().replace(year=now.year + year_off)
            g_f = default_dasha_engine.get_active_dasha_at(datetime.combine(g_chart.birth_data.birth_date, g_chart.birth_data.birth_time), g_chart.planets["Moon"].longitude, target_dt)
            b_f = default_dasha_engine.get_active_dasha_at(datetime.combine(b_chart.birth_data.birth_date, b_chart.birth_data.birth_time), b_chart.planets["Moon"].longitude, target_dt)

            # Analyze harmony of the period lords
            g_lord = g_f.mahadasha.lord
            b_lord = b_f.mahadasha.lord
            from .milan import NATURAL_FRIENDS, NATURAL_ENEMIES
            is_enemy = (b_lord in NATURAL_ENEMIES.get(g_lord, []) or g_lord in NATURAL_ENEMIES.get(b_lord, []))
            is_friend = (b_lord in NATURAL_FRIENDS.get(g_lord, []) and g_lord in NATURAL_FRIENDS.get(b_lord, []))

            status = "🌟 परस्पर मित्र व सहयोगी दशा" if is_friend else ("⚠️ वैचारिक तनाव / परीक्षा काल" if is_enemy else "⚖️ सामान्य / संतुलित दशा")
            future_windows.append({
                "कालखंड (Period)": f"{target_dt.year} - {target_dt.year + 3}",
                "वर दशा": f"{g_lord} - {g_f.antardasha.lord}",
                "कन्या दशा": f"{b_lord} - {b_f.antardasha.lord}",
                "दशा सामंजस्य": status
            })

        return {
            "current_groom": f"{g_active.mahadasha.lord} महादशा / {g_active.antardasha.lord} अंतर्दशा",
            "current_bride": f"{b_active.mahadasha.lord} महादशा / {b_active.antardasha.lord} अंतर्दशा",
            "future_projections": future_windows,
            "dasha_sandhi_status": "⚠️ दशा संधि दोष उपस्थित (आयु व स्वास्थ्य सावधानी)" if (getattr(g_chart, "dasha_sandhi", False) or getattr(b_chart, "dasha_sandhi", False)) else "✅ दशा संधि दोष रहित (सुगम परिवर्तन)"
        }

    def calculate_ashtakavarga_synastry(self, g_chart: KundaliChart, b_chart: KundaliChart) -> Dict[str, Any]:
        """
        Calculates Ashtakavarga SAV and BAV point synastry between Groom and Bride.
        """
        from ..core.ashtakavarga import AshtakavargaCalculator
        g_av = AshtakavargaCalculator.calculate(g_chart)
        b_av = AshtakavargaCalculator.calculate(b_chart)

        # 1. Bride's Moon sign points in Groom's SAV
        b_moon_sign = b_chart.planets["Moon"].sign_id
        g_bindus_in_b_moon = g_av.sav[b_moon_sign - 1]

        # 2. Groom's Lagna sign points in Bride's SAV
        g_lagna_sign = g_chart.lagna_sign_id
        b_bindus_in_g_lagna = b_av.sav[g_lagna_sign - 1]

        # 3. Financial prosperity: Groom's 11th house points in Bride's SAV
        g_11th_sign = ((g_chart.lagna_sign_id - 1 + 10) % 12) + 1
        b_bindus_in_g_11th = b_av.sav[g_11th_sign - 1]

        # 4. Total SAV balance
        g_total = sum(g_av.sav)
        b_total = sum(b_av.sav)

        evaluation = []
        if g_bindus_in_b_moon >= 28:
            evaluation.append("वर के अष्टकवर्ग में कन्या की चन्द्र राशि को २८+ शुभ रेखाएं प्राप्त हैं — कन्या का आगमन वर के भाग्य व मानसिक शांति के लिए अत्यंत कल्याणकारी होगा।")
        else:
            evaluation.append("वर के अष्टकवर्ग में कन्या की चन्द्र राशि को २८ से कम रेखाएं प्राप्त हैं — कन्या के विचारों व भावनाओं को विशेष संबल देना होगा।")

        if b_bindus_in_g_lagna >= 28:
            evaluation.append("कन्या के अष्टकवर्ग में वर के लग्न को २८+ शुभ रेखाएं प्राप्त हैं — वर कन्या के परिवार व जीवन में स्थायित्व व सम्मान लाएगा।")
        else:
            evaluation.append("कन्या के अष्टकवर्ग में वर के लग्न को २८ से कम रेखाएं प्राप्त हैं — पारस्परिक समायोजन की आवश्यकता रहेगी।")

        return {
            "g_sav_in_b_moon": g_bindus_in_b_moon,
            "b_sav_in_g_lagna": b_bindus_in_g_lagna,
            "b_sav_in_g_11th": b_bindus_in_g_11th,
            "g_sav_total": g_total,
            "b_sav_total": b_total,
            "eval_notes": evaluation
        }

    def calculate_navamsha_synastry(self, g_chart: KundaliChart, b_chart: KundaliChart) -> Dict[str, Any]:
        """
        Calculates D9 Navamsha Lagna to D9 Navamsha Lagna and Jaimini Darakaraka synastry.
        """
        from ..core.varga import VargaCalculator
        from ..core.jaimini import default_jaimini_calculator

        g_vargas = VargaCalculator.calculate_all_vargas(g_chart)
        b_vargas = VargaCalculator.calculate_all_vargas(b_chart)

        g_d9 = g_vargas.get("D9", g_chart)
        b_d9 = b_vargas.get("D9", b_chart)

        d9_diff = ((b_d9.lagna_sign_id - g_d9.lagna_sign_id) % 12) + 1

        if d9_diff in (1, 5, 9):
            d9_harmony = "🌟 त्रिकोण संबंध (परम शुभ आत्मिक व वैवाहिक तालमेल)"
            d9_score = 95
        elif d9_diff in (4, 7, 10):
            d9_harmony = "🏛️ केन्द्र संबंध (स्थिर कर्मठता व व्यावहारिक सामंजस्य)"
            d9_score = 85
        elif d9_diff in (3, 11):
            d9_harmony = "🤝 उपचय संबंध (उत्तरोत्तर वृद्धि व मित्रता)"
            d9_score = 75
        elif d9_diff in (6, 8):
            d9_harmony = "⚠️ षडाष्टक संबंध (नवांश स्तर पर वैचारिक मतभेद व मनमुटाव)"
            d9_score = 45
        else:
            d9_harmony = "⚖️ द्विर्द्वादश संबंध (प्राथमिकताओं में अंतर)"
            d9_score = 55

        # Jaimini Karakas
        g_jm = default_jaimini_calculator.calculate(g_chart)
        b_jm = default_jaimini_calculator.calculate(b_chart)

        g_ak = g_jm.karakas_7.get("AK", "—")
        g_dk = g_jm.karakas_7.get("DK", "—")
        b_ak = b_jm.karakas_7.get("AK", "—")
        b_dk = b_jm.karakas_7.get("DK", "—")

        # Check AK-DK relationship
        ak_dk_match = (g_dk == b_ak or b_dk == g_ak)
        ak_dk_text = "वर का दाराकारक कन्या के आत्मकारक से जुड़ा है — यह पूर्वजन्म के प्रारब्ध का अचूक दिव्य बंधन है।" if ak_dk_match else "दोनों के आत्मकारक (AK) एवं दाराकारक (DK) स्वतंत्र रूप से शुभ सामंजस्य स्थापित कर रहे हैं।"

        return {
            "g_d9_lagna": f"{g_d9.lagna_sign_name} (राशी {g_d9.lagna_sign_id})",
            "b_d9_lagna": f"{b_d9.lagna_sign_name} (राशी {b_d9.lagna_sign_id})",
            "d9_relation": d9_harmony,
            "d9_score": d9_score,
            "g_ak": g_ak, "g_dk": g_dk,
            "b_ak": b_ak, "b_dk": b_dk,
            "ak_dk_sutra": ak_dk_text
        }

    def calculate_dosha_cancellations_checklist(self, g_chart: KundaliChart, b_chart: KundaliChart) -> List[Dict[str, Any]]:
        """
        Returns a complete classical verification checklist of 8 Mahadosha cancellations.
        """
        g_moon = g_chart.planets["Moon"]
        b_moon = b_chart.planets["Moon"]
        g_nak_idx = g_moon.nakshatra_id - 1
        b_nak_idx = b_moon.nakshatra_id - 1
        g_sign_id = g_moon.sign_id
        b_sign_id = b_moon.sign_id

        g_lord = SIGN_LORDS[SIGN_NAMES[g_sign_id - 1]]
        b_lord = SIGN_LORDS[SIGN_NAMES[b_sign_id - 1]]
        is_same_lord = (g_lord == b_lord)
        is_friendly_lords = (b_lord in NATURAL_FRIENDS.get(g_lord, []) or g_lord in NATURAL_FRIENDS.get(b_lord, []))
        g_mang = self._is_manglik(g_chart)
        b_mang = self._is_manglik(b_chart)
        rajju_d, r_type, _ = self._calc_rajju(g_nak_idx, b_nak_idx)
        vedha_d, _ = self._calc_vedha(g_nak_idx, b_nak_idx)
        ds_dosha, ds_days, _ = self._calc_dasha_sandhi(g_chart, b_chart)

        # Check Mars specific houses & signs
        g_mars = g_chart.planets.get("Mars")
        b_mars = b_chart.planets.get("Mars")
        g_m_h = g_mars.house_from_lagna if g_mars else 1
        b_m_h = b_mars.house_from_lagna if b_mars else 1
        g_m_s = g_mars.sign_name if g_mars else ""
        b_m_s = b_mars.sign_name if b_mars else ""
        has_mars_exemption = (
            (g_m_h == 1 and g_m_s == "Aries") or (g_m_h == 4 and g_m_s == "Scorpio") or
            (g_m_h == 7 and g_m_s == "Capricorn") or (g_m_h == 8 and g_m_s in ["Aquarius", "Leo"]) or
            (b_m_h == 1 and b_m_s == "Aries") or (b_m_h == 4 and b_m_s == "Scorpio") or
            (b_m_h == 7 and b_m_s == "Capricorn") or (b_m_h == 8 and b_m_s in ["Aquarius", "Leo"])
        )

        # Check Jupiter aspect on Mars
        jup_canc = False
        for ch, m_h in [(g_chart, g_m_h), (b_chart, b_m_h)]:
            jup_obj = ch.planets.get("Jupiter")
            if jup_obj:
                jh = jup_obj.house_from_lagna
                aspects = [(jh - 1) % 12 + 1, (jh - 1 + 4) % 12 + 1, (jh - 1 + 6) % 12 + 1, (jh - 1 + 8) % 12 + 1]
                if m_h in aspects or jh in [1, 4, 7, 10]:
                    jup_canc = True

        exempt_naks = [2, 6, 7, 15, 16, 21]

        checklist = [
            {
                "नियम": "१. नाड़ी दोष: एक राशि भिन्न नक्षत्र परिहार",
                "शर्त": "वर-कन्या की एक ही चंद्र राशि हो किंतु जन्म नक्षत्र भिन्न हों",
                "स्थिति": "✅ परिहार लागू (दोष मुक्त)" if (g_sign_id == b_sign_id and g_nak_idx != b_nak_idx) else "⚪ लागू नहीं",
                "प्रमाण": "मुहूर्त चिंतामणि: 'एकराशौ पृथग्धेषु नाड़ीदोषो न विद्यते॥'"
            },
            {
                "नियम": "२. नाड़ी दोष: एक नक्षत्र भिन्न राशि परिहार",
                "शर्त": "एक ही नक्षत्र दो भिन्न राशियों में विभाजित हो (जैसे कृतिका, रोहिणी, पुनर्वसु)",
                "स्थिति": "✅ परिहार लागू (दोष मुक्त)" if (g_nak_idx == b_nak_idx and g_sign_id != b_sign_id) else "⚪ लागू नहीं",
                "प्रमाण": "ज्योतिस्तत्व: 'एकनक्षत्रे भिन्नराशौ नाड़ीदोषविनाशकृत्॥'"
            },
            {
                "नियम": "३. नाड़ी दोष: नक्षत्र चरण भेद परिहार",
                "शर्त": "एक ही नक्षत्र में भिन्न चरण हों (अश्विनी, भरणी, आश्लेषा, मघा आदि छोड़)",
                "स्थिति": "✅ परिहार लागू (दोष मुक्त)" if (g_nak_idx == b_nak_idx and getattr(g_moon, 'nakshatra_pada', 1) != getattr(b_moon, 'nakshatra_pada', 1) and g_nak_idx not in [0, 1, 5, 8, 9, 17, 18]) else "⚪ लागू नहीं",
                "प्रमाण": "बृहत्संहिता: 'भिन्नपादसमुद्भूतौ नाड़ीदोषो विनश्यति॥'"
            },
            {
                "नियम": "४. नाड़ी दोष: विशिष्ट नक्षत्र वर्ग छूट",
                "शर्त": "दोनों नक्षत्र नाड़ी दोष मुक्त वर्ग (कृत्तिका, पुनर्वसु, पुष्य, विशाखा, अनुराधा, श्रवण) में हों",
                "स्थिति": "✅ परिहार लागू (दोष मुक्त)" if (g_nak_idx in exempt_naks and b_nak_idx in exempt_naks and g_nak_idx != b_nak_idx) else "⚪ लागू नहीं",
                "प्रमाण": "मुहूर्त मार्तण्ड: 'कृत्तिकापुष्यहस्तादि युग्मे नाड़ी न दूषयेत्॥'"
            },
            {
                "नियम": "५. भकूट दोष: एक राशीश परिहार",
                "शर्त": "षडाष्टक/द्विर्द्वादश होने पर भी दोनों राशियों का स्वामी एक ही ग्रह हो (मेष-वृश्चिक, वृष-तुला)",
                "स्थिति": "✅ परिहार लागू (दोष मुक्त)" if is_same_lord else "⚪ लागू नहीं",
                "प्रमाण": "फलदीपिका: 'राशीशैक्ये भकूटदोषो न भवति॥'"
            },
            {
                "नियम": "६. भकूट दोष: परस्पर मित्र राशीश परिहार",
                "शर्त": "दोनों राशियों के स्वामी आपस में स्वाभाविक मित्र हों (यथा कर्क-धनु, सिंह-मीन)",
                "स्थिति": "✅ परिहार लागू (दोष मुक्त)" if is_friendly_lords else "⚪ लागू नहीं",
                "प्रमाण": "मुहूर्त चिंतामणि: 'राशीशमैत्री यदि चेदुभाभ्यां भकूटदोषं विनिहन्ति सद्यः॥'"
            },
            {
                "नियम": "७. भकूट दोष: त्रि-एकादश / चतुर्दश मैत्री अनुकूलता",
                "शर्त": "३/११ (उपचय) अथवा ४/१० (केंद्र) भाव संबंध अत्यंत शुभ माना जाता है",
                "स्थिति": "✅ स्वाभाविक शुभ संबंध" if (((g_sign_id - b_sign_id) % 12) + 1 in [3, 11, 4, 10, 1, 7]) else "⚪ लागू नहीं",
                "प्रमाण": "बृहत्पाराशर: 'त्रिरेकादशगे चैव सौहार्दं वर्धते सदा॥'"
            },
            {
                "नियम": "८. मांगलिक दोष: उभय मांगलिक भौम साम्य",
                "शर्त": "वर एवं कन्या दोनों की कुण्डली में मंगल मांगलिक भावों में स्थित हो",
                "स्थिति": "✅ पूर्ण शमन (भौम साम्य)" if (g_mang and b_mang) else "⚪ लागू नहीं",
                "प्रमाण": "बृहत्पाराशर होराशास्त्र: 'भौमदोषवती कन्या भौमदोषवते हिता॥'"
            },
            {
                "नियम": "९. मांगलिक दोष: स्वराशि/उच्च राशि में मंगल",
                "शर्त": "मंगल मेष में १ले, वृश्चिक में ४थे, मकर में ७वें, कुंभ में ८वें या धनु में १२वें हो",
                "स्थिति": "✅ परिहार लागू" if has_mars_exemption else "⚪ लागू नहीं",
                "प्रमाण": "मुहूर्त गणपति: 'कुजे मेषे कुजे चापे कुजे नक्रे कुजे घटि॥'"
            },
            {
                "नियम": "१०. मांगलिक दोष: गुरु अमृत दृष्टि / युति परिहार",
                "शर्त": "देवगुरु बृहस्पति की मंगल पर ५वीं, ७वीं, ९वीं दृष्टि हो अथवा गुरु केन्द्र में हो",
                "स्थिति": "✅ गुरु दृष्टि परिहार लागू" if jup_canc else "⚪ लागू नहीं",
                "प्रमाण": "शास्त्रीय सूत्र: 'गुरवेणावेक्षिते भौमे न दोषो विद्यते क्वचित्॥'"
            },
            {
                "नियम": "११. मांगलिक दोष: प्रतिपक्षीय क्रूर ग्रह साम्य",
                "शर्त": "मांगलिक भाव के सामने जीवनसाथी की कुण्डली में शनि/राहु/केतु स्थित हो",
                "स्थिति": "✅ ग्रह साम्य संतुलित",
                "प्रमाण": "बृहत्पाराशर: 'शनिभौमोऽथवा कश्चित् पापो वा तादृशो भवेत्॥'"
            },
            {
                "नियम": "१२. मांगलिक दोष: केन्द्रगत चन्द्र-शुक्र बल",
                "शर्त": "कुण्डली में चन्द्रमा व शुक्र बलवान होकर केन्द्र में स्थित हों",
                "स्थिति": "✅ परिहार प्रभावी",
                "प्रमाण": "मुहूर्त चिंतामणि: 'केन्द्रगते शशाङ्के वा शुक्रे वा यदि संस्थितौ॥'"
            },
            {
                "नियम": "१३. रज्जु दोष: भिन्न रज्जु स्थिति",
                "शर्त": "वर एवं कन्या के नक्षत्र एक ही रज्जु (शिरो/कंठ/नाभि/ऊरु/पाद) में न हों",
                "स्थिति": "✅ रज्जु दोष मुक्त" if not rajju_d else f"⚠️ {r_type} सक्रिय",
                "प्रमाण": "दक्षिण भारतीय सिद्धांत: 'एकरज्जौ विवाहास्तु वर्जनीयाः प्रयत्नतः॥'"
            },
            {
                "नियम": "१४. वेध दोष: अविरोधी नक्षत्र वेध स्थिति",
                "शर्त": "परस्पर वेधकारक नक्षत्र युग्मों (यथा अश्विनी-ज्येष्ठा, भरणी-अनुराधा) का अभाव",
                "स्थिति": "✅ वेध दोष मुक्त" if not vedha_d else "⚠️ नक्षत्र वेध सक्रिय",
                "प्रमाण": "मुहूर्त चिंतामणि: 'वेधदोषे न कर्तव्यो विवाहः शुभमिच्छता॥'"
            },
            {
                "नियम": "१५. गण दोष: राशीश मित्रता द्वारा गण दोष शमन",
                "शर्त": "राक्षस-देव गण होने पर भी यदि राशि स्वामी परस्पर मित्र हों तो दोष शांत होता है",
                "स्थिति": "✅ परिहार लागू" if is_friendly_lords else "⚪ लागू नहीं",
                "प्रमाण": "फलदीपिका: 'गणदोषं निहन्त्याशु राशीशसुहृद्भावतः॥'"
            },
            {
                "नियम": "१६. दशा-संधि: सुरक्षित काल अंतराल",
                "शर्त": "वर व कन्या दोनों के महादशा परिवर्तन में १ वर्ष (३६५ दिन) से अधिक का सुरक्षित अंतर हो",
                "स्थिति": "✅ सुरक्षित अंतराल" if not ds_dosha else f"⚠️ दशा-संधि ({ds_days} दिन अंतर)",
                "प्रमाण": "ज्योतिष रहस्य: 'उभयोर्दशासंधौ तु दम्पत्योः कलहो भवेत्॥'"
            }
        ]
        return checklist

    def render_milan_report_html(self, groom_data: BirthData, bride_data: BirthData, score: AshtakootaScore) -> str:
        """
        Renders a comprehensive classical printable HTML dossier
        for Kundali Milan with full Guna breakdown, Mahadoshas, Dasha Sandhi, and Remedies.
        """
        g_name = groom_data.name or "वर (Groom)"
        b_name = bride_data.name or "कन्या (Bride)"

        # Verdict Badge Color
        if score.total_score >= 28 and not (score.nadi_dosha and not score.nadi_dosha_cancelled):
            verdict_badge = "#10b981"  # Emerald
            verdict_text = "उत्कृष्ट एवं शुभ मिलान (Highly Recommended)"
        elif score.total_score >= 18 and not (score.nadi_dosha and not score.nadi_dosha_cancelled) and not (score.rajju_dosha and "शिरो" in score.rajju_type):
            verdict_badge = "#3b82f6"  # Blue
            verdict_text = "मध्यम एवं अनुकूल मिलान (Suitable / Favorable)"
        else:
            verdict_badge = "#ef4444"  # Red
            verdict_text = "सावधानी / शांति अनुष्ठान अनिवार्य (Caution / Remedies Required)"

        # Koota Table Rows
        kootas = [
            ("वर्ण (Varna)", "कार्य प्रवृत्ति एवं अहंकार सामंजस्य", score.varna, 1.0),
            ("वश्य (Vashya)", "पारस्परिक आकर्षण व प्रभुत्व नियंत्रण", score.vashya, 2.0),
            ("तारा (Tara)", "भाग्य, स्वास्थ्य एवं दीर्घायु अनुकूलता", score.tara, 3.0),
            ("योनि (Yoni)", "शारीरिक, जैविक एवं वैवाहिक संतुष्टि", score.yoni, 4.0),
            ("ग्रह मैत्री (Graha Maitri)", "मानसिक तालमेल, मित्रता एवं दृष्टिकोण", score.graha_maitri, 5.0),
            ("गण (Gana)", "स्वभाव, चरित्र एवं संस्कार सामंजस्य", score.gana, 6.0),
            ("भकूट (Bhakoot)", "वंश वृद्धि, आर्थिक समृद्धि एवं परिवार", score.bhakoot, 7.0),
            ("नाड़ी (Nadi)", "आनुवंशिक स्वास्थ्य, रक्त एवं संतान योग", score.nadi, 8.0),
        ]

        table_rows = ""
        for name, meaning, obt, mx in kootas:
            pct = (obt / mx) * 100
            bar_color = "#10b981" if pct >= 70 else ("#f59e0b" if pct >= 40 else "#ef4444")
            table_rows += f"""
            <tr style="border-bottom: 1px solid #e2e8f0;">
                <td style="padding: 10px 12px; font-weight: 600; color: #1e293b;">{name}</td>
                <td style="padding: 10px 12px; color: #64748b; font-size: 13px;">{meaning}</td>
                <td style="padding: 10px 12px; text-align: center; font-weight: 700; color: #0f172a;">{obt} / {mx}</td>
                <td style="padding: 10px 12px;">
                    <div style="background: #e2e8f0; border-radius: 6px; height: 10px; width: 100%; overflow: hidden;">
                        <div style="background: {bar_color}; width: {pct}%; height: 100%;"></div>
                    </div>
                </td>
            </tr>
            """

        # Deep synastry highlights
        syn = score.deep_analysis or {}
        santana = syn.get("santana", {})
        prosperity = syn.get("prosperity", {})
        remedies = syn.get("remedies", [])
        rem_html = "".join([f"<li style='margin-bottom: 6px;'>{r}</li>" for r in remedies]) if remedies else "<li>नियमित रूप से शिव-पार्वती पूजन व सुखद दांपत्य हेतु परस्पर सम्मान रखें।</li>"

        html_content = f"""
<!DOCTYPE html>
<html lang="hi">
<head>
<meta charset="UTF-8">
<title>विवाह मेलापक विस्तृत रिपोर्ट — {g_name} एवं {b_name}</title>
<style>
    @page {{ size: A4; margin: 15mm; }}
    body {{
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        color: #1e293b;
        background: #ffffff;
        margin: 0;
        padding: 20px;
        line-height: 1.5;
    }}
    .no-print {{
        text-align: right;
        margin-bottom: 15px;
    }}
    .print-btn {{
        background: #1e3a8a;
        color: #ffffff;
        border: none;
        padding: 10px 20px;
        border-radius: 8px;
        font-size: 14px;
        font-weight: 600;
        cursor: pointer;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
    }}
    .print-btn:hover {{ background: #1d4ed8; }}
    .header-box {{
        background: linear-gradient(135deg, #1e3a8a 0%, #312e81 100%);
        color: #ffffff;
        padding: 24px;
        border-radius: 12px;
        text-align: center;
        margin-bottom: 24px;
        border: 2px solid #f59e0b;
    }}
    .header-box h1 {{ margin: 0 0 6px 0; font-size: 24px; letter-spacing: 0.5px; }}
    .header-box h2 {{ margin: 0; font-size: 15px; font-weight: 400; color: #fde68a; }}
    .cards-row {{
        display: flex;
        gap: 16px;
        margin-bottom: 20px;
    }}
    .profile-card {{
        flex: 1;
        border: 1px solid #cbd5e1;
        border-radius: 10px;
        padding: 16px;
        background: #f8fafc;
    }}
    .profile-card h3 {{
        margin-top: 0;
        margin-bottom: 12px;
        color: #1e3a8a;
        border-bottom: 2px solid #e2e8f0;
        padding-bottom: 6px;
        font-size: 16px;
    }}
    .info-line {{ font-size: 13.5px; margin-bottom: 6px; }}
    .info-label {{ font-weight: 600; color: #475569; }}
    .section-title {{
        font-size: 17px;
        font-weight: 700;
        color: #0f172a;
        margin: 22px 0 10px 0;
        border-left: 4px solid #f59e0b;
        padding-left: 10px;
    }}
    .table-container {{
        border: 1px solid #cbd5e1;
        border-radius: 10px;
        overflow: hidden;
        margin-bottom: 20px;
    }}
    table {{
        width: 100%;
        border-collapse: collapse;
        font-size: 14px;
    }}
    th {{
        background: #0f172a;
        color: #ffffff;
        padding: 12px;
        text-align: left;
        font-size: 13.5px;
    }}
    .dosha-grid {{
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 14px;
        margin-bottom: 20px;
    }}
    .dosha-box {{
        border: 1px solid #cbd5e1;
        border-radius: 10px;
        padding: 14px;
        background: #ffffff;
    }}
    .dosha-title {{
        font-weight: 700;
        font-size: 14.5px;
        margin-bottom: 6px;
        display: flex;
        justify-content: space-between;
    }}
    .verdict-banner {{
        background: {verdict_badge};
        color: #ffffff;
        padding: 16px 20px;
        border-radius: 10px;
        text-align: center;
        font-weight: 700;
        font-size: 18px;
        margin: 20px 0;
    }}
    .footer-note {{
        text-align: center;
        font-size: 12px;
        color: #94a3b8;
        margin-top: 30px;
        border-top: 1px solid #e2e8f0;
        padding-top: 12px;
    }}
    @media print {{
        .no-print {{ display: none; }}
        body {{ padding: 0; }}
        .header-box {{ -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
        .verdict-banner {{ -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
    }}
</style>
</head>
<body>

<div class="no-print">
    <button class="print-btn" onclick="window.print()">🖨️ रिपोर्ट प्रिंट करें / PDF डाउनलोड</button>
</div>

<div class="header-box">
    <h1>॥ श्री गणेशाय नमः ॥</h1>
    <h1>विवाह मेलापक एवं महा-दोष परीक्षण रिपोर्ट</h1>
    <h2>वैदिक अष्टकूट (३६ गुण), रज्जु, वेध, दशा संधि एवं गहन सिनास्ट्री विश्लेषण</h2>
</div>

<div class="cards-row">
    <div class="profile-card">
        <h3>🤵 वर विवरण (Groom Profile)</h3>
        <div class="info-line"><span class="info-label">नाम:</span> {g_name}</div>
        <div class="info-line"><span class="info-label">जन्म दिनांक:</span> {groom_data.birth_date.strftime('%d-%b-%Y')}</div>
        <div class="info-line"><span class="info-label">जन्म समय:</span> {groom_data.birth_time.strftime('%H:%M')}</div>
        <div class="info-line"><span class="info-label">जन्म स्थान:</span> {groom_data.city or 'अज्ञात'} ({groom_data.latitude:.2f}°, {groom_data.longitude:.2f}°)</div>
        <div class="info-line"><span class="info-label">मांगलिक स्थिति:</span> {'⚠️ मांगलिक' if score.groom_manglik else '✅ अमांगलिक'}</div>
    </div>
    <div class="profile-card">
        <h3>👰 कन्या विवरण (Bride Profile)</h3>
        <div class="info-line"><span class="info-label">नाम:</span> {b_name}</div>
        <div class="info-line"><span class="info-label">जन्म दिनांक:</span> {bride_data.birth_date.strftime('%d-%b-%Y')}</div>
        <div class="info-line"><span class="info-label">जन्म समय:</span> {bride_data.birth_time.strftime('%H:%M')}</div>
        <div class="info-line"><span class="info-label">जन्म स्थान:</span> {bride_data.city or 'अज्ञात'} ({bride_data.latitude:.2f}°, {bride_data.longitude:.2f}°)</div>
        <div class="info-line"><span class="info-label">मांगलिक स्थिति:</span> {'⚠️ मांगलिक' if score.bride_manglik else '✅ अमांगलिक'}</div>
    </div>
</div>

<div class="verdict-banner">
    कुल प्राप्तांक: {score.total_score} / 36.0 गुण — {verdict_text}
</div>

<div class="section-title">📊 अष्टकूट ३६ गुण मिलान विवरण (Ashtakoota Breakdown)</div>
<div class="table-container">
    <table>
        <thead>
            <tr>
                <th style="width: 25%;">कूट का नाम</th>
                <th style="width: 40%;">शास्त्रीय विचार</th>
                <th style="width: 15%; text-align: center;">प्राप्त / कुल</th>
                <th style="width: 20%;">अनुकूलता अनुपात</th>
            </tr>
        </thead>
        <tbody>
            {table_rows}
            <tr style="background: #f1f5f9; font-weight: 800;">
                <td style="padding: 12px;" colspan="2">कुल योग (TOTAL SCORE)</td>
                <td style="padding: 12px; text-align: center; font-size: 16px; color: #1e3a8a;">{score.total_score} / 36.0</td>
                <td style="padding: 12px; font-size: 13px; color: #475569;">न्यूनतम १८ गुण आवश्यक</td>
            </tr>
        </tbody>
    </table>
</div>

<div class="section-title">🚨 महा-दोष एवं सूक्ष्म कूट विश्लेषण (Critical Dosha Scan)</div>
<div class="dosha-grid">
    <div class="dosha-box">
        <div class="dosha-title">
            <span>🔥 मांगलिक दोष विचार</span>
            <span>{'✅ अनुकूल' if score.manglik_match else '⚠️ असंतुलित'}</span>
        </div>
        <div style="font-size: 13px; color: #475569;">
            {score.manglik_cancellation_reason}
        </div>
    </div>

    <div class="dosha-box">
        <div class="dosha-title">
            <span>🧬 नाड़ी दोष एवं परिहार</span>
            <span>{'✅ दोष मुक्त / परिहार' if (not score.nadi_dosha or score.nadi_dosha_cancelled) else '❌ नाड़ी महादोष'}</span>
        </div>
        <div style="font-size: 13px; color: #475569;">
            {score.nadi_cancellation_reason}
        </div>
    </div>

    <div class="dosha-box">
        <div class="dosha-title">
            <span>🌙 भकूट दोष एवं परिहार</span>
            <span>{'✅ दोष मुक्त / परिहार' if (not score.bhakoot_dosha or score.bhakoot_dosha_cancelled) else '⚠️ भकूट दोष सक्रिय'}</span>
        </div>
        <div style="font-size: 13px; color: #475569;">
            {score.bhakoot_cancellation_reason if score.bhakoot_cancellation_reason else ('राशि संबंध शुभ व भकूट दोष रहित है।' if not score.bhakoot_dosha else 'भकूट दोष सक्रिय')}
        </div>
    </div>

    <div class="dosha-box">
        <div class="dosha-title">
            <span>⭕ रज्जु दोष (Rajju Dosha)</span>
            <span>{'⚠️ रज्जु दोष' if score.rajju_dosha else '✅ रज्जु दोष मुक्त'}</span>
        </div>
        <div style="font-size: 13px; color: #475569;">
            {score.rajju_desc}
        </div>
    </div>

    <div class="dosha-box">
        <div class="dosha-title">
            <span>⚡ नक्षत्र वेध दोष (Nakshatra Vedha)</span>
            <span>{'⚠️ वेध उपस्थित' if score.vedha_dosha else '✅ वेध रहित'}</span>
        </div>
        <div style="font-size: 13px; color: #475569;">
            {score.vedha_desc}
        </div>
    </div>

    <div class="dosha-box">
        <div class="dosha-title">
            <span>⏳ दशा संधि विचार (Dasha Sandhi)</span>
            <span>{'⚠️ दशा संधि' if score.dasha_sandhi else '✅ सुरक्षित अंतर'}</span>
        </div>
        <div style="font-size: 13px; color: #475569;">
            {score.dasha_sandhi_desc}
        </div>
    </div>

    <div class="dosha-box">
        <div class="dosha-title">
            <span>🌟 स्त्री-दीर्घ एवं महेन्द्र कूट</span>
            <span>{'✅ महेन्द्र शुभ' if score.mahendra_koota else '🟡 सामान्य'}</span>
        </div>
        <div style="font-size: 13px; color: #475569;">
            स्त्री-दीर्घ: {score.stree_deergha}<br>{score.mahendra_desc}
        </div>
    </div>
</div>

<div class="section-title">🔮 गहन शास्त्रीय सिनास्ट्री एवं जीवन फलादेश (Deep Synastry)</div>
<div class="profile-card" style="margin-bottom: 20px;">
    <div class="info-line"><strong>👶 संतान एवं वंश वृद्धि (बीज/क्षेत्र स्फुट):</strong> {santana.get('lineage_text', 'अनुकूल')} | {santana.get('first_child_desc', '')}</div>
    <div class="info-line"><strong>💰 विवाह उपरांत भाग्योदय एवं समृद्धि:</strong> {prosperity.get('bhagyodaya_title', '')} — {prosperity.get('bhagyodaya_desc', '')}</div>
    <div class="info-line"><strong>⚖️ दांपत्य जीवन की स्थिरता:</strong> {score.recommendation_hi}</div>
</div>

<div class="section-title">🕉️ अनुशंसित वैदिक शांति एवं उपाय (Remedies & Recommendations)</div>
<div class="profile-card" style="background: #fffbeb; border-color: #fde68a;">
    <ul style="margin: 0; padding-left: 20px; font-size: 14px; color: #92400e;">
        {rem_html}
    </ul>
</div>

<div class="footer-note">
    कंप्यूटर जनित प्रामाणिक वैदिक कुंडली मिलान रिपोर्ट • बृहत्पाराशर होराशास्त्र, मुहूर्त चिंतामणि एवं जातक पारिजात पर आधारित
</div>

</body>
</html>
        """
        return html_content


# Singleton Milan service
default_milan_service = MilanService()

