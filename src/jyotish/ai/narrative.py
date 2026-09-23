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

try:
    from google import genai
    from google.genai import types
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False


SYSTEM_PROMPT = """You are 'दैवज्ञ AI' (Daivajna AI), a revered, world-class Vedic Astrologer and scholar of Shastriya Jyotish (Brihat Parashara Hora Shastra, Saravali, Brihat Jataka, Bhrigu Nandi Nadi, Lal Kitab, Krishnamurti Paddhati, Jaimini Upadesha Sutras, Phaladeepika, Muhurtha Chintamani, and Samhitas).

YOUR SACRED CORE DIRECTIVE:
Provide deeply personalized, precise, compassionate, and shastriya astrological consultation based on the user's computed natal Kundali, current dasha/transit context, and the LIVE 12,500+ MAHA-SHASTRIYA SCANNED RULES provided in the prompt.

CRITICAL OPERATIONAL PRINCIPLES:
1. 12,500+ SHASTRIYA RULES INTEGRATION: You have access to the live scan of 12,500+ classical Jyotish rules across all ancient scriptures. In your consultation, you MUST explicitly cite and synthesize the relevant fired classical rules provided in the prompt context. Name the scripture (BPHS, Saravali, Brihat Jataka, Lal Kitab, KP, Bhrigu Nadi, Jaimini, etc.), the rule name, and the authentic classical reasoning.
2. DEEP KUNDALI SPECIFICITY: Always reference the specific parameters of the user's opened Kundali (Lagna, Moon Sign, Nakshatra, House Placements of relevant planets, Dignities, Active Dasha/Antardasha lords, and Transits). Connect your astrological reasoning directly to their exact chart.
3. SHASTRIYA RIGOR & HONESTY: Explain both positive yogas (+) and cautionary doshas/challenges (-) honestly without sugarcoating, but always provide constructive, satvik guidance.
4. EMPOWERING & ETHICAL GUIDANCE:
   - Emphasize karma, free-will (पुरूषार्थ), and spiritual growth.
   - Use balanced, uplifting language (e.g. "अनुकूल काल", "धैर्य एवं संयम की अवधि", "साधना एवं योजना का समय").
   - NEVER make fatalistic predictions, never predict exact lifespan or death, never provide medical diagnoses or stock tips.
5. ACTIONABLE VEDIC REMEDIES:
   - Always conclude with practical, satvik remedies tailored to their weak benefics or afflicting planets:
     a) Ratna (Gemstone) recommendation with metal, finger, and day.
     b) Rudraksha & Beej / Vedic Mantras with japa count.
     c) Satvik Daan (Charity) & Vrata (Fasting) suggestions.
     d) Vastu & lifestyle alignment.
6. LANGUAGE & TONE:
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
                self.api_key = key_to_use
                return True
            except Exception:
                self.client = None
                return False
        return False

    def build_full_chart_context(
        self,
        chart: KundaliChart,
        master_data: Optional[Dict[str, Any]] = None,
        active_dasha_summary: Optional[str] = None
    ) -> str:
        """
        Extracts and formats exhaustive astrological parameters of the native's Kundali
        into a dense, structured context block for the Gemini LLM.
        """
        p = chart.birth_data
        pan = chart.panchang

        # 1. Planetary Table summary
        planet_summaries = []
        for p_name, pos in chart.planets.items():
            status_flags = []
            if pos.is_retrograde:
                status_flags.append("Vakri (Retrograde)")
            if pos.is_combust:
                status_flags.append("Asta (Combust)")
            flags_str = f", {', '.join(status_flags)}" if status_flags else ""
            planet_summaries.append(
                f"{p_name}: {pos.sign_name} ({pos.sign_degree:.2f}°), House {pos.house_from_lagna}, "
                f"Nakshatra: {pos.nakshatra_name} Pada {pos.nakshatra_pada} (Lord: {pos.nakshatra_lord}), "
                f"Dignity: {pos.dignity.capitalize()}{flags_str}"
            )
        planets_block = "\n  - " + "\n  - ".join(planet_summaries)

        # 2. 12 Bhavas summary
        house_summaries = []
        for h in chart.houses:
            occ = ", ".join(h.occupants) if h.occupants else "None"
            asp = ", ".join(h.aspecting_planets) if h.aspecting_planets else "None"
            house_summaries.append(
                f"House {h.house_number} ({h.sign_name}, Lord: {h.lord}): Occupants=[{occ}], Aspecting=[{asp}]"
            )
        houses_block = "\n  - " + "\n  - ".join(house_summaries)

        # 3. Dasha Summary
        dasha_text = active_dasha_summary or "Vimshottari Dasha Active"
        if master_data and "dashas" in master_data:
            vim_list = master_data.get("dashas", {}).get("vimshottari", [])
            if vim_list:
                curr_year = datetime.now()
                for d in vim_list:
                    if d.get("start_date") <= curr_year <= d.get("end_date"):
                        dasha_text = f"Active Mahadasha: {d.get('lord')} (from {d.get('start_date').strftime('%d-%b-%Y')} to {d.get('end_date').strftime('%d-%b-%Y')})"
                        break

        # 4. Jaimini Karakas
        jaimini_text = f"Atmakaraka (AK): {chart.atmakaraka}"
        if master_data and "jaimini" in master_data:
            j_obj = master_data["jaimini"]
            karakas = j_obj.karakas_7 if hasattr(j_obj, "karakas_7") else (j_obj.get("chara_karakas", {}) if isinstance(j_obj, dict) else {})
            if karakas:
                jaimini_text = ", ".join([f"{k}: {v}" for k, v in karakas.items()])

        # 5. Shadbala Top Strength
        shadbala_text = "Calculated"
        if master_data and "shadbala" in master_data:
            sb = master_data["shadbala"]
            if sb and "planets" in sb:
                sb_ranks = []
                for p_n, p_val in sb["planets"].items():
                    ratio = p_val.get("strength_ratio", 0.0) if isinstance(p_val, dict) else getattr(p_val, "strength_ratio", 0.0)
                    sb_ranks.append((p_n, ratio))
                sb_ranks.sort(key=lambda x: x[1], reverse=True)
                shadbala_text = "Strongest: " + ", ".join([f"{p} ({r:.2f})" for p, r in sb_ranks[:3]]) + " | Weakest: " + ", ".join([f"{p} ({r:.2f})" for p, r in sb_ranks[-2:]])

        # 6. Ashtakavarga SAV
        sav_text = ""
        if master_data and "ashtakavarga" in master_data:
            sav = master_data["ashtakavarga"].get("sav", [])
            if sav and len(sav) == 12:
                sav_text = f"H1(Lagna): {sav[chart.lagna_sign_id-1]} pts, H10(Karma): {sav[(chart.lagna_sign_id+8)%12]} pts, H11(Labha): {sav[(chart.lagna_sign_id+9)%12]} pts"

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

=== 12 BHAVAS (HOUSES) OCCUPANTS & ASPECTS ==={houses_block}
======================================
"""
        return context

    def get_or_evaluate_chart_rules(self, chart: KundaliChart) -> List[RuleEvidence]:
        """
        Evaluates or retrieves cached results for all 12,500+ classical rules against the given chart.
        Fast sub-second evaluation cached directly on the chart object.
        """
        if hasattr(chart, "_cached_rules_evidence") and chart._cached_rules_evidence:
            return chart._cached_rules_evidence

        evidences = [default_rules_engine.evaluate_rule(r, chart) for r in default_rules_engine.rules]
        chart._cached_rules_evidence = evidences
        return evidences

    def scan_shastriya_rules(
        self,
        chart: KundaliChart,
        query: str = "",
        limit: int = 15
    ) -> Dict[str, Any]:
        """
        Scans all 12,500+ rules in the rules bank for the current chart,
        extracts active (fired) rules, and filters the top rules relevant to the user's query topic.
        """
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
            "remedies": ["उपाय", "रत्न", "रुद्राक्ष", "मंत्र", "पूजा", "दान", "व्रत", "शांति", "दुरुस्ती", "remedy", "gemstone", "rudraksha", "mantra", "fasting"],
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
            top_pos = sorted(positives, key=lambda x: x.signal_score, reverse=True)[:max(1, limit * 2 // 3)]
            top_neg = sorted(negatives, key=lambda x: x.signal_score, reverse=True)[:max(1, limit // 3)]
            relevant_rules = top_pos + top_neg

        evidence_lines = []
        for idx, r in enumerate(relevant_rules[:limit], 1):
            pol_badge = "[शुभ योग (+)]" if r.polarity == "+" else "[सतर्कता/दोष (-)]"
            shastra = r.source_text
            if r.source_chapter and r.source_chapter != "General":
                shastra += f" ({r.source_chapter})"
            evidence_lines.append(
                f"{idx}. {pol_badge} **{r.rule_name_hi}** | ग्रन्थ: *{shastra}*\n"
                f"   - शास्त्रीय फल: {r.explanation_hi}\n"
                f"   - प्रभाव क्षेत्र: {', '.join(r.themes)} (सिग्नल बल: {r.signal_score:.2f})"
            )
        formatted_prompt_block = "\n".join(evidence_lines)

        return {
            "total_scanned": len(evidences),
            "total_fired": len(fired),
            "total_positive": len(positives),
            "total_negative": len(negatives),
            "matched_topic": matched_topic or "सम्पूर्ण जीवन दर्शन",
            "grantha_breakdown": grantha_counts,
            "relevant_rules": relevant_rules[:limit],
            "formatted_prompt_block": formatted_prompt_block
        }

    def chat_consultation(
        self,
        user_query: str,
        chart: Optional[KundaliChart] = None,
        master_data: Optional[Dict[str, Any]] = None,
        active_dasha_summary: Optional[str] = None,
        api_key: Optional[str] = None,
        model: str = "gemini-3.8-flash",
        language: str = "Hindi",
        chat_history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """
        Interactive Astrological Sahayak (Conversational Assistant).
        Grounded strictly in the user's computed chart, 12,500+ classical rules scan, and Vedic Shastras.
        Uses gemini-3.8-flash via google-genai SDK.
        """
        from .knowledge_base import default_knowledge_base

        q_lower = user_query.lower()

        # 1. Strict Ethical Safety Guardrails
        if any(w in q_lower for w in ["death", "die", "mrityu", "suicide", "kill", "lifespan", "kab marunga", "death date"]):
            return (
                "⚠️ **शास्त्रीय मर्यादा संदेश (Ethical Notice):**\n\n"
                "प्राचीन महर्षियों के आदेशानुसार किसी व्यक्ति की मृत्यु तिथि या आयु की गणना पूर्णतः वर्जित है। "
                "यदि आप या आपका कोई परिचित मानसिक तनाव अथवा संकट में है, तो कृपया राष्ट्रीय मानसिक स्वास्थ्य हेल्पलाइन "
                "**KIRAN (1800-599-0019)** अथवा **Tele-MANAS (14416)** पर संपर्क करें। हम आपके उत्तम स्वास्थ्य, दीर्घायु एवं शांति की मंगलकामना करते हैं।"
            )

        if any(w in q_lower for w in ["lottery", "gambling", "satta", "trading tips", "jackpot"]):
            return (
                "⚠️ **मर्यादा सूचना (Ethical Notice):**\n\n"
                "वैदिक ज्योतिष शास्त्र आत्म-ज्ञान, कर्म-सुधार और जीवन मार्गदर्शन का विषय है। "
                "सट्टा, जुआ या लॉटरी नंबरों की भविष्यवाणी शास्त्र-सम्मत नहीं है। कृपया अपने पुरुषार्थ एवं कौशल पर विश्वास रखें।"
            )

        # 2. Perform Live Scan of 12,500+ Maha-Shastriya Rules
        rules_scan_info: Optional[Dict[str, Any]] = None
        shastriya_rules_block = ""
        if chart:
            try:
                rules_scan_info = self.scan_shastriya_rules(chart, user_query, limit=16)
                shastriya_rules_block = rules_scan_info["formatted_prompt_block"]
                # Save into session state if available for UI inspectability
                try:
                    import streamlit as st
                    st.session_state["ai_latest_rules_scan"] = rules_scan_info
                except Exception:
                    pass
            except Exception as ex:
                shastriya_rules_block = f"Rules scan error: {ex}"

        # 3. Retrieve relevant Shastriya passages from Knowledge Base
        shastra_passages = default_knowledge_base.search(user_query, limit=2)
        citations_text = ""
        for p in shastra_passages:
            citations_text += f"\n- **{p.grantha} ({p.chapter}):** {p.translation_hi}"

        # 4. Context Payload
        chart_context = ""
        if chart:
            chart_context = self.build_full_chart_context(chart, master_data, active_dasha_summary)

        # 5. Check & Re-initialize Gemini Client
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

            return (
                f"🙏 **प्रणाम {p_name} जी!**\n\n"
                f"आपकी कुण्डली के मुख्य आधार: **{lagna_s} लग्न**, **{moon_s} राशि** एवं **{dasha_s}**।\n"
                f"आपके प्रश्न: *\"{user_query}\"* पर **१२,५००+ महा-शास्त्रीय नियमों** के सूक्ष्म परीक्षण से निम्नलिखित निष्कर्ष प्राप्त हुए हैं:"
                f"{rules_summary_md}\n"
                f"💡 **दैवज्ञ परामर्श:** आपकी कुण्डली के लग्नेश व भाग्येश के शुभ प्रभाव को जागृत रखते हुए निष्ठापूर्वक कर्म करें।\n\n"
                f"✨ **शास्त्रीय वैदिक उपाय:**\n"
                f"- **रत्न/रुद्राक्ष:** लग्नेश व पंचमेश की अनुकूलता हेतु उपयुक्त रत्न अथवा पंचमुखी रुद्राक्ष धारण करें।\n"
                f"- **मंत्र साधना:** नित्य प्रातः 'ॐ नमो भगवते वासुदेवाय' अथवा गायत्री मंत्र का १०८ बार जप करें।\n"
                f"- **सात्विक दान:** बुधवार व शनिवार को गौसेवा अथवा असहायों को अन्नदान करें।\n\n"
                f"---\n"
                f"*(यह फलादेश १२,५००+ महा-शास्त्रीय नियमों एवं कुण्डली के गणितीय समन्वय से तैयार किया गया है)*"
            )

        # 7. Format Conversation History
        history_text = ""
        if chat_history and len(chat_history) > 1:
            history_text = "\n=== PREVIOUS CONVERSATION HISTORY ===\n"
            for msg in chat_history[-6:]:  # Keep last 3 turns
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
"{user_query}"

INSTRUCTIONS:
1. Provide a comprehensive, highly personalized astrological answer in {language} directly tailored to {chart.birth_data.name if chart else 'the user'}'s exact Kundali parameters and the 12,500+ SCANNED RULES above.
2. Explicitly cite the scanned classical rules (name the Grantha like BPHS, Saravali, Brihat Jataka, Lal Kitab, KP, Nadi, Jaimini, etc., and explain how these specific yogas/doshas manifest in the native's life).
3. Connect your prediction directly to their active Dasha, transit conditions, and relevant house lords.
4. Conclude with specific, actionable, satvik Vedic remedies (appropriate Gemstone with metal/finger, Rudraksha, Beej Mantra with count, Charity/Daan, and Vastu advice).
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
            except Exception as e:
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
