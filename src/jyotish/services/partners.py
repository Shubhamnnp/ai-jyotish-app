"""
Business Partnership and Multi-Chart Synastry Service for JyotishOS.
Analyzes mutual financial integrity, leadership synergy, legal dispute risk,
and long-term business viability between two or more charts based on BPHS and Prashna Marga.
"""

from typing import Dict, List, Any, Optional
from ..core.constants import SIGN_NAMES, SIGN_LORDS, NATURAL_FRIENDS, NATURAL_ENEMIES
from ..core.models import KundaliChart


class BusinessPartnershipService:
    """Evaluates business compatibility and partnership longevity between two charts."""

    @classmethod
    def evaluate_partnership(
        cls,
        chart_a: KundaliChart,
        chart_b: KundaliChart,
        name_a: str = "साझेदार १ (Partner A)",
        name_b: str = "साझेदार २ (Partner B)"
    ) -> Dict[str, Any]:
        """
        Analyzes partnership across 4 pillars:
        1. Financial Integrity & Gains (२रा व ११वां भाव)
        2. Leadership & Complementary Roles (१०वां भाव, सूर्य, मंगल, बुध)
        3. Conflict, Ego & Legal Risk (६ठा व ८वां भाव, षडाष्टक)
        4. Partnership Longevity (७वां व ९वां भाव)
        """
        planets_a = chart_a.planets
        planets_b = chart_b.planets
        lagna_a = chart_a.lagna_sign_id
        lagna_b = chart_b.lagna_sign_id

        def get_lord(chart: KundaliChart, h_num: int) -> str:
            s_id = ((chart.lagna_sign_id - 1 + (h_num - 1)) % 12) + 1
            return SIGN_LORDS[SIGN_NAMES[s_id - 1]]

        l1_a, l1_b = get_lord(chart_a, 1), get_lord(chart_b, 1)
        l2_a, l2_b = get_lord(chart_a, 2), get_lord(chart_b, 2)
        l7_a, l7_b = get_lord(chart_a, 7), get_lord(chart_b, 7)
        l10_a, l10_b = get_lord(chart_a, 10), get_lord(chart_b, 10)
        l11_a, l11_b = get_lord(chart_a, 11), get_lord(chart_b, 11)

        # -------------------------------------------------------------
        # Pillar 1: Financial Trust & Profit Synergy (0-25 pts)
        # -------------------------------------------------------------
        fin_score = 12
        fin_reasons = []

        # Check 2nd and 11th lords friendship
        if l11_b in NATURAL_FRIENDS.get(l11_a, []):
            fin_score += 6
            fin_reasons.append(f"दोनों के लाभेश ({l11_a} व {l11_b}) में स्वाभाविक मित्रता है (लाभ व आय में वृद्धि)।")
        elif l11_b in NATURAL_ENEMIES.get(l11_a, []):
            fin_score -= 4
            fin_reasons.append(f"दोनों के लाभेश ({l11_a} व {l11_b}) में शत्रुता है (मुनाफे के बंटवारे में असहजता)।")

        if l2_b in NATURAL_FRIENDS.get(l2_a, []):
            fin_score += 4
            fin_reasons.append("धनेशों में मित्रता वित्तीय पारदर्शिता व विश्वास को मजबूत करती है।")

        # Distance between Moon signs
        moon_dist = ((chart_b.planets["Moon"].sign_id - chart_a.planets["Moon"].sign_id) % 12) + 1
        if moon_dist in [1, 5, 9, 11, 3]:
            fin_score += 3
            fin_reasons.append("चन्द्र राशियों का त्रिकोण/एकादश संबंध धन के प्रवाह को सुगम बनाता है।")
        elif moon_dist in [6, 8, 12]:
            fin_score -= 4
            fin_reasons.append("चन्द्र राशियों में षडाष्टक/व्यय संबंध होने से आकस्मिक व्यय व वित्तीय असमंजस का भय रहता है।")

        fin_score = min(25, max(4, fin_score))

        # -------------------------------------------------------------
        # Pillar 2: Leadership & Complementary Roles (0-25 pts)
        # -------------------------------------------------------------
        lead_score = 13
        lead_reasons = []

        # Check 10th lords
        if l10_a == l10_b:
            lead_score += 5
            lead_reasons.append(f"समान कर्मेश ({l10_a}) होने से व्यापारिक विजन व कार्य-शैली में एकरूपता रहेगी।")
        elif l10_b in NATURAL_FRIENDS.get(l10_a, []):
            lead_score += 4
            lead_reasons.append(f"कर्मेशों ({l10_a} व {l10_b}) की परस्पर मैत्री व्यवसाय विस्तार में सहायक है।")

        # Sun / Mars (Ego clash check)
        sun_diff = abs(planets_a["Sun"].sign_id - planets_b["Sun"].sign_id)
        if sun_diff == 6:  # Direct 180 deg opposition
            lead_score -= 5
            lead_reasons.append("दोनों के सूर्य समसप्तक (आमने-सामने) हैं, जिससे अहंकार (Ego clash) व निर्णय लेने में टकराव संभव है।")
        else:
            lead_score += 4
            lead_reasons.append("सूर्य की संतुलित स्थिति नेतृत्व के स्पष्ट व सम्मानजनक विभाजन का समर्थन करती है।")

        lead_score = min(25, max(4, lead_score))

        # -------------------------------------------------------------
        # Pillar 3: Dispute, Litigation & Treachery Risk (0-25 pts)
        # (Higher is SAFER, lower means higher conflict)
        # -------------------------------------------------------------
        safety_score = 14
        conflict_reasons = []

        lagna_diff = ((lagna_b - lagna_a) % 12) + 1
        if lagna_diff in [6, 8]:
            safety_score -= 8
            conflict_reasons.append("⚠️ लग्नों में षडाष्टक (६-८) संबंध: मतभेद होने पर विवाद न्यायालय या तीसरे पक्ष तक पहुँचने का जोखिम।")
        elif lagna_diff in [1, 5, 9, 7]:
            safety_score += 6
            conflict_reasons.append("✅ लग्नों में परस्पर सौहार्द: मतभेदों का समाधान आपसी बातचीत से सहजता से संभव।")

        # 7th house (Partnership lord) check
        if l7_b in NATURAL_ENEMIES.get(l7_a, []):
            safety_score -= 5
            conflict_reasons.append("⚠️ सप्तमेशों में शत्रुता होने से व्यापारिक अनुबंध में अविश्वास की आशंका।")
        else:
            safety_score += 5
            conflict_reasons.append("✅ सप्तमेशों की अनुकूलता साझेदारी में निष्ठा व मर्यादा सुनिश्चित करती है।")

        safety_score = min(25, max(4, safety_score))

        # -------------------------------------------------------------
        # Pillar 4: Longevity & Commercial Fortune (0-25 pts)
        # -------------------------------------------------------------
        longevity_score = 14
        growth_reasons = []

        # 9th lord (Fortune) and Jupiter presence
        if planets_a["Jupiter"].dignity in ["exalted", "own", "friend"] and planets_b["Jupiter"].dignity in ["exalted", "own", "friend"]:
            longevity_score += 6
            growth_reasons.append("दोनों कुण्डलियों में देवगुरु बृहस्पति बलिष्ठ हैं—दीर्घकालिक विकास व ईश्वरीय कृपा का योग।")

        if lagna_diff in [3, 11]:
            longevity_score += 5
            growth_reasons.append("तृतीय-एकादश संबंध निरंतर व्यावसायिक प्रयास व विपणन (मार्केटिंग) में सफलता देता है।")

        longevity_score = min(25, max(4, longevity_score))

        # Total Composite Score (0-100)
        total_score = fin_score + lead_score + safety_score + longevity_score

        if total_score >= 80:
            verdict_badge = "🟢 अत्युत्कृष्ट साझेदारी (Highly Auspicious & Lucrative)"
            verdict_text = "यह साझेदारी अत्यंत फलदायी, वित्तीय समृद्धि दायक एवं दीर्घकालिक स्थायित्व वाली सिद्ध होगी। दोनों एक-दूसरे के पूरक बनकर विशाल व्यापारिक साम्राज्य खड़ा कर सकते हैं।"
            rating_color = "#16A34A"
        elif total_score >= 60:
            verdict_badge = "🟡 अनुकूल साझेदारी (Favorable with Clear Agreements)"
            verdict_text = "साझेदारी सामान्यतः लाभदायक व सहयोगपूर्ण रहेगी। व्यापार में वित्तीय व प्रशासनिक जिम्मेदारियों का स्पष्ट लिखित अनुबंध (MOU / Partnership Deed) अनिवार्य रूप से करें।"
            rating_color = "#D97706"
        elif total_score >= 45:
            verdict_badge = "⚠️ मध्यम सतर्कता (Moderate Risk — Requires Audits)"
            verdict_text = "साझेदारी में मतभेद व वित्तीय संदेह उत्पन्न होने की संभावना है। खातों का त्रैमासिक ऑडिट एवं निर्णयों में स्पष्टता बनाए रखना अत्यंत आवश्यक है।"
            rating_color = "#EA580C"
        else:
            verdict_badge = "🔴 उच्च जोखिम / असहयोग (High Dispute & Loss Risk)"
            verdict_text = "शास्त्रीय दृष्टि से यह साझेदारी अनुकूल नहीं है। अहंकार टकराव, वित्तीय नुकसान या कानूनी विवाद की प्रबल आशंका है। संयुक्त व्यापार के स्थान पर स्वतंत्र कार्य श्रेयस्कर होगा।"
            rating_color = "#DC2626"

        return {
            "name_a": name_a,
            "name_b": name_b,
            "total_score": total_score,
            "verdict_badge": verdict_badge,
            "verdict_text": verdict_text,
            "rating_color": rating_color,
            "pillars": {
                "financial_integrity": {
                    "score": fin_score,
                    "max": 25,
                    "label": "वित्तीय विश्वास व लाभ (Financial Trust)",
                    "reasons": fin_reasons
                },
                "leadership_synergy": {
                    "score": lead_score,
                    "max": 25,
                    "label": "नेतृत्व व कार्य विभाजन (Leadership Synergy)",
                    "reasons": lead_reasons
                },
                "conflict_safety": {
                    "score": safety_score,
                    "max": 25,
                    "label": "विवाद व मुकदमा सुरक्षा (Legal & Conflict Safety)",
                    "reasons": conflict_reasons
                },
                "partnership_longevity": {
                    "score": longevity_score,
                    "max": 25,
                    "label": "दीर्घकालिक स्थायित्व व भाग्य (Longevity & Growth)",
                    "reasons": growth_reasons
                }
            }
        }


default_partnership_service = BusinessPartnershipService()
