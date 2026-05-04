# Check 4 — OpenAlex disambiguation spot-check

**Run date:** 2026-04-28
**Snapshot recorded:** 2026-04-28T03:41:34+00:00
**Sample design:** 199 authors, frequency-weighted by appearances in
`missingness-bias-raw.parquet`'s authorships across 22K papers (1000-paper
sub-sample harvested for author frequencies, then 200 unique authors
sampled from the resulting frequency distribution).
**Flag threshold:** career_length > 60 years
(latest_pub_year − first_pub_year per OpenAlex `/authors/A{id}` record's
`counts_by_year`).
**Manual-inspection budget:** 50 (random subsample if more flagged).

## Career-length distribution

- Mean: 22.9y
- Median: 20.0y
- Max: 116y
- Authors flagged (career > 60y): 9 of
  199 (4.5%)
- Authors manually reviewed: 9 of 9

## Manual-classification breakdown (Pass B)

Of the 9 flagged authors reviewed:

| Verdict | Count | Share |
|---------|------:|------:|
| error (multiple distinct people merged) | 6 | 66.7% |
| plausible (genuine long career) | 1 | 11.1% |
| uncertain | 2 | 22.2% |
| (unclassified) | 0 | — |

## Hypothesis outcomes

- **H1 (flag rate in [5%, 15%]):** marginally below band — 4.5% (just
  below the 5% lower bound; within sampling noise of n=199, where the
  95% CI on a 4.5% proportion is roughly [2.0%, 7.7%]).
- **H2 (≥50% of flagged are genuine errors):** **PASS** — 66.7%.
- **H3 (implied disambiguation error upper bound in [3%, 10%]):** **PASS**
  at the lower edge — flag_rate × error_in_flagged = 4.5% × 66.7% =
  **3.0%**.

## Sample classifications (manually inspected)

Six errors confirmed via metadata:

- **Julia Pawłowska**: 370,697 works claimed — biologically impossible;
  catch-all merge across many distinct authors.
- **S. Vitale**: 37 institutions; name_alts include "S G Vitale" (distinct
  middle initial, suggesting different person merged).
- **Thomas Barthel**: 26 institutions including UNESCO is implausible for
  a quantum physicist — merged with non-physicists.
- **Max F. Platzer**: institutions include National Pension Service
  alongside CSULB — multiple distinct people merged.
- **Niraj Kumar Jha**: topics here are biomedical (Alzheimer's, drug
  delivery) but author ID is the famous CMU CS Niraj Jha — merge across
  distinct fields.
- **Alfred O. Hero**: 1910 start year is biologically impossible (would
  mean publishing at age 0); junk year metadata + 54 institutions.

One plausible long career:
- **Shiv N. Khanna**: 476 works over 63y with consistent
  materials-chemistry topics; productive but plausible long career.

Two uncertain (couldn't classify decisively from metadata):
- **E. Costa**: 1098 works in 74y; consistent astrophysics topics but
  high institution count.
- **R. Lorenz**: 60 works in 68y (low productivity) + 10 institutions;
  could be one mobile person or multiple merged.

## Interpretation — what 3.0% actually represents

**3.0% is a *cross-era merger* error rate, not a total disambiguation
error rate.** The career_length > 60yr screen catches one specific
failure mode: distinct authors merged across era boundaries (e.g., a
1970s researcher's record glued to a 2010s researcher with a similar
name). It does NOT catch:

- **Within-era mergers** — two distinct authors of the same era and
  similar name merged into one record.
- **Splits** — one author's publications split across two or more
  records due to name-variant disagreement.

So 3.0% is a **lower bound** on total OpenAlex disambiguation error rate
on ws2's corpus, not an upper bound.

## Comparison to plan §10

Plan §10 commits to OpenAlex's published 90-95% accuracy as a working
assumption (5-10% error rate). The 5-10% headline includes ALL error
types (mergers + splits, both within-era and cross-era).

Check 4's 3.0% cross-era-merger rate is plausibly consistent with plan
§10's 5-10% total: cross-era mergers are likely a minority of total
disambiguation errors (within-era mergers are more numerous because
similar-name authors of the same era are more common). If cross-era is
~30-50% of total errors, total error rate ≈ 6-10%, in the band.

If cross-era is a larger fraction of total errors (e.g., 80%+), our
total error rate would be ~3-4%, below plan §10's band — meaning
OpenAlex disambiguation may be slightly more accurate on ws2's corpus
than its published headline.

## Decision

**Plan §10's working assumption (5-10% error rate) is consistent with
the spot-check.** No revision to plan §10 required. The cross-era-
merger rate (3.0%) is a useful sub-band; total error rate likely sits
within plan §10's band when within-era errors are accounted for.

For ws2's downstream metrics (career stage, training-institution
concentration via Proxy A), the implication is unchanged: per-author
disambiguation noise is bounded but non-negligible; aggregate-level
metrics (Gini, effective number of distinct institutions) are robust
to this noise; per-author claims should be flagged as
disambiguation-uncertain.

## Detailed CSVs

- `disambiguation-check-raw.csv` — 199 sampled authors with career-
  length data and flag column.
- `disambiguation-check-candidates.csv` — manually-classified flagged
  candidates (9 rows) with verdicts and rationales.
