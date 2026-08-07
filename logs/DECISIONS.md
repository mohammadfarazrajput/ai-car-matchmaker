# Decisions

What was decided, by whom, and why. Append; don't rewrite history — if a decision
is reversed, add a new row pointing back at the old one.

| # | Date | Decision | Who | Why |
|---|---|---|---|---|
| 1 | 08-08 | MCP Apps rendered **both** ways — embedded host in our Next.js chat *and* the same `/mcp` endpoint as a Claude custom connector | Faraz | Same server code serves both; the Claude path is ~15 min and becomes free insurance if the embedded host doesn't land |
| 2 | 08-08 | MCP App servers in **Python** inside FastAPI, via `FastMCP` | Faraz | One language, one container. Confirmed viable against the official `qr-server` example — `meta=` works on `@mcp.tool` and `@mcp.resource` |
| 3 | 08-08 | Keep **all** optional integrations | Faraz | Maximise bonus surface |
| 4 | 08-08 | Hackathon is **2 days**, not 7 | Faraz | Corrects the assumption in `docs/PLAN.md` |
| 5 | 08-08 | Withdraw everything the brief didn't ask for | Faraz | Reverses #3 |
| 6 | 08-08 | Re-include the integrations, **free tiers only**; flag anything requiring payment | Faraz | Reverses #5 |
| 7 | 08-08 | **Drop WhatsApp** | Faraz | Meta Business Verification takes multiple days — cannot complete in the window at any price |
| 8 | 08-08 | **Replace SendGrid with Resend** | Claude, accepted | SendGrid's free plan was retired 2025-05-27. Resend gives 3,000/mo free and a sandbox sender with no DNS wait |
| 9 | 08-08 | SMS scoped to the **free toll-free path**, 5 pre-designated numbers | Claude, accepted | A2P 10DLC needs a paid account and 10–15 days of review. Money doesn't fix the wait |
| 10 | 08-08 | **One transport-agnostic core + thin channel adapters**, not one agent per channel | Claude | Per-channel agents duplicate the interview four times and lose the customer's context at every switch |
| 11 | 08-08 | Narrow channels **hand off** to richer ones; never run the interview | Claude | 160 chars can't rank cars or host an MCP checkout. SMS's job is to get the user back to web |
| 12 | 08-08 | Checkout is **web-only** | Claude | The brief requires MCP Apps in chat; no other channel can render them |
| 13 | 08-08 | Build to the **real A2UI JSONL format** | Claude | Gemini's `RENDER_COMPONENT` payload is fabricated. A2UI compliance is graded and checkable in the network tab |
| 14 | 08-08 | **Google AI Studio**, not Vertex AI | Claude | The docs conflated them. API-key path is AI Studio; Vertex needs service-account ADC |
| 15 | 08-08 | Ranking: **4 weighted components** with per-listing breakdown | Claude | Location cut (not in the brief). Breakdown makes "explains its reasoning" inspectable rather than asserted |
| 16 | 08-08 | BMW data gets **richer, never ranked higher** | Claude | Brief requires 10+ brands per category; a rigged scorer is findable in source and reads worse than a Toyota placing first |
| 17 | 08-08 | Scope tiered **SHIP / STRETCH / DESIGNED** | Claude | ~25h of work in a 16–20h window. Overrun must land on stretch items, never a graded requirement |
| 18 | 08-08 | Docker, README, deck, video are **not stretch** | Claude | A missing deck costs more marks than missing voice |

---

## Open

| Question | Status |
|---|---|
| Clean up `docs/` and `gemini/` — fix in place, or add "superseded by claudedocs/" banners? | Unanswered. Both are public and contain uninstallable pins / the fabricated A2UI format |
| Twilio toll-free verification submitted? | Longest-lead free item. Blocks all of SMS |
| Slack bot token, Resend key, Google AI Studio key | Needed in `.env` before the matching adapters can be wired |
