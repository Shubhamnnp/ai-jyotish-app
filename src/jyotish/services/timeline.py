"""
Unified Predictive Life Timeline Service for JyotishOS.
Synthesizes Vimshottari Dasha, Jaimini Chara Dasha, Yogini Dasha,
Varshaphal Muntha, and Major Transits into a year-by-year 0-100 timeline
with classical Life Event Probability Windows (Career, Marriage, Wealth, Travel, Health).
"""

from datetime import datetime, date, timedelta
from typing import Dict, List, Any, Optional
import math

from ..core.constants import SIGN_NAMES, SIGN_LORDS, GRAHAS
from ..core.models import KundaliChart
from ..dasha.vimshottari import default_vimshottari_engine
from ..dasha.chara import CharaDashaEngine
from ..dasha.yogini import YoginiDashaEngine


class PredictiveTimelineService:
    """Calculates unified life timeline and event probability curves for 0-100 years."""

    # Approximate sidereal planetary cycle periods in years
    JUPITER_YEARS_PER_SIGN = 0.989  # ~11.86 years / 12
    SATURN_YEARS_PER_SIGN = 2.455   # ~29.46 years / 12
    RAHU_YEARS_PER_SIGN = 1.549     # ~18.6 years / 12 (retrograde)

    @classmethod
    def calculate_life_timeline(
        cls,
        chart: KundaliChart,
        start_age: int = 0,
        end_age: int = 100
    ) -> Dict[str, Any]:
        """
        Calculates unified year-by-year timeline for ages start_age to end_age.
        Returns yearly slices and milestone event probability windows.
        """
        b_data = chart.birth_data
        b_dt = datetime.combine(b_data.birth_date, b_data.birth_time)
        moon_lon = chart.planets["Moon"].longitude
        moon_sign_id = chart.planets["Moon"].sign_id
        lagna_sign_id = chart.lagna_sign_id

        # 1. Precalculate Chara Dasha timeline
        chara_timeline = CharaDashaEngine.generate_timeline(chart)

        # 2. Extract natal lord references
        h_lords = {}
        for h in range(1, 13):
            s_id = ((lagna_sign_id - 1 + (h - 1)) % 12) + 1
            s_name = SIGN_NAMES[s_id - 1]
            h_lords[h] = SIGN_LORDS[s_name]

        indu_sign_id = getattr(chart, "indu_lagna_sign_id", None)
        if not indu_sign_id and hasattr(chart, "jaimini") and chart.jaimini:
            # fallback indu check
            indu_sign_id = (lagna_sign_id + 4) % 12 + 1

        yearly_records = []
        event_windows = {
            "career": [],
            "marriage": [],
            "wealth": [],
            "travel": [],
            "health": []
        }

        curr_year = datetime.now().year
        birth_year = b_dt.year

        for age in range(start_age, min(end_age + 1, 105)):
            cal_year = birth_year + age
            target_dt = b_dt.replace(year=cal_year) if cal_year <= 2100 else b_dt

            # A. Vimshottari Active Dasha
            try:
                v_hier = default_vimshottari_engine.get_5level_hierarchy(b_dt, moon_lon, target_dt)
                md_lord = v_hier.get("mahadasha", {}).get("lord", "Sun")
                ad_lord = v_hier.get("antardasha", {}).get("lord", md_lord)
                pd_lord = v_hier.get("pratyantardasha", {}).get("lord", ad_lord)
            except Exception:
                md_lord, ad_lord, pd_lord = "Sun", "Sun", "Sun"

            # B. Chara Dasha Active Sign
            chara_sign = "Aries"
            chara_sign_id = 1
            for cd in chara_timeline:
                if cd["start_date"] <= target_dt <= cd["end_date"]:
                    chara_sign = cd["sign_name"]
                    chara_sign_id = cd["sign_id"]
                    break

            # C. Yogini Dasha
            yog_info = YoginiDashaEngine.get_active_yogini_at(b_dt, moon_lon, target_dt)
            yogini_name = yog_info.get("name", "Mangala")
            yogini_lord = yog_info.get("lord", "Moon")

            # D. Varshaphal Muntha
            # Muntha advances 1 sign per completed year of age
            muntha_sign_id = ((lagna_sign_id - 1 + age) % 12) + 1
            muntha_sign_name = SIGN_NAMES[muntha_sign_id - 1]
            muntha_house = ((muntha_sign_id - lagna_sign_id) % 12) + 1
            muntha_lord = SIGN_LORDS[muntha_sign_name]
            muntha_status = "शुभ (Fav)" if muntha_house in [1, 2, 3, 5, 9, 10, 11] else "सतर्कता (Caution)"

            # E. Major Planetary Transits Approximation at Age
            # Jupiter moves ~1 sign per year
            jup_natal_sign = chart.planets["Jupiter"].sign_id
            jup_transit_sign_id = ((jup_natal_sign - 1 + int(age / cls.JUPITER_YEARS_PER_SIGN)) % 12) + 1
            jup_from_moon = ((jup_transit_sign_id - moon_sign_id) % 12) + 1
            jup_from_lagna = ((jup_transit_sign_id - lagna_sign_id) % 12) + 1
            jup_auspicious = jup_from_moon in [2, 5, 7, 9, 11]

            # Saturn moves ~1 sign per 2.5 years
            sat_natal_sign = chart.planets["Saturn"].sign_id
            sat_transit_sign_id = ((sat_natal_sign - 1 + int(age / cls.SATURN_YEARS_PER_SIGN)) % 12) + 1
            sat_from_moon = ((sat_transit_sign_id - moon_sign_id) % 12) + 1
            sat_from_lagna = ((sat_transit_sign_id - lagna_sign_id) % 12) + 1

            sade_sati = "नहीं"
            if sat_from_moon == 12:
                sade_sati = "उदय (1st Phase)"
            elif sat_from_moon == 1:
                sade_sati = "शिखर (Peak 2nd)"
            elif sat_from_moon == 2:
                sade_sati = "अस्त (3rd Phase)"
            elif sat_from_moon in [4, 8]:
                sade_sati = "ढैय्या (Kantaka/Ashtama)"

            # F. Event Probability Scores (0 to 100%)
            # 1. Career / Profession (Houses 10, 6, 11, 1, Sun, Mars)
            career_score = 40
            if md_lord in [h_lords[10], h_lords[1], h_lords[11], "Sun", "Mars"]:
                career_score += 25
            if ad_lord in [h_lords[10], h_lords[11], h_lords[6]]:
                career_score += 15
            if muntha_house in [10, 11, 1]:
                career_score += 10
            if jup_from_lagna in [10, 1, 11] or jup_from_moon in [10, 11]:
                career_score += 10
            career_score = min(98, max(20, career_score))

            # 2. Marriage / Partnership (Houses 7, 2, Venus, Jupiter)
            marriage_score = 25
            if 20 <= age <= 42:
                marriage_score += 20
                if md_lord in [h_lords[7], h_lords[2], "Venus", "Jupiter"]:
                    marriage_score += 25
                if ad_lord in [h_lords[7], h_lords[2], "Venus"]:
                    marriage_score += 15
                if jup_from_moon in [7, 5, 9, 11, 1]:
                    marriage_score += 15
                if muntha_house in [7, 2]:
                    marriage_score += 5
            marriage_score = min(96, max(15, marriage_score))

            # 3. Wealth / Property (Houses 2, 11, 4, 9, Jupiter, Indu Lagna)
            wealth_score = 35
            if md_lord in [h_lords[2], h_lords[11], h_lords[4], h_lords[9], "Jupiter"]:
                wealth_score += 25
            if ad_lord in [h_lords[2], h_lords[11], h_lords[4]]:
                wealth_score += 15
            if muntha_house in [2, 11, 4, 9]:
                wealth_score += 15
            if jup_auspicious:
                wealth_score += 10
            wealth_score = min(98, max(20, wealth_score))

            # 4. Travel / Foreign Relocation (Houses 9, 12, 3, Rahu)
            travel_score = 30
            if md_lord in [h_lords[12], h_lords[9], h_lords[3], "Rahu"]:
                travel_score += 30
            if ad_lord in [h_lords[12], h_lords[9], "Rahu"]:
                travel_score += 20
            if muntha_house in [9, 12, 3]:
                travel_score += 15
            travel_score = min(95, max(15, travel_score))

            # 5. Health Caution (Houses 6, 8, 12, 2, 7, Saturn Sade Sati)
            health_caution_score = 20
            if md_lord in [h_lords[6], h_lords[8], h_lords[12]]:
                health_caution_score += 30
            if ad_lord in [h_lords[6], h_lords[8]]:
                health_caution_score += 20
            if muntha_house in [6, 8, 12]:
                health_caution_score += 15
            if "शिखर" in sade_sati or "ढैय्या" in sade_sati:
                health_caution_score += 15
            health_caution_score = min(95, max(15, health_caution_score))

            is_current = (cal_year == curr_year)

            record = {
                "age": age,
                "year": cal_year,
                "is_current": is_current,
                "vimshottari_md": md_lord,
                "vimshottari_ad": ad_lord,
                "vimshottari_pd": pd_lord,
                "dasha_code": f"{md_lord}/{ad_lord}",
                "chara_sign": chara_sign,
                "yogini": f"{yogini_name} ({yogini_lord})",
                "muntha_sign": muntha_sign_name,
                "muntha_house": muntha_house,
                "muntha_status": muntha_status,
                "jupiter_transit_house": jup_from_moon,
                "jupiter_fav": jup_auspicious,
                "sade_sati": sade_sati,
                "career_score": career_score,
                "marriage_score": marriage_score,
                "wealth_score": wealth_score,
                "travel_score": travel_score,
                "health_caution_score": health_caution_score
            }
            yearly_records.append(record)

            # Check threshold windows for milestones
            if career_score >= 70:
                event_windows["career"].append({"year": cal_year, "age": age, "score": career_score, "dasha": record["dasha_code"]})
            if marriage_score >= 65 and 20 <= age <= 42:
                event_windows["marriage"].append({"year": cal_year, "age": age, "score": marriage_score, "dasha": record["dasha_code"]})
            if wealth_score >= 70:
                event_windows["wealth"].append({"year": cal_year, "age": age, "score": wealth_score, "dasha": record["dasha_code"]})
            if travel_score >= 65:
                event_windows["travel"].append({"year": cal_year, "age": age, "score": travel_score, "dasha": record["dasha_code"]})
            if health_caution_score >= 65:
                event_windows["health"].append({"year": cal_year, "age": age, "score": health_caution_score, "dasha": record["dasha_code"]})

        return {
            "records": yearly_records,
            "event_windows": event_windows,
            "current_age": max(0, curr_year - birth_year),
            "birth_year": birth_year
        }


default_timeline_service = PredictiveTimelineService()
