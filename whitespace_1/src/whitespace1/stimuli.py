"""Rung-0 stimuli — the five task families, as the single source of truth.

``docs/ws1-oss-rung0-stimuli.md`` is the human-readable appendix; this module is what runs.
:func:`stimulus_hash` pins the set so a frozen run can prove which stimuli it used.

Cell rendering (design note §9.2 / brief §3): cells A and B show the **identical** item set and
differ only in framing, so the actuator contrast isolates form rather than content.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Sequence
from dataclasses import dataclass


@dataclass(frozen=True)
class Role:
    """A fixed viewpoint. Form matches prior work: a bare job title is a far weaker diversity
    signal than name + viewpoint, and the ceiling calibration was measured with the latter."""

    name: str
    viewpoint: str

    @property
    def descriptor(self) -> str:
        return f"{self.name}: {self.viewpoint}"


ROLES: tuple[Role, ...] = (
    Role("Reliability engineer", "Failure modes, observability, rollback paths, and operations."),
    Role("Product designer", "User workflows, affordances, trust, and interaction friction."),
    Role("Security reviewer", "Misuse, privacy boundaries, access control, and auditability."),
    Role("Learning scientist", "Explanation, feedback loops, and durable understanding."),
    Role("Cost analyst", "Token budget, latency, throughput, and deployment constraints."),
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
            "Propose one concise feature for a developer tool that helps teams inspect and "
            "understand what actually happened during a multi-agent LLM run."
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
            "Propose one concise feature for a developer tool that helps teams build confidence "
            "in a multi-agent LLM workflow before they ship it."
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
        task_id="collaboration_v1",
        brief=(
            "Propose one concise feature for a developer tool that helps several people work "
            "together on the same multi-agent LLM workflow."
        ),
        cards=(
            Card(
                "Workflow Branching",
                "let each person develop a variant of the same workflow in isolation and merge "
                "changes deliberately.",
                7,
            ),
            Card(
                "Change Review",
                "require a second person to approve edits to agent prompts and tool wiring before "
                "they land.",
                4,
            ),
            Card(
                "Ownership Map",
                "record who is responsible for each agent, prompt, and tool so questions reach "
                "the right person.",
                2,
            ),
            Card(
                "Shared Scratchpad",
                "capture in-progress notes and open questions alongside the workflow so context "
                "survives between people.",
                1,
            ),
        ),
    ),
    Family(
        task_id="access_v1",
        brief=(
            "Propose one concise feature for a developer tool that helps teams decide and enforce "
            "what a multi-agent LLM workflow is allowed to do."
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
        task_id="iteration_v1",
        brief=(
            "Propose one concise feature for a developer tool that helps teams learn from how "
            "their multi-agent LLM workflows behave in production."
        ),
        cards=(
            Card(
                "Behavior Trends",
                "chart how a workflow's outputs and failure patterns shift across releases so "
                "drift becomes visible.",
                7,
            ),
            Card(
                "Production Sampler",
                "collect a representative sample of real runs and surface the ones most worth "
                "examining closely.",
                4,
            ),
            Card(
                "Change Impact",
                "link each workflow edit to the behavior shift that followed it in production.",
                2,
            ),
            Card(
                "Hypothesis Log",
                "record what a team expected from a change and whether the observed behavior "
                "matched.",
                1,
            ),
        ),
    ),
)


def render_cell(
    family: Family, cell: str, role: Role, *, order: Sequence[int] | None = None
) -> str:
    """Render the full prompt for one (family, cell, role). ``cell`` is 'A', 'B', or 'C'.

    ``order`` is the block's committed item permutation (see :mod:`whitespace1.schedule`). Cells A
    and B in the same block MUST receive the same ``order`` — the contrast isolates the
    annotation's meaning, not the ordering. Cell A's ``(position N)`` is the **display** position,
    which is only neutral because the order is shuffled per block.
    """
    if cell not in {"A", "B", "C"}:
        raise ValueError(f"cell must be A, B, or C; got {cell!r}")
    idx = tuple(range(len(family.cards))) if order is None else tuple(order)
    if sorted(idx) != list(range(len(family.cards))):
        raise ValueError(f"order must be a permutation of card indices; got {order!r}")
    cards = [family.cards[i] for i in idx]

    head = f"You are a {role.descriptor}\n\n{family.brief}\n\n"
    if cell == "C":
        body = EMPTY_CONTEXT
    elif cell == "A":
        items = "\n".join(f"- {c.text} (position {i})" for i, c in enumerate(cards, start=1))
        body = f"{ITEMS_HEADER_A}\n{items}\n\n{DIRECTIVE_A}"
    else:
        items = "\n".join(f"- {c.text} (adopted by {c.adoption})" for c in cards)
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
