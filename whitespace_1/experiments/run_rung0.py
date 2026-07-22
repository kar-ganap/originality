"""Execute the rung-0 reachability probe and report the gate verdict item by item.

    uv run python experiments/run_rung0.py --dry-run   # mock client, no spend, no key
    uv run python experiments/run_rung0.py             # 750 live calls, ~$2.80

Writes ``runs/rung0-<schedule-hash>.json`` with every raw block value, so the verdict regenerates
from committed artifacts without re-running paid calls.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path

from whitespace1 import rung0
from whitespace1.client import Ledger, LLMClient, MockClient, OpenAICompatClient, Usage
from whitespace1.credentials import MissingCredential, require_secret
from whitespace1.rung0 import CellMeasure, bootstrap_ci, evaluate
from whitespace1.schedule import CELLS, build_schedule, call_count, schedule_hash
from whitespace1.stimuli import FAMILIES, stimulus_hash

GEN_MODEL = "gpt-5.6-sol"
N_BLOCKS = 10
SCHEDULE_SEED = 20260722
RUNS_DIR = Path(__file__).resolve().parents[1] / "runs"

# Prior work's endogenous actuator reached this concentration without collapsing. Rung 0 supplies
# the missing denominator (H*); see the design note §9.3 three-band reading.
ENDOGENOUS_H = 0.0102


def build_client(dry_run: bool) -> tuple[LLMClient, Ledger]:
    if dry_run:
        client = MockClient()
        return client, client.ledger
    ledger = Ledger()
    return (
        OpenAICompatClient(
            GEN_MODEL, require_secret("OPENAI_API_KEY"), reasoning_effort="none", ledger=ledger
        ),
        ledger,
    )


def run(client: LLMClient, *, n_blocks: int) -> tuple[list[CellMeasure], Usage]:
    blocks = build_schedule(n_blocks=n_blocks, seed=SCHEDULE_SEED)
    total = Usage()
    measures: list[CellMeasure] = []
    roles_emb = rung0.role_embeddings(client)  # constant; hoisted out of the loop
    for i, block in enumerate(blocks, start=1):
        for cell in CELLS:
            texts, usage = rung0.collect_block(client, block, cell)
            total = total + usage
            measures.append(
                rung0.measure_cell(client, block, cell, texts, roles_emb=roles_emb)
            )
        print(f"  block {i}/{len(blocks)}  {block.family_id}", file=sys.stderr)
    return measures, total


def report(measures: list[CellMeasure], ledger: Ledger, *, n_blocks: int) -> bool:
    verdict = evaluate(measures)
    blocks = build_schedule(n_blocks=n_blocks, seed=SCHEDULE_SEED)

    print(f"\nstimulus hash: {stimulus_hash()}")
    print(f"schedule hash: {schedule_hash(blocks)}")
    print(f"calls: {call_count(blocks)}\n")

    for cell in rung0.ACTUATOR_CELLS:
        label = "instruction-lambda" if cell == "A" else "payoff-lambda"
        print(f"=== cell {cell} ({label}) vs ablation ===")
        print(f"{'family':18s} {'V_abl':>7s} {'V_act':>7s} {'decline':>8s} "
              f"{'p':>7s} {'align':>6s} {'role':>6s}  verdict")
        for v in verdict.per_cell[cell]:
            lo, hi = bootstrap_ci(list(v.deltas))
            flags = []
            if not v.margin_ok:
                flags.append("margin")
            if not v.significant:
                flags.append("p")
            if not v.guards_ok:
                flags.append("PARROTING" if v.parroting else "guards")
            status = "PASS" if v.passed else "fail:" + ",".join(flags)
            print(f"{v.family_id:18s} {v.ablation_v:7.3f} {v.actuator_v:7.3f} "
                  f"{v.decline * 100:7.1f}% {v.p_value:7.3f} {v.mean_alignment:6.2f} "
                  f"{v.role_margin_ratio:6.2f}  {status}   dCI[{lo:+.3f},{hi:+.3f}]")
        n_pass = len(verdict.passing_families(cell))
        outcome = "CELL PASS" if verdict.cell_passed(cell) else "CELL FAIL"
        print(f"  -> {n_pass}/{len(FAMILIES)} families pass "
              f"(need {rung0.FAMILIES_MIN}): {outcome}\n")

    every = [v for vs in verdict.per_cell.values() for v in vs]

    def mark(ok: bool) -> str:
        return "met" if ok else "NOT met"

    print("GATE, item by item:")
    print(f"  1. margin >={rung0.DECLINE_MIN:.0%} vs matched ablation"
          f" -> {mark(any(v.margin_ok for v in every))}")
    print(f"  2. in >={rung0.FAMILIES_MIN} of {len(FAMILIES)} families"
          f" -> {mark(any(verdict.cell_passed(c) for c in verdict.per_cell))}")
    print(f"  3. one-sided Wilcoxon p<{rung0.ALPHA} at n={n_blocks}"
          f" -> {mark(any(v.significant for v in every))}")
    print(f"  4. guards (alignment <{rung0.ALIGNMENT_CEILING}, roles preserved)"
          f" -> {mark(any(v.guards_ok for v in every))}")

    if verdict.parroting_flags:
        print("\n  ** PARROTING ARTIFACT (large decline, alignment above ceiling) — not a pass: "
              f"{[v.family_id for v in verdict.parroting_flags]}")

    h_star = verdict.h_star()
    print("\nH* (concentration at the collapse point):", f"{h_star:.4f}" if h_star else "n/a")
    if h_star:
        ratio = ENDOGENOUS_H / h_star
        band = ("actuator-limited (NOT resilience)" if ratio < 0.5
                else "bounded resilience" if ratio < 1.0 else "strong resilience")
        print(f"  prior endogenous H = {ENDOGENOUS_H:.4f}"
              f" -> H_endogenous/H* = {ratio:.2f} -> {band}")
        print("  CAVEAT: this echo-concentration is the single-round analogue of prior work's")
        print("  multi-round trend. Reconcile the definitions before trusting the ratio.")
    else:
        print("  No collapse point, so no denominator: the prior endogenous null stays")
        print("  uninterpretable, and that is itself the reportable result.")

    print(f"\ntokens: {ledger.total.input} in / {ledger.total.output} out "
          f"/ {ledger.total.embedding} embed   ~${ledger.cost_usd():.4f}")
    print("\nRUNG 0 " + ("PASSED — collapse is reachable; proceed to rung 1."
                         if verdict.passed else
                         "FAILED — no accessible collapse phase. STOP and report the floor."))
    return verdict.passed


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="mock client; no key, no spend")
    ap.add_argument("--blocks", type=int, default=N_BLOCKS)
    args = ap.parse_args()

    try:
        client, ledger = build_client(args.dry_run)
    except MissingCredential as exc:
        print(f"{exc}\n\n(use --dry-run to exercise the harness without a key)", file=sys.stderr)
        return 1

    measures, _ = run(client, n_blocks=args.blocks)
    passed = report(measures, ledger, n_blocks=args.blocks)

    if not args.dry_run:
        RUNS_DIR.mkdir(exist_ok=True)
        blocks = build_schedule(n_blocks=args.blocks, seed=SCHEDULE_SEED)
        path = RUNS_DIR / f"rung0-{schedule_hash(blocks)[:12]}.json"
        path.write_text(json.dumps({
            "stimulus_hash": stimulus_hash(),
            "schedule_hash": schedule_hash(blocks),
            "model": GEN_MODEL,
            "n_blocks": args.blocks,
            "passed": passed,
            "usage": asdict(ledger.total),
            "cost_usd": ledger.cost_usd(),
            "measures": [asdict(m) for m in measures],
        }, indent=2))
        print(f"\nartifact -> {path}")
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
