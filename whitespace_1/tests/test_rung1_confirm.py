"""Token-free tests for the rung-1 confirmatory analysis: it groups the 24 paired artifacts, fires
the collapse criterion when popularity V falls below both controls, else stays silent."""

from __future__ import annotations

import numpy as np
import pytest

from whitespace1.rung1_confirm import (
    ConfirmThresholds,
    evaluate_confirmatory_artifacts,
)

DIM = 32
E = np.eye(DIM)
P, D, A, U = E[0], E[1], E[2], E[3]  # popularity / decoy / ablation / uniform anchor directions


def _cluster(center: np.ndarray, c: float, seed: int, n: int = 5) -> np.ndarray:
    """n unit vectors whose pairwise cosine ≈ c (so V_pair ≈ 1 − c)."""
    rng = np.random.default_rng(seed)
    perp = rng.normal(size=(n, DIM))
    perp = perp - np.outer(perp @ center, center)
    perp = perp / np.linalg.norm(perp, axis=1, keepdims=True)
    a, b = np.sqrt(c), np.sqrt(1.0 - c)
    x = a * center[None, :] + b * perp
    return x / np.linalg.norm(x, axis=1, keepdims=True)


def _artifact(topic_id, run_id, condition, c_traj, center, seed, p_top4=None):  # noqa: ANN001, ANN202
    rounds = []
    for t, c in enumerate(c_traj):
        rd: dict = {"proposal_embeddings": _cluster(center, c, seed * 100 + t).tolist()}
        if condition in ("popularity", "uniform"):
            rd["post_echo_top4_share"] = float(p_top4[t])
        if condition == "popularity":
            rd["shown_sample_embeddings"] = np.tile(P, (4, 1)).tolist()  # shown = popularity anchor
            rd["decoy_embeddings"] = np.tile(D, (4, 1)).tolist()  # decoy = orthogonal
        rounds.append(rd)
    return {
        "config": {"topic_id": topic_id, "run_identifier": run_id, "condition": condition},
        "rounds": rounds,
    }


def _dataset(pop_c_traj) -> list[dict]:  # noqa: ANN001
    """8 paired triplets (4 per topic × 2). Popularity outputs cluster on P (→ high uptake) with the
    given V trajectory; ablation and uniform stay flat; popularity P_top4 rises, uniform flat."""
    flat = [0.3] * 8
    pop_top4 = [0.20 + 0.03 * t for t in range(8)]
    uni_top4 = [0.20] * 8
    artifacts = []
    for topic in ("topic-a", "topic-b"):
        for k in range(4):
            rid = f"{topic}-run{k}"
            s = hash((topic, k)) % 1000
            artifacts += [
                _artifact(topic, rid, "popularity", pop_c_traj, P, s + 1, pop_top4),
                _artifact(topic, rid, "uniform", flat, U, s + 2, uni_top4),
                _artifact(topic, rid, "ablation", flat, A, s + 3),
            ]
    return artifacts


_TH = ConfirmThresholds(bootstrap_samples=300, bootstrap_seed=20260718)


def test_groups_eight_paired_triplets() -> None:
    result = evaluate_confirmatory_artifacts(_dataset([0.3] * 8), thresholds=_TH)
    assert result.run_count == 8


def test_collapse_fires_when_popularity_v_falls_below_both_controls() -> None:
    # popularity pairwise cosine rises 0.2 → 0.85 ⇒ V falls hard, well below the flat controls
    rising_c = list(np.linspace(0.2, 0.85, 8))
    result = evaluate_confirmatory_artifacts(_dataset(rising_c), thresholds=_TH)
    assert result.dynamic_uptake_passed  # popularity outputs sit on the shown anchor
    assert result.feedback_passed  # popularity P_top4 rises faster than uniform
    assert result.popularity_v_slope < 0 and result.popularity_v_upper < 0
    assert result.collapse_passed


def test_no_collapse_when_popularity_v_rises() -> None:
    # popularity pairwise cosine falls 0.85 → 0.2 ⇒ V rises (Polyphony's null shape)
    falling_c = list(np.linspace(0.85, 0.2, 8))
    result = evaluate_confirmatory_artifacts(_dataset(falling_c), thresholds=_TH)
    assert result.dynamic_uptake_passed  # actuator still live
    assert result.popularity_v_slope > 0
    assert not result.collapse_passed


def test_requires_exactly_two_topics() -> None:
    one_topic = [a for a in _dataset([0.3] * 8) if a["config"]["topic_id"] == "topic-a"]
    with pytest.raises(ValueError):
        evaluate_confirmatory_artifacts(one_topic, thresholds=_TH)
