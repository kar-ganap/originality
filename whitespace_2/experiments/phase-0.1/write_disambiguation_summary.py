"""Check 4 — Pass C: aggregate manual classifications into the summary .md.

Reads:
- `disambiguation-check-raw.csv` (200-author sample with flag column)
- `disambiguation-check-candidates.csv` (≤50 manually-classified candidates;
  `verdict` column filled with one of: error, plausible, uncertain)
- `disambiguation-check-metadata.json` (run metadata from Pass A)

Writes:
- `disambiguation-check.md` with H1/H2/H3 outcomes and a decision section.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

_OUT_DIR = Path(__file__).parent
_FLAG_THRESHOLD_YEARS = 60


def main() -> None:
    raw = pd.read_csv(_OUT_DIR / "disambiguation-check-raw.csv")
    candidates = pd.read_csv(_OUT_DIR / "disambiguation-check-candidates.csv")
    metadata = json.loads(
        (_OUT_DIR / "disambiguation-check-metadata.json").read_text()
    )

    n_sampled = metadata["n_fetched"]
    n_flagged_total = metadata["n_flagged_total"]
    flag_rate = metadata["flag_rate"]
    n_reviewed = len(candidates)

    # H1: flag rate in [5%, 15%]?
    h1_pass = 0.05 <= flag_rate <= 0.15
    h1_status = "PASS" if h1_pass else "FAIL"

    # H2: of reviewed flagged, ≥50% are 'error'?
    verdicts = candidates["verdict"].astype(str).str.strip().str.lower()
    n_error = int((verdicts == "error").sum())
    n_plausible = int((verdicts == "plausible").sum())
    n_uncertain = int((verdicts == "uncertain").sum())
    n_blank = int(verdicts.isin(["", "nan"]).sum())
    n_classified = n_error + n_plausible + n_uncertain
    error_rate_in_flagged = (
        n_error / n_classified if n_classified > 0 else 0.0
    )
    h2_pass = error_rate_in_flagged >= 0.50
    h2_status = "PASS" if h2_pass else "FAIL"

    # H3: implied disambiguation-error upper bound consistent with [3%, 10%]?
    implied_error_rate = flag_rate * error_rate_in_flagged
    h3_pass = 0.03 <= implied_error_rate <= 0.10
    h3_status = "PASS" if h3_pass else (
        "BELOW" if implied_error_rate < 0.03 else "ABOVE"
    )

    # Career length distribution
    cl = raw["career_length"].dropna()
    body = f"""# Check 4 — OpenAlex disambiguation spot-check

**Run date:** {datetime.now(timezone.utc).date().isoformat()}
**Snapshot recorded:** {metadata['snapshot']}
**Sample design:** {n_sampled} authors, frequency-weighted by appearances in
`missingness-bias-raw.parquet`'s authorships across 22K papers (1000-paper
sub-sample harvested for author frequencies, then 200 unique authors
sampled from the resulting frequency distribution).
**Flag threshold:** career_length > {_FLAG_THRESHOLD_YEARS} years
(latest_pub_year − first_pub_year per OpenAlex `/authors/A{{id}}` record's
`counts_by_year`).
**Manual-inspection budget:** 50 (random subsample if more flagged).

## Career-length distribution

- Mean: {cl.mean():.1f}y
- Median: {cl.median():.1f}y
- Max: {int(cl.max())}y
- Authors flagged (career > {_FLAG_THRESHOLD_YEARS}y): {n_flagged_total} of
  {n_sampled} ({flag_rate:.1%})
- Authors manually reviewed: {n_reviewed} of {n_flagged_total}

## Manual-classification breakdown (Pass B)

Of the {n_reviewed} flagged authors reviewed:

| Verdict | Count | Share |
|---------|------:|------:|
| error (multiple distinct people merged) | {n_error} | {n_error / max(1, n_classified):.1%} |
| plausible (genuine long career) | {n_plausible} | {n_plausible / max(1, n_classified):.1%} |
| uncertain | {n_uncertain} | {n_uncertain / max(1, n_classified):.1%} |
| (unclassified) | {n_blank} | — |

## Hypothesis outcomes

- **H1 (flag rate in [5%, 15%]):** {h1_status} — {flag_rate:.1%}.
- **H2 (≥50% of flagged are genuine errors):** {h2_status} — {error_rate_in_flagged:.1%}.
- **H3 (implied disambiguation error upper bound in [3%, 10%]):** {h3_status} —
  flag_rate × error_in_flagged = {flag_rate:.1%} × {error_rate_in_flagged:.1%} =
  **{implied_error_rate:.1%}**.

## Comparison to plan §10

Plan §10 commits to OpenAlex's published 90-95% author-disambiguation accuracy
as the working assumption (i.e., 5-10% error rate). Check 4's implied error rate
({implied_error_rate:.1%}) {"falls within" if 0.05 <= implied_error_rate <= 0.10 else "diverges from"}
this band.

## Decision

{
  "Plan §10's working assumption (5-10% error rate) is consistent with the "
  "ws2-corpus-specific spot-check; no revision required."
  if 0.03 <= implied_error_rate <= 0.10
  else (
    "Check 4's implied error rate is below plan §10's working band — "
    "OpenAlex disambiguation may be more accurate on ws2's corpus than its "
    "published headline. Plan §10 stands as a conservative upper bound; "
    "no analytical change required."
    if implied_error_rate < 0.03 else
    "Check 4's implied error rate is ABOVE plan §10's working band. "
    "Disambiguation error may bias career-stage and training-institution "
    "metrics more than originally assumed. Flag for plan §10 revision."
  )
}

## Detailed CSVs

- `disambiguation-check-raw.csv` — {n_sampled} sampled authors with career-
  length data and flag column.
- `disambiguation-check-candidates.csv` — manually-classified flagged
  candidates ({n_reviewed} rows).
"""
    out_path = _OUT_DIR / "disambiguation-check.md"
    out_path.write_text(body)
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
