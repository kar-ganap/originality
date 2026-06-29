# Phase 1.2 H2 hand audit — results

**Status:** Complete (100/100 reviewed). Source sheet:
`h2-audit-sheet-v2.md`. Sample: `section0-sample-1M-v2.parquet`
(v2 corpus, post-type-allow-list amendment). Audit seed:
`ws2-phase-1.2-h2-audit-seed-v1`. Single reviewer (Kartik).

This document distills the 100-paper hand audit into:
1. The final tally (overall + per-stratum).
2. The patterns of §0 false positives we found and their
   frequency.
3. A ranked §0 v3 amendment proposal with bias-risk analysis and
   expected impact.
4. The substantive scope call (pure math in or out?) that needs
   resolution before v3 lands.
5. Limitations of this audit.

## 1. Final tally

100 papers, stratified 50 uniform-random + 50 pre-1990
(pre-registered design; the pre-1990 oversample exists because
the dominant pre-1990 risk — `JUNK_YEAR` from post-2000 tokens
slipping past the word-boundary regex — is rare in a uniform
draw).

| Verdict | Uniform (1-50) | Pre-1990 (51-100) | Total |
|---|---|---|---|
| **OK** | 21 | 21 | **42 (42%)** |
| `FLAG: WRONG_FIELD` | 18 (+1 compound) | 24 | **42 (42%)** |
| `FLAG: BAD_ABSTRACT` | 2 (+1 compound) | 0 | **3 (3%)** |
| `FLAG: BORDERLINE` | 9 | 5 | **14 (14%)** |
| `FLAG: JUNK_YEAR` | 0 | **0** | **0** |

- **Hard FLAG rate** (`WRONG_FIELD` + `BAD_ABSTRACT`, excluding
  borderline): 44/100 = **44%**.
- **Total non-OK:** 58/100 = 58%.
- **JUNK_YEAR: 0/100 (incl. 0/50 pre-1990 spanning 1915–1989).**

Paper 15 is the one compound flag (BAD_ABSTRACT + WRONG_FIELD):
counted once in unique-paper totals.

### 1.a Pre-registered H2 pass criterion vs reality

The audit-sheet header framed "0 FLAGs" as **aspirational**, not a
pass/fail threshold. The intended use was to **characterize
patterns** of §0 false positives, not to certify perfection. The
44% hard-FLAG rate is too high to release into Stage 2 without an
amendment round, but the patterns are sufficiently clustered that
a small set of targeted, low-bias fixes should bring it to an
acceptable range. See §3.

## 2. Patterns of §0 false positives

Six patterns surfaced, in decreasing order of frequency. The
percentages are over the 58 unique flagged papers (not the 100
audited).

### Pattern A — Non-English humanities / social-science papers tagged via weak CS/physics concept

**Count: 8 (14% of flagged).**

Examples:
- #6 Turkish international relations (2014)
- #8 Ukrainian organizational economics (2020)
- #17 Croatian philosophy of science (2004)
- #21 Portuguese Parkinson's + samba music study (2018; borderline)
- #22 Polish education / Roma sociology (2018)
- #77 Brazilian Portuguese transport policy (1958)
- #83 Catalan/French tuberculosis medicine (1934)
- #88 Japanese economics (1973)

**Failure mode:** OpenAlex's concept tagger fires `computer
science (0.34)` or `physics (0.34)` on incidental keywords in
translation. The papers are real research, but in fields adjacent
to or disjoint from CS/physics.

**Demographic correlation:** **High.** Authors disproportionately
non-Western / non-English-publishing. A language filter would
*systematically reduce* the non-Western author signal we're
trying to measure. **Don't filter on language.**

### Pattern B — Publisher chrome and non-research-paper artifacts

**Count: 16 (28% of flagged) — the dominant pattern.**

Sub-patterns with regex signatures:

| Sub-pattern | Count | Signature |
|---|---|---|
| ACS Publications chemistry papers | 6 (#29, #89, #92, #93, #94, #98) | abstract starts with `^ADVERTISEMENT RETURN TO ISSUE` |
| ACS C&EN news articles | 1 (#81) | starts with `^RETURN TO ISSUE.*News` |
| Wiley / Portland Press / OUP chrome | 3 (#3, #66, #87) | contains `Views Icon Views` |
| Article-metrics chrome | 1 (#32) | starts with `^Article Metrics` |
| "Contributors" / front-matter / book reviews | 2 (#15, #72) | title-based |
| Admin / curriculum / bibliography docs | 3 (#19, #33, #36) | residual |
| Municipal comprehensive plans | 1 (#79) | residual |

Two sub-sub-flavors worth noting:
- **#3 / #29 / #89 / #92 / #93 / #94 / #98 / #81 are all ACS-published.**
  ACS's web template puts navigation chrome into the
  abstract field instead of the paper's actual abstract.
  This is a *publisher-level* artifact, not a research-quality
  issue — many of the underlying papers are real research.
- **#15 / #45** are a complementary "publication-status placeholder"
  shape: the abstract field is *"This is the author's version of
  a work that was accepted for publication..."* with no paper content.

### Pattern C — Concept-tagger noise (English; real abstract but wrong field)

**Count: 5–6 (~10% of flagged).**

- #1 marketing/statistics methodology paper (consumer research)
- #13 Pacific Islander leadership development (education)
- #28 motor-control / object-lifting neuroscience
- #42 philosophy of time (four-dimensionalism); tagged
  `Intrinsics (0.98)` because of Lewis's *temporary intrinsics*,
  not compiler intrinsics — pure name-match noise
- (#60 ESL classroom correction guideline — also in this family)

**Failure mode:** OpenAlex's concept tagger fires on a vocabulary
keyword that has a CS/physics meaning *and* a different meaning
in another field; the paper uses the other meaning. The
`Intrinsics` failure on #42 is the cleanest example.

### Pattern D — Pure math papers tagged as CS via "Algorithm"

**Count: 3.**

- #7 Tauberian summability theorem (1982)
- #75 Topological decompositions of E³ (1976)
- #97 Statistical sampling from batches (1975)

**Substantive question, not just a noise pattern.** Pure math is
adjacent to CS — TCS, complexity theory, formal methods all live
on the boundary. A blunt "exclude math" filter would risk
excluding real theoretical CS. **Needs a scope call.** See §4.

### Pattern E — BORDERLINE due to inaccessible link / inaccessible content

**Count: 4–5.**

- #27, #34, #39 (uniform), #80 (dissertation), #95 (Navy report)

**Note:** my earlier hypothesis that all broken-link papers had
`W7…` IDs was wrong — only 1 of these 5 does (#27). Most have
standard `W2…/W4…` IDs and the broken link is unrelated to ID
class. Probably a mix of withdrawn/merged works in OpenAlex +
old technical reports without web-accessible PDFs. **Not worth a
filter** — these aren't systematic and the reviewer's BORDERLINE
verdict is the right resolution.

### Pattern F — Agency / standards / technical-report engineering

**Count: 4.**

- #62 DoD inventory management (1981)
- #63 FHWA highway noise barriers (1981)
- #64 ANSI radiobioassay standard (1986)
- #95 Navy adaptive antenna report (1979)

Real research, often well-cited, but in engineering / operations
research / regulatory science — not CS or physics core. Borderline
and ambiguous. The v2 `type` allow-list includes `report` for
exactly this reason; this is the cost of that inclusion. Probably
acceptable — the demographic and semantic signal these add isn't
fundamentally different from other applied engineering work.

## 3. §0 v3 amendment proposal — ranked by impact × bias

The headline failure modes are A (~14% of flagged), B (~28%), and
C (~10%). The fix table:

| Fix | Targets | Killed (of 44 hard FLAGs) | Bias risk | Effort |
|---|---|---|---|---|
| **3.1 Regex blacklist on abstract prefix:** `^(ADVERTISEMENT \|)RETURN TO ISSUE\|^Views Icon Views\|^Article Metrics\|^This is the author's version` | B (publisher chrome) | **12–13** | Zero | Trivial |
| **3.2 Abstract-token minimum 15 → 50** | B (short stubs); A residual | 3–4 (#12, #19, #32, #33) | Mild pre-1990 bias (older abstracts are shorter on average). Pre-1990 already a stratified block, can verify with a pre-1990 dry-run | Trivial |
| **3.3 Concept-score threshold 0.30 → 0.40** | A (most), C (some) | 8–10 | **Low** — threshold is on tagger confidence, not author identity. Mild bias toward better-indexed papers (more recent), tractable to measure | Trivial |
| **3.4 Title-prefix heuristic blacklist:** `"NEW PRODUCTS", "Contributors", "Annex \d+", "Key Messages", "Editorial Board"` | B residual | 2–3 | Very low | Easy |
| **3.5 Pure-math filter** (concept-score on `Mathematics > 0.5` AND no concept above CS/physics threshold) | D | 2–3 | **Depends on §4 scope call** | Medium (correctness) |
| **3.6 Language filter (en-only)** | A (all) | 6–8 | **HIGH demographic bias** — kills non-Western author signal | **DO NOT IMPLEMENT** |

**Combined estimate** of 3.1 + 3.2 + 3.3 + 3.4 (the low-bias
basket): kills **20–25 of 44 hard FLAGs** (45–57%). Brings
hard-FLAG rate from 44% to **roughly 19–24%** — acceptable for
Stage 2 entry, even before considering Pattern E/F residual.

If 3.5 is adopted (depends on §4), add another 2–3 FLAGs killed →
hard-FLAG rate **15–22%**.

**The three highest-ROI moves are 3.1, 3.2, and 3.3.** All three
are trivial to implement, have low or characterized bias risk,
and together kill the dominant patterns (A and B). 3.4 is a
cleanup; 3.5 is the substantive scope choice.

## 4. The pure-math scope call

Phase 0.2 pre-registration framed the analytical population as
"CS + Physics, 1970–2024." Math is implicitly out by being
unnamed, but the boundary is fuzzy:

- **Out:** Tauberian summability theorems, topology of E³,
  classical statistics → no obvious overlap with CS/physics
  embedding space.
- **In:** Theoretical CS (complexity, computability, formal
  methods), mathematical physics, numerical methods — all real
  CS/physics that use math machinery.

**Two acceptable resolutions:**

1. **Strict CS+Physics, math out.** Add a math filter in §0 v3.
   Accept that 3 of the 100 audited papers (pure math tagged via
   `Algorithm`) would be excluded. Risk: nicks some theoretical
   CS borderline work; bias is toward applied/empirical CS.
2. **Loose: math allowed if CS/physics concept present at any
   threshold.** Accept the 3 pure-math FPs as collateral cost;
   they'll appear in the embedding space but their downstream
   semantic-diversity contribution is small. Risk: residual math
   FPs in pre-1990 where math papers are over-represented in
   `Algorithm` tagger.

**Recommendation:** Option 2 (loose) is safer because the
pre-registered analytical population was specified inclusively
and option 1 risks excluding genuine theoretical CS work that
matters for the diversity time-series. The 3 pure-math papers add
~3% noise to a 38M-paper corpus — within the noise floor.

**Decision (locked 2026-06-28):** Option 2 / loose. Pure math
stays in. §0 v3 will *not* add a math filter; the 3 audited pure-
math FPs are accepted as collateral and characterized in this doc
as known noise. If Stage 2 surfaces a measurable math-cluster
effect that distorts the headline test, we revisit with data —
not with a pre-emptive filter.

## 5. Limitations of this audit

1. **Single reviewer, no inter-rater check.** The 44% hard-FLAG
   rate is one reviewer's judgment. A second pass by a different
   reviewer would tighten the confidence interval on every
   number here.
2. **Non-English handicap.** The reviewer can read English /
   Spanish / French / Portuguese / German with varying fluency,
   but not Polish / Ukrainian / Turkish / Japanese / Chinese.
   Some pattern-A flags rely on the title and concept list rather
   than the abstract content. This is fine for "is this primarily
   a CS/physics paper" but may systematically under-detect
   non-English *real* CS/physics papers tagged with weak concept
   scores.
3. **Concept-tagger black box.** OpenAlex's concept-tagger is a
   pretrained classifier; failure modes like `Intrinsics (0.98)`
   on a philosophy paper aren't documented and we can't predict
   which other vocabulary terms will cause similar failures.
4. **Single-snapshot.** The v2 corpus was built against a specific
   OpenAlex snapshot. Re-running against a future snapshot may
   yield different patterns as OpenAlex evolves their `type`
   classification, concept tagger, and abstract field
   extraction.
5. **Stratification deviates from "random 100" of pre-registered
   plan.** The 50 uniform + 50 pre-1990 split was a deliberate
   choice to power JUNK_YEAR detection; documented in the audit
   sheet header and Phase 1.2 retro. Per-stratum FP rates are
   ~40% (uniform) and ~48% (pre-1990 hard FLAG), so the overall
   44% is a slight under-estimate of pre-1990 noise.

## 6. Suggested next actions

1. **User confirms the pure-math scope call** (§4 — recommend
   option 2 / loose).
2. **Implement §0 v3** (`section0_filter.py` + Modal pipeline
   amendment): fixes 3.1, 3.2, 3.3, 3.4 from §3.
3. **Build v3 artifacts** via `build_v3.py` (~$5, ~15 min on Modal).
4. **Re-audit ~30 papers** from the v3 sample (cheap, not a full
   100) using a regenerated stratified audit sheet. Confirm
   hard-FLAG rate drops to ≤20%.
5. **Measure bias** by comparing v2 → v3 along headline axes: %
   non-English papers dropped, % pre-1990 papers dropped,
   demographic shift in author pool. If any axis moves
   disproportionately, narrow the implicated fix.
6. **Close Phase 1.2 RETRO** with both v2 and v3 corpora documented
   as a robustness pair — pre-register that the headline Stage 2
   divergence test will be reported on both corpora as a
   robustness check, per the program's "Multiple metrics per
   experiment" ground rule (applied here to multiple corpus
   definitions).

## 7. v3 build results + spot-check audit (2026-06-29)

### 7.a v3 build

Implemented per §3: regex prefix blacklist + abstract-token-min
15→50 + concept-score 0.30→0.40 + title-prefix heuristic.

**v2 → v3: 38,697,769 → 24,492,279 (63.29% kept).**

Per-stage independent drop accounting (each stage measured over
the full v2 population; numbers don't sum due to overlap):

| Stage | Drops | % of v2 |
|---|---|---|
| `score_ge_0.40` | 11,378,633 | **29.40%** ← dominant |
| `tokens_ge_50` | 4,387,177 | 11.34% |
| `abstract_prefix_ok` | 495,254 | 1.28% |
| `title_prefix_ok` | 5,407 | 0.01% |

The concept-score raise (0.30→0.40) carries nearly all the cleanup.
The publisher-chrome regex caught **~500K papers** (small as % of
v2, but a meaningful absolute reduction of low-signal abstracts).
The title-prefix heuristic was tightly targeted, catching ~5,400
non-paper artifacts (NEW PRODUCTS, Contributors, Annex N, etc.).

### 7.b v3 spot-check audit (30 papers)

Same audit seed as v2 (`ws2-phase-1.2-h2-audit-seed-v1`) so the
papers are directly comparable: the v3 sheet's papers 1-15 and
86-100 were reviewed (uniform-stratum head + pre-1990-stratum tail).

| Verdict | Count | % |
|---|---|---|
| **OK** | 17 | 57% |
| `FLAG: WRONG_FIELD` | 6 | 20% |
| `FLAG: BAD_ABSTRACT` | 0 | 0% |
| `FLAG: BORDERLINE` | 7 | 23% |
| `FLAG: JUNK_YEAR` | 0 | 0% |

**Hard FLAG rate: 20%** (95% CI roughly [8%, 39%] at n=30).
**JUNK_YEAR: still 0** (now confirmed across both audit rounds:
v2 100 + v3 30 = 130 papers, 0 JUNK_YEAR).

### 7.c v2 → v3 comparison

| Metric | v2 (100 papers) | v3 (30 papers) | Δ |
|---|---|---|---|
| OK | 42% | 57% | **+15pp** |
| Hard FLAG | 44% | 20% | **−24pp** |
| BAD_ABSTRACT | 3% | 0% | −3pp |
| BORDERLINE | 14% | 23% | +9pp |
| JUNK_YEAR | 0% | 0% | — |

**v3 hit the §3 target (hard FLAG ≤20%) at the upper bound.**

### 7.d What the v3 residual looks like

The cleanup left genuinely harder patterns:

1. **EE/CS boundary papers** — 3 of 7 v3 BORDERLINEs are
   electrical-engineering papers (signal processing, cellular
   networks, circuit design) that share concepts/methods with CS.
   This boundary is fundamentally fuzzy and cannot be filtered
   without nicking real theoretical CS.
2. **Non-English social-science** — 2-3 papers persisted
   (Turkish IR, Ukrainian econ, pharma chemometrics). The
   concept-score raise eliminated some but not all; these have
   CS concepts at 0.40+ via incidental keywords.
3. **Inaccessible-link borderline** — 1 paper marked BORDERLINE
   because the OpenAlex link was broken; cannot be filtered
   programmatically.
4. **One self-reported rubric inconsistency** — the Croatian
   urban-planning paper used as the "OK example" in §3 of this
   doc was flipped to WRONG_FIELD in the v3 audit. The reviewer
   noted they applied a stricter standard on the second pass.
   Implication: v3's measured 20% hard FLAG is probably a slight
   over-estimate vs the v2-rubric standard. By the v2 standard,
   v3 hard FLAG is likely closer to ~15%.

### 7.e Decision

**Lock v3 as the analytical population for Phase 1.2.** Three
reasons:

1. Hard-FLAG rate is at the §3 target; further amendments
   (e.g., filtering EE, language filtering) would carry larger
   bias risk than the marginal improvement justifies.
2. The big methodological wins are now visible across two audits:
   JUNK_YEAR confirmed 0/130; publisher chrome filtered; concept-
   tagger noise sharply reduced.
3. Residual FLAGs are pattern types (field-boundary ambiguity,
   non-English social-science with strong CS concept tags) that
   are fundamentally hard to filter without selection bias.
   Accepting ~15-20% residual is the principled trade-off
   (per §1.a aspirational framing).

The robustness pair stays in scope: v2 and v3 are both available
on the Modal Volume, and Stage 2 can re-run any headline analysis
on either corpus. If the Stage 2 divergence test changes sign or
magnitude between corpora, that's a finding about §0
sensitivity worth reporting.

### 7.f Build saga (notes for the Phase 1.2 retro)

The §0 v3 build went through three implementation attempts:

1. **Attempt 1 — DuckDB Python UDFs (`type='native'`)**: timed
   out at the 1-hour function timeout. UDF Python/C boundary
   overhead is the bottleneck at 38M rows; never even finished
   the COPY operation.
2. **Attempt 2 — Single-threaded PyArrow streaming + orjson +
   compiled regex**: reached 64% in ~21 min, then was cancelled
   by an unexplained local-client disconnect.
3. **Attempt 3 — ProcessPoolExecutor across 8 row-group workers**:
   filter finished in 299s (5 min) + concat in 624s (10 min).
   Total filter step: ~16 min. Sample step: 79s. Heldouts: 146s.

A separate hang surfaced in the Modal Volume read iterator on
the 310 MB sample download (file fully wrote to disk but iterator
never returned). Resolved by killing the local script and
re-downloading via `modal volume get`, then running
`resume_v3.py` for heldouts + manifests.
