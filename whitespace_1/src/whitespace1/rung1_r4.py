"""Rung-1 R4 loop — the endogenous bridge replication (``docs/ws1-oss-rung1-prereg.md``).

Ported from ``polyphony/src/polyphony/walk_r4.py``: the append-only shared-catalog actuator, the
8-round loop, the per-round measurement (``V_pair`` diversity, item ``uptake``, ``P_top4``
concentration), and the artifact schema — all verbatim in mechanism. Substrate adaptations: the
generator is any :class:`R4Provider` (the runner backs it with ``DeepSeekClient``, thinking on);
``V_pair`` uses :func:`whitespace1.rung0.mean_pairwise_cosine` (definition identical to Polyphony's
``diversity_metrics.mean_pairwise_cosine_distance``); personas come from :data:`stimuli.ROLES`
(identical to Polyphony's ``DEFAULT_PERSONAS``). Catalog-of-conclusions: only the answer text enters
the catalog. Token-free except the injected provider.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any, Protocol, cast

import numpy as np
from numpy.typing import NDArray

from .catalog import Catalog, Idea, SamplingConfig
from .rung0 import mean_pairwise_cosine
from .stimuli import ROLES, Role

FloatMatrix = NDArray[np.float64]

# The 8-item seed catalog, verbatim from Polyphony R3 (PACKET_A + PACKET_B).
R4_SEED_CATALOG: tuple[str, ...] = (
    (
        "Decision Ledger: retain the evidence, owner, and reversal trigger behind each ensemble "
        "choice."
    ),
    "Counterexample Queue: collect unresolved edge cases that a proposed workflow does not cover.",
    "Latency Budget Map: show where agent handoffs consume the workflow response-time allowance.",
    "Permission Trace: display which agent accessed each protected capability and why.",
    "Evaluation Replay: rerun a saved workflow against prior inputs to compare output coverage.",
    "Cost Envelope: forecast token and tool expenditure before launching a multi-agent run.",
    (
        "Handoff Contract: record the input, expected output, and failure owner for each agent "
        "transfer."
    ),
    "Coverage Matrix: expose which user scenarios each proposed workflow capability serves.",
)
R4_TOPICS: dict[str, str] = {
    "topic-a": (
        "Propose one concise feature for a developer tool that helps a multi-agent LLM ensemble "
        "maintain varied ideas over time."
    ),
    "topic-b": (
        "Propose one concise feature for a developer tool that helps teams inspect and improve "
        "multi-agent LLM workflows before deployment."
    ),
}
WALK_INSTRUCTIONS = (
    "Take the persona, topic, and catalog field below into account when drafting. "
    "Return exactly one feature with a short name, its mechanism, and its user benefit. "
    "Use one or two sentences with no headings, bullets, analysis, or preamble."
)


class R4Condition(str, Enum):
    ABLATION = "ablation"
    UNIFORM = "uniform"
    POPULARITY = "popularity"


def build_walk_prompt(
    *, name: str, viewpoint: str, topic: str, catalog_items: Sequence[str]
) -> str:
    """The frozen per-persona prompt; the treatment changes only the catalog field. The instruction
    is prepended (DeepSeek takes one user message) — a documented single-message adaptation."""
    lines = (
        "\n".join(f"- {item}" for item in catalog_items)
        if catalog_items
        else "- none available this round."
    )
    return (
        f"{WALK_INSTRUCTIONS}\n\n"
        f"Persona: {name}\nViewpoint: {viewpoint}\nTopic: {topic}\n"
        f"Catalog items:\n{lines}"
    )


@dataclass(frozen=True)
class GeneratedProposal:
    text: str
    persona_name: str


class R4Provider(Protocol):
    """The generation seam. The runner backs this with DeepSeek (thinking on) + a fixed embedder;
    tests back it with a deterministic mock. ``propose_many`` returns proposals in persona order."""

    def propose_many(
        self,
        *,
        personas: Sequence[Role],
        topic: str,
        catalog_samples: tuple[tuple[str, ...], ...],
    ) -> tuple[GeneratedProposal, ...]: ...

    def embed(self, texts: Sequence[str]) -> FloatMatrix: ...


@dataclass(frozen=True)
class R4Config:
    condition: R4Condition
    run_identifier: str
    topic_id: str = "topic-a"
    rounds: int = 8
    exposure_budget: int = 4
    sampling_seed: int = 20260723
    decoy_seed: int = 20260724
    seed_catalog: tuple[str, ...] = R4_SEED_CATALOG

    @property
    def topic(self) -> str:
        return R4_TOPICS[self.topic_id]

    def __post_init__(self) -> None:
        if not self.run_identifier:
            raise ValueError("run_identifier must not be empty")
        if self.rounds < 1 or self.exposure_budget != 4:
            raise ValueError("R4 requires positive rounds and exposure_budget == 4")
        if len(self.seed_catalog) != 8 or len(set(self.seed_catalog)) != 8:
            raise ValueError("R4 requires the eight distinct seed catalog items")
        if self.topic_id not in R4_TOPICS:
            raise ValueError("R4 topic_id must be one of the committed topics")


@dataclass(frozen=True)
class PreCatalogIdea:
    id: str
    text: str
    embedding: FloatMatrix
    echo_weight: float


@dataclass(frozen=True)
class R4Round:
    round_index: int
    pre_catalog: tuple[PreCatalogIdea, ...]
    shown_sample_ids: tuple[str, ...]
    shown_sample_embeddings: FloatMatrix
    decoy_ids: tuple[str, ...]
    decoy_embeddings: FloatMatrix
    proposals: tuple[GeneratedProposal, ...]
    proposal_embeddings: FloatMatrix
    item_uptake: tuple[float, ...] | None
    v_pair: float
    persona_control: float
    post_echo_top4_share: float | None


@dataclass(frozen=True)
class R4Run:
    config: R4Config
    persona_embeddings: FloatMatrix
    rounds: tuple[R4Round, ...]


def run_r4(*, provider: R4Provider, config: R4Config) -> R4Run:
    """Run one append-only R4 condition, recording shared and decoy fields for later analysis."""
    personas = list(ROLES)
    persona_embeddings = provider.embed([p.descriptor for p in personas])
    seed_embeddings = provider.embed(list(config.seed_catalog))
    catalog = Catalog(embedding_dimensions=persona_embeddings.shape[1])
    if seed_embeddings.shape != (len(config.seed_catalog), catalog.embedding_dimensions):
        raise RuntimeError("seed catalog embeddings do not match persona embedding dimensions")
    for text, embedding in zip(config.seed_catalog, seed_embeddings, strict=True):
        catalog.add(text=text, embedding=embedding, round_index=-1, persona_name="seed")
    sample_rng = np.random.default_rng(config.sampling_seed)
    decoy_rng = np.random.default_rng(config.decoy_seed)
    rounds: list[R4Round] = []

    for round_index in range(config.rounds):
        pre_catalog = _snapshot(catalog)
        sample = _sample(catalog=catalog, config=config, rng=sample_rng)
        decoy = _decoy(catalog=catalog, sample=sample, rng=decoy_rng)
        catalog_samples = tuple(tuple(idea.text for idea in sample) for _ in personas)
        proposals = provider.propose_many(
            personas=personas, topic=config.topic, catalog_samples=catalog_samples
        )
        if tuple(p.persona_name for p in proposals) != tuple(p.name for p in personas):
            raise RuntimeError("R4 provider must preserve the fixed persona order")
        proposal_embeddings = provider.embed([p.text for p in proposals])
        if proposal_embeddings.shape != (len(personas), catalog.embedding_dimensions):
            raise RuntimeError("R4 output embeddings do not match the embedding dimensions")
        uptake = _uptake(proposal_embeddings, sample, decoy) if sample else None
        if sample:
            catalog.record_echoes(
                samples=tuple(sample for _ in personas), output_embeddings=proposal_embeddings
            )
        for proposal, embedding in zip(proposals, proposal_embeddings, strict=True):
            catalog.add(
                text=proposal.text,
                embedding=embedding,
                round_index=round_index,
                persona_name=proposal.persona_name,
            )
        rounds.append(
            R4Round(
                round_index=round_index,
                pre_catalog=pre_catalog,
                shown_sample_ids=tuple(idea.id for idea in sample),
                shown_sample_embeddings=_ideas_matrix(sample, catalog.embedding_dimensions),
                decoy_ids=tuple(idea.id for idea in decoy),
                decoy_embeddings=_ideas_matrix(decoy, catalog.embedding_dimensions),
                proposals=proposals,
                proposal_embeddings=proposal_embeddings,
                item_uptake=uptake,
                v_pair=float(mean_pairwise_cosine(proposal_embeddings)),
                persona_control=float(mean_pairwise_cosine(persona_embeddings)),
                post_echo_top4_share=_top4_share(catalog.echo_weights) if sample else None,
            )
        )
    return R4Run(config=config, persona_embeddings=persona_embeddings, rounds=tuple(rounds))


def v_pair_slope(run: R4Run) -> float:
    """OLS slope of ``V_pair`` over the round index — the primary collapse estimand."""
    vs = [r.v_pair for r in run.rounds]
    x = np.arange(len(vs), dtype=np.float64)
    return float(np.polyfit(x, np.asarray(vs, dtype=np.float64), 1)[0])


def r4_run_to_dict(run: R4Run) -> dict[str, Any]:
    return {
        "config": {**asdict(run.config), "condition": run.config.condition.value},
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
                "proposals": [asdict(p) for p in item.proposals],
                "proposal_embeddings": item.proposal_embeddings.tolist(),
                "item_uptake": list(item.item_uptake) if item.item_uptake is not None else None,
                "v_pair": item.v_pair,
                "persona_control": item.persona_control,
                "post_echo_top4_share": item.post_echo_top4_share,
            }
            for item in run.rounds
        ],
    }


def _sample(*, catalog: Catalog, config: R4Config, rng: np.random.Generator) -> tuple[Idea, ...]:
    if config.condition is R4Condition.ABLATION:
        return ()
    return catalog.sample(
        SamplingConfig(
            sigma=1.0,
            exposure_budget=config.exposure_budget,
            popularity_weighted=config.condition is R4Condition.POPULARITY,
        ),
        rng=rng,
    )


def _decoy(
    *, catalog: Catalog, sample: tuple[Idea, ...], rng: np.random.Generator
) -> tuple[Idea, ...]:
    if not sample:
        return ()
    sample_ids = {item.id for item in sample}
    candidates = tuple(idea for idea in catalog.ideas if idea.id not in sample_ids)
    if len(candidates) < len(sample):
        raise RuntimeError("R4 catalog lacks enough unseen items for its matched decoy")
    indices = rng.choice(len(candidates), size=len(sample), replace=False)
    return tuple(candidates[int(index)] for index in indices)


def _uptake(
    outputs: FloatMatrix, shown: Sequence[Idea], decoy: Sequence[Idea]
) -> tuple[float, ...]:
    if not shown or not decoy:
        raise ValueError("R4 uptake requires a shown sample and a matched decoy")
    normalized = _normalize_rows(outputs)
    shown_matrix = _normalize_rows(_ideas_matrix(shown, outputs.shape[1]))
    decoy_matrix = _normalize_rows(_ideas_matrix(decoy, outputs.shape[1]))
    values = np.max(normalized @ shown_matrix.T, axis=1) - np.max(
        normalized @ decoy_matrix.T, axis=1
    )
    return tuple(float(value) for value in values)


def _snapshot(catalog: Catalog) -> tuple[PreCatalogIdea, ...]:
    return tuple(
        PreCatalogIdea(id=idea.id, text=idea.text, embedding=idea.embedding, echo_weight=float(w))
        for idea, w in zip(catalog.ideas, catalog.echo_weights, strict=True)
    )


def _ideas_matrix(ideas: Sequence[Idea], dimensions: int) -> FloatMatrix:
    if not ideas:
        return np.empty((0, dimensions), dtype=np.float64)
    return cast(FloatMatrix, np.vstack([idea.embedding for idea in ideas]))


def _top4_share(weights: NDArray[np.float64]) -> float:
    values = np.asarray(weights, dtype=np.float64)
    if values.ndim != 1 or values.size < 4 or float(values.sum()) <= 0.0:
        raise ValueError("R4 top-four share requires at least four positive weights")
    return float(np.sort(values)[-4:].sum() / values.sum())


def _normalize_rows(matrix: FloatMatrix) -> FloatMatrix:
    norms = np.linalg.norm(matrix, axis=1, keepdims=True)
    if bool(np.any(norms == 0.0)):
        raise ValueError("R4 embeddings must not contain all-zero rows")
    return cast(FloatMatrix, matrix / norms)
