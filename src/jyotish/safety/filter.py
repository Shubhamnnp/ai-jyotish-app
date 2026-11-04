"""
Astrological Safety Layer & Responsible Guidance Filter (Phase 5, Task P5-T7).
Reference: docs/IMPLEMENTATION_PRD.md (Section 5.4, P5-T7).

Strictly blocks and redirects:
1. Death timing & mortality dates ("when will I die", "kab marunga", "spouse death").
2. Specific clinical disease diagnosis ("do I have cancer", "cancer diagnosis").
3. Prenatal gender selection / determination (PCPNDT Act & ethical mandate).
4. Absolute financial/legal certainty ("100% lottery win guarantee", "court case guaranteed").
5. Fear-based remedy upsell and superstitious extortion.
"""

import os
import re
import yaml
from typing import Dict, List, Tuple, Optional, Any
from pydantic import BaseModel, Field


class SafetyViolationType(str):
    DEATH_TIMING = "DEATH_TIMING"
    MEDICAL_DIAGNOSIS = "MEDICAL_DIAGNOSIS"
    GENDER_SELECTION = "PRENATAL_GENDER_SELECTION"
    CERTAINTY_GUARANTEE = "CERTAINTY_GUARANTEE"
    FEAR_BASED_UPSELL = "FEAR_BASED_UPSELL"
    SAFE = "SAFE"


# Bilingual Redirection Messages
REDIRECTION_MESSAGES = {
    SafetyViolationType.DEATH_TIMING: {
        "en": (
            "Classical Jyotish regards the exact moment of physical departure as sacred and divine. "
            "In strict accordance with shastriya ethics and our non-negotiable safety policy, "
            "we do not compute or predict specific dates of mortality. "
            "For general vitality, peace, and spiritual fortitude, traditional texts recommend "
            "ethical living, medical care, and contemplation on the Maha Mrityunjaya mantra."
        ),
        "hi": (
            "शास्त्रीय ज्योतिष में आयु एवं देहावसान का समय ईश्वरीय विधान एवं प्रारब्ध के अधीन माना गया है। "
            "नैतिक मर्यादा एवं सुरक्षा नीति के अनुसार हम मृत्यु की सटीक तिथि अथवा समय की भविष्यवाणी नहीं करते हैं। "
            "जीवन शक्ति, स्वास्थ्य एवं आत्म-शांति हेतु शास्त्र महामृत्युंजय मंत्र जप एवं सदाचार का परामर्श देते हैं।"
        )
    },
    SafetyViolationType.MEDICAL_DIAGNOSIS: {
        "en": (
            "Astrological consultations cannot provide clinical medical diagnosis, disease identification, "
            "or treatment prescriptions. For any physical or psychological health concerns, "
            "please consult a qualified, licensed healthcare professional or medical doctor immediately."
        ),
        "hi": (
            "ज्योतिषीय परामर्श किसी भी नैदानिक रोग निदान (Medical Diagnosis) अथवा चिकित्सीय उपचार का विकल्प नहीं है। "
            "किसी भी शारीरिक अथवा मानसिक स्वास्थ्य संबंधी संशय के लिए कृपया तुरंत योग्य एवं प्रमाणित चिकित्सक से परामर्श लें।"
        )
    },
    SafetyViolationType.GENDER_SELECTION: {
        "en": (
            "In strict adherence to the Pre-Conception and Pre-Natal Diagnostic Techniques (PCPNDT) Act "
            "and ethical principles, determination or prediction of fetal gender is strictly prohibited."
        ),
        "hi": (
            "गर्भस्थ शिशु के लिंग की भविष्यवाणी अथवा निर्धारण कानूनन (PCPNDT Act) एवं नैतिक रूप से पूर्णतः निषिद्ध है।"
        )
    },
    SafetyViolationType.CERTAINTY_GUARANTEE: {
        "en": (
            "Astrological indications represent traditional tendencies and karmic potentials, never absolute guarantees. "
            "Outcomes in legal matters, financial investments, and life events remain subject to human effort, "
            "due diligence, and ethical responsibility."
        ),
        "hi": (
            "ज्योतिषीय विश्लेषण शास्त्रीय प्रवृत्तियों एवं संभावनाओं का मार्गदर्शन है, कोई निश्चित या 100% गारंटी नहीं। "
            "न्यायिक एवं वित्तीय निर्णयों में यथार्थपरक प्रयास एवं विवेक अनिवार्य है।"
        )
    },
    SafetyViolationType.FEAR_BASED_UPSELL: {
        "en": (
            "Our ethical standards strictly prohibit fear-mongering, curses, or superstitious exploitation. "
            "Remedies in Jyotish are purely spiritual, reflective, and charitable in nature."
        ),
        "hi": (
            "भय दिखाने, शाप का भय दिखाकर अनुष्ठान बेचने अथवा अंधविश्वास को बढ़ावा देने वाले आचरण पूर्णतः प्रतिबंधित हैं।"
        )
    }
}


# Regex Patterns for Sensitive Inquiries
PATTERNS = {
    SafetyViolationType.DEATH_TIMING: [
        r"\b(when\s+will\s+i\s+die|exact\s+date\s+of\s+(my\s+|the\s+)?death|death\s+date|date\s+of\s+(my\s+)?death|day\s+of\s+(my\s+)?death)\b",
        r"\b(kab\s+marunga|meri\s+maut\s+kab\s+hogi|mrityu\s+kab\s+hogi|mrityu\s+ki\s+tarikh)\b",
        r"\b(when\s+will\s+my\s+spouse\s+die|pati\s+ki\s+mrityu|patni\s+ki\s+mrityu)\b",
        r"\b(exact\s+age\s+of\s+death|marne\s+ki\s+umra)\b"
    ],
    SafetyViolationType.MEDICAL_DIAGNOSIS: [
        r"\b(do\s+i\s+have\s+cancer|diagnose\s+my\s+disease|cure\s+cancer\s+with\s+astrology)\b",
        r"\b(cancer\s+hai\s+kya|heart\s+attack|kidney\s+fail|organ\s+failure)\b",
        r"\b(astrology\s+cure\s+for\s+tumor|disease\s+diagnosis)\b"
    ],
    SafetyViolationType.GENDER_SELECTION: [
        r"\b(will\s+i\s+have\s+a\s+boy\s+or\s+girl|gender\s+of\s+(the\s+|my\s+)?(baby|child|fetus))\b",
        r"\b(beta\s+hoga\s+ya\s+beti|ladka\s+hoga\s+ya\s+ladki|garbh\s+mein\s+kya\s+hai)\b",
        r"\b(sex\s+determination\s+of\s+child)\b"
    ],
    SafetyViolationType.CERTAINTY_GUARANTEE: [
        r"\b(100%\s+guaranteed\s+lottery|sure\s+jackpot\s+numbers|guaranteed\s+court\s+win)\b",
        r"\b(pakka\s+lottery\s+lagegi|100%\s+case\s+jeetunga)\b"
    ],
    SafetyViolationType.FEAR_BASED_UPSELL: [
        r"\b(curse\s+will\s+destroy\s+you|pay\s+money\s+to\s+avert\s+death)\b",
        r"\b(sarpa\s+shrap\s+se\s+maut\s+hogi|rupaye\s+do\s+warna\s+mar\s+jaoge)\b"
    ]
}


class SafetyCheckResult(BaseModel):
    is_safe: bool
    violation_type: str = SafetyViolationType.SAFE
    redirection_message_en: str = ""
    redirection_message_hi: str = ""
    matched_pattern: Optional[str] = None


class RemedyItem(BaseModel):
    remedy_id: str
    planet: str
    type: str  # 'mantra', 'daan', 'gemstone', 'lifestyle'
    title_en: str
    title_hi: str
    description_en: str
    description_hi: str
    source_text: str
    source_chapter: str
    caution_text: str
    is_fear_based: bool = False


class AstrologicalSafetyFilter:
    """Detects safety violations, redirects harmful inquiries, and serves verified remedies."""

    def __init__(self, remedies_yaml_path: Optional[str] = None):
        if remedies_yaml_path is None:
            # Look in data/remedies.yaml
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
            remedies_yaml_path = os.path.join(base_dir, "data", "remedies.yaml")
        self.remedies_yaml_path = remedies_yaml_path
        self._remedies: List[RemedyItem] = []
        self._load_remedies()

    def _load_remedies(self):
        if os.path.exists(self.remedies_yaml_path):
            with open(self.remedies_yaml_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
                if isinstance(data, dict) and "remedies" in data:
                    for r in data["remedies"]:
                        self._remedies.append(RemedyItem(**r))

    def check_safety(self, text: str) -> SafetyCheckResult:
        """Inspects query or generated text for ethical and legal safety violations."""
        if not text:
            return SafetyCheckResult(is_safe=True)

        text_lower = text.lower().strip()

        for v_type, pattern_list in PATTERNS.items():
            for pat in pattern_list:
                if re.search(pat, text_lower, re.IGNORECASE):
                    msg_bundle = REDIRECTION_MESSAGES.get(v_type, REDIRECTION_MESSAGES[SafetyViolationType.FEAR_BASED_UPSELL])
                    return SafetyCheckResult(
                        is_safe=False,
                        violation_type=v_type,
                        redirection_message_en=msg_bundle["en"],
                        redirection_message_hi=msg_bundle["hi"],
                        matched_pattern=pat
                    )

        return SafetyCheckResult(is_safe=True)

    def get_verified_remedies_for_planet(self, planet_name: str) -> List[RemedyItem]:
        """Returns non-fear-based, source-referenced classical remedies for planet."""
        p_clean = planet_name.strip().capitalize()
        matched = [r for r in self._remedies if r.planet.capitalize() in (p_clean, "Universal")]
        return matched

    def sanitize_output(self, generated_text: str, language: str = "en") -> Tuple[bool, str]:
        """
        Scans output text. If a safety violation is detected, replaces the text
        with the appropriate compassionate redirection message.
        """
        check = self.check_safety(generated_text)
        if check.is_safe:
            return True, generated_text

        is_hi = language.strip().lower() in ("hi", "hindi")
        safe_msg = check.redirection_message_hi if is_hi else check.redirection_message_en
        return False, safe_msg

    @classmethod
    def validate_query(cls, text: str) -> Tuple[bool, str]:
        """Convenience class method to check query against safety boundaries."""
        check = default_safety_filter.check_safety(text)
        if check.is_safe:
            return True, ""
        return False, check.redirection_message_hi or check.redirection_message_en


default_safety_filter = AstrologicalSafetyFilter()
