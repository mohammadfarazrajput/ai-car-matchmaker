# Contract: Agent HTTP API

**Governs**: FR-021, FR-023, FR-029 · Backend surface consumed by the frontend

Base: `http://localhost:8010`

---

## `POST /agent` — AG-UI event stream

The single conversational endpoint. Server-Sent Events.

**Request**: `{ session_id?: string, messages: Message[] }` — omitting `session_id` mints a new one
and returns it in the first event.

**Event types**: `RUN_STARTED` · `TEXT_MESSAGE_START|CONTENT|END` · `TOOL_CALL_START|ARGS|END` ·
`STATE_SNAPSHOT` · `STATE_DELTA` · `A2UI_FRAME` · `RUN_FINISHED` · `RUN_ERROR`

`A2UI_FRAME` payloads are single-line JSON conforming to [a2ui-surfaces.md](./a2ui-surfaces.md).
`STATE_SNAPSHOT` carries the `Session` projection safe for the client — excluding
`slot_origin` internals and full listing bodies.

**Errors**: LLM failure emits `RUN_ERROR` with a human-readable message and leaves session state
untouched, so the person can retry without losing captured inputs.

### A2UI action dispatch

An A2UI surface returns interactions to the agent through **the same endpoint**, not a side channel.
A2UI actions are conversational turns — `setBudget` must be able to trigger a re-rank and stream new
frames back — so they ride the agent loop rather than a REST mutation.

**Request** — send `action` instead of (or alongside) `messages`:

```json
{ "session_id": "…",
  "action": { "name": "setBudget", "context": { "value": 65000 } } }
```

`name` and `context` are taken verbatim from the component's `action.event`. The frontend adds
nothing and interprets nothing.

**Response**: the same SSE stream. The agent applies the action, then emits whatever follows —
typically `updateDataModel` frames confirming the slot, and once the interview completes, the
`progress` and `results` surfaces.

| Action | Context | Effect |
|---|---|---|
| `setIntent` | `{value: "buy"\|"rent"}` | Fills the intent slot |
| `setCategory` | `{value: "<category>"}` | Fills the category slot |
| `setBudget` | `{value: <number>}` | Fills budget max |
| `setTargetDate` | `{value: "YYYY-MM-DD"}` | Fills the target date |
| `proceedAnyway` | `{assumption: "<text>"}` | Research with a slot missing (FR-006) |
| `selectCar` | `{index: <n>}` \| `{listingId: "…"}` | Selects, opens `checkout_launcher` |
| `openBookingForm` | `{listingId: "…"}` | Hands off to the booking MCP App |
| `explainMore` | `{index: <n>}` | Expands the reasoning for one result |
| `refineSearch` | `{…}` | Re-runs research with adjusted inputs |

**Unknown action names** return `RUN_ERROR` rather than failing silently — a typo in a surface
definition must be loud.

`value` is the conventional single-payload key. Components carrying their own bound value send it
under `value`; anything richer uses named context fields.

---

## `GET /api/listings` — marketplace read

Query: `category` · `intent` · `max_price` · `target_date` · `features` (repeatable) · `limit`
(default 10, max 50)

Returns **projections**, never full listing bodies:

```json
{ "count": 31, "results": [
  { "id": "l-014", "headline": "2024 BMW i4 eDrive40",
    "price_label": "$67,300", "image_url": "…",
    "score": 0.91,
    "breakdown": { "budget": 0.88, "category": 1.0, "features": 0.75, "date": 1.0 } } ] }
```

Full detail requires `GET /api/listings/{id}`. Returning complete listings in a search result would
flood the agent's context — the reason `docs/IMPLEMENTATION.md` §2.6 was rejected.

---

## `GET /api/listings/{id}` — full detail

The complete `Listing` per [data-model.md](../data-model.md). `404` if unknown.

---

## Session resumption

### `POST /api/session/{session_id}/resume-token`

```json
{ "code": "7QK2M", "url": "http://localhost:3000/s/7QK2M", "ttl_s": 3600 }
```

Signed, single-use, one hour.

### `GET /s/{code}`

`302` to the frontend with the session hydrated. Expired or already-used codes return `410 Gone`
with `{ "error": "expired" | "used", "message": "…", "start_fresh_url": "…" }` — an explanation and
a way forward, not a bare error (FR-023).

---

## `GET /health`

```json
{ "status": "ok", "llm_provider": "google", "listings_loaded": 180,
  "channels": { "email": "live", "slack": "mock", "sms": "mock" } }
```

`channels` reports live-vs-mock per adapter, making the zero-key state (FR-029) observable rather
than inferred.

---

## MCP endpoint

`POST /mcp` — Streamable HTTP, mounted from the same FastAPI process. Contract in
[mcp-apps.md](./mcp-apps.md). Deliberately the same endpoint whether consumed by our own
`McpAppHost` or by Claude as a custom connector, so the R3 fallback needs no code change.

---

## CORS

`FRONTEND_URL` only in production; permissive in development. `/mcp` additionally allows the host
origin so the sandboxed iframe can reach it.

---

## Contract tests

- [ ] `POST /agent` without `session_id` mints one and returns it in the first event
- [ ] `A2UI_FRAME` payloads validate against the A2UI contract
- [ ] `/api/listings` returns projections, never full bodies
- [ ] Resume code is single-use — second call returns `410`
- [ ] Expired code returns `410` with `start_fresh_url`
- [ ] `/health` reports `mock` for every channel when no keys are configured
- [ ] `RUN_ERROR` leaves captured session inputs intact
