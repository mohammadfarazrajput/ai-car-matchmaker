# Contract: MCP Apps

**Governs**: MC-001, FR-014…FR-018 · Constitution Principle I (NON-NEGOTIABLE)

Two MCP Apps are mandatory: the booking form and the mock payment checkout. Both render inside the
conversation.

Spec version: **2026-01-26**. Every identifier below is exact; none may be paraphrased.

---

## Wire contract

| Element | Exact value |
|---|---|
| Resource MIME type | `text/html;profile=mcp-app` |
| Tool metadata | `_meta.ui.resourceUri` — plus legacy `_meta["ui/resourceUri"]` for older hosts |
| URI scheme | `ui://car-matchmaker/<name>.html` |
| Resource metadata | `_meta.ui.csp.{connectDomains,resourceDomains,frameDomains,baseUriDomains}`, `_meta.ui.permissions`, `_meta.ui.prefersBorder` |

**View → Host**: `ui/initialize`, `ui/notifications/initialized`, `tools/call`, `resources/read`,
`ui/open-link`, `ui/message`, `ui/request-display-mode`, `ui/update-model-context`

**Host → View**: `ui/notifications/tool-input`, `ui/notifications/tool-input-partial`,
`ui/notifications/tool-result`, `ui/notifications/tool-cancelled`, `ui/resource-teardown`,
`ui/notifications/size-changed`, `ui/notifications/host-context-changed`

---

## Tools

### `open_booking_form`

```python
BOOKING_VIEW = "ui://car-matchmaker/booking-form.html"

@mcp.tool(meta={"ui": {"resourceUri": BOOKING_VIEW},
                "ui/resourceUri": BOOKING_VIEW})
def open_booking_form(session_id: str, listing_id: str) -> dict: ...
```

Returns `{ listing: ListingSummary, prefill: BookingDetails | None, simulated: true }`.
`prefill` carries any draft values so an interrupted form resumes (FR-018).

**Submission** — the View calls back:

```
tools/call  submit_booking_form
  { session_id, listing_id, details: BookingDetails }
→ { ok: true, booking_id, next: "payment" }
```

Validation is server-side and re-run on submission; the View's own checks are convenience only.

### `open_payment`

```python
PAYMENT_VIEW = "ui://car-matchmaker/payment.html"

@mcp.tool(meta={"ui": {"resourceUri": PAYMENT_VIEW},
                "ui/resourceUri": PAYMENT_VIEW})
def open_payment(session_id: str, booking_id: str) -> dict: ...
```

Returns `{ pricing: PricingBreakdown, arrangements: [...], simulated: true }` with an itemised
total — base, destination fee, options, subtotal, tax, total — and finance, lease and outright
alternatives (FR-015). Switching arrangement recalculates **in-View**, with no round trip.

**Confirmation**:

```
tools/call  confirm_payment
  { session_id, booking_id, arrangement }
→ { ok: true, booking_id, reference, status: "confirmed", simulated: true }
```

Confirmation raises `booking_confirmed`, which fans out per
[channel-adapter.md](./channel-adapter.md).

---

## Resources

```python
@mcp.resource(BOOKING_VIEW, mime_type="text/html;profile=mcp-app",
              meta={"ui": {"csp": {}}})
def booking_view() -> str:
    return _read_built("booking-form.html")
```

`csp: {}` — **no external domains**. Both views are built by Vite with `vite-plugin-singlefile` into
fully self-contained HTML, so the deny-by-default CSP needs no exceptions. Python reads the built
artifact at startup.

Source lives in `backend/app/mcp/views/`; build output is gitignored and produced during the Docker
build.

---

## Payment safety (FR-016 · Principle IV)

Non-negotiable, and asserted by contract test:

- **No real payment is processed.** No integration with any processor exists.
- **No real payment credentials are collected.** Card fields accept only a `4242…`-style
  demonstration value; nothing is stored beyond the session, nothing is transmitted anywhere.
- Every payment and confirmation surface carries, visibly and without needing to scroll:

  > **Simulated transaction — hackathon demo. No payment will be processed and no vehicle is reserved.**

- `simulated: true` appears in every tool result on this path. It is a constant, never a
  configurable flag.

---

## Host requirement

`McpAppHost` (frontend) must:

1. `resources/read` the `ui://` URI and render the HTML in a **sandboxed** iframe.
2. Apply the CSP from `_meta.ui.csp`.
3. Bridge postMessage in both directions using the exact method names above.
4. Deliver the tool result via `ui/notifications/tool-result`.
5. Route `tools/call` from the View to the backend MCP endpoint.

**Timeboxed at 2 hours** (research R3). On expiry, fall back to the Claude custom-connector path —
the servers are unchanged, so the requirement is still demonstrated.

---

## Contract tests

- [ ] `resources/read` returns mimeType exactly `text/html;profile=mcp-app`
- [ ] Both tools expose `_meta.ui.resourceUri` and the legacy key
- [ ] Returned HTML references no external origin (self-containment)
- [ ] Every tool result on the payment path carries `simulated: true`
- [ ] The simulated-transaction banner is present in the payment view source
- [ ] `submit_booking_form` rejects a payload failing server-side validation
- [ ] `confirm_payment` is idempotent for a given `booking_id`
