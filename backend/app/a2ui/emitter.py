"""A2UI v1.0 frame emission.

Constitution Principle I (NON-NEGOTIABLE): this module is the single place A2UI
frames are constructed, so protocol fidelity is enforceable in one file.

The wire format is newline-delimited JSON. Every message carries `version` plus
EXACTLY ONE of:

    createSurface | updateComponents | updateDataModel | deleteSurface

Components are a FLAT list of objects with `id`; hierarchy is expressed by
`children` holding ID references, never by nesting. Data binds via
`{"path": "/json/pointer"}`. Interactions declare `action.event.name` plus a
`context` object.

Explicitly NOT the format: `{"protocol": "A2UI/1.0", "action": "RENDER_COMPONENT",
"component": {..., "props": {...}}}`. No such fields exist in any published
version of A2UI. See specs/001-ai-car-matchmaker/research.md R2.

Reference: https://a2ui.org/specification/v1.0-a2ui/
"""

from __future__ import annotations

import json
from typing import Any, Literal

A2UI_VERSION = "v1.0"
"""Pinned. MUST match the version the frontend renderer implements."""

BASIC_CATALOG = "https://a2ui.org/specification/v1_0/catalogs/basic/catalog.json"

MESSAGE_KEYS: frozenset[str] = frozenset(
    {"createSurface", "updateComponents", "updateDataModel", "deleteSurface"}
)

SurfaceId = Literal["interview", "progress", "results", "checkout_launcher"]


class A2uiProtocolError(ValueError):
    """Raised when a frame would violate the wire format."""


def _frame(key: str, body: dict[str, Any]) -> dict[str, Any]:
    if key not in MESSAGE_KEYS:
        raise A2uiProtocolError(f"{key!r} is not an A2UI message key: {sorted(MESSAGE_KEYS)}")
    return {"version": A2UI_VERSION, key: body}


# --- Frame constructors ------------------------------------------------------


def create_surface(surface_id: str, catalog_id: str = BASIC_CATALOG) -> dict[str, Any]:
    return _frame("createSurface", {"surfaceId": surface_id, "catalogId": catalog_id})


def update_components(surface_id: str, components: list[dict[str, Any]]) -> dict[str, Any]:
    for c in components:
        if "id" not in c or "component" not in c:
            raise A2uiProtocolError(f"component needs 'id' and 'component': {c!r}")
        if "props" in c:
            raise A2uiProtocolError(
                f"component {c['id']!r} has a 'props' object — A2UI puts attributes at the "
                "top level of the component. 'props' is the fabricated format."
            )
    return _frame("updateComponents", {"surfaceId": surface_id, "components": components})


def update_data_model(surface_id: str, path: str, value: Any) -> dict[str, Any]:
    if not path.startswith("/"):
        raise A2uiProtocolError(f"data path must be a JSON Pointer starting with '/': {path!r}")
    return _frame("updateDataModel", {"surfaceId": surface_id, "path": path, "value": value})


def delete_surface(surface_id: str) -> dict[str, Any]:
    return _frame("deleteSurface", {"surfaceId": surface_id})


# --- Component helpers -------------------------------------------------------


def bind(path: str) -> dict[str, str]:
    """Data binding: {"path": "/json/pointer"}."""
    if not path.startswith("/"):
        raise A2uiProtocolError(f"binding path must start with '/': {path!r}")
    return {"path": path}


def action(name: str, **context: Any) -> dict[str, Any]:
    """Interaction: action.event.{name,context}, returned to the agent on activation."""
    return {"event": {"name": name, "context": context}}


# --- Serialisation -----------------------------------------------------------


def to_jsonl(frame: dict[str, Any]) -> str:
    """Serialise one frame to a single line.

    `separators` removes incidental whitespace; renderers parse line-by-line and
    a pretty-printed stream breaks progressive rendering.
    """
    validate(frame)
    return json.dumps(frame, separators=(",", ":"), ensure_ascii=False)


def validate(frame: dict[str, Any]) -> None:
    """Assert a frame conforms. Used by emission and by the contract tests."""
    if frame.get("version") != A2UI_VERSION:
        raise A2uiProtocolError(f"expected version {A2UI_VERSION!r}, got {frame.get('version')!r}")

    present = MESSAGE_KEYS & frame.keys()
    if len(present) != 1:
        raise A2uiProtocolError(
            f"frame must carry exactly one of {sorted(MESSAGE_KEYS)}; found {sorted(present)}"
        )

    for forbidden in ("protocol", "action", "component"):
        if forbidden in frame:
            raise A2uiProtocolError(
                f"top-level {forbidden!r} is not A2UI — that is the fabricated "
                "'RENDER_COMPONENT' shape. See research.md R2."
            )

    if frame.keys() - {"version"} - MESSAGE_KEYS:
        raise A2uiProtocolError(f"unexpected top-level keys: {sorted(frame.keys())}")
