"""
Modernized Birth Input Controls & Astrological Selector Components (Phase 6, Task P6-T1).
Reference: docs/IMPLEMENTATION_PRD.md (Section 3.6 & 5.5, P6-T1).

Features:
1. Place autocomplete with ambiguity prompting (latitude, longitude, state/country resolution).
2. Timezone historical notes (e.g. India War Time UTC+6.5 in 1942-1945, pre-1906 LMT, foreign DST).
3. Birth-time confidence level selector (Exact, Approx ±15m, Approx ±1h, Unknown/BTR).
4. Sane defaults and descriptive tooltips for Ayanamsa, House System, Lunar Node, and Astrological School.
"""

from typing import Dict, List, Optional, Tuple, Any
from datetime import date, time, datetime


# ---------------------------------------------------------------------------
# 1. METADATA CATALOGUES WITH SANED DEFAULTS & SCHOLARLY TOOLTIPS
# ---------------------------------------------------------------------------

BIRTH_CONFIDENCE_LEVELS = [
    {
        "id": "exact",
        "label": "Exact (< 2 min) — जन्म प्रमाण पत्र / घड़ी समय",
        "description": "Hospital record or clock verified to within 2 minutes. Safe for D9/D10 and sub-lord analysis.",
        "short_name": "Exact"
    },
    {
        "id": "approx_15m",
        "label": "Approx (±15 min) — पारिवारिक स्मरण",
        "description": "Family memory within a 15-minute window. Reliable for D1/Rashi; D9 and cusps require BTR verification.",
        "short_name": "Approx (±15 min)"
    },
    {
        "id": "approx_1h",
        "label": "Approx (±1 hour) — पहर / बेला आधारित",
        "description": "Morning/evening approximate estimate. Lagna rashi may be uncertain; rectification required.",
        "short_name": "Approx (±1 hour)"
    },
    {
        "id": "unknown",
        "label": "Unknown — समय अज्ञात (जन्म समय शोधन आवश्यक)",
        "description": "Exact hour unknown. Chandra Kundali and Prashna analysis recommended prior to full rectification.",
        "short_name": "Unknown"
    }
]

AYANAMSA_CATALOGUE = {
    "Lahiri": {
        "label": "Lahiri (Chitra Paksha) — भारत सरकार मानक",
        "tooltip": "Govt of India Calendar Reform Committee standard (1955). Spica fixed at 180°00'. Canonical Parashari default.",
        "is_default": True
    },
    "Pushya-Paksha (PVR Rao)": {
        "label": "Pushya-Paksha (PVR Rao)",
        "tooltip": "Pushya star fixed at exactly 106°00'. Research standard formulated by P.V.R. Narasimha Rao.",
        "is_default": False
    },
    "KP New (Straight Line)": {
        "label": "KP New (Straight Line)",
        "tooltip": "Modern straight-line ayanamsa standard for Krishnamurti Paddhati cuspal sub-lord timing.",
        "is_default": False
    },
    "KP Old": {
        "label": "KP Old",
        "tooltip": "Traditional KP ayanamsa authored by Prof. K.S. Krishnamurti.",
        "is_default": False
    },
    "Raman": {
        "label": "Raman (B.V. Raman)",
        "tooltip": "Ayanamsa computed according to Dr. B.V. Raman's traditional studies.",
        "is_default": False
    },
    "True Chitra (Spica 180°)": {
        "label": "True Chitra (Spica 180°)",
        "tooltip": "Exact instantaneous astronomical position of Spica (Chitra nakshatra) fixed at 180°.",
        "is_default": False
    },
    "Yukteshwar": {
        "label": "Yukteshwar (The Holy Science)",
        "tooltip": "Ayanamsa based on Sri Yukteshwar Giri's cosmic cycle calculations in 'The Holy Science'.",
        "is_default": False
    },
    "Fagan-Bradley": {
        "label": "Fagan-Bradley (Western Sidereal)",
        "tooltip": "Western sidereal astrological standard based on Cyril Fagan and Donald Bradley research.",
        "is_default": False
    }
}

HOUSE_SYSTEM_CATALOGUE = {
    "Whole Sign": {
        "label": "Whole Sign (समग्र राशि = एक भाव)",
        "tooltip": "Canonical Vedic Parashari & Jaimini standard. The entire rashi of the Ascendant degree is House 1.",
        "is_default": True
    },
    "Placidus": {
        "label": "Placidus (के.पी. पद्धति मानक)",
        "tooltip": "Semi-arc diurnal time division. Mandatory cuspal foundation for Krishnamurti Paddhati (KP).",
        "is_default": False
    },
    "Shripati": {
        "label": "Shripati (भाव चलित मध्यमान)",
        "tooltip": "Porphyry-style cusp midpoints. Classical foundation for Shripati Bhav Chalit charts in North India.",
        "is_default": False
    },
    "Equal": {
        "label": "Equal (समान ३०° भाव)",
        "tooltip": "Equal 30-degree arcs measured directly starting from the exact Ascendant degree.",
        "is_default": False
    },
    "Koch": {
        "label": "Koch (GOHS - जन्मस्थान अहोरात्र)",
        "tooltip": "Birthplace diurnal quadrant system based on the Koch system.",
        "is_default": False
    }
}

NODE_TYPE_CATALOGUE = {
    "mean": {
        "label": "Mean Node (पारंपरिक औसत पात)",
        "tooltip": "Uniform circular mean lunar orbit calculation. Canonical Vedic standard in BPHS and Surya Siddhanta.",
        "is_default": True
    },
    "true": {
        "label": "True Node (सच्चे पात - Meeus)",
        "tooltip": "Instantaneous osculating astronomical lunar node accounting for solar and planetary gravitational perturbations.",
        "is_default": False
    }
}

ASTRO_SCHOOLS_CATALOGUE = {
    "parashari": {
        "label": "Parashari (पाराशरी ज्योतिष)",
        "tooltip": "Foundation of Vedic astrology based on Maharishi Parashara: Bhavas, Shadbala, Vargas, Vimshottari Dasha.",
        "is_default": True
    },
    "jaimini": {
        "label": "Jaimini (जैमिनी सूत्र)",
        "tooltip": "Sutra tradition by Maharishi Jaimini: Chara Karakas, Arudha Padas, Chara Dasha, and Karakamsha.",
        "is_default": False
    },
    "kp": {
        "label": "KP (कृष्णमूर्ति पद्धति)",
        "tooltip": "Stellar system by Prof. K.S. Krishnamurti: Placidus cusps, sub-lords, 4-fold significators & 249 horary numbers.",
        "is_default": False
    },
    "tajika": {
        "label": "Tajika (ताजिक वर्षफल)",
        "tooltip": "Medieval annual solar return system: Varshaphal, Muntha, Sahams, Varshesha, and Mudda Dasha.",
        "is_default": False
    },
    "lalkitab": {
        "label": "Lal Kitab 1952 (लाल किताब)",
        "tooltip": "Peshawar 1952 classical urdu treatise: Fixed 12 houses, 9 karmic debts, artificial planets & sattvic totkas.",
        "is_default": False
    }
}


# ---------------------------------------------------------------------------
# 2. HISTORICAL TIMEZONE & DST ANOMALY DETECTOR
# ---------------------------------------------------------------------------

def get_historical_tz_note(birth_date: date, timezone_offset: float = 5.5, country_hint: str = "IN") -> Dict[str, Any]:
    """
    Evaluates whether the birth date falls into known historical timezone anomalies
    (such as British India War Time UTC+6.5 during WWII, pre-1906 LMT, or seasonal DST).
    """
    notes = []
    has_anomaly = False
    suggested_offset = timezone_offset

    # India checks
    if country_hint.upper() in ("IN", "INDIA"):
        # 1. India War Time (1942-09-01 to 1945-10-15): UTC+6:30
        war_start = date(1942, 9, 1)
        war_end = date(1945, 10, 15)
        if war_start <= birth_date <= war_end:
            has_anomaly = True
            suggested_offset = 6.5
            notes.append(
                "⚠️ **ऐतिहासिक युद्ध-समय (India War Time Note):** १ सितम्बर १९४२ से १५ अक्टूबर १९४५ के मध्य "
                "ब्रिटिश भारत में ग्रीष्मकालीन रक्षा हेतु मानक समय UTC+6:30 (+6.5 घंटे) लागू था। "
                "यदि जन्म समय भारतीय मानक समय (IST) के अनुसार रिकॉर्ड किया गया है, तो UTC+6.5 प्रयुक्त होना चाहिए।"
            )

        # 2. Pre-1906 Local Mean Time (LMT)
        if birth_date < date(1906, 1, 1):
            has_anomaly = True
            notes.append(
                "📜 **स्थानीय मध्यम समय (Pre-1906 LMT Note):** १ जनवरी १९०६ से पूर्व भारत में एकसमान "
                "IST (+5:30) आधिकारिक रूप से अनिवार्य नहीं था। उस काल में कोलकाता (+5:53), मद्रास (+5:21), "
                "या बॉम्बे (+4:51) का स्थानीय मध्यम समय (LMT) प्रयुक्त होता था। जन्मस्थान के देशांतर अनुसार समय जांचें।"
            )

    # Foreign DST check hint
    if timezone_offset != 5.5:
        notes.append(
            "🌐 **विदेशी समय क्षेत्र / DST सूचना (Foreign TZ Notice):** "
            f"वर्तमान ऑफसेट UTC{'+' if timezone_offset >= 0 else ''}{timezone_offset:.2f} घंटे है। "
            "कृपया सुनिश्चित करें कि जन्म तिथि पर स्थानीय डेलाइट सेविंग टाइम (DST) प्रभावी था या नहीं।"
        )

    return {
        "has_anomaly": has_anomaly,
        "suggested_offset": suggested_offset,
        "notes": notes
    }


# ---------------------------------------------------------------------------
# 3. GEOGRAPHIC SEARCH AMBIGUITY EVALUATOR
# ---------------------------------------------------------------------------

def evaluate_geo_ambiguity(search_results: List[Any], query: str) -> Dict[str, Any]:
    """
    Determines if a location query is ambiguous (e.g. multiple cities with identical names
    in different districts, states, or countries) and generates resolution prompt data.
    """
    if not search_results:
        return {
            "is_ambiguous": False,
            "count": 0,
            "prompt": "कोई स्थान नहीं मिला। कृपया मैन्युअल अक्षांश/देशांतर दर्ज करें।"
        }

    if len(search_results) == 1:
        return {
            "is_ambiguous": False,
            "count": 1,
            "prompt": None
        }

    # Check for homonyms (same city name in different regions)
    names = [getattr(r, "city", "").strip().lower() for r in search_results if hasattr(r, "city")]
    unique_names = set(names)

    is_homonym = (len(names) > 1 and len(unique_names) < len(names))
    prompt = None
    if is_homonym:
        prompt = (
            f"🔍 '{query}' नाम से एक से अधिक नगर उपलब्ध हैं। "
            "सटीक कुण्डली हेतु कृपया नीचे सूची से सही राज्य/जिला एवं देश का चयन करें।"
        )

    return {
        "is_ambiguous": is_homonym or len(search_results) > 1,
        "count": len(search_results),
        "prompt": prompt
    }
