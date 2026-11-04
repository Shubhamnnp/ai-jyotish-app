"""
Unit tests for Schema v2 rule validation and loading (Phase 4 Task 1).
"""

import pytest
import json
from pathlib import Path
from src.jyotish.rules.schema_v2 import RuleV2, RuleSource, RuleCondition, RuleEffect
from src.jyotish.rules.loader_v2 import (
    load_rule_v2,
    validate_rule_dict,
    load_rules_file_v2,
    export_schema_v2_json,
    RuleValidationError,
)


@pytest.fixture
def valid_rule_v2_dict():
    return {
        "rule_id": "BPHS-24-LORD1-H1",
        "rule_name_hi": "लग्नेश लग्न में",
        "rule_name_en": "1st Lord in 1st House",
        "schema_version": 2,
        "school": "parashari",
        "source": {
            "text": "Brihat Parashara Hora Shastra",
            "edition": "Chowkhamba Classical Series",
            "chapter": 24,
            "verse": "11",
            "original_excerpt_sa": "लग्नेशे लग्नगे जीवे...",
            "paraphrase_hi": "लग्नेश यदि लग्न में हो तो जातक दीर्घायु एवं स्वाभिमानी होता है।",
            "paraphrase_en": "When 1st lord is placed in the 1st house, native is long-lived, bold, and respected.",
            "author": "Maharishi Parashara"
        },
        "condition": {
            "type": "ALL",
            "criteria": [
                {
                    "fact": "lord_of_house",
                    "house": 1,
                    "placed_in_house": 1
                }
            ]
        },
        "modifiers": {
            "strengthens_if": [
                {"fact": "dignity_in", "values": ["own", "exalted", "moolatrikona"]}
            ],
            "weakens_if": [
                {"fact": "combust"},
                {"fact": "debilitated_without_bhanga"}
            ],
            "bhanga_refs": ["BPHS-NEECHABHANGA-1"]
        },
        "effect": {
            "domain": "personality",
            "polarity": "+",
            "summary_hi": "दीर्घायु, आत्मविश्वासी, स्वस्थ शरीर",
            "summary_en": "Long life, self-confidence, healthy constitution",
            "themes": ["longevity", "confidence", "health"]
        },
        "applicability": {
            "dasha_required": False,
            "varga": "D1",
            "min_shadbala_ratio": 1.0
        },
        "verification": {
            "status": "scholar_verified",
            "verified_by": "Vedic Scholar Review Committee",
            "verified_on": "2026-11-04",
            "notes": "Verified against BPHS Chapter 24, Shloka 11."
        },
        "generated": False
    }


def test_valid_rule_v2_parsing(valid_rule_v2_dict):
    """Verify that a compliant Schema v2 rule parses with full fidelity."""
    rule = load_rule_v2(valid_rule_v2_dict)
    assert rule.rule_id == "BPHS-24-LORD1-H1"
    assert rule.schema_version == 2
    assert rule.school == "parashari"
    assert rule.source.text == "Brihat Parashara Hora Shastra"
    assert rule.source.chapter == 24
    assert rule.source.verse == "11"
    assert rule.condition.type == "ALL"
    assert len(rule.condition.criteria) == 1
    assert rule.condition.criteria[0].fact == "lord_of_house"
    assert rule.effect.polarity == "+"
    assert rule.verification.status == "scholar_verified"
    assert rule.generated is False


def test_reject_missing_required_fields(valid_rule_v2_dict):
    """Verify that missing required keys raise RuleValidationError."""
    # 1. Missing rule_id
    bad_data = valid_rule_v2_dict.copy()
    del bad_data["rule_id"]
    with pytest.raises(RuleValidationError) as exc:
        load_rule_v2(bad_data)
    assert "rule_id" in str(exc.value)

    # 2. Missing source
    bad_data = valid_rule_v2_dict.copy()
    del bad_data["source"]
    with pytest.raises(RuleValidationError):
        load_rule_v2(bad_data)

    # 3. Missing chapter in source
    bad_data = valid_rule_v2_dict.copy()
    bad_data["source"] = {"text": "BPHS"}  # missing chapter
    with pytest.raises(RuleValidationError):
        load_rule_v2(bad_data)


def test_reject_invalid_schema_version(valid_rule_v2_dict):
    """Schema version must be strictly 2."""
    bad_data = valid_rule_v2_dict.copy()
    bad_data["schema_version"] = 1
    with pytest.raises(RuleValidationError):
        load_rule_v2(bad_data)


def test_reject_invalid_polarity(valid_rule_v2_dict):
    """Polarity must be +, -, 0, or ~."""
    bad_data = valid_rule_v2_dict.copy()
    bad_data["effect"]["polarity"] = "positive"  # Invalid! Must be "+"
    with pytest.raises(RuleValidationError):
        load_rule_v2(bad_data)


def test_reject_invalid_verification_status(valid_rule_v2_dict):
    """Status must be draft, machine_checked, scholar_verified, or rejected."""
    bad_data = valid_rule_v2_dict.copy()
    bad_data["verification"]["status"] = "pending_approval"
    with pytest.raises(RuleValidationError):
        load_rule_v2(bad_data)


def test_export_json_schema():
    """Verify JSON Schema generation for front-end/tooling validation."""
    schema = export_schema_v2_json()
    assert isinstance(schema, dict)
    assert "properties" in schema
    assert "rule_id" in schema["properties"]
    assert "schema_version" in schema["properties"]
    assert "verification" in schema["properties"]


def test_load_rules_file_v2(tmp_path, valid_rule_v2_dict):
    """Verify loading from a multi-rule JSON file."""
    fpath = tmp_path / "test_rules.json"
    rule2 = valid_rule_v2_dict.copy()
    rule2["rule_id"] = "BPHS-24-LORD1-H2"
    fpath.write_text(json.dumps({"schema_version": 2, "rules": [valid_rule_v2_dict, rule2]}), encoding="utf-8")

    loaded = load_rules_file_v2(fpath)
    assert len(loaded) == 2
    assert loaded[0].rule_id == "BPHS-24-LORD1-H1"
    assert loaded[1].rule_id == "BPHS-24-LORD1-H2"
