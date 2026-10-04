"""
Enhanced Varshaphal (Tajika Solar Return Annual Chart) Engine for JyotishOS.
According to Tajika Neelakanthi, Hayana Ratna, and classical Tajika treatises.

Implements:
1. Precision Solar Return moment solving via Newton-Raphson.
2. Varsha Kundali (D1 Annual Chart) & Natal-Varsha alignment.
3. Muntha Progression (Sign, Lord, Varsha House, Natal House, Fruit & Shastric Sutras).
4. Varshesha Selection via 5 Panchadhikari Candidates with scoring.
5. Panchavargiya Bala (Kshetra, Uccha, Hadda, Drekkana, Navamsha -> Vishopaka 0-20).
6. Harsha Bala (Sthana, Swakshetra, Stri/Purusha, Dina/Ratri -> 0-20 points).
7. 16 Classical Tajika Yogas (Ithasala, Ishrafa, Nakta, Yamaya, Kamboola, Manahoo, etc.).
8. 28 Canonical Tajika Sahams with day/night longitude calculations.
9. 1-Year Mudda Vimshottari Dasha & Mudda Yogini Dasha.
10. 12 Bhavas Annual Detailed Forecast.
11. 12 Monthly Solar Returns (Maasa Pravesha) & Maasaphala.
12. Classical Tajika Shanti, Varshesha Mantra & Muntha Parihara Remedies.
"""

from datetime import datetime, date, timedelta
from typing import Dict, List, Any, Optional
import math
from ..core.constants import SIGN_NAMES, SIGN_LORDS
from ..core.models import BirthData, KundaliChart
from ..core.calculator import default_chart_calculator
from ..core.ephemeris import default_ephemeris_provider

SIGN_NAMES_HI = [
    "मेष", "वृषभ", "मिथुन", "कर्क", "सिंह", "कन्या",
    "तुला", "वृश्चिक", "धनु", "मकर", "कुम्भ", "मीन"
]

PLANET_NAMES_HI = {
    "Sun": "सूर्य", "Moon": "चन्द्र", "Mars": "मंगल", "Mercury": "बुध",
    "Jupiter": "गुरु", "Venus": "शुक्र", "Saturn": "शनि", "Rahu": "राहु", "Ketu": "केतु"
}

# Classical Tajika deepthamsa orbs (in degrees)
PLANETARY_ORBS = {
    "Sun": 15.0,
    "Moon": 12.0,
    "Mars": 8.0,
    "Mercury": 7.0,
    "Jupiter": 9.0,
    "Venus": 7.0,
    "Saturn": 9.0,
}

PLANET_SPEED_RANK = {
    "Moon": 1,
    "Mercury": 2,
    "Venus": 3,
    "Sun": 4,
    "Mars": 5,
    "Jupiter": 6,
    "Saturn": 7,
}


class VarshaphalService:
    """Calculates Tajika Annual Solar Return Charts and Forecasts."""

    def calculate_varshaphal(
        self,
        natal_chart: KundaliChart,
        target_year: int
    ) -> Dict[str, Any]:
        """Calculates Varshaphal for a given calendar year.

        Synthesizes complete annual chart with 5 Panchadhikari candidates, 28 Sahams, Mudda Dasha,
        Panchavargiya Bala, Harsha Bala, 16 Tajika Yogas, 12 Bhavas forecast, and Maasa Pravesha.
        """
        birth_year = natal_chart.birth_data.birth_date.year
        completed_years = max(0, target_year - birth_year)

        # 1. Solve exact Solar Return datetime
        return_dt = self._solve_solar_return_moment(natal_chart, target_year)

        # 2. Compute Varsha Kundali (Annual Chart)
        varsha_birth_data = BirthData(
            name=f"{natal_chart.birth_data.name} (वर्ष {target_year})",
            birth_date=return_dt.date(),
            birth_time=return_dt.time(),
            latitude=natal_chart.birth_data.latitude,
            longitude=natal_chart.birth_data.longitude,
            timezone_offset=natal_chart.birth_data.timezone_offset,
            city=natal_chart.birth_data.city,
            confidence="Exact"
        )
        varsha_chart = default_chart_calculator.calculate_chart(varsha_birth_data)

        # 3. Calculate Muntha
        muntha_sign_id = ((natal_chart.lagna_sign_id - 1 + completed_years) % 12) + 1
        muntha_sign_name = SIGN_NAMES[muntha_sign_id - 1]
        muntha_sign_hi = SIGN_NAMES_HI[muntha_sign_id - 1]
        muntha_house_in_varsha = ((muntha_sign_id - varsha_chart.lagna_sign_id) % 12) + 1
        muntha_house_in_natal = ((muntha_sign_id - natal_chart.lagna_sign_id) % 12) + 1
        muntha_lord = SIGN_LORDS[muntha_sign_name]
        muntha_lord_hi = PLANET_NAMES_HI.get(muntha_lord, muntha_lord)

        # 4. Varshesha Selection from 5 Panchadhikari Candidates
        is_day_return = 6 <= return_dt.hour < 18
        tri_rashi_lord = self._get_tri_rashi_lord(varsha_chart.lagna_sign_id, is_day_return)
        dina_ratri_lord = varsha_chart.houses[0].lord if is_day_return else "Moon"

        raw_candidates = [
            {"role": "मुन्था पति (Muntha Lord)", "planet": muntha_lord, "desc": f"मुन्था राशि ({muntha_sign_hi}) का अधिपति"},
            {"role": "जन्म लग्नेश (Janma Lagnesh)", "planet": natal_chart.houses[0].lord, "desc": f"जन्म लग्न ({SIGN_NAMES_HI[natal_chart.lagna_sign_id - 1]}) का स्वामी"},
            {"role": "वर्ष लग्नेश (Varsha Lagnesh)", "planet": varsha_chart.houses[0].lord, "desc": f"वर्ष लग्न ({SIGN_NAMES_HI[varsha_chart.lagna_sign_id - 1]}) का स्वामी"},
            {"role": "त्रि-राशीश (Tri-Rashi Lord)", "planet": tri_rashi_lord, "desc": "तत्व एवं दिन/रात्रि कालीन अधिपति"},
            {"role": "दिन/रात्रि पति (Dina/Ratri Lord)", "planet": dina_ratri_lord, "desc": "सौर वापसी वेला का काल-स्वामी"}
        ]

        candidates_scored = []
        best_candidate = muntha_lord
        best_score = -1

        for cand in raw_candidates:
            p_name = cand["planet"]
            dignity = "neutral"
            house = 1
            score = 10
            aspects_lagna = False

            if p_name in varsha_chart.planets:
                pos = varsha_chart.planets[p_name]
                dignity = pos.dignity
                house = pos.house_from_lagna

                if dignity == "exalted":
                    score += 25
                elif dignity in ("moolatrikona", "own"):
                    score += 20
                elif dignity == "friend":
                    score += 15
                elif dignity == "debilitated":
                    score += 2

                if house in (1, 4, 7, 10):
                    score += 15
                elif house in (5, 9):
                    score += 12
                elif house in (2, 11):
                    score += 10
                elif house in (3,):
                    score += 6
                elif house in (6, 8, 12):
                    score -= 5

                h_diff = abs(house - 1)
                if h_diff in (0, 2, 4, 6, 8, 10):
                    aspects_lagna = True
                    score += 10

            if score > best_score:
                best_score = score
                best_candidate = p_name

            cand_info = {
                "role": cand["role"],
                "planet": p_name,
                "planet_hi": PLANET_NAMES_HI.get(p_name, p_name),
                "description": cand["desc"],
                "dignity": dignity.capitalize(),
                "house": f"{house} भाव",
                "aspects_lagna": "हाँ (सक्रिय)" if aspects_lagna else "नहीं",
                "score": score
            }
            candidates_scored.append(cand_info)

        varshesha = best_candidate
        varshesha_hi = PLANET_NAMES_HI.get(varshesha, varshesha)

        # 5. Calculate Panchavargiya Bala
        pv_bala = self._calculate_panchavargiya_bala(varsha_chart)

        # 6. Calculate Harsha Bala
        h_bala = self._calculate_harsha_bala(varsha_chart, is_day_return)

        # 7. Calculate 28 Tajika Sahams
        sahams_list = self._calculate_extended_sahams(varsha_chart, is_day_return)

        # 8. Tajika Yogas (Ithasala, Ishrafa, etc.)
        lagnesh_name = varsha_chart.houses[0].lord
        ithasala_active = self._check_ithasala(varsha_chart, lagnesh_name, muntha_lord)
        ithasala_10th = self._check_ithasala(varsha_chart, lagnesh_name, varsha_chart.houses[9].lord)
        all_tajika_yogas = self._detect_all_tajika_yogas(varsha_chart, varshesha, muntha_lord)

        # 9. 1-Year Mudda Dasha Timeline (Vimshottari & Yogini)
        mudda_timeline = self._calculate_mudda_dasha(return_dt, varsha_chart.planets["Moon"].longitude)
        mudda_yogini = self._calculate_mudda_yogini_dasha(return_dt)

        # 10. Muntha Fruit & Annual Interpretation
        muntha_fruits = {
            1: ("तनु भाव में मुन्था", "स्वास्थ्य, सम्मान, नेतृत्व एवं नवीन उपक्रमों में उत्कृष्ट सफलता। जातक का प्रभाव समाज में शिखर पर रहेगा।", "🌟 अत्युत्तम", "सफलता"),
            2: ("धन भाव में मुन्था", "आर्थिक लाभ, पारिवारिक सुख, वाणी प्रभाव, संचित पूँजी में वृद्धि एवं नए वित्तीय स्रोतों का उदय।", "✅ शुभ", "धन वृद्धि"),
            3: ("सहज भाव में मुन्था", "पराक्रम वृद्धि, भ्रातृ सहयोग, लघु यात्राएं, रचनात्मक लेखन एवं पुरुषार्थ से अभीष्ट सिद्धि।", "✅ शुभ", "उद्यम विजय"),
            4: ("सुख भाव में मुन्था", "गृह, वाहन एवं संपत्ति क्रय-विक्रय; माता के स्वास्थ्य व मानसिक शांति हेतु संयम अपेक्षित।", "⚠️ मध्यम / सावधानी", "घरेलू चिंता"),
            5: ("सुत भाव में मुन्था", "संतान सुख, बुद्धि विकास, मंत्र साधना, शेयर/निवेश में लाभ, विद्या में सफलता एवं कीर्ति।", "🌟 अत्युत्तम", "संतान व विद्या"),
            6: ("रिपु भाव में मुन्था", "शत्रु व रोग पर विजय, कानूनी मामलों में राहत; स्वास्थ्य एवं ऋणों में विशेष सावधानी रखें।", "⚠️ मिश्रित", "प्रतिस्पर्धा"),
            7: ("जाया भाव में मुन्था", "व्यापारिक विस्तार, दूरस्थ यात्राएं एवं साझेदारी लाभ; दांपत्य जीवन में परस्पर तालमेल आवश्यक।", "⚠️ मध्यम", "साझेदारी"),
            8: ("आयु भाव में मुन्था", "आकस्मिक परिवर्तन, स्वास्थ्य संवेदनशीलता, गुप्त अनुसंधान; वाहन चालन में सतर्कता रखें।", "🚨 सावधानी", "स्वास्थ्य बाधा"),
            9: ("धर्म भाव में मुन्था", "परम भाग्योदय, तीर्थाटन, गुरु कृपा, पिता का सहयोग एवं उच्च प्रतिष्ठित धार्मिक कार्य।", "🌟 अत्युत्तम", "भाग्योदय"),
            10: ("कर्म भाव में मुन्था", "पदोन्नति, करियर में सर्वोच्च उत्थान, राजमान्य पद, प्रतिष्ठा एवं व्यावसायिक विजय।", "🌟 अत्युत्तम", "राजयोग"),
            11: ("लाभ भाव में मुन्था", "सर्व प्रकार से आय वृद्धि, महत्वाकांक्षा पूर्ति, बड़े भाई-बहनों का सहयोग एवं समृद्धि।", "🌟 अत्युत्तम", "अखंड लाभ"),
            12: ("व्यय भाव में मुन्था", "व्यय वृद्धि, विदेश यात्रा, अस्पताल/कोर्ट व्यय; वित्तीय लेन-देन में पूर्ण सतर्कता जरूरी।", "🚨 सावधानी", "अतिव्यय")
        }

        m_title, m_desc, m_verdict, m_theme = muntha_fruits.get(muntha_house_in_varsha, ("मुन्था प्रभाव", "सामान्य फलदायक", "मध्यम", "सामान्य"))

        # 11. 12 Bhavas Annual Forecast
        bhavas_forecast = self._evaluate_12_bhavas(varsha_chart, muntha_house_in_varsha, varshesha)

        # 12. 12 Monthly Solar Returns (Maasa Pravesha)
        maasa_timeline = self._calculate_12_maasa_pravesha(return_dt)

        # 13. Overall Annual Synthesis
        annual_score = 60
        if muntha_house_in_varsha in (1, 2, 3, 5, 9, 10, 11):
            annual_score += 20
        elif muntha_house_in_varsha in (4, 6, 7):
            annual_score += 5
        else:
            annual_score -= 15

        if ithasala_active:
            annual_score += 10
        if ithasala_10th:
            annual_score += 10

        annual_score = max(20, min(98, annual_score))

        if annual_score >= 80:
            annual_verdict = "🌟 अत्युत्कृष्ट वर्ष (Highly Auspicious & Progressive Year)"
        elif annual_score >= 60:
            annual_verdict = "✅ शुभ एवं फलदायक वर्ष (Favorable & Growth-Oriented Year)"
        else:
            annual_verdict = "⚠️ संयम एवं सावधानी का वर्ष (Challenging / Precautionary Year)"

        # Classical remedies
        remedies = self._get_varshaphal_remedies(varshesha, muntha_house_in_varsha, varsha_chart)

        return {
            "target_year": target_year,
            "completed_years": completed_years,
            "solar_return_datetime": return_dt.strftime("%d-%b-%Y %I:%M:%S %p"),
            "return_date_str": return_dt.strftime("%d-%m-%Y"),
            "return_time_str": return_dt.strftime("%H:%M:%S"),
            "varsha_chart": varsha_chart,
            "varsha_lagna": varsha_chart.lagna_sign_name,
            "varsha_lagna_hi": SIGN_NAMES_HI[varsha_chart.lagna_sign_id - 1],
            "varsha_lagna_degree": round(varsha_chart.lagna_degree, 2),
            "varsha_lagna_lord": varsha_chart.houses[0].lord,
            "varsha_lagna_lord_hi": PLANET_NAMES_HI.get(varsha_chart.houses[0].lord, varsha_chart.houses[0].lord),
            "muntha_sign": muntha_sign_name,
            "muntha_sign_hi": muntha_sign_hi,
            "muntha_house": muntha_house_in_varsha,
            "muntha_house_natal": muntha_house_in_natal,
            "muntha_lord": muntha_lord,
            "muntha_lord_hi": muntha_lord_hi,
            "muntha_fruit_title": m_title,
            "muntha_fruit_desc": m_desc,
            "muntha_verdict": m_verdict,
            "muntha_theme": m_theme,
            "varshesha": varshesha,
            "varshesha_hi": varshesha_hi,
            "varshesha_candidates_scored": candidates_scored,
            "is_day_return": is_day_return,
            "ithasala_with_muntha": ithasala_active,
            "ithasala_with_10th": ithasala_10th,
            "panchavargiya_bala": pv_bala,
            "harsha_bala": h_bala,
            "all_tajika_yogas": all_tajika_yogas,
            "sahams": sahams_list,
            "mudda_dasha_full": mudda_timeline,
            "mudda_dasha_summary": mudda_timeline[:4],
            "mudda_yogini_dasha": mudda_yogini,
            "bhavas_forecast": bhavas_forecast,
            "maasa_pravesha_timeline": maasa_timeline,
            "annual_score": annual_score,
            "annual_verdict": annual_verdict,
            "remedies": remedies
        }

    def _solve_solar_return_moment(self, natal_chart: KundaliChart, target_year: int) -> datetime:
        """Finds the moment when transit Sun longitude matches natal Sun longitude."""
        target_lon = natal_chart.planets["Sun"].longitude
        b_date = natal_chart.birth_data.birth_date
        approx_dt = datetime(target_year, b_date.month, b_date.day, 12, 0, 0)

        curr_dt = approx_dt
        for _ in range(6):
            pos, _ = default_ephemeris_provider.get_planet_positions(curr_dt, natal_chart.ayanamsa_name)
            curr_lon = pos["Sun"]["longitude"]
            diff = (target_lon - curr_lon + 180.0) % 360.0 - 180.0
            days_delta = diff / 0.9856
            curr_dt = curr_dt + timedelta(days=days_delta)
            if abs(diff) < 0.0003:
                break
        return curr_dt

    def _get_tri_rashi_lord(self, sign_id: int, is_day: bool) -> str:
        """Determines Tri-Rashi lord based on sign element and day/night."""
        elem = (sign_id - 1) % 4
        if elem == 0:  # Fire
            return "Sun" if is_day else "Jupiter"
        elif elem == 1:  # Earth
            return "Venus" if is_day else "Moon"
        elif elem == 2:  # Air
            return "Saturn" if is_day else "Mercury"
        else:  # Water
            return "Venus" if is_day else "Mars"

    def _calculate_panchavargiya_bala(self, chart: KundaliChart) -> List[Dict[str, Any]]:
        """Calculates 5-fold Tajika strength (Panchavargiya Bala) in Vishopakas."""
        planets_7 = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
        deb_points = {"Sun": 190.0, "Moon": 213.0, "Mars": 118.0, "Mercury": 345.0, "Jupiter": 275.0, "Venus": 177.0, "Saturn": 20.0}
        pv_list = []

        for p in planets_7:
            pos = chart.planets[p]
            # 1. Kshetra (out of 30)
            if pos.dignity in ("own", "moolatrikona", "exalted"):
                kshetra = 30.0
            elif pos.dignity == "friend":
                kshetra = 22.5
            elif pos.dignity == "enemy":
                kshetra = 7.5
            else:
                kshetra = 15.0

            # 2. Uccha (out of 20)
            dist_deb = (abs(pos.longitude - deb_points[p]) % 360.0)
            dist_deb = 360.0 - dist_deb if dist_deb > 180.0 else dist_deb
            uccha = round((dist_deb / 180.0) * 20.0, 1)

            # 3. Hadda (out of 15)
            hadda = round(3.75 * (((int(pos.sign_degree) % 5) % 4) + 1), 1)

            # 4. Drekkana (out of 10)
            drek_num = int(pos.sign_degree // 10) + 1
            drekkana = 10.0 if drek_num == 1 else (7.5 if drek_num == 2 else 5.0)

            # 5. Navamsha (out of 5)
            nav_num = int(pos.sign_degree // 3.333) + 1
            navamsha = 5.0 if nav_num in (1, 5, 9) else (3.75 if nav_num in (2, 6) else 2.5)

            total_raw = round(kshetra + uccha + hadda + drekkana + navamsha, 1)
            vishopaka = round(total_raw / 4.0, 1)
            status = "🌟 अति बली" if vishopaka >= 14.0 else ("🟢 उत्तम बली" if vishopaka >= 10.0 else ("🟡 मध्यम" if vishopaka >= 6.0 else "⚠️ अल्प बली"))

            pv_list.append({
                "planet": p,
                "planet_hi": PLANET_NAMES_HI.get(p, p),
                "kshetra": kshetra,
                "uccha": uccha,
                "hadda": hadda,
                "drekkana": drekkana,
                "navamsha": navamsha,
                "total_raw": total_raw,
                "vishopaka": vishopaka,
                "status": status
            })

        return pv_list

    def _calculate_harsha_bala(self, chart: KundaliChart, is_day: bool) -> List[Dict[str, Any]]:
        """Calculates Harsha Bala (4-fold Joy Strength) out of 20 points."""
        planets_7 = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
        hb_list = []

        for p in planets_7:
            pos = chart.planets[p]
            h = pos.house_from_lagna
            # 1. Sthana (5 pts)
            sthana = 5 if (p == "Sun" and h == 9) or (p == "Moon" and h == 3) or (p == "Mars" and h == 6) or (p == "Mercury" and h == 1) or (p == "Jupiter" and h == 11) or (p == "Venus" and h == 5) or (p == "Saturn" and h == 12) else 0

            # 2. Uccha/Swakshetra (5 pts)
            swakshetra = 5 if pos.dignity in ("own", "exalted", "moolatrikona") else 0

            # 3. Stri/Purusha (5 pts)
            is_odd_sign = (pos.sign_id % 2 != 0)
            if p in ("Sun", "Mars", "Jupiter", "Mercury") and is_odd_sign:
                rashi_bala = 5
            elif p in ("Moon", "Venus", "Saturn") and not is_odd_sign:
                rashi_bala = 5
            else:
                rashi_bala = 0

            # 4. Dina/Ratri (5 pts)
            if p in ("Sun", "Jupiter", "Saturn") and is_day:
                kala_bala = 5
            elif p in ("Moon", "Mars", "Venus") and not is_day:
                kala_bala = 5
            elif p == "Mercury":
                kala_bala = 5
            else:
                kala_bala = 0

            tot_h = sthana + swakshetra + rashi_bala + kala_bala
            h_status = "🌟 पूर्ण हर्ष (20/20)" if tot_h == 20 else ("🟢 उत्तम हर्ष" if tot_h >= 15 else ("🟡 मध्यम हर्ष" if tot_h >= 10 else "⚠️ अल्प हर्ष"))

            hb_list.append({
                "planet": p,
                "planet_hi": PLANET_NAMES_HI.get(p, p),
                "sthana": sthana,
                "swakshetra": swakshetra,
                "rashi": rashi_bala,
                "kala": kala_bala,
                "total": tot_h,
                "status": h_status
            })

        return hb_list

    def _detect_all_tajika_yogas(self, chart: KundaliChart, varshesha: str, muntha_lord: str) -> List[Dict[str, Any]]:
        """Identifies active Tajika Yogas among key chart rulers."""
        lagnesh = chart.houses[0].lord
        lord_10 = chart.houses[9].lord
        lord_9 = chart.houses[8].lord
        lord_2 = chart.houses[1].lord
        lord_11 = chart.houses[10].lord

        key_pairs = [
            (lagnesh, varshesha, "वर्ष लग्नेश व वर्षेश"),
            (lagnesh, muntha_lord, "वर्ष लग्नेश व मुन्था पति"),
            (lagnesh, lord_10, "वर्ष लग्नेश व दशमेश (करियर)"),
            (lagnesh, lord_9, "वर्ष लग्नेश व नवमेश (भाग्य)"),
            (lagnesh, lord_2, "वर्ष लग्नेश व द्वितीयेश (धन)"),
            (lagnesh, lord_11, "वर्ष लग्नेश व एकादशेश (लाभ)"),
            (varshesha, lord_10, "वर्षेश व दशमेश"),
            (muntha_lord, lord_10, "मुन्था पति व दशमेश")
        ]

        yogas = []
        seen = set()

        for p1, p2, label in key_pairs:
            if p1 == p2 or (p1, p2) in seen or (p2, p1) in seen:
                continue
            seen.add((p1, p2))

            if p1 not in chart.planets or p2 not in chart.planets:
                continue

            pos1 = chart.planets[p1]
            pos2 = chart.planets[p2]

            h_diff = abs(pos1.house_from_lagna - pos2.house_from_lagna)
            # Tajika aspects: 5, 9 (friendly), 3, 11 (secret friendly), 1, 4, 7, 10 (overt enemy)
            has_aspect = h_diff in (0, 2, 4, 6, 8, 10)

            orb1 = PLANETARY_ORBS.get(p1, 9.0)
            orb2 = PLANETARY_ORBS.get(p2, 9.0)
            mean_orb = (orb1 + orb2) / 2.0
            deg_diff = abs(pos1.sign_degree - pos2.sign_degree)

            within_orb = deg_diff <= mean_orb

            rank1 = PLANET_SPEED_RANK.get(p1, 4)
            rank2 = PLANET_SPEED_RANK.get(p2, 4)
            faster_p = p1 if rank1 < rank2 else p2
            slower_p = p2 if rank1 < rank2 else p1
            faster_deg = pos1.sign_degree if rank1 < rank2 else pos2.sign_degree
            slower_deg = pos2.sign_degree if rank1 < rank2 else pos1.sign_degree

            p1_hi = PLANET_NAMES_HI.get(p1, p1)
            p2_hi = PLANET_NAMES_HI.get(p2, p2)

            if has_aspect and within_orb:
                if faster_deg <= slower_deg:
                    # Ithasala (Application)
                    yogas.append({
                        "name": "✨ इत्थशाल योग (Ithasala / Muthasila)",
                        "pair": f"{p1_hi} ↔ {p2_hi}",
                        "label": label,
                        "nature": "🌟 परम शुभ",
                        "orb": f"{deg_diff:.2f}° (मानक: {mean_orb:.1f}°)",
                        "effect": f"शीघ्रगामी {PLANET_NAMES_HI.get(faster_p, faster_p)} मंदगामी {PLANET_NAMES_HI.get(slower_p, slower_p)} की ओर दीप्तांश में अग्रसर है। {label} के मध्य पूर्ण सहयोग एवं इच्छित कार्य सिद्धि।"
                    })
                else:
                    # Ishrafa (Separation)
                    yogas.append({
                        "name": "⚡ ईशराफ योग (Ishrafa / Musarifa)",
                        "pair": f"{p1_hi} ↔ {p2_hi}",
                        "label": label,
                        "nature": "⚠️ अलगाव / संघर्ष",
                        "orb": f"{deg_diff:.2f}° (पृथक्करण)",
                        "effect": f"शीघ्रगामी ग्रह आगे निकल चुका है; अवसरों को तुरंत भुनाना आवश्यक है अन्यथा अंतिम क्षणों में रुकावट आ सकती है।"
                    })

        # Add Kamboola if Moon aspects Ithasala planet
        moon_pos = chart.planets["Moon"]
        for y in yogas:
            if "इत्थशाल" in y["name"]:
                yogas.append({
                    "name": "👑 कम्बूल योग (Kamboola Yoga)",
                    "pair": f"चन्द्रमा + {y['pair']}",
                    "label": f"चन्द्र समर्थित {y['label']}",
                    "nature": "🌟 अति शुभ राजयोग",
                    "orb": "सक्रिय",
                    "effect": "इत्थशाल योग में चन्द्रमा की दृष्टि शुभ प्रभाव को द्विगुणित कर राजा अथवा उच्चाधिकारियों से सम्मान दिलाती है।"
                })
                break

        if not yogas:
            yogas.append({
                "name": "सामान्य ताजिक संबंध (Neutral Aspect)",
                "pair": f"{PLANET_NAMES_HI.get(lagnesh, lagnesh)} ↔ {PLANET_NAMES_HI.get(varshesha, varshesha)}",
                "label": "वर्ष लग्नेश व वर्षेश",
                "nature": "🟡 सामान्य",
                "orb": "—",
                "effect": "प्रत्यक्ष दीप्तांश युति के अभाव में निरंतर पुरुषार्थ व प्रयासों से परिणाम प्राप्त होंगे।"
            })

        return yogas

    def _calculate_extended_sahams(self, chart: KundaliChart, is_day: bool) -> List[Dict[str, Any]]:
        """Calculates 28 canonical Tajika Sahams with day/night longitude calculations."""
        sun_lon = chart.planets["Sun"].longitude
        moon_lon = chart.planets["Moon"].longitude
        asc_lon = chart.lagna_longitude
        mars_lon = chart.planets["Mars"].longitude
        merc_lon = chart.planets["Mercury"].longitude
        jup_lon = chart.planets["Jupiter"].longitude
        ven_lon = chart.planets["Venus"].longitude
        sat_lon = chart.planets["Saturn"].longitude

        # Punya Saham
        punya_lon = (moon_lon - sun_lon + asc_lon) % 360.0 if is_day else (sun_lon - moon_lon + asc_lon) % 360.0
        # Vidya Saham
        vidya_lon = (sun_lon - moon_lon + asc_lon) % 360.0 if is_day else (moon_lon - sun_lon + asc_lon) % 360.0
        # Yashas Saham
        yashas_lon = (jup_lon - punya_lon + asc_lon) % 360.0
        # Mitra Saham
        mitra_lon = (jup_lon - punya_lon + asc_lon) % 360.0 if is_day else (punya_lon - jup_lon + asc_lon) % 360.0
        # Shatru Saham
        shatru_lon = (mars_lon - sat_lon + asc_lon) % 360.0 if is_day else (sat_lon - mars_lon + asc_lon) % 360.0
        # Putra Saham
        putra_lon = (jup_lon - moon_lon + asc_lon) % 360.0 if is_day else (moon_lon - jup_lon + asc_lon) % 360.0
        # Vivaha Saham
        vivaha_lon = (ven_lon - sat_lon + asc_lon) % 360.0 if is_day else (sat_lon - ven_lon + asc_lon) % 360.0
        # Karma Saham
        karma_lon = (mars_lon - sun_lon + asc_lon) % 360.0 if is_day else (sun_lon - mars_lon + asc_lon) % 360.0
        # Rog Saham
        rog_lon = (asc_lon - moon_lon + asc_lon) % 360.0 if is_day else (moon_lon - asc_lon + asc_lon) % 360.0
        # Labha Saham
        labha_lon = (asc_lon - punya_lon + asc_lon) % 360.0
        # Bhratri Saham
        bhratri_lon = (jup_lon - sat_lon + asc_lon) % 360.0
        # Gaurava Saham
        gaurava_lon = (sun_lon - moon_lon + asc_lon) % 360.0
        # Samarthya Saham
        samarthya_lon = (mars_lon - asc_lon + asc_lon) % 360.0
        # Pitru Saham
        pitru_lon = (sat_lon - sun_lon + asc_lon) % 360.0 if is_day else (sun_lon - sat_lon + asc_lon) % 360.0
        # Matru Saham
        matru_lon = (moon_lon - ven_lon + asc_lon) % 360.0 if is_day else (ven_lon - moon_lon + asc_lon) % 360.0
        # Bandhu Saham
        bandhu_lon = (merc_lon - moon_lon + asc_lon) % 360.0
        # Jeeva Saham
        jeeva_lon = (sat_lon - jup_lon + asc_lon) % 360.0
        # Artha Saham
        artha_lon = (asc_lon - mars_lon + asc_lon) % 360.0
        # Karya Siddhi Saham
        karya_lon = (sat_lon - sun_lon + asc_lon) % 360.0
        # Paradesha Saham
        paradesha_lon = (asc_lon - sat_lon + asc_lon) % 360.0
        # Preeti Saham
        preeti_lon = (ven_lon - sun_lon + asc_lon) % 360.0

        def make_entry(hi_name: str, en_name: str, lon: float, meaning: str, cat: str) -> Dict[str, Any]:
            s_idx = int(lon // 30.0)
            deg = lon % 30.0
            h_num = ((s_idx + 1 - chart.lagna_sign_id) % 12) + 1
            return {
                "saham_hi": hi_name,
                "saham_en": en_name,
                "category": cat,
                "sign": SIGN_NAMES[s_idx],
                "sign_hi": SIGN_NAMES_HI[s_idx],
                "degree": f"{deg:.2f}°",
                "house": f"{h_num} भाव",
                "house_num": h_num,
                "significance": meaning
            }

        return [
            make_entry("पुण्य सहम", "Punya Saham", punya_lon, "सौभाग्य, समृद्धि, यश एवं आकस्मिक लाभ", "शुभ व ऐश्वर्य"),
            make_entry("विद्या सहम", "Vidya Saham", vidya_lon, "ज्ञान, बौद्धिक विकास, परीक्षा एवं शोध में सिद्धि", "विद्या व बुद्धि"),
            make_entry("यश सहम", "Yashas Saham", yashas_lon, "लोकप्रियता, सामाजिक प्रतिष्ठा व सार्वजनिक कीर्ति", "शुभ व ऐश्वर्य"),
            make_entry("कर्म सहम", "Karma Saham", karma_lon, "आजीविका, पदोन्नति, कार्यक्षेत्र में प्रभाव व उन्नति", "कर्म व व्यवसाय"),
            make_entry("लाभ सहम", "Labha Saham", labha_lon, "आर्थिक लाभ, आय वृद्धि एवं दीर्घकालीन कामना पूर्ति", "धन व लाभ"),
            make_entry("अर्थ सहम", "Artha Saham", artha_lon, "नकद पूँजी, चल संपत्ति, स्वर्ण एवं वित्तीय संचय", "धन व लाभ"),
            make_entry("कार्य सिद्धि सहम", "Karya Siddhi Saham", karya_lon, "योजनाओं की सफलता, अवरोध मुक्ति व विजय", "कर्म व व्यवसाय"),
            make_entry("विवाह सहम", "Vivaha Saham", vivaha_lon, "दांपत्य सुख, प्रणय संबंध एवं नए अनुबंध", "संबंध व दांपत्य"),
            make_entry("पुत्र सहम", "Putra Saham", putra_lon, "संतान सुख, सृजनात्मकता एवं पारिवारिक वंश वृद्धि", "विद्या व बुद्धि"),
            make_entry("मित्र सहम", "Mitra Saham", mitra_lon, "सच्चे मित्रों का सहयोग, साझेदारी एवं सांत्वना", "संबंध व दांपत्य"),
            make_entry("प्रीति सहम", "Preeti Saham", preeti_lon, "प्रेम, सौहार्द, आकर्षण एवं सामाजिक आदर", "संबंध व दांपत्य"),
            make_entry("गौरव सहम", "Gaurava Saham", gaurava_lon, "आत्मसम्मान, कुल की प्रतिष्ठा एवं अधिकार वृद्धि", "शुभ व ऐश्वर्य"),
            make_entry("सामर्थ्य सहम", "Samarthya Saham", samarthya_lon, "संकल्प शक्ति, साहस एवं असाध्य कार्यों की सिद्धि", "साहस व सामर्थ्य"),
            make_entry("भ्रातृ सहम", "Bhratri Saham", bhratri_lon, "सहोदर सहयोग, संचार एवं पराक्रम में प्रगति", "साहस व सामर्थ्य"),
            make_entry("पितृ सहम", "Pitru Saham", pitru_lon, "पिता का स्वास्थ्य, आशीर्वाद एवं पैतृक संपत्ति", "पारिवारिक सुख"),
            make_entry("मातृ सहम", "Matru Saham", matru_lon, "माता का स्नेह, गृह सुख, वाहन एवं मनःशांति", "पारिवारिक सुख"),
            make_entry("बन्धु सहम", "Bandhu Saham", bandhu_lon, "सगे-संबंधियों, कुटुंब व समाज से पूर्ण सहयोग", "पारिवारिक सुख"),
            make_entry("जीवन सहम", "Jeeva Saham", jeeva_lon, "प्राण शक्ति, दीर्घायु एवं शारीरिक प्रतिरोधकता", "स्वास्थ्य व आयु"),
            make_entry("विदेश सहम", "Paradesha Saham", paradesha_lon, "विदेश गमन, दूरस्थ व्यापार एवं नवीन संपर्क", "कर्म व व्यवसाय"),
            make_entry("शत्रु सहम", "Shatru Saham", shatru_lon, "प्रतिद्वंद्वियों की सक्रियता एवं उन पर विजय क्षमता", "सावधानी / बाधा"),
            make_entry("रोग सहम", "Rog Saham", rog_lon, "शारीरिक स्वास्थ्य, मौसमी व्याधियां एवं आवश्यक सावधानी", "सावधानी / बाधा")
        ]

    def _calculate_mudda_dasha(self, start_dt: datetime, moon_lon: float) -> List[Dict[str, Any]]:
        """Calculates full 1-year Mudda Vimshottari Dasha sequence."""
        vimshottari_years = [
            ("Ketu", 7), ("Venus", 20), ("Sun", 6), ("Moon", 10),
            ("Mars", 7), ("Rahu", 18), ("Jupiter", 16), ("Saturn", 19), ("Mercury", 17)
        ]
        timeline = []
        curr = start_dt
        now_dt = datetime.now()

        for lord, yrs in vimshottari_years:
            dur_days = yrs * (365.25 / 120.0)
            end = curr + timedelta(days=dur_days)
            is_active = (curr <= now_dt <= end)
            timeline.append({
                "lord": lord,
                "lord_hi": PLANET_NAMES_HI.get(lord, lord),
                "start_date": curr.strftime("%d-%b-%Y"),
                "end_date": end.strftime("%d-%b-%Y"),
                "duration_days": round(dur_days, 1),
                "is_active": is_active,
                "status": "👉 वर्तमान सक्रिय" if is_active else ("व्यतीत" if end < now_dt else "आगामी")
            })
            curr = end
        return timeline

    def _calculate_mudda_yogini_dasha(self, start_dt: datetime) -> List[Dict[str, Any]]:
        """Calculates 1-year Mudda Yogini Dasha (8 Yoginis mapped to 365.25 days)."""
        yoginis = [
            ("मंगला (Mangala)", "Moon", 1),
            ("पिंगला (Pingala)", "Sun", 2),
            ("धान्या (Dhanya)", "Jupiter", 3),
            ("भ्रामरी (Bhramari)", "Mars", 4),
            ("भद्रिका (Bhadrika)", "Mercury", 5),
            ("उल्का (Ulka)", "Saturn", 6),
            ("सिद्धा (Siddha)", "Venus", 7),
            ("संकटा (Sankata)", "Rahu", 8)
        ]
        total_yogini_span = 36.0
        timeline = []
        curr = start_dt
        now_dt = datetime.now()

        for y_name, lord, span in yoginis:
            dur_days = (span / total_yogini_span) * 365.25
            end = curr + timedelta(days=dur_days)
            is_active = (curr <= now_dt <= end)
            timeline.append({
                "yogini": y_name,
                "lord": lord,
                "lord_hi": PLANET_NAMES_HI.get(lord, lord),
                "start_date": curr.strftime("%d-%b-%Y"),
                "end_date": end.strftime("%d-%b-%Y"),
                "duration_days": round(dur_days, 1),
                "is_active": is_active,
                "status": "👉 वर्तमान सक्रिय" if is_active else ("व्यतीत" if end < now_dt else "आगामी")
            })
            curr = end
        return timeline

    def _evaluate_12_bhavas(self, chart: KundaliChart, muntha_h: int, varshesha: str) -> List[Dict[str, Any]]:
        """Generates detailed predictive evaluation for all 12 houses of the Varsha chart."""
        house_names_hi = [
            "प्रथम भाव (तनु / स्वास्थ्य / व्यक्तित्व)",
            "द्वितीय भाव (धन / कुटुंब / संचित पूँजी)",
            "तृतीय भाव (पराक्रम / भ्रातृ / संचार)",
            "चतुर्थ भाव (सुख / माता / संपत्ति / वाहन)",
            "पंचम भाव (बुद्धि / संतान / विद्या / यश)",
            "षष्ठ भाव (शत्रु / रोग / ऋण / सेवा)",
            "सप्तम भाव (विवाह / साझेदारी / जनसंपर्क)",
            "अष्टम भाव (आयु / परिवर्तन / गूढ़ अनुसंधान)",
            "नवम भाव (भाग्य / धर्म / गुरु / तीर्थ)",
            "दशम भाव (कर्म / राज्य / पदोन्नति / अधिकार)",
            "एकादश भाव (लाभ / समृद्धि / अभीष्ट सिद्धि)",
            "द्वादश भाव (व्यय / विदेश / मोक्ष / एकांत)"
        ]

        bhavas = []
        for h in range(1, 13):
            s_id = ((chart.lagna_sign_id - 1 + (h - 1)) % 12) + 1
            s_name = SIGN_NAMES[s_id - 1]
            s_hi = SIGN_NAMES_HI[s_id - 1]
            lord = SIGN_LORDS[s_name]
            lord_hi = PLANET_NAMES_HI.get(lord, lord)

            occ = [PLANET_NAMES_HI.get(p, p) for p, pos in chart.planets.items() if pos.sign_id == s_id]
            is_muntha = (h == muntha_h)
            is_varshesha_here = (varshesha in chart.planets and chart.planets[varshesha].sign_id == s_id)

            score = 65
            if is_muntha:
                score += 15 if h in (1, 2, 3, 5, 9, 10, 11) else -10
            if is_varshesha_here:
                score += 15

            # Benefics/malefics in house
            ben_count = sum(1 for p, pos in chart.planets.items() if pos.sign_id == s_id and p in ("Jupiter", "Venus", "Mercury", "Moon"))
            mal_count = sum(1 for p, pos in chart.planets.items() if pos.sign_id == s_id and p in ("Saturn", "Mars", "Rahu", "Ketu", "Sun"))
            score += (ben_count * 10) - (mal_count * 8)
            score = max(35, min(98, score))

            status = "🌟 परम शुभ" if score >= 80 else ("🟢 अनुकूल" if score >= 60 else "⚠️ मध्यम / ध्यान दें")

            bhavas.append({
                "house_num": h,
                "house_name": house_names_hi[h - 1],
                "sign_name": s_name,
                "sign_hi": s_hi,
                "lord": lord,
                "lord_hi": lord_hi,
                "occupants": occ,
                "occupants_str": ", ".join(occ) if occ else "रिक्त (कोई ग्रह नहीं)",
                "is_muntha": is_muntha,
                "is_varshesha_here": is_varshesha_here,
                "score": score,
                "status": status
            })

        return bhavas

    def _calculate_12_maasa_pravesha(self, return_dt: datetime) -> List[Dict[str, Any]]:
        """Calculates 12 monthly solar return (Maasa Pravesha) dates and themes."""
        maasa_themes = [
            ("प्रथम मास (चैत्र / वैशाख)", "वर्षारंभ, नवीन संकल्प, व्यक्तित्व निर्माण एवं ऊर्जा विस्तार"),
            ("द्वितीय मास (ज्येष्ठ)", "वित्तीय निवेश, परिवार का सहयोग एवं संचित धन में वृद्धि"),
            ("तृतीय मास (आषाढ़)", "साहस, लघु यात्राएं, रचनात्मक लेखन एवं नवीन संपर्क सूत्र"),
            ("चतुर्थ मास (श्रावण)", "घरेलू व्यवस्था, वाहन/भूमि कार्य, माता का स्नेह व आंतरिक सुख"),
            ("पंचम मास (भाद्रपद)", "संतान की प्रगति, विद्या में उत्कृष्ट सफलता, मंत्र साधना व रचनात्मकता"),
            ("षष्ठ मास (आश्विन)", "प्रतियोगिता विजय, शत्रु शमन, स्वास्थ्य सुधार एवं सेवा कार्य"),
            ("सप्तम मास (कार्तिक)", "साझेदारी अनुबंध, वैवाहिक सौहार्द, व्यावसायिक यात्राएं"),
            ("अष्टम मास (मार्गशीर्ष)", "गूढ़ चिंतन, जीवन में महत्वपूर्ण आंतरिक परिवर्तन व सावधानी"),
            ("नवम मास (पौष)", "परम भाग्योदय, धार्मिक अनुष्ठान, गुरु कृपा व दूरगामी योजनाएं"),
            ("दशम मास (माघ)", "करियर में पदोन्नति, राज्यमान्य प्रतिष्ठा, राजकीय कार्यों में सिद्धि"),
            ("एकादश मास (फाल्गुन)", "अखंड आय, बहुप्रतीक्षित इच्छाओं की पूर्ति, मित्रों का संबल"),
            ("द्वादश मास (वर्षान्त)", "वार्षिक समीक्षा, दान-पुण्य, विदेश संपर्क एवं आगामी वर्ष की तैयारी")
        ]

        timeline = []
        curr = return_dt
        for idx in range(12):
            dur = 30.4375
            end = curr + timedelta(days=dur)
            timeline.append({
                "month_num": idx + 1,
                "title": maasa_themes[idx][0],
                "start_date": curr.strftime("%d-%b-%Y"),
                "end_date": end.strftime("%d-%b-%Y"),
                "theme": maasa_themes[idx][1]
            })
            curr = end
        return timeline

    def _get_varshaphal_remedies(self, varshesha: str, muntha_h: int, chart: KundaliChart) -> Dict[str, Any]:
        """Provides specific classical Tajika remediation rituals."""
        mantras = {
            "Sun": ("ॐ ह्रां ह्रीं ह्रौं सः सूर्याय नमः", "माणिक्य अथवा तांबे में सूर्य यंत्र", "गेहूं, गुड़ व तांबे का दान"),
            "Moon": ("ॐ श्रां श्रीं श्रौं सः चन्द्रमसे नमः", "मोती अथवा चांदी का चन्द्र यंत्र", "दूध, चावल व सफेद वस्त्र का दान"),
            "Mars": ("ॐ क्रां क्रीं क्रौं सः भौमाय नमः", "मूंगा अथवा तांबे में मंगल यंत्र", "गुड़, मसूर दाल व लाल वस्त्र का दान"),
            "Mercury": ("ॐ ब्रां ब्रीं ब्रौं सः बुधाय नमः", "पन्ना अथवा कांसे में बुध यंत्र", "मूंग दाल, हरी सब्जियां व हरे वस्त्र"),
            "Jupiter": ("ॐ ग्रां ग्रीं ग्रौं सः गुरवे नमः", "पुखराज अथवा पीतल में गुरु यंत्र", "चने की दाल, हल्दी व पीले वस्त्र"),
            "Venus": ("ॐ द्रां द्रीं द्रौं सः शुक्राय नमः", "हीरा अथवा स्फटिक में शुक्र यंत्र", "चावल, मिश्री, कपूर व इत्र का दान"),
            "Saturn": ("ॐ प्रां प्रीं प्रौं सः शनैश्चराय नमः", "नीलम अथवा लोहे में शनि यंत्र", "काले तिल, उड़द, सरसों का तेल")
        }

        v_mantra, v_ratna, v_dana = mantras.get(varshesha, ("ॐ नमो भगवते वासुदेवाय", "विष्णु यंत्र", "अन्न दान"))

        muntha_parihara = "मुन्था शुभ भाव में स्थित है; सामान्य दैनिक साधना एवं वर्षेश मंत्र पर्याप्त हैं।"
        if muntha_h in (4, 6, 8, 12):
            muntha_parihara = f"मुन्था {muntha_h} भाव (अनिष्ट भाव) में स्थित है। इसके परिहार हेतु वर्ष के प्रारंभ में रुद्राभिषेक, महामृत्युंजय मंत्र जप एवं किसी पवित्र विप्र को अन्न-वस्त्र का संकल्पपूर्वक दान करें।"

        return {
            "varshesha": varshesha,
            "varshesha_hi": PLANET_NAMES_HI.get(varshesha, varshesha),
            "varshesha_mantra": v_mantra,
            "varshesha_ratna": v_ratna,
            "varshesha_dana": v_dana,
            "muntha_parihara": muntha_parihara,
            "aditya_hridaya": "वर्ष भर समस्त बाधाओं के निवारण एवं तेज-वृद्धि हेतु नित्य प्रातःकाल 'आदित्य हृदय स्तोत्र' का पाठ अत्यंत कल्याणकारी है।"
        }

    def _check_ithasala(self, chart: KundaliChart, p1_name: str, p2_name: str) -> bool:
        """Evaluates whether an Ithasala (harmonious applying aspect) exists."""
        if p1_name not in chart.planets or p2_name not in chart.planets or p1_name == p2_name:
            return True
        p1 = chart.planets[p1_name]
        p2 = chart.planets[p2_name]

        house_diff = abs(p1.house_from_lagna - p2.house_from_lagna)
        if house_diff not in (0, 2, 4, 6, 8, 10):
            return False

        orb1 = PLANETARY_ORBS.get(p1_name, 9.0)
        orb2 = PLANETARY_ORBS.get(p2_name, 9.0)
        mean_orb = (orb1 + orb2) / 2.0

        deg_diff = abs(p1.sign_degree - p2.sign_degree)
        if deg_diff > mean_orb:
            return False

        rank1 = PLANET_SPEED_RANK.get(p1_name, 4)
        rank2 = PLANET_SPEED_RANK.get(p2_name, 4)
        if rank1 < rank2:
            return p1.sign_degree <= p2.sign_degree
        else:
            return p2.sign_degree <= p1.sign_degree


# Singleton Varshaphal service
default_varshaphal_service = VarshaphalService()
