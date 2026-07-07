# WS3 Phase 1 · rung 4b Retro — The channel refinement: WS2's `W↑` with `V^struct↓`

**Phase:** 1 (the ABM core), rung 4b · **Branch:** `ws3-phase-1-channel-refinement`
**Window:** 2026-07-07 · **Status:** COMPLETE. Targeted `κ` (`κ_eff=λ·H·(1−γ)`) on the
multi-prereq graph; the WS2 two-channel signature reproduced; 10 rung-4b tests, 65
total; ruff + mypy strict clean.

---

## Hypotheses (pre-registered) and verdicts

| # | Pre-registered | Verdict |
|---|---|---|
| **H1** | Under targeted `κ`: `W↑` (breadth) **while** `V^struct↓` (structural novelty), together. | **Confirmed.** `W` slope CI `[+113,+119]`; `V^struct` slope CI `[−0.012,−0.006]`. |
| **H2a** | Targeting spares breadth vs uniform. | **Confirmed.** `W` slope +116 (targeted) vs +25 (uniform); `V^lat↑` (targeted) vs flat (uniform). |
| **H2b** | `κ` crushes the structural *level* vs κ=0. | **Confirmed.** `V^struct*` ≈ 0.02 (targeted/uniform) vs ≈ 0.22 (off) — ~10×. |
| **H3** | Reconciliation `C*↑` while `V^struct↓`. | **Confirmed.** `C*` slope CI `[+2.4,+3.9]` while `V^struct↓`. |
| **H4** | Total per-capita `V` need not fall (breadth thrives). | **Confirmed.** total-`V` slope `≈ +0.02` (rises). |
| **H5** | Fidelity gate persists (deep, not uniform-κ artifact). | **Confirmed.** `V^struct↓` at `f≥0.5`, flat at `f=0.3`. |

**Controls:** NC0 (κ=0) leaves `V^struct` high + breadth free; NC-uniform collapses
breadth (`W` +25, `V^lat` flat) — the two discriminators. γ non-degeneracy: structural
fraction `0.43→0.04` across `N`.

## The headline: WS2's actual fingerprint, and an honest decomposition

Targeted `κ` reproduces **WS2's measured two-channel pattern** — collective breadth
`W↑` (WS2's rising topical diversity) **while** per-capita *structural* novelty
`V^struct↓` (Core Claim 6, the open prediction). This is the strongest WS2-consistency
result in the program: **WSC:channel** (`κ` bites structure, spares content) **and**
**WSC:indep** (breadth does *not* collapse — the orthogonality WS2 found).

But calibration corrected a naive reading (`κ ⇒ V^struct↓`). The honest decomposition:
- **`V^struct`'s decline with `N` is partly endogenous** — it falls even at κ=0 (canon
  concentration makes new work increasingly canon-aligned; the structural *fraction*
  falls with scale). κ is not the cause of the *slope*.
- **What `κ` does to structure is crush its *level*** (~0.22 → ~0.02, both uniform &
  targeted).
- **What *targeting* uniquely does is spare breadth** (`V^lat↑`, `W` +116 vs uniform's
  +25). Only targeting gives the *full* fingerprint: structure low & falling **while**
  breadth thrives. κ=0 leaves structure high; uniform κ kills breadth.

## Resolves rung 4a's "weak crossover"

rung 3/4a measured *total* per-capita `V`, which conflates a **declining** structural
channel with a **thriving** breadth channel — so the total looked weak (and fragile).
Splitting them, the structural decline is clean, and total-`V` *rising* is correct
(large teams develop breadth; small teams disrupt structure). **The proper WWE measure
is `V^struct`, not total-`V`.**

## Two honest boundaries (from the baked-in sensitivity sweep)

The signature is robust across `ε, b, p, g, γ_thresh` — but has **two boundaries**:
1. **Fidelity** (carried from rung 4a): `V^struct↓` needs `f≥0.5`; flat at `f=0.3`.
2. **Canon tightness (new):** the signature needs `α≤0.15` (a *select few* are
   canonical); a broad canon (`α≥0.20`) washes it out — sensible, since "structural
   deviance" is only well-defined against a concentrated canon.

Both are interpretable, not fragilities: the WS2 fingerprint appears in fields that
transmit reliably *and* have a concentrated canon — which is exactly where WS2 measured
it (mature, canon-concentrated fields like Physics).

## Representation + engineering

New module `channel.py` (reuses `canon`'s `gini`/`closure_weights`/frontier;
`innovation.suppression`). `K_α` = top-`⌈αE⌉` by closure weight; per-innovation `γ` =
share of prereqs canonical; per-event suppression `g(λ·H·(1−γ))`; `variance_split`
partitions persisting novelty by birth `γ`-class. `conformity`'s toolkit now accepts
`Vstruct/Vlat/W` metrics. `mode ∈ {off, uniform, targeted}` makes the controls a clean
flip.

## Anchor status

The **WS2 signature is the anchor** — `W↑` (measured) with `V^struct↓` (CC6, the
V-extension's open prediction). A qualitative *signature* match (WSC:channel +
WSC:indep), not a Level-3 number; the crossover remains novel. NC-uniform is the
internal discriminator that *targeting* is essential.

## Validation gates

10 rung-4b tests (determinism; `variance_split` + `V^struct+V^lat==V`; the signature;
targeting-spares-breadth; κ-crushes-level; reconciliation; validation; **slow:** the
fidelity gate, the sensitivity sweep, the canon-fraction boundary). 65 total. ruff +
mypy strict clean.

## Carry-forward

- **rung 4c — network topology.** Finite degree ⇒ bounded redundancy ⇒ `C` saturation
  (CC1) + the Strimling breadth anchor becomes matchable; robustness across ER/WS/BA
  topologies; local (heterogeneous) `κ`. May also interact with the two boundaries.
- **rung 5 — analytics + phase diagram + Pareto/selective-isolation** (CC3/CC4).
