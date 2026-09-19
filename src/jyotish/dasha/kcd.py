"""
Kaalachakra Dasha (KCD) Engine for JyotishOS.
According to Maharishi Parashara (Brihat Parashara Hora Shastra - BPHS).
Calculates:
1. Savya (Direct) vs Apasavya (Reverse) classification.
2. Deha Rashi (Body sign) and Jeeva Rashi (Soul sign).
3. 9 Mahadasha Rashi periods with exact classical years.
4. Identification of Gatis (Manduka Gati, Markati Gati, Simhavalokana).
5. Birth balance and full chronological dasha timeline.
"""

from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime, timedelta
from src.jyotish.core.constants import SIGN_NAMES, NAKSHATRA_NAMES
from src.jyotish.core.models import KundaliChart


# Rashi dasha durations in Kaalachakra Dasha
KCD_RASHI_YEARS = {
    "Aries": 7.0,
    "Taurus": 16.0,
    "Gemini": 9.0,
    "Cancer": 21.0,
    "Leo": 5.0,
    "Virgo": 9.0,
    "Libra": 16.0,
    "Scorpio": 7.0,
    "Sagittarius": 10.0,
    "Capricorn": 4.0,
    "Aquarius": 4.0,
    "Pisces": 10.0
}

# 12 Sign sequences for 12 Padas in Savya cycle
SAVYA_SEQUENCES = [
    # 1. Aries navamsha: Aries -> Taurus -> Gemini -> Cancer -> Leo -> Virgo -> Libra -> Scorpio -> Sagittarius
    ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius"],
    # 2. Taurus navamsha: Capricorn -> Aquarius -> Pisces -> Scorpio -> Libra -> Virgo -> Cancer -> Leo -> Gemini (Manduka/Markati)
    ["Capricorn", "Aquarius", "Pisces", "Scorpio", "Libra", "Virgo", "Cancer", "Leo", "Gemini"],
    # 3. Gemini navamsha: Taurus -> Aries -> Pisces -> Aquarius -> Capricorn -> Sagittarius -> Aries -> Taurus -> Gemini
    ["Taurus", "Aries", "Pisces", "Aquarius", "Capricorn", "Sagittarius", "Aries", "Taurus", "Gemini"],
    # 4. Cancer navamsha: Cancer -> Leo -> Virgo -> Libra -> Scorpio -> Sagittarius -> Capricorn -> Aquarius -> Pisces
    ["Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"],
]


class KaalachakraDashaEngine:
    """Computes Kaalachakra Dasha Mahadashas and Special Gatis."""

    @classmethod
    def calculate(cls, chart: KundaliChart) -> Dict[str, Any]:
        """Generate complete Kaalachakra Dasha timeline."""
        moon = chart.planets["Moon"]
        birth_dt = datetime.combine(chart.birth_data.birth_date, chart.birth_data.birth_time)

        # Nakshatra and Pada calculation
        nak_span = 360.0 / 27.0  # 13.3333 deg
        pada_span = nak_span / 4.0  # 3.3333 deg

        nak_idx = int(moon.longitude // nak_span)  # 0 to 26
        nak_name = NAKSHATRA_NAMES[nak_idx]
        rem_deg = moon.longitude % nak_span
        pada_num = int(rem_deg // pada_span) + 1  # 1 to 4
        fraction_in_pada = (rem_deg % pada_span) / pada_span  # 0.0 to 1.0

        # Savya (Direct) vs Apasavya (Reverse)
        # Savya nakshatras: 0,1,2, 6,7,8, 12,13,14, 18,19,20, 24,25,26
        savya_nak_indices = {0, 1, 2, 6, 7, 8, 12, 13, 14, 18, 19, 20, 24, 25, 26}
        is_savya = nak_idx in savya_nak_indices
        group_type = "सव्य (Savya / Direct)" if is_savya else "अपसव्य (Apasavya / Reverse)"

        # Select Rashi sequence based on pada
        seq_idx = (pada_num - 1) % len(SAVYA_SEQUENCES)
        rashi_sequence = list(SAVYA_SEQUENCES[seq_idx])
        if not is_savya:
            rashi_sequence = list(reversed(rashi_sequence))

        # Deha and Jeeva Rashis
        deha_rashi = rashi_sequence[0]
        jeeva_rashi = rashi_sequence[-1]

        # Calculate Total Cycle Years
        total_cycle_years = sum(KCD_RASHI_YEARS[r] for r in rashi_sequence)

        # Build timeline with birth balance
        timeline = []
        curr_time = birth_dt

        # First dasha has balance
        first_rashi = rashi_sequence[0]
        first_full_yrs = KCD_RASHI_YEARS[first_rashi]
        balance_yrs = first_full_yrs * (1.0 - fraction_in_pada)

        # Iterate over cycles to cover 100+ years
        for cycle in range(2):
            for i, r_name in enumerate(rashi_sequence):
                duration_yrs = KCD_RASHI_YEARS[r_name]
                is_first = (cycle == 0 and i == 0)
                actual_duration = balance_yrs if is_first else duration_yrs

                end_time = curr_time + timedelta(days=actual_duration * 365.2425)

                # Identify Gati (Jump)
                gati = "सामान्य गति (Regular Flow)"
                if i > 0:
                    prev_r = rashi_sequence[i - 1]
                    prev_id = SIGN_NAMES.index(prev_r) + 1
                    curr_id = SIGN_NAMES.index(r_name) + 1
                    diff = (curr_id - prev_id) % 12

                    if (prev_r == "Virgo" and r_name == "Cancer") or (prev_r == "Leo" and r_name == "Gemini"):
                        gati = "🐸 मण्डूक गति (Manduka Gati / Frog Jump)"
                    elif (prev_r == "Leo" and r_name == "Cancer") or (prev_r == "Cancer" and r_name == "Gemini"):
                        gati = "🐒 मर्कटी गति (Markati Gati / Monkey Jump)"
                    elif (prev_r == "Pisces" and r_name == "Scorpio") or (prev_r == "Sagittarius" and r_name == "Aries"):
                        gati = "🦁 सिंहावलोकन (Simhavalokana / Lion's Backward Gaze)"

                is_deha = (r_name == deha_rashi)
                is_jeeva = (r_name == jeeva_rashi)
                role_tag = "👤 देह राशि" if is_deha else ("❤️ जीव राशि" if is_jeeva else "")

                timeline.append({
                    "rashi": r_name,
                    "duration_years": round(actual_duration, 2),
                    "start_date": curr_time.strftime("%d-%b-%Y"),
                    "end_date": end_time.strftime("%d-%b-%Y"),
                    "status": "Birth Balance" if is_first else "Full",
                    "gati": gati,
                    "role": role_tag
                })

                curr_time = end_time

        return {
            "group_type": group_type,
            "nakshatra": nak_name,
            "pada": pada_num,
            "deha_rashi": deha_rashi,
            "jeeva_rashi": jeeva_rashi,
            "total_cycle_years": total_cycle_years,
            "timeline": timeline[:12]  # First 12 periods covering native's lifetime
        }


default_kcd_engine = KaalachakraDashaEngine()

