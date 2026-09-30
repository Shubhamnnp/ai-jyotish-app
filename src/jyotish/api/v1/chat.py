"""
Conversational Astrological Consultation & Grounded AI Advisor for JyotishOS API v1.
Strictly decoupled: AI never invents coordinates or rules (Rule 4).
Always provides calibrated evidence status and Grantha references (Rule 5).
"""

from datetime import datetime, date
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from ...core.models import BirthData
from ...core.calculator import default_chart_calculator
from ...dasha.vimshottari import default_dasha_engine
from ...rules.engine import default_rules_engine
from ...ai.narrative import default_narrative_service
from .middleware import rate_limiter

router = APIRouter(prefix="/chat", tags=["v1-chat"])


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
    evidence_status: str
    confidence_score: float
    active_dasha: Dict[str, Any]
    key_planetary_influences: List[str]
    citations: List[GranthaCitation]
    consultation_narrative: str
    ethical_disclaimer: str


@router.post("/consult", response_model=AstrologicalConsultResponse, dependencies=[Depends(rate_limiter)])
def consult_astrological_advisor(payload: AstrologicalConsultRequest):
    """
    Provides a grounded Shastriya consultation response to user inquiries.
    Evaluates real astronomical positions, active dasha hierarchy, and Shastriya rules
    before generating an explainable bilingual narrative with Gemini.
    """
    try:
        chart = default_chart_calculator.calculate_chart(payload.birth_data, ayanamsa_name=payload.ayanamsa)
        
        from ...core.gochar import default_transit_engine

        # 1. Deterministic Dasha extraction
        birth_dt = datetime.combine(payload.birth_data.birth_date, payload.birth_data.birth_time)
        moon_lon = chart.planets["Moon"].longitude if "Moon" in chart.planets else 120.0
        active_hierarchy = default_dasha_engine.get_active_dasha_at(
            birth_dt=birth_dt,
            moon_lon=moon_lon,
            target_date=date.today()
        )
        
        # 2. Shastriya Rules evaluation with Inverted Index & Conflict Graph
        transits, transit_summary = default_transit_engine.compute_transit_snapshot(chart, date.today())
        rule_eval_results = default_rules_engine.evaluate_all(
            chart,
            active_hierarchy,
            transits,
            transit_summary,
            filter_theme="all",
            use_inverted_index=True
        )
        conflicts_synthesis = default_rules_engine.synthesize_conflicts(rule_eval_results, chart=chart)

        # 3. Extract top applicable citations
        citations = []
        for r in rule_eval_results[:5]:
            citations.append(GranthaCitation(
                rule_id=r.rule_id,
                source_grantha=r.source_text,
                chapter_verse=r.source_chapter or "General",
                sanskrit_shloka=None,
                meaning=r.explanation_hi if payload.language == "hi" else r.rule_name_en
            ))

        # 4. Determine Evidence Status and Confidence Score
        score = min(95.0, 50.0 + len(rule_eval_results) * 3.5 - len(conflicts_synthesis.get("cancelled_rules", [])) * 5.0)
        status = conflicts_synthesis.get("net_status", "Moderately Supported")

        # 5. Extract Key Influences
        influences = [
            f"लग्न: {chart.lagna_sign_name} ({chart.lagna_degree:.1f}°)",
            f"चंद्र राशि: {chart.planets['Moon'].sign_name} (नक्षत्र: {chart.planets['Moon'].nakshatra_name})"
        ]
        if "Jupiter" in chart.planets:
            influences.append(f"गुरु: {chart.planets['Jupiter'].sign_name} ({chart.planets['Jupiter'].house_from_lagna} भाव)")
        if "Saturn" in chart.planets:
            influences.append(f"शनि: {chart.planets['Saturn'].sign_name} ({chart.planets['Saturn'].house_from_lagna} भाव)")

        # 6. Generate Narrative
        active_dasha_summary = active_hierarchy.formatted_summary
        narrative = default_narrative_service.chat_consultation(
            user_query=payload.question,
            chart=chart,
            active_dasha_summary=active_dasha_summary,
            language="Hindi" if payload.language == "hi" else "English"
        )

        disclaimer = (
            "यह परामर्श शास्त्रीय सिद्धांतों और गणितीय ग्रहों की स्थिति पर आधारित एक सम्भावना विश्लेषण है। "
            "ज्योतिष प्रारब्ध और कर्म का मार्गदर्शन है, निश्चित भाग्य नहीं। अंतिम निर्णय व्यक्तिगत विवेक पर निर्भर है।"
            if payload.language == "hi" else
            "This consultation is an astrological probability analysis grounded in classical Granthas and mathematical planetary coordinates. "
            "Jyotish indicates karmic tendencies, not inescapable destiny. Exercise free will and personal discernment."
        )

        return AstrologicalConsultResponse(
            question=payload.question,
            language=payload.language,
            evidence_status=status,
            confidence_score=round(score, 1),
            active_dasha={
                "mahadasha": active_hierarchy.mahadasha.lord,
                "antardasha": active_hierarchy.antardasha.lord,
                "pratyantardasha": active_hierarchy.pratyantardasha.lord,
                "end_date": str(active_hierarchy.antardasha.end_date)
            },
            key_planetary_influences=influences,
            citations=citations,
            consultation_narrative=narrative,
            ethical_disclaimer=disclaimer
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Consultation processing failed: {str(e)}")
