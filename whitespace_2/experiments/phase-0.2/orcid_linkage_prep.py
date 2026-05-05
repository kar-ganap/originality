"""Phase 0.2 Wave 3A — ORCID-linkage hand-audit prep automation.

Pre-processes the 100-record ORCID-linkage validation by:
1. Exploding ORCID-having authors from the Check 5a pilot parquet.
2. Classifying each by name region (heuristic on display_name; no
   external API used — preserves NamSor quota for production
   escalation).
3. Stratified-sampling target 17 per region × 6 regions = 102 (close
   to plan target of 100). Regions with <17 ORCIDs take all available;
   gap redistributed proportionally.
4. For each sampled author, fetching the ORCID public profile
   (https://pub.orcid.org/v3.0/{orcid}/record; no auth needed).
5. Computing automated comparison signals for hand-audit:
   - display_name vs ORCID person.name (given + family) — fuzzy
     match score
   - institution match: any string overlap between OpenAlex
     authorship.institutions[].display_name and ORCID
     employments[]/educations[].organization.name
   - publication match: paper DOI in ORCID works list
6. Output CSV where each row has all the comparison fields user
   needs to mark `linkage_correct ∈ {yes, likely, unclear, no}`.

Hand-audit time post-prep: ~30-60 sec/row × 100 = ~50-100 min
(vs ~5 hours raw per execution plan).

Cost: ~100 ORCID API calls (free, no key); 0 NamSor calls; 0
Genderize calls.

Run from ws2 root:
    uv run python experiments/phase-0.2/orcid_linkage_prep.py
"""

from __future__ import annotations

import json
import re
import sys
import time
from datetime import datetime, timezone
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any

import pandas as pd
import requests
from tqdm import tqdm

_OUT_DIR = Path(__file__).parent
_DATA_METADATA_DIR = _OUT_DIR.parent.parent / "data" / "metadata"
_PILOT_PARQUET = _DATA_METADATA_DIR / "pilot-query-results.parquet"

_ORCID_BASE = "https://pub.orcid.org/v3.0"
_USER_AGENT = "ws2/0.0.0 ORCID-linkage smoke (mailto:gkartik@gmail.com)"
_TOTAL_TARGET = 100
_SAMPLE_SEED = 17
_REQUEST_TIMEOUT = 30
_RATE_LIMIT_SLEEP = 0.25  # ORCID public API ~24 req/sec; be polite


# ---------- name-region heuristic ----------


_EAST_ASIAN_LAST = {
    # Chinese
    "wang", "li", "zhang", "liu", "chen", "yang", "huang", "zhao",
    "wu", "zhou", "xu", "sun", "ma", "zhu", "hu", "guo", "he", "lin",
    "luo", "song", "tang", "han", "cao", "deng", "feng", "shi",
    # Korean
    "kim", "lee", "park", "choi", "jung", "kang", "cho", "yoon",
    "jang", "lim", "han", "shin", "oh", "seo", "kwon",
    # Japanese
    "tanaka", "sato", "suzuki", "takahashi", "ito", "watanabe",
    "yamamoto", "nakamura", "kobayashi", "kato", "yoshida", "yamada",
    "sasaki", "matsumoto", "inoue", "kimura",
    # Vietnamese
    "nguyen", "tran", "le", "pham", "hoang", "phan", "vu", "vo", "dang",
}
_SOUTH_ASIAN_LAST = {
    "patel", "kumar", "singh", "sharma", "gupta", "rao", "reddy",
    "shah", "khan", "rahman", "hossain", "islam", "ahmed", "mukherjee",
    "iyer", "menon", "nair", "pillai", "chowdhury", "mehta", "joshi",
    "agarwal", "agrawal", "verma", "yadav", "tiwari", "trivedi",
    "mishra", "pandey", "bhattacharya", "banerjee", "chatterjee",
    "bose", "das", "ghosh", "sen", "dutta", "sinha",
}
_ARABIC_LAST_PREFIX = ("al-", "al ", "el-", "el ", "abu-", "abu ", "ibn-")
_ARABIC_LAST = {
    "hassan", "ibrahim", "mohammed", "mohamed", "ahmad", "ahmed",
    "khalil", "saleh", "nasser", "mansour", "rashid", "hamdan",
    "mahmoud", "youssef", "yousef", "amin", "fares", "shaker",
    "haddad", "hourani", "naser",
}
_SLAVIC_LAST_SUFFIX = (
    "ov", "ova", "ev", "eva", "ski", "ska", "sky", "icz", "ich",
    "enko", "yuk", "uk", "vich", "nov", "nova", "ny", "skiy",
)
_SLAVIC_LAST = {
    "petrov", "ivanov", "smirnov", "kuznetsov", "popov", "sokolov",
    "lebedev", "kozlov", "novikov", "morozov", "volkov",
    "kowalski", "nowak", "wojcik", "kaminski", "novak", "horak",
}
_ANGLO_LAST = {
    "smith", "johnson", "williams", "brown", "jones", "garcia",
    "miller", "davis", "rodriguez", "martinez", "hernandez",
    "lopez", "gonzalez", "wilson", "anderson", "thomas", "taylor",
    "moore", "jackson", "martin", "lee", "perez", "thompson",
    "white", "harris", "sanchez", "clark", "ramirez", "lewis",
    "robinson", "walker", "young", "allen", "king", "wright",
    "scott", "torres", "nguyen", "hill", "flores", "green",
    "adams", "nelson", "baker", "hall", "rivera", "campbell",
    "mitchell", "carter", "roberts",
}


def _classify_region(display_name: str) -> str:
    """Heuristic name-region classification on last-name patterns.

    Returns one of: anglo, east_asian, south_asian, arabic, slavic, other.
    Approximate but free + reproducible. Used for stratified sampling
    only; not load-bearing for any methodology claim.
    """
    if not display_name:
        return "other"
    name_lower = display_name.lower().strip()
    parts = name_lower.split()
    if not parts:
        return "other"
    last = parts[-1]
    last_clean = re.sub(r"[^a-z-]", "", last)

    # Arabic prefix
    for prefix in _ARABIC_LAST_PREFIX:
        if last_clean.startswith(prefix.replace(" ", "")):
            return "arabic"
        if any(prefix in p for p in parts):
            return "arabic"

    # Whole-word match against region lists
    if last_clean in _EAST_ASIAN_LAST:
        return "east_asian"
    if last_clean in _SOUTH_ASIAN_LAST:
        return "south_asian"
    if last_clean in _ARABIC_LAST:
        return "arabic"
    if last_clean in _SLAVIC_LAST:
        return "slavic"
    if last_clean in _ANGLO_LAST:
        return "anglo"

    # Suffix patterns
    for suf in _SLAVIC_LAST_SUFFIX:
        if last_clean.endswith(suf) and len(last_clean) > len(suf) + 1:
            return "slavic"

    return "other"


# ---------- pilot explosion ----------


def _explode_orcid_authors() -> pd.DataFrame:
    """Returns one row per (work, author) where author has ORCID."""
    df = pd.read_parquet(_PILOT_PARQUET)
    rows: list[dict[str, Any]] = []
    for _, r in df.iterrows():
        auths = json.loads(r["authorships_json"])
        for ap in auths:
            author = ap.get("author") or {}
            orcid = author.get("orcid")
            if not orcid:
                continue
            rows.append({
                "work_id": r["work_id"],
                "publication_year": r["publication_year"],
                "doi": r["doi"],
                "field": r["field"],
                "cell_year": r["cell_year"],
                "openalex_author_id": author.get("id"),
                "openalex_display_name": author.get("display_name") or "",
                "orcid_url": orcid,
                "orcid_id": orcid.rsplit("/", 1)[-1],
                "openalex_institutions_json": json.dumps(
                    ap.get("institutions") or []
                ),
                "raw_affiliation_strings": json.dumps(
                    ap.get("raw_affiliation_strings") or []
                ),
            })
    out_df = pd.DataFrame(rows)
    # Dedup: keep first occurrence of each unique ORCID for sampling
    return out_df.drop_duplicates(subset="orcid_id", keep="first").reset_index(drop=True)


# ---------- stratified sample ----------


def _random_sample(
    df: pd.DataFrame, total_target: int, seed: int,
) -> pd.DataFrame:
    """Random sample without strict regional stratification.

    Heuristic region classification is too sparse (76% land in `other`)
    to drive sampling — and using NamSor /originBatch on all 632
    candidates would burn quota we'd rather preserve for production.
    Random sample is methodologically cleaner anyway: per-region rate
    is computed post-hoc on the sampled rows, with the user free to
    re-classify ambiguous cases during the hand-audit.
    """
    n = min(total_target, len(df))
    return df.sample(n=n, random_state=seed).reset_index(drop=True)


# ---------- ORCID profile fetch ----------


def _fetch_orcid_profile(orcid_id: str) -> dict[str, Any] | None:
    url = f"{_ORCID_BASE}/{orcid_id}/record"
    headers = {"Accept": "application/json", "User-Agent": _USER_AGENT}
    try:
        r = requests.get(url, headers=headers, timeout=_REQUEST_TIMEOUT)
        if r.status_code == 200:
            data: dict[str, Any] = r.json()
            return data
        else:
            return {"_http_status": r.status_code}
    except requests.RequestException as err:
        return {"_request_error": str(err)}


def _normalize_doi(doi: str) -> str:
    """Strip URL prefixes from a DOI string for consistent comparison.

    ORCID's `external-id-value` for DOIs is user-registered and may be
    bare ("10.1234/abc") or prefixed ("https://doi.org/10.1234/abc"
    or other variants). OpenAlex's `extract_doi` strips
    `https://doi.org/` but not other prefixes. Normalize both sides
    to bare form before comparison.
    """
    if not doi:
        return ""
    cleaned = doi.lower().strip()
    for prefix in (
        "https://doi.org/",
        "http://doi.org/",
        "https://dx.doi.org/",
        "http://dx.doi.org/",
        "doi.org/",
        "dx.doi.org/",
        "doi:",
    ):
        if cleaned.startswith(prefix):
            cleaned = cleaned[len(prefix):]
            break
    return cleaned


def _extract_orcid_signals(profile: dict[str, Any]) -> dict[str, Any]:
    """Pull the fields needed for hand-audit comparison."""
    if not profile:
        return {}
    if "_http_status" in profile or "_request_error" in profile:
        return {"_fetch_error": str(profile)}

    person = profile.get("person") or {}
    name = person.get("name") or {}
    given = (name.get("given-names") or {}).get("value") or ""
    family = (name.get("family-name") or {}).get("value") or ""
    full_orcid_name = f"{given} {family}".strip()

    # Employments
    activities = profile.get("activities-summary") or {}
    employments_summary = activities.get("employments") or {}
    affiliation_groups = employments_summary.get("affiliation-group") or []
    employment_orgs: list[str] = []
    for grp in affiliation_groups:
        for summary_item in grp.get("summaries") or []:
            es = summary_item.get("employment-summary") or {}
            org = es.get("organization") or {}
            org_name = org.get("name") or ""
            if org_name:
                employment_orgs.append(org_name)

    # Educations
    educations_summary = activities.get("educations") or {}
    edu_groups = educations_summary.get("affiliation-group") or []
    education_orgs: list[str] = []
    for grp in edu_groups:
        for summary_item in grp.get("summaries") or []:
            es = summary_item.get("education-summary") or {}
            org = es.get("organization") or {}
            org_name = org.get("name") or ""
            if org_name:
                education_orgs.append(org_name)

    # Works (paper DOIs etc.)
    works = activities.get("works") or {}
    work_groups = works.get("group") or []
    work_dois: list[str] = []
    work_titles: list[str] = []
    for grp in work_groups:
        for summary_item in grp.get("work-summary") or []:
            ext_ids = (summary_item.get("external-ids") or {}).get("external-id") or []
            for ext_id in ext_ids:
                if ext_id.get("external-id-type") == "doi":
                    val = ext_id.get("external-id-value") or ""
                    normalized = _normalize_doi(val)
                    if normalized:
                        work_dois.append(normalized)
            t = summary_item.get("title") or {}
            title_val = (t.get("title") or {}).get("value") or ""
            if title_val:
                work_titles.append(title_val)

    return {
        "orcid_given": given,
        "orcid_family": family,
        "orcid_full_name": full_orcid_name,
        "orcid_employments": employment_orgs,
        "orcid_educations": education_orgs,
        "orcid_n_works": len(work_groups),
        "orcid_dois": work_dois,
        "orcid_titles": work_titles[:50],  # cap
    }


# ---------- comparison heuristics ----------


def _name_similarity(name_a: str, name_b: str) -> float:
    if not name_a or not name_b:
        return 0.0
    return SequenceMatcher(None, name_a.lower(), name_b.lower()).ratio()


def _institution_overlap(
    openalex_institutions_json: str, orcid_orgs: list[str],
) -> dict[str, Any]:
    """Returns {'has_match': bool, 'best_pair': (oa, orcid), 'best_score': float}."""
    oa_insts = json.loads(openalex_institutions_json)
    oa_names = [
        (inst.get("display_name") or "").lower()
        for inst in oa_insts if isinstance(inst, dict)
    ]
    oa_names = [n for n in oa_names if n]
    if not oa_names or not orcid_orgs:
        return {"has_match": False, "best_pair": None, "best_score": 0.0}

    best_pair = None
    best_score = 0.0
    for oa in oa_names:
        for org in orcid_orgs:
            score = _name_similarity(oa, org.lower())
            if score > best_score:
                best_score = score
                best_pair = (oa, org)
    return {
        "has_match": best_score >= 0.6,
        "best_pair": best_pair,
        "best_score": best_score,
    }


def _publication_doi_match(paper_doi: str, orcid_dois: list[str]) -> bool:
    """Match OA paper DOI against ORCID's works list of DOIs.

    Both sides are normalized via `_normalize_doi` to handle
    inconsistent URL-prefix forms (ORCID returns user-registered
    strings; OA returns prefix-stripped). Without normalization,
    "10.1234/abc" vs "https://doi.org/10.1234/abc" would silently
    miss.
    """
    if not paper_doi or not orcid_dois:
        return False
    paper_doi_clean = _normalize_doi(paper_doi)
    return paper_doi_clean in orcid_dois


# ---------- main ----------


def main() -> None:
    print("Phase 0.2 Wave 3A — ORCID-linkage hand-audit prep")
    print()

    snapshot = datetime.now(timezone.utc).isoformat(timespec="seconds")

    # 1. Explode authors
    print("Loading pilot parquet + exploding ORCID-having authors...")
    df = _explode_orcid_authors()
    print(f"  {len(df)} unique ORCID-having authors")
    print()

    # 2. Classify region
    print("Classifying name region (heuristic)...")
    df["region"] = df["openalex_display_name"].apply(_classify_region)
    region_counts = df["region"].value_counts()
    print("  Region distribution:")
    for region, count in region_counts.items():
        print(f"    {region}: {count}")
    print()

    # 3. Random sample (heuristic stratification too sparse — see _random_sample doc)
    print(f"Random-sampling {_TOTAL_TARGET} of {len(df)}...")
    sample = _random_sample(df, _TOTAL_TARGET, _SAMPLE_SEED)
    print(f"  sampled {len(sample)} records")
    print("  Sample regional distribution (heuristic; descriptive):")
    for region, count in sample["region"].value_counts().items():
        print(f"    {region}: {count}")
    print()

    # 4. Fetch ORCID profiles
    print(f"Fetching ORCID profiles ({len(sample)} records)...")
    profiles: list[dict[str, Any]] = []
    fetch_errors: list[str] = []
    for _idx, row in tqdm(
        sample.iterrows(), total=len(sample), desc="orcid",
    ):
        orcid_id = row["orcid_id"]
        profile = _fetch_orcid_profile(orcid_id)
        if profile and ("_http_status" in profile or "_request_error" in profile):
            fetch_errors.append(f"{orcid_id}: {profile}")
            profiles.append({})
        else:
            profiles.append(profile or {})
        time.sleep(_RATE_LIMIT_SLEEP)
    print(f"  fetched {len(profiles) - len(fetch_errors)} OK; "
          f"{len(fetch_errors)} errors")
    if fetch_errors:
        for err in fetch_errors[:5]:
            print(f"    {err}")
    print()

    # 5. Compute comparison signals + emit CSV
    print("Computing comparison signals + writing CSV...")
    audit_rows: list[dict[str, Any]] = []
    for (_, oa_row), profile in zip(sample.iterrows(), profiles):
        signals = _extract_orcid_signals(profile)
        # Compose comparison
        oa_name = oa_row["openalex_display_name"]
        orcid_full = signals.get("orcid_full_name", "")
        name_sim = _name_similarity(oa_name, orcid_full) if orcid_full else 0.0

        all_orcid_orgs = (
            signals.get("orcid_employments", [])
            + signals.get("orcid_educations", [])
        )
        inst_match = _institution_overlap(
            oa_row["openalex_institutions_json"], all_orcid_orgs,
        )

        pub_match = _publication_doi_match(
            oa_row.get("doi") or "", signals.get("orcid_dois", []),
        )

        audit_rows.append({
            "orcid_id": oa_row["orcid_id"],
            "orcid_url": oa_row["orcid_url"],
            "region_heuristic": oa_row["region"],
            "openalex_work_id": oa_row["work_id"],
            "openalex_pub_year": oa_row["publication_year"],
            "openalex_field_cell_year": (
                f"{oa_row['field']}_{oa_row['cell_year']}"
            ),
            "openalex_display_name": oa_name,
            "orcid_full_name": orcid_full,
            "name_similarity": round(name_sim, 3),
            "openalex_paper_doi": oa_row.get("doi") or "",
            "openalex_institutions": " | ".join(
                (i.get("display_name") or "")
                for i in json.loads(oa_row["openalex_institutions_json"])
                if isinstance(i, dict)
            ),
            "orcid_employments": " | ".join(signals.get("orcid_employments", [])),
            "orcid_educations": " | ".join(signals.get("orcid_educations", [])),
            "institution_match": inst_match["has_match"],
            "institution_best_score": round(inst_match["best_score"], 3),
            "institution_best_pair": (
                f"{inst_match['best_pair'][0]} ↔ {inst_match['best_pair'][1]}"
                if inst_match["best_pair"] else ""
            ),
            "orcid_n_works": signals.get("orcid_n_works", 0),
            "publication_doi_match": pub_match,
            "fetch_error": (
                "FETCH_FAILED" if "_fetch_error" in signals else ""
            ),
            # User-fillable columns
            "linkage_correct": "",  # yes / likely / unclear / no
            "notes": "",
        })

    audit_df = pd.DataFrame(audit_rows)

    # Order columns for review-friendliness
    column_order = [
        "orcid_id", "orcid_url", "region_heuristic",
        "openalex_pub_year", "openalex_field_cell_year",
        "openalex_display_name", "orcid_full_name", "name_similarity",
        "openalex_institutions", "orcid_employments", "orcid_educations",
        "institution_match", "institution_best_score", "institution_best_pair",
        "openalex_paper_doi", "orcid_n_works", "publication_doi_match",
        "openalex_work_id", "fetch_error",
        "linkage_correct", "notes",
    ]
    audit_df = audit_df[column_order]

    csv_path = _OUT_DIR / "orcid-linkage-audit-input.csv"
    audit_df.to_csv(csv_path, index=False)
    print(f"  wrote {csv_path}")

    # Summary md
    md_path = _OUT_DIR / "orcid-linkage-prep.md"
    n_inst_match = audit_df["institution_match"].sum()
    n_pub_match = audit_df["publication_doi_match"].sum()
    n_high_name_sim = (audit_df["name_similarity"] >= 0.85).sum()
    n_fetch_error = (audit_df["fetch_error"] != "").sum()

    region_summary = "\n".join(
        f"| {region} | {count} |"
        for region, count in audit_df["region_heuristic"].value_counts().items()
    )

    md_body = f"""# Phase 0.2 Wave 3A — ORCID-linkage hand-audit prep

**Run date:** {datetime.now(timezone.utc).date().isoformat()}
**Snapshot:** {snapshot}
**Pool:** Check 5a pilot parquet — {len(df)} unique ORCID-having authors
**Sample:** {len(sample)} records (random, seed={_SAMPLE_SEED};
heuristic region annotation only — too sparse to stratify on,
see prep script docstring)

## Pre-audit signals (auto-computed)

| Signal | Count | % |
|---|---:|---:|
| Name similarity ≥0.85 | {n_high_name_sim} | {n_high_name_sim/len(audit_df):.1%} |
| Institution match (≥0.6 sim) | {n_inst_match} | {n_inst_match/len(audit_df):.1%} |
| Publication DOI match | {n_pub_match} | {n_pub_match/len(audit_df):.1%} |
| ORCID fetch error | {n_fetch_error} | {n_fetch_error/len(audit_df):.1%} |

## Sampling distribution by name-region heuristic

| Region | N |
|---|---:|
{region_summary}

## How to hand-audit

Open `orcid-linkage-audit-input.csv`. Each row has:
- `orcid_url` — click to open the ORCID profile
- `openalex_display_name` vs `orcid_full_name` + `name_similarity`
  (auto-computed)
- `openalex_institutions` vs `orcid_employments` + `orcid_educations`
  + `institution_match` (auto-computed)
- `openalex_paper_doi` vs `publication_doi_match` (auto-computed)
- `linkage_correct` (USER FILLS): `yes` / `likely` / `unclear` / `no`
- `notes` (USER FILLS): any context

**Decision rule** (suggested):
- All three signals match (high name sim + inst match + DOI match):
  → `yes`, no need to open ORCID profile
- Two of three match: → `likely`, brief profile glance
- One of three matches: → `unclear`, full profile read
- Zero match (or fetch error): → `unclear`/`no`, investigate

Aggregate per-region linkage-correctness rate; this becomes the
input to Phase 0.2 plan §4 ORCID-linkage validation. If overall
rate <70% or any region <50%, §9a P5 ground-truth methodology
opens for revision.

## Artifacts

- `experiments/phase-0.2/orcid-linkage-audit-input.csv` — hand-audit
  input (one row per sampled author, all comparison signals
  pre-computed; user fills `linkage_correct` + `notes`)
- `experiments/phase-0.2/orcid-linkage-prep.md` — this artifact
- `experiments/phase-0.2/orcid_linkage_prep.py` — this script
"""
    md_path.write_text(md_body)
    print(f"  wrote {md_path}")

    print()
    print(f"Wave 3A prep complete. {len(audit_df)} rows ready for hand-audit.")


if __name__ == "__main__":
    main()
    sys.exit(0)
