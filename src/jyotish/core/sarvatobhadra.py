"""
Sarvatobhadra Chakra (81-Cell Multi-Dimensional Vedha Engine) for JyotishOS.
According to classical Narapatijayacharya Swarodaya and Mansagari:
1. 9x9 = 81 Kosthas (cells) arranged concentrically.
2. 28 Nakshatras including Abhijit (placed between Uttara Ashadha and Shravana: Capricorn 6°40' to 10°53'20").
3. 12 Rashis, 16 Vowels (Swaras), 20 Consonants, and 5 Tithi classes (Nanda, Bhadra, Jaya, Rikta, Purna).
4. 3 Classical Vedhas:
   - Frontal (Agra / Samukha Vedha)
   - Left Diagonal (Vama Vedha)
   - Right Diagonal (Dakshina Vedha)
5. Sensitive Nakshatras:
   - Janma (1st), Karma (10th), Sanghatika (16th), Samudayika (18th),
   - Aadhana (19th), Vainashika (23rd), Manasa (25th), Raja (26th), Abhisheka (27th).
"""

from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from .constants import SIGN_NAMES
from .models import KundaliChart, PlanetPosition


# 28 Nakshatras in classical Sarvatobhadra order starting from Krittika (East)
SARVATOBHADRA_28_NAKSHATRAS = [
    # East (Top row: 7 nakshatras)
    "Krittika", "Rohini", "Mrigashira", "Ardra", "Punarvasu", "Pushya", "Ashlesha",
    # South (Right column: 7 nakshatras)
    "Magha", "Purva Phalguni", "Uttara Phalguni", "Hasta", "Chitra", "Swati", "Vishakha",
    # West (Bottom row: 7 nakshatras)
    "Anuradha", "Jyeshtha", "Mula", "Purva Ashadha", "Uttara Ashadha", "Abhijit", "Shravana",
    # North (Left column: 7 nakshatras)
    "Dhanishta", "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada", "Revati", "Ashwini", "Bharani"
]

NAKSHATRA_NAMES_HI = {
    "Krittika": "कृत्तिका", "Rohini": "रोहिणी", "Mrigashira": "मृगशिरा", "Ardra": "आर्द्रा",
    "Punarvasu": "पुनर्वसु", "Pushya": "पुष्य", "Ashlesha": "आश्लेषा", "Magha": "मघा",
    "Purva Phalguni": "पूर्वाफाल्गुनी", "Uttara Phalguni": "उत्तराफाल्गुनी", "Hasta": "हस्त",
    "Chitra": "चित्रा", "Swati": "स्वाति", "Vishakha": "विशाखा", "Anuradha": "अनुराधा",
    "Jyeshtha": "ज्येष्ठा", "Mula": "मूल", "Purva Ashadha": "पूर्वाषाढ़ा", "Uttara Ashadha": "उत्तराषाढ़ा",
    "Abhijit": "अभिजीत", "Shravana": "श्रवण", "Dhanishta": "धनिष्ठा", "Shatabhisha": "शतभिषा",
    "Purva Bhadrapada": "पूर्वाभाद्रपद", "Uttara Bhadrapada": "उत्तराभाद्रपद", "Revati": "रेवती",
    "Ashwini": "अश्विनी", "Bharani": "भरणी"
}

SPECIAL_NAKSHATRA_OFFSETS = {
    1: ("जन्म नक्षत्र (Janma)", "शरीर, स्वास्थ्य व मूल व्यक्तित्व पर प्रभाव"),
    10: ("कर्म नक्षत्र (Karma)", "कार्यक्षेत्र, आजीविका व प्रतिष्ठा पर प्रभाव"),
    16: ("सांघातिक नक्षत्र (Sanghatika)", "साझेदारी, गठबंधन व मित्रों से संबंध"),
    18: ("सामुदायिक नक्षत्र (Samudayika)", "कुटुंब, समाज व सामूहिक कल्याण"),
    19: ("आधान नक्षत्र (Aadhana)", "मानसिक शांति, मूल आधार व स्थिरता"),
    23: ("विनाश नक्षत्र (Vainashika)", "अकस्मात संकट, हानि व सावधानी क्षेत्र"),
    25: ("मानस नक्षत्र (Manasa)", "मन, आंतरिक संकल्प व मनोबल"),
    26: ("राज नक्षत्र (Raja)", "प्रशासनिक कृपा, राज्यसम्मान व सत्ता"),
    27: ("अभिषेक नक्षत्र (Abhisheka)", "विजय, प्रतिष्ठा व राज्याभिषेक")
}


@dataclass
class VedhaTarget:
    nakshatra_name: str
    nakshatra_hi: str
    special_role: Optional[str]
    vedha_type: str  # 'अग्र वेध (Frontal)', 'दक्षिण वेध (Right Diagonal)', 'वाम वेध (Left Diagonal)'
    aspecting_planet: str
    is_malefic: bool
    influence: str


class SarvatobhadraChakraEngine:
    """81-cell Sarvatobhadra Chakra and Multi-directional Vedha Analyzer."""

    @staticmethod
    def get_28_nakshatra_for_longitude(longitude: float) -> Tuple[str, int]:
        """
        Calculates which of the 28 Nakshatras (including Abhijit) a degree occupies:
        Abhijit spans Capricorn 6°40' to 10°53'20" (276°40' to 280°53'20" = 276.6667° to 280.8889°).
        Returns (nakshatra_name, index_0_to_27).
        """
        lon = longitude % 360.0

        # Abhijit special bracket: 276°40' to 280°53'20"
        if 276.666667 <= lon < 280.888889:
            return "Abhijit", 19

        # Standard 27 nakshatras
        span_27 = 360.0 / 27.0
        n_27_idx = int(lon // span_27)  # 0 to 26 (0 is Ashwini)

        standard_names = [
            "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
            "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni",
            "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
            "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha",
            "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
        ]
        n_name = standard_names[n_27_idx]
        idx_28 = SARVATOBHADRA_28_NAKSHATRAS.index(n_name)
        return n_name, idx_28

    @classmethod
    def calculate_chakra_vedha(
        cls,
        chart: KundaliChart,
        transit_chart: Optional[KundaliChart] = None
    ) -> Dict[str, Any]:
        """
        Calculates all active Vedhas on the natal chart from transit or natal planets.
        Uses classical 28-nakshatra directional lines.
        """
        eval_chart = transit_chart or chart
        is_transit = transit_chart is not None

        # 1. Determine Native's Janma Nakshatra in 28-nakshatra wheel
        moon_lon = chart.planets["Moon"].longitude
        janma_nak, janma_idx = cls.get_28_nakshatra_for_longitude(moon_lon)

        # 2. Map Native's 9 Sensitive Nakshatras
        sensitive_nakshatras: Dict[str, str] = {}
        for offset, (role_name, desc) in SPECIAL_NAKSHATRA_OFFSETS.items():
            target_idx = (janma_idx + offset - 1) % 28
            target_name = SARVATOBHADRA_28_NAKSHATRAS[target_idx]
            sensitive_nakshatras[target_name] = role_name

        # 3. Analyze Vedha from each planet
        vedha_results: List[VedhaTarget] = []
        planet_positions_28: Dict[str, Dict[str, Any]] = {}

        malefics = {"Sun", "Mars", "Saturn", "Rahu", "Ketu"}

        for p_name, p_obj in eval_chart.planets.items():
            nak_name, nak_idx = cls.get_28_nakshatra_for_longitude(p_obj.longitude)
            is_mal = p_name in malefics

            planet_positions_28[p_name] = {
                "nakshatra": nak_name,
                "nakshatra_hi": NAKSHATRA_NAMES_HI.get(nak_name, nak_name),
                "index": nak_idx,
                "is_malefic": is_mal,
                "longitude": round(p_obj.longitude, 2),
                "speed": getattr(p_obj, "speed", 0.0),
                "is_retrograde": getattr(p_obj, "is_retrograde", False)
            }

            # In the 28-nakshatra perimeter:
            # - Frontal Vedha: Exactly opposite (index + 14) % 28
            # - Right Diagonal Vedha: (index + 7) % 28
            # - Left Diagonal Vedha: (index - 7) % 28
            targets = [
                ((nak_idx + 14) % 28, "अग्र वेध (Frontal)"),
                ((nak_idx + 7) % 28, "दक्षिण वेध (Right Diagonal)"),
                ((nak_idx - 7) % 28, "वाम वेध (Left Diagonal)")
            ]

            for t_idx, v_type in targets:
                t_name = SARVATOBHADRA_28_NAKSHATRAS[t_idx]
                role = sensitive_nakshatras.get(t_name)

                if is_mal:
                    inf = f"⚠️ क्रूर वेध ({p_name} द्वारा): अवरोध, पीड़ा अथवा कार्य में विलंब।"
                else:
                    inf = f"🌟 सौम्य वेध ({p_name} द्वारा): सफलता, संरक्षण एवं शुभ फल प्राप्ति।"

                vedha_results.append(VedhaTarget(
                    nakshatra_name=t_name,
                    nakshatra_hi=NAKSHATRA_NAMES_HI.get(t_name, t_name),
                    special_role=role,
                    vedha_type=v_type,
                    aspecting_planet=p_name,
                    is_malefic=is_mal,
                    influence=inf
                ))

        # Filter only sensitive targets for executive briefing
        sensitive_vedhas = [v for v in vedha_results if v.special_role is not None]

        return {
            "janma_nakshatra_28": janma_nak,
            "janma_nakshatra_hi": NAKSHATRA_NAMES_HI.get(janma_nak, janma_nak),
            "sensitive_nakshatra_map": sensitive_nakshatras,
            "planet_positions_28": planet_positions_28,
            "all_vedhas": vedha_results,
            "sensitive_vedhas": sensitive_vedhas,
            "is_transit_mode": is_transit
        }
