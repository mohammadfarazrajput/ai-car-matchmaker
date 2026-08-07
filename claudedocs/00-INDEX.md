# AI Car Matchmaker — Final Plan

**Amulate Summer Hackathon 2026 · hosted by BMW · 2-day build**
Authored 2026-08-08. This folder supersedes `docs/` and `gemini/`.

---

## Read in this order

| # | Document | What it settles |
|---|---|---|
| 01 | [Channel Architecture](01-CHANNEL-ARCHITECTURE.md) | The spine. One transport-independent core, six channel adapters, and the handoff rules that decide *when* each channel is used |
| 02 | [A2UI Protocol](02-A2UI-PROTOCOL.md) | The real wire format. **Read before writing any UI code** |
| 03 | [Voice & Calling](03-VOICE-CALLING.md) | Browser voice + inbound/outbound phone |
| 04 | [SMS](04-SMS.md) | Twilio SMS, and the A2P wall that constrains it |
| 05 | [Email](05-EMAIL.md) | Dossier and receipt. SendGrid is replaced — see 07 |
| 06 | [Slack](06-SLACK.md) | Internal dealer operations |
| 07 | [Feasibility & Costs](07-FEASIBILITY.md) | Verified free-tier reality; what is blocked and why |
| 08 | [Build Order](08-BUILD-ORDER.md) | The 2-day schedule, ruthlessly ordered |

---

## The one-sentence design

**A single channel-agnostic interview-and-match engine, reachable through web text, browser
voice, phone, and SMS — where every channel can hand the session to a richer one, so a
customer can start on the phone, finish in A2UI, and receive the dossier by email without ever
repeating themselves.**

Cross-channel session continuity is the differentiator. It is also, conveniently, cheap: the
channels are thin adapters over one core, so adding the fifth costs far less than the first.

---

## Three corrections to the Gemini plan

The `gemini/` drafts were a useful starting structure — the per-channel split and the
trigger-driven framing are both kept. Three things in them are wrong and would cost you marks.

**1. The A2UI payload format is invented.** `{"protocol": "A2UI/1.0", "action":
"RENDER_COMPONENT"}` does not exist. Real A2UI is newline-delimited JSON where every message
carries exactly one of `createSurface`, `updateComponents`, `updateDataModel`, `deleteSurface`.
A2UI compliance is a graded requirement and a judge can check it in ten seconds. See
[02](02-A2UI-PROTOCOL.md).

**2. SendGrid has no free tier.** Retired 27 May 2025; 60-day trial then $19.95/mo. Every email
workflow in the Gemini plan is built on a service you would have to pay for. Replaced with
Resend. See [07](07-FEASIBILITY.md).

**3. The SMS plan assumes capabilities a trial account does not have.** Price-drop alerts and
abandoned-cart recovery to arbitrary customer numbers require A2P 10DLC registration: a paid
account, $44 + $15 per campaign, and **10–15 days of review**. Not possible inside 2 days at any
price. The free path — toll-free verification, 5 pre-registered numbers — shapes what SMS can
actually do. See [04](04-SMS.md).

Smaller items: Deepgram already hosts Whisper, so "Deepgram STT + Whisper" is one pipeline and not
two; "SQLite / JSON" needs to be one choice (JSON, loaded to memory); the listing schema again
omits availability windows, which makes the required target-date matching impossible; and
`/override-match` pushing into a live web session is a bidirectional routing project, not a
hackathon feature.

---

## Scope: what ships versus what is designed

Two days is roughly 16–20 working hours. The required set alone consumes most of it. Every
document here marks its contents against this table.

| Tier | Meaning |
|---|---|
| **SHIP** | Required by the brief or needed for the demo narrative. Non-negotiable |
| **STRETCH** | Built only if the SHIP tier is green by the stated checkpoint |
| **DESIGNED** | Specified here, presented in the deck as architecture, not built |

Nothing is silently dropped. A design that is documented and honestly labelled "not built"
reads far better to judges than a half-wired integration that fails on stage.

| Capability | Tier |
|---|---|
| Web text interview, A2UI ranking, MCP form + payment apps, Docker, README, deck, video | SHIP |
| Mock marketplace (180 listings, 12 categories, 10+ brands each) | SHIP |
| Email dossier + receipt (Resend) | SHIP |
| Slack lead alert (Block Kit) | SHIP |
| Cross-channel session resume (web ↔ SMS link) | SHIP |
| Observability + evals (Phoenix, the brief's only bonus) | STRETCH |
| Browser voice interview (Deepgram STT/TTS) | STRETCH |
| Twilio SMS to verified numbers | STRETCH |
| Inbound phone interview concierge | DESIGNED |
| Outbound follow-up call, warm transfer | DESIGNED |
| Slack slash commands, live session override | DESIGNED |
| WhatsApp | DROPPED — multi-day Meta verification |

---

## Standing rules

1. **Zero-key demo.** `docker compose up` with an empty `.env` must produce a complete working
   flow. Every channel degrades to a visibly-labelled simulation when its key is absent. Only
   the LLM is a real dependency.
2. **No thumb on the scale.** BMW vehicles get *richer data*, never *higher ranking*. The brief
   requires 10+ brands per category and the agent's credibility rests on honest ordering. A
   rigged scorer is findable in the source and reads worse than a Toyota placing first.
3. **The dataset is synthetic and labelled as such** in the README. Invented MSRPs presented as
   real invite exactly the fact-check you lose.
4. **Pin exact versions.** No `^`. Commit the lockfile. `@copilotkit/*` publishes canary builds
   heavily and A2UI is at v1.0 with v0.9.x still in the wild.
