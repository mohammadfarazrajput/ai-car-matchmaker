"""A2UI surface builders.

One function per surface in contracts/a2ui-surfaces.md. These return lists of
frames; the caller streams them.

STUB STATUS: the `interview` and `results` surfaces are structurally final —
component ids, data paths and action names are the contract Agent B renders
against and will not change. Only the *values* are canned until the agent lands.
"""

from __future__ import annotations

from typing import Any

from app.models.schemas import CATEGORIES
from app.a2ui.emitter import (
    action,
    bind,
    create_surface,
    update_components,
    update_data_model,
)

# --- interview ---------------------------------------------------------------


def interview_surface() -> list[dict[str, Any]]:
    """Phase INTERVIEWING. Agent-authored: fields appear and disappear as slots fill."""
    return [
        create_surface("interview"),
        update_components(
            "interview",
            [
                {"id": "root", "component": "Column", "children": ["heading", "intent", "category", "budget", "target_date", "submit"]},
                {"id": "heading", "component": "Text", "text": "Tell me what you're looking for"},
                {
                    "id": "intent",
                    "component": "ChoicePicker",
                    "label": "Buying or renting?",
                    "variant": "mutuallyExclusive",
                    "options": [{"label": "Buy", "value": "buy"},
                                {"label": "Rent", "value": "rent"}],
                    "value": bind("/interview/intent"),
                    "action": action("setIntent"),
                },
                {
                    "id": "category",
                    "component": "ChoicePicker",
                    "label": "Type of vehicle",
                    "variant": "mutuallyExclusive",
                    "options": [{"label": c.title(), "value": c} for c in CATEGORIES],
                    "value": bind("/interview/category"),
                    "action": action("setCategory"),
                },
                {
                    "id": "budget",
                    "component": "Slider",
                    "label": "Budget ceiling",
                    "min": 5000,
                    "max": 150000,
                    # `steps` is the NUMBER OF DIVISIONS, not the increment.
                    # (150000-5000)/2500 = 58 divisions of $2,500.
                    "steps": 58,
                    "value": bind("/interview/budget/max"),
                    "action": action("setBudget"),
                },
                {
                    "id": "target_date",
                    "component": "DateTimeInput",
                    "label": "When do you need it?",
                    "enableDate": True,
                    "enableTime": False,
                    "value": bind("/interview/target_date"),
                    "action": action("setTargetDate"),
                },
                {
                    "id": "submit",
                    "component": "Button",
                    "label": "Find me options",
                    "action": action("proceedAnyway", assumption="none"),
                },
            ],
        ),
        update_data_model("interview", "/interview/intent", None),
        update_data_model("interview", "/interview/category", None),
        update_data_model("interview", "/interview/budget/max", None),
        update_data_model("interview", "/interview/target_date", None),
        update_data_model("interview", "/interview/missing",
                          ["intent", "category", "budget", "target_date"]),
    ]


# --- progress ----------------------------------------------------------------


def progress_surface() -> list[dict[str, Any]]:
    return [
        create_surface("progress"),
        update_components(
            "progress",
            [
                {"id": "root", "component": "Column", "children": ["title", "steps"]},
                {"id": "title", "component": "Text", "text": "Researching"},
                {"id": "steps", "component": "List", "items": bind("/progress/steps")},
            ],
        ),
        update_data_model("progress", "/progress/steps", []),
    ]


def progress_step(steps: list[dict[str, str]]) -> dict[str, Any]:
    """Append-and-replace: A2UI writes the whole array at the path."""
    return update_data_model("progress", "/progress/steps", steps)


# --- results -----------------------------------------------------------------


def results_surface(results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """One card per ranked listing. Card count is decided at runtime."""
    card_ids = [f"card_{i}" for i in range(len(results))]
    components: list[dict[str, Any]] = [
        {"id": "root", "component": "Column", "children": ["title", *card_ids]},
        {"id": "title", "component": "Text", "text": f"{len(results)} matches"},
    ]
    frames: list[dict[str, Any]] = [create_surface("results")]

    for i, _ in enumerate(results):
        components.append(
            {
                "id": f"card_{i}",
                "component": "Card",
                "title": bind(f"/results/{i}/headline"),
                "subtitle": bind(f"/results/{i}/price_label"),
                "imageUrl": bind(f"/results/{i}/image_url"),
                "body": bind(f"/results/{i}/reasoning"),
                "action": action("selectCar", index=i),
            }
        )

    frames.append(update_components("results", components))

    for i, r in enumerate(results):
        frames.append(update_data_model("results", f"/results/{i}/headline", r["headline"]))
        frames.append(update_data_model("results", f"/results/{i}/score", r["score"]))
        frames.append(update_data_model("results", f"/results/{i}/price_label", r["price_label"]))
        frames.append(update_data_model("results", f"/results/{i}/image_url", r["image_url"]))
        frames.append(update_data_model("results", f"/results/{i}/reasoning", r["reasoning"]))
        for component, value in r["breakdown"].items():
            frames.append(
                update_data_model("results", f"/results/{i}/breakdown/{component}", value)
            )

    return frames


# --- checkout_launcher -------------------------------------------------------


def checkout_launcher_surface(listing_id: str, headline: str) -> list[dict[str, Any]]:
    """Bridges A2UI to the MCP booking app. Deliberately holds no booking logic."""
    return [
        create_surface("checkout_launcher"),
        update_components(
            "checkout_launcher",
            [
                {"id": "root", "component": "Column", "children": ["label", "open"]},
                {"id": "label", "component": "Text", "text": f"Reserve the {headline}"},
                {
                    "id": "open",
                    "component": "Button",
                    "label": "Continue to booking",
                    "action": action("openBookingForm", listingId=listing_id),
                },
            ],
        ),
    ]
