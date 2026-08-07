# Implementation Plan: AI Car Matchmaker

**Branch**: `001-ai-car-matchmaker` | **Date**: 2026-08-08 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/001-ai-car-matchmaker/spec.md`

## Summary

A multistep agent interviews a person about buying or renting a car, searches a synthetic
marketplace, and returns a ranked shortlist in which every recommendation cites concrete figures for
and against it. Booking and simulated checkout complete inside the conversation.

The technical approach was settled before planning and is recorded in `logs/DECISIONS.md` (21
decisions) and `claudedocs/`. This plan carries it through rather than re-deciding it. Three choices
shape everything else:

1. **One transport-agnostic core with thin channel adapters**, so the interview exists once and every
   channel is I/O. This is what makes five channels affordable inside a two-day window.
2. **Python end to end on the backend** — the agent, the API, and the MCP App servers share one
   process, so the MCP tools read session state directly instead of over a network hop.
3. **Protocol fidelity over framework convenience** — A2UI emits its real JSONL wire format and the
   MCP Apps use the official `ui://` contract, because both are graded and externally verifiable.

## Technical Context

**Language/Version**: Python 3.11+ (backend), TypeScript 5.x / Node 20 (frontend)

**Primary Dependencies**: FastAPI · LangChain DeepAgents 0.7.5 · LangGraph · `mcp` 2.0.0 (FastMCP) ·
`ag-ui-langgraph` 0.0.42 · `langchain-google-genai` 4.3.2 · Next.js · React · CopilotKit
1.66.4 with `@copilotkit/a2ui-renderer` · `@modelcontextprotocol/ext-apps` 1.7.5 (host side) · Vite +
`vite-plugin-singlefile` (MCP App views)

**Storage**: None. Synthetic marketplace loaded from JSON into memory at startup; session state held
by a LangGraph checkpointer keyed on `session_id`. Durable persistence is out of scope per spec
Assumptions.

**Testing**: pytest (backend, including the marketplace coverage invariant and ranking neutrality
test) · Vitest (frontend units) · a scripted end-to-end smoke test driven by the `echo` LLM provider
so CI needs no credentials

**Target Platform**: Linux container; `docker compose up` on any host. Browser: current Chrome/Firefox/Safari

**Project Type**: Web application — separate backend and frontend

**Performance Goals**: Ranked shortlist within 3 minutes of conversational start (SC-001); research
progress visible within 2 seconds of research beginning (SC-010); marketplace search over ~180
listings returns in under 100 ms, being an in-memory scan

**Constraints**: Complete journey must run with no third-party credentials beyond the LLM (SC-008).
MCP App HTML must be fully self-contained under a deny-by-default CSP. All dependency versions
pinned exactly, no ranges. Two-day build window.

**Scale/Scope**: Single anonymous user per session; ~180 listings across 12 categories; 7 user
stories; concurrent sessions limited only by process memory

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-checked after Phase 1 design.*

| Principle | Gate | Pre-Phase 0 | Post-Phase 1 |
|---|---|---|---|
| **I. Protocol Fidelity** (NON-NEGOTIABLE) | A2UI emits real JSONL with exactly one of the four message keys; MCP Apps use `ui://`, `text/html;profile=mcp-app`, `_meta.ui.resourceUri`; no framework may hide the protocol surface | ✅ PASS — verified against a2ui.org v1.0 and the official `qr-server` Python example; `mcp-apps-builder` rejected for hiding the contract (decision #20) | ✅ PASS — `contracts/a2ui-surfaces.md` and `contracts/mcp-apps.md` fix the wire format; contract tests assert it |
| **II. Zero-Key Demo** | Empty `.env` produces the full flow; every integration degrades to a labelled mock; only the LLM is a hard dependency | ✅ PASS — adapter interface with `MockProvider` fallback; `echo` LLM provider for CI | ✅ PASS — `quickstart.md` scenario 1 is the zero-key run and gates the demo recording |
| **III. Honest Ranking** (NON-NEGOTIABLE) | No brand-specific adjustment; `score_breakdown` inspectable per listing | ✅ PASS — four components, none keyed on make/model/provider | ✅ PASS — `data-model.md` gives the scorer no access to `make`; enforced by the SC-006 masking test |
| **IV. Truthful Artifacts** | Dataset labelled synthetic; payment labelled simulated; unbuilt features labelled DESIGNED | ✅ PASS | ✅ PASS — banner text specified in `contracts/mcp-apps.md`; dataset carries a `synthetic: true` manifest field |
| **V. Reproducible Builds** | Exact pins, lockfiles committed, every dependency verified installable | ✅ PASS — versions verified against PyPI/npm on 2026-08-08; two pins in `docs/` found uninstallable and corrected | ✅ PASS |
| **VI. Scope Discipline** | Work tiered; overrun lands on STRETCH; Docker/README/deck/video never stretch | ✅ PASS — tiering inherited from spec Assumptions | ✅ PASS — every task in Phase 2 will carry its tier |

**Result: PASS.** No violations; Complexity Tracking section omitted as unused.

## Project Structure

### Documentation (this feature)

```text
specs/001-ai-car-matchmaker/
├── plan.md              # This file
├── spec.md              # Feature specification
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   ├── agent-api.md         # HTTP surface: AG-UI stream, session, health
│   ├── mcp-apps.md          # MCP tool + ui:// resource contract
│   ├── a2ui-surfaces.md     # A2UI surfaces, components, data paths, actions
│   └── channel-adapter.md   # Notification adapter interface
├── checklists/
│   └── requirements.md  # Spec quality checklist
└── tasks.md             # Phase 2 output (/speckit-tasks — NOT created here)
```

### Source Code (repository root)

```text
backend/
├── app/
│   ├── main.py                  # FastAPI app; mounts AG-UI endpoint and /mcp
│   ├── config.py                # Settings; every integration key optional
│   ├── agent/
│   │   ├── graph.py             # DeepAgents graph assembly
│   │   ├── state.py             # SessionState schema
│   │   ├── interview.py         # Slot filling
│   │   ├── research.py          # Marketplace search
│   │   ├── ranking.py           # 4-component scorer + score_breakdown
│   │   └── explain.py           # Trade-off narrative generation
│   ├── a2ui/
│   │   ├── emitter.py           # JSONL frame emission
│   │   └── surfaces.py          # interview / progress / results / checkout_launcher
│   ├── mcp/
│   │   ├── server.py            # FastMCP instance mounted at /mcp
│   │   ├── booking.py           # Form tool + ui:// resource
│   │   ├── payment.py           # Checkout tool + ui:// resource
│   │   └── views/               # Vite source for the two single-file views
│   ├── channels/
│   │   ├── base.py              # ChannelAdapter protocol + DeliveryReceipt
│   │   ├── dispatcher.py        # notify(); idempotent per (session_id, event)
│   │   ├── email.py             # Resend + mock
│   │   ├── slack.py             # Block Kit + mock
│   │   └── sms.py               # Twilio + mock          [STRETCH]
│   ├── llm/
│   │   └── providers.py         # google | groq | echo
│   ├── data/
│   │   ├── brand_matrix.json    # 12 categories x >=10 curated brands
│   │   ├── listings.json        # ~180 generated listings
│   │   └── generate.py          # Generator; run at build time
│   ├── observability/
│   │   └── tracing.py           # Phoenix + OpenInference      [STRETCH]
│   └── models/
│       └── schemas.py           # Pydantic models
├── tests/
│   ├── contract/                # A2UI frames, MCP resource shape, adapter interface
│   ├── integration/             # End-to-end journey on the echo provider
│   └── unit/                    # Coverage invariant, ranking neutrality, idempotency
├── requirements.txt             # Exact pins
└── Dockerfile

frontend/
├── src/
│   ├── app/                     # Next.js routes, incl. /s/[code] resume
│   ├── components/
│   │   ├── ChatPanel.tsx
│   │   ├── McpAppHost.tsx       # iframe + postMessage bridge
│   │   └── NotificationPanel.tsx
│   └── lib/a2ui/catalog.tsx     # A2UI catalog + renderers
├── package.json                 # Exact pins
└── Dockerfile

docker-compose.yml
```

**Structure Decision**: Web application with separate `backend/` and `frontend/`. The MCP App servers
live **inside** the backend process (`backend/app/mcp/`) rather than as a third service — they need
direct access to session state, and a separate container would add a network hop and a second
deployment unit for no benefit. Their browser-facing views are built by Vite into single-file HTML
that Python reads at startup, satisfying the deny-by-default CSP without hand-inlining assets.
