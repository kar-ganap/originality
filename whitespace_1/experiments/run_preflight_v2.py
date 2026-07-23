"""Run the rung-0 **v2** stimulus preflight — the pre-spend gate (docs/ws1-oss-rung0-v2-prereg.md).

    uv run python experiments/run_preflight_v2.py

Carries over the v1 criteria (C1-C6) and adds the v2 ones: C7 (the new cells render as designed,
token-free) and C8 (the positive control genuinely collapses — the identifiability anchor).
Generation runs on the actual v2 substrate, **DeepSeek** (thinking OFF for these V_output sanity
checks — the probe itself keeps thinking on for V_reason); embeddings on the fixed
`text-embedding-3-small`. Needs a folder-local `.env` with `DEEPSEEK_API_KEY` + `OPENAI_API_KEY`.
"""

from __future__ import annotations

import sys
from collections.abc import Sequence

import numpy as np
from numpy.typing import NDArray

from whitespace1 import preflight as pf
from whitespace1.client import DeepSeekClient, Ledger, OpenAICompatClient
from whitespace1.credentials import MissingCredential, require_secret
from whitespace1.stimuli import stimulus_hash

GEN_MODEL = "deepseek-v4-pro"  # the probe substrate; thinking off here for a fast V_output sanity
MAX_OUTPUT_TOKENS = 200


def main() -> int:
    print(f"stimulus hash: {stimulus_hash()}\n")

    # Token-free criteria run unconditionally.
    results = [
        pf.check_open_brief(),
        pf.check_length_balance(),
        pf.check_no_leakage(),
        pf.check_v2_cell_structure(),
    ]

    try:
        openai_key = require_secret("OPENAI_API_KEY")
        deepseek_key = require_secret("DEEPSEEK_API_KEY")
    except MissingCredential as exc:
        for c in results:
            print(f"[{'PASS' if c.passed else 'FAIL'}] {c.name}\n        {c.detail}")
        print(f"\n[BLOCKED] the embedding/generation criteria need folder-local keys.\n\n{exc}\n")
        return 1

    ledger = Ledger()
    embedder = OpenAICompatClient("gpt-5.6-sol", openai_key, ledger=ledger)  # embeddings only
    gen_client = DeepSeekClient(
        GEN_MODEL, deepseek_key, thinking=False, embed_with=embedder, ledger=ledger
    )

    def embed(texts: Sequence[str]) -> NDArray[np.float64]:
        return embedder.embed(texts)

    def generate(prompt: str) -> str:
        return gen_client.generate(prompt, max_output_tokens=MAX_OUTPUT_TOKENS).text

    results += [
        pf.check_card_spread(embed),
        pf.check_family_separation(embed),
        pf.check_positive_control_collapse(generate, embed),  # C8 — the anchor
        pf.check_ceiling_sanity(generate, embed),  # C6 — the ablation baseline
    ]

    for c in results:
        print(f"[{'PASS' if c.passed else 'FAIL'}] {c.name}\n        {c.detail}", flush=True)

    print(f"\ncost: ~${ledger.cost_usd():.4f}  ({ledger.total.output} gen-out tokens, "
          f"{ledger.total.embedding} embed)")

    failed = [c.name for c in results if not c.passed]
    verdict = "PASSED — stimuli may be frozen." if not failed else f"FAILED: {failed}"
    print(f"\nPREFLIGHT v2 {verdict}")
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
