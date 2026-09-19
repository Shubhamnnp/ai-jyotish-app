"""
Classical Jyotish Astronomical and Shastriya Constants.
References:
- Brihat Parashara Hora Shastra (BPHS)
- Phaladeepika (Mantreshwara)
- Saravali (Kalyanavarma)
"""

from typing import Dict, List, Tuple

# 12 Rashis (Zodiac Signs)
SIGNS = [
    {"id": 1, "name_en": "Aries", "name_hi": "मेष (Mesha)", "lord": "Mars", "element": "Fire"},
    {"id": 2, "name_en": "Taurus", "name_hi": "वृषभ (Vrishabha)", "lord": "Venus", "element": "Earth"},
    {"id": 3, "name_en": "Gemini", "name_hi": "मिथुन (Mithuna)", "lord": "Mercury", "element": "Air"},
    {"id": 4, "name_en": "Cancer", "name_hi": "कर्क (Karka)", "lord": "Moon", "element": "Water"},
    {"id": 5, "name_en": "Leo", "name_hi": "सिंह (Simha)", "lord": "Sun", "element": "Fire"},
    {"id": 6, "name_en": "Virgo", "name_hi": "कन्या (Kanya)", "lord": "Mercury", "element": "Earth"},
    {"id": 7, "name_en": "Libra", "name_hi": "तुला (Tula)", "lord": "Venus", "element": "Air"},
    {"id": 8, "name_en": "Scorpio", "name_hi": "वृश्चिक (Vrishchika)", "lord": "Mars", "element": "Water"},
    {"id": 9, "name_en": "Sagittarius", "name_hi": "धनु (Dhanu)", "lord": "Jupiter", "element": "Fire"},
    {"id": 10, "name_en": "Capricorn", "name_hi": "मकर (Makara)", "lord": "Saturn", "element": "Earth"},
    {"id": 11, "name_en": "Aquarius", "name_hi": "कुम्भ (Kumbha)", "lord": "Saturn", "element": "Air"},
    {"id": 12, "name_en": "Pisces", "name_hi": "मीन (Meena)", "lord": "Jupiter", "element": "Water"},
]

SIGN_NAMES = [s["name_en"] for s in SIGNS]

SIGN_LORDS: Dict[str, str] = {s["name_en"]: s["lord"] for s in SIGNS}

# 27 Nakshatras with lord and span (13 deg 20 min = 13.333333 deg each)
NAKSHATRAS = [
    {"id": 1, "name": "Ashwini", "lord": "Ketu"},
    {"id": 2, "name": "Bharani", "lord": "Venus"},
    {"id": 3, "name": "Krittika", "lord": "Sun"},
    {"id": 4, "name": "Rohini", "lord": "Moon"},
    {"id": 5, "name": "Mrigashira", "lord": "Mars"},
    {"id": 6, "name": "Ardra", "lord": "Rahu"},
    {"id": 7, "name": "Punarvasu", "lord": "Jupiter"},
    {"id": 8, "name": "Pushya", "lord": "Saturn"},
    {"id": 9, "name": "Ashlesha", "lord": "Mercury"},
    {"id": 10, "name": "Magha", "lord": "Ketu"},
    {"id": 11, "name": "Purva Phalguni", "lord": "Venus"},
    {"id": 12, "name": "Uttara Phalguni", "lord": "Sun"},
    {"id": 13, "name": "Hasta", "lord": "Moon"},
    {"id": 14, "name": "Chitra", "lord": "Mars"},
    {"id": 15, "name": "Swati", "lord": "Rahu"},
    {"id": 16, "name": "Vishakha", "lord": "Jupiter"},
    {"id": 17, "name": "Anuradha", "lord": "Saturn"},
    {"id": 18, "name": "Jyeshtha", "lord": "Mercury"},
    {"id": 19, "name": "Mula", "lord": "Ketu"},
    {"id": 20, "name": "Purva Ashadha", "lord": "Venus"},
    {"id": 21, "name": "Uttara Ashadha", "lord": "Sun"},
    {"id": 22, "name": "Shravana", "lord": "Moon"},
    {"id": 23, "name": "Dhanishta", "lord": "Mars"},
    {"id": 24, "name": "Shatabhisha", "lord": "Rahu"},
    {"id": 25, "name": "Purva Bhadrapada", "lord": "Jupiter"},
    {"id": 26, "name": "Uttara Bhadrapada", "lord": "Saturn"},
    {"id": 27, "name": "Revati", "lord": "Mercury"},
]

NAKSHATRA_NAMES = [n["name"] for n in NAKSHATRAS]

# Vimshottari Dasha order and period lengths (years)
VIMSHOTTARI_DASHAS = [
    {"lord": "Ketu", "years": 7},
    {"lord": "Venus", "years": 20},
    {"lord": "Sun", "years": 6},
    {"lord": "Moon", "years": 10},
    {"lord": "Mars", "years": 7},
    {"lord": "Rahu", "years": 18},
    {"lord": "Jupiter", "years": 16},
    {"lord": "Saturn", "years": 19},
    {"lord": "Mercury", "years": 17},
]
TOTAL_VIMSHOTTARI_YEARS = 120

# 9 Grahas
GRAHAS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]

# Planetary Dignities
# Exaltation: (Sign, exact peak degree)
EXALTATION: Dict[str, Tuple[str, float]] = {
    "Sun": ("Aries", 10.0),
    "Moon": ("Taurus", 3.0),
    "Mars": ("Capricorn", 28.0),
    "Mercury": ("Virgo", 15.0),
    "Jupiter": ("Cancer", 5.0),
    "Venus": ("Pisces", 27.0),
    "Saturn": ("Libra", 20.0),
    "Rahu": ("Taurus", 20.0),      # Classical / Parashari school consensus
    "Ketu": ("Scorpio", 20.0),
}

# Debilitation: Opposite sign, exact deep debilitation degree
DEBILITATION: Dict[str, Tuple[str, float]] = {
    "Sun": ("Libra", 10.0),
    "Moon": ("Scorpio", 3.0),
    "Mars": ("Cancer", 28.0),
    "Mercury": ("Pisces", 15.0),
    "Jupiter": ("Capricorn", 5.0),
    "Venus": ("Virgo", 27.0),
    "Saturn": ("Aries", 20.0),
    "Rahu": ("Scorpio", 20.0),
    "Ketu": ("Taurus", 20.0),
}

# Moolatrikona: (Sign, start_degree, end_degree)
MOOLATRIKONA: Dict[str, Tuple[str, float, float]] = {
    "Sun": ("Leo", 0.0, 20.0),
    "Moon": ("Taurus", 3.0, 30.0),
    "Mars": ("Aries", 0.0, 12.0),
    "Mercury": ("Virgo", 15.0, 20.0),
    "Jupiter": ("Sagittarius", 0.0, 10.0),
    "Venus": ("Libra", 0.0, 15.0),
    "Saturn": ("Aquarius", 0.0, 20.0),
}

# Own Signs
OWN_SIGNS: Dict[str, List[str]] = {
    "Sun": ["Leo"],
    "Moon": ["Cancer"],
    "Mars": ["Aries", "Scorpio"],
    "Mercury": ["Gemini", "Virgo"],
    "Jupiter": ["Sagittarius", "Pisces"],
    "Venus": ["Taurus", "Libra"],
    "Saturn": ["Capricorn", "Aquarius"],
    "Rahu": ["Aquarius"],  # Co-lord according to classical texts
    "Ketu": ["Scorpio"],   # Co-lord according to classical texts
}

# Planetary Relationships (Naisargika Mitra, Shatru, Sama - BPHS Ch. 3)
NATURAL_FRIENDS: Dict[str, List[str]] = {
    "Sun": ["Moon", "Mars", "Jupiter"],
    "Moon": ["Sun", "Mercury"],
    "Mars": ["Sun", "Moon", "Jupiter"],
    "Mercury": ["Sun", "Venus"],
    "Jupiter": ["Sun", "Moon", "Mars"],
    "Venus": ["Mercury", "Saturn"],
    "Saturn": ["Mercury", "Venus"],
    "Rahu": ["Venus", "Saturn", "Mercury"],
    "Ketu": ["Mars", "Venus"],
}

NATURAL_ENEMIES: Dict[str, List[str]] = {
    "Sun": ["Venus", "Saturn"],
    "Moon": [],
    "Mars": ["Mercury"],
    "Mercury": ["Moon"],
    "Jupiter": ["Mercury", "Venus"],
    "Venus": ["Sun", "Moon"],
    "Saturn": ["Sun", "Moon", "Mars"],
    "Rahu": ["Sun", "Moon", "Mars"],
    "Ketu": ["Sun", "Moon"],
}

# Classical Special Aspects (in houses counted from planet)
# All planets aspect 7th house (100% full drishti)
SPECIAL_ASPECTS: Dict[str, List[int]] = {
    "Sun": [7],
    "Moon": [7],
    "Mars": [4, 7, 8],
    "Mercury": [7],
    "Jupiter": [5, 7, 9],
    "Venus": [7],
    "Saturn": [3, 7, 10],
    "Rahu": [5, 7, 9],
    "Ketu": [5, 7, 9],
}

# Kendra, Trikona, Dusthana, Upachaya houses from Lagna
KENDRA_HOUSES = [1, 4, 7, 10]
TRIKONA_HOUSES = [1, 5, 9]
DUSTHANA_HOUSES = [6, 8, 12]
UPACHAYA_HOUSES = [3, 6, 10, 11]
MARAKA_HOUSES = [2, 7]

# Ashtakavarga benefic places (Parashara System)
# For each planet (Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn),
# houses from [Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn, Lagna] where it contributes 1 bindu
ASHTAKAVARGA_RULES: Dict[str, Dict[str, List[int]]] = {
    "Sun": {
        "Sun": [1, 2, 4, 7, 8, 9, 10, 11],
        "Moon": [3, 6, 10, 11],
        "Mars": [1, 2, 4, 7, 8, 9, 10, 11],
        "Mercury": [3, 5, 6, 9, 10, 11, 12],
        "Jupiter": [5, 6, 9, 11],
        "Venus": [6, 7, 12],
        "Saturn": [1, 2, 4, 7, 8, 9, 10, 11],
        "Lagna": [3, 4, 6, 10, 11, 12],
    },
    "Moon": {
        "Sun": [3, 6, 7, 8, 10, 11],
        "Moon": [1, 3, 6, 7, 10, 11],
        "Mars": [2, 3, 5, 6, 9, 10, 11],
        "Mercury": [1, 3, 4, 5, 7, 8, 10, 11],
        "Jupiter": [1, 4, 7, 8, 10, 11, 12],
        "Venus": [3, 4, 5, 7, 9, 10, 11],
        "Saturn": [3, 5, 6, 11],
        "Lagna": [3, 6, 10, 11],
    },
    "Mars": {
        "Sun": [3, 5, 6, 10, 11],
        "Moon": [3, 6, 11],
        "Mars": [1, 2, 4, 7, 8, 10, 11],
        "Mercury": [3, 5, 6, 11],
        "Jupiter": [6, 10, 11, 12],
        "Venus": [6, 8, 11, 12],
        "Saturn": [1, 4, 7, 8, 9, 10, 11],
        "Lagna": [1, 3, 6, 10, 11],
    },
    "Mercury": {
        "Sun": [5, 6, 9, 11, 12],
        "Moon": [2, 4, 6, 8, 10, 11],
        "Mars": [1, 2, 4, 7, 8, 9, 10, 11],
        "Mercury": [1, 3, 5, 6, 9, 10, 11, 12],
        "Jupiter": [6, 8, 11, 12],
        "Venus": [1, 2, 3, 4, 5, 8, 9, 11],
        "Saturn": [1, 2, 4, 7, 8, 9, 10, 11],
        "Lagna": [1, 2, 4, 6, 8, 10, 11],
    },
    "Jupiter": {
        "Sun": [1, 2, 3, 4, 7, 8, 9, 10, 11],
        "Moon": [2, 5, 7, 9, 11],
        "Mars": [1, 2, 4, 7, 8, 10, 11],
        "Mercury": [1, 2, 4, 5, 6, 9, 10, 11],
        "Jupiter": [1, 2, 3, 4, 7, 8, 10, 11],
        "Venus": [2, 5, 6, 9, 10, 11],
        "Saturn": [3, 5, 6, 12],
        "Lagna": [1, 2, 4, 5, 6, 7, 9, 10, 11],
    },
    "Venus": {
        "Sun": [8, 11, 12],
        "Moon": [1, 2, 3, 4, 5, 8, 9, 11, 12],
        "Mars": [3, 5, 6, 9, 11, 12],
        "Mercury": [3, 5, 6, 9, 11],
        "Jupiter": [5, 8, 9, 10, 11],
        "Venus": [1, 2, 3, 4, 5, 8, 9, 10, 11],
        "Saturn": [3, 4, 5, 8, 9, 10, 11],
        "Lagna": [1, 2, 3, 4, 5, 8, 9, 11],
    },
    "Saturn": {
        "Sun": [1, 2, 4, 7, 8, 10, 11],
        "Moon": [3, 6, 11],
        "Mars": [3, 5, 6, 10, 11, 12],
        "Mercury": [6, 8, 9, 10, 11, 12],
        "Jupiter": [5, 6, 11, 12],
        "Venus": [6, 11, 12],
        "Saturn": [3, 5, 6, 11],
        "Lagna": [1, 3, 4, 6, 10, 11],
    },
}

