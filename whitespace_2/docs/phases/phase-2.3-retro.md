# Phase 2.3 Retro — the subfield mechanism test (+ the SPECTER2 escalation)

**Phase:** 2.3 — the pre-registered "single most important analysis"
**Stage:** 2 → 3 (Walk → Run close-out)
**Branch:** `phase-2.3-subfield`
**Window:** 2026-07-01 (one session)
**Status:** Complete. **No robust localized mechanism** (the reframing's
independence holds); the Phase-2.2 "frontier widens" reframing **refined, not
overturned**, by a 3rd embedding family.

---

## Hypothesis (pre-registered, `phase-2.3-plan.md`)

Do canon-concentrated subfields show more demographic–semantic divergence than
diffuse ones? Regress `divergence_magnitude = demographic_trend_sd −
semantic_trend_sd` (absolute, NOT the Phase-2.2 confounded ratio) on
`canon_concentration` (mean reference-canonicity Gini), controlling for
`log_size`. Flat γ₁ across specs → supports the reframing's independence; robust
positive γ₁ → a localized actuator-homogenization mechanism (the last place a
narrowing could hide after the aggregate null).

## What happened

**No robust localized mechanism.** Across a 6-spec grid ({SciNCL, Qwen3,
SPECTER2} × {level-1 sub-concepts, K=50 clusters}), γ₁'s **sign is
embedding-determined** — the three significant specs contradict each other
(SciNCL sub-concepts +0.24σ, p=0.02; both SPECTER2 −0.43/−0.47σ, p<0.01). A
signal whose sign flips with the embedding is not a mechanism. Canon-
concentration does not robustly predict divergence → concentration and
frontier/authorship diversity are **independent** (the reframing).

The 2-family (SciNCL+Qwen3) read had flagged a **Physics wrinkle** (Physics/SciNCL
γ₁=+0.70σ, p=0.003, internally LOO-stable). The user asked for the pre-committed
3rd family (SPECTER2) to adjudicate it. It did: **Physics/SPECTER2 γ₁=−0.35σ
(ns)** — 1 of 3 families supports the wrinkle → not a real mechanism.

## The escalation (user: "escalate but verify first")

SPECTER2's per-subfield semantic trends skewed negative (mean −1.35σ vs SciNCL
+2.3σ), which — if real — would threaten the Phase-2.2 "the frontier diversifies"
reframing. **Verify first** dissolved most of it:

1. **Adapter active** (Modal `check_adapter`): the proximity adapter materially
   changes the embeddings → SPECTER2 is the citation-tuned model, not the base.
2. **Not drift**: the reversal does NOT attenuate on later windows (−1.35σ
   1970–2023 → −1.56σ 2000–2023), so it is not a pre-1990 embedding-drift
   artifact (though SPECTER2 is the most drift-susceptible family, Check 5c).
3. **Ill-conditioned σ** (the load-bearing catch): SPECTER2's per-year
   mean-pairwise is **near-flat** for CS subfields (AI 0.185→0.180, range 0.008),
   so `standardized_effect` (slope×range / tiny-sd) amplifies dust into large
   sign-unstable σ — the exact Phase-2.2 caution. The honest measure is the
   **aggregate whole-field** trend (higher-N, well-conditioned) judged by
   permutation significance + **absolute magnitude**:

   | Field | SciNCL | Qwen3 | SPECTER2 |
   |---|---|---|---|
   | CS | +22.6%* | +6.6%* | **+3.4%* (up)** |
   | Physics | +23.7%* | +10.5%* | **−10.2%* (down)** |

**Resolution:** in **CS all three families agree the frontier widens** (reframing
intact); **Physics is the sole locus of disagreement** — topical embeddings widen,
the citation-tuned SPECTER2 narrows. Interpretation: where the canon is most
concentrated (Physics), a citation-geometry embedding "sees" papers converging
onto the shared canon while topical embeddings see subject-matter spreading. The
"frontier diversifies" claim is **refined** ("the topical frontier widens;
citation-geometry narrows exactly where the canon concentrates"), not overturned.

## Surprises / lessons (see `tasks/lessons.md`)

- **A 3rd family can flip a trend's SIGN, not just its significance** — and a
  mean-of-per-unit-σ over near-flat units is dominated by ill-conditioned dust.
  Judge with the aggregate + permutation + absolute magnitude. (2nd time the
  ill-conditioned-σ trap bit — Phase 2.2 was the first.)
- **"Semantic diversity" is not one construct** — citation-geometry (SPECTER2)
  and topical (Qwen3/SciNCL) embeddings can trend oppositely; report families
  spanning objectives and treat disagreement as a finding about the construct.
- **Flaky Modal `.map()` result-streaming** (2.7 GB back to a flaky client)
  wedged; the fix is server-side Volume writes + tiny returns + resume loop +
  server-side concat. (Infra lesson.)
- **Ratio ≠ control / VIF / verify-extreme-claims** — all carried; the divergence
  is absolute-trend-differenced, VIF 1.2–2.0 (identifiable), and the striking
  SPECTER2 number was chased before belief.

## Workstreams (commits on `phase-2.3-subfield`)

| WS | Result |
|---|---|
| PLAN | `phase-2.3-plan.md` pre-registration |
| TEST+IMPL | `src/whitespace2/subfield_divergence.py` (map + `subfield_regression` w/ FWL permutation γ₁, VIF, standardized) + 11 tests |
| COMPUTE | `build_subfields` (2 defs, 83 concept / 50 cluster subfields) + `compute_subfield_metrics` (per-subfield canon/semantic/demographic) + `run_subfield_test` (grid + verdict) |
| SPECTER2 | 1M SPECTER2 embed (server-side volume-write, ~$3) → 6-spec grid |
| ESCALATION | `aggregate_3family` + `drift_diagnostic` + adapter check → the verified reframing refinement |
| fix | mypy `--strict` under `--all-extras` (transformers 4.57 untyped `from_pretrained`) |

## Validation gates

| Gate | Result |
|---|---|
| G1 substrate sanity (canon rises, subfield grain) | ✅ passes (CS + Physics) |
| G2 estimator correctness (TDD) | ✅ 11 tests (planted-γ₁, null, VIF, FE, degenerate) |
| G3 full grid reported (γ₁, perm p, VIF, std) | ✅ 6 specs + per-field + aggregate |
| G4 verdict with component trends shown | ✅ + LOO + drift + adapter verification |
| G5 tests + lint + typecheck clean | ✅ 260 tests, ruff + mypy strict |

## Implication for the program (WS3 bridge)

`conceptual.md` §"What ws2 contributes": no-robust-positive-γ₁ challenges the
actuator-homogenization *structural* claim at the phenomenon level — the
independence holds. The mechanism-space is **narrowed** for WS1: canon-
concentration couples to **citation-geometry convergence** (SPECTER2 Physics
narrowing), NOT to topical narrowing, and only where the canon is strong
(Physics). WS1's simulation should reproduce "topical frontier widens while
citation-geometry converges onto a concentrating canon," a sharper target than
the aggregate reframing alone.

## Companion documents

- `experiments/phase-2.3/subfield-mechanism-results.md` (full results)
- `experiments/phase-2.3/series/` — metrics (concepts/clusters), mechanism-results
  json, `aggregate-3family.json`, `specter2-verification.txt`, concept-names
- Pre-registration: `docs/phases/phase-2.3-plan.md`
- North star: `docs/conceptual.md` (line 35 subfield test)
