"""Check 4 — OpenAlex disambiguation spot-check.

Plan §10 commits to OpenAlex's published 90-95% author-disambiguation
accuracy as the working assumption. Check 4 confirms or flags deviation
on ws2's specific corpus by spot-checking implausible career lengths.

Pre-registered hypotheses (per the combined Check 4 + 5a plan, 2026-04-28):

- H1: implausible-career-length rate (>60 yr between first and latest pub)
      is in the range [5%, 15%] of frequency-weighted-sampled authors.
- H2: of flagged-implausible cases, ≥50% are genuine disambiguation errors
      upon manual inspection.
- H3: implied disambiguation-error upper bound = (flag_rate × validation_rate)
      is consistent with OpenAlex's published 5-10% error band.

Two-pass workflow:

- Pass A (this script): sample 200 unique authors frequency-weighted from
  `missingness-bias-raw.parquet`, fetch each `/authors/A{id}` record, compute
  career_length = latest_pub_year − first_pub_year, flag career_length > 60,
  also pull metadata that supports manual classification (name variants,
  affiliation history, top topics, year-by-year work counts). Outputs a
  candidates CSV with up to 50 flagged authors + their classification-
  relevant metadata, and an initial heuristic auto-classification.

- Pass B (manual, inline): inspect candidates and refine classifications.
  Aggregate verdict (error / plausible / uncertain).

- Pass C (auto): write `disambiguation-check.md` with H1/H2/H3 outcomes.

Sample design:
- 200 unique authors, frequency-weighted by appearances in
  `missingness-bias-raw.parquet`'s authorships across 22K papers.
- Manual-inspection budget: 50 (random subsample if more than 50 flagged).
- Seed: 42 (matches Check 1f).

Outputs:
- `experiments/phase-0.1/disambiguation-check-raw.csv` — all 200 sampled
  authors with career-length data + flag.
- `experiments/phase-0.1/disambiguation-check-candidates.csv` — flagged
  candidates (up to 50) with classification-relevant metadata + initial
  heuristic auto-classification. Hand-edit `verdict` column during Pass B.
- `experiments/phase-0.1/disambiguation-check.md` — written in Pass C.
"""

from __future__ import annotations

import json
import random
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd
import requests
from tqdm import tqdm

_OUT_DIR = Path(__file__).parent
# Use Check 5a's pilot output (authorships_json populated) instead of re-fetching
# 1000 papers from missingness-bias-raw.parquet. The pilot IS the §0 analytical
# population — directly relevant scope.
_PILOT_PARQUET = _OUT_DIR.parent.parent / "data" / "metadata" / "pilot-query-results.parquet"

_N_SAMPLE = 200
_MANUAL_BUDGET = 50
_FLAG_THRESHOLD_YEARS = 60
_SEED = 42

_BASE_URL = "https://api.openalex.org"
_MAILTO = "gkartik@gmail.com"
_HEADERS = {"User-Agent": "ws2/0.0.0"}


# ---------- helpers ----------


def _author_id(author_field: dict[str, Any]) -> str | None:
    raw = author_field.get("id") or ""
    bare = raw.rsplit("/", 1)[-1] if "/" in raw else raw
    return bare if bare and bare.startswith("A") else None


def _collect_author_frequencies() -> Counter[str]:
    """Harvest author appearances from Check 5a's pilot parquet (authorships
    pre-extracted in the authorships_json column). No API calls needed.
    """
    df = pd.read_parquet(_PILOT_PARQUET)
    print(f"  pilot parquet has {len(df)} papers (§0 analytical population)")
    counts: Counter[str] = Counter()
    for authorships_json in df["authorships_json"]:
        if not isinstance(authorships_json, str) or not authorships_json:
            continue
        try:
            authorships = json.loads(authorships_json)
        except json.JSONDecodeError:
            continue
        if not isinstance(authorships, list):
            continue
        for a in authorships:
            if isinstance(a, dict):
                aid = _author_id(a.get("author") or {})
                if aid:
                    counts[aid] += 1
    print(f"  harvested {len(counts)} unique author IDs from {len(df)} papers")
    return counts


def _frequency_weighted_sample(counts: Counter[str], n: int) -> list[str]:
    rng = random.Random(_SEED)
    ids = list(counts.keys())
    weights = [counts[i] for i in ids]
    if len(ids) <= n:
        return ids
    return rng.sample(ids, n) if sum(weights) == 0 else (
        rng.choices(ids, weights=weights, k=n * 3)  # over-sample to handle dedup
    )


def _fetch_author(author_id: str) -> dict[str, Any] | None:
    r = requests.get(
        f"{_BASE_URL}/authors/{author_id}",
        params={"mailto": _MAILTO},
        headers=_HEADERS,
        timeout=30,
    )
    if r.status_code != 200:
        return None
    return r.json()


def _extract_career(author_record: dict[str, Any]) -> dict[str, Any]:
    """Extract first/latest publication years from author record's
    counts_by_year. Returns dict with first_year, latest_year, career_length,
    plus classification-relevant metadata.
    """
    counts_by_year = author_record.get("counts_by_year") or []
    years = [c["year"] for c in counts_by_year if c.get("works_count", 0) > 0]
    first_year = min(years) if years else None
    latest_year = max(years) if years else None
    career_length = (latest_year - first_year) if (first_year and latest_year) else None

    # Affiliations: distinct institution display names across affiliations history
    affils = author_record.get("affiliations") or []
    institutions = []
    for a in affils:
        inst = a.get("institution") or {}
        name = inst.get("display_name")
        if name:
            institutions.append(name)
    distinct_institutions = list(set(institutions))

    # Top topics
    topics = author_record.get("topics") or []
    topic_names = [t.get("display_name") for t in topics[:5] if t.get("display_name")]

    # Name variants
    display_name = author_record.get("display_name", "")
    name_alternatives = author_record.get("display_name_alternatives") or []

    # Counts breakdown for diagnosis
    works_count = author_record.get("works_count", 0)

    return {
        "author_id": author_record.get("id", "").rsplit("/", 1)[-1],
        "display_name": display_name,
        "name_alternatives": json.dumps(name_alternatives[:5]),
        "n_name_alternatives": len(name_alternatives),
        "first_year": first_year,
        "latest_year": latest_year,
        "career_length": career_length,
        "works_count": works_count,
        "n_distinct_institutions": len(distinct_institutions),
        "top_institutions": json.dumps(distinct_institutions[:3]),
        "n_topics_listed": len(topics),
        "top_topics": json.dumps(topic_names[:3]),
        "openalex_url": author_record.get("id", ""),
    }


def _heuristic_classify(row: dict[str, Any]) -> str:
    """Heuristic auto-classification for flagged authors. Conservative — flags
    most as 'uncertain' so manual Pass B does the real work.

    Heuristics:
    - ≥3 distinct institutions AND ≥3 name alternatives → likely 'error'
      (multiple distinct people merged).
    - 1 institution AND ≤2 name alternatives AND topics consistent → likely
      'plausible' (long career, single lineage).
    - Otherwise: 'uncertain' (manual review).
    """
    n_inst = row.get("n_distinct_institutions", 0)
    n_alts = row.get("n_name_alternatives", 0)
    if n_inst >= 3 and n_alts >= 3:
        return "error_likely"
    if n_inst <= 1 and n_alts <= 2:
        return "plausible_likely"
    return "uncertain"


# ---------- main ----------


def main() -> None:
    print("Check 4 — OpenAlex disambiguation spot-check")
    print(f"  sample target: {_N_SAMPLE} authors (frequency-weighted)")
    print(f"  flag threshold: career_length > {_FLAG_THRESHOLD_YEARS} years")
    print(f"  manual budget: ≤{_MANUAL_BUDGET} flagged for hands-on review")
    print()

    snapshot = datetime.now(timezone.utc).isoformat(timespec="seconds")

    # Pass A.1 — harvest author frequencies from parquet papers
    print("Harvesting author frequencies from missingness-bias-raw.parquet...")
    counts = _collect_author_frequencies()
    print()

    # Pass A.2 — frequency-weighted sample
    print(f"Frequency-weighted sampling {_N_SAMPLE} unique authors...")
    candidates = _frequency_weighted_sample(counts, _N_SAMPLE)
    # Dedup while preserving sample
    seen: set[str] = set()
    sampled_ids: list[str] = []
    for aid in candidates:
        if aid not in seen:
            sampled_ids.append(aid)
            seen.add(aid)
        if len(sampled_ids) >= _N_SAMPLE:
            break
    print(f"  sampled {len(sampled_ids)} unique author IDs")
    print()

    # Pass A.3 — fetch each /authors record + extract career data
    print(f"Fetching /authors records for {len(sampled_ids)} authors...")
    rows: list[dict[str, Any]] = []
    for aid in tqdm(sampled_ids, desc="fetch authors"):
        record = _fetch_author(aid)
        if record is None:
            continue
        career = _extract_career(record)
        career["sample_freq"] = counts.get(aid, 0)
        rows.append(career)
        time.sleep(0.05)
    print()

    # Pass A.4 — flag implausible career lengths
    raw_df = pd.DataFrame(rows)
    print(f"Career-length distribution on {len(raw_df)} successful fetches:")
    if "career_length" in raw_df.columns and len(raw_df) > 0:
        cl = raw_df["career_length"].dropna()
        print(
            f"  mean: {cl.mean():.1f}y; median: {cl.median():.1f}y; "
            f"max: {cl.max()}; >60y: {(cl > _FLAG_THRESHOLD_YEARS).sum()} "
            f"({(cl > _FLAG_THRESHOLD_YEARS).mean():.1%})"
        )
    raw_df["flagged"] = raw_df["career_length"] > _FLAG_THRESHOLD_YEARS
    raw_path = _OUT_DIR / "disambiguation-check-raw.csv"
    raw_df.to_csv(raw_path, index=False)
    print(f"\n  wrote {raw_path}")

    # Pass A.5 — pick up to 50 flagged candidates for manual review
    flagged = raw_df[raw_df["flagged"]].copy()
    if len(flagged) > _MANUAL_BUDGET:
        flagged = flagged.sample(_MANUAL_BUDGET, random_state=_SEED)
    flagged["heuristic_class"] = flagged.apply(
        lambda r: _heuristic_classify(r.to_dict()), axis=1
    )
    flagged["verdict"] = ""  # blank for manual fill in Pass B
    flagged["rationale"] = ""
    candidates_path = _OUT_DIR / "disambiguation-check-candidates.csv"
    flagged.to_csv(candidates_path, index=False)
    print(f"  wrote {candidates_path} ({len(flagged)} candidates for manual review)")

    # Save snapshot for later .md generation
    metadata_path = _OUT_DIR / "disambiguation-check-metadata.json"
    metadata_path.write_text(
        json.dumps(
            {
                "snapshot": snapshot,
                "n_sampled": len(sampled_ids),
                "n_fetched": len(raw_df),
                "n_flagged_total": int(raw_df["flagged"].sum()),
                "manual_budget": _MANUAL_BUDGET,
                "n_in_candidates": len(flagged),
                "flag_rate": float(raw_df["flagged"].mean()),
            },
            indent=2,
        )
    )
    print(f"  wrote {metadata_path}")
    print()
    print("Pass A complete. Next: Pass B (manual classification of candidates)")
    print(f"  → review rows in {candidates_path.name}, fill `verdict` column")
    print("  → then run write_disambiguation_summary.py to produce .md")


if __name__ == "__main__":
    main()
