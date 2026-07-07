# WS3 Phase 1 · rung 4a — Endogenous canon `H` reproduces the crossover

**Whitespace:** 3 · **Phase:** 1 (the ABM core), rung 4a.
**Branch:** `ws3-phase-1-endogenous-canon`
**Status:** PLAN (plan-first; pre-registration locked before code).
**Builds on:** rung 3 (`conformity.py`) — which established the crossover on a
*reduced-form* signal `s ≈ ln N`. rung 4a's job is to **earn its keep**: replace
`ln N` with the real, endogenously-generated canonical concentration `H(t)` and
show the crossover survives.
**Formal spine:** primer Def canon (`w`, `H = Gini(w)`), Def 4.4 (CD mechanism),
Assumption 4.1 (κ must rise with scale), WSC 3.1 (`H` rises endogenously with scale).

---

## 0. Scope — the endogenous-`H` crossover (and *only* that)

Replace rung 3's reduced-form `κ = λ·s(t)` (`s ≈ ln N`) with the primer's
**canon-deviation driver** `κ = λ·H(t)`, where `H(t) = Gini(w)` is canonical
concentration on a **multi-prerequisite attachment graph** and `w(e)` is the
**dependency-closure weight** (how much later work transitively rests on `e`). Show:
(i) `H` rises endogenously with `N` (WSC 3.1, WS2's measured fact); (ii) the crossover
in per-capita `V` survives on this real `H`; (iii) the reconciliation `C*↑ / V*↓`
holds. The load-bearing "the mechanism is real, not a reduced-form artifact" step.

**Deferred (later rungs), explicitly out of scope here:**
- **rung 4b** — the *channel* refinement: canon-alignment `γ`, heterogeneous
  `κ_i = λ·H·(1−γ̄_i)`, the `V^struct/V^lat` split, and the WS2 `W↑` with
  `V^struct↓` signature. (rung 4a uses **uniform** `κ = λ·H`, generic suppression —
  the direct analog of rung 3, only with the real driver.)
- **rung 4c** — network topology (finite degree ⇒ `C` saturation + the Strimling
  breadth anchor).
- **rung 5** — analytics + phase diagram + Pareto/selective-isolation.

---

## 1. Pre-registered hypotheses

Prototype numbers from `scratchpad/verify_endogenous_H.py` (2026-07-07), which
de-risked the *precondition*; the build re-establishes on the *dynamic* model
(with `κ` feedback) at full rigor.

| # | Hypothesis | Criterion | Prototype |
|---|---|---|---|
| **H1** | **Endogenous `H` (WSC 3.1).** Closure-weight `H(t)=Gini(w)` rises with `N` (`∂H/∂logN > 0`), concave/saturating. | slope of `H*` on `log N` `> 0` | `H: 0.83→0.96` over `N=5→250` (closure) |
| **H1-robust** | **Crossover robust to the weight (revised — see §1a).** In the *dynamic* model both closure- and in-degree-`H` rise with `N` (the in-degree plateau was a *pure-PA* artifact), so the crossover holds under either weight — spec-robustness, not a knife-edge on closure. | crossover sign holds for `weight ∈ {closure, indegree}` | closure `0.80→0.96`; in-degree `0.75→0.88` (both rise) |
| **H2** | **The crossover on real `H`.** `κ = λ·H(t)` ⇒ ∃ `λ*` s.t. `∂V*/∂logN < 0` for `λ>λ*`; `≥0` at `λ=0`. Confirmed but **weak** — `λ*≈2` (larger than rung 3's `ln N` value, H's range is compressed near 1) and slope `~−0.01` (vs rung 3's `−0.03`): the reduced-form *overstates* the crossover. | slope CI `<0` for `λ≫λ*`; `≥0` at 0 | λ=3: slope `−0.010`, CI `[−0.013,−0.007]` |
| **H3** | **Reconciliation.** Under `κ=λ·H`, `∂C*/∂logN ≥ 0` **while** `∂V*/∂logN < 0`. | `C*` slope `≥0`, `V*` slope `<0` | (to establish) |

### Negative controls (pre-registered)

| # | Control | Must show |
|---|---|---|
| **NC0** | κ=0 placebo. | `V*` flat-or-rising in `N` (no crossover) — the rung-2b/3 null on the new substrate. |
| **NC-const** | **Fixed `H` (no N-scaling):** drive `κ = λ·H_ref` at a fixed reference instead of the live `H(t)`. | **no crossover** (`V*` slope CI `≥0`) — isolates that it is `H` *rising with `N`* that bites, not the suppression level. *(Verified: fixed-`H` slope CI includes 0.)* |

### 1a. Why the pre-registered "NC-weight" control was dropped (plan-first correction)

The prototype showed in-degree Gini *plateaus* while closure Gini rises, suggesting
"drive `κ` by in-degree ⇒ no crossover" as a killer control. **On the dynamic model
this does not hold:** in-degree `H` *also* rises with `N` (`0.75→0.88`) — the plateau
was specific to pure preferential-attachment graph growth, absent the transmission +
vertical-innovation dynamics. So both weights drive a crossover. That is *reframed as
spec-robustness* (H1-robust: the crossover holds under either weight), and the clean
"it's the *scaling* that bites" control becomes **NC-const** (fixed `H`), the direct
analog of rung 3's constant-`κ` control.

**Honest-null clause.** If the crossover does **not** survive on the real `H` (e.g.
the `κ`-feedback — suppressing innovation shrinks the graph and *lowers* `H` — cancels
the rise), that is a **major, reportable finding**: the reduced-form `ln N` and the
endogenous `H` would diverge, and the WS2-grounded mechanism would need rethinking
(or the crossover is genuinely reduced-form only). Either outcome is a real result.

---

## 2. Representation — the multi-prerequisite attachment graph

Generalizes rung 2b/3's single-parent tree to a **multi-parent DAG** (primer's
attachment structure), the minimal change that makes `w`/`H`/preferential-attachment
well-defined.

- **Elements:** `level[e]`, `birth[e]`, and a **prereq list** `prereqs[e]` (the `p`
  elements it builds on; `[]` for roots). `ℓ(e) = 1 + max(level of prereqs)`.
  Coherence: an agent holds `e` only if it holds **all** of `prereqs[e]`.
- **Innovation (κ throttled):** with prob `ε·g(κ)` an agent mints an element
  attaching to `p` prereqs drawn `∝ w` (preferential attachment) from what it holds.
- **Canonical weight `w(e)` = dependency-closure count** (# elements whose prereq
  closure contains `e`). Maintained **incrementally** (each new element increments the
  closure-count of all its ancestors) so `H = Gini(w)` is an `O(E log E)` sort per
  generation — the verified-crucial choice (in-degree would plateau, §1).
- **Driver:** `κ(t) = λ·H(t)` (uniform; the CD mechanism minus the `γ` heterogeneity,
  which is rung 4b). One-generation lag on `H` is acceptable (H moves slowly).
- **Outputs:** `C(t)` reproducible frontier (deepest fully-held chain, generalized to
  multi-prereq closure), per-capita `V(t)` persistence-filtered (as rung 2b), plus
  `H(t)` and repertoire breadth `W(t)` (effective # of elements / clusters — the
  collective-breadth gauge, for the reconciliation context).

Well-mixed agents (topology is rung 4c). Explicit representation (decision-A lineage);
sweep-scale optimization deferred.

---

## 3. TEST (TDD — written and green before any claim)

- **T1 — determinism.** Same seed ⇒ byte-identical `(C, V, H)` trajectory.
- **T2 — κ=0 placebo (NC0).** On the multi-prereq substrate, `κ=0` ⇒ per-capita `V*`
  flat-or-rising in `N` (the null the crossover bends; not byte-identical to
  `innovation.py` — different substrate).
- **T3 — endogenous `H` (H1).** `H*` (closure) rises with `N` (slope `>0`, seed-CI).
  Metric correctness of `w` (closure) and `Gini` on hand-built DAGs, and the
  incremental closure maintenance matches `closure_weights` from scratch.
- **T4 — reproducible frontier + `V` correctness** on hand-built multi-prereq states
  (coherence over *all* prereqs; the `k`-gen persistence filter).
- **T5 — THE crossover on real `H` (H2, headline).** `κ=λ·H`: slope of `V*` on
  `log N` is `≥0` at `λ=0` and `<0` for `λ≫λ*` (seed-bootstrap CI); `λ*` located.
- **T6 — reconciliation (H3).** Under `κ=λ·H`, `C*` slope `≥0` while `V*` slope `<0`.
- **T7 — NC-const (fixed-`H`) + spec-robustness.** `κ = λ·H_ref` (no N-scaling) ⇒
  no crossover (`V*` slope CI `≥0`); and the crossover sign holds under both
  `weight ∈ {closure, indegree}` (H1-robust).
- **T8 — input validation** (`p≥1`, `λ≥0`, `weight ∈ {closure,indegree}`, …).

Fast sign-checks gate the pre-push hook; thorough tight-CI variants are `slow`.

---

## 4. Estimand + estimation discipline (unchanged from rung 3)

Steady-state `H*`, `C*`, `V*`, `W*` = post-burn-in window means with across-seed CIs.
The crossover = **regression slope of `V*` on `log N`, seed-bootstrap CI**; `λ*` where
it crosses 0 — never two-point. Absolute `C*`/`V*` separate — never a ratio.

---

## 5. Anchor status (reproduce-published-numbers standard)

- **`H` rising with `N` = the WS2-consistency anchor (WSC 3.1).** WS2 *measured*
  canonical concentration rising endogenously with field scale (reference-canonicity
  Gini ↑ over 1970–2023; Chu–Evans rank-stability ↑). rung 4a reproduces that
  **qualitative shape** (rising, concave/saturating) from preferential attachment —
  the model earning its WS2 grounding. Not a Level-3 *number* (absolute Gini values
  differ — our closure-Gini starts high); documented as a shape/direction match.
- **The crossover remains WS3's novel result** — no published number (Level 3 N/A,
  documented). Anchors: the `κ=0` placebo, the **NC-const control** (fixed `H` ⇒ no
  crossover — it is the *scaling* that bites), spec-robustness across the weight, and
  consistency with the rung-3 reduced-form crossover (both agree in sign; the
  endogenous one is weaker — the reduced-form overstated it).
- **Divergence check:** does the endogenous-`H` `λ*` differ from rung 3's `ln N`
  `λ*`? Expected yes (compressed `H` range ⇒ larger `λ*`); reported as characterization.

---

## 6. Module

- **`src/whitespace3/canon.py` (NEW)** — the multi-prereq graph model:
  `run(...)` (transmission + κ-throttled innovation on the DAG; returns
  `C, V, H, W, R_size`), `closure_weight`, `gini`, and `endogenous_H` measurement.
  Reuses `suppression` / `variance_series` from `innovation.py` and the slope/CI
  toolkit from `conformity.py` (generalized to take a `run_fn`).
- **`tests/test_canon.py` (NEW)** — T1–T8.
- Minimal generalization of `conformity.steady_grid` to accept `run_fn=run` so the
  crossover toolkit serves both substrates.

## 7. Validation gates (rung 4a "done")

1. T1–T8 green (fast in the pre-push gate; thorough `slow` under `make test-all`);
   ruff + mypy strict clean; pre-push hook passes.
2. H1: `H` rises endogenously with `N` (closure); crossover robust across
   `weight ∈ {closure, indegree}` (H1-robust).
3. **H2 met:** the crossover survives on real `H` (weak but seed-CI `<0`), `λ*` located.
4. H3 met: reconciliation `C*↑ / V*↓`.
5. NC0 (placebo) + NC-const (fixed `H`) controls pass.
6. Anchor status documented (§5); the crossover characterized as *weaker* than
   rung 3's reduced-form (the honest divergence).
7. rung-4a retro written.

## 8. Non-goals (guardrails)

No `γ` / heterogeneous `κ` / `V^struct` split (rung 4b), no network topology
(rung 4c), no phase diagram / analytics (rung 5), no Modal sweep. One rung, one job:
**the crossover survives on the real endogenous `H`.**
