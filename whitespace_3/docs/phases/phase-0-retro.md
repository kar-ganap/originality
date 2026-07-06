# WS3 Phase 0 Retro — the C substrate (transmission)

**Phase:** 0 — substrate on-ramp (the cumulative-complexity `C` substrate)
**Branch:** `ws3`
**Window:** 2026-07-02 – 2026-07-03
**Status:** COMPLETE. rung 1 + rung 2a built, TDD, 14 tests green; ruff + mypy
strict clean; pre-push hook enforcing the gates.

---

## Goal

Build and *validate* the transmission → `C` substrate (primer §5.1), reproducing
a published cultural-evolution result as the known-answer anchor, and build enough
substrate fluency to proceed to innovation and `V` (Phase 1).

## What happened

- **rung 1 (`transmission.py`) — the scalar Henrich 2004 model, Level-3 anchored.**
  Copy-the-best oblique transmission with Gumbel inference error (mode `z_h − α`,
  dispersion `β`). Our `per_gen_drift` / `critical_population_size` are Henrich's
  Eqs (2)/(3) verbatim, verified against the paper PDF. The simulation reproduces
  **Mesoudi's canonical `DemographyModel` (Model 9)** published runs (N=100 gain /
  N=1 loss at α=30,β=15) and the Δz̄-vs-N crossover at **`N* = exp(α/β − γ_E) ≈ 616`**
  (α=7,β=1) — a specific published number, not our own formula.
- **rung 2a (`concept_base.py`) — the concept-base representation.** Discrete
  elements on a prerequisite ladder + per-level `f`/redundancy acquisition (primer
  Def 4.1). Its purpose is to **un-bundle transmission from innovation** (rung 1's
  Gumbel fused mean-loss and the improvement tail). Anchors: maintenance for large
  N, Tasmania loss for small N, monotone in N and f, and the un-bundling check —
  **transmission alone never grows C** (non-increasing, capped at `c0`).

## Surprises / lessons

1. **The Gumbel bundled transmission and innovation** (its mean-loss = imperfect
   copying, its right tail = innovation). You cannot decompose `C` from `V` while
   they share one knob — so the concept-base representation's first job is to split
   them. That split is the whole reason `V` becomes definable (rung 2b).
2. **Representation follows dynamics.** For pure single-ladder transmission the
   concept base collapses to a scalar top-level; the prerequisite/canon machinery
   is dormant until innovation/conformity need it. We don't owe the full formalism
   up front — each rung uses the minimal sufficient representation.
3. **Level-3 correction (the big one).** The user asked "did we reproduce any prior
   results?" and set the standard: reproduce a *specific published number*, not our
   own formula. Audit found (a) I had **overclaimed "reproduce Powell 2009"** — we
   built single-population Henrich, not Powell's metapopulation; (b) the anchor was
   sim-vs-our-own-formula (internal). Fixed: verified against Henrich's Eqs (2)/(3)
   and reproduced Mesoudi Model 9's specific numbers. Codified as a lessons entry +
   the `feedback_reproduce_published_numbers` memory. **Powell's metapopulation is
   now correctly scoped as the Level-3 target for the later network rung.**

## Honest scorecard (per the reproduce-published-numbers principle)

| Rung | Reproduces a published result? | Level |
|---|---|---|
| rung 1 (scalar Henrich) | **Yes** — Mesoudi Model 9 runs + `N*≈616` crossover | **3** |
| rung 2a (concept-base) | No — *our* per-level mechanism; qualitative preservation direction only | n/a (documented: novel mechanism) |

## Validation gates

- 14 tests green (7 rung 1 incl. the Level-3 regime + crossover anchors; 7 rung 2a).
- ruff + mypy --strict clean.
- **Enforcement:** a `pre-push` git hook (`hooks/pre-push`, `core.hooksPath=hooks`)
  runs `make lint typecheck test` and blocks a red push — the mechanical gate WS2
  lacked.

## What to change / carry to Phase 1

- **Plan-first cadence, restored.** Phase 0 ran a bit ahead of a written plan;
  Phase 1 gets its anchors pre-registered *before* rung 2b — in particular the
  **`κ=0` placebo** (per-capita `V` must rise/flat in `N`, *no* crossover).
- **Level 3 where a rung reproduces a published model; document the reason where
  not** (the standing standard now).
- **Two-tier model:** minimal generic-`κ` for the theorem; the two-channel
  content/attachment refinement as the WS2-consistency layer.
- Next: **Phase 1** — innovation → per-capita `V` (rung 2b), then `κ` → the
  crossover (rung 3, the load-bearing lemma).

## Sources

Henrich 2004 (Tasmania); Mesoudi, *Simulation Models of Cultural Evolution in R*,
Model 9 (`DemographyModel`) — the reproducible Level-3 source.
