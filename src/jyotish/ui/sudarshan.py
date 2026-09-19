"""
Sudarshan Chakra Engine and Visual Renderer for JyotishOS.
According to Brihat Parashara Hora Shastra (BPHS).
Unites:
1. Lagna Kundali (Physical Body & Ascendant).
2. Chandra Kundali (Mind & Psychological Plane).
3. Surya Kundali (Soul, Vitality & Divine Plane).
Generates multi-tiered consolidated house evaluation and interactive 3-ring visual SVG/HTML chart.
"""

from typing import Dict, List, Tuple, Optional, Any
from src.jyotish.core.constants import SIGN_NAMES
from src.jyotish.core.models import KundaliChart


class SudarshanChakraEngine:
    """Calculates 3-ring Sudarshan Chakra analysis and SVG visualization."""

    @classmethod
    def calculate(cls, chart: KundaliChart) -> Dict[str, Any]:
        """Calculates 12 houses through Lagna, Chandra, and Surya frames."""
        lagna_sign_id = chart.lagna_sign_id
        moon_sign_id = chart.planets["Moon"].sign_id
        sun_sign_id = chart.planets["Sun"].sign_id

        benefics = {"Jupiter", "Venus", "Mercury", "Moon"}
        malefics = {"Saturn", "Mars", "Rahu", "Ketu", "Sun"}

        house_analyses = []

        house_names_hi = [
            "प्रथम भाव (तनु / व्यक्तित्व)",
            "द्वितीय भाव (धन / कुटुंब)",
            "तृतीय भाव (पराक्रम / सहोदर)",
            "चतुर्थ भाव (सुख / मातृ / भूमि)",
            "पंचम भाव (संतान / बुद्धि / मंत्र)",
            "षष्ठ भाव (रोग / ऋण / शत्रु)",
            "सप्तम भाव (विवाह / साझेदारी)",
            "अष्टम भाव (आयु / गूढ़ ज्ञान)",
            "नवम भाव (भाग्य / धर्म / गुरु)",
            "दशम भाव (कर्म / राज्य / पद)",
            "एकादश भाव (लाभ / आय / सिद्धि)",
            "द्वादश भाव (व्यय / मोक्ष / विदेश)"
        ]

        for h in range(1, 13):
            # 1. Sign from Lagna
            l_sign_id = ((lagna_sign_id - 1 + (h - 1)) % 12) + 1
            l_sign = SIGN_NAMES[l_sign_id - 1]
            l_planets = [p_name for p_name, p_pos in chart.planets.items() if p_pos.sign_id == l_sign_id]

            # 2. Sign from Moon
            m_sign_id = ((moon_sign_id - 1 + (h - 1)) % 12) + 1
            m_sign = SIGN_NAMES[m_sign_id - 1]
            m_planets = [p_name for p_name, p_pos in chart.planets.items() if p_pos.sign_id == m_sign_id]

            # 3. Sign from Sun
            s_sign_id = ((sun_sign_id - 1 + (h - 1)) % 12) + 1
            s_sign = SIGN_NAMES[s_sign_id - 1]
            s_planets = [p_name for p_name, p_pos in chart.planets.items() if p_pos.sign_id == s_sign_id]

            # Consolidated score
            all_occupants = l_planets + m_planets + s_planets
            ben_count = sum(1 for p in all_occupants if p in benefics)
            mal_count = sum(1 for p in all_occupants if p in malefics)

            score = 65 + (ben_count * 12) - (mal_count * 8)
            score = max(35, min(98, score))

            status = "🌟 परम शुभ" if score >= 80 else ("✅ अनुकूल" if score >= 60 else "⚠️ संघर्षपूर्ण")

            house_analyses.append({
                "house_num": h,
                "house_name": house_names_hi[h - 1],
                "lagna_ring": f"{l_sign} ({', '.join(l_planets) if l_planets else '—'})",
                "chandra_ring": f"{m_sign} ({', '.join(m_planets) if m_planets else '—'})",
                "surya_ring": f"{s_sign} ({', '.join(s_planets) if s_planets else '—'})",
                "score": f"{score}/100",
                "status": status
            })

        return {
            "lagna_sign": SIGN_NAMES[lagna_sign_id - 1],
            "chandra_sign": SIGN_NAMES[moon_sign_id - 1],
            "surya_sign": SIGN_NAMES[sun_sign_id - 1],
            "houses": house_analyses
        }

    @classmethod
    def render_sudarshan_svg(cls, chart: KundaliChart) -> str:
        """Generates clean, responsive SVG of 3-ring Sudarshan Chakra."""
        res = cls.calculate(chart)

        svg = """
        <svg viewBox="0 0 700 700" width="100%" height="520" xmlns="http://www.w3.org/2000/svg" style="background:#FFFFFF; font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;">
            <!-- Outer Ring (Surya Kundali) -->
            <circle cx="350" cy="350" r="320" fill="#FFFBEB" stroke="#D97706" stroke-width="3.5" />
            <!-- Middle Ring (Chandra Kundali) -->
            <circle cx="350" cy="350" r="230" fill="#EFF6FF" stroke="#2563EB" stroke-width="3" />
            <!-- Inner Ring (Lagna Kundali) -->
            <circle cx="350" cy="350" r="140" fill="#ECFDF5" stroke="#10B981" stroke-width="3" />
            <!-- Central Bindu -->
            <circle cx="350" cy="350" r="50" fill="#FFFFFF" stroke="#0F172A" stroke-width="2.5" />
            <text x="350" y="345" text-anchor="middle" font-size="16" font-weight="900" fill="#0F172A">सुदर्शन</text>
            <text x="350" y="365" text-anchor="middle" font-size="12" font-weight="700" fill="#64748B">चक्र</text>
        """

        import math
        # 12 Sector Dividing Lines
        for i in range(12):
            angle = i * (360.0 / 12.0) - 90.0
            rad = math.radians(angle)
            x1 = 350 + 50 * math.cos(rad)
            y1 = 350 + 50 * math.sin(rad)
            x2 = 350 + 320 * math.cos(rad)
            y2 = 350 + 320 * math.sin(rad)
            svg += f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="#94A3B8" stroke-width="1.5" stroke-dasharray="3,3" />'

            # Sector Mid-angle for Labels
            mid_angle = angle + 15.0
            mid_rad = math.radians(mid_angle)

            # Ring 1 (Lagna - radius 95)
            rx1 = 350 + 95 * math.cos(mid_rad)
            ry1 = 350 + 95 * math.sin(mid_rad)
            l_info = res["houses"][i]["lagna_ring"].split('(')[0].strip()[:3]
            svg += f'<text x="{rx1:.1f}" y="{ry1:.1f}" text-anchor="middle" dominant-baseline="central" font-size="12" font-weight="800" fill="#065F46">L:{l_info}</text>'

            # Ring 2 (Chandra - radius 185)
            rx2 = 350 + 185 * math.cos(mid_rad)
            ry2 = 350 + 185 * math.sin(mid_rad)
            c_info = res["houses"][i]["chandra_ring"].split('(')[0].strip()[:3]
            svg += f'<text x="{rx2:.1f}" y="{ry2:.1f}" text-anchor="middle" dominant-baseline="central" font-size="12" font-weight="800" fill="#1E40AF">M:{c_info}</text>'

            # Ring 3 (Surya - radius 275)
            rx3 = 350 + 275 * math.cos(mid_rad)
            ry3 = 350 + 275 * math.sin(mid_rad)
            s_info = res["houses"][i]["surya_ring"].split('(')[0].strip()[:3]
            svg += f'<text x="{rx3:.1f}" y="{ry3:.1f}" text-anchor="middle" dominant-baseline="central" font-size="12" font-weight="800" fill="#92400E">S:{s_info}</text>'

        svg += "</svg>"
        return svg


default_sudarshan_engine = SudarshanChakraEngine()

