"""
Rule Quarantine & Migration Module for JyotishOS (Phase 4 Task 3).
Performs safe in-place quarantine of legacy unverified rules:
- Migrates v1 rule dictionaries to Schema v2 with verification.status = 'draft'
- Identifies and flags bulk-generated rules with generated = True
- Provides filtering mechanisms so user-facing Phaladesh only evaluates
  'scholar_verified' and 'machine_checked' rules.
- Never deletes rules; keeps full inventory available for Scholar Review / Rules Lab.
"""

from typing import Dict, List, Any, Tuple, Optional, Set
from .schema_v2 import RuleV2, RuleSource, RuleCondition, RuleEffect, RuleModifiers, RuleApplicability, RuleVerification


GENERATOR_RULE_PREFIXES = (
    "MEGA_", "PHASE", "REACH", "BUILD", "BPHS_BHAVA_", "BPHS_YOGINI_",
    "BPHS_NAK_", "BPHS_SUDARSHANA_", "PD_BHAVA_LORD_", "BJ_BLORD_"
)


def is_generated_rule(rule: Dict[str, Any]) -> bool:
    """Determines if a rule was produced by bulk synthetic generator scripts."""
    if not isinstance(rule, dict):
        return False

    if rule.get("generated") is True:
        return True

    r_id = rule.get("rule_id", "")
    for prefix in GENERATOR_RULE_PREFIXES:
        if prefix in r_id:
            return True

    # Check for metadata synthetic/generator markers (Classical Vedic is authentic antiquity, not a generator marker)
    source = rule.get("source", {})
    if isinstance(source, dict):
        if source.get("generator") or source.get("synthetic") or "generator" in str(source.get("notes", "")).lower():
            return True

    return False


def migrate_rule_to_v2_dict(raw: Dict[str, Any]) -> Dict[str, Any]:
    """
    Transforms a v1 rule dictionary into a compliant Schema v2 dictionary with draft status.
    Never mutates original argument.
    """
    if not isinstance(raw, dict):
        raise ValueError("Rule data must be a dictionary")

    out = dict(raw)
    out["schema_version"] = 2

    # Ensure rule_id
    r_id = out.get("rule_id", "UNKNOWN_RULE")
    out["rule_id"] = r_id

    # Generated flag
    out["generated"] = raw.get("generated", is_generated_rule(raw))

    # School normalization
    school = out.get("school", "parashari")
    out["school"] = str(school).lower()

    # Source normalization
    src = out.get("source", {})
    if not isinstance(src, dict):
        src = {"text": str(src), "chapter": 1}
    else:
        src = dict(src)
        if "text" not in src:
            src["text"] = "Brihat Parashara Hora Shastra"
        if "chapter" not in src:
            src["chapter"] = 1
    out["source"] = src

    # Condition normalization
    cond = out.get("condition", {})
    if not isinstance(cond, dict):
        cond = {"type": "ALL", "criteria": []}
    else:
        cond = dict(cond)
        if "type" not in cond:
            cond["type"] = "ALL"
        if "criteria" not in cond or not isinstance(cond["criteria"], list):
            cond["criteria"] = []
    out["condition"] = cond

    # Effect normalization
    eff = out.get("effect", {})
    if not isinstance(eff, dict):
        eff = {"polarity": "+", "domain": "general"}
    else:
        eff = dict(eff)
        # Normalize polarity: must be +, -, 0, or ~
        pol = eff.get("polarity", "+")
        if pol not in ("+", "-", "0", "~"):
            eff["polarity"] = "+" if "pos" in str(pol).lower() or pol == 1 else "-"
        if "domain" not in eff:
            eff["domain"] = out.get("category", "general")
    out["effect"] = eff

    # Verification metadata (Quarantine default = 'draft')
    ver = out.get("verification")
    if not isinstance(ver, dict) or "status" not in ver:
        out["verification"] = {
            "status": "draft",
            "verified_by": None,
            "verified_on": None,
            "notes": "Quarantined rule from legacy library awaiting scholar review."
        }

    return out


def migrate_rule_to_v2(raw: Dict[str, Any]) -> RuleV2:
    """Migrates a v1 dictionary into a validated RuleV2 instance."""
    v2_dict = migrate_rule_to_v2_dict(raw)
    return RuleV2.model_validate(v2_dict)


def filter_rules_by_verification(
    rules: List[Dict[str, Any]],
    allowed_statuses: Tuple[str, ...] = ("scholar_verified", "machine_checked")
) -> List[Dict[str, Any]]:
    """
    Filters rule set to only those with authorized verification status.
    Excludes quarantined draft rules.
    """
    filtered = []
    for r in rules:
        ver = r.get("verification", {})
        status = ver.get("status") if isinstance(ver, dict) else "draft"
        if status in allowed_statuses:
            filtered.append(r)
    return filtered


def get_quarantine_stats(rules: List[Dict[str, Any]]) -> Dict[str, int]:
    """Computes distribution of rules across verification lifecycle states."""
    stats = {
        "total": len(rules),
        "scholar_verified": 0,
        "machine_checked": 0,
        "draft": 0,
        "quarantined": 0,
        "rejected": 0,
        "generated": 0
    }
    for r in rules:
        ver = r.get("verification", {})
        status = ver.get("status", "draft") if isinstance(ver, dict) else "draft"
        if status in stats:
            stats[status] += 1
        else:
            stats["draft"] += 1

        if r.get("generated") is True or is_generated_rule(r):
            stats["generated"] += 1

    return stats

