"""
Unit tests for Deterministic Rule Linter (Phase U1, Task U1-T1).
Ensures the rule linter functions as a deterministic gate in CI.
"""

import os
import pytest
from scripts.rules_lint import lint_all_rules, REPO_ROOT

def test_rule_linter_execution():
    """Verify that rule linter completes without error and generates CSV and markdown reports."""
    total_rules, total_issues = lint_all_rules()
    
    # 1. Total rules check
    assert total_rules == 12506, f"Expected 12,506 rules, got {total_rules}"
    assert total_issues > 0, "Expected linter to flag known rule quality issues"
    
    # 2. Output files existence
    csv_path = os.path.join(REPO_ROOT, "docs", "upgrade", "rules_lint_issues.csv")
    md_path = os.path.join(REPO_ROOT, "docs", "upgrade", "RULES_LINT_REPORT.md")
    
    assert os.path.exists(csv_path), "CSV report must be created"
    assert os.path.exists(md_path), "Markdown report must be created"
    assert os.path.getsize(csv_path) > 1000, "CSV report must not be empty"
    assert os.path.getsize(md_path) > 500, "Markdown report must not be empty"

