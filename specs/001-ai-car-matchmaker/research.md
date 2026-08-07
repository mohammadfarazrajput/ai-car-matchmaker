# Phase 0: Research

All Technical Context entries resolved. No `NEEDS CLARIFICATION` markers remain.

Every version below was checked against its registry on **2026-08-08** rather than recalled —
constitution Principle V requires it, and doing so caught two uninstallable pins that had been sitting
in `docs/IMPLEMENTATION.md` since the project began.

---

## R1 · MCP App server language

**Decision**: Python, via `FastMCP` from the `mcp` SDK 2.0.0, mounted inside the FastAPI process.

**Rationale**: The challenge's own Resources list names the MCP Python SDK. The agent harness and API
are already Python, so co-locating lets MCP tools read session state by function call rather than
across a network boundary. The pattern is confirmed working by the official `qr-server` example:
`@mcp.tool(meta={"ui": {"resourceUri": …}})` and `@mcp.resource(URI, mime_type="text/html;profile=mcp-app")`.

**Alternatives considered**:
- *TypeScript with `@modelcontextprotocol/ext-apps`* — the official SDK, with `registerAppTool`
  helpers. Rejected: a second language and container, and the browser-facing host must be TypeScript
  regardless, so this buys consistency on only one side of the boundary.
- *TypeScript with `mcp-use` v2*, via the installed `mcp-apps-builder` skill. **Rejected on
  Principle I.** Its `references/views.md` contains no `resourceUri`, `_meta`, `ui://`,
  `text/html;profile=mcp-app` or postMessage — it wraps the contract behind `useToolContext` and
  `view: { name }`. A framework that hides the graded protocol surface makes compliance unverifiable
  by inspection. See decision #20.

---

## R2 · A2UI wire format

**Decision**: Emit the real A2UI v1.0 JSONL format — one JSON object per line, each carrying
`version` plus exactly one of `createSurface`, `updateComponents`, `updateDataModel`, `deleteSurface`.
Components are a flat list with `id`s; hierarchy comes from `children` ID references; data binds via
`{"path": "/json/pointer"}`; interactions declare `action.event.name` with a `context` object.

**Rationale**: A2UI compliance is graded and a judge can falsify a false claim from the network tab
in seconds.

**Alternatives considered**:
- *The format in `gemini/docs_SYSTEM_ARCHITECTURE.md`* — `{"protocol": "A2UI/1.0", "action":
  "RENDER_COMPONENT", "component": {…}}`. **Rejected: fabricated.** No `protocol` field, no `action`
  field, and no `RENDER_COMPONENT` message type exists in any published version. Building to it would
  have meant shipping a bespoke renderer while claiming A2UI compliance.

**Risk**: three spec versions are live (v0.9, v0.9.1, v1.0) and `@copilotkit/a2ui-renderer` publishes
canary tags aggressively. Mitigation: pin the emitted `version` to exactly what the renderer
implements, pin the package exactly, commit the lockfile.

---

## R3 · MCP Apps host in our own chat

**Decision**: Build `McpAppHost` in Next.js — fetch the `ui://` resource, render it in a sandboxed
iframe, bridge postMessage. Read `examples/basic-host` in `modelcontextprotocol/ext-apps` before
writing it. **Hard 2-hour timebox with a predetermined fallback.**

**Rationale**: The requirement is that the apps render *inside the chat*. Our chat is the Next.js app,
so that is where they belong.

**Risk — highest in the project**: the host-side API of
`@modelcontextprotocol/ext-apps/app-bridge` is not publicly documented. The published Patterns page
covers server and View authoring only and explicitly omits host architecture.

**Fallback (constitution Principle VI requires one)**: at the 2-hour mark, if the form is not
rendering, expose the same `/mcp` endpoint through `cloudflared` and add it to Claude as a custom
connector. The servers are byte-identical either way — which is precisely why they are built first.
Cost of firing the fallback: ~15 minutes. Cost of grinding past the timebox: a graded requirement.

**Alternatives considered**: `@mcp-ui/client`, endorsed by the ext-apps README as a fully-featured
host framework. Held as a second fallback if `app-bridge` proves awkward before the timebox expires.

---

## R4 · LLM provider

**Decision**: Google AI Studio via `langchain-google-genai` 4.3.2, Groq fallback, plus an `echo`
provider selected by `LLM_PROVIDER=echo`.

**Rationale**: The existing docs conflated two different products — README and SPEC said "Vertex AI"
while `config.py` took an API key and the graph imported `langchain-google-genai`. Vertex requires
service-account ADC and `langchain-google-vertexai`; the API-key path is AI Studio. AI Studio needs
far less setup, which matters in a two-day window. The `echo` provider makes CI and the smoke test
credential-free, satisfying Principle II.

**Note**: `langchain-google-genai` is at major version 4 while the docs assumed 2.x — constructor
kwargs must be re-verified against the installed version, not copied from the old snippets.

---

## R5 · Marketplace generation

**Decision**: A curated `brand_matrix.json` — 12 categories, each with an explicit list of ≥10
plausible manufacturers — sampled to generate ~180 listings. Coverage asserted by an automated test.

**Rationale**: The requirement of ≥10 categories with ≥10 brands each implies ≥100 distinct
(category, brand) pairs, so 100 listings is a floor with zero slack. Naive random generation across a
flat brand list produces nonsense such as a Lamborghini minivan. Twelve categories and ~180 listings
give headroom while every pair stays plausible. Coverage is a graded requirement, so it gets a test
rather than an inspection.

**Schema addition forced by the spec**: listings need `availability` *windows*, not the
`available: boolean` the earlier schemas carried — FR-008 requires filtering on a target date, which a
boolean cannot express. Overlapping traits (`electric`, `luxury`) move to a `tags` array so
`category` can stay single-valued for the coverage invariant.

---

## R6 · Ranking

**Decision**: Four weighted components summing to 1.0 — budget 0.35, category 0.25, features 0.25,
date 0.15 — each normalised to [0,1], with every component's contribution returned per listing as
`score_breakdown`.

**Rationale**: FR-011 requires each recommendation to cite concrete figures, and the constitution
requires ordering to be reproducible from the recorded components alone. A decomposed score satisfies
both and gives the STRETCH evaluation harness something objective to score against. Location and
provider rating were dropped: neither appears in the challenge's list of interview inputs, and fewer
components means less to tune under time pressure.

**Brand neutrality (Principle III)**: the scorer receives a projection of each listing that **excludes
`make`**. Neutrality is therefore structural rather than a matter of discipline, and SC-006's masking
test verifies it.

---

## R7 · Notification channels

**Decision**: One `notify(session, event, channels)` dispatcher with thin adapters — Slack and email
SHIP, SMS STRETCH — each with a mock fallback. Idempotent on `(session_id, event)`.

**Rationale**: Three channels on one dispatcher cost ~2.5 hours; three separate integrations cost ~6
and would have to be cut. Idempotency matters because an agent that retries a step must not send two
receipts.

**Email vendor**: **Resend**, not SendGrid. Twilio retired the SendGrid free plan on 2025-05-27 —
60-day trial, then $19.95/month — and every email workflow in the earlier drafts was built on it.
Resend gives 3,000/month free and, decisively for a two-day build, a sandbox sender that works with no
DNS verification wait.

**SMS constraint**: Twilio trial accounts cannot register A2P 10DLC at all; registration needs a paid
account, $44 + $15 per campaign, and 10–15 days of review. No budget shortens that. The free path —
toll-free verification, ≤5 pre-designated numbers — is what the templates are scoped to, so SMS is a
demo-scale channel and is documented as such.

**Dropped**: WhatsApp. Meta Business Verification takes multiple days and cannot complete in the
window; unofficial sandboxes would mean not using the Meta API the drafts claimed.

---

## R8 · State and resumption

**Decision**: LangGraph checkpointer keyed on `session_id`, in-memory. Resumption via a signed,
single-use, one-hour short code mapping to a session.

**Rationale**: Durable storage is out of scope per spec Assumptions, and the checkpointer backend is a
one-line swap if that changes. The resume link is a capability URL, which is the correct shape given
authentication is out of scope — and it is what makes the cross-channel continuity in FR-023 nearly
free, since `SessionState` already exists for the multistep requirement.

---

## R9 · Verified dependency versions

Two entries in `docs/IMPLEMENTATION.md` §2.2 **cannot install**. Corrected here.

| Package | Doc pin | Verified latest | Action |
|---|---|---|---|
| `ag-ui-langgraph` | `>=0.1.0` | **0.0.42** | ❌ unsatisfiable → pin `0.0.42` |
| `copilotkit` (PyPI) | `>=1.61.0` | **0.1.94** | ❌ unsatisfiable — 1.66.4 is the npm package → pin `0.1.94` |
| `deepgram-sdk` | `>=3.0.0` | 7.6.0 | installs, but the doc snippets call removed v3 methods |
| `langchain-google-genai` | `>=2.0.0` | 4.3.2 | two majors ahead; re-verify kwargs |
| `deepagents` | `>=0.7.0` | 0.7.5 | ✅ |
| `mcp` | *absent* | 2.0.0 | ✅ add — required for the MCP App servers |
| `@modelcontextprotocol/ext-apps` | — | 1.7.5 | ✅ host side, npm only |
| `@copilotkit/a2ui-renderer` | — | 1.66.4 | ✅ pin exact, no caret |
| `arize-phoenix` / `-otel` | — | 19.19.0 / 0.16.1 | ✅ STRETCH |
| `openinference-instrumentation-langchain` | — | 0.1.70 | ✅ STRETCH |

---

## R10 · Observability *(STRETCH)*

**Decision**: Arize Phoenix with `openinference-instrumentation-langchain`, auto-instrumenting the
LangGraph run.

**Rationale**: The only bonus category in the challenge, and auto-instrumentation makes it ~2 hours.
It scores against the `score_breakdown` the ranking already emits, so the evaluation harness needs no
new plumbing. Langfuse 4.14.3 is an equivalent alternative; Phoenix is self-hostable with no signup,
which suits the zero-key rule better.

---

## Sources

- [A2UI v1.0 specification](https://a2ui.org/specification/v1.0-a2ui/)
- [MCP Apps specification 2026-01-26](https://github.com/modelcontextprotocol/ext-apps/blob/main/specification/2026-01-26/apps.mdx)
- [Official Python `qr-server` example](https://github.com/modelcontextprotocol/ext-apps/blob/main/examples/qr-server/server.py)
- [SendGrid free plan retirement](https://www.twilio.com/en-us/changelog/sendgrid-free-plan)
- [Twilio A2P 10DLC quickstart](https://www.twilio.com/docs/messaging/compliance/a2p-10dlc/quickstart)
- [Twilio free trial guide](https://www.twilio.com/docs/usage/tutorials/how-to-use-your-free-trial-account)
