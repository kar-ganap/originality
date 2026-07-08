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
