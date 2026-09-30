"""
Classical Shastriya Rules Endpoints for /api/v1/rules.
Provides catalog count, metadata, and fast O(1) indexed search across 12,500+ classical rules.
"""

from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Query
from ...rules.engine import default_rules_engine

router = APIRouter(prefix="/rules", tags=["v1-rules"])


@router.get("/count")
def get_rules_count():
    """Returns total loaded and indexed Shastriya rules across all Granthas."""
    total = len(default_rules_engine.rules)
    indexed = default_rules_engine.inverted_index.total_rules if hasattr(default_rules_engine, "inverted_index") else total
    return {
        "total_rules": total,
        "indexed_rules": indexed,
        "status": "operational",
        "schools": ["Parashari", "Jaimini", "KP", "LalKitab", "Tajika", "Nadi"]
    }


@router.get("/search")
def search_rules(
    planet: Optional[str] = Query(None),
    house: Optional[int] = Query(None),
    theme: Optional[str] = Query(None),
    school: Optional[str] = Query(None),
    limit: int = Query(default=20, le=100)
):
    """Searches Shastriya rules catalog by planet, house, theme, or school."""
    index = default_rules_engine.inverted_index
    matched: List[Dict[str, Any]] = []

    # Use inverted index keys if possible
    if theme and f"theme:{theme.lower()}" in index._index:
        candidates = index._index[f"theme:{theme.lower()}"]
    elif planet and f"planet:{planet}" in index._index:
        candidates = index._index[f"planet:{planet}"]
    elif house and f"house:{house}" in index._index:
        candidates = index._index[f"house:{house}"]
    else:
        candidates = default_rules_engine.rules

    for r in candidates:
        if planet and planet.lower() not in (str(r.get("condition", "")) + " " + r.get("rule_name_en", "")).lower():
            continue
        if house and f"house_{house}" not in (str(r.get("condition", "")) + " " + r.get("rule_name_en", "")).lower() and f"{house}th" not in (str(r.get("condition", "")) + " " + r.get("rule_name_en", "")).lower():
            continue
        if school and r.get("school", "").lower() != school.lower():
            continue

        matched.append({
            "rule_id": r.get("rule_id"),
            "rule_name_hi": r.get("rule_name_hi"),
            "rule_name_en": r.get("rule_name_en"),
            "school": r.get("school"),
            "source_grantha": r.get("source", {}).get("text", "Classical Shastra"),
            "themes": r.get("effect", {}).get("themes", []),
            "polarity": r.get("effect", {}).get("polarity", "+")
        })

        if len(matched) >= limit:
            break

    return {
        "matched_count": len(matched),
        "limit": limit,
        "rules": matched
    }
