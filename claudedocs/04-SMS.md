# SMS

**Tier: STRETCH.** Cheap to build (~45 min on the shared dispatcher), but gated by an account
constraint that cannot be bought or rushed.

---

## 1. The constraint that defines this document

Twilio trial accounts **cannot register for A2P 10DLC**. Registration requires a paid account and
costs $44 brand + $15 per campaign + $1.50–10/campaign/month — and campaign review takes
**10–15 days**.

There is no version of this hackathon in which A2P completes. Money does not fix it.

**The free path that does work:** toll-free verification costs nothing, and a verified toll-free
number on a trial account can message **up to 5 pre-designated numbers**. Messages carry a trial
watermark.

### What that means for the plan

| Gemini's SMS draft proposed | Verdict |
|---|---|
| Abandoned-checkout recovery to customers | ✅ works — for your 5 registered demo numbers |
| Price-drop alerts to a saved-preference list | ❌ that is A2P messaging to arbitrary numbers |
| Two-way inbound with `CANCEL` keyword | ✅ inbound webhooks work on trial |
| Marketing cadences | ❌ and would need STOP/HELP compliance regardless |

So SMS is a **demo-scale channel**: real API, real delivery, to a handful of pre-registered
phones. That is honest and sufficient — say so in the deck rather than implying scale you cannot
reach.

**Start toll-free verification today.** It is the longest-lead free item in the project.

---

## 2. Role in the architecture

Per [01](01-CHANNEL-ARCHITECTURE.md) Rule 1, SMS never carries the interview. Its entire job is to
**hand the customer back to a richer channel**. 160 characters cannot rank cars, explain
trade-offs, or host an MCP checkout app — and attempting it would duplicate logic that already
exists on web.

```
 ┌──────────────┐        ┌────────────┐        ┌──────────────────┐
 │ Core event   │───────►│ Twilio SMS │───────►│ Customer handset │
 │ + resume tok │        │            │        │  → taps link     │
 └──────────────┘        └────────────┘        └────────┬─────────┘
                                                        ▼
                                          Web session hydrates, A2UI renders
```

Every outbound message contains a resume link. That is the point of the channel.

---

## 3. Triggers and templates

Templates stay under 160 characters including the link, because segmentation doubles cost and
mangles previews.

**A · Phone → web handoff** — fires when a phone interview ends *(DESIGNED, with 03)*
```
Your 4 matches are ready — 2024 i4, EQE, Model 3, i5.
See specs & reserve: {link}
```

**B · Booking confirmation** — fires on `booking_confirmed` *(STRETCH, ships with the fan-out)*
```
Confirmed: {year} {make} {model}, {date} at {dealer}.
Details: {link}  Reply STOP to opt out.
```

**C · Abandoned checkout** — 5 min idle at the payment step *(STRETCH)*
```
Your {model} is held for 15 more minutes.
Finish here: {link}
```

Template C is the strongest demo of the three because it shows the agent reacting to *inaction* —
genuine session awareness rather than request/response.

### Compliance, even in a mock

Include `STOP` handling and an opt-in checkbox on the booking form. Automotive judges will look
for it, it costs fifteen minutes, and its absence reads as carelessness in a regulated industry.

---

## 4. Implementation

Rides the shared dispatcher from [01](01-CHANNEL-ARCHITECTURE.md) §5 — this is why SMS costs ~45
minutes rather than 2 hours.

```python
class SmsAdapter(ChannelAdapter):
    name = "sms"
    capabilities = ChannelCapabilities(rich_ui=False, two_way=True, max_chars=160)

    async def deliver(self, session, msg) -> DeliveryReceipt:
        if not settings.twilio_sid:
            return DeliveryReceipt.mock("sms", msg.render_sms())
        ...
```

```
TWILIO_SID=
TWILIO_AUTH_TOKEN=
TWILIO_PHONE_NUMBER=          # verified toll-free
TWILIO_DEMO_ALLOWLIST=        # the ≤5 verified numbers
```

**Guard rails**
- Refuse to send to a number outside `TWILIO_DEMO_ALLOWLIST` — fail loudly in dev rather than
  silently on stage.
- Idempotent on `(session_id, event)`; a retrying agent must not double-text.
- Rate limit per session. An agent loop that texts eleven times will exhaust trial credit and
  look terrible.
- Inbound webhook `/api/sms/inbound` for `STOP` and replies.

---

## 5. Verification checklist

- [ ] Toll-free verification submitted (do this first — days of lead time)
- [ ] Demo numbers added to the verified list and to `TWILIO_DEMO_ALLOWLIST`
- [ ] Outbound send succeeds; watermark present and expected
- [ ] Allowlist rejection path tested
- [ ] Idempotency verified — same event twice sends once
- [ ] Inbound `STOP` handled and recorded
- [ ] Absent key → mock receipt, flow uninterrupted

**Sources:** [A2P 10DLC quickstart](https://www.twilio.com/docs/messaging/compliance/a2p-10dlc/quickstart) · [Twilio trial account guide](https://www.twilio.com/docs/usage/tutorials/how-to-use-your-free-trial-account) · [A2P fees](https://help.gohighlevel.com/support/solutions/articles/155000005200-a2p-10dlc-messaging-fees-registration-monthly-and-carrier-costs)
