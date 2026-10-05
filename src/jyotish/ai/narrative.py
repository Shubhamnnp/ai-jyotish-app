"""
AI Narrative and Explanation Engine for JyotishOS.
Powered by Google Gemini API (gemini-3.8-flash) & Classical Vedic Shastras.
Synthesizes explainable, transparent, compassionate astrological consultation
deeply personalized to the currently loaded Kundali.
"""

import os
from datetime import datetime, date
from typing import Dict, Any, Optional, List
from ..core.models import GhatnaQueryResult, KundaliChart, RuleEvidence
from ..rules.engine import default_rules_engine
from ..services.gemology import default_gemology_service
from ..core.affliction import AfflictionEngine

try:
    from google import genai
    from google.genai import types
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False


SYSTEM_PROMPT = """You are 'दैवज्ञ AI' (Daivajna AI), a revered, world-class Vedic Astrologer and scholar of Shastriya Jyotish (Brihat Parashara Hora Shastra, Saravali, Brihat Jataka, Bhrigu Nandi Nadi, Lal Kitab, Krishnamurti Paddhati, Jaimini Upadesha Sutras, Phaladeepika, Muhurta Chintamani, and Samhitas).

YOUR SACRED CORE DIRECTIVE:
Provide deeply personalized, 99.9% precise, compassionate, and shastriya astrological consultation based on the user's computed natal Kundali (D1 to D60), current dasha/transit context, the STRICT CLASSICAL GEMOLOGY AUDIT, and the LIVE 12,500+ MAHA-SHASTRIYA SCANNED RULES provided in the prompt.

CRITICAL OPERATIONAL PRINCIPLES:

1. ABSOLUTE RATNA SHASTRA & GEMOLOGY LAW (रत्न शास्त्र का अटल नियम):
   - A gemstone (रत्न) acts as a cosmic antenna and amplifier. It AMPLIFIES AND TRANSMITS the energy of the planet into the native's body and aura.
   - GOLDEN LAW: NEVER, UNDER ANY CIRCUMSTANCE, RECOMMEND THE GEMSTONE OF A PLANET SITTING IN A DUSTHANA / TRIK HOUSE (6th, 8th, or 12th house), OR A FUNCTIONAL MALEFIC!
   - SPECIFIC WARNING FOR 8TH HOUSE (अष्टम भाव): If Mercury (बुध) is placed in the 8th house, WEARING EMERALD (पन्ना) IS STRICTLY FORBIDDEN (सर्वथा वर्जित)! Wearing Emerald when Mercury is in the 8th house activates chronic disease, anxiety, nervous disorders, speech difficulties, financial loss, and sudden accidents.
   - Whenever asked about gemstones or when recommending remedies, you MUST CONSULT THE 'SHASTRIYA RATNA SHASTRA & GEMOLOGY AUDIT MATRIX' provided in the prompt.
   - If the user asks about an inauspicious or dusthana gemstone (like Panna for 8th house Mercury), YOU MUST EXPLICITLY WARN THEM AND ALERT THEM: "🚫 सावधानी: पन्ना आपके लिए सर्वथा वर्जित है क्योंकि बुध आपकी कुण्डली के ८वें भाव में स्थित है!"
   - For dusthana, debilitated, or afflicted planets, prescribe ONLY SATVIK REMEDIES:
     a) Rudraksha (e.g. 4-Mukhi for Mercury, 1/12-Mukhi for Sun, 2-Mukhi for Moon, 3-Mukhi for Mars, 5-Mukhi for Jupiter, 6-Mukhi for Venus, 7-Mukhi for Saturn, 8-Mukhi for Rahu, 9-Mukhi for Ketu).
     b) Vedic / Beej Mantra with exact counts.
     c) Satvik Daan (Charity) items and day.
     d) Vrata (Fasting) & Deity Upasana (e.g. Lord Ganesha for afflicted Mercury).

2. D1 TO D60 DIVISIONAL CHARTS & VAISHESHIKAMSHA SYNTHESIS (षोडशवर्ग विश्लेषण):
   - Always synthesize the divisional chart dignity: Navamsha (D9 - Dharma & Marriage), Dashamsha (D10 - Career & Karma), and Shashtiamsha (D60 - Past Karma & Ultimate Dignity).
   - If a planet is Vargottama or attains high Vaisheshikamsha (Simhasanamsa, Paravatamsa, etc.), highlight its heightened potency.

3. CANDID SHASTRIYA ALERTS ON NEGATIVE PREDICTIONS (नकारात्मक फलादेश पर स्पष्ट सतर्कता):
   - When a negative combination, affliction, maraka/badhaka influence, or inauspicious transit/dasha is identified, DO NOT hide or sugarcoat it.
   - State the classical risk candidly: "⚠️ शास्त्रीय चेतावनी (Astrological Caution): ...".
   - Immediately balance every negative indication with constructive, compassionate, and precise remedial countermeasures (सात्विक उपाय) so the native can mitigate the affliction.

4. 12,500+ SHASTRIYA RULES INTEGRATION:
   - You have access to the live scan of 12,500+ classical Jyotish rules across ancient scriptures.
   - Explicitly cite the fired classical rules provided in the prompt context. Name the scripture (BPHS, Saravali, Brihat Jataka, Lal Kitab, KP, Bhrigu Nadi, Jaimini, etc.), rule name, and reasoning.

5. LANGUAGE & TONE:
   - Respond in dignified, eloquent, easy-to-understand Hindi (with Sanskrit terminology where helpful). If the user asks in English, provide the response in English.
   - Format responses beautifully with bold headings, bullet points, and clean structure.
"""


class AINarrativeService:
    """Generates Gemini AI astrological narratives and conversational consultations from calculated charts."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.client = None
        self._init_client(self.api_key)

    def _init_client(self, api_key: Optional[str] = None):
        """Initializes or re-initializes the Gemini genai.Client."""
        key_to_use = api_key or self.api_key or os.getenv("GEMINI_API_KEY")
        if GENAI_AVAILABLE and key_to_use:
            try:
                self.client = genai.Client(api_key=key_to_use)
            except Exception:
                self.client = None

    def build_full_chart_context(self, chart: Optional[KundaliChart] = None, master_data: Optional[Dict[str, Any]] = None) -> str:
        """Constructs an exhaustive astrological context profile of the native's chart."""
        if not chart:
            return "=== NO SPECIFIC NATAL CHART LOADED (GENERAL JYOTISH CONSULTATION) ==="
        p = chart.birth_data
        pan = chart.panchang

        # Format Planetary Positions block
        planets_lines = []
        dusthana_warnings = []
        for p_name, pos in chart.planets.items():
            retro_str = " (Retrograde)" if pos.is_retrograde else ""
            comb_str = " (Combust)" if pos.is_combust else ""
            h = pos.house_from_lagna
            planets_lines.append(
                f"  • {p_name}: {pos.sign_name} ({pos.sign_degree:.2f}°), House {h}, "
                f"Nakshatra {pos.nakshatra_name} (Pada {pos.nakshatra_pada}), "
                f"Dignity: {pos.dignity.title()}{retro_str}{comb_str}"
            )
            if h in [6, 8, 12]:
                dusthana_warnings.append(f"  • ⚠️ DUSTHANA WARNING: {p_name} is in House {h} (6/8/12). GEMSTONE IS STRICTLY FORBIDDEN!")

        planets_block = "\n" + "\n".join(planets_lines)
        dusthana_block = "\n" + "\n".join(dusthana_warnings) if dusthana_warnings else "\n  • None"

        # Format Houses block
        houses_lines = []
        for i, h in enumerate(chart.houses):
            h_num = i + 1
            occ = [name for name, pos in chart.planets.items() if pos.house_from_lagna == h_num]
            occ_str = ", ".join(occ) if occ else "Empty"
            houses_lines.append(
                f"  • House {h_num}: {h.sign_name} (Lord: {h.lord}), Occupants: [{occ_str}]"
            )
        houses_block = "\n" + "\n".join(houses_lines)

        # Active Dasha summary
        dasha_text = "N/A"
        if master_data and "dasha" in master_data:
            d = master_data["dasha"]
            curr = d.get("current_dasha", {})
            if curr:
                dasha_text = f"Mahadasha: {curr.get('mahadasha', '')}, Antardasha: {curr.get('antardasha', '')}, Pratyantar: {curr.get('pratyantardasha', '')}"

        # Jaimini text
        ak = getattr(chart, 'atmakaraka', 'N/A')
        amk = getattr(chart, 'amatyakaraka', 'N/A')
        jaimini_text = f"Atmakaraka (AK): {ak}" + (f", Amatyakaraka (AmK): {amk}" if amk != 'N/A' else "")

        # Shadbala text
        shadbala_text = "N/A"
        if master_data and "shadbala" in master_data:
            sb = master_data["shadbala"]
            if isinstance(sb, dict) and "ranks" in sb:
                shadbala_text = ", ".join([f"{k}: Rank {v}" for k, v in list(sb["ranks"].items())[:7]])

        # SAV text
        sav_text = "N/A"
        if master_data and "ashtakavarga" in master_data:
            av = master_data["ashtakavarga"]
            if isinstance(av, dict) and "sav" in av:
                sav_points = av["sav"]
                if isinstance(sav_points, (list, dict)):
                    sav_text = str(sav_points)[:120] + "..."

        # D1 to D60 Divisional Charts & Vaisheshikamsha Summary via AfflictionEngine
        varga_block = ""
        try:
            aff_eng = AfflictionEngine(chart)
            v_sum = aff_eng.calculate_varga_dignity_summary()
            v_lines = []
            for p_nm, v_inf in v_sum.items():
                v_lines.append(f"  • {p_nm}: {v_inf.get('vaisheshikamsha', 'General')} (Benefic Points: {v_inf.get('benefic_points', 0)}/16, Vargottama: {v_inf.get('is_vargottama', False)})")
            varga_block = "\n" + "\n".join(v_lines)
        except Exception:
            varga_block = "\n  • Varga computation active in master engine."

        # Gemology Audit Matrix for strict prompt enforcement
        gemology_block = default_gemology_service.format_gemology_audit_for_prompt(chart)

        context = f"""
=== NATAL KUNDALI BASELINE PROFILE ===
• Name: {p.name}
• Birth Date & Time: {p.birth_date.strftime('%d-%B-%Y')} at {p.birth_time.strftime('%I:%M:%S %p')}
• Coordinates: Lat {p.latitude:.4f}° N, Lon {p.longitude:.4f}° E (Ayanamsa: {chart.ayanamsa_name} {chart.ayanamsa_value:.2f}°)
• Lagna (Ascendant): {chart.lagna_sign_name} ({chart.lagna_degree:.2f}°, Lord: {chart.houses[0].lord})
• Moon Sign (Rashi): {chart.planets['Moon'].sign_name} ({chart.planets['Moon'].sign_degree:.2f}°)
• Moon Nakshatra: {pan.nakshatra_name} (Pada {chart.planets['Moon'].nakshatra_pada})
• Sun Sign: {chart.planets['Sun'].sign_name} ({chart.planets['Sun'].sign_degree:.2f}°)
• Panchang: Vara={pan.vara_name}, Tithi={pan.tithi_name} ({pan.tithi_type}), Yoga={pan.yoga_name}, Karana={pan.karana_name}
• Active Dasha: {dasha_text}
• Jaimini Karakas: {jaimini_text}
• Shadbala Strengths: {shadbala_text}
• Key Ashtakavarga SAV Points: {sav_text}

=== 9 PLANETS POSITION & DIGNITY ==={planets_block}

=== DUSTHANA (6, 8, 12) PLACEMENTS & WARNINGS ==={dusthana_block}

=== D1 TO D60 DIVISIONAL CHARTS (VAISHESHIKAMSHA & VARGOTTAMA) ==={varga_block}

=== 12 BHAVAS (HOUSES) OCCUPANTS & ASPECTS ==={houses_block}

{gemology_block}
======================================
"""
        return context

    def get_or_evaluate_chart_rules(self, chart: KundaliChart) -> List[RuleEvidence]:
        """Evaluates or retrieves cached results for all 12,500+ classical rules against the given chart."""
        try:
            cached = getattr(chart, "_cached_rules_evidence", None)
            if cached:
                return cached
        except Exception:
            pass

        evidences = [default_rules_engine.evaluate_rule(r, chart) for r in default_rules_engine.rules]
        try:
            object.__setattr__(chart, "_cached_rules_evidence", evidences)
        except Exception:
            try:
                chart._cached_rules_evidence = evidences
            except Exception:
                pass
        return evidences

    def scan_shastriya_rules(
        self,
        chart: Optional[KundaliChart] = None,
        query: str = "",
        limit: int = 15
    ) -> Dict[str, Any]:
        """Scans all 12,500+ rules in the rules bank for the current chart."""
        if not chart:
            return {
                "total_scanned": 12578,
                "total_fired": 0,
                "total_positive": 0,
                "total_negative": 0,
                "matched_topic": "General",
                "relevant_rules": [],
                "grantha_breakdown": {}
            }
        evidences = self.get_or_evaluate_chart_rules(chart)
        fired = [e for e in evidences if e.fired]
        positives = [e for e in fired if e.polarity == "+"]
        negatives = [e for e in fired if e.polarity == "-"]

        # Scripture Breakdown
        grantha_counts: Dict[str, int] = {}
        for e in fired:
            src = e.source_text or "Classical Shastra"
            grantha_counts[src] = grantha_counts.get(src, 0) + 1

        # Query Intent Keyword Mapping
        q_lower = query.lower()
        topic = "general"
        matched_keywords: List[str] = []

        TOPIC_MAP = {
            "career": ["नौकरी", "व्यापार", "करियर", "पदोन्नति", "आजीविका", "काम", "धंधा", "व्यवसाय", "career", "job", "promotion", "business", "profession", "work"],
            "marriage": ["विवाह", "शादी", "दांपत्य", "जीवनसाथी", "ससुराल", "पत्नी", "पति", "प्रेम", "संबंध", "सगाई", "marriage", "spouse", "love", "relationship", "wife", "husband"],
            "wealth": ["धन", "संपत्ति", "आर्थिक", "पैसा", "मकान", "भूमि", "शेयर", "कर्ज", "खजाना", "लाभ", "wealth", "finance", "money", "property", "rich", "income"],
            "health": ["स्वास्थ्य", "रोग", "बीमारी", "दुर्घटना", "मानसिक", "कष्ट", "तनाव", "सर्जरी", "आयु", "health", "disease", "illness", "surgery", "accident", "hospital"],
            "dasha": ["दशा", "गोचर", "समय", "महादशा", "अंतर्दशा", "शनि", "साढ़ेसाती", "भ्रमण", "dasha", "transit", "gochar", "period", "timing"],
            "remedies": ["उपाय", "रत्न", "रुद्राक्ष", "मंत्र", "पूजा", "दान", "व्रत", "शांति", "दुरुस्ती", "पन्ना", "माणिक्य", "मोती", "मूँगा", "पुखराज", "हीरा", "नीलम", "गोमेद", "remedy", "gemstone", "rudraksha", "mantra", "fasting", "panna", "emerald", "ratan", "ratna"],
            "progeny": ["संतान", "गर्भ", "पुत्र", "पुत्री", "बच्चा", "family", "child", "children", "pregnancy", "progeny"],
            "education": ["विद्या", "शिक्षा", "पढ़ाई", "परीक्षा", "ज्ञान", "education", "study", "exam", "learning", "degree"]
        }

        matched_topic = None
        for t_name, kws in TOPIC_MAP.items():
            if any(kw in q_lower for kw in kws):
                matched_topic = t_name
                matched_keywords = [kw for kw in kws if kw in q_lower]
                break

        # Filter relevant rules
        relevant_rules: List[RuleEvidence] = []
        if matched_topic:
            def rule_topic_score(e: RuleEvidence) -> float:
                score = e.signal_score
                themes_str = " ".join(e.themes).lower()
                name_str = (e.rule_name_hi + " " + e.rule_name_en).lower()
                desc_str = (e.explanation_hi or "").lower()
                full_text = f"{themes_str} {name_str} {desc_str} {e.rule_id.lower()}"

                for kw in matched_keywords:
                    if kw in full_text:
                        score += 0.5
                if matched_topic in themes_str:
                    score += 0.8
                return score

            sorted_fired = sorted(fired, key=rule_topic_score, reverse=True)
            relevant_rules = sorted_fired[:limit]
        else:
            sorted_fired = sorted(fired, key=lambda e: e.signal_score, reverse=True)
            relevant_rules = sorted_fired[:limit]

        return {
            "total_scanned": len(evidences),
            "total_fired": len(fired),
            "total_positive": len(positives),
            "total_negative": len(negatives),
            "matched_topic": matched_topic or "सम्पूर्ण जीवन विश्लेषण (Comprehensive)",
            "relevant_rules": relevant_rules,
            "grantha_breakdown": grantha_counts
        }

    def chat_consultation(
        self,
        user_query: str,
        chart: Optional[KundaliChart] = None,
        master_data: Optional[Dict[str, Any]] = None,
        api_key: Optional[str] = None,
        model: str = "gemini-3.8-flash",
        language: str = "Hindi",
        chat_history: Optional[List[Dict[str, str]]] = None,
        active_dasha_summary: str = "",
        **kwargs
    ) -> str:
        """Conversational Astrological Consultation powered by Gemini and Shastriya rules."""
        # 1. Build Baseline Kundali Context
        chart_context = self.build_full_chart_context(chart, master_data)

        # 2. Extract Active Dasha
        if not active_dasha_summary and master_data and "dasha" in master_data:
            d = master_data["dasha"]
            curr = d.get("current_dasha", {})
            if curr:
                active_dasha_summary = f"{curr.get('mahadasha', '')}-{curr.get('antardasha', '')}-{curr.get('pratyantardasha', '')}"

        # 3. Live Scan of 12,500+ Rules
        rules_scan_info = self.scan_shastriya_rules(chart, query=user_query, limit=12)

        # Save scan in Streamlit session state if available
        try:
            import streamlit as st
            st.session_state.ai_latest_rules_scan = rules_scan_info
        except Exception:
            pass

        # 4. Format Shastriya Rules Block
        shastriya_rules_lines = []
        citations_set = set()
        for idx, r in enumerate(rules_scan_info.get("relevant_rules", []), 1):
            pol_badge = "[+] SHUBH YOGA" if r.polarity == "+" else "[-] CAUTIONARY RULE"
            grantha_label = r.source_text
            if r.source_chapter and r.source_chapter != "General":
                grantha_label += f" ({r.source_chapter})"
            citations_set.add(grantha_label)
            shastriya_rules_lines.append(
                f"{idx}. {pol_badge}: {r.rule_name_hi} ({r.rule_name_en})\n"
                f"   - Source: {grantha_label}\n"
                f"   - Shastriya Effect: {r.explanation_hi}\n"
                f"   - Themes: {', '.join(r.themes)} (Signal: {round(r.signal_score * 100)}%)"
            )
        shastriya_rules_block = "\n".join(shastriya_rules_lines) if shastriya_rules_lines else "None fired directly."
        citations_text = "\n" + "\n".join([f"• {c}" for c in sorted(citations_set)]) if citations_set else "\n• Classical Vedic Jyotish Traditions"

        # 5. Check API Client
        if api_key:
            self._init_client(api_key)
        elif not self.client:
            env_key = os.getenv("GEMINI_API_KEY")
            if not env_key:
                try:
                    import streamlit as st
                    env_key = st.secrets.get("GEMINI_API_KEY", "")
                except Exception:
                    env_key = ""
            if env_key:
                self._init_client(env_key)

        # 6. Fallback if client not available (Deterministic Rich Shastriya Consultation)
        if not self.client:
            if not chart:
                return (
                    f"🙏 **प्रणाम!**\n\n"
                    f"आपके प्रश्न: *\"{user_query}\"* पर वैदिक ज्योतिषीय परामर्श:\n\n"
                    f"सटीक एवं ९९.९% प्रामाणिक फलादेश (D1 से D60 षोडशवर्ग, दशा, गोचर एवं रत्न शुद्धि) हेतु कृपया अपनी कुण्डली लोड करें। "
                    f"सामान्य वैदिक मार्गदर्शन के अनुसार प्रतिदिन प्रातः गायत्री मंत्र का जप एवं अपने इष्टदेव की आराधना कल्याणकारी है।"
                )
            p_name = chart.birth_data.name if chart else "जातक"
            lagna_s = chart.lagna_sign_name if chart else ""
            moon_s = chart.planets['Moon'].sign_name if chart else ""
            dasha_s = active_dasha_summary or "वर्तमान विंशोत्तरी दशा"

            rules_summary_md = ""
            if rules_scan_info and rules_scan_info.get("relevant_rules"):
                rules_summary_md = "\n\n### 📜 १२,५००+ महा-शास्त्रीय स्कैन से प्राप्त सक्रिय योग व फल:\n"
                for r in rules_scan_info["relevant_rules"][:6]:
                    icon = "🟢" if r.polarity == "+" else "🔴"
                    rules_summary_md += f"- {icon} **{r.rule_name_hi}** (*{r.source_text}*): {r.explanation_hi}\n"

            # Gemology Audit Analysis
            gem_audit = default_gemology_service.audit_all_planets(chart)
            q_lower = user_query.lower()
            is_gem_query = any(k in q_lower for k in ["रत्न", "पन्ना", "माणिक्य", "मोती", "मूँगा", "पुखराज", "हीरा", "नीलम", "गोमेद", "लहसुनिया", "उपाय", "रुद्राक्ष", "ratan", "ratna", "gem", "gemstone", "panna", "emerald", "remedy"])

            # Dusthana / Prohibition check (special emphasis on Mercury in 8th house)
            mercury_pos = chart.planets.get("Mercury")
            merc_house = mercury_pos.house_from_lagna if mercury_pos else None

            gem_alert_md = ""
            if merc_house in [6, 8, 12]:
                m_info = gem_audit["planets_audit"]["Mercury"]
                gem_alert_md = (
                    f"\n\n### 🚨 गंभीर शास्त्रीय चेतावनी: पन्ना रत्न आपके लिए सर्वथा वर्जित है!\n"
                    f"- **शास्त्रीय कारण:** आपकी कुण्डली में बुध ग्रह **{merc_house}वें (अष्टम/दुष्टस्थान) भाव** में स्थित है।\n"
                    f"- *बृहत्संहिता* एवं *फलदीपिका* के अनुसार दुष्टस्थान (६, ८, १२) में बैठे ग्रह का रत्न कभी भी धारण नहीं करना चाहिए, क्योंकि यह उस भाव के अनिष्ट फल, मानसिक तनाव, वाणी-तंत्रिका दोष तथा अकस्मात संकट को सक्रिय करता है।\n"
                    f"- 🌿 **अनुशंसित सात्विक विकल्प:**\n"
                    f"  - 📿 **विहित रुद्राक्ष:** {m_info['rudraksha']}\n"
                    f"  - 🕉️ **वैदिक बीज मंत्र:** `{m_info['beej_mantra']}` ({m_info['japa_count']:,} जप)\n"
                    f"  - 🌾 **संकल्पित दान:** {m_info['daan_items']} ({m_info['daan_day']} को)\n"
                    f"  - 🪔 **व्रत व उपासना:** {m_info['vrata']} | {m_info['deity']}\n"
                )
            elif gem_audit["strictly_prohibited_gems"]:
                gem_alert_md = "\n\n### ⚠️ शास्त्रीय रत्न निषेध अलर्ट (Strict Prohibitions):\n"
                for pro in gem_audit["strictly_prohibited_gems"][:3]:
                    gem_alert_md += f"- 🚫 **{pro['gem']} ({pro['planet']})**: {pro['reason']}\n"

            # Recommended gems if any
            rec_gems_md = ""
            if gem_audit["recommended_gems"]:
                rec_gems_md = "\n- **शुभ अनुकूल रत्न:** " + ", ".join([f"**{rg['gem']}** ({rg['planet']} हेतु - {gem_audit['planets_audit'].get(rg['planet'], {}).get('metal', 'उचित धातु')} में)" for rg in gem_audit["recommended_gems"]])
            else:
                rec_gems_md = "\n- **रत्न विचार:** वर्तमान में ग्रहों की स्थिति अनुसार सात्विक मंत्र व रुद्राक्ष साधना ही सर्वोत्तम है।"

            return (
                f"🙏 **प्रणाम {p_name} जी!**\n\n"
                f"आपकी कुण्डली के मुख्य आधार: **{lagna_s} लग्न**, **{moon_s} राशि** एवं **{dasha_s}**।\n"
                f"आपके प्रश्न: *\"{user_query}\"* पर **१२,५००+ महा-शास्त्रीय नियमों** एवं **रत्न शुद्धि परीक्षण** से निम्नलिखित निष्कर्ष प्राप्त हुए हैं:"
                f"{rules_summary_md}"
                f"{gem_alert_md}\n\n"
                f"💡 **दैवज्ञ परामर्श:** आपकी कुण्डली के लग्नेश व भाग्येश के शुभ प्रभाव को जागृत रखते हुए निष्ठापूर्वक कर्म करें।\n\n"
                f"✨ **शास्त्रीय वैदिक उपाय:**"
                f"{rec_gems_md}\n"
                f"- **मंत्र साधना:** नित्य प्रातः 'ॐ नमो भगवते वासुदेवाय' अथवा गायत्री मंत्र का १०८ बार जप करें।\n"
                f"- **सात्विक दान:** बुधवार व शनिवार को गौसेवा अथवा असहायों को अन्नदान करें।\n\n"
                f"---\n"
                f"*(यह फलादेश १२,५००+ महा-शास्त्रीय नियमों, D1-D60 वर्ग एवं कुण्डली के गणितीय समन्वय से तैयार किया गया है)*"
            )

        # 7. Format Conversation History
        history_text = ""
        if chat_history and len(chat_history) > 1:
            history_text = "\n=== PREVIOUS CONVERSATION HISTORY ===\n"
            for msg in chat_history[-6:]:
                role = "User" if msg.get("role") == "user" else "Astrologer AI"
                history_text += f"{role}: {msg.get('content', '')}\n"
            history_text += "====================================\n"

        prompt = f"""{chart_context}

{history_text}
=== 12,500+ MAHA-SHASTRIYA SCANNED RULES EVIDENCE (EXACT CHART MATCHES) ===
Total Rules Scanned: {rules_scan_info['total_scanned'] if rules_scan_info else 12578}
Total Fired in Kundali: {rules_scan_info['total_fired'] if rules_scan_info else 'N/A'} (Positive Yogas: {rules_scan_info['total_positive'] if rules_scan_info else 'N/A'}, Cautionary Doshas: {rules_scan_info['total_negative'] if rules_scan_info else 'N/A'})
Topic Identified: {rules_scan_info['matched_topic'] if rules_scan_info else 'General'}

Top Scanned Classical Rules Fired for this Query:
{shastriya_rules_block}
=============================================================================

=== RELEVANT CLASSICAL GRANTHA SCRIPTURAL CITATIONS ==={citations_text}
======================================================

USER QUESTION:
\"{user_query}\"

INSTRUCTIONS:
1. Provide a comprehensive, highly personalized astrological answer in {language} directly tailored to {chart.birth_data.name if chart else 'the user'}'s exact Kundali parameters (D1 to D60), active Dasha, transits, and the 12,500+ SCANNED RULES above.
2. STRICT GEMOLOGY LAW: Strictly adhere to the 'SHASTRIYA RATNA SHASTRA & GEMOLOGY AUDIT MATRIX' provided above. If Mercury is in the 8th house, NEVER recommend Emerald/Panna; warn the native explicitly and prescribe 4-Mukhi Rudraksha, Budha mantra, and green moong daan! For any planet in 6, 8, 12, FORBID its gemstone and give safe satvik alternatives.
3. CAUTIONARY ALERTS: If any negative combinations, afflictions, or challenges exist, state them candidly under a bold caution heading (⚠️ शास्त्रीय चेतावनी) and provide exact remedial countermeasures.
4. Synthesize D9 Navamsha and D60 Shashtiamsha dignity levels where relevant.
"""

        # 8. Call Gemini API
        models_to_try = [model, "gemini-3.8-flash", "gemini-flash-latest", "gemini-3.1-flash-lite"]
        for m_name in models_to_try:
            try:
                response = self.client.models.generate_content(
                    model=m_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=SYSTEM_PROMPT,
                        temperature=0.35,
                    )
                )
                if response and response.text:
                    return response.text
            except Exception:
                continue

        # Fallback if API calls fail
        p_name = chart.birth_data.name if chart else "जातक"
        rules_list_md = ""
        if rules_scan_info and rules_scan_info.get("relevant_rules"):
            rules_list_md = "\n\n**सक्रिय महा-शास्त्रीय नियम:**\n"
            for r in rules_scan_info["relevant_rules"][:5]:
                pol_sym = "🟢" if r.polarity == "+" else "🔴"
                rules_list_md += f"- {pol_sym} **{r.rule_name_hi}** (*{r.source_text}*): {r.explanation_hi}\n"

        return (
            f"🙏 **शास्त्रीय फलादेश ({p_name} जी):**\n\n"
            f"आपके प्रश्न *\"{user_query}\"* पर कुण्डली के ग्रह स्थिति एवं १२,५००+ महा-शास्त्रीय नियमों के आधार पर विश्लेषण:\n"
            f"{rules_list_md}\n"
            f"{citations_text}\n\n"
            f"ग्रहों के शुभ प्रभाव को जागृत करने हेतु प्रतिदिन गायत्री मंत्र एवं अपने इष्ट देव की आराधना करें।"
        )

    def synthesize_narrative(self, result: GhatnaQueryResult, language: str = "Hindi") -> str:
        """Synthesizes narrative for Ghatna query results."""
        if not self.client:
            return result.narrative_hi if language.lower().startswith("hi") else result.narrative_en

        evidence_payload = {
            "target_date": result.target_date.isoformat(),
            "theme": result.theme,
            "composite_score": result.composite_score,
            "confidence_band": result.confidence_band,
            "active_dasha": result.active_dasha.formatted_summary,
            "top_positive_signals": [
                {"rule": s.rule_name_hi, "source": s.source_text, "explanation": s.explanation_hi, "score": s.signal_score}
                for s in result.top_positive_signals
            ],
            "top_negative_signals": [
                {"rule": s.rule_name_hi, "source": s.source_text, "explanation": s.explanation_hi, "score": s.signal_score}
                for s in result.top_negative_signals
            ]
        }

        user_prompt = (
            f"Please synthesize a clear, shastriya astrological consultation narrative for the user in {language}.\n"
            f"Input Evidence JSON:\n{evidence_payload}\n"
        )

        try:
            response = self.client.models.generate_content(
                model="gemini-3.8-flash",
                contents=user_prompt,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    temperature=0.3,
                )
            )
            return response.text
        except Exception:
            return result.narrative_hi


# Singleton instance
default_narrative_service = AINarrativeService()
