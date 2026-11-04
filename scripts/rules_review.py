"""
Shastriya Rules Review & Verification CLI Tool (Phase 4 Task 5 & Task 6).
Facilitates editorial review and verification of classical Jyotish rules:
- Renders rule conditions and citations in plain language (Hindi & English).
- Generates scholar review worksheets in Markdown.
- Allows scholars/editors to verify, edit, or reject quarantined draft rules.
- Tracks verification progress in docs/RULES_PROGRESS.md.
"""

import sys
import os
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

sys.path.insert(0, os.path.abspath("."))

import json
import argparse

from src.jyotish.rules.schema_v2 import RuleV2
from src.jyotish.rules.quarantine import is_generated_rule, get_quarantine_stats

RULE_DIR = Path("src/jyotish/rules/grantha_rules")
PROGRESS_FILE = Path("docs/RULES_PROGRESS.md")


def render_condition_plain_text(condition: Dict[str, Any]) -> Tuple[str, str]:
    """Translates criteria dictionary into human-readable English and Hindi summaries."""
    if not condition or not isinstance(condition, dict):
        return "No condition criteria defined", "कोई शर्त निर्धारित नहीं"

    crit_list = condition.get("criteria", [])
    if not crit_list:
        return "Unconditional", "शर्त-रहित"

    en_parts = []
    hi_parts = []
    for c in crit_list:
        if not isinstance(c, dict):
            continue
        ent = c.get("entity") or c.get("planet") or c.get("fact", "Entity")
        house = c.get("house") or c.get("placed_in_house")
        sign = c.get("sign") or c.get("sign_name")
        dignity = c.get("dignity")

        en = f"{ent}"
        hi = f"{ent}"
        if house:
            en += f" in House {house}"
            hi += f" {house}वें भाव में"
        if sign:
            en += f" in {sign}"
            hi += f" {sign} राशि में"
        if dignity:
            en += f" ({dignity})"
            hi += f" ({dignity})"
        en_parts.append(en)
        hi_parts.append(hi)

    op = f" {condition.get('type', 'AND')} "
    return op.join(en_parts), " तथा ".join(hi_parts)


def cmd_stats():
    """Prints verification status breakdown across all grantha rule files."""
    files = sorted(list(RULE_DIR.glob("*.json")))
    print("=" * 80)
    print("JYOTISHOS SHASTRIYA RULES VERIFICATION AUDIT")
    print("=" * 80)
    print(f"{'Grantha File':<30} {'Total':<8} {'Verified':<10} {'Machine':<10} {'Draft':<8} {'Rejected':<8}")
    print("-" * 80)

    grand_total = 0
    grand_verified = 0
    grand_draft = 0

    for fpath in files:
        with open(fpath, "r", encoding="utf-8") as f:
            data = json.load(f)
        rules = data.get("rules", data) if isinstance(data, dict) else data
        stats = get_quarantine_stats(rules)
        grand_total += stats["total"]
        grand_verified += stats["scholar_verified"]
        grand_draft += stats["draft"]

        print(f"{fpath.name:<30} {stats['total']:<8} {stats['scholar_verified']:<10} {stats['machine_checked']:<10} {stats['draft']:<8} {stats['rejected']:<8}")

    print("-" * 80)
    print(f"{'GRAND TOTAL':<30} {grand_total:<8} {grand_verified:<10} {'-':<10} {grand_draft:<8} {'-':<8}")
    print("=" * 80)


def cmd_worksheet(filename: str, limit: int = 50, output_file: Optional[str] = None):
    """Generates a Markdown review worksheet for scholar verification."""
    fpath = RULE_DIR / filename
    if not fpath.exists():
        print(f"Error: {fpath} does not exist.")
        return

    with open(fpath, "r", encoding="utf-8") as f:
        data = json.load(f)
    rules = data.get("rules", data) if isinstance(data, dict) else data

    out_p = Path(output_file) if output_file else Path(f"docs/worksheet_{fpath.stem}.md")

    with open(out_p, "w", encoding="utf-8") as wf:
        wf.write(f"# Scholar Review Worksheet: {filename}\n\n")
        wf.write(f"**Instructions for Scholar:** Review the classical source citation, Sanskrit/Hindi meaning, and rule condition. Mark with [x] and sign.\n\n")

        for idx, r in enumerate(rules[:limit], 1):
            r_id = r.get("rule_id", f"RULE_{idx}")
            src = r.get("source", {})
            cond = r.get("condition", {})
            eff = r.get("effect", {})

            en_cond, hi_cond = render_condition_plain_text(cond)

            wf.write(f"### {idx}. Rule `{r_id}`: {r.get('rule_name_hi', '')} / {r.get('rule_name_en', '')}\n")
            wf.write(f"- **Source Citation:** {src.get('text', '')} | Chapter: {src.get('chapter', '')} | Verse: {src.get('verse', 'N/A')}\n")
            wf.write(f"- **Condition (Plain):** {en_cond} ({hi_cond})\n")
            wf.write(f"- **Polarity:** `{eff.get('polarity', '+')}` | **Domain:** `{eff.get('domain', r.get('category', 'general'))}`\n")
            wf.write(f"- **Classical Indication:** {eff.get('description_hi', eff.get('summary_hi', ''))}\n")
            wf.write(f"- **Scholar Action:** [ ] VERIFY  [ ] EDIT  [ ] REJECT\n")
            wf.write(f"- **Scholar Notes:** _________________________________________\n\n")
            wf.write("---\n\n")

    print(f"Worksheet written to: {out_p} ({min(limit, len(rules))} rules included)")


def update_rules_progress():
    """Generates docs/RULES_PROGRESS.md tracking classical core verification."""
    files = sorted(list(RULE_DIR.glob("*.json")))
    total_all = 0
    verified_all = 0
    draft_all = 0

    rows = []
    for fpath in files:
        with open(fpath, "r", encoding="utf-8") as f:
            data = json.load(f)
        rules = data.get("rules", data) if isinstance(data, dict) else data
        st = get_quarantine_stats(rules)
        total_all += st["total"]
        verified_all += st["scholar_verified"]
        draft_all += st["draft"]
        rows.append(f"| `{fpath.name}` | {st['total']:,} | {st['scholar_verified']} | {st['draft']:,} | {st['rejected']} |")

    PROGRESS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
        f.write("# JyotishOS — Classical Rules Verification Progress (Phase 4.6)\n\n")
        f.write(f"**Last Updated:** November 4, 2026  \n")
        f.write(f"**Total Rule Library:** {total_all:,}  \n")
        f.write(f"**Scholar Verified:** {verified_all}  \n")
        f.write(f"**Quarantined (Draft):** {draft_all:,}  \n")
        f.write(f"**Core Target (Phase 4.6):** 300–600 canonical rules for Parashari\n\n")
        f.write("---\n\n")
        f.write("## 1. Grantha Verification Ledger\n\n")
        f.write("| Grantha File | Total Rules | Scholar Verified | Quarantined Drafts | Rejected |\n")
        f.write("| :--- | :---: | :---: | :---: | :---: |\n")
        f.write("\n".join(rows))
        f.write("\n\n---\n\n")
        f.write("## 2. Priority Starter Core Roadmap (300–600 Canonical Rules)\n\n")
        f.write("1. **Bhava Lords in 12 Houses (144 Rules):** BPHS Ch. 24 (Lord of 1st in 1st..12th, Lord of 2nd in 1st..12th, ..., Lord of 12th in 1st..12th).\n")
        f.write("2. **9 Grahas in 12 Houses (108 Rules):** BPHS Ch. 23 & Phaladeepika Ch. 8 (Sun in 1st..12th, Moon in 1st..12th, ..., Ketu in 1st..12th).\n")
        f.write("3. **Major Classical Raja & Dhana Yogas (50 Rules):** BPHS Ch. 34–42 (Pancha Mahapurusha, Gajakesari, Dharma-Karmadhipati, Viparita Raja, Neechabhanga).\n")
        f.write("4. **Dasha-Lord Classical Significations (48 Rules):** BPHS Ch. 47 & Phaladeepika Ch. 19.\n\n")
        f.write("> [!IMPORTANT]\n")
        f.write("> The AI agent must never self-certify rules as `scholar_verified`. All verified tags are reserved for human scholars and domain experts reviewing via `scripts/rules_review.py`.\n")

    print(f"Progress report updated: {PROGRESS_FILE}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="JyotishOS Shastriya Rules Review Tool")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("stats", help="Show verification statistics across granthas")
    subparsers.add_parser("progress", help="Update docs/RULES_PROGRESS.md")

    ws = subparsers.add_parser("worksheet", help="Generate scholar review worksheet")
    ws.add_argument("--file", required=True, help="Grantha file name in grantha_rules/")
    ws.add_argument("--limit", type=int, default=50, help="Maximum rules to include in worksheet")
    ws.add_argument("--output", help="Output worksheet file path")

    args = parser.parse_args()
    if args.command == "stats":
        cmd_stats()
    elif args.command == "worksheet":
        cmd_worksheet(args.file, limit=args.limit, output_file=args.output)
    elif args.command == "progress":
        update_rules_progress()
    else:
        update_rules_progress()
        cmd_stats()
