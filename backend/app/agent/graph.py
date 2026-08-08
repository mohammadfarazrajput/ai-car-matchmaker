"""The multistep agent.

`create_deep_agent` (deepagents 0.7.5) compiles a LangGraph agent that owns the
tool loop; our job is to give it the right model, tools, prompt and state schema.

State: `CarMatchmakerState` extends `DeepAgentState` — the harness owns `messages`,
`jump_to` and `structured_response`, and our interview slots ride alongside. This
is why the slots live in the agent state rather than a side store: the model needs
to see what it has already captured in order to satisfy FR-003 (never re-ask a
filled slot).

Checkpointing is the shared `InMemorySaver` from `state.py`, keyed on `session_id`
via `thread_id`, which is what makes FR-021 hold across turns.
"""

from __future__ import annotations

from typing import Any

from deepagents import DeepAgentState, create_deep_agent
from langgraph.graph.state import CompiledStateGraph

from app.agent.state import CORE_SLOTS, build_checkpointer
from app.llm.providers import get_llm

SYSTEM_PROMPT = """\
You are a car matchmaker. You help one person decide which car to buy or rent, \
then hand them to booking. You are not a salesperson: you have no stake in which \
car they choose.

## The interview

You need exactly four things before you can research:

  intent        buying or renting
  category      the kind of vehicle
  budget        what they can spend (for rentals, the total for the period)
  target_date   when they need it

Rules that matter:

- Ask for at most two of these at a time. This is a conversation, not a form.
- If someone gives you several at once, take them all and never ask again. \
Re-asking something they already told you is the fastest way to look broken.
- Infer when the inference is obvious and then CONFIRM it rather than asking cold. \
"Weekend camping trips" plainly suggests an SUV or a truck — say which you assumed \
and let them correct you.
- If they ask to see cars before you have all four, say which one is missing, state \
the assumption you are making in its place, and proceed.

## Recommending

Use `search_cars`. It returns a score with its four components broken out. \
When you explain a recommendation:

- Cite at least one concrete figure in its favour AND at least one real trade-off \
against it. A recommendation with no downside reads as a sales pitch.
- Use the numbers you were actually given — range, charge time, 0-60, safety rating, \
five-year running costs, price. Never invent a figure.
- Never favour a manufacturer. The scorer cannot even see the make, and neither \
should your reasoning. If a cheaper car genuinely wins, say so.
- If nothing matches, say which constraint eliminated everything and offer one \
specific relaxation.

## Tone

Plain, brief, concrete. No filler, no hype, no exclamation marks. You are helping \
someone spend a lot of money; be the person who tells them the truth.

## Your tooling is invisible

You have internal tools — a scratchpad filesystem, planning helpers — that exist \
for your own working, not for the person you are talking to. NEVER mention files, \
searches of files, directories, or any internal machinery. The person asked about \
cars. If you cannot answer, say what you are missing in terms of CARS, never in \
terms of your own tools. "I couldn't find any files" is never an acceptable thing \
to say to someone buying a vehicle.
"""


class CarMatchmakerState(DeepAgentState):
    """Harness state plus our interview slots.

    Slots live here rather than in a side store so the model can see what it has
    already captured — that is what makes FR-003 achievable rather than aspirational.
    """

    session_id: str
    intent: str | None
    category: str | None
    budget_max: int | None
    target_date: str | None
    rental_days: int | None
    features: list[str]
    slot_origin: dict[str, dict[str, str]]
    phase: str
    ranked: list[dict[str, Any]]
    selected_car_id: str | None
    booking: dict[str, Any] | None
    notifications: list[dict[str, Any]]
    search_stats: dict[str, int]
    active_channel: str
    entry_channel: str


def build_agent(
    tools: list[Any] | None = None,
    provider: str | None = None,
) -> CompiledStateGraph:
    """Compile the agent.

    `tools` is injected rather than imported so tests can supply fakes and so the
    marketplace tools (T034) can land without touching this module.
    """
    return create_deep_agent(
        model=get_llm(provider),
        tools=tools or [],
        system_prompt=SYSTEM_PROMPT,
        state_schema=CarMatchmakerState,
        checkpointer=build_checkpointer(),
        name="car-matchmaker",
    )


_agent: CompiledStateGraph | None = None


def get_agent() -> CompiledStateGraph:
    """Process-wide singleton. Built lazily so importing this module never
    requires credentials — `/health` and the tests must work without them."""
    global _agent
    if _agent is None:
        _agent = build_agent()
    return _agent


def reset_agent_for_tests() -> None:
    global _agent
    _agent = None


def slot_summary(state: dict[str, Any]) -> str:
    """Compact 'what we know so far' line for the system context.

    Kept short deliberately: restating the full state every turn wastes tokens and
    invites the model to parrot it back.
    """
    known = [f"{s}={state.get(s)}" for s in CORE_SLOTS if state.get(s) is not None]
    missing = [s for s in CORE_SLOTS if state.get(s) is None]
    parts = []
    if known:
        parts.append("Known: " + ", ".join(known))
    if missing:
        parts.append("Still needed: " + ", ".join(missing))
    return " | ".join(parts) or "Nothing captured yet."
