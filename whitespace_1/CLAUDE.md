# Whitespace 1 — LLM Multi-Agent Simulation (chapter 2: the OSS adjudication arm)

## Where this sits

WS1 is the program's **mechanistic / counterfactual** leg. Chapter 1 (Polyphony, GPT-5.6, in-context)
is **complete and public** at `../../polyphony`. Chapter 2 — this directory — is private program
science. See `README.md` for the split and `docs/ws1-oss-reasoning-arm.md` for the full design.

## The question

Polyphony found that role-diverse LLM ensembles **did not** homogenize under shared-context
conditioning, across six pre-registered experiments. Chapter 2 asks:

> **Is that null a fact about the system, or an artifact of measuring only the layer that talks?**

Measure two layers — `V_output` (final answers) and `V_reason` (reasoning *strategies*, extracted as
skeletons, never raw traces). Both outcomes pay: if reasoning collapses while outputs hold, the
headline null is a measurement artifact; if both hold, the null deepens.

Chapter 2 is also the program's **only venue for a causal test of WS3's C/V theory**, because λ
(conformity) is a literal experimental knob here, not the unvalidated κ→λ mapping that made the
recursion arm unidentifiable.

## Ground rules specific to this whitespace

1. **Rung 0 is LOCKED.** Build to `docs/ws1-oss-rung0-build-brief.md` exactly. Do not redesign it.
2. **The ladder gates itself.** Each rung's gate must pass before the next is built. A rung-0 failure
   *ends* the ladder and is published as a floor result — that is a valid outcome, not a setback.
3. **Register every constant.** Any threshold, margin, or floor not in the design note needs a dated
   change-log entry. Silent post-hoc constants are the specific failure this arm is built to avoid.
4. **No gate substitution.** If a pre-registered gate fails, report the failure. Never promote a
   different statistic to "the gate," never demote a failed criterion to a "sanity check."
5. **Level and slope are both primary**, applied symmetrically (design note §6). A slope-only
   estimand has hidden a real effect three times in this program.
6. **Never gate on participation-ratio effective dimensionality.** It is exactly scale-invariant, so
   it is structurally blind to uniform contraction — i.e. to collapse. Report it as a secondary only.
7. **The engine is token-free and mockable.** Only generation calls hit the network; `make check`
   must never spend money (`-m 'not live'` is the default).
8. **Log tokens on every call.** Rung 0 doubles as the cost calibration for later rungs.

## The trap (read `docs/ws1-oss-rung0-build-brief.md` §2)

Homogeneous personas + a dominant shared item produce an ~80% V collapse that is **parroting**, not
conformity — diversity zeroed by construction. Role diversity must be held fixed and verified, and
`anchor_alignment` must stay below 0.65, or a "collapse" means nothing.

## Build & test

```bash
uv sync --extra dev
make check        # lint + typecheck + test; never spends money
make test-live    # costs money; only when explicitly running an experiment
```

## Key references

- Design + pre-registration: `docs/ws1-oss-reasoning-arm.md`
- Locked first step: `docs/ws1-oss-rung0-build-brief.md`
- Stimuli (pre-generation, pending preflight): `docs/ws1-oss-rung0-stimuli.md`
- Chapter 1's superseded blueprint: `docs/ws1-hackathon-plan.md`
- Program principles: `../docs/program/desiderata.md`
- The theory under causal test: `../whitespace_3/docs/conceptual.md`
