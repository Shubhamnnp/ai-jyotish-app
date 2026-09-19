"""
Native Dasvarga Dignity, Affliction & Free Will Analysis Engine for JyotishOS.

Implements the complete classical evaluation of:
- Dasvarga Table (dignities across D1 to D60 matching Grahalakshanam's layout)
- 12 Houses Free Will & Affliction Points (Count and Detailed Planet Name views)
- 9 Planets Free Will & Dashvarga Strength
- 26 Classical Life Area 3-Pillar Breakdown
- Rashi Tatva & Astrological Quality Classification
"""

from typing import Dict, Any, List, Tuple, Optional
from .models import KundaliChart, PlanetPosition
from .constants import SIGN_NAMES, SIGN_LORDS, EXALTATION, DEBILITATION, MOOLATRIKONA, OWN_SIGNS, NATURAL_FRIENDS, NATURAL_ENEMIES
from .varga import VargaCalculator

PLANET_SYMBOLS = {
    "Sun": "Su", "Moon": "Mo", "Mars": "Ma", "Mercury": "Me",
    "Jupiter": "Ju", "Venus": "Ve", "Saturn": "Sa", "Rahu": "Ra", "Ketu": "Ke"
}

SYMBOL_TO_NAME = {v: k for k, v in PLANET_SYMBOLS.items()}

SIGN_QUALITIES = {
    "Aries": ("Movable", "Fire", "Kshatriya", "Dharm", "Male", "Hind Rising", "Night", "Shrishti"),
    "Taurus": ("Fixed", "Earth", "Vaishya", "Artha", "Female", "Hind Rising", "Night", "Sthiti"),
    "Gemini": ("Dual", "Air", "Shudra", "Kama", "Male", "Head Rising", "Night", "Samhar"),
    "Cancer": ("Movable", "Water", "Brahman", "Moksh", "Female", "Hind Rising", "Night", "Sthiti"),
    "Leo": ("Fixed", "Fire", "Kshatriya", "Dharm", "Male", "Head Rising", "Day", "Shrishti"),
    "Virgo": ("Dual", "Earth", "Vaishya", "Artha", "Female", "Head Rising", "Day", "Sthiti"),
    "Libra": ("Movable", "Air", "Shudra", "Kama", "Male", "Head Rising", "Day", "Samhar"),
    "Scorpio": ("Fixed", "Water", "Brahman", "Moksh", "Female", "Head Rising", "Day", "Sthiti"),
    "Sagittarius": ("Dual", "Fire", "Kshatriya", "Dharm", "Male", "Hind Rising", "Night", "Shrishti"),
    "Capricorn": ("Movable", "Earth", "Vaishya", "Artha", "Female", "Hind Rising", "Night", "Sthiti"),
    "Aquarius": ("Fixed", "Air", "Shudra", "Kama", "Male", "Head Rising", "Day", "Samhar"),
    "Pisces": ("Dual", "Water", "Brahman", "Moksh", "Female", "Ubhayodaya", "Day", "Sthiti")
}

LIFE_AREAS = [
    {"Id": 1, "LifeArea": "Career", "house": 10, "karaka": "Saturn", "sec_house": 2},
    {"Id": 2, "LifeArea": "Health", "house": 1, "karaka": "Sun", "sec_house": 8},
    {"Id": 3, "LifeArea": "Relationship", "house": 7, "karaka": "Venus", "sec_house": 3},
    {"Id": 4, "LifeArea": "Accumulated Wealth (Ju)", "house": 2, "karaka": "Jupiter", "sec_house": 11},
    {"Id": 5, "LifeArea": "Bank Balance (Ve)", "house": 2, "karaka": "Venus", "sec_house": 11},
    {"Id": 6, "LifeArea": "Peace of Mind", "house": 4, "karaka": "Moon", "sec_house": 5},
    {"Id": 7, "LifeArea": "Mother", "house": 4, "karaka": "Moon", "sec_house": 4},
    {"Id": 8, "LifeArea": "Immovable property", "house": 4, "karaka": "Mars", "sec_house": 4},
    {"Id": 9, "LifeArea": "Education", "house": 5, "karaka": "Jupiter", "sec_house": 4},
    {"Id": 10, "LifeArea": "Happiness", "house": 4, "karaka": "Venus", "sec_house": 9},
    {"Id": 11, "LifeArea": "Luxury", "house": 4, "karaka": "Venus", "sec_house": 12},
    {"Id": 12, "LifeArea": "Heart", "house": 4, "karaka": "Sun", "sec_house": 5},
    {"Id": 13, "LifeArea": "Intelligence", "house": 5, "karaka": "Mercury", "sec_house": 1},
    {"Id": 14, "LifeArea": "Children", "house": 5, "karaka": "Jupiter", "sec_house": 9},
    {"Id": 15, "LifeArea": "Litigation", "house": 6, "karaka": "Mars", "sec_house": 8},
    {"Id": 16, "LifeArea": "Husband (Ju)", "house": 7, "karaka": "Jupiter", "sec_house": 7},
    {"Id": 17, "LifeArea": "Husband (Ma)", "house": 7, "karaka": "Mars", "sec_house": 7},
    {"Id": 18, "LifeArea": "Pregnancy", "house": 5, "karaka": "Jupiter", "sec_house": 8},
    {"Id": 19, "LifeArea": "Inheritance", "house": 8, "karaka": "Saturn", "sec_house": 9},
    {"Id": 20, "LifeArea": "Longevity", "house": 8, "karaka": "Saturn", "sec_house": 3},
    {"Id": 21, "LifeArea": "Father", "house": 9, "karaka": "Sun", "sec_house": 9},
    {"Id": 22, "LifeArea": "Fortune", "house": 9, "karaka": "Jupiter", "sec_house": 11},
    {"Id": 23, "LifeArea": "Status", "house": 10, "karaka": "Sun", "sec_house": 1},
    {"Id": 24, "LifeArea": "Business", "house": 7, "karaka": "Mercury", "sec_house": 10},
    {"Id": 25, "LifeArea": "Job", "house": 6, "karaka": "Saturn", "sec_house": 10},
    {"Id": 26, "LifeArea": "Income", "house": 11, "karaka": "Jupiter", "sec_house": 2},
    {"Id": 27, "LifeArea": "Health & Wealth", "house": 1, "karaka": "Jupiter", "sec_house": 2}
]


class AfflictionEngine:
    """Calculates Dasvarga dignity matrix, Free Will scores, and 26 Life Area breakdowns."""

    def __init__(self, chart: KundaliChart):
        self.chart = chart
        self.all_vargas = VargaCalculator.calculate_all_vargas(chart)
        self.house_lords = self._compute_house_lords()
        self.dispositors = self._compute_dispositors()

    def _compute_house_lords(self) -> Dict[int, str]:
        lords = {}
        for h in range(1, 13):
            sign_idx = ((self.chart.lagna_sign_id - 1 + (h - 1)) % 12)
            sign_name = SIGN_NAMES[sign_idx]
            lords[h] = SIGN_LORDS[sign_name]
        return lords

    def _compute_dispositors(self) -> Dict[str, str]:
        disps = {}
        for p_name, pos in self.chart.planets.items():
            disps[p_name] = SIGN_LORDS.get(pos.sign_name, "Sun")
        return disps

    def get_dignity(self, planet_name: str, sign_name: str) -> Tuple[str, str]:
        """Return (text_description, css_class) for a planet in a sign."""
        exalt_info = EXALTATION.get(planet_name)
        if exalt_info and sign_name == exalt_info[0]:
            return f"{sign_name} : Exaltation", "exalt"

        deb_info = DEBILITATION.get(planet_name)
        if deb_info and sign_name == deb_info[0]:
            return f"{sign_name} : Debilitation", "deb"

        mool_info = MOOLATRIKONA.get(planet_name)
        if mool_info and sign_name == mool_info[0]:
            return f"{sign_name} : Mooltrikon", "mool"

        if sign_name in OWN_SIGNS.get(planet_name, []):
            return f"{sign_name} : Own Sign", "own"

        lord = SIGN_LORDS.get(sign_name, "")
        if lord in NATURAL_FRIENDS.get(planet_name, []):
            return f"{sign_name} : Friend Sign", "friend"
        if lord in NATURAL_ENEMIES.get(planet_name, []):
            return f"{sign_name} : Enemy Sign", "enemy"
        return f"{sign_name} : Neutral Sign", "neutral"

    def calculate_dasvarga_table(self) -> List[Dict[str, Any]]:
        """
        Calculates dignity for Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn
        across 11 vargas: D1, D2, D3, D7, D9, D10, D12, D16, D24, D30, D60.
        """
        varga_codes = ["D1", "D2", "D3", "D7", "D9", "D10", "D12", "D16", "D24", "D30", "D60"]
        target_planets = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]

        table = []
        for code in varga_codes:
            row: Dict[str, Any] = {"Planets": code}
            vchart = self.all_vargas.get(code)
            for p in target_planets:
                if not vchart or p not in vchart.planets:
                    row[p] = "Unknown"
                    continue
                sign_name = vchart.planets[p].sign_name
                text, css = self.get_dignity(p, sign_name)
                if css in ["own", "mool", "exalt", "deb"]:
                    row[p] = {"text": text, "className": css}
                else:
                    row[p] = text
            table.append(row)
        return table

    def calculate_house_points(self, detailed: bool = False) -> List[Dict[str, Any]]:
        """
        Calculates Free Will and Affliction points for all 12 houses.
        detailed=False -> counts ("1", "2")
        detailed=True -> planet symbols ("Ju", "Ma,Ra")
        """
        results = []
        benefics = ["Jupiter", "Venus", "Mercury"]
        malefics = ["Sun", "Mars", "Saturn", "Rahu", "Ketu"]
        separative_planets = ["Sun", "Saturn", "Rahu", "Mars"]

        trikona_lords = [self.house_lords[1], self.house_lords[5], self.house_lords[9]]
        dusthana_lords = [self.house_lords[6], self.house_lords[8], self.house_lords[12]]

        for h in range(1, 13):
            # Planets occupying this house
            occupants = [p for p, pos in self.chart.planets.items() if pos.house_from_lagna == h]

            # Aspecting planets
            aspects = []
            for p, pos in self.chart.planets.items():
                phouse = pos.house_from_lagna
                dist = ((h - phouse) % 12) + 1
                if dist == 7:
                    aspects.append(p)
                elif p == "Mars" and dist in [4, 8]:
                    aspects.append(p)
                elif p == "Jupiter" and dist in [5, 9]:
                    aspects.append(p)
                elif p == "Saturn" and dist in [3, 10]:
                    aspects.append(p)

            influencing = list(dict.fromkeys(occupants + aspects))

            soumya_p = [p for p in influencing if p in benefics]
            krura_p = [p for p in influencing if p in malefics]
            t159_p = [p for p in influencing if p in trikona_lords]
            d6812_p = [p for p in influencing if p in dusthana_lords]
            sep_p = [p for p in influencing if p in separative_planets]

            # Dispositor
            h_lord = self.house_lords[h]
            disp_sym = PLANET_SYMBOLS.get(h_lord, "0") if h_lord in occupants else "0"

            # Check mutual exchange
            exchange = "0"
            for other_h in range(1, 13):
                if other_h != h:
                    other_lord = self.house_lords[other_h]
                    if other_lord in occupants:
                        other_occupants = [p for p, pos in self.chart.planets.items() if pos.house_from_lagna == other_h]
                        if h_lord in other_occupants:
                            exchange = f"{other_h}th House"

            # Digbala
            digbala = ""
            if h == 1 and any(p in ["Mercury", "Jupiter"] for p in occupants):
                digbala = "Digbala"
            elif h == 4 and any(p in ["Moon", "Venus"] for p in occupants):
                digbala = "Digbala"
            elif h == 7 and any(p == "Saturn" for p in occupants):
                digbala = "Digbala"
            elif h == 10 and any(p in ["Sun", "Mars"] for p in occupants):
                digbala = "Digbala"
            elif h in [4, 7, 10] and len(occupants) > 0 and not digbala:
                digbala = "Nirbala"

            # Kaalbala
            kaalbala = "Bali" if h in [1, 3, 5, 9, 12] else ""

            # Free Will Formula
            base_score = 45.0
            base_score += len(soumya_p) * 12.0
            base_score += len(t159_p) * 8.0
            base_score -= len(krura_p) * 14.0
            base_score -= len(d6812_p) * 9.0
            base_score -= len(sep_p) * 4.0
            if digbala == "Digbala":
                base_score += 10.0
            elif digbala == "Nirbala":
                base_score -= 10.0
            free_will = max(0.0, min(100.0, base_score))

            def _fmt(planets: List[str]) -> str:
                if detailed:
                    return ",".join([PLANET_SYMBOLS.get(p, p) for p in planets]) if planets else "0"
                return str(len(planets))

            results.append({
                "house": f"{h}{'st' if h==1 else 'nd' if h==2 else 'rd' if h==3 else 'th'} House",
                "freeWill": round(free_will, 1) if free_will % 1 != 0 else int(free_will),
                "soumya": _fmt(soumya_p),
                "lords159": _fmt(t159_p),
                "krura": _fmt(krura_p),
                "lords6812": _fmt(d6812_p),
                "dispositor": disp_sym if detailed else ("1" if disp_sym != "0" else "0"),
                "exchange": exchange,
                "seperative": _fmt(sep_p),
                "digbala": digbala,
                "kaalbala": kaalbala
            })

        return results

    def calculate_planet_points(self, detailed: bool = False) -> List[Dict[str, Any]]:
        """Calculates Free Will, affliction points, and Dashvarga score for 9 planets."""
        results = []
        benefics = ["Jupiter", "Venus", "Mercury"]
        malefics = ["Sun", "Mars", "Saturn", "Rahu", "Ketu"]
        separative_planets = ["Sun", "Saturn", "Rahu", "Mars"]

        trikona_lords = [self.house_lords[1], self.house_lords[5], self.house_lords[9]]
        dusthana_lords = [self.house_lords[6], self.house_lords[8], self.house_lords[12]]

        dasvarga = self.calculate_dasvarga_table()

        planets_order = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]
        for p in planets_order:
            pos = self.chart.planets.get(p)
            if not pos:
                continue

            h = pos.house_from_lagna
            co_planets = [op for op, opos in self.chart.planets.items() if opos.house_from_lagna == h and op != p]

            aspecting = []
            for op, opos in self.chart.planets.items():
                if op != p:
                    dist = ((h - opos.house_from_lagna) % 12) + 1
                    if dist == 7:
                        aspecting.append(op)
                    elif op == "Mars" and dist in [4, 8]:
                        aspecting.append(op)
                    elif op == "Jupiter" and dist in [5, 9]:
                        aspecting.append(op)
                    elif op == "Saturn" and dist in [3, 10]:
                        aspecting.append(op)

            influencing = list(dict.fromkeys(co_planets + aspecting))

            soumya_p = [ip for ip in influencing if ip in benefics]
            krura_p = [ip for ip in influencing if ip in malefics]
            t159_p = [ip for ip in influencing if ip in trikona_lords]
            d6812_p = [ip for ip in influencing if ip in dusthana_lords]
            sep_p = [ip for ip in influencing if ip in separative_planets]

            # Dispositor
            disp = self.dispositors.get(p, "Sun")
            disp_sym = PLANET_SYMBOLS.get(disp, "0")

            # Dashvarga score (count of positive dignities across 11 vargas)
            dv_score = 0
            for row in dasvarga:
                val = row.get(p, "")
                if isinstance(val, dict):
                    cls = val.get("className", "")
                    if cls in ["exalt", "mool", "own"]:
                        dv_score += 1
                elif "Friend" in str(val) or "Own" in str(val):
                    dv_score += 1

            base_score = 42.0 + (dv_score * 3.5)
            base_score += len(soumya_p) * 11.0
            base_score += len(t159_p) * 7.0
            base_score -= len(krura_p) * 13.0
            base_score -= len(d6812_p) * 8.0
            free_will = max(0.0, min(100.0, base_score))

            def _fmt(planets: List[str]) -> str:
                if detailed:
                    return ",".join([PLANET_SYMBOLS.get(ip, ip) for ip in planets]) if planets else "0"
                return str(len(planets))

            results.append({
                "planet": p,
                "freeWill": round(free_will, 1) if free_will % 1 != 0 else int(free_will),
                "soumya": _fmt(soumya_p),
                "lords159": _fmt(t159_p),
                "krura": _fmt(krura_p),
                "lords6812": _fmt(d6812_p),
                "dispositor": disp_sym if detailed else ("1" if disp_sym != "0" else "0"),
                "exchange": "0",
                "seperative": _fmt(sep_p),
                "dashvarga": dv_score
            })

        return results

    def get_life_area_detail(self, life_area_id: int) -> Dict[str, Any]:
        """Calculates 3-Pillar House & Lord affliction breakdown for a life area."""
        area = next((a for a in LIFE_AREAS if a["Id"] == life_area_id), LIFE_AREAS[0])
        h_pri = area["house"]
        karaka = area["karaka"]
        h_sec = area["sec_house"]

        pri_lord = self.house_lords[h_pri]
        sec_lord = self.house_lords[h_sec]

        house_points = {hp["house"]: hp for hp in self.calculate_house_points(detailed=True)}
        planet_points = {pp["planet"]: pp for pp in self.calculate_planet_points(detailed=True)}

        def _row(label: str, pt: Dict[str, Any]) -> List[str]:
            return [
                label,
                pt.get("soumya", "0"),
                pt.get("lords159", "0"),
                pt.get("krura", "0"),
                pt.get("lords6812", "0"),
                pt.get("seperative", "0")
            ]

        h1_label = f"House : {h_pri}{'st' if h_pri==1 else 'nd' if h_pri==2 else 'rd' if h_pri==3 else 'th'} House"
        k_label = f"Karaka : {karaka}"
        h2_label = f"Ho./Karaka : {h_sec}{'st' if h_sec==1 else 'nd' if h_sec==2 else 'rd' if h_sec==3 else 'th'} House"

        house_rows = [
            _row(h1_label, house_points.get(f"{h_pri}{'st' if h_pri==1 else 'nd' if h_pri==2 else 'rd' if h_pri==3 else 'th'} House", {})),
            _row(k_label, planet_points.get(karaka, {})),
            _row(h2_label, house_points.get(f"{h_sec}{'st' if h_sec==1 else 'nd' if h_sec==2 else 'rd' if h_sec==3 else 'th'} House", {}))
        ]

        l1_label = f"{h_pri}{'st' if h_pri==1 else 'nd' if h_pri==2 else 'rd' if h_pri==3 else 'th'} House Lord : {pri_lord}"
        l2_label = f"{h_sec}{'st' if h_sec==1 else 'nd' if h_sec==2 else 'rd' if h_sec==3 else 'th'} House Lord : {sec_lord}"

        lord_rows = [
            _row(l1_label, planet_points.get(pri_lord, {})),
            _row(k_label, planet_points.get(karaka, {})),
            _row(l2_label, planet_points.get(sec_lord, {}))
        ]

        return {
            "HouseRows": house_rows,
            "LordRows": lord_rows
        }

    def get_rashi_prediction(self, life_area_id: int) -> Dict[str, Any]:
        """Classifies signs of the 3 pillars with Mobility, Element, Varna, Purushartha, etc."""
        area = next((a for a in LIFE_AREAS if a["Id"] == life_area_id), LIFE_AREAS[0])
        h_pri = area["house"]
        karaka = area["karaka"]
        h_sec = area["sec_house"]

        pri_lord = self.house_lords[h_pri]
        sec_lord = self.house_lords[h_sec]

        h_pri_sign = SIGN_NAMES[((self.chart.lagna_sign_id - 1 + (h_pri - 1)) % 12)]
        h_sec_sign = SIGN_NAMES[((self.chart.lagna_sign_id - 1 + (h_sec - 1)) % 12)]

        k_pos = self.chart.planets.get(karaka)
        k_sign = k_pos.sign_name if k_pos else "Aries"

        l_pri_pos = self.chart.planets.get(pri_lord)
        l_pri_sign = l_pri_pos.sign_name if l_pri_pos else "Aries"

        l_sec_pos = self.chart.planets.get(sec_lord)
        l_sec_sign = l_sec_pos.sign_name if l_sec_pos else "Aries"

        def _make_row(title: str, sign_name: str) -> List[str]:
            q = SIGN_QUALITIES.get(sign_name, ("Movable", "Fire", "Kshatriya", "Dharm", "Male", "Head Rising", "Day", "Sthiti"))
            return [title, sign_name, q[0], q[1], q[2], q[3], q[4], q[5], q[6], q[7]]

        house_rows = [
            _make_row(f"House : {h_pri}{'st' if h_pri==1 else 'nd' if h_pri==2 else 'rd' if h_pri==3 else 'th'} House", h_pri_sign),
            _make_row(f"Karaka : {karaka}", k_sign),
            _make_row(f"Ho./Karaka : {h_sec}{'st' if h_sec==1 else 'nd' if h_sec==2 else 'rd' if h_sec==3 else 'th'} House", h_sec_sign)
        ]

        lord_rows = [
            _make_row(f"{h_pri}{'st' if h_pri==1 else 'nd' if h_pri==2 else 'rd' if h_pri==3 else 'th'} House Lord : {pri_lord}", l_pri_sign),
            _make_row(f"Karaka : {karaka}", k_sign),
            _make_row(f"{h_sec}{'st' if h_sec==1 else 'nd' if h_sec==2 else 'rd' if h_sec==3 else 'th'} House Lord : {sec_lord}", l_sec_sign)
        ]

        return {
            "HouseRashiRows": house_rows,
            "LordRashiRows": lord_rows
        }

    def calculate_remedy(self, life_area_id: int = 1, lords: bool = False) -> List[Dict[str, Any]]:
        """
        Generates the 3-pillar Grahalakshanam Classical Affliction Remedy Matrix (10 rows):
        1. Houses & Karaka (or House Lord & Karaka)
        2. Free Will (percentage)
        3. Score (points)
        4. Benefic / Malefic
        5. Type Of Remedy
        6. Rudraksha / Herbs
        7. Yagya / Gems
        8. Mantra
        9. Donation
        10. Testing of Remedy : Vriksha Ropana
        """
        area = next((a for a in LIFE_AREAS if a["Id"] == life_area_id), LIFE_AREAS[0])
        h_pri = area["house"]
        karaka = area["karaka"]
        h_sec = area["sec_house"]

        pri_lord = self.house_lords[h_pri]
        sec_lord = self.house_lords[h_sec]

        p_house = pri_lord
        p_karaka = karaka
        p_sec = sec_lord

        def _suffix(n: int) -> str:
            return "st" if n == 1 else "nd" if n == 2 else "rd" if n == 3 else "th"

        # 1. Header Row
        if not lords:
            row_header = {
                "label": "Houses & Karaka",
                "house": f"{h_pri}{_suffix(h_pri)} House",
                "karaka": karaka,
                "houseFromKaraka": f"{h_sec}{_suffix(h_sec)} House"
            }
        else:
            row_header = {
                "label": "House Lord & Karaka",
                "house": f"{h_pri}{_suffix(h_pri)} House Lord: {pri_lord}",
                "karaka": karaka,
                "houseFromKaraka": f"{h_sec}{_suffix(h_sec)} House Lord: {sec_lord}"
            }

        # Calculate Scores & Free Will
        hp_dict = {hp["house"]: hp for hp in self.calculate_house_points(detailed=False)}
        pp_dict = {pp["planet"]: pp for pp in self.calculate_planet_points(detailed=False)}

        # Free will & points
        if not lords:
            h_key = f"{h_pri}{_suffix(h_pri)} House"
            sec_key = f"{h_sec}{_suffix(h_sec)} House"
            fw_h = hp_dict.get(h_key, {}).get("freeWill", 40)
            fw_k = pp_dict.get(p_karaka, {}).get("freeWill", 35)
            fw_s = hp_dict.get(sec_key, {}).get("freeWill", 45)

            sc_h = round((fw_h - 50.0) / 10.0, 1)
            sc_k = round((fw_k - 50.0) / 10.0, 1)
            sc_s = round((fw_s - 50.0) / 10.0, 1)
        else:
            fw_h = pp_dict.get(p_house, {}).get("freeWill", 45)
            fw_k = pp_dict.get(p_karaka, {}).get("freeWill", 35)
            fw_s = pp_dict.get(p_sec, {}).get("freeWill", 50)

            sc_h = round((fw_h - 50.0) / 10.0, 1)
            sc_k = round((fw_k - 50.0) / 10.0, 1)
            sc_s = round((fw_s - 50.0) / 10.0, 1)

        def _fmt_score(sc: float) -> str:
            sign = "+ " if sc > 0 else ("- " if sc < 0 else "")
            return f"{sign}{abs(sc)} Point" if sc != 0 else "0 Point"

        def _ben_mal(sc: float, fw: float) -> Dict[str, str]:
            if sc >= 0 and fw >= 45:
                return {"text": "Benefic", "className": "benefic"}
            return {"text": "Malefic", "className": "malefic"}

        bm_h = _ben_mal(sc_h, fw_h)
        bm_k = _ben_mal(sc_k, fw_k)
        bm_s = _ben_mal(sc_s, fw_s)

        # 2. Free Will Row
        row_fw = {
            "label": "Free Will",
            "house": f"{int(fw_h)}%",
            "karaka": f"{int(fw_k)}%",
            "houseFromKaraka": f"{int(fw_s)}%"
        }

        # 3. Score Row
        row_score = {
            "label": "Score",
            "house": _fmt_score(sc_h),
            "karaka": _fmt_score(sc_k),
            "houseFromKaraka": _fmt_score(sc_s)
        }

        # 4. Benefic / Malefic Row
        row_bm = {
            "label": "Benefic / Malefic",
            "house": bm_h,
            "karaka": bm_k,
            "houseFromKaraka": bm_s
        }

        # 5. Type Of Remedy
        def _rem_type(bm: Dict[str, str], fw: float) -> str:
            if bm["className"] == "benefic" and fw >= 50:
                return "Gemstones, Rudraksha, Mantra & Yagya"
            return "Rudraksha, Yagya, Mantra, & Donation"

        row_type = {
            "label": "Type Of Remedy",
            "house": _rem_type(bm_h, fw_h),
            "karaka": _rem_type(bm_k, fw_k),
            "houseFromKaraka": _rem_type(bm_s, fw_s)
        }

        # 6. Rudraksha / Herbs
        def _get_rudraksha(planet: str) -> str:
            cat = PLANETARY_REMEDY_CATALOG.get(planet, PLANETARY_REMEDY_CATALOG["Sun"])
            return cat["rudraksha"]

        row_rud = {
            "label": "Rudraksha / Herbs",
            "house": _get_rudraksha(p_house),
            "karaka": _get_rudraksha(p_karaka),
            "houseFromKaraka": _get_rudraksha(p_sec)
        }

        # 7. Yagya / Gems
        def _get_yagya_gem(planet: str, bm: Dict[str, str], fw: float) -> str:
            cat = PLANETARY_REMEDY_CATALOG.get(planet, PLANETARY_REMEDY_CATALOG["Sun"])
            if bm["className"] == "benefic" and fw >= 50:
                return f"Auspicious Gemstone: {cat['gem']}"
            return cat["yagya"]

        row_yg = {
            "label": "Yagya / Gems",
            "house": _get_yagya_gem(p_house, bm_h, fw_h),
            "karaka": _get_yagya_gem(p_karaka, bm_k, fw_k),
            "houseFromKaraka": _get_yagya_gem(p_sec, bm_s, fw_s)
        }

        # 8. Mantra
        def _get_mantra(planet: str) -> Dict[str, Any]:
            return PLANETARY_REMEDY_CATALOG.get(planet, PLANETARY_REMEDY_CATALOG["Sun"])["mantra"]

        row_man = {
            "label": "Mantra",
            "house": _get_mantra(p_house),
            "karaka": _get_mantra(p_karaka),
            "houseFromKaraka": _get_mantra(p_sec)
        }

        # 9. Donation
        def _get_donation(planet: str) -> Dict[str, Any]:
            return PLANETARY_REMEDY_CATALOG.get(planet, PLANETARY_REMEDY_CATALOG["Sun"])["donation"]

        row_don = {
            "label": "Donation",
            "house": _get_donation(p_house),
            "karaka": _get_donation(p_karaka),
            "houseFromKaraka": _get_donation(p_sec)
        }

        # 10. Testing of Remedy : Vriksha Ropana
        def _get_vriksha(planet: str) -> str:
            return PLANETARY_REMEDY_CATALOG.get(planet, PLANETARY_REMEDY_CATALOG["Sun"])["vriksha"]

        row_vriksha = {
            "label": "Testing of Remedy : Vriksha Ropana",
            "house": _get_vriksha(p_house),
            "karaka": _get_vriksha(p_karaka),
            "houseFromKaraka": _get_vriksha(p_sec)
        }

        return [
            row_header,
            row_fw,
            row_score,
            row_bm,
            row_type,
            row_rud,
            row_yg,
            row_man,
            row_don,
            row_vriksha
        ]


# Classical planetary remedies reference dictionary
PLANETARY_REMEDY_CATALOG: Dict[str, Dict[str, Any]] = {
    "Sun": {
        "planet_hi": "सूर्य",
        "rudraksha": "Wear 1 Mukhi or 12 Mukhi Rudraksha in red/black thread around the Neck or in the Working Hand on the day of your Janma Nakshatra or Sunday or Surya Hora.",
        "yagya": "Vedic Surya Shanti Yagya For Pacifying The Planet Sun/Surya.",
        "gem": "Natural untreated Burma Ruby (माणिक्य) set in Gold on Ring Finger.",
        "mantra": {
            "title": "Sun Mantra (सूर्य मंत्र) :",
            "mantra": "ॐ ह्रां ह्रीं ह्रौं सः सूर्याय नमः ॥",
            "translit": "Aum Hran Hrin Hron seh Suryaye Namah",
            "note": "*This mantra should be chanted for 7,000 times within 40 days."
        },
        "donation": {
            "donation_title": "Sun Donation",
            "items": [
                "More than 12kg of wheat.",
                "Gemstone of Surya (Ruby) with Golden chain or Ring.",
                "Red Sandalwood (more than a fist full) – for health.",
                "Red silk cloth with Golden border.",
                "More than 3kg of wheat with a copper vessel - for family issues."
            ],
            "timing": "Donate these articles on the day of Pushya or Sunday or Surya Hora."
        },
        "vriksha": "Plant 2 plants or its multiples of मदार / श्वेतार्क - Madar (Calotropis procera) on the day of your Janma Nakshatra or Sunday or Surya Hora."
    },
    "Moon": {
        "planet_hi": "चन्द्र",
        "rudraksha": "Wear 2 Mukhi Rudraksha in red/black thread around the Neck or in the Working Hand on the day of Pushya or Monday or Moon Hora.",
        "yagya": "Vedic Chandra Shanti Yagya For Pacifying The Planet Moon/Chandra.",
        "gem": "Natural untreated South Sea Pearl (मोती) set in Silver on Little Finger.",
        "mantra": {
            "title": "Moon Mantra (चंद्र मंत्र) :",
            "mantra": "ॐ श्रां श्रीं श्रौं सः चंद्राय नमः ॥",
            "translit": "Aum Shran Shrin Shron seh Chandraye Namah",
            "note": "*This mantra should be chanted for 11,000 times within 40 days."
        },
        "donation": {
            "donation_title": "Moon Donation",
            "items": [
                "4 Carat Basra Pearl.",
                "Rice more than 10kg.",
                "Silk cloth with Golden border.",
                "Silver vessels.",
                "Small container of silver filled with Milk."
            ],
            "timing": "Donate these articles on the day of Pushya or Monday or Moon Hora."
        },
        "vriksha": "Plant 8 plants or its multiples of पलाश - Palasha (Butea monosperma) on the time when moon or lagna in the Cancer without affliction."
    },
    "Mars": {
        "planet_hi": "मंगल",
        "rudraksha": "Wear 3 Mukhi Rudraksha in red/black thread around the Neck or in the Working Hand on the day of Pushya or Tuesday or Mars Hora.",
        "yagya": "Vedic Mangala Shanti Yagya For Pacifying The Planet Mars/Mangala.",
        "gem": "Natural untreated Red Coral (मूंगा) set in Copper or Gold on Ring Finger.",
        "mantra": {
            "title": "Mars Mantra (मंगल मंत्र) :",
            "mantra": "ॐ क्रां क्रीं क्रौं सः भौमाय नमः ॥",
            "translit": "Aum Kran Krin Kron seh Bhaumaaye Namah",
            "note": "*This mantra should be chanted for 10,000 times within 40 days."
        },
        "donation": {
            "donation_title": "Mars Donation",
            "items": [
                "Red Silk cloth with Golden Border.",
                "More than 7kgs of Toor Daal.",
                "Copper triangle or Yantra of Mangala.",
                "Gemstone of Mars, Red Coral with Golden Chain or Ring.",
                "Silver Naagaprati."
            ],
            "timing": "Donate these articles on the day of Pushya or Tuesday or Mangala Hora."
        },
        "vriksha": "Plant 8 plants or its multiples of कत्था या खैर - Khadira (Acacia catechu) on the time when moon or lagna in the Aries/Scorpio without affliction."
    },
    "Mercury": {
        "planet_hi": "बुध",
        "rudraksha": "Wear 4 Mukhi or 10 Mukhi Rudraksha in red/black thread around the Neck or in the Working Hand on the day of your Janma Nakshatra or Wednesday or Mercury Hora.",
        "yagya": "Vedic Budha Shanti Yagya For Pacifying The Planet Mercury/Budha.",
        "gem": "Natural untreated Zambian Emerald (पन्ना) set in Bronze or Gold on Little Finger.",
        "mantra": {
            "title": "Mercury Mantra (बुध मंत्र) :",
            "mantra": "ॐ ब्रां ब्रीं ब्रौं सः बुधाय नमः ॥",
            "translit": "Aum Bran Brin Bron seh Budhaye Namah",
            "note": "*This mantra should be chanted for 9,000 times within 40 days."
        },
        "donation": {
            "donation_title": "Mercury Donation",
            "items": [
                "Green Moong Dal more than 9kg.",
                "Green Silk cloth with Golden border.",
                "Bronze or Brass utensils.",
                "Camphor and green fruits/vegetables.",
                "Emerald gemstone or green jade."
            ],
            "timing": "Donate these articles on the day of Janma Nakshatra or Wednesday or Budha Hora."
        },
        "vriksha": "Plant 2 plants or its multiples of कटहल / अपामार्ग - Panasa / Apamarga on the time when moon or lagna in the Gemini/Virgo without affliction."
    },
    "Jupiter": {
        "planet_hi": "गुरु",
        "rudraksha": "Wear 5 Mukhi Rudraksha in yellow/red thread around the Neck or in the Working Hand on the day of your Janma Nakshatra or Thursday or Jupiter Hora.",
        "yagya": "Vedic Brihaspati Shanti Yagya For Pacifying The Planet Jupiter/Guru.",
        "gem": "Natural untreated Ceylon Yellow Sapphire (पुखराज) set in Gold on Index Finger.",
        "mantra": {
            "title": "Jupiter Mantra (गुरु मंत्र) :",
            "mantra": "ॐ ग्रां ग्रीं ग्रौं सः गुरवे नमः ॥",
            "translit": "Aum Gran Grin Gron seh Gurave Namah",
            "note": "*This mantra should be chanted for 19,000 times within 40 days."
        },
        "donation": {
            "donation_title": "Jupiter Donation",
            "items": [
                "Chana Dal more than 16kg.",
                "Yellow Silk cloth with Golden border.",
                "Turmeric (Haldi) roots.",
                "Yellow Sapphire or Gold coin.",
                "Books or educational material to poor scholars."
            ],
            "timing": "Donate these articles on the day of Janma Nakshatra or Thursday or Guru Hora."
        },
        "vriksha": "Plant 5 plants or its multiples of पीपल - Peepal (Ficus religiosa) on Thursday or Guru Hora."
    },
    "Venus": {
        "planet_hi": "शुक्र",
        "rudraksha": "Wear 6 Mukhi or 13 Mukhi Rudraksha in white/red thread around the Neck or in the Working Hand on the day of your Janma Nakshatra or Friday or Venus Hora.",
        "yagya": "Vedic Shukra Shanti Yagya For Pacifying The Planet Venus/Shukra.",
        "gem": "Natural untreated Diamond or White Zircon (हीरा / जरकन) set in Platinum or Silver.",
        "mantra": {
            "title": "Venus Mantra (शुक्र मंत्र) :",
            "mantra": "ॐ द्रां द्रीं द्रौं सः शुक्राय नमः ॥",
            "translit": "Aum Dran Drin Dron seh Shukraye Namah",
            "note": "*This mantra should be chanted for 16,000 times within 40 days."
        },
        "donation": {
            "donation_title": "Venus Donation",
            "items": [
                "White Sesame (Safed Til) and Mishri/Sugar.",
                "White Silk cloth with Silver border.",
                "Silver ornaments or vessels.",
                "Pure Ghee and Perfume/Attar.",
                "Donation for marriage of poor girls."
            ],
            "timing": "Donate these articles on the day of Janma Nakshatra or Friday or Shukra Hora."
        },
        "vriksha": "Plant 6 plants or its multiples of गूलर - Audumbara (Ficus glomerata) on Friday or Shukra Hora."
    },
    "Saturn": {
        "planet_hi": "शनि",
        "rudraksha": "Wear 4 Mukhi or 7 Mukhi Rudraksha in red/black thread around the Neck or in the Working Hand on the day of Pushya or Saturday or Saturn Hora.",
        "yagya": "Vedic Shani Shanti Yagya For Pacifying The Planet Saturn/Shani.",
        "gem": "Natural untreated Ceylon Blue Sapphire (नीलम) or Amethyst set in Panchdhatu.",
        "mantra": {
            "title": "Saturn Mantra (शनि मंत्र) :",
            "mantra": "ॐ प्रां प्रीं प्रौं सः शनैश्चराय नमः ॥",
            "translit": "Aum Pram Prim Pron seh Shanicharaye Namah",
            "note": "*This mantra should be chanted for 23,000 times within 40 days."
        },
        "donation": {
            "donation_title": "Saturn Donation",
            "items": [
                "More than 1kg Tila with Iron vessel.",
                "More than 5kg Tila.",
                "Dark blue cloth with Golden border.",
                "Food donation to homeless/beggars.",
                "Donation of steel utensils."
            ],
            "timing": "Donate these articles on the day of Pushya or Saturday or Shani Hora."
        },
        "vriksha": "Plant 8 plants or its multiples of खेजड़ी या शमी - Shami (Prosopis cineraria) on the day of Pushya or Saturday or Shani Hora."
    },
    "Rahu": {
        "planet_hi": "राहु",
        "rudraksha": "Wear 8 Mukhi Rudraksha in blue/black thread around the Neck or in the Working Hand on the day of your Janma Nakshatra or Saturday or Rahu Kaal.",
        "yagya": "Vedic Rahu Shanti Yagya For Pacifying The Shadow Planet Rahu.",
        "gem": "Natural untreated Hessonite Garnet (गोमेद) set in Silver on Middle Finger.",
        "mantra": {
            "title": "Rahu Mantra (राहु मंत्र) :",
            "mantra": "ॐ भ्रां भ्रीं भ्रौं सः राहवे नमः ॥",
            "translit": "Aum Bhran Bhrin Bhron seh Rahave Namah",
            "note": "*This mantra should be chanted for 18,000 times within 40 days."
        },
        "donation": {
            "donation_title": "Rahu Donation",
            "items": [
                "Mustard seeds and Urad dal.",
                "Smoky / Dark blue blanket.",
                "Seven types of grains (Satnaja).",
                "Coconut with water offered to running stream.",
                "Lead or Gomedh stone."
            ],
            "timing": "Donate these articles on Saturday evening or during Rahu Kaal."
        },
        "vriksha": "Plant 8 plants or its multiples of दूर्वा / चन्दन - Durva / Chandan on Saturday evening."
    },
    "Ketu": {
        "planet_hi": "केतु",
        "rudraksha": "Wear 9 Mukhi Rudraksha in multi-color/black thread around the Neck or in the Working Hand on the day of your Janma Nakshatra or Tuesday/Thursday.",
        "yagya": "Vedic Ketu Shanti Yagya For Pacifying The Shadow Planet Ketu.",
        "gem": "Natural untreated Chrysoberyl Cat's Eye (लहसुनिया) set in Silver.",
        "mantra": {
            "title": "Ketu Mantra (केतु मंत्र) :",
            "mantra": "ॐ स्रां स्रीं स्रौं सः केतवे नमः ॥",
            "translit": "Aum Sran Srin Sron seh Ketave Namah",
            "note": "*This mantra should be chanted for 17,000 times within 40 days."
        },
        "donation": {
            "donation_title": "Ketu Donation",
            "items": [
                "Multi-colored blanket to needy.",
                "Black and white sesame seeds.",
                "Cat's eye stone or copper wire.",
                "Feed street dogs with bread and milk.",
                "Kusha grass and spiritual books."
            ],
            "timing": "Donate these articles on Tuesday/Thursday morning."
        },
        "vriksha": "Plant 9 plants or its multiples of कुश / अश्वगंधा - Kusha / Ashwagandha on Tuesday morning."
    }
}

