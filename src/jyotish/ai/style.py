"""
Multi-Lingual Style Synthesis Engine (Phase 7, Task P7-T4).
Reference: docs/upgrade/MASTER_10_PHASE_ROADMAP.md (Phase 7).

Formats respectful, classical astrological prose across Hindi, English, and Hinglish.
Enforces dignified phrasing, avoiding fatalism and ungrounded sensationalism.
"""

from typing import Dict, List, Optional
from enum import Enum
from pydantic import BaseModel


class LanguageStyle(str, Enum):
    PURE_HINDI = "pure_hindi"
    SCHOLARLY_ENGLISH = "scholarly_english"
    HINGLISH = "hinglish"


class StylisticFormatter:
    """Formats Evidence Pack claims into dignified classical prose."""

    @classmethod
    def format_verdict(
        cls,
        theme: str,
        confidence: float,
        style: LanguageStyle = LanguageStyle.PURE_HINDI
    ) -> str:
        pct = int(confidence * 100)
        if style == LanguageStyle.PURE_HINDI:
            if confidence >= 0.70:
                return f"{theme.capitalize()} विषय पर शास्त्र-सम्मत प्रबल अनुकूलता ({pct}% प्रमाण बल) दर्शित है।"
            elif confidence >= 0.50:
                return f"{theme.capitalize()} विषय पर मध्यम शास्त्रीय समर्थन ({pct}% प्रमाण बल) प्राप्त हो रहा है।"
            else:
                return f"{theme.capitalize()} विषय पर वर्तमान ग्रह गोचर एवं दशा में सतर्कता एवं धैर्य अपेक्षित है ({pct}% अनुकूलता)।"
        elif style == LanguageStyle.SCHOLARLY_ENGLISH:
            if confidence >= 0.70:
                return f"For {theme}, classical shastriya consensus indicates a strongly supported favorable alignment ({pct}% confidence)."
            elif confidence >= 0.50:
                return f"For {theme}, moderate astrological alignment is indicated ({pct}% confidence)."
            else:
                return f"For {theme}, deliberate progression and classical remedies are recommended ({pct}% confidence)."
        else:  # Hinglish
            if confidence >= 0.70:
                return f"{theme.capitalize()} me shastra-sammat strong favorable yog ban raha hai ({pct}% confidence)."
            elif confidence >= 0.50:
                return f"{theme.capitalize()} me moderate support hai, mehnat se fal milega ({pct}% confidence)."
            else:
                return f"{theme.capitalize()} me filhal patience aur upaay ki zaroorat hai ({pct}% confidence)."

    @classmethod
    def attach_citations(cls, text: str, citations: List[str]) -> str:
        """Attaches non-obtrusive classical citation tags at paragraph end."""
        if not citations:
            return text
        c_str = ", ".join(f"[{c}]" for c in citations)
        return f"{text}\n\n*शास्त्रीय प्रमाण संदर्भ (Classical Pramana):* {c_str}"


default_style_formatter = StylisticFormatter()

