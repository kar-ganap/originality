# WS3 Phase 1 · rung 4d — The subfield channel: fragmentation as the mechanism

**Whitespace:** 3 · **Phase:** 1 (the ABM core), rung 4d.
**Branch:** `ws3-phase-1-subfield-channel`.
**Status:** PLAN (plan-first; pre-registration locked before code).
**Formal spine / anchors:** the within-niche floor inherits rung 4c's Strimling
`λ_f = ε/(1−f·m)` (Level 3, via Lehmann–Aoki–Feldman 2011 + Enquist 2010); the local
canon inherits rung 4a's endogenous `H = Gini(closure)`; the empirical fingerprint is
WS2 **Phase 2.4** (`whitespace_2/docs/phases/phase-2.4-retro.md`: within-subfield
atypicality flat, global falls `9–13×` more). Genericity anchor: division-of-labour
scales with population (Durkheim; Carneiro) / limiting similarity (MacArthur–Levins).

---

## 0. Scope — the reframe, and the one object it turns on

**Why this rung exists.** The primer's Core Claim 6 (`cc:open`) predicted per-capita
structural novelty **declines**, graded by canonical concentration `H` — the
`κ`-trade-off reading. WS2 Phase 2.4 **disconfirmed it, opposite sign**: `V^struct`
**rises** (off-canon `+0.006`, atypicality median-z `−0.74`, both p=0.0005), and the
follow-on diagnostic localised *why* — the rise is **cross-subfield**: recomputed
*within* a subfield, combination-novelty is flat (`−0.05`/`−0.07`); only against the
*whole field* does it rise (`−0.64`/`−0.66`). The field **concentrates at the top and
fragments in the middle at once.**

So rung 4d does **not** re-establish CC6 (falsified). Its job is to reproduce the
**actual** measured signature from one added structure, and to do so under a discipline
strict enough that the structure *could not* have reproduced the opposite signature.
This also resolves the **substrate-sign problem** rung 4b exposed: global preferential
attachment makes the *model's* `V^struct` **fall** (concentration suppresses structural
novelty at `κ=0` already); fragmentation is what makes the *real* one **rise**.

**The object, in one sentence.** Bound each agent's conformity/attachment neighbourhood
to a fixed size `m ≪ N` and make membership **persistent**, so the population carries
**many local canons** that drift apart as it grows — instead of one global canon every
agent sees. That is the whole addition. Everything else is recombination of machinery
already built and (for the within-niche floor) already Level-3 anchored.

**Explicitly a channel/substrate rung, not the synthesis.** This is the primer's
deferred content/`τ` layer (Phase-2 Tier-2 material) pulled forward because the
empirics made it load-bearing. No phase diagram / Pareto here (that stays rung 5).

---

## 1. The object: shape, assumptions, provenance (the anti-bolt-on argument)

### 1.1 Shape
A **persistent, bounded interaction partition** laid over rung 4a/4b's multi-prereq
attachment substrate:

- **Bounded neighbourhood.** Each agent `i` has a fixed attention set `M_i` of size
  `m` (the works/peers it can copy-attach from). `m ≪ N`.
- **Persistence.** `M_i` is drawn **once** and held across generations — this is the
  single genuinely new primitive. (Rung 4c drew a *fresh* `m`-sample every generation;
  that bounds each agent but re-mixes the field every step, so it does **not** fragment.
  Persistence is what lets neighbourhoods **drift apart**.)
- **Local canon.** Lateral preferential attachment draws prereqs `∝` in-degree **within
  `M_i`'s reach**, so each neighbourhood accretes its *own* canon `H_c`. Conformity uses
  the local canon: `κ_i = λ · H_{c(i)} · (1 − γ_i^{local})`, with `γ` measured against
  the agent's *local* canon, not the global one.
- **Emergent niche count.** With `m` fixed and `N` growing, the number of effectively
  decoupled neighbourhoods grows as `K(N) ≈ N / m(N)`. `K` is **not a knob** — it is
  forced by `N` and the independently-measured `m`.

### 1.2 The three assumptions it encodes (each a commitment, not a knob)
1. **Bounded attention** (`m` fixed, independent of `N`) — the load-bearing one. A
   generic law: division of labour grows with scale (Durkheim, Carneiro), limiting
   similarity under competition (MacArthur–Levins), bounded cognitive/reading capacity.
   *Not invented for this dataset.*
2. **Locality of conformity** — you align to your niche's canon, not the global one.
   (Global conformity = the special case `m = N`, i.e. rung 4b.)
3. **Persistence** — niches carry over and accrete local canons. The delta over 4c.

Note what is **not** an independent assumption: `K(N)` is a *consequence* of (1)+(3)
under growth, not an input.

### 1.3 Provenance (why it is generic, not a bolt-on)
The rung adds **one** new primitive (persistence of the bounded partition) and **reuses
two already-anchored** ones:

| Ingredient | Source | Anchor level |
|---|---|---|
| Bounded `m`-sample + within-niche floor `ε/(1−f·m)` | rung 4c `roles.py` | **Level 3** (Strimling/Enquist) |
| Local canon `H_c = Gini(closure)`, lateral PA | rung 4a `canon.py` | rung-4a construction (WSC-anchored) |
| `V^struct/V^lat` split, collective breadth `W` | rung 4b `channel.py` | rung-4b construction |
| **Persistent bounded partition** | **new** | Level 2 + empirical (§4) |

If the rung needed genuinely new, unvalidated dynamics to fit the data, *that* would be
the bolt-on smell. It does not: the fragmentation signature is 4c's bounded sampling
made **persistent and spatial**, inheriting 4c's Level-3 within-niche result.

### 1.4 The independent-parameter discipline (what stops it fitting)
`m` is **pinned off-trend** — from reference-list length / number of communities a
scholar tracks in the WS2 data (papers engage `~m` prior works), **never** fit to the
novelty slope. `ε` is the innovation rate already in the model. **Given `(m, ε)` the
within/between decomposition and the `K(N)` exponent are forced, not fit.** Contrast a
free "fragmentation parameter" `φ(t)`: it fits *any* row of the ledger below (up →
fragmentation, down → consolidation) and therefore has zero content. The object earns
its content precisely because `m` is measured, then the split is *forced*.

---

## 2. The forbidden ledger (the anti-vacuity argument — pre-registered pass/fail)

The specificity requirement is operationalised as a table of outcomes the object must be
**structurally incapable** of producing. Each row is a *test* (§6, T9): we attempt to
produce it by parameter search and assert the model refuses. A structure that admits any
row is too loose to have explained the data.

| # | Hypothetical observation | Verdict | Structural reason it is forbidden |
|---|---|---|---|
| F1 | global `V^struct↑` **and** within-niche `V^struct↑` equally | **FORBIDDEN** | requires `m → N` (unbounded attention) — contradicts the fixed-`m` premise |
| F2 | global `V^struct↓` under growth (consolidation) | **FORBIDDEN** | fixed `m` + growing `N` can only *add* decoupled niches; a global decline needs a **separate, declared** global-coupling term |
| F3 | fragmentation **with** global de-concentration (`H↓`) | **FORBIDDEN** | local PA sharpens local canons ⇒ concentration co-occurs by construction |
| F4 | within-niche `V^struct↓` while global `↑` | **FORBIDDEN** | within-niche sits at the **positive** Strimling floor `ε/(1−f·m)`; it cannot fall below it |
| F5 | `K ∝ N` (every paper its own niche) | **FORBIDDEN** | bounded-`m` mixing ⇒ **sub-linear** `K(N)`; linear proliferation violates the attention bound |

**Non-vacuity demonstration (crucial).** The ledger must forbid these *because of this
object*, not tautologically. So F2 is tested twice: (a) the headline object refuses
global `V^struct↓`; (b) when the **declared escape hatch** — an explicit global-coupling
term `η` forcing all niches to attach to a shared canon — is switched on, the model
**does** produce global `↓`. That the sign is recoverable *only* via a named, separate
mechanism proves the ledger is a property of the fragmentation object, not of the test
harness. (`η` is out of the headline; it exists only to prove F2 is real.)

**The admissible slice** (the *only* signature the object can produce): global
`V^struct↑`, within-niche flat, `H↑`, `W↑`, `K(N)` sub-linear — i.e. exactly the Phase
2.4 fingerprint. A thin slice; everything else is refused.

---

## 3. Pre-registered hypotheses

Criteria are **regression slopes on `log N` with seed-bootstrap CIs** (never two-point
differences — the WS2 ill-conditioned-σ lesson), using `conformity.logN_slope_ci` /
`steady_grid`.

| # | Hypothesis | Criterion | Maps to |
|---|---|---|---|
| **H1** | **The sign-flip (crux).** Persistent bounded-`m` niches flip global `V^struct` from *falling* (rung 4b) to *rising* in `N`. | global `V^struct` slope `> 0` (CI excludes 0) with `m≪N`; `< 0` as `m→N` | the empirical `V^struct↑` |
| **H2** | **Within-niche flat (the fingerprint).** Within-neighbourhood `V^struct` is `≈N`-independent. | `|within slope| ≤ (1/5)|global slope|` | 2.4's `9–13×` gap |
| **H2a** | **The floor is Strimling (anchor).** Within-niche per-agent structural repertoire matches `ε/(1−f·m)`. | within-niche level within tol of `strimling_lambda_f(ε,f,m)` | Level-3 sub-anchor |
| **H3** | **Concentration co-occurs (orthogonality).** Global `H` still rises with `N` while global `V^struct` rises. | `H` slope `> 0` **and** `V^struct` slope `> 0` jointly | 2.3 `H↑` + 2.4 `V^struct↑` |
| **H4** | **Breadth preserved.** Collective `W↑`; no collapse. | `W` slope `> 0` | WS2 `W↑` (WSC:indep) |
| **H5** | **Niche-proliferation scaling.** `K(N) ≈ N/m(N)`; with measured `m(N)` growth, sub-linear. | `K` slope on `log N ∈ (0,1)`; consistent with `N/m` | OpenAlex concept growth (Heaps) |
| **H6** | **`m` is the lever (dose-response).** The flip is *caused* by bounded `m`: the within/global gap → 0 monotonically as `m→N`, and 4b's decline returns. | monotone gap-vs-`m` | the placebo (m→N) |

**Honest-null clause.** If the persistent partition does **not** flip the global slope
(e.g. the between-niche term is too weak to overcome 4b's within-decline at realistic
`m`), report it: that would say fragmentation-of-canons is *not* sufficient to reproduce
`V^struct↑` and a different structure (endogenous nucleation, growing niche *interiors*)
is needed. The claim stands only on the *verified* sign-flip.

---

## 4. Anchor status (reproduce-published-numbers standard)

Honest Level accounting — the new mechanism is the **contribution**, so no published
*number* reproduces it (that is the point), and we say so per the standing rule:

- **Within-niche floor `ε/(1−f·m)` — Level 3 (inherited).** rung 4c already anchored it
  to Strimling 2009 (via the open LAF 2011) + Enquist 2010, incl. the number `0.2`. H2a
  rests on that published number — the *flat within-niche* limb of the fingerprint is
  Level-3 grounded.
- **Endogenous `H` concentration — rung-4a construction** (WSC-anchored, not a published
  number).
- **The fragmentation mechanism (bounded persistent `m` → global↑/within-flat) — Level 2
  (derived + verified in-model), with two external anchors:**
  1. **Empirical fingerprint (primary):** the model's within/global slope ratio must be
     consistent with Phase 2.4's `9–13×` gap (order of magnitude) — a *pre-registered,
     reproducible* target (`whitespace_2/experiments/phase-2.4/analyze.py`).
  2. **Scaling law (secondary, checkable):** `K(N) ≈ N/m(N)` predicts a specific
     sub-linear niche-proliferation exponent, checkable against OpenAlex
     concept-vocabulary growth (Heaps' law). Disagreement refutes it *independently* of
     the novelty trend.
- **Genericity anchor (qualitative):** division-of-labour-scales-with-population
  (Durkheim, Carneiro) and limiting similarity (MacArthur–Levins) — the object is a known
  social/ecological law, not a dataset-specific invention.
- **Why Level 3 is unavailable for the new mechanism:** no existing ABM decomposes
  within- vs between-niche per-capita novelty (the primer's own "no existing ABM
  decomposes these"). Documented, per the reproduce-published-numbers rule.

---

## 5. Representation / module

New module **`src/whitespace3/subfield.py`** (reuses `canon.gini/closure_weights`,
`channel.variance_split`, `innovation.suppression`, `conformity.logN_slope_ci/
steady_grid`):

- **State.** rung 4a's multi-prereq DAG + a persistent agent→neighbourhood map. Each
  agent holds a fixed `M_i` (size `m`); the "niche" is a neighbourhood/community.
- **Transmission.** As 4a, but coherent acquisition restricted to reachability within
  `M_i` (you learn what your neighbourhood carries).
- **Innovation.** Lateral PA draws prereqs `∝` local in-degree within `M_i` ⇒ local
  canons; conformity `κ_i = λ·H_{c(i)}·(1−γ_i^{local})` uses the local canon.
- **Emitted measures (the empirical bridge).** `V^struct_global` (attachment-structure
  variance across *all* agents ↔ global atypicality), `V^struct_within` (same, within
  each niche, averaged ↔ within-subfield atypicality), `H_global` (Gini closure on the
  union DAG ↔ canon concentration), `W` (effective #niches / topical breadth), `K`
  (#effective niches).

**Minimal instantiation (headline):** persistent `m`-blocks, `m` measured, `K=N/m`
forced. **Robustness variants (the ≥2–3-spec discipline):** (b) bounded-reach geometry
(agents on a line, attend to `m` nearest — limiting-similarity/adaptive-radiation
realisation, `K` emerges from a correlation length `~m`); (c) endogenous nucleation (a
new niche seeds when low-local-`γ` lateral innovation lands far from every canon). The
**sign-structure and the forbidden ledger must be invariant** across (a)/(b)/(c) — the
analog of the ≥3-`κ`-specs rule.

---

## 6. TEST (TDD — green before any claim)

- **T1 — determinism.** Same seed ⇒ identical trajectories.
- **T2 — the sign-flip (H1, crux).** global `V^struct` slope `> 0` (CI excludes 0) at
  `m≪N`; `< 0` as `m→N`. Seed-bootstrap, not two-point.
- **T3 — within-flat (H2).** within-niche slope `≈0`, `|within| ≤ (1/5)|global|`.
- **T4 — Strimling floor (H2a, Level-3 sub-anchor).** within-niche per-agent structural
  repertoire ≈ `strimling_lambda_f(ε,f,m)` within tol.
- **T5 — concentration co-occurs (H3).** `H` slope `>0` jointly with `V^struct` slope `>0`.
- **T6 — breadth (H4).** `W` slope `>0`.
- **T7 — `K(N)` scaling (H5).** `K ≈ N/m`; with an `m(N)` growth input, sub-linear
  `log K`–`log N` slope.
- **T8 — `m` dose-response (H6).** within/global gap monotone-decreasing in `m`.
- **T9 — THE FORBIDDEN LEDGER (the discipline test).** For each of F1–F5, a parametrised
  attempt to produce it fails; **and** the F2 escape-hatch demonstration succeeds *only*
  with the declared global-coupling `η` on (non-vacuity).
- **T10 — input validation** (`2 ≤ m ≤ N−1`, `f,ε,λ ∈ [0,1]`, …).
- **T11 — sensitivity (slow, baked in).** sign-structure + ledger invariant across
  neighbourhood realisations (a)/(b)/(c).
- **T12 — placebo (m→N).** one niche recovers rung 4b's global `V^struct↓` (the
  `κ=0`-analog null for this rung).

## 7. Validation gates (rung 4d "done")

1. T1–T12 green; ruff + mypy strict clean; pre-push hook passes.
2. **H1 sign-flip confirmed with CI** (the crux).
3. **H2 within-flat + H2a Strimling-floor Level-3 sub-anchor matched.**
4. **The forbidden ledger verified** — model refuses F1–F5; the `η` escape-hatch proves
   non-vacuity (F2 recoverable only via a named separate mechanism).
5. Empirical-fingerprint anchor: model within/global ratio consistent with 2.4's `9–13×`
   (order of magnitude).
6. Sign-structure + ledger invariant across ≥2–3 neighbourhood realisations.
7. rung-4d retro: the reframe (CC6 disconfirmed → fragmentation reproduces the *actual*
   signature), reconciliation-as-**orthogonality** (not `κ`-trade-off), `m`-pinned-off-
   trend, and the primer update (CC6/`cc:open` superseded).

## 8. Non-goals

- **No re-litigating CC6** (falsified — that is the premise, not a question).
- **No global-coupling `η` in the headline** — it exists solely as the F2 non-vacuity
  probe.
- **No fitting `m` to the novelty trend** — `m` is pinned off-trend (reference behaviour);
  fitting it would forfeit the whole discipline.
- **No new Level-3 *number* claim** for the fragmentation mechanism (documented — it is
  the contribution); Level 3 is inherited only for the within-niche floor.
- **No phase diagram / Pareto / Modal sweep** (rung 5; laptop-scale here).
- One rung, one job: **reproduce the Phase-2.4 fingerprint from one persistent-bounded-`m`
  partition, and prove the object could not have reproduced its negation.**

---

## 9. Post-prototype amendment (2026-07-07) — mechanism disconfirmed and replaced

§§0–8 are the pre-registration as written **before** prototyping. Prototyping (four
scratchpad tests, all seeded) **disconfirmed the specific mechanism** (disjoint `m`-blocks
with private per-niche elements) and **confirmed the fingerprint is reproducible** by a
different realisation of the *same* bounded-`m` primitive. This section supersedes the
mechanism in §1/§5; the hypotheses, the forbidden ledger, and the primitive itself
survive (with the re-anchoring below). Reported honestly per the null-results rule.

### 9.1 What was disconfirmed, and why

The headline instantiation of §5 — niches as **disjoint islands of their own
low-usage elements** — produces the fingerprint's *within-flat* limb but the **wrong
sign** on the *global-rise* limb. Triangulated four ways:

| test | global novelty | within | verdict |
|---|---|---|---|
| cross-`N` sweep (off-canon, marginal) | flat (`−0.007`) | flat | wrong (no rise) |
| cross-`N` sweep (Uzzi atypicality) | **conventionalises** (z `+2.6`) | flat | wrong sign |
| soft geometry (bw→`1/K`) | conventionalises (z `+1.2`) | flat | wrong sign |
| **faithful frame** (one null, z-vs-birth) | conventionalises (`+0.040`) | flat (`+0.005`) | wrong sign |

**Root cause (structural, not measurement):** islands are built from *low-global-degree*
elements. Under the degree-preserving null, two rarely-used elements that co-occur even
once look *surprisingly conventional* (obs ≫ tiny expectation) → high z. Real atypical
work is the opposite: **globally *popular* references combined in a rarely-done way**
(obs ≪ expectation) → low z. Islands have no shared, high-degree canon to recombine, so
the model's within/global relationship comes out *inverted* vs the data (model: global
more conventional than within; data: global more atypical). The faithful within-corpus
birth-time frame (the true analog of `panel_year_test`) did **not** rescue it — so it is
the mechanism, not the measurement.

### 9.2 The confirmed mechanism — shared-canon recombination over a growing vocabulary

Verified to reproduce the fingerprint (`verify_recombination.py`): niches **recombine a
shared, heavily-used vocabulary** (popularity accumulates across niches ⇒ high global
degree) via **persistent niche lenses** (each niche characteristically combines two
regions of a latent content space); **the vocabulary and the niche count grow with
scale**. A late niche pairs *popular* elements in *its* way — a pairing few niches use ⇒
globally rare relative to the pieces' popularity ⇒ atypical globally, standard locally.

Verified signatures (faithful frame, seeded):
- **global novelty rises** with birth-time (slope `−0.020` at `bw=0.035`), **within-niche
  flat** (`+0.000`), and the **relationship is now correct** (mean z global `−1.15` <
  within `−0.01`).
- **fragmentation is the driver, not recency:** the **K-fixed control never rises**
  (`+0.023`) — a pre-registered placebo now *demonstrated*, not just asserted.
- **concentration co-occurs (F3, now verified):** `H_global` (Gini of citation degree)
  **rises** with field size (`0.79 → 0.83`) *while* novelty rises — concentrates at the
  top, fragments in the middle, exactly the WS2+2.4 picture.

### 9.3 The single bounded-`m` lever (this is what fixes F5 and restores the discipline)

The prototype's `K`-growth and lens-width were *free inputs* — discipline debt (F5's
"`K` forced by bounded `m`" was lost). The fix is **one lever**: bounded reach over a
**growing shared vocabulary**. As the field grows (`E ∝ N`), a fixed `m`-element reach is
a bandwidth that **shrinks automatically** (`bw ∝ m/E`), niches **tile** the growing space
(`K ≈ E/m ∝ N/m`), and a single measured `m` drives *both*. This:
- **satisfies F5 by construction** (`K ∝ N/m`, sub-linear once `m` grows with the corpus);
- **kills the saturation** the sweep exposed (at *fixed* `bw`, `K`↑ weakens the effect:
  slope `−0.042 → −0.002` as `K:10→80`; shrinking `bw` with `N` prevents it);
- **re-pins anti-bolt-on** (`m` measured off-trend; it is *the* free parameter, not `K`
  or `bw` separately).

**The sign flip is a tunable crossover, not knife-edge** (robustness, Q2): monotone in
`bw`, sign-change at **`bw* ≈ 0.05`** (`−0.080, −0.039, −0.020, +0.007, +0.016, +0.013`
across `bw = 0.010…0.160`). This is the `λ*` crossover shape of rung 3/4a — a locatable
phase boundary, a strength. The rung must **locate `bw*`/`m*`** (reuse
`conformity.locate_lambda_star`-style logic), not just exhibit one point.

### 9.4 Re-anchored forbidden ledger + constraints

| row | status after prototyping |
|---|---|
| **F1** (global↑+within↑ needs `m→N`) | ✅ verified — wide lens (`bw≥0.06`, → `m→N`) kills the flip |
| **F2** (global↓ forbidden) | 🟡 partial — wide-`bw`/K-fixed conventionalise; the shared-lens `η` escape-hatch demo still owed |
| **F3** (must coexist with `H↑`) | ✅ **verified** — `H_global` `0.79→0.83` while novelty rises |
| **F4** (within↓ forbidden) | ✅ outcome holds — but **mechanism re-anchored: lens-persistence, NOT the Strimling floor** |
| **F5** (`K` sub-linear, forced) | ✅ **by construction** once `K`,`bw` are driven by the single bounded-`m` over a growing vocabulary |
| placebo (K-fixed) | ✅ **demonstrated** (never rises) |

**H2a retired.** The within-flat limb is no longer the Strimling `ε/(1−f·m)` floor (the
recombination model has no independent-traits accumulation; within mean z ≈ 0, not a
positive floor). Within-flat is now anchored on **lens-persistence** (a niche's
characteristic pairing is standard *in its own frame*, and stays so because the lens does
not drift). Level 3 is therefore **not** inherited here; the anchor is the empirical
fingerprint (2.4) + the `λ*`-analog crossover. Documented per the
reproduce-published-numbers rule — the fragmentation mechanism is the contribution.

### 9.5 Corrected measurement frame

The V^struct fingerprint is measured the **faithful way** — one large run, one fixed
full-corpus null, atypicality regressed on **element birth-time** (the analog of
`panel_year_test` on year), global frame vs within-niche frame. **Not** the cross-`N`
`logN`-slope of §3 (that frame has a null-scale confound — bigger corpus mechanically
shifts z). `H_global` and `K` (no such confound) are still read across scale.

### 9.6 Amended module + tests

`src/whitespace3/subfield.py` is the **content/`τ`-channel** model (its own substrate —
elements in a latent content space, bounded-`m` niche lenses, growing shared vocabulary),
reusing `canon.gini` and the `conformity` slope/CI tooling; it does **not** reuse the
attachment-DAG dynamics (a different channel — `τ` is ungoverned by `κ`, per the primer).
`C` is the attachment channel's business (rungs 1–4b); rung 4d owns V^struct + `H_global`
+ `K`.

- **T1 determinism.**
- **T2 the sign-flip (crux).** global atyp-vs-birth slope `< 0` (seed-bootstrap CI
  excludes 0) with `m≪E`; `≥ 0` as `m→E` (wide lens).
- **T3 within-flat.** within-niche slope `≈ 0`, `|within| ≪ |global|`.
- **T4 fragmentation-is-the-driver (placebo).** K-fixed run: global slope not `< 0`.
- **T5 concentration co-occurs (F3).** `H_global` rises with field size while novelty
  rises.
- **T6 the crossover (robustness).** global slope monotone in `bw`; a locatable `bw*`.
- **T7 `K ∝ N/m` (F5).** niche count scales sub-linearly, forced by `m` over the growing
  vocabulary.
- **T8 input validation.**
- **T9 (slow) sensitivity.** sign-structure invariant across content-space dim / lens
  shape / popularity law.

Superseded from §6: T4-Strimling-floor (H2a retired), and the cross-`N` `V^struct` slope
framing (replaced by the birth-time frame).
