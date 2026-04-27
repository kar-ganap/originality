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
| 05 | **Holst, Algaba, Tori, Wenmackers & Ginis 2024**, arXiv:2402.14583, "Dataset Artefacts are the Hidden Drivers of the Declining Disruptiveness in Science" | Dataset-artifact critique of Park-Leahey-Funk. Load-bearing for 13-F measurement-artifact null. | pending |
| 06 | **Hofstra, Kulkarni, Munoz-Najar Galvez, He, Jurafsky & McFarland 2020**, *PNAS* 117(17), "The Diversity-Innovation Paradox in Science" | Direct precedent for Test IV (team-diversity × novelty). Must engage their novelty-detection pipeline and minority-group operationalization. | complete |
| 07 | **Lockhart, King & Munsch 2023**, *Nature Human Behaviour* 7(7), "Name-based demographic inference and the unequal distribution of misrecognition" | Structural critique of name-based gender/race inference — directly load-bearing for our Genderize+NamSor pipeline. Grounds the "weight-by-confidence" choice in plan subsection 9. | pending |

### Tier 2 — Methodological underpinnings (read for method, not every claim)

| # | Paper | Role for ws2 | Status |
|---|---|---|---|
| 08 | **Wu, Wang & Evans 2019**, *Nature* 566, "Large teams develop and small teams disrupt science and technology" | Team-size confound control in Test II. Note Petersen 2025 JOI disputes the team-size interpretation. | pending |
| 09 | **Cohan, Feldman, Beltagy, Downey & Weld 2020**, *ACL*, SPECTER | Original SPECTER paper; background for SPECTER2. | pending |
| 10 | **Singh, D'Arcy, Cohan, Downey & Feldman 2023**, *EMNLP*, SciRepEval (arXiv:2211.13308) | SPECTER2 training, evaluation, documented limitations. | pending |
| 11 | **Ostendorff, Rethmeier, Augenstein, Gipp & Rehm 2022**, *EMNLP*, SciNCL (arXiv:2202.06671) | Our within-family embedding robustness partner. | pending |
| 12 | **Hamilton, Leskovec & Jurafsky 2016**, *ACL*, "Diachronic Word Embeddings Reveal Statistical Laws of Semantic Change" | Methodology template for Stage 3 Flavor A (conditional) drift mitigation. | pending |
| 13 | **Uzzi, Mukherjee, Stringer & Jones 2013**, *Science* 342, "Atypical Combinations and Scientific Impact" | Methodology for Test IV tertiary novelty metric (recombinant / reference-pair atypicality). Note: fourth author is Stringer, not Stone. | pending |
| 14 | **Kozlowski, Larivière, Sugimoto & Monroe-White 2022**, *PNAS* 119(2), "Intersectional inequalities in science" | Intersectional demographic-topic methodology at scale. Standard for demographic reporting in scientometrics. | pending |
| 15 | **Funk et al. 2026**, arXiv:2602.05140, "Is Innovation Becoming Less Disruptive? An Inventory of the Literature" | Canonical literature review of declining disruption. Reviewers will expect us to engage. | pending |
| 16 | **Culbert et al. 2024/2025**, *Scientometrics*, "Reference coverage analysis of OpenAlex compared to Web of Science and Scopus" | OpenAlex vs. WoS/Scopus. Required for our data-source positioning. | pending |

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

## Status tracking

Per-paper status in the tables above: `pending` / `reading` / `draft`
/ `under review` / `complete`. Update as work proceeds. The retrospective
(`docs/phases/phase-0.1-retro.md`) will summarize any papers whose close
reading triggered Phase 0.1 methodology revision.

## References

- Phase plan: `../docs/phases/phase-0.1-plan.md` (Check 6 section)
- Desiderata: `../docs/desiderata.md`
- Statistics primer: `../docs/primers/stats.pdf`
- Sibling format reference: `../../inverse-device-design/literature-review/01-ai-scientist-v2.md`
