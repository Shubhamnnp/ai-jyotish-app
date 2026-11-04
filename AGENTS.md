# JyotishOS — Agent Non-Negotiable Rules & Protocol
Reference: `docs/IMPLEMENTATION_PRD.md` (Section 0.1)

## 0.1 Rules for the agent (non-negotiable)

1. **Work one phase at a time.** Before coding a phase, write a short plan (files to touch, tests to add), wait for owner approval, then implement. Do not start the next phase without approval.
2. **Never invent astrological content.** Do not write new rule text, sloka numbers, chapter/verse citations, or "reference" chart values from memory. Reference data comes only from (a) Swiss Ephemeris computed in this repo, or (b) files the owner places in `tests/reference/`. If something is missing, stop and ask.
3. **Never silently fall back.** If a precise engine is unavailable, raise a clear error or return the result with `engine_degraded=true` and a visible warning. No silent substitution.
4. **Tests first for math.** Every calculation change needs a test comparing against the oracle (Section 6) before the change is merged.
5. **Small commits.** One task ID per commit, message format `P1-T3: use zoneinfo for birth datetime`.
6. **Do not delete data without a backup branch.** Rule files are quarantined (status flag), not deleted, in Phase 4.
7. **No secrets in git.** Ever. See Phase 0.
8. After each phase, produce `docs/phase_reports/PHASE_N_REPORT.md`: what changed, tests run, known gaps.

## Standard Session Startup Protocol
Every session begins with:
1. Read `docs/IMPLEMENTATION_PRD.md`.
2. Identify the active Phase (e.g., Phase 0).
3. Produce the task-by-task plan for that phase only, listing files and tests, and wait for owner approval.
4. On approval, execute task by task, running `pytest -q` after each task.

