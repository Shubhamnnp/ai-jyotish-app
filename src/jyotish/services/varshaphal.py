"""
Varshaphal (Tajika Solar Return Annual Chart) Engine for JyotishOS.
Implements precision Solar Return calculation, Varsha Kundali, Muntha,
Varshesha (Lord of the Year) via 5 Panchadhikari Candidates, 16 Tajika Sahams,
Ithasala/Ishrafa Yogas, 1-Year Mudda Dasha, and cross-module annual synthesis.
"""

from datetime import datetime, date, timedelta
from typing import Dict, List, Any, Optional
from ..core.constants import SIGN_NAMES, SIGN_LORDS
from ..core.models import BirthData, KundaliChart
from ..core.calculator import default_chart_calculator
from ..core.ephemeris import default_ephemeris_provider


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

# Average daily speeds (fast to slow order)
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
        """
        Calculates Varshaphal for a given calendar year.
        Synthesizes complete annual chart with 5 Panchadhikari candidates, 16 Sahams, Mudda Dasha,
        and annual predictions.
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
        muntha_house_in_varsha = ((muntha_sign_id - varsha_chart.lagna_sign_id) % 12) + 1
        muntha_house_in_natal = ((muntha_sign_id - natal_chart.lagna_sign_id) % 12) + 1
        muntha_lord = SIGN_LORDS[muntha_sign_name]

        # 4. Varshesha Selection from 5 Panchadhikari Candidates
        is_day_return = 6 <= return_dt.hour < 18
        tri_rashi_lord = self._get_tri_rashi_lord(varsha_chart.lagna_sign_id, is_day_return)
        dina_ratri_lord = varsha_chart.houses[0].lord if is_day_return else "Moon"

        raw_candidates = [
            {"role": "मुन्था पति (Muntha Lord)", "planet": muntha_lord, "desc": f"मुन्था राशि ({muntha_sign_name}) का स्वामी"},
            {"role": "जन्म लग्नेश (Janma Lagnesh)", "planet": natal_chart.houses[0].lord, "desc": f"मूल जन्म लग्न ({natal_chart.lagna_sign_name}) का स्वामी"},
            {"role": "वर्ष लग्नेश (Varsha Lagnesh)", "planet": varsha_chart.houses[0].lord, "desc": f"वार्षिक लग्न ({varsha_chart.lagna_sign_name}) का स्वामी"},
            {"role": "त्रि-राशीश (Tri-Rashi Lord)", "planet": tri_rashi_lord, "desc": "तत्व एवं दिन/रात्रि कालीन अधिपति"},
            {"role": "दिन/रात्रि पति (Dina/Ratri Lord)", "planet": dina_ratri_lord, "desc": "सौर वापसी वेला का काल-स्वामी"}
        ]

        # Score candidates based on dignity & house in Varsha chart
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
                
                # Dignity bonus
                if dignity == "exalted":
                    score += 25
                elif dignity in ("moolatrikona", "own"):
                    score += 20
                elif dignity == "friend":
                    score += 15
                elif dignity == "debilitated":
                    score += 2

                # House bonus (Kendra/Trikona)
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

                # Aspect to Varsha Lagna
                h_diff = abs(house - 1)
                if h_diff in (0, 2, 4, 6, 8, 10):  # Tajika friendly aspect
                    aspects_lagna = True
                    score += 10

            if score > best_score:
                best_score = score
                best_candidate = p_name

            cand_info = {
                "role": cand["role"],
                "planet": p_name,
                "description": cand["desc"],
                "dignity": dignity.capitalize(),
                "house": f"{house} भाव",
                "aspects_lagna": "हाँ (सक्रिय)" if aspects_lagna else "नहीं",
                "score": score
            }
            candidates_scored.append(cand_info)

        varshesha = best_candidate

        # 5. Calculate 16 Tajika Sahams
        sahams_list = self._calculate_16_sahams(varsha_chart, is_day_return)

        # 6. Tajika Yogas (Ithasala between Varsha Lagnesh and Muntha/10th Lord)
        lagnesh_name = varsha_chart.houses[0].lord
        ithasala_active = self._check_ithasala(varsha_chart, lagnesh_name, muntha_lord)
        ithasala_10th = self._check_ithasala(varsha_chart, lagnesh_name, varsha_chart.houses[9].lord)

        # 7. 1-Year Mudda Dasha Timeline
        mudda_timeline = self._calculate_mudda_dasha(return_dt, varsha_chart.planets["Moon"].longitude)

        # 8. Muntha Fruit & Annual Interpretation
        muntha_fruits = {
            1: ("तनु भाव में मुन्था", "स्वास्थ्य, सम्मान, नेतृत्व एवं नवीन उपक्रमों में उत्कृष्ट सफलता।", "🌟 अत्युत्तम"),
            2: ("धन भाव में मुन्था", "आर्थिक लाभ, पारिवारिक सुख, वाणी प्रभाव एवं संपत्ति अर्जन।", "✅ शुभ"),
            3: ("सहज भाव में मुन्था", "पराक्रम वृद्धि, बंधु सहयोग, लघु यात्राएं एवं कार्य सिद्धि।", "✅ शुभ"),
            4: ("सुख भाव में मुन्था", "गृह, वाहन एवं संपत्ति सुख; मानसिक शांति हेतु संयम अपेक्षित।", "⚠️ मध्यम / सावधानी"),
            5: ("सुत भाव में मुन्था", "संतान सुख, बुद्धि विकास, सट्टा/निवेश में लाभ एवं कीर्ति।", "🌟 अत्युत्तम"),
            6: ("रिपु भाव में मुन्था", "शत्रु व रोग पर विजय, परंतु स्वास्थ्य एवं ऋणों में सावधानी रखें।", "⚠️ मिश्रित"),
            7: ("जाया भाव में मुन्था", "व्यापारिक विस्तार, यात्राएं एवं दांपत्य में तालमेल आवश्यक।", "⚠️ मध्यम"),
            8: ("आयु भाव में मुन्था", "आकस्मिक परिवर्तन, स्वास्थ्य संवेदनशीलता एवं आध्यात्मिक शोध।", "🚨 सावधानी"),
            9: ("धर्म भाव में मुन्था", "भाग्योदय, तीर्थाटन, गुरु कृपा एवं उच्च प्रतिष्ठित सफलता।", "🌟 अत्युत्तम"),
            10: ("कर्म भाव में मुन्था", "पदोन्नति, करियर में सर्वोच्च उत्थान, राजमान्य पद व प्रभुत्व।", "🌟 अत्युत्तम"),
            11: ("लाभ भाव में मुन्था", "सर्व प्रकार से आय वृद्धि, महत्वाकांक्षा पूर्ति एवं आर्थिक उन्नति।", "🌟 अत्युत्तम"),
            12: ("व्यय भाव में मुन्था", "व्यय वृद्धि, विदेश यात्रा, अस्पताल/कोर्ट व्यय; सतर्कता जरूरी।", "🚨 सावधानी")
        }

        m_title, m_desc, m_verdict = muntha_fruits.get(muntha_house_in_varsha, ("मुन्था प्रभाव", "सामान्य फलदायक", "मध्यम"))

        # 9. Overall Annual Synthesis
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

        return {
            "target_year": target_year,
            "completed_years": completed_years,
            "solar_return_datetime": return_dt.strftime("%d-%b-%Y %I:%M:%S %p"),
            "varsha_chart": varsha_chart,
            "varsha_lagna": varsha_chart.lagna_sign_name,
            "varsha_lagna_degree": round(varsha_chart.lagna_degree, 2),
            "muntha_sign": muntha_sign_name,
            "muntha_house": muntha_house_in_varsha,
            "muntha_house_natal": muntha_house_in_natal,
            "muntha_lord": muntha_lord,
            "muntha_fruit_title": m_title,
            "muntha_fruit_desc": m_desc,
            "muntha_verdict": m_verdict,
            "varshesha": varshesha,
            "varshesha_candidates_scored": candidates_scored,
            "is_day_return": is_day_return,
            "ithasala_with_muntha": ithasala_active,
            "ithasala_with_10th": ithasala_10th,
            "sahams": sahams_list,
            "mudda_dasha_full": mudda_timeline,
            "mudda_dasha_summary": mudda_timeline[:4],
            "annual_score": annual_score,
            "annual_verdict": annual_verdict
        }

    def _solve_solar_return_moment(self, natal_chart: KundaliChart, target_year: int) -> datetime:
        """Finds the moment when transit Sun longitude matches natal Sun longitude."""
        target_lon = natal_chart.planets["Sun"].longitude
        b_date = natal_chart.birth_data.birth_date
        approx_dt = datetime(target_year, b_date.month, b_date.day, 12, 0, 0)

        # Iterative Newton-Raphson approximation
        curr_dt = approx_dt
        for _ in range(5):
            pos, _ = default_ephemeris_provider.get_planet_positions(curr_dt, natal_chart.ayanamsa_name)
            curr_lon = pos["Sun"]["longitude"]
            diff = (target_lon - curr_lon + 180.0) % 360.0 - 180.0
            days_delta = diff / 0.9856
            curr_dt = curr_dt + timedelta(days=days_delta)
            if abs(diff) < 0.0005:
                break
        return curr_dt

    def _get_tri_rashi_lord(self, sign_id: int, is_day: bool) -> str:
        """Determines Tri-Rashi lord based on sign element and day/night."""
        elem = (sign_id - 1) % 4
        if elem == 0:  # Fire (Aries, Leo, Sag)
            return "Sun" if is_day else "Jupiter"
        elif elem == 1:  # Earth (Taurus, Virgo, Cap)
            return "Venus" if is_day else "Moon"
        elif elem == 2:  # Air (Gemini, Libra, Aqu)
            return "Saturn" if is_day else "Mercury"
        else:  # Water (Cancer, Scorpio, Pis)
            return "Venus" if is_day else "Mars"

    def _calculate_16_sahams(self, chart: KundaliChart, is_day: bool) -> List[Dict[str, Any]]:
        """Calculates 16 primary Tajika Sahams with sign and bhava."""
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
        # Mitra Saham (Friendship)
        mitra_lon = (jup_lon - punya_lon + asc_lon) % 360.0 if is_day else (punya_lon - jup_lon + asc_lon) % 360.0
        # Shatru Saham (Enemies)
        shatru_lon = (mars_lon - sat_lon + asc_lon) % 360.0 if is_day else (sat_lon - mars_lon + asc_lon) % 360.0
        # Putra Saham (Children)
        putra_lon = (jup_lon - moon_lon + asc_lon) % 360.0 if is_day else (moon_lon - jup_lon + asc_lon) % 360.0
        # Vivaha Saham (Marriage)
        vivaha_lon = (ven_lon - sat_lon + asc_lon) % 360.0 if is_day else (sat_lon - ven_lon + asc_lon) % 360.0
        # Karma Saham (Profession)
        karma_lon = (mars_lon - sun_lon + asc_lon) % 360.0 if is_day else (sun_lon - mars_lon + asc_lon) % 360.0
        # Rog Saham (Health/Illness)
        rog_lon = (asc_lon - moon_lon + asc_lon) % 360.0 if is_day else (moon_lon - asc_lon + asc_lon) % 360.0
        # Labha Saham (Gain/Profit)
        labha_lon = (asc_lon - punya_lon + asc_lon) % 360.0
        # Bhratri Saham (Siblings)
        bhratri_lon = (jup_lon - sat_lon + asc_lon) % 360.0
        # Gaurava Saham (Honor/Respect)
        gaurava_lon = (sun_lon - moon_lon + asc_lon) % 360.0
        # Samarthya Saham (Capability)
        samarthya_lon = (mars_lon - asc_lon + asc_lon) % 360.0
        # Pitru Saham (Father)
        pitru_lon = (sat_lon - sun_lon + asc_lon) % 360.0 if is_day else (sun_lon - sat_lon + asc_lon) % 360.0
        # Matru Saham (Mother)
        matru_lon = (moon_lon - ven_lon + asc_lon) % 360.0 if is_day else (ven_lon - moon_lon + asc_lon) % 360.0
        # Bandhu Saham (Relatives)
        bandhu_lon = (merc_lon - moon_lon + asc_lon) % 360.0

        def make_entry(hi_name: str, en_name: str, lon: float, meaning: str) -> Dict[str, Any]:
            s_idx = int(lon // 30.0)
            deg = lon % 30.0
            h_num = ((s_idx + 1 - chart.lagna_sign_id) % 12) + 1
            return {
                "saham_hi": hi_name,
                "saham_en": en_name,
                "sign": SIGN_NAMES[s_idx],
                "degree": f"{deg:.2f}°",
                "house": f"{h_num} भाव",
                "significance": meaning
            }

        return [
            make_entry("पुण्य सहम", "Punya Saham", punya_lon, "सौभाग्य, समृद्धि, यश एवं शुभ अवसर"),
            make_entry("विद्या सहम", "Vidya Saham", vidya_lon, "ज्ञान, बौद्धिक विकास एवं परीक्षा में सफलता"),
            make_entry("यश सहम", "Yashas Saham", yashas_lon, "लोकप्रियता, सामाजिक प्रतिष्ठा व कीर्ति"),
            make_entry("कर्म सहम", "Karma Saham", karma_lon, "आजीविका, पदोन्नति, व्यापारिक उन्नति"),
            make_entry("लाभ सहम", "Labha Saham", labha_lon, "आर्थिक लाभ, आय वृद्धि एवं मनोकामना पूर्ति"),
            make_entry("विवाह सहम", "Vivaha Saham", vivaha_lon, "दांपत्य सुख, प्रणय संबंध एवं विवाह वार्ता"),
            make_entry("पुत्र सहम", "Putra Saham", putra_lon, "संतान सुख, सृजनात्मकता एवं पारिवारिक वृद्धि"),
            make_entry("मित्र सहम", "Mitra Saham", mitra_lon, "सच्चे मित्रों का सहयोग एवं शुभ साझेदारी"),
            make_entry("शत्रु सहम", "Shatru Saham", shatru_lon, "प्रतिद्वंद्वियों की सक्रियता एवं विजय क्षमता"),
            make_entry("रोग सहम", "Rog Saham", rog_lon, "शारीरिक स्वास्थ्य, रोग प्रतिरोधकता व सावधानी"),
            make_entry("भ्रातृ सहम", "Bhratri Saham", bhratri_lon, "भाई-बहनों का सहयोग एवं पराक्रम"),
            make_entry("गौरव सहम", "Gaurava Saham", gaurava_lon, "आत्मसम्मान, कुल की प्रतिष्ठा एवं अधिकार"),
            make_entry("सामर्थ्य सहम", "Samarthya Saham", samarthya_lon, "संकल्प शक्ति एवं कठिन कार्यों की सिद्धि"),
            make_entry("पितृ सहम", "Pitru Saham", pitru_lon, "पिता का स्वास्थ्य, सहयोग एवं पैतृक संपत्ति"),
            make_entry("मातृ सहम", "Matru Saham", matru_lon, "माता का सुख, आशीर्वाद एवं घरेलू शांति"),
            make_entry("बन्धु सहam", "Bandhu Saham", bandhu_lon, "सगे-संबंधियों व समाज से सहयोग")
        ]

    def _check_ithasala(self, chart: KundaliChart, p1_name: str, p2_name: str) -> bool:
        """Evaluates whether an Ithasala (harmonious applying aspect) exists."""
        if p1_name not in chart.planets or p2_name not in chart.planets or p1_name == p2_name:
            return True
        p1 = chart.planets[p1_name]
        p2 = chart.planets[p2_name]

        # Check Tajika aspect (houses: 1, 3, 5, 7, 9, 11)
        house_diff = abs(p1.house_from_lagna - p2.house_from_lagna)
        if house_diff not in (0, 2, 4, 6, 8, 10):
            return False

        # Check deepthamsa orb
        orb1 = PLANETARY_ORBS.get(p1_name, 9.0)
        orb2 = PLANETARY_ORBS.get(p2_name, 9.0)
        mean_orb = (orb1 + orb2) / 2.0

        deg_diff = abs(p1.sign_degree - p2.sign_degree)
        if deg_diff > mean_orb:
            return False

        # Faster planet must have lower degree for Ithasala
        rank1 = PLANET_SPEED_RANK.get(p1_name, 4)
        rank2 = PLANET_SPEED_RANK.get(p2_name, 4)
        if rank1 < rank2:  # p1 is faster
            return p1.sign_degree <= p2.sign_degree
        else:
            return p2.sign_degree <= p1.sign_degree

    def _calculate_mudda_dasha(self, start_dt: datetime, moon_lon: float) -> List[Dict[str, Any]]:
        """Calculates full 1-year Mudda Dasha sequence (Vimshottari mapped to 365.25 days)."""
        vimshottari_years = [
            ("Ketu", 7), ("Venus", 20), ("Sun", 6), ("Moon", 10),
            ("Mars", 7), ("Rahu", 18), ("Jupiter", 16), ("Saturn", 19), ("Mercury", 17)
        ]
        timeline = []
        curr = start_dt
        for lord, yrs in vimshottari_years:
            dur_days = yrs * (365.25 / 120.0)
            end = curr + timedelta(days=dur_days)
            timeline.append({
                "lord": lord,
                "start_date": curr.strftime("%d-%b-%Y"),
                "end_date": end.strftime("%d-%b-%Y"),
                "duration_days": round(dur_days, 1)
            })
            curr = end
        return timeline


# Singleton Varshaphal service
default_varshaphal_service = VarshaphalService()
