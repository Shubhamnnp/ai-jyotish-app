"""
Pydantic Data Models for JyotishOS.
Structured representations for astronomical positions, charts, dashas, rules, and query results.
"""

from datetime import datetime, date, time
from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field


class BirthData(BaseModel):
    """Input birth data for a profile."""
    name: str = "Jataka"
    birth_date: date  # YYYY-MM-DD
    birth_time: time  # HH:MM:SS
    latitude: float
    longitude: float
    timezone: str = Field(default="Asia/Kolkata", description="Standard IANA timezone string, e.g. 'Asia/Kolkata'")
    timezone_offset: Optional[float] = Field(default=5.5, description="UTC offset in hours (+5.5 for IST). Deprecated in favor of timezone.")
    city: Optional[str] = "New Delhi"
    confidence: str = Field(default="Exact", description="Exact / Approx / Unknown")
    birth_time_confidence: str = Field(default="exact", description="exact, approximate_plus_minus_minutes, unknown")
    confidence_minutes: Optional[int] = Field(default=None, description="Tolerance in minutes if confidence is approximate")
    fold: Optional[int] = Field(default=None, description="0 (first/DST) or 1 (second/standard) for ambiguous DST transition times")
    gender: str = Field(default="male", description="male / female")
    house_system: str = Field(default="Whole Sign", description="Whole Sign, Equal, Sripati, Porphyry, Placidus")


class PlanetPosition(BaseModel):
    """Calculated position and astrological state of a graha."""
    name: str
    longitude: float = Field(..., description="Sidereal longitude 0-360 degrees")
    latitude: float = 0.0
    speed: float = 0.0
    is_retrograde: bool = False
    is_combust: bool = False
    sign_id: int = Field(..., ge=1, le=12)
    sign_name: str
    sign_degree: float = Field(..., description="Degrees within sign (0-30)")
    nakshatra_id: int = Field(..., ge=1, le=27)
    nakshatra_name: str
    nakshatra_pada: int = Field(..., ge=1, le=4)
    nakshatra_lord: str
    house_from_lagna: int = Field(1, ge=1, le=12)
    house_from_moon: int = Field(1, ge=1, le=12)
    dignity: str = Field(
        default="neutral",
        description="exalted, moolatrikona, own, great_friend, friend, neutral, enemy, great_enemy, debilitated"
    )


class HouseCusp(BaseModel):
    """Cusp information for a bhava."""
    house_number: int = Field(..., ge=1, le=12)
    sign_id: int = Field(..., ge=1, le=12)
    sign_name: str
    cusp_longitude: float
    lord: str
    occupants: List[str] = []
    aspecting_planets: List[str] = []
    sandhi_start: Optional[float] = None
    sandhi_end: Optional[float] = None
    bhava_madhya: Optional[float] = None


class PanchangData(BaseModel):
    """Classical Panchang elements at time of event/birth."""
    tithi_name: str
    tithi_number: int
    tithi_type: str  # Shukla / Krishna
    vara_name: str
    nakshatra_name: str
    yoga_name: str
    karana_name: str


class VargaPlanetPosition(BaseModel):
    name: str
    sign_id: int
    sign_name: str
    degree_in_varga: float
    house_number: int
    deity: Optional[str] = None
    is_benefic_deity: Optional[bool] = None


class VargaChart(BaseModel):
    """Divisional Chart (D1 to D60)."""
    varga_code: str  # D1, D9, D10 etc.
    varga_name: str
    division: int
    lagna_sign_id: int
    lagna_sign_name: str
    planets: Dict[str, VargaPlanetPosition]
    lagna_deity: Optional[str] = None
    lagna_is_benefic_deity: Optional[bool] = None


class ShodhanaResult(BaseModel):
    """Trikona and Ekadhipatya Shodhana with Shodhita Pinda."""
    trikona_reduced_bav: Dict[str, List[int]]
    ekadhipatya_reduced_bav: Dict[str, List[int]]
    rashi_pinda: Dict[str, int]
    graha_pinda: Dict[str, int]
    yoga_pinda: Dict[str, int]


class AshtakavargaResult(BaseModel):
    """Bhinna (BAV) and Sarva (SAV) Ashtakavarga charts with Shodhana."""
    bav: Dict[str, List[int]] = Field(
        ...,
        description="7 planets x 12 signs bindu matrix (1-based sign indexing in list: indices 0..11 for Aries..Pisces)"
    )
    sav: List[int] = Field(
        ...,
        description="12 signs Sarva bindu counts, summing to exactly 337"
    )
    total_bindus: int = 337
    shodhana: Optional[ShodhanaResult] = None


class ShadbalaPlanetResult(BaseModel):
    sthana_bala: float
    dik_bala: float
    kaala_bala: float
    cheshta_bala: float
    naisargika_bala: float
    drik_bala: float
    total_virupas: float
    total_rupas: float
    required_virupas: float
    strength_ratio: float
    is_strong: bool
    ishta_phala: float = 0.0
    kashta_phala: float = 0.0
    baladi_avastha: str = "Yuva"
    jagratadi_avastha: str = "Jagrat"
    deeptadi_avastha: str = "Deepta"
    uchha_bala: float = 0.0
    kendradi_bala: float = 0.0
    ojayugma_bala: float = 0.0
    nathonnatha_bala: float = 0.0
    paksha_bala: float = 0.0


class ShadbalaSummary(BaseModel):
    planets: Dict[str, ShadbalaPlanetResult]
    bhava_bala: Dict[int, float]
    bhava_bala_components: Optional[Dict[int, Dict[str, float]]] = None


class JaiminiResult(BaseModel):
    karakas_7: Dict[str, str]
    karakas_8: Dict[str, str]
    karakamsha_sign_id: int
    karakamsha_sign_name: str
    arudha_padas: Dict[str, int]
    arudha_pada_names: Dict[str, str]
    hora_lagna_sign_name: str
    ghati_lagna_sign_name: str
    sri_lagna_sign_name: str
    indu_lagna_sign_name: str
    bhava_lagna_sign_name: Optional[str] = "Aries"
    pranapada_lagna_sign_name: Optional[str] = "Aries"
    varnada_lagna_sign_name: Optional[str] = "Aries"
    special_lagnas_detail: Optional[Dict[str, Dict[str, Any]]] = None
    arudha_details: Optional[Dict[str, Dict[str, Any]]] = None


class UpagrahaResult(BaseModel):
    gulika_sign_name: str
    gulika_longitude: float
    mandi_sign_name: str
    mandi_longitude: float
    dhuma_longitude: float
    vyatipata_longitude: float
    parivesha_longitude: float
    indrachapa_longitude: float
    upaketu_longitude: float


class CalculationMetadata(BaseModel):
    """Deterministic reproducibility metadata for astronomical chart computation."""
    engine: str = "swisseph"  # "swisseph" | "degraded_pyephem"
    engine_type: str = "Swiss Ephemeris / PyEphem Calibrated"
    engine_version: str = "2.1.0"
    ayanamsa_name: str = "Lahiri"
    ayanamsa_value: float
    ayanamsa: Optional[Dict[str, Any]] = None  # {"name": ..., "value_degrees": ...}
    house_system: str = "Whole Sign"
    node_type: str = "mean"
    coordinate_type: str = "geocentric"
    topocentric_moon: bool = False
    polar_latitude_adjusted: bool = False
    calculation_timestamp_utc: Optional[datetime] = None
    utc_datetime: Optional[datetime] = None
    timezone_iana: str = "Asia/Kolkata"
    delta_t_seconds: float = 0.0
    jd_ut: float = 0.0
    engine_degraded: bool = False
    ephemeris_mode: str = "Swiss (Moshier)"


class KundaliChart(BaseModel):
    """Complete computed Vedic Chart."""
    birth_data: BirthData
    ayanamsa_name: str = "Lahiri"
    ayanamsa_value: float
    lagna_longitude: float
    lagna_sign_id: int
    lagna_sign_name: str
    lagna_degree: float
    planets: Dict[str, PlanetPosition]
    houses: List[HouseCusp]
    panchang: PanchangData
    vargas: Dict[str, VargaChart] = {}
    ashtakavarga: Optional[AshtakavargaResult] = None
    atmakaraka: Optional[str] = None
    shadbala: Optional[ShadbalaSummary] = None
    jaimini: Optional[JaiminiResult] = None
    upagrahas: Optional[UpagrahaResult] = None
    metadata: Optional[CalculationMetadata] = None
    engine_degraded: bool = False


class DashaLevel(BaseModel):
    lord: str
    start_date: datetime
    end_date: datetime


class ActiveDashaHierarchy(BaseModel):
    """Active Vimshottari dasha periods at any given target date."""
    target_date: date
    mahadasha: DashaLevel
    antardasha: DashaLevel
    pratyantardasha: DashaLevel
    sookshmadasha: Optional[DashaLevel] = None
    formatted_summary: str


class RuleEvidence(BaseModel):
    """Detailed evidence of a rule evaluation."""
    rule_id: str
    rule_name_hi: str
    rule_name_en: str
    school: str
    category: str
    source_text: str
    source_chapter: str
    fired: bool
    signal_score: float = Field(0.0, description="Normalized score 0.0 to 1.0")
    base_strength: float
    polarity: str = "+"
    themes: List[str] = []
    explanation_hi: str = ""
    modifiers_applied: List[Dict[str, Any]] = []
    exclusions_matched: List[str] = []
    varga_confirmed: bool = False
    varga_notes: str = ""


class GhatnaQueryInput(BaseModel):
    """Input payload for Ghatna Query (Event Window Analysis)."""
    birth_data: BirthData
    target_date: date
    target_end_date: Optional[date] = None
    theme: str = Field(default="all", description="all, career, marriage, wealth, health, travel, spirituality")
    free_text_query: Optional[str] = None


class TransitSummary(BaseModel):
    """Key transit triggers at event window."""
    saturn_house_from_moon: int
    saturn_house_from_lagna: int
    jupiter_house_from_moon: int
    jupiter_house_from_lagna: int
    is_sade_sati: bool
    sade_sati_phase: Optional[str] = None
    is_dhaiya: bool
    dhaiya_type: Optional[str] = None
    is_jupiter_saturn_double_transit_on_10th: bool = False
    is_guru_chandal_transit: bool = False
    saturn_retrograde: bool = False
    jupiter_retrograde: bool = False
    saturn_paya: Optional[str] = None
    jupiter_paya: Optional[str] = None
    transit_paya_detail: Dict[str, Any] = {}
    ashtakavarga_transit_bindus: Dict[str, int] = {}
    vedha_analysis: Optional[Dict[str, Any]] = None


class GhatnaQueryResult(BaseModel):
    """Comprehensive output for Ghatna Query."""
    target_date: date
    target_end_date: Optional[date] = None
    theme: str
    composite_score: float = Field(..., ge=0.0, le=1.0)
    confidence_band: str  # "Uchha (High)", "Madhyam (Medium)", "Sanketik (Tentative)"
    consensus_ratio: str  # e.g., "5/6 Rules in agreement"
    active_dasha: ActiveDashaHierarchy
    transit_summary: TransitSummary
    top_positive_signals: List[RuleEvidence] = []
    top_negative_signals: List[RuleEvidence] = []
    all_evaluated_rules: List[RuleEvidence] = []
    narrative_hi: str
    narrative_en: str
    disclaimer: str


class ClassicalYogaItem(BaseModel):
    yoga_id: str
    name_hi: str
    name_en: str
    category: str
    is_active: bool
    strength_score: float = 75.0
    planets_involved: List[str] = []
    houses_involved: List[int] = []
    description_hi: str
    description_en: str
    shloka_reference: str = ""


class ClassicalDoshaItem(BaseModel):
    dosha_id: str
    name_hi: str
    name_en: str
    category: str
    is_present: bool
    severity: str = "None"  # None, Mild, Moderate, Severe
    is_cancelled: bool = False
    cancellation_reasons: List[str] = []
    planets_involved: List[str] = []
    houses_involved: List[int] = []
    description_hi: str
    description_en: str
    remedy_summary: str = ""
    shloka_reference: str = ""


class YogaDoshaAnalysisResult(BaseModel):
    yogas: List[ClassicalYogaItem] = []
    active_yogas_count: int = 0
    doshas: List[ClassicalDoshaItem] = []
    active_doshas_count: int = 0
    is_manglik: bool = False
    manglik_severity: str = "None"
    manglik_cancelled: bool = False
    kaal_sarp_type: Optional[str] = None
    kaal_sarp_active: bool = False
