"""Provider-agnostic generation client.

Rung 0 runs on GPT-5.6 via the OpenAI-compatible path. The same path serves OSS endpoints at
rung 1 by pointing ``base_url`` at Together/Fireworks/DeepInfra. Claude gets its own path because
extended thinking is a different request/response shape.

**Reasoning-layer caveat (verified against the Anthropic API reference, 2026-07-22).** Claude never
returns the raw chain of thought. ``thinking={"type": "adaptive", "display": "summarized"}`` returns
a *readable summary* of the reasoning; the default ``display="omitted"`` returns thinking blocks
whose text is empty. Thinking is billed at the output rate and there is no separate reasoning-token
usage field. So ``Completion.reasoning`` carries a **summary** on Claude and a **raw trace** on OSS
long-CoT models — these are not the same measurement, and §5 of the design note must treat them as
distinct instruments rather than one. See ``docs/ws1-oss-reasoning-arm.md`` §8.
"""

from __future__ import annotations

import threading
from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Any, Protocol, cast

import numpy as np
from numpy.typing import NDArray

# USD per 1M tokens (input, output). Verified 2026-07-22; DeepSeek added 2026-07-23.
PRICING: dict[str, tuple[float, float]] = {
    "gpt-5.6-sol": (5.00, 30.00),
    "gpt-5.6-terra": (2.50, 15.00),
    "gpt-5.6-luna": (1.00, 6.00),
    "claude-opus-4-8": (5.00, 25.00),
    "claude-sonnet-5": (3.00, 15.00),
    "claude-haiku-4-5": (1.00, 5.00),
    # DeepSeek V4 (thinking mode) — the OSS reasoning substrate. Reasoning bills at the output rate.
    "deepseek-v4-pro": (0.435, 0.87),
    "deepseek-v4-flash": (0.14, 0.28),
    "text-embedding-3-small": (0.02, 0.00),
}


@dataclass(frozen=True)
class Usage:
    """Token counts for one call. ``reasoning`` is a subset of ``output`` where reported."""

    input: int = 0
    output: int = 0
    reasoning: int = 0
    embedding: int = 0

    def __add__(self, other: Usage) -> Usage:
        return Usage(
            self.input + other.input,
            self.output + other.output,
            self.reasoning + other.reasoning,
            self.embedding + other.embedding,
        )


@dataclass(frozen=True)
class Completion:
    """One generation.

    ``reasoning`` is the articulated reasoning where the provider exposes it: a **summary** on
    Claude, a **raw trace** on OSS long-CoT models, and ``None`` on GPT-5.6 at effort ``none``.
    """

    text: str
    usage: Usage
    reasoning: str | None = None


class LLMClient(Protocol):
    """The seam. Rungs 1+ swap implementations without touching experiment code."""

    model: str

    def generate(self, prompt: str, *, max_output_tokens: int) -> Completion: ...

    def embed(self, texts: Sequence[str]) -> NDArray[np.float64]: ...


@dataclass
class Ledger:
    """Running token/cost tally. Rung 0 doubles as the cost calibration for later rungs.

    ``record`` is lock-guarded so concurrent generation workers (rung-0 v2) can share one ledger.
    """

    total: Usage = field(default_factory=Usage)
    by_model: dict[str, Usage] = field(default_factory=dict)
    _lock: threading.Lock = field(default_factory=threading.Lock, repr=False, compare=False)

    def record(self, model: str, usage: Usage) -> None:
        with self._lock:
            self.total = self.total + usage
            self.by_model[model] = self.by_model.get(model, Usage()) + usage

    def cost_usd(self) -> float:
        total = 0.0
        for model, u in self.by_model.items():
            inp, out = PRICING.get(model, (0.0, 0.0))
            total += u.input * inp / 1e6 + u.output * out / 1e6
            total += u.embedding * PRICING["text-embedding-3-small"][0] / 1e6
        return total


class OpenAICompatClient:
    """GPT-5.6 and any OpenAI-compatible endpoint (OSS via ``base_url``).

    ``reasoning_effort`` is ``"none"`` for rung 0. OSS long-CoT models served behind an
    OpenAI-compatible shim expose their trace differently per provider; ``reasoning`` stays ``None``
    here until rung 1 pins a provider and its trace field.
    """

    def __init__(
        self,
        model: str,
        api_key: str,
        *,
        base_url: str | None = None,
        embedding_model: str = "text-embedding-3-small",
        reasoning_effort: str = "none",
        ledger: Ledger | None = None,
    ) -> None:
        from openai import OpenAI

        self.model = model
        self.embedding_model = embedding_model
        self.reasoning_effort = reasoning_effort
        self.ledger = ledger if ledger is not None else Ledger()
        self._client = OpenAI(api_key=api_key, base_url=base_url)

    def generate(self, prompt: str, *, max_output_tokens: int) -> Completion:
        resp = self._client.responses.create(
            model=self.model,
            input=prompt,
            max_output_tokens=max_output_tokens,
            reasoning=cast(Any, {"effort": self.reasoning_effort}),
        )
        usage = Usage()
        if resp.usage is not None:
            usage = Usage(input=resp.usage.input_tokens, output=resp.usage.output_tokens)
        self.ledger.record(self.model, usage)
        return Completion(text=resp.output_text.strip(), usage=usage)

    def embed(self, texts: Sequence[str]) -> NDArray[np.float64]:
        resp = self._client.embeddings.create(model=self.embedding_model, input=list(texts))
        if resp.usage is not None:
            self.ledger.record(self.model, Usage(embedding=resp.usage.total_tokens))
        return np.asarray([d.embedding for d in resp.data], dtype=np.float64)


class AnthropicClient:
    """Claude with extended thinking — the reasoning seam for rung 2+.

    Requests ``thinking={"type": "adaptive", "display": "summarized"}``. Do **not** send
    ``budget_tokens``: it is removed on Opus 4.8/4.7, Sonnet 5, and Fable 5 and returns a 400.
    ``display`` must be set explicitly — the default omits the text.
    """

    def __init__(
        self,
        model: str,
        api_key: str,
        *,
        effort: str = "high",
        thinking: bool = True,
        embed_with: LLMClient | None = None,
        ledger: Ledger | None = None,
    ) -> None:
        from anthropic import Anthropic

        self.model = model
        self.effort = effort
        self.thinking = thinking
        self.ledger = ledger if ledger is not None else Ledger()
        self._embed_with = embed_with
        self._client = Anthropic(api_key=api_key)

    def generate(self, prompt: str, *, max_output_tokens: int) -> Completion:
        kwargs: dict[str, Any] = {
            "model": self.model,
            "max_tokens": max_output_tokens,
            "output_config": {"effort": self.effort},
            "messages": [{"role": "user", "content": prompt}],
        }
        if self.thinking:
            kwargs["thinking"] = {"type": "adaptive", "display": "summarized"}
        resp = self._client.messages.create(**kwargs)

        text_parts, reasoning_parts = [], []
        for block in resp.content:
            if block.type == "text":
                text_parts.append(block.text)
            elif block.type == "thinking":
                reasoning_parts.append(block.thinking)

        # Anthropic bills thinking at the output rate and reports no separate reasoning field.
        usage = Usage(input=resp.usage.input_tokens, output=resp.usage.output_tokens)
        self.ledger.record(self.model, usage)
        return Completion(
            text="".join(text_parts).strip(),
            usage=usage,
            reasoning="".join(reasoning_parts).strip() or None,
        )

    def embed(self, texts: Sequence[str]) -> NDArray[np.float64]:
        """Anthropic serves no embedding endpoint - delegate to an injected embedder.

        Holding the embedder fixed across backends is required by the design: a cross-model
        ``V_output`` comparison must not vary the measuring instrument.
        """
        if self._embed_with is None:
            raise RuntimeError(
                "AnthropicClient has no embedding backend. Pass "
                "embed_with=<an OpenAICompatClient> so embeddings stay on one "
                "fixed model across generation backends."
            )
        return self._embed_with.embed(texts)


class DeepSeekClient:
    """DeepSeek V4 with thinking mode — the OSS reasoning substrate that exposes the **raw** trace.

    Unlike :class:`OpenAICompatClient` (which uses OpenAI's ``responses`` API) DeepSeek speaks the
    ``chat/completions`` API, with thinking enabled via ``extra_body`` and the chain of thought
    returned as ``message.reasoning_content`` — a *raw* trace, not Claude's summary, which is the
    measurement ``V_reason`` requires. ``usage.completion_tokens_details.reasoning_tokens`` reports
    the reasoning slice of the (output-rate-billed) completion tokens.

    Model names (verified 2026-07-23): ``deepseek-v4-pro`` / ``deepseek-v4-flash``. The older
    ``deepseek-reasoner`` / ``deepseek-chat`` aliases retire 2026-07-24, so do not use them. Serves
    no embedding endpoint — delegate embeddings to a fixed model so the instrument never varies.
    """

    def __init__(
        self,
        model: str,
        api_key: str,
        *,
        base_url: str = "https://api.deepseek.com",
        reasoning_effort: str = "high",
        thinking: bool = True,
        embed_with: LLMClient | None = None,
        ledger: Ledger | None = None,
    ) -> None:
        from openai import OpenAI

        self.model = model
        self.reasoning_effort = reasoning_effort
        self.thinking = thinking  # off for cheap V_output-only sanity (preflight); on for the probe
        self._embed_with = embed_with
        self.ledger = ledger if ledger is not None else Ledger()
        self._client = OpenAI(api_key=api_key, base_url=base_url)

    def generate(self, prompt: str, *, max_output_tokens: int) -> Completion:
        thinking = (
            {"type": "enabled", "reasoning_effort": self.reasoning_effort}
            if self.thinking
            else {"type": "disabled"}
        )
        resp = self._client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_output_tokens,
            extra_body={"thinking": thinking},
        )
        message = resp.choices[0].message
        reasoning = cast(Any, getattr(message, "reasoning_content", None))
        usage = Usage()
        if resp.usage is not None:
            details = getattr(resp.usage, "completion_tokens_details", None)
            reasoning_tokens = int(getattr(details, "reasoning_tokens", 0) or 0)
            usage = Usage(
                input=resp.usage.prompt_tokens,
                output=resp.usage.completion_tokens,
                reasoning=reasoning_tokens,
            )
        self.ledger.record(self.model, usage)
        return Completion(
            text=(message.content or "").strip(),
            usage=usage,
            reasoning=reasoning.strip() if reasoning else None,
        )

    def embed(self, texts: Sequence[str]) -> NDArray[np.float64]:
        if self._embed_with is None:
            raise RuntimeError(
                "DeepSeekClient has no embedding backend. Pass "
                "embed_with=<an OpenAICompatClient> so embeddings stay on one "
                "fixed model across generation backends."
            )
        return self._embed_with.embed(texts)


class MockClient:
    """Deterministic, network-free client for tests. Never spends money."""

    def __init__(
        self, model: str = "mock", *, dims: int = 32, with_reasoning: bool = False
    ) -> None:
        self.model = model
        self.dims = dims
        self.with_reasoning = with_reasoning
        self.ledger = Ledger()
        self.prompts: list[str] = []

    def generate(self, prompt: str, *, max_output_tokens: int) -> Completion:
        self.prompts.append(prompt)
        usage = Usage(input=len(prompt.split()), output=max_output_tokens // 4)
        self.ledger.record(self.model, usage)
        return Completion(
            text=f"mock-{abs(hash(prompt)) % 10_000}",
            usage=usage,
            reasoning=f"mock-reasoning-{abs(hash(prompt)) % 997}" if self.with_reasoning else None,
        )

    def embed(self, texts: Sequence[str]) -> NDArray[np.float64]:
        rows = []
        for t in texts:
            rng = np.random.default_rng(abs(hash(t)) % (2**32))
            v = rng.normal(size=self.dims)
            rows.append(v / np.linalg.norm(v))
        return np.asarray(rows, dtype=np.float64)
