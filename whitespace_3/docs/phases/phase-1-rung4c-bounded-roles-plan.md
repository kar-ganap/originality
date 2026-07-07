# WS3 Phase 1 · rung 4c — Bounded role models: sub-criticality & the Strimling anchor

**Whitespace:** 3 · **Phase:** 1 (the ABM core), rung 4c.
**Branch:** `ws3-phase-1-network-topology` (kept; scope morphed — see §0).
**Status:** PLAN (plan-first; pre-registration locked before code).
**Formal spine / anchors:** Strimling et al. 2009 (λ_f = U/(1−β)); Lehmann–Aoki–Feldman
2011 (open re-derivation, eq 3.4/3.5 + Fig 1); Enquist et al. 2010 (the `p·n>1`
threshold, eq 7 / Prop 1).

---

## 0. Scope — bounded-role-model transmission (the honest morph)

**Origin.** rung 4c began as "network topology → `C` saturation + the Strimling
anchor." Plan-first verification (this session) disconfirmed the naive version — on a
*spatial* network traits **percolate** and persist, so there is no `N`-independent
equilibrium — and instead uncovered the *real* mechanism: **learning from `n`
randomly-sampled role models** (frequency-dependent, so rare traits die) in the
**sub-critical regime `f·n < 1`** (so per-agent culture is bounded, not runaway).

**Scope.** Build the minimal **bounded-role-model** model (flat, independent traits;
each agent learns each generation from `n` fresh random models at fidelity `f`;
innovation rate `ε`; no prerequisite structure). Establish, at **Level 3**:
1. **Strimling's per-individual equilibrium** `λ_f = ε/(1−f·n)` (= `U/(1−β)` at `n=1`),
   incl. the *specific number* `0.2` at `ε=0.1, f=0.5, n=1`, and its **`N`-independence**.
2. **Enquist's threshold** `f·n = 1` (their `p·n>1`): sub-critical ⇒ finite
   `N`-independent equilibrium; super-critical ⇒ runaway growth in `N`.
3. The **unifying principle** it exposes: *bounded/saturating culture is a
   sub-criticality phenomenon* — the exact mirror of rung 2b's runaway (`f·n ≥ 1` ⇒
   immortal traits, ballistic `C`). This is the honest resolution of "well-mixing → no
   saturation": it was never redundancy, it was **super-critical transmission**.

**Explicitly out of scope** (this is the breadth/saturation substrate, not the
conformity axis): no `κ`/crossover (rungs 3–4b), no prerequisite depth `C`, no spatial
network (the bounding structure is *role-model sampling*, not topology). A separate
later rung may test the crossover under bounded transmission.

---

## 1. Pre-registered hypotheses

Prototype numbers from `scratchpad/verify_strimling.py` (2026-07-07).

| # | Hypothesis | Criterion | Prototype |
|---|---|---|---|
| **H1** | **Strimling Level-3 number.** `λ_f = ε/(1−f·n)`; at `n=1` this is `U/(1−β)` — match `0.2` at `ε=0.1,f=0.5`. | `λ_f` within tol of `0.2`; and of `ε/(1−f)` at other `(ε,f)` | `0.20/0.17/0.21` across `N` |
| **H2** | **`N`-independence.** `λ_f` (per-individual) is independent of `N` (sub-critical). | `λ_f` ratio across `N∈[50,400]` ≈ 1 (`<1.5`) | ratios `1.0–1.1` |
| **H3** | **Closed form (my `n`-synthesis).** `λ_f = ε/(1−f·n)` across `(ε,f,n)` sub-critical. | `λ_f` matches `ε/(1−f·n)` within tol | verified vs `ε`-scaling + `f·n` |
| **H4** | **Enquist threshold `f·n=1`.** Sub-critical (`f·n<1`) ⇒ finite, `N`-independent; super-critical (`f·n>1`) ⇒ runaway, grows with `N`. | `λ_f` bounded & flat for `f·n<1`; grows with `N` for `f·n>1` | `fn=0.9`→~1 flat; `fn=1.1`→`13→56` |
| **H5** | **Population linear growth.** The population repertoire `λ_p` grows ~linearly in `N` (individual saturates, population doesn't). | `λ_p` slope on `N` `>0`, ~linear | `λ_p ∝ N` |

**Honest-null clause.** If the sim does **not** hit `λ_f = ε/(1−f·n)` (e.g. self-
sampling acts as memory and inflates it, or finite-time bias near `f·n→1`), report the
discrepancy and its cause; the Level-3 claim stands only on the *verified* number.

---

## 2. Anchor status (reproduce-published-numbers standard) — Level 3

- **`λ_f = U/(1−β)` — Strimling 2009, via LAF 2011 (Level 3).** Strimling's own PDF is
  genuinely inaccessible (checked — no OA copy), but the equilibrium is stated and
  *explicitly attributed* to Strimling in the **open, peer-reviewed** Lehmann–Aoki–
  Feldman 2011 (eq 3.4; "equation (2) of Strimling et al." at `r=0`). This is the
  **Henrich→Mesoudi pattern** (primary has no accessible number; a reproducible source
  supplies it). The number `λ_f=0.2` at `U=0.1,β=0.5` (LAF Fig 1) is our match.
- **`f·n=1` threshold — Enquist et al. 2010 (Level 3, primary open).** `p·n>1` (eq 7 /
  Prop 1), read from the open primary PDF; our sub/super-critical transition reproduces it.
- **`ε/(1−f·n)` (the `n`-generalized count form) — our synthesis (documented).** No
  single paper writes it with explicit `n`; the count form is Strimling (`n=1`), the
  `n`-threshold is Enquist. We label it *our* synthesis, Level-2 (derived + verified),
  and anchor Level 3 at `n=1` (Strimling number) and at the threshold (Enquist).

---

## 3. Representation / module

New module **`src/whitespace3/roles.py`** — minimal, flat (independent traits), no
prereqs:
- Agent bases `B: bool[N, E]` (trait holdings), start with `c0` common traits.
- Each generation: sample `n` role models per agent **excluding self** (so `r=0`, no
  memory — Strimling's headline case); `m_i(e)=` #models holding `e`; acquire with
  `1−(1−f)^{m}`; generational replacement. Then innovation at rate `ε` (fresh trait).
- Outputs: `per_agent` (mean `|B_i|` = `λ_f`) and `repertoire` (`|R|` = `λ_p`) trajectories.
- Measurement: steady-state `λ_f`, `λ_p` (post-burn-in mean, seed-CIs); the critical
  `f·n=1`.

## 4. TEST (TDD — green before any claim)

- **T1 — determinism.**
- **T2 — Strimling Level-3 number (H1).** `λ_f ≈ 0.2` at `ε=0.1,f=0.5,n=1` (within
  tol), `N`-independent across `N∈{50,150,400}`; and `λ_f ≈ ε/(1−f)` at 2–3 other `(ε,f)`.
- **T3 — closed form (H3).** `λ_f ≈ ε/(1−f·n)` across `n∈{1,2,3}` and `(ε,f)` (sub-crit).
- **T4 — `N`-independence (H2).** `λ_f` ratio across `N` `< 1.5` (sub-critical).
- **T5 — Enquist threshold (H4).** sub-critical `f·n<1` ⇒ `λ_f` bounded & `N`-flat;
  super-critical `f·n>1` ⇒ `λ_p`/`λ_f` grows with `N` (runaway). The `f·n=1` boundary.
- **T6 — population linear growth (H5).** `λ_p` slope on `N` `>0`.
- **T7 — input validation** (`n≥1`, `f,ε∈[0,1]`, …).
- **T8 — sensitivity (slow, baked in per the standing commitment).** the closed form +
  `N`-independence hold across `ε, f, n` in the sub-critical regime.

## 5. Validation gates (rung 4c "done")

1. T1–T8 green; ruff + mypy strict clean; pre-push hook passes.
2. **H1/T2: Level-3 number `0.2` matched, `N`-independent.**
3. H3 closed form; H4 Enquist threshold; H5 population growth.
4. Anchor status documented (§2) — Level 3 via LAF 2011 + Enquist 2010; the honest
   Strimling-PDF-inaccessible note (Henrich→Mesoudi pattern).
5. rung-4c retro written — incl. the sub-criticality unifying principle (rung-2b
   resolution).

## 6. Non-goals

No `κ`/crossover, no prerequisite depth, no spatial network, no memory (`r=0` headline;
memory `U/(1−β−r)` is a possible documented extension, not built here), no Modal sweep.
One rung, one job: **reproduce Strimling/Enquist at Level 3 and name the sub-criticality
principle.**
