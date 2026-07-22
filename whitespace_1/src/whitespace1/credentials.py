"""Folder-local credential resolution — the whitespace's own ``.env`` is the only authority.

**An inherited shell value is never used.** A key exported in the ambient environment may belong to
a different project (a sibling repo, or a work account); silently spending against it is the failure
this module exists to prevent. Resolution reads ``whitespace_1/.env`` directly, so it behaves the
same with or without direnv, and raises loudly when the key is absent.
"""

from __future__ import annotations

import os
from pathlib import Path

# whitespace_1/src/whitespace1/credentials.py -> whitespace_1/
WHITESPACE_ROOT = Path(__file__).resolve().parents[2]
DOTENV_PATH = WHITESPACE_ROOT / ".env"


class MissingCredential(RuntimeError):
    """Raised when a required secret is not set in the folder-local ``.env``."""


def parse_dotenv(path: Path) -> dict[str, str]:
    """Parse a minimal ``.env``: ``KEY=value``, optional ``export`` prefix, ``#`` comments,
    optional surrounding quotes. Returns ``{}`` when the file does not exist."""
    if not path.is_file():
        return {}
    out: dict[str, str] = {}
    for raw in path.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.removeprefix("export ").strip()
        value = value.split(" #", 1)[0].strip().strip("'\"")
        if key:
            out[key] = value
    return out


def require_secret(name: str, *, dotenv_path: Path | None = None) -> str:
    """Return ``name`` from the folder-local ``.env``, or raise :class:`MissingCredential`.

    Never falls back to ``os.environ``. If an inherited value exists it is reported in the error so
    the mismatch is obvious rather than silently honoured.
    """
    path = DOTENV_PATH if dotenv_path is None else dotenv_path
    value = parse_dotenv(path).get(name, "").strip()
    if value:
        return value

    inherited = bool(os.environ.get(name, "").strip())
    note = (
        f"\n  NOTE: an inherited {name} IS set in your shell environment, and is being IGNORED "
        "on purpose - it may belong to another project."
        if inherited
        else ""
    )
    raise MissingCredential(
        f"{name} is not set in the folder-local env file:\n"
        f"  {path}\n"
        f"Create it from the template and supply a key scoped to this whitespace:\n"
        f"  cp {path.parent / '.env.example'} {path}{note}"
    )


def has_secret(name: str, *, dotenv_path: Path | None = None) -> bool:
    """True when ``name`` is available folder-locally.

    Use to skip live steps, never to fall back to an inherited value.
    """
    path = DOTENV_PATH if dotenv_path is None else dotenv_path
    return bool(parse_dotenv(path).get(name, "").strip())
