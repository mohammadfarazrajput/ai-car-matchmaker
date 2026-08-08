"""LLM provider selection and cross-provider response normalisation.

These run without credentials — the `echo` provider exists so CI can exercise the
graph, and the normaliser is tested against synthetic messages rather than live
calls.
"""

from __future__ import annotations

import json

import pytest
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from app.llm.providers import (
    EchoChatModel,
    ProviderUnavailable,
    available_providers,
    get_llm,
    message_text,
)


# --- selection ---------------------------------------------------------------


def test_echo_needs_no_credentials() -> None:
    """Principle II: the zero-key path must reach a working model."""
    assert isinstance(get_llm("echo"), EchoChatModel)


def test_unknown_provider_is_loud() -> None:
    with pytest.raises(ProviderUnavailable, match="unknown LLM_PROVIDER"):
        get_llm("gpt5")


def test_missing_credential_refuses_rather_than_degrading(monkeypatch) -> None:
    """A demo that silently stops using the real model is worse than one that
    refuses to start."""
    from app.llm import providers

    monkeypatch.setattr(providers.settings, "google_api_key", "")
    with pytest.raises(ProviderUnavailable, match="GOOGLE_API_KEY"):
        get_llm("google")


def test_vertex_refuses_without_a_project(monkeypatch) -> None:
    from app.llm import providers

    monkeypatch.setattr(providers.settings, "vertex_project", "")
    with pytest.raises(ProviderUnavailable, match="VERTEX_PROJECT"):
        get_llm("vertex")


def test_echo_is_always_available() -> None:
    assert available_providers()["echo"] is True


# --- response normalisation --------------------------------------------------


def test_normalises_plain_string_content() -> None:
    """Groq and most providers return a plain string."""
    assert message_text(AIMessage(content="ok")) == "ok"


def test_normalises_google_content_blocks() -> None:
    """langchain-google-genai 4.x returns a list of blocks. Code calling .strip()
    or json.loads() on .content directly breaks on this provider only."""
    msg = AIMessage(content=[{"type": "text", "text": "ok", "extras": {"signature": "…"}}])
    assert message_text(msg) == "ok"


def test_concatenates_multiple_text_blocks() -> None:
    msg = AIMessage(content=[
        {"type": "text", "text": "hello "},
        {"type": "text", "text": "world"},
    ])
    assert message_text(msg) == "hello world"


def test_ignores_non_text_blocks() -> None:
    msg = AIMessage(content=[
        {"type": "thinking", "thinking": "internal"},
        {"type": "text", "text": "visible"},
    ])
    assert message_text(msg) == "visible"


# --- echo behaviour ----------------------------------------------------------


def test_echo_is_deterministic() -> None:
    """CI assertions depend on this."""
    model = EchoChatModel()
    prompt = [HumanMessage(content="buying an SUV")]
    assert message_text(model.invoke(prompt)) == message_text(model.invoke(prompt))


def test_echo_extracts_all_four_slots_from_one_message() -> None:
    """Mirrors SC-005: four inputs in a single message."""
    model = EchoChatModel()
    reply = model.invoke([
        SystemMessage(content="Reply in JSON."),
        HumanMessage(content="Renting an SUV under $900 for 2026-09-03"),
    ])
    slots = json.loads(message_text(reply))
    assert slots == {
        "intent": "rent",
        "category": "suv",
        "budget": 900,
        "target_date": "2026-09-03",
    }


@pytest.mark.parametrize(
    "text,expected",
    [
        ("I want to buy a sedan", "buy"),
        ("looking to rent something", "rent"),
        ("thinking of leasing", "rent"),
        ("just browsing", None),
    ],
)
def test_echo_intent_detection(text: str, expected: str | None) -> None:
    assert EchoChatModel._extract_slots(text).get("intent") == expected


def test_echo_handles_k_suffixed_budget() -> None:
    assert EchoChatModel._extract_slots("budget up to 65k")["budget"] == 65000


def test_echo_returns_prose_without_a_json_instruction() -> None:
    model = EchoChatModel()
    out = message_text(model.invoke([HumanMessage(content="hello")]))
    assert out.startswith("[echo]")
