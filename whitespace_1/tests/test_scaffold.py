"""Scaffold smoke test — replaced by real engine tests when rung 0 is built."""

import whitespace1


def test_package_imports() -> None:
    assert whitespace1.__doc__ is not None
