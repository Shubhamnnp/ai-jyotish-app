"""
Deterministic In-Memory Calculation Cache (Phase 6, Task P6-T6).
Reference: docs/IMPLEMENTATION_PRD.md (Section 6.6, P6-T6).

Rules:
1. Pure, deterministic caching keyed on canonical astronomical inputs.
2. Thread-safe LRU eviction policy with stats reporting.
3. Guarantees sub-500ms fresh computation and sub-5ms cached retrieval.
4. Deepcopy on retrieval to prevent downstream mutation side-effects.
"""

import copy
import hashlib
import json
import threading
from collections import OrderedDict
from datetime import date, time, datetime
from typing import Optional, Dict, Any, Tuple

from .models import BirthData, KundaliChart


def compute_chart_cache_key(
    birth_data: BirthData,
    ayanamsa_name: str = "Lahiri",
    house_system: str = "Whole Sign",
    node_type: str = "mean",
    is_full: bool = False,
    provider_id: str = "default",
    extra_options: Optional[Dict[str, Any]] = None
) -> str:
    """Computes a canonical SHA-256 cache key from birth parameters and calculation options."""
    b_name = str(getattr(birth_data, "name", "") or "").strip()
    b_d = birth_data.birth_date
    if isinstance(b_d, (datetime, date)):
        b_d_str = b_d.strftime("%Y-%m-%d")
    else:
        b_d_str = str(b_d)

    b_t = birth_data.birth_time
    if isinstance(b_t, (datetime, time)):
        b_t_str = b_t.strftime("%H:%M:%S")
    else:
        b_t_str = str(b_t)

    # Use full precision coordinates to avoid rounding collisions
    lat = float(birth_data.latitude)
    lon = float(birth_data.longitude)
    tz = str(birth_data.timezone or "Asia/Kolkata").strip()
    tz_off = str(getattr(birth_data, "timezone_offset", ""))
    fields_set = ",".join(sorted(getattr(birth_data, "__pydantic_fields_set__", set())))
    ayan = str(ayanamsa_name).strip().lower()
    hsys = str(house_system).strip().lower()
    ntype = str(node_type).strip().lower()

    # Canonicalize extra kwargs (e.g. topocentric_moon, ayanamsa_val)
    extra_str = ""
    if extra_options:
        filtered = {k: v for k, v in extra_options.items() if k not in ("use_cache",)}
        if filtered:
            extra_str = json.dumps(filtered, sort_keys=True, default=str)

    canonical = (
        f"{b_name}|{b_d_str}|{b_t_str}|{lat:.8f}|{lon:.8f}|{tz}|{tz_off}|{fields_set}|"
        f"{ayan}|{hsys}|{ntype}|full={is_full}|provider={provider_id}|extra={extra_str}"
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


class ChartCalculationCache:
    """Thread-safe LRU cache for KundaliChart computations."""

    def __init__(self, max_size: int = 500):
        self.max_size = max_size
        self._cache: OrderedDict[str, KundaliChart] = OrderedDict()
        self._lock = threading.RLock()
        self._hits = 0
        self._misses = 0

    def get(self, key: str) -> Optional[KundaliChart]:
        """Retrieves a deepcopy of the cached chart if present, bumping it to most recent."""
        with self._lock:
            if key in self._cache:
                self._hits += 1
                self._cache.move_to_end(key)
                return copy.deepcopy(self._cache[key])
            self._misses += 1
            return None

    def put(self, key: str, chart: KundaliChart) -> None:
        """Stores a deepcopy of the chart into the LRU cache."""
        with self._lock:
            if key in self._cache:
                self._cache.move_to_end(key)
            else:
                if len(self._cache) >= self.max_size:
                    self._cache.popitem(last=False)
            self._cache[key] = copy.deepcopy(chart)

    def clear(self) -> None:
        """Empties the cache and resets hit/miss counters."""
        with self._lock:
            self._cache.clear()
            self._hits = 0
            self._misses = 0

    def get_stats(self) -> Dict[str, Any]:
        """Returns cache telemetry and hit rates."""
        with self._lock:
            total = self._hits + self._misses
            hit_rate = round(self._hits / total, 4) if total > 0 else 0.0
            return {
                "size": len(self._cache),
                "max_size": self.max_size,
                "hits": self._hits,
                "misses": self._misses,
                "total_lookups": total,
                "hit_rate": hit_rate
            }


default_chart_cache = ChartCalculationCache(max_size=500)

