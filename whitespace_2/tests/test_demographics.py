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
    _gg_label_to_gender_probability,
    aggregate_per_author,
    annotate_gender_country,
    annotate_with_gender_guesser,
    combine_gg_and_genderize,
    compute_career_length_screen,
    compute_orcid_consistency,
    explode_authorships_for_paper,
    extract_authorships,
    query_genderize,
    query_genderize_batch,
    query_namsor,
    query_namsor_batch,
    sample_for_namsor,
    stratified_sample_names,
    tag_script_region,
    validate_disambiguation,
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


# ---------- disambiguation validation (Step 2) ----------


def _make_author_rows(
    rows: list[tuple[str, int | None, str | None]],
) -> pa.Table:
    """Build a per-author-paper Arrow table from
    (author_id, publication_year, author_orcid) tuples.

    Used by Step 2 tests to construct mock authorship inputs.
    """
    return pa.table({
        "author_id": [r[0] for r in rows],
        "publication_year": [r[1] for r in rows],
        "author_orcid": [r[2] for r in rows],
    })


def test_career_length_screen_flags_long_careers() -> None:
    """Authors whose papers span >threshold years get flagged."""
    rows = [
        # author A1: papers 1980, 2020 (40-year career) — NOT flagged
        ("https://openalex.org/A1", 1980, None),
        ("https://openalex.org/A1", 2020, None),
        # author A2: papers 1950, 2020 (70-year career) — flagged
        ("https://openalex.org/A2", 1950, None),
        ("https://openalex.org/A2", 2020, None),
        # author A3: 1 paper (career=0) — NOT flagged
        ("https://openalex.org/A3", 2010, None),
    ]
    table = _make_author_rows(rows)
    result = compute_career_length_screen(table, threshold=60)

    assert result["n_unique_authors"] == 3
    assert result["n_flagged_cross_era_merger"] == 1
    assert result["flagged_fraction"] == 1 / 3


def test_career_length_screen_handles_missing_years() -> None:
    """Authors with no publication_year are excluded from the screen."""
    rows = [
        ("https://openalex.org/A1", None, None),
        ("https://openalex.org/A1", 2020, None),
        ("https://openalex.org/A2", None, None),  # only None-year paper
    ]
    table = _make_author_rows(rows)
    result = compute_career_length_screen(table, threshold=60)
    # A1 contributes (only the non-null year); A2 has no valid year → excluded
    assert result["n_unique_authors"] == 1
    assert result["n_flagged_cross_era_merger"] == 0


def test_orcid_consistency_perfect_agreement() -> None:
    """Every ORCID maps to exactly 1 author.id → consistency rate = 1.0."""
    rows = [
        ("https://openalex.org/A1", 2020,
         "https://orcid.org/0000-0001-0000-0001"),
        ("https://openalex.org/A1", 2021,
         "https://orcid.org/0000-0001-0000-0001"),
        ("https://openalex.org/A2", 2020,
         "https://orcid.org/0000-0001-0000-0002"),
    ]
    table = _make_author_rows(rows)
    result = compute_orcid_consistency(table)

    assert result["n_paper_rows_with_orcid"] == 3
    assert result["n_unique_orcids"] == 2
    assert result["n_orcids_consistent"] == 2
    assert result["n_orcids_inconsistent"] == 0
    assert result["orcid_consistency_rate"] == 1.0
    assert result["paper_level_agreement_rate"] == 1.0


def test_orcid_consistency_with_split_author() -> None:
    """One ORCID mapping to two author.ids → consistency rate < 1.0.

    Models OpenAlex disambiguation splitting a real author into 2 IDs.
    Paper-level agreement = papers on the dominant author.id /
    total ORCID-tagged papers.
    """
    rows = [
        # ORCID #1 maps to A1 (3 papers) AND A2 (1 paper) — A1 dominant
        ("https://openalex.org/A1", 2020,
         "https://orcid.org/0000-0001-0000-0001"),
        ("https://openalex.org/A1", 2021,
         "https://orcid.org/0000-0001-0000-0001"),
        ("https://openalex.org/A1", 2022,
         "https://orcid.org/0000-0001-0000-0001"),
        ("https://openalex.org/A2", 2023,
         "https://orcid.org/0000-0001-0000-0001"),
        # ORCID #2 maps to A3 (consistent)
        ("https://openalex.org/A3", 2020,
         "https://orcid.org/0000-0001-0000-0002"),
    ]
    table = _make_author_rows(rows)
    result = compute_orcid_consistency(table)

    assert result["n_paper_rows_with_orcid"] == 5
    assert result["n_unique_orcids"] == 2
    assert result["n_orcids_consistent"] == 1  # ORCID #2 only
    assert result["n_orcids_inconsistent"] == 1
    assert result["orcid_consistency_rate"] == 0.5
    # paper-level: 4 of 5 papers are on the dominant pairing
    # (3 A1↔ORCID1, 1 A3↔ORCID2; A2↔ORCID1 disagrees)
    assert result["paper_level_agreement_rate"] == 4 / 5


def test_orcid_consistency_filters_nulls() -> None:
    """Rows with null author_orcid or null author_id are excluded."""
    rows = [
        ("https://openalex.org/A1", 2020,
         "https://orcid.org/0000-0001-0000-0001"),
        ("https://openalex.org/A2", 2020, None),  # no orcid
        (None, 2020,                              # type: ignore[list-item]
         "https://orcid.org/0000-0001-0000-0002"),  # no author_id
    ]
    table = _make_author_rows(rows)
    result = compute_orcid_consistency(table)
    # Only the first row is analyzable
    assert result["n_paper_rows_with_orcid"] == 1
    assert result["n_unique_orcids"] == 1


def test_validate_disambiguation_e2e(tmp_path: Path) -> None:
    """Write a mock authorships parquet, run validate_disambiguation,
    verify output JSON has the expected H1+H2 fields and verdicts.
    """
    rows = [
        # 4 authors with normal careers (none flagged); 1 with 70yr career (flagged)
        ("https://openalex.org/A1", 2010, "https://orcid.org/0000-1"),
        ("https://openalex.org/A1", 2020, "https://orcid.org/0000-1"),
        ("https://openalex.org/A2", 2015, None),
        ("https://openalex.org/A3", 2018,
         "https://orcid.org/0000-2"),
        ("https://openalex.org/A4", 2020, None),
        ("https://openalex.org/A5", 1950, None),  # 70-year career → flagged
        ("https://openalex.org/A5", 2020, None),
    ]
    table = _make_author_rows(rows)
    src = tmp_path / "authorships.parquet"
    pq.write_table(table, str(src))
    out = tmp_path / "validation.json"

    result = validate_disambiguation(src, out, career_length_threshold=60)

    assert out.exists()
    # H1
    assert result["h1_career_length_screen"]["n_unique_authors"] == 5
    assert result["h1_career_length_screen"]["n_flagged_cross_era_merger"] == 1
    assert result["h1_career_length_screen"]["flagged_fraction"] == 1 / 5
    # H1 acceptance: 20% flagged is > 5%; should NOT pass
    assert result["h1_passes"] is False

    # H2: 2 orcid-tagged authors, both consistent
    assert result["h2_orcid_consistency"]["orcid_consistency_rate"] == 1.0
    assert result["h2_passes"] is True

    # JSON loadable
    loaded = json.loads(out.read_text())
    assert loaded["h1_career_length_screen"]["n_unique_authors"] == 5


# ---------- gender_guesser annotation (Step 3a) ----------


def test_gg_label_to_gender_probability_mapping() -> None:
    """gender_guesser's 6-class labels → (gender, probability) tuples.

    Mapping (per Phase 1.3 plan §"Gender stack"):
      male / female    → confident (p=1.0)
      mostly_*         → mid (p=0.7)
      andy             → unknown (p=0.0; ambiguous unisex name)
      unknown          → unknown (p=0.0; not in gender_guesser's dictionary)
    """
    assert _gg_label_to_gender_probability("male") == ("male", 1.0)
    assert _gg_label_to_gender_probability("female") == ("female", 1.0)
    assert _gg_label_to_gender_probability("mostly_male") == ("male", 0.7)
    assert _gg_label_to_gender_probability("mostly_female") == ("female", 0.7)
    assert _gg_label_to_gender_probability("andy") == ("unknown", 0.0)
    assert _gg_label_to_gender_probability("unknown") == ("unknown", 0.0)
    # Defensive: any other string → unknown
    assert _gg_label_to_gender_probability("bogus") == ("unknown", 0.0)


def test_annotate_with_gender_guesser_known_names() -> None:
    """Known names from the smoke: John → male, Mary → mostly_female,
    Hiroshi → male, Wei → andy (Asian unisex), Asdfg → unknown.

    Returns dict[first_name → {gg_label, gender, probability}].
    """
    out = annotate_with_gender_guesser(
        ["John", "Mary", "Hiroshi", "Wei", "Asdfg"],
    )
    assert out["John"]["gg_label"] == "male"
    assert out["John"]["gender"] == "male"
    assert out["John"]["probability"] == 1.0
    # Mary → mostly_female in gender_guesser's dict (it's conservative)
    assert out["Mary"]["gg_label"] == "mostly_female"
    assert out["Mary"]["gender"] == "female"
    assert out["Mary"]["probability"] == 0.7
    assert out["Hiroshi"]["gender"] == "male"
    assert out["Wei"]["gender"] == "unknown"
    assert out["Wei"]["probability"] == 0.0
    assert out["Asdfg"]["gender"] == "unknown"


def test_annotate_with_gender_guesser_dedupes_and_handles_empty() -> None:
    """Duplicate names appear once in output; empty / whitespace
    names are skipped (no entry in result dict).
    """
    out = annotate_with_gender_guesser(
        ["John", "John", "", "  ", "Mary"],
    )
    assert set(out.keys()) == {"John", "Mary"}


def test_aggregate_per_author_single_paper() -> None:
    """Author with 1 paper → 1 output row with that paper's fields."""
    # Per-author-paper input: 1 author, 1 paper
    authorships = pa.table({
        "author_id": ["https://openalex.org/A1"],
        "publication_year": [2020],
        "author_first_name": ["John"],
        "first_name_is_initial": [False],
        "author_orcid": ["https://orcid.org/0000-1"],
        "countries": [["US"]],
        "source_type": ["journal"],
    })
    name_gender = {"John": {
        "gg_label": "male", "gender": "male", "probability": 1.0,
    }}
    result = aggregate_per_author(authorships, name_gender)

    assert result.num_rows == 1
    row = result.to_pylist()[0]
    assert row["author_id"] == "https://openalex.org/A1"
    assert row["author_first_name"] == "John"
    assert row["gender"] == "male"
    assert row["gender_probability"] == 1.0
    assert row["n_papers"] == 1
    assert row["primary_country"] == "US"
    assert row["n_papers_with_orcid"] == 1


def test_aggregate_per_author_multi_paper_picks_mode() -> None:
    """Author with N papers — primary_country = most-common; gender
    derived from author_first_name; n_papers counted.
    """
    authorships = pa.table({
        "author_id": ["https://openalex.org/A1"] * 4,
        "publication_year": [2018, 2019, 2020, 2021],
        "author_first_name": ["Mary", "Mary", "Mary", "Mary"],
        "first_name_is_initial": [False] * 4,
        "author_orcid": [None, None,
                          "https://orcid.org/0000-2",
                          "https://orcid.org/0000-2"],
        "countries": [["US"], ["US"], ["CA"], ["US"]],  # US wins
        "source_type": ["journal"] * 4,
    })
    name_gender = {"Mary": {
        "gg_label": "mostly_female", "gender": "female", "probability": 0.7,
    }}
    result = aggregate_per_author(authorships, name_gender)
    assert result.num_rows == 1
    row = result.to_pylist()[0]
    assert row["author_id"] == "https://openalex.org/A1"
    assert row["gender"] == "female"
    assert row["gender_probability"] == 0.7
    assert row["n_papers"] == 4
    assert row["primary_country"] == "US"
    assert row["n_papers_with_orcid"] == 2


def test_aggregate_per_author_unknown_name_yields_unknown_gender() -> None:
    """Author with first name not in name_gender dict → gender='unknown'."""
    authorships = pa.table({
        "author_id": ["https://openalex.org/A1"],
        "publication_year": [2020],
        "author_first_name": ["Xyzzy"],
        "first_name_is_initial": [False],
        "author_orcid": [None],
        "countries": [[]],
        "source_type": ["journal"],
    })
    result = aggregate_per_author(authorships, {})
    row = result.to_pylist()[0]
    assert row["gender"] == "unknown"
    assert row["gender_probability"] == 0.0
    assert row["primary_country"] is None  # empty countries → None


def test_annotate_gender_country_e2e(tmp_path: Path) -> None:
    """End-to-end: write a per-author-paper parquet, run
    annotate_gender_country, verify per-author output parquet has
    expected columns + sensible values.
    """
    rows = pa.table({
        "author_id": [
            "https://openalex.org/A1", "https://openalex.org/A1",
            "https://openalex.org/A2",
        ],
        "publication_year": [2019, 2020, 2020],
        "author_first_name": ["John", "John", "Mary"],
        "first_name_is_initial": [False, False, False],
        "author_orcid": [
            "https://orcid.org/0000-1", "https://orcid.org/0000-1", None,
        ],
        "countries": [["US"], ["US"], ["UK"]],
        "source_type": ["journal", "journal", "journal"],
    })
    src = tmp_path / "authorships.parquet"
    pq.write_table(rows, str(src))
    dst = tmp_path / "authors.parquet"

    summary = annotate_gender_country(src, dst)

    assert dst.exists()
    out = pq.read_table(str(dst))
    assert out.num_rows == 2  # 2 unique authors
    assert summary["n_unique_authors"] == 2
    assert summary["n_unique_first_names"] == 2
    # Coverage breakdown
    by_aid = {r["author_id"]: r for r in out.to_pylist()}
    assert by_aid["https://openalex.org/A1"]["gender"] == "male"
    assert by_aid["https://openalex.org/A1"]["primary_country"] == "US"
    assert by_aid["https://openalex.org/A2"]["gender"] == "female"
    assert by_aid["https://openalex.org/A2"]["primary_country"] == "UK"


# ---------- Genderize cross-validation (Step 3b) ----------
#
# All tests mock requests.get to avoid consuming the real 2,500/mo
# free-tier quota. The real Genderize call lives in
# query_genderize_batch; query_genderize orchestrates batching +
# quota tracking; combine_gg_and_genderize fuses gg + Genderize
# outputs per-name.


class _FakeResponse:
    """Minimal stand-in for requests.Response used by tests."""

    def __init__(
        self,
        json_data: Any,
        status_code: int = 200,
        headers: dict[str, str] | None = None,
    ) -> None:
        self._json = json_data
        self.status_code = status_code
        self.headers = headers or {}

    def json(self) -> Any:
        return self._json

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            from requests.exceptions import HTTPError
            raise HTTPError(f"HTTP {self.status_code}")


def test_query_genderize_batch_returns_per_name_dict(monkeypatch: Any) -> None:
    """A successful Genderize call returns {name: {gender, probability,
    count}} per name in the response.
    """
    captured: dict[str, Any] = {}

    def fake_get(url: str, params: dict[str, Any], timeout: float) -> _FakeResponse:
        captured["url"] = url
        captured["params"] = params
        return _FakeResponse([
            {"name": "John", "gender": "male", "probability": 0.99,
             "count": 12345},
            {"name": "Mary", "gender": "female", "probability": 0.98,
             "count": 11000},
        ])

    monkeypatch.setattr("requests.get", fake_get)

    out = query_genderize_batch(["John", "Mary"], api_key="test-key")
    assert out["John"]["gender"] == "male"
    assert out["John"]["probability"] == 0.99
    assert out["John"]["count"] == 12345
    assert out["Mary"]["gender"] == "female"
    assert captured["params"]["name[]"] == ["John", "Mary"]
    assert captured["params"]["apikey"] == "test-key"


def test_query_genderize_batch_handles_unknown_response(monkeypatch: Any) -> None:
    """Genderize returns gender=None for names it can't classify;
    these still get an entry in the output dict (with gender None).
    """
    monkeypatch.setattr(
        "requests.get",
        lambda *a, **kw: _FakeResponse([
            {"name": "Asdfg", "gender": None, "probability": 0.0,
             "count": 0},
        ]),
    )
    out = query_genderize_batch(["Asdfg"], api_key="test-key")
    assert "Asdfg" in out
    assert out["Asdfg"]["gender"] is None
    assert out["Asdfg"]["probability"] == 0.0


def test_query_genderize_orchestrator_batches_10(monkeypatch: Any) -> None:
    """query_genderize batches 10 names per request; n_calls counted.
    25 names → 3 calls (10 + 10 + 5).
    """
    calls: list[list[str]] = []

    def fake_get(url: str, params: dict[str, Any], timeout: float) -> _FakeResponse:
        names = params["name[]"]
        calls.append(names)
        return _FakeResponse([
            {"name": n, "gender": "male", "probability": 0.9, "count": 100}
            for n in names
        ])

    monkeypatch.setattr("requests.get", fake_get)
    names = [f"Name{i}" for i in range(25)]
    out = query_genderize(names, api_key="test-key", max_names=100)

    assert len(calls) == 3
    assert len(calls[0]) == 10
    assert len(calls[1]) == 10
    assert len(calls[2]) == 5
    assert len(out["results"]) == 25
    assert out["n_calls"] == 3
    assert out["n_names_queried"] == 25


def test_query_genderize_respects_max_names_quota(monkeypatch: Any) -> None:
    """Quota cap stops dispatching once max_names is reached.
    100 input names but max_names=25 → only the first 25 are queried."""
    def fake_get(url: str, params: dict[str, Any], timeout: float) -> _FakeResponse:
        return _FakeResponse([
            {"name": n, "gender": "male", "probability": 0.9, "count": 100}
            for n in params["name[]"]
        ])
    monkeypatch.setattr("requests.get", fake_get)

    out = query_genderize(
        [f"Name{i}" for i in range(100)],
        api_key="test-key",
        max_names=25,
    )
    assert out["n_names_queried"] == 25
    assert out["max_names"] == 25
    assert out["quota_exhausted"] is True
    assert len(out["results"]) == 25


def test_query_genderize_handles_api_error_partial(monkeypatch: Any) -> None:
    """If a batch fails mid-orchestration, prior results are kept
    and the failure is surfaced in the summary (no exception)."""
    call_counter = [0]

    def fake_get(url: str, params: dict[str, Any], timeout: float) -> _FakeResponse:
        call_counter[0] += 1
        if call_counter[0] == 2:
            return _FakeResponse({"error": "rate limit"}, status_code=429)
        return _FakeResponse([
            {"name": n, "gender": "male", "probability": 0.9, "count": 100}
            for n in params["name[]"]
        ])

    monkeypatch.setattr("requests.get", fake_get)
    out = query_genderize(
        [f"Name{i}" for i in range(25)],
        api_key="test-key",
        max_names=100,
    )
    # Batch 1 succeeded (10 names), batch 2 failed, batch 3 succeeded (5 names)
    assert len(out["results"]) == 15
    assert out["n_errors"] == 1


def test_combine_gg_and_genderize_both_confident_and_agree() -> None:
    """gg confident male + Genderize confident male → agree, combined male."""
    gg = {"John": {"gg_label": "male", "gender": "male", "probability": 1.0}}
    genderize = {"John": {"gender": "male", "probability": 0.99, "count": 1}}
    combined = combine_gg_and_genderize(gg, genderize)
    assert combined["John"]["combined_gender"] == "male"
    assert combined["John"]["both_methods_confident"] is True
    assert combined["John"]["both_methods_agree"] is True


def test_combine_gg_and_genderize_disagree() -> None:
    """gg male + Genderize female → disagree; combined is the GG result
    (gg is the locked primary per plan §"Gender stack"), but the
    disagreement flag is set so downstream can audit."""
    gg = {"Robin": {"gg_label": "mostly_male", "gender": "male", "probability": 0.7}}
    genderize = {"Robin": {"gender": "female", "probability": 0.8, "count": 100}}
    combined = combine_gg_and_genderize(gg, genderize)
    assert combined["Robin"]["both_methods_confident"] is False  # gg not confident
    assert combined["Robin"]["both_methods_agree"] is False
    # gg's lower-confidence pick still propagates as combined
    assert combined["Robin"]["combined_gender"] == "male"


def test_combine_gg_only() -> None:
    """Name with gg result but no Genderize → combined = gg, agree=None."""
    gg = {"John": {"gg_label": "male", "gender": "male", "probability": 1.0}}
    combined = combine_gg_and_genderize(gg, {})
    assert combined["John"]["combined_gender"] == "male"
    assert combined["John"]["both_methods_confident"] is False  # only gg
    assert combined["John"]["both_methods_agree"] is False
    assert combined["John"]["genderize_gender"] is None


def test_combine_gg_unknown_genderize_confident() -> None:
    """gg unknown + Genderize confident → use Genderize."""
    gg = {"Yiyu": {"gg_label": "unknown", "gender": "unknown",
                    "probability": 0.0}}
    genderize = {"Yiyu": {"gender": "female", "probability": 0.95, "count": 50}}
    combined = combine_gg_and_genderize(gg, genderize)
    assert combined["Yiyu"]["combined_gender"] == "female"
    # When gg is unknown but Genderize is confident, Genderize wins
    assert combined["Yiyu"]["genderize_gender"] == "female"


# ---------- annotate_gender_country with Genderize (Step 3c) ----------


def test_annotate_gender_country_with_genderize_extends_coverage(
    tmp_path: Path,
    monkeypatch: Any,
) -> None:
    """With genderize_api_key provided, gg-unknown names get Genderize
    extension. Verify: gg name "Yiyu" → gg unknown; Genderize returns
    female → per-author table shows gender=female, both_methods_*
    columns present, summary includes Genderize stats."""

    rows = pa.table({
        "author_id": [
            "https://openalex.org/A1", "https://openalex.org/A2",
            "https://openalex.org/A3",
        ],
        "publication_year": [2020, 2020, 2020],
        "author_first_name": ["John", "Yiyu", "Asdfg"],
        "first_name_is_initial": [False, False, False],
        "author_orcid": [None, None, None],
        "countries": [["US"], ["CN"], ["??"]],
        "source_type": ["journal", "journal", "journal"],
    })
    src = tmp_path / "authorships.parquet"
    pq.write_table(rows, str(src))
    dst = tmp_path / "authors.parquet"

    def fake_get(url: str, params: dict[str, Any], timeout: float) -> _FakeResponse:
        # Genderize sees ["Yiyu", "Asdfg"] (gg-unknown names)
        responses = {
            "Yiyu": {"name": "Yiyu", "gender": "female",
                      "probability": 0.95, "count": 50},
            "Asdfg": {"name": "Asdfg", "gender": None,
                       "probability": 0.0, "count": 0},
        }
        return _FakeResponse([
            responses[n] for n in params["name[]"] if n in responses
        ])

    monkeypatch.setattr("requests.get", fake_get)

    summary = annotate_gender_country(
        src, dst,
        genderize_api_key="test-key",
        genderize_max_names=100,
    )

    assert summary["genderize_invoked"] is True
    assert summary["genderize_summary"]["n_calls"] >= 1
    assert summary["genderize_summary"]["n_names_queried"] == 2
    # Yiyu (gg unknown, Genderize confident female) is one extension;
    # Asdfg (Genderize also fails) is not counted.
    assert summary["n_authors_extended_by_genderize"] == 1

    out = pq.read_table(str(dst))
    df = out.to_pandas()
    by_aid = {r["author_id"]: r for r in df.to_dict("records")}

    # John: gg confident male, no Genderize override
    assert by_aid["https://openalex.org/A1"]["gender"] == "male"
    # Yiyu: gg unknown, Genderize confident female → combined = female
    assert by_aid["https://openalex.org/A2"]["gender"] == "female"
    assert (
        by_aid["https://openalex.org/A2"]["genderize_gender"] == "female"
    )
    # Asdfg: gg unknown, Genderize also can't classify → still unknown
    assert by_aid["https://openalex.org/A3"]["gender"] == "unknown"


# ---------- Step 4a: script/region tagging + stratified sampler ----------


def test_tag_script_region_cjk() -> None:
    """CJK characters → cjk."""
    assert tag_script_region("张伟") == "cjk"       # Chinese
    assert tag_script_region("田中") == "cjk"       # Japanese kanji
    assert tag_script_region("김민수") == "cjk"     # Korean Hangul
    assert tag_script_region("ひろし") == "cjk"     # Japanese hiragana


def test_tag_script_region_cyrillic() -> None:
    """Cyrillic → cyrillic."""
    assert tag_script_region("Иван") == "cyrillic"
    assert tag_script_region("Людмила") == "cyrillic"


def test_tag_script_region_arabic() -> None:
    """Arabic → arabic."""
    assert tag_script_region("محمد") == "arabic"
    assert tag_script_region("فاطمة") == "arabic"


def test_tag_script_region_devanagari() -> None:
    """Devanagari → south_asian."""
    assert tag_script_region("राम") == "south_asian"
    assert tag_script_region("प्रिया") == "south_asian"


def test_tag_script_region_latin() -> None:
    """Latin script (incl. transliterations) → latin."""
    assert tag_script_region("John") == "latin"
    assert tag_script_region("Hiroshi") == "latin"      # Romaji
    assert tag_script_region("Yiyu") == "latin"         # Pinyin
    assert tag_script_region("Fenqiang") == "latin"
    assert tag_script_region("Müller") == "latin"       # Latin extended
    assert tag_script_region("Núñez") == "latin"


def test_tag_script_region_handles_empty() -> None:
    """Empty / None / whitespace-only → unknown."""
    assert tag_script_region("") == "unknown"
    assert tag_script_region("   ") == "unknown"
    assert tag_script_region(None) == "unknown"  # type: ignore[arg-type]


def test_stratified_sample_respects_strata_counts() -> None:
    """1000 names across 5 strata, sample 200 → 40 per stratum
    (deterministic by seed; uniform within stratum)."""
    names = []
    for region in ["latin", "cjk", "cyrillic", "arabic", "south_asian"]:
        for i in range(200):
            names.append((f"{region}_{i}", region))
    sample = stratified_sample_names(names, n_total=200, seed="test-seed-v1")

    assert len(sample) == 200
    from collections import Counter
    per_region = Counter(r for _, r in sample)
    # 200/5 = 40 per stratum
    for region in ["latin", "cjk", "cyrillic", "arabic", "south_asian"]:
        assert per_region[region] == 40


def test_stratified_sample_imbalanced_strata() -> None:
    """When some strata have fewer items than the per-stratum target,
    take all of them and over-sample the larger ones (sum-preserving).
    """
    # 1000 latin + 5 cjk + 10 cyrillic; sample 100 total
    names = (
        [(f"latin_{i}", "latin") for i in range(1000)]
        + [(f"cjk_{i}", "cjk") for i in range(5)]
        + [(f"cyr_{i}", "cyrillic") for i in range(10)]
    )
    sample = stratified_sample_names(names, n_total=100, seed="test-seed-v1")
    assert len(sample) == 100
    from collections import Counter
    per = Counter(r for _, r in sample)
    # cjk has only 5 → take all 5
    assert per["cjk"] == 5
    # cyrillic has 10 → take all 10
    assert per["cyrillic"] == 10
    # Remaining 85 go to latin
    assert per["latin"] == 85


def test_stratified_sample_deterministic_with_seed() -> None:
    """Same seed → same sample."""
    names = [(f"n_{i}", "latin") for i in range(100)]
    s1 = stratified_sample_names(names, n_total=20, seed="seed-A")
    s2 = stratified_sample_names(names, n_total=20, seed="seed-A")
    s3 = stratified_sample_names(names, n_total=20, seed="seed-B")
    assert s1 == s2
    assert s1 != s3


def test_stratified_sample_smaller_than_target() -> None:
    """When total population < n_total, return everything."""
    names = [(f"n_{i}", "latin") for i in range(10)]
    sample = stratified_sample_names(names, n_total=100, seed="x")
    assert len(sample) == 10


# ---------- annotate_gender_country without Genderize (Step 3a check) ----


def test_annotate_gender_country_without_genderize_unchanged(
    tmp_path: Path,
) -> None:
    """Without genderize_api_key, behavior matches Step 3a — no
    Genderize call, no genderize_* columns in output, no
    genderize_invoked flag.
    """
    rows = pa.table({
        "author_id": ["https://openalex.org/A1"],
        "publication_year": [2020],
        "author_first_name": ["John"],
        "first_name_is_initial": [False],
        "author_orcid": [None],
        "countries": [["US"]],
        "source_type": ["journal"],
    })
    src = tmp_path / "authorships.parquet"
    pq.write_table(rows, str(src))
    dst = tmp_path / "authors.parquet"

    summary = annotate_gender_country(src, dst)

    assert summary["genderize_invoked"] is False
    assert "genderize_summary" not in summary
    out = pq.read_table(str(dst))
    df = out.to_pandas()
    assert df.iloc[0]["gender"] == "male"
    # genderize_* columns NOT present when Genderize wasn't run
    assert "genderize_gender" not in df.columns


# ---------- Step 4b: NamSor API client ----------


def test_query_namsor_batch_returns_per_name_dict(monkeypatch: Any) -> None:
    """A successful NamSor batch returns {name: {gender, probability,
    score, script}} per requested name."""
    captured: dict[str, Any] = {}

    def fake_post(url: str, headers: dict[str, str],
                  json: dict[str, Any], timeout: float) -> _FakeResponse:
        captured["url"] = url
        captured["headers"] = headers
        captured["json"] = json
        return _FakeResponse({
            "personalNames": [
                {"id": "Yiyu", "firstName": "Yiyu", "lastName": "",
                 "script": "LATIN", "likelyGender": "female",
                 "genderScale": 0.27, "score": 1.6,
                 "probabilityCalibrated": 0.64},
                {"id": "Junxu", "firstName": "Junxu", "lastName": "",
                 "script": "LATIN", "likelyGender": "male",
                 "genderScale": -0.87, "score": 7.18,
                 "probabilityCalibrated": 0.94},
            ],
        })

    monkeypatch.setattr("requests.post", fake_post)
    out = query_namsor_batch(["Yiyu", "Junxu"], api_key="test-key")
    assert out["Yiyu"]["gender"] == "female"
    assert out["Yiyu"]["probability"] == 0.64
    assert out["Yiyu"]["script"] == "LATIN"
    assert out["Junxu"]["gender"] == "male"
    assert out["Junxu"]["probability"] == 0.94

    # Request shape: headers carry X-API-KEY, body is genderBatch shape
    assert captured["headers"]["X-API-KEY"] == "test-key"
    assert captured["json"]["personalNames"] == [
        {"id": "Yiyu", "firstName": "Yiyu", "lastName": ""},
        {"id": "Junxu", "firstName": "Junxu", "lastName": ""},
    ]


def test_query_namsor_batch_handles_unknown_gender(monkeypatch: Any) -> None:
    """NamSor can return likelyGender='unknown' for unclassifiable
    names. Keep in dict with gender='unknown'."""
    monkeypatch.setattr(
        "requests.post",
        lambda url, headers, json, timeout: _FakeResponse({
            "personalNames": [{
                "id": "Asdfg", "firstName": "Asdfg",
                "script": "LATIN", "likelyGender": "unknown",
                "genderScale": 0.0, "score": 0.0,
                "probabilityCalibrated": 0.5,
            }],
        }),
    )
    out = query_namsor_batch(["Asdfg"], api_key="test-key")
    assert out["Asdfg"]["gender"] == "unknown"


def test_query_namsor_orchestrator_batches_100(monkeypatch: Any) -> None:
    """query_namsor batches 100 names per request (NamSor's batch limit).
    250 names → 3 calls (100 + 100 + 50)."""
    calls: list[list[str]] = []

    def fake_post(url: str, headers: dict[str, str],
                  json: dict[str, Any], timeout: float) -> _FakeResponse:
        names = [p["firstName"] for p in json["personalNames"]]
        calls.append(names)
        return _FakeResponse({
            "personalNames": [
                {"id": n, "firstName": n, "script": "LATIN",
                 "likelyGender": "male", "probabilityCalibrated": 0.9}
                for n in names
            ],
        })

    monkeypatch.setattr("requests.post", fake_post)
    names = [f"Name{i}" for i in range(250)]
    out = query_namsor(names, api_key="test-key", max_names=2500)

    assert len(calls) == 3
    assert [len(c) for c in calls] == [100, 100, 50]
    assert len(out["results"]) == 250
    assert out["n_calls"] == 3
    assert out["n_names_queried"] == 250


def test_query_namsor_respects_max_names_quota(monkeypatch: Any) -> None:
    """500 input names, max_names=150 → only first 150 queried."""
    monkeypatch.setattr(
        "requests.post",
        lambda url, headers, json, timeout: _FakeResponse({
            "personalNames": [
                {"id": p["firstName"], "firstName": p["firstName"],
                 "script": "LATIN", "likelyGender": "male",
                 "probabilityCalibrated": 0.9}
                for p in json["personalNames"]
            ],
        }),
    )
    out = query_namsor(
        [f"Name{i}" for i in range(500)],
        api_key="test-key", max_names=150,
    )
    assert out["n_names_queried"] == 150
    assert out["quota_exhausted"] is True
    assert len(out["results"]) == 150


# ---------- Step 4c: sample_for_namsor driver ----------


def test_sample_for_namsor_e2e(
    tmp_path: Path, monkeypatch: Any,
) -> None:
    """End-to-end driver: per-author parquet + low-conf identification
    + script-tagged stratified sample + NamSor query + bias-sample
    parquet write.
    """
    # Build a per-author parquet that mimics Step 3c's output. 4 unique
    # authors / 4 unique low-conf names; 2 distinct script regions.
    per_author = pa.table({
        "author_id": [f"https://openalex.org/A{i}" for i in range(4)],
        "author_first_name": ["Yiyu", "Junxu", "Иван", "Магдалена"],
        "gg_label": ["unknown", "unknown", "unknown", "unknown"],
        "gender": ["unknown"] * 4,
        "gender_probability": [0.0] * 4,
        "primary_country": ["CN", "CN", "RU", "BG"],
        "n_papers": [1, 1, 1, 1],
    })
    per_author_path = tmp_path / "per_author.parquet"
    pq.write_table(per_author, str(per_author_path))

    def fake_post(url: str, headers: dict[str, str],
                  json: dict[str, Any], timeout: float) -> _FakeResponse:
        return _FakeResponse({
            "personalNames": [
                {"id": p["firstName"], "firstName": p["firstName"],
                 "script": "LATIN" if not any(
                     ord(c) > 127 for c in p["firstName"]
                 ) else "CYRILLIC",
                 "likelyGender": "female",
                 "probabilityCalibrated": 0.85}
                for p in json["personalNames"]
            ],
        })

    monkeypatch.setattr("requests.post", fake_post)

    out_path = tmp_path / "namsor-sample.parquet"
    summary = sample_for_namsor(
        per_author_path, out_path,
        namsor_api_key="test-key",
        max_names=100,
        seed="test-seed",
    )

    assert out_path.exists()
    tbl = pq.read_table(str(out_path))
    df = tbl.to_pandas()
    # All 4 low-conf names should be sampled (well below n=100 cap)
    assert df.shape[0] == 4
    expected_cols = {
        "first_name", "script_region", "namsor_gender",
        "namsor_probability", "namsor_script",
    }
    assert expected_cols.issubset(set(df.columns))

    # Summary metrics
    assert summary["n_low_conf_names"] == 4
    assert summary["n_sampled"] == 4
    assert summary["n_namsor_classified"] == 4
    assert summary["namsor_summary"]["n_calls"] >= 1
    # Per-region breakdown
    assert "n_sampled_by_region" in summary
    assert summary["n_sampled_by_region"]["latin"] == 2  # Yiyu, Junxu
    assert summary["n_sampled_by_region"]["cyrillic"] == 2  # Иван, Магдалена


def test_sample_for_namsor_respects_quota(
    tmp_path: Path, monkeypatch: Any,
) -> None:
    """With 50 low-conf names and max_names=20, only 20 are sampled
    and sent to NamSor."""
    per_author = pa.table({
        "author_id": [f"https://openalex.org/A{i}" for i in range(50)],
        "author_first_name": [f"Name{i}" for i in range(50)],
        "gg_label": ["unknown"] * 50,
        "gender": ["unknown"] * 50,
        "gender_probability": [0.0] * 50,
        "primary_country": ["US"] * 50,
        "n_papers": [1] * 50,
    })
    pa_path = tmp_path / "pa.parquet"
    pq.write_table(per_author, str(pa_path))

    monkeypatch.setattr(
        "requests.post",
        lambda url, headers, json, timeout: _FakeResponse({
            "personalNames": [
                {"id": p["firstName"], "firstName": p["firstName"],
                 "script": "LATIN", "likelyGender": "male",
                 "probabilityCalibrated": 0.9}
                for p in json["personalNames"]
            ],
        }),
    )

    out = tmp_path / "out.parquet"
    summary = sample_for_namsor(
        pa_path, out, namsor_api_key="k", max_names=20, seed="s",
    )
    assert summary["n_low_conf_names"] == 50
    assert summary["n_sampled"] == 20
    assert summary["n_namsor_classified"] == 20


def test_query_namsor_handles_api_error_partial(monkeypatch: Any) -> None:
    """Transient batch failure → counted in n_errors; subsequent
    batches still succeed; prior results preserved."""
    call_counter = [0]

    def fake_post(url: str, headers: dict[str, str],
                  json: dict[str, Any], timeout: float) -> _FakeResponse:
        call_counter[0] += 1
        if call_counter[0] == 2:
            return _FakeResponse({"error": "rate limit"}, status_code=429)
        names = [p["firstName"] for p in json["personalNames"]]
        return _FakeResponse({
            "personalNames": [
                {"id": n, "firstName": n, "script": "LATIN",
                 "likelyGender": "male", "probabilityCalibrated": 0.9}
                for n in names
            ],
        })

    monkeypatch.setattr("requests.post", fake_post)
    out = query_namsor(
        [f"Name{i}" for i in range(250)],
        api_key="test-key", max_names=2500,
    )
    # Batch 1 (100) + batch 3 (50) succeed; batch 2 (100) fails
    assert len(out["results"]) == 150
    assert out["n_errors"] == 1
