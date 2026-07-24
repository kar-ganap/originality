"""Rung-1 confirmatory analysis — the R4 collapse criterion via hierarchical bootstrap.

Ported from ``polyphony/src/polyphony/walk_r4_confirm.py`` (the prepared-gram path), verbatim in
estimand and thresholds. Reads the 24 R4 artifacts and returns Polyphony's three ordered verdicts:
**dynamic uptake** (actuator live), **popularity feedback**, and **collapse** — the last requiring
popularity V slope < 0 *and* all three bootstrap 95% upper bounds (pop, pop-ablation, pop-uniform)
below zero. Grouping uses this port's ``topic_id`` field (Polyphony used ``topic``). Token-free;
bootstrap seed pinned to Polyphony's 20260718 for comparability.
"""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import cast

import numpy as np
import numpy.typing as npt

from .rung0 import mean_pairwise_cosine

Artifact = Mapping[str, object]
FloatMatrix = npt.NDArray[np.float64]
FloatVector = npt.NDArray[np.float64]


@dataclass(frozen=True)
class ConfirmThresholds:
    bootstrap_samples: int = 10_000
    bootstrap_seed: int = 20260718


@dataclass(frozen=True)
class ConfirmatoryResult:
    run_count: int
    mean_uptake_delta: float
    uptake_lower: float
    mean_feedback_contrast: float
    feedback_lower: float
    popularity_v_slope: float
    popularity_v_upper: float
    popularity_minus_ablation_v: float
    popularity_minus_ablation_upper: float
    popularity_minus_uniform_v: float
    popularity_minus_uniform_upper: float
    dynamic_uptake_passed: bool
    feedback_passed: bool
    collapse_passed: bool


@dataclass(frozen=True)
class _PairedRun:
    topic: str
    run_identifier: str
    popularity: Artifact
    uniform: Artifact
    ablation: Artifact


@dataclass(frozen=True)
class _PreparedPair:
    topic: str
    popularity_grams: tuple[FloatMatrix, ...]
    uniform_grams: tuple[FloatMatrix, ...]
    ablation_grams: tuple[FloatMatrix, ...]
    popularity_uptake: tuple[FloatVector, ...]
    ablation_shadow_uptake: tuple[FloatVector, ...]
    popularity_p_slope: float
    uniform_p_slope: float


def evaluate_confirmatory_artifacts(
    artifacts: Sequence[Artifact], *, thresholds: ConfirmThresholds
) -> ConfirmatoryResult:
    """Evaluate the eight fresh R4 pairs using only persisted raw artifact fields."""
    if thresholds.bootstrap_samples < 1:
        raise ValueError("bootstrap_samples must be positive")
    pairs_by_topic = _paired_runs(artifacts)
    prepared_by_topic = {
        topic: tuple(_prepare_pair(pair) for pair in topic_pairs)
        for topic, topic_pairs in pairs_by_topic.items()
    }
    pairs = tuple(pair for topic_pairs in prepared_by_topic.values() for pair in topic_pairs)
    point = _prepared_summary(pairs, rng=None)
    rng = np.random.default_rng(thresholds.bootstrap_seed)
    draws = np.asarray(
        [
            _prepared_summary(_resample_prepared(prepared_by_topic, rng), rng=rng)
            for _ in range(thresholds.bootstrap_samples)
        ],
        dtype=np.float64,
    )
    uptake_lower, feedback_lower = np.quantile(draws[:, :2], 0.025, axis=0)
    pop_v_upper, pop_abl_upper, pop_uniform_upper = np.quantile(draws[:, 2:], 0.975, axis=0)
    dynamic = bool(point[0] > 0.0 and uptake_lower > 0.0)
    feedback = bool(dynamic and point[1] > 0.0 and feedback_lower > 0.0)
    collapse = bool(
        feedback
        and point[2] < 0.0
        and pop_v_upper < 0.0
        and pop_abl_upper < 0.0
        and pop_uniform_upper < 0.0
    )
    return ConfirmatoryResult(
        run_count=len(pairs),
        mean_uptake_delta=float(point[0]),
        uptake_lower=float(uptake_lower),
        mean_feedback_contrast=float(point[1]),
        feedback_lower=float(feedback_lower),
        popularity_v_slope=float(point[2]),
        popularity_v_upper=float(pop_v_upper),
        popularity_minus_ablation_v=float(point[3]),
        popularity_minus_ablation_upper=float(pop_abl_upper),
        popularity_minus_uniform_v=float(point[4]),
        popularity_minus_uniform_upper=float(pop_uniform_upper),
        dynamic_uptake_passed=dynamic,
        feedback_passed=feedback,
        collapse_passed=collapse,
    )


def _paired_runs(artifacts: Sequence[Artifact]) -> dict[str, tuple[_PairedRun, ...]]:
    grouped: dict[str, dict[str, dict[str, Artifact]]] = defaultdict(lambda: defaultdict(dict))
    for artifact in artifacts:
        config = artifact.get("config")
        if not isinstance(config, Mapping):
            raise ValueError("R4 artifact is missing configuration")
        topic = config.get("topic_id")
        run_identifier = config.get("run_identifier")
        condition = config.get("condition")
        if not (
            isinstance(topic, str)
            and isinstance(run_identifier, str)
            and isinstance(condition, str)
        ):
            raise ValueError("R4 config must contain topic_id, run_identifier, and condition")
        if condition not in {"popularity", "uniform", "ablation"}:
            raise ValueError("R4 artifact has an unknown condition")
        if condition in grouped[topic][run_identifier]:
            raise ValueError("R4 artifact condition is duplicated within a paired identifier")
        grouped[topic][run_identifier][condition] = artifact
    if len(grouped) != 2:
        raise ValueError("R4 confirmation requires exactly two topics")
    result: dict[str, tuple[_PairedRun, ...]] = {}
    for topic, run_map in grouped.items():
        if len(run_map) != 4:
            raise ValueError("R4 confirmation requires four complete paired identifiers per topic")
        topic_pairs: list[_PairedRun] = []
        for run_identifier, conditions in run_map.items():
            if set(conditions) != {"popularity", "uniform", "ablation"}:
                raise ValueError("R4 confirmation requires complete paired condition triplets")
            topic_pairs.append(
                _PairedRun(
                    topic=topic,
                    run_identifier=run_identifier,
                    popularity=conditions["popularity"],
                    uniform=conditions["uniform"],
                    ablation=conditions["ablation"],
                )
            )
        result[topic] = tuple(topic_pairs)
    return result


def _resample_prepared(
    pairs_by_topic: Mapping[str, tuple[_PreparedPair, ...]], rng: np.random.Generator
) -> tuple[_PreparedPair, ...]:
    selected: list[_PreparedPair] = []
    for topic_pairs in pairs_by_topic.values():
        indices = rng.integers(0, len(topic_pairs), size=len(topic_pairs))
        selected.extend(topic_pairs[int(index)] for index in indices)
    return tuple(selected)


def _prepare_pair(pair: _PairedRun) -> _PreparedPair:
    popularity_rounds = _rounds(pair.popularity)
    uniform_rounds = _rounds(pair.uniform)
    ablation_rounds = _rounds(pair.ablation)
    if not (len(popularity_rounds) == len(uniform_rounds) == len(ablation_rounds)):
        raise ValueError("R4 paired runs must have matching round counts")
    pop_out = tuple(_matrix(item, "proposal_embeddings") for item in popularity_rounds)
    uni_out = tuple(_matrix(item, "proposal_embeddings") for item in uniform_rounds)
    abl_out = tuple(_matrix(item, "proposal_embeddings") for item in ablation_rounds)
    shown = tuple(_matrix(item, "shown_sample_embeddings") for item in popularity_rounds)
    decoy = tuple(_matrix(item, "decoy_embeddings") for item in popularity_rounds)
    return _PreparedPair(
        topic=pair.topic,
        popularity_grams=tuple(_cosine_gram(o) for o in pop_out),
        uniform_grams=tuple(_cosine_gram(o) for o in uni_out),
        ablation_grams=tuple(_cosine_gram(o) for o in abl_out),
        popularity_uptake=tuple(
            np.asarray(_uptake(o, s, d), dtype=np.float64)
            for o, s, d in zip(pop_out, shown, decoy, strict=True)
        ),
        ablation_shadow_uptake=tuple(
            np.asarray(_uptake(o, s, d), dtype=np.float64)
            for o, s, d in zip(abl_out, shown, decoy, strict=True)
        ),
        popularity_p_slope=_p_top4_slope(pair.popularity),
        uniform_p_slope=_p_top4_slope(pair.uniform),
    )


def _prepared_summary(
    pairs: Sequence[_PreparedPair], *, rng: np.random.Generator | None
) -> npt.NDArray[np.float64]:
    uptake, feedback, pop_v, pop_abl, pop_uni = [], [], [], [], []
    for pair in pairs:
        if rng is None:
            indices = None
        else:
            indices = tuple(
                rng.integers(0, gram.shape[0], size=5, dtype=np.intp)
                for gram in pair.popularity_grams
            )
        v_pop = _prepared_v_slope(pair.popularity_grams, indices)
        v_uni = _prepared_v_slope(pair.uniform_grams, indices)
        v_abl = _prepared_v_slope(pair.ablation_grams, indices)
        uptake.append(_prepared_uptake(pair, indices))
        feedback.append(pair.popularity_p_slope - pair.uniform_p_slope)
        pop_v.append(v_pop)
        pop_abl.append(v_pop - v_abl)
        pop_uni.append(v_pop - v_uni)
    return np.asarray(
        [np.mean(uptake), np.mean(feedback), np.mean(pop_v), np.mean(pop_abl), np.mean(pop_uni)],
        dtype=np.float64,
    )


def _prepared_uptake(
    pair: _PreparedPair, indices: tuple[npt.NDArray[np.intp], ...] | None
) -> float:
    pop_scores: list[FloatVector] = []
    abl_scores: list[FloatVector] = []
    for round_index, (popularity, ablation) in enumerate(
        zip(pair.popularity_uptake, pair.ablation_shadow_uptake, strict=True)
    ):
        if indices is not None:
            popularity = popularity[indices[round_index]]
            ablation = ablation[indices[round_index]]
        pop_scores.append(popularity)
        abl_scores.append(ablation)
    return float(np.mean(np.concatenate(pop_scores)) - np.mean(np.concatenate(abl_scores)))


def _prepared_v_slope(
    round_grams: Sequence[FloatMatrix], indices: tuple[npt.NDArray[np.intp], ...] | None
) -> float:
    values = [
        _v_from_gram(gram, None if indices is None else indices[round_index])
        for round_index, gram in enumerate(round_grams)
    ]
    return _slope(values)


def _cosine_gram(embeddings: FloatMatrix) -> FloatMatrix:
    normalized = _normalize_rows(embeddings)
    return cast(FloatMatrix, normalized @ normalized.T)


def _v_from_gram(gram: FloatMatrix, indices: npt.NDArray[np.intp] | None) -> float:
    selected = gram if indices is None else gram[np.ix_(indices, indices)]
    n_agents = selected.shape[0]
    if n_agents < 2:
        return 0.0
    upper = selected[np.triu_indices(n_agents, k=1)]
    return float(np.mean(1.0 - upper))


def _p_top4_slope(artifact: Artifact) -> float:
    values = [round_item.get("post_echo_top4_share") for round_item in _rounds(artifact)]
    if not all(isinstance(value, (int, float)) for value in values):
        raise ValueError("shared R4 artifact is missing P_top4 values")
    return _slope([float(cast("int | float", value)) for value in values])


def _uptake(outputs: FloatMatrix, shown: FloatMatrix, decoy: FloatMatrix) -> list[float]:
    out = _normalize_rows(outputs)
    shown_n = _normalize_rows(shown)
    decoy_n = _normalize_rows(decoy)
    return list(np.max(out @ shown_n.T, axis=1) - np.max(out @ decoy_n.T, axis=1))


def _rounds(artifact: Artifact) -> Sequence[Mapping[str, object]]:
    rounds = artifact.get("rounds")
    if not isinstance(rounds, Sequence) or isinstance(rounds, (str, bytes)):
        raise ValueError("R4 artifact rounds must be a sequence")
    if not all(isinstance(round_item, Mapping) for round_item in rounds):
        raise ValueError("R4 artifact rounds must contain mappings")
    return cast("Sequence[Mapping[str, object]]", rounds)


def _matrix(round_item: Mapping[str, object], key: str) -> FloatMatrix:
    matrix = np.asarray(round_item.get(key), dtype=np.float64)
    if matrix.ndim != 2 or matrix.shape[0] == 0 or matrix.shape[1] == 0:
        raise ValueError(f"R4 artifact {key} must be a non-empty matrix")
    return matrix


def _normalize_rows(matrix: FloatMatrix) -> FloatMatrix:
    norms = np.linalg.norm(matrix, axis=1, keepdims=True)
    if bool(np.any(norms == 0.0)):
        raise ValueError("R4 embeddings must not contain all-zero rows")
    return cast(FloatMatrix, matrix / norms)


def _slope(values: Sequence[float]) -> float:
    if len(values) < 2:
        raise ValueError("R4 slope requires at least two rounds")
    return float(np.polyfit(np.arange(len(values), dtype=np.float64), values, 1)[0])


# `mean_pairwise_cosine` is re-exported so callers can recompute a non-bootstrap V if needed;
# the gram path above is the bootstrap-efficient equivalent (identical definition).
__all__ = [
    "ConfirmThresholds",
    "ConfirmatoryResult",
    "evaluate_confirmatory_artifacts",
    "mean_pairwise_cosine",
]
