"""The shared-catalog exposure actuator (rung 1). Every generated idea is retained.

Ported verbatim (mechanism unchanged) from ``polyphony/src/polyphony/catalog.py``. The faithful R4
actuator: append-only, popularity = cumulative semantic echo weight, sampled without replacement
from an immutable pre-round snapshot. No LLM dependency — pure and token-free.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import cast

import numpy as np
import numpy.typing as npt

FloatVector = npt.NDArray[np.float64]
FloatMatrix = npt.NDArray[np.float64]


@dataclass(frozen=True)
class Idea:
    id: str
    text: str
    embedding: FloatVector
    round_index: int
    persona_name: str = ""


@dataclass(frozen=True)
class SamplingConfig:
    sigma: float
    exposure_budget: int
    popularity_weighted: bool = True
    isolated: bool = False

    def __post_init__(self) -> None:
        if not 0.0 <= self.sigma <= 1.0:
            raise ValueError("sigma must be between 0 and 1")
        if self.exposure_budget < 0:
            raise ValueError("exposure_budget must not be negative")


class Catalog:
    """Append-only catalog with popularity-weighted or uniform exposure sampling."""

    def __init__(self, *, embedding_dimensions: int) -> None:
        if embedding_dimensions < 2:
            raise ValueError("embedding_dimensions must be at least 2")
        self.embedding_dimensions = embedding_dimensions
        self._ideas: list[Idea] = []
        self._echo_weights: list[float] = []

    @property
    def ideas(self) -> tuple[Idea, ...]:
        return tuple(self._ideas)

    @property
    def echo_weights(self) -> npt.NDArray[np.float64]:
        """Popularity weights produced by semantic echo, not by sampling alone."""
        return np.asarray(self._echo_weights, dtype=np.float64)

    def embeddings(self) -> FloatMatrix:
        if not self._ideas:
            return np.empty((0, self.embedding_dimensions), dtype=np.float64)
        return cast(FloatMatrix, np.vstack([idea.embedding for idea in self._ideas]))

    def add(
        self, *, text: str, embedding: npt.ArrayLike, round_index: int, persona_name: str = ""
    ) -> Idea:
        vector = _unit_vector(embedding, dimensions=self.embedding_dimensions)
        idea = Idea(
            id=f"idea-{len(self._ideas)}",
            text=text,
            embedding=vector,
            round_index=round_index,
            persona_name=persona_name,
        )
        self._ideas.append(idea)
        self._echo_weights.append(1.0)
        return idea

    def sample(self, config: SamplingConfig, *, rng: np.random.Generator) -> tuple[Idea, ...]:
        """Select shared exposure from a weight snapshot without mutating the catalog."""
        if config.isolated or not self._ideas or config.exposure_budget == 0:
            return ()
        if float(rng.random()) >= config.sigma:
            return ()
        count = min(config.exposure_budget, len(self._ideas))
        probabilities: npt.NDArray[np.float64] | None
        if config.popularity_weighted:
            weights = self.echo_weights
            probabilities = weights / weights.sum()
        else:
            probabilities = None
        selected = np.asarray(
            rng.choice(len(self._ideas), size=count, replace=False, p=probabilities), dtype=np.intp
        )
        return tuple(self._ideas[int(index)] for index in selected)

    def record_echoes(
        self, *, samples: tuple[tuple[Idea, ...], ...], output_embeddings: npt.ArrayLike
    ) -> None:
        """Increase sampled-item popularity only when a generated output semantically echoes it."""
        outputs = np.asarray(output_embeddings, dtype=np.float64)
        if outputs.ndim != 2 or outputs.shape != (len(samples), self.embedding_dimensions):
            raise ValueError("output_embeddings must align with samples and catalog dimensions")
        positions = {idea.id: index for index, idea in enumerate(self._ideas)}
        for sample, output in zip(samples, outputs, strict=True):
            output_unit = _unit_vector(output, dimensions=self.embedding_dimensions)
            for idea in sample:
                similarity = float(output_unit @ idea.embedding)
                self._echo_weights[positions[idea.id]] += max(similarity, 0.0)


def _unit_vector(values: npt.ArrayLike, *, dimensions: int) -> FloatVector:
    vector = np.asarray(values, dtype=np.float64)
    if vector.ndim != 1 or vector.shape[0] != dimensions:
        raise ValueError(f"embedding must have shape ({dimensions},)")
    norm = float(np.linalg.norm(vector))
    if norm == 0.0:
        raise ValueError("embedding must not be all zeros")
    return cast(FloatVector, vector / norm)
