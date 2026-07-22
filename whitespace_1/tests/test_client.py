"""Client seam tests — all network-free."""

from __future__ import annotations

import numpy as np
import pytest

from whitespace1.client import Completion, Ledger, LLMClient, MockClient, Usage


def test_mock_satisfies_the_protocol() -> None:
    client: LLMClient = MockClient()
    out = client.generate("hello", max_output_tokens=120)
    assert isinstance(out, Completion)
    assert out.text
    assert client.embed(["a", "b"]).shape == (2, 32)


def test_usage_adds() -> None:
    assert Usage(1, 2, 3, 4) + Usage(10, 20, 30, 40) == Usage(11, 22, 33, 44)


def test_embeddings_are_deterministic_and_distinct() -> None:
    c = MockClient()
    assert np.allclose(c.embed(["x"]), c.embed(["x"]))
    assert not np.allclose(c.embed(["x"]), c.embed(["y"]))


def test_ledger_totals_and_costs() -> None:
    ledger = Ledger()
    ledger.record("gpt-5.6-sol", Usage(input=1_000_000, output=1_000_000))
    assert ledger.total.input == 1_000_000
    assert ledger.cost_usd() == pytest.approx(35.0)  # $5 in + $30 out per 1M


def test_ledger_separates_models() -> None:
    ledger = Ledger()
    ledger.record("gpt-5.6-sol", Usage(output=1_000_000))
    ledger.record("claude-opus-4-8", Usage(output=1_000_000))
    assert ledger.cost_usd() == pytest.approx(55.0)  # $30 + $25
    assert set(ledger.by_model) == {"gpt-5.6-sol", "claude-opus-4-8"}


def test_rung0_budget_is_within_the_registered_estimate() -> None:
    """750 calls at measured R7C-A rates must land near the ~$2.80 registered figure."""
    ledger = Ledger()
    ledger.record("gpt-5.6-sol", Usage(input=750 * 250, output=750 * 80))
    assert ledger.cost_usd() < 3.00


def test_reasoning_absent_by_default_present_when_enabled() -> None:
    assert MockClient().generate("p", max_output_tokens=10).reasoning is None
    assert MockClient(with_reasoning=True).generate("p", max_output_tokens=10).reasoning is not None


def test_mock_records_prompts_for_assertion() -> None:
    c = MockClient()
    c.generate("first", max_output_tokens=10)
    c.generate("second", max_output_tokens=10)
    assert c.prompts == ["first", "second"]


def test_anthropic_client_refuses_to_embed_without_a_backend() -> None:
    """Embeddings must stay on one fixed model across generation backends."""
    from whitespace1.client import AnthropicClient

    client = AnthropicClient.__new__(AnthropicClient)  # no network, no SDK import
    client._embed_with = None  # type: ignore[attr-defined]
    with pytest.raises(RuntimeError, match="no embedding backend"):
        client.embed(["a"])
