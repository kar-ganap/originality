# Check 1f follow-up — country-extraction operational sanity check

**Run date:** 2026-04-28
**Snapshot recorded:** 2026-04-28T00:36:22+00:00
**Diagnostic 1 (UNKNOWN recoverability):** 180 papers sampled from
`missingness-bias-raw.parquet` UNKNOWN subset, stratified by era (60/era).
**Diagnostic 2 (KNOWN consistency):** 30 papers sampled from
`missingness-bias-raw.parquet` KNOWN subset.

## Question

Does `openalex.extract_first_country` (which walks
`authorships[*].institutions[*].country_code`) miss country information
recoverable from `authorships[*].countries` (the authorship-level array)
or `authorships[*].raw_affiliation_strings` (free-text affiliations)?
The 55% UNKNOWN rate from Check 1f drives the §0 analytical-population
definition of P_demo (~45%); the user requested a sanity check on this
number after the Check 2 score-thresholding episode taught us that
misreading the API can cost a methodological commitment.

## Diagnostic 1 — UNKNOWN recoverability

| Era | n | inst.cc recovered | authorship.countries recovered | raw_affil non-empty | raw_affil rate |
|-----|---:|---:|---:|---:|---:|
| 1970-1989 | 60 | 0 | 0 | 5 | 8.3% |
| 1990-2009 | 60 | 0 | 0 | 4 | 6.7% |
| 2010-2024 | 60 | 0 | 0 | 8 | 13.3% |

**Pooled raw_affiliation recoverability: 17/180 = 9.4%**

`authorships[*].countries` recovery is essentially 0 in all eras —
it does not provide an alternative channel; the field appears to be
derived from institutions and is empty when institutions is empty.

`authorships[*].raw_affiliation_strings` recovery is ~7-13% by era,
~10% pooled. Recoverable papers contain country-derivable text (explicit
country names like "Canada", "USA"; or city/state/postcode like "Harrow,
Middlesex HA1 3UJ" which a UK-postcode lookup would resolve).

## Diagnostic 2 — KNOWN consistency

**Mismatches: 0 / 30.**

If 0/30: `extract_first_country` produces results consistent with
the parquet AND `authorships[*].countries` doesn't disagree with
`institutions[*].country_code` on any sampled paper. Function is
correctly labeling the papers it processes — no false positives on the
KNOWN side.

If >0/30: the function may be producing inconsistent results
under some conditions; investigate before trusting the parquet.

## Decision

**No catastrophic operational mistake.** Unlike the score-thresholding
episode (where filtering by `concepts.id:X` returned papers the
classifier explicitly rejected), the current `extract_first_country`
function produces correct results on the papers it identifies as KNOWN.
The 55% UNKNOWN rate is correct given the function's current implementation.

**Real-but-bounded gap.** ~10% of currently-UNKNOWN papers have parseable
`raw_affiliation_strings` that contain country-derivable text. The current
implementation misses these. Extending the function to fall back on
raw-affiliation parsing would shrink the UNKNOWN rate from ~55% to ~50%
(approximately a 5 pp shrinkage of the UNKNOWN bucket, equivalent to
P_demo growing from ~45% to ~50%).

**Stage-1 commitment** (added to plan §4 in N1+ revision):
extend `extract_first_country` to fall back on `raw_affiliation_strings`
parsing when `institutions[*].country_code` is empty. Two-pass
implementation:
1. **First pass (Stage 1):** explicit-country-name match on raw strings
   using an ISO-name lookup table. Estimated to recover ~half of the
   ~10% UNKNOWN papers with raw_affiliation_strings (those with an
   explicit country mention).
2. **Second pass (Stage 1 stretch / Stage 3 robustness):** city/state/
   postcode → country gazetteer lookup (e.g., GeoNames). Recovers the
   remaining half. Heavier engineering; defer unless first-pass falls
   short of expectations.

**Plan revisions absorbed:**
- §0 P_demo numerical bound updated from "~45%" to "~50%" with current
  implementation noted as upper bound on UNKNOWN.
- §4 Stage-1 commitment added.
- §9e country axis bound updated; scope-narrowing remains structurally
  necessary (the residual ~50% is genuinely missing affiliation data,
  not a parsing miss).

## Severity comparison vs. earlier operational miss

| | Score-thresholding miss (2026-04-27) | Country-extraction miss (now) |
|---|---|---|
| Function correctness | Wrong (returned papers classifier explicitly rejected) | Correct (0/30 false positives on KNOWN sample) |
| Magnitude correction | "95% off-target" → "0-2% off-target" — 90 pp swing | "55% UNKNOWN" → "~50% UNKNOWN" — 5 pp shrinkage |
| Plan-level impact | Forced retraction of strengthened §11 commitment | Loosens §0 P_demo; no methodology overturn |

Methodology is robust; this is a documentation + Stage-1 implementation
update, not a course correction.
