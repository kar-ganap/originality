# WS3 Phase 1 · rung 4d retro — the subfield channel: fragmentation

**Branch:** `ws3-phase-1-subfield-channel` · **Window:** 2026-07-07
**Status:** COMPLETE. `subfield.py` reproduces the WS2 Phase-2.4 fingerprint (global
structural novelty rises, within-niche flat, coexists with `H↑`) from one added
structure — niches recombining a shared canon. 9 tests (6 fast + 3 slow), 69 fast total;
ruff + mypy strict clean.
**Plan / pre-registration:** `phase-1-rung4d-subfield-channel-plan.md` (§§0–8 pre-reg;
§9 the post-prototype amendment).

---

## Hypothesis and verdict

Pre-registered (before prototyping): niches as **disjoint `m`-blocks with private
elements** reproduce the fingerprint. **Verdict: the *fingerprint* is reproduced, the
*pre-registered mechanism* is not.** The disjoint-block mechanism was **disconfirmed**
(wrong sign) and replaced, via prototyping, by **shared-canon recombination**. Reported
per the null-results rule; the pre-registration record is preserved in §§0–8.

## What happened — the honest path (four seeded prototypes)

1. **Disjoint blocks → wrong sign, triangulated four ways** (cross-`N` off-canon &
   atypicality, soft geometry, and the faithful within-corpus birth-time frame). Root
   cause: islands are built from *low-degree* elements, so under the degree-preserving
   null a within-niche pair looks *conventional* globally — the model's within/global
   relationship comes out **inverted** vs the data. Not a measurement artifact; the
   faithful frame (the true `panel_year_test` analog) did not rescue it.
2. **Shared-canon recombination → correct sign.** Niches recombine a *shared, high-degree*
   vocabulary; a niche pairs popular elements in *its* way (globally rare, locally
   standard). Global novelty rises (`−0.020`), within flat, the relationship is now
   correct (global more atypical than within), and it is **fragmentation-driven** — the
   K-fixed control never rises.
3. **Bounded-`m` single-lever (`bw = m/E`) → disconfirmed by pre-build verification.**
   Shrinking `bw` makes late niches concentrate on low-degree fringe → conventional →
   wrong sign at every `m`. Caught *before* baking it into the module.
4. **Corrected wiring → confirmed.** `F5` via `K = N/m` (agents-per-niche, the original
   primitive); `bw` a *separate* off-trend crossover lever; a stable high-degree canon
   core. Reproduces the fingerprint (`−0.023`, CI `[−0.033, −0.012]`), within flat
   (`+0.001`), `H_global` `0.94`.

## What the rung establishes

- **The fingerprint from one structure.** Global structural novelty **rises** with scale,
  within-niche **flat**, and canonical concentration `H` **rises alongside** — the field
  *concentrates at the top and fragments in the middle at once*, exactly the WS2 + Phase-2.4
  picture, from the single addition of **niches recombining a shared canon**.
- **Fragmentation is the driver, not recency** — the K-fixed placebo (field grows, `K`
  frozen) does not rise (pre-registered, now *demonstrated*).
- **A tunable crossover.** The sign flip is monotone in niche distinctiveness `bw`, with a
  locatable `bw* ≈ 0.05` — the `λ*` shape of rungs 3/4a. Robust for distinct niches, absent
  for diffuse ones. The effect scales with a *justifiable* knob (subfield specialisation),
  and it is **falsifiable in both directions** (diffuse niches ⇒ no decoupling).
- **`K = N/m` forced** (F5), sub-linear once `m` grows with the corpus.

## Reading it onto WS3 (the reconciliation)

The content/`τ` channel is a **different substrate** from the attachment/`κ` channel
(rungs 3–4b): `κ` acts on citation geometry and drives `H↑`; `τ` places content and
fragments, driving `V^struct↑`. They are **orthogonal** — the reconciliation is
orthogonality, not a `κ`-trade-off. This *is* the resolution of the substrate-sign problem
rung 4b exposed (preferential attachment makes the model's `V^struct` *fall*; fragmentation
is what makes the real one *rise*): the two live on different channels, so both the rise of
`H` and the rise of `V^struct` hold at once. Core Claim 6 / `cc:open` (per-capita `V^struct`
*declines*) is superseded — the primer needs updating.

## Surprises

- Reproducing the *literal* Uzzi-z fingerprint in a toy ABM is genuinely hard — the measure
  is **scale-confounded**, and both islands *and* naive soft-geometry give the wrong sign.
  The signal lives specifically in **high-degree elements recombined rarely**.
- The `V^struct`-rise is *not* individual novelty-seeking and *not* islands — it is a
  measurement-frame effect of a fragmenting shared space, which is exactly what the Phase-2.4
  within-vs-global diagnostic said.
- A single seed is unreliable (one outlier flips positive); the effect is a **mean over
  seeds** — the seed-CI discipline is load-bearing here, not ceremony.

## Honest limits / scope

- **Sign-structure + crossover, not magnitude.** The claim is the qualitative fingerprint
  and the phase boundary (per CC:robust), *not* a parameter-free match to `−0.64` (the
  Uzzi-z is scale-confounded — chasing its magnitude in a minimal ABM is not meaningful).
- **Two off-trend-pinned parameters** (`m` for `K`, `bw` for distinctiveness) — both
  measured, neither fit to the trend; not the "one lever" the amendment first claimed.
- **`H2a` (Strimling floor) retired** — within-flat is now anchored on lens-persistence, not
  the independent-traits `ε/(1−f·m)` floor; Level 3 is not inherited here.
- **Content channel only.** `C` remains the attachment channel's business (rungs 1–4b); this
  substrate does not model cumulative depth.
- The `F2` global-coupling escape-hatch (shared-lens ⇒ consolidation) is argued, not
  demonstrated — a small owed check.

## What's next

- **Update the primer** — `cv-reconciliation-primer.tex`: mark CC6 / `cc:open` superseded
  (per-capita `V^struct` *rises* via fragmentation), and add the content/`τ` channel as the
  orthogonal driver.
- **rung 5 (synthesis)** — fold the two channels (`κ`→`H↑`; `τ`→`V^struct↑`) into the phase
  diagram / Results: concentration + fragmentation as orthogonal axes, the program's arc.
