# Slack — Dealer Operations

**Tier: SHIP (alert only).** The cheapest integration of the five: no verification, no per-message
cost, no compliance surface. Roughly 30 minutes on the shared dispatcher.

---

## 1. Why it earns its place

Slack is the only channel that is **not customer-facing**, and that is exactly why it is worth
demoing to an automotive audience. Every other entry will show a consumer chat experience. Showing
the *dealer* side — a high-intent lead landing in `#sales-leads` the moment the agent scores a
match above threshold — reframes the project from a chatbot into retail infrastructure.

It also costs almost nothing, because it reuses the notification fan-out from
[01](01-CHANNEL-ARCHITECTURE.md) §5.

```
 ┌───────────────────┐      ┌──────────────┐      ┌────────────────────┐
 │ ranking_ready     │      │  Slack Bot   │      │  #sales-leads      │
 │ score > 0.90      │─────►│ chat.post-   │─────►│  Block Kit card    │
 │ booking_confirmed │      │ Message      │      │  + Claim Lead btn  │
 └───────────────────┘      └──────────────┘      └────────────────────┘
```

---

## 2. Setup — genuinely free

1. Create a workspace (or use an existing one)
2. api.slack.com/apps → **Create New App** → From scratch
3. OAuth scopes: `chat:write`. Add `commands` only if you build slash commands (DESIGNED)
4. Install to workspace, copy the bot token
5. Invite the bot to the channel: `/invite @matchmaker`

```
SLACK_BOT_TOKEN=xoxb-…
SLACK_CHANNEL=#sales-leads
```

No verification, no waiting, no billing. Do this first — it is the fastest win of the five
integrations and gives the fan-out something real to prove itself against.

**Prefer a bot token over an incoming webhook.** Webhooks are simpler but are locked to one
channel and cannot be extended to interactivity later. The token path costs the same today and
keeps the DESIGNED tier reachable.

---

## 3. The lead alert — SHIP

Fires on `ranking_ready` when the top match scores above 0.90, and on every
`booking_confirmed`.

```json
{ "blocks": [
  { "type": "header",
    "text": { "type": "plain_text", "text": "High-intent lead · 0.91 match" } },
  { "type": "section", "fields": [
    { "type": "mrkdwn", "text": "*Intent*\nBuy · target 3 Sept" },
    { "type": "mrkdwn", "text": "*Budget*\n$60–70k" },
    { "type": "mrkdwn", "text": "*Top match*\n2024 BMW i4 eDrive40" },
    { "type": "mrkdwn", "text": "*Entry channel*\nPhone → Web" } ] },
  { "type": "section",
    "text": { "type": "mrkdwn",
      "text": "*Why:* 285 mi range and 31-min 10–80% charging fit a 40-mile daily commute; scored 1.0 on availability for the target date." } },
  { "type": "context", "elements": [
    { "type": "mrkdwn", "text": "Session `7QK2M` · budget .88 · category 1.0 · features .75 · date 1.0" } ] },
  { "type": "actions", "elements": [
    { "type": "button", "style": "primary",
      "text": { "type": "plain_text", "text": "Claim lead" }, "value": "claim:7QK2M" } ] }
] }
```

Two details that make this land:

**Entry channel is in the card.** *"Phone → Web"* tells a sales rep something no CRM alert
normally does, and it visibly demonstrates the cross-channel continuity from
[01](01-CHANNEL-ARCHITECTURE.md) §3.

**The reasoning is the agent's actual output**, carrying the same `score_breakdown` that the A2UI
cards bind to and the email dossier tabulates. One source of truth across three surfaces — if the
numbers ever disagree, that is a bug, not a formatting difference.

### Scope honesty

For the SHIP tier the **Claim lead** button posts an ephemeral acknowledgement and marks the
session claimed. It does not route to a CRM, assign an owner, or notify the customer. A button
that looks functional but silently does nothing is worse than no button — keep the acknowledgement
truthful.

---

## 4. Interactive operations — DESIGNED

Specified for the deck; not built.

| Command | Behaviour | Why it is out of scope |
|---|---|---|
| `/match-status <session>` | Return live interview stage, slots filled, ranked shortlist | Needs a request-URL endpoint, signature verification, and 3-second ack semantics |
| `/override-match <session> <vehicle>` | Push an alternative recommendation into the customer's live web session | **Substantially harder than it looks** — requires server→browser push routed to one specific session, i.e. a socket registry and reverse channel. This is a project, not a feature |
| Claim → assignment | Real ownership, SLA timers, CRM write-back | No CRM exists in scope |

The Gemini draft lists `/override-match` alongside the alert as though they were comparable. They
are not: the alert is outbound fire-and-forget over an existing dispatcher; the override needs a
bidirectional session bus that nothing else in the architecture requires. Naming that asymmetry in
the deck is a credibility point, not an admission.

---

## 5. Implementation

```python
class SlackAdapter(ChannelAdapter):
    name = "slack"
    capabilities = ChannelCapabilities(rich_ui=True, two_way=False, internal_only=True)

    async def deliver(self, session, msg) -> DeliveryReceipt:
        if not settings.slack_bot_token:
            return DeliveryReceipt.mock("slack", blocks=self.render_blocks(msg))
        ...
```

- Threshold in config, not hardcoded — you will tune it live while demoing.
- Idempotent on `(session_id, event)`; a re-ranked session must not spam the channel.
- Mock mode renders the Block Kit JSON into the UI notification panel, so the zero-key demo still
  shows the payload. Paste it into [Block Kit Builder](https://app.slack.com/block-kit-builder)
  to verify rendering without a workspace.

---

## 6. Verification checklist

- [ ] App created, `chat:write` granted, bot invited to the channel
- [ ] Alert posts and renders correctly on desktop **and mobile** Slack
- [ ] Score breakdown matches the A2UI cards and email dossier exactly
- [ ] Threshold configurable at runtime
- [ ] Idempotency verified — re-ranking sends once
- [ ] Claim button acknowledges truthfully, claims nothing it cannot claim
- [ ] Absent token → Block Kit JSON in the notification panel, flow uninterrupted
