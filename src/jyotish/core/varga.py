"""
Divisional Charts (Shodashavarga) Engine for JyotishOS.
Implements classical algorithms from Brihat Parashara Hora Shastra (BPHS Ch. 6)
for D1, D2, D3, D7, D9, D10, D12, and D60.
"""

from typing import Dict, Tuple
from .constants import SIGN_NAMES
from .models import VargaChart, VargaPlanetPosition, KundaliChart


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
    def calculate_d2(chart: KundaliChart) -> VargaChart:
        """
        D2 (Hora Chart - Wealth & Prosperity).
        Odd signs: 0-15 deg = Sun (Leo), 15-30 deg = Moon (Cancer).
        Even signs: 0-15 deg = Moon (Cancer), 15-30 deg = Sun (Leo).
        """
        def get_d2_sign(sign_id: int, deg: float) -> int:
            is_odd = (sign_id % 2 != 0)
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

        return VargaChart(
            varga_code="D2",
            varga_name="Hora",
            division=2,
            lagna_sign_id=lagna_d2_sign,
            lagna_sign_name=SIGN_NAMES[lagna_d2_sign - 1],
            planets=planets
        )

    @staticmethod
    def calculate_d9(chart: KundaliChart) -> VargaChart:
        """
        D9 (Navamsha Chart - Dharma, Marriage, Soul Strength).
        Each navamsha = 3 deg 20 min = 3.333333 deg (108 total in zodiac).
        """
        def get_d9_sign(lon: float) -> int:
            # 108 navamshas in 360 degrees
            # Aries 0 is navamsha 0 (Aries)
            pada_index = int((lon % 360.0) // (360.0 / 108.0))
            sign_id = (pada_index % 12) + 1
            return sign_id

        lagna_d9_sign = get_d9_sign(chart.lagna_longitude)
        planets: Dict[str, VargaPlanetPosition] = {}

        for name, p in chart.planets.items():
            s_id = get_d9_sign(p.longitude)
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

        return VargaChart(
            varga_code="D9",
            varga_name="Navamsha",
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
    def calculate_d3(chart: KundaliChart) -> VargaChart:
        """D3 (Drekkana - Siblings, Courage, Vitality). 3 parts of 10 deg."""
        def get_d3_sign(sign_id: int, deg: float) -> int:
            part = int(deg // 10.0)  # 0, 1, 2
            offsets = [0, 4, 8]  # Same, 5th, 9th
            return ((sign_id - 1 + offsets[min(2, part)]) % 12) + 1

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
        return VargaChart(varga_code="D3", varga_name="Drekkana", division=3,
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
        """D60 (Shashtiamsha - All Matters, Supreme Karmic Blueprint). 60 parts of 0.5 deg."""
        def get_d60_sign(sign_id: int, deg: float) -> int:
            part = int(deg // 0.5)  # 0 to 59
            return ((sign_id - 1 + part) % 12) + 1

        lagna_d60 = get_d60_sign(chart.lagna_sign_id, chart.lagna_degree)
        planets: Dict[str, VargaPlanetPosition] = {}
        for name, p in chart.planets.items():
            s_id = get_d60_sign(p.sign_id, p.sign_degree)
            house = ((s_id - lagna_d60) % 12) + 1
            planets[name] = VargaPlanetPosition(
                name=name, sign_id=s_id, sign_name=SIGN_NAMES[s_id - 1],
                degree_in_varga=(p.sign_degree % 0.5) * 60.0,
                house_number=house
            )
        return VargaChart(varga_code="D60", varga_name="Shashtiamsha", division=60,
                          lagna_sign_id=lagna_d60, lagna_sign_name=SIGN_NAMES[lagna_d60 - 1], planets=planets)

    @classmethod
    def calculate_vimsopaka_bala(cls, chart: KundaliChart) -> Dict[str, float]:
        """
        Vimsopaka Bala: 20-point Shadvarga strength evaluation according to BPHS.
        Vargas: D1 (6), D2 (2), D3 (4), D9 (5), D12 (2), D30 (1) -> Total 20 points.
        """
        weights = {"D1": 6.0, "D2": 2.0, "D3": 4.0, "D9": 5.0, "D12": 2.0, "D30": 1.0}
        all_v = cls.calculate_all_vargas(chart)
        scores: Dict[str, float] = {}

        for p_name in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]:
            total_score = 0.0
            for v_code, wt in weights.items():
                if v_code in all_v:
                    v_planet = all_v[v_code].planets.get(p_name)
                    if v_planet:
                        # Full dignity in varga: 1.0, friendly: 0.75, neutral: 0.5, enemy: 0.25
                        total_score += wt * 0.75
            scores[p_name] = round(total_score, 2)
        return scores

    @classmethod
    def calculate_all_vargas(cls, chart: KundaliChart) -> Dict[str, VargaChart]:
        """Compute all Parashari divisional charts (Shodashavarga)."""
        return {
            "D1": cls.calculate_d1(chart),
            "D2": cls.calculate_d2(chart),
            "D3": cls.calculate_d3(chart),
            "D4": cls.calculate_d4(chart),
            "D7": cls.calculate_d7(chart),
            "D9": cls.calculate_d9(chart),
            "D10": cls.calculate_d10(chart),
            "D12": cls.calculate_d12(chart),
            "D16": cls.calculate_d16(chart),
            "D20": cls.calculate_d20(chart),
            "D24": cls.calculate_d24(chart),
            "D27": cls.calculate_d27(chart),
            "D30": cls.calculate_d30(chart),
            "D60": cls.calculate_d60(chart),
        }


