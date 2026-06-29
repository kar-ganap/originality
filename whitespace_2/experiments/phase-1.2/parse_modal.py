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
        # DuckDB for cross-shard dedup with disk spill (polars sort
        # can't stream; OOMs on ~64 GB compressed corpus even with
        # 32 GB memory). DuckDB's window functions spill to disk
        # automatically when memory runs short.
        "duckdb>=1.0",
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


# ---------- Cross-shard dedup (Phase 1.2 Step 7 follow-on) ----------


@app.function(
    image=parse_image,
    cpu=8,
    memory=65536,  # 64 GB; first pass uses tiny memory, second pass
                   # uses hash-join with small winners table in memory.
                   # The previous attempt used a full window function
                   # over ~64 GB compressed parquet which OOMed even
                   # with disk spill (working set ~250 GB decompressed).
    ephemeral_disk=524_288,  # 512 GB ephemeral; DuckDB spill files go here
    volumes={"/output": section0_volume},
    timeout=7200,
)
def dedup_to_population() -> dict[str, Any]:
    """Concat all shard parquets + dedup by paper-id (max updated_date wins).

    OpenAlex's incremental snapshot model means a paper updated
    multiple times appears in multiple ``updated_date=YYYY-MM-DD/``
    partitions. The "current corpus" is built by taking the latest
    record per paper-id across all partitions.

    Two-pass approach (after first attempt with single window-function
    OOMed despite 64 GB + disk spill):

    1. **Pass 1** — small projection: scan ALL shards, GROUP BY id,
       MAX(updated_date). Result: ~10-15M (id, max_date) pairs ≈
       ~500 MB. Fits comfortably in memory.
    2. **Pass 2** — hash-join: scan ALL shards again, INNER JOIN
       with winners table on (id, updated_date). The small winners
       table goes into a hash table in memory; the big shard scan
       streams through, looking up matches. Output streams to parquet.

    Both passes are bounded; no operation needs to materialize the
    full corpus in memory.

    Output: ``/output/section0-population.parquet`` on the Volume.
    """
    import glob
    import time

    import duckdb

    t_start = time.time()

    shard_pattern = "/output/*_part_*.parquet"
    shard_files = sorted(glob.glob(shard_pattern))
    print(f"  found {len(shard_files)} shard parquets to dedup")

    if not shard_files:
        return {
            "error": "no shard parquets found at /output",
            "elapsed_sec": time.time() - t_start,
        }

    output_path = "/output/section0-population.parquet"

    con = duckdb.connect()
    con.execute("PRAGMA memory_limit='48GB'")
    con.execute("PRAGMA threads=8")
    con.execute("PRAGMA temp_directory='/tmp/duckdb-spill'")

    # ---------- Pass 1: build winners table ----------
    print("  Pass 1: GROUP BY id MAX(updated_date) (small projection)")
    t_pass1 = time.time()
    con.execute(f"""
        CREATE TEMP TABLE winners AS
        SELECT id, MAX(updated_date) AS max_updated_date
        FROM read_parquet('{shard_pattern}')
        WHERE id IS NOT NULL AND id != ''
        GROUP BY id;
    """)
    n_winners = con.execute(
        "SELECT COUNT(*) FROM winners",
    ).fetchone()[0]
    print(f"    found {n_winners:,} unique paper-ids "
          f"({time.time() - t_pass1:.0f}s)")

    # ---------- Pass 2: hash-join + write ----------
    print("  Pass 2: hash-join shards × winners; write parquet")
    t_pass2 = time.time()
    # If multiple shards have a paper at the same updated_date,
    # we still need to deduplicate down to one. Use ROW_NUMBER() on the
    # join result restricted to winning (id, date) pairs — small after
    # the join filter so this is cheap.
    con.execute(f"""
        COPY (
            SELECT * EXCLUDE (rn) FROM (
                SELECT s.*,
                       ROW_NUMBER() OVER (PARTITION BY s.id) AS rn
                FROM read_parquet('{shard_pattern}') s
                INNER JOIN winners w
                    ON s.id = w.id
                    AND s.updated_date = w.max_updated_date
            ) WHERE rn = 1
        ) TO '{output_path}' (FORMAT PARQUET, COMPRESSION 'zstd');
    """)
    print(f"    wrote {output_path} ({time.time() - t_pass2:.0f}s)")

    # Count rows in the output
    n_records = con.execute(
        f"SELECT COUNT(*) FROM read_parquet('{output_path}')",
    ).fetchone()[0]
    con.close()

    section0_volume.commit()
    elapsed = time.time() - t_start
    return {
        "n_records": int(n_records),
        "n_winners": int(n_winners),
        "n_shards_concat": len(shard_files),
        "output": output_path,
        "elapsed_sec": elapsed,
    }


# ---------- §0 type allow-list amendment (Phase 1.2 retro) ----------


@app.function(
    image=parse_image,
    cpu=8,
    memory=32768,
    ephemeral_disk=524_288,
    volumes={"/output": section0_volume},
    timeout=3600,
)
def filter_population_by_type() -> dict[str, Any]:
    """Apply the §0 type allow-list amendment to the v1 population,
    producing ``section0-population-v2.parquet`` on the Volume.

    Source: ``/output/section0-population.parquet`` (v1; un-type-
    filtered, 72.17M rows).
    Output: ``/output/section0-population-v2.parquet`` (allowed types
    only; expected ~36-37M rows based on the 1M sample's type
    distribution).

    Allow-list (mirrors ``ALLOWED_WORK_TYPES`` in
    ``whitespace2.section0_filter``): article, preprint, review,
    book-chapter, dissertation, book, letter, editorial, report.
    Anything else (dataset, paratext, libguides, peer-review, erratum,
    retraction, reference-entry, supplementary-materials, grant,
    software, standard, other, NULL) is dropped.

    No re-parse required — ``type`` is already a column in the v1
    population parquet.
    """
    import time

    import duckdb

    # Mirror ALLOWED_WORK_TYPES; can't import the constant because the
    # remote container doesn't have whitespace2 on its sys.path until
    # add_local_python_source completes the build, but we want the
    # allow-list inline for SQL-readability anyway.
    allowed_types = (
        "article", "preprint", "review", "book-chapter", "dissertation",
        "book", "letter", "editorial", "report",
    )

    src_path = "/output/section0-population.parquet"
    dst_path = "/output/section0-population-v2.parquet"

    t_start = time.time()
    con = duckdb.connect()
    con.execute("PRAGMA memory_limit='28GB'")
    con.execute("PRAGMA threads=8")
    con.execute("PRAGMA temp_directory='/tmp/duckdb-spill'")
    con.execute("PRAGMA preserve_insertion_order=false")

    n_v1 = con.execute(
        f"SELECT COUNT(*) FROM read_parquet('{src_path}')",
    ).fetchone()[0]
    print(f"  v1 population: {n_v1:,} records")

    # Per-type counts pre-filter (informational)
    print("  v1 type distribution:")
    type_dist = con.execute(f"""
        SELECT type, COUNT(*) AS n
        FROM read_parquet('{src_path}')
        GROUP BY type ORDER BY n DESC
    """).fetchall()
    for t, n in type_dist:
        kept = "KEEP" if t in allowed_types else "DROP"
        print(f"    {kept} {t!s:<25} {n:>10,}")

    allowed_quoted = ", ".join(f"'{t}'" for t in allowed_types)
    print(f"  filtering to allow-list: {allowed_types}")
    con.execute(f"""
        COPY (
            SELECT *
            FROM read_parquet('{src_path}')
            WHERE type IN ({allowed_quoted})
        ) TO '{dst_path}' (FORMAT PARQUET, COMPRESSION 'zstd');
    """)

    n_v2 = con.execute(
        f"SELECT COUNT(*) FROM read_parquet('{dst_path}')",
    ).fetchone()[0]
    con.close()

    section0_volume.commit()
    elapsed = time.time() - t_start
    return {
        "n_v1": int(n_v1),
        "n_v2": int(n_v2),
        "kept_fraction": n_v2 / n_v1 if n_v1 else 0.0,
        "allowed_types": list(allowed_types),
        "type_distribution_v1": [(t, int(n)) for t, n in type_dist],
        "v1_path": src_path,
        "v2_path": dst_path,
        "elapsed_sec": elapsed,
    }


# ---------- §0 v3 amendments (Phase 1.2 H2 audit retro) ----------


@app.function(
    image=parse_image,
    cpu=8,
    memory=32768,
    ephemeral_disk=524_288,
    volumes={"/output": section0_volume},
    timeout=3600,
)
def filter_population_v3() -> dict[str, Any]:
    """Apply §0 v3 amendments to the v2 population.

    v3 = v2 with:
      1. Concept-score threshold 0.30 → 0.40
      2. Abstract-token minimum 15 → 50
      3. Abstract-prefix blacklist (publisher chrome)
      4. Title-prefix blacklist (non-paper artifacts)

    Locked patterns mirror ``whitespace2.section0_filter`` (see that
    module for rationale). Reproduced here inline because the SQL
    UDFs need them in-scope on the remote container.

    Source: ``/output/section0-population-v2.parquet`` (38.7M rows
    after the v2 type allow-list amendment).
    Output: ``/output/section0-population-v3.parquet``.

    Expected v3 size: ~30-32M rows (audit projected ~25-50% drop on
    top of v2, mostly publisher-chrome ACS papers + weak-CS-score
    papers).

    Also computes per-stage independent drop counts as an
    informational audit trail in the return dict.
    """
    import re
    import time

    import duckdb
    import orjson

    # Mirror section0_filter v3 constants. Keep in sync.
    score_threshold_v3 = 0.40
    min_tokens_v3 = 50
    cs_id = "https://openalex.org/C41008148"
    physics_id = "https://openalex.org/C121332964"
    prefix_lookahead = 20

    abs_prefix_re = re.compile(
        r"^("
        r"(?:ADVERTISEMENT\s+)?RETURN TO ISSUE"
        r"|Views Icon Views"
        r"|Article Metrics"
        r"|This is the author'?s version"
        r")",
        re.IGNORECASE,
    )
    title_prefix_re = re.compile(
        r"^("
        r"NEW PRODUCTS\b"
        r"|Contributors(?:\s*$|\s*[:,;.]|\s+\d)"
        r"|Annex\s+\d+"
        r"|Key Messages\b"
        r"|Editorial Board\b"
        r")",
        re.IGNORECASE,
    )

    def _reconstruct_prefix(json_str: str | None) -> str:
        if not json_str:
            return ""
        try:
            inv = orjson.loads(json_str)
        except Exception:
            return ""
        if not isinstance(inv, dict):
            return ""
        pos_to_word: dict[int, str] = {}
        for word, positions in inv.items():
            if not isinstance(positions, list):
                continue
            for p in positions:
                if isinstance(p, int) and 0 <= p < prefix_lookahead:
                    pos_to_word[p] = word
        if not pos_to_word:
            return ""
        max_pos = max(pos_to_word.keys())
        return " ".join(
            pos_to_word.get(i, "") for i in range(max_pos + 1)
        ).strip()

    def passes_abs_prefix(json_str: str | None) -> bool:
        prefix = _reconstruct_prefix(json_str)
        if not prefix:
            return True
        return abs_prefix_re.match(prefix) is None

    def passes_title_prefix(title: str | None) -> bool:
        if not isinstance(title, str):
            return True
        return title_prefix_re.match(title) is None

    def count_tokens(json_str: str | None) -> int:
        if not json_str:
            return 0
        try:
            inv = orjson.loads(json_str)
        except Exception:
            return 0
        if not isinstance(inv, dict):
            return 0
        return sum(
            len(ps) for ps in inv.values() if isinstance(ps, list)
        )

    src = "/output/section0-population-v2.parquet"
    dst = "/output/section0-population-v3.parquet"

    con = duckdb.connect()
    con.execute("PRAGMA memory_limit='28GB'")
    con.execute("PRAGMA threads=8")
    con.execute("PRAGMA temp_directory='/tmp/duckdb-spill'")
    con.execute("PRAGMA preserve_insertion_order=false")

    # Register UDFs. Explicit types so DuckDB vectorizes without
    # falling back to per-row Python introspection.
    con.create_function(
        "passes_abs_prefix", passes_abs_prefix,
        [duckdb.typing.VARCHAR], duckdb.typing.BOOLEAN,
    )
    con.create_function(
        "passes_title_prefix", passes_title_prefix,
        [duckdb.typing.VARCHAR], duckdb.typing.BOOLEAN,
    )
    con.create_function(
        "count_tokens", count_tokens,
        [duckdb.typing.VARCHAR], duckdb.typing.INTEGER,
    )

    n_v2 = con.execute(
        f"SELECT COUNT(*) FROM read_parquet('{src}')",
    ).fetchone()[0]
    print(f"  v2 population: {n_v2:,} records")

    t_start = time.time()

    # Single-pass v3 filter. The SQL is the canonical v3 spec; keep
    # in sync with ``whitespace2.section0_filter.apply_section0_filter_v3``.
    filter_sql = f"""
        len(list_filter(
            from_json(concepts_json,
                      '[{{"id": "VARCHAR", "score": "DOUBLE"}}]'),
            c -> (c.id = '{cs_id}' OR c.id = '{physics_id}')
                 AND c.score >= {score_threshold_v3}
        )) > 0
        AND count_tokens(abstract_inverted_index_json) >= {min_tokens_v3}
        AND passes_abs_prefix(abstract_inverted_index_json)
        AND passes_title_prefix(title)
    """

    con.execute(f"""
        COPY (
            SELECT *
            FROM read_parquet('{src}')
            WHERE {filter_sql}
        ) TO '{dst}' (FORMAT PARQUET, COMPRESSION 'zstd');
    """)

    n_v3 = con.execute(
        f"SELECT COUNT(*) FROM read_parquet('{dst}')",
    ).fetchone()[0]
    print(f"  v3 population: {n_v3:,} records "
          f"({100 * n_v3 / n_v2:.2f}% kept)")

    # Per-stage independent drop accounting. Each stage's "passes"
    # count is over the full v2 population (NOT cascaded). Useful
    # for identifying which stage carries which patterns; the
    # numbers don't sum because of overlap.
    print("  per-stage drop accounting (independent of cascade):")
    stage_specs = [
        ("score_ge_0.40", f"""
            len(list_filter(
                from_json(concepts_json,
                          '[{{"id": "VARCHAR", "score": "DOUBLE"}}]'),
                c -> (c.id = '{cs_id}' OR c.id = '{physics_id}')
                     AND c.score >= {score_threshold_v3}
            )) > 0
        """),
        ("tokens_ge_50",
         f"count_tokens(abstract_inverted_index_json) >= {min_tokens_v3}"),
        ("abstract_prefix_ok",
         "passes_abs_prefix(abstract_inverted_index_json)"),
        ("title_prefix_ok", "passes_title_prefix(title)"),
    ]
    stage_drops: dict[str, dict[str, int]] = {}
    for label, predicate in stage_specs:
        n_pass = con.execute(f"""
            SELECT COUNT(*) FROM read_parquet('{src}') WHERE {predicate}
        """).fetchone()[0]
        n_drop = n_v2 - n_pass
        stage_drops[label] = {"n_passes": int(n_pass), "n_drops": int(n_drop)}
        print(f"    {label:<22} passes {n_pass:>10,}  "
              f"drops {n_drop:>10,} ({100 * n_drop / n_v2:.2f}%)")

    con.close()
    section0_volume.commit()
    elapsed = time.time() - t_start

    return {
        "n_v2": int(n_v2),
        "n_v3": int(n_v3),
        "kept_fraction": n_v3 / n_v2 if n_v2 else 0.0,
        "v2_path": src,
        "v3_path": dst,
        "score_threshold_v3": score_threshold_v3,
        "min_tokens_v3": min_tokens_v3,
        "stage_drops_independent": stage_drops,
        "elapsed_sec": elapsed,
    }


# ---------- Server-side sampling (Step 8) ----------


@app.function(
    image=parse_image,
    cpu=8,
    memory=32768,  # 32 GB
    ephemeral_disk=524_288,  # 512 GB (Modal minimum); for spill
    volumes={"/output": section0_volume},
    timeout=3600,
)
def sample_population(
    n: int,
    population_filename: str = "section0-population.parquet",
    output_suffix: str = "",
) -> dict[str, Any]:
    """Sample N rows from a population parquet using deterministic
    nested-sampling order (sort by hash(seed|id), take first N).

    Nested property: sample(M) ⊂ sample(N) for any M ≤ N drawn with the
    same seed AND the same population. Lets Stage 2 escalate from 1M to
    2M without re-embedding.

    Server-side sampling avoids downloading the ~50 GB population
    parquet locally; only the small sample (~800 MB for N=1M) is
    downloaded.

    Implementation: 2-pass to keep working set small.
    - Pass 1: hash-rank just (id, hash) over the population, take top N.
      ~72M × ~70B ≈ 5 GB working set; fits comfortably.
    - Pass 2: hash-join the N selected ids back to the population for
      full rows; write to Parquet.

    The single-pass ``ORDER BY hash`` over the full row including
    abstracts OOMs at ~12 GB on a 32 GB box (DuckDB materializes the
    full row width during the sort).

    Args:
        n: sample size.
        population_filename: which parquet on the Volume to sample from.
            Defaults to v1 ``section0-population.parquet``; pass
            ``section0-population-v2.parquet`` for the type-filtered v2.
        output_suffix: appended to the sample filename (before
            ``.parquet``). E.g., ``"-v2"`` produces
            ``section0-sample-<N_LABEL>-v2.parquet``.

    Output filename: ``section0-sample-<N_LABEL><output_suffix>.parquet``.
    """
    import time

    import duckdb

    nesting_seed = "ws2-phase-1.2-nesting-seed-v1"
    population_path = f"/output/{population_filename}"

    # Format N label
    if n >= 1_000_000 and n % 1_000_000 == 0:
        n_label = f"{n // 1_000_000}M"
    elif n >= 1_000_000:
        # 1.5M → "1_5M"
        n_label = f"{n / 1_000_000:.1f}M".replace(".", "_")
    elif n >= 1_000 and n % 1_000 == 0:
        n_label = f"{n // 1_000}K"
    else:
        n_label = str(n)

    output_path = f"/output/section0-sample-{n_label}{output_suffix}.parquet"

    t_start = time.time()
    con = duckdb.connect()
    con.execute("PRAGMA memory_limit='28GB'")
    con.execute("PRAGMA threads=8")
    con.execute("PRAGMA temp_directory='/tmp/duckdb-spill'")
    con.execute("PRAGMA preserve_insertion_order=false")

    # Population size (sanity check)
    n_population = con.execute(
        f"SELECT COUNT(*) FROM read_parquet('{population_path}')",
    ).fetchone()[0]
    print(f"  population: {n_population:,} records")
    if n > n_population:
        print(f"  WARN: requested N={n:,} > population {n_population:,}; "
              "capping at population size")

    # Pass 1: rank by hash over (id, hash) only — small projection.
    print(f"  pass 1: hash-ranking {n_population:,} ids, taking top {n:,}...")
    t_p1 = time.time()
    con.execute(f"""
        CREATE TEMP TABLE selected_ids AS
        SELECT id
        FROM read_parquet('{population_path}')
        ORDER BY hash('{nesting_seed}' || id)
        LIMIT {n};
    """)
    n_selected = con.execute("SELECT COUNT(*) FROM selected_ids").fetchone()[0]
    print(f"    pass 1: {n_selected:,} ids selected in {time.time()-t_p1:.0f}s")

    # Pass 2: hash-join back to full population, write Parquet.
    print(f"  pass 2: joining {n_selected:,} ids to population, writing parquet...")
    t_p2 = time.time()
    con.execute(f"""
        COPY (
            SELECT p.*
            FROM read_parquet('{population_path}') p
            INNER JOIN selected_ids s ON p.id = s.id
        ) TO '{output_path}' (FORMAT PARQUET, COMPRESSION 'zstd');
    """)
    print(f"    pass 2: written in {time.time()-t_p2:.0f}s")

    n_records = con.execute(
        f"SELECT COUNT(*) FROM read_parquet('{output_path}')",
    ).fetchone()[0]
    con.close()

    section0_volume.commit()
    elapsed = time.time() - t_start
    return {
        "n_target": n,
        "n_actual": int(n_records),
        "n_label": n_label,
        "n_population": int(n_population),
        "output": output_path,
        "nesting_seed": nesting_seed,
        "elapsed_sec": elapsed,
    }


# ---------- Dedup correctness spot-check (retro pressure-point D) ----------


@app.function(
    image=parse_image,
    cpu=4,
    memory=16384,
    volumes={"/output": section0_volume},
    timeout=900,
)
def dedup_spot_check(ids: list[str]) -> dict[str, Any]:
    """For a small set of paper ids, return where they appear across the
    per-shard parquets vs the deduplicated population. Used to verify
    the cross-shard dedup is collapsing to max(updated_date) correctly.

    Returns:
      ``shard_appearances``: list of (id, filename, updated_date) — every
        per-shard row matching the ids.
      ``population``: list of (id, updated_date) — the post-dedup row for
        each id.

    The local caller cross-checks: for each id, population.updated_date
    must equal max(shard.updated_date) for that id.
    """
    import duckdb

    con = duckdb.connect()
    con.execute("PRAGMA memory_limit='12GB'")
    con.execute("PRAGMA threads=4")
    con.execute("PRAGMA temp_directory='/tmp/duckdb-spill'")

    ids_str = ", ".join(f"'{i}'" for i in ids)

    print(f"  scanning shards for {len(ids)} ids...")
    shard_rows = con.execute(f"""
        SELECT id, filename, updated_date
        FROM read_parquet('/output/*_part_*.parquet', filename=true)
        WHERE id IN ({ids_str})
        ORDER BY id, updated_date
    """).fetchall()
    print(f"    {len(shard_rows)} shard appearances total")

    print("  scanning population for the same ids...")
    pop_rows = con.execute(f"""
        SELECT id, updated_date
        FROM read_parquet('/output/section0-population.parquet')
        WHERE id IN ({ids_str})
        ORDER BY id
    """).fetchall()
    print(f"    {len(pop_rows)} population rows")

    con.close()
    return {
        "shard_appearances": [
            {
                "id": r[0],
                "filename": str(r[1]).split("/")[-1] if r[1] else None,
                "updated_date": r[2],
            }
            for r in shard_rows
        ],
        "population": [
            {"id": r[0], "updated_date": r[1]} for r in pop_rows
        ],
    }


# ---------- Held-out generation (Step 9) ----------


@app.function(
    image=parse_image,
    cpu=8,
    memory=32768,  # 32 GB
    ephemeral_disk=524_288,
    volumes={"/output": section0_volume},
    timeout=3600,
)
def generate_heldouts(
    sample_filename: str,
    n_per: int,
    population_filename: str = "section0-population.parquet",
    output_suffix: str = "",
) -> dict[str, Any]:
    """Generate held-out sets for Stage 2 §11 cluster-fit + drift studies.

    Produces 4 held-out Parquet files:
        heldout-1975-cs<suffix>.parquet
        heldout-1975-physics<suffix>.parquet
        heldout-2020-cs<suffix>.parquet
        heldout-2020-physics<suffix>.parquet

    Each contains ``n_per`` papers (typically 500). Each is disjoint
    from the sample (anti-joined on ``id``) and disjoint from the
    other held-outs (different year × field cells; rare cross-field
    overlap is allowed since cs+physics cross-disciplinary papers
    can legitimately appear in both).

    Field detection: ``concepts_json`` contains an array of concept
    objects ``{id, score, ...}``; a paper is "cs" if any element has
    ``id = "https://openalex.org/C41008148"`` AND ``score >= 0.30``.
    Same threshold for "physics" with ``C121332964``. Mirrors §0.

    Hash-ranking: sort by ``hash(HELDOUT_SEED || id)`` — different
    seed than the sample's nesting hash so held-outs aren't
    correlated with sample membership beyond the disjointness
    constraint.

    Args:
        sample_filename: which sample parquet to anti-join against.
        n_per: papers per cell.
        population_filename: which population parquet to draw from.
            Defaults to v1; pass ``section0-population-v2.parquet``
            for the type-filtered v2.
        output_suffix: appended to each held-out filename before
            ``.parquet`` (e.g., ``"-v2"``).
    """
    import time

    import duckdb

    HELDOUT_SEED = "ws2-phase-1.2-heldout-seed-v1"
    population_path = f"/output/{population_filename}"
    sample_path = f"/output/{sample_filename}"

    cell_specs = [
        (1975, "cs", "https://openalex.org/C41008148"),
        (1975, "physics", "https://openalex.org/C121332964"),
        (2020, "cs", "https://openalex.org/C41008148"),
        (2020, "physics", "https://openalex.org/C121332964"),
    ]

    t_total = time.time()
    con = duckdb.connect()
    con.execute("PRAGMA memory_limit='28GB'")
    con.execute("PRAGMA threads=8")
    con.execute("PRAGMA temp_directory='/tmp/duckdb-spill'")
    con.execute("PRAGMA preserve_insertion_order=false")

    # Cache the sample IDs for anti-join
    print("  loading sample ids for anti-join...")
    con.execute(f"""
        CREATE TEMP TABLE sample_ids AS
        SELECT id FROM read_parquet('{sample_path}');
    """)
    n_sample = con.execute("SELECT COUNT(*) FROM sample_ids").fetchone()[0]
    print(f"    {n_sample:,} sample ids loaded")

    cell_results: list[dict[str, Any]] = []
    for year, field, concept_id in cell_specs:
        t_cell = time.time()
        out_filename = f"heldout-{year}-{field}{output_suffix}.parquet"
        out_path = f"/output/{out_filename}"
        print(f"  cell {year}-{field}: filtering + ranking + writing...")

        # Single-CTE: year filter + strict JSON field check + anti-join +
        # hash-rank. JSON parse is only on year-filtered subset (cheap).
        con.execute(f"""
            COPY (
                SELECT p.*
                FROM read_parquet('{population_path}') p
                WHERE p.publication_year = {year}
                  AND NOT EXISTS (
                      SELECT 1 FROM sample_ids s WHERE s.id = p.id
                  )
                  AND len(list_filter(
                      from_json(
                          p.concepts_json,
                          '[{{"id": "VARCHAR", "score": "DOUBLE"}}]'
                      ),
                      c -> c.id = '{concept_id}' AND c.score >= 0.30
                  )) > 0
                ORDER BY hash('{HELDOUT_SEED}' || p.id)
                LIMIT {n_per}
            ) TO '{out_path}' (FORMAT PARQUET, COMPRESSION 'zstd');
        """)
        n_records = con.execute(
            f"SELECT COUNT(*) FROM read_parquet('{out_path}')",
        ).fetchone()[0]
        cell_elapsed = time.time() - t_cell
        cell_results.append({
            "year": year,
            "field": field,
            "concept_id": concept_id,
            "n_target": n_per,
            "n_actual": int(n_records),
            "filename": out_filename,
            "output": out_path,
            "elapsed_sec": cell_elapsed,
        })
        print(f"    {n_records}/{n_per} written in {cell_elapsed:.0f}s")

    con.close()
    section0_volume.commit()

    return {
        "n_per_target": n_per,
        "heldout_seed": HELDOUT_SEED,
        "sample_filename": sample_filename,
        "n_sample_excluded": int(n_sample),
        "population_path": population_path,
        "cells": cell_results,
        "elapsed_sec": time.time() - t_total,
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
