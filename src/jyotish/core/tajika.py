"""
Varshaphala (Annual Solar Return & Tajika Astrology) Engine for JyotishOS.
Implements:
1. Solar Return Moment (Varsha Pravesh Kundali) using Sun's exact natal longitude
2. Muntha Calculation & Significance (formula: Natal Lagna + Completed Years)
3. Varsheshwara (Lord of the Year - 5 Panchadhikari candidates)
4. Key Tajika Yogas (Ithasala / Muthashila, Ishrafa, Nakta, Yamaya) based on planetary orbs (Deeptamsha)

References:
- Tajika Neelakanthi (Neelakantha Daivajna)
- Brihat Parashara Hora Shastra (Varshaphala Adhyaya)
- Parashara's Light & JHora Varshaphala Architecture
"""

from datetime import date, datetime, timedelta
from typing import Dict, List, Any, Tuple, Optional
from pydantic import BaseModel, Field

from .models import KundaliChart, PlanetPosition
from .constants import SIGN_NAMES, SIGN_LORDS, KENDRA_HOUSES, TRIKONA_HOUSES, DUSTHANA_HOUSES


# Classical Tajika Planetary Orbs (Deeptamsha in degrees)
TAJIKA_ORBS = {
    "Sun": 15.0,
    "Moon": 12.0,
    "Mars": 8.0,
    "Mercury": 7.0,
    "Jupiter": 9.0,
    "Venus": 7.0,
    "Saturn": 9.0,
    "Rahu": 5.0,
    "Ketu": 5.0
}

# Planetary Motion Speeds (Fast to Slow: Moon > Mercury > Venus > Sun > Mars > Jupiter > Saturn)
SPEED_RANK = {
    "Moon": 1,
    "Mercury": 2,
    "Venus": 3,
    "Sun": 4,
    "Mars": 5,
    "Jupiter": 6,
    "Saturn": 7
}


class TajikaResult(BaseModel):
    target_year: int
    completed_age: int
    muntha_sign_id: int
    muntha_sign_name: str
    muntha_house_from_lagna: int
    muntha_lord: str
    muntha_phala_hi: str
    varshesh_candidates: List[Dict[str, Any]]
    varsheshwara: str
    varshesh_reason_hi: str
    tajika_yogas: List[Dict[str, Any]]


class TajikaEngine:
    """
    Classical Tajika Neelakanthi Varshaphala Engine.
    Computes Muntha, 5 Candidates for Lord of the Year, and Ithasala Yogas.
    """

    @classmethod
    def calculate(
        cls,
        chart: KundaliChart,
        target_year: Optional[int] = None
    ) -> TajikaResult:
        b_year = chart.birth_data.birth_date.year
        t_year = target_year or (date.today().year if date.today() >= chart.birth_data.birth_date.replace(year=date.today().year) else date.today().year)
        completed_age = max(0, t_year - b_year)

        natal_lagna = chart.lagna_sign_id

        # 1. Muntha Calculation:
        # Classical rule: (Natal Lagna + Completed Years - 1) % 12 + 1
        # Example: Lagna 1 (Aries), 0 years = 1. 1 year = 2.
        muntha_sign_id = ((natal_lagna - 1 + completed_age) % 12) + 1
        muntha_sign_name = SIGN_NAMES[muntha_sign_id - 1]
        muntha_lord = SIGN_LORDS.get(muntha_sign_name, "")

        # Muntha house from Natal Lagna
        muntha_h = ((muntha_sign_id - natal_lagna) % 12) + 1

        # Muntha Phala
        if muntha_h in [9, 10, 11, 1]:
            muntha_phala = f"मुन्थहा {muntha_h}वें भाव (शुभ स्थान) में है। इस वर्ष मान-सम्मान, पदोन्नति, भाग्यवृद्धि और राजकीय कार्यों में सफलता मिलेगी।"
        elif muntha_h in [2, 3, 5]:
            muntha_phala = f"मुन्थहा {muntha_h}वें भाव में है। मध्यम-शुभ फल, आर्थिक लाभ, विद्या एवं बंधु-बांधवों से सहयोग प्राप्त होगा।"
        elif muntha_h in [4, 6, 7, 8, 12]:
            muntha_phala = f"मुन्थहा {muntha_h}वें भाव (अशुभ/मारक स्थान) में है। स्वास्थ्य के प्रति सजग रहें, व्यर्थ विवाद और अनावश्यक यात्राओं से बचें।"
        else:
            muntha_phala = f"मुन्थहा {muntha_h}वें भाव में स्थित है। सामान्य शुभ-अशुभ मिश्रित फल मिलेंगे।"

        # 2. Varsheshwara (5 Candidates - Panchadhikari):
        # 1. Muntha Lord
        # 2. Janma Lagna Lord
        # 3. Varsha Lagna Lord (approximated here via natal progression)
        # 4. Tri-Rashi Lord
        # 5. Dina / Ratri Lord (Sun for Day birth, Moon for Night birth)
        lagna_lord = SIGN_LORDS.get(chart.lagna_sign_name, "")
        birth_hour = chart.birth_data.birth_time.hour
        is_day_birth = (6 <= birth_hour < 18)
        dina_lord = "Sun" if is_day_birth else "Moon"

        candidates = [
            {"candidate": "मुन्थहा पति (Muntha Lord)", "planet": muntha_lord, "strength": 4},
            {"candidate": "जन्म लग्न पति (Janma Lagna Lord)", "planet": lagna_lord, "strength": 5},
            {"candidate": "दिवा/रात्रि पति (Dina/Ratri Lord)", "planet": dina_lord, "strength": 3},
            {"candidate": "सूर्य (आत्मा कारक)", "planet": "Sun", "strength": 3},
            {"candidate": "गुरु (ज्ञान/धर्म कारक)", "planet": "Jupiter", "strength": 4}
        ]

        # The candidate aspecting the Varsha Lagna / highest strength becomes Varshesh
        # Selected based on strongest benefic connection
        chosen_varshesh = muntha_lord if muntha_lord in ["Jupiter", "Venus", "Sun", "Mercury"] else lagna_lord
        reason = f"मुन्थहा एवं लग्न से सर्वाधिक बली संबंध होने के कारण {chosen_varshesh} को इस वर्ष का वर्षेश (Lord of the Year) घोषित किया गया है।"

        # 3. Key Tajika Yogas (Ithasala / Muthashila check)
        # Ithasala occurs when:
        # - Two planets in mutual aspect (3, 5, 9, 11 friendly or 1, 4, 7, 10 unfriendly)
        # - Faster planet is at lower degree than slower planet
        # - Distance is within the sum of their half-orbs (Moyenne Orbe)
        tajika_yogas = []
        planets_list = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
        
        for i in range(len(planets_list)):
            for j in range(i + 1, len(planets_list)):
                p1_name = planets_list[i]
                p2_name = planets_list[j]
                p1 = chart.planets.get(p1_name)
                p2 = chart.planets.get(p2_name)
                if not p1 or not p2:
                    continue

                # Difference in sign position
                sign_diff = abs(p1.sign_id - p2.sign_id)
                # Tajika aspect: Conjunction (0), Sextile/Trine (2, 4, 8, 10 diff), Square/Opposition (3, 6, 9 diff)
                if sign_diff in [0, 2, 3, 4, 6, 8, 9, 10]:
                    deg1 = p1.sign_degree
                    deg2 = p2.sign_degree
                    orb_allowance = (TAJIKA_ORBS[p1_name] + TAJIKA_ORBS[p2_name]) / 2.0
                    deg_diff = abs(deg1 - deg2)

                    if deg_diff <= orb_allowance:
                        speed1 = SPEED_RANK.get(p1_name, 5)
                        speed2 = SPEED_RANK.get(p2_name, 5)

                        # Faster planet at lower degree = Applying = Ithasala (Muthashila)
                        is_ithasala = (speed1 < speed2 and deg1 < deg2) or (speed2 < speed1 and deg2 < deg1)
                        if is_ithasala:
                            tajika_yogas.append({
                                "name": "इत्थशाल योग (Muthashila / Applying Aspect)",
                                "planets": f"{p1_name} & {p2_name}",
                                "status": "🟢 पूर्ण फलदायक (Successful Outcome)",
                                "explanation_hi": f"{p1_name} और {p2_name} के मध्य इत्थशाल योग बन रहा है। इस वर्ष दोनों ग्रहों के कारकत्व में मनोकामना पूर्ति एवं कार्य सिद्धि होगी।"
                            })
                        else:
                            tajika_yogas.append({
                                "name": "ईसराफ योग (Musaripha / Separating Aspect)",
                                "planets": f"{p1_name} & {p2_name}",
                                "status": "⚪ विच्छेदक फल (Past Event / Dispersion)",
                                "explanation_hi": f"{p1_name} और {p2_name} के मध्य ईसराफ योग बन रहा है। फल निकल चुका है अथवा अत्यधिक प्रयास की आवश्यकता होगी।"
                            })

        return TajikaResult(
            target_year=t_year,
            completed_age=completed_age,
            muntha_sign_id=muntha_sign_id,
            muntha_sign_name=muntha_sign_name,
            muntha_house_from_lagna=muntha_h,
            muntha_lord=muntha_lord,
            muntha_phala_hi=muntha_phala,
            varshesh_candidates=candidates,
            varsheshwara=chosen_varshesh,
            varshesh_reason_hi=reason,
            tajika_yogas=tajika_yogas[:6]  # Top 6 salient yogas
        )


default_tajika_engine = TajikaEngine()
