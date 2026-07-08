# Whitespace 3: Reconciling Population-Complexity and Small-Team-Disruption

## Project Thesis

Two robust empirical traditions appear to contradict each other:

- **Henrich tradition** (Henrich 2004; Powell–Shennan–Thomas 2009; Derex 2013):
  larger, better-connected populations accumulate and preserve more **cumulative
  complexity** `C`; small isolated groups lose it.
- **Wu–Wang–Evans tradition** (Wu-Wang-Evans 2019; Lin-Frey-Wu 2023): smaller
  teams produce more **per-capita variance / disruption** `V`; large teams
  consolidate.

WS3 shows both are right because they measure **distinct fitness components** of
the same dynamics: `C` (a stock of depth) and `V` (a per-capita flow of persisting
novelty) respond differently — often oppositely — to the same levers. The
contribution is **the first minimal ABM that explicitly decomposes `C` and `V`**
and reproduces both traditions from one model (the deep-research report:
*"No existing ABM explicitly decomposes these. This is the central theoretical
contribution available."*).

**WS3 is simulation-first** (minimal mathematical ABM + phase diagram + *light*
analytics), **not** a hard-theorem paper and **not** WS1's LLM multi-agent model.
The value is conceptual clarity, robust across specifications.

## What WS2 already decided for WS3 (you are ~80% of the way in)

WS2's empirical results are not just background — they **constrain the model** and
have largely chosen the thesis:

- **The conformity mechanism is measured, not assumed.** WS2 documented canonical
  concentration rising endogenously with scale (`H(t)↑`) — so the canon-deviation
  `κ` is empirically privileged, not a stipulation.
- **The channel `κ` acts on is known:** attachment / citation-geometry, **not**
  topic (WS2's structure-vs-topic split). Conformity bites on *how work builds on
  the canon*, not *what it is about*.
- **The reconciliation is orthogonality-leaning, not a strict trade-off.** WS2
  Phase 2.3 found the conformity driver rising does **not** collapse collective
  diversity (independence) — empirical support for the compass's already-preferred
  *non-strict / Pareto* claim.
- **A differential prediction to reproduce:** the effect is strongest where the
  canon concentrates (Physics) — a field-level gradient.
- **A testable open prediction:** Core Claim 6 (`V^struct↓`), measurable by the
  V-extension (Phase 2.4) if/when the empirical loop is closed.

**Why you can't really fail.** Run the ABM and either the `κ`-crossover emerges
(per-capita `V` flips to *decreasing* in `N` while `C` rises → the strong
same-lever-opposite-response reconciliation) **or** it doesn't (→ `C` and `V` are
simply independent axes → still a full reconciliation, matching WS2). Both
dissolve the Henrich↔WWE contradiction. The only way to fail is not reproducing
the two traditions individually — and those are classical.

## Current State

- **Stage:** **Phase 1 (the ABM core) COMPLETE** — rung 5 (synthesis) done; all five
  audited Phase-1 items closed. rung 5 + 4e + 4d + 4c + 4b + 4a + 3 + 2b + Phase 0 COMPLETE.
- **Prelude (this session, on branch `ws3`):**
  - `docs/primers/cv-reconciliation-primer.tex` — unambiguous parameters; the
    surviving hypotheses (refined 13-D + 13-H) in the model's language; **Core
    Claims 1–6** (shape + scaling) constrained by WS2.
  - `docs/primers/v-extension-empirical-spec.tex` — the empirical instrument for
    Core Claim 6 (per-capita structural novelty), reusing WS2 data.
  - `docs/phases/phase-1-abm-core-plan.md` — the ABM Phase plan (5-rung ladder,
    pre-registered hypotheses ↔ Core Claims, Modal sweep design).
- **Phase 0 done (branch `ws3`):** rung 1 (`transmission.py`) reproduces
  **Henrich 2004** at **Level 3** — it matches Mesoudi's canonical
  `DemographyModel` (Model 9) published runs and the Δz̄-vs-N crossover at
  `N*≈616` (α=7, β=1). rung 2a (`concept_base.py`) is *our* per-level concept-base
  representation (un-bundles transmission from innovation; qualitative
  maintenance/Tasmania anchor, **not** a published-number reproduction — novel
  mechanism). Pre-push hook enforces the gates. 14 tests green.
- **Phase 1 rung 2b done (branch `ws3-phase-1-innovation-v`):** `innovation.py`
  adds the innovation operator (primer Def 4.2) on the concept-base substrate
  (κ=0, well-mixed); instruments `C` (reproducible frontier) and per-capita `V`
  (persistence-filtered). H1′ (growth restored above `c0`) + H2 (the κ=0 placebo:
  `V` flat-or-rising in `N`, saturating at `ε`) confirmed; 11 tests (25 total).
  **Key finding:** well-mixing → unbounded redundancy → **no saturation** (`C`
  ratchets ballistically `+1`/gen and `f`-independently; traits go immortal,
  repertoire grows linearly). CC1's saturation + the Strimling breadth anchor are
  **bounded-degree** phenomena → **rung 4**. See `docs/phases/phase-1-rung2b-retro.md`.
- **Phase 1 rung 3 done (branch `ws3-phase-1-conformity-crossover`):** `κ` added to
  the innovation operator (`innovation.run`: `ε·g(κ)`, modes off/scaling/const/
  fraction); `conformity.py` = the crossover toolkit (slope + seed-bootstrap CI,
  `λ*` locator). **THE lemma confirmed:** scaling-`κ` flips per-capita `V*` from
  rising to **falling** in `N` (`λ*≈0.086`), hump-shaped with small-team advantage;
  **reconciliation** (H4′): `C*↑` while `V*↓` under the same lever (`C*` slope +11
  while `V*` slope −0.03 at `λ=0.25`) — and it holds *without* `γ`-sparing (`C` is
  preservation-robust to `κ`). Both negative controls (const-level, VC-fraction)
  give no crossover ⇒ it's **absolute scale-tracking** consensus that bites;
  sign-invariant across `g×s` specs. 15 tests (40 total). Honest ceiling: `s≈ln N`
  is reduced-form → the endogenous-`H` driver is rung 4. See `docs/phases/phase-1-rung3-retro.md`.
- **Phase 1 rung 4a done (branch `ws3-phase-1-endogenous-canon`):** `canon.py` — a
  **multi-prereq attachment-graph** model with `κ=λ·H(t)`, `H=Gini(closure-weight)`.
  Replaces rung 3's reduced-form `s≈ln N` with the real endogenous driver. H1
  (`H` rises with `N`, `0.80→0.96`, WSC 3.1) + H2 (the crossover survives on real
  `H`) + H3 (reconciliation `C*↑/V*↓`) confirmed. **Headline finding:** the
  crossover is **real but WEAK** on `H` (slope `~−0.01`, `λ*≈2`) — the reduced-form
  `ln N` *overstated* it (`−0.03`), because `H` is compressed near 1 — **and
  fidelity-gated**: a sensitivity sweep found it absent at low `f=0.3` (the substrate's
  persistence-rise beats the weak `H`-rise); rung 3's `ln N` was `f`-robust *by
  construction*, masking `H`'s `f`-dependence. Controls: NC0 placebo + NC-const (fixed
  `H`) ✓; spec-robust across `weight ∈ {closure,indegree}`, `ε/b/p`, `g ∈ {exp,hyper}`.
  Correction (verified pre-build): the "in-degree plateaus" contrast was a pure-PA
  artifact — dynamically in-degree `H` rises too. 12 tests (52 total). See
  `docs/phases/phase-1-rung4a-retro.md`.
- **Phase 1 rung 4b done (branch `ws3-phase-1-channel-refinement`):** `channel.py` —
  targeted `κ_eff=λ·H·(1−γ)` (suppress low-canon-alignment `γ` novelty, spare
  content) on the multi-prereq graph, with the `V^struct/V^lat` split + collective
  breadth `W`. **Reproduces WS2's two-channel fingerprint:** `W↑` with `V^struct↓`
  (WSC:channel + WSC:indep orthogonality — breadth doesn't collapse). Honest
  decomposition: `V^struct`'s *decline* is partly endogenous (present at κ=0, from
  canon concentration); `κ` crushes its *level* (~0.22→0.02); **targeting** uniquely
  spares breadth (`W` +116 vs uniform's +25). **Resolves rung 4a's "weak crossover":**
  it was *total*-`V` diluting a clean structural decline with rising breadth — the
  proper WWE measure is `V^struct`. Two boundaries (baked-in sweep): needs `f≥0.5`
  (fidelity) **and** `α≤0.15` (a tight canon). 10 tests (65 total). See
  `docs/phases/phase-1-rung4b-retro.md`.
- **Phase 1 rung 4c done (branch `ws3-phase-1-network-topology`):** `roles.py` —
  bounded-role-model accumulation of independent traits (each agent learns from `n`
  randomly-sampled models, sub-critical `f·n<1`). **Program's 2nd Level-3 result:**
  reproduces Strimling 2009 `λ_f=U/(1−β)` incl. the number **0.2** (ε=0.1,f=0.5,n=1),
  `N`-independent; and Enquist 2010's threshold `p·n>1` (= `f·n=1`). Anchored via the
  OPEN Lehmann–Aoki–Feldman 2011 (states+attributes Strimling's eq) + Enquist 2010
  (open primary) — Strimling's own PDF is inaccessible (Henrich→Mesoudi pattern,
  documented). **Unifying principle:** saturation is a *sub-criticality* phenomenon
  (`f·n<1`), the mirror of rung 2b's runaway — resolves "well-mixing → no saturation"
  (it was super-critical transmission, not redundancy). Scope morphed from the naive
  "spatial network topology" (disconfirmed: traits percolate → no `N`-independence).
  9 tests (74 total). See `docs/phases/phase-1-rung4c-retro.md`.
- **Phase 1 rung 4d done (branch `ws3-phase-1-subfield-channel`):** `subfield.py` — the
  **content/`τ` channel**, built because WS2 Phase 2.4 **disconfirmed** Core Claim 6
  (`cc:open`): per-capita `V^struct` does not decline — it **rises**, cross-subfield.
  Niches recombine a **shared, growing, high-degree canon** (`K = N/m`, F5 forced);
  measured the faithful way (one null, atypicality-vs-birth-time): **global structural
  novelty rises** (`−0.023`, CI excludes 0), **within-niche flat** (`+0.001`), **coexists
  with `H_global↑`** (`0.94`) — concentrates at the top, fragments in the middle.
  Fragmentation-driven (K-fixed placebo flat); a **tunable crossover** in niche
  distinctiveness `bw` (`bw*≈0.05`). **The reconciliation is orthogonality:** `τ`
  (content, `V^struct↑`) ⊥ `κ` (attachment, `H↑`) — resolves rung 4b's substrate-sign
  problem. Honest path (4 seeded prototypes): disjoint blocks disconfirmed → shared-canon
  recombination → bounded-`m` single-lever (`bw=m/E`) disconfirmed pre-build → corrected to
  `K=N/m` + separate off-trend `bw`. Scope: **sign-structure + crossover, not the
  scale-confounded Uzzi-z magnitude**; `H2a` Strimling floor retired (within-flat now
  lens-persistence). 9 tests (6 fast + 3 slow; 69 fast total). See
  `docs/phases/phase-1-rung4d-retro.md`. **Primer updated** (merged): `cc:open`/CC6 marked
  disconfirmed + the content channel added as the orthogonal driver.
- **Phase 1 rung 4e done (branch `ws3-phase-1-topology-robustness`):** `channel.run` gains
  an optional interaction **topology** (`well_mixed` default = **byte-identical**; `er`/`ws`/
  `ba` = fixed finite-degree graph via `networkx`, neighbour-carriers through a `scipy.sparse`
  adjacency with self-loops). The κ-signature (`V^struct↓`, `W` spared) is **topology-
  invariant** across well-mixed/ER/WS/BA, and κ **steepens** the `V^struct`-vs-`logN` decline
  on every topology (H3). **Closes `cc:robust`** (κ-specs from rungs 3/4a/4b × topologies).
  Sign-structure invariant, magnitude varies with degree; nothing killed it (even BA hubs).
  7 tests (6 fast + 1 slow; 75 fast total). See `docs/phases/phase-1-rung4e-retro.md`.
- **Phase 1 rung 5 done — the synthesis capstone (branches `ws3-phase-1-rung5-synthesis`
  (5a, merged) + `ws3-phase-1-rung5b-closeout` (5b)).** Closed all five audited items:
  (1) **light analytics** (`analytics.py`) — the crossover law `λ*=d ln P/d ln N`, Henrich
  carrier-survival, GW anchor `μ=2→0.7968`; (2) **phase diagram** (`experiments/phase-1-rung5/`)
  — `λ*≈0.09` (matches rung 3), V- vs C-favouring regions + the figure; (3) **Pareto** —
  selective isolation `ι` (`channel.run`: shielded subgroup `V^struct` high, global `C`
  pinned) + two-channel orthogonality; (4) **robustness-grid** — memory-with-decay `r` in
  `roles.py`, the **3rd Level-3 anchor** `λ_f=ε/(1−f·n−r)=1.0`; (5) **at-scale** — a detached
  Modal sweep (300 cells, N→1500) shows the crossover holds (`λ*` unchanged) — *not* a
  small-N artifact. Honest: at-scale is the focused `(λ,N)` slice, not the full N=3000 grid
  (`channel.run` is O(N²) — infeasible; logged). See `docs/phases/phase-1-rung5-retro.md`.
- **Phase 2 (empirical bridge / Lever 1) — A, B/B′, C COMPLETE (branch
  `ws3-phase-2-empirical-bridge`).** Calibrated prediction + the Park reconciliation, on the WS2
  data. **A** (`bridge_A.py`): PASS — the fragmentation signature (global atyp-rise ⊥ within-flat)
  reproduces at the right magnitude (15.6×≈13×). **B/B′** (`bridge_B/Bprime.py`): PARTIAL — the
  sign-structure + microstructure are forced & confirmed (apples-to-apples on the `d_min` subset);
  the ~13× *magnitude* is `bw`-tunable ⇒ consistency, not a tight prediction. **C — the
  disruption reconciliation (`phase-2-experiment-C-retro.md`): the two-channel decoupling is
  CONFIRMED on the full 24M-paper citation graph, and our mid-course *adjudication* hypothesis was
  run to a decisive test and DISCONFIRMED.** C-1/C-1b (model): the PA substrate makes CD *rise*
  under κ (mis-signs the CD-index — a documented limitation; the model reconciles via `H`↑, not
  CD↓), and length-inflation *can* flip toy-CD down ⇒ the (later-rejected) length-artifact
  hypothesis. C-2-full (`cd_data_C2_full.py`, all server-side on Modal `ws2-section0`, 24M pop,
  46.7% dense, 149.6M edges, `cd_index_csr`): **C-2a-full ✓** Park's decline replicates cleanly
  (`−0.00086`, tight CI, `0.050→0.013`, all eras); **C-2b-full ✗** it is NOT a reference-length
  artifact (mediation attenuates only 24% <50% gate; random cap *steepens* it). ⇒ the empirical
  **decoupling is real on both channels** — CD↓ + `H`↑ (consolidation) ⊥ atyp↑ (fragmentation) —
  and the C/V model reconciles it via `H` + atyp; Park's CD-decline is independent confirmation.
  We **confirm Park additively**; the model's CD-sign is a documented PA limitation. `cd_index`
  vendored WS3→WS2 (pin `282e09f`). **D deferred** (A–C mixed ⇒ the paper is the confirmed
  decoupling + reconciliation, not a cross-field OOS capstone).
- **Next:** **the paper.** Both empirical bridges land (fragmentation signature reproduced; the
  decoupling confirmed at 24M). The arc is whole: two driving claims (WS2 Claim #13, WS3 CC6)
  honestly disconfirmed into a sharper positive thesis (concentration + fragmentation, orthogonal),
  three Level-3 anchors, the phase diagram + crossover law, and now a full-scale empirical
  decoupling. The writeup (`docs/conceptual.md` → paper) is the capstone. Deferred: full N=3000
  sweep *if* `channel.run` is vectorised; depth-`C` saturation under sub-criticality; C's
  coverage-artifact prong (out of scope); F2 escape-hatch.

## The WS3 arc (four phases)

- **Phase 0 — substrate on-ramp.** Read the ~6 core papers; build + validate the
  **transmission harness** that reproduces the **Henrich 2004** critical-population-
  size result at Level 3 (via Mesoudi's Model 9) (`src/whitespace3/transmission.py`).
  This is rung 1 of the ABM plan
  and the C-substrate. Deliverable: a validated engine + you can think in the
  substrate. *Your gap is domain knowledge, not method — your portfolio is
  rigorous computational experimentation; this is a ~2-week onboarding.*
- **Phase 1 — the ABM core** (`docs/phases/phase-1-abm-core-plan.md`, rungs 2–5):
  add innovation → per-capita `V`; add `κ` → find the crossover `λ*` (the
  load-bearing lemma); robustness + the reconciliation + phase diagram.
- **Phase 2 — robustness + the WS2 bridge:** ≥3 `κ` specs × ≥3 topologies; the
  two-channel (content/attachment) Tier-2 refinement matching WS2; *optionally*
  the Phase-2.4 empirical probe.
- **Phase 3 — writeup:** the reconciliation, faithful to both literatures, plus
  an explicit "diversity collapse in AI systems" discussion (the frontier framing).

## The two-tier model (resolves theorem-vs-empirical-fit)

- **Tier 1 — minimal generic model** (`κ` suppresses innovation generically):
  carries the reconciliation theorem + the crossover. Clean, camp-agnostic.
- **Tier 2 — two-channel refinement** (content vs attachment; `κ` on attachment):
  the WS2-consistency layer reproducing `W↑` with `V^struct↓` and the Physics
  gradient. Prove in Tier 1; match the empirics in Tier 2.

## Build & Test

```bash
cd whitespace_3
uv sync --extra dev
make test          # pytest (fast); make test-all includes slow sweeps
make lint          # ruff check
make typecheck     # mypy strict
```

Whitespace independence: WS3 has its **own** lockfile / venv; no ambient sharing
with WS2 (shared utilities graduate to a versioned package with tests).

## Ground Rules (inherited from the program + WS2's hard-won discipline)

1. **Plan mode** for any non-trivial task; **TDD** (tests/hypotheses first).
2. **Pre-register** hypotheses + evaluation criteria before running.
3. **Report nulls honestly** — the orthogonality outcome is a full result.
4. **Trust = independent agreement + placebo,** not "my sim runs": every rung has
   a known-answer anchor (reproduce a published baseline) + a placebo (e.g.
   `κ=0` must not produce the crossover). **Aim for Level 3** — reproduce a
   specific published *number* of the same model (not just our own coded formula,
   and not merely a matching equation). Where the source is analytical-only or the
   rung is our own construction, document the reason Level 3 is unavailable and use
   the strongest anchor. Never name a published model we haven't implemented. See
   `tasks/lessons.md` (2026-07-03) + the `feedback_reproduce_published_numbers` memory.
5. **Robustness across specifications** is the analog of WS2's ≥2-embedding-
   families rule: ≥3 `κ` specs × ≥3 topologies; the *sign-structure* must be
   invariant.
6. **Replication + CIs, not point estimates**; the crossover sign is a regression
   slope with seed-bootstrap CIs — never a two-point difference (the WS2
   ill-conditioned-σ lesson).
7. **Absolute `C` and `V` separately, never a `C/V` ratio** (the ratio≠control
   lesson).
8. **Verify extreme claims** before believing them.
9. Small, focused commits; **no Co-Authored-By**; phase branches off `main`, user
   merges. Track spend in `tasks/spend.md`.

## Key References

- North star: `docs/conceptual.md` (the WS3 compass).
- **Formal spine:** `docs/primers/cv-reconciliation-primer.tex` (parameters,
  `C`/`V`, Core Claims).
- Empirical bridge: `docs/primers/v-extension-empirical-spec.tex`.
- ABM plan: `docs/phases/phase-1-abm-core-plan.md`.
- Core readings (to build the model — the fuller 30–40 is for the paper's lit
  review): **Henrich 2004** (Tasmania / critical population size — the
  single-population model reproduced at rungs 1–3), via **Mesoudi, *Simulation
  Models of Cultural Evolution in R*, Model 9** (`DemographyModel` — the
  reproducible Level-3 source: concrete parameters + runs, e.g. `N*≈616` at
  α=7,β=1); **Powell–Shennan–Thomas 2009** (the *metapopulation* N→complexity
  ABM — the Level-3 target for the later network rung, NOT rungs 1–3);
  **Vaesen et al. 2016** (the robustness critique), **Derex et al. 2013**,
  **Wu–Wang–Evans 2019**, **Zollman 2007/2010** (network-epistemology ABM template).
- Program context: `../docs/program/` (overview, deep-research pathways).

## Known Gotchas

- **The crossover is the only hard part.** Transmission→`C` (Henrich) is classical;
  the joint `C`–`V` response is emergent. Spend your attention on how `κ` must
  scale for per-capita `V` to flip sign in `N`.
- **Don't over-fit to WS2.** Keep the reconciliation in the minimal Tier-1 model;
  add the attachment-channel refinement only as the Tier-2 empirical layer.
- **Keep analytics light.** Mean-field / steady-state approximations, guided by
  the simulation — not airtight theorems (the compass says so).
- **Scope discipline:** this is an abstract mathematical ABM (CPU, laptop-scale).
  Do NOT drift toward WS1's realistic-agent model.
