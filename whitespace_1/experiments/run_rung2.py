"""Fire the rung-2 two-channel endogenous loop on DeepSeek (rung 2 of ws1-oss-rung1-prereg.md).

    uv run --extra llm python experiments/run_rung2.py                # the full 24 artifacts
    uv run --extra llm python experiments/run_rung2.py --limit 3      # smoke one run-id first

The rung-1 catalog-of-conclusions loop, now capturing each agent's reasoning trace. After a run,
the ``strategy`` skeleton is extracted from every trace (deepseek-v4-flash, rung-0's prompt) and
embedded on the fixed ``text-embedding-3-small``, so the artifact carries ``skeleton_embeddings``
alongside ``proposal_embeddings`` — the two diversity channels the confirmatory then compares. ~$1.
Concurrent + resumable (bank per run-id×condition to ``runs/rung2-r4/``). Needs the two keys in
the folder-local ``.env`` (``DEEPSEEK_API_KEY`` + ``OPENAI_API_KEY``).
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any, Callable, Sequence

import numpy as np
from numpy.typing import NDArray

from whitespace1 import rung0_v2, rung1_r4 as r4
from whitespace1.client import DeepSeekClient, Ledger, OpenAICompatClient
from whitespace1.credentials import MissingCredential, require_secret

GEN_MODEL = "deepseek-v4-pro"
EXTRACT_MODEL = "deepseek-v4-flash"
MAX_GEN_TOKENS = 2000
MAX_SKEL_TOKENS = 256
SKELETON_PROCEDURE = "strategy"  # rung-0's refinement: the strategy layer is where collapse lives
BASE_SAMPLING_SEED = 20260723
BASE_DECOY_SEED = 20260731
RUN_IDS_PER_TOPIC = 4
TOPICS = ("topic-a", "topic-b")
CONDITIONS = (r4.R4Condition.ABLATION, r4.R4Condition.UNIFORM, r4.R4Condition.POPULARITY)
PERSONA_WORKERS = 5
RUN_WORKERS = 4
RETRY_ATTEMPTS = 4
EMPTY = "(no proposal)"
RUNS_DIR = Path(__file__).resolve().parents[1] / "runs" / "rung2-r4"


def _retry(fn: Callable[[], Any], *, attempts: int = RETRY_ATTEMPTS) -> Any:
    for attempt in range(attempts):
        try:
            return fn()
        except Exception:  # noqa: BLE001 - transient API errors retried
            if attempt == attempts - 1:
                raise
            time.sleep(2.0 * (2**attempt))
    raise RuntimeError("unreachable")


def _nonempty(texts: Sequence[str]) -> list[str]:
    return [t if str(t).strip() else EMPTY for t in texts]


class DeepSeekReasoningProvider:
    """R4 provider that captures the raw trace into ``GeneratedProposal.reasoning`` (rung 2)."""

    def __init__(self, gen: DeepSeekClient, embedder: OpenAICompatClient) -> None:
        self._gen = gen
        self._embedder = embedder

    def propose_many(self, *, personas, topic, catalog_samples):  # noqa: ANN001, ANN201
        def one(pair):  # noqa: ANN001, ANN202
            persona, sample = pair
            prompt = r4.build_walk_prompt(
                name=persona.name, viewpoint=persona.viewpoint, topic=topic, catalog_items=sample
            )
            comp = _retry(lambda: self._gen.generate(prompt, max_output_tokens=MAX_GEN_TOKENS))
            text = comp.text if comp.text.strip() else EMPTY
            return r4.GeneratedProposal(
                text=text, persona_name=persona.name, reasoning=comp.reasoning or ""
            )

        with ThreadPoolExecutor(max_workers=PERSONA_WORKERS) as ex:
            proposals = list(ex.map(one, zip(personas, catalog_samples, strict=True)))
        return tuple(proposals)

    def embed(self, texts: Sequence[str]) -> NDArray[np.float64]:
        return _retry(lambda: self._embedder.embed(_nonempty(list(texts))))


def _specs() -> list[tuple[str, str, r4.R4Condition, int, int]]:
    specs = []
    run_index = 0
    for topic_id in TOPICS:
        for k in range(RUN_IDS_PER_TOPIC):
            run_id = f"{topic_id}-run{k}"
            sseed, dseed = BASE_SAMPLING_SEED + run_index, BASE_DECOY_SEED + run_index
            run_index += 1
            for condition in CONDITIONS:
                specs.append((run_id, topic_id, condition, sseed, dseed))
    return specs


def _artifact_path(run_id: str, condition: r4.R4Condition) -> Path:
    return RUNS_DIR / f"{run_id}-{condition.value}.json"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--workers", type=int, default=RUN_WORKERS)
    args = ap.parse_args()

    try:
        openai_key = require_secret("OPENAI_API_KEY")
        deepseek_key = require_secret("DEEPSEEK_API_KEY")
    except MissingCredential as exc:
        print(f"{exc}\n\n(folder-local .env with both keys is required)", file=sys.stderr)
        return 1

    ledger = Ledger()
    embedder = OpenAICompatClient("gpt-5.6-sol", openai_key, ledger=ledger)
    gen = DeepSeekClient(GEN_MODEL, deepseek_key, thinking=True, ledger=ledger)
    skel = DeepSeekClient(EXTRACT_MODEL, deepseek_key, thinking=False, ledger=ledger)
    provider = DeepSeekReasoningProvider(gen, embedder)
    RUNS_DIR.mkdir(parents=True, exist_ok=True)
    prompt_template = rung0_v2.SKELETON_PROMPTS[SKELETON_PROCEDURE]

    def extract(trace: str) -> str:
        if not trace.strip():
            return EMPTY
        text = _retry(lambda: skel.generate(prompt_template.format(trace=trace),
                                            max_output_tokens=MAX_SKEL_TOKENS).text)
        return text if text.strip() else EMPTY

    specs = _specs()
    banked = [s for s in specs if _artifact_path(s[0], s[2]).exists()]
    todo = [s for s in specs if s not in banked]
    if args.limit is not None:
        todo = todo[: args.limit]
    print(f"rung 2: {len(banked)} banked, {len(todo)} to run "
          f"({args.workers} run-workers × {PERSONA_WORKERS} personas)", file=sys.stderr)

    def run_one(spec: tuple[str, str, r4.R4Condition, int, int]) -> str:
        run_id, topic_id, condition, sseed, dseed = spec
        config = r4.R4Config(condition=condition, run_identifier=run_id, topic_id=topic_id,
                             sampling_seed=sseed, decoy_seed=dseed)
        run = r4.run_r4(provider=provider, config=config)
        art = r4.r4_run_to_dict(run)
        # post-hoc: extract the strategy skeleton per trace, embed on the fixed instrument
        for round_dict, r4round in zip(art["rounds"], run.rounds, strict=True):
            with ThreadPoolExecutor(max_workers=PERSONA_WORKERS) as ex:
                skeletons = list(ex.map(extract, r4round.traces))
            round_dict["skeletons"] = skeletons
            round_dict["skeleton_embeddings"] = embedder.embed(_nonempty(skeletons)).tolist()
        _artifact_path(run_id, condition).write_text(json.dumps(art, indent=2))
        return f"{run_id}-{condition.value}"

    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        futures = [ex.submit(run_one, s) for s in todo]
        for i, fut in enumerate(futures, start=1):
            print(f"  done {i}/{len(todo)}: {fut.result()}", file=sys.stderr, flush=True)

    print(f"\ncost ~${ledger.cost_usd():.4f}  ({ledger.total.output} gen-out tokens, "
          f"{ledger.total.embedding} embed)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
