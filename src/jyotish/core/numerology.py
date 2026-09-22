"""
Vedic & Lo-Shu Numerology Engine for JyotishOS.
Implements:
1. Mulank (Driver / Root Number) & Bhagyank (Conductor / Destiny Number)
2. Chaldean & Pythagorean Name Number (Namank) with compatibility
3. 3x3 Lo-Shu Grid (Magic Square of 15) with 8 Planes / Yogas
4. Missing Numbers & Excessive Numbers Analysis with Crystal/Metal/Color Remedies
5. Kua Number (Feng Shui / Directional Energy)
6. Personal Year, Personal Month & Lucky Factors (Days, Colors, Stones, Planets)

References:
- Sankhya Shastra (Vedic Numerology by Cheiro / Sepharial / Harish Johari)
- Lo-Shu Magic Square (I-Ching & Chinese Numerology tradition adopted by LeoStar)
- Chaldean Alphabet Gematria Table
"""

from datetime import date
from typing import Dict, List, Any, Tuple, Optional
from pydantic import BaseModel, Field


# -------------------------------------------------------------
# 1. Classical Alphabet Mappings
# -------------------------------------------------------------

# Chaldean Gematria (Ancient Babylonian - most respected in Indian astrology)
# Note: 9 is considered sacred in Chaldean and not assigned to individual letters
CHALDEAN_MAP = {
    'A': 1, 'I': 1, 'J': 1, 'Q': 1, 'Y': 1,
    'B': 2, 'K': 2, 'R': 2,
    'C': 3, 'G': 3, 'L': 3, 'S': 3,
    'D': 4, 'M': 4, 'T': 4,
    'E': 5, 'H': 5, 'N': 5, 'X': 5,
    'U': 6, 'V': 6, 'W': 6,
    'O': 7, 'Z': 7,
    'F': 8, 'P': 8
}

# Pythagorean Western Gematria (Sequential 1 to 9)
PYTHAGOREAN_MAP = {
    'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5, 'F': 6, 'G': 7, 'H': 8, 'I': 9,
    'J': 1, 'K': 2, 'L': 3, 'M': 4, 'N': 5, 'O': 6, 'P': 7, 'Q': 8, 'R': 9,
    'S': 1, 'T': 2, 'U': 3, 'V': 4, 'W': 5, 'X': 6, 'Y': 7, 'Z': 8
}

# Number Attributes & Planetary Lords
NUMBER_DATA = {
    1: {
        "planet": "Sun (सूर्य)",
        "element": "Fire (अग्नि)",
        "nature": "Leadership, Independence, Originality, Ambition",
        "nature_hi": "नेतृत्व, आत्मविश्वास, स्वावलंबन, पराक्रम, मान-सम्मान",
        "direction": "North (उत्तर - जल तत्व इन लो-शू)",
        "lucky_days": ["Sunday", "Monday"],
        "lucky_colors": ["Golden", "Yellow", "Copper", "Orange"],
        "friendly_numbers": [1, 2, 3, 5, 9],
        "neutral_numbers": [4, 7],
        "enemy_numbers": [6, 8],
        "gemstone": "Ruby (माणिक्य)"
    },
    2: {
        "planet": "Moon (चन्द्र)",
        "element": "Water / Earth (जल / पृथ्वी)",
        "nature": "Intuition, Diplomacy, Sensitivity, Cooperation, Peace",
        "nature_hi": "संवेदनशीलता, सौम्यता, कल्पनाशीलता, शांति, कूटनीति",
        "direction": "South-West (दक्षिण-पश्चिम)",
        "lucky_days": ["Monday", "Sunday", "Friday"],
        "lucky_colors": ["White", "Cream", "Silver", "Light Green"],
        "friendly_numbers": [1, 2, 3, 5],
        "neutral_numbers": [4, 7],
        "enemy_numbers": [6, 8, 9],
        "gemstone": "Pearl (मोती / मूनस्टोन)"
    },
    3: {
        "planet": "Jupiter (बृहस्पति / गुरु)",
        "element": "Wood / Ether (काष्ठ / आकाश)",
        "nature": "Wisdom, Optimism, Creative Expression, Expansion",
        "nature_hi": "ज्ञान, विस्तार, परामर्श, धार्मिकता, सृजनशीलता",
        "direction": "East (पूर्व)",
        "lucky_days": ["Thursday", "Tuesday", "Friday"],
        "lucky_colors": ["Yellow", "Saffron", "Purple", "Pink"],
        "friendly_numbers": [1, 2, 3, 5, 7, 9],
        "neutral_numbers": [8],
        "enemy_numbers": [6],
        "gemstone": "Yellow Sapphire (पुखराज)"
    },
    4: {
        "planet": "Rahu / Uranus (राहु / यूरेनस)",
        "element": "Wood / Earth (काष्ठ / पृथ्वी)",
        "nature": "Practicality, Revolution, Discipline, Sudden Changes",
        "nature_hi": "व्यावहारिकता, अचानक परिवर्तन, संगठन कौशल, तकनीकी बुद्धि",
        "direction": "South-East (दक्षिण-पूर्व)",
        "lucky_days": ["Sunday", "Monday", "Saturday"],
        "lucky_colors": ["Blue", "Grey", "Electric Violet"],
        "friendly_numbers": [1, 5, 6, 7, 8],
        "neutral_numbers": [2, 3],
        "enemy_numbers": [4, 9],
        "gemstone": "Hessonite (गोमेद / लेपिडोलिट)"
    },
    5: {
        "planet": "Mercury (बुध)",
        "element": "Earth / Center (पृथ्वी / मध्य केन्द्र)",
        "nature": "Communication, Adaptability, Commerce, Freedom, Balance",
        "nature_hi": "संतुलन, संवाद कुशलता, व्यापार, बहुमुखी प्रतिभा, बुद्धि",
        "direction": "Center (ब्रह्मस्थान / मध्य)",
        "lucky_days": ["Wednesday", "Friday", "Thursday"],
        "lucky_colors": ["Green", "Emerald", "Turquoise", "White"],
        "friendly_numbers": [1, 2, 3, 5, 6],
        "neutral_numbers": [7, 8, 9],
        "enemy_numbers": [4],
        "gemstone": "Emerald (पन्ना / पेरिडॉट)"
    },
    6: {
        "planet": "Venus (शुक्र)",
        "element": "Metal / Water (धातु / जल)",
        "nature": "Love, Luxury, Aesthetics, Harmony, Responsibility",
        "nature_hi": "विलासिता, कला, आकर्षण, दांपत्य सुख, सौंदर्य, शान-शौकत",
        "direction": "North-West (उत्तर-पश्चिम)",
        "lucky_days": ["Friday", "Tuesday", "Thursday"],
        "lucky_colors": ["White", "Light Blue", "Pink", "Silver"],
        "friendly_numbers": [1, 4, 5, 6, 7],
        "neutral_numbers": [8, 9],
        "enemy_numbers": [3],
        "gemstone": "Diamond (हीरा / ओपल / जरकन)"
    },
    7: {
        "planet": "Ketu / Neptune (केतु / नेप्च्यून)",
        "element": "Metal (धातु)",
        "nature": "Spirituality, Analysis, Research, Detachment, Mystery",
        "nature_hi": "अध्यात्म, गूढ़ शोध, अंतर्ज्ञान, वैराग्य, दार्शनिक चिंतन",
        "direction": "West (पश्चिम)",
        "lucky_days": ["Sunday", "Monday", "Wednesday"],
        "lucky_colors": ["Light Green", "White", "Pastel Yellow", "Light Grey"],
        "friendly_numbers": [1, 3, 4, 5, 6],
        "neutral_numbers": [2, 8],
        "enemy_numbers": [9],
        "gemstone": "Cat's Eye (लहसुनिया / मूनस्टोन)"
    },
    8: {
        "planet": "Saturn (शनि)",
        "element": "Earth (पृथ्वी)",
        "nature": "Hard Work, Karmic Justice, Perseverance, Material Mastery",
        "nature_hi": "कड़ा परिश्रम, कर्मफल, न्याय, धैर्य, संगठन, गूढ़ विद्या",
        "direction": "North-East (उत्तर-पूर्व)",
        "lucky_days": ["Saturday", "Wednesday", "Friday"],
        "lucky_colors": ["Dark Blue", "Black", "Dark Violet", "Grey"],
        "friendly_numbers": [3, 4, 5, 6, 7],
        "neutral_numbers": [1, 8],
        "enemy_numbers": [2, 9],
        "gemstone": "Blue Sapphire (नीलम / एमेथिस्ट)"
    },
    9: {
        "planet": "Mars (मंगल)",
        "element": "Fire (अग्नि)",
        "nature": "Energy, Courage, Humanitarianism, Passion, Defense",
        "nature_hi": "ऊर्जा, साहस, पराक्रम, नेतृत्व, परोपकार, गतिशीलता",
        "direction": "South (दक्षिण)",
        "lucky_days": ["Tuesday", "Thursday", "Sunday"],
        "lucky_colors": ["Red", "Coral", "Crimson", "Pink"],
        "friendly_numbers": [1, 2, 3, 5],
        "neutral_numbers": [6, 7],
        "enemy_numbers": [4, 8],
        "gemstone": "Red Coral (मूंगा)"
    }
}

# Lo-Shu 8 Planes (Yogas)
LO_SHU_PLANES = [
    {
        "name": "Mental Plane (मानसिक तल)",
        "numbers": [4, 9, 2],
        "significance_hi": "उत्कृष्ट स्मरणशक्ति, तार्किक सोच, बौद्धिक योजना और सूक्ष्म विश्लेषण क्षमता।",
        "significance_en": "Superb memory, sharp intellect, analytical planning, and cognitive reasoning."
    },
    {
        "name": "Emotional Plane (हृदय / भावनात्मक तल)",
        "numbers": [3, 5, 7],
        "significance_hi": "आत्मिक संतुलन, उच्च अंतर्ज्ञान, आध्यात्मिक संवेदनशीलता और दूसरों के दर्द को समझने की शक्ति।",
        "significance_en": "Emotional balance, deep spiritual intuition, empathy, and artistic sensibility."
    },
    {
        "name": "Practical Plane (व्यावहारिक तल)",
        "numbers": [8, 1, 6],
        "significance_hi": "जमीनी काम, भौतिक प्रगति, वित्तीय समझ और कठिन परिश्रम से सफलता प्राप्त करने का सामर्थ्य।",
        "significance_en": "Grounded execution, financial acumen, business skill, and practical manifestation."
    },
    {
        "name": "Thought Plane (विचार शक्ति तल)",
        "numbers": [4, 3, 8],
        "significance_hi": "योजनाकार, दूरदर्शी सोच, नई संकल्पनाओं को जन्म देने वाला और संगठनात्मक निपुणता।",
        "significance_en": "Strategic vision, deep planning capability, conceptual originality, and architecture."
    },
    {
        "name": "Will Plane (दृढ़ इच्छाशक्ति तल)",
        "numbers": [9, 5, 1],
        "significance_hi": "अदम्य इच्छाशक्ति, कभी हार न मानने का जज्बा, विपत्तियों को पार कर शीर्ष पर पहुँचने की क्षमता।",
        "significance_en": "Unshakable determination, resilience, perseverance against all odds, and triumph."
    },
    {
        "name": "Action Plane (कर्म शक्ति तल)",
        "numbers": [2, 7, 6],
        "significance_hi": "त्वरित निर्णय, योजनाओं को तुरंत जमीन पर लागू करना और शब्दों को कर्म में बदलने की शक्ति।",
        "significance_en": "Decisive action, rapid execution, translating ideas into physical reality."
    },
    {
        "name": "Golden Raj Yoga (स्वर्ण राजयोग)",
        "numbers": [4, 5, 6],
        "significance_hi": "नाम, यश, अकूत संपत्ति, राजसी सुख और जीवन में सभी भौतिक कामनाओं की सहज पूर्ति।",
        "significance_en": "Extreme wealth, fame, royal luxury, status, and effortless material elevation."
    },
    {
        "name": "Silver Property Yoga (भूमि-सम्पत्ति योग)",
        "numbers": [2, 5, 8],
        "significance_hi": "अचल संपत्ति, रियल एस्टेट, भवन निर्माण, पैतृक भूमि और स्थिरता का सर्वश्रेष्ठ योग।",
        "significance_en": "Extensive real estate, land ownership, ancestral property, and material stability."
    }
]

# Remedies for Missing Numbers
MISSING_NUMBER_REMEDIES = {
    1: {
        "lacking_hi": "आत्मविश्वास की कमी, संवाद में संकोच, करियर में दिशाहीनता या पिता से वैचारिक मतभेद।",
        "remedy_hi": "प्रातः सूर्य देव को तांबे के लोटे से जल दें। उत्तर दिशा में बहते पानी का फव्वारा या जल तत्व का चित्र लगाएं। लाल कलावा पहनें।",
        "item": "तांबा / सूर्य यंत्र"
    },
    2: {
        "lacking_hi": "धैर्य का अभाव, संवेदनशीलता की कमी, संबंधों में कड़वाहट या माता के स्वास्थ्य को लेकर चिंता।",
        "remedy_hi": "चाँदी का कड़ा अथवा अंगूठी पहनें। माता के चरण स्पर्श कर आशीर्वाद लें। दक्षिण-पश्चिम दिशा में दो हंसों का जोड़ा या क्रिस्टल बॉल रखें।",
        "item": "चाँदी / सफेद मोती / मूनस्टोन"
    },
    3: {
        "lacking_hi": "ज्ञान अर्जन में रुकावट, एकाग्रता की कमी, गुरुजनों के मार्गदर्शन का अभाव, वित्तीय योजना में चूक।",
        "remedy_hi": "बृहस्पतिवार को हल्दी या केसर का तिलक लगाएं। पूर्व दिशा में हरे पौधे लगाएं। तुलसी की पूजा करें और गले में पंचमुखी रुद्राक्ष धारण करें।",
        "item": "पीला पुखराज / हल्दी की गांठ / तुलसी माला"
    },
    4: {
        "lacking_hi": "अनुशासनहीनता, वित्तीय अस्थिरता, संगठनात्मक क्षमता की कमी, अचानक धन हानि का भय।",
        "remedy_hi": "दक्षिण-पूर्व दिशा में लकड़ी की विंड चाइम (Wind Chime) लगाएं। घर में हरा-भरा मनी प्लांट रखें। अपने पर्स में हरे रंग का कपड़ा रखें।",
        "item": "ग्रीन एवेंचुरिन / रुद्राक्ष"
    },
    5: {
        "lacking_hi": "जीवन में असंतुलन, व्यापारिक समझ की कमी, निर्णय लेने में असमंजस, आत्मविश्वास डगमगाना।",
        "remedy_hi": "घर के मध्य (ब्रह्मस्थान) को साफ व हल्का रखें। पीले रंग की मिट्टी की वस्तुएं या क्रिस्टल पिरामिड ब्रह्मस्थान में रखें। गाय को हरी घास खिलाएं।",
        "item": "येलो जैस्पर / सिट्रीन क्रिस्टल"
    },
    6: {
        "lacking_hi": "सुख-सुविधाओं की कमी, दांपत्य जीवन में रसहीनता, मित्रों या सहयोगियों से सहयोग न मिलना।",
        "remedy_hi": "उत्तर-पश्चिम दिशा में 6 छड़ों वाली मेटल विंड चाइम लगाएं। सुगंधित इत्र/परफ्यूम का प्रयोग करें। कलाई में ब्रास या सिल्वर ब्रेसलेट पहनें।",
        "item": "क्लियर क्वार्ट्ज / स्फटिक माला / जरकन"
    },
    7: {
        "lacking_hi": "संतान पक्ष में चिंता, अध्यात्म से दूरी, जीवन की सीख न ले पाना, डिप्रेशन या एकाकीपन।",
        "remedy_hi": "पश्चिम दिशा में धातु की घंटी या व्हाइट क्रिस्टल रखें। सफेद वस्त्र पहनें। कुत्तों को मीठी रोटी खिलाएं। गणेश जी की आराधना करें।",
        "item": "लहसुनिया / टाइगर आई क्रिस्टल"
    },
    8: {
        "lacking_hi": "स्थायी संपत्ति बनाने में कठिनाई, वित्तीय अनुशासन का अभाव, अत्यधिक संघर्ष, बार-बार रुकावटें।",
        "remedy_hi": "उत्तर-पूर्व (ईशान कोण) को साफ रखें और वहाँ पानी का घड़ा या फव्वारा रखें। शनिवार को पीपल के पेड़ के नीचे सरसों तेल का दीपक जलाएं।",
        "item": "ब्लू सफायर उपरत्न / एमेथिस्ट क्रिस्टल"
    },
    9: {
        "lacking_hi": "साहस व ऊर्जा की कमी, काम को टालने की आदत, नेतृत्व में विफलता, रक्त संबंधी विकार।",
        "remedy_hi": "दक्षिण दिशा में लाल बल्ब, त्रिकोण पिरामिड या लाल चित्र लगाएं। नित्य हनुमान चालीसा पढ़ें। लाल रंग का धागा या ताम्बे का कड़ा पहनें।",
        "item": "रेड जैस्पर / ताम्बा"
    }
}


# -------------------------------------------------------------
# 2. Helper Calculation Functions
# -------------------------------------------------------------

def reduce_to_single_digit(n: int, preserve_master: bool = False) -> int:
    """Reduces an integer to a single digit 1-9 (optionally preserving 11, 22, 33)."""
    while n > 9:
        if preserve_master and n in (11, 22, 33):
            return n
        n = sum(int(d) for d in str(n))
    return n


def calculate_name_number(name: str, method: str = "chaldean") -> int:
    """Calculates the single-digit Name Number (Namank) using Chaldean or Pythagorean."""
    clean_name = "".join([c.upper() for c in name if c.isalpha()])
    mapping = CHALDEAN_MAP if method.lower() == "chaldean" else PYTHAGOREAN_MAP
    total = sum(mapping.get(c, 0) for c in clean_name)
    return reduce_to_single_digit(total)


def calculate_kua_number(birth_year: int, gender: str = "male") -> int:
    """
    Calculates the Feng Shui / Directional Kua number:
    - Male: 100 - last two digits of birth year, then reduce; or (10 - sum(last 2 digits))
    Standard classical formula:
    - For males born up to 1999: 10 - single_digit(sum of year digits)
    - For males born 2000+: 9 - single_digit(sum of year digits)
    - For females born up to 1999: single_digit(sum of year digits) + 5
    - For females born 2000+: single_digit(sum of year digits) + 6
    """
    year_sum = reduce_to_single_digit(sum(int(d) for d in str(birth_year)))
    is_post_2000 = (birth_year >= 2000)

    if gender.lower() in ("male", "पुरुष"):
        kua = (9 - year_sum) if is_post_2000 else (10 - year_sum)
        if kua <= 0:
            kua += 9
    else:
        kua = (year_sum + 6) if is_post_2000 else (year_sum + 5)

    kua = reduce_to_single_digit(kua)
    # Exception: Kua 5 becomes 2 for Male, 8 for Female
    if kua == 5:
        kua = 2 if gender.lower() in ("male", "पुरुष") else 8
    return kua


# -------------------------------------------------------------
# 3. Main Numerology Analysis Engine
# -------------------------------------------------------------

class NumerologyResult(BaseModel):
    birth_date_str: str
    mulank: int
    bhagyank: int
    kua_number: int
    chaldean_namank: int
    pythagorean_namank: int
    grid_digits: List[int]
    lo_shu_grid: Dict[int, int]
    present_numbers: List[int]
    missing_numbers: List[int]
    completed_planes: List[Dict[str, Any]]
    incomplete_planes: List[Dict[str, Any]]
    driver_info: Dict[str, Any]
    conductor_info: Dict[str, Any]
    personal_year: int
    remedies_for_missing: List[Dict[str, Any]]
    lucky_summary: Dict[str, Any]


class NumerologyEngine:
    """
    High-precision Vedic and Lo-Shu Numerology Engine for JyotishOS.
    Matches the depth of LeoStar and AstroSage with complete explanation bases.
    """

    @classmethod
    def calculate(
        cls,
        birth_date: date,
        full_name: str,
        gender: str = "male",
        target_year: Optional[int] = None
    ) -> NumerologyResult:
        """Computes complete Numerological Dossier."""
        
        # 1. Mulank (Driver Number = day of birth reduced)
        day = birth_date.day
        mulank = reduce_to_single_digit(day)

        # 2. Bhagyank (Conductor / Destiny Number = full date sum reduced)
        full_sum = day + birth_date.month + birth_date.year
        bhagyank = reduce_to_single_digit(full_sum)

        # 3. Kua Number
        kua = calculate_kua_number(birth_date.year, gender)

        # 4. Namank (Chaldean & Pythagorean)
        chaldean_num = calculate_name_number(full_name, method="chaldean")
        pythagorean_num = calculate_name_number(full_name, method="pythagorean")

        # 5. Extract all digits for Lo-Shu Grid
        # Digits include: Day, Month, Year digits + Mulank + Bhagyank + (Kua number optionally)
        # Classical LeoStar method: Date digits + Mulank + Bhagyank
        date_str = birth_date.strftime("%d%m%Y")
        all_digits = [int(d) for d in date_str if d != '0']
        all_digits.append(mulank)
        all_digits.append(bhagyank)

        # Count frequencies 1 to 9
        grid_counts = {i: all_digits.count(i) for i in range(1, 10)}
        present_nums = [i for i in range(1, 10) if grid_counts[i] > 0]
        missing_nums = [i for i in range(1, 10) if grid_counts[i] == 0]

        # 6. Evaluate 8 Planes
        completed_planes = []
        incomplete_planes = []
        for plane in LO_SHU_PLANES:
            req = plane["numbers"]
            is_full = all(grid_counts[n] > 0 for n in req)
            has_count = sum(1 for n in req if grid_counts[n] > 0)
            plane_entry = {
                "name": plane["name"],
                "numbers": req,
                "is_active": is_full,
                "strength_pct": round((has_count / len(req)) * 100),
                "significance_hi": plane["significance_hi"],
                "significance_en": plane["significance_en"]
            }
            if is_full:
                completed_planes.append(plane_entry)
            else:
                incomplete_planes.append(plane_entry)

        # 7. Remedies for Missing Numbers
        remedies = []
        for m in missing_nums:
            if m in MISSING_NUMBER_REMEDIES:
                r_data = MISSING_NUMBER_REMEDIES[m]
                remedies.append({
                    "number": m,
                    "planet": NUMBER_DATA[m]["planet"],
                    "lacking_hi": r_data["lacking_hi"],
                    "remedy_hi": r_data["remedy_hi"],
                    "item": r_data["item"]
                })

        # 8. Personal Year Calculation
        curr_year = target_year or date.today().year
        # Personal Year = Day + Month + Current Year
        py_sum = day + birth_date.month + curr_year
        personal_year = reduce_to_single_digit(py_sum)

        # 9. Driver & Conductor Dossiers
        driver_info = NUMBER_DATA[mulank]
        conductor_info = NUMBER_DATA[bhagyank]

        # 10. Composite Lucky Factors
        lucky_summary = {
            "lucky_days": list(set(driver_info["lucky_days"] + conductor_info["lucky_days"])),
            "lucky_colors": list(set(driver_info["lucky_colors"] + conductor_info["lucky_colors"])),
            "lucky_numbers": sorted(list(set(driver_info["friendly_numbers"] + conductor_info["friendly_numbers"]))),
            "unfavorable_numbers": sorted(list(set(driver_info["enemy_numbers"] + conductor_info["enemy_numbers"]))),
            "lucky_gemstones": [driver_info["gemstone"], conductor_info["gemstone"]],
            "mulank_lord": driver_info["planet"],
            "bhagyank_lord": conductor_info["planet"],
        }

        return NumerologyResult(
            birth_date_str=birth_date.strftime("%d-%m-%Y"),
            mulank=mulank,
            bhagyank=bhagyank,
            kua_number=kua,
            chaldean_namank=chaldean_num,
            pythagorean_namank=pythagorean_num,
            grid_digits=all_digits,
            lo_shu_grid=grid_counts,
            present_numbers=present_nums,
            missing_numbers=missing_nums,
            completed_planes=completed_planes,
            incomplete_planes=incomplete_planes,
            driver_info=driver_info,
            conductor_info=conductor_info,
            personal_year=personal_year,
            remedies_for_missing=remedies,
            lucky_summary=lucky_summary
        )


default_numerology_engine = NumerologyEngine()

