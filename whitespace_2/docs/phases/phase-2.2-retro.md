# Phase 2.2 Retro — the divergence test + robustness + the reframing

**Phase:** 2.2 — compute the 3 series + run the pre-registered divergence test
**Stage:** 2 — Walk
**Branch:** `phase-2.2-execution`
**Window:** 2026-07-01 (one session)
**Status:** Complete. **Claim #13 robustly disconfirmed — a successful null,
reframed.** Remaining Stage-2 packaging: publication-grade figures + paper draft
(Stage 3).

---

## Hypothesis (what we set out to test)

Claim #13, in its **absolute** form: over 1970–2024, demographic plurality rises
**while semantic plurality stagnates or declines** (a decoupling / narrowing).
Successful-null = the two rise in tandem. Physics replication required.

## What happened

**Claim #13 is disconfirmed, robustly.** Semantic plurality did **not** narrow;
it rose alongside demographic plurality. But the more interesting reading is a
**reframing** the data supports:

- **Canonical concentration ↑** (reference-canonicity Gini, significant) — the
  citation canon ossifies.
- **Semantic (frontier) diversity ↑** (robustly on pairwise cosine; noisier on
  cluster-entropy / effective-dim) — the topical frontier widens.
- **Demographic diversity ↑** (+3.3σ) — authorship diversifies.

The "narrowing" intuition **conflated canonical concentration with frontier
diversity**; empirically they move in opposite directions. The paper's thesis:
*the canon concentrates while the frontier (and authorship) diversify.*

## The methodological spine (why the naive answer was wrong)

1. **The pre-registered ratio estimator is denominator-confounded.** It returned
   "divergence" for both fields — but `semantic/demographic` falls whenever the
   (steeply rising) demographic denominator *outpaces* semantic, even when
   semantic *rises*. The tell: three metrics measuring very different things all
   fell ~−3.2σ (identical → a common denominator, not semantic decline). The
   estimator tested a *relative-rate* claim, not the *absolute-narrowing*
   hypothesis.
2. **The residual "critical second figure" is collinearity-limited.** Year,
   log-volume, and demographic plurality are near-collinear (year VIF 44–60), so
   the partial year-effect is unidentifiable. Reported, not decisive.
3. **The one narrowing signal (Physics effective-dim −2.86σ) is model-specific:**
   it reverses to +2.49σ under Qwen3. Not a robust divergence — exactly the
   "search until a variant declines" trap we refused.
4. **Adjudication falls to raw absolute trends + cross-config robustness**
   (volume-control matched-N, Qwen3 swap, K∈{30,100}, score≥0.5 clean subset):
   no semantic metric declines robustly. `mean_pairwise` robustly rises in both
   fields, all 5 configs.

## Correctness verification (drawing trust)

An independent battery (`verify_correctness.py` → `test_pipeline_verification.py`):
metrics cross-checked against scipy/sklearn/independent formulas (8/8, ~6 sig
figs); **placebos** — year-shuffle (1% FP vs the real significant finding) +
random-noise embeddings (**0 of 16** spurious significant trends) — confirm the
pipeline invents no signal; permutation calibration 1.2% ≈ alpha. An initial
placebo "FAIL" was chased across 8 seeds and resolved as an ill-conditioned-σ
threshold artifact, not a bug. The findings are real properties of the data.

## Workstreams (commits on `phase-2.2-execution`)

| WS | Result |
|---|---|
| A | `reference_canonicity` (Chu-Evans primary canonical) — the working negative control |
| B | cross-era drift gate CLEARS (SciNCL/Qwen3 topical coherence across eras) |
| D | 3 series + `build_joint_plurality_series` (pre-registered demographic denominator) |
| E | divergence test — confounded "divergence" caught, honest verdict |
| F | residual + robustness stack — robust null; correctness battery |
| G | Tier-2 lit-review honest disposition |
| — | PA-1/2/3 pre-registration amendments (Phase 2.2 opening) |

240 tests pass, ruff + mypy strict clean throughout.

## Surprises / lessons

- **Verify extreme claims (again).** The ratio "divergence" was striking, too
  clean, and contradicted the pilot's finding #2 — all red flags. Skepticism +
  the raw-trend check dissolved it. (Third time this discipline caught a
  would-be-wrong headline in the program.)
- **A ratio does not control for its denominator's own trend.** Dividing by
  demographic ≠ regressing it out; the ratio conflates "semantic declined" with
  "semantic rose slower." Any future divergence framing must separate absolute
  from relative.
- **Collinear confounds can be unidentifiable.** The "critical second figure"
  (residual regression) is defeated by year/volume/demographic collinearity —
  report the VIF, don't over-trust the coefficient.
- **Embedding-based semantic metrics are model-specific;** report ≥2 families
  and let the mixed-verdict rule adjudicate (the one decline reversed on swap).
- **Trust = independent agreement + placebos,** not "my tests pass." The
  year-shuffle + noise placebos are the checks that most directly validated
  *this* result.

## Implication for the program (WS3)

The result maps onto Whitespace 3's C–V (cumulative-complexity vs per-capita-
variance) decomposition: WS2's **canon concentration** empirically instantiates
WS3's endogenous-canonical-substrate conformity mechanism (κ#3); WS2's **rising
aggregate frontier diversity** is Henrich-consistent at the population scale but
is SILENT on WS3's *per-capita* V (WS2 measures the aggregate — the exact
aggregate-vs-per-capita conflation WS3 warns about). If the subfield test shows
concentration/diversity are independent, that supports WS3's *orthogonality*
(not strict-tradeoff) reconciliation. See the session hand-off for the full
mapping.

## Validation gates

| Gate | Result |
|---|---|
| Chu-Evans canonical in `src/` | ✅ |
| Drift gate clears (or E3) | ✅ clears |
| 3 series computed, CS + Physics | ✅ |
| Divergence test run per §5 + PA-2 | ✅ + confound diagnosed |
| Pipeline correctness verified | ✅ battery + tests |
| Tests + lint/typecheck clean | ✅ 240 pass |
| Figures | ◑ 3-panel draft (publication polish → Stage 3) |

## Companion documents

- `experiments/phase-2.2/divergence-verdict-results.md` (WS-E)
- `experiments/phase-2.2/robustness-and-verification-results.md` (WS-F + battery)
- `experiments/phase-2.2/drift-check-results.md` (WS-B)
- `experiments/phase-2.2/figures/phase2.2-3panel.png` (draft)
- Pre-registration: `docs/phases/phase-2.0-plan.md` §5
