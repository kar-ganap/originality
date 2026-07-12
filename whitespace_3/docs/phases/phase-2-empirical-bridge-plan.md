# WS3 Phase 2 — The empirical bridge (Lever 1): calibrated prediction + the disruption reconciliation

**Whitespace:** 3 · **Phase:** 2 (the WS2 bridge) · **Branch:** `ws3-phase-2-empirical-bridge`.
**Status:** PLAN (pre-registration — hypotheses + criteria + honest-null clauses locked before running).
**Formal spine / anchors:** the Phase-1 two-channel reconciliation must (i) **predict** WS2's
measured fragmentation from **off-trend-calibrated** parameters, and (ii) **reconcile
Park–Leahey–Funk 2023** (Nature; the CD "disruption is declining" result) with WS2 Phase-2.4's
atypicality-*rise*. Reproduce-published-numbers standard: **Park's CD-decline is the external
number** the bridge must engage.

---

## 0. Scope + the driving claim

**Lever 1 (chosen). Lever 2 (the AI / model-collapse arm) is deferred pending funding** — its
compute would balloon past the program's budget discipline; not a non-funded starter.

**The driving claim (pre-registered).** The observed *decline in scientific disruption*
(Park et al., CD index ↓) and the observed *rise in per-capita structural novelty* (WS2 2.4,
reference-atypicality ↑) are **not contradictory** — they are the **two orthogonal channels**
of the Phase-1 model: **within-field consolidation onto a concentrating canon (`κ`)** + 
**cross-field recombination across fragmenting niches (`τ`)**. A paper can *build on the canon*
(low CD, consolidating) **while** *combining canon elements across subfields unusually* (high
cross-field atypicality). The two-channel ABM, **calibrated to independently-measured
parameters**, reproduces both. If it lands, this reframes a live high-profile debate at ~\$1.

**Cross-whitespace (implementation note).** The bridge applies WS2's measurement pipeline
(`v_extension`: `reference_atypicality`, `off_canon`, `forward_uptake`, `within_group_atypicality`)
+ a new **CD-index** to *WS3 ABM output*, and measures calibration inputs from the OpenAlex
snapshot. Per the independence rule, the shared surface (the measures; the ABM `run` functions)
graduates to a small **versioned util** or is vendored with attribution — decided at build, not
ambient coupling. The pinned OpenAlex snapshot date carries over from WS2.

---

## 1. Pre-registered hypotheses

| # | Hypothesis | Criterion (pass) | Honest-null (report, don't hide) |
|---|---|---|---|
| **H-A** *(measurement bridge)* | The ABM, emitting a synthetic reference corpus run through WS2's **identical** atypicality pipeline, produces the fragmentation fingerprint: **global atypicality rises, within-subfield flat**. | model within/global slope-ratio ≥ ~5× (order-of-magnitude vs the empirical 9–13×) | if the pipeline on model output does **not** show the split, the model's fragmentation is not measurement-faithful → diagnose (the Uzzi-z scale confound may recur) |
| **H-B** *(forced prediction)* | With `m`, `bw`, `q` calibrated **off-trend** from OpenAlex (never fit to the novelty trend), the model **predicts** the observed within/global gap and the `H(t)` trajectory. | predicted within/global within ~2× of observed **and** `H` rises | if the fit is only *consistent* (wide error), report as **consistency, not prediction** — a weaker but honest claim |
| **H-C** *(the disruption reconciliation — the headline)* | *(data)* CD declines **within-field** on OpenAlex while atypicality rises **cross-field**; *(model)* the two-channel ABM reproduces **both** signs from the calibrated params. | data: CD-within slope `<0` **and** cross-field novelty `↑`; model: CD `↓` **and** atyp `↑` jointly reproduced | if the model can't reproduce both, **or** the empirical CD-decline is artifactual (coverage / citation-inflation) → report; fall back to the *decoupling* paper without the Park headline |
| **H-D** *(cross-field OOS — fate after A–C)* | Calibrated on CS, the model **predicts** the fragmentation signature in a **held-out field** (bio/chem) from that field's measured parameters. | within-flat / global-rise holds in the held-out field | **fate decided after A–C** (§5); if pursued and it fails, the effect is field-specific → report |

---

## 2. Experiments

- **A — the measurement bridge.** Add a model→reference-corpus emitter to the ABM (each model
  "paper" = its attachment/prereq set as references; niches = subfields). Run WS2's exact
  `reference_atypicality` + `off_canon` + `within_group_atypicality` on the emitted corpus.
  **Deliverable:** apples-to-apples model-vs-data fragmentation numbers (not a bespoke model metric).

- **B — off-trend calibration → forced prediction.** From the pinned OpenAlex snapshot, measure
  **independently of the novelty trend**: `m` (median reference-list length / engaged prior works),
  `bw` (within-subfield reference concentration — Gini/entropy of a subfield's citation targets),
  `q` (share of references to cross-cutting / foundational canon). Run the ABM with these; compare
  the pipeline-measured within/global gap + `H(t)` to the observed.

- **C — the disruption reconciliation.** Implement the **CD (consolidation–disruption) index**
  (Funk–Owen-Smith / Park) on *(i)* the OpenAlex data (in-sample forward-citation graph,
  coverage-caveated) and *(ii)* the ABM corpus. Show: **data** — CD declines within-field while
  atypicality rises cross-field (the decomposition); **model** — the two-channel structure
  reproduces CD↓ and atyp↑ jointly. **Engage the CD-index-artifact debate honestly** (control for
  reference-list inflation / coverage; report the residual).

- **D — cross-field out-of-sample.** Extend the empirical extraction to ≥1 held-out field
  (bio/chem); calibrate on CS, predict the held-out field's fragmentation signature. Fate after A–C.

---

## 3. Validation gates

1. Pre-registration honored: criteria + honest-null clauses fixed before running (this doc).
2. **A** green: the bridge emits + measures; the fingerprint (or its honest absence).
3. **B** green: forced prediction (or the honest "consistency" fallback).
4. **C** green: the reconciliation (data decomposition + model joint reproduction), or the fallback.
5. **Reproducibility:** every number regenerable from committed code + the pinned snapshot; ≥2
   measures where WS2's discipline demands; permutation + absolute magnitude (no ill-conditioned-σ).
6. Retro: the paper spine; the venue calibration; **D's fate**.

## 4. Risks + honest-null discipline

- **The CD index is contested** — Park's decline has been challenged as partly a
  citation-practice / database-coverage artifact. *Mitigation:* control for reference-list
  inflation + coverage, report the residual. Engaging the debate is the contribution, not a bug.
- **In-sample forward citations are sparse** (2.4's ~8.4% caveat) → CD on our data is noisy.
  *Mitigation:* with-refs subset, permutation, report coverage.
- **Calibration fidelity** — `bw`-proxy ≠ model `bw`; "prediction" may only be "consistency."
  *Mitigation:* claim prediction only if the error is tight; else say consistency.
- **C might not reproduce both** — pre-registered honest-null; fall back to the decoupling paper.

## 5. D's fate (decided after A–C)

- **A–C land cleanly** (calibrated prediction + Park reconciliation): D is the rigor capstone →
  pursue; aim PNAS / Science Advances / (stretch) Nature Human Behaviour.
- **A–C mixed** (consistency-not-prediction, or Park messy): D deferred; the paper is the
  decoupling result at QSS / Science Advances, D as future work.
- **A–C fail the reconciliation:** D moot; reframe (still a publishable decoupling + ABM paper).

## 6. Non-goals

- **No AI arm** (Lever 2; deferred pending funding).
- **No new ABM mechanism** — this is **calibration + measurement + the CD-index bridge** on the
  *existing* two-channel model (`channel.py` κ-channel, `subfield.py` τ-channel).
- **No new dataset** beyond the pinned OpenAlex snapshot (+ the held-out field for D).
- One phase, one job: **make the theory *predict* the empirics, and reconcile the disruption
  debate — or fail honestly and fall back to the decoupling result.**

---

## 7. Amendment (2026-07-08) — Experiment B′ (principled augmentation, pre-registered)

**B's outcome (H-B honest-null).** The model's `niche_specific_ref_share` is ~0 at every
`bw` vs the empirical `0.58`, so `bw` is not pinnable by that statistic. Two candidate causes,
tested in order:

### B′-1 — apples-to-apples re-measurement (does the null survive the `d_min` filter?)
The `0.58` is over **all** refs (long-tail-dominated), but `reference_atypicality` **excludes**
works with degree `< d_min` — so the atypicality is measured only on heavily-cited (canonical)
works, which are largely multi-subfield. Re-measure `niche_specific_ref_share` **over the
`d_min`-relevant subset** (works with total citation degree `≥ 20`, the atypicality vocab).
- **H-B′1:** if the `≥d_min` share ≈ the model's (~0 — canonical works are multi-niche), then
  B's gap was a *long-tail artifact*; the model is **consistent on the relevant subset** →
  B softens to *consistency-with-the-right-microstructure*, **no augmentation needed**.
- else the gap is real on the relevant subset → **B′-2**.

### B′-2 (conditional) — the pinned-φ augmentation + the `bw`-sensitivity falsifier
Add a **niche-private-vocabulary** channel: a fraction φ of a paper's refs go to
niche-private elements (cited only by that niche, ∝ within-niche popularity), the rest to the
shared canon (existing lens). This is the data's *second* distinctiveness channel (private
literatures) the minimal model lacks — **not** a dilution of `bw` (which carries *combination*
distinctiveness). **Pin φ = the `≥d_min` empirical share; `m`, `K`, `q` off-trend; tune NOTHING
to the ratio.**
- **H-B′2 (pre-registered dichotomy — the honesty test):**
  - predicted ratio **≈ 13× (within ~2×) AND `bw`-INSENSITIVE** (varies `< ~2×` over
    `bw ∈ [0.02, 0.08]`) ⇒ **FORCED PREDICTION** — φ (pinned) carries it, `bw` is not the free
    knob. B upgraded.
  - the ratio **swings with `bw`** (`> ~2×`) ⇒ `bw` was never pinnable from structure; the
    **honest-null STANDS, sharpened** (the data's fragmentation has a combination-distinctiveness
    component the minimal model can't pin off-trend).
- **Non-negotiable:** the `bw`-sensitivity is the **headline**, not buried. Also report
  sensitivity to the private-pool size `P` (a secondary knob) — if `P` is a free lever too, say so.
- Rationale: the guardrail against overfitting is not "refuse structure" but "add the
  independently-motivated structure, pin what an *independent observable* pins (φ), and publish
  the sensitivity to what it does not (`bw`)."

---

## 8. Amendment (2026-07-08) — Experiment C reframed: **adjudicate, don't reconcile**

**C's model-side outcome (C-1, C-1b).**
- **C-1** (`experiments/phase-2/cd_C.py`) — CD index on the attachment channel (`channel.py`).
  Under κ, mean CD **rises** (`+0.327→+0.381`, λ:0→1) and rises over birth-time (`+0.0067`) —
  the OPPOSITE of Park's decline. Not a bug: a correct property of preferential attachment (a
  hub's citers cite the hub + *other* hubs, not the hub's specific prereqs ⇒ CD↑ as
  concentration intensifies). The model reproduces canonical concentration as **Gini `H`↑**
  (rungs 4a/4b), NOT as CD↓ — CD is the wrong operationalization of the κ-channel.
- **C-1b** (`experiments/phase-2/cd_C1b.py`) — the model holds reference-list length FIXED.
  Injecting birth-proportional length-inflation (uniform extra refs over earlier elements;
  attachment kernel untouched) drags the CD-vs-birth slope monotonically `+0.0067 → … → −`
  (flips at ~×4; ref-lists grew ~3–4× over 1970–2024, so ×4 is in-range). With the real
  dynamics held fixed, **length-inflation ALONE reproduces a CD-decline.**

**The reframe.** C-1/C-1b land in H-C's pre-registered honest-null branch ("the empirical
CD-decline is artifactual → fall back"), but with a POSITIVE mechanism. The model **dissociates**
real concentration (`H`↑, which it reproduces; CD would *rise*) from the empirical CD-**decline**
(reproducible from length-inflation — the Petersen-Holst-Macher artifact). C moves from *reconcile
Park (reproduce CD↓)* to **adjudicate Park**: the decline is a reference-length artifact; the real
signals are **concentration (`H`↑) + fragmentation (atyp↑)**, exactly the two-channel model's
output. We *mechanistically underpin* the existing critique — we do not discover it.

### C-2 — the data-half (pre-registered)
On WS2 `panel-2.4.parquet` (CS 1970–2024), CD computed via the SAME vendored `cd_index` on the
**within-panel** citation graph (invert `refs`). *Boundary caveat:* citations crossing the
CS-1970-2024 panel are truncated ⇒ within-panel CD (cf. Park's full WoS graph) — stated, not buried.

- **C-2a (go/no-go):** does the decline replicate? CD-vs-year slope within CS. **Gate: slope `<0`,
  bootstrap CI excluding 0.** If the within-panel graph is too truncated to show a decline → C-2
  inconclusive on our data; report C-1/C-1b as the mechanistic contribution + fall back to
  decoupling. *Pre-committed pivot.*
- **C-2b (the adjudication test):** length-cap control — recompute CD after capping each paper's
  reference list to the early-era level (removes length-inflation; the mirror of C-1b, which
  ADDED it). **Gate: the decline attenuates materially toward 0** (≥ ~50%).
- **C-2c (real signals survive):** the same cap must NOT kill the real signals — concentration
  (reference-canonicity Gini `H`↑) and atypicality (2.4-style, rising) persist. **Gate: both
  trend signs unchanged under the cap.**
- **C-2d (quantitative bridge, nice-to-have):** measure the panel's actual ref-length growth,
  feed it through the C-1b machinery, compare the model's post-inflation CD-decline *magnitude*
  to the data's.

**Evaluation (H-C, amended).** The adjudication is EARNED iff **C-2a ∧ C-2b ∧ C-2c**. Any failure
→ honest fallback to the decoupling paper with the model result as a mechanistic caveat (not a
debate claim). The within-panel truncation and the shallow model flip are reported, not hidden.

---

## 9. Amendment (2026-07-08) — C-2 escalates to the FULL 24M graph (the truncation is fixable)

**Why.** C-2a/b on the base-1m sample hit the pre-registered truncation limit: the within-panel
graph is only **1.9%** dense (0.24 in-panel refs/paper), so the length mechanism (which lives in
the full reference lists) is projected away — the decline replicates (`−0.00266`) but is
selection-confounded and NOT in-sample decomposable (7% attenuation). The blocker was the 1M/24M
*sampling*, not the method.

**The fix is cheap because the data already exists.** The phase-1.2 parse retained
`referenced_works_json` for the full **24M v3 population** (`section0-population-v3.parquet`, 54.8
GB on Modal Volume `ws2-section0`) — no 639 GB dump re-parse. **Step-0 go/no-go**
(`cd_density_check.py`, server-side): in-population citation density **46.7%** (25× the sample),
mean 6.1 in-pop refs/paper, **41% of papers CD-eligible** (≥3 in-pop refs ≈ 10M), usable across
all eras (pre-1990 27% → 2010+ 43%). Clears the ~30% threshold decisively ⇒ **GO**.

**C-2-full (`cd_data_C2_full.py`, all server-side).** Build the within-population reference graph
as CSR; compute CD (`cd_index_csr`, scipy-sparse, tested byte-equivalent to `cd_index`) for a
per-year focal sample (≈2.5K/yr) on:
- **uncapped** (C-2a-full): does the decline replicate cleanly now that eligibility is 41% across
  all eras (not the sample's selection-biased 0.85%)? Gate: slope `<0`, bootstrap CI excludes 0.
- **length-capped** (C-2b-full): refs truncated to the early-era length `cap` (removes
  length-inflation — the data mirror of C-1b). Gate: decline attenuates ≥ ~50%.
Whitespace bridge: `cd_index`/`cd_index_csr` vendored WS3→WS2 (pin `282e09f`), operated on the WS2
Volume; population is all-field (CS+physics per the §0 pull), focal CD uses the full graph
(Park-style within-field). Residual caveat: even 46.7% < 100%, so some cross-boundary truncation
remains; our snapshot/field defs won't match Park's CD *magnitude* (trend + attenuation are the
targets). **The novel contribution (C/V mechanism + two-channel decoupling) does not depend on
C-2-full — this is a rigor/completeness upgrade of the adjudication's data half.**

**VERDICT (C-2-full, 2026-07-08 — the adjudication is disconfirmed; the decoupling is confirmed).**
- **C-2a-full ✓:** `CD-vs-year = −0.00086`, CI `[−0.00091, −0.00081]`, monotone `0.050 (1975) →
  0.013 (2020)` across all eras (137.5K focals). Park's decline **replicates cleanly** on 24M.
- **C-2b-full ✗ (gate NOT met):** mediation attenuates only **24%** (`−0.00086 → −0.00065`, <50%);
  random length-cap **steepens** the decline (−78%). The decline is **NOT a reference-length
  artifact** — it survives length-control ⇒ a **real consolidation signal**.
- **Landing:** the two-channel **decoupling is confirmed** (CD↓ + `H`↑ consolidation ⊥ atyp↑
  fragmentation, all real). The C/V model reconciles via `H` + atyp; Park's CD-decline is
  independent confirmation of consolidation; the model's PA substrate mis-signs the *CD-index*
  (C-1) — a documented limitation, not a data artifact. We **confirm Park, additively**. C-1b's
  length-mechanism is real in the toy but overstates length vs the data (24%). Coverage/practice
  artifact untested (deliberately — out of scope). Full arc: `phase-2-experiment-C-retro.md`.
- **D deferred** (plan §5): A–C landed mixed ⇒ the paper is the confirmed decoupling + reconciliation.

---

## 10. Amendment (2026-07-08) — C-2c, the coverage battery (the critique's *other* prong)

C-2b-full tested the reference-*length* prong of the CD-critique (not the driver: 24% mediation).
A **citation-coverage** artifact is distinct. Decomposed into four mechanisms, three testable on
our 24M graph (`cd_data_C2c_coverage.py`); the fourth is the irreducible external-benchmark limit.

- **Free pre-check (from `cd_full-result.json`) — mechanism 1 (reference-recording completeness):**
  the CD-vs-year slope is **uniform across coverage regimes** — pre-digital 1970–99 `−0.00083`,
  born-digital 2000–24 `−0.00093`, 2010–24 `−0.00088`. If old-paper under-coverage manufactured
  the decline it would flatten post-2000; it does not ⇒ largely disconfirmed already.
- **Mechanism 2 (observation-window / accumulation asymmetry):** we counted **all-time** citations,
  so old focals were watched ~50 yrs, recent ~6. **Fixed forward-citation window** `W=5`, `W=10`
  (Park-standard equal window); focals restricted to `year ≤ max_year − W` (uncensored). Gate:
  slope `<0`.
- **Mechanism 3 (field-growth / network size):** corpus grows ⇒ the `n_k` pool grows ⇒ CD↓
  mechanically. **Control the year-slope for `log(papers published in the focal's year)`.** Gate:
  slope survives (attenuation `< ~50%`).
- **Mechanism 4 (citation inflation, edges/paper):** ≈ the reference-length artifact — **done**
  (C-2b-full).
- **Rigor confirm — born-digital clean cut:** focals AND citers ≥ 2010 (`year_min=2010`), making
  mechanism-1 airtight on the citer side too. Gate: slope `<0`.

**Irreducible limit (stated, not hidden):** all four tests are *internal* to OpenAlex; none checks
OpenAlex coverage against ground truth (WoS/Crossref cross-match or hand audit) — the same limit
every CD paper faces. Meeting the window + growth + era controls is the standard the field expects.
**Evaluation:** the decline is coverage-robust iff window (2) ∧ growth (3) ∧ born-digital hold; any
failure re-opens the coverage question honestly.

**VERDICT (C-2c, 2026-07-08 — the decline is an OBSERVATION-WINDOW artifact; gate FAILS at window).**
- **Window (2) — FAILS:** the all-time `−0.00087` **erases** under a fixed forward-citation window
  (Park's own method): `W=5` slope **+0.00044** (CI `[+0.00037,+0.00052]`, rises `−0.009→+0.012`
  over 1970–2019), `W=10` **+0.00006** (flat). Old focals had ~50-yr windows the CD-index reads as
  disruptive; recent focals ~6. This is the culprit.
- **Growth (3) ✓ small:** field-growth (`log` corpus) control attenuates only 14%. **Coverage-era
  (1) ✓:** uniform slope across eras. So the artifact is the *window*, not length/growth/coverage.
- **Fixed-window disruption is flat-to-rising ⇒ AGREES with atyp↑** (WS2 2.4): structural novelty is
  not declining in our corpus.
- **Landing (supersedes §9's "decline is real"):** the CD-index is **length-robust but
  window-FRAGILE** ⇒ **not load-bearing**. The decoupling stands on **`H`↑ (concentration) ⊥ atyp↑
  (fragmentation)** — window-robust. CD → a robustness/discussion subsection engaging the Park debate
  (window-fragility + consistency-with-atyp), **not** a pillar. We neither confirm nor overturn Park
  (our within-pop graph ≠ his full graph). Full arc: `phase-2-experiment-C-retro.md`. Lesson (use a
  fixed CD window from the start): `tasks/lessons.md`.
