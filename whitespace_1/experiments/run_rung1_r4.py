"""Fire the rung-1 R4 loop on DeepSeek (``docs/ws1-oss-rung1-prereg.md``).

    uv run --extra llm python experiments/run_rung1_r4.py                # the full 24 artifacts
    uv run --extra llm python experiments/run_rung1_r4.py --limit 1      # smoke one run first

24 R4 artifacts = 8 run-ids (4 per topic × 2 topics) × 3 conditions; 5 personas × 8 rounds each =
960 generations on ``deepseek-v4-pro`` (thinking on) + embeddings on the fixed
``text-embedding-3-small``. ~$1.5. Concurrent (a run pool + a 5-persona inner pool per round)
and **resumable**: each completed (run-id, condition) artifact is banked to ``runs/rung1-r4/``; a
rerun skips banked artifacts. Needs ``DEEPSEEK_API_KEY`` + ``OPENAI_API_KEY`` in the folder-local
``.env``.

Registered seed extension (pre-reg base: sampling 20260723 / decoy 20260731): run-id k (0..7) uses
``sampling_seed = 20260723 + k`` and ``decoy_seed = 20260731 + k``, shared across its 3 conditions
(the paired triplet), distinct across run-ids.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Callable, Sequence

import numpy as np
from numpy.typing import NDArray

from whitespace1 import rung1_r4 as r4
from whitespace1.client import DeepSeekClient, Ledger, OpenAICompatClient
from whitespace1.credentials import MissingCredential, require_secret

GEN_MODEL = "deepseek-v4-pro"
MAX_OUTPUT_TOKENS = 2000  # room for the reasoning trace + a 1-2 sentence answer
BASE_SAMPLING_SEED = 20260723
BASE_DECOY_SEED = 20260731
RUN_IDS_PER_TOPIC = 4
TOPICS = ("topic-a", "topic-b")
CONDITIONS = (r4.R4Condition.ABLATION, r4.R4Condition.UNIFORM, r4.R4Condition.POPULARITY)
PERSONA_WORKERS = 5
RUN_WORKERS = 4
RETRY_ATTEMPTS = 4
EMPTY = "(no proposal)"
RUNS_DIR = Path(__file__).resolve().parents[1] / "runs" / "rung1-r4"


def _retry(fn: Callable[[], Any], *, attempts: int = RETRY_ATTEMPTS) -> Any:
    for attempt in range(attempts):
        try:
            return fn()
        except Exception:  # noqa: BLE001 - transient API errors (rate limit, timeout) are retried
            if attempt == attempts - 1:
                raise
            time.sleep(2.0 * (2**attempt))
    raise RuntimeError("unreachable")


def _nonempty(texts: Sequence[str]) -> list[str]:
    return [t if str(t).strip() else EMPTY for t in texts]


class DeepSeekR4Provider:
    """Backs the R4Provider seam with DeepSeek (thinking on) + a fixed embedder. The 5 personas of a
    round generate concurrently; the loop across rounds stays sequential (the catalog evolves)."""

    def __init__(self, gen: DeepSeekClient, embedder: OpenAICompatClient) -> None:
        self._gen = gen
        self._embedder = embedder

    def propose_many(self, *, personas, topic, catalog_samples):  # noqa: ANN001, ANN201
        def one(pair):  # noqa: ANN001, ANN202
            persona, sample = pair
            prompt = r4.build_walk_prompt(
                name=persona.name, viewpoint=persona.viewpoint, topic=topic, catalog_items=sample
            )
            comp = _retry(lambda: self._gen.generate(prompt, max_output_tokens=MAX_OUTPUT_TOKENS))
            text = comp.text
            return r4.GeneratedProposal(
                text=text if text.strip() else EMPTY, persona_name=persona.name
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


def _summary() -> None:
    """Quick per-condition mean V_pair slope — direction only; the bootstrap is a separate step."""
    print("\n--- per-condition mean V_pair slope (direction read; bootstrap is separate) ---")
    for condition in CONDITIONS:
        slopes = []
        for path in sorted(RUNS_DIR.glob(f"*-{condition.value}.json")):
            rounds = json.loads(path.read_text())["rounds"]
            vs = np.asarray([r["v_pair"] for r in rounds], dtype=np.float64)
            slopes.append(float(np.polyfit(np.arange(len(vs), dtype=np.float64), vs, 1)[0]))
        if slopes:
            mean = float(np.mean(slopes))
            arrow = "rises (no collapse)" if mean > 0 else "falls (toward collapse)"
            print(f"  {condition.value:11s}: mean slope {mean:+.5f}  {arrow}  (n={len(slopes)})")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=None, help="run only the first N specs (smoke)")
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
    provider = DeepSeekR4Provider(gen, embedder)
    RUNS_DIR.mkdir(parents=True, exist_ok=True)

    specs = _specs()
    todo = [s for s in specs if not _artifact_path(s[0], s[2]).exists()]
    if args.limit is not None:
        todo = todo[: args.limit]
    print(f"R4: {len(specs) - len([s for s in specs if not _artifact_path(s[0], s[2]).exists()])} "
          f"banked, {len(todo)} to run ({args.workers} run-workers × {PERSONA_WORKERS} personas)",
          file=sys.stderr)

    def run_one(spec: tuple[str, str, r4.R4Condition, int, int]) -> str:
        run_id, topic_id, condition, sseed, dseed = spec
        config = r4.R4Config(
            condition=condition, run_identifier=run_id, topic_id=topic_id,
            sampling_seed=sseed, decoy_seed=dseed,
        )
        run = r4.run_r4(provider=provider, config=config)
        _artifact_path(run_id, condition).write_text(json.dumps(r4.r4_run_to_dict(run), indent=2))
        return f"{run_id}-{condition.value}"

    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        futures = {ex.submit(run_one, s): s for s in todo}
        for i, fut in enumerate(as_completed(futures), start=1):
            print(f"  done {i}/{len(todo)}: {fut.result()}", file=sys.stderr, flush=True)

    print(f"\ncost ~${ledger.cost_usd():.4f}  ({ledger.total.output} gen-out tokens, "
          f"{ledger.total.embedding} embed)")
    if len(list(RUNS_DIR.glob("*.json"))) == len(specs):
        _summary()
    return 0


if __name__ == "__main__":
    sys.exit(main())
