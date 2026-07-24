"""Catalog-of-reasoning verdict — does reasoning collapse when agents see each other's reasoning?

    uv run python experiments/analyze_rung2_reasoning.py

Runs the collapse criterion on the reasoning-actuator artifacts. The actuator acts on reasoning, so
V_reason (skeletons) is the PRIMARY channel and uptake is reasoning-side; V_output (answers) is
secondary. Zero-spend. Headline: V_reason collapses -> reasoning-collapse requires exposure
(a mechanism finding). Summary -> runs/rung2-reasoning-confirm.json.
"""

from __future__ import annotations

import json
import sys
from dataclasses import asdict
from pathlib import Path

from whitespace1.rung1_confirm import ConfirmThresholds, evaluate_confirmatory_artifacts

RUNS_DIR = Path(__file__).resolve().parents[1] / "runs" / "rung2-reasoning"


def _collapse_line(label: str, r) -> None:  # noqa: ANN001
    mark = "COLLAPSE" if r.collapse_passed else "no collapse"
    pa, pau = r.popularity_minus_ablation_v, r.popularity_minus_ablation_upper
    print(f"  {label}: pop V {r.popularity_v_slope:+.5f} (up {r.popularity_v_upper:+.5f}) | "
          f"pop-abl {pa:+.5f} (up {pau:+.5f}) -> {mark}")


def main() -> int:
    paths = sorted(RUNS_DIR.glob("*.json"))
    if len(paths) != 24:
        print(f"expected 24 reasoning artifacts, found {len(paths)} in {RUNS_DIR}", file=sys.stderr)
        return 1
    artifacts = [json.loads(p.read_text()) for p in paths]
    th = ConfirmThresholds()
    # the actuator acts on reasoning: uptake is skeleton-side for both channels
    rea = evaluate_confirmatory_artifacts(
        artifacts, thresholds=th,
        v_embeddings_key="skeleton_embeddings", uptake_embeddings_key="skeleton_embeddings",
    )
    out = evaluate_confirmatory_artifacts(
        artifacts, thresholds=th,
        v_embeddings_key="proposal_embeddings", uptake_embeddings_key="skeleton_embeddings",
    )

    print("\n===  CATALOG-OF-REASONING VERDICT — reasoning-exposure (DeepSeek V4)  ===\n")
    print(f"pairs: {rea.run_count}   bootstrap: 10,000 draws, seed 20260718\n")
    print("actuator (reasoning-side: do agents take up the shown reasoning?):")
    print(f"  dynamic uptake {rea.mean_uptake_delta:+.5f} (lower {rea.uptake_lower:+.5f}) "
          f"-> {'live' if rea.dynamic_uptake_passed else 'NOT live'}")
    print("collapse criterion per channel (pop slope < 0 AND all upper bounds < 0):")
    _collapse_line("V_reason (primary)", rea)
    _collapse_line("V_output (2ndary) ", out)

    print("\n" + "=" * 70)
    if not rea.dynamic_uptake_passed:
        verdict = "ACTUATOR NOT LIVE - agents did not take up the shown reasoning; unreadable."
    elif rea.collapse_passed:
        verdict = (
            "V_reason COLLAPSES under reasoning-exposure -> reasoning-collapse REQUIRES\n"
            "  reasoning-exposure. Mechanism finding: sharing conclusions leaves reasoning\n"
            "  diverse (rung 2a), but sharing the reasoning itself homogenizes it. Bounds the\n"
            "  deployment risk to trace-sharing systems."
        )
    else:
        verdict = (
            "V_reason HOLDS even under reasoning-exposure -> the resilience is deep: showing\n"
            "  agents each other's reasoning still does not homogenize it. Polyphony's null is\n"
            "  robust to the strongest reasoning-side actuator this arm can build."
        )
    print(f"REASONING VERDICT: {verdict}")

    summary = {
        "v_reason_primary": asdict(rea),
        "v_output_secondary": asdict(out),
        "reasoning_collapses_under_exposure": bool(rea.collapse_passed),
    }
    out_path = RUNS_DIR.parent / "rung2-reasoning-confirm.json"
    out_path.write_text(json.dumps(summary, indent=2))
    print(f"\nsummary artifact -> {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
