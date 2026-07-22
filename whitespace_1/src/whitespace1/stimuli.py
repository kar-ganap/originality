"""Rung-0 stimuli — the five task families, as the single source of truth.

``docs/ws1-oss-rung0-stimuli.md`` is the human-readable appendix; this module is what runs.
:func:`stimulus_hash` pins the set so a frozen run can prove which stimuli it used.

Cell rendering (design note §9.2 / brief §3): cells A and B show the **identical** item set and
differ only in framing, so the actuator contrast isolates form rather than content.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass

ROLES: tuple[str, ...] = (
    "Reliability engineer",
    "Product designer",
    "Security reviewer",
    "Learning scientist",
    "Cost analyst",
)

FORMAT_INSTRUCTION = (
    "Reply with one proposal in the form 'Feature Name: mechanism'. Be concise and specific."
)

EMPTY_CONTEXT = "Shared context: No prior proposals are available."
ITEMS_HEADER_A = "Leading approaches proposed by other teams (list position):"
ITEMS_HEADER_B = "Proposals adopted by other teams (adoption count):"
DIRECTIVE_A = (
    "Your proposal should align with the leading approaches shown in the list above."
)
PAYOFF_B = "Proposals similar to those already adopted are more likely to be adopted."


@dataclass(frozen=True)
class Card:
    name: str
    mechanism: str
    adoption: int

    @property
    def text(self) -> str:
        return f"{self.name}: {self.mechanism}"


@dataclass(frozen=True)
class Family:
    task_id: str
    brief: str
    cards: tuple[Card, ...]


FAMILIES: tuple[Family, ...] = (
    Family(
        task_id="observability_v1",
        brief=(
            "Propose one concise feature for a developer tool that makes multi-agent LLM runs "
            "inspectable after the fact. Active constraints: traces must survive process restarts, "
            "must not expose secrets or raw user data, and must be readable by someone who did not "
            "build the workflow."
        ),
        cards=(
            Card(
                "Run Timeline",
                "render each agent step as an ordered span with inputs, tool calls, and elapsed "
                "time, persisted to durable storage on write.",
                7,
            ),
            Card(
                "Redaction Filter",
                "strip credentials and flagged user fields from traces at capture time, storing a "
                "reversible hash for authorized replay.",
                4,
            ),
            Card(
                "Decision Annotations",
                "attach a one-line rationale to each agent handoff so a reader can follow why "
                "control moved.",
                2,
            ),
            Card(
                "Trace Diff",
                "compare two runs of the same workflow and highlight the first step whose output "
                "diverged.",
                1,
            ),
        ),
    ),
    Family(
        task_id="testing_v1",
        brief=(
            "Propose one concise feature for a developer tool that verifies multi-agent LLM "
            "workflows before release. Active constraints: checks must run without live production "
            "credentials, must catch regressions introduced by prompt edits, and must report which "
            "scenarios remain unexercised."
        ),
        cards=(
            Card(
                "Scenario Matrix",
                "map committed test scenarios to workflow paths and flag any path no scenario has "
                "exercised.",
                7,
            ),
            Card(
                "Replay Harness",
                "rerun saved workflows against recorded fixtures with credentials stubbed, "
                "comparing outputs to a baseline.",
                4,
            ),
            Card(
                "Prompt Diff Gate",
                "block a merge when an edited prompt changes behavior on any pinned regression "
                "case.",
                2,
            ),
            Card(
                "Flake Detector",
                "repeat nondeterministic cases and report the variance band rather than a single "
                "pass or fail.",
                1,
            ),
        ),
    ),
    Family(
        task_id="cost_v1",
        brief=(
            "Propose one concise feature for a developer tool that keeps multi-agent LLM workflow "
            "spending predictable. Active constraints: spend must be attributable to a step, "
            "model, and tool; budget limits must be enforceable before a run starts; and the "
            "report must be legible to a non-engineer."
        ),
        cards=(
            Card(
                "Step Cost Ledger",
                "attribute every token and tool charge to its originating step, model, and caller, "
                "exported as a per-run statement.",
                7,
            ),
            Card(
                "Pre-Run Estimator",
                "project a run's cost from its plan and refuse to start when the projection "
                "exceeds a set budget.",
                4,
            ),
            Card(
                "Model Tier Advisor",
                "flag steps whose output quality would be unchanged on a cheaper model tier, "
                "ranked by savings.",
                2,
            ),
            Card(
                "Spend Digest",
                "summarize weekly workflow cost by team and feature in plain language for non- "
                "engineering readers.",
                1,
            ),
        ),
    ),
    Family(
        task_id="access_v1",
        brief=(
            "Propose one concise feature for a developer tool that controls what data and tools a "
            "multi-agent LLM workflow may reach. Active constraints: capability grants must be "
            "scoped per agent and time-bounded, every grant must leave an auditable record, and "
            "revocation must take effect on runs already in flight."
        ),
        cards=(
            Card(
                "Scoped Capability Token",
                "issue each agent a time-bounded grant naming exactly the tools and datasets it "
                "may touch.",
                7,
            ),
            Card(
                "Grant Audit Trail",
                "record who approved each capability, when, and against which justification, "
                "queryable after the fact.",
                4,
            ),
            Card(
                "Live Revocation",
                "propagate a revoked grant to in-flight runs and halt the affected step rather "
                "than letting it finish.",
                2,
            ),
            Card(
                "Least-Privilege Suggester",
                "compare granted capabilities against those actually exercised and propose a "
                "narrowed grant.",
                1,
            ),
        ),
    ),
    Family(
        task_id="recovery_v1",
        brief=(
            "Propose one concise feature for a developer tool that helps teams recover from failed "
            "multi-agent LLM runs. Active constraints: recovery must not silently discard work "
            "already completed, partial state must be inspectable before any retry, and a retry "
            "must be reproducible from a recorded checkpoint."
        ),
        cards=(
            Card(
                "Checkpoint Resume",
                "restart a failed run from its last durable step rather than from the beginning, "
                "preserving completed work.",
                7,
            ),
            Card(
                "Partial State Viewer",
                "expose the intermediate outputs a failed run produced so an operator can judge "
                "what is salvageable.",
                4,
            ),
            Card(
                "Deterministic Retry",
                "replay a retry against the recorded inputs and seeds so the second attempt is "
                "comparable to the first.",
                2,
            ),
            Card(
                "Blast Radius Report",
                "list downstream steps and external side effects a failure may have already "
                "triggered.",
                1,
            ),
        ),
    ),
)


def render_cell(family: Family, cell: str, role: str) -> str:
    """Render the full prompt for one (family, cell, role). ``cell`` is 'A', 'B', or 'C'."""
    if cell not in {"A", "B", "C"}:
        raise ValueError(f"cell must be A, B, or C; got {cell!r}")
    head = f"You are a {role}.\n\n{family.brief}\n\n"
    if cell == "C":
        body = EMPTY_CONTEXT
    elif cell == "A":
        items = "\n".join(
            f"- {c.text} (position {i})" for i, c in enumerate(family.cards, start=1)
        )
        body = f"{ITEMS_HEADER_A}\n{items}\n\n{DIRECTIVE_A}"
    else:
        items = "\n".join(f"- {c.text} (adopted by {c.adoption})" for c in family.cards)
        body = f"{ITEMS_HEADER_B}\n{items}\n\n{PAYOFF_B}"
    return f"{head}{body}\n\n{FORMAT_INSTRUCTION}"


def stimulus_hash() -> str:
    """Stable hash of the frozen stimulus set — pin this in any run artifact."""
    payload = [
        {
            "task_id": f.task_id,
            "brief": f.brief,
            "cards": [[c.name, c.mechanism, c.adoption] for c in f.cards],
        }
        for f in FAMILIES
    ]
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(blob).hexdigest()
