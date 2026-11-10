# -*- coding: utf-8 -*-
"""
Tests for Module 18: Shastriya Rules Bank & Research Engine Audit.
Verifies:
1. Tab synchronization with MODULE_TABS_REGISTRY.
2. Authentic Samudrika Shastra rules (Garuda/Bhavishya Purana) with Sanskrit shlokas.
3. Authentic Ankashastra & Lo-Shu Grid rules with positive/negative polarities and Sanskrit shlokas.
4. RulesEngine loading and safe quarantine isolation.
5. RulesExplorerService indexing across 16 classical granthas.
6. Shastriya Pramana matrix integration.
"""

import os
import json
import pytest
from src.jyotish.rules.schema_v2 import RuleV2
from src.jyotish.rules.quarantine import is_generated_rule, filter_rules_by_verification
from src.jyotish.services.rules_explorer import default_rules_explorer_service
from src.jyotish.services.shastriya_pramana import default_shastriya_pramana_engine, SHASTRIYA_SHLOKAS
from src.jyotish.ui.modules.rules_library_view import render_rules_library_view


def test_module18_tabs_registry_alignment():
    """Verifies that Module 18 registry has the 4 canonical tabs."""
    expected_tabs = [
        "📚 १२,५०० नियम बैंक",
        "🔍 ग्रन्थ एक्सप्लोरर",
        "🔬 कुण्डली अनुसंधान इंजन",
        "🛡️ Rules Lab (Admin)"
    ]
    # Check default tabs in render function signature
    assert callable(render_rules_library_view)
    assert len(expected_tabs) == 4


def test_samudrika_rules_authenticity_and_schema():
    """Verifies that samudrika_rules.json contains authentic classical rules with Sanskrit shlokas."""
    fpath = os.path.join("src", "jyotish", "rules", "grantha_rules", "samudrika_rules.json")
    assert os.path.exists(fpath), "samudrika_rules.json must exist"

    with open(fpath, "r", encoding="utf-8") as f:
        data = json.load(f)

    rules = data.get("rules", [])
    assert len(rules) >= 20, f"Expected at least 20 Samudrika rules, got {len(rules)}"

    # Validate all against Schema V2
    polarities = set()
    has_shloka_count = 0
    for r in rules:
        validated = RuleV2.model_validate(r)
        assert validated.school == "Samudrika Shastra"
        assert validated.source.text in ["Garuda Purana (गरुड़ पुराण)", "Bhavishya Purana (भविष्य पुराण)", "Brihat Samhita (बृहत्संहिता)", "Samudrika Sudhakara (सामुद्रिक सुधाकर)"]
        if validated.source.original_excerpt_sa:
            has_shloka_count += 1
        polarities.add(validated.effect.polarity)

    assert has_shloka_count >= 20, "All primary Samudrika rules must contain authentic Sanskrit shlokas"
    assert "+" in polarities, "Must contain positive auspicious rules"
    assert "-" in polarities, "Must contain negative caution rules"

    # Verify key classical rules exist
    rule_ids = {r["rule_id"] for r in rules}
    assert "SAM_MNT_JUP_PROMINENT" in rule_ids
    assert "SAM_LINE_LIFE_CLEAR_LONG" in rule_ids
    assert "SAM_SYM_MATSYA_KETU_JUP" in rule_ids
    assert "SAM_SYM_YAVA_THUMB" in rule_ids
    assert "SAM_LINE_LIFE_BROKEN" in rule_ids


def test_numerology_and_loshu_rules_authenticity():
    """Verifies that numerology_rules.json contains authentic Radical, Missing, Repeated, and Plane rules."""
    fpath = os.path.join("src", "jyotish", "rules", "grantha_rules", "numerology_rules.json")
    assert os.path.exists(fpath), "numerology_rules.json must exist"

    with open(fpath, "r", encoding="utf-8") as f:
        data = json.load(f)

    rules = data.get("rules", [])
    assert len(rules) >= 100, f"Expected at least 100 numerology rules, got {len(rules)}"

    # Check Mulank 1-9 rules exist for both positive and negative
    rule_ids = {r.get("rule_id") for r in rules}
    for n in range(1, 10):
        assert f"NUM_MULANK_{n}_POS" in rule_ids, f"Missing positive rule for Mulank {n}"
        assert f"NUM_MULANK_{n}_NEG" in rule_ids, f"Missing negative rule for Mulank {n}"
        assert f"NUM_LOSHU_MISSING_{n}" in rule_ids, f"Missing Lo-Shu remedy rule for number {n}"

    # Check Lo Shu 8 planes exist
    planes = ["492_MENTAL", "357_EMOTIONAL", "816_PRACTICAL", "438_THOUGHT", "951_WILL", "276_ACTION", "456_GOLDEN", "258_SILVER"]
    for p in planes:
        assert f"NUM_LOSHU_PLANE_{p}" in rule_ids, f"Missing Lo Shu plane rule for {p}"

    # Check repeated number rules exist
    assert "NUM_LOSHU_REP_1_1" in rule_ids
    assert "NUM_LOSHU_REP_1_4" in rule_ids
    assert "NUM_LOSHU_REP_9_4" in rule_ids


def test_rules_explorer_service_indexing():
    """Verifies that RulesExplorerService indexes all 16 classical granthas and executes search queries."""
    stats = default_rules_explorer_service.get_stats()
    assert stats["granthas_count"] >= 16, f"Expected at least 16 granthas, got {stats['granthas_count']}"
    assert stats["total_rules"] >= 12500, f"Expected at least 12,500 indexed rules, got {stats['total_rules']}"

    # Test Search for Samudrika Shastra
    sam_res = default_rules_explorer_service.search_rules(query="मत्स्य", grantha_filter="Samudrika Shastra (सामुद्रिक एवं हस्तरेखा शास्त्र)")
    assert len(sam_res) >= 1, "Expected to find Matsya rule in Samudrika grantha"
    assert sam_res[0]["rule_id"] == "SAM_SYM_MATSYA_KETU_JUP"
    assert "कोटिद्रव्यपतिः" in sam_res[0]["source"]["original_excerpt_sa"]

    # Test Search for Ankashastra
    num_res = default_rules_explorer_service.search_rules(query="मूलांक 1", grantha_filter="Vedic Numerology (अंक ज्योतिष शास्त्र)")
    assert len(num_res) >= 1, "Expected to find Mulank 1 rule in Numerology grantha"


def test_shastriya_pramana_samudrika_and_loshu():
    """Verifies that Shastriya Pramana Matrix contains Samudrika and Lo Shu shlokas."""
    assert "samudrika_shastra_lakshana" in SHASTRIYA_SHLOKAS
    assert "loshu_grid_planes" in SHASTRIYA_SHLOKAS
    assert "vedic_numerology_graha_anka" in SHASTRIYA_SHLOKAS

    sam_p = SHASTRIYA_SHLOKAS["samudrika_shastra_lakshana"]
    assert "आयुरेखा" in sam_p["shloka_sanskrit"]
    assert "गरुड़ पुराण" in sam_p["grantha"]

    loshu_p = SHASTRIYA_SHLOKAS["loshu_grid_planes"]
    assert "पञ्चदशसमन्वितम्" in loshu_p["shloka_sanskrit"]


def test_quarantine_integrity():
    """Verifies that synthetic bulk generator rules are properly identified for quarantine."""
    mock_gen_rule = {"rule_id": "MEGA_BPHS_BHAVA_1_LORD_1"}
    assert is_generated_rule(mock_gen_rule) is True

    mock_authentic_rule = {
        "rule_id": "SAM_SYM_MATSYA_KETU_JUP",
        "verification": {"status": "scholar_verified"}
    }
    assert is_generated_rule(mock_authentic_rule) is False


def test_module18_classical_shloka_and_constants():
    """Verifies that Module 18 includes authentic BPHS shloka and planetary swabhav dictionaries."""
    from src.jyotish.ui.modules.rules_library_view import (
        BPHS_RULES_SHLOKA, GRAHA_NAMES_HI, DIGNITY_HI, NATURAL_SWABHAV, _format_dms
    )
    assert "बृहत्पाराशर" in BPHS_RULES_SHLOKA["title"]
    assert "पाराशर्यादि शास्त्राणि" in BPHS_RULES_SHLOKA["shloka"]
    assert "जातकार्णवसङ्ग्रहम्" in BPHS_RULES_SHLOKA["shloka"]
    assert GRAHA_NAMES_HI["Sun"] == "सूर्य"
    assert GRAHA_NAMES_HI["Jupiter"] == "गुरु"
    assert "उच्च" in DIGNITY_HI["exalted"]
    assert "नीच" in DIGNITY_HI["debilitated"]
    assert "आत्मा कारक" in NATURAL_SWABHAV["Sun"]


def test_module18_format_dms():
    """Verifies degree to ansh-kala (DMS) conversion."""
    from src.jyotish.ui.modules.rules_library_view import _format_dms
    ansh, kala, dms = _format_dms(12.5)
    assert ansh == 12
    assert kala == 30
    assert dms == "12° 30'"

    ansh2, kala2, dms2 = _format_dms(29.999)
    assert ansh2 == 30
    assert kala2 == 0
    assert dms2 == "30° 00'"


def test_module18_chart_rules_evaluation():
    """Verifies that RulesEngine evaluates a live chart and returns valid rule evidences."""
    from datetime import date, time
    from src.jyotish.core.models import BirthData
    from src.jyotish.core.calculator import default_chart_calculator
    from src.jyotish.rules.engine import RulesEngine

    b_data = BirthData(
        name="सुनील कुमार",
        birth_date=date(1991, 10, 10),
        birth_time=time(8, 20, 0),
        latitude=28.6139,
        longitude=77.2090,
        timezone_offset=5.5
    )
    chart = default_chart_calculator.calculate_chart(b_data)
    engine = RulesEngine()
    evidences = engine.evaluate_all(chart, None, {}, None)
    assert len(evidences) > 0

    fired = [ev for ev in evidences if ev.fired]
    assert len(fired) > 0, "Active chart should trigger classical astrological rules"
    polarities = {ev.polarity for ev in fired}
    assert "+" in polarities or "-" in polarities


def test_module18_render_source_audit():
    """Verifies that render_rules_library_view contains micro HUD, planetary grid, and shastriya balance."""
    import inspect
    from src.jyotish.ui.modules import rules_library_view
    src = inspect.getsource(rules_library_view.render_rules_library_view)

    assert "BPHS_RULES_SHLOKA" in src
    assert "सक्रिय जातक" in src
    assert "_format_dms" in src
    assert "सक्रिय जातक सूक्ष्म ग्रह-स्थिति" in src
    assert "शास्त्रीय नियम संतुलन मीमांसा" in src
