"""Per-session state and its checkpointer.

FR-021 requires state to survive across interview, research and recommendation.
FR-023 requires a session to be resumable from a single-use, time-limited link.

The graph's working state is a TypedDict (LangGraph merges channel updates, which
needs a mapping), while the durable record is the Pydantic `Session` from
`models.schemas` — validated, and the thing every other layer reads. `to_session`
and `from_session` convert between them.

Storage is in-memory per spec Assumptions; swapping the checkpointer backend is a
one-line change in `build_checkpointer`.
"""

from __future__ import annotations

import hashlib
import hmac
import secrets
from datetime import date, datetime, timedelta, timezone
from typing import Annotated, Any, TypedDict

from langchain_core.messages import BaseMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph.message import add_messages

from app.config import settings
from app.models.schemas import (
    Booking,
    BudgetRange,
    ChannelStamp,
    Contact,
    DeliveryReceipt,
    RankedResult,
    ResumeToken,
    Session,
)


class GraphState(TypedDict, total=False):
    """The graph's working state.

    Deliberately flat and small. The legacy pattern of one enormous state object
    carrying every subgraph's channels is what made earlier agent codebases
    unmaintainable; everything here is either an interview slot, a result, or
    plumbing.
    """

    session_id: str
    messages: Annotated[list[BaseMessage], add_messages]

    # interview slots
    intent: str | None
    category: str | None
    budget_max: int | None
    target_date: str | None       # ISO; graph state stays JSON-serialisable
    rental_days: int | None
    features: list[str]

    # provenance — which channel filled each slot (FR-022)
    slot_origin: dict[str, dict[str, str]]

    # downstream
    phase: str
    ranked: list[dict[str, Any]]
    selected_car_id: str | None
    booking: dict[str, Any] | None
    notifications: list[dict[str, Any]]

    # last research run, for the progress surface
    search_stats: dict[str, int]

    active_channel: str
    entry_channel: str


CORE_SLOTS: tuple[str, ...] = ("intent", "category", "budget_max", "target_date")

# Graph slot name -> Session field name. They differ for budget because the graph
# keeps a scalar while Session carries a BudgetRange.
_SLOT_TO_FIELD = {
    "intent": "intent",
    "category": "category",
    "budget_max": "budget",
    "target_date": "target_date",
}


def new_state(session_id: str, channel: str = "web") -> GraphState:
    return GraphState(
        session_id=session_id,
        messages=[],
        intent=None,
        category=None,
        budget_max=None,
        target_date=None,
        rental_days=None,
        features=[],
        slot_origin={},
        phase="INTERVIEWING",
        ranked=[],
        selected_car_id=None,
        booking=None,
        notifications=[],
        search_stats={},
        active_channel=channel,
        entry_channel=channel,
    )


def missing_slots(state: GraphState) -> list[str]:
    """Drives FR-005 and the `/interview/missing` data path."""
    return [s for s in CORE_SLOTS if state.get(s) is None]


def interview_complete(state: GraphState) -> bool:
    return not missing_slots(state)


def record_slot(state: GraphState, slot: str, value: Any, channel: str) -> GraphState:
    """Set a slot and stamp its provenance (FR-022).

    Revising a slot after ranking clears the results and returns to RESEARCHING
    (FR-004) — stale recommendations must never outlive the inputs that produced
    them. A confirmed booking is immutable.
    """
    if state.get("phase") == "CONFIRMED":
        raise ValueError("cannot revise inputs after a booking is confirmed")

    changed = state.get(slot) != value
    state[slot] = value
    origin = dict(state.get("slot_origin") or {})
    origin[slot] = {"channel": channel, "at": datetime.now(timezone.utc).isoformat()}
    state["slot_origin"] = origin

    if changed and state.get("ranked"):
        state["ranked"] = []
        state["selected_car_id"] = None
        state["phase"] = "RESEARCHING"
    return state


# --- conversion --------------------------------------------------------------


def to_session(state: GraphState) -> Session:
    """Validated view for every layer outside the graph."""
    budget = state.get("budget_max")
    target = state.get("target_date")
    return Session(
        session_id=state["session_id"],
        phase=state.get("phase", "INTERVIEWING"),  # type: ignore[arg-type]
        intent=state.get("intent"),  # type: ignore[arg-type]
        category=state.get("category"),  # type: ignore[arg-type]
        budget=BudgetRange(max=budget) if budget is not None else None,
        target_date=date.fromisoformat(target) if target else None,
        rental_days=state.get("rental_days"),
        features=list(state.get("features") or []),
        contact=Contact(**state["contact"]) if state.get("contact") else None,  # type: ignore[typeddict-item]
        slot_origin={
            k: ChannelStamp(channel=v["channel"], at=datetime.fromisoformat(v["at"]))
            for k, v in (state.get("slot_origin") or {}).items()
        },
        ranked=[RankedResult.model_validate(r) for r in state.get("ranked") or []],
        selected_car_id=state.get("selected_car_id"),
        booking=Booking.model_validate(state["booking"]) if state.get("booking") else None,
        notifications=[
            DeliveryReceipt.model_validate(n) for n in state.get("notifications") or []
        ],
        entry_channel=state.get("entry_channel", "web"),
        active_channel=state.get("active_channel", "web"),
    )


def from_session(session: Session) -> GraphState:
    return GraphState(
        session_id=session.session_id,
        messages=[],
        intent=session.intent,
        category=session.category,
        budget_max=session.budget.max if session.budget else None,
        target_date=session.target_date.isoformat() if session.target_date else None,
        rental_days=session.rental_days,
        features=list(session.features),
        slot_origin={
            k: {"channel": v.channel, "at": v.at.isoformat()}
            for k, v in session.slot_origin.items()
        },
        phase=session.phase,
        ranked=[r.model_dump() for r in session.ranked],
        selected_car_id=session.selected_car_id,
        booking=session.booking.model_dump(mode="json") if session.booking else None,
        notifications=[n.model_dump(mode="json") for n in session.notifications],
        search_stats={},
        active_channel=session.active_channel,
        entry_channel=session.entry_channel,
    )


def client_snapshot(state: GraphState) -> dict[str, Any]:
    """The STATE_SNAPSHOT payload. Excludes `slot_origin` internals and messages."""
    return {
        "session_id": state["session_id"],
        "phase": state.get("phase"),
        "intent": state.get("intent"),
        "category": state.get("category"),
        "budget": state.get("budget_max"),
        "target_date": state.get("target_date"),
        "missing": missing_slots(state),
        "ranked": state.get("ranked") or [],
        "selected_car_id": state.get("selected_car_id"),
    }


# --- checkpointer ------------------------------------------------------------

_checkpointer: InMemorySaver | None = None


def build_checkpointer() -> InMemorySaver:
    """Process-lifetime checkpointer, keyed by `session_id` via thread_id.

    Durable storage is out of scope per spec Assumptions. Swapping to Sqlite or
    Postgres is a change to this function alone.
    """
    global _checkpointer
    if _checkpointer is None:
        _checkpointer = InMemorySaver()
    return _checkpointer


def thread_config(session_id: str) -> dict[str, Any]:
    """LangGraph addresses a conversation by `thread_id`; ours is the session id."""
    return {"configurable": {"thread_id": session_id}}


# --- resume tokens (FR-023) --------------------------------------------------

_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"  # no I/O/0/1 — these get read aloud
_TOKENS: dict[str, ResumeToken] = {}


class ResumeTokenError(Exception):
    """Carries a reason so the caller can explain rather than 404."""

    def __init__(self, reason: str, message: str) -> None:
        super().__init__(message)
        self.reason = reason


def _sign(code: str) -> str:
    return hmac.new(settings.session_secret.encode(), code.encode(), hashlib.sha256).hexdigest()[:16]


def issue_resume_token(session_id: str) -> ResumeToken:
    """Single-use, one hour. A capability URL, not authentication.

    Authentication is out of scope per the spec, so this grants access to one
    session and nothing else — which is the correct shape for that constraint.
    """
    code = "".join(secrets.choice(_ALPHABET) for _ in range(5))
    token = ResumeToken(
        code=code,
        session_id=session_id,
        expires_at=datetime.now(timezone.utc) + timedelta(seconds=settings.resume_token_ttl_s),
        used=False,
    )
    _TOKENS[code] = token
    return token


def redeem_resume_token(code: str) -> str:
    """Return the session id, or raise with a reason the caller can explain."""
    token = _TOKENS.get(code.upper())
    if token is None:
        raise ResumeTokenError("unknown", "That link isn't valid.")
    if token.used:
        raise ResumeTokenError("used", "That link has already been used.")
    if datetime.now(timezone.utc) > token.expires_at:
        raise ResumeTokenError("expired", "That link has expired.")
    token.used = True
    return token.session_id


def reset_tokens_for_tests() -> None:
    _TOKENS.clear()
