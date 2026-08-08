"""FastAPI application.

STUB STATUS (T022, T024 + WORK-SPLIT §4): the endpoint shapes, the AG-UI event
envelope and every A2UI frame are FINAL — they are the contract Agent B renders
against. The listing data and the interview script behind them are canned and get
replaced by the real agent in T023/T026/T034 without any wire change.
"""

from __future__ import annotations

import asyncio
import json
from typing import Any, AsyncIterator

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.a2ui import surfaces
from app.a2ui.emitter import to_jsonl, update_data_model
from app.config import settings
from app.stub_data import STUB_LISTINGS, STUB_PROGRESS_STEPS, listing_detail, projection

app = FastAPI(title="AI Car Matchmaker", version="0.1.0-stub")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- AG-UI event envelope ----------------------------------------------------


def sse(event_type: str, **payload: Any) -> str:
    """One Server-Sent Event. Type travels inside the JSON, AG-UI style."""
    return f"data: {json.dumps({'type': event_type, **payload}, separators=(',', ':'))}\n\n"


def a2ui_event(frame: dict[str, Any]) -> str:
    """A2UI_FRAME carries the frame as a pre-serialised single line.

    `to_jsonl` validates on the way out, so a malformed frame fails here rather
    than silently reaching the renderer.
    """
    return sse("A2UI_FRAME", frame=to_jsonl(frame))


# --- POST /agent -------------------------------------------------------------


class Message(BaseModel):
    role: str
    content: str


class A2uiAction(BaseModel):
    """Verbatim from a component's `action.event`. The frontend interprets nothing."""

    name: str
    context: dict[str, Any] = {}


class AgentRequest(BaseModel):
    session_id: str | None = None
    messages: list[Message] = []
    action: A2uiAction | None = None


# Stub session store. Replaced by the LangGraph checkpointer at T021.
_SESSIONS: dict[str, dict[str, Any]] = {}

_SLOT_FOR_ACTION = {
    "setIntent": "intent",
    "setCategory": "category",
    "setBudget": "budget",
    "setTargetDate": "target_date",
}
CORE_SLOTS = ("intent", "category", "budget", "target_date")


def _session(session_id: str) -> dict[str, Any]:
    return _SESSIONS.setdefault(
        session_id, {"intent": None, "category": None, "budget": None,
                     "target_date": None, "selected_car_id": None},
    )


async def _apply_action(session_id: str, act: A2uiAction) -> AsyncIterator[str]:
    """Apply an A2UI action and stream the consequences."""
    state = _session(session_id)

    if act.name in _SLOT_FOR_ACTION:
        slot = _SLOT_FOR_ACTION[act.name]
        state[slot] = act.context.get("value")
        path = "/interview/budget/max" if slot == "budget" else f"/interview/{slot}"
        yield a2ui_event(update_data_model("interview", path, state[slot]))
        missing = [s for s in CORE_SLOTS if state[s] is None]
        yield a2ui_event(update_data_model("interview", "/interview/missing", missing))
        yield sse("STATE_SNAPSHOT", state={"session_id": session_id, **state, "missing": missing})

        if not missing:
            async for chunk in _research_and_rank():
                yield chunk
        return

    if act.name == "proceedAnyway":
        async for chunk in _research_and_rank():
            yield chunk
        return

    if act.name in ("selectCar", "openBookingForm"):
        idx = act.context.get("index", 0)
        listing_id = act.context.get("listingId") or STUB_LISTINGS[idx]["id"]
        state["selected_car_id"] = listing_id
        detail = listing_detail(listing_id) or STUB_LISTINGS[0]
        headline = f"{detail['year']} {detail['make']} {detail['model']}"
        for frame in surfaces.checkout_launcher_surface(listing_id, headline):
            yield a2ui_event(frame)
        yield sse("STATE_SNAPSHOT", state={"session_id": session_id, **state})
        return

    if act.name in ("explainMore", "refineSearch"):
        yield sse("TEXT_MESSAGE_START", message_id="m-act")
        yield sse("TEXT_MESSAGE_CONTENT", message_id="m-act",
                  delta=f"[stub] {act.name} acknowledged; the real agent answers this at T040.")
        yield sse("TEXT_MESSAGE_END", message_id="m-act")
        return

    # A typo in a surface definition must be loud, not silent.
    yield sse("RUN_ERROR", message=f"unknown action {act.name!r}")


async def _research_and_rank() -> AsyncIterator[str]:
    for frame in surfaces.progress_surface():
        yield a2ui_event(frame)
    steps: list[dict[str, str]] = []
    for step in STUB_PROGRESS_STEPS:
        steps.append(step)
        yield a2ui_event(surfaces.progress_step(list(steps)))
        await asyncio.sleep(0.25)
    ranked = [projection(l, i) for i, l in enumerate(STUB_LISTINGS)]
    for frame in surfaces.results_surface(ranked):
        yield a2ui_event(frame)
        await asyncio.sleep(0.03)


async def _stub_run(session_id: str) -> AsyncIterator[str]:
    yield sse("RUN_STARTED", session_id=session_id)

    yield sse("TEXT_MESSAGE_START", message_id="m1")
    yield sse("TEXT_MESSAGE_CONTENT", message_id="m1",
              delta="Happy to help you find a car. A few questions first.")
    yield sse("TEXT_MESSAGE_END", message_id="m1")

    for frame in surfaces.interview_surface():
        yield a2ui_event(frame)
        await asyncio.sleep(0.05)

    yield sse("STATE_SNAPSHOT", state={
        "session_id": session_id,
        "intent": None, "category": None, "budget": None, "target_date": None,
        "missing": ["intent", "category", "budget", "target_date"],
        "ranked": [],
    })

    # Canned research + ranking so B can build the progress and results surfaces.
    for frame in surfaces.progress_surface():
        yield a2ui_event(frame)

    steps: list[dict[str, str]] = []
    for step in STUB_PROGRESS_STEPS:
        steps.append(step)
        yield a2ui_event(surfaces.progress_step(list(steps)))
        await asyncio.sleep(0.25)

    ranked = [projection(l, i) for i, l in enumerate(STUB_LISTINGS)]
    for frame in surfaces.results_surface(ranked):
        yield a2ui_event(frame)
        await asyncio.sleep(0.03)

    yield sse("RUN_FINISHED", session_id=session_id)


async def _action_run(session_id: str, act: A2uiAction) -> AsyncIterator[str]:
    yield sse("RUN_STARTED", session_id=session_id)
    async for chunk in _apply_action(session_id, act):
        yield chunk
    yield sse("RUN_FINISHED", session_id=session_id)


@app.post("/agent")
async def agent(req: AgentRequest) -> StreamingResponse:
    session_id = req.session_id or "stub-session-1"
    stream = _action_run(session_id, req.action) if req.action else _stub_run(session_id)
    return StreamingResponse(
        stream,
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


# --- Marketplace -------------------------------------------------------------


@app.get("/api/listings")
async def list_listings(limit: int = 10) -> dict[str, Any]:
    """Projections only — never full bodies, which would flood the agent context."""
    results = [projection(l, i) for i, l in enumerate(STUB_LISTINGS)][: min(limit, 50)]
    return {"count": len(STUB_LISTINGS), "results": results}


@app.get("/api/listings/{listing_id}")
async def get_listing(listing_id: str) -> dict[str, Any]:
    detail = listing_detail(listing_id)
    if detail is None:
        raise HTTPException(status_code=404, detail=f"unknown listing {listing_id}")
    return detail


# --- Health ------------------------------------------------------------------


@app.get("/health")
async def health() -> dict[str, Any]:
    return {
        "status": "ok",
        "llm_provider": settings.llm_provider,
        "listings_loaded": len(STUB_LISTINGS),
        "channels": settings.channel_modes(),
        "stub": True,
    }
