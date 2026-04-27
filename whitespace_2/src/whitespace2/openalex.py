"""OpenAlex REST API client.

Function-based, no global state. Anonymous access with mailto identification;
exponential backoff on 429 / 5xx; raises RuntimeError on other 4xx and on
max-retries exhaustion. See whitespace_2/docs/phases/phase-0.1-plan.md §"Check 1"
for usage context.
"""

from __future__ import annotations

import time
from datetime import datetime, timezone
from typing import Any

import requests

_BASE_URL = "https://api.openalex.org"
_USER_AGENT = "ws2/0.0.0 (https://github.com/kgkartik/originality)"
_DEFAULT_MAILTO = "gkartik@gmail.com"


def _build_filter_string(filters: dict[str, str]) -> str:
    return ",".join(f"{key}:{value}" for key, value in filters.items())


def _request_with_retry(
    url: str,
    params: dict[str, Any],
    max_retries: int,
) -> dict[str, Any]:
    session = requests.Session()
    session.headers.update({"User-Agent": _USER_AGENT})
    last_status: int | None = None
    for attempt in range(max_retries):
        response = session.get(url, params=params, timeout=30)
        last_status = response.status_code
        if response.status_code == 200:
            data: dict[str, Any] = response.json()
            return data
        if response.status_code == 429 or 500 <= response.status_code < 600:
            time.sleep(2**attempt)
            continue
        raise RuntimeError(
            f"OpenAlex returned {response.status_code} (no retry); url={url}"
        )
    raise RuntimeError(
        f"OpenAlex max_retries={max_retries} exceeded; last status={last_status}; url={url}"
    )


def fetch_works(
    filters: dict[str, str],
    sample_size: int | None = None,
    seed: int | None = None,
    select: list[str] | None = None,
    mailto: str = _DEFAULT_MAILTO,
    max_retries: int = 5,
) -> list[dict[str, Any]]:
    """Fetch a list of works matching the given filters.

    If ``sample_size`` is set, OpenAlex returns a random sample of that size
    (server-side, reproducible with ``seed``). Otherwise the first page of
    results is returned.
    """
    params: dict[str, Any] = {
        "filter": _build_filter_string(filters),
        "mailto": mailto,
    }
    if sample_size is not None:
        params["sample"] = sample_size
    if seed is not None:
        params["seed"] = seed
    if select:
        params["select"] = ",".join(select)
    if sample_size is not None:
        params["per-page"] = min(sample_size, 200)

    payload = _request_with_retry(f"{_BASE_URL}/works", params, max_retries)
    results = payload.get("results", [])
    assert isinstance(results, list)
    return results


def get_concept(
    concept_id: str,
    mailto: str = _DEFAULT_MAILTO,
    max_retries: int = 5,
) -> dict[str, Any]:
    """Fetch a single concept entity by ID (e.g., 'C41008148')."""
    params = {"mailto": mailto}
    return _request_with_retry(f"{_BASE_URL}/concepts/{concept_id}", params, max_retries)


def get_work(
    work_id: str,
    mailto: str = _DEFAULT_MAILTO,
    max_retries: int = 5,
) -> dict[str, Any]:
    """Fetch a single work by ID. Accepts bare 'W123' or full URL form."""
    bare_id = work_id.rsplit("/", 1)[-1] if "/" in work_id else work_id
    params = {"mailto": mailto}
    return _request_with_retry(f"{_BASE_URL}/works/{bare_id}", params, max_retries)


_ARXIV_SOURCE_ID = "https://openalex.org/S4306400194"
_ARXIV_DOI_PREFIX = "10.48550/arxiv."


def has_arxiv(work: dict[str, Any]) -> bool:
    """True if work has an arXiv linkage via location source or arXiv DOI."""
    locations = work.get("locations") or []
    for location in locations:
        source = location.get("source") if isinstance(location, dict) else None
        if isinstance(source, dict) and source.get("id") == _ARXIV_SOURCE_ID:
            return True
    ids = work.get("ids") or {}
    doi = ids.get("doi") if isinstance(ids, dict) else None
    if isinstance(doi, str) and _ARXIV_DOI_PREFIX in doi.lower():
        return True
    return False


def has_abstract(work: dict[str, Any]) -> bool:
    """True iff work has a non-empty abstract_inverted_index."""
    abstract = work.get("abstract_inverted_index")
    if abstract is None:
        return False
    if not isinstance(abstract, dict):
        return False
    return len(abstract) > 0


def extract_doi(work: dict[str, Any]) -> str | None:
    """Pull bare DOI string (no URL prefix) from a work record's ids.doi field."""
    ids = work.get("ids") or {}
    if not isinstance(ids, dict):
        return None
    doi = ids.get("doi")
    if not isinstance(doi, str):
        return None
    if doi.startswith("https://doi.org/"):
        return doi[len("https://doi.org/") :]
    if doi.startswith("http://doi.org/"):
        return doi[len("http://doi.org/") :]
    return doi


def extract_first_country(work: dict[str, Any]) -> str | None:
    """ISO country code of the first authorship's first non-empty institution.

    Walks authorships in order; for each, returns the first institution's
    country_code if available. Returns None if no authorship/institution has
    a country_code.
    """
    authorships = work.get("authorships") or []
    if not isinstance(authorships, list):
        return None
    for authorship in authorships:
        if not isinstance(authorship, dict):
            continue
        institutions = authorship.get("institutions") or []
        if not isinstance(institutions, list):
            continue
        for institution in institutions:
            if not isinstance(institution, dict):
                continue
            country = institution.get("country_code")
            if isinstance(country, str) and country:
                return country
    return None


def extract_top_concept_id(work: dict[str, Any], level: int = 0) -> str | None:
    """Bare concept ID (e.g., 'C41008148') of the highest-score concept at the
    given level, or None if no concept at that level.
    """
    concepts = work.get("concepts") or []
    if not isinstance(concepts, list):
        return None
    candidates = [
        c for c in concepts if isinstance(c, dict) and c.get("level") == level
    ]
    if not candidates:
        return None
    top = max(candidates, key=lambda c: c.get("score") or 0.0)
    raw_id = top.get("id")
    if not isinstance(raw_id, str):
        return None
    return raw_id.rsplit("/", 1)[-1] if "/" in raw_id else raw_id


def latest_snapshot_date() -> str:
    """Record the request-time as a snapshot proxy.

    OpenAlex's REST API does not expose snapshot-date pinning; bulk-dump
    access is required for true snapshot pinning per ws2 desideratum §1.
    Returns ISO-8601 UTC timestamp.
    """
    return datetime.now(timezone.utc).isoformat(timespec="seconds")
