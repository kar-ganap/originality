# Independent Cross-Program Audit — Consolidated Findings
**Date:** 2026-07-24. **Scope:** WS1, WS2, WS3 (originality), canary, polyphony.
**Method:** five independent adversarial auditors (one per body of work, blind to each other),
read-only, token-free reproduction only (no paid API/Modal). Consolidator (main agent)
personally re-verified the four highest-stakes findings. Per-body reports: `ws1.md ws2.md ws3.md canary.md polyphony.md`.

---

## BOTTOM LINE

**No surviving headline collapsed, and no NEW catastrophic defect was found.** Unlike the last
audit — which discovered the defects the authors had missed — this time the authors had **already
found and honestly recorded** the three big ones (WS2 ref_gini withdrawal, WS3 crossover-absence,
polyphony R4 refutation + P_top4 null). The auditors independently **reproduced those self-corrections
and found them sound** (in WS2's case "more rigorous than the work it corrects"). The self-correction
machinery worked.

**What's left is not a hidden false headline. It is:** (1) one genuine cross-body **overclaim** in how
the parent program *compresses* polyphony; (2) one **surviving** empirical claim (WS2 semantic leg)
that is narrower than stated; (3) **propagation/hygiene drift** — corrected narratives not fully
reaching the paper-bound artifacts and top-level summaries.

**The auditors' one shared ERROR (corrected):** WS2 and WS3 both flagged [HIGH] "corrections are
unmerged; `main` still carries the withdrawn claim." **False alarm** — they read a stale *local* `main`.
`origin/main` (canonical) has everything: 3 withdrawn markers in top CLAUDE.md, 5 in WS2's, all three
null/replacement modules present, correction files byte-identical to HEAD. Real residue: **local `main`
is 40 commits behind `origin/main`** → `git fetch` / `git branch -f main origin/main`.

---

## TIER 1 — Overclaims that would misrepresent the work in a paper (fix BEFORE writing)

### T1.1 — The AI-arm resilience result over-compresses polyphony. [CONFIRMED by consolidator: grep-negative]
- The program framings **"role-diverse ensembles resist homogenization across SIX experiments / CI
  excludes zero across THREE designs"** and **"R4 reproduces WS2's concentration+fragmentation
  DECOUPLING on an AI substrate"** appear **nowhere in polyphony** (`git grep` for `six experiment |
  three design | resist(s) homogeni | decoupl` = 0 hits; `published_evidence.py` computes no such statistic).
- Polyphony's ACTUAL record: R4's confirmatory result is a **one-sided refutation of *collapse*** (a
  null — "diversity rose rather than declined"). The affirmative anti-homogenization CIs that exclude
  zero are **three EXPLORATORY diagnostics inside the single R4 experiment** (pop-V slope +0.0090,
  residual-V +0.0105, persona-persistence gap +0.0332). Other experiments show **task-conditional
  convergence/harm** (R6 topic-B anchor collapse; R7A governance off-task −0.207 V; R7C-A 40/40).
- Note: originality's *top-level* CLAUDE.md is largely self-aware here (it already says the R4
  replication "originated in this repo, not polyphony" and calls the leg **refuted**). The overclaim
  lives in (a) the "What still stands → across three designs" bullet and (b) the **stale memory file**.

### T1.2 — "version-conflict is the one real effect" is undercut by a near-total confound. [auditor CONFIRMED from raw artifacts]
- The one surviving positive polyphony signal (R7C-A, 40/40 "deprecated_adopted") is **~100% confounded
  with literal card-name copying**: the payload string "Approval Snapshot" appears in **40/40** superseded
  outputs and **0/40** empty-cell outputs — the label is collinear with *whether the named payload was shown*.
- A **pre-registered** "literal card-name copy rate" diagnostic (`R7CContextQualitySpec.md:116`) was **never
  reported**. Polyphony already labels this signal `not-confirmed`/task-specific and flags the confound as
  *possible*; measured, it is near-total. Don't lean on version-conflict as a robust effect.

### T1.3 — Stale memory feeds future sessions. [consolidator]
- `memory/project_polyphony_findings.md` still asserts "R4 reproduces WS2's DECOUPLING (the correct
  framing)", "resist homogenization across six experiments", and "version-conflict is the one real effect"
  — all three now over-claims contradicted by T1.1/T1.2 and by originality's own "refuted" verdict. **Update it.**

### T1.4 — WS2 semantic-fragmentation leg is narrower than "three families." [CONFIRMED by consolidator from artifacts]
- Raw perm-test: CS mean-pairwise-cosine rises + perm-significant on **all three** families (SciNCL
  +22.6%/3.35σ, Qwen3 +6.6%/3.07σ, SPECTER2 +3.4%/2.2σ). Directional 3-family claim holds.
- Collinearity-controlled (`robustness-sweep.json`, year VIF **44.3**): `resid_sig=true` on **only SciNCL
  mean-pairwise-cosine** (2 specs). Qwen3 mean-pairwise = false; every `cluster_entropy` / `effective_dim`
  = false; `cluster_entropy` **reverses down** under SciNCL-k30 and Qwen3.
- **This is a SURVIVING program headline** ("semantic fragmentation across three embedding families"), so
  it matters most of all. Fair caveat: VIF 44 makes the residual-against-year control arguably
  *over-conservative* for an intrinsically temporal trend — report both, claim narrowly. Also: the metric
  is **mean-pairwise-cosine (embedding spread), NOT "atypicality."** The program docs mis-name it.

---

## TIER 2 — Real internal inconsistencies (fix; do NOT threaten a headline)

### T2.1 — canary H4 "reverts" vs "level-step" contradiction. [CONFIRMED by consolidator: read both scripts]
- `compare_families.py:9,83-85` + `h3-theory-test.md:171` say H4 is "a round-1 spike that **reverts**."
  `report_h4.py:118-127` (repo's own analysis) says concentration "rises as a **LEVEL-STEP in all collapse
  arms**" — persistent, control-significant plateau (10/10, MWU p≤0.002; ref_gini ends above baseline 10/10).
- Two committed scripts, opposite morphologies for the same data. Data support the level-step reading;
  "reverts" is the one framing the data contradict. **Both agree on the decision** (registered slope-gate
  fails 4/10 → H4-as-registered correctly WITHDRAWN); they disagree only on describing the residual. This is
  an *under*-claim, not an overclaim. **H1 (the headline) is untouched.** Fix = reconcile wording.

### T2.2 — WS3 formal-spine primer is stale and paper-bound. [auditor CONFIRMED]
- `docs/primers/cv-reconciliation-primer.tex` carries the 2026-07-07 amendment but **not** the 2026-07-22
  one. It still labels the withdrawn crossover "the paper's central result" and asserts a Pareto
  "raise both (∂C*>0, ∂V*>0)" that the **committed model refutes** (`phase_diagram.py` → C≡46.0 flat across
  ι, ∂C/∂ι = 0). This .tex is named the "formal spine" and feeds the paper. Fix before it propagates.

### T2.3 — WS3 figure generator reintroduces the retired defect. [auditor CONFIRMED]
- `phase_diagram.py` still prints "λ* ≈ 0.09" and labels λ=0 "V-favouring" with **no CI caveat**, between
  two slopes that both straddle zero (λ=0: [−0.0017,+0.0052]; λ=0.15: [−0.0117,+0.0070]). Master docs caveat
  it; the *reproducible figure* does not. A figure lifted from it re-imports the exact uncertainty-free
  point-estimate defect #2. Fix before lifting.

### T2.4 — In-body stale headlines (additive-correction drift). [CONFIRMED by consolidator on origin/main]
- WS2 CLAUDE.md repeats "the citation canon concentrates" in-body at lines 116/124/169/227, superseded only
  by boxes at 16/83. canary "fluently" not propagated to retro §1 headline / `fluent` code field. Benign under
  lab additive-correction discipline, but a **paper needs the corrected claim in the body**, not 100 lines down.

---

## TIER 3 — Reproducibility & precision hygiene (note for the methods/appendix)

- **Raw artifacts gitignored** → several arms not reproducible from a *fresh clone* (bit-exact on-disk only):
  WS1 72 rung-1/2a/2b files (rung-0 + insulation raws ARE committed); WS2 needs raw parquet; canary needs
  Modal; WS3 300-cell sweep; polyphony ~630 MB. Fine if disclosed; document what's regenerable-vs-archived.
- **Point estimates dressed as precision:** canary "31–37%" = two single-seed points (OLMo κ=0.125 has **zero**
  replicates; severity axis is seed-noisy, Qwen3 κ=0.25 swings 17→40%); WS3 Bridge A "15.6×≈13×" is a loose,
  `bw`-tunable, within-slope≈0 fingerprint (pass bar is ≥5×), not a magnitude match; WS1 rung-0 "+27/+17/+10"
  ordering invites over-reading — the co-registered `decisions` skeleton **significantly reverses** (−6.8%, CI
  excludes 0). Directions robust; the *intervals/orderings* overstate precision.
- **Pinning/provenance:** canary model-revision hashes never pinned (pre-reg required it; `TBD`; absent from
  31 result JSONs); WS3 `spend.md` not updated for Modal runs; WS2 `make test` needs `--extra demo` (5 fail
  out of the box); WS1 insulation prose ("both founding claims now unsupported") rounds up one equal-size
  operationalization; local `main` 40 commits stale (root of the false alarm).

---

## WHAT SURVIVES CLEANLY (the reassuring column — coverage explicit)

- **WS1 (all 5 ch.2 claims):** reproduce **bit-exactly** from committed code+artifacts; 100 tests pass;
  ruff+mypy clean. **None of the 3 fatal failure-modes recur** — the P_top4 null is genuinely matched and
  kills the arm's OWN concentration (232%, p=0.19, conservative direction); the uncertainty-free crossover was
  retired (rung-3 never ran); the cross-substrate replication targets polyphony's **committed corrected** record.
  `catalog.py`/`rung1_null.py` verbatim-in-mechanism from polyphony (cosmetics + one *registered* seed change).
- **canary H1:** recursion collapses generation diversity even at 12.5% synthetic, in **two genuine
  architectures**, **survives its matched κ=0 null** (dead-flat vs 31–37%, effect 10× larger), reproduces exactly.
- **WS2 ref_gini WITHDRAWAL:** sound, matched-null-instrumented, **unit-tested**, reproduces **bit-for-bit**
  (null means regenerate to 0.000e+00 from committed series). The age-restricted substrate gate (CS declines
  all 3 windows) and replacement measures (CS canon flat / Physics rises, 24M pop) survive. **A real result.**
- **WS3 self-critique:** accurate, not overstated (every 2026-07-22 correction number reproduced). Usable
  estimands hold: E1 conformity crushes V^struct (−37%@λ0.5…−86%@λ2), E2 W↑/V^struct↓ N-decoupling 16/16 cells,
  E3 isolation +59% [+0.53,+0.64]. 154 tests pass, deterministic.
- **polyphony:** the P_top4 matched null is **exemplary** (replay 2.22e-16, preference-removed matched); R4
  collapse-refutation solid; amendment trail additive + internally consistent; public surface disciplined (a
  test literally forbids overclaim words). 113 tests pass.
- **Demographic plurality rise:** robust (minor undisclosed 2019→2024 endpoint plateau).

---

## HOW TO PROCEED (recommended sequence into paper-writing)

1. **Fix the two Tier-1 overclaims.**
   (a) Restate the AI-arm result to polyphony's actual record: *refuted collapse + exploratory anti-homogenization
   rises + task-conditional harm* — drop "six experiments / three designs / decoupling replication." Update the
   stale memory (T1.3).
   (b) Restate WS2's semantic leg narrowly (mean-pairwise-cosine; SciNCL-robust; 3-family-directional; not
   "atypicality"), reporting raw + collinearity-controlled side by side.
2. **De-stale the paper-bound WS3 artifacts** (primer `.tex` T2.2; `phase_diagram.py` CI caveat T2.3) so no
   figure/section re-imports the withdrawn crossover.
3. **Reconcile the canary H4 wording** (T2.1) to the level-step reading.
4. **Decide the correction-style policy for paper source:** the supersession-box (additive) style is right for
   lab docs; a paper must carry the corrected claim in the body (T2.4).
5. **Git hygiene:** fast-forward local `main` to `origin/main` (the false-alarm root).
6. **Then the clean surviving story is paper-ready** and coherent: demographic rise; WS2 ref_gini withdrawal as
   a *null-model methods result*; WS3 two-channel N-decoupling + honest crossover-null; WS1 cross-substrate
   replication of resilience/null; canary H1 recursion collapse; polyphony resilience (carefully stated). Thesis:
   *intellectual diversity is more robust than the founding claims (#13 decoupling, #17 insulation) assumed — and
   here are the matched-null methods that show why the original concentration signals were artifacts.*
