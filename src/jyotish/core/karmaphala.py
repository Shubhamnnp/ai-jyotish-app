"""
Karmaphala & Personality Engine (व्यक्तित्व एवं कर्मफल विश्लेषण) for JyotishOS.
Calculates authentic Shastriya evaluations for:
1. व्यापार बनाम नौकरी (Business vs Job / Service Aptitude)
2. पढ़ाई, मेधा एवं बौद्धिक क्षमता (Education, Intellect & Academic Hurdles)
3. नैतिक व्यवहार, सत्यनिष्ठा एवं गुण प्रवृत्तियां (Ethics, Moral Character & Guna Balance)
4. गलत लत, व्यसन एवं प्रलोभन संवेदनशीलता (Addictions, Vices & Vulnerability Assessment)
5. पैतृक संपत्ति, वसीयत एवं भूमि-भवन लाभ (Ancestral Property, Inheritance & Family Legacy)
6. आंतरिक सुख, मानसिक शांति एवं संतोष (Happiness, Mental Peace & Moon Afflictions)
7. पूर्वजन्म के कर्म, ऋणानुबंध एवं प्रारब्ध (Past Life Karma, Karmic Ledger & Soul Debts)

Rooted in Classical Vedic Astrology:
- Brihat Parashara Hora Shastra (BPHS: Karakatvas, Bhava Phala, Atmakaraka & Purva Punya)
- Phaladeepika (Mantreshwara: Adhyaya 15 & 16 Bhava Vichara, Planetary Yogas)
- Saravali (Kalyanavarma: Rajayogas, Arishta, and Moral Virtues)
- Jaimini Upadesha Sutras (Atmakaraka, Arudhas, and Soul Evolution)
- Uttara Kalamrita (Kalidasa: Detailed Significations of Houses & Grahas)
"""

from typing import Dict, List, Tuple, Optional, Any
from .constants import (
    SIGNS, SIGN_NAMES, SIGN_LORDS, GRAHAS,
    EXALTATION, DEBILITATION
)
from .models import KundaliChart, PlanetPosition, HouseCusp


class KarmaphalaEngine:
    """Rigorous Shastriya engine for Personality & Karmic Ledger analysis."""

    NATURAL_BENEFICS = {"Jupiter", "Venus", "Mercury", "Moon"}
    NATURAL_MALEFICS = {"Saturn", "Mars", "Rahu", "Ketu", "Sun"}

    # =========================================================================
    # 1. HELPER CALCULATIONS
    # =========================================================================

    @classmethod
    def _get_planet(cls, chart: KundaliChart, name: str) -> Optional[PlanetPosition]:
        return chart.planets.get(name)

    @classmethod
    def _get_house(cls, chart: KundaliChart, house_num: int) -> Optional[HouseCusp]:
        if 1 <= house_num <= len(chart.houses):
            return chart.houses[house_num - 1]
        return None

    @classmethod
    def _planet_strength_score(cls, p: Optional[PlanetPosition]) -> float:
        """Returns normalized score 0.0 to 1.0 based on dignity, retro, combustion."""
        if not p:
            return 0.5
        score = 0.5
        d = p.dignity.lower()
        if "exalt" in d:
            score = 1.0
        elif "moolatrikona" in d:
            score = 0.9
        elif "own" in d:
            score = 0.8
        elif "great_friend" in d:
            score = 0.7
        elif "friend" in d:
            score = 0.6
        elif "neutral" in d:
            score = 0.5
        elif "enemy" in d:
            score = 0.4
        elif "great_enemy" in d:
            score = 0.3
        elif "debil" in d:
            score = 0.15

        if p.is_combust:
            score *= 0.65
        if p.is_retrograde and p.name not in ("Rahu", "Ketu"):
            # Retrograde natural benefics become stronger; malefics can be erratic
            if p.name in ("Jupiter", "Venus", "Mercury"):
                score = min(1.0, score * 1.15)
            else:
                score *= 0.95
        return round(score, 2)

    @classmethod
    def _house_strength_score(cls, chart: KundaliChart, house_num: int) -> float:
        """Evaluates house strength using lord dignity, occupants, and aspects."""
        h = cls._get_house(chart, house_num)
        if not h:
            return 50.0

        score = 50.0
        lord_p = cls._get_planet(chart, h.lord)
        lord_str = cls._planet_strength_score(lord_p)
        score += (lord_str - 0.5) * 40.0  # Range -20 to +20

        # Occupants
        for occ in h.occupants:
            if occ in cls.NATURAL_BENEFICS:
                score += 8.0
            elif occ in ("Rahu", "Ketu", "Saturn", "Mars"):
                score -= 7.0
            elif occ == "Sun":
                # Sun gives authority in 10th/11th, but heat in 4th/7th
                score += 5.0 if house_num in (10, 11, 6, 3) else -4.0

        # Aspects
        for asp in h.aspecting_planets:
            if asp in cls.NATURAL_BENEFICS:
                score += 6.0
            elif asp in cls.NATURAL_MALEFICS:
                score -= 5.0

        # Ashtakavarga SAV bindus bonus if available
        if chart.ashtakavarga and chart.ashtakavarga.sav:
            sign_idx = h.sign_id - 1
            if 0 <= sign_idx < len(chart.ashtakavarga.sav):
                bindus = chart.ashtakavarga.sav[sign_idx]
                score += (bindus - 28) * 1.5  # 28 is average

        return max(5.0, min(98.0, round(score, 1)))

    # =========================================================================
    # 2. CAREER: BUSINESS VS JOB (व्यापार बनाम नौकरी)
    # =========================================================================

    @classmethod
    def analyze_career(cls, chart: KundaliChart) -> Dict[str, Any]:
        """Calculates authentic Business vs Job compatibility and sector suitability."""
        # 6th house = Service, competition, subordinate work (Job)
        # 7th house = Public trade, partnerships, commercial exchange (Business)
        # 10th house = Karma, status, executive power
        # 11th house = Gains, recurring profits
        # 3rd house = Enterprise, initiative, self-effort

        h6_score = cls._house_strength_score(chart, 6)
        h7_score = cls._house_strength_score(chart, 7)
        h10_score = cls._house_strength_score(chart, 10)
        h11_score = cls._house_strength_score(chart, 11)
        h3_score = cls._house_strength_score(chart, 3)

        mercury_str = cls._planet_strength_score(cls._get_planet(chart, "Mercury"))
        saturn_str = cls._planet_strength_score(cls._get_planet(chart, "Saturn"))
        sun_str = cls._planet_strength_score(cls._get_planet(chart, "Sun"))
        mars_str = cls._planet_strength_score(cls._get_planet(chart, "Mars"))
        jupiter_str = cls._planet_strength_score(cls._get_planet(chart, "Jupiter"))

        # Business Score: 7th (30%) + 11th (20%) + 3rd (15%) + 10th (15%) + Mercury (20%)
        raw_biz = (h7_score * 0.30) + (h11_score * 0.20) + (h3_score * 0.15) + (h10_score * 0.15) + (mercury_str * 100 * 0.20)
        
        # Job Score: 6th (35%) + 10th (25%) + Saturn (20%) + Sun (20%)
        raw_job = (h6_score * 0.35) + (h10_score * 0.25) + (saturn_str * 100 * 0.20) + (sun_str * 100 * 0.20)

        # Penalties/Bonuses
        h7 = cls._get_house(chart, 7)
        h6 = cls._get_house(chart, 6)
        h10 = cls._get_house(chart, 10)

        # If Rahu in 7th without Jupiter aspect -> Risk of fraud in partnership
        rahu_in_7 = "Rahu" in (h7.occupants if h7 else [])
        saturn_in_7 = "Saturn" in (h7.occupants if h7 else [])
        if rahu_in_7:
            raw_biz -= 6.0
        if saturn_in_7:
            raw_biz -= 4.0  # Delay, slow initial turnover

        # If Sun or Mars or Saturn in 6th -> Shatru Hanta & immense job competitive strength
        if any(p in ("Sun", "Mars", "Saturn") for p in (h6.occupants if h6 else [])):
            raw_job += 8.0

        business_score = int(max(15, min(95, round(raw_biz))))
        job_score = int(max(15, min(95, round(raw_job))))

        # Recommendation
        diff = business_score - job_score
        if diff >= 12:
            recommendation_hi = "स्वतंत्र व्यापार एवं उद्यम (Business / Self-Enterprise) सर्वथा अनुकूल"
            rec_tag = "व्यापार प्रधान (Business)"
            verdict_desc = "आपकी कुण्डली में ७वें (वाणिज्य), ११वें (लाभ) एवं ३रे (पराक्रम) भाव का प्रभाव ६ठे भाव (सेवा) से अधिक शक्तिशाली है। बुध एवं लाभेश की स्थिति स्वतंत्र निर्णय क्षमता और ग्राहक प्रबंधन में भारी सफलता का संकेत देती है।"
        elif diff <= -12:
            recommendation_hi = "नौकरी एवं प्रतिष्ठित सेवा (Corporate / Govt Job) अधिक सुरक्षित व फलदायी"
            rec_tag = "नौकरी प्रधान (Service / Job)"
            verdict_desc = "आपकी कुण्डली में ६ठे भाव (सेवा, प्रतियोगिता) एवं शनि/सूर्य का बल अधिक प्रभावी है। स्वतंत्र व्यापार में पूँजी फँसने या साझेदारों से विश्वासघात का जोखिम रहेगा, जबकि व्यवस्थित सेवा या कॉर्पोरेट/प्रशासनिक पद पर नियमित मान-सम्मान व स्थिरता प्राप्त होगी।"
        else:
            recommendation_hi = "मिश्रित आजीविका (प्रारंभिक नौकरी उपरांत व्यापार अथवा पेशेवर कंसल्टेंसी)"
            rec_tag = "मिश्रित (Job then Business / Consultancy)"
            verdict_desc = "आपकी कुण्डली में व्यापार और सेवा दोनों के कारक संतुलित हैं। जीवन के पूर्वार्ध में नौकरी द्वारा अनुभव एवं संचित पूँजी प्राप्त करना और उत्तरार्ध में स्वतंत्र कंसल्टेंसी या व्यापार में उतरना स्वर्णिम सिद्ध होगा।"

        # Risk Appetite
        if h3_score >= 65 and mars_str >= 0.65:
            risk_appetite = "उच्च जोखिम सहिष्णुता (High Risk Appetite - साहसिक निर्णय क्षमता)"
        elif h3_score <= 45 or saturn_str >= 0.75:
            risk_appetite = "सुरक्षात्मक एवं रूढ़िवादी (Conservative - सुरक्षित व सुनिश्चित लाभ पसंद)"
        else:
            risk_appetite = "संतुलित एवं नपा-तुला (Calculated Risk-Taker)"

        # 10th lord and sign element for sector determination
        sectors = []
        if h10:
            lord_10 = h10.lord
            # Check element of 10th sign
            sign_info = next((s for s in SIGNS if s["name_en"] == h10.sign_name), None)
            elem = sign_info["element"] if sign_info else "Earth"
            
            if elem == "Fire":
                sectors.extend(["प्रशासन, सिविल सेवा व रक्षा (Administration/Govt)", "ऊर्जा, धातु, खनिज व विनिर्माण (Energy/Industry)", "नेतृत्व, राजनीति व रियल एस्टेट प्रबंधन"])
            elif elem == "Earth":
                sectors.extend(["बैंकिंग, वित्त, सी.ए. व चार्टर्ड एकाउंटेंसी (Finance/CA)", "रियल एस्टेट, कृषि, निर्माण व आपूर्ति श्रृंखला (Logistics)", "व्यवस्थित कॉर्पोरेट संचालन व ऑडिटिंग"])
            elif elem == "Air":
                sectors.extend(["सूचना प्रौद्योगिकी, सॉफ्टवेयर व ए.आई. (IT & Artificial Intelligence)", "संचार, मीडिया, डिजिटल मार्केटिंग व ट्रेडिंग (Trading/Media)", "परामर्श, बौद्धिक संपदा व विदेश व्यापार"])
            elif elem == "Water":
                sectors.extend(["चिकित्सा, फार्मास्युटिकल व रसायन (Pharma & Healthcare)", "हॉस्पिटैलिटी, पर्यटन, खाद्य व पेय पदार्थ (F&B/Hotels)", "मनोविज्ञान, अनुसंधान, जल संसाधन व कला"])

        # Warnings
        warnings = []
        if rahu_in_7:
            warnings.append("⚠️ ७वें भाव में राहु: साझेदारों (Business Partners) पर अंधविश्वास से बचें। लिखित अनुबंध (Legal Contracts) के बिना कोई बड़ा निवेश न करें।")
        if saturn_in_7:
            warnings.append("⏳ ७वें भाव में शनि: व्यापारिक सफलता ३०-३२ वर्ष की आयु के बाद परिपक्वता से स्थापित होगी; धैर्य रखें।")
        if "Mars" in (h6.occupants if h6 else []) and "Rahu" in (h6.occupants if h6 else []):
            warnings.append("⚡ ६ठे भाव में अंगारक प्रभाव: कार्यस्थल पर वरिष्ठ अधिकारियों से अहंकार का टकराव न करें; गुप्त शत्रुओं से सजग रहें।")
        if not warnings:
            warnings.append("✅ कुण्डली में कार्यक्षेत्र को लेकर कोई गंभीर मारक या बाधक दोष नहीं है; निष्ठावान प्रयास फलदायी रहेंगे।")

        return {
            "business_score": business_score,
            "job_score": job_score,
            "recommendation_hi": recommendation_hi,
            "rec_tag": rec_tag,
            "verdict_desc": verdict_desc,
            "risk_appetite": risk_appetite,
            "sectors": sectors[:3],
            "warnings": warnings,
            "shastriya_basis": f"दशमेश '{h10.lord if h10 else 'N/A'}' का प्रभाव, षष्ठम भाव बल ({h6_score}%) बनाम सप्तम भाव बल ({h7_score}%), तथा बुध/शनि का नैसर्गिक कारकलक्षण।"
        }

    # =========================================================================
    # 3. EDUCATION & INTELLECT (शिक्षा, मेधा एवं बौद्धिक क्षमता)
    # =========================================================================

    @classmethod
    def analyze_education(cls, chart: KundaliChart) -> Dict[str, Any]:
        """Evaluates formal schooling (4th), higher intellect (5th), wisdom (9th) and Mercury/Jupiter."""
        h4_score = cls._house_strength_score(chart, 4)
        h5_score = cls._house_strength_score(chart, 5)
        h9_score = cls._house_strength_score(chart, 9)

        mercury_p = cls._get_planet(chart, "Mercury")
        jupiter_p = cls._get_planet(chart, "Jupiter")
        rahu_p = cls._get_planet(chart, "Rahu")

        mercury_str = cls._planet_strength_score(mercury_p)
        jupiter_str = cls._planet_strength_score(jupiter_p)

        # Composite score
        raw_edu = (h4_score * 0.25) + (h5_score * 0.35) + (h9_score * 0.15) + (mercury_str * 100 * 0.15) + (jupiter_str * 100 * 0.10)
        education_score = int(max(20, min(98, round(raw_edu))))

        # Intellect Type
        h5 = cls._get_house(chart, 5)
        occ_5 = h5.occupants if h5 else []
        if "Mercury" in occ_5 or (mercury_p and mercury_p.house_from_lagna in (1, 5, 9, 10)):
            intellect_type = "तार्किक, गणितीय एवं विश्लेषणात्मक (Logical, Analytical & Quick-Witted)"
            intellect_desc = "बुध की प्रबलता के कारण आपकी समझ अत्यंत तीव्र है। आंकड़ों, कोडिंग, गणनाओं और तर्कों को आप त्वरित गति से आत्मसात करते हैं।"
        elif "Jupiter" in occ_5 or (jupiter_p and jupiter_p.house_from_lagna in (1, 5, 9)):
            intellect_type = "गहन दार्शनिक, नीतिगत एवं अनुसंधानात्मक (Philosophical, Deep Comprehension & Wisdom)"
            intellect_desc = "गुरु के प्रभाव से आपकी बुद्धि सतही ज्ञान के स्थान पर सिद्धांतों की गहराई और नीतिगत विवेक को प्राथमिकता देती है।"
        elif "Mars" in occ_5 or "Sun" in occ_5:
            intellect_type = "क्रियाशील, तकनीकी एवं व्यावहारिक (Applied, Engineering & Problem-Solving)"
            intellect_desc = "अग्नि तत्वीय प्रभाव से आपकी मेधा सैद्धांतिक रटने के स्थान पर व्यावहारिक क्रियान्वयन, इंजीनियरिंग व समस्या समाधान में उत्कृष्ट है।"
        elif "Venus" in occ_5 or "Moon" in occ_5:
            intellect_type = "रचनात्मक, कलात्मक एवं नवोन्मेषी (Creative, Imaginative & Aesthetic)"
            intellect_desc = "चंद्र-शुक्र का प्रभाव कल्पनाशीलता, भाषा, डिजाइनिंग और नवाचार में असाधारण प्रतिभा प्रदान करता है।"
        else:
            intellect_type = "संतुलित एवं व्यावहारिक (Practical & Methodical)"
            intellect_desc = "आपकी मेधा व्यवस्थित अध्ययन, अनुशासन और नियमित पुनरावृत्ति से निरंतर निखरती है।"

        # Memory & Grasping Power
        if mercury_str >= 0.75 and jupiter_str >= 0.70:
            memory_power = "तीक्ष्ण एवं दीर्घकालिक (Photographic / Highly Retentive)"
        elif mercury_str <= 0.40 or (mercury_p and mercury_p.is_combust):
            memory_power = "परिश्रम साध्य (Needs Revision & Written Notes - कभी-कभी परीक्षा समय विस्मृति)"
        else:
            memory_power = "सक्रिय एवं उत्तम (Good Retention with Structured Study)"

        # Academic Hurdles & Breaks
        hurdles = []
        h4 = cls._get_house(chart, 4)
        h6 = cls._get_house(chart, 6)
        h9 = cls._get_house(chart, 9)
        h10 = cls._get_house(chart, 10)
        occ_4 = h4.occupants if h4 else []
        occ_6 = h6.occupants if h6 else []
        occ_10 = h10.occupants if h10 else []

        if "Rahu" in occ_4 or "Rahu" in occ_5:
            hurdles.append("⚡ राहु का प्रभाव: अध्ययन में मन का भटकना, स्क्रीन/इंटरनेट का अति-आकर्षण अथवा स्ट्रीम बदलने की प्रवृत्ति।")
        if "Saturn" in occ_4 or "Saturn" in occ_5:
            hurdles.append("⏳ शनि का प्रभाव: औपचारिक शिक्षा में विलंब, प्रारंभिक अंकों में अपेक्षा से कम परिणाम या एक बार रुकावट, परंतु बाद में ठोस ज्ञान।")
        if "Ketu" in occ_5:
            hurdles.append("🌀 केतु का प्रभाव: परंपरागत रटने वाली शिक्षा से विरक्ति; गूढ़, कोडिंग या आध्यात्मिक विषयों में ही विशेष रुचि।")
        if mercury_p and mercury_p.is_combust:
            hurdles.append("☀️ बुध अस्त: अत्यधिक दबाव में परीक्षा कक्ष में त्वरित निर्णय लेने में घबराहट; लिखित अभ्यास अनिवार्य है।")
        if not hurdles:
            hurdles.append("✅ शिक्षा भावों में कोई गंभीर पाप प्रभाव नहीं है; एकाग्रता निरंतर बनी रहने पर उच्च डिग्रियां सुगम रहेंगी।")

        # Best Streams
        streams = []
        if mercury_str >= 0.60 or "Mars" in occ_10 or (h10 and h10.lord in ("Mercury", "Mars", "Saturn")):
            streams.append("इंजीनियरिंग, कंप्यूटर साइंस, ए.आई. व डेटा एनालिटिक्स (STEM / Tech)")
        if jupiter_str >= 0.65 or (h9 and h9.lord in ("Jupiter", "Sun")):
            streams.append("विधि, न्यायपालिका, सिविल सर्विसेज व प्रबंधन (Law, Civil Services, MBA)")
        if "Sun" in occ_10 or "Sun" in occ_5 or (h5 and h5.lord == "Sun") or "Mars" in occ_6:
            streams.append("चिकित्सा, शल्यक्रिया, बायोटेक्नोलॉजी व फार्मेसी (Medicine / Biotech)")
        if "Venus" in occ_5 or (mercury_str >= 0.60 and jupiter_str >= 0.60):
            streams.append("चार्टर्ड एकाउंटेंसी, वित्तीय विश्लेषण, कॉर्पोरेट वित्त (CA, Finance, Economics)")
        if not streams:
            streams.append("वाणिज्य, प्रशासन, शिक्षण एवं परामर्श (Commerce & Administration)")

        return {
            "education_score": education_score,
            "intellect_type": intellect_type,
            "intellect_desc": intellect_desc,
            "memory_power": memory_power,
            "hurdles": hurdles,
            "recommended_streams": streams[:3],
            "shastriya_basis": f"चतुर्थ भाव (विद्या आधार: {h4_score}%), पंचम भाव (धी-शक्ति: {h5_score}%), नवम भाव (उच्च गुरु ज्ञान: {h9_score}%) एवं बुध-गुरु बल।"
        }

    # =========================================================================
    # 4. MORAL CHARACTER & INTEGRITY (नैतिक व्यवहार एवं सत्यनिष्ठा)
    # =========================================================================

    @classmethod
    def analyze_morals(cls, chart: KundaliChart) -> Dict[str, Any]:
        """Calculates Guna balance (Satva, Rajas, Tamas) and moral integrity."""
        # Satvic planets: Sun, Moon, Jupiter
        # Rajasic planets: Mercury, Venus
        # Tamasic planets: Mars, Saturn, Rahu, Ketu

        satva_pts = 0.0
        rajas_pts = 0.0
        tamas_pts = 0.0

        for p_name in ("Sun", "Moon", "Jupiter"):
            satva_pts += cls._planet_strength_score(cls._get_planet(chart, p_name)) * 1.3
        for p_name in ("Mercury", "Venus"):
            rajas_pts += cls._planet_strength_score(cls._get_planet(chart, p_name)) * 1.5
        for p_name in ("Mars", "Saturn", "Rahu", "Ketu"):
            tamas_pts += cls._planet_strength_score(cls._get_planet(chart, p_name)) * 1.0

        # Check Lagna & 9th house influences
        h1 = cls._get_house(chart, 1)
        h9 = cls._get_house(chart, 9)
        occ_1_9 = (h1.occupants if h1 else []) + (h9.occupants if h9 else [])
        for occ in occ_1_9:
            if occ in ("Jupiter", "Sun", "Moon"):
                satva_pts += 1.5
            elif occ in ("Mercury", "Venus"):
                rajas_pts += 1.5
            elif occ in ("Mars", "Saturn", "Rahu", "Ketu"):
                tamas_pts += 1.5

        total_pts = max(1.0, satva_pts + rajas_pts + tamas_pts)
        satva_pct = int(round((satva_pts / total_pts) * 100))
        rajas_pct = int(round((rajas_pts / total_pts) * 100))
        tamas_pct = 100 - satva_pct - rajas_pct
        if tamas_pct < 0:
            tamas_pct = 0

        # Integrity Score (0-100)
        h9_score = cls._house_strength_score(chart, 9)
        h1_score = cls._house_strength_score(chart, 1)
        jup_str = cls._planet_strength_score(cls._get_planet(chart, "Jupiter"))
        sun_str = cls._planet_strength_score(cls._get_planet(chart, "Sun"))

        raw_moral = (satva_pct * 0.40) + (h9_score * 0.25) + (jup_str * 100 * 0.20) + (sun_str * 100 * 0.15)
        
        # Affliction deduction: Rahu or Ketu in Lagna without Jupiter aspect
        if "Rahu" in (h1.occupants if h1 else []) and "Jupiter" not in (h1.aspecting_planets if h1 else []):
            raw_moral -= 12.0
        
        morality_score = int(max(25, min(98, round(raw_moral))))

        if morality_score >= 75:
            integrity_level = "उच्च सत्यनिष्ठा एवं धर्मपरायण (High Moral Integrity & Conscientious)"
            integrity_desc = "शास्त्रसम्मत मर्यादा, वचनबद्धता और न्याय के प्रति गहरी निष्ठा। अनैतिक लाभ के अवसर मिलने पर भी अंतरात्मा की पुकार को सर्वोपरि रखते हैं।"
        elif morality_score >= 50:
            integrity_level = "व्यावहारिक एवं परिस्थिति-अनुकूल (Pragmatic & Situationally Ethical)"
            integrity_desc = "सामान्यतः नैतिक व सामाजिक नियमों का पालन करते हैं, किंतु व्यावसायिक या जीवन के जटिल मोड़ों पर कूटनीतिक समझौते करने में हिचकिचाते नहीं।"
        else:
            integrity_level = "नैतिक द्वंद्व एवं प्रलोभन-संवेदनशील (Prone to Moral Conflicts / Utilitarian)"
            integrity_desc = "महत्वाकांक्षा पूर्ति हेतु कभी-कभी नैतिक सीमाओं का अतिक्रमण करने या सत्य से समझौता करने का आंतरिक प्रलोभन रहता है; आत्म-नियंत्रण आवश्यक है।"

        # Positive Virtues & Shadow Vulnerabilities
        virtues = []
        if satva_pct >= 40:
            virtues.append("करुणा, दया एवं परोपकार की स्वाभाविक भावना")
        if jup_str >= 0.65:
            virtues.append("बड़ों एवं गुरुजनों के प्रति आदर, न्यायप्रिय निर्णय क्षमता")
        if sun_str >= 0.65:
            virtues.append("आत्मसम्मान, सत्यवादिता एवं वचन का पक्का होना")
        if not virtues:
            virtues.append("कर्तव्यनिष्ठा, यथार्थवादी सोच एवं व्यावहारिक अनुशासन")

        shadows = []
        if "Rahu" in (h1.occupants if h1 else []) or "Rahu" in (h9.occupants if h9 else []):
            shadows.append("अति-महत्वाकांक्षा व गुप्त कूटनीति के चक्कर में नियमों को तोड़ने की चेष्टा")
        if "Mars" in (h1.occupants if h1 else []) or "Mars" in (cls._get_house(chart, 2).occupants if cls._get_house(chart, 2) else []):
            shadows.append("तीव्र क्रोध में कटु वाणी का प्रयोग व आक्रामक जिद्द")
        if tamas_pct >= 38:
            shadows.append("आलस्य, प्रतिशोध की भावना अथवा नकारात्मक विचारों का पूर्वाग्रह")
        if not shadows:
            shadows.append("अपेक्षाकृत संयमित स्वभाव; कोई गंभीर नैतिक विचलन दोष नहीं")

        return {
            "morality_score": morality_score,
            "guna_distribution": {
                "satva": satva_pct,
                "rajas": rajas_pct,
                "tamas": tamas_pct
            },
            "integrity_level": integrity_level,
            "integrity_desc": integrity_desc,
            "virtues": virtues,
            "shadows": shadows,
            "shastriya_basis": f"नवम भाव (धर्म भाव बल: {h9_score}%), लग्न भाव (आत्म बल: {h1_score}%), तथा सूर्य-बृहस्पति की शास्त्रीय दृष्टि।"
        }

    # =========================================================================
    # 5. VICES & ADDICTIONS (गलत लत, व्यसन एवं प्रलोभन संवेदनशीलता)
    # =========================================================================

    @classmethod
    def analyze_vices_addictions(cls, chart: KundaliChart) -> Dict[str, Any]:
        """Strict, honest scanning of 2nd house (diet/intoxicants), 8th/12th (hidden vices),

        and afflicted Rahu/Venus/Saturn/Mars according to classical Parashari rules.
        """
        h2 = cls._get_house(chart, 2)
        h8 = cls._get_house(chart, 8)
        h12 = cls._get_house(chart, 12)
        h5 = cls._get_house(chart, 5)

        occ_2 = h2.occupants if h2 else []
        occ_8 = h8.occupants if h8 else []
        occ_12 = h12.occupants if h12 else []
        occ_5 = h5.occupants if h5 else []

        asp_2 = h2.aspecting_planets if h2 else []
        asp_8 = h8.aspecting_planets if h8 else []

        rahu_p = cls._get_planet(chart, "Rahu")
        venus_p = cls._get_planet(chart, "Venus")
        mars_p = cls._get_planet(chart, "Mars")
        saturn_p = cls._get_planet(chart, "Saturn")
        jupiter_p = cls._get_planet(chart, "Jupiter")

        jup_protects = "Jupiter" in asp_2 or "Jupiter" in asp_8 or "Jupiter" in (h2.occupants if h2 else [])

        risk_points = 15.0  # Base natural human vulnerability

        triggers = []
        vulnerabilities = []

        # 1. Alcohol & Substance Abuse (मदिरा एवं मादक द्रव्य लत)
        # BPHS: Rahu or afflicted Saturn in 2nd house causes toxic intake / unholy food & drink
        if "Rahu" in occ_2:
            risk_points += 22.0
            triggers.append("२रे भाव में राहु: खान-पान में तामसिक उत्तेजकों, नशीले पदार्थों या अनियंत्रित स्वाद की लालसा का गहरा जोखिम।")
            vulnerabilities.append({
                "vice": "मदिरा / मादक द्रव्य एवं तामसिक खानपान (Alcohol & Toxic Intake Risk)",
                "level": "उच्च जोखिम (High Alert)",
                "reason": "द्वितीय भाव (मुख व आहार भाव) में राहु अनियंत्रित उत्तेजक पदार्थों के प्रति लत उत्पन्न करता है।"
            })
        elif "Saturn" in occ_2 and not jup_protects:
            risk_points += 14.0
            triggers.append("२रे भाव में शनि: बासी, कड़वे या व्यसनकारी पदार्थों (तंबाकू, धूम्रपान, कड़े पेय) के प्रति खिंचाव।")
            vulnerabilities.append({
                "vice": "तंबाकू, धूम्रपान अथवा कड़वे पेय की आदत (Tobacco / Smoking Tendency)",
                "level": "मध्यम जोखिम (Moderate Risk)",
                "reason": "द्वितीय भाव में शनि नीरसता व तनाव से मुक्ति हेतु धूम्रपान या चबाने वाले पदार्थों की लत बना सकता है।"
            })

        # 2. Hidden Addictions & Secret Escapism (गुप्त व्यसन एवं अष्टम भाव)
        if "Rahu" in occ_8 or "Mars" in occ_8:
            risk_points += 18.0
            triggers.append("८वें भाव में राहु/मंगल: गुप्त व्यसनों, इंटरनेट के अंधकारमय कोनों (Dark/Taboo content) या गुप्त दुर्गुणों का प्रलोभन।")
            vulnerabilities.append({
                "vice": "गुप्त व्यसन एवं वर्जित प्रवृत्तियां (Secret Escapism / Taboo Habits)",
                "level": "उच्च जोखिम (High Risk)",
                "reason": "अष्टम भाव गुप्त रहस्यों व पाताल का है; राहु/मंगल यहाँ व्यक्ति को समाज से छिपाकर व्यसनों में प्रवृत्त करते हैं।"
            })

        # 3. Speculation, Gambling & Crypto Trading Greed (सट्टा, जुआ एवं अनियंत्रित जोखिम)
        if "Rahu" in occ_5 or ("Mars" in occ_5 and "Mercury" in occ_8):
            risk_points += 16.0
            triggers.append("५वें भाव में राहु: लॉटरी, जुआ, इंट्राडे ट्रेडिंग, क्रिप्टो या शॉर्टकट से धन कमाने की तीव्र लत में पूंजी गंवाने का खतरा।")
            vulnerabilities.append({
                "vice": "सट्टा, जुआ एवं अनियंत्रित ट्रेडिंग की लत (Gambling / Speculative Trading Obsession)",
                "level": "गंभीर जोखिम (Critical Caution)",
                "reason": "पंचम भाव सट्टेबाजी व बुद्धि का है; राहु यहाँ त्वरित अमीर बनने का भ्रम रचकर भारी आर्थिक चोट देता है।"
            })

        # 4. Sensory Obsession & Sensual Excess (इन्द्रिय लोलुपता एवं वासना का अतिरेक)
        if venus_p and (venus_p.house_from_lagna in (8, 12) or "Rahu" in (h12.occupants if h12 else [])):
            risk_points += 12.0
            triggers.append("१२वें भाव में राहु अथवा अष्टम/द्वादश में पीड़ित शुक्र: विलासिता, कामुक भटकाव व रात्रि जागरण (अनिद्रा) की लत।")
            vulnerabilities.append({
                "vice": "कामुक भटकाव, अनैतिक संबंध प्रलोभन व अनिद्रा (Sensory Obsession & Sleep Disorders)",
                "level": "मध्यम से उच्च (Moderate to High)",
                "reason": "द्वादश भाव शयन सुख व भोग का है; यहाँ राहु या पीड़ित शुक्र भटकाव और धन के अपव्यय की लत लगाते हैं।"
            })

        # 5. Rage & Aggression Addiction (क्रोध एवं आक्रामकता का आवेश)
        h1 = cls._get_house(chart, 1)
        if "Mars" in (h1.occupants if h1 else []) or ("Mars" in occ_2 and not jup_protects):
            risk_points += 10.0
            triggers.append("लग्न अथवा द्वितीय भाव में मंगल: बात-बात पर अत्यधिक क्रोध, चीखना-चिल्लाना व आक्रामक प्रतिक्रिया देने की आदत।")
            vulnerabilities.append({
                "vice": "तीव्र क्रोध व विस्फोटक वाणी की लत (Destructive Rage & Verbal Outbursts)",
                "level": "मध्यम जोखिम (Moderate Alert)",
                "reason": "मंगल का अग्नि तत्व वाणी व मस्तिष्कीय संतुलन को क्षणिक रूप से बिगाड़कर आक्रामक बना देता है।"
            })

        # Protective discount if Jupiter aspects
        if jup_protects:
            risk_points = max(10.0, risk_points - 18.0)
            triggers.append("🛡️ देवगुरु बृहस्पति की अमृत दृष्टि: गुरु का प्रभाव आंतरिक आत्म-नियंत्रण, पश्चाताप और व्यसनों से उबरने की दिव्य शक्ति प्रदान करता है।")

        if not vulnerabilities:
            vulnerabilities.append({
                "vice": "कोई गंभीर व्यसन या घातक लत के योग नहीं (Clean Astrological Profile)",
                "level": "न्यूनतम जोखिम (Safe)",
                "reason": "२रे, ८वें व १२वें भाव पर कोई अनियंत्रित पापी प्रभाव नहीं है; जातक में सात्विक आत्म-नियंत्रण विद्यमान है।"
            })

        addiction_score = int(max(5, min(95, round(risk_points))))

        if addiction_score >= 65:
            risk_level = "उच्च जोखिम / विशेष सतर्कता अपेक्षित (High Vulnerability - Strict Self-Control Required)"
            warning_advice = "शास्त्र चेतावनी: कुण्डली में २रे/८वें/५वें भाव पर तमोगुणी ग्रहों का गहरा दबाव है। मदिरा, सट्टा-ट्रेडिंग, जुआ अथवा अनैतिक संबंधों के संपर्क से पूर्णतः दूर रहें; एक बार लत लगने पर मुक्ति अत्यंत कठिन होगी।"
        elif addiction_score >= 40:
            risk_level = "मध्यम जोखिम / संगति पर ध्यान दें (Moderate Caution - Watch Peer Influence)"
            warning_advice = "मित्र मंडली और एकांत के समय विशेष सतर्क रहें। तनाव के क्षणों में धूम्रपान, स्क्रीन के अति-प्रयोग या अस्वास्थ्यकर खान-पान की लत पकड़ सकती है।"
        else:
            risk_level = "न्यूनतम जोखिम / सुरक्षित (Low Risk - High Natural Resilience)"
            warning_advice = "आपकी कुण्डली में आत्म-संयम का स्तर उत्कृष्ट है। सामान्य सामाजिक दबावों से आप विचलित नहीं होते।"

        remedies = [
            "नित्य प्रातः भगवान शिव का जल से अभिषेक करें और 'ॐ नमः शिवाय' का १०८ बार जाप करें।",
            "२रे भाव के शुद्धिकरण हेतु भोजन से पूर्व 'अन्नपूर्णा स्तोत्र' अथवा गायत्री मंत्र का एक बार स्मरण अवश्य करें।",
            "शनिवार अथवा अमावस्या के दिन किसी निर्धन अथवा सफाईकर्मी को भोजन व तिल का दान करें (राहु-शनि शांति)।",
            "घर के शयनकक्ष (Bedroom) में कभी भी मदिरापान अथवा मांसाहार का सेवन न करें।"
        ]

        return {
            "addiction_score": addiction_score,
            "risk_level": risk_level,
            "warning_advice": warning_advice,
            "vulnerabilities": vulnerabilities,
            "triggers": triggers,
            "remedies": remedies,
            "shastriya_basis": "बृहत्पाराशर होराशास्त्र (द्वितीय भाव फल, अष्टम भाव छिद्र विचार एवं राहु-शुक्र युति लक्षण)।"
        }

    # =========================================================================
    # 6. ANCESTRAL PROPERTY & INHERITANCE (पैतृक संपत्ति, वसीयत एवं विरासत)
    # =========================================================================

    @classmethod
    def analyze_inheritance(cls, chart: KundaliChart) -> Dict[str, Any]:
        """Calculates 8th house (inheritance/wills), 9th house (father's wealth),

        4th house (lands/properties), Mars (Bhumi), and Jupiter.
        """
        h8_score = cls._house_strength_score(chart, 8)
        h9_score = cls._house_strength_score(chart, 9)
        h4_score = cls._house_strength_score(chart, 4)
        h2_score = cls._house_strength_score(chart, 2)

        mars_str = cls._planet_strength_score(cls._get_planet(chart, "Mars"))
        jup_str = cls._planet_strength_score(cls._get_planet(chart, "Jupiter"))
        sun_str = cls._planet_strength_score(cls._get_planet(chart, "Sun"))

        # Composite score
        raw_inh = (h8_score * 0.35) + (h9_score * 0.25) + (h4_score * 0.20) + (mars_str * 100 * 0.10) + (jup_str * 100 * 0.10)

        # Affliction checks
        h8 = cls._get_house(chart, 8)
        occ_8 = h8.occupants if h8 else []
        saturn_in_8 = "Saturn" in occ_8
        rahu_in_8 = "Rahu" in occ_8
        mars_in_8 = "Mars" in occ_8

        dispute_risk = "न्यूनतम / सहज पारिवारिक सहमति"
        if saturn_in_8 and rahu_in_8:
            raw_inh -= 15.0
            dispute_risk = "अत्यधिक उच्च जोखिम / न्यायालयीन वसीयत विवाद (Court Litigation)"
        elif saturn_in_8 or rahu_in_8 or mars_in_8:
            raw_inh -= 8.0
            dispute_risk = "मध्यम जोखिम / पारिवारिक हिस्सेदारी को लेकर वैचारिक खींचतान व विलंब"

        inheritance_score = int(max(15, min(95, round(raw_inh))))

        if inheritance_score >= 70:
            status = "प्रचुर एवं सहज पैतृक लाभ (Substantial & Unobstructed Inheritance)"
            status_desc = "अष्टम एवं नवम भाव के शुभ प्रभाव से पिता व पूर्वजों द्वारा निर्मित अचल संपत्ति, स्वर्ण, भूमि अथवा पारिवारिक प्रतिष्ठान का प्रचुर लाभ प्राप्त होगा।"
        elif inheritance_score >= 45:
            status = "मध्यम लाभ / विलंब उपरांत प्राप्ति (Moderate Inheritance after Negotiations)"
            status_desc = "पैतृक संपत्ति प्राप्त तो होगी, परंतु कागजी औपचारिकताओं, हिस्सेदारों के साथ वार्ताओं अथवा कुछ समय के विलंब के उपरांत ही पूर्ण अधिकार मिलेगा।"
        else:
            status = "सीमित पैतृक लाभ अथवा दायित्वों की अधिकता (Minimal Inheritance / Self-Made Wealth Foreseen)"
            status_desc = "पूर्वजों से संपत्ति की तुलना में पारिवारिक दायित्व या ऋण अधिक मिल सकते हैं। जातक का संपूर्ण भाग्योदय स्व-अर्जित पुरुषार्थ (Self-Made) पर ही आधारित रहेगा।"

        # Land & Immovable Property (Mars + 4th house)
        if mars_str >= 0.65 and h4_score >= 60:
            land_status = "भूमि, भवन व कृषि संपदा का विशेष योग (Strong Real Estate & Land Acquisition)"
        else:
            land_status = "सामान्य आवासीय संपत्ति योग (Standard Residential Property)"

        # Father's Support & Harmony (9th house & Sun)
        if sun_str >= 0.60 and h9_score >= 55:
            father_support = "पिता का पूर्ण स्नेह, मार्गदर्शन एवं आशीर्वाद (Harmonious Paternal Bond)"
        elif sun_str <= 0.40 or (cls._get_planet(chart, "Sun") and cls._get_planet(chart, "Sun").dignity == "debilitated"):
            father_support = "पिता के स्वास्थ्य की चिंता अथवा वैचारिक मतभेद (Ideological Differences with Father)"
        else:
            father_support = "सामान्य व व्यावहारिक पितृ संबंध (Balanced Paternal Support)"

        return {
            "inheritance_score": inheritance_score,
            "status": status,
            "status_desc": status_desc,
            "dispute_risk": dispute_risk,
            "land_status": land_status,
            "father_support": father_support,
            "shastriya_basis": f"अष्टम भाव (वसीयत व पैतृक धन: {h8_score}%), नवम भाव (पितृ भाव: {h9_score}%), चतुर्थ भाव (भूमि-भवन: {h4_score}%) एवं मंगल का कारकत्व।"
        }

    # =========================================================================
    # 7. HAPPINESS & MENTAL INNER PEACE (सुख एवं मानसिक शांति)
    # =========================================================================

    @classmethod
    def analyze_sukha_peace(cls, chart: KundaliChart) -> Dict[str, Any]:
        """Calculates 4th house (heart's peace), Moon condition, Kemadruma, Vish Yoga, Grahan Yoga."""
        h4_score = cls._house_strength_score(chart, 4)
        moon_p = cls._get_planet(chart, "Moon")
        moon_str = cls._planet_strength_score(moon_p)

        raw_peace = (h4_score * 0.45) + (moon_str * 100 * 0.55)

        moon_doshas = []
        stressors = []

        if moon_p:
            moon_house = moon_p.house_from_lagna
            h_moon = cls._get_house(chart, moon_house)
            moon_occ = h_moon.occupants if h_moon else []

            # 1. Vish Yoga (Moon + Saturn)
            if "Saturn" in moon_occ:
                raw_peace -= 18.0
                moon_doshas.append("⚠️ चन्द्र-शनि युति (विष योग - Vish Yoga): मन में अज्ञात भय, अत्यधिक चिंता, निराशावाद (Pessimism) एवं अकेलापन महसूस होना।")
                stressors.append("अकेलापन, करियर में विलंब का तनाव एवं अत्यधिक उत्तरदायित्व का बोझ")

            # 2. Grahan Yoga (Moon + Rahu or Ketu)
            if "Rahu" in moon_occ:
                raw_peace -= 16.0
                moon_doshas.append("⚡ चन्द्र-राहु युति (ग्रहण योग - Grahan Yoga): अत्यधिक विचार (Overthinking), अनिद्रा, भय एवं भावनात्मक अस्थिरता (Mood Swings)।")
                stressors.append("अति-कल्पनाशीलता, भविष्य की अनावश्यक घबराहट एवं अनिद्रा")
            elif "Ketu" in moon_occ:
                raw_peace -= 14.0
                moon_doshas.append("🌀 चन्द्र-केतु युति: संसार से विरक्ति, वैराग्य की भावना, भावनात्मक अलगाव एवं चित्त की चंचलता।")
                stressors.append("भावनात्मक संवाद की कमी एवं अंतर्मुखी उदासी")

            # 3. Chandra-Mangal (Restlessness)
            if "Mars" in moon_occ:
                raw_peace -= 8.0
                moon_doshas.append("🔥 चन्द्र-मंगल युति: अत्यधिक अधीरता, गुस्सा जल्दी आना और मानसिक उद्विग्नता, यद्यपि यह धन हेतु श्रेष्ठ है।")
                stressors.append("अधीरता एवं जल्दबाजी में लिए गए निर्णयों का पछतावा")

            # 4. Debilitated Moon (in Scorpio)
            if moon_p.sign_name == "Scorpio":
                raw_peace -= 14.0
                moon_doshas.append("♏ चन्द्रमा नीच राशि (वृश्चिक) में: मन की संवेदनशीलता अत्यधिक होना, छोटी-छोटी बातों को दिल पर लगाना और गहरा मानसिक आघात।")
                stressors.append("अत्यधिक भावुकता एवं असुरक्षा की आंतरिक भावना")

            # 5. Moon in 6th, 8th or 12th house (Trik Bhava)
            if moon_house in (6, 8, 12):
                raw_peace -= 10.0
                moon_doshas.append(f"🌊 चन्द्रमा {moon_house}वें (त्रिक) भाव में: मानसिक शांति में निरंतर उतार-चढ़ाव एवं अज्ञात आशंकाएं।")
                stressors.append("पारिवारिक या स्वास्थ्य संबंधी चिंताओं से मन में अशांति")

        if not moon_doshas:
            moon_doshas.append("✅ चन्द्रमा कुण्डली में शुभ एवं निष्पाप है; किसी बड़े मानसिक दोष (विष/ग्रहण योग) का अभाव है।")

        if not stressors:
            stressors.append("सामान्य सांसारिक जिम्मेदारियों के अतिरिक्त कोई स्थायी मानसिक अवसाद नहीं।")

        inner_peace_score = int(max(10, min(95, round(raw_peace))))

        if inner_peace_score >= 70:
            peace_status = "प्रशांत, संतुलित एवं संतोषप्रद (Deep Inner Serenity & Contentment)"
            peace_desc = "चतुर्थ भाव एवं चन्द्रमा के अनुग्रह से आपका हृदय शांत रहता है। प्रतिकूल परिस्थितियों में भी आप धैर्य और आत्मिक संतुलन बनाए रखते हैं।"
        elif inner_peace_score >= 45:
            peace_status = "उतार-चढ़ाव युक्त / परिस्थिति-संवेदनशील (Fluctuating / Stress-Prone under Pressure)"
            peace_desc = "बाहरी वातावरण अनुकूल होने पर प्रसन्न रहते हैं, किंतु अत्यधिक कार्यभार या संबंधों में तनाव आने पर तुरंत विचलित हो जाते हैं।"
        else:
            peace_status = "गंभीर मानसिक उद्विग्नता व अशांति (Severe Restlessness & Anxiety Tendency)"
            peace_desc = "कुण्डली में चन्द्रमा अथवा चतुर्थ भाव पीड़ित होने से मन को गहरा आंतरिक विश्राम नहीं मिल पाता; अति-विचार और अवसाद से रक्षा हेतु वैदिक उपाय अनिवार्य हैं।"

        remedies = [
            "प्रतिदिन चांदी के गिलास में जल पिएं (चन्द्रमा को शीतलता व बल प्रदान करता है)।",
            "सोमवार को शिवलिंग पर कच्चा दूध व जल अर्पित कर 'महामृत्युंजय मंत्र' का १०८ बार जप करें।",
            "प्रतिदिन १०-१५ मिनट अनुलोम-विलोम प्राणायाम करें और पूर्णिमा की रात्रि में चन्द्रमा की किरणों में बैठें।",
            "माता का चरण स्पर्श कर नित्य आशीर्वाद लें; माता का आशीर्वाद चन्द्रमा का सर्वोत्तम रक्षा कवच है।"
        ]

        return {
            "inner_peace_score": inner_peace_score,
            "peace_status": peace_status,
            "peace_desc": peace_desc,
            "moon_doshas": moon_doshas,
            "stressors": stressors[:3],
            "remedies": remedies,
            "shastriya_basis": f"चतुर्थ भाव (सुख भाव बल: {h4_score}%), चन्द्रमा की गरिमा ({moon_p.dignity if moon_p else 'N/A'}), तथा चन्द्रमा से संबंधित शास्त्रीय योग।"
        }

    # =========================================================================
    # 8. PAST LIFE KARMA & DEBTS (पूर्वजन्म के कर्म, ऋणानुबंध एवं प्रारब्ध)
    # =========================================================================

    @classmethod
    def analyze_past_life_karma(cls, chart: KundaliChart) -> Dict[str, Any]:
        """Calculates 5th house (Purva Punya merits brought forward), 9th house (Dharma Grace),

        6th/8th/12th houses (Rina Bandhana / Karmic Debts), Rahu (Unfulfilled desires),
        Ketu (Past life mastery & detachment), and Atmakaraka lesson (BPHS Ch. 32 & Jaimini).
        """
        h5_score = cls._house_strength_score(chart, 5)
        h9_score = cls._house_strength_score(chart, 9)
        h12_score = cls._house_strength_score(chart, 12)

        jup_str = cls._planet_strength_score(cls._get_planet(chart, "Jupiter"))
        sun_str = cls._planet_strength_score(cls._get_planet(chart, "Sun"))

        # Purva Punya Score (0-100)
        raw_punya = (h5_score * 0.45) + (h9_score * 0.35) + (jup_str * 100 * 0.20)
        purva_punya_score = int(max(20, min(98, round(raw_punya))))

        # Karmic Debt Burden Level
        if purva_punya_score >= 70:
            karmic_burden = "अल्प ऋण / संचित पुण्यों की प्रचुरता (Abundant Purva Punya & Light Debts)"
            burden_desc = "पूर्वजन्मों में किए गए धर्म, दान व सत्कर्मों की पूंजी इस जन्म में आपको कठिन संकटों में भी दैवीय सुरक्षा एवं अप्रत्याशित सहायता प्रदान करती है।"
        elif purva_punya_score >= 45:
            karmic_burden = "संतुलित ऋणानुबंध (Moderate Karmic Balance - Balanced Give & Take)"
            burden_desc = "आपके संचित कर्मों में पुण्य और ऋण दोनों बराबर अनुपात में हैं। जीवन में सुख और संघर्ष दोनों का क्रमिक अनुभव होगा।"
        else:
            karmic_burden = "गहन प्रारब्ध जनित ऋणानुबंध (Heavy Karmic Debts to Clear Through Seva)"
            burden_desc = "पूर्वजन्म के कुछ जटिल ऋणानुबंध शेष हैं, जिन्हें इस जन्म में त्याग, सेवा, क्षमा और कठिन संघर्ष के माध्यम से चुकाना विधाता का विधान है।"

        # Rahu: Soul's Unfulfilled Desires (जिस भाव में राहु है, वहाँ पिछले जन्म की अतृप्त वासनाएं हैं)
        rahu_p = cls._get_planet(chart, "Rahu")
        rahu_desire_map = {
            1: "प्रथम भाव (लग्न): पूर्वजन्म में दूसरों के अधीन रहने के कारण इस जन्म में स्वतंत्र पहचान, आत्म-सम्मान व समाज पर प्रभुत्व स्थापित करने की तीव्र पिपासा।",
            2: "द्वितीय भाव: पूर्वजन्म में आर्थिक तंगी अथवा कुटुंब विछोह के कारण इस जन्म में अकूत धन संग्रह, परिवार विस्तार व उत्तम भोजन की प्रबल लिप्सा।",
            3: "तृतीय भाव: पूर्वजन्म में अपने बाहुबल का प्रयोग न कर पाने के कारण इस जन्म में अदम्य पराक्रम, मीडिया, खेल, संचार व सोशल प्रभाव की भूख।",
            4: "चतुर्थ भाव: पूर्वजन्म में गृह-सुख अथवा मातृ-वात्सल्य से वंचित रहने के कारण इस जन्म में भव्य महल, वाहन, अचल संपत्ति व सुरक्षित आश्रय की तीव्र चाह।",
            5: "पंचम भाव: पूर्वजन्म में ज्ञान, प्रसिद्धि अथवा संतान सुख अधूरा रहने के कारण इस जन्म में विशिष्ट बौद्धिक मान्यता, सट्टा-लाभ व श्रेष्ठ संतति की अभिलाषा।",
            6: "षष्ठम भाव: पूर्वजन्म के शत्रुओं, मुकदमों अथवा ऋणों से इस जन्म में जूझकर उन पर पूर्ण विजय प्राप्त करने और सेवा क्षेत्र में वर्चस्व की चाह।",
            7: "सप्तम भाव: पूर्वजन्म में वैवाहिक निष्ठा अथवा साझेदारी का अधूरा पाठ; इस जन्म में आकर्षक जीवनसाथी, जन-आकर्षण व व्यापारिक अनुबंधों की भूख।",
            8: "अष्टम भाव: पूर्वजन्म में गूढ़ विधाओं, वसीयत व रहस्यमय ज्ञान की खोज अधूरी रही; इस जन्म में तंत्र, गुप्त धन व अनदेखी शक्तियों के प्रति गहरा आकर्षण।",
            9: "नवम भाव: पूर्वजन्म में धर्म, तीर्थ अथवा पिता से जुड़े असंतोष के कारण इस जन्म में नए दार्शनिक मार्गों की खोज, विदेश यात्रा व आध्यात्मिक सत्ता की चाह।",
            10: "दशम भाव: पूर्वजन्म में सत्ता व प्रतिष्ठा की अधूरी महत्वाकांक्षा; इस जन्म में उच्च पद, राजकीय अधिकार, सत्ता व जनता पर राज करने की अदम्य इच्छा।",
            11: "एकादश भाव: पूर्वजन्म में बड़े लक्ष्यों व आर्थिक लाभों की अतृप्ति; इस जन्म में विशाल सामाजिक नेटवर्क, शीर्ष मित्रों व अनपेक्षित लाभों की तीव्र लालसा।",
            12: "द्वादश भाव: पूर्वजन्म में मोक्ष, विदेश प्रवास व भौतिक त्याग का अधूरा क्रम; इस जन्म में विदेशी भूमि, एकांत व परलौकिक अनुसंधानों की ओर खिंचाव।"
        }
        rahu_house = rahu_p.house_from_lagna if rahu_p else 1
        rahu_desire = rahu_desire_map.get(rahu_house, "सांसारिक महत्वाकांक्षाओं की पूर्ति का तीव्र खिंचाव।")

        # Ketu: Past Life Mastery & Detachment (जिस भाव में केतु है, वहाँ पूर्वजन्म की सिद्धि है)
        ketu_p = cls._get_planet(chart, "Ketu")
        ketu_mastery_map = {
            1: "प्रथम भाव: पूर्वजन्म में वैराग्य, आत्म-साधना व संन्यास का अनुभव; इस जन्म में स्वयं के प्रति अनासक्ति व आंतरिक उदासीनता।",
            2: "द्वितीय भाव: पूर्वजन्म में धन व कुटुंब के मोह से मुक्ति का पाठ सीखा; इस जन्म में भौतिक धन संचय से अंततः सहज विरक्ति।",
            3: "तृतीय भाव: पूर्वजन्म में पराक्रम व युद्ध कला में प्रवीणता; इस जन्म में व्यर्थ के विवादों व बाहुबल के प्रदर्शन में रुचि न होना।",
            4: "चतुर्थ भाव: पूर्वजन्म में भौतिक महलों से हटकर हृदय-गुहा में शांति पा चुके हैं; इस जन्म में भौतिक मकानों से पूर्ण तृप्ति नहीं मिलती।",
            5: "पंचम भाव: पूर्वजन्म में मंत्र-सिद्धि, पूर्व-पुण्य व आध्यात्मिक मेधा का संचय; इस जन्म में सहज अंतर्ज्ञान (Intuition) का वरदान।",
            6: "षष्ठम भाव: पूर्वजन्म में तपस्या व रोगों-शत्रुओं पर विजय की सिद्धि; इस जन्म में सेवा भाव स्वतः जाग्रत रहता है।",
            7: "सप्तम भाव: पूर्वजन्म में गृहस्थ जीवन के सुख-दुख भोग चुके हैं; इस जन्म में दांपत्य में भौतिक आकर्षण की जगह आध्यात्मिक संगति की खोज।",
            8: "अष्टम भाव: पूर्वजन्म के तंत्र, योग व गूढ़ रहस्यों का गहरा अवचेतन ज्ञान; गुप्त विधाएं बिना सीखे भी स्वतः समझ आने लगती हैं।",
            9: "नवम भाव: पूर्वजन्म में कठोर तीर्थाटन, धर्मशास्त्रों का ज्ञान व गुरु कृपा प्राप्त; इस जन्म में बाह्य पाखंड से परे वास्तविक सत्य की खोज।",
            10: "दशम भाव: पूर्वजन्म में सत्ता व राजपद का पूर्ण उपभोग कर चुके हैं; इस जन्म में उच्च पद पाकर भी पद के प्रति आंतरिक मोह नहीं रहता।",
            11: "एकादश भाव: पूर्वजन्म में सांसारिक लाभों की निरर्थकता जान चुके हैं; इस जन्म में मित्रों की भीड़ से दूर एकांत अधिक प्रिय लगता है।",
            12: "द्वादश भाव: पूर्वजन्म में मोक्ष के द्वार तक पहुँच चुके थे; इस जन्म में आध्यात्मिक मुक्ति, ध्यान व ईश्वर-मिलन की तीव्र सहज प्रेरणा।"
        }
        ketu_house = ketu_p.house_from_lagna if ketu_p else 7
        ketu_mastery = ketu_mastery_map.get(ketu_house, "पूर्वजन्म के गूढ़ संस्कारों की अवचेतन स्मृति।")

        # Atmakaraka Soul Lesson (BPHS & Jaimini Sutras)
        ak_name = chart.atmakaraka or "Jupiter"
        ak_lesson_map = {
            "Sun": {
                "lesson_hi": "अहंकार व प्रभुत्व का विसर्जन (Transcending False Pride & Ego)",
                "detail_hi": "आत्मा का पाठ: दूसरों पर अपनी सत्ता थोपने के स्थान पर विनम्रता, सेवा और निस्वार्थ नेतृत्व को अपनाना।"
            },
            "Moon": {
                "lesson_hi": "भावनात्मक अनासक्ति एवं सार्वभौमिक करुणा (Emotional Equanimity & Compassion)",
                "detail_hi": "आत्मा का पाठ: रिश्तों में अति-अपेक्षाओं व मूड-स्विंग्स से परे होकर सभी प्राणियों के प्रति समभाव व ममता विकसित करना।"
            },
            "Mars": {
                "lesson_hi": "क्रोध-विजय, अहिंसा एवं रचनात्मक शक्ति (Mastery Over Anger & Non-Violence)",
                "detail_hi": "आत्मा का पाठ: आवेश, बदले की भावना व शारीरिक आक्रामकता को त्यागकर अपनी ऊर्जा को धर्म रक्षा व सृजन में लगाना।"
            },
            "Mercury": {
                "lesson_hi": "सत्य-निष्ठा, वाक्-संयम एवं कपट-त्याग (Absolute Truthfulness & Pure Intellect)",
                "detail_hi": "आत्मा का पाठ: वाक्-चातुर्य से दूसरों को छलने या दोहरे मापदंड अपनाने से बचना और बुद्धि को केवल सत्य व ईश्वरीय ज्ञान में लगाना।"
            },
            "Jupiter": {
                "lesson_hi": "ज्ञान-अहंकार का त्याग एवं गुरु-मर्यादा (Humility in Wisdom & Respect for Teachers)",
                "detail_hi": "आत्मा का पाठ: अपने ज्ञान, धर्म या कुल का दंभ न करना; अन्य मतों का आदर करना और संकीर्ण हठधर्मिता से मुक्त रहना।"
            },
            "Venus": {
                "lesson_hi": "इन्द्रिय-संयम एवं पवित्र प्रेम (Sublimation of Lust into Divine Love)",
                "detail_hi": "आत्मा का पाठ: वासना व भौतिक भोग-विलास की लालसा को शुद्ध प्रेम, भक्ति और दांपत्य निष्ठा में रूपांतरित करना।"
            },
            "Saturn": {
                "lesson_hi": "धैर्य, सेवा एवं दीन-दुखियों का उद्धार (Patience, Duty & Serving the Downtrodden)",
                "detail_hi": "आत्मा का पाठ: बिना किसी कड़वाहट के कष्टों को प्रारब्ध मानकर स्वीकार करना और समाज के उपेक्षित जनों की सेवा करना।"
            },
            "Rahu": {
                "lesson_hi": "माया-त्याग एवं निष्कपट साधना (Transcending Illusions & Deception)",
                "detail_hi": "आत्मा का पाठ: सांसारिक प्रलोभनों, छलावे व शॉर्टकट मार्गों का परित्याग कर आध्यात्मिक सरलता व सत्य को धारण करना।"
            }
        }
        ak_info = ak_lesson_map.get(ak_name, ak_lesson_map["Jupiter"])

        # Detect Specific Karmic Debts (ऋणानुबंध)
        active_debts = []
        sun_p = cls._get_planet(chart, "Sun")
        moon_p = cls._get_planet(chart, "Moon")
        mars_p = cls._get_planet(chart, "Mars")

        # Pitru Rina (Sun afflicted by Rahu/Saturn or 9th house heavily afflicted)
        if sun_p and (sun_p.house_from_lagna in (8, 12) or "Rahu" in (cls._get_house(chart, sun_p.house_from_lagna).occupants if cls._get_house(chart, sun_p.house_from_lagna) else [])):
            active_debts.append({
                "debt_name": "पितृ ऋण (Ancestral / Paternal Debt)",
                "symptom": "वंश वृद्धि में बाधा, पिता से मतभेद अथवा जीवन में अप्रत्याशित अपमान।",
                "redemption": "अमावस्या को पितरों के निमित्त तर्पण, पीपल वृक्ष को जल व निर्धन वृद्धों को अन्न वस्त्र दान करें।"
            })

        # Matru Rina (Moon afflicted by Rahu/Saturn or 4th house afflicted)
        if moon_p and (moon_p.house_from_lagna in (6, 8, 12) or "Saturn" in (cls._get_house(chart, moon_p.house_from_lagna).occupants if cls._get_house(chart, moon_p.house_from_lagna) else [])):
            active_debts.append({
                "debt_name": "मातृ ऋण (Mother / Female Lineage Debt)",
                "symptom": "मानसिक अशांति, अनिद्रा, पारिवारिक कलह व माता के स्वास्थ्य में कष्ट।",
                "redemption": "माता की नित्य सेवा, वृद्ध महिलाओं को सफेद वस्त्र/चावल का दान एवं पूर्णिमा को शिव-पार्वती पूजन।"
            })

        # Bhratri / Bhumi Rina (Mars afflicted by Rahu/Saturn)
        if mars_p and ("Rahu" in (cls._get_house(chart, mars_p.house_from_lagna).occupants if cls._get_house(chart, mars_p.house_from_lagna) else [])):
            active_debts.append({
                "debt_name": "बंधु / भूमि ऋण (Sibling & Land Karma)",
                "symptom": "भाइयों से विवाद, भूमि-मकान संबंधी सौदों में धोखा या कोर्ट-कचहरी।",
                "redemption": "मंगलवार को हनुमान जी को सिंदूर व चोला चढ़ाएं, पक्षियों को लाल मसूर डालें व छोटे भाइयों की सहायता करें।"
            })

        if not active_debts:
            active_debts.append({
                "debt_name": "सामान्य सांसारिक ऋण (General Worldly Dharma)",
                "symptom": "कोई गंभीर कुल-ऋण या पितृ दोष सक्रिय नहीं है।",
                "redemption": "दैनिक पंच महायज्ञ (देव, ऋषि, पितृ, मनुष्य, भूत यज्ञ - पक्षियों/चींटियों को दाना) का पालन करें।"
            })

        return {
            "purva_punya_score": purva_punya_score,
            "karmic_burden": karmic_burden,
            "burden_desc": burden_desc,
            "rahu_desire": rahu_desire,
            "ketu_mastery": ketu_mastery,
            "atmakaraka": ak_name,
            "atmakaraka_lesson": ak_info["lesson_hi"],
            "atmakaraka_detail": ak_info["detail_hi"],
            "active_debts": active_debts,
            "shastriya_basis": "बृहत्पाराशर होराशास्त्र (पंचम भाव पूर्व-पुण्य, आत्मकारक अध्याय ३२ व जैमिनी उपदेश सूत्र)।"
        }

    # =========================================================================
    # MASTER ANALYZER
    # =========================================================================

    @classmethod
    def analyze(cls, chart: KundaliChart) -> Dict[str, Any]:
        """Runs the complete personality and karmaphala evaluation."""
        return {
            "career": cls.analyze_career(chart),
            "education": cls.analyze_education(chart),
            "morals": cls.analyze_morals(chart),
            "vices": cls.analyze_vices_addictions(chart),
            "inheritance": cls.analyze_inheritance(chart),
            "peace": cls.analyze_sukha_peace(chart),
            "karma": cls.analyze_past_life_karma(chart),
        }
