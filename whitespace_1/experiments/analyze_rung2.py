"""Rung-2 two-channel verdict — does reasoning collapse where output held?

    uv run python experiments/analyze_rung2.py

Runs the R4 collapse criterion on BOTH channels of the rung-2 artifacts: V_output
(proposal_embeddings) and V_reason (skeleton_embeddings, the strategy layer). The actuator gates
(uptake, feedback) are answer-based and shared. Zero-spend, deterministic. Headline: V_reason
collapses while V_output holds -> Polyphony's output-only null is a measurement artifact in the
*endogenous* regime it actually ran. Summary -> runs/rung2-r4-confirm.json.
"""

from __future__ import annotations

import json
import sys
from dataclasses import asdict
from pathlib import Path

from whitespace1.rung1_confirm import ConfirmThresholds, evaluate_confirmatory_artifacts

RUNS_DIR = Path(__file__).resolve().parents[1] / "runs" / "rung2-r4"


def _collapse_line(label: str, r) -> None:  # noqa: ANN001
    mark = "COLLAPSE" if r.collapse_passed else "no collapse"
    pa, pau = r.popularity_minus_ablation_v, r.popularity_minus_ablation_upper
    print(f"  {label}: pop V {r.popularity_v_slope:+.5f} (up {r.popularity_v_upper:+.5f}) | "
          f"pop-abl {pa:+.5f} (up {pau:+.5f}) -> {mark}")


def main() -> int:
    paths = sorted(RUNS_DIR.glob("*.json"))
    if len(paths) != 24:
        print(f"expected 24 rung-2 artifacts, found {len(paths)} in {RUNS_DIR}", file=sys.stderr)
        return 1
    artifacts = [json.loads(p.read_text()) for p in paths]
    th = ConfirmThresholds()
    out = evaluate_confirmatory_artifacts(
        artifacts, thresholds=th, v_embeddings_key="proposal_embeddings"
    )
    rea = evaluate_confirmatory_artifacts(
        artifacts, thresholds=th, v_embeddings_key="skeleton_embeddings"
    )

    print("\n===  RUNG-2 TWO-CHANNEL VERDICT — reasoning vs output (DeepSeek V4)  ===\n")
    print(f"pairs: {out.run_count}   bootstrap: 10,000 draws, seed 20260718\n")
    print("actuator (answer-based, shared across channels):")
    print(f"  dynamic uptake {out.mean_uptake_delta:+.5f} (lower {out.uptake_lower:+.5f}) "
          f"-> {'live' if out.dynamic_uptake_passed else 'NOT live'}")
    print("collapse criterion per channel (pop slope < 0 AND all upper bounds < 0):")
    _collapse_line("V_output ", out)
    _collapse_line("V_reason ", rea)

    print("\n" + "=" * 74)
    if not out.dynamic_uptake_passed:
        verdict = "ACTUATOR NOT LIVE - the mechanism did not engage; neither channel is readable."
    elif rea.collapse_passed and not out.collapse_passed:
        verdict = (
            "V_reason COLLAPSES while V_output HOLDS -> Polyphony's output-only null is a\n"
            "  MEASUREMENT ARTIFACT: reasoning homogenizes invisibly under the endogenous actuator.\n"
            "  The arm's headline (rung 0 showed it under imposed conformity; rung 2 reaches it\n"
            "  endogenously)."
        )
    elif rea.collapse_passed and out.collapse_passed:
        verdict = "BOTH channels collapse - endogenous reachability confirmed on both layers."
    elif not rea.collapse_passed and not out.collapse_passed:
        verdict = (
            "NEITHER channel collapses under catalog-of-conclusions - the null DEEPENS (resilience\n"
            "  is not surface-level). An informative null; the reasoning-exposure actuator\n"
            "  (catalog-of-reasoning) is the next test of whether reasoning can be moved."
        )
    else:
        verdict = "V_output collapses but V_reason holds - unexpected; report the split as-is."
    print(f"RUNG-2 VERDICT: {verdict}")

    summary = {
        "v_output": asdict(out),
        "v_reason": asdict(rea),
        "headline_measurement_artifact": bool(rea.collapse_passed and not out.collapse_passed),
    }
    out_path = RUNS_DIR.parent / "rung2-r4-confirm.json"
    out_path.write_text(json.dumps(summary, indent=2))
    print(f"\nsummary artifact -> {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
