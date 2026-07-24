# Rung 2 — the two-channel adjudication (catalog-of-conclusions): result

**2026-07-24.** The arm's centerpiece (design note `ws1-oss-reasoning-arm.md` §4, §9.4). Rung 1 showed
Polyphony's *output* null replicates on DeepSeek under the endogenous actuator. Rung 2 adds the second
channel: does **reasoning** collapse where output held? Outcomes were pre-committed in §9.4.

## What was run

The rung-1 R4 loop under **catalog-of-conclusions** (agents see each other's answers — the regime
Polyphony actually ran), now capturing each agent's reasoning trace. After each run the **strategy**
skeleton (rung 0's refinement — the layer where imposed collapse lives) is extracted from every trace
(`deepseek-v4-flash`, rung-0's frozen prompt) and embedded on the fixed `text-embedding-3-small`, so
each artifact carries `skeleton_embeddings` beside `proposal_embeddings`. The confirmatory collapse
criterion (`rung1_confirm`, `v_embeddings_key`) then runs on **both** channels. 24 artifacts, ~$0.71.
`experiments/{run_rung2,analyze_rung2}.py`; summary `runs/rung2-r4-confirm.json`.

## Verdict — the null DEEPENS (neither channel collapses)

Bootstrap (10,000 draws, seed 20260718), actuator answer-based and shared:

| channel | popularity V slope | 95% upper | pop − ablation | verdict |
|---|---|---|---|---|
| actuator | uptake +0.03444 | lower +0.01395 | — | **live** |
| **V_output** | −0.00096 | +0.00802 | +0.00169 | no collapse |
| **V_reason** | +0.00262 | +0.00926 | +0.00449 | no collapse |

Under a demonstrably live actuator, **both** channels resist: `V_output` holds (as in rung 1) and
`V_reason` if anything *rises* (+0.0026) — all collapse upper bounds straddle zero. This is §9.4's
"`V_reason` holds with `V_output` → the null **deepens**: resilience is not surface-level. Report as
strengthening, not as a failure to find." **Eyeball-confirmed:** at round 7 the five personas still
reason from distinct angles (reliability→rollback, security→misuse, learning→feedback loops,
cost→token budget), not the shared "adopt the leading approach" convergence rung 0's imposed C3 showed.

## The arm-level synthesis (rungs 0 · 1 · 2)

- **Rung 0 (imposed):** reasoning-strategy *can* collapse — but only under **maximal imposed**
  conformity ("adopt the leading approach"): strategy +27% vs output +17%, robust across 3 seeds.
- **Rung 1 (endogenous):** outputs do **not** collapse under the endogenous actuator (null replicates,
  cross-substrate; concentration a sampling artifact).
- **Rung 2 (endogenous):** reasoning *also* does not collapse under the endogenous actuator (null
  deepens).

Together this is exactly the design note's **imposed-vs-endogenous gap** (§3): reasoning collapse sits
at an imposed strength (rung 0's C3) that the **realistic endogenous actuator does not reach** — for
either layer. The reasoning collapse rung 0 found is *imposed-only*.

## What this settles about the founding question

The arm exists to ask: **is Polyphony's output-only null a measurement artifact — is reasoning
collapsing invisibly under the layer that talks?** For the regime Polyphony actually ran
(catalog-of-conclusions, shared conclusions): **no.** Reasoning resists as much as output. The
measurement-artifact hypothesis — which rung 0 made plausible *under imposed conformity* — does **not**
hold endogenously. Polyphony's null is genuine and **two-layer**, deeper than the output metric showed,
not a measurement artifact. (This honestly revises rung 0's "first evidence it *could* be an artifact":
that evidence was imposed-only.)

## What remains — the reasoning-exposure actuator

One pre-registered variant is untested (§9.4: "reasoning collapses only under catalog-of-reasoning →
reasoning-collapse **requires reasoning-exposure**"). Under catalog-of-**conclusions** reasoning holds;
the open mechanism question is whether sharing the **reasoning traces** themselves (catalog-of-reasoning
— the actuator a proprietary API structurally cannot run) collapses reasoning. That is rung 2's second
half and the arm's remaining novel test.
