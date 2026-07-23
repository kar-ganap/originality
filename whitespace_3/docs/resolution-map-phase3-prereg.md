# Phase 3 pre-registration: noise-floor diagnostics for the resolution map

**Registered 2026-07-22, before running.** Parent design: `docs/counterfactual-resolution-map.md` §3.
This gate decides *which estimands are candidates* for the full sweep and *what seed/point budget* the
sweep needs. Its thresholds are gameable if chosen after seeing results, so they are fixed here.

Model pinned at `dbd367a` (`channel.run`, `innovation.run`, `conformity.*`). Any change to those files
voids this pre-registration.

## Corrections after smoke-testing (2026-07-22, before the real run)

A tiny smoke run (3 seeds) exposed two estimands whose **lever or metric was mis-assigned** relative
to where the phenomenon actually lives in the model. These are specification fixes made *before* the
real grid, from the model's structure (not from any threshold moving to fit a desired result), and
they are recorded here so the change is auditable:

- **E2 pointed at the wrong lever.** It required `W` to *rise* as **λ** rises. The smoke showed `W`
  *falls* under conformity but rises steeply in **N** (381→1674→6303), while `Vstruct` falls in N.
  The two-channel decoupling is a *scale* effect (as WS2's is an over-*time* effect), so E2 is now an
  **N-slope** test, not a λ-response. User set reading (a) — the internal N-decoupling — as primary.
- **E4 used the wrong metric.** It measured the crossover on `Vstruct`, which only ever *declines* in
  N (no sign flip is possible). The V-favouring→C-favouring crossover was always a **total-V**
  phenomenon; the focused check confirmed `Vstruct`'s N-slope is negative at every λ, while total-V
  under *targeted* rises at every λ. E4 now measures total-V under **both** modes (the original λ*
  was a uniform-mode, total-V result). User agreed.

Thresholds (SESOI, det_tol, the grid) are unchanged; only the estimand definitions for E2 and E4 are
corrected. E1, E3, E5 unchanged.

## Reproducibility pins

- **Baseline anchor** (the vetted phase-diagram point): `c0=5, f=0.6, epsilon=0.3, b=0.5,
  generations=60, alpha=0.15, burn_in=30`. `mode="targeted"` for the V^struct / W estimands (rung 4b:
  targeting is what spares breadth); `mode="uniform"` reported alongside as a contrast, not the primary.
- **Determinism/CV seed set**: `seed ∈ range(30)` at each grid point.
- **Estimand outputs** (keys of `channel.run`): `Vstruct`, `W`, `Vstruct_iso`, `Vstruct_conf`, `C`, `H`.
  Steady state = mean over generations `[burn_in:]`.

## The fixed diagnostic grid (no point chosen after peeking)

Small, spanning the regimes; `channel.run` is O(N²) so N is capped for the cheap phase.

- **λ ∈ {0.0, 0.1, 0.5, 2.0}** — placebo / near the putative low-H crossover / clear C-favouring / the
  high-H crossover (rung 4a `λ*≈2` on real `H`). λ=0 is included *because* it is the known C-clock — the
  detector must flag it, which validates the detector.
- **N ∈ {30, 120, 480}** — small / mid / large-but-feasible.
- **f ∈ {0.3, 0.6}** — out-of-regime / in-regime (rung 4b/4a f-gating).
- α, topology (`well_mixed`), `bw` held at baseline (they are §4/§5's robustness axes, not the noise floor).

Grid = 4 λ × 3 N × 2 f = 24 points, each run at 30 seeds. All 24 are reported; none is dropped.

## SESOI per estimand (WS1's floor, translated into model units — fixed now)

WS1's rung-0 gate resolves a **20% relative `V` decline** at n=10. Translated:

- **E1 — `Vstruct(λ)` level.** SESOI = 20% relative change in steady-state `Vstruct` vs the λ=0 baseline
  at the same N. (rung 4b's 0.22→0.02 is ~90%, ~4.5× the floor.)
- **E2 — two-channel decoupling (N-lever, internal). Corrected 2026-07-22 after smoke, see below.**
  The signature is a **scale** response (matching WS2's over-*time* pattern), not a λ-response.
  Internal standard, per (mode, f, λ): `∂W/∂logN` CI entirely **> 0** *and* `∂Vstruct/∂logN` CI
  entirely **< 0**. Targeted mode primary (user, 2026-07-22). A secondary WS1-relevant reading (b) —
  conformity crushes `Vstruct` more than `W` under λ — is reported as a contrast.
- **E3 — isolation Pareto.** SESOI = `(Vstruct_iso − Vstruct_conf) ≥ 20%` of `Vstruct_conf`.
**E4 and E5 are N-slopes, which WS1 never varies, so they get an *internal-relevance* standard, not
the WS1 floor (decision 2026-07-22).** The question they answer is "does the model have this structure
at all," and only if it does do we (a deferred stage 2) ask whether it is steep enough to matter at
WS1's resolution.

- **E4 — the `∂V*/∂logN` crossover, total-V, both modes. Corrected 2026-07-22 after smoke, see below.**
  Internal standard = a **CI-separated sign flip** across λ: ∃ a lower λ whose slope CI lies entirely
  **above 0** (V-favouring) *and* a higher λ whose slope CI lies entirely **below 0** (C-favouring),
  in that order. This is exactly what "the model has a crossover" means; per-point SESOI is 0
  (sign-determination only). Magnitude is **not** judged here — the tiny-but-significant risk is
  deferred to **stage 2**: *if* the flip exists, apply the WS1 translation
  `SESOI_slope = 0.20 · V_ref / Δln N` over the pinned N range. Existence first, magnitude second.
- **E5 — the `∂C/∂logN` response.** Internal standard = the slope's CI excludes 0 at any λ, i.e. `C`
  actually depends on `N` rather than being a pure `t`-clock. Per-point SESOI 0 (sign-determination).
  Same deferred stage-2 magnitude check if it survives.

## The 4-way classification rule (applied per estimand × lever × grid point)

Using 30 seeds at each point; CI = 2.5/97.5 percentile seed bootstrap:

1. **deterministic-flat** — seed-CV of the output < `1e-6` (float-tolerance, not a science threshold)
   **and** |response to the lever| < SESOI. → EXCL. The lever does nothing and there's no uncertainty.
2. **deterministic-clock** — seed-CV < `1e-6` **and** |response| ≥ SESOI. → EXCL for counterfactual use
   (a deterministic prediction carries no stochastic uncertainty to test against WS1's stochastic
   measurement), but reported as color. This is the expected verdict for `C` at λ=0.
3. **stochastic-with-signal** — seed-CV ≥ `1e-6`, CI excludes 0 (C1), **and** |effect| ≥ SESOI (C2). → the
   only USABLE class. Candidate for §4.
4. **stochastic-noise-dominated** — seed-CV ≥ `1e-6` but CI includes 0 or |effect| < SESOI. → run the
   power curve (below): if the CI half-width shrinks below SESOI/2 at an affordable seed/point budget,
   it is *rescuable* (promote to §4 at that budget); otherwise it is *intrinsically mush*.

## The two supporting diagnostics

- **Variance decomposition.** At each point, nested sampling separates seed variance from graph-draw
  variance (relevant once topology ≠ well_mixed). Reports each as a fraction of total, so a
  noise-dominated verdict is attributed to a fixable vs intrinsic source.
- **Power curve.** CI half-width as a function of `n_seeds ∈ {6, 12, 24, 48}` and
  `n_N-points ∈ {3, 5, 8}`. **Adequate power** ≡ half-width < SESOI/2. The output is the (seeds, points)
  budget §4 must use — decided by this curve, not after §4 disappoints.

## Pre-registered predictions (so a surprise is flagged, not absorbed)

(Predictions below reflect the corrected E2/E4 specs, informed by the smoke; the real 30-seed grid
either confirms them or flags a miss.)

- **E1 (`Vstruct` level vs λ)**: stochastic-with-signal, well above SESOI → USABLE.
- **E2 (N-decoupling, targeted)**: `∂W/∂logN` reliably > 0 AND `∂Vstruct/∂logN` reliably < 0 → USABLE.
  (Smoke: W-slope ≈ +1300, Vstruct-slope ≈ −0.01, both CI-separated — strong.)
- **E3 (isolation Pareto)**: stochastic-with-signal → USABLE (lower confidence; untested for CI).
- **E4 (crossover, total-V, both modes)**: under **targeted**, no flip (total-V rises at every λ) →
  EXCL. Under **uniform**, genuinely uncertain — the original λ*≈0.09 lived here, but the audit found
  it CI-straddling at scale. If a CI-separated flip appears under uniform, stage 2 decides whether it
  clears WS1's floor; if not, EXCL and the reconciliation crossover is confirmed mush at n=30.
- **E5 (`∂C/∂logN`, internal)**: N-range-scoped. At the §3 grid (N≤480) the smoke showed `C` *rising*
  with N (contra the audit's ∂=0 at N=200–1500), so E5 may read internally-usable here while being
  flat at scale — I predict CI-excludes-0 at λ>0 → provisionally USABLE-at-this-N, flagged as a
  regime-local verdict, not a contradiction of the large-N audit.

Any estimand landing in a class other than predicted is called out explicitly in the retro.

## The §3 → §4 decision rule (mechanical)

- Estimands classified **stochastic-with-signal** at ≥1 grid point → proceed to §4, swept around those
  points.
- **E4/E5 (internal standard)**: proceed to §4 iff the internal test passes — a CI-separated sign flip
  for E4, a CI-excluding-0 N-response for E5. If it passes, **stage 2** (the WS1-magnitude translation)
  runs in §4 to label it WS1-testable vs internal-only; a §4 estimand can be "internally real but below
  WS1's floor," which is reported, not dropped.
- Estimands **stochastic-noise-dominated but rescuable** by the power curve → proceed at the budget the
  curve specifies.
- Estimands **deterministic (flat or clock)** or **intrinsically mush** → excluded, listed in the §4 doc
  as non-usable with the reason.
- **If no estimand is usable or rescuable** → stop; report "WS3 is not a usable counterfactual engine"
  (design doc §6 negative-result contingency). Do not proceed to §4.

## Tests-first (TDD for the two new functions)

Before running on the model, the diagnostic functions get known-answer tests:

- clock-detector: a deterministic series (`C=1+t`) → classified deterministic; a Gaussian-noise series →
  stochastic. A deterministic series with a nonzero lever response → deterministic-clock, not -flat.
- variance-decomposer: synthetic data with a known seed/graph variance split → recovers the fractions.
- SESOI translation: a hand-checked case (20% of a known `Vstruct_ref` over a known `Δln N`) → matches.

## What this phase does NOT decide

Not the §4 sweep design beyond the (seeds, points) budget; not the C3 robustness axes (topology/bw/
calibration — those are §4/§5); not any counterfactual claim. This phase only classifies estimands and
sizes the sweep.
