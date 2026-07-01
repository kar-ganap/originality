# Phase 1.4 Retro

**Phase:** 1.4 — Pre-Stage-2 quality gates + 100K divergence smoke + signoff
**Stage:** 1 — Crawl (final phase)
**Branch:** `phase-1.4-execution`
**Window:** 2026-06-30 (plan → execution, single session)
**Status:** Complete. **Stage 1 (Crawl) CLOSED. Ready for Stage 2 (Walk).**

---

## One-line summary

Validated the Stage-1 demographic substrate at production scale (all field
intuitions pass — CS volume growth, China's CS rise 2%→30%, career-length
distribution), lifted the semantic + canonical diversity metrics into `src/`
and implemented the divergence estimator, ran a **100K end-to-end mini-Stage-2
pilot** that de-risked the whole embed → semantic → divergence pipeline (clean
$0.22 embed) while surfacing **three concrete Stage-2 methodology
requirements** before the spend, and **pre-registered the divergence test**
(gender × country × career-stage vs cluster-entropy + effective-dim + mean-
pairwise-cosine; OLS-of-ratio-on-year; citation-age-robust canonical control)
per desideratum §5. Stage 1 → Stage 2 transition signed off.

---

## What happened

### A — Production sanity gates (commit `6a4a43c`)

All field intuitions pass (`sanity-checks.md`): CS author volume
1,064→150,061 (1975→2024, exponential, overtakes physics ~2005); **China's
CS author share 2.2%→29.8%** (reproduces the known macro trend — a strong
external validation of the country inference); female share rises;
career-length distribution sane (0.014% >60yr). Year-bound → **1970–2024**
(pre-1970 = 0.6% mis-dated tail; headline unchanged). Two methodology
clarifications: the physics ≥ CS early-female pattern is robust to sample
size (mechanism open → Stage 2); **per-cell H7 re-framed for Option B** (the
correction is per-region → H5+H8 are the binding gates, both pass).

### C1/C2 — Stage-2 metric code (commits `c3d432b`, `4667cb2`)

`semantic_metrics.py` (effective dimensionality, mean pairwise cosine,
cluster entropy) — ported from Phase 0.1 and **verified to match the
originals exactly** on shared random input; `canonical_metrics.py` (Gini,
top-k share); `divergence.py` (the pre-registered Test-I OLS estimator). 15
new tests.

### C3/C4 — 100K mini-Stage-2 pilot (commit `2db807b`)

100K SciNCL embed on Modal A100 — clean (norm 23.70 in band, all finite,
319 s, **$0.22**). The pilot ran the full chain (embed → per-year semantic →
canonical → demographic → `divergence_test`) end to end — **the de-risk goal**
— and surfaced three findings (below).

### B — Divergence-test pre-registration (commit `13ab22c`)

`docs/phases/phase-2.0-plan.md` locks Test I per §5 before any full-data run.

---

## Surprises / findings

1. **Citation-age artifact in the canonical negative control.** Raw citation
   Gini per *publication* year declines instead of rising — recent papers are
   zero-inflated (haven't accrued citations), so their citation distribution
   is artificially less concentrated. **A rescale doesn't fix it** (Gini is
   scale-invariant — dividing by paper age is a no-op; confirmed). Needs a
   citation *window* or age-cohort. Pre-registered as an S3 requirement.
2. **The two primary semantic metrics can disagree in direction.**
   `cluster_entropy` ratio falls (→ divergence) but `effective_dimensionality`
   rises (→ not). Interpretable (fixed-cluster concentration vs global spread),
   and the reason the pre-registration adds a **MIXED verdict** rule (report
   all three; never cherry-pick).
3. **§11 temporal K-means stratification is confirmed load-bearing** (the
   pilot's non-§11 global fit likely contributes to #2).
4. **China's CS rise (2%→30%)** cleanly validates the country inference
   against a known macro trend — the strongest single sanity signal.
5. **The 100K pilot cost $0.22, not ~$4** — SciNCL is far cheaper than the
   plan's conservative estimate.

---

## Lessons (logged in `tasks/lessons.md`)

- **A cross-year citation-concentration comparison is confounded by accrual
  time, and rescaling can't fix a scale-invariant statistic.** Any citation
  metric compared across publication years needs a fixed window / age-cohort,
  not a per-year rescale.
- **A de-risking smoke's value is the issues it surfaces, not the numbers it
  produces.** The 100K pilot's "substrate_broken" verdict was an artifact, but
  it surfaced three real Stage-2 requirements before the $77 spend.

---

## Validation gates check

Gates from `phase-1.4-plan.md`:

| # | Gate | Status |
|---|---|---|
| 1 | Year-bound applied | ✅ 1970–2024; headline unchanged |
| 2 | Field-intuition checks pass | ✅ volume, China-rise, career length; physics≥CS diagnosed |
| 3 | Per-cell H7 | 🟡 re-framed (H5+H8 binding, both pass) |
| 4 | Semantic + canonical metrics in `src/` | ✅ match Phase 0.1 exactly |
| 5 | Divergence estimator implemented | ✅ 6 tests |
| 6 | 100K embed clean | ✅ norms in band, finite, $0.22 |
| 7 | Pilot divergence computable | ✅ composes (substrate_broken = finding #1 artifact) |
| 8 | Divergence test pre-registered | ✅ `phase-2.0-plan.md` |
| 9 | Tests pass + lint/typecheck clean | ✅ 188 tests, ruff + mypy strict |
| 10 | Retro + signoff committed | ✅ this document |

All clean or benign-amber (#3, #7 both diagnosed, not defects).

---

## Methodology amendments locked through Phase 1.4

- **Study window = 1970–2024**, applied downstream; a `publication_year` floor
  is a future §0/sampling amendment (the §0 filter screened junk-year *tokens*,
  not the year field).
- **Headline demographic plurality = gender × country × career-stage**
  (user-locked). Prestige deferred to Test II / Stage 3 (region-entangled).
- **Canonical negative control must be citation-age-robust** (window /
  age-cohort), not raw `cited_by_count`.
- **MIXED verdict pre-registered** for semantic-metric direction disagreement.
- **Per-cell H7 re-framed** for Option B (per-region H5 + per-cell H8 binding).

---

## Stage 1 → Stage 2 transition signoff

All 7 transition deliverables in place:

| # | Deliverable | Status |
|---|---|---|
| 1 | §0 analytical population (v3 24.5M + v2) | ✅ Phase 1.2 |
| 2 | Sampled production sets (1M v3 + 1M v2 + manifests) | ✅ Phase 1.2 |
| 3 | Held-out sets (8 parquets) | ✅ Phase 1.2 |
| 4 | Author + demographic annotations (v3 + v2 coverage tables + bias kernel) | ✅ Phase 1.3 |
| 5 | Validated Modal A100 cost + preemption profile | ✅ Phase 1.1 |
| 6 | Resumable runner + Modal embed functions | ✅ Phase 1.1 (re-validated at 100K, Phase 1.4) |
| 7 | Sanity-check sign-off on production data | ✅ Phase 1.4 (workstream A) |

Plus Phase 1.4 delivered the Stage-2 metric code (`semantic_metrics`,
`canonical_metrics`, `divergence`), the 100K pilot de-risk, and the
**pre-registered divergence test** (`phase-2.0-plan.md`).

**Stage 1 (Crawl) is CLOSED.** Stage 2 (Walk) begins with S1 — the full 1M
embed (needs the §9 ~$77 pre-commit in `tasks/spend.md`) — and S2/S3 (the
career-stage + citation-age-robust extensions the pilot flagged), then the
pre-registered divergence test on CS and Physics.

---

## Companion documents

- Plan: `docs/phases/phase-1.4-plan.md`
- Sanity checks: `experiments/phase-1.4/sanity-checks.md`
- Pilot: `experiments/phase-1.4/smoke-100k-results.md`
- Pre-registration / Stage 2 plan: `docs/phases/phase-2.0-plan.md`
- Metric code: `src/whitespace2/{semantic_metrics, canonical_metrics, divergence}.py`
