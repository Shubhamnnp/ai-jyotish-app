"""
AI Narrative and Explanation Engine for JyotishOS.
Synthesizes explainable, transparent, compassionate narratives from structured evidence JSON.
Strictly bounded by classical rules evidence: the LLM never calculates positions or invents predictions.
Implements ethical guardrails against death prediction, medical diagnosis, and fear-mongering.
"""

import os
from typing import Dict, Any, Optional
from ..core.models import GhatnaQueryResult, KundaliChart

try:
    from google import genai
    from google.genai import types
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False


SYSTEM_PROMPT = """You are JyotishOS, an expert shastriya Vedic Astrology assistant.
Your role is to explain the calculated astrological results to the user based EXCLUSIVELY on the provided structured evidence JSON.

STRICT OPERATIONAL PRINCIPLES:
1. MATHEMATICAL FIDELITY: Never calculate or guess planetary positions, dashas, or dates yourself. All calculations are provided in the input JSON.
2. EVIDENCE BOUND: Do not invent any yoga, affliction, or event not present in the evidence list.
3. PROBABILISTIC & EMPOWERING LANGUAGE: Use terms like "संभावना अधिक है (favorable probability)", "सावधानी / धैर्य की अवधि", "योजना और चिंतन का समय". Never use deterministic absolutes like "यह पक्का होगा" or "आप बर्बाद हो जाएंगे".
4. SOURCE CITATIONS: Always mention the classical grantha references present in the evidence (e.g., Brihat Parashara Hora Shastra, Phaladeepika, Saravali).
5. STRICT ETHICAL GUARDRAILS:
   - NEVER predict exact date of death or lifespan.
   - NEVER give medical diagnosis or prescribe clinical treatments.
   - NEVER provide stock trading tips or lottery numbers.
   - NEVER sell expensive superstitious remedies or instill fear (bhaya).
6. LANGUAGE: Provide a structured, dignified Hindi explanation followed by an English summary.
"""


class AINarrativeService:
    """Generates LLM narratives from calculated evidence."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.client = None
        if GENAI_AVAILABLE and self.api_key:
            try:
                self.client = genai.Client(api_key=self.api_key)
            except Exception:
                self.client = None

    def synthesize_narrative(self, result: GhatnaQueryResult, language: str = "Hindi") -> str:
        """
        Uses Gemini to generate an eloquent, evidence-bound explanation.
        Falls back seamlessly to the deterministic narrative if API key is not configured.
        """
        if not self.client:
            # High-fidelity deterministic fallback
            return result.narrative_hi if language.lower().startswith("hi") else result.narrative_en

        # Package minimal structured evidence for prompt
        evidence_payload = {
            "target_date": result.target_date.isoformat(),
            "theme": result.theme,
            "composite_score": result.composite_score,
            "confidence_band": result.confidence_band,
            "active_dasha": result.active_dasha.formatted_summary,
            "transit_summary": {
                "sade_sati": result.transit_summary.is_sade_sati,
                "sade_sati_phase": result.transit_summary.sade_sati_phase,
                "dhaiya": result.transit_summary.is_dhaiya,
                "double_transit_10th": result.transit_summary.is_jupiter_saturn_double_transit_on_10th,
                "guru_chandal": result.transit_summary.is_guru_chandal_transit,
            },
            "top_positive_signals": [
                {
                    "rule": s.rule_name_hi,
                    "source": s.source_text,
                    "explanation": s.explanation_hi,
                    "score": s.signal_score
                }
                for s in result.top_positive_signals
            ],
            "top_negative_signals": [
                {
                    "rule": s.rule_name_hi,
                    "source": s.source_text,
                    "explanation": s.explanation_hi,
                    "score": s.signal_score
                }
                for s in result.top_negative_signals
            ]
        }

        user_prompt = (
            f"Please synthesize a clear, shastriya astrological consultation narrative for the user in {language}.\n"
            f"Input Evidence JSON:\n{evidence_payload}\n"
        )

        try:
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=user_prompt,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    temperature=0.3,
                )
            )
            return response.text
        except Exception:
            return result.narrative_hi

    def chat_consultation(
        self,
        user_query: str,
        chart: Optional[KundaliChart] = None,
        active_dasha_summary: Optional[str] = None,
        language: str = "Hindi",
        chat_history: Optional[list] = None
    ) -> str:
        """
        Interactive Astrological Sahayak (Conversational Assistant).
        Grounded strictly in the user's computed chart and classical Shastra scriptures.
        Enforces DPDP Act and ethical guardrails against fatalistic predictions.
        """
        from .knowledge_base import default_knowledge_base

        q_lower = user_query.lower()

        # 1. Strict Ethical Safety Guardrails
        if any(w in q_lower for w in ["death", "die", "mrityu", "suicide", "kill", "lifespan", "kab marunga"]):
            return (
                "⚠️ **शास्त्रीय मर्यादा संदेश (Ethical Notice):**\n"
                "प्राचीन महर्षियों के आदेशानुसार किसी व्यक्ति की मृत्यु तिथि या आयु की गणना पूर्णतः वर्जित है। "
                "यदि आप या आपका कोई परिचित मानसिक तनाव अथवा संकट में है, तो कृपया राष्ट्रीय मानसिक स्वास्थ्य हेल्पलाइन "
                "**KIRAN (1800-599-0019)** अथवा **Tele-MANAS (14416)** पर संपर्क करें। हम आपके उत्तम स्वास्थ्य की कामना करते हैं।"
            )

        if any(w in q_lower for w in ["lottery", "gambling", "satta", "trading tips", "jackpot"]):
            return (
                "⚠️ **मर्यादा सूचना:** ज्योतिष शास्त्र आत्म-ज्ञान, कर्म-सुधार और जीवन मार्गदर्शन का विषय है। "
                "सट्टा, जुआ या लॉटरी नंबरों की भविष्यवाणी शास्त्र-सम्मत नहीं है।"
            )

        # 2. Retrieve relevant Shastriya passages from Knowledge Base
        shastra_passages = default_knowledge_base.search(user_query, limit=2)
        citations_text = ""
        for p in shastra_passages:
            citations_text += f"\n- {p.grantha} ({p.chapter}): {p.translation_hi}"

        # 3. Context Payload
        chart_context = ""
        if chart:
            chart_context = (
                f"Lagna: {chart.lagna_sign_name} ({chart.lagna_degree:.2f}°), "
                f"Moon Sign: {chart.planets['Moon'].sign_name} ({chart.planets['Moon'].sign_degree:.2f}° in {chart.planets['Moon'].nakshatra_name}), "
                f"Sun Sign: {chart.planets['Sun'].sign_name}, "
                f"Atmakaraka (AK): {chart.atmakaraka}, "
                f"Active Dasha: {active_dasha_summary or 'Vimshottari'}"
            )

        if not self.client:
            # Deterministic classical fallback narrative
            return (
                f"नमस्ते। आपकी कुण्डली के अनुसार {chart_context}।\n\n"
                f"आपके प्रश्न **'{user_query}'** के सन्दर्भ में शास्त्रीय आधार:\n"
                f"{citations_text}\n\n"
                f"वर्तमान काल में अपनी क्षमता और सत्कर्म पर ध्यान केंद्रित करें। ग्रह-गोचर अनुकूल कर्म करने पर ही शुभ फल देते हैं।"
            )

        prompt = (
            f"User Question: {user_query}\n"
            f"User Natal Baseline Context: {chart_context}\n"
            f"Relevant Classical Granthas Retrieved:\n{citations_text}\n"
            f"Language: {language}\n"
            f"Provide an empowering, insightful, shastriya astrological consultation response."
        )

        try:
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    temperature=0.4,
                )
            )
            return response.text
        except Exception:
            return (
                f"आपकी कुण्डली के आधार पर ({chart_context}):\n"
                f"शास्त्रीय निर्देश: {citations_text}\n"
                f"कर्म की प्रधानता रखते हुए धैर्यपूर्वक आगे बढ़ें।"
            )


default_narrative_service = AINarrativeService()

