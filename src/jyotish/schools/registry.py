"""
Astrological School Registry & Side-by-Side Evaluator.
Reference: docs/IMPLEMENTATION_PRD.md (Section 4.2, P4-T8).

Provides isolated access to individual astrological schools:
- Parashari
- Jaimini
- Krishnamurti Padhdhati (KP)
- Lal Kitab
- Tajika

Strict Rule:
Schools are evaluated in isolated sandboxes. Combined views present results side-by-side
without synthetic cross-school probability averaging or confidence blurs.
"""

from typing import Dict, List, Optional, Any
from ..core.models import KundaliChart
from .base import BaseSchoolEngine, SchoolResult
from .parashari import ParashariEngine
from .jaimini import JaiminiEngine
from .kp import KPEngine
from .lalkitab import LalKitabEngine
from .tajika import TajikaEngine


class SchoolRegistry:
    """Registry managing isolated classical astrological engines."""

    def __init__(self):
        self._engines: Dict[str, BaseSchoolEngine] = {
            "parashari": ParashariEngine(),
            "jaimini": JaiminiEngine(),
            "kp": KPEngine(),
            "lal_kitab": LalKitabEngine(),
            "tajika": TajikaEngine()
        }

    def get_engine(self, school_key: str) -> BaseSchoolEngine:
        """Retrieves engine for given school key."""
        key = school_key.strip().lower()
        if key not in self._engines:
            raise KeyError(
                f"Unknown astrological school '{school_key}'. "
                f"Available schools: {list(self._engines.keys())}"
            )
        return self._engines[key]

    def list_schools(self) -> List[str]:
        """Returns list of registered school keys."""
        return list(self._engines.keys())

    def evaluate_isolated(
        self,
        school_key: str,
        chart: KundaliChart,
        domain: str = "general",
        **kwargs
    ) -> SchoolResult:
        """Evaluates chart using a single isolated school engine."""
        engine = self.get_engine(school_key)
        return engine.evaluate(chart, domain=domain, **kwargs)

    def evaluate_all_side_by_side(
        self,
        chart: KundaliChart,
        domain: str = "general",
        **kwargs
    ) -> Dict[str, SchoolResult]:
        """
        Evaluates all schools independently.
        Returns side-by-side dictionary of SchoolResult objects.
        NO cross-school score averaging or weighting is applied.
        """
        results: Dict[str, SchoolResult] = {}
        for key, engine in self._engines.items():
            results[key] = engine.evaluate(chart, domain=domain, **kwargs)
        return results


default_school_registry = SchoolRegistry()

