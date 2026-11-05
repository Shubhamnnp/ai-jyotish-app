#!/usr/bin/env python3
"""
JyotishOS Deterministic Rule Linter (Phase U1, Task U1-T1).
Reference: Master Upgrade Protocol Phase U1.

Performs read-only astronomical & linguistic audits on all 12,506 classical rules:
1. Ordinal Grammar Check ('1th', '2th', '3th', etc.).
2. Name vs Condition Consistency (house numbers & planetary entities).
3. Contradictory Polarity Pairs (identical criteria evaluated with opposite +/- effects).
4. Citation & Source Validity (missing text, missing chapter, 'Sloka 0').
5. Generated / Template Markings ('generated: true').
6. Identical Description Clusters (verbatim repeated translations).

Outputs:
- CSV: docs/upgrade/rules_lint_issues.csv
- Markdown: docs/upgrade/RULES_LINT_REPORT.md
Zero file modifications to data or rules files (strictly read-only).
"""

import os
import sys
import json
import csv
import re
from collections import Counter, defaultdict
from typing import Dict, List, Any, Tuple

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
RULES_DIR = os.path.join(REPO_ROOT, "src", "jyotish", "rules", "grantha_rules")
OUT_DIR = os.path.join(REPO_ROOT, "docs", "upgrade")

PLANETS = ["sun", "moon", "mars", "mercury", "jupiter", "venus", "saturn", "rahu", "ketu"]


def lint_all_rules():
    os.makedirs(OUT_DIR, exist_ok=True)
    rule_files = sorted([os.path.join(RULES_DIR, f) for f in os.listdir(RULES_DIR) if f.endswith(".json")])

    total_rules = 0
    all_issues = []
    grantha_stats = defaultdict(lambda: {"total": 0, "issues": 0})
    issue_type_counts = Counter()

    desc_map = defaultdict(list)
    condition_map = defaultdict(list)

    # 1. First Pass: Single-Rule Linting
    for f_path in rule_files:
        with open(f_path, "r", encoding="utf-8") as fp:
            d = json.load(fp)

        rules = d.get("rules", []) if isinstance(d, dict) else d
        grantha_name = d.get("metadata", {}).get("grantha", os.path.basename(f_path)) if isinstance(d, dict) else os.path.basename(f_path)

        for r in rules:
            total_rules += 1
            grantha_stats[grantha_name]["total"] += 1
            rule_id = r.get("rule_id", "UNKNOWN")
            rname_en = r.get("rule_name_en", "")
            rname_hi = r.get("rule_name_hi", "")
            school = r.get("school", "Parashari")
            cond = r.get("condition", {})
            criteria = cond.get("criteria", [])
            src = r.get("source", {})
            eff = r.get("effect", {})
            desc_hi = eff.get("description_hi", "").strip()
            polarity = eff.get("polarity", "")

            # A. Ordinal Grammar Check
            bad_ordinal = re.search(r'\b(1th|2th|3th|21th|22th|23th|31th)\b', rname_en, re.IGNORECASE)
            if bad_ordinal:
                issue_type_counts["ORDINAL_GRAMMAR"] += 1
                grantha_stats[grantha_name]["issues"] += 1
                all_issues.append({
                    "rule_id": rule_id,
                    "grantha": grantha_name,
                    "school": school,
                    "issue_type": "ORDINAL_GRAMMAR",
                    "severity": "LOW",
                    "details": f"Incorrect ordinal suffix '{bad_ordinal.group(0)}' in rule_name_en",
                    "name_en": rname_en,
                    "condition_summary": str(criteria)
                })

            # B. Citation / Source Check
            chap = str(src.get("chapter", "")).strip()
            txt = str(src.get("text", "")).strip()
            if not txt or not chap or chap == "Unknown" or "Sloka 0" in chap:
                issue_type_counts["CITATION_ANOMALY"] += 1
                grantha_stats[grantha_name]["issues"] += 1
                all_issues.append({
                    "rule_id": rule_id,
                    "grantha": grantha_name,
                    "school": school,
                    "issue_type": "CITATION_ANOMALY",
                    "severity": "MEDIUM",
                    "details": f"Missing or placeholder citation (text='{txt}', chapter='{chap}')",
                    "name_en": rname_en,
                    "condition_summary": str(criteria)
                })

            # C. Generated Template Flag Check
            if r.get("generated") is True or "generated" in str(r.get("tags", [])):
                issue_type_counts["GENERATED_FLAG"] += 1
                grantha_stats[grantha_name]["issues"] += 1
                all_issues.append({
                    "rule_id": rule_id,
                    "grantha": grantha_name,
                    "school": school,
                    "issue_type": "GENERATED_FLAG",
                    "severity": "HIGH",
                    "details": "Explicit 'generated: true' flag detected",
                    "name_en": rname_en,
                    "condition_summary": str(criteria)
                })

            # D. Name vs Condition Consistency Check
            # House mismatch
            h_matches = re.findall(r'in\s+(\d+)(?:st|nd|rd|th)\s+house', rname_en, re.IGNORECASE)
            if h_matches:
                expected_h = int(h_matches[-1])
                crit_houses = [c.get("house") for c in criteria if c.get("house") is not None]
                if crit_houses and expected_h not in crit_houses:
                    issue_type_counts["NAME_CONDITION_MISMATCH"] += 1
                    grantha_stats[grantha_name]["issues"] += 1
                    all_issues.append({
                        "rule_id": rule_id,
                        "grantha": grantha_name,
                        "school": school,
                        "issue_type": "NAME_CONDITION_MISMATCH",
                        "severity": "HIGH",
                        "details": f"Name mentions house {expected_h}, but condition criteria specifies house {crit_houses}",
                        "name_en": rname_en,
                        "condition_summary": str(criteria)
                    })

            # Planet entity mismatch
            for p in PLANETS:
                if f" {p} " in f" {rname_en.lower()} ":
                    crit_entities = [str(c.get("entity", "")).lower() for c in criteria]
                    if crit_entities and not any(p in ce for ce in crit_entities) and not any(ce.startswith("lord") for ce in crit_entities):
                        issue_type_counts["NAME_CONDITION_MISMATCH"] += 1
                        grantha_stats[grantha_name]["issues"] += 1
                        all_issues.append({
                            "rule_id": rule_id,
                            "grantha": grantha_name,
                            "school": school,
                            "issue_type": "NAME_CONDITION_MISMATCH",
                            "severity": "HIGH",
                            "details": f"Name mentions planet {p.capitalize()}, but condition criteria has {crit_entities}",
                            "name_en": rname_en,
                            "condition_summary": str(criteria)
                        })

            # Track description for clustering
            if desc_hi:
                desc_map[(grantha_name, desc_hi)].append(rule_id)

            # Track criteria for contradictory polarity
            crit_key = json.dumps(sorted([tuple(sorted((k, str(v)) for k, v in c.items())) for c in criteria]))
            condition_map[crit_key].append((rule_id, grantha_name, school, polarity, rname_en, str(criteria)))

    # 2. Second Pass: Cross-Rule Contradictions & Clusters
    for ckey, items in condition_map.items():
        if len(items) > 1:
            polarities = set(x[3] for x in items if x[3] in ("+", "-"))
            if "+" in polarities and "-" in polarities:
                issue_type_counts["CONTRADICTORY_POLARITY"] += len(items)
                rule_ids = [x[0] for x in items]
                for x in items:
                    grantha_stats[x[1]]["issues"] += 1
                    all_issues.append({
                        "rule_id": x[0],
                        "grantha": x[1],
                        "school": x[2],
                        "issue_type": "CONTRADICTORY_POLARITY",
                        "severity": "CRITICAL",
                        "details": f"Opposite +/- polarities for identical criteria with peer rules: {rule_ids}",
                        "name_en": x[4],
                        "condition_summary": x[5]
                    })

    for (g_name, d_text), r_ids in desc_map.items():
        if len(r_ids) > 10:
            issue_type_counts["IDENTICAL_DESC_CLUSTER"] += len(r_ids)
            grantha_stats[g_name]["issues"] += len(r_ids)
            for rid in r_ids:
                all_issues.append({
                    "rule_id": rid,
                    "grantha": g_name,
                    "school": "Parashari",
                    "issue_type": "IDENTICAL_DESC_CLUSTER",
                    "severity": "MEDIUM",
                    "details": f"Template cluster of {len(r_ids)} rules sharing identical text: '{d_text[:50]}...'",
                    "name_en": "",
                    "condition_summary": ""
                })

    # 3. Write CSV Output
    csv_file = os.path.join(OUT_DIR, "rules_lint_issues.csv")
    with open(csv_file, "w", encoding="utf-8", newline="") as fp:
        writer = csv.DictWriter(
            fp,
            fieldnames=["rule_id", "grantha", "school", "issue_type", "severity", "details", "name_en", "condition_summary"]
        )
        writer.writeheader()
        writer.writerows(all_issues)

    # 4. Write Markdown Report
    md_file = os.path.join(OUT_DIR, "RULES_LINT_REPORT.md")
    with open(md_file, "w", encoding="utf-8") as fp:
        fp.write("# JyotishOS — Classical Rules Lint & Quality Audit Report (U1-T1)\n\n")
        fp.write(f"**Audit Timestamp:** 2026-11-05T11:00:00Z  \n")
        fp.write(f"**Total Rules Audited:** {total_rules:,} across {len(rule_files)} Granthas  \n")
        fp.write(f"**Total Quality Flags:** {len(all_issues):,}  \n\n")

        fp.write("## 1. Quality Issues Breakdown by Type\n\n")
        fp.write("| Issue Type | Severity | Count | Impact |\n")
        fp.write("| :--- | :---: | :---: | :--- |\n")
        fp.write(f"| **CONTRADICTORY_POLARITY** | `CRITICAL` | {issue_type_counts['CONTRADICTORY_POLARITY']:,} | Identical astronomical criteria producing conflicting +/- outcomes |\n")
        fp.write(f"| **NAME_CONDITION_MISMATCH** | `HIGH` | {issue_type_counts['NAME_CONDITION_MISMATCH']:,} | Title refers to different planet or house than evaluated condition |\n")
        fp.write(f"| **GENERATED_FLAG** | `HIGH` | {issue_type_counts['GENERATED_FLAG']:,} | Rules marked as synthetic templates requiring quarantine |\n")
        fp.write(f"| **IDENTICAL_DESC_CLUSTER** | `MEDIUM` | {issue_type_counts['IDENTICAL_DESC_CLUSTER']:,} | Large clusters of rules sharing verbatim identical description |\n")
        fp.write(f"| **CITATION_ANOMALY** | `MEDIUM` | {issue_type_counts['CITATION_ANOMALY']:,} | Missing, generic, or Sloka 0 placeholder citations |\n")
        fp.write(f"| **ORDINAL_GRAMMAR** | `LOW` | {issue_type_counts['ORDINAL_GRAMMAR']:,} | Linguistic errors in English naming ('1th', '2th', '3th') |\n\n")

        fp.write("## 2. Grantha-by-Grantha Audit Statistics\n\n")
        fp.write("| Grantha / Source | Total Rules | Quality Flags | Flagged % |\n")
        fp.write("| :--- | :---: | :---: | :---: |\n")
        for g, st in sorted(grantha_stats.items(), key=lambda x: x[1]["total"], reverse=True):
            pct = (st["issues"] / st["total"] * 100) if st["total"] > 0 else 0
            fp.write(f"| **{g}** | {st['total']:,} | {st['issues']:,} | {pct:.1f}% |\n")

        fp.write("\n## 3. Top Contradictory Rule Pairs (Sample)\n\n")
        fp.write("The following rule pairs evaluate identical astronomical configurations with opposing polarities and must be quarantined until scholar review:\n\n")
        contradictions = [i for i in all_issues if i["issue_type"] == "CONTRADICTORY_POLARITY"]
        for c in contradictions[:10]:
            fp.write(f"- **{c['rule_id']}** ({c['grantha']}): {c['details']} | Condition: `{c['condition_summary']}`\n")

        fp.write(f"\n*Full machine-readable issue database saved to: `docs/upgrade/rules_lint_issues.csv`*\n")

    print(f"Linter finished: {total_rules} rules checked, {len(all_issues)} issues found.")
    print(f"Generated {csv_file}")
    print(f"Generated {md_file}")
    return total_rules, len(all_issues)


if __name__ == "__main__":
    lint_all_rules()

