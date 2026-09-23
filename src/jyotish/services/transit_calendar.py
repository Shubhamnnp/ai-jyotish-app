"""
Personalized Monthly Astrological Transit Calendar Service for JyotishOS.
Generates an interactive Google-Calendar style monthly grid showing daily personal fortune stars,
lunar transits, planetary ingresses (Rashi transitions), and auspicious festivals.
"""

from typing import Dict, List, Any, Optional
import calendar
from datetime import datetime, date, time, timedelta, timezone
from ..core.ephemeris import PyEphemProvider
from ..core.constants import SIGN_NAMES
from ..core.models import KundaliChart

PLANET_ICONS = {
    "Sun": "☀️",
    "Moon": "🌙",
    "Mars": "⚔️",
    "Mercury": "☿️",
    "Jupiter": "🪐",
    "Venus": "💎",
    "Saturn": "⚖️",
    "Rahu": "🐉",
    "Ketu": "☄️"
}

PLANET_NAMES_HI = {
    "Sun": "सूर्य", "Moon": "चन्द्र", "Mars": "मंगल", "Mercury": "बुध",
    "Jupiter": "गुरु", "Venus": "शुक्र", "Saturn": "शनि", "Rahu": "राहु", "Ketu": "केतु"
}


class PersonalTransitCalendarService:
    """Calculates personalized monthly transit events and daily auspiciousness."""

    def __init__(self):
        self.provider = PyEphemProvider()

    def generate_monthly_calendar(
        self,
        year: int,
        month: int,
        chart: KundaliChart
    ) -> Dict[str, Any]:
        """
        Generates full month transit schedule with daily personal star rating and ingress events.
        """
        natal_moon_sign = chart.planets["Moon"].sign_id if "Moon" in chart.planets else 1
        natal_lagna_id = chart.lagna_sign_id

        num_days = calendar.monthrange(year, month)[1]
        first_weekday = calendar.monthrange(year, month)[0]  # 0=Mon..6=Sun

        days_data = []
        ingress_events = []

        prev_signs: Dict[str, int] = {}

        for d in range(1, num_days + 1):
            cur_date = date(year, month, d)
            dt_noon = datetime.combine(cur_date, time(12, 0)).replace(tzinfo=timezone.utc)
            pos, _ = self.provider.get_planet_positions(dt_noon)

            # Check planet sign changes (Ingress)
            daily_events = []
            for p_name in ["Sun", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]:
                if p_name in pos:
                    s_id = int((pos[p_name]["longitude"] % 360.0) // 30.0) + 1
                    if p_name in prev_signs and prev_signs[p_name] != s_id:
                        h_from_lagna = ((s_id - natal_lagna_id) % 12) + 1
                        sign_name = SIGN_NAMES[s_id - 1]
                        p_hi = PLANET_NAMES_HI.get(p_name, p_name)
                        ev_str = f"{p_hi} का {sign_name} राशि में प्रवेश (भाव {h_from_lagna})"
                        daily_events.append(f"{PLANET_ICONS.get(p_name, '')} {ev_str}")
                        ingress_events.append({
                            "date": cur_date.strftime("%d %b %Y"),
                            "event": ev_str,
                            "planet": p_name,
                            "sign": sign_name,
                            "house": h_from_lagna
                        })
                    prev_signs[p_name] = s_id

            # Moon & Sun positions for Tithi and Chandra Balam
            m_lon = pos.get("Moon", {}).get("longitude", 0.0)
            s_lon = pos.get("Sun", {}).get("longitude", 0.0)

            tithi_num = int(((m_lon - s_lon) % 360.0) // 12.0) + 1
            moon_sign = int((m_lon % 360.0) // 30.0) + 1

            # Tithi description & Parva
            paksha = "शुक्ल" if tithi_num <= 15 else "कृष्ण"
            t_in_paksha = tithi_num if tithi_num <= 15 else (tithi_num - 15)
            
            tithi_label = f"{paksha} {t_in_paksha}"
            if tithi_num == 15:
                tithi_label = "🌕 पूर्णिमा (Purnima)"
                daily_events.append("🌕 पूर्णिमा पावन पर्व")
            elif tithi_num == 30:
                tithi_label = "🌑 अमावस्या (Amavasya)"
                daily_events.append("🌑 अमावस्या")
            elif tithi_num in [11, 26]:
                daily_events.append("🚩 एकादशी व्रत")
            elif tithi_num in [13, 28]:
                daily_events.append("🔱 प्रदोष व्रत")

            # Chandra Balam & Personal Fortune Stars (1 to 5)
            h_from_moon = ((moon_sign - natal_moon_sign) % 12) + 1

            if h_from_moon in [11, 3, 6, 10]:
                stars = 5
                fortune_status = "उत्कृष्ट कार्य सिद्धि (Highly Favorable)"
                status_color = "#15803D"
                bg_card = "#F0FDF4"
            elif h_from_moon in [1, 2, 5, 7, 9]:
                stars = 4
                fortune_status = "शुभ व सामान्य अनुकूल (Good & Peaceful)"
                status_color = "#2563EB"
                bg_card = "#EFF6FF"
            elif h_from_moon in [4]:
                stars = 2
                fortune_status = "कंटक चंद्र / मानसिक अशांति (Caution in Travel)"
                status_color = "#D97706"
                bg_card = "#FFFBEB"
            else:  # 8, 12
                stars = 1
                fortune_status = "अष्टम/व्यय चंद्र (Avoid Big Investments)"
                status_color = "#DC2626"
                bg_card = "#FEF2F2"

            days_data.append({
                "day": d,
                "date_str": cur_date.strftime("%d %b"),
                "weekday": cur_date.strftime("%a"),
                "weekday_num": cur_date.weekday(),  # 0=Mon..6=Sun
                "tithi": tithi_label,
                "moon_sign": SIGN_NAMES[moon_sign - 1],
                "moon_house": h_from_moon,
                "stars": stars,
                "fortune_status": fortune_status,
                "status_color": status_color,
                "bg_card": bg_card,
                "events": daily_events
            })

        month_name = calendar.month_name[month]
        kpi = {
            "high_fortune_days": [d["day"] for d in days_data if d["stars"] >= 4],
            "caution_days": [d["day"] for d in days_data if d["stars"] <= 2],
            "ingress_count": len(ingress_events)
        }
        return {
            "year": year,
            "month": month,
            "month_name": month_name,
            "native_name": chart.birth_data.name,
            "janma_rashi": chart.planets["Moon"].sign_name if "Moon" in chart.planets else "—",
            "days": days_data,
            "first_weekday": first_weekday,
            "ingress_events": ingress_events,
            "kpi": kpi
        }

    @classmethod
    def render_calendar_html(cls, cal_data: Dict[str, Any]) -> str:
        """Renders interactive 7-column monthly calendar grid."""
        days = cal_data["days"]
        month_name = cal_data["month_name"]
        year = cal_data["year"]
        native = cal_data["native_name"]
        rashi = cal_data["janma_rashi"]

        # Days of week headers (Sun to Sat)
        headers = ["रविवार (Sun)", "सोमवार (Mon)", "मंगलवार (Tue)", "बुधवार (Wed)", "गुरुवार (Thu)", "शुक्रवार (Fri)", "शनिवार (Sat)"]

        # Re-index first_weekday from Monday=0 to Sunday=0:
        # In Python, Monday is 0. Sunday is 6.
        # If Sunday is first col: (first_weekday + 1) % 7
        start_pad = (cal_data["first_weekday"] + 1) % 7

        html = [
            f'<div style="background:#FFFFFF; border:1.5px solid #CBD5E1; border-radius:12px; padding:18px; box-shadow:0 4px 15px rgba(0,0,0,0.06); font-family:-apple-system,BlinkMacSystemFont,sans-serif;">',
            f'<div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:14px; border-bottom:1.5px solid #E2E8F0; padding-bottom:10px;">',
            f'  <div><h3 style="margin:0; color:#0F172A; font-size:18px; font-weight:900;">📅 {month_name} {year} — व्यक्तिगत गोचर पंचांग</h3>',
            f'  <small style="color:#64748B;">जातक: <b>{native}</b> | जन्म राशि: <b style="color:#2563EB;">{rashi}</b></small></div>',
            f'  <div style="font-size:12px; font-weight:700;">🟢 ५★ श्रेष्ठ | 🔵 ४★ शुभ | 🟡 २★ कंटक | 🔴 १★ अष्टम चंद्र</div>',
            f'</div>',
            f'<div style="display:grid; grid-template-columns: repeat(7, 1fr); gap:6px;">'
        ]

        # Header Row
        for h in headers:
            html.append(f'<div style="background:#0F172A; color:#FFFFFF; text-align:center; padding:8px 4px; border-radius:6px; font-size:11.5px; font-weight:800;">{h}</div>')

        # Empty padding cells before 1st of month
        for _ in range(start_pad):
            html.append('<div style="background:#F8FAFC; border:1px dashed #E2E8F0; border-radius:6px; min-height:85px;"></div>')

        # Day cells
        for d in days:
            stars_str = "⭐" * d["stars"]
            ev_html = ""
            for ev in d["events"][:2]:
                ev_html += f'<div style="background:#FFFFFF; border:1px solid #CBD5E1; border-radius:3px; padding:1px 4px; font-size:10px; margin-top:2px; font-weight:700; color:#0F172A; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;">{ev}</div>'

            html.append(f"""
            <div style="background:{d['bg_card']}; border:1.5px solid {d['status_color']}; border-radius:8px; padding:6px; min-height:92px; display:flex; flex-direction:column; justify-content:space-between;">
                <div>
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <b style="font-size:14px; color:#0F172A;">{d['day']}</b>
                        <span style="font-size:9.5px; color:{d['status_color']}; font-weight:800;">{stars_str}</span>
                    </div>
                    <div style="font-size:10px; color:#475569; margin-top:1px;">{d['tithi']}</div>
                    <div style="font-size:10px; color:#64748B;">चन्द्र: <b>{d['moon_sign']}</b> ({d['moon_house']}वां)</div>
                    {ev_html}
                </div>
            </div>
            """)

        html.append('</div></div>')
        return "".join(html)


default_transit_calendar_service = PersonalTransitCalendarService()
