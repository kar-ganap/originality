# Phase 3 retro: noise-floor diagnostics — the verdict

**Run 2026-07-22.** Grid: 1440 `channel.run` calls (2 modes × 2 f × 4 λ × 3 N × 30 seeds) + the E3
isolation point, model pinned at `dbd367a`. Executed exactly per `resolution-map-phase3-prereg.md`
(with the smoke-stage E2/E4 corrections recorded there). Raw per-seed steady states →
`runs/raw-grid.json`; classification → `runs/phase3-verdict.json`. Nothing was tuned after the run.

## Verdict vs. the pre-registered predictions

| estimand | predicted | observed | match |
| --- | --- | --- | --- |
| **E1** — Vstruct level vs λ | USABLE | **USABLE at λ≥0.5** (−37% to −86%); noise-dominated at λ=0.1 (−3 to −10%, below the 20% floor) | ✓ refined |
| **E2** — N-decoupling (targeted) | USABLE | **USABLE, 16/16 cells** (W-slope reliably +875…+2193, Vstruct-slope reliably <0) | ✓ |
| **E3** — isolation Pareto | USABLE | **USABLE** (+58.9%, CI [+0.54,+0.64]) | ✓ |
| **E4** — crossover (total-V, both modes) | uncertain; likely EXCL | **EXCL, all 4 mode×f** — no CI-separated flip | ✓ |
| **E5** — C responds to N | provisionally USABLE-at-this-N | **EXCL — deterministic clock** (all cells) | ✗ **miss** |

## The headline: the crossover is not statistically present at n=30

E4 is the load-bearing one, and it settles the audit's open question. Under **uniform total-V** — where
the reconciliation crossover was supposed to live — the N-slope is **≈0 and CI-straddling at low λ**
(λ=0.0: −0.0008 [−.003,+.001]; λ=0.1: −0.0008 [−.003,+.001]) and **reliably negative at high λ**
(λ=0.5: −0.0034 [−.005,−.002]; λ=2.0: −0.0060 [−.007,−.005]). There is **no reliably V-favouring
region**: total-V never reliably *rises* in N. So the "same lever, opposite signs" reconciliation
fails its first half — the V-favouring side that gives small teams their per-capita advantage is
indistinguishable from zero. Under *targeted*, total-V trends the wrong way for a crossover
(negative→positive). `λ*≈0.09` was interpolation across a straddle-zero low-λ slope.

This is **intrinsic mush, not under-power**: at 30 seeds the CIs are already tight (±0.002); the low-λ
slopes are *centered* near zero, so more seeds tighten *around zero*, they do not reveal a positive
slope. E4 is not power-rescuable.

## The surprise (a real miss): C is a deterministic clock in N

I predicted E5 provisionally usable because C *rises* with N on this grid (it does: slopes +0.24…+8.7,
CIs exclude 0). But the gate correctly excluded it: **C has ~zero seed variance at N=480 in every
cell** (`deterministic=True`), so its N-response carries no stochastic uncertainty — a clock, not a
testable counterfactual. My prediction focused on whether C *responds* and missed whether it does so
*stochastically*. The determinism guard I built caught what my prediction didn't. (The 4-seed smoke
had shown `deterministic=False` — a small-sample artifact; 30 seeds resolves C as deterministic.)

Both halves of the reconciliation's "opposite signs" therefore fail at n=30: **no V-favouring region**
(E4) and **C is a trivial clock** (E5). The crossover is not a usable counterfactual.

## What IS usable — the constructive result

The map found crisp, WS1-relevant content, just not where the theory's headline is:

- **E1 — conformity crushes structural novelty**, a large *level* effect (−37% at λ=0.5, −86% at
  λ=2.0), WS1-testable (a level contrast, matching the rung-0 gate) — but only **above λ≈0.5**; at
  weak conformity the effect is real yet below WS1's 20% floor. That threshold is itself a prediction.
- **E3 — isolation preserves structural novelty** (+59% for the shielded subgroup), WS1-testable.
- **E2 — the N-decoupling** (breadth↑ while structure↓ in N) is robustly present (16/16), though
  internal (WS1 cannot vary N).

## §3 → §4 decision

- **Proceed to §4: E1, E2, E3.** All stochastic-with-signal. 30 seeds gave tight CIs cleanly separated
  from SESOI, so the §4 seed budget is settled at 30 (no larger budget needed for these).
- **Excluded: E4** (intrinsic mush — no V-favouring region; not power-rescuable) and **E5**
  (deterministic clock). Neither proceeds.

## Honest gaps in this phase

- The two *supporting* §3 diagnostics — the formal **variance decomposition** and the **power curve** —
  were not separately run. They are moot for the outcome: the usable estimands (E1/E2/E3) came back
  with tight CIs well clear of SESOI (so 30 seeds is demonstrably adequate), and the exclusions (E4
  intrinsic-zero, E5 deterministic) are not power-limited, so a power curve would not change them. If
  §4 proceeds they can be run then; flagged here rather than skipped silently.
- E1's λ=0.1 noise-dominated verdict is a *SESOI* (effect-size) verdict, not a variance one — the CI
  excludes zero, the effect is just below WS1's floor.

## Bearing on "WS3 as a counterfactual engine"

The resolution map answered its question. WS3's usable counterfactual content is the **level and
intervention** estimands — *conformity crushes structural novelty above a threshold; isolation
preserves it* — both of which map directly onto WS1's actuator (drive conformity; shield a subgroup).
Its **crossover** (the λ* reconciliation headline) and its **C-accumulation** are **not** usable: one
is not reliably present, the other is a deterministic clock. So the engine survives, demoted exactly as
anticipated — trustworthy on the level/intervention channel, mute on the crossover — and now that
demotion is a measured result, not an assertion.
