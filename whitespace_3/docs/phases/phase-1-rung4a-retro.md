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
| **H2** | The crossover survives on the *real* `H`: `κ=λ·H` ⇒ `∂V*/∂logN < 0` for `λ>λ*`. | **Confirmed but WEAK.** `λ*≈2`; at `λ=3`, slope `−0.010`, CI `[−0.013,−0.007]`. |
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

12 rung-4a tests (determinism; κ=0 placebo; `H` rises; `gini`/`closure`/frontier
correctness + incremental==scratch; the crossover; reconciliation; NC-const +
spec-robustness; validation). 52 total. ruff + mypy strict clean; pre-push gate green.

## Carry-forward

- **rung 4b — the channel refinement (Tier 2 proper).** Add canon-alignment `γ(e)`
  (share of prereqs canonical), heterogeneous `κ_i = λ·H·(1−γ̄_i)`, and the
  `V^struct/V^lat` split; show `κ` bites the *structural* channel while sparing
  lateral/content → the WS2 signature `W↑` with `V^struct↓` (WSC channel). This may
  also *strengthen* the crossover (targeting structure concentrates the suppression).
- **rung 4c — network topology** (finite degree ⇒ `C` saturation + the Strimling
  breadth anchor); **rung 5** — analytics + phase diagram + Pareto/isolation.
