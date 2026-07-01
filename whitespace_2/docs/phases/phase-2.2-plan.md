# Phase 2.2 Plan — Compute the 3 series + run the pre-registered divergence test

**Stage:** 2 — Walk
**Phase:** 2.2 — divergence-test execution (CS + Physics)
**Window opens:** post-Phase-2.1
**Status:** **PLAN — amendments LOCKED (user-signed-off 2026-07-01);** ready for
execution. PA-1/2/3 have been written into `docs/phases/phase-2.0-plan.md` §5
(all pre-full-data-run, so §5-compliant). Execution (WS-A → G) opens on a fresh
`phase-2.2-execution` branch off `main` after the Phase 2.1 merge.

> This plan folds in the six items from the 2026-07-01 lit-review / desiderata
> navigation audit (see §"Audit items addressed"). Three of them are
> pre-registration decisions (PA-1/2/3); three are execution tasks (WS-B/C/G).

---

## One-line scope

Compute the demographic / semantic / canonical **annual series** from the base
1M embeddings (Phase 2.1) + the Phase-1.3 demographic substrate, run the
**pre-registered divergence test** (Test I, `phase-2.0-plan.md` §5) on **CS then
Physics**, and produce the 3-panel + residual figures — while closing the six
audit items so no known gotcha is left unhandled before the headline.

---

## Inputs ready (from Phase 2.1)

- Base **1M SciNCL + Qwen3** vectors + row-aligned `metadata.parquet` + §11
  `scincl-cluster-assignments.npy` + production centroids — durable on Modal
  volume `ws2-embeddings` `/base-1m/`.
- `src/` metrics: §11 `cluster_fit`, `semantic_metrics`, career-stage joint
  plurality (`build_coverage_table`), age-restricted `canonical_metrics`,
  `divergence`.
- Phase-1.3 demographic substrate: v3 corrected per-author parquet (**confirm
  `min_year` + `primary_country` survive** for the WS2 joint plurality).
- Locked pre-registration: `phase-2.0-plan.md` §5.

---

## Pre-registration amendments (LOCKED — signed off 2026-07-01; in phase-2.0-plan.md §5)

### PA-1 — Chu-Evans reference-list canonicity as the PRIMARY canonical metric
- **Why:** `conceptual.md` + close-read 01 lock the canonical *primary* as
  "Chu-Evans Spearman N=50, Δ=5"; desiderata §8's example is "Spearman top-N +
  Gini." Currently only citation Gini + top-k (the *secondary* metrics) exist,
  and those two are the same construct (one citation distribution's
  concentration) — the canonical axis has no genuinely independent 2nd metric.
- **Metric (WS-A):** `reference_canonicity`, built from `referenced_works_json`
  (present in the §0 corpus — **no `counts_by_year` needed**, so it sidesteps
  the blocker that killed the fixed-window metric). Per publication year *t*:
  (a) concentration of reference-target frequency (Gini / top-k over how often
  each cited work is referenced by year-*t* papers) and (b) **Spearman rank
  correlation of the top-N most-referenced works between year *t* and *t+Δ*,
  Δ=5, N=50** (canon ossification). Higher stability + concentration = more
  canonical.
- **Role:** `reference_canonicity` becomes the **primary** canonical series;
  age-restricted citation Gini/top-k (WS3) stay as **secondary** canonical
  metrics (§8 satisfied with two *independent* constructs).
- **Caveat to document:** references are counted *within the 1M sample*
  (a subsampled canon proxy); Δ=1 reported as a comparability column vs
  Chu-Evans's published values (close-read A4).

### PA-2 — Permutation null + effect-size floor in the decision rule (not p-value alone)
- **Why (pinned from close-read 04):** PAP 2025's 0.06–0.09σ is a **total
  standardized contrast** (CD 2015-vs-1995 = +0.06σ; team k=25-vs-k=2 = 0.09σ),
  in per-(journal-year)-standardized units — the magnitude a measurement
  artifact alone can manufacture. The literature's own reform: "report effect
  sizes in σ; **treat anything below ~0.1σ as noise**." A bare p<0.05 slope
  over ~53 year-points can sit inside that band.
- **Decision gate — permutation null (data-derived, unit-safe):** shuffle the
  year labels, recompute the (semantic/demographic) ratio-slope N≥10⁴ times →
  the null distribution of "slope from noise alone in OUR data." Require the
  observed slope beyond the **99.5/0.5 percentile** (two-tailed). Replaces the
  bare p<0.05 and imports none of PAP's units.
- **Literature-anchored effect-size floor (veto + reporting):** report the
  slope as SD/year AND **total standardized change over 1970–2024**. A slope
  that beats the permutation null but whose total change is **< ~0.1σ** (the
  CD-critique "below = noise" line) → **"no material divergence,"** not a
  confirmation. Flag whether it also clears the stronger **~1σ** (≈0.02 SD/yr ×
  window) "substantial divergence" mark (close-read 04's mooted Test-I
  threshold). A CONFIRMED divergence needs **both** primary semantic ratios to
  clear the permutation null AND the 0.1σ floor.
- *(Retires the earlier ad-hoc 0.3σ placeholder — ~3× the literature's own
  ~0.1σ noise line, anchored to nothing.)*

### PA-3 — Per-metric degenerate-case exclusion list (pre-registered)
- **Why:** Holst-derived (close-read 05) — pre-register which degenerate cases
  are excluded, with justification, before analysis.
- **List (proposed):**
  - `effective_dimensionality`: publication-years with **N < 768** are flagged
    degenerate (participation ratio ≤ N−1 by construction) — reported
    separately, excluded from the primary slope, sensitivity with them included.
  - `cluster_entropy`: years with N below the Check-5b N_target (200) flagged.
  - canonical: all-zero-citation / all-zero-reference years excluded (undefined
    concentration).
  - joint plurality: cells with zero career-joint coverage excluded (already
    null in WS2).

---

## Workstreams

| WS | Scope | Audit item | Spend |
|---|---|---|---|
| **A** | Build `reference_canonicity` (Chu-Evans, TDD) — reference-target freq + top-N Spearman-Δ5 stability + concentration | 1 (PA-1) | $0 |
| **B** | **Cross-era drift check** on the 1M SciNCL + Qwen3 vectors: pre-1990 query papers → NN era-match rate + topical hand-audit (mirror Check 5c/H7). **Gate:** if pre-1990 drift dominates → invoke the pre-registered **E3 fallback (bound semantic claims to post-2000)** | 3 | $0 (existing vectors) |
| **C** | **Per-year power audit:** per-year N in the 1M sample; flag years under the PA-3 floors; run the **year-stratified + citation-weighted** samples as the pre-registered robustness axis (J3). Re-draw/re-embed early years ONLY if power is inadequate (would trigger a small §9 pre-commit) | 4 | ~$0 unless re-sample |
| **D** | Compute the **3 annual series** (§11-stratified semantic: cluster-entropy + effective-dim + mean-pairwise-cosine; joint-demographic: career-joint Shannon + Gini-Simpson; canonical: reference-canonicity primary + age-restricted Gini/top-k, N∈{3,5,10} sweep) — CS + Physics | — | $0 |
| **E** | Run `divergence_test` per §5 + PA-1/PA-2 decision rule; **report divergence / null / mixed honestly**; then **Physics replication** | — | $0 |
| **F** | Figures: 3-panel (demographic / semantic / canonical) + the **critical second figure** (residual semantic diversity after controlling for field growth, publication volume, demographic composition) + cross-field + subfield-decomposition | — | $0 |
| **G** | **Lit-review cleanup:** mark 09/10/11 (SPECTER/SciRepEval/SciNCL, Tier 2B non-load-bearing) superseded by the empirical model validation; 08 (Wu-Wang-Evans) — light-touch read OR explicit deferred-to-Stage-3 note (Test I doesn't depend on it) | 5 | $0 |

**Order:** A + G (cheap, parallel) → B (drift gate) → C (power) → D → E → F.
B is a **gate**: no pre-1990 semantic claim ships until the drift check clears
or the post-2000 bound is invoked.

---

## Pre-registered acceptance gates

| # | Gate | Acceptance |
|---|---|---|
| 1 | Chu-Evans canonicity in `src/` | tests pass; reference-freq + Spearman-Δ5 correct; sample-caveat documented |
| 2 | Drift check clears (or E3 invoked) | pre-1990 era-match + topical audit reported; if fail → semantic claims bounded to post-2000, stated |
| 3 | Per-year power bounded | per-year N reported; degenerate years (PA-3) flagged + handled |
| 4 | 3 series computed, CS + Physics | all metrics per year; §11 fit used for cluster-entropy |
| 5 | Divergence test run per §5 + PA-1/PA-2 | verdict reported honestly (divergence / null / **mixed**); effect-size floor applied |
| 6 | Figures produced | 3-panel + residual second figure + cross-field |
| 7 | Tests + lint/typecheck clean; pre-registration amendments locked into phase-2.0-plan.md | ruff + mypy strict; PA-1/2/3 written into §5 |

---

## Risks + mitigations

| # | Risk | Mitigation |
|---|---|---|
| R1 | **Mixed verdict** — cluster-entropy vs effective-dim disagree (pilot finding #2) | pre-registered as "mixed / metric-dependent, NOT confirmed"; all 3 semantic metrics always reported |
| R2 | **Pre-1990 embedding drift** distorts early semantic diversity | WS-B gate; E3 fallback bounds claims to post-2000 |
| R3 | **Thin early years** (uniform sample, ~1.4K/yr in 1970s) | PA-3 degenerate flags; year-stratified robustness (WS-C) |
| R4 | Reference-canonicity is sample-subsampled | documented; robustness on the v2 corpus / larger sample if it's load-bearing |
| R5 | Effect-size below noise floor read as a finding | PA-2 floor |

---

## Cost

Series + test + drift check + figures run on the **existing** 1M vectors →
**$0**. Physics is already embedded (256K in-window). New spend only if WS-C's
early-year power audit forces a stratified re-sample + re-embed (small; would
get its own §9 pre-commit). Program total stays ~$52, well under the §9 cap.

---

## Audit items addressed (2026-07-01 lit-review / desiderata cross-check)

1. Chu-Evans primary canonical → **PA-1 + WS-A**.
2. Effect-size floor → **PA-2**.
3. Production drift check (desiderata §3 / E4) → **WS-B** (gate).
4. Uniform-vs-year-stratified sampling power (§7 / J4) → **WS-C + PA-3**.
5. Lit-review pending papers (08/09/10/11) → **WS-G**.
6. Degenerate-case exclusion list → **PA-3**.

## Companion documents

- Pre-registration (LOCKED; amended on approval): `docs/phases/phase-2.0-plan.md`
- Phase 2.1 retro: `docs/phases/phase-2.1-retro.md`
- Conceptual north-star (3-panel + residual figure): `docs/conceptual.md`
- Desiderata (§3 drift, §7 sampling, §8 metric plurality, §11 fit): `docs/desiderata.md`
- Metric code: `src/whitespace2/{cluster_fit,semantic_metrics,canonical_metrics,demographics,divergence}.py`
