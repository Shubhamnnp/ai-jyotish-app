# JyotishOS — Legacy Rule Library Audit & Linter Report

**Audit Date:** November 4, 2026  
**Total Rule Files Scanned:** 15  
**Total Rules in Library:** 12,506  
**Identified Generator Artifacts (`generated: true`):** 2,114 (16.9%)  
**Name/Condition Mismatches:** 243  
**Ordinal Grammar Errors:** 99  
**Missing Chapter/Verse Citations:** 0  
**Contradictory Opposing Polarity Pairs:** 306  

---

## 1. Inventory by Grantha / File

| Grantha File | Total Rules | Generated (%) | Grammar Errors | Mismatches | Missing Sources |
| :--- | :---: | :---: | :---: | :---: | :---: |
| `bphs_rules.json` | 2,060 | 2,060 (100%) | 99 | 103 | 0 |
| `brihat_jataka_rules.json` | 1,005 | 0 (0%) | 0 | 1 | 0 |
| `classic_misc_rules.json` | 658 | 0 (0%) | 0 | 0 | 0 |
| `jaimini_rules.json` | 415 | 0 (0%) | 0 | 0 | 0 |
| `kp_rules.json` | 1,300 | 0 (0%) | 0 | 0 | 0 |
| `lalkitab_rules.json` | 1,224 | 0 (0%) | 0 | 0 | 0 |
| `muhurtha_rules.json` | 505 | 0 (0%) | 0 | 6 | 0 |
| `nadi_rules.json` | 1,128 | 0 (0%) | 0 | 0 | 0 |
| `numerology_rules.json` | 213 | 0 (0%) | 0 | 1 | 0 |
| `phaladeepika_rules.json` | 552 | 0 (0%) | 0 | 36 | 0 |
| `prashna_rules.json` | 498 | 0 (0%) | 0 | 0 | 0 |
| `samhita_rules.json` | 956 | 54 (6%) | 0 | 96 | 0 |
| `saravali_rules.json` | 1,655 | 0 (0%) | 0 | 0 | 0 |
| `sarvatobhadra_rules.json` | 229 | 0 (0%) | 0 | 0 | 0 |
| `tajika_rules.json` | 108 | 0 (0%) | 0 | 0 | 0 |

---

## 2. Top 30 Name vs. Condition Mismatches

The following rules display severe discordance between what the title states and what the engine actually evaluates:

| File | Rule ID | Title Mention | Mismatch Analysis |
| :--- | :--- | :--- | :--- |
| `bphs_rules.json` | `BPHS_BUDHADITYA_YOGA` | Budhaditya Yoga | Planet mismatch: Title mentions ['Mercury'] but condition checks ['Sun'] |
| `bphs_rules.json` | `BPHS_NAK_1_ASHWINI_PADA_1` | BPHS Nakshatra Ashwini Pada 1 | Planet mismatch: Title mentions ['Ketu'] but condition checks ['Moon'] |
| `bphs_rules.json` | `BPHS_NAK_1_ASHWINI_PADA_2` | BPHS Nakshatra Ashwini Pada 2 | Planet mismatch: Title mentions ['Ketu'] but condition checks ['Moon'] |
| `bphs_rules.json` | `BPHS_NAK_1_ASHWINI_PADA_3` | BPHS Nakshatra Ashwini Pada 3 | Planet mismatch: Title mentions ['Ketu'] but condition checks ['Moon'] |
| `bphs_rules.json` | `BPHS_NAK_1_ASHWINI_PADA_4` | BPHS Nakshatra Ashwini Pada 4 | Planet mismatch: Title mentions ['Ketu'] but condition checks ['Moon'] |
| `bphs_rules.json` | `BPHS_NAK_2_BHARANI_PADA_1` | BPHS Nakshatra Bharani Pada 1 | Planet mismatch: Title mentions ['Venus'] but condition checks ['Moon'] |
| `bphs_rules.json` | `BPHS_NAK_2_BHARANI_PADA_2` | BPHS Nakshatra Bharani Pada 2 | Planet mismatch: Title mentions ['Venus'] but condition checks ['Moon'] |
| `bphs_rules.json` | `BPHS_NAK_2_BHARANI_PADA_3` | BPHS Nakshatra Bharani Pada 3 | Planet mismatch: Title mentions ['Venus'] but condition checks ['Moon'] |
| `bphs_rules.json` | `BPHS_NAK_2_BHARANI_PADA_4` | BPHS Nakshatra Bharani Pada 4 | Planet mismatch: Title mentions ['Venus'] but condition checks ['Moon'] |
| `bphs_rules.json` | `BPHS_NAK_3_KRITTIKA_PADA_1` | BPHS Nakshatra Krittika Pada 1 | Planet mismatch: Title mentions ['Sun'] but condition checks ['Moon'] |
| `bphs_rules.json` | `BPHS_NAK_3_KRITTIKA_PADA_2` | BPHS Nakshatra Krittika Pada 2 | Planet mismatch: Title mentions ['Sun'] but condition checks ['Moon'] |
| `bphs_rules.json` | `BPHS_NAK_3_KRITTIKA_PADA_3` | BPHS Nakshatra Krittika Pada 3 | Planet mismatch: Title mentions ['Sun'] but condition checks ['Moon'] |
| `bphs_rules.json` | `BPHS_NAK_3_KRITTIKA_PADA_4` | BPHS Nakshatra Krittika Pada 4 | Planet mismatch: Title mentions ['Sun'] but condition checks ['Moon'] |
| `bphs_rules.json` | `BPHS_NAK_5_MRIGASHIRA_PADA_1` | BPHS Nakshatra Mrigashira Pada 1 | Planet mismatch: Title mentions ['Mars'] but condition checks ['Moon'] |
| `bphs_rules.json` | `BPHS_NAK_5_MRIGASHIRA_PADA_2` | BPHS Nakshatra Mrigashira Pada 2 | Planet mismatch: Title mentions ['Mars'] but condition checks ['Moon'] |
| `bphs_rules.json` | `BPHS_NAK_5_MRIGASHIRA_PADA_3` | BPHS Nakshatra Mrigashira Pada 3 | Planet mismatch: Title mentions ['Mars'] but condition checks ['Moon'] |
| `bphs_rules.json` | `BPHS_NAK_5_MRIGASHIRA_PADA_4` | BPHS Nakshatra Mrigashira Pada 4 | Planet mismatch: Title mentions ['Mars'] but condition checks ['Moon'] |
| `bphs_rules.json` | `BPHS_NAK_6_ARDRA_PADA_1` | BPHS Nakshatra Ardra Pada 1 | Planet mismatch: Title mentions ['Rahu'] but condition checks ['Moon'] |
| `bphs_rules.json` | `BPHS_NAK_6_ARDRA_PADA_2` | BPHS Nakshatra Ardra Pada 2 | Planet mismatch: Title mentions ['Rahu'] but condition checks ['Moon'] |
| `bphs_rules.json` | `BPHS_NAK_6_ARDRA_PADA_3` | BPHS Nakshatra Ardra Pada 3 | Planet mismatch: Title mentions ['Rahu'] but condition checks ['Moon'] |
| `bphs_rules.json` | `BPHS_NAK_6_ARDRA_PADA_4` | BPHS Nakshatra Ardra Pada 4 | Planet mismatch: Title mentions ['Rahu'] but condition checks ['Moon'] |
| `bphs_rules.json` | `BPHS_NAK_7_PUNARVASU_PADA_1` | BPHS Nakshatra Punarvasu Pada 1 | Planet mismatch: Title mentions ['Jupiter'] but condition checks ['Moon'] |
| `bphs_rules.json` | `BPHS_NAK_7_PUNARVASU_PADA_2` | BPHS Nakshatra Punarvasu Pada 2 | Planet mismatch: Title mentions ['Jupiter'] but condition checks ['Moon'] |
| `bphs_rules.json` | `BPHS_NAK_7_PUNARVASU_PADA_3` | BPHS Nakshatra Punarvasu Pada 3 | Planet mismatch: Title mentions ['Jupiter'] but condition checks ['Moon'] |
| `bphs_rules.json` | `BPHS_NAK_7_PUNARVASU_PADA_4` | BPHS Nakshatra Punarvasu Pada 4 | Planet mismatch: Title mentions ['Jupiter'] but condition checks ['Moon'] |
| `bphs_rules.json` | `BPHS_NAK_8_PUSHYA_PADA_1` | BPHS Nakshatra Pushya Pada 1 | Planet mismatch: Title mentions ['Saturn'] but condition checks ['Moon'] |
| `bphs_rules.json` | `BPHS_NAK_8_PUSHYA_PADA_2` | BPHS Nakshatra Pushya Pada 2 | Planet mismatch: Title mentions ['Saturn'] but condition checks ['Moon'] |
| `bphs_rules.json` | `BPHS_NAK_8_PUSHYA_PADA_3` | BPHS Nakshatra Pushya Pada 3 | Planet mismatch: Title mentions ['Saturn'] but condition checks ['Moon'] |
| `bphs_rules.json` | `BPHS_NAK_8_PUSHYA_PADA_4` | BPHS Nakshatra Pushya Pada 4 | Planet mismatch: Title mentions ['Saturn'] but condition checks ['Moon'] |
| `bphs_rules.json` | `BPHS_NAK_9_ASHLESHA_PADA_1` | BPHS Nakshatra Ashlesha Pada 1 | Planet mismatch: Title mentions ['Mercury'] but condition checks ['Moon'] |

---

## 3. Top Ordinal Grammar Artifacts

Examples of synthetic template formatting errors ('1th', '2th', '3th house'):

- `bphs_rules.json` (`BPHS_BHAVA_L1_H1`): 1th (should be 1st), 1th (should be 1st) $\to$ *"Lord of 1th house in 1th house"*
- `bphs_rules.json` (`BPHS_BHAVA_L1_H2`): 1th (should be 1st), 2th (should be 2nd) $\to$ *"Lord of 1th house in 2th house"*
- `bphs_rules.json` (`BPHS_BHAVA_L1_H3`): 1th (should be 1st), 3th (should be 3rd) $\to$ *"Lord of 1th house in 3th house"*
- `bphs_rules.json` (`BPHS_BHAVA_L1_H4`): 1th (should be 1st) $\to$ *"Lord of 1th house in 4th house"*
- `bphs_rules.json` (`BPHS_BHAVA_L1_H5`): 1th (should be 1st) $\to$ *"Lord of 1th house in 5th house"*
- `bphs_rules.json` (`BPHS_BHAVA_L1_H6`): 1th (should be 1st) $\to$ *"Lord of 1th house in 6th house"*
- `bphs_rules.json` (`BPHS_BHAVA_L1_H7`): 1th (should be 1st) $\to$ *"Lord of 1th house in 7th house"*
- `bphs_rules.json` (`BPHS_BHAVA_L1_H8`): 1th (should be 1st) $\to$ *"Lord of 1th house in 8th house"*
- `bphs_rules.json` (`BPHS_BHAVA_L1_H9`): 1th (should be 1st) $\to$ *"Lord of 1th house in 9th house"*
- `bphs_rules.json` (`BPHS_BHAVA_L1_H10`): 1th (should be 1st) $\to$ *"Lord of 1th house in 10th house"*
- `bphs_rules.json` (`BPHS_BHAVA_L1_H11`): 1th (should be 1st) $\to$ *"Lord of 1th house in 11th house"*
- `bphs_rules.json` (`BPHS_BHAVA_L1_H12`): 1th (should be 1st) $\to$ *"Lord of 1th house in 12th house"*
- `bphs_rules.json` (`BPHS_BHAVA_L2_H1`): 2th (should be 2nd), 1th (should be 1st) $\to$ *"Lord of 2th house in 1th house"*
- `bphs_rules.json` (`BPHS_BHAVA_L2_H2`): 2th (should be 2nd), 2th (should be 2nd) $\to$ *"Lord of 2th house in 2th house"*
- `bphs_rules.json` (`BPHS_BHAVA_L2_H3`): 2th (should be 2nd), 3th (should be 3rd) $\to$ *"Lord of 2th house in 3th house"*

---

## 4. Contradictory Opposing Rules with Identical Criteria

The following rule pairs evaluate identical astrological conditions but assign diametrically opposing polarities:

- **Condition:** `ALL:{"entity": "Lord_1", "house": 1}`
  - Rules: bphs_rules.json:BPHS_BHAVA_L1_H1 (+), bphs_rules.json:BPHS_YOGINI_MANGALA_H1 (+), bphs_rules.json:BPHS_YOGINI_PINGALA_H1 (-), bphs_rules.json:BPHS_YOGINI_DHANYA_H1 (+), bphs_rules.json:BPHS_YOGINI_BHRAMARI_H1 (+), bphs_rules.json:BPHS_YOGINI_BHADRIKA_H1 (+), bphs_rules.json:BPHS_YOGINI_ULKA_H1 (-), bphs_rules.json:BPHS_YOGINI_SIDDHA_H1 (+), bphs_rules.json:BPHS_YOGINI_SANKATA_H1 (-), bphs_rules.json:BPHS_SUDARSHANA_लग्न_H1_SHUBHA (+), bphs_rules.json:BPHS_SUDARSHANA_लग्न_H1_ASHUBHA (-), brihat_jataka_rules.json:BJ_BLORD_L1_IN_H1 (+), phaladeepika_rules.json:PD_BHAVA_LORD_L1_H1 (+), tajika_rules.json:TAJIKA_MUNTHAHA_H1 (+)

- **Condition:** `ALL:{"entity": "Lord_1", "house": 2}`
  - Rules: bphs_rules.json:BPHS_BHAVA_L1_H2 (+), bphs_rules.json:BPHS_YOGINI_MANGALA_H2 (+), bphs_rules.json:BPHS_YOGINI_PINGALA_H2 (-), bphs_rules.json:BPHS_YOGINI_DHANYA_H2 (+), bphs_rules.json:BPHS_YOGINI_BHRAMARI_H2 (+), bphs_rules.json:BPHS_YOGINI_BHADRIKA_H2 (+), bphs_rules.json:BPHS_YOGINI_ULKA_H2 (-), bphs_rules.json:BPHS_YOGINI_SIDDHA_H2 (+), bphs_rules.json:BPHS_YOGINI_SANKATA_H2 (-), bphs_rules.json:BPHS_SUDARSHANA_लग्न_H2_SHUBHA (+), bphs_rules.json:BPHS_SUDARSHANA_लग्न_H2_ASHUBHA (-), brihat_jataka_rules.json:BJ_BLORD_L1_IN_H2 (+), phaladeepika_rules.json:PD_BHAVA_LORD_L1_H2 (+), tajika_rules.json:TAJIKA_MUNTHAHA_H2 (+)

- **Condition:** `ALL:{"entity": "Lord_1", "house": 3}`
  - Rules: bphs_rules.json:BPHS_BHAVA_L1_H3 (+), bphs_rules.json:BPHS_YOGINI_MANGALA_H3 (+), bphs_rules.json:BPHS_YOGINI_PINGALA_H3 (-), bphs_rules.json:BPHS_YOGINI_DHANYA_H3 (+), bphs_rules.json:BPHS_YOGINI_BHRAMARI_H3 (+), bphs_rules.json:BPHS_YOGINI_BHADRIKA_H3 (+), bphs_rules.json:BPHS_YOGINI_ULKA_H3 (-), bphs_rules.json:BPHS_YOGINI_SIDDHA_H3 (+), bphs_rules.json:BPHS_YOGINI_SANKATA_H3 (-), bphs_rules.json:BPHS_SUDARSHANA_लग्न_H3_SHUBHA (+), bphs_rules.json:BPHS_SUDARSHANA_लग्न_H3_ASHUBHA (-), brihat_jataka_rules.json:BJ_BLORD_L1_IN_H3 (+), phaladeepika_rules.json:PD_BHAVA_LORD_L1_H3 (-), tajika_rules.json:TAJIKA_MUNTHAHA_H3 (+)

- **Condition:** `ALL:{"entity": "Lord_1", "house": 4}`
  - Rules: bphs_rules.json:BPHS_BHAVA_L1_H4 (+), bphs_rules.json:BPHS_YOGINI_MANGALA_H4 (+), bphs_rules.json:BPHS_YOGINI_PINGALA_H4 (-), bphs_rules.json:BPHS_YOGINI_DHANYA_H4 (+), bphs_rules.json:BPHS_YOGINI_BHRAMARI_H4 (+), bphs_rules.json:BPHS_YOGINI_BHADRIKA_H4 (+), bphs_rules.json:BPHS_YOGINI_ULKA_H4 (-), bphs_rules.json:BPHS_YOGINI_SIDDHA_H4 (+), bphs_rules.json:BPHS_YOGINI_SANKATA_H4 (-), bphs_rules.json:BPHS_SUDARSHANA_लग्न_H4_SHUBHA (+), bphs_rules.json:BPHS_SUDARSHANA_लग्न_H4_ASHUBHA (-), brihat_jataka_rules.json:BJ_BLORD_L1_IN_H4 (+), phaladeepika_rules.json:PD_BHAVA_LORD_L1_H4 (+), tajika_rules.json:TAJIKA_MUNTHAHA_H4 (+)

- **Condition:** `ALL:{"entity": "Lord_1", "house": 5}`
  - Rules: bphs_rules.json:BPHS_BHAVA_L1_H5 (+), bphs_rules.json:BPHS_YOGINI_MANGALA_H5 (+), bphs_rules.json:BPHS_YOGINI_PINGALA_H5 (-), bphs_rules.json:BPHS_YOGINI_DHANYA_H5 (+), bphs_rules.json:BPHS_YOGINI_BHRAMARI_H5 (+), bphs_rules.json:BPHS_YOGINI_BHADRIKA_H5 (+), bphs_rules.json:BPHS_YOGINI_ULKA_H5 (-), bphs_rules.json:BPHS_YOGINI_SIDDHA_H5 (+), bphs_rules.json:BPHS_YOGINI_SANKATA_H5 (-), bphs_rules.json:BPHS_SUDARSHANA_लग्न_H5_SHUBHA (+), bphs_rules.json:BPHS_SUDARSHANA_लग्न_H5_ASHUBHA (-), brihat_jataka_rules.json:BJ_BLORD_L1_IN_H5 (+), phaladeepika_rules.json:PD_BHAVA_LORD_L1_H5 (+), tajika_rules.json:TAJIKA_MUNTHAHA_H5 (+)

- **Condition:** `ALL:{"entity": "Lord_1", "house": 6}`
  - Rules: bphs_rules.json:BPHS_BHAVA_L1_H6 (-), bphs_rules.json:BPHS_YOGINI_MANGALA_H6 (+), bphs_rules.json:BPHS_YOGINI_PINGALA_H6 (-), bphs_rules.json:BPHS_YOGINI_DHANYA_H6 (+), bphs_rules.json:BPHS_YOGINI_BHRAMARI_H6 (+), bphs_rules.json:BPHS_YOGINI_BHADRIKA_H6 (+), bphs_rules.json:BPHS_YOGINI_ULKA_H6 (-), bphs_rules.json:BPHS_YOGINI_SIDDHA_H6 (+), bphs_rules.json:BPHS_YOGINI_SANKATA_H6 (-), bphs_rules.json:BPHS_SUDARSHANA_लग्न_H6_SHUBHA (+), bphs_rules.json:BPHS_SUDARSHANA_लग्न_H6_ASHUBHA (-), brihat_jataka_rules.json:BJ_BLORD_L1_IN_H6 (-), phaladeepika_rules.json:PD_BHAVA_LORD_L1_H6 (-), tajika_rules.json:TAJIKA_MUNTHAHA_H6 (-)

- **Condition:** `ALL:{"entity": "Lord_1", "house": 7}`
  - Rules: bphs_rules.json:BPHS_BHAVA_L1_H7 (+), bphs_rules.json:BPHS_YOGINI_MANGALA_H7 (+), bphs_rules.json:BPHS_YOGINI_PINGALA_H7 (-), bphs_rules.json:BPHS_YOGINI_DHANYA_H7 (+), bphs_rules.json:BPHS_YOGINI_BHRAMARI_H7 (+), bphs_rules.json:BPHS_YOGINI_BHADRIKA_H7 (+), bphs_rules.json:BPHS_YOGINI_ULKA_H7 (-), bphs_rules.json:BPHS_YOGINI_SIDDHA_H7 (+), bphs_rules.json:BPHS_YOGINI_SANKATA_H7 (-), bphs_rules.json:BPHS_SUDARSHANA_लग्न_H7_SHUBHA (+), bphs_rules.json:BPHS_SUDARSHANA_लग्न_H7_ASHUBHA (-), brihat_jataka_rules.json:BJ_BLORD_L1_IN_H7 (+), phaladeepika_rules.json:PD_BHAVA_LORD_L1_H7 (-), tajika_rules.json:TAJIKA_MUNTHAHA_H7 (+)

- **Condition:** `ALL:{"entity": "Lord_1", "house": 8}`
  - Rules: bphs_rules.json:BPHS_BHAVA_L1_H8 (-), bphs_rules.json:BPHS_YOGINI_MANGALA_H8 (+), bphs_rules.json:BPHS_YOGINI_PINGALA_H8 (-), bphs_rules.json:BPHS_YOGINI_DHANYA_H8 (+), bphs_rules.json:BPHS_YOGINI_BHRAMARI_H8 (+), bphs_rules.json:BPHS_YOGINI_BHADRIKA_H8 (+), bphs_rules.json:BPHS_YOGINI_ULKA_H8 (-), bphs_rules.json:BPHS_YOGINI_SIDDHA_H8 (+), bphs_rules.json:BPHS_YOGINI_SANKATA_H8 (-), bphs_rules.json:BPHS_SUDARSHANA_लग्न_H8_SHUBHA (+), bphs_rules.json:BPHS_SUDARSHANA_लग्न_H8_ASHUBHA (-), brihat_jataka_rules.json:BJ_BLORD_L1_IN_H8 (-), phaladeepika_rules.json:PD_BHAVA_LORD_L1_H8 (-), tajika_rules.json:TAJIKA_MUNTHAHA_H8 (-)

- **Condition:** `ALL:{"entity": "Lord_1", "house": 9}`
  - Rules: bphs_rules.json:BPHS_BHAVA_L1_H9 (+), bphs_rules.json:BPHS_YOGINI_MANGALA_H9 (+), bphs_rules.json:BPHS_YOGINI_PINGALA_H9 (-), bphs_rules.json:BPHS_YOGINI_DHANYA_H9 (+), bphs_rules.json:BPHS_YOGINI_BHRAMARI_H9 (+), bphs_rules.json:BPHS_YOGINI_BHADRIKA_H9 (+), bphs_rules.json:BPHS_YOGINI_ULKA_H9 (-), bphs_rules.json:BPHS_YOGINI_SIDDHA_H9 (+), bphs_rules.json:BPHS_YOGINI_SANKATA_H9 (-), bphs_rules.json:BPHS_SUDARSHANA_लग्न_H9_SHUBHA (+), bphs_rules.json:BPHS_SUDARSHANA_लग्न_H9_ASHUBHA (-), brihat_jataka_rules.json:BJ_BLORD_L1_IN_H9 (+), phaladeepika_rules.json:PD_BHAVA_LORD_L1_H9 (+), tajika_rules.json:TAJIKA_MUNTHAHA_H9 (+)

- **Condition:** `ALL:{"entity": "Lord_1", "house": 10}`
  - Rules: bphs_rules.json:BPHS_BHAVA_L1_H10 (+), bphs_rules.json:BPHS_YOGINI_MANGALA_H10 (+), bphs_rules.json:BPHS_YOGINI_PINGALA_H10 (-), bphs_rules.json:BPHS_YOGINI_DHANYA_H10 (+), bphs_rules.json:BPHS_YOGINI_BHRAMARI_H10 (+), bphs_rules.json:BPHS_YOGINI_BHADRIKA_H10 (+), bphs_rules.json:BPHS_YOGINI_ULKA_H10 (-), bphs_rules.json:BPHS_YOGINI_SIDDHA_H10 (+), bphs_rules.json:BPHS_YOGINI_SANKATA_H10 (-), bphs_rules.json:BPHS_SUDARSHANA_लग्न_H10_SHUBHA (+), bphs_rules.json:BPHS_SUDARSHANA_लग्न_H10_ASHUBHA (-), brihat_jataka_rules.json:BJ_BLORD_L1_IN_H10 (+), phaladeepika_rules.json:PD_BHAVA_LORD_L1_H10 (+), tajika_rules.json:TAJIKA_MUNTHAHA_H10 (+)

---

## 5. Architectural Recommendations for Phase 4.3 (Quarantine)

1. **Status Tagging:** Every legacy rule must be quarantined with `verification.status = 'draft'` and `generated = true`.
2. **Runtime Gating:** In `src/jyotish/rules/engine.py`, the default production evaluator must strictly ignore rules with `status != 'scholar_verified'`.
3. **Archiving Generators:** Move `build_*.py` to `scripts/legacy_rule_generators/` to prevent synthetic inflation.
4. **Scholar Core:** Populate the starter verified core with ~300 verified rules from BPHS and Phaladeepika.
