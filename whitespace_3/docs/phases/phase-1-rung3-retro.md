# WS3 Phase 1 · rung 3 Retro — Conformity `κ` → the crossover `λ*` (THE lemma)

**Phase:** 1 (the ABM core), rung 3 · **Branch:** `ws3-phase-1-conformity-crossover`
**Window:** 2026-07-06 · **Status:** COMPLETE. `κ` added to the innovation operator;
the crossover established with CIs; 15 rung-3 tests (11 fast + 4 slow), 40 total;
ruff + mypy strict clean; pre-push hook enforces the gates.

---

## Hypotheses (pre-registered) and verdicts

| # | Pre-registered | Verdict |
|---|---|---|
| **H3** | The crossover: scaling-`κ` ⇒ ∃ `λ*` s.t. `∂V*/∂logN` CI `<0` for `λ>λ*`, `≥0` at `λ=0`. | **Confirmed.** Placebo (`λ=0`) slope `[+0.042,+0.069]`; `λ=0.5` slope `[−0.029,−0.018]` (CI entirely below 0). `λ*≈0.086`. |
| **H3a** | Dose–response: slope monotone decreasing in `λ` up to the floor. | **Confirmed.** `+0.055 → −0.007 → −0.030` as `λ`: 0→0.15→0.30. |
| **H3b** | The hump: interior peak `N*`; small-team advantage on the descending branch. | **Confirmed.** `V*(N)=[0.21,0.29,0.25,0.21]` for `N=[3,8,24,72]`, peak `N*≈8`. |
| **H4′** | Reconciliation: under scaling-`κ`, `∂C*/∂logN ≥ 0` **while** `∂V*/∂logN < 0`. | **Confirmed.** At `λ=0.25`: `C*` slope `[+11.4,+12.0]`, `V*` slope `[−0.047,−0.022]`. |

**Negative controls** — both confirm it is **absolute scale-tracking** consensus,
not the level and not the fraction, that bites:

- **NC1 (const, level-not-scaling):** `V*` slope `[−0.0001,+0.023]`, `hi≥0` — no crossover. ✓
- **NC2 (fraction, VC-style `κ ∝ max_e M / N ≈ 1`):** `V*` slope `[+0.001,+0.042]` at
  `λ=0.5` (rising, like the placebo) — no crossover. ✓ (Even at `λ=2` the CI straddles 0.)

**Spec-invariance (§2, the genuinely-open check):** the crossover sign holds across
**all four** `g ∈ {e^{−κ}, 1/(1+κ)}` × `s ∈ {ln max-redundancy, ln repsize}` combos
(slopes `−0.027, −0.016, −0.011, −0.013` at `λ=0.5`). Not mechanism-specific.

## Surprises / what the build resolved that the prototype could not

1. **NC2 (fraction) is a *cleaner* control than feared.** I expected the consensus
   *fraction* `max_e M / N` might drift up with `N` (founders lost at small `N`,
   ≈1 at large `N`) and produce a spurious weak crossover. It does not — at `λ=0.5`
   fractional-`κ` gives *rising* `V*`, indistinguishable from the placebo. Verified,
   not assumed (calibrated before the test threshold was written).
2. **The reconciliation holds without `γ`-sparing.** I worried that generic `κ`
   (throttling *all* innovation, including depth-extending) might drag `C*` down too,
   killing the reconciliation. It doesn't: `C*` at `λ=0.25` is essentially unchanged
   from `λ=0` (slope `+11–12` either way). **Why:** `C` is preservation-dominated
   (redundancy, untouched by `κ`) and even throttled vertical innovation `∝ ε·N^{1−λ}`
   still grows with `N` for `λ<1`. So `C` is *robust* to conformity while per-capita
   `V` is *fragile* to it — exactly the asymmetry the reconciliation needs, and it
   emerges in Tier 1 without the attachment/`γ` machinery. Stronger than expected.
3. **The crossover is *sharp* — `λ*≈0.086` is small.** Even weak scale-tracking
   conformity flips the sign; beyond `λ*` the descending branch dominates. Consistent
   with the reduced-form `s≈ln N` (a smooth power-law suppression `ε_eff≈ε·N^{−λ}`).

## Honest characterization + the ceiling (why rung 4 exists)

The Tier-1 crossover is a **clean but reduced-form existence proof**: well-mixed, the
only emergent signals are smooth functions of `N` (`max_e M ≈ N`), so `κ ≈ λ·ln N`
and `κ` is *uniform* across agents (everyone sees the same global state). The
**non-degenerate, heterogeneous, WS2-grounded driver — endogenous canonical
concentration `H`** — needs the multi-prereq attachment graph and is **rung 4 /
Tier 2**, which must reproduce this same sign-structure. What rung 3 delivers: the
crossover *exists*, `λ*` is *located with a CI*, the reconciliation *emerges*, and
the sign is *spec-invariant* and *control-isolated*.

## Anchors (reproduce-published-numbers standard)

The crossover is **WS3's novel contribution — no published number to hit** (WWE is
empirical; an ABM decomposing `C`/`V` with this crossover is new). Level 3 is
genuinely unavailable (documented). In force: the `κ=0` placebo (reduces to rung 2b),
the **two negative controls** (level, fraction), the **WWE qualitative shape** (hump +
per-capita decline), and **spec-invariance**. rung 4 substitutes endogenous `H` for
`ln N` and adds a WS2-calibrated comparison (not a Level-3 number).

## Process lesson

Calibrated every control/threshold with the *real* `conformity.py` (not the
throwaway) *before* writing the test assertions — which resolved the two genuinely
open questions (NC2 drift, spec-invariance) empirically rather than by hope, and set
non-flaky thresholds. (Appended to `tasks/lessons.md`.)

## Validation gates

- 15 rung-3 tests (11 fast in the pre-push gate: determinism, κ=0 regression,
  throttle primitives, THE crossover, hump, reconciliation, both controls,
  validation; 4 `slow`: thorough crossover, dose-response, spec-invariance, `λ*`).
  40 tests total. ruff + mypy --strict clean; `κ=0` regression byte-exact.

## Carry-forward to rung 4 (Tier 2 + robustness)

- **Endogenous `H`.** Replace the reduced-form `s≈ln N` with canonical concentration
  `H(t)=Gini(w)` on a **multi-prereq attachment graph** (elements draw prereqs `∝ w`,
  preferential attachment ⇒ `H` rises endogenously, WSC 3.1). The CD mechanism
  `κ=λ·H·(1−γ̄_i)` must reproduce this crossover — with **heterogeneous** `κ` (per-agent
  `γ`) and the `V^struct/V^lat` split.
- **Bounded degree ⇒ saturation.** Finite network degree `ρ` caps redundancy ⇒ `C`
  saturates (CC1) and the Strimling breadth equilibrium becomes matchable (the
  deferred rung-2b anchor).
- **Full robustness grid + phase diagram + Pareto/selective-isolation** (CC3/CC4).
