# Quickstart & Validation

How to run the system and prove each user story works. Scenarios map to
[spec.md](./spec.md) success criteria.

---

## Prerequisites

Docker and Docker Compose. Nothing else — no Python or Node install needed for the container path.

For local development: Python 3.11+, Node 20+.

---

## Scenario 1 — Zero-key run *(gates everything else)*

**Proves**: SC-008, FR-029 · Constitution Principle II

```bash
git clone https://github.com/mohammadfarazrajput/ai-car-matchmaker.git
cd ai-car-matchmaker
cp .env.example .env          # leave every value empty
docker compose up --build
```

Open `http://localhost:3000`.

**Expected**: the complete journey works — interview, ranking, booking, payment. Every notification
shows as visibly simulated in the panel. `GET /health` reports `"channels": {"email": "mock",
"slack": "mock", "sms": "mock"}`.

**This scenario must pass before the demo video is recorded.** It is exactly what an evaluator does,
and it is the fastest way to catch an accidental dependency on a credential that happens to be
present locally.

---

## Scenario 2 — Interview

**Proves**: US1, SC-001, SC-005, FR-001…FR-006

1. Say: *"I need something for weekend camping trips."*
   → agent infers a category and **confirms** rather than asking cold.
2. New session. Say: *"Renting an SUV under $900 for the week of September 3rd."*
   → all four inputs captured from one message; **no redundant question** (SC-005); research begins.
3. Say: *"Actually make it $1,200."*
   → budget revised, prior results cleared and recomputed (FR-004).

---

## Scenario 3 — Ranking and reasoning

**Proves**: US2, SC-002, FR-009…FR-013

After scenario 2, confirm each card shows a score **and** its four-component breakdown, and that the
reasoning cites at least one supporting figure and at least one trade-off.

Ask *"why not something cheaper?"* → the answer uses the same components it ranked on.

```bash
docker compose exec backend pytest tests/unit/test_ranking.py -v
```

---

## Scenario 4 — Brand neutrality

**Proves**: SC-006, FR-010 · Constitution Principle III (NON-NEGOTIABLE)

```bash
docker compose exec backend pytest tests/unit/test_ranking_neutrality.py -v
```

Ranks a fixed candidate set, then re-ranks with manufacturer names masked. **Order must be
identical.** The scorer receives a projection excluding `make`, so neutrality is structural — this
test guards against that projection regressing.

---

## Scenario 5 — Marketplace coverage

**Proves**: SC-003, FR-007

```bash
docker compose exec backend pytest tests/unit/test_marketplace_coverage.py -v
```

Asserts ≥100 listings, ≥12 categories, ≥10 distinct manufacturers **in every category**, every
listing carrying a non-empty availability window, and the dataset manifest declaring
`synthetic: true`.

---

## Scenario 6 — MCP Apps in-chat

**Proves**: US3, SC-004, MC-001, FR-014…FR-018

1. Select a car → booking form appears **in the conversation**; no page navigation.
2. Complete it → checkout appears with itemised total and finance/lease/outright options.
3. Toggle arrangement → total recalculates without a round trip.
4. Confirm → reference shown, booking recorded.

Verify the wire contract directly:

```bash
curl -s -X POST localhost:8000/mcp \
  -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","id":1,"method":"resources/read",
       "params":{"uri":"ui://car-matchmaker/booking-form.html"}}' | jq '.result.contents[0].mimeType'
# → "text/html;profile=mcp-app"
```

```bash
docker compose exec backend pytest tests/contract/test_mcp_apps.py -v
```

**Fallback check** — if `McpAppHost` did not land within its timebox, the same endpoint must work as a
Claude custom connector:

```bash
npx cloudflared tunnel --url http://localhost:8000
```

---

## Scenario 7 — A2UI protocol fidelity

**Proves**: MC-002, FR-019, FR-020 · Constitution Principle I (NON-NEGOTIABLE)

Open the browser network tab, filter the agent stream, and inspect `A2UI_FRAME` payloads.

**Expected**: each is single-line JSON carrying `version` plus exactly one of `createSurface`,
`updateComponents`, `updateDataModel`, `deleteSurface`. **No `protocol` field. No `action:
"RENDER_COMPONENT"`. No `props` object.**

```bash
docker compose exec backend pytest tests/contract/test_a2ui_frames.py -v
```

Confirm progress steps carry real counts — the listing figures must match what the search actually
processed, not a scripted sequence.

---

## Scenario 8 — Notifications

**Proves**: US5, SC-009, FR-024…FR-028

Zero-key: complete a booking → the panel shows the rendered email, Block Kit JSON and SMS text, each
marked simulated. Figures must match the cards.

With credentials in `.env`, restart and repeat → real delivery; `/health` reports `live`.

```bash
docker compose exec backend pytest tests/contract/test_dispatcher.py -v   # idempotency, failure isolation
```

---

## Scenario 9 — Session resume

**Proves**: US6, SC-007, FR-023

```bash
curl -s -X POST localhost:8000/api/session/{id}/resume-token | jq -r .url
```

Open in a private window → every input and result restored, no re-asking. Open the same link again →
`410` with an explanation and a fresh-start link.

---

## Scenario 10 — Full smoke test

**Proves**: end-to-end on the credential-free `echo` provider — what CI runs.

```bash
docker compose exec backend pytest tests/integration/ -v
```

---

## Local development

```bash
# Backend
cd backend && python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python -m app.data.generate            # regenerate listings.json
uvicorn app.main:app --reload --port 8000

# MCP App views (rebuild after editing)
cd backend/app/mcp/views && npm install && npm run build

# Frontend
cd frontend && npm install && npm run dev
```

**Note**: `NEXT_PUBLIC_*` values are baked at **build** time, not runtime. Changing them requires a
frontend rebuild — in Docker they are build args, not environment entries.

---

## Definition of done

- [ ] Scenario 1 passes from a clean clone with an empty `.env`
- [ ] Scenarios 2–9 pass
- [ ] All contract, unit and integration tests green
- [ ] No artifact implies a real transaction or real inventory
- [ ] Unbuilt capabilities presented as DESIGNED, never demonstrated as working
