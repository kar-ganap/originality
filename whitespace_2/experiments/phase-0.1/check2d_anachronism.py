"""Check 2d — Anachronism audit.

For each of ~20 modern concepts (with known invention/popularization years),
search OpenAlex for the matching concept ID, find the earliest paper tagged
with it, and compare to the known year. Red flag: earliest tagged paper
pre-dates the concept's invention by >5 years (suggests the OpenAlex
classifier retroactively assigns modern labels to older papers via shared
keyword/text).

Outputs:

- ``anachronism-audit.csv`` — concept | known_year | earliest_paper_year | gap | flag
- ``anachronism-audit.md`` — summary + interpretation
"""

from __future__ import annotations

import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

from whitespace2 import openalex

_OUT_DIR = Path(__file__).parent

# Concept name → known invention/popularization year (where ambiguous, the year
# the concept name as such became established usage). Pre-dating by >5 years
# is the red flag.
_ANACHRONISTIC_CONCEPTS: list[tuple[str, int]] = [
    ("Deep learning", 2006),
    ("Transformer (machine learning model)", 2017),
    ("Attention mechanism", 2014),
    ("Generative adversarial network", 2014),
    ("BERT", 2018),
    ("Convolutional neural network", 1989),
    ("Reinforcement learning", 1989),
    ("Word embedding", 2013),
    ("Recurrent neural network", 1986),
    ("CRISPR", 2012),
    ("Cloud computing", 2006),
    ("Internet of things", 1999),
    ("Big data", 2005),
    ("Bitcoin", 2009),
    ("Smartphone", 2007),
    ("Augmented reality", 1992),
    ("Internet", 1990),
    ("World Wide Web", 1991),
    ("MapReduce", 2004),
    ("Quantum supremacy", 2019),
]


def _find_concept(query: str) -> dict[str, Any] | None:
    """Use OpenAlex search to find best concept match for a query."""
    results = openalex.search_concepts(query, per_page=5)
    if not results:
        return None
    # Prefer exact (case-insensitive) display_name match; fall back to first.
    query_lower = query.lower()
    for result in results:
        if isinstance(result, dict) and (result.get("display_name") or "").lower() == query_lower:
            return result
    return results[0] if isinstance(results[0], dict) else None


def _earliest_paper_for_concept(concept_id: str) -> dict[str, Any] | None:
    """Fetch the single earliest paper tagged with this concept."""
    works = openalex.fetch_works(
        filters={"concepts.id": concept_id, "publication_year": ">1900"},
        sort="publication_year:asc",
        per_page=1,
    )
    return works[0] if works else None


def main() -> None:
    print("Check 2d — Anachronism audit")
    snapshot_date = openalex.latest_snapshot_date()

    rows: list[dict[str, Any]] = []
    for query, known_year in _ANACHRONISTIC_CONCEPTS:
        print(f"  {query} ...", end=" ", flush=True)
        concept = _find_concept(query)
        if not concept:
            print("(no concept found)")
            rows.append(
                {
                    "query": query,
                    "known_year": known_year,
                    "matched_concept": None,
                    "matched_concept_id": None,
                    "earliest_paper_year": None,
                    "earliest_paper_id": None,
                    "earliest_paper_title": None,
                    "gap_years": None,
                    "flag_anachronism": None,
                }
            )
            continue
        time.sleep(0.5)
        try:
            earliest = _earliest_paper_for_concept(concept["id"].rsplit("/", 1)[-1])
        except RuntimeError as err:
            print(f"(fetch failed: {err})")
            rows.append(
                {
                    "query": query,
                    "known_year": known_year,
                    "matched_concept": concept.get("display_name"),
                    "matched_concept_id": concept.get("id"),
                    "earliest_paper_year": None,
                    "earliest_paper_id": None,
                    "earliest_paper_title": None,
                    "gap_years": None,
                    "flag_anachronism": None,
                }
            )
            continue
        time.sleep(0.5)
        if earliest is None:
            earliest_year: int | None = None
            earliest_id = None
            earliest_title = None
        else:
            earliest_year = earliest.get("publication_year")
            earliest_id = earliest.get("id")
            earliest_title = earliest.get("title")
        gap = (known_year - earliest_year) if earliest_year is not None else None
        flag = (gap is not None and gap > 5)
        print(
            f"matched={concept.get('display_name')!r} earliest={earliest_year} "
            f"gap={gap} flag={flag}"
        )
        rows.append(
            {
                "query": query,
                "known_year": known_year,
                "matched_concept": concept.get("display_name"),
                "matched_concept_id": concept.get("id"),
                "earliest_paper_year": earliest_year,
                "earliest_paper_id": earliest_id,
                "earliest_paper_title": earliest_title,
                "gap_years": gap,
                "flag_anachronism": flag,
            }
        )

    df = pd.DataFrame(rows)
    csv_path = _OUT_DIR / "anachronism-audit.csv"
    df.to_csv(csv_path, index=False)
    print(f"\n  wrote {csv_path}")

    n_total = len(df)
    n_flagged = int(df["flag_anachronism"].fillna(False).sum())
    n_no_match = int(df["matched_concept_id"].isna().sum())

    md_lines = [
        "# Check 2d — Anachronism audit",
        "",
        f"**Run date:** {datetime.now(timezone.utc).date().isoformat()}",
        f"**Snapshot recorded:** {snapshot_date}",
        f"**Concepts tested:** {n_total}",
        f"**Concepts not found in OpenAlex:** {n_no_match}",
        f"**Anachronistically tagged (gap > 5 years before invention):** {n_flagged}",
        "",
        "## Per-concept results",
        "",
        "| Concept query | Known year | Matched concept | Earliest paper year | Gap | Anachronistic? |",
        "|---|---:|---|---:|---:|---:|",
    ]
    for _, row in df.iterrows():
        gap_str = f"{int(row['gap_years'])}" if pd.notna(row["gap_years"]) else "—"
        flag_str = (
            "**YES**" if row["flag_anachronism"] is True
            else ("no" if row["flag_anachronism"] is False else "—")
        )
        ey = row["earliest_paper_year"]
        ey_str = f"{int(ey)}" if pd.notna(ey) else "—"
        md_lines.append(
            f"| {row['query']} | {row['known_year']} | "
            f"{row['matched_concept'] or '*not found*'} | {ey_str} | {gap_str} | {flag_str} |"
        )
    md_lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "**Red flag** = gap > 5 years (earliest paper tagged pre-dates the concept's "
            "invention/popularization by more than 5 years).",
            "",
            f"**Headline:** {n_flagged}/{n_total} concepts show >5 year anachronistic tagging.",
            "",
            "If many concepts are anachronistically tagged, the OpenAlex classifier is "
            "retroactively assigning modern labels to older papers — likely via shared "
            "keywords or text patterns that happen to match. This biases ws2's semantic-",
            "plurality measurement: pre-1990 papers may be mis-tagged as covering modern "
            "topics, inflating apparent semantic continuity across eras.",
            "",
            "*(Detailed implications filled after inspection.)*",
        ]
    )
    out_path = _OUT_DIR / "anachronism-audit.md"
    out_path.write_text("\n".join(md_lines))
    print(f"  wrote {out_path}")
    print(f"\n  flagged: {n_flagged}/{n_total}; not-found: {n_no_match}")
    print("Check 2d complete.")


if __name__ == "__main__":
    main()
