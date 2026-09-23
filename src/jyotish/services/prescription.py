"""
Astrologer Consultation Prescription Slip Service for JyotishOS.
Generates an official, doctor-style 1-page astrological prescription with
prescribed gems, strictly prohibited gems, mantra sadhana, charity, daily routine,
and a quarterly transit precaution. Printable as A4 or shareable via WhatsApp.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, date

try:
    from ..core.constants import SIGN_NAMES, SIGN_LORDS, NATURAL_FRIENDS, NATURAL_ENEMIES
    from ..core.models import KundaliChart
except (ImportError, ValueError):
    from src.jyotish.core.constants import SIGN_NAMES, SIGN_LORDS, NATURAL_FRIENDS, NATURAL_ENEMIES
    from src.jyotish.core.models import KundaliChart

GEMSTONE_DATA = {
    "Sun": {"gem": "माणिक्य (Ruby)", "sub": "गार्नेट / लाल तुरमली", "metal": "स्वर्ण (Gold) अथवा तांबा", "finger": "अनामिका (Ring Finger)", "day": "रविवार प्रातः", "mantra": "ॐ घृणिः सूर्याय नमः (७,००० जप)"},
    "Moon": {"gem": "सच्चा मोती (Natural Pearl)", "sub": "मूनस्टोन (Moonstone)", "metal": "चांदी (Silver)", "finger": "कनिष्ठिका (Little Finger)", "day": "सोमवार संध्याकाल", "mantra": "ॐ सों सोमाय नमः (११,००० जप)"},
    "Mars": {"gem": "लाल मूंगा (Red Coral)", "sub": "कार्नेलियन", "metal": "स्वर्ण अथवा तांबा", "finger": "अनामिका (Ring Finger)", "day": "मंगलवार प्रातः", "mantra": "ॐ क्रां क्रीं क्रौं सः भौमाय नमः (१०,००० जप)"},
    "Mercury": {"gem": "पन्ना (Emerald)", "sub": "ओनेक्स / पेरीडॉट", "metal": "स्वर्ण अथवा चांदी", "finger": "कनिष्ठिका (Little Finger)", "day": "बुधवार प्रातः", "mantra": "ॐ ब्रां ब्रीं ब्रौं सः बुधाय नमः (९,००० जप)"},
    "Jupiter": {"gem": "पीला पुखराज (Yellow Sapphire)", "sub": "सुनहला (Citrine) / पीला टोपाज", "metal": "स्वर्ण (Gold) अथवा पीतल", "finger": "तर्जनी (Index Finger)", "day": "गुरुवार प्रातः", "mantra": "ॐ ग्रां ग्रीं ग्रौं सः गुरवे नमः (१९,००० जप)"},
    "Venus": {"gem": "हीरा / ओपल (Diamond / White Opal)", "sub": "अमेरिकन डायमंड / जरकन", "metal": "प्लेटिनम अथवा चांदी", "finger": "मध्यमा अथवा कनिष्ठिका", "day": "शुक्रवार प्रातः", "mantra": "ॐ द्रां द्रीं द्रौं सः शुक्राय नमः (१६,००० जप)"},
    "Saturn": {"gem": "नीलम (Blue Sapphire)", "sub": "जमुनिया (Amethyst) / कटैला", "metal": "पंचधातु अथवा चांदी", "finger": "मध्यमा (Middle Finger)", "day": "शनिवार संध्या", "mantra": "ॐ प्रां प्रीं प्रौं सः शनैश्चराय नमः (२३,००० जप)"},
    "Rahu": {"gem": "गोमेद (Hessonite)", "sub": "तुरमली", "metal": "अष्टधातु अथवा चांदी", "finger": "मध्यमा (Middle Finger)", "day": "शनिवार रात्रि", "mantra": "ॐ भ्रां भ्रीं भ्रौं सः राहवे नमः (१८,००० जप)"},
    "Ketu": {"gem": "लहसुनिया (Cat's Eye)", "sub": "टाइगर आई", "metal": "पंचधातु अथवा चांदी", "finger": "कनिष्ठिका (Little Finger)", "day": "मंगलवार रात्रि", "mantra": "ॐ स्रां स्रीं स्रौं सः केतवे नमः (१७,००० जप)"},
}

CHARITY_DATA = {
    "Sun": "तांबे का पात्र, गेहूं, गुड़, लाल वस्त्र, केशर का रविवार को दान।",
    "Moon": "दूध, चावल, चांदी, सफेद वस्त्र, चीनी, जलपात्र का सोमवार को दान।",
    "Mars": "मसूर दाल, गुड़, तांबा, लाल वस्त्र, सिंदूर, रक्तचंदन का मंगलवार को दान।",
    "Mercury": "हरी मूंग दाल, हरे वस्त्र, कांस्य पात्र, हरी सब्जियां, फल का बुधवार को दान।",
    "Jupiter": "चना दाल, हल्दी, पीले वस्त्र, पपीता, धार्मिक पुस्तकें, स्वर्ण का गुरुवार को दान।",
    "Venus": "खीर, सफेद चंदन, इत्र, मिश्री, घी, कपूर, रेशमी वस्त्र का शुक्रवार को दान।",
    "Saturn": "काले उड़द, काले तिल, सरसों का तेल, लोहा, चमड़े का सामान, कंबल का शनिवार को दान।",
    "Rahu": "नारियल, कंबल, उड़द, तिल, नीले वस्त्र, सिक्के का शनिवार या राहुकाल में दान।",
    "Ketu": "सफेद व काले दोरंगे कंबल, तिल, नींबू, ध्वज, भोजन का मंगलवार या गुरुवार को दान।",
}


class ConsultationSlipService:
    """Generates 1-page clinical astrology consultation prescription slip."""

    @classmethod
    def generate_prescription(cls, chart: KundaliChart) -> Dict[str, Any]:
        """Synthesizes chart into a structured, actionable 1-page prescription."""
        planets = chart.planets
        lagna_sign_id = chart.lagna_sign_id
        lagna_sign_name = chart.lagna_sign_name

        def get_lord(h_num: int) -> str:
            s_id = ((lagna_sign_id - 1 + (h_num - 1)) % 12) + 1
            return SIGN_LORDS[SIGN_NAMES[s_id - 1]]

        l1 = get_lord(1)
        l5 = get_lord(5)
        l9 = get_lord(9)
        l6 = get_lord(6)
        l8 = get_lord(8)
        l12 = get_lord(12)
        l2 = get_lord(2)
        l7 = get_lord(7)

        # 1. Primary Gemstone (Lagna Lord or 9th Lord)
        # If Lagnesh is strong, recommend Lagna gem; else 9th lord (Bhagyoday)
        primary_planet = l1
        if planets[l1].dignity in ["debilitated"] or planets[l1].house_from_lagna in [6, 8, 12]:
            primary_planet = l9 if l9 not in [l6, l8, l12] else l5

        primary_gem_info = GEMSTONE_DATA.get(primary_planet, GEMSTONE_DATA["Jupiter"])

        # 2. Secondary Gemstone (5th Lord / 9th Lord)
        sec_planet = l9 if primary_planet != l9 else l5
        sec_gem_info = GEMSTONE_DATA.get(sec_planet, GEMSTONE_DATA["Sun"])

        # 3. Strictly Prohibited Gemstones (Dusthana + Maraka lords inimical to Lagnesh)
        prohibited_planets = []
        for p in [l6, l8, l12, l2, l7]:
            if p not in [l1, l5, l9]:
                if p not in prohibited_planets and p not in ["Rahu", "Ketu"]:
                    prohibited_planets.append(p)

        prohibited_gems = []
        for p in prohibited_planets[:3]:
            g_data = GEMSTONE_DATA.get(p)
            if g_data:
                prohibited_gems.append({
                    "planet": p,
                    "gem": g_data["gem"],
                    "reason": f"{p} कुण्डली में प्रतिकूल/मारक भावेश है, इसका रत्न जीवन में अवरोध व कष्ट बढ़ा सकता है।"
                })

        # 4. Prescribed Mantras
        # Ishta / Dasha Lord mantra
        current_dasha_lord = "Jupiter"
        if hasattr(chart, "dasha_hierarchy") and chart.dasha_hierarchy:
            current_dasha_lord = chart.dasha_hierarchy.get("mahadasha", "Jupiter")
        elif "Saturn" in planets:
            current_dasha_lord = "Saturn"

        mantra_list = [
            {
                "deity": f"इष्ट व आत्मकारक साधना ({chart.atmakaraka})",
                "mantra": f"ॐ नमो नारायणाय अथवा {GEMSTONE_DATA.get(chart.atmakaraka, {}).get('mantra', 'गायत्री मंत्र')}",
                "count": "नित्य १०८ बार (१ माला प्रातःकाल)",
                "purpose": "आत्मबल, मानसिक शांति व ईश्वरीय कृपा प्राप्ति हेतु"
            },
            {
                "deity": f"सक्रिय महादशा स्वामी ({current_dasha_lord})",
                "mantra": GEMSTONE_DATA.get(current_dasha_lord, {}).get("mantra", "महामृत्युंजय मंत्र"),
                "count": "नित्य १०८ बार (संध्याकाल)",
                "purpose": f"वर्तमान {current_dasha_lord} महादशा के शुभ फलों में वृद्धि एवं अनिष्ट शमन"
            }
        ]

        # 5. Charity & Offerings (Afflicted planet)
        afflicted_p = l6 if l6 not in [l1, l9] else (l8 if l8 not in [l1, l9] else "Saturn")
        charity_info = {
            "planet": afflicted_p,
            "items": CHARITY_DATA.get(afflicted_p, "काले तिल, तेल, कंबल व भोजन का शनिवार को दान।"),
            "when": f"{afflicted_p} के वार को अथवा प्रदोष काल में",
            "recipient": "किसी वृद्ध, असहाय, दिव्यांग अथवा मंदिर के पुजारी को"
        }

        # 6. Daily Routine & Fasting
        fast_day_map = {"Sun": "रविवार", "Moon": "सोमवार", "Mars": "मंगलवार", "Mercury": "बुधवार", "Jupiter": "गुरुवार", "Venus": "शुक्रवार", "Saturn": "शनिवार"}
        prescribed_fast_day = fast_day_map.get(primary_planet, "गुरुवार")

        # 7. Quarterly Transit Precaution (Next 90 Days)
        caution_text = f"आगामी ३ माह में {current_dasha_lord} की दशा एवं गोचर प्रभाव के कारण वित्तीय लेन-देन में जल्दबाजी से बचें। नियमित सूर्य नमस्कार एवं सात्विक आहार रखने से भाग्य का पूरा सहयोग मिलेगा।"

        return {
            "native_name": chart.birth_data.name,
            "birth_date": str(chart.birth_data.birth_date),
            "birth_time": str(chart.birth_data.birth_time),
            "city": chart.birth_data.city,
            "lagna": f"{lagna_sign_name} ({chart.lagna_degree:.2f}°)",
            "moon_sign": chart.planets["Moon"].sign_name if "Moon" in planets else "—",
            "nakshatra": chart.panchang.nakshatra_name if hasattr(chart, "panchang") else "—",
            "atmakaraka": chart.atmakaraka,
            "mahadasha": current_dasha_lord,
            "primary_gem": {
                "planet": primary_planet,
                "role": "जीवन व मुख्य भाग्य रत्न",
                **primary_gem_info,
                "ratti": f"५.२५ से ६.२५ रत्ती (Carats)"
            },
            "secondary_gem": {
                "planet": sec_planet,
                "role": "सहायक उन्नति रत्न",
                **sec_gem_info,
                "ratti": f"४.२५ से ५.२५ रत्ती"
            },
            "prohibited_gems": prohibited_gems,
            "mantras": mantra_list,
            "charity": charity_info,
            "lifestyle": {
                "fast_day": prescribed_fast_day,
                "morning_ritual": "सूर्योदय के समय तांबे के लोटे से सूर्य को कुमकुम-मिश्रित जल अर्पित करें।",
                "favorable_color": "श्वेत, पीला व हल्का केसरिया",
                "unfavorable_color": "गहरा काला व नीला"
            },
            "quarterly_caution": caution_text
        }

    @classmethod
    def generate_whatsapp_text(cls, p_data: Dict[str, Any]) -> str:
        """Formats the prescription into WhatsApp markdown."""
        lines = [
            f"🔮 *ज्योतिषीय परामर्श एवं उपाय पर्चा (Consultation Slip)* 🔮",
            f"👤 *जातक:* {p_data['native_name']} | *लग्न:* {p_data['lagna']} | *राशि:* {p_data['moon_sign']}",
            f"🪐 *सक्रिय महादशा:* {p_data['mahadasha']} | *आत्मकारक:* {p_data['atmakaraka']}",
            f"━━━━━━━━━━━━━━━━━━",
            f"💎 *१. धारण योग्य रत्न (Prescribed Gems):*",
            f"• *मुख्य रत्न:* {p_data['primary_gem']['gem']} ({p_data['primary_gem']['ratti']})",
            f"  - धातु: {p_data['primary_gem']['metal']} | अंगुली: {p_data['primary_gem']['finger']}",
            f"  - दिन: {p_data['primary_gem']['day']}",
            f"• *सहायक रत्न:* {p_data['secondary_gem']['gem']} ({p_data['secondary_gem']['ratti']})",
            f"",
            f"🚫 *२. सख्त वर्जित रत्न (Do NOT Wear):*",
        ]
        for pg in p_data.get("prohibited_gems", []):
            lines.append(f"❌ {pg['gem']} ({pg['planet']}) — {pg['reason']}")

        lines.extend([
            f"",
            f"📿 *३. वैदिक मंत्र जप (Daily Sadhana):*",
        ])
        for m in p_data.get("mantras", []):
            lines.append(f"• *{m['deity']}:* {m['mantra']} ({m['count']})")

        lines.extend([
            f"",
            f"🎁 *४. अनिष्ट शांति दान (Charity):*",
            f"• *सामग्री:* {p_data['charity']['items']}",
            f"• *समय:* {p_data['charity']['when']} | *पात्र:* {p_data['charity']['recipient']}",
            f"",
            f"🧘 *५. दिनचर्या एवं उपवास:*",
            f"• *अनुकूल व्रत वार:* {p_data['lifestyle']['fast_day']}",
            f"• *प्रातः नियम:* {p_data['lifestyle']['morning_ritual']}",
            f"• *शुभ रंग:* {p_data['lifestyle']['favorable_color']} | *अशुभ रंग:* {p_data['lifestyle']['unfavorable_color']}",
            f"",
            f"⚠️ *विशेष त्रैमासिक चेतावनी:* {p_data['quarterly_caution']}",
            f"━━━━━━━━━━━━━━━━━━",
            f"✨ _AI JyotishOS Certified Vedic Consultation_"
        ])
        return "\n".join(lines)

    @classmethod
    def render_prescription_html(
        cls,
        p_data: Dict[str, Any],
        astro_name: str = "ज्योतिषाचार्य पं. शुभम तिवारी",
        astro_center: str = "वैदिक ज्योतिष अनुसंधान केंद्र",
        astro_contact: str = "+91-9452155742"
    ) -> str:
        """Renders clean, high-contrast, printable 1-page HTML card."""
        prohibited_html = ""
        for pg in p_data.get("prohibited_gems", []):
            prohibited_html += f"""
            <div style="background:#FEF2F2; border-left:3.5px solid #DC2626; padding:6px 10px; margin-bottom:6px; border-radius:4px;">
                <b style="color:#991B1B; font-size:12.5px;">❌ {pg['gem']} ({pg['planet']}):</b>
                <span style="color:#1E293B; font-size:12px;">{pg['reason']}</span>
            </div>
            """

        mantras_html = ""
        for m in p_data.get("mantras", []):
            mantras_html += f"""
            <div style="background:#F0FDF4; border-left:3.5px solid #16A34A; padding:6px 10px; margin-bottom:6px; border-radius:4px;">
                <b style="color:#166534; font-size:12.5px;">🕉️ {m['deity']}:</b> <span style="font-weight:700; color:#0F172A;">{m['mantra']}</span><br/>
                <small style="color:#475569;">संख्या: {m['count']} | उद्देश्य: {m['purpose']}</small>
            </div>
            """

        html = f"""
        <div id="jyotish-prescription-slip" style="background:#FFFFFF; border:2px solid #0F172A; border-radius:12px; padding:22px; max-width:820px; margin:0 auto; font-family:-apple-system,BlinkMacSystemFont,sans-serif; color:#0F172A; box-shadow:0 6px 20px rgba(0,0,0,0.08);">
            <!-- Header -->
            <div style="display:flex; justify-content:space-between; align-items:center; border-bottom:2px solid #0F172A; padding-bottom:12px; margin-bottom:14px;">
                <div>
                    <h2 style="margin:0; color:#0F172A; font-size:20px; font-weight:900; letter-spacing:0.5px;">📜 ज्योतिषीय परामर्श एवं उपाय पत्र</h2>
                    <span style="color:#0F172A; font-size:13px; font-weight:800;">{astro_name}</span> &nbsp;|&nbsp; <span style="color:#64748B; font-size:12px;">{astro_center} ({astro_contact})</span>
                </div>
                <div style="text-align:right;">
                    <span style="background:#0F172A; color:#FFFFFF; padding:4px 10px; border-radius:6px; font-size:11px; font-weight:800;">गोपनीय परामर्श</span><br/>
                    <small style="color:#64748B;">दिनांक: {datetime.now().strftime('%d %b %Y')}</small>
                </div>
            </div>

            <!-- Client Info Grid -->
            <div style="background:#F8FAFC; border:1px solid #E2E8F0; border-radius:8px; padding:10px 14px; margin-bottom:14px; display:grid; grid-template-columns: repeat(4, 1fr); gap:8px; font-size:12.5px;">
                <div><b>👤 जातक:</b> {p_data['native_name']}</div>
                <div><b>🏛️ लग्न:</b> {p_data['lagna']}</div>
                <div><b>🌙 राशि:</b> {p_data['moon_sign']} ({p_data['nakshatra']})</div>
                <div><b>🪐 महादशा:</b> {p_data['mahadasha']}</div>
            </div>

            <!-- Gemstones Grid -->
            <div style="margin-bottom:14px;">
                <div style="background:#EFF6FF; border:1.5px solid #93C5FD; border-radius:8px; padding:12px; margin-bottom:10px;">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <b style="color:#1D4ED8; font-size:14px;">💎 १. मुख्य जीवन रत्न: {p_data['primary_gem']['gem']}</b>
                        <span style="background:#DBEAFE; color:#1E40AF; padding:2px 8px; border-radius:4px; font-size:11px; font-weight:800;">{p_data['primary_gem']['ratti']}</span>
                    </div>
                    <div style="font-size:12.5px; color:#1E293B; margin-top:6px; line-height:1.5;">
                        • <b>धातु:</b> {p_data['primary_gem']['metal']} &nbsp;|&nbsp; 
                        • <b>अंगुली:</b> {p_data['primary_gem']['finger']} &nbsp;|&nbsp; 
                        • <b>धारण समय:</b> {p_data['primary_gem']['day']}
                    </div>
                    <div style="font-size:12px; color:#475569; margin-top:3px;">
                        • <b>प्राण-प्रतिष्ठा मंत्र:</b> {p_data['primary_gem']['mantra']}
                    </div>
                </div>

                <div style="background:#FAF5FF; border:1.5px solid #D8B4FE; border-radius:8px; padding:10px 12px; margin-bottom:10px; font-size:12.5px;">
                    <b style="color:#7E22CE;">🌸 सहायक रत्न:</b> {p_data['secondary_gem']['gem']} ({p_data['secondary_gem']['ratti']}) — धातु: {p_data['secondary_gem']['metal']}, अंगुली: {p_data['secondary_gem']['finger']}
                </div>

                <!-- Prohibited Gems -->
                <div>
                    <b style="color:#DC2626; font-size:12.5px;">🚫 भूलकर भी धारण न करें (Strictly Prohibited Gems):</b>
                    <div style="margin-top:5px;">
                        {prohibited_html}
                    </div>
                </div>
            </div>

            <!-- Mantras & Charity 2-Col -->
            <div style="display:grid; grid-template-columns: 1fr 1fr; gap:12px; margin-bottom:14px;">
                <div>
                    <b style="color:#0F172A; font-size:13px;">📿 २. दैनिक वैदिक मंत्र जप:</b>
                    <div style="margin-top:6px;">
                        {mantras_html}
                    </div>
                </div>
                <div>
                    <b style="color:#0F172A; font-size:13px;">🎁 ३. अनिष्ट शांति दान विधान:</b>
                    <div style="background:#FFFBEB; border:1.5px solid #FDE68A; border-radius:6px; padding:10px; margin-top:6px; font-size:12px; line-height:1.5;">
                        <b>सामग्री:</b> {p_data['charity']['items']}<br/>
                        <b>समय:</b> {p_data['charity']['when']}<br/>
                        <b>पात्र:</b> {p_data['charity']['recipient']}
                    </div>
                    <div style="margin-top:8px; font-size:12px; background:#F8FAFC; padding:8px 10px; border-radius:6px; border:1px solid #E2E8F0;">
                        <b>🧘 साप्ताहिक व्रत:</b> {p_data['lifestyle']['fast_day']} &nbsp;|&nbsp; <b>शुभ रंग:</b> {p_data['lifestyle']['favorable_color']}
                    </div>
                </div>
            </div>

            <!-- Quarterly Caution Footer -->
            <div style="background:#FEF2F2; border:1px solid #FCA5A5; border-radius:8px; padding:10px 14px; font-size:12px; color:#1E293B;">
                <b style="color:#B91C1C;">⚠️ आगामी ९० दिनों की विशेष सावधानी:</b> {p_data['quarterly_caution']}
            </div>

            <div style="text-align:center; margin-top:14px; font-size:11px; color:#64748B; border-top:1px dashed #CBD5E1; padding-top:8px;">
                नोट: यह परामर्श पत्र पाराशरीय सिद्धांतों व ग्रहों के कार्याधिपत्य के आधार पर तैयार किया गया है। रत्न धारण से पूर्व प्राण-प्रतिष्ठा अवश्य कराएं।
            </div>
        </div>
        """
        return html


default_prescription_service = ConsultationSlipService()
