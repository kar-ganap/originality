"""Semantic Scholar Academic Graph (S2AG) REST client.

Function-based, mirrors the openalex.py house pattern. Anonymous tier is
1000 RPS shared (per S2AG docs); exponential backoff on 429/5xx; raises
RuntimeError on other 4xx and on max-retries exhaustion.

If the env var ``SEMANTIC_SCHOLAR_API_KEY`` is set, requests include the
corresponding ``x-api-key`` header. Otherwise anonymous.
"""

from __future__ import annotations

import os
import time
from datetime import datetime, timezone
from typing import Any

import requests

_BASE_URL = "https://api.semanticscholar.org/graph/v1"
_USER_AGENT = "ws2/0.0.0 (https://github.com/kgkartik/originality)"
_BATCH_MAX = 500


def _build_headers() -> dict[str, str]:
    headers = {"User-Agent": _USER_AGENT}
    api_key = os.environ.get("SEMANTIC_SCHOLAR_API_KEY")
    if api_key:
        headers["x-api-key"] = api_key
    return headers


def _post_with_retry(
    url: str,
    body: dict[str, Any],
    params: dict[str, Any] | None,
    max_retries: int,
) -> Any:
    session = requests.Session()
    last_status: int | None = None
    headers = _build_headers()
    for attempt in range(max_retries):
        response = session.post(
            url,
            json=body,
            params=params or {},
            headers=headers,
            timeout=60,
        )
        last_status = response.status_code
        if response.status_code == 200:
            return response.json()
        if response.status_code == 429 or 500 <= response.status_code < 600:
            time.sleep(2**attempt)
            continue
        raise RuntimeError(f"S2AG returned {response.status_code} (no retry); url={url}")
    raise RuntimeError(
        f"S2AG max_retries={max_retries} exceeded; last status={last_status}; url={url}"
    )


def batch_lookup(
    paper_ids: list[str],
    fields: list[str] | None = None,
    max_retries: int = 5,
) -> list[dict[str, Any] | None]:
    """Look up papers in S2AG by external ID. Returns one entry per input
    ID, in order. Entries are None when S2AG returns null (paper not found).

    Each ID should be prefixed: 'DOI:10.x/y', 'ARXIV:1234.5678', etc.
    Batches over 500 are chunked transparently.
    """
    url = f"{_BASE_URL}/paper/batch"
    params: dict[str, Any] = {}
    if fields:
        params["fields"] = ",".join(fields)
    results: list[dict[str, Any] | None] = []
    for start in range(0, len(paper_ids), _BATCH_MAX):
        chunk = paper_ids[start : start + _BATCH_MAX]
        body: dict[str, Any] = {"ids": chunk}
        chunk_result = _post_with_retry(url, body, params, max_retries)
        if not isinstance(chunk_result, list):
            raise RuntimeError(f"S2AG batch returned non-list payload: {type(chunk_result)}")
        if len(chunk_result) != len(chunk):
            raise RuntimeError(
                f"S2AG batch returned {len(chunk_result)} entries for {len(chunk)} inputs"
            )
        for entry in chunk_result:
            if entry is None or isinstance(entry, dict):
                results.append(entry)
            else:
                results.append(None)
    return results


def has_abstract(paper: dict[str, Any] | None) -> bool:
    """True iff paper is non-None and 'abstract' is a non-empty string."""
    if paper is None:
        return False
    abstract = paper.get("abstract")
    if not isinstance(abstract, str):
        return False
    return len(abstract) > 0


def latest_snapshot_date() -> str:
    """Record the request-time as a snapshot proxy.

    S2AG's REST API does not expose snapshot-date pinning. Returns ISO-8601
    UTC timestamp.
    """
    return datetime.now(timezone.utc).isoformat(timespec="seconds")
