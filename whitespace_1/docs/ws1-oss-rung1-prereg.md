# Rung-1 pre-registration — the endogenous bridge replication (Polyphony R4 on DeepSeek)

**LOCKED 2026-07-23** (JC1 settled: thinking ON; faithful R4 port; `V_pair` slope primary). Follows the
rung-0 v2 result (`ws1-oss-rung0-v2-prereg.md` → Results): reachability reached under **imposed**
conformity, with a robust strategy-layer channel asymmetry. Rung 1 moves to the **endogenous**
actuator — Polyphony's own mechanism — on the DeepSeek substrate. Substrate: **DeepSeek V4-pro**
(thinking ON) via `DeepSeekClient`; the fixed embedder is `text-embedding-3-small`.

## Why rung 1 exists — the bridge/control (design note §4, §9.4)

Rung 0 proved collapse is *reachable when ordered*. It says nothing about whether Polyphony's
**endogenous** actuator (shared popularity-weighted catalog, no directive) reaches that regime — which
is the actual claim under test. Rung 1 is the **control that makes rung 2 interpretable**: replicate
Polyphony's output-layer null on this substrate with `V_output` only, holding model + output contract
+ reasoning effort fixed, so that a later `V_reason` signal (rung 2) is attributable to the reasoning
layer and not to the fact that the arm changed model family, length, and effort all at once.

Its payoff (design note §3): convert Polyphony's *bare* null into a *quantitative* one — the endogenous
actuator reaches conditioning strength λ_eff; place λ_eff on rung 0's imposed C1/C2/C3 ladder (clean,
because **rung 0 and rung 1 share the same 5 personas**) and report the imposed-vs-endogenous gap.

## The question and the pre-registered branches

**Does Polyphony's endogenous output-layer null — outputs do NOT homogenize while the actuator is
demonstrably live — replicate on DeepSeek V4?**

| outcome | meaning | action |
|---|---|---|
| **Day-0 gate fails** | conditioning does not *bite* on this substrate | STOP — rung 1 unrunnable here; report, pick another substrate/effort. **The R4 build is conditional on this gate.** |
| actuator live **and** `V_output` does **not** collapse | Polyphony's null **replicates** — bridge holds | proceed to **rung 2** (add `V_reason`) |
| actuator live **and** `V_output` **collapses** | Polyphony's null is **substrate-specific**, not general | major finding; **do not** proceed to rung 2 as planned — ask why DeepSeek collapses where GPT-5.6 did not |
| actuator **not** live (uptake null despite Day-0 pass) | the mechanism did not engage this run | report as unrun; do **not** read a V null off a dead actuator |

## Gate 0 — the Day-0 bite gate (substrate selection; run FIRST, before the loop)

Polyphony's kill-test, re-run on DeepSeek. **Load-bearing for substrate selection** — GPT-5.6 Sol
passed (persona diversity 0.4286, alignment shift +0.0487, lower +0.0153); **GPT-5.6 Luna FAILED the
shift gate (+0.0256) and was rejected.** DeepSeek is not assumed to pass.

- **(a) latent diversity** — 5 personas, no catalog: `V_pair` of the 5 outputs **≥ 0.10** (else the
  `sigma=0` baseline evaporates — the substrate can't produce diverse outputs to begin with).
- **(b) conditioning bites** — show a homogeneous popular-canon sample: mean output→sample alignment
  **shifts ≥ 0.03** above a no-catalog null ceiling (else the endogenous actuator is dead here).
- ~20 calls, ~$0.10. Both pass → build the R4 loop. Either fails → STOP and report (§ branches).

## Design — faithful R4 replication (design note §4 rung 1)

**5 personas × 8 rounds × 3 conditions × 8 run-ids (4 per topic × 2 topics) = 960 generations.**
Ported verbatim from Polyphony R4 (`polyphony/src/polyphony/{catalog,walk_r4,persona,day0_r3}.py`),
generator swapped to `DeepSeekClient`, embedder held fixed.

- **Personas** — the 5 in `stimuli.py::ROLES` (Reliability engineer / Product designer / Security
  reviewer / Learning scientist / Cost analyst), fixed order, **identical to rung 0** and to Polyphony.
- **Actuator** — append-only catalog: 8-item seed (weight 1.0), **4 items shown/round shared across
  all 5 agents**, popularity = cumulative semantic echo weight (`weight += Σ max(cos(output, shown),
  0)`), sampled without replacement from an immutable pre-round snapshot. Nothing culled.
- **Conditions** — no-catalog ablation / shared-uniform / shared-popularity, run as **paired triplets**
  sharing seed catalog, topic, persona order, and sampling/decoy seeds.
- **Catalog-of-conclusions** — agents see only each other's 1–2 sentence proposals, never reasoning.
  (Rung 2's key manipulation, catalog-of-*reasoning*, is deliberately out of scope here.)
- **Topics + seed catalog** — Polyphony's two R4 topics and its 8-item R3 seed catalog, verbatim.

## Substrate changes (registered) and their rationale

- **Generator:** `gpt-5.6-sol` (effort `none`) → **`deepseek-v4-pro`, thinking ON** (JC1). Rung 1 is
  the control for rung 2, which *requires* thinking on to read `V_reason`; running thinking-on makes
  the only rung 1 → rung 2 change "add the `V_reason` measurement." The effort-`none` difference from
  Polyphony is unavoidable (different model) and is recorded as a substrate caveat, not eliminated. A
  thinking-OFF side-arm (to also bridge to Polyphony's exact effort-`none`) was **considered and
  deferred** — the model already differs, so it buys complexity, not a clean comparison; it can be
  added later as a robustness pass if rung 2 turns on the reasoning layer.
- **Output contract unchanged** — "exactly one feature, one or two sentences, no analysis"; `V_output`
  is measured on the **answer** (the conclusion), exactly as Polyphony. `max_output_tokens` sized to
  allow the reasoning trace plus a ~120-token answer.
- **Embedder held fixed** at `text-embedding-3-small` — the measuring instrument must not vary across
  substrates. (I2/I3 from rung 0 may be added as near-free robustness; the faithful primary is I1.)

## Measurement (Polyphony's, ported)

- **Primary — `V_pair`** (mean pairwise cosine distance of the round's 5 outputs), per-round OLS slope
  over 8 rounds. **Collapse (refute) criterion, verbatim from Polyphony:** popularity `V` slope < 0
  **and** all three bootstrap **95% upper bounds < 0** — popularity slope, popularity − ablation,
  popularity − uniform. (Polyphony: +0.0090 / upper +0.0158 — collapse refuted, V *rose*.)
- **Actuator-live gate — `Δ_U_pop`** (per output, `max cos(out, shown) − max cos(out, decoy)`),
  bootstrap lower bound > 0. **Must pass**, or a `V` null is read off a dead actuator (meaningless).
- **Concentration (secondary, artifact-flagged) — `P_top4`** slope + **the matched null**
  (`null_p_top4.py`, ported). Polyphony's `P_top4` "+0.0102" is reproduced at **151% by a preference-free
  null** — the same artifact class as WS2's withdrawn `ref_gini`. Report `P_top4` **only relative to
  its null**; never claim ensemble concentration from a positive pop−uniform slope.
- **Secondary diversity** — effective dimensionality (scale-invariant → secondary only, never a gate)
  and cluster entropy.
- **Uncertainty** — Polyphony's 10,000-draw **hierarchical bootstrap** (resample paired triplets within
  topic, then the 5 persona indices within each round, same indices across the paired conditions). This
  is CI-led over 8 paired triplets by construction — it structurally avoids the single-run fragile
  binary that rung-0's replication exposed.

## The quantitative upgrade — λ_eff on the imposed ladder (design note §3)

Because rung 0 and rung 1 share personas, place the endogenous actuator's realized conditioning
strength on rung-0's imposed C1/C2/C3 `V_output`-decline ladder: report which imposed cell the
endogenous effect resembles. This turns "no collapse appeared" into "the endogenous actuator reaches
only the strength of imposed cell C_j, below the C_k where `V_output` first moved — *that is why*."

## Registered constants and seeds

`N = 5` · `T = 8` rounds · `exposure_budget = 4` · seed catalog 8 items · 3 conditions · 8 run-ids
(4 per topic × 2 topics = 24 artifacts). Collapse criterion + `Δ_U_pop` + `P_top4` thresholds are
Polyphony's, ported unchanged. **Day-0 gate:** latent diversity ≥ 0.10, alignment shift ≥ 0.03.
**Seeds (registered):** sampling `20260723`, decoy `20260724`, bootstrap `20260718` (Polyphony's, kept
for comparability), null `20260725`. Personas, topics, and seed-catalog text ported verbatim; any
divergence from Polyphony's text is a dated change-log entry, not silent.

## Cost

Day-0 gate ~**$0.10** (~20 calls). Main loop 960 calls on `deepseek-v4-pro` thinking-on ≈ **$1** gen
+ embeddings; the matched null is compute-only. **~$1.5 all-in** — the rung-0 regime.

## Build plan

1. **Gate 0 first.** Port Polyphony's Day-0 checks; drive with `DeepSeekClient` (thinking on) +
   `text-embedding-3-small`; reuse `rung0.mean_pairwise_cosine` / `rung0.anchor_alignment`. TDD the
   token-free parts. **Fire it (~$0.10) before anything else.**
2. Add the graduated `diversity_metrics` package as a dependency; port `catalog.py` (actuator), the R4
   round loop, the confirmatory hierarchical bootstrap, and the `P_top4` matched null. Personas already
   present. TDD every token-free part against Polyphony's committed tests as executable spec.
3. Run the R4 replication (960 calls) → confirmatory analysis → verdict (§ branches).

## Results (post-registration, 2026-07-23)

*Appended, not edited into the locked design above.* Gate 0 PASSED (diversity 0.5816, shift +0.0657 —
stronger than GPT-5.6 Sol). The R4 loop then fired: 24 artifacts (8 run-ids × 3 conditions × 5 personas
× 8 rounds = 960 gens, **$0.61**). Confirmatory analysis (`experiments/analyze_rung1_r4.py`,
10,000-draw hierarchical bootstrap, seed 20260718):

| gate | statistic | value | bound | verdict |
|---|---|---|---|---|
| 1 — dynamic uptake (actuator live) | mean Δ_U_pop | +0.04197 | lower +0.02106 | **PASS** |
| 2 — popularity feedback (`P_top4`) | mean pop−uniform slope | +0.00627 | lower +0.00108 | **PASS** |
| 3 — collapse (`V_pair`) | popularity V slope | −0.00275 | **upper +0.00604** | **FAIL** |
| 3 | popularity − ablation V | −0.00048 | upper +0.00547 | FAIL |
| 3 | popularity − uniform V | −0.00481 | upper +0.00136 | FAIL |

**Verdict: NO COLLAPSE under a live actuator → Polyphony's output-layer null REPLICATES on DeepSeek.
The bridge holds; rung 2 is well-founded.** All three collapse upper bounds straddle zero — the point
V-slopes are slightly negative but not reliably so.

- **The actuator is demonstrably live** (uptake +0.042, feedback +0.0063, both CI-excluding-0). Not a
  dead-actuator null — the mechanism engages and outputs still resist.
- **DeepSeek is flatter than Polyphony, not collapsing.** Polyphony's popularity V *rose* (+0.0090);
  DeepSeek's is −0.00275 (CI straddles 0), and pop−ablation ≈ 0 — the catalog adds essentially nothing
  to a slightly-declining baseline. Closer to collapse than GPT-5.6, but no reliable collapse.
- **The Day-0 "conditions harder" hint did not translate.** DeepSeek's stronger per-round conditioning
  (+0.066) did not compound into multi-round output homogenization; the substrate-specific-collapse
  branch is retired.
- **Gate 2 concentration is a SAMPLING ARTIFACT (matched null, 2026-07-23,
  `experiments/analyze_rung1_null.py`).** Replay validates the process model to **2.2e-16**; the
  preference-free POPULARITY−HETEROGENEOUS null reproduces the observed pop−uniform +0.0063 at **232%**
  (+0.0146), and the popularity arm is indistinguishable from / *below* its matched null (raw excess
  −0.003, p=0.19; normalized excess −0.072, p=0.004). So the recurrence is a property of
  popularity-weighted sampling of a growing catalog, not ensemble concentration — the same artifact
  class as WS2's `ref_gini` and Polyphony's +0.0102. (The uniform *control* shows a small raw excess
  +0.0053/p=0.004 that vanishes when normalized — the same after-the-fact non-result Polyphony had.)

**Rung 1 is complete.** Polyphony's *full* R4 pattern reproduces on DeepSeek across a different model
family: a live actuator, outputs that do not homogenize, and a `P_top4` concentration that is a
sampling artifact. The bridge holds three ways; rung 2 (add `V_reason`) is well-founded.

## What rung 1 deliberately does not do

Not `V_reason` (rung 2). Not catalog-of-reasoning (rung 2). Not the imposed-λ* grid (rung 3). Not the
cross-model panel (rung 4). Rung 1 is the **endogenous output-layer bridge** — the control that earns
the right to read the reasoning layer.
