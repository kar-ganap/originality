"""Execute the rung-0 v2 probe (docs/ws1-oss-rung0-v2-prereg.md) — concurrent + resumable.

    uv run python experiments/run_rung0_v2.py --dry-run          # mock everything; no key, no spend
    uv run python experiments/run_rung0_v2.py                    # ~1,250 gens + extraction, ~$1.5
    uv run python experiments/run_rung0_v2.py --workers 16       # tune concurrency

Two API phases, each **concurrent** (a thread pool over the network calls) and **checkpointed** per
``(block, cell)``: generation banks answers + traces, extraction banks skeletons. A finished cell is
appended to a JSONL bank the moment it finishes, so a mid-run snag loses nothing — rerun the same
command and it skips banked cells and resumes. The measurement + gate run locally from the banks, so
they never re-pay for generation.

Substrate: DeepSeek V4-pro (thinking on) → answer + raw trace; V4-flash (thinking off) → skeletons.
Instruments: I1 = text-embedding-3-small (fixed), I2 = a local open embedder, I3 = distinct-2. Keys
`DEEPSEEK_API_KEY` + `OPENAI_API_KEY` in the folder-local `.env`.
"""

from __future__ import annotations

import argparse
import json
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict
from pathlib import Path
from typing import Any, Callable

import numpy as np
from numpy.typing import NDArray

from whitespace1 import rung0_v2 as v2
from whitespace1.client import DeepSeekClient, Ledger, MockClient, OpenAICompatClient
from whitespace1.credentials import MissingCredential, require_secret
from whitespace1.schedule import Block, build_schedule, render_block, schedule_hash
from whitespace1.stimuli import FAMILIES, ROLES, stimulus_hash

CELLS = (v2.ABLATION, v2.POSITIVE, *v2.ACTUATOR_CELLS)  # C0, CP, C1, C2, C3
GEN_MODEL = "deepseek-v4-pro"
EXTRACT_MODEL = "deepseek-v4-flash"
I2_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
N_BLOCKS = 10
SCHEDULE_SEED = 20260723
MAX_GEN_TOKENS = 2000
MAX_SKELETON_TOKENS = 256
DEFAULT_WORKERS = 12
RETRY_ATTEMPTS = 4
RUNS_DIR = Path(__file__).resolve().parents[1] / "runs"


def _retry(fn: Callable[[], Any], *, attempts: int = RETRY_ATTEMPTS) -> Any:
    """Call ``fn`` with exponential backoff; re-raise if every attempt fails."""
    for attempt in range(attempts):
        try:
            return fn()
        except Exception:  # noqa: BLE001 - transient API errors (rate limit, timeout) are retried
            if attempt == attempts - 1:
                raise
            time.sleep(2.0 * (2**attempt))
    raise RuntimeError("unreachable")


def _key(family_id: str, block_index: int, cell: str) -> str:
    """Globally-unique cell key. block_index resets per family, so family_id is required."""
    return f"{family_id}:{block_index}:{cell}"


def _load_bank(path: Path) -> dict[str, dict]:
    """Read a JSONL checkpoint into ``{"<family>:<block>:<cell>": record}``; empty if absent."""
    if not path.exists():
        return {}
    done: dict[str, dict] = {}
    for line in path.read_text().splitlines():
        if line.strip():
            rec = json.loads(line)
            done[_key(rec["family_id"], rec["block_index"], rec["cell"])] = rec
    return done


def _run_phase(
    items: list[tuple[Block, str]],
    worker: Callable[[Block, str], dict],
    bank_path: Path,
    *,
    workers: int,
    desc: str,
) -> dict[str, dict]:
    """Run ``worker`` over the not-yet-banked ``items`` concurrently, appending each result to the
    JSONL bank as it completes. Returns the full bank (previously + newly done)."""
    bank = _load_bank(bank_path)
    todo = [(b, c) for b, c in items if _key(b.family_id, b.block_index, c) not in bank]
    print(f"{desc}: {len(bank)} banked, {len(todo)} to run ({workers} workers)", file=sys.stderr)
    lock = threading.Lock()

    def do(block: Block, cell: str) -> dict:
        rec = worker(block, cell)
        with lock, bank_path.open("a") as fh:
            fh.write(json.dumps(rec) + "\n")
        return rec

    with ThreadPoolExecutor(max_workers=workers) as ex:
        futures = {ex.submit(do, b, c): (b, c) for b, c in todo}
        for i, fut in enumerate(as_completed(futures), start=1):
            rec = fut.result()
            bank[_key(rec["family_id"], rec["block_index"], rec["cell"])] = rec
            if i % 25 == 0 or i == len(todo):
                print(f"  {desc} {i}/{len(todo)}", file=sys.stderr)
    return bank


def build_pieces(dry_run: bool):  # noqa: ANN201 - a bundle of callables
    """Return (generate, extract_generate, embed_i1, embed_i2, ledger)."""
    if dry_run:
        gen = MockClient(with_reasoning=True)
        skel = MockClient()

        def mock_embed(salt: int) -> Callable[[Any], NDArray[np.float64]]:
            def _e(texts: Any) -> NDArray[np.float64]:
                rows = [np.random.default_rng((abs(hash(t)) + salt) % (2**32)).normal(size=32)
                        for t in texts]
                return np.asarray([r / np.linalg.norm(r) for r in rows], dtype=np.float64)
            return _e

        gen_fn = lambda p: gen.generate(p, max_output_tokens=MAX_GEN_TOKENS)  # noqa: E731
        skel_fn = lambda p: skel.generate(p, max_output_tokens=MAX_SKELETON_TOKENS).text  # noqa: E731
        return gen_fn, skel_fn, mock_embed(0), mock_embed(999), gen.ledger

    ledger = Ledger()
    openai = OpenAICompatClient("gpt-5.6-sol", require_secret("OPENAI_API_KEY"), ledger=ledger)
    gen = DeepSeekClient(
        GEN_MODEL, require_secret("DEEPSEEK_API_KEY"), thinking=True,
        embed_with=openai, ledger=ledger,
    )
    skel = DeepSeekClient(
        EXTRACT_MODEL, require_secret("DEEPSEEK_API_KEY"), thinking=False, ledger=ledger
    )
    model = _local_embedder()

    def gen_fn(prompt: str) -> Any:
        return gen.generate(prompt, max_output_tokens=MAX_GEN_TOKENS)

    def skel_fn(prompt: str) -> str:
        return skel.generate(prompt, max_output_tokens=MAX_SKELETON_TOKENS).text

    def embed_i2(texts: Any) -> NDArray[np.float64]:
        return np.asarray(model.encode(list(texts), normalize_embeddings=True), dtype=np.float64)

    return gen_fn, skel_fn, lambda t: openai.embed(list(t)), embed_i2, ledger


def _local_embedder() -> Any:
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer(I2_MODEL)


def run(dry_run: bool, workers: int) -> int:
    gen_fn, skel_fn, embed_i1, embed_i2, ledger = build_pieces(dry_run)
    blocks = build_schedule(n_blocks=N_BLOCKS, seed=SCHEDULE_SEED)
    tag = "dry" if dry_run else schedule_hash(blocks)[:12]
    RUNS_DIR.mkdir(exist_ok=True)
    gen_bank_path = RUNS_DIR / f"rung0-v2-{tag}-gen.jsonl"
    skel_bank_path = RUNS_DIR / f"rung0-v2-{tag}-skel.jsonl"
    items = [(b, c) for b in blocks for c in CELLS]

    # --- Phase 1: generation (concurrent, checkpointed) ---------------------------------------
    def gen_worker(block: Block, cell: str) -> dict:
        answers, traces = [], []
        for role_index in range(len(ROLES)):
            comp = _retry(lambda: gen_fn(render_block(block, cell, role_index)))
            answers.append(comp.text)
            traces.append(comp.reasoning or "")
        return {"block_index": block.block_index, "family_id": block.family_id, "cell": cell,
                "answers": answers, "traces": traces}

    gen_bank = _run_phase(items, gen_worker, gen_bank_path, workers=workers, desc="generate")

    # --- Phase 2: skeleton extraction (concurrent, checkpointed) -------------------------------
    def skel_worker(block: Block, cell: str) -> dict:
        traces = gen_bank[_key(block.family_id, block.block_index, cell)]["traces"]
        skeletons = {
            p: [_retry(lambda: skel_fn(v2.SKELETON_PROMPTS[p].format(trace=t))) for t in traces]
            for p in v2.SKELETON_PROCEDURES
        }
        return {"block_index": block.block_index, "family_id": block.family_id, "cell": cell,
                "skeletons": skeletons}

    skel_bank = _run_phase(items, skel_worker, skel_bank_path, workers=workers, desc="extract")

    # --- Phase 3: measurement + gate (local, from the banks) ----------------------------------
    instruments = [
        ("I1", v2.embed_instrument(embed_i1)),
        ("I2", v2.embed_instrument(embed_i2)),
        ("I3", v2.distinct_2),
    ]
    roles_emb = embed_i1([r.descriptor for r in ROLES])
    measures = _measure_from_banks(blocks, gen_bank, skel_bank, instruments, embed_i1, roles_emb)

    families = [f.task_id for f in FAMILIES]
    verdict = v2.evaluate(measures, instrument_names=["I1", "I2", "I3"], families=families)
    _report(verdict, ledger)

    if not dry_run:
        path = RUNS_DIR / f"rung0-v2-{tag}.json"
        path.write_text(json.dumps({
            "stimulus_hash": stimulus_hash(), "schedule_hash": schedule_hash(blocks),
            "gen_model": GEN_MODEL, "extract_model": EXTRACT_MODEL, "i2_model": I2_MODEL,
            "cost_usd": ledger.cost_usd(), "measures": [asdict(m) for m in measures],
        }, indent=2))
        print(f"\nverdict artifact -> {path}")
    return 0


def _measure_from_banks(
    blocks: list[Block], gen_bank: dict[str, dict], skel_bank: dict[str, dict],
    instruments: list[tuple[str, v2.Instrument]], embed_i1: Any, roles_emb: NDArray[np.float64],
) -> list[v2.CellMeasureV2]:
    """Compute the measures from the banked answers/traces/skeletons — no API calls."""
    measures = []
    for block in blocks:
        family = next(f for f in FAMILIES if f.task_id == block.family_id)
        for cell in CELLS:
            g = gen_bank[_key(block.family_id, block.block_index, cell)]
            skeletons = skel_bank[_key(block.family_id, block.block_index, cell)]["skeletons"]
            cards = None if cell == v2.ABLATION else [
                family.cards[j].text for j in block.item_order
            ][: (1 if cell == v2.POSITIVE else len(family.cards))]
            measures.append(v2.measure_cell(
                family_id=block.family_id, block_index=block.block_index, cell=cell,
                answers=g["answers"], traces=g["traces"], instruments=instruments,
                extract=lambda _t, p, _s=skeletons: _s[p],  # _s binds this cell's banked skeletons
                embed_fixed=embed_i1, card_texts=cards, roles_emb=roles_emb,
            ))
    return measures


def _report(verdict: v2.Rung0V2Verdict, ledger: Ledger) -> None:
    print("\n================  RUNG-0 v2 GATE  ================\n")
    h0 = verdict.h0_apparatus_valid()
    print(f"H0 apparatus validity (CP collapses >= {v2.POS_CONTROL_MIN:.0%}, both channels): "
          f"{'VALID' if h0 else 'INVALID -- STOP, measurement is blind'}")
    for fam in verdict.families:
        cp = verdict.declines[v2.POSITIVE][fam]
        print(f"    {fam:16s} V_out {cp['V_output'].decline:+.0%} "
              f"V_reason {cp['V_reason'].decline:+.0%}")

    reached, cell, channel = verdict.reachable()
    print(f"\nH1 reachability: {'REACHED via ' + f'{cell}/{channel}' if reached else 'NULL'}")

    print("\nH2 sweep + H3 adjudication (decline vs ablation; * = clean collapse):")
    for cell in v2.ACTUATOR_CELLS:
        print(f"  {cell}:")
        for fam in verdict.families:
            d = verdict.declines[cell][fam]
            o, r = d["V_output"], d["V_reason"]
            om = "*" if o.collapses(v2.DECLINE_MIN) else " "
            rm = "*" if r.collapses(v2.DECLINE_MIN) else " "
            print(f"    {fam:16s} V_out {o.decline:+.0%}{om}  V_reason {r.decline:+.0%}{rm}  "
                  f"guards={'ok' if verdict.guards_ok[cell][fam] else 'FAIL'}")

    print(f"\ncost ~${ledger.cost_usd():.4f}")
    print("\nRUNG-0 v2 " + (
        "APPARATUS INVALID -- fix measurement before interpreting." if not h0 else
        ("COLLAPSE REACHED -- proceed to the lambda-ladder." if reached else
         "NULL under a VALID apparatus -- measured resistance (report the channel split).")))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="mock everything; no key, no spend")
    ap.add_argument("--workers", type=int, default=DEFAULT_WORKERS)
    args = ap.parse_args()
    try:
        return run(args.dry_run, args.workers)
    except MissingCredential as exc:
        print(f"{exc}\n\n(use --dry-run to exercise the pipeline without a key)", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
