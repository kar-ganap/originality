# Resolution map: where does the WS3 model make crisp counterfactual predictions?

**Status: design outline, 2026-07-22. Not executed.** Prerequisite for any counterfactual use of the
WS3 machinery (feeding intervention hypotheses to WS1). Written before running, hypotheses-first.

## 0. Why this exists

An independent audit found that at scale (N=200–1500) the model's headline estimand — the crossover
slope `∂V*/∂logN` — has a seed-bootstrap CI that **straddles zero**, and `∂C/∂logN ≈ 0.0000` exactly.
A model whose own counterfactual is "effect indistinguishable from zero" is not a usable what-if
engine there. Before WS3 can generate intervention hypotheses for WS1, we must **map where in
parameter space the model's signal exceeds its own noise floor** — treat the model as an instrument
and characterize its resolution.

This is *not* an attempt to rescue `λ*`. It is a characterization that may well conclude "the crossover
slope is mush everywhere and the usable predictions are a different output form" — or even "there is
no usable envelope," which is a valid and decision-relevant result (see §6).

## The reframe that changes the target: test the output *form*, not just the headline

The famous estimand — the sign flip of `∂V*/∂logN` — is the **weakest** thing the model produces:

| finding | source | implication |
| --- | --- | --- |
| crossover slope weak, `~−0.01` on real `H`, CI straddles 0 at scale | rung 4a, the audit | the N-slope form is likely mush |
| conformity crushes `V^struct` **level** 0.22 → 0.02 (~90%) at fixed N | rung 4b | the **level** form is a huge effect |
| two-channel sign-opposition (`W↑` while `V^struct↓`) topology-invariant | rung 4b/4e | the **sign-structure** form is robust |
| `∂C/∂logN ≈ 0`, `C(t)=1+t` at λ=0 (deterministic clock) | the audit | the C-side may be trivial, not crisp |

**And WS1 measures levels, not N-slopes.** The rung-0 gate is "`V_output` declines ≥20% vs a matched
ablation" — a level contrast at fixed configuration. WS1 never varies N. So the estimand that (a) is
likely crisp and (b) actually matches the downstream test is the **level-response and the
sign-opposition**, not the crossover slope. The map should center on those.

## 1. The crispness criterion (pre-registered; four conjunctive conditions)

A model prediction at a parameter point is **usable** iff all hold:

- **C1 — excludes zero.** The effect's seed × graph-draw bootstrap CI excludes 0 (reuse the
  `conformity.logN_slope_ci` percentile-bootstrap pattern, extended to level and difference
  estimands).
- **C2 — exceeds the downstream floor (SESOI).** `|effect| ≥` a smallest-effect-of-interest tied to
  **what WS1 can detect**, not chosen for convenience. Anchor: the rung-0 gate resolves a ~20%
  `V` decline at n=10 (one-sided Wilcoxon). A model effect below WS1's floor is crisp-in-model but
  untestable, therefore not usable. (rung 4b's ~90% level crush clears this by 4×; the crossover
  slope does not clear it in the right units at all.)
- **C3 — sign-robust to nuisance.** The *sign* survives topology `∈ {well_mixed, er, ws, ba}`, the
  plausible `bw` range, and baseline-calibration uncertainty. Magnitude is allowed to vary (rung 4e
  showed sign topology-invariant, magnitude degree-dependent); only the sign is load-bearing.
- **EXCL — not deterministic-trivial.** A prediction that is "crisp" only because the output is
  deterministic (C(t)=1+t counts time) is excluded. Diagnosed in §3(a). This is the trap of
  mistaking a clock for a measurement.

## 2. The estimand catalog (rank by expected crispness, then let the map decide)

| id | estimand | form | prior expectation | matches WS1? |
| --- | --- | --- | --- | --- |
| **E1** | `V^struct(λ)` at fixed N — the conformity crush | level | crisp, large (4b) | **yes** (level contrast) |
| **E2** | `sign(dW/dλ) = +` while `sign(dV^struct/dλ) = −` | sign-opposition | robust (4b/4e) | partially |
| **E3** | isolation Pareto: `V^struct_iso − V^struct_conf` vs `isolated_frac` | difference | untested for CI | **yes** (subgroup contrast) |
| **E4** | `∂V*/∂logN` vs λ, and `λ*` | slope | mush (audit) | no (WS1 fixes N) |
| **E5** | `∂C/∂logN` | slope | ~0 / trivial | no |

Pre-registered expectation: **E1, E2, E3 usable; E4, E5 not.** If the map inverts this — e.g. E4
turns out crisp in some regime — that is a genuine surprise to report, not a target to steer toward.

## 3. Noise-floor characterization (cheap; do this FIRST, before any sweep)

The point is to rule out regions cheaply and diagnose *why* a CI includes zero, distinguishing three
very different causes:

- **(a) Deterministic-trivial audit.** At a fixed parameter point, vary *only* the seed. If output
  variance ≈ 0, the output is deterministic — "crisp" but vacuous (the C(t)=1+t case). Run this on C
  first; if C is a clock, the entire C-side (E5) is excluded here, not in the expensive sweep.
- **(b) Variance decomposition.** Decompose output variance into seed / graph-draw / parameter
  components (nested sampling). Tells us whether a zero-crossing CI is *noise-dominated* (a real
  effect under-powered — fixable with seeds) or *intrinsically null* (the model genuinely predicts
  nothing). Only the first is rescuable.
- **(c) Convergence / power curve.** CI half-width as a function of `n_seeds`, number of N-points,
  and `burn_in`. The current `phase_diagram.py` uses **6 seeds and 4 N-points** — almost certainly
  under-powered for a slope CI. Find the (seeds, points) that halve the CI, so §4 is run at adequate
  power rather than re-discovering under-power as "mush."

Deliverable of §3: a cheap verdict on which estimands are even *candidates*, and the seed/point
budget the real sweep needs.

## 4. The sweep (the resolution map proper)

For each surviving estimand, sweep the axes that the rungs showed matter, and flag each cell
`{usable / noise-dominated / intrinsic-null / deterministic-trivial}`:

- **λ** — fine grid near the putative crossover (0–0.3) *and* the high range (`λ*≈2` on real `H`,
  rung 4a): the crossover lives at very different λ depending on the driver.
- **N** — more points than 4, extended via the existing Modal path (`experiments/phase-1-rung5/
  modal_sweep.py`, which already did 300 cells to N=1500).
- **f (fidelity)** and **α (canon tightness)** — rung 4b found the signature needs `f ≥ 0.5` and
  `α ≤ 0.15`; a prediction crisp only inside a narrow `f`-band is fragile and must be *swept*, not
  fixed, so the envelope's boundaries are explicit.
- **topology, bw, isolated_frac** — for the C3 robustness axis and E3.

Reuse: `innovation.run` / `channel.run`, `conformity.steady_grid`, `conformity.logN_slope_ci`;
add level- and difference-estimand CI functions in the same bootstrap style.

## 5. Robustness + falsifiability gate

A usable cell must additionally pass:

- **C3 in practice** — recompute the sign across topology, across the `bw` range, and across
  baseline-calibration perturbations (resample `m`, `K(t)`, `niche_specific_ref_share` within their
  empirical CIs from `calibration.json`). Sign must hold.
- **Could-be-wrong** — there must be a plausible alternative outcome WS1 could observe instead. A
  prediction with no failing alternative is not a prediction. State, per usable cell, the WS1 result
  that would falsify it.

## 6. Deliverable: the usable envelope — and the negative-result contingency

- **The map:** "WS3 makes crisp (C1), meaningful (C2), sign-robust (C3), non-trivial (EXCL),
  falsifiable (§5) predictions on estimand E in region R; it is mute elsewhere." Each usable
  prediction written as a WS1-testable hypothesis with an explicit kill condition.
- **The explicit non-usable list** (expected: E4 crossover-slope, E5 C-side) — stated, so no one
  later reaches for a mush estimand.
- **Negative-result contingency (report honestly).** If *no* estimand is usable anywhere, the
  finding is "WS3 is not a usable counterfactual engine." That is decision-relevant: it says do
  **not** spend WS1 compute testing WS3 predictions, and it should be reported as a result, not
  buried. The whole exercise is worth running precisely because this outcome is on the table.

## 7. Cost & feasibility

CPU numpy ABM. `channel.run` is O(N²) (noted in the WS3 retro; caps practical N ~1500–3000). The
existing Modal sweep did 300 cells to N=1500; the resolution map is more cells on the same
infrastructure — low dollar cost, dominated by design and compute time, not spend. §3 is laptop-cheap
and gates whether §4 is worth running at all.

## 8. Discipline (so the map itself doesn't become a trap)

- **Pre-register the expected-crisp regions** (§2: E1/E2/E3 usable, E4/E5 not) before the sweep. The
  map confirms or surprises; it is not steered.
- **SESOI is fixed to WS1's floor before running** (§1 C2), not chosen after seeing effect sizes.
- **Deterministic-triviality is excluded** (§3a), so a clock is never sold as a prediction.
- **No parameter-tuning to manufacture crispness.** Finding the regime where the model *happens* to
  exceed its noise floor is legitimate; tuning `bw`/`f`/`α` until a CI clears zero is the same
  motivated move as the field-difference trap, one level down. The envelope is *found*, not fit.
