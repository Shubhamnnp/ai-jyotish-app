"""
Enterprise Dossier & Report Exporting Gateway for JyotishOS API v1.
Generates exhaustive 50+ page publication-quality Master Natal Kundali dossiers,
white-label astrologer headers, and Shastriya Event Verification certificates.
"""

from datetime import datetime, date
from typing import Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, Response
from pydantic import BaseModel

from ...core.models import BirthData
from ...core.calculator import default_chart_calculator
from ...services.report_generator import NatalReportGenerator
from ...events.past_verification import PastEventVerificationEngine, default_past_event_engine
from .middleware import require_tier, SubscriptionTier

router = APIRouter(prefix="/reports", tags=["v1-reports"])
report_gen = NatalReportGenerator()


class MasterReportRequest(BaseModel):
    birth_data: BirthData
    ayanamsa: str = "Lahiri"
    astro_name: Optional[str] = "ज्योतिषाचार्य पं. शुभम तिवारी"
    astro_phone: Optional[str] = "+91-9452155742"
    astro_org: Optional[str] = "वैदिक ज्योतिष अनुसंधान केंद्र"


class VerificationCertificateRequest(BaseModel):
    birth_data: BirthData
    event_theme: str  # marriage, career_breakthrough, property_purchase, accident_illness
    query_text: str
    event_start_year: int
    event_end_year: int
    prashna_number: Optional[int] = None
    astro_name: Optional[str] = "ज्योतिषाचार्य पं. शुभम तिवारी"
    astro_org: Optional[str] = "वैदिक ज्योतिष अनुसंधान केंद्र"


@router.post("/master-html", dependencies=[Depends(require_tier(SubscriptionTier.PRO))])
def generate_master_natal_html_report(payload: MasterReportRequest):
    """
    Generates a 50+ Page Comprehensive Master Natal Report (सम्पूर्ण वृहद जन्म पत्रिका महा-दस्तावेज़)
    in full publication-ready HTML format with SVG charts, Panchang, Vargas, Shadbala, and Remedies.
    Requires PRO or ENTERPRISE subscription tier.
    """
    try:
        chart = default_chart_calculator.calculate_chart(payload.birth_data, ayanamsa_name=payload.ayanamsa)
        html_content = report_gen.generate_html_report(
            chart=chart,
            astro_name=payload.astro_name,
            astro_phone=payload.astro_phone,
            astro_org=payload.astro_org
        )
        return Response(
            content=html_content,
            media_type="text/html",
            headers={"Content-Disposition": f'inline; filename="Kundali_Master_{payload.birth_data.name}.html"'}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate master report: {str(e)}")


@router.post("/event-verification-certificate", dependencies=[Depends(require_tier(SubscriptionTier.PRO))])
def generate_event_verification_certificate(payload: VerificationCertificateRequest):
    """
    Generates a certified Shastriya Event Verification Dossier across the 6 Classical Pillars.
    Requires PRO or ENTERPRISE subscription tier.
    """
    try:
        chart = default_chart_calculator.calculate_chart(payload.birth_data)
        from ...events.past_verification import PastEventVerificationInput
        from datetime import date
        
        inp = PastEventVerificationInput(
            birth_data=payload.birth_data,
            event_theme=payload.event_theme,
            query_text=payload.query_text,
            target_date=date(payload.event_start_year, 1, 1),
            search_window_start=date(payload.event_start_year, 1, 1),
            search_window_end=date(payload.event_end_year, 12, 31)
        )
        verification_result = default_past_event_engine.verify_past_event(
            inp=inp,
            precomputed_chart=chart
        )

        now_str = datetime.now().strftime('%d-%m-%Y %H:%M')
        score_pct = verification_result.confidence_score * 100.0
        p2 = verification_result.pillar_2_prashna_evidence or {}
        p6_rules = verification_result.pillar_6_rules_evidence.get("active_rules", [])
        p6_cancels = verification_result.pillar_6_rules_evidence.get("cancellations", [])

        # Generate elegant certified HTML certificate
        cert_html = f"""<!DOCTYPE html>
<html lang="hi">
<head>
<meta charset="utf-8">
<title>Shastriya Event Verification Certificate - {payload.birth_data.name}</title>
<style>
    body {{ font-family: 'Segoe UI', Arial, sans-serif; background: #0f172a; color: #f8fafc; padding: 40px; margin: 0; }}
    .cert-box {{ border: 3px double #d97706; padding: 30px; border-radius: 12px; background: #1e293b; max-width: 900px; margin: 0 auto; box-shadow: 0 10px 25px rgba(0,0,0,0.5); }}
    .header {{ text-align: center; border-bottom: 2px solid #b45309; padding-bottom: 15px; margin-bottom: 20px; }}
    .header h1 {{ color: #fbbf24; margin: 0; font-size: 24px; }}
    .header p {{ color: #94a3b8; margin: 5px 0 0 0; font-size: 14px; }}
    .status-badge {{ display: inline-block; padding: 8px 18px; border-radius: 20px; font-weight: bold; font-size: 16px; background: #d97706; color: white; margin: 15px 0; }}
    .pillars-grid {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px; margin-top: 20px; }}
    .pillar-card {{ background: #0f172a; border-left: 4px solid #f59e0b; padding: 12px 16px; border-radius: 6px; }}
    .pillar-title {{ font-weight: bold; color: #fcd34d; font-size: 14px; margin-bottom: 4px; }}
    .pillar-desc {{ color: #cbd5e1; font-size: 12px; line-height: 1.4; }}
    .footer {{ margin-top: 30px; border-top: 1px solid #334155; padding-top: 15px; display: flex; justify-content: space-between; font-size: 12px; color: #94a3b8; }}
</style>
</head>
<body>
<div class="cert-box">
    <div class="header">
        <h1>{payload.astro_org}</h1>
        <p>प्रमाणित भूतपूर्व घटना ज्योतिषीय सत्यापन पत्र (Shastriya Retrospective Verification Certificate)</p>
        <p>परीक्षक ज्योतिषाचार्य: <b>{payload.astro_name}</b> | दिनांक: {now_str}</p>
    </div>

    <div style="text-align: center;">
        <div class="status-badge">शास्त्रीय निष्कर्ष: {verification_result.status.value.upper()} (प्रमाण स्कोर: {score_pct:.1f}/100)</div>
        <p style="font-style: italic; color: #e2e8f0; font-size: 14px;">"{verification_result.query_text}"</p>
    </div>

    <div style="background: rgba(245, 158, 11, 0.1); border: 1px solid #b45309; padding: 15px; border-radius: 8px; margin: 20px 0;">
        <h4 style="margin: 0 0 8px 0; color: #fbbf24;">शास्त्रीय विवेचना (Sanskrit Shastriya Assessment)</h4>
        <p style="margin: 0; font-size: 13px; line-height: 1.6; color: #f1f5f9;">{verification_result.ai_explanation_hi}</p>
    </div>

    <h3 style="color: #fbbf24; border-bottom: 1px solid #475569; padding-bottom: 5px;">षट्-स्तंभ सत्यापन रिपोर्ट (6-Pillar Evidence Breakdown)</h3>
    <div class="pillars-grid">
        <div class="pillar-card">
            <div class="pillar-title">1. जन्म लग्न (D1 Potential)</div>
            <div class="pillar-desc">समर्थक: {verification_result.pillar_1_d1_evidence.get("supporting_factors", [])}<br>बाधक: {verification_result.pillar_1_d1_evidence.get("inhibiting_factors", [])}</div>
        </div>
        <div class="pillar-card">
            <div class="pillar-title">2. प्रश्न कुण्डली (Horary Overlay)</div>
            <div class="pillar-desc">कार्येश: {p2.get("karyesh", "N/A")}<br>इत्थशाल योग: {p2.get("itthashala_formed", False)}</div>
        </div>
        <div class="pillar-card">
            <div class="pillar-title">3. सूक्ष्म वर्ग (Divisional Varga)</div>
            <div class="pillar-desc">वर्ग: {verification_result.pillar_3_varga_evidence.get("varga_code", "D9")}<br>लग्न/कारक: {verification_result.pillar_3_varga_evidence.get("karaka_strength", "Balavan")}</div>
        </div>
        <div class="pillar-card">
            <div class="pillar-title">4. विंशोत्तरी दशा (Dasha Operating)</div>
            <div class="pillar-desc">महादशा: {verification_result.pillar_4_dasha_evidence.get("mahadasha", "N/A")} &bull; अंतर्दशा: {verification_result.pillar_4_dasha_evidence.get("antardasha", "N/A")}</div>
        </div>
        <div class="pillar-card">
            <div class="pillar-title">5. द्वि-गोचर (Double Transit Guru-Shani)</div>
            <div class="pillar-desc">सक्रियता: {verification_result.pillar_5_transit_evidence.get("transit_alignment", "Neutral")}</div>
        </div>
        <div class="pillar-card">
            <div class="pillar-title">6. शास्त्रीय सूत्र (Classical Rules & Cancellations)</div>
            <div class="pillar-desc">कुल सूत्र: {len(p6_rules)} | निरस्त/भंगा: {len(p6_cancels)}</div>
        </div>
    </div>

    <div class="footer">
        <div>संस्थान: {payload.astro_org}</div>
        <div>प्रमाणीकरण कोड: JYOTISH-CERT-{verification_result.event_theme.upper()}-{payload.event_start_year}</div>
        <div>हस्ताक्षर: {payload.astro_name}</div>
    </div>
</div>
</body>
</html>
"""
        return Response(
            content=cert_html,
            media_type="text/html",
            headers={"Content-Disposition": f'inline; filename="Verification_{payload.event_theme}_{payload.birth_data.name}.html"'}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Verification certificate generation failed: {str(e)}")
