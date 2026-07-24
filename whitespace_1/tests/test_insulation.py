"""Token-free tests for the insulation experiment: the adoption echo, the per-capita gap, and the
label-shuffle null all behave — a field that echoes the isolated origin yields a gap that beats the
null; a field with no origin preference yields a gap of zero."""

from __future__ import annotations

import numpy as np

from whitespace1.insulation import (
    CONNECTED,
    ISOLATED,
    Candidate,
    Showing,
    _echo,
    adoption_gap,
    label_shuffle_null,
    live_check,
    run_adoption,
)
from whitespace1.rung1_r4 import GeneratedProposal
from whitespace1.stimuli import ROLES

DIM = 8
E = np.eye(DIM)


def _cands(iso_dir, conn_dir, k: int = 5):  # noqa: ANN001, ANN202
    return [Candidate(f"iso{i}", tuple(iso_dir), ISOLATED) for i in range(k)] + [
        Candidate(f"conn{i}", tuple(conn_dir), CONNECTED) for i in range(k)
    ]


class _Field:
    """A field whose every output points at ``out_dir`` — echoing candidates aligned with it."""

    def __init__(self, out_dir) -> None:  # noqa: ANN001
        self.out = np.asarray(out_dir, dtype=np.float64)

    def propose_many(self, *, personas, topic, catalog_samples):  # noqa: ANN001, ANN201
        return tuple(GeneratedProposal(text=f"o{p.name}", persona_name=p.name) for p in personas)

    def embed(self, texts):  # noqa: ANN001, ANN201
        return np.tile(self.out, (len(list(texts)), 1))


def test_echo_formula() -> None:
    outs = np.tile(E[0], (5, 1))
    assert abs(_echo(outs, E[0]) - 5.0) < 1e-9  # 5 agents, all aligned
    assert abs(_echo(outs, E[1]) - 0.0) < 1e-9  # orthogonal → no echo


def test_adoption_produces_shown_and_decoy_counts() -> None:
    s = run_adoption(provider=_Field(E[0]), personas=ROLES, topic="T",
                     candidates=_cands(E[0], E[1]), rounds=4, shown_per_origin=2,
                     rng=np.random.default_rng(0))
    assert sum(1 for x in s if x.shown) == 4 * 4  # 2+2 shown per round × 4 rounds
    assert sum(1 for x in s if not x.shown) == 4 * 6  # 3+3 unseen per round × 4 rounds


def test_gap_positive_and_beats_null_when_field_echoes_isolated() -> None:
    s = run_adoption(provider=_Field(E[0]), personas=ROLES, topic="T",
                     candidates=_cands(E[0], E[1]), rounds=4, shown_per_origin=2,
                     rng=np.random.default_rng(1))
    gap = adoption_gap(s)
    assert gap > 0  # isolated on E0, echoed by the E0-field; connected on E1, not
    null = label_shuffle_null(s, np.random.default_rng(2), n=2000)
    assert float((null >= gap).mean()) < 0.05  # observed gap beats the label-shuffle null


def test_gap_zero_when_field_has_no_origin_preference() -> None:
    neutral = (E[0] + E[1]) / np.sqrt(2)
    s = run_adoption(provider=_Field(neutral), personas=ROLES, topic="T",
                     candidates=_cands(E[0], E[1]), rounds=4, shown_per_origin=2,
                     rng=np.random.default_rng(3))
    assert abs(adoption_gap(s)) < 1e-6  # both origins echoed equally


def test_label_shuffle_null_centers_near_zero() -> None:
    s = [Showing(ISOLATED, 5.0, True), Showing(ISOLATED, 5.0, True),
         Showing(CONNECTED, 0.0, True), Showing(CONNECTED, 0.0, True)]
    null = label_shuffle_null(s, np.random.default_rng(0), n=5000)
    assert abs(float(null.mean())) < 0.3  # symmetric around 0


def test_live_check_positive_when_shown_beats_decoy() -> None:
    s = [Showing(ISOLATED, 3.0, True), Showing(CONNECTED, 3.0, True),
         Showing(ISOLATED, 1.0, False), Showing(CONNECTED, 1.0, False)]
    assert live_check(s) > 0  # shown (3) beats decoy (1)
