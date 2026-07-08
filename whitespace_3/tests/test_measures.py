"""Phase 2 — the vendored WS2 measures must be byte-faithful (Experiment A's apples-to-apples
relies on the model being measured by the *identical* code as the data). Toy values mirror
WS2's own ``test_v_extension.test_reference_atypicality``."""

from __future__ import annotations

import numpy as np

from whitespace3.measures import cd_index, reference_atypicality, within_group_atypicality


def test_reference_atypicality_vendored() -> None:
    # C,D always co-cited (conventional); A,B each common but co-cited only once (atypical).
    refs = [["C", "D"]] * 50 + [["A"]] * 30 + [["B"]] * 30 + [["A", "B"]]
    med, _ = reference_atypicality(refs, d_min=20, min_pairs=1)
    assert med[0] > 0            # [C,D] co-cited far more than expected → conventional
    assert med[-1] < 0           # [A,B] never co-cited before → atypical
    assert med[0] > med[-1]
    assert np.isnan(med[50])     # single-ref paper [A] → no pair → NaN


def test_within_group_atypicality() -> None:
    # two groups, each with its own repeated (locally-standard) pair; within-frame ⇒ non-NaN,
    # and the locally-standard pair reads conventional. (Refs are non-universal so Var>0.)
    refs: list[list[str]] = ([["X", "Y"]] * 10 + [["A", "B"]] * 5
                             + [["X", "Z"]] * 10 + [["C", "D"]] * 5)
    groups = [0] * 15 + [1] * 15
    w = within_group_atypicality(refs, groups, d_min=3, min_pairs=1)
    assert not np.isnan(w[0]) and not np.isnan(w[-1])
    assert w[0] > 0              # [X,Y] co-cited 10× vs ~6.7 expected → conventional in group 0


def test_cd_index() -> None:
    # element 1 (cites root 0) cited by 3 papers ignoring its ref (disruptive) + 1 citing both
    # (consolidating) ⇒ CD > 0.
    disruptive = [[], [0], [1], [1], [1], [1, 0]]
    cd = cd_index(disruptive, min_citers=3)
    assert cd[1] > 0
    assert np.isnan(cd[0])       # root: no references → NaN
    # reverse: 3 consolidating citers + 1 disruptive ⇒ CD < 0.
    consolidating = [[], [0], [1, 0], [1, 0], [1, 0], [1]]
    assert cd_index(consolidating, min_citers=3)[1] < 0
