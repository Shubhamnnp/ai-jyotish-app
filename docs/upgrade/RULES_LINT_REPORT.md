# JyotishOS — Classical Rules Lint & Quality Audit Report (U1-T1)

**Audit Timestamp:** 2026-11-05T11:00:00Z  
**Total Rules Audited:** 12,584 across 16 Granthas  
**Total Quality Flags:** 10,657  

## 1. Quality Issues Breakdown by Type

| Issue Type | Severity | Count | Impact |
| :--- | :---: | :---: | :--- |
| **CONTRADICTORY_POLARITY** | `CRITICAL` | 8,210 | Identical astronomical criteria producing conflicting +/- outcomes |
| **NAME_CONDITION_MISMATCH** | `HIGH` | 309 | Title refers to different planet or house than evaluated condition |
| **GENERATED_FLAG** | `HIGH` | 0 | Rules marked as synthetic templates requiring quarantine |
| **IDENTICAL_DESC_CLUSTER** | `MEDIUM` | 2,048 | Large clusters of rules sharing verbatim identical description |
| **CITATION_ANOMALY** | `MEDIUM` | 0 | Missing, generic, or Sloka 0 placeholder citations |
| **ORDINAL_GRAMMAR** | `LOW` | 90 | Linguistic errors in English naming ('1th', '2th', '3th') |

## 2. Grantha-by-Grantha Audit Statistics

| Grantha / Source | Total Rules | Quality Flags | Flagged % |
| :--- | :---: | :---: | :---: |
| **Brihat Parashara Hora Shastra** | 2,060 | 1,997 | 96.9% |
| **Saravali** | 1,655 | 1,003 | 60.6% |
| **KP Astrology** | 1,300 | 1,669 | 128.4% |
| **Lal Kitab** | 1,224 | 1,236 | 101.0% |
| **Bhrigu Nandi Nadi** | 1,128 | 648 | 57.4% |
| **Brihat Jataka** | 1,005 | 725 | 72.1% |
| **Brihat Samhita & Garga Samhita** | 956 | 1,124 | 117.6% |
| **Classic Misc** | 658 | 120 | 18.2% |
| **Phaladeepika** | 552 | 465 | 84.2% |
| **Muhurtha Chintamani & Nirnaya Sindhu** | 505 | 495 | 98.0% |
| **Prashna Marga** | 498 | 323 | 64.9% |
| **Jaimini Upadesha Sutras** | 415 | 408 | 98.3% |
| **Ank Shastra & Lo-Shu (अंकशास्त्र एवं लो-शू चक्र)** | 264 | 226 | 85.6% |
| **Sarvatobhadra & Kota Chakra Shastra** | 229 | 104 | 45.4% |
| **Tajika Neelakanthi** | 108 | 108 | 100.0% |
| **Samudrika Shastra (सामुद्रिक शास्त्र - गरुड़ एवं भविष्य पुराण)** | 27 | 6 | 22.2% |

## 3. Top Contradictory Rule Pairs (Sample)

The following rule pairs evaluate identical astronomical configurations with opposing polarities and must be quarantined until scholar review:

- **BPHS_BHAVA_L1_H1** (Brihat Parashara Hora Shastra): Opposite +/- polarities for identical criteria with peer rules: ['BPHS_BHAVA_L1_H1', 'BPHS_YOGINI_MANGALA_H1', 'BPHS_YOGINI_PINGALA_H1', 'BPHS_YOGINI_DHANYA_H1', 'BPHS_YOGINI_BHRAMARI_H1', 'BPHS_YOGINI_BHADRIKA_H1', 'BPHS_YOGINI_ULKA_H1', 'BPHS_YOGINI_SIDDHA_H1', 'BPHS_YOGINI_SANKATA_H1', 'BPHS_SUDARSHANA_लग्न_H1_SHUBHA', 'BPHS_SUDARSHANA_लग्न_H1_ASHUBHA', 'BJ_BLORD_L1_IN_H1', 'PD_BHAVA_LORD_L1_H1', 'TAJIKA_MUNTHAHA_H1'] | Condition: `[{'entity': 'Lord_1', 'house': 1}]`
- **BPHS_YOGINI_MANGALA_H1** (Brihat Parashara Hora Shastra): Opposite +/- polarities for identical criteria with peer rules: ['BPHS_BHAVA_L1_H1', 'BPHS_YOGINI_MANGALA_H1', 'BPHS_YOGINI_PINGALA_H1', 'BPHS_YOGINI_DHANYA_H1', 'BPHS_YOGINI_BHRAMARI_H1', 'BPHS_YOGINI_BHADRIKA_H1', 'BPHS_YOGINI_ULKA_H1', 'BPHS_YOGINI_SIDDHA_H1', 'BPHS_YOGINI_SANKATA_H1', 'BPHS_SUDARSHANA_लग्न_H1_SHUBHA', 'BPHS_SUDARSHANA_लग्न_H1_ASHUBHA', 'BJ_BLORD_L1_IN_H1', 'PD_BHAVA_LORD_L1_H1', 'TAJIKA_MUNTHAHA_H1'] | Condition: `[{'entity': 'Lord_1', 'house': 1}]`
- **BPHS_YOGINI_PINGALA_H1** (Brihat Parashara Hora Shastra): Opposite +/- polarities for identical criteria with peer rules: ['BPHS_BHAVA_L1_H1', 'BPHS_YOGINI_MANGALA_H1', 'BPHS_YOGINI_PINGALA_H1', 'BPHS_YOGINI_DHANYA_H1', 'BPHS_YOGINI_BHRAMARI_H1', 'BPHS_YOGINI_BHADRIKA_H1', 'BPHS_YOGINI_ULKA_H1', 'BPHS_YOGINI_SIDDHA_H1', 'BPHS_YOGINI_SANKATA_H1', 'BPHS_SUDARSHANA_लग्न_H1_SHUBHA', 'BPHS_SUDARSHANA_लग्न_H1_ASHUBHA', 'BJ_BLORD_L1_IN_H1', 'PD_BHAVA_LORD_L1_H1', 'TAJIKA_MUNTHAHA_H1'] | Condition: `[{'entity': 'Lord_1', 'house': 1}]`
- **BPHS_YOGINI_DHANYA_H1** (Brihat Parashara Hora Shastra): Opposite +/- polarities for identical criteria with peer rules: ['BPHS_BHAVA_L1_H1', 'BPHS_YOGINI_MANGALA_H1', 'BPHS_YOGINI_PINGALA_H1', 'BPHS_YOGINI_DHANYA_H1', 'BPHS_YOGINI_BHRAMARI_H1', 'BPHS_YOGINI_BHADRIKA_H1', 'BPHS_YOGINI_ULKA_H1', 'BPHS_YOGINI_SIDDHA_H1', 'BPHS_YOGINI_SANKATA_H1', 'BPHS_SUDARSHANA_लग्न_H1_SHUBHA', 'BPHS_SUDARSHANA_लग्न_H1_ASHUBHA', 'BJ_BLORD_L1_IN_H1', 'PD_BHAVA_LORD_L1_H1', 'TAJIKA_MUNTHAHA_H1'] | Condition: `[{'entity': 'Lord_1', 'house': 1}]`
- **BPHS_YOGINI_BHRAMARI_H1** (Brihat Parashara Hora Shastra): Opposite +/- polarities for identical criteria with peer rules: ['BPHS_BHAVA_L1_H1', 'BPHS_YOGINI_MANGALA_H1', 'BPHS_YOGINI_PINGALA_H1', 'BPHS_YOGINI_DHANYA_H1', 'BPHS_YOGINI_BHRAMARI_H1', 'BPHS_YOGINI_BHADRIKA_H1', 'BPHS_YOGINI_ULKA_H1', 'BPHS_YOGINI_SIDDHA_H1', 'BPHS_YOGINI_SANKATA_H1', 'BPHS_SUDARSHANA_लग्न_H1_SHUBHA', 'BPHS_SUDARSHANA_लग्न_H1_ASHUBHA', 'BJ_BLORD_L1_IN_H1', 'PD_BHAVA_LORD_L1_H1', 'TAJIKA_MUNTHAHA_H1'] | Condition: `[{'entity': 'Lord_1', 'house': 1}]`
- **BPHS_YOGINI_BHADRIKA_H1** (Brihat Parashara Hora Shastra): Opposite +/- polarities for identical criteria with peer rules: ['BPHS_BHAVA_L1_H1', 'BPHS_YOGINI_MANGALA_H1', 'BPHS_YOGINI_PINGALA_H1', 'BPHS_YOGINI_DHANYA_H1', 'BPHS_YOGINI_BHRAMARI_H1', 'BPHS_YOGINI_BHADRIKA_H1', 'BPHS_YOGINI_ULKA_H1', 'BPHS_YOGINI_SIDDHA_H1', 'BPHS_YOGINI_SANKATA_H1', 'BPHS_SUDARSHANA_लग्न_H1_SHUBHA', 'BPHS_SUDARSHANA_लग्न_H1_ASHUBHA', 'BJ_BLORD_L1_IN_H1', 'PD_BHAVA_LORD_L1_H1', 'TAJIKA_MUNTHAHA_H1'] | Condition: `[{'entity': 'Lord_1', 'house': 1}]`
- **BPHS_YOGINI_ULKA_H1** (Brihat Parashara Hora Shastra): Opposite +/- polarities for identical criteria with peer rules: ['BPHS_BHAVA_L1_H1', 'BPHS_YOGINI_MANGALA_H1', 'BPHS_YOGINI_PINGALA_H1', 'BPHS_YOGINI_DHANYA_H1', 'BPHS_YOGINI_BHRAMARI_H1', 'BPHS_YOGINI_BHADRIKA_H1', 'BPHS_YOGINI_ULKA_H1', 'BPHS_YOGINI_SIDDHA_H1', 'BPHS_YOGINI_SANKATA_H1', 'BPHS_SUDARSHANA_लग्न_H1_SHUBHA', 'BPHS_SUDARSHANA_लग्न_H1_ASHUBHA', 'BJ_BLORD_L1_IN_H1', 'PD_BHAVA_LORD_L1_H1', 'TAJIKA_MUNTHAHA_H1'] | Condition: `[{'entity': 'Lord_1', 'house': 1}]`
- **BPHS_YOGINI_SIDDHA_H1** (Brihat Parashara Hora Shastra): Opposite +/- polarities for identical criteria with peer rules: ['BPHS_BHAVA_L1_H1', 'BPHS_YOGINI_MANGALA_H1', 'BPHS_YOGINI_PINGALA_H1', 'BPHS_YOGINI_DHANYA_H1', 'BPHS_YOGINI_BHRAMARI_H1', 'BPHS_YOGINI_BHADRIKA_H1', 'BPHS_YOGINI_ULKA_H1', 'BPHS_YOGINI_SIDDHA_H1', 'BPHS_YOGINI_SANKATA_H1', 'BPHS_SUDARSHANA_लग्न_H1_SHUBHA', 'BPHS_SUDARSHANA_लग्न_H1_ASHUBHA', 'BJ_BLORD_L1_IN_H1', 'PD_BHAVA_LORD_L1_H1', 'TAJIKA_MUNTHAHA_H1'] | Condition: `[{'entity': 'Lord_1', 'house': 1}]`
- **BPHS_YOGINI_SANKATA_H1** (Brihat Parashara Hora Shastra): Opposite +/- polarities for identical criteria with peer rules: ['BPHS_BHAVA_L1_H1', 'BPHS_YOGINI_MANGALA_H1', 'BPHS_YOGINI_PINGALA_H1', 'BPHS_YOGINI_DHANYA_H1', 'BPHS_YOGINI_BHRAMARI_H1', 'BPHS_YOGINI_BHADRIKA_H1', 'BPHS_YOGINI_ULKA_H1', 'BPHS_YOGINI_SIDDHA_H1', 'BPHS_YOGINI_SANKATA_H1', 'BPHS_SUDARSHANA_लग्न_H1_SHUBHA', 'BPHS_SUDARSHANA_लग्न_H1_ASHUBHA', 'BJ_BLORD_L1_IN_H1', 'PD_BHAVA_LORD_L1_H1', 'TAJIKA_MUNTHAHA_H1'] | Condition: `[{'entity': 'Lord_1', 'house': 1}]`
- **BPHS_SUDARSHANA_लग्न_H1_SHUBHA** (Brihat Parashara Hora Shastra): Opposite +/- polarities for identical criteria with peer rules: ['BPHS_BHAVA_L1_H1', 'BPHS_YOGINI_MANGALA_H1', 'BPHS_YOGINI_PINGALA_H1', 'BPHS_YOGINI_DHANYA_H1', 'BPHS_YOGINI_BHRAMARI_H1', 'BPHS_YOGINI_BHADRIKA_H1', 'BPHS_YOGINI_ULKA_H1', 'BPHS_YOGINI_SIDDHA_H1', 'BPHS_YOGINI_SANKATA_H1', 'BPHS_SUDARSHANA_लग्न_H1_SHUBHA', 'BPHS_SUDARSHANA_लग्न_H1_ASHUBHA', 'BJ_BLORD_L1_IN_H1', 'PD_BHAVA_LORD_L1_H1', 'TAJIKA_MUNTHAHA_H1'] | Condition: `[{'entity': 'Lord_1', 'house': 1}]`

*Full machine-readable issue database saved to: `docs/upgrade/rules_lint_issues.csv`*
