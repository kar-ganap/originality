# Check 2e — Hand-audit setup

**Run date:** 2026-04-27
**Snapshot recorded:** 2026-04-27T22:11:29+00:00
**Subfields:** ['operating systems', 'compilers']
**Years audited:** [1975, 2020]
**Per cell:** 50 top-cited papers
**Total papers fetched:** 200

## How to review

Open `hand-audit-papers.csv`. For each row, judge whether the paper *genuinely* belongs to the subfield (operating systems / compilers) based on title + abstract preview. Mark a column `audit_correct` (yes/no/uncertain) for each row.

Then count the false-positive rate per (subfield, year) cell:
- 1975 cells: how many of 50 papers are clearly off-target?
- 2020 cells: same question.

If the false-positive rate differs substantially across eras (e.g., 1975 has 30% off-target but 2020 has 5%), the classifier is drifting in reliability across eras — this biases ws2's semantic-
plurality measurement.

## CORRECTION (after user pushback)

**Important caveat — added retroactively.** The "off-target" interpretation below
is largely a query artifact, not a classifier failure. OpenAlex's `concepts`
array on each paper includes ALL concepts the classifier considered, including
those scored 0.0 (correctly identified as NOT about the topic). The
`concepts.id:X` filter returns ANY paper where X appears in the array
*regardless of score*.

So filtering "Operating system" papers via `concepts.id:C111919701` returned
papers where the classifier scored OS at exactly 0.0. The classifier WAS doing
its job correctly; my interpretation of its outputs was wrong.

Corrected score-thresholded counts (from `check2-correction-score-thresholds.md`):

- OS × 1975 top-50: 45/50 zero-score; **0/50 score≥0.3**.
- OS × 2020 top-50: 41/50 zero-score; **1/50 score≥0.3**.
- Compilers × 1975 top-50: 2/50 zero-score; **46/50 score≥0.3** (and ≥0.5).
- Compilers × 2020 top-50: 4/50 zero-score; **45/50 score≥0.3**; 30/50 ≥0.5.

The classifier is **reliable when score-thresholded**. The "OS 95% off-target"
framing below should be read as "OS-tagged-at-any-score 95% off-target" —
which only matters if a downstream pipeline uses the unscore-thresholded
`concepts.id:X` filter. ws2's pipeline must respect score thresholds.

The original directional read below is preserved for historical record.

## Interpretation (directional, from spot-check of top-10 rows of each cell — superseded by correction above)

Full hand-audit of all 200 rows still pending. Directional read on top-10:

### Operating systems × 1975

Of the 10 top-cited "Operating system"-tagged 1975 papers, ~1 (Saltzer-Schroeder
"Protection of information in computer systems") is genuinely about operating
systems. The other 9 are off-target: Kahneman-Tversky on heuristics; Salton on
information retrieval; Tinto on higher-education dropout; Mayhew on Congress;
protein synthesis; political science; spatial cognition; bacteriology; etc.
**~90% off-target.**

### Compilers × 1975

~4-5 of 10 are genuine compiler-related (Concurrent Pascal, programming-large-
vs-small, register allocation, semantic evaluators). Others include INGRES
(database), TeX (typesetting), Old English humanities, hydrology.
**~50% off-target.**

### Operating systems × 2020

Almost none are about operating systems: bioinformatics tools, vision ML, COVID
dashboards, structural biology software, climate data, animal-research
guidelines. **~95% off-target.**

### Headline

**The OpenAlex concept tagger is promiscuous in both eras.** Tags attach to
top-cited papers where the subject is at most peripheral. This is consistent
with 2c (era-stable confidence scores) — the classifier's behavior is similar
across eras, but the *correctness* of the tags is poor regardless.

What 2e adds beyond 2d is qualitative confirmation that concept tags **even on
highly-cited modern papers** are unreliable as subfield labels.

### What this means for ws2 (compounds 2d)

- **2d** showed multi-decade anachronistic tagging on the time axis.
- **2e** shows promiscuous tagging on the cross-section, in both eras.

Together: OpenAlex concept tags are not reliable as subfield labels at any
era. ws2's semantic-plurality measure must use embedding-cluster-based
subfields (desiderata §11). The level-0 field-restriction tag (CS C41008148,
Physics C121332964) is the only concept-tag use that survives — and even
there, ws2's analytical population includes some incorrectly-tagged papers,
adding to the selection-bias-correction burden from Check 1f.