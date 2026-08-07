# Build Order — 2 Days

Ordered so that every hour of overrun lands on a STRETCH item and never on a graded requirement.
Checkpoints are gates, not suggestions: if a checkpoint is red, the following STRETCH block is
skipped rather than compressed.

---

## Before hour zero — in parallel, costs nothing

Per [07](07-FEASIBILITY.md) §3. Do these while the first commits land:

- **Twilio toll-free verification** — days of lead time, submit first
- **Slack app + bot token** — 5 minutes
- **Resend** and **Google AI Studio** signups
- `cp .env.example .env`, fill what exists

---

## Day 1 — the walking skeleton

**Goal: talk to it in a browser and get ranked cars with real explanations.**

| Block | Work | Done when |
|---|---|---|
| **1 · Foundation** (~1.5h) | spec-kit init, backend/frontend scaffold, Docker skeleton, CI smoke test with `LLM_PROVIDER=echo` | `docker compose up` serves both, CI green |
| **2 · Marketplace** (~1.5h) | `brand_matrix.json` (12 categories × ≥10 plausible brands), generator → ~180 listings with availability windows, trim, EV, safety, TCO fields; Pydantic schemas; **coverage test** | Test asserts ≥10 categories and ≥10 brands each; 180 listings load |
| **3 · Agent core** (~4h) | DeepAgents graph, `SessionState`, interview slot-filling, `search_cars` + `get_car_details`, 4-component ranking with `score_breakdown`, trade-off generator | Interview fills 4 slots; ranking returns breakdowns; explanations cite real numbers |
| **4 · A2UI** (~4h) | Real JSONL emitter per [02](02-A2UI-PROTOCOL.md); `interview`, `progress`, `results` surfaces; CopilotKit renderer wired | Cards render from `updateComponents`; progress streams real steps, not a spinner |

### 🚦 Checkpoint D1 — end of Day 1
- [ ] Browser interview captures intent, budget, category, date
- [ ] Ranked cars render as A2UI cards with visible score breakdown
- [ ] Progress surface streams genuine reasoning steps
- [ ] Network tab shows `createSurface` / `updateComponents` — **not** invented JSON

**Red here means cut browser voice and observability outright.** Do not carry the slip forward.

---

## Day 2 — MCP Apps, channels, ship

**Goal: the required MCP Apps work in-chat, and it is packaged and presented.**

| Block | Work | Done when |
|---|---|---|
| **5 · MCP servers** (~2h) | Vite singlefile build for `booking-form.html` + `payment.html`; `FastMCP` tools and `ui://` resources at `/mcp`; premium price breakdown with finance/lease toggle | `resources/read` returns `text/html;profile=mcp-app`; tools carry `_meta.ui.resourceUri` |
| **6 · MCP host** (~2h, **hard timebox**) | `McpAppHost` in Next.js — iframe, CSP, postMessage bridge. **Read `examples/basic-host` in `modelcontextprotocol/ext-apps` first** | Form and payment render and round-trip inside our chat |
| **7 · Fan-out** (~2.5h) | One `notify()` dispatcher + Slack, Resend, SMS adapters; resume-token endpoint; notification panel | Booking fires all three; mock mode shows real payloads |
| **8 · Ship** (~2h) | Dockerfiles (`NEXT_PUBLIC_*` as **build args**), zero-key verification, README, `.env.example` | Fresh clone + empty `.env` + `docker compose up` → full flow |
| **9 · Present** (~1.5h) | Deck + video | Both submitted |

### 🚦 Checkpoint D2-mid — after block 6
- [ ] MCP form and payment render in-chat and return data to the agent
- [ ] Booking state round-trips through both apps

**Green → blocks 7–9, then STRETCH. Red → fire the fallback below immediately.**

---

## The MCP host fallback — decide fast, do not grind

Block 6 is the highest-uncertainty item in the project: the `app-bridge` host API is not publicly
documented, and only `examples/basic-host` shows the wiring.

**At the 2-hour mark, if the form is not rendering in our chat, stop.** Expose the same `/mcp`
endpoint through `cloudflared` and add it to Claude as a custom connector. The servers are
identical either way — that is why they were built first. You demo the required MCP Apps in
Claude's chat, note the embedded host as in-progress, and you have lost ~15 minutes instead of a
graded requirement.

```bash
npx cloudflared tunnel --url http://localhost:8000
# add the generated URL as a custom connector in Claude
```

---

## STRETCH — only after checkpoint D2-mid is green

Strict order. Stop when time runs out.

1. **Observability** (~2h) — Phoenix + `openinference-instrumentation-langchain`. The brief's only
   bonus, and it scores against the `score_breakdown` you already emit
2. **Browser voice** (~3h) — highest demo value of the remainder, highest risk to blocks 8–9
3. **SMS** (~45min) — only if toll-free verification came back
4. **Eval set** (~1h) — 20 scripted interviews, assert slot extraction, LLM-judge the explanations

---

## Non-negotiables

**Blocks 8 and 9 are not STRETCH.** A missing Dockerfile or deck costs more marks than missing
voice. If it is late on Day 2 and voice is half-built, **stop voice and ship**. Half-wired
integrations that fail on stage are worse than an honest DESIGNED slide.

**Commit continuously on a feature branch.** Never push to `main` without confirmation.

**Verify the zero-key path before the video.** Record the demo from a fresh clone with an empty
`.env` — it is what a judge will do, and it is the fastest way to catch an accidental dependency
on a key you happen to have locally.

---

## Deck outline (block 9)

Nine slides, mapped to what is actually graded:

1. Problem — conversational car buying
2. **Live demo video** — lead with it
3. Architecture — the one core, six adapters diagram from [01](01-CHANNEL-ARCHITECTURE.md)
4. Multistep agent — state machine and the cross-channel resume
5. **MCP Apps** — form and payment in-chat, `ui://` and `_meta.ui.resourceUri` named explicitly
6. **A2UI** — real JSONL frames on screen; this is where a fabricated format would have shown
7. Ranking and trade-off explanations — the score breakdown, honestly unweighted by brand
8. Channels — the capability matrix, with DESIGNED items labelled as such
9. Observability and what is next

Slides 5 and 6 are the two the judges are checking against the brief. Show real protocol output on
both, not screenshots of UI.

---

## Definition of done

- [ ] Interview captures intent, category, budget, target date, in-UI
- [ ] ≥100 listings, ≥10 categories, ≥10 brands per category — **enforced by test**
- [ ] Ranked results with per-listing reasoning citing real figures
- [ ] MCP App: form-filling, rendered in chat
- [ ] MCP App: mock payment, rendered in chat, clearly simulated
- [ ] A2UI drives catalogue and live progress — real protocol, verifiable in the network tab
- [ ] State persists across interview → research → recommend
- [ ] Docker container runs from a fresh clone with an empty `.env`
- [ ] README with run instructions; dataset labelled synthetic
- [ ] Public repo, deck, video
- [ ] No BMW APIs used; no real payment processed; no thumb on the ranking scale
