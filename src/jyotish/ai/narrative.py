"""
AI Narrative and Explanation Engine for JyotishOS.
Powered by Google Gemini API (gemini-3.8-flash) & Classical Vedic Shastras.
Synthesizes explainable, transparent, compassionate astrological consultation
deeply personalized to the currently loaded Kundali.
Supports Hindi, Hinglish (Roman Hindi), and English seamlessly.
"""

import os
from datetime import datetime, date
from typing import Dict, Any, Optional, List, Union
from ..core.models import GhatnaQueryResult, KundaliChart

try:
    from google import genai
    from google.genai import types
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False


def detect_query_language(text: str) -> str:
    """Detects whether the user asked in Hindi (Devanagari), Hinglish (Roman Hindi), or English."""
    if not text:
        return "Hindi (Devanagari)"
    # Check for Devanagari Unicode characters
    if any('\u0900' <= char <= '\u097F' for char in text):
        return "Hindi (Devanagari)"
    
    # Check for distinctive Hinglish grammatical and vocabulary markers
    hinglish_markers = {
        "meri", "mera", "mere", "kab", "kaisa", "kaisi", "kaise", "hoga", "hogi", "honge",
        "shadi", "shaadi", "vivah", "naukri", "paisa", "dhan", "ghar", "dasha", "upay",
        "hai", "hain", "kya", "batao", "bataiye", "chal", "raha", "rahi", "rahe", "badlegi",
        "badlega", "milegi", "milega", "apna", "apni", "apne", "kare", "karein", "karna",
        "chahiye", "lagna", "rashi", "kundli", "kundali", "grah", "graha", "bhav", "bhava",
        "shani", "guru", "rahu", "ketu", "mangal", "surya", "chandra", "budh", "shukra",
        "kripa", "namaste", "pranam", "karo", "kijiye", "bataen", "puja", "pooja", "mandir",
        "ratna", "rudraksha", "sadesati", "sade", "dhaiya", "kaal", "dosha", "dosh", "bata"
    }
    
    english_stop_words = {
        "when", "will", "what", "how", "which", "where", "who", "why", "can", "should", "could",
        "would", "is", "are", "am", "my", "your", "the", "about", "tell", "me", "change",
        "future", "career", "job", "marriage", "health", "wealth", "finance", "business",
        "money", "good", "bad", "time", "period", "life", "success", "prediction", "remedy",
        "stone", "gemstone", "planet", "horoscope", "chart", "birth", "love", "education"
    }

    words = [w.strip() for w in text.lower().replace("?", " ").replace(".", " ").replace(",", " ").replace("!", " ").split() if w.strip()]
    if not words:
        return "Hindi (Devanagari)"
    
    hinglish_count = sum(1 for w in words if w in hinglish_markers)
    english_count = sum(1 for w in words if w in english_stop_words)

    if hinglish_count > 0 and hinglish_count >= english_count:
        return "Hinglish (Roman Hindi)"
    elif english_count > 0:
        return "English"
    elif hinglish_count > 0:
        return "Hinglish (Roman Hindi)"
    
    return "English"


SYSTEM_PROMPT = """You are 'दैवज्ञ AI' (Daivajna AI), a revered, world-class Vedic Astrologer and scholar of Shastriya Jyotish (Brihat Parashara Hora Shastra, Phaladeepika, Jaimini Upadesha Sutras, Saravali, Tajika Neelakanthi, and Krishnamurti Paddhati).

YOUR SACRED CORE DIRECTIVE:
Provide deeply personalized, precise, compassionate, and shastriya astrological consultation based EXCLUSIVELY on the user's computed natal Kundali and current dasha/transit context provided in the prompt.

CRITICAL OPERATIONAL PRINCIPLES:
1. DEEP KUNDALI SPECIFICITY: Always reference the specific parameters of the user's opened Kundali (Lagna, Moon Sign, Nakshatra, House Placements of relevant planets, Dignities, Active Dasha/Antardasha lords, and Transits). Connect your astrological reasoning directly to their exact chart.
2. SHASTRIYA RIGOR: Cite classical granthas and principles (e.g. Parashari house lord relationships, Jaimini Chara Karakas like Atmakaraka/Amatyakaraka, Shadbala strength, Ashtakavarga points, KP Cuspal sub-lords) when explaining why a certain result or period is indicated.
3. EMPOWERING & ETHICAL GUIDANCE:
   - Emphasize karma, free-will (पुरूषार्थ), and spiritual growth.
   - Use balanced, uplifting language (e.g. "अनुकूल काल / Favorable timing", "धैर्य एवं संयम की अवधि", "साधना एवं योजना का समय").
   - NEVER make fatalistic predictions, never predict exact lifespan or death, never provide medical diagnoses or stock tips.
4. ACTIONABLE VEDIC REMEDIES:
   - Always conclude with practical, satvik remedies tailored to their weak benefics or afflicting planets:
     a) Ratna (Gemstone) recommendation with metal, finger, and day.
     b) Rudraksha & Beej / Vedic Mantras with japa count.
     c) Satvik Daan (Charity) & Vrata (Fasting) suggestions.
     d) Vastu & lifestyle alignment.
5. TRILINGUAL SUPPORT (Hindi / Hinglish / English):
   - If the user asks in Hinglish (Roman Hindi, e.g. 'meri naukri kab badlegi', 'meri shadi kab hogi', 'kya dasha chal rahi hai'), UNDERSTAND IT FULLY and reply in natural, fluent, crystal-clear HINGLISH (Roman script Hindi) with clean bold headings and bullet points!
   - If the user asks in pure Hindi (Devanagari script, e.g. 'मेरी नौकरी कब बदलेगी?'), reply in dignified, pure Hindi.
   - If the user asks in English (e.g. 'When will I change my job?'), reply in articulate, professional English.
"""


class AINarrativeService:
    """Generates Gemini AI astrological narratives and conversational consultations from calculated charts."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.client = None
        self._init_client(self.api_key)

    def _init_client(self, api_key: Optional[str] = None) -> bool:
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

    def chat_consultation(
        self,
        user_query: str,
        chart: Optional[KundaliChart] = None,
        *args,
        **kwargs
    ) -> str:
        """
        Interactive Astrological Sahayak (Conversational Assistant).
        Grounded strictly in the user's computed chart and classical Shastra scriptures.
        Accepts *args and **kwargs to ensure 100% signature stability on Streamlit Cloud.
        """
        from .knowledge_base import default_knowledge_base

        master_data = kwargs.get("master_data")
        active_dasha_summary = kwargs.get("active_dasha_summary")
        api_key = kwargs.get("api_key")
        model = kwargs.get("model", "gemini-3.8-flash")
        chat_history = kwargs.get("chat_history")

        # Detect User Language / Script (Hindi, Hinglish, English)
        detected_lang = detect_query_language(user_query)

        q_lower = user_query.lower()

        # 1. Strict Ethical Safety Guardrails
        if any(w in q_lower for w in ["death", "die", "mrityu", "suicide", "kill", "lifespan", "kab marunga", "death date", "mar jaunga"]):
            if detected_lang.startswith("Hinglish"):
                return (
                    "⚠️ **Shastriya Maryada Sandesh (Ethical Notice):**\n\n"
                    "Prachin Maharshiyon ke nirdesh anusar kisi bhi vyakti ki mrityu tithi ya aayu ki ganana karna sarvatha varjit hai. "
                    "Yadi aap ya aapka koi parichit mansik tanav me hai, to kripya Rashtriya Helpline **KIRAN (1800-599-0019)** ya **Tele-MANAS (14416)** par sampark karein. "
                    "Hum aapke swasthya, deerghayu aur shanti ki kamna karte hain."
                )
            elif detected_lang.startswith("English"):
                return (
                    "⚠️ **Ethical & Astrological Notice:**\n\n"
                    "According to classical Vedic scriptures, predicting exact lifespan or date of death is strictly prohibited. "
                    "If you or someone you know is experiencing distress, please reach out to the National Mental Health Helpline **KIRAN (1800-599-0019)** or **Tele-MANAS (14416)**. We wish you peace, good health, and longevity."
                )
            else:
                return (
                    "⚠️ **शास्त्रीय मर्यादा संदेश (Ethical Notice):**\n\n"
                    "प्राचीन महर्षियों के आदेशानुसार किसी व्यक्ति की मृत्यु तिथि या आयु की गणना पूर्णतः वर्जित है। "
                    "यदि आप या आपका कोई परिचित मानसिक तनाव अथवा संकट में है, तो कृपया राष्ट्रीय मानसिक स्वास्थ्य हेल्पलाइन "
                    "**KIRAN (1800-599-0019)** अथवा **Tele-MANAS (14416)** पर संपर्क करें। हम आपके उत्तम स्वास्थ्य, दीर्घायु एवं शांति की मंगलकामना करते हैं।"
                )

        if any(w in q_lower for w in ["lottery", "gambling", "satta", "trading tips", "jackpot"]):
            if detected_lang.startswith("Hinglish"):
                return (
                    "⚠️ **Maryada Suchna:**\n\n"
                    "Vedic Jyotish aatm-gyan, karm-sudhar aur jeevan margdarshan ka shastra hai. Satta, jua ya lottery numberon ki bhavishyavani shastra-sammat nahi hai. Kripya apne purusharth par vishwas rakhein."
                )
            else:
                return (
                    "⚠️ **मर्यादा सूचना (Ethical Notice):**\n\n"
                    "वैदिक ज्योतिष शास्त्र आत्म-ज्ञान, कर्म-सुधार और जीवन मार्गदर्शन का विषय है। "
                    "सट्टा, जुआ या लॉटरी नंबरों की भविष्यवाणी शास्त्र-सम्मत नहीं है। कृपया अपने पुरुषार्थ एवं कौशल पर विश्वास रखें।"
                )

        # 2. Retrieve relevant Shastriya passages from Knowledge Base
        shastra_passages = default_knowledge_base.search(user_query, limit=2)
        citations_text = ""
        for p in shastra_passages:
            citations_text += f"\n- **{p.grantha} ({p.chapter}):** {p.translation_hi}"

        # 3. Context Payload
        chart_context = ""
        if chart:
            chart_context = self.build_full_chart_context(chart, master_data, active_dasha_summary)

        # 4. Check & Re-initialize Gemini Client
        if api_key:
            self._init_client(api_key)
        elif not self.client:
            self._init_client(os.getenv("GEMINI_API_KEY"))

        if not self.client:
            # Deterministic classical fallback narrative
            p_name = chart.birth_data.name if chart else "जातक"
            lagna_s = chart.lagna_sign_name if chart else ""
            moon_s = chart.planets['Moon'].sign_name if chart else ""
            
            if detected_lang.startswith("Hinglish"):
                return (
                    f"🙏 **Namaste {p_name} ji!**\n\n"
                    f"Aapki Kundali ke mukhya aadhar: **{lagna_s} Lagna** aur **{moon_s} Chandra Rashi**.\n\n"
                    f"Aapke prashna: *\"{user_query}\"* ke sandarbh me shastriya sutra:\n"
                    f"{citations_text}\n\n"
                    f"💡 **Mukhya Paramarsh:** Vartaman kal me apne 10th/11th house lords aur active dasha ki sthiti anukul karm me lagayein.\n\n"
                    f"---\n"
                    f"ℹ️ *Note: Real-time interactive AI baat-cheet ke liye kripya upar apna Google Gemini API Key darj karein.*"
                )
            else:
                return (
                    f"🙏 **नमस्ते {p_name} जी!**\n\n"
                    f"आपकी कुण्डली के मुख्य आधार: **{lagna_s} लग्न** एवं **{moon_s} चंद्र राशि**।\n\n"
                    f"आपके प्रश्न: *\"{user_query}\"* के संदर्भ में प्रासंगिक शास्त्रीय सूत्र:\n"
                    f"{citations_text}\n\n"
                    f"💡 **विशेष परामर्श:** वर्तमान काल में अपनी क्षमताओं, लग्न स्वामी और भाग्येश की स्थिति का सदुपयोग करते हुए सत्कर्म में संलग्न रहें।\n\n"
                    f"---\n"
                    f"ℹ️ *नोट: रीयल-टाइम AI संवाद और विस्तृत फलादेश हेतु कृपया ऊपर अपना Google Gemini API Key दर्ज करें।*"
                )

        # 5. Format Conversation History
        history_text = ""
        if chat_history and len(chat_history) > 1:
            history_text = "\n=== PREVIOUS CONVERSATION HISTORY ===\n"
            for msg in chat_history[-6:]:
                role = "User" if msg.get("role") == "user" else "Astrologer AI"
                history_text += f"{role}: {msg.get('content', '')}\n"
            history_text += "====================================\n"

        prompt = f"""{chart_context}

{history_text}
=== RELEVANT CLASSICAL GRANTHA SCRIPTURAL CITATIONS ==={citations_text}
======================================================

USER QUESTION:
"{user_query}"

DETECTED USER LANGUAGE / SCRIPT:
{detected_lang}

INSTRUCTIONS:
1. Provide a detailed, highly personalized astrological answer in **{detected_lang}** directly tailored to {chart.birth_data.name if chart else 'the user'}'s exact Kundali parameters above.
   - If the detected language is Hinglish (Roman Hindi), write the response in conversational, clear, easy-to-read Hinglish (Roman script Hindi) with clean formatting.
   - If Hindi (Devanagari), write in dignified Hindi.
   - If English, write in professional English.
2. Analyze the specific houses, house lords, planet dignities, active dasha periods, and transits relevant to this query.
3. Conclude with specific, satvik Vedic remedies (appropriate Gemstone with metal/finger, Rudraksha, Beej Mantra with count, Charity/Daan, and Vastu advice).
"""

        # 6. Call Gemini API
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
        if detected_lang.startswith("Hinglish"):
            return (
                f"🙏 **Shastriya Phaladesh ({chart.birth_data.name if chart else 'Jataka'}):**\n\n"
                f"Aapke prashna *\"{user_query}\"* par Kundali ke grah sthiti ke anusar vishleshan:\n\n"
                f"{citations_text}\n\n"
                f"Grahon ke shubh prabhav ko badhane ke liye Gayatri Mantra aur apne Ishta Dev ki upasana karein."
            )
        else:
            return (
                f"🙏 **शास्त्रीय फलादेश ({chart.birth_data.name if chart else 'जातक'}):**\n\n"
                f"आपके प्रश्न *\"{user_query}\"* पर कुण्डली के ग्रह स्थिति के अनुसार विचार:\n\n"
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
