"""Insulation verdict — do isolated-origin ideas get adopted more per capita? (Claim #17)

    uv run python experiments/analyze_insulation.py

Reads runs/insulation/*.json, computes per-capita adoption per origin, bootstraps the origin gap
over run-ids, comparing the pooled gap to the label-shuffle null. Zero-spend, deterministic.
Summary -> runs/insulation-confirm.json.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

from whitespace1.insulation import (
    Showing,
    adoption_gap,
    label_shuffle_null,
    live_check,
    per_capita_adoption,
)

RUNS_DIR = Path(__file__).resolve().parents[1] / "runs" / "insulation"


def _load() -> dict[str, list[Showing]]:
    runs: dict[str, list[Showing]] = {}
    for path in sorted(RUNS_DIR.glob("*.json")):
        d = json.loads(path.read_text())
        runs[d["run_id"]] = [Showing(s["origin"], float(s["echo"]), bool(s["shown"]))
                             for s in d["showings"]]
    return runs


def main() -> int:
    runs = _load()
    if len(runs) != 8:
        print(f"expected 8 insulation run-ids, found {len(runs)} in {RUNS_DIR}", file=sys.stderr)
        return 1
    all_showings = [s for sh in runs.values() for s in sh]
    lc = live_check(all_showings)
    run_gaps = np.array([adoption_gap(sh) for sh in runs.values()], dtype=np.float64)
    obs = float(run_gaps.mean())
    rng = np.random.default_rng(20260718)
    idx = rng.integers(0, len(run_gaps), size=(10_000, len(run_gaps)))
    boot = run_gaps[idx].mean(axis=1)
    lo, hi = (float(x) for x in np.percentile(boot, [2.5, 97.5]))
    pooled_gap = adoption_gap(all_showings)
    null = label_shuffle_null(all_showings, np.random.default_rng(20260724), n=10_000)
    p_null = float((null >= pooled_gap).mean())
    pc = per_capita_adoption(all_showings)

    print("\n===  INSULATION VERDICT — Claim #17 (DeepSeek V4)  ===\n")
    print(f"run-ids: {len(runs)}   bootstrap 10,000 (over run-ids); label-shuffle null 10,000\n")
    print(f"live-check (shown echo - decoy echo): {lc:+.4f}  -> "
          f"{'field responds to what it is shown' if lc > 0 else 'NOT live (unreadable)'}")
    print(f"per-capita adoption: isolated {pc['isolated']:.4f} | connected {pc['connected']:.4f}")
    print(f"gap (isolated - connected): mean {obs:+.4f}  95% CI [{lo:+.4f}, {hi:+.4f}]")
    print(f"vs label-shuffle null (pooled gap {pooled_gap:+.4f}): one-sided p = {p_null:.4f}")

    live = lc > 0
    supported = bool(live and obs > 0 and lo > 0 and p_null < 0.05)
    print("\n" + "=" * 60)
    if not live:
        verdict = "ADOPTION NOT LIVE - the field does not echo shown candidates; unreadable."
    elif supported:
        verdict = ("Claim #17 SUPPORTED - insulated-origin ideas are adopted more per capita than\n"
                   "  the connected field's own, beating the null. Insulation produces\n"
                   "  disproportionately-adopted ideas.")
    else:
        verdict = ("Claim #17 NOT supported - insulated ideas are not adopted more per capita\n"
                   "  (gap <= 0, CI includes 0, or within the null). Insulation buys no\n"
                   "  disproportionate adoption here. An informative null.")
    print(f"INSULATION VERDICT: {verdict}")

    (RUNS_DIR.parent / "insulation-confirm.json").write_text(json.dumps({
        "run_ids": len(runs), "live_check": lc, "per_capita": pc,
        "gap_mean": obs, "gap_ci": [lo, hi], "pooled_gap": pooled_gap, "null_p": p_null,
        "claim17_supported": supported,
    }, indent=2))
    print(f"\nsummary artifact -> {RUNS_DIR.parent / 'insulation-confirm.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
