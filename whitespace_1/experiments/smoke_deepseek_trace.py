"""Trace-length smoke — measure how long DeepSeek V4 reasons on the rung-0 task.

    uv run python experiments/smoke_deepseek_trace.py

Purpose: turn the rung-0 v2 cost estimate from a range into a number *before* the full probe.
Reasoning bills at the output rate, so the whole budget rides on tokens/call — which depends on how
long the model actually reasons on *this* task (short idea-generation), not on a hard math prompt.
This makes ~20 real calls on the actual rung-0 stimuli, reports the measured trace length, and
projects the full-probe generation cost. A few cents. Also a sanity check that traces are *diverse*
across roles (a homogeneous trace would mean V_reason has nothing to measure).

Key: `DEEPSEEK_API_KEY` in the folder-local `.env` (the credential guard reads only there).
"""

from __future__ import annotations

import json
import statistics
import sys
from pathlib import Path

from whitespace1.client import PRICING, DeepSeekClient, Ledger
from whitespace1.credentials import MissingCredential, require_secret
from whitespace1.schedule import CELLS, build_schedule, render_block
from whitespace1.stimuli import ROLES

MODEL = "deepseek-v4-pro"
N_SAMPLE = 20
MAX_OUTPUT_TOKENS = 8000  # high, so the trace is measured at its natural length, not capped
SEED = 20260723
RUNS_DIR = Path(__file__).resolve().parents[1] / "runs"


def main() -> int:
    try:
        key = require_secret("DEEPSEEK_API_KEY")
    except MissingCredential as exc:
        print(f"{exc}", file=sys.stderr)
        return 1

    ledger = Ledger()
    client = DeepSeekClient(MODEL, key, reasoning_effort="high", ledger=ledger)

    blocks = build_schedule(n_blocks=5, seed=SEED)  # 5 families
    every = [
        (b.family_id, cell, r, render_block(b, cell, r))
        for b in blocks
        for cell in CELLS
        for r in range(len(ROLES))
    ]
    step = max(1, len(every) // N_SAMPLE)
    sample = every[::step][:N_SAMPLE]  # strided so families / cells / roles are all represented

    rows: list[dict] = []
    for i, (family, cell, role, prompt) in enumerate(sample, start=1):
        completion = client.generate(prompt, max_output_tokens=MAX_OUTPUT_TOKENS)
        rows.append(
            {
                "family": family,
                "cell": cell,
                "role": role,
                "reasoning_tokens": completion.usage.reasoning,
                "output_tokens": completion.usage.output,
                "input_tokens": completion.usage.input,
                "answer_chars": len(completion.text),
                "reasoning_chars": len(completion.reasoning or ""),
                "answer": completion.text,
                "reasoning": completion.reasoning,
            }
        )
        print(
            f"  [{i}/{len(sample)}] {family} {cell} r{role}: "
            f"reasoning={completion.usage.reasoning} out={completion.usage.output}",
            file=sys.stderr,
        )

    reasoning = [r["reasoning_tokens"] for r in rows]
    output = [r["output_tokens"] for r in rows]
    inp = [r["input_tokens"] for r in rows]

    print(f"\n=== DeepSeek trace smoke ({MODEL}, {len(rows)} calls) ===")
    print(f"reasoning tokens/call : mean {statistics.mean(reasoning):.0f}  "
          f"median {statistics.median(reasoning):.0f}  max {max(reasoning)}")
    print(f"output tokens/call    : mean {statistics.mean(output):.0f}  max {max(output)}  "
          "(reasoning + answer, both billed at output rate)")
    print(f"input tokens/call     : mean {statistics.mean(inp):.0f}")
    empty = sum(1 for r in rows if not r["reasoning_tokens"])
    if empty:
        print(f"  ** {empty}/{len(rows)} calls returned NO reasoning trace — is thinking enabled?")
    print(f"smoke cost            : ${ledger.cost_usd():.4f}")

    mean_out, mean_in = statistics.mean(output), statistics.mean(inp)
    print("\nprojected FULL-PROBE generation cost (input + output, embeddings/extraction extra):")
    for n_calls in (1000, 1250):
        for model in ("deepseek-v4-pro", "deepseek-v4-flash"):
            p_in, p_out = PRICING[model]
            gen = (n_calls * mean_in * p_in + n_calls * mean_out * p_out) / 1e6
            print(f"  {n_calls:>4} calls · {model:18s}: ${gen:.2f}")

    RUNS_DIR.mkdir(exist_ok=True)
    path = RUNS_DIR / "deepseek-trace-smoke.json"
    path.write_text(
        json.dumps({"model": MODEL, "cost_usd": ledger.cost_usd(), "rows": rows}, indent=2)
    )
    print(f"\nartifact -> {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
