# Contract: Channel Adapter

**Governs**: FR-024…FR-028 · Constitution Principle II (Zero-Key Demo)

One dispatcher, thin adapters. Three channels on a shared dispatcher cost ~2.5 hours; three separate
integrations cost ~6 and would have to be cut.

---

## Interface

```python
class ChannelCapabilities(NamedTuple):
    rich_ui: bool
    two_way: bool
    max_chars: int | None = None
    internal_only: bool = False

class ChannelAdapter(Protocol):
    name: str
    capabilities: ChannelCapabilities

    def render(self, session: Session, msg: AgentMessage) -> str: ...
    async def deliver(self, session: Session, msg: AgentMessage) -> DeliveryReceipt: ...
```

`AgentMessage` is channel-neutral — prose, an optional structured payload, optional choices. Each
adapter renders it natively. **The core never branches on channel.**

`render` is separate from `deliver` so mock mode produces the real artifact without sending it.

---

## Dispatcher

```python
async def notify(session: Session,
                 event: NotifyEvent,
                 channels: list[str] | None = None) -> list[DeliveryReceipt]:
```

| Event | Email | Slack | SMS | Fires when |
|---|---|---|---|---|
| `ranking_ready` | dossier | alert if top score > 0.90 | — | Ranking completes |
| `booking_confirmed` | receipt | deal alert | confirmation | `confirm_payment` returns |
| `session_abandoned` | — | — | resume link | 5 min idle at checkout *(STRETCH)* |

### Rules

**Idempotent (FR-025)** — keyed on `(session_id, event, channel)` against `session.notifications`.
A repeated event is a no-op. An agent that retries a step must not send two receipts.

**Never blocking (FR-026)** — every adapter failure is caught, recorded as `status: "failed"`, and
the journey continues. Notifications are best-effort by definition; no required step may depend on
one succeeding.

**Mock fallback (FR-027)** — absent credentials, `deliver` returns `status: "mock"` with `rendered`
fully populated. The UI notification panel shows the actual content. A "would have sent" toast is not
acceptable — the zero-key demo must show the real artifact.

**Figures must match (FR-028)** — all rendered content draws from the same `RankedResult.breakdown`
the A2UI cards bind to. A discrepancy between an email and the UI is a bug, not a formatting
difference.

---

## Adapters

### `email` — SHIP

Resend. `RESEND_API_KEY`, `EMAIL_FROM` (default `onboarding@resend.dev`, which works with no DNS
verification wait).

Jinja2 templates rendered server-side — not provider-hosted dynamic templates, which are not in
version control and cannot be tested offline. Table layout, inlined CSS, ~600px, plain-text
alternative always.

Two templates: match dossier (top 3, breakdown, comparison table) and reservation receipt (itemised
pricing, reference, **simulated-transaction banner**).

Mock mode writes rendered HTML to `/tmp/outbox/*.html` and surfaces it in the notification panel.

> **Not SendGrid.** Its free plan was retired 2025-05-27 — 60-day trial, then $19.95/month.

### `slack` — SHIP

Bot token, `chat:write`. Block Kit alert carrying the person's stated needs, the top match, the
agent's reasoning, the score breakdown, and `entry_channel`.

Threshold configurable at runtime — it will be tuned live during the demo.

The **Claim lead** button posts an ephemeral acknowledgement and marks the session claimed. It does
not route to a CRM. Per Principle IV, the acknowledgement states only what actually happened — a
button that appears functional but silently does nothing is worse than no button.

Bot token over incoming webhook: same cost today, and it keeps the DESIGNED slash-command tier
reachable.

### `sms` — STRETCH

Twilio. `TWILIO_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_PHONE_NUMBER`, `TWILIO_DEMO_ALLOWLIST`.

**Hard constraint**: trial accounts cannot register A2P 10DLC — it needs a paid account, $44 + $15
per campaign, and 10–15 days of review. The free path is toll-free verification to ≤5 pre-designated
numbers. SMS is therefore a demo-scale channel and is documented as such.

Guard rails: refuse any recipient outside `TWILIO_DEMO_ALLOWLIST` — fail loudly in development rather
than silently on stage. Rate limit per session. Templates ≤160 characters including the link, since
segmentation doubles cost and mangles previews. Handle `STOP`.

---

## Contract tests

- [ ] Every adapter satisfies the Protocol
- [ ] Same event dispatched twice → exactly one receipt per channel
- [ ] Adapter raising an exception → `failed` recorded, `notify` returns normally
- [ ] No credentials → `status: "mock"` with `rendered` populated
- [ ] Rendered figures equal `RankedResult.breakdown` for the same session
- [ ] Receipt content contains the simulated-transaction banner
- [ ] SMS refuses a recipient outside the allowlist
- [ ] `booking_confirmed` completes even when every adapter fails
