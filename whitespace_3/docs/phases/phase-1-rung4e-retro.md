# WS3 Phase 1 · rung 4e retro — topology robustness

**Branch:** `ws3-phase-1-topology-robustness` · **Window:** 2026-07-07
**Status:** COMPLETE. The κ-signature (`V^struct↓` with breadth `W` spared) is invariant
across well-mixed / ER / WS / BA. This closes Core Claim `cc:robust` — the κ-spec half was
rungs 3/4a/4b, the topology half is now done. 7 tests (6 fast + 1 slow); 75 fast total;
ruff + mypy strict clean.
**Plan:** `phase-1-rung4e-topology-robustness-plan.md`.

---

## Hypotheses and verdicts

| # | Pre-registered | Verdict |
|---|---|---|
| **H0** | well-mixed default byte-identical to the pre-4e model | **✓** — arrays equal (no regression to rungs 4a/4b) |
| **H1** | targeted κ lowers `V^struct` vs `κ=0`, on every topology | **✓** — `V^struct`: WM `.18→.15`, ER `.17→.12`, WS `.18→.13`, BA `.15→.12` |
| **H2** | κ does not collapse `W` on any topology | **✓** — `W` stays `>0.5×` off (spared) everywhere |
| **H3** | κ steepens the `V^struct`-vs-`log N` decline on each topology | **✓** — `slope(targeted) ≤ slope(off)` on ER/WS/BA (seed-bootstrap) |
| **placebo** | `κ=0` ⇒ no suppression on a graph | **✓** — `off` ≈ `targeted,λ=0` |

## What it establishes

The load-bearing κ-crossover result — conformity suppresses **structural** per-capita
novelty while sparing the **breadth** channel — is **not an artifact of the well-mixed
assumption**. It holds on a fixed finite-degree interaction graph, random / small-world /
scale-free alike. Together with the ≥2–3 κ-specs of rungs 3/4a/4b, this is the full
`cc:robust`: **the sign-structure is invariant to both the functional form of κ and the
interaction topology.** That is what makes the reconciliation a qualitative claim rather
than a fitted one.

## Surprises / notes

- **Nothing killed it** — even BA hubs (which concentrate transmission) did not break the
  signature. The honest-null clause was not triggered.
- **Magnitude varies, sign does not.** Suppression is a touch deeper on ER/WS than
  well-mixed and shallower on BA; the *sign* is invariant, which is exactly the `cc:robust`
  claim (not a magnitude match).
- **Cheap and clean** — the overlay is one localised change (neighbour-carriers
  `A @ base` via a `scipy.sparse` adjacency); well-mixed stays the fast path and
  byte-identical, so the RNG stream is untouched and rungs 4a/4b are unaffected.

## Honest limits

- **Sign-structure, not magnitude** (as pre-registered).
- **Self-loops added** to the graphs so an agent counts its own prior holding — a modelling
  choice for parity with well-mixed (`base.sum` includes self); the sign-structure is not
  sensitive to it.
- **Moderate `N`** (laptop-scale, sparse adjacency); no large-`N` / Modal sweep.
- The crossover remains **weak** (rung 4b's finding); κ steepens the decline on every
  topology but the effect is small — the robust claim is the *sign*.

## What's next

- **rung 5 (synthesis)** — the phase diagram / Pareto / Results, now able to state full
  `cc:robust` (κ-specs × topologies) and the two orthogonal channels (concentration via
  `κ`; fragmentation via `τ`, rung 4d). This is the program's capstone.
