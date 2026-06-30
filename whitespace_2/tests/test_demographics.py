"""Unit tests for demographic-annotation pipeline (Phase 1.3).

§4 of `docs/desiderata.md` constrains the demographic-inference
stack:

- Gender: gender_guesser primary, Genderize cross-validation,
  NamSor sample-based bias estimation per Phase 1.3 plan §3.
- Country: extracted from ``authorships[*].countries`` (preferred)
  or ``authorships[*].institutions[*].country_code`` (fallback).
- Coverage + sensitivity bounds per cell.

Step 1 covers author-records extraction; subsequent steps cover
gender + country annotation, NamSor stratified sampling, bias
correction, and the per-cell coverage table.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pyarrow as pa
import pyarrow.parquet as pq

from whitespace2.demographics import (
    _extract_first_name,
    _extract_source_type,
    explode_authorships_for_paper,
    extract_authorships,
)

# ---------- helpers for building test author records ----------


def _make_author(
    *,
    author_id: str = "https://openalex.org/A5000000001",
    display_name: str = "John Q. Public",
    orcid: str | None = "https://orcid.org/0000-0000-0000-0001",
    position: str = "first",
    is_corresponding: bool = True,
    countries: list[str] | None = None,
    institutions: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    return {
        "author": {
            "display_name": display_name,
            "id": author_id,
            "orcid": orcid,
        },
        "author_position": position,
        "is_corresponding": is_corresponding,
        "countries": countries if countries is not None else ["US"],
        "institutions": institutions if institutions is not None else [
            {"country_code": "US", "display_name": "Test Univ",
             "id": "https://openalex.org/I0001"},
        ],
        "raw_author_name": display_name,
        "affiliations": [],
        "raw_affiliation_strings": [],
    }


def _make_paper(
    *,
    paper_id: str = "https://openalex.org/W1000000001",
    year: int | None = 2020,
    authorships: list[dict[str, Any]] | None = None,
    source_type: str | None = "journal",
) -> dict[str, Any]:
    if authorships is None:
        authorships = [_make_author()]
    primary_location: dict[str, Any] | None
    if source_type is not None:
        primary_location = {
            "source": {
                "type": source_type,
                "display_name": "Test Venue",
                "id": "https://openalex.org/S0001",
            },
        }
    else:
        primary_location = None
    return {
        "id": paper_id,
        "publication_year": year,
        "authorships_json": json.dumps(authorships),
        "primary_location_json": (
            json.dumps(primary_location)
            if primary_location is not None
            else None
        ),
    }


# ---------- _extract_first_name ----------


def test_extract_first_name_handles_full_name() -> None:
    """Full first name + middle initial + last → first token returned."""
    assert _extract_first_name("Thomas A. Brubaker") == ("Thomas", False)
    assert _extract_first_name("Jane Doe") == ("Jane", False)
    assert _extract_first_name("Hiroshi Tanaka") == ("Hiroshi", False)


def test_extract_first_name_flags_initials() -> None:
    """Single-letter or 2-letter first tokens are flagged as initials."""
    # "C.F. Gauss" → first token "C.F.", strip period → "C.F" (3 chars,
    # not flagged). Actually with two periods we get tokens ["C.F.", "Gauss"]
    # → strip trailing period → "C.F". Let's check both behaviours.
    # For the simple case:
    assert _extract_first_name("C. Gauss") == ("C", True)
    assert _extract_first_name("J Doe") == ("J", True)
    # Two-letter initial (e.g., "CF Gauss"):
    assert _extract_first_name("CF Gauss") == ("CF", True)


def test_extract_first_name_handles_missing_or_empty() -> None:
    """None, empty, whitespace, non-string → (empty, False)."""
    assert _extract_first_name(None) == ("", False)
    assert _extract_first_name("") == ("", False)
    assert _extract_first_name("   ") == ("", False)
    assert _extract_first_name(42) == ("", False)  # type: ignore[arg-type]


# ---------- _extract_source_type ----------


def test_extract_source_type_valid_journal() -> None:
    """Well-formed primary_location_json → source.type returned."""
    pl = json.dumps({"source": {"type": "journal", "display_name": "X"}})
    assert _extract_source_type(pl) == "journal"

    pl_repo = json.dumps({"source": {"type": "repository", "display_name": "arXiv"}})
    assert _extract_source_type(pl_repo) == "repository"


def test_extract_source_type_handles_missing_or_malformed() -> None:
    """None / empty / malformed / missing-source / missing-type → None."""
    assert _extract_source_type(None) is None
    assert _extract_source_type("") is None
    assert _extract_source_type("{not json") is None
    assert _extract_source_type("[]") is None  # wrong shape
    assert _extract_source_type(json.dumps({"source": None})) is None
    assert _extract_source_type(json.dumps({"source": {}})) is None
    assert _extract_source_type(
        json.dumps({"source": {"type": None}}),
    ) is None
    assert _extract_source_type(json.dumps({})) is None  # no source key


# ---------- explode_authorships_for_paper ----------


def test_explode_authorships_produces_one_row_per_author_paper() -> None:
    """A paper with N authors → exactly N rows, each with
    paper_id + author fields. Matches the pre-registered H1 test
    pattern from the plan.
    """
    paper = _make_paper(
        paper_id="https://openalex.org/W42",
        year=2022,
        authorships=[
            _make_author(author_id="https://openalex.org/A1",
                         display_name="Alice Smith"),
            _make_author(author_id="https://openalex.org/A2",
                         display_name="Bob Jones", position="middle",
                         is_corresponding=False),
            _make_author(author_id="https://openalex.org/A3",
                         display_name="Carol Tan", position="last",
                         is_corresponding=False),
        ],
    )
    rows = explode_authorships_for_paper(paper)
    assert len(rows) == 3
    assert all(r["paper_id"] == "https://openalex.org/W42" for r in rows)
    assert all(r["publication_year"] == 2022 for r in rows)
    assert all(r["source_type"] == "journal" for r in rows)
    assert [r["author_id"] for r in rows] == [
        "https://openalex.org/A1",
        "https://openalex.org/A2",
        "https://openalex.org/A3",
    ]
    assert [r["author_first_name"] for r in rows] == ["Alice", "Bob", "Carol"]
    assert [r["author_position"] for r in rows] == ["first", "middle", "last"]
    assert [r["is_corresponding"] for r in rows] == [True, False, False]


def test_explode_authorships_carries_repository_source_type() -> None:
    """Repository / preprint papers get source_type='repository' per row."""
    paper = _make_paper(
        source_type="repository",
        authorships=[
            _make_author(author_id="https://openalex.org/A1"),
            _make_author(author_id="https://openalex.org/A2"),
        ],
    )
    rows = explode_authorships_for_paper(paper)
    assert len(rows) == 2
    assert all(r["source_type"] == "repository" for r in rows)


def test_explode_authorships_carries_none_source_type_when_missing() -> None:
    """Missing primary_location_json → source_type=None on all rows."""
    paper = _make_paper(
        source_type=None,  # primary_location_json will be None
        authorships=[_make_author(author_id="https://openalex.org/A1")],
    )
    rows = explode_authorships_for_paper(paper)
    assert len(rows) == 1
    assert rows[0]["source_type"] is None


def test_explode_authorships_skips_author_without_id() -> None:
    """Authors lacking a stable id (the disambiguation key) are
    dropped — they can't be tracked across papers.
    """
    paper = _make_paper(
        authorships=[
            _make_author(author_id="https://openalex.org/A1"),
            {
                "author": {"display_name": "No ID Anon", "id": None,
                           "orcid": None},
                "author_position": "middle",
                "is_corresponding": False,
                "countries": [], "institutions": [],
            },
        ],
    )
    rows = explode_authorships_for_paper(paper)
    assert len(rows) == 1
    assert rows[0]["author_id"] == "https://openalex.org/A1"


def test_explode_authorships_handles_empty_or_malformed_json() -> None:
    """Missing / malformed authorships_json → empty list, no exception."""
    # None
    p = _make_paper()
    p["authorships_json"] = None  # type: ignore[assignment]
    assert explode_authorships_for_paper(p) == []
    # Empty string
    p["authorships_json"] = ""
    assert explode_authorships_for_paper(p) == []
    # Malformed JSON
    p["authorships_json"] = "{not json"
    assert explode_authorships_for_paper(p) == []
    # Valid JSON but wrong shape (e.g., dict instead of list)
    p["authorships_json"] = "{}"
    assert explode_authorships_for_paper(p) == []
    # Empty list
    p["authorships_json"] = "[]"
    assert explode_authorships_for_paper(p) == []


def test_explode_authorships_preserves_orcid_and_countries() -> None:
    """ORCID + countries pass through verbatim."""
    paper = _make_paper(
        authorships=[
            _make_author(
                author_id="https://openalex.org/A1",
                orcid="https://orcid.org/0000-0002-5444-8105",
                countries=["US", "JP"],
            ),
            _make_author(
                author_id="https://openalex.org/A2",
                orcid=None,
                countries=[],
            ),
        ],
    )
    rows = explode_authorships_for_paper(paper)
    assert rows[0]["author_orcid"] == "https://orcid.org/0000-0002-5444-8105"
    assert rows[0]["countries"] == ["US", "JP"]
    assert rows[1]["author_orcid"] is None
    assert rows[1]["countries"] == []


# ---------- extract_authorships (parquet streaming) ----------


def test_extract_authorships_writes_parquet_with_expected_shape(
    tmp_path: Path,
) -> None:
    """End-to-end: write a 3-paper synthetic input parquet, run
    extract_authorships, verify the output parquet has the right
    row count + columns.
    """
    # Build synthetic input matching v3 schema
    papers = [
        _make_paper(
            paper_id=f"https://openalex.org/W{i}",
            year=2000 + i,
            authorships=[
                _make_author(
                    author_id=f"https://openalex.org/A{i}_{j}",
                    display_name=f"Author{i}_{j} Surname",
                )
                for j in range(1 + i)  # paper 0 has 1 author, paper 1 has 2, paper 2 has 3
            ],
        )
        for i in range(3)
    ]
    src = tmp_path / "input.parquet"
    tbl = pa.Table.from_pylist(papers)
    pq.write_table(tbl, str(src), compression="zstd")

    dst = tmp_path / "output.parquet"
    result = extract_authorships(src, dst, batch_size=2)

    assert result["n_papers"] == 3
    assert result["n_author_paper_rows"] == 1 + 2 + 3  # = 6

    # Output parquet shape
    out_tbl = pq.read_table(str(dst))
    assert out_tbl.num_rows == 6
    cols = set(out_tbl.column_names)
    assert {"paper_id", "publication_year", "source_type", "author_id",
            "author_first_name", "author_position",
            "is_corresponding", "author_orcid", "countries"}.issubset(cols)


def test_extract_authorships_handles_no_authors_papers(
    tmp_path: Path,
) -> None:
    """Papers with empty authorships_json → 0 rows but pipeline
    doesn't error. Writer is only created if there's at least one
    row to write.
    """
    papers = [_make_paper(paper_id="https://openalex.org/W1", authorships=[])]
    src = tmp_path / "in.parquet"
    pq.write_table(pa.Table.from_pylist(papers), str(src))

    dst = tmp_path / "out.parquet"
    result = extract_authorships(src, dst, batch_size=10)
    assert result["n_papers"] == 1
    assert result["n_author_paper_rows"] == 0
    # No output parquet created (acceptable; documented behaviour)
    assert not dst.exists()
