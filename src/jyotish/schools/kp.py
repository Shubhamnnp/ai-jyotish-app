"""
Krishnamurti Padhdhati (KP System) School Engine.
Reference: docs/IMPLEMENTATION_PRD.md (Section 4.2, P4-T8).

Governs KP principles:
- Sources: KP Readers I to VI (Prof. K.S. Krishnamurti)
- Core factors: Placidus Cusps, 249 Sub-Lords, 4-Fold Significations (A, B, C, D),
  Cuspal Sub-Lord promises for life domains.
- Strictly isolated from Parashari or Lal Kitab house concepts.
"""

from typing import Dict, List, Any
from ..core.models import KundaliChart
from ..core.kp import default_kp_engine, KP_QUERY_RULES
from .base import BaseSchoolEngine, SchoolResult, Finding


class KPEngine(BaseSchoolEngine):
    """Krishnamurti Padhdhati (KP System) engine."""

    @property
    def school_key(self) -> str:
        return "kp"

    @property
    def school_name(self) -> str:
        return "Krishnamurti Padhdhati (के.पी. ज्योतिष पद्धति)"

    @property
    def canonical_texts(self) -> List[str]:
        return [
            "KP Readers I-VI (Prof. K.S. Krishnamurti)",
            "Krishman's Astrological Tables"
        ]

    def evaluate(self, chart: KundaliChart, domain: str = "career", **kwargs) -> SchoolResult:
        """Evaluates chart using pure KP cuspal sub-lord and signification principles."""
        supported_findings: List[Finding] = []
        cautionary_findings: List[Finding] = []

        kp_data = default_kp_engine.calculate_chart_kp(chart)
        cusps_list = kp_data.get("cusps_kp", [])
        cusps_map = {c["cusp_num"]: c for c in cusps_list}
        significators = kp_data.get("significators", {}).get("planets", {})

        # Mapping domain to KP query rule
        domain_key_map = {
            "career": "JOB_CAREER",
            "job": "JOB_CAREER",
            "marriage": "MARRIAGE",
            "wealth": "FINANCIAL_PROSPERITY",
            "property": "PROPERTY_VEHICLE",
            "education": "HIGHER_EDUCATION",
            "foreign": "FOREIGN_TRAVEL",
            "health": "LITIGATION_LEGAL"
        }
        kp_query_key = domain_key_map.get(domain.lower(), "JOB_CAREER")
        query_rule = KP_QUERY_RULES.get(kp_query_key, KP_QUERY_RULES["JOB_CAREER"])

        primary_cusps = query_rule.get("primary_cusps", [10])
        fav_houses = set(query_rule.get("favorable_houses", []))
        unfav_houses = set(query_rule.get("unfavorable_houses", []))

        for c_num in primary_cusps:
            c_info = cusps_map.get(c_num)
            if not c_info:
                continue

            sub_lord = c_info.get("sub_lord", "")
            star_lord = c_info.get("star_lord", "")

            # Check houses signified by the sub-lord
            sub_sig = significators.get(sub_lord, {})
            all_sig_houses = set(sub_sig.get("all_signified_houses", []))

            fav_matches = all_sig_houses.intersection(fav_houses)
            unfav_matches = all_sig_houses.intersection(unfav_houses)

            if len(fav_matches) >= len(unfav_matches):
                supported_findings.append(Finding(
                    finding_id=f"KP-CUSP-{c_num}-SUBLORD-{sub_lord.upper()}",
                    rule_ids=[f"KP-READER-IV-CUSP-{c_num}"],
                    title_en=f"Cusp {c_num} Sub-Lord {sub_lord} Promises Fulfillment",
                    title_hi=f"भाव {c_num} का उप-स्वामी {sub_lord} अनुकूल फलदायक",
                    claim_en=(
                        f"House {c_num} Sub-Lord {sub_lord} (Star: {star_lord}) signifies favorable houses "
                        f"{sorted(list(fav_matches))}, indicating positive fruition."
                    ),
                    claim_hi=(
                        f"भाव {c_num} के उप-स्वामी {sub_lord} (नक्षत्र स्वामी: {star_lord}) द्वारा अनुकूल भाव "
                        f"{sorted(list(fav_matches))} सक्रिय हो रहे हैं।"
                    ),
                    domain=domain,
                    polarity="+",
                    strength_score=1.15,
                    strength_reason=[f"Signifies houses {sorted(list(fav_matches))}"]
                ))
            else:
                cautionary_findings.append(Finding(
                    finding_id=f"KP-CUSP-{c_num}-SUBLORD-{sub_lord.upper()}",
                    rule_ids=[f"KP-READER-IV-CUSP-{c_num}"],
                    title_en=f"Cusp {c_num} Sub-Lord {sub_lord} Signals Obstacles",
                    title_hi=f"भाव {c_num} का उप-स्वामी {sub_lord} विलंब/अड़चन सूचक",
                    claim_en=(
                        f"House {c_num} Sub-Lord {sub_lord} signifies unfavorable houses "
                        f"{sorted(list(unfav_matches))}, indicating delays or impediments."
                    ),
                    claim_hi=(
                        f"भाव {c_num} के उप-स्वामी {sub_lord} द्वारा प्रतिकूल भाव "
                        f"{sorted(list(unfav_matches))} सक्रिय हो रहे हैं।"
                    ),
                    domain=domain,
                    polarity="-",
                    strength_score=0.85
                ))

        # General 1st Cusp Sub-Lord overview
        c1 = cusps_map.get(1)
        if c1:
            supported_findings.append(Finding(
                finding_id=f"KP-ASC-SUBLORD-{c1.get('sub_lord', '').upper()}",
                rule_ids=["KP-READER-III-ASC"],
                title_en=f"Ascendant Sub-Lord: {c1.get('sub_lord', '')}",
                title_hi=f"लग्न उप-स्वामी: {c1.get('sub_lord', '')}",
                claim_en=f"Lagna Cusp is governed by Sub-Lord {c1.get('sub_lord', '')} in star of {c1.get('star_lord', '')}.",
                claim_hi=f"लग्न भाव का उप-स्वामी {c1.get('sub_lord', '')} है जो {c1.get('star_lord', '')} के नक्षत्र में स्थित है।",
                domain="personality",
                polarity="+"
            ))

        c_prim = cusps_map.get(primary_cusps[0]) if primary_cusps else None
        summary_en = (
            f"KP assessment for {domain}: Cusp {primary_cusps[0]} sub-lord is "
            f"{c_prim.get('sub_lord') if c_prim else 'N/A'}. "
            f"Found {len(supported_findings)} favorable significations, {len(cautionary_findings)} challenges."
        )
        summary_hi = (
            f"के.पी. पद्धति {domain} विश्लेषण: मुख्य भाव {primary_cusps[0]} का उप-स्वामी "
            f"{c_prim.get('sub_lord') if c_prim else 'N/A'} है। "
            f"{len(supported_findings)} अनुकूल एवं {len(cautionary_findings)} प्रतिकूल सूचक प्राप्त हुए।"
        )

        return SchoolResult(
            school_key=self.school_key,
            school_name=self.school_name,
            canonical_texts=self.canonical_texts,
            domain=domain,
            supported_findings=supported_findings,
            cautionary_findings=cautionary_findings,
            active_cancellations=[],
            conflicts_resolved=[],
            summary_en=summary_en,
            summary_hi=summary_hi,
            system_metrics={
                "cusp_1_sublord": c1.get("sub_lord") if c1 else None,
                "primary_cusp": primary_cusps[0] if primary_cusps else None,
                "evaluated_query": kp_query_key
            }
        )
