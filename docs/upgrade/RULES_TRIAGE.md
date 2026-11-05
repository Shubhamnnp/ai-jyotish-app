# JyotishOS — Shastriya Rule Library Triage & Verification Report

**Reference:** Implementation PRD Section 4.1 & Master Upgrade Phase U1 (Task U1-T4)
**Total Rules Audited:** 12,506

## 1. Summary Distribution across Verification Tiers

| Verification Tier | Count | Percentage | Description / Policy |
| :--- | :---: | :---: | :--- |
| `scholar_verified` | **0** | 0.0% | Formally validated by credentialed Vedic scholar (strictly 0, never auto-promoted) |
| `machine_checked` | **3,595** | 28.7% | Passed all lint checks, unique criteria, evaluable condition (Approved for production runtime) |
| `draft` | **576** | 4.6% | Unverified template clusters, awaiting grantha chapter/verse alignment |
| `quarantined` | **8,335** | 66.6% | Conflicting polarities, name/condition mismatch, or ordinal grammar bugs (Hidden from public UI) |
| `rejected` | **0** | 0.0% | Structurally corrupted / unparseable |
| **Total Corpus** | **12,506** | **100.0%** | **Zero deletion policy maintained** |

## 2. Grantha-Wise Distribution Breakdown

| Grantha JSON File | Total | Machine Checked | Draft | Quarantined | Rejected |
| :--- | :---: | :---: | :---: | :---: | :---: |
| `bphs_rules.json` | 2,060 | 307 | 28 | 1,725 | 0 |
| `brihat_jataka_rules.json` | 1,005 | 328 | 0 | 677 | 0 |
| `classic_misc_rules.json` | 658 | 538 | 0 | 120 | 0 |
| `jaimini_rules.json` | 415 | 7 | 0 | 408 | 0 |
| `kp_rules.json` | 1,300 | 351 | 0 | 949 | 0 |
| `lalkitab_rules.json` | 1,224 | 86 | 0 | 1,138 | 0 |
| `muhurtha_rules.json` | 505 | 10 | 0 | 495 | 0 |
| `nadi_rules.json` | 1,128 | 528 | 540 | 60 | 0 |
| `numerology_rules.json` | 213 | 5 | 0 | 208 | 0 |
| `phaladeepika_rules.json` | 552 | 87 | 0 | 465 | 0 |
| `prashna_rules.json` | 498 | 175 | 0 | 323 | 0 |
| `samhita_rules.json` | 956 | 24 | 0 | 932 | 0 |
| `saravali_rules.json` | 1,655 | 976 | 0 | 679 | 0 |
| `sarvatobhadra_rules.json` | 229 | 173 | 8 | 48 | 0 |
| `tajika_rules.json` | 108 | 0 | 0 | 108 | 0 |

## 3. Operational Policy for Customer Phaladesh & AI Evidence Pack

1. **Public Engine Execution:** Customer-facing kundali reports, event analysis, and AI Evidence Packs evaluate **ONLY** `scholar_verified` and `machine_checked` rules.
2. **Rules Lab Access:** All `draft` and `quarantined` rules remain 100% accessible in the internal **Rules Lab** view with clear warning badges for editorial audit.
3. **Zero Deletion:** Not a single rule file or record was deleted.
