# Rung-0 stimulus appendix — five task families (draft, pre-generation)

> **Status:** draft stimuli, 2026-07-21. Committed **before** any generation call, per the preflight
> discipline: stimuli are frozen and hashed before the run, and **no generation output may be
> examined while revising them.** Companion to `ws1-oss-rung0-build-brief.md` §3 and
> `ws1-oss-reasoning-arm.md` §9.2.
>
> These are **not yet frozen.** They require the §4 preflight below to pass first.

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

Domains are chosen to be mutually distinct and to avoid reusing prior work's task set, so a result
here is not a re-run of an already-observed sample.

---

### F1 — `observability_v1`

**Public brief.** Propose one concise feature for a developer tool that makes multi-agent LLM runs
inspectable after the fact. Active constraints: traces must survive process restarts, must not expose
secrets or raw user data, and must be readable by someone who did not build the workflow.

**Shown items** (adoption counts for cell B in brackets):

1. **Run Timeline:** render each agent step as an ordered span with inputs, tool calls, and elapsed time, persisted to durable storage on write. `[7]`
2. **Redaction Filter:** strip credentials and flagged user fields from traces at capture time, storing a reversible hash for authorized replay. `[4]`
3. **Decision Annotations:** attach a one-line rationale to each agent handoff so a reader can follow why control moved. `[2]`
4. **Trace Diff:** compare two runs of the same workflow and highlight the first step whose output diverged. `[1]`

---

### F2 — `testing_v1`

**Public brief.** Propose one concise feature for a developer tool that verifies multi-agent LLM
workflows before release. Active constraints: checks must run without live production credentials,
must catch regressions introduced by prompt edits, and must report which scenarios remain unexercised.

**Shown items:**

1. **Scenario Matrix:** map committed test scenarios to workflow paths and flag any path no scenario has exercised. `[7]`
2. **Replay Harness:** rerun saved workflows against recorded fixtures with credentials stubbed, comparing outputs to a baseline. `[4]`
3. **Prompt Diff Gate:** block a merge when an edited prompt changes behavior on any pinned regression case. `[2]`
4. **Flake Detector:** repeat nondeterministic cases and report the variance band rather than a single pass or fail. `[1]`

---

### F3 — `cost_v1`

**Public brief.** Propose one concise feature for a developer tool that keeps multi-agent LLM
workflow spending predictable. Active constraints: spend must be attributable to a step, model, and
tool; budget limits must be enforceable before a run starts; and the report must be legible to a
non-engineer.

**Shown items:**

1. **Step Cost Ledger:** attribute every token and tool charge to its originating step, model, and caller, exported as a per-run statement. `[7]`
2. **Pre-Run Estimator:** project a run's cost from its plan and refuse to start when the projection exceeds a set budget. `[4]`
3. **Model Tier Advisor:** flag steps whose output quality would be unchanged on a cheaper model tier, ranked by savings. `[2]`
4. **Spend Digest:** summarize weekly workflow cost by team and feature in plain language for non-engineering readers. `[1]`

---

### F4 — `access_v1`

**Public brief.** Propose one concise feature for a developer tool that controls what data and tools a
multi-agent LLM workflow may reach. Active constraints: capability grants must be scoped per agent
and time-bounded, every grant must leave an auditable record, and revocation must take effect on runs
already in flight.

**Shown items:**

1. **Scoped Capability Token:** issue each agent a time-bounded grant naming exactly the tools and datasets it may touch. `[7]`
2. **Grant Audit Trail:** record who approved each capability, when, and against which justification, queryable after the fact. `[4]`
3. **Live Revocation:** propagate a revoked grant to in-flight runs and halt the affected step rather than letting it finish. `[2]`
4. **Least-Privilege Suggester:** compare granted capabilities against those actually exercised and propose a narrowed grant. `[1]`

---

### F5 — `recovery_v1`

**Public brief.** Propose one concise feature for a developer tool that helps teams recover from
failed multi-agent LLM runs. Active constraints: recovery must not silently discard work already
completed, partial state must be inspectable before any retry, and a retry must be reproducible from
a recorded checkpoint.

**Shown items:**

1. **Checkpoint Resume:** restart a failed run from its last durable step rather than from the beginning, preserving completed work. `[7]`
2. **Partial State Viewer:** expose the intermediate outputs a failed run produced so an operator can judge what is salvageable. `[4]`
3. **Deterministic Retry:** replay a retry against the recorded inputs and seeds so the second attempt is comparable to the first. `[2]`
4. **Blast Radius Report:** list downstream steps and external side effects a failure may have already triggered. `[1]`

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
