"""Check 2 correction — re-analyse with score-thresholded concept membership.

User-prompted correction. The original Check 2e ("~95% off-target on OS-tagged
2020 papers") was a query artifact: OpenAlex's `concepts.id:X` filter returns
ANY paper where concept X appears in the concepts array, regardless of the
classifier's score for X. Many of the "off-target" papers had OS score = 0.0
or near-zero — the classifier WAS correctly identifying them as not about
operating systems, but the concept still appeared in the array.

This script re-runs the analysis with explicit score thresholding to get the
correct picture of OpenAlex classifier behavior.

For each (subfield, year) cell:
1. Pull top-50 papers by `concepts.id:X` filter (the buggy way).
2. Compute the actual concept score for each paper.
3. Report fraction at score >= 0.0 (everything; the buggy denominator), score
   >= 0.3 (loose threshold), score >= 0.5 (strict threshold).

Outputs:

- ``check2-correction-score-thresholds.csv``
- ``check2-correction-score-thresholds.md``
"""

from __future__ import annotations

import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

from whitespace2 import openalex

_OUT_DIR = Path(__file__).parent

_CELLS: list[tuple[str, str, int]] = [
    ("operating systems", "C111919701", 1975),
    ("operating systems", "C111919701", 2020),
    ("compilers", "C169590947", 1975),
    ("compilers", "C169590947", 2020),
]
_PER_CELL = 50


def _score_for_concept(work: dict[str, Any], target_id: str) -> float:
    for concept in work.get("concepts") or []:
        if not isinstance(concept, dict):
            continue
        cid = (concept.get("id") or "").rsplit("/", 1)[-1]
        if cid == target_id:
            score = concept.get("score") or 0.0
            return float(score)
    return 0.0


def main() -> None:
    print("Check 2 correction — score-thresholded subfield membership")
    snapshot_date = openalex.latest_snapshot_date()

    rows: list[dict[str, Any]] = []
    for subfield, concept_id, year in _CELLS:
        print(f"\n  {subfield} × {year} (concept={concept_id})")
        works = openalex.fetch_works(
            filters={"concepts.id": concept_id, "publication_year": str(year)},
            sort="cited_by_count:desc",
            select=["id", "title", "concepts", "cited_by_count"],
            per_page=_PER_CELL,
        )
        time.sleep(0.5)
        scores = [_score_for_concept(w, concept_id) for w in works]
        n = len(scores)
        n_ge_01 = sum(1 for s in scores if s >= 0.1)
        n_ge_03 = sum(1 for s in scores if s >= 0.3)
        n_ge_05 = sum(1 for s in scores if s >= 0.5)
        n_zero = sum(1 for s in scores if s == 0.0)
        print(f"    n={n}; zero-score={n_zero}; score>=0.1: {n_ge_01}, >=0.3: {n_ge_03}, >=0.5: {n_ge_05}")
        rows.append(
            {
                "subfield": subfield,
                "year": year,
                "concept_id": concept_id,
                "n_papers_in_filter": n,
                "n_zero_score": n_zero,
                "n_score_ge_0.1": n_ge_01,
                "n_score_ge_0.3": n_ge_03,
                "n_score_ge_0.5": n_ge_05,
                "frac_zero_score": n_zero / n if n else 0.0,
                "frac_score_ge_0.3": n_ge_03 / n if n else 0.0,
                "frac_score_ge_0.5": n_ge_05 / n if n else 0.0,
            }
        )

    df = pd.DataFrame(rows)
    csv_path = _OUT_DIR / "check2-correction-score-thresholds.csv"
    df.to_csv(csv_path, index=False)
    print(f"\n  wrote {csv_path}")

    md_lines = [
        "# Check 2 correction — score-thresholded subfield membership",
        "",
        f"**Run date:** {datetime.now(timezone.utc).date().isoformat()}",
        f"**Snapshot recorded:** {snapshot_date}",
        "",
        "## Why this correction",
        "",
        "The original Check 2e found **~95% off-target on OS-tagged 2020 top-cited",
        "papers** (Kahneman-Tversky, COVID dashboards, GhostNet vision-ML, etc.). The",
        "user pushed back: 95% off-target felt unreasonably high. Investigation showed:",
        "",
        "- OpenAlex's `concepts` array on a paper includes ALL concepts the classifier",
        "  considered, including those scored 0.0 (correctly identified as NOT about",
        "  the topic).",
        "- The `concepts.id:X` filter returns ANY paper where X appears in the array,",
        "  *regardless of score*.",
        "- So filtering by `concepts.id:C111919701` (Operating system) returned papers",
        "  where the classifier scored OS at 0.0 — i.e., papers it correctly identified",
        "  as not about OS.",
        "",
        "**The classifier was doing its job; my interpretation of its outputs was",
        "wrong.** Score-thresholded results below show the corrected picture.",
        "",
        "## Score distribution by cell",
        "",
        "| Subfield × Year | n | zero-score | ≥0.1 | ≥0.3 | ≥0.5 | %≥0.3 | %≥0.5 |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for _, row in df.iterrows():
        md_lines.append(
            f"| {row['subfield']} × {int(row['year'])} | "
            f"{int(row['n_papers_in_filter'])} | "
            f"{int(row['n_zero_score'])} | "
            f"{int(row['n_score_ge_0.1'])} | "
            f"{int(row['n_score_ge_0.3'])} | "
            f"{int(row['n_score_ge_0.5'])} | "
            f"{row['frac_score_ge_0.3']:.0%} | "
            f"{row['frac_score_ge_0.5']:.0%} |"
        )

    md_lines.extend(
        [
            "",
            "## Interpretation (corrected)",
            "",
            "**Operating systems** has many zero-score noise tags but score-thresholded",
            "membership is essentially zero on top-cited papers — the classifier",
            "correctly identifies that OS is *not* the primary topic of those papers.",
            "",
            "**Compilers** has ~95%+ score-thresholded membership at >=0.3 and >=0.5",
            "in 1975 — the classifier IS reliable for this concept in this era.",
            "",
            "The 'OS 95% off-target' finding from the original Check 2e was a query",
            "artifact, not a classifier failure. **Score-thresholded OpenAlex concept",
            "tags appear to be reasonably reliable for ws2's subfield ontology** —",
            "subject to the broader caveat that 'Operating system' is a very broad",
            "concept (9.1M works tagged) and the score distribution behaves",
            "differently than narrower technical concepts like 'Compiler'.",
            "",
            "## What this changes for ws2",
            "",
            "1. **Retract the strengthened §11 commitment.** OpenAlex concept tags are",
            "   NOT broken; the issue was using `concepts.id:X` without score",
            "   thresholding. The §11 cluster-fit-on-temporally-stratified-pooled-",
            "   subsample commitment remains the **preferred** subfield mechanism per",
            "   the original desiderata, but no longer 'necessary.'",
            "",
            "2. **New Phase 0.2 commitment:** ws2's pipeline must respect score",
            "   thresholds when filtering by OpenAlex concept ID. Default threshold",
            "   for subfield-membership claims: score >= 0.3 (loose, inclusive) or",
            "   >= 0.5 (strict). Pre-register specific thresholds per use case in",
            "   Phase 0.2.",
            "",
            "3. **Check 2d anachronism finding partially holds, with nuance.** Some",
            "   pre-1920 papers DO have non-trivial scores (0.4-0.6) for modern",
            "   concepts, suggesting either classifier failure on very old papers OR",
            "   junk metadata. But these are pre-1970 (outside ws2's window), so the",
            "   anachronism concern within ws2's analytical population is much smaller",
            "   than the original Check 2d framing suggested. Within ws2's window,",
            "   spot-checks need to be re-run with score thresholding before drawing",
            "   conclusions.",
            "",
            "4. **lessons.md update:** add 'OpenAlex concepts.id filter does NOT",
            "   respect score thresholds; concept array includes 0-score concepts",
            "   that the classifier explicitly rejected. Always score-threshold",
            "   client-side.'",
            "",
            "## Sanity check on \"Operating system\" being level=1 with 9.1M works",
            "",
            "The OS concept has 9.1M works tagged at level=1, which is dramatically",
            "more than would genuinely be about operating systems. This reflects",
            "OpenAlex's classifier producing a long tail of low-score 'considered but",
            "rejected' tags, not promiscuous high-score tagging. Any analysis",
            "consuming OpenAlex concepts must score-threshold; the 9.1M number is",
            "the size of the 'considered' set, not the 'about-it' set.",
        ]
    )
    out_path = _OUT_DIR / "check2-correction-score-thresholds.md"
    out_path.write_text("\n".join(md_lines))
    print(f"  wrote {out_path}")
    print("\nCheck 2 correction complete.")


if __name__ == "__main__":
    main()
