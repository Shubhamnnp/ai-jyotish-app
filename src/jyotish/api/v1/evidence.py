"""
Evidence Pack and Domain Analysis Endpoints for JyotishOS API v1 (Phase 6, Task P6-T4).
Reference: docs/IMPLEMENTATION_PRD.md (Section 5.3, 5.4, 6.4, P6-T4).

Rules:
1. Pure calculation and grounded classical evidence generation.
2. Validates strictly against EvidencePack schema.
3. No hallucination or unprovenanced data.
"""

from typing import Dict, List, Any, Optional
from fastapi import APIRouter, HTTPException, status, Query
from pydantic import BaseModel, Field

from ...core.models import BirthData, KundaliChart
from ...core.calculator import default_chart_calculator
from ...core.varga import VargaCalculator
from ...core.ashtakavarga import AshtakavargaCalculator
from ...evidence.pack import EvidencePack, EvidencePackBuilder
from ...evidence.factors import ChartFactors, default_factor_extractor
from ...evidence.domains.analyzer import DomainSignificators, default_domain_analyzer


router = APIRouter(prefix="/evidence", tags=["v1-evidence"])


class EvidenceBuildRequest(BaseModel):
    """Payload to build a grounded Evidence Pack for a given birth profile."""
    birth_data: BirthData
    domain: str = Field(default="career", description="Domain key (e.g. career, marriage, wealth, health)")
    school: str = Field(default="parashari", description="Astrological school (parashari, jaimini, kp)")
    ayanamsa: str = Field(default="Lahiri", description="Ayanamsa system name")


class DomainSummary(BaseModel):
    """Summary of domain significators for client discovery."""
    domain: str
    display_name_en: str
    display_name_hi: str
    primary_bhavas: List[int]
    secondary_bhavas: List[int]
    karakas: List[str]
    vargas: List[str]
    disclaimer: Optional[str] = None


class SupportedDomainsResponse(BaseModel):
    """Supported domains discovery response."""
    total_domains: int
    domains: List[DomainSummary]


@router.get("/domains", response_model=SupportedDomainsResponse)
def get_supported_domains():
    """Returns all supported astrological domains and their classical significators."""
    summaries = []
    for k in default_domain_analyzer.list_available_domains():
        sig = default_domain_analyzer.get_significators(k)
        summaries.append(DomainSummary(
            domain=sig.domain,
            display_name_en=sig.display_name_en,
            display_name_hi=sig.display_name_hi,
            primary_bhavas=sig.parashari_primary_bhavas,
            secondary_bhavas=sig.parashari_secondary_bhavas,
            karakas=sig.parashari_karakas,
            vargas=sig.parashari_vargas,
            disclaimer=sig.disclaimer
        ))
    return SupportedDomainsResponse(
        total_domains=len(summaries),
        domains=summaries
    )


@router.get("/schema")
def get_evidence_pack_schema():
    """Returns the official JSON Schema for EvidencePack validation."""
    return EvidencePack.export_json_schema()


@router.post("/pack", response_model=EvidencePack)
def generate_evidence_pack(payload: EvidenceBuildRequest):
    """
    Builds a complete, grounded Evidence Pack for a birth chart and domain.
    All claims in the evidence pack are backed by verified classical rules,
    planetary dignities, Shadbala, and Shastriya Grantha citations.
    """
    domain_key = payload.domain.strip().lower()
    avail = default_domain_analyzer.list_available_domains()
    if domain_key not in avail:
        valid_domains = ", ".join(avail)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported domain '{payload.domain}'. Supported domains: {valid_domains}"
        )

    try:
        chart = default_chart_calculator.calculate_full_chart(
            payload.birth_data,
            ayanamsa_name=payload.ayanamsa
        )
        if not chart.vargas:
            chart.vargas = VargaCalculator.calculate_all_vargas(chart)
        if not chart.ashtakavarga:
            chart.ashtakavarga = AshtakavargaCalculator.calculate(chart)

        builder = EvidencePackBuilder()
        evidence_pack = builder.build_evidence_pack(
            chart=chart,
            domain=domain_key,
            school=payload.school.strip().lower()
        )
        return evidence_pack
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to assemble evidence pack: {str(e)}"
        )


@router.post("/factors", response_model=ChartFactors)
def extract_chart_factors(birth_data: BirthData, ayanamsa: str = "Lahiri"):
    """
    Extracts typed, structured chart factors (planets, houses, yogas, special lagnas)
    for downstream shastriya analysis.
    """
    try:
        chart = default_chart_calculator.calculate_full_chart(
            birth_data,
            ayanamsa_name=ayanamsa
        )
        if not chart.vargas:
            chart.vargas = VargaCalculator.calculate_all_vargas(chart)
        if not chart.ashtakavarga:
            chart.ashtakavarga = AshtakavargaCalculator.calculate(chart)

        factors = default_factor_extractor.extract_factors(chart)
        return factors
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to extract chart factors: {str(e)}"
        )

