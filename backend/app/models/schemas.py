"""Domain entities.

Mirrors specs/001-ai-car-matchmaker/data-model.md. Validation rules here are the
functional requirements made executable — a listing that cannot satisfy FR-008
should fail construction, not fail silently at search time.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Any, ClassVar, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

# --- Vocabularies ------------------------------------------------------------

Category = Literal[
    "sedan", "suv", "truck", "van", "coupe", "convertible",
    "hatchback", "wagon", "sports", "luxury", "electric", "hybrid",
]

CATEGORIES: tuple[str, ...] = (
    "sedan", "suv", "truck", "van", "coupe", "convertible",
    "hatchback", "wagon", "sports", "luxury", "electric", "hybrid",
)

FuelType = Literal["petrol", "diesel", "hybrid", "plugin_hybrid", "electric"]
Condition = Literal["new", "used"]
Intent = Literal["buy", "rent"]
Arrangement = Literal["finance", "lease", "outright"]
NotifyEvent = Literal["ranking_ready", "booking_confirmed", "session_abandoned"]
ChannelName = Literal["email", "slack", "sms"]
DeliveryStatus = Literal["sent", "failed", "mock"]
BookingStatus = Literal["draft", "confirmed", "cancelled"]

Phase = Literal[
    "INTERVIEWING", "RESEARCHING", "RANKED", "CAR_SELECTED",
    "BOOKING", "PAYING", "CONFIRMED",
]


# --- Listing components ------------------------------------------------------


class Price(BaseModel):
    currency: str = "USD"
    buy: int | None = None
    rent_per_day: int | None = None

    @model_validator(mode="after")
    def _at_least_one(self) -> Price:
        if self.buy is None and self.rent_per_day is None:
            raise ValueError("a listing must be purchasable, hireable, or both")
        return self


class Performance(BaseModel):
    hp: int
    torque_lb_ft: int
    zero_sixty_s: float


class EvSpec(BaseModel):
    range_mi: int
    battery_kwh: float
    dc_peak_kw: int
    ten_to_eighty_min: int


class Safety(BaseModel):
    nhtsa_stars: int = Field(ge=1, le=5)
    iihs: str | None = None


class TcoBreakdown(BaseModel):
    """Five-year running costs, currency units. Feeds trade-off narratives (FR-011)."""

    fuel_or_charging: int
    insurance: int
    maintenance: int
    depreciation: int

    @property
    def total(self) -> int:
        return self.fuel_or_charging + self.insurance + self.maintenance + self.depreciation


class Provider(BaseModel):
    id: str
    name: str
    type: Literal["dealership", "rental"]
    rating: float = Field(ge=0.0, le=5.0)


class AvailabilityWindow(BaseModel):
    from_date: date
    to_date: date

    @model_validator(mode="after")
    def _ordered(self) -> AvailabilityWindow:
        if self.to_date < self.from_date:
            raise ValueError(f"window ends before it starts: {self.from_date} → {self.to_date}")
        return self

    def covers(self, day: date) -> bool:
        return self.from_date <= day <= self.to_date


class Location(BaseModel):
    city: str
    country: str


# --- Listing -----------------------------------------------------------------


class Listing(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: str
    make: str
    model: str
    year: int = Field(ge=2018, le=2026)
    category: Category
    tags: list[str] = Field(default_factory=list)
    condition: Condition
    price: Price
    features: list[str] = Field(default_factory=list)
    mileage: int = Field(ge=0)
    fuel_type: FuelType
    transmission: str
    drivetrain: str
    seats: int = Field(ge=2, le=8)
    performance: Performance
    ev: EvSpec | None = None
    safety: Safety
    tco_5yr: TcoBreakdown
    image_url: str
    location: Location
    provider: Provider
    availability: list[AvailabilityWindow] = Field(min_length=1)
    description: str

    @model_validator(mode="after")
    def _ev_spec_iff_electrified(self) -> Listing:
        electrified = self.fuel_type in ("electric", "plugin_hybrid")
        if electrified and self.ev is None:
            raise ValueError(f"{self.id}: {self.fuel_type} listing needs an EvSpec")
        if not electrified and self.ev is not None:
            raise ValueError(f"{self.id}: {self.fuel_type} listing must not carry an EvSpec")
        return self

    @model_validator(mode="after")
    def _new_cars_have_no_mileage(self) -> Listing:
        if self.condition == "new" and self.mileage != 0:
            raise ValueError(f"{self.id}: new listing has {self.mileage} miles")
        return self

    @model_validator(mode="after")
    def _windows_ordered_and_disjoint(self) -> Listing:
        windows = sorted(self.availability, key=lambda w: w.from_date)
        for earlier, later in zip(windows, windows[1:]):
            if later.from_date <= earlier.to_date:
                raise ValueError(f"{self.id}: overlapping availability windows")
        return self

    def available_on(self, day: date) -> bool:
        """FR-008. A boolean `available` flag could not answer this."""
        return any(w.covers(day) for w in self.availability)

    @property
    def headline(self) -> str:
        return f"{self.year} {self.make} {self.model}"


class ScorableListing(BaseModel):
    """The projection the ranker sees.

    Principle III (NON-NEGOTIABLE): `make`, `model` and `provider.name` are
    absent by construction. The scorer cannot favour a manufacturer because it
    cannot see one — neutrality is structural, not a matter of discipline.
    SC-006's masking test guards this projection against regression.
    """

    model_config = ConfigDict(frozen=True)

    id: str
    category: Category
    tags: list[str]
    price: Price
    features: list[str]
    seats: int
    fuel_type: FuelType
    availability: list[AvailabilityWindow]
    provider_rating: float

    @classmethod
    def of(cls, listing: Listing) -> ScorableListing:
        return cls(
            id=listing.id,
            category=listing.category,
            tags=listing.tags,
            price=listing.price,
            features=listing.features,
            seats=listing.seats,
            fuel_type=listing.fuel_type,
            availability=listing.availability,
            provider_rating=listing.provider.rating,
        )


# --- Ranking -----------------------------------------------------------------


class ScoreBreakdown(BaseModel):
    """Every component recorded individually (FR-009), so ordering is reproducible."""

    budget: float = Field(ge=0.0, le=1.0)
    category: float = Field(ge=0.0, le=1.0)
    features: float = Field(ge=0.0, le=1.0)
    date: float = Field(ge=0.0, le=1.0)

    WEIGHTS: ClassVar[dict[str, float]] = {
        "budget": 0.35, "category": 0.25, "features": 0.25, "date": 0.15,
    }

    def total(self) -> float:
        return round(sum(getattr(self, k) * w for k, w in self.WEIGHTS.items()), 4)


class RankedResult(BaseModel):
    listing_id: str
    rank: int = Field(ge=1)
    score: float = Field(ge=0.0, le=1.0)
    breakdown: ScoreBreakdown
    reasoning: str


# --- Session -----------------------------------------------------------------


class BudgetRange(BaseModel):
    min: int | None = None
    max: int
    currency: str = "USD"


class Contact(BaseModel):
    name: str | None = None
    email: str | None = None
    phone: str | None = None


class ChannelStamp(BaseModel):
    """Which channel supplied a slot, and when (FR-022)."""

    channel: str
    at: datetime


class BookingDetails(BaseModel):
    name: str
    email: str
    phone: str | None = None
    licence_number: str
    consent_contact: bool = False


class PricingBreakdown(BaseModel):
    base: int
    destination_fee: int
    options: int
    subtotal: int
    tax: int
    total: int
    finance_apr: float | None = None
    finance_months: int | None = None
    monthly: int | None = None


class Booking(BaseModel):
    booking_id: str
    listing_id: str
    details: BookingDetails | None = None
    pricing: PricingBreakdown | None = None
    arrangement: Arrangement | None = None
    status: BookingStatus = "draft"
    simulated: Literal[True] = True
    """Constant, never a configurable flag (FR-016 · Principle IV)."""
    created_at: datetime


class DeliveryReceipt(BaseModel):
    event: NotifyEvent
    channel: ChannelName
    recipient: str
    rendered: str
    """Retained so mock mode can display the real artifact, not a 'would have sent' toast."""
    status: DeliveryStatus
    at: datetime


class ResumeToken(BaseModel):
    code: str
    session_id: str
    expires_at: datetime
    used: bool = False


class Session(BaseModel):
    session_id: str
    phase: Phase = "INTERVIEWING"

    intent: Intent | None = None
    category: Category | None = None
    budget: BudgetRange | None = None
    target_date: date | None = None
    rental_days: int | None = None
    features: list[str] = Field(default_factory=list)
    contact: Contact | None = None

    slot_origin: dict[str, ChannelStamp] = Field(default_factory=dict)

    ranked: list[RankedResult] = Field(default_factory=list)
    selected_car_id: str | None = None
    booking: Booking | None = None
    notifications: list[DeliveryReceipt] = Field(default_factory=list)

    entry_channel: str = "web"
    active_channel: str = "web"

    CORE_SLOTS: ClassVar[tuple[str, ...]] = ("intent", "category", "budget", "target_date")

    def missing_slots(self) -> list[str]:
        """Drives FR-005 and the /interview/missing data path."""
        return [s for s in self.CORE_SLOTS if getattr(self, s) is None]

    def interview_complete(self) -> bool:
        return not self.missing_slots()

    def already_notified(self, event: NotifyEvent, channel: ChannelName) -> bool:
        """Idempotency ledger for FR-025."""
        return any(n.event == event and n.channel == channel for n in self.notifications)

    def state_snapshot(self) -> dict[str, Any]:
        """Client-safe projection for STATE_SNAPSHOT — no slot_origin internals."""
        return {
            "session_id": self.session_id,
            "phase": self.phase,
            "intent": self.intent,
            "category": self.category,
            "budget": self.budget.model_dump() if self.budget else None,
            "target_date": self.target_date.isoformat() if self.target_date else None,
            "missing": self.missing_slots(),
            "ranked": [r.model_dump() for r in self.ranked],
            "selected_car_id": self.selected_car_id,
        }
