# WS3 Phase 1 · rung 4e — Topology robustness: the κ-signature on ER/WS/BA

**Whitespace:** 3 · **Phase:** 1 (the ABM core), rung 4e.
**Branch:** `ws3-phase-1-topology-robustness`.
**Status:** PLAN (plan-first; pre-registration locked before code).
**Formal spine:** Core Claim `cc:robust` — the sign-structure must be invariant across
"random, small-world, and scale-free topologies" (ER / WS / BA), the topology half of the
robustness claim (the κ-spec half was done in rungs 3/4a/4b).

---

## 0. Scope — the deferred Phase-2 topology remnant

The κ-**crossover** (rungs 3/4a) and the **channel signature** (rung 4b: `W↑` with
`V^struct↓`) were all established on **well-mixed** agents (`channel.py`: *"Well-mixed
agents; topology is rung 4c"*). rung 4c did finite-degree *sampling* for the
independent-trait breadth substrate (`roles.py`, fresh `n`-sample each generation) — a
*different* substrate, re-randomized, not a persistent interaction graph carrying the
crossover. So **whether the κ-signature survives on a fixed finite-degree topology is
untested**, and `cc:robust` pre-registers exactly this.

**Scope (small).** Put the existing `channel.py` `V^struct` model on a **fixed finite-degree
interaction graph** (ER / WS / BA) — transmission acquires from **graph-neighbour carriers**
instead of global carriers — and re-test that the **sign-structure is invariant**: targeted
κ suppresses `V^struct` while sparing breadth `W`, on every topology. No new mechanism; a
robustness overlay on a committed model.

---

## 1. Pre-registered hypotheses

Criteria are steady-state (post-burn-in mean, seed-replicated) at a crossover-regime
`λ` (rung 4b used `λ=0.25`, `f≥0.5`, `α≤0.15`). "Topology-invariant" = the *sign* holds on
each of {well-mixed, ER, WS, BA} at matched mean degree.

| # | Hypothesis | Criterion |
|---|---|---|
| **H0** | **Regression: well-mixed is the identity.** `topology="well_mixed"` is byte-identical to the current `channel.run` (no graph built, RNG stream untouched). | arrays equal |
| **H1** | **Structural suppression, sign-invariant.** On ER/WS/BA (and WM), targeted κ lowers `V^struct` vs `κ=0`. | `Vstruct(targeted) < Vstruct(off)` on each topology |
| **H2** | **Breadth spared, sign-invariant.** κ does not collapse collective breadth `W` on any topology (targeting spares content). | `W(targeted) ≳ W(off)` (not crushed) on each |
| **H3** | **Crossover sign-invariant (slow).** The `V^struct`-vs-`log N` slope under κ is ≤ its `κ=0` value on each topology (κ makes per-capita structural novelty *fall harder* in `N`, everywhere). | `slope(targeted) ≤ slope(off)` per topology, seed-bootstrap |
| **placebo** | `κ=0` ⇒ no suppression on any topology (the sign-structure is κ-driven, not a graph artifact). | `Vstruct(off)` not depressed vs its own `W` |

**Honest-null clause.** If a topology *kills* the signature (e.g. BA hubs so dominate
transmission that `V^struct` no longer responds to κ), report it — that is a real
boundary of `cc:robust`, not a failure to hide. The claim is **sign-invariance where the
crossover exists** (`f≥0.5`, `α≤0.15`), not universality.

---

## 2. Representation / module

Extend **`channel.run`** with an optional interaction topology (minimal, default-unchanged):

- New params: `topology: str = "well_mixed"`, `mean_degree: int = 8`, `graph_seed: int = 0`.
- **`well_mixed` (default):** the current fast path (`carriers = base.sum(axis=0)`) — no
  graph, RNG untouched ⇒ **byte-identical** (H0).
- **`er`/`ws`/`ba`:** build a fixed graph once via `networkx`
  (`erdos_renyi`/`watts_strogatz`/`barabasi_albert`) at the target mean degree, add
  self-loops (so an agent counts its own prior holding, matching well-mixed semantics),
  convert to a `scipy.sparse` adjacency `A`; transmission becomes per-agent
  `carriers = A @ base` (neighbour holdings). The graph is fixed across generations
  (persistent topology), built from `graph_seed` (separate from the dynamics `seed`).
- Everything downstream (coherence, γ-targeted innovation, `variance_split`) is unchanged.

Measurement reuses `conformity.steady_grid` / `logN_slope_ci` with `run_fn=channel.run`
and `topology=...` forwarded via `**run_kw`.

## 3. TEST (TDD — green before any claim)

- **T1 — determinism** (with a topology; same `seed`+`graph_seed` ⇒ identical).
- **T2 — H0 regression:** `topology="well_mixed"` output equals the no-arg call, arrays equal.
- **T3 — graph sanity:** ER/WS/BA realized mean degree ≈ target; connected enough to transmit.
- **T4 — H1 structural suppression, sign-invariant:** `Vstruct(targeted) < Vstruct(off)` on
  ER/WS/BA.
- **T5 — H2 breadth spared:** `W(targeted)` not collapsed vs `W(off)` on each topology.
- **T6 — placebo:** `κ=0` gives no κ-suppression on any topology.
- **T7 — input validation** (bad `topology`, `mean_degree` out of range).
- **T8 — H3 crossover sign (slow):** `Vstruct`-vs-`logN` slope under κ ≤ its `κ=0` value on
  each topology (seed-bootstrap CI).

## 4. Validation gates (rung 4e "done")

1. T1–T8 green; ruff + mypy strict clean; pre-push hook passes.
2. **H0** byte-identical well-mixed (no regression to rungs 4a/4b).
3. **H1 + H2 sign-invariant** across ER/WS/BA (the `cc:robust` topology half).
4. Retro: `cc:robust` now complete (κ-specs × topologies); any topology boundary noted.

## 5. Non-goals

- **No new mechanism** — a transmission-topology overlay on `channel.py` only.
- **No magnitude claim** — `cc:robust` is *sign-structure* invariance; the crossover
  strength may vary with degree/topology.
- **No re-derivation of the crossover** (rungs 3/4a/4b own it); rung 4e only tests its
  topology-robustness.
- **No Modal / large-N sweep** — laptop-scale, moderate `N`, sparse adjacency.
- One rung, one job: **show the κ-signature (`V^struct↓`, `W↑`) survives on ER/WS/BA.**
