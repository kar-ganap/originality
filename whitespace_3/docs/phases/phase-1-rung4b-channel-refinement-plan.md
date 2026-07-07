# WS3 Phase 1 · rung 4b — The channel refinement: `κ` on structure, the WS2 signature

**Whitespace:** 3 · **Phase:** 1 (the ABM core), rung 4b (Tier 2 proper).
**Branch:** `ws3-phase-1-channel-refinement`
**Status:** PLAN (plan-first; pre-registration locked before code).
**Builds on:** rung 4a (`canon.py`) — endogenous `H` on the multi-prereq graph, with
*uniform* `κ=λ·H` (weak, total-`V` crossover). rung 4b makes `κ` **targeted**.
**Formal spine:** primer §4.3 (`κ` acts on the attachment channel — suppresses low-`γ`
structurally-deviant novelty, spares content), Def 5.3 (`V^struct/V^lat` split),
Constraints WSC:channel + WSC:indep, Core Claim 6 (the open prediction `V^struct↓`).

---

## 0. Scope — targeted `κ` and the WS2 signature `W↑` with `V^struct↓`

Add the **canon** `K_α` (top-`α` elements by closure weight), **canon-alignment**
`γ(e')` (share of an innovation's prereqs that are canonical), and make `κ` **targeted**:
it suppresses **structurally deviant** (low-`γ`) innovation while **sparing**
canon-aligned / lateral content — `κ_eff(e') = λ·H(t)·(1−γ(e'))`. Instrument the
`V^struct/V^lat` split and collective breadth `W`. Show the model reproduces **WS2's
actual empirical fingerprint**: `W(t)↑` (breadth rises with scale) **while**
`V^struct(t)↓` (per-capita *structural* novelty falls) — the CC6 open prediction and
the WSC:channel constraint.

**Deferred (later rungs):** network topology + bounded-degree saturation (rung 4c);
phase diagram + Pareto/selective-isolation + analytics (rung 5).

---

## 1. Pre-registered hypotheses

Prototype numbers from `scratchpad/verify_channel.py` (2026-07-07) at `λ=3`; the build
re-establishes on the committed model with seed-CIs + the sensitivity sweep.

**Honest decomposition (calibration, 2026-07-07 — corrects the naive "κ ⇒ `V^struct↓`").**
The `V^struct` *decline with `N`* is partly **endogenous** — it falls even at κ=0
(canon concentration makes new work increasingly canon-aligned, so the structural
*fraction* falls with scale). What κ does is (a) crush the structural *level* (~0.22 →
~0.02, both uniform & targeted), and (b) *under targeting only*, **spare breadth**.
The *full* WS2 fingerprint — structural novelty low & falling **while** breadth thrives
— is therefore **unique to targeting** (κ=0 leaves structure high; uniform κ kills
breadth). Prototype numbers at `λ=3`, `f=0.6`:

| # | Hypothesis | Criterion | Prototype (off / uniform / targeted) |
|---|---|---|---|
| **H1** | **The full WS2 signature (headline).** Under **targeted** κ: `W↑` (strong) **while** `V^struct` is suppressed & falling. | `W` slope CI `>0` **and** `V^struct` slope CI `<0` | `V^struct −0.009`, `W +116` |
| **H2a** | **Targeting spares breadth (vs uniform — the κ-channel effect).** `V^lat`/`W` rise far more under targeted than uniform, which crushes them. | targeted `W` slope `≫` uniform; targeted `V^lat` slope `> 0 ≈` uniform | `W`: +274 / **+25** / **+116**; `V^lat`: +0.014 / **−0.00** / **+0.029** |
| **H2b** | **κ crushes the structural *level* (vs κ=0).** Both uniform & targeted drop `V^struct` ~10×. | `V^struct*` (targeted) `≪` `V^struct*` (off) | `V^struct*`: **~0.22** / ~0.02 / ~0.02 |
| **H3** | **Reconciliation intact.** `C*↑` while `V^struct↓` under targeted κ. | `C*` slope CI `≥0`, `V^struct` slope `<0` | `C +3.1` while `V^struct −0.009` |
| **H4** | **The reframe.** Total per-capita `V` need *not* fall (breadth thrives); the WWE decline is `V^struct`, not total-`V`. | total-`V` slope may be `≥0` | total `V` slope `≈ +0.02` |
| **H5** | **Fidelity gate (deep, not a uniform-κ artifact).** `V^struct↓` needs `f≥0.5`; flat at `f=0.3`. | `V^struct` slope `<0` at `f≥0.5`, `≥0` at `f=0.3` | f=0.3 `+0.0001`; f=0.5 `−0.006`; f=0.7 `−0.013` |

### Negative controls (pre-registered — the two discriminators)

| # | Control | Must show |
|---|---|---|
| **NC0** | κ=0 placebo. | `V^struct` stays **high** (not crushed); breadth free — the no-conformity baseline that κ suppresses against. |
| **NC-uniform** | `κ=λ·H` (untargeted, `γ`-independent) — same driver, no channel targeting. | breadth **collapses** (`W` slope `≪` targeted; `V^lat` flat) — isolating that it is *targeting the structural channel* that yields the full `W↑`-with-`V^struct↓` fingerprint (WSC:indep). |
| **γ non-degeneracy** | the structural-innovation fraction is nonzero. | `frac_struct > 0` (prototype: `0.43→0.04` across `N`). |

**Honest-null clause.** If targeting does **not** separate the channels (`V^lat`/`W`
collapse like uniform, or the targeted `W`-slope is indistinguishable from uniform),
the WSC:channel reading fails and is reported — the reconciliation would then be
uniform-suppression only (rung 4a), not the two-channel WS2 form.

---

## 2. Representation / module

New module **`src/whitespace3/channel.py`** (reuses `canon.py`'s `closure_weights`,
`gini`, `reproducible_frontier_multi`; `innovation.suppression`, `variance_series`):

- **Canon** `K_α(t)` = top-`⌈α·E⌉` elements by closure weight (recomputed per gen).
- **Innovation with per-event suppression.** Agent innovates at base rate `ε`; draws
  `p` prereqs (vertical: deepest held; lateral: `∝` in-degree); computes
  `γ = |prereqs ∩ K_α| / |prereqs|`; the event **succeeds** with prob
  `g(κ_eff)`, `κ_eff = λ·H·(1−γ)` (**targeted**) or `λ·H` (**uniform** control) or `0`
  (off). A minted element is **structural** iff `γ < γ_thresh`.
- **Outputs:** `V^struct`, `V^lat` (persistence-filtered novelty split by the birth
  `γ`-class), `W` (collective breadth = repertoire size — a `C`-family collective
  gauge, cf. primer: `W` is a cousin of `C`, *not* `V^lat`), plus `C`, `H`, total `V`.
- Params: `alpha=0.15` (canon fraction), `gamma_thresh=0.5`, `mode ∈ {off, uniform,
  targeted}`, `g_map`, and the rung-4a set. Well-mixed (topology = rung 4c).

---

## 3. TEST (TDD — written and green before any claim)

- **T1 — determinism** (same seed ⇒ byte-identical `V^struct/V^lat/W/C/H`).
- **T2 — κ=0 placebo (NC0)** — no `V^struct` decline; and `mode="off"` ⇒ total-`V`
  behaves as the rung-2b/4a null.
- **T3 — metric correctness** — `K_α` (top-`α` by closure), `γ` on hand-built prereqs,
  and the `V^struct/V^lat` split on hand-built birth-classes; `V^struct+V^lat == V`.
- **T4 — THE WS2 signature (H1, headline)** — targeted `κ`: `W` slope CI `>0`
  **and** `V^struct` slope CI `<0` (both, together).
- **T5 — targeting spares breadth vs uniform (H2a, NC-uniform)** — targeted `W` slope
  `≫` uniform `W` slope; targeted `V^lat` slope `>0` while uniform `V^lat` slope `≈0`.
- **T5b — κ crushes the structural level vs κ=0 (H2b, NC0)** — `V^struct*` under
  targeted `≪` `V^struct*` at `mode="off"` (κ suppresses structure; the decline-with-N
  is partly endogenous, present at κ=0).
- **T6 — reconciliation (H3)** — `C*` slope CI `≥0` while `V^struct` slope `<0`.
- **T7 — fidelity gate (H5)** — `V^struct↓` at `f≥0.5`, flat at `f=0.3` (the deep boundary).
- **T8 — sensitivity sweep (baked in per the standing commitment)** — the signature
  (`V^struct↓`, `W↑`) holds across `ε, b, p, g, α, γ_thresh` (one-axis-at-a-time,
  seed-CIs), documenting any boundary. `slow`.
- **T9 — input validation** (`α∈(0,1]`, `γ_thresh∈[0,1]`, `mode`, …).

Fast sign-checks gate the pre-push hook; thorough / sweep variants are `slow`.

---

## 4. Estimand + estimation discipline (unchanged)

Steady-state `V^struct*, V^lat*, W*, C*, H*` = post-burn-in window means, across-seed
CIs. Slopes = regression on `log N` with seed-bootstrap CI — never two-point. `C*` and
the `V`-components absolute and separate — never a ratio. Adequate fidelity (`f≥0.5`)
is the default regime (rung 4a/H5); low-`f` is exercised only by the boundary test.

## 5. Anchor status (reproduce-published-numbers standard)

- **The WS2 signature is the anchor.** `W↑` is WS2's *measured* rising topical breadth;
  `V^struct↓` is **Core Claim 6** — the open per-capita prediction WS2 left for the
  V-extension (`docs/primers/v-extension-empirical-spec.tex`). Reproducing `W↑` *with*
  `V^struct↓` from one targeted mechanism is the WSC:channel + WSC:indep payoff — the
  strongest WS2-consistency result in the program, though a *qualitative signature*
  match, not a Level-3 number (the crossover remains novel; no published number).
- **NC-uniform** is the internal discriminator (only *targeting* gives the signature).

## 6. Validation gates (rung 4b "done")

1. T1–T9 green (fast in the pre-push gate; sweep/thorough `slow`); ruff + mypy strict
   clean; pre-push hook passes.
2. H1: the WS2 signature (`V^struct↓`, `W↑`) with seed-CIs.
3. H2/NC-uniform: targeting spares content; uniform does not.
4. H3: reconciliation `C*↑ / V^struct↓`.
5. H4 reframe documented; H5 fidelity boundary confirmed.
6. Sensitivity sweep (T8) run and any boundary documented.
7. rung-4b retro written.

## 7. Non-goals (guardrails)

No network topology / bounded-degree saturation (rung 4c), no phase diagram / analytics
/ Pareto-isolation (rung 5), no Modal sweep. One rung, one job: **targeted `κ`
reproduces WS2's `W↑` with `V^struct↓`.**
