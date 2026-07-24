"""Rung-1 Gate 0 — the Day-0 bite gate on DeepSeek (``docs/ws1-oss-rung1-prereg.md``, Gate 0).

Ported from ``polyphony/src/polyphony/day0_killtest.py``: the two scoring functions and the pinned
stimuli are reproduced verbatim (metric definitions unchanged); the generator is swapped to
``DeepSeekClient`` (thinking on) and the embedder held at ``text-embedding-3-small``. Personas come
from :data:`whitespace1.stimuli.ROLES`, identical to Polyphony's WALK/R4 personas, so rung 0, this
gate, and the rung-1 loop share one persona set. The scoring here is token-free; the network calls
live in ``experiments/run_rung1_day0.py``.

Substrate-selection gate. GPT-5.6 Sol passed (diversity 0.4286, shift +0.0487); Luna **failed**
the shift gate (+0.0256) and was rejected. DeepSeek is not assumed to pass.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import cast

import numpy as np
from numpy.typing import NDArray

from .rung0 import mean_pairwise_cosine
from .stimuli import ROLES

DIVERSITY_MIN = 0.10  # (a) latent diversity: no-catalog outputs must be at least this far apart
ALIGNMENT_SHIFT_MIN = 0.03  # (b) conditioning bite: catalog must pull outputs at least this much

# Pinned stimuli, verbatim from polyphony day0_killtest.py (kept for comparability to GPT-5.6 Sol).
DAY0_TOPIC = (
    "Propose one concise feature for a developer tool that helps a multi-agent LLM "
    "ensemble maintain varied ideas over time."
)
DAY0_CATALOG_SAMPLE: tuple[str, ...] = (
    "Show every agent a popularity-ranked leaderboard of prior ideas before it proposes.",
    "Highlight the most repeated idea clusters as consensus winners in the shared workspace.",
    (
        "Ask agents to extend the highest-vote catalog entries rather than starting from a "
        "blank slate."
    ),
)
DAY0_INSTRUCTIONS = (
    "You are one persona-conditioned idea generator inside a small multi-agent ensemble. "
    "Return exactly one concrete feature idea in one or two sentences. Do not include bullets, "
    "headings, analysis, or a preamble. Do not mention the persona name."
)


def build_prompt(*, name: str, viewpoint: str, catalog_sample: Sequence[str]) -> str:
    """One persona's single-message prompt. DeepSeek's chat API takes one user message, so the
    instruction is prepended, not sent as a separate system role — a documented single-message
    adaptation of Polyphony's system+user split; immaterial to a diversity/alignment gate."""
    lines = (
        "\n".join(f"- {item}" for item in catalog_sample)
        if catalog_sample
        else "- none available this round."
    )
    return (
        f"{DAY0_INSTRUCTIONS}\n\n"
        f"Persona: {name}\nViewpoint: {viewpoint}\nTopic: {DAY0_TOPIC}\n"
        f"Catalog items:\n{lines}\n\n"
        "Propose one concrete feature that follows this persona's viewpoint."
    )


def no_catalog_prompts() -> list[str]:
    """The five no-catalog prompts (latent-diversity arm)."""
    return [build_prompt(name=r.name, viewpoint=r.viewpoint, catalog_sample=()) for r in ROLES]


def conditioned_prompts() -> list[str]:
    """The five prompts that show the homogeneous popular-canon sample (conditioning arm)."""
    return [
        build_prompt(name=r.name, viewpoint=r.viewpoint, catalog_sample=DAY0_CATALOG_SAMPLE)
        for r in ROLES
    ]


def _normalize_rows(m: NDArray[np.float64]) -> NDArray[np.float64]:
    arr = np.asarray(m, dtype=np.float64)
    norms = np.linalg.norm(arr, axis=1, keepdims=True)
    return cast(NDArray[np.float64], arr / np.where(norms == 0.0, 1.0, norms))


def _normalized_centroid(matrix: NDArray[np.float64]) -> NDArray[np.float64]:
    centroid = _normalize_rows(matrix).mean(axis=0)
    norm = float(np.linalg.norm(centroid))
    if norm == 0.0:
        raise ValueError("catalog centroid is zero after normalization")
    return cast(NDArray[np.float64], centroid / norm)


def _mean_cosine_to_vector(matrix: NDArray[np.float64], vector: NDArray[np.float64]) -> float:
    return float(np.mean(_normalize_rows(matrix) @ vector))


@dataclass(frozen=True)
class Day0Verdict:
    """The two-gate Day-0 result; ``passed`` requires both."""

    diversity: float
    no_catalog_alignment: float
    conditioned_alignment: float
    alignment_shift: float
    diversity_min: float
    shift_min: float

    @property
    def diversity_ok(self) -> bool:
        return self.diversity >= self.diversity_min

    @property
    def shift_ok(self) -> bool:
        return self.alignment_shift >= self.shift_min

    @property
    def passed(self) -> bool:
        return self.diversity_ok and self.shift_ok


def evaluate_day0(
    *,
    no_catalog_emb: NDArray[np.float64],
    conditioned_emb: NDArray[np.float64],
    catalog_emb: NDArray[np.float64],
    diversity_min: float = DIVERSITY_MIN,
    shift_min: float = ALIGNMENT_SHIFT_MIN,
) -> Day0Verdict:
    """(a) latent diversity = mean pairwise cosine distance of no-catalog outputs; (b) conditioning
    shift = mean cosine of conditioned outputs to the catalog centroid, minus the baseline.
    Reproduces Polyphony's ``score_persona_diversity`` / ``score_conditioning_shift``."""
    nc = np.asarray(no_catalog_emb, dtype=np.float64)
    cond = np.asarray(conditioned_emb, dtype=np.float64)
    catalog = np.asarray(catalog_emb, dtype=np.float64)
    diversity = float(mean_pairwise_cosine(nc))
    centroid = _normalized_centroid(catalog)
    no_cat_align = _mean_cosine_to_vector(nc, centroid)
    cond_align = _mean_cosine_to_vector(cond, centroid)
    return Day0Verdict(
        diversity=diversity,
        no_catalog_alignment=no_cat_align,
        conditioned_alignment=cond_align,
        alignment_shift=cond_align - no_cat_align,
        diversity_min=diversity_min,
        shift_min=shift_min,
    )
