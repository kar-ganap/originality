"""Tests for the OpenAlex REST client (whitespace2.openalex).

All tests mock requests.Session.get; no live HTTP traffic.
"""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from whitespace2 import openalex


def _mock_response(status_code: int, json_data: dict[str, Any] | None = None) -> MagicMock:
    response = MagicMock()
    response.status_code = status_code
    response.json.return_value = json_data if json_data is not None else {}
    response.headers = {}
    return response


def test_fetch_works_basic() -> None:
    payload = {
        "results": [
            {"id": "W1", "publication_year": 1990, "abstract_inverted_index": {"hello": [0]}},
            {"id": "W2", "publication_year": 1990, "abstract_inverted_index": None},
        ],
        "meta": {"count": 2},
    }
    with patch("whitespace2.openalex.requests.Session.get") as mock_get:
        mock_get.return_value = _mock_response(200, payload)
        works = openalex.fetch_works(filters={"publication_year": "1990"})
    assert isinstance(works, list)
    assert len(works) == 2
    assert works[0]["id"] == "W1"
    assert works[1]["abstract_inverted_index"] is None


def test_fetch_works_passes_filters_and_sample() -> None:
    payload = {"results": [], "meta": {"count": 0}}
    with patch("whitespace2.openalex.requests.Session.get") as mock_get:
        mock_get.return_value = _mock_response(200, payload)
        openalex.fetch_works(
            filters={"concepts.id": "C41008148", "publication_year": "1990"},
            sample_size=200,
            seed=42,
            select=["id", "publication_year", "abstract_inverted_index"],
            mailto="test@example.com",
        )
    assert mock_get.call_count == 1
    call_args, call_kwargs = mock_get.call_args
    params = call_kwargs.get("params") or (call_args[1] if len(call_args) > 1 else {})
    filter_str = params["filter"]
    assert "concepts.id:C41008148" in filter_str
    assert "publication_year:1990" in filter_str
    assert params["sample"] == 200
    assert params["seed"] == 42
    assert params["mailto"] == "test@example.com"
    assert params["select"] == "id,publication_year,abstract_inverted_index"


def test_fetch_works_retry_on_429() -> None:
    payload_ok = {"results": [{"id": "W1"}], "meta": {"count": 1}}
    responses = [_mock_response(429), _mock_response(200, payload_ok)]
    with (
        patch("whitespace2.openalex.requests.Session.get", side_effect=responses) as mock_get,
        patch("whitespace2.openalex.time.sleep"),
    ):
        works = openalex.fetch_works(filters={"publication_year": "1990"})
    assert mock_get.call_count == 2
    assert works == [{"id": "W1"}]


def test_fetch_works_retry_on_5xx() -> None:
    payload_ok = {"results": [{"id": "W1"}], "meta": {"count": 1}}
    responses = [_mock_response(503), _mock_response(200, payload_ok)]
    with (
        patch("whitespace2.openalex.requests.Session.get", side_effect=responses) as mock_get,
        patch("whitespace2.openalex.time.sleep"),
    ):
        works = openalex.fetch_works(filters={"publication_year": "1990"})
    assert mock_get.call_count == 2
    assert works == [{"id": "W1"}]


def test_fetch_works_max_retries_exceeded() -> None:
    responses = [_mock_response(429) for _ in range(10)]
    with (
        patch("whitespace2.openalex.requests.Session.get", side_effect=responses) as mock_get,
        patch("whitespace2.openalex.time.sleep"),
        pytest.raises(RuntimeError),
    ):
        openalex.fetch_works(filters={"publication_year": "1990"}, max_retries=3)
    assert mock_get.call_count == 3


def test_fetch_works_no_retry_on_4xx_other_than_429() -> None:
    responses = [_mock_response(400)]
    with (
        patch("whitespace2.openalex.requests.Session.get", side_effect=responses) as mock_get,
        patch("whitespace2.openalex.time.sleep"),
        pytest.raises(RuntimeError),
    ):
        openalex.fetch_works(filters={"publication_year": "1990"})
    assert mock_get.call_count == 1


def test_has_abstract_true_for_nonempty_inverted_index() -> None:
    work = {"id": "W1", "abstract_inverted_index": {"hello": [0], "world": [1]}}
    assert openalex.has_abstract(work) is True


def test_has_abstract_false_for_null() -> None:
    work = {"id": "W1", "abstract_inverted_index": None}
    assert openalex.has_abstract(work) is False


def test_has_abstract_false_for_missing_key() -> None:
    work = {"id": "W1"}
    assert openalex.has_abstract(work) is False


def test_has_abstract_false_for_empty_dict() -> None:
    work = {"id": "W1", "abstract_inverted_index": {}}
    assert openalex.has_abstract(work) is False


def test_get_concept() -> None:
    payload = {
        "id": "https://openalex.org/C41008148",
        "display_name": "Computer science",
        "level": 0,
        "works_count": 1234567,
    }
    with patch("whitespace2.openalex.requests.Session.get") as mock_get:
        mock_get.return_value = _mock_response(200, payload)
        concept = openalex.get_concept("C41008148")
    assert concept["display_name"] == "Computer science"
    assert concept["level"] == 0
