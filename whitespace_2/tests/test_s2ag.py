"""Tests for the Semantic Scholar (S2AG) REST client (whitespace2.s2ag).

All tests mock requests.Session.post; no live HTTP traffic.
"""

from __future__ import annotations

import os
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from whitespace2 import s2ag


def _mock_response(status_code: int, json_data: Any = None) -> MagicMock:
    response = MagicMock()
    response.status_code = status_code
    response.json.return_value = json_data if json_data is not None else []
    response.headers = {}
    return response


def test_batch_lookup_basic() -> None:
    payload = [
        {"paperId": "abc123", "abstract": "Hello world.", "year": 2020},
        {"paperId": "def456", "abstract": "Another paper.", "year": 2021},
    ]
    with patch("whitespace2.s2ag.requests.Session.post") as mock_post:
        mock_post.return_value = _mock_response(200, payload)
        result = s2ag.batch_lookup(["DOI:10.x/y", "DOI:10.a/b"])
    assert len(result) == 2
    assert result[0] is not None
    assert result[0]["paperId"] == "abc123"
    assert result[1] is not None
    assert result[1]["paperId"] == "def456"


def test_batch_lookup_chunks_over_500() -> None:
    ids = [f"DOI:10.x/{i}" for i in range(750)]
    payload_chunk1 = [{"paperId": f"p{i}"} for i in range(500)]
    payload_chunk2 = [{"paperId": f"p{i}"} for i in range(500, 750)]
    responses = [_mock_response(200, payload_chunk1), _mock_response(200, payload_chunk2)]
    with patch("whitespace2.s2ag.requests.Session.post", side_effect=responses) as mock_post:
        result = s2ag.batch_lookup(ids)
    assert mock_post.call_count == 2
    assert len(result) == 750


def test_batch_lookup_returns_none_for_unfound() -> None:
    payload = [{"paperId": "abc"}, None, {"paperId": "def"}]
    with patch("whitespace2.s2ag.requests.Session.post") as mock_post:
        mock_post.return_value = _mock_response(200, payload)
        result = s2ag.batch_lookup(["DOI:1", "DOI:2", "DOI:3"])
    assert result[0] is not None
    assert result[1] is None
    assert result[2] is not None


def test_batch_lookup_includes_fields_param() -> None:
    payload = [{"paperId": "abc"}]
    with patch("whitespace2.s2ag.requests.Session.post") as mock_post:
        mock_post.return_value = _mock_response(200, payload)
        s2ag.batch_lookup(["DOI:10.x/y"], fields=["paperId", "abstract", "externalIds"])
    _call_args, call_kwargs = mock_post.call_args
    # fields appear as comma-joined string either in JSON body or query params.
    body = call_kwargs.get("json") or {}
    params = call_kwargs.get("params") or {}
    fields_value = params.get("fields") or body.get("fields") or ""
    assert "abstract" in fields_value
    assert "paperId" in fields_value


def test_batch_lookup_retry_on_429() -> None:
    payload = [{"paperId": "abc"}]
    responses = [_mock_response(429), _mock_response(200, payload)]
    with (
        patch("whitespace2.s2ag.requests.Session.post", side_effect=responses) as mock_post,
        patch("whitespace2.s2ag.time.sleep"),
    ):
        result = s2ag.batch_lookup(["DOI:10.x/y"])
    assert mock_post.call_count == 2
    assert result == [{"paperId": "abc"}]


def test_batch_lookup_retry_on_5xx() -> None:
    payload = [{"paperId": "abc"}]
    responses = [_mock_response(503), _mock_response(200, payload)]
    with (
        patch("whitespace2.s2ag.requests.Session.post", side_effect=responses) as mock_post,
        patch("whitespace2.s2ag.time.sleep"),
    ):
        result = s2ag.batch_lookup(["DOI:10.x/y"])
    assert mock_post.call_count == 2
    assert result == [{"paperId": "abc"}]


def test_batch_lookup_max_retries_exceeded() -> None:
    responses = [_mock_response(429) for _ in range(10)]
    with (
        patch("whitespace2.s2ag.requests.Session.post", side_effect=responses) as mock_post,
        patch("whitespace2.s2ag.time.sleep"),
        pytest.raises(RuntimeError),
    ):
        s2ag.batch_lookup(["DOI:10.x/y"], max_retries=3)
    assert mock_post.call_count == 3


def test_batch_lookup_uses_api_key_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SEMANTIC_SCHOLAR_API_KEY", "test-key-abc")
    payload = [{"paperId": "abc"}]
    with patch("whitespace2.s2ag.requests.Session.post") as mock_post:
        mock_post.return_value = _mock_response(200, payload)
        s2ag.batch_lookup(["DOI:10.x/y"])
    _call_args, call_kwargs = mock_post.call_args
    headers = call_kwargs.get("headers") or {}
    assert headers.get("x-api-key") == "test-key-abc"


def test_batch_lookup_no_api_key_header_when_unset(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("SEMANTIC_SCHOLAR_API_KEY", raising=False)
    payload = [{"paperId": "abc"}]
    with patch("whitespace2.s2ag.requests.Session.post") as mock_post:
        mock_post.return_value = _mock_response(200, payload)
        s2ag.batch_lookup(["DOI:10.x/y"])
    _call_args, call_kwargs = mock_post.call_args
    headers = call_kwargs.get("headers") or {}
    assert "x-api-key" not in headers


def test_has_abstract_true_for_nonempty_string() -> None:
    paper = {"paperId": "abc", "abstract": "This is an abstract."}
    assert s2ag.has_abstract(paper) is True


def test_has_abstract_false_for_null_paper() -> None:
    assert s2ag.has_abstract(None) is False


def test_has_abstract_false_for_missing_field() -> None:
    paper = {"paperId": "abc"}
    assert s2ag.has_abstract(paper) is False


def test_has_abstract_false_for_empty_string() -> None:
    paper = {"paperId": "abc", "abstract": ""}
    assert s2ag.has_abstract(paper) is False


def test_has_abstract_false_for_explicit_null() -> None:
    paper = {"paperId": "abc", "abstract": None}
    assert s2ag.has_abstract(paper) is False


# Sanity: the env var is cleaned up between tests.
def test_no_global_api_key_leakage(monkeypatch: pytest.MonkeyPatch) -> None:
    # If an earlier test left SEMANTIC_SCHOLAR_API_KEY set globally, this would fail.
    monkeypatch.delenv("SEMANTIC_SCHOLAR_API_KEY", raising=False)
    assert os.environ.get("SEMANTIC_SCHOLAR_API_KEY") is None
