# Insulation pre-registration — the AI causal test of Claim #17

**LOCKED 2026-07-24.** Claim #17: *small, insulated groups produce disproportionate per-capita
originality.* The AI causal test the human (observational) version can't run cleanly — manipulation
kills reverse-causality, survivorship, and the group-detection forking paths in one move. Substrate:
DeepSeek V4-pro (thinking on) via `DeepSeekClient`; fixed embedder `text-embedding-3-small`. Reuses
the rung-1 R4 machinery (`Catalog`, `run_r4`, `record_echoes`, the bootstrap+null pattern).

## The design (two decisions settled)

Two ensembles, the same 5 personas (`stimuli.ROLES`), the same 8-item seed catalog:

- **FIELD (connected):** a `run_r4` popularity run over T rounds. Its catalog **is** the mainstream —
  agents condition on it and grow it, drifting toward the popular.
- **ISOLATED (insulated group):** a `run_r4` popularity run over T rounds on its **own local catalog**
  — internal cross-pollination, insulated from the field (decision 1: *local catalog*, not lone-wolf
  ablation).

**Candidate pool:** the round-T proposals from each run (5 connected-origin + 5 isolated-origin ideas),
with their embeddings.

**Adoption phase (A rounds):** the **field** ensemble (conditioning on the field catalog — decision 2:
*the connected field judges*, conformity-biased and realistic) is shown, each round, a **balanced mix**
of candidates (k connected + k isolated). The field proposes; we measure **echo** accrued by each shown
candidate — `Σ_agents max(cos(field_output, candidate), 0)`, the `record_echoes` formula.

## The estimand (the non-tautological core)

**Per-capita adoption** for an origin = mean echo per candidate of that origin. The claim predicts
**isolated > connected**. This is not circular: adoption is the field's *behavioral uptake*, measured
separately from divergence, and the direction is not predetermined — a conformity-biased field would
echo the *familiar* (connected/its-own) ideas more (→ isolated **less**); a novelty-rewarding field
echoes the outsider ideas more (→ isolated **more**). "Isolated agents are more diverse" would be
near-tautological, which is exactly why the outcome is **adoption, not diversity**.

## Matched null (registered)

**Label-shuffle:** permute the candidate origin labels (isolated/connected) across the pool and
recompute the per-capita adoption gap, many times. The observed gap must exceed this null's — this
guards against the gap being a mechanical property of pool composition rather than of origin.

## Refute criteria (pre-committed)

- **Claim #17 supported** iff isolated − connected per-capita adoption **> 0**, its bootstrap 95% CI
  (over run-ids) **excludes 0**, **and** the observed gap **exceeds the label-shuffle null** (one-sided
  p < 0.05).
- **Informative null** iff the gap is ≤ 0 or indistinguishable from the label-shuffle null: insulation
  does **not** produce disproportionately-adopted ideas. Report as-is (per the program's discipline, a
  clean disconfirmation is a result).
- **Actuator-live precondition:** the field must measurably echo *shown* candidates over *unseen* decoys
  (a positive uptake, CI-excluding-0) — else adoption is unmeasurable and the result is unreadable, as
  in rung 2b.

## Registered constants

`N_PERSONAS = 5` · field/isolated rounds `T = 8` · adoption rounds `A = 6` · candidates per origin from
round T = 5 · adoption sample per round = 2 connected + 2 isolated · seed catalog = the 8 R4 items ·
bootstrap 10,000 draws, seed 20260718 · label-shuffle 10,000, seed 20260724 · **run-ids: 8** (4 per
topic × 2 topics) for the CI. Group size held equal (5 vs 5) for a clean per-idea test; an
isolated-group-**size** sweep (the "small" dimension) is a registered secondary, not the primary.

## Cost

~$1–1.5 fire (2 × 5-persona R4 runs + a 6-round adoption loop per run-id, no skeleton extraction) +
~$0.10 smoke + buffer ≈ **~$2 all-in**. Null + bootstrap are compute-only.

## What this is not

Not the human observational study (skipped — tenable only via a natural-experiment design). Not a
group-**size** primary (secondary only). Not a diversity claim — the outcome is field adoption.
