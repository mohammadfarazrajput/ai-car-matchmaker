"""Canned data for the contract stub.

TEMPORARY — deleted at T034 once the real marketplace and ranker land. The shapes
here match data-model.md so the swap is invisible to the frontend.

Note the ordering: the top match is a Tesla, not a BMW. The stub deliberately does
not rehearse a BMW-first result, because Principle III forbids the real ranker
from producing one by preference, and a stub that implies otherwise sets a wrong
expectation for the demo.
"""

from __future__ import annotations

from typing import Any

STUB_PROGRESS_STEPS: list[dict[str, str]] = [
    {"label": "Searching the marketplace", "detail": "180 listings"},
    {"label": "Filtered by category and budget", "detail": "31 remain"},
    {"label": "Checked availability", "detail": "12 free on 3 September"},
    {"label": "Ranking", "detail": "4 criteria"},
]

STUB_LISTINGS: list[dict[str, Any]] = [
    {
        "id": "l-014",
        "make": "Tesla", "model": "Model Y Long Range", "year": 2024,
        "category": "suv", "tags": ["electric"],
        "price": {"currency": "USD", "buy": 48990, "rent_per_day": 95},
        "score": 0.93,
        "breakdown": {"budget": 0.96, "category": 1.0, "features": 0.80, "date": 1.0},
        "reasoning": (
            "337 mi of range and a 27-minute 10-80% charge lead this shortlist, and at "
            "$48,990 it sits well inside your ceiling. You give up interior finish "
            "against the German cars and its 5-year depreciation is the steepest here "
            "at about $24,100."
        ),
        "image_url": "https://placehold.co/640x360?text=Model+Y",
        "seats": 5, "fuel_type": "electric", "transmission": "automatic",
        "ev": {"range_mi": 337, "battery_kwh": 78.1, "dc_peak_kw": 250, "ten_to_eighty_min": 27},
        "safety": {"nhtsa_stars": 5, "iihs": "Top Safety Pick+"},
        "tco_5yr": {"fuel_or_charging": 3900, "insurance": 9200,
                    "maintenance": 2400, "depreciation": 24100},
    },
    {
        "id": "l-041",
        "make": "BMW", "model": "i4 eDrive40", "year": 2024,
        "category": "sedan", "tags": ["electric", "luxury"],
        "price": {"currency": "USD", "buy": 67300, "rent_per_day": 129},
        "score": 0.91,
        "breakdown": {"budget": 0.88, "category": 1.0, "features": 0.75, "date": 1.0},
        "reasoning": (
            "285 mi of range with a 31-minute 10-80% charge, and the best-judged chassis "
            "of the group. It costs $18,310 more than the Model Y and charges more slowly, "
            "but holds value far better — about $19,400 of 5-year depreciation against "
            "$24,100."
        ),
        "image_url": "https://placehold.co/640x360?text=i4+eDrive40",
        "seats": 5, "fuel_type": "electric", "transmission": "automatic",
        "ev": {"range_mi": 285, "battery_kwh": 81.5, "dc_peak_kw": 195, "ten_to_eighty_min": 31},
        "safety": {"nhtsa_stars": 5, "iihs": "Top Safety Pick+"},
        "tco_5yr": {"fuel_or_charging": 4200, "insurance": 9800,
                    "maintenance": 3100, "depreciation": 19400},
    },
    {
        "id": "l-077",
        "make": "Hyundai", "model": "IONIQ 5 SEL", "year": 2024,
        "category": "suv", "tags": ["electric"],
        "price": {"currency": "USD", "buy": 46100, "rent_per_day": 88},
        "score": 0.87,
        "breakdown": {"budget": 1.0, "category": 1.0, "features": 0.60, "date": 1.0},
        "reasoning": (
            "The fastest charger here — 18 minutes from 10-80% on an 800V architecture — "
            "and the cheapest to buy at $46,100. Range is the shortest of the four at "
            "303 mi, and it lacks the adaptive cruise you asked about."
        ),
        "image_url": "https://placehold.co/640x360?text=IONIQ+5",
        "seats": 5, "fuel_type": "electric", "transmission": "automatic",
        "ev": {"range_mi": 303, "battery_kwh": 77.4, "dc_peak_kw": 235, "ten_to_eighty_min": 18},
        "safety": {"nhtsa_stars": 5, "iihs": "Top Safety Pick"},
        "tco_5yr": {"fuel_or_charging": 3700, "insurance": 8600,
                    "maintenance": 2200, "depreciation": 21800},
    },
    {
        "id": "l-102",
        "make": "Mercedes-Benz", "model": "EQE 350+", "year": 2024,
        "category": "sedan", "tags": ["electric", "luxury"],
        "price": {"currency": "USD", "buy": 74900, "rent_per_day": 145},
        "score": 0.79,
        "breakdown": {"budget": 0.62, "category": 1.0, "features": 0.85, "date": 1.0},
        "reasoning": (
            "The most comfortable and best-equipped of the shortlist, matching 6 of your "
            "7 requested features. At $74,900 it is the only one over your stated ceiling, "
            "and 260 mi is the shortest range here."
        ),
        "image_url": "https://placehold.co/640x360?text=EQE+350",
        "seats": 5, "fuel_type": "electric", "transmission": "automatic",
        "ev": {"range_mi": 260, "battery_kwh": 90.6, "dc_peak_kw": 170, "ten_to_eighty_min": 32},
        "safety": {"nhtsa_stars": 5, "iihs": "Top Safety Pick+"},
        "tco_5yr": {"fuel_or_charging": 4400, "insurance": 11200,
                    "maintenance": 3600, "depreciation": 28900},
    },
    {
        "id": "l-155",
        "make": "Kia", "model": "EV6 Wind AWD", "year": 2023,
        "category": "suv", "tags": ["electric"],
        "price": {"currency": "USD", "buy": 43500, "rent_per_day": 82},
        "score": 0.74,
        "breakdown": {"budget": 1.0, "category": 1.0, "features": 0.40, "date": 0.0},
        "reasoning": (
            "Cheapest here at $43,500 with a 20-minute fast charge. Two problems: it "
            "matches only 2 of your 7 requested features, and it is unavailable until "
            "17 September — two weeks after your target date."
        ),
        "image_url": "https://placehold.co/640x360?text=EV6",
        "seats": 5, "fuel_type": "electric", "transmission": "automatic",
        "ev": {"range_mi": 274, "battery_kwh": 77.4, "dc_peak_kw": 233, "ten_to_eighty_min": 20},
        "safety": {"nhtsa_stars": 5, "iihs": "Top Safety Pick"},
        "tco_5yr": {"fuel_or_charging": 3800, "insurance": 8900,
                    "maintenance": 2300, "depreciation": 20400},
    },
]


def _price_label(listing: dict[str, Any]) -> str:
    return f"${listing['price']['buy']:,} · ${listing['price']['rent_per_day']}/day"


def projection(listing: dict[str, Any], index: int) -> dict[str, Any]:
    """Search-result shape per contracts/agent-api.md — never the full body."""
    return {
        "id": listing["id"],
        "rank": index + 1,
        "headline": f"{listing['year']} {listing['make']} {listing['model']}",
        "price_label": _price_label(listing),
        "image_url": listing["image_url"],
        "score": listing["score"],
        "breakdown": listing["breakdown"],
        "reasoning": listing["reasoning"],
    }


def listing_detail(listing_id: str) -> dict[str, Any] | None:
    for listing in STUB_LISTINGS:
        if listing["id"] == listing_id:
            return listing
    return None
