# WS2 Phase 2.4 Retro — the per-capita V-extension (empirical anchor for WS3 Core Claim 6)

**Stage:** 3 · **Branch:** `phase-2.4-v-extension` · **Window:** 2026-07-07
**Status:** Pre-registered headline test COMPLETE. Core Claim 6 **disconfirmed**; the
mechanism behind the disconfirmation **identified (fragmentation)**. SPECTER2/`V^lat`
arms remain as optional robustness/color.
**Pre-registration:** `../../whitespace_3/docs/primers/v-extension-empirical-spec.tex`.
**Reproducible:** `experiments/phase-2.4/{build_panel,analyze}.py` regenerate the panel
+ every headline number (seeded); measures/estimator tested in
`src/whitespace2/v_extension.py`.

---

## Hypotheses (from the spec) and verdicts

| # | Pre-registered | Verdict |
|---|---|---|
| **H-decline** | per-capita `V^struct` **declines** (`β₁<0`), ≥2 structural measures, permutation-sig. | **Disconfirmed, opposite sign.** off-canon `+0.006` (p=0.0005); atypicality median-z `−0.64` (p=0.0005) — both say `V^struct` **RISES**. |
| **H-gradient** | steeper decline where the canon concentrates (Physics > CS). | **Disconfirmed** — no decline; if anything Physics rises too (VIF-limited). |
| **H-within-team** | decline survives within team-size strata. | **N/A / reversed** — solo null; teams *rise* (stronger for larger teams). |
| **negative controls** | random-canon placebo → null; year-shuffle → null. | **Pass** — random-canon placebo flat (`+0.000001`, p=0.99); the off-canon rise is canon-*specific*, α-robust (1/5/10%). |

## The headline: Core Claim 6 is disconfirmed — structural novelty *rises*

Two independent embedding-free measures — off-canon reference share (`1−γ̂`, canon-based)
and Uzzi reference-atypicality (canon-free co-reference z vs a degree-preserving null) —
**agree**: per-capita structural novelty has **risen** over 1970–2023, controlling for
team size, field-year volume, and field, permutation-significant. The random-canon
placebo (flat) rules out a reference-growth artifact; α-robustness rules out a
canon-depth artifact. Papers increasingly build **off** the canon — the opposite of the
predicted `V^struct↓`.

## The deeper finding: the rise is **fragmentation**, not individual novelty

The pre-registered test answers *whether* CC6 holds; a follow-on diagnostic answers
*why* the sign is what it is. Recomputing atypicality **within each subfield** (no
canon-accretion artifact):

| | global atypicality slope | within-subfield slope |
|---|---|---|
| concept level-1 (78 subfields) | `−0.64` (p=0.0005) | **`−0.05`** (≈flat, 13× smaller) |
| K=50 SciNCL clusters | `−0.66` (p=0.0005) | **`−0.07`** (≈flat, 9× smaller) |

**Within a niche, combination-novelty barely moves; it's only against the *whole field*
that novelty rises** — because the subfields have drifted apart. So the rising
structural novelty is **cross-subfield fragmentation** (specialization), *not* a growing
periphery individuals draw on and *not* deliberate novelty-seeking. The off-canon result
agrees once read through this lens (controlled: global deviance ↑, local deviance ↓ =
aligning to your niche's canon while drifting from the global one).

**This unifies the whole WS2+WS3 empirical picture under one mechanism:** WS2's *topical*
frontier widening and Phase 2.4's *structural* frontier widening are the **same
fragmentation**, seen through topics vs. citations. And it coexists with canon
concentration with no contradiction: **the field concentrates at the top and fragments
in the middle simultaneously.**

## Reading it back onto WS3 (the interpretation matrix)

- **The canon-deviation `κ` (trade-off) mechanism is falsified** — canon concentration
  does not suppress per-capita structural novelty (Core Claim 6's driver is wrong).
- **The orthogonality reconciliation is supported** — `V` and canon-concentration are
  independent axes (both rise), matching WS2 Phase 2.3 and WS3's pre-authorized
  orthogonality outcome. Henrich↔WWE still dissolved — as orthogonality, not trade-off.
- **The next WS3 rung is now *determined, not guessed*:** the **content/subfield channel**
  the primer deferred (the `τ` layer) — communities with *local* canons whose number
  grows with scale. It reproduces "conventional within-niche, divergent across niches"
  and would generate *both* the topical and structural widening from one added structure.
  This resolves the substrate-sign problem rung 4b exposed (preferential attachment makes
  the model's `V^struct` *fall*; fragmentation is what makes the real one *rise*).

## Honest limits

- **Reference coverage ~50%** (stable over time → doesn't fabricate a trend, but the
  panel is the with-refs subset).
- **The in-sample forward-citation graph is sparse** (8.4% of papers get ≥1 in-sample
  cite in 5y) → the *persistence-weighted* `ν^struct` is noisy; the raw off-canon +
  atypicality carry the headline, not the persistence filter.
- **Physics VIF elevated** (year/volume collinearity in the smaller field) → the pooled +
  CS numbers are the reliable ones; Physics-alone is directional.
- **Atypicality null is full-corpus** (mild look-ahead); the trend is robust to it.
- Within-subfield novelty isn't *exactly* zero (`−0.05`, p<0.01) — a sliver of genuine
  within-niche novelty, but ~90% of the global rise is fragmentation.

## Process (a correction, captured)

The measure/estimator *functions* were TDD'd and committed, but the *analyses* that
produced the findings were first run as ephemeral one-offs — a reproducibility gap the
user flagged. Fixed: `experiments/phase-2.4/{build_panel,analyze}.py` regenerate the
panel + every headline number deterministically. Lesson logged in `tasks/lessons.md`:
*a number I can't regenerate from `git` + `uv run` isn't a result yet.*

## What's next
- **Optional robustness/color:** the SPECTER2 structural arm + topical `V^lat` contrast
  (need the base-1M vectors) — expected to corroborate; not the crux (the ≥2 embedding-
  free measures ARE the pre-registered headline).
- **The capstone:** the synthesis / writeup — the program now has its full arc (WS3 theory
  + two Level-3 anchors; WS2 + Phase 2.4 empirics), converging on **concentration +
  fragmentation**, with **the content/subfield channel** as the concrete next WS3 rung.
