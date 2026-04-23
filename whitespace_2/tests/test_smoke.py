"""Smoke test: the package imports and exposes a version string."""

import whitespace2


def test_package_imports() -> None:
    assert isinstance(whitespace2.__version__, str)
    assert whitespace2.__version__  # non-empty
