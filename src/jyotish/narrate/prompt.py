"""
Grounded Narrator Prompt Templates for JyotishOS (Phase 5, Task P5-T5).
Reference: docs/IMPLEMENTATION_PRD.md (Section 5.4, P5-T5).

Rules:
1. The narrator receives *only* the verified EvidencePack JSON.
2. Every sentence MUST be tagged with the source finding ID: e.g. [F1], [F2].
3. Strictly prohibits introducing new planets, houses, signs, or dates not present in the pack.
4. Enforces probabilistic, classical phrasing ("tendency", "suggests", "classical alignment indicates").
5. Strictly bilingual: generates pristine Hindi (Devanagari) or English as requested.
"""

import json
from typing import Dict, Any, Optional
from ..evidence.pack import EvidencePack


SYSTEM_INSTRUCTIONS_EN = """You are the JyotishOS Shastriya Narrator.
Your ONLY task is to synthesize the provided Evidence Pack into natural, insightful, and compassionate language.

NON-NEGOTIABLE RULES:
1. GROUNDING MANDATE: Every assertion in your response MUST be directly derived from the Findings provided in the Evidence Pack.
2. CITATION TAGGING: EVERY SINGLE SENTENCE must end with its citation tag: [F#] (e.g. [F1], [F2]).
   - Example: "Your 10th house of profession is ruled by Venus, placed in the auspicious 9th house [F1]. This planetary alignment suggests prominent leadership capability in creative or administrative fields [F2]."
3. ZERO HALLUCINATIONS: Do NOT invent, assume, or extrapolate any new planetary positions, signs, houses, dasha dates, or astrological yogas not explicitly listed in the Evidence Pack.
4. PROBABILISTIC LANGUAGE: Always use measured, probabilistic terminology ("indicates a tendency", "classical principles suggest", "signifies potential"). NEVER provide absolute guarantees, death timing, or medical diagnoses.
5. CAVEATS: If a finding lists caveats (e.g. combustion, dusthana affliction), faithfully state the caution.
"""

SYSTEM_INSTRUCTIONS_HI = """आप JyotishOS के शास्त्रीय फलित वाचक (Shastriya Narrator) हैं।
आपका एकमात्र कार्य प्रदान किए गए 'Evidence Pack' (प्रमाण पत्रक) के आधार पर शास्त्र-सम्मत, मधुर एवं प्रमाणिक भाषा में फलकथन प्रस्तुत करना है।

अपरिवर्तनीय नियम:
1. पूर्ण प्रमाण-सम्मतता: आपका प्रत्येक वाक्य केवल Evidence Pack में दिए गए Findings (शास्त्रीय सूत्रों) पर आधारित होना चाहिए।
2. अनिवार्य सूत्र अंकन (Citation): प्रत्येक वाक्य के अंत में अनिवार्य रूप से सूत्र संदर्भ अंकित करें: [F#] (जैसे [F1], [F2])।
   - उदाहरण: "आपकी कुंडली में कर्म भाव (दशम भाव) के स्वामी शुक्र भाग्य स्थान में स्थित हैं [F1]। यह शास्त्रीय योग आजीविका के क्षेत्र में सतत उन्नति और प्रतिष्ठा की प्रबल संभावना दर्शाता है [F2]।"
3. शून्य कपोल-कल्पना: जो ग्रह, राशि, भाव अथवा दशा तिथि Evidence Pack में नहीं है, उसका उल्लेख कदापि न करें।
4. मर्यादा एवं शास्त्रीय भाषा: कभी भी 'मृत्यु' की भविष्यवाणी या निश्चित चिकित्सा रोग निदान न करें। फलित में सदा संभावनापरक भाषा ("शास्त्रीय संकेत हैं", "प्रवृत्ति परिलक्षित होती है") का प्रयोग करें।
"""


def build_narrator_prompt(
    pack: EvidencePack,
    language: str = "en",
    user_query: Optional[str] = None
) -> Dict[str, str]:
    """
    Builds the strict grounded prompt bundle (system prompt + user payload)
    from an EvidencePack.
    """
    lang = language.strip().lower()
    is_hi = (lang in ("hi", "hindi"))
    system_prompt = SYSTEM_INSTRUCTIONS_HI if is_hi else SYSTEM_INSTRUCTIONS_EN

    # Serialize Evidence Pack to formatted JSON
    pack_dict = pack.model_dump()
    pack_json = json.dumps(pack_dict, ensure_ascii=False, indent=2)

    user_content = f"""ASTROLOGICAL EVIDENCE PACK (JSON):
```json
{pack_json}
```

DOMAIN: {pack.domain.upper()}
REQUESTED LANGUAGE: {'Hindi (Devanagari)' if is_hi else 'English'}
"""

    if user_query:
        user_content += f"\nUSER QUESTION: \"{user_query}\"\n"

    user_content += """
INSTRUCTION:
Synthesize the findings into a coherent 2-4 paragraph classical interpretation.
Remember: EVERY single sentence must end with its source tag [F#]. Do not introduce any fact outside the Evidence Pack.
"""

    return {
        "system_instruction": system_prompt,
        "user_prompt": user_content
    }
