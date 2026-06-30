# Phase 1.3 Retro

**Phase:** 1.3 — Author disambiguation + demographic inference
**Stage:** 1 — Crawl
**Branch:** `phase-1.3-execution`
**Window:** 2026-06-29 (plan) → 2026-06-30 (execution + VERIFY)
**Status:** Complete. Demographic substrate delivered for v3 + v2.
Ready for Phase 1.4 (pre-Stage-2 quality gates).

---

## One-line summary

Built the demographic-annotation pipeline (Steps 1–6) as TDD functions
in `src/whitespace2/demographics.py`, then ran it end to end on the 1M v3
production sample (and the v2 robustness pair). It produces the **bias-
corrected demographic time series** the program exists to measure: CS
female share among latin-script authors rose **22.4% (1975) → 31.9%
(2025)**, tightly estimated and robust to both the §0 filter choice
(v2↔v3 within 1.4pp) and the correction axis (script vs country, parallel
trends). The §9e-style NamSor bias correction extends a probabilistic
gender to ~100% of authors from a 41.5% confident-direct base. H1, H2,
H4, H6, and H8 (on headline cells) pass cleanly; H3 is a documented near-
miss; E1 fired benignly on one population-limited stratum; E2 did not
fire. The keyed smoke caught an H5 metric bug before it could corrupt the
production run.

---

## What happened

### PLAN (`docs/phases/phase-1.3-plan.md`, commit `9d4926c`)

8 pre-registered hypotheses across three layers (A: disambiguation
correctness — H1, H2; B: coverage + bias estimation — H3–H6; C: output
validity — H7, H8), 4 escape triggers (E1–E4), 15 validation gates.
**Key methodology lock:** NamSor scope set to **Option B** — *sample-
based per-region bias estimation*, not direct labeling of every low-
confidence name. Direct labeling of ~190K names would cost $50–200 and
yield point estimates with no uncertainty; Option B costs ≤$10 and
produces principled per-region CIs that plug into the §9e four-layer
defense. (User-locked 2026-06-29.)

### IMPLEMENT — Steps 1–6, TDD (173 tests, ruff + mypy strict clean)

| Step | Function(s) | Commit |
|---|---|---|
| 1 / 1.5 | `extract_authorships` (streaming) + `source_type` | `ee776c0`, `1e5b627` |
| 2 | `validate_disambiguation` (H1 career screen, H2 ORCID) | `e4f805f` |
| 3a–c | `annotate_with_gender_guesser`, `aggregate_per_author`, Genderize x-val | `0b5cce0`, `652ad0f`, `09e919b`, `58907f0` |
| 4a–c | `tag_script_region`, `stratified_sample_names`, NamSor client, `sample_for_namsor` | `c140c12`, `975b281`, `c1a6fb1` |
| 5a | `compute_confusion_matrix` + `_wilson_ci` | `7d21408` |
| 5b | `apply_bias_correction` (script/country axis) | `4ab9e54` |
| 5c | `extract_primary_field`, `build_paper_field_map`, `build_cell_coverage_table` | `636308a` |
| 6 | `build_coverage_table` (coverage + diversity + CIs), `perturb_row_normalized` | `ab37967` |

The full Step 1→6 chain composes: `compute_confusion_matrix` →
`apply_bias_correction` → `build_paper_field_map` +
`build_cell_coverage_table` → `build_coverage_table`.

### VERIFY — smoke discipline, then the production run

- **Driver** `experiments/phase-1.3/run_pipeline.py` (`6e43902`) chains
  all steps, reads keys from `.env`, supports `--no-api` /
  `--reuse-matrix` / `--no-genderize`.
- **Smokes on 2000 real heldout papers** validated the chain end to end
  (`--no-api` zero-quota, then keyed). The keyed smoke **caught a real
  H5 bug** (`max_ci_halfwidth` pegged at 0.5 for every region by
  structurally-empty gg-confident rows → H5 unpassable by construction);
  fixed (`a213f42`) before the production run.
- **v3 1M production run** (`92aca3d`): 1,000,000 papers → 3.12M author-
  paper rows → 1.82M unique authors → 630 cells, 17 min local. Genderize
  2,200 / NamSor 2,300 names, 0 errors, $0.
- **Hypothesis evaluation** (full table in `verify-results.md`) +
  **E2 sweep** (`sensitivity_e2.py`).

### Robustness

- **v2/v3 pair** (`1599089`): v2 re-run reusing the v3 confusion matrix
  (§0-version-independent) — **zero new API quota**. CS female-share
  trend matches v3 within 1.4pp at every decade.
- **Axis sensitivity** (`15e0f52`, `sensitivity_axis.py`): script vs
  country correction give parallel trends (max diff 4.9pp = sparse-
  country confound).

---

## Surprises

1. **The H5 metric was unpassable by construction.** The confusion
   matrix's gg-male / gg-female rows are *always* empty — gg-confident
   names never enter the low-confidence NamSor sample — so their
   degenerate `_wilson_ci(0,0)=(0,1)` bands pinned `max_ci_halfwidth` at
   0.5 for every region. The unit tests missed it (fixtures populated
   all rows); only the keyed smoke on real data, where the low-conf
   subset is purely gg-unknown, exposed it. Fixed by excluding empty
   rows. **Smoke-before-bulk earned its place.**
2. **E1 fired, but for a population-limited stratum, not under-sampling.**
   `south_asian` half-width 0.33 (>0.10) because only **4 Devanagari-
   script names exist** in the 1M sample — South Asian names romanize
   into `latin` (well-corrected at n=606). The plan's E1 escalation
   ("expand the sample") is inapplicable; the right move was to diagnose
   and document, not escalate. The other 4 script regions pass at ≤4.3pp.
3. **Physics ≥ CS on early female share** (27.5% vs 22.4% in 1975),
   counter to the usual prior. Could be real subfield composition or a
   name-inference artifact on physics' heavier East-Asian name mix.
   Flagged for Stage-2 scrutiny; not obviously a bug.
4. **The §0 corpus has a pre-1970 mis-dated tail** (papers back to 1803
   with CS/physics tags — OpenAlex metadata errors; tiny cells). The §0
   filter screened junk-year *tokens in text*, not the `publication_year`
   field. Phase 1.4 / Stage 2 must year-bound to 1970–2024.
5. **The 1M-sample decision.** The plan said "24.5M corpus", but the
   full corpus (~32GB / ~75M author-paper rows) would OOM locally and
   need a Modal app, while Stage 2 actually embeds the **1M sample**.
   Running the demographic pipeline on the 1M sample matches the Stage-2
   population *and* is locally tractable — and H8 already passes on the
   headline cells, so the full corpus is deferred unless precision
   demands it. (User-locked "1M now, full later if needed.")

---

## Lessons (logged in `tasks/lessons.md`)

- **Measurement-unit composition.** A calibration kernel measured per-
  NAME composes cleanly only with stratifiers that are functions of the
  name (script); per-AUTHOR attributes (country) require a lossy
  projection — so script-region is the headline axis, country the
  robustness axis.
- **Don't pre-aggregate past the granularity downstream needs.** Step 3
  collapsed year/field away, so Step 5c had to re-join to paper-level
  data + a fresh concepts pass. Carry join keys; know the downstream
  cell definitions before collapsing.
- **Reuse established metric definitions.** `country_shannon` reuses
  Phase 0.1's Miller-Madow `demographic_shannon` for cross-phase
  consistency (re-implemented in `src`, not imported from `experiments`).
- **A metric over a structured object can be unpassable by construction**
  — exclude empty-by-construction cells, and test against the real
  sparsity pattern, not the happy fully-populated fixture.
- **Diagnose a fired escape trigger before invoking its escalation** —
  population-limited ≠ under-sampled; the pre-registered escalation may
  be a no-op.
- **You can't fairly test a stratification axis your calibration sample
  wasn't stratified on** — report the confound (country-correctable
  41.6% vs 99.97%) so a coverage artifact isn't misread as an axis
  effect; the robust takeaway is the parallel trend.
- **Aggregate precision ≠ individual certainty.** We don't claim to know
  any corrected author's gender; we estimate each cell's gender
  *composition* with quantified uncertainty (the §9e move).

---

## Validation gates check

Gates from `phase-1.3-plan.md` §"Validation gates". Status at retro:

| # | Gate | Status |
|---|---|---|
| 1 | All unit tests pass | ✅ 173 total (83 demographics) |
| 2 | Lint + typecheck clean | ✅ ruff + mypy strict |
| 3 | Local end-to-end smoke | ✅ `--no-api` smoke, 4.5s |
| 4 | Production smoke | ✅ keyed smoke (2000 real papers) — caught the H5 bug |
| 5 | H1 cross-era-merger ≤ 5% | ✅ 0.014% |
| 6 | H2 ORCID agreement ≥ 95% | ✅ 99.62% |
| 7 | H3 gender coverage ≥ 45% | 🟡 41.5% confident (near-miss; ~100% post-correction) |
| 8 | H4 country coverage ≥ 50% | ✅ 71.9% |
| 9 | H5 per-region CI ≤ 10pp | 🟡 4/5 regions pass; south_asian E1 (population-limited, benign) |
| 10 | H6 NamSor spend ≤ $10 | ✅ $0 |
| 11 | H7 per-headline-cell NamSor ≥ 10 | 🟡 4 regions 476–607; south_asian = 4 (E3, benign). Per-CELL eval deferred to 1.4 |
| 12 | H8 CI half-width ≤ 2.5pp | ✅ max 1.48pp on cells n≥1000 |
| 13 | Both v3 + v2 corpora annotated | ✅ `data/metadata/v{3,2}-coverage-table.parquet` |
| 14 | Reproducibility: seeds + manifests committed | ✅ confusion matrix, run summaries, seeds, commands in verify-results |
| 15 | Retro committed | ✅ this document |

11 of 15 clean. The three 🟡 are all on the demographic-coverage gates
(H3, H5/H7 south_asian) and all reduce to the **same root fact**:
non-Western names are sparse where the inference is weakest. None
compromise the headline — H3 is handled by the §9e correction, and the
south_asian stratum is empirically negligible (captured in `latin`).
Escape triggers: **E1 fired** (south_asian, benign), **E2 NOT fired**
(~13% << 30%), **E3** (south_asian cells, benign), **E4 NOT fired**
(0 NamSor errors).

---

## Methodology amendments locked through Phase 1.3

- **NamSor Option B** — sample-based per-region bias estimation, not
  direct labeling. ≤$10 (actual $0); principled per-region CIs feed the
  §9e correction. (Amends Phase 0.2 Check 3's "escalation on the low-conf
  subset" framing.)
- **H5 metric** — `max_ci_halfwidth` excludes structurally-empty gg rows
  (only the evidenced gg-unknown row, which `apply_bias_correction`
  actually uses, counts). Codified in `compute_confusion_matrix`.
- **Both-unit aggregation** — every cell reported under `distinct_authors`
  (headline, per-capita) AND `appearances` (robustness). They barely
  differ (2024 CS: 0.3187 vs 0.3164).
- **Demographic run population** — the **1M production sample** (matches
  Stage 2's embedded set + locally tractable), not the full 24.5M corpus.
  Full-corpus run deferred unless headline-cell precision demands it.
- **`country_shannon`** reuses Phase 0.1's Miller-Madow Shannon over
  `primary_country` (cross-phase metric consistency).

---

## What carries to Phase 1.4

1. **Year-bound the corpus to 1970–2024** before the headline test — the
   §0 sample has a pre-1970 mis-dated tail (back to 1803).
2. **Scrutinize the physics ≥ CS early-female finding** — real subfield
   effect or name-inference artifact?
3. **Per-cell H7** — the driver reports NamSor sample per *region*; the
   per-(year×field×region)-cell count for headline cells is a 1.4 check.
4. **Optional: a country-stratified NamSor sample** if a clean country-
   axis estimate is wanted (the current axis sensitivity is confounded
   by the script-stratified sample).
5. **Deliverables in hand:** `data/metadata/v{3,2}-coverage-table.parquet`
   (630 / 776 cells × 2 units), `v3-confusion-matrix.json` (reusable
   kernel), `v3-sensitivity-{e2,axis}.json`, `v{3,2}-run-summary.json`.

---

## Companion documents

- Plan: `docs/phases/phase-1.3-plan.md`
- VERIFY results: `experiments/phase-1.3/verify-results.md`
- Driver + sensitivity: `experiments/phase-1.3/{run_pipeline,sensitivity_e2,sensitivity_axis}.py`
- Pipeline code: `src/whitespace2/demographics.py` (~2570 lines)
- Tests: `tests/test_demographics.py` (83 tests)
- Lessons: `tasks/lessons.md`

---

## Phase 1.3 → Phase 1.4 transition signoff

Phase 1.3 delivers the **demographic substrate** for Stage 2: per-(year ×
field × region) coverage tables with bias-corrected gender (+CIs),
geographic diversity, and confidence/coverage characterization, on both
the v3 and v2 corpora, plus the reusable per-region bias kernel. The
headline demographic-plurality series (rising CS female share) is
established, precise on the headline cells, and robust to the §0 filter
and correction axis.

Phase 1.4 runs pre-Stage-2 sanity gates on this substrate (year-bound,
field-intuition checks, per-cell H7) and signs off the Stage 1 → Stage 2
transition. No methodology amendments are needed at the 1.3 → 1.4
boundary; all Phase 1.3 locks survive. Stage 2 then computes the semantic
plurality series and runs the pre-registered divergence test — the
question this whole program is built to answer: did semantic plurality
track the demographic rise, or decouple from it?
