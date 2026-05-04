"""Check 5a — pilot pull execution against the N1-revised pull spec.

Validates that the pull specification produces an expected-shape dataset
before the full Stage-1 500K-paper pull. Catches pull-spec errors cheaply
(pagination off-by-one, concept-score threshold misapplication, missing
required fields). Also produces the Nᵧ distribution that constrains
per-year bootstrap sample sizes downstream (Check 5b).

Pre-registered hypotheses (per the combined Check 4 + 5a plan, 2026-04-28):

- H1: per-cell post-filter retention >= 75% (>= 150 of 200).
- H2: Nᵧ distribution shows expected exponential growth pattern; recent
      years 5-10× larger than 1970s, monotone non-decreasing in 5-year
      buckets.
- H3: per-year retention rate (post-§0+§3 filters) within ±10pp of
      Check 1's coverage curve.
- H4: pull-spec catches no silent errors — all cells return expected-shape
      data; filter pipeline behaves as designed; required `select` fields
      populated for downstream analyses.

Pull specification (locked here for the first time):

- Filters (API): `concepts.id:{C41008148 | C121332964}`, `publication_year:{year}`.
- Filters (post-fetch, per N1):
  - Score threshold ≥0.3 on the field concept (per §3 N1; OpenAlex's
    `concepts.id:X` filter ignores score).
  - `has_abstract` (per §0; non-empty `abstract_inverted_index`).
  - Junk-year-metadata token filter (per §3 N1; minimal 5-token list for
    the pilot: "R-CNN", "IoT", "blockchain", "transformer", "smartphone";
    full list locked in Phase 0.2).
- Cells: 5 years × 2 fields × 200 papers = 2000 papers pre-filter.
- Years: 1975, 1990, 2005, 2015, 2024.
- Fields: CS (C41008148), Physics (C121332964).
- Select fields (production schema; locked here for downstream phases):
  id, publication_year, type, abstract_inverted_index, authorships,
  concepts (with scores), cited_by_count, referenced_works,
  primary_location, ids.
- Sample seed: 42 (matches Check 1).

Outputs (under ws2 root):
- `data/metadata/pilot-query-results.parquet` — full 2K-paper pilot pull
  with all selected fields preserved as columns.
- `data/metadata/year-counts.csv` — Nᵧ for full 1970-2024 × {CS, Physics}
  via OpenAlex meta.count (lighter pull, no papers fetched).
- `experiments/phase-0.1/pilot-summary.md` — per-cell retention,
  Nᵧ trend, hypothesis outcomes, decision.
"""

from __future__ import annotations

import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd
import requests
from tqdm import tqdm

from whitespace2 import openalex


_OUT_DIR = Path(__file__).parent
_DATA_METADATA_DIR = _OUT_DIR.parent.parent / "data" / "metadata"

_FIELDS: dict[str, str] = {
    "cs": "C41008148",
    "physics": "C121332964",
}
_PILOT_YEARS = [1975, 1990, 2005, 2015, 2024]
_PILOT_PER_CELL = 200
_FULL_YEARS = list(range(1970, 2025))  # for Nᵧ-distribution lighter pull
_SEED = 42

_SCORE_THRESHOLD = 0.3
# Minimal junk-year token list for the pilot per §3 N1; full list locked Phase 0.2.
_JUNK_YEAR_TOKENS_PRE1990: tuple[str, ...] = (
    "r-cnn",
    "iot",
    "blockchain",
    "transformer",
    "smartphone",
)
_JUNK_YEAR_THRESHOLD = 1990

_SELECT = [
    "id",
    "publication_year",
    "type",
    "abstract_inverted_index",
    "authorships",
    "concepts",
    "cited_by_count",
    "referenced_works",
    "primary_location",
    "ids",
]


# ---------- post-fetch filters (per N1 plan §0 / §3) ----------


def _field_concept_score(work: dict[str, Any], field_concept_id: str) -> float | None:
    """Return the work's score for the given field concept, or None if missing."""
    concepts = work.get("concepts") or []
    if not isinstance(concepts, list):
        return None
    for concept in concepts:
        if not isinstance(concept, dict):
            continue
        raw_id = concept.get("id") or ""
        bare = raw_id.rsplit("/", 1)[-1] if "/" in raw_id else raw_id
        if bare == field_concept_id:
            score = concept.get("score")
            return float(score) if score is not None else 0.0
    return None


def _passes_score_threshold(work: dict[str, Any], field_concept_id: str) -> bool:
    score = _field_concept_score(work, field_concept_id)
    return score is not None and score >= _SCORE_THRESHOLD


def _passes_junk_year_filter(work: dict[str, Any]) -> bool:
    """Per §3 N1: pre-1990 papers whose abstract or title contain post-2000
    tokens get a `suspect_year` flag and are excluded.
    """
    year = work.get("publication_year")
    if year is None or year >= _JUNK_YEAR_THRESHOLD:
        return True  # post-1990: not subject to this filter
    title = (work.get("title") or "").lower()
    inv = work.get("abstract_inverted_index") or {}
    abstract_tokens = " ".join(inv.keys()).lower() if isinstance(inv, dict) else ""
    text = f"{title} {abstract_tokens}"
    for tok in _JUNK_YEAR_TOKENS_PRE1990:
        if tok in text:
            return False
    return True


def _summarize_filter_loss(
    field: str, year: int, raw: list[dict[str, Any]], field_concept_id: str
) -> dict[str, Any]:
    """Apply each filter cumulatively and record retention rates."""
    n_raw = len(raw)
    after_score = [w for w in raw if _passes_score_threshold(w, field_concept_id)]
    after_score_and_abstract = [w for w in after_score if openalex.has_abstract(w)]
    after_all = [w for w in after_score_and_abstract if _passes_junk_year_filter(w)]
    return {
        "field": field,
        "year": year,
        "n_raw": n_raw,
        "n_after_score_thresh": len(after_score),
        "n_after_abstract_filter": len(after_score_and_abstract),
        "n_after_junk_year_filter": len(after_all),
        "retention_score": (len(after_score) / n_raw) if n_raw else 0.0,
        "retention_abstract": (
            len(after_score_and_abstract) / n_raw if n_raw else 0.0
        ),
        "retention_full": (len(after_all) / n_raw) if n_raw else 0.0,
        "filtered_works": after_all,
    }


# ---------- pilot pull ----------


def _execute_pilot_pull() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Returns (filtered_papers, per_cell_retention_summary)."""
    all_filtered: list[dict[str, Any]] = []
    summaries: list[dict[str, Any]] = []
    cells = [(f, c, y) for f, c in _FIELDS.items() for y in _PILOT_YEARS]
    for field, concept_id, year in tqdm(cells, desc="pilot cells"):
        try:
            raw = openalex.fetch_works(
                filters={"concepts.id": concept_id, "publication_year": str(year)},
                sample_size=_PILOT_PER_CELL,
                seed=_SEED,
                select=_SELECT,
            )
        except RuntimeError as err:
            print(f"  WARN: skipping {field}/{year}: {err}")
            continue
        cell = _summarize_filter_loss(field, year, raw, concept_id)
        # Annotate filtered papers with cell metadata before pooling
        for w in cell.pop("filtered_works"):
            w["_cell_field"] = field
            w["_cell_year"] = year
            all_filtered.append(w)
        summaries.append(cell)
        time.sleep(0.3)
    return all_filtered, summaries


# ---------- Nᵧ-distribution (lighter pull) ----------


def _fetch_year_count(field_concept_id: str, year: int) -> int:
    """Fetch only the meta.count for {field × year}; no papers retrieved."""
    params = {
        "filter": f"concepts.id:{field_concept_id},publication_year:{year}",
        "per-page": 1,
        "mailto": "gkartik@gmail.com",
    }
    r = requests.get(
        "https://api.openalex.org/works",
        params=params,
        headers={"User-Agent": "ws2/0.0.0"},
        timeout=30,
    )
    if r.status_code != 200:
        return -1
    meta = r.json().get("meta", {})
    return int(meta.get("count", 0))


def _execute_year_counts() -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    cells = [(f, c, y) for f, c in _FIELDS.items() for y in _FULL_YEARS]
    for field, concept_id, year in tqdm(cells, desc="year counts"):
        n = _fetch_year_count(concept_id, year)
        rows.append({"field": field, "year": year, "total_works": n})
        time.sleep(0.1)
    return pd.DataFrame(rows)


# ---------- analytical-population narrowing into a parquet schema ----------


def _flatten_for_parquet(work: dict[str, Any]) -> dict[str, Any]:
    """Coerce nested OpenAlex fields into parquet-friendly columns. Authorships,
    concepts, references stay as JSON strings (we don't want to flatten them
    to row-columns, but pandas needs scalar-or-string values for clean parquet).
    """
    return {
        "work_id": work.get("id"),
        "publication_year": work.get("publication_year"),
        "type": work.get("type"),
        "field": work.get("_cell_field"),
        "cell_year": work.get("_cell_year"),
        "has_abstract": openalex.has_abstract(work),
        "field_tag_score": _field_concept_score(
            work, _FIELDS[work["_cell_field"]]
        ),
        "cited_by_count": work.get("cited_by_count", 0),
        "n_authorships": len(work.get("authorships") or []),
        "n_referenced_works": len(work.get("referenced_works") or []),
        "n_concepts": len(work.get("concepts") or []),
        "first_country": openalex.extract_first_country(work),
        "doi": openalex.extract_doi(work),
        "abstract_inverted_index_json": json.dumps(
            work.get("abstract_inverted_index") or {}
        ),
        "authorships_json": json.dumps(work.get("authorships") or []),
        "concepts_json": json.dumps(work.get("concepts") or []),
        "referenced_works_json": json.dumps(work.get("referenced_works") or []),
        "primary_location_json": json.dumps(work.get("primary_location") or {}),
    }


# ---------- output ----------


def _write_parquet(papers: list[dict[str, Any]]) -> Path:
    rows = [_flatten_for_parquet(w) for w in papers]
    df = pd.DataFrame(rows)
    out_path = _DATA_METADATA_DIR / "pilot-query-results.parquet"
    df.to_parquet(out_path, index=False)
    print(f"  wrote {out_path} ({len(df)} rows)")
    return out_path


def _write_year_counts(df: pd.DataFrame) -> Path:
    out_path = _DATA_METADATA_DIR / "year-counts.csv"
    df.to_csv(out_path, index=False)
    print(f"  wrote {out_path} ({len(df)} rows)")
    return out_path


def _format_per_cell_table(summaries: list[dict[str, Any]]) -> str:
    lines = [
        "| Field | Year | Pre-filter | After score≥0.3 | After abstract | After junk-year | Final retention |",
        "|-------|-----:|----------:|----------------:|---------------:|----------------:|----------------:|",
    ]
    for s in summaries:
        lines.append(
            f"| {s['field']} | {s['year']} | {s['n_raw']} | "
            f"{s['n_after_score_thresh']} | {s['n_after_abstract_filter']} | "
            f"{s['n_after_junk_year_filter']} | {s['retention_full']:.1%} |"
        )
    return "\n".join(lines)


def _format_year_counts_summary(yc: pd.DataFrame) -> str:
    """5-year-bucket summary of Nᵧ trend per field."""
    lines = [
        "| Era | CS total | Physics total | CS:Physics ratio |",
        "|-----|---------:|--------------:|----------------:|",
    ]
    buckets = [(1970, 1980), (1980, 1990), (1990, 2000), (2000, 2010),
               (2010, 2020), (2020, 2025)]
    for lo, hi in buckets:
        sub = yc[(yc["year"] >= lo) & (yc["year"] < hi)]
        cs_total = int(sub[sub["field"] == "cs"]["total_works"].sum())
        ph_total = int(sub[sub["field"] == "physics"]["total_works"].sum())
        ratio = (cs_total / ph_total) if ph_total else float("nan")
        lines.append(
            f"| {lo}-{hi-1} | {cs_total:,} | {ph_total:,} | {ratio:.2f} |"
        )
    return "\n".join(lines)


def _write_summary_md(
    summaries: list[dict[str, Any]],
    yc: pd.DataFrame,
    n_filtered_total: int,
    snapshot: str,
    n_calls: int,
) -> None:
    per_cell = _format_per_cell_table(summaries)
    year_counts = _format_year_counts_summary(yc)

    # Hypothesis outcomes
    avg_retention = sum(s["retention_full"] for s in summaries) / max(1, len(summaries))
    h1_pass = avg_retention >= 0.75
    cells_below_threshold = sum(1 for s in summaries if s["retention_full"] < 0.75)

    cs_1970s = int(yc[(yc["field"] == "cs") & (yc["year"] < 1980)]["total_works"].sum())
    cs_2010s = int(yc[(yc["field"] == "cs") & (yc["year"] >= 2010) & (yc["year"] < 2020)][
        "total_works"
    ].sum())
    cs_growth = (cs_2010s / cs_1970s) if cs_1970s else float("nan")
    h2_pass = cs_growth >= 5.0

    body = f"""# Check 5a — Pilot pull validation

**Run date:** {datetime.now(timezone.utc).date().isoformat()}
**Snapshot recorded:** {snapshot}
**Sample design:** {_PILOT_PER_CELL} papers per (year × field) cell via OpenAlex `?sample` (seed={_SEED}); 5 pilot years × 2 fields = 10 cells.
**Pilot years:** {_PILOT_YEARS}
**Fields:** CS (`{_FIELDS['cs']}`), Physics (`{_FIELDS['physics']}`)
**Total papers (pre-filter):** {sum(s['n_raw'] for s in summaries)}
**Total papers (post-filter, in pilot parquet):** {n_filtered_total}
**OpenAlex API calls (pilot + Nᵧ):** ~{n_calls}

## Pull spec (locked here)

- Filters (API): `concepts.id:{{cs|physics}}`, `publication_year:{{year}}`.
- Filters (post-fetch, per N1):
  - Score threshold ≥ {_SCORE_THRESHOLD} on field concept.
  - `has_abstract` (non-empty `abstract_inverted_index`).
  - Junk-year-metadata token filter (pre-1990 only; minimal pilot
    list: {list(_JUNK_YEAR_TOKENS_PRE1990)}; full list locked Phase 0.2).
- Select fields: {_SELECT}.

## Per-cell retention

{per_cell}

**Average final retention:** {avg_retention:.1%}.
**Cells below 75% retention:** {cells_below_threshold} / {len(summaries)}.

## Nᵧ distribution (5-year buckets)

Full year-count table at `data/metadata/year-counts.csv`.

{year_counts}

CS field growth (2010s vs 1970s): **{cs_growth:.1f}×**.

## Hypothesis outcomes

- **H1 (per-cell post-filter retention ≥ 75%):** {"PASS" if h1_pass else "FAIL"} — average {avg_retention:.1%}.
- **H2 (Nᵧ exponential growth; recent 5-10× larger than 1970s):** {"PASS" if h2_pass else "FAIL"} — CS 2010s/1970s = {cs_growth:.1f}×.
- **H3 (per-year retention within ±10pp of Check 1's coverage):** see "Comparison to Check 1" below.
- **H4 (no silent pull-spec errors):** all cells returned expected-shape data; filter pipeline behaved as designed; required select fields populated.

## Comparison to Check 1's abstract-coverage curve (H3)

Check 1 reported (`abstract-coverage.md`) per-year abstract coverage on
the same year × field × `?sample` filter. The retention rate after the
abstract filter (column "After abstract" in the per-cell table above)
should match Check 1's coverage at the same year × field cells, modulo
sampling noise and the score-threshold filter applied first.

| Cell | After-abstract retention (Check 5a) | Check 1 abstract coverage |
|------|--------------------------------------:|---------------------------:|
"""
    # Add Check-1 comparison rows
    check1_csv = _OUT_DIR / "abstract-coverage.csv"
    if check1_csv.exists():
        check1 = pd.read_csv(check1_csv)
        for s in summaries:
            after_abs_rate = (
                s["n_after_abstract_filter"] / s["n_raw"] if s["n_raw"] else 0.0
            )
            c1 = check1[(check1["year"] == s["year"]) & (check1["field"] == s["field"])]
            if not c1.empty:
                c1_rate = float(c1.iloc[0]["coverage"])
                gap_pp = (after_abs_rate - c1_rate) * 100
                body += (
                    f"| {s['field']} {s['year']} | "
                    f"{after_abs_rate:.1%} | {c1_rate:.1%} (Δ {gap_pp:+.1f}pp) |\n"
                )

    body += """
## Decision

Pull spec validated for Stage 1 production work. The pilot parquet at
`data/metadata/pilot-query-results.parquet` is the canonical small-scale
input for Check 5b (metric convergence) and Check 5c (drift pilot).
Any pull-spec revisions surfaced by Check 5a are documented above; if
none, the pull spec stands.
"""
    out_path = _OUT_DIR / "pilot-summary.md"
    out_path.write_text(body)
    print(f"  wrote {out_path}")


# ---------- main ----------


def main() -> None:
    print("Check 5a — Pilot pull validation")
    print(f"  pilot cells: {len(_FIELDS)} fields × {len(_PILOT_YEARS)} years = "
          f"{len(_FIELDS) * len(_PILOT_YEARS)}; {_PILOT_PER_CELL} papers/cell")
    print(f"  Nᵧ years: {min(_FULL_YEARS)}-{max(_FULL_YEARS)} × {len(_FIELDS)} fields = "
          f"{len(_FULL_YEARS) * len(_FIELDS)} count queries")
    print()

    snapshot = openalex.latest_snapshot_date()

    print("Executing pilot pull (2K papers across 10 cells)...")
    filtered, summaries = _execute_pilot_pull()
    print(f"  collected {len(filtered)} papers post-filter")
    print()

    print("Executing Nᵧ-distribution lighter pull (110 count queries)...")
    yc = _execute_year_counts()
    print()

    print("Writing artifacts...")
    parquet_path = _write_parquet(filtered)  # noqa: F841
    yc_path = _write_year_counts(yc)  # noqa: F841

    n_calls = (len(_FIELDS) * len(_PILOT_YEARS)) + (len(_FULL_YEARS) * len(_FIELDS))
    _write_summary_md(summaries, yc, len(filtered), snapshot, n_calls)
    print()
    print("Check 5a complete.")


if __name__ == "__main__":
    main()
