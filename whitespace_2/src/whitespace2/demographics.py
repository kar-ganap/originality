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
from collections.abc import Iterable
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


# ---------- Step 3a: gender_guesser annotation + per-author rollup ----------
#
# Phase 1.3 plan §"Pre-flight choices already locked": gender_guesser
# is the offline / deterministic / free primary inference. Step 3b
# layers Genderize cross-validation on top of this; Step 4 layers
# NamSor bias estimation. Step 3a produces a per-author parquet with
# gender_guesser-only annotation that downstream can join with the
# Genderize + NamSor outputs.
#
# gender_guesser returns one of six labels:
#   male            confident male                  → ("male",    p=1.0)
#   female          confident female                → ("female",  p=1.0)
#   mostly_male     unisex but mostly male          → ("male",    p=0.7)
#   mostly_female   unisex but mostly female        → ("female",  p=0.7)
#   andy            ambiguous unisex (used both)    → ("unknown", p=0.0)
#   unknown         name not in the dictionary      → ("unknown", p=0.0)
#
# The p≥0.8 "confident" gate maps cleanly: confident = label ∈
# {male, female}. mostly_* fall into the low-confidence subset that
# Genderize (Step 3b) cross-validates and NamSor (Step 4) bias-
# estimates.

_GG_LABEL_MAP: dict[str, tuple[str, float]] = {
    "male": ("male", 1.0),
    "female": ("female", 1.0),
    "mostly_male": ("male", 0.7),
    "mostly_female": ("female", 0.7),
    "andy": ("unknown", 0.0),
    "unknown": ("unknown", 0.0),
}


def _gg_label_to_gender_probability(label: str) -> tuple[str, float]:
    """Map a gender_guesser raw label to (gender, probability).

    Unknown / unexpected labels default to ("unknown", 0.0) — safer
    than raising, since gender_guesser's label set could expand in
    future versions and we want the pipeline to keep running.
    """
    return _GG_LABEL_MAP.get(label, ("unknown", 0.0))


def annotate_with_gender_guesser(
    first_names: Iterable[str],
) -> dict[str, dict[str, Any]]:
    """Per-name gender_guesser annotation.

    Deduplicates the input. Empty / whitespace-only names are
    skipped. Returns ``{first_name: {gg_label, gender, probability}}``.

    Lazy import of ``gender_guesser`` (it's in the ``demo`` extra;
    we don't want top-of-module imports to fail when the extra
    isn't installed and the user isn't running the annotation
    step).
    """
    import gender_guesser.detector as gg_detector

    detector = gg_detector.Detector()
    unique = {n.strip() for n in first_names if isinstance(n, str) and n.strip()}

    out: dict[str, dict[str, Any]] = {}
    for name in unique:
        label = detector.get_gender(name)
        gender, p = _gg_label_to_gender_probability(label)
        out[name] = {"gg_label": label, "gender": gender, "probability": p}
    return out


def aggregate_per_author(
    authorships_table: pa.Table,
    name_gender_dict: dict[str, dict[str, Any]],
) -> pa.Table:
    """Per-author rollup from per-author-paper rows.

    Inputs:
      - ``authorships_table`` from :func:`extract_authorships`
        (the per-author-paper parquet schema)
      - ``name_gender_dict`` from :func:`annotate_with_gender_guesser`
        (``{first_name: {gg_label, gender, probability}}``)

    For each unique ``author_id``:
      - ``author_first_name`` = mode (most common across that author's
        paper rows; consistent author_id should have consistent name)
      - ``gender`` / ``gender_probability`` = lookup ``author_first_name``
        in ``name_gender_dict``, default ``("unknown", 0.0)``
      - ``primary_country`` = most common country across the author's
        per-paper ``countries`` lists (None if none)
      - ``n_papers`` = count of paper rows for this author_id
      - ``n_papers_with_orcid`` = count where ``author_orcid`` non-null
      - ``min_year`` / ``max_year`` = first / last paper year
        (None if no non-null years)

    Returns a per-author Arrow table.
    """
    df = authorships_table.select([
        "author_id",
        "publication_year",
        "author_first_name",
        "author_orcid",
        "countries",
    ]).to_pandas()

    def _mode_or_none(values: Any) -> str | None:
        cleaned = [v for v in values if isinstance(v, str) and v]
        if not cleaned:
            return None
        from collections import Counter
        return Counter(cleaned).most_common(1)[0][0]

    def _country_mode(country_lists: Any) -> str | None:
        from collections import Counter
        flat: list[str] = []
        for lst in country_lists:
            if lst is None:
                continue
            # lst may be a Python list or a numpy array — iterate
            # without relying on its truthiness (numpy arrays raise
            # DeprecationWarning on bool conversion).
            try:
                items = list(lst)
            except TypeError:
                continue
            flat.extend(c for c in items if isinstance(c, str))
        if not flat:
            return None
        return Counter(flat).most_common(1)[0][0]

    grouped = df.groupby("author_id").agg(
        author_first_name=("author_first_name", _mode_or_none),
        n_papers=("author_first_name", "count"),
        n_papers_with_orcid=("author_orcid", lambda s: int(s.notna().sum())),
        min_year=("publication_year", lambda s: (
            int(s.min()) if s.notna().any() else None
        )),
        max_year=("publication_year", lambda s: (
            int(s.max()) if s.notna().any() else None
        )),
        primary_country=("countries", _country_mode),
    ).reset_index()

    # Attach gender via lookup
    def _lookup(name: str | None) -> tuple[str, float]:
        if not isinstance(name, str) or not name:
            return ("unknown", 0.0)
        rec = name_gender_dict.get(name)
        if not rec:
            return ("unknown", 0.0)
        return (rec["gender"], rec["probability"])

    grouped["gender"] = grouped["author_first_name"].apply(
        lambda n: _lookup(n)[0],
    )
    grouped["gender_probability"] = grouped["author_first_name"].apply(
        lambda n: _lookup(n)[1],
    )
    grouped["gg_label"] = grouped["author_first_name"].apply(
        lambda n: (
            name_gender_dict.get(n, {}).get("gg_label", "unknown")
            if isinstance(n, str)
            else "unknown"
        ),
    )

    return pa.Table.from_pandas(grouped, preserve_index=False)


def annotate_gender_country(
    authorships_parquet: str | Path,
    output_parquet: str | Path,
) -> dict[str, Any]:
    """End-to-end Step 3a driver: per-author gender + country annotation.

    Reads the Step 1 output, extracts unique first names, runs
    :func:`annotate_with_gender_guesser`, aggregates per-author via
    :func:`aggregate_per_author`, writes the per-author parquet,
    and returns a summary dict.

    Step 3a covers gender_guesser only. Step 3b will layer Genderize
    cross-validation on top by joining a second annotation dict into
    the per-author table.
    """
    authorships_parquet = Path(authorships_parquet)
    output_parquet = Path(output_parquet)

    table = pq.read_table(str(authorships_parquet))

    first_names = table.column("author_first_name").to_pylist()
    name_to_gg = annotate_with_gender_guesser(first_names)

    per_author = aggregate_per_author(table, name_to_gg)
    pq.write_table(per_author, str(output_parquet), compression="zstd")

    # Coverage summary
    df = per_author.to_pandas()
    n_authors = int(len(df))
    gender_counts = df["gender"].value_counts().to_dict()
    gender_confident = int(
        ((df["gender"] != "unknown") & (df["gender_probability"] >= 0.8)).sum(),
    )
    n_with_country = int(df["primary_country"].notna().sum())

    return {
        "source": str(authorships_parquet),
        "output": str(output_parquet),
        "n_unique_authors": n_authors,
        "n_unique_first_names": int(len(name_to_gg)),
        "gender_counts": {str(k): int(v) for k, v in gender_counts.items()},
        "gender_confident_count": gender_confident,
        "gender_confident_rate": (
            float(gender_confident / n_authors) if n_authors else 0.0
        ),
        "country_coverage_count": n_with_country,
        "country_coverage_rate": (
            float(n_with_country / n_authors) if n_authors else 0.0
        ),
    }


# ---------- Step 3b: Genderize cross-validation -----------------------------
#
# Genderize is a freemium HTTPS API: https://api.genderize.io
#   GET /?name[]=John&name[]=Mary&apikey=...
#   → [{"name": "John", "gender": "male", "probability": 0.99, "count": ...},
#       {"name": "Mary", "gender": "female", "probability": 0.98, "count": ...}]
#
# Quota (keyed-free tier): 2,500 names per month (one call counts toward
# both name-count and call-count). We treat ``max_names`` as the quota
# gate and stop dispatching once we'd exceed it.
#
# Phase 0.2 Wave 1B verified the keyed-free flow with the user's key.
# Phase 1.3 plan §"Pre-flight choices already locked": Genderize is the
# **cross-validation** layer over gender_guesser (the primary), not a
# replacement. Step 3b runs Genderize only on the low-confidence subset
# (gender_guesser p<0.8).

_GENDERIZE_URL = "https://api.genderize.io"


def query_genderize_batch(
    names: list[str],
    api_key: str,
    timeout: float = 30.0,
) -> dict[str, dict[str, Any]]:
    """One Genderize HTTP call for up to 10 names.

    Returns ``{name: {gender, probability, count}}``. Names not in
    the response are simply absent from the output dict (caller
    decides how to handle).

    Names returned with ``gender=None`` (Genderize couldn't classify)
    are kept as-is in the dict — that's distinct from "not queried."

    Raises on HTTP errors (≥400) — the orchestrator
    :func:`query_genderize` catches and counts these.
    """
    import requests

    params: dict[str, Any] = {
        "name[]": list(names),
        "apikey": api_key,
    }
    resp = requests.get(_GENDERIZE_URL, params=params, timeout=timeout)
    resp.raise_for_status()
    data = resp.json()

    if not isinstance(data, list):
        return {}

    out: dict[str, dict[str, Any]] = {}
    for item in data:
        if not isinstance(item, dict):
            continue
        name = item.get("name")
        if not isinstance(name, str) or not name:
            continue
        out[name] = {
            "gender": item.get("gender"),  # str | None
            "probability": float(item.get("probability") or 0.0),
            "count": int(item.get("count") or 0),
        }
    return out


def query_genderize(
    names: Iterable[str],
    api_key: str,
    *,
    max_names: int = 2500,
    batch_size: int = 10,
    timeout: float = 30.0,
) -> dict[str, Any]:
    """Orchestrate batched Genderize calls up to a quota.

    Batches the input ``names`` into groups of ``batch_size`` (Genderize
    accepts up to 10 names per request). Stops dispatching once
    ``max_names`` would be exceeded — keeps prior results, sets
    ``quota_exhausted=True`` in the summary.

    Errors in individual batches (HTTP 4xx/5xx, network timeouts) are
    caught and counted in ``n_errors``; the orchestrator continues
    with subsequent batches so a transient failure doesn't lose all
    progress.

    Returns a summary dict with the per-name results plus operational
    metrics for the verify-results doc.
    """
    deduped: list[str] = []
    seen: set[str] = set()
    for n in names:
        if not isinstance(n, str) or not n.strip():
            continue
        if n in seen:
            continue
        seen.add(n)
        deduped.append(n)

    n_queried = 0
    n_calls = 0
    n_errors = 0
    quota_exhausted = False
    results: dict[str, dict[str, Any]] = {}

    for i in range(0, len(deduped), batch_size):
        if n_queried >= max_names:
            quota_exhausted = True
            break
        # Trim the batch to not exceed max_names
        remaining = max_names - n_queried
        batch = deduped[i : i + min(batch_size, remaining)]
        if not batch:
            quota_exhausted = True
            break

        try:
            batch_result = query_genderize_batch(
                batch, api_key=api_key, timeout=timeout,
            )
            results.update(batch_result)
        except Exception:
            n_errors += 1

        n_queried += len(batch)
        n_calls += 1

    # Detect quota exhaustion by post-condition too: if we
    # processed every item without break, max_names was either
    # equal to or exceeded len(deduped) — not exhausted in that
    # case.
    if n_queried < len(deduped):
        quota_exhausted = True

    return {
        "results": results,
        "n_names_queried": n_queried,
        "n_calls": n_calls,
        "n_errors": n_errors,
        "max_names": max_names,
        "quota_exhausted": quota_exhausted,
    }


# Confidence gate for "both methods confident" (per Phase 1.3 plan
# §"Pre-registered hypotheses"): probability ≥ 0.8 from gg AND
# probability ≥ 0.8 from Genderize.
_CONFIDENCE_GATE = 0.8


def combine_gg_and_genderize(
    gg_results: dict[str, dict[str, Any]],
    genderize_results: dict[str, dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    """Per-name fusion of gender_guesser + Genderize annotations.

    For each name in ``gg_results`` (the universe is what gg saw):

    - ``combined_gender``: gg's gender if gg is confident (p ≥ 0.8);
      otherwise Genderize's gender if Genderize is confident;
      otherwise gg's (low-confidence) gender.
    - ``combined_probability``: probability associated with combined
      pick.
    - ``genderize_gender`` / ``genderize_probability`` /
      ``genderize_count``: pass-through (or None if Genderize wasn't
      queried for this name).
    - ``both_methods_confident``: both gg and Genderize at p ≥ 0.8.
    - ``both_methods_agree``: both confident AND same gender — the
      "agreement rate" metric tracked from Phase 0.2 Check 3.

    Names with only gg (no Genderize result) get genderize fields =
    None and the combined fields fall back to gg's pick.
    """
    out: dict[str, dict[str, Any]] = {}
    for name, gg in gg_results.items():
        gz = genderize_results.get(name)
        gg_gender = gg.get("gender", "unknown")
        gg_prob = float(gg.get("probability", 0.0))
        gg_confident = gg_prob >= _CONFIDENCE_GATE

        if gz is not None:
            gz_gender = gz.get("gender")  # str | None
            gz_prob = float(gz.get("probability", 0.0))
            gz_count = int(gz.get("count", 0))
            gz_confident = (
                isinstance(gz_gender, str) and gz_prob >= _CONFIDENCE_GATE
            )
        else:
            gz_gender = None
            gz_prob = 0.0
            gz_count = 0
            gz_confident = False

        # Combined pick policy (gg is the locked primary per Phase 1.3
        # plan):
        #   - If gg has ANY non-"unknown" pick, keep it (gg owns the
        #     final answer for any name it has signal on, even at
        #     mid-confidence p=0.7).
        #   - If gg returned "unknown" (the name isn't in its
        #     dictionary at all), use Genderize's pick if Genderize
        #     is confident.
        #   - Otherwise fall through to gg's "unknown".
        # This keeps gender_guesser as the locked primary while
        # letting Genderize EXTEND coverage on names gg can't handle.
        if gg_gender != "unknown":
            combined_gender = gg_gender
            combined_prob = gg_prob
        elif gz_confident and isinstance(gz_gender, str):
            combined_gender = gz_gender
            combined_prob = gz_prob
        else:
            combined_gender = gg_gender
            combined_prob = gg_prob

        both_confident = gg_confident and gz_confident
        both_agree = (
            both_confident and gg_gender == gz_gender
        )

        out[name] = {
            **gg,
            "genderize_gender": gz_gender,
            "genderize_probability": gz_prob,
            "genderize_count": gz_count,
            "combined_gender": combined_gender,
            "combined_probability": combined_prob,
            "both_methods_confident": both_confident,
            "both_methods_agree": both_agree,
        }
    return out
