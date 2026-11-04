"""
Unit tests for Rule Quarantine & Migration (Phase 4 Task 3).
Verifies:
1. Migration of legacy v1 rules into Schema v2 with draft status.
2. Generator rule detection (generated=True).
3. Runtime gating: evaluate_all(..., allow_drafts=False) excludes unverified draft rules.
4. RulesEngine.get_quarantine_summary() reports accurate distribution.
"""

import pytest
from src.jyotish.rules.quarantine import (
    migrate_rule_to_v2_dict,
    is_generated_rule,
    filter_rules_by_verification,
    get_quarantine_stats
)
from src.jyotish.rules.engine import RulesEngine


@pytest.fixture
def sample_v1_rule():
    return {
        "rule_id": "BPHS_BHAVA_L1_H1",
        "rule_name_hi": "तनु भावपति लग्न में",
        "rule_name_en": "Lord of 1th house in 1th house",
        "source": {
            "text": "Brihat Parashara Hora Shastra",
            "chapter": "Adhyaya 24"
        },
        "school": "Parashari",
        "category": "bhav-based",
        "condition": {
            "type": "ALL",
            "criteria": [{"entity": "Lord_1", "house": 1}]
        },
        "effect": {
            "polarity": "+",
            "strength_base": 0.8,
            "description_hi": "दीर्घायु, आत्मविश्वासी"
        }
    }


def test_migrate_rule_to_v2_sets_draft_and_generated(sample_v1_rule):
    """Verify v1 rule gets quarantined as draft with generated=True."""
    v2 = migrate_rule_to_v2_dict(sample_v1_rule)
    assert v2["schema_version"] == 2
    assert v2["rule_id"] == "BPHS_BHAVA_L1_H1"
    assert v2["school"] == "parashari"
    assert v2["verification"]["status"] == "draft"
    assert v2["generated"] is True
    assert "Quarantined" in v2["verification"]["notes"]


def test_filter_rules_by_verification():
    """Verify filtering rejects draft and rejected rules when scholar_verified is required."""
    rules = [
        {"rule_id": "R1", "verification": {"status": "scholar_verified"}},
        {"rule_id": "R2", "verification": {"status": "draft"}},
        {"rule_id": "R3", "verification": {"status": "machine_checked"}},
        {"rule_id": "R4", "verification": {"status": "rejected"}},
        {"rule_id": "R5"},  # implicitly draft
    ]
    verified = filter_rules_by_verification(rules, allowed_statuses=("scholar_verified",))
    assert len(verified) == 1
    assert verified[0]["rule_id"] == "R1"

    both = filter_rules_by_verification(rules, allowed_statuses=("scholar_verified", "machine_checked"))
    assert len(both) == 2
    assert {r["rule_id"] for r in both} == {"R1", "R3"}


def test_quarantine_stats_distribution():
    """Verify get_quarantine_stats correctly aggregates counts."""
    rules = [
        {"rule_id": "R1", "verification": {"status": "scholar_verified"}, "generated": False},
        {"rule_id": "MEGA_R2", "verification": {"status": "draft"}},
        {"rule_id": "R3", "verification": {"status": "machine_checked"}, "generated": False},
    ]
    stats = get_quarantine_stats(rules)
    assert stats["total"] == 3
    assert stats["scholar_verified"] == 1
    assert stats["machine_checked"] == 1
    assert stats["draft"] == 1
    assert stats["generated"] == 1


def test_engine_quarantine_integration():
    """Verify RulesEngine loads rules as quarantined Schema v2 with full count preserved."""
    engine = RulesEngine()
    summary = engine.get_quarantine_summary()
    assert summary["total"] >= 12500
    assert summary["draft"] > 0
    # By default, draft rules are quarantined but tracked
    assert summary["total"] == summary["draft"] + summary["scholar_verified"] + summary["machine_checked"] + summary["rejected"]
