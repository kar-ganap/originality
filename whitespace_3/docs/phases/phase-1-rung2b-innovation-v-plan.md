# WS3 Phase 1 · rung 2b — Innovation → per-capita `V` (κ=0)

**Whitespace:** 3 · **Phase:** 1 (the ABM core), rung 2b of the 5-rung ladder.
**Branch:** `ws3-phase-1-innovation-v`
**Status:** PLAN (plan-first; no code until this is reviewed).
**Parent plan:** `docs/phases/phase-1-abm-core-plan.md` (§3 rung 2, H2, T4).
**Formal spine:** `docs/primers/cv-reconciliation-primer.tex` (Def 4.2 innovation,
Def 5.1 `C`, Def 5.2 `V`, Assumption 4.1 the κ-scaling requirement).

**Decisions locked (2026-07-06, pre-build):** (1) Representation **A** — explicit
`agents × elements` matrix now; carrier-count/sparse optimization deferred to
rung 4 as its own equivalence-tested rung (§2c). (2) V-side anchor — **fetching
Strimling 2009 (+ optional Kobayashi–Aoki 2012)** to hold T7 at Level 3; build
proceeds in parallel and T7's tier is finalized when the paper lands (§5a).

---

## 0. Scope — one rung, one job

Add the **innovation operator** to the concept-base substrate (rung 2a) with
conformity **off (`κ≡0`, so `g(κ)=1`)**, and instrument the two output gauges
`C(t)` and per-capita `V(t)`. That is the whole of rung 2b. Explicitly **out of
scope** here (later rungs): conformity `κ` and the crossover (rung 3); the
network topology `ρ` / `ι` (rung 4 — rung 2b stays **well-mixed**, inheriting
rung 2a's panmictic redundancy `m_k`=#holders); the `V^struct/V^lat` split and
`γ` canon-alignment (rung 3, where `κ` needs them).

**Why this rung matters.** rung 2a proved transmission *alone* can only preserve
or lose `C` (never grow it). Innovation is the growth channel. Adding it here —
*before* `κ* — gives us the honest **baseline** against which the whole thesis is
judged: with no conformity, per-capita `V` must **not** fall with scale (H2 / T4).
If it did, the later WWE decline would be an artifact of the substrate, not of
`κ`. rung 2b's deliverable is a *clean, decline-free `V` baseline* and the
machinery (`C`, `V`, persistence filter) that rung 3 then bends.

---

## 1. Pre-registered hypotheses (this rung only)

Restated from the parent plan's H1/H2; the crossover (H3) is **not** touched here.

| # | Hypothesis | Shape / criterion | Primer |
|---|---|---|---|
| **H1′** | Innovation restores `C`-growth: with `ε>0`, the reproducible frontier `C(t)` grows above `c0` (vs rung 2a where `max C = c0`), and steady-state `C*` is non-decreasing in `N` and `f`. | `C*` rises above `c0`; `∂C*/∂N ≥ 0`, `∂C*/∂f ≥ 0` | CC1 |
| **H2** | **The κ=0 placebo (the load-bearing pre-registration).** With conformity off, per-capita `V*` is **flat or increasing** in `N` — never decreasing. | slope of `V*` on `log N` has a CI that is `≥ 0` (does not lie below 0) | CC2 |

### 1a. Why `V` is flat-to-rising at κ=0 (the mechanism we are pre-committing to)

This is the honest core of the placebo, so we state the expected mechanism *before*
running:

- **Every innovation event mints a fresh element id** (primer: a novelty is "never
  previously instantiated"). So distinct innovation events = distinct elements —
  **no collisions**. Gross novelty per generation `≈ ε·N`, hence *gross* per-capita
  novelty `≈ ε` — **flat in `N` by construction.** (This is deliberate: it forbids
  a spurious *crowding* decline. A per-capita fall must come from `g(κ)<1` throttling
  the rate — rung 3 — not from the substrate.)
- **The persistence filter is the one place `N` can help.** A novelty counts only
  if it survives `≥ k` generations, i.e. ≥1 agent keeps carrying it (redundancy).
  Larger `N` ⇒ higher carrier redundancy ⇒ novelties clear the `k`-gen filter more
  often ⇒ `V*` **flat-to-rising** in `N`. That is the WWE-*contradicting* baseline
  that motivates `κ`: absent conformity, scale is (weakly) *good* for per-capita
  persisting novelty.

**Falsifier of our own substrate:** if `V*` comes out *decreasing* in `N` at
`κ=0`, rung 2b has a bug or a hidden crowding term, and no downstream crossover
claim is admissible until it is fixed (parent plan escape trigger).

---

## 2. Representation — concept → code (the decision to review before building)

The user's standing instruction: *show how the primer's concepts map to code
before building more.* Here is the mapping and the one real design fork.

### 2a. What rung 2b's dynamics actually require

| Primer object | Needed at 2b? | Why |
|---|---|---|
| Element `e` with level `ℓ(e)` (Def 2.1) | **yes** | `C` is a max over levels; vertical innovation makes `ℓ+1`. |
| Prerequisite `π(e)` / closure `Π(e)` (Def 2.2) | **yes, minimal** | coherence; vertical innovation needs a complete lower chain. |
| Concept base `B_i`, coherence (Def 2.4) | **yes** | who can innovate/transmit what; per-agent state. |
| Repertoire `R(t)`, carrier count `M(e,t)` (Def 2.5) | **yes** | loss, redundancy `m`, persistence filter. |
| Birth set `Δ(t)`, persistence `Δ^{(k)}` (Def 5.2) | **yes** | the definition of `V`. |
| content `τ(e)` / topical breadth `W` (Rem 2.3, Def 2.9) | **no** (defer) | needed for the WS2 `W` bridge (rung 4/H6), not for `V` at κ=0. |
| canon `K_α`, weight `w`, `H` (Def 2.8) | **no** (defer) | `κ`'s driver — rung 3. |
| canon-alignment `γ` (Eq 4.3), `V^struct/V^lat` | **no** (defer) | `κ` acts on `γ` — rung 3. |

So the **minimal sufficient representation** is: *explicit elements on a
prerequisite tree, explicit per-agent bases, well-mixed, no `κ`/`γ`/`τ` yet.*

### 2b. The recommended representation — a single-parent prerequisite **tree**

- **Element registry** (grows as innovation mints ids): parallel arrays
  `level[e] : int≥1`, `parent[e] : int` (the one lower-level element it extends;
  `-1` for level-1 roots), `birth[e] : int` (generation of first appearance).
  A single parent ⇒ `Π(e)` is the root→`e` path; `ℓ(e)=1+level[parent]`. This is
  the *minimal* DAG that is coherent, supports **vertical** (extend a held `e` to a
  new child at `ℓ+1`) and **lateral** (new sibling: a fresh element whose parent is
  an existing level-`(k-1)` element the agent holds) innovation, and makes every
  `C`/`V` quantity well-defined.
- **Agent bases** `B` as a boolean matrix `agents × elements` (coherent = closed
  under `parent`). Well-mixed ⇒ redundancy `m(e)=M(e,·)=B[:,e].sum()` (population
  carrier count), exactly rung 2a's `(tops>=k).sum()` generalized off the single
  chain.
- **`C(t)`** = `max level[e]` over `e` in the repertoire whose full chain is
  carried (reproducible frontier, primer Def 5.1 `C_R`); we will also log the
  population-max `max_i max ℓ(B_i)` and confirm they agree in the well-mixed case.
- **`V(t)`** = `|{e : birth[e]==t and e ∈ R(t..t+k)}| / N` (Def 5.2), evaluated
  with a `k`-generation lookahead (so `V` is reported up to `T−k`).

**Why single-parent (not the full multi-prereq DAG) now:** it is the minimal thing
that is *correct* for every rung-2b quantity, and it keeps the un-bundling honest
(one clean depth axis). **Extensibility flag for rung 3:** `κ`'s `γ` = "share of an
element's prereqs that are canonical" wants *multiple* prereqs per element to be
graded rather than binary; rung 3 will generalize `parent` → an attachment *set*
drawn `∝ w` (preferential attachment, which is also what makes `H` rise
endogenously per WSC 3.1). That generalization is additive and does not invalidate
rung 2b's tests. We note it now so we don't paint ourselves in.

### 2c. The one design fork I want a decision on

The `agents × elements` boolean matrix is **O(N · |E|)** and `|E|` grows ~`ε·N·T`.
For rung-2b *development and the T1–T4 gates* (small `N`, `T`) this is trivially
fine and maximally legible. For the **Modal sweep at `N=3000`, `T=300`** (rung 4)
it is ~10⁸ cells/seed — heavy. Two ways to handle it:

- **(A · recommended) Build rung 2b with the explicit matrix; log the scaling
  concern; defer the optimization to rung 4.** Rationale: minimal-first, the code
  is a direct transcription of the primer (easy to verify), and the sweep-scale
  representation (carrier-count reduction `M(e,t)` + sparse/CSR bases, exploiting
  well-mixedness so all agents share one acquisition prob per element) is itself a
  rung-4 task with its *own* equivalence test against the explicit matrix.
- **(B) Build the carrier-count-reduced representation now.** Faster at scale, but
  couples a performance optimization into the correctness rung and makes the T4
  placebo harder to read.

I recommend **(A)**: correctness-legible now, one clearly-scoped optimization rung
later, gated by an explicit-vs-reduced equivalence test. Flagging in case you'd
rather pay the complexity up front.

---

## 3. TEST (TDD — written and green before any sweep)

Ported from the parent plan's T-series, specialized to rung 2b. Tests first.

- **T1 — `C`-side regression guard (the un-bundling invariant).** With innovation
  *off* (`ε=0`), rung 2b reduces to rung 2a: `C` **non-increasing, capped at `c0`**
  (transmission alone cannot grow `C`), and `retained_complexity(N,c0,f,…)` matches
  rung 2a's within seed-CI (behavioral equivalence — not byte-identity, since the
  richer representation consumes RNG differently). Plus the *qualitative* Henrich
  regimes on the concept-base substrate: maintenance for large `N`/high redundancy,
  Tasmania loss for small `N`. *(This guarantees `C`-growth is the only thing the
  innovation operator changed.)* **NB:** the *quantitative* Level-3 Henrich number
  (`N*≈616`, Mesoudi eq 9.4) lives at **rung 1** (the Gumbel model, `transmission.py`)
  and is not re-derived here — the concept-base substrate has no Gumbel `α/β`, so a
  "re-bundle to eq 9.4" claim would be a category error (§5).
- **T2 — metric correctness on hand-built states.** `C(t)` (reproducible frontier),
  `Δ(t)`, the `k`-gen persistence filter, and `V(t)=|Δ^{(k)}|/N` computed correctly
  on ≤3 hand-constructed populations with known answers (including: a novelty that
  dies at `k−1` gens does **not** count; one that survives exactly `k` does).
- **T3 — determinism.** Same seed ⇒ byte-identical `(C, V)` trajectory (required
  for the resumable sweep and reproducibility).
- **T4 — the κ=0 placebo (H2), the headline gate.** Estimate the slope of `V*` on
  `log N` across `N ∈ {small…large}` at `κ=0`, with seed-bootstrap CIs; assert the
  slope's CI **is not below 0** (flat-or-rising, never a decline). This is the
  pre-registered guard that the WWE decline, when it appears in rung 3, is `κ`'s
  doing and not the substrate's.
- **T5 — innovation restores growth (H1′).** With `ε>0`, `max_t C(t) > c0` for a
  large well-mixed population (vertical innovation demonstrably extends depth),
  and `C*` is non-decreasing in `f` on a coarse grid.
- **T6 — input validation.** `ε∈[0,1]`, `b∈[0,1]`, `k≥1`, plus rung-2a's
  `n≥1, c0≥0, f∈[0,1], generations≥1`.
- **T7 — Strimling breadth anchor (the V-side external check; §5).** In the flat
  reduction (`b=0`, single level → independent traits under innovation-vs-loss),
  the equilibrium repertoire size matches Strimling et al. 2009 — at **Level 3**
  (their reported equilibrium number) if the fetched paper gives one, else at
  **Level 2** (their closed-form equilibrium equation) with the reason documented.
  Also confirms the equilibrium is ~independent of `N` (their result, and the
  breadth-side complement to H2).

These join the permanent (slow-marked where heavy) suite behind the pre-push hook.
**T7's Level tier is finalized once the paper is in hand (§5a).**

---

## 4. Estimand + estimation discipline (WS2 lessons, ported)

- **Per-cell outputs:** steady-state `C*` and per-capita `V*` = mean over the
  post-burn-in window, **with across-seed CIs** — never a single run (WS2
  replication + ill-conditioned-σ lessons).
- **The placebo slope (T4/H2):** `∂V*/∂log N` as the **regression slope** of `V*`
  on `log N`, seed-bootstrap CI — **not** a two-point `V(N_big) − V(N_small)`
  difference (the WS2 ratio/two-point lesson). H2 passes iff that CI does not lie
  entirely below zero.
- **Absolute `C*` and `V*`, reported separately** — never a `C/V` ratio (WS2
  ratio≠control). rung 2b produces the two clean baselines; their *joint* response
  is a later rung.

---

## 5. Level-3 anchor status (scout complete — 2026-07-06)

Per the reproduce-published-numbers standard (Ground Rule 4), each rung wants a
*specific published number*, or a documented reason one is unavailable. The
background scout (Bloom 2020; Park–Leahey–Funk 2023; Wu–Wang–Evans 2019;
Kobayashi–Aoki 2012; Strimling 2009; Mesoudi Model 9 re-verified at source)
settled the picture:

**There is no clean published Level-3 *number* for the exact combined object we
build** — an explicit-innovation-rate operator on a Henrich *depth* (cumulative-
complexity) model, run in simulation with a reported outcome. The Henrich
tradition (incl. Mesoudi Model 9, confirmed at source: innovation lives entirely
in the Gumbel β-tail, no separate operator) *bundles* innovation into
transmission by design. Our split is therefore a genuine contribution, not a
re-run — which is exactly why no drop-in number exists. Given that, we anchor at
**two channels + a re-bundling gate**, aiming for Level 3 where reachable:

- **`C`-side (depth): the un-bundling invariant + qualitative Henrich (rung 1 holds
  the quantitative anchor).** T1 asserts `ε=0` → rung 2a (`C` non-increasing, capped
  at `c0`) + qualitative maintenance/Tasmania on the concept-base substrate. The
  *quantitative* Level-3 Henrich number (`Δz̄ = −α + β(γ_E + ln N)`, Mesoudi eq 9.4,
  `N* = exp(α/β − γ_E) ≈ 616`) is **rung 1's** (`transmission.py`, the Gumbel model),
  already green and unchanged. The concept-base substrate has no Gumbel `α/β`, so it
  does **not** re-derive eq 9.4 — a "re-bundle to Henrich's number" claim for the
  discrete substrate would be a category error. What rung 2b must not do is regress
  the *qualitative* Henrich behavior; the quantitative anchor stays at its rung.
- **`V`-side (breadth): Level 3 *candidate* — Strimling et al. 2009.** *Accumulation
  of independent cultural traits* (Theor. Pop. Biol. 76:77–83) gives a **closed-form
  equilibrium number of traits** set by innovation rate vs loss rate and (under
  broad conditions) **~independent of `N`**. A **flat reduction of rung 2b** — `b=0`
  (lateral only), single level, so elements are independent traits accumulating
  under innovation-vs-loss — should reproduce that equilibrium. This is a real
  external anchor for the innovation/breadth channel *and* an independent proof
  that breadth need not track `N`. **Level 3 is achievable iff the paper reports a
  specific equilibrium number (or a figure data point) to plug into**; if it gives
  only the closed form, we match the *equation* (Level 2) at the reduction and
  document. **→ needs the paper (see §5a).**
- **`V`-side (depth-decline) shape: qualitative, rung 3.** The WWE / Bloom
  per-capita decline is the *shape* rung 2b must be *able* to produce for `V` once
  `κ` is added — it must **not** appear at `κ=0` (that is T4, the placebo). WWE
  itself is empirical, not an ABM, so it is a shape target, not a number.
- **Separability sanity — Kobayashi–Aoki 2012.** Analytic result that the
  innovation rate can contribute *more than proportionally* vs `N` to cumulative
  skill — i.e. splitting `ε` out exposes a lever the aggregate drift hides.
  Optional Level-2 separability check; needs the PDF for the exact inequality.
- **Deferred to Phase 2.4 (empirical V-extension), not rung 2b:** the reproducible
  **Park–Leahey–Funk CD index** (−90% papers / −78% patents, formula + Dataverse,
  same OpenAlex substrate as WS2) — that is the anchor for measuring real-corpus
  `V^struct`, tracked in `docs/primers/v-extension-empirical-spec.tex`.

### 5a. Papers to fetch (the user offered) — to lock the V-side anchor at Level 3

1. **Strimling, Sjöstrand, Enquist & Eriksson 2009**, *Accumulation of independent
   cultural traits*, Theoretical Population Biology **76**(2):77–83 — the
   equilibrium-trait closed form + any reported numeric equilibrium / figure. This
   is what upgrades the breadth-`V` anchor from Level 2 to Level 3.
2. *(optional)* **Kobayashi & Aoki 2012**, Theor. Pop. Biol. **82**:38–47 — the
   exact innovation-rate-vs-`N` inequality, for the separability check.

If Strimling is unavailable, the documented fallback is: `C`-side Level 3 (T1
re-bundling) + the breadth reduction matched at Level 2 (closed-form equation) +
the pre-registered κ=0 placebo (T4) — stated plainly, no overclaim.

---

## 6. Validation gates (rung 2b "done")

1. T1–T7 green; ruff + mypy --strict clean; pre-push hook passes.
2. `C`-side Level-3 anchor intact under `ε=0` + re-bundling to Mesoudi eq 9.4 (T1)
   — no regression.
3. **H2 / T4 met:** per-capita `V*` flat-or-rising in `N` at `κ=0`, by seed-CI
   slope (not two-point).
4. H1′ met: innovation restores `C`-growth above `c0` (T5).
5. `V`-side breadth anchor met (T7) — Strimling 2009 equilibrium matched at
   Level 3 (paper number) or Level 2 (closed form) with the reason documented (§5).
6. rung-2b retro written (hypothesis → what happened → surprises → carry-forward),
   in `docs/phases/`.

## 7. Deliverables

- `src/whitespace3/innovation.py` (or an extension of `concept_base.py`) — the
  innovation operator + `C`/`V` instrumentation, well-mixed, `κ=0`.
- `tests/test_innovation.py` — T1–T6 (permanent suite).
- This plan's retro; parent-plan + CLAUDE.md "current state" updated to rung 2b
  COMPLETE.

## 8. Non-goals (guardrails)

No `κ`, no crossover, no network topology, no `γ`/`H`/`W`, no Modal sweep, no
performance optimization (that is rung 4, gated by an explicit-vs-reduced
equivalence test). One rung, one job.
