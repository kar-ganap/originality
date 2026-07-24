"""Rung-1 matched null — is the Gate-2 P_top4 recurrence a sampling artifact?

    uv run python experiments/analyze_rung1_null.py

Ports Polyphony's null study to the DeepSeek R4 artifacts: replay (positive control) + three nulls
(STRUCTURE / HETEROGENEOUS / POPULARITY). The decisive comparison is the popularity arm vs its
preference-free POPULARITY null — a high p means the recurrence is a property of the sampling rule,
not of the ensemble. Zero-spend, deterministic. Summary -> runs/rung1-r4-null.json.
"""

from __future__ import annotations

import json
import sys
from dataclasses import asdict
from pathlib import Path

from whitespace1.rung1_null import run_study

RUNS_DIR = Path(__file__).resolve().parents[1] / "runs" / "rung1-r4"


def main() -> int:
    if not RUNS_DIR.exists() or not list(RUNS_DIR.glob("*.json")):
        print(f"no R4 artifacts under {RUNS_DIR}", file=sys.stderr)
        return 1
    study = run_study(RUNS_DIR, n_replicates=2000)

    print("\n======  RUNG-1 MATCHED NULL — P_top4 concentration (Gate-2 secondary)  ======\n")
    print(f"replay max error {study.replay_max_error:.2e}  (positive control; ~0 validates)")
    print(f"similarity pool: {study.pool_size} values, mean {study.pool_mean:.4f}\n")

    print("observed arms (raw P_top4 slope / denominator-normalized):")
    for arm, s in sorted(study.observed.items()):
        print(f"  {arm:11s} raw {s.raw_slope:+.5f}   norm {s.normalized_slope:+.5f}   (n={s.n})")
    print("null arms (preference-free):")
    for mode in ("structure", "heterogeneous", "popularity"):
        s = study.null[mode]
        print(f"  {mode:11s} raw {s.raw_slope:+.5f}   norm {s.normalized_slope:+.5f}")

    obs = study.observed["popularity"].raw_slope - study.observed["uniform"].raw_slope
    nul = study.null["popularity"].raw_slope - study.null["heterogeneous"].raw_slope
    pct = f"{nul / obs * 100:.0f}% of observed" if obs else "n/a"
    print(f"\nobserved popularity - uniform (raw slope): {obs:+.5f}")
    print(f"null POPULARITY - HETEROGENEOUS (raw slope): {nul:+.5f}   = {pct}")

    print("\nmatched comparisons (observed arm vs its null; HIGH p = artifact):")
    for c in study.comparisons:
        print(f"  {c.arm:11s} vs {c.null_mode:13s} [{c.metric:10s}]  observed {c.observed:+.5f}  "
              f"null {c.null_mean:+.5f}  excess {c.excess:+.5f}  p={c.p_value:.4f}")

    pop_raw = next(c for c in study.comparisons if c.arm == "popularity" and c.metric == "raw")
    artifact = pop_raw.p_value > 0.05
    print("\n" + "=" * 68)
    if artifact:
        print("VERDICT: Gate-2 concentration is a SAMPLING ARTIFACT — the popularity arm is\n"
              "  indistinguishable from its preference-free null. No concentration to claim\n"
              "  (same artifact class as WS2's ref_gini and Polyphony's +0.0102).")
    else:
        print("VERDICT: the popularity arm EXCEEDS its matched null — a real concentration excess\n"
              "  survives the sampling machinery. Investigate before claiming.")

    summary = {
        "replay_max_error": study.replay_max_error,
        "pool_size": study.pool_size,
        "pool_mean": study.pool_mean,
        "observed": {k: asdict(v) for k, v in study.observed.items()},
        "null": {k: asdict(v) for k, v in study.null.items()},
        "comparisons": [asdict(c) for c in study.comparisons],
    }
    out = RUNS_DIR.parent / "rung1-r4-null.json"
    out.write_text(json.dumps(summary, indent=2))
    print(f"\nsummary artifact -> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
