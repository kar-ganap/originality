# WS1 — OSS / cross-model arm: the two-layer adjudication study (design note)

**Status:** **v2, rewritten 2026-07-21.** Supersedes the 2026-07-14 v1, whose premise — *Polyphony
establishes output collapse, this arm adds the reasoning layer* — was **inverted by Polyphony's
result**. Polyphony refuted output collapse across six pre-registered experiments, so this arm's job
changes from *additive* to *adjudicative*. Not yet pre-registered; not yet scoped for spend.

**Firewall.** Private program science. Polyphony is **public**
(`github.com/kar-ganap/polyphony`) and is freely citable. WS2, WS3, and canary are unpublished —
their internals never leave this repo, and nothing here goes into a public repo without a firewall
pass.

---

## 1. What changed

Two sibling results landed after v1 was written, and both bear directly on this design.

**Polyphony (WS1 ch.1, complete + public).** Across six pre-registered experiments, endogenous
homogenization did **not** bite in role-diverse GPT-5.6 ensembles. R4 is the cleanest read: catalog
uptake was real (+0.0530, lower bound +0.0268) and popularity feedback genuinely made context recur
(+0.0102 top-four echo-concentration, lower bound +0.0055) — yet output diversity **rose** (V slope
+0.0090, upper bound +0.0158). The obvious artifact (a fixed-persona floor masking a decline) was
tested and rejected: the de-persona contrast projection left the slope positive (+0.0105). Visible
consensus (R5) turned out text-focal, not count-driven. Off-task context (R7A) harmed only
task-conditionally. The one real effect was **version-conflict contamination** (R7C-A: superseded
context → deprecated-constraint adoption 40/40 vs 0/40 empty), which failed its cross-task rule.

Two consequences. First, there is no established output collapse for a reasoning layer to be *added
to* — so the arm must adjudicate rather than extend. Second, R4 **reproduced WS2's decoupling
signature** on an AI substrate (concentration↑ *and* diversity↑ simultaneously, mechanism confirmed
live in between), which is why this arm also carries Paper 1's cross-substrate capstone.

**Canary (AI recursion arm, closed).** Its honest landing: recursive self-training collapses
diversity robustly (H1), couples concentration with diversity-loss as a *partial echo* (H4), but its
C/V theory test is an **honest null** — an identifiability failure, not a disconfirmation. Three
lessons transfer here and are baked into §4–§6 below:

- **You cannot study a transition from inside one phase.** Canary sat deep in the collapse phase
  everywhere except κ=0; Polyphony sat deep in the sustain phase throughout. The program has now
  bracketed the transition **from both sides without ever straddling it**.
- **Probe reachability before running the expensive test at an unknown location.** Canary spent
  ~$100 on a fidelity test at the floor, where it could not resolve, instead of ~$20 first checking
  whether the floor could be moved.
- **A slope-only estimand hides level effects.** This one is now three-for-three (Polyphony R6,
  canary's classifier v1, and v1 of *this* note) and is fixed in §6.

---

## 2. The question

> **Is Polyphony's output-null a fact about the system, or an artifact of measuring only the layer
> that talks?**

Output-only diversity compresses away the reasoning: two agents that reason completely differently
to the *same* stated conclusion read as identical. Proprietary models hide or summarize the trace;
open reasoning models and Claude's extended thinking expose it. That is this arm's independent
reason to exist.

Measure two layers per round — **`V_output`** (embedding diversity of final answers) and
**`V_reason`** (diversity of reasoning *strategies*, §5) — and read the joint trajectory:

| | reasoning diverse | reasoning collapsed |
|---|---|---|
| **outputs diverse** | no collapse — Polyphony's null **deepens** into a robust finding | **the live cell:** convergent thinking in varied phrasing — *invisible to output metrics* |
| **outputs collapsed** | surface monoculture; one answer, many paths (arguably healthy consensus) | deep collapse |

v1 spread effort across all four cells. Polyphony's result collapses this to **one live cell** — the
top-right — so power the study for that one. Both outcomes pay: if `V_reason` declines while
`V_output` holds, the headline null is a measurement artifact and homogenization is real but
invisible; if `V_reason` also holds, the null deepens — resilience is not surface-level.

---

## 3. Why this arm is now the program's theory test

WS3's C/V model is a theory of **conformity** — copy versus innovate. Canary could reach conformity
only through the κ→λ identity (data-mixture fraction ≟ behavioural conformity weight), which its own
design doc distrusted, and which is the root of its identifiability failure.

**In a multi-agent ensemble, λ is not a mapping — it is a knob.** The copy-vs-innovate weight is
directly settable, ε (innovation) is temperature or an explicit innovate-instruction, and neither
requires an unknown monotone *g*. That makes this arm the **native** substrate for the theory, and
the only venue in the program that can give WS3 a **causal** test: you cannot manipulate λ in a
scientific field, so the human data is structurally observational. WS3 currently has theory +
simulation + an observational bridge; this would be its first experimental anchor.

So the `cv_predictor` λ\* hook — marked *"speculative, a stretch goal, not load-bearing"* in v1 — is
**promoted to primary** (§4 rung 3).

**Imposed λ vs endogenous λ — run both; the gap is the finding.** An explicitly instructed
copy-probability is *imposed*, which violates the endogeneity discipline Polyphony was built around
(collapse must emerge from conditioning, not from a rule). The resolution is that the two arms
answer different questions and both are needed:

- **Imposed-λ** is a legitimate — indeed necessary — *calibration ruler*. It locates λ\* empirically
  and tests the theory's shift predictions. It makes no mechanism claim.
- **Endogenous-λ** (shared catalog, popularity weighting — Polyphony's actuator) asks whether
  realistic deployment conditions *reach* that λ\*.

Their difference converts Polyphony's bare null into a **quantitative** statement: *the crossover
sits at λ\*≈X; endogenous shared-context conditioning reaches only λ_eff≈Y < X, which is why no
collapse appeared.* That is a far stronger result than "we failed to induce collapse," and it is the
cleanest thing this arm can produce for Paper 2.

---

## 4. The build ladder — each rung gates the next

Ordered deliberately: the cheap, decisive checks come first. This is canary's lesson applied.

**Rung 0 — reachability probe (cheap; run first; both outcomes publishable).**
Under an imposed-λ knob at maximum, **can `V_output` be driven down at all in a *role-diverse*
ensemble?** This is the multi-agent analog of canary's rank-probe, and it addresses the symmetric
risk: just as canary could never leave the collapse phase, this substrate may have **no accessible
collapse phase**, which is what Polyphony's six nulls suggest.

**The trivial-corner trap — the reason this rung needs guards.** Polyphony's R6 already ran the
naive version and it is *not* informative. With **homogeneous** personas and a dominant feed, V fell
0.158 → 0.032 on one topic (−80%) — but `anchor_alignment` rose 0.576 → **0.843** and the artifacts
are near-verbatim restatements of the shown item. That is parroting with diversity zeroed by
construction, not conformity dynamics. In the **role-diverse** regime the *same* actuator produced
**+0.0029** and **+0.0111** — V moved the *wrong way*. So an actuator instructed to "extend the shown
item" would pass this rung on a tautology and green-light the whole ladder falsely. Three guards are
therefore mandatory: **personas held at the diverse setting and verified unchanged**, an
**anchor-alignment ceiling** so a decline is not restatement, and the effect required in **≥2 task
families** (every single-task result in this program has failed to generalize — R6 flipped sign by
topic, R7A was task-conditional, R7C-A was 1-of-6).

**Two actuator forms, run as a contrast** (locked 2026-07-21) — this separates actuator *form* from
*strength*, and a null in both is a far stronger floor result than a null in one:
  - **instruction-λ** — a graded "align with the leading approaches shown" directive. Closest to
    WS3's conformity weight; agents still produce their own text.
  - **payoff-λ** — agents see which prior proposals were "adopted" and are told adoption is the
    goal. Preferential attachment made explicit with a payoff.
  - shared **ablation** control (no catalog, matched prompt/format).

Outcomes: *reachable in either form* → a bracket exists, proceed to rung 1, noting any form
dependence. *Not reachable in either* → **stop and report.** "Role-diverse in-context ensembles have
no accessible collapse phase even under imposed maximal conformity, in two independent actuator
forms" is a strong boundary-conditions result with a measured floor, and it retires the rest of the
ladder honestly.

**Rung 1 — Arm 0: bridge replication (mandatory before any reasoning claim).**
Replicate Polyphony's **output-layer null** on the OSS/Claude substrate, endogenous actuator,
`V_output` only, catalog-of-conclusions. Without this, a later `V_reason` signal cannot be
attributed to the reasoning layer rather than to the fact that the arm changed model family, output
length, and reasoning effort all at once — Polyphony ran GPT-5.6 at effort `none` with 120-token
caps. Arm 0 is the control that makes the rest interpretable.

**Rung 2 — the two-layer adjudication (the arm's centerpiece).**
Add `V_reason`. Contrast **catalog-of-conclusions** (agents see others' answers) against
**catalog-of-reasoning** (agents see others' traces). This contrast is now the *key manipulation*,
not a side knob: Polyphony only ever shared conclusions, so "does reasoning-exposure homogenize
reasoning?" is the genuinely untested actuator — and the one a proprietary API structurally cannot
run. Pre-register that reasoning-collapse may be weak or absent under catalog-of-conclusions; that
is an informative null.

**Rung 3 — λ\* straddling (the theory test).**
A fine imposed-λ grid **bracketing** the rung-0 boundary, with the distinctive C/V predictions as
primary: **∂λ\*/∂fidelity** and **∂λ\*/∂innovation**. Shift *directions* survive an unknown monotone
transform, which is why they — not λ\*'s location — are the tests. Two hard requirements inherited
from canary:
  - **Wire the WS3 ABM** (`whitespace3.conformity.locate_lambda_star`). ε is a literal no-op in the
    mean-field `predict()`, so the innovation test is unrunnable without it, and `cv_predictor.
    calibrate()` is a documented stub.
  - **Know which side of f=0.15 you are on** — the mean-field ∂λ\*/∂f *flips sign* below it, so the
    predicted direction is not stable across fidelity space. State the operating point before
    running.
  Then measure λ_eff for the endogenous actuator and report the imposed-vs-endogenous gap (§3).

**Rung 4 — cross-model panel (conditional; do not build first).**
Demoted from v1. Its original job was killing the shared-weights confound — "same-model convergence
might not be conditioning." **A null has no convergence to explain, so there is no confound to
kill.** Build the harness model-agnostic from day one, but run the panel only if the reasoning layer
bites. `V_reason` stays **within-model longitudinal** regardless; CoT formats are not comparable
across families, so cross-model comparison lives at `V_output`.

---

## 5. Measurement

**`V_output`.** Primary metric = **mean pairwise cosine distance**, with ≥2 embedding families.
**Do not use participation-ratio effective dimensionality as the primary.** Canary's v9 catch,
verified: it is `(Σλ)²/Σλ²`, exactly **scale-invariant** — scale every embedding by *c* and it is
unchanged — so it measures the *shape* of residual variance and is structurally **blind to uniform
contraction toward a point**, which is what collapse is. In canary's pilot it went 63→32→76, ending
*higher*, while every magnitude-aware metric fell cleanly. Report it as a secondary; never gate on
it.

**`V_reason`.** **Do not embed raw traces** — length, verbosity, and format dominate the geometry,
and long traces average out, understating diversity. Instead extract a **reasoning skeleton** per
trace (the ordered sub-claims, or the approach taken) and measure diversity over skeletons
(embedding, edit-distance, or cluster→entropy). Extraction via a cheap parse or a small extraction
model — a judge for *extraction*, not for scoring. Requirements: control for trace length; report
**≥2 skeleton granularities** and **≥2 extraction procedures** (the WS2 ≥2-embedding-family
discipline, applied to reasoning); and verify that the extractor does not itself homogenize (run it
on deliberately diverse traces and confirm the skeletons stay diverse).

**Concentration.** Carry the H-axis alongside V so this arm can speak to the decoupling: a
**reference-anchored** concentration measure (partition fit once on a fixed reference set), not a
per-round refit. Canary's v9 showed per-round k-means Gini is confounded — it reads noise once the
signal vanishes.

---

## 6. Estimands and gates — the part v1 got wrong

v1's refute criteria read: *"shared-catalog slope < 0, CI excludes 0, AND no-catalog slope
flatter/≥0."* **That is slope-only, and it is the same defect three times over** — it is what hid a
−0.127 level shift under a +0.0033 slope in Polyphony R6, and what canary had to fix. Replace it
with canary's frozen classifier, which is already validated code:

- **Level and slope are BOTH primary, applied symmetrically.**
- **collapse** if EITHER (a) OLS slope < 0 with **one-sided** permutation p<.05 (*progressive*), OR
  (b) cumulative decline ≥ a pre-registered cut / changepoint-detected level drop (*acute*).
- **sustain** requires BOTH a flat slope (**TOST** with a *t*-quantile, not z) AND cumulative
  decline within the flat margin. A failure-to-reject is **not** an equivalence claim.
- **ambiguous** otherwise → grid refinement, never a silent sustain.
- **acute vs progressive are distinct pre-registered labels** (early changepoint **plus** a plateau
  clause), never merged — they read differently against λ\*, since an acute drop to a stable floor
  is a lower fixed point, not runaway decline.
- **flat margin calibrated from the no-catalog control**, not guessed. Register every constant; do
  not add a floor or a certification branch post-freeze without a dated change-log entry.

**Corroboration.** Require multiple substrates to agree before a collapse call, but note canary's
N1 finding: an unthresholded first→last sign test across 4 substrates fires ~31% of the time under
noise, and it *did* fire 3/4 on one of canary's negative controls. Either threshold the substrate
checks or make them control-referenced.

**Power — decide before spending.** Canary's pre-registered `p<.05` gate was **arithmetically
unreachable** at its planned n (minimum one-sided Wilcoxon p is 0.0625 at n=4). **Use n≥5 seeds per
cell**, or pre-register a gate that the design can actually reach. Run this arithmetic *before*
launch, not in the retro.

**Observation windows must be equal across compared conditions.** Canary's Study A compared 8-round
arms against 4-round arms, which inflated its effect by ~2× and was only caught in audit. If any run
is truncated, report the matched-window sensitivity alongside the full result.

---

## 7. The faithfulness caveat — scoped, not fatal

Stated CoT is not guaranteed faithful to the model's computation. This is a framing discipline, not
a measurement problem, for three reasons:

1. **Articulated reasoning is the causally-operative layer for *collective* homogenization.** The
   dynamic propagates through what is *shared*. Un-articulated cognition is causally inert for the
   collective — it cannot homogenize anyone. For the collective-diversity question, articulated
   reasoning is not a lossy proxy; it *is* the operative layer.
2. **It is symmetric with the human arm, which tightens the bridge.** WS2/WS3 measure diversity of
   human *articulated* outputs — papers, abstracts, citations — never cognition. And human
   articulated reasoning is itself imperfectly faithful (confabulation, post-hoc rationalization:
   Nisbett–Wilson, Haidt). Using articulated reasoning on both sides makes the human↔AI comparison
   *more* apples-to-apples, not less.
3. **The discipline:** claim *"diversity of articulated reasoning,"* never *"diversity of
   cognition."* Faithfulness only bites if you slide from the former to the latter.

**Residual AI-specific wrinkle (the one genuine asymmetry):** RL can make CoT decorative
(reward-hacked), plausibly more so than human articulation, which carries some social and
professional accountability. Note it; the catalog-of-reasoning contrast plus skeleton extraction
partly guard against pure decoration — decorative traces should show low *strategy* diversity even
when surface-diverse.

---

## 8. Substrate and harness

**Models.** Open reasoning models with native long CoT (a DeepSeek-R1-class model, a Qwen-QwQ-class
model) plus **Claude as a first-class backend** — extended thinking exposes the trace, which is
decisive for `V_reason` and better than any API that hides it. Natural panel for rung 4: GPT-5.6 +
Claude + ≥1 OSS reasoning model. Served on Modal (vLLM) or a per-token inference API
(Together/Fireworks/DeepInfra).

**Harness — correction to v1.** v1 assumed this arm "reuses Polyphony's provider-agnostic
`LLMClient` harness… so this is a drop-in." **That harness does not exist.** Polyphony has
`_make_openai_client()` — a private helper returning a bare `OpenAI()` with no `base_url`, imported
across ~6 modules. Concretely:
  - OSS endpoints are OpenAI-compatible → a small `base_url` parameterization suffices.
  - **Claude needs a separate client path**, including extended-thinking trace retrieval.
  - Budget this as real (if modest) work, not as free reuse.

Everything else in Polyphony worth reusing is public and citable: the metric battery, the
persona/catalog machinery, and the token-free test discipline.

---

## 9. Pre-registration (rung 0 locked 2026-07-21; rungs 1–4 stubbed)

### 9.1 The measurement scale (calibrated from Polyphony, not guessed)

R6's level reanalysis gives the scale this arm operates on, so every margin below is anchored to
observed data rather than intuition:

| quantity | value | source |
|---|---|---|
| `V_output` ceiling, role-diverse free generation | **≈ 0.42** | R6 diverse ablation (0.4310 / 0.4076) |
| `V_output` floor, total copying (`imposed_copy_floor`) | **≈ 0.00** | R6, all blocks |
| bootstrap CI half-width, 2 blocks/topic | **0.003 – 0.013** | R6 level reanalysis |
| strongest actuator tried, role-diverse effect | **+0.0029 / +0.0111** (wrong way) | R6 diverse level effect |
| parroting signature | `anchor_alignment` **0.58 → 0.84** | R6 homogeneous topic-b |
| role-diverse alignment shift (non-parroting) | **+0.014 to +0.050** | R6 diverse |

Because V's floor is 0, any effect can be read as a fraction of the distance to total copying.

### 9.2 Rung-0 gate (LOCKED)

**Design.** 3 task families × 3 cells (**instruction-λ=1**, **payoff-λ=1**, shared **ablation**) × 5
**distinct** roles × **6 blocks**. Single round; the question is acute reachability, not dynamics.

**Passes iff all four hold:**
1. **Margin** — `V_output` declines **≥20%** vs matched ablation (0.42 → ≤0.336, Δ ≈ −0.084).
2. **Generality** — in **≥2 of 3** task families.
3. **Significance** — one-sided sign/Wilcoxon **p<.05** at n=6.
4. **Guards** — `anchor_alignment` stays **below a ceiling pre-registered from the R6 scale** (the
   diverse baseline is 0.34–0.51; parroting is 0.84 — set the ceiling at **0.65**), **and** measured
   persona diversity D is statistically unchanged from ablation.

**The arithmetic, checked in advance** (canary's gate was arithmetically unreachable and nobody
noticed until audit): Δ = −0.084 against a CI half-width of 0.003–0.013 is **7–28× headroom**, so
detection is not the constraint. Minimum one-sided Wilcoxon p is 0.031 at n=5 and **0.016 at n=6**,
so the p<.05 branch **is reachable** at the planned n. Power is not binding here; **actuator strength
is** — the gate demands ~8× the magnitude, and the opposite sign, of anything Polyphony achieved.

### 9.3 The actuator floor — derived from rung 0, not guessed

Polyphony's endogenous actuator reached **+0.0102** concentration and produced no collapse, but that
null is uninterpretable because *no one knew what concentration collapse requires*. Rung 0 supplies
the missing denominator: let **H\*** be the concentration observed at the imposed-λ collapse point.
Pre-commit the reading of the endogenous arm:

| endogenous H reached | if no collapse, this means |
|---|---|
| **≥ H\*** | **Strong resilience.** The actuator reached the level that collapses an imposed system and nothing happened. A headline result. |
| **0.5·H\* – H\*** | **Bounded resilience.** Report as "reached X% of the collapse concentration without collapse." Informative, not decisive. |
| **< 0.5·H\*** | **Actuator-limited — NOT evidence of resilience.** Report the ceiling; do not claim the system resists. This is the box Polyphony's null sits in. |

This converts the arm's central null into a quantitative statement and is the single biggest
interpretive upgrade over Polyphony.

### 9.4 Honest-null table (pre-committed; write the meaning before the result)

| gate | fails → this is what it means | action |
|---|---|---|
| **Rung 0**, both actuator forms | Role-diverse in-context ensembles have **no accessible collapse phase** under imposed maximal conformity. A measured floor, not an absence of evidence. | **Stop.** Publish as Paper 2's boundary-conditions result. Ladder ends honestly. |
| **Rung 0**, one form only | Reachability is **actuator-form-dependent** — a finding about *what kind* of pressure homogenizes, not whether. | Proceed with the working form; report the dependence prominently. |
| **Rung 1** (Arm 0) — the output-null does **not** replicate | Polyphony's null is **substrate-specific**, not general. Major finding, and it *redirects* the arm. | **Do not proceed to rung 2 as planned.** The question becomes why this substrate collapses where GPT-5.6 did not. |
| **Rung 2** — `V_reason` holds with `V_output` | The null **deepens**: resilience is not surface-level. | Headline result. Report as strengthening, not as a failure to find. |
| **Rung 2** — `V_reason` collapses, `V_output` holds | Polyphony's headline null is a **measurement artifact**; homogenization is real but invisible to output metrics. | Headline result — the arm's reason to exist. |
| **Rung 2** — reasoning collapses only under catalog-of-reasoning | Reasoning-collapse **requires reasoning-exposure**. Mechanism finding. | Report; it bounds the deployment risk to trace-sharing systems. |
| **Rung 3** — shift directions absent/wrong | The C/V conformity mechanism **does not transfer** to LLM ensembles. The bridge-calibration null. | Report. Per canary's reporting spine, a null here costs a *section*, not the paper. |
| **Rung 3** — ABM unavailable or ε untestable | The theory test is **not runnable**, not "passed by other means." | **Report as unrun.** Do NOT substitute a degenerate regime-ordering test — that is exactly canary's H3a failure. |

**Meta-rule — no gate substitution.** If a pre-registered gate fails, report the failure. Do not
promote a different statistic to "the gate," and do not demote the failed one to a "sanity check."
Every constant is registered here or in a dated change-log entry; none is introduced post-freeze.

### 9.5 Cost ladder

Rung 0 is priced from Polyphony actuals (960 calls inside a ~$3–4 total). Rungs 1–3 are dominated by
**reasoning tokens, which bill at output rate** — the single largest uncertainty, since a long-CoT
model may emit 1k–10k thinking tokens per response.

| rung | scale | estimate |
|---|---|---|
| **0** reachability | 3 families × 3 cells × 5 agents × 6 blocks ≈ 270 calls, short outputs | **< $10** |
| **1** Arm 0 bridge | 3 × 2 × 5 × 8 rounds × 6 seeds ≈ 1,440 calls, long CoT | **$40–80** |
| **2** two-layer | ≈ 2,880 calls + skeleton extraction (~5,760 cheap calls) | **$100–150** |
| **3** λ\* straddling | fine λ grid × fidelity/innovation arms ≈ 9k–13k calls + ABM compute | **$300–500** |
| **4** cross-model | conditional; rung 2 × panel size | **$200–300** |

**Rung 0 doubles as the cost calibration.** It must log actual tokens/call so rungs 1–3 are costed
from measurement, not estimate — canary's ledger ran ~$65 low against a hard cap and cost it two
arms. **No rung launches without a re-costed estimate from the prior rung's telemetry.**

### 9.6 Standing commitments (all rungs)

- **Metrics:** `V_output` (mean pairwise cosine, ≥2 embedding families — **never** eff-dim as primary,
  §5) + `V_reason` (≥2 skeleton extractions × ≥2 granularities) + reference-anchored concentration.
- **Primary:** the joint `(V_output, V_reason)` trajectory and the **which-collapses-first** ordering,
  classified by the §6 level+slope co-primary — never a bare slope.
- **n≥6** per cell; equal observation windows across compared conditions; if any run is truncated,
  report the matched-window sensitivity alongside the full result.
- **Report regime/sign over magnitude** — the short-output magnitude-inflation caution carries over.

---

## 10. Portfolio relevance

Reasoning-diversity collapse in multi-agent systems is squarely what frontier reasoning/RL teams
think about: RLHF/RLVR mode collapse is documented for *outputs*; the *reasoning* layer is
under-studied. Connects to self-consistency (reasoning-path diversity as an already-valued
construct) and algorithmic-monoculture concerns. The framing — **"does the *thinking* collapse, or
only the *talking*?"** — is novel and legible. Claude as a backend also makes the arm
Anthropic-facing.

## 11. What this arm cannot do

- It cannot establish that **weight-level** collapse and **in-context** homogenization share a
  mechanism. That contrast is canary-vs-Polyphony, and it is qualitative — the conditioning
  strengths were never matched.
- It cannot validate C/V's crossover *location* (that does not survive the units question); only
  **shift directions** do.
- A rung-0 failure ends the ladder. That is a real possibility given Polyphony's six nulls, and the
  design must be willing to report it as the result rather than escalate until something moves.
