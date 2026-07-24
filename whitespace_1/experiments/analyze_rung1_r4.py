"""Rung-1 confirmatory verdict — the R4 collapse criterion on the 24 artifacts.

    uv run python experiments/analyze_rung1_r4.py

Reads ``runs/rung1-r4/*.json`` (local, gitignored), runs the 10,000-draw hierarchical bootstrap, and
prints Polyphony's three ordered verdicts plus the derived rung-1 branch. Zero-spend, deterministic
(bootstrap seed pinned). Persists a compact, committable summary to ``runs/rung1-r4-confirm.json``.
"""

from __future__ import annotations

import json
import sys
from dataclasses import asdict
from pathlib import Path

from whitespace1.rung1_confirm import ConfirmThresholds, evaluate_confirmatory_artifacts

RUNS_DIR = Path(__file__).resolve().parents[1] / "runs" / "rung1-r4"


def main() -> int:
    paths = sorted(RUNS_DIR.glob("*.json"))
    if len(paths) != 24:
        print(f"expected 24 artifacts, found {len(paths)} in {RUNS_DIR}", file=sys.stderr)
        return 1
    artifacts = [json.loads(p.read_text()) for p in paths]
    r = evaluate_confirmatory_artifacts(artifacts, thresholds=ConfirmThresholds())

    print("\n======  RUNG-1 CONFIRMATORY — R4 endogenous verdict (DeepSeek V4)  ======\n")
    print(f"pairs: {r.run_count}   bootstrap: 10,000 draws, seed 20260718\n")
    print("Gate 1 - dynamic uptake (actuator live):")
    print(f"    mean d_U_pop {r.mean_uptake_delta:+.5f}  (95% lower {r.uptake_lower:+.5f})   "
          f"-> {'PASS' if r.dynamic_uptake_passed else 'FAIL'}")
    print("Gate 2 - popularity feedback (P_top4 recurrence):")
    print(f"    mean pop-uniform slope {r.mean_feedback_contrast:+.5f}  "
          f"(95% lower {r.feedback_lower:+.5f})   -> {'PASS' if r.feedback_passed else 'FAIL'}")
    print("Gate 3 - collapse (V_pair; ALL three upper bounds must be < 0):")
    print(f"    popularity V slope       {r.popularity_v_slope:+.5f}  "
          f"(95% upper {r.popularity_v_upper:+.5f})")
    print(f"    popularity - ablation V  {r.popularity_minus_ablation_v:+.5f}  "
          f"(95% upper {r.popularity_minus_ablation_upper:+.5f})")
    print(f"    popularity - uniform  V  {r.popularity_minus_uniform_v:+.5f}  "
          f"(95% upper {r.popularity_minus_uniform_upper:+.5f})")
    print(f"    -> COLLAPSE {'DETECTED' if r.collapse_passed else 'NOT detected'}")

    print("\n" + "=" * 68)
    if not r.dynamic_uptake_passed:
        verdict = "ACTUATOR NOT LIVE - the mechanism did not engage; a V null is unreadable."
    elif r.collapse_passed:
        verdict = (
            "COLLAPSE - DeepSeek outputs homogenize where GPT-5.6 did not. Polyphony's null is\n"
            "  SUBSTRATE-SPECIFIC. Major finding; do NOT proceed to rung 2 as planned (redirect)."
        )
    else:
        verdict = (
            "NO COLLAPSE under a live actuator - Polyphony's output-layer null REPLICATES on\n"
            "  DeepSeek. The bridge holds; proceed to rung 2 (add V_reason)."
        )
    print(f"RUNG-1 VERDICT: {verdict}")

    summary_path = RUNS_DIR.parent / "rung1-r4-confirm.json"
    summary_path.write_text(json.dumps(asdict(r), indent=2))
    print(f"\nsummary artifact -> {summary_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
