"""Phase 0.2 Wave 1B — NamSor smoke (50-name × 6-region accuracy).

Validates NamSor's gender-inference accuracy claims on a stratified
small batch BEFORE the production-scale escalation in Stage 1. Per
Phase 0.2 plan, NamSor is the locked escalation for the
low-confidence subset that gender_guesser + Genderize won't commit
on; particularly relevant for East-Asian / South-Asian / Arabic /
Slavic name regions where the name-list-lookup methods underperform.

Smoke design:
- 8 names × 6 regions = 48 names (close to 50 target).
- Call NamSor's gender batch endpoint (`/genderBatch`).
- Record response per name + aggregate per-region confidence (mean,
  min, count).
- Cache full response JSON for reproducibility.

Acceptance per `phase-0.2-execution.md` Wave 1B:
- API key in env (NAMSOR_API_KEY); script reads via python-dotenv.
- 50-name response cached for reproducibility.
- Per-region accuracy table logged.

Setup:
1. Sign up at https://namsor.com/ for an API key.
2. Copy `.env.example` to `.env` and fill in `NAMSOR_API_KEY=<your key>`.
3. Run: `uv run python experiments/phase-0.2/namsor_smoke.py`

Cost: NamSor free tier ~500 calls/mo; this smoke uses 48. Production
escalation cost-bounded by Stage 1 budget (locked $0-500 in §9).
"""

from __future__ import annotations

import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests
from dotenv import load_dotenv

_OUT_DIR = Path(__file__).parent

# Load .env from project root (whitespace_2/.env)
load_dotenv(_OUT_DIR.parent.parent / ".env")

_NAMSOR_API_KEY = os.environ.get("NAMSOR_API_KEY")
_NAMSOR_BASE_URL = "https://v2.namsor.com/NamSorAPIv2/api2/json"
_USER_AGENT = "ws2/0.0.0 NamSor smoke"

# Stratified 8-name × 6-region batch (48 names; near 50 target).
# Names sampled to cover the regional space NamSor is locked-in for.
# Format: list of {"id", "firstName", "lastName", "expected_gender",
#                  "region"}. Expected genders set per common public
# usage; NamSor's "score" is what we measure.
_NAMES: list[dict[str, str]] = [
    # Anglo (8)
    {"id": "anglo_01", "firstName": "John", "lastName": "Smith",
     "expected_gender": "male", "region": "anglo"},
    {"id": "anglo_02", "firstName": "Mary", "lastName": "Johnson",
     "expected_gender": "female", "region": "anglo"},
    {"id": "anglo_03", "firstName": "James", "lastName": "Williams",
     "expected_gender": "male", "region": "anglo"},
    {"id": "anglo_04", "firstName": "Patricia", "lastName": "Brown",
     "expected_gender": "female", "region": "anglo"},
    {"id": "anglo_05", "firstName": "Robert", "lastName": "Jones",
     "expected_gender": "male", "region": "anglo"},
    {"id": "anglo_06", "firstName": "Jennifer", "lastName": "Davis",
     "expected_gender": "female", "region": "anglo"},
    {"id": "anglo_07", "firstName": "Michael", "lastName": "Miller",
     "expected_gender": "male", "region": "anglo"},
    {"id": "anglo_08", "firstName": "Linda", "lastName": "Wilson",
     "expected_gender": "female", "region": "anglo"},
    # East-Asian (8) — Chinese, Japanese, Korean
    {"id": "easian_01", "firstName": "Wei", "lastName": "Zhang",
     "expected_gender": "male", "region": "east_asian"},
    {"id": "easian_02", "firstName": "Mei", "lastName": "Chen",
     "expected_gender": "female", "region": "east_asian"},
    {"id": "easian_03", "firstName": "Hiroshi", "lastName": "Tanaka",
     "expected_gender": "male", "region": "east_asian"},
    {"id": "easian_04", "firstName": "Yuki", "lastName": "Sato",
     "expected_gender": "female", "region": "east_asian"},
    {"id": "easian_05", "firstName": "Min-jun", "lastName": "Kim",
     "expected_gender": "male", "region": "east_asian"},
    {"id": "easian_06", "firstName": "Ji-hye", "lastName": "Park",
     "expected_gender": "female", "region": "east_asian"},
    {"id": "easian_07", "firstName": "Jun", "lastName": "Wang",
     "expected_gender": "male", "region": "east_asian"},
    {"id": "easian_08", "firstName": "Xiu", "lastName": "Liu",
     "expected_gender": "female", "region": "east_asian"},
    # South-Asian (8) — Indian, Pakistani, Bangladeshi
    {"id": "sasian_01", "firstName": "Raj", "lastName": "Patel",
     "expected_gender": "male", "region": "south_asian"},
    {"id": "sasian_02", "firstName": "Priya", "lastName": "Sharma",
     "expected_gender": "female", "region": "south_asian"},
    {"id": "sasian_03", "firstName": "Arjun", "lastName": "Kumar",
     "expected_gender": "male", "region": "south_asian"},
    {"id": "sasian_04", "firstName": "Aisha", "lastName": "Singh",
     "expected_gender": "female", "region": "south_asian"},
    {"id": "sasian_05", "firstName": "Vikram", "lastName": "Reddy",
     "expected_gender": "male", "region": "south_asian"},
    {"id": "sasian_06", "firstName": "Anjali", "lastName": "Gupta",
     "expected_gender": "female", "region": "south_asian"},
    {"id": "sasian_07", "firstName": "Imran", "lastName": "Khan",
     "expected_gender": "male", "region": "south_asian"},
    {"id": "sasian_08", "firstName": "Fatima", "lastName": "Rahman",
     "expected_gender": "female", "region": "south_asian"},
    # Arabic (8) — Levantine, Gulf, North African
    {"id": "arab_01", "firstName": "Mohammed", "lastName": "Al-Rashid",
     "expected_gender": "male", "region": "arabic"},
    {"id": "arab_02", "firstName": "Fatima", "lastName": "Hassan",
     "expected_gender": "female", "region": "arabic"},
    {"id": "arab_03", "firstName": "Ahmed", "lastName": "Ibrahim",
     "expected_gender": "male", "region": "arabic"},
    {"id": "arab_04", "firstName": "Layla", "lastName": "Mansour",
     "expected_gender": "female", "region": "arabic"},
    {"id": "arab_05", "firstName": "Yusuf", "lastName": "Nasser",
     "expected_gender": "male", "region": "arabic"},
    {"id": "arab_06", "firstName": "Aaliyah", "lastName": "Khalil",
     "expected_gender": "female", "region": "arabic"},
    {"id": "arab_07", "firstName": "Omar", "lastName": "Saleh",
     "expected_gender": "male", "region": "arabic"},
    {"id": "arab_08", "firstName": "Noor", "lastName": "Hamdan",
     "expected_gender": "female", "region": "arabic"},
    # Slavic (8) — Russian, Polish, Czech, Ukrainian
    {"id": "slavic_01", "firstName": "Ivan", "lastName": "Petrov",
     "expected_gender": "male", "region": "slavic"},
    {"id": "slavic_02", "firstName": "Anna", "lastName": "Sokolova",
     "expected_gender": "female", "region": "slavic"},
    {"id": "slavic_03", "firstName": "Pavel", "lastName": "Novak",
     "expected_gender": "male", "region": "slavic"},
    {"id": "slavic_04", "firstName": "Olga", "lastName": "Volkova",
     "expected_gender": "female", "region": "slavic"},
    {"id": "slavic_05", "firstName": "Andrzej", "lastName": "Kowalski",
     "expected_gender": "male", "region": "slavic"},
    {"id": "slavic_06", "firstName": "Katarzyna", "lastName": "Nowak",
     "expected_gender": "female", "region": "slavic"},
    {"id": "slavic_07", "firstName": "Dmitri", "lastName": "Ivanov",
     "expected_gender": "male", "region": "slavic"},
    {"id": "slavic_08", "firstName": "Svetlana", "lastName": "Kuznetsova",
     "expected_gender": "female", "region": "slavic"},
    # Other (8) — Hispanic, African, Persian, Southeast-Asian
    {"id": "other_01", "firstName": "Carlos", "lastName": "Rodriguez",
     "expected_gender": "male", "region": "other"},
    {"id": "other_02", "firstName": "Maria", "lastName": "Garcia",
     "expected_gender": "female", "region": "other"},
    {"id": "other_03", "firstName": "Adesola", "lastName": "Okonkwo",
     "expected_gender": "female", "region": "other"},
    {"id": "other_04", "firstName": "Kwame", "lastName": "Asante",
     "expected_gender": "male", "region": "other"},
    {"id": "other_05", "firstName": "Reza", "lastName": "Hosseini",
     "expected_gender": "male", "region": "other"},
    {"id": "other_06", "firstName": "Soraya", "lastName": "Karimi",
     "expected_gender": "female", "region": "other"},
    {"id": "other_07", "firstName": "Nguyen", "lastName": "Tran",
     "expected_gender": "male", "region": "other"},
    {"id": "other_08", "firstName": "Aroon", "lastName": "Suksawat",
     "expected_gender": "male", "region": "other"},
]


def _call_namsor_gender_batch(
    api_key: str, names: list[dict[str, str]],
) -> dict[str, Any]:
    url = f"{_NAMSOR_BASE_URL}/genderBatch"
    payload = {
        "personalNames": [
            {
                "id": n["id"],
                "firstName": n["firstName"],
                "lastName": n["lastName"],
            }
            for n in names
        ]
    }
    headers = {
        "X-API-KEY": api_key,
        "Content-Type": "application/json",
        "User-Agent": _USER_AGENT,
        "Accept": "application/json",
    }
    response = requests.post(url, headers=headers, json=payload, timeout=60)
    response.raise_for_status()
    data: dict[str, Any] = response.json()
    return data


def main() -> None:
    print("Phase 0.2 Wave 1B — NamSor 50-name × 6-region smoke")
    print()

    if not _NAMSOR_API_KEY:
        print("ERROR: NAMSOR_API_KEY not in env.")
        print()
        print("Setup:")
        print("  1. Sign up at https://namsor.com/")
        print("  2. Copy .env.example to .env (cd whitespace_2/)")
        print("  3. Fill in NAMSOR_API_KEY=<your key> in .env")
        print("  4. Re-run: uv run python experiments/phase-0.2/namsor_smoke.py")
        sys.exit(2)

    snapshot = datetime.now(timezone.utc).isoformat(timespec="seconds")
    print(f"Calling NamSor /genderBatch on {len(_NAMES)} names...")
    t0 = time.time()
    response = _call_namsor_gender_batch(_NAMSOR_API_KEY, _NAMES)
    elapsed = time.time() - t0
    print(f"  done in {elapsed:.1f}s")
    print()

    # Cache full response
    cache_path = _OUT_DIR / "namsor-smoke-response.json"
    cache_path.write_text(json.dumps(
        {"snapshot": snapshot, "names": _NAMES, "response": response},
        indent=2, default=str,
    ))
    print(f"Cached response: {cache_path}")
    print()

    # Build per-name lookup from response
    inferences = response.get("personalNames", [])
    inf_by_id: dict[str, dict[str, Any]] = {
        str(item.get("id")): item for item in inferences if isinstance(item, dict)
    }

    # Per-name analysis
    per_name_rows: list[dict[str, Any]] = []
    for n in _NAMES:
        inf = inf_by_id.get(n["id"], {})
        likely_gender = inf.get("likelyGender")
        score = inf.get("score")
        prob_cal = inf.get("probabilityCalibrated")
        match = (
            likely_gender == n["expected_gender"]
            if likely_gender is not None else None
        )
        per_name_rows.append({
            "id": n["id"],
            "region": n["region"],
            "name": f"{n['firstName']} {n['lastName']}",
            "expected": n["expected_gender"],
            "predicted": likely_gender,
            "score": score,
            "prob_calibrated": prob_cal,
            "match": match,
        })

    # Per-region aggregation
    per_region: dict[str, dict[str, Any]] = {}
    for region in {n["region"] for n in _NAMES}:
        rows = [r for r in per_name_rows if r["region"] == region]
        n_total = len(rows)
        n_resolved = sum(1 for r in rows if r["predicted"] is not None)
        n_match = sum(1 for r in rows if r["match"])
        scores = [r["score"] for r in rows if isinstance(r["score"], (int, float))]
        probs = [
            r["prob_calibrated"] for r in rows
            if isinstance(r["prob_calibrated"], (int, float))
        ]
        per_region[region] = {
            "n_total": n_total,
            "n_resolved": n_resolved,
            "n_match_expected": n_match,
            "match_rate": n_match / n_total if n_total else 0.0,
            "score_mean": sum(scores) / len(scores) if scores else None,
            "score_min": min(scores) if scores else None,
            "prob_cal_mean": sum(probs) / len(probs) if probs else None,
            "prob_cal_min": min(probs) if probs else None,
        }

    # Print per-region table
    print("Per-region accuracy summary:")
    hdr = f"{'region':<13} {'n':>3} {'resolved':>9} {'match':>6} {'rate':>6} {'p_cal_mean':>11}"
    print(hdr)
    print("-" * len(hdr))
    for region in sorted(per_region.keys()):
        s = per_region[region]
        rate_str = f"{s['match_rate']:.3f}"
        pcm = s["prob_cal_mean"]
        pcm_str = f"{pcm:.3f}" if pcm is not None else "—"
        print(
            f"{region:<13} {s['n_total']:>3} {s['n_resolved']:>9} "
            f"{s['n_match_expected']:>6} {rate_str:>6} {pcm_str:>11}"
        )
    print()

    # Write artifact md
    md_lines = [
        "# Phase 0.2 Wave 1B — NamSor 50-name × 6-region smoke",
        "",
        f"**Run date:** {datetime.now(timezone.utc).date().isoformat()}",
        f"**Snapshot:** {snapshot}",
        "**API:** NamSor v2 /genderBatch",
        f"**Wall-clock:** {elapsed:.1f}s for {len(_NAMES)} names",
        "",
        "## Per-region accuracy",
        "",
        "| Region | N | Resolved | Match expected | Rate | p_calibrated mean | p_calibrated min |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for region in sorted(per_region.keys()):
        s = per_region[region]
        pcm = s["prob_cal_mean"]
        pcmin = s["prob_cal_min"]
        pcm_str = f"{pcm:.3f}" if pcm is not None else "—"
        pcmin_str = f"{pcmin:.3f}" if pcmin is not None else "—"
        md_lines.append(
            f"| {region} | {s['n_total']} | {s['n_resolved']} | "
            f"{s['n_match_expected']} | {s['match_rate']:.3f} | "
            f"{pcm_str} | {pcmin_str} |"
        )

    md_lines += [
        "",
        "## Per-name table",
        "",
        "| ID | Region | Name | Expected | Predicted | Score | p_cal | Match? |",
        "|---|---|---|---|---|---:|---:|---|",
    ]
    for r in per_name_rows:
        score = r["score"]
        prob = r["prob_calibrated"]
        score_str = f"{score:.3f}" if isinstance(score, (int, float)) else "—"
        prob_str = f"{prob:.3f}" if isinstance(prob, (int, float)) else "—"
        match_str = (
            "✅" if r["match"] is True
            else ("❌" if r["match"] is False else "—")
        )
        md_lines.append(
            f"| {r['id']} | {r['region']} | {r['name']} | "
            f"{r['expected']} | {r['predicted'] or '—'} | "
            f"{score_str} | {prob_str} | {match_str} |"
        )

    md_lines += [
        "",
        "## Notes",
        "",
        "- **Score** is NamSor's raw confidence; **probabilityCalibrated** is "
        "the calibrated [0, 1] probability the prediction is correct (per "
        "NamSor's calibration set).",
        "- The 'expected' column is a sanity-check ground truth based on "
        "common usage — *not* claimed authoritative. Some names are "
        "genuinely ambiguous (e.g., gender-balanced first names within a "
        "region).",
        "- For Stage 1 production, NamSor is locked as the escalation for "
        "the low-confidence subset that gender_guesser + Genderize won't "
        "commit on (per `phase-0.2-plan.md` §4).",
        "",
        "## Acceptance check (Wave 1B)",
        "",
        "- API key in env (NAMSOR_API_KEY): ✅ (load_dotenv from .env)",
        "- 50-name response cached: ✅ (`namsor-smoke-response.json`)",
        "- Per-region accuracy table logged: ✅ (above)",
        "",
        "## Artifacts",
        "",
        "- `experiments/phase-0.2/namsor-smoke.md` — this artifact",
        "- `experiments/phase-0.2/namsor-smoke-response.json` — full API response cache",
        "- `experiments/phase-0.2/namsor_smoke.py` — this script",
    ]

    md_path = _OUT_DIR / "namsor-smoke.md"
    md_path.write_text("\n".join(md_lines) + "\n")
    print(f"Wrote {md_path}")
    print()

    print("Wave 1B smoke complete.")


if __name__ == "__main__":
    main()
    sys.exit(0)
