"""Credential resolution must ignore inherited shell values and fail loudly."""

from __future__ import annotations

import pytest

from whitespace1.credentials import MissingCredential, has_secret, parse_dotenv, require_secret


def test_parses_plain_export_quoted_and_comments(tmp_path) -> None:
    p = tmp_path / ".env"
    p.write_text(
        "# comment\n\nOPENAI_API_KEY=sk-plain\nexport OTHER='quoted'\n"
        'THIRD="dq" # trailing\nMALFORMED\n'
    )
    got = parse_dotenv(p)
    assert got == {"OPENAI_API_KEY": "sk-plain", "OTHER": "quoted", "THIRD": "dq"}


def test_missing_file_yields_empty(tmp_path) -> None:
    assert parse_dotenv(tmp_path / "nope") == {}


def test_returns_folder_local_value(tmp_path) -> None:
    p = tmp_path / ".env"
    p.write_text("OPENAI_API_KEY=sk-local\n")
    assert require_secret("OPENAI_API_KEY", dotenv_path=p) == "sk-local"


def test_inherited_value_is_ignored_and_reported(tmp_path, monkeypatch) -> None:
    """The core guard: a shell key must NOT satisfy the requirement."""
    monkeypatch.setenv("OPENAI_API_KEY", "sk-inherited-from-somewhere-else")
    with pytest.raises(MissingCredential) as e:
        require_secret("OPENAI_API_KEY", dotenv_path=tmp_path / ".env")
    assert "IGNORED" in str(e.value)


def test_empty_value_in_dotenv_still_fails(tmp_path) -> None:
    p = tmp_path / ".env"
    p.write_text("OPENAI_API_KEY=\n")
    with pytest.raises(MissingCredential):
        require_secret("OPENAI_API_KEY", dotenv_path=p)


def test_has_secret_tracks_folder_local_only(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "sk-inherited")
    assert has_secret("OPENAI_API_KEY", dotenv_path=tmp_path / ".env") is False
    p = tmp_path / ".env"
    p.write_text("OPENAI_API_KEY=sk-local\n")
    assert has_secret("OPENAI_API_KEY", dotenv_path=p) is True
