# Channel Architecture

**The spine of the system.** Everything else is an adapter over this.

---

## 1. The problem with per-channel agents

The obvious way to add voice, SMS and email is to build a voice agent, an SMS agent and an email
agent. That is what the Gemini drafts imply, and it is wrong: you end up with four
implementations of "ask about budget" that drift apart, four state stores, and a customer who
must repeat themselves every time they switch.

Instead: **one core, many adapters.** The interview state machine, the ranking engine and the
tools never know which transport they are speaking over. Channels are I/O.

```
        ┌───────────────────────────────────────────────────────┐
        │              MATCH CORE  (transport-agnostic)         │
        │                                                       │
        │   SessionState ── Interview ── Research ── Rank        │
        │        │              ▲                    │          │
        │        │              └── slot filling ────┘          │
        │        └── persisted by session_id, resumable         │
        └───────────────────────┬───────────────────────────────┘
                                │  ChannelAdapter
    ┌───────────┬───────────┬───┴───────┬───────────┬───────────┐
    ▼           ▼           ▼           ▼           ▼           ▼
 Web text   Web voice     Phone        SMS        Email      Slack
  A2UI      Deepgram     Twilio      Twilio      Resend       Bot
 SHIP       STRETCH     DESIGNED     STRETCH      SHIP        SHIP
```

### The adapter contract

```python
class ChannelAdapter(Protocol):
    name: str
    capabilities: ChannelCapabilities

    async def deliver(self, session: SessionState, msg: AgentMessage) -> DeliveryReceipt: ...
    async def receive(self, raw: Any) -> tuple[SessionState, UserMessage]: ...
```

`AgentMessage` is channel-neutral: prose, an optional structured payload, and an optional list of
choices. Each adapter renders it natively — A2UI components on web, SSML on voice, 160 characters
plus a link on SMS, an HTML block in email, Block Kit in Slack. The core never branches on channel.

---

## 2. Capability matrix — the "when and where" answer

This table is the reason each channel exists. A channel is used *only* for what its profile
suits.

| Channel | Direction | Rich UI | Latency budget | Marginal cost | What it is genuinely good at |
|---|---|---|---|---|---|
| **Web text** | sync, two-way | A2UI, full | ~1s | free | The primary surface. Interview, ranked cards, reasoning trace, MCP checkout |
| **Web voice** | sync, two-way | A2UI alongside | <500ms | credits | Hands-free interview, accessibility, and the single most demo-friendly moment |
| **Phone** | sync, two-way | none | <500ms hard | per minute | Intake when the customer is away from a screen; human escalation |
| **SMS** | async, two-way | none | seconds–minutes | per message | Short nudges that **hand back** to a rich channel. Never the interview itself |
| **Email** | async, outbound | rich HTML | minutes–hours | free tier | Dossiers, comparisons, receipts — anything the customer will re-read later |
| **Slack** | async, outbound + interactive | Block Kit | seconds | free | Internal only. Dealer lead routing, never customer-facing |

### The three rules that fall out of it

**Rule 1 — Channels escalate toward richness, never away.** A narrow channel's job is to move the
customer to a wider one. SMS sends a resume link to web. Phone captures intent, then texts a link.
Email attaches the dossier and links to checkout. Nothing important terminates in a 160-character
channel.

**Rule 2 — Only web channels run the full interview.** Phone can capture the four core slots
(intent, budget, category, date) because they are short and unambiguous. It never attempts
feature preferences or trade-off discussion — that needs to be seen, not heard.

**Rule 3 — Checkout is web-only, always.** The brief requires MCP Apps for form-filling and
payment. Those render in a chat surface. No channel other than web can satisfy that, so every
path converges there.

---

## 3. Cross-channel session continuity — the differentiator

This is the capability worth demoing, and it is nearly free once the adapter model exists.

```
 Customer calls the number          Twilio → Deepgram → core
        │                            captures: rent · SUV · ≤$900/wk · Sept 3
        ▼
 Core mints resume token ────────►  SMS: "Picked up 4 matches for you —
        │                                  finish here: …/s/7QK2M"
        ▼
 Customer opens the link            Web session hydrates from SessionState.
        │                            Interview already 80% filled. A2UI renders
        │                            ranked cards immediately.
        ▼
 Refines in chat, picks the i4      MCP form app → MCP payment app, in-chat
        │
        ▼
 Confirmation fans out              Email dossier (customer)
                                    SMS confirmation (customer)
                                    Slack #sales-leads (dealer)
```

**Why it matters:** it demonstrates genuine multistep agent memory — the brief's explicit
requirement — across a boundary judges do not expect. Most entries will show memory across turns
in one chat window. Showing it across *transports* is a different class of claim.

**What makes it cheap:** `SessionState` is already required for the multistep agent. The resume
token is a signed short code mapping to a `session_id`. The adapters already exist. The whole
feature is a token endpoint and a hydration path — under an hour once two adapters work.

### Resume token

```
POST /api/session/{id}/resume-token   →  { "code": "7QK2M", "url": "…/s/7QK2M", "ttl_s": 3600 }
GET  /s/{code}                        →  302 to the web app with the session hydrated
```

Short code, one hour TTL, single use, signed. Not an auth system — the brief puts authentication
out of scope, and a resume link is a capability URL, which is the right shape for a demo anyway.

---

## 4. Session state

Extends the interview state with channel provenance, so the agent can say *"you mentioned on the
phone that…"* — a small touch that reads as genuine memory.

```python
class SessionState(TypedDict):
    session_id: str
    # ── interview slots (the brief's four, plus optional refinements)
    intent: Literal["buy", "rent"] | None
    category: str | None
    budget: BudgetRange | None
    target_date: date | None
    features: list[str]
    # ── provenance: which channel filled each slot, and when
    slot_origin: dict[str, ChannelStamp]
    # ── downstream
    ranked: list[RankedCar]
    selected_car_id: str | None
    booking: BookingDraft | None
    # ── delivery log, for the demo panel and for idempotency
    notifications: list[DeliveryReceipt]
    entry_channel: str
    active_channel: str
```

Persistence is LangGraph's checkpointer keyed on `session_id`. In-memory for the demo; the brief
puts a database out of scope, and swapping the checkpointer backend later is a one-line change.

---

## 5. Notification fan-out

Email, SMS and Slack all fire on the same events. Building them separately triples the work, so
they share one dispatcher — this is why three channels cost ~2.5 hours rather than six.

```python
async def notify(session, event: NotifyEvent, channels: list[str] | None = None):
    """One event, N adapters. Unconfigured adapters return a mock receipt."""
```

| Event | Email | SMS | Slack | Fires when |
|---|---|---|---|---|
| `ranking_ready` | dossier | — | lead alert if score > 0.9 | Phase 3 completes |
| `booking_confirmed` | receipt | confirmation | deal alert | MCP payment app returns |
| `session_abandoned` | — | resume link | — | 5 min idle at checkout (STRETCH) |
| `handoff_requested` | — | — | claim-lead alert | Customer asks for a human (DESIGNED) |

Every adapter is idempotent on `(session_id, event)` — an agent that retries must not send two
receipts.

---

## 6. Failure behaviour

Non-negotiable, because a live demo will hit at least one of these:

- **Missing key** → mock adapter, receipt tagged `mode: "mock"`, UI shows it as simulated.
- **Provider error** → log, mark the receipt failed, **continue**. A failing SMS must never block
  a booking confirmation.
- **Voice unavailable** → the mic button degrades to text input with an explanatory tooltip.
- **MCP host fails to render** → fall back to the Claude custom-connector demo path, which proves
  the servers are correct even if our host is not. See [08](08-BUILD-ORDER.md).

Notifications are best-effort and out-of-band by definition. Nothing in the required flow may
depend on one succeeding.
