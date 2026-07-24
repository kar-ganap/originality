# Adversarial Audit — `canary` (AI single-model / recursion-κ arm)

**Auditor:** independent adversarial reviewer. **Date:** 2026-07-24.
**Repo:** `/Users/kartikganapathi/Documents/Personal/random_projects/canary`
**Branch:** `phase-1b-h3b` — **NOTE: fully published.** `main`, `origin/main`, and `phase-1b-h3b`
all point to the same commit `a54cac4`; the withdrawal (87ed136) is on `main`. Claims are NOT
stranded on an unmerged branch (a point in canary's favor vs the sibling program).
**Scope:** canary only. **Cost guardrail honored:** no Modal/training/API launched; end-to-end
data-generation NOT independently reproduced (verified against committed artifacts + analysis code).

---

## EXECUTIVE SUMMARY

- **H1 (surviving headline — collapse even at 12.5% synthetic, 31–37%, two architectures): SURVIVES.**
  The 31.2% (Qwen3 κ=0.125) and 36.8% (OLMo κ=0.125) reproduce exactly from committed JSONs; both
  arms labeled `collapse`; clean separation from a dead-flat κ=0 matched null (−0.3% / +1.6%).
- **H1 caveat (WEAKENED precision): the "31–37%" carries NO uncertainty** — two single-seed point
  estimates (OLMo κ=0.125 has **zero** replicates), on a severity axis the repo itself shows is
  seed-noisy (Qwen3 κ=0.25 swings 17→40%). Direction robust; the *interval* is not.
- **H3a/H4 withdrawal is INCOMPLETE / INTERNALLY INCONSISTENT.** H3a's withdrawal is clean in the
  active docs. **H4's is not:** the withdrawal's stated reason ("a round-1 spike that reverts") is
  **contradicted by the repo's own committed `report_h4.py` (persistent, control-significant
  level-step in 10/10; MWU p≤0.002) and by the data** (ref_gini ends above baseline in 10/10). Two
  committed scripts give opposite morphologies for the same data.
- **"Fluently" qualification: COHERENT but not fully propagated** (retro §1 headline still says
  "fluently" unqualified; code field still literally named `fluent`).
- **Provenance gap:** model-revision hashes **never pinned** (pilot plan = literal `TBD`; no
  `revision=` in code; absent from all 31 result JSONs), despite the pre-reg's own lock requirement.

**Bottom line:** the surviving headline (H1) is real and holds; the *withdrawal machinery around it is
not internally consistent*, and the headline number is a point estimate dressed as a range.

---

## FINDINGS (most-severe first)

### [HIGH] H4 withdrawal is self-contradictory; its stated reason is falsified by the repo's own committed analysis — CONFIRMED
- **Claim affected:** "H4 is WITHDRAWN — a round-1 concentration spike that reverts."
- **Where:** `experiments/analysis/compare_families.py:9,83-85`; `docs/h3-theory-test.md:171`
  (the "reverts" camp) vs `experiments/analysis/report_h4.py:118-127` + `docs/phases/phase-1-retro.md:34`
  + `tasks/spend.md:69-70` + `experiments/README.md:15` + `docs/pre-registration.md:276`
  (the "persistent level-step / partial echo" camp).
- **What's wrong:** The withdrawal (2026-07-22) says the concentration rise is "a round-1 spike that
  reverts (post-round-1 slope negative in 6/10 collapse arms)." I regenerated the committed data:
  - `report_h4.py` output (regenerated): **level-step positive 10/10; control-referenced plateau >
    κ=0 control, MWU p<.05, 10/10** (p ≤ 0.002 every arm). The plateau is rounds **3–7** — well
    *after* round 1.
  - Raw ref_gini net change (first→last) is **positive in all 10/10 collapse arms** (Qwen3
    +0.098…+0.436; OLMo +0.080…+0.189). It does **not** return to baseline in any arm.
  - Even OLMo (largest round-1 overshoot, peaks ~0.66–0.69 at r1) settles at an elevated plateau
    ~0.10–0.15 **above** baseline — hence the MWU significance.
  The "post-round-1 slope negative in 6/10" is arithmetically true, but it reflects a **retrace from
  an initial overshoot to a still-elevated plateau, not a reversion to baseline.** "Reverts"
  conflates the two and is contradicted by the very level-step it disputes.
- **Also self-contradictory *within* `compare_families.py`:** its table body still prints `H4✓` in
  every collapse cell and "`H4 coupled 5/5 collapse arms`" for both families; only the appended footer
  says WITHDRAWN. The underlying `h4_verdict(...).coupled` still returns `True` for all 10 arms (code
  unchanged; only English prose withdrew).
- **Fair reading:** the withdrawal *decision* is defensible — the **pre-registered** gate (monotone
  ref_gini slope, perm p<.05) is met in only **4/10**, and the level-step that holds is an explicitly
  **post-hoc, not-re-frozen** refinement (retro §8). So "H4 confirmed 5/5" should not be claimed. But
  the honest reason is "registered slope-gate not met; the persistent rise is post-hoc" — **not**
  "it reverts." The record now tells two incompatible empirical stories about the same data; a referee
  diffing the two scripts will catch it.
- **Evidence:** `report_h4.py` run (10/10 level-step, 10/10 MWU p≤0.002); my `extract.py`
  (rg_net > 0 in 10/10); `compare_families.py` run (table `H4✓ 5/5` + footer "reverts").

### [MEDIUM] H1 headline "31–37%" is a pair of single-seed point estimates, not an interval with uncertainty — CONFIRMED
- **Claim affected:** "even 12.5% synthetic still collapses diversity by 31–37% in two architectures."
- **Where:** program `CLAUDE.md` H1 note; `docs/phases/phase-1-retro.md:32`; `tasks/spend.md:25`.
- **What's wrong:** "31–37%" is **not** a CI — it is Qwen3 κ=0.125 seed-0 (31.2%) and OLMo κ=0.125
  seed-0 (36.8%), one point per family. **OLMo κ=0.125 has no replicate at all.** Qwen3 κ=0.125 has
  one replicate (seed-1 = 36.0%). The severity axis is demonstrably seed-noisy — from committed arms:
  Qwen3 κ=0.25 = 17.1% (s0) vs 39.6% (s1); Qwen3 κ=0.5 spans 18.4/26.5/41.5/40.9% across four seeds.
  The retro is candid that "severity is single-seed noise-limited" and "regime, not severity, is the
  robust axis" — but the **headline still quotes the noisy severity as a precise range** without that
  caveat travelling with it.
- **Mitigation (why only MEDIUM):** the *direction* is rock-solid and survives its matched null — every
  non-zero κ collapses ≥17% (mostly ≥30%) vs κ=0 control at −0.3%/+1.6%; κ=1.0 one-sided slope-p=0.000
  both families. So "recursion collapses diversity even at low synthetic fraction, in two
  architectures" holds; only the *precise magnitude* "31–37%" overstates precision.
- **Evidence:** per-seed severity table (my extraction, all 31 committed arms); `report_audit_checks.py`.

### [MEDIUM] H1's required ≥3/4 corroboration gate is non-specific — fires on the κ=0 control — CONFIRMED
- **Claim affected:** H1's "collapse corroborated by ≥3 of 4 independent substrates."
- **Where:** `src/canary/analyze.py:113-137` (`corroboration_verdict`, N1 note) + `classify_arm:316`
  (corroboration is a *required* conjunct); `report_audit_checks.py` N1 output.
- **What's wrong:** `classify_arm` calls collapse only if `corroborated AND (level≥20% OR sig-neg
  slope)`. But corroboration fires **2/4 on the Qwen3 κ=0 control and 3/4 on the OLMo κ=0 control** —
  and 3/4 **meets** the `corroborated` threshold. So the "4 independent metrics agree" safeguard gives
  *no* false-positive protection; collapse detection rests entirely on the mpcd primary. (The related
  `h4_verdict.coupled` flag is likewise non-specific — returns `True` for the OLMo κ=0 control.)
- **Mitigation:** the mpcd primary itself cleanly separates control (decline 0–2%, perm_p 0.38–0.96)
  from treatment (31–44%, perm_p 0.000–0.032), so H1 is not actually endangered. And it is **honestly
  documented** as N1 in code and retro. Flagged so the paper does not lean on corroboration rhetoric.
- **Evidence:** `report_audit_checks.py` N1 block; `report_sweep.py` `corr` column (κ=0: 2/4 Qwen3, 3/4 OLMo).

### [MEDIUM] Reproducibility: model/embedding revision hashes never pinned; absent from all artifacts — CONFIRMED
- **Claim affected:** end-to-end regenerability of every headline number.
- **Where:** `docs/phases/phase-0-pilot-plan.md:34` ("revision pinned here at snapshot: `TBD`");
  `src/canary/train.py:63,68` (`from_pretrained(base_model)` — no `revision=`);
  `src/canary/measure.py:65` (`SentenceTransformer(model)` — `all-MiniLM-L6-v2` unpinned);
  all 31 `experiments/phase1/results/*.json` (config keys: model, kappa, rounds, gen_per_round,
  seed_size, lora_r, epochs, lr, gen_temperature, seed — **no revision/hash/volume-snapshot**).
- **What's wrong:** the pre-reg's own lock condition ("pin the model-revision hashes + embedding-model
  + volume snapshot at snapshot time", `pre-registration.md:8-9`) was **never satisfied**. Runs pulled
  HF `main` at execution time; a re-run could draw different weights. Seeds/κ/LoRA/lr ARE pinned, and
  the *analysis* reproduces bit-faithfully from committed JSONs — but the **data generation** is not
  reproducible from committed code + documented params, and (Modal-only) cannot be re-verified here.
- **Evidence:** greps above; JSON config-key union.

### [LOW] "Fluently" qualification is coherent but not propagated to the headline or the code — CONFIRMED
- **Claim affected:** "recursive self-training collapses diversity … fluently."
- **Where:** correction at `docs/phases/phase-1-retro.md:127-136` (good, coherent, data-backed — ppl
  *drops* 9.4→6.5 / 13.2→3.4, exactly the "low-ppl repetition" the caveat predicts) **vs** the
  un-qualified "fluently" still in the retro's own §1 headline (`:12`) and §9 lead (`:125`), the pilot
  plan `phase-0-pilot-plan.md:6` ("FLUENT collapse"), and pre-reg change-log `:209`.
- **What's wrong:** the qualification ("read 'fluently' as 'not gibberish' = coherent low-ppl
  repetition") is sound, but a reader hitting §1 first still gets un-hedged "fluently." The code field
  is still literally named `fluent` (`analyze.py:219`; printed by `report_h3b.py:94`), which the retro
  itself calls "misleadingly-named … means `not_gibberish`" — acknowledged but not renamed.
- **Mitigation:** the function docstring (`analyze.py:210,220`) does carry the one-sided caveat.

### [LOW] Residual positive H3a claims persist in append-only ledgers — CONFIRMED (acceptable hygiene)
- **Where:** `tasks/spend.md:23` ("H3a ρ=0.90 p=.037"); `docs/pre-registration.md:240` (2026-07-20
  "H3a regime-ordering supported").
- **What's wrong / mitigation:** both are dated ledger/change-log rows **explicitly superseded** by
  later entries (`spend.md:61-71` correction; pre-reg **v12** `:267` "the 2026-07-20 'results' entry
  above is superseded"; sweep prints "H3a … FAILS p=.27/.40"). Append-only discipline is fine, but a
  naive reader scanning the ledger could be misled. H3a's withdrawal in the **active** docs is complete
  and correct.

---

## REPRODUCTION LOG

| Step | Result |
|---|---|
| `uv sync --extra dev --extra analysis` | OK — resolves numpy/scipy/sklearn + sibling `diversity_metrics`/`cv_predictor` (editable); **no torch** (token-free). |
| `uv run --extra dev pytest -q` | **96 passed, 1 skipped, 1 xfailed** (22.8s). PASS. |
| `report_sweep.py` (Qwen3) | Reproduces: κ*∈(0,0.125]; H3a ρ=0.543 **p=0.266 FAILS**; C/V 6/6 (flagged degenerate non-gate); all κ≥0.125 collapse/progressive. |
| `report_sweep.py` (OLMo) | Reproduces: κ*∈(0,0.125]; H3a ρ=0.429 **p=0.397 FAILS**; C/V 6/6; all κ≥0.125 collapse. |
| `report_h4.py` | Reproduces: registered slope-gate **4/10**; level-step **10/10**; control-referenced **10/10** (MWU p≤0.002); coupling-dir 10/10; morphology partial-echo 10/10. |
| `compare_families.py` | Reproduces: table `H4✓ 5/5` both families + footer WITHDRAWN ("reverts"). Self-inconsistent (see HIGH finding). |
| `report_audit_checks.py` | Reproduces: H1 κ=1.0 decline 27%/44% slope-p=0.000, ppl drops; N1 corroboration fires 2/4 & 3/4 on κ=0 controls; N3 window-asymmetry −0.546→−0.266. |
| Own `extract.py` (read-only) | Confirms H1 31.2%/36.8% at κ=0.125; ref_gini net>0 in 10/10; per-seed severity spread. |
| **End-to-end (Modal training)** | **NOT INDEPENDENTLY REPRODUCED (requires Modal training run)** — per cost guardrail. Verified vs committed artifacts + analysis code only. |

No tracked file modified (read-only audit).

---

## WITHDRAWAL-CONSISTENCY CHECK

- **H3a — COMPLETE in active docs.** Sweep prints "FAILS the pre-registered gate (p≥.05)"; retro §3,
  compare_families footer, h3-theory-test §8 all say withdrawn/failed. Residual positives only in
  superseded append-only ledgers (LOW finding).
- **H4 — INCOMPLETE / INCONSISTENT.** The 2026-07-22 "reverts" re-characterization landed in exactly
  **two** places (`compare_families.py`, `h3-theory-test.md:171`) and was **not** reconciled with the
  ~six committed artifacts (report_h4.py output, report_sweep.py:118, spend.md:69, experiments/README:15,
  pre-reg:276, retro §3/§9) that describe H4 as a *persistent, control-significant level-step /
  "partial echo."* The data support the level-step reading; **"reverts" is the one framing the data
  contradict.** `compare_families.py` also contradicts itself (table vs footer), and `h4_verdict`'s
  `coupled` field still returns `True` 10/10 in code.
- **"Fluently" — MOSTLY complete** (coherent correction exists) but the retro's own §1 headline and the
  `fluent` code field were not updated (LOW finding).

---

## WHAT SURVIVES CLEANLY

1. **H1 — the surviving headline holds.** Recursive self-training collapses generation diversity,
   **robustly across two genuinely different architectures** (Qwen3-1.7B-Base, OLMo-2-0425-1B), **even
   at 12.5% synthetic** (mpcd −31.2% / −36.8% vs κ=0 control −0.3% / +1.6%), with κ=1.0 one-sided
   slope-p=0.000. **It survives its matched null** — κ=0 (0% synthetic, fresh real data, retrain from
   base) is dead-flat, and the effect is an order of magnitude larger. The 31/37 numbers reproduce
   exactly. (Bounded caveats: single-seed magnitude, corroboration non-specific, "fluent"=not-gibberish.)
2. **The v9 methods catch** — effective-dimensionality is a scale-invariant participation ratio and
   structurally blind to magnitude collapse (it *rose* during the pilot); caught mid-flight, primary
   switched to mean-pairwise-cosine. Verified in `analyze.py` + change-log; a genuine, honest result.
3. **H2 crossover *substance*** — κ=0 dead-flat vs κ≥0.125 collapse gives a real crossover in (0,0.125]
   (its exact "sustain@κ=0" *labeling* is disclosed as level-certified, TOST-underpowered at n=8).
4. **The self-correction apparatus itself** — the retro, the honest N1/N3 notes, and report scripts that
   regenerate their numbers from committed JSONs are unusually candid and mostly internally consistent.
   The one place the machinery slipped is the H4 "reverts" wording (HIGH finding).
