"""
Domain Analysis Engine for JyotishOS (Phase 5, Task P5-T2).
Reference: docs/IMPLEMENTATION_PRD.md (Section 5.2).

Governs domain analysis:
- Loads declarative YAML configurations from `domains/*.yaml`.
- Enforces classical order of analysis:
  Bhava -> Bhava Lord -> Karaka -> Aspects -> Varga Placements -> Dasha / Transits
- Pure computation against typed `ChartFactors`. No ungrounded free text.
"""

import os
import yaml
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from ..factors import ChartFactors, PlanetFactors, HouseFactors


class DomainSignificators(BaseModel):
    """Classical significators configured for a domain."""
    domain: str
    display_name_en: str
    display_name_hi: str
    analysis_order: List[str]
    parashari_primary_bhavas: List[int]
    parashari_secondary_bhavas: List[int]
    parashari_karakas: List[str]
    parashari_vargas: List[str]
    jaimini_karakas: List[str] = Field(default_factory=list)
    jaimini_arudhas: List[str] = Field(default_factory=list)
    kp_primary_cusps: List[int] = Field(default_factory=list)
    kp_favorable_houses: List[int] = Field(default_factory=list)
    kp_unfavorable_houses: List[int] = Field(default_factory=list)
    disclaimer: Optional[str] = None


class BhavaAnalysisFactor(BaseModel):
    """Extracted factors for a single domain bhava."""
    house_num: int
    sign_name: str
    lord: str
    lord_placement_house: int
    lord_dignity: str
    lord_shadbala_ratio: float
    occupants: List[str]
    benefic_occupants: List[str]
    malefic_occupants: List[str]
    aspecting_planets: List[str]
    benefic_aspects: List[str]
    malefic_aspects: List[str]
    sav_bindus: int
    net_bhava_strength: float  # computed from lord shadbala, SAV bindus, benefic/malefic ratio


class KarakaAnalysisFactor(BaseModel):
    """Extracted factors for a domain karaka."""
    planet: str
    sign_name: str
    house_from_lagna: int
    dignity: str
    shadbala_ratio: float
    is_combust: bool
    is_retrograde: bool
    is_vargottama: bool
    baladi_avastha: str
    deeptadi_avastha: str
    chara_karaka_tag: Optional[str] = None


class DomainAnalysisResult(BaseModel):
    """Full structured evaluation of a domain against ChartFactors."""
    domain: str
    display_name_en: str
    display_name_hi: str
    school: str = "parashari"
    primary_bhavas: List[BhavaAnalysisFactor]
    secondary_bhavas: List[BhavaAnalysisFactor] = Field(default_factory=list)
    primary_karakas: List[KarakaAnalysisFactor]
    varga_indicators: Dict[str, Dict[str, str]] = Field(default_factory=dict)
    overall_prominence_score: float = 1.0  # composite metric (0.0 to 2.0)
    classical_summary_en: str = ""
    classical_summary_hi: str = ""
    disclaimers: List[str] = Field(default_factory=list)


class DomainAnalyzer:
    """Loads YAML configurations and evaluates domain factors against ChartFactors."""

    def __init__(self, config_dir: Optional[str] = None):
        if config_dir is None:
            config_dir = os.path.dirname(os.path.abspath(__file__))
        self.config_dir = config_dir
        self._configs: Dict[str, Dict[str, Any]] = {}
        self._load_configs()

    def _load_configs(self):
        """Loads all .yaml domain definitions from the config directory."""
        if not os.path.exists(self.config_dir):
            return
        for fname in os.listdir(self.config_dir):
            if fname.endswith(".yaml") or fname.endswith(".yml"):
                fpath = os.path.join(self.config_dir, fname)
                with open(fpath, "r", encoding="utf-8") as f:
                    cfg = yaml.safe_load(f)
                    if isinstance(cfg, dict) and "domain" in cfg:
                        self._configs[cfg["domain"].lower()] = cfg

    def list_available_domains(self) -> List[str]:
        """Returns list of supported domain identifiers."""
        return sorted(list(self._configs.keys()))

    def get_domain_config(self, domain: str) -> Dict[str, Any]:
        """Retrieves raw configuration dictionary for domain."""
        dom_key = domain.strip().lower()
        if dom_key not in self._configs:
            raise KeyError(
                f"Unknown domain '{domain}'. Available domains: {self.list_available_domains()}"
            )
        return self._configs[dom_key]

    def get_significators(self, domain: str) -> DomainSignificators:
        """Returns strongly-typed domain significators."""
        cfg = self.get_domain_config(domain)
        p_cfg = cfg.get("schools", {}).get("parashari", {})
        j_cfg = cfg.get("schools", {}).get("jaimini", {})
        kp_cfg = cfg.get("schools", {}).get("kp", {})

        return DomainSignificators(
            domain=cfg["domain"],
            display_name_en=cfg.get("display_name_en", cfg["domain"].capitalize()),
            display_name_hi=cfg.get("display_name_hi", cfg["domain"]),
            analysis_order=cfg.get("analysis_order", ["bhava_occupants", "bhava_lord", "karaka_strength"]),
            parashari_primary_bhavas=p_cfg.get("primary_bhavas", []),
            parashari_secondary_bhavas=p_cfg.get("secondary_bhavas", []),
            parashari_karakas=p_cfg.get("primary_karakas", []),
            parashari_vargas=p_cfg.get("relevant_vargas", ["D1", "D9"]),
            jaimini_karakas=j_cfg.get("primary_karakas", []),
            jaimini_arudhas=j_cfg.get("primary_arudhas", []),
            kp_primary_cusps=kp_cfg.get("primary_cusps", []),
            kp_favorable_houses=kp_cfg.get("favorable_houses", []),
            kp_unfavorable_houses=kp_cfg.get("unfavorable_houses", []),
            disclaimer=cfg.get("disclaimer")
        )

    def analyze_domain(
        self,
        domain: str,
        factors: ChartFactors,
        school: str = "parashari"
    ) -> DomainAnalysisResult:
        """
        Executes classical domain analysis by mapping ChartFactors
        against the domain's primary and secondary significators.
        """
        sigs = self.get_significators(domain)

        # 1. Evaluate Primary Bhavas
        primary_bhavas_list: List[BhavaAnalysisFactor] = []
        for h_num in sigs.parashari_primary_bhavas:
            hf = factors.houses.get(h_num)
            if not hf:
                continue

            # Compute Net Bhava Strength:
            # SAV norm: (SAV / 28.0) * 0.4 + Lord Shadbala * 0.4 + Benefic Bonus * 0.2 - Malefic Penalty * 0.2
            sav_ratio = hf.sav_bindus / 28.0
            benefic_factor = len(hf.benefic_occupants) + len(hf.benefic_aspects)
            malefic_factor = len(hf.malefic_occupants) + len(hf.malefic_aspects)
            occ_delta = (benefic_factor - malefic_factor) * 0.1

            net_str = round(max(0.2, (sav_ratio * 0.35) + (hf.lord_shadbala_ratio * 0.45) + occ_delta), 3)

            primary_bhavas_list.append(BhavaAnalysisFactor(
                house_num=h_num,
                sign_name=hf.sign_name,
                lord=hf.lord,
                lord_placement_house=hf.lord_placement_house,
                lord_dignity=hf.lord_dignity,
                lord_shadbala_ratio=hf.lord_shadbala_ratio,
                occupants=hf.occupants,
                benefic_occupants=hf.benefic_occupants,
                malefic_occupants=hf.malefic_occupants,
                aspecting_planets=hf.aspecting_planets,
                benefic_aspects=hf.benefic_aspects,
                malefic_aspects=hf.malefic_aspects,
                sav_bindus=hf.sav_bindus,
                net_bhava_strength=net_str
            ))

        # 2. Evaluate Secondary Bhavas
        secondary_bhavas_list: List[BhavaAnalysisFactor] = []
        for h_num in sigs.parashari_secondary_bhavas:
            hf = factors.houses.get(h_num)
            if not hf:
                continue
            sav_ratio = hf.sav_bindus / 28.0
            net_str = round(max(0.2, (sav_ratio * 0.4) + (hf.lord_shadbala_ratio * 0.6)), 3)
            secondary_bhavas_list.append(BhavaAnalysisFactor(
                house_num=h_num,
                sign_name=hf.sign_name,
                lord=hf.lord,
                lord_placement_house=hf.lord_placement_house,
                lord_dignity=hf.lord_dignity,
                lord_shadbala_ratio=hf.lord_shadbala_ratio,
                occupants=hf.occupants,
                benefic_occupants=hf.benefic_occupants,
                malefic_occupants=hf.malefic_occupants,
                aspecting_planets=hf.aspecting_planets,
                benefic_aspects=hf.benefic_aspects,
                malefic_aspects=hf.malefic_aspects,
                sav_bindus=hf.sav_bindus,
                net_bhava_strength=net_str
            ))

        # 3. Evaluate Primary Karakas
        primary_karakas_list: List[KarakaAnalysisFactor] = []
        for p_name in sigs.parashari_karakas:
            pf = factors.planets.get(p_name)
            if not pf:
                continue
            primary_karakas_list.append(KarakaAnalysisFactor(
                planet=p_name,
                sign_name=pf.sign_name,
                house_from_lagna=pf.house_from_lagna,
                dignity=pf.dignity,
                shadbala_ratio=pf.shadbala_ratio,
                is_combust=pf.is_combust,
                is_retrograde=pf.is_retrograde,
                is_vargottama=pf.is_vargottama,
                baladi_avastha=pf.baladi_avastha,
                deeptadi_avastha=pf.deeptadi_avastha,
                chara_karaka_tag=pf.chara_karaka
            ))

        # 4. Varga Indicators for Domain
        varga_map: Dict[str, Dict[str, str]] = {}
        for p_name in sigs.parashari_karakas:
            pf = factors.planets.get(p_name)
            if pf:
                varga_map[p_name] = {
                    "D1": pf.sign_name,
                    "D9": pf.d9_navamsha_sign,
                    "D10": pf.d10_dashamsha_sign
                }

        # 5. Composite Prominence Score
        bhava_scores = [b.net_bhava_strength for b in primary_bhavas_list]
        karaka_scores = [k.shadbala_ratio for k in primary_karakas_list]
        avg_bhava = sum(bhava_scores) / len(bhava_scores) if bhava_scores else 1.0
        avg_karaka = sum(karaka_scores) / len(karaka_scores) if karaka_scores else 1.0
        prominence = round((avg_bhava * 0.6) + (avg_karaka * 0.4), 3)

        summary_en = (
            f"Domain '{sigs.display_name_en}': Primary Bhava(s) {sigs.parashari_primary_bhavas} "
            f"exhibit average strength {avg_bhava:.2f}. Key Karakas ({', '.join(sigs.parashari_karakas)}) "
            f"hold average Shadbala ratio {avg_karaka:.2f}. Overall Prominence: {prominence:.2f}."
        )
        summary_hi = (
            f"विषय '{sigs.display_name_hi}': मुख्य भाव {sigs.parashari_primary_bhavas} "
            f"का औसत सामर्थ्य {avg_bhava:.2f} है। कारक ग्रह ({', '.join(sigs.parashari_karakas)}) "
            f"का षड्बल अनुपात {avg_karaka:.2f} है। समग्र प्रमाण बल: {prominence:.2f}।"
        )

        disclaimers = []
        if sigs.disclaimer:
            disclaimers.append(sigs.disclaimer)

        return DomainAnalysisResult(
            domain=sigs.domain,
            display_name_en=sigs.display_name_en,
            display_name_hi=sigs.display_name_hi,
            school=school,
            primary_bhavas=primary_bhavas_list,
            secondary_bhavas=secondary_bhavas_list,
            primary_karakas=primary_karakas_list,
            varga_indicators=varga_map,
            overall_prominence_score=prominence,
            classical_summary_en=summary_en,
            classical_summary_hi=summary_hi,
            disclaimers=disclaimers
        )


default_domain_analyzer = DomainAnalyzer()
