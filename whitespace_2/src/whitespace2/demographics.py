"""Phase 1.3 — Author disambiguation + demographic-annotation pipeline.

This module produces per-author-paper records from the §0 v3 corpus
(via :func:`extract_authorships`), then attaches gender + country
+ confidence + bias-correction features in subsequent steps (added
as Phase 1.3 progresses).

Phase 1.3 plan: ``docs/phases/phase-1.3-plan.md``.

Step 1 (this module's current scope): extract per-author-paper rows
from the v3/v2 corpus parquets. Streaming over PyArrow batches so a
24.5M-paper input stays in <10 GB peak memory regardless of total
row count.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pyarrow as pa
import pyarrow.parquet as pq


def _extract_first_name(display_name: Any) -> tuple[str, bool]:
    """Extract a paper-author's first name + an ``is_initial`` flag.

    Heuristic: take the first whitespace-separated token of
    ``display_name``, strip trailing periods, return as the first
    name. Flag as ``is_initial`` if the resulting token is ≤2
    characters (e.g., ``"C"`` from ``"C. Gauss"``; ``"CF"`` from
    ``"CF Gauss"``) — these names won't yield reliable
    gender_guesser / Genderize / NamSor lookups and downstream
    code should skip or treat them as unknown.

    Returns ``("", False)`` on missing / non-string / whitespace-
    only input.
    """
    if not isinstance(display_name, str):
        return ("", False)
    tokens = display_name.strip().split()
    if not tokens:
        return ("", False)
    first = tokens[0].rstrip(".")
    is_initial = len(first) <= 2
    return (first, is_initial)


def explode_authorships_for_paper(
    paper: dict[str, Any],
) -> list[dict[str, Any]]:
    """Explode a single paper's ``authorships_json`` into per-author rows.

    Each emitted row has:

    - ``paper_id`` — copied from the input
    - ``publication_year`` — copied (may be None)
    - ``author_id`` — OpenAlex author URI (the disambiguation key)
    - ``author_display_name`` — full ``author.display_name``
    - ``author_first_name`` — extracted via :func:`_extract_first_name`
    - ``first_name_is_initial`` — bool flag
    - ``author_orcid`` — ORCID URI or None
    - ``author_position`` — ``"first"``/``"middle"``/``"last"``
    - ``is_corresponding`` — bool
    - ``countries`` — list of ISO country codes from
      ``authorships[i].countries`` (OpenAlex's pre-aggregated field)

    Authors without an ``author.id`` are skipped — there's no stable
    disambiguation key to track them across papers.

    Returns ``[]`` (empty list, no exception) on missing / malformed
    / empty / wrong-shape ``authorships_json``.
    """
    paper_id = paper.get("id", "")
    publication_year = paper.get("publication_year")
    authorships_json = paper.get("authorships_json")

    if not authorships_json or not isinstance(authorships_json, str):
        return []
    try:
        authorships = json.loads(authorships_json)
    except (json.JSONDecodeError, TypeError):
        return []
    if not isinstance(authorships, list):
        return []

    rows: list[dict[str, Any]] = []
    for entry in authorships:
        if not isinstance(entry, dict):
            continue

        author_obj = entry.get("author")
        if not isinstance(author_obj, dict):
            continue

        author_id = author_obj.get("id")
        if not isinstance(author_id, str) or not author_id:
            continue  # no disambiguation key → drop

        display_name = author_obj.get("display_name") or ""
        if not isinstance(display_name, str):
            display_name = ""
        first_name, is_initial = _extract_first_name(display_name)

        orcid = author_obj.get("orcid")
        if orcid is not None and not isinstance(orcid, str):
            orcid = None

        author_position = entry.get("author_position")
        if author_position is not None and not isinstance(author_position, str):
            author_position = None

        is_corresponding = bool(entry.get("is_corresponding"))

        countries = entry.get("countries") or []
        if not isinstance(countries, list):
            countries = []
        # Filter to string elements only
        countries = [c for c in countries if isinstance(c, str)]

        rows.append({
            "paper_id": paper_id,
            "publication_year": publication_year,
            "author_id": author_id,
            "author_display_name": display_name,
            "author_first_name": first_name,
            "first_name_is_initial": is_initial,
            "author_orcid": orcid,
            "author_position": author_position,
            "is_corresponding": is_corresponding,
            "countries": countries,
        })

    return rows


def extract_authorships(
    source_path: str | Path,
    output_path: str | Path,
    batch_size: int = 50_000,
) -> dict[str, Any]:
    """Stream a §0 corpus parquet → per-author-paper parquet.

    Lazy/batched: critical at production scale (v3 = 24.5M papers
    → ~75M author-paper rows). PyArrow batched read keeps peak
    memory bounded by ``batch_size``-many papers regardless of
    total row count.

    Only the three columns we need are read off the input parquet
    (``id``, ``publication_year``, ``authorships_json``) — PyArrow
    column projection skips the rest at the file level.

    If no paper in the input has any extractable author (all
    empty/malformed authorships), no output parquet is written
    and the result dict reports ``n_author_paper_rows = 0``.
    """
    source_path = Path(source_path)
    output_path = Path(output_path)

    pf = pq.ParquetFile(str(source_path))

    writer: pq.ParquetWriter | None = None
    n_papers_seen = 0
    n_rows_written = 0

    for batch in pf.iter_batches(
        batch_size=batch_size,
        columns=["id", "publication_year", "authorships_json"],
    ):
        paper_dicts = batch.to_pylist()
        all_rows: list[dict[str, Any]] = []
        for paper in paper_dicts:
            all_rows.extend(explode_authorships_for_paper(paper))
        if all_rows:
            out_tbl = pa.Table.from_pylist(all_rows)
            if writer is None:
                writer = pq.ParquetWriter(
                    str(output_path), out_tbl.schema, compression="zstd",
                )
            writer.write_table(out_tbl)
            n_rows_written += len(all_rows)
        n_papers_seen += len(paper_dicts)

    if writer is not None:
        writer.close()

    return {
        "source": str(source_path),
        "output": str(output_path),
        "n_papers": int(n_papers_seen),
        "n_author_paper_rows": int(n_rows_written),
    }
