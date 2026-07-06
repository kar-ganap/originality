# WS3 Phase 1 · rung 2b Retro — Innovation → per-capita `V` (κ=0)

**Phase:** 1 (the ABM core), rung 2b · **Branch:** `ws3-phase-1-innovation-v`
**Window:** 2026-07-06 · **Status:** COMPLETE. Innovation operator + `C`/`V`
instrumentation built, TDD, 11 rung-2b tests green (25 total); ruff + mypy strict
clean; pre-push hook enforces the gates.

---

## Hypotheses (pre-registered) and verdicts

| # | Pre-registered | Verdict |
|---|---|---|
| **H1′** | Innovation restores `C`-growth above `c0`; `C*` non-decreasing in `N`, `f`. | **Confirmed** — with `ε>0`, `C` exceeds `c0` (vertical innovation extends depth); `C*` monotone in `f` in the preservation-limited regime; non-decreasing in `N`. |
| **H2** | The κ=0 placebo: per-capita `V*` flat-or-rising in `N`, never decreasing (slope of `V*` on `log N`, seed-bootstrap CI ≥ 0). | **Confirmed** — slope CI not below 0 (T4); prototype: `V` rises from `0.05→0.30` at low `f`, ~flat at high `f`, saturating at `ε`. |

The un-bundling is complete: rung 2a proved transmission alone cannot grow `C`;
rung 2b's innovation operator is the growth channel, and `V` (per-capita persisting
novelty) is now a first-class, separately-instrumented output.

## The surprise (the load-bearing finding): well-mixing → unbounded redundancy → **no saturation**

Two checks during the build converged on one structural fact about the *well-mixed*
κ=0 baseline:

1. **`V`-side (Strimling scout follow-up).** In the flat reduction (`b=0`, single
   level → independent traits), the repertoire grows **linearly at every `N`** (5 →
   400), never to a plateau. Reason: redundancy = *global* carrier count, so a trait
   seen by all `N` agents is lost only if all `N` fail (`≈(1−f)^{MN}→0`). Traits go
   **immortal**; there is **no `N`-independent innovation-loss equilibrium**.
2. **`C`-side (the failed-then-fixed `f` test).** With strong vertical innovation
   (`ε=0.3, b=0.8`) the depth frontier ratchets **ballistically** — `C(t)=c0+t`,
   `+1`/generation, and `C*` is **`f`-independent** above a low threshold (identical
   `55.0` at `f=0.4` and `f=0.95`). `C*` is *innovation-limited*, not
   *fidelity-limited*, here. Fidelity binds only when innovation is weak
   (`ε=0.05`: `C*` climbs `7.8→42.6` across `f`), which is where the H1′ `f`-test
   now lives.

**Both are the same fact:** with unbounded redundancy (well-mixing) nothing
saturates — `C` ratchets without bound, `V` saturates at `ε`, breadth grows without
bound. The primer's CC1 "increasing **and saturating**, threshold collapse below a
critical redundancy `m*`" shape and Strimling's `N`-independent equilibrium are
**bounded-redundancy phenomena** — they require finite degree `ρ` (a cap on `m`),
which is **rung 4**. This is not a bug; it is the honest characterization of the
well-mixed baseline, and it sharpens what rung 4 must add.

## Anchors (reproduce-published-numbers standard)

- **`C`-side:** un-bundling invariant (`ε=0` → rung 2a: `C` non-increasing, capped at
  `c0`; behavioral equivalence to `concept_base` within seed-CI) + qualitative
  Henrich (maintenance large-`N`, Tasmania small-`N`) — T1. The *quantitative*
  Henrich number (`N*≈616`, Mesoudi eq 9.4) stays at **rung 1** (Gumbel model); the
  concept-base substrate has no Gumbel `α/β`, so re-deriving it here would be a
  category error (corrected during planning).
- **`V`-side:** anchored by the **pre-registered κ=0 placebo (T4)**; no published
  Level-3 number exists for the exact well-mixed object (documented). Strimling 2009
  (breadth equilibrium) re-sited to **rung 4** — verified during planning that its
  `N`-independence needs bounded role-models, absent in well-mixing.

## Process lesson

Picked the *ballistic* (strong-innovation) regime for the initial `∂C*/∂f≥0` test,
where `f` doesn't bind → the test failed with `55.0 == 55.0`. Fix: **probe the
regime before asserting a monotonicity** (the same verify-before-baking discipline
that caught the Strimling mis-siting). The failure was diagnostic, not a code bug —
it surfaced the ballistic-growth finding above. (Appended to `tasks/lessons.md`.)

## Validation gates

- 11 rung-2b tests green (T1 un-bundling; T2 metric correctness incl. the `k`-gen
  persistence filter; T3 determinism; T4 the κ=0 placebo headline; T5 growth
  restored + `C*` monotone in `f`/`N`; T6 validation). 25 tests total.
- ruff + mypy --strict clean; pre-push hook passes.

## Carry-forward to rung 3 (add `κ` → the crossover)

- **Pre-register the `κ`-scaling BEFORE building rung 3.** The κ=0 placebo (this
  rung) is the null; rung 3 must show the WWE decline appears *only* with `κ` rising
  in scale (Assumption 4.1), and the negative controls (random-`κ` must not
  reproduce it).
- **rung 3 needs the deferred machinery:** canon `K_α`/weight `w`/concentration `H`,
  canon-alignment `γ`, and the `V^struct/V^lat` split — the single-parent tree
  generalizes to a multi-prereq attachment (drawn `∝ w`) so `γ` is graded and `H`
  rises endogenously (WSC 3.1). Additive; does not invalidate rung-2b tests.
- **rung 4 owns saturation + the Strimling anchor:** bounded degree caps redundancy
  → `C` saturates (CC1), traits can be lost at large `N` → the `N`-independent
  breadth equilibrium (Strimling 2009, the fetched paper) becomes matchable.
