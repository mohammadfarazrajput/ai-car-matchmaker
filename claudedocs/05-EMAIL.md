# Email

**Tier: SHIP.** The one outbound channel with no gate, no verification wait, and no per-message
cost — and the only one that can carry a full comparison dossier.

---

## 1. SendGrid is out

Twilio retired the SendGrid free plan on **27 May 2025**. New accounts get a 60-day trial at
100/day, then Email API plans start at **$19.95/month**. The Gemini email plan, and
`docs/IMPLEMENTATION.md` §2.7, are both written against a tier that no longer exists.

**Replacement: [Resend](https://resend.com)** — 3,000 emails/month free, no credit card, and
crucially you can send from `onboarding@resend.dev` **immediately**, with no DNS verification
wait. For a 2-day build that last property matters more than the quota.

| Option | Free tier | Setup delay | Verdict |
|---|---|---|---|
| **Resend** | 3,000/mo | none — sandbox sender works instantly | **Chosen** |
| Brevo | 300/day | sender verification | Backup |
| SendGrid | trial only, then $19.95/mo | sender auth | Rejected |
| Gmail SMTP | ~500/day | app password | Last resort; poor deliverability, no templates |

The adapter interface makes this a one-file swap if Resend disappoints.

---

## 2. Role in the architecture

Email is the **only channel that can carry the full reasoning output**. Web shows ranked cards
in-session; email is what the customer forwards to their partner, reads on the train, and returns
to three days later. Per [01](01-CHANNEL-ARCHITECTURE.md) it is async and outbound — never part
of the interview loop.

It is also where the BMW-audience trade-off framing pays off best: an HTML table comparing range,
charge time, 0–60, safety and 5-year TCO across three vehicles is the single most
automotive-credible artifact the system produces.

---

## 3. The two emails

### A · Match dossier — fires on `ranking_ready`

The top three vehicles with score breakdown, a head-to-head trade-off paragraph, and a link back
into the live session.

```
┌──────────────────────────────────────────────┐
│  Your matches                                │
├──────────────────────────────────────────────┤
│  1 · 2024 BMW i4 eDrive40          0.91      │
│      budget .88 · category 1.0 ·             │
│      features .75 · date 1.0                 │
│      ── 285 mi range, 31 min 10–80%.         │
│         Gives up 1.1s to 60 vs the EQE,      │
│         gains ~$4k on 5-yr depreciation.     │
├──────────────────────────────────────────────┤
│  2 · …        3 · …                          │
├──────────────────────────────────────────────┤
│  Range   285 / 260 / 272 mi                  │
│  10–80%   31 / 32 / 27 min                   │
│  0–60    5.5 / 4.4 / 4.2 s                   │
│  5yr TCO  $39.5k / $44.2k / $41.1k           │
├──────────────────────────────────────────────┤
│           [ Continue in chat ]               │
└──────────────────────────────────────────────┘
```

The comparison table is generated from the same `score_breakdown` the A2UI cards bind to — one
source of truth, so email and UI can never disagree.

### B · Reservation receipt — fires on `booking_confirmed`

Transaction ID, vehicle, the full price breakdown from the MCP payment app (base, destination,
options, tax, finance terms), dealer contact, next steps. Explicitly marked as a simulated
transaction — see §5.

---

## 4. Templates

**Render HTML server-side with Jinja2. Do not use provider-hosted dynamic templates.** They are
another dashboard to configure, they are not in version control, and they cannot be tested
offline — all three are wrong for a 2-day build with a zero-key demo requirement.

```
backend/app/channels/email/templates/
├── _base.html.j2        # table layout, inlined CSS
├── dossier.html.j2
└── receipt.html.j2
```

Email HTML constraints that trip people up: table-based layout, inlined CSS only (no `<style>`
blocks in Gmail), no flexbox or grid, ~600px max width, and always ship a plain-text alternative.
The Gemini draft's stylesheet uses `display: table` and a `<style>` block — it will render
inconsistently across clients.

**Skip PDF generation.** The Gemini plan attaches a WeasyPrint dossier; WeasyPrint drags in
Pango, Cairo and GDK-Pixbuf, which materially complicates the Docker image for a deliverable
nobody grades. The HTML email *is* the dossier.

---

## 5. Honesty in the receipt

The brief requires payments to be *"a safe, fully mocked interface."* A receipt that looks
authentically real is exactly the artifact that shouldn't leave the demo looking genuine. The
receipt template carries a clear banner:

> **Simulated reservation — Amulate Hackathon demo. No payment was processed and no vehicle is reserved.**

Same reasoning as labelling the dataset synthetic: costs nothing, and removes any chance of the
artifact being mistaken for a real financial record.

---

## 6. Implementation

```python
class EmailAdapter(ChannelAdapter):
    name = "email"
    capabilities = ChannelCapabilities(rich_ui=True, two_way=False, async_=True)

    async def deliver(self, session, msg) -> DeliveryReceipt:
        if not settings.resend_api_key:
            return DeliveryReceipt.mock("email", html=self.render(msg))
        ...
```

```
RESEND_API_KEY=
EMAIL_FROM=onboarding@resend.dev     # works instantly, no DNS setup
```

In mock mode the rendered HTML is written to `/tmp/outbox/*.html` and surfaced in the UI's
notification panel — so the zero-key demo still *shows the actual email*, which is much better
than a "would have sent" toast.

---

## 7. Verification checklist

- [ ] Resend key resolves; test send to a real inbox lands
- [ ] Dossier renders correctly in Gmail web, Gmail iOS, and Apple Mail
- [ ] Plain-text alternative present
- [ ] Comparison table figures match the A2UI card breakdown exactly
- [ ] Simulated-transaction banner present on the receipt
- [ ] Idempotent on `(session_id, event)`
- [ ] Absent key → HTML written to outbox and shown in the UI panel

**Sources:** [SendGrid free plan changelog](https://www.twilio.com/en-us/changelog/sendgrid-free-plan) · [Free plan discontinued](https://helpdesk.reusser.com/hc/en-us/articles/38602119422349-SendGrid-Free-Plan-Discontinued)
