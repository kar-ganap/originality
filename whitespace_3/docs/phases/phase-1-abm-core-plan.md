# WS3 Phase 1 — The Minimal ABM: Computational Reconciliation of C and V

**Whitespace:** 3 (theoretical reconciliation) — **this is WS3's core, simulation-first.**
**Status:** PLAN. Supersedes the "WS2.5" idea: rather than a separate whitespace,
the intuition-building simulation *is* WS3's central method and central
contribution, front-loaded.
**Cost:** ~\$0 local + **< \$50** of the \$250 Modal budget (see §8); budget is
not the binding constraint.

---

## 0. One-line scope + the contribution

Build the **minimal mathematical agent-based model** (concept-base agents;
transmission fidelity `f`; innovation rate `ε` under conformity pressure `κ`;
network density `ρ`; isolation `ι`) that instruments the two output gauges
`C(t)` (cumulative complexity) and `V(t)` (per-capita variance generation), and
show that **both the Henrich result (`C` rises with scale) and the Wu–Wang–Evans
result (per-capita `V` falls with scale) emerge from one dynamics, with a
tunable crossover, robust across conformity specifications.**

> **Why it is the contribution, not scaffolding.** The program's own
> deep-research report: *"No existing ABM explicitly decomposes these [C and V].
> This is the central theoretical contribution available."* A clean minimal ABM
> that (i) reproduces Henrich, (ii) reproduces WWE, (iii) exhibits the crossover
> + phase diagram, robust across `κ` specs, **is** the publishable result. The
> analytical layer (§ rung 5) is light and *simulation-guided*, consistent with
> the WS3 compass ("value is conceptual clarity, not model realism").

**This is categorically not WS1.** WS1 is an *LLM* multi-agent model (expensive,
realistic agents). This is an *abstract mathematical* ABM in the
Powell–Shennan–Thomas 2009 / Zollman lineage — CPU-bound, laptop-scale.

**Full formal definitions are pinned in** `docs/primers/cv-reconciliation-primer.tex`
(parameters §3, dynamics §4, outputs §5). This plan references those objects by
name and does not re-derive them.

---

## 1. Pre-registered hypotheses (mapped to the primer's Core Claims)

| # | Hypothesis | Shape / scaling to establish | Primer link |
|---|---|---|---|
| **H1** | *Henrich / `C`.* Steady-state `C*` is non-decreasing in `N, ρ, f`; small/insulated/low-fidelity populations lose `C` stochastically. | increasing + **saturating**; **threshold** collapse below a critical redundancy `m*` | CC1 |
| **H2** | *`κ=0` baseline.* With conformity off, per-capita `V*` is flat or **increasing** in `N`. | monotone/flat in `N`; the WWE-contradicting baseline that *motivates* `κ` | CC2 |
| **H3** | **The crossover (the load-bearing lemma).** With `κ` scaling up in visible consensus / `N`, per-capita `V*` becomes **decreasing** in `N` beyond `N*`; there is a critical conformity-scaling `λ*` at which `∂V*/∂N` flips sign. | per-capita `V` **hump-then-falling** in `N`; a sign-flip locus `λ*(N,ρ)` | CC2 |
| **H4** | *Reconciliation.* One lever moves the gauges **oppositely** (`∂C*/∂ρ > 0`, `∂V*/∂ρ < 0`); **and** selective isolation (raise `ι` for an innovation subgroup, hold global `N,ρ`) moves **both up** (Pareto). Trade-off frequent, **not strict**. | opposite-sign columns **and** a same-sign (Pareto) column in the `(C,V)` Jacobian; a **phase diagram** | CC3 |
| **H5** | *Robustness / shape-invariance.* H1–H4 hold across **≥3 `κ` specs** (visible-consensus, attention-competition, canon-deviation) and **≥3 topologies** (ER, Watts–Strogatz, Barabási–Albert). | the **sign-structure** is invariant to functional form | CC4 |
| **H6** | *WS2-consistency bridge (secondary).* The canon-deviation `κ` reproduces **endogenous, scale-driven, saturating** canon concentration `H(t)` (matching WS2), and `κ` acting on the attachment channel yields breadth `W↑` with structural novelty `V^struct↓`. | `H` increasing/concave in scale; `W↑` with `V^struct↓` | CC5/CC6 |

**Negative controls (pre-registered).** (i) `κ=0` must **not** produce the H3
crossover. (ii) A large, dense, high-fidelity population must **not** lose `C`
(no spurious Tasmania). (iii) A random-`κ` (consensus-blind) suppressor must not
reproduce the WWE decline — it must be the *consensus scaling* that bites.

**Honest-null clause.** If the crossover (H3) is **not** robust across ≥2 `κ`
specs, that is a real, reportable result: it would mean the `C`–`V` opposition is
mechanism-specific, and the reconciliation is **orthogonality-only** (the two
gauges are independent, no genuine trade-off) — which the WS3 compass explicitly
pre-authorizes as valuable, and which is *consistent with WS2's Phase-2.3
independence finding.* Either outcome advances the paper.

---

## 2. TEST (TDD — written and green before the sweep)

Trust in a simulation pipeline comes from **independent agreement** (reproduce a
known result) + **placebo calibration** (no-signal input → no-signal output) — the
WS2 "how do we draw trust" lesson, ported to simulation.

- **T1 — known-answer anchor.** The transmission-only harness reproduces
  Powell–Shennan–Thomas 2009's `N`→complexity loss threshold within tolerance
  (be aware of the Vaesen 2016 robustness caveat; test the *canonical* regime).
- **T2 — metric correctness.** `C(t)`, `V(t)`, canon-concentration `H`, and the
  `V^struct/V^lat` split computed correctly on hand-built states.
- **T3 — determinism.** Same seed ⇒ byte-identical trajectory (required for the
  resumable sweep and for reproducibility).
- **T4 — `κ=0` placebo (H2).** Per-capita `V` is **not** decreasing in `N` when
  `κ=0` (the crossover must not appear without conformity).
- **T5 — pre-validated crossover.** On a small, hand-checked case, a known
  `κ`-scaling produces the H3 sign-flip (guards the load-bearing lemma against a
  metric/estimation bug).

These become the permanent (slow-marked) test suite.

---

## 3. IMPLEMENT — the 5-rung ladder (each rung a gated milestone)

Build bottom-up; each rung is independently checkable and the classical rungs
have known answers.

1. **Transmission → `C`.** Concept-base agents + redundancy-based acquisition
   (primer Def. 4.1). **Gate:** T1 (reproduce Powell 2009). *This rung is the
   substrate-fluency on-ramp — a known-answer target.*
2. **Innovation, `κ=0` → per-capita `V`.** Add the innovation operator (primer
   Def. 4.2) and the persistence-filtered `V` (primer Def. 5.2). **Gate:** T4
   (per-capita `V` flat/rising in `N`).
3. **Add `κ` → find the crossover `λ*` (THE lemma).** Visible-consensus `κ`
   first (simplest). Sweep the conformity-scaling coefficient `λ` and locate the
   `∂V*/∂N` sign-flip. **Gate:** T5 + a clean crossover on the primary grid.
4. **Robustness + reconciliation.** All 3 `κ` specs × 3 topologies + the
   isolation/subgroup machinery. **Gate:** H4 (opposite-sign lever + Pareto
   selective-isolation) and H5 (sign-structure invariant).
5. **Light analytics.** Mean-field steady states — `C*(N,f,ρ)` via
   carrier-survival / branching, per-capita `V*(N,κ)` via innovation net of
   `κ`-suppression — and the **crossover condition on `λ`**. Guided by the
   simulation, not attempted cold. **Gate:** analytic crossover matches the
   simulated `λ*` qualitatively.

---

## 4. Estimands, estimator, and estimation discipline

- **Per-cell outputs:** steady-state `C*` and per-capita `V*` (mean over the
  post-burn-in window), plus `H*` and `W*` for the H6 bridge, **with
  across-seed confidence intervals** — never a single-run value (the WS2
  "replication, not point estimates" + ill-conditioned-σ lessons).
- **The crossover (H3):** estimate `∂V*/∂N` as the **regression slope of `V*` on
  `log N`** at fixed `(ρ,f,κ,λ,topology)`, with seed-bootstrap CIs; `λ*` is where
  that slope's CI crosses zero. Do **not** infer the sign from a two-point
  difference.
- **The reconciliation (H4):** report **absolute** `C*` and `V*` responses to
  each lever **separately** — never a `C/V` ratio (the WS2 ratio≠control lesson).
  The reconciliation lives in the *joint sign pattern*, not a composite.
- **The phase diagram:** over `(N, ρ)` (and over `(λ, N)`), map the `C`-optimal
  vs `V`-optimal regions and the crossover locus.

---

## 5. Robustness grid (the ≥2-families discipline, ported)

| Axis | Settings |
|---|---|
| `κ` mechanism | visible-consensus / attention-competition / canon-deviation |
| suppression map `g(κ)` | `e^{-κ}` / `1/(1+κ)` |
| topology | Erdős–Rényi / Watts–Strogatz / Barabási–Albert |
| retention | generational-replacement / memory-with-decay |
| innovation split `b` | 0.1 / 0.3 (lateral-heavy / more vertical) |
| persistence filter `k` | 1 / 3 |

The headline (H3 crossover, H4 reconciliation) must hold across the **`κ`-mechanism
and topology** axes at minimum. A result that appears under only one `κ` spec is
mechanism-specific and reported as such (the WS2 "one-family signal reversed under
swap" caution, in simulation form).

---

## 6. The Modal sweep (VERIFY at scale)

**Smoke-before-bulk:** validate the harness (T1–T5) and a coarse grid locally,
then run the full sweep on Modal.

**Primary grid (illustrative, log-spaced where natural):**
`N ∈ {10,30,100,300,1000,3000}` × `ρ ∈ {2,4,8,16}` × `f ∈ {0.5,0.7,0.9,0.99}` ×
`κ-mech ∈ {VC,AC,CD}` × `λ ∈ {0,0.5,1,2,4,8}` × `topology ∈ {ER,WS,BA}`, with
**R = 30 seeds/cell**, `T ≈ 300` generations (+ burn-in discard). Targeted finer
1-D `λ`-sweeps around each crossover.

**Execution:** embarrassingly parallel over `(cell × seed)` via Modal `.map`
(CPU containers); each worker returns only the scalar steady-state summaries
(not trajectories) so the client never streams large payloads — the **server-side-
summary lesson from the Phase-2.3 SPECTER2 embed.** Resumable per-cell
persistence + `return_exceptions=True` (the Phase-2.1/2.3 resume lessons) so a
flaky run costs one cell, not the sweep.

**Cost:** the primary grid is ≈ 5k cells × 30 seeds ≈ 1.5×10⁵ runs; at a few
CPU-seconds each this is a few hundred core-hours — **well under \$50** on Modal
CPU. The remaining budget is headroom for iteration and finer sweeps. *No GPU.*
Any coverage/sampling caps are `log`ged, never silently applied.

---

## 7. Validation gates + escape triggers

**Gates (pre-registered "done"):**
1. T1–T5 green; Powell 2009 reproduced (independent-agreement anchor).
2. H3 crossover robust across **≥2 `κ` specs and ≥2 topologies**, estimated with
   seed-CIs.
3. H4 demonstrated: opposite-sign lever **and** a Pareto selective-isolation
   intervention; phase diagram produced.
4. H5 sign-structure invariant across the robustness grid.
5. H1/H2 reproduced (the two traditions individually).
6. (If reached) rung-5 mean-field crossover matches the simulated `λ*`
   qualitatively.

**Escape triggers (diagnose before redirecting — the WS2 "diagnose, don't
mechanically escalate" lesson):**
- *Powell not reproduced* → harness bug; fix before any downstream claim.
- *Crossover only under one `κ` spec* → report as mechanism-specific; pivot the
  paper's thesis toward **orthogonality** (independent gauges, no strict
  trade-off), which is still a full contribution and matches WS2's independence
  result.
- *No crossover under any `κ` scaling* → the minimal model is too weak; the
  `κ`-on-attachment channel or a competition-for-attention term is missing;
  document and extend before claiming the reconciliation.

---

## 8. Deliverables → WS3 paper

- `src/` ABM + the permanent test suite (T1–T5).
- The **phase diagram**, the **crossover law** (`λ*` locus), the robustness grid,
  and steady-state `C*/V*` surfaces with CIs.
- A results writeup that **becomes WS3 Sections 4–5** ("The model" + "Robustness"
  in the compass's outline). If rung-3 yields a clean standalone statement (a
  "conformity-scaling law for the C–V crossover"), it can be a short companion
  note — but default to **one strong WS3**, not salami-slicing.
- (Optional bridge) the H6 run linking to WS2's measured `H(t)` and the
  V-extension spec (`docs/primers/v-extension-empirical-spec.tex`).

## 9. Cost, reproducibility, timeline

~\$0 local + `<\$50` Modal (§6). All seeds/parameters pinned; runs deterministic
(T3). Maps onto the WS3 compass timeline (weeks 5–10: formal setup → basic
results → robustness). A few focused weeks, in your demonstrated
rigorous-computational mode.

## 10. Companion documents

- `docs/primers/cv-reconciliation-primer.tex` — parameters, `C`/`V`, Core Claims (the formal spine).
- `docs/primers/v-extension-empirical-spec.tex` — the empirical bridge (Core Claim 6).
- `docs/conceptual.md` — the WS3 compass (model, robustness, venue).
