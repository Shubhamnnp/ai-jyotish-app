"""
Astrological Chart Calculator for JyotishOS.
Converts astronomical coordinates into Vedic astrological entities:
Signs, Nakshatras, Padas, Houses, Dignities, Panchang, and Atmakaraka.
"""

import math
from datetime import datetime, date, time, timedelta
from typing import Dict, List, Tuple, Optional

from .constants import (
    SIGNS, SIGN_NAMES, SIGN_LORDS, NAKSHATRAS, GRAHAS,
    EXALTATION, DEBILITATION, MOOLATRIKONA, OWN_SIGNS,
    NATURAL_FRIENDS, NATURAL_ENEMIES, SPECIAL_ASPECTS
)
from .models import (
    BirthData, PlanetPosition, HouseCusp, PanchangData,
    KundaliChart
)
from .ephemeris import PyEphemProvider, default_ephemeris_provider


# 27 Yogas (Sun + Moon longitude / 13.333333 deg)
YOGAS = [
    "Vishkambha", "Priti", "Ayushman", "Saubhagya", "Shobhana", "Atiganda",
    "Sukarma", "Dhriti", "Shula", "Ganda", "Vriddhi", "Dhruva", "Vyaghata",
    "Harshana", "Vajra", "Siddhi", "Vyatipata", "Variyan", "Parigha", "Shiva",
    "Siddha", "Sadhya", "Shubha", "Shukla", "Brahma", "Indra", "Vaidhriti"
]

# 11 Karanas
KARANAS = [
    "Bava", "Balava", "Kaulava", "Taitila", "Gara", "Vanija", "Vishti (Bhadra)",
    "Shakuni", "Chatushpada", "Naga", "Kintughna"
]

VARAS = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
VARA_LORDS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]


class ChartCalculator:
    """Core calculation engine for Vedic Kundali Charts."""

    def __init__(self, ephem_provider: Optional[PyEphemProvider] = None):
        self.provider = ephem_provider or default_ephemeris_provider

    def longitude_to_sign(self, lon: float) -> Tuple[int, str, float]:
        """Returns (sign_id 1-12, sign_name, degree_within_sign 0-30)."""
        norm_lon = lon % 360.0
        sign_idx = int(norm_lon // 30.0)
        sign_deg = norm_lon % 30.0
        sign_id = sign_idx + 1
        sign_name = SIGN_NAMES[sign_idx]
        return sign_id, sign_name, sign_deg

    def longitude_to_nakshatra(self, lon: float) -> Tuple[int, str, int, str]:
        """Returns (nakshatra_id 1-27, nakshatra_name, pada 1-4, nakshatra_lord)."""
        norm_lon = lon % 360.0
        span = 360.0 / 27.0  # 13.3333333 degrees
        nak_idx = int(norm_lon // span) % 27
        rem_deg = norm_lon % span
        pada_span = span / 4.0  # 3.3333333 degrees
        pada = int(rem_deg // pada_span) + 1
        nak = NAKSHATRAS[nak_idx]
        return nak["id"], nak["name"], pada, nak["lord"]

    def determine_dignity(self, planet_name: str, sign_name: str, sign_deg: float) -> str:
        """Determines classical Parashari planetary dignity."""
        if planet_name in ("Rahu", "Ketu"):
            if sign_name in EXALTATION.get(planet_name, ("", 0))[0]:
                return "exalted"
            if sign_name in DEBILITATION.get(planet_name, ("", 0))[0]:
                return "debilitated"
            if sign_name in OWN_SIGNS.get(planet_name, []):
                return "own"
            return "neutral"

        # 1. Exaltation Check
        exalt_info = EXALTATION.get(planet_name)
        if exalt_info and sign_name == exalt_info[0]:
            return "exalted"

        # 2. Debilitation Check
        debil_info = DEBILITATION.get(planet_name)
        if debil_info and sign_name == debil_info[0]:
            return "debilitated"

        # 3. Moolatrikona Check
        moola_info = MOOLATRIKONA.get(planet_name)
        if moola_info and sign_name == moola_info[0]:
            start_deg, end_deg = moola_info[1], moola_info[2]
            if start_deg <= sign_deg <= end_deg:
                return "moolatrikona"

        # 4. Own Sign Check
        own_list = OWN_SIGNS.get(planet_name, [])
        if sign_name in own_list:
            return "own"

        # 5. Natural Friend / Enemy Check (Sign Lord relationship)
        sign_lord = SIGN_LORDS.get(sign_name)
        if sign_lord:
            friends = NATURAL_FRIENDS.get(planet_name, [])
            enemies = NATURAL_ENEMIES.get(planet_name, [])
            if sign_lord in friends:
                return "friend"
            elif sign_lord in enemies:
                return "enemy"

        return "neutral"

    def check_combustion(self, planet_name: str, planet_lon: float, sun_lon: float, is_retro: bool) -> bool:
        """Determines if a planet is combust (Asta) by closeness to the Sun."""
        if planet_name in ("Sun", "Rahu", "Ketu"):
            return False

        diff = abs(planet_lon - sun_lon)
        if diff > 180.0:
            diff = 360.0 - diff

        limits = {
            "Moon": 12.0,
            "Mars": 17.0,
            "Mercury": 12.0 if is_retro else 14.0,
            "Jupiter": 11.0,
            "Venus": 8.0 if is_retro else 10.0,
            "Saturn": 15.0,
        }
        return diff <= limits.get(planet_name, 10.0)

    def calculate_panchang(self, dt_utc: datetime, sun_lon: float, moon_lon: float) -> PanchangData:
        """Calculates Tithi, Vara, Nakshatra, Yoga, and Karana."""
        # 1. Tithi: (Moon - Sun) / 12 degrees
        diff = (moon_lon - sun_lon) % 360.0
        tithi_num = int(diff // 12.0) + 1  # 1 to 30

        tithi_names = [
            "Pratipada", "Dwitiya", "Tritiya", "Chaturthi", "Panchami",
            "Shashthi", "Saptami", "Ashtami", "Navami", "Dashami",
            "Ekadashi", "Dwadashi", "Trayodashi", "Chaturdashi", "Purnima",
            "Pratipada", "Dwitiya", "Tritiya", "Chaturthi", "Panchami",
            "Shashthi", "Saptami", "Ashtami", "Navami", "Dashami",
            "Ekadashi", "Dwadashi", "Trayodashi", "Chaturdashi", "Amavasya"
        ]
        tithi_type = "Shukla Paksha" if tithi_num <= 15 else "Krishna Paksha"
        tithi_name = f"{tithi_type} {tithi_names[tithi_num - 1]}"

        # 2. Vara (Weekday)
        weekday_idx = dt_utc.weekday()  # Monday=0, Sunday=6
        # Convert to Sunday=0
        vara_idx = (weekday_idx + 1) % 7
        vara_name = VARAS[vara_idx]

        # 3. Nakshatra of Moon
        _, nak_name, _, _ = self.longitude_to_nakshatra(moon_lon)

        # 4. Yoga: (Sun + Moon) / 13.333333 degrees
        sum_lon = (sun_lon + moon_lon) % 360.0
        yoga_idx = int(sum_lon // (360.0 / 27.0)) % 27
        yoga_name = YOGAS[yoga_idx]

        # 5. Karana: Half of a Tithi = 6 degrees
        karana_idx = int(diff // 6.0)  # 0 to 59
        if karana_idx == 0:
            karana_name = "Kintughna"
        elif karana_idx >= 57:
            fixed = ["Shakuni", "Chatushpada", "Naga"]
            karana_name = fixed[karana_idx - 57]
        else:
            repeating = ["Bava", "Balava", "Kaulava", "Taitila", "Gara", "Vanija", "Vishti (Bhadra)"]
            karana_name = repeating[(karana_idx - 1) % 7]

        return PanchangData(
            tithi_name=tithi_name,
            tithi_number=tithi_num,
            tithi_type=tithi_type,
            vara_name=vara_name,
            nakshatra_name=nak_name,
            yoga_name=yoga_name,
            karana_name=karana_name,
        )

    def calculate_houses(
        self,
        lagna_lon: float,
        house_system: str = "Whole Sign"
    ) -> List[HouseCusp]:
        """Calculates 12 bhava cusps and sign rulers."""
        houses: List[HouseCusp] = []
        lagna_sign_id, _, _ = self.longitude_to_sign(lagna_lon)

        for h in range(1, 13):
            if house_system.lower() == "whole sign":
                # Whole sign: House 1 = Lagna sign, House 2 = Next sign, etc.
                sign_id = ((lagna_sign_id - 1 + (h - 1)) % 12) + 1
                sign_name = SIGN_NAMES[sign_id - 1]
                cusp_lon = (sign_id - 1) * 30.0 + 15.0  # Midpoint of sign
            else:
                # Equal house: Cusp starts from exact Lagna degree
                cusp_lon = (lagna_lon + (h - 1) * 30.0) % 360.0
                sign_id, sign_name, _ = self.longitude_to_sign(cusp_lon)

            lord = SIGN_LORDS[sign_name]
            houses.append(HouseCusp(
                house_number=h,
                sign_id=sign_id,
                sign_name=sign_name,
                cusp_longitude=cusp_lon,
                lord=lord,
                occupants=[],
                aspecting_planets=[]
            ))
        return houses

    def calculate_chart(
        self,
        birth_data: BirthData,
        ayanamsa_name: str = "Lahiri",
        house_system: str = "Whole Sign"
    ) -> KundaliChart:
        """Full Natal Kundali Calculation Pipeline."""
        # 1. Convert local birth time to UTC
        birth_dt = datetime.combine(birth_data.birth_date, birth_data.birth_time)
        dt_utc = birth_dt - timedelta(hours=birth_data.timezone_offset)

        # 2. Compute Planetary Positions & Ayanamsa
        raw_positions, ayanamsa_val = self.provider.get_planet_positions(dt_utc, ayanamsa_name)

        # 3. Compute Lagna
        lagna_lon = self.provider.calculate_ascendant(
            dt_utc, birth_data.latitude, birth_data.longitude, ayanamsa_val
        )
        lagna_sign_id, lagna_sign_name, lagna_deg = self.longitude_to_sign(lagna_lon)

        # 4. Generate Houses
        houses = self.calculate_houses(lagna_lon, house_system)
        sun_lon = raw_positions["Sun"]["longitude"]
        moon_lon = raw_positions["Moon"]["longitude"]
        moon_sign_id, _, _ = self.longitude_to_sign(moon_lon)

        # 5. Build PlanetPosition objects
        planets: Dict[str, PlanetPosition] = {}
        for name in GRAHAS:
            pos = raw_positions[name]
            lon = pos["longitude"]
            sign_id, sign_name, sign_deg = self.longitude_to_sign(lon)
            nak_id, nak_name, nak_pada, nak_lord = self.longitude_to_nakshatra(lon)

            # House from Lagna (Whole sign: offset from lagna sign)
            house_lagna = ((sign_id - lagna_sign_id) % 12) + 1
            # House from Moon
            house_moon = ((sign_id - moon_sign_id) % 12) + 1

            dignity = self.determine_dignity(name, sign_name, sign_deg)
            is_combust = self.check_combustion(name, lon, sun_lon, pos["is_retrograde"])

            planet_obj = PlanetPosition(
                name=name,
                longitude=lon,
                latitude=pos.get("latitude", 0.0),
                speed=pos.get("speed", 0.0),
                is_retrograde=pos.get("is_retrograde", False),
                is_combust=is_combust,
                sign_id=sign_id,
                sign_name=sign_name,
                sign_degree=sign_deg,
                nakshatra_id=nak_id,
                nakshatra_name=nak_name,
                nakshatra_pada=nak_pada,
                nakshatra_lord=nak_lord,
                house_from_lagna=house_lagna,
                house_from_moon=house_moon,
                dignity=dignity,
            )
            planets[name] = planet_obj

            # Register occupant in house
            if 1 <= house_lagna <= 12:
                houses[house_lagna - 1].occupants.append(name)

        # 6. Calculate aspects on houses
        for p_name, p_pos in planets.items():
            aspect_steps = SPECIAL_ASPECTS.get(p_name, [7])
            for step in aspect_steps:
                target_house = ((p_pos.house_from_lagna - 1 + (step - 1)) % 12) + 1
                houses[target_house - 1].aspecting_planets.append(p_name)

        # 7. Calculate Atmakaraka (Jaimini 7 Karaka system)
        # 7 planets (Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn) ordered by sign degree
        seven_planets = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
        sorted_by_deg = sorted(
            seven_planets,
            key=lambda p: planets[p].sign_degree,
            reverse=True
        )
        atmakaraka = sorted_by_deg[0] if sorted_by_deg else None

        # 8. Calculate Panchang
        panchang = self.calculate_panchang(dt_utc, sun_lon, moon_lon)

        return KundaliChart(
            birth_data=birth_data,
            ayanamsa_name=ayanamsa_name,
            ayanamsa_value=ayanamsa_val,
            lagna_longitude=lagna_lon,
            lagna_sign_id=lagna_sign_id,
            lagna_sign_name=lagna_sign_name,
            lagna_degree=lagna_deg,
            planets=planets,
            houses=houses,
            panchang=panchang,
            atmakaraka=atmakaraka,
        )

    def calculate_full_chart(
        self,
        birth_data: BirthData,
        ayanamsa_name: str = "Lahiri",
        house_system: str = "Whole Sign"
    ) -> KundaliChart:
        """Calculates complete chart including Vargas, Ashtakavarga with Shodhana, Shadbala, Jaimini, and Upagrahas."""
        from .varga import VargaCalculator
        from .ashtakavarga import AshtakavargaCalculator
        from .shadbala import default_shadbala_calculator
        from .jaimini import default_jaimini_calculator
        from .upagraha import default_upagraha_calculator

        chart = self.calculate_chart(birth_data, ayanamsa_name, house_system)
        chart.vargas = VargaCalculator.calculate_all_vargas(chart)
        chart.ashtakavarga = AshtakavargaCalculator.calculate(chart)
        chart.shadbala = default_shadbala_calculator.calculate(chart)
        chart.jaimini = default_jaimini_calculator.calculate(chart)
        chart.upagrahas = default_upagraha_calculator.calculate(chart)
        return chart


# Singleton calculator instance
default_chart_calculator = ChartCalculator()


