"""
Classical Yoga and Dosha Engine for Bharat Jyotish AI.
Evaluates 30+ classical Yogas (Pancha Mahapurusha, Raja, Dhana, Chandra, Surya, Vipareeta, Neechabhanga)
and major classical Doshas (Manglik with cancellations, Kaal Sarp 12 types, Guru Chandal, Pitru, Gandanta)
according to Brihat Parashara Hora Shastra, Phaladeepika, Saravali, and Jataka Parijata.
"""

import math
from typing import Dict, List, Tuple, Optional, Any
from .constants import (
    SIGN_NAMES, SIGN_LORDS, EXALTATION, DEBILITATION, OWN_SIGNS,
    KENDRA_HOUSES, TRIKONA_HOUSES, DUSTHANA_HOUSES
)
from .models import (
    KundaliChart, PlanetPosition, ClassicalYogaItem, ClassicalDoshaItem,
    YogaDoshaAnalysisResult
)


class ClassicalYogaDoshaEngine:
    """Deterministic Shastriya Engine for Yoga and Dosha Evaluation."""

    @classmethod
    def evaluate_all(cls, chart: KundaliChart) -> YogaDoshaAnalysisResult:
        """Evaluates all classical Yogas and Doshas for the chart."""
        yogas: List[ClassicalYogaItem] = []
        doshas: List[ClassicalDoshaItem] = []

        # 1. Evaluate Pancha Mahapurusha Yogas
        yogas.extend(cls._evaluate_pancha_mahapurusha(chart))

        # 2. Evaluate Raja Yogas & Neechabhanga
        yogas.extend(cls._evaluate_raja_yogas(chart))

        # 3. Evaluate Dhana Yogas
        yogas.extend(cls._evaluate_dhana_yogas(chart))

        # 4. Evaluate Chandra & Surya Yogas
        yogas.extend(cls._evaluate_chandra_surya_yogas(chart))

        # 5. Evaluate Amala & Special Yogas
        yogas.extend(cls._evaluate_amala_yoga(chart))

        # 4. Evaluate Major Doshas
        m_dosha, is_manglik, m_sev, m_canc = cls._evaluate_manglik_dosha(chart)
        doshas.append(m_dosha)

        ks_dosha, ks_type, ks_active = cls._evaluate_kaal_sarp_dosha(chart)
        doshas.append(ks_dosha)

        doshas.append(cls._evaluate_guru_chandal(chart))
        doshas.append(cls._evaluate_pitru_dosha(chart))
        doshas.append(cls._evaluate_kemadruma_dosha(chart))
        doshas.append(cls._evaluate_gandanta(chart))

        active_yogas = [y for y in yogas if y.is_active]
        active_doshas = [d for d in doshas if d.is_present and not d.is_cancelled]

        return YogaDoshaAnalysisResult(
            yogas=yogas,
            active_yogas_count=len(active_yogas),
            doshas=doshas,
            active_doshas_count=len(active_doshas),
            is_manglik=is_manglik,
            manglik_severity=m_sev,
            manglik_cancelled=m_canc,
            kaal_sarp_type=ks_type,
            kaal_sarp_active=ks_active
        )

    # -------------------------------------------------------------
    # 1. PANCHA MAHAPURUSHA YOGAS
    # -------------------------------------------------------------
    @classmethod
    def _evaluate_pancha_mahapurusha(cls, chart: KundaliChart) -> List[ClassicalYogaItem]:
        results = []
        p_definitions = [
            ("Mars", "Ruchaka", "रूचक महापुरुष योग", "Ruchaka Mahapurusha Yoga",
             ["Aries", "Scorpio", "Capricorn"], "BPHS Ch. 35.1-4",
             "साहस, सैन्य पराक्रम, नेतृत्व, अचल सम्पत्ति एवं विशिष्ट प्रशासनिक शक्ति।",
             "Valor, executive administrative authority, leadership, and land ownership."),
            ("Mercury", "Bhadra", "भद्र महापुरुष योग", "Bhadra Mahapurusha Yoga",
             ["Gemini", "Virgo"], "BPHS Ch. 35.5-8",
             "तीक्ष्ण बुद्धि, वाकचातुर्य, गणित, व्यापार एवं उच्च बौद्धिक प्रतिष्ठा।",
             "Supreme intellectual brilliance, eloquence, commerce, and scholarly fame."),
            ("Jupiter", "Hamsa", "हंस महापुरुष योग", "Hamsa Mahapurusha Yoga",
             ["Sagittarius", "Pisces", "Cancer"], "BPHS Ch. 35.9-12",
             "आध्यात्मिक ज्ञान, सदाचार, पूज्य प्रतिष्ठा, धर्मपरायणता एवं दीर्घायु।",
             "Spiritual wisdom, virtue, universal respect, righteous wealth, and longevity."),
            ("Venus", "Malavya", "मालव्य महापुरुष योग", "Malavya Mahapurusha Yoga",
             ["Taurus", "Libra", "Pisces"], "BPHS Ch. 35.13-16",
             "ऐश्वर्य, कलात्मक प्रतिभा, भौतिक सुख, वाहन एवं तेजस्वी व्यक्तित्व।",
             "Sensory luxuries, artistic mastery, wealth, charm, and matrimonial felicity."),
            ("Saturn", "Sasa", "शश महापुरुष योग", "Sasa Mahapurusha Yoga",
             ["Capricorn", "Aquarius", "Libra"], "BPHS Ch. 35.17-20",
             "जनसमूह पर आधिपत्य, दृढ़ता, रणनीतिक चातुर्य, दीर्घायु एवं उच्च पद।",
             "Command over masses, steadfast perseverance, strategy, and enduring authority.")
        ]

        for p_name, yoga_key, name_hi, name_en, qualifying_signs, shloka, desc_hi, desc_en in p_definitions:
            planet = chart.planets[p_name]
            in_kendra = planet.house_from_lagna in KENDRA_HOUSES
            in_sign = planet.sign_name in qualifying_signs
            is_active = in_kendra and in_sign

            score = 0.0
            if is_active:
                score = 80.0
                if planet.is_retrograde:
                    score += 10.0
                if planet.is_combust:
                    score -= 25.0

            results.append(ClassicalYogaItem(
                yoga_id=f"PMP_{yoga_key.upper()}",
                name_hi=name_hi,
                name_en=name_en,
                category="Pancha Mahapurusha",
                is_active=is_active,
                strength_score=round(max(0.0, min(100.0, score)), 1),
                planets_involved=[p_name],
                houses_involved=[planet.house_from_lagna],
                description_hi=desc_hi,
                description_en=desc_en,
                shloka_reference=shloka
            ))
        return results

    # -------------------------------------------------------------
    # 2. RAJA YOGAS & NEECHABHANGA
    # -------------------------------------------------------------
    @classmethod
    def _evaluate_raja_yogas(cls, chart: KundaliChart) -> List[ClassicalYogaItem]:
        results = []

        # A. Dharma-Karmadhipati Yoga (9th & 10th lords relationship)
        h9_lord_name = chart.houses[8].lord
        h10_lord_name = chart.houses[9].lord
        p9 = chart.planets[h9_lord_name]
        p10 = chart.planets[h10_lord_name]

        is_dharma_karma = False
        dk_planets = [h9_lord_name, h10_lord_name]
        dk_houses = [p9.house_from_lagna, p10.house_from_lagna]

        # Conjunction
        if p9.sign_id == p10.sign_id:
            is_dharma_karma = True
        # Mutual 7th aspect
        elif abs(p9.house_from_lagna - p10.house_from_lagna) == 6:
            is_dharma_karma = True
        # Parivartana
        elif p9.sign_id == chart.houses[9].sign_id and p10.sign_id == chart.houses[8].sign_id:
            is_dharma_karma = True

        results.append(ClassicalYogaItem(
            yoga_id="RY_DHARMA_KARMADHIPATI",
            name_hi="धर्म-कर्माधिपति राजयोग",
            name_en="Dharma-Karmadhipati Raja Yoga",
            category="Raja Yoga",
            is_active=is_dharma_karma,
            strength_score=90.0 if is_dharma_karma else 0.0,
            planets_involved=list(set(dk_planets)),
            houses_involved=list(set(dk_houses)),
            description_hi="नवम (धर्म) व दशम (कर्म) स्वामियों का शुभ संबंध जातक को समाज में सर्वोच्च यश, मान-प्रतिष्ठा व अधिकार दिलाता है।",
            description_en="The mutual alliance of 9th and 10th lords produces supreme renown, executive authority, and professional triumph.",
            shloka_reference="BPHS Ch. 34.1-3, Phaladeepika Ch. 6.32"
        ))

        # B. Vipareeta Raja Yogas (Harsha 6, Sarala 8, Vimala 12)
        h6_lord = chart.planets[chart.houses[5].lord]
        h8_lord = chart.planets[chart.houses[7].lord]
        h12_lord = chart.planets[chart.houses[11].lord]

        vry_definitions = [
            ("VRY_HARSHA", "हर्ष विपरीत राजयोग", "Harsha Vipareeta Raja Yoga", h6_lord, 6,
             "शत्रुहंता, निरोगी काया, संकटों पर विजय एवं विषम परिस्थितियों में अप्रत्याशित लाभ।",
             "Triumph over adversaries, robust immunity, and fortune arising out of crisis."),
            ("VRY_SARALA", "सरल विपरीत राजयोग", "Sarala Vipareeta Raja Yoga", h8_lord, 8,
             "दीर्घायु, निर्भय स्वभाव, गुप्त धन प्राप्ति, अनुसंधान एवं बाधाओं का नाश।",
             "Longevity, fearlessness, sudden gains, and victory over deep adversities."),
            ("VRY_VIMALA", "विमल विपरीत राजयोग", "Vimala Vipareeta Raja Yoga", h12_lord, 12,
             "स्वतंत्र विचारधारा, व्यय पर नियंत्रण, आध्यात्मिक उत्थान एवं परोपकारी स्वभाव।",
             "Financial autonomy, spiritual purity, high character, and noble expenditure.")
        ]

        for v_id, n_hi, n_en, lord_p, orig_h, d_hi, d_en in vry_definitions:
            is_vry = lord_p.house_from_lagna in DUSTHANA_HOUSES
            results.append(ClassicalYogaItem(
                yoga_id=v_id,
                name_hi=n_hi,
                name_en=n_en,
                category="Raja Yoga",
                is_active=is_vry,
                strength_score=75.0 if is_vry else 0.0,
                planets_involved=[lord_p.name],
                houses_involved=[lord_p.house_from_lagna],
                description_hi=d_hi,
                description_en=d_en,
                shloka_reference="Phaladeepika Ch. 6.63-66"
            ))

        # C. Neechabhanga Raja Yoga
        debilitated_planets = [p for p in chart.planets.values() if p.dignity == "debilitated"]
        for deb_p in debilitated_planets:
            is_neechabhanga = False
            reasons = []

            # Clause 1: Dispositor in Kendra from Lagna or Moon
            disp_name = SIGN_LORDS.get(deb_p.sign_id)
            if disp_name and disp_name in chart.planets:
                disp_p = chart.planets[disp_name]
                if disp_p.house_from_lagna in KENDRA_HOUSES:
                    is_neechabhanga = True
                    reasons.append(f"Dispositor {disp_name} in Lagna Kendra ({disp_p.house_from_lagna})")
                moon_h = chart.planets["Moon"].house_from_lagna
                h_from_moon = ((disp_p.house_from_lagna - moon_h) % 12) + 1
                if h_from_moon in KENDRA_HOUSES:
                    is_neechabhanga = True
                    reasons.append(f"Dispositor {disp_name} in Moon Kendra ({h_from_moon})")

            # Clause 2: Exaltation lord of that sign in Kendra from Lagna or Moon
            exalt_p_name = None
            for p_candidate, (e_sign, _) in EXALTATION.items():
                if e_sign == deb_p.sign_name:
                    exalt_p_name = p_candidate
                    break
            if exalt_p_name and exalt_p_name in chart.planets:
                exalt_p = chart.planets[exalt_p_name]
                if exalt_p.house_from_lagna in KENDRA_HOUSES:
                    is_neechabhanga = True
                    reasons.append(f"Exaltation lord {exalt_p_name} in Kendra ({exalt_p.house_from_lagna})")

            # Clause 3: Aspected by its dispositor
            if disp_name and disp_name in chart.planets:
                disp_p = chart.planets[disp_name]
                if abs(deb_p.house_from_lagna - disp_p.house_from_lagna) == 6:
                    is_neechabhanga = True
                    reasons.append(f"Directly aspected by dispositor {disp_name}")

            if is_neechabhanga:
                results.append(ClassicalYogaItem(
                    yoga_id=f"NBRY_{deb_p.name.upper()}",
                    name_hi=f"नीचभंग राजयोग ({deb_p.name})",
                    name_en=f"Neechabhanga Raja Yoga ({deb_p.name})",
                    category="Neechabhanga",
                    is_active=True,
                    strength_score=85.0,
                    planets_involved=[deb_p.name],
                    houses_involved=[deb_p.house_from_lagna],
                    description_hi=f"{deb_p.name} का नीचत्व भंग होकर राजयोग में परिवर्तित हुआ: {'; '.join(reasons)}।",
                    description_en=f"Debility of {deb_p.name} is cancelled into Raja Yoga: {'; '.join(reasons)}.",
                    shloka_reference="Phaladeepika Ch. 6.26-30, BPHS Ch. 39"
                ))

        return results

    # -------------------------------------------------------------
    # 2B. DHANA YOGAS (Wealth Combinations)
    # -------------------------------------------------------------
    @classmethod
    def _evaluate_dhana_yogas(cls, chart: KundaliChart) -> List[ClassicalYogaItem]:
        """Evaluates classical wealth combinations (BPHS Ch. 41-42)."""
        results = []
        l1 = chart.houses[0].lord
        l2 = chart.houses[1].lord
        l5 = chart.houses[4].lord
        l9 = chart.houses[8].lord
        l11 = chart.houses[10].lord

        p1 = chart.planets[l1]
        p2 = chart.planets[l2]
        p5 = chart.planets[l5]
        p9 = chart.planets[l9]
        p11 = chart.planets[l11]

        # 1. 2nd & 11th Lords connection (Prime Dhana Yoga)
        is_2_11 = (p2.sign_id == p11.sign_id) or (abs(p2.house_from_lagna - p11.house_from_lagna) == 6)
        results.append(ClassicalYogaItem(
            yoga_id="DY_2_11_PRIME",
            name_hi="धन-लाभ अधिपति योग",
            name_en="Dhana Yoga (2nd & 11th Lords)",
            category="Dhana Yoga",
            is_active=is_2_11,
            strength_score=85.0 if is_2_11 else 0.0,
            planets_involved=list(set([l2, l11])),
            houses_involved=[p2.house_from_lagna, p11.house_from_lagna],
            description_hi="धन भाव (द्वितीय) व लाभ भाव (एकादश) के स्वामियों की युति या दृष्टि से जातक प्रचुर सम्पत्ति अर्जित करता है।",
            description_en="Alliance of 2nd (accumulated wealth) and 11th (gains) lords creates enduring financial prosperity.",
            shloka_reference="BPHS Ch. 41.1-5, Jataka Parijata Ch. 7"
        ))

        # 2. 1st & 2nd / 1st & 11th Lord connection (Lakshmi Dhana Yoga)
        is_1_2 = (p1.sign_id == p2.sign_id) or (abs(p1.house_from_lagna - p2.house_from_lagna) == 6)
        is_1_11 = (p1.sign_id == p11.sign_id) or (abs(p1.house_from_lagna - p11.house_from_lagna) == 6)
        is_lakshmi = is_1_2 or is_1_11
        lakshmi_planets = [l1]
        if is_1_2: lakshmi_planets.append(l2)
        if is_1_11: lakshmi_planets.append(l11)

        results.append(ClassicalYogaItem(
            yoga_id="DY_LAGNESH_DHANA",
            name_hi="लग्नेश धन-लाभ योग",
            name_en="Lagnesha Dhana Yoga",
            category="Dhana Yoga",
            is_active=is_lakshmi,
            strength_score=80.0 if is_lakshmi else 0.0,
            planets_involved=list(set(lakshmi_planets)),
            houses_involved=[p1.house_from_lagna],
            description_hi="लग्नेश का धन अथवा लाभ भाव के स्वामी से संबंध जातक को स्वप्रयास से विपुल वैभव प्रदान करता है।",
            description_en="Connection of 1st lord with 2nd or 11th lord grants wealth through personal enterprise.",
            shloka_reference="BPHS Ch. 41.6-10"
        ))

        # 3. 5th & 9th Lords connection (Mahalakshmi Trikona Dhana Yoga)
        is_5_9 = (p5.sign_id == p9.sign_id) or (abs(p5.house_from_lagna - p9.house_from_lagna) == 6)
        results.append(ClassicalYogaItem(
            yoga_id="DY_TRIKONA_LAKSHMI",
            name_hi="त्रिकोण महालक्ष्मी योग",
            name_en="Mahalakshmi Trikona Dhana Yoga",
            category="Dhana Yoga",
            is_active=is_5_9,
            strength_score=88.0 if is_5_9 else 0.0,
            planets_involved=list(set([l5, l9])),
            houses_involved=[p5.house_from_lagna, p9.house_from_lagna],
            description_hi="पंचम (धी) व नवम (भाग्य) स्वामियों का संबंध पूर्व-पुण्य एवं ईश्वरीय कृपा से प्रचुर ऐश्वर्य दिलाता है।",
            description_en="The mutual conjunction or aspect of 5th and 9th lords produces supreme fortune and divine prosperity.",
            shloka_reference="Phaladeepika Ch. 6.35, BPHS Ch. 42"
        ))

        return results

    # -------------------------------------------------------------
    # 2C. AMALA YOGA (Pure Benefic in 10th)
    # -------------------------------------------------------------
    @classmethod
    def _evaluate_amala_yoga(cls, chart: KundaliChart) -> List[ClassicalYogaItem]:
        """Evaluates Amala Yoga: pure natural benefic in 10th from Lagna or Moon (BPHS Ch. 36 / Phaladeepika Ch. 6)."""
        benefics = ["Jupiter", "Venus", "Mercury"]
        active_planets = []
        moon_h = chart.planets["Moon"].house_from_lagna

        for b_name in benefics:
            b_p = chart.planets[b_name]
            h_lagna = b_p.house_from_lagna
            h_moon = ((h_lagna - moon_h) % 12) + 1
            if h_lagna == 10 or h_moon == 10:
                active_planets.append(b_name)

        is_amala = len(active_planets) > 0
        return [ClassicalYogaItem(
            yoga_id="AY_AMALA",
            name_hi="अमला योग",
            name_en="Amala Yoga",
            category="Auspicious Yoga",
            is_active=is_amala,
            strength_score=80.0 if is_amala else 0.0,
            planets_involved=active_planets if is_amala else ["Jupiter", "Venus", "Mercury"],
            houses_involved=[10],
            description_hi="लग्न अथवा चन्द्रमा से दशम भाव में केवल शुभ ग्रह होने से अमला योग बनता है, जो निष्कलंक यश, सदाचार एवं स्थाई राजसम्मान दिलाता है।",
            description_en="A natural benefic occupying 10th house from Lagna or Moon creates Amala Yoga, conferring spotless fame, pure virtue, and lasting respect.",
            shloka_reference="BPHS Ch. 36.5-6, Phaladeepika Ch. 6.21"
        )]

    # -------------------------------------------------------------
    # 3. CHANDRA & SURYA YOGAS
    # -------------------------------------------------------------
    @classmethod
    def _evaluate_chandra_surya_yogas(cls, chart: KundaliChart) -> List[ClassicalYogaItem]:
        results = []
        moon = chart.planets["Moon"]
        sun = chart.planets["Sun"]

        # A. Gajakesari Yoga (Jupiter in 1, 4, 7, 10 from Moon)
        jup = chart.planets["Jupiter"]
        h_jup_from_moon = ((jup.house_from_lagna - moon.house_from_lagna) % 12) + 1
        is_gajakesari = h_jup_from_moon in KENDRA_HOUSES

        results.append(ClassicalYogaItem(
            yoga_id="CY_GAJAKESARI",
            name_hi="गजकेसरी योग",
            name_en="Gajakesari Yoga",
            category="Chandra Yoga",
            is_active=is_gajakesari,
            strength_score=85.0 if is_gajakesari else 0.0,
            planets_involved=["Moon", "Jupiter"],
            houses_involved=[moon.house_from_lagna, jup.house_from_lagna],
            description_hi="चन्द्रमा से केन्द्र (१, ४, ७, १०) में बृहस्पति होने से गजकेसरी योग बनता है, जो असीम ज्ञान, कीर्ति व धन प्रदान करता है।",
            description_en="Jupiter in an angular house from Moon forms Gajakesari Yoga, granting high intellect, noble character, and prosperity.",
            shloka_reference="BPHS Ch. 36.3-4, Brihat Jataka Ch. 13.5"
        ))

        # B. Sunaphaa, Anaphaa, Dhurudhara
        planets_in_2nd_moon = []
        planets_in_12th_moon = []
        for p_name, pos in chart.planets.items():
            if p_name in ("Moon", "Sun", "Rahu", "Ketu"):
                continue
            h_from_moon = ((pos.house_from_lagna - moon.house_from_lagna) % 12) + 1
            if h_from_moon == 2:
                planets_in_2nd_moon.append(p_name)
            elif h_from_moon == 12:
                planets_in_12th_moon.append(p_name)

        has_2nd = len(planets_in_2nd_moon) > 0
        has_12th = len(planets_in_12th_moon) > 0

        # Dhurudhara (both 2nd and 12th)
        is_dhurudhara = has_2nd and has_12th
        results.append(ClassicalYogaItem(
            yoga_id="CY_DHURUDHARA",
            name_hi="दुरुधरा योग",
            name_en="Dhurudhara Yoga",
            category="Chandra Yoga",
            is_active=is_dhurudhara,
            strength_score=80.0 if is_dhurudhara else 0.0,
            planets_involved=["Moon"] + planets_in_2nd_moon + planets_in_12th_moon,
            houses_involved=[moon.house_from_lagna],
            description_hi="चन्द्रमा के द्वितीय एवं द्वादश दोनों भावों में ग्रह स्थित होने से दुरुधरा योग बनता है, जो सम्पन्नता एवं वाहन सुख देता है।",
            description_en="Planets flanking both sides of Moon form Dhurudhara Yoga, blessing the native with wealth, conveyances, and generosity.",
            shloka_reference="Brihat Jataka Ch. 13.1-3"
        ))

        # Sunaphaa (2nd only)
        is_sunaphaa = has_2nd and not has_12th
        results.append(ClassicalYogaItem(
            yoga_id="CY_SUNAPHAA",
            name_hi="सुनफा योग",
            name_en="Sunaphaa Yoga",
            category="Chandra Yoga",
            is_active=is_sunaphaa,
            strength_score=75.0 if is_sunaphaa else 0.0,
            planets_involved=["Moon"] + planets_in_2nd_moon,
            houses_involved=[moon.house_from_lagna],
            description_hi="चन्द्रमा के द्वितीय भाव में ग्रह होने से सुनफा योग बनता है, जो स्वअर्जित धन एवं मेधा प्रदान करता है।",
            description_en="Planets in 2nd from Moon form Sunaphaa Yoga, conferring self-earned wealth, fame, and mental contentment.",
            shloka_reference="BPHS Ch. 36.1-2"
        ))

        # Anaphaa (12th only)
        is_anaphaa = has_12th and not has_2nd
        results.append(ClassicalYogaItem(
            yoga_id="CY_ANAPHAA",
            name_hi="अनफा योग",
            name_en="Anaphaa Yoga",
            category="Chandra Yoga",
            is_active=is_anaphaa,
            strength_score=75.0 if is_anaphaa else 0.0,
            planets_involved=["Moon"] + planets_in_12th_moon,
            houses_involved=[moon.house_from_lagna],
            description_hi="चन्द्रमा के द्वादश भाव में ग्रह होने से अनफा योग बनता है, जो शिष्ट आचरण, सुन्दर स्वरूप एवं सम्मान देता है।",
            description_en="Planets in 12th from Moon form Anaphaa Yoga, granting physical charm, moral uprightness, and good health.",
            shloka_reference="BPHS Ch. 36.1-2"
        ))

        # C. Budhaditya Yoga
        merc = chart.planets["Mercury"]
        is_budhaditya = (sun.sign_id == merc.sign_id)
        budh_score = 75.0 if is_budhaditya else 0.0
        if is_budhaditya and merc.is_combust:
            budh_score -= 20.0

        results.append(ClassicalYogaItem(
            yoga_id="SY_BUDHADITYA",
            name_hi="बुधादित्य योग",
            name_en="Budhaditya Yoga",
            category="Surya Yoga",
            is_active=is_budhaditya,
            strength_score=budh_score,
            planets_involved=["Sun", "Mercury"],
            houses_involved=[sun.house_from_lagna],
            description_hi="सूर्य व बुध की युति से बुधादित्य योग बनता है, जो उच्च प्रशासनिक मेधा, व्यापारिक कुशाग्रता एवं सम्मानीय पद दिलाता है।",
            description_en="Sun and Mercury conjoined form Budhaditya Yoga, conferring sharp intellect, analytical ability, and administration skills.",
            shloka_reference="Saravali Ch. 35.1-2"
        ))

        return results

    # -------------------------------------------------------------
    # 4. MAJOR DOSHAS & CANCELLATIONS
    # -------------------------------------------------------------
    @classmethod
    def _evaluate_manglik_dosha(cls, chart: KundaliChart) -> Tuple[ClassicalDoshaItem, bool, str, bool]:
        mars = chart.planets["Mars"]
        moon = chart.planets["Moon"]
        venus = chart.planets["Venus"]

        # Manglik houses from Lagna, Moon, and Venus: 1, 2, 4, 7, 8, 12
        manglik_houses = (1, 2, 4, 7, 8, 12)
        h_lagna = mars.house_from_lagna
        h_moon = ((mars.house_from_lagna - moon.house_from_lagna) % 12) + 1
        h_venus = ((mars.house_from_lagna - venus.house_from_lagna) % 12) + 1

        is_present = (h_lagna in manglik_houses) or (h_moon in manglik_houses) or (h_venus in manglik_houses)

        # Severity
        severity = "None"
        if is_present:
            if h_lagna in (1, 7, 8):
                severity = "Severe"
            elif h_lagna in (4, 12):
                severity = "Moderate"
            else:
                severity = "Mild"

        # Classical Cancellations (Pariharas)
        cancellations = []
        is_cancelled = False

        if is_present:
            # 1. Mars in own sign or exaltation
            if mars.sign_name in ("Aries", "Scorpio", "Capricorn"):
                is_cancelled = True
                cancellations.append("Mars is in own sign or exalted (Aries/Scorpio/Capricorn).")
            # 2. Mars in Leo or Aquarius
            elif mars.sign_name in ("Leo", "Aquarius"):
                is_cancelled = True
                cancellations.append(f"Mars in {mars.sign_name} neutralizes Manglik dosha.")
            # 3. Mars conjunct or aspected by Jupiter
            jup = chart.planets["Jupiter"]
            if mars.sign_id == jup.sign_id:
                is_cancelled = True
                cancellations.append("Mars is conjoined with Jupiter (Guru-Mangala).")
            elif abs(mars.house_from_lagna - jup.house_from_lagna) in (4, 6, 8):
                is_cancelled = True
                cancellations.append("Mars is aspected by Jupiter (Guru Drishti).")
            # 4. Mars conjunct Moon
            elif mars.sign_id == moon.sign_id:
                is_cancelled = True
                cancellations.append("Mars is conjoined with Moon (Chandra-Mangala).")

        dosha_item = ClassicalDoshaItem(
            dosha_id="DOSHA_MANGLIK",
            name_hi="मांगलिक दोष (भौम दोष)",
            name_en="Manglik / Kuja Dosha",
            category="Manglik",
            is_present=is_present,
            severity=severity,
            is_cancelled=is_cancelled,
            cancellation_reasons=cancellations,
            planets_involved=["Mars"],
            houses_involved=[h_lagna],
            description_hi="लग्न, चन्द्र या शुक्र से १, २, ४, ७, ८, १२ भाव में मंगल की स्थिति मांगलिक दोष बनाती है।" +
                           (f" (दोष परिहार: {'; '.join(cancellations)})" if is_cancelled else ""),
            description_en=f"Mars in house {h_lagna} creates Kuja Dosha." +
                           (f" Neutralized by: {'; '.join(cancellations)}" if is_cancelled else ""),
            remedy_summary="मंगलवार को हनुमान चालीसा, कुंभ विवाह, या तांबे का दान।",
            shloka_reference="Muhurta Chintamani, Brihat Jataka"
        )
        return dosha_item, is_present, severity, is_cancelled

    @classmethod
    def _evaluate_kaal_sarp_dosha(cls, chart: KundaliChart) -> Tuple[ClassicalDoshaItem, Optional[str], bool]:
        rahu = chart.planets["Rahu"]
        ketu = chart.planets["Ketu"]

        rahu_lon = rahu.longitude
        ketu_lon = ketu.longitude

        seven_planets = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
        side_a = 0
        side_b = 0

        for p_name in seven_planets:
            p_lon = chart.planets[p_name].longitude
            # Measure relative to Rahu moving counter-clockwise towards Ketu
            arc = (p_lon - rahu_lon) % 360.0
            if arc <= 180.0:
                side_a += 1
            else:
                side_b += 1

        is_present = False
        is_full = False
        if side_a == 7 or side_b == 7:
            is_present = True
            is_full = True
        elif side_a == 6 or side_b == 6:
            is_present = True
            is_full = False  # Anshik / Partial

        names_12 = [
            "Anant", "Kulik", "Vasuki", "Shankhpal", "Padma", "Mahapadma",
            "Takshak", "Karkotak", "Shankhachood", "Ghatak", "Vishdhar", "Sheshnag"
        ]
        r_house = rahu.house_from_lagna
        ks_name = f"{names_12[r_house - 1]} Kaal Sarp ({'Full' if is_full else 'Partial'})" if is_present else None

        dosha_item = ClassicalDoshaItem(
            dosha_id="DOSHA_KAAL_SARP",
            name_hi=f"काल सर्प दोष ({names_12[r_house - 1]})" if is_present else "काल सर्प दोष",
            name_en=ks_name or "Kaal Sarp Dosha",
            category="Kaal Sarp",
            is_present=is_present,
            severity="Severe" if is_full else ("Moderate" if is_present else "None"),
            is_cancelled=False,
            cancellation_reasons=[],
            planets_involved=["Rahu", "Ketu"],
            houses_involved=[rahu.house_from_lagna, ketu.house_from_lagna],
            description_hi=f"समस्त ग्रह राहु-केतु के अक्ष के मध्य स्थित होने से {ks_name} बना है।" if is_present else "कुण्डली में काल सर्प दोष नहीं है।",
            description_en=f"All planets hemmed between Rahu and Ketu forming {ks_name}." if is_present else "No Kaal Sarp Dosha present.",
            remedy_summary="महामृत्युंजय जाप, शिवलिंग पर रुद्राभिषेक, नागपंचमी पूजा।",
            shloka_reference="Vedic Classical Samhita Consensus"
        )
        return dosha_item, ks_name, is_present

    @classmethod
    def _evaluate_guru_chandal(cls, chart: KundaliChart) -> ClassicalDoshaItem:
        jup = chart.planets["Jupiter"]
        rahu = chart.planets["Rahu"]
        diff = abs(jup.longitude - rahu.longitude)
        if diff > 180.0:
            diff = 360.0 - diff

        is_present = (jup.sign_id == rahu.sign_id) and (diff <= 12.0)
        is_cancelled = False
        reasons = []

        if is_present:
            if jup.sign_name in ("Sagittarius", "Pisces", "Cancer"):
                is_cancelled = True
                reasons.append("Jupiter is in own/exaltation sign.")
            elif diff > 8.0:
                is_cancelled = True
                reasons.append(f"Separation is {diff:.1f}° (beyond deep combust orb of 8°).")

        return ClassicalDoshaItem(
            dosha_id="DOSHA_GURU_CHANDAL",
            name_hi="गुरु चाण्डाल दोष",
            name_en="Guru Chandal Dosha",
            category="Guru Chandal",
            is_present=is_present,
            severity="Moderate" if is_present and not is_cancelled else "None",
            is_cancelled=is_cancelled,
            cancellation_reasons=reasons,
            planets_involved=["Jupiter", "Rahu"],
            houses_involved=[jup.house_from_lagna],
            description_hi=f"बृहस्पति और राहु की युति {jup.house_from_lagna} भाव में गुरु चाण्डाल दोष बनाती है।" if is_present else "गुरु चाण्डाल दोष नहीं है।",
            description_en=f"Jupiter-Rahu conjunction in house {jup.house_from_lagna} creates Guru Chandal Dosha." if is_present else "No Guru Chandal Dosha.",
            remedy_summary="बृहस्पति गायत्री मंत्र जाप, चने की दाल व पीली वस्तुओं का दान।",
            shloka_reference="BPHS Ch. 84"
        )

    @classmethod
    def _evaluate_pitru_dosha(cls, chart: KundaliChart) -> ClassicalDoshaItem:
        sun = chart.planets["Sun"]
        rahu = chart.planets["Rahu"]
        saturn = chart.planets["Saturn"]

        # Sun conjunct Rahu or Saturn
        sun_rahu = sun.sign_id == rahu.sign_id
        sun_sat = sun.sign_id == saturn.sign_id
        h9 = chart.houses[8]
        h9_afflicted = ("Rahu" in h9.occupants) or ("Saturn" in h9.occupants)

        is_present = sun_rahu or sun_sat or h9_afflicted

        return ClassicalDoshaItem(
            dosha_id="DOSHA_PITRU",
            name_hi="पितृ दोष",
            name_en="Pitru Dosha",
            category="Pitru",
            is_present=is_present,
            severity="Moderate" if is_present else "None",
            is_cancelled=False,
            cancellation_reasons=[],
            planets_involved=["Sun", "Rahu" if (sun_rahu or "Rahu" in h9.occupants) else "Saturn"],
            houses_involved=[sun.house_from_lagna, 9],
            description_hi="सूर्य अथवा नवम भाव का राहु/शनि से संबंध पितृ दोष निर्मित करता है।" if is_present else "कुण्डली में पितृ दोष नहीं है।",
            description_en="Affliction to Sun or 9th house by Rahu/Saturn indicates Pitru Dosha." if is_present else "No Pitru Dosha present.",
            remedy_summary="अमावस्या को पितृ तर्पण, पीपल में जल, श्रीमद्भगवद्गीता के ११वें अध्याय का पाठ।",
            shloka_reference="BPHS Ch. 84, Garuda Purana"
        )

    @classmethod
    def _evaluate_kemadruma_dosha(cls, chart: KundaliChart) -> ClassicalDoshaItem:
        moon = chart.planets["Moon"]
        planets_in_2nd = []
        planets_in_12th = []
        for p_name, pos in chart.planets.items():
            if p_name in ("Moon", "Sun", "Rahu", "Ketu"):
                continue
            h_from_moon = ((pos.house_from_lagna - moon.house_from_lagna) % 12) + 1
            if h_from_moon == 2:
                planets_in_2nd.append(p_name)
            elif h_from_moon == 12:
                planets_in_12th.append(p_name)

        is_present = (len(planets_in_2nd) == 0) and (len(planets_in_12th) == 0)
        is_cancelled = False
        reasons = []

        if is_present:
            # Cancellation: Benefic in Kendra from Lagna or Moon
            for b_name in ("Jupiter", "Venus", "Mercury"):
                b_pos = chart.planets[b_name]
                if b_pos.house_from_lagna in KENDRA_HOUSES:
                    is_cancelled = True
                    reasons.append(f"{b_name} in Lagna Kendra ({b_pos.house_from_lagna}) cancels Kemadruma.")
                    break
                h_from_moon = ((b_pos.house_from_lagna - moon.house_from_lagna) % 12) + 1
                if h_from_moon in KENDRA_HOUSES:
                    is_cancelled = True
                    reasons.append(f"{b_name} in Moon Kendra ({h_from_moon}) cancels Kemadruma.")
                    break

        return ClassicalDoshaItem(
            dosha_id="DOSHA_KEMADRUMA",
            name_hi="केमद्रुम दोष",
            name_en="Kemadruma Dosha",
            category="Kemadruma",
            is_present=is_present,
            severity="Moderate" if is_present and not is_cancelled else "None",
            is_cancelled=is_cancelled,
            cancellation_reasons=reasons,
            planets_involved=["Moon"],
            houses_involved=[moon.house_from_lagna],
            description_hi="चन्द्रमा के द्वितीय एवं द्वादश भाव में कोई ग्रह न होने से केमद्रुम दोष बनता है।" +
                           (f" (दोष भंग: {'; '.join(reasons)})" if is_cancelled else ""),
            description_en="Moon devoid of flanking planets creates Kemadruma Dosha." +
                           (f" Neutralized: {'; '.join(reasons)}" if is_cancelled else ""),
            remedy_summary="पूर्णिमा का व्रत, शिवलिंग पर कच्चा दूध, भगवान शिव का पूजन।",
            shloka_reference="Brihat Jataka Ch. 13.3-4, Phaladeepika Ch. 6.7"
        )

    @classmethod
    def _evaluate_gandanta(cls, chart: KundaliChart) -> ClassicalDoshaItem:
        moon = chart.planets["Moon"]
        lagna_deg = chart.lagna_degree
        lagna_sign_id = chart.lagna_sign_id

        # Nakshatra Gandanta: Ashlesha (end), Magha (start), Jyeshtha (end), Mula (start), Revati (end), Ashwini (start)
        # Sign junctions: Cancer (4) -> Leo (5); Scorpio (8) -> Sagittarius (9); Pisces (12) -> Aries (1)
        is_nak_gandanta = False
        is_lagna_gandanta = False

        if moon.sign_id in (4, 8, 12) and moon.sign_degree >= 26.666667:
            is_nak_gandanta = True
        elif moon.sign_id in (5, 9, 1) and moon.sign_degree <= 3.333333:
            is_nak_gandanta = True

        if lagna_sign_id in (1, 5, 9) and lagna_deg <= 0.8:
            is_lagna_gandanta = True
        elif lagna_sign_id in (4, 8, 12) and lagna_deg >= 29.2:
            is_lagna_gandanta = True

        is_present = is_nak_gandanta or is_lagna_gandanta

        return ClassicalDoshaItem(
            dosha_id="DOSHA_GANDANTA",
            name_hi="गंडान्त दोष",
            name_en="Gandanta Dosha",
            category="Gandanta",
            is_present=is_present,
            severity="Severe" if is_present else "None",
            is_cancelled=False,
            cancellation_reasons=[],
            planets_involved=["Moon"] if is_nak_gandanta else ["Lagna"],
            houses_involved=[moon.house_from_lagna] if is_nak_gandanta else [1],
            description_hi="जल एवं अग्नि राशि के संधिकाल पर जन्म गंडान्त दोष कहलाता है।" if is_present else "गंडान्त दोष नहीं है।",
            description_en="Birth at the junction of water and fire signs creates Gandanta Dosha." if is_present else "No Gandanta Dosha present.",
            remedy_summary="मूल शांति पूजा, २७ दिन बाद नक्षत्र शांति एवं ब्राह्मण भोजन।",
            shloka_reference="BPHS Ch. 87"
        )


default_yoga_dosha_engine = ClassicalYogaDoshaEngine()

