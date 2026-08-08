---
description: "Task list for AI Car Matchmaker implementation"
---

# Tasks: AI Car Matchmaker

**Input**: Design documents from `/specs/001-ai-car-matchmaker/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Included. The contract tests in each `contracts/*.md` and three named unit tests were
explicitly requested and back graded requirements.

## Format: `[ID] [P?] [Story] [Tier] Description`

- **[P]**: Parallelisable — different files, no dependency on incomplete work
- **[Story]**: US1–US7 from spec.md
- **[Tier]**: `SHIP` · `STRETCH` · `DESIGNED` — constitution Principle VI

## Tier rules (binding)

- **SHIP** — required. Docker, README, deck and video are SHIP and **MUST NOT** be reclassified.
- **STRETCH** — begins only after checkpoint D2-MID is green.
- **DESIGNED** — documented and presented as architecture; no implementation task exists.

---

## Phase 0: Before hour zero — account lead times

Zero build cost, days of waiting. Start in parallel with Phase 1.

- [ ] T002 [P] SHIP Create Slack app, grant `chat:write`, invite bot, record token in `.env`
- [ ] T003 [P] SHIP Sign up Resend, record `RESEND_API_KEY` in `.env`
- [ ] T004 [P] SHIP Obtain Google AI Studio key, record `GOOGLE_API_KEY` in `.env`

---

## Phase 1: Setup — Day 1 block 1

- [x] T005 SHIP Create `backend/` tree per plan.md Structure Decision (`frontend/` left to T025 — opencode owns it)
- [x] T006 SHIP Write `backend/requirements.txt` with exact pins from research.md R9 — no ranges
- [ ] T007 SHIP Write `frontend/package.json` with exact pins; commit the lockfile
- [ ] T008 [P] SHIP Configure ruff + black in `backend/pyproject.toml`
- [ ] T009 [P] SHIP Configure ESLint + Prettier in `frontend/.eslintrc.json`
- [x] T010 SHIP Write `backend/app/config.py` — Pydantic settings, every integration key optional
- [ ] T011 SHIP Write `docker-compose.yml` with backend and frontend services
- [ ] T012 SHIP Add CI workflow in `.github/workflows/ci.yml` running pytest on `LLM_PROVIDER=echo`
- [x] T013 SHIP Verify `pip install -r backend/requirements.txt` resolves — Principle V gate

---

## Phase 2: Foundational — blocking prerequisites

**⚠️ No user story work begins until this phase completes.**

- [x] T014 SHIP Define Pydantic entities in `backend/app/models/schemas.py` — `Listing`, `Price`, `Performance`, `EvSpec`, `Safety`, `TcoBreakdown`, `Provider`, `AvailabilityWindow` per data-model.md
- [x] T015 SHIP Define `Session`, `BudgetRange`, `Contact`, `ChannelStamp`, `RankedResult`, `ScoreBreakdown`, `Booking`, `Notification`, `ResumeToken` in `backend/app/models/schemas.py`
- [x] T016 SHIP Author `backend/app/data/brand_matrix.json` — 12 categories, ≥10 curated plausible manufacturers each
- [x] T017 SHIP Write generator `backend/app/data/generate.py` producing ~180 listings with trim, EV, safety and TCO attributes, non-empty availability windows, and a `synthetic: true` manifest
- [x] T018 SHIP Generate `backend/app/data/listings.json` and commit it
- [x] T019 SHIP **Unit test: marketplace coverage invariant** in `backend/tests/unit/test_marketplace_coverage.py` — ≥100 listings, ≥12 categories, ≥10 distinct makes per category, every listing has an availability window, manifest declares synthetic
- [x] T020 [P] SHIP Implement LLM providers in `backend/app/llm/providers.py` — `google`, `groq`, and a deterministic `echo` for CI
- [x] T021 SHIP Implement `SessionState` and the LangGraph checkpointer in `backend/app/agent/state.py`, keyed on `session_id`
- [x] T022 SHIP Scaffold FastAPI app in `backend/app/main.py` with CORS and `GET /health` reporting `llm_provider`, `listings_loaded` and per-channel live/mock
- [ ] T023 SHIP Assemble the DeepAgents graph in `backend/app/agent/graph.py`
- [x] T024 SHIP Mount the AG-UI SSE endpoint at `POST /agent` in `backend/app/main.py`
- [ ] T025 [P] SHIP Scaffold Next.js app with CopilotKit provider in `frontend/src/app/layout.tsx` and `page.tsx`

**Checkpoint**: `docker compose up` serves both services; `/health` responds; CI green.

---

## Phase 3: US1 — Tell the agent what I need (P1)

**Goal**: Conversation captures intent, category, budget and target date.
**Independent test**: Cold-start conversation captures all four; same inputs in one message asks nothing redundant.

- [ ] T026 [US1] SHIP Implement slot-filling in `backend/app/agent/interview.py` — multi-slot extraction from a single message, never re-asking a filled slot (FR-003)
- [ ] T027 [US1] SHIP Implement slot revision in `backend/app/agent/interview.py` — clears `ranked`, returns state to RESEARCHING (FR-004)
- [ ] T028 [US1] SHIP Implement missing-slot reporting and explicit-assumption proceed in `backend/app/agent/interview.py` (FR-005, FR-006)
- [x] T029 [US1] SHIP Write the A2UI JSONL emitter in `backend/app/a2ui/emitter.py` — one object per line, `version` plus exactly one of the four keys, no pretty-printing
- [ ] T030 [US1] SHIP Build the `interview` surface in `backend/app/a2ui/surfaces.py` with data paths and actions per contracts/a2ui-surfaces.md §1
- [ ] T031 [P] [US1] SHIP Write the A2UI catalog and renderers in `frontend/src/lib/a2ui/catalog.tsx`
- [ ] T032 [P] [US1] SHIP Build `frontend/src/components/ChatPanel.tsx` wiring the AG-UI stream to the A2UI renderer
- [ ] T033 [US1] SHIP **Contract test** in `backend/tests/contract/test_a2ui_frames.py` — every frame single-line JSON, exactly one of the four keys, no `protocol` / `action: "RENDER_COMPONENT"` / `props`, components flat with `children` ID references

**Checkpoint**: US1 independently testable in the browser.

---

## Phase 4: US2 — Ranked options with reasoning (P1)

**Goal**: Shortlist where each entry explains itself with real figures.
**Independent test**: Complete an interview; every option carries a breakdown matching listing data.

- [ ] T034 [US2] SHIP Implement marketplace search and filtering in `backend/app/agent/research.py`, including target-date availability (FR-008)
- [ ] T035 [US2] SHIP Implement the four-component scorer in `backend/app/agent/ranking.py` — budget .35, category .25, features .25, date .15, each normalised to [0,1]
- [ ] T036 [US2] SHIP Implement the `ScorableListing` projection in `backend/app/agent/ranking.py` excluding `make`, `model` and `provider.name` — structural brand neutrality (FR-010)
- [ ] T037 [US2] SHIP Implement deterministic tie-break on score then `listing_id` in `backend/app/agent/ranking.py`
- [ ] T038 [US2] SHIP Implement trade-off narrative generation in `backend/app/agent/explain.py` — ≥1 supporting figure and ≥1 trade-off per recommendation (FR-011)
- [ ] T039 [US2] SHIP Implement no-match handling in `backend/app/agent/research.py` — name the eliminating constraint, offer a specific relaxation (FR-012)
- [ ] T040 [US2] SHIP Implement follow-up answering over the same components in `backend/app/agent/explain.py` (FR-013)
- [ ] T041 [US2] SHIP Expose `GET /api/listings` returning projections with `score_breakdown` — never full bodies — in `backend/app/main.py`
- [ ] T042 [US2] SHIP Expose `GET /api/listings/{id}` returning full detail in `backend/app/main.py`
- [ ] T043 [US2] SHIP Build the `results` surface in `backend/app/a2ui/surfaces.py` binding `/results/{i}/breakdown/*` per contracts/a2ui-surfaces.md §3
- [ ] T044 [US2] SHIP **Unit test: brand-neutrality masking** in `backend/tests/unit/test_ranking_neutrality.py` — rank a fixed candidate set, re-rank with manufacturer names masked, assert identical order (SC-006)
- [ ] T045 [P] [US2] SHIP **Unit test: ranking components** in `backend/tests/unit/test_ranking.py` — each component's boundary behaviour, weights sum to 1.0
- [ ] T046 [P] [US2] SHIP **Contract test** in `backend/tests/contract/test_agent_api.py` — `/api/listings` returns projections, `POST /agent` mints a `session_id`, `RUN_ERROR` preserves captured inputs

**🚦 CHECKPOINT D1 — end of Day 1.** Browser interview captures all four inputs; ranked cards render
with visible breakdowns; network tab shows real A2UI frames.
**If red: cancel Phase 11 STRETCH entirely. Do not carry the slip forward.**

---

## Phase 5: US3 — Book and pay in-conversation (P1) — Day 2

**Goal**: Both MCP Apps render inside the chat and round-trip data.
**Independent test**: Select a car, complete both steps without leaving the conversation.

- [ ] T047 [US3] SHIP Scaffold Vite + `vite-plugin-singlefile` in `backend/app/mcp/views/vite.config.ts` for self-contained view builds
- [ ] T048 [US3] SHIP Build the booking form view in `backend/app/mcp/views/booking-form.html` — no external assets
- [ ] T049 [US3] SHIP Build the payment view in `backend/app/mcp/views/payment.html` with itemised pricing and in-view finance/lease/outright recalculation
- [ ] T050 [US3] SHIP Add the simulated-transaction banner to the payment view, visible without scrolling (FR-016)
- [ ] T051 [US3] SHIP Create the FastMCP instance in `backend/app/mcp/server.py` and mount it at `POST /mcp` in `backend/app/main.py`
- [ ] T052 [US3] SHIP Implement `open_booking_form` and `submit_booking_form` in `backend/app/mcp/booking.py` with `_meta.ui.resourceUri` plus the legacy key, and server-side validation
- [ ] T053 [US3] SHIP Register the `ui://car-matchmaker/booking-form.html` resource with `mime_type="text/html;profile=mcp-app"` and `csp: {}` in `backend/app/mcp/booking.py`
- [ ] T054 [US3] SHIP Implement `open_payment` and `confirm_payment` in `backend/app/mcp/payment.py`, idempotent per `booking_id`, every result carrying `simulated: true`
- [ ] T055 [US3] SHIP Register the `ui://car-matchmaker/payment.html` resource in `backend/app/mcp/payment.py`
- [ ] T056 [US3] SHIP Implement booking draft persistence for interrupted forms in `backend/app/agent/state.py` (FR-018)
- [ ] T057 [US3] SHIP Build the `checkout_launcher` A2UI surface in `backend/app/a2ui/surfaces.py`
- [ ] T058 [US3] SHIP **Read `examples/basic-host` in `modelcontextprotocol/ext-apps` before writing T059**
- [ ] T059 [US3] SHIP Implement `frontend/src/components/McpAppHost.tsx` — `resources/read`, sandboxed iframe, CSP from `_meta.ui.csp`, postMessage bridge using the exact method names in contracts/mcp-apps.md. **HARD 2-HOUR TIMEBOX**
- [ ] T060 [US3] SHIP **Contract test** in `backend/tests/contract/test_mcp_apps.py` — mimeType exactly `text/html;profile=mcp-app`, both `_meta` keys present, HTML references no external origin, every payment result carries `simulated: true`, banner present in view source, `confirm_payment` idempotent

**🚦 CHECKPOINT D2-MID.** Both MCP Apps render in-chat and round-trip booking state.

- [ ] T061 [US3] SHIP **Fallback, fires only if T059 exceeds its timebox**: expose `/mcp` via `npx cloudflared tunnel --url http://localhost:8010`, add as a Claude custom connector, verify both apps render there, and record the substitution in `logs/DECISIONS.md`

---

## Phase 6: US4 — Watch the agent work (P2)

**Goal**: Research progress visible as real steps, not a spinner.
**Independent test**: Trigger a search; steps appear sequentially carrying real counts.

- [ ] T062 [US4] SHIP Emit progress steps from actual search stages in `backend/app/agent/research.py` — real listing counts, never scripted
- [ ] T063 [US4] SHIP Build the `progress` surface in `backend/app/a2ui/surfaces.py` per contracts/a2ui-surfaces.md §2
- [ ] T064 [US4] SHIP Extend `backend/tests/contract/test_a2ui_frames.py` to assert progress step counts equal the real search figures for the same run

---

## Phase 7: US5 — Notifications (P2)

**Goal**: Dossier, receipt and dealer alert fire on the right events, exactly once.
**Independent test**: Complete a booking; each configured recipient gets exactly one correct message.

- [ ] T065 [US5] SHIP Define `ChannelAdapter`, `ChannelCapabilities`, `AgentMessage` and `DeliveryReceipt` in `backend/app/channels/base.py`
- [ ] T066 [US5] SHIP Implement `notify()` in `backend/app/channels/dispatcher.py` — idempotent on `(session_id, event, channel)`, failures caught and recorded, never blocking
- [ ] T067 [P] [US5] SHIP Implement the Resend email adapter in `backend/app/channels/email.py` with a mock fallback writing to `/tmp/outbox/`
- [ ] T068 [P] [US5] SHIP Write Jinja2 templates `_base.html.j2`, `dossier.html.j2` and `receipt.html.j2` in `backend/app/channels/email/templates/` — table layout, inlined CSS, plain-text alternative, simulated banner on the receipt
- [ ] T069 [P] [US5] SHIP Implement the Slack adapter in `backend/app/channels/slack.py` — Block Kit alert with breakdown and `entry_channel`, runtime-configurable threshold, truthful Claim-lead acknowledgement
- [ ] T070 [US5] SHIP Wire `ranking_ready` and `booking_confirmed` into the agent flow in `backend/app/agent/graph.py`
- [ ] T071 [P] [US5] SHIP Build `frontend/src/components/NotificationPanel.tsx` displaying rendered content and mock/live status
- [ ] T072 [US5] SHIP **Contract test: dispatcher idempotency** in `backend/tests/contract/test_dispatcher.py` — same event twice sends once, adapter exception records `failed` and returns normally, no credentials yields `status: "mock"` with `rendered` populated, figures equal `RankedResult.breakdown`, `booking_confirmed` completes when every adapter fails

---

## Phase 8: US6 — Resume a session (P3)

**Goal**: A link restores everything already said.
**Independent test**: Capture inputs, open the resume link in a fresh browser session, confirm nothing is lost.

- [ ] T073 [US6] SHIP Implement `POST /api/session/{id}/resume-token` in `backend/app/main.py` — signed, single-use, 1-hour TTL
- [ ] T074 [US6] SHIP Implement `GET /s/{code}` redirect with hydration, returning `410` and `start_fresh_url` for expired or spent codes
- [ ] T075 [P] [US6] SHIP Build the resume route in `frontend/src/app/s/[code]/page.tsx`
- [ ] T076 [US6] SHIP Record `slot_origin` and `entry_channel` per captured slot in `backend/app/agent/state.py` (FR-022)
- [ ] T077 [US6] SHIP Extend `backend/tests/contract/test_agent_api.py` — resume code single-use, second call `410`, expired code carries `start_fresh_url`

---

## Phase 9: Ship — Docker, docs, submission (SHIP, never reclassified)

- [ ] T078 SHIP Write `backend/Dockerfile` including the Vite view build step
- [ ] T079 SHIP Write `frontend/Dockerfile` passing `NEXT_PUBLIC_*` as **build args**, not runtime env
- [ ] T080 SHIP Finalise `docker-compose.yml` with healthchecks and build args
- [ ] T081 SHIP **Verify quickstart.md Scenario 1** — clean clone, empty `.env`, `docker compose up`, full journey works. Gates the video
- [ ] T082 SHIP Rewrite root `README.md` with run instructions, architecture summary, synthetic-dataset label and a DESIGNED-vs-built table
- [ ] T083 SHIP Update `.env.example` to match `config.py` exactly, including `RESEND_API_KEY`
- [ ] T084 SHIP Write `backend/tests/integration/test_journey.py` — full end-to-end on the `echo` provider
- [ ] T085 SHIP Record the demo video from the zero-key clone
- [ ] T086 SHIP Produce the 9-slide deck per claudedocs/08-BUILD-ORDER.md, showing real A2UI frames and the MCP `ui://` contract on slides 5–6
- [ ] T087 SHIP Push branch and open the submission

---

## Phase 10: Polish

- [ ] T088 [P] SHIP Add "superseded by claudedocs/" banners to `docs/*.md` and `gemini/*.md`, or correct the uninstallable pins in place
- [ ] T089 [P] SHIP Update `logs/WORKLOG.md` and `logs/DECISIONS.md` with the build's outcomes
- [ ] T090 SHIP Verify no artifact implies a real transaction or real inventory (Principle IV sweep)

---

## Phase 11: STRETCH — only after CHECKPOINT D2-MID is green

Strict order. Stop when time runs out.

- [ ] T091 STRETCH [US7] Wire Arize Phoenix and `openinference-instrumentation-langchain` in `backend/app/observability/tracing.py`
- [ ] T092 STRETCH [US7] Verify a completed session's decision path is reconstructable from its trace alone (SC-011)
- [ ] T093 [US1] STRETCH Implement browser voice capture and playback in `frontend/src/components/VoiceInput.tsx` with Deepgram STT/TTS, push-to-talk, barge-in, and commit-on-final only
- [ ] T095 STRETCH [US7] Build the eval set in `backend/tests/eval/` — ~20 scripted interviews asserting slot extraction, LLM-judged explanation quality

---

## DESIGNED — specified, not built

No implementation tasks. Presented as architecture in the deck; must never be demonstrated as working.

- Inbound phone interview concierge (claudedocs/03 §3a)
- Outbound follow-up call and warm transfer (claudedocs/03 §3b)
- Slack `/match-status` and `/override-match` slash commands (claudedocs/06 §4)
- SMS — dropped 2026-08-08; A2P 10DLC needs a paid account and 10–15 days of review, and the free toll-free path caps at 5 pre-designated numbers
- WhatsApp — dropped, multi-day Meta Business Verification

---

## Dependencies

```
Phase 0 (accounts) ──────────────┐  parallel, no build dependency
Phase 1 Setup                    │
   └─► Phase 2 Foundational      │
          ├─► Phase 3 US1 ───┐   │
          │                  ▼   │
          ├─► Phase 4 US2 ───┤   │   ← CHECKPOINT D1
          ├─► Phase 5 US3 ───┤   │   ← CHECKPOINT D2-MID
          ├─► Phase 6 US4 ───┤   │
          ├─► Phase 7 US5 ◄──────┘
          └─► Phase 8 US6 ───┤
                             ▼
                    Phase 9 Ship ──► Phase 10 Polish
                             │
                             ▼
                    Phase 11 STRETCH   (gated on D2-MID)
```

**Story dependencies**: US2 needs US1's captured inputs. US3 needs US2's selection. US4, US5 and US6
are independent of one another once Phase 2 is complete. US7 observes everything and depends on
nothing.

---

## Parallel opportunities

- **Phase 0**: T002–T004 all at once, and alongside Phase 1
- **Phase 1**: T008, T009 together
- **Phase 2**: T020 and T025 alongside T014–T019
- **Phase 3**: T031, T032 (frontend) alongside T026–T030 (backend)
- **Phase 4**: T045, T046 together
- **Phase 7**: T067, T068, T069, T071 — separate adapters, separate files
- **Phase 10**: T088, T089 together

---

## Implementation strategy

**MVP = Phase 1 + Phase 2 + Phase 3 (US1).** A working conversational interview that captures all
four inputs and shows them in A2UI. Demonstrable on its own.

**Increment 2** adds US2 — the ranked, explained shortlist. This is the product's core claim and the
point at which it stops being a chat window.

**Increment 3** adds US3, the two MCP Apps. Highest risk, hardest requirement, and the reason T058
(read the reference host) precedes T059, and T061 exists as a pre-agreed fallback rather than an
improvisation under pressure.

Everything after that is additive. If the clock runs out during Phase 11, nothing graded is missing.
