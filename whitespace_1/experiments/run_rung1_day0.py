"""Fire Rung-1 Gate 0 — the Day-0 bite gate on DeepSeek (``docs/ws1-oss-rung1-prereg.md``, Gate 0).

    uv run --extra llm python experiments/run_rung1_day0.py

Ten generations (5 no-catalog + 5 conditioned) on deepseek-v4-pro thinking-on, then one embedding
batch on the fixed ``text-embedding-3-small``. ~$0.10. **Both gates pass → build the R4 loop; either
fails → STOP** (the substrate cannot carry the endogenous arm). Needs ``DEEPSEEK_API_KEY`` +
``OPENAI_API_KEY`` in the folder-local ``.env``.
"""

from __future__ import annotations

import json
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from whitespace1 import rung1_day0 as d0
from whitespace1.client import DeepSeekClient, Ledger, OpenAICompatClient
from whitespace1.credentials import MissingCredential, require_secret

GEN_MODEL = "deepseek-v4-pro"
MAX_OUTPUT_TOKENS = 2000  # room for the reasoning trace + a 1-2 sentence answer (avoids truncation)
WORKERS = 5
EMPTY = "(no proposal)"
RUNS_DIR = Path(__file__).resolve().parents[1] / "runs"


def main() -> int:
    try:
        openai_key = require_secret("OPENAI_API_KEY")
        deepseek_key = require_secret("DEEPSEEK_API_KEY")
    except MissingCredential as exc:
        print(f"{exc}\n\n(folder-local .env with both keys is required — inherited env is refused)",
              file=sys.stderr)
        return 1

    ledger = Ledger()
    embedder = OpenAICompatClient("gpt-5.6-sol", openai_key, ledger=ledger)  # embeddings only
    gen = DeepSeekClient(GEN_MODEL, deepseek_key, thinking=True, ledger=ledger)

    def generate(prompt: str) -> str:
        text = gen.generate(prompt, max_output_tokens=MAX_OUTPUT_TOKENS).text
        return text if text.strip() else EMPTY

    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        no_catalog = list(ex.map(generate, d0.no_catalog_prompts()))
        conditioned = list(ex.map(generate, d0.conditioned_prompts()))

    n = len(no_catalog)
    emb = embedder.embed([*no_catalog, *conditioned, *d0.DAY0_CATALOG_SAMPLE])
    verdict = d0.evaluate_day0(
        no_catalog_emb=emb[:n], conditioned_emb=emb[n : 2 * n], catalog_emb=emb[2 * n :]
    )

    print("\n========  RUNG-1 GATE 0 — Day-0 bite gate (DeepSeek V4-pro, thinking on)  ========\n")
    print(f"(a) latent diversity (no-catalog V_pair): {verdict.diversity:.4f}   "
          f">= {verdict.diversity_min:.2f} ? {'PASS' if verdict.diversity_ok else 'FAIL'}")
    print(f"(b) conditioning shift: {verdict.no_catalog_alignment:.4f} -> "
          f"{verdict.conditioned_alignment:.4f}  = {verdict.alignment_shift:+.4f}   "
          f">= {verdict.shift_min:.2f} ? {'PASS' if verdict.shift_ok else 'FAIL'}")
    n_empty = sum(1 for t in (*no_catalog, *conditioned) if t == EMPTY)
    if n_empty:
        print(f"    (warning: {n_empty}/{2 * n} empty answers mapped to a placeholder)")
    print(f"\ncost ~${ledger.cost_usd():.4f}")
    print("\nGATE 0 " + (
        "PASSED -- substrate carries the endogenous arm; build the R4 loop." if verdict.passed else
        "FAILED -- DeepSeek cannot carry rung 1 as-is; STOP and report (pre-reg branch)."))

    RUNS_DIR.mkdir(exist_ok=True)
    path = RUNS_DIR / "rung1-day0-deepseek.json"
    path.write_text(json.dumps({
        "model": GEN_MODEL, "thinking": True, "passed": verdict.passed,
        "diversity": verdict.diversity, "diversity_ok": verdict.diversity_ok,
        "diversity_min": verdict.diversity_min,
        "no_catalog_alignment": verdict.no_catalog_alignment,
        "conditioned_alignment": verdict.conditioned_alignment,
        "alignment_shift": verdict.alignment_shift, "shift_ok": verdict.shift_ok,
        "shift_min": verdict.shift_min, "cost_usd": ledger.cost_usd(),
        "no_catalog_outputs": no_catalog, "conditioned_outputs": conditioned,
    }, indent=2))
    print(f"verdict artifact -> {path}")
    return 0 if verdict.passed else 2


if __name__ == "__main__":
    sys.exit(main())
