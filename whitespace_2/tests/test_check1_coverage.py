"""Tests for the Check 1 analysis helpers (coverage_rate, wilson_ci).

The helpers live alongside the script in experiments/phase-0.1/check1_abstract_coverage.py.
We import them by inserting the experiments directory on sys.path; the script's
top-level main() block must therefore be guarded by `if __name__ == "__main__"`.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

_EXPERIMENT_DIR = Path(__file__).parent.parent / "experiments" / "phase-0.1"
_SCRIPT_PATH = _EXPERIMENT_DIR / "check1_abstract_coverage.py"


def _load_check1_module():  # type: ignore[no-untyped-def]
    spec = importlib.util.spec_from_file_location("check1", _SCRIPT_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load module spec from {_SCRIPT_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules["check1"] = module
    spec.loader.exec_module(module)
    return module


def test_coverage_rate_basic() -> None:
    module = _load_check1_module()
    rows = [
        {"year": 1990, "field": "cs", "has_abstract": True},
        {"year": 1990, "field": "cs", "has_abstract": True},
        {"year": 1990, "field": "cs", "has_abstract": False},
        {"year": 1990, "field": "cs", "has_abstract": True},
    ]
    n_total, n_with, rate = module.coverage_rate(rows)
    assert n_total == 4
    assert n_with == 3
    assert rate == pytest.approx(0.75)


def test_wilson_ci_at_typical_values() -> None:
    module = _load_check1_module()
    low, high = module.wilson_ci(190, 200, alpha=0.05)
    assert 0.90 < low < 0.95
    assert 0.96 < high < 0.99


def test_wilson_ci_at_edge_p_zero() -> None:
    module = _load_check1_module()
    low, high = module.wilson_ci(0, 200, alpha=0.05)
    assert low == pytest.approx(0.0, abs=1e-9)
    assert 0.0 < high < 0.05


def test_wilson_ci_at_edge_p_one() -> None:
    module = _load_check1_module()
    low, high = module.wilson_ci(200, 200, alpha=0.05)
    assert 0.95 < low < 1.0
    assert high == pytest.approx(1.0, abs=1e-9)
