# Build brief — WS1 OSS arm, Rung 0 (reachability probe)

> **How to use this.** Paste the whole document into a fresh agent session in a **new private repo**.
> It is deliberately self-contained. The parent design note is `ws1-oss-reasoning-arm.md` (§4 rung 0,
> §9); this brief is the executable subset. **Rung 0 is LOCKED — build to it, do not redesign it.**
>
> Status: drafted 2026-07-21, sizing locked the same day (5 families × 10 blocks). Not yet built.

## 0. Hard rules

- **New PRIVATE repo**, sibling to the others. Self-contained.
- **Firewall.** Never reference or describe any other study, dataset, or program by name. One
  exception: **Polyphony is public** (`github.com/kar-ganap/polyphony`) and is citable as prior work
  by the same author. Everything else stays out.
- **Secrets** in env/`.env` only, never committed. API-key auth with a hard cap.
- **TDD.** The engine (actuators, metrics, classifier, analysis) must be token-free and unit-tested
  behind a mockable client. Only generation calls hit the network.
- **Every reported number regenerates from a committed script** reading committed results. No
  one-time scripts; no hand-edited artifacts.
- **Register every constant.** Any threshold, floor, or margin not in this brief needs a dated
  change-log entry and an explicit flag in your report. Silent post-hoc constants are the single
  failure mode this study exists to avoid.

## 1. The question

Prior work (Polyphony, public) found that role-diverse LLM ensembles did **not** homogenize under
shared-context conditioning — six pre-registered experiments, every actuator tried. Rung 0 asks the
prerequisite question that makes that null interpretable:

> **Under maximal imposed conformity, can output diversity be driven down *at all* in a role-diverse
> ensemble?**

Both answers are publishable. If yes, we learn the concentration level collapse requires, which
gives the earlier null a denominator. If no, *"role-diverse in-context ensembles have no accessible
collapse phase under two independent actuator forms"* is a strong boundary result with a measured
floor, and the study stops there honestly.

## 2. THE TRAP — read this twice

There is a degenerate corner that will pass this rung on a tautology and silently invalidate
everything downstream. Prior work already ran it:

With **homogeneous** personas (5 identical roles) and a dominant shared item, V fell **0.158 → 0.032**
(−80%) on one task — but `anchor_alignment` rose **0.576 → 0.843** and the outputs were near-verbatim
restatements of the shown item. That is **parroting with diversity zeroed by construction**, not
conformity dynamics.

With **role-diverse** personas, the *same* actuator produced **+0.0029** and **+0.0111** — V moved the
*wrong way*.

So an actuator that instructs agents to "extend/restate the shown item" measures nothing. Three
guards are **mandatory and non-negotiable**:

1. Personas held at the **diverse** setting (5 distinct roles), with measured persona diversity D
   verified statistically unchanged vs the ablation cell.
2. `anchor_alignment` must stay **below 0.65** (diverse baseline 0.34–0.51; parroting 0.84).
3. The effect must appear in **≥3 of 5** task families. Every single-task result in this line of work
   has failed to generalize.

A large V drop *with* alignment above the ceiling is a **parroting artifact** and must be reported as
such — never as a pass.

## 3. Specification (LOCKED)

**Substrate:** GPT-5.6 (`gpt-5.6-sol`), reasoning effort `none`, ~120 max output tokens.
**Use this substrate, not an OSS model.** Every calibration constant below comes from GPT-5.6 runs;
changing substrate here would confound reachability with substrate change — precisely the error a
later rung exists to prevent. OSS and Claude enter at rung 1.

**Design:** **5** self-authored task families × **3 cells** × **5 distinct roles** × **10 blocks** =
**750 generation calls**. Single round — the question is acute reachability, not dynamics.

| cell | actuator |
|---|---|
| **A — instruction-λ=1** | directive at maximum: "align with the leading approaches shown" |
| **B — payoff-λ=1** | agents see which prior proposals were "adopted" + adoption counts, and are told adoption is the goal |
| **C — ablation** | no shared context; matched prompt, format, and length |

A and B are a deliberate **form-vs-strength contrast**: a null in both is far stronger than a null in
one. Suggested roles (reuse or adapt): Reliability engineer, Product designer, Security reviewer,
Learning scientist, Cost analyst.

**Measurement scale, calibrated from prior work — do not re-derive:**

| quantity | value |
|---|---|
| `V_output` ceiling (role-diverse free generation) | ≈ **0.42** |
| `V_output` floor (total copying) | **0.00** |
| bootstrap CI half-width (2 blocks/topic) | 0.003 – 0.013 |
| parroting signature (`anchor_alignment`) | 0.84 |
| non-parroting alignment shift | +0.014 to +0.050 |

**Gate — passes iff ALL FOUR hold:**

1. `V_output` declines **≥20%** vs matched ablation (V ≤ 0.336, Δ ≈ −0.084).
2. In **≥3 of 5** task families.
3. One-sided sign/Wilcoxon **p<.05** at **n=10** blocks.
4. All three §2 guards satisfied.

**The arithmetic is already checked — do not re-derive it, but do not violate it either.** Δ=−0.084
against a CI half-width of 0.003–0.013 is 7–28× headroom, so detection is not the constraint.
Minimum one-sided Wilcoxon p is 0.0625 at n=4, 0.031 at n=5, 0.016 at n=6, **0.00098 at n=10**.
**Never reduce n below 6; at n≤4 a p<.05 gate is arithmetically dead.**

## 4. What to build

1. **Provider-agnostic client.** Prior work has only a private helper returning a bare `OpenAI()` with
   no `base_url`. Build a real abstraction: OpenAI-compatible with a `base_url` parameter (so OSS
   endpoints drop in at rung 1), **plus a stub seam for a Claude extended-thinking path**. Mockable.
2. **The two actuators** (A, B) as composable, tested, token-free-renderable prompt builders.
3. **Measurement.**
   - `V_output` = **mean pairwise cosine distance** over the round's outputs.
     **Do NOT use participation-ratio effective dimensionality as the primary** — it is exactly
     scale-invariant `(Σλ)²/Σλ²`, hence structurally blind to uniform contraction toward a point.
     Report it as a secondary; never gate on it.
   - `anchor_alignment` — mean cosine of outputs to the shown item(s). The parroting guard.
   - **Concentration**, reference-anchored (partition fit once on a fixed reference set, never refit
     per round). **Also reproduce prior work's "top-four echo-concentration" definition**, so the
     comparison in §5 is apples-to-apples.
   - Persona diversity D, to verify guard 1.
4. **Classifier.** Level and slope both primary, applied symmetrically. Collapse fires on level OR
   slope; sustain requires flat on BOTH — a genuine TOST with a **t**-quantile, not "CI contains
   zero" (a failure-to-reject is not an equivalence claim). Permutation tests **one-sided**. Rung 0
   is single-round so the level path dominates, but build it correctly now; later rungs need it.
5. **Token/cost telemetry.** Log actual input/output/reasoning tokens per call. Rung 0 doubles as the
   cost calibration for later rungs, which are dominated by reasoning tokens billed at output rate.

## 5. Report these, whatever happens

- Per-cell, per-family V, alignment, concentration, D — with bootstrap CIs and all raw block values.
- The gate verdict **item by item** (all four conditions, pass/fail each).
- **H\*** — the concentration observed at the collapse point, if collapse occurs. This is the number
  the whole study needs. Prior work's endogenous actuator reached concentration **+0.0102** without
  collapsing, and that null is currently uninterpretable because nobody knows what level collapse
  requires. Report **`H_endogenous / H*`** explicitly; it classifies the earlier null into one of
  three pre-committed bands (≥H\* = strong resilience; 0.5–1× = bounded; <0.5× = actuator-limited and
  **not** evidence of resilience).
- Measured tokens/call and total spend.

## 6. Honest-null commitments (pre-registered — honor them)

- **Fails in both cells** → "no accessible collapse phase under two independent actuator forms."
  **STOP.** That is the result. Do not escalate the actuator until something moves.
- **Fails in one cell only** → reachability is actuator-form-dependent. Report the dependence
  prominently; it is a finding about *what kind* of pressure homogenizes.
- **Large V drop with alignment >0.65** → parroting artifact, **not** a pass.
- **No gate substitution.** If the gate fails, report the failure. Do not promote a different
  statistic to "the gate," do not demote a failed criterion to a "sanity check," and do not
  reinterpret a threshold after seeing the numbers.

## 7. Conditional tail — run ONLY if the gate passes

If λ=1 collapses V, immediately extend on the same warm harness to **λ ∈ {0.33, 0.66}** for both
actuator forms: 5 families × 4 added cells × 5 agents × 10 blocks = **1,000 calls ≈ $3.65**. This
brackets λ\* while the apparatus is running and pulls the cheap half of the later theory rung
forward.

**Do not run it if the gate fails.** Every intermediate λ is weaker than λ=1, so a λ=1 null makes the
ladder vacuous — this is exactly the staging error a sibling project made by running its dose-response
test at the floor, where it could not resolve.

## 8. Budget

Priced from **measured actuals**, not estimates. A prior 960-call run on this exact substrate
(effort `none`, 120-token cap, 5-agent cells) used **137.4 input** and **63.0 output** tokens/call =
**$2.47** at Sol's $5/$30 per 1M.

| item | calls | estimate |
|---|---|---|
| rung 0 | 750 | **≈ $2.80** |
| hard ceiling (output capped at 120, bills 6× input) | 750 | **$4.60** |
| conditional λ tail | 1,000 | ≈ $3.65 |
| all-in with preflight, prompt iteration, one full re-run | — | **$8–12** |

Cost is **not** a design constraint at this rung — size by what the science needs. Report actual
spend against this table; a sibling project's ledger ran ~$65 low against a hard cap and it cost two
experimental arms.

## 9. Out of scope — do not build

Later rungs: substrate change, the endogenous multi-round arm, `V_reason` / reasoning-skeleton
extraction, λ\* straddling with fidelity and innovation shift arms, the cross-model panel. Their
gates are deliberately unset and will be calibrated from rung 0's telemetry. Build the client seam
for them; build nothing else.

**Definition of done:** engine token-free-tested and green; the 5×3×5×10 run executed under budget;
every number regenerates from a committed script; the gate verdict stated item by item; H\* (or its
absence) reported; and a retro covering hypothesis, what happened, surprises, and what to change.
