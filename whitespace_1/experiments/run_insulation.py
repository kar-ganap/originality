"""Fire the insulation experiment on DeepSeek (docs/ws1-insulation-prereg.md).

    uv run --extra llm python experiments/run_insulation.py            # 8 run-ids
    uv run --extra llm python experiments/run_insulation.py --limit 2  # smoke

Per run-id: a FIELD `run_r4` (popularity) + an insulated ISOLATED `run_r4` (its own local
catalog, a distinct seed), then the connected field is shown balanced mixes of both origins' round-T
ideas and we record adoption echo. ~$0.6. Resumable (bank showings per run-id
to runs/insulation/). Needs DEEPSEEK_API_KEY + OPENAI_API_KEY in the folder-local .env.
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

from whitespace1 import insulation as ins
from whitespace1 import rung1_r4 as r4
from whitespace1.client import DeepSeekClient, Ledger, OpenAICompatClient
from whitespace1.credentials import MissingCredential, require_secret
from whitespace1.stimuli import ROLES

GEN_MODEL = "deepseek-v4-pro"
MAX_GEN_TOKENS = 2000
T_ROUNDS = 8
A_ROUNDS = 6
SHOWN_PER_ORIGIN = 2
FIELD_SAMPLING, FIELD_DECOY = 20260723, 20260731
ISO_SAMPLING, ISO_DECOY = 20260800, 20260810
ADOPT_SEED = 20260724
RUN_IDS_PER_TOPIC = 4
TOPICS = ("topic-a", "topic-b")
PERSONA_WORKERS = 5
RUN_WORKERS = 4
RETRY_ATTEMPTS = 4
EMPTY = "(no proposal)"
RUNS_DIR = Path(__file__).resolve().parents[1] / "runs" / "insulation"


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


class DeepSeekR4Provider:
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
            return r4.GeneratedProposal(text=text, persona_name=persona.name)

        with ThreadPoolExecutor(max_workers=PERSONA_WORKERS) as ex:
            return tuple(ex.map(one, zip(personas, catalog_samples, strict=True)))

    def embed(self, texts: Sequence[str]) -> NDArray[np.float64]:
        return _retry(lambda: self._embedder.embed(_nonempty(list(texts))))


def _candidates(run: r4.R4Run, origin: str) -> list[ins.Candidate]:
    last = run.rounds[-1]
    return [
        ins.Candidate(text=p.text, embedding=tuple(float(x) for x in emb), origin=origin)
        for p, emb in zip(last.proposals, last.proposal_embeddings, strict=True)
    ]


def _specs() -> list[tuple[str, str, int]]:
    specs, idx = [], 0
    for topic_id in TOPICS:
        for k in range(RUN_IDS_PER_TOPIC):
            specs.append((f"{topic_id}-run{k}", topic_id, idx))
            idx += 1
    return specs


def _path(run_id: str) -> Path:
    return RUNS_DIR / f"{run_id}.json"


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
    provider = DeepSeekR4Provider(gen, embedder)
    RUNS_DIR.mkdir(parents=True, exist_ok=True)

    specs = _specs()
    todo_all = [s for s in specs if not _path(s[0]).exists()]
    todo = todo_all[: args.limit] if args.limit is not None else todo_all
    print(f"insulation: {len(specs) - len(todo_all)} banked, {len(todo)} to run "
          f"({args.workers} run-workers × {PERSONA_WORKERS} personas)", file=sys.stderr)

    def run_one(spec: tuple[str, str, int]) -> str:
        run_id, topic_id, i = spec
        field_cfg = r4.R4Config(
            condition=r4.R4Condition.POPULARITY, run_identifier=f"{run_id}-field",
            topic_id=topic_id, sampling_seed=FIELD_SAMPLING + i, decoy_seed=FIELD_DECOY + i,
        )
        iso_cfg = r4.R4Config(condition=r4.R4Condition.POPULARITY, run_identifier=f"{run_id}-iso",
                              topic_id=topic_id, sampling_seed=ISO_SAMPLING + i,
                              decoy_seed=ISO_DECOY + i)
        field_run = r4.run_r4(provider=provider, config=field_cfg)
        iso_run = r4.run_r4(provider=provider, config=iso_cfg)
        candidates = _candidates(field_run, ins.CONNECTED) + _candidates(iso_run, ins.ISOLATED)
        showings = ins.run_adoption(
            provider=provider, personas=ROLES, topic=field_cfg.topic, candidates=candidates,
            rounds=A_ROUNDS, shown_per_origin=SHOWN_PER_ORIGIN,
            rng=np.random.default_rng(ADOPT_SEED + i),
        )
        _path(run_id).write_text(json.dumps({
            "run_id": run_id, "topic_id": topic_id,
            "connected_candidates": [c.text for c in candidates if c.origin == ins.CONNECTED],
            "isolated_candidates": [c.text for c in candidates if c.origin == ins.ISOLATED],
            "showings": [{"origin": s.origin, "echo": s.echo, "shown": s.shown} for s in showings],
        }, indent=2))
        return run_id

    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        futures = [ex.submit(run_one, s) for s in todo]
        for i, fut in enumerate(futures, start=1):
            print(f"  done {i}/{len(todo)}: {fut.result()}", file=sys.stderr, flush=True)

    print(f"\ncost ~${ledger.cost_usd():.4f}  ({ledger.total.output} gen-out tokens, "
          f"{ledger.total.embedding} embed)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
