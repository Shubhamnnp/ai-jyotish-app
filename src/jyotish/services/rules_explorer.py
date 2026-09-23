"""
Classical Grantha Rules Explorer & Shastriya Search Engine for JyotishOS.
Indexes and provides high-speed search across 24,000+ rules from:
- Brihat Parashara Hora Shastra (BPHS)
- Brihat Jataka (Varahamihira)
- Saravali (Kalyana Varma)
- Phaladeepika (Mantreswara)
- Jaimini Upadesha Sutras
- Lal Kitab (1952)
- KP System & Nadi Astrology

Allows live keyword search, grantha/theme filtering, and 1-click active chart testing.
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional, Tuple

try:
    from ..core.models import KundaliChart
    from ..rules.evaluator import UniversalConditionEvaluator
except (ImportError, ValueError):
    from src.jyotish.core.models import KundaliChart
    from src.jyotish.rules.evaluator import UniversalConditionEvaluator

logger = logging.getLogger(__name__)

GRANTHA_FILES = {
    "Brihat Parashara Hora Shastra (BPHS)": "bphs_rules.json",
    "Brihat Jataka (वराहमिहिर)": "brihat_jataka_rules.json",
    "Saravali (कल्याण वर्मा)": "saravali_rules.json",
    "Phaladeepika (मंत्रेश्वर)": "phaladeepika_rules.json",
    "Jaimini Sutras (महर्षि जैमिनी)": "jaimini_rules.json",
    "Lal Kitab 1952 (लाल किताब)": "lalkitab_rules.json",
    "KP System (कृष्णमूर्ति पद्धति)": "kp_rules.json",
    "Nadi Astrology (सप्तर्षि व नाड़ी)": "nadi_rules.json",
    "Prashna Marga (प्रश्न मार्ग)": "prashna_rules.json",
    "Tajika Nilakanthi (वार्षिक ताजिक)": "tajika_rules.json",
    "Brihat Samhita (मेदिनी व संहिता)": "samhita_rules.json",
    "Muhurtha Chintamani (मुहूर्त शास्त्र)": "muhurtha_rules.json",
    "Sarvatobhadra Chakra (सर्वतोभद्र चक्र वेध)": "sarvatobhadra_rules.json",
    "Classical Misc Granthas (विविध योग व संहिता)": "classic_misc_rules.json",
    "Vedic Numerology (अंक ज्योतिष शास्त्र)": "numerology_rules.json",
}

RULES_DIR = os.path.join(os.path.dirname(__file__), "..", "rules", "grantha_rules")


class RulesExplorerService:
    """Provides high-speed indexing, search, and active-chart matching for classical astrological rules."""

    def __init__(self, rules_dir: str = RULES_DIR):
        self.rules_dir = os.path.abspath(rules_dir)
        self._cache: Dict[str, List[Dict[str, Any]]] = {}
        self._total_count = 0
        self._is_indexed = False

    def _ensure_indexed(self) -> None:
        """Lazily indexes rule files on first access."""
        if self._is_indexed:
            return

        total = 0
        for grantha_label, filename in GRANTHA_FILES.items():
            path = os.path.join(self.rules_dir, filename)
            if os.path.exists(path):
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        rules = data.get("rules", []) if isinstance(data, dict) else (data if isinstance(data, list) else [])
                        # Attach grantha label to each rule
                        for r in rules:
                            r["_grantha"] = grantha_label
                        self._cache[grantha_label] = rules
                        total += len(rules)
                except Exception as e:
                    logger.error(f"Error loading rules from {filename}: {e}")
                    self._cache[grantha_label] = []
            else:
                self._cache[grantha_label] = []

        self._total_count = total
        self._is_indexed = True

    def get_stats(self) -> Dict[str, Any]:
        """Returns statistics on indexed rules and granthas."""
        self._ensure_indexed()
        breakdown = {g: len(rules) for g, rules in self._cache.items()}
        return {
            "total_rules": self._total_count,
            "granthas_count": len(self._cache),
            "breakdown": breakdown
        }

    def search_rules(
        self,
        query: str = "",
        grantha_filter: Optional[str] = None,
        max_results: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Searches rules by keyword across rule_id, rule_name_hi, rule_name_en, and description_hi.
        """
        self._ensure_indexed()
        q = query.lower().strip()
        results = []

        target_granthas = [grantha_filter] if (grantha_filter and grantha_filter in self._cache) else list(self._cache.keys())

        for g in target_granthas:
            for r in self._cache.get(g, []):
                # Match check
                if q:
                    name_hi = str(r.get("rule_name_hi", "")).lower()
                    name_en = str(r.get("rule_name_en", "")).lower()
                    r_id = str(r.get("rule_id", "")).lower()
                    eff = r.get("effect", {})
                    desc_hi = str(eff.get("description_hi", "")).lower()
                    themes = " ".join(str(t).lower() for t in eff.get("themes", []))

                    if q not in name_hi and q not in name_en and q not in r_id and q not in desc_hi and q not in themes:
                        continue

                results.append(r)
                if len(results) >= max_results:
                    return results

        return results

    def test_rule_on_chart(self, rule: Dict[str, Any], chart: KundaliChart) -> Tuple[bool, str]:
        """
        Evaluates whether a rule's condition is met by the given chart using UniversalConditionEvaluator.
        """
        try:
            cond = rule.get("condition", {})
            if not cond:
                return True, "सार्वभौमिक नियम (बिना शर्त लागू)"

            fired, explanations, delta = UniversalConditionEvaluator.evaluate(cond, chart)
            if fired:
                exp_text = "; ".join(explanations) if explanations else "सभी शास्त्रीय शर्तें पूर्ण"
                return True, f"✅ सक्रिय — {exp_text}"
            else:
                return False, "❌ निष्क्रिय (शर्त घटित नहीं हुई)"
        except Exception as e:
            return False, f"परीक्षण त्रुटि: {e}"


# Singleton instance
default_rules_explorer_service = RulesExplorerService()
