# WS3 Phase 1 · rung 3 — Conformity `κ` → the crossover `λ*` (THE lemma)

**Whitespace:** 3 · **Phase:** 1 (the ABM core), rung 3 of the 5-rung ladder.
**Branch:** `ws3-phase-1-conformity-crossover`
**Status:** PLAN (plan-first; pre-registration locked before code).
**Parent plan:** `docs/phases/phase-1-abm-core-plan.md` (§3 rung 3, H3).
**Formal spine:** `docs/primers/cv-reconciliation-primer.tex` (Def 4.2 innovation
`ε·g(κ)`, Def 4.4 κ-mechanisms, Assumption 4.1 the scaling requirement, CC2 WWE,
CC3 reconciliation).
**Builds on:** rung 2b (`innovation.py`) — the κ=0 baseline (H2 placebo: `V`
flat-or-rising in `N`) is the null this rung bends.

---

## 0. Scope — the Tier-1 minimal generic crossover

Add conformity pressure `κ` to the innovation operator (primer Def 4.2:
innovation fires with prob `ε·g(κ)`), where `κ` **rises with `N`** via an emergent
*absolute* consensus signal, and **establish the crossover**: per-capita `V*` flips
from rising (κ=0) to **falling** in `N`, with a locatable conformity-scaling
threshold `λ*`. This is **the load-bearing lemma** — the whole reconciliation needs
it.

**Tier 1, one job.** `κ` here is the *minimal generic* form (primer's two-tier
model): a single scale-tracking pressure that suppresses innovation **generically**
and **uniformly** across agents. Explicitly **deferred to rung 4 / Tier 2**:
heterogeneous / per-agent `κ`; the **endogenous-`H`** (canon-deviation) mechanism
that grounds `κ` in WS2's measured concentration; the `γ` canon-alignment and the
`V^struct/V^lat` split; network topology; the full robustness grid (3 mechanisms ×
3 topologies); the phase diagram + Pareto/selective-isolation.

**Why the reduced form is legitimate (and its ceiling).** Well-mixed, the only
emergent signals are smooth functions of `N` (the canon is held by ~everyone, so its
*absolute* backing `max_e M ≈ N`), so `κ ≈ λ·ln N` — the crossover is clean but
*transparent*. That is an honest existence proof of the mechanism; the
*non-degenerate, heterogeneous, WS2-grounded* driver (endogenous `H`) needs the
attachment graph and is **rung 4**, which must reproduce this same sign-structure.

---

## 1. Pre-registered hypotheses

Prototype numbers below are from a throwaway (`scratchpad/verify_crossover.py`,
2026-07-06) that de-risked the mechanism; the build re-establishes them at full
rigor (CIs, permanent tests, spec swaps).

| # | Hypothesis | Criterion | Prototype |
|---|---|---|---|
| **H3** | **The crossover (THE lemma).** With `κ` scaling in `N`, ∃ `λ*>0` s.t. for `λ>λ*` the slope of `V*` on `log N` is **negative** (seed-bootstrap CI < 0); at `λ=0` it is `≥0` (the rung-2b placebo). | slope CI: `≥0` at λ=0, `<0` at λ≫λ*; `λ*` = where the CI brackets 0 | `λ*≈0.12`; slope `+0.021→−0.012` as λ: 0→0.15 |
| **H3a** | **Dose–response.** Over the identifiable range above 0, `∂V*/∂logN` is **monotone decreasing in `λ`** (more scale-tracking conformity → more negative slope), until the `V→0` floor. | slopes non-increasing in λ across the grid | `+0.021,+0.016,+0.011,+0.006,−0.012` |
| **H3b** | **The hump (CC2 shape).** `V*(N)` has an **interior peak** `N*`: rising for `N<N*` (substrate persistence-gain), falling for `N>N*` (conformity) — the **small-team advantage** is the descending branch. | argmax of `V*(N)` is interior; `V*` higher at small `N` than large on the descending branch | peak `N*≈8`; e.g. λ=0.15: `0.22,0.28,0.26,0.22,0.19` |
| **H4′** | **Reconciliation preview (CC3 core).** Under scaling-`κ`, the **same lever moves the gauges oppositely**: `∂C*/∂logN ≥ 0` (Henrich, depth preserved) **while** `∂V*/∂logN < 0` (WWE). | `C*` slope `≥0` and `V*` slope `<0` at the same `λ,N`-grid | λ=0.15: `C*` slope `+10.3`, `V*` slope `−0.012` |

### Negative controls (pre-registered — the crossover must be *scale-tracking* conformity)

| # | Control | Must show |
|---|---|---|
| **NC0** | κ=0 placebo (from rung 2b). | no crossover (`V*` slope `≥0`) — regression guard. |
| **NC1** | **Level, not scaling:** constant `κ = λ·ln(1+N_ref)` (same suppression *level*, no `N`-dependence). | **no crossover** (`V*` slope `≥0`). Rules out "it's the level of suppression." *Prototype: slopes ~0.* |
| **NC2** | **Fraction, not absolute (VC-style):** `κ ∝` the consensus *fraction* `max_e M / N` (≈1, scale-free) instead of the absolute count. | **no crossover**. Rules out "any consensus signal works" — it must be the **absolute** (scale-tracking) canon, not the fraction. Operationalizes the VC-fails-well-mixed argument. |

**Honest-null clause.** If the crossover is **not** robust to the `g`/`s` spec swaps
(§2), it is mechanism-specific and reported as such (still a result: the `C`–`V`
opposition would be orthogonality-leaning, consistent with WS2 Phase-2.3). If a
negative control *does* produce a decline, the "scaling bites" reading is wrong and
must be diagnosed before any crossover claim — escalate as a substrate bug.

---

## 2. Robustness (light at rung 3; the full grid is rung 4)

The sign-structure of H3/H4′ must be **invariant** across:

| Axis | Settings (rung 3) |
|---|---|
| suppression map `g(κ)` | `e^{−κ}` **and** `1/(1+κ)` |
| consensus signal `s(t)` | `ln(1+max_e M)` (max redundancy) **and** `ln(1+|R(t)|)` (repertoire size) — both rise with `N` well-mixed |

A crossover that appears under only one `(g,s)` is flagged mechanism-specific (the
WS2 "one-family signal reversed under swap" caution, in simulation form). Full
`κ`-mechanism × topology invariance is rung 4.

---

## 3. TEST (TDD — written and green before any claim)

Trust = the rung-2b reduction (known baseline) + placebo/controls + CIs, ported.

- **T1 — determinism.** Same seed ⇒ byte-identical `(C, V)` trajectory with `κ` on
  (needed for the resumable rung-4 sweep).
- **T2 — κ=0 regression guard.** With `λ=0` / `kappa_mode="off"`, the engine is
  *identical* to rung 2b (`innovation.run`) — same code path; the rung-2b suite
  still passes unchanged. (The crossover only appears with `κ` on.)
- **T3 — throttle correctness.** `g(κ)` (both maps), `s(t)` (both signals), and the
  realized rate `ε·g(κ)` computed correctly on hand-built states; `g(0)=1`;
  `ε_eff ≤ ε`; `ε_eff` decreasing in `κ`.
- **T4 — THE crossover (H3), headline gate.** Scaling-`κ`: the seed-bootstrap CI of
  `∂V*/∂logN` is `≥0` at `λ=0` and `<0` at `λ≫λ*`; `λ*` is located where the CI
  brackets 0. (Estimator = regression slope of `V*` on `log N`, seed-bootstrap CI —
  never a two-point difference.)
- **T5 — the hump (H3b).** `V*(N)` has an interior argmax; `V*` is higher at small
  `N` than large on the descending branch (the small-team advantage).
- **T6 — reconciliation (H4′).** Under scaling-`κ`, `∂C*/∂logN ≥ 0` while
  `∂V*/∂logN < 0` on the same grid (absolute `C*`, `V*`, reported separately — never
  a `C/V` ratio).
- **T7 — NC1 (level-not-scaling).** Constant-`κ` at matched level ⇒ `V*` slope
  CI `≥0` (no crossover).
- **T8 — NC2 (fraction-not-absolute).** VC-style fractional `κ` ⇒ no crossover.
- **T9 — dose–response (H3a).** Slopes non-increasing in `λ` over the identifiable
  range.
- **T10 — spec-robustness (§2).** The crossover sign (slope `<0` at fixed `λ>λ*`)
  holds under both `g` maps and both `s` signals.
- **T11 — input validation.** `λ≥0`; `kappa_mode ∈ {off,scaling,const,fraction}`;
  `g_map ∈ {exp,hyper}`; `signal ∈ {maxredundancy,repsize}`; `N_ref≥1` when needed.

Heavy tests (T4–T10 run grids) get a fast default-suite version (small `N`/seeds,
in the pre-push gate) **and** a thorough `@pytest.mark.slow` version (tighter CIs)
for `make test-all`. The headline crossover (T4) runs in the default gate.

---

## 4. Estimand + estimation discipline (WS2 lessons, ported)

- **Per-cell:** steady-state `C*`, `V*` = post-burn-in window mean, **with
  across-seed CIs** — never a single run.
- **The crossover slope:** `∂V*/∂logN` = **regression slope of `V*` on `log N`**,
  seed-bootstrap CI; `λ*` = where that CI crosses 0. **Not** a two-point
  `V(N_big)−V(N_small)` (the WS2 two-point / ill-conditioned-σ lesson).
- **Absolute `C*` and `V*`, separately** — never a `C/V` ratio (WS2 ratio≠control).
  The reconciliation lives in the *joint sign pattern*.
- **Report `N*`** (the hump peak) alongside `λ*`.

---

## 5. Level-3 anchor status (reproduce-published-numbers standard)

**The crossover is WS3's novel contribution — there is no published *number* to
hit.** WWE (large-teams-develop / small-teams-disrupt) is *empirical*; an ABM that
*decomposes* `C` and `V` and exhibits the crossover is new ("No existing ABM
explicitly decomposes these" — the deep-research report). Level 3 is therefore
**genuinely unavailable** (documented reason: novel result, no prior model reports
this number). The strongest available anchors, in force:

1. **The κ=0 placebo (NC0)** — reduces exactly to rung 2b (already Level-3-adjacent:
   its `C`-side inherits rung 1's Henrich).
2. **The two negative controls (NC1 level, NC2 fraction)** — the discipline that the
   effect is *scale-tracking* conformity, not an artifact.
3. **The WWE qualitative *shape*** — per-capita decline with scale + the hump —
   reproduced.
4. **Spec-invariance (§2)** — the sign-structure survives `g`/`s` swaps.

**Caveat carried forward:** the reduced-form `s≈ln N` makes the mechanism
transparent; **rung 4 replaces `s` with the endogenous `H`** (non-degenerate,
heterogeneous, WS2-grounded) and must reproduce this same sign-structure — that is
where the mechanism earns its empirical grounding (and where a WS2-calibrated
comparison, not a Level-3 *number*, becomes the anchor).

---

## 6. Representation / module

- **`κ` lives in the innovation operator** (faithful to Def 4.2: innovation fires
  with prob `ε·g(κ)`). Add to `innovation.run(...)` the params
  `lam=0.0, kappa_mode="off", g_map="exp", signal="maxredundancy", n_ref=None`;
  defaults reproduce rung-2b behavior byte-for-byte (⇒ T2 holds by construction).
  Per generation: compute `s(t)` from state → `κ = λ·s` (scaling) / `λ·ln(1+n_ref)`
  (const) / `λ·(max_e M / N)` (fraction) / `0` (off) → `ε_eff = ε·g(κ)`.
- **`conformity.py` (NEW)** — the rung-3 measurement toolkit (reused by the rung-4
  sweep): `v_star_grid`, `c_star_grid`, `logN_slope` (regression + seed-bootstrap
  CI), `locate_lambda_star`, `hump_peak`.
- **`tests/test_conformity.py` (NEW)** — T1–T11.
- Uniform `κ` (no per-agent state) — heterogeneous `κ` is rung 4.

---

## 7. Validation gates (rung 3 "done")

1. T1–T11 green (fast default suite incl. the headline crossover); the thorough
   `slow` variants green under `make test-all`; ruff + mypy --strict clean;
   pre-push hook passes.
2. `κ=0` regression intact (T2) — rung-2b suite unchanged.
3. **H3 met:** the crossover, with a seed-CI `λ*` (not a two-point diff).
4. **H4′ met:** reconciliation preview — `C*↑` while `V*↓` under the same lever.
5. Both negative controls (NC1, NC2) show **no** crossover.
6. Spec-robustness (§2): crossover sign invariant to `g` and `s`.
7. Anchor status documented (§5) — novel result, Level 3 unavailable, reason stated.
8. rung-3 retro written (hypotheses → what happened → surprises → carry-forward).

## 8. Deliverables

- `src/whitespace3/innovation.py` (κ added) + `src/whitespace3/conformity.py`
  (crossover toolkit).
- `tests/test_conformity.py` (T1–T11, permanent).
- `docs/phases/phase-1-rung3-retro.md`; CLAUDE.md "current state" → rung 3 COMPLETE.

## 9. Non-goals (guardrails)

No network topology, no heterogeneous/per-agent `κ`, no endogenous `H`/`γ`, no
`V^struct/V^lat` split, no phase diagram / Pareto-isolation, no Modal sweep, no
performance optimization. One rung, one job: **the crossover `λ*`, rigorously.**
