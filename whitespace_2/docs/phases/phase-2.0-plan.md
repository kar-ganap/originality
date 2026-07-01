# Phase 2.0 Plan — Stage 2 (Walk) + the pre-registered divergence test

**Stage:** 2 — Walk
**Phase:** 2.0 — Stage 2 plan + divergence-test pre-registration
**Window opens:** post-Phase-1.4 signoff
**Status:** Pre-registration LOCKED (per desideratum §5) before any full-data
run. Stage 2 workstreams headline-level (detailed when each begins).

> **Desideratum §5:** "The primary statistical test of demographic-vs-semantic
> divergence is pre-registered (metric, estimator, field, time window, null,
> threshold) in `docs/phases/phase-2.X-plan.md` **before full-data analysis
> runs**." This document is that pre-registration. It consolidates Phase 0.2's
> "Test I", reconciles it with the realized Phase-1.3 metrics + the
> user-locked demographic axes (gender × country × career-stage), and bakes in
> the three findings from the Phase-1.4 100K pilot
> (`experiments/phase-1.4/smoke-100k-results.md`).

---

## THE PRE-REGISTERED DIVERGENCE TEST (Test I) — LOCKED

**Claim (#13):** Over 1970–2024, intellectual (semantic) plurality has
decoupled from demographic plurality — demographic plurality rises while
semantic plurality stagnates or declines.

### Field + window
- **Field:** Computer Science (primary). **Physics replication REQUIRED**
  (§6): a headline finding in CS is not a finding until it replicates (or is
  reported as failing to replicate) in Physics.
- **Time window:** **1970–2024** (the pre-registered study window; the §0
  corpus has a pre-1970 mis-dated tail + partial post-2024 — Phase 1.4 A1).
- **Unit:** distinct authors per (year, field) cell (headline); authorship
  appearances as a robustness slice (Phase 1.3 — they barely differ).

### Demographic plurality (the denominator) — gender × country × career-stage
- **Primary metric:** **joint Shannon entropy** (nats, Miller-Madow corrected)
  over the joint distribution of
  (**gender** [bias-corrected, Phase 1.3] × **country of affiliation** ×
  **career-stage bin**) per (year, field) cell.
  - Career stage = `year − author.min_year` (years since first publication),
    binned **0–5 / 6–15 / 16+** (per conceptual.md; derivable from the
    `min_year` already in the Phase-1.3 per-author table — a small Stage-2
    pipeline extension, no re-extraction).
- **Secondary metric:** **Gini-Simpson (Blau) index** `1 − Σ pᵢ²` over the
  same joint distribution (§8: demographic ≥2 metrics).
- **Prestige is NOT in the headline** (user-locked 2026-06-30). Per the prior
  art's own caveat (`phase-0.1-plan.md` §iv: prestige entangles regional
  composition; coverage-limited), institutional prestige (ARWU top-10/50/200
  tier + CSRankings cross-check) is deferred to **Test II / Stage 3**,
  pre-registered as a region-disaggregated robustness axis.

### Semantic plurality (the numerator) — on SciNCL embeddings
- **Primary A:** **cluster entropy** — Shannon (MM-corrected) over K-means
  (K=50) cluster assignments, with the **§11 temporally-stratified fit**
  (non-negotiable; the pilot reconfirmed it matters — finding #3).
- **Primary B:** **effective dimensionality** — PCA participation ratio.
- **Secondary:** **mean pairwise cosine distance** (bootstrap-subsampled).
- Model: **SciNCL** (primary); **Qwen3** cross-family robustness swap.

### Estimator + decision rule
- **Estimator:** OLS regression of the per-year **(semantic metric /
  demographic metric) ratio** on year → slope + two-tailed p-value
  (`src/whitespace2/divergence.py`).
- **Divergence CONFIRMED** iff:
  (a) BOTH primary semantic ratios (cluster entropy AND effective
  dimensionality) show a **negative slope significant at p<0.05 two-tailed**,
  AND (b) the secondary (mean pairwise cosine) agrees directionally.
- **Successful NULL** (Claim #13 disconfirmed — a publishable result): both
  plurality series rise in tandem; no significant negative ratio slope.
- **MIXED verdict (pre-registered, per pilot finding #2):** the pilot showed
  cluster entropy and effective dimensionality **can disagree in direction**
  (global spread vs fixed-cluster concentration). If they disagree at full
  scale (with §11 + the age-robust setup), the outcome is reported as **mixed
  / metric-dependent — NOT a confirmed divergence** and NOT cherry-picked to
  the favorable metric. All three semantic metrics are always reported (§8).

### Negative control (pre-registered)
- **Canonical concentration** must show a significant **positive** slope over
  year (citations concentrate). Metric: citation Gini + top-k share
  (`src/whitespace2/canonical_metrics.py`), **citation-age-robust** per pilot
  finding #1. Raw total-`cited_by_count` per publication year is INVALID
  across years (recent papers are zero-inflated; Gini is scale-invariant so a
  rescale is a no-op).
- **Age-restricted, not fixed-window (amended 2026-06-30, Phase 2.1 WS3;
  user-locked).** The pilot named two candidate robust metrics — a fixed
  N-year citation window OR an age-cohort normalization. The **fixed N-year
  window is DROPPED**: it needs `counts_by_year` (citations accrued within N
  years of publication), which is not in the §0 corpus and — even if
  re-pulled — OpenAlex's `counts_by_year` does not reach back to ~1970, so a
  5-yr-from-publication window is unreconstructable for old papers (the whole
  early window). The committed control is **age restriction**
  (`age_restricted_concentration`): compute Gini + top-k **per publication
  year on only the years whose papers are ≥ N years old** at the snapshot,
  dropping the immature recent tail where Gini spuriously collapses. No data
  pull — uses the total `cited_by_count` + `publication_year` already in the
  corpus.
- **N-floor + residual-gradient caveat.** Age restriction removes the worst
  zero-inflation but leaves a residual accrual gradient (a 1980 paper still
  has more accrual years than a 2015 one). So the control is **directional**:
  Gini/top-k must **rise across the retained mature years**, reported over a
  **sweep of N ∈ {3, 5, 10}** (Phase 2.2) rather than at a single N. If the
  positive slope does not survive the sweep — i.e. the age-robust control is
  flat/negative on the mature years — the analysis substrate is broken; do
  not interpret the primary test.

### Confound controls (§13)
- Field growth + publication volume: the ratio partially controls; the
  headline is complemented by the conceptual.md "critical second figure" —
  **residual semantic diversity after controlling for field growth,
  publication volume, and demographic composition, vs year.**

---

## Stage 2 workstreams (headline-level)

| # | Workstream | Note |
|---|---|---|
| S1 | Full embed: 1M v3 (headline) + 500K robustness, SciNCL + Qwen3 | Modal A100 preempt; `ws2-embed` + `ChunkedEmbedRunner` (validated at 100K, Phase 1.4). **§9 cost gate: pre-commit ~$77 in `tasks/spend.md`.** |
| S2 | Career-stage pipeline extension | add the career-stage-binned joint demographic plurality (from `min_year`) to the coverage pipeline (+ tests) |
| S3 | Citation-age-robust canonical metric | **age-restricted** (papers ≥ N yr old; fixed-window dropped — `counts_by_year` unreconstructable pre-~2015); sweep N∈{3,5,10} (pilot finding #1) — DONE Phase 2.1 WS3 |
| S4 | Compute the 3 axes as annual time series (§11-stratified cluster fit) | demographic / semantic / canonical |
| S5 | Run the pre-registered divergence test | `divergence_test`; CS then Physics |
| S6 | 3-panel figure + residual-controls figure | per conceptual.md |
| S7 | Robustness sweep | model swap (Qwen3), v2 corpus, unit, domestic-only (diaspora §iii), demographic-inference uncertainty band (§4) |
| S8 | Paper draft | report the verdict honestly (divergence / null / mixed) |

---

## Cost (Stage 2)

Per Phase 1.1 measurement ($0.0000191/abs combined) + Phase 1.4 100K
($0.22 SciNCL): full Stage 2 embed ≈ **$77** (3×1M + 2×500K). **>$50 → a
written pre-commit estimate in `tasks/spend.md` is REQUIRED (§9) before S1
runs.** Within the §9 $500 cap (Wave 4A budget $250–550).

---

## What the pilot already de-risked (Phase 1.4)

- The embed → per-year semantic → canonical → demographic → `divergence_test`
  chain **composes** and yields computable statistics at 100K.
- SciNCL embeds clean at 100K (norms in band, finite, $0.22).
- Three methodology requirements are now pre-registered above (S2/S3, the
  §11 fit, the mixed-verdict rule).

---

## Companion documents

- Pre-registration source: `docs/phases/phase-0.2-plan.md` "Test I"
- Pilot: `experiments/phase-1.4/smoke-100k-results.md`
- Metric code: `src/whitespace2/{semantic_metrics, canonical_metrics,
  divergence}.py`
- Desiderata §5/§6/§8/§9/§11: `docs/desiderata.md`
- Conceptual (3-panel + residual figure): `docs/conceptual.md`
- Compute lock: `experiments/phase-0.2/stage2-compute-decision.md`
