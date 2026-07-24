"""Token-free tests for the catalog-of-reasoning loop: the catalog fills with agent skeletons, both
channels are measured, and the artifact keys feed the generalized confirmatory."""

from __future__ import annotations

import hashlib

import numpy as np

from whitespace1.rung1_r4 import GeneratedProposal, R4Condition, R4Config
from whitespace1.rung2_reasoning import (
    build_reasoning_prompt,
    r4_reasoning_to_dict,
    run_r4_reasoning,
)


class _Mock:
    def __init__(self, dims: int = 16) -> None:
        self.dims = dims
        self.calls = 0

    def propose_many(self, *, personas, topic, catalog_samples):  # noqa: ANN001, ANN201
        self.calls += 1
        return tuple(
            GeneratedProposal(text=f"{p.name}|ans{self.calls}", persona_name=p.name,
                              reasoning=f"{p.name}|trace{self.calls}")
            for p in personas
        )

    def embed(self, texts):  # noqa: ANN001, ANN201
        rows = []
        for t in texts:
            s = int(hashlib.sha256(t.encode()).hexdigest(), 16) % (2**32)
            v = np.random.default_rng(s).normal(size=self.dims)
            rows.append(v / np.linalg.norm(v))
        return np.asarray(rows, dtype=np.float64)


def _extract_many(traces):  # noqa: ANN001, ANN202
    return [f"skeleton::{t}" for t in traces]


def _cfg(condition: R4Condition = R4Condition.POPULARITY) -> R4Config:
    return R4Config(condition=condition, run_identifier="r")


def test_catalog_fills_with_skeletons_and_both_channels_measured() -> None:
    run = run_r4_reasoning(provider=_Mock(), config=_cfg(), extract_many=_extract_many)
    assert len(run.rounds) == 8
    assert len(run.rounds[-1].pre_catalog) == 8 + 5 * 7  # 8 seed + 5 skeletons × 7 prior rounds
    # the appended catalog items are skeletons, not answers
    assert run.rounds[-1].pre_catalog[-1].text.startswith("skeleton::")
    for r in run.rounds:
        assert len(r.skeletons) == 5 and len(r.answers) == 5
        assert r.skeleton_embeddings.shape == (5, 16) and r.answer_embeddings.shape == (5, 16)
        assert 0.0 <= r.v_reason <= 2.0 and 0.0 <= r.v_output <= 2.0


def test_popularity_shows_reasoning_sample_and_scores_uptake() -> None:
    run = run_r4_reasoning(provider=_Mock(), config=_cfg(), extract_many=_extract_many)
    for r in run.rounds:
        assert len(r.shown_sample_ids) == 4
        assert r.item_uptake is not None and len(r.item_uptake) == 5
        assert r.post_echo_top4_share is not None


def test_ablation_shows_no_sample() -> None:
    run = run_r4_reasoning(provider=_Mock(), config=_cfg(R4Condition.ABLATION),
                           extract_many=_extract_many)
    for r in run.rounds:
        assert r.shown_sample_ids == () and r.item_uptake is None
        assert r.post_echo_top4_share is None


def test_artifact_keys_feed_the_confirmatory() -> None:
    d = r4_reasoning_to_dict(run_r4_reasoning(provider=_Mock(), config=_cfg(),
                                              extract_many=_extract_many))
    assert d["config"]["catalog_mode"] == "reasoning"
    r0 = d["rounds"][0]
    assert len(r0["skeleton_embeddings"]) == 5  # V_reason (primary)
    assert len(r0["proposal_embeddings"]) == 5  # answers (secondary V_output)
    assert len(r0["shown_sample_embeddings"]) == 4  # shown reasoning skeletons


def test_build_reasoning_prompt_frames_reasoning() -> None:
    p = build_reasoning_prompt(name="X", viewpoint="V", topic="T",
                               reasoning_notes=["strat a", "strat b"])
    assert "How other agents reasoned" in p and "- strat a" in p and "Persona: X" in p
