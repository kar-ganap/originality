# WS3 Phase 1 · rung 4a Retro — Endogenous canon `H` reproduces the crossover

**Phase:** 1 (the ABM core), rung 4a · **Branch:** `ws3-phase-1-endogenous-canon`
**Window:** 2026-07-07 · **Status:** COMPLETE. Multi-prereq attachment-graph model
with `κ=λ·H(t)` (closure-weight `H`); the crossover reproduced on the *real*
endogenous driver; 12 rung-4a tests, 52 total; ruff + mypy strict clean.

---

## Hypotheses (pre-registered) and verdicts

| # | Pre-registered | Verdict |
|---|---|---|
| **H1** | Endogenous `H` (closure-weight `Gini`) rises with `N` (WSC 3.1). | **Confirmed.** `H*: 0.80→0.96` over `N=5→200`, slope `+0.043`, CI `>0`. |
| **H2** | The crossover survives on the *real* `H`: `κ=λ·H` ⇒ `∂V*/∂logN < 0` for `λ>λ*`. | **Confirmed but WEAK + fidelity-gated** (see Sensitivity). `λ*≈2`, slope `−0.010` (CI `[−0.013,−0.007]`) at `f≥0.5`; **absent at `f=0.3`**. |
| **H3** | Reconciliation `C*↑ / V*↓` under `κ=λ·H`. | **Confirmed.** At `λ=3`: `C*` slope `>0` (CI `>0`) while `V*` slope `<0`. |

**Controls:** NC0 (κ=0 placebo) `V*` flat-or-rising ✓; **NC-const** (fixed `H`, no
N-scaling) `V*` slope CI includes 0 — no crossover ✓ (isolates that it is `H` *rising
with `N`* that bites). **Spec-robustness:** the crossover sign holds under
`weight ∈ {closure, indegree}`.

## The headline finding: the reduced-form OVERSTATED the crossover

rung 3's crossover rode `s ≈ ln N`, which has a wide dynamic range → a strong decline
(slope `−0.03`, `λ*≈0.09`). The **real** endogenous driver `H = Gini(closure)` is
**compressed near 1** (`0.80→0.96`), so the same mechanism gives a **much weaker**
crossover (slope `~−0.01`, `λ*≈2`). This is the honest, load-bearing result of rung 4a:
*the crossover is real on the WS2-grounded driver, but the reduced-form materially
overstated its strength.* The reconciliation (`C↑` while `V↓`) is robust either way —
`C` remains preservation-dominated and unbothered by `κ` (as in rung 3).

## Sensitivity / robustness (added in response to "did we test robustness?")

A one-axis-at-a-time sweep (`f, ε, b, p, g`) around the baseline, with seed-CIs:

- **The precondition `∂H/∂N > 0` is fully robust** — `H` rises with `N` under *every*
  setting (`+0.019` to `+0.066`).
- **The crossover survives 8 of 9 settings** (`f=0.7`, `ε∈{0.25,0.55}`, `b∈{0.2,0.6}`,
  `p=3`, `g=hyper`) — but **fails at low fidelity (`f=0.3`)**: `V*` *rises* with `N` at
  every `λ` (squeezed between the substrate's persistence-rise at low `λ` and `V→0`
  flooring at high `λ`; verified up to `λ=20`).
- **Mechanism (crisp).** The crossover needs the `H`-driven suppression gradient to
  beat the substrate's own persistence-rise. At `f=0.3` the persistence-rise is
  *steepest* (`κ=0` `V`-slope `+0.085`, per rung 2b) *and* the `H`-rise is *weakest*
  (`+0.019`) → suppression loses. At `f=0.6` the persistence-rise is flat (`−0.001`)
  and `H`-rise strong (`+0.063`) → suppression wins easily.

**The deeper lesson (sharper than "weak").** rung 3's reduced-form `s = ln N` rises
with `N` *regardless of `f`*, so its crossover was `f`-robust **by construction**. The
real endogenous `H` *depends on `f`*, so the real crossover is **`f`-gated**. The
reduced-form overstated not only the crossover's *strength* but its *robustness* — it
masked the fidelity-dependence. (In the low-`f` regime the model gives `C↑` with
`V↑` — **orthogonality, not trade-off** — which is itself WS2-consistent, WSC:indep:
the two reconciliation modes are separated by fidelity.) Captured as
`test_crossover_requires_fidelity` + `test_H_rises_robust_across_params` +
`test_crossover_robust_in_valid_regime` (slow), and the `g_map` axis (missing vs
rung 3) was added to `canon.run`.

## Surprises / corrections (verify-on-the-real-model, not the prototype)

1. **The "in-degree plateaus" contrast was a pure-PA artifact.** The scouting
   prototype (graph growth under pure preferential attachment, no agents) showed
   in-degree `Gini` plateauing (`0.51→0.57`) while closure rose — motivating an
   "NC-weight killer control" (in-degree-`κ` ⇒ no crossover). **On the dynamic model
   this is false:** with transmission + vertical innovation, in-degree `H` *also*
   rises (`0.75→0.88`). So both weights drive a crossover. **Corrected before building:**
   dropped NC-weight, reframed as **spec-robustness** (crossover holds under either
   weight), and adopted **NC-const** (fixed `H`) as the clean "it's the scaling" control.
   *Lesson: calibrate controls on the real model; a simplified prototype can invent a
   false contrast.*
2. **`H` had to be closure, not in-degree, for the *precondition* — but the crossover
   is robust to it dynamically.** Closure was the verified-essential choice for the
   prototype's `∂H/∂N > 0`; on the full model both rise, so the crossover survives
   under either. Closure remains the faithful (primer) choice and the one we drive.
3. **`κ`-feedback did not cancel the rise.** A pre-registered risk was that
   suppressing innovation shrinks the graph and *lowers* `H`, cancelling the crossover.
   It doesn't — `H` stays high under suppression (a small concentrated graph is still
   concentrated), so `∂H/∂N > 0` and the (weak) crossover survives.

## Representation + engineering notes

Multi-parent DAG (elements carry a *prereq list*; coherence = hold **all** prereqs).
Closure weight maintained **incrementally** (each new element increments its ancestors'
descendant counts; verified byte-equal to `closure_weights` from scratch). `κ=λ·H`
uniform. Preferential attachment on `(in-degree+1)`; `H` = `Gini(closure)`. The
`conformity` crossover toolkit was generalized to take a `run_fn`, so the same
slope/CI/`λ*` machinery serves both substrates.

## Anchor status

- **`H` rising with `N` = WS2-consistency (WSC 3.1)** — a qualitative *shape* match to
  WS2's measured reference-canonicity rise (not a Level-3 number; our closure-Gini
  starts high). The model earns its WS2 grounding: concentration rises endogenously
  from preferential attachment.
- **The crossover stays novel** (no published number; Level 3 N/A). Anchored by the
  `κ=0` placebo, **NC-const** (scaling, not level), spec-robustness across the weight,
  and *sign-agreement with the rung-3 reduced-form* crossover (both negative; the
  endogenous one weaker).

## Validation gates

15 rung-4a tests (determinism; κ=0 placebo; `H` rises; `gini`/`closure`/frontier
correctness + incremental==scratch; the crossover; reconciliation; NC-const +
spec-robustness; validation; **3 slow robustness: `H`-rise across params, crossover
across `ε/b/p/g`, and the fidelity boundary**). 55 total. ruff + mypy strict clean;
pre-push gate green.

## Carry-forward

- **rung 4b — the channel refinement (Tier 2 proper).** Add canon-alignment `γ(e)`
  (share of prereqs canonical), heterogeneous `κ_i = λ·H·(1−γ̄_i)`, and the
  `V^struct/V^lat` split; show `κ` bites the *structural* channel while sparing
  lateral/content → the WS2 signature `W↑` with `V^struct↓` (WSC channel). This may
  also *strengthen* the crossover (targeting structure concentrates the suppression).
- **rung 4c — network topology** (finite degree ⇒ `C` saturation + the Strimling
  breadth anchor); **rung 5** — analytics + phase diagram + Pareto/isolation.
