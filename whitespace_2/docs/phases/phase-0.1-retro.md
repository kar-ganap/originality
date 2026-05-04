# Phase 0.1 Retro

**Phase:** 0.1 (Stage 0 — Foundation)
**Window:** 2026-04-23 → 2026-05-04
**Author:** Kartik Ganapathi (with Claude assistance)
**Status:** Complete; Phase 0.2 pre-registration is the forward-looking
companion document at `docs/phases/phase-0.2-plan.md`.

---

## What Phase 0.1 was supposed to do

Per `phase-0.1-plan.md` §"Why this phase exists", Phase 0.1 was the
**empirical scoping phase** between Phase 0 (which committed to the
program-level whitespace-2 thesis on demographic-vs-intellectual
plurality decoupling) and Phase 0.2 (which would lock the
pre-registration for Stage 1 production work). Three sub-goals:

1. **Lock methodology commitments** that depend on empirical
   characterization of OpenAlex CS+Physics 1970-2024 — the
   analytical-population definition (§0), drift-mitigation ladder
   (§2 + §3), demographic-feature inference policy (§4 + §9), and
   subfield-partition strategy (§5 + §11).
2. **Surface unknowns** that would otherwise become Phase 0.2
   surprises — abstract-availability rate, country-coverage rate,
   disambiguation error rate, classifier drift, embedding drift,
   metric-convergence sample sizes, gender-inference coverage.
3. **Build the embedding pipeline scaffold** (Phase 0.1.E) so
   Stage 2's metric computation has working machinery and pinned
   model versions.

Hypothesis: empirical findings would refine the plan but not
fundamentally retire its commitments. (This held — see "Plan
revisions" below.)

---

## What happened

Phase 0.1 ran 8 sanity checks plus the embedding-pipeline scaffold
plus one wholesale plan revision (N1) plus N1+ adjustments. All
artifacts in `experiments/phase-0.1/`. Summary:

### Sanity checks completed

| Check | What | Outcome | Plan-impact |
|---|---|---|---|
| 1 | Abstract availability by year | ~50% bottleneck across all year × field × type cells; structural, not method-induced | §0 restricted to `has_abstract`; §9e selection-bias-correction layer added |
| 1c | By paper type | Articles 45% (CS) / 60% (Physics); type-restriction yields only ~3pp improvement | Type-restriction closed as rescue path |
| 1d | arXiv linkage via OpenAlex `locations` | 1.4% (CS) / 4.8% (Physics) post-1991; doesn't scale | arXiv-linkage rescue closed |
| 1e | S2AG cross-source rescue | 2.2-5.2% fill rate on no-abstract subset; below 50% viability threshold | S2AG rescue closed; OpenAlex is the ceiling |
| 1f | Bias of missingness | Citation tertile gap 26pp in CS; concept (semantic) and country (demographic) biases also present | §9e selection-bias-correction commitment locked; §9a P5 ORCID-validation methodology informed |
| 1f-followup | Country-extraction sanity | Current `extract_first_country` produces ~45%; raw-affiliation-parsing fix is a Stage-1 commitment | §0 P_demo bound noted |
| 2 (a-c) | Concept classifier drift | Initially appeared 95% off-target; Check 2 correction revealed score-thresholding artifact | §3 score-thresholding policy locked; lessons.md entry on extreme-claims verification |
| 2-correction | Score-threshold reapplication | Off-target rate is 30-76%, expected given OpenAlex's `concepts.id` ignoring score | Always score-threshold ≥0.3 (loose) or ≥0.5 (strict) |
| 2d | Anachronism audit | Within-window keyword-match false positives confirmed for hard-category modern concepts | Junk-year-token filter committed; embedding-cluster preferred over concept-tag for subfields |
| 2d-within-window | Refinement | Hard-category tags fire on pre-1990 papers via keyword match without semantic context | §11 cluster-fit advantage substantiated |
| 2a-redesigned | Venue-anchored field-tag drift (post-N1) | Clean null (slope <0.002 /yr); analytical population is era-clean at field-tagging step | Bias channel ruled out |
| 2e | Hand-audit setup | Audit framework prepared; harvested into Phase 0.2 |  |
| 4 | OpenAlex disambiguation spot-check | 3.0% cross-era-merger rate; consistent with §10's 5-10% total-error band as a lower bound | §10 reaffirmed; Culbert non-Western over-merge surface added (post-Tier-2A close-read) |
| 5a | Pilot pull validation | 467 papers in §0 P; pull spec (concepts.id + score≥0.3 + has_abstract + junk-year filter) locked; 4-5× over-sample needed for production | Pull spec locked; Stage 1 sizing implication recorded |
| 5b | Metric convergence on cs 2024 (10K papers) | All 4 metrics converged within pre-registered bands: cluster_entropy=200, effective_dim=1000, mean_pairwise_cosine=200, demographic_shannon=500 | Per-metric N_target locked for Phase 0.2 |
| 5c | Drift pilot on 100 cs 1970-1980 + era-balanced pool | SPECTER2 era-match 62.8% [CI 57.0%, 68.6%]; gray-zone outcome → commit Flavor A as cheap insurance per §2; H7 hand-audit FAILED at 66.7% reinforcing the commit | Flavor A locked; three pull-spec follow-ups surfaced (strict ≥0.5 score threshold, expanded junk-year tokens, empty-abstract filter) |
| 5d | Cluster-fit stratification artifact | Pilot scale: K=50 negative control fails (small-N instability with \|S\|=316); K=30 directional signal (S/U ratio 1.36) consistent with §11 just below 1.43 threshold | §11 commitment retained; production-scale re-validation locked for Phase 0.2 |
| 3 | Demographic inference coverage | gg + Genderize methods agree 99.7% on assignments; H5 fails 0/10 cells under both (Physics underperforms CS due to East-Asian / transliterated names); H6 confirms ~52% country (Check 1f); H7 ABOVE band 9/10 cells (ORCID back-propagation) | NamSor escalation locked; §9e confirmed; §9a P5 generously sized |

### Embedding pipeline scaffold (Phase 0.1.E)

- `src/whitespace2/embeddings.py` — three-model pipeline (SPECTER2 +
  SciNCL + Qwen3-Embedding-0.6B) at 768-dim via Matryoshka.
- 9 slow tests in `tests/test_embeddings.py`, all green.
- HF revisions pinned in `data/metadata/embedding-model-pins.csv`.
- `experiments/phase-0.1/embedding-pipeline-smoke.md` artifact.
- H1-H6 confirmed; **H7 (timing) failed plan §1 estimate by 15-70×**:
  actual M-series MPS fp16 timing is 0.16-4.2 s/abs vs planned
  0.004-0.065 s/abs. At Stage 2 N=500K, naive triple-pass would take
  ~643 hrs locally — Stage 2 compute prior shifted strongly toward
  cloud GPU.

### Plan revisions

- **N1 wholesale revision (mid-Phase-0.1)** — restructured plan
  around §0 (analytical-population narrowing), §3 (subfield drift
  ladder), §9 (demographic-inference uncertainty stack with new §9e
  selection-bias correction layer). Touched §1, §3, §4, §5, §9a,
  §9b, §12, §13, §14. New §9e introduced.
- **N1+ adjustments** — country-extraction sanity check; §9e
  blast-radius diagnostic; stats primer §18 (MAR / MNAR / IPW).
- **Inline post-check additions** — Check 5c outcome appended to §2;
  Check 5b N_targets appended to "Open decisions deferred" with
  Phase 0.2 commitment language; Check 5d outcome appended to §11;
  Check 3 outcome appended to §4.

### Tier 2A literature engagement

Surface reads + structured review files for the 4 highest-priority
post-N1 Tier 2 papers (Culbert, Kozlowski, Wu-Wang-Evans, Funk).
Each .md file contains Background, Key Ideas, Three-Level discourse,
Connection to Our Project, Key Quotes, Study Questions, Challenge
Corner, Synthesis Pointers, Discussion Notes (skeletal), Surfaces
flagged.

Discussion-Notes sections await collaborative review (not gating
Phase 0.2 pre-registration; they feed Methods drafting at Stage 3).

---

## Surprises

The work-defining surprises of Phase 0.1 in chronological order:

### 1. The 50% abstract bottleneck

Pre-Phase-0.1 expectation was "abstract coverage ≥95% post-1990 in
OpenAlex CS+Physics" based on Phase 0 conversational priors. Check 1
showed coverage hovering at **~50% across the 1970-2024 window**,
including post-1990 cells. This isn't a method-induced artifact —
direct ID lookup confirmed the missing abstracts are not in
OpenAlex's data state.

Implication: §0 became a hard `has_abstract` restriction on the
analytical population, NOT just a fallback policy. §9e selection-
bias correction layer was new methodology surfaced by this finding;
it propagates to every downstream commitment.

Lesson logged in `tasks/lessons.md`: don't trust pre-empirical
coverage assumptions on a substrate; characterize empirically before
locking population.

### 2. The 95% off-target finding that wasn't

Initial Check 2 reported that 95% of `concepts.id`-tagged Operating-
Systems papers had Operating-Systems concept score 0.0 — an apparently
catastrophic classifier failure. User pushback ("are you reading the
right field?") triggered verification.

The actual finding: OpenAlex's `concepts.id:X` filter ignores the
concept's score and returns any paper where X appears in the
`concepts` array, INCLUDING papers the classifier scored at 0.0
(considered-but-rejected). The 95% rate was the size of the
*considered* set, not a classifier failure.

Methodology implication: always score-threshold concept-tag
membership client-side. ≥0.3 for loose population restriction; ≥0.5
for strict subfield identity. Lesson logged: extreme empirical
claims warrant verification before bake-in.

### 3. Phase 0.1.E H7 timing — 15-70× slower than plan §1

Plan §1 estimated SPECTER2 at 0.0036-0.011 s/abs and Qwen3 at
0.025-0.065 s/abs on M-series MPS fp16. Actual smoke timing on the
dev hardware: 0.237 s/abs SPECTER2, 4.228 s/abs Qwen3 (with naive
batching) — 15-70× slower than estimate.

At Stage 2 N=500K abstracts, the naive triple-pass would take ~643
hours locally vs the planned ~half day. Sorted-batching mitigation
brings Qwen3 down to ~0.7 s/abs, which is tolerable but still slow
for robustness sweeps.

Implication: deferred Stage 2 compute decision (local vs cloud)
shifted strongly toward cloud GPU. Lesson logged: planning estimates
on hardware-dependent timings are assumptions, not measurements.
The PLAN→TEST→IMPLEMENT→VERIFY discipline is exactly what surfaces
this.

### 4. Check 5c H7 hand-audit failure

Check 5c's date-based era-match metric (whether top-10 NN of a
1970-1980 query paper are pre-1990) gave SPECTER2 = 62.8% (gray
zone, commit Flavor A as cheap insurance). The H7 qualitative
audit was supposed to validate the date-based metric against
human topical-relatedness judgment. **The audit failed at 66.7%
agreement (vs ≥80% threshold), and the failure was asymmetric**:
Type A errors (date=match BUT NOT topical) at 47% of pairs vs
Type B (date=mismatch BUT topical) at 20%.

Implication: the date-based metric *understates drift severity*.
Many "successful era-matches" are surface-vocabulary coincidences
between unrelated old papers, not actual topical retrievals. Under
a strict topical-match metric, SPECTER2 would push toward 33% —
firmly into "drift severe." The pre-registered cheap-insurance
commitment reinforces toward firm-commit.

Methodology lesson: pre-register a qualitative-validation hypothesis
alongside any date/proxy-based primary metric. The negative-control
Type-A/Type-B decomposition is what made the failure interpretable
rather than mysterious.

### 5. Check 5d K=50 negative control failure (small-N instability)

Check 5d's §11 stratification validation expected the unstratified
fit to concentrate held-out 1975 papers in fewer effective clusters
than the stratified fit. At K=50 (primary), the result was the
*opposite* (effN ratio 0.72) AND the negative control on cs 2020
also failed (29.5% rel diff > 20%). At K=30 — the only K with
passing negative control — the H_1975 ratio was 1.36, directionally
consistent with §11 but just below the pre-registered 1.43
threshold.

The mechanism: pull underrun on the stratified pool (|S|=316 vs
target 480, due to early-decade low retention on single-call sampling)
put us in the small-N cluster-fit regime where K=50 with N=316 averages
~6 papers per cluster and KMeans is noise-dominated.

Implication: §11 commitment STAYS (literature support + K=30
directional signal); Phase 0.2 must re-validate at production scale
(|S| ≥ 1500). Pull-spec follow-up: per-decade supplemental seeds.

Methodology lesson: when a pre-registered threshold fails, look at
the test's negative control before treating the failure as
substantive. Negative controls convert mysterious failures into
legible methodology issues.

### 6. SPECTER2 full-run timing 2× smoke estimate

Smoke (388 abs) clocked SPECTER2 at 0.229 s/abs. Full run (11K abs)
clocked **0.423 s/abs** — nearly 2× slower. Same model, same device,
same dtype, same batch size. Probable causes: thermal throttling
over a 78-min sustained run, memory pressure, tokenizer overhead at
scale.

Implication: smoke-mode timing extrapolation underestimates full-
scale wall-clock. For Stage 2 cloud-vs-local decision, use the
FULL-RUN factor (0.423) not smoke (0.229) as the prior. At N=500K,
local M-series triple-pass with this factor is ~58 hrs (not the
~32 hrs Phase 0.1.E projected) — reinforces cloud-leaning prior.

### 7. Genderize free-tier-no-key throttle

Pre-flight finding for Check 3 was wrong: I assumed Genderize's "free
tier 1000/day" was the no-key limit, but the actual no-key tier is
~100/day per IP. Check 3 hit the wall after ~60 names. Recovery was
twofold: pivot to gender_guesser (offline, free, deterministic) +
use the user-provided keyed-free Genderize tier (2500/mo) as
cross-validation.

The two methods agree at 99.7% on jointly-assigned names; gg is
30pp more conservative on the ambiguous tail. Both fail H5 in 0/10
cells, confirming NamSor escalation as a Phase 0.2 commitment.

Methodology lesson: always look up actual rate limits (not just
headline numbers) and prototype with a small batch before committing
to full runs on third-party APIs.

### 8. ORCID coverage above pre-registered band (with caveat)

Check 3 H7 found pre-1990 ORCID coverage at 13-34% vs pre-registered
<5%. Initial framing: methodology bonus from OpenAlex back-propagating
ORCID from current author profiles. Tier 2A close-read of Culbert
2025 added a noise-floor caveat: OpenAlex's "generous disambiguation"
over-merges non-Western (specifically Chinese) author records,
attributing one ORCID to 10K+ records.

Implication: §9a P5 ORCID-validation methodology adds a 100-record
linkage-validation step (Phase 0.2 commit). The "methodology bonus"
is partially synthetic; the real ground-truth-subsample size is
(ORCID coverage × disambiguation correctness rate).

### 9. Tier 2A close-reads surfaced specification-refinement work

Surface read of Wu-Wang-Evans 2019 + Culbert 2025 + Funk 2026 +
Kozlowski 2022 added several Phase-0.2 specification refinements:
- Test IV regression: explicit quadratic team-size + interaction
  with team-diversity (W-W-E saturation+reversal at team size 8-10).
- Test II: search-depth + search-popularity as cross-check measures
  alongside semantic-distance primary.
- §11 cluster-fit reporting: CV-by-region as third statistic
  (Kozlowski specialization-vs-ubiquity).
- Methods substrate-divergence note: ws2's CS results may diverge
  from W-W-E's pattern by substrate (OpenAlex covers conferences;
  WoS doesn't).
- Introduction framing: "documentation-to-explanation" turn per
  Funk 2026.

These don't retire commitments; they refine specifications already
queued.

---

## What carries to Phase 0.2

Phase 0.2 pre-registration (`docs/phases/phase-0.2-plan.md`) consolidates
the following commitments surfaced during Phase 0.1:

### Locked (no further investigation needed)

1. **§0 analytical population**: CS or Physics × `concepts.id:X` × score
   ≥ 0.3 × `has_abstract` × junk-year-token filter (pre-1990 only) ×
   suspected-empty-abstract filter.
2. **§3 score-thresholding policy**: ≥0.3 loose for population
   restriction; ≥0.5 strict for tight subfield identity (pre-registered
   per use case).
3. **§4 demographic features**: gender (Genderize p≥0.8 + NamSor on
   low-confidence subset + ORCID validation) + country (OpenAlex
   institution ROR with raw-affiliation-parsing fallback) + career
   stage + prestige tier + institution type.
4. **§9 cost gate**: NamSor budget ($0-$500) within the existing
   plan budget; pre-commit estimate logged in `tasks/spend.md`.
5. **§9e selection-bias correction layer**: IPW-corrected aggregates
   over P_demo (the ~45% of OpenAlex CS+Physics with abstract AND
   determinable country); both inference-uncertainty and selection-
   uncertainty bands reported on every headline.
6. **§11 cluster-fit stratification**: K=50 on a temporally-stratified
   pool (equal papers per decade, |S| ≥ 1500 production scale);
   K∈{30, 50, 100} robustness; centroids committed as cluster-fit
   manifest.
7. **§2 drift mitigation**: Stage 2 default = SPECTER2 + SciNCL +
   Qwen3-0.6B + anchor-projection (Mitigation 4); **Stage 3 Flavor A
   committed** (Word2Vec-per-decade + Procrustes) per Check 5c
   gray-zone outcome.
8. **Per-metric N_target** (Check 5b): cluster_entropy=200,
   effective_dim=1000, mean_pairwise_cosine=200, demographic_shannon=500.

### Phase 0.2-specific commitments to lock in pre-registration

1. **Pull spec tightenings**: strict ≥0.5 score threshold for analytical
   population (Check 5c); expanded junk-year token list (chip names +
   non-English content patterns); empty-abstract filter (minimum N
   tokens after decoding).
2. **NamSor escalation pipeline** for low-confidence gender subset;
   cached per-name responses.
3. **§11 production-scale re-validation** with per-decade supplemental
   seed pulls (matching the unstratified-pool pattern from Check 5d).
4. **100-record ORCID-linkage validation** stratified by name region,
   before §9a P5 uses ORCID as gender-inference ground truth.
5. **CV-by-region** as a third statistic in §11 cluster-fit reporting
   (alongside cluster entropy and effN). Per Kozlowski 2022.
6. **Test II three-spec team-size pre-registration**: control
   (W-W-E within-author), predictor (Petersen 2025), stratified.
7. **Test II multi-measure intellectual scope**: semantic-distance
   primary + W-W-E search-depth + search-popularity as cross-check.
8. **Test IV quadratic team-size + interaction** (W-W-E saturation+
   reversal); team-diversity × team-size interaction.
9. **Methods substrate-divergence note** for CS-specific results
   (W-W-E used WoS journal-only; ws2 uses OpenAlex including
   conferences).
10. **Funded-research-bias acknowledgment** in Limitations (W-W-E
    Fig. S30).
11. **Fractional probabilistic counting** for §9a P5 + §9e composition
    (Kozlowski 2022 + Lockhart 2023 P5 lineage).
12. **Snapshot-pinning + post-snapshot errata check** before
    publication (Culbert 2025 volatility findings).
13. **Introduction framing**: "documentation-to-explanation" turn
    per Funk 2026; workforce-composition niche claim defensibility.
14. **Reviewer pre-emption** via Funk 2026 inventory citation; trio
    engagement (Park-Leahey-Funk 2023, Holst 2024, Petersen 2025);
    Park 2025 added as Tier 1B.

### Stage-1 prereqs (deferred from Phase 0.1.E)

1. **Qwen3 sorted-by-length batching benchmark**. Phase 0.1.E
   surfaced that naive bs=8 is ~4× slower than bs=1 due to padding
   waste against Qwen3's 32K context. Implement length-sorted batching
   in `embed_qwen3`; re-time under naive-bs=8 / sorted-bs=8 / sorted-
   bs=32; use best-strategy timing for the cloud-vs-local Stage-2
   decision.
2. **Stage 2 compute target (cloud vs local)** — locked at Stage 1
   with full-run timing prior (0.423 s/abs SPECTER2 per Check 5b
   surface), Qwen3 sorted-batch result, Check 5b N_target, and user's
   time-vs-budget preference at decision point.
3. **Genderize.io paid-tier API key procurement** if production-scale
   gender inference exceeds the keyed-free 2500/mo tier. ws2 desideratum
   §9 pre-commit estimate required.

---

## Validation gates

Per `phase-0.1-plan.md` "Validation gates (go/no-go for Stage 1)":

| # | Gate | Status | Evidence |
|---|---|---|---|
| 1 | All sanity checks 1–5 complete with documented outcomes | ✅ | 8 checks (1, 2, 3, 4, 5a, 5b, 5c, 5d) + extensions, all in `experiments/phase-0.1/` |
| 2 | Methodology commitments §0-§14 finalized in plan | ✅ | N1 wholesale revision + N1+ + inline post-check updates; `phase-0.1-plan.md` ~2000 lines |
| 3 | Phase 0.1.E embedding pipeline scaffold implemented + tested | ✅ | `src/whitespace2/embeddings.py` + 9 slow tests + smoke artifact |
| 4 | Phase 0.2 pre-registration draft underway | ✅ | `docs/phases/phase-0.2-plan.md` is the companion to this retro |
| 5 | Tier 1 lit review complete | ✅ | 7 papers in `literature-review/` |
| 6 | Tier 2A close reads + structured review files complete | ✅ | 4 papers (08, 14, 15, 16) with .md files; collaborative review pending (not gating Phase 0.2) |
| 7 | All `tasks/lessons.md` entries logged | ✅ | 9 lessons spanning 2026-04-27 → 2026-04-30 |
| 8 | Spend tracked at $0 incurred | ✅ | `tasks/spend.md` records OpenAlex anonymous + Genderize keyed-free at $0 each |
| 9 | All key references and pull artifacts pinned to snapshot date | ✅ | `data/metadata/embedding-model-pins.csv` + per-artifact snapshot date |
| 10 | Retro written (this document) | ✅ | This document |

**All Phase 0.1 validation gates met. Phase 0.2 unblocked.**

---

## Lessons (consolidated)

Pulled from `tasks/lessons.md`. Cross-cutting themes:

**Don't trust pre-empirical assumptions on data substrates.** Three
of the load-bearing surprises (50% abstract bottleneck, 55% country
undeterminable, H7 timing 15-70× over budget) trace to substrate-
behavior assumptions that didn't survive empirical contact.

**Verify extreme claims before baking them into commitments.** The
Check 2 95% off-target episode would have produced a substantively
wrong Phase 0.2 commitment had user pushback not triggered
verification. Pattern: any single number that *feels* too extreme,
verify before committing.

**Pre-register negative controls on every directional hypothesis.**
The Check 5d K=50 outcome was interpretable only because the
negative control (cs 2020) failed alongside the primary. Without a
negative control, "S/U ratio = 0.72" reads as "§11 mechanism reversed";
with the negative control, it reads as "the test is internally
broken at this scale."

**Pair every proxy metric with a qualitative validation
hypothesis.** Check 5c's date-based era-match was a proxy for
topical-era-match; the H7 hand-audit caught the 47% Type-A error
rate that the proxy hid. Discipline applies broadly: date-based
proxy → qualitative validation; threshold-based proxy → fractional-
counting alternative; majority-class proxy → minority-class
sensitivity check.

**Sanity checks at one phase generate constraints that lock later
phases.** Check 5c surfaced three Phase-0.2 follow-ups (strict
score threshold, junk-year tokens, empty-abstract filter); Check 3
locked NamSor escalation; Check 5d locked §11 production-scale
re-validation; Check 5b locked per-metric N_target. Discipline:
each check's surprises produce explicit Phase-0.2 follow-ups, not
inline commentary.

**Smoke-mode timings underestimate full-scale wall-clock for
sustained-load embedding compute.** The 0.229 → 0.423 s/abs SPECTER2
gap (smoke vs full) was not visible in 50-abstract smokes because
sustained thermal load + memory pressure don't kick in. For
compute-decision priors, use full-scale empirical numbers.

**API rate limits in the wild differ from documented free tiers.**
Genderize free-tier-no-key throttles much more aggressively than
"1000/day" suggests. Pre-flight check on actual recent throttle
behavior, not just docs, before committing to full runs.

**A commitment surviving a methodologically inconclusive validation
is not a methodology retreat.** §11 stratification commitment
survived Check 5d's pilot-scale inconclusive outcome because the
literature support + K=30 directional signal + small-N-explained
failure are jointly defensible. Phase 0.2 commits to production-
scale re-validation, not to retiring §11. Be honest about what
survived and what's pending.

---

## What I'd do differently next phase

1. **Pre-register hypotheses with calibrated thresholds, derived
   from filter-stack arithmetic.** Check 5a's H1 (75% retention)
   threshold was a leftover from a pre-N1 mental model; it produced
   misleading "FAIL" labels on data that was structurally exactly
   what the N1 filter stack predicted. Phase 0.2 thresholds should
   be derived from explicit filter-loss arithmetic, not from
   priors.

2. **Allocate budget for negative controls upfront.** Check 5d's
   negative-control commitment was load-bearing post-hoc. Phase 0.2
   should pre-register negative controls for every test (Test I,
   II, III, IV) explicitly, not as an afterthought.

3. **Smoke-test third-party APIs before committing to full runs.**
   Specifically Genderize and (when we get there) NamSor — run a
   ~50-name batch with timing + rate-limit observation before
   committing to a 100K-name production run.

4. **Time the Tier 2A close-read pass earlier in the phase.** The
   close-reads were done at the very end of Phase 0.1; they
   surfaced specification refinements (W-W-E quadratic team-size,
   Kozlowski CV diagnostic) that ideally would have been caught
   during the plan-revision step. Phase 0.2's analog: do Tier 2B
   methodology-notes up front, not at the end.

5. **Include "what would falsify this?" in each pre-registered
   hypothesis.** Some Phase 0.1 hypotheses (e.g., 5c H6 SPECTER2
   prediction band) were specified with a narrow point estimate and
   wide pass criteria, which made the "passed" bookkeeping less
   informative. Phase 0.2 hypotheses should include explicit
   falsification conditions.

---

## Open questions explicitly carried forward

These are NOT Phase 0.2 commitments; they're open questions Phase
0.2 will need to resolve along the way.

1. **Stage 2 compute target** — local M-series MPS vs cloud GPU
   (Modal A10G default). Locked at Stage 1 with full-run timing +
   Qwen3 sorted-batch result + Check 5b N_target. Plan §1 + this
   retro.

2. **Production-scale N** — 500K vs 1M vs 2M. Driven by Check 5b
   N_target (locked) + per-year Nᵧ distribution (Check 5a) + cost
   commitment.

3. **NamSor budget commitment** — $0-$500 range from §9 cost
   compass; specific number depends on low-confidence-subset size at
   production scale.

4. **Pre-1990 specifically** — Culbert 2025's data is 2015-2022;
   we have no direct cross-substrate evidence on OpenAlex's pre-1990
   data quality. Phase 0.1 Checks 1-2-4 are our pre-1990 diagnostic
   stack; whether additional pre-1990-specific validation is needed
   for Stage 1 is open.

5. **Phase 0.2 → Stage 1 transition gating** — Phase 0.2 lands the
   pre-registration; Stage 1 begins the production pull. The
   transition gating includes user signoff on the pre-registration
   document, ORCID-linkage validation result, and Stage 1 prereqs
   (Qwen3 batching benchmark, compute decision).

---

## Phase 0.1 close-out

Phase 0.1 substantively delivered:
- 8 sanity checks + extensions, all artifacts committed.
- Wholesale plan revision (N1) absorbing empirical findings.
- Embedding pipeline scaffold (Phase 0.1.E) with model-version pinning.
- Tier 1 (7 papers) + Tier 2A (4 papers, surface-read + structured
  review files) literature engagement.
- 9 logged lessons + this retro.
- All Phase 0.2 commitments queued and consolidated in
  `docs/phases/phase-0.2-plan.md`.

The phase ran ~10 days. Productivity drivers: clean PLAN→TEST→
IMPLEMENT→VERIFY discipline; user pushback that caught a substantively-
wrong commitment before bake-in (Check 2 95% off-target episode);
multiple plan revisions absorbed without deferred-debt accumulation.

Phase 0.2 is unblocked. The pre-registration document is the
forward-looking companion to this retro.
