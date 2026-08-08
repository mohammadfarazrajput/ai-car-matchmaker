"""LLM provider selection.

Constitution Principle II: the LLM is the only permitted hard dependency, and even
that has a credential-free fallback so CI and a zero-key clone still exercise the
whole graph.

    google  Google AI Studio, API key. The committed default — an evaluator pastes
            one env var and it works. Free tier is tight: ~10-15 RPM.
    vertex  Vertex AI. Real quota headroom and no training on your content, but it
            needs a GCP project, billing, and ADC — too much to ask of a judge, so
            it is never the committed default.
    groq    Free, fast, more headroom than AI Studio. Best for iteration.
    echo    Deterministic, no credentials. CI and smoke tests.

Model note: `gemini-2.5-flash` returns 404 "no longer available to new users" as of
2026-08-08, and `gemini-2.0-flash` 429s immediately on the free tier. `gemini-3.5-flash`
is verified working. Do NOT use `gemini-flash-latest` — a floating tag violates
Principle V.
"""

from __future__ import annotations

import json
import re
from typing import Any, Sequence

from langchain_core.callbacks import CallbackManagerForLLMRun
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage
from langchain_core.outputs import ChatGeneration, ChatResult

from app.config import settings


class ProviderUnavailable(RuntimeError):
    """Raised when a provider is selected but its credentials are absent."""


# --- echo --------------------------------------------------------------------

_CATEGORY_WORDS = {
    "sedan": "sedan", "saloon": "sedan", "suv": "suv", "crossover": "suv",
    "truck": "truck", "pickup": "truck", "van": "van", "minivan": "van",
    "coupe": "coupe", "convertible": "convertible", "cabriolet": "convertible",
    "hatchback": "hatchback", "hatch": "hatchback", "wagon": "wagon", "estate": "wagon",
    "sports": "sports", "sportscar": "sports", "luxury": "luxury",
    "electric": "electric", "ev": "electric", "hybrid": "hybrid",
}


class EchoChatModel(BaseChatModel):
    """A scripted stand-in, not a language model.

    Deterministic by construction so CI assertions are stable. It does enough
    real work — regex slot extraction, JSON when JSON is asked for — to exercise
    the graph end to end without credentials.
    """

    @property
    def _llm_type(self) -> str:
        return "echo"

    def bind_tools(self, tools: Sequence[Any], **kwargs: Any) -> BaseChatModel:
        """Accept a tool binding without acting on it.

        The default `BaseChatModel.bind_tools` raises `NotImplementedError`, and
        DeepAgents binds unconditionally — it injects filesystem and subagent
        tools even when the caller passes none. Without this, the zero-key path
        cannot reach the model node at all, which would defeat Principle II.

        Echo never emits tool calls: it returns text, the agent loop sees no
        tool call, and the turn ends. That is the intended CI behaviour — we are
        exercising the graph's plumbing, not its tool selection.
        """
        return self

    def _generate(
        self,
        messages: list[BaseMessage],
        stop: list[str] | None = None,
        run_manager: CallbackManagerForLLMRun | None = None,
        **kwargs: Any,
    ) -> ChatResult:
        text = ""
        for m in reversed(messages):
            if m.type == "human":
                text = str(m.content)
                break

        wants_json = any(
            "json" in str(m.content).lower() for m in messages if m.type == "system"
        )
        content = (
            json.dumps(self._extract_slots(text)) if wants_json else self._reply(text)
        )
        return ChatResult(generations=[ChatGeneration(message=AIMessage(content=content))])

    @staticmethod
    def _extract_slots(text: str) -> dict[str, Any]:
        low = text.lower()
        slots: dict[str, Any] = {}

        if re.search(r"\brent(al|ing)?\b|\bhir(e|ing)\b|\bleas(e|ing)\b", low):
            slots["intent"] = "rent"
        elif re.search(r"\bbuy(ing)?\b|\bpurchase\b|\bown\b", low):
            slots["intent"] = "buy"

        for word, category in _CATEGORY_WORDS.items():
            if re.search(rf"\b{word}\b", low):
                slots["category"] = category
                break

        money = re.search(r"[\$£€]?\s?([\d,]+)\s?(k\b)?", low)
        if money and re.search(r"budget|under|below|up to|max|[\$£€]", low):
            amount = int(money.group(1).replace(",", ""))
            slots["budget"] = amount * 1000 if money.group(2) else amount

        iso = re.search(r"\b(\d{4}-\d{2}-\d{2})\b", text)
        if iso:
            slots["target_date"] = iso.group(1)

        return slots

    @staticmethod
    def _reply(text: str) -> str:
        return (
            "[echo] Deterministic stand-in — no model was called. "
            f"Received {len(text)} characters."
        )


# --- real providers ----------------------------------------------------------


def _google() -> BaseChatModel:
    if not settings.google_api_key:
        raise ProviderUnavailable(
            "LLM_PROVIDER=google but GOOGLE_API_KEY is unset. "
            "Get one at https://aistudio.google.com/apikey, or use LLM_PROVIDER=echo."
        )
    from langchain_google_genai import ChatGoogleGenerativeAI

    return ChatGoogleGenerativeAI(
        model=settings.google_model,
        google_api_key=settings.google_api_key,
        temperature=0.3,
    )


def _vertex() -> BaseChatModel:
    """Vertex authenticates via ADC or a service-account JSON — never an API key.

    A leaked service account is materially worse than a leaked API key, so the
    credential file must stay out of the repo. `.gitignore` already excludes
    `service-account*.json` and `*-credentials.json`.
    """
    if not settings.vertex_project:
        raise ProviderUnavailable(
            "LLM_PROVIDER=vertex but VERTEX_PROJECT is unset. "
            "Vertex needs a GCP project with billing plus ADC "
            "(`gcloud auth application-default login`)."
        )
    from langchain_google_vertexai import ChatVertexAI

    return ChatVertexAI(
        model_name=settings.vertex_model,
        project=settings.vertex_project,
        location=settings.vertex_location,
        temperature=0.3,
    )


def _groq() -> BaseChatModel:
    if not settings.groq_api_key:
        raise ProviderUnavailable(
            "LLM_PROVIDER=groq but GROQ_API_KEY is unset. "
            "Get one at https://console.groq.com/keys, or use LLM_PROVIDER=echo."
        )
    from langchain_groq import ChatGroq

    return ChatGroq(
        model=settings.groq_model,
        api_key=settings.groq_api_key,
        temperature=0.3,
    )


_BUILDERS = {
    "google": _google,
    "vertex": _vertex,
    "groq": _groq,
    "echo": EchoChatModel,
}


def get_llm(provider: str | None = None) -> BaseChatModel:
    """Return the configured chat model.

    Fails loudly on a missing credential rather than silently degrading to echo —
    a demo that quietly stops using the real model is worse than one that refuses
    to start.
    """
    name = (provider or settings.llm_provider).lower()
    builder = _BUILDERS.get(name)
    if builder is None:
        raise ProviderUnavailable(
            f"unknown LLM_PROVIDER {name!r}; expected one of {sorted(_BUILDERS)}"
        )
    return builder()


def message_text(message: BaseMessage) -> str:
    """Normalise `.content` to a plain string across providers.

    Providers disagree on shape: `langchain-google-genai` 4.x returns a list of
    content blocks (`[{"type": "text", "text": "ok", ...}]`), while Groq returns a
    plain `str`. Anything calling `.strip()` or `json.loads()` on `.content`
    directly works with one provider and breaks with the other.

    **Every consumer of a model response must go through this function.**
    """
    text = getattr(message, "text", None)
    if isinstance(text, str) and text:
        return text
    if callable(text):  # older langchain-core exposed text() as a method
        try:
            result = text()
            if isinstance(result, str):
                return result
        except TypeError:
            pass

    content = message.content
    if isinstance(content, str):
        return content
    if isinstance(content, Sequence):
        return "".join(
            block.get("text", "")
            for block in content
            if isinstance(block, dict) and block.get("type") == "text"
        )
    return str(content)


def available_providers() -> dict[str, bool]:
    """Which providers could actually run right now. Surfaced by /health."""
    return {
        "google": bool(settings.google_api_key),
        "vertex": bool(settings.vertex_project),
        "groq": bool(settings.groq_api_key),
        "echo": True,
    }
