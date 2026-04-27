"""Check 2d follow-up — within-window anachronism with score thresholding.

Question: are pre-1990 papers tagged with post-2000 concepts at meaningful
scores? If so, the anachronism concern from the original Check 2d carries
into ws2's actual analytical window (1970-2024). If high scores on pre-1990
papers are rare for clearly-anachronistic concepts (e.g., Bitcoin, GAN), then
the anachronism issue is largely confined to the very-old tail outside ws2's
window.

For each of ~20 modern concepts, we:

1. Filter for pre-1990 papers tagged (any score) with that concept.
2. Pull top-50 by cited_by_count desc.
3. Score-threshold per paper.
4. Report: how many of those pre-1990 papers have score≥0.3 / ≥0.5?
5. Spot-check titles: are they genuine (precursor) or anachronistic (irrelevant)?

Outputs:

- ``within-window-anachronism.csv`` — per-concept stats + sample paper titles
- ``within-window-anachronism.md`` — interpretation
"""

from __future__ import annotations

import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

from whitespace2 import openalex

_OUT_DIR = Path(__file__).parent

# (concept query, year the concept's popular usage began, anachronism category)
# Anachronism category:
#   "hard"     = pre-1990 score>=0.3 is almost certainly anachronism
#   "medium"   = pre-1990 score>=0.3 might be genuine precursor (gray zone)
#   "soft"     = the concept has 20th-century roots; pre-1990 tag could be legit
_TARGETS: list[tuple[str, int, str]] = [
    ("Deep learning", 2006, "medium"),  # multi-layer NN existed in 80s but term post-2006
    ("Transformer (machine learning model)", 2017, "hard"),
    ("Generative adversarial network", 2014, "hard"),
    ("BERT", 2018, "hard"),
    ("Convolutional neural network", 1989, "soft"),  # LeNet 1989; some 80s precursors
    ("Recurrent neural network", 1986, "soft"),
    ("Word embedding", 2013, "hard"),
    ("CRISPR", 2012, "medium"),  # bacterial CRISPR discovered ~1987-1993
    ("Cloud computing", 2006, "hard"),
    ("Internet of things", 1999, "hard"),
    ("Big data", 2005, "hard"),
    ("Bitcoin", 2009, "hard"),
    ("Smartphone", 2007, "hard"),
    ("Augmented reality", 1992, "soft"),  # term coined in 1990
    ("World Wide Web", 1991, "hard"),
    ("MapReduce", 2004, "hard"),
    ("Quantum computing", 1985, "soft"),
    ("Machine learning", 1959, "soft"),  # term older
    ("Artificial intelligence", 1956, "soft"),
    ("Neural network", 1943, "soft"),  # McCulloch-Pitts
]
_PER_CELL = 50


def _score_for_concept(work: dict[str, Any], target_id: str) -> float:
    for concept in work.get("concepts") or []:
        if not isinstance(concept, dict):
            continue
        cid = (concept.get("id") or "").rsplit("/", 1)[-1]
        if cid == target_id:
            return float(concept.get("score") or 0.0)
    return 0.0


def _find_concept_id(query: str) -> tuple[str, str] | None:
    results = openalex.search_concepts(query, per_page=5)
    if not results:
        return None
    # Best match: case-insensitive exact display_name, else first
    for r in results:
        if isinstance(r, dict) and (r.get("display_name") or "").lower() == query.lower():
            cid = (r.get("id") or "").rsplit("/", 1)[-1]
            return cid, r.get("display_name") or query
    first = results[0]
    cid = (first.get("id") or "").rsplit("/", 1)[-1]
    return cid, first.get("display_name") or query


def main() -> None:
    print("Check 2d within-window anachronism (score-thresholded)")
    snapshot_date = openalex.latest_snapshot_date()

    rows: list[dict[str, Any]] = []
    sample_titles: dict[str, list[dict[str, Any]]] = {}

    for query, popular_year, category in _TARGETS:
        print(f"\n  {query} (popular={popular_year}, category={category})")
        match = _find_concept_id(query)
        if match is None:
            print("    no concept found")
            rows.append(
                {
                    "query": query,
                    "popular_year": popular_year,
                    "category": category,
                    "concept_id": None,
                    "matched_name": None,
                    "n_pre1990_papers": 0,
                    "n_score_ge_0.3": 0,
                    "n_score_ge_0.5": 0,
                    "frac_score_ge_0.3": float("nan"),
                    "frac_score_ge_0.5": float("nan"),
                }
            )
            continue
        cid, matched_name = match
        time.sleep(0.5)
        try:
            works = openalex.fetch_works(
                filters={
                    "concepts.id": cid,
                    "publication_year": "1970-1989",
                },
                sort="cited_by_count:desc",
                select=["id", "title", "concepts", "cited_by_count", "publication_year"],
                per_page=_PER_CELL,
            )
        except RuntimeError as err:
            print(f"    fetch failed: {err}")
            continue
        time.sleep(0.5)
        n = len(works)
        scored = [(w, _score_for_concept(w, cid)) for w in works]
        n_ge_03 = sum(1 for _, s in scored if s >= 0.3)
        n_ge_05 = sum(1 for _, s in scored if s >= 0.5)
        print(f"    matched={matched_name!r}; pre-1990 papers={n}; score>=0.3: {n_ge_03}; >=0.5: {n_ge_05}")
        rows.append(
            {
                "query": query,
                "popular_year": popular_year,
                "category": category,
                "concept_id": cid,
                "matched_name": matched_name,
                "n_pre1990_papers": n,
                "n_score_ge_0.3": n_ge_03,
                "n_score_ge_0.5": n_ge_05,
                "frac_score_ge_0.3": (n_ge_03 / n) if n else 0.0,
                "frac_score_ge_0.5": (n_ge_05 / n) if n else 0.0,
            }
        )
        # Capture top-5 score≥0.3 papers for spot-check
        spot_check = [
            {
                "year": w.get("publication_year"),
                "title": w.get("title"),
                "cited_by_count": w.get("cited_by_count"),
                "score": s,
            }
            for w, s in sorted(scored, key=lambda x: -x[1])[:5]
            if s >= 0.3
        ]
        sample_titles[query] = spot_check

    df = pd.DataFrame(rows)
    csv_path = _OUT_DIR / "within-window-anachronism.csv"
    df.to_csv(csv_path, index=False)
    print(f"\n  wrote {csv_path}")

    md_lines = [
        "# Check 2d follow-up — within-window anachronism (score-thresholded)",
        "",
        f"**Run date:** {datetime.now(timezone.utc).date().isoformat()}",
        f"**Snapshot recorded:** {snapshot_date}",
        f"**Window:** 1970-1989 (ws2's pre-1990 retention zone per §13)",
        f"**Concepts checked:** {len(_TARGETS)}",
        "",
        "## Per-concept counts",
        "",
        "| Concept | Popular | Cat | n pre-1990 | score≥0.3 | score≥0.5 | %≥0.3 |",
        "|---|---:|---|---:|---:|---:|---:|",
    ]
    for _, row in df.iterrows():
        if pd.isna(row["frac_score_ge_0.3"]):
            frac_str = "—"
        else:
            frac_str = f"{row['frac_score_ge_0.3']:.0%}"
        md_lines.append(
            f"| {row['query']} | {row['popular_year']} | {row['category']} | "
            f"{int(row['n_pre1990_papers'])} | "
            f"{int(row['n_score_ge_0.3'])} | "
            f"{int(row['n_score_ge_0.5'])} | "
            f"{frac_str} |"
        )

    md_lines.extend(
        [
            "",
            "## Spot-check: top score≥0.3 pre-1990 papers per concept",
            "",
            "Are these genuine precursors (legit) or anachronisms (irrelevant)?",
            "",
        ]
    )
    for query, papers in sample_titles.items():
        if not papers:
            continue
        md_lines.append(f"### {query}")
        md_lines.append("")
        for p in papers:
            year = int(p["year"]) if p["year"] else "?"
            cited = int(p["cited_by_count"]) if p["cited_by_count"] is not None else 0
            md_lines.append(
                f"- {year} (score={p['score']:.2f}, cited={cited}): "
                f"{(p['title'] or '(no title)')[:90]}"
            )
        md_lines.append("")

    md_lines.extend(
        [
            "## Decision support",
            "",
            "**For 'hard' anachronism concepts (term coined post-2000, no precursor):**",
            "any score≥0.3 pre-1990 paper is a likely anachronism. If hard-category",
            "concepts have meaningful pre-1990 score≥0.3 counts, the OpenAlex classifier",
            "is producing genuine anachronism within ws2's window. Counts ≤2 per concept",
            "are likely tolerable noise; counts ≥10 indicate systematic anachronism.",
            "",
            "**For 'medium' / 'soft' concepts:** pre-1990 score≥0.3 papers may be genuine",
            "precursors (e.g., 1980s neural-net papers tagged 'Deep learning' at low",
            "score). Spot-check titles to disambiguate.",
            "",
            "*(Final assessment filled after inspection of the spot-check titles.)*",
        ]
    )
    out_path = _OUT_DIR / "within-window-anachronism.md"
    out_path.write_text("\n".join(md_lines))
    print(f"  wrote {out_path}")
    print("\nWithin-window anachronism check complete.")


if __name__ == "__main__":
    main()
