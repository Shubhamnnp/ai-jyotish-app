"""
Canonical Jyotish Event Taxonomy & Significator Mapping (Phase 5, Task P5-T1).
Reference: docs/upgrade/MASTER_10_PHASE_ROADMAP.md (Phase 5).

Maps each life event to its classical astrological parameters:
- Primary and secondary bhavas (houses)
- Primary and secondary karakas (planetary significators)
- Associated divisional chart (Varga: D9, D10, D7, D4, D30, etc.)
- Auspicious vs malefic orientation
- Classical triggers and conditions
"""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class EventDefinition(BaseModel):
    """Canonical definition of a verifiable life event in Vedic Astrology."""
    event_id: str
    name_en: str
    name_hi: str
    domain: str  # career, marriage, progeny, property, health, travel, spirituality
    primary_houses: List[int]
    secondary_houses: List[int] = Field(default_factory=list)
    primary_karakas: List[str]
    secondary_karakas: List[str] = Field(default_factory=list)
    varga: str = "D1"  # Associated varga (D9, D10, D7, D4, D30, etc.)
    is_favorable: bool = True
    classical_description_en: str
    classical_description_hi: str


CANONICAL_EVENTS: Dict[str, EventDefinition] = {
    "career_recognition": EventDefinition(
        event_id="career_recognition",
        name_en="Career Breakthrough & Public Recognition",
        name_hi="कार्यक्षेत्र में अप्रत्याशित सफलता एवं यश",
        domain="career",
        primary_houses=[10, 11],
        secondary_houses=[1, 2, 9],
        primary_karakas=["Sun", "Saturn", "Jupiter"],
        secondary_karakas=["Mercury"],
        varga="D10",
        is_favorable=True,
        classical_description_en="Activation of 10th and 11th bhavas with Sun/Jupiter prominence conferring high authority, public honor, and career apex.",
        classical_description_hi="दशम एवं एकादश भावों की सक्रियता तथा सूर्य/गुरु के प्रभाव से प्रतिष्ठा, उच्च पद एवं सामाजिक कीर्ति की प्राप्ति।"
    ),
    "job_start": EventDefinition(
        event_id="job_start",
        name_en="New Job or Career Commencement",
        name_hi="नवीन नौकरी या कार्य आरम्भ",
        domain="career",
        primary_houses=[10, 6],
        secondary_houses=[2, 11, 1],
        primary_karakas=["Saturn", "Mercury"],
        secondary_karakas=["Sun"],
        varga="D10",
        is_favorable=True,
        classical_description_en="Activation of 6th (service) and 10th (profession) bhavas through dasha or transit.",
        classical_description_hi="षष्ठ (सेवा) एवं दशम (कर्म) भावों की दशा-गोचर द्वारा सक्रियता से रोजगार की प्राप्ति।"
    ),
    "promotion": EventDefinition(
        event_id="promotion",
        name_en="Job Promotion & Increment",
        name_hi="पद-पदोन्नति एवं वेतन वृद्धि",
        domain="career",
        primary_houses=[10, 11],
        secondary_houses=[2, 6],
        primary_karakas=["Sun", "Mars", "Jupiter"],
        secondary_karakas=["Saturn"],
        varga="D10",
        is_favorable=True,
        classical_description_en="Kendra-Labha resonance triggering elevated status and professional growth.",
        classical_description_hi="दशम व एकादश भावों के योग से पदोन्नति एवं आर्थिक उत्थान।"
    ),
    "marriage": EventDefinition(
        event_id="marriage",
        name_en="Marriage & Sacred Union",
        name_hi="विवाह संस्कार एवं दांपत्य जीवन आरम्भ",
        domain="marriage",
        primary_houses=[7],
        secondary_houses=[2, 11],
        primary_karakas=["Venus", "Jupiter"],
        secondary_karakas=["Moon"],
        varga="D9",
        is_favorable=True,
        classical_description_en="7th bhava fruition with 2nd (kutumba) and 11th (desire fulfillment) supported by Venus/Jupiter.",
        classical_description_hi="सप्तम (विवाह), द्वितीय (कुटुम्ब) एवं एकादश भावों की शुक्र/गुरु के प्रभाव से सक्रियता।"
    ),
    "childbirth": EventDefinition(
        event_id="childbirth",
        name_en="Childbirth & Progeny Blessing",
        name_hi="संतानोत्पत्ति एवं कुल वृद्धि",
        domain="progeny",
        primary_houses=[5],
        secondary_houses=[2, 11, 9],
        primary_karakas=["Jupiter"],
        secondary_karakas=["Sun", "Mars"],
        varga="D7",
        is_favorable=True,
        classical_description_en="5th bhava (putra) fruition supported by natural putra-karaka Jupiter and D7 Saptamsha.",
        classical_description_hi="पंचम (संतान) भाव तथा संतानकारक गुरु की अनुकूल दशा-गोचर द्वारा संतान सुख।"
    ),
    "property_purchase": EventDefinition(
        event_id="property_purchase",
        name_en="Real Estate & Property Acquisition",
        name_hi="भूमि, भवन एवं अचल संपत्ति क्रय",
        domain="property",
        primary_houses=[4],
        secondary_houses=[2, 11],
        primary_karakas=["Mars", "Venus"],
        secondary_karakas=["Saturn", "Moon"],
        varga="D4",
        is_favorable=True,
        classical_description_en="4th bhava (sukha/griha) activated by bhumi-karaka Mars and vahan/griha karaka Venus.",
        classical_description_hi="चतुर्थ (गृह/भूमि) भाव तथा भूमिकारक मंगल एवं शुक्र की सक्रियता से संपत्ति लाभ।"
    ),
    "foreign_travel": EventDefinition(
        event_id="foreign_travel",
        name_en="Foreign Travel & Relocation",
        name_hi="विदेश गमन एवं दूरस्थ प्रवास",
        domain="travel",
        primary_houses=[9, 12],
        secondary_houses=[3, 7],
        primary_karakas=["Moon", "Rahu", "Jupiter"],
        secondary_karakas=["Saturn"],
        varga="D9",
        is_favorable=True,
        classical_description_en="9th (long journeys) and 12th (foreign lands) bhavas triggered by moving planets Moon and Rahu.",
        classical_description_hi="नवम (दीर्घ यात्रा) एवं द्वादश (विदेश) भावों की चंद्र व राहु द्वारा सक्रियता।"
    ),
    "litigation": EventDefinition(
        event_id="litigation",
        name_en="Legal Dispute & Litigation",
        name_hi="विवाद, न्यायालयीन प्रकरण एवं शत्रु बाधा",
        domain="legal",
        primary_houses=[6],
        secondary_houses=[8, 12],
        primary_karakas=["Mars", "Saturn", "Rahu"],
        secondary_karakas=["Sun"],
        varga="D1",
        is_favorable=False,
        classical_description_en="6th bhava (ripu/shatru) affliction by malefics triggering court cases or adversarial conflict.",
        classical_description_hi="षष्ठ (शत्रु/विवाद) भाव की क्रूर ग्रहों द्वारा उत्तेजना से कानूनी वाद-विवाद।"
    ),
    "disease_onset": EventDefinition(
        event_id="disease_onset",
        name_en="Health Vulnerability & Disease Onset",
        name_hi="रोग व्याधि एवं स्वास्थ्य कष्ट",
        domain="health",
        primary_houses=[6, 8],
        secondary_houses=[12, 1],
        primary_karakas=["Saturn", "Rahu", "Mars"],
        secondary_karakas=["Sun"],
        varga="D30",
        is_favorable=False,
        classical_description_en="Rogashana 6th and Ashtama 8th bhavas afflicted without benefic protection causing physical distress.",
        classical_description_hi="षष्ठ व अष्टम भावों पर पाप प्रभाव एवं लग्नेश की निर्बलता से शारीरिक कष्ट।"
    )
}


class EventTaxonomyRegistry:
    """Registry providing lookup and validation for astrological event types."""

    @classmethod
    def get_event(cls, event_id: str) -> Optional[EventDefinition]:
        return CANONICAL_EVENTS.get(event_id.strip().lower())

    @classmethod
    def list_all_events(cls) -> List[EventDefinition]:
        return list(CANONICAL_EVENTS.values())

    @classmethod
    def get_events_for_domain(cls, domain: str) -> List[EventDefinition]:
        dom = domain.strip().lower()
        return [ev for ev in CANONICAL_EVENTS.values() if ev.domain == dom]


default_event_taxonomy = EventTaxonomyRegistry()
