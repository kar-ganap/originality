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


def _extract_source_type(primary_location_json: Any) -> str | None:
    """Extract ``source.type`` from a ``primary_location_json`` string.

    Returns ``None`` on missing / non-string / malformed JSON, or
    when the parsed structure lacks the expected ``source.type``
    path.

    Used to stratify per-author records by venue type
    (``"journal"`` / ``"repository"`` / ``"conference"`` / etc.).
    Phase 1.3 Step 1 smoke surfaced that ~26% of 2020 physics
    papers have ``source_type='repository'`` (predominantly arXiv
    preprints) and that those papers are far more likely to have
    no disambiguated authors (no ``author.id``). Carrying the
    source type per author-paper row lets downstream stratify
    coverage + bias correction by venue type.
    """
    if not isinstance(primary_location_json, str) or not primary_location_json:
        return None
    try:
        loc = json.loads(primary_location_json)
    except (json.JSONDecodeError, TypeError):
        return None
    if not isinstance(loc, dict):
        return None
    source = loc.get("source")
    if not isinstance(source, dict):
        return None
    source_type = source.get("type")
    if not isinstance(source_type, str):
        return None
    return source_type


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
    - ``source_type`` — extracted from ``primary_location.source.type``
      (e.g., ``"journal"``, ``"repository"``, ``"conference"``); used to
      stratify coverage + bias correction downstream
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
    source_type = _extract_source_type(paper.get("primary_location_json"))

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
            "source_type": source_type,
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

    Only the four columns we need are read off the input parquet
    (``id``, ``publication_year``, ``authorships_json``,
    ``primary_location_json``) — PyArrow column projection skips
    the rest at the file level.

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
        columns=[
            "id",
            "publication_year",
            "authorships_json",
            "primary_location_json",
        ],
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


# ---------- Step 2: disambiguation validation -------------------------------
#
# H1 (Phase 0.1 §10): cross-era-merger rate ≤ 5%. Per-author career length
# (max - min publication_year) > 60 → flag as candidate merger.
#
# H2 (Phase 0.2 Wave 3A scale-up): paper-level ORCID agreement ≥ 95%. For
# each ORCID that appears on ≥1 paper, OpenAlex's author.id should be
# consistent. Disagreement = OpenAlex split a real author across multiple
# IDs.


def compute_career_length_screen(
    authorships_table: pa.Table,
    threshold: int = 60,
) -> dict[str, Any]:
    """Per-author career-length stats + cross-era-merger flag count.

    For each unique ``author_id`` in the table, compute
    ``max(publication_year) - min(publication_year)``. Author IDs
    whose career length exceeds ``threshold`` years are flagged as
    cross-era-merger candidates (per Phase 0.1 §10).

    Rows with null ``publication_year`` are excluded from the per-
    author min/max; authors with NO non-null year are dropped from
    the screen entirely (uncountable).
    """
    df = authorships_table.select(
        ["author_id", "publication_year"],
    ).to_pandas()
    df = df[df["publication_year"].notna() & df["author_id"].notna()]

    grouped = df.groupby("author_id").agg(
        min_year=("publication_year", "min"),
        max_year=("publication_year", "max"),
        n_papers=("publication_year", "count"),
    )
    grouped["career_length"] = grouped["max_year"] - grouped["min_year"]

    n_unique = int(len(grouped))
    flagged = grouped[grouped["career_length"] > threshold]
    n_flagged = int(len(flagged))

    if n_unique > 0:
        pcts = grouped["career_length"].quantile([0.5, 0.75, 0.9, 0.95, 0.99])
        percentiles = {
            "p50": int(pcts.loc[0.50]),
            "p75": int(pcts.loc[0.75]),
            "p90": int(pcts.loc[0.90]),
            "p95": int(pcts.loc[0.95]),
            "p99": int(pcts.loc[0.99]),
        }
    else:
        percentiles = {"p50": 0, "p75": 0, "p90": 0, "p95": 0, "p99": 0}

    return {
        "threshold_years": threshold,
        "n_unique_authors": n_unique,
        "n_flagged_cross_era_merger": n_flagged,
        "flagged_fraction": (
            float(n_flagged / n_unique) if n_unique else 0.0
        ),
        "career_length_percentiles": percentiles,
        "flagged_author_ids_sample": [
            str(a) for a in flagged.index[:100].tolist()
        ],
    }


def compute_orcid_consistency(
    authorships_table: pa.Table,
) -> dict[str, Any]:
    """Per-ORCID author.id consistency + paper-level agreement rate.

    Filter to rows where BOTH ``author_orcid`` AND ``author_id`` are
    non-null. Group by ``author_orcid``:

    - consistent ORCID: maps to exactly 1 author.id
    - inconsistent ORCID: maps to >1 author.id (potential OpenAlex
      split of a single real author)

    Paper-level agreement = (#papers on the dominant pairing for each
    ORCID) / (#orcid-tagged paper rows). This mirrors Phase 0.2 Wave
    3A's 98.6% measurement and is the H2 metric.
    """
    df = authorships_table.select(
        ["author_id", "author_orcid"],
    ).to_pandas()
    df = df[df["author_orcid"].notna() & df["author_id"].notna()]

    n_with_orcid = int(len(df))
    if n_with_orcid == 0:
        return {
            "n_paper_rows_with_orcid": 0,
            "n_unique_orcids": 0,
            "n_orcids_consistent": 0,
            "n_orcids_inconsistent": 0,
            "orcid_consistency_rate": 0.0,
            "n_papers_dominant_pairing": 0,
            "paper_level_agreement_rate": 0.0,
        }

    by_orcid = df.groupby("author_orcid")["author_id"].agg([
        ("n_distinct_author_ids", "nunique"),
        ("total_papers", "count"),
        # Dominant author.id per ORCID = most frequent (ties → first
        # alphabetically, which is deterministic across runs).
        ("dominant_author_id", lambda s: s.value_counts().index[0]),
    ])

    n_orcids = int(len(by_orcid))
    consistent_mask = by_orcid["n_distinct_author_ids"] == 1
    n_consistent = int(consistent_mask.sum())
    n_inconsistent = n_orcids - n_consistent

    # Paper-level agreement: #papers where author.id == ORCID's
    # dominant author.id.
    df_with_dominant = df.merge(
        by_orcid[["dominant_author_id"]],
        left_on="author_orcid",
        right_index=True,
    )
    n_agreeing = int(
        (
            df_with_dominant["author_id"]
            == df_with_dominant["dominant_author_id"]
        ).sum(),
    )

    return {
        "n_paper_rows_with_orcid": n_with_orcid,
        "n_unique_orcids": n_orcids,
        "n_orcids_consistent": n_consistent,
        "n_orcids_inconsistent": n_inconsistent,
        "orcid_consistency_rate": (
            float(n_consistent / n_orcids) if n_orcids else 0.0
        ),
        "n_papers_dominant_pairing": n_agreeing,
        "paper_level_agreement_rate": (
            float(n_agreeing / n_with_orcid) if n_with_orcid else 0.0
        ),
    }


# H1, H2 acceptance thresholds — locked per Phase 1.3 plan §"Pre-
# registered hypotheses" (Layer A).
_H1_CROSS_ERA_MERGER_RATE_MAX = 0.05  # 5%
_H2_ORCID_AGREEMENT_MIN = 0.95         # 95%


def validate_disambiguation(
    authorships_parquet: str | Path,
    output_json: str | Path,
    *,
    career_length_threshold: int = 60,
) -> dict[str, Any]:
    """End-to-end disambiguation validation (Step 2).

    Reads the per-author-paper parquet produced by
    :func:`extract_authorships`, runs the H1 career-length screen
    and the H2 ORCID consistency check, writes a JSON summary, and
    returns the same dict.

    Acceptance gates (from Phase 1.3 plan):

    - H1: ``flagged_fraction`` (cross-era-merger rate) ≤ 5%
    - H2: ``paper_level_agreement_rate`` ≥ 95%

    ``h1_passes`` and ``h2_passes`` boolean flags in the output
    summarize each gate's verdict.
    """
    authorships_parquet = Path(authorships_parquet)
    output_json = Path(output_json)

    table = pq.read_table(str(authorships_parquet))

    career = compute_career_length_screen(
        table, threshold=career_length_threshold,
    )
    orcid = compute_orcid_consistency(table)

    h1_passes = career["flagged_fraction"] <= _H1_CROSS_ERA_MERGER_RATE_MAX
    h2_passes = (
        orcid["paper_level_agreement_rate"] >= _H2_ORCID_AGREEMENT_MIN
    )

    result: dict[str, Any] = {
        "source": str(authorships_parquet),
        "h1_career_length_screen": career,
        "h2_orcid_consistency": orcid,
        "h1_threshold_max_flagged_fraction": _H1_CROSS_ERA_MERGER_RATE_MAX,
        "h2_threshold_min_agreement_rate": _H2_ORCID_AGREEMENT_MIN,
        "h1_passes": bool(h1_passes),
        "h2_passes": bool(h2_passes),
    }

    output_json.write_text(json.dumps(result, indent=2))
    return result
