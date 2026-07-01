# Phase 2.2 WS-E — divergence test result (base 1M, CS + Physics)

**Date:** 2026-07-01 · **Headline: Claim #13 is NOT supported — a successful
NULL (CS) / mixed (Physics).** The pre-registered *ratio* estimator returns
"divergence," but it is **denominator-confounded**; the absolute semantic
trends (and the pre-registered residual analysis, WS-F) show semantic plurality
**rising**, not stagnating/declining.

## The two readings

| | CS | Physics |
|---|---|---|
| **Pre-registered ratio verdict** | divergence | divergence |
| **Honest verdict (absolute trends)** | **null — semantic rises** | **mixed** |
| demographic joint plurality (raw σ) | **+3.30σ** | **+3.34σ** |
| cluster_entropy (raw σ) | +1.72σ | +1.87σ |
| effective_dimensionality (raw σ) | +1.94σ | **−2.96σ** |
| mean_pairwise_cosine (raw σ) | +3.35σ | +3.27σ |
| negative control (ref-canonicity Gini) | rises, sig ✓ | rises, sig ✓ |

(σ = total standardized change over 1970–2024, each series vs its own SD.)

## Why the ratio test is confounded (the load-bearing point)

The estimator is the OLS slope of `semantic / demographic` on year. That ratio
falls whenever the demographic denominator **outpaces** the semantic numerator —
**even if semantic rises.** Here the demographic joint plurality rises steeply
(+3.30σ CS / +3.34σ Physics — real: more countries [China 2%→30%, Phase 1.3],
career-stages, gender mix over 55 years), so `semantic/demographic` falls for
*every* semantic metric that rises more slowly. That is exactly what happened:
all three CS ratios fall ~−3.2σ at the permutation floor — but the tell is their
**near-identical** effect sizes across metrics that measure very different
things (cluster entropy, PCA dimensionality, pairwise cosine). Near-identical
ratio slopes ⇒ a common factor (the denominator) drives them, not semantic
decline.

Claim #13 requires semantic plurality to **stagnate or decline in absolute
terms**. It does not: in CS all three metrics rise; in Physics they disagree
(cluster-entropy up, effective-dim down — the Phase-1.4 pilot's finding #2,
reproduced at full scale). So the honest verdict is **NULL / mixed**, and the
ratio test's "divergence" is a false positive of a confounded estimator.

## Implication for the pre-registration (reported, not quietly patched)

The pre-registered §5 decision rule (negative ratio slope, now with the PA-2
permutation null + 0.1σ floor) is **insufficient to test Claim #13** — a falling
ratio conflates "semantic declined" (real divergence) with "semantic rose
slower than demographic" (not divergence). The correct adjudicator is the
**pre-registered "critical second figure"** (§13 confound controls): residual
semantic diversity after controlling for demographic composition + field growth
+ publication volume, regressed on year. The raw absolute trends already
strongly predict its outcome — no absolute semantic decline. We report the
pre-registered ratio result honestly AND the confound; we do not swap the
estimator post-hoc to change the answer. **WS-F (residual figure) is now the
decisive analysis, not a supplement.**

## Substrate + method notes

- **Negative control is now sound.** Reference-canonicity Gini (WS-A / PA-1
  primary) rises significantly in both fields — the pilot's `substrate_broken`
  (citation-Gini accrual artifact) is fixed. Substrate OK; the primary test is
  interpretable.
- **Demographic substrate:** regenerated offline (gg-only + reused NamSor
  kernel, `--no-genderize`), so gender coverage is lower than the Phase-1.3
  Genderize-augmented production; the demographic *trend* (what the test uses)
  is robust to this (Phase 1.3: v2↔v3 within 1.4pp). A Genderize-augmented
  robustness pass belongs in Stage 3.
- **PA-3 degenerate years:** effective_dimensionality is dropped (NaN) for years
  with < 768 papers (7 CS / 5 Physics early years); cluster-entropy +
  pairwise-cosine use all years.
- **Semantic metrics** computed on a common per-(field,year) subsample of 5,000
  (N-comparability + tractability); cluster-entropy on the full year via the
  §11 assignments.

## Verdict

Per the program's "nulls count" discipline, this is a **successful whitespace**
result so far: the driving claim (#13) is **disconfirmed** in CS (semantic
plurality rose alongside demographic) and **mixed** in Physics — and, as a
bonus, we caught that the pre-registered ratio estimator is confounded before it
could produce a false "divergence" headline. WS-F (the residual figure) is the
next step to formalize the absolute-trend reading.

## Artifacts

- `experiments/phase-2.2/run_test.py` — assembly + test.
- `series/semantic-canonical.json`, `series/demographic-joint.json` — the series.
- `series/divergence-verdict.json` — the full verdict (ratio + honest + raw).
