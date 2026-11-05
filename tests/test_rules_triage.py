"""
Unit tests for Rules Triage & Classification Engine (Phase U1 Task U1-T3/T4).
"""

import pytest
from pathlib import Path
from scripts.rules_triage import classify_rules, generate_reports


def test_classify_rules_structure():
    """Verify triage correctly runs and respects non-negotiable verification constraints."""
    triage = classify_rules()
    summary = triage["summary"]

    assert summary["total_rules"] == 12506
    # Non-negotiable rule: Never auto-promote to scholar_verified
    assert summary["scholar_verified"] == 0
    # Must identify clean machine_checked candidates
    assert summary["machine_checked"] > 3000
    # Must quarantine conflicting/corrupt rules
    assert summary["quarantined"] > 5000
    # Zero rules rejected/lost
    assert summary["rejected"] == 0
    assert summary["total_rules"] == summary["machine_checked"] + summary["draft"] + summary["quarantined"] + summary["scholar_verified"] + summary["rejected"]


def test_triage_reports_generated():
    """Verify RULES_TRIAGE.md and scholar review CSV exist and are populated."""
    triage = classify_rules()
    generate_reports(triage)

    md_path = Path("docs/upgrade/RULES_TRIAGE.md")
    csv_path = Path("docs/upgrade/rules_scholar_review_needed.csv")

    assert md_path.exists()
    assert csv_path.exists()

    md_content = md_path.read_text(encoding="utf-8")
    assert "12,506" in md_content
    assert "scholar_verified" in md_content
    assert "machine_checked" in md_content
    assert "quarantined" in md_content
