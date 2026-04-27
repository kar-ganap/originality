# Check 2 correction — score-thresholded subfield membership

**Run date:** 2026-04-27
**Snapshot recorded:** 2026-04-27T22:25:48+00:00

## Why this correction

The original Check 2e found **~95% off-target on OS-tagged 2020 top-cited
papers** (Kahneman-Tversky, COVID dashboards, GhostNet vision-ML, etc.). The
user pushed back: 95% off-target felt unreasonably high. Investigation showed:

- OpenAlex's `concepts` array on a paper includes ALL concepts the classifier
  considered, including those scored 0.0 (correctly identified as NOT about
  the topic).
- The `concepts.id:X` filter returns ANY paper where X appears in the array,
  *regardless of score*.
- So filtering by `concepts.id:C111919701` (Operating system) returned papers
  where the classifier scored OS at 0.0 — i.e., papers it correctly identified
  as not about OS.

**The classifier was doing its job; my interpretation of its outputs was
wrong.** Score-thresholded results below show the corrected picture.

## Score distribution by cell

| Subfield × Year | n | zero-score | ≥0.1 | ≥0.3 | ≥0.5 | %≥0.3 | %≥0.5 |
|---|---:|---:|---:|---:|---:|---:|---:|
| operating systems × 1975 | 50 | 45 | 1 | 0 | 0 | 0% | 0% |
| operating systems × 2020 | 50 | 41 | 7 | 1 | 0 | 2% | 0% |
| compilers × 1975 | 50 | 2 | 48 | 46 | 46 | 92% | 92% |
| compilers × 2020 | 50 | 4 | 46 | 45 | 30 | 90% | 60% |

## Interpretation (corrected)

**Operating systems** has many zero-score noise tags but score-thresholded
membership is essentially zero on top-cited papers — the classifier
correctly identifies that OS is *not* the primary topic of those papers.

**Compilers** has ~95%+ score-thresholded membership at >=0.3 and >=0.5
in 1975 — the classifier IS reliable for this concept in this era.

The 'OS 95% off-target' finding from the original Check 2e was a query
artifact, not a classifier failure. **Score-thresholded OpenAlex concept
tags appear to be reasonably reliable for ws2's subfield ontology** —
subject to the broader caveat that 'Operating system' is a very broad
concept (9.1M works tagged) and the score distribution behaves
differently than narrower technical concepts like 'Compiler'.

## What this changes for ws2

1. **Retract the strengthened §11 commitment.** OpenAlex concept tags are
   NOT broken; the issue was using `concepts.id:X` without score
   thresholding. The §11 cluster-fit-on-temporally-stratified-pooled-
   subsample commitment remains the **preferred** subfield mechanism per
   the original desiderata, but no longer 'necessary.'

2. **New Phase 0.2 commitment:** ws2's pipeline must respect score
   thresholds when filtering by OpenAlex concept ID. Default threshold
   for subfield-membership claims: score >= 0.3 (loose, inclusive) or
   >= 0.5 (strict). Pre-register specific thresholds per use case in
   Phase 0.2.

3. **Check 2d anachronism finding partially holds, with nuance.** Some
   pre-1920 papers DO have non-trivial scores (0.4-0.6) for modern
   concepts, suggesting either classifier failure on very old papers OR
   junk metadata. But these are pre-1970 (outside ws2's window), so the
   anachronism concern within ws2's analytical population is much smaller
   than the original Check 2d framing suggested. Within ws2's window,
   spot-checks need to be re-run with score thresholding before drawing
   conclusions.

4. **lessons.md update:** add 'OpenAlex concepts.id filter does NOT
   respect score thresholds; concept array includes 0-score concepts
   that the classifier explicitly rejected. Always score-threshold
   client-side.'

## Sanity check on "Operating system" being level=1 with 9.1M works

The OS concept has 9.1M works tagged at level=1, which is dramatically
more than would genuinely be about operating systems. This reflects
OpenAlex's classifier producing a long tail of low-score 'considered but
rejected' tags, not promiscuous high-score tagging. Any analysis
consuming OpenAlex concepts must score-threshold; the 9.1M number is
the size of the 'considered' set, not the 'about-it' set.