"""
Kundali Chart SVG Renderer for JyotishOS.
Generates authentic, high-contrast, vector-rendered North Indian Diamond,
South Indian Box, and East Indian Surya charts with classical high-contrast color grading.
"""

from typing import Dict, List, Tuple
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
        """Renders East Indian (Bengali/Odia style) Kundali."""
        return cls.render_south_indian_svg(chart, title=f"East Indian (Prachya) - {title}", varga_code=varga_code)
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
