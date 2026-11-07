"""
हस्तरेखा विज़ुअलाइज़र (Interactive High-Definition SVG Palm Renderer)
Renders canonical palm maps with planetary mounts, major/minor lines, age markers, and sacred marks.
Supports both Right Hand (दायां हाथ - Thumb on Right) and Left Hand (बायां हाथ - Thumb on Left).
"""

from typing import Dict, Any, Optional
from src.jyotish.core.palmistry import PalmInputProfile


class PalmRenderer:
    """
    Renders scalable, crisp, responsive SVG palm diagrams for Vedic Hastarekha.
    Supports both Right Hand (Dakshina Hasta) and Left Hand (Vama Hasta).
    """

    @classmethod
    def render_palm_svg(
        cls,
        profile: PalmInputProfile,
        width: int = 540,
        height: int = 680,
        is_right_hand: Optional[bool] = None
    ) -> str:
        """
        Generates full-detail SVG markup representing the native's palm.
        When is_right_hand is True (default in Vedic for right hand photo),
        the thumb is positioned on the RIGHT side, matching camera/photo input.
        """
        if is_right_hand is None:
            is_right_hand = (getattr(profile, "hand_side", "Right") != "Left")

        # Sacred marks visibility
        show_yava = profile.has_buddha_eye
        show_cross = profile.has_mystic_cross
        show_matsya = profile.has_matsya_sign
        show_trishul = profile.has_trishul_sign
        show_jup_cross = profile.mount_jupiter.has_cross

        hand_label = "दायां हाथ (Right Palm)" if is_right_hand else "बायां हाथ (Left Palm)"

        if is_right_hand:
            # =================================================================
            # RIGHT HAND GEOMETRY (Thumb on RIGHT, Little finger on LEFT)
            # =================================================================
            # Hand Contour Path
            contour_path = (
                "M 170 560 "
                "C 140 530, 130 480, 132 440 "
                "C 134 380, 140 320, 145 270 "
                "C 142 220, 150 160, 160 135 "
                "C 168 115, 185 125, 188 150 "
                "C 192 190, 188 230, 192 250 "
                "C 198 210, 208 100, 218 75 "
                "C 228 55, 245 70, 245 105 "
                "C 245 160, 246 215, 248 235 "
                "C 255 180, 270 70, 280 50 "
                "C 292 35, 310 50, 308 100 "
                "C 305 160, 302 215, 304 235 "
                "C 315 190, 332 135, 345 120 "
                "C 360 110, 372 130, 368 170 "
                "C 360 220, 356 260, 358 290 "
                "C 362 310, 385 315, 415 325 "
                "C 455 340, 485 355, 480 385 "
                "C 475 415, 435 430, 410 455 "
                "C 390 480, 385 525, 370 560 "
                "Z"
            )

            # Mount positions
            m_jup = (335, 280, "♃ गुरु", profile.mount_jupiter.prominence, "#92400E", "#FEF3C7", "#D97706")
            m_sat = (275, 260, "♄ शनि", profile.mount_saturn.prominence, "#1E293B", "#E2E8F0", "#475569")
            m_sun = (215, 275, "☉ सूर्य", profile.mount_sun.prominence, "#854D0E", "#FEF9C3", "#CA8A04")
            m_mer = (160, 295, "☿ बुध", profile.mount_mercury.prominence, "#166534", "#DCFCE7", "#16A34A")
            m_lmars = (365, 345, "♂ नि.मंगल", "#991B1B", "#FEE2E2", "#DC2626")
            m_umars = (155, 365, "♂ उ.मंगल", "#991B1B", "#FEE2E2", "#DC2626")
            m_rahu = (270, 380, "☊ राहु गर्त", "#6B21A8", "#F3E8FF", "#9333EA")
            m_ven = (365, 465, "♀ शुक्र", profile.mount_venus.prominence, "#9D174D", "#FCE7F3", "#DB2777")
            m_moon = (175, 475, "☽ चन्द्र", profile.mount_moon.prominence, "#075985", "#E0F2FE", "#0284C7")
            m_ketu = (270, 535, "☋ केतु", "#334155", "#F1F5F9", "#475569")

            # Lines Paths
            # 1. Heart Line (Starts under little finger on Left, sweeps right towards Jupiter)
            heart_path = "M 135 325 C 190 315, 260 310, 310 285 C 325 278, 335 270, 340 265"
            heart_lbl_x, heart_lbl_y, heart_anchor = 125, 320, "end"

            # 2. Head Line (Starts near thumb on Right, sweeps left towards Moon mount)
            head_path = "M 365 330 C 315 335, 245 365, 195 395 C 175 410, 160 425, 150 440"
            head_lbl_x, head_lbl_y, head_anchor = 140, 445, "end"

            # 3. Life Line (Starts near thumb on Right, wraps around Venus mount down to Ketu)
            life_path = "M 365 325 C 345 345, 320 395, 315 440 C 310 490, 320 525, 290 555"
            life_lbl_x, life_lbl_y, life_anchor = 280, 565, "end"

            # Life Line Age Markers (Right Hand)
            age_dots = [
                (345, 365, "२० व.", 355, 368),
                (325, 425, "४० व.", 335, 428),
                (315, 485, "६० व.", 325, 488),
                (300, 535, "८० व.", 310, 538),
            ]

            # 4. Fate Line (Vertical up center towards Saturn)
            fate_path = "M 270 545 C 272 485, 274 395, 275 320 C 275 295, 275 275, 275 255"
            fate_lbl_x, fate_lbl_y = 275, 240

            # 5. Sun Line (Vertical towards Sun mount)
            sun_path = "M 218 385 C 216 350, 215 315, 215 270"
            sun_lbl_x, sun_lbl_y = 215, 255

            # 6. Marriage Line (Outer edge below little finger)
            marr_path = "M 132 295 L 155 295"
            marr_lbl_x, marr_lbl_y = 125, 298

            # Bracelets
            brc1 = "M 190 572 C 250 585, 290 585, 350 572"
            brc2 = "M 195 584 C 250 597, 290 597, 345 584"
            brc3 = "M 200 596 C 250 608, 290 608, 340 596"
            brc_lbl_x = 175

            # Sacred Marks Coordinates
            yava_cx, yava_cy = 430, 375
            cross_x, cross_y = 250, 345
            matsya_x, matsya_y = 270, 515
            jup_cross_x, jup_cross_y = 340, 290
            trishul_x, trishul_y = 275, 248

        else:
            # =================================================================
            # LEFT HAND GEOMETRY (Thumb on LEFT, Little finger on RIGHT)
            # =================================================================
            contour_path = (
                "M 370 560 "
                "C 400 530, 410 480, 408 440 "
                "C 406 380, 400 320, 395 270 "
                "C 398 220, 390 160, 380 135 "
                "C 372 115, 355 125, 352 150 "
                "C 348 190, 352 230, 348 250 "
                "C 342 210, 332 100, 322 75 "
                "C 312 55, 295 70, 295 105 "
                "C 295 160, 294 215, 292 235 "
                "C 285 180, 270 70, 260 50 "
                "C 248 35, 230 50, 232 100 "
                "C 235 160, 238 215, 236 235 "
                "C 225 190, 208 135, 195 120 "
                "C 180 110, 168 130, 172 170 "
                "C 180 220, 184 260, 182 290 "
                "C 178 310, 155 315, 125 325 "
                "C 85 340, 55 355, 60 385 "
                "C 65 415, 105 430, 130 455 "
                "C 150 480, 155 525, 170 560 "
                "Z"
            )

            m_jup = (205, 280, "♃ गुरु", profile.mount_jupiter.prominence, "#92400E", "#FEF3C7", "#D97706")
            m_sat = (265, 260, "♄ शनि", profile.mount_saturn.prominence, "#1E293B", "#E2E8F0", "#475569")
            m_sun = (325, 275, "☉ सूर्य", profile.mount_sun.prominence, "#854D0E", "#FEF9C3", "#CA8A04")
            m_mer = (380, 295, "☿ बुध", profile.mount_mercury.prominence, "#166534", "#DCFCE7", "#16A34A")
            m_lmars = (175, 345, "♂ नि.मंगल", "#991B1B", "#FEE2E2", "#DC2626")
            m_umars = (385, 365, "♂ उ.मंगल", "#991B1B", "#FEE2E2", "#DC2626")
            m_rahu = (270, 380, "☊ राहु गर्त", "#6B21A8", "#F3E8FF", "#9333EA")
            m_ven = (175, 465, "♀ शुक्र", profile.mount_venus.prominence, "#9D174D", "#FCE7F3", "#DB2777")
            m_moon = (365, 475, "☽ चन्द्र", profile.mount_moon.prominence, "#075985", "#E0F2FE", "#0284C7")
            m_ketu = (270, 535, "☋ केतु", "#334155", "#F1F5F9", "#475569")

            heart_path = "M 405 325 C 350 315, 280 310, 230 285 C 215 278, 205 270, 200 265"
            heart_lbl_x, heart_lbl_y, heart_anchor = 415, 320, "start"

            head_path = "M 175 330 C 225 335, 295 365, 345 395 C 365 410, 380 425, 390 440"
            head_lbl_x, head_lbl_y, head_anchor = 400, 445, "start"

            life_path = "M 175 325 C 195 345, 220 395, 225 440 C 230 490, 220 525, 250 555"
            life_lbl_x, life_lbl_y, life_anchor = 260, 565, "start"

            age_dots = [
                (195, 365, "२० व.", 185, 368),
                (215, 425, "४० व.", 205, 428),
                (225, 485, "६० व.", 215, 488),
                (240, 535, "८० व.", 230, 538),
            ]

            fate_path = "M 270 545 C 268 485, 266 395, 265 320 C 265 295, 265 275, 265 255"
            fate_lbl_x, fate_lbl_y = 265, 240

            sun_path = "M 322 385 C 324 350, 325 315, 325 270"
            sun_lbl_x, sun_lbl_y = 325, 255

            marr_path = "M 408 295 L 385 295"
            marr_lbl_x, marr_lbl_y = 415, 298

            brc1 = "M 350 572 C 290 585, 250 585, 190 572"
            brc2 = "M 345 584 C 290 597, 250 597, 195 584"
            brc3 = "M 340 596 C 290 608, 250 608, 200 596"
            brc_lbl_x = 365

            yava_cx, yava_cy = 110, 375
            cross_x, cross_y = 290, 345
            matsya_x, matsya_y = 270, 515
            jup_cross_x, jup_cross_y = 200, 290
            trishul_x, trishul_y = 265, 248

        # Build clean compact SVG without blank lines
        svg_parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="100%" height="{height}" style="background: radial-gradient(circle at 50% 50%, #FFFFFF 0%, #F8FAFC 100%); border: 2px solid #CBD5E1; border-radius: 16px; box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.05); font-family: -apple-system, BlinkMacSystemFont, \'Segoe UI\', Roboto, sans-serif;">',
            '<defs>',
            '  <linearGradient id="palmSkinGrad" x1="0%" y1="0%" x2="100%" y2="100%">',
            '    <stop offset="0%" stop-color="#FFF5EB" />',
            '    <stop offset="50%" stop-color="#FFEAD6" />',
            '    <stop offset="100%" stop-color="#FED7AA" />',
            '  </linearGradient>',
            '  <filter id="subtleGlow" x="-20%" y="-20%" width="140%" height="140%">',
            '    <feDropShadow dx="0" dy="2" stdDeviation="3" flood-color="#D97706" flood-opacity="0.25" />',
            '  </filter>',
            '</defs>',
            f'<text x="{width//2}" y="30" text-anchor="middle" fill="#0F172A" font-size="16" font-weight="900" letter-spacing="0.5">✋ शास्त्रीय हस्तरेखा एवं नवग्रह पर्वत आरेख ({hand_label})</text>',
            f'<text x="{width//2}" y="48" text-anchor="middle" fill="#64748B" font-size="11" font-weight="600">हस्त: {profile.hand_type} | अंगूठा: {profile.thumb_type} | वर्ण: {profile.skin_texture}</text>',
            f'<g id="handContour"><path d="{contour_path}" fill="url(#palmSkinGrad)" stroke="#F59E0B" stroke-width="2.5" stroke-linejoin="round" /></g>',
            # Mounts
            '<g id="mounts">',
            f'  <circle cx="{m_jup[0]}" cy="{m_jup[1]}" r="22" fill="{m_jup[5]}" stroke="{m_jup[6]}" stroke-width="1.6" stroke-dasharray="2 2" opacity="0.85" />',
            f'  <text x="{m_jup[0]}" y="{m_jup[1]-3}" text-anchor="middle" fill="{m_jup[4]}" font-size="11" font-weight="900">{m_jup[2]}</text>',
            f'  <text x="{m_jup[0]}" y="{m_jup[1]+10}" text-anchor="middle" fill="{m_jup[4]}" font-size="8.5" font-weight="700">{m_jup[3]}</text>',
            f'  <circle cx="{m_sat[0]}" cy="{m_sat[1]}" r="22" fill="{m_sat[5]}" stroke="{m_sat[6]}" stroke-width="1.6" stroke-dasharray="2 2" opacity="0.85" />',
            f'  <text x="{m_sat[0]}" y="{m_sat[1]-3}" text-anchor="middle" fill="{m_sat[4]}" font-size="11" font-weight="900">{m_sat[2]}</text>',
            f'  <text x="{m_sat[0]}" y="{m_sat[1]+10}" text-anchor="middle" fill="{m_sat[4]}" font-size="8.5" font-weight="700">{m_sat[3]}</text>',
            f'  <circle cx="{m_sun[0]}" cy="{m_sun[1]}" r="22" fill="{m_sun[5]}" stroke="{m_sun[6]}" stroke-width="1.6" stroke-dasharray="2 2" opacity="0.85" />',
            f'  <text x="{m_sun[0]}" y="{m_sun[1]-3}" text-anchor="middle" fill="{m_sun[4]}" font-size="11" font-weight="900">{m_sun[2]}</text>',
            f'  <text x="{m_sun[0]}" y="{m_sun[1]+10}" text-anchor="middle" fill="{m_sun[4]}" font-size="8.5" font-weight="700">{m_sun[3]}</text>',
            f'  <circle cx="{m_mer[0]}" cy="{m_mer[1]}" r="20" fill="{m_mer[5]}" stroke="{m_mer[6]}" stroke-width="1.6" stroke-dasharray="2 2" opacity="0.85" />',
            f'  <text x="{m_mer[0]}" y="{m_mer[1]-3}" text-anchor="middle" fill="{m_mer[4]}" font-size="11" font-weight="900">{m_mer[2]}</text>',
            f'  <text x="{m_mer[0]}" y="{m_mer[1]+10}" text-anchor="middle" fill="{m_mer[4]}" font-size="8.5" font-weight="700">{m_mer[3]}</text>',
            f'  <circle cx="{m_lmars[0]}" cy="{m_lmars[1]}" r="18" fill="{m_lmars[4]}" stroke="{m_lmars[5]}" stroke-width="1.2" stroke-dasharray="2 2" opacity="0.85" />',
            f'  <text x="{m_lmars[0]}" y="{m_lmars[1]+4}" text-anchor="middle" fill="{m_lmars[3]}" font-size="9.5" font-weight="800">{m_lmars[2]}</text>',
            f'  <circle cx="{m_umars[0]}" cy="{m_umars[1]}" r="18" fill="{m_umars[4]}" stroke="{m_umars[5]}" stroke-width="1.2" stroke-dasharray="2 2" opacity="0.85" />',
            f'  <text x="{m_umars[0]}" y="{m_umars[1]+4}" text-anchor="middle" fill="{m_umars[3]}" font-size="9.5" font-weight="800">{m_umars[2]}</text>',
            f'  <ellipse cx="{m_rahu[0]}" cy="{m_rahu[1]}" rx="35" ry="25" fill="{m_rahu[4]}" stroke="{m_rahu[5]}" stroke-width="1.2" stroke-dasharray="3 3" opacity="0.7" />',
            f'  <text x="{m_rahu[0]}" y="{m_rahu[1]+4}" text-anchor="middle" fill="{m_rahu[3]}" font-size="10" font-weight="800">{m_rahu[2]}</text>',
            f'  <ellipse cx="{m_ven[0]}" cy="{m_ven[1]}" rx="36" ry="48" fill="{m_ven[5]}" stroke="{m_ven[6]}" stroke-width="1.6" stroke-dasharray="2 2" opacity="0.8" />',
            f'  <text x="{m_ven[0]}" y="{m_ven[1]-3}" text-anchor="middle" fill="{m_ven[4]}" font-size="12" font-weight="900">{m_ven[2]}</text>',
            f'  <text x="{m_ven[0]}" y="{m_ven[1]+11}" text-anchor="middle" fill="{m_ven[4]}" font-size="9" font-weight="700">{m_ven[3]}</text>',
            f'  <ellipse cx="{m_moon[0]}" cy="{m_moon[1]}" rx="36" ry="48" fill="{m_moon[5]}" stroke="{m_moon[6]}" stroke-width="1.6" stroke-dasharray="2 2" opacity="0.8" />',
            f'  <text x="{m_moon[0]}" y="{m_moon[1]-3}" text-anchor="middle" fill="{m_moon[4]}" font-size="12" font-weight="900">{m_moon[2]}</text>',
            f'  <text x="{m_moon[0]}" y="{m_moon[1]+11}" text-anchor="middle" fill="{m_moon[4]}" font-size="9" font-weight="700">{m_moon[3]}</text>',
            f'  <circle cx="{m_ketu[0]}" cy="{m_ketu[1]}" r="16" fill="{m_ketu[4]}" stroke="{m_ketu[5]}" stroke-width="1.2" stroke-dasharray="2 2" opacity="0.85" />',
            f'  <text x="{m_ketu[0]}" y="{m_ketu[1]+4}" text-anchor="middle" fill="{m_ketu[3]}" font-size="9.5" font-weight="800">{m_ketu[2]}</text>',
            '</g>',
            # Main Lines
            '<g id="mainLines" stroke-linecap="round" fill="none">',
            f'  <path d="{heart_path}" stroke="#DC2626" stroke-width="3.8" filter="url(#subtleGlow)" />',
            f'  <text x="{heart_lbl_x}" y="{heart_lbl_y}" text-anchor="{heart_anchor}" fill="#DC2626" font-size="11" font-weight="900">हृदय रेखा</text>',
            f'  <path d="{head_path}" stroke="#2563EB" stroke-width="3.8" />',
            f'  <text x="{head_lbl_x}" y="{head_lbl_y}" text-anchor="{head_anchor}" fill="#2563EB" font-size="11" font-weight="900">मस्तिष्क रेखा</text>',
            f'  <path d="{life_path}" stroke="#059669" stroke-width="4.0" />',
            f'  <text x="{life_lbl_x}" y="{life_lbl_y}" text-anchor="{life_anchor}" fill="#059669" font-size="11" font-weight="900">जीवन रेखा</text>',
            f'  <path d="{fate_path}" stroke="#D97706" stroke-width="3.4" />',
            f'  <text x="{fate_lbl_x}" y="{fate_lbl_y}" text-anchor="middle" fill="#D97706" font-size="11" font-weight="900">भाग्य रेखा</text>',
            f'  <path d="{sun_path}" stroke="#CA8A04" stroke-width="2.8" />',
            f'  <text x="{sun_lbl_x}" y="{sun_lbl_y}" text-anchor="middle" fill="#CA8A04" font-size="9.5" font-weight="900">सूर्य रेखा</text>',
            f'  <path d="{marr_path}" stroke="#E11D48" stroke-width="2.8" />',
            f'  <text x="{marr_lbl_x}" y="{marr_lbl_y}" text-anchor="{heart_anchor}" fill="#E11D48" font-size="9.5" font-weight="800">विवाह</text>',
            '</g>',
            # Age Milestones on Life Line
            '<g id="ageMarkers">',
        ]

        for dot in age_dots:
            svg_parts.append(f'  <circle cx="{dot[0]}" cy="{dot[1]}" r="3.5" fill="#059669" stroke="#FFFFFF" stroke-width="1.2" />')
            svg_parts.append(f'  <text x="{dot[3]}" y="{dot[4]}" fill="#047857" font-size="8.5" font-weight="900">{dot[2]}</text>')
        svg_parts.append('</g>')

        # Wrist Bracelets
        svg_parts.extend([
            '<g id="bracelets" stroke="#0D9488" stroke-width="2.2" stroke-linecap="round" fill="none">',
            f'  <path d="{brc1}" />',
            f'  <text x="{brc_lbl_x}" y="575" fill="#0D9488" font-size="9" font-weight="700">१. आरोग्य</text>',
            f'  <path d="{brc2}" />',
            f'  <text x="{brc_lbl_x}" y="587" fill="#0D9488" font-size="9" font-weight="700">२. संपदा</text>',
            f'  <path d="{brc3}" />' if profile.bracelets_count >= 3 else '',
            f'  <text x="{brc_lbl_x}" y="599" fill="#0D9488" font-size="9" font-weight="700">३. दीर्घायु</text>' if profile.bracelets_count >= 3 else '',
            '</g>',
        ])

        # Sacred Marks
        svg_parts.append('<g id="sacredMarks">')
        if show_yava:
            svg_parts.extend([
                f'  <ellipse cx="{yava_cx}" cy="{yava_cy}" rx="9" ry="5" fill="#FEF3C7" stroke="#B45309" stroke-width="2" />',
                f'  <circle cx="{yava_cx}" cy="{yava_cy}" r="2.5" fill="#B45309" />',
                f'  <text x="{yava_cx}" y="{yava_cy+18}" text-anchor="middle" fill="#B45309" font-size="8.5" font-weight="900">👁️ यव (बुद्ध चक्षु)</text>',
            ])
        if show_cross:
            svg_parts.extend([
                f'  <g transform="translate({cross_x}, {cross_y})">',
                '    <line x1="-7" y1="-7" x2="7" y2="7" stroke="#7C3AED" stroke-width="2.6" stroke-linecap="round" />',
                '    <line x1="7" y1="-7" x2="-7" y2="7" stroke="#7C3AED" stroke-width="2.6" stroke-linecap="round" />',
                '    <text x="12" y="4" fill="#7C3AED" font-size="9" font-weight="900">✨ रहस्यमयी क्रॉस</text>',
                '  </g>',
            ])
        if show_matsya:
            svg_parts.extend([
                f'  <g transform="translate({matsya_x}, {matsya_y})">',
                '    <path d="M -10 -8 C 0 0, 5 5, 10 5 C 5 5, 0 0, -10 8 C -5 2, -5 -2, -10 -8 Z" fill="#FDE68A" stroke="#B45309" stroke-width="1.8" />',
                '    <line x1="-10" y1="-8" x2="-14" y2="-12" stroke="#B45309" stroke-width="1.6" />',
                '    <line x1="-10" y1="8" x2="-14" y2="12" stroke="#B45309" stroke-width="1.6" />',
                '    <text x="14" y="4" fill="#B45309" font-size="9" font-weight="900">🐟 मत्स्य</text>',
                '  </g>',
            ])
        if show_jup_cross:
            svg_parts.extend([
                f'  <g transform="translate({jup_cross_x}, {jup_cross_y})">',
                '    <line x1="-6" y1="-6" x2="6" y2="6" stroke="#059669" stroke-width="2.2" stroke-linecap="round" />',
                '    <line x1="6" y1="-6" x2="-6" y2="6" stroke="#059669" stroke-width="2.2" stroke-linecap="round" />',
                '  </g>',
            ])
        if show_trishul:
            svg_parts.extend([
                f'  <g transform="translate({trishul_x}, {trishul_y})">',
                '    <line x1="0" y1="8" x2="0" y2="-8" stroke="#B45309" stroke-width="2" />',
                '    <path d="M -6 -2 C -6 -6, -2 -8, 0 -4 C 2 -8, 6 -6, 6 -2" fill="none" stroke="#B45309" stroke-width="1.8" />',
                '    <text x="8" y="-4" fill="#B45309" font-size="9" font-weight="900">🔱 त्रिशूल</text>',
                '  </g>',
            ])
        svg_parts.append('</g>')

        # Footer Legend Strip
        svg_parts.extend([
            f'<rect x="20" y="{height-42}" width="{width - 40}" height="32" rx="8" fill="#F8FAFC" stroke="#E2E8F0" />',
            f'<text x="{width//2}" y="{height-22}" text-anchor="middle" fill="#475569" font-size="9.5" font-weight="700">',
            '🟢 जीवन रेखा | 🔵 मस्तिष्क रेखा | 🔴 हृदय रेखा | 🟠 भाग्य रेखा | 🟡 सूर्य रेखा | 🟣 रहस्यमयी क्रॉस | 🟤 यव/मत्स्य',
            '</text>',
            '</svg>'
        ])

        return "\n".join([p for p in svg_parts if p.strip()])
