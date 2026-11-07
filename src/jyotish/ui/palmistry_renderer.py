"""
हस्तरेखा विज़ुअलाइज़र (Interactive High-Definition SVG Palm Renderer)
Renders canonical palm maps with planetary mounts, major/minor lines, age markers, and sacred marks.
"""

from typing import Dict, Any, Optional
from src.jyotish.core.palmistry import PalmInputProfile


class PalmRenderer:
    """
    Renders scalable, crisp, responsive SVG palm diagrams for Vedic Hastarekha.
    """

    @classmethod
    def render_palm_svg(cls, profile: PalmInputProfile, width: int = 560, height: int = 680) -> str:
        """
        Generates full-detail SVG markup representing the native's palm.
        """
        # Sacred marks visibility
        show_yava = profile.has_buddha_eye
        show_cross = profile.has_mystic_cross
        show_matsya = profile.has_matsya_sign
        show_trishul = profile.has_trishul_sign
        show_jup_cross = profile.mount_jupiter.has_cross

        svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="100%" height="{height}" style="background: radial-gradient(circle at 50% 50%, #FFFFFF 0%, #F8FAFC 100%); border: 2px solid #CBD5E1; border-radius: 16px; box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.05); font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">
  <defs>
    <!-- Gradients -->
    <linearGradient id="palmSkinGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#FFF5EB" />
      <stop offset="50%" stop-color="#FFEAD6" />
      <stop offset="100%" stop-color="#FED7AA" />
    </linearGradient>
    <filter id="subtleGlow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="2" stdDeviation="3" flood-color="#D97706" flood-opacity="0.25" />
    </filter>
  </defs>

  <!-- TITLE HEADER -->
  <text x="{width//2}" y="32" text-anchor="middle" fill="#1E293B" font-size="16" font-weight="900" letter-spacing="0.5">
    ✋ शास्त्रीय हस्तरेखा एवं सामुद्रिक हस्त-नक्शा (Vedic Palm Map)
  </text>
  <text x="{width//2}" y="50" text-anchor="middle" fill="#64748B" font-size="11.5" font-weight="600">
    हस्त प्रकार: {profile.hand_type} | अंगूठा: {profile.thumb_type} | त्वचा: {profile.skin_texture}
  </text>

  <!-- BASE HAND SILHOUETTE (PALM & FINGERS) -->
  <g id="handContour">
    <!-- Palm Outline -->
    <path d="M 170 560 
             C 120 540, 90 480, 85 400
             C 80 340, 85 280, 95 240
             C 98 220, 105 170, 115 130
             C 120 100, 145 95, 155 125
             C 165 155, 175 205, 180 230
             C 185 200, 205 70, 220 55
             C 235 45, 255 60, 250 110
             C 245 160, 240 215, 240 230
             C 255 190, 280 85, 298 75
             C 315 65, 335 80, 325 135
             C 315 190, 305 235, 305 250
             C 325 210, 355 145, 375 140
             C 390 135, 405 150, 395 195
             C 380 260, 365 310, 375 350
             C 385 390, 410 440, 405 480
             C 400 520, 370 550, 340 560
             Z" 
          fill="url(#palmSkinGrad)" stroke="#F59E0B" stroke-width="2.5" stroke-linejoin="round" />
          
    <!-- Thumb Contour -->
    <path d="M 95 240
             C 70 270, 45 320, 38 360
             C 30 400, 45 425, 65 410
             C 85 395, 115 345, 125 320"
          fill="url(#palmSkinGrad)" stroke="#F59E0B" stroke-width="2" />
  </g>

  <!-- WRIST BRACELETS (MANIBANDHA REKHAS) -->
  <g id="bracelets" stroke="#0D9488" stroke-width="2.2" stroke-linecap="round" fill="none">
    <path d="M 180 572 C 240 585, 280 585, 330 572" />
    <text x="345" y="575" fill="#0D9488" font-size="9" font-weight="700">१. आरोग्य</text>
    <path d="M 185 584 C 240 597, 280 597, 325 584" />
    <text x="345" y="587" fill="#0D9488" font-size="9" font-weight="700">२. संपदा</text>
    {f'<path d="M 190 596 C 240 608, 280 608, 320 596" /><text x="345" y="599" fill="#0D9488" font-size="9" font-weight="700">३. दीर्घायु</text>' if profile.bracelets_count >= 3 else ''}
  </g>

  <!-- PLANETARY MOUNTS (नवग्रह पर्वत) -->
  <g id="mounts">
    <!-- 1. Jupiter Mount (गुरु) - Under Index Finger -->
    <circle cx="150" cy="250" r="22" fill="#FEF3C7" stroke="#D97706" stroke-width="1.5" stroke-dasharray="2 2" opacity="0.8" />
    <text x="150" y="247" text-anchor="middle" fill="#92400E" font-size="11" font-weight="900">♃ गुरु</text>
    <text x="150" y="260" text-anchor="middle" fill="#B45309" font-size="8.5" font-weight="700">{profile.mount_jupiter.prominence}</text>

    <!-- 2. Saturn Mount (शनि) - Under Middle Finger -->
    <circle cx="215" cy="240" r="22" fill="#E2E8F0" stroke="#475569" stroke-width="1.5" stroke-dasharray="2 2" opacity="0.8" />
    <text x="215" y="237" text-anchor="middle" fill="#1E293B" font-size="11" font-weight="900">♄ शनि</text>
    <text x="215" y="250" text-anchor="middle" fill="#475569" font-size="8.5" font-weight="700">{profile.mount_saturn.prominence}</text>

    <!-- 3. Sun Mount (सूर्य) - Under Ring Finger -->
    <circle cx="280" cy="250" r="22" fill="#FEF9C3" stroke="#CA8A04" stroke-width="1.5" stroke-dasharray="2 2" opacity="0.8" />
    <text x="280" y="247" text-anchor="middle" fill="#854D0E" font-size="11" font-weight="900">☉ सूर्य</text>
    <text x="280" y="260" text-anchor="middle" fill="#A16207" font-size="8.5" font-weight="700">{profile.mount_sun.prominence}</text>

    <!-- 4. Mercury Mount (बुध) - Under Little Finger -->
    <circle cx="340" cy="275" r="20" fill="#DCFCE7" stroke="#16A34A" stroke-width="1.5" stroke-dasharray="2 2" opacity="0.8" />
    <text x="340" y="272" text-anchor="middle" fill="#166534" font-size="11" font-weight="900">☿ बुध</text>
    <text x="340" y="285" text-anchor="middle" fill="#15803D" font-size="8.5" font-weight="700">{profile.mount_mercury.prominence}</text>

    <!-- 5. Lower Mars (निम्न मंगल) - Under Thumb Joint -->
    <circle cx="115" cy="340" r="18" fill="#FEE2E2" stroke="#DC2626" stroke-width="1.2" stroke-dasharray="2 2" opacity="0.8" />
    <text x="115" y="342" text-anchor="middle" fill="#991B1B" font-size="9.5" font-weight="800">♂ नि.मंगल</text>

    <!-- 6. Upper Mars (उच्च मंगल) - Under Mercury -->
    <circle cx="355" cy="355" r="18" fill="#FEE2E2" stroke="#DC2626" stroke-width="1.2" stroke-dasharray="2 2" opacity="0.8" />
    <text x="355" y="357" text-anchor="middle" fill="#991B1B" font-size="9.5" font-weight="800">♂ उ.मंगल</text>

    <!-- 7. Rahu Plain (राहु क्षेत्र) - Palm Hollow Center -->
    <ellipse cx="230" cy="365" rx="35" ry="25" fill="#F3E8FF" stroke="#9333EA" stroke-width="1" stroke-dasharray="3 3" opacity="0.6" />
    <text x="230" y="369" text-anchor="middle" fill="#6B21A8" font-size="10" font-weight="800">☊ राहु गर्त</text>

    <!-- 8. Venus Mount (शुक्र) - Base of Thumb -->
    <ellipse cx="145" cy="445" rx="35" ry="50" fill="#FCE7F3" stroke="#DB2777" stroke-width="1.5" stroke-dasharray="2 2" opacity="0.75" />
    <text x="145" y="443" text-anchor="middle" fill="#9D174D" font-size="12" font-weight="900">♀ शुक्र</text>
    <text x="145" y="457" text-anchor="middle" fill="#BE185D" font-size="9" font-weight="700">{profile.mount_venus.prominence}</text>

    <!-- 9. Moon Mount (चन्द्र) - Percussion Opposite Thumb -->
    <ellipse cx="325" cy="465" rx="35" ry="45" fill="#E0F2FE" stroke="#0284C7" stroke-width="1.5" stroke-dasharray="2 2" opacity="0.75" />
    <text x="325" y="463" text-anchor="middle" fill="#075985" font-size="12" font-weight="900">☽ चन्द्र</text>
    <text x="325" y="477" text-anchor="middle" fill="#0369A1" font-size="9" font-weight="700">{profile.mount_moon.prominence}</text>

    <!-- 10. Ketu Region (केतु) - Above Wrist Center -->
    <circle cx="240" cy="535" r="16" fill="#F1F5F9" stroke="#475569" stroke-width="1.2" stroke-dasharray="2 2" opacity="0.8" />
    <text x="240" y="539" text-anchor="middle" fill="#334155" font-size="9.5" font-weight="800">☋ केतु</text>
  </g>

  <!-- PRIMARY PALM LINES (मुख्य रेखाएं) -->
  <g id="mainLines" stroke-linecap="round" fill="none">
    <!-- 1. HEART LINE (हृदय रेखा) - Crimson Red -->
    <path d="M 370 305 
             C 310 300, 240 305, 185 270 
             C 165 258, 155 250, 150 245" 
          stroke="#DC2626" stroke-width="3.5" filter="url(#subtleGlow)" />
    <text x="382" y="302" fill="#DC2626" font-size="10.5" font-weight="800">हृदय रेखा</text>

    <!-- 2. HEAD LINE (मस्तिष्क रेखा) - Royal Blue -->
    <path d="M 115 315 
             C 160 320, 230 350, 280 375
             C 315 395, 335 415, 345 430" 
          stroke="#2563EB" stroke-width="3.5" />
    <text x="352" y="435" fill="#2563EB" font-size="10.5" font-weight="800">मस्तिष्क रेखा</text>

    <!-- 3. LIFE LINE (जीवन रेखा) - Vibrant Emerald Green -->
    <path d="M 120 310 
             C 140 325, 175 365, 185 415
             C 195 465, 185 520, 215 560" 
          stroke="#059669" stroke-width="3.8" />
    <text x="225" y="565" fill="#059669" font-size="10.5" font-weight="800">जीवन रेखा</text>

    <!-- Age Markers on Life Line -->
    <circle cx="152" cy="345" r="3" fill="#059669" />
    <text x="162" y="347" fill="#047857" font-size="8.5" font-weight="800">२० व.</text>
    <circle cx="180" cy="405" r="3" fill="#059669" />
    <text x="190" y="407" fill="#047857" font-size="8.5" font-weight="800">४० व.</text>
    <circle cx="188" cy="475" r="3" fill="#059669" />
    <text x="198" y="477" fill="#047857" font-size="8.5" font-weight="800">६० व.</text>
    <circle cx="198" cy="535" r="3" fill="#059669" />
    <text x="208" y="537" fill="#047857" font-size="8.5" font-weight="800">८० व.</text>

    <!-- 4. FATE LINE (भाग्य / ऊर्ध्व रेखा) - Rich Amber / Gold -->
    <path d="M 245 540 
             C 240 480, 235 390, 225 320 
             C 220 280, 216 260, 215 245" 
          stroke="#D97706" stroke-width="3.2" stroke-dasharray="0" />
    <text x="228" y="235" fill="#D97706" font-size="10.5" font-weight="800">भाग्य रेखा</text>

    <!-- 5. SUN LINE (सूर्य / विद्या रेखा) - Golden Amber -->
    <path d="M 285 380 C 283 340, 281 295, 280 260" 
          stroke="#CA8A04" stroke-width="2.5" />
    <text x="290" y="275" fill="#CA8A04" font-size="9" font-weight="800">सूर्य रेखा</text>

    <!-- 6. MARRIAGE LINE (विवाह रेखा) - Rose Pink -->
    <path d="M 375 272 L 350 272" stroke="#E11D48" stroke-width="2.8" />
    <text x="382" y="275" fill="#E11D48" font-size="9.5" font-weight="800">विवाह</text>
  </g>

  <!-- SACRED SAMUDRIKA MARKS (शास्त्रीय दिव्य चिन्ह) -->
  <g id="sacredMarks">
    <!-- 1. Yava / Buddha's Eye on Thumb -->
    {f'''
    <!-- Yava Sign -->
    <ellipse cx="62" cy="370" rx="9" ry="5" fill="#FEF3C7" stroke="#B45309" stroke-width="2" />
    <circle cx="62" cy="370" r="2.5" fill="#B45309" />
    <text x="62" y="390" text-anchor="middle" fill="#B45309" font-size="8.5" font-weight="900">👁️ यव (बुद्ध चक्षु)</text>
    ''' if show_yava else ''}

    <!-- 2. Mystic Cross (La Croix Mystique) between Head & Heart Lines -->
    {f'''
    <!-- Mystic Cross -->
    <g transform="translate(250, 325)">
      <line x1="-8" y1="-8" x2="8" y2="8" stroke="#7C3AED" stroke-width="2.6" stroke-linecap="round" />
      <line x1="8" y1="-8" x2="-8" y2="8" stroke="#7C3AED" stroke-width="2.6" stroke-linecap="round" />
      <text x="14" y="4" fill="#7C3AED" font-size="9.5" font-weight="900">✨ रहस्यमयी क्रॉस</text>
    </g>
    ''' if show_cross else ''}

    <!-- 3. Fish Sign (मत्स्य चिन्ह) on Ketu / Wrist -->
    {f'''
    <!-- Matsya Sign -->
    <g transform="translate(242, 515)">
      <path d="M -10 -8 C 0 0, 5 5, 10 5 C 5 5, 0 0, -10 8 C -5 2, -5 -2, -10 -8 Z" fill="#FDE68A" stroke="#B45309" stroke-width="1.8" />
      <line x1="-10" y1="-8" x2="-14" y2="-12" stroke="#B45309" stroke-width="1.6" />
      <line x1="-10" y1="8" x2="-14" y2="12" stroke="#B45309" stroke-width="1.6" />
      <text x="14" y="4" fill="#B45309" font-size="9" font-weight="900">🐟 मत्स्य</text>
    </g>
    ''' if show_matsya else ''}

    <!-- 4. Jupiter Cross (शुभ विवाह व प्रतिष्ठा) -->
    {f'''
    <!-- Jupiter Cross -->
    <g transform="translate(142, 268)">
      <line x1="-6" y1="-6" x2="6" y2="6" stroke="#059669" stroke-width="2.2" stroke-linecap="round" />
      <line x1="6" y1="-6" x2="-6" y2="6" stroke="#059669" stroke-width="2.2" stroke-linecap="round" />
    </g>
    ''' if show_jup_cross else ''}

    <!-- 5. Trident (त्रिशूल) on Saturn / Fate Line Top -->
    {f'''
    <!-- Trishul Sign -->
    <g transform="translate(215, 232)">
      <line x1="0" y1="8" x2="0" y2="-8" stroke="#B45309" stroke-width="2" />
      <path d="M -6 -2 C -6 -6, -2 -8, 0 -4 C 2 -8, 6 -6, 6 -2" fill="none" stroke="#B45309" stroke-width="1.8" />
      <text x="8" y="-4" fill="#B45309" font-size="9" font-weight="900">🔱 त्रिशूल</text>
    </g>
    ''' if show_trishul else ''}
  </g>

  <!-- LEGEND STRIP AT BOTTOM -->
  <rect x="25" y="635" width="{width - 50}" height="32" rx="8" fill="#F8FAFC" stroke="#E2E8F0" />
  <text x="{width//2}" y="655" text-anchor="middle" fill="#475569" font-size="10" font-weight="700">
    🟢 जीवन रेखा | 🔵 मस्तिष्क रेखा | 🔴 हृदय रेखा | 🟠 भाग्य रेखा | 🟡 सूर्य रेखा | 🟣 रहस्यमयी क्रॉस | 🟤 यव/मत्स्य
  </text>
</svg>"""
        return svg
