"""
Divisional Charts (Shodashavarga) Engine for JyotishOS.
Implements classical algorithms from Brihat Parashara Hora Shastra (BPHS Ch. 6)
for D1, D2, D3, D7, D9, D10, D12, and D60.
"""

from typing import Dict, Tuple, Optional, Any, List
from .constants import SIGN_NAMES, SIGN_LORDS, EXALTATION, DEBILITATION, MOOLATRIKONA, OWN_SIGNS, NATURAL_FRIENDS, NATURAL_ENEMIES
from .models import VargaChart, VargaPlanetPosition, KundaliChart


D60_DEITIES = [
    "Ghora", "Rakshasa", "Deva", "Kubera", "Yaksha", "Kinnara", "Bhrashta", "Kulaghna", "Garala", "Vahni",
    "Maya", "Purishaka", "Apampati", "Marutvana", "Kaala", "Sarpa", "Amrita", "Indu", "Mridu", "Komala",
    "Heramba", "Brahma", "Vishnu", "Maheshwara", "Deva", "Ardra", "Kalinasha", "Kshiteesha", "Kamalakara", "Gulika",
    "Mrityu", "Kaala", "Davagni", "Ghora", "Adhama", "Kantaka", "Sudha", "Amrita", "Purnachandra", "Vishadagdha",
    "Kulanasha", "Vamshakshaya", "Utpata", "Kaala", "Saumya", "Komala", "Sheetala", "Karaladamshtra", "Chandramukhi", "Praveena",
    "Kalapavaka", "Dandayudha", "Nirmala", "Saumya", "Krura", "Atisheetala", "Amrita", "Payodhi", "Bhramana", "Chandrarekha"
]

D60_MALEFIC_INDICES = {
    0, 1, 6, 7, 8, 9, 10, 11, 14, 15, 25, 29, 30, 31, 32, 33, 34, 35, 39, 40, 41, 42, 43, 47, 50, 51, 54, 58
}

D60_DEITY_DESCRIPTIONS: Dict[str, Dict[str, str]] = {
    "Ghora": {"nature": "क्रूर (Malefic)", "phala": "दारुण कष्ट, उग्र स्वभाव व संघर्षमय प्रारब्ध।"},
    "Rakshasa": {"nature": "क्रूर (Malefic)", "phala": "तामसिक वृत्तियां, बाधाएं व हिंसक प्रवृत्तियां।"},
    "Deva": {"nature": "सौम्य (Benefic)", "phala": "दैवीय कृपा, धार्मिकता, सद्बुद्धि व यश।"},
    "Kubera": {"nature": "सौम्य (Benefic)", "phala": "प्रचुर धन, संपदा, कुबेर समान ऐश्वर्य व आदर।"},
    "Yaksha": {"nature": "सौम्य (Benefic)", "phala": "भौतिक आकर्षण, कला, सौंदर्य व संचित संपदा।"},
    "Kinnara": {"nature": "सौम्य (Benefic)", "phala": "संगीत, काव्य, ललित कलाएं व मधुर व्यक्तित्व।"},
    "Bhrashta": {"nature": "क्रूर (Malefic)", "phala": "पदच्युति, अपव्यय, मार्गभ्रष्टता व संशय।"},
    "Kulaghna": {"nature": "क्रूर (Malefic)", "phala": "कुल व कुटुंब में विवाद, पारिवारिक कष्ट।"},
    "Garala": {"nature": "क्रूर (Malefic)", "phala": "विषतुल्य क्लेश, गुप्त व्याधि व मानसिक उद्वेग।"},
    "Vahni": {"nature": "क्रूर (Malefic)", "phala": "अग्नि भय, तीव्र क्रोध, पित्त विकार व ज्वर।"},
    "Maya": {"nature": "क्रूर (Malefic)", "phala": "कपट, मायाजाल, भ्रम व मिथ्या आकर्षण।"},
    "Purishaka": {"nature": "क्रूर (Malefic)", "phala": "मलिनता, अस्वच्छता, रोग व दरिद्रता।"},
    "Apampati": {"nature": "सौम्य (Benefic)", "phala": "वरुण देव कृपा, जल यात्रा, शांति व सौम्यता।"},
    "Marutvana": {"nature": "क्रूर (Malefic)", "phala": "वात व्याधि, अस्थिरता, निरंतर भ्रमण व चिंता।"},
    "Kaala": {"nature": "क्रूर (Malefic)", "phala": "काल का कठोर दंड, संकट, भय व अवरोध।"},
    "Sarpa": {"nature": "क्रूर (Malefic)", "phala": "सर्प भय, गुप्त शत्रु, कुटिलता व विष प्रकोप।"},
    "Amrita": {"nature": "सौम्य (Benefic)", "phala": "अमृत समान आरोग्य, दीर्घायु, शांति व सुख।"},
    "Indu": {"nature": "सौम्य (Benefic)", "phala": "चंद्र समान शांति, शीतलता, कांति व लोकप्रियता।"},
    "Mridu": {"nature": "सौम्य (Benefic)", "phala": "कोमल हृदय, विनम्रता, दयालुता व लोकसम्मान।"},
    "Komala": {"nature": "सौम्य (Benefic)", "phala": "सुकुमारता, शारीरिक सौंदर्य व मधुर वाणी।"},
    "Heramba": {"nature": "सौम्य (Benefic)", "phala": "श्री गणेश कृपा, विघ्न विनाश, बुद्धि व सिद्धि।"},
    "Brahma": {"nature": "सौम्य (Benefic)", "phala": "सृष्टि ज्ञान, उच्च विद्या, वेद निष्ठा व तप।"},
    "Vishnu": {"nature": "सौम्य (Benefic)", "phala": "पालन सामर्थ्य, ऐश्वर्य, राजकृपा व धर्मनिष्ठा।"},
    "Maheshwara": {"nature": "सौम्य (Benefic)", "phala": "शिव कृपा, वैराग्य, मोक्ष मार्ग व दिव्य ज्ञान।"},
    "Ardra": {"nature": "क्रूर (Malefic)", "phala": "तीव्र शोक, अश्रुपात, संताप व मानसिक वेदना।"},
    "Kalinasha": {"nature": "सौम्य (Benefic)", "phala": "कलह का नाश, धर्म विजय, शांति व शुद्धि।"},
    "Kshiteesha": {"nature": "सौम्य (Benefic)", "phala": "भूमि स्वामित्व, राजतुल्य अधिकार व उच्च पद।"},
    "Kamalakara": {"nature": "सौम्य (Benefic)", "phala": "लक्ष्मी का अक्षय निवास, धन-धान्य व वैभव।"},
    "Gulika": {"nature": "क्रूर (Malefic)", "phala": "शनि पुत्र गुलिक प्रभाव, मरणतुल्य कष्ट व पीड़ा।"},
    "Mrityu": {"nature": "क्रूर (Malefic)", "phala": "मारक बाधा, भय, दुर्घटना व क्षीणता।"},
    "Davagni": {"nature": "क्रूर (Malefic)", "phala": "दावाग्नि समान आकस्मिक विपत्ति व विनाश।"},
    "Adhama": {"nature": "क्रूर (Malefic)", "phala": "नीच संगति, अपयश व आत्मग्लानि।"},
    "Kantaka": {"nature": "क्रूर (Malefic)", "phala": "कंटकमय जीवन, मार्ग में अवरोध व तीक्ष्ण कष्ट।"},
    "Sudha": {"nature": "सौम्य (Benefic)", "phala": "परम तृप्ति, सुधापान, आरोग्य व मनःशांति।"},
    "Purnachandra": {"nature": "सौम्य (Benefic)", "phala": "पूर्ण चंद्र समान मानसिक शांति, यश व सुख।"},
    "Vishadagdha": {"nature": "क्रूर (Malefic)", "phala": "आहत मन, विष का प्रभाव व कटु अनुभव।"},
    "Kulanasha": {"nature": "क्रूर (Malefic)", "phala": "कुल में विघ्न, संतति कष्ट व अलगाव।"},
    "Vamshakshaya": {"nature": "क्रूर (Malefic)", "phala": "वंश वृद्धि में मंदता, क्लेश व चिंता।"},
    "Utpata": {"nature": "क्रूर (Malefic)", "phala": "आकस्मिक उपद्रव, अनहोनी व उथल-पुथल।"},
    "Saumya": {"nature": "सौम्य (Benefic)", "phala": "बुद्धियुक्त, सौम्य व्यवहार, शांति व प्रतिष्ठा।"},
    "Sheetala": {"nature": "सौम्य (Benefic)", "phala": "शीतलता, ताप निवारण, संतोष व आनंद।"},
    "Karaladamshtra": {"nature": "क्रूर (Malefic)", "phala": "भयावह परिस्थितियां, शत्रु भय व कठोरता।"},
    "Chandramukhi": {"nature": "सौम्य (Benefic)", "phala": "चंद्र समान मुख कांति, आकर्षण व सर्वप्रियता।"},
    "Praveena": {"nature": "सौम्य (Benefic)", "phala": "सर्व कार्य कुशलता, निपुणता, चातुर्य व सफलता।"},
    "Kalapavaka": {"nature": "क्रूर (Malefic)", "phala": "प्रलय अग्नि समान संहारक संकट व हानि।"},
    "Dandayudha": {"nature": "क्रूर (Malefic)", "phala": "न्याय दंड, राजदंड भय, अस्त्र-शस्त्र पीड़ा।"},
    "Nirmala": {"nature": "सौम्य (Benefic)", "phala": "निष्कलंक चरित्र, निर्मल बुद्धि व सात्विक यश।"},
    "Krura": {"nature": "क्रूर (Malefic)", "phala": "क्रूर परिणाम, कठोर निर्णय व संघर्ष।"},
    "Atisheetala": {"nature": "सौम्य (Benefic)", "phala": "परम शांत चित्त, आधि-व्याधि से मुक्ति।"},
    "Payodhi": {"nature": "सौम्य (Benefic)", "phala": "क्षीरसागर समान गंभीरता, अकूत संपदा व कृपा।"},
    "Bhramana": {"nature": "क्रूर (Malefic)", "phala": "अनावश्यक देशाटन, व्यर्थ भटकाव व अस्थिरता।"},
    "Chandrarekha": {"nature": "सौम्य (Benefic)", "phala": "द्वितीया के चंद्र समान नित्य वर्धमान सौभाग्य।"}
}

SHODASHAVARGA_CODES = [
    "D1", "D2", "D3", "D4", "D7", "D9", "D10", "D12",
    "D16", "D20", "D24", "D27", "D30", "D40", "D45", "D60"
]

VAISHESHIKAMSA_BENCHMARKS = {
    2: "Parijata",
    3: "Uttama",
    4: "Gopura",
    5: "Simhasana",
    6: "Paravata",
    7: "Devaloka",
    8: "Kumkumamsha",
    9: "Airavata",
    10: "Vaisheshikamsa",
    11: "Goloka",
    12: "Vaikuntha",
    13: "Sarvathasiddha",
    14: "Kalpavriksha",
    15: "Brahmaloka",
    16: "Shridham",
}


class VargaCalculator:
    """Calculates Divisional Charts according to Parashara principles."""

    @staticmethod
    def calculate_d1(chart: KundaliChart) -> VargaChart:
        """D1 (Rashi Chart)."""
        planets: Dict[str, VargaPlanetPosition] = {}
        for name, p in chart.planets.items():
            planets[name] = VargaPlanetPosition(
                name=name,
                sign_id=p.sign_id,
                sign_name=p.sign_name,
                degree_in_varga=p.sign_degree,
                house_number=p.house_from_lagna
            )
        return VargaChart(
            varga_code="D1",
            varga_name="Rashi",
            division=1,
            lagna_sign_id=chart.lagna_sign_id,
            lagna_sign_name=chart.lagna_sign_name,
            planets=planets
        )

    @staticmethod
    def calculate_d2(chart: KundaliChart, variation: str = "parashari") -> VargaChart:
        """
        D2 (Hora Chart - Wealth & Prosperity).
        Variations:
          - 'parashari' (default): Odd signs: 0-15 Sun (Leo), 15-30 Moon (Cancer). Even: 0-15 Moon, 15-30 Sun.
          - 'parivritti': Cyclical 24 horas across the zodiac (Aries, Taurus, Gemini...).
        """
        def get_d2_sign(sign_id: int, deg: float) -> int:
            is_odd = (sign_id % 2 != 0)
            if variation == "parivritti":
                hora_idx = (sign_id - 1) * 2 + (0 if deg < 15.0 else 1)
                return (hora_idx % 12) + 1
            else:
                if is_odd:
                    return 5 if deg < 15.0 else 4
                else:
                    return 4 if deg < 15.0 else 5

        lagna_d2_sign = get_d2_sign(chart.lagna_sign_id, chart.lagna_degree)
        planets: Dict[str, VargaPlanetPosition] = {}

        for name, p in chart.planets.items():
            s_id = get_d2_sign(p.sign_id, p.sign_degree)
            house = ((s_id - lagna_d2_sign) % 12) + 1
            planets[name] = VargaPlanetPosition(
                name=name,
                sign_id=s_id,
                sign_name=SIGN_NAMES[s_id - 1],
                degree_in_varga=(p.sign_degree % 15.0) * 2.0,
                house_number=house
            )

        v_label = "Hora (Parivritti)" if variation == "parivritti" else "Hora (Parashari)"
        return VargaChart(
            varga_code="D2",
            varga_name=v_label,
            division=2,
            lagna_sign_id=lagna_d2_sign,
            lagna_sign_name=SIGN_NAMES[lagna_d2_sign - 1],
            planets=planets
        )

    @staticmethod
    def calculate_d9(chart: KundaliChart, variation: str = "parashari") -> VargaChart:
        """
        D9 (Navamsha Chart - Dharma, Marriage, Soul Strength).
        Variations:
          - 'parashari' (default): Continuous 108 padas.
          - 'krishna_mishra': Jaimini Krishna Mishra tradition (Movable from sign, Fixed from 9th, Dual from 5th).
        """
        def get_d9_sign(sign_id: int, deg: float, lon: float) -> int:
            if variation == "krishna_mishra":
                pada = min(8, int(deg // (30.0 / 9.0)))
                sign_type = sign_id % 3
                if sign_type == 1:
                    start = sign_id
                elif sign_type == 2:
                    start = ((sign_id - 1 + 8) % 12) + 1
                else:
                    start = ((sign_id - 1 + 4) % 12) + 1

                if sign_id % 2 != 0:
                    return ((start - 1 + pada) % 12) + 1
                else:
                    return ((start - 1 - pada) % 12) + 1
            else:
                # 108 navamshas in 360 degrees (Standard Parashari)
                pada_index = int((lon % 360.0) // (360.0 / 108.0))
                return (pada_index % 12) + 1

        lagna_d9_sign = get_d9_sign(chart.lagna_sign_id, chart.lagna_degree, chart.lagna_longitude)
        planets: Dict[str, VargaPlanetPosition] = {}

        for name, p in chart.planets.items():
            s_id = get_d9_sign(p.sign_id, p.sign_degree, p.longitude)
            house = ((s_id - lagna_d9_sign) % 12) + 1
            span = 360.0 / 108.0
            deg_in_varga = ((p.longitude % span) / span) * 30.0
            planets[name] = VargaPlanetPosition(
                name=name,
                sign_id=s_id,
                sign_name=SIGN_NAMES[s_id - 1],
                degree_in_varga=deg_in_varga,
                house_number=house
            )

        v_label = "Navamsha (Krishna Mishra)" if variation == "krishna_mishra" else "Navamsha (Parashari)"
        return VargaChart(
            varga_code="D9",
            varga_name=v_label,
            division=9,
            lagna_sign_id=lagna_d9_sign,
            lagna_sign_name=SIGN_NAMES[lagna_d9_sign - 1],
            planets=planets
        )

    @staticmethod
    def calculate_d10(chart: KundaliChart) -> VargaChart:
        """
        D10 (Dashamsha Chart - Profession, Career, Public Status).
        Each part = 3 deg (10 parts per sign).
        Odd signs: Starts from the sign itself.
        Even signs: Starts from the 9th sign from it.
        """
        def get_d10_sign(sign_id: int, deg: float) -> int:
            part = int(deg // 3.0)  # 0 to 9
            is_odd = (sign_id % 2 != 0)
            start_sign = sign_id if is_odd else (((sign_id - 1 + 8) % 12) + 1)
            target_sign = ((start_sign - 1 + part) % 12) + 1
            return target_sign

        lagna_d10_sign = get_d10_sign(chart.lagna_sign_id, chart.lagna_degree)
        planets: Dict[str, VargaPlanetPosition] = {}

        for name, p in chart.planets.items():
            s_id = get_d10_sign(p.sign_id, p.sign_degree)
            house = ((s_id - lagna_d10_sign) % 12) + 1
            deg_in_varga = ((p.sign_degree % 3.0) / 3.0) * 30.0
            planets[name] = VargaPlanetPosition(
                name=name,
                sign_id=s_id,
                sign_name=SIGN_NAMES[s_id - 1],
                degree_in_varga=deg_in_varga,
                house_number=house
            )

        return VargaChart(
            varga_code="D10",
            varga_name="Dashamsha",
            division=10,
            lagna_sign_id=lagna_d10_sign,
            lagna_sign_name=SIGN_NAMES[lagna_d10_sign - 1],
            planets=planets
        )

    @staticmethod
    def calculate_d7(chart: KundaliChart) -> VargaChart:
        """
        D7 (Saptamsha - Progeny, Creativity).
        Each part = 30/7 degrees ~ 4.285714 deg.
        Odd signs: Starts from the sign itself.
        Even signs: Starts from the 7th sign from it.
        """
        def get_d7_sign(sign_id: int, deg: float) -> int:
            span = 30.0 / 7.0
            part = int(deg // span)  # 0 to 6
            is_odd = (sign_id % 2 != 0)
            start_sign = sign_id if is_odd else (((sign_id - 1 + 6) % 12) + 1)
            target_sign = ((start_sign - 1 + part) % 12) + 1
            return target_sign

        lagna_d7_sign = get_d7_sign(chart.lagna_sign_id, chart.lagna_degree)
        planets: Dict[str, VargaPlanetPosition] = {}

        for name, p in chart.planets.items():
            s_id = get_d7_sign(p.sign_id, p.sign_degree)
            house = ((s_id - lagna_d7_sign) % 12) + 1
            span = 30.0 / 7.0
            deg_in_varga = ((p.sign_degree % span) / span) * 30.0
            planets[name] = VargaPlanetPosition(
                name=name,
                sign_id=s_id,
                sign_name=SIGN_NAMES[s_id - 1],
                degree_in_varga=deg_in_varga,
                house_number=house
            )

        return VargaChart(
            varga_code="D7",
            varga_name="Saptamsha",
            division=7,
            lagna_sign_id=lagna_d7_sign,
            lagna_sign_name=SIGN_NAMES[lagna_d7_sign - 1],
            planets=planets
        )

    @staticmethod
    def calculate_d3(chart: KundaliChart, variation: str = "parashari") -> VargaChart:
        """
        D3 (Drekkana - Siblings, Courage, Vitality). 3 parts of 10 deg.
        Variations:
          - 'parashari' (default): 1st, 5th, 9th from sign (BPHS Ch. 6)
          - 'jagannatha': Movable (1-5-9), Fixed (9-1-5), Dual (5-9-1)
          - 'somanatha': Odd signs direct count, Even signs reverse count
          - 'parivritti_traya': Continuous 36 decans from Aries
        """
        def get_d3_sign(sign_id: int, deg: float) -> int:
            part = min(2, int(deg // 10.0))  # 0, 1, 2

            if variation == "jagannatha":
                sign_type = sign_id % 3  # 1=Movable, 2=Fixed, 0=Dual
                if sign_type == 1:
                    offsets = [0, 4, 8]
                elif sign_type == 2:
                    offsets = [8, 0, 4]
                else:
                    offsets = [4, 8, 0]
                return ((sign_id - 1 + offsets[part]) % 12) + 1

            elif variation == "somanatha":
                is_odd = (sign_id % 2 != 0)
                if is_odd:
                    offsets = [0, 4, 8]
                else:
                    offsets = [0, 8, 4]  # Reverse direction
                return ((sign_id - 1 + offsets[part]) % 12) + 1

            elif variation == "parivritti_traya":
                total_part = (sign_id - 1) * 3 + part
                return (total_part % 12) + 1

            else:
                # Standard Parashari
                offsets = [0, 4, 8]
                return ((sign_id - 1 + offsets[part]) % 12) + 1

        lagna_d3 = get_d3_sign(chart.lagna_sign_id, chart.lagna_degree)
        planets: Dict[str, VargaPlanetPosition] = {}
        for name, p in chart.planets.items():
            s_id = get_d3_sign(p.sign_id, p.sign_degree)
            house = ((s_id - lagna_d3) % 12) + 1
            planets[name] = VargaPlanetPosition(
                name=name, sign_id=s_id, sign_name=SIGN_NAMES[s_id - 1],
                degree_in_varga=((p.sign_degree % 10.0) / 10.0) * 30.0,
                house_number=house
            )

        var_labels = {
            "jagannatha": "Drekkana (Jagannatha)",
            "somanatha": "Drekkana (Somanatha)",
            "parivritti_traya": "Drekkana (Parivritti Traya)",
            "parashari": "Drekkana (Parashari)"
        }
        v_name = var_labels.get(variation, "Drekkana (Parashari)")
        return VargaChart(varga_code="D3", varga_name=v_name, division=3,
                          lagna_sign_id=lagna_d3, lagna_sign_name=SIGN_NAMES[lagna_d3 - 1], planets=planets)

    @staticmethod
    def calculate_d4(chart: KundaliChart) -> VargaChart:
        """D4 (Chaturthamsha - Assets, Property, Home). 4 parts of 7.5 deg."""
        def get_d4_sign(sign_id: int, deg: float) -> int:
            part = int(deg // 7.5)  # 0, 1, 2, 3
            offsets = [0, 3, 6, 9]  # Same, 4th, 7th, 10th
            return ((sign_id - 1 + offsets[min(3, part)]) % 12) + 1

        lagna_d4 = get_d4_sign(chart.lagna_sign_id, chart.lagna_degree)
        planets: Dict[str, VargaPlanetPosition] = {}
        for name, p in chart.planets.items():
            s_id = get_d4_sign(p.sign_id, p.sign_degree)
            house = ((s_id - lagna_d4) % 12) + 1
            planets[name] = VargaPlanetPosition(
                name=name, sign_id=s_id, sign_name=SIGN_NAMES[s_id - 1],
                degree_in_varga=((p.sign_degree % 7.5) / 7.5) * 30.0,
                house_number=house
            )
        return VargaChart(varga_code="D4", varga_name="Chaturthamsha", division=4,
                          lagna_sign_id=lagna_d4, lagna_sign_name=SIGN_NAMES[lagna_d4 - 1], planets=planets)

    @staticmethod
    def calculate_d12(chart: KundaliChart) -> VargaChart:
        """D12 (Dwadashamsha - Parents, Ancestral Karma). 12 parts of 2.5 deg."""
        def get_d12_sign(sign_id: int, deg: float) -> int:
            part = int(deg // 2.5)  # 0 to 11
            return ((sign_id - 1 + part) % 12) + 1

        lagna_d12 = get_d12_sign(chart.lagna_sign_id, chart.lagna_degree)
        planets: Dict[str, VargaPlanetPosition] = {}
        for name, p in chart.planets.items():
            s_id = get_d12_sign(p.sign_id, p.sign_degree)
            house = ((s_id - lagna_d12) % 12) + 1
            planets[name] = VargaPlanetPosition(
                name=name, sign_id=s_id, sign_name=SIGN_NAMES[s_id - 1],
                degree_in_varga=((p.sign_degree % 2.5) / 2.5) * 30.0,
                house_number=house
            )
        return VargaChart(varga_code="D12", varga_name="Dwadashamsha", division=12,
                          lagna_sign_id=lagna_d12, lagna_sign_name=SIGN_NAMES[lagna_d12 - 1], planets=planets)

    @staticmethod
    def calculate_d16(chart: KundaliChart) -> VargaChart:
        """D16 (Shodashamsha - Vehicles, Luxuries, Inner Happiness). 16 parts of 1.875 deg."""
        def get_d16_sign(sign_id: int, deg: float) -> int:
            part = int(deg // 1.875)  # 0 to 15
            # Movable (1,4,7,10): Aries(1); Fixed (2,5,8,11): Leo(5); Dual (3,6,9,12): Sagittarius(9)
            m_type = (sign_id - 1) % 3
            start_sign = 1 if m_type == 0 else (5 if m_type == 1 else 9)
            return ((start_sign - 1 + part) % 12) + 1

        lagna_d16 = get_d16_sign(chart.lagna_sign_id, chart.lagna_degree)
        planets: Dict[str, VargaPlanetPosition] = {}
        for name, p in chart.planets.items():
            s_id = get_d16_sign(p.sign_id, p.sign_degree)
            house = ((s_id - lagna_d16) % 12) + 1
            planets[name] = VargaPlanetPosition(
                name=name, sign_id=s_id, sign_name=SIGN_NAMES[s_id - 1],
                degree_in_varga=((p.sign_degree % 1.875) / 1.875) * 30.0,
                house_number=house
            )
        return VargaChart(varga_code="D16", varga_name="Shodashamsha", division=16,
                          lagna_sign_id=lagna_d16, lagna_sign_name=SIGN_NAMES[lagna_d16 - 1], planets=planets)

    @staticmethod
    def calculate_d20(chart: KundaliChart) -> VargaChart:
        """D20 (Vimshamsha - Spiritual Evolution, Upasana). 20 parts of 1.5 deg."""
        def get_d20_sign(sign_id: int, deg: float) -> int:
            part = int(deg // 1.5)  # 0 to 19
            m_type = (sign_id - 1) % 3
            start_sign = 1 if m_type == 0 else (9 if m_type == 1 else 5)
            return ((start_sign - 1 + part) % 12) + 1

        lagna_d20 = get_d20_sign(chart.lagna_sign_id, chart.lagna_degree)
        planets: Dict[str, VargaPlanetPosition] = {}
        for name, p in chart.planets.items():
            s_id = get_d20_sign(p.sign_id, p.sign_degree)
            house = ((s_id - lagna_d20) % 12) + 1
            planets[name] = VargaPlanetPosition(
                name=name, sign_id=s_id, sign_name=SIGN_NAMES[s_id - 1],
                degree_in_varga=((p.sign_degree % 1.5) / 1.5) * 30.0,
                house_number=house
            )
        return VargaChart(varga_code="D20", varga_name="Vimshamsha", division=20,
                          lagna_sign_id=lagna_d20, lagna_sign_name=SIGN_NAMES[lagna_d20 - 1], planets=planets)

    @staticmethod
    def calculate_d24(chart: KundaliChart) -> VargaChart:
        """D24 (Chaturvimshamsha / Siddhamsa - Higher Learning, Intellect). 24 parts of 1.25 deg."""
        def get_d24_sign(sign_id: int, deg: float) -> int:
            part = int(deg // 1.25)
            is_odd = (sign_id % 2 != 0)
            start_sign = 5 if is_odd else 4  # Leo for odd, Cancer for even
            return ((start_sign - 1 + part) % 12) + 1

        lagna_d24 = get_d24_sign(chart.lagna_sign_id, chart.lagna_degree)
        planets: Dict[str, VargaPlanetPosition] = {}
        for name, p in chart.planets.items():
            s_id = get_d24_sign(p.sign_id, p.sign_degree)
            house = ((s_id - lagna_d24) % 12) + 1
            planets[name] = VargaPlanetPosition(
                name=name, sign_id=s_id, sign_name=SIGN_NAMES[s_id - 1],
                degree_in_varga=((p.sign_degree % 1.25) / 1.25) * 30.0,
                house_number=house
            )
        return VargaChart(varga_code="D24", varga_name="Chaturvimshamsha", division=24,
                          lagna_sign_id=lagna_d24, lagna_sign_name=SIGN_NAMES[lagna_d24 - 1], planets=planets)

    @staticmethod
    def calculate_d27(chart: KundaliChart) -> VargaChart:
        """D27 (Saptavimshamsha / Bhamsha - Subconscious Strengths & Vulnerabilities). 27 parts."""
        def get_d27_sign(sign_id: int, deg: float) -> int:
            span = 30.0 / 27.0
            part = int(deg // span)
            element = (sign_id - 1) % 4
            start_sign = 1 if element == 0 else (4 if element == 1 else (7 if element == 2 else 10))
            return ((start_sign - 1 + part) % 12) + 1

        lagna_d27 = get_d27_sign(chart.lagna_sign_id, chart.lagna_degree)
        planets: Dict[str, VargaPlanetPosition] = {}
        for name, p in chart.planets.items():
            s_id = get_d27_sign(p.sign_id, p.sign_degree)
            house = ((s_id - lagna_d27) % 12) + 1
            span = 30.0 / 27.0
            planets[name] = VargaPlanetPosition(
                name=name, sign_id=s_id, sign_name=SIGN_NAMES[s_id - 1],
                degree_in_varga=((p.sign_degree % span) / span) * 30.0,
                house_number=house
            )
        return VargaChart(varga_code="D27", varga_name="Saptavimshamsha", division=27,
                          lagna_sign_id=lagna_d27, lagna_sign_name=SIGN_NAMES[lagna_d27 - 1], planets=planets)

    @staticmethod
    def calculate_d30(chart: KundaliChart) -> VargaChart:
        """D30 (Trimshamsha - Afflictions, Evils, Karmic Debts). Unequal parts."""
        def get_d30_sign(sign_id: int, deg: float) -> int:
            is_odd = (sign_id % 2 != 0)
            if is_odd:
                if deg < 5.0: return 1   # Mars / Aries
                elif deg < 10.0: return 11 # Saturn / Aquarius
                elif deg < 18.0: return 9  # Jupiter / Sagittarius
                elif deg < 25.0: return 3  # Mercury / Gemini
                else: return 2             # Venus / Taurus
            else:
                if deg < 5.0: return 2   # Venus / Taurus
                elif deg < 12.0: return 6  # Mercury / Virgo
                elif deg < 20.0: return 12 # Jupiter / Pisces
                elif deg < 25.0: return 10 # Saturn / Capricorn
                else: return 8             # Mars / Scorpio

        lagna_d30 = get_d30_sign(chart.lagna_sign_id, chart.lagna_degree)
        planets: Dict[str, VargaPlanetPosition] = {}
        for name, p in chart.planets.items():
            s_id = get_d30_sign(p.sign_id, p.sign_degree)
            house = ((s_id - lagna_d30) % 12) + 1
            planets[name] = VargaPlanetPosition(
                name=name, sign_id=s_id, sign_name=SIGN_NAMES[s_id - 1],
                degree_in_varga=(p.sign_degree % 5.0) * 6.0,
                house_number=house
            )
        return VargaChart(varga_code="D30", varga_name="Trimshamsha", division=30,
                          lagna_sign_id=lagna_d30, lagna_sign_name=SIGN_NAMES[lagna_d30 - 1], planets=planets)

    @staticmethod
    def calculate_d60(chart: KundaliChart) -> VargaChart:
        """
        D60 (Shashtiamsha - All Matters, Supreme Karmic Blueprint). 60 parts of 0.5 deg.
        BPHS Ch. 6:
        - 60 parts of 30' (0.5°) each.
        - Deities:
            Odd signs: Counted directly from 0 (Ghora) to 59 (Chandrarekha).
            Even signs: Counted in reverse order from 59 (Chandrarekha) down to 0 (Ghora).
        """
        def get_d60_info(sign_id: int, deg: float) -> Tuple[int, str, bool]:
            part = min(59, int(deg // 0.5))  # 0 to 59
            target_sign = ((sign_id - 1 + part) % 12) + 1
            is_odd = (sign_id % 2 != 0)
            deity_idx = part if is_odd else (59 - part)
            deity_name = D60_DEITIES[deity_idx]
            is_benefic = deity_idx not in D60_MALEFIC_INDICES
            return target_sign, deity_name, is_benefic

        lagna_d60, lagna_deity, lagna_is_benefic = get_d60_info(chart.lagna_sign_id, chart.lagna_degree)
        planets: Dict[str, VargaPlanetPosition] = {}
        for name, p in chart.planets.items():
            s_id, d_name, is_ben = get_d60_info(p.sign_id, p.sign_degree)
            house = ((s_id - lagna_d60) % 12) + 1
            planets[name] = VargaPlanetPosition(
                name=name,
                sign_id=s_id,
                sign_name=SIGN_NAMES[s_id - 1],
                degree_in_varga=(p.sign_degree % 0.5) * 60.0,
                house_number=house,
                deity=d_name,
                is_benefic_deity=is_ben
            )
        return VargaChart(
            varga_code="D60",
            varga_name="Shashtiamsha",
            division=60,
            lagna_sign_id=lagna_d60,
            lagna_sign_name=SIGN_NAMES[lagna_d60 - 1],
            planets=planets,
            lagna_deity=lagna_deity,
            lagna_is_benefic_deity=lagna_is_benefic
        )

    @classmethod
    def get_d60_deity_details(cls, deity_name: str) -> Dict[str, str]:
        """Returns classical BPHS Ch. 6 deity description, nature, and phala."""
        clean_name = str(deity_name).strip()
        desc = D60_DEITY_DESCRIPTIONS.get(clean_name, {
            "nature": "विद्वत् सम्मत (Classical)",
            "phala": "पाराशरी षष्ट्यंश अधिष्ठाता प्रभाव।"
        })
        return {
            "name": clean_name,
            "nature": desc["nature"],
            "phala": desc["phala"],
            "grantha": "बृहत्पाराशर होराशास्त्रम् अ. ६ (BPHS Ch. 6)"
        }

    @staticmethod
    def calculate_d40(chart: KundaliChart) -> VargaChart:
        """D40 (Khavedamsha / Chatvarimshamsha - Auspicious / Inauspicious Results). 40 parts of 0.75 deg."""
        def get_d40_sign(sign_id: int, deg: float) -> int:
            part = int(deg // 0.75)  # 0 to 39
            is_odd = (sign_id % 2 != 0)
            start_sign = 1 if is_odd else 7  # Aries for odd, Libra for even
            return ((start_sign - 1 + part) % 12) + 1

        lagna_d40 = get_d40_sign(chart.lagna_sign_id, chart.lagna_degree)
        planets: Dict[str, VargaPlanetPosition] = {}
        for name, p in chart.planets.items():
            s_id = get_d40_sign(p.sign_id, p.sign_degree)
            house = ((s_id - lagna_d40) % 12) + 1
            planets[name] = VargaPlanetPosition(
                name=name, sign_id=s_id, sign_name=SIGN_NAMES[s_id - 1],
                degree_in_varga=((p.sign_degree % 0.75) / 0.75) * 30.0,
                house_number=house
            )
        return VargaChart(varga_code="D40", varga_name="Khavedamsha", division=40,
                          lagna_sign_id=lagna_d40, lagna_sign_name=SIGN_NAMES[lagna_d40 - 1], planets=planets)

    @staticmethod
    def calculate_d45(chart: KundaliChart) -> VargaChart:
        """D45 (Akshavedamsha - Character, Morals, General Fortunes). 45 parts of 2/3 deg = 0.666667 deg."""
        def get_d45_sign(sign_id: int, deg: float) -> int:
            span = 30.0 / 45.0  # 0.6666667 deg
            part = int(deg // span)  # 0 to 44
            m_type = (sign_id - 1) % 3  # 0: Movable, 1: Fixed, 2: Dual
            start_sign = 1 if m_type == 0 else (5 if m_type == 1 else 9)
            return ((start_sign - 1 + part) % 12) + 1

        lagna_d45 = get_d45_sign(chart.lagna_sign_id, chart.lagna_degree)
        planets: Dict[str, VargaPlanetPosition] = {}
        for name, p in chart.planets.items():
            s_id = get_d45_sign(p.sign_id, p.sign_degree)
            house = ((s_id - lagna_d45) % 12) + 1
            span = 30.0 / 45.0
            planets[name] = VargaPlanetPosition(
                name=name, sign_id=s_id, sign_name=SIGN_NAMES[s_id - 1],
                degree_in_varga=((p.sign_degree % span) / span) * 30.0,
                house_number=house
            )
        return VargaChart(varga_code="D45", varga_name="Akshavedamsha", division=45,
                          lagna_sign_id=lagna_d45, lagna_sign_name=SIGN_NAMES[lagna_d45 - 1], planets=planets)

    @staticmethod
    def calculate_d5(chart: KundaliChart) -> VargaChart:
        """D5 (Panchamsha - Fame, Power, Punya). 5 parts of 6.0 deg."""
        odd_map = [1, 11, 9, 3, 7]    # Aries, Aquarius, Sagittarius, Gemini, Libra
        even_map = [2, 6, 8, 10, 12]  # Taurus, Virgo, Scorpio, Capricorn, Pisces

        def get_d5_sign(sign_id: int, deg: float) -> int:
            part = min(4, int(deg // 6.0))
            is_odd = (sign_id % 2 != 0)
            return odd_map[part] if is_odd else even_map[part]

        lagna_d5 = get_d5_sign(chart.lagna_sign_id, chart.lagna_degree)
        planets: Dict[str, VargaPlanetPosition] = {}
        for name, p in chart.planets.items():
            s_id = get_d5_sign(p.sign_id, p.sign_degree)
            house = ((s_id - lagna_d5) % 12) + 1
            planets[name] = VargaPlanetPosition(
                name=name, sign_id=s_id, sign_name=SIGN_NAMES[s_id - 1],
                degree_in_varga=((p.sign_degree % 6.0) / 6.0) * 30.0,
                house_number=house
            )
        return VargaChart(varga_code="D5", varga_name="Panchamsha", division=5,
                          lagna_sign_id=lagna_d5, lagna_sign_name=SIGN_NAMES[lagna_d5 - 1], planets=planets)

    @staticmethod
    def calculate_d6(chart: KundaliChart) -> VargaChart:
        """D6 (Shashtamsha - Health, Obstacles, Debts). 6 parts of 5.0 deg."""
        def get_d6_sign(sign_id: int, deg: float) -> int:
            part = min(5, int(deg // 5.0))
            is_odd = (sign_id % 2 != 0)
            start_sign = 1 if is_odd else 7  # Aries for odd, Libra for even
            return ((start_sign - 1 + part) % 12) + 1

        lagna_d6 = get_d6_sign(chart.lagna_sign_id, chart.lagna_degree)
        planets: Dict[str, VargaPlanetPosition] = {}
        for name, p in chart.planets.items():
            s_id = get_d6_sign(p.sign_id, p.sign_degree)
            house = ((s_id - lagna_d6) % 12) + 1
            planets[name] = VargaPlanetPosition(
                name=name, sign_id=s_id, sign_name=SIGN_NAMES[s_id - 1],
                degree_in_varga=((p.sign_degree % 5.0) / 5.0) * 30.0,
                house_number=house
            )
        return VargaChart(varga_code="D6", varga_name="Shashtamsha", division=6,
                          lagna_sign_id=lagna_d6, lagna_sign_name=SIGN_NAMES[lagna_d6 - 1], planets=planets)

    @staticmethod
    def calculate_d8(chart: KundaliChart) -> VargaChart:
        """D8 (Ashtamsha - Longevity, Transformations, Hidden Realities). 8 parts of 3.75 deg."""
        def get_d8_sign(sign_id: int, deg: float) -> int:
            part = min(7, int(deg // 3.75))
            m_type = (sign_id - 1) % 3  # 0: Movable, 1: Fixed, 2: Dual
            start_sign = 1 if m_type == 0 else (9 if m_type == 1 else 5)
            return ((start_sign - 1 + part) % 12) + 1

        lagna_d8 = get_d8_sign(chart.lagna_sign_id, chart.lagna_degree)
        planets: Dict[str, VargaPlanetPosition] = {}
        for name, p in chart.planets.items():
            s_id = get_d8_sign(p.sign_id, p.sign_degree)
            house = ((s_id - lagna_d8) % 12) + 1
            planets[name] = VargaPlanetPosition(
                name=name, sign_id=s_id, sign_name=SIGN_NAMES[s_id - 1],
                degree_in_varga=((p.sign_degree % 3.75) / 3.75) * 30.0,
                house_number=house
            )
        return VargaChart(varga_code="D8", varga_name="Ashtamsha", division=8,
                          lagna_sign_id=lagna_d8, lagna_sign_name=SIGN_NAMES[lagna_d8 - 1], planets=planets)

    @staticmethod
    def calculate_d11(chart: KundaliChart) -> VargaChart:
        """D11 (Rudramsha / Ekadashamsha - Warfare, Destruction, Longevity). 11 parts of 30/11 deg."""
        span = 30.0 / 11.0
        def get_d11_sign(sign_id: int, deg: float) -> int:
            part = min(10, int(deg // span))
            start_sign = 13 - sign_id
            return ((start_sign - 1 - part) % 12) + 1

        lagna_d11 = get_d11_sign(chart.lagna_sign_id, chart.lagna_degree)
        planets: Dict[str, VargaPlanetPosition] = {}
        for name, p in chart.planets.items():
            s_id = get_d11_sign(p.sign_id, p.sign_degree)
            house = ((s_id - lagna_d11) % 12) + 1
            planets[name] = VargaPlanetPosition(
                name=name, sign_id=s_id, sign_name=SIGN_NAMES[s_id - 1],
                degree_in_varga=((p.sign_degree % span) / span) * 30.0,
                house_number=house
            )
        return VargaChart(varga_code="D11", varga_name="Rudramsha", division=11,
                          lagna_sign_id=lagna_d11, lagna_sign_name=SIGN_NAMES[lagna_d11 - 1], planets=planets)

    @staticmethod
    def calculate_d72(chart: KundaliChart) -> VargaChart:
        """D72 (Ashtottaramsha / Aparajita - Latent Spiritual Powers & Subtle Strengths). 6 parts of 5.0 deg."""
        def get_d72_sign(sign_id: int, deg: float) -> int:
            part = min(5, int(deg // 5.0))  # 0 to 5
            is_odd = (sign_id % 2 != 0)
            start_sign = 1 if is_odd else 7  # Aries for odd signs, Libra for even signs
            return ((start_sign - 1 + part) % 12) + 1

        lagna_d72 = get_d72_sign(chart.lagna_sign_id, chart.lagna_degree)
        planets: Dict[str, VargaPlanetPosition] = {}
        for name, p in chart.planets.items():
            s_id = get_d72_sign(p.sign_id, p.sign_degree)
            house = ((s_id - lagna_d72) % 12) + 1
            planets[name] = VargaPlanetPosition(
                name=name, sign_id=s_id, sign_name=SIGN_NAMES[s_id - 1],
                degree_in_varga=((p.sign_degree % 5.0) / 5.0) * 30.0,
                house_number=house
            )
        return VargaChart(varga_code="D72", varga_name="Ashtottaramsha", division=72,
                          lagna_sign_id=lagna_d72, lagna_sign_name=SIGN_NAMES[lagna_d72 - 1], planets=planets)

    @staticmethod
    def calculate_d81(chart: KundaliChart) -> VargaChart:
        """D81 (Navanavamsha - Navamsha of Navamsha - Esoteric Vitality & Inner Character). 81 parts."""
        def get_d81_sign(lon: float) -> int:
            # 1. Primary D9 Navamsha sign
            d9_part = int((lon % 360.0) // (360.0 / 108.0))  # 0 to 107
            d9_sign = (d9_part % 12) + 1

            # 2. Sub-Navamsha inside the D9 span (3°20' = 200 arcmin)
            d9_span = 360.0 / 108.0  # 3.333333°
            deg_in_d9 = lon % d9_span
            sub_span = d9_span / 9.0  # ~0.37037° = 22.222 arcmin
            sub_part = min(8, int(deg_in_d9 // sub_span))

            # Sub-navamsha start by element of D9 sign
            elem = (d9_sign - 1) % 4  # 0: Fire, 1: Earth, 2: Air, 3: Water
            start_sign = 1 if elem == 0 else (10 if elem == 1 else (7 if elem == 2 else 4))
            return ((start_sign - 1 + sub_part) % 12) + 1

        lagna_d81 = get_d81_sign(chart.lagna_longitude)
        planets: Dict[str, VargaPlanetPosition] = {}
        sub_span = (360.0 / 108.0) / 9.0
        for name, p in chart.planets.items():
            s_id = get_d81_sign(p.longitude)
            house = ((s_id - lagna_d81) % 12) + 1
            planets[name] = VargaPlanetPosition(
                name=name, sign_id=s_id, sign_name=SIGN_NAMES[s_id - 1],
                degree_in_varga=((p.longitude % sub_span) / sub_span) * 30.0,
                house_number=house
            )
        return VargaChart(varga_code="D81", varga_name="Navanavamsha", division=81,
                          lagna_sign_id=lagna_d81, lagna_sign_name=SIGN_NAMES[lagna_d81 - 1], planets=planets)

    @staticmethod
    def calculate_d108(chart: KundaliChart) -> VargaChart:
        """D108 (Ashtottarashatamsha - Nakshatra Pada Wheel & High Nadi Divination). 108 parts of 3°20'."""
        span = 360.0 / 108.0  # 3.333333° = 3°20'
        def get_d108_sign(lon: float) -> int:
            part = int((lon % 360.0) // span)  # 0 to 107
            return (part % 12) + 1  # 9 complete cycles of 12 zodiac signs

        lagna_d108 = get_d108_sign(chart.lagna_longitude)
        planets: Dict[str, VargaPlanetPosition] = {}
        for name, p in chart.planets.items():
            s_id = get_d108_sign(p.longitude)
            house = ((s_id - lagna_d108) % 12) + 1
            planets[name] = VargaPlanetPosition(
                name=name, sign_id=s_id, sign_name=SIGN_NAMES[s_id - 1],
                degree_in_varga=((p.longitude % span) / span) * 30.0,
                house_number=house
            )
        return VargaChart(varga_code="D108", varga_name="Ashtottarashatamsha", division=108,
                          lagna_sign_id=lagna_d108, lagna_sign_name=SIGN_NAMES[lagna_d108 - 1], planets=planets)

    @staticmethod
    def calculate_d144(chart: KundaliChart) -> VargaChart:
        """D144 (Dwadash-Dwadashamsha - Ancestral Heritage & Genetic Karmic Lineage). 144 parts of 12.5 arcmin."""
        d12_span = 30.0 / 12.0  # 2.5°
        sub_span = d12_span / 12.0  # 0.208333° = 12.5'

        def get_d144_sign(sign_id: int, deg: float) -> int:
            d12_part = min(11, int(deg // d12_span))
            d12_sign = ((sign_id - 1 + d12_part) % 12) + 1
            deg_in_d12 = deg % d12_span
            sub_part = min(11, int(deg_in_d12 // sub_span))
            return ((d12_sign - 1 + sub_part) % 12) + 1

        lagna_d144 = get_d144_sign(chart.lagna_sign_id, chart.lagna_degree)
        planets: Dict[str, VargaPlanetPosition] = {}
        for name, p in chart.planets.items():
            s_id = get_d144_sign(p.sign_id, p.sign_degree)
            house = ((s_id - lagna_d144) % 12) + 1
            planets[name] = VargaPlanetPosition(
                name=name, sign_id=s_id, sign_name=SIGN_NAMES[s_id - 1],
                degree_in_varga=((p.sign_degree % sub_span) / sub_span) * 30.0,
                house_number=house
            )
        return VargaChart(varga_code="D144", varga_name="Dwadash-Dwadashamsha", division=144,
                          lagna_sign_id=lagna_d144, lagna_sign_name=SIGN_NAMES[lagna_d144 - 1], planets=planets)

    @staticmethod
    def calculate_d150(chart: KundaliChart) -> VargaChart:
        """D150 (Nadiamsha - Chandra Kala Nadi / Deva Keralam 150 Micro-divisions of 12 arcmin = 0.2°)."""
        span = 30.0 / 150.0  # 0.2° = 12 arcmin

        def get_d150_info(sign_id: int, deg: float) -> Tuple[int, int, str]:
            part = min(149, int(deg // span))  # 0 to 149
            m_type = (sign_id - 1) % 3  # 0: Movable, 1: Fixed, 2: Dual
            if m_type == 0:
                nadi_num = part + 1
            elif m_type == 1:
                nadi_num = 150 - part
            else:
                nadi_num = (part + 76) if part < 75 else (part - 74)

            target_sign = ((sign_id - 1 + part) % 12) + 1
            half = "Poorvardha (पूर्वार्ध: 0-6')" if (deg % span) < (span / 2.0) else "Uttarardha (उत्तरार्ध: 6-12')"
            return target_sign, nadi_num, half

        lagna_d150, l_nadi, l_half = get_d150_info(chart.lagna_sign_id, chart.lagna_degree)
        planets: Dict[str, VargaPlanetPosition] = {}
        for name, p in chart.planets.items():
            s_id, p_nadi, p_half = get_d150_info(p.sign_id, p.sign_degree)
            house = ((s_id - lagna_d150) % 12) + 1
            planets[name] = VargaPlanetPosition(
                name=name, sign_id=s_id, sign_name=SIGN_NAMES[s_id - 1],
                degree_in_varga=((p.sign_degree % span) / span) * 30.0,
                house_number=house,
                deity=f"Nadi #{p_nadi} ({p_half})"
            )
        return VargaChart(varga_code="D150", varga_name="Nadiamsha", division=150,
                          lagna_sign_id=lagna_d150, lagna_sign_name=SIGN_NAMES[lagna_d150 - 1],
                          planets=planets, lagna_deity=f"Nadi #{l_nadi} ({l_half})")

    @classmethod
    def get_vargottama_planets(cls, chart: KundaliChart) -> List[str]:
        """
        Identify planets that occupy the exact same zodiac sign in D1 (Rashi) and D9 (Navamsha).
        Includes 'Lagna' if the ascendant is vargottama.
        """
        vargas = chart.vargas or cls.calculate_all_vargas(chart)
        d1 = vargas.get("D1", cls.calculate_d1(chart))
        d9 = vargas.get("D9", cls.calculate_d9(chart))

        vargottama_list: List[str] = []
        if d1.lagna_sign_id == d9.lagna_sign_id:
            vargottama_list.append("Lagna")

        for p_name, d1_pos in d1.planets.items():
            d9_pos = d9.planets.get(p_name)
            if d9_pos and d1_pos.sign_id == d9_pos.sign_id:
                vargottama_list.append(p_name)

        return vargottama_list

    @classmethod
    def get_bhavottama_planets(cls, chart: KundaliChart) -> List[str]:
        """
        Identify planets that occupy the same house number in D1 (Rashi) and D9 (Navamsha).
        """
        vargas = chart.vargas or cls.calculate_all_vargas(chart)
        d1 = vargas.get("D1", cls.calculate_d1(chart))
        d9 = vargas.get("D9", cls.calculate_d9(chart))

        bhavottama_list: List[str] = []
        for p_name, d1_pos in d1.planets.items():
            d9_pos = d9.planets.get(p_name)
            if d9_pos and d1_pos.house_number == d9_pos.house_number:
                bhavottama_list.append(p_name)

        return bhavottama_list

    @classmethod
    def _evaluate_planet_dignity(cls, planet_name: str, sign_id: int) -> float:
        """
        Calculate BPHS dignity score (0 to 20) for a planet in a given sign.
        """
        sign_name = SIGN_NAMES[sign_id - 1]

        # 1. Exaltation
        if planet_name in EXALTATION and EXALTATION[planet_name][0] == sign_name:
            return 20.0

        # 2. Debilitation
        if planet_name in DEBILITATION and DEBILITATION[planet_name][0] == sign_name:
            return 0.0

        # 3. Moolatrikona
        if planet_name in MOOLATRIKONA and MOOLATRIKONA[planet_name][0] == sign_name:
            return 18.0

        # 4. Own Sign
        if planet_name in OWN_SIGNS and sign_name in OWN_SIGNS[planet_name]:
            return 15.0

        # 5. Planetary Relationship via Sign Lord
        lord = SIGN_LORDS.get(sign_id)
        if not lord or lord == planet_name:
            return 15.0

        friends = NATURAL_FRIENDS.get(planet_name, [])
        enemies = NATURAL_ENEMIES.get(planet_name, [])

        if lord in friends:
            return 10.0
        elif lord in enemies:
            return 4.0
        else:
            return 7.0

    @classmethod
    def calculate_vimsopaka_bala(cls, chart: KundaliChart, scheme: str = "shadvarga") -> Dict[str, float]:
        """
        Vimsopaka Bala: 20-point divisional strength evaluation according to BPHS Ch. 45.
        Supported schemes: 'shadvarga', 'saptavarga', 'dashavarga', 'shodashavarga'.
        """
        schemes = {
            "shadvarga": {"D1": 6.0, "D2": 2.0, "D3": 4.0, "D9": 5.0, "D12": 2.0, "D30": 1.0},
            "saptavarga": {"D1": 5.0, "D2": 2.0, "D3": 3.0, "D7": 2.5, "D9": 4.5, "D12": 2.0, "D30": 1.0},
            "dashavarga": {"D1": 3.0, "D2": 1.5, "D3": 1.5, "D7": 1.5, "D9": 1.5, "D10": 1.5, "D12": 1.5, "D16": 1.5, "D30": 1.5, "D60": 5.0},
            "shodashavarga": {
                "D1": 3.5, "D2": 1.0, "D3": 1.0, "D4": 0.5, "D7": 0.5, "D9": 3.0, "D10": 0.5, "D12": 0.5,
                "D16": 2.0, "D20": 0.5, "D24": 0.5, "D27": 0.5, "D30": 1.0, "D40": 0.5, "D45": 0.5, "D60": 4.0
            }
        }
        weights = schemes.get(scheme, schemes["shadvarga"])
        all_v = cls.calculate_all_vargas(chart)
        scores: Dict[str, float] = {}

        planets_to_score = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
        total_weight = sum(weights.values())

        for p_name in planets_to_score:
            weighted_points = 0.0
            for v_code, wt in weights.items():
                v_chart = all_v.get(v_code)
                if v_chart:
                    v_planet = v_chart.planets.get(p_name)
                    if v_planet:
                        dignity = cls._evaluate_planet_dignity(p_name, v_planet.sign_id)
                        weighted_points += (dignity / 20.0) * wt
            score_out_of_20 = (weighted_points / total_weight) * 20.0 if total_weight > 0 else 0.0
            scores[p_name] = round(score_out_of_20, 2)

        return scores

    @classmethod
    def calculate_all_vargas(cls, chart: KundaliChart, variations: Optional[Dict[str, str]] = None) -> Dict[str, VargaChart]:
        """Compute all 16 divisional charts with optional classical sampradaya variations."""
        v_map = variations or {}
        d2_var = v_map.get("D2", "parashari")
        d3_var = v_map.get("D3", "parashari")
        d9_var = v_map.get("D9", "parashari")

        return {
            "D1": cls.calculate_d1(chart),
            "D2": cls.calculate_d2(chart, variation=d2_var),
            "D3": cls.calculate_d3(chart, variation=d3_var),
            "D4": cls.calculate_d4(chart),
            "D5": cls.calculate_d5(chart),
            "D6": cls.calculate_d6(chart),
            "D7": cls.calculate_d7(chart),
            "D8": cls.calculate_d8(chart),
            "D9": cls.calculate_d9(chart, variation=d9_var),
            "D10": cls.calculate_d10(chart),
            "D11": cls.calculate_d11(chart),
            "D12": cls.calculate_d12(chart),
            "D16": cls.calculate_d16(chart),
            "D20": cls.calculate_d20(chart),
            "D24": cls.calculate_d24(chart),
            "D27": cls.calculate_d27(chart),
            "D30": cls.calculate_d30(chart),
            "D40": cls.calculate_d40(chart),
            "D45": cls.calculate_d45(chart),
            "D60": cls.calculate_d60(chart),
            "D72": cls.calculate_d72(chart),
            "D81": cls.calculate_d81(chart),
            "D108": cls.calculate_d108(chart),
            "D144": cls.calculate_d144(chart),
            "D150": cls.calculate_d150(chart),
        }

    @classmethod
    def calculate_all_shodashavarga(
        cls,
        chart: KundaliChart,
        variations: Optional[Dict[str, str]] = None
    ) -> Dict[str, VargaChart]:
        """
        Compute the canonical 16 Shodashavarga divisional charts (BPHS Ch. 6).
        Canonical 16: D1, D2, D3, D4, D7, D9, D10, D12, D16, D20, D24, D27, D30, D40, D45, D60.
        """
        all_v = cls.calculate_all_vargas(chart, variations=variations)
        return {code: all_v[code] for code in SHODASHAVARGA_CODES if code in all_v}

    @classmethod
    def calculate_vaisheshikamsa(
        cls,
        chart: KundaliChart,
        include_friends: bool = False
    ) -> Dict[str, Dict[str, Any]]:
        """
        Evaluate Vaisheshikamsa dignity tally across the classical 16 Shodashavargas (BPHS Ch. 6).
        Tally counts how many vargas a planet occupies in its Exaltation, Moolatrikona, or Own sign.
        Designations:
          2: Parijata
          3: Uttama
          4: Gopura
          5: Simhasana
          6: Paravata
          7: Devaloka
          8: Kumkumamsha
          9: Airavata
          10: Vaisheshikamsa
          11: Goloka
          12: Vaikuntha
          13: Sarvathasiddha
          14: Kalpavriksha
          15: Brahmaloka
          16: Shridham
        """
        shodasha_vargas = cls.calculate_all_shodashavarga(chart)
        planets_to_eval = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
        results: Dict[str, Dict[str, Any]] = {}

        for p_name in planets_to_eval:
            dignified_vargas: List[str] = []
            for v_code in SHODASHAVARGA_CODES:
                v_chart = shodasha_vargas.get(v_code)
                if not v_chart:
                    continue
                v_planet = v_chart.planets.get(p_name)
                if not v_planet:
                    continue

                sign_name = v_planet.sign_name
                is_exalted = p_name in EXALTATION and EXALTATION[p_name][0] == sign_name
                is_mt = p_name in MOOLATRIKONA and MOOLATRIKONA[p_name][0] == sign_name
                is_own = p_name in OWN_SIGNS and sign_name in OWN_SIGNS[p_name]
                is_friend = False
                if include_friends:
                    lord = SIGN_LORDS.get(v_planet.sign_id)
                    is_friend = lord in NATURAL_FRIENDS.get(p_name, [])

                if is_exalted or is_mt or is_own or is_friend:
                    dignified_vargas.append(v_code)

            count = len(dignified_vargas)
            designation = VAISHESHIKAMSA_BENCHMARKS.get(count)
            if designation is None:
                if count >= 16:
                    designation = "Shridham"
                elif count == 1:
                    designation = "Sadharana (1 Varga)"
                else:
                    designation = "Sadharana"

            results[p_name] = {
                "count": count,
                "designation": designation,
                "vargas": dignified_vargas
            }

        return results


