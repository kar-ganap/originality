"""Matched null for rung-1 R4's ``P_top4`` concentration statistic (the Gate-2 secondary).

Ported from ``polyphony/src/polyphony/null_p_top4.py``, verbatim in mechanism. ``P_top4`` is a
fixed-k share of a catalog that grows 13 → 48 over the eight rounds, so a perfectly even catalog's
top-4 share falls by construction. This re-runs R4's exact echo-accumulation process with the
preference mechanisms switched off, one at a time, to ask whether the popularity arm's recurrence
is a property of the sampling rule rather than of anything the ensemble did.

``replay_run`` is the positive control: it reconstructs each run's ``P_top4`` from ``pre_catalog``
+ the embeddings + ``shown_sample_ids`` **without** reading ``post_echo_top4_share``, so agreement
validates the process model. The three nulls: STRUCTURE (uniform sampling, identical boost),
HETEROGENEOUS (uniform sampling, echoes resampled from the pooled observed similarities), POPULARITY
(weight-proportional sampling with HETEROGENEOUS echoes — the matched null for the treatment arm).
The decisive comparison is POPULARITY minus its null.
"""

from __future__ import annotations

import json
from collections.abc import Callable, Iterable, Sequence
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

import numpy as np
import numpy.typing as npt

FloatArray = npt.NDArray[np.float64]

TOP_K = 4
N_SEED_ITEMS = 8
N_AGENTS = 5
EXPOSURE_BUDGET = 4
N_ROUNDS = 8


class NullMode(str, Enum):
    STRUCTURE = "structure"
    HETEROGENEOUS = "heterogeneous"
    POPULARITY = "popularity"


def top_k_share(weights: Sequence[float] | FloatArray, k: int = TOP_K) -> float:
    array = np.asarray(weights, dtype=np.float64)
    total = float(array.sum())
    if total <= 0.0:
        return 0.0
    return float(np.sort(array)[::-1][:k].sum() / total)


def even_share(n_items: int, k: int = TOP_K) -> float:
    """``top_k_share`` on a perfectly even catalog — the denominator that silently varies."""
    return k / float(n_items)


def _unit_rows(matrix: FloatArray) -> FloatArray:
    norms = np.linalg.norm(matrix, axis=1, keepdims=True)
    return np.asarray(matrix / norms, dtype=np.float64)


def round_similarities(round_record: dict[str, Any]) -> FloatArray:
    """The (n_agents, n_shown) clipped cosines that drove one round's echo update."""
    outputs = _unit_rows(np.asarray(round_record["proposal_embeddings"], dtype=np.float64))
    shown = _unit_rows(np.asarray(round_record["shown_sample_embeddings"], dtype=np.float64))
    return np.maximum(outputs @ shown.T, 0.0)


def replay_run(run: dict[str, Any]) -> list[float]:
    """Positive control: reconstruct a run's ``P_top4`` from committed raw fields only."""
    trajectory: list[float] = []
    for record in run["rounds"]:
        if record.get("post_echo_top4_share") is None:
            continue
        catalog = record["pre_catalog"]
        weights = np.array([item["echo_weight"] for item in catalog], dtype=np.float64)
        position = {item["id"]: index for index, item in enumerate(catalog)}
        similarities = round_similarities(record)
        for column, item_id in enumerate(record["shown_sample_ids"]):
            weights[position[item_id]] += float(similarities[:, column].sum())
        weights = np.concatenate([weights, np.ones(similarities.shape[0], dtype=np.float64)])
        trajectory.append(top_k_share(weights))
    return trajectory


def pooled_similarities(runs: Iterable[dict[str, Any]]) -> FloatArray:
    """Every clipped cosine across the runs — the nulls resample echo magnitudes from this pool."""
    values: list[FloatArray] = []
    for run in runs:
        for record in run["rounds"]:
            if record.get("post_echo_top4_share") is None:
                continue
            values.append(round_similarities(record).ravel())
    if not values:
        raise ValueError("no rounds with a defined P_top4 were supplied")
    return np.concatenate(values)


def simulate(
    rng: np.random.Generator,
    mode: NullMode,
    similarity_pool: FloatArray,
    *,
    n_rounds: int = N_ROUNDS,
    n_seed: int = N_SEED_ITEMS,
    n_agents: int = N_AGENTS,
    exposure: int = EXPOSURE_BUDGET,
) -> list[float]:
    """One null replicate of R4's generative process. Returns the ``P_top4`` trajectory."""
    weights: FloatArray = np.ones(n_seed, dtype=np.float64)
    mean_similarity = float(similarity_pool.mean())
    trajectory: list[float] = []
    for _ in range(n_rounds):
        n_items = len(weights)
        if mode is NullMode.POPULARITY:
            probabilities = weights / weights.sum()
            shown = rng.choice(n_items, size=exposure, replace=False, p=probabilities)
        else:
            shown = rng.choice(n_items, size=exposure, replace=False)
        if mode is NullMode.STRUCTURE:
            boosts = np.full(exposure, mean_similarity * n_agents, dtype=np.float64)
        else:
            draws = rng.choice(similarity_pool, size=(n_agents, exposure), replace=True)
            boosts = draws.sum(axis=0)
        weights[shown] += boosts
        weights = np.concatenate([weights, np.ones(n_agents, dtype=np.float64)])
        trajectory.append(top_k_share(weights))
    return trajectory


def slope(values: Sequence[float]) -> float:
    y = np.asarray(values, dtype=np.float64)
    return float(np.polyfit(np.arange(len(y), dtype=np.float64), y, 1)[0])


def normalized_trajectory(
    values: Sequence[float], *, n_seed: int = N_SEED_ITEMS, n_agents: int = N_AGENTS
) -> list[float]:
    """``P_top4`` as a multiple of its even-catalog share — removes the growing denominator."""
    return [
        value / even_share(n_seed + n_agents * (index + 1)) for index, value in enumerate(values)
    ]


@dataclass(frozen=True)
class ArmSummary:
    label: str
    n: int
    raw_slope: float
    normalized_slope: float


@dataclass(frozen=True)
class Comparison:
    """One observed arm placed in its matched null's distribution of equal-sized means."""

    arm: str
    null_mode: str
    metric: str
    observed: float
    null_mean: float
    null_band: tuple[float, float]
    p_value: float

    @property
    def excess(self) -> float:
        return self.observed - self.null_mean


@dataclass
class NullStudy:
    observed: dict[str, ArmSummary] = field(default_factory=dict)
    null: dict[str, ArmSummary] = field(default_factory=dict)
    comparisons: list[Comparison] = field(default_factory=list)
    replay_max_error: float = float("nan")
    n_replicates: int = 0
    pool_size: int = 0
    pool_mean: float = float("nan")


MATCHED_NULL: dict[str, NullMode] = {
    "uniform": NullMode.HETEROGENEOUS,
    "popularity": NullMode.POPULARITY,
}


def compare_to_null(
    rng: np.random.Generator,
    arm: str,
    observed_trajectories: Sequence[Sequence[float]],
    null_trajectories: Sequence[Sequence[float]],
    *,
    null_mode: str,
    n_resamples: int = 20_000,
) -> list[Comparison]:
    """Place each observed arm mean inside its null's distribution of equal-sized means."""
    def _normalized_slope(trajectory: Sequence[float]) -> float:
        return slope(normalized_trajectory(trajectory))

    results: list[Comparison] = []
    metrics: tuple[tuple[str, Callable[[Sequence[float]], float]], ...] = (
        ("raw", slope),
        ("normalized", _normalized_slope),
    )
    for metric, statistic in metrics:
        observed = float(np.mean([statistic(t) for t in observed_trajectories]))
        null = np.array([statistic(t) for t in null_trajectories], dtype=np.float64)
        group_means = null[
            rng.integers(0, len(null), size=(n_resamples, len(observed_trajectories)))
        ].mean(axis=1)
        upper = float((group_means >= observed).mean())
        results.append(
            Comparison(
                arm=arm,
                null_mode=null_mode,
                metric=metric,
                observed=observed,
                null_mean=float(null.mean()),
                null_band=(
                    float(np.percentile(group_means, 2.5)),
                    float(np.percentile(group_means, 97.5)),
                ),
                p_value=2.0 * min(upper, 1.0 - upper),
            )
        )
    return results


def _summarize(label: str, trajectories: Sequence[Sequence[float]]) -> ArmSummary:
    raw = np.array([slope(t) for t in trajectories], dtype=np.float64)
    norm = np.array([slope(normalized_trajectory(t)) for t in trajectories], dtype=np.float64)
    return ArmSummary(label=label, n=len(trajectories), raw_slope=float(raw.mean()),
                      normalized_slope=float(norm.mean()))


def load_runs(runs_dir: Path) -> dict[str, list[dict[str, Any]]]:
    """Group rung-1 R4 artifacts by condition, skipping the ablation (P_top4 undefined there)."""
    grouped: dict[str, list[dict[str, Any]]] = {}
    for path in sorted(runs_dir.glob("*.json")):
        payload = json.loads(path.read_text())
        if "rounds" not in payload:
            continue
        condition = str(payload.get("config", {}).get("condition", ""))
        if condition == "ablation":
            continue
        grouped.setdefault(condition, []).append(payload)
    return grouped


def run_study(runs_dir: Path, *, n_replicates: int = 2000, seed: int = 20260725) -> NullStudy:
    """Replay the observed arms (positive control), then run each null n_replicates times."""
    grouped = load_runs(runs_dir)
    if not grouped:
        raise ValueError(f"no R4 runs found under {runs_dir}")
    study = NullStudy(n_replicates=n_replicates)
    errors: list[float] = []
    observed_trajectories: dict[str, list[list[float]]] = {}
    for condition, runs in sorted(grouped.items()):
        trajectories = []
        for run in runs:
            replayed = replay_run(run)
            expected = [
                r["post_echo_top4_share"]
                for r in run["rounds"]
                if r.get("post_echo_top4_share") is not None
            ]
            errors.extend(abs(a - b) for a, b in zip(replayed, expected, strict=True))
            trajectories.append(replayed)
        observed_trajectories[condition] = trajectories
        study.observed[condition] = _summarize(condition, trajectories)
    study.replay_max_error = max(errors) if errors else float("nan")
    pool = pooled_similarities(run for runs in grouped.values() for run in runs)
    study.pool_size = int(pool.size)
    study.pool_mean = float(pool.mean())
    rng = np.random.default_rng(seed)
    null_trajectories: dict[str, list[list[float]]] = {}
    for mode in NullMode:
        replicates = [simulate(rng, mode, pool) for _ in range(n_replicates)]
        null_trajectories[mode.value] = replicates
        study.null[mode.value] = _summarize(mode.value, replicates)
    for arm, mode in MATCHED_NULL.items():
        if arm not in observed_trajectories:
            continue
        study.comparisons.extend(
            compare_to_null(
                rng, arm, observed_trajectories[arm], null_trajectories[mode.value],
                null_mode=mode.value,
            )
        )
    return study
