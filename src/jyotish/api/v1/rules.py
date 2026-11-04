"""
Classical Shastriya Rules Endpoints for /api/v1/rules.
Provides catalog count, metadata, and fast O(1) indexed search across classical Shastriya rules.
"""

from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Query, Header, HTTPException, status
from pydantic import BaseModel
from ...rules.engine import default_rules_engine
from ...rules.quarantine import get_quarantine_stats, filter_rules_by_verification

router = APIRouter(prefix="/rules", tags=["v1-rules"])


class RuleReviewRequest(BaseModel):
    rule_id: str
    new_status: str  # "scholar_verified", "verified", "rejected", "draft"
    scholar_notes: Optional[str] = None


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


@router.get("/audit-stats")
def get_audit_stats(x_admin_role: Optional[str] = Header(None, alias="X-Admin-Role")):
    """Returns quarantined rules audit and review queue statistics (Admin)."""
    if x_admin_role not in ("admin", "researcher", "scholar"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required to access Rules Lab audit stats."
        )
    stats = get_quarantine_stats(default_rules_engine.rules)
    return {
        "status": "success",
        "stats": stats,
        "rules_lab_ready": True
    }


@router.get("/drafts")
def list_draft_rules(
    limit: int = Query(default=20, le=100),
    offset: int = Query(default=0, ge=0),
    grantha: Optional[str] = Query(None),
    x_admin_role: Optional[str] = Header(None, alias="X-Admin-Role")
):
    """Lists draft quarantined rules waiting in the scholar review queue (Admin)."""
    if x_admin_role not in ("admin", "researcher", "scholar"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required to access draft review queue."
        )
    drafts = filter_rules_by_verification(default_rules_engine.rules, "draft")
    if grantha:
        drafts = [r for r in drafts if r.get("source", {}).get("text", "").lower() == grantha.lower()]

    total_drafts = len(drafts)
    slice_drafts = drafts[offset:offset + limit]
    return {
        "total_drafts": total_drafts,
        "offset": offset,
        "limit": limit,
        "drafts": slice_drafts
    }


@router.post("/review")
def review_rule(
    payload: RuleReviewRequest,
    x_admin_role: Optional[str] = Header(None, alias="X-Admin-Role")
):
    """Reviews and updates the verification status of a rule (Admin)."""
    if x_admin_role not in ("admin", "researcher", "scholar"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required to review and promote rules."
        )
    r = default_rules_engine.rules_by_id.get(payload.rule_id)
    if not r:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Rule {payload.rule_id} not found.")

    if "verification" not in r:
        r["verification"] = {}
    r["verification"]["status"] = payload.new_status
    if payload.scholar_notes:
        r["verification"]["notes"] = payload.scholar_notes

    return {
        "status": "updated",
        "rule_id": payload.rule_id,
        "new_status": payload.new_status
    }
