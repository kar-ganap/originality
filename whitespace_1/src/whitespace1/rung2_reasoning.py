"""Rung 2, second variant — the catalog-of-**reasoning** actuator (``ws1-oss-rung2-result.md``).

Where catalog-of-conclusions shows agents each other's *answers*, this shows them each other's
*reasoning skeletons*: each round the strategy skeleton is extracted from every trace and appended
to the shared catalog, so the next round's agents condition on prior **reasoning**, not conclusions.
The mechanism question (design note §9.4): does reasoning-exposure homogenize reasoning? This is the
actuator a proprietary API structurally cannot run.

Reuses rung-1's ``Catalog`` actuator and the R4 helpers verbatim. Two channels: ``V_reason`` (the
agents' skeletons — the primary here, since the actuator acts on reasoning) and ``V_output`` (the
answers — secondary). Extraction is **inline** (on the critical path), so the loop takes an injected
``extract_many``. Token-free except the injected provider.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import asdict, dataclass
from typing import Any

import numpy as np
from numpy.typing import NDArray

from .catalog import Catalog
from .rung0 import mean_pairwise_cosine
from .rung1_r4 import (
    WALK_INSTRUCTIONS,
    PreCatalogIdea,
    R4Config,
    R4Provider,
    _decoy,
    _ideas_matrix,
    _sample,
    _snapshot,
    _top4_share,
    _uptake,
)
from .stimuli import ROLES

FloatMatrix = NDArray[np.float64]


def build_reasoning_prompt(
    *, name: str, viewpoint: str, topic: str, reasoning_notes: Sequence[str]
) -> str:
    """The reasoning-framed prompt: the shared field is other agents' reasoning, not answers."""
    lines = (
        "\n".join(f"- {note}" for note in reasoning_notes)
        if reasoning_notes
        else "- none available this round."
    )
    return (
        f"{WALK_INSTRUCTIONS}\n\n"
        f"Persona: {name}\nViewpoint: {viewpoint}\nTopic: {topic}\n"
        f"How other agents reasoned about this:\n{lines}"
    )


@dataclass(frozen=True)
class R4ReasoningRound:
    round_index: int
    pre_catalog: tuple[PreCatalogIdea, ...]
    shown_sample_ids: tuple[str, ...]
    shown_sample_embeddings: FloatMatrix  # shown reasoning skeletons
    decoy_ids: tuple[str, ...]
    decoy_embeddings: FloatMatrix
    answers: tuple[str, ...]
    answer_embeddings: FloatMatrix
    skeletons: tuple[str, ...]
    skeleton_embeddings: FloatMatrix
    item_uptake: tuple[float, ...] | None
    v_output: float
    v_reason: float
    post_echo_top4_share: float | None


@dataclass(frozen=True)
class R4ReasoningRun:
    config: R4Config
    persona_embeddings: FloatMatrix
    rounds: tuple[R4ReasoningRound, ...]


def run_r4_reasoning(
    *,
    provider: R4Provider,
    config: R4Config,
    extract_many: Callable[[Sequence[str]], list[str]],
) -> R4ReasoningRun:
    """One append-only R4 condition whose catalog holds reasoning skeletons. ``propose_many`` must
    build reasoning prompts (:func:`build_reasoning_prompt`); ``extract_many`` turns the round's
    traces into strategy skeletons, which become the next round's shared catalog."""
    personas = list(ROLES)
    persona_embeddings = provider.embed([p.descriptor for p in personas])
    seed_embeddings = provider.embed(list(config.seed_catalog))
    catalog = Catalog(embedding_dimensions=persona_embeddings.shape[1])
    for text, embedding in zip(config.seed_catalog, seed_embeddings, strict=True):
        catalog.add(text=text, embedding=embedding, round_index=-1, persona_name="seed")
    sample_rng = np.random.default_rng(config.sampling_seed)
    decoy_rng = np.random.default_rng(config.decoy_seed)
    rounds: list[R4ReasoningRound] = []

    for round_index in range(config.rounds):
        pre_catalog = _snapshot(catalog)
        sample = _sample(catalog=catalog, config=config, rng=sample_rng)
        decoy = _decoy(catalog=catalog, sample=sample, rng=decoy_rng)
        catalog_samples = tuple(tuple(idea.text for idea in sample) for _ in personas)
        proposals = provider.propose_many(
            personas=personas, topic=config.topic, catalog_samples=catalog_samples
        )
        if tuple(p.persona_name for p in proposals) != tuple(p.name for p in personas):
            raise RuntimeError("reasoning provider must preserve the fixed persona order")
        skeletons = extract_many([p.reasoning for p in proposals])
        answer_embeddings = provider.embed([p.text for p in proposals])
        skeleton_embeddings = provider.embed(skeletons)
        # the agents' *skeletons* echo the shown reasoning, and become the next catalog
        uptake = _uptake(skeleton_embeddings, sample, decoy) if sample else None
        if sample:
            catalog.record_echoes(
                samples=tuple(sample for _ in personas), output_embeddings=skeleton_embeddings
            )
        for skel, embedding in zip(skeletons, skeleton_embeddings, strict=True):
            catalog.add(text=skel, embedding=embedding, round_index=round_index)
        rounds.append(
            R4ReasoningRound(
                round_index=round_index,
                pre_catalog=pre_catalog,
                shown_sample_ids=tuple(idea.id for idea in sample),
                shown_sample_embeddings=_ideas_matrix(sample, catalog.embedding_dimensions),
                decoy_ids=tuple(idea.id for idea in decoy),
                decoy_embeddings=_ideas_matrix(decoy, catalog.embedding_dimensions),
                answers=tuple(p.text for p in proposals),
                answer_embeddings=answer_embeddings,
                skeletons=tuple(skeletons),
                skeleton_embeddings=skeleton_embeddings,
                item_uptake=uptake,
                v_output=float(mean_pairwise_cosine(answer_embeddings)),
                v_reason=float(mean_pairwise_cosine(skeleton_embeddings)),
                post_echo_top4_share=_top4_share(catalog.echo_weights) if sample else None,
            )
        )
    return R4ReasoningRun(
        config=config, persona_embeddings=persona_embeddings, rounds=tuple(rounds)
    )


def r4_reasoning_to_dict(run: R4ReasoningRun) -> dict[str, Any]:
    """Artifact keys chosen so the confirmatory reads them directly: ``skeleton_embeddings`` is the
    primary V_reason channel (the actuator acts on reasoning); ``proposal_embeddings`` holds the
    answers (secondary V_output). Uptake/shown/decoy are all reasoning-side here."""
    return {
        "config": {**asdict(run.config), "condition": run.config.condition.value,
                   "catalog_mode": "reasoning"},
        "persona_embeddings": run.persona_embeddings.tolist(),
        "rounds": [
            {
                "round_index": item.round_index,
                "pre_catalog": [
                    {"id": i.id, "text": i.text, "embedding": np.asarray(i.embedding).tolist(),
                     "echo_weight": i.echo_weight}
                    for i in item.pre_catalog
                ],
                "shown_sample_ids": list(item.shown_sample_ids),
                "shown_sample_embeddings": item.shown_sample_embeddings.tolist(),
                "decoy_ids": list(item.decoy_ids),
                "decoy_embeddings": item.decoy_embeddings.tolist(),
                "answers": list(item.answers),
                "proposal_embeddings": item.answer_embeddings.tolist(),  # V_output (secondary)
                "skeletons": list(item.skeletons),
                "skeleton_embeddings": item.skeleton_embeddings.tolist(),  # V_reason (primary)
                "item_uptake": list(item.item_uptake) if item.item_uptake is not None else None,
                "v_output": item.v_output,
                "v_reason": item.v_reason,
                "post_echo_top4_share": item.post_echo_top4_share,
            }
            for item in run.rounds
        ],
    }


def v_slope(values: Sequence[float]) -> float:
    y = np.asarray(values, dtype=np.float64)
    return float(np.polyfit(np.arange(len(y), dtype=np.float64), y, 1)[0])
