"""
हस्तरेखा विज़ुअलाइज़र (Interactive High-Definition SVG Palm Renderer)
Professional, anatomically proportional palm diagrams with non-colliding labels,
canonical planetary mounts, natural curvature lines, age markers, and sacred signs.
"""

from typing import Dict, Any, Optional
from src.jyotish.core.palmistry import PalmInputProfile


class PalmRenderer:
    """
    Renders scalable, crisp, responsive SVG palm diagrams for Vedic Hastarekha.
    Zero-collision typography, graceful organic line curves, and authentic anatomy.
    """

    @classmethod
    def render_palm_svg(
        cls,
        profile: PalmInputProfile,
        width: int = 580,
        height: int = 740,
        is_right_hand: Optional[bool] = None
    ) -> str:
        """
        Generates full-detail SVG markup representing the native's palm.
        """
        if is_right_hand is None:
            is_right_hand = (getattr(profile, "hand_side", "Right") != "Left")

        # Sacred marks visibility
        show_yava = getattr(profile, "has_buddha_eye", True)
        show_cross = getattr(profile, "has_mystic_cross", True)
        show_matsya = getattr(profile, "has_matsya_sign", True)
        show_trishul = getattr(profile, "has_trishul_sign", False)

        hand_label = "दायां हाथ (Right Palm)" if is_right_hand else "बायां हाथ (Left Palm)"

        # Safe attribute extraction
        jup_prom = getattr(profile.mount_jupiter, "prominence", "Prominent")
        sat_prom = getattr(profile.mount_saturn, "prominence", "Normal")
        sun_prom = getattr(profile.mount_sun, "prominence", "Prominent")
        mer_prom = getattr(profile.mount_mercury, "prominence", "Normal")
        ven_prom = getattr(profile.mount_venus, "prominence", "Prominent")
        moon_prom = getattr(profile.mount_moon, "prominence", "Prominent")

        if is_right_hand:
            # =================================================================
            # RIGHT HAND (Thumb on RIGHT, Little finger on LEFT)
            # Coordinates designed for width=580, height=740
            # =================================================================
            contour_path = (
                "M 210 645 "
                "C 175 620, 155 555, 155 490 "
                "C 155 435, 165 380, 170 335 "
                "C 170 295, 175 230, 182 185 "
                "C 186 160, 204 160, 208 185 "
                "C 212 230, 215 285, 218 315 "
                "C 220 280, 225 190, 232 125 "
                "C 236 100, 256 100, 260 125 "
                "C 264 190, 268 255, 270 298 "
                "C 272 260, 278 150, 288 75 "
                "C 292 50, 314 50, 318 75 "
                "C 324 150, 326 245, 328 300 "
                "C 332 260, 338 175, 345 115 "
                "C 349 90, 370 90, 374 115 "
                "C 378 180, 380 260, 382 325 "
                "C 386 365, 392 395, 400 420 "
                "C 422 415, 460 420, 495 440 "
                "C 520 455, 520 480, 498 495 "
                "C 475 510, 445 520, 425 545 "
                "C 405 570, 390 610, 370 645 "
                "Z"
            )

            # Mount badge coordinates (x, y, label, symbol)
            mount_badges = [
                (358, 325, "गुरु", "♃", "#92400E", "#FEF3C7", "#D97706"),
                (303, 310, "शनि", "♄", "#1E293B", "#F1F5F9", "#64748B"),
                (246, 322, "सूर्य", "☉", "#854D0E", "#FEF9C3", "#CA8A04"),
                (192, 335, "बुध", "☿", "#166534", "#DCFCE7", "#16A34A"),
                (178, 415, "उ.मंगल", "♂", "#991B1B", "#FEE2E2", "#DC2626"),
                (388, 410, "नि.मंगल", "♂", "#991B1B", "#FEE2E2", "#DC2626"),
                (285, 445, "राहु", "☊", "#6B21A8", "#F3E8FF", "#A855F7"),
                (385, 530, "शुक्र", "♀", "#9D174D", "#FCE7F3", "#EC4899"),
                (195, 530, "चन्द्र", "☽", "#075985", "#E0F2FE", "#0284C7"),
                (285, 605, "केतु", "☋", "#334155", "#F1F5F9", "#64748B"),
            ]

            # Primary Lines (natural organic curvatures)
            # 1. Heart Line (Red) - from outer under pinky curving up towards Jupiter
            heart_d = "M 160 375 C 215 382, 275 375, 320 350 C 342 338, 355 320, 360 305"
            heart_badge = (65, 372, "हृदय रेखा", "#E11D48", 160, 375)

            # 2. Head Line (Blue) - from index/thumb sloping towards Moon mount
            head_d = "M 390 410 C 340 420, 280 445, 230 480 C 195 505, 175 530, 162 550"
            head_badge = (65, 548, "मस्तिष्क रेखा", "#2563EB", 162, 550)

            # 3. Life Line (Green) - wrapping graciously around Venus mount
            life_d = "M 390 405 C 375 440, 352 490, 352 540 C 352 585, 342 615, 308 635"
            life_badge = (395, 645, "जीवन रेखा (आयु)", "#059669", 308, 635)

            # Age markers along life line
            age_markers = [
                (362, 442, "२०"),
                (352, 498, "४०"),
                (352, 555, "६०"),
                (330, 612, "८०"),
            ]

            # 4. Fate Line (Gold) - vertical from wrist to Saturn mount
            fate_d = "M 285 630 C 288 560, 292 480, 295 415 C 298 375, 300 340, 300 310"
            fate_badge = (300, 255, "भाग्य रेखा", "#D97706", 300, 310)

            # 5. Sun Line (Yellow) - rising towards Sun mount
            sun_d = "M 246 455 C 246 410, 246 365, 246 325"

            # 6. Marriage Line (Pink)
            marr_d = "M 158 355 L 180 355"
            marr_badge = (75, 354, "विवाह", "#BE123C")

            # Bracelets at wrist
            brc_paths = [
                "M 215 658 C 265 670, 315 670, 365 658",
                "M 220 670 C 265 682, 315 682, 360 670",
                "M 225 682 C 265 694, 315 694, 355 682",
            ]

            # Sacred Marks
            yava_pos = (455, 455)
            cross_pos = (255, 415)
            matsya_pos = (285, 590)

        else:
            # =================================================================
            # LEFT HAND (Thumb on LEFT, Little finger on RIGHT)
            # =================================================================
            contour_path = (
                "M 370 645 "
                "C 405 620, 425 555, 425 490 "
                "C 425 435, 415 380, 410 335 "
                "C 410 295, 405 230, 398 185 "
                "C 394 160, 376 160, 372 185 "
                "C 368 230, 365 285, 362 315 "
                "C 360 280, 355 190, 348 125 "
                "C 344 100, 324 100, 320 125 "
                "C 316 190, 312 255, 310 298 "
                "C 308 260, 302 150, 292 75 "
                "C 288 50, 266 50, 262 75 "
                "C 256 150, 254 245, 252 300 "
                "C 248 260, 242 175, 235 115 "
                "C 231 90, 210 90, 206 115 "
                "C 202 180, 200 260, 198 325 "
                "C 194 365, 188 395, 180 420 "
                "C 158 415, 120 420, 85 440 "
                "C 60 455, 60 480, 82 495 "
                "C 105 510, 135 520, 155 545 "
                "C 175 570, 190 610, 210 645 "
                "Z"
            )

            mount_badges = [
                (222, 325, "गुरु", "♃", "#92400E", "#FEF3C7", "#D97706"),
                (277, 310, "शनि", "♄", "#1E293B", "#F1F5F9", "#64748B"),
                (334, 322, "सूर्य", "☉", "#854D0E", "#FEF9C3", "#CA8A04"),
                (388, 335, "बुध", "☿", "#166534", "#DCFCE7", "#16A34A"),
                (402, 415, "उ.मंगल", "♂", "#991B1B", "#FEE2E2", "#DC2626"),
                (192, 410, "नि.मंगल", "♂", "#991B1B", "#FEE2E2", "#DC2626"),
                (295, 445, "राहु", "☊", "#6B21A8", "#F3E8FF", "#A855F7"),
                (195, 530, "शुक्र", "♀", "#9D174D", "#FCE7F3", "#EC4899"),
                (385, 530, "चन्द्र", "☽", "#075985", "#E0F2FE", "#0284C7"),
                (295, 605, "केतु", "☋", "#334155", "#F1F5F9", "#64748B"),
            ]

            heart_d = "M 420 375 C 365 382, 305 375, 260 350 C 238 338, 225 320, 220 305"
            heart_badge = (515, 372, "हृदय रेखा", "#E11D48", 420, 375)

            head_d = "M 190 410 C 240 420, 300 445, 350 480 C 385 505, 405 530, 418 550"
            head_badge = (515, 548, "मस्तिष्क रेखा", "#2563EB", 418, 550)

            life_d = "M 190 405 C 205 440, 228 490, 228 540 C 228 585, 238 615, 272 635"
            life_badge = (185, 645, "जीवन रेखा (आयु)", "#059669", 272, 635)

            age_markers = [
                (218, 442, "२०"),
                (228, 498, "४०"),
                (228, 555, "६०"),
                (250, 612, "८०"),
            ]

            fate_d = "M 295 630 C 292 560, 288 480, 285 415 C 282 375, 280 340, 280 310"
            fate_badge = (280, 255, "भाग्य रेखा", "#D97706", 280, 310)

            sun_d = "M 334 455 C 334 410, 334 365, 334 325"

            marr_d = "M 422 355 L 400 355"
            marr_badge = (505, 354, "विवाह", "#BE123C")

            brc_paths = [
                "M 365 658 C 315 670, 265 670, 215 658",
                "M 360 670 C 315 682, 265 682, 220 670",
                "M 355 682 C 315 694, 265 694, 225 682",
            ]

            yava_pos = (125, 455)
            cross_pos = (325, 415)
            matsya_pos = (295, 590)

        # Build crisp, modern SVG with zero clutter
        svg_parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="100%" height="{height}" style="background: radial-gradient(circle at 50% 40%, #FFFFFF 0%, #F8FAFC 100%); border: 1.5px solid #CBD5E1; border-radius: 16px; font-family: -apple-system, BlinkMacSystemFont, \'Segoe UI\', Roboto, sans-serif;">',
            '<defs>',
            '  <linearGradient id="palmGrad" x1="0%" y1="0%" x2="100%" y2="100%">',
            '    <stop offset="0%" stop-color="#FFF8F0" />',
            '    <stop offset="50%" stop-color="#FFEEDD" />',
            '    <stop offset="100%" stop-color="#FCDCB2" />',
            '  </linearGradient>',
            '  <filter id="softShadow" x="-10%" y="-10%" width="120%" height="120%">',
            '    <feDropShadow dx="0" dy="3" stdDeviation="4" flood-color="#D97706" flood-opacity="0.18" />',
            '  </filter>',
            '</defs>',
            # Header Titles
            f'<text x="{width//2}" y="28" text-anchor="middle" fill="#0F172A" font-size="15" font-weight="900" letter-spacing="0.5">✋ शास्त्रीय हस्तरेखा एवं नवग्रह पर्वत आरेख</text>',
            f'<text x="{width//2}" y="46" text-anchor="middle" fill="#64748B" font-size="11" font-weight="600">{hand_label} | हस्त: {profile.hand_type} | अंगूठा: {profile.thumb_type}</text>',
            # Hand Contour with Soft Shadow
            f'<path d="{contour_path}" fill="url(#palmGrad)" stroke="#F59E0B" stroke-width="2.2" stroke-linejoin="round" filter="url(#softShadow)" />',
            # Mount Badges
            '<g id="mountBadges">',
        ]

        for mb in mount_badges:
            bx, by, bname, bsym, btxt, bbg, bstrk = mb
            svg_parts.append(
                f'<g transform="translate({bx-24}, {by-11})">'
                f'<rect width="48" height="22" rx="11" fill="{bbg}" stroke="{bstrk}" stroke-width="1.2" opacity="0.9" />'
                f'<text x="24" y="15" text-anchor="middle" fill="{btxt}" font-size="10.5" font-weight="900">{bsym} {bname}</text>'
                f'</g>'
            )
        svg_parts.append('</g>')

        # Major Lines
        svg_parts.extend([
            '<g id="majorLines" stroke-linecap="round" fill="none">',
            f'  <path d="{heart_d}" stroke="#E11D48" stroke-width="3.6" />',
            f'  <path d="{head_d}" stroke="#2563EB" stroke-width="3.6" />',
            f'  <path d="{life_d}" stroke="#059669" stroke-width="4.0" />',
            f'  <path d="{fate_d}" stroke="#D97706" stroke-width="3.2" stroke-dasharray="0" />',
            f'  <path d="{sun_d}" stroke="#CA8A04" stroke-width="2.6" />',
            f'  <path d="{marr_d}" stroke="#BE123C" stroke-width="2.8" />',
            '</g>',
        ])

        # Age Milestones on Life Line
        svg_parts.append('<g id="ageMarkers">')
        for am in age_markers:
            svg_parts.append(
                f'<circle cx="{am[0]}" cy="{am[1]}" r="4" fill="#059669" stroke="#FFFFFF" stroke-width="1.5" />'
                f'<text x="{am[0]+8}" y="{am[1]+4}" fill="#047857" font-size="9" font-weight="900">{am[2]}व.</text>'
            )
        svg_parts.append('</g>')

        # Callout Badges with clean pointers
        # Heart Line Badge
        svg_parts.extend([
            f'<line x1="{heart_badge[0]+38}" y1="{heart_badge[1]}" x2="{heart_badge[4]}" y2="{heart_badge[5]}" stroke="#E11D48" stroke-width="1" stroke-dasharray="2 2" opacity="0.7" />',
            f'<g transform="translate({heart_badge[0]-35}, {heart_badge[1]-11})">',
            f'  <rect width="76" height="22" rx="6" fill="#FFF1F2" stroke="#E11D48" stroke-width="1.2" />',
            f'  <text x="38" y="15" text-anchor="middle" fill="#BE123C" font-size="10" font-weight="900">{heart_badge[2]}</text>',
            '</g>',
            # Head Line Badge
            f'<line x1="{head_badge[0]+42}" y1="{head_badge[1]}" x2="{head_badge[4]}" y2="{head_badge[5]}" stroke="#2563EB" stroke-width="1" stroke-dasharray="2 2" opacity="0.7" />',
            f'<g transform="translate({head_badge[0]-42}, {head_badge[1]-11})">',
            f'  <rect width="84" height="22" rx="6" fill="#EFF6FF" stroke="#2563EB" stroke-width="1.2" />',
            f'  <text x="42" y="15" text-anchor="middle" fill="#1D4ED8" font-size="10" font-weight="900">{head_badge[2]}</text>',
            '</g>',
            # Fate Line Badge
            f'<g transform="translate({fate_badge[0]-34}, {fate_badge[1]-11})">',
            f'  <rect width="68" height="22" rx="6" fill="#FFFBEB" stroke="#D97706" stroke-width="1.2" />',
            f'  <text x="34" y="15" text-anchor="middle" fill="#B45309" font-size="10" font-weight="900">{fate_badge[2]}</text>',
            '</g>',
            # Marriage Badge
            f'<text x="{marr_badge[0]}" y="{marr_badge[1]}" fill="#BE123C" font-size="9.5" font-weight="800">{marr_badge[2]}</text>',
        ])

        # Bracelets at Wrist
        svg_parts.append('<g id="bracelets" stroke="#0D9488" stroke-width="2.2" stroke-linecap="round" fill="none">')
        for bp in brc_paths:
            svg_parts.append(f'  <path d="{bp}" />')
        svg_parts.append('</g>')

        # Sacred Marks (Yava, Cross, Matsya)
        svg_parts.append('<g id="sacredMarks">')
        if show_yava:
            svg_parts.extend([
                f'<ellipse cx="{yava_pos[0]}" cy="{yava_pos[1]}" rx="9" ry="5" fill="#FEF3C7" stroke="#B45309" stroke-width="1.8" />',
                f'<circle cx="{yava_pos[0]}" cy="{yava_pos[1]}" r="2" fill="#B45309" />',
                f'<text x="{yava_pos[0]}" y="{yava_pos[1]+16}" text-anchor="middle" fill="#B45309" font-size="8.5" font-weight="800">बुद्ध चक्षु</text>',
            ])
        if show_cross:
            svg_parts.extend([
                f'<g transform="translate({cross_pos[0]}, {cross_pos[1]})">',
                '  <line x1="-6" y1="-6" x2="6" y2="6" stroke="#7C3AED" stroke-width="2.4" stroke-linecap="round" />',
                '  <line x1="6" y1="-6" x2="-6" y2="6" stroke="#7C3AED" stroke-width="2.4" stroke-linecap="round" />',
                '  <text x="10" y="4" fill="#7C3AED" font-size="8.5" font-weight="800">क्रॉस</text>',
                '</g>',
            ])
        if show_matsya:
            svg_parts.extend([
                f'<g transform="translate({matsya_pos[0]}, {matsya_pos[1]})">',
                '  <path d="M -8 -6 C 0 0, 4 4, 8 4 C 4 4, 0 0, -8 6 C -4 2, -4 -2, -8 -6 Z" fill="#FDE68A" stroke="#B45309" stroke-width="1.6" />',
                '  <text x="12" y="3" fill="#B45309" font-size="8.5" font-weight="800">मत्स्य</text>',
                '</g>',
            ])
        svg_parts.append('</g>')

        # Footer Legend Strip
        svg_parts.extend([
            f'<rect x="15" y="{height-38}" width="{width - 30}" height="28" rx="8" fill="#F8FAFC" stroke="#E2E8F0" />',
            f'<text x="{width//2}" y="{height-20}" text-anchor="middle" fill="#475569" font-size="10" font-weight="700">',
            '🔴 हृदय रेखा | 🔵 मस्तिष्क रेखा | 🟢 जीवन रेखा (आयु) | 🟠 भाग्य रेखा | 🟡 सूर्य रेखा | 📿 मणिबंध कंकण',
            '</text>',
            '</svg>'
        ])

        return "\n".join([p for p in svg_parts if p.strip()])
