# Polyphony (WS1 ch.1) — Independent Adversarial Audit

Scope: `/Users/kartikganapathi/Documents/Personal/random_projects/polyphony` only.
Auditor did not produce this work. Read-only; no tracked file modified; no paid API calls.
Git: branch `p-top4-null-and-corrections` @ `de9b7913`, which **is identical to `origin/main`**
(`git rev-list --left-right --count origin/main...HEAD` = `0 0`). The self-correction described as
"in progress" is in fact already on public `main`.

---

## EXECUTIVE SUMMARY (≤7 lines)

- Six-experiment "resists homogenization" headline → **WEAKENED / OVERSTATED as phrased** — and it is
  **not a claim polyphony's own record makes** (grep-negative; no code computes it). Polyphony's record
  refutes *collapse* (a null) plus one *exploratory* rise, concentrated in R4.
- **R4 current status:** consistently framed as a **refuted collapse (negative result)**, NOT a positive
  decoupling replication. The word "decoupl" appears **nowhere**. Its `P_top4` concentration is
  null-reproduced (I ran it): registered `+0.0102` reproduced by a preference-free null at `+0.0153`
  (151%); popularity arm p=0.882 raw / 0.289 normalized. **Concentration = sampling artifact: CONFIRMED.**
- **version-conflict ("the one real effect"):** survived only as **not-confirmed**, single-family, and I
  measured it to be **100% confounded with literal card-name copying** (40/40 contain "Approval Snapshot").
- Single most important finding: the **one surviving positive signal is ~totally confounded** by verbatim
  payload reproduction, and the pre-registered diagnostic that would show this was never reported.

---

## FINDINGS (most severe first)

### [HIGH] The one surviving positive signal (R7C-A 40/40) is ~100% confounded with literal card-name copying — CONFIRMED
- **Claim affected:** "version-conflict is THE ONE real effect"; README:11–14; CrawlWalkRecord.md:297–331;
  web `evidence.ts` `superseded-context` record.
- **Evidence (measured from committed raw artifacts `runs/r7c-a/*evaluation_v2*`):**
  - Superseded cell: the literal payload name **"Approval Snapshot" appears in 40/40** outputs; all 40 are
    judged `deprecated_adopted=true` (`runs/r7c-a-scores.json`).
  - Empty cell (payload not shown): **0/40** contain "Approval Snapshot"; 0/40 adopted.
  - The `deprecated_adopted` label is therefore perfectly collinear with *whether the salient named payload
    was shown*. The 120-token outputs graft "Approval Snapshot … certify the last passing run" onto the
    required feature.
- **What's wrong:** R7CContextQualitySpec.md:116 **pre-registered** a "literal card-name copy rate" secondary
  observable. R7CAResultAmendment.md:41–51 honestly flags the payload-salience confound but calls it a
  *possible* alternative and states the diagnostic "is not reported here or elsewhere." Measured, the
  confound is **near-total (100% literal name reproduction)**, not merely possible. The record's wording
  "strong, label-supported hazard" / "strong version-conflict failure" overstates what a 100%-literal-copy
  cell can support.
- **Mitigant (fairness):** the record already labels this signal `not-confirmed`, task-specific, cross-task
  rule failed, and the amendment does flag the confound. This is a precision/weakening issue on the one
  positive signal, not a hidden positive claim.
- **Confidence: CONFIRMED.**

### [MEDIUM] Public web evidence surface is stale relative to the P_top4 null — CONFIRMED
- **Claim affected:** web `web/src/data/evidence.ts:23–31` (`popularity-feedback`), status `supported`,
  statistic `"+0.0102 top-four echo-concentration trend"`; mirrored in DemoSurfaceSpec.md:106.
- **What's wrong:** `evidence.ts` was last modified in commit `7838158` (**before** the null commits
  `93743e3`/`de9b791`, 2026-07-22) and is unchanged on `main`. It presents `+0.0102` as clean "supported"
  evidence with **no null caveat**. The correction's whole point (CrawlWalkRecord.md:187–204) is that
  `+0.0102` is a **sampler manipulation-check reproduced 151% by a preference-free null**, "never licensed
  any inference about what the agents did." `grep -rn "null|manipulation|sampler"` over `web/src` returns
  nothing substantive.
- **Fairness:** the web *headline* ("popularity increased repeated shared context") is **true** and
  independently corroborated by the R4 exploratory Jaccard diagnostic (+0.1587 [+0.0845,+0.2330]); the null
  *confirms* the sampler concentrates. So the claim is not false — it is stale and omits the reframing. The
  web is **source-only, not deployed** (README:50; web/README:18 — "does not represent the inspector as
  currently hosted"), which lowers exposure.
- **Confidence: CONFIRMED.**

### [MEDIUM/LOW] "Six experiments / CI excludes zero across THREE designs" overstates polyphony's evidence — CONFIRMED (as a mismatch), the claim is parent-program, not polyphony's
- **Claim affected:** the audit's stated headline ("resists homogenization across SIX experiments; CI
  excludes zero in the OPPOSITE direction across THREE designs"). This phrasing lives in the *originality*
  program memory, **not** in polyphony — `grep -riE "six experiment|resist homogeniz|three design|decoupl"`
  over all polyphony docs/code returns **nothing**; `published_evidence.py` computes only the R7C-A 40/40
  readout, no cross-design statistic.
- **What's wrong when mapped onto polyphony's artifacts:** the affirmative anti-homogenization CIs that
  exclude zero are **three diagnostics inside the single R4 experiment**, and all are **exploratory**:
  popularity V slope +0.0090 [+0.0057,+0.0118], residual-V slope +0.0105 [+0.0068,+0.0138], persona-
  persistence gap +0.0332 [+0.0231,+0.0437] (R4ExploratoryAudit.md:120,133–136,116; r4-exploratory-audit.json).
  The **confirmatory** R4 result is a **one-sided refutation of collapse** (summary reports only
  `popularity_v_upper` 0.0158; r4-confirm-summary.json), i.e. a null, not an affirmed rise. And R6, R7A,
  R7C-A each surfaced **task-conditional convergence/harm** (R6 topic-B immediate anchor collapse; R7A
  governance off-task harm −0.207 V; R7C-A eval_v2 40/40). So "three designs" is not supported (it's three
  exploratory diagnostics in one design) and "resists across six" glosses over three conditional
  homogenization/harm findings.
- **Fairness:** polyphony's *own* record does not make this claim; its framing ("diversity rose rather than
  declined" = refuted collapse) is careful. The overclaim is the parent-program compression.
- **Confidence: CONFIRMED.**

### [LOW] `+0.0102` presented as "feedback passed" without the null caveat in frozen/older docs — propagation gap
- WalkR4Preregistration.md:185–187, Implement.md:105, Plan.md:139, DemoSurfaceSpec.md:106 present the
  `+0.0102` feedback-check pass without the null reframing. Not contradictory — CrawlWalkRecord.md:203–204
  states the sentence "stands as written about the actuator." The clarification lives only in
  CrawlWalkRecord + the null module. Consistent with the append-only amendment discipline; noted as a
  propagation gap. **Confidence: CONFIRMED (benign).**

### [LOW] Affirmative "diversity rose" is one-sided-confirmatory / two-sided-exploratory; minor doc nits
- The confirmatory R4 summary reports one-sided upper bounds (refuting collapse); the two-sided CIs that
  exclude zero on the positive side are exploratory. The record is careful about this ("rose rather than
  declined"), so it is a nuance, not a defect. Trivial: null_p_top4.py:13 docstring says replay validated
  to "6e-17"; actual and CrawlWalkRecord say 2.2e-16 (I reproduced 2.22e-16). CrawlWalkRecord.md:79 cites
  "99 passing tests" as a historical snapshot; the suite now has 113. **Confidence: CONFIRMED (immaterial).**

---

## R4 STATUS (precise)

Polyphony's current record (which on `main` already includes the 2026-07-22 amendments) presents R4 as
**the strongest direct test of the original progressive-collapse idea, which FAILED** — a reported negative
result, not a positive finding. WalkR4Preregistration.md:186–187: Claim 3 (collapse) failed
(`collapse_passed=false` in r4-confirm-summary.json); popularity V slope `+0.0090`, upper `+0.0158`.
CrawlWalkRecord.md:138–164 and the "What We Can and Cannot Say" table (line 339) state persona-diverse
collapse is **Not supported**.

**R4 is nowhere presented as a positive decoupling replication of a human study.** The strings
"decoupl", "replicate/replication of [a prior human record]", "six experiments", "resists homogenization"
do **not appear** anywhere in polyphony. This directly resolves the provenance gap the audit was created to
chase: the "R4 reproduces WS2's concentration+fragmentation decoupling on an AI substrate" framing **never
lived in polyphony's record** — it is a parent-program (originality) framing. Polyphony's own record is
cleaner than the thing that cited it.

The `P_top4` concentration (`+0.0102`) has been explicitly **reframed as a manipulation check** and shown to
be a sampling artifact by a matched null (CrawlWalkRecord.md:166–204; src/polyphony/null_p_top4.py;
runs/r4-null-p-top4.json). I reproduced the null (below): registered `+0.0102` → null `+0.0153` (151%);
popularity arm indistinguishable from null (p=0.882 raw, 0.289 normalized). **No stale positive R4
concentration/decoupling claim stands anywhere in polyphony** — the only residual staleness is the web
`evidence.ts` presenting `+0.0102` as "supported" without the null caveat (MEDIUM finding above), and that
claim is about the *sampler* (true), not the ensemble.

---

## AMENDMENT-CONSISTENCY CHECK

All three amendments are **additive** ("no prior text rewritten", commit de9b791) and internally consistent;
cited facts verified against the frozen specs (no invented citations):

- **P_top4 denominator / matched null:** implemented in null_p_top4.py; integrated into CrawlWalkRecord;
  null artifact committed and reproduced bit-exactly. Consistent. Older docs retain the pre-null "feedback
  passed" wording, which the null itself says still "stands about the actuator" (LOW propagation gap).
- **R6 initial-V guard:** R6LevelReanalysisAmendment.md:15–22 carries forward a guard failure. Verified in
  the frozen spec: R6BoundarySpec.md:97 registers the `0.02` round-zero guard; line 146 records it FAILED.
  The amendment correctly confines the level-effect reading to exploratory and **withdraws** the prior
  "bounded resistance including the homogeneous boundary" phrase (line 114; also withdrawn in Plan.md:199).
  Consistent.
- **R7C-A payload confound:** R7CAResultAmendment.md:41–51 flags the n=1 payload/staleness confound and
  names the unreported pre-registered literal-copy diagnostic. Verified: R7CContextQualitySpec.md:116
  registers "literal card-name copy rate" as a secondary observable. Consistent — and my measurement shows
  the confound is near-total (HIGH finding).
- **R7C-A provenance:** R7CAProvenanceAmendment.md corrects the 144-output set from "human review" to
  "independent-LLM cross-adjudication" (labeled by "Fable 5"); no stale "144 human" claim remains
  (grep-clean). Web enforces this discipline with a test: evidence.test.ts:26 forbids
  /prevents|proves|guarantees|validated/.

No earlier doc was found asserting a *pre-correction number that now contradicts* an amendment. The one
real gap is the web/demo surface not yet reflecting the null (MEDIUM).

---

## REPRODUCTION LOG

- `uv sync --extra dev` → OK.
- `uv run pytest -q` → **113 passed in 21.75s** (token-free; many mock-based).
- `uv run python scripts/null_model_p_top4.py` (output redirected to scratch to stay read-only) →
  **matches committed `runs/r4-null-p-top4.json` and CrawlWalkRecord exactly**:
  - replay positive control max |replay−committed| = **2.22e-16**;
  - registered effect observed `+0.0102`, null `+0.0153`, **null reproduces 151%**;
  - popularity raw p=**0.882**, normalized p=**0.289**; uniform raw excess `+0.0055` p=0.003 (Bonferroni-
    surviving), normalized `+0.0353` p=0.041.
- `uv run python scripts/verify_published_evidence.py` → **192 raw artifacts; superseded 40/40; empty 0/40.**
- R4 artifacts vs record: r4-confirm-summary.json exact (`mean_feedback_contrast`=0.01018→+0.0102,
  `collapse_passed`=false, all V slopes/uppers match); r4-exploratory-audit.json matches (persona gap 0.222,
  Jaccard 0.2604).
- Direct raw-artifact check (my own): superseded eval_v2 40/40 literal "Approval Snapshot"; empty 0/40.
- **NOT reproduced (paid guardrail):** all end-to-end model generation (Day0, WALK R1–R4, R5/R5-prime, R6,
  R7A, R7C-A). Verified only against committed artifacts + analysis code. Marked NOT INDEPENDENTLY
  REPRODUCED (requires paid GPT-5.6/Luna run).

---

## COVERAGE GAP (explicit — repo is large)

- Did **not** recompute R5/R5-prime or R7A bootstrap numbers from raw artifacts (per-cell raw dumps are
  git-ignored, ~630 MB); read specs/amendments + published summaries only.
- Did **not** recompute the R6 Stage-A/Stage-B level-reanalysis numbers (needs ignored embedding dumps);
  verified the amendment's logic and that the published summary exists.
- Did **not** inspect the 144-output independent-LLM cross-adjudication or the 18-output human spot-check
  contents; read the provenance amendment only.
- Measured the R7C-A literal-copy confound on **evaluation_v2 only** (the one positive cell); did not sweep
  all six task families.
- Did **not** individually audit every one of ~30 src modules / ~30 test files; ran the full suite (pass)
  and read the load-bearing modules (null_p_top4, published_evidence) closely; skimmed web App.tsx/scenarios.
- Did **not** build/run the web demo; audited its committed source and git provenance.

---

## WHAT SURVIVES CLEANLY

- **The P_top4 matched null** — well-designed (replay positive control at 2e-16, preference-removed matched
  nulls, sample-size-matched empirical p), bit-exactly reproducible, honest conclusion. Exemplary.
- **R4 collapse refutation** — artifacts match the record exactly; `collapse_passed=false`; solid negative
  result. No positive R4 decoupling/concentration claim survives anywhere.
- **The amendment trail** — additive, internally consistent, citations real, withdrawn phrases explicitly
  retracted, provenance mislabel corrected.
- **Public-surface discipline** — Context Inspector is deterministic/no-network/carefully caveated; a test
  forbids overclaim words; README honest that nothing is deployed and that vendor/ is prior work.
- **Reproduction hygiene** — seeds pinned (null seed 20260722; bootstraps committed), token-free verifiers
  published, evidence tier reconciles to raw outputs (40/40, 192).
