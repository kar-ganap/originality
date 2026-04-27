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


def test_get_work_strips_url_prefix() -> None:
    payload = {"id": "https://openalex.org/W123", "publication_year": 2020}
    with patch("whitespace2.openalex.requests.Session.get") as mock_get:
        mock_get.return_value = _mock_response(200, payload)
        # Should accept either bare 'W123' or full URL form
        work = openalex.get_work("https://openalex.org/W123")
    assert work["id"] == "https://openalex.org/W123"
    call_args, _call_kwargs = mock_get.call_args
    url = call_args[0]
    assert url.endswith("/works/W123")


def test_get_work_bare_id() -> None:
    payload = {"id": "https://openalex.org/W456", "publication_year": 2010}
    with patch("whitespace2.openalex.requests.Session.get") as mock_get:
        mock_get.return_value = _mock_response(200, payload)
        openalex.get_work("W456")
    call_args, _call_kwargs = mock_get.call_args
    url = call_args[0]
    assert url.endswith("/works/W456")


def test_has_arxiv_via_location_source_id() -> None:
    work = {
        "id": "W1",
        "locations": [
            {"source": {"id": "https://openalex.org/S99999"}},
            {"source": {"id": "https://openalex.org/S4306400194"}},
        ],
    }
    assert openalex.has_arxiv(work) is True


def test_has_arxiv_via_arxiv_doi() -> None:
    work = {"id": "W1", "ids": {"doi": "https://doi.org/10.48550/arxiv.1706.03762"}}
    assert openalex.has_arxiv(work) is False or openalex.has_arxiv(work) is True
    # Disambiguate: implementation should treat arxiv DOI as positive signal.
    assert openalex.has_arxiv(work) is True


def test_has_arxiv_false_when_no_signal() -> None:
    work = {
        "id": "W1",
        "ids": {"doi": "https://doi.org/10.1145/12345"},
        "locations": [{"source": {"id": "https://openalex.org/S99999"}}],
    }
    assert openalex.has_arxiv(work) is False


def test_has_arxiv_false_when_empty() -> None:
    assert openalex.has_arxiv({"id": "W1"}) is False
    assert openalex.has_arxiv({"id": "W1", "locations": [], "ids": {}}) is False


def test_has_arxiv_handles_none_source() -> None:
    # Real OpenAlex responses sometimes have null source on a location.
    work = {"id": "W1", "locations": [{"source": None}, {"source": {"id": "https://openalex.org/S4306400194"}}]}
    assert openalex.has_arxiv(work) is True


def test_extract_doi_strips_url_prefix() -> None:
    work = {"ids": {"doi": "https://doi.org/10.48550/arxiv.1706.03762"}}
    assert openalex.extract_doi(work) == "10.48550/arxiv.1706.03762"


def test_extract_doi_handles_bare_doi() -> None:
    work = {"ids": {"doi": "10.1145/12345"}}
    assert openalex.extract_doi(work) == "10.1145/12345"


def test_extract_doi_returns_none_when_missing() -> None:
    assert openalex.extract_doi({"id": "W1"}) is None
    assert openalex.extract_doi({"id": "W1", "ids": {}}) is None
    assert openalex.extract_doi({"id": "W1", "ids": {"doi": None}}) is None


def test_extract_first_country_from_authorships() -> None:
    work = {
        "authorships": [
            {
                "institutions": [
                    {"country_code": "US", "display_name": "MIT"},
                    {"country_code": "GB", "display_name": "Cambridge"},
                ]
            },
            {"institutions": [{"country_code": "JP"}]},
        ]
    }
    assert openalex.extract_first_country(work) == "US"


def test_extract_first_country_handles_no_institutions() -> None:
    assert openalex.extract_first_country({"authorships": []}) is None
    assert openalex.extract_first_country({"authorships": [{"institutions": []}]}) is None
    assert openalex.extract_first_country({"id": "W1"}) is None


def test_extract_first_country_skips_empty_institution_to_next_authorship() -> None:
    work = {
        "authorships": [
            {"institutions": []},
            {"institutions": [{"country_code": "DE"}]},
        ]
    }
    assert openalex.extract_first_country(work) == "DE"


def test_extract_top_concept_id_picks_highest_score_at_target_level() -> None:
    work = {
        "concepts": [
            {"id": "https://openalex.org/C1", "level": 0, "score": 0.5, "display_name": "low"},
            {"id": "https://openalex.org/C2", "level": 0, "score": 0.9, "display_name": "high"},
            {"id": "https://openalex.org/C3", "level": 1, "score": 0.99, "display_name": "deeper"},
        ]
    }
    assert openalex.extract_top_concept_id(work, level=0) == "C2"


def test_extract_top_concept_id_returns_none_when_no_match() -> None:
    work = {
        "concepts": [
            {"id": "https://openalex.org/C3", "level": 2, "score": 0.99},
        ]
    }
    assert openalex.extract_top_concept_id(work, level=0) is None
    assert openalex.extract_top_concept_id({"concepts": []}, level=0) is None
    assert openalex.extract_top_concept_id({"id": "W1"}, level=0) is None


def test_fetch_works_passes_sort_param() -> None:
    payload = {"results": [], "meta": {"count": 0}}
    with patch("whitespace2.openalex.requests.Session.get") as mock_get:
        mock_get.return_value = _mock_response(200, payload)
        openalex.fetch_works(
            filters={"publication_year": "1990"},
            sort="publication_year:asc",
        )
    _call_args, call_kwargs = mock_get.call_args
    params = call_kwargs.get("params") or {}
    assert params["sort"] == "publication_year:asc"


def test_search_concepts_returns_results() -> None:
    payload = {
        "results": [
            {
                "id": "https://openalex.org/C108583219",
                "display_name": "Deep learning",
                "level": 2,
                "works_count": 12345,
            },
            {
                "id": "https://openalex.org/C999999",
                "display_name": "Deep learning theory",
                "level": 3,
                "works_count": 100,
            },
        ]
    }
    with patch("whitespace2.openalex.requests.Session.get") as mock_get:
        mock_get.return_value = _mock_response(200, payload)
        results = openalex.search_concepts("deep learning")
    assert len(results) == 2
    assert results[0]["display_name"] == "Deep learning"
    _call_args, call_kwargs = mock_get.call_args
    params = call_kwargs.get("params") or {}
    assert params["search"] == "deep learning"


def test_search_concepts_returns_empty_when_no_match() -> None:
    payload = {"results": []}
    with patch("whitespace2.openalex.requests.Session.get") as mock_get:
        mock_get.return_value = _mock_response(200, payload)
        results = openalex.search_concepts("nonexistent gibberish term xyz")
    assert results == []
