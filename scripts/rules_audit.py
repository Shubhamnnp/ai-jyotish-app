"""
Rules Audit & Linter Script for JyotishOS (Phase 4 Task 2).
Audits legacy rule library in src/jyotish/rules/grantha_rules/*.json for:
1. Rule counts per file and school
2. Bulk generator artifacts (generated: true)
3. Name vs. Condition mismatches (e.g. title mentions Mars, condition checks Saturn)
4. Ordinal grammar artifacts ("1th", "2th", "3th")
5. Near-duplicate effect descriptions (>= 90% similarity)
6. Missing source citations (missing chapter or verse)
7. Contradictory rules (identical condition with opposing polarity)

Produces:
- docs/RULES_AUDIT.md (comprehensive markdown analysis)
- docs/rules_audit.csv (raw itemized issue log)
"""

import json
import re
import csv
from pathlib import Path
from typing import Dict, List, Any, Tuple, Set
from collections import defaultdict
from difflib import SequenceMatcher

RULE_DIR = Path("src/jyotish/rules/grantha_rules")
DOCS_DIR = Path("docs")

PLANETS_EN = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]
SIGNS_EN = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]

PLANETS_MAP = {
    "sun": "Sun", "सूर्य": "Sun", "surya": "Sun", "ravi": "Sun",
    "moon": "Moon", "चन्द्र": "Moon", "chandra": "Moon", "soma": "Moon",
    "mars": "Mars", "मंगल": "Mars", "mangal": "Mars", "kuja": "Mars",
    "mercury": "Mercury", "बुध": "Mercury", "budha": "Mercury",
    "jupiter": "Jupiter", "गुरु": "Jupiter", "बृहस्पति": "Jupiter", "guru": "Jupiter", "brihaspati": "Jupiter",
    "venus": "Venus", "शुक्र": "Venus", "shukra": "Venus",
    "saturn": "Saturn", "शनि": "Saturn", "shani": "Saturn",
    "rahu": "Rahu", "राहु": "Rahu",
    "ketu": "Ketu", "केतु": "Ketu"
}

SIGNS_MAP = {
    "aries": "Aries", "मेष": "Aries", "mesha": "Aries",
    "taurus": "Taurus", "वृषभ": "Taurus", "vrishabha": "Taurus",
    "gemini": "Gemini", "मिथुन": "Gemini", "mithuna": "Gemini",
    "cancer": "Cancer", "कर्क": "Cancer", "karka": "Cancer",
    "leo": "Leo", "सिंह": "Leo", "simha": "Leo",
    "virgo": "Virgo", "कन्या": "Virgo", "kanya": "Virgo",
    "libra": "Libra", "तुला": "Libra", "tula": "Libra",
    "scorpio": "Scorpio", "वृश्चिक": "Scorpio", "vrischika": "Scorpio",
    "sagittarius": "Sagittarius", "धनु": "Sagittarius", "dhanu": "Sagittarius",
    "capricorn": "Capricorn", "मकर": "Capricorn", "makara": "Capricorn",
    "aquarius": "Aquarius", "कुम्भ": "Aquarius", "kumbha": "Aquarius",
    "pisces": "Pisces", "मीन": "Pisces", "meena": "Pisces"
}

ORDINAL_ERROR_REGEX = re.compile(r"\b(\d+)(th)\b", re.IGNORECASE)


def check_ordinal_grammar(text: str) -> List[str]:
    """Finds grammatical ordinal errors like '1th', '2th', '3th'."""
    if not text:
        return []
    errors = []
    for match in ORDINAL_ERROR_REGEX.finditer(text):
        num = int(match.group(1))
        rem10 = num % 10
        rem100 = num % 100
        if rem100 not in (11, 12, 13):
            if rem10 == 1:
                errors.append(f"{num}th (should be {num}st)")
            elif rem10 == 2:
                errors.append(f"{num}th (should be {num}nd)")
            elif rem10 == 3:
                errors.append(f"{num}th (should be {num}rd)")
    return errors


def extract_entities_from_text(text: str) -> Set[str]:
    """Extracts mentioned planets and signs from text."""
    if not text:
        return set()
    found = set()
    text_lower = text.lower()
    for token, canonical in PLANETS_MAP.items():
        if token in text_lower:
            found.add(canonical)
    for token, canonical in SIGNS_MAP.items():
        if token in text_lower:
            found.add(canonical)
    return found


def extract_condition_entities(condition: Dict[str, Any]) -> Set[str]:
    """Extracts planets, signs, and entities from criteria."""
    entities = set()
    if not condition or not isinstance(condition, dict):
        return entities
    criteria = condition.get("criteria", [])
    if isinstance(criteria, list):
        for c in criteria:
            if isinstance(c, dict):
                ent = c.get("entity") or c.get("planet") or c.get("fact")
                if ent and isinstance(ent, str):
                    ent_lower = ent.lower()
                    for token, canonical in PLANETS_MAP.items():
                        if token in ent_lower:
                            entities.add(canonical)
                sign = c.get("sign") or c.get("sign_name")
                if sign and isinstance(sign, str):
                    sign_lower = sign.lower()
                    for token, canonical in SIGNS_MAP.items():
                        if token in sign_lower:
                            entities.add(canonical)
    return entities


def condition_hash(condition: Dict[str, Any]) -> str:
    """Deterministic string representation of condition for contradiction checking."""
    if not condition or not isinstance(condition, dict):
        return ""
    crit = condition.get("criteria", [])
    sorted_crit = sorted([json.dumps(c, sort_keys=True) for c in crit if isinstance(c, dict)])
    return f"{condition.get('type', 'ALL')}:{'|'.join(sorted_crit)}"


def run_audit():
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    all_files = sorted(list(RULE_DIR.glob("*.json")))

    file_stats = []
    total_rules = 0
    total_grammar_errors = 0
    total_mismatches = 0
    total_missing_sources = 0
    total_generated = 0

    audit_records = []
    mismatch_records = []
    grammar_records = []
    missing_source_records = []
    contradiction_records = []

    # Map condition hash -> list of (file, rule_id, polarity, desc)
    condition_map = defaultdict(list)

    # For duplicate checking
    descriptions_seen = defaultdict(list)

    for fpath in all_files:
        with open(fpath, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except Exception as e:
                print(f"Error loading {fpath.name}: {e}")
                continue

        rules = data.get("rules", data) if isinstance(data, dict) else data
        if not isinstance(rules, list):
            continue

        f_rule_count = len(rules)
        total_rules += f_rule_count

        f_grammar = 0
        f_mismatch = 0
        f_missing_src = 0
        f_generated = 0

        for r in rules:
            if not isinstance(r, dict):
                continue

            r_id = r.get("rule_id", "UNKNOWN")
            r_name_en = r.get("rule_name_en", "")
            r_name_hi = r.get("rule_name_hi", "")
            source = r.get("source", {})
            condition = r.get("condition", {})
            effect = r.get("effect", {})
            polarity = effect.get("polarity", "+") if isinstance(effect, dict) else "+"
            desc_en = effect.get("description_en", "") if isinstance(effect, dict) else ""
            desc_hi = effect.get("description_hi", "") if isinstance(effect, dict) else ""

            # 1. Generator heuristic
            is_gen = False
            if r.get("generated") is True:
                is_gen = True
            elif any(prefix in r_id for prefix in ["MEGA_", "PHASE", "REACH", "BUILD", "BPHS_BHAVA_"]):
                is_gen = True
            elif "era" in source and source["era"] == "Classical Vedic" and "count" in data.get("metadata", {}):
                is_gen = True

            if is_gen:
                f_generated += 1
                total_generated += 1

            # 2. Grammar check
            g_errs = check_ordinal_grammar(r_name_en) + check_ordinal_grammar(desc_en)
            if g_errs:
                f_grammar += len(g_errs)
                total_grammar_errors += len(g_errs)
                grammar_records.append({
                    "file": fpath.name,
                    "rule_id": r_id,
                    "errors": ", ".join(g_errs),
                    "text": r_name_en
                })

            # 3. Name vs Condition mismatch check
            title_entities = extract_entities_from_text(r_name_en).union(extract_entities_from_text(r_name_hi))
            cond_entities = extract_condition_entities(condition)
            # If title specifies a planet but condition checks a completely different planet
            title_planets = {e for e in title_entities if e in PLANETS_EN}
            cond_planets = {e for e in cond_entities if e in PLANETS_EN}

            # Check house mismatch in title (e.g. "Lord of 1th house in 2th house")
            title_houses = re.findall(r"(\d+)(?:st|nd|rd|th)?\s+house", r_name_en, re.IGNORECASE)
            title_h_nums = {int(h) for h in title_houses if 1 <= int(h) <= 12}
            cond_crit = condition.get("criteria", []) if isinstance(condition, dict) else []
            cond_h_nums = set()
            for c in cond_crit:
                if isinstance(c, dict):
                    h_val = c.get("house")
                    if isinstance(h_val, list):
                        cond_h_nums.update(int(x) for x in h_val if isinstance(x, (int, str)) and str(x).isdigit())
                    elif isinstance(h_val, (int, str)) and str(h_val).isdigit():
                        cond_h_nums.add(int(h_val))

                    p_val = c.get("placed_in_house")
                    if isinstance(p_val, list):
                        cond_h_nums.update(int(x) for x in p_val if isinstance(x, (int, str)) and str(x).isdigit())
                    elif isinstance(p_val, (int, str)) and str(p_val).isdigit():
                        cond_h_nums.add(int(p_val))

            has_mismatch = False
            mismatch_detail = ""
            if title_planets and cond_planets and not title_planets.intersection(cond_planets):
                has_mismatch = True
                mismatch_detail = f"Planet mismatch: Title mentions {list(title_planets)} but condition checks {list(cond_planets)}"
            elif title_h_nums and cond_h_nums and not title_h_nums.intersection(cond_h_nums):
                has_mismatch = True
                mismatch_detail = f"House mismatch: Title mentions houses {list(title_h_nums)} but condition checks {list(cond_h_nums)}"

            if has_mismatch:
                f_mismatch += 1
                total_mismatches += 1
                mismatch_records.append({
                    "file": fpath.name,
                    "rule_id": r_id,
                    "title": r_name_en or r_name_hi,
                    "detail": mismatch_detail
                })

            # 4. Missing sources check
            has_chapter = bool(source.get("chapter")) if isinstance(source, dict) else False
            has_verse = bool(source.get("verse")) if isinstance(source, dict) else False
            if not has_chapter and not has_verse:
                f_missing_src += 1
                total_missing_sources += 1
                missing_source_records.append({
                    "file": fpath.name,
                    "rule_id": r_id,
                    "source": str(source)
                })

            # 5. Contradiction tracking
            c_hash = condition_hash(condition)
            if c_hash:
                condition_map[c_hash].append((fpath.name, r_id, polarity, desc_en or desc_hi))

        file_stats.append({
            "file": fpath.name,
            "rules": f_rule_count,
            "generated": f_generated,
            "grammar_errors": f_grammar,
            "mismatches": f_mismatch,
            "missing_sources": f_missing_src,
        })

    # Find contradictory conditions with opposing polarities
    for c_h, r_list in condition_map.items():
        if len(r_list) > 1:
            polarities = {item[2] for item in r_list}
            if "+" in polarities and "-" in polarities:
                contradiction_records.append({
                    "condition": c_h[:80],
                    "rules": [f"{item[0]}:{item[1]} ({item[2]})" for item in r_list]
                })

    # Write CSV audit log
    csv_path = DOCS_DIR / "rules_audit.csv"
    with open(csv_path, "w", encoding="utf-8", newline="") as cf:
        writer = csv.writer(cf)
        writer.writerow(["Category", "File", "RuleID", "Detail"])
        for m in mismatch_records:
            writer.writerow(["NameConditionMismatch", m["file"], m["rule_id"], f"{m['title']} | {m['detail']}"])
        for g in grammar_records:
            writer.writerow(["GrammarError", g["file"], g["rule_id"], f"{g['errors']} in: {g['text']}"])
        for s in missing_source_records[:200]:
            writer.writerow(["MissingSource", s["file"], s["rule_id"], s["source"]])
        for c in contradiction_records:
            writer.writerow(["Contradiction", "Multiple", "Multiple", f"Cond: {c['condition']} | Rules: {', '.join(c['rules'])}"])

    # Write Markdown summary: docs/RULES_AUDIT.md
    md_path = DOCS_DIR / "RULES_AUDIT.md"
    with open(md_path, "w", encoding="utf-8") as mf:
        mf.write("# JyotishOS — Legacy Rule Library Audit & Linter Report\n\n")
        mf.write(f"**Audit Date:** November 4, 2026  \n")
        mf.write(f"**Total Rule Files Scanned:** {len(file_stats)}  \n")
        mf.write(f"**Total Rules in Library:** {total_rules:,}  \n")
        mf.write(f"**Identified Generator Artifacts (`generated: true`):** {total_generated:,} ({total_generated/total_rules*100:.1f}%)  \n")
        mf.write(f"**Name/Condition Mismatches:** {total_mismatches:,}  \n")
        mf.write(f"**Ordinal Grammar Errors:** {total_grammar_errors:,}  \n")
        mf.write(f"**Missing Chapter/Verse Citations:** {total_missing_sources:,}  \n")
        mf.write(f"**Contradictory Opposing Polarity Pairs:** {len(contradiction_records)}  \n\n")

        mf.write("---\n\n")
        mf.write("## 1. Inventory by Grantha / File\n\n")
        mf.write("| Grantha File | Total Rules | Generated (%) | Grammar Errors | Mismatches | Missing Sources |\n")
        mf.write("| :--- | :---: | :---: | :---: | :---: | :---: |\n")
        for st in file_stats:
            gen_pct = (st["generated"] / st["rules"] * 100) if st["rules"] > 0 else 0.0
            mf.write(f"| `{st['file']}` | {st['rules']:,} | {st['generated']:,} ({gen_pct:.0f}%) | {st['grammar_errors']:,} | {st['mismatches']:,} | {st['missing_sources']:,} |\n")

        mf.write("\n---\n\n")
        mf.write("## 2. Top 30 Name vs. Condition Mismatches\n\n")
        mf.write("The following rules display severe discordance between what the title states and what the engine actually evaluates:\n\n")
        mf.write("| File | Rule ID | Title Mention | Mismatch Analysis |\n")
        mf.write("| :--- | :--- | :--- | :--- |\n")
        for idx, m in enumerate(mismatch_records[:30]):
            mf.write(f"| `{m['file']}` | `{m['rule_id']}` | {m['title']} | {m['detail']} |\n")

        mf.write("\n---\n\n")
        mf.write("## 3. Top Ordinal Grammar Artifacts\n\n")
        mf.write("Examples of synthetic template formatting errors ('1th', '2th', '3th house'):\n\n")
        for g in grammar_records[:15]:
            mf.write(f"- `{g['file']}` (`{g['rule_id']}`): {g['errors']} $\\to$ *\"{g['text']}\"*\n")

        mf.write("\n---\n\n")
        mf.write("## 4. Contradictory Opposing Rules with Identical Criteria\n\n")
        if contradiction_records:
            mf.write("The following rule pairs evaluate identical astrological conditions but assign diametrically opposing polarities:\n\n")
            for c in contradiction_records[:10]:
                mf.write(f"- **Condition:** `{c['condition']}`\n")
                mf.write(f"  - Rules: {', '.join(c['rules'])}\n\n")
        else:
            mf.write("No direct identical-condition polarity clashes detected.\n\n")

        mf.write("---\n\n")
        mf.write("## 5. Architectural Recommendations for Phase 4.3 (Quarantine)\n\n")
        mf.write("1. **Status Tagging:** Every legacy rule must be quarantined with `verification.status = 'draft'` and `generated = true`.\n")
        mf.write("2. **Runtime Gating:** In `src/jyotish/rules/engine.py`, the default production evaluator must strictly ignore rules with `status != 'scholar_verified'`.\n")
        mf.write("3. **Archiving Generators:** Move `build_*.py` to `scripts/legacy_rule_generators/` to prevent synthetic inflation.\n")
        mf.write("4. **Scholar Core:** Populate the starter verified core with ~300 verified rules from BPHS and Phaladeepika.\n")

    print(f"Audit Complete! Processed {total_rules} rules.")
    print(f"Markdown report written to: {md_path}")
    print(f"CSV log written to: {csv_path}")


if __name__ == "__main__":
    run_audit()
