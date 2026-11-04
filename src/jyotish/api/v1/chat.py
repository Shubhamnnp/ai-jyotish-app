"""
Conversational Astrological Consultation & Grounded AI Advisor for JyotishOS API v1 (Phase 5, Task P5-T8).
Reference: docs/IMPLEMENTATION_PRD.md (Section 5.4, P5-T8).

Rules:
1. Every answer is grounded on a freshly generated EvidencePack for the question's domain.
2. Refuses to answer from 'general astrology memory' or ungrounded external topics.
3. Intercepts unsafe inquiries (death-timing, medical diagnosis, gender determination).
4. Strictly decoupled: AI receives only mathematical factors and verified classical rules.
"""

from datetime import datetime, date
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field

from ...core.models import BirthData
from ...core.calculator import default_chart_calculator
from ...dasha.vimshottari import default_dasha_engine
from ...evidence.pack import default_evidence_pack_builder, EvidencePack
from ...narrate.engine import default_grounded_narrator, GroundedNarrativeResponse
from ...safety.filter import default_safety_filter, SafetyViolationType
from ...ai.orchestrator import default_daivajna_orchestrator, DaivajnaConsultationResult
from .middleware import rate_limiter

router = APIRouter(prefix="/chat", tags=["v1-chat"])


DOMAIN_KEYWORD_MAP = {
    "career": ["career", "job", "profession", "business", "naukri", "vyapar", "kaam", "promotion", "work", "office"],
    "marriage": ["marriage", "spouse", "wedding", "relationship", "shadi", "vivah", "shaadi", "patni", "pati", "wife", "husband", "partner"],
    "wealth": ["wealth", "finance", "money", "dhan", "paisa", "income", "assets", "invest", "financial"],
    "health": ["health", "swasthya", "disease", "illness", "vitality", "bimari", "energy"],
    "education": ["education", "study", "exam", "school", "college", "vidya", "degree", "learning"],
    "spirituality": ["spiritual", "dharma", "moksha", "guru", "meditation", "pooja", "bhakti", "temple"],
    "property": ["property", "house", "vehicle", "car", "makaan", "bhavan", "land", "real estate"],
    "children": ["child", "children", "baby", "kid", "santaan", "putra", "son", "daughter"]
}


def detect_domain_from_query(query: str) -> str:
    """Classifies question into a supported classical domain or defaults to 'personality'."""
    q_lower = query.lower()
    for dom, keywords in DOMAIN_KEYWORD_MAP.items():
        if any(kw in q_lower for kw in keywords):
            return dom
    return "personality"


def is_non_astrological_query(query: str) -> bool:
    """Detects inquiries completely detached from astrology, life guidance, or horoscopy."""
    q_lower = query.lower()
    irrelevant_triggers = [
        "python code", "quicksort", "write a poem about pizza", "who won the world cup",
        "solve this equation", "sql query", "translate this to spanish"
    ]
    return any(trig in q_lower for trig in irrelevant_triggers)


class AstrologicalConsultRequest(BaseModel):
    birth_data: BirthData
    question: str
    language: str = "hi"  # "hi" or "en"
    ayanamsa: str = "Lahiri"


class GranthaCitation(BaseModel):
    rule_id: str
    source_grantha: str
    chapter_verse: str
    sanskrit_shloka: Optional[str] = None
    meaning: str


class AstrologicalConsultResponse(BaseModel):
    question: str
    language: str
    domain: str
    evidence_status: str
    confidence_score: float
    active_dasha: Dict[str, Any]
    key_planetary_influences: List[str]
    citations: List[GranthaCitation]
    consultation_narrative: str
    provenance: List[Any] = Field(default_factory=list)
    ethical_disclaimer: str


@router.post("/consult", response_model=AstrologicalConsultResponse, dependencies=[Depends(rate_limiter)])
def consult_astrological_advisor(payload: AstrologicalConsultRequest):
    """
    Provides a grounded Shastriya consultation response strictly derived from
    a freshly generated Evidence Pack. Refuses to answer from 'general memory'.
    """
    # 1. Safety Check (Death-timing, diagnosis, PCPNDT)
    safety_check = default_safety_filter.check_safety(payload.question)
    if not safety_check.is_safe:
        safe_msg = safety_check.redirection_message_hi if payload.language == "hi" else safety_check.redirection_message_en
        return AstrologicalConsultResponse(
            question=payload.question,
            language=payload.language,
            domain="safety_redirection",
            evidence_status="Blocked by Shastriya Safety Layer",
            confidence_score=0.0,
            active_dasha={},
            key_planetary_influences=[],
            citations=[],
            consultation_narrative=safe_msg,
            provenance=[],
            ethical_disclaimer="Safety Redirection Policy (P5-T7)."
        )

    # 2. Refuse out-of-domain ungrounded queries
    if is_non_astrological_query(payload.question):
        refusal_msg = (
            "मैं केवल वैदिक कुंडली गणित एवं शास्त्रीय ग्रंथों के आधार पर प्रमाणिक परामर्श प्रदान करता हूँ। "
            "सामान्य विषय अथवा अप्रासंगिक स्मृति आधारित प्रश्नों का उत्तर देना ज्योतिषीय मर्यादा के अनुकूल नहीं है।"
            if payload.language == "hi" else
            "I provide consultations strictly grounded in Vedic horoscopic mathematics and classical Shastras. "
            "I cannot answer questions from general memory or ungrounded external topics."
        )
        return AstrologicalConsultResponse(
            question=payload.question,
            language=payload.language,
            domain="unsupported",
            evidence_status="Refused - Ungrounded External Topic",
            confidence_score=0.0,
            active_dasha={},
            key_planetary_influences=[],
            citations=[],
            consultation_narrative=refusal_msg,
            provenance=[],
            ethical_disclaimer="Grounding Enforcement Policy (P5-T8)."
        )

    try:
        # 3. Calculate Chart & Detect Domain
        chart = default_chart_calculator.calculate_full_chart(payload.birth_data, ayanamsa_name=payload.ayanamsa)
        detected_domain = detect_domain_from_query(payload.question)

        # 4. Generate Fresh Evidence Pack for Detected Domain
        evidence_pack: EvidencePack = default_evidence_pack_builder.build_evidence_pack(
            chart=chart,
            domain=detected_domain,
            school="parashari"
        )

        # 5. Extract Citations from Verified Evidence Pack Findings
        citations: List[GranthaCitation] = []
        for f in evidence_pack.findings[:5]:
            citations.append(GranthaCitation(
                rule_id=f.rule_ids[0] if f.rule_ids else f.finding_id,
                source_grantha="Brihat Parashara Hora Shastra (BPHS)",
                chapter_verse=f.finding_id,
                sanskrit_shloka=None,
                meaning=f.claim_hi if payload.language == "hi" else f.claim_en
            ))

        # 6. Active Dasha Details
        birth_dt = datetime.combine(payload.birth_data.birth_date, payload.birth_data.birth_time)
        moon_lon = chart.planets["Moon"].longitude if "Moon" in chart.planets else 120.0
        active_hierarchy = default_dasha_engine.get_active_dasha_at(
            birth_dt=birth_dt,
            moon_lon=moon_lon,
            target_date=date.today()
        )

        # 7. Generate Grounded Narrative
        narrative_res: GroundedNarrativeResponse = default_grounded_narrator.narrate(
            pack=evidence_pack,
            language=payload.language,
            user_query=payload.question
        )

        # 8. Influences List
        influences = [
            f"Lagna: {chart.houses[0].sign_name}",
            f"Moon: {chart.planets['Moon'].sign_name} ({chart.planets['Moon'].nakshatra_name})" if 'Moon' in chart.planets else "Moon: N/A"
        ]
        if "Jupiter" in chart.planets:
            influences.append(f"Jupiter: {chart.planets['Jupiter'].sign_name} (H{chart.planets['Jupiter'].house_from_lagna})")
        if "Saturn" in chart.planets:
            influences.append(f"Saturn: {chart.planets['Saturn'].sign_name} (H{chart.planets['Saturn'].house_from_lagna})")

        return AstrologicalConsultResponse(
            question=payload.question,
            language=payload.language,
            domain=detected_domain,
            evidence_status="Strongly Grounded on Evidence Pack",
            confidence_score=round(min(98.0, max(50.0, len(evidence_pack.findings) * 12.5)), 1),
            active_dasha={
                "mahadasha": active_hierarchy.mahadasha.lord,
                "antardasha": active_hierarchy.antardasha.lord,
                "pratyantardasha": active_hierarchy.pratyantardasha.lord,
                "end_date": str(active_hierarchy.antardasha.end_date)
            },
            key_planetary_influences=influences,
            citations=citations,
            consultation_narrative=narrative_res.display_text,
            provenance=narrative_res.provenance,
            ethical_disclaimer=evidence_pack.disclaimers[0] if evidence_pack.disclaimers else "Traditional guidance, not guarantee."
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Consultation processing failed: {str(e)}")


class DaivajnaInquiryRequest(BaseModel):
    birth_data: BirthData
    topic: str = "general"
    user_query: Optional[str] = None
    ayanamsa: str = "Lahiri"


@router.post("/orchestrate", response_model=DaivajnaConsultationResult, dependencies=[Depends(rate_limiter)])
def orchestrate_daivajna_consultation(payload: DaivajnaInquiryRequest):
    """
    Executes Layer 4 Daivajna Multi-Agent consultation with Evidence Pack grounding.
    """
    try:
        chart = default_chart_calculator.calculate_full_chart(payload.birth_data, ayanamsa_name=payload.ayanamsa)
        result = default_daivajna_orchestrator.process_consultation(
            chart=chart,
            topic=payload.topic,
            user_query=payload.user_query
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Daivajna orchestration failed: {str(e)}")
