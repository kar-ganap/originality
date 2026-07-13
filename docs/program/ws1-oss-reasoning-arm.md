# WS1 — OSS / cross-model arm: two-layer reasoning-diversity study (design note)

**Status:** design note, picked up **post-hackathon** (after Polyphony ships). Private program science —
**never** in the polyphony repo, never shared with judges. Reuses Polyphony's provider-agnostic
`LLMClient` harness (build that agnostic during the hackathon so this is a drop-in).

## Placement — why this arm exists

WS1 (the multi-agent leg) has two arms:

| arm | model | venue | measures | audience |
|---|---|---|---|---|
| **Polyphony** (Build Week) | GPT-5.6 | shared repo + hosted demo | output diversity only | hackathon judges |
| **OSS / cross-model** (this note) | open models | Modal, self-funded, private | **output + reasoning** diversity | the paper / frontier labs |

The OSS arm is not a cheaper re-run. It does two things the frontier-API product **structurally cannot**:
1. **Cross-model** endogenous collapse — different model families conditioning on one shared catalog,
   which kills the shared-weights confound (same-model convergence ≠ conditioning; different-model
   convergence *must* be the shared exposure).
2. **Two-layer diversity** — measure whether the *reasoning* collapses, not just the *outputs*.
   Proprietary models hide/summarize the trace; open models expose the full CoT. This is the arm's
   centerpiece and its independent scientific reason to exist.

## The gap it closes

Output-only diversity **compresses away the reasoning**: two agents that reason completely differently
to the *same* stated conclusion read as identical (Lever-2 construct narrowing, from the cost audit).
Open models expose the CoT, so we can measure the reasoning layer directly and recover that hidden
diversity.

## Design — two layers

Per round, measure diversity at two layers:
- **V_output** — embedding diversity of final answers (the Polyphony metric; `diversity_metrics`).
- **V_reason** — diversity of reasoning *strategies* (see Measurement).

Headline object = the **joint trajectory `(V_output, V_reason)` over rounds**. The 2×2:

| | reasoning diverse | reasoning collapsed |
|---|---|---|
| **outputs diverse** | no collapse | convergent thinking, varied phrasing — *invisible to output metrics* |
| **outputs collapsed** | surface monoculture — one answer, many paths (arguably healthy consensus) | deep collapse |

New empirical questions: **which layer collapses first?** Can output-collapse coexist with preserved
reasoning-diversity (healthy consensus) vs. the insidious reverse (varied phrasing hiding convergent
thought)? The *order* and *decoupling* of the two layers is the novel finding.

## Design knob — what goes in the shared catalog

- **Catalog-of-conclusions** (agents see others' *answers*): does reasoning homogenize even when only
  outputs are shared? (indirect pathway)
- **Catalog-of-reasoning** (agents see others' *reasoning traces*): direct reasoning-homogenization.

The contrast isolates whether reasoning-collapse *requires* reasoning-exposure. Pre-register that
reasoning-collapse may be the weaker/absent signal under catalog-of-conclusions — a fine, informative
null.

## Measurement — the careful part

- **Do NOT embed raw traces.** Length / verbosity / format dominate the geometry, and long traces
  average out (understating diversity).
- **Extract a reasoning skeleton/strategy per trace** — the ordered sub-claims, or the approach taken —
  then measure diversity over skeletons (embedding, edit-distance, or cluster→entropy). Extraction via
  a cheap parse or a small extraction model (a "judge" for *extraction*, not scoring).
- **V_reason is within-model longitudinal only** — CoT formats aren't comparable across families;
  cross-model comparison stays at V_output.
- Control for trace length; report ≥2 skeleton granularities and ≥2 extraction procedures (the WS2
  ≥2-embedding-family discipline, applied to reasoning).

## The faithfulness caveat — scoped, not fatal

Stated CoT is not guaranteed faithful to the model's computation. But this is a framing discipline, not
a measurement problem, for three reasons:

1. **Articulated reasoning is the causally-operative layer for *collective* homogenization.** The
   dynamic propagates through what is *shared*. Un-articulated cognition is causally inert for the
   collective — it can't homogenize anyone. So for the collective-diversity question, articulated
   reasoning is not a lossy proxy; it *is* the operative layer.
2. **It's symmetric with the human arm, which makes the bridge tighter.** WS2/WS3 measure diversity of
   human *articulated* outputs (papers, abstracts, citations) — never cognition. And human articulated
   reasoning is *itself* imperfectly faithful (confabulation / post-hoc rationalization: Nisbett–Wilson,
   Haidt). Using articulated reasoning on both sides makes the human↔AI comparison *more*
   apples-to-apples, not less.
3. **The discipline:** claim *"diversity of articulated reasoning,"* never *"diversity of cognition."*
   Faithfulness only bites if you slide from the former to the latter.

**Residual AI-specific wrinkle (the one genuine asymmetry):** RL can make CoT *decorative*
(reward-hacked), possibly more so than human articulation, which carries some social/professional
accountability. Note it; the catalog-of-reasoning knob + skeleton extraction partly guard against pure
decoration (decorative traces should show low *strategy* diversity even when surface-diverse).

## Substrate

Open **reasoning** models with native long CoT: a DeepSeek-R1-class model, a Qwen-QwQ-class model, and
≥1 further family for the cross-model output layer. Served on Modal (vLLM) or a per-token inference API
(Together/Fireworks/DeepInfra). Cheap — GPU-seconds / pennies-per-token, no API premium.

## Theory hook (`cv_predictor`)

Open question: does the C/V crossover `λ*` **differ by layer**? If, under the same conditioning,
V_output goes C-favouring while V_reason stays V-favouring, the two layers have different `λ*` — the
mean-field predictor could be extended to a two-layer forecast. Speculative; a stretch goal, not
load-bearing.

## Portfolio relevance

Reasoning-diversity collapse in multi-agent systems is squarely what frontier reasoning/RL teams think
about: RLHF/RLVR mode collapse is documented for *outputs*; the *reasoning* layer is under-studied.
Connects to self-consistency (reasoning-*path* diversity as an already-valued construct) and
algorithmic-monoculture concerns. The 2×2 (which layer collapses, in what order) is a novel, legible
framing — "does the *thinking* collapse, or only the *talking*?"

## Pre-registration stub (fill before running)

- Metrics: V_output (≥2 embedding families) + V_reason (≥2 skeleton extractions), per round, ≥4 seeds.
- Primary: the `(V_output, V_reason)` joint slope trajectory + which-collapses-first ordering.
- Refute criteria (per layer): shared-catalog slope < 0, CI excludes 0, AND no-catalog slope flatter/≥0.
- Knob contrast: catalog-of-conclusions vs catalog-of-reasoning (does reasoning-collapse need
  reasoning-exposure?).
- Report **regime-ordering/sign over magnitude** (short-output magnitude-inflation caution carries over).
