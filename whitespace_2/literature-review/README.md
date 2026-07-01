# Whitespace 2 — Literature Review

This folder is the working home for ws2's methodological literature
review. The review is a parallel track of Phase 0.1 (see sanity Check 6
in `../docs/phases/phase-0.1-plan.md`) and gates Phase 0.2 pre-registration.

## Master reading list

Papers are tiered by methodological dependence. Tier 1 and Tier 2 each
get a structured review file in this folder. Tier 3 is for positioning
reads and reviewer-engagement preparation — no individual review files
unless needed.

### Tier 1 — Direct methodological dependence (close read, deep review)

| # | Paper | Role for ws2 | Status |
|---|---|---|---|
| 01 | **Chu & Evans 2021**, *PNAS* 118(41), "Slowed canonical progress in large fields of science" | Canonical-concentration methodology (Chu-Evans Spearman top-N). Our primary canonical metric inherits their operationalization. | complete |
| 02 | **Park, Leahey & Funk 2023**, *Nature* 613, "Papers and patents are becoming less disruptive over time" | The contested headline we're positioning against. We decline to use CD-index as primary; we must engage this paper. | complete |
| 03 | **Petersen, Arroyave & Pammolli 2024**, *QSS* 5(4), "The disruption index is biased by citation inflation" | Broader citation-inflation critique. **Positioning read (~2 hrs)** justifying CD-index exclusion. | complete |
| 04 | **Petersen, Arroyave & Pammolli 2025**, *J. of Informetrics* 19(1), team-size / CD re-analysis | **Close methodological read (~4 hrs).** Directly challenges Wu-Wang-Evans team-size interpretation — load-bearing for our Test II team-size control and Test IV team-diversity × novelty setup. | complete |
| 05 | **Holst, Algaba, Tori, Wenmackers & Ginis 2024**, arXiv:2402.14583, "Dataset Artefacts are the Hidden Drivers of the Declining Disruptiveness in Science" | Dataset-artifact critique of Park-Leahey-Funk. Load-bearing for 13-F measurement-artifact null. | complete |
| 06 | **Hofstra, Kulkarni, Munoz-Najar Galvez, He, Jurafsky & McFarland 2020**, *PNAS* 117(17), "The Diversity-Innovation Paradox in Science" | Direct precedent for Test IV (team-diversity × novelty). Must engage their novelty-detection pipeline and minority-group operationalization. | complete |
| 07 | **Lockhart, King & Munsch 2023**, *Nature Human Behaviour* 7(7), "Name-based demographic inference and the unequal distribution of misrecognition" | Structural critique of name-based gender/race inference — directly load-bearing for our Genderize+NamSor pipeline. Grounds the "weight-by-confidence" choice in plan subsection 9. | complete |

### Tier 2 — Methodological underpinnings (read for method, not every claim)

**Post-N1 priority + depth (locked 2026-04-28).** N1 plan revision
substantially shifted Tier 2 priorities relative to the pre-empirical
ranking. Two depth tiers within Tier 2:

- **Tier 2A (close read with structured review file, ~3 hrs each):**
  16, 14, 08, 15. These are the papers whose methodology is
  load-bearing for ws2's pre-registered tests OR whose framing N1
  elevated.
- **Tier 2B (methodology notes only, ~1 hr each; full close read
  deferred to Stage-3-if-triggered):** 12, 13, 09, 10, 11. Stage-3-
  conditional or background; no need for full template up front.

Total budget: ~18 hrs (11 hrs Tier 2A + 5 hrs Tier 2B + 2-3 hrs
synthesis.md harvest). Slightly above the original 15 hr budget;
justified by N1's reshuffling of priorities.

| # | Paper | Role for ws2 | Tier | Status |
|---|---|---|---|---|
| 08 | **Wu, Wang & Evans 2019**, *Nature* 566, "Large teams develop and small teams disrupt science and technology" | Team-size confound for Test II AND Test IV. Paired with Petersen 2025 (Tier 1) — read together to resolve the team-size interpretation tension for Phase 0.2 pre-registration. | **2A** | deferred → Stage 3 |
| 09 | **Cohan, Feldman, Beltagy, Downey & Weld 2020**, *ACL*, SPECTER | Background for SPECTER2; methodology not load-bearing. Single combined session with 10+11. | 2B | superseded (empirical validation) |
| 10 | **Singh, D'Arcy, Cohan, Downey & Feldman 2023**, *EMNLP*, SciRepEval (arXiv:2211.13308) | SPECTER2 training/evaluation; methodology not load-bearing. Combined with 09+11. | 2B | superseded (empirical validation) |
| 11 | **Ostendorff, Rethmeier, Augenstein, Gipp & Rehm 2022**, *EMNLP*, SciNCL (arXiv:2202.06671) | Within-family robustness partner; we use it but methodology details aren't load-bearing. Combined with 09+10. | 2B | superseded (empirical validation) |
| 12 | **Hamilton, Leskovec & Jurafsky 2016**, *ACL*, "Diachronic Word Embeddings Reveal Statistical Laws of Semantic Change" | Methodology template for Stage 3 Flavor A drift mitigation — *conditional* on Check 5c drift-pilot triggering Flavor A. Defer full close read until then. | 2B | deferred → Stage 3 |
| 13 | **Uzzi, Mukherjee, Stringer & Jones 2013**, *Science* 342, "Atypical Combinations and Scientific Impact" | Test IV tertiary novelty (Stage 3 only, contingent on Stage 3 bandwidth). Note: fourth author is Stringer, not Stone. | 2B | deferred → Stage 3 |
| 14 | **Kozlowski, Larivière, Sugimoto & Monroe-White 2022**, *PNAS* 119(2), "Intersectional inequalities in science" | Intersectional demographic-topic methodology. **Elevated post-N1** because intersectional reporting under §9e propensity weighting is structurally complex; Kozlowski's framework likely informs Methods-level decisions about how to report intersectional cells. | **2A** | pending |
| 15 | **Funk et al. 2026**, arXiv:2602.05140, "Is Innovation Becoming Less Disruptive? An Inventory of the Literature" | Canonical literature inventory. Reviewer-engagement piece. Lighter close read (~2 hrs) since it's mostly inventory. | **2A** | pending |
| 16 | **Culbert et al. 2024/2025**, *Scientometrics*, "Reference coverage analysis of OpenAlex compared to Web of Science and Scopus" | **Highest post-N1 priority shift.** §0/§9e are OpenAlex-specific commitments; this paper informs whether the ~50% abstract bottleneck and 55% UNKNOWN-affiliation rate are OpenAlex-specific or universal. Could also surface a WoS/Scopus cross-substrate robustness check for Stage 3. | **2A** | pending |

### Tier 3 — Secondary (positioning / reviewer engagement, no review file required)

- **Foster, Rzhetsky & Evans 2015**, *ASR*, "Tradition and Innovation in Scientists' Research Strategies" — strategy-frequency framing
- **Clauset, Arbesman & Larremore 2015**, *Sci Advances*, "Systematic inequality and hierarchy in faculty hiring networks" — prestige hierarchy grounding for Proxy A
- **Zheng et al. 2025**, *JASIST*, OpenAlex China coverage — relevant if cross-national analysis matters
- **Chaney, Stewart & Engelhardt 2018**, *RecSys*, algorithmic confounding — 13-A positioning
- **Kleinberg & Raghavan 2021**, *PNAS*, "Algorithmic monoculture and social welfare" — 13-A positioning
- **Bommasani et al. 2022**, *NeurIPS*, "Picking on the Same Person" — 13-A positioning
- **Azoulay, Graff Zivin & Manso 2011**, *RAND J. Econ.*, "Incentives and Creativity" — 13-C positioning
- **Wahle, Ruas, Abdalla, Gipp & Mohammad 2024**, arXiv:2402.12046, "Citation amnesia" — 13-A positioning
- **Priem, Piwowar & Orr 2022**, arXiv:2205.01833, OpenAlex introduction
- **Killick, Fearnhead & Eckley 2012**, *JASA*, PELT changepoint algorithm — break-point robustness

## Template for per-paper reviews

Create each file as `XX-<first-author-lastname>-<year>-<short-title>.md`
(e.g., `01-chu-evans-2021-canonical-progress.md`). Use the sibling
project convention (`inverse-device-design/literature-review/` format)
with the three MUST-have elements pinned as non-negotiable:

```markdown
# XX — Full Paper Title

**Authors:** (full list)
**Venue:** (journal / conference / arXiv ID)
**PDF:** `literature-review/XX-<slug>.pdf` (gitignored — download locally)
**DOI/URL:** (link)

---

## Background

(1–2 paragraphs of context: what problem the paper addresses, what
state of the literature it enters, what the authors were responding to.)

---

## Key Ideas

### 1. (First key idea as section header)

(Substantive explanation.)

### 2. (Second key idea...)

(etc.)

---

## Results — Three Levels

### Level 1: For a smart high-schooler

(Accessible explanation, no jargon assumed. 1–2 paragraphs.)

### Level 2: For a junior/senior undergraduate

(Mid-level technical explanation assuming undergraduate exposure to
the field. Introduces domain-specific terminology but explains it.)

### Level 3: For an early graduate student

(Methodological depth, technical precision, honest assessment of
what is and isn't established. This is the level at which the paper's
failure modes and limitations become visible.)

---

## Connection to Our Project

### What the paper does well that we should learn from

(1–5 numbered points.)

### What the paper does NOT do — and where ws2 fills the gap

(1–5 numbered points. Critical for positioning.)

### Specific design implications for ws2

(How does this paper affect our Phase 0.1 commitments or Phase 0.2
pre-registration? Be concrete.)

---

## Key Quotes

(Direct quotes worth preserving for the Methods or Related Work
section of the ws2 paper. Include page numbers where possible.)

---

## Study Questions

**Warm-up (Level 1):**
1. (Basic comprehension question.)
2. ...
3. ...

**Intermediate (Level 2):**
4. (Question requiring synthesis across sections.)
5. ...
6. ...

**Advanced (Level 3):**
7. (Question requiring methodological or theoretical judgment.)
8. ...
9. ...

---

## Challenge Corner

(Numbered challenges — C1, C2, ... — that the review session will
discuss and answer during reading. These are the "let's think about
this carefully" questions whose answers aren't obvious.)

**C1:** (Challenge question.)

**C2:** (Challenge question.)

...

---

## Synthesis Pointers (for `synthesis.md`)

(Numbered pointers that get harvested into the cross-paper synthesis
document. Typically: connections to other papers in the list,
methodological tensions, shared assumptions that bind multiple lines
of work.)

1. (Pointer.)

2. (Pointer.)

---

## Discussion Notes

(Filled in during the review session as we discuss the Challenge
Corner questions together. Blank until that session happens.)

### On CQ1 — (topic)

(Our discussion and answer.)

### On CQ2 — (topic)

...
```

## Three MUST elements — non-negotiable

Per user direction during Phase 0.1 scoping, every review file includes
at minimum:

1. **Three-level discourse** (smart high-schooler / junior-senior
   undergrad / early grad) — not optional; not combinable.
2. **Study questions** spanning basic / intermediate / advanced — three
   tiers, at least 2–3 questions per tier.
3. **Challenge questions** — numbered (C1, C2, ...) in the Challenge
   Corner; answers filled during review session, not pre-written.

The remaining sections (Background, Key Ideas, Connection to Our
Project, Key Quotes, Synthesis Pointers, Discussion Notes) follow
sibling-project tradition.

## Workflow

1. For each Tier 1 and Tier 2 paper, create `XX-<slug>.md` using the
   template. File numbering follows the list order above.
2. PDFs live locally (gitignored via `../.gitignore` pattern
   `literature-review/*.pdf`). Link to them via the PDF header field
   in each review file.
3. As reviews accumulate, populate `synthesis.md` with cross-paper
   threads: methodological tensions, shared assumptions, pathway
   coverage, reviewer-engagement notes.
4. Review sessions are held iteratively as papers are read; Discussion
   Notes in each file track the conversation.
5. Phase 0.1 closure gate: all Tier 1 and Tier 2 files complete with
   Discussion Notes filled; `synthesis.md` populated; no un-addressed
   contradictions with Phase 0.1 methodology commitments.
   **(Honest status, 2026-07-01 Phase 2.2 WS-G:** Tier 1 (01–07) was fully
   close-read and drove the Phase 0.1/0.2 methodology. Tier 2 (08–16) was
   **not** close-read — Phase 0.1 closed on Tier 1 + scoping, and the study
   proceeded. Tier 2 is now dispositioned rather than left dangling — see
   "Tier 2 disposition" below. The gate as literally worded was not met; the
   substantive intent (no un-addressed methodology contradiction) holds for
   Test I, with three genuinely-open items flagged for the write-up.)**

## Status tracking

Per-paper status in the tables above: `pending` / `reading` / `draft`
/ `under review` / `complete` / `superseded (empirical validation)` /
`deferred → Stage 3`. Update as work proceeds. The retrospective
(`docs/phases/phase-0.1-retro.md`) summarizes any papers whose close
reading triggered Phase 0.1 methodology revision.

## Tier 2 disposition (2026-07-01, Phase 2.2 WS-G — audit item 5)

Tier 2 (08–16) was never close-read; the lit-review/desiderata audit
surfaced it. Each paper is now dispositioned:

- **Superseded (closed) — 09 SPECTER, 10 SciRepEval, 11 SciNCL.** These are
  model-methodology background; the models themselves were **empirically
  validated** (Phase 0.1.E embedding smoke + Phase 1.1 A100 runs: norm bands,
  finiteness, cross-era era-match), which is stronger than reading the papers.
  Non-load-bearing → closed.
- **Deferred → Stage 3 — 08 Wu-Wang-Evans, 12 Hamilton (diachronic
  embeddings), 13 Uzzi.** 08's team-size interpretation is only load-bearing
  for the Stage-3 subfield / Test-II/IV analyses (Test I does not depend on
  it); 12 is conditional on Flavor-A drift mitigation; 13 is Stage-3 tertiary
  novelty. Read when Stage 3 is planned, so they're fresh.
- **OPEN — read before the Methods / write-up (still `pending`):**
  - **16 Culbert et al. (OpenAlex reference/abstract coverage) — highest
    priority.** Informs whether the ~50% abstract bottleneck + affiliation-
    coverage limits are OpenAlex-specific or universal — directly relevant to
    the Methods/Limitations and a possible WoS/Scopus robustness check.
  - **14 Kozlowski (intersectional inequalities)** — informs how intersectional
    demographic cells are reported under §9e weighting.
  - **15 Funk 2026 (disruption-literature inventory)** — reviewer-engagement /
    positioning for the Discussion.
  These three do NOT block Phase 2.2's Test I, but must be read before the
  paper draft (Stage 2 S8 / Stage 3).

## References

- Phase plan: `../docs/phases/phase-0.1-plan.md` (Check 6 section)
- Desiderata: `../docs/desiderata.md`
- Statistics primer: `../docs/primers/stats.pdf`
- Sibling format reference: `../../inverse-device-design/literature-review/01-ai-scientist-v2.md`
