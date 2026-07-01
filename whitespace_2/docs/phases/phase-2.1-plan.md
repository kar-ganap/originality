# Phase 2.1 Plan — Stage 2 metric machinery + base 1M embed

**Stage:** 2 — Walk
**Phase:** 2.1 — first Stage 2 execution phase
**Window opens:** 2026-06-30
**Branch:** `phase-2.1-execution` (cut from `main` post-Phase-1.4 merge, PR #10)
**Status:** Plan locked. TEST → IMPLEMENT → VERIFY → RETRO discipline.

---

## Stage 2 (Walk) — overview (per `docs/phases/phase-2.0-plan.md`)

| Phase | One-line scope | Status |
|---|---|---|
| **2.1** | **Stage-2 metric machinery (§11 fit, career-stage, age-canonical) + base 1M embed** | **CURRENT — this plan** |
| 2.2 | Compute the 3 annual series + run the pre-registered divergence test (CS + Physics) | Stub |
| 2.3 | Robustness sweep (model swap, v2, unit, domestic-only) | Stub |
| 2.4 | 3-panel + residual figures; paper draft | Stub |

---

## One-line scope

Build the three Stage-2 metrics that don't yet exist in `src/` — the §11
temporally-stratified cluster fit, the career-stage joint demographic
plurality, the citation-age-robust canonical concentration — all TDD, and run
the base 1M v3 embedding (SciNCL + Qwen3) that every downstream metric needs.

---

## Why this phase exists

The pre-registered divergence test (`phase-2.0-plan.md`, §5) needs three
inputs that the Phase-1.4 100K pilot proved are non-trivial: a §11-stratified
cluster fit (the cluster-entropy metric is invalid without it), a
citation-age-robust canonical negative control (raw citation Gini is
accrual-confounded), and the realized demographic plurality (gender × country ×
career-stage). None exist in `src/` yet, and the whole test runs on embeddings
we haven't produced at 1M scale. Phase 2.1 delivers all four so Phase 2.2 can
go straight to computing the series + running the test.

**Locked decisions (user, 2026-06-30):** scope = prereqs + base embed;
canonical control = **age-restricted** (no data pull — `counts_by_year` isn't
in the corpus and likely doesn't reach back to 1970, so a fixed-window metric
is infeasible for old papers).

---

## Workstreams

### WS1 — Productionize the §11 cluster-fit (`src/whitespace2/cluster_fit.py`, TDD)

Lift from `experiments/phase-0.2/section11_production_validation.py` (only the
scorer `cluster_entropy` is in `src/` today):
- `build_decade_stratified_sample(years, n_per_decade, seed)` — 6 decade bins
  `(1970-1980)…(2020-2025)`, equal papers/decade (the §11 balance).
- `fit_clusters(vectors, k=50, n_init=20, random_state=46, max_iter=300)` — on
  L2-normalized vectors → centroids (locked params).
- `project_to_clusters(vectors, centroids)` — the KMeans-consistent Euclidean
  projection `argmin‖v−c‖² = argmax(2·v·c − ‖c‖²)` (NOT argmax-cosine — the
  Phase-0.2 bug). **Test: == `KMeans.predict` on a fitted model.**
- Then run the **production fit** on the WS4 SciNCL 1M vectors (decade-balanced
  fit → centroids → project all 1M → assignments) + cross-check the committed
  Phase-0.2 SciNCL centroids (`data/metadata/section11-cluster-fit-*-scincl.npy`).

### WS2 — Career-stage joint demographic plurality (`demographics.py`, TDD)

- Add `"min_year"` to `_join_cells`'s `corrected_cols` (already in the
  per-author table; survives `apply_bias_correction`; just not read).
- `career_stage = year − min_year`, binned **0–5 / 6–15 / 16+**.
- In `build_coverage_table`'s per-cell loop, add a **joint (gender × country ×
  career-stage) plurality**: joint Shannon (`_shannon_entropy_mm`) +
  **Gini-Simpson** `1 − Σpᵢ²`. Each author spreads their soft `corrected_p_g`
  mass across their `(country, career-bin)` → the joint (g,c,s) distribution.

### WS3 — Age-restricted canonical metric (`canonical_metrics.py`, TDD) + pre-reg amendment

- Age-restricted concentration: Gini / top-k per publication year **only on
  papers ≥ N years old** (drop the immature recent years; report N-sensitivity).
  Uses the total `cited_by_count` + `publication_year` already in the corpus —
  no pull.
- **Amend `phase-2.0-plan.md`** (still before any full-data test): canonical
  control = age-restricted (fixed-window dropped — `counts_by_year`
  unreconstructable pre-~2015), with the N-floor + residual-gradient caveat.

### WS4 — Base 1M v3 embed (Modal) + §9 pre-commit

- Embed the full **1M v3** sample (local in scratchpad) with **SciNCL (primary)
  + Qwen3 (cross-family)** via the deployed `ws2-embed` + `ChunkedEmbedRunner`
  (validated at 100K). `experiments/phase-2.1/embed_1m.py`.
- **Parallelize the long pole:** SciNCL 1M ≈ 50 min; Qwen3 bs=1 ≈ **~10 hrs**
  sequential → dispatch chunks concurrently via Modal `.map()` / multiple
  A100s (the one real engineering task; preserve the resumable chunk-to-disk
  contract).
- **§9 pre-commit** (`tasks/spend.md`) written BEFORE running.

---

## Pre-registered acceptance gates

| # | Gate | Acceptance |
|---|---|---|
| 1 | §11 cluster-fit in `src/` | tests pass; projection == `KMeans.predict`; decade-balance correct |
| 2 | Career-stage joint plurality | joint Shannon + Gini-Simpson per cell; tests pass |
| 3 | Age-restricted canonical | tests pass; `phase-2.0-plan.md` amended |
| 4 | 1M embed clean | norms in band (SciNCL ~[22.7,24.4], Qwen3 ≈1.0), finite, ~$19, resumable |
| 5 | §11 production fit runs on 1M | assignment distribution sane; cross-checks committed centroids |
| 6 | Tests + lint/typecheck clean; §9 pre-commit written | ruff + mypy strict |

---

## IMPLEMENT order

WS1–WS3 are independent local TDD (parallelizable). **WS4's embed is the long
pole — start it early / background.** WS1's *production fit* needs WS4's SciNCL
vectors, so: build WS1 code → run WS4 SciNCL → run the WS1 fit.

---

## Risks + mitigations

| # | Risk | Mitigation |
|---|---|---|
| R1 | Qwen3 1M ≈ 10 hrs sequential | Modal `.map()` fan-out across A100s; resumable chunks |
| R2 | §11 projection drift from Phase 0.2 | test `project_to_clusters` == `KMeans.predict`; cross-check committed centroids |
| R3 | Soft-gender × hard-country/career joint is ambiguous | spread `corrected_p_g` mass across observed (country, career-bin); documented |
| R4 | Age-restriction still leaves a residual accrual gradient | report N-sensitivity; the control's job is directional (concentration rises on mature decades) |

---

## Cost

Base 1M embed ≈ **$19** (SciNCL ~$2 + Qwen3 ~$17). WS1–3 + fit: $0. Under the
§9 $50 gate individually, but the pre-commit is written (full Stage 2 ~$77).
Running total ~$56.

---

## Companion documents

- Stage 2 plan + pre-registration: `docs/phases/phase-2.0-plan.md`
- §11 fit source: `experiments/phase-0.2/section11_production_validation.py`
- Pilot findings: `experiments/phase-1.4/smoke-100k-results.md`
- Metric code: `src/whitespace2/{semantic_metrics, canonical_metrics, divergence}.py`
- Embed: `experiments/phase-1.1/embed_modal.py`, `src/whitespace2/resumable_runner.py`
