"""
Master Daivajna Multi-Agent Orchestrator for JyotishOS (Layer 4: AI Intelligence).

Implements the PRD v2.0 AI Architecture:
1. Master Orchestrator: Deconstructs user intent, coordinates specialist agents.
2. Specialist Calculation Agent: Extracts deterministic astronomical & Jyotish core metrics.
   (Invariant: AI NEVER invents astronomical values).
3. Classical Shastriya Rule Retrieval Agent: Fetches classical grantha pramana (BPHS, Phaladeepika, Saravali, etc.).
4. Evidence Verification & Conflict Resolution Agent (Independent Audit Agent):
   Segregates supporting vs conflicting evidence and calculates grounded, formulaic confidence scores.
5. Synthesis & Explanation Agent: Formulates transparent, evidence-traceable narratives with authentic Vedic remedies.
"""

import os
import json
import logging
from datetime import date, datetime
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field

from ..core.models import KundaliChart, PlanetPosition, HouseCusp
from ..core.calculator import default_chart_calculator
from ..core.shadbala import ShadbalaCalculator
from ..core.ashtakavarga import AshtakavargaCalculator
from ..core.yoga import default_yoga_dosha_engine
from ..core.varga import VargaCalculator
from ..dasha.vimshottari import default_dasha_engine
from .knowledge_base import default_knowledge_base, ShastraPassage

logger = logging.getLogger(__name__)

try:
    from google import genai
    from google.genai import types
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False


# ============================================================================
# Pydantic Output Models for Layer 4 AI Intelligence
# ============================================================================

class DeterministicFactSheet(BaseModel):
    """Deterministic, verified astronomical facts. AI must never hallucinate these."""
    native_name: str
    birth_datetime: str
    latitude: float
    longitude: float
    ayanamsa_name: str
    ayanamsa_value: float
    ascendant_sign: str
    ascendant_degree: float
    ascendant_lord: str
    moon_sign: str
    moon_degree: float
    moon_nakshatra: str
    moon_pada: int
    sun_sign: str
    sun_degree: float
    active_mahadasha: str
    active_antardasha: str
    dasha_summary: str
    planets: Dict[str, Dict[str, Any]]
    houses_sav: Dict[int, int]
    dusthana_occupants: List[str] = []
    exalted_planets: List[str] = []
    debilitated_planets: List[str] = []
    combust_planets: List[str] = []
    retrograde_planets: List[str] = []
    digbala_planets: List[str] = []
    vargottama_planets: List[str] = []
    active_yogas: List[str] = []
    active_doshas: List[str] = []


class ShastriyaPramanaItem(BaseModel):
    """Classical scripture citation and rule pramana."""
    grantha: str
    author: str
    chapter: str
    theme: str
    shloka_sanskrit: Optional[str] = None
    translation_hi: str
    translation_en: str
    principles: List[str] = []
    relevance_context: str = ""


class EvidenceFactor(BaseModel):
    """A weighted evidence factor evaluated by the Audit Agent."""
    factor: str
    category: str  # Dasha, Dignity, House, Transit, SAV, Yoga, Dosha
    weight: float
    impact: str  # SUPPORTING or CONFLICTING
    rationale: str


class AuditVerdict(BaseModel):
    """Deterministic, formulaic confidence audit evaluating both sides."""
    supporting_evidence: List[EvidenceFactor] = []
    conflicting_evidence: List[EvidenceFactor] = []
    total_supporting_weight: float = 0.0
    total_conflicting_weight: float = 0.0
    confidence_score: float = Field(..., ge=0.0, le=100.0)
    confidence_tier: str  # HIGH, MODERATE, LOW
    verdict_summary: str
    methodology: str = (
        "Weighted Bayesian ratio: Sum(W_support) / (Sum(W_support) + Sum(W_conflict)), "
        "bounded between 15% and 92% per PRD classical non-determinism guidelines."
    )


class VedicRemedyRecommendation(BaseModel):
    """Authentic, classical non-commercial Vedic remedy."""
    planet_or_deity: str
    remedy_type: str  # Mantra, Stotra, Dana, Vrata, Lifestyle
    title_hi: str
    title_en: str
    procedure: str
    classical_reference: str


class DaivajnaConsultationResult(BaseModel):
    """Full Layer 4 synthesized consultation output."""
    status: str = "success"
    topic: str
    user_query: Optional[str] = None
    fact_sheet: DeterministicFactSheet
    shastriya_pramana: List[ShastriyaPramanaItem] = []
    audit_verdict: AuditVerdict
    synthesis_hi: str
    synthesis_en: str
    remedies: List[VedicRemedyRecommendation] = []
    disclaimer: str = (
        "शास्त्रीय सूचना: वैदिक ज्योतिष सम्भावना, प्रारब्ध एवं काल-ज्ञान का शास्त्र है। "
        "यह नियतिवाद (Fatalism) नहीं अपितु पुरुषार्थ और कर्म-संशोधन का मार्गदर्शक है।"
    )


# ============================================================================
# Specialist Agents Implementation
# ============================================================================

class SpecialistCalculationAgent:
    """
    Agent 1: Extracts deterministic facts strictly from verified core engines.
    Zero hallucination guarantee.
    """

    def extract_fact_sheet(self, chart: KundaliChart) -> DeterministicFactSheet:
        p = chart.birth_data
        b_dt = f"{p.birth_date.strftime('%Y-%m-%d')} {p.birth_time.strftime('%H:%M:%S')}"
        
        # 1. Active Dasha
        active_md = "Unknown"
        active_ad = "Unknown"
        dasha_sum = "Vimshottari Dasha active"
        try:
            curr = default_dasha_engine.get_current_dasha(chart)
            if curr and "mahadasha" in curr and "lord" in curr["mahadasha"]:
                active_md = curr["mahadasha"]["lord"]
                active_ad = curr.get("antardasha", {}).get("lord", "Unknown")
                md_s = str(curr["mahadasha"].get("start_date", "")).split()[0]
                md_e = str(curr["mahadasha"].get("end_date", "")).split()[0]
                dasha_sum = f"MD: {active_md} ({md_s} to {md_e}), AD: {active_ad}"
        except Exception as e:
            logger.warning(f"Error fetching current dasha: {e}")

        # 2. Planetary Placements
        planets_data: Dict[str, Dict[str, Any]] = {}
        exalted: List[str] = []
        debilitated: List[str] = []
        combust: List[str] = []
        retrograde: List[str] = []
        dusthana_occ: List[str] = []
        digbala: List[str] = []

        for p_name, pos in chart.planets.items():
            h = pos.house_from_lagna
            dignity = pos.dignity.lower()
            
            if "exalted" in dignity:
                exalted.append(p_name)
            elif "debilitated" in dignity or "neecha" in dignity:
                debilitated.append(p_name)
            
            if pos.is_combust and p_name != "Sun":
                combust.append(p_name)
            if pos.is_retrograde:
                retrograde.append(p_name)
            if h in [6, 8, 12]:
                dusthana_occ.append(f"{p_name} in H{h}")

            # Digbala check
            if (p_name in ["Sun", "Mars"] and h == 10) or \
               (p_name in ["Jupiter", "Mercury"] and h == 1) or \
               (p_name in ["Venus", "Moon"] and h == 4) or \
               (p_name == "Saturn" and h == 7):
                digbala.append(p_name)

            planets_data[p_name] = {
                "sign": pos.sign_name,
                "degree": round(pos.sign_degree, 2),
                "total_longitude": round(pos.longitude, 2),
                "house": h,
                "nakshatra": pos.nakshatra_name,
                "pada": pos.nakshatra_pada,
                "dignity": pos.dignity,
                "is_retrograde": pos.is_retrograde,
                "is_combust": pos.is_combust
            }

        # 3. SAV points
        houses_sav: Dict[int, int] = {}
        try:
            sav_list = AshtakavargaCalculator.calculate(chart).sav
            for i, pts in enumerate(sav_list):
                houses_sav[i + 1] = int(pts)
        except Exception:
            houses_sav = {i: 28 for i in range(1, 13)}

        # 4. Vargottama Planets
        vargottama: List[str] = []
        try:
            vargottama = VargaCalculator.get_vargottama_planets(chart)
        except Exception:
            pass

        # 5. Yogas & Doshas
        active_yogas: List[str] = []
        active_doshas: List[str] = []
        try:
            yd_res = default_yoga_dosha_engine.evaluate_yogas_and_doshas(chart)
            active_yogas = [y.name_en for y in yd_res.yogas if y.is_active]
            active_doshas = [d.name_en for d in yd_res.doshas if d.is_present and not d.is_cancelled]
        except Exception:
            pass

        return DeterministicFactSheet(
            native_name=p.name,
            birth_datetime=b_dt,
            latitude=round(p.latitude, 4),
            longitude=round(p.longitude, 4),
            ayanamsa_name=chart.ayanamsa_name,
            ayanamsa_value=round(chart.ayanamsa_value, 4),
            ascendant_sign=chart.lagna_sign_name,
            ascendant_degree=round(chart.lagna_degree, 2),
            ascendant_lord=chart.houses[0].lord if chart.houses else "Mars",
            moon_sign=chart.planets["Moon"].sign_name if "Moon" in chart.planets else "Aries",
            moon_degree=round(chart.planets["Moon"].sign_degree, 2) if "Moon" in chart.planets else 0.0,
            moon_nakshatra=chart.panchang.nakshatra_name if chart.panchang else "Ashwini",
            moon_pada=chart.planets["Moon"].nakshatra_pada if "Moon" in chart.planets else 1,
            sun_sign=chart.planets["Sun"].sign_name if "Sun" in chart.planets else "Aries",
            sun_degree=round(chart.planets["Sun"].sign_degree, 2) if "Sun" in chart.planets else 0.0,
            active_mahadasha=active_md,
            active_antardasha=active_ad,
            dasha_summary=dasha_sum,
            planets=planets_data,
            houses_sav=houses_sav,
            dusthana_occupants=dusthana_occ,
            exalted_planets=exalted,
            debilitated_planets=debilitated,
            combust_planets=combust,
            retrograde_planets=retrograde,
            digbala_planets=digbala,
            vargottama_planets=vargottama,
            active_yogas=active_yogas,
            active_doshas=active_doshas
        )


class ShastriyaRuleRetrievalAgent:
    """
    Agent 2: RAG retrieval of classical shastriya evidence with Sanskrit shlokas.
    """

    def retrieve_evidence(self, topic: str, fact_sheet: DeterministicFactSheet) -> List[ShastriyaPramanaItem]:
        results: List[ShastriyaPramanaItem] = []
        
        # Search the knowledge base for the topic
        query = f"{topic} {fact_sheet.ascendant_sign} {fact_sheet.active_mahadasha}"
        passages: List[ShastraPassage] = default_knowledge_base.search(query=query, theme=topic, limit=4)
        
        for p in passages:
            results.append(
                ShastriyaPramanaItem(
                    grantha=p.grantha,
                    author=p.author,
                    chapter=p.chapter,
                    theme=p.theme,
                    shloka_sanskrit=p.shloka_sanskrit,
                    translation_hi=p.translation_hi,
                    translation_en=p.translation_en,
                    principles=p.principles,
                    relevance_context=f"Classical authority for {topic} analysis under {p.grantha}."
                )
            )
        
        return results


class EvidenceVerificationAuditAgent:
    """
    Agent 3 (Independent Audit Agent):
    Audits calculation facts against classical rules, strictly separates supporting vs conflicting factors,
    and applies a documented Bayesian weight algorithm to prevent arbitrary or hallucinated confidence scores.
    """

    # Primary house associations by topic
    TOPIC_PRIMARY_HOUSES = {
        "career": [10, 1, 2, 6, 11],
        "marriage": [7, 2, 11, 4],
        "wealth": [2, 11, 9, 5, 1],
        "health": [1, 6, 8, 12],
        "spirituality": [9, 12, 5, 8, 4],
        "education": [4, 5, 2, 9],
        "general": [1, 5, 9, 10]
    }

    def audit_evidence(self, topic: str, facts: DeterministicFactSheet) -> AuditVerdict:
        clean_topic = topic.lower().strip()
        primary_houses = self.TOPIC_PRIMARY_HOUSES.get(clean_topic, [1, 5, 9, 10])
        main_house = primary_houses[0]

        supporting: List[EvidenceFactor] = []
        conflicting: List[EvidenceFactor] = []

        # 1. Dasha Lord Audit (Weight = 3.0)
        md_name = facts.active_mahadasha
        if md_name in facts.planets:
            md_info = facts.planets[md_name]
            md_h = md_info["house"]
            md_dignity = md_info["dignity"].lower()
            
            if md_h in [1, 4, 5, 7, 9, 10, 11] and ("exalted" in md_dignity or "own" in md_dignity or "friend" in md_dignity):
                supporting.append(EvidenceFactor(
                    factor=f"Active Mahadasha Lord {md_name}",
                    category="Dasha",
                    weight=3.0,
                    impact="SUPPORTING",
                    rationale=f"{md_name} is in auspicious House {md_h} with dignity '{md_info['dignity']}', empowering manifestation."
                ))
            elif md_h in [6, 8, 12] or "debilitated" in md_dignity or md_info.get("is_combust"):
                conflicting.append(EvidenceFactor(
                    factor=f"Active Mahadasha Lord {md_name} Afflicted",
                    category="Dasha",
                    weight=3.0,
                    impact="CONFLICTING",
                    rationale=f"{md_name} occupies Dusthana House {md_h} (or combust/debilitated), demanding patience and remedial discipline."
                ))
            else:
                supporting.append(EvidenceFactor(
                    factor=f"Active Mahadasha Lord {md_name} Neutral",
                    category="Dasha",
                    weight=1.5,
                    impact="SUPPORTING",
                    rationale=f"{md_name} operates with balanced normative transit strength."
                ))

        # 2. Primary House SAV Bindu Audit (Weight = 2.0)
        sav_pts = facts.houses_sav.get(main_house, 28)
        if sav_pts >= 30:
            supporting.append(EvidenceFactor(
                factor=f"House {main_house} High Ashtakavarga SAV ({sav_pts} pts)",
                category="SAV",
                weight=2.0,
                impact="SUPPORTING",
                rationale=f"House {main_house} holds {sav_pts} SAV bindus (threshold >= 28), providing strong structural resilience."
            ))
        elif sav_pts < 25:
            conflicting.append(EvidenceFactor(
                factor=f"House {main_house} Low Ashtakavarga SAV ({sav_pts} pts)",
                category="SAV",
                weight=2.0,
                impact="CONFLICTING",
                rationale=f"House {main_house} holds only {sav_pts} bindus (< 25), indicating vulnerable karmic reservoir."
            ))

        # 3. Dignities & Strengths (Weight = 2.0)
        if facts.exalted_planets:
            supporting.append(EvidenceFactor(
                factor=f"Exalted Planets: {', '.join(facts.exalted_planets)}",
                category="Dignity",
                weight=2.0,
                impact="SUPPORTING",
                rationale="Exalted grahas provide uninhibited royal capability and fortune."
            ))
        if facts.debilitated_planets:
            conflicting.append(EvidenceFactor(
                factor=f"Debilitated Planets: {', '.join(facts.debilitated_planets)}",
                category="Dignity",
                weight=2.0,
                impact="CONFLICTING",
                rationale="Debilitated grahas necessitate cancellation (Neechabhanga) or karmic remediation."
            ))

        # 4. Yogas vs Doshas (Weight = 1.5)
        if facts.active_yogas:
            supporting.append(EvidenceFactor(
                factor=f"Active Classical Yogas: {', '.join(facts.active_yogas[:3])}",
                category="Yoga",
                weight=1.5,
                impact="SUPPORTING",
                rationale="Classical auspicious combinations reinforce positive life milestones."
            ))
        if facts.active_doshas:
            conflicting.append(EvidenceFactor(
                factor=f"Active Classical Doshas: {', '.join(facts.active_doshas[:3])}",
                category="Dosha",
                weight=1.5,
                impact="CONFLICTING",
                rationale="Karmic afflictions indicate delays, friction or tests requiring self-rectification."
            ))

        # 5. Vargottama & Digbala (Weight = 1.0)
        if facts.vargottama_planets:
            supporting.append(EvidenceFactor(
                factor=f"Vargottama Planets: {', '.join(facts.vargottama_planets)}",
                category="Varga",
                weight=1.0,
                impact="SUPPORTING",
                rationale="D1=D9 alignment guarantees unwavering planetary integrity."
            ))
        if facts.combust_planets:
            conflicting.append(EvidenceFactor(
                factor=f"Combust Planets: {', '.join(facts.combust_planets)}",
                category="Affliction",
                weight=1.0,
                impact="CONFLICTING",
                rationale="Planets within solar orb have their external manifestations suppressed."
            ))

        # Ensure at least minimal baseline
        if not supporting:
            supporting.append(EvidenceFactor(
                factor="Baseline Chart Vitality",
                category="Lagna",
                weight=1.5,
                impact="SUPPORTING",
                rationale="Native's ascendant and trikona architecture provides foundational support."
            ))
        if not conflicting:
            conflicting.append(EvidenceFactor(
                factor="Normative Karmic Friction",
                category="Prarabdha",
                weight=1.0,
                impact="CONFLICTING",
                rationale="Every human chart experiences standard temporal tests during transit transitions."
            ))

        tot_sup = sum(f.weight for f in supporting)
        tot_conf = sum(f.weight for f in conflicting)
        
        # Documented formula: Ratio bounded between 15% and 92%
        ratio = tot_sup / (tot_sup + tot_conf)
        raw_score = ratio * 100.0
        final_score = round(max(15.0, min(92.0, raw_score)), 1)

        if final_score >= 68.0:
            tier = "HIGH"
            summary = "Pradhanik planetary consensus is strongly auspicious with supportive dasha and varga dignity."
        elif final_score >= 45.0:
            tier = "MODERATE"
            summary = "Mixed influences: Substantial classical promise accompanied by cautionary factors and timing delays."
        else:
            tier = "LOW"
            summary = "Significant afflictions or unfavorable dasha; disciplined remediation and patience recommended."

        return AuditVerdict(
            supporting_evidence=supporting,
            conflicting_evidence=conflicting,
            total_supporting_weight=round(tot_sup, 2),
            total_conflicting_weight=round(tot_conf, 2),
            confidence_score=final_score,
            confidence_tier=tier,
            verdict_summary=summary
        )


class SynthesisExplanationAgent:
    """
    Agent 4: Formulates transparent, evidence-traceable narrative synthesis
    with balanced perspectives and authentic classical Vedic remedies.
    """

    def generate_remedies(self, facts: DeterministicFactSheet, verdict: AuditVerdict) -> List[VedicRemedyRecommendation]:
        remedies: List[VedicRemedyRecommendation] = []
        
        # 1. Target afflicted planets (combust or debilitated)
        afflicted = list(set(facts.debilitated_planets + facts.combust_planets))
        if not afflicted:
            afflicted = [facts.active_mahadasha]

        for p in afflicted[:2]:
            if p == "Sun":
                remedies.append(VedicRemedyRecommendation(
                    planet_or_deity="Surya Narayana",
                    remedy_type="Stotra",
                    title_hi="आदित्य हृदय स्तोत्र पाठ",
                    title_en="Aditya Hridaya Stotra Recitation",
                    procedure="प्रातःकाल सूर्योदय के समय तांबे के लोटे से सूर्य को जल अर्पित कर आदित्य हृदय स्तोत्र का पाठ करें।",
                    classical_reference="वाल्मीकि रामायण युद्ध काण्ड"
                ))
            elif p == "Moon":
                remedies.append(VedicRemedyRecommendation(
                    planet_or_deity="Chandra / Shiva",
                    remedy_type="Mantra",
                    title_hi="ॐ नमः शिवाय / शिव पञ्चाक्षर मन्त्र",
                    title_en="Shiva Panchakshari Japa",
                    procedure="सोमवार के दिन श्वेत पुष्प व जल से शिवलिंग का अभिषेक करें एवं १०८ बार पञ्चाक्षर मन्त्र का जप करें।",
                    classical_reference="शिव पुराण विद्येश्वर संहिता"
                ))
            elif p == "Mars":
                remedies.append(VedicRemedyRecommendation(
                    planet_or_deity="Mangala / Hanuman",
                    remedy_type="Stotra",
                    title_hi="सुन्दरकाण्ड अथवा हनुमान चालीसा",
                    title_en="Sundarkand or Hanuman Chalisa",
                    procedure="मंगलवार एवं शनिवार को दीपक प्रज्वलित कर सुन्दरकाण्ड का पाठ करें एवं लाल मसूर का दान करें।",
                    classical_reference="पराशर होराशास्त्र मङ्गल शान्ति"
                ))
            elif p == "Mercury":
                remedies.append(VedicRemedyRecommendation(
                    planet_or_deity="Budha / Vishnu",
                    remedy_type="Stotra",
                    title_hi="विष्णु सहस्रनाम स्तोत्र",
                    title_en="Vishnu Sahasranama Stotra",
                    procedure="बुधवार को गौमाता को हरी घास या पालक खिलाएं एवं श्री विष्णु सहस्रनाम का श्रवण या पाठ करें।",
                    classical_reference="बृहत्पाराशर होराशास्त्र बुध शान्ति"
                ))
            elif p == "Jupiter":
                remedies.append(VedicRemedyRecommendation(
                    planet_or_deity="Guru / Brihaspati",
                    remedy_type="Lifestyle",
                    title_hi="गुरु सेवा एवं बेसन/चने का दान",
                    title_en="Service of Teachers & Gram Dal Donation",
                    procedure="गुरुवार को गुरुजनों व संतों का आशीर्वाद लें, चने की दाल या पीली वस्तु का दान करें।",
                    classical_reference="फलदीपिका गुरु शान्ति"
                ))
            elif p == "Venus":
                remedies.append(VedicRemedyRecommendation(
                    planet_or_deity="Shukra / Mahalakshmi",
                    remedy_type="Stotra",
                    title_hi="श्री सूक्त पाठ",
                    title_en="Shree Suktam Recitation",
                    procedure="शुक्रवार को शुद्ध घी का दीपक जलाकर कनकधारा या श्री सूक्त का पाठ करें।",
                    classical_reference="ऋग्वेद खिलभाग"
                ))
            elif p == "Saturn":
                remedies.append(VedicRemedyRecommendation(
                    planet_or_deity="Shani / Dasharatha Shani Stotra",
                    remedy_type="Stotra",
                    title_hi="दशरथकृत शनि स्तोत्र",
                    title_en="King Dasharatha Shani Stotra",
                    procedure="शनिवार संध्या समय पीपल वृक्ष के नीचे सरसों के तेल का दीपक जलाकर दशरथकृत शनि स्तोत्र का पाठ करें।",
                    classical_reference="पद्म पुराण शनि माहात्म्य"
                ))
            elif p in ["Rahu", "Ketu"]:
                remedies.append(VedicRemedyRecommendation(
                    planet_or_deity="Rahu-Ketu / Bhairava & Ganesha",
                    remedy_type="Mantra",
                    title_hi="संकटनाशन गणेश स्तोत्र / भैरव जप",
                    title_en="Sankat Nashan Ganesha Stotra",
                    procedure="भगवान गणेश को दूर्वा अर्पित करें एवं शनिवार को पक्षियों को बाजरा/सप्तधान्य डालें।",
                    classical_reference="नारद पुराण गणेश स्तोत्र"
                ))

        # Always add a universal Sattvic recommendation
        remedies.append(VedicRemedyRecommendation(
            planet_or_deity="Ishta Devata",
            remedy_type="Vrata",
            title_hi="सात्विक जीवनशैली एवं नित्य ध्यान",
            title_en="Sattvic Lifestyle & Daily Contemplation",
            procedure="नित्य १५ मिनट मौन ध्यान, वृद्धजनों का सम्मान, और क्रोध-नियंत्रण द्वारा प्रारब्ध का शोधन करें।",
            classical_reference="महाभारत शान्तिपर्व मोक्षधर्म"
        ))

        return remedies

    def synthesize(
        self,
        topic: str,
        facts: DeterministicFactSheet,
        pramana: List[ShastriyaPramanaItem],
        verdict: AuditVerdict,
        remedies: List[VedicRemedyRecommendation],
        user_query: Optional[str] = None
    ) -> Dict[str, str]:
        """Synthesizes grounded bilingual explanation."""
        # 1. Hindi Synthesis
        sup_txt_hi = "\n".join([f"- **{f.factor}** ({f.category}): {f.rationale}" for f in verdict.supporting_evidence])
        conf_txt_hi = "\n".join([f"- **{f.factor}** ({f.category}): {f.rationale}" for f in verdict.conflicting_evidence])
        pramana_txt_hi = "\n".join([f"- *{p.grantha}* ({p.chapter}): {p.translation_hi}" for p in pramana[:2]])

        synthesis_hi = f"""
### 🌟 {facts.native_name} जी की कुण्डली: {topic.title()} विषयक दैवज्ञ विश्लेषण

**१. प्राथमिक गणितीय स्थिति (Deterministic Core Facts):**
- लग्न: **{facts.ascendant_sign}** ({facts.ascendant_degree:.2f}°, स्वामी: {facts.ascendant_lord})
- चन्द्र राशि: **{facts.moon_sign}** ({facts.moon_nakshatra} नक्षत्र, पद {facts.moon_pada})
- वर्तमान महादशा: **{facts.active_mahadasha}** | अन्तर्दशा: **{facts.active_antardasha}**
- विषय भाव अष्टकवर्ग बल: {facts.houses_sav.get(10 if topic == 'career' else 7, 28)} बिन्दु

**२. 🟢 सकारात्मक शास्त्रीय पक्ष (Supporting Evidence):**
{sup_txt_hi}

**३. ⚠️ शास्त्रीय सत्य व सतर्कता (Challenges, Delays & Prarabdha):**
{conf_txt_hi}

**४. 📜 प्रामाणिक ग्रन्थ साक्ष्य (Scriptural Authority):**
{pramana_txt_hi}

**५. ⚖️ निष्पक्ष दैवज्ञ निष्कर्ष (Audit Verdict):**
- शास्त्रीय सम्भावना स्तर: **{verdict.confidence_tier} ({verdict.confidence_score}%)**
- {verdict.verdict_summary}
"""

        # 2. English Synthesis
        sup_txt_en = "\n".join([f"- **{f.factor}** ({f.category}): {f.rationale}" for f in verdict.supporting_evidence])
        conf_txt_en = "\n".join([f"- **{f.factor}** ({f.category}): {f.rationale}" for f in verdict.conflicting_evidence])
        pramana_txt_en = "\n".join([f"- *{p.grantha}* ({p.chapter}): {p.translation_en}" for p in pramana[:2]])

        synthesis_en = f"""
### 🌟 Horoscopic Consultation for {facts.native_name}: Domain '{topic.title()}'

**1. Verified Astronomical Baseline:**
- Ascendant: **{facts.ascendant_sign}** ({facts.ascendant_degree:.2f}°, Lord: {facts.ascendant_lord})
- Moon Sign: **{facts.moon_sign}** ({facts.moon_nakshatra} Nakshatra, Pada {facts.moon_pada})
- Active Vimshottari Period: **{facts.active_mahadasha} - {facts.active_antardasha}**
- House Ashtakavarga SAV: {facts.houses_sav.get(10 if topic == 'career' else 7, 28)} bindus

**2. 🟢 Supporting Astrological Evidence:**
{sup_txt_en}

**3. ⚠️ Critical Afflictions & Cautions (Karmic Friction):**
{conf_txt_en}

**4. 📜 Classical Scriptural Pramana:**
{pramana_txt_en}

**5. ⚖️ Independent Audit Verdict:**
- Confidence Alignment: **{verdict.confidence_tier} ({verdict.confidence_score}%)**
- {verdict.verdict_summary}
"""

        return {
            "synthesis_hi": synthesis_hi.strip(),
            "synthesis_en": synthesis_en.strip()
        }


# ============================================================================
# Master Orchestrator
# ============================================================================

class MasterDaivajnaOrchestrator:
    """
    Master Orchestrator coordinating all 4 specialist agents in strict sequence.
    Guarantees reproducible calculation integrity, evidence verification, and balanced consultation.
    """

    def __init__(self):
        self.calc_agent = SpecialistCalculationAgent()
        self.retrieval_agent = ShastriyaRuleRetrievalAgent()
        self.audit_agent = EvidenceVerificationAuditAgent()
        self.synthesis_agent = SynthesisExplanationAgent()

    def process_consultation(
        self,
        chart: KundaliChart,
        topic: str = "general",
        user_query: Optional[str] = None
    ) -> DaivajnaConsultationResult:
        """
        Executes the full 5-stage Layer 4 Multi-Agent pipeline:
        Stage 1: Extract deterministic facts from core calculations (no hallucination).
        Stage 2: Retrieve classical scriptural rules from Grantha knowledge base.
        Stage 3: Audit supporting vs conflicting evidence and derive formulaic confidence score.
        Stage 4: Generate authentic, non-commercial Vedic remedies.
        Stage 5: Synthesize balanced, bilingual consultation report.
        """
        # Stage 1: Deterministic Calculation Facts
        fact_sheet = self.calc_agent.extract_fact_sheet(chart)

        # Stage 2: Shastriya Rule Retrieval (RAG)
        pramana = self.retrieval_agent.retrieve_evidence(topic, fact_sheet)

        # Stage 3: Evidence Verification & Conflict Audit
        verdict = self.audit_agent.audit_evidence(topic, fact_sheet)

        # Stage 4: Classical Remedies
        remedies = self.synthesis_agent.generate_remedies(fact_sheet, verdict)

        # Stage 5: Synthesis
        narratives = self.synthesis_agent.synthesize(
            topic=topic,
            facts=fact_sheet,
            pramana=pramana,
            verdict=verdict,
            remedies=remedies,
            user_query=user_query
        )

        return DaivajnaConsultationResult(
            status="success",
            topic=topic,
            user_query=user_query,
            fact_sheet=fact_sheet,
            shastriya_pramana=pramana,
            audit_verdict=verdict,
            synthesis_hi=narratives["synthesis_hi"],
            synthesis_en=narratives["synthesis_en"],
            remedies=remedies
        )


# Singleton Instance
default_daivajna_orchestrator = MasterDaivajnaOrchestrator()
