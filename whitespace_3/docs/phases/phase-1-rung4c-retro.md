# WS3 Phase 1 · rung 4c Retro — Bounded role models, the Strimling Level-3 anchor

**Phase:** 1 (the ABM core), rung 4c · **Branch:** `ws3-phase-1-network-topology`
**Window:** 2026-07-07 · **Status:** COMPLETE. `roles.py` (bounded-role-model
accumulation of independent traits); Strimling/Enquist reproduced at **Level 3**;
9 rung-4c tests, 74 total; ruff + mypy strict clean.

---

## Hypotheses (pre-registered) and verdicts

| # | Pre-registered | Verdict |
|---|---|---|
| **H1** | Strimling `λ_f = ε/(1−f·n)` = `U/(1−β)` at `n=1`; match the number **0.2** at ε=0.1,f=0.5. | **Confirmed (Level 3).** `λ_f = 0.20/0.20/0.20` across N=50/150/400. |
| **H2** | `N`-independence of per-individual culture. | **Confirmed.** ratio across N≈1.0. |
| **H3** | Closed form `λ_f = ε/(1−f·n)` across `(ε,f,n)`. | **Confirmed** (sub-critical; ~13% bias only right at `f·n→1`). |
| **H4** | Enquist threshold `f·n=1`: sub-critical finite/N-indep, super-critical runaway. | **Confirmed.** `f·n=0.6`→flat; `f·n=1.4`→`75→480` in N. |
| **H5** | Population repertoire `λ_p` grows ~linearly in `N`. | **Confirmed.** individual saturates, population grows. |

## The result: the program's second Level-3 anchor

`roles.py` reproduces **Strimling et al. 2009's** per-individual equilibrium
`λ_f = U/(1−β)` — including the *specific number* `0.2` (ε=0.1, f=0.5, n=1),
`N`-independent across an 8× population range — and **Enquist et al. 2010's** critical
threshold `p·n>1` (our `f·n=1`). This is the **Henrich→Mesoudi pattern, again**:
Strimling's own 2009 PDF is genuinely inaccessible (no OA copy exists), but the
equilibrium is stated and *explicitly attributed to Strimling* in the open,
peer-reviewed **Lehmann–Aoki–Feldman 2011** (eq 3.4), and the threshold is read
verbatim from the open primary **Enquist 2010**. Documented as such (no overclaim that
we opened Strimling's PDF). Our `n`-generalized count form `ε/(1−f·n)` is the *synthesis*
of the two — labelled our own (Level 2, derived + verified), with Level 3 anchored at
`n=1` (Strimling number) and at the threshold (Enquist).

## The unifying principle (the rung-2b resolution)

**Bounded/saturating culture is a *sub-criticality* phenomenon** (`f·n < 1`), the exact
mirror of rung 2b's runaway. Below the line, each trait is lost faster than it spreads,
so constant innovation balances loss at a finite, `N`-independent level. Above it,
traits self-sustain and culture runs away, capped only by `N` (rung 2b's immortal
traits / ballistic `C`). So "well-mixing → no saturation" was **never about unbounded
redundancy — it was super-critical transmission.** One principle now explains the whole
arc from rung 2b to here.

## The journey (why persistence mattered)

rung 4c began as "spatial network topology → `C` saturation + Strimling." Plan-first
verification **disconfirmed** it: on a connected graph traits *percolate* and persist,
so no `N`-independent equilibrium (per-agent count grew with `N` even at ρ=2). I was
ready to document Strimling as an unreachable anchor. The user chose to **pursue it
anyway** (option 2). That was right: the *nearby correct* mechanism — random `n`-role-
model sampling (frequency-dependent) in the sub-critical regime — reproduces Strimling
cleanly, and a targeted secondary-source search (Strimling PDF closed → LAF 2011 +
Enquist 2010 open) recovered the Level-3 numbers. A disconfirmed premise had a correct
mechanism one step away.

## Representation

`roles.py` — flat independent traits (no prereqs); each generation every agent learns
from `n` **randomly-sampled models excluding self** (⇒ `r=0`, no memory — Strimling's
headline), acquiring each trait with `1−(1−f)^m`; innovation at `ε`; dead traits pruned
(behavior-preserving speedup). `strimling_lambda_f(ε,f,n)` exposes the closed form.
This is a *distinct*, minimal model — no `κ`, no depth `C`, no spatial network (the
bounding structure is role-model sampling, not topology).

## Validation gates

9 rung-4c tests (determinism; the Level-3 number; the closed form; `N`-independence;
the Enquist threshold; population growth; the formula helper; validation; slow
sensitivity sweep). 74 total. ruff + mypy strict clean; pre-push gate green.

## Carry-forward

Phase 1's rung ladder now spans: transmission (Henrich, **L3**), innovation → `V`,
`κ` → the crossover, endogenous `H`, the channel/WS2-signature, and bounded roles
(Strimling/Enquist, **L3**). Open threads for a later phase:
- **Memory extension** `λ_f = U/(1−β−r)` (LAF's `r>0`) — a second Strimling number
  (`1.0` at r=0.4) if a memory term is added; documented as a possible extension.
- **Depth `C` under sub-criticality** — the low-degree `C`-saturation seen in the
  spatial prototype, if a depth version of the bounded model is wanted.
- **rung 5** — synthesis / phase diagram / the paper's Results section.
