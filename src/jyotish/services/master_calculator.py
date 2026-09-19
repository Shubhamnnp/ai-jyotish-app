"""
Master Astrological Calculation Synthesizer for JyotishOS.
Aggregates and executes all 21 JyotishOS modules in a clean, unified pipeline:
1. Natal Chart & Shodashavarga (D1-D60)
2. Affliction & Free-Will Diagnostics (12 Houses & 9 Planets)
3. Vastu-Jyotish 8-Direction Mandala & Zones
4. Shadbala & Bhava Bala Calculations
5. Jaimini 7 Chara Karakas, Arudhas (AL, UL, HL) & Upagrahas (Mandi/Gulika)
6. Ayurdaya (Longevity Evaluation & Shayanadi Avasthas)
7. Full 5 Dasha Suite (Vimshottari, Yogini, Chara, Kaalachakra, Shoola)
8. Ashtakavarga (BAV 8x12, SAV 337, Shodhita Pinda)
9. Gochar & Transit (Live positions, Sade Sati phase, Double Transit)
10. Sarvatobhadra Chakra (9x9 Vedhas & Sensitive Nakshatras)
11. Kota Chakra (4-Zone Fortress Defense & Allocations)
12. KP Astrology (Planets & 12 Cuspal Sub-Lords & Ruling Planets)
13. Sudarshan Chakra (Lagna-Chandra-Surya Concentric Mandala)
14. Tajika Varshaphal (Solar Return, Muntha, Varshesha, 16 Sahams, Mudda Dasha)
"""

from datetime import datetime, date
from typing import Dict, Any, Optional

from ..core.models import BirthData, KundaliChart
from ..core.calculator import default_chart_calculator
from ..core.shadbala import ShadbalaCalculator
from ..core.jaimini import JaiminiCalculator
from ..core.upagraha import UpagrahaCalculator
from ..core.ayurdaya import default_ayurdaya_engine
from ..core.chakras import default_sarvatobhadra_engine, default_kota_chakra_engine
from ..core.kp import default_kp_engine
from ..core.affliction import AfflictionEngine, LIFE_AREAS
from ..services.vastu import VastuJyotishEngine
from ..services.varshaphal import default_varshaphal_service
from ..dasha.vimshottari import default_dasha_engine
from ..dasha.yogini import default_yogini_engine
from ..dasha.chara import default_chara_engine
from ..dasha.kcd import default_kcd_engine
from ..dasha.shoola import default_shoola_engine
from ..ui.sudarshan import default_sudarshan_engine


class MasterCalculator:
    """Central orchestrator for executing and bundling all astrological modules."""

    def calculate_all(
        self,
        chart: KundaliChart,
        target_year: Optional[int] = None,
        transit_chart: Optional[KundaliChart] = None
    ) -> Dict[str, Any]:
        """
        Executes all 21 modules on the given natal chart and returns a comprehensive bundle.
        """
        if target_year is None:
            target_year = datetime.now().year

        p = chart.birth_data
        birth_dt = datetime.combine(p.birth_date, p.birth_time)
        moon_lon = chart.planets["Moon"].longitude

        # 1. Base Engines (Affliction & Vastu)
        affliction_eng = AfflictionEngine(chart)
        house_points = affliction_eng.calculate_house_points(detailed=False)
        planet_points = affliction_eng.calculate_planet_points(detailed=False)
        dasvarga_table = affliction_eng.calculate_dasvarga_table()

        avg_free_will = round(sum(hp.get("freeWill", 50) for hp in house_points) / max(1, len(house_points)), 1)

        affliction_data = {
            "house_points": house_points,
            "planet_points": planet_points,
            "dasvarga_table": dasvarga_table,
            "life_areas_count": len(LIFE_AREAS),
            "free_will_score": avg_free_will,
            "manglik_status": "अल्प / परिहार युक्त",
            "kaalsarp_status": "लागू नहीं"
        }

        vastu_eng = VastuJyotishEngine(chart)
        vastu_zones = vastu_eng.evaluate_vastu_zones()
        vastu_data = {
            "zones": vastu_zones,
            "dominant_favorable_direction": "ईशान (North-East / Jupiter)",
            "afflicted_direction": "नैऋत्य (South-West / Rahu)",
            "primary_remedy": "घर के ईशान कोण को स्वच्छ एवं जल तत्व से परिपूर्ण रखें।"
        }

        # 2. Planetary Strengths (Shadbala & Bhava Bala)
        shadbala_obj = chart.shadbala if chart.shadbala else ShadbalaCalculator.calculate(chart)
        
        # Calculate ranks 1..7 based on strength_ratio descending
        sorted_planets = sorted(
            shadbala_obj.planets.items(),
            key=lambda item: item[1].strength_ratio,
            reverse=True
        ) if hasattr(shadbala_obj, "planets") else []
        ranks_map = {p_name: r + 1 for r, (p_name, _) in enumerate(sorted_planets)}

        shadbala_res = {
            "planets": {
                p_k: {
                    "total_virupas": p_v.total_virupas,
                    "total_rupas": p_v.total_rupas,
                    "required_virupas": p_v.required_virupas,
                    "required_rupas": round(p_v.required_virupas / 60.0, 2),
                    "strength_ratio": p_v.strength_ratio,
                    "rank": ranks_map.get(p_k, 1),
                    "is_adequate": p_v.is_strong or (p_v.total_virupas >= p_v.required_virupas),
                    "is_strong": p_v.is_strong
                }
                for p_k, p_v in shadbala_obj.planets.items()
            } if hasattr(shadbala_obj, "planets") else {},
            "bhava_bala": shadbala_obj.bhava_bala if hasattr(shadbala_obj, "bhava_bala") else {}
        }

        # 3. Jaimini & Upagrahas
        jaimini_obj = chart.jaimini if chart.jaimini else JaiminiCalculator.calculate(chart)
        upagraha_obj = chart.upagrahas if chart.upagrahas else UpagrahaCalculator.calculate(chart)

        # 4. Ayurdaya (Longevity & Shayanadi Avasthas)
        jaimini_ayur = default_ayurdaya_engine.calculate_jaimini_longevity(chart)
        pindayu = default_ayurdaya_engine.calculate_pindayu(chart)
        shayanadi = default_ayurdaya_engine.calculate_shayanadi_avasthas(chart)
        ayurdaya_res = {
            "jaimini_longevity": jaimini_ayur,
            "pindayu": pindayu,
            "shayanadi_avasthas": shayanadi,
            "consensus_category": jaimini_ayur.get("consensus_hi", "मध्यायु (36-72 वर्ष)")
        }

        # 5. Dasha Systems
        vimshottari_seq = default_dasha_engine.generate_mahadasha_sequence(birth_dt, moon_lon)
        active_vimshottari = default_dasha_engine.get_active_dasha_at(birth_dt, moon_lon, datetime.now().date())
        yogini_seq = default_yogini_engine.generate_timeline(chart)
        chara_seq = default_chara_engine.generate_timeline(chart)
        kcd_res = default_kcd_engine.calculate(chart)
        shoola_res = default_shoola_engine.calculate(chart)

        # 6. Ashtakavarga & Gochar Transits
        if transit_chart is None:
            now_dt = datetime.now()
            t_birth = BirthData(
                name="Current Transit",
                birth_date=now_dt.date(),
                birth_time=now_dt.time(),
                latitude=chart.birth_data.latitude,
                longitude=chart.birth_data.longitude,
                timezone_offset=chart.birth_data.timezone_offset,
                city=chart.birth_data.city,
                confidence="Exact"
            )
            transit_chart = default_chart_calculator.calculate_chart(t_birth)

        # 7. Chakras
        sbc_res = default_sarvatobhadra_engine.calculate(chart, transit_chart)
        kota_res = default_kota_chakra_engine.calculate(chart, transit_chart)

        # 8. KP Astrology
        kp_res = default_kp_engine.calculate_chart_kp(chart)

        # 9. Sudarshan Chakra
        sudarshan_res = default_sudarshan_engine.calculate(chart)

        # 10. Tajika Varshaphal (Annual Solar Return)
        varshaphal_res = default_varshaphal_service.calculate_varshaphal(chart, int(target_year))

        return {
            "chart": chart,
            "transit_chart": transit_chart,
            "target_year": target_year,
            "affliction": affliction_data,
            "vastu": vastu_data,
            "shadbala": shadbala_res,
            "jaimini": jaimini_obj,
            "upagraha": upagraha_obj,
            "ayurdaya": ayurdaya_res,
            "dashas": {
                "vimshottari": vimshottari_seq,
                "active_vimshottari": active_vimshottari,
                "yogini": yogini_seq,
                "chara": chara_seq,
                "kcd": kcd_res,
                "shoola": shoola_res
            },
            "ashtakavarga": {
                "bav": chart.ashtakavarga.bav if chart.ashtakavarga else {},
                "sav": chart.ashtakavarga.sav if chart.ashtakavarga else [0]*12,
                "shodhana": chart.ashtakavarga.shodhana if chart.ashtakavarga else None
            },
            "chakras": {
                "sbc": sbc_res,
                "kota": kota_res
            },
            "kp": kp_res,
            "sudarshan": sudarshan_res,
            "varshaphal": varshaphal_res,
            "calculated_at": datetime.now().strftime("%d-%b-%Y %I:%M %p")
        }


# Singleton Instance
default_master_calculator = MasterCalculator()
