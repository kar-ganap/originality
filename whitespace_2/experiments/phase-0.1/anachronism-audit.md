# Check 2d — Anachronism audit

**Run date:** 2026-04-27
**Snapshot recorded:** 2026-04-27T22:09:50+00:00
**Concepts tested:** 20
**Concepts not found in OpenAlex:** 6
**Anachronistically tagged (gap > 5 years before invention):** 14

## Per-concept results

| Concept query | Known year | Matched concept | Earliest paper year | Gap | Anachronistic? |
|---|---:|---|---:|---:|---:|
| Deep learning | 2006 | Deep learning | 1907 | 99 | **YES** |
| Transformer (machine learning model) | 2017 | *not found* | — | — | — |
| Attention mechanism | 2014 | *not found* | — | — | — |
| Generative adversarial network | 2014 | Generative adversarial network | 1978 | 36 | **YES** |
| BERT | 2018 | *not found* | — | — | — |
| Convolutional neural network | 1989 | Convolutional neural network | 1913 | 76 | **YES** |
| Reinforcement learning | 1989 | Reinforcement learning | 1941 | 48 | **YES** |
| Word embedding | 2013 | Word embedding | 1975 | 38 | **YES** |
| Recurrent neural network | 1986 | Recurrent neural network | 1901 | 85 | **YES** |
| CRISPR | 2012 | CRISPR | 1905 | 107 | **YES** |
| Cloud computing | 2006 | Cloud computing | 1901 | 105 | **YES** |
| Internet of things | 1999 | Internet of Things | 1922 | 77 | **YES** |
| Big data | 2005 | Big data | 1903 | 102 | **YES** |
| Bitcoin | 2009 | *not found* | — | — | — |
| Smartphone | 2007 | Smartphone application | 1977 | 30 | **YES** |
| Augmented reality | 1992 | Augmented reality | 1925 | 67 | **YES** |
| Internet | 1990 | The Internet | 1901 | 89 | **YES** |
| World Wide Web | 1991 | World Wide Web | 1901 | 90 | **YES** |
| MapReduce | 2004 | *not found* | — | — | — |
| Quantum supremacy | 2019 | *not found* | — | — | — |

## Interpretation

**Red flag** = gap > 5 years (earliest paper tagged pre-dates the concept's invention/popularization by more than 5 years).

**Headline:** 14/20 concepts show >5 year anachronistic tagging.

If many concepts are anachronistically tagged, the OpenAlex classifier is retroactively assigning modern labels to older papers — likely via shared keywords or text patterns that happen to match. This biases ws2's semantic-plurality measurement: pre-1990 papers may be mis-tagged as covering modern topics, inflating apparent semantic continuity across eras.

## CORRECTION (after user pushback on Check 2e)

The "earliest paper" search uses `concepts.id:X` + `sort=publication_year:asc`,
which returns the oldest paper where concept X appears in the concepts array
**regardless of score**. As shown in the related Check 2 correction (see
`check2-correction-score-thresholds.md`), OpenAlex's concepts array can
include concepts scored at 0.0 — i.e., concepts the classifier explicitly
rejected.

Spot-check of the earliest papers from this audit:

- "Deep learning" earliest=1907 ("Spa Treatment of Neurasthenia"): score=**0.527**
  — non-trivial. So the classifier really did assign deep-learning relevance to
  a 1907 medical paper.
- "CRISPR" earliest=1905 ("Stump in Appendicectomy"): score=**0.590** — also
  non-trivial.
- "Cloud computing" earliest=1901 ("The Purple Cloud"): score=**0.416** — also
  non-trivial.

So **the anachronism finding is real for these specific concepts** — these are
NOT zero-score noise; the classifier really does produce meaningful scores for
modern concepts on very old papers, likely via keyword matching (the words
"deep", "cloud" etc. trigger relevance even in unrelated contexts).

**However:** these are pre-1920 papers, well outside ws2's analytical window
(1970-2024). Within ws2's window, the question is open — needs a corrected
within-window anachronism check before drawing strong conclusions. The
multi-decade-anachronism framing below is correct for the very-old tail but
may not apply within ws2's actual scope.

## Detailed implications (some superseded — see correction above)

**The headline number is decisive: 14 of 20 modern concepts (70%) have anachronistic
tagging by margins of 30 to 107 years.** This is not "5 years off" — it's
multi-decade to multi-century anachronism.

A subtle confound: many of the "earliest paper" years cluster suspiciously around
1901-1907. This is plausibly a sentinel/default value that OpenAlex uses for papers
with unknown or malformed `publication_year` metadata, rather than a genuine 1901
publication on cloud computing. Either way, the implication for ws2 is the same:
**the OpenAlex `publication_year × concept_id` join is unreliable for identifying
when a topic was first studied**, because either (a) the classifier retroactively
assigns modern labels, or (b) the metadata is dirty enough that junk dates attach
to modern-tagged papers, or both.

### What this means for ws2

1. **OpenAlex concept tags cannot be used as reliable subfield labels for
   pre-1990 papers.** Any analysis that buckets papers by concept_id and treats
   the bucket as semantically coherent will mis-include irrelevant papers,
   especially pre-1990.

2. **Time-stratified concept analyses are particularly compromised.** If we
   measure "fraction of CS papers in subfield X over time," the time-axis
   measurement is contaminated by anachronistic tagging that systematically
   over-attributes modern topics to historical papers.

3. **ws2's semantic-plurality measure must avoid leaning on concept tags as
   subfield identifiers.** This pushes hard toward embedding-based subfield
   identification (already in desiderata §11 — "cluster fit on temporally
   stratified pooled subsample"). Check 2d **strengthens** that commitment from
   "preferred approach" to "necessary approach."

4. **Filtering by concept_id at the field level (CS C41008148, Physics
   C121332964) inherits some of this noise.** ws2's analytical population
   (papers tagged with the CS or Physics concept) likely includes some
   anachronistically-tagged papers, especially pre-1990. The field-restriction
   itself has uncertainty.

5. **A new Phase 0.2 commitment:** semantic-plurality measurements must use
   embedding-cluster-based subfield assignment (per desiderata §11), NOT
   OpenAlex concept tags as subfield labels. Concept tags can be retained as
   *features* (e.g., the level=0 field tag for population restriction) but
   not as the *granular subfield ontology*.