# JyotishOS — World-Class Shastriya Phaladesh: Implementation PRD & Agent Playbook

**Repo:** `ai-jyotish-app` (Python, FastAPI + Streamlit, `src/jyotish/...`)
**Audience:** an AI coding agent (Antigravity) working inside VS Code, supervised by the product owner (Shubham).
**Goal:** turn the current codebase into a mathematically correct, classically grounded, auditable Vedic astrology engine whose phaladesh (interpretation) is traceable to verified shastriya sources, with the LLM used only as a narrator.

---

## 0. How to use this document (read first)

### 0.1 Rules for the agent (non-negotiable)

1. **Work one phase at a time.** Before coding a phase, write a short plan (files to touch, tests to add), wait for owner approval, then implement. Do not start the next phase without approval.
2. **Never invent astrological content.** Do not write new rule text, sloka numbers, chapter/verse citations, or "reference" chart values from memory. Reference data comes only from (a) Swiss Ephemeris computed in this repo, or (b) files the owner places in `tests/reference/`. If something is missing, stop and ask.
3. **Never silently fall back.** If a precise engine is unavailable, raise a clear error or return the result with `engine_degraded=true` and a visible warning. No silent substitution.
4. **Tests first for math.** Every calculation change needs a test comparing against the oracle (Section 6) before the change is merged.
5. **Small commits.** One task ID per commit, message format `P1-T3: use zoneinfo for birth datetime`.
6. **Do not delete data without a backup branch.** Rule files are quarantined (status flag), not deleted, in Phase 4.
7. **No secrets in git.** Ever. See Phase 0.
8. After each phase, produce `docs/phase_reports/PHASE_N_REPORT.md`: what changed, tests run, known gaps.

### 0.2 Suggested workflow in Antigravity

- Save this file as `docs/IMPLEMENTATION_PRD.md` in the repo.
- Put Section 0.1 into the agent's persistent rules/instructions (e.g. `AGENTS.md` or the IDE's workspace rules folder) so every session sees it.
- Start each session with: *"Read docs/IMPLEMENTATION_PRD.md. We are on Phase N. Produce the plan for Phase N only, list files and tests, and wait for my approval."*
- Review each plan, then say *"Approved, implement Phase N, task by task, running tests after each task."*
- Ask the agent to run `pytest -q` and attach the output at the end of every task.

---

## 1. Baseline audit (what the code review found)

These are findings from reading the repository. Items marked **VERIFY** were inferred from code and must be confirmed by a test in Phase 1/2.

| # | Finding | Location |
|---|---------|----------|
| B1 | README claims "Swiss Ephemeris / JPL DE431", but `pyswisseph` is **not** in `requirements.txt`; Dockerfile installs only that file, so production runs the PyEphem fallback. | `requirements.txt`, `Dockerfile`, `core/ephemeris.py` |
| B2 | `SwissEphemerisProvider` silently falls back to PyEphem on any exception (`except BaseException`). | `core/ephemeris.py` |
| B3 | PyEphem path uses `ephem.Ecliptic(body)`; the equinox/epoch of the resulting longitude must match the ayanamsa epoch. **VERIFY** (possible ~0.3–0.4° systematic error in 2026). | `core/ephemeris.py` |
| B4 | PyEphem ayanamsas other than Lahiri are fixed offsets from a Lahiri polynomial; Swiss path supports only a few modes. | `core/ephemeris.py` |
| B5 | True node computed by hand-written perturbation series on the PyEphem path. | `core/ephemeris.py` |
| B6 | Time zone is a plain float (`timezone_offset=5.5`); no IANA tz database, no historical DST, no LMT handling. | `core/models.py`, `core/calculator.py:239`, `services/geocoding.py` |
| B7 | House systems: whole sign / equal only; `calculate_bhava_chalit` uses 30° spans centred on cusp. | `core/calculator.py` |
| B8 | ~12,506 rules in `rules/grantha_rules/*.json` are largely produced by generator scripts (`build_*.py`) with targets like "reach 12,500"; citations (adhyaya/sloka) are written by code, not verified against the texts. Some rule names and conditions disagree (e.g. a D12 "Vishnu in Scorpio" rule whose condition is "Jupiter in Scorpio"). Grammar artefacts ("1th house"), heavy templating (e.g. Tajika ~89% same description prefix). | `rules/build_*.py`, `rules/grantha_rules/` |
| B9 | Multiple schools (Parashari, Jaimini, KP, Nadi, Lal Kitab, Tajika, numerology, vastu) feed one engine/consensus score. | `rules/engine.py`, `rules/consensus.py` |
| B10 | Golden tests snapshot the code's own output; they do not validate correctness against an independent reference. | `tests/golden/` |
| B11 | Secrets/data committed: `data/users.json`, `data/purchase_codes.json`, `data/jyotish_enterprise.db` (14 MB), hard-coded master licence code in `services/auth.py`; `.gitignore` does not exclude `data/`. CORS `allow_origins=["*"]`. | repo root, `api/main.py` |
| B12 | Inconsistent LLM model names (e.g. docstring "gemini-3.8-flash"; code falls back through old models); `google-genai` and `google-generativeai` both listed. | `ai/narrative.py`, `requirements.txt` |
| B13 | Very large single files (e.g. `ui/app.py` ~1.4 MB, `services/panchang.py` ~190 KB, `services/milan.py` ~140 KB) — hard to test and maintain. | `ui/`, `services/` |

---

## 2. Product vision & principles

**Vision:** an astrology engine a serious Jyotishi would trust: correct charts, correct dashas, interpretations that cite their classical source, honest uncertainty.

**Principles**

1. **Math is deterministic and verified.** The LLM never computes planetary positions, dashas, or yogas.
2. **Every interpretive statement has provenance** (rule id → source text → verification status).
3. **School purity.** Parashari, Jaimini, KP, Tajika, Nadi, Lal Kitab are separate engines with separate outputs. They are never averaged into one number.
4. **Honest confidence.** Show birth-time uncertainty, engine used, and rule verification status. Phaladesh is traditional guidance, not a guarantee.
5. **Safety.** No death-date prediction, no medical diagnosis, no gambling/stock tips, no fear-based remedy selling.

**Non-goals (this PRD):** new astrology schools, mobile native apps, payments redesign, scientific claims of predictive validity.

---

## 3. Target architecture

```
Input (birth data, place, school, ayanamsa, house system)
   │
   ▼
[Location & Time Service]  → IANA tz, historical DST, LMT, ambiguity flags
   │
   ▼
[Ephemeris Service]        → pyswisseph (required); degraded mode explicit
   │
   ▼
[Chart Core]               → D1..D60, houses, avasthas, bala, ashtakavarga
   │
   ▼
[Dasha Engines]            → Vimshottari (+ others), per-school
   │
   ▼
[Factor Extractor]         → typed facts: "Jupiter in 10H, own sign, aspected by..., lord of 5 & 8"
   │
   ▼
[Rule Engine per School]   → only status=verified rules; bhanga/cancellation; conflict resolution
   │
   ▼
[Evidence Pack (JSON)]     → domain-wise findings, each with rule_id + source + strength + why
   │
   ▼
[Narrator (LLM)]           → writes prose ONLY from Evidence Pack; citation validator rejects extras
   │
   ▼
API / UI / PDF
```

Module layout to move toward (keep backward-compatible imports during migration):

```
src/jyotish/
  core/            # pure math, no I/O, no LLM
  timeloc/         # NEW: tz, DST, geocoding wrappers
  schools/         # NEW: parashari/, jaimini/, kp/, tajika/, nadi/, lalkitab/
  rules/           # schema, loader, linter, engine, provenance
  evidence/        # NEW: factor extraction + evidence pack
  narrate/         # NEW (refactor of ai/): prompts, validator, providers
  api/ ui/ services/
tests/
  reference/       # owner-supplied reference charts (read-only)
  oracle/          # Swiss-generated expectations
```

---

## 4. Phases

Effort tags: **S** ≤ 0.5 day, **M** 1–2 days, **L** 3–5 days, **XL** > 1 week.

### Phase 0 — Security & repo hygiene (do first, ~2 days)

| ID | Task | Size | Acceptance |
|----|------|------|-----------|
| P0-T1 | Add `data/`, `*.db`, `saved_charts_db.json`, `.env` to `.gitignore`. `git rm --cached` those files. Keep `data/*.example.json` templates with fake values. | S | `git ls-files data` shows only examples |
| P0-T2 | Remove hard-coded master licence code from `services/auth.py`; licence codes must be created via admin CLI and stored hashed. | S | `grep -ri "MASTER" src` returns no code |
| P0-T3 | Provide `docs/SECURITY_ROTATION.md` telling the owner to (a) rotate all passwords/API keys, (b) purge history with `git filter-repo` or BFG, (c) invalidate existing licence codes. Agent must **not** run history rewrite itself. | S | Doc exists |
| P0-T4 | CORS: read allowed origins from env `ALLOWED_ORIGINS`; default empty (deny). | S | Test: disallowed origin gets no CORS header |
| P0-T5 | Add rate limiting (e.g. `slowapi`) to auth and chat endpoints; add login attempt lockout. | M | Tests for 429 |
| P0-T6 | Move DB/users from JSON files to the SQLAlchemy models already in `db/models.py`; migration script `scripts/migrate_json_to_database.py` is the base. Password hashing stays PBKDF2-HMAC-SHA256 with ≥ 600k iterations or switch to argon2id. | M | Tests in `test_database_persistence.py` pass |
| P0-T7 | Dependency cleanup: pin versions, remove duplicate Gemini SDK (keep one: `google-genai`), add `pyswisseph`, `tzdata`, `timezonefinder`, `pytest`, `pytest-cov` to dev/prod files separately (`requirements.txt`, `requirements-dev.txt`). | S | `pip install -r requirements.txt` succeeds in a clean venv |

**Phase gate:** CI green; no secrets in tree (`gitleaks` or `detect-secrets` in CI).

---

### Phase 1 — Ephemeris & time correctness (~1–2 weeks)

**Objective:** planetary longitudes, ayanamsa, lagna, and local time are right to professional tolerance.

| ID | Task | Size | Acceptance |
|----|------|------|-----------|
| P1-T1 | Make `pyswisseph` a hard requirement. On startup, call `swe.set_ephe_path` to a configured folder (`SWE_EPHE_PATH`), verify `.se1` files for 1800–2400 CE exist (document how the owner downloads them), run a self-test (compute Sun at J2000, compare to known value), and expose `/health/engine`. | M | Health shows `engine="swisseph"`, version, ephe path, files found |
| P1-T2 | Remove the silent `except BaseException` fallbacks. New behaviour: if Swiss fails → raise `EphemerisUnavailable`; PyEphem allowed only when env `ALLOW_DEGRADED_ENGINE=true`, and then every response carries `engine_degraded=true` + UI banner. Remove the label "Swiss Ephemeris (DE431)" unless Swiss with DE files is actually loaded (Moshier mode must be labelled "Swiss (Moshier)"). | M | Unit tests for each mode |
| P1-T3 | Ayanamsa: map all supported names to Swiss sidereal modes (`SIDM_LAHIRI`, `SIDM_RAMAN`, `SIDM_KRISHNAMURTI`, `SIDM_YUKTESHWAR`, `SIDM_TRUE_CITRA`, `SIDM_FAGAN_BRADLEY`, etc.). Unknown name → error, not silent Lahiri. Default Lahiri. Expose list via API. | M | Test every mode against `swe.get_ayanamsa_ut` |
| P1-T4 | **Investigate B3:** write a test computing Sun/Moon/Jupiter sidereal longitude via PyEphem path vs Swiss for 20 dates (1950–2050). Report max error. If > 0.02° (Moon > 0.05°), fix epoch handling (use of-date ecliptic/true equinox) or declare PyEphem path unsupported. Document result in report. | M | Error table in `docs/phase_reports/PHASE_1_REPORT.md` |
| P1-T5 | Nodes: Swiss `MEAN_NODE` / `TRUE_NODE` only; node speed from Swiss, not constants. Ketu = Rahu + 180°. | S | Tests |
| P1-T6 | Lagna & houses via Swiss `swe.houses_ex` with sidereal flag; support **Whole Sign, Equal, Sripati (Porphyry-based), Porphyry, Placidus (for KP)**. Add `house_system` to `BirthData`. Bhava Chalit built from actual cusps (not "30° centred"). Define behaviour for latitude > 66° (fallback to Equal/Whole Sign with warning). | L | Compare ASC/MC/cusps to Swiss for 20 places incl. Lucknow, Delhi, London, Sydney, Reykjavik |
| P1-T7 | **Time & location service (`timeloc/`)**: replace `timezone_offset: float` with `timezone: IANA string` + optional manual override. Use `zoneinfo`/`tzdata`; derive local → UTC with correct historical rules (India: 1942–45 war time, 1962, 1965, 1971 DST; also pre-1906 LMT / pre-1947 regional zones where tz data exists). Detect and flag **ambiguous/non-existent local times** (DST transitions) and require user choice. Keep a `birth_time_confidence` field (exact / approximate ± minutes / unknown). | L | Tests with known historical Indian dates; ambiguous-time test |
| P1-T8 | Geocoding: cache results; return lat/lon/elevation/IANA tz via `timezonefinder`; allow manual lat/lon. Keep the built-in gazetteer as offline fallback but verify coordinates against a trusted source (owner supplies list or agent flags values for manual review — do not guess). | M | Tests; gazetteer review list in report |
| P1-T9 | Speed/retrograde: take from Swiss `FLG_SPEED`; keep combustion orbs configurable (document classical orbs and let school select). | S | Tests |
| P1-T10 | Add Julian Day, UTC datetime, ayanamsa value, engine info, and tz info to every chart's `meta` block. | S | Schema test |

**Phase gate:** oracle tests (Section 6) green; max planetary error vs Swiss reference ≤ 1 arc-second (same engine), Lagna ≤ 1 arc-minute vs Swiss `houses_ex`.

---

### Phase 2 — Verification harness (~1 week, can run in parallel with P1 after T1)

| ID | Task | Size | Acceptance |
|----|------|------|-----------|
| P2-T1 | Create `tests/oracle/` generator that uses Swiss directly (independent of app code paths) to produce expected longitudes/ayanamsa/houses for a fixed set of ≥ 100 (datetime, lat, lon) inputs spanning 1900–2100, multiple hemispheres. | M | Regeneration is deterministic |
| P2-T2 | Create `tests/reference/README.md` and a JSON schema for **owner-supplied reference charts** (e.g. exported from Jagannatha Hora / other trusted software, or from documented birth records with verified time). The agent must not populate these itself. | S | Schema + sample with fake marker `"_example": true` |
| P2-T3 | Comparison tests: app output vs oracle vs reference, with explicit tolerances per field (planets 1″, lagna 1′, nakshatra/pada exact, varga signs exact, dasha dates ±1 day, ashtakavarga bindus exact). | M | `pytest -m reference` runs |
| P2-T4 | Property/invariant tests: SAV total = 337 for classical method; Vimshottari sum = 120 y; Moon nakshatra ∈ 27; varga signs ∈ 1–12; retrograde ⇔ negative speed; Rahu–Ketu 180°. | S | Pass |
| P2-T5 | Demote existing `tests/golden/` snapshots to "regression only" (rename marker `regression`); never treat as proof of correctness. | S | Marker present |
| P2-T6 | CI: GitHub Actions job runs unit + oracle tests on every PR; coverage ≥ 80% on `core/`, `timeloc/`, `dasha/`. | S | CI green |

---

### Phase 3 — Calculation core audit (~2–3 weeks)

Audit each module against the classical definition. For every module the agent must (a) write down the formula/rule it implements in a docstring with its **source name** (text name only; verse numbers only if the owner confirms), (b) add tests, (c) list deviations in the phase report. Where classical authorities differ, expose a **configuration option** rather than choosing silently.

| ID | Module | Checks |
|----|--------|--------|
| P3-T1 | `core/varga.py` | D2 (Parashari hora vs Jaimini/Kashinath variants), D3 (Parashari vs Jagannatha), D4, D7, D9, D10, D12, D16, D20, D24, D27, D30 (Parashari Trimshamsa degrees by odd/even sign), D40, D45, D60. Add missing D5, D6, D8, D11 if desired. Make variants selectable. Test with boundary degrees (0°, 29°59′59″). |
| P3-T2 | `core/constants.py` | Exaltation/debilitation degrees, moolatrikona ranges, own signs, natural and temporal friendship, aspects (full + special for Mars/Jupiter/Saturn; Rahu/Ketu option), dignities table. Cross-check with a BPHS-based table the owner supplies. |
| P3-T3 | `core/shadbala.py` | Sthana (Uccha, Saptavargaja, Ojayugma, Kendradi, Drekkana), Dik, Kala (Nathonnatha, Paksha, Tribhaga, Abda/Masa/Vara/Hora, Ayana, Yuddha), Cheshta, Naisargika, Drik. Required minimums in Rupas. Compare with an owner-supplied reference for ≥ 5 charts. |
| P3-T4 | `core/ashtakavarga.py` | BAV tables per classical contributors, SAV totals, Trikona & Ekadhipatya shodhana, Pinda. Invariants from P2-T4. |
| P3-T5 | `dasha/vimshottari.py` | Balance of dasha from Moon's nakshatra fraction; year length option (365.25 / 365.2425 / 360 savana) with explicit default; antardasha/pratyantardasha boundaries; test against reference charts. Document that Mean vs True node does not affect Vimshottari but ayanamsa does. |
| P3-T6 | Other dashas (`yogini`, `ashtottari`, `chara`, `kcd`, `narayana`, `sthira_drig`, `shoola`, `sama_dashas`) | For each: applicability conditions (e.g. Ashtottari only when its classical condition holds), sequence, years, tests vs reference. Mark unverified ones `experimental=true` and hide from default UI. |
| P3-T7 | `core/jaimini.py`, `services/jaimini_suite.py` | Chara Karakas (7 vs 8), Karakamsha, Arudha (incl. exceptions when arudha falls in 1st/7th from the house), Upapada, Argala, Rashi drishti. |
| P3-T8 | `core/kp.py` | Sub-lord/sub-sub-lord tables (249), Placidus cusps, KP ayanamsa, significators, ruling planets. Keep KP fully separate from Parashari scoring. |
| P3-T9 | `services/panchang.py` | Sunrise/sunset (Swiss `rise_trans`, with refraction & disc-centre options), tithi/nakshatra/yoga/karana end times, vara boundaries at sunrise, Choghadiya, Rahukala, Abhijit, adhika/kshaya tithi handling. Split file into submodules. |
| P3-T10 | `services/milan.py` | Ashtakoota 36 points tables, cancellations (bhanga) clearly attributed, Manglik rules with school options, Nadi/Bhakoot parihara. Split file; tests per koota. |
| P3-T11 | `core/gochar.py`, `services/transit_*` | Sade Sati / Dhaiya from natal Moon sign, Vedha, Ashtakavarga transit scoring; transit computed with Swiss at requested date. |
| P3-T12 | `services/varshaphal.py` | Solar return to the second (Swiss `solcross`), Muntha, Varsheshwar (Panchadhikari), Sahams, Tajika aspects/yogas (Ithasala, Ishrafa, etc.), Mudda dasha. |
| P3-T13 | Refactor oversized files (`ui/app.py`, `services/panchang.py`, `services/milan.py`, `core/karmaphala.py`, `core/lalkitab.py`) into modules < 800 lines each **without behaviour change** (tests prove equivalence). | |

**Phase gate:** each module has a docstring stating its classical basis, configuration options, tests, and a line in `docs/CALC_AUDIT.md` (status: verified / partially verified / unverified).

---

### Phase 4 — Rule library re-architecture (~3–4 weeks, owner-heavy)

**Problem:** rule *quantity* was optimised, not rule *truth*. Goal: a smaller, verified, provenance-rich library.

#### 4.1 New rule schema (v2)

```json
{
  "rule_id": "BPHS-24-LORD1-H1",
  "schema_version": 2,
  "school": "parashari",
  "source": {
    "text": "Brihat Parashara Hora Shastra",
    "edition": "<edition/translator/year as given by owner>",
    "chapter": 24,
    "verse": "11",
    "original_excerpt_sa": "<short Sanskrit excerpt if public domain / permitted>",
    "paraphrase_hi": "<own-words summary>",
    "paraphrase_en": "<own-words summary>"
  },
  "condition": { "type": "ALL", "criteria": [ { "fact": "lord_of_house", "house": 1, "placed_in_house": 1 } ] },
  "modifiers": {
    "strengthens_if": [ { "fact": "dignity_in", "values": ["own","exalted","moolatrikona"] } ],
    "weakens_if": [ { "fact": "combust" }, { "fact": "debilitated_without_bhanga" } ],
    "bhanga_refs": ["BPHS-NEECHABHANGA-1"]
  },
  "effect": { "domain": "personality", "polarity": "+", "summary_hi": "...", "summary_en": "..." },
  "applicability": { "dasha_required": false, "varga": "D1", "min_shadbala_ratio": null },
  "verification": {
    "status": "draft|machine_checked|scholar_verified|rejected",
    "verified_by": null,
    "verified_on": null,
    "notes": ""
  },
  "generated": false
}
```

Rules:
- `strength_base` numeric values from the old library are **not** carried over unless the owner can justify them; strength comes from computed shadbala/dignity/modifiers, not from a hand-typed number.
- Copyright: store verse **references** and short, permitted excerpts; paraphrases must be original. Do not paste full translations of in-copyright books.

#### 4.2 Tasks

| ID | Task | Size | Acceptance |
|----|------|------|-----------|
| P4-T1 | Implement schema v2 with Pydantic + JSON Schema; loader rejects invalid rules. | M | Schema tests |
| P4-T2 | **Inventory & lint script** `scripts/rules_audit.py`: counts per file; flags (a) `generated: true` (rules emitted by `build_*.py`), (b) name/condition mismatch (e.g. name mentions planet/sign/varga not present in condition), (c) ordinal grammar errors, (d) near-duplicate effect text (≥ 90% similarity), (e) missing source fields, (f) contradictory rules with identical condition but opposite polarity. Output CSV + Markdown summary. | M | `docs/RULES_AUDIT.md` produced |
| P4-T3 | **Quarantine, don't delete:** migrate all existing rules to v2 with `verification.status = "draft"`, `generated = true` where a build script produced them. Engine default: **only `scholar_verified` (and optionally `machine_checked`) rules are used in user-facing phaladesh.** Draft rules visible only in an admin "Rules Lab". | L | Counter shows verified vs draft |
| P4-T4 | Archive generator scripts under `scripts/legacy_rule_generators/` with a README stating they are historical and must not be used to inflate counts. Remove "12,500+" claims from README/UI. | S | Grep clean |
| P4-T5 | **Verification workflow UI/CLI** (`scripts/rules_review.py` or a Streamlit admin page): shows rule, condition rendered in plain language, test chart that triggers it, and buttons *Verify / Edit / Reject* with reviewer name. Writes to `verification`. | L | Reviewer can verify 20 rules/hour |
| P4-T6 | **Starter verified core (owner + scholar):** target first ~300–600 rules for Parashari (bhava lords in houses, planets in houses, key yogas with bhanga, dasha-lord effects) from BPHS/Phaladeepika/Saravali/Brihat Jataka. The agent prepares worksheets; humans verify. Agent must not mark anything `scholar_verified`. | XL | Target tracked in `docs/RULES_PROGRESS.md` |
| P4-T7 | **Yoga catalogue with definitions + bhanga:** Pancha Mahapurusha, Gajakesari, Raja yogas (kendra-trikona lord relations), Dhana, Viparita Raja, Neechabhanga (all listed variants), Kemadruma + cancellation, Kaal Sarp (with school variants), Mangal dosha (with parihara variants), Pitra/Grahan etc. Each yoga is a **function with explicit conditions** unit-tested on synthetic charts, then linked to textual rules. | L | Synthetic chart tests |
| P4-T8 | **School isolation:** `schools/<name>/` each with own rule set, engine, and output section. Remove cross-school mixing in `rules/consensus.py`; if a combined view is shown it must display per-school results side by side, never an averaged "confidence". | L | Tests: Parashari output unaffected by Lal Kitab rules |
| P4-T9 | **Conflict handling:** within a school, define precedence (e.g. stronger planet/ bhava, classical "vishesha" rules, bhanga overrides) and record the reasoning in the evidence pack. | M | Conflict tests |
| P4-T10 | Performance: inverted index on rule facts (reuse `inverted_index.py`) so evaluation < 200 ms per chart. | M | Benchmark |

---

### Phase 5 — Phaladesh synthesis & narration (~3 weeks)

**Objective:** interpretations come from verified rules + computed strength, assembled per life domain; the LLM only writes language.

#### 5.1 Factor extractor (`evidence/factors.py`)

Computes typed facts per planet/house: sign, house, dignity, avastha, combustion, retrogression, shadbala ratio, aspects received/given, conjunctions, house lordships, nakshatra and lord, varga positions (D9 vargottama, etc.), ashtakavarga bindus, karakatwa. Pure function of the chart; unit-tested.

#### 5.2 Domain analysis (`evidence/domains/`)

Domains: personality, health tendencies (general, not diagnosis), education, career, wealth, marriage/relationships, children, family, foreign travel, spirituality, property. For each domain define, per school, the **classical significators** (bhava, bhava lord, karaka, relevant vargas) and the order of analysis (Bhava → Lord → Karaka → Aspects → Varga → Dasha → Transit). Only `domains/*.yaml` configuration + code; no free text.

#### 5.3 Evidence Pack (JSON)

```json
{
  "chart_meta": { "engine": "swisseph", "ayanamsa": "lahiri", "house_system": "whole_sign", "birth_time_confidence": "exact" },
  "domain": "career",
  "school": "parashari",
  "findings": [
    {
      "finding_id": "F1",
      "rule_ids": ["BPHS-10-LORD10-H11"],
      "claim_en": "...", "claim_hi": "...",
      "polarity": "+",
      "strength": 0.72,
      "strength_reason": ["10th lord exalted (shadbala 1.34)", "aspected by Jupiter"],
      "timing": { "dasha_support": ["Jupiter MD / Saturn AD: 2027-03 → 2029-09"], "transit_support": [] },
      "caveats": ["Combustion reduces result"]
    }
  ],
  "unresolved_conflicts": [],
  "disclaimers": ["traditional guidance, not guarantee"]
}
```

`claim_*` text is taken from the verified rule's `effect.summary_*`, never newly written by the LLM.

#### 5.4 Tasks

| ID | Task | Size | Acceptance |
|----|------|------|-----------|
| P5-T1 | Implement factor extractor with full unit tests. | L | ≥ 90% coverage |
| P5-T2 | Implement domain YAML configs + analysis functions for Parashari (first), then Jaimini/KP/Tajika as separate packs. | XL | Evidence packs validate against JSON Schema |
| P5-T3 | Strength model: documented formula combining dignity, shadbala ratio, avastha, bhanga, aspects. Weights in config with documented rationale; no magic numbers in code. Expose "why" breakdown. | M | Test cases + docs |
| P5-T4 | Dasha/transit timing: for each finding, mark whether the current MD/AD/PD lord is a significator (lord/karaka/occupant/aspecting); list windows. Event-window query (existing "Ghatna Query") refactored to use evidence packs. | L | Tests with fixed dates |
| P5-T5 | **Narrator refactor (`narrate/`)**: prompt template receives *only* the Evidence Pack; instructs the model to (a) use only provided findings, (b) tag every sentence with `[F#]`, (c) add no new planetary facts, (d) use probabilistic wording ("tendency", "suggests"), (e) respect language (Hindi/English). Single provider config via env (`LLM_MODEL`), no hard-coded fallback list of old models. | M | Prompt snapshot test |
| P5-T6 | **Citation/grounding validator:** after generation, parse tags; reject or regenerate if any sentence has no `[F#]`, references an unknown id, or introduces a planet/house/sign/dates not in the pack (regex + entity check). Strip tags for display but keep them in the API response (`provenance`). Max 2 retries then fall back to template rendering of `claim_*`. | L | Adversarial tests (model told to hallucinate) |
| P5-T7 | **Safety layer:** block/redirect death-timing, specific disease diagnosis, pregnancy/legal/financial certainty, "your spouse will die" style outputs, and fear-based remedy upsell. Remedies come only from a curated, source-referenced remedy table (`data/remedies.yaml`), each with caution text (e.g. gemstones: "consult a qualified practitioner; not a medical/financial guarantee"). | M | Red-team test list |
| P5-T8 | Interactive chat (`api/v1/chat.py`): ground each answer on a freshly built evidence pack for the question's domain; refuse to answer from "general astrology memory". | M | Tests |
| P5-T9 | Report generator (`services/report_generator.py`, `pdf_generator.py`): per-domain sections, each finding shows source (text + chapter/verse reference) and verification badge; Devanagari fonts embedded; chart images (North/South/East) rendered correctly; page numbers; disclaimer. | L | Sample PDF review by owner |
| P5-T10 | Retire/rewrite `services/shastriya_faladesh.py` and `shastriya_pramana.py` templates that produce text without rule provenance; keep only what flows through evidence packs. | M | No text without provenance |

---

### Phase 6 — API, UI/UX, ops (~2 weeks)

| ID | Task | Size |
|----|------|------|
| P6-T1 | Birth input form: place autocomplete, tz display with "DST/historical note", ambiguity prompt, birth-time confidence selector, ayanamsa / house system / node type / school selectors with sane defaults and tooltips. |
| P6-T2 | Result pages always show: engine badge (`swisseph`/degraded), ayanamsa value, rules used count (verified), and per-finding "source" popover. |
| P6-T3 | "Rules Lab" admin page (draft rules, review queue, audit stats) behind admin role. |
| P6-T4 | OpenAPI regeneration; version API as `/v1`, add `/v1/charts/{id}/evidence?domain=career&school=parashari`; update Postman collection. |
| P6-T5 | Observability: structured logs (no PII), request ids, error tracking, `/health`, `/health/engine`. |
| P6-T6 | Performance targets: chart compute < 500 ms; full evidence pack < 2 s; PDF < 8 s; cache by (birth data hash, options). |
| P6-T7 | Privacy: encrypt birth data at rest, add "delete my data" endpoint, consent text, no birth data in logs/LLM provider logs where configurable. |
| P6-T8 | Deployment: Docker image installs from pinned requirements, includes ephemeris files via volume; docker-compose healthchecks; `DEPLOYMENT.md` updated. |

---

### Phase 7 — Hardening & release (~1–2 weeks)

| ID | Task |
|----|------|
| P7-T1 | Full regression + oracle + reference suite in CI; mutation-style sanity checks on 5 critical functions (ayanamsa, lagna, dasha balance, varga D9, SAV). |
| P7-T2 | External review: 3 practising Jyotishis review 10 generated reports each using a rubric (correct facts, classical consistency, tone, safety); results in `docs/REVIEW_FEEDBACK.md`; fix issues. |
| P7-T3 | Load test (100 concurrent chart requests). |
| P7-T4 | Documentation: `docs/METHODOLOGY.md` (all formulas/options), `docs/RULES_POLICY.md` (verification policy), `docs/LIMITATIONS.md`. Public claims limited to what is verified. |
| P7-T5 | Release checklist and version tag `v1.0.0`. |

---

## 5. Critical requirements (cross-cutting)

1. **Reproducibility:** same input + options → identical output; chart `meta` contains everything needed to reproduce.
2. **Configuration over hidden choices:** ayanamsa, node type, house system, dasha year length, varga variants, combustion orbs, school.
3. **Traceability:** `rule_id → source → verification status` visible in API and report.
4. **Degradation is visible:** never hide a lower-accuracy path.
5. **No overclaiming:** remove README/UI claims ("no hallucination", "12,500+ authentic rules", "DE431") unless proven by Phase 2/4 evidence.
6. **Legal/IP:** respect copyright of translations/commentaries; store references and original paraphrases.

---

## 6. Test strategy

| Layer | Source of truth | Tolerance |
|-------|-----------------|-----------|
| Planet longitude (Swiss path) | Independent Swiss oracle script | ≤ 1″ |
| Planet longitude (degraded path, if allowed) | Swiss oracle | ≤ 0.02° (Moon ≤ 0.05°) or path disabled |
| Ayanamsa | `swe.get_ayanamsa_ut` per mode | ≤ 0.0001° |
| Lagna / house cusps | `swe.houses_ex` | ≤ 1′ |
| Nakshatra/pada, varga sign | Derived from oracle longitude | exact |
| Vimshottari dates | Owner-supplied reference software output | ±1 day |
| Ashtakavarga | Classical invariants + reference | exact |
| Shadbala | Owner-supplied reference | ±2% |
| Rules | Synthetic charts built to trigger each rule | exact match |
| Narration | Grounding validator + red-team prompts | 0 ungrounded sentences |

Markers: `unit`, `oracle`, `reference`, `regression`, `redteam`, `slow`.

---

## 7. Owner inputs required (agent must ask, not guess)

1. Swiss Ephemeris data files (`.se1`) and licence note (Swiss Ephemeris is AGPL/commercial dual-licensed — owner must decide licensing before commercial release).
2. At least 10 reference charts with verified birth data and exports from a trusted software (planet longitudes, houses, Vimshottari dates, shadbala, ashtakavarga).
3. Edition list of classical texts to be used as sources, plus scholar(s) available for rule verification.
4. Decision on default options: ayanamsa (default Lahiri), node (default Mean/True), house system (default Whole Sign for Parashari, Placidus for KP), dasha year length, languages.
5. Curated remedies list and their sources.
6. LLM provider/model and budget; privacy stance on sending birth data to a third-party model.

---

## 8. Definition of Done (v1.0)

- Chart math passes oracle + reference tests; engine is Swiss and labelled truthfully.
- Birth datetime handled with IANA tz and historical DST; ambiguities flagged.
- Only verified rules appear in user-facing phaladesh; draft rules isolated.
- Every phaladesh sentence has provenance; grounding validator enabled by default.
- Schools separated; no cross-school averaged score.
- Security items B11/B12 closed; CI green with secret scanning.
- Methodology, limitations and rules-policy docs published.

---

## 9. Risks

| Risk | Mitigation |
|------|-----------|
| Rule verification is slow/expensive | Start with a small high-quality core; track progress; do not pad counts |
| Swiss licence/commercial terms | Decide early (Section 7.1) |
| Reference data unavailable | Use Swiss oracle for math; delay "verified" labels for dashas/bala until references arrive |
| LLM ignores constraints | Validator + template fallback; low temperature; regression red-team set |
| Scope creep (numerology, vastu, gemology, etc.) | Freeze auxiliary modules; mark `experimental`; revisit after v1.0 |
| Agent fabricates citations | Rule 0.1-2; review checks; lint rejects verse fields lacking an owner-supplied edition |

---

## 10. Suggested first prompts for Antigravity

**Phase 0**
> Read docs/IMPLEMENTATION_PRD.md. We are on Phase 0. Produce a task-by-task plan (files, tests, risks) and wait for my approval. Do not rewrite git history; only prepare docs/SECURITY_ROTATION.md.

**Phase 1**
> Phase 1. Start with P1-T1 and P1-T4: add pyswisseph, create the engine health check, and write the test that compares the PyEphem path against Swiss on 20 dates. Report the error table before changing any ephemeris logic.

**Phase 4**
> Phase 4. Implement P4-T1 and P4-T2 only. Do not edit any rule text. Produce docs/RULES_AUDIT.md and show me the top 30 name/condition mismatches.

