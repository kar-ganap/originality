# Whitespace 1 — LLM Multi-Agent Simulation (ACTIVE)

**Active since 2026-07-21.** WS1 is the program's *mechanistic / counterfactual* leg: it
manipulates the actuator that WS2 could only observe and WS3 only theorize.

## Structure — two chapters

| chapter | substrate | code lives | status |
|---|---|---|---|
| **1 — Polyphony** | GPT-5.6, in-context multi-agent | `../../polyphony` (**public**) | **complete** |
| **2 — OSS / cross-model arm** | OSS reasoning models + Claude | `src/whitespace1/` (here, private) | designed, not built |

**Why chapter 1's code is external.** Polyphony was published
(`github.com/kar-ganap/polyphony`), so it is firewalled from the program and lives in its own repo.
Chapter 2 is private program science and lives here, like WS2 and WS3. If it is ever published,
extract a sanitized repo at that point — the same route Polyphony took.

## Chapter 1 result (complete)

Role-diverse LLM ensembles **did not** homogenize under shared-context conditioning, across six
pre-registered experiments and every actuator tried. The one real effect was version-conflict
contamination (superseded context → deprecated-constraint adoption, 40/40 vs 0/40 empty), which
failed its cross-task rule.

**Correction (2026-07-22) — withdrawn, and now on positive evidence.** This section previously said
R4 *reproduced WS2's decoupling signature* on an AI substrate (concentration↑ and diversity↑
together). It does not. The claim was never in polyphony's own record; it originated here.

`P_top4` is a fixed-`k` share of a catalog growing 13→48 items at measurement, so its denominator
inflates by design and it falls in both arms (uniform −0.0390, popularity −0.0288). A matched null —
R4's exact generative process with item preference removed, replay-validated against every committed
run to 2e-16 — settles the rest (`../../polyphony/scripts/null_model_p_top4.py`):

- **The popularity arm's concentration is indistinguishable from the null**, raw (p = 0.882) and
  normalized (p = 0.289). No ensemble contribution is detectable.
- **The registered +0.0102 is over-reproduced by the null at +0.0153 (151%)** with zero agent
  preference. It measured the sampler, not the ensemble — a live-actuator manipulation check.
- Only the *uniform* arm carries a real excess (+0.0055 raw, p = 0.003, Bonferroni-surviving).
  Post-hoc, so a hypothesis for a future pre-registration, not a result.

**There is no ensemble-driven concentration↑ to pair with the diversity↑.** The AI-substrate
decoupling is **refuted for the arm it was claimed on**, not merely unmeasured — which also removes
the cross-substrate capstone this chapter was carrying.

## Chapter 2 (this directory)

Adjudicates whether chapter 1's null is real or an artifact of measuring only the layer that talks,
by adding a **reasoning-diversity** layer that proprietary APIs structurally cannot expose. It is
also the program's only venue for a **causal** test of WS3's C/V theory, because λ (conformity) is a
literal experimental knob in a multi-agent ensemble rather than an unvalidated mapping.

- **Design note:** [`docs/ws1-oss-reasoning-arm.md`](docs/ws1-oss-reasoning-arm.md) — the build
  ladder, estimands, and the §9 pre-registration.
- **Rung-0 build brief:** [`docs/ws1-oss-rung0-build-brief.md`](docs/ws1-oss-rung0-build-brief.md)
  — the locked, executable first step (~$2.80).
- **Stimuli:** [`docs/ws1-oss-rung0-stimuli.md`](docs/ws1-oss-rung0-stimuli.md) — five task
  families, committed pre-generation, pending preflight.
- **Provenance:** [`docs/ws1-hackathon-plan.md`](docs/ws1-hackathon-plan.md) — chapter 1's original
  blueprint. **Superseded:** its diversity-thermostat premise was falsified. Kept as the record.

## Build & test

```bash
cd whitespace_1
uv sync --extra dev
make test          # pytest
make lint          # ruff
make typecheck     # mypy strict
```

## References

- Program context: `../docs/program/research_program_overview.md`
- Program principles: `../docs/program/desiderata.md`
- The theory this arm tests causally: `../whitespace_3/docs/conceptual.md`
- The human-side result it bridges to: `../whitespace_2/`
