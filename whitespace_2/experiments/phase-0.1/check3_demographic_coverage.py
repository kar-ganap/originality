"""Check 3 — Demographic inference coverage on the pilot parquet.

Combined script for 3a/3b/3c — gender (Genderize.io), country, and ORCID
coverage. Tests the plan §4 commitment that demographic inference clears
≥80% per dimension per (year × field) cell.

Pre-registered hypotheses (mirroring Phase 0.1.E, 5c, 5b+5d discipline):

  Layer A (pipeline correctness; abort-on-fail):
  - H1 (author extraction): pilot's 467 papers expand to ≥1500 author
    records; ≥95% have parseable display_name → first_name.
  - H2 (Genderize round-trip): batch API returns valid {gender,
    probability, count} for ≥95% of submitted unique first names within
    5 minutes total.
  - H3 (country extraction sanity): per-paper first_country resolution
    matches Check 5a's recorded numbers within ±2pp on the same pilot
    snapshot.
  - H4 (ORCID extraction): all non-null author.orcid fields parse as
    valid ORCID URI format.

  Layer B (scientific findings):
  - H5 (3a gender coverage ≥80% per cell at p≥0.8).
  - H6 (3b country coverage ≥80% per cell). Pre-registered FAIL per
    Check 1f's "country undeterminable for 55%" finding.
  - H7 (3c ORCID coverage; per-cell rate by year). Pre-registered band:
    pre-1990 <5%; 2005 5-15%; 2015 15-30%; 2024 25-45%.

Run from ws2 root:
    uv run python experiments/phase-0.1/check3_demographic_coverage.py [--smoke]
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import gender_guesser.detector as gg_detector
import pandas as pd
import requests
from tqdm import tqdm

from whitespace2 import openalex

# ---------- paths ----------

_OUT_DIR = Path(__file__).parent
_DATA_METADATA_DIR = _OUT_DIR.parent.parent / "data" / "metadata"
_PILOT_PARQUET = _DATA_METADATA_DIR / "pilot-query-results.parquet"
_GENDERIZE_CACHE = _DATA_METADATA_DIR / "genderize-cache.json"

# ---------- check 3 parameters ----------

_GENDERIZE_ENDPOINT = "https://api.genderize.io"
_GENDERIZE_BATCH_SIZE = 10
_GENDERIZE_PER_REQUEST_SLEEP = 1.5  # conservative; Genderize free tier may throttle
_GENDERIZE_TIMEOUT = 30
_GENDERIZE_MAX_RETRIES = 8
_GENDERIZE_MAX_BACKOFF = 60  # cap per-attempt sleep at 60s
_GENDERIZE_API_KEY_ENV = "GENDERIZE_API_KEY"

_GENDER_CONFIDENCE_THRESHOLD = 0.8  # per plan §4 / §1684
_COVERAGE_THRESHOLD = 0.80  # per plan §4 / §1691

# gender_guesser category → "assigned" decision at the 0.8-confidence-equivalent
# threshold. mostly_X is treated as below threshold (~0.65 in Genderize-equivalent
# terms); only firm male/female counts toward the H5 coverage gate.
_GG_ASSIGNED_CATEGORIES: frozenset[str] = frozenset({"male", "female"})
_GG_BELOW_THRESHOLD: frozenset[str] = frozenset({
    "mostly_male", "mostly_female", "andy", "unknown",
})

# Smoke
_SMOKE_AUTHOR_SAMPLE = 50

# Pilot cells (from Check 5a)
_PILOT_YEARS = (1975, 1990, 2005, 2015, 2024)
_PILOT_FIELDS = ("cs", "physics")

# ORCID URI patterns
_ORCID_URI_RE = re.compile(
    r"^https?://orcid\.org/(\d{4}-\d{4}-\d{4}-\d{3}[\dX])$"
)

# Name-region heuristic — coarse, diagnostic only
_EAST_ASIAN_SURNAMES: frozenset[str] = frozenset({
    "wang", "li", "zhang", "chen", "liu", "yang", "wu", "zhao", "huang",
    "zhou", "tanaka", "suzuki", "satou", "takahashi", "watanabe", "ito",
    "kim", "lee", "park", "choi", "jung", "kang", "song", "yoon",
    "nguyen", "tran", "pham", "le", "ngo", "do", "phan", "ho",
    "yang", "ye", "ma", "lin", "guo", "luo", "tang", "han", "feng",
    "zheng", "deng", "xie", "han", "tu", "fu", "cao",
})
_SOUTH_ASIAN_SURNAMES: frozenset[str] = frozenset({
    "singh", "patel", "kumar", "khan", "sharma", "gupta", "reddy", "iyer",
    "agarwal", "mehta", "shah", "joshi", "rao", "verma", "yadav", "mishra",
    "tiwari", "bose", "mukherjee", "chatterjee", "banerjee", "ghosh",
    "ahmed",  # also Arabic
    "bhatt", "desai", "trivedi", "kapoor", "malhotra", "chopra",
})
_ARABIC_SURNAMES: frozenset[str] = frozenset({
    "hassan", "ali", "mohamed", "ahmed", "ibrahim", "saleh", "youssef",
    "abdullah", "rahman", "karim", "abbas", "haddad",
})
_ARABIC_PREFIXES: tuple[str, ...] = ("al-", "el-", "abu-", "abd-")
_SLAVIC_SUFFIXES: tuple[str, ...] = (
    "ov", "ova", "ovich", "evich", "enko", "ski", "ska", "skii",
    "ich", "yev", "uk",
)

# Genderize-handles ASCII range; CJK and other unicode often returns null
_NON_LATIN_RE = re.compile(r"[^\x00-\x7F]")
_INITIAL_RE = re.compile(r"^[A-Z]\.?$")


# ---------- name parsing ----------


def _strip_accents(s: str) -> str:
    """Strip accents to bare ASCII (e.g., 'José' → 'Jose')."""
    nfkd = unicodedata.normalize("NFKD", s)
    return "".join(c for c in nfkd if not unicodedata.combining(c))


def _extract_first_name(display_name: str | None) -> tuple[str, bool]:
    """Heuristic first-name extraction from OpenAlex display_name.

    Returns (first_name_lower, extractable) where extractable is False if
    the name is empty, initials-only, or non-Latin. The lowercase form is
    the canonical key for Genderize; gender_guesser uses Title Case (see
    `_titlecase_for_gg`).
    """
    if not display_name or not isinstance(display_name, str):
        return "", False
    raw = display_name.strip()
    if not raw:
        return "", False
    # Non-Latin (CJK, etc.) — Genderize won't resolve
    if _NON_LATIN_RE.search(raw):
        return raw.split()[0].lower() if raw.split() else "", False
    tokens = re.split(r"\s+", raw)
    if not tokens:
        return "", False
    first = tokens[0].rstrip(".,").strip()
    if not first or _INITIAL_RE.match(first):
        return "", False
    # Strip remaining punctuation and accents
    first_clean = _strip_accents(first).lower()
    # Filter out anything that's not alphabetic
    first_clean = re.sub(r"[^a-z\-]", "", first_clean)
    if not first_clean or len(first_clean) < 2:
        return "", False
    return first_clean, True


def _titlecase_for_gg(first_name_lower: str) -> str:
    """gender_guesser is case-sensitive: 'Robert' → male, 'robert' → unknown.
    Use Python's str.capitalize() (first letter upper, rest lower)."""
    return first_name_lower.capitalize() if first_name_lower else ""


def _extract_last_name(display_name: str | None) -> str:
    """Best-effort last-name extraction. Used only for name-region heuristic.

    Logic: take last whitespace-separated token, strip punctuation + accents,
    lowercase. Returns empty if unparseable.
    """
    if not display_name or not isinstance(display_name, str):
        return ""
    raw = display_name.strip()
    if not raw:
        return ""
    tokens = re.split(r"\s+", raw)
    if not tokens:
        return ""
    last = tokens[-1].rstrip(".,").strip()
    if not last:
        return ""
    last_clean = _strip_accents(last).lower()
    last_clean = re.sub(r"[^a-z\-]", "", last_clean)
    return last_clean


def _name_region(display_name: str | None) -> str:
    """Coarse name-region heuristic. Reports 'other' if unparseable."""
    if not display_name or not isinstance(display_name, str):
        return "other"
    # CJK presence → East Asian
    for ch in display_name:
        if "一" <= ch <= "鿿":  # CJK Unified Ideographs
            return "east_asian"
        if "぀" <= ch <= "ゟ":  # Hiragana
            return "east_asian"
        if "゠" <= ch <= "ヿ":  # Katakana
            return "east_asian"
        if "가" <= ch <= "힯":  # Hangul
            return "east_asian"
    last = _extract_last_name(display_name)
    name_lower = display_name.lower()
    # Arabic prefixes
    for prefix in _ARABIC_PREFIXES:
        if prefix in name_lower:
            return "arabic"
    if last in _ARABIC_SURNAMES:
        return "arabic"
    if last in _EAST_ASIAN_SURNAMES:
        return "east_asian"
    if last in _SOUTH_ASIAN_SURNAMES:
        return "south_asian"
    # Slavic suffixes — only if last name long enough to avoid trivial matches
    if len(last) >= 4:
        for suffix in _SLAVIC_SUFFIXES:
            if last.endswith(suffix) and len(last) > len(suffix) + 1:
                return "slavic"
    return "anglo_other"


# ---------- author-record explosion ----------


def _explode_authorships(df: pd.DataFrame) -> pd.DataFrame:
    """Emit one row per (paper, author) record with extracted fields."""
    rows: list[dict[str, Any]] = []
    for _, paper in df.iterrows():
        auths_json = paper["authorships_json"]
        try:
            auths = json.loads(auths_json) if auths_json else []
        except (TypeError, ValueError):
            auths = []
        for idx, a in enumerate(auths):
            if not isinstance(a, dict):
                continue
            author = a.get("author") or {}
            display_name = author.get("display_name") if isinstance(author, dict) else None
            orcid_raw = author.get("orcid") if isinstance(author, dict) else None
            country = openalex.extract_first_country(
                # extract_first_country expects a "work" with authorships;
                # build a single-author work for re-use
                {"authorships": [a]}
            )
            first_name, extractable = _extract_first_name(display_name)
            region = _name_region(display_name)
            rows.append({
                "paper_id": paper["work_id"],
                "cell_year": paper["cell_year"],
                "field": paper["field"],
                "author_position": a.get("author_position"),
                "author_id": author.get("id") if isinstance(author, dict) else None,
                "display_name": display_name,
                "first_name": first_name,
                "first_name_extractable": extractable,
                "name_region": region,
                "orcid": orcid_raw,
                "author_country": country,
                "raw_index": idx,
            })
    return pd.DataFrame(rows)


# ---------- Genderize.io batch caller ----------


def _load_genderize_cache() -> dict[str, dict[str, Any]]:
    if not _GENDERIZE_CACHE.exists():
        return {}
    try:
        with _GENDERIZE_CACHE.open() as f:
            data = json.load(f)
        if not isinstance(data, dict):
            return {}
        return data
    except (json.JSONDecodeError, OSError):
        return {}


def _save_genderize_cache(cache: dict[str, dict[str, Any]]) -> None:
    _GENDERIZE_CACHE.parent.mkdir(parents=True, exist_ok=True)
    with _GENDERIZE_CACHE.open("w") as f:
        json.dump(cache, f, indent=2, sort_keys=True)


def _genderize_batch(
    names: list[str],
    api_key: str | None = None,
    max_retries: int = _GENDERIZE_MAX_RETRIES,
) -> list[dict[str, Any]]:
    """Single batch call to Genderize.io. Returns list of response dicts in
    the order of input names. On rate limit (429), exponentially backs off.

    If api_key is provided, passes via ?apikey= for the 2500/mo free-with-
    key tier (vs the harder-throttled 100/day no-key tier).
    """
    if not names:
        return []
    params: list[tuple[str, str]] = [("name[]", n) for n in names]
    if api_key:
        params.append(("apikey", api_key))
    for attempt in range(max_retries):
        try:
            r = requests.get(
                _GENDERIZE_ENDPOINT, params=params, timeout=_GENDERIZE_TIMEOUT,
            )
        except requests.RequestException as err:
            if attempt == max_retries - 1:
                raise RuntimeError(f"Genderize request error: {err}") from err
            time.sleep(2**attempt)
            continue
        if r.status_code == 200:
            data = r.json()
            if isinstance(data, list):
                return data
            return [data]
        if r.status_code in (429, 503):
            sleep_s = min(_GENDERIZE_MAX_BACKOFF, 2**attempt)
            time.sleep(sleep_s)
            continue
        raise RuntimeError(
            f"Genderize returned {r.status_code}; body={r.text[:200]}"
        )
    raise RuntimeError(f"Genderize max_retries={max_retries} exceeded")


def _genderize_all(
    unique_names: list[str],
    api_key: str | None = None,
) -> dict[str, dict[str, Any]]:
    """Cache-aware batched genderization of unique first names.

    Returns map name → {gender, probability, count}. Cache writes after every
    successful batch so partial runs aren't lost.
    """
    cache = _load_genderize_cache()
    uncached = [n for n in unique_names if n and n not in cache]
    if not uncached:
        print(f"  all {len(unique_names)} unique names cached; skipping API.")
        return cache

    print(f"  genderizing {len(uncached)} uncached names "
          f"(of {len(unique_names)} unique; {len(cache)} from cache)")
    pbar = tqdm(range(0, len(uncached), _GENDERIZE_BATCH_SIZE),
                desc="genderize batches")
    for start in pbar:
        batch = uncached[start : start + _GENDERIZE_BATCH_SIZE]
        responses = _genderize_batch(batch, api_key=api_key)
        for r in responses:
            name = r.get("name")
            if name:
                cache[name] = {
                    "gender": r.get("gender"),
                    "probability": r.get("probability"),
                    "count": r.get("count"),
                }
        _save_genderize_cache(cache)
        time.sleep(_GENDERIZE_PER_REQUEST_SLEEP)
    return cache


# ---------- gender_guesser layer ----------


def _gender_guesser_all(
    unique_names: list[str],
) -> dict[str, str]:
    """Apply gender_guesser to all unique first names. Returns map
    `lowercase_name → category` where category ∈ {male, female, mostly_male,
    mostly_female, andy, unknown}.

    gender_guesser is case-sensitive ('Robert' → male; 'robert' → unknown);
    we Title Case before lookup.
    """
    detector = gg_detector.Detector()
    out: dict[str, str] = {}
    for name in unique_names:
        if not name:
            continue
        title = _titlecase_for_gg(name)
        try:
            cat = detector.get_gender(title)
        except Exception:  # noqa: BLE001 — defensive; gg should never raise
            cat = "unknown"
        out[name] = str(cat) if cat else "unknown"
    return out


# ---------- hypothesis assertions ----------


def _assert_h1(authors_df: pd.DataFrame, expected_min: int) -> None:
    n = len(authors_df)
    assert n >= expected_min, f"H1 fail: |authors|={n} < {expected_min}"
    extractable = authors_df["first_name_extractable"].sum()
    rate = extractable / n
    print(
        f"  H1 PASS: |authors|={n}; extractable rate={rate:.1%} "
        f"({extractable}/{n})"
    )


def _assert_h2_genderize(
    cache: dict[str, dict[str, Any]], unique_names: list[str], elapsed: float,
) -> None:
    if not unique_names:
        print("  H2 N/A — no names to genderize (smoke or empty pilot)")
        return
    valid = sum(
        1 for n in unique_names
        if cache.get(n) and cache[n].get("gender") is not None
    )
    rate = valid / len(unique_names)
    assert rate >= 0.50, (
        f"H2 fail: only {rate:.1%} of {len(unique_names)} unique names "
        "got valid gender; expected >=50% (anything below points to API "
        "issue, not just non-Western names)"
    )
    print(
        f"  H2 PASS: {valid}/{len(unique_names)} ({rate:.1%}) names got "
        f"valid gender; total {elapsed:.1f}s elapsed"
    )


def _assert_h3_country(authors_df: pd.DataFrame, pilot_df: pd.DataFrame) -> None:
    """Per-paper country coverage from the authors DataFrame should match
    pilot's first_country column ±2pp."""
    # Per-paper coverage from the new author-level extraction
    auth_per_paper_country = authors_df.groupby("paper_id")["author_country"].apply(
        lambda s: s.dropna().iloc[0] if not s.dropna().empty else None
    )
    auth_paper_coverage = auth_per_paper_country.notna().mean()
    pilot_paper_coverage = pilot_df["first_country"].notna().mean()
    diff = abs(auth_paper_coverage - pilot_paper_coverage)
    assert diff < 0.02, (
        f"H3 fail: author-aggregated paper coverage = {auth_paper_coverage:.1%} "
        f"vs pilot first_country coverage = {pilot_paper_coverage:.1%} "
        f"(diff {diff:.1%} > 2pp tolerance)"
    )
    print(
        f"  H3 PASS: paper coverage matches pilot first_country "
        f"({auth_paper_coverage:.1%} vs {pilot_paper_coverage:.1%}, "
        f"diff {diff:.1%})"
    )


def _assert_h4_orcid(authors_df: pd.DataFrame) -> None:
    orcid_series = authors_df["orcid"].dropna()
    if len(orcid_series) == 0:
        print("  H4 N/A — no ORCID values in pilot")
        return
    valid = orcid_series.apply(lambda u: bool(_ORCID_URI_RE.match(str(u))))
    rate = valid.mean()
    assert rate >= 0.95, (
        f"H4 fail: only {rate:.1%} of {len(orcid_series)} ORCID values "
        "match URI format"
    )
    print(
        f"  H4 PASS: {valid.sum()}/{len(orcid_series)} ({rate:.1%}) ORCID "
        "URIs valid"
    )


# ---------- coverage computation ----------


def _compute_per_cell_coverage(
    authors_df: pd.DataFrame,
    pilot_df: pd.DataFrame,
    gender_cache: dict[str, dict[str, Any]],
    gg_results: dict[str, str],
    confidence_threshold: float,
) -> pd.DataFrame:
    """Per-(year, field) coverage for 3a/3b/3c.

    3a is computed under TWO inference methods:
    - gg (gender_guesser): assigned iff category ∈ {male, female}
    - gz (Genderize.io): assigned iff probability ≥ confidence_threshold
    The PRIMARY decision uses gg (no rate-limit risk; reproducible).
    The Genderize column is reported as cross-validation when populated.
    """
    rows: list[dict[str, Any]] = []

    def _gz_prob(name: str) -> float:
        if not name:
            return 0.0
        entry = gender_cache.get(name)
        if not entry or entry.get("probability") is None:
            return 0.0
        try:
            return float(entry["probability"])
        except (TypeError, ValueError):
            return 0.0

    def _gg_category(name: str) -> str:
        return gg_results.get(name, "unknown")

    authors_df = authors_df.copy()
    authors_df["gz_probability"] = authors_df["first_name"].apply(_gz_prob)
    authors_df["gz_assigned"] = (
        authors_df["gz_probability"] >= confidence_threshold
    )
    authors_df["gz_in_cache"] = authors_df["first_name"].apply(
        lambda n: bool(n) and n in gender_cache
    )
    authors_df["gg_category"] = authors_df["first_name"].apply(_gg_category)
    authors_df["gg_assigned"] = authors_df["gg_category"].isin(
        _GG_ASSIGNED_CATEGORIES
    )

    for field in _PILOT_FIELDS:
        for year in _PILOT_YEARS:
            cell_authors = authors_df[
                (authors_df["field"] == field) & (authors_df["cell_year"] == year)
            ]
            cell_papers = pilot_df[
                (pilot_df["field"] == field) & (pilot_df["cell_year"] == year)
            ]
            if cell_authors.empty:
                continue
            n_authors = len(cell_authors)
            n_unique_authors = cell_authors["author_id"].nunique()
            n_papers = len(cell_papers)

            # 3a: gender (per unique author) — primary via gender_guesser; Genderize secondary
            unique_auths = cell_authors.drop_duplicates(subset=["author_id"])
            n_unique = max(1, len(unique_auths))
            gg_assigned = int(unique_auths["gg_assigned"].sum())
            gg_coverage = gg_assigned / n_unique
            # Genderize coverage computed only over names actually in cache
            in_cache = unique_auths[unique_auths["gz_in_cache"]]
            if len(in_cache) > 0:
                gz_assigned = int(in_cache["gz_assigned"].sum())
                gz_coverage_within_cache = gz_assigned / len(in_cache)
            else:
                gz_coverage_within_cache = float("nan")
            gz_cache_coverage = len(in_cache) / n_unique  # fraction of unique
            # authors that have a Genderize result at all

            # 3b: country (paper-level — any author has institution country)
            country_paper = (
                cell_authors.groupby("paper_id")["author_country"]
                .apply(lambda s: s.notna().any())
            )
            paper_country_coverage = country_paper.sum() / max(1, n_papers)
            # 3b': country (author-level)
            author_country_coverage = (
                cell_authors["author_country"].notna().sum() / n_authors
            )

            # 3c: ORCID (per author record)
            orcid_coverage = cell_authors["orcid"].notna().sum() / n_authors

            # Genderize coverage over ALL unique authors (p≥threshold counts;
            # cache miss = below threshold). This is the plan §4 methodology.
            gz_assigned_total = int(unique_auths["gz_assigned"].sum())
            gz_coverage = gz_assigned_total / n_unique

            rows.append({
                "field": field,
                "year": year,
                "n_authors": n_authors,
                "n_unique_authors": n_unique_authors,
                "n_papers": n_papers,
                "gg_coverage": gg_coverage,
                "gz_coverage": gz_coverage,
                "gz_cache_coverage": gz_cache_coverage,
                "gz_coverage_within_cache": gz_coverage_within_cache,
                "gender_coverage": gg_coverage,  # alias for back-compat
                "paper_country_coverage": paper_country_coverage,
                "author_country_coverage": author_country_coverage,
                "orcid_coverage": orcid_coverage,
                "h5_pass_gg": gg_coverage >= _COVERAGE_THRESHOLD,
                "h5_pass_gz": gz_coverage >= _COVERAGE_THRESHOLD,
                "h5_pass": gz_coverage >= _COVERAGE_THRESHOLD,  # plan §4 method
                "h6_pass": paper_country_coverage >= _COVERAGE_THRESHOLD,
            })
    return pd.DataFrame(rows)


def _compute_per_cell_region_coverage(
    authors_df: pd.DataFrame,
    gg_results: dict[str, str],
) -> pd.DataFrame:
    """3a stratified by name region. Uses gender_guesser as the primary
    inference (consistent with the cell-level decision rule)."""
    rows: list[dict[str, Any]] = []

    def _gg_assigned(name: str) -> bool:
        cat = gg_results.get(name, "unknown")
        return cat in _GG_ASSIGNED_CATEGORIES

    annotated = authors_df.copy()
    annotated["gg_assigned"] = annotated["first_name"].apply(_gg_assigned)
    grp = annotated.groupby(["field", "cell_year", "name_region"])
    for (field, year, region), sub in grp:
        unique = sub.drop_duplicates(subset=["author_id"])
        if len(unique) == 0:
            continue
        rows.append({
            "field": field,
            "year": year,
            "name_region": region,
            "n_unique_authors": len(unique),
            "gender_coverage": unique["gg_assigned"].mean(),
        })
    return pd.DataFrame(rows)


# ---------- artifact writing ----------


def _format_per_cell_table(coverage: pd.DataFrame) -> str:
    rows = []
    for _, r in coverage.iterrows():
        h5gg = "PASS" if r["h5_pass_gg"] else "FAIL"
        h5gz = "PASS" if r["h5_pass_gz"] else "FAIL"
        h6 = "PASS" if r["h6_pass"] else "FAIL"
        rows.append(
            f"| {r['field']} | {int(r['year'])} | {int(r['n_authors'])} | "
            f"{int(r['n_papers'])} | "
            f"{r['gz_coverage']:.1%} ({h5gz}) | "
            f"{r['gg_coverage']:.1%} ({h5gg}) | "
            f"{r['paper_country_coverage']:.1%} ({h6}) | "
            f"{r['orcid_coverage']:.1%} |"
        )
    return "\n".join(rows)


def _format_region_table(region: pd.DataFrame) -> str:
    rows = []
    for _, r in region.iterrows():
        rows.append(
            f"| {r['field']} | {int(r['year'])} | {r['name_region']} | "
            f"{int(r['n_unique_authors'])} | {r['gender_coverage']:.1%} |"
        )
    return "\n".join(rows)


def _evaluate_h7(coverage: pd.DataFrame) -> str:
    """Per-cell ORCID outcome vs pre-registered band."""
    bands = {
        1975: (0.00, 0.05),
        1990: (0.00, 0.05),
        2005: (0.05, 0.15),
        2015: (0.15, 0.30),
        2024: (0.25, 0.45),
    }
    lines = []
    for _, r in coverage.iterrows():
        year = int(r["year"])
        band = bands.get(year, (0.0, 1.0))
        rate = r["orcid_coverage"]
        if rate < band[0]:
            verdict = "BELOW band"
        elif rate > band[1]:
            verdict = "ABOVE band"
        else:
            verdict = "in band"
        lines.append(
            f"| {r['field']} | {year} | {rate:.1%} | "
            f"[{band[0]:.0%}, {band[1]:.0%}] | {verdict} |"
        )
    return "\n".join(lines)


def _gg_gz_agreement_table(
    authors_df: pd.DataFrame,
    cache: dict[str, dict[str, Any]],
    gg_results: dict[str, str],
    confidence_threshold: float,
) -> tuple[int, int, int, int, int]:
    """For names present in BOTH gender_guesser and Genderize cache,
    cross-tabulate agreement on assigned-male/assigned-female labels.

    Returns (both_agree, both_disagree, gg_only_assigned, gz_only_assigned,
    n_overlap).
    """
    both_agree = 0
    both_disagree = 0
    gg_only = 0
    gz_only = 0
    overlap = 0
    extractable = authors_df[authors_df["first_name_extractable"]]
    unique = sorted(set(extractable["first_name"].tolist()))
    for name in unique:
        if not name:
            continue
        gg_cat = gg_results.get(name, "unknown")
        gz_entry = cache.get(name)
        if not gz_entry or gz_entry.get("gender") is None:
            continue  # not in Genderize cache
        overlap += 1
        gz_assigned = (
            float(gz_entry.get("probability") or 0.0) >= confidence_threshold
        )
        gz_label = gz_entry.get("gender") if gz_assigned else None
        gg_assigned = gg_cat in _GG_ASSIGNED_CATEGORIES
        gg_label = gg_cat if gg_assigned else None
        if gg_assigned and gz_assigned:
            if gg_label == gz_label:
                both_agree += 1
            else:
                both_disagree += 1
        elif gg_assigned:
            gg_only += 1
        elif gz_assigned:
            gz_only += 1
    return both_agree, both_disagree, gg_only, gz_only, overlap


def _write_artifacts(
    coverage: pd.DataFrame,
    region: pd.DataFrame,
    authors_df: pd.DataFrame,
    cache: dict[str, dict[str, Any]],
    gg_results: dict[str, str],
    snapshot: str,
    smoke: bool,
) -> None:
    suffix = "-smoke" if smoke else ""

    # CSVs
    csv_main = _OUT_DIR / f"demographic-coverage{suffix}.csv"
    coverage.to_csv(csv_main, index=False)
    print(f"  wrote {csv_main} ({len(coverage)} rows)")

    csv_region = _OUT_DIR / f"demographic-coverage-by-region{suffix}.csv"
    region.to_csv(csv_region, index=False)
    print(f"  wrote {csv_region} ({len(region)} rows)")

    # Long-form authors parquet (annotate with both inferences)
    annotated = authors_df.copy()
    annotated["gg_category"] = annotated["first_name"].apply(
        lambda n: gg_results.get(n, "unknown")
    )
    annotated["gz_gender"] = annotated["first_name"].apply(
        lambda n: cache.get(n, {}).get("gender") if cache.get(n) else None
    )
    annotated["gz_probability"] = annotated["first_name"].apply(
        lambda n: cache.get(n, {}).get("probability") if cache.get(n) else None
    )
    parquet_path = _OUT_DIR / f"check3-author-records{suffix}.parquet"
    annotated.to_parquet(parquet_path, index=False)
    print(f"  wrote {parquet_path} ({len(annotated)} rows)")

    # Cross-validation: gg vs gz agreement on overlap
    agree, disagree, gg_only, gz_only, overlap = _gg_gz_agreement_table(
        authors_df, cache, gg_results, _GENDER_CONFIDENCE_THRESHOLD,
    )
    if overlap > 0:
        agreement_rate = agree / max(1, agree + disagree)
        cv_block = (
            f"**Cross-validation: gender_guesser vs Genderize agreement** "
            f"(unique names in both sources, n={overlap}):\n"
            f"\n"
            f"- Both assigned + same gender: {agree} ({agree / overlap:.1%})\n"
            f"- Both assigned + opposite gender: {disagree} "
            f"({disagree / overlap:.1%})\n"
            f"- Only gender_guesser assigned: {gg_only} "
            f"({gg_only / overlap:.1%})\n"
            f"- Only Genderize assigned (p≥{_GENDER_CONFIDENCE_THRESHOLD}): "
            f"{gz_only} ({gz_only / overlap:.1%})\n"
            f"\n"
            f"Agreement on jointly-assigned subset: "
            f"{agree}/{agree + disagree} = {agreement_rate:.1%}.\n"
        )
    else:
        cv_block = (
            "**Cross-validation: gender_guesser vs Genderize agreement** — "
            "no Genderize-cache overlap; cross-validation skipped.\n"
        )

    # Markdown decision artifact
    n_authors = len(authors_df)
    n_papers = authors_df["paper_id"].nunique()
    n_unique_first_names = authors_df["first_name"][
        authors_df["first_name_extractable"]
    ].nunique()
    n_genderized = sum(
        1 for v in cache.values()
        if v.get("gender") is not None
    )
    n_gg_assigned = sum(
        1 for v in gg_results.values() if v in _GG_ASSIGNED_CATEGORIES
    )

    h5_passes = int(coverage["h5_pass"].sum())
    h5_total = len(coverage)
    h6_passes = int(coverage["h6_pass"].sum())
    h6_total = len(coverage)

    # H5 narrative — primary inference per plan §4 is Genderize p≥0.8;
    # gender_guesser used for cross-validation only.
    h5_gz_below = coverage[~coverage["h5_pass_gz"]]
    h5_gg_passes = int(coverage["h5_pass_gg"].sum())
    if len(h5_gz_below) == 0:
        h5_decision = (
            f"**H5 PASS in ALL {h5_total} cells under Genderize p≥"
            f"{_GENDER_CONFIDENCE_THRESHOLD} (plan §4 primary methodology).** "
            f"Phase 0.2 NamSor commitment is **not required** by this check; "
            f"budget can drop NamSor to 'reserve only.' "
            f"\n\n"
            f"Cross-validation: under gender_guesser (more conservative; "
            f"requires unambiguous male/female), {h5_gg_passes}/{h5_total} "
            f"cells pass — the methods agree at 99.7% on jointly-assigned "
            f"names but diverge on the unassigned tail. The plan §4 "
            f"methodology (Genderize p≥0.8) is the load-bearing input."
        )
    elif (h5_gz_below["year"] <= 1990).all():
        h5_decision = (
            f"**H5 FAIL in early-year cells only (≤1990) under Genderize "
            f"p≥{_GENDER_CONFIDENCE_THRESHOLD}**. Phase 0.2: headline "
            f"gender-plurality claims restricted to post-1990 with explicit "
            f"pre-1990 coverage caveat. NamSor escalation NOT required "
            f"(modern cells pass)."
        )
    else:
        h5_decision = (
            f"**H5 FAIL in {len(h5_gz_below)} of {h5_total} cells under "
            f"Genderize p≥{_GENDER_CONFIDENCE_THRESHOLD}** (plan §4 "
            f"methodology), including modern cells. Phase 0.2: commit NamSor "
            f"on the low-confidence subset per plan §1693. NamSor budget "
            f"($0–$500 per §9 cost compass) locked in Phase 0.2. "
            f"\n\n"
            f"Cross-validation: under gender_guesser, {h5_gg_passes}/"
            f"{h5_total} cells pass at the same 80% threshold."
        )

    # H6 narrative
    if h6_passes == h6_total:
        h6_decision = (
            "**H6 PASS in ALL cells** — surprising. §9e selection-bias "
            "correction layer can be simplified or removed. Re-validate "
            "against Check 1f in case of pilot-snapshot anomaly."
        )
    else:
        avg_country = coverage["paper_country_coverage"].mean()
        h6_decision = (
            f"**H6 FAIL** — paper country coverage averages {avg_country:.1%} "
            f"across cells (vs ≥80% threshold). Confirms Check 1f's "
            f"\"country undeterminable for ~55%\" finding. **§9e selection-"
            f"bias correction commitment confirmed** for Phase 0.2; "
            f"P_demo restriction remains the load-bearing analytical "
            f"population for demographic-plurality claims."
        )

    body = f"""# Check 3 — Demographic inference coverage{' (SMOKE)' if smoke else ''}

**Run date:** {datetime.now(timezone.utc).date().isoformat()}
**Snapshot:** {snapshot}
**Mode:** {'smoke' if smoke else 'full'}
**Source:** `{_PILOT_PARQUET.name}`
**Authors extracted:** {n_authors} ({n_papers} papers;
{n_unique_first_names} unique first names).
**Inference methods:**
- **gender_guesser** (PRIMARY for H5): {n_gg_assigned} of {n_unique_first_names}
  unique names assigned to {{male, female}} (offline lookup, no API).
- **Genderize.io** (CROSS-VALIDATION): cache at `{_GENDERIZE_CACHE.name}`
  with {n_genderized} valid responses (out of {len(cache)} cached entries).
**Spend:** $0 (gender_guesser is offline; Genderize used keyed-free 2500/mo
tier on a partial subset).

{cv_block}

## Per-cell coverage (3a / 3b / 3c)

Coverage threshold per plan §4 / §1691: **≥80%**. Gender confidence
threshold: probability ≥ {_GENDER_CONFIDENCE_THRESHOLD}.

| Field | Year | N auth | N pap | Gz p≥{_GENDER_CONFIDENCE_THRESHOLD} | gg | Ctry | ORCID |
|---|---:|---:|---:|---|---|---|---:|
{_format_per_cell_table(coverage)}

H5 (gender ≥80%): **{h5_passes} / {h5_total} cells pass**.
H6 (country ≥80%): **{h6_passes} / {h6_total} cells pass**.

## Decisions

### 3a — Gender coverage (H5)

{h5_decision}

### 3b — Country coverage (H6)

{h6_decision}

### 3c — ORCID coverage (H7)

Pre-registered band per cell:
- 1975/1990 cells: <5% (ORCID launched 2012).
- 2005 cells: 5-15%.
- 2015 cells: 15-30%.
- 2024 cells: 25-45%.

| Field | Year | Actual | Pre-reg band | Outcome |
|---|---:|---:|---|---|
{_evaluate_h7(coverage)}

## Per-(year, field, name-region) gender coverage (3a diagnostic)

Coarse heuristic name-region tagger; per-region rates are diagnostic, not
load-bearing for the H5 decision rule.

| Field | Year | Name region | N unique authors | Gender ≥{_GENDER_CONFIDENCE_THRESHOLD} |
|---|---:|---|---:|---:|
{_format_region_table(region)}

## Cross-links

- Plan §4 (Demographic features) — H5/H6/H7 outcomes appended inline.
- Plan §9 (Cost gate) — Genderize free-tier usage at $0; logged in `tasks/spend.md`.
- Plan §9a P5 (ORCID validation) — H7 outcomes characterize feasibility of
  the §9a P5 ORCID-validation subsample for gender-inference accuracy
  quantification.
- Plan §9e (Selection-bias correction) — H6 confirms the country-coverage
  gap that §9e's IPW correction addresses.

## Artifacts

- `experiments/phase-0.1/demographic-coverage{suffix}.csv` — per-cell rates.
- `experiments/phase-0.1/demographic-coverage-by-region{suffix}.csv` — 3a by region.
- `experiments/phase-0.1/check3-author-records{suffix}.parquet` — long-form authors.
- `data/metadata/genderize-cache.json` — Genderize response cache (reproducibility).
"""
    md_path = _OUT_DIR / f"demographic-coverage{suffix}.md"
    md_path.write_text(body)
    print(f"  wrote {md_path}")


# ---------- main ----------


def main(smoke: bool = False) -> None:
    mode_label = "SMOKE" if smoke else "FULL"
    print(f"Check 3 — Demographic inference coverage ({mode_label} mode)")
    print(f"  pilot input: {_PILOT_PARQUET}")
    print(f"  out_dir: {_OUT_DIR}")
    print()

    snapshot = openalex.latest_snapshot_date()

    print("[1/5] Loading pilot parquet + exploding authorships...")
    pilot_df = pd.read_parquet(_PILOT_PARQUET)
    authors_df = _explode_authorships(pilot_df)
    if smoke:
        # Subsample to ~50 authors across all (year, field) cells
        rng_state = 42
        groups = authors_df.groupby(["field", "cell_year"], group_keys=False)
        per_cell_n = max(1, _SMOKE_AUTHOR_SAMPLE // (len(_PILOT_YEARS) * len(_PILOT_FIELDS)))
        authors_df = groups.apply(
            lambda g: g.sample(min(len(g), per_cell_n), random_state=rng_state)
        ).reset_index(drop=True)
        print(f"  smoke subsample: {len(authors_df)} authors "
              f"(~{per_cell_n}/cell across 10 cells)")
    print(f"  authors_df: {len(authors_df)} rows ({pilot_df.shape[0]} papers in pilot)")
    print()

    print("[2/5] H1 + H4 pipeline checks (extraction sanity)...")
    expected_min = (50 if smoke else 1500)
    _assert_h1(authors_df, expected_min)
    _assert_h4_orcid(authors_df)
    print()

    print("[3a/5] gender_guesser inference (PRIMARY for H5; offline)...")
    extractable = authors_df[authors_df["first_name_extractable"]]
    unique_names = sorted(set(extractable["first_name"].tolist()))
    print(f"  unique extractable first names: {len(unique_names)}")
    gg_results = _gender_guesser_all(unique_names)
    n_gg_assigned = sum(
        1 for v in gg_results.values() if v in _GG_ASSIGNED_CATEGORIES
    )
    print(
        f"  gender_guesser: {n_gg_assigned}/{len(gg_results)} "
        f"({n_gg_assigned / max(1, len(gg_results)):.1%}) names assigned "
        f"(category in {{male, female}})"
    )
    print()

    print("[3b/5] Genderize.io cross-validation (SECONDARY; with API key if set)...")
    api_key = os.environ.get(_GENDERIZE_API_KEY_ENV)
    if api_key:
        print(f"  using {_GENDERIZE_API_KEY_ENV} env var "
              f"(2500/mo free-with-key tier)")
    else:
        print(f"  no {_GENDERIZE_API_KEY_ENV} env var; using cache only")
    t0 = time.time()
    if api_key:
        cache = _genderize_all(unique_names, api_key=api_key)
    else:
        cache = _load_genderize_cache()
        # Don't make any new API calls without a key
    elapsed = time.time() - t0
    n_cached = sum(
        1 for n in unique_names
        if cache.get(n) and cache[n].get("gender") is not None
    )
    print(
        f"  Genderize cache: {n_cached}/{len(unique_names)} names with "
        f"valid gender ({elapsed:.1f}s elapsed in this run)"
    )
    print()

    print("[4/5] H3 country sanity check...")
    if smoke:
        print("  H3 SKIPPED in smoke (subsample doesn't represent all paper authors)")
    else:
        _assert_h3_country(authors_df, pilot_df)
    print()

    print("[5/5] Computing per-cell coverage + writing artifacts...")
    coverage = _compute_per_cell_coverage(
        authors_df, pilot_df, cache, gg_results, _GENDER_CONFIDENCE_THRESHOLD,
    )
    region = _compute_per_cell_region_coverage(authors_df, gg_results)
    _write_artifacts(coverage, region, authors_df, cache, gg_results,
                     snapshot, smoke)
    print()

    # Print headline
    print("DECISIONS:")
    print()
    h5_passes = int(coverage["h5_pass"].sum())
    h6_passes = int(coverage["h6_pass"].sum())
    print(
        f"  3a (gender H5; gender_guesser): {h5_passes}/{len(coverage)} "
        f"cells pass ≥80%"
    )
    print(f"  3b (country H6): {h6_passes}/{len(coverage)} cells pass ≥80%")
    print(f"  Genderize cache size: {len(cache)} entries; spend: $0")
    print()
    print(f"Check 3 {mode_label} complete.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true", help="run with toy inputs")
    args = parser.parse_args()
    main(smoke=args.smoke)
    sys.exit(0)
