# Phase 2.0 Plan — Stage 2 (Walk) + the pre-registered divergence test

**Stage:** 2 — Walk
**Phase:** 2.0 — Stage 2 plan + divergence-test pre-registration
**Window opens:** post-Phase-1.4 signoff
**Status:** Pre-registration LOCKED (per desideratum §5) before any full-data
run. Stage 2 workstreams headline-level (detailed when each begins).

**Amendments (all pre-full-data-run — §5 compliant):**
- *2026-06-30 (Phase 2.1 WS3):* canonical control = age-restricted (fixed
  citation window dropped — `counts_by_year` unreconstructable).
- *2026-07-01 (Phase 2.2 PA-1/2/3, user-signed-off from the lit-review/
  desiderata audit):* **PA-1** Chu-Evans reference-list canonicity is the
  **primary** canonical metric (age-restricted citation Gini/top-k → secondary);
  **PA-2** decision gate = year-permutation null + a ~0.1σ effect-size floor
  (replaces bare p<0.05); **PA-3** pre-registered per-metric degenerate-case
  exclusions. Rationale + detail in the sections below.

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
  demographic metric) ratio** on year → slope, reported as a **standardized
  effect** (SD/year AND total standardized change over 1970–2024)
  (`src/whitespace2/divergence.py`).
- **Significance — permutation null (amended 2026-07-01, Phase 2.2 PA-2).**
  The decision gate is a **year-label permutation test**, NOT a bare p<0.05:
  shuffle the year labels N≥10⁴ times, recompute the ratio-slope each time →
  the null distribution of a slope arising from noise alone in this data; the
  observed slope must fall **beyond the 99.5/0.5 percentile** (two-tailed).
  Data-derived and unit-safe (imports none of the CD-critique's units).
- **Effect-size floor (amended 2026-07-01, Phase 2.2 PA-2).** A slope that
  beats the permutation null but whose **total standardized change is < ~0.1σ**
  is reported as **"no material divergence,"** not a confirmation — the
  CD-critique literature's "treat below ~0.1σ as noise" line (PAP 2025's
  measurement-artifact residuals are 0.06–0.09σ *total* contrasts; close-read
  04). A total change clearing **~1σ** (≈0.02 SD/yr × window) is flagged as a
  **substantial** divergence.
- **Divergence CONFIRMED** iff:
  (a) BOTH primary semantic ratios (cluster entropy AND effective
  dimensionality) show a **negative slope that clears the permutation null
  (99.5th pct) AND the ~0.1σ effect-size floor**, AND (b) the secondary (mean
  pairwise cosine) agrees directionally.
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
  year (the canon ossifies / concentrates).
- **Primary metric (amended 2026-07-01, Phase 2.2 PA-1): Chu-Evans reference-
  list canonicity** (`reference_canonicity`, `canonical_metrics.py`) — per
  publication year, the concentration (Gini / top-k) of reference-target
  frequency **and** the **Spearman rank stability of the top-N=50 most-
  referenced works across Δ=5** (Δ=1 reported as a comparability column vs
  Chu-Evans's published values). Built from `referenced_works` (in-corpus) →
  **no `counts_by_year` needed**, and — since a reference list is fixed at
  publication — **no citation-accrual confound** (unlike citation Gini).
  Targets counted over ALL cited works (cross-field foundational works
  included — the canon a field draws on); the top-N Spearman uses the union of
  the two years' top-N with actual-frequency ranks. Sample-based (references
  counted within the 1M sample) — documented. This is the conceptual doc's
  designated primary canonical operationalization + gives the axis a metric
  genuinely independent of the citation-distribution ones (§8).
- **Secondary metric: age-restricted citation Gini + top-k** (the former
  primary). Raw total-`cited_by_count` per publication year is INVALID across
  years (recent papers are zero-inflated; Gini is scale-invariant so a rescale
  is a no-op) — hence the age restriction below.
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

### Degenerate-case exclusions (pre-registered, amended 2026-07-01, Phase 2.2 PA-3)

Per-metric degenerate cases are excluded from the **primary** slope BEFORE
analysis (Holst-derived, close-read 05), each paired with a sensitivity that
re-includes them so an exclusion can never silently drive a finding:
- **effective_dimensionality:** publication-years with **N < 768** are
  structurally degenerate (participation ratio ≤ N−1 by construction) →
  excluded from the primary slope; a sensitivity at a higher stability floor
  (~1500) is also reported.
- **cluster_entropy:** years with N below the Check-5b N_target (200) flagged.
- **canonical:** all-zero-citation / all-zero-reference years excluded
  (concentration undefined).
- **joint demographic plurality:** cells with zero career-joint coverage
  excluded (already null in `build_coverage_table`).

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
