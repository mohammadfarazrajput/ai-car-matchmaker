"""Agent graph assembly.

Runs on the `echo` provider — no credentials, per Principle II. These assert that
the graph compiles, carries our state, and persists across turns; they do not
assert model quality, which is the eval set's job (T095).
"""

from __future__ import annotations

import pytest
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool

from app.agent.graph import SYSTEM_PROMPT, build_agent, reset_agent_for_tests, slot_summary
from app.agent.state import thread_config


@pytest.fixture(autouse=True)
def _reset() -> None:
    reset_agent_for_tests()


@tool
def _fake_search(category: str) -> str:
    """Search cars."""
    return "[]"


def test_graph_compiles_without_credentials() -> None:
    """Principle II: the zero-key path must reach a working agent."""
    agent = build_agent(provider="echo")
    assert "model" in agent.get_graph().nodes


def test_graph_accepts_domain_tools() -> None:
    agent = build_agent(tools=[_fake_search], provider="echo")
    assert "tools" in agent.get_graph().nodes


def test_agent_runs_a_turn_on_echo() -> None:
    """DeepAgents binds tools unconditionally, so EchoChatModel must implement
    bind_tools or the zero-key path cannot reach the model node at all."""
    agent = build_agent(provider="echo")
    out = agent.invoke(
        {"messages": [HumanMessage(content="hello")], "session_id": "t"},
        thread_config("t-run"),
    )
    assert len(out["messages"]) == 2


def test_state_accumulates_across_turns(monkeypatch) -> None:
    """FR-021 — the checkpointer keyed on session_id is what makes multistep
    memory real rather than claimed."""
    agent = build_agent(provider="echo")
    cfg = thread_config("t-multi")
    agent.invoke({"messages": [HumanMessage(content="one")], "session_id": "s"}, cfg)
    out = agent.invoke({"messages": [HumanMessage(content="two")]}, cfg)
    assert len(out["messages"]) == 4
    assert out["session_id"] == "s"


def test_sessions_are_isolated() -> None:
    agent = build_agent(provider="echo")
    agent.invoke({"messages": [HumanMessage(content="a")], "session_id": "A"}, thread_config("A"))
    out = agent.invoke({"messages": [HumanMessage(content="b")], "session_id": "B"}, thread_config("B"))
    assert len(out["messages"]) == 2  # B did not inherit A's history


# --- the system prompt carries the graded constraints ------------------------


def test_prompt_forbids_re_asking_a_captured_slot() -> None:
    """FR-003 / SC-005."""
    assert "never ask again" in SYSTEM_PROMPT.lower()


def test_prompt_requires_a_trade_off_in_every_recommendation() -> None:
    """FR-011 — a recommendation with no downside reads as a sales pitch."""
    low = SYSTEM_PROMPT.lower()
    assert "trade-off" in low and "in its favour" in low


def test_prompt_forbids_brand_preference() -> None:
    """Principle III (NON-NEGOTIABLE). Structural neutrality lives in the scorer;
    this stops the narrative reintroducing what the scorer excluded."""
    assert "never favour a manufacturer" in SYSTEM_PROMPT.lower()


def test_prompt_forbids_inventing_figures() -> None:
    assert "never invent a figure" in SYSTEM_PROMPT.lower()


def test_prompt_hides_internal_tooling() -> None:
    """DeepAgents injects filesystem and planning tools. Without this the model
    tells car buyers it 'could not find any files' — observed on groq before the
    guard was added."""
    low = SYSTEM_PROMPT.lower()
    assert "never mention files" in low


# --- slot summary ------------------------------------------------------------


def test_slot_summary_reports_known_and_missing() -> None:
    out = slot_summary({"intent": "rent", "category": "suv"})
    assert "intent=rent" in out
    assert "budget_max" in out and "target_date" in out


def test_slot_summary_handles_an_empty_state() -> None:
    assert "Still needed" in slot_summary({})
