"""
Kundali Chart SVG Renderer for JyotishOS.
Generates authentic, high-contrast, vector-rendered North Indian Diamond,
South Indian Box, and East Indian Surya charts with classical high-contrast color grading.
"""

from typing import Dict, List, Tuple, Optional, Any
from ..core.models import KundaliChart, VargaChart


class ChartRenderer:
    """Generates standalone SVG strings for Vedic Kundali charts with classical high-contrast color grading."""

    # Planet-specific color grading matching Vedic
    PLANET_COLORS = {
        "Su": "#B45309",  # Sun - Saffron Amber
        "Mo": "#1D4ED8",  # Moon - Royal Indigo/Sapphire
        "Ma": "#DC2626",  # Mars - Ruby Crimson
        "Me": "#059669",  # Mercury - Emerald Green
        "Ju": "#D97706",  # Jupiter - Sacred Gold
        "Ve": "#0D9488",  # Venus - Radiant Teal
        "Sa": "#1E293B",  # Saturn - Deep Slate/Charcoal
        "Ra": "#6D28D9",  # Rahu - Royal Purple
        "Ke": "#78350F",  # Ketu - Smoky Bronze
        "Asc": "#7C3AED", # Ascendant / Lagna
        "Ur": "#0284C7",
        "Ne": "#2563EB",
        "Pl": "#475569",
    }

    @classmethod
    def get_planet_color(cls, short_name: str) -> str:
        clean_key = short_name.split("(")[0].replace("*", "").strip()
        return cls.PLANET_COLORS.get(clean_key, "#000000")

    @classmethod
    def render_north_indian_svg(cls, chart: KundaliChart, title: str = "Lagna Kundali (D1)", varga_code: str = "D1") -> str:
        """
        Renders a classical North Indian diamond chart in SVG format with classical high-contrast color grading.
        House positions are geometrically fixed; sign numbers and planets rotate.
        """
        target_varga = chart.vargas.get(varga_code) if (chart.vargas and varga_code in chart.vargas) else None
        lagna_s_id = target_varga.lagna_sign_id if target_varga else chart.lagna_sign_id

        # Map planets to houses from Lagna
        house_planets: Dict[int, List[Tuple[str, str]]] = {h: [] for h in range(1, 13)}
        if target_varga:
            for p_name, vp in target_varga.planets.items():
                h_num = vp.house_number
                short_name = p_name[:2]
                if p_name in chart.planets and chart.planets[p_name].is_retrograde:
                    short_name += "(R)"
                color = cls.get_planet_color(short_name)
                house_planets[h_num].append((short_name, color))
        else:
            for p_name, p in chart.planets.items():
                h_num = p.house_from_lagna
                short_name = p_name[:2]
                if p.is_retrograde:
                    short_name += "(R)"
                if p.is_combust:
                    short_name += "*"
                color = cls.get_planet_color(short_name)
                house_planets[h_num].append((short_name, color))

        # Rashi number for each house: House 1 = lagna_s_id, House 2 = ...
        house_signs = {}
        for h in range(1, 13):
            s_id = ((lagna_s_id - 1 + (h - 1)) % 12) + 1
            house_signs[h] = s_id

        # SVG layout constants
        W, H = 420, 420

        # House polygon coordinates for subtle Vedic background shading
        # Kendra (1, 4, 7, 10): Soft Warm Gold (#FEF3C7 / 50%)
        # Trikona (5, 9): Soft Auspicious Emerald (#D1FAE5 / 50%)
        # Dusthana (6, 8, 12): Soft Rose Tint (#FEE2E2 / 40%)
        # Upachaya / Others (2, 3, 11): Clean Ivory (#F8FAFC)
        house_polygons = {
            1: ("210,30 305,120 210,210 115,120", "#FFFBEB"),   # H1 Kendra/Trikona (Gold)
            2: ("20,30 210,30 115,120", "#F8FAFC"),            # H2
            3: ("20,30 115,120 20,210", "#F8FAFC"),             # H3
            4: ("20,210 115,120 210,210 115,300", "#FFFBEB"),  # H4 Kendra (Gold)
            5: ("20,210 115,300 20,390", "#ECFDF5"),            # H5 Trikona (Emerald)
            6: ("20,390 115,300 210,390", "#FEF2F2"),           # H6 Dusthana (Rose)
            7: ("210,210 305,300 210,390 115,300", "#FFFBEB"),  # H7 Kendra (Gold)
            8: ("210,390 305,300 400,390", "#FEF2F2"),          # H8 Dusthana (Rose)
            9: ("400,390 305,300 400,210", "#ECFDF5"),          # H9 Trikona (Emerald)
            10: ("210,210 305,120 400,210 305,300", "#FFFBEB"), # H10 Kendra (Gold)
            11: ("400,210 305,120 400,30", "#F8FAFC"),          # H11 Upachaya
            12: ("400,30 305,120 210,30", "#FEF2F2"),           # H12 Dusthana (Rose)
        }

        house_coords = {
            1: (210, 115, 210, 65),
            2: (110, 65, 135, 45),
            3: (65, 110, 42, 135),
            4: (115, 210, 75, 210),
            5: (65, 305, 42, 285),
            6: (110, 355, 135, 375),
            7: (210, 305, 210, 355),
            8: (305, 355, 280, 375),
            9: (355, 305, 378, 285),
            10: (305, 210, 345, 210),
            11: (355, 110, 378, 135),
            12: (305, 65, 280, 45),
        }

        svg_parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="100%" height="380" style="background:#FFFFFF; border:2px solid #CBD5E1; border-radius:14px; box-shadow:0 4px 15px rgba(0,0,0,0.06); font-family: -apple-system, BlinkMacSystemFont, sans-serif;">',
            f'<text x="{W//2}" y="22" text-anchor="middle" fill="#78350F" font-size="14" font-weight="900" letter-spacing="0.5">{title}</text>',
        ]

        # Draw shaded house polygons
        for h_num, (poly_pts, bg_color) in house_polygons.items():
            svg_parts.append(f'<polygon points="{poly_pts}" fill="{bg_color}" stroke="none"/>')

        # Outer Box (Rich Saffron / Amber)
        svg_parts.append(f'<rect x="20" y="30" width="380" height="360" fill="none" stroke="#D97706" stroke-width="2.5"/>')
        # Diagonals
        svg_parts.append(f'<line x1="20" y1="30" x2="400" y2="390" stroke="#D97706" stroke-width="2"/>')
        svg_parts.append(f'<line x1="400" y1="30" x2="20" y2="390" stroke="#D97706" stroke-width="2"/>')
        # Inner Diamond
        svg_parts.append(f'<polygon points="210,30 400,210 210,390 20,210" fill="none" stroke="#D97706" stroke-width="2"/>')

        # Draw Rashi numbers and color-coded Planets
        for h_num, (cx, cy, rx, ry) in house_coords.items():
            sign_num = house_signs[h_num]
            planets_in_h = house_planets[h_num]

            # Sign Number (Crisp Dark Charcoal)
            svg_parts.append(
                f'<text x="{rx}" y="{ry}" text-anchor="middle" fill="#334155" font-size="11.5" font-weight="800">{sign_num}</text>'
            )
            # Planets (Color Graded)
            if planets_in_h:
                if len(planets_in_h) == 1:
                    p_txt, p_col = planets_in_h[0]
                    svg_parts.append(
                        f'<text x="{cx}" y="{cy}" text-anchor="middle" fill="{p_col}" font-size="12.5" font-weight="900">{p_txt}</text>'
                    )
                else:
                    # Multi-planet stack
                    count = len(planets_in_h)
                    start_y = cy - (count - 1) * 7
                    for idx, (p_txt, p_col) in enumerate(planets_in_h):
                        py = start_y + idx * 14
                        svg_parts.append(
                            f'<text x="{cx}" y="{py}" text-anchor="middle" fill="{p_col}" font-size="11.5" font-weight="900">{p_txt}</text>'
                        )

        svg_parts.append('</svg>')
        return "".join(svg_parts)

    @classmethod
    def render_south_indian_svg(cls, chart: KundaliChart, title: str = "South Indian Kundali", varga_code: str = "D1") -> str:
        """
        Renders a classical South Indian box chart in SVG format with classical high-contrast color grading.
        Signs are geometrically fixed clockwise starting from Pisces at top-left.
        """
        target_varga = chart.vargas.get(varga_code) if (chart.vargas and varga_code in chart.vargas) else None
        lagna_s_id = target_varga.lagna_sign_id if target_varga else chart.lagna_sign_id

        sign_planets: Dict[int, List[Tuple[str, str]]] = {s: [] for s in range(1, 13)}
        if target_varga:
            for p_name, vp in target_varga.planets.items():
                short_name = p_name[:2]
                if p_name in chart.planets and chart.planets[p_name].is_retrograde:
                    short_name += "(R)"
                color = cls.get_planet_color(short_name)
                sign_planets[vp.sign_id].append((short_name, color))
        else:
            for p_name, p in chart.planets.items():
                short_name = p_name[:2]
                if p.is_retrograde: short_name += "(R)"
                if p.is_combust: short_name += "*"
                color = cls.get_planet_color(short_name)
                sign_planets[p.sign_id].append((short_name, color))

        W, H = 420, 420
        cell_w, cell_h = 90, 85
        ox, oy = 30, 45

        grid_pos = {
            12: (0, 0), 1: (0, 1), 2: (0, 2), 3: (0, 3),
            11: (1, 0), 4: (1, 3),
            10: (2, 0), 5: (2, 3),
            9: (3, 0), 8: (3, 1), 7: (3, 2), 6: (3, 3)
        }

        sign_abbrevs = {
            1: "Mes", 2: "Vri", 3: "Mit", 4: "Kar",
            5: "Sim", 6: "Kan", 7: "Tul", 8: "Vrk",
            9: "Dha", 10: "Mak", 11: "Kum", 12: "Mee"
        }

        svg_parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="100%" height="380" style="background:#FFFFFF; border:2px solid #CBD5E1; border-radius:14px; box-shadow:0 4px 15px rgba(0,0,0,0.06); font-family: -apple-system, BlinkMacSystemFont, sans-serif;">',
            f'<text x="{W//2}" y="25" text-anchor="middle" fill="#78350F" font-size="14" font-weight="900">{title}</text>',
            f'<rect x="{ox}" y="{oy}" width="{cell_w*4}" height="{cell_h*4}" fill="none" stroke="#D97706" stroke-width="2.5"/>',
            f'<rect x="{ox + cell_w}" y="{oy + cell_h}" width="{cell_w*2}" height="{cell_h*2}" fill="#F8FAFC" stroke="#D97706" stroke-width="2"/>',
            f'<text x="{ox + cell_w*2}" y="{oy + cell_h*2 - 8}" text-anchor="middle" fill="#1E293B" font-size="13" font-weight="900">दक्षिण भारतीय चक्र</text>',
            f'<text x="{ox + cell_w*2}" y="{oy + cell_h*2 + 12}" text-anchor="middle" fill="#D97706" font-size="11" font-weight="700">Vedic Shastriya Edition</text>',
        ]

        for s_id, (row, col) in grid_pos.items():
            bx = ox + col * cell_w
            by = oy + row * cell_h
            is_lagna = (s_id == lagna_s_id)

            cell_bg = "#FFFBEB" if is_lagna else "#FFFFFF"
            svg_parts.append(f'<rect x="{bx}" y="{by}" width="{cell_w}" height="{cell_h}" fill="{cell_bg}" stroke="#D97706" stroke-width="1.2"/>')

            lbl_color = "#DC2626" if is_lagna else "#475569"
            svg_parts.append(f'<text x="{bx + 6}" y="{by + 16}" fill="{lbl_color}" font-size="10.5" font-weight="800">{sign_abbrevs[s_id]}{" (ASC)" if is_lagna else ""}</text>')

            if is_lagna:
                svg_parts.append(f'<line x1="{bx}" y1="{by}" x2="{bx + cell_w}" y2="{by + cell_h}" stroke="#DC2626" stroke-width="1.8" stroke-dasharray="4,2"/>')

            p_list = sign_planets[s_id]
            if p_list:
                for idx, (p_str, p_col) in enumerate(p_list):
                    py = by + 34 + idx * 16
                    svg_parts.append(f'<text x="{bx + cell_w//2}" y="{py}" text-anchor="middle" fill="{p_col}" font-size="11.5" font-weight="900">{p_str}</text>')

        svg_parts.append('</svg>')
        return "".join(svg_parts)

    @classmethod
    def render_east_indian_svg(cls, chart: KundaliChart, title: str = "East Indian (Surya) Kundali", varga_code: str = "D1") -> str:
        """
        Renders a classical East Indian (Bengali / Odia / Prachya Surya Chakra) kundali in SVG format.
        Layout is a 3x3 square structure where the 4 corner squares are split diagonally into two triangles each,
        yielding exactly 12 sign-fixed compartments (Mesha/Aries fixed at Top-Center, followed anticlockwise).
        """
        target_varga = chart.vargas.get(varga_code) if (chart.vargas and varga_code in chart.vargas) else None
        lagna_s_id = target_varga.lagna_sign_id if target_varga else chart.lagna_sign_id

        sign_planets: Dict[int, List[Tuple[str, str]]] = {s: [] for s in range(1, 13)}
        if target_varga:
            for p_name, vp in target_varga.planets.items():
                short_name = p_name[:2]
                if p_name in chart.planets and chart.planets[p_name].is_retrograde:
                    short_name += "(R)"
                color = cls.get_planet_color(short_name)
                sign_planets[vp.sign_id].append((short_name, color))
        else:
            for p_name, p in chart.planets.items():
                short_name = p_name[:2]
                if p.is_retrograde: short_name += "(R)"
                if p.is_combust: short_name += "*"
                color = cls.get_planet_color(short_name)
                sign_planets[p.sign_id].append((short_name, color))

        W, H = 420, 420
        # 3x3 outer box boundaries
        x0, y0 = 30, 45
        size = 360
        s3 = 120  # 360 / 3

        # Coordinates of 3x3 grid points
        x1, x2, x3 = x0 + s3, x0 + 2 * s3, x0 + size
        y1, y2, y3 = y0 + s3, y0 + 2 * s3, y0 + size

        # Standard East Indian 12 compartment polygons (Aries=1 Top-Center, anticlockwise)
        # 1. Mesha (Top-Center rectangle): (x1,y0) to (x2,y1)
        # 2. Vrishabha (Top-Left upper triangle): (x0,y0) -> (x1,y0) -> (x1,y1)
        # 3. Mithuna (Top-Left lower triangle): (x0,y0) -> (x0,y1) -> (x1,y1)
        # 4. Karka (Middle-Left rectangle): (x0,y1) to (x1,y2)
        # 5. Simha (Bottom-Left upper triangle): (x0,y1) -> (x1,y2) -> (x0,y2) ...
        # Standard diagonal partitioning:
        # TL corner (x0,y0 to x1,y1): diagonal from (x0,y0) to (x1,y1)
        # BL corner (x0,y2 to x1,y3): diagonal from (x0,y3) to (x1,y2)
        # BR corner (x2,y2 to x3,y3): diagonal from (x2,y2) to (x3,y3)
        # TR corner (x2,y0 to x3,y1): diagonal from (x2,y1) to (x3,y0)

        compartments = {
            1: {  # Mesha (Aries) - Top Center
                "poly": f"{x1},{y0} {x2},{y0} {x2},{y1} {x1},{y1}",
                "name": "Mesha (1)",
                "cx": (x1 + x2) // 2,
                "cy": y0 + 55,
                "lx": (x1 + x2) // 2,
                "ly": y0 + 22
            },
            2: {  # Vrishabha (Taurus) - Top-Left inner/upper triangle
                "poly": f"{x0},{y0} {x1},{y0} {x1},{y1}",
                "name": "Vrishabha (2)",
                "cx": x0 + 80,
                "cy": y0 + 60,
                "lx": x0 + 75,
                "ly": y0 + 25
            },
            3: {  # Mithuna (Gemini) - Top-Left outer/lower triangle
                "poly": f"{x0},{y0} {x1},{y1} {x0},{y1}",
                "name": "Mithuna (3)",
                "cx": x0 + 40,
                "cy": y0 + 80,
                "lx": x0 + 38,
                "ly": y0 + 45
            },
            4: {  # Karka (Cancer) - Mid Left
                "poly": f"{x0},{y1} {x1},{y1} {x1},{y2} {x0},{y2}",
                "name": "Karka (4)",
                "cx": (x0 + x1) // 2,
                "cy": y1 + 55,
                "lx": (x0 + x1) // 2,
                "ly": y1 + 22
            },
            5: {  # Simha (Leo) - Bottom-Left upper triangle
                "poly": f"{x0},{y1} {x1},{y2} {x0},{y3}",
                "name": "Simha (5)",
                "cx": x0 + 40,
                "cy": y2 + 40,
                "lx": x0 + 38,
                "ly": y2 + 15
            },
            6: {  # Kanya (Virgo) - Bottom-Left lower triangle
                "poly": f"{x0},{y3} {x1},{y2} {x1},{y3}",
                "name": "Kanya (6)",
                "cx": x0 + 80,
                "cy": y2 + 65,
                "lx": x0 + 75,
                "ly": y3 - 10
            },
            7: {  # Tula (Libra) - Bottom Center
                "poly": f"{x1},{y2} {x2},{y2} {x2},{y3} {x1},{y3}",
                "name": "Tula (7)",
                "cx": (x1 + x2) // 2,
                "cy": y2 + 55,
                "lx": (x1 + x2) // 2,
                "ly": y2 + 22
            },
            8: {  # Vrishchika (Scorpio) - Bottom-Right lower triangle
                "poly": f"{x2},{y3} {x2},{y2} {x3},{y3}",
                "name": "Vrishchika (8)",
                "cx": x2 + 40,
                "cy": y2 + 65,
                "lx": x2 + 45,
                "ly": y3 - 10
            },
            9: {  # Dhanu (Sagittarius) - Bottom-Right upper triangle
                "poly": f"{x2},{y2} {x3},{y2} {x3},{y3}",
                "name": "Dhanu (9)",
                "cx": x2 + 80,
                "cy": y2 + 40,
                "lx": x2 + 82,
                "ly": y2 + 15
            },
            10: {  # Makara (Capricorn) - Mid Right
                "poly": f"{x2},{y1} {x3},{y1} {x3},{y2} {x2},{y2}",
                "name": "Makara (10)",
                "cx": (x2 + x3) // 2,
                "cy": y1 + 55,
                "lx": (x2 + x3) // 2,
                "ly": y1 + 22
            },
            11: {  # Kumbha (Aquarius) - Top-Right lower triangle
                "poly": f"{x2},{y1} {x3},{y1} {x3},{y0}",
                "name": "Kumbha (11)",
                "cx": x2 + 80,
                "cy": y0 + 80,
                "lx": x2 + 82,
                "ly": y0 + 45
            },
            12: {  # Meena (Pisces) - Top-Right upper triangle
                "poly": f"{x2},{y0} {x3},{y0} {x2},{y1}",
                "name": "Meena (12)",
                "cx": x2 + 40,
                "cy": y0 + 60,
                "lx": x2 + 45,
                "ly": y0 + 25
            }
        }

        svg_parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="100%" height="380" style="background:#FFFFFF; border:2px solid #CBD5E1; border-radius:14px; box-shadow:0 4px 15px rgba(0,0,0,0.06); font-family: -apple-system, BlinkMacSystemFont, sans-serif;">',
            f'<text x="{W//2}" y="25" text-anchor="middle" fill="#78350F" font-size="14" font-weight="900">{title}</text>',
            # Center Square: Brand / Watermark
            f'<rect x="{x1}" y="{y1}" width="{s3}" height="{s3}" fill="#FFFBEB" stroke="#D97706" stroke-width="2"/>',
            f'<text x="{(x1+x2)//2}" y="{(y1+y2)//2 - 10}" text-anchor="middle" fill="#B45309" font-size="14" font-weight="900">सूर्य चक्र</text>',
            f'<text x="{(x1+x2)//2}" y="{(y1+y2)//2 + 8}" text-anchor="middle" fill="#1E293B" font-size="11.5" font-weight="800">पूर्व भारतीय (प्राच्य)</text>',
            f'<text x="{(x1+x2)//2}" y="{(y1+y2)//2 + 24}" text-anchor="middle" fill="#64748B" font-size="10" font-weight="700">Bengal / Odisha Style</text>'
        ]

        # Draw 12 Compartments
        for s_id in range(1, 13):
            comp = compartments[s_id]
            is_lagna = (s_id == lagna_s_id)
            bg_color = "#FEF3C7" if is_lagna else "#FFFFFF"
            poly_pts = comp["poly"]

            # Polygon cell
            svg_parts.append(f'<polygon points="{poly_pts}" fill="{bg_color}" stroke="#D97706" stroke-width="1.6"/>')

            # Sign Label (with Lagna Ascendant indicator)
            lbl_color = "#DC2626" if is_lagna else "#475569"
            lbl_text = comp["name"]
            if is_lagna:
                lbl_text += " [Lagna]"

            svg_parts.append(f'<text x="{comp["lx"]}" y="{comp["ly"]}" text-anchor="middle" fill="{lbl_color}" font-size="10" font-weight="800">{lbl_text}</text>')

            # Planets inside this sign
            p_list = sign_planets[s_id]
            if p_list:
                count = len(p_list)
                start_y = comp["cy"] - (count - 1) * 7
                for idx, (p_str, p_col) in enumerate(p_list):
                    py = start_y + idx * 14
                    svg_parts.append(
                        f'<text x="{comp["cx"]}" y="{py}" text-anchor="middle" fill="{p_col}" font-size="11.5" font-weight="900">{p_str}</text>'
                    )

        svg_parts.append('</svg>')
        return "".join(svg_parts)

    @classmethod
    def render_transit_biwheel_svg(
        cls,
        chart: KundaliChart,
        transit_positions: Optional[Dict[str, int]] = None,
        title: str = "जन्म एवं तात्कालिक गोचर ओवरले चक्र (Natal & Transit Bi-Wheel)"
    ) -> str:
        """
        Renders a Dual-Ring Bi-Wheel chart overlaying Natal planets (Inner)
        and Current Transiting planets (Outer Amber/Gold with '⚡') on the same North Indian diamond chart.
        """
        lagna_s_id = chart.lagna_sign_id

        # Natal planets by house
        natal_house_planets: Dict[int, List[str]] = {h: [] for h in range(1, 13)}
        for p_name, p in chart.planets.items():
            short = p_name[:2]
            if p.is_retrograde:
                short += "(R)"
            natal_house_planets[p.house_from_lagna].append(short)

        # Transit planets by house (sign_id 1..12)
        transit_house_planets: Dict[int, List[str]] = {h: [] for h in range(1, 13)}
        if transit_positions:
            for p_name, s_id in transit_positions.items():
                short = p_name[:2]
                h_num = ((s_id - lagna_s_id) % 12) + 1
                transit_house_planets[h_num].append(short)

        W, H = 460, 460
        house_polygons = {
            1: ("230,35 335,135 230,235 125,135", "#FFFBEB"),
            2: ("25,35 230,35 125,135", "#F8FAFC"),
            3: ("25,35 125,135 25,235", "#F8FAFC"),
            4: ("25,235 125,135 230,235 125,335", "#FFFBEB"),
            5: ("25,235 125,335 25,435", "#ECFDF5"),
            6: ("25,435 125,335 230,435", "#FEF2F2"),
            7: ("230,235 335,335 230,435 125,335", "#FFFBEB"),
            8: ("230,435 335,335 435,435", "#FEF2F2"),
            9: ("435,435 335,335 435,235", "#ECFDF5"),
            10: ("230,235 335,135 435,235 335,335", "#FFFBEB"),
            11: ("435,235 335,135 435,35", "#F8FAFC"),
            12: ("435,35 335,135 230,35", "#FEF2F2"),
        }

        house_coords = {
            1: (230, 130, 230, 75),
            2: (120, 75, 145, 55),
            3: (75, 120, 50, 145),
            4: (130, 230, 85, 230),
            5: (75, 335, 50, 315),
            6: (120, 395, 145, 415),
            7: (230, 335, 230, 395),
            8: (335, 395, 310, 415),
            9: (395, 335, 420, 315),
            10: (335, 230, 380, 230),
            11: (395, 120, 420, 145),
            12: (335, 75, 310, 55),
        }

        svg_parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="100%" height="420" style="background:#FFFFFF; border:2px solid #CBD5E1; border-radius:14px; box-shadow:0 4px 15px rgba(0,0,0,0.08); font-family: -apple-system, BlinkMacSystemFont, sans-serif;">',
            f'<text x="{W//2}" y="24" text-anchor="middle" fill="#78350F" font-size="14.5" font-weight="900">{title}</text>',
        ]

        for h_num, (poly_pts, bg_color) in house_polygons.items():
            svg_parts.append(f'<polygon points="{poly_pts}" fill="{bg_color}" stroke="none"/>')

        svg_parts.append(f'<rect x="25" y="35" width="410" height="400" fill="none" stroke="#D97706" stroke-width="2.5"/>')
        svg_parts.append(f'<line x1="25" y1="35" x2="435" y2="435" stroke="#D97706" stroke-width="1.8"/>')
        svg_parts.append(f'<line x1="435" y1="35" x2="25" y2="435" stroke="#D97706" stroke-width="1.8"/>')
        svg_parts.append(f'<polygon points="230,35 435,235 230,435 25,235" fill="none" stroke="#D97706" stroke-width="2"/>')

        for h in range(1, 13):
            s_id = ((lagna_s_id - 1 + (h - 1)) % 12) + 1
            cx, cy, lx, ly = house_coords[h]

            # Sign number
            s_color = "#DC2626" if h == 1 else "#64748B"
            s_weight = "900" if h == 1 else "800"
            svg_parts.append(f'<text x="{lx}" y="{ly}" text-anchor="middle" fill="{s_color}" font-size="11" font-weight="{s_weight}">{s_id}</text>')

            # Natal Planets (Blue / Purple)
            n_pls = natal_house_planets.get(h, [])
            # Transit Planets (Orange / Red with ⚡)
            t_pls = transit_house_planets.get(h, [])

            start_y = cy - ((len(n_pls) + len(t_pls) - 1) * 7)
            line_idx = 0
            for np_str in n_pls:
                py = start_y + line_idx * 13
                svg_parts.append(f'<text x="{cx}" y="{py}" text-anchor="middle" fill="#1E40AF" font-size="11" font-weight="900">{np_str}</text>')
                line_idx += 1

            for tp_str in t_pls:
                py = start_y + line_idx * 13
                svg_parts.append(f'<text x="{cx}" y="{py}" text-anchor="middle" fill="#D97706" font-size="10.5" font-weight="900">⚡{tp_str}</text>')
                line_idx += 1

        # Legend at bottom
        svg_parts.append(f'<rect x="35" y="438" width="390" height="18" fill="#F8FAFC" rx="4"/>')
        svg_parts.append(f'<text x="230" y="451" text-anchor="middle" fill="#475569" font-size="10" font-weight="800">🔵 जन्म ग्रह (Natal) | 🟠 ⚡ वर्तमान गोचर ग्रह (Real-time Transit)</text>')

        svg_parts.append('</svg>')
        return "".join(svg_parts)

    @classmethod
    def render_kota_chakra_svg(cls, kota_data: Dict[str, Any], title: str = "कोटा चक्र दुर्ग आरेख (Kota Chakra Durga Fortress)") -> str:
        """
        Renders a classical 4-tiered Durga Fortress SVG diagram with
        Stambha (Center Core), Madhya, Prakaara, and Bahya zones,
        indicating planet placements, Ingress/Egress, and siege evaluation.
        """
        W, H = 540, 520
        swami = kota_data.get("kota_swami", "Moon")
        pala = kota_data.get("kota_pala", "Mercury")
        status = kota_data.get("defense_status", "सामान्य स्थिति")
        allocations = kota_data.get("planet_allocations", [])
        stambha_malefics = kota_data.get("stambha_malefics", [])
        stambha_benefics = kota_data.get("stambha_benefics", [])

        # Stambha fill color depends on affliction
        if len(stambha_malefics) >= 2:
            stambha_fill = "#FEE2E2"
            stambha_stroke = "#DC2626"
        elif len(stambha_benefics) >= 1:
            stambha_fill = "#DCFCE7"
            stambha_stroke = "#16A34A"
        else:
            stambha_fill = "#FEF3C7"
            stambha_stroke = "#D97706"

        planets_by_zone = {"Stambha": [], "Madhya": [], "Prakaara": [], "Bahya": []}
        for item in allocations:
            z_str = item.get("zone", "")
            if "Stambha" in z_str or "स्तम्भ" in z_str:
                planets_by_zone["Stambha"].append(item)
            elif "Madhya" in z_str or "मध्य" in z_str:
                planets_by_zone["Madhya"].append(item)
            elif "Prakaara" in z_str or "प्राकार" in z_str:
                planets_by_zone["Prakaara"].append(item)
            else:
                planets_by_zone["Bahya"].append(item)

        svg = [
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="100%" height="480" style="background:#FFFFFF; border:2px solid #E2E8F0; border-radius:14px; box-shadow:0 4px 15px rgba(0,0,0,0.06); font-family: -apple-system, BlinkMacSystemFont, sans-serif;">',
            f'<rect x="0" y="0" width="{W}" height="40" fill="#1E1B4B" rx="12 12 0 0"/>',
            f'<text x="{W//2}" y="25" text-anchor="middle" fill="#F8FAFC" font-size="14.5" font-weight="900">🏰 {title}</text>',
            f'<rect x="20" y="48" width="{W-40}" height="28" fill="#F1F5F9" rx="6" stroke="#CBD5E1"/>',
            f'<text x="35" y="66" fill="#1E293B" font-size="12" font-weight="800">👑 कोटा स्वामी: <tspan fill="#D97706">{swami}</tspan> | 🛡️ कोटा पाल: <tspan fill="#2563EB">{pala}</tspan></text>',
            f'<text x="{W-35}" y="66" text-anchor="end" fill="#0F172A" font-size="11.5" font-weight="900">{status}</text>',
            f'<rect x="30" y="85" width="480" height="380" fill="#F8FAFC" stroke="#94A3B8" stroke-width="2" rx="10"/>',
            f'<text x="45" y="105" fill="#64748B" font-size="11" font-weight="800">🌾 बाह्य क्षेत्र (Bahya - Outer Grounds)</text>',
            f'<rect x="80" y="130" width="380" height="290" fill="#FFFBEB" stroke="#F59E0B" stroke-width="2.5" stroke-dasharray="6,4" rx="8"/>',
            f'<text x="95" y="150" fill="#B45309" font-size="11" font-weight="800">🧱 प्राकार (Prakaara - Fort Walls)</text>',
            f'<rect x="135" y="175" width="270" height="200" fill="#EFF6FF" stroke="#3B82F6" stroke-width="2" rx="8"/>',
            f'<text x="150" y="195" fill="#1D4ED8" font-size="11" font-weight="800">🏛️ मध्य (Madhya - Inner Court)</text>',
            f'<rect x="195" y="220" width="150" height="110" fill="{stambha_fill}" stroke="{stambha_stroke}" stroke-width="3" rx="8"/>',
            f'<text x="270" y="242" text-anchor="middle" fill="#1E293B" font-size="12" font-weight="900">⚡ स्तम्भ (Stambha)</text>',
        ]

        s_pls = planets_by_zone["Stambha"]
        for idx, pl in enumerate(s_pls):
            p_name = pl["planet"]
            p_color = "#DC2626" if pl["nature"] == "Malefic" else "#15803D"
            m_arrow = "➡️" if "प्रवेश" in pl["motion"] else "⬅️"
            py = 265 + (idx * 20)
            svg.append(f'<text x="270" y="{py}" text-anchor="middle" fill="{p_color}" font-size="12" font-weight="900">{m_arrow} {p_name} ({pl["nakshatra"][:4]})</text>')

        m_pls = planets_by_zone["Madhya"]
        for idx, pl in enumerate(m_pls):
            p_name = pl["planet"]
            p_color = "#DC2626" if pl["nature"] == "Malefic" else "#1D4ED8"
            m_arrow = "➡️" if "प्रवेश" in pl["motion"] else "⬅️"
            px = 150 + ((idx % 2) * 140)
            py = 345 + ((idx // 2) * 18)
            svg.append(f'<text x="{px}" y="{py}" fill="{p_color}" font-size="11" font-weight="800">{m_arrow} {p_name}</text>')

        p_pls = planets_by_zone["Prakaara"]
        for idx, pl in enumerate(p_pls):
            p_name = pl["planet"]
            p_color = "#DC2626" if pl["nature"] == "Malefic" else "#0D9488"
            m_arrow = "➡️" if "प्रवेश" in pl["motion"] else "⬅️"
            px = 95 + ((idx % 4) * 85)
            py = 405
            svg.append(f'<text x="{px}" y="{py}" fill="{p_color}" font-size="10.5" font-weight="800">{m_arrow} {p_name}</text>')

        b_pls = planets_by_zone["Bahya"]
        for idx, pl in enumerate(b_pls):
            p_name = pl["planet"]
            p_color = "#DC2626" if pl["nature"] == "Malefic" else "#059669"
            m_arrow = "➡️" if "प्रवेश" in pl["motion"] else "⬅️"
            px = 45 + ((idx % 6) * 75)
            py = 452
            svg.append(f'<text x="{px}" y="{py}" fill="{p_color}" font-size="10" font-weight="700">{m_arrow} {p_name}</text>')

        svg.append(f'<rect x="20" y="475" width="{W-40}" height="32" fill="#F8FAFC" rx="6" stroke="#E2E8F0"/>')
        svg.append(f'<text x="{W//2}" y="495" text-anchor="middle" fill="#475569" font-size="11" font-weight="800">🟢 शुभ ग्रह (Defense) | 🔴 पाप ग्रह (Attacker) | ➡️ प्रवेश (Entering/Siege) | ⬅️ निर्गम (Exiting/Relief)</text>')
        svg.append('</svg>')
        return "".join(svg)

    @classmethod
    def render_kalapurusha_anatomy_svg(
        cls,
        health_data: Dict[str, Any],
        title: str = "कालपुरुष देह वेध आरेख (Kalapurusha Anatomical Health Map)"
    ) -> str:
        """
        Renders an interactive-style SVG diagram of the 12 anatomical organ zones
        color-coded by affliction and vitality status.
        """
        W, H = 640, 560
        organ_zones = health_data.get("organ_zones", [])
        vitality = health_data.get("vitality_score", 85)
        tridosha = health_data.get("tridosha", {})

        v_color = "#16A34A" if vitality >= 75 else ("#D97706" if vitality >= 50 else "#DC2626")

        svg = [
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="100%" height="520" style="background:#FFFFFF; border:2px solid #E2E8F0; border-radius:14px; box-shadow:0 4px 15px rgba(0,0,0,0.06); font-family: -apple-system, BlinkMacSystemFont, sans-serif;">',
            f'<rect x="0" y="0" width="{W}" height="42" fill="#0F172A" rx="12 12 0 0"/>',
            f'<text x="{W//2}" y="26" text-anchor="middle" fill="#F8FAFC" font-size="15" font-weight="900">🩺 {title}</text>',
            f'<rect x="18" y="50" width="{W-36}" height="32" fill="#F8FAFC" rx="6" stroke="#CBD5E1"/>',
            f'<text x="32" y="71" fill="#1E293B" font-size="12.5" font-weight="800">💪 आरोग्य बल (Vitality): <tspan fill="{v_color}" font-weight="900">{vitality}/100</tspan> | 🌿 त्रिदोष: <tspan fill="#2563EB">{tridosha.get("dominant", "संतुलित")}</tspan></text>',
        ]

        # 2 Columns of 6 organ cards each
        # Left col: Houses 1 to 6 (Head to Digestion)
        # Right col: Houses 7 to 12 (Pelvis to Feet)
        col_w = (W - 54) // 2
        card_h = 66
        start_y = 92

        for idx, org in enumerate(organ_zones):
            h_num = org["house"]
            col_idx = 0 if h_num <= 6 else 1
            row_idx = (h_num - 1) if col_idx == 0 else (h_num - 7)

            cx = 18 if col_idx == 0 else (18 + col_w + 18)
            cy = start_y + (row_idx * (card_h + 8))

            score = org["affliction_score"]
            if score >= 60:
                bg = "#FEF2F2"
                stroke = "#DC2626"
                badge_bg = "#FEE2E2"
                badge_fg = "#991B1B"
                badge_txt = f"🔴 {score}% पीड़ित"
            elif score >= 35:
                bg = "#FFFBEB"
                stroke = "#D97706"
                badge_bg = "#FEF3C7"
                badge_fg = "#92400E"
                badge_txt = f"🟡 {score}% सतर्क"
            else:
                bg = "#F0FDF4"
                stroke = "#16A34A"
                badge_bg = "#DCFCE7"
                badge_fg = "#166534"
                badge_txt = f"🟢 {score}% बलिष्ठ"

            svg.append(f'<g transform="translate({cx}, {cy})">')
            svg.append(f'<rect width="{col_w}" height="{card_h}" fill="{bg}" stroke="{stroke}" stroke-width="1.8" rx="8"/>')
            svg.append(f'<rect width="6" height="{card_h}" fill="{stroke}" rx="8 0 0 8"/>')
            # Header
            svg.append(f'<text x="14" y="20" fill="#0F172A" font-size="12" font-weight="900">भाव {h_num}: {org["organ_hi"].split("(")[0].strip()}</text>')
            svg.append(f'<rect x="{col_w-85}" y="8" width="75" height="18" fill="{badge_bg}" rx="4"/>')
            svg.append(f'<text x="{col_w-48}" y="21" text-anchor="middle" fill="{badge_fg}" font-size="10" font-weight="800">{badge_txt}</text>')
            # Issues
            issues_trunc = org["potential_issues"][:42] + ("..." if len(org["potential_issues"]) > 42 else "")
            svg.append(f'<text x="14" y="38" fill="#475569" font-size="10.5" font-weight="600">⚠️ {issues_trunc}</text>')
            # Reasons
            reasons_trunc = ", ".join(org["reasons"])[:38] + ("..." if len(", ".join(org["reasons"])) > 38 else "")
            svg.append(f'<text x="14" y="54" fill="#64748B" font-size="9.5" font-weight="500">🔍 {reasons_trunc}</text>')
            svg.append('</g>')

        # Footer Legend
        svg.append(f'<rect x="18" y="525" width="{W-36}" height="26" fill="#F8FAFC" rx="6" stroke="#E2E8F0"/>')
        svg.append(f'<text x="{W//2}" y="542" text-anchor="middle" fill="#475569" font-size="10.5" font-weight="800">🟢 0-34% बलिष्ठ एवं स्वस्थ | 🟡 35-59% सामान्य संवेदनशील | 🔴 60-100% विशेष ध्यान योग्य व पीड़ित अंग</text>')
        svg.append('</svg>')
        return "".join(svg)

    @classmethod
    def render_astrallis_circular_svg(
        cls,
        chart: "KundaliChart",
        title: str = "Natal Chart",
        varga_code: str = "D1",
        dark_bg: bool = True,
    ) -> str:
        """
        Renders an Astrallis Scientific Observatory-style circular Western zodiac wheel with:
        - Deep black background (#050811)
        - Outer zodiac sign ring with neon sign glyphs & degree ticks
        - House cusp radial spokes
        - Neon-coloured aspect lines: Trine=green, Square=red, Sextile=cyan,
          Opposition=magenta, Conjunction=yellow-dashed
        - Planet glyphs with neon colours & degree labels
        - Lagna/Asc marker
        """
        import math

        target_varga = chart.vargas.get(varga_code) if (chart.vargas and varga_code in chart.vargas) else None
        lagna_s_id = target_varga.lagna_sign_id if target_varga else chart.lagna_sign_id

        bg_color = "#050811" if dark_bg else "#FFFFFF"
        ring_stroke = "#1E3A5F" if dark_bg else "#D97706"
        text_color = "#E2E8F0" if dark_bg else "#0F172A"
        tick_color = "#2D4A6A" if dark_bg else "#94A3B8"
        sign_ring_bg = "#0A1628" if dark_bg else "#FEF3C7"
        house_line_color = "#1E3A5F" if dark_bg else "#D97706"

        SIGN_GLYPHS  = ["♈","♉","♊","♋","♌","♍","♎","♏","♐","♑","♒","♓"]
        SIGN_NEON = [
            "#FF4444","#88CC22","#44DDFF","#4488FF",
            "#FFB800","#44CC88","#FF88CC","#FF5555",
            "#BB8833","#88AACC","#44AAFF","#6688BB"
        ]
        PLANET_NEON = {
            "Sun":     ("Su", "#FFB800"),
            "Moon":    ("Mo", "#88AAFF"),
            "Mars":    ("Ma", "#FF4444"),
            "Mercury": ("Me", "#44DD88"),
            "Jupiter": ("Ju", "#FFD700"),
            "Venus":   ("Ve", "#FF88CC"),
            "Saturn":  ("Sa", "#AAAACC"),
            "Rahu":    ("Ra", "#CC88FF"),
            "Ketu":    ("Ke", "#AA6633"),
        }

        W, H = 560, 560
        cx_c, cy_c = W // 2, H // 2
        R_outer     = 252
        R_sign_out  = 252
        R_sign_in   = 210
        R_house_out = 210
        R_house_in  = 40
        R_planet    = 170
        R_asp       = 150

        def lon2rad(lon_deg: float) -> float:
            lagna_lon = (lagna_s_id - 1) * 30.0
            rotated = lon_deg - lagna_lon + 180.0
            return math.radians(-rotated)

        def polar(r: float, a: float):
            return (cx_c + r * math.cos(a), cy_c + r * math.sin(a))

        p = []
        p.append(
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
            f'width="100%" style="background:{bg_color};border-radius:12px;">'
        )
        p.append('<defs>')
        p.append('<radialGradient id="bg2" cx="50%" cy="50%" r="50%">'
                 f'<stop offset="0%" stop-color="#0A1628"/>'
                 f'<stop offset="100%" stop-color="{bg_color}"/></radialGradient>')
        p.append('<filter id="gl"><feGaussianBlur stdDeviation="2.5" result="b"/>'
                 '<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>')
        p.append('<filter id="gl2"><feGaussianBlur stdDeviation="1.2" result="b"/>'
                 '<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>')
        p.append('</defs>')

        p.append(f'<circle cx="{cx_c}" cy="{cy_c}" r="{R_outer}" fill="url(#bg2)"/>')
        p.append(f'<circle cx="{cx_c}" cy="{cy_c}" r="{R_outer}" fill="none" stroke="#00E5FF" stroke-width="1.5" opacity="0.5"/>')

        # Sign ring
        p.append(f'<circle cx="{cx_c}" cy="{cy_c}" r="{R_sign_out}" fill="none" stroke="{ring_stroke}" stroke-width="1"/>')
        p.append(f'<circle cx="{cx_c}" cy="{cy_c}" r="{R_sign_in}" fill="none" stroke="{ring_stroke}" stroke-width="1"/>')

        for i, (glyph, scol) in enumerate(zip(SIGN_GLYPHS, SIGN_NEON)):
            mid_lon = i * 30.0 + 15.0
            a = lon2rad(mid_lon)
            R_mid = (R_sign_out + R_sign_in) / 2
            sx, sy = polar(R_mid, a)
            p.append(f'<text x="{sx:.1f}" y="{sy:.1f}" text-anchor="middle" dominant-baseline="central" fill="{scol}" font-size="15" font-weight="900" filter="url(#gl2)">{glyph}</text>')

            bnd_a = lon2rad(i * 30.0)
            b1 = polar(R_sign_in, bnd_a); b2 = polar(R_sign_out, bnd_a)
            p.append(f'<line x1="{b1[0]:.1f}" y1="{b1[1]:.1f}" x2="{b2[0]:.1f}" y2="{b2[1]:.1f}" stroke="{ring_stroke}" stroke-width="1.2"/>')

        # Degree ticks
        for deg in range(0, 360, 5):
            a = lon2rad(float(deg))
            tl = 8 if deg % 30 == 0 else (5 if deg % 10 == 0 else 3)
            t1 = polar(R_sign_out - tl, a); t2 = polar(R_sign_out, a)
            p.append(f'<line x1="{t1[0]:.1f}" y1="{t1[1]:.1f}" x2="{t2[0]:.1f}" y2="{t2[1]:.1f}" stroke="{tick_color}" stroke-width="0.7"/>')

        # House cusp lines
        p.append(f'<circle cx="{cx_c}" cy="{cy_c}" r="{R_house_out}" fill="none" stroke="{ring_stroke}" stroke-width="0.7" stroke-dasharray="3,3"/>')
        ROMAN = ["I","II","III","IV","V","VI","VII","VIII","IX","X","XI","XII"]
        for h in range(1, 13):
            h_lon = (lagna_s_id - 1) * 30.0 + (h - 1) * 30.0
            a = lon2rad(h_lon)
            lp1 = polar(R_house_in, a); lp2 = polar(R_house_out, a)
            lw = "1.8" if h in [1,4,7,10] else "0.7"
            lc = "#00E5FF" if h == 1 else ("#4488FF" if h in [4,7,10] else house_line_color)
            p.append(f'<line x1="{lp1[0]:.1f}" y1="{lp1[1]:.1f}" x2="{lp2[0]:.1f}" y2="{lp2[1]:.1f}" stroke="{lc}" stroke-width="{lw}"/>')
            # House label
            mid_lon_h = (lagna_s_id - 1) * 30.0 + (h - 1) * 30.0 + 15.0
            am = lon2rad(mid_lon_h)
            R_hl = (R_house_out + R_sign_in) / 2 - 4
            hlx, hly = polar(R_hl, am)
            hcol = "#00E5FF" if h in [1,4,7,10] else "#3A5A7A"
            p.append(f'<text x="{hlx:.1f}" y="{hly:.1f}" text-anchor="middle" dominant-baseline="central" fill="{hcol}" font-size="9" font-weight="800">{ROMAN[h-1]}</text>')

        # Hub
        p.append(f'<circle cx="{cx_c}" cy="{cy_c}" r="{R_house_in}" fill="{sign_ring_bg}" stroke="#00E5FF" stroke-width="1.2"/>')
        p.append(f'<text x="{cx_c}" y="{cy_c-5}" text-anchor="middle" fill="#00E5FF" font-size="8" font-weight="900">Asc</text>')
        p.append(f'<text x="{cx_c}" y="{cy_c+8}" text-anchor="middle" fill="#4A6080" font-size="7">Lagna</text>')

        # Aspect lines
        ASP_DEFS = [
            (0,   10, "#FFD700", "6,3",   "1.8"),
            (60,  6,  "#00E5FF", "none",  "1.4"),
            (90,  8,  "#FF4444", "none",  "1.8"),
            (120, 8,  "#44FF88", "none",  "1.8"),
            (150, 3,  "#666688", "4,3",   "0.9"),
            (180, 8,  "#FF44FF", "none",  "1.8"),
        ]
        planet_lons_list: list = []
        for pn in ["Sun","Moon","Mars","Mercury","Jupiter","Venus","Saturn","Rahu","Ketu"]:
            pp_obj = chart.planets.get(pn)
            if pp_obj:
                planet_lons_list.append((pn, float(pp_obj.longitude)))

        for i, (pn1, lon1) in enumerate(planet_lons_list):
            for j, (pn2, lon2) in enumerate(planet_lons_list):
                if j <= i:
                    continue
                diff = abs(lon1 - lon2)
                if diff > 180:
                    diff = 360 - diff
                for asp_d, orb, ac, dash, lw in ASP_DEFS:
                    if abs(diff - asp_d) <= orb:
                        a1 = lon2rad(lon1); a2 = lon2rad(lon2)
                        ax1, ay1 = polar(R_asp, a1)
                        ax2, ay2 = polar(R_asp, a2)
                        sd = f' stroke-dasharray="{dash}"' if dash != "none" else ""
                        p.append(f'<line x1="{ax1:.1f}" y1="{ay1:.1f}" x2="{ax2:.1f}" y2="{ay2:.1f}" stroke="{ac}" stroke-width="{lw}" opacity="0.82"{sd}/>')
                        break

        # Planets
        # Spread planets in same sign by slight angular offset
        sign_counts: dict = {}
        for pn, lon in planet_lons_list:
            s_idx = int(lon // 30)
            sign_counts[s_idx] = sign_counts.get(s_idx, 0) + 1
        sign_offset_idx: dict = {}
        for pn, lon in planet_lons_list:
            s_idx = int(lon // 30)
            oi = sign_offset_idx.get(s_idx, 0)
            sign_offset_idx[s_idx] = oi + 1
            total = sign_counts[s_idx]
            spread = (oi - (total - 1) / 2.0) * 4.0  # 4° per planet in same sign
            p_lon_adj = lon + spread
            a = lon2rad(p_lon_adj)
            px, py = polar(R_planet, a)
            gl_txt, nc = PLANET_NEON.get(pn, (pn[:2], "#CCCCCC"))
            pp_obj = chart.planets.get(pn)
            lbl = gl_txt
            if pp_obj and pp_obj.is_retrograde:
                lbl += "℞"
            # Dot
            p.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="3.5" fill="{nc}" filter="url(#gl)"/>')
            # Name
            p.append(f'<text x="{px:.1f}" y="{py-9:.1f}" text-anchor="middle" fill="{nc}" font-size="10" font-weight="900" filter="url(#gl2)">{lbl}</text>')
            # Degree
            deg_str = f"{(lon % 30.0):.1f}°"
            p.append(f'<text x="{px:.1f}" y="{py+14:.1f}" text-anchor="middle" fill="{nc}" font-size="7.5" opacity="0.8">{deg_str}</text>')
            # Spoke
            sp = polar(R_house_in + 6, a)
            p.append(f'<line x1="{px:.1f}" y1="{py:.1f}" x2="{sp[0]:.1f}" y2="{sp[1]:.1f}" stroke="{nc}" stroke-width="0.5" opacity="0.35"/>')

        # Asc / Dsc labels on outer ring
        asc_a = lon2rad((lagna_s_id - 1) * 30.0)
        asc_lx, asc_ly = polar(R_sign_in - 8, asc_a)
        p.append(f'<text x="{asc_lx:.1f}" y="{asc_ly:.1f}" text-anchor="middle" dominant-baseline="central" fill="#00E5FF" font-size="11" font-weight="900" filter="url(#gl)">Asc</text>')
        dsc_a = lon2rad((lagna_s_id - 1) * 30.0 + 180.0)
        dsc_lx, dsc_ly = polar(R_sign_in - 8, dsc_a)
        p.append(f'<text x="{dsc_lx:.1f}" y="{dsc_ly:.1f}" text-anchor="middle" dominant-baseline="central" fill="#4488FF" font-size="11" font-weight="900">Dsc</text>')

        # Title
        p.append(f'<text x="{cx_c}" y="16" text-anchor="middle" fill="#00E5FF" font-size="12" font-weight="900">{title}</text>')

        # Aspect legend
        legend = [("━","#FFD700","Conj"),("━","#44FF88","Trine"),("━","#FF4444","Sqr"),("━","#00E5FF","Sex"),("━","#FF44FF","Opp")]
        ly_pos = H - 6
        p.append(f'<text x="{cx_c}" y="{ly_pos}" text-anchor="middle" fill="#3A5A7A" font-size="8">')
        for sym, lc, ln in legend:
            p.append(f'<tspan fill="{lc}"> {sym} {ln} </tspan>')
        p.append('</text>')
        p.append('</svg>')
        return "".join(p)


def render_aspect_orb_matrix_html(chart: "KundaliChart", dark_bg: bool = True) -> str:
    """
    Renders an Astrallis-style 9x9 aspect orb matrix as an HTML table.
    Color-coded: Conjunction=gold, Trine=green, Square=red, Sextile=cyan,
    Opposition=magenta, Quincunx=grey, blank=dot.
    """
    PLANETS = ["Sun","Moon","Mars","Mercury","Jupiter","Venus","Saturn","Rahu","Ketu"]
    SYMS = {"Sun":"☉","Moon":"☽","Mars":"♂","Mercury":"☿","Jupiter":"♃",
             "Venus":"♀","Saturn":"♄","Rahu":"☊","Ketu":"☋"}
    P_COLS = {"Sun":"#FFB800","Moon":"#88AAFF","Mars":"#FF4444",
              "Mercury":"#44DD88","Jupiter":"#FFD700","Venus":"#FF88CC",
              "Saturn":"#AAAACC","Rahu":"#CC88FF","Ketu":"#AA6633"}
    ASPECTS = [
        (0,   10, "#FFD700", "☌"),
        (60,  6,  "#00E5FF", "✶"),
        (90,  8,  "#FF4444", "□"),
        (120, 8,  "#44FF88", "△"),
        (150, 3,  "#888888", "⚻"),
        (180, 8,  "#FF44FF", "☍"),
    ]
    lons: dict = {}
    for pn in PLANETS:
        pp = chart.planets.get(pn)
        if pp:
            lons[pn] = float(pp.longitude)

    bg       = "#050811" if dark_bg else "#FFFFFF"
    hdr_bg   = "#0A1628" if dark_bg else "#F1F5F9"
    cell_bg  = "#070D1A" if dark_bg else "#FFFFFF"
    bdr      = "#1E3A5F" if dark_bg else "#D97706"

    rows = [f'<div style="overflow-x:auto;background:{bg};border-radius:8px;padding:4px;">',
            f'<table style="border-collapse:collapse;font-size:11px;width:100%;background:{bg};">',
            f'<tr><th style="background:{hdr_bg};color:#00E5FF;padding:3px 5px;border:1px solid {bdr};font-size:10px;">P/O</th>']
    for pn in PLANETS:
        sym = SYMS.get(pn, pn[:2])
        pc = P_COLS.get(pn, "#CCC")
        rows.append(f'<th style="background:{hdr_bg};color:{pc};padding:3px 4px;border:1px solid {bdr};font-size:11px;font-weight:900;">{sym}</th>')
    rows.append('</tr>')

    for pn1 in PLANETS:
        pc1 = P_COLS.get(pn1, "#CCC")
        sym1 = SYMS.get(pn1, pn1[:2])
        rows.append(f'<tr><td style="background:{hdr_bg};color:{pc1};padding:3px 4px;border:1px solid {bdr};font-weight:900;font-size:11px;">{sym1}</td>')
        for pn2 in PLANETS:
            if pn1 == pn2:
                rows.append(f'<td style="background:#0D1A2E;border:1px solid {bdr};text-align:center;color:#1E3A5F;font-size:12px;">■</td>')
                continue
            if pn1 not in lons or pn2 not in lons:
                rows.append(f'<td style="background:{cell_bg};border:1px solid {bdr};text-align:center;"></td>')
                continue
            diff = abs(lons[pn1] - lons[pn2])
            if diff > 180:
                diff = 360 - diff
            matched = False
            for asp_deg, orb, ac, sym in ASPECTS:
                if abs(diff - asp_deg) <= orb:
                    orb_v = round(abs(diff - asp_deg), 1)
                    rows.append(
                        f'<td style="background:{ac}22;border:1px solid {bdr};text-align:center;'
                        f'color:{ac};font-weight:900;font-size:13px;" title="{pn1}-{pn2}:{int(asp_deg)}°({orb_v}° orb)">{sym}</td>'
                    )
                    matched = True
                    break
            if not matched:
                rows.append(f'<td style="background:{cell_bg};border:1px solid {bdr};text-align:center;color:#1E3A5F;font-size:10px;">·</td>')
        rows.append('</tr>')
    rows.append('</table></div>')
    return "".join(rows)
