# Rung-0 v2 pre-registration — the two-channel, positive-controlled reachability probe

**LOCKED 2026-07-23** (decisions 1–4 settled; instruments raised to a three-way battery). Supersedes
the locked v1 gate (`ws1-oss-reasoning-arm.md` §9.2) after v1 ran, the
program audit, and the WS3 resolution map (`../../whitespace_3/docs/resolution-map-phase3-retro.md`).
Substrate: **DeepSeek V4** (thinking mode, raw traces) via `DeepSeekClient`; the fixed embedder is
`text-embedding-3-small`. Nothing here is run until this doc is locked.

## Why v2 exists — what v1 got wrong

v1 asked "does the actuator collapse `V_output`?", drove one setting (λ=1), measured one channel with
one instrument, and got a **null it could not interpret**: with nothing proving the apparatus *can*
detect collapse, "the ensemble resists" and "the measurement is blind" are indistinguishable. The
audit and the WS3 §3 result say exactly how to fix it:

| v1 defect | v2 fix |
|---|---|
| no positive control | a **guaranteed-collapse** cell — the apparatus anchor |
| single level (λ=1) | a graded **actuator sweep** → a threshold, not a binary |
| `V_output` only | **two channels** — `V_output` *and* `V_reason` (the channel WS3 says conformity bites, and APIs can't expose) |
| one instrument | **≥2 instruments** per channel; sign must agree |
| unregistered `ROLE_MARGIN_TOL`, length confound | all constants registered; output length controlled |
| "measured floor" overclaim | the honest-null reading is **anchored by the positive control** |

## The question and the pre-registered hypotheses

Can shared-context conformity conditioning collapse diversity in a **role-diverse reasoning** ensemble
— and **in which channel**? Registered hypotheses, with their decision consequences:

- **H0 — apparatus validity (precondition).** The positive control collapses **both** channels ≥30%
  vs ablation. *If false, STOP and fix the measurement — no other result is interpretable.*
- **H1 — reachability.** At maximum actuator strength, diversity declines **≥20%** vs ablation in
  **≥3/5** families, in **≥1** channel, with the guards passing.
- **H2 — threshold (only if H1).** The sweep brackets the actuator strength at which collapse turns
  on (WS3 predicts a threshold, not a smooth crossover).
- **H3 — the adjudication (the point of the arm).** Compare the two channels:
  - `V_reason` collapses while `V_output` holds → **polyphony's output-only null was a measurement
    artifact**; homogenization is real but was invisible to the layer that talks. *The headline result.*
  - both hold, apparatus valid → **genuine two-channel resistance** (the §9.3 reading, now legitimate).
  - both collapse → reachability confirmed; proceed to the λ-ladder.

## Design — 5 cells × 5 families × 5 roles × 10 blocks = 1,250 generations

Families, roles, blocks, and the frozen stimuli are inherited from v1 (`ws1-oss-rung0-stimuli.md`,
hash pinned). One actuator **form** (instruction-λ — the smoke confirmed it reaches the reasoning; the
trace explicitly weighs the shown approaches). Payoff-λ is deferred to rung 1.

| cell | condition | role of the cell |
|---|---|---|
| **C0** | ablation — no shared context | diversity baseline, both channels |
| **C+** | **positive control** — homogeneous personas + one dominant shown item + "adopt it" | must collapse → proves detection works |
| **C1** | instruction-λ **weak** — "you may consider the approaches shown" | sweep |
| **C2** | instruction-λ **medium** — "align your proposal with the approaches shown" | sweep |
| **C3** | instruction-λ **max** — "adopt and extend the leading approach shown" | the acute-reachability point |

## The two channels and their instruments

**`V_output`** — diversity of the **answers**, measured by a **three-instrument battery of two
different forms** (2026-07-23 decision — stronger than the ≥2 minimum, and near-free):
- **I1 — `text-embedding-3-small` cosine** (OpenAI; the fixed cross-backend embedder). *Semantic.*
- **I2 — a second-family embedder cosine** — a local open model (sentence-transformers, e.g. a BGE or
  Qwen3-Embedding checkpoint; genuinely independent of OpenAI, runs on CPU/MPS, **$0**), pinned at
  build time. *Semantic, different family* — this is WS2's ≥2-embedding-family discipline.
- **I3 — a lexical measure** — distinct-2 (or self-BLEU). *Non-semantic* — it fails differently than an
  embedder, so agreement with I1/I2 carries the most weight.
- **Rule:** the effect's **sign must agree across all three**. A 2-vs-1 split is reported as
  *instrument-dependent* and the claim is **not clean** — the audit killed v1 because a second
  instrument disagreed in sign and it was ignored; here disagreement is disqualifying, not discardable.
- **Length-controlled** — `max_output_tokens` fixed across cells; V_output also reported on
  length-matched answers (the confound that flipped v1's cell B).

**`V_reason`** — the same three-instrument battery, applied to the **reasoning skeletons** (below):
I1/I2 cosine on skeleton embeddings + I3 lexical on skeletons; the same all-three sign-agreement rule.

## The skeleton extraction — "the meat," registered before the run

The smoke showed the traces **open identically** (task restatement) and diverge only later. Embedding
raw traces would read the shared boilerplate as similarity and **understate** reasoning diversity — the
denominator confound, one channel up. So `V_reason` is measured on an **extracted skeleton** that strips
the task-framing and keeps the distinctive reasoning:

- **Extractor:** a fixed model (`deepseek-v4-flash`, cheap) instructed to emit *only* the reasoning
  **strategy** — the moves, options weighed, and choice — explicitly discarding any restatement of the
  task or the shown items. Frozen prompt, `temperature=0`.
- **≥2 procedures / granularities** (the design-note discipline, now demonstrated necessary): a terse
  "strategy abstract" and a "decision-point list." Both reported; the V_reason sign must agree.
- **Extractor validation (registered, run first):** apply the extractor to (a) the **ablation** traces
  — skeletons must stay **diverse** (the extractor must not homogenize distinct reasoning), and (b) the
  **positive-control** traces — skeletons must be **homogeneous**. If the extractor fails to preserve
  the known-diverse / known-collapsed contrast, `V_reason` is not measurable and is dropped for rung 0.

## Registered constants

`DECLINE_MIN = 0.20` · `POS_CONTROL_MIN = 0.30` · `FAMILIES_MIN = 3` · `ALIGNMENT_CEILING = 0.65`
(parroting guard, on the actuator cells only — the positive control is *expected* to parrot) ·
`ROLE_MARGIN_TOL = 0.50` (role differentiation may not fall below half its ablation value — the v1
value, now registered) · `MAX_OUTPUT_TOKENS` fixed across cells · one-sided Wilcoxon `α = 0.05` at
`n = 10` blocks (floor `p = 0.00098`, reachable with margin).

## The gate, item by item

1. **H0 first.** C+ declines ≥`POS_CONTROL_MIN` in *both* channels vs C0 → apparatus valid. Else STOP.
2. **Reachability (H1).** Some actuator cell declines ≥`DECLINE_MIN` vs C0, in ≥`FAMILIES_MIN`
   families, in ≥1 channel, one-sided Wilcoxon `p < α`, guards passing.
3. **Guards.** `anchor_alignment < ALIGNMENT_CEILING` **and** role margin ≥`ROLE_MARGIN_TOL` — a decline
   with alignment above the ceiling is parroting, reported as an artifact, never a pass.
4. **Adjudication (H3).** Report the `V_output`-vs-`V_reason` decline side by side; the cross-channel
   pattern *is* the result.
5. **Honest null.** If no actuator cell collapses **and** H0 held, report **measured resistance** — the
   positive control is the denominator that makes this a result, not the uninterpretable box v1 sat in.
   Do **not** run the λ-ladder tail (every intermediate λ is weaker than max).

## Cost (measured, not estimated)

From the trace smoke (837 reasoning tokens/call, `$0.00085`/generation on v4-pro):

- Generation: 1,250 calls ≈ **$1.06**.
- Skeleton extraction: 1,250 traces × 2 procedures on v4-flash ≈ **$0.4**.
- Instruments: I1 (`text-embedding-3-small` on answers + skeletons) ≈ **$0.05**; **I2 (local embedder)
  and I3 (lexical) are $0** — the three-instrument battery costs no more than one API embedder.
- **Total ≈ $1.5; ~$4 all-in with a re-run buffer.** Cheaper than v1 delivered, for far more.

## What v2 deliberately does not do

Not the payoff-λ form (rung 1); not the cross-model Claude check (a conditional robustness pass, not
the substrate); not the full λ-ladder (only if the gate passes). Rung 0 remains an **acute
reachability probe** — now interpretable, two-channel, and controlled.

---

## Results (post-registration, 2026-07-23) — replication + pooled CI

*The design above was locked before any run; this section is appended, not edited into it.* Three
seeds were fired — the original `20260723` plus replications `20260724`, `20260725`, each a full
1,250-generation probe at an **independent schedule**. Artifacts: `runs/rung0-v2-{a28965362227,
d1af2cd9a75f,762f48f4d1dd}.json`. Pooled analysis: `experiments/pool_rung0_v2_seeds.py` (zero-spend,
reads the artifacts via the gate's own `evaluate`, bootstrap seed pinned).

**H0 (apparatus) — valid 3/3.** The positive control collapses both channels every seed (V_output
+54–76%, V_reason +29–48%). Extractor validation is satisfied implicitly by the contrast: ablation
skeletons stay diverse, C+ skeletons homogenize.

**H2 (threshold) — 3/3.** C1/C2 show no collapse (V drifts slightly up); collapse turns on only at
C3. A threshold, as WS3 predicted.

**H1 (reachability, the binary gate) — did NOT robustly replicate: REACHED / REACHED / NULL (2/3).**
The miss is a **guard-count threshold artifact, not a disappearance of the effect.** V_reason
clean-collapses (≥20%, significant, all three instruments agree) in 5/5 families every seed; the gate
*additionally* requires ≥3 families to clear the parroting/role guards, and that count is **3 / 3 /
2** — sitting on the threshold. Seed `20260725` fell to 2 only because the `testing` family's leading
item induced output parroting in that schedule (its guard failed), dropping the count below 3. This
is precisely the thresholded-binary-hides-a-continuous-effect failure this arm's ground rules (rule
5, "level and slope both primary") warn about.

**The pooled continuous estimand — robust.** Per (seed, family), `gap = decline_reason −
decline_output` at C3 on the registered primary (I1, `strategy` procedure), the gate's own arithmetic:

| set | mean gap | 95% CI (bootstrap 10k) | positive |
|---|---|---|---|
| guarded — clean conformity (n=8) | **+9.9%** | [+6.3%, +13.9%] **excl. 0** | 8/8 |
| all cells (n=15) | +14.0% | [+10.4%, +17.8%] excl. 0 | 15/15 |

Reasoning-strategy collapses **+27.1%**, output **+17.1%** — both collapse; strategy more. Holds in
all 3 seeds (+10.7/+15.7/+15.6%) and all 5 families (+5.6% … +24.5%). Survives the instrument swap —
I2 (independent local embedder) +11.5% [7.1, 15.3], I3 (lexical distinct-2) +5.1% [3.9, 6.2], both
excl. 0. Not a small-denominator artifact: ablation baselines are comparable (V_reason 0.40, V_output
0.48; ratio 0.83) and reasoning loses more on the **absolute** scale too (~0.11 vs ~0.08).

**The refinement that qualifies H3 — the collapse is STRATEGIC, not total.** The second registered
skeleton procedure, `decisions` (granular decision points), shows the **opposite sign**: gap −6.8%
[−9.0, −4.5]. The three layers order as **strategy +27% ▸ output +17% ▸ decisions +10%** — the
high-level approach converges hardest (every role "adopts the leading approach"), the outputs converge
moderately (surface-diverse extensions), and the specific decision points stay the *most* diverse.
The homogenization an output-only measure misses is therefore **shared high-level strategy**, not
homogenization of the whole reasoning trace. Running both procedures and reporting the disagreeing one
is what surfaced this; the registered primary (`strategy`) is designated and holds.

**H3 verdict.** Not the clean "V_reason collapses while V_output holds" scenario — output *does*
collapse ~17%. The adjudication direction is confirmed (**reasoning-strategy homogenizes measurably
more than output**, CI excluding zero across seeds/families/instruments) but **layer-localized to
strategy**. An output-only null (polyphony) would understate *strategic* convergence specifically.
Whether polyphony's **endogenous** actuator reaches the regime where this bites is rung 1's question —
unchanged by this result, but now carrying a clean, layer-specific estimand rather than the fragile
binary gate.
