# Scaled WS1 for OpenAI Build Week — a multi-agent GPT-5.6 diversity-collapse study

## Context

**Why.** WS1 — the program's *mechanistic / counterfactual* leg — was shelved as out of personal
budget (~$7–40K). **OpenAI Build Week** (Jul 13–21; build with **Codex** + **GPT-5.6**; credits TBD)
is the chance to fund a scaled version: a hackathon build *and* the program-completing experiment.

**Decisions locked.** Wait for the Jul 13 rules (this is the ready blueprint). Domain-agnostic engine.
After an **independent soundness review**, two design corrections are baked in: (1) **collapse must be
ENDOGENOUS** — it emerges from LLM agents conditioning on a shared catalog, *not* imposed by a numpy
filter (which would make "diversity collapses" near-definitional and the LLM decorative); (2) the
**autonomous Codex harness + full observability are post-WALK flourishes**, never on the critical path
to the science. Plus: a Day-0 kill-test, a real statistical plan, and rungs labeled by **time-risk**.

## Preservation + porting (so a fresh Jul-13 repo stays clean)

This is a **design doc, not code** — so preserving it does not touch any "built from scratch during the
event" rule (which restricts *code*). **Where it lives:** on approval, saved to
**`originality/docs/program/ws1-hackathon-plan.md`** (version-controlled, alongside the canary docs, in
the *research* repo — cleanly separate from the hackathon build). **On Jul 13:** `git init` a *fresh*
`ws1/` repo (created during the event) and port this in as its **`CLAUDE.md`** + the Codex **`Prompt.md`**
(frozen spec); the **`Plan.md`** milestones come from the ambition ladder + the execution steps.
**The two reused packages** (`diversity_metrics`, `cv_predictor`) + the WS2 seed data are **cited
dependencies** (`pip install` / a Volume), not pre-built hackathon code — which every hackathon permits;
if the rules are strict, publishing the packages as public pip libraries beforehand makes that
unambiguous (a portfolio win anyway).

## Relevance verdict — WS1 is NOT redundant given canary

Canary is the AI **single-model / recursion (κ)** arm. WS1 owns the **mechanistic/counterfactual** leg
— persona-conditioned **multi-agent** dynamics + a tunable **shared-catalog actuator** +
**intervention-testing** — which *causally* tests the founding claims (#13, #17) that WS2 could only
observe and WS3 only theorize.

| | owns |
|---|---|
| WS2 (human) | observational: concentration + fragmentation |
| WS3 (theory) | the C/V mechanism + crossover λ*≈0.09 + orthogonality + the ι intervention |
| canary (AI) | single-model recursion (κ) collapse |
| **WS1 (AI)** | **multi-agent + counterfactual catalog manipulation + intervention-testing + personas** |

**Frontier reframe.** The human system *resisted* intellectual collapse (WS2's null), **but AI systems
have far stronger actuators** (shared foundation models, recommenders, RLHF / synthetic-data loops). A
multi-agent AI collective is where that mechanism should *bite* — and where the intervention matters.

## Ambition ladder — crawl → walk → run → sprint (labeled by TIME-RISK, not $)

The GPT-5.6 findings make the science **cheap (~$1–50)** — so the binding constraint is **engineer-hours,
not money**. Aim higher, but climb a ladder where **each rung is a complete, de-risked deliverable**;
bank the lower rung before reaching. **Rungs are fixed; the aim-point + domain skin are set Jul 13.**

- **CRAWL (~½ day, low risk).** The engine on a **mock agent** (loop + measurement + `cv_predictor` +
  dashboard, all token-free + unit-tested) **+ the Day-0 kill-test** (below). *Deliverable: it runs;
  the two load-bearing assumptions are verified.*
- **WALK (~1–2 days, low-moderate risk). THE FLOOR — banked before climbing.** Real GPT-5.6 (Luna/
  `minimal`), small N: the **endogenous causal result** — outputs homogenize under shared-catalog
  conditioning, and the **catalog-ablation** proves it's the LLM's doing (not a filter) — + the
  insulation intervention, with a **statistical plan**. *Deliverable: the minimal publishable + demo-able
  result.*
- **RUN (~2–3 days, moderate risk). THE TARGET.** (a) **validate `cv_predictor` across the collapse
  phase diagram** (map the conditioning-strength × N boundary; the theory *forecasts* it); (b) an
  **intervention suite** (exposure-diversity + isolation + novelty-injection + rotating-exposure →
  a taxonomy of what preserves diversity); (c) **real-data grounding** — seed the catalog with *real*
  WS2 abstracts (`ws2-section0`) and ask whether the AI society recapitulates human concentration +
  fragmentation; (d) **scale** for emergent phenomenology. *Deliverable: a real multi-agent-science
  result + a strong theory validation.*
- **SPRINT (reach; only if RUN lands early). The apex + the flourishes.** The closed-loop **"diversity
  thermostat"** (forecast collapse, auto-intervene live) **and** the **autonomous round-the-clock Codex
  harness + full utilization observability** (below) as a *separate* showcase. *Deliverable: the
  north-star.*

**Discipline:** a landed WALK beats a half-built SPRINT; submit the highest rung that *landed*.

## The experiment — endogenous conditioning (the LLM does the collapsing)

**Agents.** N persona-conditioned GPT-5.6 agents (persona = a fixed viewpoint/expertise descriptor,
embedded once). **The collapse is emergent, not imposed:** each round an agent is shown a *sample of
the shared catalog* + its persona + the topic and **proposes a new idea conditioned on what it sees**;
if agents attend to a shared, popularity-weighted catalog, the model itself drifts toward the popular
priors → outputs homogenize over rounds. **Every idea joins the catalog — nothing is culled.**

**Knobs:** `sigma` (fraction of agents drawing from the ONE shared catalog vs a local one), `exposure`
(catalog sample = popularity-weighted / canon-reinforcing vs uniform; + how many items shown),
`isolated_frac` (ι — a subgroup sees a local/no catalog), N, T. Personas fixed.

**The causal test = the catalog-ablation (this is the fix the review demanded).** Run **catalog-in-
prompt ON vs OFF**: if outputs homogenize *with* shared-catalog exposure but *not without*, the collapse
is attributable to **LLM conditioning**, not any exogenous rule. The `sigma`/`exposure` sweep locates
*how much* shared exposure triggers it.

**Baseline comparison (the demoted numpy filter):** the WS3 `channel.py` suppression filter
(`exp(−λ·H·(1−γ))`) as an *imposed-collapse baseline* — contrasts "collapse imposed by a filter" vs
"collapse emergent from conditioning," showing the endogenous effect is real.

**Measured each round — embedding-based, cheap (`diversity_metrics`):** **V** (intellectual) =
semantic diversity of the round's *outputs* (`effective_dimensionality`, `mean_pairwise_cosine_distance`,
`cluster_entropy`); **H** (concentration) = which ideas get echoed (`gini` of catalog cluster
occupancy); **D** (control) = persona-embedding diversity. **Honest framing (fixes the tautology):**
D is fixed by construction, so the finding is *"persona-diverse agents produce collapsing outputs under
shared-catalog conditioning"* — diverse inputs → homogeneous outputs via the actuator — NOT a claim
that we "discovered" a demographic/intellectual decoupling (that is baked in).

**Statistical plan (makes it a result, not an anecdote).** ≥4 seeds/condition; V-vs-round slope with
bootstrap CI over agents×seeds. **Pre-registered refute criteria:** "collapse" = shared-catalog slope
`<0`, CI excludes 0, **AND** the ablation (no-catalog) slope is significantly flatter/≥0; the crossover
= the `sigma`/`exposure` where the slope flips, CI-bracketed; the theory-test = predicted vs observed
crossover (regime-ordering primary).

## Day-0 kill-test (~$0.50 real GPT-5.6, BEFORE building the engine)

Two load-bearing assumptions, tested cheaply first: **(1) diversity** — does Luna at `minimal` effort
with a cached persona prefix produce *diverse* outputs across personas (else the `sigma=0` baseline
evaporates — bump effort / strengthen persona signal)? **(2) conditioning bites** — does showing agents
a homogeneous popular-canon sample measurably *shift* their outputs toward it vs a no-catalog control
(else the endogenous mechanism is dead — rethink now, not on Day 6)? Both pass → build. Either fails →
known Day 0.

## Theory-guided efficiency + the crossover test

`theory.py` (mirrors `canary/theory.py`): map the loop to `SystemParams` (conditioning strength
`sigma·exposure` → `lam`; generation temperature → `epsilon`; persona/catalog signal → `f`), call
`cv_predictor.predict()` (zero tokens) → `lambda_star`. **WALK** runs GPT-5.6 at **3 exposure levels**
bracketing λ* (the "novel job per token" headline); **RUN** extends to the full phase diagram. Use
`predict()` for the regime-ordering gate; the sim (`calibrate()`) for the exact λ*.

## GPT-5.6 in the best light

At `sigma=0` (no shared catalog) GPT-5.6 agents stay **richly diverse** — the kill-test verifies this.
Collapse emerges only when a **shared popularity-weighted catalog** (a *deployment choice*) conditions
them; the intervention (**exposure diversity / insulation**) *leverages GPT-5.6's latent richness* to
sustain diversity. **GPT-5.6 is the cure; the shared actuator is the disease.** Three showcases in the
core: **capability** (a few Sol/`xhigh` calls), **efficiency** (the Luna/`minimal` core proves the same
science for ~$X, on a live token meter), and **the science** itself; the **long-horizon-autonomy**
showcase (Codex building+running it round-the-clock) is the SPRINT flourish.

## Build architecture

New sibling repo `ws1/` (peer of `originality/`, `canary/`), reusing `diversity_metrics` + `cv_predictor`
via editable path deps (canary template). `src/ws1/{persona,agent,catalog,measure,theory,baseline,
dashboard}.py`.

- **`agent.py` (now central — the LLM *is* the mechanism):** GPT-5.6 wrapper; `propose(persona,
  catalog_sample, topic)`; batched; **prompt-caches** the constant persona+topic prefix; short outputs.
  A **deterministic mock** behind the interface for token-free *harness* dev/testing (the *science*
  needs real calls).
- **`catalog.py` (the actuator — exposure, not suppression):** the accumulating idea pool + embeddings;
  the sampler (`sigma` shared-vs-local, popularity-weighted vs uniform, exposure budget, `isolated_frac`).
  Zero culling.
- **`baseline.py`:** the WS3 `channel.py` numpy suppression filter, imported faithfully, as the
  *imposed-collapse* comparison only.
- **`measure.py`:** wraps `diversity_metrics` (V/H/D + the iso-vs-conformist split), embedding-only.
- **`dashboard.py` (the demo IS the experiment):** sliders (`sigma`/`exposure`/`isolated_frac`), a
  catalog-ablation toggle, live **V-collapse vs D-flat** trajectories, and the intervention toggle
  showing V recover. Plus a thin **token/cost meter**.
- **Built by *supervised* Codex** (ordinary use) from a canary-style `CLAUDE.md`; TDD the token-free
  parts (`catalog`, `measure`, `theory`, `baseline`) against WS3 references.

## Token efficiency + budget (GPT-5.6 Sol/Terra/Luna)

**Ladder** (per 1M tok; *confirm Jul 13*): **Sol** $5/$0.50c/$30 · **Terra** $2.50/$0.25/$15 · **Luna**
$1/$0.10/$6. `reasoning_effort` (none…xhigh, default medium) — **reasoning tokens bill at OUTPUT rate**,
the dominant knob. **Task→model→effort:** high-volume `propose` → **Luna / `minimal`** (cached ≥1,024-tok
persona prefix −90%, +Batch −50% if offline); persona seed (once) → Sol/Terra medium/high; showcase (a
few) → Sol high/`xhigh`; embeddings → `text-embedding-3-small` ($0.02/1M). **The science is cheap, not
token-free** (the collapse *is* the LLM behavior): WALK ≈ **$1–3**, RUN ≈ **$20–50**, + the $0.50 kill-test.
A **thin per-turn token ledger** (from the SDK/`--json` `usage`) drives the live meter — the full
Usage/Cost reconciliation is a SPRINT flourish.

**Codex coding sessions** (building the repo — *distinct* from the science calls above; Codex runs on
the same Sol/Terra/Luna tiers, no codex SKU). A **cost-aware coding ladder:** **Terra / `medium`** as
the default (≈GPT-5.5-class coding at half Sol's cost, ample for a canary-sized build); **Sol / `high`**
for genuinely hard or stuck tasks (the `cv_predictor`/WS3 integration, gnarly test debugging); **Luna /
`low`** for mechanical work (scaffolding, boilerplate, formatting, doc updates). Set per session via
`codex exec --model <tier> --config model_reasoning_effort=<effort>` (or the `openai/codex-action`
`model`/`effort` inputs). In the SPRINT autonomous harness, the supervisor picks tier/effort per
milestone difficulty and the budget-guard **degradation ladder** steps Sol/high → Terra/medium →
Luna/low as budget depletes.

## Post-WALK flourishes (SPRINT only — off the critical path)

Build these *after* the causal result is banked; the science never depends on them.
- **Autonomous round-the-clock Codex harness** (your long-horizon-autonomy push): drive via the Codex
  SDK (`Turn.usage`) / `codex exec --json` in a disposable container (`--sandbox workspace-write
  --ask-for-approval never`), **API-key auth (hard cap)**, OpenAI's `Prompt/Plan/Implement/
  Documentation.md` durable-memory pattern, `codex exec resume` checkpointing, a **harness budget ledger
  stopping at ~80–90%** (primary — don't rely on the new `rollout_budget`), a degradation ladder, and an
  org monthly-cap backstop.
- **Full observability:** session harvest of `$CODEX_HOME/sessions` `token_count`, `notify`/`[hooks]`
  taps, Admin **Usage + Cost APIs**; the **novel-job-per-token** metric (scientific yield ÷ tokens,
  across theory-guided × model-tier × autonomous-orchestration).
- **The diversity thermostat:** `cv_predictor` + `diversity_metrics` in a closed loop that detects an
  approaching collapse live and auto-triggers interventions — theory → prediction → *control*.

## Hackathon-week execution (rules-adaptive; wait for Jul 13)

1. **Jul 13 (rules drop):** read tracks/prizes/credits; pick the domain skin + aim-point.
2. **Jul 13 — Day-0 kill-test** (~$0.50): verify diversity + conditioning-bites before building.
3. **Jul 13–15 — CRAWL:** supervised Codex scaffolds `ws1/`; TDD the token-free engine + mock-agent
   dashboard + thin token ledger; pre-register the λ* predictions + the refute criteria.
4. **Jul 15–17 — WALK (bank the floor):** real GPT-5.6 (Luna/`minimal`); the endogenous causal result +
   catalog-ablation + insulation, with seeds + CIs; a few Sol/`xhigh` showcase calls. *Commit as a
   complete deliverable.*
5. **Jul 17–20 — RUN, then SPRINT if landing early:** phase-diagram validation + intervention suite +
   real-data grounding + scale (RUN); the thermostat + the autonomous-Codex-harness/observability
   showcase (SPRINT).
6. **Jul 21 (5pm PT):** submit the highest rung that *landed* — the live dashboard, the utilization/
   efficiency report, and a short writeup (endogenous collapse + the ablation; "GPT-5.6 is the cure";
   theory-guided efficiency; the cross-domain program tie-in).

## Risks + mitigations

- **Mechanism is real, not definitional** → the **catalog-ablation** is the core test; the Day-0
  kill-test verifies conditioning bites before we build; the numpy filter is only a labeled baseline.
- **`minimal`-effort outputs might be samey** → Day-0 kill-test catches it; fallback = higher effort /
  stronger persona signal / `low`.
- **Result vs anecdote** → the pre-registered statistical plan (seeds, CIs, refute criteria).
- **Over-scope in 8 days** → the ladder banks WALK first; **autonomy + observability + thermostat are
  SPRINT-only, off the critical path** — if finicky, drop to supervised Codex + `ccusage` and the
  science + demo still land.
- **Portfolio vs sponsor (cross-backbone)** → the catalog-conditioning design is all-GPT-5.6 and
  on-message *and* clean (the manipulation is catalog exposure, so "shared backbone → shared priors"
  is not the confound); the scientifically-stronger cross-model-family version is a **post-hackathon
  extension**, noted honestly, not engineered away.
- **Unverified specs (confirm Jul 13)** → model names/prices, a `max` effort value, `text-embedding-4`,
  cache×Batch stacking, `rollout_budget` enforcement. The ledger reads *actual* `usage`; the API-key
  org cap is the backstop.

## Ready to leverage (no work now; pointers for Jul 13)

- Repo/deps template: `canary/pyproject.toml`, `canary/src/canary/{measure,theory}.py`.
- The exposure↔conditioning mapping + the imposed-filter baseline: `originality/whitespace_3/src/
  whitespace3/channel.py` (`κ_eff=λ·H·(1−γ)`, `suppression`, `isolated_frac`).
- The predictor contract: `originality/packages/cv_predictor/src/cv_predictor/predictor.py`.
- V/H metrics: `originality/packages/diversity_metrics/src/diversity_metrics/{semantic,concentration}.py`.
- Real seed abstracts: Modal Volume `ws2-section0`, `section0-population-v3.parquet` (RUN(c)).
- SPRINT-flourish pointers: `codex exec --json` / Codex SDK `Turn.usage`; `Prompt/Plan/Implement/
  Documentation.md`; `$CODEX_HOME/sessions` `token_count`; Admin Usage + Cost APIs; `ccusage codex`.

## Verification

**Engine (token-free):** unit-test `catalog.py` (sampler weighting, `sigma`/`isolated_frac`), `measure.py`
(V/H/D on random embeddings, mirror canary), `theory.py` (`predict()` λ* + 3 bracketing levels),
`baseline.py` (matches a WS3 `channel.run` reference); the mock-agent dashboard runs the full loop +
intervention toggle. **Science (cheap, empirical):** the Day-0 kill-test gates the build; the WALK result
is judged against the **pre-registered refute criteria** (shared-catalog slope `<0` CI-excluding-0 AND a
flatter ablation), not asserted. Only after the kill-test passes do we run the full engine on real GPT-5.6.
