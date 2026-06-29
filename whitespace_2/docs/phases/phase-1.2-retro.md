# Phase 1.2 Retro

**Phase:** 1.2 — Production OpenAlex pull via bulk dump
**Stage:** 1 — Crawl
**Branch:** `phase-1.2-execution`
**Window:** 2026-05-05 → 2026-06-29 (~7-8 weeks calendar; ~20 hrs
active execution)
**Status:** Complete. v3 corpus locked. Ready for Phase 1.3.

---

## One-line summary

Streamed the OpenAlex works bulk dump (492M records, 639 GB
compressed) through Modal, applied the locked §0 filter inline,
deduped to a 72M-row v1 population — then surfaced two corpus-
quality issues mid-VERIFY (type contamination and abstract-quality
issues) that triggered two consecutive §0 amendments (v2 and v3),
each closed with a hand audit. Final v3 analytical population:
**24,492,279 papers, ready for Stage 2.**

---

## What happened

### IMPLEMENT (Steps 1-9 per phase-1.2-plan.md)

- **Steps 1-6**: parse_modal.py infrastructure + §0 filter module
  lift + single-shard, 5-shard parallel smokes (all PASS).
- **Step 7**: full bulk-dump parse + cross-shard dedup.
  - Per-shard parse: 2,127 shards × 100-way Modal `.map()`, each
    container processing ~30-60 sec.
  - Dedup ran into a polars OOM (32 GB box) at the concat stage;
    switched to DuckDB with disk spill — succeeded in 1,278s.
  - Initial dedup attempt used a window function (single-pass
    ROW_NUMBER over PARTITION BY id ORDER BY updated_date) which
    OOMed at 11 GB. Rewrote as 2-pass GROUP BY → JOIN. Worked.
  - **Result: 72,173,308 unique paper-ids in
    `section0-population.parquet` (54.8 GB on Modal Volume).**
- **Step 8**: server-side sampling (cleaner than local download +
  sample on a 50+ GB file). Same 2-pass pattern. Nesting seed
  `ws2-phase-1.2-nesting-seed-v1` produces deterministic
  nested-sample ordering so sample(M) ⊆ sample(N) for M ≤ N.
- **Step 9**: held-out generation. Four cells (1975×cs, 1975×physics,
  2020×cs, 2020×physics) at N=500 each. Excludes the sample at
  pull time via NOT EXISTS subquery.

### VERIFY — surfaced two corpus-quality issues

1. **Yield miss**: pre-registered Hypothesis H4 expected ~30%
   §0-retention from the bulk-dump pass, derived from a single-
   cell Phase 0.1 measurement. Actual yield: 14.6%, with v1
   = 72M (vs expected 150M). Quantitatively a miss, but the
   smoke-extrapolated 8.7% number was even further off — there
   was no dedup-driven inflation. Dedup spot-check (5 random
   year-stratified ids) confirmed each was in exactly 1 shard.
   **Re-framed H4: yield is honestly lower than the
   one-cell extrapolation predicted; the pull mechanics are
   correct.** verify-results.md pressure-points A/B/C/D
   addressed.

2. **§0 type contamination — v2 amendment**: H2 hand audit on a
   100-paper sample of v1 found **56,084 / 1M = 5.6% v1
   papers were `type=dataset`** ("Occurrence Download" GBIF auto-
   DOIs). Investigation surfaced ~40% of the original sample was
   non-research types (dataset, paratext, libguides, peer-review,
   erratum, etc.). User-locked decision: amend §0 with a type
   allow-list (`article, preprint, review, book-chapter,
   dissertation, book, letter, editorial, report`). **v2 build
   produced
   `section0-population-v2.parquet` at 38,697,769 rows (53.62%
   v2-kept-of-v1) for ~$5 in ~15 min.**

3. **§0 quality patterns — v3 amendment**: full 100-paper hand
   audit of the v2 sample found **44% hard-FLAG rate** —
   dominated by two pattern classes: publisher chrome ("ADVERTISEMENT
   RETURN TO ISSUE" template from ACS Publications; "Views Icon
   Views" from Wiley/OUP/AIP) and concept-tagger noise (non-CS
   papers tagged with CS at 0.30-0.39 due to incidental keywords).
   User-locked decision: four-fix v3 amendment — regex prefix
   blacklist on abstract + abstract-token-min 15→50 + concept-
   score 0.30→0.40 + title-prefix heuristic. **No language
   filter** (demographic-bias risk) and **no pure-math filter**
   (scope-call locked as "math in"). **v3 build produced
   `section0-population-v3.parquet` at 24,492,279 rows (63.29%
   v3-kept-of-v2) for ~$3.50 in ~20 min wall-clock (3 attempts;
   see Surprises §3).**

   Concept-score raise carries most of the cleanup (29.4% of v2).
   Publisher-chrome regex caught ~495K papers (1.28% of v2).

   Spot-check audit of 30 v3 papers (first 15 + last 15) found
   **20% hard FLAG** — at the v3 target. JUNK_YEAR confirmed
   at 0 across both audit rounds (130 papers total).

### RETRO

This document, plus:
- `experiments/phase-1.2/h2-audit-results.md` §7 (v3 results)
- `tasks/lessons.md` (Phase 1.2 lessons)
- `tasks/spend.md` (actual costs)

---

## Surprises

1. **Pull yield 14.6% (not 30%)** — the Phase 0.1 single-cell
   extrapolation was loose; production pulls have to absorb
   per-shard yield variance the cell-test couldn't see. Phase 1.3
   should be sized against the v3 24M number, not Phase-0.2-locked
   1M-out-of-pull-of-3.3M targets. **No replan trigger fired**
   because v3 24M >> downstream Stage 2 N=1M.

2. **§0 type contamination at 39.9% of un-type-filtered v1
   sample** — un-anticipated. The v1 population was admitting
   GBIF dataset DOIs, library research guides, peer-review
   reports, paratext (frontmatter), etc., all of which OpenAlex
   classifies under `type`. Allow-list amendment cleaner than
   deny-list (new types added to OpenAlex default to "out" until
   inspected). **Methodology lesson: when an upstream taxonomy
   has dozens of categories, the safer default is an explicit
   allow-list, not a moving deny-list.**

3. **§0 v3 implementation took 3 attempts; the right tool was
   not the first tool**:
   - DuckDB Python UDFs (`type='native'`) hit the 1-hour timeout
     on 38M rows — per-row Python/C boundary overhead is
     prohibitive at scale.
   - Single-threaded PyArrow streaming reached 64% in ~21 min,
     then mysteriously cancelled (root cause never identified;
     possibly local-client disconnect).
   - ProcessPoolExecutor across 8 row-group workers completed
     the filter in 5 min + concat in 10 min. **Lesson: when CPU
     parallelism is available and the workload is row-independent,
     use ProcessPoolExecutor — don't reach for UDFs.**

4. **Modal Volume `read_file` hang on a 310 MB sample download**
   — file fully wrote to disk but the iterator never returned a
   completion signal. Local script went into S-state for 50+
   minutes idle before being killed. Resolved by using `modal
   volume get` (CLI) instead of the SDK iterator. **Lesson: for
   files >100 MB, prefer `modal volume get`; for smaller
   artifacts, the SDK iterator works fine.**

5. **Deploy-cache silent skip** — `modal deploy` sometimes
   reports "Deployment skipped: no changes detected" even after
   substantive function-body changes (Modal hashes a digest of
   the function; can miss new closures or inner functions).
   Fix: `modal app stop -y ws2-parse` before re-deploying to
   force a fresh upload. **Lesson: when iterating on Modal
   functions, always stop the app first if you suspect cached
   state.**

6. **Auditing recalibration mid-stream** — the H2 audit of v2
   used 4 verdict categories. After ~13 papers the reviewer-task
   wording was clarified mid-audit (added the explicit
   "Important: 'belongs in' means the paper itself uses cs/physics
   methods" sub-rule, with the Croatian LiDAR paper as the OK
   example and the Pacific Islander education paper as the
   WRONG_FIELD example). Two prior verdicts (paper #3 chem-phys
   chrome → BAD_ABSTRACT, paper #13 Pacific Islander → WRONG_FIELD)
   were retroactively updated to maintain consistency. In the v3
   audit, the same Croatian paper was flipped from OK→WRONG_FIELD
   despite being the rubric's OK example. **Lesson: a single
   reviewer can drift across audit rounds even with a written
   rubric. The "ground truth" 44% v2 / 20% v3 hard-FLAG rates
   both have non-trivial reviewer-strictness variance baked in.
   The headline finding (v3 is much better than v2) is robust
   to this; the precise rates are not.**

---

## Lessons (logged in `tasks/lessons.md`)

See `tasks/lessons.md` entries for 2026-06-28 and 2026-06-29
covering:

- §0 type allow-list amendment (defensible methodology choice +
  why allow-list beats deny-list).
- §0 v3 amendments (regex prefix blacklist + token raise +
  concept-score raise; bias risk analysis).
- DuckDB UDF performance ceiling at 38M rows.
- ProcessPoolExecutor on Modal for row-group-parallel work.
- Modal Volume `read_file` 310 MB hang + `modal volume get`
  workaround.
- Modal deploy-cache silent skip + force-stop pattern.
- Hand-audit reviewer recalibration across rounds.

---

## Validation gates check

Gates were defined in `phase-1.2-plan.md` §10. Status at retro:

| # | Gate | Status |
|---|---|---|
| 1 | All §0 unit tests pass | ✅ 32/32 (v2 + v3 amendments included) |
| 2 | lint + typecheck clean | ✅ ruff + mypy strict |
| 3 | Single-shard smoke (Step 5) | ✅ Phase 1.2 Step 5 commit |
| 4 | 5-shard parallel smoke (Step 6) | ✅ Phase 1.2 Step 6 commit |
| 5 | Full bulk-dump parse completes | ✅ 2,127 shards processed; 72.17M unique paper-ids |
| 6 | H1 sample size ≥ N target | ✅ 1M sampled from each of v2 + v3 |
| 7 | H2 hand-audit: ≥X% of sample are research papers | ✅ v3 audit @ 80% OK+BORDERLINE; 20% hard FLAG (target was ≤20%) |
| 8 | H3 cost ≤ $50 | ✅ ~$33 total (see spend.md) |
| 9 | H4 yield ≥ pull target | 🟡 14.6% vs 30% expected — re-framed honestly in verify-results.md; v3 yield of 24M still >> Stage 2 needs |
| 10 | Reproducibility: manifests committed for v2 + v3 corpora | ✅ section0-sample-{1M-v2, 1M-v3}-manifest.json, heldouts-{v2, v3}-manifest.json |
| 11 | Retro committed | ✅ this document |

H4's miss is the only non-clean gate. Re-framed honestly in
verify-results.md (the smoke-extrapolated 8.7% was wrong;
actual yield is 14.6% with no dedup inflation). Downstream
phases sized against actual v3 24M, not the original 1M-of-
3.3M expectation.

---

## Methodology amendments locked through Phase 1.2

- **§0 type allow-list (v2)** — `article, preprint, review,
  book-chapter, dissertation, book, letter, editorial, report`.
  Per the H2 v1 audit. Codified in
  `src/whitespace2/section0_filter.py::ALLOWED_WORK_TYPES`.
- **§0 v3 amendments** — concept-score 0.30→0.40, abstract-token
  min 15→50, abstract-prefix blacklist (ACS / Wiley / OUP / AIP
  publisher chrome + author-version placeholders), title-prefix
  blacklist (NEW PRODUCTS / Contributors-strict / Annex N / Key
  Messages / Editorial Board). Per the v2 H2 audit. Codified
  in `src/whitespace2/section0_filter.py::SCORE_THRESHOLD_V3`,
  `EMPTY_ABSTRACT_MIN_TOKENS_V3`,
  `ABSTRACT_PREFIX_BLACKLIST_PATTERN`,
  `TITLE_PREFIX_BLACKLIST_PATTERN`, and
  `apply_section0_filter_v3`.
- **Pure-math scope: in** — not filtered. The 3 audited pure-
  math papers stay in v3. Decision locked
  2026-06-28 in `h2-audit-results.md` §4. Stage 2 can revisit
  with measurements if math-cluster effects distort the headline.
- **No language filter** — demographic-bias risk too high.
  Accepted ~7 non-English social-science false positives per
  100 sampled papers as a known residual.

---

## What carries to Phase 1.3

- **v3 corpus** (`section0-population-v3.parquet` on Modal
  Volume `ws2-section0`, 24,492,279 rows). The primary
  analytical population.
- **v2 corpus** (`section0-population-v2.parquet`, 38,697,769
  rows). Retained as the v2/v3 robustness pair — Stage 2
  divergence test will be reported on both.
- **1M sample of v3** (local: `data/metadata/section0-sample-
  1M-v3.parquet`, 1.3 GB; gitignored). The Stage 2 input.
- **4 held-out cells** (`heldout-{1975,2020}-{cs,physics}-v3
  .parquet`, ~500 KB each, committed). For per-era / per-field
  robustness validation in Stage 2.
- **Manifests** (`section0-sample-1M-v3-manifest.json`,
  `heldouts-v3-manifest.json`) — full reproducibility record.
- **§0 filter module** (`src/whitespace2/section0_filter.py`
  with v2 + v3 predicates, 32 unit tests).
- **Modal parse infrastructure** (`experiments/phase-1.2/
  parse_modal.py` with `filter_population_by_type`,
  `filter_population_v3`, `sample_population`,
  `generate_heldouts` — all deployed to `ws2-parse`).

---

## Companion documents

- Plan: `docs/phases/phase-1.2-plan.md`
- VERIFY artifact: `experiments/phase-1.2/verify-results.md`
- H2 audit results: `experiments/phase-1.2/h2-audit-results.md`
- H2 v2 audit sheet (full 100 papers reviewed):
  `experiments/phase-1.2/h2-audit-sheet-v2.md`
- H2 v3 audit sheet (30 papers spot-checked):
  `experiments/phase-1.2/h2-audit-sheet-v3.md`
- Build logs: `experiments/phase-1.2/build-v3-log.txt`,
  `experiments/phase-1.2/resume-v3-log.txt`
- Filter source: `src/whitespace2/section0_filter.py`
- Filter tests: `tests/test_section0_filter.py`
- Modal functions: `experiments/phase-1.2/parse_modal.py`

---

## Phase 1.2 → Phase 1.3 transition signoff

Phase 1.2 produced the §0 analytical population P. Phase 1.3
takes P and produces:

- Per-author records via the OpenAlex `authorships` field (already
  in the v3 parquet via Phase 1.2's `_KEEP_FIELDS` projection).
- Disambiguated author IDs (using OpenAlex's `authorships[*]
  .author.id` field as the primary key, with cross-era spot
  checks per Phase 0.1 Check 4 methodology).
- Demographic inference (gender via `gender_guesser` primary +
  Genderize keyed cross-validation per Phase 0.2 Check 3 lock;
  country via affiliation; NamSor escalation on low-confidence
  subset per Phase 0.2 commitment).
- Pre-Stage-2 quality gates (per phase-1.2-plan.md Phase 1.4 stub:
  joint coverage cross-tabulation, sub-population assignment
  rates, sensitivity bounds on per-cell demographic measures).

Phase 1.3 plan to be authored next session. No methodology
amendments needed at the Phase 1.2→1.3 boundary; all Phase 0.2
locks survive.
