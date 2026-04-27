"""Check 2e — Hand-audit setup.

Pick two stable subfields that clearly existed in 1975 (operating systems,
compilers); fetch the top 50 papers tagged with each in 1975 and 2020.
Output a CSV for human qualitative review of classifier reliability across
eras.

The interpretation is qualitative and manual — does the 1975 sample look
like genuine OS/compiler papers, or do mis-tagged papers slip in? Same for
2020.

Outputs:

- ``hand-audit-papers.csv`` — 4 cells × 50 papers = 200 rows for review
- ``hand-audit-papers.md`` — review template
"""

from __future__ import annotations

import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

from whitespace2 import openalex

_OUT_DIR = Path(__file__).parent

# Stable subfields that demonstrably existed in 1975 — picked so that
# off-target classifications are easy for a human to spot.
_SUBFIELDS: list[tuple[str, str]] = [
    ("Operating system", "operating systems"),
    ("Compiler", "compilers"),
]

_YEARS_TO_AUDIT = [1975, 2020]
_PER_CELL = 50


def _abstract_preview(work: dict[str, Any]) -> str:
    """Reconstruct a short abstract preview from the inverted index."""
    inverted = work.get("abstract_inverted_index")
    if not isinstance(inverted, dict) or not inverted:
        return ""
    # Reconstruct in word order.
    word_at_pos: dict[int, str] = {}
    for word, positions in inverted.items():
        if isinstance(positions, list):
            for pos in positions:
                if isinstance(pos, int):
                    word_at_pos[pos] = word
    if not word_at_pos:
        return ""
    text = " ".join(word_at_pos[i] for i in sorted(word_at_pos.keys()))
    return text[:300] + ("..." if len(text) > 300 else "")


def _author_names(work: dict[str, Any], n: int = 3) -> str:
    authorships = work.get("authorships") or []
    names = []
    for authorship in authorships[:n]:
        if not isinstance(authorship, dict):
            continue
        author = authorship.get("author") or {}
        if isinstance(author, dict):
            display = author.get("display_name")
            if isinstance(display, str):
                names.append(display)
    return "; ".join(names)


def _concept_summary(work: dict[str, Any], n: int = 3) -> str:
    concepts = work.get("concepts") or []
    summaries = []
    for concept in concepts[:n]:
        if not isinstance(concept, dict):
            continue
        name = concept.get("display_name") or "?"
        score = concept.get("score") or 0.0
        summaries.append(f"{name} ({score:.2f})")
    return "; ".join(summaries)


def main() -> None:
    print("Check 2e — Hand-audit setup")
    snapshot_date = openalex.latest_snapshot_date()

    rows: list[dict[str, Any]] = []
    select = [
        "id",
        "title",
        "publication_year",
        "abstract_inverted_index",
        "concepts",
        "authorships",
        "primary_location",
    ]

    for subfield_query, subfield_label in _SUBFIELDS:
        # Look up the concept ID
        results = openalex.search_concepts(subfield_query, per_page=5)
        if not results:
            print(f"  WARN: no concept found for {subfield_query}")
            continue
        # Best match: case-insensitive exact display_name, else first
        concept = None
        for r in results:
            if isinstance(r, dict) and (r.get("display_name") or "").lower() == subfield_query.lower():
                concept = r
                break
        if concept is None:
            concept = results[0]
        concept_id = concept["id"].rsplit("/", 1)[-1]
        concept_name = concept.get("display_name")
        print(f"  subfield={subfield_label!r}: concept={concept_name!r} ({concept_id})")
        time.sleep(0.5)

        for year in _YEARS_TO_AUDIT:
            try:
                works = openalex.fetch_works(
                    filters={"concepts.id": concept_id, "publication_year": str(year)},
                    sort="cited_by_count:desc",
                    select=select,
                    per_page=_PER_CELL,
                )
            except RuntimeError as err:
                print(f"    WARN: fetch failed for {year}: {err}")
                continue
            print(f"    {year}: {len(works)} papers")
            for rank, work in enumerate(works, start=1):
                rows.append(
                    {
                        "subfield": subfield_label,
                        "year": year,
                        "rank": rank,
                        "work_id": work.get("id"),
                        "title": work.get("title"),
                        "authors_top3": _author_names(work, n=3),
                        "concepts_top3": _concept_summary(work, n=3),
                        "abstract_preview": _abstract_preview(work),
                        "primary_source": (
                            (work.get("primary_location") or {}).get("source") or {}
                        ).get("display_name"),
                    }
                )
            time.sleep(0.5)

    df = pd.DataFrame(rows)
    csv_path = _OUT_DIR / "hand-audit-papers.csv"
    df.to_csv(csv_path, index=False)
    print(f"\n  wrote {csv_path} ({len(df)} rows)")

    md_lines = [
        "# Check 2e — Hand-audit setup",
        "",
        f"**Run date:** {datetime.now(timezone.utc).date().isoformat()}",
        f"**Snapshot recorded:** {snapshot_date}",
        f"**Subfields:** {[s[1] for s in _SUBFIELDS]}",
        f"**Years audited:** {_YEARS_TO_AUDIT}",
        f"**Per cell:** {_PER_CELL} top-cited papers",
        f"**Total papers fetched:** {len(df)}",
        "",
        "## How to review",
        "",
        "Open `hand-audit-papers.csv`. For each row, judge whether the paper "
        "*genuinely* belongs to the subfield (operating systems / compilers) "
        "based on title + abstract preview. Mark a column `audit_correct` "
        "(yes/no/uncertain) for each row.",
        "",
        "Then count the false-positive rate per (subfield, year) cell:",
        "- 1975 cells: how many of 50 papers are clearly off-target?",
        "- 2020 cells: same question.",
        "",
        "If the false-positive rate differs substantially across eras "
        "(e.g., 1975 has 30% off-target but 2020 has 5%), the classifier is "
        "drifting in reliability across eras — this biases ws2's semantic-",
        "plurality measurement.",
        "",
        "## Interpretation",
        "",
        "*(Filled after manual review of the CSV.)*",
    ]
    out_path = _OUT_DIR / "hand-audit-papers.md"
    out_path.write_text("\n".join(md_lines))
    print(f"  wrote {out_path}")
    print("\nCheck 2e setup complete (qualitative review pending).")


if __name__ == "__main__":
    main()
