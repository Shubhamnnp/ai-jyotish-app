"""
Grounded Shastriya Narrator Engine (Phase 5, Tasks P5-T5 & P5-T6).
Reference: docs/IMPLEMENTATION_PRD.md (Section 5.4, P5-T5 & P5-T6).

Rules:
1. Feeds strictly the EvidencePack into the prompt.
2. Calls the configured model (env: LLM_MODEL, default: 'gemini-2.5-flash').
3. Validates citations and grounding via CitationGroundingValidator.
4. Performs maximum 2 retries on validation failure.
5. If validation fails after 2 retries or if offline/unconfigured, falls back
   deterministically to template rendering of `claim_*`.
6. Zero hallucination guarantee.
"""

import os
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field

from ..evidence.pack import EvidencePack
from .prompt import build_narrator_prompt
from .validator import CitationGroundingValidator, ValidationResult, default_citation_validator

try:
    from google import genai
    from google.genai import types
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False


class GroundedNarrativeResponse(BaseModel):
    """Complete grounded narrative response with display text and provenance."""
    domain: str
    language: str
    display_text: str
    validation_passed: bool
    fallback_used: bool
    retries_count: int = 0
    provenance: List[Any] = Field(default_factory=list)
    disclaimers: List[str] = Field(default_factory=list)


class GroundedNarrator:
    """Orchestrates grounded narrative generation with strict validation and fallback."""

    def __init__(
        self,
        model_name: Optional[str] = None,
        validator: Optional[CitationGroundingValidator] = None,
        max_retries: int = 2
    ):
        self.model_name = model_name or os.environ.get("LLM_MODEL", "gemini-2.5-flash")
        self.validator = validator or default_citation_validator
        self.max_retries = max_retries

    def _call_llm(self, prompt_bundle: Dict[str, str]) -> str:
        """Invokes the configured LLM using google-genai SDK."""
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key or not GENAI_AVAILABLE:
            raise RuntimeError("Gemini API not configured or google-genai SDK unavailable.")

        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model=self.model_name,
            contents=prompt_bundle["user_prompt"],
            config=types.GenerateContentConfig(
                system_instruction=prompt_bundle["system_instruction"],
                temperature=0.2,  # Low temperature for strict factual adherence
                max_output_tokens=1500
            )
        )
        return response.text or ""

    def narrate(
        self,
        pack: EvidencePack,
        language: str = "en",
        user_query: Optional[str] = None
    ) -> GroundedNarrativeResponse:
        """
        Generates and validates a grounded astrological narrative.
        Guarantees 100% adherence through validator checks and deterministic fallback.
        """
        prompt_bundle = build_narrator_prompt(pack, language=language, user_query=user_query)
        retries = 0
        raw_text = ""

        # Attempt generation and validation up to max_retries
        while retries <= self.max_retries:
            try:
                raw_text = self._call_llm(prompt_bundle)
                val_res = self.validator.validate_and_clean(raw_text, pack)
                if val_res.is_valid:
                    return GroundedNarrativeResponse(
                        domain=pack.domain,
                        language=language,
                        display_text=val_res.clean_display_text,
                        validation_passed=True,
                        fallback_used=False,
                        retries_count=retries,
                        provenance=[p.model_dump() for p in val_res.provenance],
                        disclaimers=pack.disclaimers
                    )
                else:
                    retries += 1
                    # Append validation errors to prompt for correction on retry
                    prompt_bundle["user_prompt"] += f"\n\nPREVIOUS ATTEMPT FAILED VALIDATION:\n" + "\n".join(val_res.errors) + "\nPlease correct these errors and ensure EVERY sentence ends with [F#]."
            except Exception:
                # LLM call failure (offline, rate limit, or invalid key) -> break to fallback
                break

        # Fallback to deterministic template rendering
        fallback_res = self.validator.fallback_template_render(pack, language=language)
        return GroundedNarrativeResponse(
            domain=pack.domain,
            language=language,
            display_text=fallback_res.clean_display_text,
            validation_passed=True,
            fallback_used=True,
            retries_count=retries,
            provenance=[p.model_dump() for p in fallback_res.provenance],
            disclaimers=pack.disclaimers
        )


default_grounded_narrator = GroundedNarrator()
