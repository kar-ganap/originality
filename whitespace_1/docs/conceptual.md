# Whitespace 1 — Conceptual (compass)

**Active since 2026-07-21.** This is the compass for WS1's *mechanistic / counterfactual* leg.
Detailed design lives in `ws1-oss-reasoning-arm.md`; this document says why the whitespace exists and
what would settle it.

## Why WS1 exists

WS2 (human, observational) reported that intellectual plurality **decouples** from concentration: a
citation canon concentrates while the semantic frontier fragments, and the two are orthogonal — both
window-robust. WS3 (theory) explains it with a C/V model whose conformity parameter λ has a crossover
λ\* separating a V-favouring regime from a C-favouring one.

> **Status correction (2026-07-22).** The premise above is weaker than it reads, and an independent
> audit of each arm found the weakness at both ends. **WS2's concentration leg:** a uniform-random-
> attachment null carrying no canon at all reproduces ~92% of the `ref_gini` trend, the trend
> reverses post-2000 (t = −2.18), and the pre-registered substrate gate (age-restricted Gini)
> declined — it was computed and not reported, and its own pre-registration says a decline means the
> substrate is broken and the primary test must not be interpreted. **WS3's crossover:** λ\*≈0.09
> carries no confidence interval and interpolates between slopes individually indistinguishable from
> zero; at N=200–1500 the V-slope CI straddles zero at λ = 0, 0.1, and 0.25 while ∂C/∂logN = 0.0000
> exactly, so neither half of "same lever, opposite signs" is statistically present at scale.
> The fragmentation leg (mean pairwise cosine rising across three embedding families in CS) and the
> demographic leg both survive. What does *not* currently stand is the orthogonality that names this
> whitespace. **Read the rest of this document as the design that was motivated by that premise, not
> as a claim that the premise holds.** Settling it is what the null-model suite is for.

Neither leg can establish **causation**. You cannot manipulate conformity in a scientific field: the
human record is what it is. WS1 supplies the missing arm — a system where the actuator is a knob.

## The two chapters

**Chapter 1 (Polyphony — complete, public).** Asked whether shared-context conditioning homogenizes a
role-diverse LLM ensemble. Across six pre-registered experiments and every actuator tried, **it did
not**. The one real effect was version-conflict contamination, which failed its cross-task rule.

The result that matters most for the program: R4 showed **concentration↑ and diversity↑
simultaneously**, with the mechanism confirmed live in between — the same signature WS2 found in the
human corpus, now on an AI substrate where the actuator was *driven* rather than observed. That is
the program's cross-substrate capstone.

**Chapter 2 (this whitespace).** Two jobs.

1. **Adjudicate chapter 1's null.** Output-only diversity compresses away reasoning: agents that
   reason differently to the same stated conclusion read as identical. Open reasoning models and
   Claude's extended thinking expose the trace, so the reasoning layer can be measured directly. If
   `V_reason` collapses while `V_output` holds, the headline null is a measurement artifact. If both
   hold, the null deepens into a robust finding.
2. **Give the C/V theory its first causal test.** In a multi-agent ensemble λ is a literal knob —
   exposure strength, conformity directive, adoption payoff — with no unvalidated units-conversion in
   between. The recursion arm (a sibling project) could reach conformity only through a data-fraction
   → conformity-weight identity it could not justify, and its theory test was unidentifiable as a
   result. This substrate has no such gap.

## What would settle it

The design is a self-gating ladder (`ws1-oss-reasoning-arm.md` §4). Its first question is not "does
collapse happen" but **"is collapse reachable at all"** — because the program has now bracketed the
transition from both sides without ever straddling it: the recursion arm sat deep in the collapse
phase everywhere except its zero control; chapter 1 sat deep in the sustain phase throughout. You
cannot study a transition from inside one phase.

So rung 0 imposes maximal conformity and asks whether output diversity moves at all. A **floor
result** — no accessible collapse phase under two independent actuator forms — is a genuine finding
and ends the ladder honestly. Only if collapse is reachable do the reasoning layer and the λ\*
straddling become answerable questions.

## Non-goals

- Not a claim that in-context homogenization and weight-level model collapse share a mechanism. That
  contrast is qualitative; the conditioning strengths were never matched.
- Not a validation of C/V's crossover **location** — that does not survive the units question. Only
  **shift directions** do.
- Not a demonstration project. Chapter 1 already demonstrated what this substrate does; chapter 2
  exists to adjudicate and to test a theory, which are different experiments with different designs.
