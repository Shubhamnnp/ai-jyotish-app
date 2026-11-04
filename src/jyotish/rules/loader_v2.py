"""
Rule Loader & Validator for Schema v2.
Validates rule payloads and files against the Pydantic Schema v2 specification,
rejecting malformed, unversioned, or schema-violating entries.
"""

from typing import List, Dict, Any, Union, Tuple, Optional
from pathlib import Path
import json
from pydantic import ValidationError

from .schema_v2 import RuleV2


class RuleValidationError(Exception):
    """Raised when a rule payload fails Schema v2 validation."""
    def __init__(self, rule_id: Optional[str], errors: List[Any], message: str = ""):
        self.rule_id = rule_id
        self.errors = errors
        prefix = f"Rule '{rule_id}' failed Schema v2 validation" if rule_id else "Rule payload failed Schema v2 validation"
        super().__init__(f"{prefix}: {message or errors}")


def load_rule_v2(data: Dict[str, Any]) -> RuleV2:
    """
    Validates a raw dictionary against RuleV2.
    Raises RuleValidationError with detailed breakdown on failure.
    """
    rule_id = data.get("rule_id") if isinstance(data, dict) else None
    try:
        return RuleV2.model_validate(data)
    except ValidationError as err:
        raise RuleValidationError(rule_id=rule_id, errors=err.errors()) from err


def validate_rule_dict(data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """
    Validates a rule dictionary without raising an exception.
    Returns: (is_valid, error_message_if_any)
    """
    try:
        load_rule_v2(data)
        return True, None
    except RuleValidationError as err:
        return False, str(err)


def load_rules_file_v2(file_path: Union[str, Path]) -> List[RuleV2]:
    """
    Loads and validates all rules from a Schema v2 JSON file.
    Expected format: {"schema_version": 2, "rules": [...]} or raw list of rules [...].
    """
    p = Path(file_path)
    if not p.exists():
        raise FileNotFoundError(f"Rules file not found: {p}")

    with open(p, "r", encoding="utf-8") as f:
        content = json.load(f)

    raw_rules = content.get("rules", content) if isinstance(content, dict) else content
    if not isinstance(raw_rules, list):
        raise RuleValidationError(rule_id=None, errors=[], message=f"Expected JSON list of rules in {p}")

    rules_out: List[RuleV2] = []
    for idx, r_data in enumerate(raw_rules):
        if not isinstance(r_data, dict):
            raise RuleValidationError(rule_id=f"index_{idx}", errors=[], message="Rule element must be a dictionary")
        rules_out.append(load_rule_v2(r_data))

    return rules_out


def export_schema_v2_json() -> Dict[str, Any]:
    """Generates standard JSON Schema for RuleV2."""
    return RuleV2.model_json_schema()

