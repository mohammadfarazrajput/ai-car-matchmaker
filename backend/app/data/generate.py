"""Synthetic marketplace generator.

    python -m app.data.generate

Writes `listings.json`. Deterministic — a fixed seed means the dataset is
reproducible and the committed file is diffable.

Constitution Principle IV: the output declares `synthetic: true` in its manifest
and the figures, while internally consistent and plausible, describe no real
vehicle. Nothing here should be read as an accurate MSRP.
"""

from __future__ import annotations

import json
import random
from datetime import date, timedelta
from pathlib import Path
from typing import Any

DATA_DIR = Path(__file__).parent
MATRIX_PATH = DATA_DIR / "brand_matrix.json"
OUTPUT_PATH = DATA_DIR / "listings.json"

SEED = 20260808
TARGET_LISTINGS = 180
BASE_DATE = date(2026, 8, 1)

FEATURE_POOL = [
    "adaptive-cruise", "heated-seats", "ventilated-seats", "panoramic-roof",
    "360-camera", "blind-spot-monitor", "wireless-carplay", "android-auto",
    "premium-audio", "head-up-display", "lane-keep-assist", "parking-assist",
    "tow-package", "third-row", "awd", "roof-rails", "keyless-entry",
    "power-liftgate", "ambient-lighting", "massage-seats",
]

# Per-category shape: (price band, seats, 0-60 band, base body traits)
CATEGORY_PROFILE: dict[str, dict[str, Any]] = {
    "sedan":       {"price": (24_000, 62_000), "seats": (5, 5), "zero_sixty": (5.4, 8.6), "hp": (180, 380)},
    "suv":         {"price": (28_000, 78_000), "seats": (5, 7), "zero_sixty": (5.8, 9.2), "hp": (190, 400)},
    "truck":       {"price": (32_000, 82_000), "seats": (5, 6), "zero_sixty": (5.2, 8.8), "hp": (270, 480)},
    "van":         {"price": (34_000, 68_000), "seats": (7, 8), "zero_sixty": (7.2, 9.8), "hp": (200, 310)},
    "coupe":       {"price": (30_000, 74_000), "seats": (4, 4), "zero_sixty": (4.2, 6.8), "hp": (250, 430)},
    "convertible": {"price": (31_000, 88_000), "seats": (2, 4), "zero_sixty": (4.0, 7.4), "hp": (180, 420)},
    "hatchback":   {"price": (21_000, 44_000), "seats": (5, 5), "zero_sixty": (5.6, 9.4), "hp": (150, 315)},
    "wagon":       {"price": (27_000, 72_000), "seats": (5, 5), "zero_sixty": (5.0, 8.4), "hp": (180, 375)},
    "sports":      {"price": (34_000, 132_000), "seats": (2, 4), "zero_sixty": (3.2, 5.6), "hp": (300, 510)},
    "luxury":      {"price": (58_000, 148_000), "seats": (4, 7), "zero_sixty": (3.8, 6.4), "hp": (330, 540)},
    "electric":    {"price": (36_000, 96_000), "seats": (5, 7), "zero_sixty": (3.5, 7.2), "hp": (200, 480)},
    "hybrid":      {"price": (26_000, 64_000), "seats": (5, 7), "zero_sixty": (6.2, 9.0), "hp": (170, 300)},
}

CITIES = [
    ("Munich", "DE"), ("Berlin", "DE"), ("Hamburg", "DE"), ("Frankfurt", "DE"),
    ("Vienna", "AT"), ("Zurich", "CH"), ("Amsterdam", "NL"), ("Paris", "FR"),
]

DEALERS = [
    "Alpenblick Motors", "Nordstern Auto", "Rheinweg Cars", "Hansa Automobile",
    "Kaiserstrasse Motors", "Elbtal Vehicles", "Sudpark Auto", "Westhafen Motors",
]
RENTALS = [
    "Wegfrei Rentals", "CityDrive Hire", "Autobahn Rent", "Freiheit Mobility",
]


def _money(rng: random.Random, low: int, high: int) -> int:
    return int(rng.randint(low, high) / 50) * 50


def _availability(rng: random.Random) -> list[dict[str, str]]:
    """One or two forward windows. Some listings deliberately miss common target
    dates so the date component of the ranker has something real to discriminate on."""
    windows: list[dict[str, str]] = []
    cursor = BASE_DATE + timedelta(days=rng.randint(0, 45))
    for _ in range(rng.choice([1, 1, 1, 2])):
        length = rng.randint(14, 120)
        windows.append({
            "from_date": cursor.isoformat(),
            "to_date": (cursor + timedelta(days=length)).isoformat(),
        })
        cursor = cursor + timedelta(days=length + rng.randint(7, 40))
    return windows


def _ev_spec(rng: random.Random, plugin: bool) -> dict[str, Any]:
    if plugin:
        return {
            "range_mi": rng.randint(24, 52),
            "battery_kwh": round(rng.uniform(11.0, 19.5), 1),
            "dc_peak_kw": rng.randint(40, 95),
            "ten_to_eighty_min": rng.randint(22, 40),
        }
    return {
        "range_mi": rng.randint(215, 350),
        "battery_kwh": round(rng.uniform(58.0, 105.0), 1),
        "dc_peak_kw": rng.choice([120, 150, 170, 195, 235, 250, 270]),
        "ten_to_eighty_min": rng.randint(18, 38),
    }


def _tco(rng: random.Random, buy_price: int, fuel_type: str) -> dict[str, int]:
    """Five-year running costs, scaled off purchase price. Electrified cars run
    cheaper on energy and maintenance, and depreciate slightly harder."""
    electrified = fuel_type in ("electric", "plugin_hybrid", "hybrid")
    energy = int(buy_price * (0.06 if electrified else 0.11) * rng.uniform(0.85, 1.15))
    insurance = int(buy_price * 0.15 * rng.uniform(0.85, 1.15))
    maintenance = int(buy_price * (0.045 if electrified else 0.075) * rng.uniform(0.85, 1.15))
    depreciation = int(buy_price * rng.uniform(0.34, 0.48))
    return {
        "fuel_or_charging": energy,
        "insurance": insurance,
        "maintenance": maintenance,
        "depreciation": depreciation,
    }


def _fuel_for(category: str, rng: random.Random) -> str:
    if category == "electric":
        return "electric"
    if category == "hybrid":
        return rng.choice(["hybrid", "hybrid", "plugin_hybrid"])
    if category in ("sports", "coupe", "convertible", "truck"):
        return rng.choice(["petrol", "petrol", "petrol", "diesel"])
    return rng.choice(["petrol", "petrol", "diesel", "hybrid"])


def build() -> dict[str, Any]:
    rng = random.Random(SEED)
    matrix = json.loads(MATRIX_PATH.read_text())
    categories: dict[str, list[str]] = matrix["categories"]
    models: dict[str, dict[str, list[str]]] = matrix["models"]

    listings: list[dict[str, Any]] = []
    counter = 0

    # Pass 1 — guarantee the invariant: every (category, make) pair appears at
    # least once. FR-007 is a graded requirement, so it is satisfied by
    # construction rather than by hoping random sampling covers it.
    pairs: list[tuple[str, str]] = [
        (cat, make) for cat, makes in categories.items() for make in makes
    ]
    # Pass 2 — top up to the target with random pairs for volume and variety.
    while len(pairs) < TARGET_LISTINGS:
        cat = rng.choice(list(categories))
        pairs.append((cat, rng.choice(categories[cat])))

    for category, make in pairs:
        counter += 1
        profile = CATEGORY_PROFILE[category]
        model = rng.choice(models[category].get(make) or [f"{make} {category.title()}"])

        fuel_type = _fuel_for(category, rng)
        condition = rng.choice(["new", "new", "used"])
        year = 2026 if condition == "new" else rng.randint(2019, 2025)
        buy = _money(rng, *profile["price"])
        if condition == "used":
            buy = int(buy * rng.uniform(0.58, 0.86) / 50) * 50

        seats = rng.randint(*profile["seats"])
        hp = rng.randint(*profile["hp"])
        city, country = rng.choice(CITIES)
        is_rental = rng.random() < 0.45

        listing: dict[str, Any] = {
            "id": f"l-{counter:03d}",
            "make": make,
            "model": model,
            "year": year,
            "category": category,
            "tags": sorted({
                *(["electric"] if fuel_type == "electric" else []),
                *(["hybrid"] if fuel_type in ("hybrid", "plugin_hybrid") else []),
                *(["luxury"] if buy > 70_000 else []),
                *(["performance"] if hp > 400 else []),
                *(["family"] if seats >= 6 else []),
            }),
            "condition": condition,
            "price": {
                "currency": "USD",
                "buy": buy,
                "rent_per_day": max(35, int(buy / 520 / 5) * 5),
            },
            "features": sorted(rng.sample(FEATURE_POOL, rng.randint(4, 9))),
            "mileage": 0 if condition == "new" else rng.randint(4_000, 78_000),
            "fuel_type": fuel_type,
            "transmission": "manual" if (category == "sports" and rng.random() < 0.3) else "automatic",
            "drivetrain": rng.choice(["fwd", "rwd", "awd", "awd"]),
            "seats": seats,
            "performance": {
                "hp": hp,
                "torque_lb_ft": int(hp * rng.uniform(0.9, 1.45)),
                "zero_sixty_s": round(rng.uniform(*profile["zero_sixty"]), 1),
            },
            "safety": {
                "nhtsa_stars": rng.choice([4, 5, 5, 5]),
                "iihs": rng.choice(["Top Safety Pick+", "Top Safety Pick", None]),
            },
            "tco_5yr": _tco(rng, buy, fuel_type),
            "image_url": f"https://placehold.co/640x360?text={make.replace(' ', '+')}+{model.split()[0]}",
            "location": {"city": city, "country": country},
            "provider": {
                "id": f"p-{rng.randint(1, 40):03d}",
                "name": rng.choice(RENTALS if is_rental else DEALERS),
                "type": "rental" if is_rental else "dealership",
                "rating": round(rng.uniform(3.4, 4.9), 1),
            },
            "availability": _availability(rng),
            "description": f"{year} {make} {model} — {category}, {fuel_type.replace('_', ' ')}, {seats} seats.",
        }

        if fuel_type in ("electric", "plugin_hybrid"):
            listing["ev"] = _ev_spec(rng, plugin=fuel_type == "plugin_hybrid")

        listings.append(listing)

    return {
        "manifest": {
            "synthetic": True,
            "notice": (
                "Invented data for a hackathon demo. Figures are internally consistent "
                "and plausible but describe no real vehicle, price, or inventory."
            ),
            "generated_from": "brand_matrix.json",
            "seed": SEED,
            "listing_count": len(listings),
            "category_count": len(categories),
            "min_makes_per_category": min(len(m) for m in categories.values()),
        },
        "listings": listings,
    }


def main() -> None:
    payload = build()
    OUTPUT_PATH.write_text(json.dumps(payload, indent=1) + "\n")
    m = payload["manifest"]
    print(
        f"wrote {OUTPUT_PATH.name}: {m['listing_count']} listings, "
        f"{m['category_count']} categories, >={m['min_makes_per_category']} makes each"
    )


if __name__ == "__main__":
    main()
