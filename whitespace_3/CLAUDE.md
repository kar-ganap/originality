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

- **Stage:** Phase 0 (substrate on-ramp) — STARTING. Prelude COMPLETE.
- **Prelude (this session, on branch `ws3`):**
  - `docs/primers/cv-reconciliation-primer.tex` — unambiguous parameters; the
    surviving hypotheses (refined 13-D + 13-H) in the model's language; **Core
    Claims 1–6** (shape + scaling) constrained by WS2.
  - `docs/primers/v-extension-empirical-spec.tex` — the empirical instrument for
    Core Claim 6 (per-capita structural novelty), reusing WS2 data.
  - `docs/phases/phase-1-abm-core-plan.md` — the ABM Phase plan (5-rung ladder,
    pre-registered hypotheses ↔ Core Claims, Modal sweep design).
- **Next:** Phase 0 rung 1 — reproduce Henrich 2004 / Powell 2009 (the
  known-answer harness anchor + substrate fluency).

## The WS3 arc (four phases)

- **Phase 0 — substrate on-ramp.** Read the ~6 core papers; build + validate the
  **transmission harness** that reproduces the Henrich/Powell critical-population-
  size result (`src/whitespace3/transmission.py`). This is rung 1 of the ABM plan
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
   `κ=0` must not produce the crossover).
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
  review): **Powell–Shennan–Thomas 2009** (the N→complexity ABM to reproduce),
  **Henrich 2004** (Tasmania / critical population size), **Vaesen et al. 2016**
  (the robustness critique), **Derex et al. 2013**, **Wu–Wang–Evans 2019**,
  **Zollman 2007/2010** (network-epistemology ABM template).
- Program context: `../docs/program/` (overview, deep-research pathways).

## Known Gotchas

- **The crossover is the only hard part.** Transmission→`C` (Powell) is classical;
  the joint `C`–`V` response is emergent. Spend your attention on how `κ` must
  scale for per-capita `V` to flip sign in `N`.
- **Don't over-fit to WS2.** Keep the reconciliation in the minimal Tier-1 model;
  add the attachment-channel refinement only as the Tier-2 empirical layer.
- **Keep analytics light.** Mean-field / steady-state approximations, guided by
  the simulation — not airtight theorems (the compass says so).
- **Scope discipline:** this is an abstract mathematical ABM (CPU, laptop-scale).
  Do NOT drift toward WS1's realistic-agent model.
