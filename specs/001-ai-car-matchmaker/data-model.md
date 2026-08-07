# Phase 1: Data Model

Entities from [spec.md](./spec.md) §Key Entities, with the validation rules the functional
requirements imply. Types are Pydantic-shaped; nothing here is persisted beyond process lifetime.

---

## Listing

One vehicle offered for sale or hire.

| Field | Type | Rules |
|---|---|---|
| `id` | `str` | Unique; stable across regeneration |
| `make` | `str` | ≥10 distinct per category (FR-007). **Withheld from the scorer** — see Ranking below |
| `model` | `str` | |
| `year` | `int` | 2018–2026 |
| `category` | `Category` | Single-valued; one of exactly 12. Single-valued so the coverage invariant is countable |
| `tags` | `list[str]` | Overlapping traits: `electric`, `luxury`, `performance`, `family`. Resolves "is an i4 an EV or a sedan?" without breaking the invariant |
| `condition` | `"new" \| "used"` | |
| `price` | `Price` | |
| `features` | `list[str]` | Controlled vocabulary; matched against interview input |
| `mileage` | `int` | 0 when `condition == "new"` |
| `fuel_type` | `str` | `petrol` · `diesel` · `hybrid` · `plugin_hybrid` · `electric` |
| `transmission` | `str` | |
| `drivetrain` | `str` | Incl. manufacturer badge (`xDrive`, `quattro`, …) |
| `seats` | `int` | 2–8 |
| `performance` | `Performance` | |
| `ev` | `EvSpec \| None` | Required when `fuel_type` is `electric` or `plugin_hybrid`, else `None` |
| `safety` | `Safety` | |
| `tco_5yr` | `TcoBreakdown` | Feeds trade-off narratives (FR-011) |
| `image_url` | `str` | |
| `provider` | `Provider` | |
| `availability` | `list[AvailabilityWindow]` | **Non-empty.** Windows, not a boolean — FR-008 filters on a target date and a boolean cannot express that |
| `description` | `str` | |

```
Price            currency, buy: int|None, rent_per_day: int|None   # at least one non-null
Performance      hp, torque_lb_ft, zero_sixty_s
EvSpec           range_mi, battery_kwh, dc_peak_kw, ten_to_eighty_min
Safety           nhtsa_stars: 1-5, iihs: str|None
TcoBreakdown     fuel_or_charging, insurance, maintenance, depreciation   # 5-year, currency units
Provider         id, name, type: "dealership"|"rental", rating: 0.0-5.0
AvailabilityWindow  from_date, to_date            # to_date >= from_date
```

**Validation**
- `price.buy` required when the listing is purchasable; `price.rent_per_day` when hireable; at least
  one present.
- `ev` present iff `fuel_type` is electric or plug-in hybrid.
- `availability` non-empty and non-overlapping, ascending.

**Dataset manifest**: `listings.json` carries `synthetic: true`, a generation timestamp, and the
counts asserted by the coverage test — Principle IV requires the dataset to declare what it is.

---

## Category

A marketplace grouping. Exactly 12, fixed at build time:

`sedan` · `suv` · `truck` · `van` · `coupe` · `convertible` · `hatchback` · `wagon` · `sports` ·
`luxury` · `electric` · `hybrid`

**Invariant (FR-007, SC-003), enforced by unit test:**

```
len(categories) >= 12
for every category:  len({listing.make}) >= 10
len(listings) >= 100
```

Sourced from `brand_matrix.json`, which pairs each category with a curated ≥10-manufacturer list.
Curated rather than sampled from a flat pool, because random pairing yields implausible combinations.

---

## Session

One person's journey. The multistep memory FR-021 requires.

| Field | Type | Rules |
|---|---|---|
| `session_id` | `str` | Checkpointer key |
| `intent` | `"buy" \| "rent" \| None` | FR-001 |
| `category` | `Category \| None` | FR-002 |
| `budget` | `BudgetRange \| None` | For hire, compared against the **period total**, not the daily rate |
| `target_date` | `date \| None` | Single date, not a range |
| `rental_days` | `int \| None` | Captured only when `intent == "rent"` |
| `features` | `list[str]` | Optional refinements |
| `contact` | `Contact \| None` | Optional at interview, **required at booking** — see spec Assumptions |
| `slot_origin` | `dict[str, ChannelStamp]` | Which channel filled each slot and when (FR-022) |
| `ranked` | `list[RankedResult]` | Cleared whenever an input changes (FR-004) |
| `selected_car_id` | `str \| None` | |
| `booking` | `Booking \| None` | |
| `notifications` | `list[DeliveryReceipt]` | Delivery log; also the idempotency ledger |
| `entry_channel` | `str` | |
| `active_channel` | `str` | |

```
BudgetRange   min: int|None, max: int, currency        # max required
Contact       email: str|None, phone: str|None, name: str|None
ChannelStamp  channel: str, at: datetime
```

**State transitions**

```
INTERVIEWING ──(4 core slots filled)──► RESEARCHING ──► RANKED
     ▲                                                    │
     └────────────(any slot revised, FR-004)──────────────┤
                                                          ▼
                                                  CAR_SELECTED
                                                          │
                                                     BOOKING  (form)
                                                          │
                                                    PAYING  (checkout)
                                                          │
                                                    CONFIRMED
```

Revising a slot from `RANKED` or later clears `ranked` and returns to `RESEARCHING`. Revising after
`CONFIRMED` is refused — a confirmed booking is immutable.

---

## RankedResult

A listing paired with why it placed where it did.

| Field | Type | Rules |
|---|---|---|
| `listing_id` | `str` | |
| `score` | `float` | 0.0–1.0 |
| `breakdown` | `ScoreBreakdown` | Every component recorded individually (FR-009) |
| `reasoning` | `str` | ≥1 supporting figure **and** ≥1 trade-off (FR-011) |
| `rank` | `int` | 1-based |

```
ScoreBreakdown   budget: float, category: float, features: float, date: float   # each 0.0-1.0
```

### Ranking (FR-009, FR-010 · Principle III)

```
score = 0.35·budget + 0.25·category + 0.25·features + 0.15·date

budget    1.0 at <=80% of ceiling, decaying linearly to 0.0 at 120%
category  exact 1.0 | tag overlap 0.6 | adjacent body style 0.3 | otherwise 0.0
features  |requested ∩ listing| / |requested|;  1.0 when none requested
date      1.0 if target_date falls inside an availability window, else 0.0
```

**Brand neutrality is structural.** The scorer is handed a `ScorableListing` projection that omits
`make`, `model` and `provider.name`. It cannot favour a manufacturer because it cannot see one.
SC-006's masking test asserts identical ordering with manufacturer names redacted.

Ties break on `score`, then `listing_id` ascending — deterministic, and not on brand.

---

## Booking

A simulated reservation.

| Field | Type | Rules |
|---|---|---|
| `booking_id` | `str` | Human-quotable reference |
| `listing_id` | `str` | |
| `details` | `BookingDetails` | From the form MCP App |
| `pricing` | `PricingBreakdown` | From the payment MCP App |
| `arrangement` | `"finance" \| "lease" \| "outright"` | |
| `status` | `"draft" \| "confirmed" \| "cancelled"` | |
| `simulated` | `bool` | **Always `true`.** Constant, not a flag — FR-016 |
| `created_at` | `datetime` | |

```
BookingDetails      name, email, phone, licence_number, consent_contact: bool
PricingBreakdown    base, destination_fee, options, subtotal, tax, total,
                    finance_apr|None, finance_months|None, monthly|None
```

`draft` persists partially entered values across an interruption (FR-018). Confirmation requires
`contact.email`.

---

## Notification

One delivery attempt.

| Field | Type | Rules |
|---|---|---|
| `event` | `"ranking_ready" \| "booking_confirmed" \| "session_abandoned"` | |
| `channel` | `"email" \| "slack" \| "sms"` | |
| `recipient` | `str` | |
| `rendered` | `str` | Content, retained so mock mode can display the real artifact |
| `status` | `"sent" \| "failed" \| "mock"` | |
| `at` | `datetime` | |

**Idempotency (FR-025)**: `(session_id, event, channel)` is unique across `session.notifications`.
A repeated event is a no-op.

**Failure (FR-026)**: `failed` is recorded and the journey continues. No required step may depend on
delivery.

**Mock (FR-027)**: absent credentials produce `status: "mock"` with `rendered` fully populated, so the
zero-key demo shows the actual message rather than a "would have sent" toast.

---

## ResumeToken

| Field | Type | Rules |
|---|---|---|
| `code` | `str` | 5 characters, unambiguous alphabet |
| `session_id` | `str` | |
| `expires_at` | `datetime` | Issued + 1 hour |
| `used` | `bool` | Single use (FR-023) |

Expired or spent codes are rejected with an explanation and an offer to start fresh — not a bare 404.
