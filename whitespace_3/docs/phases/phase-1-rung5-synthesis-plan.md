# WS3 Phase 1 · rung 5 — Synthesis: the reconciliation deliverable + analytics + at-scale

**Whitespace:** 3 · **Phase:** 1 (the ABM core), rung 5 — the capstone.
**Branch:** `ws3-phase-1-rung5-synthesis`.
**Status:** PLAN (scope). 5a detailed (next); 5b headline-level (plan-when-reached).
**Formal spine:** Core Claims `cc:reconcile` (CC3) + `cc:robust` (CC4); the ABM plan
`phase-1-abm-core-plan.md` §3 rung 5 (light analytics) + the *un-done* rung-4 deliverables
(reconciliation, phase diagram) surfaced in the rung-4e retro's honest scope audit.

**Decisions locked (this session):**
- **Pareto route:** two-channel **orthogonality** as the primary framing (κ→`C`/`H`,
  τ→`V^struct`, what WS2+2.4 show) **+ a light selective-isolation `ι` demo** (so H4's
  concrete intervention is literally exhibited).
- **At-scale:** the **full Modal sweep is IN** (the stipulated §6 grid), not a spot-check.

---

## 0. Scope — close the five open Phase-1 items

The rung-4e retro's audit found five stipulated-but-open Phase-1 deliverables: (1) light
analytics, (2) the phase diagram, (3) the Pareto/selective-isolation half of the
reconciliation, (4) robustness-grid completion, (5) the at-scale Modal sweep. rung 5 closes
all five, split at the natural seam:

- **rung 5a — the reconciliation *deliverable*** (laptop-scale): the phase diagram + the
  Pareto claim. The paper's centerpiece; items (2)+(3).
- **rung 5b — analytics + robustness + at-scale**: light mean-field analytics, grid
  completion, and the full Modal sweep. The formalisation + rigor; items (1)+(4)+(5).

---

## 1. rung 5a — the reconciliation deliverable (detailed)

### 1.1 The phase diagram (item 2)
Map, at laptop scale (moderate grids, seed-CIs, reusing `conformity.steady_grid` /
`logN_slope_ci`):
- **`(λ, N)` plane** — locate the **`λ*` crossover locus** (where `∂V^struct*/∂ log N`
  changes sign) and partition into a **C-favouring** region (large `λ`: consensus
  dominates, `V^struct` falls in `N`) and a **V-favouring** region (small `λ`: more minds
  help). This is the load-bearing figure.
- **`(N, ρ)` plane** — show the **trade-off** columns: `∂C*/∂ρ > 0` while
  `∂V^struct*/∂ρ < 0` (density preserves depth, suppresses per-capita structural novelty).
- Estimands: absolute `C*` and `V^struct*` per cell (post-burn-in mean, across-seed CIs),
  **never a `C/V` ratio** (the WS2 ratio≠control lesson); the crossover is a **regression
  slope on `log N`**, never a two-point difference.

### 1.2 The Pareto / non-strict-trade-off claim (item 3)
**Primary — orthogonality (synthesis, no new mechanism).** WS2 Phase 2.3 + 2.4 + rung 4d
established that `C`/`H` (attachment/κ) and `V^struct` (content/τ) are **independent
channels**. So the `(C, V^struct)` Jacobian has **same-sign directions** (raise both) as
well as opposite-sign ones — the trade-off is *not strict*. The "both up" region is where
preservation (large `N,ρ` → `C↑`) coexists with fragmentation (many niches → `V^struct↑`).
This is the data-faithful route to `cc:reconcile`'s non-strict clause.

**Corroborating — selective isolation `ι` (a light build).** Exhibit the primer's concrete
prototype: add an `isolated_frac` of agents **shielded from κ** (`κ_eff = 0` for the
subgroup) while the majority feels conformity. Pre-registered prediction: the **isolated
subgroup's `V^struct` stays high** while **global `C` is preserved** (the whole population's
redundancy protects depth) — a concrete `∂C*≥0, ∂V^struct*>0` intervention. Minimal
addition to `channel.run` (a subgroup mask on `κ_eff`), same optional-param pattern as
rung 4e's topology.

### 1.3 Pre-registered hypotheses (5a)

| # | Hypothesis | Criterion |
|---|---|---|
| **H-cross** | the `(λ,N)` plane has a locatable `λ*` separating a V-favouring (small λ) from a C-favouring (large λ) region | `∂V^struct*/∂logN` slope-CI crosses zero at a finite `λ*` |
| **H-trade** | the `(N,ρ)` plane shows opposite-sign columns: `C*` up, `V^struct*` down in `ρ` | both signs, seed-CIs exclude 0 |
| **H-pareto-orth** | a same-sign direction exists (`∂C*≥0` **and** `∂V^struct*>0`) — the trade-off is not strict | a mapped region / direction with both rising |
| **H-pareto-iso** | selective isolation (`ι` subgroup, `κ_eff=0`) raises subgroup `V^struct` without lowering global `C` | `V^struct_iso > V^struct_conformist`, `C_global` not depressed |
| **placebo** | `ι=0` (no isolation) ⇒ no subgroup effect; `λ=0` ⇒ no crossover | flat |

### 1.4 TEST (5a, TDD)
- **T1 determinism** (the `ι` path; well-mixed `ι=0` byte-identical to rung-4b/4e).
- **T2 crossover locus:** `λ*` located with seed-bootstrap CI; V-region vs C-region.
- **T3 trade-off:** `(N,ρ)` opposite-sign columns.
- **T4 Pareto (orthogonality):** a same-sign `(C,V^struct)` direction exists.
- **T5 Pareto (isolation):** `ι` subgroup raises `V^struct`, global `C` preserved; `ι=0`
  placebo flat.
- **T6 input validation** (`isolated_frac ∈ [0,1)`).
- Deliverable: the phase-diagram figure(s) + the crossover law, regenerable from committed
  code.

---

## 2. rung 5b — analytics + robustness + at-scale (headline; plan-when-reached)

- **Light analytics (item 1).** Mean-field steady states — `C*(N,f,ρ)` via
  carrier-survival / branching, `V*(N,κ)` via innovation net of κ-suppression — and an
  **analytic `λ*` condition** that matches the simulated crossover *qualitatively*
  (simulation-guided, not a cold theorem; the compass says "keep analytics light").
- **Robustness-grid completion (item 4).** The §5 grid's remaining un-crossed axis is
  **memory-with-decay retention** (deferred at rung 4c: `λ_f = U/(1−β−r)`, a 2nd Strimling
  number `1.0`); everything else (κ-modes, `g∈{exp,hyper}`, ER/WS/BA, `b/ε/p`) is covered.
  Complete the **headline κ-mechanism × topology cross**; document any remainder honestly.
- **Full Modal sweep (item 5).** The stipulated §6 grid:
  `N∈{10,30,100,300,1000,3000} × ρ × f × κ-mech × λ × topology`, **30 seeds/cell**,
  `T≈300` (+burn-in). Embarrassingly parallel over `(cell×seed)` via Modal `.map`;
  **server-side scalar summaries** only (the Phase-2.3 payload lesson); **resumable
  per-cell + `return_exceptions=True`** (the Phase-2.1/2.3 resume lessons); any coverage
  cap `log`ged. **VERIFY the phase diagram + `λ*` survive at scale.** Budget **< \$50**
  CPU, no GPU; **spend logged in `tasks/spend.md` at time of incurring**.

---

## 3. Validation gates

1. **5a:** T1–T6 green; ruff + mypy strict; pre-push hook. The phase diagram + `λ*` locus +
   both Pareto routes (orthogonality region **and** the `ι` intervention) established,
   figure regenerable.
2. **5b:** analytic `λ*` matches simulated qualitatively; grid completion documented; the
   Modal sweep reproduces the laptop phase diagram at scale (sign-structure invariant);
   spend logged.
3. Retro: Phase 1 **actually** complete (all five items closed), the two-channel
   reconciliation stated, `cc:reconcile` + `cc:robust` both established.

## 4. Non-goals

- No new *mechanism* beyond the light `ι` subgroup mask (5a) and memory-with-decay (5b).
- No airtight analytic theorems (mean-field, simulation-guided — the compass).
- No GPU / no scope drift toward WS1's realistic-agent model.
- 5a stays laptop-scale; the at-scale verification is 5b's Modal job.

## 5. Sequencing

**5a first** (laptop, the deliverable) → review/merge → **5b** (analytics → grid → Modal
sweep last, since it is the costliest and confirms rather than reveals). Each is a gated,
independently-reviewable rung.
