"""Run the rung-0 stimulus preflight and print a pass/fail report.

Token-free criteria (C1, C4, C5) always run. The embedding- and generation-backed criteria
(C2, C3, C6) require a **folder-local** ``whitespace_1/.env``; an inherited shell key is
deliberately refused (see ``whitespace1.credentials``).

    uv run python experiments/run_preflight.py
"""

from __future__ import annotations

import sys
from collections.abc import Sequence

import numpy as np
from numpy.typing import NDArray

from whitespace1 import preflight as pf
from whitespace1.credentials import MissingCredential, require_secret
from whitespace1.stimuli import stimulus_hash

EMBED_MODEL = "text-embedding-3-small"
GEN_MODEL = "gpt-5.6-sol"
MAX_OUTPUT_TOKENS = 120


def _client(api_key: str):  # noqa: ANN202 - thin SDK wrapper
    from openai import OpenAI

    return OpenAI(api_key=api_key)


def main() -> int:
    print(f"stimulus hash: {stimulus_hash()}\n")

    results = [pf.check_open_brief(), pf.check_length_balance(), pf.check_no_leakage()]

    try:
        key = require_secret("OPENAI_API_KEY")
    except MissingCredential as exc:
        for c in results:
            print(f"[{'PASS' if c.passed else 'FAIL'}] {c.name}\n        {c.detail}")
        print(f"\n[BLOCKED] C2, C3, C6 need a folder-local key.\n\n{exc}\n")
        return 1

    client = _client(key)
    spend = {"embed_tokens": 0, "in": 0, "out": 0}

    def embed(texts: Sequence[str]) -> NDArray[np.float64]:
        resp = client.embeddings.create(model=EMBED_MODEL, input=list(texts))
        if resp.usage is not None:
            spend["embed_tokens"] += resp.usage.total_tokens
        return np.asarray([d.embedding for d in resp.data], dtype=np.float64)

    def generate(prompt: str) -> str:
        resp = client.responses.create(
            model=GEN_MODEL,
            input=prompt,
            max_output_tokens=MAX_OUTPUT_TOKENS,
            reasoning={"effort": "none"},
        )
        if resp.usage is not None:
            spend["in"] += resp.usage.input_tokens
            spend["out"] += resp.usage.output_tokens
        return resp.output_text.strip()

    results += [
        pf.check_card_spread(embed),
        pf.check_family_separation(embed),
        pf.check_ceiling_sanity(generate, embed),
    ]

    for c in results:
        print(f"[{'PASS' if c.passed else 'FAIL'}] {c.name}\n        {c.detail}")

    cost = spend["in"] * 5 / 1e6 + spend["out"] * 30 / 1e6 + spend["embed_tokens"] * 0.02 / 1e6
    print(
        f"\ntokens: {spend['in']} in / {spend['out']} out / {spend['embed_tokens']} embed"
        f"   ~${cost:.4f}"
    )

    failed = [c.name for c in results if not c.passed]
    verdict = "PASSED - stimuli may be frozen." if not failed else f"FAILED: {failed}"
    print(f"\nPREFLIGHT {verdict}")
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
