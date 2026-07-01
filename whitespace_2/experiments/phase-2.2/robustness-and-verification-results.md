# Phase 2.2 WS-F + robustness + correctness verification

**Date:** 2026-07-01 · **Verdict: Claim #13 is NOT supported — a ROBUST null /
mixed.** After the full pre-registered robustness stack, there is **no robust
semantic decline** anywhere; the ratio test's "divergence" was a demographic-
denominator confound, and the one narrowing signal does not survive a model
swap. The analysis machinery is independently verified correct.

---

## 1. Correctness battery (`verify_correctness.py`)

Trust comes from **independent agreement + placebo controls**, not "tests pass."

- **(A) Cross-implementation — 8/8 PASS.** Every metric matches a second,
  independent computation to ~6 sig figs: `gini` vs mean-abs-difference;
  `effective_dimensionality` vs **sklearn PCA**; `cluster_entropy` vs **scipy**
  entropy + Miller-Madow; `mean_pairwise` vs an explicit loop; OLS slope vs
  `np.polyfit`; `standardized_effect` vs manual; `residual_trend` year-coef vs
  **numpy normal-equations**; reference-stability = 1 on identical years.
- **(B) Placebo / null — PASS.** (i) **Year-shuffle:** scrambling the year
  labels on the real CS ratio kills the trend (significant in 2/200 ≈ 1%),
  while the real finding IS significant → **not a pipeline leak.** (ii)
  **Random-noise embeddings** at matched N → **0 of 16** spurious
  permutation-significant trends (8 seeds × 2 metrics). The initial raw-σ
  "FAIL" was a threshold artifact: those series are constant to ~4 decimals
  (`1.00000 ± 1e-4`), so `σ = slope·range/sd` is ill-conditioned; the correct
  null criterion is *significance*, which passes clean.
- **(C) Calibration — PASS.** Permutation false-positive rate 1.7% ≈ the 0.01
  alpha; a proportional (known-null) series → `divergence_confirmed = False`.

**Conclusion:** the metrics are independently correct, and the pipeline does not
manufacture trends from shuffled years or Gaussian noise. The signals below are
real properties of the data.

---

## 2. Robustness sweep (`robustness_sweep.py`) — raw σ / residual per config

All cluster-entropy is on the **matched-N (5000) subsample** (volume-controlled
by construction). "resid" = year-coef of `metric ~ year + log(volume) +
demographic`.

### 2a. The residual "critical second figure" is collinearity-limited
Year, log-volume, and demographic plurality all rise near-monotonically
together, so **year VIF = 44 (CS) / 60 (Physics)** — the partial year effect
**cannot be cleanly separated** from the confounds. The residual coefficients
are therefore unreliable (reported, but not decisive). This is an honest
methodological result: the confounds are too collinear to partial out via
regression, so adjudication falls to the **raw absolute trends + cross-config
robustness**.

### 2b. Raw absolute trends across the stack (total σ, 1970-2024)

| metric | config | CS | Physics |
|---|---|---|---|
| **mean_pairwise_cosine** | base / qwen3 / clean05 | +3.35 / +3.01 / +3.33 | +3.27 / +3.25 / +3.27 |
| **effective_dim** | base / qwen3 / clean05 | +2.42 / +2.10 / +2.82 | **−2.86 / +2.49 / −2.77** |
| **cluster_entropy** | base / K30 / K100 / qwen3 / clean05 | +1.68 / +1.45 / +2.69 / +0.10 / +0.37 | +1.93 / +2.78 / +0.71 / +2.63 / +2.13 |

**Three robustness findings:**
1. **`mean_pairwise_cosine` robustly RISES** — both fields, all 5 configs
   (+3.0 to +3.35σ). The most stable signal; semantic content is getting more
   dispersed, not less.
2. **The one narrowing signal — Physics `effective_dim` (−2.86σ SciNCL) — does
   NOT survive the model swap:** Qwen3 gives **+2.49σ** (reverses sign). So it
   is SciNCL-specific, not a robust property — exactly the "search until a
   variant declines" trap we refused to fall into. Not evidence of divergence.
3. **`cluster_entropy` is the fragile metric** (as the pilot's finding #2
   warned): +0.10 (CS/Qwen3) to +2.79 (Physics/K30) depending on model and K.
   It ranges from a clear rise to near-flat — but **never robustly declines.**

### 2c. Verdict
No semantic metric declines robustly across model × K × subset. The strongest
*honest* reading the numerator can support — even after the disciplined "push"
(volume control, Qwen3 swap, K-sweep, score≥0.5 clean subset) — is **null /
mixed**, never a confirmed divergence. **Claim #13 is disconfirmed robustly:**
semantic plurality did not stagnate or decline; it rose (robustly on pairwise
distance, mostly on the others) while demographic plurality rose faster.

---

## 3. What this means

- **A successful whitespace** (program discipline: nulls count). The driving
  claim is robustly disconfirmed, and — a methodological bonus — we caught that
  the pre-registered ratio estimator is denominator-confounded *and* that the
  residual estimator is collinearity-limited, before either could produce a
  false "divergence."
- **The numerator's fragility is real but bounded** (the user's hypothesis
  confirmed): it manifests as metric disagreement + model-sensitivity
  (cluster-entropy, Physics eff-dim), which the pre-registered mixed-verdict
  rule absorbs — it can dissolve the null into "mixed," but cannot manufacture
  a robust divergence.
- **Caveats for the writeup:** demographic substrate is gg-only (Genderize
  robustness → Stage 3); residual regression is VIF-limited; the pre-1990
  corpus-quality tail (WS-B) persists in clean05 only partially.

## Artifacts
- `verify_correctness.py` + `series/*.json`; `robustness_sweep.py` +
  `series/robustness-sweep.json`; `divergence-verdict-results.md` (WS-E).
