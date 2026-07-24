"""Token-free tests for the rung-1 R4 loop: the append-only actuator runs, conditions differ, the
per-round measurements populate, and the artifact round-trips — all against a deterministic mock."""

from __future__ import annotations

import hashlib

import numpy as np
import pytest

from whitespace1.rung1_r4 import (
    R4_TOPICS,
    GeneratedProposal,
    R4Condition,
    R4Config,
    build_walk_prompt,
    r4_run_to_dict,
    run_r4,
    v_pair_slope,
)


class MockR4Provider:
    """Deterministic, network-free provider. Distinct per-persona, per-round texts → distinct
    embeddings (so V_pair > 0 and the catalog fills with distinct items)."""

    def __init__(self, dims: int = 16) -> None:
        self.dims = dims
        self.calls = 0

    def propose_many(self, *, personas, topic, catalog_samples):  # noqa: ANN001, ANN201
        self.calls += 1
        return tuple(
            GeneratedProposal(text=f"{p.name}|round{self.calls}", persona_name=p.name)
            for p in personas
        )

    def embed(self, texts):  # noqa: ANN001, ANN201
        rows = []
        for t in texts:
            seed = int(hashlib.sha256(t.encode()).hexdigest(), 16) % (2**32)
            v = np.random.default_rng(seed).normal(size=self.dims)
            rows.append(v / np.linalg.norm(v))
        return np.asarray(rows, dtype=np.float64)


def _cfg(condition: R4Condition = R4Condition.POPULARITY) -> R4Config:
    return R4Config(condition=condition, run_identifier="r")


def test_config_validates_rounds_exposure_and_seed_catalog() -> None:
    with pytest.raises(ValueError):
        R4Config(condition=R4Condition.POPULARITY, run_identifier="")  # empty id
    with pytest.raises(ValueError):
        R4Config(condition=R4Condition.POPULARITY, run_identifier="r", exposure_budget=3)
    with pytest.raises(ValueError):
        R4Config(condition=R4Condition.POPULARITY, run_identifier="r", seed_catalog=("a",) * 8)
    ok = _cfg()
    assert ok.topic == R4_TOPICS["topic-a"] and ok.rounds == 8


def test_loop_runs_eight_rounds_and_catalog_grows() -> None:
    run = run_r4(provider=MockR4Provider(), config=_cfg())
    assert len(run.rounds) == 8
    assert len(run.rounds[-1].pre_catalog) == 8 + 5 * 7  # 8 seed + 5 outputs × 7 prior rounds
    assert all(0.0 <= r.v_pair <= 2.0 for r in run.rounds)


def test_popularity_shows_a_sample_and_scores_uptake_and_top4() -> None:
    run = run_r4(provider=MockR4Provider(), config=_cfg(R4Condition.POPULARITY))
    for r in run.rounds:
        assert len(r.shown_sample_ids) == 4 and len(r.decoy_ids) == 4
        assert r.item_uptake is not None and len(r.item_uptake) == 5
        assert r.post_echo_top4_share is not None and 0.0 <= r.post_echo_top4_share <= 1.0


def test_ablation_shows_no_sample_and_no_uptake() -> None:
    run = run_r4(provider=MockR4Provider(), config=_cfg(R4Condition.ABLATION))
    for r in run.rounds:
        assert r.shown_sample_ids == () and r.item_uptake is None
        assert r.post_echo_top4_share is None


def test_provider_must_preserve_persona_order() -> None:
    class BadProvider(MockR4Provider):
        def propose_many(self, *, personas, topic, catalog_samples):  # noqa: ANN001, ANN201
            proposals = super().propose_many(
                personas=personas, topic=topic, catalog_samples=catalog_samples
            )
            return tuple(reversed(proposals))  # wrong order

    with pytest.raises(RuntimeError):
        run_r4(provider=BadProvider(), config=_cfg())


def test_artifact_roundtrips_and_slope_is_a_float() -> None:
    run = run_r4(provider=MockR4Provider(), config=_cfg())
    d = r4_run_to_dict(run)
    assert d["config"]["condition"] == "popularity"
    assert len(d["rounds"]) == 8
    assert len(d["rounds"][0]["proposal_embeddings"]) == 5
    assert isinstance(v_pair_slope(run), float)


def test_build_walk_prompt_shows_catalog_or_none() -> None:
    shown = build_walk_prompt(name="X", viewpoint="V", topic="T", catalog_items=["alpha", "beta"])
    assert "- alpha" in shown and "- beta" in shown and "Persona: X" in shown
    empty = build_walk_prompt(name="X", viewpoint="V", topic="T", catalog_items=[])
    assert "none available this round." in empty
