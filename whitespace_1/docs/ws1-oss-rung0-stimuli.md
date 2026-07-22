# Rung-0 stimulus appendix — five task families (FROZEN)

> **Status: FROZEN 2026-07-21 — preflight PASSED (6/6).**
> Stimulus set hash `7940ad166f80cfacad44233f6d2d9ab0c5ca666e85bde68e98551139c3cbe25a`.
> Revising any stimulus from here requires a dated change-log entry and invalidates runs made
> against the prior version. Companion to `ws1-oss-rung0-build-brief.md` §3 and
> `ws1-oss-reasoning-arm.md` §9.2. Source of truth is `src/whitespace1/stimuli.py`; reproduce with
> `uv run python experiments/run_preflight.py`.
>
> *On the "no generation output may be examined while revising stimuli" rule: C6 is by
> construction an outcome check on **ablation** pilots, so its output legitimately informs
> stimulus revision. **No treatment cell (A or B) has been run.** The freeze binds from here.*

## 0. Preflight record (2026-07-21)

Three real defects were caught, all in the stimuli or the criteria — **`CEILING_MIN` was never
moved.** Validation that the target itself was right: `testing_v1` now measures **0.405 [0.38–0.42]**
against prior work's role-diverse ablation of **0.408–0.431**, so the calibration transfers and the
earlier failures were genuine stimulus defects rather than a mis-set threshold.

| # | defect | fix |
|---|---|---|
| **C4** | Cell B annotated items with adoption counts, cell A annotated none → B was +16 words in every family (9.1–10.1% skew). A B-vs-A difference could have been prompt length, not actuator form. | Structural parity: both cells render `- {text} ({annotation})`; only the annotation's meaning differs. Skew → 1.1–1.3%. |
| **C1** | The check *rewarded* briefs for enumerating ≥3 constraint clauses. That was backwards — an enumerated checklist hands every role the same answer. All five roles produced near-identical proposals (ablation V 0.14–0.24). | **Inverted:** briefs must state the problem domain *without* enumerating solution requirements, ≤30 words. All five briefs rewritten as open prompts. |
| **C3** | Compared brief-to-brief distance against card-to-card. Incommensurable — briefs share a deliberately identical stem, so their distance is boilerplate-dominated. The test could not pass however distinct the families were. | **Re-specified** onto card-to-card on both sides. Now passes: between-family 0.701 > within-family 0.631. |

A fourth fix came from matching prior work's form, which the design principle already required:
roles carry a **viewpoint**, not a bare job title (`"Reliability engineer: Failure modes,
observability, rollback paths, and operations."`). Bare titles are a much weaker diversity signal.
Effect on ablation V, cumulative across all fixes:

```
                    original   open briefs   + viewpoint roles (3 blocks)
observability_v1     0.236        0.291        0.368 [0.35-0.39]  PASS
testing_v1           0.209        0.323        0.405 [0.38-0.42]  PASS
access_v1            0.221        0.250        0.376 [0.36-0.40]  PASS
cost_v1              0.179        0.163        0.279 [0.26-0.31]  FAIL
recovery_v1          0.142        0.209        0.273 [0.24-0.31]  FAIL
```

**Resolution — two families replaced (not tuned).** `cost_v1` and `recovery_v1` are genuinely
narrow domains: cost converges on "attribute the spend," recovery on "checkpoint and replay," so
every role lands in the same place. Their ranges did not overlap the passing families', so this was
not sampling noise. They were replaced by **`collaboration_v1`** and **`iteration_v1`**, chosen for
multi-facetedness rather than reworded. Final run, all six criteria passing:

```
                     ablation V (3 blocks)
observability_v1     0.380 [0.38-0.39]  PASS
testing_v1           0.404 [0.38-0.43]  PASS
collaboration_v1     0.508 [0.47-0.55]  PASS   <- replacement, highest of all five
access_v1            0.369 [0.34-0.41]  PASS
iteration_v1         0.355 [0.33-0.40]  PASS   <- replacement, clears with least margin
```

**Two honest caveats on the passing set.** (1) `access_v1` and `iteration_v1` have individual blocks
dipping to 0.34 and 0.33, below the 0.35 floor; the criterion is on the 3-block mean, as registered,
and the means clear — but both sit near the boundary and should be watched in the run proper.
(2) `collaboration_v1` at 0.508 sits *above* the ~0.42 calibration reference, so the ensemble spans
0.355–0.508 (a 43% spread). Rung 0's margin is **relative** to each family's own ablation, so this
is handled by construction, but per-family baselines must be reported alongside any pooled figure.

## 1. Design constraints these stimuli must satisfy

**Form is held constant with prior work so the calibration transfers.** Rung 0's margins (V ceiling
≈0.42, alignment ceiling 0.65) come from runs whose task form was *"propose one concise feature for a
developer tool that…"* with five role-diverse agents and a ~120-token cap. **Keep that form**; vary
only the domain across the five families. Changing the form would invalidate the constants.

**The two actuator cells must show the identical item set.** Cell A (instruction-λ) and cell B
(payoff-λ) differ **only in framing** — A adds a conformity directive, B adds adoption counts and a
payoff frame. If the item sets differed, the form-vs-strength contrast would be confounded with
content. Cell C (ablation) shows no items.

**Four items shown per cell.** This makes the shown set directly commensurable with the
"top-four echo-concentration" measure that prior work used to report +0.0102, which is what the
`H_endogenous / H*` comparison depends on.

**Each family must give all five roles a genuine angle** — Reliability engineer, Product designer,
Security reviewer, Learning scientist, Cost analyst. A brief that only one role can answer will
collapse V for reasons unrelated to conformity.

**Cards must be plausible and semantically spread.** Strawman cards make conformity look weak; a
narrow card set makes exposure look strong for the wrong reason. Cards are **14–24 words**, uniform
`Feature Name: mechanism` format.

> *Spec correction 2026-07-21:* this originally said 20–30 words, which the drafted cards below
> violate (measured range 14–23). The range is relaxed to 14–24 to match the drafted set rather than
> padding cards to hit an arbitrary target — length is controlled by the **balance** criterion in §4,
> not by an absolute floor. Preflight criterion 4 is authoritative.

## 2. The five families

*Generated from `src/whitespace1/stimuli.py`, which is the source of truth. Frozen set hash `7940ad166f80cfacad44233f6d2d9ab0c5ca666e85bde68e98551139c3cbe25a`.*

Domains are chosen to be mutually distinct and multi-faceted enough that the five roles pull
apart. `cost_v1` and `recovery_v1` were **replaced** after preflight (§0): each had one
obvious answer, so every role converged on it.

---

### `observability_v1`

**Public brief.** Propose one concise feature for a developer tool that helps teams inspect and understand what actually happened during a multi-agent LLM run.

**Shown items** (adoption counts, used in cell B only, in brackets):

1. **Run Timeline:** render each agent step as an ordered span with inputs, tool calls, and elapsed time, persisted to durable storage on write. `[7]`
2. **Redaction Filter:** strip credentials and flagged user fields from traces at capture time, storing a reversible hash for authorized replay. `[4]`
3. **Decision Annotations:** attach a one-line rationale to each agent handoff so a reader can follow why control moved. `[2]`
4. **Trace Diff:** compare two runs of the same workflow and highlight the first step whose output diverged. `[1]`

---

### `testing_v1`

**Public brief.** Propose one concise feature for a developer tool that helps teams build confidence in a multi-agent LLM workflow before they ship it.

**Shown items** (adoption counts, used in cell B only, in brackets):

1. **Scenario Matrix:** map committed test scenarios to workflow paths and flag any path no scenario has exercised. `[7]`
2. **Replay Harness:** rerun saved workflows against recorded fixtures with credentials stubbed, comparing outputs to a baseline. `[4]`
3. **Prompt Diff Gate:** block a merge when an edited prompt changes behavior on any pinned regression case. `[2]`
4. **Flake Detector:** repeat nondeterministic cases and report the variance band rather than a single pass or fail. `[1]`

---

### `collaboration_v1`

**Public brief.** Propose one concise feature for a developer tool that helps several people work together on the same multi-agent LLM workflow.

**Shown items** (adoption counts, used in cell B only, in brackets):

1. **Workflow Branching:** let each person develop a variant of the same workflow in isolation and merge changes deliberately. `[7]`
2. **Change Review:** require a second person to approve edits to agent prompts and tool wiring before they land. `[4]`
3. **Ownership Map:** record who is responsible for each agent, prompt, and tool so questions reach the right person. `[2]`
4. **Shared Scratchpad:** capture in-progress notes and open questions alongside the workflow so context survives between people. `[1]`

---

### `access_v1`

**Public brief.** Propose one concise feature for a developer tool that helps teams decide and enforce what a multi-agent LLM workflow is allowed to do.

**Shown items** (adoption counts, used in cell B only, in brackets):

1. **Scoped Capability Token:** issue each agent a time-bounded grant naming exactly the tools and datasets it may touch. `[7]`
2. **Grant Audit Trail:** record who approved each capability, when, and against which justification, queryable after the fact. `[4]`
3. **Live Revocation:** propagate a revoked grant to in-flight runs and halt the affected step rather than letting it finish. `[2]`
4. **Least-Privilege Suggester:** compare granted capabilities against those actually exercised and propose a narrowed grant. `[1]`

---

### `iteration_v1`

**Public brief.** Propose one concise feature for a developer tool that helps teams learn from how their multi-agent LLM workflows behave in production.

**Shown items** (adoption counts, used in cell B only, in brackets):

1. **Behavior Trends:** chart how a workflow's outputs and failure patterns shift across releases so drift becomes visible. `[7]`
2. **Production Sampler:** collect a representative sample of real runs and surface the ones most worth examining closely. `[4]`
3. **Change Impact:** link each workflow edit to the behavior shift that followed it in production. `[2]`
4. **Hypothesis Log:** record what a team expected from a change and whether the observed behavior matched. `[1]`

---

## 3. Cell rendering (identical across families)

Implemented in `src/whitespace1/stimuli.py` (`render_cell`), which is the source of truth.

- **Cell C — ablation.** Public brief + role + format instruction. Visible context field reads:
  `Shared context: No prior proposals are available.`
- **Cell A — instruction-λ=1.** Identical, plus the four items under
  `Leading approaches proposed by other teams (list position):`, each annotated `(position N)`,
  and the directive:
  *"Your proposal should align with the leading approaches shown in the list above."*
- **Cell B — payoff-λ=1.** Identical, plus the **same four items** under
  `Proposals adopted by other teams (adoption count):`, each annotated `(adopted by N)`, and the
  payoff frame: *"Proposals similar to those already adopted are more likely to be adopted."*

**Structural parity (added 2026-07-21 after preflight C4 failed).** Both cells render every item as
`- {card text} ({annotation})`; **only the annotation's meaning differs** — list position vs adoption
count. The first draft annotated items in B only, which made B systematically **+16 words** longer in
every family (9.1–10.1% skew; `testing_v1` breached the registered ±10% tolerance). That is a real
confound: a B-vs-A difference could then be prompt length rather than actuator form, which defeats
the contrast's purpose. Parity brings the skew to **1.1–1.3%**. The threshold was **not** relaxed —
the stimuli were fixed.

Adoption counts `[7, 4, 2, 1]` are deliberately skewed to give preferential attachment a clear
target. **Item order must be a committed shuffle per block**, so cell A's `position` annotation
carries no rank information; without the shuffle, position would proxy adoption rank and leak the
manipulation into A.

## 4. Preflight — must pass before freezing

Run these as token-free or embedding-only checks and commit the results:

1. **Role coverage.** Each of the five roles can produce a substantively different proposal for each
   brief. Check by construction and by a blinded read; a family failing this is replaced, not tuned.
2. **Card spread.** Within-family pairwise cosine distance across the four cards is **≥ the
   cross-family card distance floor** — cards must not be near-duplicates, or exposure narrows the
   space for trivial reasons.
3. **Family separation.** Between-family brief distance exceeds within-family card distance, so the
   five families are genuinely distinct samples.
4. **Length balance.** Cards 14–24 words; briefs within ±15% of each other in token count; A and B
   prompts within ±10% of each other after the framing text is added.
5. **No leakage.** Adoption counts, condition labels, and the words *conformity*, *diversity*,
   *collapse*, and *align* (outside cell A's directive itself) never appear in any brief or card.
6. **Ceiling sanity.** A single ablation pilot block per family lands `V_output` near the calibrated
   ceiling (≈0.42). A family whose ablation V is already low has a floor problem and is replaced —
   otherwise the ≥20% margin is measured against the wrong baseline.

**Freeze rule.** Once preflight passes, hash the stimulus set and the call schedule and commit both.
After that, revising stimuli requires a dated change-log entry and invalidates any run already made
against the prior version. No stimulus revision may be informed by generation output.
