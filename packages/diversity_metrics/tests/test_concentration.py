"""Unit tests for the concentration metrics (lifted from WS2 test_metrics.py)."""

from __future__ import annotations

import numpy as np

from diversity_metrics.concentration import gini, top_k_share

# ---------- gini ----------


def test_gini_known() -> None:
    """gini([1,2,3,4]) = 0.25; equal values → 0."""
    assert abs(gini(np.array([1.0, 2.0, 3.0, 4.0])) - 0.25) < 1e-9
    assert gini(np.array([5.0, 5.0, 5.0])) == 0.0
    # Empty / all-zero → 0 (degenerate, no concentration)
    assert gini(np.array([0.0, 0.0, 0.0])) == 0.0


def test_gini_concentration_rises() -> None:
    """More concentrated citations → higher Gini (the canonical negative
    control's expected direction over time)."""
    spread = gini(np.array([10.0, 11.0, 9.0, 10.0]))
    concentrated = gini(np.array([0.0, 0.0, 1.0, 100.0]))
    assert concentrated > spread


# ---------- top_k_share ----------


def test_top_k_share_known() -> None:
    """Share of total held by the top k-fraction of items."""
    v = np.array([1.0, 1.0, 1.0, 7.0])  # total 10
    assert abs(top_k_share(v, 0.25) - 0.7) < 1e-9   # top 1 of 4 = 7/10
    assert abs(top_k_share(v, 0.5) - 0.8) < 1e-9    # top 2 = (7+1)/10
    assert top_k_share(np.array([0.0, 0.0]), 0.5) == 0.0  # degenerate
