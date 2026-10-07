"""
Ghatna Query (Event Window Analysis) Service for JyotishOS.
Orchestrates:
1. Natal Baseline Chart & Divisional Charts
2. Ashtakavarga Calculations
3. Active Vimshottari Dasha Hierarchy at Target Date
4. Planetary Transits & Gochar Triggers
5. 3-Tier Classical Trigger System:
   - Tier 1: Vimshottari Dasha Connection to Event Houses & Lords (0-40)
   - Tier 2: Double Transit (Jupiter & Saturn) on Event Houses & Lords (0-35)
   - Tier 3: Ashtakavarga BAV/SAV Strength & Protection (0-25)
6. 12-24 Month Horizon Probability Scanner with Golden Window Detection
7. 32-Rule Evaluation Engine & Multi-System Consensus
8. Structured Evidence Packaging
"""

from datetime import date, datetime, timedelta
from typing import Optional, Dict, List, Any, Tuple

from ..core.models import (
    BirthData, GhatnaQueryInput, GhatnaQueryResult, KundaliChart, TransitSummary
)
from ..core.calculator import default_chart_calculator
from ..core.varga import VargaCalculator
from ..core.ashtakavarga import AshtakavargaCalculator
from ..core.gochar import default_transit_engine
from ..dasha.vimshottari import default_dasha_engine
from ..rules.engine import default_rules_engine
from ..rules.consensus import ConsensusAggregator
from ..core.constants import SIGN_NAMES, SIGN_LORDS


DISCLAIMER_TEXT_HI = (
    "वैधानिक एवं नैतिक सूचना: ज्योतिष एक पारम्परिक विद्या और सांस्कृतिक मार्गदर्शक है। "
    "यह गणना गणितीय ग्रहीय स्थिति एवं शास्त्रीय ग्रन्थों के नियमों पर आधारित है। "
    "इसे किसी भी प्रकार की चिकित्सीय (medical), विधिक (legal), या वित्तीय निवेश की निश्चित भविष्यवाणी न समझें। "
    "अंतिम निर्णय अपने विवेक और योग्य विशेषज्ञों के परामर्श से ही लें।"
)

DISCLAIMER_TEXT_EN = (
    "Disclaimer: Vedic Astrology is a traditional interpretive system for reflection and planning. "
    "Calculations are strictly derived from astronomical ephemeris and classical Sanskrit treatises. "
    "This does not constitute medical, legal, or financial advice."
)

# -------------------------------------------------------------------------
# Classical Theme House, Karaka & Shastric Significators
# -------------------------------------------------------------------------
THEME_SIGNIFICATORS: Dict[str, Dict[str, Any]] = {
    "marriage": {
        "name_hi": "विवाह एवं वैवाहिक संबंध (Marriage)",
        "prime_house": 7,
        "houses": [7, 2, 11],
        "karakas": ["Venus", "Jupiter"],
        "shastra_quote": "सप्तमे दारसंस्थानं द्वितीये कुलवर्धनम्। एकादशे लाभसिद्धिश्च त्रिकोणेषु च मङ्गलम्॥",
        "description_hi": "सप्तम भाव (जीवनसाथी), द्वितीय भाव (कुटुम्ब वृद्धि) एवं एकादश भाव (मनोरथ सिद्धि व पाणिग्रहण) का दशा व दोहरे गोचर से संबंध।"
    },
    "career": {
        "name_hi": "आजीविका / नौकरी / पदोन्नति (Career)",
        "prime_house": 10,
        "houses": [10, 6, 11, 1],
        "karakas": ["Sun", "Saturn", "Mercury", "Mars"],
        "shastra_quote": "दशमे मानमुद्योगं षष्ठे सेवाजयं तथा। एकादशे सर्वलाभं च कर्मेशबलसंयुतम्॥",
        "description_hi": "दशम भाव (कर्म, प्रतिष्ठा), षष्ठ भाव (प्रतियोगिता विजय, सेवा), एकादश भाव (आय वृद्धि) एवं लग्न (स्वाभिमान) का संयुक्त संरेखण।"
    },
    "wealth": {
        "name_hi": "धन / संचित वैभव / समृद्धि (Wealth)",
        "prime_house": 2,
        "houses": [2, 11, 9, 5],
        "karakas": ["Jupiter", "Venus", "Mercury"],
        "shastra_quote": "द्वितीये वित्तकोशं च लाभे वृद्धिं निरन्तरम्। धनेशलाभेशयोगेन धनयोगः प्रजायते॥",
        "description_hi": "द्वितीय भाव (कोश), एकादश भाव (आय), नवम व पंचम भाव (लक्ष्मी स्थान) के स्वामियों का परस्पर संबंध एवं अष्टकवर्ग समृद्धि।"
    },
    "children": {
        "name_hi": "संतान प्राप्ति / विद्या (Children)",
        "prime_house": 5,
        "houses": [5, 9, 2, 11],
        "karakas": ["Jupiter"],
        "shastra_quote": "पञ्चमे पुत्रसंस्थानं नवमे पूर्वपुण्यकम्। गुरुदृष्टियुते भावे सन्ततेः सुखमुत्तमम्॥",
        "description_hi": "पंचम भाव (संतति, विद्या), नवम भाव (पूर्वपुण्य) एवं देवगुरु बृहस्पति की अमृतमयी दृष्टि का संयुक्त फलादेश।"
    },
    "child": {
        "name_hi": "संतान प्राप्ति (Children)",
        "prime_house": 5,
        "houses": [5, 9, 2, 11],
        "karakas": ["Jupiter"],
        "shastra_quote": "पञ्चमे पुत्रसंस्थानं नवमे पूर्वपुण्यकम्। गुरुदृष्टियुते भावे सन्ततेः सुखमुत्तमम्॥",
        "description_hi": "पंचम भाव (संतति), नवम भाव (पूर्वपुण्य) एवं गुरु का पंचम भाव या पंचमेश पर दोहरा गोचर।"
    },
    "property": {
        "name_hi": "भूमि / भवन / वाहन क्रय (Property)",
        "prime_house": 4,
        "houses": [4, 11, 2],
        "karakas": ["Mars", "Venus", "Saturn"],
        "shastra_quote": "चतुर्थे गृहयानं च क्षेत्रं भूमिसुखं तथा। भौमे बलयुते सौम्ये गृहलाभः प्रजायते॥",
        "description_hi": "चतुर्थ भाव (सुख, भवन, वाहन), मंगल (भूमि कारक) एवं शुक्र (वाहन कारक) का शुभ दशा-गोचर संयोग।"
    },
    "travel": {
        "name_hi": "विदेश गमन / दूरस्थ यात्रा (Travel)",
        "prime_house": 12,
        "houses": [9, 12, 3, 7],
        "karakas": ["Moon", "Rahu", "Jupiter"],
        "shastra_quote": "द्वादशे दूरदेशं च नवमे तीर्थयात्रिकम्। तृतीये लघुयात्रा च वायुराशी गते शशाङ्के॥",
        "description_hi": "द्वादश भाव (विदेश वास), नवम भाव (दीर्घ यात्रा), तृतीय भाव (प्रवास) तथा चर राशियों में ग्रहों का गोचर।"
    },
    "health": {
        "name_hi": "स्वास्थ्य एवं दीर्घायु (Health)",
        "prime_house": 1,
        "houses": [1, 6, 8, 12],
        "karakas": ["Sun", "Moon", "Mars"],
        "shastra_quote": "लग्ने देहसुखं रूपमारोग्यं बलवर्धनम्। षष्ठाष्टमव्ययेशैस्तु अरोग्यं नाशयेत्तदा॥",
        "description_hi": "लग्न (देह, जीवनी शक्ति), षष्ठ भाव (रोग निवारण क्षमता) एवं अष्टकवर्ग में लग्न व सूर्य के शुभ बिन्दु।"
    },
    "spirituality": {
        "name_hi": "आध्यात्म एवं मोक्ष (Spirituality)",
        "prime_house": 9,
        "houses": [9, 12, 5, 8],
        "karakas": ["Jupiter", "Ketu", "Sun"],
        "shastra_quote": "नवमे धर्मसंस्थानं मोक्षं च द्वादशे स्थितम्। केतौ शुभयुते युक्ते कैवल्यपदमाप्नुयात्॥",
        "description_hi": "नवम भाव (धर्म), द्वादश भाव (मोक्ष), पंचम भाव (उपासना) तथा गुरु व केतु का आध्यात्मिक प्रभाव।"
    },
    "all": {
        "name_hi": "समग्र जीवन चक्र (Comprehensive)",
        "prime_house": 1,
        "houses": [1, 10, 7, 5, 2, 11],
        "karakas": ["Jupiter", "Sun", "Venus"],
        "shastra_quote": "सर्वेषां कर्मणां सिद्धिर्भाग्यदशाविशेषतः।",
        "description_hi": "लग्न, कर्म, भाग्य, सुख एवं लाभ भावों का समग्र बहु-आयामी समन्वय।"
    }
}


class EventQueryService:
    """Core Ghatna Query execution service."""

    def __init__(self):
        self.calculator = default_chart_calculator
        self.dasha_engine = default_dasha_engine
        self.transit_engine = default_transit_engine
        self.rules_engine = default_rules_engine

    def execute_query(
        self,
        query_input: GhatnaQueryInput,
        precomputed_chart: Optional[KundaliChart] = None
    ) -> GhatnaQueryResult:
        """Executes complete Event Window Analysis for a given profile and date."""
        # 1. Compute or use precomputed natal chart
        if precomputed_chart:
            chart = precomputed_chart
        else:
            chart = self.calculator.calculate_chart(query_input.birth_data)
            chart.vargas = VargaCalculator.calculate_all_vargas(chart)
            chart.ashtakavarga = AshtakavargaCalculator.calculate(chart)

        # 2. Compute active Vimshottari Dasha at target date
        full_birth_dt = datetime.combine(chart.birth_data.birth_date, chart.birth_data.birth_time)
        moon_lon = chart.planets["Moon"].longitude
        active_dasha = self.dasha_engine.get_active_dasha_at(
            full_birth_dt, moon_lon, query_input.target_date
        )

        # 3. Compute Transits (Gochar) at target date
        transits, transit_summary = self.transit_engine.compute_transit_snapshot(
            chart, query_input.target_date, chart.ayanamsa_name
        )

        # 4. Evaluate Rules Library (32 rules)
        evidences = self.rules_engine.evaluate_all(
            chart, active_dasha, transits, transit_summary, filter_theme=query_input.theme
        )

        # 5. Consensus Aggregation
        composite_score, confidence_band, consensus_ratio, top_pos, top_neg = (
            ConsensusAggregator.aggregate(evidences)
        )

        # 6. Generate Deterministic Structured Narrative
        narrative_hi, narrative_en = self._generate_narrative(
            query_input, active_dasha, transit_summary, composite_score, top_pos, top_neg
        )

        return GhatnaQueryResult(
            target_date=query_input.target_date,
            target_end_date=query_input.target_end_date,
            theme=query_input.theme,
            composite_score=composite_score,
            confidence_band=confidence_band,
            consensus_ratio=consensus_ratio,
            active_dasha=active_dasha,
            transit_summary=transit_summary,
            top_positive_signals=top_pos,
            top_negative_signals=top_neg,
            all_evaluated_rules=evidences,
            narrative_hi=narrative_hi,
            narrative_en=narrative_en,
            disclaimer=DISCLAIMER_TEXT_HI,
        )

    # -------------------------------------------------------------------------
    # 3-Tier Classical Trigger System
    # -------------------------------------------------------------------------
    def evaluate_3tier_triggers(
        self,
        chart: KundaliChart,
        theme: str,
        target_date: date
    ) -> Dict[str, Any]:
        """
        Calculates the classical 3-Tier Trigger System for a specific life event theme and date:
        - Tier 1: Vimshottari Dasha Hierarchy (MD, AD, PD) connection to theme houses & lords (0-40 pts).
        - Tier 2: Double Transit (Saturn & Jupiter) aspect/conjunction on target houses & lords (0-35 pts).
        - Tier 3: Ashtakavarga BAV/SAV support & protection (0-25 pts).
        Total Composite Probability: 0 to 100%.
        """
        theme_key = theme.lower()
        theme_info = THEME_SIGNIFICATORS.get(theme_key, THEME_SIGNIFICATORS["all"])
        prime_h = theme_info["prime_house"]
        target_houses = theme_info["houses"]
        karakas = theme_info["karakas"]

        lagna_sign_id = chart.lagna_sign_id

        # Map each house to its sign and lord
        house_lords = {}
        for h in range(1, 13):
            s_id = ((lagna_sign_id - 1 + (h - 1)) % 12) + 1
            s_name = SIGN_NAMES[s_id - 1]
            house_lords[h] = SIGN_LORDS[s_name]

        prime_lord = house_lords.get(prime_h, "Sun")
        prime_lord_house = chart.planets[prime_lord].house_from_lagna if prime_lord in chart.planets else 1

        # -------------------------------------------------------------
        # TIER 1: VIMSHOTTARI DASHA HIERARCHY (0 - 40 Points)
        # -------------------------------------------------------------
        full_birth_dt = datetime.combine(chart.birth_data.birth_date, chart.birth_data.birth_time)
        moon_lon = chart.planets["Moon"].longitude
        active_dasha = self.dasha_engine.get_active_dasha_at(full_birth_dt, moon_lon, target_date)

        md = active_dasha.mahadasha.lord
        ad = active_dasha.antardasha.lord
        pd = active_dasha.pratyantardasha.lord if getattr(active_dasha, "pratyantardasha", None) else ad

        md_h = chart.planets[md].house_from_lagna if md in chart.planets else 1
        ad_h = chart.planets[ad].house_from_lagna if ad in chart.planets else 1
        pd_h = chart.planets[pd].house_from_lagna if pd in chart.planets else 1

        # Check if planet rules any of target houses
        def planet_rules_houses(p_name: str) -> List[int]:
            return [h for h, lord in house_lords.items() if lord == p_name and h in target_houses]

        md_rules = planet_rules_houses(md)
        ad_rules = planet_rules_houses(ad)
        pd_rules = planet_rules_houses(pd)

        tier1_pts = 0
        t1_reasons = []

        # Mahadasha Lord check
        if md_h == prime_h or prime_h in md_rules:
            tier1_pts += 15
            t1_reasons.append(f"महादशा स्वामी {md} प्रधान भाव {prime_h} से प्रत्यक्ष संबद्ध")
        elif md_h in target_houses or len(md_rules) > 0:
            tier1_pts += 10
            t1_reasons.append(f"महादशा स्वामी {md} संबंधित भावों से संबद्ध")
        else:
            tier1_pts += 4

        # Antardasha Lord check (crucial timing trigger)
        if ad_h == prime_h or prime_h in ad_rules:
            tier1_pts += 15
            t1_reasons.append(f"अन्तर्दशा स्वामी {ad} प्रधान भाव {prime_h} से प्रत्यक्ष संबद्ध")
        elif ad_h in target_houses or len(ad_rules) > 0:
            tier1_pts += 11
            t1_reasons.append(f"अन्तर्दशा स्वामी {ad} संबंधित भावों से अनुकूल")
        else:
            tier1_pts += 4

        # Pratyantardasha Lord check
        if pd_h in target_houses or len(pd_rules) > 0:
            tier1_pts += 6
            t1_reasons.append(f"प्रत्यन्तर दशा स्वामी {pd} कार्य सिद्धि पोषक")
        else:
            tier1_pts += 2

        # Karaka Involvement
        if md in karakas or ad in karakas or pd in karakas:
            tier1_pts += 4
            t1_reasons.append(f"नैसर्गिक कारक ({', '.join(k for k in [md, ad, pd] if k in karakas)}) दशा चक्र में सक्रिय")

        tier1_pts = min(40, tier1_pts)

        # -------------------------------------------------------------
        # TIER 2: DOUBLE TRANSIT (SATURN & JUPITER) (0 - 35 Points)
        # -------------------------------------------------------------
        transits, _ = self.transit_engine.compute_transit_snapshot(chart, target_date, chart.ayanamsa_name)

        sat_h = transits["Saturn"]["house_from_lagna"]
        jup_h = transits["Jupiter"]["house_from_lagna"]

        # Saturn aspects: occupies (1st), 3rd, 7th, 10th
        sat_aspects = {
            sat_h,
            ((sat_h - 1 + 2) % 12) + 1,
            ((sat_h - 1 + 6) % 12) + 1,
            ((sat_h - 1 + 9) % 12) + 1,
        }
        # Jupiter aspects: occupies (1st), 5th, 7th, 9th
        jup_aspects = {
            jup_h,
            ((jup_h - 1 + 4) % 12) + 1,
            ((jup_h - 1 + 6) % 12) + 1,
            ((jup_h - 1 + 8) % 12) + 1,
        }

        sat_touches_prime = (prime_h in sat_aspects)
        jup_touches_prime = (prime_h in jup_aspects)
        sat_touches_lord = (prime_lord_house in sat_aspects)
        jup_touches_lord = (prime_lord_house in jup_aspects)

        sat_touches_any = any(h in sat_aspects for h in target_houses)
        jup_touches_any = any(h in jup_aspects for h in target_houses)

        tier2_pts = 0
        t2_reasons = []
        is_double_transit_active = False

        if (sat_touches_prime or sat_touches_lord) and (jup_touches_prime or jup_touches_lord):
            is_double_transit_active = True
            tier2_pts = 35
            t2_reasons.append(f"पूर्ण दोहरा गोचर (Double Transit): शनि (भाव {sat_h}) एवं गुरु (भाव {jup_h}) दोनों का प्रधान भाव {prime_h} / भावेश {prime_lord} पर संयुक्त शास्त्रीय दृष्टि प्रभाव।")
        elif sat_touches_any and jup_touches_any:
            is_double_transit_active = True
            tier2_pts = 28
            t2_reasons.append(f"दोहरा गोचर सक्रिय: शनि एवं गुरु दोनों का विषयगत भावों ({target_houses}) पर संयुक्त प्रभाव।")
        elif jup_touches_prime or jup_touches_lord:
            tier2_pts = 18
            t2_reasons.append(f"देवगुरु बृहस्पति की अमृत दृष्टि प्रधान भाव {prime_h} / भावेश पर सक्रिय (एकल शुभ गोचर)।")
        elif sat_touches_prime or sat_touches_lord:
            tier2_pts = 14
            t2_reasons.append(f"कर्मफलदाता शनि का दृष्टि प्रभाव प्रधान भाव {prime_h} पर सक्रिय (कर्म परिपक्वता)।")
        elif sat_touches_any or jup_touches_any:
            tier2_pts = 10
            t2_reasons.append(f"शनि या गुरु में से एक का सहायक भावों पर गोचरीय प्रभाव।")
        else:
            tier2_pts = 5
            t2_reasons.append("इस अवधि में प्रधान भाव पर शनि-गुरु का प्रत्यक्ष गोचरीय संरेखण नहीं है।")

        # -------------------------------------------------------------
        # TIER 3: ASHTAKAVARGA BAV & SAV STRENGTH (0 - 25 Points)
        # -------------------------------------------------------------
        tier3_pts = 0
        t3_reasons = []

        sat_bav = transits["Saturn"].get("ashtakavarga_bindu", 0)
        jup_bav = transits["Jupiter"].get("ashtakavarga_bindu", 0)

        # Prime house SAV
        prime_sign_id = ((lagna_sign_id - 1 + (prime_h - 1)) % 12) + 1
        prime_sav = 28
        if chart.ashtakavarga and chart.ashtakavarga.sav:
            prime_sav = chart.ashtakavarga.sav[prime_sign_id - 1]

        # Jupiter BAV evaluation
        if jup_bav >= 4:
            tier3_pts += 10
            t3_reasons.append(f"गुरु का गोचर राशि में प्रचुर बल (BAV: {jup_bav} बिन्दु - शुभ)")
        else:
            tier3_pts += 4
            t3_reasons.append(f"गुरु BAV: {jup_bav} बिन्दु (मध्यम)")

        # Saturn BAV evaluation
        if sat_bav >= 4:
            tier3_pts += 8
            t3_reasons.append(f"शनि BAV: {sat_bav} बिन्दु (कवच सुदृढ़, बाधाओं का परिहार)")
        else:
            tier3_pts += 2
            t3_reasons.append(f"शनि BAV: {sat_bav} बिन्दु (कम बिन्दु, विलंब या परीक्षा की संभावना)")

        # Prime house SAV evaluation
        if prime_sav >= 28:
            tier3_pts += 7
            t3_reasons.append(f"प्रधान भाव राशि में सर्वाष्टकवर्ग सामर्थ्य (SAV: {prime_sav} बिन्दु - सशक्त आधार)")
        else:
            tier3_pts += 3
            t3_reasons.append(f"प्रधान भाव SAV: {prime_sav} बिन्दु (औसत)")

        tier3_pts = min(25, tier3_pts)

        # -------------------------------------------------------------
        # Composite Calculation & Probability Band
        # -------------------------------------------------------------
        composite_probability = tier1_pts + tier2_pts + tier3_pts

        if composite_probability >= 78:
            status_hi = "🌟 स्वर्ण अवसर काल (Peak Golden Window)"
            color = "#10B981"
            guidance_hi = "शास्त्रीय दृष्टि से यह घटना के फलीभूत होने का सर्वोत्कृष्ट कालखंड है। इस अवधि में किए गए संकल्प व प्रयास शीघ्र फलदायी होते हैं।"
        elif composite_probability >= 62:
            status_hi = "🟢 अनुकूल फलदायी काल (Favorable Opportunity)"
            color = "#3B82F6"
            guidance_hi = "दशा व गोचर का सकारात्मक सहयोग प्राप्त हो रहा है। सक्रिय प्रयास करने पर अभीष्ट सिद्धि के प्रबल योग हैं।"
        elif composite_probability >= 45:
            status_hi = "🟡 मध्यम / मिश्रित काल (Moderate Window)"
            color = "#F59E0B"
            guidance_hi = "कुछ अनुकूलता व कुछ विलंबकारी कारक साथ चल रहे हैं। धैर्यपूर्वक प्रयास जारी रखें।"
        else:
            status_hi = "🔴 प्रतीक्षा / साधना काल (Challenging / Delay Window)"
            color = "#EF4444"
            guidance_hi = "शास्त्रीय ट्रिगर्स अभी पूर्णतः परिपक्व नहीं हैं। इस समय धैर्य, तैयारी और अनुष्ठान/उपाय पर बल दें।"

        return {
            "target_date": target_date,
            "theme": theme_key,
            "theme_name_hi": theme_info["name_hi"],
            "prime_house": prime_h,
            "prime_lord": prime_lord,
            "composite_probability": composite_probability,
            "status_hi": status_hi,
            "status_color": color,
            "guidance_hi": guidance_hi,
            "shastra_quote": theme_info["shastra_quote"],
            "tier1": {
                "name": "विंशोत्तरी दशा संरेखण (Dasha Alignment)",
                "score": tier1_pts,
                "max": 40,
                "active_dasha": active_dasha.formatted_summary,
                "reasons": t1_reasons
            },
            "tier2": {
                "name": "दोहरा गोचर (Double Transit: Saturn & Jupiter)",
                "score": tier2_pts,
                "max": 35,
                "is_double_transit_active": is_double_transit_active,
                "saturn_house": sat_h,
                "jupiter_house": jup_h,
                "reasons": t2_reasons
            },
            "tier3": {
                "name": "अष्टकवर्ग एवं संरचनात्मक संपुष्टि (Ashtakavarga Strength)",
                "score": tier3_pts,
                "max": 25,
                "jupiter_bav": jup_bav,
                "saturn_bav": sat_bav,
                "prime_sav": prime_sav,
                "reasons": t3_reasons
            }
        }

    # -------------------------------------------------------------------------
    # 12 - 24 Months Horizon Range Scanner
    # -------------------------------------------------------------------------
    def scan_event_range(
        self,
        chart: KundaliChart,
        theme: str,
        start_date: date,
        months_count: int = 12
    ) -> Dict[str, Any]:
        """
        Scans a monthly time horizon (e.g. 12 or 24 months) starting from start_date.
        Returns month-by-month probability scores, peak golden window, and actionable guidance.
        """
        monthly_records = []
        peak_score = -1.0
        peak_record = None

        for m_idx in range(months_count):
            # Sample around 15th of each sequential month
            year = start_date.year + ((start_date.month - 1 + m_idx) // 12)
            month = ((start_date.month - 1 + m_idx) % 12) + 1
            sample_date = date(year, month, 15)

            eval_res = self.evaluate_3tier_triggers(chart, theme, sample_date)
            month_label = sample_date.strftime("%b %Y")

            rec = {
                "month_idx": m_idx + 1,
                "month_label": month_label,
                "sample_date": sample_date,
                "score": eval_res["composite_probability"],
                "status_hi": eval_res["status_hi"],
                "status_color": eval_res["status_color"],
                "tier1_score": eval_res["tier1"]["score"],
                "tier2_score": eval_res["tier2"]["score"],
                "tier3_score": eval_res["tier3"]["score"],
                "active_dasha": eval_res["tier1"]["active_dasha"],
                "double_transit": eval_res["tier2"]["is_double_transit_active"],
                "guidance_hi": eval_res["guidance_hi"],
                "eval_detail": eval_res
            }
            monthly_records.append(rec)

            if rec["score"] > peak_score:
                peak_score = rec["score"]
                peak_record = rec

        # Detect Golden Window Range (consecutive high months)
        golden_months = [r["month_label"] for r in monthly_records if r["score"] >= 70]

        theme_info = THEME_SIGNIFICATORS.get(theme.lower(), THEME_SIGNIFICATORS["all"])

        return {
            "theme": theme,
            "theme_name_hi": theme_info["name_hi"],
            "shastra_quote": theme_info["shastra_quote"],
            "months_scanned": months_count,
            "start_date": start_date,
            "monthly_records": monthly_records,
            "peak_month": peak_record["month_label"] if peak_record else "",
            "peak_score": peak_score,
            "peak_record": peak_record,
            "golden_months": golden_months,
            "average_score": round(sum(r["score"] for r in monthly_records) / len(monthly_records), 1) if monthly_records else 0
        }

    def _generate_narrative(
        self,
        query_input: GhatnaQueryInput,
        dasha,
        transit: TransitSummary,
        score: float,
        top_pos,
        top_neg
    ) -> Tuple[str, str]:
        """Generates clear, transparent Hindi and English summaries based strictly on evidence."""
        d_summary = dasha.formatted_summary
        theme_title = query_input.theme.capitalize()

        # Hindi Narrative Construction
        hi_lines = [
            f"### घटना विश्लेषण सार (विषय: {theme_title} | दिनांक: {query_input.target_date.strftime('%d-%b-%Y')})",
            f"- **सक्रिय विंशोत्तरी दशा:** {d_summary}",
            f"- **समग्र सम्भावना सूचकांक (Composite Score):** {score:.2f} ({'अनुकूल अवसर' if score >= 0.60 else ('मिश्रित / सामान्य' if score >= 0.45 else 'सावधानी / धैर्य की आवश्यकता')})",
            "",
            "#### मुख्य सकारात्मक शास्त्रीय संकेत:",
        ]
        if top_pos:
            for s in top_pos:
                hi_lines.append(f"- **{s.rule_name_hi}** ({s.source_text}): {s.explanation_hi}")
        else:
            hi_lines.append("- इस विषय में कोई असाधारण सकारात्मक शास्त्रीय योग सक्रिय नहीं दिखा।")

        hi_lines.append("\n#### मुख्य अवरोधक / सावधानी संकेत:")
        if top_neg:
            for s in top_neg:
                hi_lines.append(f"- **{s.rule_name_hi}** ({s.source_text}): {s.explanation_hi}")
        else:
            hi_lines.append("- कोई बड़ा नकारात्मक दोष या अवरोध इस अवधि में सक्रिय नहीं है।")

        if transit.is_sade_sati:
            hi_lines.append(f"\n> **गोचर चेतावनी:** {transit.sade_sati_phase} सक्रिय है। कार्यक्षेत्र और पारिवारिक मामलों में अनुशासित रहने की सलाह है।")

        # English Narrative Construction
        en_lines = [
            f"### Event Analysis Summary (Theme: {theme_title} | Date: {query_input.target_date.strftime('%d-%b-%Y')})",
            f"- **Operating Vimshottari Dasha:** {d_summary}",
            f"- **Composite Probability Score:** {score:.2f}",
            "",
            "#### Key Supporting Classical Signals:",
        ]
        if top_pos:
            for s in top_pos:
                en_lines.append(f"- **{s.rule_name_en}** [{s.source_text}]: {s.explanation_hi}")
        else:
            en_lines.append("- No strong affirmative classical indicators active for this theme.")

        hi_lines.append("\n#### Key Mitigating / Restrictive Factors:")
        if top_neg:
            for s in top_neg:
                en_lines.append(f"- **{s.rule_name_en}** [{s.source_text}]: {s.explanation_hi}")
        else:
            en_lines.append("- No major obstructive afflictions active for this window.")

        return "\n".join(hi_lines), "\n".join(en_lines)


# Singleton event query service
default_event_query_service = EventQueryService()
