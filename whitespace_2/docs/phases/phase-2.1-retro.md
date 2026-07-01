# Phase 2.1 Retro

**Phase:** 2.1 — Stage-2 metric machinery + base 1M embed
**Stage:** 2 — Walk (first execution phase)
**Branch:** `phase-2.1-execution`
**Window:** 2026-06-30 → 2026-07-01 (plan committed prior session; execution one session)
**Status:** Complete. **All 6 acceptance gates pass.** Ready for Phase 2.2.

---

## One-line summary

Built the three Stage-2 metrics that didn't exist in `src/` — the §11
temporally-stratified cluster fit, the career-stage joint demographic
plurality, and the citation-age-robust canonical control — all TDD, and ran
the base 1M v3 embed (SciNCL + Qwen3) with the Qwen3 long pole parallelized
via Modal `.map()`. Phase 2.2 can now go straight to computing the three
series and running the pre-registered divergence test.

---

## What happened

### WS4 — parallel embed path + base 1M embed (commits `5dd4ad4`, `487e631`, `<ws4-embed>`)

The one real engineering task. `ChunkedEmbedRunner.run_mapped(abstracts,
map_fn)` fans not-yet-done chunks across Modal containers via an
order-preserving `fn.map` while preserving the exact resumable chunk-to-disk
contract of the sequential `run()` (skip valid done chunks, re-dispatch
missing/corrupt, concat in chunk-id order, incremental save). +8 runner tests
(clean / uneven / resume-only-missing / interop-with-`run()` / corrupt / empty
/ shape-mismatch / **per-chunk-failure tolerance**).
`experiments/phase-2.1/embed_1m.py` drives it.

**Base 1M embed** (902,531 in-window 1970–2024 papers; cs 645,721 / physics
256,810):
- **SciNCL**: mean norm 23.70 (band [22.5, 24.5]), all finite, **~8 min
  wall-clock** via `.map()` (vs ~50 min sequential), ~$2.
- **Qwen3**: mean norm **1.000** (band [0.99, 1.01]), all finite, ~40 min
  wall-clock — bs=1 cross-family, parallelized via `.map()` (the ~10 hr
  sequential long pole collapsed to wall-clock-parallel at unchanged
  GPU-seconds), ~$15.3. **Total embed ~$17.3** (under the ~$19 pre-commit).

**Production hardening (commit `487e631`).** The first full run died at chunk
250: one Qwen3 Modal call exhausted its 3 retries on a transient error and the
ordered `.map()` raised there, discarding the concurrently-completed later
chunks. Chunk-250 data verified clean (max 9,992 chars / 4,694 tokens ≪ 32K
context) → transient, not data. Fixed: `run_mapped` skips exception results
(`fn.map(return_exceptions=True)`), persists every good chunk, and raises a
resume-needed error if any remain — so a resume re-dispatches ONLY the missing
chunks. The resumed run swept 250 → 903 in a single clean pass.

### WS1 — §11 cluster fit in `src/` (commits `9900e0d`, `e701a9a`)

`src/whitespace2/cluster_fit.py`: `build_decade_stratified_sample` (equal
papers/decade, 6 bins) + `fit_clusters` (locked K=50 / n_init=20 /
random_state=46 / max_iter=300) + `project_to_clusters` (Euclidean
`argmin‖v−c‖² = argmax(2·v·c − ‖c‖²)` — the Phase-0.2 Wave-2A cosine-bug fix).
+11 tests, incl. `project_to_clusters == KMeans.predict` and a **differing-norm
divergence guard** proving the buggy cosine criterion genuinely disagrees (so
the equivalence test isn't vacuous).

**Production fit** on the base 1M SciNCL vectors (60K decade-balanced sample):
cluster_entropy 3.859, **effective 47.4 / 50 clusters, 0 empty, max cluster
share 3.7%**. Cross-check vs the committed Phase-0.2 |S|=1,500 SciNCL centroids:
consistent structure (no empty clusters, ~16K median), and the 60K fit resolves
the small-sample fit's dominant/near-empty clusters (min 65→5,596; max share
8.7%→3.7%). See `experiments/phase-2.1/section11-production-fit-results.md`.

### WS2 — career-stage joint demographic plurality (commit `6f308e4`)

`_join_cells` conditionally carries `min_year` (survives
`apply_bias_correction`; read only when present — same pattern as
`primary_country`). `build_coverage_table` adds `career_bin = year − min_year`
(0-5 / 6-15 / 16+) and the **pre-registered joint gender × country ×
career-stage plurality** per cell: MM Shannon + Gini-Simpson (`1 − Σpᵢ²`), each
author's soft `corrected_p_{male,female}` mass spread over their (country,
career-bin); null unless the corrected parquet has both `primary_country` and
`min_year`. +4 tests (bins, hand-computed joint, partial coverage,
null-when-no-min_year).

### WS3 — age-restricted canonical metric + pre-reg amendment (commit `6857276`)

`age_restricted_concentration`: per-publication-year Gini + top-k on only the
years whose papers are ≥ `min_age` years old at the snapshot, dropping the
zero-inflated immature recent tail (pilot finding #1). No pull — uses the
`cited_by_count` + `publication_year` already in the corpus. **Amended
`phase-2.0-plan.md`**: the fixed N-year window is DROPPED (`counts_by_year`
unreconstructable pre-~2015), age-restriction committed with an N∈{3,5,10}
sweep + the residual-accrual-gradient caveat. +6 tests.

---

## Surprises / findings

1. **`.map()` collapsed the long pole cheaply.** The plan budgeted the Qwen3
   parallelization as "the one real engineering task"; in practice a single
   order-preserving `run_mapped` method (reusing every existing disk
   primitive) did it. SciNCL 1M went 50 min → 8 min as a side benefit. Cost is
   parallelism-invariant (same GPU-seconds), so the win is pure wall-clock.
2. **The larger balanced fit sample is strictly better.** The §11 principle is
   decade *balance*, but the committed Phase-0.2 fit (1,500) still carried
   small-N artifacts (one cluster with 65 of 902K papers; max share 8.7%). The
   60K-balanced production fit removed both while reproducing the validated
   structure — sample size still matters for K=50 centroid stability even
   after balancing.
3. **Centroid norm mean 0.887**, slightly below the Phase-0.2 "~0.92–0.94"
   note — expected: more (and more diverse) papers per cluster → more spread →
   lower centroid norms. Not a defect; it's exactly why the Euclidean (not
   cosine) projection is mandatory.
4. **`.map()`'s fail-fast default is a production hazard.** The base-1M Qwen3
   run died at chunk 250 on a single transient Modal failure — the ordered
   `.map()` raises on the first exhausted-retries input and discards all the
   concurrently-completed later chunks. `return_exceptions=True` + skipping
   exception results in `run_mapped` turned a whole-run abort into a
   skip-and-resume; the resumed run finished in one pass. The resumable
   chunk-to-disk contract, built in Phase 1.1 for preemption, is what made the
   recovery a non-event.

---

## Validation gates check

| # | Gate | Acceptance | Result |
|---|---|---|---|
| 1 | §11 cluster-fit in `src/` | tests pass; projection == `KMeans.predict`; decade-balance correct | ✅ 11 tests; == predict; balance verified |
| 2 | Career-stage joint plurality | joint Shannon + Gini-Simpson per cell; tests pass | ✅ 4 tests, hand-computed joint |
| 3 | Age-restricted canonical | tests pass; `phase-2.0-plan.md` amended | ✅ 6 tests + amendment |
| 4 | 1M embed clean | norms in band, finite, ~$19, resumable | ✅ SciNCL 23.70 / $2; Qwen3 1.000 / $15.3; all finite; ~$17.3 total; resumability exercised (survived a mid-run failure) |
| 5 | §11 production fit runs on 1M | distribution sane; cross-checks committed centroids | ✅ effective 47.4/50, 0 empty; cross-check consistent |
| 6 | Tests + lint/typecheck clean; §9 pre-commit written | ruff + mypy strict | ✅ 216 pass / 1 skip; ruff + mypy clean; pre-commit in `spend.md` |

---

## Lessons (logged in `tasks/lessons.md`)

- Order-preserving `.map()` + a disk-resume contract = a small, testable
  parallelization of an embarrassingly-parallel embed; results zip back to
  chunk-ids with no index threading.
- An equivalence test for a bug fix needs a companion test that the buggy and
  fixed criteria genuinely diverge, else the equivalence can pass vacuously.
- Gate a pipeline extension's new optional input on schema presence
  (`min_year` like `primary_country`) so existing fixtures stay green.

---

## Cost

Base 1M embed: SciNCL ~$2.00 + Qwen3 ~$15.34 + `.map()` smoke ~$0.01 ≈
**~$17.4** (under the ~$19 pre-commit). Some extra transient GPU-seconds were
spent on the crashed-run's cancelled in-flight chunks, but the summary
estimates bill only the persisted work; call it ≤~$19 all-in. Program total
~$52. Well under the §9 $500 cap.

---

## Phase 2.1 → 2.2 transition

Phase 2.2 has all four inputs: the §11 production centroids
(`data/metadata/section11-prod-fit-K50-scincl-1m.npy`), the career-stage joint
plurality + age-restricted canonical metrics in `src/`, and the base 1M
SciNCL + Qwen3 embeddings. Next: compute the 3 annual series (§11-stratified)
and run the pre-registered divergence test (`phase-2.0-plan.md` §5) on CS then
Physics.

## Companion documents

- Plan: `docs/phases/phase-2.1-plan.md`
- Pre-registration: `docs/phases/phase-2.0-plan.md`
- Production fit: `experiments/phase-2.1/section11-production-fit-results.md`
- Embed results: `experiments/phase-2.1/embed-1m-results.md`
