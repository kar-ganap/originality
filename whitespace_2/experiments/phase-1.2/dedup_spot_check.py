"""Phase 1.2 retro spot-check D — dedup correctness.

Picks 5 paper ids from the §0 sample (one each from a spread of
years), then on Modal counts:

- how many per-shard parquets contain that id
- the updated_date in each appearance
- the updated_date the dedup pass kept in the population

Verifies: for every id, population.updated_date == max(shard.updated_date).
A failure here would indicate the dedup is silently dropping rows
or keeping non-max-updated rows.

Why 5 not 100: this is a sanity check, not a statistical claim.
The dedup logic is a single SQL operation; if it works on 5
diverse ids, it works on 72M.

Usage:

  uv run --with modal python experiments/phase-1.2/dedup_spot_check.py
"""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any

import duckdb
import modal

dedup_spot_check_fn = modal.Function.from_name(
    "ws2-parse", "dedup_spot_check",
)

_OUT_DIR = Path(__file__).parent
_DATA_METADATA_DIR = _OUT_DIR.parent.parent / "data" / "metadata"
_SAMPLE_PARQUET = _DATA_METADATA_DIR / "section0-sample-1M.parquet"


def _pick_diverse_ids() -> list[tuple[str, int]]:
    """Pick 5 ids spanning a range of years (so we exercise both
    rare-shard cases (1975) and dense-shard cases (2020+)).

    Returns list of (id, publication_year). Uses a fixed seed so the
    spot-check is reproducible across runs.
    """
    con = duckdb.connect()
    rows = con.execute(f"""
        WITH per_year AS (
            SELECT id, publication_year,
                   ROW_NUMBER() OVER (
                       PARTITION BY publication_year
                       ORDER BY hash('ws2-spot-check-seed' || id)
                   ) AS rk
            FROM read_parquet('{_SAMPLE_PARQUET}')
            WHERE publication_year IN (1975, 1995, 2010, 2020, 2024)
        )
        SELECT id, publication_year FROM per_year
        WHERE rk = 1
        ORDER BY publication_year
    """).fetchall()
    con.close()
    return [(r[0], r[1]) for r in rows]


def main() -> None:
    print("Phase 1.2 retro spot-check D — dedup correctness")
    print()

    picks = _pick_diverse_ids()
    print(f"Picked {len(picks)} ids:")
    for paper_id, year in picks:
        print(f"  {year}: {paper_id}")
    print()

    ids = [p[0] for p in picks]
    print("Calling dedup_spot_check.remote() on Modal...")
    result: dict[str, Any] = dedup_spot_check_fn.remote(ids)
    print()

    # Group shard appearances by id
    by_id: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in result["shard_appearances"]:
        by_id[row["id"]].append(row)
    pop_by_id = {r["id"]: r for r in result["population"]}

    # Per-id verification
    pass_count = 0
    fail_count = 0
    summary = []
    for paper_id, year in picks:
        appearances = by_id.get(paper_id, [])
        pop_row = pop_by_id.get(paper_id)
        n_app = len(appearances)
        if not pop_row:
            print(f"  FAIL: {paper_id} ({year}): no population row "
                  f"(but {n_app} shard appearances)")
            fail_count += 1
            continue
        max_shard_date = max((a["updated_date"] for a in appearances),
                             default=None)
        pop_date = pop_row["updated_date"]
        ok = pop_date == max_shard_date
        status = "OK  " if ok else "FAIL"
        print(f"  [{status}] {year} {paper_id[-12:]}: "
              f"{n_app} shard rows, "
              f"max_shard_date={max_shard_date}, "
              f"pop_date={pop_date}")
        for a in appearances:
            print(f"          ↳ {a['filename']}: {a['updated_date']}")
        summary.append({
            "paper_id": paper_id,
            "publication_year": year,
            "n_shard_appearances": n_app,
            "shard_dates": [a["updated_date"] for a in appearances],
            "max_shard_date": max_shard_date,
            "population_date": pop_date,
            "dedup_correct": ok,
        })
        if ok:
            pass_count += 1
        else:
            fail_count += 1

    print()
    print(f"Summary: {pass_count}/{len(picks)} pass; {fail_count} fail")

    # Write JSON
    out_path = _OUT_DIR / "dedup-spot-check-results.json"
    out_path.write_text(json.dumps({
        "n_picks": len(picks),
        "pass_count": pass_count,
        "fail_count": fail_count,
        "results": summary,
    }, indent=2, default=str))
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
