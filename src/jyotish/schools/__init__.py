"""
JyotishOS School Architecture.
Reference: docs/IMPLEMENTATION_PRD.md (Section 4.2, P4-T8 & P4-T9).

Exports:
- BaseSchoolEngine, SchoolResult, Finding, PrecedenceRecord
- ParashariEngine, JaiminiEngine, KPEngine, LalKitabEngine, TajikaEngine
- SchoolRegistry, default_school_registry
- ShastriyaPrecedenceEngine
"""

from .base import (
    BaseSchoolEngine,
    SchoolResult,
    Finding,
    PrecedenceRecord,
    PrecedencePrinciple
)
from .conflict import ShastriyaPrecedenceEngine
from .parashari import ParashariEngine
from .jaimini import JaiminiEngine
from .kp import KPEngine
from .lalkitab import LalKitabEngine
from .tajika import TajikaEngine
from .registry import SchoolRegistry, default_school_registry

__all__ = [
    "BaseSchoolEngine",
    "SchoolResult",
    "Finding",
    "PrecedenceRecord",
    "PrecedencePrinciple",
    "ShastriyaPrecedenceEngine",
    "ParashariEngine",
    "JaiminiEngine",
    "KPEngine",
    "LalKitabEngine",
    "TajikaEngine",
    "SchoolRegistry",
    "default_school_registry"
]

