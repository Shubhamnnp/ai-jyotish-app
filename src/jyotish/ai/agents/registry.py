"""
Canonical 14 Specialist AI Agent Registry (Phase 7, Task P7-T1).
Reference: docs/upgrade/MASTER_10_PHASE_ROADMAP.md (Phase 7).

Defines the roles, capabilities, and system boundaries for all 14 specialist AI agents
in the Daivajna Brain architecture.
"""

from typing import Dict, List, Optional
from enum import Enum
from pydantic import BaseModel, Field


class AgentDomain(str, Enum):
    ORCHESTRATION = "orchestration"
    CLASSICAL_PARASHARI = "classical_parashari"
    JAIMINI = "jaimini"
    KP = "kp"
    PRASHNA = "prashna"
    TIMING_DASHA = "timing_dasha"
    TIMING_TRANSIT = "timing_transit"
    DIVISIONAL_VARGAS = "divisional_vargas"
    YOGAS = "yogas"
    DOSHAS = "doshas"
    RECTIFICATION_BTR = "rectification_btr"
    EVENT_PREDICTION = "event_prediction"
    SHASTRA_RESEARCH = "shastra_research"
    INDEPENDENT_AUDIT = "independent_audit"


class SpecialistAgentDefinition(BaseModel):
    """Specification of an autonomous astrological specialist agent."""
    agent_id: str
    name_en: str
    name_hi: str
    domain: AgentDomain
    description_en: str
    description_hi: str
    authorized_sources: List[str]
    can_emit_verdicts: bool = True
    must_audit: bool = True


CANONICAL_14_AGENTS: Dict[str, SpecialistAgentDefinition] = {
    "master_jyotish_agent": SpecialistAgentDefinition(
        agent_id="master_jyotish_agent",
        name_en="Master Jyotish Orchestrator Agent",
        name_hi="प्रधान दैवज्ञ समन्वयकर्ता एजेंट",
        domain=AgentDomain.ORCHESTRATION,
        description_en="Synthesizes findings across all 13 specialist agents and formats final client report.",
        description_hi="समस्त विशेषज्ञ एजेंटों के साक्ष्यों का शास्त्रीय समन्वय एवं अंतिम फलादेश निर्माण।",
        authorized_sources=["All Verified Grantha Evidence Packs"],
        can_emit_verdicts=True,
        must_audit=True
    ),
    "parashari_agent": SpecialistAgentDefinition(
        agent_id="parashari_agent",
        name_en="Parashari Classical Agent",
        name_hi="पाराशरी शास्त्रीय सिद्धांत एजेंट",
        domain=AgentDomain.CLASSICAL_PARASHARI,
        description_en="Evaluates Kendra, Trikona, Dusthana, Bhava-Bhavesha-Karaka, and planetary dignities.",
        description_hi="केंद्र-त्रिकोण, भाव-भावेश-कारक एवं ग्रह गरिमा का पाराशरी शास्त्रीय फलादेश।",
        authorized_sources=["Brihat Parashara Hora Shastra", "Phaladeepika", "Saravali"],
        can_emit_verdicts=True,
        must_audit=True
    ),
    "jaimini_agent": SpecialistAgentDefinition(
        agent_id="jaimini_agent",
        name_en="Jaimini Sutra Agent",
        name_hi="जैमिनी सूत्र मीमांसक एजेंट",
        domain=AgentDomain.JAIMINI,
        description_en="Evaluates 7/8 Chara Karakas, Karakamsha Lagna, Arudha Padas A1-A12, and Chara Dasha.",
        description_hi="चर कारक, कारकांश लग्न, आरूढ़ पद एवं चर दशा का स्वतंत्र विश्लेषण।",
        authorized_sources=["Jaimini Upadesha Sutras"],
        can_emit_verdicts=True,
        must_audit=True
    ),
    "kp_agent": SpecialistAgentDefinition(
        agent_id="kp_agent",
        name_en="Krishnamurti Paddhati (KP) Agent",
        name_hi="कृष्णमूर्ति पद्धति (के.पी.) एजेंट",
        domain=AgentDomain.KP,
        description_en="Evaluates Placidus Cusps, 249 Sub-Lords, 4-fold significations (A, B, C, D), and Ruling Planets.",
        description_hi="कस्पल सब-लॉर्ड, ४-स्तरीय कारकत्व एवं तात्कालिक रूलिंग प्लैनेट्स का विश्लेषण।",
        authorized_sources=["KP Readers I-VI (Prof. K.S. Krishnamurti)"],
        can_emit_verdicts=True,
        must_audit=True
    ),
    "prashna_agent": SpecialistAgentDefinition(
        agent_id="prashna_agent",
        name_en="Prashna Horary Agent",
        name_hi="प्रश्न शास्त्र एवं दैवज्ञ शुद्धि एजेंट",
        domain=AgentDomain.PRASHNA,
        description_en="Evaluates Horary query moment, Tajika aspects/yogas (Ithasala/Ishrafa), and Daivajna Authenticity.",
        description_hi="प्रश्न कुण्डली, इत्थशाल/ईशराफ योग एवं प्रश्न मार्ग अनुसार दैवज्ञ शुद्धि का मापन।",
        authorized_sources=["Prashna Marga", "Tajika Neelakanthi", "Daivajna Vallabha"],
        can_emit_verdicts=True,
        must_audit=True
    ),
    "dasha_agent": SpecialistAgentDefinition(
        agent_id="dasha_agent",
        name_en="Dasha Timeline Agent",
        name_hi="दशा कालचक्र विशेषज्ञ एजेंट",
        domain=AgentDomain.TIMING_DASHA,
        description_en="Calculates and analyzes Vimshottari 120-year and Yogini 36-year dasha periods.",
        description_hi="विंशोत्तरी एवं योगिनी दशा चक्रों का सूक्ष्म काल-निर्धारण।",
        authorized_sources=["BPHS Adhyayas 46-52", "Jataka Parijata"],
        can_emit_verdicts=True,
        must_audit=True
    ),
    "transit_agent": SpecialistAgentDefinition(
        agent_id="transit_agent",
        name_en="Gochar (Transit) Agent",
        name_hi="गोचर एवं अष्टकवर्ग वेध एजेंट",
        domain=AgentDomain.TIMING_TRANSIT,
        description_en="Evaluates current planetary transits, classical Double Transit, Sade Sati, and Vedha.",
        description_hi="ग्रह गोचर, गुरु-शनि द्वि-गोचर प्रभाव, साढ़ेसाती एवं गोचर वेध का फलादेश।",
        authorized_sources=["Phaladeepika Chapter 26", "BPHS Ashtakavarga Adhyaya"],
        can_emit_verdicts=True,
        must_audit=True
    ),
    "varga_agent": SpecialistAgentDefinition(
        agent_id="varga_agent",
        name_en="Shodashvarga Divisional Agent",
        name_hi="षोडशवर्ग एवं वैशेषिकांश एजेंट",
        domain=AgentDomain.DIVISIONAL_VARGAS,
        description_en="Analyzes D1 through D60 divisional charts, Vargottama dignities, and Vaisheshikamsa counts.",
        description_hi="D1 से D60 षोडशवर्ग, वर्गोत्तम स्थिति एवं १६-स्तरीय वैशेषिकांश फल।",
        authorized_sources=["BPHS Shodashvarga Adhyaya 6"],
        can_emit_verdicts=True,
        must_audit=True
    ),
    "yoga_agent": SpecialistAgentDefinition(
        agent_id="yoga_agent",
        name_en="Classical Yoga Agent",
        name_hi="शास्त्रीय योग एवं राजयोग एजेंट",
        domain=AgentDomain.YOGAS,
        description_en="Detects Raja yogas, Dhana yogas, Pancha Mahapurusha yogas, and Gajakesari yogas.",
        description_hi="पंच महापुरुष, गजकेसरी, बुधादित्य एवं केंद्र-त्रिकोण राजयोगों की पहचान।",
        authorized_sources=["BPHS Adhyayas 35-42", "Saravali", "Phaladeepika"],
        can_emit_verdicts=True,
        must_audit=True
    ),
    "dosha_agent": SpecialistAgentDefinition(
        agent_id="dosha_agent",
        name_en="Dosha & Bhanga Cancellation Agent",
        name_hi="दोष एवं शास्त्रीय परिहार (भंग) एजेंट",
        domain=AgentDomain.DOSHAS,
        description_en="Analyzes Manglik, Kemadruma, Kalasarpa doshas, along with rigorous cancellation rules.",
        description_hi="मांगलिक, केमद्रुम, कालसर्प दोष एवं उनके शास्त्र-सम्मत परिहार नियमों का परीक्षण।",
        authorized_sources=["BPHS Adhyaya 37", "Phaladeepika Ch 6"],
        can_emit_verdicts=True,
        must_audit=True
    ),
    "btr_agent": SpecialistAgentDefinition(
        agent_id="btr_agent",
        name_en="Birth Time Rectification (BTR) Agent",
        name_hi="जन्म समय शुद्धिकरण (BTR) एजेंट",
        domain=AgentDomain.RECTIFICATION_BTR,
        description_en="Performs Kunda Shodhana, Tattwa Shodhana, and multi-event divisional boundary fit analysis.",
        description_hi="कुण्ड व तत्व शोधन तथा जीवन की घटनाओं द्वारा जन्म समय का सूक्ष्म शुद्धिकरण।",
        authorized_sources=["BPHS Shodhana Sutras", "Jataka Parijata BTR"],
        can_emit_verdicts=True,
        must_audit=True
    ),
    "event_prediction_agent": SpecialistAgentDefinition(
        agent_id="event_prediction_agent",
        name_en="5-Layer Event Prediction Agent",
        name_hi="पंच-स्तरीय घटना काल-निर्धारण एजेंट",
        domain=AgentDomain.EVENT_PREDICTION,
        description_en="Evaluates life event probability across Natal, Varga, Dasha, Transit, and Yoga layers.",
        description_hi="जन्म कुण्डली, सम्बद्ध वर्ग, दशा चक्र, गोचर एवं योगों के समन्वय से घटना निर्धारण।",
        authorized_sources=["Canonical 5-Layer Fruition Pipeline"],
        can_emit_verdicts=True,
        must_audit=True
    ),
    "shastra_research_agent": SpecialistAgentDefinition(
        agent_id="shastra_research_agent",
        name_en="Shastra Research & Sanskrit Retrieval Agent",
        name_hi="शास्त्र अनुसंधान एवं संस्कृत श्लोक एजेंट",
        domain=AgentDomain.SHASTRA_RESEARCH,
        description_en="Retrieves verified Sanskrit shlokas, chapter numbers, and classical grantha citations.",
        description_hi="प्रामाणिक संस्कृत श्लोक, अध्याय संख्या एवं ग्रंथ संदर्भों का सटीक उद्धरण।",
        authorized_sources=["15 Classical Granthas Verified Corpus"],
        can_emit_verdicts=False,
        must_audit=True
    ),
    "independent_auditor_agent": SpecialistAgentDefinition(
        agent_id="independent_auditor_agent",
        name_en="Independent Auditor & Anti-Hallucination Agent",
        name_hi="स्वतंत्र ऑडिटर एवं मतिभ्रम (Anti-Hallucination) रक्षक एजेंट",
        domain=AgentDomain.INDEPENDENT_AUDIT,
        description_en="Audits all AI-generated assertions against grounded Evidence Packs, blocking hallucinated claims.",
        description_hi="AI द्वारा उत्पन्न प्रत्येक वाक्य का साक्ष्य पैक से मिलान कर मतिभ्रम को पूर्णतः रोकना।",
        authorized_sources=["Deterministic Evidence Pack Validator"],
        can_emit_verdicts=True,
        must_audit=False
    ),
}


class AgentRegistry:
    """Registry providing lookup and validation for the 14 specialist agents."""

    @classmethod
    def get_agent(cls, agent_id: str) -> Optional[SpecialistAgentDefinition]:
        return CANONICAL_14_AGENTS.get(agent_id.strip().lower())

    @classmethod
    def list_all_agents(cls) -> List[SpecialistAgentDefinition]:
        return list(CANONICAL_14_AGENTS.values())

    @classmethod
    def get_agent_by_domain(cls, domain: AgentDomain) -> Optional[SpecialistAgentDefinition]:
        for agent in CANONICAL_14_AGENTS.values():
            if agent.domain == domain:
                return agent
        return None


default_agent_registry = AgentRegistry()

