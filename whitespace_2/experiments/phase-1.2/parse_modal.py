"""Phase 1.2 Step 3 — Modal CPU function for bulk-dump shard parsing.

For each OpenAlex works manifest shard URL, the function:
1. Streams the gzipped JSONL from OpenAlex's public S3 bucket
2. Parses each line with orjson (5-10× faster than stdlib json)
3. Applies the locked §0 filter (`whitespace2.section0_filter`)
4. Projects to a slim field set (drops fields we don't need for ws2)
5. Writes filtered records to a per-shard Parquet on a Modal Volume
6. Returns metadata: {n_in, n_out, shard_path, updated_date}

Runs on Modal CPU containers (no GPU needed); preemptible by default.
Up to 3 retries on preemption with exponential backoff. Idempotent
on re-run (overwrites output).

Image: debian-slim + orjson + pyarrow + httpx + the local
whitespace2 package (for the §0 filter).

Usage:

  # Deploy:
  modal deploy experiments/phase-1.2/parse_modal.py

  # Single-shard smoke (Step 5):
  modal run experiments/phase-1.2/parse_modal.py::smoke_one_shard

See ``docs/phases/phase-1.2-plan.md`` for context.
"""

from __future__ import annotations

import gzip
import io
import time
from pathlib import PurePosixPath
from typing import Any

import modal

# ---------- App + image ----------

app = modal.App("ws2-parse")

parse_image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install(
        "orjson>=3.10",
        "pyarrow>=15",
        "httpx>=0.27",
        "numpy>=1.24,<2",
    )
    # add_local_python_source last per Modal best-practice
    .add_local_python_source("whitespace2")
)

# ---------- Volume ----------

# Volume holds per-shard Parquet outputs of the §0-filtered records.
# Shard naming: <updated_date>_<part_filename>.parquet, deterministic
# from the URL. Existence of the file = "this shard is done."
section0_volume = modal.Volume.from_name(
    "ws2-section0", create_if_missing=True,
)

# ---------- Field projection ----------

# Fields to KEEP from each OpenAlex Work record. Trims away open_access
# details, grants, abstract_inverted_index_v3, etc. — fields ws2 won't
# use. Keeps everything Phase 1.3 + Stage 2 will need.
_KEEP_FIELDS = (
    "id",
    "title",
    "publication_year",
    "publication_date",
    "type",
    "abstract_inverted_index",
    "authorships",
    "concepts",
    "cited_by_count",
    "referenced_works",
    "primary_location",
    "ids",
    "updated_date",
    "language",
)


def _project_fields(work: dict[str, Any]) -> dict[str, Any]:
    """Keep only the fields we'll need downstream."""
    return {k: work.get(k) for k in _KEEP_FIELDS}


# ---------- Shard URL → output filename ----------


def _shard_output_filename(shard_url: str) -> str:
    """Deterministic Parquet filename from a shard URL.

    e.g. s3://openalex/data/works/updated_date=2026-01-13/part_0042.gz
        →  '2026-01-13_part_0042.parquet'
    """
    # The URL ends with .../updated_date=YYYY-MM-DD/part_NNNN.gz
    parts = PurePosixPath(shard_url).parts
    date_part = next(
        (p for p in parts if p.startswith("updated_date=")), "unknown_date",
    )
    date_str = date_part.split("=", 1)[-1]
    fname_part = parts[-1]  # part_NNNN.gz
    fname_stem = fname_part.removesuffix(".gz")
    return f"{date_str}_{fname_stem}.parquet"


def _shard_url_to_https(shard_url: str) -> str:
    """Convert s3://openalex/... to https://openalex.s3.amazonaws.com/..."""
    if shard_url.startswith("s3://openalex/"):
        return shard_url.replace(
            "s3://openalex/",
            "https://openalex.s3.amazonaws.com/",
            1,
        )
    return shard_url


# ---------- Modal parse function ----------


@app.function(
    image=parse_image,
    cpu=4,
    memory=8192,
    volumes={"/output": section0_volume},
    timeout=1800,
    retries=modal.Retries(
        max_retries=3, initial_delay=10.0, max_delay=60.0,
    ),
)
def parse_one_shard(shard_url: str) -> dict[str, Any]:
    """Stream one OpenAlex shard, filter via §0, persist to Volume.

    Args:
        shard_url: ``s3://openalex/...`` shard URL from the manifest.

    Returns:
        dict with keys: ``shard_url``, ``output_path``, ``n_in``,
        ``n_out``, ``elapsed_sec``, ``updated_date``.

    Side effect: writes filtered records to
    ``/output/<date>_<part_NN>.parquet`` on the ``ws2-section0`` Volume.
    """
    import httpx
    import orjson
    import pyarrow as pa
    import pyarrow.parquet as pq

    from whitespace2.section0_filter import (
        has_abstract,
        passes_empty_abstract_filter,
        passes_junk_year_filter,
        passes_score_any_field,
    )

    https_url = _shard_url_to_https(shard_url)
    output_filename = _shard_output_filename(shard_url)
    output_path = f"/output/{output_filename}"

    # Extract updated_date from URL for metadata
    parts = PurePosixPath(shard_url).parts
    date_part = next(
        (p for p in parts if p.startswith("updated_date=")), "unknown_date",
    )
    updated_date = date_part.split("=", 1)[-1]

    t_start = time.time()
    n_in = 0
    n_out = 0
    kept_records: list[dict[str, Any]] = []

    # Stream + decompress + parse
    with httpx.stream("GET", https_url, timeout=300.0) as resp:
        resp.raise_for_status()
        # httpx.stream gives us iter_bytes; wrap in BytesIO + GzipFile.
        # We accumulate the response into memory because most shards
        # are <1.2 GB compressed — fits in 8 GB container memory.
        raw_bytes = b"".join(resp.iter_bytes(chunk_size=8 * 1024 * 1024))
    with gzip.open(io.BytesIO(raw_bytes), mode="rt", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                work = orjson.loads(line)
            except orjson.JSONDecodeError:
                continue  # skip malformed lines
            n_in += 1
            # Per-rule §0 filter (single-record path; gives per-record
            # accounting that the generator-style apply_section0_filter
            # doesn't expose).
            if not passes_score_any_field(work):
                continue
            if not has_abstract(work):
                continue
            if not passes_junk_year_filter(work):
                continue
            if not passes_empty_abstract_filter(work):
                continue
            kept_records.append(_project_fields(work))
            n_out += 1

    # Write Parquet
    if kept_records:
        # Serialize nested dict/list fields to JSON strings for pyarrow
        # (pyarrow can handle nested types but it's faster + smaller to
        # store complex nested as JSON strings; downstream re-parses
        # only when needed).
        rows: list[dict[str, Any]] = []
        for w in kept_records:
            row = {
                "id": w.get("id") or "",
                "title": w.get("title") or "",
                "publication_year": w.get("publication_year"),
                "publication_date": w.get("publication_date") or "",
                "type": w.get("type") or "",
                "cited_by_count": w.get("cited_by_count", 0),
                "language": w.get("language") or "",
                "updated_date": w.get("updated_date") or "",
                "abstract_inverted_index_json": orjson.dumps(
                    w.get("abstract_inverted_index") or {},
                ).decode("utf-8"),
                "authorships_json": orjson.dumps(
                    w.get("authorships") or [],
                ).decode("utf-8"),
                "concepts_json": orjson.dumps(
                    w.get("concepts") or [],
                ).decode("utf-8"),
                "referenced_works_json": orjson.dumps(
                    w.get("referenced_works") or [],
                ).decode("utf-8"),
                "primary_location_json": orjson.dumps(
                    w.get("primary_location") or {},
                ).decode("utf-8"),
                "ids_json": orjson.dumps(
                    w.get("ids") or {},
                ).decode("utf-8"),
            }
            rows.append(row)
        table = pa.Table.from_pylist(rows)
        pq.write_table(table, output_path, compression="zstd")
    else:
        # Write empty parquet with the expected schema so the
        # orchestrator's "shard done" check is unambiguous.
        empty_schema = pa.schema([
            ("id", pa.string()),
            ("title", pa.string()),
            ("publication_year", pa.int64()),
            ("publication_date", pa.string()),
            ("type", pa.string()),
            ("cited_by_count", pa.int64()),
            ("language", pa.string()),
            ("updated_date", pa.string()),
            ("abstract_inverted_index_json", pa.string()),
            ("authorships_json", pa.string()),
            ("concepts_json", pa.string()),
            ("referenced_works_json", pa.string()),
            ("primary_location_json", pa.string()),
            ("ids_json", pa.string()),
        ])
        empty_table = pa.Table.from_pylist([], schema=empty_schema)
        pq.write_table(empty_table, output_path, compression="zstd")

    # Commit volume changes (Modal Volumes have explicit commit semantics
    # for writes to be visible across containers).
    section0_volume.commit()

    elapsed = time.time() - t_start
    return {
        "shard_url": shard_url,
        "output_path": output_path,
        "n_in": n_in,
        "n_out": n_out,
        "elapsed_sec": elapsed,
        "updated_date": updated_date,
        "yield_pct": (n_out / n_in * 100.0) if n_in > 0 else 0.0,
    }


# ---------- Single-shard smoke (Step 5) ----------


@app.local_entrypoint()
def smoke_one_shard() -> None:
    """Phase 1.2 Step 5 — single-shard smoke on a known mid-size shard.

    Uses a 2026-01-13 shard (likely the bulk-update partition; ~915 MB
    compressed; ~330K records). Verifies the parse pipeline end-to-end
    on real data.

    Cost estimate: ~$0.10. Wall-clock: ~1-3 min on warm container.
    """
    test_url = (
        "s3://openalex/data/works/updated_date=2026-01-13/part_0001.gz"
    )
    print("Phase 1.2 Step 5 — single-shard smoke")
    print(f"  shard: {test_url}")
    print()

    result = parse_one_shard.remote(test_url)

    print(f"  n_in:        {result['n_in']:,}")
    print(f"  n_out:       {result['n_out']:,}")
    print(f"  yield:       {result['yield_pct']:.2f}%")
    print(f"  elapsed:     {result['elapsed_sec']:.1f}s")
    print(f"  output:      {result['output_path']}")
    print(f"  updated_date: {result['updated_date']}")
    print()

    # Sanity: yield should be in 1-30% range for §0 filter on
    # general OpenAlex (not specific to cs+physics — across all fields)
    if result["yield_pct"] < 0.5:
        print("  WARN: yield <0.5% — filter may be too strict, "
              "or this shard has unusual content")
    elif result["yield_pct"] > 50:
        print("  WARN: yield >50% — filter may be too loose, "
              "or this shard is heavily cs+physics-skewed")
    else:
        print("  PASS: yield in expected band")
