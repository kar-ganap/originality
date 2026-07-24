"""Token-free tests for the rung-1/2 confirmatory analysis: it groups the 24 paired artifacts, fires
the collapse criterion when a channel's V falls below both controls, else stays silent — and the
``v_embeddings_key`` runs it on either the output or the reasoning channel independently."""

from __future__ import annotations

import numpy as np
import pytest

from whitespace1.rung1_confirm import ConfirmThresholds, evaluate_confirmatory_artifacts

DIM = 32
E = np.eye(DIM)
P, D, A, U = E[0], E[1], E[2], E[3]  # popularity / decoy / ablation / uniform anchor directions
FLAT = [0.3] * 8


def _cluster(center: np.ndarray, c: float, seed: int, n: int = 5) -> np.ndarray:
    """n unit vectors whose pairwise cosine ≈ c (so V_pair ≈ 1 − c)."""
    rng = np.random.default_rng(seed)
    perp = rng.normal(size=(n, DIM))
    perp = perp - np.outer(perp @ center, center)
    perp = perp / np.linalg.norm(perp, axis=1, keepdims=True)
    a, b = np.sqrt(c), np.sqrt(1.0 - c)
    x = a * center[None, :] + b * perp
    return x / np.linalg.norm(x, axis=1, keepdims=True)


def _artifact(topic_id, run_id, condition, c_traj, center, seed, p_top4=None,  # noqa: ANN001, ANN202
              skel_c_traj=None, skel_center=None):
    skel_c_traj = skel_c_traj if skel_c_traj is not None else c_traj  # default: mirror output
    skel_center = skel_center if skel_center is not None else center
    rounds = []
    for t, c in enumerate(c_traj):
        skel = _cluster(skel_center, skel_c_traj[t], seed * 100 + t + 7)
        rd: dict = {
            "proposal_embeddings": _cluster(center, c, seed * 100 + t).tolist(),
            "skeleton_embeddings": skel.tolist(),
        }
        if condition in ("popularity", "uniform"):
            rd["post_echo_top4_share"] = float(p_top4[t])
        if condition == "popularity":
            rd["shown_sample_embeddings"] = np.tile(P, (4, 1)).tolist()
            rd["decoy_embeddings"] = np.tile(D, (4, 1)).tolist()
        rounds.append(rd)
    return {
        "config": {"topic_id": topic_id, "run_identifier": run_id, "condition": condition},
        "rounds": rounds,
    }


def _dataset(pop_c_traj, skel_pop_c_traj=None) -> list[dict]:  # noqa: ANN001
    """8 paired triplets (4 per topic × 2). Popularity outputs cluster on P (high uptake); ablation
    and uniform stay flat. ``skel_pop_c_traj`` sets the popularity skeleton trajectory (defaults to
    the output one); ablation/uniform skeletons stay flat."""
    pop_top4 = [0.20 + 0.03 * t for t in range(8)]
    uni_top4 = [0.20] * 8
    artifacts = []
    for topic in ("topic-a", "topic-b"):
        for k in range(4):
            rid = f"{topic}-run{k}"
            s = hash((topic, k)) % 1000
            artifacts += [
                _artifact(topic, rid, "popularity", pop_c_traj, P, s + 1, pop_top4,
                          skel_c_traj=skel_pop_c_traj, skel_center=P),
                _artifact(topic, rid, "uniform", FLAT, U, s + 2, uni_top4,
                          skel_c_traj=FLAT, skel_center=U),
                _artifact(topic, rid, "ablation", FLAT, A, s + 3, skel_c_traj=FLAT, skel_center=A),
            ]
    return artifacts


_TH = ConfirmThresholds(bootstrap_samples=300, bootstrap_seed=20260718)


def test_groups_eight_paired_triplets() -> None:
    assert evaluate_confirmatory_artifacts(_dataset(FLAT), thresholds=_TH).run_count == 8


def test_collapse_fires_when_popularity_v_falls_below_both_controls() -> None:
    rising_c = list(np.linspace(0.2, 0.85, 8))  # V falls hard, below the flat controls
    result = evaluate_confirmatory_artifacts(_dataset(rising_c), thresholds=_TH)
    assert result.dynamic_uptake_passed and result.feedback_passed
    assert result.popularity_v_slope < 0 and result.popularity_v_upper < 0
    assert result.collapse_passed


def test_no_collapse_when_popularity_v_rises() -> None:
    falling_c = list(np.linspace(0.85, 0.2, 8))  # V rises (Polyphony's null shape)
    result = evaluate_confirmatory_artifacts(_dataset(falling_c), thresholds=_TH)
    assert result.dynamic_uptake_passed and result.popularity_v_slope > 0
    assert not result.collapse_passed


def test_two_channel_split_reasoning_collapses_where_output_holds() -> None:
    # output V flat (holds); popularity SKELETON cosine rises => V_reason falls (collapses)
    rising = list(np.linspace(0.2, 0.85, 8))
    ds = _dataset(FLAT, skel_pop_c_traj=rising)
    out = evaluate_confirmatory_artifacts(
        ds, thresholds=_TH, v_embeddings_key="proposal_embeddings"
    )
    rea = evaluate_confirmatory_artifacts(
        ds, thresholds=_TH, v_embeddings_key="skeleton_embeddings"
    )
    assert not out.collapse_passed  # V_output holds
    assert rea.collapse_passed  # V_reason collapses — the rung-2 headline pattern


def test_uptake_key_runs_on_the_skeleton_channel() -> None:
    # reasoning-mode analysis path: both the collapse channel and the uptake source are skeletons
    r = evaluate_confirmatory_artifacts(
        _dataset(FLAT), thresholds=_TH,
        v_embeddings_key="skeleton_embeddings", uptake_embeddings_key="skeleton_embeddings",
    )
    assert r.run_count == 8 and r.dynamic_uptake_passed  # pop skeletons on P echo the shown-on-P


def test_requires_exactly_two_topics() -> None:
    one_topic = [a for a in _dataset(FLAT) if a["config"]["topic_id"] == "topic-a"]
    with pytest.raises(ValueError):
        evaluate_confirmatory_artifacts(one_topic, thresholds=_TH)
