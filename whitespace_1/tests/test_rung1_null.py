"""Token-free tests for the rung-1 matched null: the replay positive control reproduces the recorded
P_top4 exactly, and a preference-free null's P_top4 falls as the catalog grows."""

from __future__ import annotations

import hashlib

import numpy as np

from whitespace1.rung1_null import (
    NullMode,
    even_share,
    replay_run,
    simulate,
    slope,
    top_k_share,
)
from whitespace1.rung1_r4 import GeneratedProposal, R4Condition, R4Config, r4_run_to_dict, run_r4


class _Mock:
    def __init__(self, dims: int = 16) -> None:
        self.dims = dims
        self.calls = 0

    def propose_many(self, *, personas, topic, catalog_samples):  # noqa: ANN001, ANN201
        self.calls += 1
        return tuple(
            GeneratedProposal(text=f"{p.name}|r{self.calls}", persona_name=p.name) for p in personas
        )

    def embed(self, texts):  # noqa: ANN001, ANN201
        rows = []
        for t in texts:
            s = int(hashlib.sha256(t.encode()).hexdigest(), 16) % (2**32)
            v = np.random.default_rng(s).normal(size=self.dims)
            rows.append(v / np.linalg.norm(v))
        return np.asarray(rows, dtype=np.float64)


def test_replay_reproduces_recorded_p_top4_exactly() -> None:
    cfg = R4Config(condition=R4Condition.POPULARITY, run_identifier="r")
    art = r4_run_to_dict(run_r4(provider=_Mock(), config=cfg))
    replayed = replay_run(art)
    expected = [
        r["post_echo_top4_share"] for r in art["rounds"] if r["post_echo_top4_share"] is not None
    ]
    assert len(replayed) == len(expected) == 8
    assert max(abs(a - b) for a, b in zip(replayed, expected, strict=True)) < 1e-9


def test_preference_free_null_p_top4_declines_as_catalog_grows() -> None:
    rng = np.random.default_rng(0)
    pool = np.abs(rng.normal(size=1000))  # positive similarity pool
    trajectory = simulate(rng, NullMode.HETEROGENEOUS, pool)
    assert len(trajectory) == 8 and slope(trajectory) < 0  # growing denominator ⇒ raw P_top4 falls


def test_top_k_and_even_share() -> None:
    assert abs(top_k_share([1, 1, 1, 1]) - 1.0) < 1e-12
    assert abs(even_share(8) - 0.5) < 1e-12  # 4 / 8
