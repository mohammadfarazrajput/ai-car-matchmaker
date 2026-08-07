# AI Car Matchmaker — Build Plan (Revision 2)

**Status**: supersedes conflicting details in SPEC.md / ARCHITECTURE.md / IMPLEMENTATION.md / TASKS.md.
Those documents remain the reference for intent; this document is the reference for *what we actually build*.

**Date**: 2026-08-08

---

## 0. Locked Decisions

| Decision | Choice | Consequence |
|---|---|---|
| MCP Apps rendering | **Both** — embedded host in our Next.js chat *and* the same servers exposed over Streamable HTTP so a judge can add them to Claude as a custom connector | One server implementation, two demo surfaces |
| MCP App server language | **Python**, hosted inside the FastAPI process via `mcp.server.fastmcp.FastMCP` | No separate container; we hand-roll what the TS SDK automates |
| Optional integrations | **Keep all** — observability, email, SMS, voice, Slack, WhatsApp, STT/TTS | ~10 days of work compressed into the window; requires the mock-mode discipline in §1 |

---

## 1. Non-Negotiable Design Principle: Zero-Key Demo

A judge must be able to `git clone && docker compose up` with **no API keys at all** and see the complete
flow work end to end. Therefore:

- Every external integration sits behind a provider interface with a `MockProvider` fallback.
- `settings.<key>` absent ⇒ the mock provider is selected automatically, and the tool returns a
  realistic success payload tagged `"mode": "mock"`.
- The UI renders mock-mode sends in a visibly distinct "simulated" style — honest, not fake.
- The LLM is the only hard dependency. Provide `LLM_PROVIDER=google|groq|echo`, where `echo` is a
  scripted deterministic agent used for CI smoke tests.

This single rule is what makes "keep all integrations" survivable: none of them can block the
critical path, and none of them can break the demo.

---

## 2. Errata — Corrections to Apply to the Existing Docs

### 2.1 Dependency versions (IMPLEMENTATION.md §2.2 is not installable)

| Doc pin | Reality (verified 2026-08-08) | Action |
|---|---|---|
| `ag-ui-langgraph>=0.1.0` | latest is **0.0.42** | `ag-ui-langgraph>=0.0.42,<0.1` |
| `copilotkit>=1.61.0` | PyPI `copilotkit` is **0.1.94**; 1.66.4 is the *npm* version | `copilotkit>=0.1.94` |
| `deepgram-sdk>=3.0.0` | **7.6.0**; all doc samples use the removed v3 API | pin `>=7.0,<8`, rewrite §2.9/§2.10 |
| `langchain-google-genai>=2.0.0` | **4.3.2** | pin `>=4.3,<5`, re-verify `ChatGoogleGenerativeAI` kwargs |
| `deepagents>=0.7.0` | 0.7.5 | OK |
| `mcp` (not listed) | **2.0.0** | add — required for the MCP App servers |
| `@copilotkit/a2ui-renderer` | 1.66.4 | OK, but align all `@copilotkit/*` to one version |
| `@modelcontextprotocol/ext-apps` | 1.7.5 (npm only) | frontend host side only |

### 2.2 LLM provider conflation

README/SPEC say "Vertex AI"; `config.py` takes an API key; the graph imports `langchain-google-genai`.
Those are two different products. **Decision: Google AI Studio** (`GOOGLE_API_KEY` +
`langchain-google-genai`) as primary, Groq as fallback. Delete all "Vertex AI" wording, or switch
to `langchain-google-vertexai` + ADC and drop `google_api_key`. Do not ship both.

### 2.3 Broken code samples in IMPLEMENTATION.md

| Location | Problem |
|---|---|
| §2.4 `main.py` | `add_langgraph_fastapi_endpoint(app, graph, "/agent")` — takes a `LangGraphAgent` wrapper, not a raw compiled graph |
| §2.9 STT | `deepgram.asyncprerecorded.transcribe_file` does not exist in v7 |
| §2.10 TTS | `deepgram.synthesis.speak` does not exist in v7 |
| §2.6 `search_cars` | no min price, brand, seats, or date filters; returns unranked `[:10]`; `json.dumps` of full listings will flood the context window |
| §3.2 `page.tsx` | mixes `@copilotkit/react-core/v2` (`CopilotKitProvider`) with v1 (`useCopilotReadable`) |
| §3.5 `catalog.ts` | contains JSX — must be `catalog.tsx` |
| §2.3 `config.py` | `class Config: env_file` is pydantic-v1 style; use `model_config = SettingsConfigDict(...)` |

### 2.4 Internal contradictions

- SPEC §8 "Database persistence — out of scope" vs ARCHITECTURE §5.2 "LangGraph checkpointer for
  durability" vs SPEC §3.2 "Database connection pooling".
  **Resolution**: LangGraph `InMemorySaver` for the session, thread-id keyed. Delete the connection-pooling NFR.
- `docs/README.md` uses `docs/`-relative links. Move it to repo root as `README.md`.

---

## 3. Revised Architecture — the MCP Apps Host

This is the piece missing entirely from ARCHITECTURE.md. Everything else there stands.

```
┌────────────────────────── Next.js frontend ───────────────────────────┐
│                                                                       │
│   CopilotKit chat  ──── A2UI catalog ────▶ car cards, progress, plans │
│          │                                                            │
│          │ agent emits tool call: open_booking_form / open_payment    │
│          ▼                                                            │
│   ┌──────────────────────────────────────────────────┐                │
│   │  McpAppHost (our component)                      │                │
│   │   1. resources/read  ui://car/booking-form.html  │                │
│   │   2. <iframe sandbox csp=... srcdoc={html}>      │                │
│   │   3. postMessage bridge:                         │                │
│   │        View →  ui/initialize, tools/call,        │                │
│   │                ui/update-model-context           │                │
│   │        Host →  ui/notifications/tool-result,     │                │
│   │                ui/notifications/tool-input       │                │
│   └──────────────────────────────────────────────────┘                │
└───────────────────────────────┬───────────────────────────────────────┘
                                │ JSON-RPC over /mcp (Streamable HTTP)
                                ▼
┌──────────────────── FastAPI (single process) ─────────────────────────┐
│  /agent   AG-UI SSE  ──▶ DeepAgents graph ──▶ tools + subagents       │
│  /mcp     FastMCP ASGI mount  ──▶ MCP App servers (booking, payment)  │
└───────────────────────────────────────────────────────────────────────┘
                                ▲
                                │ same endpoint, no code change
                    Claude Desktop / claude.ai custom connector
                              (via cloudflared tunnel)
```

### 3.1 Verified protocol contract (spec 2026-01-26)

- Resource mimeType: **`text/html;profile=mcp-app`**
- Tool meta: `_meta.ui.resourceUri` (+ legacy `_meta["ui/resourceUri"]` for older hosts)
- Resource meta: `_meta.ui.csp.{connectDomains,resourceDomains,frameDomains,baseUriDomains}`,
  `_meta.ui.permissions`, `_meta.ui.prefersBorder`
- URI scheme: `ui://<server>/<path>`
- View→Host: `ui/initialize`, `ui/notifications/initialized`, `tools/call`, `resources/read`,
  `ui/open-link`, `ui/message`, `ui/request-display-mode`, `ui/update-model-context`
- Host→View: `ui/notifications/tool-input`, `ui/notifications/tool-input-partial`,
  `ui/notifications/tool-result`, `ui/notifications/tool-cancelled`, `ui/resource-teardown`,
  `ui/notifications/size-changed`, `ui/notifications/host-context-changed`

### 3.2 Python server pattern (confirmed against the official `qr-server` example)

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Car Matchmaker Apps", stateless_http=True)
BOOKING_VIEW = "ui://car-matchmaker/booking-form.html"

@mcp.tool(meta={"ui": {"resourceUri": BOOKING_VIEW},
                "ui/resourceUri": BOOKING_VIEW})
def open_booking_form(car_id: str) -> dict:
    """Open the booking form for a selected car."""
    ...

@mcp.resource(BOOKING_VIEW, mime_type="text/html;profile=mcp-app",
              meta={"ui": {"csp": {}}})
def booking_view() -> str:
    return BOOKING_HTML          # fully inlined, no external assets
```

**Constraint that drives the frontend build**: MCP App HTML must be self-contained (deny-by-default
CSP). Either inline everything by hand, or add a small Vite + `vite-plugin-singlefile` build for the
two views and have Python read the bundled `.html` at startup. **Choose the Vite build** — hand-inlined
HTML will not survive iteration.

### 3.3 Host implementation note

`@modelcontextprotocol/ext-apps/app-bridge` exists for exactly this, but its host-side API is not
publicly documented. Before writing `McpAppHost`, read `examples/basic-host` in the
`modelcontextprotocol/ext-apps` repo — that is the reference implementation. Fallback if it proves
awkward: `@mcp-ui/client`, which the ext-apps README endorses as a fully-featured host framework.
**Timebox this to half a day; it is the highest-uncertainty item in the project.**

---

## 4. Revised Data Model

The schema in SPEC §5.2 cannot satisfy the date requirement and cannot express overlapping categories.

```jsonc
{
  "id": "string",
  "make": "string",              // ≥10 distinct per category
  "model": "string",
  "year": 2021,
  "category": "SUV",             // single-valued: the marketplace taxonomy, ≥10 values
  "tags": ["electric", "luxury"],// overlapping traits — fixes "is a Model Y Electric or SUV?"
  "condition": "new|used",
  "price": { "currency": "USD", "buy": 41990, "rent_per_day": 89 },
  "features": ["awd", "heated-seats"],
  "mileage": 12400,
  "fuel_type": "electric",
  "range_miles": 330,            // EV/hybrid only
  "transmission": "automatic",
  "drivetrain": "awd",
  "seats": 5,
  "image_url": "string",
  "location": { "city": "Berlin", "country": "DE", "lat": 52.52, "lon": 13.40 },
  "provider": { "id": "d-014", "name": "…", "type": "dealership|rental", "rating": 4.6 },
  "availability": [              // REQUIRED — makes target_date rankable
    { "from": "2026-08-10", "to": "2026-09-30" }
  ],
  "description": "string"
}
```

### 4.1 Coverage requirement

The brief demands ≥10 categories **and** ≥10 brands per category — that is ≥100 distinct
(category, brand) pairs, so 100 listings is a floor with zero slack, and naive random generation
produces nonsense ("Lamborghini minivan").

**Build a curated `brand_matrix.json`**: for each of **12** categories, an explicit list of ≥10
plausible brands. Generate **~180 listings** by sampling that matrix, so every pair is covered with
headroom. Add a test that asserts the coverage invariant — it is a graded requirement, so it gets a
test.

Categories: Sedan, SUV, Truck, Van, Coupe, Convertible, Hatchback, Wagon, Sports, Luxury, Electric, Hybrid.

---

## 5. Ranking Algorithm (currently unspecified)

"Ranks by relevance" is not an acceptance criterion, and the brief requires the agent to **explain
its reasoning**. So the score must be decomposable and returned to the agent, not just sorted by.

```
score = Σ wᵢ · cᵢ        each cᵢ ∈ [0,1],  Σ wᵢ = 1

c_budget    0.30   1.0 at ≤80% of ceiling, linear decay to 0 at 120%
c_category  0.20   exact 1.0 | tag overlap 0.6 | adjacent body style 0.3
c_features  0.20   |requested ∩ listing| / |requested|
c_date      0.15   1.0 if target_date inside an availability window, else 0
c_location  0.10   1.0 same city, decaying by haversine distance
c_provider  0.05   provider.rating / 5
```

`search_cars` returns the top N with a `score_breakdown` object per listing. The system prompt
instructs the agent to cite the two highest-contributing components per recommendation. This turns a
vague requirement into something verifiable — and it is exactly what the observability bonus
evaluates against.

**Also fix**: the tool must return a *projection* (id, make, model, year, price, score_breakdown,
one-line why), not full listing JSON. Full details come from a separate `get_car_details(id)` call.
Otherwise ten listings blow the context.

---

## 6. Revised Phasing

Ordered so that everything the brief *requires* is done before anything optional starts. If time
runs out, what gets cut is optional by construction.

### Slice A — Vertical slice, end to end (highest priority)
1. Repo scaffold, spec-kit init, Docker compose skeleton, CI smoke test
2. `brand_matrix.json` + generator → 180 listings + coverage test + Pydantic schemas
3. FastAPI + DeepAgents graph + AG-UI endpoint; `echo` LLM provider for CI
4. Interview subagent with typed state; `search_cars` / `get_car_details` with §5 ranking
5. Next.js + CopilotKit + A2UI catalog: car card, interview progress, reasoning trace
6. **Walking skeleton green**: talk to it, get ranked cars with explanations, in the browser

### Slice B — MCP Apps (the required, highest-risk feature)
7. Vite singlefile build for `booking-form.html` and `payment.html`
8. `FastMCP` servers mounted at `/mcp`; tools + `ui://` resources per §3.2
9. `McpAppHost` in Next.js — **timeboxed, read `examples/basic-host` first**
10. Verify the *same* endpoint works as a Claude custom connector over cloudflared
11. Booking state round-trips: form → payment → confirmation, all in-chat

### Slice C — Observability (the only actual bonus)
12. Phoenix (`arize-phoenix-otel` 0.16.1) or Langfuse (4.14.3) +
    `openinference-instrumentation-langchain` 0.1.70; trace routing, tool calls, MCP calls
13. An eval set: ~20 scripted interviews with expected category/budget extraction, scored
    LLM-as-judge on recommendation explanation quality

### Slice D — Optional integrations (all mock-first per §1)
14. Provider interface + `MockProvider` for every channel — **this lands before any real SDK**
15. SendGrid email → Slack → Twilio SMS → Deepgram STT/TTS → Twilio Voice → WhatsApp
    (that order: cheapest and most reliable first; WhatsApp last, it may not land)

### Slice E — Ship
16. Dockerfiles (note: Next.js needs `NEXT_PUBLIC_*` at **build** time, not runtime — a standard trap)
17. Root README, `.env.example`, deployment, deck, video

---

## 7. Deliverables vs. the Brief

| Brief requirement | Where | Risk |
|---|---|---|
| Interview in-UI: use case, type, budget, date | Slice A.4 | low |
| Research + rank + explain reasoning | Slice A.4, §5 | low |
| **MCP App: form filling** | Slice B | **high** |
| **MCP App: mock payment/checkout** | Slice B | **high** |
| A2UI dynamic UI (not static HTML) | Slice A.5 | medium |
| 100+ listings / 10+ categories / 10+ brands per category | Slice A.2 | low — has a test |
| Multistep state across interview→research→recommend | Slice A.3 | low |
| Multistep agent harness (DeepAgents) | Slice A.3 | low |
| Spec-driven development (spec-kit) | Slice A.1 | **not yet started** |
| Docker or deployed app | Slice E | low |
| Public repo + README | Slice E | low |
| Slide deck | Slice E | **untracked in TASKS.md** |
| Video demo | Slice E | **untracked in TASKS.md** |
| *Bonus*: observability + evals | Slice C | medium |
| No real payments, no BMW APIs | by construction | — |

---

## 8. Open Risks

1. **`McpAppHost` is undocumented.** Highest-uncertainty item. Mitigation: timebox, read
   `basic-host`, fall back to `@mcp-ui/client`, and keep the Claude-connector path as proof the
   servers are correct even if our host lags.
2. **Scope.** Slices A–C alone are a full week. Slice D adds ~4 days of integrations that the brief
   never asked for. The mock-first rule (§1) means D can be truncated at any point without breaking
   the demo — but it will still compete for time with the deck and video, which *are* graded.
3. **A2UI + CopilotKit version churn.** `@copilotkit/a2ui-renderer` publishes canary/next tags
   heavily. Pin exact versions, commit the lockfile, do not use `^`.
4. **Deadline unknown.** Not stated in any document. Everything above assumes ~7 working days.
