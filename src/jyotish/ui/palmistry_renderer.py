"""
हस्तरेखा विज़ुअलाइज़र (Interactive High-Definition Realistic SVG Palm Renderer)
Professional, anatomically authentic palm diagrams with 3D pad volumes, finger joint
creases (पोर), natural skin shading, non-colliding labels, and sacred shastriya marks.
"""

from typing import Dict, Any, Optional
from src.jyotish.core.palmistry import PalmInputProfile


class PalmRenderer:
    """
    Renders scalable, crisp, responsive SVG palm diagrams for Vedic Hastarekha.
    Features realistic anatomical volume, finger phalanxes, thenar/hypothenar cushions,
    zero-collision typography, and canonical scriptural line paths.
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
        Generates realistic 3D anatomical SVG representing the native's palm.
        """
        if is_right_hand is None:
            is_right_hand = (getattr(profile, "hand_side", "Right") != "Left")

        # Sacred marks visibility
        show_yava = getattr(profile, "has_buddha_eye", True)
        show_cross = getattr(profile, "has_mystic_cross", True)
        show_matsya = getattr(profile, "has_matsya_sign", True)
        show_trishul = getattr(profile, "has_trishul_sign", False)

        hand_label = "दायां हाथ (Right Palm)" if is_right_hand else "बायां हाथ (Left Palm)"

        if is_right_hand:
            # =================================================================
            # RIGHT HAND (Thumb on RIGHT, Little finger on LEFT)
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

            # Realistic Finger Joint Creases (पोर)
            finger_creases = [
                # Little finger joints
                "M 176 235 C 185 237, 195 237, 204 235",
                "M 178 280 C 187 282, 197 282, 206 280",
                # Ring finger joints
                "M 226 180 C 236 182, 246 182, 254 180",
                "M 228 245 C 238 247, 248 247, 258 245",
                # Middle finger joints
                "M 282 155 C 292 157, 302 157, 312 155",
                "M 284 225 C 295 227, 305 227, 316 225",
                # Index finger joints
                "M 342 175 C 350 177, 360 177, 368 175",
                "M 344 240 C 354 242, 364 242, 372 240",
                # Thumb joint
                "M 432 440 C 445 448, 460 455, 475 460",
            ]

            thenar_pos = (395, 525)
            moon_pos = (195, 525)
            rahu_pos = (285, 445)

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

            heart_d = "M 160 375 C 215 382, 275 375, 320 350 C 342 338, 355 320, 360 305"
            heart_badge = (65, 372, "हृदय रेखा", "#E11D48", 160, 375)

            head_d = "M 390 410 C 340 420, 280 445, 230 480 C 195 505, 175 530, 162 550"
            head_badge = (65, 548, "मस्तिष्क रेखा", "#2563EB", 162, 550)

            life_d = "M 390 405 C 375 440, 352 490, 352 540 C 352 585, 342 615, 308 635"
            life_badge = (395, 645, "जीवन रेखा (आयु)", "#059669", 308, 635)

            age_markers = [
                (362, 442, "२०"),
                (352, 498, "४०"),
                (352, 555, "६०"),
                (330, 612, "८०"),
            ]

            fate_d = "M 285 630 C 288 560, 292 480, 295 415 C 298 375, 300 340, 300 310"
            fate_badge = (300, 255, "भाग्य रेखा", "#D97706", 300, 310)

            sun_d = "M 246 455 C 246 410, 246 365, 246 325"
            sun_badge = (246, 265, "सूर्य रेखा", "#CA8A04")

            marr_d = "M 158 355 L 180 355"
            marr_badge = (75, 354, "विवाह", "#BE123C")

            brc_paths = [
                "M 215 658 C 265 670, 315 670, 365 658",
                "M 220 670 C 265 682, 315 682, 360 670",
                "M 225 682 C 265 694, 315 694, 355 682",
            ]

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

            finger_creases = [
                "M 404 235 C 395 237, 385 237, 376 235",
                "M 402 280 C 393 282, 383 282, 374 280",
                "M 354 180 C 344 182, 334 182, 326 180",
                "M 352 245 C 342 247, 332 247, 322 245",
                "M 298 155 C 288 157, 278 157, 268 155",
                "M 296 225 C 285 227, 275 227, 264 225",
                "M 238 175 C 230 177, 220 177, 212 175",
                "M 236 240 C 226 242, 216 242, 208 240",
                "M 148 440 C 135 448, 120 455, 105 460",
            ]

            thenar_pos = (185, 525)
            moon_pos = (385, 525)
            rahu_pos = (295, 445)

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
            sun_badge = (334, 265, "सूर्य रेखा", "#CA8A04")

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

        # Build realistic 3D anatomical SVG
        svg_parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="100%" height="{height}" style="background: radial-gradient(circle at 50% 35%, #FFFFFF 0%, #F1F5F9 100%); border: 1.5px solid #CBD5E1; border-radius: 16px; font-family: -apple-system, BlinkMacSystemFont, \'Segoe UI\', Roboto, sans-serif;">',
            '<defs>',
            '  <!-- Realistic Multi-Stop Skin Gradient -->',
            '  <linearGradient id="realSkin" x1="20%" y1="0%" x2="80%" y2="100%">',
            '    <stop offset="0%" stop-color="#FFF5EB" />',
            '    <stop offset="35%" stop-color="#FFE7D3" />',
            '    <stop offset="70%" stop-color="#FDD0A2" />',
            '    <stop offset="100%" stop-color="#F6B26B" />',
            '  </linearGradient>',
            '  <!-- Thenar Venus Cushion 3D Highlight -->',
            '  <radialGradient id="venusCushion" cx="45%" cy="45%" r="55%">',
            '    <stop offset="0%" stop-color="#FFEEDD" stop-opacity="0.85" />',
            '    <stop offset="60%" stop-color="#FDBA74" stop-opacity="0.35" />',
            '    <stop offset="100%" stop-color="#F59E0B" stop-opacity="0" />',
            '  </radialGradient>',
            '  <!-- Moon Hypothenar Cushion 3D Highlight -->',
            '  <radialGradient id="moonCushion" cx="45%" cy="45%" r="55%">',
            '    <stop offset="0%" stop-color="#FFEEDD" stop-opacity="0.75" />',
            '    <stop offset="60%" stop-color="#FDBA74" stop-opacity="0.30" />',
            '    <stop offset="100%" stop-color="#F59E0B" stop-opacity="0" />',
            '  </radialGradient>',
            '  <!-- Rahu Palm Hollow Center Shadow -->',
            '  <radialGradient id="rahuDepth" cx="50%" cy="50%" r="50%">',
            '    <stop offset="0%" stop-color="#92400E" stop-opacity="0.10" />',
            '    <stop offset="70%" stop-color="#92400E" stop-opacity="0.03" />',
            '    <stop offset="100%" stop-color="#92400E" stop-opacity="0" />',
            '  </radialGradient>',
            '  <!-- Soft Natural Drop Shadow -->',
            '  <filter id="handShadow" x="-15%" y="-10%" width="130%" height="120%">',
            '    <feDropShadow dx="0" dy="5" stdDeviation="6" flood-color="#78350F" flood-opacity="0.22" />',
            '  </filter>',
            '</defs>',
            # Header
            f'<text x="{width//2}" y="28" text-anchor="middle" fill="#0F172A" font-size="15" font-weight="900" letter-spacing="0.5">✋ यथार्थवादी ३D हस्तरेखा एवं नवग्रह पर्वत आरेख</text>',
            f'<text x="{width//2}" y="46" text-anchor="middle" fill="#64748B" font-size="11" font-weight="600">{hand_label} | हस्त: {profile.hand_type} | अंगूठा: {profile.thumb_type}</text>',
            # Base Hand Contour with 3D Depth
            f'<path d="{contour_path}" fill="url(#realSkin)" stroke="#D97706" stroke-width="2.4" stroke-linejoin="round" filter="url(#handShadow)" />',
            # 3D Palm Cushions & Hollow
            f'<ellipse cx="{thenar_pos[0]}" cy="{thenar_pos[1]}" rx="45" ry="58" fill="url(#venusCushion)" />',
            f'<ellipse cx="{moon_pos[0]}" cy="{moon_pos[1]}" rx="40" ry="54" fill="url(#moonCushion)" />',
            f'<ellipse cx="{rahu_pos[0]}" cy="{rahu_pos[1]}" rx="46" ry="32" fill="url(#rahuDepth)" />',
            # Finger Phalanx Joint Creases (पोर)
            '<g id="fingerJoints" stroke="#C2410C" stroke-width="1.3" opacity="0.45" stroke-linecap="round">',
        ]

        for fc in finger_creases:
            svg_parts.append(f'  <path d="{fc}" />')
        svg_parts.append('</g>')

        # Mount Badges
        svg_parts.append('<g id="mountBadges">')
        for mb in mount_badges:
            bx, by, bname, bsym, btxt, bbg, bstrk = mb
            svg_parts.append(
                f'<g transform="translate({bx-24}, {by-11})">'
                f'<rect width="48" height="22" rx="11" fill="{bbg}" stroke="{bstrk}" stroke-width="1.2" opacity="0.95" />'
                f'<text x="24" y="15" text-anchor="middle" fill="{btxt}" font-size="10.5" font-weight="900">{bsym} {bname}</text>'
                f'</g>'
            )
        svg_parts.append('</g>')

        # Major Canonical Lines
        svg_parts.extend([
            '<g id="majorLines" stroke-linecap="round" fill="none">',
            f'  <path d="{heart_d}" stroke="#E11D48" stroke-width="3.8" />',
            f'  <path d="{head_d}" stroke="#2563EB" stroke-width="3.8" />',
            f'  <path d="{life_d}" stroke="#059669" stroke-width="4.2" />',
            f'  <path d="{fate_d}" stroke="#D97706" stroke-width="3.4" />',
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
        svg_parts.extend([
            f'<line x1="{heart_badge[0]+38}" y1="{heart_badge[1]}" x2="{heart_badge[4]}" y2="{heart_badge[5]}" stroke="#E11D48" stroke-width="1" stroke-dasharray="2 2" opacity="0.7" />',
            f'<g transform="translate({heart_badge[0]-35}, {heart_badge[1]-11})">',
            f'  <rect width="76" height="22" rx="6" fill="#FFF1F2" stroke="#E11D48" stroke-width="1.2" />',
            f'  <text x="38" y="15" text-anchor="middle" fill="#BE123C" font-size="10" font-weight="900">{heart_badge[2]}</text>',
            '</g>',
            f'<line x1="{head_badge[0]+42}" y1="{head_badge[1]}" x2="{head_badge[4]}" y2="{head_badge[5]}" stroke="#2563EB" stroke-width="1" stroke-dasharray="2 2" opacity="0.7" />',
            f'<g transform="translate({head_badge[0]-42}, {head_badge[1]-11})">',
            f'  <rect width="84" height="22" rx="6" fill="#EFF6FF" stroke="#2563EB" stroke-width="1.2" />',
            f'  <text x="42" y="15" text-anchor="middle" fill="#1D4ED8" font-size="10" font-weight="900">{head_badge[2]}</text>',
            '</g>',
            f'<g transform="translate({fate_badge[0]-34}, {fate_badge[1]-11})">',
            f'  <rect width="68" height="22" rx="6" fill="#FFFBEB" stroke="#D97706" stroke-width="1.2" />',
            f'  <text x="34" y="15" text-anchor="middle" fill="#B45309" font-size="10" font-weight="900">{fate_badge[2]}</text>',
            '</g>',
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
